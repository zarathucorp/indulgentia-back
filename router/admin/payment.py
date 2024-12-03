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


router = APIRouter(
    prefix="/payment",
    responses={404: {"description": "Not found"}},
)


@router.get("/subscription/list", tags=["admin-payment"])
def list_subscription(req: Request):
    admin_user: UUID4 = verify_user(req)
    if not admin_user:
        raise_custom_error(403, 213)
    admin_user_data, count = supabase.table("user_setting").select(
        "*").eq("is_deleted", False).eq("id", admin_user).execute()
    if admin_user_data[1][0]["is_admin"] == False:
        raise_custom_error(403, 200)
    subscription_data, count = supabase.table("subscription").select(
        "*").execute()
    if not subscription_data:
        raise_custom_error(500, 232)

    return JSONResponse(content={
        "status": "succeed",
        "subscriptions": subscription_data[1],
    })


@router.put("/subscription/{subscription_id}", tags=["admin-payment"])
def update_subscription(req: Request, subscription_id: str, subscription: SubscriptionUpdate):
    try:
        uuid.UUID(subscription_id)
    except ValueError:
        raise_custom_error(422, 210)
    admin_user: UUID4 = verify_user(req)
    if not admin_user:
        raise_custom_error(403, 213)
    admin_user_data, count = supabase.table("user_setting").select(
        "*").eq("is_deleted", False).eq("id", admin_user).execute()
    if admin_user_data[1][0]["is_admin"] == False:
        raise_custom_error(403, 200)

    subscription_data, count = supabase.table("subscription").update(
        subscription.model_dump(mode="json")).eq("id", subscription_id).execute()
    if not subscription_data[1]:
        raise_custom_error(500, 220)

    return JSONResponse(content={
        "status": "succeed",
        "subscriptions": subscription_data[1],
    })


@router.get("/order/list", tags=["admin-payment"])
def list_order(req: Request):
    admin_user: UUID4 = verify_user(req)
    if not admin_user:
        raise_custom_error(403, 213)
    admin_user_data, count = supabase.table("user_setting").select(
        "*").eq("is_deleted", False).eq("id", admin_user).execute()
    if admin_user_data[1][0]["is_admin"] == False:
        raise_custom_error(403, 200)
    order_data, count = supabase.table("order").select(
        "*").execute()
    if not order_data[1]:
        raise_custom_error(500, 232)

    return JSONResponse(content={
        "status": "succeed",
        "orders": order_data[1],
    })


@router.get("/order/{order_id}", tags=["admin-payment"])
async def get_order(req: Request, order_id: str):
    try:
        uuid.UUID(order_id)
    except ValueError:
        raise_custom_error(422, 210)
    admin_user: UUID4 = verify_user(req)
    if not admin_user:
        raise_custom_error(403, 213)
    admin_user_data, count = supabase.table("user_setting").select(
        "*").eq("is_deleted", False).eq("id", admin_user).execute()
    if admin_user_data[1][0]["is_admin"] == False:
        raise_custom_error(403, 200)
    order_data, count = supabase.table("order").select(
        "*").eq("id", order_id).execute()
    if not order_data[1]:
        raise_custom_error(500, 231)
    return JSONResponse(content={
        "status": "succeed",
        "data": order_data[1][0]
    })


@router.put("/order/{order_id}", tags=["admin-payment"])
def update_order(req: Request, order_id: str, order: OrderUpdate):
    try:
        uuid.UUID(order_id)
    except ValueError:
        raise_custom_error(422, 210)
    admin_user: UUID4 = verify_user(req)
    if not admin_user:
        raise_custom_error(403, 213)
    admin_user_data, count = supabase.table("user_setting").select(
        "*").eq("is_deleted", False).eq("id", admin_user).execute()
    if admin_user_data[1][0]["is_admin"] == False:
        raise_custom_error(403, 200)

    order_data, count = supabase.table("order").update(
        order.model_dump(mode="json")).eq("id", order_id).execute()
    if not order_data[1]:
        raise_custom_error(500, 220)

    return JSONResponse(content={
        "status": "succeed",
        "orders": order_data[1],
    })
