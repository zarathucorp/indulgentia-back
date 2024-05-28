from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import UUID4
from func.auth.auth import verify_user
from func.user.team import get_user_team, get_team_user
from database import supabase, schemas
router = APIRouter(
    prefix="/team",
    responses={404: {"description": "Not found"}},
)


@router.get("/list")
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


@router.get("/")
def get_user_team_req(req: Request):
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user_team_id = get_user_team(user)

    return JSONResponse(content={
        "status": "succeed",
        "data": user_team_id
    })


@router.post("/")
def make_team(req: Request, team: schemas.TeamCreate):
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    data, count = supabase.table("team").insert(
        team.model_dump(mode="json")).execute()
    if not data[1]:
        raise HTTPException(status_code=400, detail="Failed to create team")
    res = data[1][0]
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })


@router.put("/{team_id}")
def update_team(req: Request, team_id: str, team: schemas.TeamUpdate):
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    data, count = supabase.table("team").update(
        team.model_dump(mode="json")).eq("id", team_id).execute()
    if not data[1]:
        raise HTTPException(status_code=400, detail="Failed to update team")
    res = data[1][0]
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })


@router.patch("/{team_id}/leader")
def change_team_leader(req: Request, team_id: str, next_leader_id: str):
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    data, count = supabase.table("team").update(
        {"team_leader_id": next_leader_id}).eq("id", team_id).execute()
    if not data[1]:
        raise HTTPException(
            status_code=400, detail="Failed to change team leader")
    res = data[1][0]
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })


@router.patch("/{team_id}/accept")
def accept_team_invite(req: Request, team_id: str, invite_id: str):
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    data1, count = supabase.table("team_invite").update(
        {"is_accepted": True}).eq("id", invite_id).execute()
    if not data1[1]:
        raise HTTPException(
            status_code=400, detail="Failed to accept team invite")
    data2, count = supabase.table("user_setting").update(
        {"team_id": team_id}).eq("id", user).execute()
    if not data2[1]:
        raise HTTPException(
            status_code=400, detail="Failed to update user setting")
    return JSONResponse(content={
        "status": "succeed",
        "data": [data1[1][0], data2[1][0]]
    })


@router.patch("/{team_id}/reject")
def reject_team_invite(req: Request, team_id: str, invite_id: str):
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    data, count = supabase.table("team_invite").update(
        {"is_accepted": False}).eq("id", invite_id).execute()
    if not data[1]:
        raise HTTPException(
            status_code=400, detail="Failed to reject team invite")
    res = data[1][0]
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })


@router.delete("/{team_id}/exit")
def exit_team(req: Request, team_id: str):
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    data, count = supabase.table("user_setting").update(
        {"team_id": None}).eq("id", user).execute()
    if not data[1]:
        raise HTTPException(status_code=400, detail="Failed to exit team")
    res = data[1][0]
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })


@router.delete("/{team_id}")
def drop_team(req: Request, team_id: str):
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    data, count = supabase.table("team").update(
        "is_deleted", True).eq("id", team_id).execute()
    if not data[1]:
        raise HTTPException(status_code=400, detail="Failed to delete team")
    res = data[1][0]
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })
