from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import UUID4
from func.auth.auth import verify_user
router = APIRouter(
    prefix="/note",
    responses={404: {"description": "Not found"}},
)


@router.get("/list")
async def note_list(req: Request, bucket_uuid: UUID4):
    # print(req.cookies)
    # print(bucket_uuid)

    return {"status": "succeed", "bucket_uuid": bucket_uuid, "user_uuid": verify_user(req)}
