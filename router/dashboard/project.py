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


router = APIRouter(
    prefix="/project",
    responses={404: {"description": "Not found"}},
)


class DownloadProjectInfo(BaseModel):
    project_ids: List[str]


@router.post("/file", tags=["project"])
async def get_project_files(req: Request, download_project_info: DownloadProjectInfo, background_tasks: BackgroundTasks):
    user: UUID4 = verify_user(req)
    project_ids = download_project_info.project_ids
    if not user:
        raise_custom_error(403, 213)
    if not validate_user_in_premium_team(user):
        raise_custom_error(401, 820)
    for project_id in project_ids:
        try:
            uuid.UUID(project_id)
        except ValueError:
            raise_custom_error(422, 210)

    download_project_infos = []
    for project_id in project_ids:
        try:
            project_info = {}
            # 프로젝트 유효성 검사
            data, count = supabase.rpc(
                "verify_project", {"user_id": str(user), "project_id": project_id}).execute()
            if not data[1]:
                raise_custom_error(401, 210)
            # 프로젝트의 버킷 목록 읽기
            bucket_list = read_bucket_list(uuid.UUID(project_id))
            bucket_ids = [bucket.get("id") for bucket in bucket_list]

            # 버킷의 노트 작업
            download_project_infos.extend(
                process_bucket_ids(user, bucket_ids, True, False)
            )
        except Exception as e:
            print(e)
            raise_custom_error(500, 312)

    current_time = datetime.now(
        timezone('Asia/Seoul')).strftime("%Y%m%d_%H%M%S GMT+0900")
    with zipfile.ZipFile(f"func/dashboard/pdf_generator/output/Report_{current_time}.zip", "w") as zipf:
        for project_info in download_project_infos:
            zipf.write(project_info["output_file"], project_info["filename"])

    # 작업 후 파일 삭제
    final_files_to_delete = []
    for project_info in download_project_infos:
        final_files_to_delete += project_info["files_to_delete"]
    final_files_to_delete.append(
        f"func/dashboard/pdf_generator/output/Report_{current_time}.zip")

    background_tasks.add_task(delete_files, final_files_to_delete)

    return FileResponse(f"func/dashboard/pdf_generator/output/Report_{current_time}.zip", filename=f"Report_{current_time}.zip", media_type="application/zip")

# read list


@router.get("/list/{team_id}", tags=["project"])
async def get_project_list(req: Request, team_id: str):
    try:
        uuid.UUID(team_id)
    except ValueError:
        raise_custom_error(422, 210)
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    if not validate_user_in_premium_team(user):
        raise_custom_error(401, 820)
    if not verify_team(user, team_id):
        raise_custom_error(401, 510)
    res = read_project_list(team_id)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })


@router.get("/list", tags=["project"])
async def get_project_list_by_current_user(req: Request):
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    if not validate_user_in_premium_team(user):
        raise_custom_error(401, 820)
    data, count = supabase.table("user_setting").select(
        "team_id").eq("is_deleted", False).eq("id", user).execute()
    if not data[1]:
        raise_custom_error(500, 231)
    if not data[1][0].get("team_id"):
        raise_custom_error(401, 540)
    else:
        res = read_project_list(data[1][0].get("team_id"))
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })

# read


@router.get("/{project_id}", tags=["project"])
async def get_project(req: Request, project_id: str):
    try:
        uuid.UUID(project_id)
    except ValueError:
        raise_custom_error(422, 210)
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    if not validate_user_in_premium_team(user):
        raise_custom_error(401, 820)
    data, count = supabase.rpc(
        "verify_project", {"user_id": str(user), "project_id": project_id}).execute()
    if not data[1]:
        raise_custom_error(401, 210)
    res = read_project(project_id)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })


# create

@router.post("", include_in_schema=False)
@router.post("/", tags=["project"])
async def add_project(req: Request, project: schemas.ProjectCreate):
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    if not validate_user_in_premium_team(user):
        raise_custom_error(401, 820)
    if not verify_team(user, project.team_id):
        raise_custom_error(401, 510)
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
        raise_custom_error(403, 213)
    if not validate_user_in_premium_team(user):
        raise_custom_error(401, 820)
    data, count = supabase.rpc("verify_project", {
                               "user_id": str(user), "project_id": str(project.id)}).execute()
    if not data[1]:
        raise_custom_error(401, 210)
    team_id = uuid.UUID(get_user_team(user))
    if not validate_user_is_leader(user, team_id):
        raise_custom_error(401, 520)

    res = update_project(project)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })

# delete


@router.delete("/{project_id}", tags=["project"])
async def drop_project(req: Request, project_id: str):
    try:
        uuid.UUID(project_id)
    except ValueError:
        raise_custom_error(422, 210)
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    if not validate_user_in_premium_team(user):
        raise_custom_error(401, 820)
    data, count = supabase.rpc(
        "verify_project", {"user_id": str(user), "project_id": project_id}).execute()
    if not data[1]:
        raise_custom_error(401, 210)
    team_id = uuid.UUID(get_user_team(user))
    if not validate_user_is_leader(user, team_id):
        raise_custom_error(401, 520)

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
