from protogen.core import Parser

import glob
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Protocol Generator Compiler.', prog='protogen')
    parser.add_argument('input', type=str, nargs="+",
                        help='Input directory for Protogen files.')
    parser.add_argument('--python', nargs=1, metavar="out_dir",
                        help='Output directory for compiled Python files.')
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='Display additional information during compile.')
    args = parser.parse_args()

    print(args)

    # Clean up and list input files.
    files_to_compile = set()
    for items in args.input:
        for item in glob.glob(items):
            files_to_compile.add(item)

    for item in files_to_compile:
        print(item)

    parser = Parser(inputs=files_to_compile)

    parser.parse()

    parser.display()