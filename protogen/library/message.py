from typing import Tuple


class Serializable(object):
    def Serialize(self, data):
        pass


class Printable(object):

    def _str(self, data=None, indent: Tuple[str, int] = ('    ', 0)) -> str:
        ind, mul = indent
        variables = vars(self) if data is None else vars(data)
        outString = ''
        for var in variables:
            if not isinstance(variables[var], (int, float, str, list, dict, set, type(None))):
                # self.__str__(indent+indent)
                if var.startswith('_o_'):
                    outString += 'Optional {:>12}: \n{}{}'.format(
                        var.strip('_o_').upper(),
                        ind*(mul),
                        self._str(variables[var], (ind, mul+1)))

                elif var.startswith('_r_'):
                    outString += 'Required {:>12}: \n{}{}'.format(
                        var.strip('_r_').upper(),
                        ind*(mul),
                        self._str(variables[var], (ind, mul+1)))
            elif data is not None:
                if var.startswith('_o_'):
                    outString += '{}Optional {:>12}: {}'.format(
                        ind*(mul), var.strip('_o_').upper(), variables[var])

                elif var.startswith('_r_'):
                    outString += '{}Required {:>12}: {}'.format(
                        ind*(mul), var.strip('_r_').upper(), variables[var])
            else:
                if var.startswith('_o_'):
                    outString += 'Optional {:>12}: {}{}'.format(
                        var.strip('_o_').upper(), ind*mul, variables[var])

                elif var.startswith('_r_'):
                    outString += 'Required {:>12}: {}{}'.format(
                        var.strip('_r_').upper(), ind*mul, variables[var])

            outString += '\n'
        return outString

    def __str__(self):
        return self._str()


class Message(object):
    def __init__(self):
        pass
