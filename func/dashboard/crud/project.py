import json
from pydantic import UUID4
from fastapi import HTTPException

from database.supabase import supabase
from database import schemas
from func.error.error import raise_custom_error


def create_project(project: schemas.ProjectCreate):
    try:
        project = project.model_dump(mode="json")

        if (project.get("start_date") is not None and project.get("end_date") is not None) and (project.get("start_date") >= project.get("end_date")):
            raise_custom_error(422, 231)

        data, count = supabase.table("project").insert({**project}).execute()
        if not data[1]:
            raise_custom_error(500, 210)
        return data[1][0]
    except Exception as e:
        print(e)
        raise_custom_error(500, 210)


def read_project(project_id: UUID4):
    try:
        data, count = supabase.table("project").select(
            '*').eq("is_deleted", False).eq("id", project_id).execute()
        if not data[1]:
            raise_custom_error(500, 231)
        return data[1][0]
    except Exception as e:
        print(e)
        raise_custom_error(500, 230)


def read_project_list(team_id: UUID4):
    try:
        data, count = supabase.table("project").select(
            '*').eq("is_deleted", False).eq("team_id", team_id).order("created_at", desc=True).execute()
        return data[1]
    except Exception as e:
        print(e)
        raise_custom_error(500, 230)


def update_project(project: schemas.ProjectUpdate):
    try:
        project = project.model_dump(mode="json")

        if (project.get("start_date") is not None and project.get("end_date") is not None) and (project.get("start_date") >= project.get("end_date")):
            raise_custom_error(422, 231)

        data, count = supabase.table("project").update(
            {**project}).eq("is_deleted", False).eq("id", project["id"]).execute()
        if not data[1]:
            raise_custom_error(500, 220)
        return data[1][0]
    except Exception as e:
        print(e)
        raise_custom_error(500, 220)
        raise HTTPException(status_code=400, detail=str(e))


def flag_is_deleted_project(project_id: UUID4):
    try:
        data, count = supabase.table("project").update(
            {"is_deleted": True}).eq("id", project_id).execute()
        if not data[1]:
            raise_custom_error(500, 242)
        return data[1][0]
    except Exception as e:
        print(e)
        raise_custom_error(500, 240)

# Old version


def delete_project(project_id: UUID4):
    try:
        data, count = supabase.table("project").delete().eq(
            "id", project_id).execute()
        print(data, count)
        if not data[1]:
            raise_custom_error(500, 241)
        return data[1][0]
    except Exception as e:
        print(e)
        raise_custom_error(500, 240)

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
