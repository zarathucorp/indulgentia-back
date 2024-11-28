import os
from dotenv import load_dotenv
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
    prefix="/team",
    responses={404: {"description": "Not found"}},
)


@router.get("/list", tags=["admin-team"])
def list_team(req: Request):
    admin_user: UUID4 = verify_user(req)
    if not admin_user:
        raise_custom_error(403, 213)
    admin_user_data, count = supabase.table("user_setting").select(
        "*").eq("is_deleted", False).eq("id", admin_user).execute()
    if admin_user_data[1][0]["is_admin"] == False:
        raise_custom_error(403, 200)
    team_data, count = supabase.table("team").select(
        "*").eq("is_deleted", False).order("created_at", desc=False).execute()

    return JSONResponse(content={
        "status": "succeed",
        "teams": team_data[1],
    })


@router.get("/{team_id}", tags=["admin-team"])
def get_team(req: Request, team_id: UUID4):
    admin_user: UUID4 = verify_user(req)
    if not admin_user:
        raise_custom_error(403, 213)
    admin_user_data, count = supabase.table("user_setting").select(
        "*").eq("is_deleted", False).eq("id", admin_user).execute()
    if admin_user_data[1][0]["is_admin"] == False:
        raise_custom_error(403, 200)
    team_user_data, count = supabase.table("user_setting").select(
        "*").eq("team_id", team_id).eq("is_deleted", False).execute()
    if not team_user_data:
        raise_custom_error(401, 110)

    return JSONResponse(content={
        "status": "succeed",
        "users": team_user_data[1],
    })


@router.get("/{team_id}/note/list", tags=["admin-team"])
def get_team_note_list(req: Request, team_id: UUID4):
    admin_user: UUID4 = verify_user(req)
    if not admin_user:
        raise_custom_error(403, 213)
    admin_user_data, count = supabase.table("user_setting").select(
        "*").eq("is_deleted", False).eq("id", admin_user).execute()
    if admin_user_data[1][0]["is_admin"] == False:
        raise_custom_error(403, 200)
    team_note_data, count = supabase.table("note").select(
        "*").eq("team_id", team_id).eq("is_deleted", False).execute()

    return JSONResponse(content={
        "status": "succeed",
        "notes": team_note_data[1],
    })
