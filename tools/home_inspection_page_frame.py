"""A restrained common frame for assembled property-review packets.

The page body is outside this renderer. Card format, signals, writing space,
images and evidence remain owned by their source renderers. This is a local
print profile; it does not admit a new BBDF brand or global template.
"""
from io import BytesIO
from pathlib import Path
import sys
import json

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing

sys.path.insert(0, str(Path(__file__).resolve().parent))
import team_paths
TOKENS = team_paths.brand('tokens')

def print_palette():
    # Read the canonical print tokens directly; no screen, filing or DB side effects.
    data=json.loads((TOKENS/'palette.json').read_text(encoding='utf-8-sig'))
    return {'navy':data['color']['navy']['primary']['$value']}


def frame(width, height, *, address, section, page, total, title=None,
          subtitle=None, logo=None, crab=None, cards=False):
    navy = HexColor(print_palette()['navy'])
    ink = navy
    margin = 36
    out = BytesIO()
    c = Canvas(out, pagesize=(width, height), invariant=1)
    c.setStrokeColor(navy)
    c.setLineWidth(1.5)
    c.line(margin, height - 20, width - margin, height - 20)
    c.setFillColor(navy)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(margin, height - 35, f'BEN-BALL / {address.upper()} / {section.upper()}')
    if logo:
        mark_height = 24 if cards else 38
        mark_width = mark_height * 289 / 655
        drawing = Drawing(width, height)
        logo(drawing, width-margin-mark_width, height-(50 if cards else 73), mark_width)
        renderPDF.draw(drawing, c, 0, 0)
    if not cards:
        assert title and subtitle
        c.setFont('Helvetica-Bold', 24)
        assert c.stringWidth(title, 'Helvetica-Bold', 24) <= width - 2 * margin
        c.drawString(margin, height - 68, title)
        style = ParagraphStyle('property-subtitle', fontName='Helvetica', fontSize=10.5,
                               leading=12, textColor=ink)
        p = Paragraph(subtitle, style)
        _, ph = p.wrap(width-2*margin, 30)
        assert ph <= 24
        p.drawOn(c, margin, height-85-ph)
        c.setStrokeColor(navy)
        c.line(margin, height - 118, width - margin, height - 118)
        if crab:
            crab(c, width-110, height-38, 15)
            c.setFillColor(HexColor('#007A9E'))
            c.setFont('Helvetica-Bold', 8)
            c.drawString(width-91, height-35, 'MD')

    c.setStrokeColor(navy)
    c.setLineWidth(1)
    c.line(margin, 36, width-margin, 36)
    c.setFillColor(ink)
    c.setFont('Helvetica', 8.5)
    if cards:
        c.setLineWidth(.75)
        c.line(margin, 26, margin+72, 26)
        c.drawString(margin+79, 23, '1 inch / Actual size / single-sided')
        c.drawString(355, 23, f'{address.upper()} / FIELD CARDS')
    else:
        c.drawString(margin, 23, f'{address.upper()} / DESKTOP PREPARATION')
        c.drawString(300, 23, section.upper())
    c.setFont('Helvetica-Bold', 8.5)
    label = f'{page} / {total}'
    c.drawRightString(width-margin, 23, label)
    c.showPage()
    c.save()
    return out.getvalue()
