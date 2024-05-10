from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import UUID4

from database import schemas
from func.dashboard.crud.note import *


router = APIRouter(
    prefix="/note",
    responses={404: {"description": "Not found"}},
)


# read


@router.get("/{note_id}", tags=["note"])
async def get_note(req: Request, note_id: str):
    res = read_note(note_id)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })

# read list


@router.get("/list/{bucket_id}", tags=["note"])
async def get_note_list(req: Request, bucket_id: str):
    res = read_note_list(bucket_id)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })

# create


@router.post("/", tags=["note"])
async def add_note(req: Request, note: schemas.NoteCreate):
    res = create_note(note)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })

# update


@router.put("/{note_id}", tags=["note"])
async def change_note(req: Request, note: schemas.NoteUpdate):
    res = update_note(note)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })

# delete


@router.delete("/{note_id}", tags=["note"])
async def drop_note(req: Request, note_id: str):
    res = delete_note(note_id)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })
