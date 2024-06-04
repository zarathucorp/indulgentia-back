import base64
import os
import httpx
from pydantic import BaseModel
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi import APIRouter
from env import TOSS_PAYMENT_CLIENT_KEY, TOSS_PAYMENT_SECRET_KEY
from database.schemas import *
from database.supabase import supabase
from func.auth.auth import verify_user
from func.user.team import get_user_team

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


@router.post("/confirm-payment/", tags=["payment"])
async def confirm_payment(req: Request, request: ConfirmPaymentRequest):
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
                    status_code=400, detail=f"{error_data['code']}: {error_data['message']}")
            user: UUID4 = verify_user(req)
            user_team_id = get_user_team(user)
            # started_at, expired_at dummy data, need to be updated
            from datetime import datetime
            from dateutil.relativedelta import relativedelta
            today = datetime.today()
            next_month = today + relativedelta(months=1)
            started_at = next_month.replace(day=1).strftime("%Y-%m-%d")
            month_after_next = today + relativedelta(months=2)
            expired_at = month_after_next.replace(day=1).strftime("%Y-%m-%d")

            payment = response.json()
            order = OrderCreate(team_id=user_team_id, order_number=request.orderId,
                                started_at=started_at, expired_at=expired_at, status=payment["status"], payment_key=request.paymentKey)  # Need testing
            order = order.model_dump(mode="json")
            data, count = supabase.table(
                "order").insert(order).execute()
            return payment

    except httpx.HTTPError as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/receipt/list", tags=["payment"])
async def get_invoice_list(req: Request):
    user: UUID4 = verify_user(req)
    user_team_id = get_user_team(user)
    data, count = supabase.table("order").select(
        "*").eq("team_id", user_team_id).order("created_at", desc=True).execute()
    if not data[1]:
        raise HTTPException(status_code=400, detail="receipt not found")
    return JSONResponse(content={
        "status": "succeed",
        "data": data[1]
    })


@router.get("/receipt/{order_id}", tags=["payment"])
async def get_invoice(req: Request, order_id: str):
    user: UUID4 = verify_user(req)
    user_team_id = get_user_team(user)
    data, count = supabase.table("order").select(
        "*").eq("team_id", user_team_id).eq("order_number", order_id).execute()
    if not data[1]:
        raise HTTPException(status_code=400, detail="Order not found")
    return JSONResponse(content={
        "status": "succeed",
        "data": data[1][0]
    })
