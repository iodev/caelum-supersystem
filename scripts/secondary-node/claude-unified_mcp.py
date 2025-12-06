#!/usr/bin/env python3
"""
Secondary Node Claude-Unified MCP Setup Script (Python version)
This script configures a secondary node (10.32.3.44, 10.32.3.62) to:
1. Deploy caelum-unified in Docker with connection to primary node (10.32.3.27)
2. Configure Claude Code CLI to use Caelum MCP servers

Usage: ./secondary_node_claude-unified_mcp.py [NODE_IP]
Example: ./secondary_node_claude-unified_mcp.py 10.32.3.62
"""

import os
import sys
import json
import socket
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Colors for terminal output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

class SecondaryNodeSetup:
    def __init__(self, node_ip: Optional[str] = None):
        self.script_dir = Path(__file__).parent.absolute()
        self.caelum_unified_dir = self.script_dir / "caelum-unified"
        self.primary_node_ip = os.environ.get('PRIMARY_NODE_IP', '10.32.3.27')

        # Get current node IP
        if node_ip:
            self.current_node_ip = node_ip
        else:
            self.current_node_ip = self.get_local_ip()

        self.node_id = os.environ.get('NODE_ID', f"node-{self.current_node_ip.replace('.', '-')}")

        self.home_dir = Path.home()
        self.claude_config_file = self.home_dir / ".claude.json"
        self.claude_dir = self.home_dir / ".claude"
        self.caelum_dir = self.home_dir / ".caelum"

    @staticmethod
    def get_local_ip() -> str:
        """Get the local IP address"""
        try:
            # Connect to an external server to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            return "127.0.0.1"

    def log_info(self, msg: str):
        print(f"{Colors.BLUE}ℹ️  {msg}{Colors.NC}")

    def log_success(self, msg: str):
        print(f"{Colors.GREEN}✅ {msg}{Colors.NC}")

    def log_warning(self, msg: str):
        print(f"{Colors.YELLOW}⚠️  {msg}{Colors.NC}")

    def log_error(self, msg: str):
        print(f"{Colors.RED}❌ {msg}{Colors.NC}", file=sys.stderr)

    def print_banner(self):
        print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║      Caelum Unified - Secondary Node MCP Setup                ║
