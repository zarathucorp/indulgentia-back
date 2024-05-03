import os
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status, Security, APIRouter, Request, Cookie
from fastapi.responses import JSONResponse
from typing import Annotated, List
from pydantic import BaseModel
from dotenv import load_dotenv
import jwt

from database import supabase, schemas, crud

load_dotenv()

router = APIRouter(
    prefix="/auth",
    responses={404: {"description": "Not found"}},
)
