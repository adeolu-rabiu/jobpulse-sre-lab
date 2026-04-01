# Phase 2: Application and Database Layer

## Overview
Built and containerised the JobPulse API service and MySQL database. The application is a Python Flask REST API with native Prometheus instrumentation, backed by MySQL 8.0 with a production schema including indexes and foreign key constraints.

## Components Delivered

| Component | Technology | Version |
|---|---|---|
| REST API | Python Flask | 3.0.0 |
| Metrics instrumentation | prometheus-flask-exporter | 0.23.0 |
| Distributed tracing | OpenTelemetry SDK | 1.22.0 |
| Database | MySQL | 8.0 |
| Container runtime | Docker | 29.3.1 |
| Stack orchestration | Docker Compose | v3.8 |

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | /health | Service health including database connectivity |
| GET | /jobs | List all jobs (latest 100) |
| POST | /jobs | Create a new job listing |
| GET | /jobs/:id | Get a specific job by ID |
| POST | /jobs/:id/apply | Submit a job application |
| GET | /stats | Platform-wide job and application counts |
| GET | /metrics | Prometheus metrics exposition |

## Database Schema
- jobs table: id, title, company, location, salary_min, salary_max, description, created_at
- applications table: id, job_id (FK), candidate_email, applied_at
- Indexes on company, location, and job_id for query performance

## Verification Results
- All 7 API endpoints returning correct HTTP status codes
- Prometheus /metrics endpoint exposing flask_http_request metrics
- Docker Compose stack running with healthy database connectivity
- MySQL data persisting across container restarts via named volume
- API accessible from outside the VM on port 5000

## Next Phase
Phase 3: Kubernetes deployment on K3s cluster
