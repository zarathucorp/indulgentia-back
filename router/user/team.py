from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import UUID4
from uuid import UUID
import re
from pydantic import BaseModel

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
    if not user_team_id:
        raise HTTPException(status_code=400, detail="User not in team")
    try:
        UUID(user_team_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid team id")
    res = get_team_user(user_team_id)
    # need verify timestamp logic

    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })


@router.get("", include_in_schema=False)
@router.get("/", tags=["team"])
def get_user_team_req(req: Request):
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user_team_id = get_user_team(user)
    if not user_team_id:
        raise HTTPException(status_code=400, detail="User not in team")
    try:
        UUID(user_team_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid team id")
    data, count = supabase.table("team").select(
        "*").eq("is_deleted", False).eq("id", user_team_id).execute()
    if not data[1]:
        raise HTTPException(status_code=400, detail="Failed to get team")
    res = data[1][0]
    print(res)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })


@router.post("", include_in_schema=False)
@router.post("/", tags=["team"])
def make_team(req: Request, team: schemas.TeamCreate):
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not validate_user_free(user):
        raise HTTPException(status_code=403, detail="Already in team")
    team_data, count = supabase.table("team").insert(
        {**team.model_dump(mode="json"), "team_leader_id": user}).execute()
    if not team_data[1]:
        raise HTTPException(status_code=400, detail="Failed to create team")
    team_id = team_data[1][0].get("id")
    user_data, count = supabase.table("user_setting").update(
        {"team_id": team_id}).eq("id", user).execute()
    if not user_data[1]:
        raise HTTPException(
            status_code=400, detail="Failed to update user setting")
    return JSONResponse(content={
        "status": "succeed",
        "data": {"team": team_data[1][0], "user": user_data[1][0]}
    })


@router.put("/{team_id}", tags=["team"])
def update_team(req: Request, team_id: str, team: schemas.TeamUpdate):
    try:
        test_id = UUID(team_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid UUID format")
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not validate_user_is_leader(user, UUID(team_id)):
        raise HTTPException(status_code=403, detail="Not a team leader")
    data, count = supabase.table("team").update(
        team.model_dump(mode="json")).eq("is_deleted", False).eq("id", team_id).execute()
    if not data[1]:
        raise HTTPException(status_code=400, detail="Failed to update team")
    res = data[1][0]
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })


class ChangeTeamLeaderRequest(BaseModel):
    next_leader_id: str


@router.patch("/{team_id}/leader", tags=["team"])
def change_team_leader(req: Request, team_id: str, team: ChangeTeamLeaderRequest):
    try:
        test_id = UUID(team_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid UUID format")
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not validate_user_is_leader(user, UUID(team_id)):
        raise HTTPException(status_code=403, detail="Not a team leader")
    data, count = supabase.table("team").update(
        {"team_leader_id": team.next_leader_id}).eq("is_deleted", False).eq("is_deleted", False).eq("id", team_id).execute()
    if not data[1]:
        raise HTTPException(
            status_code=400, detail="Failed to change team leader")
    res = data[1][0]
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })


class TeamInviteRequest(BaseModel):
    invite_id: str


