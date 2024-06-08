import os
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from backend.config import Config
from main import orchestrate_process  # Import orchestrate_process from main.py

# ensure necessary directories exist
os.makedirs(Config.OUTPUT_FOLDER, exist_ok=True)
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(Config.IMAGE_FOLDER, exist_ok=True)
os.makedirs(Config.MODELS_FOLDER, exist_ok=True)

# set up basic logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, static_url_path='', static_folder='../frontend')
CORS(app)

app.config.from_object(Config)

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
        slide_data, image_folder = orchestrate_process(file_path, app.config['OUTPUT_FOLDER'])
        if slide_data and image_folder:
            return jsonify({
                "slides": slide_data,
                "image_folder": image_folder
            })
        return jsonify({"error": "processing error"}), 500
    return jsonify({"error": "invalid file or no file uploaded."}), 400

@app.route('/images/<path:folder>/<path:filename>')
def serve_image(folder, filename):
    full_path = os.path.join(Config.IMAGE_FOLDER, folder)
    logging.info(f"serving image from {full_path}/{filename}")
    return send_from_directory(full_path, filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
