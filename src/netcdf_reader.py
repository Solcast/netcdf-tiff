import os

import netCDF4

import src.util.type_helper as th


class NetCDFReader:

    @staticmethod
    def info(netcdf_data):

        # NetCDF global attributes
        nc_attrs = netcdf_data.ncattrs()
        # Variable information.
        nc_vars = [var for var in netcdf_data.variables]  # list of nc variables
        nc_dims = [dim for dim in netcdf_data.dimensions]  # list of nc dimensions
        return nc_attrs, nc_dims, nc_vars

    @staticmethod
    def dump(netcdf_data, logfile="nc_dump.log"):
        '''
        ncdump outputs dimensions, variables and their attribute information.
        The information is similar to that of NCAR's ncdump utility.
        ncdump requires a valid instance of Dataset.

        Parameters
        ----------
        nc_file : netCDF4.Dataset
            A netCDF4 dateset object
        verb : Boolean
            whether or not nc_attrs, nc_dims, and nc_vars are printed

        Returns
        -------
        nc_attrs : list
            A Python list of the NetCDF file global attributes
        nc_dims : list
            A Python list of the NetCDF file dimensions
        nc_vars : list
            A Python list of the NetCDF file variables
        '''

        nc_attrs, nc_dims, nc_vars = NetCDFReader.info(netcdf_data)

        if os.path.exist(logfile):
            os.remove(logfile)

        logfile = open(logfile, 'w')

        def _print_attr(nc_file, key, logfile):
            """
            Prints the NetCDF file attributes for a given key

            Parameters
            ----------
            key : unicode
                a valid netCDF4.Dataset.variables key
            """
            try:
                print("\t\ttype:", repr(nc_file.variables[key].dtype), file=logfile)
                for ncattr in nc_file.variables[key].ncattrs():
                    print('\t\t%s:' % ncattr, repr(nc_file.variables[key].getncattr(ncattr)), file=logfile)
            except KeyError:
                print("\t\tWARNING: %s does not contain variable attributes" % key, file=logfile)

        print("NetCDF Global Attributes:", file=logfile)
        for nc_attr in nc_attrs:
            print('\t%s:' % nc_attr, repr(netcdf_data.getncattr(nc_attr)), file=logfile)

        # Dimension shape information.
        print("NetCDF dimension information:", file=logfile)
        for dim in nc_dims:
            print("\tName:", dim, file=logfile)
            print("\t\tsize:", len(netcdf_data.dimensions[dim]), file=logfile)
            _print_attr(netcdf_data, dim, logfile)

        print("NetCDF variable information:", file=logfile)
        for var in nc_vars:
            if var not in nc_dims:
                print('\tName:', var, file=logfile)
                print("\t\tdimensions:", netcdf_data.variables[var].dimensions, file=logfile)
                print("\t\tsize:", netcdf_data.variables[var].size, file=logfile)
                _print_attr(netcdf_data, var, logfile)
        return nc_attrs, nc_dims, nc_vars

    def __init__(self, *args, **kwargs):
        self.verbose = False
        self.debug = False

        if 'netcdf_file' in kwargs:
            filename = kwargs.get('netcdf_file')
            if os.path.exists(filename):
                self.netcdf_file = filename
        if 'verbose' in kwargs:
            value = kwargs.get('verbose')
            th.validate(name_of_value='verbose', value_to_check=value, d_type=bool)
            self.verbose = value
        if 'debug' in kwargs:
            value = kwargs.get('debug')
            th.validate(name_of_value='debug', value_to_check=value, d_type=bool)
            self.debug = value

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
        """
        Lots of details here
        http://edc.occ-data.org/goes16/python/#reading-in-goes-16-netcdf
        https://github.com/occ-data/goes16-jupyter
        """
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

    def variable_exists(self, variable_name) -> bool:
        nc = netCDF4.Dataset(self.netcdf_file, 'r')
        all_variables = [var for var in nc.variables]  # list of nc variables
        found_keys = [i for i, x in enumerate(all_variables) if x == variable_name]
        nc.close()
        if len(found_keys) == 0:
            return False
        return True

    def variable_projection(self, variable_name, grid_key="grid_mapping") -> dict:
        attrib_dict = self.variable_attributes_dict(variable_name)
        if not grid_key in attrib_dict:
            return None
        projection_dict = self.variable_attributes_dict(attrib_dict[grid_key])
        return projection_dict

    def variable_attributes_dict(self, variable_name) -> dict:
        results = {}
        if not self.variable_exists(variable_name):
            return results

        nc = netCDF4.Dataset(self.netcdf_file, 'r')
        for attrib_name in nc.variables[variable_name].ncattrs():
            attrib_value = nc.variables[variable_name].getncattr(attrib_name)
            results[attrib_name] = attrib_value
        nc.close()
        return results
