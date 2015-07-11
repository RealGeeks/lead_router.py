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
