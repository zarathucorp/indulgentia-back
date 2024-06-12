from PIL import Image, UnidentifiedImageError
from pdfmerge import pdfmerge
from fpdf import FPDF
import io
from pydantic import UUID4, BaseModel
from fastapi import HTTPException, UploadFile, File
from uuid import UUID
from typing import List, Union
import os
import shutil
import subprocess
import re
import asyncio
from func.error.error import raise_custom_error


# def generate_pdf(user_id:str, files=List[UploadFile], descriptions=List[str]):
#     class PDF(FPDF):
#         def header(self):
#             self.add_font("Pretendard", style="B", fname="Pretendard-Bold.ttf")
#             self.set_font("Pretendard", "B", 12)
#             self.cell(0, 10, user_id, 0, 1, "C")
#             self.ln(10)

#         def footer(self):
#             self.add_font("Pretendard", style="I", fname="Pretendard-Thin.ttf")
#             self.set_y(-15)
#             self.set_font("Pretendard", "I", 8)
#             self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "R")

#     pdf = PDF()
#     pdf.add_font("Pretendard", style="", fname="Pretendard-Regular.ttf")
#     pdf.set_font("Pretendard", size=12)

#     if len(files) != len(descriptions):
#         raise HTTPException(status_code=400, detail="Number of files and descriptions do not match")

#     num_pages = len(descriptions)

#     for idx in num_pages:
#         description = descriptions[idx] if descriptions[idx] else None
#         description = description.encode("utf-8")[:800].decode("utf-8", "ignore") if description else None # Limit description to 800 characters

#         raw_image = files[idx].file.read() if files[idx] else None

#         pdf.add_page()

#         if raw_image:
#             max_image_height = pdf.h * 1/2
#             max_image_width = pdf.w - 20  # 10 points margin on each side
#             image_stream = io.BytesIO(raw_image)
#             image = Image.open(image_stream)
#             image_height = image.height * max_image_height / image.width
#             image_width = image.width * max_image_height / image.height

#             if image_height > max_image_height:
#                 image_height = max_image_height
#                 image_width = image.width * image_height / image.height

#             if image_width > max_image_width:
#                 image_width = max_image_width
#                 image_height = image.height * image_width / image.width

#             image_y = (pdf.h - image_height) / 2  # Center the image
#             image_x = (pdf.w - image_width) / 2
#             pdf.image(raw_image, x=image_x, y=image_y, h=image_height, w=image_width)

#             if description:
#                 pdf.set_y(image_y + image_height + 10)
#                 pdf.multi_cell(0, 10, description)
#         elif description:
#             pdf.set_y(10)  # Set description at the top
#             pdf.multi_cell(0, 10, description)
#         else:
#             continue  # Skip to the next page if both image and description are None

#     res = pdf.output()

#     print(res)
#     print(type(res))

#     return res

# MS office & HWP to PDF
def convert_doc_to_pdf(source_path: str, file_name: str, extension: str):
    try:
        subprocess.run(["libreoffice", "--headless", "--convert-to", "pdf",
                        f"{source_path}/input/{file_name}.{extension}", "--outdir", f"{source_path}/output"])
    except Exception as e:
        print(e)
        raise_custom_error(500, 420)
    return f"{file_name}.pdf"


def split_text(text: str, max_width: int, pdf: FPDF):
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        if pdf.get_string_width(current_line + " " + word) <= max_width:
            current_line += " " + word
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines


