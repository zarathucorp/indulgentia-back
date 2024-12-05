from fastapi import APIRouter, Depends, HTTPException, Request, File, UploadFile, Form, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from pydantic import UUID4
from typing import Optional, List, Union, Annotated, Literal
import os
import uuid
import hashlib
from pdfmerge import pdfmerge
from datetime import datetime
from pytz import timezone
from urllib.parse import quote

from cloud.azure.blob_storage import *
from database import schemas
from func.dashboard.crud.note import *
from func.auth.auth import *
from func.dashboard.pdf_generator.pdf_generator import generate_pdf, generate_pdf_using_markdown, generate_preview_pdf
from func.note_handling.pdf_sign import sign_pdf
from func.note_handling.pdf_verify import verify_pdf
from cloud.azure.confidential_lendger import write_ledger, read_ledger, get_ledger_receipt
from func.error.error import raise_custom_error
from func.user.team import validate_user_in_premium_team
from func.github.fetch import fetch_github_data
from func.note_handling.note_export import process_note_ids, delete_files
from func.user.team import validate_user_is_leader_in_own_team


router = APIRouter(
    prefix="/note",
    responses={404: {"description": "Not found"}},
)


# read list


@router.get("/list/{bucket_id}", tags=["note"])
async def get_note_list(req: Request, bucket_id: str):
    try:
        uuid.UUID(bucket_id)
    except ValueError:
        raise_custom_error(422, 210)
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    data, count = supabase.rpc(
        "verify_bucket", {"user_id": str(user), "bucket_id": bucket_id}).execute()
    if not data[1]:
        raise_custom_error(401, 310)
    res = read_note_list(bucket_id)
    if not validate_user_in_premium_team(user):
        raise_custom_error(401, 820)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })

# read


@router.get("/{note_id}", tags=["note"])
async def get_note(req: Request, note_id: str):
    try:
        uuid.UUID(note_id)
    except ValueError:
        raise_custom_error(422, 210)
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    # print(user)
    # data, count = supabase.rpc(
    #     "verify_note", {"user_id": user, "note_id": note_id}).execute()
    data, count = supabase.rpc(
        "verify_note", {"p_user_id": user, "p_note_id": note_id}).execute()
    if not data[1]:
        raise_custom_error(401, 410)
    res = read_note_detail(note_id)
    if not validate_user_in_premium_team(user):
        raise_custom_error(401, 820)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })


# note preview
@router.post("", include_in_schema=False)
@router.post("/", tags=["note"])
# file: Optional[UploadFile] = File(None)
async def get_note_preview(req: Request,
                           background_tasks: BackgroundTasks,
                           bucket_id: UUID4 = Form(...),
                           title: str = Form(...),
                           file_name: str = Form(...),
                           is_github: bool = Form(...),
                           files: List[Union[UploadFile, None]] = File(None),
                           description: Optional[str] = Form(None),
                           ):
    # description 유효성 검사
    if description:
        # \r 문자를 제거하고 빈 문자열을 필터링
        description_lines = list(
            filter(None, description.replace("\r", "").split("\n")))
        print(description_lines)
        if len(description) > 1000 or len(description_lines) > 20:
            print("description length :", len(description))
            print("description line count :", description.count("\n"))
            raise_custom_error(422, 250)

    user: UUID4 = verify_user(req)
    note_id = uuid.uuid4()
    if not user:
        raise_custom_error(403, 213)
    if not validate_user_in_premium_team(user):
        raise_custom_error(401, 820)
    verify_bucket_data, count = supabase.rpc(
        "verify_bucket", {"user_id": str(user), "bucket_id": str(bucket_id)}).execute()
    if not verify_bucket_data[1]:
        raise_custom_error(401, 310)
    user_data, count = supabase.table("user_setting").select("first_name", "last_name").eq("is_deleted", False).eq(
        "id", user).execute()
    first_name = user_data[1][0].get("first_name")
    last_name = user_data[1][0].get("last_name")
    if not first_name and not last_name:
        raise_custom_error(401, 121)
    username = last_name + " " + first_name
    try:
        contents = []
        if files:
            for file in files:
                contents.append(await file.read())
    except Exception as e:
        print(e)
        raise_custom_error(500, 120)
    user_signature_data, count = supabase.table("user_setting").select(
        "has_signature").eq("is_deleted", False).eq("id", user).execute()
    has_signature = user_signature_data[1][0].get("has_signature")
    if has_signature:
        url = generate_presigned_url(str(user) + ".png")
    else:
        url = None
    breadcrumb_data, count = supabase.rpc(
        "bucket_breadcrumb_data", {"bucket_id": str(bucket_id)}).execute()
    if not breadcrumb_data[1]:
        raise_custom_error(500, 250)
    pdf_res = await generate_pdf(title=title, username=username,
                                 note_id=str(note_id), description=description, files=files, contents=contents, project_title=breadcrumb_data[1][0].get("project_title"), bucket_title=breadcrumb_data[1][0].get("bucket_title"), signature_url=url)

    # pdf_preview = f"func/dashboard/pdf_generator/output/{note_id}_preview.pdf"
    pdf_preview = await generate_preview_pdf(pdf_res)

    # 작업 후 파일 삭제
    background_tasks.add_task(delete_files, [pdf_preview])

    return FileResponse(pdf_preview, media_type="application/pdf", filename=f"{note_id}_preview.pdf", headers={
        "x-note-id": str(note_id)
    })


