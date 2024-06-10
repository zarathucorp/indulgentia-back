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
from func.error.error import raise_custom_error


router = APIRouter(
    prefix="/team",
    responses={404: {"description": "Not found"}},
)


@router.get("/list", tags=["team"])
def get_team_user_list(req: Request):
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    user_team_id = get_user_team(user)
    if not user_team_id:
        raise_custom_error(401, 540)
    try:
        UUID(user_team_id)
    except ValueError:
        raise_custom_error(422, 210)
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
        raise_custom_error(403, 213)
    user_team_id = get_user_team(user)
    if not user_team_id:
        raise_custom_error(422, 210)
    try:
        UUID(user_team_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid team id")
    data, count = supabase.table("team").select(
        "*").eq("is_deleted", False).eq("id", user_team_id).execute()
    if not data[1]:
        raise_custom_error(500, 242)
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
        raise_custom_error(403, 213)
    if not validate_user_free(user):
        raise_custom_error(401, 530)
    team_data, count = supabase.table("team").insert(
        {**team.model_dump(mode="json"), "team_leader_id": user}).execute()
    if not team_data[1]:
        raise_custom_error(500, 210)
    team_id = team_data[1][0].get("id")
    user_data, count = supabase.table("user_setting").update(
        {"team_id": team_id}).eq("id", user).execute()
    if not user_data[1]:
        raise_custom_error(500, 220)
    return JSONResponse(content={
        "status": "succeed",
        "data": {"team": team_data[1][0], "user": user_data[1][0]}
    })


@router.put("/{team_id}", tags=["team"])
def update_team(req: Request, team_id: str, team: schemas.TeamUpdate):
    try:
        UUID(team_id)
    except ValueError:
        raise_custom_error(422, 210)
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    if not validate_user_is_leader(user, UUID(team_id)):
        raise_custom_error(401, 520)
    data, count = supabase.table("team").update(
        team.model_dump(mode="json")).eq("is_deleted", False).eq("id", team_id).execute()
    if not data[1]:
        raise_custom_error(500, 220)
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
        UUID(team_id)
    except ValueError:
        raise_custom_error(422, 210)
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    if not validate_user_is_leader(user, UUID(team_id)):
        raise_custom_error(401, 520)
    data, count = supabase.table("team").update(
        {"team_leader_id": team.next_leader_id}).eq("is_deleted", False).eq("is_deleted", False).eq("id", team_id).execute()
    if not data[1]:
        raise_custom_error(500, 220)
    res = data[1][0]
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })


class TeamInviteRequest(BaseModel):
    invite_id: UUID4


@router.patch("/{team_id}/accept", tags=["team"])
def accept_team_invite(req: Request, team_id: str, invite: TeamInviteRequest):
    try:
        UUID(team_id)
        UUID(invite.invite_id)
    except ValueError:
        raise_custom_error(422, 210)
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    if not validate_user_free(user):
        raise_custom_error(401, 530)

    is_invite_accepted = validate_invite_accepted(UUID(invite.invite_id))
    if is_invite_accepted == False:
        invite_data, count = supabase.table("team_invite").update({"is_deleted": True}).eq(
            "id", invite.invite_id).execute()
        raise_custom_error(401, 620)
    elif is_invite_accepted == True:
        invite_data, count = supabase.table("team_invite").update({"is_deleted": True}).eq(
            "id", invite.invite_id).execute()
        raise_custom_error(401, 610)
    else:  # is_invite_accepted == None
        team_invite_data, count = supabase.table("team_invite").update(
            {"is_accepted": True, "is_deleted": True}).eq("id", invite.invite_id).execute()
        if not team_invite_data[1]:
            raise_custom_error(500, 220)
        # change to trigger in supabase
        user_data, count = supabase.table("user_setting").update(
            {"team_id": team_id}).eq("id", user).execute()
        if not user_data[1]:
            raise_custom_error(500, 220)
        return JSONResponse(content={
            "status": "succeed",
            "data": {"team_invite": team_invite_data[1][0], "user": user_data[1][0]}
        })


@router.patch("/{team_id}/reject", tags=["team"])
def reject_team_invite(req: Request, team_id: str, invite: TeamInviteRequest):
    try:
        UUID(team_id)
        UUID(invite.invite_id)
    except ValueError:
        raise_custom_error(422, 210)
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    # if not validate_user_free(user):
    #     raise_custom_error(401, 530)

    is_invite_accepted = validate_invite_accepted(UUID(invite.invite_id))
    if is_invite_accepted == False:
        invite_data, count = supabase.table("team_invite").update({"is_deleted": True}).eq(
            "id", invite.invite_id).execute()
        raise_custom_error(401, 620)
    elif is_invite_accepted == True:
        invite_data, count = supabase.table("team_invite").update({"is_deleted": True}).eq(
            "id", invite.invite_id).execute()
        raise_custom_error(401, 610)
    else:  # is_invite_accepted == None
        data, count = supabase.table("team_invite").update(
            {"is_accepted": False, "is_deleted": True}).eq("id", invite.invite_id).execute()
        if not data[1]:
            raise_custom_error(500, 220)
        res = data[1][0]
        return JSONResponse(content={
            "status": "succeed",
            "data": res
        })


