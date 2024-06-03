from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import logging
import uuid
from config import Config
from ocr import process_presentation

# set up basic logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__, static_url_path='', static_folder='../frontend')
CORS(app)

app.config.from_object(Config)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    """serve the index.html file"""
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
