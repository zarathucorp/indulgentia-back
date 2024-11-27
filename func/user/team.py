import json
from pydantic import UUID4
from fastapi import HTTPException
from datetime import datetime

from database.supabase import supabase
from database import schemas
from func.error.error import raise_custom_error


def get_user_team(user_id: UUID4):
    try:
        data, count = supabase.table(
            "user_setting").select("team_id").eq("is_deleted", False).eq("id", user_id).execute()
        if not data[1]:
            raise_custom_error(500, 231)
        return data[1][0].get('team_id', None)
    except Exception as e:
        print(e)
        raise_custom_error(500, 230)


def get_team_user(team_id: UUID4):
    try:
        data, count = supabase.table(
            "user_setting").select("id", "email", "first_name", "last_name").eq("is_deleted", False).eq("team_id", team_id).execute()
        if not data[1]:
            raise_custom_error(500, 232)
        return data[1]
    except Exception as e:
        print(e)
        raise_custom_error(500, 230)


def get_user_id_by_email(email: str):
    try:
        data, count = supabase.table(
            "user_setting").select("id").eq("is_deleted", False).eq("email", email).execute()
        if not data[1]:
            raise_custom_error(500, 231)
        return data[1][0].get('id', None)
    except Exception as e:
        print(e)
        raise_custom_error(500, 230)


def validate_user_in_team(user_id: UUID4, team_id: UUID4):
    try:
        data, count = supabase.table(
            "user_setting").select("team_id").eq("is_deleted", False).eq("id", user_id).execute()
        if not data[1]:
            return False
        if data[1][0].get('team_id', None) != str(team_id):
            return False
        return True
    except Exception as e:
        print(e)
        raise_custom_error(500, 230)
        raise HTTPException(status_code=400, detail=str(e))


def validate_user_free(user_id: UUID4):
    try:
        data, count = supabase.table(
            "user_setting").select("team_id").eq("is_deleted", False).eq("id", user_id).execute()
        if not data[1]:
            return True
        if data[1][0].get('team_id', None):
            return False
        return True
    except Exception as e:
        print(e)
        raise_custom_error(500, 230)


def validate_user_is_leader(user_id: UUID4, team_id: UUID4):
    try:
        data, count = supabase.table(
            "team").select("team_leader_id").eq("is_deleted", False).eq("id", team_id).execute()
        if not data[1]:
            print(data[1])
            return False
        if data[1][0].get('team_leader_id', None) != str(user_id):
            return False
        return True
    except Exception as e:
        print(e)
        raise_custom_error(500, 230)


def validate_invite_accepted(invite_id: UUID4):
    try:
        data, count = supabase.table(
            "team_invite").select("is_accepted").eq("is_deleted", False).eq("id", invite_id).execute()
        if not data[1]:
            raise_custom_error(500, 231)
        return data[1][0].get('is_accepted')
    except Exception as e:
        print(e)
        raise_custom_error(500, 230)


def validate_exceed_max_members(team_id: UUID4):
    try:
        datetime_now = datetime.now()
        data, count = supabase.table(
            "subscription").select("max_members").eq("team_id", team_id).eq("is_active", True).lte("started_at", datetime_now).gte("expired_at", datetime_now).execute()
        if not data[1]:
            return True
        team_max_members = data[1][0].get('max_members', None)
        team_user_count = len(get_team_user(team_id))
        return team_user_count >= team_max_members
    except Exception as e:
        print(e)
        raise_custom_error(500, 230)


def validate_user_in_premium_team(user_id: UUID4):
    team_id = get_user_team(user_id)
    if not team_id:
        raise_custom_error(401, 540)
    try:
        datetime_now = datetime.now()
        data, count = supabase.table(
            "subscription").select("*").eq("team_id", team_id).eq("is_active", True).lte("started_at", datetime_now).gte("expired_at", datetime_now).execute()
        print(data)
        return not not data[1]
    except Exception as e:
        print(e)
        raise_custom_error(500, 230)


def validate_user_is_leader_in_own_team(user_id: UUID4):
    team_id = get_user_team(user_id)
    if not team_id:
        raise_custom_error(401, 540)
    return validate_user_is_leader(user_id, team_id)
