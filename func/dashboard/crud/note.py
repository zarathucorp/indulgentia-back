import json
from fastapi.responses import JSONResponse
from pydantic import UUID4
from gotrue.errors import AuthApiError
import uuid

from database.supabase import supabase
from database import schemas


def create_note(note: schemas.NoteCreate):
    try:
        note = note.model_dump(mode="json")

        data, count = supabase.table("Note").insert({**note}).execute()
        print('='*120)
        print(data, count)

        return data[1]
    except AuthApiError as message:
        print('='*120)
        print(message)
        return JSONResponse(status_code=400, content={"message": str(message)})

def read_note(note_id: UUID4):
    try:
        data, count = supabase.table("Note").select('*').eq("id", note_id).single().execute()
        print('='*120)
        print(data, count)
        return data[1]
    except AuthApiError as message:
        return JSONResponse(status_code=400, content={"message": str(message)})

def read_note_list(bucket_id: UUID4):
    try:
        data ,count = supabase.table("Note").select('*').eq("bucket_id", bucket_id).execute()
        print('='*120)
        print(data ,count)
        return data[1]
    except AuthApiError as message:
        return JSONResponse(status_code=400, content={"message": str(message)})

def update_note(note: schemas.NoteUpdate):
    try:
        note = note.model_dump(mode="json")

        data, count = supabase.table("Note").update(note).eq("id", note["id"]).execute()
        print('='*120)
        print(data, count)
        return data[1]
    except AuthApiError as message:
        return JSONResponse(status_code=400, content={"message": str(message)})

def delete_note(note_id: UUID4):
    try:
        data, count = supabase.table("Note").delete().eq("id", note_id).execute()
        print('='*120)
        print(data, count)
        return data[1]
    except AuthApiError as message:
        return JSONResponse(status_code=400, content={"message": str(message)})
