import base64
import os
import httpx
from pydantic import BaseModel
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi import APIRouter
from env import TOSS_PAYMENT_CLIENT_KEY, TOSS_PAYMENT_SECRET_KEY
from datetime import datetime
from dateutil.relativedelta import relativedelta

from database.schemas import *
from database.supabase import supabase
from func.auth.auth import verify_user
from func.user.team import get_user_team
from func.error.error import raise_custom_error


router = APIRouter(
    prefix="/payment",
    responses={404: {"description": "Not found"}},
)


@router.get("/subscription", tags=["payment"])
def get_team_subscription(req: Request):
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    user_team_id = get_user_team(user)
    if not user_team_id:
        raise_custom_error(401, 540)
    data, count = supabase.table("subscription").select(
        "*").eq("team_id", user_team_id).execute()
    if not data[1]:
        raise_custom_error(500, 231)
    return JSONResponse(content={
        "status": "succeed",
        "data": data[1][0]
    })


class StartPaymentRequest(BaseModel):
    orderId: str
    amount: int
    is_annual: bool = True
    max_members: int
    note: str | None = None


@router.post("/start-payment", tags=["payment"])
async def start_payment(req: Request, request: StartPaymentRequest):
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    user_team_id = get_user_team(user)
    if not user_team_id:
        raise_custom_error(401, 540)
    if request.is_annual:
        subscription_range = relativedelta(years=1)
    else:
        subscription_range = relativedelta(months=1)

    datetime_now = datetime.now()
    current_subscription_data, count = supabase.table("subscription").select("*").eq("team_id", user_team_id).eq("is_active", True).lte("started_at", datetime_now).gte("expired_at", datetime_now).execute()
    if current_subscription_data[1]:
        started_at = current_subscription_data[1][0]["expired_at"]
        expired_at = started_at + subscription_range - relativedelta(days=1)
    else:
        started_at = datetime.now()
        expired_at = started_at + subscription_range - relativedelta(days=1)

    subscription = SubscriptionCreate(team_id=user_team_id, started_at=started_at, expired_at=expired_at, max_members=request.max_members, is_active=False, order_no=request.orderId)
    subscription_data, count = supabase.table("subscription").insert(subscription.model_dump(mode="json")).execute()
    if not subscription_data[1]:
        raise_custom_error(500, 511)
        # raise HTTPException(
        #     status_code=400, detail=f"{error_data['code']}: {error_data['message']}")

    user_team_id = get_user_team(user)
    order = OrderCreate(team_id=user_team_id, order_no=request.orderId, status="READY", payment_key=None, purchase_datetime=None, is_canceled=False, total_amount=request.amount, purchase_user_id=user, payment_method=None, currency=None, notes=request.note)
    data, count = supabase.table("order").insert(order.model_dump(mode="json")).execute()
    if not data[1]:
        raise_custom_error(500, 210)
    return JSONResponse(content={
        "status": "succeed",
        "data": data[1][0]
    })


class Payment(BaseModel):
    orderName: str
    approvedAt: str
    receipt: dict
    totalAmount: int
    method: str
    paymentKey: str
    orderId: str


class ConfirmPayment(BaseModel):
    paymentKey: str
    orderId: str
    amount: int




@router.post("/confirm-payment", tags=["payment"])
async def confirm_payment(req: Request, payment: ConfirmPayment):
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    user_team_id = get_user_team(user)
    if not user_team_id:
        raise_custom_error(401, 540)
    # if TOSS_PAYMENT_SECRET_KEY is None:
    #     return {"error": "TOSS_PAYMENT_SECRET_KEY is not set"}
    TOSS_PAYMENT_SECRET_KEY = "test_gsk_docs_OaPz8L5KdmQXkzRz3y47BMw6"
    auth_header = f"Basic {base64.b64encode((TOSS_PAYMENT_SECRET_KEY + ':').encode()).decode()}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.tosspayments.com/v1/payments/confirm",
                headers={
                    "Authorization": auth_header,
                    "Content-Type": "application/json",
                },
                json={
                    "paymentKey": payment.paymentKey,
                    "orderId": payment.orderId,
                    "amount": payment.amount,
                },
            )

            if response.status_code != 200:
                error_data = response.json()
                print(error_data)
                fail_order_data, count = supabase.table("order").update({"status": "ABORTED", "is_canceled": True}).eq("order_no", payment["orderId"]).execute()
                print(fail_order_data)
                raise_custom_error(500, 511)

            payment = response.json()


    except httpx.HTTPError as exc:
        print(exc)
        fail_order_data, count = supabase.table("order").update({"status": "ABORTED", "is_canceled": True}).eq("order_no", payment["orderId"]).execute()
        print(fail_order_data)
        raise_custom_error(500, 510)
    except Exception as e:
        print(e)
        fail_order_data, count = supabase.table("order").update({"status": "ABORTED", "is_canceled": True}).eq("order_no", payment["orderId"]).execute()
        print(fail_order_data)
        raise_custom_error(500,500)

    order = OrderUpdate(status=payment["status"], payment_key=payment["paymentKey"], purchase_datetime=payment["approvedAt"], total_amount=payment["totalAmount"], purchase_user_id=user, payment_method=payment["method"], currency=payment["currency"])
    order_data, count = supabase.table("order").update(order.model_dump(mode="json")).eq("order_no", payment["orderId"]).execute()
    if not order_data[1]:
        raise_custom_error(500, 220)
    subscription_data, count = supabase.table("subscription").update({"is_active": True}).eq("order_no", payment["orderId"]).execute()
    if not subscription_data[1]:
        raise_custom_error(500, 231)
    # order_data = (None, [{"id": "test"}])
    return JSONResponse(content={"status": "succeed", "data": {"order": order_data[1][0], "subscription": subscription_data[1][0],"payment": payment}})




@router.get("/receipt/list", tags=["payment"])
async def get_invoice_list(req: Request):
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    user_team_id = get_user_team(user)
    data, count = supabase.table("order").select(
        "*").eq("team_id", user_team_id).order("created_at", desc=True).execute()
    return JSONResponse(content={
        "status": "succeed",
        "data": data[1]
    })


@router.get("/receipt/{order_no}", tags=["payment"])
async def get_invoice(req: Request, order_no: str):
    user: UUID4 = verify_user(req)
    user_team_id = get_user_team(user)
    data, count = supabase.table("order").select(
        "*").eq("team_id", user_team_id).eq("order_no", order_no).execute()
    if not data[1]:
        raise_custom_error(500, 231)
    return JSONResponse(content={
        "status": "succeed",
        "data": data[1][0]
    })


# Toss Webhook API
@router.post("/webhook/toss", tags=["payment"])
def webhook_order(req: Request, order: OrderWebhook):
    user: UUID4 = verify_user(req)
    # verify Toss user needed

    data, count = supabase.table("order").update(order.model_dump(mode="json")
        ).eq("order_no", order.get("order_no")).execute()
    if not data[1]:
        raise_custom_error(500, 220)
    return JSONResponse(content={
        "status": "succeed",
        "data": data[1][0]
    })

