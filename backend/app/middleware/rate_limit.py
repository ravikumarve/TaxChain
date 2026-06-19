"""
Rate limiting middleware.
"""

import time
from functools import wraps
from fastapi import Request, HTTPException

_rate_limit_store = {}


def get_rate_limit_key(request, endpoint):
    client_ip = request.client.host
    return f"{client_ip}:{endpoint}"


def check_rate_limit(request, endpoint):
    rate_limit_config = {"requests": 10, "window": 60}
    max_requests = rate_limit_config["requests"]
    window_seconds = rate_limit_config["window"]

    key = get_rate_limit_key(request, endpoint)
    current_time = time.time()

    if key not in _rate_limit_store:
        _rate_limit_store[key] = {"timestamps": []}

    store = _rate_limit_store[key]
    store["timestamps"] = [
        ts for ts in store["timestamps"] if current_time - ts < window_seconds
    ]

    if len(store["timestamps"]) >= max_requests:
        return False

    store["timestamps"].append(current_time)
    return True


def rate_limit_middleware(endpoint):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Find the Request object in args/kwargs (FastAPI injects it)
            request = next((a for a in args if isinstance(a, Request)), None) or kwargs.get("request")
            if request and not check_rate_limit(request, endpoint):
                raise HTTPException(
                    status_code=429, detail="Too many requests. Please try again later."
                )
            return await func(*args, **kwargs)

        return wrapper

    return decorator


reports_rate_limit = rate_limit_middleware("reports")
