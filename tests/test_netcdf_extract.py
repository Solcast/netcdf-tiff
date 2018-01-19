import pytest

from src.metadata.goes16_filename_metadata import Goes16FileNameMetadata

@pytest.mark.parametrize(
    ('input_filename', 'channel'),
    [
        (
                'or_abi-l2-cmipf-m3c13_g16_s20180100515410_e20180100526189_c20180100526268.nc',
                13
        ),
        (
                'OR_ABI-l2-CMIPF-M3C13_G16_S20180100515410_E20180100526189_C20180100526268.NC',
                13
        )
    ]
)
def test_goes16_metadata(input_filename, channel):
    file_metadata = Goes16FileNameMetadata.parse(input_filename)
    assert (int(file_metadata.sensor.channel), channel)
