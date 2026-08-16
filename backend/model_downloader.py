# -*- coding: utf-8 -*-
"""
Model Downloader — background downloads for models missing from /models.

Mirrors scripts/download_model.py's download logic, but runs it in a
background thread and exposes progress over HTTP instead of a CLI progress
bar, so the model selector in the UI can offer "Download" for any catalogue
entry that isn't on disk yet.
"""

import logging
import threading
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional

from model_registry import MODEL_CATALOGUE, _BASE_DIR

logger = logging.getLogger(__name__)

MODELS_DIR = _BASE_DIR / "models"
_CHUNK_SIZE = 1024 * 1024  # 1MB


class ModelDownloadManager:
    """Tracks at most one in-flight download per model_id."""

    def __init__(self):
        self._lock = threading.Lock()
        self._state: Dict[str, Dict[str, Any]] = {}

    @staticmethod
    def _catalogue_entry(model_id: str) -> Optional[Dict[str, Any]]:
        for m in MODEL_CATALOGUE:
            if m["id"] == model_id:
                return m
        return None

    def get_status(self, model_id: str) -> Dict[str, Any]:
        with self._lock:
            state = self._state.get(model_id)
            return dict(state) if state else {"status": "idle"}

    def start(self, model_id: str) -> None:
        """Kick off a background download. Raises ValueError on bad input."""
        entry = self._catalogue_entry(model_id)
        if not entry:
            raise ValueError(f"Unknown model id: '{model_id}'")
        if not entry.get("download_url"):
            raise ValueError(f"No download URL registered for '{model_id}'")

        dest = MODELS_DIR / entry["filename"]
        if dest.exists():
            raise ValueError(f"Model '{model_id}' is already downloaded")

        with self._lock:
            current = self._state.get(model_id)
            if current and current.get("status") == "downloading":
                return  # already in progress — no-op, let the poller catch up
            self._state[model_id] = {
                "status": "downloading",
                "downloaded_mb": 0.0,
                "total_mb": round((entry.get("size_mb") or 0), 1),
                "percent": 0.0,
                "error": None,
            }

        thread = threading.Thread(
            target=self._run_download, args=(model_id, entry, dest), daemon=True
        )
        thread.start()

    def _run_download(self, model_id: str, entry: Dict[str, Any], dest: Path) -> None:
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        tmp_path = dest.with_suffix(dest.suffix + ".part")

        try:
            opener = urllib.request.build_opener()
            opener.addheaders = [("User-Agent", "Mozilla/5.0")]
            with opener.open(entry["download_url"]) as resp:
                total = int(resp.headers.get("Content-Length", 0))
                downloaded = 0
                last_update = 0.0

                with open(tmp_path, "wb") as f:
                    while True:
                        chunk = resp.read(_CHUNK_SIZE)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)

                        now = time.monotonic()
                        if now - last_update > 0.3:
                            last_update = now
                            self._update(model_id, downloaded, total)

            self._update(model_id, downloaded, total)
            tmp_path.rename(dest)
            with self._lock:
                self._state[model_id]["status"] = "completed"
                self._state[model_id]["percent"] = 100.0
            logger.info(f"✅ Model download completed: {model_id} -> {dest}")

        except Exception as e:
            logger.error(f"❌ Model download failed for {model_id}: {e}")
            try:
                if tmp_path.exists():
                    tmp_path.unlink()
            except OSError:
                pass
            with self._lock:
                prev_total = self._state.get(model_id, {}).get("total_mb", 0)
                self._state[model_id] = {
                    "status": "failed",
                    "downloaded_mb": 0.0,
                    "total_mb": prev_total,
                    "percent": 0.0,
                    "error": str(e),
                }

    def _update(self, model_id: str, downloaded: int, total: int) -> None:
        with self._lock:
            state = self._state.get(model_id)
            if not state:
                return
            state["downloaded_mb"] = round(downloaded / (1024 * 1024), 1)
            if total:
                state["total_mb"] = round(total / (1024 * 1024), 1)
                state["percent"] = round(downloaded * 100 / total, 1)


download_manager = ModelDownloadManager()
