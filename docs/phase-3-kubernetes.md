# Phase 3: Kubernetes with K3s

## Overview
Deployed the JobPulse application stack to a two-node Kubernetes cluster
running K3s on VMware ESXi. This phase establishes production-grade container
orchestration with health probes, resource limits, rolling deployments,
and service discovery.

## Cluster Topology

| Node | Role | IP | Version |
|---|---|---|---|
| jobpulse-k8s-master | K3s Server (control plane) | 192.168.1.104 | v1.34.6+k3s1 |
| jobpulse-k8s-worker | K3s Agent (worker) | 192.168.1.113 | v1.34.6+k3s1 |

## Steps Completed

### 1. K3s Server Installation (master node)
- Installed K3s server via official install script
- Configured kubeconfig at ~/.kube/config with correct permissions
- Fixed kubeconfig file permissions: chmod 644 /etc/rancher/k3s/k3s.yaml
- Set KUBECONFIG environment variable in ~/.bashrc

### 2. K3s Agent Installation (worker node)
- Joined worker node using master IP and node token
- Opened required firewall ports on both nodes before agent could connect:
  - TCP 6443: Kubernetes API server
  - TCP 10250: Kubelet API
  - UDP 8472: VXLAN overlay network (Flannel)
- Confirmed both nodes showing Ready status

### 3. Container Image Distribution
- Built jobpulse-api:latest Docker image on master node
- Exported image to tar file and copied to worker node via scp
- Imported image into K3s containerd runtime on both nodes
- Configured passwordless sudo on all nodes for operational efficiency

### 4. Kubernetes Manifests Created

| File | Resource | Purpose |
|---|---|---|
| namespace.yaml | Namespace | Isolated jobpulse namespace |
| secret.yaml | Secret | Database credentials |
| mysql-configmap.yaml | ConfigMap | Database schema for initialisation |
| mysql-deployment.yaml | Deployment + Service | MySQL with readiness probe |
| api-deployment.yaml | Deployment + Service | Flask API with 2 replicas |

### 5. Production Features Implemented
- Liveness probes: automatic pod restart on application failure
- Readiness probes: traffic only routed to healthy pods
- Resource requests and limits: CPU and memory guardrails per container
- Prometheus annotations: automatic metrics scraping by Prometheus
- Rolling deployment strategy: zero-downtime updates
- Kubernetes Secrets: database credentials managed securely
- NodePort service: API exposed on port 30500

## Kubernetes Resources Deployed

| Resource | Name | Namespace | Status |
|---|---|---|---|
| Namespace | jobpulse | cluster | Active |
| Secret | db-credentials | jobpulse | Created |
| ConfigMap | mysql-schema | jobpulse | Created |
| Deployment | mysql | jobpulse | 1/1 Ready |
| Deployment | jobpulse-api | jobpulse | 2/2 Ready |
| Service | mysql-svc (ClusterIP) | jobpulse | Active |
| Service | jobpulse-api-svc (NodePort 30500) | jobpulse | Active |

## Issues Encountered and Resolved

### ErrImageNeverPull on worker node
- Root cause: Docker image was imported into master K3s runtime only
- Resolution: Exported image as tar, copied to worker via scp, imported into worker K3s containerd runtime
- Prevention: For future phases, build images on both nodes or use a local registry

### Worker node not joining cluster
- Root cause: UFW firewall blocking K3s communication ports
- Resolution: Opened ports 6443/tcp, 10250/tcp, 8472/udp on both nodes
- Worker node appeared in kubectl get nodes immediately after ports were opened

### sudo password required for remote commands
- Root cause: Default Ubuntu sudo requires terminal for password entry
- Resolution: Configured NOPASSWD sudoers entry on all nodes

## Verification Results
- Both nodes showing Ready status: kubectl get nodes
- 2/2 API pods running with 0 restarts
- 1/1 MySQL pod running with readiness probe passing
- NodePort service accessible on port 30500
- /health endpoint returning database connected status
- Rolling restart completed successfully via kubectl rollout restart

## Useful Commands Reference
```bash
# Check cluster status
kubectl get nodes
kubectl get pods -n jobpulse
kubectl get services -n jobpulse
kubectl get deployments -n jobpulse

# Check pod logs
kubectl logs -n jobpulse -l app=jobpulse-api --tail=20

# Describe pod for events and probe status
kubectl describe pods -n jobpulse -l app=jobpulse-api

# Rolling restart
kubectl rollout restart deployment/jobpulse-api -n jobpulse
kubectl rollout status deployment/jobpulse-api -n jobpulse

# Scale deployment
kubectl scale deployment jobpulse-api -n jobpulse --replicas=3

# Test API through NodePort
curl http://192.168.1.104:30500/health
curl http://192.168.1.104:30500/jobs
curl http://192.168.1.104:30500/stats
```

## Next Phase
Phase 4: Observability stack on jobpulse-monitoring (192.168.1.114)
- Prometheus for metrics collection and SLO alerting
- Grafana for dashboards and visualisation
- Loki and Promtail for centralised log aggregation
- Alertmanager for alert routing and notification
- Node Exporter on all four nodes for infrastructure metrics
