# Runbook: Node Down

## Alert
NodeDown: Node exporter unreachable for more than 1 minute

## Severity
Critical

## Step 1: Identify which node is down
```bash
bash ~/jobpulse-sre-lab/scripts/cluster_status.sh
```

## Step 2: Try to SSH into the node
```bash
ssh agzo@192.168.1.104  # master
ssh agzo@192.168.1.113  # worker
ssh agzo@192.168.1.114  # monitoring
ssh agzo@192.168.1.115  # cicd
```

## Step 3: If SSH fails, check ESXi console
- Open https://192.168.1.235/ui
- Check if the VM is powered on
- Open the console and check for kernel panics or disk errors

## Step 4: If worker node is down
```bash
# Check what pods were running on the worker
ssh agzo@192.168.1.104 'kubectl get pods -n jobpulse -o wide'

# K3s will reschedule pods automatically after 5 minutes
# Force immediate reschedule
ssh agzo@192.168.1.104 'kubectl delete pod -n jobpulse -l app=jobpulse-api'
```

## Step 5: After node recovers
```bash
# Verify node rejoined the cluster
ssh agzo@192.168.1.104 'kubectl get nodes'

# Run health check
python3 ~/jobpulse-sre-lab/scripts/deployment_health.py
```
