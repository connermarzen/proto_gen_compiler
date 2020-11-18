# README

## Installation

This modules requires `messagepack` npm package:

```bash
$ npm install messagepack
```

## Subclass Support

Due to the fact that nested classes do not exist in Javascript, support for this is only partially implemented.

The use of `module.exports` simulates the nested class structure, but as a result, no subtypes are allowed to share the same name:

```
name TestFile;

type TestMessage {
    type TestSubMessage {
        contents
            .String
            .req;
    }
    submessage
        .TestSubMessage
        .req;

    author
        .String
        .req;
}
```

Becomes (stubbed):

```javascript
const { Serializable } = require('./protogen')

class TestSubMessage extends Serializable {
    ...
}

class TestMessage extends Serializable {
    ...
}

module.exports.TestMessage = TestMessage
module.exports.TestMessage.TestSubMessage = TestSubMessage
```

As opposed to what would like this in other languages:

```javascript
const { Serializable } = require('./protogen')

class TestMessage extends Serializable {

    class TestSubMessage extends Serializable {
        ...
    }

    ...
}

module.exports.TestMessage = TestMessage
```

As a side effect, iff two top level messages share the same name for a sub-type, this will cause a conflict and the class will be compiled twice.

There are two best fixes:

1. Are the subtypes identical?

Pull them out and make a top-level type shared between the two:

```
name TestFile;

type TestSubMessage { <-- We moved it up here to be used by both.
    contents
        .String
        .req;
}

type TestMessage {
    submessage
        .TestSubMessage
        .req;

    author
        .String
        .req;
}

type TestMessage2 {
    submessage
        .TestSubMessage
        .req;

    year
        .int
        .req;
}
```

2. Are only the names identical?

Namespace the names in a way that makes sense for your project.

```
name TestFile;

type TestMessage {
    type TestSubMessage {
        contents
            .String
            .req;
    }
    submessage
        .TestSubMessage
        .req;

    author
        .String
        .req;
}

type TestMessage2 {
    type TestSubMessage2 { // <-- they're now different and safe.
        contents
            .String
            .req;
    }
    submessage
        .TestSubMessage
        .req;

    author
        .String
        .req;
}
```