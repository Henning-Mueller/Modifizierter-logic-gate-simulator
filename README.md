# <h1>Modifizierter Logic Gate Simulator</h1>

Diese ist der modifizierte Logic Gate Simulator der für die Generierung der Trainingsdaten verwendet wurde.<br/>
Es wurden einige Änderungen durchgeführt.<br/>
Orginal Readme.md vom Ersteller folgt.<br/>
Orginal Github: https://github.com/qqii/logic-gate-simulator <br/>











# Logic Gate Simulator
An old A Level computing coursework written in python.

A boolean algebra/logic gate simulator written in python using pygame. Written by a younger Qi-rui who didn't know about git or version control.

## Installation

### Windows Binary

1. [Download the binary](https://github.com/qqii/logic-gate-simulator/releases).
2. Extract into a folder with [7zip](http://www.7-zip.org/download.html).
3. Run logic_gates.exe.

### From Source

1. Install Python 3.x (3.4 for py2exe building).
2. `pip install pygame (py2exe)` (py2exe is optional and windows only).
3. `python logic_gates.py`

## Usage

The program has 3 "tabs" which can be navigated using the button on the top right: "Boolean Algebra", "Circuit Simulation" and "Help". Depending on which tab you are in, the bottom right buttons will do different things. 

### Circuit Simulation

Click the buttons to spawn more components. Components, wires can be dragged by clicking on them. You can move everything by dragging on the background.  

Components and wires can be:
* dragged using the left mouse button
* duplicated using the middle mouse button
* deleted using the right mouse button

Connect compoents by dragging from output circle of a component. This create a wire you can attach to the input of another component.

Clicking "Convert to Expression" will attempt to create an expression starting at a lamp.

### Boolean Algebra

Click the terrible text box on the bottom left to enter a boolean expression. 
Click "Convert to Expression" to parse the expression and create a table. 

The table can be zoomed using the scroll wheel and dragged around.

The simplify button will attempt to simplify your boolean expression.

Clicking "Convert to Circuit" will create a logic circuit from your expression.

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
