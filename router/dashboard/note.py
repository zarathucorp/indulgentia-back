from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import UUID4
from typing import List

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
    data, count = supabase.rpc("verify_bucket", {"user_id": str(user), "bucket_id": bucket_id}).execute()
    if not data[1]:
        raise HTTPException(status_code=401, detail="Unauthorized")
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
    data, count = supabase.rpc("verify_note", {"user_id": user, "note_id": note_id}).execute()
    if not data[1]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    res = read_note(note_id)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })



# create


@router.post("/", tags=["note"])
async def add_note(files: List[UploadFile], bucket_id: UUID4 = Form(...), title: str = Form(...), file_name: str = Form(...), is_github: bool = Form(...), description: str = None):
    # user: UUID4 = verify_user(req)
    # if not user:
    #     raise HTTPException(status_code=401, detail="Unauthorized")
    # data, count = supabase.rpc("verify_bucket", {"user_id": user, "bucket_id": note.get("bucket_id", "")}).execute()
    # if not data[1]:
    #     raise HTTPException(status_code=401, detail="Unauthorized")

    # Test user
    from uuid import UUID
    user = UUID("6a423db5-8a34-4153-9795-c6f058020445", version=4)
    
    # need verify timestamp logic

    note = schemas.NoteCreate(user_id=user, bucket_id=bucket_id, title=title, file_name=file_name, is_github=is_github, description=description, is_deleted=False)
    res = create_note(note)
    # create pdf
    try:
        contents = []
        for file in files:
            contents.append(await file.read())
        pdf_res = generate_pdf(note_id=res.get("id"), description=description, files=files, contents=contents)
        print(pdf_res)
        if not pdf_res:
            raise HTTPException(status_code=500, detail="Internal Server Error")
        # upload pdf
        with open(pdf_res, "rb") as f:
            pdf_data = f.read()
        await upload_blob(pdf_data, note.id + ".pdf")
    except Exception as e:
        delete_note(res.get("id"))
        raise HTTPException(status_code=500, detail=str(e))

    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })

# update


@router.put("/{note_id}", tags=["note"])
async def change_note(req: Request, note: schemas.NoteUpdate):
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not user == note.user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
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
    data, count = supabase.table("note").select("user_id").eq("id", note_id).execute()
    if not data[1]:
        raise HTTPException(status_code=400, detail="No data")
    if not user == data[1][0]["user_id"]:
        raise HTTPException(status_code=401, detail="Unauthorized")
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
    data, count = supabase.table("note").select("user_id").eq("id", note_id).execute()
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
