import numpy as np

import src.util.type_helper as th


class GoesTransform:
    @staticmethod
    def all_channels() -> dict:
        channel_dict = {
            1: GoesLevel(extents=GoesResolution.one_km()),
            2: GoesLevel(extents=GoesResolution.half_km()),
            3: GoesLevel(extents=GoesResolution.one_km()),
            4: GoesLevel(extents=GoesResolution.two_km()),
            5: GoesLevel(extents=GoesResolution.one_km()),
            6: GoesLevel(extents=GoesResolution.two_km()),
            7: GoesLevel(extents=GoesResolution.two_km()),
            8: GoesLevel(extents=GoesResolution.two_km()),
            9: GoesLevel(extents=GoesResolution.two_km()),
            10: GoesLevel(extents=GoesResolution.two_km()),
            11: GoesLevel(extents=GoesResolution.two_km()),
            12: GoesLevel(extents=GoesResolution.two_km()),
            13: GoesLevel(extents=GoesResolution.two_km()),
            14: GoesLevel(extents=GoesResolution.two_km()),
            15: GoesLevel(extents=GoesResolution.two_km()),
            16: GoesLevel(extents=GoesResolution.two_km())
        }
        return channel_dict

    @staticmethod
    def channel(channel_number):
        number = int(channel_number)
        if number < 1 or number > 16:
            raise ValueError("{0} is not within valid channel range 1 - 16".format(channel_number))
        match = GoesTransform.all_channels().get(number)
        return match


class GoesLevel(object):
    def __init__(self, *args, **kwargs):
        self.verbose = False
        self.debug = False
        self.data_type = np.uint8
        self.extents = GoesResolution.two_km()

        if 'data_type' in kwargs:
            self.data_type = kwargs.get('data_type')
        if 'extents' in kwargs:
            self.extents = kwargs.get('extents')
        if 'verbose' in kwargs:
            value = kwargs.get('verbose')
            th.validate(name_of_value='verbose', value_to_check=value, d_type=bool)
            self.verbose = value
        if 'debug' in kwargs:
            value = kwargs.get('debug')
            th.validate(name_of_value='debug', value_to_check=value, d_type=bool)
            self.debug = value


class GoesResolution:

    @staticmethod
    def extents_for_meters(meters=2000) -> tuple:
        if meters == 500:
            return GoesResolution.half_km()
        if meters == 1000:
            return GoesResolution.one_km()
        return GoesResolution.two_km()

    @staticmethod
    def half_km() -> tuple:
        return (-5434895.081637931, 501.0043288718853, 0, -5434894.837566491, 0, 501.0043288718853)

    @staticmethod
    def one_km() -> tuple:
        return (-5434894.954752678, 1002.0086577437705, 0, -5434894.964451744, 0, 1002.0086577437705)

    @staticmethod
    def two_km() -> tuple:
        return (-5434894.700982173, 2004.0173154875410, 0, -5434895.218222249, 0, 2004.0173154875410)
