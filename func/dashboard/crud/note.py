import json
from pydantic import UUID4

from database.supabase import supabase
from database import schemas


def create_note(note: schemas.NoteCreate):
    try:
        note = note.model_dump(mode="json")

        data, count = supabase.table("note").insert({**note}).execute()
        print('='*120)
        print(data, count)
        return {
            "status_code": 200,
            "content": data[1],
            "message": "succeed"
        }
    except Exception as e:
        print('='*120)
        print(e)
        return {
            "status_code": 400,
            "content": None,
            "message": str(e)
        }

def read_note(note_id: UUID4):
    try:
        data, count = supabase.table("note").select('*').eq("id", note_id).execute()
        print('='*120)
        print(data, count)
        if not data[1]:
            return {
                "status_code": 400,
                "content": None,
                "message": "No data"
            }
        return {
            "status_code": 200,
            "content": data[1][0],
            "message": "succeed"
        }
    except Exception as e:
        print('='*120)
        print(e)
        return {
            "status_code": 400,
            "content": None,
            "message": str(e)
        }

def read_note_list(bucket_id: UUID4):
    try:
        data ,count = supabase.table("note").select('*').eq("bucket_id", bucket_id).execute()
        print('='*120)
        print(data ,count)
        if not data[1]:
            return {
                "status_code": 400,
                "content": None,
                "message": "No data"
            }
        return {
            "status_code": 200,
            "content": data[1],
            "message": "succeed"
        }
    except Exception as e:
        print('='*120)
        print(e)
        return {
            "status_code": 400,
            "content": None,
            "message": str(e)
        }

def update_note(note: schemas.NoteUpdate):
    try:
        note = note.model_dump(mode="json")

        data, count = supabase.table("note").update(note).eq("id", note["id"]).execute()
        print('='*120)
        print(data, count)
        if not data[1]:
            return {
                "status_code": 400,
                "content": None,
                "message": "No data"
            }
        return {
            "status_code": 200,
            "content": data[1],
            "message": "succeed"
        }
    except Exception as e:
        print('='*120)
        print(e)
        return {
            "status_code": 400,
            "content": None,
            "message": str(e)
        }

def delete_note(note_id: UUID4):
    try:
        data, count = supabase.table("note").delete().eq("id", note_id).execute()
        print('='*120)
        print(data, count)
        if not data[1]:
            return {
                "status_code": 400,
                "content": None,
                "message": "No data"
            }
        return {
            "status_code": 200,
            "content": data[1][0],
            "message": "succeed"
        }
    except Exception as e:
        print('='*120)
        print(e)
        return {
            "status_code": 400,
            "content": None,
            "message": str(e)
        }
