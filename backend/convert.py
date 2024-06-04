import os
import subprocess
import logging
from utils import wait_for_file

def convert_to_pdf(pptx_path, output_folder):
    """converts PowerPoint to PDF"""
    base_name = os.path.basename(pptx_path)
    pdf_name = base_name.rsplit('.', 1)[0] + '.pdf'
    pdf_path = os.path.join(output_folder, pdf_name)
    
    # convert PowerPoint to PDF specifying the output filename
    subprocess.run(['libreoffice', '--headless', '--convert-to', 'pdf', '--outdir', output_folder, pptx_path], capture_output=True)
    
    # wait for the PDF to be available
    pdf_ready = wait_for_file(pdf_path)
    
    if pdf_ready:
        return pdf_path
    else:
        logging.error("PDF file was not created.")
        return None
