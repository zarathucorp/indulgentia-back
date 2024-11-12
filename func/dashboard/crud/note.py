import json
from pydantic import UUID4

from database.supabase import supabase
from database import schemas
from func.error.error import raise_custom_error


def create_note(note: schemas.NoteCreate):
    try:
        note = note.model_dump(mode="json")

        data, count = supabase.table("note").insert({**note}).execute()
        if not data[1]:
            raise_custom_error(500, 210)
        return data[1][0]
    except Exception as e:
        print(e)
        raise_custom_error(500, 210)


def read_note(note_id: UUID4):
    try:
        data, count = supabase.table("note").select(
            '*').eq("is_deleted", False).eq("id", note_id).execute()
        if not data[1]:
            raise_custom_error(500, 231)
        return data[1][0]
    except Exception as e:
        print(e)
        raise_custom_error(500, 230)


def read_note_detail(note_id: UUID4):
    try:
        data, count = supabase.rpc(
            "get_note_details", {"p_note_id": str(note_id)}).execute()
        if not data[1]:
            raise_custom_error(500, 231)
        return data[1][0]
    except Exception as e:
        print(e)
        raise_custom_error(500, 230)


def read_note_list(bucket_id: UUID4):
    try:
        # data, count = supabase.table("note").select('*').eq("is_deleted", False).eq(
        #     "bucket_id", bucket_id).order("created_at", desc=True).execute()
        data, count = supabase.rpc(
            "read_note_list_with_user_setting", {"b_id": str(bucket_id)}).execute()
        if not data:
            raise_custom_error(500, 231)
        return data[1]
    except Exception as e:
        print(e)
        raise_custom_error(500, 230)


def update_note(note: schemas.NoteUpdate):
    try:
        note = note.model_dump(mode="json")

        data, count = supabase.table("note").update(
            note).eq("is_deleted", False).eq("id", note["id"]).execute()
        if not data[1]:
            raise_custom_error(500, 220)
        return data[1][0]
    except Exception as e:
        print(e)
        raise_custom_error(500, 220)


def flag_is_deleted_note(note_id: UUID4):
    try:
        data, count = supabase.table("note").update(
            {"is_deleted": True}).eq("id", note_id).execute()
        if not data[1]:
            raise_custom_error(500, 242)
        return data[1][0]
    except Exception as e:
        print(e)
        raise_custom_error(500, 240)

# Old version


def delete_note(note_id: UUID4):
    try:
        data, count = supabase.table(
            "note").delete().eq("id", note_id).execute()
        if not data[1]:
            raise_custom_error(500, 241)
        return data[1][0]
    except Exception as e:
        print(e)
        raise_custom_error(500, 240)
