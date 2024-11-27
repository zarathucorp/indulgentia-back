from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from pydantic import UUID4, BaseModel
from uuid import UUID

from database.supabase import supabase
from func.auth.auth import verify_user
from cloud.azure.blob_storage import *
from env import DEFAULT_AZURE_CONTAINER_NAME
from database import schemas
from func.error.error import raise_custom_error
from func.user.team import validate_user_is_leader_in_own_team

router = APIRouter(
    prefix="/settings",
    responses={404: {"description": "Not found"}},
)

# Temp
SIGNATURE_AZURE_CONTAINER_NAME = DEFAULT_AZURE_CONTAINER_NAME

ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif',
                      'svg', 'bmp', 'webp', 'tiff', 'jfif', 'pjpeg', 'pjp']

MAX_FILE_SIZE = 1024 * 1024  # 1MB


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# signature API
@router.get("/signature", tags=["settings"])
async def get_signature(req: Request):
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    # # testing user
    # user = UUID("6a423db5-8a34-4153-9795-c6f058020445", version=4)
    blob_name = str(user) + ".png"

    try:
        url = generate_presigned_url(
            blob_name, container_name=SIGNATURE_AZURE_CONTAINER_NAME)
        return JSONResponse(content={"status": "succeed", "url": url})
    except Exception as e:
        print(e)
        raise_custom_error(500, 312)
        # return JSONResponse(status_code=400, content={"status": "failed", "message": str(e)})


# file upload 방식
@router.post("/signature/file", tags=["settings"])
async def add_signature_file(req: Request, file: UploadFile = File(...)):
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)

    if not allowed_file(file.filename):
        raise_custom_error(422, 240)

    # 파일 용량 체크
    print("파일 사이즈 체크")
    print(file.size)
    if file.size and file.size > MAX_FILE_SIZE:
        raise_custom_error(422, 251)

    data = await file.read()
    blob_extention = file.filename.split(".")[-1]
    blob_name = str(user) + "." + blob_extention
    res = upload_blob(data, blob_name)
    if res:
        data, count = supabase.table("user_setting").update(
            {"has_signature": True}).eq("is_deleted", False).eq("id", user).execute()
        if not data[1]:
            raise_custom_error(500, 220)
        return JSONResponse(content={
            "status": "succeed",
            "has_signature": data[1][0].get("has_signature")
        })
    else:
        raise_custom_error(500, 311)


@router.post("/signature", tags=["settings"])
# async def add_signature(req: Request, file: UploadFile = File(...)):
async def add_signature(req: Request, signature: schemas.CreateSignature):
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)

    import base64
    from PIL import Image
    from io import BytesIO

    file = signature.file
    base64_string = file.replace("data:image/png;base64,", "")
    image_data = base64.b64decode(base64_string)
    res = upload_blob(BytesIO(image_data).getvalue(), f"{user}.png")

    if res:
        data, count = supabase.table("user_setting").update(
            {"has_signature": True}).eq("is_deleted", False).eq("id", user).execute()
        if not data[1]:
            raise_custom_error(500, 220)
        return JSONResponse(content={
            "status": "succeed",
            "has_signature": data[1][0].get("has_signature"),
        })
    else:
        raise_custom_error(500, 311)
        # return JSONResponse(content={
        #     "status": "failed",
        # })


@router.delete("/signature", tags=["settings"])
async def drop_signature(req: Request):
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)

    data, count = supabase.table("user_setting").select(
        "has_signature").eq("is_deleted", False).eq("id", user).execute()
    if not data[1]:
        raise_custom_error(500, 231)
    blob_name = str(user) + ".png"
    res = delete_blob(blob_name)
    if res:
        data, count = supabase.table("user_setting").update(
            {"has_signature": False}).eq("is_deleted", False).eq("id", user).execute()
        if not data[1]:
            raise_custom_error(500, 242)
        return JSONResponse(content={
            "status": "succeed",
            "has_signature": data[1][0].get("has_signature")
        })
    else:
        raise_custom_error(500, 313)
        # return JSONResponse(content={
        #     "status": "failed",
        # })


# user info API
@router.get("/info", tags=["settings"])
def get_user_info(req: Request):
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    data, count = supabase.table("user_setting").select(
        "id", "first_name", "last_name", "email", "is_admin").eq("is_deleted", False).eq("id", user).execute()
    if not data[1]:
        raise_custom_error(500, 231)
    is_leader = validate_user_is_leader_in_own_team(user)
    data[1][0]["is_leader"] = is_leader
    return JSONResponse(content={
        "status": "succeed",
        "data": data[1][0]
    })


@router.patch("/info", tags=["settings"])
async def update_user_info(req: Request, user_info: schemas.UserUpdate):
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    data, count = supabase.table("user_setting").update(
        {"first_name": user_info.first_name, "last_name": user_info.last_name}).eq("is_deleted", False).eq("id", user).execute()
    if not data[1]:
        raise_custom_error(500, 220)
    return JSONResponse(content={
        "status": "succeed",
        "data": data[1][0]
    })

# need to decide how to delete user info


@router.delete("/info", tags=["settings"])
async def drop_user_info(req: Request):
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    data, count = supabase.table(
        "user_setting").delete().eq("id", user).execute()
    if not data[1]:
        raise_custom_error(500, 242)
    return JSONResponse(content={
        "status": "succeed",
        "data": data[1][0]
    })


@router.get("/github/token", tags=["settings"])
def get_github_token(req: Request):
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    data, count = supabase.table("user_setting").select(
        "github_token").eq("is_deleted", False).eq("id", user).execute()
    if not data[1]:
        raise_custom_error(500, 231)
    return JSONResponse(content={
        "status": "succeed",
        "data": data[1][0]
    })


class AddGithubToken(BaseModel):
    token: str


@router.patch("/github/token", tags=["settings"])
def change_github_token(req: Request, body: AddGithubToken):
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    data, count = supabase.table("user_setting").update(
        {"github_token": body.token}).eq("id", user).execute()
    if not data[1]:
        raise_custom_error(500, 220)
    return JSONResponse(content={
        "status": "succeed",
        "data": data[1][0]
    })


@router.delete("/github/token", tags=["settings"])
def drop_github_token(req: Request):
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    data, count = supabase.table("user_setting").update(
        {"github_token": None}).eq("is_deleted", False).eq("id", user).execute()
    if not data[1]:
        raise_custom_error(500, 242)
    return JSONResponse(content={
        "status": "succeed",
        "data": data[1][0]
    })
