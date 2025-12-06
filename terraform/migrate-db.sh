#!/bin/bash
set -e

# Script to run database migration on remote server

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
echo "Migrating Remote Database at $DROPLET_IP"
echo "==========================================="

# 1. Upload migration script
echo ""
echo "Step 1: Uploading migration script..."
rsync -avz $LOCAL_DIR/backend/migrate_tags_color.py root@$DROPLET_IP:$APP_DIR/backend/
ssh root@$DROPLET_IP "chown $APP_USER:$APP_USER $APP_DIR/backend/migrate_tags_color.py"
echo "✓ Migration script uploaded"

# 2. Upload backend code (just to be safe that models match)
echo ""
echo "Step 2: Syncing backend code..."
rsync -avz --exclude 'venv' --exclude '.git' --exclude '__pycache__' \
    --exclude 'sql_app.db' --exclude '*.pyc' \
    $LOCAL_DIR/backend/ root@$DROPLET_IP:$APP_DIR/backend/
ssh root@$DROPLET_IP "chown -R $APP_USER:$APP_USER $APP_DIR/backend"
echo "✓ Backend code synced"

# 3. Run migration
echo ""
echo "Step 3: Running migration..."
ssh root@$DROPLET_IP "cd $APP_DIR/backend && source venv/bin/activate && python3 migrate_tags_color.py"
echo "✓ Migration command executed"

# 4. Restart backend service
echo ""
echo "Step 4: Restarting backend service..."
ssh root@$DROPLET_IP "systemctl restart mealplanner-backend"
echo "✓ Service restarted"

echo ""
echo "==========================================="
echo "✓ Migration Complete!"
echo "==========================================="
