\"\"\"Simple ThreadPool-based async worker for Phase 0 background tasks.\"\"\"
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable, Any

# Small pool for background tasks (embeddings, heavy IO)
_executor = ThreadPoolExecutor(max_workers=2)


def submit_task(func: Callable, *args, **kwargs) -> Future:
    \"\"\"Submit a callable to the thread pool and return a Future.\"\"\"
    return _executor.submit(func, *args, **kwargs)


def shutdown(wait: bool = True) -> None:
    \"\"\"Shutdown the thread pool executor.\"\"\"
    _executor.shutdown(wait=wait)

