from env import SUPABASE_URL, SUPABASE_KEY
from supabase import create_client, Client
from fastapi import Request
from gotrue.errors import AuthApiError

url: str = SUPABASE_URL
key: str = SUPABASE_KEY
supabase: Client = create_client(url, key)


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
