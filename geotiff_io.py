from osgeo import gdal

class GeoTIFF_IO:
    verbose = False
    debug = False

    def __init__(self, *args, **kwargs):
        if 'verbose' in kwargs:
            self.verbose = kwargs.get('verbose')
        if 'debug' in kwargs:
            self.debug = kwargs.get('debug')

    def _to_geotiff(self, output_file, array, gdal_type, transform=None, projection=None, nodata=None):
        (y_res, x_res) = array.shape
        driver = gdal.GetDriverByName('GTiff')
        image = driver.Create(output_file, x_res, y_res, eType=gdal_type)

        if transform is not None:
            image.SetGeoTransform(transform)
        if projection is not None:
            image.SetProjection(projection)
        band = image.GetRasterBand(1)
        if nodata is not None:
            band.SetNoDataValue(nodata)
        band.WriteArray(array)
        band.FlushCache()
        return image

    def extract(self, options, converter):
        data = converter.extract(options)
        self._to_geotiff(options.output_file, data, converter.)
        tiff_file = converter.extract(options)
        return tiff_file