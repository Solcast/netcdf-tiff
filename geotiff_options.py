import numpy as np


class GeoTIFF_Options:
    def __init__(self, *args, **kwargs):
        """

        :rtype: object
        """
        self.output_file = ""
        self.data = np.array([])
        self.gdal_type = np.uint8
        self.extents = None
        self.projection = None
        self.empty = None

        if 'output_file' in kwargs:
            self.output_file = kwargs.get('output_file')
        if 'data' in kwargs:
            self.data = kwargs.get('data')
        if 'gdal_type' in kwargs:
            self.gdal_type = kwargs.get('gdal_type')
        if 'extents' in kwargs:
            self.extents = kwargs.get('extents')
        if 'projection' in kwargs:
            self.projection = kwargs.get('projection')
        if 'empty' in kwargs:
            self.empty = kwargs.get('empty')
