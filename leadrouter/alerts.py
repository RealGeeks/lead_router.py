
import pprint
import json

from leadrouter import sentry

class Alerts(object):
    '''Alerts is an interface to both a standard python logger and sentry

    Only critical() messages are sent to sentry.  Make sure SENTRY_DSN environment
    variable is set (see sentry.py)

    '''

    def __init__(self, logger):
        self.logger = logger

    def info(self, msg, details={}):
        '''Send INFO message to logger'''
        self.logger.info(self._format('INFO', msg, details))

    def debug(self, msg, details={}):
        '''Send DEBUG message to logger'''
        self.logger.debug(self._format('DEBUG', msg, details))

    def warning(self, msg, details={}):
        '''Send WARNING message to logger'''
        self.logger.warning(self._format('WARNING', msg, details))

    def critical(self, msg, details={}):
        '''Send ERROR message to logger and send notification to pagerduty'''
        msg = self._format('ERROR', msg, details)
        self.logger.error(msg)
        sentry.captureMessage(msg)

    def _format(self, level, msg, details):
        data = details.copy()
        data['log_message'] = msg
        data['log_level'] = level
        try:
            return json.dumps(data)
        except (TypeError, ValueError):
            return "%s" % data

class NullAlerts(object):
    def info(self, msg, details={}):
        pass
    def debug(self, msg, details={}):
        pass
    def warning(self, msg, details={}):
        pass
    def critical(self, msg, details={}):
        pass
