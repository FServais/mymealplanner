# Data Migration Guide

This guide explains how to migrate your local data to the DigitalOcean cloud instance.

## What Gets Migrated

- **SQLite Database** (`sql_app.db`): All your recipes, meal plans, and ingredients
- **Recipe Images** (`backend/data/images/`): Cached thumbnails from Efarmz

## Prerequisites

- ✅ Terraform infrastructure deployed (`terraform apply` completed)
- ✅ Initial deployment successful (`deploy-initial.sh` completed)
- ✅ Backend service fixed (run `fix-backend.sh` if needed)
- ✅ Local database exists at `backend/sql_app.db`

## Migration Steps

### 1. Fix Backend Service (If Needed)

If your initial deployment failed with a service error:

```bash
cd terraform
./fix-backend.sh <DROPLET_IP>
```

This installs the missing `gunicorn` package and restarts the service.

### 2. Run Migration Script

```bash
cd terraform
./migrate-data.sh <DROPLET_IP>
```

The script will:
1. ✅ Check for local database and images
2. ✅ Show you what will be migrated
3. ✅ Ask for confirmation
4. ✅ Backup remote database (if exists)
5. ✅ Stop backend service
6. ✅ Upload database file
7. ✅ Upload images (with progress)
8. ✅ Fix permissions
9. ✅ Restart backend service
10. ✅ Verify migration success

### 3. Verify Migration

After migration completes, visit `http://<DROPLET_IP>` and verify:
- Your recipes are visible
- Recipe thumbnails load correctly
- Meal plans are present
- Everything works as expected

## Manual Migration (Alternative)

If you prefer to migrate manually:

```bash
# 1. Backup remote database
ssh root@<DROPLET_IP> 'cp /home/mealplanner/mymealplanner/backend/sql_app.db /home/mealplanner/mymealplanner/backend/sql_app.db.backup'

# 2. Stop backend
ssh root@<DROPLET_IP> 'systemctl stop mealplanner-backend'

# 3. Upload database
scp backend/sql_app.db root@<DROPLET_IP>:/home/mealplanner/mymealplanner/backend/

# 4. Upload images (if you have them)
rsync -avz backend/data/images/ root@<DROPLET_IP>:/home/mealplanner/mymealplanner/backend/data/images/

# 5. Fix permissions
ssh root@<DROPLET_IP> 'chown -R mealplanner:mealplanner /home/mealplanner/mymealplanner/backend/sql_app.db /home/mealplanner/mymealplanner/backend/data'

# 6. Start backend
ssh root@<DROPLET_IP> 'systemctl start mealplanner-backend'
```

## Backup and Restore

### View Available Backups

```bash
ssh root@<DROPLET_IP> 'ls -lh /home/mealplanner/mymealplanner/backend/sql_app.db.backup.*'
```

### Restore from Backup

```bash
# Stop service
ssh root@<DROPLET_IP> 'systemctl stop mealplanner-backend'

# Restore backup (replace timestamp)
ssh root@<DROPLET_IP> 'cp /home/mealplanner/mymealplanner/backend/sql_app.db.backup.20251201-133000 /home/mealplanner/mymealplanner/backend/sql_app.db'

# Start service
ssh root@<DROPLET_IP> 'systemctl start mealplanner-backend'
```

### Download Current Database

To download the current database from the server:

```bash
scp root@<DROPLET_IP>:/home/mealplanner/mymealplanner/backend/sql_app.db ./sql_app.db.$(date +%Y%m%d-%H%M%S)
```

## Troubleshooting

### "No local database found"

Make sure you're running the script from the `terraform/` directory and that `../backend/sql_app.db` exists.

### Service Failed to Start After Migration

Check the logs:
```bash
ssh root@<DROPLET_IP> 'journalctl -u mealplanner-backend -n 50'
```

Common issues:
- **Permission denied**: Run `ssh root@<DROPLET_IP> 'chown -R mealplanner:mealplanner /home/mealplanner/mymealplanner/backend'`
- **Database locked**: Make sure no other process is using the database
- **Disk full**: Check disk space with `ssh root@<DROPLET_IP> 'df -h'`

### Database Size Mismatch

If the migration script reports a size mismatch:
```bash
# Check local size
du -h backend/sql_app.db

# Check remote size
ssh root@<DROPLET_IP> 'du -h /home/mealplanner/mymealplanner/backend/sql_app.db'
```

If they're different, try uploading again or use the manual method.

### Images Not Appearing

Check if images were uploaded:
```bash
ssh root@<DROPLET_IP> 'ls -lh /home/mealplanner/mymealplanner/backend/data/images/ | head -20'
```

Check permissions:
```bash
ssh root@<DROPLET_IP> 'ls -ld /home/mealplanner/mymealplanner/backend/data/images'
```

Should show `mealplanner mealplanner` as owner.

## Data Sync Strategy

For keeping local and remote in sync:

### Option 1: Always Work Remotely
Use the cloud instance as your primary and download backups periodically.

### Option 2: Periodic Migrations
Work locally and run `migrate-data.sh` when you want to publish changes.

### Option 3: Git-Based Workflow
Use git to version control your database:
```bash
# On your local machine
git add backend/sql_app.db
git commit -m "Updated recipes"
git push

# On the server
ssh root@<DROPLET_IP>
cd /home/mealplanner/mymealplanner
git pull
systemctl restart mealplanner-backend
```

**Note**: SQLite databases in git can get large. Consider using Git LFS.

## Best Practices

1. ✅ **Always backup before migrating**: The script does this automatically
2. ✅ **Test locally first**: Make sure your local app works before migrating
3. ✅ **Verify after migration**: Check that all data is accessible
4. ✅ **Keep backups**: Download periodic backups of your cloud database
5. ✅ **Monitor disk space**: SQLite databases and images can grow

## Security Notes

- Database contains all your recipes and meal plans
- Images are publicly accessible via the `/images/thumbnails/` endpoint
- No sensitive data should be in the database
- Backups are stored on the same server (consider off-site backups for production)
