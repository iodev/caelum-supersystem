# Secondary Node Setup for Caelum-Unified

This directory contains scripts to configure secondary nodes (10.32.3.44, 10.32.3.62) with the caelum-unified Docker deployment and Claude Code CLI MCP integration.

## Overview

The current Caelum architecture consists of:

- **Primary Node (10.32.3.27)**: Runs all databases (PostgreSQL, MongoDB, Redis, InfluxDB) and the main caelum-unified instance
- **Secondary Nodes (10.32.3.44, 10.32.3.62)**: Run lightweight caelum-unified instances that connect to the primary node's databases, with shared NFS mounts for GPU resources

## Current Configuration on 10.32.3.44

### Docker Setup
- **Container**: `caelum-unified-secondary-node-10-32-3-44`
- **Status**: Running and healthy
- **Ports**:
  - 8090: TCP MCP Server
  - 8091: WebSocket MCP Server
  - 8099: Health Check Endpoint
- **Environment**: Connects to primary at 10.32.3.27 for databases

### Claude Code CLI Setup
- **Configuration File**: `~/.claude.json`
- **MCP Servers**: Uses individual Caelum MCP servers from `/home/rford/caelum/caelum`
- **Note**: The unified MCP proxy approach is not yet implemented (requires STDIO mode per DEPLOYMENT-MCP-CONNECTIONS.md)

### Key Files
- `~/.claude.json` - Main Claude configuration
- `~/.claude/settings.json` - Hooks and session settings
- `~/.claude/session-start-context-loader.sh` - Session initialization hook

## Setup Scripts

Two versions of the setup script are provided:

### 1. Bash Script: `secondary_node_claude-unified_mcp.sh`

```bash
# Run on the target secondary node
cd ~/caelum/ss
./secondary_node_claude-unified_mcp.sh [NODE_IP]

# Example for 10.32.3.62
./secondary_node_claude-unified_mcp.sh 10.32.3.62
```

### 2. Python Script: `secondary_node_claude-unified_mcp.py`

```bash
# Run on the target secondary node
cd ~/caelum/ss
./secondary_node_claude-unified_mcp.py [NODE_IP]

# Example for 10.32.3.62
./secondary_node_claude-unified_mcp.py 10.32.3.62
```

Both scripts perform the same operations:

1. ✅ Check prerequisites (Docker, docker-compose, repository access)
2. ✅ Test connectivity to primary node (10.32.3.27)
3. ✅ Deploy caelum-unified Docker container using `docker-compose.secondary.yml`
4. ✅ Verify Claude Code CLI configuration
5. ✅ Configure session hooks
6. ✅ Verify deployment health

## Prerequisites

Before running the setup script, ensure:

1. **Docker is installed and running**
   ```bash
   docker info
   ```

2. **docker-compose is available**
   ```bash
   docker-compose --version
   ```

3. **Repository is cloned**
   ```bash
   ls ~/caelum/ss/caelum-unified
   ```

4. **Primary node is accessible**
   ```bash
   ping -c 1 10.32.3.27
   ```

5. **NFS mounts are active** (per CLAUDE.md)
   ```bash
   ls /home/rford/caelum/caelum
   ```

## Important Notes

### NFS Shared Paths

According to `CLAUDE.md`:
> There is no SETUP time for GPUs on 10.32.3.44 or 10.32.3.62 because they have the same files mounted by NFS share from same path on 10.32.3.27

This means:
- The MCP server files at `/home/rford/caelum/caelum` should be the same across all nodes
- No need to rebuild or redeploy individual MCP servers on secondary nodes
- Configuration changes on 10.32.3.27 automatically propagate

### MCP Server Configuration

The current approach (per `DEPLOYMENT-MCP-CONNECTIONS.md`) uses:
- **Individual MCP Servers**: Each Caelum service runs as a separate STDIO MCP server
- **Not Using Unified Proxy**: The unified proxy approach via TCP requires STDIO mode implementation
- **Recommended Approach**: Continue using individual servers until STDIO mode is added

### Database Connections

Secondary nodes connect to primary databases at:
- PostgreSQL: `10.32.3.27:15432`
- MongoDB: `10.32.3.27:27017`
- Redis: `10.32.3.27:6379`
- InfluxDB: `10.32.3.27:8086`

## Troubleshooting

### Container Won't Start

```bash
# Check Docker status
docker ps -a --filter "name=caelum-unified"

# View logs
cd ~/caelum/ss/caelum-unified
docker-compose -f docker-compose.secondary.yml logs -f

# Restart container
docker-compose -f docker-compose.secondary.yml restart
```

### Health Check Fails

```bash
# Test health endpoint
curl http://10.32.3.27:8099/health

# Check container status
docker exec caelum-unified-secondary-[NODE_ID] env | grep -E "PRIMARY|PORT"
```

