import netCDF4
import numpy as np
from osgeo import gdal, gdal_array, osr
import netcdf_info
import os

class Converters:
    verbose = False
    debug = False

    def __init__(self, *args, **kwargs):
        if 'verbose' in kwargs:
            self.verbose = kwargs.get('verbose')
        if 'debug' in kwargs:
            self.debug = kwargs.get('debug')

    def extract(self, options):
        return None

class Goes16Converter(Converters):

    def _extract_projection(self, options, extract_key):
        # load netCDF values into memory
        netcdf_file = netCDF4.Dataset(options.input_file, 'r')
        netcdf_file_attrs, netcdf_file_dims, netcdf_file_vars = netcdf_info.NetCDF_Info.info(netcdf_file)
        found_keys = [i for i, x in enumerate(netcdf_file_vars) if x == extract_key]
        netcdf_file.close()
        return netcdf_file_vars

    def _nc_variable(self, netcdf_file, extract_key):
        all_variables = [var for var in netcdf_file.variables]  # list of nc variables

        found_keys =

        return None

    def _extract_netcdf_image(self, options, extract_key):
        # load netCDF values into memory
        netcdf_file = netCDF4.Dataset(options.input_file, 'r')



        # automatically scale to meaningful units and compute mask
        # uses 'scale_factor', 'add_offset' and '_FillValue'
        netcdf_file.set_auto_maskandscale(True)
        extracted_data = netcdf_file.variables[extract_key][:]  # a numpy.ma.MaskedArray
        netcdf_file.close()
        image_data = np.flip(np.matrix(extracted_data), 0)  # GOESR images are inverted for reprojection
        return image_data

    def extract(self, options, extract_key="CMI"):
        image_data = self._extract_netcdf_image(options, extract_key)
        projection = self._goes_imager_projection()

        projection = osr.SpatialReference()
        projection.ImportFromProj4('+proj=geos'
                                   '+lon_0=-75'
                                   '+h=35786023.0'
                                   '+a=6378137.0'
                                   '+b=6356752.31414'
                                   '+units=m'
                                   '+sweep=x'
                                   '+no_defs')

        tiff_data = self.npmatrix_to_geotiff(
            options.output_file,
            image_data,
            gdal_array.NumericTypeCodeToGDALTypeCode(options.transform.data_type),
            options.transform.extents,
            projection.ExportToWkt(),
            None
        )
        return options.output_file

