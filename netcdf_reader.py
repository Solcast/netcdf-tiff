import netCDF4
import os

class NetCDFReader:

    def __init__(self, *args, **kwargs):
        self.verbose = False
        self.debug = False

        if 'netcdf_file' in kwargs:
            filename = kwargs.get('netcdf_file')
            if os.path.exists(filename):
                self.netcdf_file = filename
        if 'verbose' in kwargs:
            self.verbose = kwargs.get('verbose')
        if 'debug' in kwargs:
            self.debug = kwargs.get('debug')

    def global_attribute(self, variable_name):
        if os.path.exists(self.netcdf_file) is False:
            return None
        nc = netCDF4.Dataset(self.netcdf_file, 'r')
        found_keys = [i for i, x in enumerate(nc.ncattrs()) if x == variable_name]
        if len(found_keys) == 0:
            nc.close()
            return
        resolution = nc.getncattr(variable_name)
        nc.close()
        return resolution

    def read(self, variable_name):
        if os.path.exists(self.netcdf_file) is False or self.variable_exists(variable_name) is False:
            return None
        # load netCDF values into memory
        nc = netCDF4.Dataset(self.netcdf_file, 'r')
        # automatically scale to meaningful units and compute mask
        # uses 'scale_factor', 'add_offset' and '_FillValue'
        nc.set_auto_maskandscale(True)
        extracted_data = nc.variables[variable_name][:]  # a numpy.ma.MaskedArray
        nc.close()
        return extracted_data

    def variable_exists(self, extract_key):
        nc = netCDF4.Dataset(self.netcdf_file, 'r')
        all_variables = [var for var in nc.variables]  # list of nc variables
        found_keys = [i for i, x in enumerate(all_variables) if x == extract_key]
        nc.close()
        if len(found_keys) == 0:
            return False
        return True

    def variable_projection(self, extract_key, grid_key="grid_mapping"):
        attrib_dict = self.variable_attributes_dict(extract_key)
        if not grid_key in attrib_dict:
            return None
        projection_dict = self.variable_attributes_dict(attrib_dict[grid_key])
        return projection_dict

    def variable_attributes_dict(self, extract_key):
        results = {}
        if not self.variable_exists(extract_key):
            return results

        nc = netCDF4.Dataset(self.netcdf_file, 'r')
        for attrib_name in nc.variables[extract_key].ncattrs():
            attrib_value = nc.variables[extract_key].getncattr(attrib_name)
            results[attrib_name] = attrib_value
        nc.close()
        return results
