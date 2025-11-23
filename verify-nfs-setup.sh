#!/bin/bash
# Quick verification script for NFS setup on secondary nodes

echo "=== Caelum NFS Setup Verification ==="
echo ""

# Check NFS mount
echo "1. Checking NFS mount point..."
if [[ -d "/home/rford/caelum" ]]; then
    echo "   ✅ /home/rford/caelum exists"
    
    # Check if it's an NFS mount
    if mount | grep -q "/home/rford/caelum"; then
        echo "   ✅ Path is mounted (likely NFS)"
        mount | grep "/home/rford/caelum"
    else
        echo "   ⚠️  Path exists but may not be NFS mounted"
    fi
else
    echo "   ❌ /home/rford/caelum NOT FOUND"
    exit 1
fi

echo ""
echo "2. Checking Caelum directories..."

# Check caelum/caelum (individual servers)
if [[ -d "/home/rford/caelum/caelum" ]]; then
    echo "   ✅ /home/rford/caelum/caelum exists (individual MCP servers)"
    ls -la /home/rford/caelum/caelum | head -5
else
    echo "   ❌ /home/rford/caelum/caelum NOT FOUND"
fi

echo ""
# Check caelum/ss/caelum-unified
if [[ -d "/home/rford/caelum/ss/caelum-unified" ]]; then
    echo "   ✅ /home/rford/caelum/ss/caelum-unified exists (unified server)"
else
    echo "   ❌ /home/rford/caelum/ss/caelum-unified NOT FOUND"
fi

echo ""
echo "3. Checking Docker container..."
if docker ps --filter "name=caelum-unified-secondary" --format "{{.Names}}\t{{.Status}}" | grep -q "caelum-unified-secondary"; then
    echo "   ✅ Caelum unified secondary container is running"
    docker ps --filter "name=caelum-unified-secondary" --format "   {{.Names}}\t{{.Status}}"
else
    echo "   ⚠️  No caelum-unified-secondary container running"
fi

echo ""
echo "4. Checking Claude Code CLI config..."
if [[ -f "$HOME/.claude.json" ]]; then
    echo "   ✅ ~/.claude.json exists"
    
    # Count MCP servers
    mcp_count=$(cat ~/.claude.json | python3 -c "import json, sys; data = json.load(sys.stdin); print(len(data.get('mcpServers', {})))" 2>/dev/null || echo "0")
    echo "   📊 Number of MCP servers configured: $mcp_count"
else
    echo "   ❌ ~/.claude.json NOT FOUND"
fi

echo ""
echo "5. Checking connectivity to primary node (10.32.3.27)..."
if ping -c 1 -W 2 10.32.3.27 &> /dev/null; then
    echo "   ✅ Primary node 10.32.3.27 is reachable"
else
    echo "   ❌ Cannot reach primary node 10.32.3.27"
fi

echo ""
echo "=== Verification Complete ==="
