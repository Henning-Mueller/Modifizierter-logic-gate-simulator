"""
This module creates a visual element to logic circuits.
"""
import math

import pygame
import pygame.gfxdraw

import boolean
import logic_circuit

import alignment
import interfaces
import gui

# How much the images are scaled
SCALE = 0.1
# The colors that are used, the colors for the bulb itself it taken from
# the images
COLOR_DICT = {True: pygame.color.Color(0, 0, 255, 255),
              False: pygame.color.Color(0, 255, 255, 255),
              None: pygame.color.Color(0, 0, 0, 255),
              "other": pygame.color.Color(255, 255, 255, 255)}

# Converting cannot be done unless a video mode has been set
# Currently is just doesn't convert the surface
# TODO: Raise error if the video mode has not been set


def load_surfaces(path="images"):
    """
    This should be called before creating any instances of classes or after changing
    the SCALE or COLOR_DICT.
    """
    def load_file_to_surface(file_name):
        """
        Takes a filename and returns the surface of the file. 

        This raises a FileNotFoundError if the file could not be opened.
        """
        try:
            raw = pygame.image.load(file_name)
            raw_rect = raw.get_rect()
            final_rect = (int(raw_rect.w * SCALE), int(raw_rect.h * SCALE))
            surf = pygame.transform.smoothscale(raw, final_rect)
            if pygame.display.get_surface() is not None:
                surf = surf.convert_alpha()
            return surf
        except pygame.error as e:
            if str(e) == "Couldn't open " + file_name:
                raise FileNotFoundError(file_name)
            else:
                raise

    global SURFACE
    global SELECT_RADIUS

    # A dictionary mapping the following strings to surfaces
    SURFACE = {}
    # A list of all files that can be loaded
    files = ("and", "or", "not",
             "nand", "nor", "repeater",
             "bulb", "bulb_on", "bulb_off",
             "switch", "switch_on", "switch_off")
    for f in files:
        s = load_file_to_surface(path + "\\" + f + ".png")
        SURFACE[f] = s

    # 0.825/30.939 is the ratio of the height of the and surface to the radius
    # of the circle
    SELECT_RADIUS = int(
        4 * SURFACE["and"].get_rect().h * 0.0266654)  # 0.825/30.939


class IRenderableComponent(interfaces.IDraggable):

    """
    Base class for all renderable components.
    """

    def __init__(self,
                 pos,
                 hidden=False,
                 component=None):
        self.component = component
        rect = SURFACE[self.surface_key[self.component.output]].get_rect()
        hitbox = pos + (rect.w, rect.h)
        super().__init__(hitbox,
                         hidden)

        # Maps a position (x, y) to a Symbol
        # pygame.math.Vector2s cannot be hashed
        self.inputs = {}
        # A pygame.math.Vector2 of the position of the output
        self.output = pygame.math.Vector2(self.w - SELECT_RADIUS, self.h / 2)

    # Dictionary mapping the value of the output to a surface.
    # This is used for components that change their surface when their output
    # changes
    @property
    def surface_key(self):
        return {True: self.__class__.__name__.lower(),
                False: self.__class__.__name__.lower(),
                None: self.__class__.__name__.lower()}

    def update(self, others, keys, events):
        super().update(others, keys, events)
        old_output = self.component.output
        self.component.update()
        if old_output is not self.component.output:
            self.dirty = True

    def on_select(self, others, keys, events):
        interfaces.IDraggable.on_select(self, others, keys, events)

        # Gets mouse button down event that selected this object
        for event in events:
            if event.type in (pygame.MOUSEBUTTONDOWN, ):
                break

        # All values inside of this class are relative to the top left
        pos = (event.pos[0] - self.x, event.pos[1] - self.y)
        # Snap to input
        if self.output.distance_squared_to(pos) < SELECT_RADIUS ** 2:
            self.output_clicked(others, keys, event, events)
            index = events.index(event)
            events[index] = interfaces.new_event(event)
        # The pixel that has been clicked on is transparent
        elif self.surface.get_at(pos)[3] == 0 or\
                self.surface.get_at(pos) == self.surface.get_colorkey():  # transparent
            self.selected = False
            index = events.index(event)
            events[index] = interfaces.new_event(event)

    def output_clicked(self, others, keys, event, events):
        # Output is a pygame.math.Vector2 and Vector2 addition is the same as
        # (v1[0]+v2[0, v1[1]+v2[1])
        input_pos = tuple(self.output + self.top_left)
        # Wire output is at the mouse
        output_pos = event.pos
        wire = Wire(input_pos, output_pos, input_component=self.component)
        wire.dragging = True
        self.selected = False
        others.append(wire)

    def mouse_down(self, others, keys, event, events):
        if event.type == interfaces.MOUSEBUTTONDOWN_NEW:
            if self.hitbox.collidepoint(event.pos):
                # Middle click to copy
                if event.button == 2:
                    # Shift the new object by a bit so that it is obvious
                    # that you have copied the object
                    new_self = self.__class__(
                        pos=(self.top_left[0] + SELECT_RADIUS / 2,
                             self.top_left[1] + SELECT_RADIUS / 2))
                    new_self.selected = True
                    self.selected = False
                    others.insert(0, new_self)

                    index = events.index(event)
                    events[index] = interfaces.normal_event(event)
                # Right click to delete
                elif event.button == 3:
                    board = list(o.component for o in others
                                 if isinstance(o, IRenderableComponent))
                    # Remove the components that contain wires that use us as an
                    # output
                    for o in (other for other in others.copy()
                              if other is not self
                              and isinstance(other, Wire)):
                        if self.component in o.component:
                            o.component.remove(board)
                            others.remove(o)
                            del o

                    # Remove ourself from any components
                    self.component.remove(board)
                    others.remove(self)

                    index = events.index(event)
                    events[index] = interfaces.normal_event(event)

                    return
        super().mouse_down(others, keys, event, events)

    def update_surface(self):
        # We're going to be drawing on the surface so make a copy
        self.surface = SURFACE[self.surface_key[self.component.output]].copy()

        # Removes a circle at the output
        # This is because the output is slightly inside of the component
        pygame.gfxdraw.filled_circle(self.surface,
                                     int(self.w),
                                     int(self.h / 2),
                                     SELECT_RADIUS,
                                     pygame.color.Color(0, 0, 0, 0))
        # Draws a small filled circle at the output
        pygame.draw.circle(self.surface,
                           COLOR_DICT[self.component.output],
                           (int(self.output[0]), int(self.output[1])),
                           int(SELECT_RADIUS / 2))
        # DEBUG CODE
        # Draws a small circle around the collision detection area of the
        # output
        pygame.gfxdraw.circle(self.surface,
                              int(self.output[0] - 1),
                              int(self.output[1]),
                              SELECT_RADIUS,
                              COLOR_DICT[self.component.output])

        # Draws circles for the output in the same way as the input
        for input in self.inputs.keys():
            pygame.gfxdraw.filled_circle(self.surface,
                                         0,
                                         int(input[1]),
                                         SELECT_RADIUS,
                                         pygame.color.Color(0, 0, 0, 0))
            pygame.draw.circle(self.surface,
                               COLOR_DICT[self.component.output],
                               (int(input[0]), int(input[1])),
                               int(SELECT_RADIUS / 2))
            # DEBUG CODE
            # The same but for the output
            pygame.gfxdraw.circle(self.surface,
                                  int(input[0]),
                                  int(input[1]),
                                  SELECT_RADIUS,
                                  COLOR_DICT[self.component.output])


