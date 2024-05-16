from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
import uuid
from pydantic import UUID4
from typing import List

from database import supabase, schemas
from func.auth.auth import *
from func.dashboard.crud.project import *


router = APIRouter(
    prefix="/project",
    responses={404: {"description": "Not found"}},
)


# read list


@router.get("/list/{team_id}", tags=["project"])
async def get_project_list(req: Request, team_id: str):
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not verify_team(user, team_id):
        raise HTTPException(status_code=401, detail="Unauthorized")
    res = read_project_list(team_id)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })


@router.get("/list", tags=["project"])
async def get_project_list_by_current_user(req: Request):
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    data, count = supabase.table("user_setting").select(
        "team_id").eq("id", user).execute()
    if not data[1]:
        raise HTTPException(status_code=500, detail="Supabase Error")
    res = read_project_list(data[1][0].get("team_id"))
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })

# read


@router.get("/{project_id}", tags=["project"])
async def get_project(req: Request, project_id: str):
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    data, count = supabase.rpc(
        "verify_project", {"user_id": str(user), "project_id": project_id}).execute()
    if not data[1]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    res = read_project(project_id)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })


# create


@router.post("/", tags=["project"])
async def add_project(req: Request, project: schemas.ProjectCreate):
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized - user")
    if not verify_team(user, project.team_id):
        raise HTTPException(status_code=401, detail="Unauthorized - team")
    res = create_project(project)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })

# update


@router.put("/{project_id}", tags=["project"])
async def change_project(req: Request, project: schemas.ProjectUpdate):
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    data, count = supabase.rpc("verify_project", {
                               "user_id": str(user), "project_id": str(project.id)}).execute()
    if not data[1]:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # # need verify project_leader?
    # if not user == project["project_leader"]:  # not working
    #     raise HTTPException(status_code=401, detail="Unauthorized")

    res = update_project(project)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })

# delete


@router.delete("/{project_id}", tags=["project"])
async def drop_project(req: Request, project_id: str):
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    data, count = supabase.rpc(
        "verify_project", {"user_id": str(user), "project_id": project_id}).execute()
    if not data[1]:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # # need verify project_leader?
    # if not user == project["project_leader"]:  # not working
    #     raise HTTPException(status_code=401, detail="Unauthorized")

    res = flag_is_deleted_project(project_id)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })

""" Old version
@router.delete("/{project_id}", tags=["project"])
async def drop_project(req: Request, project_id: str):
    user: UUID4 = verify_user(req)
    # if not user:
    #     raise HTTPException(status_code=401, detail="Unauthorized")
    if not verify_project(user, project_id):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # # need verify project_leader?
    # if not user == project["project_leader"]:  # not working
    #     raise HTTPException(status_code=401, detail="Unauthorized")

    res = delete_project(project_id)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })
"""

# alternative version
# read list


# @router.get("/")
# def project_list(req: Request):
#     user: uuid.UUID = verify_user(req)
#     if not user:
#         raise HTTPException(status_code=401, detail="Unauthorized")
#     data, count = supabase.from_("user_setting").select(
#         "team_id").eq("id", user).execute()
#     if len(user[1]) == 0:
#         raise HTTPException(status_code=500, detail="Supabase Error")
#     team_id = data[1][0].get("team_id")
#     if not team_id:
#         raise HTTPException(status_code=400, detail="User not found")
#     project_list = read_project_list(team_id)
#     return JSONResponse(content={
#         "status": "succeed",
#         "data": project_list["content"]
#     })
