from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Image, Table, TableStyle, Spacer
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import utils


def get_image_flowable(path, width):
    img_reader = utils.ImageReader(path)
    iw, ih = img_reader.getSize()
    aspect = ih / float(iw)
    return Image(path, width=width, height=(width * aspect))


def create_storybook_pdf(pages, title="My Storybook", output_file="storybook.pdf"):
    doc = SimpleDocTemplate(output_file, pagesize=landscape(A4))
    elements = []
    styles = getSampleStyleSheet()

    # Custom title style
    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        fontSize=36,
        leading=42,
        alignment=1,  # center
        spaceAfter=40
    )

    story_style = styles["Normal"]
    story_style.fontSize = 14
    story_style.leading = 18

    # --- First page: Title only ---
    elements.append(Spacer(1, 200))  # push title down a bit
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 100))

    # --- Remaining pages ---
    for page in pages:
        img = get_image_flowable(page["image"], width=350)
        txt = Paragraph(page["text"], story_style)
        table = Table([[img, txt]], colWidths=[370, 420])
        table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 20),
            ("RIGHTPADDING", (0, 0), (-1, -1), 20),
        ]))
        elements.append(table)

    doc.build(elements)
    return f"✅ PDF saved to {output_file}"
pages = [
    {"image": "image_chapter_1.png", "text": "Deep in a meadow lived a bee named Mellie..."},
    {"image": "image_chapter_2.png", "text": "Mellie watched her sisters zoom off..."},
]

# create_storybook_pdf(pages, output_file="storybook222.pdf", title="Mellie the Helpful Bee")
