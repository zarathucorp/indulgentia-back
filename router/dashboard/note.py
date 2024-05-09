from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import UUID4

from database import schemas
from func.dashboard.crud.note import *


router = APIRouter(
    prefix="/note",
    responses={404: {"description": "Not found"}},
)


@router.post("/")
async def add_note(req: Request, note: schemas.NoteCreate):
    res = create_note(note)
    if res["status_code"] >= 300:
        return JSONResponse(status_code=res["status_code"], content={
            "status": "failed",
            "message": res["message"]
        })
    return JSONResponse(content={
        "status": "succeed",
        "data": res["content"]
    })

@router.get("/{note_id}")
async def get_note(req: Request, note_id: str):
    res = read_note(note_id)
    if res["status_code"] >= 300:
        return JSONResponse(status_code=res["status_code"], content={
            "status": "failed",
            "message": res["message"]
        })
    return JSONResponse(content={
        "status": "succeed",
        "data": res["content"]
    })

@router.get("/list/{bucket_id}")
async def get_note_list(req: Request, bucket_id: str):
    res = read_note_list(bucket_id)
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
async def change_note(req: Request, note: schemas.NoteUpdate):
    res = update_note(note)
    if res["status_code"] >= 300:
        return JSONResponse(status_code=res["status_code"], content={
            "status": "failed",
            "message": res["message"]
        })
    return JSONResponse(content={
        "status": "succeed",
        "data": res["content"]
    })

@router.delete("/{note_id}")
async def drop_note(req: Request, note_id: str):
    res = delete_note(note_id)
    if res["status_code"] >= 300:
        return JSONResponse(status_code=res["status_code"], content={
            "status": "failed",
            "message": res["message"]
        })
    return JSONResponse(content={
        "status": "succeed",
        "data": res["content"]
    })
