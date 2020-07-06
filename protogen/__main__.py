from protogen.core import PGParser
from protogen.compiler import PythonCompiler

import argparse
import glob
import sys
from pprint import pprint

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Protocol Generator Compiler.',
        prog='protogen')

    parser.add_argument('input',
                        type=str,
                        nargs="+",
                        help='Input directory for Protogen files.')

    parser.add_argument('-py', '--python',
                        type=str,
                        const="output",
                        metavar='out_dir',
                        nargs='?',
                        help='Output directory for compiled Python files.')

    parser.add_argument('-m', '--minify',
                        metavar="out_dir",
                        help="Minify your protogen files for storage.")

    parser.add_argument('-e', '--expand',
                        metavar="out_dir",
                        help="Expand your previously minified protogen file.")

    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        default=False,
                        help='Display additional '
                        'information during compile time.')

    args = parser.parse_args()

    if not args.python:
        print('You must specify at least one output format ("--python out_dir" etc.)')
        sys.exit(1)

    if args.python:
        pyCompiler = PythonCompiler(inFiles=args.input,
                                    outDir=args.python,
                                    verbose=args.verbose)
        pyCompiler.compile()
