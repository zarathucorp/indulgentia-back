from fastapi import APIRouter, Depends, HTTPException, Request
from func.auth.auth import verify_user
import uuid
from database.supabase import supabase
from func.dashboard.crud.project import read_project_list
router = APIRouter(
    prefix="/project",
    responses={404: {"description": "Not found"}},
)


@router.get("/")
def project_list(req: Request):
    user: uuid.UUID = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    data, error = supabase.from_("user_setting").select(
        "team_id").eq("id", user).execute()

    team_id = data[1][0].get("team_id")
    if not team_id:
        raise HTTPException(status_code=400, detail="User not found")
    project_list = read_project_list(team_id)
    return {"status": "succeed", "project_list": project_list}
