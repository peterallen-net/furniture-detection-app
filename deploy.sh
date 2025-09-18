#!/bin/bash

echo "🚀 Furniture Detection App - Serverless Deployment Script"
echo "========================================================="

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

echo "📦 Preparing for deployment..."

# Create .vercelignore if it doesn't exist
if [ ! -f .vercelignore ]; then
    echo "Creating .vercelignore..."
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
EOF
fi

echo "🔧 Setting up environment..."

# Check if user wants to set API key
read -p "Do you want to set your Roboflow API key as an environment variable? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Enter your Roboflow API key: " api_key
    vercel env add ROBOFLOW_API_KEY production <<< "$api_key"
    echo "✅ API key set!"
fi

echo "🌐 Deploying to Vercel..."

# Deploy to production
vercel --prod

echo ""
echo "🎉 Deployment complete!"
echo "Your furniture detection app is now live!"
echo ""
echo "Next steps:"
echo "1. Test your deployed app"
echo "2. Set up a custom domain (optional): vercel domains add yourdomain.com"
echo "3. Enable automatic deployments by connecting your Git repository"
echo ""
echo "For other deployment options, check DEPLOYMENT.md"
