# Furniture Detection Web Application

A web-based furniture detection system that uses AI to identify and analyze furniture in uploaded images.

## Features

- **Web Interface**: Beautiful, responsive web interface for easy image uploads
- **Drag & Drop**: Support for drag-and-drop file uploads
- **AI Detection**: Powered by Roboflow's custom furniture detection model
- **Visual Results**: Displays detected furniture with bounding boxes and confidence scores
- **Detailed Analysis**: Provides object counts and detailed detection information
- **Multiple Formats**: Supports JPG, PNG, GIF, and BMP image formats

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   python app.py
   ```

3. **Access the Web Interface**:
   Open your browser and go to: `http://localhost:5001`

## How to Use

1. **Upload an Image**: 
   - Click the upload area or drag and drop an image file
   - Supported formats: JPG, PNG, GIF, BMP (max 16MB)

2. **View Results**:
   - The system will process your image using AI
   - Results include:
     - Annotated image with bounding boxes
     - Object count summary
     - Detailed detection list with confidence scores and positions

3. **Upload Another Image**:
   - Click "Upload Another Image" to process additional images

## Detected Furniture Types

The system can detect various furniture items including:
- Armchairs
- Carpets
- Floor lamps
- Side tables
- Plants
- Paintings
- Sideboards/Credenzas
- And more...

## Technical Details

- **Backend**: Flask web framework
- **AI Model**: Roboflow custom furniture detection workflow
- **Image Processing**: OpenCV for visualization
- **Frontend**: HTML/CSS/JavaScript with responsive design

## Files Structure

```
├── app.py                 # Flask web application
├── main.py               # Command-line version
├── templates/
│   └── index.html        # Web interface template
├── uploads/              # Temporary upload directory
├── outputs/              # Generated visualization outputs
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## API Endpoints

- `GET /`: Main web interface
- `POST /upload`: Image upload and processing endpoint

## Example Usage

The web application provides an intuitive interface where users can:

1. Upload images of rooms or furniture
2. Receive AI-powered furniture detection results
3. View annotated images with detected objects highlighted
4. See detailed statistics about detected furniture

Perfect for interior designers, real estate professionals, or anyone interested in automated furniture analysis!
