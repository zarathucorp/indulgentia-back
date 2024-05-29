import json
from pydantic import UUID4
from fastapi import HTTPException

from database.supabase import supabase
from database import schemas


def create_note(note: schemas.NoteCreate):
    try:
        note = note.model_dump(mode="json")

        data, count = supabase.table("note").insert({**note}).execute()
        print('='*120)
        print(data, count)
        return data[1][0]
    except Exception as e:
        print('='*120)
        print(e)
        raise HTTPException(status_code=400, detail=str(e))


def read_note(note_id: UUID4):
    try:
        data, count = supabase.table("note").select(
            '*').eq("is_deleted", False).eq("id", note_id).execute()
        print('='*120)
        print(data, count)
        if not data[1]:
            raise HTTPException(status_code=400, detail="No data")
        return data[1][0]
    except Exception as e:
        print('='*120)
        print(e)
        raise HTTPException(status_code=400, detail=str(e))


def read_note_list(bucket_id: UUID4):
    try:
        data, count = supabase.table("note").select('*').eq("is_deleted", False).eq(
            "bucket_id", bucket_id).order("created_at", desc=True).execute()
        print('='*120)
        print(data, count)
        return data[1]
    except Exception as e:
        print('='*120)
        print(e)
        raise HTTPException(status_code=400, detail=str(e))


def update_note(note: schemas.NoteUpdate):
    try:
        note = note.model_dump(mode="json")

        data, count = supabase.table("note").update(
            note).eq("is_deleted", False).eq("id", note["id"]).execute()
        print('='*120)
        print(data, count)
        if not data[1]:
            raise HTTPException(status_code=400, detail="No data")
        return data[1][0]
    except Exception as e:
        print('='*120)
        print(e)
        raise HTTPException(status_code=400, detail=str(e))


def flag_is_deleted_note(note_id: UUID4):
    try:
        data, count = supabase.table("note").update(
            {"is_deleted": True}).eq("id", note_id).execute()
        print('='*120)
        print(data, count)
        if not data[1]:
            raise HTTPException(status_code=400, detail="No data")
        return data[1][0]
    except Exception as e:
        print('='*120)
        print(e)
        raise HTTPException(status_code=400, detail=str(e))

# Old version


def delete_note(note_id: UUID4):
    try:
        data, count = supabase.table(
            "note").delete().eq("id", note_id).execute()
        print('='*120)
        print(data, count)
        if not data[1]:
            raise HTTPException(status_code=400, detail="No data")
        return data[1][0]
    except Exception as e:
        print('='*120)
        print(e)
        raise HTTPException(status_code=400, detail=str(e))
