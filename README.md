# Logic Gate Simulator
An old A Level computing coursework written in python.

A boolean algebra/logic gate simulator written in python using pygame. Written by a younger Qi-rui who didn't know about git or version control.

## Installation

1. Install Python 3.X (3.4 for py2exe building).
2. `pip install pygame (py2exe)` (py2exe is optional and windows only).
3. `python logic_gates.py`

## Usage

TODO: include my terrible user manual? 

## Contributing

It's probably not a good idea to contribute to this code, maybe when I've cleaned it up a little.

## Notable "Features"

### Overbar Rendering

Using the combination of what I now know is a parser and terrible font code, correctly draws an overbar instead of a not symbol. The code is pretty bad and I'm pretty sure it was hacked together in the span of 2 days. Originally the parsing and rendering was done in `standalone_expression_rendering.py`, which contains a naive implimentation of parsing my youger self came up with. 

### Logic Gates/Boolean Algebra Converter

Converts a set of logic gates with no loops into a boolean algebra. Conversion must start from a "lamp" and I'm pretty sure the loop code is broken.
Converts a boolean expression to logic gates. Unfortunatly I ran out of time and all of the components are put into the bottom right hand corner.

### Boolean Expression Simplification

### Truth Table Creation

Creates a nice truth table for a given boolean expression. Unfortunatly this code is terribly inefficient thus even the expression `A+B+C+D+E` will cause notable lag when dragging around.

### Save to File

Saving to a file is implimented by converting the logic gate to an expression and then picking it. This is a terrible idea since the program will crash if you attempt to save or load a circuit with loops. It also means that loading a save will result in all the components dumped on the middle of the screen. On the upside, saves are pretty small.

### "Dynamic UI"

Menu buttons align with resizing and I'm pretty sure font size scales terribly with display resolution. Unfotunatly the program also crashes if you make the window too small. 

### "Removing Circuit Loops"

Technically the logic gate implimentation is tri state: On, Off, Undefined. At first the idea was to not allow the user to have any loops at all, but this quickly became too costly to instead the undefined state was added. A gate will output undefined if any of its inputs are undefined. 
It is still possible to create loop "clocks", you simply need to connect everything to a well defined input then replace them. 

### "Nice" Wire Rendering

By playing around with beizer curves, magic numbers and the exponential function, I managed to get a nice-ish curve for the wire.