@router.delete("/{team_id}/exit", tags=["team"])
def exit_team(req: Request, team_id: str):
    try:
        UUID(team_id)
    except ValueError:
        raise_custom_error(422, 210)
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    if not validate_user_in_team(user, UUID(team_id)):
        raise_custom_error(401, 510)
    if validate_user_is_leader(user, UUID(team_id)) and len(get_team_user(UUID(team_id))) > 1:
        raise_custom_error(401, 550)
    data, count = supabase.table("user_setting").update(
        {"team_id": None}).eq("id", user).execute()
    if not data[1]:
        raise_custom_error(500, 242)
    res = data[1][0]
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })


@router.delete("/{team_id}", tags=["team"])
def drop_team(req: Request, team_id: str):
    try:
        UUID(team_id)
    except ValueError:
        raise_custom_error(422, 210)
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    if not validate_user_is_leader(user, UUID(team_id)):
        raise_custom_error(401, 520)
    if len(get_team_user(UUID(team_id))) > 1:
        raise_custom_error(401, 550)
    team_data, count = supabase.table("team").update(
        {"is_deleted": True}).eq("id", team_id).execute()
    if not team_data[1]:
        raise_custom_error(500, 242)
    user_data, count = supabase.table("user_setting").update(
        {"team_id": None}).eq("team_id", team_id).execute()
    if not user_data[1]:
        raise_custom_error(500, 242)
    return JSONResponse(content={
        "status": "succeed",
        "data": {"team": team_data[1][0], "user": user_data[1][0]}
    })


class TeamInviteEmailRequest(BaseModel):
    user_email: str


@router.post("/invite", tags=["team"])
def send_team_invite_by_email(req: Request, invite: TeamInviteEmailRequest):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", invite.user_email):
        raise_custom_error(422, 220)
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    team_id = get_user_team(user)
    if not validate_user_is_leader(user, UUID(team_id)):
        raise_custom_error(401, 520)
    invited_user_id = get_user_id_by_email(invite.user_email)
    if not validate_user_free(UUID(invited_user_id)):
        raise_custom_error(401, 530)
    check_team_invite_data, count = supabase.table("team_invite").select(
        "*").eq("is_deleted", False).eq("invited_user_id", invited_user_id).eq("team_id", team_id).execute()
    if check_team_invite_data[1]:
        raise_custom_error(401, 630)
    result_team_invite_data, count = supabase.table("team_invite").insert(
        {"invited_user_id": invited_user_id, "is_accepted": None, "team_id": team_id}).execute()
    if not result_team_invite_data[1]:
        raise_custom_error(500, 210)
    res = result_team_invite_data[1][0]
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })


@router.get("/invite/receive/list", tags=["team"])
def get_team_invite_received_list(req: Request):
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    data, count = supabase.rpc("get_team_invite_and_team_and_user_setting", {
                               "user_id": str(user)}).execute()
    return JSONResponse(content={
        "status": "succeed",
        "data": data[1]
    })


@router.get("/invite/send/list", tags=["team"])
def get_team_invite_sent_list(req: Request):
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    team_id = get_user_team(user)
    if not validate_user_is_leader(user, UUID(team_id)):
        raise_custom_error(401, 520)
    data, count = supabase.rpc("get_team_invite_send_and_team_and_user_setting", {
                               "sent_team_id": team_id}).execute()
    return JSONResponse(content={
        "status": "succeed",
        "data": data[1]
    })


@router.get("/invite/{invite_id}", tags=["team"])
def get_team_invite_single(req: Request, invite_id: str):
    try:
        UUID(invite_id)
    except ValueError:
        raise_custom_error(422, 210)
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    data, count = supabase.table("team_invite").select(
        "*").eq("id", invite_id).execute()
    if not data[1]:
        raise_custom_error(500, 231)
    return JSONResponse(content={
        "status": "succeed",
        "data": data[1][0]
    })


@router.delete("/invite/cancel", tags=["team"])
def cancel_team_invite(req: Request, team_invite: TeamInviteRequest):
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    team_id = get_user_team(user)
    if not validate_user_is_leader(user, UUID(team_id)):
        raise_custom_error(401, 520)
    data, count = supabase.table("team_invite").update(
        {"is_deleted": True}).eq("id", team_invite.invite_id).execute()
    if not data[1]:
        raise_custom_error(500, 242)
    res = data[1][0]
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })
