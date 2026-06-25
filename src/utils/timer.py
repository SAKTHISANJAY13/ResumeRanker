"""Execution timer utility for benchmarking code blocks."""

import time
from typing import Type, Optional

class Timer:
    """A context manager to measure execution time of a code block."""

    def __enter__(self) -> 'Timer':
        self.start_time = time.perf_counter()
        self.elapsed: float = 0.0
        return self

    def __exit__(self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[object]) -> None:
        self.end_time = time.perf_counter()
        self.elapsed = self.end_time - self.start_time
