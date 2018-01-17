# http://schubert.atmos.colostate.edu/~cslocum/code/netcdf_example.py

import os

class NetCDF_Info:

    def info(nc_file):
        # NetCDF global attributes
        nc_attrs = nc_file.ncattrs()
        # Variable information.
        nc_vars = [var for var in nc_file.variables]  # list of nc variables
        nc_dims = [dim for dim in nc_file.dimensions]  # list of nc dimensions
        return nc_attrs, nc_dims, nc_vars


    def dump(nc_file, logfile="nc_dump.log"):
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

        nc_attrs, nc_dims, nc_vars = NetCDF_Info.info(nc_file)

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
            print('\t%s:' % nc_attr, repr(nc_file.getncattr(nc_attr)), file=logfile)

        # Dimension shape information.
        print("NetCDF dimension information:", file=logfile)
        for dim in nc_dims:
            print("\tName:", dim, file=logfile)
            print("\t\tsize:", len(nc_file.dimensions[dim]), file=logfile)
            _print_attr(nc_file, dim, logfile)

        print("NetCDF variable information:", file=logfile)
        for var in nc_vars:
            if var not in nc_dims:
                print('\tName:', var, file=logfile)
                print("\t\tdimensions:", nc_file.variables[var].dimensions, file=logfile)
                print("\t\tsize:", nc_file.variables[var].size, file=logfile)
                _print_attr(nc_file, var, logfile)
        return nc_attrs, nc_dims, nc_vars