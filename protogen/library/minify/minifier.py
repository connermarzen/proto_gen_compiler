import os
import glob
from typing import List
import sys


class Minifier():
    def __init__(self, inFiles: List[str], outDir: str):

        # clean up trailing slashes (will be re-added later)
        self.outDir = outDir.rstrip('/')

        # Clean up and list input files.
        self._files = {}
        for items in inFiles:
            for item in glob.glob(items):
                self._files[item] = None  # Add placeholder in dict for parsing

    def minify(self):
        if len(self._files) == 0:
            print('No valid files were specified.')
            print('Note: a glob pattern is acceptible for multiple files.\n')
            print('Example:\n  *.protogen\n')
            print('You can also specify more than one file, '
                  'separated by spaces.\n')
            print('Example:\n  a.protogen b.protogen c.protogen')
            sys.exit(1)

        if not os.path.exists(self.outDir):
            os.makedirs(self.outDir)

        for item in self._files:
            text = ''
            try:
                with open(item, 'r') as data:
                    for line in data.readlines():
                        
                        text += ''.join(line.strip()).split('//', 1)[0]
                file = open(self.outDir + '/' +
                            item[:item.find('.')] + '.min.protogen', 'w')
                file.write(text+'\n')
            except IsADirectoryError as e:
                print('You must specify files. For multiple files in a '
                      'directory, a glob pattern may be used.')
                print('Example: directory/*.protogen')
                sys.exit(2)
