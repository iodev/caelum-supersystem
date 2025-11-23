#!/bin/bash
# Setup Weekly Cron Jobs for Volume Backups
# This script configures cron to run weekly backups for both:
# - Caelum Unified volumes (Sundays at 2 AM)
# - PIM volumes (Sundays at 3 AM)

set -e

echo "Setting up weekly backup cron jobs..."

# Create temporary crontab file
TEMP_CRON=$(mktemp)

# Get existing crontab (if any)
crontab -l 2>/dev/null > "$TEMP_CRON" || true

# Remove any existing backup entries (to avoid duplicates)
sed -i '/backup-volumes\.sh/d' "$TEMP_CRON"
sed -i '/backup-pim-volumes\.sh/d' "$TEMP_CRON"

# Add header comment
if ! grep -q "# Caelum & PIM Weekly Volume Backups" "$TEMP_CRON"; then
    cat >> "$TEMP_CRON" <<'EOF'

# Caelum & PIM Weekly Volume Backups
# Runs every Sunday at 2 AM (Caelum) and 3 AM (PIM)
EOF
fi

# Add Caelum backup (Sundays at 2 AM)
echo "0 2 * * 0 /home/rford/caelum/ss/caelum-unified/scripts/backup-volumes.sh >> /mnt/e/docker-volumes/caelum/backup.log 2>&1" >> "$TEMP_CRON"

# Add PIM backup (Sundays at 3 AM)
echo "0 3 * * 0 /home/rford/caelum/ss/PassiveIncomeMaximizer/scripts/backup-pim-volumes.sh >> /mnt/e/docker-volumes/pim/backup.log 2>&1" >> "$TEMP_CRON"

# Install the new crontab
crontab "$TEMP_CRON"

# Clean up
rm "$TEMP_CRON"

echo ""
echo "✓ Weekly backup cron jobs configured:"
echo "  - Caelum volumes: Sundays at 2:00 AM"
echo "  - PIM volumes: Sundays at 3:00 AM"
echo ""
echo "Current crontab:"
crontab -l
echo ""
echo "Backup directories:"
echo "  - Caelum: /mnt/e/docker-volumes/caelum/"
echo "  - PIM: /mnt/e/docker-volumes/pim/"
echo ""
echo "To verify backups are running, check log files:"
echo "  tail -50 /mnt/e/docker-volumes/caelum/backup.log"
echo "  tail -50 /mnt/e/docker-volumes/pim/backup.log"
