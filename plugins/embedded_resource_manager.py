from lxml import html, etree
import logging
import re


class EmbeddedResourceManager:
    """
    provides features for finding and managing resources embedded in html
    """
    def __init__(self, user, include_resources_by_default=False, default_resource_filter=".*", bundle_resource_stats=True, cache_resource_links=True):

        # store resource links for requests
        self.cache_resource_links = cache_resource_links
        self.resource_link_cache = {}
        # bundle all stats into single line for each request (_resources)
        self.bundle_resource_stats = bundle_resource_stats
        self.resource_filter_pattern = re.compile(default_resource_filter)
        self.include_resources = include_resources_by_default
        # for finding url links in style tags
        self.url_link_pattern = re.compile(
            r".*URL\(\s*('|\")(.*)('|\")\s*\).*",
            re.IGNORECASE | re.MULTILINE | re.DOTALL,
        )

        # for finding if a link is partial or full
        self.full_url_pattern = re.compile("^https?://", re.IGNORECASE)

        self.resource_paths = [
            '//link[@rel="stylesheet"]/@href',
            '//link[@rel="Stylesheet"]/@href',
            '//link[@rel="STYLESHEET"]/@href',
            "//script/@src",
            "//img/@src",
            "//source/@src",
            "//embed/@src",
            "//body/@background",
            '//input[@type="image"]/@src',
            '//input[@type="IMAGE"]/@src',
            '//input[@type="Image"]/@src',
            "//object/@data",
            "//frame/@src",
            "//iframe/@src",
        ]

        self.client = user.client
        self.client.request = self._request(self.client.request)
        self.host = user.host

    def get_embedded_resources(self, response_content, **kwargs):
        """
        returns a list of embedded resources in response_content
        provide a regex filter to limit what resources are returned
        """
        resources = []
        #check if defaults have been overridden for this request
        if "resource_filter" in kwargs:
            resource_filter_pattern = re.compile(kwargs['resource_filter'])
        else:
            resource_filter_pattern = self.resource_filter_pattern

        if self.cache_resource_links and response_content in self.resource_link_cache:
            resources = self.resource_link_cache[response_content]
        else:
            try:
                tree = html.fromstring(response_content)
                # check for base tag - otherwise use host for partial urls
                base_path_links = tree.xpath("//base/@href")
                base_path = (
                    base_path_links[0] if len(base_path_links) > 0 else self.host
                )
                # build resource list
                for resource_path in self.resource_paths:
                    for resource in tree.xpath(resource_path):
                        if re.search(self.full_url_pattern, resource) is None:
                            resource = base_path + "/" + resource
                        if re.search(resource_filter_pattern, resource):
                            resources.append(resource)
                # add style urls
                style_tag_texts = tree.xpath("//style/text()")
                for text in style_tag_texts:
                    # check for url
                    url_matches = re.match(self.url_link_pattern, text)
                    if url_matches is not None:
                        resource = url_matches[2]
                        if re.search(self.full_url_pattern, resource) is None:
                            resource = base_path + "/" + resource
                        if re.search(resource_filter_pattern, resource):
                            resources.append(resource)
                if self.cache_resource_links:
                    self.resource_link_cache[response_content] = resources
            except etree.ParserError as e:
                logging.warning(str(e) + " " + str(response_content))
        return resources

    def _request(self, func):
        def wrapper(*args, **kwargs):
            # check if include_resources flag set
            if "include_resources" in kwargs:
                include_resources = kwargs["include_resources"]
                del kwargs["include_resources"]
            else:
                include_resources = self.include_resources

            response = func(*args, **kwargs)
            if include_resources:
                content = response.content
                if isinstance(content, bytearray):
                    content = content.decode("utf-8")
                resources = self.get_embedded_resources(content)
                name = kwargs.get("name", args[0])
                for resource in resources:
                    # determine name for the resource
                    if self.bundle_resource_stats:
                        resource_name = name + "_resources"
                    else:
                        resource_name = resource
                    self.client.request("GET", resource, name=resource_name, include_resources=False)
            return response

        return wrapper