@router.patch("/{team_id}/accept", tags=["team"])
def accept_team_invite(req: Request, team_id: str, invite: TeamInviteRequest):
    try:
        test_id = UUID(team_id)
        test_id = UUID(invite.invite_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid UUID format")
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not validate_user_free(user):
        raise HTTPException(status_code=403, detail="Already in team")

    is_invite_accepted = validate_invite_accepted(UUID(invite.invite_id))
    if is_invite_accepted == False:
        raise HTTPException(status_code=400, detail="Invite already rejected")
    elif is_invite_accepted == True:
        raise HTTPException(status_code=400, detail="Invite already accepted")
    else:  # is_invite_accepted == None
        team_invite_data, count = supabase.table("team_invite").update(
            {"is_accepted": True}).eq("id", invite.invite_id).execute()
        if not team_invite_data[1]:
            raise HTTPException(
                status_code=400, detail="Failed to accept team invite")
        # change to trigger in supabase
        user_data, count = supabase.table("user_setting").update(
            {"team_id": team_id}).eq("id", user).execute()
        if not user_data[1]:
            raise HTTPException(
                status_code=400, detail="Failed to update user setting")
        return JSONResponse(content={
            "status": "succeed",
            "data": {"team_invite": team_invite_data[1][0], "user": user_data[1][0]}
        })


@router.patch("/{team_id}/reject", tags=["team"])
def reject_team_invite(req: Request, team_id: str, invite: TeamInviteRequest):
    try:
        test_id = UUID(team_id)
        test_id = UUID(invite.invite_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid UUID format")
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    # if not validate_user_free(user):
    #     raise HTTPException(status_code=403, detail="Already in team")

    is_invite_accepted = validate_invite_accepted(UUID(invite.invite_id))
    if is_invite_accepted == False:
        raise HTTPException(status_code=400, detail="Invite already rejected")
    elif is_invite_accepted == True:
        raise HTTPException(status_code=400, detail="Invite already accepted")
    else:  # is_invite_accepted == None
        data, count = supabase.table("team_invite").update(
            {"is_accepted": False}).eq("id", invite.invite_id).execute()
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
        test_id = UUID(team_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid UUID format")
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not validate_user_in_team(user, UUID(team_id)):
        raise HTTPException(status_code=403, detail="Not in this team")
    if validate_user_is_leader(user, UUID(team_id)) and len(get_team_user(UUID(team_id))) > 1:
        raise HTTPException(
            status_code=403, detail="Team leader can't exit team with members")
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
        test_id = UUID(team_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid UUID format")
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not validate_user_is_leader(user, UUID(team_id)):
        raise HTTPException(status_code=403, detail="Not a team leader")
    if len(get_team_user(UUID(team_id))) > 1:
        raise HTTPException(
            status_code=403, detail="Team leader can't drop team with members")
    team_data, count = supabase.table("team").update(
        {"is_deleted": True}).eq("id", team_id).execute()
    if not team_data[1]:
        raise HTTPException(status_code=400, detail="Failed to delete team")
    user_data, count = supabase.table("user_setting").update(
        {"team_id": None}).eq("team_id", team_id).execute()
    if not user_data[1]:
        raise HTTPException(
            status_code=400, detail="Failed to update user setting")
    return JSONResponse(content={
        "status": "succeed",
        "data": {"team": team_data[1][0], "user": user_data[1][0]}
    })


class TeamInviteEmailRequest(BaseModel):
    user_email: str


@router.post("/invite", tags=["team"])
def send_team_invite_by_email(req: Request, invite: TeamInviteEmailRequest):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", invite.user_email):
        raise HTTPException(status_code=422, detail="Invalid email format")
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    team_id = get_user_team(user)
    if not validate_user_is_leader(user, UUID(team_id)):
        raise HTTPException(status_code=403, detail="Not a team leader")
    invited_user_id = get_user_id_by_email(invite.user_email)
    if not validate_user_free(UUID(invited_user_id)):
        raise HTTPException(status_code=403, detail="Already in team")
    check_team_invite_data, count = supabase.table("team_invite").select(
        "*").neq("is_accepted", False).eq("invited_user_id", invited_user_id).eq("team_id", team_id).execute()
    print(check_team_invite_data[1])
    if check_team_invite_data[1]:
        raise HTTPException(status_code=400, detail="Invite already sent")
    result_team_invite_data, count = supabase.table("team_invite").insert(
        {"invited_user_id": invited_user_id, "is_accepted": None, "team_id": team_id}).execute()
    if not result_team_invite_data[1]:
        raise HTTPException(
            status_code=400, detail="Failed to send team invite")
    res = result_team_invite_data[1][0]
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })


@router.get("/invite/receive/list", tags=["team"])
def get_team_invite_received_list(req: Request):
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    data, count = supabase.rpc("get_team_invite_and_team_and_user_setting", {
                               "user_id": str(user)}).execute()
    print(data)
    return JSONResponse(content={
        "status": "succeed",
        "data": data[1]
    })


@router.get("/invite/send/list", tags=["team"])
def get_team_invite_sent_list(req: Request):
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    team_id = get_user_team(user)
    if not validate_user_is_leader(user, UUID(team_id)):
        raise HTTPException(status_code=403, detail="Not a team leader")
    data, count = supabase.table("team_invite").select(
        "*").is_("is_accepted", "null").eq("team_id", team_id).order("created_at").execute()
    return JSONResponse(content={
        "status": "succeed",
        "data": data[1]
    })


@router.get("/invite/{invite_id}", tags=["team"])
def get_team_invite_single(req: Request, invite_id: str):
    try:
        test_id = UUID(invite_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid UUID format")
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    data, count = supabase.table("team_invite").select(
        "*").eq("id", invite_id).execute()
    if not data[1]:
        raise HTTPException(
            status_code=400, detail="Failed to get team invite")
    return JSONResponse(content={
        "status": "succeed",
        "data": data[1][0]
    })
