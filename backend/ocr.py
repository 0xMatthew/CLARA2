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
from convert import convert_to_pdf

def process_presentation(file_path):
    """converts powerpoint to images and processes each image with ocr"""
    image_folder = os.path.join(Config.IMAGE_FOLDER, uuid.uuid4().hex)
    os.makedirs(image_folder, exist_ok=True)
    pdf_path = convert_to_pdf(file_path, image_folder)
    
    if pdf_path:
        convert_pdf_to_images(pdf_path, image_folder)
        slide_data = process_images(image_folder)
        return slide_data, image_folder
    else:
        logging.error("failed to convert presentation to pdf.")
        return None, None

def convert_pdf_to_images(pdf_path, output_folder):
    images_path_pattern = os.path.join(output_folder, f"slide_%d.{Config.PDF_CONVERSION_FORMAT}")
    process = subprocess.run(['convert', '-density', Config.PDF_CONVERSION_DENSITY, pdf_path, images_path_pattern], capture_output=True)
    logging.info(f"imagemagick stdout: {process.stdout.decode('utf-8')}")
    logging.info(f"imagemagick stderr: {process.stderr.decode('utf-8')}")

    if process.returncode != 0:
        logging.error("imagemagick failed to convert pdf to images.")
    else:
        logging.info(f"converted {pdf_path} to images at {images_path_pattern}")

def process_images(image_folder):
    images = sorted([os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.endswith(f'.{Config.PDF_CONVERSION_FORMAT}')], key=lambda x: int(x.split('_')[-1].split('.')[0]))
    if not images:
        logging.error("no images found for ocr processing.")
        return None

    logging.info(f"processing {len(images)} slides for ocr...")

    results = []
    max_workers = Config.OCR_MAX_WORKERS
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(perform_ocr, image, idx): idx for idx, image in enumerate(images)}
        for future in as_completed(futures):
            idx = futures[future]
            try:
                result = future.result(timeout=Config.OCR_TIMEOUT)  # 60 seconds timeout for each ocr task
                results.append(result)
                logging.info(f"processed slide {idx + 1}")
            except TimeoutError:
                logging.error(f"processing slide {idx + 1} timed out.")
            except Exception as e:
                logging.error(f"error processing slide {idx + 1}: {e}")

    results.sort(key=lambda x: x['slide_number'])

    return results

def perform_ocr(image_path, slide_number):
    try:
        text = pytesseract.image_to_string(Image.open(image_path))
        return {"slide_number": slide_number + 1, "text": text}
    except Exception as e:
        logging.error(f"error performing ocr on slide {slide_number + 1}: {e}")
        return {"slide_number": slide_number + 1, "text": ""}
