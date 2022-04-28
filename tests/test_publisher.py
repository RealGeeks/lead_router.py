import json
import uuid

import beanstalkc
import pytest
import mock
from freezegun import freeze_time

from leadrouter import Publisher

def setup_function(f):
    global freezer
    freezer = freeze_time('2014-01-01 08:15:20')
    freezer.start()

def teardown_function(f):
    global freezer
    freezer.stop()

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
    bean_conn = beanstalkc.Connection('beanstalk', 11300)
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

    publisher.create_lead('123', {
        'email': 'lead@gmail.com',
        'activities': [{'type': 'a'}],
    })

    publisher._publish.assert_called_once_with('create_lead', {
        'site_uuid': '123',
        'lead': {
            'email': 'lead@gmail.com',
            'created': '2014-01-01T08:15:20+00:00',                    # set timestamp
            'activities': [
                {'type': 'a', 'created': '2014-01-01T08:15:20+00:00'}, # set timestamp
            ],
        }
    })

def test_create_lead_dont_override_timestamps(publisher):
    publisher._publish = mock.Mock()

    publisher.create_lead('123', {
        'email': 'lead@gmail.com',
        'created': '2010-01-01T08:15:20',
        'activities': [
            {'type': 'b', 'created': '2010-01-01T08:15:20'},
        ],
    })

    publisher._publish.assert_called_once_with('create_lead', {
        'site_uuid': '123',
        'lead': {
            'email': 'lead@gmail.com',
            'created': '2010-01-01T08:15:20',
            'activities': [
                {'type': 'b', 'created': '2010-01-01T08:15:20'},
            ],
        }
    })

def test_update_lead(publisher):
    publisher._publish = mock.Mock()

    publisher.update_lead('123', 'abc', {
        'email': 'lead@gmail.com',
        'activities': [{'type': 'a'}],
    })

    publisher._publish.assert_called_once_with('update_lead', {
        'site_uuid': '123',
        'lead_uuid': 'abc',
        'lead': {
            'email': 'lead@gmail.com',
            'activities': [
                {'type': 'a', 'created': '2014-01-01T08:15:20+00:00'}, # set timestamp
            ],
        }
    })

def test_update_lead_dont_override_timestamps(publisher):
    publisher._publish = mock.Mock()

    publisher.update_lead('123', 'abc', {
        'email': 'lead@gmail.com',
        'activities': [
            {'type': 'b', 'created': '2010-01-01T08:15:20'},
        ],
    })

    publisher._publish.assert_called_once_with('update_lead', {
        'site_uuid': '123',
        'lead_uuid': 'abc',
        'lead': {
            'email': 'lead@gmail.com',
            'activities': [
                {'type': 'b', 'created': '2010-01-01T08:15:20'},
            ],
        }
    })

def test_add_activities(publisher):
    publisher._publish = mock.Mock()

    publisher.add_activities('123', 'abc', [
        {'type': 'a', 'created': '2010-01-01T08:15:20'},
        {'type': 'b'},
    ])

    publisher._publish.assert_called_once_with('add_activities', {
        'site_uuid': '123',
        'lead_uuid': 'abc',
        'activities': [
            {'type': 'a', 'created': '2010-01-01T08:15:20'},
            {'type': 'b', 'created': '2014-01-01T08:15:20+00:00'}, # set timestamp,
        ],
    })

def test_create_potential_seller_lead(publisher):
    publisher._publish = mock.Mock()

    publisher.create_potential_seller_lead('123', {
        'source_details': 'here',
        'activities': [{'type': 'a'}],
    })

    publisher._publish.assert_called_once_with('create_potential_seller_lead', {
        'site_uuid': '123',
        'lead': {
            'source_details': 'here',
            'created': '2014-01-01T08:15:20+00:00',                    # set timestamp
            'activities': [
                {'type': 'a', 'created': '2014-01-01T08:15:20+00:00'}, # set timestamp
            ],
        }
    })

def test_create_potential_seller_lead_dont_override_timestamps(publisher):
    publisher._publish = mock.Mock()

    publisher.create_potential_seller_lead('123', {
        'source_details': 'here',
        'created': '2010-01-01T08:15:20',
        'activities': [
            {'type': 'b', 'created': '2010-01-01T08:15:20'},
        ],
    })

    publisher._publish.assert_called_once_with('create_potential_seller_lead', {
        'site_uuid': '123',
        'lead': {
            'source_details': 'here',
            'created': '2010-01-01T08:15:20',
            'activities': [
                {'type': 'b', 'created': '2010-01-01T08:15:20'},
            ],
        }
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

def test_publish_priorities(publisher):
    publisher._publish('update_lead', params={
        'lead': {'email': 'lead@gmail.com'},
        'site_uuid': '123-abc',
        'lead_uuid': 'abc',
    })
    publisher._publish('add_activities', params={
        'site_uuid': '123',
        'lead_uuid': 'abc',
        'activities': [{'type': 'a', 'type': 'b'}],
    })
    publisher._publish('create_lead', params={
        'lead': {'email': 'lead@gmail.com'},
        'site_uuid': '123-abc',
    })

    # 1st
    package = last_package(publisher.bean_tube)
    assert package['method'] == 'create_lead'

    # 2nd
    package = last_package(publisher.bean_tube)
    assert package['method'] == 'add_activities'

    # 3rd
    package = last_package(publisher.bean_tube)
    assert package['method'] == 'update_lead'

def test_publish_reconnect(publisher):
    publisher.queue = mock.Mock(['put', 'close'])
    publisher.queue.put.side_effect = [beanstalkc.SocketError(), None]
    publisher.connect = mock.Mock()

    publisher._publish('create_lead', params={
        'lead': {'email': 'lead@gmail.com'},
        'site_uuid': '123-abc',
    })

    # queue.put() 1st call failed and second succeeded
    assert publisher.queue.put.call_count == 2

    # after queue.put() first call we called connect() again
    assert publisher.connect.call_count == 1
