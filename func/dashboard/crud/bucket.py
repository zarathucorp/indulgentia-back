import json
from fastapi.responses import JSONResponse
from pydantic import UUID4
import uuid

from database.supabase import supabase
from database import schemas


def create_bucket(bucket: schemas.BucketCreate):
    try:
        bucket = bucket.model_dump(mode="json")

        data, count = supabase.table("bucket").insert({**bucket}).execute()
        print('='*120)
        print(data, count)
        return data[1]
    except Exception as e:
        print('='*120)
        print(e)
        return JSONResponse(status_code=400, content={"message": str(e)})

def read_bucket(bucket_id: UUID4):
    try:
        data, count = supabase.table("bucket").select('*').eq("id", bucket_id).single().execute()
        print('='*120)
        print(data, count)
        return data[1]
    except Exception as e:
        print('='*120)
        print(e)
        return JSONResponse(status_code=400, content={"message": str(e)})
    
def read_bucket_list(project_id: UUID4):
    try:
        data, count = supabase.table("bucket").select('*').eq("project_id", project_id).execute()
        print('='*120)
        print(data, count)
        return data[1]
    except Exception as e:
        print('='*120)
        print(e)
        return JSONResponse(status_code=400, content={"message": str(e)})

def update_bucket(bucket: schemas.BucketUpdate):
    try:
        bucket = bucket.model_dump()
        data, count = supabase.table("bucket").update(bucket).eq("id", bucket["id"]).execute()
        print('='*120)
        print(data, count)
        return data[1]
    except Exception as e:
        print('='*120)
        print(e)
        return JSONResponse(status_code=400, content={"message": str(e)})

def delete_bucket(bucket_id: UUID4):
    try:
        bucket = bucket.model_dump()
        data, count = supabase.table("bucket").delete().eq("id", bucket_id).execute()
        print('='*120)
        print(data, count)
        return data[1]
    except Exception as e:
        print('='*120)
        print(e)
        return JSONResponse(status_code=400, content={"message": str(e)})
    