class DualBaseGate(IRenderableComponent):

    """
    A gate that takes 2 inputs.
    """

    def __init__(self,
                 pos,
                 dual_expression,
                 hidden=False,
                 anonymous_symbols=True):
        if isinstance(dual_expression, str):
            dual_expression = boolean.parse(dual_expression)
        if not isinstance(dual_expression, boolean.Function):
            raise TypeError("Argument must be str or Function but it is {}"
                            .format(dual_expression.__class__))
        if len(dual_expression.symbols) != 2:
            raise ValueError("Argument must only contain two symbols but contains {}"
                             .format(len(dual_expression.symbols)))

        component = logic_circuit.Gate(dual_expression,
                                       anonymous_symbols=anonymous_symbols)
        super().__init__(pos, hidden, component)

        input_symbols = tuple(k for k, v in self.component.inputs.items())

        # Comments are the maths behind the ratio for where the inputs are
        # (30.939-(22.482+0.825/2))*self.h/30.939
        top_input_y = int(0.260012 * self.h)
        # (30.939-(7.633+0.825/2))*self.h/30.939
        botton_input_y = math.ceil(0.739956 * self.h)

        self.inputs[(SELECT_RADIUS, top_input_y)] = input_symbols[0]
        self.inputs[(SELECT_RADIUS, botton_input_y)] = input_symbols[1]


# These classes need to be called the same name (ignoring capitals) as the files
# for their surface
class And(DualBaseGate):

    def __init__(self,
                 pos,
                 hidden=False,
                 anonymous_symbols=True):
        dual_expression = boolean.AND(
            boolean.Symbol(None), boolean.Symbol(None))
        super().__init__(pos, dual_expression, hidden, anonymous_symbols)


class Or(DualBaseGate):

    def __init__(self,
                 pos,
                 hidden=False,
                 anonymous_symbols=True):
        dual_expression = boolean.OR(
            boolean.Symbol(None), boolean.Symbol(None))
        super().__init__(pos, dual_expression, hidden, anonymous_symbols)


class Nand(DualBaseGate):

    def __init__(self,
                 pos,
                 hidden=False,
                 anonymous_symbols=True):
        dual_expression = boolean.NOT(
            boolean.AND(boolean.Symbol(None), boolean.Symbol(None)))
        super().__init__(pos, dual_expression, hidden, anonymous_symbols)


class Nor(DualBaseGate):

    def __init__(self,
                 pos,
                 hidden=False,
                 anonymous_symbols=True):
        dual_expression = boolean.NOT(
            boolean.OR(boolean.Symbol(None), boolean.Symbol(None)))
        super().__init__(pos, dual_expression, hidden, anonymous_symbols)


# Not only has 1 input
class Not(IRenderableComponent):

    def __init__(self,
                 pos,
                 input_component=None,
                 hidden=False,
                 anonymous_symbols=True):
        component = logic_circuit.Not(input_component, anonymous_symbols)
        super().__init__(pos, hidden, component)

        input_symbols = tuple(k for k, v in self.component.inputs.items())
        self.inputs[(SELECT_RADIUS, self.h / 2)] = input_symbols[0]
        self.output = pygame.math.Vector2(self.w - SELECT_RADIUS, self.h / 2)

    @property
    def input(self):
        return tuple(self.inputs.keys())[0]


class InputOutputCommon(IRenderableComponent):

    @property
    def surface_key(self):
        return {True: self.__class__.__name__.lower() + "_on",
                False: self.__class__.__name__.lower() + "_off",
                None: self.__class__.__name__.lower()}


class Switch(InputOutputCommon):

    def __init__(self,
                 pos,
                 hidden=False,
                 output=False):
        component = logic_circuit.Switch(output)
        super().__init__(pos, hidden, component)
        # self.inputs = {} by default
        # therefore iterating through self.inputs.keys() doesn't run any code

    def on_select(self, others, keys, events):
        interfaces.IDraggable.on_select(self, others, keys, events)

        for event in events:
            if event.type in (pygame.MOUSEBUTTONDOWN, ):
                break

        # Exactly the same as all other components except...
        pos = (event.pos[0] - self.x, event.pos[1] - self.y)
        if self.output.distance_squared_to(pos) < SELECT_RADIUS ** 2:
            self.output_clicked(others, keys, event, events)
            index = events.index(event)
            events[index] = interfaces.new_event(event)
        elif self.surface.get_at(pos)[3] == 0 or\
                self.surface.get_at(pos) == self.surface.get_colorkey():  # transparent
            self.selected = False
            index = events.index(event)
            events[index] = interfaces.new_event(event)
        else:
            # If you've clicked on them then you toggle their output
            # TODO: Do not toggle output until you have clicked on them twice
            self.component.press()
            self.dirty = True


