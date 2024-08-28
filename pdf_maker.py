# pdf_generator.py
from fpdf import FPDF
import logging
import os

logger = logging.getLogger(__name__)

def generate_pdf(data, pdf_filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Add title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="User Data Report", ln=True, align='C')
    pdf.ln(10)  # Line break

    # Example content
    for i in range(1, 15):
        pdf.cell(0, 10, f"This is line {i}: so", ln=1)

    # Ensure PDF folder exists
    pdf_folder = 'pdfs'
    os.makedirs(pdf_folder, exist_ok=True)

    # Define the PDF path
    pdf_path = os.path.join(pdf_folder, os.path.splitext(pdf_filename)[0] + ".pdf")
    pdf.output(pdf_path)  # Save PDF to the defined path
    logger.info(f"PDF generated: {pdf_path}")
    
    return pdf_path  # Return the path of the generated PDF
