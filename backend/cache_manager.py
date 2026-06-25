"""
Persistent cache backed by SQLite — drop-in replacement for a plain dict.
The stored tuple format mirrors the in-memory pattern:  cache[key] = (timestamp, data)
"""

import sqlite3
import json
import time
from pathlib import Path

_DB_PATH = Path(__file__).parent.parent / "data" / "cache" / "football_cache.db"
_CACHE_TTL = 3600  # seconds — must match main.py CACHE_TTL


def _conn() -> sqlite3.Connection:
    c = sqlite3.connect(str(_DB_PATH), check_same_thread=False)
    c.execute("PRAGMA journal_mode=WAL")
    return c


def _init() -> None:
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _conn() as c:
        c.execute(
            "CREATE TABLE IF NOT EXISTS cache "
            "(key TEXT PRIMARY KEY, data TEXT NOT NULL, ts REAL NOT NULL)"
        )
        # Clean up already-expired entries on startup
        c.execute("DELETE FROM cache WHERE ts < ?", (time.time() - _CACHE_TTL,))
        c.commit()


class PersistentCache:
    """
    Dict-like interface over SQLite so main.py requires no changes beyond
    swapping  cache = {}  →  cache = PersistentCache()

    Stored values are always (timestamp: float, payload: dict) tuples,
    serialised to JSON in the DB.
    """

    def __init__(self) -> None:
        _init()
        self._hits = 0
        self._misses = 0

    # ── dict interface ────────────────────────────────────────────────────────

    def __setitem__(self, key: str, value: tuple) -> None:
        ts, data = value
        with _conn() as c:
            c.execute(
                "INSERT OR REPLACE INTO cache (key, data, ts) VALUES (?,?,?)",
                (key, json.dumps(data, default=str), ts),
            )
            c.commit()

    def __getitem__(self, key: str) -> tuple:
        with _conn() as c:
            row = c.execute(
                "SELECT data, ts FROM cache WHERE key=?", (key,)
            ).fetchone()
        if row is None:
            raise KeyError(key)
        return row[1], json.loads(row[0])

    def __contains__(self, key: object) -> bool:
        with _conn() as c:
            row = c.execute(
                "SELECT 1 FROM cache WHERE key=?", (key,)
            ).fetchone()
        return row is not None

    def __delitem__(self, key: str) -> None:
        with _conn() as c:
            c.execute("DELETE FROM cache WHERE key=?", (key,))
            c.commit()

    # ── extras ────────────────────────────────────────────────────────────────

    def stats(self) -> dict:
        with _conn() as c:
            count = c.execute("SELECT COUNT(*) FROM cache").fetchone()[0]
        size_kb = round(_DB_PATH.stat().st_size / 1024, 1) if _DB_PATH.exists() else 0
        return {
            "entries":    count,
            "file_size_kb": size_kb,
            "ttl_seconds":  _CACHE_TTL,
            "hits":       self._hits,
            "misses":     self._misses,
            "db_path":    str(_DB_PATH),
        }

    def clear(self) -> int:
        with _conn() as c:
            n = c.execute("SELECT COUNT(*) FROM cache").fetchone()[0]
            c.execute("DELETE FROM cache")
            c.commit()
        return n

    def clear_expired(self) -> int:
        cutoff = time.time() - _CACHE_TTL
        with _conn() as c:
            n = c.execute(
                "SELECT COUNT(*) FROM cache WHERE ts < ?", (cutoff,)
            ).fetchone()[0]
            c.execute("DELETE FROM cache WHERE ts < ?", (cutoff,))
            c.commit()
        return n
