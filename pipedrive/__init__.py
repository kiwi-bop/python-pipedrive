from logging import getLogger

import requests


PIPEDRIVE_API_URL = "https://api.pipedrive.com/v1/"
logger = getLogger('pipedrive')


class PipedriveError(Exception):
    def __init__(self, response):
        self.response = response

    def __str__(self):
        return self.response.get('error', 'No error provided')


class IncorrectLoginError(PipedriveError):
    pass


class Pipedrive(object):
    def _request(self, endpoint, data, method='POST'):
        uri = PIPEDRIVE_API_URL + endpoint
        payload = {'api_token': self.api_token}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        # avoid storing the string 'None' when a value is None
        data = {k: "" if v is None else v for k, v in data.items()}
        if method == "GET":
            if data:
                payload.update(data)
            response = self.http.request(method, uri, params=payload, headers=headers)
        else:
            response = self.http.request(method, uri, data=data, params=payload, headers=headers)

        logger.debug('sending {method} request to {uri}'.format(
            method=method,
            uri=response.url
        ))
        return response.json()

    def __init__(self, email, password=None):
        self.http = requests.Session()
        if password:
            response = self._request("/authorizations/", {"email": email, "password": password})

            if 'error' in response:
                raise IncorrectLoginError(response)

            # self.api_token = response['authorization'][0]['api_token']
            self.api_token = response['data'][0]['api_token']
            print('api_token is ' + self.api_token)
        else:
            # Assume that login is actually the api token
            self.api_token = email

    def __getattr__(self, name):
        def wrapper(data={}, method='GET'):
            response = self._request(name.replace('_', '/'), data, method)
            if 'error' in response:
                raise PipedriveError(response)
            return response
        return wrapper
