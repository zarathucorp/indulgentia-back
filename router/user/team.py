from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import UUID4
from func.auth.auth import verify_user
from func.user.team import *
from database import schemas
from database.supabase import supabase
router = APIRouter(
    prefix="/team",
    responses={404: {"description": "Not found"}},
)


@router.get("/list", tags=["team"])
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


@router.get("/", tags=["team"])
def get_user_team_req(req: Request):
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user_team_id = get_user_team(user)

    return JSONResponse(content={
        "status": "succeed",
        "data": user_team_id
    })


@router.post("/", tags=["team"])
def make_team(req: Request, team: schemas.TeamCreate):
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not validate_user_free(user):
        raise HTTPException(status_code=403, detail="Already in team")
    data2, count = supabase.table("team").insert(
        team.model_dump(mode="json")).execute()
    if not data2[1]:
        raise HTTPException(status_code=400, detail="Failed to create team")
    team_id = data2[1][0].get("id")
    data3, count = supabase.table("user_setting").update(
        {"team_id": team_id}).eq("id", user).execute()
    if not data3[1]:
        raise HTTPException(
            status_code=400, detail="Failed to update user setting")
    res = data2[1][0]
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })


@router.put("/{team_id}", tags=["team"])
def update_team(req: Request, team_id: str, team: schemas.TeamUpdate):
    try:
        test_id = UUID4(team_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid UUID format")
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if validate_user_in_team(user, UUID4(team_id)):
        raise HTTPException(status_code=403, detail="Already in team")
    data, count = supabase.table("team").select(
        team.model_dump(mode="json")).eq("id", team_id).execute()
    if not data[1]:
        raise HTTPException(status_code=400, detail="Failed to update team")
    res = data[1][0]
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })


@router.patch("/{team_id}/leader", tags=["team"])
def change_team_leader(req: Request, team_id: str, next_leader_id: str):
    try:
        test_id = UUID4(team_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid UUID format")
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not validate_user_is_leader(user, UUID4(team_id)):
        raise HTTPException(status_code=403, detail="Not a team leader")
    data2, count = supabase.table("team").update(
        {"team_leader_id": next_leader_id}).eq("id", team_id).execute()
    if not data2[1]:
        raise HTTPException(
            status_code=400, detail="Failed to change team leader")
    res = data2[1][0]
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })


@router.patch("/{team_id}/accept", tags=["team"])
def accept_team_invite(req: Request, team_id: str, invite_id: str):
    try:
        test_id = UUID4(team_id)
        test_id = UUID4(invite_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid UUID format")
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not validate_user_free(user):
        raise HTTPException(status_code=403, detail="Already in team")

    is_invite_accepted = validate_invite_accepted(UUID4(invite_id))
    if is_invite_accepted == False:
        raise HTTPException(status_code=400, detail="Invite already rejected")
    elif is_invite_accepted == True:
        raise HTTPException(status_code=400, detail="Invite already accepted")
    else:  # is_invite_accepted == None
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


@router.patch("/{team_id}/reject", tags=["team"])
def reject_team_invite(req: Request, team_id: str, invite_id: str):
    try:
        test_id = UUID4(team_id)
        test_id = UUID4(invite_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid UUID format")
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not validate_user_free(user):
        raise HTTPException(status_code=403, detail="Already in team")

    is_invite_accepted = validate_invite_accepted(UUID4(invite_id))
    if is_invite_accepted == False:
        raise HTTPException(status_code=400, detail="Invite already rejected")
    elif is_invite_accepted == True:
        raise HTTPException(status_code=400, detail="Invite already accepted")
    else:  # is_invite_accepted == None
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


@router.delete("/{team_id}/exit", tags=["team"])
def exit_team(req: Request, team_id: str):
    try:
        test_id = UUID4(team_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid UUID format")
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not validate_user_in_team(user, UUID4(team_id)):
        raise HTTPException(status_code=403, detail="Not in team")
    data, count = supabase.table("user_setting").update(
        {"team_id": None}).eq("id", user).execute()
    if not data[1]:
        raise HTTPException(status_code=400, detail="Failed to exit team")
    res = data[1][0]
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })


@router.delete("/{team_id}", tags=["team"])
def drop_team(req: Request, team_id: str):
    try:
        test_id = UUID4(team_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid UUID format")
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not validate_user_is_leader(user, UUID4(team_id)):
        raise HTTPException(status_code=403, detail="Not a team leader")
    data1, count = supabase.table("team").update(
        "is_deleted", True).eq("id", team_id).execute()
    if not data1[1]:
        raise HTTPException(status_code=400, detail="Failed to delete team")
    data2, count = supabase.table("user_setting").update(
        {"team_id": None}).eq("team_id", team_id).execute()
    if not data2[1]:
        raise HTTPException(
            status_code=400, detail="Failed to update user setting")
    return JSONResponse(content={
        "status": "succeed",
        "data": [data1[1][0], data2[1][0]]
    })
