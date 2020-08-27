from urllib.parse import urlparse, parse_qs, unquote


class BaseRepository:
    def __init__(self, req):
        self.req = req

    def validate_args(self):
        return parse_qs(urlparse(unquote(self.req.url)).query)
