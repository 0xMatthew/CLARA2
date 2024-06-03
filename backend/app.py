from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
CORS(app)

app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # limit file size to 16MB

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['presentation']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)
        return jsonify({"message": "file uploaded successfully, processing started."})
    return jsonify({"error": "invalid file or no file uploaded."}), 400

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'pptx'}

if __name__ == '__main__':
    app.run(debug=True, port=5000)
