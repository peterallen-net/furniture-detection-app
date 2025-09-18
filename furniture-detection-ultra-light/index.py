import os
import json
import base64
from flask import Flask, request, render_template, jsonify

app = Flask(__name__, template_folder='../templates')
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024  # 4MB max

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload an image file.'}), 400
        
        # Read file data
        file_data = file.read()
        
        # Convert to base64 for display
        img_data = base64.b64encode(file_data).decode('utf-8')
        
        # Mock furniture detection data for demo
        # In production, this would call an external API
        mock_detections = [
            {'class': 'Chair', 'confidence': 0.95},
            {'class': 'Table', 'confidence': 0.88},
            {'class': 'Lamp', 'confidence': 0.92},
            {'class': 'Sofa', 'confidence': 0.85},
            {'class': 'Bookshelf', 'confidence': 0.78}
        ]
        
        # Count objects by class
        object_counts = {}
        detection_list = []
        
        for i, detection in enumerate(mock_detections):
            class_name = detection['class']
            confidence = detection['confidence']
            
            if class_name in object_counts:
                object_counts[class_name] += 1
            else:
                object_counts[class_name] = 1
            
            detection_list.append({
                'class': class_name,
                'confidence': f"{confidence:.1%}",
                'position': {
                    'x': 100 + (i * 50),
                    'y': 100 + (i * 30)
                },
                'size': {
                    'width': 80,
                    'height': 60
                }
            })
        
        response_data = {
            'success': True,
            'total_objects': len(mock_detections),
            'object_counts': object_counts,
            'detections': detection_list,
            'output_image': f"data:image/jpeg;base64,{img_data}"
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

# Vercel handler
def handler(event, context):
    return app(event, context)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
