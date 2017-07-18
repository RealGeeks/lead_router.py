import json  # todo: instal ujson
import datetime


from . import timestamp

PRIORITIES = {
    'create_lead': 0,
    'add_activities': 3,
    'update_lead': 6,
    'create_potential_seller_lead': 6,
}

class Publisher(object):
    '''
    Producer implements the same interface as Client but instead of sending requests
    directly to the API it adds the requests to a Beanstalkd queue to be consumed
    by Consumer.

    Require a consumer process to be running reading from the same queue (called tube
    in beanstalkd) and actually performing the specified requests

    The job published in the tube has all information necessary to instantiate a
    valid Client() object (with credentials) and call one of it's methods

    We automatically set 'created' to both lead and all activities, because the job
    could take some time to be successfully processed

    '''

    def __init__(self, host, user, token,
                 beanstalkd_host='localhost',
                 beanstalkd_port=11300,
                 beanstalkd_tube='leadrouter'):
        self.host = host
        self.auth = (user, token)
        self.bean_host = beanstalkd_host
        self.bean_port = beanstalkd_port
        self.bean_tube = beanstalkd_tube
        self.queue = None

    def connect(self):
        import beanstalkc
        self.queue = beanstalkc.Connection(self.bean_host, self.bean_port)
        self.queue.use(self.bean_tube)

    def close(self):
        if self.queue:
            self.queue.close()
            self.queue = None

    def create_lead(self, site_uuid, lead):
        set_timestamp(lead)
        set_timestamp(*lead.get('activities', []))
        return self._publish('create_lead', {
            'site_uuid': site_uuid,
            'lead': lead,
        })

    def update_lead(self, site_uuid, lead_uuid, lead):
        set_timestamp(*lead.get('activities', []))
        return self._publish('update_lead', {
            'site_uuid': site_uuid,
            'lead_uuid': lead_uuid,
            'lead': lead,
        })

    def add_activities(self, site_uuid, lead_uuid, activities):
        set_timestamp(*activities)
        return self._publish('add_activities', {
            'site_uuid': site_uuid,
            'lead_uuid': lead_uuid,
            'activities': activities,
        })

    def create_potential_seller_lead(self, site_uuid, lead):
        set_timestamp(lead)
        set_timestamp(*lead.get('activities', []))
        return self._publish('create_potential_seller_lead', {
            'site_uuid': site_uuid,
            'lead': lead,
        })

    def _publish(self, method, params):
        '''Format and send a job to beanstalk

        It won't retry on failure but it knows how to reconnect if the connection
        was lost at some point after connect()
        '''
        import beanstalkc
        if not self.queue:
            self.connect()
        body = json.dumps({
            'host': self.host,
            'auth': self.auth,
            'method': method,
            'params': params
        })
        try:
            self.queue.put(body, priority=PRIORITIES[method])
        except beanstalkc.SocketError:
            self.connect()
            self.queue.put(body, priority=PRIORITIES[method])


def set_timestamp(*objects):
    # todo: if 'created' already exist need to ensure it's timezone aware
    now = timestamp.now()
    for obj in objects:
        obj.setdefault('created', now.isoformat())


class DebugPublisher(object):
    '''
    DebugPublisher implements the same interface of Publisher() but doesn't talk
    to beanstalkd, just saves debug information of all method calls to a file

    '''

    FILEPATH = '/tmp/leadrouter-queue.txt'

    def __init__(self, *args, **kwargs):
        self.filepath = kwargs.get('filepath', self.FILEPATH)
        self._record(self._new_section(), '__init__()')

    def connect(self):
        self._record('connect()')

    def close(self):
        self._record('close()')

    def create_lead(self, site_uuid, lead):
        self._record('create_lead("{0}", {1})'.format(site_uuid, repr(lead)))

    def update_lead(self, site_uuid, lead_uuid, lead):
        self._record('update_lead("{0}", "{1}", {2})'.format(site_uuid, lead_uuid, repr(lead)))

    def add_activities(self, site_uuid, lead_uuid, activities):
        self._record('add_activities("{0}", "{1}", {2})'.format(site_uuid, lead_uuid, repr(activities)))

    def create_potential_seller_lead(self, site_uuid, lead):
        self._record('create_potential_seller_lead("{0}", {1})'.format(site_uuid, repr(lead)))

    def _new_section(self):
        return ('-------------------' +
                datetime.datetime.utcnow().strftime('%a, %e %b %Y %H:%M:%S %z') +
                '-------------------')

    def _record(self, *lines):
        with open(self.filepath, 'a') as fobj:
            for line in lines:
                fobj.write(line + '\n')
