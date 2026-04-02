# Phase 6: Infrastructure as Code with Terraform and Ansible

## Overview
Codified the entire JobPulse infrastructure using Terraform for orchestration
and Ansible for configuration management. All infrastructure state is
version-controlled, reproducible, and idempotent. Any new node can be brought
to the correct baseline state by running a single Ansible playbook.

## Tools Installed

| Tool | Version | Purpose |
|---|---|---|
| Ansible | 2.x | Configuration management across all nodes |
| Terraform | 1.7.5 | Infrastructure orchestration and state management |

## Ansible Playbooks Created

| Playbook | Hosts | Purpose |
|---|---|---|
| base-setup.yml | all_nodes | Packages, UFW, fail2ban, hostname, hosts file |
| security-hardening.yml | all_nodes | SSH hardening, fail2ban tuning, kernel params |
| open-observability-ports.yml | role-specific | UFW rules per node role |

## Ansible Idempotency Verified
- First run: applied all configuration changes across 4 nodes
- Second run: changed=0 on all nodes confirming idempotency
- Any configuration drift will be corrected on the next playbook run

## Terraform Resources Created

| Resource | Count | Purpose |
|---|---|---|
| null_resource.node_connectivity_check | 4 | SSH reachability check per node |
| null_resource.ansible_base_setup | 1 | Runs base Ansible playbook |
| local_file.cluster_info | 1 | Generates cluster summary output file |
| Total | 6 | All applied successfully |

## Terraform Outputs

| Output | Value |
|---|---|
| api_url | http://192.168.1.104:30500 |
| grafana_url | http://192.168.1.114:3000 |
| prometheus_url | http://192.168.1.114:9090 |
| cluster_nodes | All 4 nodes with hostname, IP, and role |

## Issues Encountered and Resolved

### Broken PPA on WSL
- Root cause: linuxuprising java PPA not compatible with Ubuntu noble
- Resolution: Removed the broken sources.list.d entry

### Terraform not found after HashiCorp repo method
- Root cause: HashiCorp apt repo setup failed on WSL
- Resolution: Direct binary install from releases.hashicorp.com

### Ansible Missing sudo password on 3 nodes
- Root cause: NOPASSWD sudoers entry only on worker node
- Resolution: Applied /etc/sudoers.d/agzo NOPASSWD entry to all nodes

## Key IaC Principles Demonstrated
- All configuration in version control, no manual steps undocumented
- Idempotent operations safe to run multiple times
- Declarative state: describe desired state not procedural steps
- Separation of concerns: Terraform orchestrates, Ansible configures
- Drift detection: re-running playbooks detects and corrects drift
- Infrastructure documented as code, not tribal knowledge

## Files Created

| File | Purpose |
|---|---|
| ansible/inventory.ini | Node inventory with IPs and SSH config |
| ansible/base-setup.yml | Base configuration playbook |
| ansible/security-hardening.yml | Security hardening playbook |
| ansible/open-observability-ports.yml | UFW port configuration |
| terraform/main.tf | Main Terraform configuration |
| terraform/variables.tf | Input variables |
| terraform/outputs.tf | Output values |
| terraform/templates/cluster-info.tpl | Cluster summary template |

## Next Phase
Phase 7: Automation scripts, load testing, and incident simulation