class Bulb(InputOutputCommon):

    def __init__(self,
                 pos,
                 input_component=None,
                 hidden=False):
        component = logic_circuit.Bulb(input_component)
        super().__init__(pos, hidden, component)
        self.output = None
        self.inputs[(SELECT_RADIUS, self.h / 2)] = self.component.expression

    @property
    def input(self):
        return tuple(self.inputs.keys())[0]

    def on_select(self, others, keys, events):
        interfaces.IDraggable.on_select(self, others, keys, events)

        for event in events:
            if event.type in (pygame.MOUSEBUTTONDOWN, ):
                break

        # Bulbs can only be moved around
        pos = (event.pos[0] - self.x, event.pos[1] - self.y)
        if self.surface.get_at(pos)[3] == 0 or\
                self.surface.get_at(pos) == self.surface.get_colorkey():  # transparent
            self.selected = False
            index = events.index(event)
            events[index] = interfaces.new_event(event)

    def update_surface(self):
        self.surface = SURFACE[self.surface_key[self.component.output]]

        # Draw the input, which there is only 1 of for the bulb
        pygame.gfxdraw.filled_circle(self.surface,
                                     int(0),
                                     int(self.input[1]),
                                     SELECT_RADIUS,
                                     pygame.color.Color(0, 0, 0, 0))
        pygame.draw.circle(self.surface,
                           COLOR_DICT[self.component.output],
                           (int(self.input[0]), int(self.input[1])),
                           int(SELECT_RADIUS / 2))
        # DEBUG CODE
        pygame.gfxdraw.circle(self.surface,
                              int(self.input[0]),
                              int(self.input[1]),
                              SELECT_RADIUS,
                              COLOR_DICT[self.component.output])