def create_intro_page(title: str, author: str, description: str | None, SOURCE_PATH: str, note_id: str, project_title: str, bucket_title, signature_url: str | None = None):
    from datetime import datetime

    try:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=5)

        date = datetime.now().strftime("%Y-%m-%d")
        date_kor = datetime.now().strftime("%Y년 %m월 %d일")
        pdf.add_page()

        pdf.add_font("Pretendard", style="",
                     fname=f"{SOURCE_PATH}/Pretendard-Regular.ttf")
        pdf.set_font("Pretendard", size=24)
        pdf.cell(200, 10, text=title, ln=True, align='C')
        pdf.set_y(pdf.get_y()+10)
        pdf.line(0, pdf.get_y(), pdf.w, pdf.get_y())

        pdf.set_y(pdf.get_y())
        pdf.set_font_size(12)
        pdf.cell(200, 10, text="Description", ln=True, align='L')
        if description:
            # # Limit description to 2000 characters
            # description = description.encode(
            #     "utf-8")[:2000].decode("utf-8", "ignore") if description else None
            description = description[:1000]
            print(description)
            pdf.set_font_size(12)
            pdf.multi_cell(0, 10, description)

        pdf.set_font_size(10)
        pdf.set_y(pdf.h - 50)
        pdf.cell(
            190, 10, text=f"※ 본 문서는 {date_kor}에 작성되었으며 이후 수정되지 않았습니다. 이 문서의 내용은 변조 불가능한 블록체인에 기록되어 있습니다.", ln=0, align='R')

        # project_title = "Lorem ipsum dolor sit amet, consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. Lorem ipsum dolor sit amet, consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
        # project_title = "대통령은 제3항과 제4항의 사유를 지체없이 공포하여야 한다. 선거에 있어서 최고득표자가 2인 이상인 때에는 국회의 재적의원 과반수가 출석한 공개회의에서 다수표를 얻은 자를 당선자로 한다. 국무총리는 국회의 동의를 얻어 대통령이 임명한다. 모든 국민은 신체의 자유를 가진다. 누구든지 법률에 의하지 아니하고는 체포·구속·압수·수색 또는 심문을 받지 아니하며, 법률과 적법한 절차에 의하지 아니하고는 처벌·보안처분 또는 강제노역을 받지 아니한다. 국회의 회의는 공개한다. 다만, 출석의원 과반수의 찬성이 있거나 의장이 국가의 안전보장을 위하여 필요하다고 인정할 때에는 공개하지 아니할 수 있다."
        # Footer
        pdf.set_font_size(12)
        pdf.set_y(pdf.h - 40)
        pdf.line(0, pdf.get_y(), pdf.w, pdf.get_y())
        pdf.set_y(pdf.get_y() + 5)
        pdf.set_x(35)
        pdf.set_font_size(10)
        pdf.set_text_color(157, 1, 1)
        pdf.cell(15, 10, text="Project: ", ln=0, align='L', border="B")

        pdf.set_font_size(12)
        pdf.set_text_color(70, 70, 70)
        lines = split_text(project_title, 89, pdf)
        if len(lines) == 1:
            pdf.cell(90, 10, text=f"{project_title}",
                     ln=True, align='L', border="RB")
        else:
            pdf.set_font_size(8)
            new_lines = split_text(project_title, 89, pdf)
            project_title_1 = new_lines[0]
            project_title_2 = new_lines[1] + '...'
            pdf.cell(90, 5, text=f"{project_title_1}",
                     ln=True, align='L', border="R")
            pdf.set_x(50)
            pdf.cell(90, 5, text=f"{project_title_2}",
                     ln=True, align='L', border="RB")
        pdf.set_x(35)
        pdf.set_font_size(10)
        pdf.set_text_color(157, 1, 1)
        pdf.cell(15, 10, text="Bucket: ", ln=0, align='L', border="B")
        pdf.set_font_size(12)
        pdf.set_text_color(70, 70, 70)
        pdf.cell(90, 10, text=f"{bucket_title}",
                 ln=True, align='L', border="RB")
        pdf.set_x(35)
        pdf.set_font_size(10)
        pdf.set_text_color(157, 1, 1)
        pdf.cell(15, 10, text="Date: ", ln=0, align='L')
        pdf.set_font_size(12)
        pdf.set_text_color(70, 70, 70)
        pdf.cell(90, 10, text=f"{date}", ln=0, align='L', border="R")
        pdf.set_y(pdf.get_y() - 20)
        pdf.set_x(140)
        pdf.set_font_size(10)
        pdf.set_text_color(157, 1, 1)
        pdf.cell(15, 10, text=f"Author: ", ln=0, align='L', border="B")
        pdf.set_x(155)
        pdf.set_font_size(12)
        pdf.set_text_color(70, 70, 70)
        pdf.cell(50, 10, text=f"{author}", ln=True, align='C', border="B")
        pdf.set_x(140)
        pdf.set_font_size(10)
        pdf.set_text_color(157, 1, 1)
        pdf.cell(20, 10, text=f"Signature: ", ln=True, align='L')

        if signature_url:
            img_width = 50
            img_height = 20

            img_x = pdf.w - img_width - 0
            # Set the y coordinate of the image to the current y coordinate plus the height of the cell
            img_y = pdf.get_y() - 10

            pdf.image(signature_url, x=img_x, y=img_y,
                      w=img_width, h=img_height)

        res = pdf.output()
    except Exception as e:
        print(e)
        raise_custom_error(500, 410)
    try:
        with open(f"{SOURCE_PATH}/output/{note_id}_intro.pdf", 'wb') as f:
            f.write(res)
            print(f"{SOURCE_PATH}/output/{note_id}_intro.pdf saved")
    except Exception as e:
        print(e)
        raise_custom_error(500, 110)


