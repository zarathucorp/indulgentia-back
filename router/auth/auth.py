import os
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status, Security, APIRouter, Request, Cookie
from fastapi.responses import JSONResponse
from typing import Annotated, List
from pydantic import BaseModel
import jwt

from database.schemas import *
from database.supabase import supabase
from func.auth.auth import verify_user
from func.error.error import raise_custom_error


router = APIRouter(
    prefix="/auth",
    responses={404: {"description": "Not found"}},
)


# @router.get("/join")
# def join(request: Request):
#     # NewUser = schemas.UserCreate(
#     #     email="foo@bar.com",
#     #     password="foobar",
#     # )
#     NewUser = schemas.UserCreate(
#         email="koolerjaebee@gmail.com",
#         password="1q2w3e$r",
#         team_id=None,
#         signature_path=None,
#         is_admin=False,
#     )
#     res = supabase.auth.sign_up({"email": NewUser.email, "password": NewUser.password})
#     print('='*120)
#     print(res)

#     return res


# @router.get("/login")
# def login():
#     pass


# @router.get("/logout")
# def logout():
#     pass


@router.delete("/remove", tags=["auth"])
def remove_user(req: Request):
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    supabase.auth.admin.delete_user(id=user, should_soft_delete=True)
    return JSONResponse(content={
        "status": "succeed"
    })
    