class Wire(IRenderableComponent):

    """
    A wire.

    Wires connect components together.

    Unlike other renderable objects, wires are given a surface to draw on as they often
    cover the entire display.
    """

    def __init__(self,
                 input_pos,
                 output_pos,
                 input_component=None,
                 hidden=False,
                 surface=None):
        # Defaults to getting the main display for rendering on.
        if surface is None:
            surface = pygame.display.get_surface()
        rect = surface.get_rect()
        interfaces.IDraggable.__init__(self, rect, hidden)

        self.surface = surface
        self.component = logic_circuit.Wire(input_component)
        self.inputs = {input_pos: self.component.input}
        self.output = pygame.math.Vector2(output_pos)

    @property
    def input(self):
        return tuple(self.inputs.keys())[0]

    # This is never used by the class itself
    # It is kept in case something in the future uses surface_keys
    @property
    def surface_key(self):
        return {}

    # When a wire is being dragged, the output position follows the mouse
    @property
    def dragging(self):
        return self._dragging

    @dragging.setter
    def dragging(self, dragging):
        self._dragging = bool(dragging)
        self.selected = dragging
        self.dirty = True

    def update(self, others, keys, events):
        for o in (other for other in others
                  if other is not self
                  and isinstance(other, IRenderableComponent)):
            if self.component in o.component:
                # Calculate the input position of the component that this wire
                # is connected to
                reverse_dict = {v: k for k, v in o.component.inputs.items()}
                key = reverse_dict[self.component]
                reverse_dict = {v: k for k, v in o.inputs.items()}
                # Sets the output pos of the wire to the input pos of the
                # component
                self.output = pygame.math.Vector2(reverse_dict[key])
                self.output += o.top_left
            if o.component is self.component.input:
                # Do the same for the input pos of this wire, this is much
                # easier as components only have one output
                input_pos = o.top_left[0] + \
                    o.output[0], o.top_left[1] + o.output[1]
                self.inputs = {
                    tuple(input_pos): tuple(self.inputs.values())[0]}
        super().update(others, keys, events)

    def mouse_down(self, others, keys, event, events):
        if event.type == interfaces.MOUSEBUTTONDOWN_NEW:
            if self.output.distance_squared_to(event.pos) < SELECT_RADIUS ** 2:
                # Middle click to copy
                if event.button == 2:
                    # Find the component that this wire is connected to
                    for other in (o for o in others if o is not self):
                        if other.component in self.component:
                            input_component = other.component
                            break
                    else:
                        # The wire is not connected to something
                        # This shouldn't happen if the wire is spawned by a
                        # gate
                        return
                    new_self = self.__class__(
                        input_pos=self.input,
                        output_pos=event.pos,
                        input_component=input_component,
                        surface=self.surface)
                    self.selected = False
                    new_self.dragging = True
                    others.insert(0, new_self)

                    index = events.index(event)
                    events[index] = interfaces.normal_event(event)
                # Right click to delete
                elif event.button == 3:
                    board = list(o.component for o in others
                                 if isinstance(o, IRenderableComponent))
                    self.component.remove(board)
                    others.remove(self)

                    index = events.index(event)
                    events[index] = interfaces.normal_event(event)
                    return
        interfaces.IDraggable.mouse_down(self, others, keys, event, events)

    def while_selected(self, others, keys, events):
        mouse_motion_events = (e for e in events
                               if e.type in (interfaces.MOUSEMOTION_NEW,)
                               and e.buttons[0])
        for event in mouse_motion_events:
            # Instead of moving the entire object like normal draggable objects
            # Make the output position into the event position
            self.output = pygame.math.Vector2(event.pos)
            self.dragging = True

    def on_select(self, others, keys, events):
        # The surface of the wire is the same as the entire surface
        interfaces.IDraggable.on_select(self, others, keys, events)

        for event in events:
            if event.type in (pygame.MOUSEBUTTONDOWN, ):
                break

        pos = (event.pos[0] - self.x, event.pos[1] - self.y)
        if self.output.distance_squared_to(pos) < SELECT_RADIUS ** 2:
            # Because the surface of a wire is the entire surface
            # We need to only be selected when we click near the output
            self.output_clicked(others, keys, event, events)
            # TODO: Check this code
            index = events.index(event)
            events[index] = interfaces.new_event(event)
        else:
            # So if we haven't clicked next to the output, then we should
            # deselect ourselves
            self.selected = False
            index = events.index(event)
            events[index] = interfaces.new_event(event)

    def on_deselect(self, others, keys, events):
        for o in (other for other in others
                  if other is not self
                  and isinstance(other, IRenderableComponent)
                  and not isinstance(other, self.__class__)):  # Don't connect to wires
            for p in o.inputs.keys():
                pos = (p[0] + o.x, p[1] + o.y)
                if self.output.distance_squared_to(pos) < (SELECT_RADIUS * 2) ** 2:
                    self.output = pygame.math.Vector2(pos)
                    # Break current connection
                    # This should never need to be called if the wire is part of a
                    # RenderableCircuitBoard
                    for ot in (other for other in others
                               if other is not self
                               and isinstance(other, IRenderableComponent)):
                        if ot.component == o.component.inputs[o.inputs[p]]:
                            board = list(o.component for o in others
                                         if isinstance(o, IRenderableComponent))
                            ot.component.remove(board)
                            others.remove(ot)
                            break
                    o.component.inputs[o.inputs[p]] = self.component
                    # Consider rethinking the loops to avoid this
                    super().on_deselect(others, keys, events)
                    return
        super().on_deselect(others, keys, events)

    def output_clicked(self, others, keys, event, events):
        # Break current connection
        for o in (other for other in others
                  if other is not self
                  and isinstance(other, IRenderableComponent)):
            if self.component in o.component:
                reverse_dict = {v: k for k, v in o.component.inputs.items()}
                key = reverse_dict[self.component]
                o.component.inputs[key] = None
        self.dragging = True

    # For comparability
    def update_surface(self):
        self.surface.fill(COLOR_DICT["other"])
        self.surface.set_colorkey(COLOR_DICT["other"])
        self.render(self.surface)

    # When each wire created their own surface, there would be a lot of lag as
    # every surface needs to be blitted onto the display surface
    # Instead we take the display surface and draw onto it, which is
    # destructive but faster
    # This requires wires to be drawn last
    def render(self, surface):
        """
        Takes a surface and draws the wire onto the surface
        """
        if self.dirty and not self.hidden:
            if self.surface is not surface:
                self.surface = surface
                self.hitbox = surface.get_rect()
                if self.surface.get_colorkey() is not COLOR_DICT["other"]:
                    self.surface.set_colorkey(COLOR_DICT["other"])

            distance = self.output.distance_to(self.input)
            niceness_factor = pow(distance, 0.6) * math.log(distance + 1)
            points = (self.input,
                      (self.input[0] + niceness_factor, self.input[1]),
                      (self.output[0] - niceness_factor, self.output[1]),
                      self.output)
            steps = 10
            pygame.gfxdraw.bezier(
                self.surface, points, steps, COLOR_DICT[self.component.output])

            pygame.draw.circle(self.surface,
                               COLOR_DICT[self.component.output],
                               (int(self.output[0]), int(self.output[1])),
                               int(SELECT_RADIUS / 2))
            pygame.gfxdraw.circle(self.surface,
                                  int(self.output[0]),
                                  int(self.output[1]),
                                  SELECT_RADIUS,
                                  COLOR_DICT[self.component.output])


