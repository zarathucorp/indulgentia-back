from fastapi import APIRouter, Depends, HTTPException, Request
from . import order
from . import toss
router = APIRouter(
    prefix="/payment",
    responses={404: {"description": "Not found"}},
)

router.include_router(order.router)
router.include_router(toss.router)
