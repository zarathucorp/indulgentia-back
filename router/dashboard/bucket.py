from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import UUID4

from database import schemas
from func.dashboard.crud.bucket import *


router = APIRouter(
    prefix="/bucket",
    responses={404: {"description": "Not found"}},
)


# read


@router.get("/{bucket_id}", tags=["bucket"])
async def get_bucket(req: Request, bucket_id: str):
    res = read_bucket(bucket_id)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })

# read list


@router.get("/list/{project_id}", tags=["bucket"])
async def get_bucket_list(req: Request, project_id: str):
    res = read_bucket_list(project_id)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })

# create


@router.post("/", tags=["bucket"])
async def add_bucket(req: Request, bucket: schemas.BucketCreate):
    res = create_bucket(bucket)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })

# update


@router.put("/{bucket_id}", tags=["bucket"])
async def change_bucket(req: Request, bucket: schemas.BucketUpdate):
    res = update_bucket(bucket)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })

# delete


@router.delete("/{bucket_id}", tags=["bucket"])
async def drop_bucket(req: Request, bucket_id: str):
    res = delete_bucket(bucket_id)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
   })
