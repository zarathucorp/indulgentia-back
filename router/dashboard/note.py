from fastapi import APIRouter, Depends, HTTPException, Request, File, UploadFile, Form
from fastapi.responses import JSONResponse
from pydantic import UUID4
from typing import Optional, List
import os
import uuid

from cloud.azure.blob_storage import *
from database import schemas
from func.dashboard.crud.note import *
from func.auth.auth import *
from func.dashboard.pdf_generator.pdf_generator import generate_pdf


router = APIRouter(
    prefix="/note",
    responses={404: {"description": "Not found"}},
)


# read list


@router.get("/list/{bucket_id}", tags=["note"])
async def get_note_list(req: Request, bucket_id: str):
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    data, count = supabase.rpc(
        "verify_bucket", {"user_id": str(user), "bucket_id": bucket_id}).execute()
    if not data[1]:
        raise HTTPException(status_code=403, detail="Forbidden")
    res = read_note_list(bucket_id)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })

# read


@router.get("/{note_id}", tags=["note"])
async def get_note(req: Request, note_id: str):
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    data, count = supabase.rpc(
        "verify_note", {"user_id": user, "note_id": note_id}).execute()
    if not data[1]:
        raise HTTPException(status_code=403, detail="Forbidden")
    res = read_note(note_id)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })


# create


@router.post("/", tags=["note"])
# file: Optional[UploadFile] = File(None)
async def add_note(req: Request,
                   bucket_id: UUID4 = Form(...),
                   title: str = Form(...),
                   file_name: str = Form(...),
                   is_github: bool = Form(...),
                   files: List[UploadFile] = File(None),
                   description: str = Form(None)
                   ):
    user: UUID4 = verify_user(req)
    note_id = uuid.uuid4()
    note = schemas.NoteCreate(
        id=note_id,
        bucket_id=bucket_id,
        user_id=user,
        title=title,
        file_name=file_name,
        is_github=is_github
    )
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    data, count = supabase.rpc(
        "verify_bucket", {"user_id": str(user), "bucket_id": str(note.bucket_id)}).execute()
    if not data[1]:
        raise HTTPException(status_code=403, detail="Forbidden")

    try:
        contents = []
        if files:
            for file in files:
                contents.append(await file.read())
        pdf_res = generate_pdf(
            note_id=str(note_id), description=description, files=files, contents=contents)
        # upload pdf
        with open(pdf_res, "rb") as f:
            pdf_data = f.read()
        upload_blob(pdf_data, str(note_id) + ".pdf")
    except Exception as e:
        print(e)
        res_e = delete_note(str(note_id))
        print(res_e)
        raise HTTPException(status_code=500, detail=str(e))

    # delete result pdf
    SOURCE_PATH = "func/dashboard/pdf_generator"
    if os.path.isfile(f"{SOURCE_PATH}/output/{note_id}.pdf"):
        os.unlink(f"{SOURCE_PATH}/output/{note_id}.pdf")
        print(f"{SOURCE_PATH}/output/{note_id}.pdf deleted")

    res = create_note(note)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })

    # need verify timestamp logic


# update


@router.put("/{note_id}", tags=["note"])
async def change_note(req: Request, note: schemas.NoteUpdate):
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not user == note.user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # need verify timestamp logic

    res = update_note(note)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })

# delete


@router.delete("/{note_id}", tags=["note"])
async def drop_note(req: Request, note_id: str):
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    data, count = supabase.table("note").select(
        "user_id").eq("id", note_id).execute()
    if not data[1]:
        raise HTTPException(status_code=400, detail="No data")
    if not user == data[1][0]["user_id"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    res = flag_is_deleted_note(note_id)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })

""" Old version
@router.delete("/{note_id}", tags=["note"])
async def drop_note(req: Request, note_id: str):
    user: UUID4 = verify_user(req)
    # if not user:
    #     raise HTTPException(status_code=401, detail="Unauthorized")
    data, count = supabase.table("note").select(
        "user_id").eq("id", note_id).execute()
    if not data[1]:
        raise HTTPException(status_code=400, detail="No data")
    if not user == data[1][0]["user_id"]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    res = delete_note(note_id)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })
"""


@router.get("/file/{note_id}")
async def get_note_file(req: Request, note_id: str):
    # Auth 먼저 해야함
    try:
        url = generate_presigned_url(note_id + ".pdf")
        return JSONResponse(content={"status": "succeed", "url": url})
    except Exception as e:
        return JSONResponse(status_code=400, content={"status": "failed", "message": str(e)})


@router.get("/{note_id}/breadcrumb")
async def get_breadcrumb(req: Request, note_id: str):
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    data, count = supabase.rpc(
        "note_breadcrumb_data", {"note_id": note_id}).execute()
    if not data[1]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return JSONResponse(content={
        "status": "succeed",
        "data": data[1][0]
    })
