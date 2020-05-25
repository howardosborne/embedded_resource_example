from locust import HttpUser, task, events, constant
import time
from lxml import html
import re

resource_paths = ['//link/@href', '//script/@src','//img/@src', '//source/@src', '//embed/@src']

def get_embedded_resources(response_content, filter='.*'):
    resources = []
    tree = html.fromstring(response_content)
    for resource_path in resource_paths:
        for resource in tree.xpath(resource_path):
            if re.search(filter, resource): resources.append(resource)
    return resources
	
		
class HttpUserWithContent(HttpUser):
    host = "https://www.demoblaze.com"
    wait_time = constant(10)
    
    @task
    def t(self):
        name = "/"
        response = self.client.get("/", name=name)
        resources = get_embedded_resources(response.content)
        for resource in resources:
            if re.search("^https?://", resource) == None: resource = self.host + "/" + resource          
            self.client.get(resource, name=name+"_resources")
