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
    pdf_path = os.path.join(output_folder, "presentation.pdf")
    subprocess.run(['libreoffice', '--headless', '--convert-to', 'pdf', pptx_path, '--outdir', output_folder], capture_output=True)
    convert_pdf_to_images(pdf_path, output_folder)

def convert_pdf_to_images(pdf_path, output_folder):
    images_path_pattern = os.path.join(output_folder, "slide_%d.png")
    subprocess.run(['convert', '-density', '150', pdf_path, images_path_pattern], capture_output=True)
    process_images(output_folder)

def process_images(image_folder):
    with ProcessPoolExecutor() as executor:
        images = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.endswith('.png')]
        results = list(executor.map(perform_ocr, images))
        logging.info(f"OCR results: {results}")

def perform_ocr(image_path):
    return pytesseract.image_to_string(Image.open(image_path))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
