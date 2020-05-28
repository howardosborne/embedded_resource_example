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
    def __init__(self, parent):
        super().__init__(parent)
        self.client.get = self._request(self.client.get)

    def _request(self, func):
        def wrapper(*args, **kwargs):
            response = None
            if 'include_resources' in kwargs:
                if kwargs['include_resources']: 
                    del kwargs['include_resources']
                    response = func(*args,**kwargs)
                    resources = get_embedded_resources(response.content)
                    if 'name' in kwargs:
                        name = kwargs['name']
                        print(name)
                    else:
                        name = args[0]
                    for resource in resources:
                        if re.search("^https?://", resource) == None: resource = self.host + "/" + resource
                        self.client.request("GET",resource, name=name+"_resources")
            return response
        return wrapper

    @task
    def t(self):
        name = "/"
        response = self.client.get("/", name=name, include_resources=True)

