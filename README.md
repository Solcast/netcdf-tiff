[![Build Status](https://travis-ci.org/Solcast/netcdf-tiff.svg?branch=master)](https://travis-ci.org/Solcast/netcdf-tiff)

# netcdf-tiff
NETCDF to GeoTIFF utility library

Python 3 library designed to extract GeoTIFF images from NETCDF4+ files.  Working code extraction model is built for the GOES16 :satellite:

## Sample images produced 

### Channel 2
![Channel 2](/images/goes16_channel2.jpg)

### Channel 7
![Channel 7](/images/goes16_channel7.jpg)

### Channel 13
![Channel 13](/images/goes16_channel13.jpg)

#### Example code, complete Cloud and Moisture product [example](/example/goes16_cloud_moisture.py)
```python
    conv_options = ConversionOptions(
        filename="OR_ABI-L2-CMIPF-M3C02_G16_s20180161600431_e20180161611198_c20180161611267.nc",
        output="my_test_image.tiff",
        verbose=True,
        debug=True)
    goes16 = Goes16Converter(verbose=conv_options.verbose, debug=conv_options.debug)
    result = goes16.extract(conv_options)
```

### Live GOES16 data sources
[NOAA](http://www.noaa.gov/) is currently producing data extracts for public use on [AWS](https://aws.amazon.com/).  You should download and setup your [AWS CLI](https://aws.amazon.com/cli/) tool first in your choice of environment Linux/mac OS/Windows.  There are scripts in the subfolder `/tests/data/` that will generate the command to obtain the latest netcdf files for you to work with

* [Linux/mac OS](/tests/data/get_goes16_data.sh)
* [Windows](/tests/data/get_goes16_data.ps1)
 

### Need help?
* [Forums](https://forums.solcast.com.au)
* [NOAA-GOES16](https://www.nesdis.noaa.gov/GOES-R-Series-Satellites)
* [GOES16 Band Reference](https://www.weather.gov/media/crp/GOES_16_Guides_FINALBIS.pdf)

### How to contribute
 * Fork the repository
 * Add something awesome
 * Create a pull request
 * :sun_with_face: Celebrate :sun_with_face:


License
-------
License can be found here: [LICENSE](LICENSE)
