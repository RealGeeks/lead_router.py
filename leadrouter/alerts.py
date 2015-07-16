
import pprint
import json

from leadrouter import sentry

class Alerts(object):
    '''Alerts is an interface to both a standard python logger and pagerduty

    TODO: integrate with pagerduty
    '''

    def __init__(self, logger):
        self.logger = logger

    def info(self, msg, details={}):
        '''Send INFO message to logger'''
        self.logger.info(self._format(msg, details))

    def debug(self, msg, details={}):
        '''Send DEBUG message to logger'''
        self.logger.debug(self._format(msg, details))

    def critical(self, msg, details={}):
        '''Send ERROR message to logger and send notification to pagerduty'''
        msg = self._format(msg, details)
        self.logger.error(msg)
        sentry.captureMessage(msg)

    def _format(self, msg, details):
        s = msg
        if details:
            s += '\n'
            s += details.pop('traceback', '')
            # try to render json because it's easier to reuse from other
            # systems, but fallback to python values, never lose the data
            try:
                s += json.dumps(details, indent=2)
            except (TypeError, ValueError):
                s += pprint.pformat(details)
        return s

class NullAlerts(object):
    def info(self, msg, details={}):
        pass
    def debug(self, msg, details={}):
        pass
    def critical(self, msg, details={}):
        pass
