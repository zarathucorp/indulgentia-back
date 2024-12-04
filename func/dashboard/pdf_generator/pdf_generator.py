from PIL import Image, UnidentifiedImageError
from pdfmerge import pdfmerge
from fpdf import FPDF, FontFace
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
import aiofiles
from markdown import markdown
from func.error.error import raise_custom_error
from datetime import datetime
import time
# from md2pdf.core import md2pdf
from markdown2 import markdown, markdown_path
from weasyprint import HTML, CSS


def custom_md2pdf(pdf_file_path, md_content=None, md_file_path=None,
                  css_file_path=None, base_url=None):
    """
    Converts input markdown to styled HTML and renders it to a PDF file.

    Args:
        pdf_file_path: output PDF file path.
        md_content: input markdown raw string content.
        md_file_path: input markdown file path.
        css_file_path: input styles path (CSS).
        base_url: absolute base path for markdown linked content (as images).

    Returns:
        None

    Raises:
        ValidationError: if md_content and md_file_path are empty.
    """
    class ValidationError(Exception):
        pass

    # Convert markdown to html
    raw_html = ''
    extras = ['cuddled-lists', 'tables', 'footnotes', 'fenced-code-blocks']
    if md_file_path:
        raw_html = markdown_path(md_file_path, extras=extras)
    elif md_content:
        raw_html = markdown(md_content, extras=extras)

    if not len(raw_html):
        raise ValidationError('Input markdown seems empty')

    # Weasyprint HTML object
    html = HTML(string=raw_html, base_url=base_url)
    print(raw_html)

    # Get styles
    css = []
    if css_file_path:
        css.append(CSS(filename=css_file_path))

    # Generate PDF
    html.write_pdf(pdf_file_path, stylesheets=css)

    return


def convert_doc_to_pdf(source_path: str, file_name: str, extension: str):
    try:
        subprocess.run(["libreoffice", "--headless", "--convert-to", "pdf",
                        f"{source_path}/input/{file_name}.{extension}", "--outdir", f"{source_path}/output"])
    except Exception as e:
        print(e)
        raise_custom_error(500, 420)
    return f"{file_name}.pdf"


def convert_markdown_to_pdf(source_path: str, file_name: str, extension: str):
    try:
        custom_md2pdf(pdf_file_path=f"{source_path}/output/{file_name}.pdf",
                      md_file_path=f"{source_path}/input/{file_name}.{extension}",
                      css_file_path=f"{source_path}/md2pdf.css"
                      )
        # subprocess.run(["md2pdf", "-e", "fenced-code-blocks",
        #                f"{source_path}/input/{file_name}.{extension}", f"{source_path}/output/{file_name}.pdf"])
    except Exception as e:
        print(e)
        raise_custom_error(500, 460)
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


def delete_old_files(directory_path):
    try:
        print(f"Deleting old files in {directory_path}")
        # Get the current time
        current_time = time.time()

        # Iterate over all files in the directory
        for filename in os.listdir(directory_path):
            if filename == ".gitignore":
                continue
            file_path = os.path.join(directory_path, filename)

            # If the file is a file (not a directory) and it was last modified more than 24 hours ago
            if os.path.isfile(file_path) and os.path.getmtime(file_path) < current_time - 24 * 60 * 60:
                # Delete the file
                os.remove(file_path)
    except OSError as e:
        print(e)
        raise_custom_error(500, 130)


def count_sections_and_split(markdown_content):
    # "##"의 위치를 찾아 리스트에 저장
    splits = [pos for pos in range(
        len(markdown_content)) if markdown_content.startswith("##", pos)]

    # 각 섹션이 4개의 "##"을 포함하도록 인덱스 계산
    split_indices = splits[4::4]  # 4개의 "##"마다 인덱스를 추출하여 섹션을 나눔

    # markdown_content를 섹션으로 나누기
    sections = []
    start = 0
    for index in split_indices:
        sections.append(markdown_content[start:index])
        start = index  # "##" 위치부터 시작
    sections.append(markdown_content[start:])  # 마지막 섹션 추가

    return sections


