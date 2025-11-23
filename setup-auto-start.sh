#!/bin/bash
###############################################################################
# PassiveIncomeMaximizer Auto-Start Setup
#
# This script configures PM2 to auto-start all critical services on reboot
# CRITICAL for position management during unexpected reboots
###############################################################################

set -euo pipefail

echo "=========================================="
echo "PIM Auto-Start Configuration"
echo "=========================================="

cd /home/rford/caelum/ss

# 1. Create log directories
echo "Creating log directories..."
mkdir -p PassiveIncomeMaximizer/logs
mkdir -p finvec/logs
mkdir -p fincoll/logs
mkdir -p senvec/logs
mkdir -p logs

# 2. Stop all PM2 processes
echo "Stopping existing PM2 processes..."
pm2 delete all || true

# 3. Start services using ecosystem config
echo "Starting services from ecosystem config..."
pm2 start pm2-ecosystem.config.js

# 4. Save PM2 process list
echo "Saving PM2 process list..."
pm2 save

# 5. Configure PM2 startup script
echo "Configuring PM2 auto-start..."
echo "You will need to run the following command with sudo:"
echo ""
pm2 startup
echo ""
read -p "Press Enter after running the sudo command above..."

# 6. Verify PM2 processes
echo ""
echo "Current PM2 processes:"
pm2 list

# 7. Set up health monitoring cron job
echo ""
echo "Setting up health monitoring cron job..."
CRON_CMD="*/5 * * * * /home/rford/caelum/ss/health-monitor.sh >> /home/rford/caelum/ss/logs/health-monitor.log 2>&1"
(crontab -l 2>/dev/null | grep -v health-monitor.sh; echo "$CRON_CMD") | crontab -

echo ""
echo "=========================================="
echo "✓ Auto-start configuration complete!"
echo "=========================================="
echo ""
echo "Services will now auto-start on reboot."
echo "Health monitoring runs every 5 minutes."
echo ""
echo "Test with: sudo reboot"
echo "Monitor with: pm2 list"
echo "View logs: pm2 logs"
echo "=========================================="
