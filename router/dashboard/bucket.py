from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import UUID4

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
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    data, count = supabase.rpc(
        "verify_project", {"user_id": str(user), "project_id": project_id}).execute()
    if not data[1]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    res = read_bucket_list(project_id)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })

# read


@router.get("/{bucket_id}", tags=["bucket"])
async def get_bucket(req: Request, bucket_id: str):
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    data, count = supabase.rpc(
        "verify_bucket", {"user_id": str(user), "bucket_id": bucket_id}).execute()
    if not data[1]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    res = read_bucket(bucket_id)
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
        raise HTTPException(status_code=401, detail="Unauthorized")
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
    #     raise HTTPException(status_code=401, detail="Unauthorized")
    res = update_bucket(bucket)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })

# delete


@router.delete("/{bucket_id}", tags=["bucket"])
async def drop_bucket(req: Request, bucket_id: str):
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    data, count = supabase.table("bucket").select(
        "manager_id").eq("id", bucket_id).execute()
    if not data[1]:
        raise HTTPException(status_code=400, detail="No data")
    # if not user == data[1][0]["manager_id"]:
    #     raise HTTPException(status_code=401, detail="Unauthorized")
    res = flag_is_deleted_bucket(bucket_id)
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
    data, count = supabase.table("bucket").select("manager_id").eq("id", bucket_id).execute()
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
