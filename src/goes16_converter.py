import numpy as np
import osgeo

from src.converters import Converters
from src.geotiff_options import GeoTIFF_Options
from src.metadata.goes16_filename_metadata import Goes16FileNameMetadata
from src.netcdf_reader import NetCDFReader
from src.transforms import GoesResolution


class Goes16Converter(Converters):

    def _extract_projection(self, options, variable_name):
        netcdf_file = NetCDFReader(netcdf_file=options.input_file, debug=self.debug, verbose=self.verbose)
        attribs = netcdf_file.variable_projection(variable_name)

        projection = osgeo.osr.SpatialReference()

        # GOES 16 seems to not be in data projection of -75 but instead -75.2
        origin_longitude = attribs['longitude_of_projection_origin']
        if float(origin_longitude) == float(-75):
            origin_longitude = -75.2

        params = ["+proj={0}".format(attribs['long_name'].replace(' ', '_')),
                  "+lon_0={0}".format(origin_longitude),
                  "+h={0}".format(attribs['perspective_point_height']), "+a={0}".format(attribs['semi_major_axis']),
                  "+b={0}".format(attribs['semi_minor_axis']), "+units={0}".format('m'),
                  "+sweep={0}".format(attribs['sweep_angle_axis']), "+nodefs"]
        projection.ImportFromProj4(" ".join(params))
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
        scaled_data = self._cmip_to_visible(data_values=extracted_data,
                                            channel=int(
                                                Goes16FileNameMetadata.parse(options.input_file).sensor.channel))
        image_data = np.flip(np.matrix(scaled_data), 0)  # GOESR images are inverted for reprojection
        return image_data

    def _to_geotiff(self, options):
        (y_res, x_res) = options.data.shape
        driver = osgeo.gdal.GetDriverByName('GTiff')
        data_type = osgeo.gdal_array.NumericTypeCodeToGDALTypeCode(options.gdal_type)
        image = driver.Create(options.output_file, x_res, y_res, eType=data_type)

        if options.extents is not None:
            image.SetGeoTransform(options.extents)
        if options.projection is not None:
            image.SetProjection(options.projection.ExportToWkt())
        band = image.GetRasterBand(1)
        if options.empty is not None:
            band.SetNoDataValue(options.empty)
        band.WriteArray(options.data)
        band.FlushCache()
        return image

    def _get_transform(self, options, global_variable_name="spatial_resolution"):
        netcdf_file = NetCDFReader(netcdf_file=options.input_file, debug=self.debug, verbose=self.verbose)
        resolution = netcdf_file.global_attribute(global_variable_name)
        if resolution is None:
            return GoesResolution.two_km()

        resolution_in_meters = int(float(resolution.upper().split("km".upper())[0]) * 1000)
        return GoesResolution.extents_for_meters(resolution_in_meters)

    def _gdal_warp(self, options, tiff_file,
                   projection="+proj=geos +lon_0=-75.2 +h=35786023 +x_0=0 +y_0=0 +ellps=GRS80 +units=m +no_defs"):
        world_latlng_tiff = "{0}_world.tiff".format(options.input_file)
        reproject = osgeo.gdal.Open(tiff_file)
        reproject = osgeo.gdal.Warp(world_latlng_tiff, reproject, format="GTiff",
                                    srcSRS=projection,
                                    dstSRS="EPSG:4326", resampleAlg=osgeo.gdal.GRIORA_Bilinear)
        reproject = None
        return world_latlng_tiff

    #  https://www.linkedin.com/pulse/convert-netcdf4-file-geotiff-using-python-chonghua-yin
    def _gdal_extraction(self, options, variable_name):
        netcdf_name = "NETCDF:{0}:{1}".format(options.input_file, variable_name)
        world_tiff_file = "{0}.tiff".format(options.input_file)
        net_cdf_data = osgeo.gdal.Open(netcdf_name)
        net_cdf_data = osgeo.gdal.Translate(world_tiff_file, net_cdf_data)
        projection = osgeo.osr.SpatialReference()
        projection.ImportFromWkt(net_cdf_data.GetProjectionRef())
        net_cdf_data = None
        return projection

    def extract(self, options, variable_name="CMI"):
        tiff_options = GeoTIFF_Options(output_file=options.output_file,
                                       data=self._extract_netcdf_image(options, variable_name),
                                       projection=self._extract_projection(options, variable_name),
                                       extents=self._get_transform(options))
        tiff_data = self._to_geotiff(tiff_options)
        return tiff_data
