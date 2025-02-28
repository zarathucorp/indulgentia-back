import os
from dotenv import load_dotenv
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status, Security, APIRouter, Request
from pydantic import BaseModel, UUID4
import jwt
from jwt import PyJWTError
import secrets
from datetime import datetime, timedelta
from database.supabase import supabase
from gotrue.errors import AuthApiError
from env import SUPABASE_URL
import uuid
from func.error.error import raise_custom_error
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


def verify_user(req: Request) -> UUID4:
    import urllib.parse
    import json
    from fastapi import HTTPException
    SUPABASE_URL_REFERENCE_ID = SUPABASE_URL.replace(
        "https://", "").replace(".supabase.co", "")
    # ID/PW 로그인은 여기서 처리
    SUPABASE_COOKIE = req.cookies.get(
        f"sb-{SUPABASE_URL_REFERENCE_ID}-auth-token")
    # Cookie가 길어서 0, 1로 나누어진 경우도 있음.

    if SUPABASE_COOKIE is None:
        SUPABASE_COOKIE = ""
        cookie_order = 0
        while True:
            if req.cookies.get(f"sb-{SUPABASE_URL_REFERENCE_ID}-auth-token.{cookie_order}") == None:
                break
            SUPABASE_COOKIE = SUPABASE_COOKIE + req.cookies.get(
                f"sb-{SUPABASE_URL_REFERENCE_ID}-auth-token.{cookie_order}")
            cookie_order += 1

    # 쿠키 없는경우 Exception
    if (SUPABASE_COOKIE is None) | (SUPABASE_COOKIE == ""):
        print(req.__dict__)
        raise_custom_error(403, 211)
        # raise HTTPException(status_code=401, detail="Unauthorized")
    SUPABASE_COOKIE_DICT = json.loads(urllib.parse.unquote(
        SUPABASE_COOKIE))
    access_token = SUPABASE_COOKIE_DICT.get("access_token")
    try:
        data = supabase.auth.get_user(access_token)
        user = data.user
        return user.id
    except AuthApiError:
        raise_custom_error(401, 110)
        # raise HTTPException(status_code=401, detail="Unauthorized")
    except Exception as e:
        raise_custom_error(500, 200)
        # raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")


# 최적화 필요함 (너무 많은 Query 요청)
# N + 1 query problem -> join?
def verify_team(user_id: UUID4, team_id: UUID4) -> bool:
    # Left
    data, count = supabase.table("user_setting").select(
        "team_id").eq("is_deleted", False).eq("id", user_id).execute()
    if not data[1]:
        raise_custom_error(500, 231)
    left_team_id = uuid.UUID(data[1][0].get("team_id"))

    return left_team_id == team_id
