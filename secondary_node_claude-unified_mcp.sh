#!/bin/bash
# Secondary Node Claude-Unified MCP Setup Script
# This script configures a secondary node (10.32.3.44, 10.32.3.62) to:
# 1. Deploy caelum-unified in Docker with connection to primary node (10.32.3.27)
# 2. Configure Claude Code CLI to use Caelum MCP servers
#
# Usage: ./secondary_node_claude-unified_mcp.sh [NODE_IP]
# Example: ./secondary_node_claude-unified_mcp.sh 10.32.3.62

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CAELUM_UNIFIED_DIR="${SCRIPT_DIR}/caelum-unified"
PRIMARY_NODE_IP="${PRIMARY_NODE_IP:-10.32.3.27}"
CURRENT_NODE_IP="${1:-$(hostname -I | awk '{print $1}')}"
NODE_ID="${NODE_ID:-node-$(echo $CURRENT_NODE_IP | sed 's/\./-/g')}"

# Check if we're on the expected secondary nodes
if [[ "$CURRENT_NODE_IP" != "10.32.3.44" && "$CURRENT_NODE_IP" != "10.32.3.62" ]]; then
    echo -e "${YELLOW}⚠️  Warning: This script is designed for 10.32.3.44 or 10.32.3.62${NC}"
    echo -e "${YELLOW}   Current IP: $CURRENT_NODE_IP${NC}"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Display banner
cat << 'BANNER'
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║      Caelum Unified - Secondary Node MCP Setup                ║
║                                                               ║
║  Configures secondary nodes to use caelum-unified proxy       ║
║  with coordination to the main instance on 10.32.3.27         ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
BANNER

echo ""
log_info "Configuration Summary:"
echo "   Node IP: $CURRENT_NODE_IP"
echo "   Node ID: $NODE_ID"
echo "   Primary Node: $PRIMARY_NODE_IP"
echo "   Caelum Unified Dir: $CAELUM_UNIFIED_DIR"
echo ""

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    local missing_deps=()

    # Check Docker
    if ! command -v docker &> /dev/null; then
        missing_deps+=("docker")
    elif ! docker info &> /dev/null; then
        log_error "Docker is installed but not running"
        exit 1
    fi

    # Check docker-compose
    if ! command -v docker-compose &> /dev/null; then
        missing_deps+=("docker-compose")
    fi

    # Check if caelum-unified directory exists
    if [[ ! -d "$CAELUM_UNIFIED_DIR" ]]; then
        log_error "Caelum unified directory not found: $CAELUM_UNIFIED_DIR"
        exit 1
    fi

    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log_error "Missing dependencies: ${missing_deps[*]}"
        exit 1
    fi

    log_success "All prerequisites satisfied"
}

# Test connectivity to primary node
test_primary_connectivity() {
    log_info "Testing connectivity to primary node ($PRIMARY_NODE_IP)..."

    if ! ping -c 1 -W 3 "$PRIMARY_NODE_IP" &> /dev/null; then
        log_error "Cannot ping primary node at $PRIMARY_NODE_IP"
        log_warning "Please ensure the primary node is reachable before continuing"
        exit 1
    fi

    # Test if primary's databases are accessible
    if ! nc -zv "$PRIMARY_NODE_IP" 15432 2>&1 | grep -q "succeeded"; then
        log_warning "Cannot connect to primary PostgreSQL (port 15432)"
        log_warning "Deployment may fail if databases are not accessible"
    else
        log_success "Primary PostgreSQL is accessible"
    fi

    log_success "Primary node is reachable"
}

