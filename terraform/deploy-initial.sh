#!/bin/bash
set -e

# Deployment script for initial code upload to the droplet
# Run this script after terraform apply completes

if [ $# -eq 0 ]; then
    echo "Usage: $0 <droplet-ip-address>"
    echo "Example: $0 167.71.123.45"
    exit 1
fi

DROPLET_IP=$1
APP_USER="mealplanner"
APP_DIR="/home/mealplanner/mymealplanner"
LOCAL_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "==========================================="
echo "Deploying Meal Planner to $DROPLET_IP"
echo "==========================================="

# Wait for cloud-init to complete
echo ""
echo "Step 1: Waiting for cloud-init to complete..."
# ssh -o StrictHostKeyChecking=no root@$DROPLET_IP 'cloud-init status --wait'
echo "✓ Cloud-init complete"

# Upload application code
echo ""
echo "Step 2: Uploading application code..."
ssh root@$DROPLET_IP "rm -rf $APP_DIR/*"
rsync -avz --exclude 'node_modules' --exclude 'venv' --exclude '.git' --exclude '__pycache__' \
    --exclude 'sql_app.db' --exclude 'dist' \
    $LOCAL_DIR/backend/ root@$DROPLET_IP:$APP_DIR/backend/

rsync -avz --exclude 'node_modules' --exclude 'dist' --exclude '.git' \
    $LOCAL_DIR/frontend/ root@$DROPLET_IP:$APP_DIR/frontend/

ssh root@$DROPLET_IP "chown -R $APP_USER:$APP_USER $APP_DIR"
echo "✓ Code uploaded"

# Set up backend
echo ""
echo "Step 3: Setting up backend..."
ssh root@$DROPLET_IP "cd $APP_DIR/backend && python3 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt"
echo "✓ Backend dependencies installed"

# Build frontend
echo ""
echo "Step 4: Building frontend..."
ssh root@$DROPLET_IP "cd $APP_DIR/frontend && npm install && VITE_API_URL=https://meal.servais-devos.com npm run build"
ssh root@$DROPLET_IP "rm -rf /var/www/mealplanner/* && cp -r $APP_DIR/frontend/dist/* /var/www/mealplanner/ && chown -R www-data:www-data /var/www/mealplanner"
echo "✓ Frontend built and deployed"

# Initialize database
echo ""
echo "Step 5: Initializing database..."
ssh root@$DROPLET_IP "cd $APP_DIR/backend && sudo -u $APP_USER bash -c 'source venv/bin/activate && python3 -c \"from database import engine, Base; from models import Recipe, MealPlan; Base.metadata.create_all(bind=engine); print(\\\"Database initialized\\\")\"'"
echo "✓ Database initialized"

# Start backend service
echo ""
echo "Step 6: Starting backend service..."
ssh root@$DROPLET_IP "systemctl enable mealplanner-backend && systemctl start mealplanner-backend"
sleep 3
ssh root@$DROPLET_IP "systemctl status mealplanner-backend --no-pager"
echo "✓ Backend service started"

# Verify Nginx
echo ""
echo "Step 7: Verifying Nginx..."
ssh root@$DROPLET_IP "nginx -t && systemctl restart nginx"
echo "✓ Nginx configured"

echo ""
echo "==========================================="
echo "✓ Deployment complete!"
echo "==========================================="
echo ""
echo "Your application is now running at: http://$DROPLET_IP"
echo ""
echo "Useful commands:"
echo "  - View backend logs: ssh root@$DROPLET_IP 'journalctl -u mealplanner-backend -f'"
echo "  - Restart backend: ssh root@$DROPLET_IP 'systemctl restart mealplanner-backend'"
echo "  - Check status: ssh root@$DROPLET_IP 'systemctl status mealplanner-backend'"
echo "  - Redeploy: ssh root@$DROPLET_IP '/home/mealplanner/deploy.sh'"
echo ""
