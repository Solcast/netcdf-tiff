import argparse
import sys

from conversion_options import ConversionOptions
from goes16_converter import Goes16Converter


def parse_arguments():
    """ Creates an ArgumentParser, adds arguments and options, and then returns
    the populated name space
        Returns:
            Populated namespace
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", dest="input_file", help="input file or pattern", default="")
    parser.add_argument("-o", "--output", dest="output_file", help="output file or pattern", default="")
    parser.add_argument("-d", "--debug", dest="debug", action='store_true')
    parser.add_argument("-v", "--verbose", dest="verbose", action='store_true')
    parser.set_defaults(verbose=False)
    parser.set_defaults(debug=False)
    return parser.parse_args()

def main():
    args = parse_arguments()
    extract_args = ConversionOptions(
        filename=args.input_file,
        output=args.output_file,
        verbose=args.verbose,
        debug=args.debug)
    print(extract_args)

    io_extract = Goes16Converter(verbose=extract_args.verbose, debug=extract_args.debug)
    io_extract.extract(extract_args)



if __name__ == "__main__":
    print('Starting {0}'.format(str(sys.argv)))
    main()