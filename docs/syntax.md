# Syntax Guide

## Not-so-practical example

This is a basic example file that we can use to explain the most basic aspects of the syntax:

```javascript
name ExampleProtocol; // Notice, inline comments are allowed.

/*
Also notice that block comments are allowed!
*/

type ExampleMessage {
    /*
    The Example message is comprised of some contents and
        a slight anount of metadata.
    */
    messageContent // This is main portion of the message
        .string    // this is the data type
        .req;      // indicates a required type.

    isParent
        .bool      // Be sure to read the section on types.
        .opt;      // indicates an optional type.

    delay
        .uint32;
        // I chose to leave out the required or optional type
        // will default to optional.
}
```

The above will get generated into this (Python) code:

```python
from protogen.library.message import Message
from protogen.library.message import Serializable
from protogen.library.message import Printable


class ExampleMessage(Message, Serializable, Printable):

    def __init__(self, data: dict = None):
        self._r_messageContent: str = None
        self._o_isParent: bool = None
        self._o_delay: int = None

        if data is not None:
            self._init(self, data)

    def getMessagecontent(self) -> str:
        return self._r_messageContent

    def setMessagecontent(self, messageContent: str) -> 'ExampleMessage':
        self._r_messageContent = messageContent
        return self

    def getIsparent(self) -> bool:
        return self._o_isParent

    def setIsparent(self, isParent: bool) -> 'ExampleMessage':
        self._o_isParent = isParent
        return self

    def getDelay(self) -> int:
        return self._o_delay

    def setDelay(self, delay: int) -> 'ExampleMessage':
        self._o_delay = delay
        return self
# End Class ExampleMessage


class ExampleProtocolFactory(object):
    @staticmethod
    def deserialize(data: bytes) -> Message:
        data = Serializable.deserialize(data)
        if len(data) > 1:
            raise AttributeError('This is likely not a Protogen packet.')

        packetType = None
        for item in data:
            packetType = item[item.rfind('.')+1:]
            if packetType == 'ExampleMessage':
                return ExampleMessage(data[item])
            else:
                raise AttributeError('Respective class not found.')
```

The generated code consists of a few key items:

### Classes

There is a class for every type that was declared in our file. In this case, the ExampleMessage type we wrote in our `.protogen` file became a PYthon class. This class has a getter and setter for every single attribute you specified. Note that nested types are allowed, and will be explained in further detail down below.

This class can now be used like so:

```python
>>> import ExampleProtocol_proto as ex

>>> myMessage = ex.ExampleMessage() # we construct an empty message
>>> myMessage.setMessagecontents('Hello, there!')
>>> myMessage.setIsparent(True)

>>> print(myMessage)
```