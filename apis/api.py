from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
from flask_cors import CORS
import os
import base64
import docx
from backend.tts_services import generate_tts_audio  # Import from your tts_service.py

app = Flask(__name__)
CORS(app)

ALLOWED_EXTENSIONS = {'txt', 'docx', 'doc'}
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# -------------------------------
# Helper functions
# -------------------------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def process_docx(file_path):
    doc = docx.Document(file_path)
    return '\n'.join([para.text for para in doc.paragraphs])

# -------------------------------
# Upload route with TTS
# -------------------------------
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    try:
        file.save(file_path)
        print(f"[INFO] File saved to {file_path}")
    except Exception as e:
        return jsonify({"error": f"Error saving file: {e}"}), 500

    # Extract text
    if filename.endswith('.txt'):
        text = process_txt(file_path)
    elif filename.endswith('.docx'):
        text = process_docx(file_path)
    else:
        return jsonify({"error": "Unsupported file type"}), 400

    # Generate TTS Audio
    try:
        mp3_bytes = generate_tts_audio(text)
        audio_base64 = base64.b64encode(mp3_bytes.getvalue()).decode('utf-8')
    except Exception as e:
        return jsonify({"error": f"TTS generation failed: {e}"}), 500

    # Return both text and audio
    return jsonify({
        "message": "File processed successfully",
        "text": text,
        "audio_base64": audio_base64
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

