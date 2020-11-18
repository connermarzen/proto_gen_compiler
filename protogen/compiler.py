import os
from typing import List

from protogen.core import PGParser
from protogen.library.python.std import ACCEPTED_TYPES
from protogen.util import PGFile, PyClass

tab = '    '


class Compiler(object):

    def __init__(self, inFiles: List[str], outDir: str, verbose: bool = False):
        self._parser = PGParser(inFiles)
        self._parser.parse()

        # clean up trailing slashes (will be re-added later)
        self.outDir = outDir.rstrip('/')
        self.classes: List[PyClass] = []
        self.files: List[PGFile] = self._parser.transform()

        for file in self.files:  # sift through the files and find any suspect type declarations.
            declarations, types = set(), set()
            for item in file.types:
                types.add(item[0])
            # Fill the set before re-iterating against delcarations.
            for item in file.declarations:
                declarations.add(file.declarations[item][0])

            for item in declarations:
                if item not in types and item not in ACCEPTED_TYPES:
                    raise ValueError(
                        f"The declaration of type {item} was specified but no type {item} exists.")

        if not os.path.exists(outDir):
            os.makedirs(outDir)

        del(self._parser)  # save memory, the parser is dense and repetitive
