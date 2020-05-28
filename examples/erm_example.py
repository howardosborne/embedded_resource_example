import sys, os
sys.path.append(os.getcwd)
from embedded_resource_manager import EmbeddedResourceManager
from locust import HttpUser, task, events, constant
import time

class HttpUserWithContent(HttpUser):
    host = "https://www.demoblaze.com"
    wait_time = constant(10)
    erm = EmbeddedResourceManager()

    @task
    def t(self):
        name = "/"
        response = self.client.get("/", name=name)
        resources = self.erm.get_embedded_resources(response.content, self.host)
        for resource in resources:
            self.client.get(resource, name=name+"_resources")
