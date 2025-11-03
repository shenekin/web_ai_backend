from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
from werkzeug.utils import secure_filename
import os
import docx

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)  # This will allow requests from any origin by default

ALLOWED_EXTENSIONS = {'txt', 'docx', 'doc'}
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        try:
            file.save(file_path)
            print(f"File saved to {file_path}")
        except Exception as e:
            return jsonify({"error": f"Error saving file: {e}"}), 500

        # Process the file based on its type
        if filename.endswith('.txt'):
            text = process_txt(file_path)
        elif filename.endswith('.docx'):
            text = process_docx(file_path)
        else:
            return jsonify({"error": "Unsupported file type"}), 400

        return jsonify({"message": "File processed successfully", "text": text})
    else:
        return jsonify({"error": "File type not allowed"}), 400

def process_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    print("TXT File Content:", text)  # Debugging line
    return text

def process_docx(file_path):
    doc = docx.Document(file_path)
    text = '\n'.join([para.text for para in doc.paragraphs])
    print("DOCX File Content:", text)  # Debugging line
    return text

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
