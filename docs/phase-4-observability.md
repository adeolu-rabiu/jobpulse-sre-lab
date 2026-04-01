# Phase 4: Observability Stack

## Overview
Deployed a full three-pillar observability platform on the dedicated
monitoring VM (192.168.1.114). The stack provides metrics collection,
log aggregation, distributed tracing, SLO-based alerting, and unified
dashboards across the entire JobPulse platform.

## Components Deployed

| Component | Version | Port | Purpose |
|---|---|---|---|
| Prometheus | latest | 9090 | Metrics collection and SLO evaluation |
| Grafana | latest | 3000 | Unified dashboards and visualisation |
| Loki | latest | 3100 | Centralised log aggregation |
| Promtail | latest | 9080 | Log shipping agent |
| Alertmanager | latest | 9093 | Alert routing and deduplication |
| Node Exporter | 1.7.0 | 9100 | Host metrics on all 4 nodes |

## Alert Rules Implemented

| Alert | Condition | Severity |
|---|---|---|
| HighErrorRate | Error rate > 0.1% for 2 minutes | critical |
| HighLatency | p99 latency > 500ms for 5 minutes | warning |
| APIDown | API unreachable for 1 minute | critical |
| HighCPU | CPU > 80% for 5 minutes | warning |
| LowDiskSpace | Disk < 15% free for 10 minutes | critical |
| HighMemoryUsage | Memory > 85% for 5 minutes | warning |
| NodeDown | Node exporter unreachable for 1 minute | critical |

## Prometheus Scrape Targets

| Job | Target | Metrics |
|---|---|---|
| jobpulse-api | 192.168.1.104:30500 | Flask HTTP metrics |
| node-exporter | All 4 VMs :9100 | CPU, memory, disk, network |
| prometheus | localhost:9090 | Prometheus self-metrics |

## Grafana Dashboards Imported
- Node Exporter Full (ID: 1860)
- Kubernetes cluster overview (ID: 10856)

## Verification Results
- All 5 observability containers running with 0 restarts
- All Prometheus targets showing health: up
- Loki receiving logs from Promtail
- Grafana dashboards rendering with live data
- Alert rules loaded and evaluated every 15 seconds
- Node metrics flowing from all 4 cluster nodes

## Access URLs

| Service | URL | Credentials |
|---|---|---|
| Grafana | http://192.168.1.114:3000 | admin / JobPulse2024! |
| Prometheus | http://192.168.1.114:9090 | none |
| Alertmanager | http://192.168.1.114:9093 | none |
| Loki | http://192.168.1.114:3100 | none |

## Next Phase
Phase 5: CI/CD pipeline with GitHub Actions self-hosted runner
