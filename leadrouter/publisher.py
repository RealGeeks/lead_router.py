import json  # todo: instal ujson

import beanstalkc

class Publisher(object):
    '''
    Producer implements the same interface as Client but instead of sending requests
    directly to the API it adds the requests to a Beanstalkd queue to be consumed
    by Consumer.

    Require a consumer process to be running reading from the same queue (called tube
    in beanstalkd) and actually performing the specified requests

    The job published in the tube has all information necessary to instantiate a
    valid Client() object (with credentials) and call one of it's methods

    '''

    def __init__(self, host, user, token,
                 beanstalkd_host='localhost',
                 beanstalkd_port=11300,
                 beanstalkd_tube='leadrouter'):
        self.host = host
        self.auth = (user, token)
        self.queue = beanstalkc.Connection(beanstalkd_host, beanstalkd_port)
        self.queue.use(beanstalkd_tube)

    def create_lead(self, site_uuid, lead):
        return self._publish('create_lead', {
            'site_uuid': site_uuid,
            'lead': lead,
        })

    def update_lead(self, site_uuid, lead_uuid, lead):
        return self._publish('update_lead', {
            'site_uuid': site_uuid,
            'lead_uuid': lead_uuid,
            'lead': lead,
        })

    def add_activities(self, site_uuid, lead_uuid, activities):
        return self._publish('add_activities', {
            'site_uuid': site_uuid,
            'lead_uuid': lead_uuid,
            'activities': activities,
        })

    def _publish(self, method, params):
        self.queue.put(json.dumps({
            'host': self.host,
            'auth': self.auth,
            'method': method,
            'params': params
        }))
