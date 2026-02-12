# backend/app/cache_service.py
"""
Disk-based Cache Service for Phase-3.

Uses `diskcache` for zero-infrastructure caching of:
- ML findings (24h TTL)
- Generated reports (24h TTL)
- LLM responses (1h TTL)

No Redis required — stores directly on disk with SQLite indexing.
"""

import json
import hashlib
from pathlib import Path
from typing import Optional, Any, Dict

try:
    import diskcache
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    print("[cache] ⚠️ diskcache not installed. Caching disabled. Run: pip install diskcache")


# =============================================================================
# Configuration
# =============================================================================

CACHE_DIR = Path(__file__).parent / ".cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# TTL constants (seconds)
TTL_FINDINGS = 60 * 60 * 24      # 24 hours
TTL_REPORTS = 60 * 60 * 24       # 24 hours
TTL_LLM = 60 * 60                # 1 hour
TTL_AGENT = 60 * 60 * 2          # 2 hours


# =============================================================================
# Cache Instance
# =============================================================================

_cache = None

def get_cache():
    """Get or create cache instance (lazy init)."""
    global _cache
    if not CACHE_AVAILABLE:
        return None
    if _cache is None:
        _cache = diskcache.Cache(
            str(CACHE_DIR),
            size_limit=500 * 1024 * 1024  # 500MB max
        )
    return _cache


# =============================================================================
# Cache Operations
# =============================================================================

def cache_get(key: str) -> Optional[Any]:
    """Get a value from cache. Returns None on miss."""
    cache = get_cache()
    if cache is None:
        return None
    try:
        return cache.get(key)
    except Exception:
        return None


def cache_set(key: str, value: Any, ttl: int = TTL_FINDINGS) -> bool:
    """Set a value in cache with TTL."""
    cache = get_cache()
    if cache is None:
        return False
    try:
        cache.set(key, value, expire=ttl)
        return True
    except Exception:
        return False


def cache_delete(key: str) -> bool:
    """Delete a key from cache."""
    cache = get_cache()
    if cache is None:
        return False
    try:
        cache.delete(key)
        return True
    except Exception:
        return False


def cache_clear() -> bool:
    """Clear all cached data."""
    cache = get_cache()
    if cache is None:
        return False
    try:
        cache.clear()
        return True
    except Exception:
        return False


# =============================================================================
# Domain-specific Cache Helpers
# =============================================================================

def cache_findings(case_id: str, findings: Dict) -> bool:
    """Cache ML findings for a case."""
    return cache_set(f"findings:{case_id}", findings, TTL_FINDINGS)


def get_cached_findings(case_id: str) -> Optional[Dict]:
    """Get cached findings for a case."""
    return cache_get(f"findings:{case_id}")


def cache_llm_response(prompt_hash: str, response: str) -> bool:
    """Cache an LLM response."""
    return cache_set(f"llm:{prompt_hash}", response, TTL_LLM)


def get_cached_llm_response(prompt_hash: str) -> Optional[str]:
    """Get a cached LLM response."""
    return cache_get(f"llm:{prompt_hash}")


def make_prompt_hash(prompt: str, context: str = "") -> str:
    """Create a deterministic hash for an LLM prompt + context."""
    content = f"{prompt}|{context}"
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def cache_report_path(case_id: str, report_type: str, path: str) -> bool:
    """Cache the path of a generated report."""
    return cache_set(f"report:{case_id}:{report_type}", path, TTL_REPORTS)


def get_cached_report_path(case_id: str, report_type: str) -> Optional[str]:
    """Get cached report path."""
    return cache_get(f"report:{case_id}:{report_type}")


# =============================================================================
# Stats
# =============================================================================

def get_cache_stats() -> Dict:
    """Get cache statistics."""
    cache = get_cache()
    if cache is None:
        return {"available": False}
    
    try:
        return {
            "available": True,
            "size_bytes": cache.volume(),
            "num_keys": len(cache),
            "cache_dir": str(CACHE_DIR)
        }
    except Exception as e:
        return {"available": True, "error": str(e)}
