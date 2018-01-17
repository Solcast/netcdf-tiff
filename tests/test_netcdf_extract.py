import pytest

from goesr_file_metadata import GoesrFileMetadata
from ..s3_goesr_sync import S3GoesrConverter
from ..s3_goesr_sync_arguments import S3GoesrSyncArguments
import os


@pytest.mark.parametrize(
    ('input_filename', 'output_filename'),
    [
        (
            'or_abi-l2-cmipf-m3c13_g16_s20180100515410_e20180100526189_c20180100526268.nc',
            'ABI - L2 - CMIPF_13_201801100515.nc'
        ),
        (
                'OR_ABI-l2-CMIPF-M3C13_G16_S20180100515410_E20180100526189_C20180100526268.NC',
                'ABI - L2 - CMIPF_13_201801100515.nc'
        )
    ]
)
def test_goesr_metadata(input_filename, output_filename):
    s3sync = S3GoesrConverter(verbose=True, debug=True)
    command_args = S3GoesrSyncArguments(verbose=True,
                                        debug=True,
                                        filename=input_filename)

    file_metadata = GoesrFileMetadata.parse(command_args.filename)
    simple_name = s3sync.simple_name(file_metadata, "", file_metadata.sensor_desc.s3source, "nc")
    assert(simple_name, output_filename)


def test_data_extraction_by_s3_filename():
    s3sync = S3GoesrConverter(verbose=True, debug=True)
    command_args = S3GoesrSyncArguments(verbose=True,
                                        debug=True,
                                        filename="OR_ABI-L2-CMIPF-M3C07_G16_s20173561615439_e20173561626211_c20173561626289.nc")
    world_tiff_file = s3sync.extract_data(command_args)
    assert (os.path.exists(world_tiff_file))
    os.remove(world_tiff_file)


def test_data_extraction_valid_date():
    s3sync = S3GoesrConverter(verbose=True, debug=True)
    command_args = S3GoesrSyncArguments(verbose=True, channel=7, debug=True, timestamp="2017_12_22_0045")
    world_tiff_file = s3sync.extract_data(command_args)
    assert (os.path.exists(world_tiff_file))
    os.remove(world_tiff_file)


def test_data_extraction_invalid_date():
    s3sync = S3GoesrConverter(verbose=True, debug=True)
    command_args = S3GoesrSyncArguments(verbose=True, debug=True, timestamp="2017_12_22_0245")
    world_tiff_file = s3sync.extract_data(command_args)
    assert world_tiff_file is None
