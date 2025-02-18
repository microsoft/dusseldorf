from fastapi import Request, Response
from typing import Callable
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
import time

tracer = trace.get_tracer(__name__)

async def telemetry_middleware(
    request: Request,
    call_next: Callable
) -> Response:
    """OpenTelemetry middleware for request tracing"""
    request_id = request.state.correlation_id
    
    with tracer.start_as_current_span(
        name=f"{request.method} {request.url.path}",
        kind=trace.SpanKind.SERVER,
        attributes={
            "http.method": request.method,
            "http.url": str(request.url),
            "http.request_id": request_id,
            "http.client_ip": request.client.host
        }
    ) as span:
        try:
            # Process request and measure timing
            start_time = time.time()
            response = await call_next(request)
            duration = time.time() - start_time
            
            # Add response attributes to span
            span.set_attribute("http.status_code", response.status_code)
            span.set_attribute("http.duration", duration)
            
            if 200 <= response.status_code < 400:
                span.set_status(Status(StatusCode.OK))
            else:
                span.set_status(Status(StatusCode.ERROR))
                
            return response
            
        except Exception as e:
            # Record exception in span
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR))
            raise 