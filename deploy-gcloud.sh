#!/bin/bash

echo "🚀 Google Cloud Deployment Script for Furniture Detection App"
echo "============================================================="

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud CLI not found. Installing..."
    echo "Please install Google Cloud CLI from: https://cloud.google.com/sdk/docs/install"
    echo "Or run: curl https://sdk.cloud.google.com | bash"
    exit 1
fi

echo "📋 Choose deployment option:"
echo "1. Cloud Run (Recommended - Serverless)"
echo "2. App Engine (Traditional Serverless)"
echo "3. Compute Engine (Virtual Machine)"

read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo "🚀 Deploying to Cloud Run..."
        
        # Check if user is logged in
        if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
            echo "🔐 Please login to Google Cloud..."
            gcloud auth login
        fi
        
        # Get or set project
        PROJECT_ID=$(gcloud config get-value project)
        if [ -z "$PROJECT_ID" ]; then
            read -p "Enter your Google Cloud Project ID: " PROJECT_ID
            gcloud config set project $PROJECT_ID
        fi
        
        echo "📦 Using project: $PROJECT_ID"
        
        # Enable required APIs
        echo "🔧 Enabling required APIs..."
        gcloud services enable run.googleapis.com
        gcloud services enable cloudbuild.googleapis.com
        
        # Deploy to Cloud Run
        echo "🚀 Deploying to Cloud Run..."
        gcloud run deploy furniture-detection \
            --source . \
            --platform managed \
            --region us-central1 \
            --allow-unauthenticated \
            --port 8080 \
            --memory 2Gi \
            --cpu 1 \
            --timeout 300 \
            --set-env-vars ROBOFLOW_API_KEY=OCYzLwdUcqDtypAh0OYT
        
        echo "✅ Cloud Run deployment complete!"
        echo "🌐 Your app is now live at the URL shown above"
        ;;
        
    2)
        echo "🚀 Deploying to App Engine..."
        
        # Check if user is logged in
        if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
            echo "🔐 Please login to Google Cloud..."
            gcloud auth login
        fi
        
        # Get or set project
        PROJECT_ID=$(gcloud config get-value project)
        if [ -z "$PROJECT_ID" ]; then
            read -p "Enter your Google Cloud Project ID: " PROJECT_ID
            gcloud config set project $PROJECT_ID
        fi
        
        echo "📦 Using project: $PROJECT_ID"
        
        # Enable App Engine API
        echo "🔧 Enabling App Engine API..."
        gcloud services enable appengine.googleapis.com
        
        # Create App Engine app if it doesn't exist
        if ! gcloud app describe &>/dev/null; then
            echo "🏗️ Creating App Engine application..."
            gcloud app create --region=us-central
        fi
        
        # Deploy to App Engine
        echo "🚀 Deploying to App Engine..."
        gcloud app deploy app.yaml --quiet
        
        echo "✅ App Engine deployment complete!"
        echo "🌐 Your app is live at: https://$PROJECT_ID.appspot.com"
        ;;
        
    3)
        echo "🚀 Setting up Compute Engine..."
        echo "This will create a virtual machine and deploy your app."
        
        read -p "Enter VM name (default: furniture-detection-vm): " VM_NAME
        VM_NAME=${VM_NAME:-furniture-detection-vm}
        
        read -p "Enter zone (default: us-central1-a): " ZONE
        ZONE=${ZONE:-us-central1-a}
        
        # Create VM
        echo "🏗️ Creating virtual machine..."
        gcloud compute instances create $VM_NAME \
            --zone=$ZONE \
            --machine-type=e2-medium \
            --image-family=ubuntu-2004-lts \
            --image-project=ubuntu-os-cloud \
            --boot-disk-size=20GB \
            --tags=http-server,https-server
        
        # Enable HTTP/HTTPS traffic
        gcloud compute firewall-rules create allow-http-8080 \
            --allow tcp:8080 \
            --source-ranges 0.0.0.0/0 \
            --description "Allow HTTP traffic on port 8080"
        
        echo "✅ VM created successfully!"
        echo "🔧 To complete setup, SSH into your VM and run:"
        echo "   gcloud compute ssh $VM_NAME --zone=$ZONE"
        echo "   Then upload your code and run: python app.py"
        ;;
        
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "🎉 Deployment process complete!"
echo ""
echo "📱 Your furniture detection app features:"
echo "✅ Mobile-first responsive design"
echo "✅ Professional inventory list format"
echo "✅ AI-powered furniture detection"
echo "✅ Interactive checkboxes"
echo "✅ Global CDN and auto-scaling"
echo ""
echo "🔧 To update your app, just run this script again!"
