from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import base64
import docx
from backend.tts_services import generate_tts_audio  # Assuming TTS service is in this module
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

ALLOWED_EXTENSIONS = {'txt', 'docx', 'doc'}
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 160 * 1024 * 1024  # 16 MB max file size

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def process_docx(file_path):
    doc = docx.Document(file_path)
    return '\n'.join([para.text for para in doc.paragraphs])

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
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
            print(f"File saved to {file_path}")  # Log the file path for debugging
        except Exception as e:
            print(f"Error saving file: {str(e)}")
            return jsonify({"error": f"Error saving file: {str(e)}"}), 500

        if filename.endswith('.txt'):
            text = process_txt(file_path)
        elif filename.endswith('.docx'):
            text = process_docx(file_path)
        else:
            return jsonify({"error": "Unsupported file type"}), 400

        # Log the text that was extracted
        print(f"Extracted text: {text[:100]}...")

        try:
            # Generate TTS (This function now only returns the BytesIO object)
            mp3_bytes = generate_tts_audio(text)

            # Ensure mp3_bytes is a BytesIO object
            if not hasattr(mp3_bytes, 'getvalue'):
                return jsonify({"error": "Invalid TTS response: expected a BytesIO object."}), 500

            # Convert the audio to base64
            audio_data = mp3_bytes.getvalue()  # Get the byte data from the BytesIO object
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')

            # Log the length of the audio data
            print(f"TTS audio generated: {len(audio_data)} bytes")

            return jsonify({
                "message": "File processed successfully",
                "text": text,
                "audio_base64": audio_base64
            })

        except Exception as e:
            print(f"TTS generation failed: {str(e)}")
            return jsonify({"error": f"TTS generation failed: {str(e)}"}), 500

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
