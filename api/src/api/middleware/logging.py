from fastapi import Request, Response
from typing import Callable
import logging
import time
import json

logger = logging.getLogger(__name__)

async def logging_middleware(
    request: Request,
    call_next: Callable
) -> Response:
    """Request/Response logging middleware"""
    # Start timer
    start_time = time.time()
    
    # Log request
    await log_request(request)
    
    # Process request
    response = await call_next(request)
    
    # Log response
    await log_response(request, response, start_time)
    
    return response

async def log_request(request: Request) -> None:
    """Log incoming request details"""
    body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.json()
        except:
            body = await request.body()
            
    log_data = {
        "request_id": request.state.correlation_id,
        "method": request.method,
        "path": str(request.url),
        "headers": dict(request.headers),
        "query_params": dict(request.query_params),
        "client_ip": request.client.host,
        "body": body
    }
    
    logger.info(f"Incoming request: {json.dumps(log_data)}")

async def log_response(
    request: Request,
    response: Response,
    start_time: float
) -> None:
    """Log outgoing response details"""
    time_taken = time.time() - start_time
    
    log_data = {
        "request_id": request.state.correlation_id,
        "status_code": response.status_code,
        "time_taken": f"{time_taken:.4f}s",
        "headers": dict(response.headers)
    }
    
    logger.info(f"Outgoing response: {json.dumps(log_data)}") 