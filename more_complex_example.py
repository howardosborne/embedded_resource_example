from locust import HttpUser, task, events, constant
import time
from lxml import html
import re

#for finding url links in style tags
url_link_pattern = re.compile("URL\(\s*('|\")(.*)('|\")\s*\)",re.IGNORECASE | re.MULTILINE)
#for finding if a link is partial or full
full_url_pattern = re.compile("^https?://",re.IGNORECASE)
resource_paths = ['//link[@rel="stylesheet"]/@href', '//link[@rel="Stylesheet"]/@href',
    '//link[@rel="STYLESHEET"]/@href','//script/@src',
    '//img/@src', '//source/@src', '//embed/@src',
    '//body/@background', '//input[@type="image"]/@src',
    '//input[@type="IMAGE"]/@src','//input[@type="Image"]/@src',
    '//object/@data', '//frame/@src', '//iframe/@src']

def get_embedded_resources(response_content, host, filter='.*'):
    resources = []
    tree = html.fromstring(response_content)
    #check for base tag - otherwise use host for partial urls
    base_path_links = tree.xpath('//base/@href')
    base_path = base_path_links[0] if len(base_path_links) > 0 else host
    #build resource list
    for resource_path in resource_paths:
        for resource in tree.xpath(resource_path):
            if re.search(full_url_pattern, resource) == None: resource = base_path + "/" + resource
            if re.search(filter, resource):
                resources.append(resource)
    #add style urls
    style_tag_texts = tree.xpath('//style/text()')
    for text in style_tag_texts:
        #check for url
        url_matches = re.match(url_link_pattern,text)
        if url_matches != None:
            for url_match in url_matches:
                print(url_match.group())
    return resources

resource_link_cache = {}	
		
class HttpUserWithContent(HttpUser):
    host = "https://www.demoblaze.com"
    wait_time = constant(10)
    
    @task
    def t(self):
        name = "/"
        response = self.client.get("/", name=name)
        resources = []
        if name in resource_link_cache:
            resources = resource_link_cache[name]
        else:
            resources = get_embedded_resources(response.content, self.host)
            resource_link_cache[name] = resources
        for resource in resources:
            self.client.get(resource, name=name + "_resources")
