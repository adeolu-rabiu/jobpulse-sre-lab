# Runbook: High Error Rate

## Alert
HighErrorRate: Error rate exceeds 0.1% for more than 2 minutes

## Severity
Critical

## Impact
Users receiving errors. Platform SLO at risk.

## Detection
- Grafana alert fires
- Alertmanager routes to receiver
- Check: http://192.168.1.114:9090/alerts

## Step 1: Assess (2 minutes)
```bash
# Check error rate in Prometheus
curl -s "http://192.168.1.114:9090/api/v1/query?query=rate(flask_http_request_exceptions_total[5m])"

# Check pod status
ssh agzo@192.168.1.104 'kubectl get pods -n jobpulse'

# Check recent logs
ssh agzo@192.168.1.104 'kubectl logs -n jobpulse -l app=jobpulse-api --tail=50'
```

## Step 2: Correlate
```bash
# Check recent deployments
git log --oneline -10

# Check events in namespace
ssh agzo@192.168.1.104 'kubectl get events -n jobpulse --sort-by=.lastTimestamp | tail -20'
```

## Step 3: Mitigate

If caused by a recent deployment:
```bash
ssh agzo@192.168.1.104 'kubectl rollout undo deployment/jobpulse-api -n jobpulse'
ssh agzo@192.168.1.104 'kubectl rollout status deployment/jobpulse-api -n jobpulse'
```

If caused by database issue:
```bash
ssh agzo@192.168.1.104 'kubectl get pods -n jobpulse -l app=mysql'
ssh agzo@192.168.1.104 'kubectl logs -n jobpulse -l app=mysql --tail=20'
```

## Step 4: Verify
```bash
python3 ~/jobpulse-sre-lab/scripts/deployment_health.py
curl http://192.168.1.104:30500/health
```

## Step 5: Post-Incident
- Document in docs/post-incident-log.md
- Root cause analysis within 24 hours
- Action items with owners and due dates
