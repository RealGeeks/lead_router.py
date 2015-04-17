import json
import uuid

import beanstalkc
import pytest
import mock

from leadrouter import Publisher


@pytest.fixture
def publisher(request):
    pub = Publisher('api.com', 'user', 'secret', beanstalkd_tube=generate_tube())
    request.addfinalizer(pub.close)
    return pub

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


def test_create_lead(publisher):
    publisher._publish = mock.Mock()

    publisher.create_lead('123', {'email': 'lead@gmail.com'})

    publisher._publish.assert_called_once_with('create_lead', {
        'site_uuid': '123',
        'lead': {'email': 'lead@gmail.com'}
    })

def test_update_lead(publisher):
    publisher._publish = mock.Mock()

    publisher.update_lead('123', 'abc', {'email': 'lead@gmail.com'})

    publisher._publish.assert_called_once_with('update_lead', {
        'site_uuid': '123',
        'lead_uuid': 'abc',
        'lead': {'email': 'lead@gmail.com'}
    })

def test_add_activities(publisher):
    publisher._publish = mock.Mock()

    publisher.add_activities('123', 'abc', [{'type': 'a', 'type': 'b'}])

    publisher._publish.assert_called_once_with('add_activities', {
        'site_uuid': '123',
        'lead_uuid': 'abc',
        'activities': [{'type': 'a', 'type': 'b'}],
    })

def test_publish(publisher):
    publisher._publish('create_lead', params={
        'lead': {'email': 'lead@gmail.com'},
        'site_uuid': '123-abc',
    })

    package = last_package(publisher.bean_tube)

    assert package == {
        'host': 'api.com',
        'auth': ['user', 'secret'],
        'method': 'create_lead',
        'params': {
            'lead': {'email': 'lead@gmail.com'},
            'site_uuid': '123-abc'},
        }
