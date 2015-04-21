import json  # todo: instal ujson
from collections import namedtuple

import beanstalkc

from . import client
from .alerts import NullAlerts

RETRY_DELAY = 30  # (seconds) delay between retries of the same job

class Subscriber(object):

    def __init__(self, host='localhost', port=11300, tube='leadrouter', alerts=None):
        self.host, self.port = host, port
        self.tube = tube
        self.queue = None
        self.alerts = alerts or NullAlerts()

    def connect(self):
        self.queue = beanstalkc.Connection(self.host, self.port)
        self.queue.watch(self.tube)
        self.queue.ignore('default')
        self.alerts.info('Connected to beanstalkd {0}:{1} watching tube {2}'.format(
                         self.host, self.port, ','.join(self.queue.watching())))

    def close(self):
        if self.queue:
            self.queue.close()
            self.queue = None

    def consume(self):
        '''Consume will block forever reading jobs from beanstalkd tube,
        parsing it and making the request specified in it

        Some failures will trigger a retry, in this case the job will
        go back to the tube.

        On success and unrecoverable errors job will be deleted from tube
        '''
        if not self.queue:
            self.connect()
        while 1:
            job = self.queue.reserve()
            self.handle(job)

    def handle(self, job):
        package, err = self.parse(job)
        if err:
            job.delete()
            self.alerts.critical('invalid job: '+err, {'job_body': job.body})
            return
        result = make_request(package)
        if result.error:
            self.alerts.critical(result.error, {
                'parsed_job_body': package,
                'job_id': job.jid,
                'response_status': result.response_status,
                'response_body': result.response_body,
                'retry': result.retry,
            })
            if result.retry:
                job.release(delay=RETRY_DELAY)
                return
        else:
            self.alerts.debug('job processed', package)
        job.delete()

    def parse(self, job):
        try:
            return json.loads(job.body), ''
        except ValueError as ex:
            return {}, str(ex)


# List of HTTP status code lead_router api could return that will make
# us NOT retry the request
STATUS_NO_RETRY = (
    # Unauthorized, the credentials in the package published into beanstalkd
    # are invalid or don't have enough permissions
    401,

    # Bad Request, the JSON object sent is invalid, very rare because it would
    # mean the Client didn't know how to send the request
    400,

    # Unprocessable Entity, the Lead or Activity sent didn't validate, like missing
    # a required field.
    422,
)

RequestResult = namedtuple('RequestResult', (
    'success',        # boolean indicating if the request was successful
    'retry',          # boolean indicating if called MUST retry the request
    'error',          # error message string, if success is False
    'response_body',  # full response body when success is False, if available
    'response_status',# status code of response, if available
))

def make_request(package):
    '''Given a package from beanstalkd tube perform the request to lead_router

    Return a ProcessResult with information about what happened
    '''
    method, params = build_client(package)
    try:
        method(**params)
    except client.HTTPError as ex:
        if ex.status_code in STATUS_NO_RETRY:
            return RequestResult(success=False, retry=False,
                                 error='send failed: ' + str(ex),
                                 response_body=ex.response_text,
                                 response_status=ex.status_code)
        return RequestResult(success=False, retry=True,
                             error='send failed (RETRYING): ' + str(ex),
                             response_body=ex.response_text,
                             response_status=ex.status_code)
    except Exception as ex:
        return RequestResult(success=False, retry=False,
                             error='send failed: ' + str(ex),
                             response_body='', response_status=None)
    return RequestResult(success=True, retry=False, error='',
                         response_body='', response_status=None)

def build_client(package):
    '''Build a client.Client given the package from beanstalkd tube and return
    one of it's methods as specified by package

    The package has all information we need to make the request, including
    which method to call on a Client object and credentials to use
    '''
    cli = client.Client(package['host'], *package['auth'])
    method = getattr(cli, package['method'])
    return method, package['params']