# create accept


# @router.post("", include_in_schema=False)
@router.post("/{note_id}/accept", tags=["note"])
async def add_note(req: Request,
                   note_id: str,
                   bucket_id: UUID4 = Form(...),
                   title: str = Form(...),
                   file_name: str = Form(...),
                   is_github: bool = Form(...),
                   description: Optional[str] = Form(None)
                   ):
    try:
        uuid.UUID(note_id)
    except ValueError:
        raise_custom_error(422, 210)
    # description 유효성 검사
    if description:
        # \r 문자를 제거하고 빈 문자열을 필터링
        description_lines = list(
            filter(None, description.replace("\r", "").split("\n")))
        print(description_lines)
        if len(description) > 1000 or len(description_lines) > 20:
            print("description length :", len(description))
            print("description line count :", description.count("\n"))
            raise_custom_error(422, 250)
    verify_note, count = supabase.table(
        "note").select("*").eq("id", note_id).execute()
    # 이미 존재하는 노트
    if verify_note[1]:
        raise_custom_error(500, 233)

    user: UUID4 = verify_user(req)
    # note_id = uuid.uuid4()
    if not user:
        raise_custom_error(403, 213)
    if not validate_user_in_premium_team(user):
        raise_custom_error(401, 820)
    verify_bucket_data, count = supabase.rpc(
        "verify_bucket", {"user_id": str(user), "bucket_id": str(bucket_id)}).execute()
    if not verify_bucket_data[1]:
        raise_custom_error(401, 310)

    SOURCE_PATH = "func/dashboard/pdf_generator"
    pdf_res = f"{SOURCE_PATH}/output/{note_id}"
    await sign_pdf(pdf_res)
    signed_pdf_res = f"func/dashboard/pdf_generator/output/{note_id}_signed.pdf"
    # # 테스트
    # raise Exception("test")
    try:
        # upload pdf
        with open(signed_pdf_res, "rb") as f:
            pdf_data = f.read()
    except Exception as e:
        print(e)
        # delete result pdf
        if os.path.isfile(f"{SOURCE_PATH}/output/{note_id}.pdf"):
            os.unlink(f"{SOURCE_PATH}/output/{note_id}.pdf")
            print(f"{SOURCE_PATH}/output/{note_id}.pdf deleted")
        raise_custom_error(500, 120)
    upload_blob(pdf_data, str(note_id) + ".pdf")
    pdf_hash = hashlib.sha256(pdf_data).hexdigest()
    ledger_result = write_ledger(
        {"id": str(note_id), "hash": pdf_hash})
    transaction_id = ledger_result.get("transactionId")
    try:
        # delete result pdf
        os.unlink(f"{SOURCE_PATH}/output/{note_id}.pdf")
        print(f"{SOURCE_PATH}/output/{note_id}.pdf deleted")
        os.unlink(f"{SOURCE_PATH}/output/{note_id}_signed.pdf")
        print(f"{SOURCE_PATH}/output/{note_id}_signed.pdf deleted")
    except Exception as e:
        print(e)
        raise_custom_error(500, 130)

    note = schemas.NoteCreate(
        id=uuid.UUID(note_id),
        bucket_id=bucket_id,
        user_id=user,
        title=title,
        timestamp_transaction_id=transaction_id,
        file_name=file_name,
        is_github=is_github,
        pdf_hash=pdf_hash
    )
    res = create_note(note)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })

