import json
from pydantic import UUID4
from fastapi import HTTPException

from database.supabase import supabase
from database import schemas


def get_user_team(user_id: UUID4):
    try:
        data, count = supabase.table(
            "user_setting").select("team_id").eq("id", user_id).execute()
        print('='*120)
        print(data, count)
        return data[1][0].get('team_id', None)
    except Exception as e:
        print('='*120)
        print(e)
        raise HTTPException(status_code=400, detail=str(e))


def get_team_user(team_id: UUID4):
    try:
        data, count = supabase.table(
            "user_setting").select("id").eq("team_id", team_id).execute()

        print('='*120)
        print(data, count)
        return data[1]
    except Exception as e:
        print('='*120)
        print(e)
        raise HTTPException(status_code=400, detail=str(e))