class SpawnGate(gui.TextButton):

    """
    A button that spawns a renderable object given the class.
    """

    def __init__(self,
                 hitbox,
                 gate_class,
                 hidden=False,
                 font_size=50):
        # The function that spawns the object
        def f(self, others, keys, events):
            # This is strictly not needed, by making the object selected
            # ensures that on the next tick it is moved to the correct position
            for event in events:
                if event.type in (pygame.MOUSEBUTTONDOWN,):
                    break
            new_gate = gate_class(pos=self.top_left)
            new_gate.align(event.pos, alignment.center_center)
            # We don't need to set dragging because that is done automatically
            new_gate.selected = True
            self.selected = False
            others.insert(0, new_gate)

        super().__init__(gate_class.__name__,
                         hitbox,
                         function=f,
                         hidden=hidden,
                         font_size=font_size,
                         fgcolor=COLOR_DICT[None],
                         bgcolor=COLOR_DICT["other"])


class CircuitBoard(interfaces.IContainer):

    """
    A renderable circuit board that contains components.

    This creates the buttons that spawns the gates and ensures that wires are rendered on top 
    and updated first
    """
    GATE_CLASSES = (Switch, Bulb,
                    And, Or, Not,
                    Nand, Nor)

    def __init__(self,
                 hitbox,
                 renderable_list=[],
                 hidden=False):
        load_surfaces()

        renderable_list = list(renderable_list)
        rect = SURFACE["and"].get_rect()

        # Move the buttons down slightly
        for i, gate_class in enumerate(self.GATE_CLASSES):
            rect.topleft = (0, i * rect.h)
            spawn_gate = SpawnGate((0, 0),
                                   gate_class,
                                   font_size=rect.h * 0.6)
            spawn_gate.align(rect, alignment.left_middle)
            renderable_list.insert(0, spawn_gate)

        super().__init__(hitbox,
                         renderable_list,
                         hidden,
                         COLOR_DICT["other"])

    def mouse_motion(self, others, keys, event, events):
        if event.type == interfaces.MOUSEMOTION_NEW:
            if self.selected:
                selected = any(o.selected for o in self.renderable_list
                               if isinstance(o, interfaces.IInteractable))
                if not selected:
                    # Move everything
                    for r in (o for o in self.renderable_list
                              if isinstance(o, IRenderableComponent)):
                        if isinstance(r, Wire):
                            r.inputs = {(k[0] + event.rel[0], k[1] + event.rel[1]): v
                                        for k, v in r.inputs.items()}
                            r.output += event.rel
                        else:
                            r.move(event.rel)
                            r.dirty = True
        super().mouse_motion(others, keys, event, events)

    def update_renderable_list(self):
        # Ensure that the update is in the same order as if a
        # logic_circuit.CircuitBoard was created
        def sort_key(renderable):
            if isinstance(renderable, Wire):
                return 0
            if isinstance(renderable, IRenderableComponent):
                return 1
            if isinstance(renderable, SpawnGate):
                return 3
            return 4
        self.renderable_list = sorted(self.renderable_list, key=sort_key)

    def update_surface(self):
        interfaces.IInteractable.update_surface(self)

        self.surface.fill(self.bgcolor)

        self.update_renderable_list()

        # This stops the lookup of the values for every iteration of the loop
        surface_blit = self.surface.blit
        # Draw the things that get updated first last as each draw draws over
        # the other stuff
        for r in reversed(self.renderable_list):
            if isinstance(r, Wire):
                r.render(self.surface)
            else:
                surface_blit(r.render_surface(), r.top_left)

        outline = pygame.rect.Rect(0, 0, self.hitbox.w, self.hitbox.h)
        pygame.gfxdraw.rectangle(self.surface, outline, COLOR_DICT[None])

    def update(self, others, keys, events):
        def logic_board(renderable_list):
            return logic_circuit.CircuitBoard(c.component for c in renderable_list
                                              if isinstance(c, IRenderableComponent))
        old_circuit_board = logic_board(self.renderable_list)

        super().update(others, keys, events)

        if not self.hidden:
            if logic_board(self.renderable_list) != old_circuit_board:
                # Something has changed, either something has been removed or
                # added to the board
                # This might not be needed as new objects are supposed to be
                # dirty until they are drawn
                self.dirty = True


