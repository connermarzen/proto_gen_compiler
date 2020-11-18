
import argparse
from protogen.library import markdown
import sys
from pprint import pprint

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Protocol Generator Compiler.',
        prog='protogen')

    parser.add_argument('input',
                        type=str,
                        nargs='+',
                        help='Input directory for Protogen files.')

    parser.add_argument('-py', '--python',
                        type=str,
                        const='output',
                        metavar='out_dir',
                        nargs='?',
                        help='Output directory for compiled Python files.'
                             '[Default]: "output" folder')

    parser.add_argument('-node', '--node-javascript',
                        type=str,
                        const='output',
                        metavar='out_dir',
                        nargs='?',
                        help='Output directory for compiled NodeJS Javscript files.'
                             '[Default]: "output" folder')

    parser.add_argument('-md', '--markdown',
                        type=str,
                        const='output',
                        metavar='out_dir',
                        nargs='?',
                        help='Generate Markdown documentation.'
                             '[Default]: "output" folder')

    parser.add_argument('-m', '--minify',
                        type=str,
                        const='output',
                        metavar='out_dir',
                        nargs='?',
                        help='Minify your protogen files for storage.'
                             '[Default]: "output" folder')

    # parser.add_argument('-e', '--expand',
    #                     metavar='out_dir',
    #                     help='Expand your previously minified protogen file.')

    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        default=False,
                        help='Display additional '
                        'information during compile time.')

    args = parser.parse_args()

    operated = False

    if args.python:
        from protogen.library.python.compiler import PythonCompiler
        pyCompiler = PythonCompiler(inFiles=args.input,
                                    outDir=args.python,
                                    verbose=args.verbose)
        pyCompiler.compile()
        del(pyCompiler)
        operated = True

    if args.node_javascript:
        from protogen.library.nodeJS.compiler import NodeJSCompiler
        nodeJsCompiler = NodeJSCompiler(inFiles=args.input,
                                        outDir=args.node_javascript,
                                        verbose=args.verbose)
        nodeJsCompiler.compile()
        del(nodeJsCompiler)
        operated = True

    if args.minify:
        from protogen.library.minify.minifier import Minifier
        minifier = Minifier(inFiles=args.input,
                            outDir=args.minify)
        minifier.minify()
        del(minifier)
        operated = True

    if args.markdown:
        from protogen.library.markdown.compiler import MarkdownCompiler
        markdownCompiler = MarkdownCompiler(inFiles=args.input,
                                            outDir=args.markdown)
        markdownCompiler.compile()
        operated = True

    if not operated:
        print('You must specify at least one output format ("--python out_dir" etc.)')
        sys.exit(1)