# create reject


@router.post("/{note_id}/reject", tags=["note"])
async def reject_note(req: Request,
                      note_id: str,
                      bucket_id: UUID4 = Form(...),
                      title: str = Form(...),
                      file_name: str = Form(...),
                      is_github: bool = Form(...),
                      description: Optional[str] = Form(None)
                      ):
    try:
        uuid.UUID(note_id)
    except ValueError:
        raise_custom_error(422, 210)
    verify_note, count = supabase.table(
        "note").select("*").eq("id", note_id).execute()
    # 이미 존재하는 노트
    if verify_note[1]:
        raise_custom_error(500, 233)

    try:
        # delete result pdf
        SOURCE_PATH = "func/dashboard/pdf_generator"
        os.unlink(f"{SOURCE_PATH}/output/{note_id}.pdf")
        print(f"{SOURCE_PATH}/output/{note_id}.pdf deleted")
    except Exception as e:
        print(e)
        raise_custom_error(500, 130)

    return JSONResponse(content={
        "status": "succeed",
        "data": {
            "message": "Note creation rejected"
        }
    })

# 노트 수정 불가
# # update


# @ router.put("/{note_id}", tags=["note"])
# async def change_note(req: Request, note: schemas.NoteUpdate):
#     user: UUID4 = verify_user(req)
#     if not user:
#         raise_custom_error(403, 213)
#     if not validate_user_in_premium_team(user):
#         raise_custom_error(401, 820)
#     if not user == note.user_id:
#         raise_custom_error(401, 420)

#     # need verify timestamp logic

#     res = update_note(note)
#     return JSONResponse(content={
#         "status": "succeed",
#         "data": res
#     })

# delete


@ router.delete("/{note_id}", tags=["note"])
async def drop_note(req: Request, note_id: str):
    try:
        uuid.UUID(note_id)
    except ValueError:
        raise_custom_error(422, 210)
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    # if not validate_user_in_premium_team(user):
    #     raise_custom_error(401, 820)

    # 팀 리더인지 확인
    if not validate_user_is_leader_in_own_team(user):
        raise_custom_error(401, 520)

    data, count = supabase.table("note").select(
        "user_id").eq("id", note_id).execute()
    if not data[1]:
        raise_custom_error(500, 242)
    if not user == data[1][0]["user_id"]:
        raise_custom_error(401, 420)
    res = flag_is_deleted_note(note_id)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })

""" Old version
@router.delete("/{note_id}", tags=["note"])
async def drop_note(req: Request, note_id: str):
    user: UUID4 = verify_user(req)
    # if not user:
    #     raise HTTPException(status_code=401, detail="Unauthorized")
    data, count = supabase.table("note").select(
        "user_id").eq("id", note_id).execute()
    if not data[1]:
        raise HTTPException(status_code=400, detail="No data")
    if not user == data[1][0]["user_id"]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    res = delete_note(note_id)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })
"""


@ router.get("/file/{note_id}", tags=["note"])
async def get_note_file(req: Request, note_id: str):
    # Auth 먼저 해야함
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    if not validate_user_in_premium_team(user):
        raise_custom_error(401, 820)
    # generate_presigned_url 오류 시 500 에러 발생
    try:
        url = generate_presigned_url(note_id + ".pdf")
        return JSONResponse(content={"status": "succeed", "url": url})
    except Exception as e:
        print(e)
        raise_custom_error(500, 312)
        # return JSONResponse(status_code=400, content={"status": "failed", "message": str(e)})


class DonwloadNoteInfo(BaseModel):
    note_ids: List[str]
    is_merged_required: Optional[bool] = False
    is_filename_id: Optional[bool] = False