# Simply a wrapper
def expression(renderable_component, anonymous_symbols=False):
    """
    Returns an expression when given a renderable component.

    Raises logic_circuit.RecursionError if any component is self referencing.
    """
    return logic_circuit.expression(renderable_component.component)


# Rendreable components need the correct class names for them to know
# which surface to use
# Other than that it is very similar to the one in logic_circuit
def renderable_components(expression, pos=(0, 0), bulb=True):
    """
    Returns an list of renderable components when given an expression.
    """
    if isinstance(expression, str):
        expression = boolean.parse(expression, eval=False)
    if not isinstance(expression, boolean.Expression):
        raise TypeError(
            "Argument must be str or Expression but it is {}"
            .format(expression.__class__))

    r = [Bulb(pos)]
    symbol_dict = {}

    def recursive_components(e):
        # This function can be used if there is ever the want to attempt to make the
        # converted logic circuit look nicer by spacing the components
        def append(r_comp):
            r.append(r_comp)

        if isinstance(e, boolean.BaseElement):
            rc = Switch(pos)
        elif isinstance(e, boolean.Symbol):
            if e in symbol_dict.keys():
                return symbol_dict[e]
            else:
                rc = Switch(pos)
                symbol_dict[e] = rc
        elif isinstance(e, boolean.NOT):
            pre = recursive_components(e.args[0])
            w = Wire(pos, pos, pre.component)
            append(w)

            rc = Not(pos, w.component)
        elif isinstance(e, boolean.DualBase):
            if len(e.args) != 2:
                new_expr = e.__class__(e.args[0], e.args[1])
                for i in range(2, len(e.args)):
                    new_expr = e.__class__(new_expr, e.args[i], eval=False)
                e = new_expr
            pre0 = recursive_components(e.args[0])
            pre1 = recursive_components(e.args[1])
            w0 = Wire(pos, pos, pre0.component)
            w1 = Wire(pos, pos, pre1.component)
            append(w0)
            append(w1)

            if isinstance(e, boolean.AND):
                rc = And(pos)
            elif isinstance(e, boolean.OR):
                rc = Or(pos)
            c = rc.component
            c.inputs[c.empty_input_keys[0]] = w0.component
            c.inputs[c.empty_input_keys[0]] = w1.component
        append(rc)
        return rc

    recursive_components(expression)
    if bulb:
        w = Wire(pos, pos, r[-1].component)
        r[0].component.input = w.component
        r.append(w)
    else:
        r.pop(0)
    return r
