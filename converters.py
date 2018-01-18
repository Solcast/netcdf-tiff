class Converters:
    def __init__(self, *args, **kwargs):
        self.verbose = False
        self.debug = False

        if 'verbose' in kwargs:
            self.verbose = kwargs.get('verbose')
        if 'debug' in kwargs:
            self.debug = kwargs.get('debug')

    def extract(self, options):
        return None