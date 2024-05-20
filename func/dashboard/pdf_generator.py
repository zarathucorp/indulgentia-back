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
            self.add_font("Pretendard", style="B", fname="Pretendard-Bold.ttf")
            self.set_font("Pretendard", "B", 12)
            self.cell(0, 10, title, 0, 1, "C")
            self.ln(10)
        
        def footer(self):
            self.add_font("Pretendard", style="I", fname="Pretendard-Thin.ttf")
            self.set_y(-15)
            self.set_font("Pretendard", "I", 8)
            self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "R")
    
    pdf = PDF()
    pdf.add_font("Pretendard", style="", fname="Pretendard-Regular.ttf")
    pdf.set_font("Pretendard", size=12)

    for page in pdf_pages:
        description = page.get("description")
        description = description.encode("utf-8")[:800].decode("utf-8", "ignore")  # Limit description to 800 characters
        pdf.add_page()

        max_image_height = pdf.h * 1/2
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
        "description": "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. Nam quam nunc, blandit vel, luctus pulvinar, hendrerit id, lorem. Maecenas nec odio et ante tincidunt tempus. Donec vitae sapien ut libero venenatis faucibus. Nullam quis ante. Etiam sit amet orci eget eros faucibus tincidunt. Duis leo. Sed fringilla mauris sit amet nibh. Donec sodales sagittis magna. Sed consequat, leo eget bibendum sodales, augue velit cursus nunc, quis gravida magna mi a libero. Fusce vulputate eleifend sapien. Vestibulum purus quam, scelerisque ut, mollis sed, nonummy id, metus. Nullam accumsan lorem in dui. Cras ultricies mi eu turpis hendrerit fringilla. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; In ac dui quis mi consectetuer lacinia. Nam pretium turpis et arcu. Duis arcu tortor, suscipit eget, imperdiet nec, imperdiet iaculis, ipsum. Sed aliquam ultrices mauris. Integer ante arcu, accumsan a, consectetuer eget, posuere ut, mauris. Praesent adipiscing. Phasellus ullamcorper ipsum rutrum nunc. Nunc nonummy metus. Vestib"
    },
    {
        "page": 2,
        "image": image2,
        "description": '원장은 국회의 동의를 얻어 대통령이 임명하고. 대통령의 임기연장 또는 중임변경을 위한 헌법개정은 그 헌법개정 제안 당시의 대통령에 대하여는 효력이 없다, 국가안전보장회의의 조직·직무범위 기타 필요한 사항은 법률로 정한다. 국가원로자문회의의 의장은 직전대통령이 된다.법률이 정한 국무위원의 순서로 그 권한을 대행한다, 국가는 농·어민과 중소기업의 자조조직을 육성하여야 하며. 감사원은 세입·세출의 결산을 매년 검사하여 대통령과 차년도국회에 그 결과를 보고하여야 한다. 원장은 국회의 동의를 얻어 대통령이 임명하고.모든 국민은 행위시의 법률에 의하여 범죄를 구성하지 아니하는 행위로 소추되지 아니하며. 정당은 헌법재판소의 심판에 의하여 해산된다. 국채를 모집하거나 예산외에 국가의 부담이 될 계약을 체결하려 할 때에는 정부는 미리 국회의 의결을 얻어야 한다. 국무위원은 국정에 관하여 대통령을 보좌하며.대통령은 법률이 정하는 바에 의하여 훈장 기타의 영전을 수여한다. 대통령은 내우·외환·천재·지변 또는 중대한 재정·경제상의 위기에 있어서 국가의 안전보장 또는 공공의 안녕질서를 유지하기 위하여 긴급한 조치가 필요하고 국회의 집회를 기다릴 여유가 없을 때에 한하여 최소한으로 필요한 재정·경제상의 처분을 하거나 이에 관하여 법률의 효력을 가지는 명령을 발할 수 있다. 국토와 자원은 국가의 보호를 받으며. 국회에 제출된 법률안 기타의 의안은 회기중에 의결되지 못한 이유로 폐기되지 아니한다.공무원의 직무상 불법행위로 손해를 받은 국민은 법률이 정하는 바에 의하여 국가 또는 공공단체에 정당한 배상을 청구할 수 있다. 제1항의 지시를 받은 당해 행정기관은 이에 응하여야 한다. 이 경우 공무원 자신의 책임은 면제되지 아니한다, 누구든지 법률에 의하지 아니하고는 체포·구속·압수·수색 또는 심문을 받지 아니하며.국회의 의결은 재적의원 3분의 2 이상의 찬성을 얻어야 한다. 국가는 농업 및 어업을 보호·육성하기 위하여 농·어촌종합개발과 그 지원등 필요한 계획을 수립·시행하여야 한다. 군사법원의 조직·권한 및 재판관의 자격은 법률로 정한다, 재판관은 대통령이 임명한다.위원은 탄핵 또는 금고 이상의 형의 선고에 의하지 아니하고는 파면되지 아니한다. 국회의원은 그 지위를 남용하여 국가·공공단체 또는 기업체와의 계약이나 그 처분에 의하여 재산상의 권리·이익 또는 직위를 취득하거나 타인을 위하여 그 취득을 알선할 수 없다, 대통령은 국무회의의 의장이 되고. 어떠한 형태로도 이를 창설할 수 없다.국가는 건전한 소비행위를 계도하고 생산품의 품질향상을 촉구하기 위한 소비자보호운동을 법률이 정하는 바에 의하여 보장한다. 국회는 국정을 감사하거나 특정한 국정사안에 대하여 조사할 수 있으며. 고용·임금 및 근로조건에 있어서 부당한 차별을 받지 아니한다. 국가의 세입·세출의 결산.외교사절을 신임·접수 또는 파견하며. 대통령은 법률이 정하는 바에 의하여 사면·감형 또는 복권을 명할 수 있다. 그 임기는 4년으로 하며, 국가는 농업 및 어업을 보호·육성하기 위하여 농·어촌종합개발과 그 지원등 필요한 계획을 수립·시행하여야 한다.군인은 현역을 면한 후가 아니면 국무총리로 임명될 수 없다. 대법원장의 임기는 6년으로 하며. 환경권의 내용과 행사에 관하여는 법률로 정한다, 대통령이 궐위되거나 사고로 인하여 직무를 수행할 수 없을 때에는 국무총리.'
    }
]

test_note_id = UUID("6a423db5-8a34-4153-9795-c6f058020445", version=4)

res = generate_pdf("test_title", test_pdf_pages, test_note_id)

with open("test.pdf", "wb") as f:
    f.write(res)
