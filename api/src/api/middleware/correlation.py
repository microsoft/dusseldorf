from fastapi import Request, Response
from typing import Callable
import uuid

async def correlation_middleware(
    request: Request,
    call_next: Callable
) -> Response:
    """Add correlation ID to request/response cycle"""
    # Get or generate correlation ID
    correlation_id = request.headers.get(
        "X-Correlation-ID",
        str(uuid.uuid4())
    )
    
    # Add to request state
    request.state.correlation_id = correlation_id
    
    # Process request
    response = await call_next(request)
    
    # Add to response headers
    response.headers["X-Correlation-ID"] = correlation_id
    
    return response 