### MCP Servers Not Available in Claude

```bash
# Verify NFS mount
ls -la /home/rford/caelum/caelum

# Check Claude config
cat ~/.claude.json | python3 -m json.tool | grep -A 10 "mcpServers"

# Test individual MCP server
node /home/rford/caelum/caelum/ollama-pool-integration-server/build/index.js
```

### Primary Node Unreachable

```bash
# Test connectivity
ping -c 3 10.32.3.27

# Test database ports
nc -zv 10.32.3.27 15432  # PostgreSQL
nc -zv 10.32.3.27 6379   # Redis
nc -zv 10.32.3.27 27017  # MongoDB
```

## Manual Reinitialization

If you need to completely reinitialize a secondary node:

```bash
# 1. Stop and remove existing container
cd ~/caelum/ss/caelum-unified
docker-compose -f docker-compose.secondary.yml down

# 2. Remove volumes (optional - will lose local data)
docker volume ls | grep "caelum.*secondary" | awk '{print $2}' | xargs docker volume rm

# 3. Pull latest changes
git pull origin docker-db-sync  # or current branch

# 4. Run setup script
cd ~/caelum/ss
./secondary_node_claude-unified_mcp.sh

# 5. Verify deployment
docker ps --filter "name=caelum-unified"
curl http://10.32.3.27:8099/health
```

## Verification Checklist

After running the setup script, verify:

- [ ] Docker container is running: `docker ps --filter "name=caelum-unified-secondary"`
- [ ] Health endpoint responds: `curl http://10.32.3.27:8099/health`
- [ ] TCP MCP port accessible: `nc -zv 10.32.3.27 8090`
- [ ] WebSocket port accessible: `nc -zv 10.32.3.27 8091`
- [ ] Primary node reachable: `ping -c 1 10.32.3.27`
- [ ] NFS mount active: `ls /home/rford/caelum/caelum`
- [ ] Claude config valid: `cat ~/.claude.json | python3 -m json.tool > /dev/null`
- [ ] Session hooks present: `ls ~/.claude/session-start-context-loader.sh`

## Next Steps After Setup

1. **Start Claude Code CLI**
   ```bash
   claude
   ```

2. **Verify MCP Tools**
   ```bash
   # In Claude Code CLI
   /mcp
   ```

3. **Test Cross-Node Coordination**
   ```bash
   # Test that tools can access shared data on primary
   # Use any caelum MCP tool that requires database access
   ```

## Architecture Diagram

```
┌─────────────────────────────────┐
│  PRIMARY NODE (10.32.3.27)      │
│  ┌──────────────────────────┐   │
│  │ caelum-unified (main)    │   │
│  │ Port: 8090 (TCP)         │   │
│  └────────┬─────────────────┘   │
│           │                     │
│  ┌────────▼─────────────────┐   │
│  │ PostgreSQL  :15432       │   │
│  │ MongoDB     :27017       │   │
│  │ Redis       :6379        │   │
│  │ InfluxDB    :8086        │   │
│  └──────────────────────────┘   │
│           │                     │
│  ┌────────▼─────────────────┐   │
│  │ NFS Share                │   │
│  │ /home/rford/caelum/caelum  │   │
│  └──────────────────────────┘   │
└────────┬────────────────────────┘
         │ Network + NFS
         ├─────────────────┬─────────────────┐
         │                 │                 │
┌────────▼────────┐ ┌──────▼─────────┐ ┌───▼────────────┐
│ 10.32.3.44      │ │ 10.32.3.62     │ │ Other Nodes    │
│ ┌─────────────┐ │ │ ┌────────────┐ │ │                │
│ │caelum-      │ │ │ │caelum-     │ │ │                │
│ │unified-     │ │ │ │unified-    │ │ │                │
│ │secondary    │ │ │ │secondary   │ │ │                │
│ └─────────────┘ │ │ └────────────┘ │ │                │
│                 │ │                │ │                │
│ Claude CLI      │ │ Claude CLI     │ │                │
│ (Individual     │ │ (Individual    │ │                │
│  MCP Servers)   │ │  MCP Servers)  │ │                │
└─────────────────┘ └────────────────┘ └────────────────┘
```

## References

- [Deployment Guide](./caelum-unified/DEPLOYMENT_GUIDE.md)
- [MCP Connection Methods](./caelum-unified/DEPLOYMENT-MCP-CONNECTIONS.md)
- [Secondary Deployment Compose](./caelum-unified/docker-compose.secondary.yml)
- [Project CLAUDE.md](./CLAUDE.md)

---

**Last Updated**: 2025-10-24
**Tested On**: 10.32.3.44
**Target Nodes**: 10.32.3.44, 10.32.3.62
