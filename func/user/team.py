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
        if not data[1]:
            raise HTTPException(status_code=400, detail="User not found")
        return data[1][0].get('team_id', None)
    except Exception as e:
        print('='*120)
        print(e)
        raise HTTPException(status_code=400, detail=str(e))


def get_team_user(team_id: UUID4):
    try:
        data, count = supabase.table(
            "user_setting").select("id", "email", "first_name", "last_name").eq("team_id", team_id).execute()

        print('='*120)
        print(data, count)
        if not data[1]:
            raise HTTPException(status_code=400, detail="Team not found")
        return data[1]
    except Exception as e:
        print('='*120)
        print(e)
        raise HTTPException(status_code=400, detail=str(e))


def get_user_id_by_email(email: str):
    try:
        data, count = supabase.table(
            "user_setting").select("id").eq("email", email).execute()
        print('='*120)
        print(data, count)
        if not data[1]:
            raise HTTPException(status_code=400, detail="Email not found")
        return data[1][0].get('id', None)
    except Exception as e:
        print('='*120)
        print(e)
        raise HTTPException(status_code=400, detail=str(e))


def validate_user_in_team(user_id: UUID4, team_id: UUID4):
    try:
        data, count = supabase.table(
            "user_setting").select("team_id").eq("id", user_id).execute()
        print('='*120)
        print(data, count)
        if not data[1]:
            return False
        if data[1][0].get('team_id', None) != str(team_id):
            return False
        return True
    except Exception as e:
        print('='*120)
        print(e)
        raise HTTPException(status_code=400, detail=str(e))


def validate_user_free(user_id: UUID4):
    try:
        data, count = supabase.table(
            "user_setting").select("team_id").eq("id", user_id).execute()
        print('='*120)
        print(data, count)
        if not data[1]:
            return True
        if data[1][0].get('team_id', None):
            return False
        return True
    except Exception as e:
        print('='*120)
        print(e)
        raise HTTPException(status_code=400, detail=str(e))


def validate_user_is_leader(user_id: UUID4, team_id: UUID4):
    try:
        data, count = supabase.table(
            "team").select("team_leader_id").eq("is_deleted", False).eq("id", team_id).execute()
        print('='*120)
        print(data, count)
        if not data[1]:
            return False
        if data[1][0].get('team_leader_id', None) != str(user_id):
            return False
        return True
    except Exception as e:
        print('='*120)
        print(e)
        raise HTTPException(status_code=400, detail=str(e))


def validate_invite_accepted(invite_id: UUID4):
    try:
        data, count = supabase.table(
            "team_invite").select("is_accepted").eq("id", invite_id).execute()
        print('='*120)
        print(data, count)
        if not data[1]:
            return HTTPException(status_code=400, detail="Failed to get invite data")
        return data[1][0].get('is_accepted')
    except Exception as e:
        print('='*120)
        print(e)
        raise HTTPException(status_code=400, detail=str(e))
