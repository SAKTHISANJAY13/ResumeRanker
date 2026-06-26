"""Streaming candidate loader from gzipped JSONL files."""

import gzip
from typing import Generator, Dict, Any
import orjson
from src.utils.logger import Logger

def load_candidates(path: str) -> Generator[Dict[str, Any], None, None]:
    """Streams candidate records from a gzipped or plain text JSON Lines file.
    
    Args:
        path: Path to the candidates file (either .gz or uncompressed).
        
    Yields:
        Parsed candidate records as dictionaries.
    """
    try:
        is_gzip = path.endswith(".gz")
        open_func = gzip.open if is_gzip else open
        with open_func(path, "rb") as f:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    candidate = orjson.loads(line)
                    if isinstance(candidate, dict):
                        yield candidate
                    else:
                        Logger.warning(f"Line {line_no} parsed, but not a JSON object: {candidate}")
                except orjson.JSONDecodeError as jde:
                    Logger.warning(f"Failed to parse JSON at line {line_no}: {jde}")
                except Exception as e:
                    Logger.warning(f"Unexpected error parsing line {line_no}: {e}")
    except FileNotFoundError:
        Logger.error(f"Candidates file not found at path: {path}")
        raise
    except Exception as e:
        Logger.error(f"Failed to open candidates file {path}: {e}")
        raise
