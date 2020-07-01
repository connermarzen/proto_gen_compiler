from enum import Enum


class PGToken(Enum):
    DECLARATION = 1
    TYPE_BLOCK = 2
    DATA_TYPE = 3
    HEADER_NAME = 4
    NAME = 5
    REQ = 6
    OPT = 7
    REQUIRED = 8
    INCLUDE = 9