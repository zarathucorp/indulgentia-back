import json
from pydantic import UUID4
from postgrest.exceptions import APIError

from database.supabase import supabase
from database import schemas


def create_project(project: schemas.ProjectCreate):
    try:
        project = project.model_dump(mode="json")

        if project.get("start_date") >= project.get("end_date"):
            return {
                "status_code": 400,
                "content": None,
                "message": "Start date should be earlier than end date"
            }

        data, count = supabase.table("project").insert({**project}).execute()
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
    
def read_project(project_id: UUID4):
    try:
        data, count = supabase.table("project").select('*').eq("id", project_id).execute()
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

def read_project_list(team_id: UUID4):
    try:
        data, count = supabase.table("project").select('*').eq("team_id", team_id).execute()
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

def update_project(project: schemas.ProjectUpdate):
    try:
        project = project.model_dump(mode="json")

        if project.get("start_date") >= project.get("end_date"):
            return {
                "status_code": 400,
                "content": None,
                "message": "Start date should be earlier than end date"
            }

        data, count = supabase.table("project").update({**project}).eq("id", project["id"]).execute()
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

def delete_project(project_id: UUID4):
    try:
        data, count = supabase.table("project").delete().eq("id", project_id).execute()
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
