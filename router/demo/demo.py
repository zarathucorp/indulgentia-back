from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
import uuid
from pydantic import UUID4
from typing import Optional, List
import uuid
from datetime import datetime
from pytz import timezone
import zipfile

from database import supabase, schemas
from func.auth.auth import *
from func.dashboard.crud.project import *
from func.dashboard.crud.bucket import *
from func.dashboard.crud.note import *
from func.user.team import *
from func.error.error import raise_custom_error
from func.note_handling.note_export import process_bucket_ids, delete_files
from cloud.azure.blob_storage import *

router = APIRouter(
    prefix="/demo/dashboard",
    responses={404: {"description": "Not found"}},
)

DEMO_TEAM_ID = "93aed9f7-44bf-4dc6-a5c6-b4cb1788cf69"
DEMO_PROJECT_LIST = ["84be34cb-b709-478f-b644-2c6045a72257"]
DEMO_BUCKET_LIST = [
    "3824463e-3b63-40e5-ba2c-80537e891a97",
    "48dc5533-676f-47f5-9c4e-e831dd89d8bb",
    "7381ffa4-14af-40f2-994b-b509eb2adc5a",
    "814a3b18-ca64-4167-9485-2d5051e23f8f",
    "9e77b6ac-0583-4447-bf24-d738ef19316e",
    "ccb444cf-df33-4f1a-a351-4bf40ed5c180"
]

DEMO_NOTE_LIST = [
    "606ad635-5950-488c-af49-4775852c5bf6",
    "8e1d2324-324e-4d0f-bfe3-9b85e6cf9e1c",
    "f65f9d7f-1498-4f0f-8cea-31fc5cdee287",
    "cc353c01-2c49-45cb-a160-d6664b48d364",
    "5c9141ba-5c54-4f9d-9ae9-55625fa1f625",
    "0fd57894-cdf1-4127-8881-0891ef6aa2ce",
    "d2f35dcd-97af-4c00-b24f-6a3fc5ad2c20",
    "1c174c5f-7794-4e45-ba9d-a38cda1a6938",
    "50f5e321-d33c-4d33-b8a0-02c69f01c8e9",
    "a7302d6b-76bd-4006-abc4-f4ceed30027b",
    "3c6b518c-5895-458e-b135-bb67a52b0b70",
    "08b21861-3373-460a-b1fc-bdde014da330",
    "699f5885-6085-482f-96ba-5706c68bb570",
    "439f213d-655a-46a1-a99c-98bfd2ecf42d",
    "e5ce0c50-9a3f-48e9-a73c-45e211d69779",
    "54787183-21bd-49a4-89d7-4798e2dfb6a3",
    "4c7d5d78-745f-4f63-996a-9d023085aa2d"
]


@router.get("/project/list", tags=["demo"])
async def get_demo_project_list(req: Request):
    res = read_project_list(uuid.UUID(DEMO_TEAM_ID))
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })


@router.get("/project/{project_id}", tags=["demo"])
async def get_demo_project(req: Request, project_id: str):
    try:
        uuid.UUID(project_id)
        if project_id not in DEMO_PROJECT_LIST:
            raise_custom_error(422, 210)
    except ValueError:
        raise_custom_error(422, 210)
    res = read_project(uuid.UUID(project_id))
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })


@router.get("/bucket/list/{project_id}", tags=["demo"])
async def get_demo_bucket_list(req: Request, project_id: str):
    try:
        uuid.UUID(project_id)
        if project_id not in DEMO_PROJECT_LIST:
            raise_custom_error(422, 210)
    except ValueError:
        raise_custom_error(422, 210)

    res = read_bucket_list(uuid.UUID(project_id))
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })


@router.get("/bucket/{bucket_id}/breadcrumb", tags=["demo"])
async def get_demo_bucket_breadcrumb(req: Request, bucket_id: str):
    try:
        uuid.UUID(bucket_id)
        if bucket_id not in DEMO_BUCKET_LIST:
            raise_custom_error(422, 210)
    except ValueError:
        raise_custom_error(422, 210)
    data, count = supabase.rpc(
        "bucket_breadcrumb_data", {"bucket_id": bucket_id}).execute()
    if not data[1]:
        raise_custom_error(500, 250)
    return JSONResponse(content={
        "status": "succeed",
        "data": data[1][0]
    })


@router.get("/note/{note_id}", tags=["demo"])
async def get_demo_note(req: Request, note_id: str):
    try:
        uuid.UUID(note_id)
        if note_id not in DEMO_NOTE_LIST:
            raise_custom_error(422, 210)
    except ValueError:
        raise_custom_error(422, 210)
    res = read_note_detail(uuid.UUID(note_id))
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })


@router.get("/note/list/{bucket_id}", tags=["demo"])
async def get_demo_note_list(req: Request, bucket_id: str):
    try:
        uuid.UUID(bucket_id)
        if bucket_id not in DEMO_BUCKET_LIST:
            raise_custom_error(422, 210)
    except ValueError:
        raise_custom_error(422, 210)
    res = read_note_list(uuid.UUID(bucket_id))
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })


@ router.get("/note/{note_id}/breadcrumb", tags=["demo"])
async def get_demo_note_breadcrumb(req: Request, note_id: str):
    try:
        uuid.UUID(note_id)
        if note_id not in DEMO_NOTE_LIST:
            raise_custom_error(422, 210)
    except ValueError:
        raise_custom_error(422, 210)
    data, count = supabase.rpc(
        "note_breadcrumb_data", {"note_id": note_id}).execute()
    if not data[1]:
        raise_custom_error(500, 250)
    return JSONResponse(content={
        "status": "succeed",
        "data": data[1][0]
    })


@ router.get("/note/file/{note_id}", tags=["demo"])
async def get_demo_note_file(req: Request, note_id: str):
    try:
        uuid.UUID(note_id)
        if note_id not in DEMO_NOTE_LIST:
            raise_custom_error(422, 210)
    except ValueError:
        raise_custom_error(422, 210)
    # generate_presigned_url 오류 시 500 에러 발생
    try:
        url = generate_presigned_url(note_id + ".pdf")
        return JSONResponse(content={"status": "succeed", "url": url})
    except Exception as e:
        print(e)
        raise_custom_error(500, 312)
