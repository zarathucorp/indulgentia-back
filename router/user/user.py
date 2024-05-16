from fastapi import APIRouter, Depends, HTTPException
from . import team, settings
router = APIRouter(
    prefix="/user",
    responses={404: {"description": "Not found"}},
)

router.include_router(team.router)
router.include_router(settings.router)
