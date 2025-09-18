#!/bin/bash

echo "📦 Preparing your furniture detection app for upload..."

# Create a clean directory for deployment
mkdir -p furniture-detection-deploy
cd furniture-detection-deploy

# Copy essential files
cp ../app.py .
cp ../requirements.txt .
cp ../vercel.json .
cp -r ../templates .

# Create .vercelignore
cat > .vercelignore << EOF
.venv/
__pycache__/
*.pyc
.env
.DS_Store
node_modules/
uploads/
outputs/
test_inventory.html
living-room.jpg
detection_results.json
output_with_detections.jpg
notebooks/
docs/
scripts/
data/
models/
.git/
EOF

# Create README for deployment
cat > README.md << EOF
# Furniture Detection App

A mobile-first web application for detecting and cataloging furniture using AI.

## Features
- 📱 Mobile-first responsive design
- 📋 Professional inventory list format
- ✅ Interactive checkboxes for verification
- 🎨 Clean, center-aligned interface
- 🚀 AI-powered furniture detection

## Deployment
This app is ready to deploy on:
- Vercel (recommended)
- Railway
- Render
- Netlify
- AWS Lambda

## Environment Variables
Set \`ROBOFLOW_API_KEY\` to your Roboflow API key.

## Local Development
\`\`\`bash
pip install -r requirements.txt
python app.py
\`\`\`

Visit http://localhost:5002
EOF

cd ..

# Create zip file
echo "🗜️ Creating deployment package..."
zip -r furniture-detection-app.zip furniture-detection-deploy/

echo "✅ Deployment package ready!"
echo ""
echo "📁 Files created:"
echo "   - furniture-detection-deploy/ (clean project folder)"
echo "   - furniture-detection-app.zip (upload this to any platform)"
echo ""
echo "🚀 Next steps:"
echo "1. Go to vercel.com, railway.app, or render.com"
echo "2. Upload furniture-detection-app.zip"
echo "3. Set ROBOFLOW_API_KEY environment variable"
echo "4. Deploy!"
echo ""
echo "Your app will be live in minutes! 🎉"
