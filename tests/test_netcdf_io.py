"""
Tests goes16_io
"""
import netCDF4
import numpy as np
import pytest

from src.conversion_options import ConversionOptions
from src.goes16_converter import Goes16Converter

FILL_VALUE = 65535


@pytest.mark.parametrize(
    ('val', 'channel', 'exp_unmasked'),
    [
        # reflective channel 02
        (-1, 2, 0),
        (0, 2, 0),
        (0.005, 2, 1),
        (0.23, 2, 59),  # round up
        (0.852, 2, 217),  # round down
        (0.995, 2, 254),
        (1, 2, 255),
        (1.12, 2, 255),

        # emmissive channel 07
        (330, 7, 0),
        (328.15, 7, 0),  # 55 degC
        (327.5, 7, 1),
        (300, 7, 58),  # round up
        (270, 7, 119),  # round down
        (204.5, 7, 254),
        (203.965, 7, 255),  # -67.185 degC
        (150, 7, 255),

        # channel 13
        (300, 13, 58),
    ]
)
def test__cmip_to_solrad(val, channel, exp_unmasked):
    """
    Tests _cmip_to_solrad on single values,
    and checks that masked values are always converted to 0
    """
    # try it unmasked

    goes16 = Goes16Converter()
    unmasked = np.ma.masked_array([val], [False], fill_value=FILL_VALUE)
    out = goes16._cmip_to_visible(unmasked, channel)
    np.testing.assert_array_equal(out, exp_unmasked)
    assert out.dtype.name == 'uint8'

    # if it is masked, then should always return 0
    masked = np.ma.masked_array([val], [True], fill_value=FILL_VALUE)
    out = goes16._cmip_to_visible(masked, channel)
    np.testing.assert_array_equal(out, 0)
    assert out.dtype.name == 'uint8'


@pytest.mark.parametrize(
    ('values', 'channel', 'exp'),
    [
        (  # reflective channel 02
                np.ma.masked_array(
                    [[0.5, 0.23], [0, 1]],
                    [[True, False], [False, False]],
                    fill_value=FILL_VALUE
                ),
                2,
                np.array([[0, 59], [0, 255]])
        ),
        (  # emmissive channel 07
                np.ma.masked_array(
                    [[300, 270], [330, 200]],
                    [[False, False], [True, True]],
                    fill_value=FILL_VALUE
                ),
                7,
                np.array([[58, 119], [0, 0]])
        ),
        (  # emmissive channel 13 (as above)
                np.ma.masked_array(
                    [[300, 270], [330, 200]],
                    [[False, False], [True, True]],
                    fill_value=FILL_VALUE
                ),
                13,
                np.array([[58, 119], [0, 0]])
        ),
    ]
)
def test__cmip_to_solrad_array(values, channel, exp):
    """Tests _cmip_to_solrad produces correct array output"""
    goes16 = Goes16Converter()

    out = goes16._cmip_to_visible(values, channel)
    np.testing.assert_array_equal(out, exp)
    assert out.dtype.name == 'uint8'


# tmpdir is pytest 'magic' fixutre, will create a temporary directory
def test_extract_netcdf_image(tmpdir):
    """Tests extract_nedcdf_image can read in a netcdf and convert it to solrad"""
    # create a temporary netcdf on-disk
    nc_name = str(tmpdir.join(
        'OR_ABI-L2-CMIPF-M3C07_G16_s20173531600429_e20173531611208_c20173531611264.nc'
    ))
    test_ds = netCDF4.Dataset(nc_name, mode='w')
    test_ds.createDimension('x', size=2)
    test_ds.createDimension('y', size=3)
    # int16 with _FillValue + scale_factor + add_offset
    test_ds.createVariable('CMI', 'i2', dimensions=('y', 'x'), fill_value=65535)
    test_ds.variables['CMI'].setncattr('scale_factor', 0.0130962)
    test_ds.variables['CMI'].setncattr('add_offset', 197.31)
    test_ds.set_auto_maskandscale(False)  # allow setting int16 values directly
    test_ds.variables['CMI'][:] = [
        [8000, 65535], [4000, 65535], [65535, 500],
    ]
    test_ds.close()

    goes16 = Goes16Converter()

    options = ConversionOptions(filename=nc_name)
    out = goes16._extract_netcdf_image(options, "CMI")

    exp = np.array([[0, 255], [161, 0], [54, 0]])
    np.testing.assert_array_equal(out, exp)
    assert out.dtype.name == 'uint8'
