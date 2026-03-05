from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from io import BytesIO

def generate_report(name, disease, risk, level, diet, lifestyle):

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("<b>AI Clinical Risk Report</b>", styles["Heading1"]))
    elements.append(Spacer(1, 0.3 * inch))

    data = [
        ["Patient Name", name],
        ["Disease", disease],
        ["Risk %", str(risk)],
        ["Risk Level", level],
        ["Diet Advice", diet],
        ["Lifestyle Advice", lifestyle]
    ]

    table = Table(data)
    elements.append(table)

    doc.build(elements)

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes