import os
import json
import datetime
from time import mktime

class GameOnUtils(object):
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'

    @classmethod
    def json_serializer(cls, obj):
        import calendar, datetime
        if isinstance(obj, datetime.datetime):
            if obj.utcoffset() is not None:
                obj = obj - obj.utcoffset()
        millis = int(
            calendar.timegm(obj.timetuple()) * 1000 +
            obj.microsecond / 1000
        )
        return millis

    class MyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime.datetime):
                return int(mktime(obj.timetuple()))
            if hasattr(obj, '__dict__'):
                return obj.__dict__
            return json.JSONEncoder.default(self, obj)
