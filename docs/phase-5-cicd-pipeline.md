# Phase 5: CI/CD Pipeline with GitHub Actions

## Overview
Implemented a fully automated three-stage CI/CD pipeline using GitHub Actions
with a self-hosted runner on the dedicated cicd VM (192.168.1.115). Every push
to main triggers automated testing, Docker image build, Kubernetes deployment,
and smoke testing with automatic rollback on failure.

## Runner Configuration

| Property | Value |
|---|---|
| VM | jobpulse-cicd (192.168.1.115) |
| Runner name | jobpulse-cicd |
| Runner type | Self-hosted Linux x64 |
| Runner version | 2.333.1 |
| Service | Installed as systemd service |
| Status | Listening for Jobs |

## Steps Completed

### 1. CI/CD VM Preparation
- Installed Docker on jobpulse-cicd VM
- Installed kubectl and configured kubeconfig
- Fixed kubeconfig server address from 127.0.0.1 to 192.168.1.104
- Verified kubectl get nodes returns both cluster nodes from cicd VM
- Opened UFW port 9100 for Node Exporter

### 2. GitHub Actions Runner Registration
- Downloaded runner package from GitHub releases
- Ran config.sh with repository URL and registration token
- Named runner: jobpulse-cicd
- Installed runner as systemd service via svc.sh
- Confirmed runner showing Listening for Jobs in service logs
- Verified runner showing Idle status on GitHub

### 3. SSH Key Configuration
- Generated ed25519 SSH keypair on cicd VM
- Distributed public key to master (192.168.1.104) via ssh-copy-id
- Distributed public key to worker (192.168.1.113) via ssh-copy-id
- Verified passwordless SSH from cicd to both cluster nodes

### 4. Unit Test Suite
- Created pytest test suite with 5 tests
- Tests use mock patching to run without a real database connection
- Tests cover: health endpoint, missing field validation, service name
- All 5 tests passing locally before pipeline integration

### 5. Pipeline Design
Three-stage sequential pipeline in .github/workflows/deploy.yml:

Stage 1 - test:
- Triggers on every push and pull request to main
- Creates Python venv, installs dependencies
- Runs pytest with verbose output
- Pipeline stops here on any test failure

Stage 2 - build:
- Only runs on push to main (not on PRs)
- Requires test stage to pass
- Builds Docker image tagged with commit SHA and latest
- Saves image as tar and imports into K3s on both master and worker
- Ensures both cluster nodes have the image before deployment

Stage 3 - deploy:
- Only runs on push to main
- Requires build stage to pass
- Applies all Kubernetes manifests via kubectl apply
- Triggers rolling restart of API deployment
- Waits for rollout status confirmation
- Runs HTTP smoke test against /health endpoint
- Automatically runs kubectl rollout undo on smoke test failure

## Pipeline Safety Features

| Feature | Behaviour |
|---|---|
| Test gate | No deployment if tests fail |
| Build gate | No deployment if image build fails |
| Rollout wait | Pipeline waits for Kubernetes to confirm rollout |
| Smoke test | HTTP 200 required before pipeline passes |
| Auto rollback | kubectl rollout undo on smoke test failure |
| PR protection | PRs only run tests, never build or deploy |

## Files Created

| File | Purpose |
|---|---|
| .github/workflows/deploy.yml | Pipeline definition |
| app/tests/test_app.py | Unit test suite with mock patching |

## Verification Results
- Runner service active and listening for jobs
- Runner showing Idle on GitHub repository settings
- Pipeline triggered on push to main
- All three stages passing in GitHub Actions UI
- Pods restarted by pipeline confirmed in kubectl get pods
- Smoke test returning HTTP 200 post-deployment
- Rollback tested by deliberate failure commit

## Useful Commands
```bash
# Check runner service status on cicd VM
ssh agzo@192.168.1.115 'sudo systemctl status actions.runner.*'

# View runner logs
ssh agzo@192.168.1.115 'sudo journalctl -u actions.runner.* -n 20 --no-pager'

# Check pipeline triggered a new deployment
kubectl get pods -n jobpulse

# Manually trigger rollback
kubectl rollout undo deployment/jobpulse-api -n jobpulse

# Check rollout history
kubectl rollout history deployment/jobpulse-api -n jobpulse
```

## Next Phase
Phase 6: Infrastructure as Code with Terraform and Ansible
- Ansible playbook for base node configuration
- Idempotency verification across all nodes
- Configuration drift detection
- Terraform provider setup for vSphere/ESXi
