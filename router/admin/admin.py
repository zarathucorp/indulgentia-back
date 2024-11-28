from fastapi import APIRouter
from . import note
from . import notification
from . import payment
from . import team
from . import user

router = APIRouter(
    prefix="/admin",
    responses={404: {"description": "Not found"}},
)

router.include_router(note.router)
router.include_router(notification.router)
router.include_router(payment.router)
router.include_router(team.router)
router.include_router(user.router)
