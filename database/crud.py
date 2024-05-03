import json
from fastapi.responses import JSONResponse
from gotrue.errors import AuthApiError

from database.supabase import supabase
from database import schemas



def create_user(user: schemas.UserCreate):
    try:
        user = user.model_dump()
        email = user.pop("email")
        password = user.pop("password")

        print('='*120)
        print({**user})
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "data": {**user}
        })
        # auth_response
        print(auth_response)
        return JSONResponse(status_code=200, content={
            "status": "success", "message": "User created successfully",
            "data": auth_response.user.model_dump()
                })
    except AuthApiError as message:
        print('='*120)
        print(message)
        return JSONResponse(status_code=400, content={"message": str(message)})
