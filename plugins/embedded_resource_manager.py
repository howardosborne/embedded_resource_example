from lxml import html
import re 

class EmbeddedResourceManager():
    """
    provides features for finding and managing resources embedded in html
    """
    def __init__(self):
        #for finding url links in style tags
        self.url_link_pattern = re.compile("URL\(\s*('|\")(.*)('|\")\s*\)",re.IGNORECASE | re.MULTILINE)

        #for finding if a link is partial or full
        self.full_url_pattern = re.compile("^https?://",re.IGNORECASE)

        self.resource_paths = ['//link[@rel="stylesheet"]/@href', '//link[@rel="Stylesheet"]/@href',
    '//link[@rel="STYLESHEET"]/@href','//script/@src',
    '//img/@src', '//source/@src', '//embed/@src',
    '//body/@background', '//input[@type="image"]/@src',
    '//input[@type="IMAGE"]/@src','//input[@type="Image"]/@src',
    '//object/@data', '//frame/@src', '//iframe/@src']

        self.resource_link_cache = {}	

    def get_embedded_resources(self,response_content, host="", cache_resources=False, filter='.*'):
        """
        returns a list of embedded resources in response_content
        provide a host to complete partial urls
        set cache_resources to true for greater efficiency
        provide a regex filter to limit what resources are returned
        """
        if cache_resources == True and response_content in self.resource_link_cache:
               return resource_link_cache[response_content]
        else:
            resources = []
            tree = html.fromstring(response_content)
            #check for base tag - otherwise use host for partial urls
            base_path_links = tree.xpath('//base/@href')
            base_path = base_path_links[0] if len(base_path_links) > 0 else host
            #build resource list
            for resource_path in self.resource_paths:
                for resource in tree.xpath(resource_path):
                    if re.search(self.full_url_pattern, resource) == None: resource = base_path + "/" + resource
                    if re.search(filter, resource):
                        resources.append(resource)
            #add style urls
            style_tag_texts = tree.xpath('//style/text()')
            for text in style_tag_texts:
                #check for url
                url_matches = re.match(self.url_link_pattern,text)
                if url_matches != None:
                    for url_match in url_matches:
                        print(url_match.group())
            if cache_resources == True: resource_link_cache[response_content] = resources
            return resources
