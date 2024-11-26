import os
import zipfile
import uuid
from datetime import datetime
from pytz import timezone
from pdfmerge import pdfmerge
from func.error.error import raise_custom_error
from cloud.azure.blob_storage import *
from func.dashboard.crud.bucket import *
from func.dashboard.crud.note import *


# 파일 삭제 함수
def delete_files(file_paths):
    for file_path in file_paths:
        try:
            os.remove(file_path)
            print(f"{file_path} deleted")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")


def process_note_ids(note_ids, is_merged_required, is_filename_id):
    download_note_infos = []
    title_list = []

    for note_id in note_ids:
        try:
            note_info = {}
            pdf = download_blob(note_id + ".pdf")
            with open(f"func/dashboard/pdf_generator/input/Report_{note_id}.pdf", "wb") as f:
                f.write(pdf)
            note_info["index"] = note_ids.index(note_id)
            note_info["id"] = note_id
            note_detail = read_note_detail(note_id)
            temp_title = note_detail.get("note_title")
            if temp_title in title_list:
                num = title_list.count(temp_title)
                note_info["title"] = f"{temp_title}({num+1})"
            else:
                note_info["title"] = temp_title
            title_list.append(temp_title)
            download_note_infos.append(note_info)
        except Exception as e:
            print(e)
            raise_custom_error(500, 312)

    if not is_merged_required and not is_filename_id:
        for note_info in download_note_infos:
            os.rename(f"func/dashboard/pdf_generator/input/Report_{note_info['id']}.pdf",
                      f"func/dashboard/pdf_generator/input/Report_{note_info['title']}.pdf")

    current_time = datetime.now(
        timezone('Asia/Seoul')).strftime("%Y%m%d_%H%M%S GMT+0900")

    if is_merged_required:
        pdfs = [
            f"func/dashboard/pdf_generator/input/Report_{note_info['id']}.pdf" for note_info in download_note_infos]
        output_file = f"func/dashboard/pdf_generator/output/Report_{current_time}.pdf"
        pdfmerge(pdfs, output_file)
        return output_file, 'application/pdf', f"Report_{current_time}.pdf", pdfs + [output_file]
    else:
        output_file = f"func/dashboard/pdf_generator/output/Report_{current_time}.zip"
        with zipfile.ZipFile(output_file, "w") as zipf:
            for note_info in download_note_infos:
                if is_filename_id:
                    zipf.write(
                        f"func/dashboard/pdf_generator/input/Report_{note_info['id']}.pdf", f"Report_{note_info['id']}.pdf")
                else:
                    zipf.write(
                        f"func/dashboard/pdf_generator/input/Report_{note_info['title']}.pdf", f"Report_{note_info['title']}.pdf")
        return output_file, 'application/zip', f"Report_{current_time}.zip", [
            f"func/dashboard/pdf_generator/input/Report_{note_info['title']}.pdf" for note_info in download_note_infos] + [output_file]


def process_bucket_ids(user, bucket_ids, is_merged_required, is_filename_id):
    download_bucket_infos = []
    for bucket_id in bucket_ids:
        try:
            bucket_info = {}
            # 버킷 유효성 검사
            data, count = supabase.rpc(
                "verify_bucket", {"user_id": str(user), "bucket_id": bucket_id}).execute()
            if not data[1]:
                raise_custom_error(401, 310)
            # 버킷 내용 읽기 (시간순으로 변경)
            note_list = read_note_list(bucket_id)
            note_list.reverse()

            note_ids = [note.get("id") for note in note_list]

            # 노트 작업
            output_file, media_type, filename, files_to_delete = process_note_ids(
                note_ids, is_merged_required, is_filename_id)

            # 파일명 변경
            bucket_title = read_bucket(uuid.UUID(bucket_id)).get("title")
            if media_type == "application/pdf":
                new_filename = f"{bucket_title}.pdf"
            else:
                new_filename = f"{bucket_title}.zip"
            new_output_file = f"func/dashboard/pdf_generator/output/{new_filename}"
            new_files_to_delete = []
            for file_to_delete in files_to_delete:
                if file_to_delete.startswith("func/dashboard/pdf_generator/input/"):
                    new_files_to_delete.append(file_to_delete)

            new_files_to_delete.append(new_output_file)

            os.rename(output_file, new_output_file)

            # 버킷 정보 저장
            bucket_info["id"] = bucket_id
            bucket_info["title"] = bucket_title
            bucket_info["note_ids"] = note_ids
            bucket_info["output_file"] = new_output_file
            bucket_info["media_type"] = media_type
            bucket_info["filename"] = new_filename
            bucket_info["files_to_delete"] = new_files_to_delete

            download_bucket_infos.append(bucket_info)
        except Exception as e:
            print(e)
            raise_custom_error(500, 312)
    return download_bucket_infos
