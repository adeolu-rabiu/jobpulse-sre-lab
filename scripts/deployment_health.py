#!/usr/bin/env python3
"""
JobPulse Deployment Health Checker
Validates all platform components after every deployment
"""

import requests
import sys
import time
import json
from datetime import datetime

BASE_URL = "http://192.168.1.104:30500"
PROMETHEUS = "http://192.168.1.114:9090"
GRAFANA = "http://192.168.1.114:3000"

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"

passed = 0
failed = 0
results = []


def check(name, fn):
    global passed, failed
    try:
        fn()
        print(f"  {GREEN}PASS{RESET} {name}")
        passed += 1
        results.append({"check": name, "status": "PASS"})
    except Exception as e:
        print(f"  {RED}FAIL{RESET} {name}: {e}")
        failed += 1
        results.append({"check": name, "status": "FAIL", "error": str(e)})


def check_api_health():
    r = requests.get(f"{BASE_URL}/health", timeout=5)
    assert r.status_code == 200, f"Expected 200 got {r.status_code}"
    data = r.json()
    assert data["status"] == "ok", f"Status is {data['status']}"
    assert data["database"] == "connected", "Database not connected"


def check_jobs_endpoint():
    r = requests.get(f"{BASE_URL}/jobs", timeout=5)
    assert r.status_code == 200, f"Expected 200 got {r.status_code}"
    jobs = r.json()
    assert isinstance(jobs, list), "Expected list of jobs"
    assert len(jobs) > 0, "No jobs returned"


def check_stats_endpoint():
    r = requests.get(f"{BASE_URL}/stats", timeout=5)
    assert r.status_code == 200, f"Expected 200 got {r.status_code}"
    data = r.json()
    assert "total_jobs" in data, "Missing total_jobs"
    assert "total_applications" in data, "Missing total_applications"


def check_metrics_endpoint():
    r = requests.get(f"{BASE_URL}/metrics", timeout=5)
    assert r.status_code == 200, f"Expected 200 got {r.status_code}"
    assert "flask_http_request_total" in r.text, "Flask metrics not found"


def check_prometheus_health():
    r = requests.get(f"{PROMETHEUS}/-/healthy", timeout=5)
    assert r.status_code == 200, f"Prometheus unhealthy: {r.status_code}"


def check_prometheus_targets():
    r = requests.get(f"{PROMETHEUS}/api/v1/targets", timeout=5)
    assert r.status_code == 200
    data = r.json()
    active = data["data"]["activeTargets"]
    down = [t for t in active if t["health"] != "up"]
    assert len(down) == 0, f"{len(down)} targets are down: {[t['labels'] for t in down]}"


def check_api_response_time():
    start = time.time()
    r = requests.get(f"{BASE_URL}/health", timeout=5)
    elapsed = (time.time() - start) * 1000
    assert elapsed < 500, f"Response time {elapsed:.0f}ms exceeds 500ms SLO"


def check_create_job():
    r = requests.post(
        f"{BASE_URL}/jobs",
        json={
            "title": "Health Check Job",
            "company": "JobPulse Monitor",
            "location": "Cloud",
            "salary_min": 50000,
            "salary_max": 60000
        },
        timeout=5
    )
    assert r.status_code == 201, f"Expected 201 got {r.status_code}"
    data = r.json()
    assert "id" in data, "No ID in response"


def check_grafana_health():
    r = requests.get(f"{GRAFANA}/api/health", timeout=5)
    assert r.status_code == 200, f"Grafana unhealthy: {r.status_code}"


def main():
    print(f"\n{BOLD}JobPulse Platform Health Check{RESET}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    print(f"\n{BOLD}API Checks:{RESET}")
    check("API health endpoint", check_api_health)
    check("Jobs endpoint returns data", check_jobs_endpoint)
    check("Stats endpoint", check_stats_endpoint)
    check("Prometheus metrics exposed", check_metrics_endpoint)
    check("API response time under 500ms", check_api_response_time)
    check("Create job endpoint", check_create_job)

    print(f"\n{BOLD}Observability Checks:{RESET}")
    check("Prometheus is healthy", check_prometheus_health)
    check("All Prometheus targets up", check_prometheus_targets)
    check("Grafana is healthy", check_grafana_health)

    print("\n" + "=" * 50)
    total = passed + failed
    print(f"{BOLD}Results: {passed}/{total} passed{RESET}")

    if failed > 0:
        print(f"{RED}PLATFORM UNHEALTHY: {failed} check(s) failed{RESET}")
        sys.exit(1)
    else:
        print(f"{GREEN}PLATFORM HEALTHY: All checks passed{RESET}")
        sys.exit(0)


if __name__ == "__main__":
    main()
