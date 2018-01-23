import os
import src.util.type_helper as th
from src.metadata.goes16_sensor import Goes16Sensor
from src.metadata.goes16_timestamps import Goes16TimeStamps


class Goes16FileNameMetadata:

    @staticmethod
    def find_timestamp_text(text, starts_with="", delimiter="_") -> str:
        if starts_with == "":
            return ""
        results = [item for item in text.split(delimiter) if item.startswith(starts_with)]
        if len(results) == 0:
            return ""
        return results[0]

    @staticmethod
    def parse(text):
        """

        :rtype: Goes16FileNameMetadata
        """
        clone = Goes16FileNameMetadata()
        if len(text) == 0:
            return clone

        upper_text = os.path.basename(text).upper();
        try:
            filename_dict = {
                "system": upper_text.split("_")[0],
                "sensor": upper_text.split("_")[1],
                "satellite": upper_text.split("_")[2],
                "start_scan": clone.find_timestamp_text(upper_text, "s".upper()),
                "end_scan": clone.find_timestamp_text(upper_text, "e".upper()),
                "created": clone.find_timestamp_text(upper_text, "c".upper())
            }
        except:
            return None

        clone.original_filename = text
        clone.system = filename_dict["system"]
        clone.satellite_id = filename_dict["satellite"]

        clone.sensor = Goes16Sensor.parse(filename_dict["sensor"])
        clone.timestamps.start_scan = Goes16TimeStamps.parse_timestamp(filename_dict["start_scan"])
        clone.timestamps.end_scan = Goes16TimeStamps.parse_timestamp(filename_dict["end_scan"])
        clone.timestamps.created = Goes16TimeStamps.parse_timestamp(filename_dict["created"])
        return clone

    def __init__(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        """
        self.original_filename = ""
        self.file_type = ""
        self.sensor = Goes16Sensor()
        self.satellite_id = ""
        self.timestamps = Goes16TimeStamps()
        self.debug = False
        self.verbose = False

        if 'original_filename' in kwargs:
            self.original_filename = kwargs.get('original_filename')
        if 'file_type' in kwargs:
            self.file_type = kwargs.get('file_type')
        if 'sensor' in kwargs:
            self.sensor = kwargs.get('sensor')
        if 'satellite_id' in kwargs:
            self.satellite_id = kwargs.get('satellite_id')
        if 'timestamps' in kwargs:
            self.timestamps = kwargs.get('timestamps')
        if 'verbose' in kwargs:
            value = kwargs.get('verbose')
            th.validate(name_of_value='verbose', value_to_check=value, d_type=bool)
            self.verbose = value
        if 'debug' in kwargs:
            value = kwargs.get('debug')
            th.validate(name_of_value='debug', value_to_check=value, d_type=bool)
            self.debug = value
