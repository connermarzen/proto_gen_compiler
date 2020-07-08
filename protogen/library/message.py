from typing import Dict
from pprint import pprint
import msgpack


class Serializable(object):
    def serialize(self):
        return msgpack.packb(self._encode())

    @staticmethod
    def deserialize(data: bytes) -> Dict:
        return msgpack.unpackb(data, raw=False)

    def __encode(self, data=None, out: Dict = None) -> Dict:
        out = dict()

        if data is None:
            data = vars(self)
        else:
            data = vars(data)

        for item in data:
            if not isinstance(data[item], (int, float, str, list, dict, set, type(None))):
                if item.startswith('_r_'):
                    out[item.lstrip('_r_')] = (self.__encode(
                        data=data[item], out=out), True)
                elif item.startswith('_o_'):
                    out[item.lstrip('_o_')] = (self.__encode(
                        data=data[item], out=out), False)
            else:
                if item.startswith('_r_'):
                    out[item.lstrip('_r_')] = (data[item], True)
                elif item.startswith('_o_'):
                    out[item.lstrip('_o_')] = (data[item], False)
        return out

    def _encode(self) -> Dict:
        finalOut = self.__encode()
        return {
            self.__class__.__module__+'.'+self.__class__.__name__: finalOut
        }

    @staticmethod
    def _init(node, data):
        for item in data:
            req = ('_r_' if data[item][1] else '_o_') + item
            if type(data[item][0]) is dict:
                Serializable._init(getattr(node, req), data[item][0])
            else:
                setattr(node, req, data[item][0])


class Printable(object):

    def _indent(self, level: int):
        if level > 0:
            return '    '*(level-1) + ' \u2514' + '\u2500'*2
        return ''

    def _str(self, data=None, indent: int = 0) -> str:
        if data is None:
            data = vars(self)
        else:
            data = vars(data)
        outString = ''

        for item in data:
            if not isinstance(data[item], (int, float, str, list, dict, set, type(None))):
                # the object is a recursive type.
                if indent > 0:
                    if item.startswith('_o_'):
                        outString += '{}{:<20} \n{}'.format(
                            self._indent(indent),
                            item.lstrip('_o_') + ' (opt)',
                            self._str(data[item], indent+1))
                    elif item.startswith('_r_'):
                        outString += '{}{:<20} \n{}'.format(
                            self._indent(indent),
                            item.lstrip('_r_') + ' (req)',
                            self._str(data[item], indent+1))
                else:
                    if item.startswith('_o_'):
                        outString += '{}{:<20} \n{}'.format(
                            '    '*indent,
                            item.lstrip('_o_') + ' (opt)',
                            self._str(data[item], indent+1))
                    elif item.startswith('_r_'):
                        outString += '{}{:<20} \n{}'.format(
                            '    '*indent,
                            item.lstrip('_r_') + ' (req)',
                            self._str(data[item], indent+1))
            else:
                if indent > 0:
                    if item.startswith('_o_'):
                        outString += '{}\u2192 {:<20}: {} (opt)\n'.format(
                            self._indent(indent),
                            item.lstrip('_o_'),
                            data[item])
                    elif item.startswith('_r_'):
                        outString += '{}\u2192 {:<20}: {} (req) \n'.format(
                            self._indent(indent),
                            item.lstrip('_r_'),
                            data[item])
                else:
                    if item.startswith('_o_'):
                        outString += '{}{:<20}: {} (opt)\n'.format(
                            self._indent(indent),
                            item.lstrip('_o_'),
                            data[item])
                    elif item.startswith('_r_'):
                        outString += '{}{:<20}: {} (req) \n'.format(
                            self._indent(indent),
                            item.lstrip('_r_'),
                            data[item])
        return outString

    def __str__(self):
        # return self._str()
        return self._str()


class Validatable(object):
    def __init__(self):
        pass


class Message(object):
    def _filterVars(self, data) -> bool:
        if data.startswith('_o_') or data.startswith('_r_'):
            return True
        return False

    def matchAttribute(self, varName: str):
        for item in filter(self._filterVars, vars(self)):
            if item.lstrip('_o_').lstrip('_r_') == varName:
                return item
        raise AttributeError('Variable name \'{}\' not found in {}.'
                             .format(varName, self.__class__.__name__))