async def generate_pdf(title: str, username: str, note_id: str, description: str | None, files: List[Union[UploadFile, None]], contents: List[Union[bytes, None]], project_title: str, bucket_title: str, signature_url: str | None = None):
    SOURCE_PATH = "func/dashboard/pdf_generator"
    DOC_EXTENSIONS = ["doc", "docx", "hwp",
                      "hwpx", "ppt", "pptx", "xls", "xlsx"]
    IMAGE_EXTENSIONS = ["png", "jpg", "jpeg", "bmp"]
    AVAILABLE_EXTENSIONS = DOC_EXTENSIONS + IMAGE_EXTENSIONS + ["pdf"]
    A4_SIZE = (595, 842)

    # Intro PDF
    print(description)
    print(files)
    create_intro_page(title, username, description,
                      SOURCE_PATH, note_id, project_title, bucket_title, signature_url)

    async def process_file(file, idx):
        extension = file.filename.split(".")[-1]
        filename = f"{note_id}_{idx}"
        try:
            with open(f"{SOURCE_PATH}/input/{filename}.{extension}", 'wb') as f:
                f.write(contents[idx])
                print(f"{SOURCE_PATH}/input/{filename}.{extension} saved")

            if extension in DOC_EXTENSIONS:
                res = convert_doc_to_pdf(SOURCE_PATH, filename, extension)
                print(f"{SOURCE_PATH}/output/{res} saved")
            elif extension in IMAGE_EXTENSIONS:
                image = Image.open(
                    f"{SOURCE_PATH}/input/{filename}.{extension}")
                image.thumbnail(A4_SIZE)
                if image.mode == "RGBA":
                    image.load()
                    background = Image.new(
                        "RGB", image.size, (255, 255, 255))
                    background.paste(image, mask=image.split()[3])
                    background.save(f"{SOURCE_PATH}/output/{filename}.pdf")
                else:
                    image.save(f"{SOURCE_PATH}/output/{filename}.pdf")
                print(f"{SOURCE_PATH}/output/{filename}.pdf saved")
            else:
                # pdf file
                with open(f"{SOURCE_PATH}/output/{filename}.{extension}", 'wb') as f:
                    f.write(contents[idx])
                    print(f"{SOURCE_PATH}/output/{filename}.pdf saved")
        except FileNotFoundError as e:
            print(e)
            # 이미지 pdf 없음
            raise_custom_error(500, 430)
        except ValueError as e:
            print(e)
            # 이미지 pdf 변환 오류
            raise_custom_error(500, 430)
        except UnidentifiedImageError as e:
            print(e)
            # PIL 범용 에러
            raise_custom_error(500, 430)
        except OSError as e:
            print(e)
            # file 읽기/쓰기 오류
            raise_custom_error(500, 110)
        except Exception as e:
            print(e)
            # 그외 에러
            raise_custom_error(500, 400)

    if files:
        if not all([file.filename.split(".")[-1] in AVAILABLE_EXTENSIONS for file in files]):
            raise HTTPException(
                status_code=422, detail="Unprocessable file extension")

        tasks = [process_file(file, idx) for idx, file in enumerate(files)]
        await asyncio.gather(*tasks)

    # merge pdfs
    try:
        pdfs = [f"{SOURCE_PATH}/output/{note_id}_intro.pdf"]
        if files:
            pdfs = pdfs + \
                [f"{SOURCE_PATH}/output/{note_id}_{idx}.pdf" for idx in range(
                    len(files))]
        print(pdfs)
        pdfmerge(pdfs, f"{SOURCE_PATH}/output/{note_id}.pdf")
        print(f"{SOURCE_PATH}/output/{note_id}.pdf saved")
    except Exception as e:
        print(e)
        raise_custom_error(500, 440)
        raise HTTPException(
            status_code=500, detail="Failed to merge pdfs")

    # delete files
    try:
        os.unlink(f"{SOURCE_PATH}/output/{note_id}_intro.pdf")
        print(f"{SOURCE_PATH}/output/{note_id}_intro.pdf deleted")
        if files:
            for idx, file in enumerate(files):
                file_input_path = os.path.join(
                    SOURCE_PATH + "/input/", f"{note_id}_{idx}.{file.filename.split('.')[-1]}")
                file_output_path = os.path.join(
                    SOURCE_PATH + "/output/", f"{note_id}_{idx}.pdf")
                if os.path.isfile(file_input_path):
                    os.unlink(file_input_path)
                    print(f"{file_input_path} deleted")
                if os.path.isfile(file_output_path):
                    os.unlink(file_output_path)
                    print(f"{file_output_path} deleted")
    except Exception as e:
        print(e)
        raise_custom_error(500, 130)
    print("Success!")

    return f"{SOURCE_PATH}/output/{note_id}"

# # testing
# convert_doc_to_pdf("func/dashboard/pdf_generator", "3d4256d9-20e8-4acc-9c51-42c90b4456ab_0", "docx")
