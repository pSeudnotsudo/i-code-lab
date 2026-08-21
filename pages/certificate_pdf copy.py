from io import BytesIO
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = BASE_DIR / "templates_pdf" / "certificate_template.pdf"
FONTS_DIR = BASE_DIR / "fonts"

NAVY = HexColor("#1F3A6E")
TEAL = HexColor("#17C1C8")
GOLD = HexColor("#D4A017")
INK_SOFT = HexColor("#2B2B2B")

# ---------------------------------------------------------------------
# Font registration
# - Montserrat ExtraBold  -> recipient name + certificate title
# - Poppins Regular/Medium -> supporting text (course, dates, cred. ID label)
# - Courier New (reportlab's built-in "Courier" IS Courier New's metric
#   equivalent on every platform, so no ttf needed for that one)
#
# Drop the .ttf files into fonts/ with these exact names, or adjust the
# paths below to match whatever you actually downloaded:
#   fonts/Montserrat-ExtraBold.ttf
#   fonts/Poppins-Regular.ttf
#   fonts/Poppins-Medium.ttf
# ---------------------------------------------------------------------

def _register(font_name, filename, fallback):
    try:
        pdfmetrics.registerFont(TTFont(font_name, str(FONTS_DIR / filename)))
        return font_name
    except Exception:
        return fallback


TITLE_FONT = _register("MontserratExtraBold", "Montserrat-ExtraBold.ttf", "Helvetica-Bold")
NAME_FONT = _register("MontserratExtraBold", "Montserrat-ExtraBold.ttf", "Helvetica-Bold")
BODY_FONT_REGULAR = _register("PoppinsRegular", "Poppins-Regular.ttf", "Helvetica")
BODY_FONT_MEDIUM = _register("PoppinsMedium", "Poppins-Medium.ttf", "Helvetica-Bold")


def ordinal(n: int) -> str:
    if 11 <= n % 100 <= 13:
        return f"{n}th"
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def build_certificate_pdf(certificate) -> bytes:
    template_reader = PdfReader(str(TEMPLATE_PATH))
    template_page = template_reader.pages[0]
    width = float(template_page.mediabox.width)
    height = float(template_page.mediabox.height)

    def from_top(pt):
        return height - pt

    overlay_buffer = BytesIO()
    c = canvas.Canvas(overlay_buffer, pagesize=(width, height))

    # ---------- Title ----------
    c.setFillColor(NAVY)
    c.setFont(TITLE_FONT, 26)
    c.drawCentredString(width / 2, from_top(190), "CERTIFICATE OF COMPLETION")

    # ---------- Subtitle ----------
    c.setFillColor(HexColor("#E0A030"))
    c.setFont(BODY_FONT_MEDIUM, 11)
    c.drawCentredString(width / 2, from_top(210), "3 - WEEK INNOVATION BOOTCAMP")

    # ---------- Divider ----------
    c.setStrokeColor(TEAL)
    c.setLineWidth(1.5)
    c.line(width / 2 - 55, from_top(220), width / 2 + 55, from_top(220))

    # ---------- "This certificate is proudly presented to" ----------
    c.setFillColor(INK_SOFT)
    c.setFont(BODY_FONT_REGULAR, 12)
    c.drawCentredString(width / 2, from_top(245), "This certificate is proudly presented to")

    # ---------- Gold line + name on top of it ----------
    line_y = from_top(290)
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.2)
    c.line(width / 2 - 180, line_y, width / 2 + 180, line_y)

    c.setFillColor(NAVY)
    c.setFont(NAME_FONT, 26)
    c.drawCentredString(width / 2, line_y + 8, certificate.name.upper())

    # ---------- Paragraph (course name, dates -> Poppins Regular) ----------
    para_lines = [
        "for successfully completing a 3 week bootcamp program at I-CODE Robotics & AI Lab, demonstrating",
        f"dedication, curiosity, and hands-on innovation in the field of {certificate.program},",
        f"held from {ordinal(certificate.completion_date.day)} {certificate.completion_date:%B} to "
        f"{ordinal(certificate.issue_date.day)} {certificate.issue_date:%B, %Y}.",
    ]
    c.setFont(BODY_FONT_REGULAR, 11)
    c.setFillColor(INK_SOFT)
    for i, line in enumerate(para_lines):
        c.drawCentredString(width / 2, from_top(320 + i * 18), line)

    # ---------- QR code (on top) ----------
    if certificate.qr_code:
        try:
            certificate.qr_code.open("rb")
            qr_img = ImageReader(certificate.qr_code)
            qr_size = 55
            qr_y = from_top(535)
            c.drawImage(
                qr_img,
                width / 2 - qr_size / 2, qr_y,
                qr_size, qr_size,
                preserveAspectRatio=True, mask="auto",
            )
        finally:
            certificate.qr_code.close()

    # ---------- Certificate ID (Courier New, just below the QR code) ----------
    c.setFont("Courier-Bold", 9)
    c.setFillColor(NAVY)
    c.drawCentredString(width / 2, from_top(545), f"{certificate.certificate_id}")

    c.showPage()
    c.save()
    overlay_buffer.seek(0)

    overlay_reader = PdfReader(overlay_buffer)
    template_page.merge_page(overlay_reader.pages[0])

    writer = PdfWriter()
    writer.add_page(template_page)

    output_buffer = BytesIO()
    writer.write(output_buffer)
    output_buffer.seek(0)
    return output_buffer.getvalue()