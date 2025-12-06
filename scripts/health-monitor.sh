#!/bin/bash
###############################################################################
# PassiveIncomeMaximizer Health Monitor
#
# CRITICAL: Monitors system health and restarts failed services
# Essential for managing active positions during failures
#
# Usage: Run via cron every 5 minutes:
#   */5 * * * * /home/rford/caelum/ss/health-monitor.sh >> /home/rford/caelum/ss/logs/health-monitor.log 2>&1
###############################################################################

set -euo pipefail

# Configuration
LOG_DIR="/home/rford/caelum/ss/logs"
ALERT_EMAIL="${ALERT_EMAIL:-}"
SLACK_WEBHOOK="${SLACK_WEBHOOK:-}"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Timestamp for logging
timestamp() {
  date '+%Y-%m-%d %H:%M:%S'
}

log() {
  echo "[$(timestamp)] $*"
}

alert() {
  local message="$1"
  log "ALERT: $message"

  # Send email if configured
  if [[ -n "$ALERT_EMAIL" ]]; then
    echo "$message" | mail -s "[PIM] System Alert" "$ALERT_EMAIL" || true
  fi

  # Send Slack notification if configured
  if [[ -n "$SLACK_WEBHOOK" ]]; then
    curl -X POST -H 'Content-type: application/json' \
      --data "{\"text\":\"[PIM Alert] $message\"}" \
      "$SLACK_WEBHOOK" || true
  fi
}

# Check if a service is healthy
check_service() {
  local name="$1"
  local url="$2"
  local timeout="${3:-5}"

  if curl -sf --max-time "$timeout" "$url" > /dev/null 2>&1; then
    log "✓ $name is healthy"
    return 0
  else
    log "✗ $name is DOWN"
    return 1
  fi
}

# Check PM2 process
check_pm2_process() {
  local name="$1"

  if pm2 jlist | jq -e ".[] | select(.name == \"$name\" and .pm2_env.status == \"online\")" > /dev/null 2>&1; then
    log "✓ PM2 process '$name' is running"
    return 0
  else
    log "✗ PM2 process '$name' is NOT running"
    return 1
  fi
}

# Restart PM2 process
restart_pm2_process() {
  local name="$1"
  log "Restarting PM2 process '$name'..."
  pm2 restart "$name" || pm2 start "$name" || {
    alert "Failed to restart $name - manual intervention required!"
    return 1
  }
  sleep 10  # Give it time to start
  return 0
}

# Main health check
log "========================================="
log "Starting health check..."
log "========================================="

FAILED_SERVICES=()
CRITICAL_FAILURE=false

# ============================================================================
# 1. Check PIM Server (CRITICAL - manages active positions)
# ============================================================================
log "Checking PIM Server..."
if ! check_pm2_process "pim-server"; then
  alert "CRITICAL: PIM Server is down! Active positions may be unmanaged!"
  CRITICAL_FAILURE=true
  FAILED_SERVICES+=("pim-server")
  restart_pm2_process "pim-server"
elif ! check_service "PIM Server" "http://10.32.3.27:5000/api/health/check"; then
  alert "CRITICAL: PIM Server not responding to health checks!"
  CRITICAL_FAILURE=true
  FAILED_SERVICES+=("pim-server")
  restart_pm2_process "pim-server"
fi

# ============================================================================
# 2. Check FinVec Inference Server (CRITICAL - for trading decisions)
# ============================================================================
log "Checking FinVec Inference Server..."
if ! check_pm2_process "inference-server-v5"; then
  alert "WARNING: FinVec Inference Server is down!"
  FAILED_SERVICES+=("inference-server-v5")
  restart_pm2_process "inference-server-v5"
fi

# ============================================================================
# 3. Check FinColl Server (HIGH PRIORITY)
# ============================================================================
log "Checking FinColl Server..."
if ! check_pm2_process "fincoll-server"; then
  alert "WARNING: FinColl Server is down!"
  FAILED_SERVICES+=("fincoll-server")
  restart_pm2_process "fincoll-server"
elif ! check_service "FinColl" "http://10.32.3.27:8001/health"; then
  alert "WARNING: FinColl not responding!"
  FAILED_SERVICES+=("fincoll-server")
  restart_pm2_process "fincoll-server"
fi

# ============================================================================
# 4. Check SenVec Aggregator (MEDIUM PRIORITY)
# ============================================================================
log "Checking SenVec Aggregator..."
if ! check_pm2_process "senvec-aggregator"; then
  log "WARNING: SenVec Aggregator is down (non-critical)"
  FAILED_SERVICES+=("senvec-aggregator")
  # Don't auto-restart - it's optional
elif ! check_service "SenVec" "http://10.32.3.27:18000/health" 3; then
  log "WARNING: SenVec not responding (non-critical)"
fi

# ============================================================================
# 5. Check Infrastructure Dependencies
# ============================================================================
log "Checking Redis..."
if ! nc -z 10.32.3.27 6379 2>/dev/null; then
  alert "WARNING: Redis on 10.32.3.27:6379 is not accessible!"
  FAILED_SERVICES+=("redis")
fi

log "Checking Qdrant..."
if ! check_service "Qdrant" "http://10.32.3.27:6333/" 3; then
  alert "WARNING: Qdrant on 10.32.3.27:6333 is not accessible!"
  FAILED_SERVICES+=("qdrant")
fi

# ============================================================================
# 6. Check for Active Positions (CRITICAL CHECK)
# ============================================================================
log "Checking for active positions..."
ACTIVE_POSITIONS=$(curl -sf http://10.32.3.27:5000/api/positions 2>/dev/null | jq -r '.count // 0' || echo "0")
log "Active positions: $ACTIVE_POSITIONS"

if [[ "$ACTIVE_POSITIONS" -gt 0 ]] && [[ "$CRITICAL_FAILURE" = true ]]; then
  alert "CRITICAL ALERT: $ACTIVE_POSITIONS active positions with system failures! Immediate attention required!"
fi

# ============================================================================
# Summary
# ============================================================================
log "========================================="
if [[ ${#FAILED_SERVICES[@]} -eq 0 ]]; then
  log "✓ All systems operational"
else
  log "✗ Failed services: ${FAILED_SERVICES[*]}"
  if [[ "$CRITICAL_FAILURE" = true ]]; then
    log "CRITICAL FAILURE DETECTED - Active positions may be at risk!"
  fi
fi
log "========================================="

# Exit with error if critical failure
[[ "$CRITICAL_FAILURE" = false ]] && exit 0 || exit 1
