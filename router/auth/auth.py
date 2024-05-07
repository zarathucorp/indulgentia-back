import os
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status, Security, APIRouter, Request, Cookie
from fastapi.responses import JSONResponse
from typing import Annotated, List
from pydantic import BaseModel
import jwt

from database import schemas, crud



router = APIRouter(
    prefix="/auth",
    responses={404: {"description": "Not found"}},
)


@router.get("/join")
def join(request: Request):
    # NewUser = schemas.UserCreate(
    #     email="foo@bar.com",
    #     password="foobar",
    # )
    NewUser = schemas.UserCreate(
        email="koolerjaebee@gmail.com",
        password="1q2w3e$r",
    )

    res = crud.create_user(NewUser)
    return res


@router.get("/login")
def login():
    pass


@router.get("/logout")
def logout():
    pass


@router.get("/drop")
def drop():
    pass
