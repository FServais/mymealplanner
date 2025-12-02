#!/bin/bash
set -e

# Quick backend-only deployment script
# Use this when you only need to update backend code

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
echo "Deploying Backend to $DROPLET_IP"
echo "==========================================="

# Upload backend code
echo ""
echo "Step 1: Uploading backend code..."
rsync -avz --exclude 'venv' --exclude '.git' --exclude '__pycache__' \
    --exclude 'sql_app.db' --exclude '*.pyc' \
    $LOCAL_DIR/backend/ root@$DROPLET_IP:$APP_DIR/backend/
ssh root@$DROPLET_IP "chown -R $APP_USER:$APP_USER $APP_DIR/backend"
echo "✓ Backend code uploaded"

# Install dependencies (if requirements.txt changed)
echo ""
echo "Step 2: Updating backend dependencies..."
ssh root@$DROPLET_IP "cd $APP_DIR/backend && source venv/bin/activate && pip install -r requirements.txt"
echo "✓ Dependencies updated"

# Restart backend service
echo ""
echo "Step 3: Restarting backend service..."
ssh root@$DROPLET_IP "systemctl restart mealplanner-backend"
sleep 3
ssh root@$DROPLET_IP "systemctl status mealplanner-backend --no-pager"
echo "✓ Backend service restarted"

echo ""
echo "==========================================="
echo "✓ Backend deployment complete!"
echo "==========================================="
echo ""
echo "Useful commands:"
echo "  - View logs: ssh root@$DROPLET_IP 'journalctl -u mealplanner-backend -f'"
echo "  - Check status: ssh root@$DROPLET_IP 'systemctl status mealplanner-backend'"
echo ""
