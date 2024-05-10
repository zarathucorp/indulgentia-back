import json
from pydantic import UUID4
from fastapi import HTTPException

from database.supabase import supabase
from database import schemas


def create_project(project: schemas.ProjectCreate):
    try:
        project = project.model_dump(mode="json")

        if project.get("start_date") >= project.get("end_date"):
            raise HTTPException(status_code=400, detail="Start date should be earlier than end date")

        data, count = supabase.table("project").insert({**project}).execute()
        print('='*120)
        print(data, count)
        return data[1][0]
    except Exception as e:
        print('='*120)
        print(e)
        raise HTTPException(status_code=400, detail=str(e))
    
def read_project(project_id: UUID4):
    try:
        data, count = supabase.table("project").select('*').eq("is_deleted", False).eq("id", project_id).execute()
        print('='*120)
        print(data, count)
        if not data[1]:
            raise HTTPException(status_code=400, detail="No data")
        return data[1][0]
    except Exception as e:
        print('='*120)
        print(e)
        raise HTTPException(status_code=400, detail=str(e))


def read_project_list(team_id: UUID4):
    try:
        data, count = supabase.table("project").select('*').eq("is_deleted", False).eq("team_id", team_id).execute()
        print('='*120)
        print(data, count)
        if not data[1]:
            raise HTTPException(status_code=400, detail="No data")
        return data[1]
    except Exception as e:
        print('='*120)
        print(e)
        raise HTTPException(status_code=400, detail=str(e))


def update_project(project: schemas.ProjectUpdate):
    try:
        project = project.model_dump(mode="json")

        if project.get("start_date") >= project.get("end_date"):
            raise HTTPException(status_code=400, detail="Start date should be earlier than end date")

        data, count = supabase.table("project").update(
            {**project}).eq("id", project["id"]).execute()
        print('='*120)
        print(data, count)
        if not data[1]:
            raise HTTPException(status_code=400, detail="No data")
        return data[1][0]
    except Exception as e:
        print('='*120)
        print(e)
        raise HTTPException(status_code=400, detail=str(e))
    
def flag_is_deleted_project(project_id: UUID4):
    try:
        data, count = supabase.table("project").update({"is_deleted": True}).eq("id", project_id).execute()
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
def delete_project(project_id: UUID4):
    try:
        data, count = supabase.table("project").delete().eq(
            "id", project_id).execute()
        print('='*120)
        print(data, count)
        if not data[1]:
            raise HTTPException(status_code=400, detail="No data")
        return data[1][0]
    except Exception as e:
        print('='*120)
        print(e)
        raise HTTPException(status_code=400, detail=str(e))
        
# # 검증 필요 로직 (삭제)
# def read_user_list_in_project(project_id: UUID4):
#     try:
#         data, count = supabase.table("UserProject").select('*').eq("project_id", project_id).execute()
#         print('='*120)
#         print(data, count)
#         return data[1]
#     except Exception as message:
#         return JSONResponse(status_code=400, content={"message": str(message)})

# def read_project_list_in_user(user_id: UUID4):
#     try:
#         data, count = supabase.table("UserProject").select('*').eq("user_id", user_id).execute()
#         print('='*120)
#         print(data, count)
#         return data[1]
#     except Exception as message:
#         return JSONResponse(status_code=400, content={"message": str(message)})
