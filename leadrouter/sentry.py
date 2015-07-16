'''
Sentry integration

Requires environment variable SENTRY_DSN

'''

from raven import Client

def captureMessage(message, **kwargs):
    client = Client()
    client.captureMessage(message, **kwargs)
