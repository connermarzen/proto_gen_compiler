import lark
from protogen.util import PGToken
from protogen.library.python.std import ACCEPTED_TYPES


class PGTransformer(lark.Transformer):
    def header(self, item):
        (item,) = item
        return item

    def start(self, items): return list(items)

    def declaration(self, items): return {PGToken.DECLARATION: items}

    def type_block(self, items): return {PGToken.TYPE_BLOCK: items}

    def data_opt(self, item):
        if len(item) > 0:
            return item[0]
        return False

    def include(self, item): return {PGToken.INCLUDE: item[0]}

    def data_type(self, item):
        if item[0] == 'req' or item[0] == 'opt':
            raise SyntaxError('DATATYPE Expected, '
                              'received {}'.format(item[0]))
        # if item[0] in ACCEPTED_TYPES:
        #     return ACCEPTED_TYPES[item[0]]
        else:
            return item[0]

    def HEADER_NAME(self, item):
        return {PGToken.HEADER_NAME: item.value}

    def name(self, item): return item[0]
    def DATATYPE(self, item): return item.value
    def REQUIRED(self, item): return True
    def OPTIONAL(self, item): return False
    def ESCAPED_STRING(self, item): return item.strip("'").strip('"')
    def QNAME(self, item): return self.ESCAPED_STRING(item)
