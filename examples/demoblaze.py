from locust import HttpUser, SequentialTaskSet, task, between, events
#from locust_plugins.jmeter_listener import JmeterListener
from plugins.embedded_resource_manager import EmbeddedResourceManager
import logging

import json, random, string

class MakePurchase(SequentialTaskSet):
    
    def on_start(self):
        #use protocol analyser to debug
        #self.client.proxies = { "http"  : "http://localhost:8888", "https" : "https://localhost:8888"}
        #self.client.verify = False
        r_s = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
        self.user_cookie = r_s[:8] + "-" + r_s[8:12] + "-" + r_s[12:16] + "-" + r_s[16:20] + "-" + r_s[20:32]
        r_s = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
        self.purchase_id = r_s[:8] + "-" + r_s[8:12] + "-" + r_s[12:16] + "-" + r_s[16:20] + "-" + r_s[20:32]


    #@tag('browse')
    #@tag('purchase')
    @task
    def get_config_json(self):
        response = self.client.get("/config.json", name="02 /config.json", include_resources=True)
        response_json = json.loads(response.text)
        self.api_host = response_json["API_URL"]

    #@tag('browse')
    #@tag('purchase')
    @task
    def third_task(self):
        response = self.client.get(self.api_host + "/entries", name="03 /entries", include_resources=True)
        response_json = json.loads(response.text)
        self.id = response_json["Items"][0]["id"]

    #@tag('browse')
    #@tag('purchase')
    @task
    def fourth_task(self):
        self.client.cookies["user"] = self.user_cookie
        response = self.client.get("/prod.html?idp_=" + str(self.id), name="04 /prod.html?idp_", include_resources=True)

    #@tag('purchase')
    @task
    def fifth_task(self):
        payload = '{"id":"' + str(self.id) + '"}'
        response = self.client.post(self.api_host + "/view", payload , headers={"Content-Type": "application/json"}, name="05 /view", include_resources=True)

    #@tag('purchase')
    @task
    def sixth_task(self):
        payload = '{"id":"' + self.purchase_id + '","cookie":"user=' + self.user_cookie + '","prod_id":' + str(self.id) + ',"flag":false}'
        response = self.client.post(self.api_host + "/addtocart", payload, headers={"Content-Type": "application/json"},  name="06 /addtocart", include_resources=True)

    #@tag('purchase')
    @task
    def seventh_task(self):
        response = self.client.get("/cart.html", name="07 /cart.html", include_resources=True)

    #@tag('purchase')
    @task
    def eighth_task(self):
        payload = '{"cookie":"user=' + self.user_cookie + '","flag":false}'
        response = self.client.post(self.api_host + "/viewcart", payload, headers={"Content-Type": "application/json"},  name="08 /viewcart", include_resources=True)

    #@tag('purchase')
    @task
    def ninth_task(self):
        payload = '{"cookie":"user=' + self.user_cookie + '"}'
        #response = self.client.post(self.api_host + "/deletecart", payload, headers={"Content-Type": "application/json"},  name="09 /deletecart", catch_response=True)
        with self.client.post(self.api_host + "/deletecart", payload, headers={"Content-Type": "application/json"},  name="09 /deletecart", catch_response=True, include_resources=True) as response:
            if response.content != b"Delete complete":
                response.failure("delete incomplete")

class DemoBlazePurchaser(HttpUser):
    wait_time = between(2, 5)
    tasks = [MakePurchase]
    def on_start(self):
        EmbeddedResourceManager(self,cache_resource_links=True)

class DemoBlazeBrowser(HttpUser):
    wait_time = between(2, 5)
    def on_start(self):
        EmbeddedResourceManager(self,cache_resource_links=True)
    @task
    def home(self):
        self.client.get("/", name ="01 /")
    
