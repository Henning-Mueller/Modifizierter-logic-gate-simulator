"""
The main module of the Logic Gates program.
"""
# Imports everything, including those imported by other modules
# This is because when converting to .pyd, py2exe can no longer find out which
# modules have been imported
import math
import pickle
import threading
import itertools
import collections
from xml.dom import minidom
import os
import tkinter
import tkinter.filedialog
import tkinter.simpledialog
import tkinter.colorchooser
import tkinter.messagebox

import pygame
import pygame.gfxdraw
import pygame.freetype

import boolean
import logic_circuit
import uuid
import alignment
import interfaces
import text
import gui
import logic_circuit_gui

# TODO: Consider having an options file
# TODO: Consider making the colors editable
# TODO: Consider making the font size editable

# Load pygame
pygame.init()
pygame.display.init()

NATIVE_RESOLUTION = (pygame.display.Info().current_w,
                     pygame.display.Info().current_h)
# Ensure that the initial window is not too large so that it doesn't fix
# on the screen
RESOLUTION = (int(NATIVE_RESOLUTION[0] * 3 / 4),
             int(NATIVE_RESOLUTION[1] * 3 / 4))

FLAGS = pygame.RESIZABLE  # pygame.DOUBLEBUF|pygame.HWACCEL|pygame.HWSURFACE


"""
Modifizierter Code
"""
WHITE = pygame.color.Color(255, 255, 255, 255)
BLACK = pygame.color.Color(0, 0, 0, 255)
BLUE = pygame.color.Color(0, 0, 0, 255)
LIGHT_BLUE = pygame.color.Color(0, 0, 0, 255)
RED = pygame.color.Color(255, 0, 0, 255)

"""
Ende Modifizierter Code
"""
# 0 for uncapped fps
FPS = 0

# This is the pygame surface for the display which everything is drawn on
surface = pygame.display.set_mode(RESOLUTION, FLAGS)
pygame.display.set_icon(pygame.image.load("images\\favicon.ico"))
pygame.display.set_caption("Logic Gates 1.0.0")
# Clock for keeping FPS
clock = pygame.time.Clock()

# For copy and paste, must be called after pygame.display.set_mode()
pygame.scrap.init()
pygame.fastevent.init()

# Load Tkinter
# Not all of these popup dialoges are used, but are kept in in case they
# are needed for later use
tk_function_dict = {"directory": tkinter.filedialog.askdirectory,
                    "openfile": tkinter.filedialog.askopenfile,
                    "openfilename": tkinter.filedialog.askopenfilename,
                    "openfilenames": tkinter.filedialog.askopenfilenames,
                    "openfiles": tkinter.filedialog.askopenfiles,
                    "saveasfile": tkinter.filedialog.asksaveasfile,
                    "saveasfilename": tkinter.filedialog.asksaveasfilename,
                    "color": tkinter.colorchooser.askcolor,
                    "float": tkinter.simpledialog.askfloat,
                    "integer": tkinter.simpledialog.askinteger,
                    "string": tkinter.simpledialog.askstring,
                    "okcancel": tkinter.messagebox.askokcancel,
                    "question": tkinter.messagebox.askquestion,
                    "retrycancel": tkinter.messagebox.askretrycancel,
                    "yesno": tkinter.messagebox.askyesno,
                    "yesnocancel": tkinter.messagebox.askyesnocancel,
                    "error": tkinter.messagebox.showerror,
                    "info": tkinter.messagebox.showinfo,
                    "warning": tkinter.messagebox.showwarning}
# Create a tk window
root = tkinter.Tk()
# Move it to the top
root.attributes("-topmost", True)
# Now hide it
root.withdraw()
# This is so that when tk_popup_dialog is called, a new tk window is not
# created


# TODO: when doing files, make it only open a specific type
# This is done by passing
# filetypes=(("<file_type>", "*.<filetype>"), ("<file_type>", "*.<filetype>;*.<filetype>"))
# when calling the function
def tk_popup_dialog(mode, title="", prompt=""):
    """
    Displays a dialog using Tkinter.

    tk_function_dict.keys() is a list of all possible modes.
    """
    pumping = True

    # Keep the display from freezing up
    def event_pump():
        while pumping:
            # Ignore any events that occur
            pygame.event.get()
        pygame.event.get()
        # print("stopped")
    t = threading.Thread(target=event_pump)
    t.start()

    if mode in ("float", "integer", "string",
                "okcancel", "question", "retrycancel",
                "yesno", "yesnocancel",
                "error", "info", "warning"):
        r = tk_function_dict[mode](title, prompt)
    else:
        r = tk_function_dict[mode]()
    pumping = False
    return r

# Create objects

# Constants
# TODO: Make this scale with NATIVE_RESOLUTION
FONT_SIZE = 40
# _ is used as a throw away
_ = pygame.freetype.SysFont("Calibri", FONT_SIZE)
# TODO: Make text.py classes take 3 (x, y, w)
BUTTON_SIZE = (
    0,  # x
    0,  # y
    _.get_rect("|").h * 1.1  # w
)
BUTTON_SEPERATION = _.get_rect("-").w

