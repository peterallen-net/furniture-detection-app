# Use Python 3.9 slim image
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
    libglib2.0-0 \
    libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads outputs

# Expose port 8080 (Cloud Run default)
EXPOSE 8080

# Set environment variable for Flask
ENV FLASK_APP=app.py
ENV PORT=8080

# Update app.py to use PORT environment variable
RUN sed -i "s/port=5002/port=int(os.environ.get('PORT', 8080))/" app.py

# Run the application
CMD ["python", "app.py"]
