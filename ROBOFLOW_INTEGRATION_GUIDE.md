# 🤖 Complete Roboflow API Integration Guide

## 📋 Overview
This guide shows you how to add full AI furniture detection capabilities to your Google Cloud Run deployment using the Roboflow API.

## 🌐 Current Working Deployment
**Live URL**: https://furniture-detection-app-213170531876.us-central1.run.app
**Docker Image**: `gcr.io/roboflow-cv/furniture-detection-app:latest`

## 🔧 Step-by-Step Integration

### Step 1: Update Your Application Code

Replace your current `app-minimal.py` with this AI-enabled version:

```python
import os
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
import requests

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Use /tmp for Cloud Run
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
app.config['OUTPUT_FOLDER'] = '/tmp/outputs'

# Create directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

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

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'port': os.environ.get('PORT', 8080)})

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
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = str(int(os.urandom(4).hex(), 16))
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Run furniture detection using Roboflow API
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
            # Return original image if no furniture detected
            with open(filepath, 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode('utf-8')
            
            os.remove(filepath)
            
            return jsonify({
                'success': True,
                'message': 'No furniture detected in the image.',
                'total_objects': 0,
                'object_counts': {},
                'detections': [],
                'output_image': f"data:image/jpeg;base64,{img_data}"
            })
        
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
        output_filename = f"output_{filename}"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
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
            
            # Clean up files
            os.remove(filepath)
            os.remove(output_path)
            
            return jsonify(response_data)
        else:
            # If visualization fails, return original image
            with open(filepath, 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode('utf-8')
            
            os.remove(filepath)
            
            return jsonify({
                'success': True,
                'message': 'Detection successful but visualization failed.',
                'total_objects': len(detections),
                'object_counts': dict(object_counts.most_common()),
                'detections': detection_list,
                'output_image': f"data:image/jpeg;base64,{img_data}"
            })
            
    except Exception as e:
        # Clean up file if it exists
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"Starting server on port {port}")
    app.run(debug=False, host='0.0.0.0', port=port)
```

### Step 2: Update Requirements

Update your `requirements-minimal.txt`:

```txt
Flask==2.3.3
Werkzeug==2.3.7
Pillow==10.0.1
requests==2.31.0
opencv-python-headless==4.8.1.78
numpy==1.24.3
inference-sdk==0.9.13
```

### Step 3: Update Dockerfile

Update your `Dockerfile-minimal`:

```dockerfile
# Use Python 3.9 slim image for smaller size and faster startup
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements-minimal.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-minimal.txt

# Copy application files
COPY app-minimal.py app.py
COPY templates/ templates/

# Create necessary directories
RUN mkdir -p /tmp/uploads /tmp/outputs

# Expose port 8080 for Cloud Run
EXPOSE 8080

# Set environment variable for port
ENV PORT=8080

# Run the application
CMD ["python", "app.py"]
```

### Step 4: Build and Deploy

```bash
# Build the AI-enabled image
docker build -f Dockerfile-minimal -t furniture-detection-app-ai .

# Tag for Google Cloud Registry
docker tag furniture-detection-app-ai gcr.io/roboflow-cv/furniture-detection-app:ai-latest

# Push to registry
docker push gcr.io/roboflow-cv/furniture-detection-app:ai-latest

# Deploy to Cloud Run with more resources
gcloud run deploy furniture-detection-app \
  --image gcr.io/roboflow-cv/furniture-detection-app:ai-latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 600 \
  --max-instances 10
```

## 🔑 API Configuration

### Roboflow API Key
The app uses the API key: `OCYzLwdUcqDtypAh0OYT`

You can also set it as an environment variable:
```bash
export ROBOFLOW_API_KEY="your-api-key-here"
```

### Workflow Details
- **Workspace**: `petes-workspace-oetpj`
- **Workflow ID**: `detect-count-and-visualise-furniture-instant`

## 🎯 What the AI Integration Provides

### ✅ Features Added:
1. **Real AI Furniture Detection** - Uses Roboflow's trained models
2. **Visual Bounding Boxes** - Draws colored boxes around detected furniture
3. **Confidence Scores** - Shows detection confidence percentages
4. **Object Counting** - Counts each type of furniture detected
5. **Detailed Results** - Provides position and size data for each detection

### 📊 Detection Results Include:
- **Total Objects**: Count of all furniture detected
- **Object Counts**: Breakdown by furniture type (chair, table, sofa, etc.)
- **Individual Detections**: Each with:
  - Class name (furniture type)
  - Confidence percentage
  - Position (x, y coordinates)
  - Size (width, height)
- **Annotated Image**: Original image with bounding boxes and labels

## 🚀 Testing Your AI Integration

1. **Upload an image** with furniture
2. **View results** showing:
   - Detected furniture with bounding boxes
   - Confidence scores for each detection
   - Count summary by furniture type
   - Detailed detection data

## 🔧 Troubleshooting

### Common Issues:

1. **Container Startup Timeout**
   - Increase memory to 2Gi and CPU to 2
   - Extend timeout to 600 seconds

2. **OpenCV Dependencies**
   - Ensure system packages are installed in Dockerfile
   - Use `opencv-python-headless` for serverless environments

3. **API Errors**
   - Check Roboflow API key is valid
   - Verify workspace and workflow IDs
   - Ensure image format is supported

### Performance Tips:
- Use caching (`use_cache=True`) for faster repeated requests
- Optimize image sizes before processing
- Consider implementing request queuing for high traffic

## 📝 Manual Google Cloud Console Access

If you need to deploy manually through Google Cloud Console:

**Docker Registry URL**: `gcr.io/roboflow-cv/furniture-detection-app:ai-latest`

**Required Settings**:
- Memory: 2 GiB
- CPU: 2
- Port: 8080
- Timeout: 600 seconds
- Max instances: 10
- Authentication: Allow unauthenticated invocations

## 🎉 Success!

Once deployed, your application will have full AI-powered furniture detection capabilities, providing real-time analysis of uploaded images with professional-grade computer vision results!
