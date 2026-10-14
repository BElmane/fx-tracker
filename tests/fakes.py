"""Fake objects shared by the tests. They pretend to be the internet."""

HTTP_OK = 200


class FakeResponse:
    """Pretends to be a response from the API."""

    def __init__(self, status_code, data):
        self.status_code = status_code
        self.ok = status_code == HTTP_OK
        self._data = data

    def json(self):
        return self._data


class FakeSession:
    """Pretends to send web requests. Remembers the last URL."""

    def __init__(self, response=None, error=None):
        self._response = response
        self._error = error
        self.last_url = None

    def get(self, url, timeout):
        self.last_url = url
        if self._error:
            raise self._error
        return self._response
    