from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
import uuid
from pydantic import UUID4
from typing import List

from database import supabase, schemas
from func.auth.auth import verify_user
from func.dashboard.crud.project import *


router = APIRouter(
    prefix="/project",
    responses={404: {"description": "Not found"}},
)


# read


@router.get("/{project_id}", tags=["project"])
async def get_project(req: Request, project_id: str):
    res = read_project(project_id)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })

# read list


@router.get("/list/{team_id}", tags=["project"])
async def get_project_list(req: Request, team_id: str):
    res = read_project_list(team_id)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })

# create


@router.post("/", tags=["project"])
async def add_project(req: Request, project: schemas.ProjectCreate):
    # user verification?
    

    res = create_project(project)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })

# update


@router.put("/{project_id}", tags=["project"])
async def change_project(req: Request, project: schemas.ProjectUpdate):
    res = update_project(project)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })

# delete


@router.delete("/{project_id}", tags=["project"])
async def drop_project(req: Request, project_id: str):
    # project_id = uuid.UUID(project_id, version=4)
    res = delete_project(project_id)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })

# alternative version
# read list


@router.get("/", tags=["project"])
def project_list(req: Request):
    user: uuid.UUID = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    data, count = supabase.from_("user_setting").select(
        "team_id").eq("id", user).execute()
    if len(user[1]) == 0:
        raise HTTPException(status_code=500, detail="Supabase Error")
    team_id = data[1][0].get("team_id")
    if not team_id:
        raise HTTPException(status_code=400, detail="User not found")
    project_list = read_project_list(team_id)
    return {"status": "succeed", "project_list": project_list}
