import os
from database.supabase import supabase
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status, Security, APIRouter, Request, Cookie
from fastapi.responses import JSONResponse
from typing import Annotated, List
from pydantic import BaseModel

from database import schemas


router = APIRouter(
    prefix="/admin",
    responses={404: {"description": "Not found"}},
)

