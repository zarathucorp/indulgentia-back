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
async def add_project(request: Request, project: schemas.ProjectCreate):
    # user verification?
    print(request)

    res = create_project(project)
    return JSONResponse(content={
        "status": "succeed",
        "data": res   
    })
    
# read
@router.get("/{project_id}")
async def get_project(request: Request, project_id: str):
    # user verification?
    print(request)

    # project_id = uuid.UUID(project_id, version=4)
    res = read_project(project_id)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })

# read list
@router.get("/list/{team_id}")
async def get_project_list(request: Request, team_id: str):
    # user verification?

    # team_id = uuid.UUID(team_id, version=4)
    res = read_project_list(team_id)
    print(res)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })

# update
@router.put("/")
async def change_project(request: Request, project: schemas.ProjectUpdate):
    # user verification?

    res = update_project(project)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })

# delete
@router.delete("/{project_id}")
async def drop_project(request: Request, project_id: str):
    # user verification?
    
    # project_id = uuid.UUID(project_id, version=4)
    res = delete_project(project_id)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })
