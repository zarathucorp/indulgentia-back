import base64
import os
import httpx
from pydantic import BaseModel
from fastapi import FastAPI, Request, HTTPException
from fastapi import APIRouter
from env import TOSS_PAYMENT_CLIENT_KEY, TOSS_PAYMENT_SECRET_KEY
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
async def confirm_payment(request: ConfirmPaymentRequest):
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

            payment = response.json()
            return payment

    except httpx.HTTPError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
