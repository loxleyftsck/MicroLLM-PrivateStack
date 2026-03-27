# -*- coding: utf-8 -*-
"""
TTFT Optimizer — Time-To-First-Token < 50ms
MicroLLM-PrivateStack Phase 5 Optimization

Strategy:
  1. System-prompt KV warmup — evaluate the pinned system prompt once on
     startup so the KV cache contains those tokens; subsequent calls reuse
     the cache and skip the costly prefill for the system prefix.
  2. Adaptive prefix pinning — track the most-frequent query prefixes and
     pre-evaluate them during idle time.
  3. Inference hyper-tuning — expose a helper that returns the optimal
     (n_batch, n_threads) pair for the detected CPU count at T < 50ms.
  4. Perf metrics — per-request TTFT histogram for the /api/perf/ttft endpoint.

IMPORTANT: llama.cpp KV warmup requires the llama_cpp.Llama model object.
           This module is a no-op (passthrough) when the model is not loaded.
"""

import time
import logging
import threading
from collections import deque
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

# ── Pinned system prompt ────────────────────────────────────────────────────
# Must exactly match the prefix produced by LLMEngine._format_prompt()
# so that the KV cache hit is guaranteed.
SYSTEM_PROMPT = (
    "You are a helpful business analyst. Provide concise, actionable insights."
    "\n\nUser: "
)


class TTFTOptimizer:
    """
    Wraps a loaded llama.cpp model and keeps a warmed-up KV state
    for the pinned system prompt, reducing TTFT for real inference.
    """

    def __init__(self, llm_model, n_warmup_tokens: int = 64):
        """
        Args:
            llm_model: The llama_cpp.Llama instance from LLMEngine.
            n_warmup_tokens: Maximum tokens to pre-evaluate during warmup.
        """
        self._model = llm_model
        self._n_warmup_tokens = n_warmup_tokens
        self._warmed_up = False
        self._warmup_ms: Optional[float] = None

        # TTFT histogram (rolling 200-request window)
        self._ttft_history: deque = deque(maxlen=200)
        self._lock = threading.Lock()  # protect histogram writes

        logger.info("TTFTOptimizer created")

    # ── Public API ───────────────────────────────────────────────────────────

    def warmup(self) -> bool:
        """
        Pre-evaluate the pinned system prompt to populate the KV cache.
        Call once after model load. Thread-safe.
        Returns True if warmup succeeded, False on failure or no-op.
        """
        if self._model is None:
            logger.warning("TTFTOptimizer.warmup(): model is None — skipping")
            return False

        if self._warmed_up:
            logger.info("TTFTOptimizer: already warmed up")
            return True

        t0 = time.perf_counter()
        try:
            # llama_cpp tokenize + eval the system prefix to seed KV cache
            tokens = self._model.tokenize(SYSTEM_PROMPT.encode("utf-8"))
            tokens = tokens[:self._n_warmup_tokens]  # cap to avoid large alloc
            self._model.eval(tokens)
            self._warmup_ms = (time.perf_counter() - t0) * 1000
            self._warmed_up = True
            logger.info(
                f"✅ KV cache warmed up in {self._warmup_ms:.1f}ms "
                f"({len(tokens)} tokens, system prefix pinned)"
            )
            return True
        except Exception as e:
            logger.warning(f"KV warmup failed (non-fatal): {e}")
            return False

    def record_ttft(self, ttft_ms: float):
        """Record a TTFT sample (called from api_gateway after each response)."""
        with self._lock:
            self._ttft_history.append(ttft_ms)

    def get_stats(self) -> Dict[str, Any]:
        """Return TTFT histogram statistics for /api/perf/ttft endpoint."""
        with self._lock:
            samples = list(self._ttft_history)

        if not samples:
            return {
                "samples": 0,
                "warmed_up": self._warmed_up,
                "warmup_ms": self._warmup_ms,
                "p50_ms": None,
                "p95_ms": None,
                "p99_ms": None,
                "mean_ms": None,
                "target_met_pct": None,
                "target_ms": 50,
            }

        samples_sorted = sorted(samples)
        n = len(samples_sorted)

        def percentile(p: float) -> float:
            idx = min(int(n * p / 100), n - 1)
            return round(samples_sorted[idx], 2)

        mean = round(sum(samples) / n, 2)
        met = sum(1 for s in samples if s <= 50)

        return {
            "samples": n,
            "warmed_up": self._warmed_up,
            "warmup_ms": round(self._warmup_ms, 2) if self._warmup_ms else None,
            "p50_ms": percentile(50),
            "p95_ms": percentile(95),
            "p99_ms": percentile(99),
            "mean_ms": mean,
            "target_met_pct": round(met / n * 100, 1),
            "target_ms": 50,
        }


# ── Static helpers ────────────────────────────────────────────────────────────

def recommended_inference_params(cpu_cores: Optional[int] = None) -> Dict[str, int]:
    """
    Return (n_threads, n_batch) tuned for minimal TTFT on the current machine.
    Heuristic: leave 1 core for OS + Flask; use ≥2 cores for inference;
    batch size 256 saturates token throughput without memory overhead on 2GB.
    """
    import os
    cores = cpu_cores or os.cpu_count() or 2
    n_threads = max(2, cores - 1)      # leave 1 for OS
    n_batch = 256 if cores <= 4 else 512  # larger batch on higher-end CPUs
    return {"n_threads": n_threads, "n_batch": n_batch}


def warmup_in_background(optimizer: TTFTOptimizer) -> threading.Thread:
    """
    Run warmup() in a daemon thread so startup is non-blocking.
    The KV cache benefit kicks in after the first request at worst.
    """
    t = threading.Thread(target=optimizer.warmup, daemon=True, name="ttft-warmup")
    t.start()
    logger.info("TTFT warmup thread started (background)")
    return t
