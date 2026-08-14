"""Generates the downloadable certificate PDF (section 11: 'Certificate PDF
generator'). Kept in its own module so the visual layout can evolve without
touching the model.
"""
from io import BytesIO

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

NAVY = HexColor("#1F3A6E")
TEAL = HexColor("#17C1C8")
HEADER_NAVY = HexColor("#0D2B4E")
INK_SOFT = HexColor("#55677F")


def build_certificate_pdf(certificate) -> bytes:
    buffer = BytesIO()
    width, height = landscape(A4)
    c = canvas.Canvas(buffer, pagesize=(width, height))

    # Background + double border frame
    c.setFillColor(white)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    c.setStrokeColor(NAVY)
    c.setLineWidth(3)
    c.rect(14 * mm, 14 * mm, width - 28 * mm, height - 28 * mm, fill=0, stroke=1)
    c.setStrokeColor(TEAL)
    c.setLineWidth(1)
    c.rect(18 * mm, 18 * mm, width - 36 * mm, height - 36 * mm, fill=0, stroke=1)

    # Header band
    c.setFillColor(HEADER_NAVY)
    c.rect(0, height - 26 * mm, width, 26 * mm, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 16 * mm, "i-CODE ROBOTICS & AI LAB")
    c.setFont("Helvetica", 9)
    c.drawCentredString(width / 2, height - 21.5 * mm, "icodeailab.com")

    # Title — uses the programme's configured certificate name if set
    # (Program.certificate_name), else the generic certificate type label.
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(width / 2, height - 55 * mm, certificate.display_title.upper())

    c.setFillColor(INK_SOFT)
    c.setFont("Helvetica", 13)
    c.drawCentredString(width / 2, height - 68 * mm, "This certifies that")

    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(width / 2, height - 82 * mm, certificate.name)

    level = certificate.effective_level
    c.setFillColor(INK_SOFT)
    c.setFont("Helvetica", 13)
    level_phrase = f"has successfully completed the {level.name} level of" if level else "has successfully completed"
    c.drawCentredString(width / 2, height - 94 * mm, level_phrase)

    c.setFillColor(TEAL)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, height - 104 * mm, str(certificate.program))

    c.setFillColor(INK_SOFT)
    c.setFont("Helvetica", 11)
    c.drawCentredString(
        width / 2, height - 116 * mm,
        f"Completed {certificate.completion_date:%d %B %Y}   ·   Issued {certificate.issue_date:%d %B %Y}",
    )

    # Certificate ID + verification hint (bottom left)
    c.setFont("Courier-Bold", 11)
    c.setFillColor(NAVY)
    c.drawString(26 * mm, 26 * mm, f"Certificate ID: {certificate.certificate_id}")
    c.setFont("Helvetica", 8)
    c.setFillColor(INK_SOFT)
    c.drawString(26 * mm, 21 * mm, "Verify at icodeailab.com/verify or scan the QR code")

    # QR code (bottom right) — only embedded if it's already been generated
    if certificate.qr_code:
        try:
            certificate.qr_code.open("rb")
            qr_img = ImageReader(certificate.qr_code)
            qr_size = 26 * mm
            c.drawImage(
                qr_img, width - 26 * mm - qr_size, 20 * mm, qr_size, qr_size,
                preserveAspectRatio=True, mask="auto",
            )
        finally:
            certificate.qr_code.close()

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()