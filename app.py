from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_file_path(filename):
    return os.path.join(UPLOAD_FOLDER, filename)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    filepath = get_file_path(file.filename)
    file.save(filepath)
     # Validate structure
    try:
        df = pd.read_csv(filepath)
        if 'timestamp' not in df.columns or 'value' not in df.columns:
            os.remove(filepath)
            return jsonify({'error': 'Invalid CSV structure. Expected columns: "timestamp", "value".'}), 400
    except Exception as e:
        os.remove(filepath)
        return jsonify({'error': f'Failed to read CSV: {e}'}), 400

    return jsonify({'message': f'File {file.filename} uploaded successfully!'}), 200

@app.route('/filter', methods=['POST'])
def filter_csv():
    data = request.json
    filename = data.get('filename')
    min_value = data.get('min_value')
    max_value = data.get('max_value')

    filepath = get_file_path(filename)
    if not os.path.exists(filepath):
        return jsonify({'error': f'File {filename} does not exist'}), 404

    try:
        df = pd.read_csv(filepath)
        if 'timestamp' not in df.columns or 'value' not in df.columns:
            return jsonify({'error': 'CSV must have "timestamp" and "value" columns'}), 400

        filtered_df = df[(df['value'] >= min_value) & (df['value'] <= max_value)]
        filtered_filename = f'filtered_{filename}'
        filtered_path = get_file_path(filtered_filename)
        filtered_df.to_csv(filtered_path, index=False)

        return send_file(filtered_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/add', methods=['POST'])
def add_data():
    data = request.json
    filename = data.get('filename')
    new_rows = data.get('new_rows')  # List of rows from the frontend

    if not filename or not new_rows:
        return jsonify({'error': 'Filename and new_rows are required.'}), 400

    filepath = get_file_path(filename)
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
    data = request.json
    filename = data.get('filename')

    filepath = get_file_path(filename)
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
    filepath = get_file_path(filename)

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
    app.run(host='0.0.0.0', port=5000, debug=True)
