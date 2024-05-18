
from fastapi import APIRouter, Depends, HTTPException, Request
from . import project
from . import bucket
from . import note
router = APIRouter(
    prefix="/dashboard",
    responses={404: {"description": "Not found"}},
)

router.include_router(project.router)
router.include_router(bucket.router)
router.include_router(note.router)


@router.get("/breadcrumb/note/{note_id}")
async def get_breadcrumb(req: Request, note_id: str):
    from pydantic import UUID4
    from func.auth.auth import verify_user
    from database.supabase import supabase
    from fastapi.responses import JSONResponse
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    data, count = supabase.rpc(
        "note_breadcrumb_data", {"note_id": note_id}).execute()
    if not data[1]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return JSONResponse(content={
        "status": "succeed",
        "data": data[1][0]
    })


@router.get("/breadcrumb/bucket/{bucket_id}")
async def get_breadcrumb(req: Request, bucket_id: str):
    from pydantic import UUID4
    from func.auth.auth import verify_user
    from database.supabase import supabase
    from fastapi.responses import JSONResponse
    user: UUID4 = verify_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    data, count = supabase.rpc(
        "bucket_breadcrumb_data", {"bucket_id": bucket_id}).execute()
    if not data[1]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return JSONResponse(content={
        "status": "succeed",
        "data": data[1][0]
    })
