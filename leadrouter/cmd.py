'''
Command line interface
'''
import logging
import time
import json
import pprint
import sys

import click
import beanstalkc

from leadrouter.subscriber import Subscriber, make_request
from leadrouter.alerts import Alerts


@click.group()
def cmd():
    '''Command line interface for the lead router client'''

@cmd.command()
@click.option('--beanstalkd-host', default='127.0.0.1', help='Default to 127.0.0.1')
@click.option('--beanstalkd-port', default=11300, help='Default to 11300')
@click.option('--beanstalkd-tube', default='leadrouter', help='Default to "leadrouter"')
@click.option('--loglevel', default='debug', type=click.Choice(['critical', 'error', 'warning', 'info', 'debug']))
def subscriber(beanstalkd_host, beanstalkd_port, beanstalkd_tube, loglevel):
    '''Read jobs from beanstalkd tube and send the requests to lead_router'''
    alerts = Alerts(build_logger(loglevel))
    while 1:
        try:
            sub = Subscriber(beanstalkd_host, beanstalkd_port, beanstalkd_tube, alerts=alerts)
            sub.consume()
        except beanstalkc.SocketError:
            click.echo('Failed to connect to beanstalkd. Retrying in 5s', err=True)
            time.sleep(5)


@cmd.command()
@click.argument('job', type=click.File('r'))
@click.option('-v/--verbose', default=False, help="More verbose output")
@click.option('-f/--force', default=False, help="Send job even if it's marked as retry")
def send(job, v, f):
    '''Send a single beanstalkd job to lead_router

    To send from a file:

        $ leadrouter send job.json

    To send from stdin

        $ cat job.json | leadrouter send -

    It does not interact with beanstalkd, this could be used to resend failed
    jobs you see in the log file.
    '''
    job = job.read()
    job = json.loads(job)

    if v:
        click.echo("~> Parsed job:\n%s" % pprint.pformat(job))

    # if the 'job' given is the 'details' we send to alerts package when something
    # goes wrong, it will have a 'retry' key and the actual job will be in key
    # 'parsed_job_body'

    if job.get('retry') and not f:
        click.echo("\n~> WARNING The job is marked as retry, that means 'leadrouter "
                   "subscriber' will retry to send it.  If you send manually you "
                   "might end up with duplicate information.  To send anyway use --force\n",
                   err=True)
        sys.exit(1)

    if 'parsed_job_body' in job:
        job = job['parsed_job_body']

    result = make_request(job)

    if not result.success:
        click.echo("~> Error: %s" % result.error, err=True)
        if result.response_status:
            click.echo("~> Lead Router Response status: %s" % result.response_status, err=True)
        if result.response_body:
            click.echo("~> Lead Router Response body: '%s'" % result.response_body, err=True)
        if result.traceback:
            click.echo("~> Exception handled:\n%s" % result.traceback, err=True)
        sys.exit(1)

    click.echo("~> Success")


def build_logger(level):
    level = getattr(logging, level.upper())
    logger = logging.getLogger('leadrouter-subscriber')
    logger.setLevel(level)
    handler = logging.StreamHandler()
    handler.setLevel(level)
    fmt = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
    handler.setFormatter(fmt)
    logger.addHandler(handler)
    return logger