# pdf multiple download
@router.post("/file", tags=["note"])
async def get_note_files(req: Request, download_note_info: DonwloadNoteInfo, background_tasks: BackgroundTasks):
    user: UUID4 = verify_user(req)
    note_ids = download_note_info.note_ids
    is_merged_required = download_note_info.is_merged_required
    is_filename_id = download_note_info.is_filename_id
    if not user:
        raise_custom_error(403, 213)
    if not validate_user_in_premium_team(user):
        raise_custom_error(401, 820)
    for note_id in note_ids:
        try:
            uuid.UUID(note_id)
        except ValueError:
            raise_custom_error(422, 210)

    # 노트 작업
    output_file, media_type, filename, files_to_delete = process_note_ids(
        note_ids, is_merged_required, is_filename_id)

    # 작업 후 파일 삭제
    background_tasks.add_task(delete_files, files_to_delete)

    return FileResponse(output_file, media_type=media_type, filename=filename)


@ router.get("/{note_id}/breadcrumb", tags=["note"])
async def get_breadcrumb(req: Request, note_id: str):
    try:
        uuid.UUID(note_id)
    except ValueError:
        raise_custom_error(422, 210)
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    if not validate_user_in_premium_team(user):
        raise_custom_error(401, 820)
    data, count = supabase.rpc(
        "note_breadcrumb_data", {"note_id": note_id}).execute()
    if not data[1]:
        raise_custom_error(500, 250)
    return JSONResponse(content={
        "status": "succeed",
        "data": data[1][0]
    })


# @ router.get("/{note_id}/timestamp", tags=["note"])
# def get_note_timestamp(req: Request, note_id: str):
#     try:
#         uuid.UUID(note_id)
#     except ValueError:
#         raise_custom_error(422, 210)
#     user: UUID4 = verify_user(req)
#     if not user:
#         raise_custom_error(403, 213)
#     data, count = supabase.table("note").select(
#         "timestamp_transaction_id").eq("id", note_id).execute()
#     if not data[1]:
#         raise_custom_error(500, 231)
#     transaction_id = data[1][0].get("timestamp_transaction_id")
#     entry = read_ledger(transaction_id)

#     return JSONResponse(content={
#         "status": "succeed",
#         "data": entry
#     })


class RepositoryInfo(BaseModel):
    owner: str  # username
    name: str  # repository name
    url: str
    full_name: str  # owner/name == full_name 입니다.


class GithubMarkdownRequest(BaseModel):
    markdownContent: str
    # eventType: Literal["Commit", "PR", "Issue"]
    eventType: Literal["Commit", "PR", "Issue"]
    repositoryInfo: RepositoryInfo


