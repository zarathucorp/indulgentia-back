from io import BytesIO
from pyhanko.keys import load_cert_from_pemder
from pyhanko_certvalidator import ValidationContext
from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.sign.validation import validate_pdf_signature
from fastapi import UploadFile, File

root_cert = load_cert_from_pemder('cert/certificate.crt')
vc = ValidationContext(trust_roots=[root_cert])


# def verify_pdf(note_id: str) -> bool:
#     '''
#     제시된 note_id에 해당하는 pdf 파일 서명

#     :param note_id: 서명할 pdf 파일의 UUID

#     :return: 서명이 유효한지 여부
#     '''
#     with open(f'{note_id}.pdf', 'rb') as doc:
#         r = PdfFileReader(doc)
#         sig = r.embedded_signatures[0]
#         status = validate_pdf_signature(sig, vc)
#         return status.bottom_line


def verify_pdf(file_contents: bytes) -> bool:
    '''
    제시된 pdf 파일 서명

    :param file: 서명할 pdf 파일

    :return: 서명이 유효한지 여부
    '''
    r = PdfFileReader(BytesIO(file_contents))
    sig = r.embedded_signatures[0]
    status = validate_pdf_signature(sig, vc)
    return status.bottom_line