# Circuit Simulation Tab
# For same size and outside text: FONT_SIZE/(0.6*844)
# 884 is the height of the ANG surface by default
logic_circuit_gui.SCALE = FONT_SIZE / (0.6 * 844)
logic_circuit_gui.COLOR_DICT = {True: BLUE,
                                False: LIGHT_BLUE,
                                None: BLACK,
                                "other": WHITE}
try:
    logic_circuit_gui.load_surfaces()
except FileNotFoundError as e:
    # Close display
    pygame.quit()
    # Cannot use tk_popup_dialogue because we have closed pygame
    tkinter.messagebox.showerror(
        "Error",
        "Cound not find \"" + str(e) + "\"\nPlease reinstall.")
    # Quit program
    from sys import exit
    exit()
# To enable strict AND, OR, NOT only:
# logic_circuit_gui.CircuitBoard.GATE_CLASSES = (logic_circuit_gui.Switch,
# logic_circuit_gui.Bulb,
# logic_circuit_gui.And,
# logic_circuit_gui.Or,
# logic_circuit_gui.Not)
# The size of the main tab:
_ = (0, 0, RESOLUTION[0], RESOLUTION[1] - 2 * BUTTON_SIZE[2])
circuit_simulation = logic_circuit_gui.CircuitBoard(_, hidden=False)
# Move the buttons slightly further away from the left
for b in circuit_simulation.renderable_list:
    b.move((BUTTON_SEPERATION, BUTTON_SEPERATION))


# Boolean Algebra Tab
class BooleanAlgebraContainer(interfaces.IContainer):

    """
    A class for the boolean algebra tab.

    This class allows for the table to be resized and moved about.
    """

    def __init__(self,
                 hitbox,
                 bgcolor=WHITE,
                 hidden=False):
        # The buttons is only visable when there is a valid expression
        def func_simplify(func_self, others, keys, events):
            self.expression = self.expression.eval()
            input_expression.text = str(self.expression)
        self.table_expression = text.TruthTable("A",
                                                (0, 0),
                                                font_size=1.5 * FONT_SIZE)
        self.button_simplify = gui.TextButton("Simplify",
                                              (0, 0),
                                              func_simplify,
                                              font_size=1.5 * FONT_SIZE)
        self.text_expression = text.Expression("A",
                                               (0, 0),
                                               size=2 * FONT_SIZE)
        # So helpful...
        self.text_helpful = text.Text("Enter an expression below...",
                                      (0, 0),
                                      True,
                                      FONT_SIZE * 2,
                                      BLACK,
                                      WHITE)
        super().__init__(hitbox,
                         [self.button_simplify,
                          self.text_expression,
                          self.table_expression,
                          self.text_helpful],
                         hidden,
                         bgcolor)
        # This also needs to be called whenever the display changes size
        self.text_helpful.align((0, 0, self.w, self.h),
                                alignment.middle_middle)
        self.expression = ""

    @property
    def expression(self):
        return self.text_expression.expression

    @expression.setter
    def expression(self, expression):
        # Reset zoom
        self.table_expression.font_size = 1.5 * FONT_SIZE
        if expression == "":
            self.text_expression.hidden = True
            self.table_expression.hidden = True
            self.button_simplify.hidden = True
            self.text_helpful.hidden = False
            # text.Text and text.Table must have a valid expression
            # boolean.Symbol("-") can never be returned by boolean.parse()
            self.text_expression.expression = boolean.Symbol("-")
            self.table_expression.expression = boolean.Symbol("-")
        else:
            self.text_expression.hidden = False
            self.table_expression.hidden = False
            self.button_simplify.hidden = False
            self.text_helpful.hidden = True
            self.text_expression.expression = expression
            self.table_expression.expression = expression
            # The table and the text will most likely change size, so refit
            # their surfaces
            w, h = self.text_expression.fit_surface()
            self.text_expression.w = w
            self.text_expression.h = h
            w, h = self.table_expression.fit_surface()
            self.table_expression.w = w
            self.table_expression.h = h

            self.table_expression.align((0, 0, self.w, self.h),
                                        alignment.bottom_middle)

    def mouse_down(self, others, keys, event, events):
        if event.type in (interfaces.MOUSEBUTTONDOWN_NEW,):
            if self.expression != boolean.Symbol("-"):
                # 4 = scroll wheel up
                # 5 = scroll wheel down
                if event.button in (4, 5):
                    # How much to increase the font size per scroll
                    per_scroll = 5
                    if event.button == 4:
                        self.table_expression.font_size += per_scroll
                    elif event.button == 5:
                        if self.table_expression.font_size - per_scroll > 0:
                            self.table_expression.font_size -= per_scroll
                        else:
                            self.table_expression.font_size = 1
                    center = self.table_expression.hitbox.center
                    w, h = self.table_expression.fit_surface()
                    self.table_expression.w = w
                    self.table_expression.h = h
                    self.table_expression.align(
                        center, alignment.center_center)

                    index = events.index(event)
                    events[index] = interfaces.normal_event(event)
        super().mouse_down(others, keys, event, events)




    # This allows the user to drag the truth table around
    def mouse_motion(self, others, keys, event, events):
        if event.type == interfaces.MOUSEMOTION_NEW:
            if self.selected:
                if not self.button_simplify.selected:
                    self.table_expression.move(event.rel)
                    # Ensure that the table is drawn every frame
                    self.table_expression.dirty = True
        super().mouse_motion(others, keys, event, events)

    def update_renderable_list(self):
        # TODO: Only call this when the expression is changed or the surface size changes
        # Align the button
        self.button_simplify.align((0,
                                    0,
                                    self.w,
                                    self.h - self.table_expression.h),
                                   alignment.top_right)
        # Align the text
        self.text_expression.align((0,
                                    0,
                                    self.w - self.button_simplify.w,
                                    self.h - self.table_expression.h),
                                   alignment.top_middle)
        # Move them down slightly
        self.button_simplify.move((0, BUTTON_SEPERATION))
        self.text_expression.move((0, BUTTON_SEPERATION))