@ router.post("/github", tags=["note"])
async def add_github_note(req: Request, GithubMarkdownRequest: GithubMarkdownRequest):
    # user: UUID4 = verify_user(req)
    # if not user:
    #     raise_custom_error(403, 213)
    data, count = supabase.table("gitrepo").select("*").ilike("git_username", GithubMarkdownRequest.repositoryInfo.owner).ilike(
        "git_repository", GithubMarkdownRequest.repositoryInfo.name).eq("is_deleted", False).execute()
    if not data[1]:
        raise_custom_error(500, 232)
    # # 테스트 data
    # data = None, [{"bucket_id": "b1", "user_id": "u1"}]
    res_list = []
    for idx, row in enumerate(data[1]):
        note_id = uuid.uuid4()
        note_id_string = str(note_id)
        user_id = row.get("user_id")
        if not validate_user_in_premium_team(user_id):
            raise_custom_error(401, 820)
        user_data, count = supabase.table("user_setting").select(
            "*").eq("is_deleted", False).eq("id", user_id).execute()
        # # 테스트 user_data
        # user_data = None, [{"id": "u1", "has_signature": False,
        #                     "first_name": "first", "last_name": "last"}]
        has_signature = user_data[1][0].get("has_signature")
        if has_signature:
            url = generate_presigned_url(
                str(user_data[1][0].get("id")) + ".png")
        else:
            url = None
        first_name = user_data[1][0].get("first_name")
        last_name = user_data[1][0].get("last_name")
        if not first_name and not last_name:
            raise_custom_error(401, 121)
        else:
            username = last_name + " " + first_name

        breadcrumb_data, count = supabase.rpc(
            "bucket_breadcrumb_data", {"bucket_id": row.get("bucket_id")}).execute()
        if not breadcrumb_data[1]:
            raise_custom_error(500, 250)
        # # 테스트 breadcrumb_data
        # breadcrumb_data = None, [
        #     {"project_title": "project", "bucket_title": "bucket"}]

        pdf_res = await generate_pdf_using_markdown(note_id=note_id_string, markdown_content=GithubMarkdownRequest.markdownContent, project_title=breadcrumb_data[1][0].get("project_title"), bucket_title=breadcrumb_data[1][0].get("bucket_title"), author=username, signature_url=url)
        await sign_pdf(pdf_res)
        signed_pdf_res = f"func/dashboard/pdf_generator/output/{note_id_string}_signed.pdf"
        SOURCE_PATH = "func/dashboard/pdf_generator"
        # # 테스트 Response
        # return JSONResponse(content={
        #     "status": "succeed",
        #     "data": res_list
        # })
        try:
            # upload pdf
            with open(signed_pdf_res, "rb") as f:
                pdf_data = f.read()
        except Exception as e:
            print(e)
            # delete result pdf
            if os.path.isfile(f"{SOURCE_PATH}/output/{note_id_string}.pdf"):
                os.unlink(f"{SOURCE_PATH}/output/{note_id_string}.pdf")
                print(f"{SOURCE_PATH}/output/{note_id_string}.pdf deleted")
            raise_custom_error(500, 120)
        # raise Exception("test")
        upload_blob(pdf_data, note_id_string + ".pdf")
        pdf_hash = hashlib.sha256(pdf_data).hexdigest()
        ledger_result = write_ledger(
            {"id": note_id_string, "hash": pdf_hash})
        try:
            os.unlink(f"{SOURCE_PATH}/output/{note_id_string}.pdf")
            print(f"{SOURCE_PATH}/output/{note_id_string}.pdf deleted")
            os.unlink(f"{SOURCE_PATH}/output/{note_id_string}_signed.pdf")
            print(f"{SOURCE_PATH}/output/{note_id_string}_signed.pdf deleted")
        except Exception as e:
            print(e)
            raise_custom_error(500, 130)

        transaction_id = ledger_result.get("transactionId")
        current_time = datetime.now(
            timezone('Asia/Seoul')).strftime("%Y-%m-%d %H:%M:%S")
        note = schemas.NoteCreate(
            id=note_id,
            bucket_id=uuid.UUID(row.get("bucket_id")),
            user_id=uuid.UUID(row.get("user_id")),
            title=f"{current_time}에 생성된 {GithubMarkdownRequest.eventType} 노트(Github)",
            timestamp_transaction_id=transaction_id,
            file_name=f"{current_time}에 생성된 {GithubMarkdownRequest.eventType} 노트(Github)",
            is_github=True,
            github_type=GithubMarkdownRequest.eventType,
            github_link=GithubMarkdownRequest.repositoryInfo.url,
            pdf_hash=pdf_hash
        )
        res = create_note(note)
        res_list.append(res)
    return JSONResponse(content={
        "status": "succeed",
        "data": res_list
    })


@router.post("/verify", tags=["note"])
def verify_note_pdf(req: Request, file: UploadFile = File()):
    if not file or not file.content_type == "application/pdf":
        raise_custom_error(422, 240)
    file_contents = file.file.read()
    try:
        pyhanko_verify_res = verify_pdf(file_contents)
    except IndexError:
        return JSONResponse(content={
            "status": "succeed",
            "data": {"is_verified": False, "message": "PDF is not signed by Rndsillog", "entry": None, "receipt": None}
        })
    file_hash = hashlib.sha256(file_contents).hexdigest()
    print(file_hash)
    note_data, count = supabase.table("note").select(
        "*").eq("is_deleted", False).eq("pdf_hash", file_hash).execute()
    if len(note_data[1]) > 1:
        raise_custom_error(500, 231)
    hash_exist_verify_res = not not note_data[1]
    if hash_exist_verify_res:
        transaction_id = note_data[1][0].get("timestamp_transaction_id")
        entry = read_ledger(transaction_id)["entry"]
        ledger_contents = json.loads(entry.get("contents"))
        entry["contents"] = ledger_contents
        hash_equal_verify_res = file_hash == ledger_contents.get("hash")
        receipt = get_ledger_receipt(transaction_id).get("receipt")
    else:
        entry = None
        receipt = None
        hash_equal_verify_res = False

    if not pyhanko_verify_res:
        verify_res = False
        message = "PDF is modified"
    elif not hash_exist_verify_res:
        verify_res = False
        message = "PDF does not exist in database"
    elif not hash_equal_verify_res:
        verify_res = False
        message = "PDF is different from the one in database"
    else:
        verify_res = True
        message = "PDF is verified"
    return JSONResponse(content={
        "status": "succeed",
        "data": {"is_verified": verify_res, "message": message, "entry": entry, "receipt": receipt}
    })


