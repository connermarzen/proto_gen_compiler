from protogen.core import PGParser

import argparse
import glob
import sys
from pprint import pprint

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Protocol Generator Compiler.', prog='protogen')
    parser.add_argument('input', type=str, nargs="+",
                        help='Input directory for Protogen files.')
    parser.add_argument('-py', '--python', nargs=1, metavar="out_dir",
                        help='Output directory for compiled Python files.')
    parser.add_argument('-m', '--minify', metavar="out_dir",
                        help="Minify your protogen files for storage.")
    parser.add_argument('-e', '--expand', metavar="out_dir",
                        help="Expand your previously minified protogen file.")
    parser.add_argument('-v', '--verbose',
                        action='store_true', default=False,
                        help='Display additional '
                        'information during compile time.')
    args = parser.parse_args()

    if not args.python:
        print('You must specify at least one output format ("--python out_dir" etc.)')
        sys.exit(1)

    # Begin Parsing Documents
    parser = PGParser(inputs=args.input)
    parser.parse()
    parser.transform()

    if args.verbose:
        parser.display()
    
    # pprint(parser._trees)
