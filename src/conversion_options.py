import os

import src.util.type_helper as th


class ConversionOptions:

    def __str__(self):
        return "Input: {0}\nOutput: {1}\nVerbose: {2}\nDebug: {3}".format(self.input_file, self.output_file,
                                                                          self.verbose, self.debug)

    def __init__(self, *args, **kwargs):
        self.verbose = False
        self.debug = False
        self.input_file = ""
        self.output_file = ""

        if 'verbose' in kwargs:
            value = kwargs.get('verbose')
            th.validate(name_of_value='verbose', value_to_check=value, d_type=bool)
            self.verbose = value
        if 'debug' in kwargs:
            value = kwargs.get('debug')
            th.validate(name_of_value='debug', value_to_check=value, d_type=bool)
            self.debug = value
        if 'output' in kwargs:
            self.output = kwargs.get('output')
        if 'filename' in kwargs:
            filename = kwargs.get('filename')
            if len(filename) > 0 and os.path.exists(filename):
                self.input_file = filename
                if self.output_file == "":
                    self.output_file = "{0}.tiff".format(self.input_file)