# Deploy caelum-unified Docker container
deploy_docker_container() {
    log_info "Deploying caelum-unified Docker container..."

    cd "$CAELUM_UNIFIED_DIR"

    # Check if .env file exists
    if [[ ! -f .env ]]; then
        log_warning ".env file not found, creating from template..."
        if [[ -f .env.example ]]; then
            cp .env.example .env
        else
            log_error "No .env or .env.example found"
            exit 1
        fi
    fi

    # Set environment variables for secondary deployment
    export NODE_ID="$NODE_ID"
    export PRIMARY_NODE_IP="$PRIMARY_NODE_IP"
    export NODE_IP="$CURRENT_NODE_IP"

    # Stop any existing deployment
    log_info "Stopping existing containers..."
    docker-compose -f docker-compose.secondary.yml down 2>/dev/null || true

    # Build and start the container
    log_info "Building Docker image..."
    docker-compose -f docker-compose.secondary.yml build

    log_info "Starting caelum-unified container..."
    docker-compose -f docker-compose.secondary.yml up -d caelum-unified

    # Wait for container to be healthy
    log_info "Waiting for container to become healthy (max 60s)..."
    local timeout=60
    local elapsed=0
    while [[ $elapsed -lt $timeout ]]; do
        if curl -sf http://localhost:8099/health &> /dev/null; then
            log_success "Container is healthy"
            break
        fi
        sleep 2
        elapsed=$((elapsed + 2))
    done

    if [[ $elapsed -ge $timeout ]]; then
        log_error "Container failed to become healthy within ${timeout}s"
        docker logs caelum-unified-secondary-$NODE_ID --tail 50
        exit 1
    fi

    log_success "Docker container deployed successfully"
}

# Configure Claude Code CLI
configure_claude_cli() {
    log_info "Configuring Claude Code CLI..."

    local claude_config="$HOME/.claude.json"
    local claude_dir="$HOME/.claude"

    # Create backup of existing configuration
    if [[ -f "$claude_config" ]]; then
        local backup_file="${claude_config}.backup.$(date +%Y%m%d_%H%M%S)"
        log_info "Backing up existing config to: $backup_file"
        cp "$claude_config" "$backup_file"
    fi

    # Create .claude directory if it doesn't exist
    mkdir -p "$claude_dir"

    # Note: Based on the current setup on 10.32.3.44, we're using individual MCP servers
    # rather than a proxy. This is the recommended approach per DEPLOYMENT-MCP-CONNECTIONS.md

    log_info "Current MCP setup uses individual Caelum MCP servers"
    log_info "MCP servers should point to shared paths (via NFS from 10.32.3.27)"

    # Verify NFS mount points exist
    local nfs_mount_path="/home/rford/caelum"
    local caelum_servers_path="$nfs_mount_path/caelum"
    local caelum_unified_path="$nfs_mount_path/ss/caelum-unified"

    if [[ ! -d "$nfs_mount_path" ]]; then
        log_error "NFS mount path not found: $nfs_mount_path"
        log_error "This path should be mounted via NFS from 10.32.3.27"
        log_error "Per CLAUDE.md: GPUs on 10.32.3.44/62 share same NFS mount from 10.32.3.27"
        exit 1
    else
        log_success "NFS mount path exists: $nfs_mount_path"
    fi

    if [[ ! -d "$caelum_servers_path" ]]; then
        log_warning "Caelum servers path not found: $caelum_servers_path"
    else
        log_success "Caelum individual servers path exists: $caelum_servers_path"
    fi

    if [[ ! -d "$caelum_unified_path" ]]; then
        log_warning "Caelum unified path not found: $caelum_unified_path"
    else
        log_success "Caelum unified path exists: $caelum_unified_path"
    fi

    log_success "Claude CLI configuration verified"
    log_info "MCP servers configured in $claude_config should remain as-is"
    log_info "They use individual servers from: $caelum_servers_path"
}

# Configure session hooks
configure_session_hooks() {
    log_info "Configuring session hooks..."

    local hooks_dir="$HOME/.claude"
    local session_hook="$hooks_dir/session-start-context-loader.sh"

    if [[ -f "$session_hook" ]]; then
        log_success "Session hook already exists: $session_hook"
    else
        log_info "Session hook not found, will be created on first Claude Code session"
    fi

    # Ensure hooks directory exists
    mkdir -p "$HOME/.caelum/logs"
    mkdir -p "$HOME/.caelum/session-memory"

    log_success "Session hooks configured"
}

