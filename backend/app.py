from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import subprocess
import uuid
from concurrent.futures import ProcessPoolExecutor
import pytesseract
from PIL import Image
import logging
import time

# set up basic logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__, static_url_path='', static_folder='../frontend')
CORS(app)

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['IMAGE_FOLDER'] = 'images'
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
        process_presentation(file_path)
        return jsonify({"message": "File uploaded successfully, processing started."})
    return jsonify({"error": "Invalid file or no file uploaded."}), 400

def process_presentation(file_path):
    """ Converts PowerPoint to images and processes each image with OCR. """
    image_folder = os.path.join(app.config['IMAGE_FOLDER'], uuid.uuid4().hex)
    os.makedirs(image_folder, exist_ok=True)
    convert_to_images(file_path, image_folder)

def convert_to_images(pptx_path, output_folder):
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
    """Wait for a file to exist until timeout."""
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
        logging.info(f"Converted {pdf_path} to images at {images_path_pattern}")
        process_images(output_folder)


def process_images(image_folder):
    images = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.endswith('.png')]
    if not images:
        logging.error("No images found for OCR processing.")
        return

    with ProcessPoolExecutor() as executor:
        results = list(executor.map(perform_ocr, images))
        logging.info(f"OCR results: {results}")

def perform_ocr(image_path):
    text = pytesseract.image_to_string(Image.open(image_path))
    logging.info(f"OCR result for {image_path}: {text}")
    return text

if __name__ == '__main__':
    app.run(debug=True, port=5000)
