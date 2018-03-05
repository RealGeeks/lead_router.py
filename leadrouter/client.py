import json  # todo: instal ujson

import requests


class HTTPError(Exception):
    '''
    Exception raised by Client methods when interacting with the API
    '''
    # original exception object raised by the http client library used
    # to make the request
    original = None

    # present if the error was an invalid status code given by the server, will
    # be an integer with the status code
    status_code = None

    # present if the error was an invalid status code given by the server, will
    # be the original response text from the server
    response_text = None


class Client(object):
    '''
    Client is a simple direct http client to the lead_router REST API

    http://docs.realgeeks.com/incoming_leads_api
    '''

    def __init__(self, host, user, token):
        self.host = prefix_http(host)
        self.auth = requests.auth.HTTPBasicAuth(user, token)

    def create_lead(self, site_uuid, lead, headers={}):
        url = '/rest/sites/{0}/leads'.format(site_uuid)
        return self._request('post', url, lead, headers=headers)

    def update_lead(self, site_uuid, lead_uuid, lead, headers={}):
        url = '/rest/sites/{0}/leads/{1}'.format(site_uuid, lead_uuid)
        return self._request('patch', url, lead, headers=headers)

    def add_activities(self, site_uuid, lead_uuid, activities, headers={}):
        url = '/rest/sites/{0}/leads/{1}/activities'.format(site_uuid, lead_uuid)
        return self._request('post', url, activities, headers=headers)

    def create_potential_seller_lead(self, site_uuid, lead, headers={}):
        url = '/rest/sites/{0}/potential-seller-leads'.format(site_uuid)
        return self._request('post', url, lead, headers=headers)

    def _request(self, method, url, body, headers={}):
        hdrs = {'Content-Type': 'application/json; charset=utf-8'}
        hdrs.update(headers)
        try:
            resp = requests.request(method, self.host+url, data=json.dumps(body),
                                    timeout=2, auth=self.auth, headers=hdrs)
            resp.raise_for_status()
        except requests.exceptions.RequestException as ex:
            raise wrap_requests_exception(ex)


def wrap_requests_exception(ex):
    '''
    For every requests exception we raise our own HTTPError.

    Depending if the request completed or not we include response
    information.  See HTTPError exception class

    '''
    if getattr(ex, 'response', None) is not None:
        try:
            message = ex.response.json()['error']
        except ValueError:
            message = str(ex)
        status_code = ex.response.status_code
        response_text = ex.response.text
    else:
        message = str(ex)
        status_code = None
        response_text = None

    new_ex = HTTPError(message)
    new_ex.original = ex
    new_ex.status_code = status_code
    new_ex.response_text = response_text

    return new_ex


def prefix_http(host):
    if host.startswith(('http://', 'https://')):
        return host
    return 'https://'+host
