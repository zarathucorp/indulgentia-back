from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import UUID4
from func.auth.auth import verify_user
from func.user.team import get_user_team, get_team_user
from database import supabase
router = APIRouter(
    prefix="/team",
    responses={404: {"description": "Not found"}},
)


@router.get("/")
def get_team_user_list(req: Request):
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user_team_id = get_user_team(user)
    res = get_team_user(user_team_id)
    # need verify timestamp logic

    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })
