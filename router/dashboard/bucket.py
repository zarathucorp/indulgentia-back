from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from pydantic import UUID4
from typing import Optional, List, Union, Annotated, Literal
import uuid
import hashlib
from datetime import datetime
from pytz import timezone
import zipfile

from database import schemas
from func.dashboard.crud.bucket import *
from func.auth.auth import *
from cloud.azure.blob_storage import *
from cloud.azure.confidential_lendger import write_ledger, read_ledger, get_ledger_receipt
from func.error.error import raise_custom_error
from func.user.team import validate_user_in_premium_team
from func.github.fetch import fetch_github_data
from func.dashboard.pdf_generator.pdf_generator import generate_pdf_using_markdown
from func.note_handling.pdf_sign import sign_pdf
from func.note_handling.note_export import process_bucket_ids, delete_files
from func.dashboard.crud.note import *
from func.user.team import validate_user_is_leader_in_own_team


router = APIRouter(
    prefix="/bucket",
    responses={404: {"description": "Not found"}},
)


class DonwloadBucketInfo(BaseModel):
    bucket_ids: List[str]
    is_merged_required: Optional[bool] = False
    is_filename_id: Optional[bool] = False

# pdf multiple download


@router.post("/file", tags=["bucket"])
async def get_bucket_files(req: Request, download_bucket_info: DonwloadBucketInfo, background_tasks: BackgroundTasks):
    user: UUID4 = verify_user(req)
    bucket_ids = download_bucket_info.bucket_ids
    is_merged_required = download_bucket_info.is_merged_required
    is_filename_id = download_bucket_info.is_filename_id
    if not user:
        raise_custom_error(403, 213)
    if not validate_user_in_premium_team(user):
        raise_custom_error(401, 820)
    for bucket_id in bucket_ids:
        try:
            uuid.UUID(bucket_id)
        except ValueError:
            raise_custom_error(422, 210)

    download_bucket_infos = process_bucket_ids(
        user, bucket_ids, is_merged_required, is_filename_id)

    current_time = datetime.now(
        timezone('Asia/Seoul')).strftime("%Y%m%d_%H%M%S GMT+0900")
    with zipfile.ZipFile(f"func/dashboard/pdf_generator/output/Report_{current_time}.zip", "w") as zipf:
        for bucket_info in download_bucket_infos:
            zipf.write(bucket_info["output_file"], bucket_info["filename"])

    # 작업 후 파일 삭제
    final_files_to_delete = []
    for bucket_info in download_bucket_infos:
        final_files_to_delete += bucket_info["files_to_delete"]
    final_files_to_delete.append(
        f"func/dashboard/pdf_generator/output/Report_{current_time}.zip")

    background_tasks.add_task(delete_files, final_files_to_delete)

    return FileResponse(f"func/dashboard/pdf_generator/output/Report_{current_time}.zip", filename=f"Report_{current_time}.zip", media_type="application/zip")


# read list


@router.get("/list/{project_id}", tags=["bucket"])
async def get_bucket_list(req: Request, project_id: str):
    try:
        uuid.UUID(project_id)
    except ValueError:
        raise_custom_error(422, 210)
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    if not validate_user_in_premium_team(user):
        raise_custom_error(401, 820)
    data, count = supabase.rpc(
        "verify_project", {"user_id": str(user), "project_id": project_id}).execute()
    if not data[1]:
        raise_custom_error(401, 210)
    res = read_bucket_list(uuid.UUID(project_id))
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })

# read


@router.get("/{bucket_id}", tags=["bucket"])
async def get_bucket(req: Request, bucket_id: str):
    try:
        uuid.UUID(bucket_id)
    except ValueError:
        raise_custom_error(422, 210)
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    if not validate_user_in_premium_team(user):
        raise_custom_error(401, 820)
    data, count = supabase.rpc(
        "verify_bucket", {"user_id": str(user), "bucket_id": bucket_id}).execute()
    if not data[1]:
        raise_custom_error(401, 310)
    res = read_bucket(uuid.UUID(bucket_id))
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })


# create

@router.post("", include_in_schema=False)
@router.post("/", tags=["bucket"])
async def add_bucket(req: Request, bucket: schemas.BucketCreate):
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    if not validate_user_in_premium_team(user):
        raise_custom_error(401, 820)
    data, count = supabase.rpc("verify_project", {"user_id": str(
        user), "project_id": str(bucket.project_id)}).execute()
    if not data[1]:
        raise_custom_error(401, 210)
    res = create_bucket(bucket)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })

# update


@router.put("/{bucket_id}", tags=["bucket"])
async def change_bucket(req: Request, bucket: schemas.BucketUpdate):
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    # if not validate_user_in_premium_team(user):
    #     raise_custom_error(401, 820)
    # if not user == bucket.manager_id:
        # raise_custom_error(401, 320)

    # 팀 리더인지 확인
    if not validate_user_is_leader_in_own_team(user):
        raise_custom_error(401, 520)

    res = update_bucket(bucket)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })

# delete


@router.delete("/{bucket_id}", tags=["bucket"])
async def drop_bucket(req: Request, bucket_id: str):
    try:
        uuid.UUID(bucket_id)
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

    data, count = supabase.table("bucket").select(
        "manager_id").eq("id", bucket_id).execute()
    if not data[1]:
        raise_custom_error(500, 231)
    # if not user == data[1][0]["manager_id"]:
        # raise_custom_error(401, 320)
    res = flag_is_deleted_bucket(uuid.UUID(bucket_id))
    return JSONResponse(content={
        "status": "succeed",
        "data": res
    })


""" Old version
@router.delete("/{bucket_id}", tags=["bucket"])
async def drop_bucket(req: Request, bucket_id: str):
    user: UUID4 = verify_user(req)
    # if not user:
    #     raise HTTPException(status_code=401, detail="Unauthorized")
    data, count = supabase.table("bucket").select(
        "manager_id").eq("id", bucket_id).execute()
    if not data[1]:
        raise HTTPException(status_code=400, detail="No data")
    if not user == data[1][0]["manager_id"]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    res = delete_bucket(bucket_id)
    return JSONResponse(content={
        "status": "succeed",
        "data": res
   })
"""


@router.get("/{bucket_id}/breadcrumb", tags=["bucket"])
async def get_bucket_breadcrumb(req: Request, bucket_id: str):
    try:
        uuid.UUID(bucket_id)
    except ValueError:
        raise_custom_error(422, 210)
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    if not validate_user_in_premium_team(user):
        raise_custom_error(401, 820)
    data, count = supabase.rpc(
        "bucket_breadcrumb_data", {"bucket_id": bucket_id}).execute()
    if not data[1]:
        raise_custom_error(500, 250)
    return JSONResponse(content={
        "status": "succeed",
        "data": data[1][0]
    })


@router.get("/{bucket_id}/github_repo", tags=["bucket"])
async def get_connected_github_repositories(req: Request, bucket_id: str):
    try:
        uuid.UUID(bucket_id)
    except ValueError:
        raise_custom_error(422, 210)
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    if not validate_user_in_premium_team(user):
        raise_custom_error(401, 820)
        # raise HTTPException(status_code=401, detail="Unauthorized")
    data = get_connected_gitrepo(uuid.UUID(bucket_id))
    verify_data, count = supabase.rpc(
        "verify_bucket", {"user_id": str(user), "bucket_id": bucket_id}).execute()
    if not verify_data[1]:
        raise_custom_error(401, 310)
    return JSONResponse(content={
        "status": "succeed",
        "data": data
    })


