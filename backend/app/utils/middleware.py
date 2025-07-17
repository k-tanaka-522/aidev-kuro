from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
import structlog
from typing import Dict, Any
from collections import defaultdict
from datetime import datetime, timedelta


logger = structlog.get_logger()


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting Prometheus metrics"""
    
    def __init__(self, app):
        super().__init__(app)
        self.request_count = defaultdict(int)
        self.request_duration = defaultdict(list)
        
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Collect metrics
        method = request.method
        path = request.url.path
        status_code = response.status_code
        
        metric_key = f"{method}_{path}_{status_code}"
        self.request_count[metric_key] += 1
        self.request_duration[metric_key].append(duration)
        
        # Log request
        logger.info(
            "HTTP request",
            method=method,
            path=path,
            status_code=status_code,
            duration=duration,
            user_agent=request.headers.get("user-agent", "")
        )
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware"""
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients = defaultdict(list)
        
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host
        
        # Clean old requests
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=self.period)
        self.clients[client_ip] = [
            req_time for req_time in self.clients[client_ip]
            if req_time > cutoff
        ]
        
        # Check rate limit
        if len(self.clients[client_ip]) >= self.calls:
            logger.warning(
                "Rate limit exceeded",
                client_ip=client_ip,
                requests=len(self.clients[client_ip])
            )
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded", "retry_after": self.period}
            )
        
        # Record this request
        self.clients[client_ip].append(now)
        
        return await call_next(request)