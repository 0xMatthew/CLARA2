import os
import logging
import json
import uuid
import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed, TimeoutError
from PIL import Image
import pytesseract
from config import Config
from utils import wait_for_file

def process_presentation(file_path):
    """Converts PowerPoint to images and processes each image with OCR"""
    image_folder = os.path.join(Config().IMAGE_FOLDER, uuid.uuid4().hex)
    os.makedirs(image_folder, exist_ok=True)
    convert_to_pdf(file_path, image_folder)
    ocr_results_path = process_images(image_folder)

    logging.info(f"OCR processing completed. Results saved to {ocr_results_path}")
    return ocr_results_path

def convert_to_pdf(pptx_path, output_folder):
    # Strip the original file extension and replace with .pdf
    base_name = os.path.basename(pptx_path)
    pdf_name = base_name.rsplit('.', 1)[0] + '.pdf'
    pdf_path = os.path.join(output_folder, pdf_name)
    
    # Convert PowerPoint to PDF specifying the output filename
    subprocess.run(['libreoffice', '--headless', '--convert-to', 'pdf', '--outdir', output_folder, pptx_path], capture_output=True)
    
    # Wait for the PDF to be available
    pdf_ready = wait_for_file(pdf_path)
    
    if pdf_ready:
        convert_pdf_to_images(pdf_path, output_folder)
    else:
        logging.error("PDF file was not created.")

def convert_pdf_to_images(pdf_path, output_folder):
    images_path_pattern = os.path.join(output_folder, "slide_%d.png")
    process = subprocess.run(['convert', '-density', '150', pdf_path, images_path_pattern], capture_output=True)
    logging.info(f"ImageMagick stdout: {process.stdout.decode('utf-8')}")
    logging.info(f"ImageMagick stderr: {process.stderr.decode('utf-8')}")

    if process.returncode != 0:
        logging.error("ImageMagick failed to convert PDF to images.")
    else:
        logging.info(f"Converted {pdf_path} to images at {images_path_pattern}")

def process_images(image_folder):
    images = sorted([os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.endswith('.png')], key=lambda x: int(x.split('_')[-1].split('.')[0]))
    if not images:
        logging.error("No images found for OCR processing.")
        return None

    logging.info(f"Processing {len(images)} slides for OCR...")

    results = []
    max_workers = min(8, os.cpu_count() - 1)  # Limit the number of workers to avoid using too many threads/locking CPU usage at 100%
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(perform_ocr, image, idx): idx for idx, image in enumerate(images)}
        for future in as_completed(futures):
            idx = futures[future]
            try:
                result = future.result(timeout=60)  # 60 seconds timeout for each OCR task
                results.append(result)
                logging.info(f"Processed slide {idx + 1}")
            except TimeoutError:
                logging.error(f"Processing slide {idx + 1} timed out.")
            except Exception as e:
                logging.error(f"Error processing slide {idx + 1}: {e}")

    results.sort(key=lambda x: x['slide_number'])

    # Write OCR results to a JSON file
    output_file_path = os.path.join(Config().OUTPUT_FOLDER, f'{uuid.uuid4().hex}.json')
    with open(output_file_path, 'w') as output_file:
        json.dump(results, output_file, indent=4)

    logging.info(f"OCR processing completed. Results saved to {output_file_path}")
    return output_file_path

def perform_ocr(image_path, slide_number):
    try:
        text = pytesseract.image_to_string(Image.open(image_path))
        return {"slide_number": slide_number + 1, "text": text}
    except Exception as e:
        logging.error(f"Error performing OCR on slide {slide_number + 1}: {e}")
        return {"slide_number": slide_number + 1, "text": ""}
