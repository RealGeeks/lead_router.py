'''
Command line interface
'''
import logging
import time

import click
import beanstalkc

from leadrouter.subscriber import Subscriber
from leadrouter.alerts import Alerts


@click.group()
def cmd():
    '''Command line interface for the lead router client'''

@cmd.command()
@click.option('--beanstalkd-host', default='127.0.0.1', help='Default to 127.0.0.1')
@click.option('--beanstalkd-port', default=11300, help='Default to 11300')
@click.option('--beanstalkd-tube', default='leadrouter', help='Default to "leadrouter"')
def subscriber(beanstalkd_host, beanstalkd_port, beanstalkd_tube):
    '''Read jobs from beanstalkd tube and send the requests to lead_router'''
    alerts = Alerts(build_logger())
    while 1:
        try:
            sub = Subscriber(beanstalkd_host, beanstalkd_port, beanstalkd_tube, alerts=alerts)
            sub.consume()
        except beanstalkc.SocketError:
            click.echo('Failed to connect to beanstalkd. Retrying in 5s', err=True)
            time.sleep(5)


def build_logger():
    logger = logging.getLogger('leadrouter-subscriber')
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    fmt = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
    handler.setFormatter(fmt)
    logger.addHandler(handler)
    return logger
