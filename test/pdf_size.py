from fpdf import FPDF, FontFace
from markdown import markdown

SOURCE_PATH = "/home/koolerjaebee/projects/indulgentia-back/func/dashboard/pdf_generator"

pdf = FPDF()
pdf.add_page()

pdf.add_font("Pretendard", style="",
             fname=f"{SOURCE_PATH}/Pretendard-Regular.ttf")
pdf.add_font("Pretendard", style="B",
             fname=f"{SOURCE_PATH}/Pretendard-Bold.ttf")
pdf.add_font("PretendardB", style="",
             fname=f"{SOURCE_PATH}/Pretendard-Bold.ttf")

pdf.set_font("Pretendard", size=24)
pdf.cell(200, 10, text="Title", ln=True, align='C')
pdf.set_y(pdf.get_y()+10)
pdf.line(0, pdf.get_y(), pdf.w, pdf.get_y())

pdf.set_y(pdf.get_y())
pdf.set_font_size(12)
pdf.cell(200, 10, text="Description", ln=True, align='L')

print("page height : ", pdf.h)
print("current y : ", pdf.get_y())

variables = {
    "h1_text": "# This is a header This is a header This is a header This is a header This is a header",
    "h2_text": "## This is a subheader This is a subheader This is a subheader This is a subheader This is a subheader",
    "h3_text": "### This is a subsubheader This is a subsubheader This is a subsubheader This is a subsubheader This is a subsubheader",
    "h4_text": "#### This is a subsubsubheader This is a subsubsubheader This is a subsubsubheader This is a subsubsubheader This is a subsubsubheader",
    "p_text": "This is a paragraph This is a paragraph This is a paragraph This is a paragraph This is a paragraph This is a paragraph This is a paragraph ",
    "a_text": "[This is a link](https://www.google.com)",
    "code_text": "```python\nprint('Hello, World!')\n```",
    "table_text": "| Header 1 | Header 2 |\n| -------- | -------- |\n| Data 1 | Data 2 |",
    "list_text": "- Item 1\n- Item 2\n- Item 3",
}

# calculate y


def test_html(variables, var):
    pdf = FPDF()
    pdf.add_page()

    pdf.add_font("Pretendard", style="",
                 fname=f"{SOURCE_PATH}/Pretendard-Regular.ttf")
    pdf.add_font("Pretendard", style="B",
                 fname=f"{SOURCE_PATH}/Pretendard-Bold.ttf")
    pdf.add_font("PretendardB", style="",
                 fname=f"{SOURCE_PATH}/Pretendard-Bold.ttf")
    pdf.set_font("Pretendard", size=12)

    print("-"*50)
    before_y = pdf.get_y()
    print("before y :", before_y)
    html = markdown(variables.get(var), extensions=[
                    'fenced_code', 'markdown.extensions.tables'])
    p_html = markdown(variables.get("p_text"), extensions=[
        'fenced_code', 'markdown.extensions.tables'])
    pdf.write_html(html, tag_styles={
        "h1": FontFace(family="PretendardB", color=(0, 0, 0), size_pt=24),
        "h2": FontFace(family="PretendardB", color=(0, 0, 0), size_pt=20),
        "h3": FontFace(family="PretendardB", color=(0, 0, 0), size_pt=16),
        "h4": FontFace(family="PretendardB", color=(0, 0, 0), size_pt=14),
        "a": FontFace(family="Pretendard", color=(0, 0, 255), emphasis=None),
        "code": FontFace(family="Pretendard", color=(120, 120, 120), size_pt=12),
    }, li_prefix_color=(0, 0, 0), ul_bullet_char=u"\u2022")

    pdf.write_html(p_html, tag_styles={
        "h1": FontFace(family="PretendardB", color=(0, 0, 0), size_pt=24),
        "h2": FontFace(family="PretendardB", color=(0, 0, 0), size_pt=20),
        "h3": FontFace(family="PretendardB", color=(0, 0, 0), size_pt=16),
        "h4": FontFace(family="PretendardB", color=(0, 0, 0), size_pt=14),
        "a": FontFace(family="Pretendard", color=(0, 0, 255), emphasis=None),
        "code": FontFace(family="Pretendard", color=(120, 120, 120), size_pt=12),
    }, li_prefix_color=(0, 0, 0), ul_bullet_char=u"\u2022")

    after_y = pdf.get_y()
    print("after y :", after_y)
    print(var, "y size :", after_y - before_y)
    print("real", var, "y size :", after_y - before_y - 6.35)
    res = pdf.output()
    with open(f"/home/koolerjaebee/projects/indulgentia-back/test/{var}.pdf", "wb") as f:
        f.write(res)


for var in variables:
    test_html(variables, var)

"""
결과 값

page height :  297.0000833333333
current y :  9.999999999999998

--------------------------------------------------

before y : 9.999999999999998
after y : 30.319999999999993
h1_text y size : 20.319999999999993
real h1_text y size : 13.969999999999994

--------------------------------------------------

before y : 9.999999999999998
after y : 28.34444444444444
h2_text y size : 18.34444444444444
real h2_text y size : 11.994444444444442

--------------------------------------------------

before y : 9.999999999999998
after y : 26.36888888888889
h3_text y size : 16.36888888888889
real h3_text y size : 10.01888888888889

--------------------------------------------------

before y : 9.999999999999998
after y : 25.38111111111111
h4_text y size : 15.381111111111112
real h4_text y size : 9.031111111111112

--------------------------------------------------

before y : 9.999999999999998
after y : 22.699999999999996
p_text y size : 12.699999999999998
real p_text y size : 6.349999999999998

--------------------------------------------------

before y : 9.999999999999998
after y : 22.699999999999996
a_text y size : 12.699999999999998
real a_text y size : 6.349999999999998

--------------------------------------------------

before y : 9.999999999999998
after y : 22.699999999999996
code_text y size : 12.699999999999998
real code_text y size : 6.349999999999998

--------------------------------------------------

before y : 9.999999999999998
after y : 37.94
table_text y size : 27.939999999999998
real table_text y size : 21.589999999999996

--------------------------------------------------

before y : 9.999999999999998
after y : 33.166666666666664
list_text y size : 23.166666666666664
real list_text y size : 16.816666666666663
"""