@ router.post("/verify/{note_id}", tags=["note"])
def verify_note_pdf_with_note_id(req: Request, note_id: str, file: UploadFile = File()):
    try:
        uuid.UUID(note_id)
    except ValueError:
        raise_custom_error(422, 210)
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    if not validate_user_in_premium_team(user):
        raise_custom_error(401, 820)
    if not file or not file.content_type == "application/pdf":
        raise_custom_error(422, 240)
    file_hash = hashlib.sha256(file.file.read()).hexdigest()

    data, count = supabase.table("note").select(
        "timestamp_transaction_id").eq("id", note_id).execute()
    if not data[1]:
        raise_custom_error(500, 231)
    transaction_id = data[1][0].get("timestamp_transaction_id")
    entry = read_ledger(transaction_id)["entry"]
    ledger_contents = json.loads(entry.get("contents"))
    entry["contents"] = ledger_contents
    receipt = get_ledger_receipt(transaction_id).get("receipt")

    veify_res = file_hash == ledger_contents.get("hash")
    if veify_res:
        message = "PDF is verified"
    else:
        message = "PDF is different from the one in database"

    return JSONResponse(content={
        "status": "succeed",
        "data": {"is_verified": veify_res, "message": message, "entry": entry, "receipt": receipt}
    })


@ router.post("/github/{bucket_id}", tags=["note"])
async def add_github_note_all_in_bucket(req: Request, repository_info: RepositoryInfo, bucket_id: str):
    try:
        bucket_id = uuid.UUID(bucket_id)
    except ValueError:
        raise_custom_error(422, 210)
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    data, count = supabase.table("gitrepo").select("*").ilike("git_username", repository_info.owner).ilike(
        "git_repository", repository_info.name).eq("is_deleted", False).eq("bucket_id", bucket_id).execute()
    if not data[1]:
        raise_custom_error(500, 232)
    user_data, count = supabase.table("user_setting").select("github_token").eq(
        "is_deleted", False).eq("id", user).execute()
    if not user_data[1]:
        raise_custom_error(500, 231)

    commit_responses = fetch_github_data(user_data[1][0].get(
        "github_token"), repository_info.owner, repository_info.name, "commits")
    issue_responses = fetch_github_data(user_data[1][0].get(
        "github_token"), repository_info.owner, repository_info.name, "issues")
    pr_responses = fetch_github_data(user_data[1][0].get(
        "github_token"), repository_info.owner, repository_info.name, "pulls")
    commit_markdown = "# Commit Details\n\n"
    issue_markdown = ""
    issue_action = {
        "open": "Issue opened",
        "closed": "Issue closed",
        "all": "Issue all"
    }
    pr_markdown = ""
    pr_action = {
        "open": "Pull Request Event: opened",
        "closed": "Pull Request Event: closed",
        "all": "Pull Request Event: all"
    }
    for res in commit_responses:
        commit_markdown += f"## Commit by {res.get('commit').get('author').get('name')}\n"
        commit_markdown += f"- **SHA: **{res.get('sha')}\n"
        commit_markdown += f"- **Message: **{res.get('commit').get('message')}\n"
        commit_markdown += f"- **URL: **[Commit Link]({res.get('html_url')})\n\n"
    for res in issue_responses:
        body = res.get('body', 'No description')
        description = body.split(
            '\n')[0] + ('\n(...)' if len(body.split('\n')) > 1 else '')
        issue_markdown += f"## {issue_action.get(res.get('state'))}\n"
        issue_markdown += f"- Title: {res.get('title')}\n"
        issue_markdown += f"- Description: \n```markdown\n{description}\n```\n"
        issue_markdown += f"- Author: {res.get('user').get('login')}\n"
        issue_markdown += f"- URL: [Link]({res.get('html_url')})\n\n"
    for res in pr_responses:
        pr_markdown += f"## {pr_action.get(res.get('state'))}\n"
        pr_markdown += f"- PR Number: {res.get('number')}\n"
        pr_markdown += f"- Title: {res.get('title')}\n"
        pr_markdown += f"- Author: {res.get('user').get('login')}\n"
        pr_markdown += f"- State: {res.get('state')}\n"
        pr_markdown += f"- Created At: {res.get('created_at')}\n"
        if res.get('state') == "closed" and res.get('merged'):
            pr_markdown += f"- Merged: Yes\n\n"
        elif res.get('state') == "closed":
            pr_markdown += f"- Merged: No\n\n"
    markdown_content = commit_markdown + issue_markdown + pr_markdown

    # res_list = []
    # for idx, row in enumerate(data[1]):
    note_id = uuid.uuid4()
    note_id_string = str(note_id)
    user_id = data[1][0].get("user_id")
    if not validate_user_in_premium_team(user_id):
        # break
        raise_custom_error(401, 820)
    user_data, count = supabase.table("user_setting").select(
        "*").eq("is_deleted", False).eq("id", user_id).execute()
    has_signature = user_data[1][0].get("has_signature")
    if has_signature:
        url = generate_presigned_url(
            str(user_data[1][0].get("id")) + ".png")
    else:
        url = None
    first_name = user_data[1][0].get("first_name")
    last_name = user_data[1][0].get("last_name")
    if not first_name and not last_name:
        raise_custom_error(401, 121)
        # username = "No Name"
    else:
        username = last_name + " " + first_name

    breadcrumb_data, count = supabase.rpc(
        "bucket_breadcrumb_data", {"bucket_id": data[1][0].get("bucket_id")}).execute()
    if not breadcrumb_data[1]:
        raise_custom_error(500, 250)

    pdf_res = await generate_pdf_using_markdown(note_id=note_id_string, markdown_content=markdown_content, project_title=breadcrumb_data[1][0].get("project_title"), bucket_title=breadcrumb_data[1][0].get("bucket_title"), author=username, signature_url=url)
    await sign_pdf(pdf_res)
    signed_pdf_res = f"func/dashboard/pdf_generator/output/{note_id_string}_signed.pdf"
    SOURCE_PATH = "func/dashboard/pdf_generator"
    try:
        # upload pdf
        with open(signed_pdf_res, "rb") as f:
            pdf_data = f.read()
    except Exception as e:
        print(e)
        # delete result pdf
        if os.path.isfile(f"{SOURCE_PATH}/output/{note_id_string}.pdf"):
            os.unlink(f"{SOURCE_PATH}/output/{note_id_string}.pdf")
            print(f"{SOURCE_PATH}/output/{note_id_string}.pdf deleted")
        raise_custom_error(500, 120)
    # raise Exception("test")
    upload_blob(pdf_data, note_id_string + ".pdf")
    pdf_hash = hashlib.sha256(pdf_data).hexdigest()
    ledger_result = write_ledger(
        {"id": note_id_string, "hash": pdf_hash})
    try:
        os.unlink(f"{SOURCE_PATH}/output/{note_id_string}.pdf")
        print(f"{SOURCE_PATH}/output/{note_id_string}.pdf deleted")
        os.unlink(f"{SOURCE_PATH}/output/{note_id_string}_signed.pdf")
        print(f"{SOURCE_PATH}/output/{note_id_string}_signed.pdf deleted")
    except Exception as e:
        print(e)
        raise_custom_error(500, 130)

    transaction_id = ledger_result.get("transactionId")
    current_time = datetime.now(
        timezone('Asia/Seoul')).strftime("%Y-%m-%d %H:%M:%S")
    note = schemas.NoteCreate(
        id=note_id,
        bucket_id=uuid.UUID(data[1][0].get("bucket_id")),
        user_id=uuid.UUID(data[1][0].get("user_id")),
        # title=f"{current_time}에 생성된 {GithubMarkdownRequest.eventType} 노트(Github)",
        title=f"{current_time} 이전에 생성된 모든 Commit | PR | Issue 노트(Github)",
        timestamp_transaction_id=transaction_id,
        # file_name=f"{current_time}에 생성된 {GithubMarkdownRequest.eventType} 노트(Github)",
        file_name=f"{current_time} 이전에 생성된 모든 Commit | PR | Issue 노트(Github)",
        is_github=True,
        github_type="Commit",
        github_link=repository_info.url,
        pdf_hash=pdf_hash
    )
    res = create_note(note)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })
