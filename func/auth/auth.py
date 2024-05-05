import os
from dotenv import load_dotenv
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status, Security, APIRouter, Request
from pydantic import BaseModel
import jwt
from jwt import PyJWTError
import secrets
from datetime import datetime, timedelta
from database.supabase import supabase
from gotrue.errors import AuthApiError

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


def verify_user(req: Request):
    import urllib.parse
    import json
    from fastapi import HTTPException
    SUPABASE_URL_REFERENCE_ID = SUPABASE_URL.replace(
        "https://", "").replace(".supabase.co", "")
    print(SUPABASE_URL_REFERENCE_ID)
    SUPABASE_COOKIE = req.cookies.get(
        f"sb-{SUPABASE_URL_REFERENCE_ID}-auth-token")
    SUPABASE_COOKIE_DICT = json.loads(urllib.parse.unquote(
        SUPABASE_COOKIE))
    access_token = SUPABASE_COOKIE_DICT["access_token"]
    try:
        data = supabase.auth.get_user(access_token + "1")
        user = data.user
        return user.id
    except AuthApiError:
        raise HTTPException(status_code=401, detail="Unauthorized")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Internal Server Error: {e}")
