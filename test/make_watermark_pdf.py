##!/usr/bin/env python3
# Author: Björn Seipel
# License: MIT
# Tested with fpdf 2.7.5, Pillow 9.1.0, Python 3.8.10

from random import randint
from fpdf import FPDF


class PDFMark(FPDF):

    _watermark_data = []
    _stamp_data = []

    def watermark(self, text, x=None, y=None, angle=45, alpha=1, text_color=[200, 200, 200], font='Pretendard', font_size=50, font_style=''):
        self._watermark_data = [text, x, y, angle,
                                alpha, text_color, font, font_size, font_style]

    def stamp(self, text, x=None, y=None, angle=45, alpha=1, text_color=[255, 0, 0], font='Pretendard', font_size=50, font_style=''):
        self._stamp_data = [text, x, y, angle, alpha,
                            text_color, font, font_size, font_style]

    def _mark(self, text_data):

        if len(text_data) != 0 and len(text_data[0]) != 0:

            with pdf.local_context(fill_opacity=text_data[4], text_color=text_data[5], font_family=text_data[6], font_style=text_data[8], font_size=text_data[7]):
                text = text_data[0]
                stringWidth = self.get_string_width(text)/2
                x, y = text_data[1], text_data[2]

                if x == None:
                    x = self.w/2-stringWidth
                if y == None:
                    y = self.h/2

                # rotate and print text
                with self.rotation(text_data[3], x+stringWidth, y):
                    self.text(x, y, text)

    def header(self):
        super().header()
        self._mark(self._watermark_data)

    def footer(self):
        super().footer()
        self._mark(self._stamp_data)

#!/usr/bin/env python3


# some random text to fill the pages


def textlines(pdf, lines):
    loremIpsum = ''
    for x in range(0, lines):
        pdf.cell(180, 5, loremIpsum)
        pdf.ln()


pdf = PDFMark()

SOURCE_PATH = "/home/koolerjaebee/projects/indulgentia-back/func/dashboard/pdf_generator"
pdf.add_font("Pretendard", style="",
             fname=f"{SOURCE_PATH}/Pretendard-Regular.ttf")
pdf.add_font("Pretendard", style="B",
             fname=f"{SOURCE_PATH}/Pretendard-Bold.ttf")
pdf.add_font("PretendardB", style="",
             fname=f"{SOURCE_PATH}/Pretendard-Bold.ttf")
pdf.set_font("Pretendard")

# set stamp prior to calling add_page()
pdf.stamp('Preview', y=50, angle=10, font_size=60, font_style='B')
# set watermark prior to calling add_page()
pdf.watermark('연구실록 - 차라투', font_style='B')

pdf.add_page()

# pdf.set_font("Pretendard", "B", size=12)
# # pdf.set_font('Helvetica', 'B', 12)
# textlines(pdf, 50)

# pdf.add_page()
# pdf.set_text_color(0, 0, 255)
# pdf.set_font("Pretendard", size=12)
# # pdf.set_font('Helvetica', 'I', 12)
# textlines(pdf, 30)
# # change watermark for all pages that follow (pass empty string to stop printing watermarks)
# pdf.watermark('New Watermark', angle=0, text_color=[
#               255, 255, 50], font='Pretendard', font_style='B')

# pdf.add_page()
# # change stamp for this page and all that follow (pass empty string to stop printing stamps)
# pdf.stamp('NOT APPROVED!', alpha=0.5, angle=10, font_size=60, font_style='B')
# pdf.set_text_color(0, 255, 255)
# pdf.set_font('Pretendard', 'B', 12)
# textlines(pdf, 50)

res = pdf.output()
with open(f"/home/koolerjaebee/projects/indulgentia-back/test/watermark.pdf", "wb") as f:
    f.write(res)
