from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi import APIRouter
from datetime import datetime
import uuid

from database.schemas import *
from database.supabase import supabase
from func.auth.auth import verify_user
from func.user.team import get_user_team
from func.error.error import raise_custom_error


router = APIRouter(
    prefix="/order",
    responses={404: {"description": "Not found"}},
)


@router.get("/subscription", tags=["order"])
def get_team_subscription(req: Request):
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    user_team_id = get_user_team(user)
    if not user_team_id:
        raise_custom_error(401, 540)

    datetime_now = datetime.now()
    data, count = supabase.table("subscription").select("*").eq("team_id", user_team_id).eq(
        "is_active", True).lte("started_at", datetime_now).gte("expired_at", datetime_now).execute()
    if not data[1]:
        res = None
    else:
        res = data[1][0]
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })


@router.get("/list", tags=["order"])
async def get_order_list(req: Request):
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    data, count = supabase.table("order").select(
        "*").eq("purchase_user_id", user).order("created_at", desc=True).execute()
    return JSONResponse(content={
        "status": "succeed",
        "data": data[1]
    })


@router.get("/{order_no}", tags=["order"])
async def get_order(req: Request, order_no: str):
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    data, count = supabase.table("order").select(
        "*").eq("order_no", order_no).execute()
    if not data[1]:
        raise_custom_error(500, 231)
    if data[1][0].get('purchase_user_id', None) != str(user):
        raise_custom_error(401, 710)
    return JSONResponse(content={
        "status": "succeed",
        "data": data[1][0]
    })
