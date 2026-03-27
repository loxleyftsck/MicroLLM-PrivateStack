# -*- coding: utf-8 -*-
"""
Model Registry - Multi-model management for MicroLLM-PrivateStack
Phase 5: Model Selector feature

Supports declaring multiple GGUF models and switching the active model
at runtime. All model definitions live here — api_gateway.py just
delegates to the registry.
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

# ── Model catalogue ─────────────────────────────────────────────────────────
# Add new models here. Only the model file needs to exist in /models.
# 'active' is controlled at runtime via POST /api/models/switch

_BASE_DIR = Path(__file__).parent.parent

MODEL_CATALOGUE: List[Dict[str, Any]] = [
    {
        "id": "deepseek-r1-1.5b-q4",
        "name": "DeepSeek-R1 1.5B (Q4)",
        "description": "Primary model — fast, 2GB-safe",
        "filename": "deepseek-r1-1.5b-q4.gguf",
        "parameters": "1.5B",
        "quantization": "Q4_K_M",
        "context_length": 512,
        "recommended_threads": 2,
        "recommended_batch": 256,
        "tags": ["reasoning", "fast", "2gb-safe"],
    },
    {
        "id": "deepseek-r1-7b-q4",
        "name": "DeepSeek-R1 7B (Q4)",
        "description": "Larger model — higher quality, needs 4GB+",
        "filename": "deepseek-r1-7b-q4.gguf",
        "parameters": "7B",
        "quantization": "Q4_K_M",
        "context_length": 1024,
        "recommended_threads": 4,
        "recommended_batch": 512,
        "tags": ["reasoning", "quality"],
    },
    {
        "id": "phi-3-mini-q4",
        "name": "Phi-3 Mini (Q4)",
        "description": "Microsoft Phi-3 — compact with strong reasoning",
        "filename": "phi-3-mini-4k-instruct-q4.gguf",
        "parameters": "3.8B",
        "quantization": "Q4_K_M",
        "context_length": 4096,
        "recommended_threads": 2,
        "recommended_batch": 256,
        "tags": ["reasoning", "instruction-tuned"],
    },
]


class ModelRegistry:
    """
    Manages model catalogue and active model state.
    Thread-safe: active_model_id is read-only after init except via switch().
    """

    def __init__(self):
        self._catalogue: Dict[str, Dict] = {}
        self._active_id: Optional[str] = None

        for m in MODEL_CATALOGUE:
            self._catalogue[m["id"]] = m

        # Set active model from env or first available
        env_model = os.getenv("DEFAULT_MODEL_ID", "")
        if env_model and env_model in self._catalogue:
            self._active_id = env_model
        else:
            self._active_id = MODEL_CATALOGUE[0]["id"]

        logger.info(f"ModelRegistry: {len(self._catalogue)} models registered, active='{self._active_id}'")

    def list_models(self) -> List[Dict]:
        """Return all models with availability status (no filesystem paths)."""
        result = []
        for m in MODEL_CATALOGUE:
            path = _BASE_DIR / "models" / m["filename"]
            result.append({
                "id": m["id"],
                "name": m["name"],
                "description": m["description"],
                "parameters": m["parameters"],
                "quantization": m["quantization"],
                "context_length": m["context_length"],
                "tags": m["tags"],
                "available": path.exists(),
                "active": m["id"] == self._active_id,
            })
        return result

    def get_active(self) -> Dict:
        """Return active model definition (with filesystem path for internal use)."""
        active_id: str = self._active_id or MODEL_CATALOGUE[0]["id"]
        m = self._catalogue[active_id]
        m_copy = dict(m)
        m_copy["path"] = str(_BASE_DIR / "models" / m["filename"])
        return m_copy

    def switch(self, model_id: str) -> Dict:
        """
        Switch active model. Returns new active model info.
        Raises ValueError if model_id is unknown or file not present.
        """
        if model_id not in self._catalogue:
            raise ValueError(f"Unknown model id: '{model_id}'. Available: {list(self._catalogue)}")

        m = self._catalogue[model_id]
        path = _BASE_DIR / "models" / m["filename"]
        if not path.exists():
            raise ValueError(
                f"Model file not found: {m['filename']}. "
                f"Download it and place in /models/."
            )

        self._active_id = model_id
        logger.info(f"ModelRegistry: switched active model → '{model_id}'")
        return self.get_active()

    @property
    def active_id(self) -> str:
        """ID of the currently active model."""
        return self._active_id or MODEL_CATALOGUE[0]["id"]


# Singleton
model_registry = ModelRegistry()
