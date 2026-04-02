"""
JobPulse Load Testing Suite
Simulates realistic job board traffic patterns
"""
from locust import HttpUser, task, between
import random
import json


class JobBoardUser(HttpUser):
    wait_time = between(0.5, 2)

    def on_start(self):
        self.job_ids = [1, 2, 3]

    @task(5)
    def browse_jobs(self):
        with self.client.get(
            "/jobs",
            catch_response=True,
            name="GET /jobs"
        ) as response:
            if response.status_code == 200:
                try:
                    jobs = response.json()
                    if jobs:
                        self.job_ids = [j["id"] for j in jobs]
                    response.success()
                except Exception:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(3)
    def view_job(self):
        job_id = random.choice(self.job_ids)
        with self.client.get(
            f"/jobs/{job_id}",
            catch_response=True,
            name="GET /jobs/:id"
        ) as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(2)
    def health_check(self):
        with self.client.get(
            "/health",
            catch_response=True,
            name="GET /health"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "ok":
                    response.success()
                else:
                    response.failure("Status not ok")
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(1)
    def post_job(self):
        titles = [
            "SRE Engineer", "DevOps Engineer", "Platform Engineer",
            "Cloud Architect", "Infrastructure Engineer"
        ]
        companies = ["TechCorp", "CloudBase", "DataFlow", "NetSystems"]
        locations = ["London", "Manchester", "Fleet", "Birmingham", "Remote"]

        with self.client.post(
            "/jobs",
            json={
                "title": random.choice(titles),
                "company": random.choice(companies),
                "location": random.choice(locations),
                "salary_min": random.randint(40000, 60000),
                "salary_max": random.randint(60000, 80000),
                "description": "Load test generated job"
            },
            catch_response=True,
            name="POST /jobs"
        ) as response:
            if response.status_code == 201:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(1)
    def apply_for_job(self):
        job_id = random.choice(self.job_ids)
        with self.client.post(
            f"/jobs/{job_id}/apply",
            json={"email": f"loadtest{random.randint(1,9999)}@test.com"},
            catch_response=True,
            name="POST /jobs/:id/apply"
        ) as response:
            if response.status_code in [201, 404, 500]:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(1)
    def view_stats(self):
        with self.client.get(
            "/stats",
            catch_response=True,
            name="GET /stats"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")
