# Serverless Deployment Guide

This guide covers multiple options for deploying your furniture detection web app serverlessly.

## Option 1: Vercel (Recommended) ⭐

Vercel is the easiest option for Flask apps with excellent performance and free tier.

### Prerequisites
- Install Vercel CLI: `npm install -g vercel`
- Create account at [vercel.com](https://vercel.com)

### Deployment Steps
1. **Login to Vercel**
   ```bash
   vercel login
   ```

2. **Deploy from project directory**
   ```bash
   vercel
   ```

3. **Follow prompts:**
   - Set up and deploy? `Y`
   - Which scope? Choose your account
   - Link to existing project? `N`
   - Project name? `furniture-detection-app`
   - Directory? `./`
   - Override settings? `N`

4. **Environment Variables (if needed)**
   ```bash
   vercel env add ROBOFLOW_API_KEY
   ```

### Features
- ✅ Free tier with generous limits
- ✅ Automatic HTTPS
- ✅ Global CDN
- ✅ Easy custom domains
- ✅ Automatic deployments from Git

---

## Option 2: Netlify Functions

Convert to Netlify Functions for serverless deployment.

### Setup
1. Create `netlify.toml`:
   ```toml
   [build]
     functions = "netlify/functions"
     publish = "dist"

   [[redirects]]
     from = "/api/*"
     to = "/.netlify/functions/:splat"
     status = 200
   ```

2. Move Flask logic to `netlify/functions/app.py`
3. Deploy: `netlify deploy --prod`

---

## Option 3: AWS Lambda + API Gateway

Use AWS SAM or Serverless Framework for AWS deployment.

### Using AWS SAM
1. **Install AWS SAM CLI**
2. **Create `template.yaml`:**
   ```yaml
   AWSTemplateFormatVersion: '2010-09-09'
   Transform: AWS::Serverless-2016-10-31
   
   Resources:
     FurnitureDetectionApi:
       Type: AWS::Serverless::Function
       Properties:
         CodeUri: .
         Handler: app.lambda_handler
         Runtime: python3.9
         Events:
           Api:
             Type: Api
             Properties:
               Path: /{proxy+}
               Method: ANY
   ```

3. **Deploy:**
   ```bash
   sam build
   sam deploy --guided
   ```

---

## Option 4: Google Cloud Functions

Deploy as a Cloud Function with HTTP trigger.

### Setup
1. **Install Google Cloud SDK**
2. **Create `main.py` wrapper:**
   ```python
   from app import app
   
   def furniture_detection(request):
       return app(request.environ, lambda *args: None)
   ```

3. **Deploy:**
   ```bash
   gcloud functions deploy furniture-detection \
     --runtime python39 \
     --trigger-http \
     --allow-unauthenticated
   ```

---

## Option 5: Railway

Simple deployment with built-in database support.

### Setup
1. **Install Railway CLI:** `npm install -g @railway/cli`
2. **Login:** `railway login`
3. **Deploy:** `railway up`

### Features
- ✅ Simple deployment
- ✅ Built-in database support
- ✅ Automatic HTTPS
- ✅ Environment variables

---

## Recommended Approach: Vercel

For your Flask furniture detection app, **Vercel is the best choice** because:

1. **Zero Configuration**: Works out of the box with Flask
2. **Free Tier**: Generous limits for personal projects
3. **Performance**: Global CDN and edge functions
4. **Easy Setup**: Single command deployment
5. **Git Integration**: Automatic deployments from GitHub/GitLab

### Quick Start with Vercel
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy (from your project directory)
vercel

# That's it! Your app will be live at a vercel.app URL
```

### Custom Domain (Optional)
```bash
vercel --prod
vercel domains add yourdomain.com
```

---

## Important Notes

### File Upload Considerations
- **Vercel**: 4.5MB request limit (sufficient for most images)
- **Netlify**: 6MB limit for functions
- **AWS Lambda**: 6MB payload limit
- **Google Cloud**: 10MB limit

### Environment Variables
Remember to set your Roboflow API key:
```bash
vercel env add ROBOFLOW_API_KEY
# Enter your API key when prompted
```

### Static Files
Your `templates/` and `static/` directories will be automatically handled by most platforms.

Choose Vercel for the easiest deployment experience! 🚀