boolean_algebra = BooleanAlgebraContainer(_, WHITE, True)

# Help Tab
# The following is the text and text like stuff that is displyed on the
# help tab
help_list = []
help_list.append(
    text.Text("Boolean expressions\ncan be simplified using\nthe following identities:",
              (0, 0),
              size=FONT_SIZE))
help_list.append(
    text.Text("0∙A = 0",
              (0, 0),
              size=FONT_SIZE))
help_list.append(
    text.Text("1∙A = A",
              (0, 0),
              size=FONT_SIZE))
help_list.append(
    text.Text("A∙A = A",
              (0, 0),
              size=FONT_SIZE))
# This hack allows for a space and equals sign to be rendered in an expression
help_list.append(
    text.Expression(~boolean.Symbol("A") * boolean.Symbol("A = 0"),
                    (0, 0),
                    size=FONT_SIZE))
help_list.append(
    text.Text("0+A = A",
              (0, 0),
              size=FONT_SIZE))
help_list.append(
    text.Text("1+A = 1",
              (0, 0),
              size=FONT_SIZE))
help_list.append(
    text.Text("A+A = A",
              (0, 0),
              size=FONT_SIZE))
help_list.append(
    text.Expression(~boolean.Symbol("A") + boolean.Symbol("A = 1"),
                    (0, 0),
                    size=FONT_SIZE))
help_list.append(
    text.Text("A∙B = B∙A",
              (0, 0),
              size=FONT_SIZE))
help_list.append(
    text.Text("A+B = B+A",
              (0, 0),
              size=FONT_SIZE))
help_list.append(
    text.Text("A∙(B∙C) = A∙B∙C",
              (0, 0),
              size=FONT_SIZE))
help_list.append(
    text.Text("A+(B+C) = A+B+C",
              (0, 0),
              size=FONT_SIZE))
help_list.append(
    text.Text("A∙(B+C) = (A∙B)+(A∙C)",
              (0, 0),
              size=FONT_SIZE))
help_list.append(
    text.Text("A+(B∙C) = (A+B)∙(A+C)",
              (0, 0),
              size=FONT_SIZE))
help_list.append(
    text.Text(("These can be used to\nalgebraically solve\nboolean expressions."),
              (0, 0),
              size=FONT_SIZE))
help_list.append(
    text.Text(("An alternative method is to use a truth table."),
              (0, 0),
              size=FONT_SIZE))
help_list.append(
    text.TruthTable("A*~B*(A+C)",
                    (0, 0),
                    font_size=FONT_SIZE))
help_list.append(
    text.Text(("Here you can clearly see that C has no impact on the\nexpression. By removing it we get:"),
              (0, 0),
              size=FONT_SIZE))
help_list.append(
    text.Expression("A*~B*A",
                    (0, 0),
                    size=FONT_SIZE))
help_list.append(
    text.Expression("A*~B",
                    (0, 0),
                    size=FONT_SIZE))
help_section = interfaces.IContainer(_, help_list, True, WHITE)


# Helper functions
# If buttons need to be dissabled when tabs change it should be done here
def show_boolean():
    circuit_simulation.hidden = True
    boolean_algebra.hidden = False
    help_section.hidden = True


def show_circuit():
    circuit_simulation.hidden = False
    boolean_algebra.hidden = True
    help_section.hidden = True


def show_help():
    circuit_simulation.hidden = True
    boolean_algebra.hidden = True
    help_section.hidden = False


