# pdf_generator.py
from fpdf import FPDF
import logging

logger = logging.getLogger(__name__)

def generate_pdf(data, pdf_filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Add title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="User Data Report", ln=True, align='C')
    pdf.ln(10)  # Line break

    ## Add table header
    #pdf.set_font("Arial", 'B', 12)
    #for header in data[0].keys():
    #    pdf.cell(40, 10, header, border=1)
    #pdf.ln()  # Line break
#
    ## Add table rows
    #pdf.set_font("Arial", size=12)
    #for row in data:
    #    for value in row.values():
    #        pdf.cell(40, 10, str(value), border=1)
    #    pdf.ln()  # Line break

    for i in range(1,15):
        pdf.cell(0, 10, f"This is line{i} :so", ln=1) 
    # Save PDF to file
    pdf.output(pdf_filename)
    logger.info(f"PDF generated: {pdf_filename}")
