"""Thread-safe lazy singletons for synchronous factory callables."""

from __future__ import annotations

import threading
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def thread_safe_singleton(factory: Callable[[], T]) -> Callable[[], T]:
    """Return a getter that invokes ``factory`` at most once, safely under concurrent access."""
    lock = threading.Lock()
    cell: list[T | None] = [None]

    def get() -> T:
        res = cell[0]
        if res is not None:
            return res
        with lock:
            if cell[0] is None:
                cell[0] = factory()
            res = cell[0]
            assert res is not None
            return res

    return get
