from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(
    prefix="/note",
    responses={404: {"description": "Not found"}},
)
