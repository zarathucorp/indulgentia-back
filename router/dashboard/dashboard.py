from fastapi import APIRouter, Depends, HTTPException
from . import project
from . import bucket
from . import note
router = APIRouter(
    prefix="/dashboard",
    responses={404: {"description": "Not found"}},
)

router.include_router(project.router)
router.include_router(bucket.router)
router.include_router(note.router)
