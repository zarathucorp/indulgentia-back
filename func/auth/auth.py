import os
from dotenv import load_dotenv
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status, Security, APIRouter, Request
from pydantic import BaseModel
import jwt
from jwt import PyJWTError
import secrets
from datetime import datetime, timedelta



load_dotenv()

JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")
JWT_ALGORITHM = os.getenv("SUPABASE_JWT_ALGORITHM")

security = HTTPBearer()


class TokenPayload(BaseModel):
    username: str
    id: str
    is_admin: bool


def decode_jwt(token: str) -> TokenPayload:
    try:
        decoded_token = jwt.decode(
            token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return TokenPayload(**decoded_token)
    except PyJWTError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Could not validate credentials")


def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> TokenPayload:
    return decode_jwt(credentials.credentials)

