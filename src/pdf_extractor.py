import pdfplumber
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging


def extract_value(line, keyword):
    """Extracts a float value following a given keyword in a line."""
    if keyword in line:
        try:
            return float(line.split(":")[1].strip())
        except (IndexError, ValueError) as e:
            logging.error(f"Error extracting value: {e}")
    return 0.0


def extract_transactions(line, keyword):
    """Extracts an integer count following a given keyword in a line."""
    if keyword in line:
        try:
            return int(line.split(":")[1].strip())
        except (IndexError, ValueError) as e:
            logging.error(f"Error extracting transactions: {e}")
    return 0


def extract_transaction_data(pdf_path):
    """Extracts transaction data for ETFs and stocks from a given PDF path."""
    data = {
        "etfs": {"total_transactions": 0, "total_value": 0.0, "total_tax": 0.0},
        "stocks": {"total_transactions": 0, "total_value": 0.0, "total_tax": 0.0}
    }

    section_keywords = {
        "TAX ON STOCK-EXCHANGE TRANSACTIONS FOR ETFS": "etfs",
        "TAX ON STOCK-EXCHANGE TRANSACTIONS FOR STOCKS": "stocks"
    }
    
    current_section = None
    date_pattern = r"\d{2}\.\d{2}\.\d{4}"
    extracted_date = None

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                
                lines = text.split("\n")
                if not extracted_date:
                    for line in lines[:3]:  # Check first few lines for date
                        date_match = re.search(date_pattern, line)
                        if date_match:
                            extracted_date = date_match.group()
                            break


                for line in lines:
                    for keyword, section in section_keywords.items():
                        if keyword in line:
                            current_section = data[section]
                            logging.info(f"Switched to section '{section}'.")
                            break
                        
                    if current_section:
                        current_section["total_value"] += extract_value(line, "TOTAL TAX BASIS IN EUR:")
                        current_section["total_transactions"] += extract_transactions(line, "TOTAL TRANSACTIONS:")

    except Exception as e:
        logging.error(f"Error processing PDF '{pdf_path}': {e}")
        raise

    if not extracted_date:
        raise ValueError(f"No date found in PDF '{pdf_path}'.")

    # Calculate total tax based on total values
    data["etfs"]["total_tax"] = round(data["etfs"]["total_value"] * 0.0012, 2)
    data["stocks"]["total_tax"] = round(data["stocks"]["total_value"] * 0.0035, 2)

    # Adjust extracted date by one month
    adjusted_date = datetime.strptime(extracted_date, "%d.%m.%Y") - relativedelta(months=1)

    return {"etfs": data["etfs"], "stocks": data["stocks"], "date": adjusted_date}