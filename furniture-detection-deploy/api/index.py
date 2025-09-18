import os
import sys
import json
import cv2
import numpy as np
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
from collections import Counter
from inference_sdk import InferenceHTTPClient
import base64
from io import BytesIO
from PIL import Image
import tempfile

app = Flask(__name__, template_folder='../templates')
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024  # 4MB max for Vercel

# Initialize Roboflow client
client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key=os.getenv("ROBOFLOW_API_KEY", "OCYzLwdUcqDtypAh0OYT")
)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_visualization(image_path, detections, output_path):
    """Create a visualization of the detections on the image"""
    try:
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            return False
        
        # Define colors for different classes (BGR format for OpenCV)
        colors = [
            (255, 0, 0),    # Blue
            (0, 255, 0),    # Green
            (0, 0, 255),    # Red
            (255, 255, 0),  # Cyan
            (255, 0, 255),  # Magenta
            (0, 255, 255),  # Yellow
            (128, 0, 128),  # Purple
            (255, 165, 0),  # Orange
        ]
        
        class_color_map = {}
        color_index = 0
        
        # Draw bounding boxes and labels
        for detection in detections:
            class_name = detection.get('class', 'Unknown')
            confidence = detection.get('confidence', 0)
            x = detection.get('x', 0)
            y = detection.get('y', 0)
            width = detection.get('width', 0)
            height = detection.get('height', 0)
            
            # Assign color to class if not already assigned
            if class_name not in class_color_map:
                class_color_map[class_name] = colors[color_index % len(colors)]
                color_index += 1
            
            color = class_color_map[class_name]
            
            # Calculate bounding box coordinates
            x1 = int(x - width / 2)
            y1 = int(y - height / 2)
            x2 = int(x + width / 2)
            y2 = int(y + height / 2)
            
            # Draw bounding box
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
            
            # Draw label with confidence
            label = f"{class_name}: {confidence:.1%}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            
            # Draw label background
            cv2.rectangle(image, (x1, y1 - label_size[1] - 10), 
                         (x1 + label_size[0], y1), color, -1)
            
            # Draw label text
            cv2.putText(image, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Save the visualization
        cv2.imwrite(output_path, image)
        return True
        
    except Exception as e:
        print(f"Error creating visualization: {str(e)}")
        return False

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
        
        # Use temporary files for serverless environment
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_input:
            file.save(temp_input.name)
            filepath = temp_input.name
        
        # Run furniture detection
        result = client.run_workflow(
            workspace_name="petes-workspace-oetpj",
            workflow_id="detect-count-and-visualise-furniture-instant",
            images={
                "image": filepath
            },
            use_cache=True
        )
        
        # Extract detections
        detections = []
        if isinstance(result, list) and len(result) > 0:
            first_result = result[0]
            if 'predictions' in first_result and 'predictions' in first_result['predictions']:
                detections = first_result['predictions']['predictions']
            elif 'detections' in first_result:
                detections = first_result['detections']
        
        if not detections:
            return jsonify({'error': 'No furniture detected in the image'}), 400
        
        # Count objects by class
        object_counts = Counter()
        detection_list = []
        
        for detection in detections:
            class_name = detection.get('class', 'Unknown')
            confidence = detection.get('confidence', 0)
            object_counts[class_name] += 1
            
            detection_list.append({
                'class': class_name,
                'confidence': f"{confidence:.1%}",
                'position': {
                    'x': round(detection.get('x', 0), 1),
                    'y': round(detection.get('y', 0), 1)
                },
                'size': {
                    'width': round(detection.get('width', 0), 1),
                    'height': round(detection.get('height', 0), 1)
                }
            })
        
        # Create visualization
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_output:
            output_path = temp_output.name
        
        if create_visualization(filepath, detections, output_path):
            # Convert output image to base64 for display
            with open(output_path, 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode('utf-8')
            
            response_data = {
                'success': True,
                'total_objects': len(detections),
                'object_counts': dict(object_counts.most_common()),
                'detections': detection_list,
                'output_image': f"data:image/jpeg;base64,{img_data}"
            }
            
            # Clean up temporary files
            os.unlink(filepath)
            os.unlink(output_path)
            
            return jsonify(response_data)
        else:
            return jsonify({'error': 'Failed to create visualization'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

# Vercel serverless handler
def handler(event, context):
    return app(event, context)
