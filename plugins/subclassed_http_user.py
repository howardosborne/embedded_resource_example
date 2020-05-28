from locust import HttpUser
    
class HttpUserWithContent(HttpUser):
    def __init__(self, parent):
        super().__init__(parent)
        super(HttpUser,self).client.get = self._request(super(HttpUser,self).client.get)
        self.erm = EmbeddedResourceManager()


    def _request(self, func):
        def wrapper(*args, **kwargs):
            response = None
            if 'include_resources' in kwargs:
                if kwargs['include_resources']: 
                    del kwargs['include_resources']
                    response = func(*args,**kwargs)
                    resources = self.erm.get_embedded_resources(response.content, self.host)
                    if 'name' in kwargs:
                        name = kwargs['name']
                        print("got name from kwargs " + name)
                    else:
                        name = args[0]
                    for resource in resources:
                        self.client.request("GET",resource, name=name+"_resources")
            return response
        return wrapper