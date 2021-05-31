# Introduction

<WIP PROJECT>

Mimic is a small tool with the intention to defer actions done on objects or classes. These actions can then be executed at a later date. It's main goal is to solve the chicken-and-egg design conundrum.

When you find yourself in a chicken-and-egg situation within your own code, I would probably attribute this to bad design, and advise you to rethink your project structure.

Sometimes, though, when working with 3rd party libraries, you just don't have the choice, and the design of one library does not mesh with that of another.

# Quickstart

The usage should be pretty straightforward, basically you "trap" the object you want to defer, and "release" it at a later date. To do this, you'll need the SasisTrap as followed:

```python
from mimic import StasisTrap

trap = StasisTrap()

my_number = trap.suspend(4)
result = my_number + 5

print(my_number) # <mimic.trap.Deferred object at 0x7fe41a971c18>
print(result) # <mimic.trap.Deferred object at 0x7fe41a971cc0>

trap.release(my_number)

print(my_number) # 4
print(result) # 9

```

# Pitfalls

It's important to note that only operations performed __on__ deferred objects are allowed. Performing operations __with__ deferred objects will go horribly wrong.

For instance 
```python
my_number = trap.suspend(4)
result = 5 + my_number
```
will result in a TypeError
