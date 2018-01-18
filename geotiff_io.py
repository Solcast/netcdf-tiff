from osgeo import gdal

class GeoTIFF_IO:


    def __init__(self, *args, **kwargs):
        self.verbose = False
        self.debug = False
        if 'verbose' in kwargs:
            self.verbose = kwargs.get('verbose')
        if 'debug' in kwargs:
            self.debug = kwargs.get('debug')

    def extract(self, options, converter):
        data = converter.extract(options)
        self._to_geotiff(options.output_file, data, converter.)
        tiff_file = converter.extract(options)
        return tiff_file