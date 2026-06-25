"""Lightweight logger utility for performance tracking and pipeline statistics."""

import sys
import time
import resource
from typing import Optional

class Logger:
    """Lightweight console logger with standard formatting."""
    
    @staticmethod
    def _get_timestamp() -> str:
        """Returns the current timestamp in ISO format."""
        return time.strftime("%Y-%m-%d %H:%M:%S")

    @classmethod
    def info(cls, message: str) -> None:
        """Logs an informational message to stdout."""
        print(f"[{cls._get_timestamp()}] [INFO] {message}", file=sys.stdout)
        sys.stdout.flush()

    @classmethod
    def warning(cls, message: str) -> None:
        """Logs a warning message to stderr."""
        print(f"[{cls._get_timestamp()}] [WARNING] {message}", file=sys.stderr)
        sys.stderr.flush()

    @classmethod
    def error(cls, message: str) -> None:
        """Logs an error message to stderr."""
        print(f"[{cls._get_timestamp()}] [ERROR] {message}", file=sys.stderr)
        sys.stderr.flush()

    @staticmethod
    def get_peak_memory_mb() -> float:
        """Returns the peak memory usage of the process in MB.
        
        Handles difference between Darwin (macOS - bytes) and Linux (kilobytes).
        """
        usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        if sys.platform == "darwin":
            return usage / (1024 * 1024)
        else:
            return usage / 1024
