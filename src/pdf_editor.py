from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PyPDF2 import PdfWriter, PdfReader
from reportlab.lib import colors
from datetime import datetime
import os
import logging


def add_text_to_pdf(input_pdf, output_pdf, signature_path, personal_info, result):
    """Adds text and images to a PDF and saves it as a new file."""
    temp_pdf_path = "temp_overlay.pdf"

    try:
        # Create overlay
        c = canvas.Canvas(temp_pdf_path, pagesize=letter)
        width, height = letter

        # Page 1
        c.setFont("Helvetica", 8.5)
        c.drawString(275, height - 67, result["dates"][0].strftime("%m  %y"))  # Month 1
        c.drawString(385, height - 67, result["dates"][1].strftime("%m  %y"))  # Month 2

        c.setFont("Helvetica", 9.5)
        c.setStrokeColor(colors.red)
        c.setLineWidth(1.5)
        c.line(310, height - 90, 430, height - 90)
        c.line(310, height - 102, 425, height - 102)

        c.drawString(302, height - 137, personal_info['national_id_number'])  # National number
        c.drawString(302, height - 149, f"{personal_info['first_name']} {personal_info['last_name']}")  # Name
        c.drawString(302, height - 171, personal_info['address_line_1'])  # Address 1
        c.drawString(302, height - 183, personal_info['address_line_2'])  # Address 2

        c.setFont("Helvetica", 11)
        c.drawString(235, height - 255, str(result['etfs']['total_transactions']))  # ETF Transactions
        c.drawString(355, height - 267, f"{result['etfs']['total_value']:.2f}")  # ETF Value
        c.drawString(490, height - 267, f"{result['etfs']['total_tax']:.2f}")  # ETF Tax

        c.drawString(235, height - 330, str(result['stocks']['total_transactions']))  # Stock Transactions
        c.drawString(355, height - 330, f"{result['stocks']['total_value']:.2f}")  # Stock Value
        c.drawString(490, height - 330, f"{result['stocks']['total_tax']:.2f}")  # Stock Tax

        total_tax = result['etfs']['total_tax'] + result['stocks']['total_tax']
        c.drawString(490, height - 460, f"{total_tax:.2f}")  # Total Tax

        # Page 2
        c.showPage()
        c.setFont("Helvetica", 11)
        c.drawString(418, height - 418, f"{total_tax:.2f}")

        c.drawString(122, height - 538, "Brussels")
        c.drawString(192, height - 538, datetime.now().strftime("%d/%m/%Y"))

        # Signature
        signature_x, signature_y = 340, height - 550
        c.drawImage(signature_path, signature_x, signature_y, width=121, height=55)

        c.save()

        # Merge with original PDF
        original_pdf = PdfReader(input_pdf)
        temp_pdf = PdfReader(temp_pdf_path)
        pdf_writer = PdfWriter()

        for page_number, original_page in enumerate(original_pdf.pages):
            if page_number < len(temp_pdf.pages):
                original_page.merge_page(temp_pdf.pages[page_number])
            pdf_writer.add_page(original_page)

        with open(output_pdf, "wb") as out_file:
            pdf_writer.write(out_file)
            logging.info(f"Generated PDF saved at '{output_pdf}'.")

    except Exception as e:
        logging.error(f"Error generating PDF: {e}")
        raise

    finally:
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)