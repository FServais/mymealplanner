#!/bin/bash
set -e

# Quick fix script to fix the missing gunicorn dependency on the server
# Run this if the backend service failed to start

if [ $# -eq 0 ]; then
    echo "Usage: $0 <droplet-ip-address>"
    echo "Example: $0 167.71.123.45"
    exit 1
fi

DROPLET_IP=$1
APP_USER="mealplanner"
APP_DIR="/home/mealplanner/mymealplanner/backend"

echo "==========================================="
echo "Fixing Backend Service on $DROPLET_IP"
echo "==========================================="

# Step 1: Upload updated requirements.txt
echo ""
echo "Step 1: Uploading updated requirements.txt..."
scp ../backend/requirements.txt root@$DROPLET_IP:$APP_DIR/requirements.txt
echo "✓ Requirements uploaded"

# Step 2: Install gunicorn
echo ""
echo "Step 2: Installing gunicorn..."
ssh root@$DROPLET_IP "cd $APP_DIR && source venv/bin/activate && pip install gunicorn"
echo "✓ Gunicorn installed"

# Step 3: Restart backend service
echo ""
echo "Step 3: Restarting backend service..."
ssh root@$DROPLET_IP "systemctl restart mealplanner-backend"
sleep 3
echo "✓ Service restarted"

# Step 4: Check status
echo ""
echo "Step 4: Checking service status..."
ssh root@$DROPLET_IP "systemctl status mealplanner-backend --no-pager --lines=10" || {
    echo ""
    echo "⚠️  Service failed to start. Viewing logs..."
    ssh root@$DROPLET_IP "journalctl -u mealplanner-backend -n 30 --no-pager"
    exit 1
}

echo ""
echo "==========================================="
echo "✓ Backend service fixed!"
echo "==========================================="
echo ""
echo "Your application should now be running at: http://$DROPLET_IP"
echo ""
