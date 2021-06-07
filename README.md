# Introduction

Mimic is a small tool with the intention to defer actions done on objects or classes. These actions can then be executed at a later date. It's main goal is to solve the chicken-and-egg design conundrum.

When you find yourself in a chicken-and-egg situation within your own code, it's most likely attributed to a sub-optimal project design.
If this is the case, it's probably advisable to rethink your project structure.

Sometimes, though, when working with 3rd party libraries, you just don't have the choice, and the design of one library does not mesh with that of another.
Out of spite (I'm looking at you \<insert most libraries that require an initialized instance to define global decorators\>), I started writing this library so that I had control over "when" I initialized "what", while being able to do it in a controlled local scope without losing the ability to use global definitions.
  
**BIG FAT DISCLAIMER**: I wouldn't use this lib in production code, not in its current state at least :) It needs some more battle testing before I can comfortably say it's stable. Feel free to contribute to this battle testing.

# Quickstart

The core of this library is the `Deferred` object, that basically behaves as a mock object. The only difference is that the `Deferred` object does not have reserved names, so you can do literally **__any__** operation on it.

Of course, that means that you, the user, won't be able to use this deferred object as the driver. For this we'll need a handler object that set things in motion, and ties things together when needed.

```python
from mimic import Mimic

# Make the handler object
mimic = Mimic()
# Make a deferred object using the factory on the handler object
husk = mimic.husk()

# Do the deferred operations you want to do
result = husk + 3

# Replay anything done on the deferred object
mimic.absorb(husk).as_being(5)
assert result == 5
```

# A more elaborate example
This example won't make much sense, as Flask-SQLAlchemy plays quite nicely when it comes to having control over the local scope while still performing global actions, but I thought it was a nice example of what the library is capable of. Here we'll defer the creation, initialization and persisting of an SQLAlchemy model. Then then play it when it suits us best.

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

# Pitfalls

It's important to note that only operations performed __on__ deferred objects are allowed. Performing operations __with__ deferred objects will go horribly wrong.

For instance 
```python
my_number = trap.suspend(4)
result = 5 + my_number
```
will result in a TypeError
