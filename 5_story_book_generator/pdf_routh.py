
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import utils

def get_image_flowable(path, width):
    img_reader = utils.ImageReader(path)
    iw, ih = img_reader.getSize()
    aspect = ih / float(iw)
    return Image(path, width=width, height=(width * aspect))

def create_storybook_pdf(pages, output_file="storybook.pdf"):
    doc = SimpleDocTemplate(output_file, pagesize=landscape(A4))
    elements = []
    styles = getSampleStyleSheet()
    story_style = styles["Normal"]
    story_style.fontSize = 14
    story_style.leading = 18

    for page in pages:
        img = get_image_flowable(page["image"], width=350)
        txt = Paragraph(page["text"], story_style)
        table = Table([[img, txt]], colWidths=[370, 420])
        table.setStyle(TableStyle([
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("LEFTPADDING", (0,0), (-1,-1), 20),
            ("RIGHTPADDING", (0,0), (-1,-1), 20),
        ]))
        elements.append(table)

    doc.build(elements)
    return f"✅ PDF saved to {output_file}"
    



