import src.util.type_helper as th


class Goes16Sensor:

    @staticmethod
    def known_formats():
        return [
            'F',  # full disk
            'C',  # CONUS
            'M1',  # mesoscale-1
            'M2'  # mesoscale-2
        ]

    @staticmethod
    def parse(text):
        """

        :rtype: Goes16Sensor
        """

        def split_product_format(product_format_str):
            """
            Extracts the product and format from a joint product-format string,
            e.g.
                >>> split_product_format('RadF')
                ('Rad', 'F')
                >>> split_product_format('CMIPM1')
                ('CMIP', 'M1')
            """
            for fmt in Goes16Sensor.known_formats():
                if product_format_str.endswith(fmt):
                    return product_format_str[:-len(fmt)], fmt
            raise ValueError("Cannot recognise product/format in {0} known formats are {1}".format(product_format_str,
                                                                                                   Goes16Sensor.known_formats()))

        sensor_desc = text.split("-")
        clone = Goes16Sensor()
        clone.original_source = text
        clone.desc = sensor_desc[0]
        clone.level = sensor_desc[1]
        clone.product, clone.format = split_product_format(sensor_desc[2])
        clone.mode = sensor_desc[3][:2]
        clone.channel = sensor_desc[3][2:][1:]
        return clone

    def __init__(self, *args, **kwargs):

        self.desc = ""
        self.level = ""
        self.product = ""
        self.channel = ""
        self.mode = ""
        self.format = ""
        self.original_source = ""
        self.debug = False
        self.verbose = False

        if 'desc' in kwargs:
            self.desc = kwargs.get('desc')
        if 'level' in kwargs:
            self.level = kwargs.get('level')
        if 'product' in kwargs:
            self.product = kwargs.get('product')
        if 'channel' in kwargs:
            self.channel = kwargs.get('channel')
        if 'mode' in kwargs:
            self.mode = kwargs.get('mode')
        if 'format' in kwargs:
            self.format = kwargs.get('format')
        if 'original_source' in kwargs:
            self.original_source = kwargs.get('original_source')
        if 'verbose' in kwargs:
            value = kwargs.get('verbose')
            th.validate(name_of_value='verbose', value_to_check=value, d_type=bool)
            self.verbose = value
        if 'debug' in kwargs:
            value = kwargs.get('debug')
            th.validate(name_of_value='debug', value_to_check=value, d_type=bool)
            self.debug = value
