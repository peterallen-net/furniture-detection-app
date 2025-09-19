# 🚀 Google Cloud Serverless Deployment Instructions

## Complete Docker Package for Google Cloud Run

This guide provides step-by-step instructions to deploy your furniture detection web app to Google Cloud Run (serverless).

## 📋 Prerequisites

1. **Google Cloud Account** with billing enabled
2. **Google Cloud CLI** installed ([Download here](https://cloud.google.com/sdk/docs/install))
3. **Docker Desktop** running on your machine
4. **Project ID** from Google Cloud Console

## 🔧 Setup Instructions

### Step 1: Authenticate with Google Cloud

```bash
# Login to Google Cloud
gcloud auth login

# Set your project (replace YOUR_PROJECT_ID with your actual project ID)
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### Step 2: Configure Docker for Google Cloud

```bash
# Configure Docker to use gcloud as a credential helper
gcloud auth configure-docker
```

### Step 3: Build and Deploy

#### Option A: Using the Automated Script (Recommended)

1. **Edit the deployment script:**
   ```bash
   nano deploy-to-gcloud.sh
   ```

2. **Replace `PROJECT_ID=""` with your actual project ID:**
   ```bash
   PROJECT_ID="your-actual-project-id"
   ```

3. **Run the deployment script:**
   ```bash
   ./deploy-to-gcloud.sh
   ```

#### Option B: Manual Deployment

1. **Build the Docker image:**
   ```bash
   docker build -t furniture-detection-app .
   ```

2. **Tag for Google Container Registry:**
   ```bash
   docker tag furniture-detection-app gcr.io/YOUR_PROJECT_ID/furniture-detection-app:latest
   ```

3. **Push to Google Container Registry:**
   ```bash
   docker push gcr.io/YOUR_PROJECT_ID/furniture-detection-app:latest
   ```

4. **Deploy to Cloud Run:**
   ```bash
   gcloud run deploy furniture-detection-app \
     --image gcr.io/YOUR_PROJECT_ID/furniture-detection-app:latest \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --port 8080 \
     --memory 2Gi \
     --cpu 2 \
     --timeout 300 \
     --max-instances 10 \
     --set-env-vars ROBOFLOW_API_KEY=OCYzLwdUcqDtypAh0OYT
   ```

## 🐳 Docker Configuration Details

### Dockerfile Features:
- **Base Image:** Python 3.9 slim for optimal size
- **Port:** 8080 (Google Cloud Run standard)
- **Dependencies:** All required packages for OpenCV and AI processing
- **Environment:** Production-ready configuration
- **Auto-scaling:** Configured for serverless deployment

### Key Files:
- `Dockerfile` - Container configuration
- `app.py` - Flask web application (port 8080 configured)
- `requirements.txt` - Python dependencies
- `templates/` - Web interface
- `deploy-to-gcloud.sh` - Automated deployment script

## 🌐 After Deployment

1. **Your app will be available at:** `https://furniture-detection-app-[hash]-uc.a.run.app`
2. **Features included:**
   - AI-powered furniture detection
   - Image upload and processing
   - Real-time results with bounding boxes
   - Mobile-responsive design
   - Auto-scaling serverless infrastructure

## 🔧 Configuration Options

### Memory and CPU Settings:
- **Memory:** 2Gi (can be adjusted based on usage)
- **CPU:** 2 cores (can be scaled up/down)
- **Timeout:** 300 seconds (5 minutes for processing)
- **Max Instances:** 10 (prevents runaway costs)

### Environment Variables:
- `PORT=8080` (automatically set by Cloud Run)
- `ROBOFLOW_API_KEY` (set in deployment command)

## 💰 Cost Estimation

Google Cloud Run pricing (pay-per-use):
- **Free tier:** 2 million requests/month
- **CPU:** ~$0.00002400 per vCPU-second
- **Memory:** ~$0.00000250 per GiB-second
- **Requests:** $0.40 per million requests

**Estimated cost for moderate usage:** $5-20/month

## 🛠️ Troubleshooting

### Common Issues:

1. **"Container failed to start"**
   - Check that PORT=8080 is properly configured
   - Verify all dependencies are in requirements.txt

2. **"Permission denied"**
   - Run: `gcloud auth login`
   - Ensure billing is enabled on your project

3. **"Image not found"**
   - Verify your PROJECT_ID is correct
   - Check that the image was pushed successfully

4. **"Service timeout"**
   - Increase timeout: `--timeout 600`
   - Check application logs in Cloud Console

### View Logs:
```bash
gcloud logs read --service=furniture-detection-app --limit=50
```

## 🔄 Updates and Redeployment

To update your app:
1. Make changes to your code
2. Run the deployment script again: `./deploy-to-gcloud.sh`
3. Cloud Run will automatically create a new revision

## 📱 Testing Your Deployment

1. Visit the provided URL
2. Upload a furniture image
3. Verify AI detection results
4. Test on mobile devices

## 🎉 Success!

Your furniture detection app is now running on Google Cloud Run with:
- ✅ Serverless auto-scaling
- ✅ Global CDN
- ✅ HTTPS by default
- ✅ Pay-per-use pricing
- ✅ 99.95% uptime SLA

---

**Need help?** Check the [Google Cloud Run documentation](https://cloud.google.com/run/docs) or contact support.
