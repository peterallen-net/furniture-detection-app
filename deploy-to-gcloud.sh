#!/bin/bash

# Google Cloud Deployment Script for Furniture Detection App
# This script builds and deploys the Docker container to Google Cloud Run

set -e

echo "🚀 Starting Google Cloud deployment..."

# Configuration
PROJECT_ID="roboflow-cv"
SERVICE_NAME="furniture-detection-app"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Check if PROJECT_ID is set
if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: Please set your PROJECT_ID in this script"
    echo "   Edit deploy-to-gcloud.sh and replace PROJECT_ID=\"\" with your actual project ID"
    exit 1
fi

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI is not installed"
    echo "   Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Error: Docker is not running"
    echo "   Please start Docker Desktop"
    exit 1
fi

echo "📦 Building Docker image..."
docker build -t ${SERVICE_NAME} .

echo "🏷️  Tagging image for Google Container Registry..."
docker tag ${SERVICE_NAME} ${IMAGE_NAME}

echo "🔐 Configuring Docker for Google Cloud..."
gcloud auth configure-docker --quiet

echo "⬆️  Pushing image to Google Container Registry..."
docker push ${IMAGE_NAME}

echo "🌐 Deploying to Google Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --port 8080 \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --set-env-vars ROBOFLOW_API_KEY=OCYzLwdUcqDtypAh0OYT

echo "✅ Deployment complete!"
echo "🔗 Your app should be available at the URL shown above"
