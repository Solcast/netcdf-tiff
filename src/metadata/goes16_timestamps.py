import datetime
import pytz

import src.util.type_helper as th


class Goes16TimeStamps:

    @staticmethod
    def parse_timestamp(text_timestamp) -> datetime:
        """

        :rtype: datetime
        """
        time_split = text_timestamp.split(".")[0]
        full_time = time_split[1:]
        year = int(full_time[:4])
        day_of_year = int(full_time[4:7]) - 1
        hour = int(full_time[7:9])
        minute = int(full_time[9:11])
        second = int(full_time[11:13])
        millisecond = int(full_time[13:14]) * 100

        the_date = datetime.datetime(year, 1, 1, tzinfo=pytz.UTC)
        delta = datetime.timedelta(days=day_of_year, hours=hour, minutes=minute, seconds=second,
                                   milliseconds=millisecond)
        the_date = the_date + delta
        return the_date

    @staticmethod
    def parse(start_scan, end_scan, created):
        """

        :rtype: Goes16TimeStamps
        """
        clone = Goes16TimeStamps()
        clone.start_scan = Goes16TimeStamps.parse_timestamp(start_scan)
        clone.end_scan = Goes16TimeStamps.parse_timestamp(end_scan)
        clone.created = Goes16TimeStamps.parse_timestamp(created)
        return clone

    def __init__(self, *args, **kwargs):
        self.start_scan = None
        self.end_scan = None
        self.created = None
        self.verbose = False
        self.debug = False

        if 'start_scan' in kwargs:
            value = kwargs.get('start_scan')
            th.validate(name_of_value='start_scan', value_to_check=value, d_type=datetime)
            self.start_scan = value
        if 'created' in kwargs:
            value = kwargs.get('created')
            th.validate(name_of_value='created', value_to_check=value, d_type=datetime)
            self.created = value
        if 'end_scan' in kwargs:
            value = kwargs.get('end_scan')
            th.validate(name_of_value='end_scan', value_to_check=value, d_type=datetime)
            self.end_scan = value
        if 'verbose' in kwargs:
            value = kwargs.get('verbose')
            th.validate(name_of_value='verbose', value_to_check=value, d_type=bool)
            self.verbose = value
        if 'debug' in kwargs:
            value = kwargs.get('debug')
            th.validate(name_of_value='debug', value_to_check=value, d_type=bool)
            self.debug = value
