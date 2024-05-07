import json
from fastapi.responses import JSONResponse
from pydantic import UUID4
from gotrue.errors import AuthApiError
import uuid

from database.supabase import supabase
from database import schemas


def create_bucket(bucket: schemas.BucketCreate):
    try:
        bucket = bucket.model_dump(mode="json")

        data, count = supabase.table("Bucket").insert({**bucket}).execute()
        print('='*120)
        print(data, count)
        return data[1]
    except AuthApiError as message:
        print('='*120)
        print(message)
        return JSONResponse(status_code=400, content={"message": str(message)})

def read_bucket(bucket_id: UUID4):
    try:
        data, count = supabase.table("Bucket").select('*').eq("id", bucket_id).single().execute()
        print('='*120)
        print(data, count)
        return data[1]
    except AuthApiError as message:
        return JSONResponse(status_code=400, content={"message": str(message)})
    
def read_bucket_list(project_id: UUID4):
    try:
        data, count = supabase.table("Bucket").select('*').eq("project_id", project_id).execute()
        print('='*120)
        print(data, count)
        return data[1]
    except AuthApiError as message:
        return JSONResponse(status_code=400, content={"message": str(message)})

def update_bucket(bucket: schemas.BucketUpdate):
    try:
        bucket = bucket.model_dump()
        data, count = supabase.table("Bucket").update(bucket).eq("id", bucket["id"]).execute()
        print('='*120)
        print(data, count)
        return data[1]
    except AuthApiError as message:
        return JSONResponse(status_code=400, content={"message": str(message)})

def delete_bucket(bucket_id: UUID4):
    try:
        bucket = bucket.model_dump()
        data, count = supabase.table("Bucket").delete().eq("id", bucket_id).execute()
        print('='*120)
        print(data, count)
        return data[1]
    except AuthApiError as message:
        return JSONResponse(status_code=400, content={"message": str(message)})
    