# Clear Button
def func_clear(self, others, keys, events):
    # Only clear the selected window
    if not circuit_simulation.hidden:
        for o in circuit_simulation.renderable_list.copy():
            if isinstance(o, logic_circuit_gui.IRenderableComponent):
                circuit_simulation.renderable_list.remove(o)
                del o
    elif not boolean_algebra.hidden:
        boolean_algebra.expression = ""
button_clear = gui.TextButton("Clear",
                              BUTTON_SIZE,
                              func_clear,
                              font_size=FONT_SIZE)


# Save Button
def func_save(self, others, keys, events):
    if help_section.hidden:
        save_location = tk_popup_dialog("saveasfilename")
        if save_location == "":
            # Assume the user has made a mistake
            return

    # Save the circuit_simulation
    if not circuit_simulation.hidden:
        if save_location.find(".") != -1:
            save_location = save_location[:save_location.find(".")]
        # .lgs stands for logic circuit save
        save_location += ".lgs"

        # TODO: Make boolean.py objects pickeable
        # They can currently be dumped but not loaded
        # This hack saves the expression instead, but can save things twice
        expr_list = []
        for c in (g for g in circuit_simulation.renderable_list
                  if isinstance(g, logic_circuit_gui.Bulb)):
            try:
                expr_list.append(str(logic_circuit_gui.expression(c)))
            except TypeError:
                pass
        with open(save_location, "wb") as f:
            pickle.dump(expr_list, f)
    # Save the expression
    elif not boolean_algebra.hidden:
        if save_location.find(".") != -1:
            save_location = save_location[:save_location.find(".")]
        # Save the expression image with the overbars
        pygame.image.save(boolean_algebra.text_expression.surface,
                          save_location + "_expression.png")
        # Save the table
        pygame.image.save(boolean_algebra.table_expression.surface,
                          save_location + "_table.png")
        # TODO: save the table as a cvs
        # Save the expression as text
        with open(save_location + ".les", "w") as f:
            # .les stands for Logic Expression Save
            f.write(
                str(boolean_algebra.expression)
                .replace(boolean.AND.operator, "*"))
            # By defualt ∙ is used for AND, but this cannot be saved as text
button_save = gui.TextButton("Save",
                             BUTTON_SIZE,
                             func_save,
                             font_size=FONT_SIZE)


# Load Button
def func_load(self, others, keys, events):
    # TODO: make only .lgs and .les files appear
    if help_section.hidden:
        load_location = tk_popup_dialog("openfilename")
        if load_location == "":
            return

    # TODO: accept both .lgs and .les file types for both
    if not circuit_simulation.hidden:
        while not load_location.endswith(".lgs"):
            tk_popup_dialog("error",
                            "Error",
                            "Circuit simulation save files end with \".lgs\".")
            load_location = tk_popup_dialog("openfilename")
            if load_location == "":
                return
        with open(load_location, "rb") as f:
            expr_list = pickle.load(f)

        gates = []
        for expr in expr_list:
            gates += logic_circuit_gui.renderable_components(expr)
        # For now just center them, if renderable_components actually positioned them nicely,
        # then this is not needed
        # This also depends on fixing picking boolean.py objects
        for g in gates:

            g.align((0, 0, circuit_simulation.w, circuit_simulation.h),
                    alignment.middle_middle)

        circuit_simulation.renderable_list += gates
    elif not boolean_algebra.hidden:
        while not load_location.endswith(".les"):
            tk_popup_dialog("error",
                            "Error",
                            "Circuit simulation save files end with \".les\".")
            load_location = tk_popup_dialog("openfilename")
            if load_location == "":
                return
        with open(load_location, "r") as f:
            input_expression.text = f.read()
        try:
            boolean_algebra.expression = input_expression.text
        except TypeError as e:
            tk_popup_dialog("error",
                            "Error",
                            "This expression is not valid.\n" + str(e))
            input_expression.text = input_expression._default_text
            boolean_algebra.expression = ""
button_load = gui.TextButton("Load",
                             BUTTON_SIZE,
                             func_load,
                             font_size=FONT_SIZE)


# These functions have no real use at the moment
# Help Button
def func_help(self, others, keys, events):
    show_help()
button_help = gui.TextButton("Help",
                             BUTTON_SIZE,
                             func_help,
                             font_size=FONT_SIZE)


# Circuit Button
def func_circuit(self, others, keys, events):
    show_circuit()
button_circuit = gui.TextButton("Circuit Simulation",
                                BUTTON_SIZE,
                                func_circuit,
                                font_size=FONT_SIZE)


# Boolean Button
def func_boolean(self, others, keys, events):
    show_boolean()
button_boolean = gui.TextButton("Boolean Algebra",
                                BUTTON_SIZE,
                                func_boolean,
                                font_size=FONT_SIZE)


