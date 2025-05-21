from lib.security.structs.apiRequest import APIRequest
from lib.security.structs.apiCalls import APICalls
from lib.security.ratelimiter.structs import RateLimiter
from lib.security.trackers.api_tracker import (
    set_global_api_tracker,
    get_global_api_tracker,
    add_api_call,
    clear_api_calls,
    get_api_calls,
)
from util.timing_utils import constant_time_compare
from util.logging import log

import time
import functools
import uuid
from collections import defaultdict
from typing import Dict, List, Callable, Any, Optional
from flask import request, jsonify

MODULE_LOGGER = log()
# Create a global rate limiter instance
global_rate_limiter = RateLimiter()


def rate_limit(limit: Optional[int] = None, window: Optional[int] = None):
    """
    Decorator to apply rate limiting to a route.
    Integrates with API tracker to monitor all requests, including rate-limited ones.
    
    Args:
        limit: Optional override for number of requests allowed
        window: Optional override for time window in seconds
    
    Usage:
        @app.route('/api/endpoint')
        @rate_limit(limit=10, window=60)  # 10 requests per minute
        def my_endpoint():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            endpoint = request.path
            request_method = request.method
            request_body = request.get_json(silent=True) or {}
            
            # Set custom rate limit if provided
            if limit is not None and window is not None:
                global_rate_limiter.set_rate_limit(endpoint, limit, window)
                
            # Generate a unique request ID for tracking
            request_id = str(uuid.uuid4())
            
            # Check if rate limited before adding to history
            if global_rate_limiter.is_rate_limited(endpoint):
                MODULE_LOGGER.info(f"Rate limit exceeded for {endpoint} by {global_rate_limiter.get_identifier()}", 'WARNING')
                
                # Create API request with rate limit info
                now = time.time()
                rate_limited_api_request = APIRequest(
                    method=request_method,
                    endpoint=endpoint,
                    headers=dict(request.headers),
                    body={
                        "rate_limited": True,
                        "request_id": request_id,
                        "original_request": request_body
                    },
                    request_time=now
                )
                add_api_call(rate_limited_api_request)
                
                # Mark this request as rate-limited in our tracking
                global_rate_limiter.mark_request_as_limited(request_id, endpoint)
                
                response = jsonify({
                    "error": "Rate limit exceeded",
                    "message": "Too many requests. Please try again later.",
                    "status": 429,
                    "request_id": request_id
                })
                response.status_code = 429
                return response
                
            # Add request to rate limiter's history and API tracker
            request_id = global_rate_limiter.add_request(endpoint)
            
            # Add request ID to response headers for tracking
            response = func(*args, **kwargs)
            
            # If response is a tuple, it's (response, status_code) or (response, status_code, headers)
            if isinstance(response, tuple):
                response_obj = response[0]
                if hasattr(response_obj, 'headers'):
                    response_obj.headers['X-Request-ID'] = request_id
            # If response is a response object
            elif hasattr(response, 'headers'):
                response.headers['X-Request-ID'] = request_id
                
            return response
            
        return wrapper
    return decorator


def get_rate_stats(endpoint: Optional[str] = None, user_id: Optional[str] = None, ip: Optional[str] = None):
    """
    Get rate limiting statistics for analysis.
    
    Args:
        endpoint: Optional filter by endpoint
        user_id: Optional filter by user ID
        ip: Optional filter by IP address
        
    Returns:
        Dictionary with rate limiting statistics
    """
    # Get all API calls from the API tracker
    api_calls = get_api_calls()
    
    stats = {
        "total_tracked_requests": len(api_calls),
        "rate_limited_requests": len(global_rate_limiter.get_rate_limited_requests()),
        "rate_limits": global_rate_limiter.default_rate_limits,
        "custom_rate_limits": global_rate_limiter.custom_rate_limits,
    }
    
    # Get endpoint specific data if provided
    if endpoint:
        stats["endpoint"] = endpoint
        stats["endpoint_limit"] = global_rate_limiter.get_rate_limit(endpoint)
        endpoint_requests = [call for call in api_calls if call.endpoint == endpoint]
        stats["endpoint_request_count"] = len(endpoint_requests)
        
    # Filter by identifier if user_id or ip is provided
    identifier = None
    if user_id:
        identifier = f"user:{user_id}"
        stats["user_id"] = user_id
    elif ip:
        identifier = f"ip:{ip}"
        stats["ip"] = ip
        
    if identifier:
        history = global_rate_limiter.get_request_history_for_identifier(identifier)
        stats["request_count"] = len(history)
        if history:
            stats["first_request_time"] = history[0][0] if history else None
            stats["last_request_time"] = history[-1][0] if history else None
            
    return stats


def reset_rate_limiter():
    """
    Reset the rate limiter state (for testing purposes).
    """
    global global_rate_limiter
    global_rate_limiter = RateLimiter()
    clear_api_calls()
    MODULE_LOGGER.info("Rate limiter has been reset", "INFO")

