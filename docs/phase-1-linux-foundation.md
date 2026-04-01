# Phase 1: Linux Foundation and VM Setup

## Overview
Established the infrastructure baseline for the JobPulse SRE platform across four Ubuntu 24.04 LTS virtual machines running on a VMware ESXi 8.0 host. This phase covers host provisioning, network configuration, security hardening, SSH key authentication, and operational tooling.

## Infrastructure Provisioned

| VM | Role | IP | CPU | RAM |
|---|---|---|---|---|
| jobpulse-k8s-master | K3s Control Plane | 192.168.1.104 | 2 vCPU | 4 GB |
| jobpulse-k8s-worker | K3s Worker Node | 192.168.1.113 | 2 vCPU | 4 GB |
| jobpulse-monitoring | Observability Stack | 192.168.1.114 | 2 vCPU | 4 GB |
| jobpulse-cicd | CI/CD Runner | 192.168.1.115 | 1 vCPU | 2 GB |

## Steps Completed

### 1. VM Provisioning on ESXi
- Created four Ubuntu 24.04 LTS VMs via ESXi 8.0 web console
- Allocated compute and storage resources per architecture specification
- Attached Ubuntu Server ISO and completed unattended installation on each node
- Configured user account: agzo with sudo privileges

### 2. Network Configuration
- Assigned static IP addresses via Netplan on all four nodes
- Configured default gateway: 192.168.1.1
- Set DNS resolvers: 8.8.8.8, 8.8.4.4
- Populated /etc/hosts on all nodes for hostname-based resolution between peers
- Fixed Netplan file permissions: chmod 600 /etc/netplan/00-installer-config.yaml

### 3. Package Baseline
Installed on all four nodes:
- curl, wget — HTTP tooling
- git — version control
- vim — text editor
- net-tools — network diagnostics (ifconfig, netstat)
- htop — interactive process monitor
- tmux — terminal multiplexer for persistent sessions
- ufw — host firewall
- fail2ban — brute-force protection

### 4. Security Hardening
- UFW configured on all nodes: default deny incoming, allow outgoing
- SSH port explicitly allowed before enabling UFW to prevent lockout
- UFW enabled and verified active on all four nodes
- Fail2ban installed and running for SSH brute-force protection

### 5. Hostname Configuration
Each node configured with a descriptive hostname matching its role:
- jobpulse-k8s-master
- jobpulse-k8s-worker
- jobpulse-monitoring
- jobpulse-cicd

### 6. SSH Key Authentication
- Generated ed25519 SSH keypair on the control machine (WSL on Windows)
- Distributed public key to all four nodes via ssh-copy-id
- Verified passwordless SSH access to all nodes
- Password-based authentication remains as fallback for console access

### 7. Git Repository Initialised
- Repository created at github.com/adeolu-rabiu/jobpulse-sre-lab
- SSH key added to GitHub for secure push authentication
- Git global config set: user.name and user.email
- Project directory structure created matching all planned phases
- README.md authored with full architecture documentation

### 8. Operational Automation
- Bash health check script created: scripts/health_check.sh
- Reports CPU load, memory usage, disk utilisation, and uptime for all four nodes
- Executes across the entire cluster in a single command with no manual SSH steps

## Verification Checklist
- [x] SSH passwordless access confirmed on all four nodes
- [x] Hostname resolution working between all nodes (ping by name)
- [x] UFW active and enforcing on all four nodes
- [x] Static IPs confirmed stable after netplan apply
- [x] Git repository initialised and linked to GitHub remote
- [x] health_check.sh returns output for all four nodes without errors

## Commands Reference
```bash
# Verify SSH access
ssh agzo@192.168.1.104 'echo ok'

# Verify hostname resolution from master
ssh agzo@192.168.1.104 'ping -c 2 jobpulse-k8s-worker'

# Check firewall status on all nodes
for IP in 192.168.1.104 192.168.1.113 192.168.1.114 192.168.1.115; do
  echo "=== $IP ==="
  ssh agzo@$IP 'sudo ufw status'
done

# Run cluster health check
bash scripts/health_check.sh
```

## Next Phase
Phase 2: Application and Database Layer
- Python Flask REST API with native Prometheus instrumentation
- MySQL 8.0 database with production schema and indexing
- Docker containerisation of the full application stack