# to Expression Button
def func_to_expr(self, others, keys, events):
    # Convert a gate to an expression
    if not circuit_simulation.hidden:
        # This actually selects the last bulb that was selected
        for c in (g for g in circuit_simulation.renderable_list
                  if isinstance(g, logic_circuit_gui.Bulb)):
            try:
                input_expression.text = logic_circuit_gui.expression(c)
                break
            except logic_circuit_gui.logic_circuit.RecursionError as e:
                tk_popup_dialog("error",
                                "Error",
                                str(e))
                return
        else:
            # If no bulb is found
            tk_popup_dialog("error",
                            "Error",
                            "There must be 1 bulb which is attached to the circuit you are trying to convert.")
            return
    # Set the expression for the boolean algebra tab
    try:
        boolean_algebra.expression = input_expression.text
    except TypeError as e:
        tk_popup_dialog("error",
                        "Error",
                        "This expression is not valid.\n" + str(e))
        boolean_algebra.expression = ""
        return
    show_boolean()
button_to_expr = gui.TextButton("Convert to Expression",
                                BUTTON_SIZE,
                                func_to_expr,
                                font_size=FONT_SIZE)


# to Gate Button
def func_to_gate(self, others, keys, events):
    try:
        gates = logic_circuit_gui.renderable_components(input_expression.text)
    except TypeError as e:
        tk_popup_dialog("error",
                        "Error",
                        "Unable to convert expression into a logic circuit\n" + str(e))
        return
    # For now just center them, if renderable_components actually positioned them nicely,
    # then this is not needed
    for g in gates:
        g.align((0, 0, circuit_simulation.w, circuit_simulation.h),
                alignment.bottom_right)
    circuit_simulation.renderable_list += gates
    show_circuit()
button_to_circuit = gui.TextButton("Convert to Circuit",
                                   BUTTON_SIZE,
                                   func_to_gate,
                                   font_size=FONT_SIZE)


# Expression InputBox
class ExpressionBox(gui.InputBox):

    """
    An input box that only takes values that can be conveted into expression.

    This also adds the ability to cut, copy and paste using keybord shortcuts.
    """

    def __init__(self,
                 default_text,
                 hitbox,
                 hidden=False,
                 font_size=50,
                 fgcolor=pygame.color.THECOLORS["black"],
                 bgcolor=pygame.color.THECOLORS["white"],
                 underline=False,
                 strong=False,
                 oblique=False,
                 name="Calibri",):
        super().__init__(default_text,
                         hitbox,
                         hidden,
                         font_size,
                         fgcolor,
                         bgcolor,
                         underline,
                         strong,
                         oblique,
                         name)
        self.allowed_characters = ("ABCDEFGHIKJLMNOPQRSTUVWXYZ"
                                   "abcdefghijklmnopqrstuvwxyz"
                                   "1234567890"
                                   "()~¬!'*∙.^∧+∨ ")

    def update_surface(self):
        # As text creates a surface howeer long it needs, if it gets too long
        # then it will thrown an error
        # I think the size depends on the computer's memory
        try:
            super().update_surface()
        except pygame.error as error:
            if str(error) != "Width or height is too large":
                raise
            tk_popup_dialog(
                "error", "Error", "You have entered too much text.")
            self.text = ""
            super().update_surface()

    # The following features could be added to gui.py but they require pygame.scrap,
    # for which the init function can only be called after you have set the display mode.
    # A possible solution is to create an init function inside gui.py which must be called
    # before any of the classes can be used.
    def clipboard_copy(self):
        b = bytes(self.text, "utf-8")
        pygame.scrap.put(pygame.SCRAP_TEXT, b)

    def clipboard_paste(self):
        def allowed(char):
            return char in self.allowed_characters

        s = pygame.scrap.get(pygame.SCRAP_TEXT)
        if s is not None:
            s = s.decode("utf-8")
            if all(allowed(c) for c in s):
                self.text += s

    def clipboard_cut(self):
        self.clipboard_copy()
        self.text = ""

    def while_selected(self, others, keys, events):
        for event in (e for e in events
                      if e.type in (interfaces.KEYDOWN_NEW,)):
            if event.mod == pygame.KMOD_LCTRL:
                if event.key == pygame.K_c:
                    self.clipboard_copy()
                elif event.key == pygame.K_x:
                    self.clipboard_cut()
                elif event.key == pygame.K_v:
                    self.clipboard_paste()
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_DELETE:
                self.text = ""
            elif event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                self.selected = False
            elif event.unicode in self.allowed_characters:
                self.text = self.text + event.unicode

            index = events.index(event)
            events[index] = interfaces.normal_event(event)

    def on_deselect(self, others, keys, events):
        super().on_deselect(others, keys, events)
        try:
            self.text = str(boolean.parse(self.text, False))
        except TypeError:
            pass

    def mouse_down(self, others, keys, event, events):
        # This adds right click to delete and middle click to copy,
        # which is the same controls as for the logic gates gui
        if event.type == interfaces.MOUSEBUTTONDOWN_NEW:
            if self.hitbox.collidepoint(event.pos):
                if event.button == 3:
                    self.text = ""
                if event.button == 2:
                    self.clipboard_copy()
            else:
                self.selected = False
        super().mouse_down(others, keys, event, events)
