from fpdf import FPDF
from PIL import Image
import io
from pydantic import UUID4, BaseModel
from fastapi import UploadFile, File
from uuid import UUID
from typing import List


class PageContentBase(BaseModel):
    page: int
    image: bytes
    description: str

def generate_pdf(title:str, pdf_pages: List[PageContentBase], note_id: UUID4):
    class PDF(FPDF):
        def header(self):
            self.set_font("helvetica", "B", 12)
            self.cell(0, 10, title, 0, 1, "C")
            self.ln(10)
        
        def footer(self):
            self.set_y(-15)
            self.set_font("helvetica", "I", 8)
            self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "R")
    
    pdf = PDF()
    pdf.set_font("helvetica", size=12)

    for page in pdf_pages:
        description = page.get("description")[:500]
        pdf.add_page()

        max_image_height = pdf.h * 2/3
        max_image_width = pdf.w - 20  # 10 points margin on each side
        image_stream = io.BytesIO(page.get("image"))
        image = Image.open(image_stream)
        image_height = image.height * max_image_height / image.width
        image_width = image.width * max_image_height / image.height

        if image_height > max_image_height:
            image_height = max_image_height
            image_width = image.width * image_height / image.height

        if image_width > max_image_width:
            image_width = max_image_width
            image_height = image.height * image_width / image.width
            
        image_y = 20  # 10 points for header height, 10 points for margin
        image_x = (pdf.w - image_width) / 2
        pdf.image(page.get("image"), x=image_x, y=image_y, h=image_height, w=image_width)

        pdf.set_y(image_y + image_height + 10)
        pdf.multi_cell(0, 10, description)

    res = pdf.output()

    print(res)
    print(type(res))

    return res

with open("cat.jpg", "rb") as f:
    image1 = f.read()

with open("dog.png", "rb") as f:
    image2 = f.read()

test_pdf_pages = [
    {
        "page": 1,
        "image": image1,
        "description": "This is page 1"
    },
    {
        "page": 2,
        "image": image2,
        "description": "This is page 2"
    }
]

test_note_id = UUID("6a423db5-8a34-4153-9795-c6f058020445", version=4)

res = generate_pdf("test_title", test_pdf_pages, test_note_id)

with open("test.pdf", "wb") as f:
    f.write(res)
