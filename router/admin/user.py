import os
from dotenv import load_dotenv
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status, Security, APIRouter, Request, Cookie
from fastapi.responses import JSONResponse
from typing import Annotated, List
from pydantic import BaseModel
import jwt
import uuid

from database.schemas import *
from database.supabase import supabase
from func.auth.auth import verify_user
from func.error.error import raise_custom_error

load_dotenv(verbose=True)

FRONTEND_URL = os.getenv("FRONTEND_URL")


router = APIRouter(
    prefix="/user",
    responses={404: {"description": "Not found"}},
)


class AdminBase(BaseModel):
    email: str


class AdminChangePassword(AdminBase):
    password: str


class AdminSetAdmin(AdminBase):
    is_admin: bool


@router.post("/verify", tags=["admin-user"])
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


@router.post("/reset-password", tags=["admin-user"])
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


@router.post("/change-password", tags=["admin-user"])
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


@router.post("/delete", tags=["admin-user"])
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


@router.get("/list", tags=["admin-user"])
def list_user(req: Request):
    admin_user: UUID4 = verify_user(req)
    if not admin_user:
        raise_custom_error(403, 213)
    admin_user_data, count = supabase.table("user_setting").select(
        "*").eq("is_deleted", False).eq("id", admin_user).execute()
    if admin_user_data[1][0]["is_admin"] == False:
        raise_custom_error(403, 200)
    # user_data, count = supabase.table("user_setting").select(
    #     "*").eq("is_deleted", False).execute()
    user_data, count = supabase.rpc(
        "get_user_settings_with_auth_info", {}).execute()

    return JSONResponse(content={
        "status": "succeed",
        "users": user_data[1],
    })


@router.get("/list/no-team", tags=["admin-user"])
def list_user_with_no_team(req: Request):
    admin_user: UUID4 = verify_user(req)
    if not admin_user:
        raise_custom_error(403, 213)
    admin_user_data, count = supabase.table("user_setting").select(
        "*").eq("is_deleted", False).eq("id", admin_user).execute()
    if admin_user_data[1][0]["is_admin"] == False:
        raise_custom_error(403, 200)
    user_data, count = supabase.table("user_setting").select(
        "*").is_("team_id", "null").eq("is_deleted", False).execute()

    return JSONResponse(content={
        "status": "succeed",
        "users": user_data[1],
    })


@router.get("/{user_id}", tags=["admin-user"])
def get_user(req: Request, user_id: str):
    try:
        uuid.UUID(user_id)
    except ValueError:
        raise_custom_error(422, 210)
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


@router.post("/{user_id}/set-admin", tags=["admin-user"])
def set_admin(req: Request, user_id: str, user: AdminSetAdmin):
    try:
        uuid.UUID(user_id)
    except ValueError:
        raise_custom_error(422, 210)
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
        "id", user_id).eq("is_deleted", False).execute()

    return JSONResponse(content={
        "status": "succeed",
        "data": user_data[1][0],
    })


@router.post("/send-reset-password-email", tags=["admin-user"])
def send_reset_password(req: Request, user: AdminBase):
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

    supabase.auth.reset_password_email(user.email, {
        "redirect_to": FRONTEND_URL + "/auth/resetpassword",
    })

    return JSONResponse(content={
        "status": "succeed",
        "email": user.email,
    })


@router.post("/{user_id}/create-team", tags=["admin-user"])
def create_team(req: Request, user_id: str):
    try:
        uuid.UUID(user_id)
    except ValueError:
        raise_custom_error(422, 210)
    admin_user: UUID4 = verify_user(req)
    if not admin_user:
        raise_custom_error(403, 213)
    admin_user_data, count = supabase.table("user_setting").select(
        "*").eq("is_deleted", False).eq("id", admin_user).execute()
    if admin_user_data[1][0]["is_admin"] == False:
        raise_custom_error(403, 200)
    # 임시 팀 생성
    team_data, count = supabase.table("team").insert(
        {"name": "연구실록 임시 팀", "team_leader_id": user_id}).execute()

    # 임시 팀 소속으로 변경
    team_id = team_data[1][0].get("id")
    user_data, count = supabase.table("user_setting").update(
        {"team_id": team_id}).eq("id", user_id).execute()
    if not user_data[1]:
        raise_custom_error(500, 220)

    return JSONResponse(content={
        "status": "succeed",
        "data": {"team": team_data[1][0], "user": user_data[1][0]}
    })
