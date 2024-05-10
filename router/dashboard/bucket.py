from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import UUID4

from database import schemas
from func.dashboard.crud.bucket import *


router = APIRouter(
    prefix="/bucket",
    responses={404: {"description": "Not found"}},
)

@router.post("/")
async def add_bucket(req: Request, bucket: schemas.BucketCreate):
    res = create_bucket(bucket)
    if res["status_code"] >= 300:
        return JSONResponse(status_code=res["status_code"], content={
            "status": "failed",
            "message": res["message"]
        })
    return JSONResponse(content={
        "status": "succeed",
        "data": res["content"]
    })

@router.get("/{bucket_id}")
async def get_bucket(req: Request, bucket_id: str):
    res = read_bucket(bucket_id)
    if res["status_code"] >= 300:
        return JSONResponse(status_code=res["status_code"], content={
            "status": "failed",
            "message": res["message"]
        })
    return JSONResponse(content={
        "status": "succeed",
        "data": res["content"]
    })

@router.get("/list/{project_id}")
async def get_bucket_list(req: Request, project_id: str):
    res = read_bucket_list(project_id)
    if res["status_code"] >= 300:
        return JSONResponse(status_code=res["status_code"], content={
            "status": "failed",
            "message": res["message"]
        })
    return JSONResponse(content={
        "status": "succeed",
        "data": res["content"]
    })

@router.put("/")
async def change_bucket(req: Request, bucket: schemas.BucketUpdate):
    res = update_bucket(bucket)
    if res["status_code"] >= 300:
        return JSONResponse(status_code=res["status_code"], content={
            "status": "failed",
            "message": res["message"]
        })
    return JSONResponse(content={
        "status": "succeed",
        "data": res["content"]
    })

@router.delete("/{bucket_id}")
async def drop_bucket(req: Request, bucket_id: str):
    res = delete_bucket(bucket_id)
    if res["status_code"] >= 300:
        return JSONResponse(status_code=res["status_code"], content={
            "status": "failed",
            "message": res["message"]
        })
    return JSONResponse(content={
        "status": "succeed",
        "data": res["content"]
   })
