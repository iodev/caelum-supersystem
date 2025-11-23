# Actual Setup on 10.32.3.44

## Storage Architecture

This machine (10.32.3.44) has **two separate Caelum locations**:

### 1. NFS Mount from Primary (10.32.3.27)
```
Path: /home/rford/caelum
Mount: 10.32.3.27:/home/rford/caelum (NFS4)
Size: 1007GB (15% used)
Contains:
  - /home/rford/caelum/ss/caelum-unified (unified MCP server repo)
```

### 2. Local Windows D: Drive
```
Path: /mnt/d/swdatasci/caelum
Mount: D:\ (WSL/drvfs)
Size: 1.9TB (40% used)
Contains:
  - 135+ individual MCP server directories
  - All the individual Caelum MCP server implementations
```

## Current Configuration

### Claude Code CLI (~/.claude.json)
- **MCP Servers**: 14 servers configured
- **Path**: All point to `/mnt/d/swdatasci/caelum/*server/build/*.js`
- **Type**: Individual STDIO MCP servers (not unified proxy)

Examples:
- caelum-ollama-pool: `/mnt/d/swdatasci/caelum/ollama-pool-integration-server/build/index.js`
- caelum-project-intelligence: `/mnt/d/swdatasci/caelum/project-intelligence-server/build-enhanced/index-enhanced.js`
- caelum-notifications: `/mnt/d/swdatasci/caelum/cross-device-notification-server/build-enhanced/index-enhanced.js`

### Docker Container
- **Name**: `caelum-unified-secondary-node-10-32-3-44`
- **Status**: Running (healthy)
- **Ports**: 8090 (TCP MCP), 8091 (WS), 8099 (Health)
- **Deployment**: Uses `/home/rford/caelum/ss/caelum-unified`
- **Purpose**: Connects to primary databases, provides unified MCP endpoint

## Key Findings

1. **NFS mount DOES NOT contain individual MCP servers**
   - Only contains the unified `caelum-unified` repository
   - Individual servers are on local Windows D: drive

2. **CLAUDE.md statement clarification**
   > "There is no SETUP time for GPUs on 10.32.3.44 or 10.32.3.62 because they have the same files mounted by NFS"
   
   This refers to:
   - **GPU-related files** and shared resources
   - **The caelum-unified repository**
   - **NOT the individual MCP servers** (those are on local Windows drive)

3. **For 10.32.3.62 setup**, we need to know:
   - Does 10.32.3.62 also have a Windows D: drive with MCP servers?
   - Or will it use the NFS mount for everything?
   - Is there a D: drive available or should we use the NFS-shared version?

## Setup Script Implications

The setup scripts should:

1. **Verify NFS mount**: `/home/rford/caelum` from 10.32.3.27
2. **Check for local MCP servers**: `/mnt/d/swdatasci/caelum` (if on Windows/WSL)
3. **Deploy Docker**: Using NFS-shared caelum-unified
4. **Claude CLI config**: Keep using whatever path has the MCP servers (likely `/mnt/d` on 10.32.3.44)

## Questions for 10.32.3.62

Before deploying to 10.32.3.62, we need to determine:

1. Is 10.32.3.62 running WSL with Windows D: drive access?
2. Or is it a native Linux machine that will use only NFS mounts?
3. Where are/should the individual MCP servers be located on 10.32.3.62?

## Recommended Approach

For a **clean, consistent deployment** across all secondary nodes:

1. **Move individual MCP servers to NFS mount**
   - Clone/copy all MCP servers from `/mnt/d/swdatasci/caelum` to `/home/rford/caelum/caelum`
   - Update `.claude.json` to point to `/home/rford/caelum/caelum/*server`
   - This ensures all nodes use the same shared source

2. **Or keep Windows-specific setup**
   - Only works for nodes running WSL with Windows D: drive
   - Each node needs its own copy of MCP servers on Windows drive
   - Not truly "shared" across nodes

## Current Working State

✅ Everything is working as-is on 10.32.3.44 with:
- Docker: Uses NFS `/home/rford/caelum/ss/caelum-unified`
- MCP Servers: Uses local `/mnt/d/swdatasci/caelum`
- Healthy and operational

---
**Last Updated**: 2025-10-24
**Machine**: 10.32.3.44 (WSL on Windows)
