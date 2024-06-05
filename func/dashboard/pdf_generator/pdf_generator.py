from PIL import Image
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
    subprocess.run(["libreoffice", "--headless", "--convert-to", "pdf",
                   f"{source_path}/input/{file_name}.{extension}", "--outdir", f"{source_path}/output"])
    return f"{file_name}.pdf"


def create_intro_page(title: str, author: str, description: str | None, SOURCE_PATH: str, note_id: str, signature_url: str | None = None):
    from datetime import datetime

    pdf = FPDF()

    date = datetime.now().strftime("%Y-%m-%d")
    pdf.add_page()

    pdf.add_font("Pretendard", style="",
                 fname=f"{SOURCE_PATH}/Pretendard-Regular.ttf")
    pdf.set_font("Pretendard", size=24)
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.set_font("Pretendard", size=12)
    pdf.cell(200, 10, txt=f"Author: {author}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Date: {date}", ln=True, align='L')
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())

    pdf.set_font("Pretendard", size=12)
    if description:
        # # Limit description to 2000 characters
        # description = description.encode(
        #     "utf-8")[:2000].decode("utf-8", "ignore") if description else None
        description = description[:1000]
        print(description)
        pdf.set_font("Pretendard", size=12)
        pdf.multi_cell(0, 10, description)
    if signature_url:
        # 이미지 크기
        img_width = 100
        img_height = 40

        # 이미지 위치
        img_x = pdf.w - img_width - 0  # 우측 여백 0
        img_y = pdf.h - img_height - 0  # 하단 여백 0

        pdf.image(signature_url, x=img_x, y=img_y, w=img_width, h=img_height)

    res = pdf.output()
    with open(f"{SOURCE_PATH}/output/{note_id}_intro.pdf", 'wb') as f:
        f.write(res)
        print(f"{SOURCE_PATH}/output/{note_id}_intro.pdf saved")


def generate_pdf(title: str, username: str, note_id: str, description: str | None, files: List[Union[UploadFile, None]], contents: List[Union[bytes, None]], signature_url: str | None = None):
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
                      SOURCE_PATH, note_id, signature_url)

    if files:
        if not all([file.filename.split(".")[-1] in AVAILABLE_EXTENSIONS for file in files]):
            raise HTTPException(
                status_code=422, detail="Unprocessable file extension")
        for idx, file in enumerate(files):
            extension = file.filename.split(".")[-1]
            filename = f"{note_id}_{idx}"

        if not all([file.filename.split(".")[-1] in AVAILABLE_EXTENSIONS for file in files]):
            raise HTTPException(
                status_code=422, detail="Unprocessable file extension")

        for idx, file in enumerate(files):
            extension = file.filename.split(".")[-1]
            filename = f"{note_id}_{idx}"

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
                    background = Image.new("RGB", image.size, (255, 255, 255))
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

    # merge pdfs
    pdfs = [f"{SOURCE_PATH}/output/{note_id}_intro.pdf"]
    if files:
        pdfs = pdfs + \
            [f"{SOURCE_PATH}/output/{note_id}_{idx}.pdf" for idx in range(
                len(files))]
    print(pdfs)
    pdfmerge(pdfs, f"{SOURCE_PATH}/output/{note_id}.pdf")
    print(f"{SOURCE_PATH}/output/{note_id}.pdf saved")

    raise HTTPException(status_code=500, detail="Test Error")

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
    print("Success!")

    return f"{SOURCE_PATH}/output/{note_id}"

# # testing
# convert_doc_to_pdf("func/dashboard/pdf_generator", "3d4256d9-20e8-4acc-9c51-42c90b4456ab_0", "docx")