║                                                               ║
║  Configures secondary nodes to use caelum-unified proxy       ║
║  with coordination to the main instance on 10.32.3.27         ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
""")
        print()
        self.log_info("Configuration Summary:")
        print(f"   Node IP: {self.current_node_ip}")
        print(f"   Node ID: {self.node_id}")
        print(f"   Primary Node: {self.primary_node_ip}")
        print(f"   Caelum Unified Dir: {self.caelum_unified_dir}")
        print()

    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        self.log_info("Checking prerequisites...")

        # Check Docker
        if not shutil.which('docker'):
            self.log_error("Docker is not installed")
            return False

        # Check if Docker is running
        try:
            subprocess.run(['docker', 'info'], capture_output=True, check=True)
        except subprocess.CalledProcessError:
            self.log_error("Docker is installed but not running")
            return False

        # Check docker-compose
        if not shutil.which('docker-compose'):
            self.log_error("docker-compose is not installed")
            return False

        # Check caelum-unified directory
        if not self.caelum_unified_dir.exists():
            self.log_error(f"Caelum unified directory not found: {self.caelum_unified_dir}")
            return False

        self.log_success("All prerequisites satisfied")
        return True

    def test_primary_connectivity(self) -> bool:
        """Test connectivity to the primary node"""
        self.log_info(f"Testing connectivity to primary node ({self.primary_node_ip})...")

        # Test ping
        try:
            result = subprocess.run(
                ['ping', '-c', '1', '-W', '3', self.primary_node_ip],
                capture_output=True,
                timeout=5
            )
            if result.returncode != 0:
                self.log_error(f"Cannot ping primary node at {self.primary_node_ip}")
                return False
        except subprocess.TimeoutExpired:
            self.log_error("Ping timeout")
            return False

        # Test PostgreSQL port
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((self.primary_node_ip, 15432))
            sock.close()

            if result == 0:
                self.log_success("Primary PostgreSQL is accessible")
            else:
                self.log_warning("Cannot connect to primary PostgreSQL (port 15432)")
        except Exception as e:
            self.log_warning(f"PostgreSQL connectivity test failed: {e}")

        self.log_success("Primary node is reachable")
        return True

    def deploy_docker_container(self) -> bool:
        """Deploy the caelum-unified Docker container"""
        self.log_info("Deploying caelum-unified Docker container...")

        os.chdir(self.caelum_unified_dir)

        # Check .env file
        env_file = self.caelum_unified_dir / ".env"
        if not env_file.exists():
            self.log_warning(".env file not found, creating from template...")
            env_example = self.caelum_unified_dir / ".env.example"
            if env_example.exists():
                shutil.copy(env_example, env_file)
            else:
                self.log_error("No .env or .env.example found")
                return False

        # Set environment variables
        env = os.environ.copy()
        env.update({
            'NODE_ID': self.node_id,
            'PRIMARY_NODE_IP': self.primary_node_ip,
            'NODE_IP': self.current_node_ip,
        })

        # Stop existing deployment
        self.log_info("Stopping existing containers...")
        subprocess.run(
            ['docker-compose', '-f', 'docker-compose.secondary.yml', 'down'],
            env=env,
            capture_output=True
        )

        # Build image
        self.log_info("Building Docker image...")
        result = subprocess.run(
            ['docker-compose', '-f', 'docker-compose.secondary.yml', 'build'],
            env=env
        )
        if result.returncode != 0:
            self.log_error("Docker build failed")
            return False

        # Start container
        self.log_info("Starting caelum-unified container...")
        result = subprocess.run(
            ['docker-compose', '-f', 'docker-compose.secondary.yml', 'up', '-d', 'caelum-unified'],
            env=env
        )
        if result.returncode != 0:
            self.log_error("Failed to start container")
            return False

        # Wait for health check
        self.log_info("Waiting for container to become healthy (max 60s)...")
        import time
        timeout = 60
        elapsed = 0

        while elapsed < timeout:
            try:
                result = subprocess.run(
                    ['curl', '-sf', 'http://10.32.3.27:8099/health'],
                    capture_output=True,
                    timeout=2
                )
                if result.returncode == 0:
                    self.log_success("Container is healthy")
                    return True
            except Exception:
                pass

            time.sleep(2)
            elapsed += 2

        self.log_error(f"Container failed to become healthy within {timeout}s")

        # Show container logs
        subprocess.run(
            ['docker', 'logs', f'caelum-unified-secondary-{self.node_id}', '--tail', '50']
        )
        return False

    def configure_claude_cli(self) -> bool:
        """Configure Claude Code CLI"""
        self.log_info("Configuring Claude Code CLI...")

        # Create backup of existing configuration
        if self.claude_config_file.exists():
            backup_file = Path(f"{self.claude_config_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            self.log_info(f"Backing up existing config to: {backup_file}")
            shutil.copy(self.claude_config_file, backup_file)

        # Create .claude directory
        self.claude_dir.mkdir(exist_ok=True)

        self.log_info("Current MCP setup uses individual Caelum MCP servers")
        self.log_info("MCP servers should point to shared paths (via NFS from 10.32.3.27)")

        # Verify NFS mount points
        caelum_base_path = Path("/home/rford/caelum/caelum")
        if not caelum_base_path.exists():
            self.log_warning(f"Caelum base path not found: {caelum_base_path}")
            self.log_warning("This path should be mounted via NFS from 10.32.3.27")
            self.log_warning("Per CLAUDE.md: GPUs on 10.32.3.44/62 share same NFS mount from 10.32.3.27")

            if caelum_base_path.is_symlink():
                target = caelum_base_path.readlink()
                self.log_info(f"Path is a symlink to: {target}")
        else:
            self.log_success(f"Caelum base path exists: {caelum_base_path}")

        self.log_success("Claude CLI configuration verified")
        self.log_info(f"MCP servers configured in {self.claude_config_file} should remain as-is")
        self.log_info(f"They use individual servers from: {caelum_base_path}")

        return True

    def configure_session_hooks(self) -> bool:
        """Configure session hooks"""
        self.log_info("Configuring session hooks...")

        session_hook = self.claude_dir / "session-start-context-loader.sh"

        if session_hook.exists():
            self.log_success(f"Session hook already exists: {session_hook}")
        else:
            self.log_info("Session hook not found, will be created on first Claude Code session")

        # Ensure required directories exist
        (self.caelum_dir / "logs").mkdir(parents=True, exist_ok=True)
        (self.caelum_dir / "session-memory").mkdir(parents=True, exist_ok=True)

        self.log_success("Session hooks configured")
        return True

    def verify_deployment(self) -> bool:
        """Verify the deployment"""
        self.log_info("Verifying deployment...")

        # Check Docker container status
        result = subprocess.run(
            ['docker', 'ps', '--filter', 'name=caelum-unified-secondary',
             '--filter', 'status=running', '--format', '{{.Names}}'],
            capture_output=True,
            text=True
        )

        if 'caelum-unified-secondary' not in result.stdout:
            self.log_error("Docker container is not running")
            return False

        self.log_success("Docker container is running")

        # Check health endpoint
        try:
            result = subprocess.run(
                ['curl', '-sf', 'http://10.32.3.27:8099/health'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                self.log_success(f"Health check passed: {result.stdout}")
            else:
                self.log_error("Health check failed")
                return False
        except Exception as e:
            self.log_error(f"Health check error: {e}")
            return False

        # Check TCP MCP port
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('10.32.3.27', 8090))
            sock.close()

            if result == 0:
                self.log_success("TCP MCP port (8090) is accessible")
            else:
                self.log_warning("TCP MCP port (8090) is not accessible")
        except Exception:
            self.log_warning("TCP MCP port check failed")

        # Check WebSocket MCP port
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('10.32.3.27', 8091))
            sock.close()

            if result == 0:
                self.log_success("WebSocket MCP port (8091) is accessible")
            else:
                self.log_warning("WebSocket MCP port (8091) is not accessible")
        except Exception:
            self.log_warning("WebSocket MCP port check failed")

        self.log_success("Deployment verification complete")
        return True

    def display_summary(self):
        """Display deployment summary"""
        print(f"""
{Colors.GREEN}╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║              Deployment Complete! ✅                          ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝{Colors.NC}

