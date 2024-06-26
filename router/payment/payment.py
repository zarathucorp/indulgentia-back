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


class Payment(BaseModel):
    orderName: str
    approvedAt: str
    receipt: dict
    totalAmount: int
    method: str
    paymentKey: str
    orderId: str


class ConfirmPaymentRequest(BaseModel):
    paymentKey: str
    orderId: str
    amount: int
    is_annual: bool = False
    max_members: int
    note: str | None = None



@router.post("/confirm-payment", tags=["payment"])
async def confirm_payment(req: Request, request: ConfirmPaymentRequest):
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    user_team_id = get_user_team(user)
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
                    "paymentKey": request.paymentKey,
                    "orderId": request.orderId,
                    "amount": request.amount,
                },
            )

            if response.status_code != 200:
                error_data = response.json()
                raise HTTPException(
                    status_code=500, detail="511")

            started_at = datetime.now()
            # started_at = request.get("premium_started_at", None)
            expired_at = started_at + relativedelta(months=1) - relativedelta(days=1)
            # expired_at = request.get("premium_expired_at", None)

            # raise Exception(started_at, expired_at)
            paid_team = TeamPay(id=user_team_id, is_premium=True, premium_started_at=started_at,
                                premium_expired_at=expired_at, max_members=request.max_members)
            team_data, count = supabase.table("team").update(paid_team.model_dump(mode="json")).eq("id", user_team_id).execute()
            if not team_data[1]:
                raise_custom_error(500, 511)
                # raise HTTPException(
                #     status_code=400, detail=f"{error_data['code']}: {error_data['message']}")

            payment = response.json()

            order = OrderCreate(team_id=user_team_id, order_no=request.orderId, status=payment["status"], payment_key=payment["paymentKey"], purchase_datetime=payment["approvedAt"], is_canceled=False, total_amount=payment["totalAmount"], purchase_user_id=user, payment_method=payment["method"], currency=payment["currency"], notes=request.note)
            order_data, count = supabase.table("order").insert(order.model_dump(mode="json")).execute()
            if not order_data[1]:
                raise_custom_error(500, 210)
            # order_data = (None, [{"id": "test"}])
            return JSONResponse(content={"status": "succeed", "data": {"team": team_data[1][0], "order": order_data[1][0], "payment": payment}})

    except httpx.HTTPError as exc:
        print(exc)
        raise_custom_error(500, 510)


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

