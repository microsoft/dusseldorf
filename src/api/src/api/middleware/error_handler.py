from fastapi import Request, Response
from fastapi.responses import JSONResponse
from typing import Union
import traceback
import logging

logger = logging.getLogger(__name__)

async def error_handler_middleware(
    request: Request,
    call_next
) -> Union[Response, JSONResponse]:
    """Global error handling middleware"""
    try:
        return await call_next(request)
    except Exception as e:
        # Log the full error with traceback
        logger.error(
            f"Unhandled error processing request: {request.url}",
            exc_info=True
        )
        
        # Prepare error response
        error_detail = {
            "message": str(e),
            "type": type(e).__name__,
        }
        
        if request.app.debug:
            error_detail["traceback"] = traceback.format_exc()
            
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": error_detail,
                "path": str(request.url)
            }
        ) 