import numpy as np
import osgeo
from osgeo import gdal, gdal_array, osr

from src.converters import Converters
from src.geotiff_options import GeoTIFF_Options
from src.metadata.goes16_filename_metadata import Goes16FileNameMetadata
from src.netcdf_reader import NetCDFReader
from src.transforms import GoesResolution

class Goes16Converter(Converters):

    @property
    def extents(self):
        return [-5434894.885056, -5434894.885056, 5434894.885056, 5434894.885056] # From a raw gdal conversion

    @property
    def extents_WGS84(self):
        return [-160, -80.0, 0.0, 80.0] # Reference extents

    @staticmethod
    def geo_transform(extent, y_rows, x_columns):
        # Compute resolution based on data dimension
        res_x = (extent[2] - extent[0]) / x_columns
        res_y = (extent[3] - extent[1]) / y_rows
        return [extent[0], res_x, 0, extent[3], 0, -res_y]

    def _extract_projection_def(self, options, variable_name):
        netcdf_file = NetCDFReader(netcdf_file=options.input_file, debug=self.debug, verbose=self.verbose)
        attribs = netcdf_file.variable_projection(variable_name)
        projection = osgeo.osr.SpatialReference()
        params = ["+proj=geos", # The projection name is very important this means geostationary
                  "+lon_0={0}".format(attribs['longitude_of_projection_origin']),
                  "+h={0}".format(attribs['perspective_point_height']),
                  "+a={0}".format(attribs['semi_major_axis']),
                  "+b={0}".format(attribs['semi_minor_axis']),
                  "+units={0}".format('m'),
                  "+sweep={0}".format(attribs['sweep_angle_axis']),
                  "+no_defs"]
        command_text = " ".join(params)
        projection.ImportFromProj4(command_text)
        return projection

    def _cmip_to_visible(self, data_values, channel, bit_depth=np.uint8):
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

        data_desc = np.iinfo(bit_depth)

        # reflective channels, values are reflectances in [0, 1]
        if channel == 2:
            converted = data_values * data_desc.max
        # emissive channels, values are brightness temperatures in Kelvin
        elif channel in [7, 13]:
            # inverse of custom IRCT formula (values in Celsius)
            converted = -1 * ((data_values - 273.15) - 55) / 0.4870
        else:
            # raise ValueError("Unconfigured channel: {0}".format(channel))
            converted = data_values

        # Replace designated fill value with 0 for nice GDAL TIFF conversion
        converted[data_values.mask] = 0

        # convert to uint8 (will overflow if not capped)
        converted = np.round(converted)
        converted = converted.clip(min=data_desc.min, max=data_desc.max)
        converted = converted.astype(bit_depth)

        return converted

    def _extract_netcdf_image(self, options, extract_key):
        netcdf_file = NetCDFReader(netcdf_file=options.input_file, debug=self.debug, verbose=self.verbose)
        extracted_data = netcdf_file.read(extract_key)
        filename_metadata = Goes16FileNameMetadata.parse(options.input_file)
        if filename_metadata is not None:
            channel_text = filename_metadata.sensor.channel
            scaled_data = self._cmip_to_visible(data_values=extracted_data, channel=int(channel_text))
            return scaled_data
        return extracted_data

    def _transform_extents(self, options):
        transform = options.extents
        if transform is not None:
            return transform
        (y_res, x_res) = options.data.shape
        transform = Goes16Converter.geo_transform(self.extents , y_res, x_res)
        return transform

    def _write_to_memory(self, options):
        transform = self._transform_extents(options)
        (y_res, x_res) = options.data.shape
        driver = osgeo.gdal.GetDriverByName('MEM')
        export_type = osgeo.gdal_array.NumericTypeCodeToGDALTypeCode(options.gdal_type)
        image_mem = driver.Create('grid', x_res, y_res, eType=export_type)
        projection = options.projection
        if transform is not None:
            image_mem.SetGeoTransform(transform)
        if projection is not None:
            image_mem.SetProjection(projection.ExportToWkt())
        band = image_mem.GetRasterBand(1)
        if options.empty is not None:
            band.SetNoDataValue(options.empty)
        band.WriteArray(options.data)
        band.FlushCache()
        return image_mem

    @staticmethod
    def latlng_projection():
        projection = osr.SpatialReference()
        projection.ImportFromProj4('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
        return projection


    def _to_geotiff(self, options):

        (y_res, x_res) = options.data.shape
        export_type = osgeo.gdal_array.NumericTypeCodeToGDALTypeCode(options.gdal_type)
        image_mem = self._write_to_memory(options)
        target_proj_wkt = Goes16Converter.latlng_projection().ExportToWkt()

        gtiff_driver = osgeo.gdal.GetDriverByName('GTiff')
        image = gtiff_driver.Create(options.output_file, x_res, y_res, eType=export_type)
        image.SetProjection(target_proj_wkt)
        image.SetGeoTransform(Goes16Converter.geo_transform(self.extents_WGS84, y_res, x_res))

        osgeo.gdal.ReprojectImage(image_mem,
                                  image,
                                  options.projection.ExportToWkt(),
                                  target_proj_wkt,
                                  osgeo.gdal.GRA_NearestNeighbour,
                                  options=['NUM_THREADS=ALL_CPUS'])

        raster_image_data = image.GetRasterBand(1)
        raster_image_data.FlushCache()

        return image

    def _get_transform(self, options, global_variable_name="spatial_resolution"):
        netcdf_file = NetCDFReader(netcdf_file=options.input_file, debug=self.debug, verbose=self.verbose)
        resolution = netcdf_file.global_attribute(global_variable_name)
        if resolution is None:
            return GoesResolution.two_km()

        resolution_in_meters = int(float(resolution.upper().split("km".upper())[0]) * 1000)
        return GoesResolution.extents_for_meters(resolution_in_meters)

    def extract(self, options, variable_name="CMI"):
        tiff_options = GeoTIFF_Options(output_file=options.output_file,
                                       projection=self._extract_projection_def(options, variable_name),
                                       data=self._extract_netcdf_image(options, variable_name))
        tiff_data = self._to_geotiff(tiff_options)
        return tiff_data
