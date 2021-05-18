# Introduction

Stasis is a small tool with the intention to defer actions done on objects or classes. These actions can then be executed at a later date. It's main goal is to solve the chicken-and-egg design conundrum.

When you find yourself in a chicken-and-egg situation within your own code, I would probably attribute this to bad design, and advise you to rethink your project structure.

Sometimes, though, when working with 3rd party libraries, you just don't have the choice, and the design of one library does not mesh with one another.

# Quickstart

The usage should be pretty straightforward, basically you "trap" the object you want to defer, and "release" it at a later date. To do this, you'll need the SasisTrap as followed:

```python
from stasis import StasisTrap

trap = StasisTrap

my_number = trap.suspend(4)
my_number += 


```
