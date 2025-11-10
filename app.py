from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import pandas as pd
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Configuration via environment variables
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
ALLOWED_EXTENSIONS = {'csv'}
MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16 MB default
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_file_path(filename):
    return os.path.join(app.config['UPLOAD_FOLDER'], filename)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

@app.route('/upload', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file extension. Only .csv allowed.'}), 400

    filename = secure_filename(file.filename)
    filepath = get_file_path(filename)
    try:
        file.save(filepath)
        # Validate structure
        df = pd.read_csv(filepath)
        if 'timestamp' not in df.columns or 'value' not in df.columns:
            os.remove(filepath)
            return jsonify({'error': 'Invalid CSV structure. Expected columns: "timestamp", "value".'}), 400
    except Exception as e:
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception:
                pass
        return jsonify({'error': f'Failed to read CSV: {e}'}), 400

    return jsonify({'message': f'File {filename} uploaded successfully!'}), 200

@app.route('/filter', methods=['POST'])
def filter_csv():
    data = request.json or {}
    filename = data.get('filename')
    min_value = data.get('min_value')
    max_value = data.get('max_value')

    if filename is None or min_value is None or max_value is None:
        return jsonify({'error': 'filename, min_value and max_value are required.'}), 400

    filepath = get_file_path(secure_filename(filename))
    if not os.path.exists(filepath):
        return jsonify({'error': f'File {filename} does not exist'}), 404

    try:
        df = pd.read_csv(filepath)
        if 'timestamp' not in df.columns or 'value' not in df.columns:
            return jsonify({'error': 'CSV must have "timestamp" and "value" columns'}), 400

        filtered_df = df[(df['value'] >= min_value) & (df['value'] <= max_value)]
        filtered_filename = f'filtered_{os.path.basename(filename)}'
        filtered_path = get_file_path(filtered_filename)
        filtered_df.to_csv(filtered_path, index=False)

        return send_file(filtered_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/add', methods=['POST'])
def add_data():
    data = request.json or {}
    filename = data.get('filename')
    new_rows = data.get('new_rows')  # List of rows from the frontend

    if not filename or not new_rows:
        return jsonify({'error': 'Filename and new_rows are required.'}), 400

    filepath = get_file_path(secure_filename(filename))
    if not os.path.exists(filepath):
        return jsonify({'error': f'File {filename} does not exist'}), 404

    try:
        df = pd.read_csv(filepath)
        # Add new rows to the existing DataFrame
        new_data = pd.DataFrame(new_rows)
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_csv(filepath, index=False)

        return jsonify({'message': f'{len(new_rows)} rows added successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete', methods=['POST'])
def delete_csv():
    data = request.json or {}
    filename = data.get('filename')
    if not filename:
        return jsonify({'error': 'filename is required.'}), 400

    filepath = get_file_path(secure_filename(filename))
    if not os.path.exists(filepath):
        return jsonify({'error': f'File {filename} does not exist'}), 404

    try:
        os.remove(filepath)
        return jsonify({'message': f'File {filename} deleted successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/visualize', methods=['GET'])
def visualize_csv():
    filename = request.args.get('filename')
    if not filename:
        return jsonify({'error': 'filename is required.'}), 400

    filepath = get_file_path(secure_filename(filename))
    if not os.path.exists(filepath):
        return jsonify({'error': f'File {filename} does not exist'}), 404

    try:
        df = pd.read_csv(filepath)
        if 'timestamp' not in df.columns or 'value' not in df.columns:
            return jsonify({'error': 'CSV must have "timestamp" and "value" columns'}), 400

        data = {
            'timestamps': df['timestamp'].tolist(),
            'values': df['value'].tolist()
        }
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Default values for local runs; production should use WSGI server (gunicorn)
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    debug_env = os.getenv('FLASK_DEBUG', '0')
    debug = debug_env == '1'
    app.run(host=host, port=port, debug=debug)