import json
from pydantic import UUID4

from database.supabase import supabase
from database import schemas


def create_bucket(bucket: schemas.BucketCreate):
    try:
        bucket = bucket.model_dump(mode="json")

        data, count = supabase.table("bucket").insert({**bucket}).execute()
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

def read_bucket(bucket_id: UUID4):
    try:
        data, count = supabase.table("bucket").select('*').eq("id", bucket_id).execute()
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
    
def read_bucket_list(project_id: UUID4):
    try:
        data, count = supabase.table("bucket").select('*').eq("project_id", project_id).execute()
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

def update_bucket(bucket: schemas.BucketUpdate):
    try:
        bucket = bucket.model_dump()
        data, count = supabase.table("bucket").update(bucket).eq("id", bucket["id"]).execute()
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

def delete_bucket(bucket_id: UUID4):
    try:
        bucket = bucket.model_dump()
        data, count = supabase.table("bucket").delete().eq("id", bucket_id).execute()
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
    