
import pprint

class Alerts(object):
    '''Alerts is an interface to both a standard python logger and pagerduty

    TODO: integrate with pagerduty
    '''

    def __init__(self, logger):
        self.logger = logger

    def info(self, msg):
        '''Send notification message as INFO to logger'''
        self.logger.info(msg)

    def critical(self, msg, details={}):
        '''Send ERROR message to logger, pretty printing the details and send
        notification to pagerduty
        '''
        s = msg
        if details:
            s += '\n'
            s += pprint.pformat(details)
        self.logger.error(s)


class NullAlerts(object):
    def info(self, msg):
        pass

    def critical(self, msg, details={}):
        pass
