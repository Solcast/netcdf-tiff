import os

class ConversionOptions:


    def __str__(self):
        return "Input: {0}\nOutput: {1}\nVerbose: {2}\nDebug: {3}".format(self.input_file, self.output_file, self.verbose, self.debug)

    def __init__(self, *args, **kwargs):
        self.verbose = False
        self.debug = False
        self.input_file = ""
        self.output_file = ""

        if 'verbose' in kwargs:
            self.verbose = kwargs.get('verbose')
        if 'debug' in kwargs:
            self.debug = kwargs.get('debug')
        if 'output' in kwargs:
            self.output = kwargs.get('output')
        if 'filename' in kwargs:
            filename = kwargs.get('filename')
            if len(filename) > 0 and os.path.exists(filename):
                self.input_file = filename
                if self.output_file == "":
                    self.output_file = "{0}.tiff".format(self.input_file)