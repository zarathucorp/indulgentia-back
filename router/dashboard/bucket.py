from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import UUID4
import uuid

from database import schemas
from func.dashboard.crud.bucket import *
from func.auth.auth import *


router = APIRouter(
    prefix="/bucket",
    responses={404: {"description": "Not found"}},
)


# read list


@router.get("/list/{project_id}", tags=["bucket"])
async def get_bucket_list(req: Request, project_id: str):
    try:
        test_id = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid UUID format")
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    data, count = supabase.rpc(
        "verify_project", {"user_id": str(user), "project_id": project_id}).execute()
    if not data[1]:
        raise HTTPException(status_code=403, detail="Forbidden")
    res = read_bucket_list(uuid.UUID(project_id))
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })

# read


@router.get("/{bucket_id}", tags=["bucket"])
async def get_bucket(req: Request, bucket_id: str):
    try:
        test_id = uuid.UUID(bucket_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid UUID format")
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    data, count = supabase.rpc(
        "verify_bucket", {"user_id": str(user), "bucket_id": bucket_id}).execute()
    if not data[1]:
        raise HTTPException(status_code=403, detail="Forbidden")
    res = read_bucket(uuid.UUID(bucket_id))
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })


# create


@router.post("/", tags=["bucket"])
async def add_bucket(req: Request, bucket: schemas.BucketCreate):
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    data, count = supabase.rpc("verify_project", {"user_id": str(
        user), "project_id": str(bucket.project_id)}).execute()
    if not data[1]:
        raise HTTPException(status_code=403, detail="Forbidden")
    res = create_bucket(bucket)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })

# update


@router.put("/{bucket_id}", tags=["bucket"])
async def change_bucket(req: Request, bucket: schemas.BucketUpdate):
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    # if not user == bucket.manager_id:
        # raise HTTPException(status_code=403, detail="Forbidden")
    res = update_bucket(bucket)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })

# delete


@router.delete("/{bucket_id}", tags=["bucket"])
async def drop_bucket(req: Request, bucket_id: str):
    try:
        test_id = uuid.UUID(bucket_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid UUID format")
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    data, count = supabase.table("bucket").select(
        "manager_id").eq("id", bucket_id).execute()
    if not data[1]:
        raise HTTPException(status_code=400, detail="No data")
    # if not user == data[1][0]["manager_id"]:
        # raise HTTPException(status_code=403, detail="Forbidden")
    res = flag_is_deleted_bucket(uuid.UUID(bucket_id))
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })


""" Old version
@router.delete("/{bucket_id}", tags=["bucket"])
async def drop_bucket(req: Request, bucket_id: str):
    user: UUID4 = verify_user(req)
    # if not user:
    #     raise HTTPException(status_code=401, detail="Unauthorized")
    data, count = supabase.table("bucket").select(
        "manager_id").eq("id", bucket_id).execute()
    if not data[1]:
        raise HTTPException(status_code=400, detail="No data")
    if not user == data[1][0]["manager_id"]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    res = delete_bucket(bucket_id)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
   })
"""


@router.get("/{bucket_id}/breadcrumb")
async def get_breadcrumb(req: Request, bucket_id: str):
    try:
        test_id = uuid.UUID(bucket_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid UUID format")
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    data, count = supabase.rpc(
        "bucket_breadcrumb_data", {"bucket_id": bucket_id}).execute()
    if not data[1]:
        raise HTTPException(status_code=403, detail="Forbidden")
    return JSONResponse(content={
        "status": "succeed",
        "data": data[1][0]
    })


@router.get("/{bucket_id}/github_repo")
async def get_connected_github_repositories(req: Request, bucket_id: str):
    # user: UUID4 = verify_user(req)
    # if not user:
    #     raise HTTPException(status_code=401, detail="Unauthorized")
    data = get_connected_gitrepo(uuid.UUID(bucket_id))
    # data, count = supabase.rpc(
    #     "verify_bucket", {"user_id": str(user), "bucket_id": bucket_id}).execute()
    # if not data[1]:
    #     raise HTTPException(status_code=403, detail="Forbidden")
    return JSONResponse(content={
        "status": "succeed",
        "data": data
    })


@router.post("/{bucket_id}/github_repo")
async def connect_github_repository(req: Request, bucket_id: str, newRepo: schemas.GitrepoCreate):
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    data = create_connected_gitrepo(newRepo, user)
    return JSONResponse(content={
        "status": "succeed",
        "data": data
    })


@router.delete("/{bucket_id}/github_repo/{repo_id}")
async def disconnect_github_repository(req: Request, bucket_id: str, repo_id: str):
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    data = flag_is_deleted_gitrepo(uuid.UUID(repo_id))
    return JSONResponse(content={
        "status": "succeed",
        "data": data
    })
