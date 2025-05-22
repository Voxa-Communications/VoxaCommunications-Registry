from lib.security.structs.apiRequest import APIRequest
from lib.security.structs.apiCalls import APICalls
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
from collections import defaultdict
from typing import Dict, List, Callable, Any, Optional, Tuple
from flask import request, jsonify

class RateLimiter:
    """
    Rate limiter to track and limit API requests.
    Integrated with API tracker for comprehensive request monitoring.
    """
    def __init__(self):
        # Store request counts per IP address or user ID
        # Format: {'identifier': [(timestamp, endpoint, request_id), ...]}
        self.request_history: Dict[str, List[Tuple]] = defaultdict(list)
        # Default rate limits: requests per window (in seconds) per endpoint
        self.default_rate_limits = {
            'global': {'limit': 100, 'window': 60},  # 100 requests per minute globally
            '/api/login': {'limit': 5, 'window': 60},  # 5 login attempts per minute
            '/api/register': {'limit': 3, 'window': 60},  # 3 registration attempts per minute
            '/api/verify_2fa': {'limit': 5, 'window': 60},  # 5 2FA verification attempts per minute
        }
        self.custom_rate_limits = {}
        # Map request IDs to rate limiting actions
        self.rate_limited_requests = {}
        self.logger = log()

    def set_rate_limit(self, endpoint: str, limit: int, window: int):
        """
        Set a custom rate limit for a specific endpoint.
        
        Args:
            endpoint: API endpoint path
            limit: Number of requests allowed
            window: Time window in seconds
        """
        self.custom_rate_limits[endpoint] = {'limit': limit, 'window': window}
        self.logger.info(f"Set custom rate limit for {endpoint}: {limit} requests per {window} seconds")

    def get_rate_limit(self, endpoint: str):
        """
        Get the rate limit configuration for an endpoint.
        Falls back to global limit if endpoint-specific limit is not found.
        """
        if endpoint in self.custom_rate_limits:
            return self.custom_rate_limits[endpoint]
        elif endpoint in self.default_rate_limits:
            return self.default_rate_limits[endpoint]
        else:
            return self.default_rate_limits['global']

    def get_identifier(self) -> str:
        """
        Extract a unique identifier from the request.
        Uses user ID if authenticated, otherwise falls back to IP address.
        """
        # Try to get user ID from session or token
        user_id = request.headers.get('X-User-ID') or getattr(request, 'user_id', None)
        
        if user_id:
            return f"user:{user_id}"
        
        # Fall back to IP address
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        return f"ip:{ip}"

    def is_rate_limited(self, endpoint: str) -> bool:
        """
        Check if the current request exceeds the rate limit.
        
        Returns:
            True if request should be rate limited, False otherwise
        """
        identifier = self.get_identifier()
        now = time.time()
        rate_limit = self.get_rate_limit(endpoint)
        
        # Clean up old entries
        self.request_history[identifier] = [
            entry for entry in self.request_history[identifier] 
            if now - entry[0] < rate_limit['window']
        ]
        
        # Check endpoint-specific limit
        endpoint_requests = [
            entry for entry in self.request_history[identifier] 
            if entry[1] == endpoint
        ]
        
        # Check if limit exceeded
        is_limited = len(endpoint_requests) >= rate_limit['limit']
        
        # Log rate limit info
        if is_limited:
            self.logger.warning(f"Rate limit exceeded - Endpoint: {endpoint}, Identifier: {identifier}, " 
                f"Requests: {len(endpoint_requests)}/{rate_limit['limit']} in {rate_limit['window']}s", 
                level="WARNING")
        
        return is_limited

    def add_request(self, endpoint: str) -> str:
        """
        Record the current request in the rate limiting history.
        Also tracks the request in the API tracker.
        
        Returns:
            str: Request ID for tracking
        """
        identifier = self.get_identifier()
        now = time.time()
        
        # Generate a request ID for tracking
        request_id = f"{identifier}-{endpoint}-{now}"
        
        # Store in request history with request ID
        self.request_history[identifier].append((now, endpoint, request_id))
        
        # Create and record API request
        api_request = APIRequest(
            method=request.method, 
            endpoint=endpoint, 
            headers=dict(request.headers), 
            body=request.get_json(silent=True) or {},
            request_time=now
        )
        add_api_call(api_request)
        
        return request_id
    
    def mark_request_as_limited(self, request_id: str, endpoint: str):
        """
        Mark a request as rate-limited in the tracking system.
        
        Args:
            request_id: Unique identifier for the request
            endpoint: The endpoint that was accessed
        """
        self.rate_limited_requests[request_id] = {
            'endpoint': endpoint,
            'time': time.time(),
            'identifier': self.get_identifier()
        }
        
        # Log the rate limiting action
        self.logger.info(f"Request {request_id} to {endpoint} was rate-limited", level="INFO")
    
    def get_rate_limited_requests(self):
        """
        Get all requests that have been rate limited.
        
        Returns:
            dict: Dictionary of rate-limited requests
        """
        return self.rate_limited_requests
    
    def get_request_history_for_identifier(self, identifier: str) -> List[tuple]:
        """
        Get request history for a specific identifier.
        
        Args:
            identifier: User ID or IP address identifier
            
        Returns:
            List of request tuples (timestamp, endpoint, request_id)
        """
        return self.request_history.get(identifier, [])
    
    def get_all_request_history(self) -> Dict[str, List[tuple]]:
        """
        Get all request history tracked by the rate limiter.
        
        Returns:
            Dict mapping identifiers to their request histories
        """
        return self.request_history