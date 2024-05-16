from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from pydantic import UUID4

from database.supabase import supabase
from func.auth.auth import verify_user
from cloud.azure.blob_storage import *
from env import DEFAULT_AZURE_CONTAINER_NAME

router = APIRouter(
    prefix="/settings",
    responses={404: {"description": "Not found"}},
)

# Temp
SIGNATURE_AZURE_CONTAINER_NAME = DEFAULT_AZURE_CONTAINER_NAME


@router.get("/signature", tags=["settings"])
def get_signature(req: Request):
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    blob_url = generate_presigned_url(str(user), container_name=SIGNATURE_AZURE_CONTAINER_NAME)
    res = download_blob(blob_url)

    return FileResponse(res)


@router.post("/signature", tags=["settings"])
async def add_signature(req: Request, file: UploadFile = File(...)):
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    data = await file.read()
    blob_url = generate_presigned_url(str(user), container_name=SIGNATURE_AZURE_CONTAINER_NAME)
    res = upload_blob(blob_url, data)
    if res:
        data, count = supabase.table("user_setting").update({"has_signature": True}).eq("id", user).execute()
        if not data[1]:
            raise HTTPException(status_code=500, detail="Internal Server Error")
        return JSONResponse(content={
            "status": "succeed",
            "has_signature": data[1].get("has_signature")
        })
    else:
        return JSONResponse(content={
            "status": "failed",
        })


@router.delete("/signature", tags=["settings"])
def drop_signature(req: Request):
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    blob_url = generate_presigned_url(str(user), container_name=SIGNATURE_AZURE_CONTAINER_NAME)
    res = delete_blob(blob_url)
    if res:
        data, count = supabase.table("user_setting").update({"has_signature": False}).eq("id", user).execute()
        if not data[1]:
            raise HTTPException(status_code=500, detail="Internal Server Error")
        return JSONResponse(content={
            "status": "succeed",
            "has_signature": data[1].get("has_signature")
        })
    else:
        return JSONResponse(content={
            "status": "failed",
        })
