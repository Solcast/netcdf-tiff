import numpy as np

class GeoTIFF_Options:

    output_file = ""
    data = np.array()
    gdal_type = np.uint8
    transform = None
    projection = None
    empty = None

    def __init__(self, *args, **kwargs):
        """

        :rtype: object
        """
        self.transform = None
        self.input_file = ""
        self.netcdf_details = None
        self.output_file = ""

        if 'input_file' in kwargs:
            self.input_file = kwargs.get('input_file')
        if 'netcdf_details' in kwargs:
            self.netcdf_details = kwargs.get('netcdf_details')
        if 'output_file' in kwargs:
            self.output_file = kwargs.get('output_file')
        if 'transform' in kwargs:
            self.transform = kwargs.get('transform')