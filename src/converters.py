import src.util.type_helper as th


class Converters:
    def __init__(self, *args, **kwargs):
        self.verbose = False
        self.debug = False

        if 'verbose' in kwargs:
            value = kwargs.get('verbose')
            th.validate(name_of_value='verbose', value_to_check=value, d_type=bool)
            self.verbose = value
        if 'debug' in kwargs:
            value = kwargs.get('debug')
            th.validate(name_of_value='debug', value_to_check=value, d_type=bool)
            self.debug = kwargs.get('debug')

    def extract(self, options):
        return None
