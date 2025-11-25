# Sudo Access Note

**Date**: 2025-11-15
**Author**: Claude (automated note)

## Sudo Access Available

Claude has sudo access to the following machines:

1. **Primary WSL Machine** (caelum)
   - Current machine: WSL2 on Windows
   - User: `rford`
   - Network: 10.32.3.x subnet
   - Purpose: Main development and orchestration

2. **GPU Server 1**: 10.32.3.44
   - User: `rford`
   - Hardware: NVIDIA GPU
   - NFS Mount: `/home/rford/caelum/ss` from 10.32.3.27
   - Purpose: ML training, inference
   - Note: Instant code access via NFS (no copying needed)

3. **GPU Server 2**: 10.32.3.62
   - User: `rford`
   - Hardware: NVIDIA GPU
   - NFS Mount: `/home/rford/caelum/ss` from 10.32.3.27
   - Purpose: ML training, inference
   - Note: Instant code access via NFS (no copying needed)

## Important Capabilities

### With sudo access, Claude can:
- ✅ Install system packages (apt, pip, npm)
- ✅ Configure systemd services (PM2 auto-start, etc.)
- ✅ Modify system configuration files
- ✅ Manage Docker containers
- ✅ Configure networking and firewall
- ✅ Install and configure databases
- ✅ Set up GPU drivers and CUDA

### Security Note
- Sudo access is granted by user `rford`
- Use responsibly and only when necessary
- Always verify commands before execution
- Document system changes in session notes

## Recent Sudo Operations

### 2025-11-15: PM2 Auto-Start Setup
```bash
sudo env "PATH=$PATH" /home/rford/.nvm/versions/node/v20.19.2/lib/node_modules/pm2/bin/pm2 startup systemd -u rford --hp /home/rford
```
- Created `/etc/systemd/system/pm2-rford.service`
- Enabled PM2 auto-start on system reboot
- Service will resurrect 6 services: pim-server, fincoll-server, senvec-aggregator, senvec-alphavantage, senvec-social, senvec-news

---

**Remember**: Document all sudo operations in session notes for traceability.
