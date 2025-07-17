#!/usr/bin/env python3
"""
Simple caching system for bot settings and user data.
"""

import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Simple in-memory cache
_cache: Dict[str, Dict[str, Any]] = {}
_cache_timestamps: Dict[str, float] = {}

# Cache TTL settings (in seconds)
SETTINGS_CACHE_TTL = 300  # 5 minutes
USER_CACHE_TTL = 60       # 1 minute
DEFAULT_TTL = 300         # 5 minutes


def _is_expired(key: str, ttl: int = DEFAULT_TTL) -> bool:
    """Check if a cache entry is expired."""
    if key not in _cache_timestamps:
        return True
    return time.time() - _cache_timestamps[key] > ttl


def _set_cache(key: str, value: Any, ttl: int = DEFAULT_TTL) -> None:
    """Set a cache entry."""
    _cache[key] = value
    _cache_timestamps[key] = time.time()


def _get_cache(key: str, ttl: int = DEFAULT_TTL) -> Optional[Any]:
    """Get a cache entry if not expired."""
    if key not in _cache or _is_expired(key, ttl):
        return None
    return _cache[key]


def _delete_cache(key: str) -> None:
    """Delete a cache entry."""
    _cache.pop(key, None)
    _cache_timestamps.pop(key, None)


def get_setting_cached(setting_key: str) -> Optional[str]:
    """
    Get a setting from cache or database.

    Args:
        setting_key: The setting key to retrieve

    Returns:
        The setting value or None if not found
    """
    cache_key = f"setting:{setting_key}"

    # Try cache first
    cached_value = _get_cache(cache_key, SETTINGS_CACHE_TTL)
    if cached_value is not None:
        return cached_value

    # Fallback to getting setting without cache
    try:
        # Import here to avoid circular imports
        from bot import get_setting
        value = get_setting(setting_key)

        # Cache the result
        if value is not None:
            _set_cache(cache_key, value, SETTINGS_CACHE_TTL)

        return value
    except ImportError:
        logger.warning("Could not import get_setting function")
        return None
    except Exception as e:
        logger.error(f"Error getting setting {setting_key}: {e}")
        return None


def invalidate_user_cache(user_id: int) -> None:
    """
    Invalidate all cache entries for a specific user.

    Args:
        user_id: The user ID to invalidate cache for
    """
    keys_to_delete = []
    for key in _cache.keys():
        if key.startswith(f"user:{user_id}:"):
            keys_to_delete.append(key)

    for key in keys_to_delete:
        _delete_cache(key)

    logger.debug(f"Invalidated {len(keys_to_delete)} cache entries for user {user_id}")


def invalidate_settings_cache() -> None:
    """Invalidate all settings cache entries."""
    keys_to_delete = []
    for key in _cache.keys():
        if key.startswith("setting:"):
            keys_to_delete.append(key)

    for key in keys_to_delete:
        _delete_cache(key)

    logger.debug(f"Invalidated {len(keys_to_delete)} settings cache entries")


def get_user_credits_cached(user_id: int) -> Optional[int]:
    """
    Get user credits from cache or database.

    Args:
        user_id: The user ID to get credits for

    Returns:
        The user's credits or None if not found
    """
    cache_key = f"user:{user_id}:credits"

    # Try cache first
    cached_value = _get_cache(cache_key, USER_CACHE_TTL)
    if cached_value is not None:
        return cached_value

    # Fallback to getting credits without cache
    try:
        # Import here to avoid circular imports
        from bot import get_user_credits
        credits = get_user_credits(user_id)

        # Cache the result
        if credits is not None:
            _set_cache(cache_key, credits, USER_CACHE_TTL)

        return credits
    except ImportError:
        logger.warning("Could not import get_user_credits function")
        return None
    except Exception as e:
        logger.error(f"Error getting credits for user {user_id}: {e}")
        return None


def set_user_credits_cache(user_id: int, credits: int) -> None:
    """
    Set user credits in cache.

    Args:
        user_id: The user ID
        credits: The credits amount
    """
    cache_key = f"user:{user_id}:credits"
    _set_cache(cache_key, credits, USER_CACHE_TTL)


def clear_all_cache() -> None:
    """Clear all cache entries."""
    _cache.clear()
    _cache_timestamps.clear()
    logger.info("Cleared all cache entries")


def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    now = time.time()
    expired_count = 0
    valid_count = 0

    for key, timestamp in _cache_timestamps.items():
        if now - timestamp > DEFAULT_TTL:
            expired_count += 1
        else:
            valid_count += 1

    return {
        'total_entries': len(_cache),
        'valid_entries': valid_count,
        'expired_entries': expired_count,
        'cache_size_bytes': sum(len(str(v)) for v in _cache.values()),
        'oldest_entry_age': now - min(_cache_timestamps.values()) if _cache_timestamps else 0
    }


def cleanup_expired_cache() -> int:
    """Clean up expired cache entries and return count of removed entries."""
    keys_to_delete = []

    for key in _cache.keys():
        if _is_expired(key):
            keys_to_delete.append(key)

    for key in keys_to_delete:
        _delete_cache(key)

    logger.debug(f"Cleaned up {len(keys_to_delete)} expired cache entries")
    return len(keys_to_delete)