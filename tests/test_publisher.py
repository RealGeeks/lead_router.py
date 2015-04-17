import json
import uuid

import beanstalkc
import pytest
import mock

from leadrouter import Publisher


def new_publisher(*args, **kwargs):
    try:
        return Publisher(*args, **kwargs)
    except beanstalkc.SocketError:
        pytest.fail('beanstalkd not running. See README.md for instructions')

def last_package(tube):
    '''
    Return last package put in the queue. Fail test if queue is empty
    '''
    # connect to beanstalk watching only the current tube
    bean_conn = beanstalkc.Connection('localhost', 11300)
    bean_conn.watch(tube)
    bean_conn.ignore('default')
    job = bean_conn.reserve(timeout=0.5)
    try:
        package = job.body
        job.delete()
        return json.loads(package)
    except AttributeError:  # job is None
        pytest.fail('tube {0} is empty'.format(tube))
    finally:
        bean_conn.close()

def generate_tube():
    '''
    Generate random name for a tube
    Each test uses it's own tube to avoid tests affecting each other
    '''
    return str(uuid.uuid4())


def test_create_lead():
    pub = Publisher('api.com', 'user', 'secret')
    pub._publish = mock.Mock()

    pub.create_lead('123', {'email': 'lead@gmail.com'})

    pub._publish.assert_called_once_with('create_lead', {
        'site_uuid': '123',
        'lead': {'email': 'lead@gmail.com'}
    })

def test_update_lead():
    pub = Publisher('api.com', 'user', 'secret')
    pub._publish = mock.Mock()

    pub.update_lead('123', 'abc', {'email': 'lead@gmail.com'})

    pub._publish.assert_called_once_with('update_lead', {
        'site_uuid': '123',
        'lead_uuid': 'abc',
        'lead': {'email': 'lead@gmail.com'}
    })

def test_add_activities():
    pub = Publisher('api.com', 'user', 'secret')
    pub._publish = mock.Mock()

    pub.add_activities('123', 'abc', [{'type': 'a', 'type': 'b'}])

    pub._publish.assert_called_once_with('add_activities', {
        'site_uuid': '123',
        'lead_uuid': 'abc',
        'activities': [{'type': 'a', 'type': 'b'}],
    })

def test_publish():
    tube = generate_tube()
    pub = new_publisher('api.com', 'user', 'secret', beanstalkd_tube=tube)

    pub._publish('create_lead', params={
        'lead': {'email': 'lead@gmail.com'},
        'site_uuid': '123-abc',
    })

    package = last_package(tube)

    assert package == {
        'host': 'api.com',
        'auth': ['user', 'secret'],
        'method': 'create_lead',
        'params': {
            'lead': {'email': 'lead@gmail.com'},
            'site_uuid': '123-abc'},
        }
