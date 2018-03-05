import re

import requests
import httpretty
import mock
import pytest

from leadrouter import Client, HTTPError

def test_create_lead_request():
    c = Client('api.com', 'user', 'token')
    c._request = mock.Mock()

    c.create_lead('123', {'email': 'lead@gmail.com'})

    c._request.assert_called_once_with('post', '/rest/sites/123/leads',
                                       {'email': 'lead@gmail.com'},
                                       headers={})

def test_create_lead_request_with_custom_headers():
    c = Client('api.com', 'user', 'token')
    c._request = mock.Mock()

    c.create_lead('123', {'email': 'lead@gmail.com'}, headers={'User-Agent': 'Me'})

    c._request.assert_called_once_with('post', '/rest/sites/123/leads',
                                       {'email': 'lead@gmail.com'},
                                       headers={'User-Agent': 'Me'})

def test_update_lead_request():
    c = Client('api.com', 'user', 'token')
    c._request = mock.Mock()

    c.update_lead('123', '432', {'email': 'lead@gmail.com'})

    c._request.assert_called_once_with('patch', '/rest/sites/123/leads/432',
                                       {'email': 'lead@gmail.com'},
                                       headers={})

def test_update_lead_request_with_custom_headers():
    c = Client('api.com', 'user', 'token')
    c._request = mock.Mock()

    c.update_lead('123', '432', {'email': 'lead@gmail.com'}, headers={'User-Agent': 'Me'})

    c._request.assert_called_once_with('patch', '/rest/sites/123/leads/432',
                                       {'email': 'lead@gmail.com'},
                                       headers={'User-Agent': 'Me'})

def test_add_activities_request():
    c = Client('api.com', 'user', 'token')
    c._request = mock.Mock()

    c.add_activities('123', '543', [{'type': 'one'}, {'type': 'two'}])

    c._request.assert_called_once_with('post', '/rest/sites/123/leads/543/activities',
                                       [{'type': 'one'}, {'type': 'two'}],
                                       headers={})

def test_add_activities_request_with_custom_headers():
    c = Client('api.com', 'user', 'token')
    c._request = mock.Mock()

    c.add_activities('123', '543', [{'type': 'one'}, {'type': 'two'}], headers={'User-Agent': 'Me'})

    c._request.assert_called_once_with('post', '/rest/sites/123/leads/543/activities',
                                       [{'type': 'one'}, {'type': 'two'}],
                                       headers={'User-Agent': 'Me'})

def test_create_potential_seller_lead_request():
    c = Client('api.com', 'user', 'token')
    c._request = mock.Mock()

    c.create_potential_seller_lead('123', {'id': '123'})

    c._request.assert_called_once_with('post', '/rest/sites/123/potential-seller-leads',
                                       {'id': '123'},
                                       headers={})

def test_create_potential_seller_lead_request_with_custom_headers():
    c = Client('api.com', 'user', 'token')
    c._request = mock.Mock()

    c.create_potential_seller_lead('123', {'id': '123'}, headers={'User-Agent': 'Me'})

    c._request.assert_called_once_with('post', '/rest/sites/123/potential-seller-leads',
                                       {'id': '123'},
                                       headers={'User-Agent': 'Me'})

# _request() is the method used by all methods of Client(), so we test it
# exhaustively

@httpretty.activate
def test_request_sent():
    "Ensure the request sent by _request() is built correctly"

    httpretty.register_uri(httpretty.PUT, re.compile(r'.*'))

    c = Client('api.com', 'user', 'token')
    c._request('put', '/endpoint', {"email":"lead@gmail.com"})

    request = httpretty.last_request()

    assert request.path == '/endpoint'
    assert request.method == 'PUT'
    assert request.body == '{"email": "lead@gmail.com"}'
    assert request.headers['Host'] == 'api.com'
    assert request.headers['Authorization'] == 'Basic dXNlcjp0b2tlbg=='
    assert request.headers['Content-Type'] == 'application/json; charset=utf-8'

@httpretty.activate
def test_request_sent_with_custom_headers():
    "Ensure the request sent by _request() is built correctly"

    httpretty.register_uri(httpretty.PUT, re.compile(r'.*'))

    c = Client('api.com', 'user', 'token')
    c._request('put', '/endpoint', {"email":"lead@gmail.com"}, headers={
        'User-Agent': 'me :)',
        'X-Custom-Header': 'custom',
        'Content-Type': 'application/json', # can override the default
    })

    request = httpretty.last_request()

    assert request.headers['user-agent'] == 'me :)'
    assert request.headers['x-custom-header'] == 'custom'
    assert request.headers['content-type'] == 'application/json'

@httpretty.activate
def test_request_returns_invalid_status_code_with_error_in_body():
    httpretty.register_uri(httpretty.POST, 'https://api.com/endpoint',
                           body='{"error": "something went wrong"}',
                           content_type='application/json',
                           status=400)

    c = Client('api.com', 'user', 'token')

    with pytest.raises(HTTPError) as exc_info:
        c._request('post', '/endpoint', {"email":"lead@gmail.com"})

    http_error = exc_info.value

    assert str(http_error) == 'something went wrong'
    assert http_error.status_code == 400
    assert http_error.response_text == '{"error": "something went wrong"}'


@httpretty.activate
def test_request_returns_invalid_status_code_without_nice_error_message():
    httpretty.register_uri(httpretty.POST, 'https://api.com/endpoint',
                           body='<strong>Sorry...</strong>',
                           content_type='application/json',
                           status=503)

    c = Client('api.com', 'user', 'token')

    with pytest.raises(HTTPError) as exc_info:
        c._request('post', '/endpoint', {"email":"lead@gmail.com"})

    http_error = exc_info.value

    assert str(http_error) == '503 Server Error: Service Unavailable for url: https://api.com/endpoint'
    assert http_error.status_code == 503
    assert http_error.response_text == "<strong>Sorry...</strong>"


@mock.patch('requests.request')
def test_request_failed_to_be_sent(requests_request):
    exception = requests.exceptions.ConnectionError("can't connect")
    requests_request.side_effect = exception

    c = Client('api.com', 'user', 'token')
    with pytest.raises(HTTPError) as exc_info:
        c._request('post', '/endpoint', {"email":"lead@gmail.com"})

    http_error = exc_info.value

    assert str(http_error) == "can't connect"
    assert http_error.original is exception
    assert http_error.status_code is None
    assert http_error.response_text is None


@mock.patch('requests.request')
def test_request_failed_with_exception_that_doesnt_have_much_information(requests_request):
    # I found this bug in production, not sure how requests could raise a
    # Timeout without a 'response' attribute
    #
    # I didn't have a stack trace, only a log line:
    # 'Timeout' object has no attribute 'response'
    #
    # so just to be safe I'll handle it here
    exception = requests.exceptions.Timeout("timeout")
    delattr(exception, "response")
    delattr(exception, "request")

    requests_request.side_effect = exception

    c = Client('api.com', 'user', 'token')
    with pytest.raises(HTTPError) as exc_info:
        c._request('post', '/endpoint', {"email":"lead@gmail.com"})

    http_error = exc_info.value

    assert str(http_error) == "timeout"
    assert http_error.original is exception
    assert http_error.status_code is None
    assert http_error.response_text is None
