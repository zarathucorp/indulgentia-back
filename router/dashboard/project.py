from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
import uuid
from pydantic import UUID4
from typing import List
from func.auth.auth import verify_user

from database import supabase, schemas
from func.dashboard.crud.project import *


router = APIRouter(
    prefix="/project",
    responses={404: {"description": "Not found"}},
)

# create


@router.post("/")
async def add_project(req: Request, project: schemas.ProjectCreate):
    # user verification?
    print(req)

    res = create_project(project)
    if res["status_code"] >= 300:
        return JSONResponse(status_code=res["status_code"], content={
            "status": "failed",
            "message": res["message"]
        })
    return JSONResponse(content={
        "status": "succeed",
        "data": res["content"]
    })

# read


@router.get("/{project_id}")
async def get_project(req: Request, project_id: str):
    res = read_project(project_id)
    if res["status_code"] >= 300:
        return JSONResponse(status_code=res["status_code"], content={
            "status": "failed",
            "message": res["message"]
        })
    return JSONResponse(content={
        "status": "succeed",
        "data": res["content"]
    })

# read list


@router.get("/list/{team_id}")
async def get_project_list(req: Request, team_id: str):
    res = read_project_list(team_id)
    if res["status_code"] >= 300:
        return JSONResponse(status_code=res["status_code"], content={
            "status": "failed",
            "message": res["message"]
        })
    return JSONResponse(content={
        "status": "succeed",
        "data": res["content"]
    })

# update


@router.put("/")
async def change_project(req: Request, project: schemas.ProjectUpdate):
    res = update_project(project)
    if res["status_code"] >= 300:
        return JSONResponse(status_code=res["status_code"], content={
            "status": "failed",
            "message": res["message"]
        })
    return JSONResponse(content={
        "status": "succeed",
        "data": res["content"]
    })

# delete


@router.delete("/{project_id}")
async def drop_project(req: Request, project_id: str):
    # project_id = uuid.UUID(project_id, version=4)
    res = delete_project(project_id)
    if res["status_code"] >= 300:
        return JSONResponse(status_code=res["status_code"], content={
            "status": "failed",
            "message": res["message"]
        })
    return JSONResponse(content={
        "status": "succeed",
        "data": res["content"]
    })


@router.get("/")
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
    return JSONResponse(content={
        "status": "succeed",
        "data": project_list["content"]
    })
