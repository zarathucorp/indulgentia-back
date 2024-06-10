import json
from pydantic import UUID4
from fastapi import HTTPException

from database.supabase import supabase
from database import schemas
from func.error.error import raise_custom_error


def create_bucket(bucket: schemas.BucketCreate):
    try:
        bucket = bucket.model_dump(mode="json")

        data, count = supabase.table("bucket").insert({**bucket}).execute()
        if not data[1]:
            raise_custom_error(500, 210)
        return data[1][0]
    except Exception as e:
        print(e)
        raise_custom_error(500, 210)


def read_bucket(bucket_id: UUID4):
    try:
        data, count = supabase.table("bucket").select(
            '*').eq("is_deleted", False).eq("id", bucket_id).execute()
        if not data[1]:
            raise_custom_error(500, 231)
        return data[1][0]
    except Exception as e:
        print(e)
        raise_custom_error(500, 230)


def read_bucket_list(project_id: UUID4):
    try:
        data, count = supabase.table("bucket").select(
            '*').eq("is_deleted", False).eq("project_id", project_id).order("created_at", desc=True).execute()
        return data[1]
    except Exception as e:
        print(e)
        raise_custom_error(500, 230)


def update_bucket(bucket: schemas.BucketUpdate):
    try:
        bucket = bucket.model_dump(mode="json")
        data, count = supabase.table("bucket").update(
            bucket).eq("is_deleted", False).eq("id", bucket["id"]).execute()
        if not data[1]:
            raise_custom_error(500, 220)
        return data[1][0]
    except Exception as e:
        print(e)
        raise_custom_error(500, 220)


def flag_is_deleted_bucket(bucket_id: UUID4):
    try:
        data, count = supabase.table("bucket").update(
            {"is_deleted": True}).eq("id", bucket_id).execute()
        if not data[1]:
            raise_custom_error(500, 242)
        return data[1][0]
    except Exception as e:
        print(e)
        raise_custom_error(500, 240)

# Old version


def delete_bucket(bucket_id: UUID4):
    try:
        data, count = supabase.table("bucket").delete().eq(
            "id", bucket_id).execute()
        if not data[1]:
            raise_custom_error(500, 241)
        return data[1][0]
    except Exception as e:
        print(e)
        raise_custom_error(500, 240)


def get_connected_gitrepo(bucket_id: UUID4):
    try:
        data, count = supabase.table("gitrepo").select(
            "*").eq("is_deleted", False).eq("bucket_id", bucket_id).execute()
        if not data[1]:
            raise_custom_error(500, 231)
        return data[1]
    except Exception as e:
        print(e)
        raise_custom_error(500, 230)


def create_connected_gitrepo(newRepo: schemas.GitrepoCreate, user: UUID4):
    repo = newRepo.model_dump(mode="json")
    try:
        data, count = supabase.table("gitrepo").insert(
            {**repo, "user_id": str(user)}).execute()
        if not data[1]:
            raise_custom_error(500, 210)
        return data[1]
    except Exception as e:
        print(e)
        raise_custom_error(500, 210)


# Don't use this
def delete_connected_gitrepo(repo_id: UUID4):
    try:
        data, count = supabase.table("gitrepo").delete().eq(
            "id", repo_id).execute()
        if not data[1]:
            raise_custom_error(500, 241)
        return data[1]
    except Exception as e:
        print(e)
        raise_custom_error(500, 240)


def flag_is_deleted_gitrepo(repo_id: UUID4):
    try:
        data, count = supabase.table("gitrepo").update(
            {"is_deleted": True}).eq("id", repo_id).execute()
        if not data[1]:
            raise_custom_error(500, 242)
        return data[1]
    except Exception as e:
        print(e)
        raise_custom_error(500, 240)
