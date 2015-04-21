import datetime

try:
    import pytz
except ImportError:
    pytz = None

class UTC(datetime.tzinfo):
    '''
    UTC implementation taken from Python's docs.

    Used only when pytz isn't available.
    '''

    def __repr__(self):
        return '<UTC>'

    def utcoffset(self, dt):
        return datetime.timedelta(0)

    def tzname(self, dt):
        return 'UTC'

    def dst(self, dt):
        return datetime.timedelta(0)

utc = pytz.utc if pytz else UTC()

def now():
    return datetime.datetime.utcnow().replace(tzinfo=utc)