@router.post("/{bucket_id}/github_repo", tags=["bucket"])
async def connect_github_repository(req: Request, bucket_id: str, newRepo: schemas.GitrepoCreate):
    try:
        uuid.UUID(bucket_id)
    except ValueError:
        raise_custom_error(422, 210)
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    if not validate_user_in_premium_team(user):
        raise_custom_error(401, 820)
    verify_data, count = supabase.rpc(
        "verify_bucket", {"user_id": str(user), "bucket_id": bucket_id}).execute()
    if not verify_data[1]:
        raise_custom_error(401, 310)
    check_gitrepo_exists_result = supabase.rpc("check_gitrepo_exists", {
                                               "g_bucket_id": bucket_id, "g_repo_url": newRepo.repo_url}).execute().data
    if check_gitrepo_exists_result:
        print(check_gitrepo_exists_result)
        print("here")
        raise_custom_error(401, 330)
    data = create_connected_gitrepo(newRepo, user)

    # 이전 github commit | issue | PR 내역 note에 저장
    user_data, count = supabase.table("user_setting").select("github_token").eq(
        "is_deleted", False).eq("id", user).execute()
    if not user_data[1]:
        raise_custom_error(500, 231)

    commit_responses = fetch_github_data(user_data[1][0].get(
        "github_token"), newRepo.git_username, newRepo.git_repository, "commits")
    issue_responses = fetch_github_data(user_data[1][0].get(
        "github_token"), newRepo.git_username, newRepo.git_repository, "issues")
    pr_responses = fetch_github_data(user_data[1][0].get(
        "github_token"), newRepo.git_username, newRepo.git_repository, "pulls")
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
        issue_markdown += f"## {issue_action.get(res.get('state'))}\n"
        issue_markdown += f"- Title: {res.get('title')}\n"
        issue_markdown += f"- Description: {res.get('body', 'No description')}\n"
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
            pr_markdown += f"- Merged: Yes\n"
        elif res.get('state') == "closed":
            pr_markdown += f"- Merged: No\n"
    markdown_content = commit_markdown + issue_markdown + pr_markdown

    # res_list = []
    # for idx, row in enumerate(data[1]):
    note_id = uuid.uuid4()
    note_id_string = str(note_id)
    if not validate_user_in_premium_team(user):
        # break
        raise_custom_error(401, 820)
    user_data, count = supabase.table("user_setting").select(
        "*").eq("is_deleted", False).eq("id", user).execute()
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
        "bucket_breadcrumb_data", {"bucket_id": bucket_id}).execute()
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
        bucket_id=uuid.UUID(bucket_id),
        user_id=user,
        # title=f"{current_time}에 생성된 {GithubMarkdownRequest.eventType} 노트(Github)",
        title=f"{current_time} 이전에 생성된 모든 Commit | PR | Issue 노트(Github)",
        timestamp_transaction_id=transaction_id,
        # file_name=f"{current_time}에 생성된 {GithubMarkdownRequest.eventType} 노트(Github)",
        file_name=f"{current_time} 이전에 생성된 모든 Commit | PR | Issue 노트(Github)",
        is_github=True,
        github_type="Commit",
        github_link=newRepo.repo_url,
        pdf_hash=pdf_hash
    )
    res = create_note(note)
    print(res)

    return JSONResponse(content={
        "status": "succeed",
        "data": data
    })


@router.delete("/{bucket_id}/github_repo/{repo_id}", tags=["bucket"])
async def disconnect_github_repository(req: Request, bucket_id: str, repo_id: str):
    try:
        uuid.UUID(bucket_id)
        uuid.UUID(repo_id)
    except ValueError:
        raise_custom_error(422, 210)
    user: UUID4 = verify_user(req)
    if not user:
        raise_custom_error(403, 213)
    if not validate_user_in_premium_team(user):
        raise_custom_error(401, 820)
    verify_data, count = supabase.rpc(
        "verify_bucket", {"user_id": str(user), "bucket_id": bucket_id}).execute()
    if not verify_data[1]:
        raise_custom_error(401, 310)
    data = flag_is_deleted_gitrepo(uuid.UUID(repo_id))
    return JSONResponse(content={
        "status": "succeed",
        "data": data
    })
