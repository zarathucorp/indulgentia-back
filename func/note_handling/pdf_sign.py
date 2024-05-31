from pyhanko import stamp
from pyhanko.pdf_utils import text, images
from pyhanko.pdf_utils.font import opentype
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign import fields, signers

signer = signers.SimpleSigner.load(
    # 회사에서 자체 서명한 인증서
    'cert/private.key', 'cert/certificate.crt',
)


async def sign_pdf(note_id: str):
    '''
    제시된 note_id에 해당하는 pdf 파일 서명

    :param note_id: 서명할 pdf 파일의 UUID
    '''
    with open(f'{note_id}.pdf', 'rb') as inf:
        w = IncrementalPdfFileWriter(inf)
        fields.append_signature_field(
            w, sig_field_spec=fields.SigFieldSpec(
                'Signature', box=(0, 100, 100, 0)
            )
        )

        meta = signers.PdfSignatureMetadata(field_name='Signature')
        pdf_signer = signers.PdfSigner(
            meta, signer=signer, stamp_style=stamp.TextStampStyle(
                # the 'signer' and 'ts' parameters will be interpolated by pyHanko, if present
                stamp_text='RNDSillog Certificated Note\nSigned by: %(signer)s\nTime: %(ts)s',
                text_box_style=text.TextBoxStyle(
                    font=opentype.GlyphAccumulatorFactory(
                        'func/note_handling/NotoSans_Condensed-Regular.ttf')
                ),
                background=images.PdfImage('func/note_handling/logo.png')
            ),
        )
        with open(f'{note_id}_signed.pdf', 'wb') as outf:
            await pdf_signer.async_sign_pdf(w, output=outf)
