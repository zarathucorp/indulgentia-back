import json
from pydantic import UUID4
from fastapi import HTTPException

from database.supabase import supabase
from database import schemas


def create_bucket(bucket: schemas.BucketCreate):
    try:
        bucket = bucket.model_dump(mode="json")

        data, count = supabase.table("bucket").insert({**bucket}).execute()
        print('='*120)
        print(data, count)
        return data[1][0]
    except Exception as e:
        print('='*120)
        print(e)
        raise HTTPException(status_code=400, detail=str(e))


def read_bucket(bucket_id: UUID4):
    try:
        data, count = supabase.table("bucket").select(
            '*').eq("is_deleted", False).eq("id", bucket_id).execute()
        print('='*120)
        print(data, count)
        if not data[1]:
            raise HTTPException(status_code=400, detail="No data")
        return data[1][0]
    except Exception as e:
        print('='*120)
        print(e)
        raise HTTPException(status_code=400, detail=str(e))


def read_bucket_list(project_id: UUID4):
    try:
        data, count = supabase.table("bucket").select(
            '*').eq("is_deleted", False).eq("project_id", project_id).order("created_at", desc=True).execute()
        print('='*120)
        print(data, count)
        return data[1]
    except Exception as e:
        print('='*120)
        print(e)
        raise HTTPException(status_code=400, detail=str(e))


def update_bucket(bucket: schemas.BucketUpdate):
    try:
        bucket = bucket.model_dump(mode="json")
        data, count = supabase.table("bucket").update(
            bucket).eq("is_deleted", False).eq("id", bucket["id"]).execute()
        print('='*120)
        print(data, count)
        if not data[1]:
            raise HTTPException(status_code=400, detail="No data")
        return data[1][0]
    except Exception as e:
        print('='*120)
        print(e)
        raise HTTPException(status_code=400, detail=str(e))


def flag_is_deleted_bucket(bucket_id: UUID4):
    try:
        data, count = supabase.table("bucket").update(
            {"is_deleted": True}).eq("id", bucket_id).execute()
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


def delete_bucket(bucket_id: UUID4):
    try:
        data, count = supabase.table("bucket").delete().eq(
            "id", bucket_id).execute()
        print('='*120)
        print(data, count)
        if not data[1]:
            raise HTTPException(status_code=400, detail="No data")
        return data[1][0]
    except Exception as e:
        print('='*120)
        print(e)
        raise HTTPException(status_code=400, detail=str(e))


def get_connected_gitrepo(bucket_id: UUID4):
    try:
        data, count = supabase.table("gitrepo").select(
            "*").eq("is_deleted", False).eq("bucket_id", bucket_id).execute()
        print('='*120)
        print(data, count)
        return data[1]
    except Exception as e:
        print('='*120)
        print(e)
        raise HTTPException(status_code=400, detail=str(e))


def create_connected_gitrepo(newRepo: schemas.GitrepoCreate, user: UUID4):
    repo = newRepo.model_dump(mode="json")
    try:
        data, count = supabase.table("gitrepo").insert(
            {**repo, "user_id": str(user)}).execute()
        print('='*120)
        print(data, count)
        return data[1]
    except Exception as e:
        print('='*120)
        print(e)
        raise HTTPException(status_code=400, detail=str(e))


# Don't use this
def delete_connected_gitrepo(repo_id: UUID4):
    try:
        data, count = supabase.table("gitrepo").delete().eq(
            "id", repo_id).execute()
        print('='*120)
        print(data, count)
        return data[1]
    except Exception as e:
        print('='*120)
        print(e)
        raise HTTPException(status_code=400, detail=str(e))


def flag_is_deleted_gitrepo(repo_id: UUID4):
    try:
        data, count = supabase.table("gitrepo").update(
            {"is_deleted": True}).eq("id", repo_id).execute()
        print('='*120)
        print(data, count)
        return data[1]
    except Exception as e:
        print('='*120)
        print(e)
        raise HTTPException(status_code=400, detail=str(e))
