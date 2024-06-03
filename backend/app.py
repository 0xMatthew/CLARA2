from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import subprocess
import uuid
import pytesseract
from PIL import Image
import logging
import time
import json
from concurrent.futures import ProcessPoolExecutor, as_completed, TimeoutError

# set up basic logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__, static_url_path='', static_folder='../frontend')
CORS(app)

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['IMAGE_FOLDER'] = 'images'
app.config['OUTPUT_FOLDER'] = 'outputs'
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

@app.route('/')
def index():
    """Serve the index.html file."""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/upload.js')
def script():
    return send_from_directory(app.static_folder, 'upload.js')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pptx'}

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['presentation']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        ocr_results_path = process_presentation(file_path)
        return jsonify({"message": "file uploaded successfully, OCR processing finished.", "ocr_results": ocr_results_path})
    return jsonify({"error": "invalid file or no file uploaded."}), 400

def process_presentation(file_path):
    """converts PowerPoint to images and processes each image with OCR"""
    image_folder = os.path.join(app.config['IMAGE_FOLDER'], uuid.uuid4().hex)
    os.makedirs(image_folder, exist_ok=True)
    convert_to_pdf(file_path, image_folder)
    return process_images(image_folder)

def convert_to_pdf(pptx_path, output_folder):
    # strip the original file extension and replace with .pdf
    base_name = os.path.basename(pptx_path)
    pdf_name = base_name.rsplit('.', 1)[0] + '.pdf'
    pdf_path = os.path.join(output_folder, pdf_name)
    
    # convert PowerPoint to PDF specifying the output filename
    subprocess.run(['libreoffice', '--headless', '--convert-to', 'pdf', '--outdir', output_folder, pptx_path], capture_output=True)
    
    # wait for the PDF to be available
    pdf_ready = wait_for_file(pdf_path)
    
    if pdf_ready:
        convert_pdf_to_images(pdf_path, output_folder)
    else:
        logging.error("PDF file was not created.")

def wait_for_file(file_path, timeout=30):
    """wait for a file to exist until timeout."""
    start_time = time.time()
    while True:
        if os.path.exists(file_path):
            logging.info(f"File {file_path} found, proceeding with conversion.")
            return True
        elif (time.time() - start_time) > timeout:
            logging.error(f"File {file_path} not found after {timeout} seconds.")
            return False
        time.sleep(1)  # sleep for a second before retrying

def convert_pdf_to_images(pdf_path, output_folder):
    images_path_pattern = os.path.join(output_folder, "slide_%d.png")
    process = subprocess.run(['convert', '-density', '150', pdf_path, images_path_pattern], capture_output=True)
    logging.info(f"ImageMagick stdout: {process.stdout.decode('utf-8')}")
    logging.info(f"ImageMagick stderr: {process.stderr.decode('utf-8')}")

    if process.returncode != 0:
        logging.error("ImageMagick failed to convert PDF to images.")
    else:
        logging.info(f"converted {pdf_path} to images at {images_path_pattern}")

def process_images(image_folder):
    images = sorted([os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.endswith('.png')], key=lambda x: int(x.split('_')[-1].split('.')[0]))
    if not images:
        logging.error("no images found for OCR processing.")
        return None

    logging.info(f"processing {len(images)} slides for OCR...")

    results = []
    max_workers = min(8, os.cpu_count() - 1)  # limit the number of workers to avoid overwhelming the system
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(perform_ocr, image, idx): idx for idx, image in enumerate(images)}
        for future in as_completed(futures):
            idx = futures[future]
            try:
                result = future.result(timeout=60)  # 60 seconds timeout for each OCR task
                results.append(result)
                logging.info(f"processed slide {idx + 1}")
            except TimeoutError:
                logging.error(f"processing slide {idx + 1} timed out.")
            except Exception as e:
                logging.error(f"error processing slide {idx + 1}: {e}")

    results.sort(key=lambda x: x['slide_number'])

    # write OCR results to a JSON file
    output_file_path = os.path.join(app.config['OUTPUT_FOLDER'], f'{uuid.uuid4().hex}.json')
    with open(output_file_path, 'w') as output_file:
        json.dump(results, output_file, indent=4)

    logging.info(f"OCR processing completed. results saved to {output_file_path}")
    return output_file_path

def perform_ocr(image_path, slide_number):
    try:
        text = pytesseract.image_to_string(Image.open(image_path))
        return {"slide_number": slide_number + 1, "text": text}
    except Exception as e:
        logging.error(f"error performing OCR on slide {slide_number + 1}: {e}")
        return {"slide_number": slide_number + 1, "text": ""}

if __name__ == '__main__':
    app.run(debug=True, port=5000)
