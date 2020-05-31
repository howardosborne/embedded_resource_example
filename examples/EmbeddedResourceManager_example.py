import sys, os
sys.path.append(os.getcwd())
from plugins.embedded_resource_manager import HttpUserWithResources
from locust import task, events
import time

class TestUserWithResources(HttpUserWithResources):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, include_resources_by_default=True, default_resource_filter=".*", bundle_resource_stats=True, cache_resource_links=False)

    @task
    def include_resources_true(self):
        response = self.client.get("/", resource_filter=".*[^(js)]$")

    @task
    def include_resources_missing(self):
        response = self.client.get("/cart.html")

    @task
    def include_resources_false(self):
        response = self.client.get("/index.html", include_resources=False)