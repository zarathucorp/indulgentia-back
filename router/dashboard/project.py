from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(
    prefix="/project",
    responses={404: {"description": "Not found"}},
)
