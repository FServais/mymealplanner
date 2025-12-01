#!/bin/bash
set -e

# Migration script to upload local database and images to the cloud instance
# This preserves your local recipes, meal plans, and cached images

if [ $# -eq 0 ]; then
    echo "Usage: $0 <droplet-ip-address>"
    echo "Example: $0 167.71.123.45"
    exit 1
fi

DROPLET_IP=$1
APP_USER="mealplanner"
APP_DIR="/home/mealplanner/mymealplanner/backend"
LOCAL_BACKEND="$(cd "$(dirname "$0")/../backend" && pwd)"

echo "==========================================="
echo "Migrating Local Data to $DROPLET_IP"
echo "==========================================="

# Check if local database exists
if [ ! -f "$LOCAL_BACKEND/sql_app.db" ]; then
    echo "❌ No local database found at $LOCAL_BACKEND/sql_app.db"
    echo "   Make sure you're running this from the terraform directory"
    echo "   and that you have a local database to migrate."
    exit 1
fi

LOCAL_DB_SIZE=$(du -h "$LOCAL_BACKEND/sql_app.db" | cut -f1)
echo "Found local database: $LOCAL_DB_SIZE"

# Count local images
if [ -d "$LOCAL_BACKEND/data/images" ]; then
    IMAGE_COUNT=$(find "$LOCAL_BACKEND/data/images" -type f | wc -l)
    echo "Found $IMAGE_COUNT cached images to migrate"
else
    IMAGE_COUNT=0
    echo "No images directory found, will create empty one"
fi

echo ""
read -p "Continue with migration? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Migration cancelled"
    exit 0
fi

# Step 1: Backup remote database (if exists)
echo ""
echo "Step 1: Backing up remote database (if exists)..."
ssh root@$DROPLET_IP "if [ -f $APP_DIR/sql_app.db ]; then cp $APP_DIR/sql_app.db $APP_DIR/sql_app.db.backup.\$(date +%Y%m%d-%H%M%S); echo 'Backup created'; else echo 'No remote database to backup'; fi"
echo "✓ Backup complete"

# Step 2: Stop backend service
echo ""
echo "Step 2: Stopping backend service..."
ssh root@$DROPLET_IP "systemctl stop mealplanner-backend || true"
echo "✓ Service stopped"

# Step 3: Upload database
echo ""
echo "Step 3: Uploading database..."
scp "$LOCAL_BACKEND/sql_app.db" root@$DROPLET_IP:$APP_DIR/sql_app.db
echo "✓ Database uploaded"

# Step 4: Upload images (if any)
if [ $IMAGE_COUNT -gt 0 ]; then
    echo ""
    echo "Step 4: Uploading images..."
    ssh root@$DROPLET_IP "mkdir -p $APP_DIR/data/images"
    rsync -avz --progress "$LOCAL_BACKEND/data/images/" root@$DROPLET_IP:$APP_DIR/data/images/
    echo "✓ Images uploaded"
else
    echo ""
    echo "Step 4: Creating images directory..."
    ssh root@$DROPLET_IP "mkdir -p $APP_DIR/data/images"
    echo "✓ Images directory created"
fi

# Step 5: Fix permissions
echo ""
echo "Step 5: Fixing permissions..."
ssh root@$DROPLET_IP "chown -R $APP_USER:$APP_USER $APP_DIR/sql_app.db $APP_DIR/data"
echo "✓ Permissions fixed"

# Step 6: Start backend service
echo ""
echo "Step 6: Starting backend service..."
ssh root@$DROPLET_IP "systemctl start mealplanner-backend"
sleep 2
ssh root@$DROPLET_IP "systemctl status mealplanner-backend --no-pager --lines=0" || {
    echo ""
    echo "⚠️  Service may have failed to start. Checking logs..."
    ssh root@$DROPLET_IP "journalctl -u mealplanner-backend -n 20 --no-pager"
    exit 1
}
echo "✓ Service started"

# Step 7: Verify migration
echo ""
echo "Step 7: Verifying migration..."
REMOTE_DB_SIZE=$(ssh root@$DROPLET_IP "du -h $APP_DIR/sql_app.db | cut -f1")
REMOTE_IMAGE_COUNT=$(ssh root@$DROPLET_IP "find $APP_DIR/data/images -type f 2>/dev/null | wc -l")

echo "  Local database:  $LOCAL_DB_SIZE"
echo "  Remote database: $REMOTE_DB_SIZE"
echo "  Local images:    $IMAGE_COUNT"
echo "  Remote images:   $REMOTE_IMAGE_COUNT"

if [ "$LOCAL_DB_SIZE" = "$REMOTE_DB_SIZE" ] && [ "$IMAGE_COUNT" -eq "$REMOTE_IMAGE_COUNT" ]; then
    echo "✓ Migration verified"
else
    echo "⚠️  Size mismatch detected, please verify manually"
fi

echo ""
echo "==========================================="
echo "✓ Migration complete!"
echo "==========================================="
echo ""
echo "Your recipes and images are now available at: http://$DROPLET_IP"
echo ""
echo "Notes:"
echo "  - Remote database backups are stored at: $APP_DIR/sql_app.db.backup.*"
echo "  - To view logs: ssh root@$DROPLET_IP 'journalctl -u mealplanner-backend -f'"
echo "  - To restore a backup: ssh root@$DROPLET_IP 'cp $APP_DIR/sql_app.db.backup.YYYYMMDD-HHMMSS $APP_DIR/sql_app.db'"
echo ""
