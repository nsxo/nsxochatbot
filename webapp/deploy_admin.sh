#!/bin/bash

echo "🚀 Deploying Admin Dashboard to Railway..."

# Check if railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Please install it first:"
    echo "curl -fsSL https://railway.app/install.sh | sh"
    exit 1
fi

# Build the React app
echo "📦 Building React app..."
npm run build

# Navigate to project root
cd ..

# Check if we're in a Railway project
if [ ! -f "railway.json" ]; then
    echo "❌ Not in a Railway project. Please run 'railway login' and 'railway init' first."
    exit 1
fi

# Deploy using the webapp-specific configuration
echo "🚀 Deploying to Railway..."
railway up --dockerfile Dockerfile

echo "✅ Deployment completed!"
echo "🌐 Your admin dashboard should be available at your Railway URL"
echo ""
echo "📝 Next steps:"
echo "1. Check Railway dashboard for deployment status"
echo "2. Visit your Railway URL to test the admin dashboard"
echo "3. Verify API endpoints are working correctly" 