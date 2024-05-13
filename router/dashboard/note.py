from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import UUID4
from cloud.azure.blob_storage import generate_presigned_url
from database import schemas
from func.dashboard.crud.note import *
from func.auth.auth import *


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
    if not verify_bucket(user, bucket_id):
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
    if not verify_note(user, note_id):
        raise HTTPException(status_code=401, detail="Unauthorized")
    res = read_note(note_id)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })



# create


@router.post("/", tags=["note"])
async def add_note(req: Request, note: schemas.NoteCreate):
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not verify_bucket(user, note["bucket_id"]):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # need verify timestamp logic

    res = create_note(note)
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
    if not user == note["user_id"]:
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
