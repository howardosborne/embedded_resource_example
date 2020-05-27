from locust import HttpUser, User
from locust import task, events, constant

class HttpUserWithContent(HttpUser):

    def __init__(self, parent):
        super().__init__(parent)
        super().client.get = get
            
    #create childclass of session which will be used
    def get(self, **kwargs):
        print(kwargs)
        pass
    