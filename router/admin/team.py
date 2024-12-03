import os
from dotenv import load_dotenv
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status, Security, APIRouter, Request, Cookie
from fastapi.responses import JSONResponse
from typing import Annotated, List
from pydantic import BaseModel
import uuid
from nanoid import generate
from datetime import datetime
from dateutil.relativedelta import relativedelta

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
def get_team(req: Request, team_id: str):
    try:
        uuid.UUID(team_id)
    except ValueError:
        raise_custom_error(422, 210)
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


class Users(BaseModel):
    label: str
    value: str


class UsersAddInTeam(BaseModel):
    users: List[Users]


@router.post("/{team_id}", tags=["admin-team"])
def add_user_in_team(req: Request, team_id: str, user_add_in_team: UsersAddInTeam):
    try:
        uuid.UUID(team_id)
    except ValueError:
        raise_custom_error(422, 210)
    admin_user: UUID4 = verify_user(req)
    if not admin_user:
        raise_custom_error(403, 213)
    admin_user_data, count = supabase.table("user_setting").select(
        "*").eq("is_deleted", False).eq("id", admin_user).execute()
    if admin_user_data[1][0]["is_admin"] == False:
        raise_custom_error(403, 200)

    responses = []

    for user in user_add_in_team.users:
        try:
            uuid.UUID(user.value)
        except ValueError:
            raise_custom_error(422, 210)

        data, count = supabase.table("user_setting").update(
            {"team_id": team_id}).eq("id", user.value).execute()
        print(data)
        responses.append(data[1][0])

    return JSONResponse(content={
        "status": "succeed",
        "users": responses,
    })


@router.post("/{team_id}/add-1year", tags=["admin-team"])
def add_1year_in_team(req: Request, team_id: str):
    try:
        uuid.UUID(team_id)
    except ValueError:
        raise_custom_error(422, 210)
    admin_user: UUID4 = verify_user(req)
    if not admin_user:
        raise_custom_error(403, 213)
    admin_user_data, count = supabase.table("user_setting").select(
        "*").eq("is_deleted", False).eq("id", admin_user).execute()
    if admin_user_data[1][0]["is_admin"] == False:
        raise_custom_error(403, 200)

    # 기존 subscription이 있으면 fail
    subscription_data, count = supabase.table("subscription").select(
        "*").eq("team_id", team_id).eq("is_active", True).execute()
    if subscription_data[1]:
        raise_custom_error(500, 231)

    # order, subscription 추가
    subscription_range = relativedelta(years=1)
    started_at = datetime.now()
    expired_at = started_at + subscription_range - relativedelta(days=1)
    order_no = generate()
    subscription = SubscriptionCreate(team_id=team_id, started_at=started_at,
                                      expired_at=expired_at, max_members=10, is_active=True, order_no=order_no)

    order_data, count = supabase.table("order").insert(
        {"team_id": team_id, "order_no": order_no, "total_amount": 1000000, "purchase_user_id": admin_user, "status": "DONE", "notes": "어드민 기능 구독"}).execute()
    if not order_data[1]:
        raise_custom_error(500, 231)
    subscription_data, count = supabase.table("subscription").insert(
        subscription.model_dump(mode="json")).execute()
    if not subscription_data[1]:
        raise_custom_error(500, 231)

    return JSONResponse(content={
        "status": "succeed",
        "order": order_data[1][0],
        "subscription": subscription_data[1][0],
    })


@router.get("/{team_id}/note/list", tags=["admin-team"])
def get_team_note_list(req: Request, team_id: str):
    try:
        uuid.UUID(team_id)
    except ValueError:
        raise_custom_error(422, 210)
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
