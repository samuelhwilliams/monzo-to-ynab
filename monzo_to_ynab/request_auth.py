import requests


class HTTPBearerAuth(requests.auth.AuthBase):
    """Helper to inject the Bearer authorisation token into a request"""

    def __init__(self, token: str):
        self.token = token

    def __call__(self, r: requests.Request):
        if "Authorization" not in r.headers:
            r.headers["Authorization"] = f"Bearer {self.token}"

        return r
