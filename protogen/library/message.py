from typing import Tuple


class Serializable(object):
    def Serialize(self, data):
        pass


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
                            item.strip('_o_') + ' (opt)',
                            self._str(data[item], indent+1))
                    elif item.startswith('_r_'):
                        outString += '{}{:<20} \n{}'.format(
                            self._indent(indent),
                            item.strip('_r_') + ' (req)',
                            self._str(data[item], indent+1))
                else:
                    if item.startswith('_o_'):
                        outString += '{}{:<20} \n{}'.format(
                            '    '*indent,
                            item.strip('_o_') + ' (opt)',
                            self._str(data[item], indent+1))
                    elif item.startswith('_r_'):
                        outString += '{}{:<20} \n{}'.format(
                            '    '*indent,
                            item.strip('_r_') + ' (req)',
                            self._str(data[item], indent+1))
            else:
                if indent > 0:
                    if item.startswith('_o_'):
                        outString += '{}\u2192 {:<20}: {} (opt)\n'.format(
                            self._indent(indent),
                            item.strip('_o_'),
                            data[item])
                    elif item.startswith('_r_'):
                        outString += '{}\u2192 {:<20}: {} (req) \n'.format(
                            self._indent(indent),
                            item.strip('_r_'),
                            data[item])
                else:
                    if item.startswith('_o_'):
                        outString += '{}{:<20}: {} (opt)\n'.format(
                            self._indent(indent),
                            item.strip('_o_'),
                            data[item])
                    elif item.startswith('_r_'):
                        outString += '{}{:<20}: {} (req) \n'.format(
                            self._indent(indent),
                            item.strip('_r_'),
                            data[item])
        return outString

    def __str__(self):
        # return self._str()
        return self._str()


class Validatable(object):
    def __init__(self):
        pass


class Message(object):
    def __init__(self):
        pass
