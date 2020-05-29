import sys, os
sys.path.append(os.getcwd())
from plugins.embedded_resource_manager import EmbeddedResourceManager
from locust import HttpUser, task, events
from locust.contrib.fasthttp import FastHttpUser
import time

class test(FastHttpUser):
    
    def on_start(self):
        EmbeddedResourceManager(self,cache_resource_links=True)

    @task
    def include_resources_true(self):
        name = "include resources_true"
        response = self.client.get("/", name=name, include_resources=True)

    @task
    def include_resources_missing(self):
        name = "include_resources_missing"
        response = self.client.get("/", name=name)

    @task
    def include_resources_false(self):
        name = "include_resources_false"
        response = self.client.get("/", name=name, include_resources=False)