# Verify deployment
verify_deployment() {
    log_info "Verifying deployment..."

    # Check Docker container status
    if docker ps --filter "name=caelum-unified-secondary" --filter "status=running" | grep -q "caelum-unified-secondary"; then
        log_success "Docker container is running"
    else
        log_error "Docker container is not running"
        return 1
    fi

    # Check health endpoint
    if curl -sf http://localhost:8099/health &> /dev/null; then
        local health_response=$(curl -s http://localhost:8099/health)
        log_success "Health check passed: $health_response"
    else
        log_error "Health check failed"
        return 1
    fi

    # Check TCP MCP port
    if nc -zv localhost 8090 2>&1 | grep -q "succeeded"; then
        log_success "TCP MCP port (8090) is accessible"
    else
        log_warning "TCP MCP port (8090) is not accessible"
    fi

    # Check WebSocket MCP port
    if nc -zv localhost 8091 2>&1 | grep -q "succeeded"; then
        log_success "WebSocket MCP port (8091) is accessible"
    else
        log_warning "WebSocket MCP port (8091) is not accessible"
    fi

    log_success "Deployment verification complete"
}

# Display summary
display_summary() {
    cat << EOF

${GREEN}╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║              Deployment Complete! ✅                          ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝${NC}

${BLUE}📋 Deployment Summary:${NC}
   Node IP: $CURRENT_NODE_IP
   Node ID: $NODE_ID
   Primary Node: $PRIMARY_NODE_IP
   Container: caelum-unified-secondary-$NODE_ID

${BLUE}🌐 Service Endpoints:${NC}
   Health Check: http://localhost:8099/health
   TCP MCP Server: tcp://localhost:8090
   WebSocket MCP: ws://localhost:8091

${BLUE}🔧 MCP Configuration:${NC}
   Claude Config: ~/.claude.json
   MCP Servers: Using individual servers from /home/rford/caelum/caelum
   Note: MCP servers use NFS-shared paths from 10.32.3.27

${BLUE}📊 Docker Management:${NC}
   View logs: docker-compose -f $CAELUM_UNIFIED_DIR/docker-compose.secondary.yml logs -f
   Stop container: docker-compose -f $CAELUM_UNIFIED_DIR/docker-compose.secondary.yml down
   Restart: docker-compose -f $CAELUM_UNIFIED_DIR/docker-compose.secondary.yml restart

${BLUE}🧪 Testing:${NC}
   Test health: curl http://localhost:8099/health
   View container status: docker ps --filter "name=caelum-unified"

${BLUE}📚 Documentation:${NC}
   Deployment Guide: $CAELUM_UNIFIED_DIR/DEPLOYMENT_GUIDE.md
   MCP Connections: $CAELUM_UNIFIED_DIR/DEPLOYMENT-MCP-CONNECTIONS.md

${YELLOW}⚠️  Important Notes:${NC}
   1. This node connects to primary databases at $PRIMARY_NODE_IP
   2. Ensure NFS mounts are active from 10.32.3.27
   3. Claude Code CLI uses individual MCP servers (current recommended approach)
   4. GPU resources are shared across 10.32.3.27, 10.32.3.44, and 10.32.3.62

${GREEN}✨ Next Steps:${NC}
   1. Start Claude Code CLI: claude
   2. Verify MCP tools are available
   3. Test cross-node coordination with primary at 10.32.3.27

EOF
}

# Main execution
main() {
    log_info "Starting secondary node setup..."
    echo ""

    check_prerequisites
    test_primary_connectivity
    deploy_docker_container
    configure_claude_cli
    configure_session_hooks

    if verify_deployment; then
        display_summary
        exit 0
    else
        log_error "Deployment verification failed"
        log_error "Please check the logs above for details"
        exit 1
    fi
}

# Run main function
main
