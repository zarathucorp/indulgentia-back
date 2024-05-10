from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
import uuid
from pydantic import UUID4
from typing import List

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
  