from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from pydantic import UUID4
from uuid import UUID

from database.supabase import supabase
from func.auth.auth import verify_user
from cloud.azure.blob_storage import *
from env import DEFAULT_AZURE_CONTAINER_NAME

router = APIRouter(
    prefix="/settings",
    responses={404: {"description": "Not found"}},
)

# Temp
SIGNATURE_AZURE_CONTAINER_NAME = DEFAULT_AZURE_CONTAINER_NAME

ALLOWED_EXTENSIONS = {'png'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@router.get("/signature", tags=["settings"])
async def get_signature(req: Request):
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    # # testing user
    # user = UUID("6a423db5-8a34-4153-9795-c6f058020445", version=4)
    blob_name = str(user) + ".png"

    try:
        url = generate_presigned_url(
            blob_name, container_name=SIGNATURE_AZURE_CONTAINER_NAME)
        return JSONResponse(content={"status": "succeed", "url": url})
    except Exception as e:
        return JSONResponse(status_code=400, content={"status": "failed", "message": str(e)})


# # file upload 방식
# @router.post("/signature", tags=["settings"])
# async def add_signature(req: Request, file: UploadFile = File(...)):
#     # user: UUID4 = verify_user(req)
#     # if not user:
#     #     raise HTTPException(status_code=401, detail="Unauthorized")

#     # testing user
#     user = UUID("6a423db5-8a34-4153-9795-c6f058020445", version=4)

#     if not allowed_file(file.filename):
#         raise HTTPException(status_code=400, detail="Invalid file extension. Allowed extensions are png, jpg, jpeg")
#     data = await file.read()
#     blob_extention = file.filename.split(".")[-1]
#     blob_name = str(user) + "." + blob_extention
#     res = upload_blob(data, blob_name)
#     if res:
#         data, count = supabase.table("user_setting").update({"has_signature": True, "signature_type": blob_extention}).eq("id", user).execute()
#         if not data[1]:
#             raise HTTPException(status_code=500, detail="Internal Server Error")
#         return JSONResponse(content={
#             "status": "succeed",
#             "data": {
#                 "has_signature": data[1].get("has_signature"),
#                 "signature_type": data[1].get("signature_type")
#             }
#         })
#     else:
#         return JSONResponse(content={
#             "status": "failed",
#         })

@router.post("/signature", tags=["settings"])
# async def add_signature(req: Request, file: UploadFile = File(...)):
async def add_signature(req: Request, file: str):
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    # # testing user
    # user = UUID("6a423db5-8a34-4153-9795-c6f058020445", version=4)

    import base64
    from PIL import Image
    from io import BytesIO

    base64_string = file.replace("data:image/png;base64,", "")
    image_data = base64.b64decode(base64_string)
    res = upload_blob(BytesIO(image_data).getvalue(), f"{user}.png")

    if res:
        data, count = supabase.table("user_setting").update(
            {"has_signature": True}).eq("id", user).execute()
        if not data[1]:
            raise HTTPException(
                status_code=500, detail="Internal Server Error")
        return JSONResponse(content={
            "status": "succeed",
            "has_signature": data[1][0].get("has_signature"),
        })
    else:
        return JSONResponse(content={
            "status": "failed",
        })


@router.delete("/signature", tags=["settings"])
async def drop_signature(req: Request):
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    # # testing user
    # user = UUID("6a423db5-8a34-4153-9795-c6f058020445", version=4)

    data, count = supabase.table("user_setting").select(
        "has_signature").eq("id", user).execute()
    if not data[1]:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    blob_name = str(user) + ".png"
    res = delete_blob(blob_name)
    if res:
        data, count = supabase.table("user_setting").update(
            {"has_signature": False}).eq("id", user).execute()
        if not data[1]:
            raise HTTPException(
                status_code=500, detail="Internal Server Error")
        return JSONResponse(content={
            "status": "succeed",
            "has_signature": data[1][0].get("has_signature")
        })
    else:
        return JSONResponse(content={
            "status": "failed",
        })
