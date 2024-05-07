from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(
    prefix="/bucket",
    responses={404: {"description": "Not found"}},
)
