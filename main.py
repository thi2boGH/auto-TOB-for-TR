import os
import logging
from utils.config_loader import load_config
from utils.logger import setup_logging
from src.pdf_extractor import extract_transaction_data
from src.pdf_editor import add_text_to_pdf


def main():
    setup_logging()
    logging.info("Starting PDF processing...")

    try:
        # Load configuration
        config = load_config()
        personal_info = config["personal_info"]

        # Define paths
        input_folder = 'resources/input'
        output_folder = 'resources/output'
        template_pdf = 'resources/templates/Changement de compte formulaire TOB EN.pdf'
        signature_image = 'resources/images/signature.jpg'

        # Ensure output directory exists
        os.makedirs(output_folder, exist_ok=True)

        # PDFs to process
        pdf_files = [
            'month1.pdf', 
            'month2.pdf',
            ]
        results = []

        # Process PDFs
        for pdf_file in pdf_files:
            pdf_path = os.path.join(input_folder, pdf_file)
            result = extract_transaction_data(pdf_path)
            results.append(result)
            logging.info(f"Processed '{pdf_file}'.")

        # Combine results
        combined_result = {
            'etfs': {
                'total_transactions': sum(r['etfs']['total_transactions'] for r in results),
                'total_value': sum(r['etfs']['total_value'] for r in results),
                'total_tax': sum(r['etfs']['total_tax'] for r in results),
            },
            'stocks': {
                'total_transactions': sum(r['stocks']['total_transactions'] for r in results),
                'total_value': sum(r['stocks']['total_value'] for r in results),
                'total_tax': sum(r['stocks']['total_tax'] for r in results),
            },
            'dates': [r['date'] for r in results]
        }

        # Generate output PDF name
        month1 = combined_result['dates'][0].strftime("%b")
        month2 = combined_result['dates'][1].strftime("%b")
        year = combined_result['dates'][0].strftime("%Y")
        national_id = personal_info["national_id_number"].replace("-", "").replace(".", "")
        output_pdf_name = f"TOB EN {month1} + {month2} {year} {national_id}.pdf"
        output_pdf_path = os.path.join(output_folder, output_pdf_name)

        # Generate PDF
        add_text_to_pdf(
            input_pdf=template_pdf,
            output_pdf=output_pdf_path,
            signature_path=signature_image,
            personal_info=personal_info,
            result=combined_result
        )

        logging.info("PDF processing completed successfully.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()