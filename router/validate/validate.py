# PDF 진본 검증 모듈
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
import hashlib

router = APIRouter(
    prefix="/validate",
    responses={404: {"description": "Not found"}},
)


@router.post("/pdf", tags=["features"])
async def validate_pdf(file: UploadFile = File(...)):
    contents = await file.read()
    hash_object = hashlib.sha256(contents)
    hex_dig = hash_object.hexdigest()
    return {"hash": hex_dig}
