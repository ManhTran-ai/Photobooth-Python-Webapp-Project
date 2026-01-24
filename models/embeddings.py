"""Helpers for embedding vector serialization and normalization."""
import io
import base64
import numpy as np


def l2_normalize(vec: np.ndarray) -> np.ndarray:
    arr = np.asarray(vec, dtype='float32')
    norm = np.linalg.norm(arr)
    if norm == 0:
        return arr
    return arr / norm


def serialize_embedding(vec: np.ndarray) -> str:
    """Serialize numpy array to base64 string for storage."""
    buf = io.BytesIO()
    # Use numpy savez to preserve dtype/shape
    np.save(buf, np.asarray(vec))
    return base64.b64encode(buf.getvalue()).decode('ascii')


def deserialize_embedding(encoded: str) -> np.ndarray:
    """Deserialize base64 string back to numpy array."""
    raw = base64.b64decode(encoded.encode('ascii'))
    buf = io.BytesIO(raw)
    buf.seek(0)
    arr = np.load(buf, allow_pickle=False)
    return arr

