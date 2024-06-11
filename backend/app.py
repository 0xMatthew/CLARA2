import os
import logging
import subprocess
import time
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from backend.config import Config
from main import orchestrate_process

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

# track the current state of processing
processing_state = {
    "is_processing": False,
    "should_continue": True,
    "current_slide": 0
}

@app.route('/')
def index():
    """Serve the index.html file"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/upload.js')
def script():
    return send_from_directory(app.static_folder, 'upload.js')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pptx'}

@app.route('/upload', methods=['POST'])
def upload_file():
    if processing_state["is_processing"]:
        return jsonify({"error": "already processing a file."}), 400

    file = request.files['presentation']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        processing_state["is_processing"] = True
        processing_state["should_continue"] = True
        result = orchestrate_process(file_path, app.config['OUTPUT_FOLDER'], processing_state)
        processing_state["is_processing"] = False
        return jsonify(result)
    return jsonify({"error": "Invalid file or no file uploaded."}), 400

@app.route('/stop-audio2face', methods=['POST'])
def stop_audio2face():
    try:
        # Command to find the process ID of kit.exe and kill it
        find_cmd = 'cmd.exe /C "tasklist /FI "IMAGENAME eq kit.exe" /FO CSV /NH"'
        output = subprocess.check_output(find_cmd, shell=True).decode('utf-8').strip().split('\r\n')
        
        for line in output:
            if line:
                pid = line.split(',')[1].strip('"')
                kill_cmd = ['cmd.exe', '/C', f'taskkill /PID {pid} /F']
                subprocess.run(kill_cmd, check=True)
        
        # Command to start a new instance of audio2face
        start_cmd = 'cmd.exe /C "C:\\Users\\Matthew\\AppData\\Local\\ov\\pkg\\audio2face-2023.2.0\\audio2face_headless.bat"'
        subprocess.Popen(start_cmd, shell=True)
        
        # Allow some time for the audio2face to initialize
        time.sleep(10)
        
        # Send the curl command to configure audio2face
        curl_cmd = [
            'curl', '-X', 'POST',
            f'http://{os.getenv("HOST_IP_ADDRESS")}:8011/A2F/USD/Load',
            '-H', 'accept: application/json',
            '-H', 'Content-Type: application/json',
            '-d', '{"file_name": "C:/Users/Matthew/Documents/Desktop/CLARA2/unreal_streaming.usd"}'
        ]
        subprocess.run(curl_cmd, check=True)
        
        # reset the processing state
        processing_state["is_processing"] = False
        processing_state["should_continue"] = False
        processing_state["current_slide"] = 0

        return jsonify({"message": "Audio2Face restarted successfully."})
    except subprocess.CalledProcessError as e:
        logging.error(f"Error stopping or starting Audio2Face: {e}")
        return jsonify({"error": f"Failed to restart Audio2Face: {e}"}), 500
    except subprocess.SubprocessError as e:
        logging.error(f"Subprocess error: {e}")
        return jsonify({"error": f"Failed to restart Audio2Face: {e}"}), 500
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
