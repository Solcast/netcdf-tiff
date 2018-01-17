import os
import netCDF4
import numpy as np
from osgeo import gdal, gdal_array, osr
import netcdf_info

from goesr_file_metadata import GoesrFileMetadata


def _cmip_to_solrad(values, channel):
    """
    Converts GOES-R16 CMIP (cloud and moisture product) netCDF values into
    the solrad geotiff scale. These are always on a uint8 scale (0 - 255).
    For reflective channels, this is 0: 0% reflectance, 255: 100% reflectance.
    For emissive channels, this is the inverse of the solrad IRCT formula
    (https://gitlab.com/solcast/solcast-alpha/blob/04da0b0c0d04577b5309b5f9ab6ff0c2f843dfeb/src/matlab/cloud-advection/computeCloudLayersFromSatImagery.m#L21)
    i.e. `uint8_value = -1 * (degreesC - 55) / 0.4870`, e.g. 0: 55 degC, 255: -70 degC

    Parameters
    ----------
    values: numpy.ma.MaskedArray
        values to convert, with a mask
    channel: int

    Returns
    -------
        numpy.ndarray: `values` converted to uint8, with all masked
            values set to 0
    """

    bit_depth = np.uint8
    data_desc = np.iinfo(bit_depth)

    # reflective channels, values are reflectances in [0, 1]
    if channel == 2:
        converted = values * data_desc.max
    # emmisive channels, values are brightness temperatures in Kelvin
    elif channel in [7, 13]:
        # inverse of solrad IRCT formula (values in Celcius)
        converted = -1 * ((values - 273.15) - 55) / 0.4870
    else:
        raise ValueError("Unconfigured channel: {0}".format(channel))

    # Replace designated fill value with 0 for nice GDAL TIFF conversion
    converted[values.mask] = 0

    # convert to uint8 (will overflow if not capped)
    converted = np.round(converted)
    converted = converted.clip(min=data_desc.min, max=data_desc.max)
    converted = converted.astype(bit_depth)

    return converted


class NetCDFReader:

    def __init__(self, debug=False, verbose=False):
        self.verbose = verbose
        self.debug = debug

    def npmatrix_to_geotiff (self, filepath, array, gdal_type, transform = None, projection = None, nodata = None):
        (y_res, x_res) = array.shape
        driver = gdal.GetDriverByName('GTiff')
        image = driver.Create(filepath, x_res, y_res, eType=gdal_type)

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

    def extract_netcdf_image(self, source_netcdf, dtype, metadata=None):
        # get netcdf metadata from filename
        if metadata is None:
            metadata = GoesrFileMetadata.parse(os.path.basename(source_netcdf))
        product = metadata.sensor_desc.product
        channel = int(metadata.sensor_desc.channel)

        # sanistisation for hard-coded assumptions
        if dtype != np.uint8:
            raise ValueError("Unsupported dtype {0}, must be np.uint8".format(dtype))
        if product != 'CMIP':
            raise ValueError("Unsupported product: \"{0}\", must be \"CMIP\"".format(product))

        # load netCDF values into memory
        nc = netCDF4.Dataset(source_netcdf, 'r')
        if self.debug:
            logfile = "{0}.log".format(source_netcdf)
            if os.path.exists(logfile):
                if self.verbose:
                    print("Deleting log file {0}".format(logfile))
                os.remove(logfile)
            netcdf_info.ncdump(nc, logfile)
        # automatically scale to meaningful units and compute mask
        # uses 'scale_factor', 'add_offset' and '_FillValue'
        nc.set_auto_maskandscale(True)
        values = nc.variables['CMI'][:]  # a numpy.ma.MaskedArray
        nc.close()

        return _cmip_to_solrad(values, channel)

    def netcdf_to_geotiff(self, options):
        extracted_data = self.extract_netcdf_image(options.input_file, options.transform.data_type, options.netcdf_details)
        image_data = np.flip(np.matrix(extracted_data), 0) # GOESR images are inverted for reprojection

        projection = osr.SpatialReference()
        projection.ImportFromProj4('+proj=geos +lon_0=-75 +h=35786023.0 +a=6378137.0 +b=6356752.31414 +units=m +sweep=x +no_defs')
        tiff_data = self.npmatrix_to_geotiff(
            options.output_file,
            image_data,
            gdal_array.NumericTypeCodeToGDALTypeCode(options.transform.data_type),
            options.transform.extents,
            projection.ExportToWkt(),
            None
        )
        return options.output_file
