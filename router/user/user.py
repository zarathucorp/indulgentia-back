from fastapi import APIRouter, Depends, HTTPException
from . import team
router = APIRouter(
    prefix="/user",
    responses={404: {"description": "Not found"}},
)

router.include_router(team.router)