def create_intro_page(title: str, author: str, description: str | None, SOURCE_PATH: str, note_id: str, project_title: str, bucket_title, signature_url: str | None = None):
    # 마크다운 텍스트 크기 정보 (FPDF2)
    # h1 폰트 크기: 24
    # h1 y길이: 14
    # h1 1줄 글자수: 43
    #
    # h2 폰트 크기: 20
    # h2 y길이: 12
    # h2 1줄 글자수: 49
    #
    # h3 폰트 크기: 16
    # h3 y길이: 10.1
    # h3 1줄 글자수: 68 (61로 취급할 것)
    #
    # h4 폰트 크기: 14
    # h4 y길이: 9.1
    # h4 1줄 글자수: 61
    #
    # p 폰트 크기: 12
    # p y길이: 6.5
    # p 1줄 글자수: 98
    # code y길이: 6.5
    # table y길이: 11 / 줄
    # list y길이: 6.5 / 줄
    #
    # page height: 297
    # 타이틀 height: 40
    # 서명 height: 50
    # 가용 height: 200 가정 (실제값 207)

    try:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=False, margin=5)

        date = datetime.now().strftime("%Y-%m-%d")
        date_kor = datetime.now().strftime("%Y년 %m월 %d일")
        pdf.add_page()

        pdf.add_font("Pretendard", style="",
                     fname=f"{SOURCE_PATH}/Pretendard-Regular.ttf")
        pdf.add_font("Pretendard", style="B",
                     fname=f"{SOURCE_PATH}/Pretendard-Bold.ttf")
        pdf.add_font("PretendardB", style="",
                     fname=f"{SOURCE_PATH}/Pretendard-Bold.ttf")

        pdf.set_font("Pretendard", size=24)
        pdf.cell(200, 10, text=title, ln=True, align='C')
        pdf.set_y(pdf.get_y()+10)
        pdf.line(0, pdf.get_y(), pdf.w, pdf.get_y())

        pdf.set_y(pdf.get_y())
        pdf.set_font_size(12)
        pdf.cell(200, 10, text="Description", ln=True, align='L')

        if description:
            html_intro = markdown(
                description, extensions=['fenced_code', 'markdown.extensions.tables'])
            # <hr /> 태그를 수평선으로 변환하기 위해 리스트로 변환
            html_intro = re.sub(r"<hr\s*/?>", "<hr>", html_intro)
            print("html_intro", html_intro)
            print("line break count", html_intro.count("\n"))
            html_intro_list = html_intro.split(r"<hr>")

            for html in html_intro_list:
                pdf.write_html(html, tag_styles={
                    # "h1": FontFace(family="PretendardB", color=(0, 0, 0), size_pt=24),
                    "h1": FontFace(family="PretendardB", color=(0, 0, 0), size_pt=20),
                    # "h2": FontFace(family="PretendardB", color=(0, 0, 0), size_pt=20),
                    "h2": FontFace(family="PretendardB", color=(0, 0, 0), size_pt=18),
                    "h3": FontFace(family="PretendardB", color=(0, 0, 0), size_pt=16),
                    "h4": FontFace(family="PretendardB", color=(0, 0, 0), size_pt=14),
                    "a": FontFace(family="Pretendard", color=(0, 0, 255), emphasis=None),
                    "code": FontFace(family="Pretendard", color=(120, 120, 120), size_pt=12),
                }, li_prefix_color=(0, 0, 0), ul_bullet_char=u"\u2022")
                if html != html_intro_list[-1]:
                    x1, y1, x2, y2 = pdf.get_x(), pdf.get_y() + 2, pdf.w - 10, pdf.get_y() + 2
                    pdf.line(x1, y1, x2, y2)

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
    MARKDOWN_EXTENSIONS = ["md", "markdown"]
    AVAILABLE_EXTENSIONS = DOC_EXTENSIONS + \
        IMAGE_EXTENSIONS + MARKDOWN_EXTENSIONS + ["pdf"]
    A4_SIZE = (595, 842)

    # delete old files
    delete_old_files(f"{SOURCE_PATH}/input")
    delete_old_files(f"{SOURCE_PATH}/output")

    # Intro PDF
    create_intro_page(title, username, description,
                      SOURCE_PATH, note_id, project_title, bucket_title, signature_url)

    async def process_file(file: UploadFile, idx: int, note_id: str, contents: List[Union[bytes, None]], SOURCE_PATH: str):
        extension = file.filename.split(".")[-1]
        filename = f"{note_id}_{idx}"
        try:
            # 비동기 파일 처리
            async with aiofiles.open(f"{SOURCE_PATH}/input/{filename}.{extension}", 'wb') as f:
                await f.write(contents[idx])
                print(f"{SOURCE_PATH}/input/{filename}.{extension} saved")

            # PIL은 비동기 지원 안됨
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
            elif extension in MARKDOWN_EXTENSIONS:
                res = convert_markdown_to_pdf(SOURCE_PATH, filename, extension)
                print(f"{SOURCE_PATH}/output/{res} saved")
            else:
                # Copy PDF file asynchronously
                async with aiofiles.open(f"{SOURCE_PATH}/output/{filename}.{extension}", 'wb') as f:
                    await f.write(contents[idx])
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
            raise_custom_error(422, 240)

        # 소요시간 측정
        # start = time.time()
        # print("start time", start)
        tasks = [process_file(file, idx, note_id, contents, SOURCE_PATH)
                 for idx, file in enumerate(files)]
        await asyncio.gather(*tasks)
        # end = time.time()
        # print("end_time", end)
        # print("time elapsed", end - start)

    # merge pdfs
    try:
        pdfs = [f"{SOURCE_PATH}/output/{note_id}_intro.pdf"]
        if files:
            pdfs += [
                f"{SOURCE_PATH}/output/{note_id}_{idx}.pdf" for idx in range(len(files))]
        print(pdfs)
        pdfmerge(pdfs, f"{SOURCE_PATH}/output/{note_id}.pdf")
        print(f"{SOURCE_PATH}/output/{note_id}.pdf saved")
    except Exception as e:
        print(e)
        raise_custom_error(500, 440)

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


