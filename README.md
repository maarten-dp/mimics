[![Build Status](https://travis-ci.com/maarten-dp/mimics.svg?branch=master)](https://travis-ci.com/maarten-dp/mimics)
[![codecov](https://codecov.io/gh/maarten-dp/mimics/branch/master/graph/badge.svg?token=PBYN5VAJVZ)](https://codecov.io/gh/maarten-dp/mimics)
[![PyPI version](https://badge.fury.io/py/mimics.svg)](https://pypi.org/project/mimics/)

# Introduction

Mimic is a small tool with the intention to defer actions done on objects or classes. These actions can then be executed at a later date. It's main goal is to solve the chicken-and-egg design conundrum.

**When you find yourself in a chicken-and-egg situation within your own code, it's most likely attributed to a sub-optimal project design.
If this is the case, it's probably advisable to rethink your project structure.**

Sometimes, though, when working with 3rd party libraries, you just don't have the choice, and the design of one library does not mesh with that of another.
Out of spite (I'm looking at you \<insert most libraries that require an initialized instance to define global scoped decorators\>), I started writing this library so that I had control over "when" I initialized "what", while being able to do it in a controlled local scope without losing the ability to use global definitions.

**BIG FAT DISCLAIMER**: I wouldn't use this lib in production code, not in its current state at least :) It needs some more battle testing before I can comfortably say it's stable. Feel free to contribute to this battle testing.

# Quickstart

The core of this library is the `Deferred` object, that basically behaves like a mock object. The only difference is that the `Deferred` object does not have reserved names, so you can do literally ***any*** operation on it.

Of course, that means that you, the user, won't be able to use this deferred object as the driver. For this we'll need a handler object that set things in motion, and ties things together when needed.

```python
from mimics import Mimic

# Make the handler object
mimic = Mimic()
# Make an object, using the factory on the handler object, that will record all actions
husk = mimic.husk()

# Do the deferred operations you want to do
result = husk + 3

# Replay anything done on the deferred object onto another object
mimic.absorb(husk).as_being(5)
# Doing an additional `is True` to ensure to result is a boolean and not a deferred object
# (because, yes, even these actions are deferred before playing)
assert (result == 8) is True
```

# A more elaborate example
This example won't make much sense, as Flask-SQLAlchemy plays quite nicely when it comes to having control over the local scope while still performing global actions, but I thought it was a nice example of what the library is capable of. Here we'll defer the creation, initialization and persisting of an SQLAlchemy model.

Once we've done all we wanted, we can play it whenever it suits us best.

```python
# Make the handler and deferred object
mimic = Mimic()
husk = mimic.husk()

# Defer the making of an SQLA model using the deferred object
class MyModel(husk.Model):
    id = husk.Column(husk.Integer, primary_key=True)
    name = husk.Column(husk.String(255), nullable=False, unique=True)

# Defer the db creation
husk.create_all()
# Defer the initialization and persisting of an instance
my_model = MyModel(name="test")
husk.session.add(my_model)
husk.session.commit()

# Make the actual SQLA db object
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Replay deferred actions as being the db
mimic.absorb(husk).as_being(db)

# Verify it worked
models = MyModel.query.all()
assert len(models) == 1
assert models[0].name == "test"
```

# How it works
As mentioned above, the entire library revolves around the `Deferred` object. Due to being able to do, well, almost anything with this object, it's important that you don't initialize a deferred object yourself (unless you know what you're doing). It's important that you make an instance of this class through the factory method that is available on a `Mimic` instance.

Basically the `Deferred` object can be in two states:
- suspended
- unsuspended

A shocker, I know. Whenever the `Deferred` object is suspended, it will record any action done upon it. Whenever an attribute is accessed, a method is called, or anything that returns a value, it will create and return a new instance of the `Deferred` object, that in turn also records actions done with it.

Once you're ready to play your deferred actions, bringing it to an unsuspended state, the recorded actions will be re-played on the chosen object. From then on, the spawned deferred objects will work as a proxy that forwards any request to the subject it's related to.

# Pitfalls
## Proxy object
Because this library is not doing black magic (or at least, not an aweful lot 😉), it's important to know that any subject that the `Deferred` object shadows, will never ***truly*** be itself after unsuspending. We're not manipulating the virtual memory, manipulating local and global variables or patching imported modules (mind you, I've thought about it).

While it may look like you're interacting with the subject itself, you'll always be interacting with a proxy object that looks and feels like its subject. As such, some kinks might pop up in certain cases (cfr. BIG FAT DISCLAIMER).

## The Deferred object's limits
It's important to note that only operations performed ***on*** deferred objects are allowed. Performing operations ***with*** deferred objects will go horribly wrong.

For instance
```python
husk = Mimic().husk()
result = 5 + husk
```
will result in a TypeError
