import logging
import hashlib
import hmac
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

class SignatureMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        if request.method == "POST" and request.url.path == "/webhook":
            signature = request.headers.get("X-Hub-Signature-256", "")[7:]
            payload = await request.body()
            expected_signature = hmac.new(
                bytes(request.app.state.config.APP_SECRET, "latin-1"),
                msg=payload,
                digestmod=hashlib.sha256,
            ).hexdigest()

            if not hmac.compare_digest(expected_signature, signature):
                logging.info("Signature verification failed!")
                return JSONResponse(
                    content={"status": "error", "message": "Invalid signature"},
                    status_code=403
                )
        response = await call_next(request)
        return response