async def generate_pdf_using_markdown(note_id: str, markdown_content: str, project_title: str, bucket_title: str, author: str, signature_url: str | None = None):
    from datetime import datetime
    from fpdf import HTMLMixin
    SOURCE_PATH = "func/dashboard/pdf_generator"

    # delete old files
    delete_old_files(f"{SOURCE_PATH}/input")
    delete_old_files(f"{SOURCE_PATH}/output")

    markdown_content_sections = count_sections_and_split(markdown_content)
    section_count = len(markdown_content_sections)

    try:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=5)

        date = datetime.now().strftime("%Y-%m-%d")
        date_kor = datetime.now().strftime("%Y년 %m월 %d일")
        pdf.add_page()

        pdf.add_font("Pretendard", style="",
                     fname=f"{SOURCE_PATH}/Pretendard-Regular.ttf")
        pdf.add_font("Pretendard", style="B",
                     fname=f"{SOURCE_PATH}/Pretendard-Bold.ttf")
        pdf.add_font("PretendardB", style="",
                     fname=f"{SOURCE_PATH}/Pretendard-Bold.ttf")
        pdf.set_font("Pretendard", size=16)

        html_intro = markdown(
            markdown_content_sections[0], extensions=['fenced_code'])
        # pdf.multi_cell(w=200, text=markdown_content, markdown=True)
        pdf.write_html(html_intro, tag_styles={
            "h1": FontFace(family="PretendardB", color=(0, 0, 0), size_pt=24),
            "h2": FontFace(family="PretendardB", color=(0, 0, 0), size_pt=20),
            "a": FontFace(family="Pretendard", color=(0, 0, 255), emphasis=None),
            "code": FontFace(family="Pretendard", color=(120, 120, 120), size_pt=12),
        }, li_prefix_color=(0, 0, 0), ul_bullet_char=u"\u2022")

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

        if section_count > 1:
            for section in markdown_content_sections[1:]:
                pdf.add_page()
                pdf.set_text_color(0, 0, 0)
                pdf.set_font_size(16)
                html_section = markdown(section, extensions=['fenced_code'])
                pdf.write_html(html_section, tag_styles={
                    "h1": FontFace(family="PretendardB", color=(0, 0, 0), size_pt=24),
                    "h2": FontFace(family="PretendardB", color=(0, 0, 0), size_pt=20),
                    "a": FontFace(family="Pretendard", color=(0, 0, 255), emphasis=None),
                    "code": FontFace(family="Pretendard", color=(120, 120, 120), size_pt=12),
                }, li_prefix_color=(0, 0, 0), ul_bullet_char=u"\u2022")

        res = pdf.output()
    except Exception as e:
        print(e)
        raise_custom_error(500, 410)
    try:
        with open(f"{SOURCE_PATH}/output/{note_id}.pdf", 'wb') as f:
            f.write(res)
            print(f"{SOURCE_PATH}/output/{note_id}.pdf saved")
    except Exception as e:
        print(e)
        raise_custom_error(500, 110)

    return f"{SOURCE_PATH}/output/{note_id}"
