#!/bin/bash
set -e

# Frontend-only deployment script
# Matches the style of deploy-initial.sh (builds on server)

if [ $# -eq 0 ]; then
    echo "Usage: $0 <droplet-ip-address>"
    echo "Example: $0 64.227.76.113"
    exit 1
fi

DROPLET_IP=$1
APP_USER="mealplanner"
APP_DIR="/home/mealplanner/mymealplanner"
LOCAL_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "==========================================="
echo "Deploying Frontend to $DROPLET_IP"
echo "==========================================="

# 1. Upload frontend code
echo ""
echo "Step 1: Uploading frontend source code..."
rsync -avz --exclude 'node_modules' --exclude 'dist' --exclude '.git' \
    $LOCAL_DIR/frontend/ root@$DROPLET_IP:$APP_DIR/frontend/

ssh root@$DROPLET_IP "chown -R $APP_USER:$APP_USER $APP_DIR/frontend"
echo "✓ Frontend code uploaded"

# 2. Build on server
echo ""
echo "Step 2: Building frontend on server..."
ssh root@$DROPLET_IP "cd $APP_DIR/frontend && npm install && VITE_API_URL=https://meal.servais-devos.com npm run build"
echo "✓ Build complete"

# 3. Deploy to web root
echo ""
echo "Step 3: Deploying to web root..."
ssh root@$DROPLET_IP "rm -rf /var/www/mealplanner/* && cp -r $APP_DIR/frontend/dist/* /var/www/mealplanner/ && chown -R www-data:www-data /var/www/mealplanner"
echo "✓ Deployed to /var/www/mealplanner"

echo ""
echo "==========================================="
echo "✓ Frontend deployment complete!"
echo "==========================================="
echo ""
echo "🌍 Visit https://meal.servais-devos.com"
echo ""
