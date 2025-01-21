from locust import HttpUser, task

import random

class TestUser(HttpUser):
    @task
    def test(self):
        # new_staff_code = random.
        payload = random.choice(
            [
                "hello",
                "self.http_code = http_code if http_code else HTTP_500_INTERNAL_SERVER_ERROR",
                "    def bad_request_exception(message: str):",
                "    def unauthorized_exception(message: str):",
                "    def forbiden_exception(message: str):",                
            ]
        )
        self.client.post("/api/v1/llm/answer", json=payload)