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
    prefix="/admin",
    responses={404: {"description": "Not found"}},
)


class AdminBase(BaseModel):
    email: str


class AdminChangePassword(AdminBase):
    password: str


class AdminSetAdmin(AdminBase):
    is_admin: bool


@router.post("/user/verify", tags=["admin"])
def verify_signup_user(req: Request, user: AdminBase):
    admin_user: UUID4 = verify_user(req)
    if not admin_user:
        raise_custom_error(403, 213)
    admin_user_data, count = supabase.table("user_setting").select(
        "*").eq("is_deleted", False).eq("id", admin_user).execute()
    print(admin_user_data[1])
    if admin_user_data[1][0]["is_admin"] == False:
        raise_custom_error(403, 200)
    user_data, count = supabase.table("user_setting").select(
        "*").eq("is_deleted", False).eq("email", user.email).execute()
    if not user_data:
        raise_custom_error(401, 110)

    response = supabase.auth.admin.update_user_by_id(
        user_data[1][0]["id"],
        {"email_confirm": True}
    )

    return JSONResponse(content={
        "status": "succeed",
        "email": user.email
    })


@router.post("/user/reset-password", tags=["admin"])
def reset_user_password(req: Request, user: AdminBase):
    admin_user: UUID4 = verify_user(req)
    if not admin_user:
        raise_custom_error(403, 213)
    admin_user_data, count = supabase.table("user_setting").select(
        "*").eq("is_deleted", False).eq("id", admin_user).execute()
    if admin_user_data[1][0]["is_admin"] == False:
        raise_custom_error(403, 200)
    user_data, count = supabase.table("user_setting").select(
        "*").eq("is_deleted", False).eq("email", user.email).execute()
    if not user_data:
        raise_custom_error(401, 110)

    response = supabase.auth.admin.update_user_by_id(
        user_data[1][0]["id"],
        {"password": f"{user.email}"}
    )

    return JSONResponse(content={
        "status": "succeed",
        "email": user.email,
    })


@router.post("/user/change-password", tags=["admin"])
def change_user_password(req: Request, user: AdminChangePassword):
    admin_user: UUID4 = verify_user(req)
    if not admin_user:
        raise_custom_error(403, 213)
    admin_user_data, count = supabase.table("user_setting").select(
        "*").eq("is_deleted", False).eq("id", admin_user).execute()
    if admin_user_data[1][0]["is_admin"] == False:
        raise_custom_error(403, 200)
    user_data, count = supabase.table("user_setting").select(
        "*").eq("is_deleted", False).eq("email", user.email).execute()
    if not user_data:
        raise_custom_error(401, 110)

    response = supabase.auth.admin.update_user_by_id(
        user_data[1][0]["id"],
        {"password": f"{user.password}"}
    )

    return JSONResponse(content={
        "status": "succeed",
        "email": user.email,
    })


@router.post("/user/delete", tags=["admin"])
def delete_user(req: Request, user: AdminBase):
    admin_user: UUID4 = verify_user(req)
    if not admin_user:
        raise_custom_error(403, 213)
    admin_user_data, count = supabase.table("user_setting").select(
        "*").eq("is_deleted", False).eq("id", admin_user).execute()
    if admin_user_data[1][0]["is_admin"] == False:
        raise_custom_error(403, 200)
    user_data, count = supabase.table("user_setting").select(
        "*").eq("is_deleted", False).eq("email", user.email).execute()
    if not user_data:
        raise_custom_error(401, 110)

    response = supabase.auth.admin.delete_user(
        id=user_data[1][0]["id"],
        should_soft_delete=True
    )

    return JSONResponse(content={
        "status": "succeed",
        "email": user.email,
    })


@router.get("/user/list", tags=["admin"])
def list_user(req: Request):
    admin_user: UUID4 = verify_user(req)
    if not admin_user:
        raise_custom_error(403, 213)
    admin_user_data, count = supabase.table("user_setting").select(
        "*").eq("is_deleted", False).eq("id", admin_user).execute()
    if admin_user_data[1][0]["is_admin"] == False:
        raise_custom_error(403, 200)
    user_data, count = supabase.table("user_setting").select(
        "*").eq("is_deleted", False).execute()

    return JSONResponse(content={
        "status": "succeed",
        "users": user_data[1],
    })


@router.get("/user/{user_id}", tags=["admin"])
def get_user(req: Request, user_id: UUID4):
    admin_user: UUID4 = verify_user(req)
    if not admin_user:
        raise_custom_error(403, 213)
    admin_user_data, count = supabase.table("user_setting").select(
        "*").eq("is_deleted", False).eq("id", admin_user).execute()
    if admin_user_data[1][0]["is_admin"] == False:
        raise_custom_error(403, 200)
    user_data, count = supabase.table("user_setting").select(
        "*").eq("is_deleted", False).eq("id", user_id).execute()
    if not user_data:
        raise_custom_error(401, 110)

    return JSONResponse(content={
        "status": "succeed",
        "user": user_data[1][0],
    })


@router.post("/user/set-admin", tags=["admin"])
def set_admin(req: Request, user: AdminSetAdmin):
    admin_user: UUID4 = verify_user(req)
    if not admin_user:
        raise_custom_error(403, 213)
    admin_user_data, count = supabase.table("user_setting").select(
        "*").eq("is_deleted", False).eq("id", admin_user).execute()
    if admin_user_data[1][0]["is_admin"] == False:
        raise_custom_error(403, 200)
    user_data, count = supabase.table("user_setting").select(
        "*").eq("is_deleted", False).eq("email", user.email).execute()
    if not user_data:
        raise_custom_error(401, 110)

    user_data, count = supabase.table("user_setting").update({"is_admin": user.is_admin}).eq(
        "id", user_data[1][0]["id"]).eq("is_deleted", False).execute()

    return JSONResponse(content={
        "status": "succeed",
        "data": user_data[1][0],
    })