_ = (0,
     0,
     RESOLUTION[0] - button_to_circuit.w -
     button_to_expr.w - 2 * BUTTON_SEPERATION,
     BUTTON_SIZE[2])
input_expression = ExpressionBox("Enter a boolean expression...",
                                 _,
                                font_size=FONT_SIZE)

# All objects that are rendered and and updated
objects = [circuit_simulation]

    #[button_clear, button_save, button_load,
    #       button_help, button_circuit, button_boolean,
    #       button_to_expr, button_to_circuit, input_expression,
    #       circuit_simulation, boolean_algebra, help_section]

"""
Modifizierter Code
"""
def GenerateXML(foldername, filename, widthtext, heighttext, depthtext, objs):
    pathname = os.getcwd() + "\\" + os.path.join('images',  'mixed',
                                                 filename + '.jpg')
    root = minidom.Document()
    xml = root.createElement('annotation')
    root.appendChild(xml)
    productChild = root.createElement('folder')
    text = root.createTextNode(foldername)
    productChild.appendChild(text)
    xml.appendChild(productChild)
    productChild = root.createElement('filename')
    text = root.createTextNode(filename + '.jpg')
    productChild.appendChild(text)
    xml.appendChild(productChild)
    productChild = root.createElement('path')
    text = root.createTextNode(pathname)
    productChild.appendChild(text)
    xml.appendChild(productChild)
    productChild = root.createElement('source')
    productChild1 = root.createElement('database')
    text = root.createTextNode("Unknown")
    productChild.appendChild(productChild1)
    productChild1.appendChild(text)
    xml.appendChild(productChild)
    productChild = root.createElement('size')
    productChild1 = root.createElement('width')
    text = root.createTextNode(str(widthtext))
    productChild.appendChild(productChild1)
    productChild1.appendChild(text)
    productChild1 = root.createElement('height')
    text = root.createTextNode(str(heighttext))
    productChild.appendChild(productChild1)
    productChild1.appendChild(text)
    productChild1 = root.createElement('depth')
    text = root.createTextNode(str(depthtext))
    productChild.appendChild(productChild1)
    productChild1.appendChild(text)
    xml.appendChild(productChild)
    productChild = root.createElement('segmented')
    text = root.createTextNode("0")
    productChild.appendChild(text)
    xml.appendChild(productChild)
    for obj in objs:
        if not type(obj) ==logic_circuit_gui.SpawnGate and not type(obj) ==logic_circuit_gui.Wire:
            productChild = root.createElement('object')
            productChild1 = root.createElement('name')
            if type(obj) ==logic_circuit_gui.Switch:
                text = root.createTextNode(str(obj.surface_key[None])+ "_" + str(obj.component.output))
            else:
                text = root.createTextNode(str(obj.surface_key[None]))
            productChild.appendChild(productChild1)
            productChild1.appendChild(text)
            productChild1 = root.createElement('pose')
            text = root.createTextNode("Unspecified")
            productChild.appendChild(productChild1)
            productChild1.appendChild(text)
            productChild1 = root.createElement('truncated')
            text = root.createTextNode("0")
            productChild.appendChild(productChild1)
            productChild1.appendChild(text)
            productChild1 = root.createElement('difficult')
            text = root.createTextNode("0")
            productChild.appendChild(productChild1)
            productChild1.appendChild(text)
            xml.appendChild(productChild)
            productChild1 = root.createElement('bndbox')
            productChild.appendChild(productChild1)
            productChild2 = root.createElement('xmin')
            text = root.createTextNode(str(obj.hitbox.x))
            productChild1.appendChild(productChild2)
            productChild2.appendChild(text)
            productChild2 = root.createElement('ymin')
            text = root.createTextNode(str(obj.hitbox.y))
            productChild1.appendChild(productChild2)
            productChild2.appendChild(text)
            productChild2 = root.createElement('xmax')
            text = root.createTextNode(str(obj.hitbox.right))
            productChild1.appendChild(productChild2)
            productChild2.appendChild(text)
            productChild2 = root.createElement('ymax')
            text = root.createTextNode(str(obj.hitbox.bottom))
            productChild1.appendChild(productChild2)
            productChild2.appendChild(text)
            xml.appendChild(productChild)

    xml_str = root.childNodes[0].toprettyxml(indent="\t")

    with open(os.path.join('images',  'mixed', filename + ".xml"),
              "w") as f:
        f.write(xml_str)



