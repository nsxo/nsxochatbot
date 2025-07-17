#!/usr/bin/env python3
"""
Error handling and performance monitoring decorators.
"""

import logging
import time
import functools
from typing import Dict, Any, Callable, Optional
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

# Rate limiting storage
rate_limit_storage: Dict[str, deque] = defaultdict(lambda: deque())

# Performance monitoring storage
performance_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
    'total_calls': 0,
    'total_time': 0,
    'avg_time': 0,
    'max_time': 0,
    'min_time': float('inf')
})


def error_handler(func: Optional[Callable] = None, *, log_errors: bool = True, reraise: bool = True):
    """
    Decorator for handling errors in bot functions.

    Args:
        func: Function to decorate
        log_errors: Whether to log errors
        reraise: Whether to reraise exceptions after logging
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        async def wrapper(*args, **kwargs):
            try:
                return await f(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    logger.error(f"Error in {f.__name__}: {e}", exc_info=True)
                if reraise:
                    raise
                return None
        return wrapper

    if func is None:
        return decorator
    else:
        return decorator(func)


def rate_limit(max_calls: int = 10, window_seconds: int = 60):
    """
    Rate limiting decorator.

    Args:
        max_calls: Maximum number of calls allowed
        window_seconds: Time window in seconds
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Get a unique key for this function and user
            func_name = func.__name__
            user_id = None

            # Try to extract user_id from common argument patterns
            if args and hasattr(args[0], 'effective_user'):
                user_id = args[0].effective_user.id
            elif len(args) > 1 and hasattr(args[1], 'user_data'):
                user_id = getattr(args[1], 'user_id', None)

            rate_key = f"{func_name}:{user_id}" if user_id else func_name

            # Clean old entries
            now = time.time()
            storage = rate_limit_storage[rate_key]
            while storage and storage[0] < now - window_seconds:
                storage.popleft()

            # Check rate limit
            if len(storage) >= max_calls:
                logger.warning(f"Rate limit exceeded for {rate_key}")
                return None

            # Record this call
            storage.append(now)

            # Execute function
            return await func(*args, **kwargs)

        return wrapper
    return decorator


def monitor_performance(func: Callable) -> Callable:
    """
    Performance monitoring decorator.

    Args:
        func: Function to monitor
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()

        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            # Record performance stats
            execution_time = time.time() - start_time
            stats = performance_stats[func.__name__]

            stats['total_calls'] += 1
            stats['total_time'] += execution_time
            stats['avg_time'] = stats['total_time'] / stats['total_calls']
            stats['max_time'] = max(stats['max_time'], execution_time)
            stats['min_time'] = min(stats['min_time'], execution_time)

            # Log slow functions
            if execution_time > 1.0:  # Log if takes more than 1 second
                logger.warning(f"Slow function {func.__name__}: {execution_time:.2f}s")

    return wrapper


def get_performance_stats() -> Dict[str, Dict[str, Any]]:
    """Get current performance statistics."""
    return dict(performance_stats)


def reset_performance_stats() -> None:
    """Reset performance statistics."""
    performance_stats.clear()


def get_rate_limit_stats() -> Dict[str, int]:
    """Get current rate limit statistics."""
    return {key: len(calls) for key, calls in rate_limit_storage.items()}