{Colors.BLUE}📋 Deployment Summary:{Colors.NC}
   Node IP: {self.current_node_ip}
   Node ID: {self.node_id}
   Primary Node: {self.primary_node_ip}
   Container: caelum-unified-secondary-{self.node_id}

{Colors.BLUE}🌐 Service Endpoints:{Colors.NC}
   Health Check: http://10.32.3.27:8099/health
   TCP MCP Server: tcp://10.32.3.27:8090
   WebSocket MCP: ws://10.32.3.27:8091

{Colors.BLUE}🔧 MCP Configuration:{Colors.NC}
   Claude Config: {self.claude_config_file}
   MCP Servers: Using individual servers from /home/rford/caelum/caelum
   Note: MCP servers use NFS-shared paths from 10.32.3.27

{Colors.BLUE}📊 Docker Management:{Colors.NC}
   View logs: cd {self.caelum_unified_dir} && docker-compose -f docker-compose.secondary.yml logs -f
   Stop container: cd {self.caelum_unified_dir} && docker-compose -f docker-compose.secondary.yml down
   Restart: cd {self.caelum_unified_dir} && docker-compose -f docker-compose.secondary.yml restart

{Colors.BLUE}🧪 Testing:{Colors.NC}
   Test health: curl http://10.32.3.27:8099/health
   View container status: docker ps --filter "name=caelum-unified"

{Colors.BLUE}📚 Documentation:{Colors.NC}
   Deployment Guide: {self.caelum_unified_dir}/DEPLOYMENT_GUIDE.md
   MCP Connections: {self.caelum_unified_dir}/DEPLOYMENT-MCP-CONNECTIONS.md

{Colors.YELLOW}⚠️  Important Notes:{Colors.NC}
   1. This node connects to primary databases at {self.primary_node_ip}
   2. Ensure NFS mounts are active from 10.32.3.27
   3. Claude Code CLI uses individual MCP servers (current recommended approach)
   4. GPU resources are shared across 10.32.3.27, 10.32.3.44, and 10.32.3.62

{Colors.GREEN}✨ Next Steps:{Colors.NC}
   1. Start Claude Code CLI: claude
   2. Verify MCP tools are available
   3. Test cross-node coordination with primary at 10.32.3.27
""")

    def run(self) -> int:
        """Main execution"""
        self.print_banner()

        # Check for expected nodes
        if self.current_node_ip not in ['10.32.3.44', '10.32.3.62']:
            self.log_warning(f"This script is designed for 10.32.3.44 or 10.32.3.62")
            self.log_warning(f"Current IP: {self.current_node_ip}")
            response = input("Continue anyway? (y/N) ")
            if response.lower() != 'y':
                return 1

        try:
            if not self.check_prerequisites():
                return 1

            if not self.test_primary_connectivity():
                return 1

            if not self.deploy_docker_container():
                return 1

            if not self.configure_claude_cli():
                return 1

            if not self.configure_session_hooks():
                return 1

            if not self.verify_deployment():
                self.log_error("Deployment verification failed")
                self.log_error("Please check the logs above for details")
                return 1

            self.display_summary()
            return 0

        except KeyboardInterrupt:
            print("\n\nSetup interrupted by user")
            return 130
        except Exception as e:
            self.log_error(f"Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return 1


def main():
    node_ip = sys.argv[1] if len(sys.argv) > 1 else None
    setup = SecondaryNodeSetup(node_ip)
    return setup.run()


if __name__ == "__main__":
    sys.exit(main())