running = True
while running:
    # Pre Update
    keys = pygame.key.get_pressed()
    events = interfaces.new_events(pygame.fastevent.get())

    for e in events:

        """
        Modifizierter Code
        """
        if e.type == pygame.TEXTINPUT:
            if e.text == 'a':
                jpgname = uuid.uuid4()
                #GenerateXML("Mixed", str(jpgname),RESOLUTION[0],RESOLUTION[1],3,circuit_simulation.renderable_list)

                #pygame.image.save(surface, "images/mixed/" + str(jpgname) + ".jpg")
                if not os.path.exists("../BachelorAbgabe/images/" + str(jpgname)):
                     #TODO Check linux
                    if os.name == 'posix':
                        os.mkdir("../BachelorAbgabe/images/" + str(jpgname))
                    if os.name == 'nt':
                        os.mkdir("../BachelorAbgabe/images/" + str(jpgname))
                pygame.image.save(surface, "../BachelorAbgabe/images/" + str(jpgname) +  "/" + str(jpgname) +".jpg")
                print(circuit_simulation.renderable_list)
                print(jpgname)

        if e.type == pygame.TEXTINPUT:
            if e.text == 'h':
                # if not logic_circuit_gui.SELECT_RADIUS == 0:
                #     logic_circuit_gui.SELECT_RADIUS = 0
                # else:
                #     logic_circuit_gui.SELECT_RADIUS = 7
                for g in circuit_simulation.renderable_list:
                    if type(g) == logic_circuit_gui.SpawnGate:
                        #print("!!!!!")
                        #print(g)
                        g.hidden = not g.hidden
        if e.type == pygame.TEXTINPUT:
            if e.text == 'c':
                print(circuit_simulation.renderable_list)

        """
        Ende Modifizierter Code
        """






        if e.type == pygame.QUIT:
            running = False
        elif e.type in (pygame.KEYDOWN, interfaces.KEYDOWN_NEW):
            if e.key == pygame.K_F4 and e.mod == pygame.KMOD_LALT:
                running = False
            elif e.key == pygame.K_ESCAPE:
                running = False
        elif e.type == pygame.VIDEORESIZE:
            # This is called when the display is created
            # The following aligns, which is why the display can be resized
            RESOLUTION = e.size
            surface = pygame.display.set_mode(RESOLUTION, FLAGS)

            _ = pygame.rect.Rect(
                0, 0, RESOLUTION[0], RESOLUTION[1] - 2 * BUTTON_SIZE[2])
            circuit_simulation.hitbox = _
            circuit_simulation.dirty = True
            circuit_simulation.align(
                (0, 0) + RESOLUTION, alignment.middle_middle)

            boolean_algebra.hitbox = _
            boolean_algebra.dirty = True
            boolean_algebra.table_expression.align((0, 0,  boolean_algebra.w,  boolean_algebra.h),
                                                   alignment.bottom_middle)
            boolean_algebra.text_helpful.align((0, 0, boolean_algebra.w, boolean_algebra.h),
                                               alignment.middle_middle)
            boolean_algebra.align((0, 0) + RESOLUTION, alignment.middle_middle)

            help_section.hitbox = _
            help_section.align((0, 0) + RESOLUTION, alignment.middle_middle)
            help_section.renderable_list[0].align(
                (0, 0, help_section.w, help_section.h), alignment.top_left)
            help_section.renderable_list[0].move(
                (BUTTON_SEPERATION, BUTTON_SEPERATION))
            help_section.renderable_list[1].align(
                help_section.renderable_list[0].hitbox.bottomleft, alignment.top_left)
            help_section.renderable_list[1].move((0, BUTTON_SEPERATION))
            help_section.renderable_list[2].align(
                help_section.renderable_list[1].hitbox.bottomleft, alignment.top_left)
            help_section.renderable_list[2].move((0, BUTTON_SEPERATION))
            help_section.renderable_list[3].align(
                help_section.renderable_list[2].hitbox.bottomleft, alignment.top_left)
            help_section.renderable_list[3].move((0, BUTTON_SEPERATION))
            help_section.renderable_list[4].align(
                help_section.renderable_list[3].hitbox.bottomleft, alignment.top_left)
            help_section.renderable_list[4].move((0, BUTTON_SEPERATION))
            help_section.renderable_list[5].align(
                help_section.renderable_list[0].hitbox.bottomright, alignment.top_right)
            help_section.renderable_list[5].move((0, BUTTON_SEPERATION))
            help_section.renderable_list[6].align(
                help_section.renderable_list[5].hitbox.bottomright, alignment.top_right)
            help_section.renderable_list[6].move((0, BUTTON_SEPERATION))
            help_section.renderable_list[7].align(
                help_section.renderable_list[6].hitbox.bottomright, alignment.top_right)
            help_section.renderable_list[7].move((0, BUTTON_SEPERATION))
            help_section.renderable_list[8].align(
                help_section.renderable_list[7].hitbox.bottomright, alignment.top_right)
            help_section.renderable_list[8].move((0, BUTTON_SEPERATION))
            help_section.renderable_list[9].align(
                help_section.renderable_list[
                    4].hitbox.bottomleft + (help_section.renderable_list[0].w, 0),
                alignment.top_center)
            help_section.renderable_list[9].move((0, BUTTON_SEPERATION))
            help_section.renderable_list[10].align(
                help_section.renderable_list[
                    9].hitbox.bottomleft + (help_section.renderable_list[9].w, 0),
                alignment.top_center)
            help_section.renderable_list[10].move((0, BUTTON_SEPERATION))
            help_section.renderable_list[11].align(
                help_section.renderable_list[
                    10].hitbox.bottomleft + (help_section.renderable_list[10].w, 0),
                alignment.top_center)
            help_section.renderable_list[11].move((0, BUTTON_SEPERATION))
            help_section.renderable_list[12].align(
                help_section.renderable_list[
                    11].hitbox.bottomleft + (help_section.renderable_list[11].w, 0),
                alignment.top_center)
            help_section.renderable_list[12].move((0, BUTTON_SEPERATION))
            help_section.renderable_list[13].align(
                help_section.renderable_list[
                    12].hitbox.bottomleft + (help_section.renderable_list[12].w, 0),
                alignment.top_center)
            help_section.renderable_list[13].move((0, BUTTON_SEPERATION))
            help_section.renderable_list[14].align(
                help_section.renderable_list[
                    13].hitbox.bottomleft + (help_section.renderable_list[13].w, 0),
                alignment.top_center)
            help_section.renderable_list[14].move((0, BUTTON_SEPERATION))
            help_section.renderable_list[15].align(
                (help_section.renderable_list[
                 0].x, help_section.renderable_list[14].hitbox.bottomleft[1]),
                alignment.top_left)
            help_section.renderable_list[15].move((0, BUTTON_SEPERATION))
            help_section.renderable_list[16].align(
                (0, 0, help_section.w, help_section.h), alignment.top_right)
            help_section.renderable_list[16].move(
                (-BUTTON_SEPERATION, +BUTTON_SEPERATION))
            help_section.renderable_list[17].align(
                help_section.renderable_list[16].hitbox.bottomright, alignment.top_right)
            help_section.renderable_list[17].move((0, BUTTON_SEPERATION))
            help_section.renderable_list[18].align(
                help_section.renderable_list[17].hitbox.bottomright, alignment.top_right)
            help_section.renderable_list[18].move((0, BUTTON_SEPERATION))
            help_section.renderable_list[19].align(
                help_section.renderable_list[
                    18].hitbox.bottomleft + (help_section.renderable_list[18].w, 0),
                alignment.top_middle)
            help_section.renderable_list[19].move((0, BUTTON_SEPERATION))
            help_section.renderable_list[20].align(
                help_section.renderable_list[
                    19].hitbox.bottomleft + (help_section.renderable_list[19].w, 0),
                alignment.top_middle)
            help_section.renderable_list[20].move((0, BUTTON_SEPERATION))
            help_section.dirty = True

            button_clear.align((0, 0) + RESOLUTION, alignment.top_left)

            button_save.align(
                button_clear.hitbox.midright, alignment.middle_left)
            button_save.move((BUTTON_SEPERATION, 0))

            button_load.align(
                button_save.hitbox.midright, alignment.middle_left)
            button_load.move((BUTTON_SEPERATION, 0))

            button_help.align((0, 0) + RESOLUTION, alignment.top_right)

            button_circuit.align(
                button_help.hitbox.midleft, alignment.middle_right)
            button_circuit.move((-BUTTON_SEPERATION, 0))

            button_boolean.align(
                button_circuit.hitbox.midleft, alignment.middle_right)
            button_boolean.move((-BUTTON_SEPERATION, 0))

            button_to_expr.align((0, 0) + RESOLUTION, alignment.bottom_right)

            button_to_circuit.align(
                button_to_expr.hitbox.bottomleft, alignment.bottom_right)
            button_to_circuit.move((-BUTTON_SEPERATION, 0))

            _ = pygame.rect.Rect(0,
                                 0,
                                 RESOLUTION[
                                     0] - button_to_circuit.w - button_to_expr.w - 2 * BUTTON_SEPERATION,
                                 BUTTON_SIZE[2])
            input_expression.hitbox = _
            input_expression.dirty = True
            input_expression.align((0, 0) + RESOLUTION, alignment.bottom_left)

    # Update
    for o in objects:
        o.update(objects, keys, events)

    # Render
    surface.fill(WHITE)
    surface_blit = surface.blit
    for o in reversed(objects):
        surface_blit(o.render_surface(), o.top_left)

# This displays the fps
# pygame.freetype.SysFont(
#        "Calibri", 30
# ).render_to(
# surface,
#            (0, 0),
#            str(round(clock.get_fps(), 3)),
# BLACK,
# pygame.color.Color("lightgray"))

    # TODO: Add hitboxes for all objects before and after update and call
    # pygame.display.flip(hitboxes) instead
    pygame.display.flip()

    # Post Render
    clock.tick(FPS)

# TODO: Consider saving the circuit simulation tab to be reloaded
pygame.quit()
