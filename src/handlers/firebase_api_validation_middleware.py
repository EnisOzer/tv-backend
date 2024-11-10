from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
from starlette.middleware.base import BaseHTTPMiddleware
from firebase_admin import app_check
import jwt

class FirebaseValidationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        app_check_token = request.headers.get("X-Firebase-AppCheck")
        
        try:
            if not app_check_token:
                raise ValueError("X-Firebase-AppCheck token is missing")

            app_check_claims = app_check.verify_token(app_check_token)
            
        except (ValueError, jwt.exceptions.DecodeError) as ex:
            print(str(ex))
            return PlainTextResponse(status_code=401, content="Firebase validation failed.")

        response = await call_next(request)
        return response


