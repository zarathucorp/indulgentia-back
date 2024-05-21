from PIL import Image
from pdfmerge import pdfmerge
from fpdf import FPDF
import io
from pydantic import UUID4, BaseModel
from fastapi import HTTPException, UploadFile, File
from uuid import UUID
from typing import List, Union
import sys
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
def convert_doc_to_pdf(filename:str):
    subprocess.run(["libreoffice", "--headless", "--convert-to", "pdf", f"./input/{filename}", "--outdir", "./output"])
    return f"{filename}.pdf"


def generate_pdf(note_id:str, description:str, files=List[UploadFile], contents=List[bytes]):
    DOC_EXTENSIONS = ["doc", "docx", "hwp"]
    IMAGE_EXTENSIONS = ["png", "jpg", "jpeg", "bmp"]

    for idx, file in enumerate(files):
        extension = file.filename.split(".")[-1]
        filename = f"{note_id}_{idx}.{extension}"

        with open(f"./input/{filename}", 'wb') as f:
            f.write(contents[idx])
            print(f"input/{filename} saved")
            
        if extension in DOC_EXTENSIONS:
            res = convert_doc_to_pdf(filename)
            print(f"./output/{res} saved")
        elif extension in IMAGE_EXTENSIONS:
            image = Image.open(f"./input/{filename}")
            if extension == "png":
                image.load()
                background = Image.new("RGB", image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])
                background.save(f"./output/{filename}.pdf")
            else:
                image.save(f"./output/{filename}.pdf")
            
            print(f"output/{filename}.pdf saved")
        else:
            # pdf file
            with open(f"./output/{filename}", 'wb') as f:
                f.write(contents)
                print(f"output/{filename} saved")
    
    # description to pdf
    if description:
        pdf = FPDF()
        pdf.add_font("Pretendard", style="", fname="Pretendard-Regular.ttf")
        pdf.set_font("Pretendard", size=12)
        pdf.add_page()
        description = description.encode("utf-8")[:2000].decode("utf-8", "ignore") if description else None # Limit description to 2000 characters
        pdf.multi_cell(0, 10, description)
        res = pdf.output()
        with open(f"./output/{note_id}_description.pdf", 'wb') as f:
            f.write(res)
            print(f"output/{note_id}_description.pdf saved")
    
    # merge pdfs
    pdfs = [f"./output/{note_id}_{idx}.pdf" for idx in range(len(files))]
    pdfs.append(f"./output/{note_id}_description.pdf") if description else None
    pdfmerge(pdfs, f"./output/{note_id}.pdf")
    print(f"output/{note_id}.pdf saved")
    print("Success!")

    return f"./output/{note_id}.pdf"            

# Testing
file_name = "dummy.hwpx"

file = convert_doc_to_pdf(file_name)
