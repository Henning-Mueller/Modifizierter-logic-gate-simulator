"""
Renderable Interfaces.

This module provides some interfaces for renderable objects. Interfaces each
contain a hitbox and surface. All interfaces have an update method, which should
be called every tick. Rendering is left to caller, this can be done by blitting
the surface recieved when calling render_surface to the display.

Currently there are four interfaces provided: IRenderable, IInteractable,
IDraggable and IContainer.
IContainer can contain other renderable objects. Objects contained inside of an
IContainer instance cannot interact with those outside of it.
"""
import pickle

import pygame
import pygame.gfxdraw

import alignment


# The following functions are used to keep track of which events are new
# and which are old, making sure that mouse events are keyboard events are only
# handled by one object.
def new_event(event):
    HAS_NEW = (pygame.KEYDOWN,
               pygame.KEYUP,
               pygame.MOUSEBUTTONDOWN,
               pygame.MOUSEBUTTONUP,
               pygame.MOUSEMOTION)
    if isinstance(event, int):
        if event in HAS_NEW:
            return event + pygame.USEREVENT
        return event
    if isinstance(event, pygame.event.EventType):
        if event.type in HAS_NEW:
            return pygame.fastevent.Event(event.type + pygame.USEREVENT,
                                          event.dict)
        return event


def normal_event(event):
    global KEYDOWN_NEW
    global KEYUP_NEW
    global MOUSEMOTION_NEW
    global MOUSEBUTTONDOWN_NEW
    global MOUSEBUTTONUP_NEW
    HAS_OLD = (KEYDOWN_NEW,
               KEYUP_NEW,
               MOUSEBUTTONDOWN_NEW,
               MOUSEBUTTONUP_NEW,
               MOUSEMOTION_NEW)
    if isinstance(event, int):
        if event in HAS_OLD:
            return event - pygame.USEREVENT
        return event
    if isinstance(event, pygame.event.EventType):
        if event.type in HAS_OLD:
            return pygame.fastevent.Event(event.type - pygame.USEREVENT,
                                          event.dict)
        return event


def new_events(events):
    return list(new_event(e) for e in events)


def normal_events(events):
    return list(normal_event(e) for e in events)

KEYDOWN_NEW = new_event(pygame.KEYDOWN)
KEYUP_NEW = new_event(pygame.KEYUP)
MOUSEMOTION_NEW = new_event(pygame.MOUSEMOTION)
MOUSEBUTTONDOWN_NEW = new_event(pygame.MOUSEBUTTONDOWN)
MOUSEBUTTONUP_NEW = new_event(pygame.MOUSEBUTTONUP)


class IRenderable:

    """
    An interface for renderable objects.

    All renderable objects have a hitbox, which is also the size of the surface
    that can be rendered on.
    Renderable objects have an attribute called hidden. Hidden objects return
    a surface of size 0x0 which if blitted does nothing.

    Whenever a change is made to a renderable object that causes it's surface to
    be rendered differently, the object is considered "dirty". This is why you
    should not modify the hitbox attributes directly, but instead use the
    wrappers for them. This ensures that the surface only needs to be redrawn
    every time a change is made to it.

    Every tick you should call update and render_surface.
    """

    def __init__(self,
                 hitbox,
                 hidden=False):
        self.hitbox = pygame.rect.Rect(hitbox)
        self.hidden = hidden
        self.dirty = True
        self.surface = pygame.surface.Surface((self.hitbox.w, self.hitbox.h))

    def __repr__(self):
        return "<{name}({hitbox})>".format(name=self.__class__.__name__,
                                           hitbox=repr(self.hitbox))

    # The following are wrappers for the hitbox's attributes
    # These allow for the object to be set as dirty if needed
    @property
    def x(self):
        return self.hitbox.x

    @x.setter
    def x(self, x):
        self.hitbox.x = x

    @property
    def y(self):
        return self.hitbox.y

    @y.setter
    def y(self, y):
        self.hitbox.y = y

    @property
    def w(self):
        return self.hitbox.w

    @w.setter
    def w(self, w):
        self.hitbox.w = w
        self.dirty = True

    @property
    def h(self):
        return self.hitbox.h

    @h.setter
    def h(self, h):
        self.hitbox.h = h
        self.dirty = True

    @property
    def top_left(self):
        return self.hitbox.topleft

    @top_left.setter
    def top_left(self, top_left):
        self.hitbox.topleft = top_left

    # This function is overridden in child classes to allow them to draw
    # on the surface
    def update_surface(self):
        """
        Recreates the surface and redraws everything.

        This should only be called when the object is dirty, but the only
        adverse effect is wasted time.

        The size of the surface is set by the size of the hitbox, and by
        default it is not transparent.
        """
        # A new surface must be created in case thw width or height changes
        self.surface = pygame.surface.Surface((self.hitbox.w, self.hitbox.h))
        # If child classes need transparency, they should call
        # self.surface.set_colorkey(<pygame.color.Color>)
        # after super().update_surface()

        # An alternative is the flag pygame.SRCALPHA
        # which makes the whole surface have transparency

    # If this function is overridden, it should do the following:
    #surface = super().render_surface()
    # do stuff (to the surface)
    # return surface
    def render_surface(self):
        """
        Returns a surface.

        If the renderable object is hidden, it returns a surface of size 0x0.

        This should be called once per tick and blitted onto the display surface
        using:
        display_surface.blit(<object>.render_surface(), <object>.top_left)
        """
        if self.hidden:
            return pygame.surface.Surface((0, 0))
        if self.dirty:
            self.update_surface()
            self.dirty = False
        return self.surface

    # A "virtual" function
    # This should be overridden if needed
    def update(self, others, keys, events):
        """
        Updates the object.

        This should be called once per tick.
        "others" contains a list of other renderable objects.
        "keys" is a list of booleans, which can be gotten by calling:
        pygame.key.get_pressed()
        "events" is a list of events, which can be gotten by calling:
        pygame.event.get() or pygame.fastevent.get()
        You should call ininterfaces.new_events(<events>) before giving
        then to any objects.
        """
        pass

    # Moving an object does not make it dirty because the size of the hitbox
    # does not change
    def move(self, vector):
        self.hitbox.move_ip(vector)

    def align(self, pos, align):
        """
        Aligns the object with a position or rectagle like object.

        The argument pos can be either a position (x, y) or a rectangle like
        object (x, y, w, h).
        Alignments are defined in alignment.py and are in the format (x, y).
        Aligning to a rectangle aligns to the inside of the rectangle.
        """
        # Rectangle
        if len(pos) == 4:
            # X:
            if align.x == alignment.left:
                self.x = pos[0]
            elif align.x == alignment.middle:
                self.x = pos[0] + (pos[2] - self.w) / 2
            elif align.x == alignment.right:
                self.x = pos[0] + pos[2] - self.w
            # Y:
            if align.y == alignment.top:
                self.y = pos[1]
            elif align.y == alignment.center:
                self.y = pos[1] + (pos[3] - self.h) / 2
            elif align.y == alignment.bottom:
                self.y = pos[1] + pos[3] - self.h
        # Point
        elif len(pos) == 2:
            # X:
            if align.x == alignment.left:
                self.x = pos[0]
            elif align.x == alignment.middle:
                self.x = pos[0] - self.w / 2
            elif align.x == alignment.right:
                self.x = pos[0] - self.w
            # Y:
            if align.y == alignment.top:
                self.y = pos[1]
            elif align.y == alignment.center:
                self.y = pos[1] - self.h / 2
            elif align.y == alignment.bottom:
                self.y = pos[1] - self.h

    def pre_pickle(self):
        # pygame surfaces cannot be pickled
        self.surface = None
        # When unpickling the object, the surface needs to be recreated
        self.dirty = True

    def pickle(self, file_name, protocol=pickle.HIGHEST_PROTOCOL):
        """
        Saves the object to a file.

        pickle.dump(object) should not be called as pygame surfaces cannot be
        pickled. pre_pickle should be called before pickling an object.
        """
        self.pre_pickle()
        with open(file_name, "wb") as f:
            pickle.dump(self, f, protocol)


class IInteractable(IRenderable):

    """
    An interface for objects that you can interact with.

    All interactable objects can be selected, therefore have the selected
    attribute.
    Objects are selected when a mouse down occurs inside of them.
    Leaving the bounding box or releasing the mouse is considered deselecting.

    You can interact by clicking or pressing a key.
    """

    def __init__(self,
                 hitbox,
                 hidden=False):
        # Selected objects should take convert all events that they have dealt
        # with into normal events
        self._selected = False
        super().__init__(hitbox=hitbox,
                         hidden=hidden)

    @property
    def hidden(self):
        return self._hidden

    @hidden.setter
    def hidden(self, hidden):
        self._hidden = bool(hidden)
        # If an object is made hidden, it can no longer be selected
        self.selected = False

    # These allow for the object to be set as dirty if needed
    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, selected):
        self._selected = bool(selected)
        self.dirty = True

    def update_surface(self):
        # Generate the surface first
        super().update_surface()

        if self.selected:
            # dark blue
            outline_color = pygame.color.Color(0, 255, 255)
        else:
            # light blue
            outline_color = pygame.color.Color(0, 0, 255)
        outline = pygame.rect.Rect(0, 0, self.hitbox.w, self.hitbox.h)
        pygame.gfxdraw.rectangle(self.surface, outline, outline_color)

    # others is an array of all other IRenderables
    # keys is an array of booleans which corespond to which keys are pressed
    # events is an array of all the events since the previous update
    def update(self, others, keys, events):
        old_selected = self.selected
        if self.selected:
            self.while_selected(others, keys, events)

        if not self.hidden:
            for event in events:
                # Even handled events are given to each function
                # This is in case an object needs to check if an event occured
                if event.type in (pygame.KEYDOWN, KEYDOWN_NEW):
                    self.key_down(others, keys, event, events)
                elif event.type in (pygame.KEYUP, KEYUP_NEW):
                    self.key_up(others, keys, event, events)
                elif event.type in (pygame.MOUSEMOTION, MOUSEMOTION_NEW):
                    self.mouse_motion(others, keys, event, events)
                elif event.type in (pygame.MOUSEBUTTONDOWN, MOUSEBUTTONDOWN_NEW):
                    self.mouse_down(others, keys, event, events)
                elif event.type in (pygame.MOUSEBUTTONUP, MOUSEBUTTONUP_NEW):
                    self.mouse_up(others, keys, event, events)

        if not old_selected and self.selected:
            self.on_select(others, keys, events)
        elif old_selected and not self.selected:
            self.on_deselect(others, keys, events)

    # Although not implimented, classes that inherit from IInteractable should
    # ensure that they are selected before acting on key presses
    def key_down(self, others, keys, event, events):
        pass

    def key_up(self, others, keys, event, events):
        pass

    def mouse_motion(self, others, keys, event, events):
        if event.type == MOUSEMOTION_NEW:
            if self.selected:
                index = events.index(event)
                events[index] = normal_event(event)

    def mouse_down(self, others, keys, event, events):
        # left_click: 1
        # middle_click: 2
        # right_click:3
        # scroll_up: 4
        # scroll_down: 5

        # If the event hasn't been handled already
        if event.type == MOUSEBUTTONDOWN_NEW:
            if event.button == 1:
                if self.hitbox.collidepoint(event.pos):
                    self.selected = True
                if self.selected:
                    index = events.index(event)
                    events[index] = normal_event(event)

    def mouse_up(self, others, keys, event, events):
        if event.button == 1:
            self.selected = False

    def on_select(self, others, keys, events):
        # Bring self to front.
        others.insert(0, others.pop(others.index(self)))

    def on_deselect(self, others, keys, events):
        pass

    def while_selected(self, others, keys, events):
        # An object can be delseected the tick that this is called
        # This is called at the start of the update
        pass


class IDraggable(IInteractable):

    """
    An interface for objects that can be dragged around.

    For an object to be dragged, they must be selected. Then any mouse motion
    events translate to movement. If an object was being dragged in the
    previous call of update, their dragging attribute is set to True.

    If you need something that can only be dragged when a key is pressed or
    when the user right clicks, overridde the mouse_down, mouse_up and
    mouse_motion methods to only select the object when you want.
    """

    def __init__(self,
                 hitbox,
                 hidden=False):
        self._dragging = False
        super().__init__(hitbox=hitbox,
                         hidden=hidden)

    @property
    def dragging(self):
        return self._dragging

    @dragging.setter
    def dragging(self, dragging):
        self._dragging = bool(dragging)
        # This is only required if the surface needs to be changed when the
        # object is being dragged

        self.dirty = True

    def update(self, others, keys, events):
        old_dragging = self.dragging
        if self.dragging:
            self.while_dragging(others, keys, events)


        super().update(others, keys, events)

        if not old_dragging and self.dragging:
            self.on_drag(others, keys, events)
        elif old_dragging and not self.dragging:
            self.on_release(others, keys, events)

    def on_deselect(self, others, keys, events):
        self.dragging = False

    def while_selected(self, others, keys, events):
        super().while_selected(others, keys, events)
        mouse_motion_events = (e for e in events
                               if e.type in (MOUSEMOTION_NEW,)
                               and e.buttons[0])  # pygame.MOUSEMOTION))
        for event in mouse_motion_events:
                ##                x = event.pos[0] - self.x - self.w/2
                ##                y = event.pos[1] - self.y - self.h/2
                ##                self.move((x, y))
            self.move(event.rel)
            self.dragging = True

    def on_drag(self, others, keys, events):
        pass

    def on_release(self, others, keys, events):
        pass

    def while_dragging(self, others, keys, events):
        # An object can be released the tick that this is called
        # This is called at the start of the update
        pass


class IContainer(IInteractable):

    """
    An interface for a container of renderable objects.

    Containers contain renderable objects. Objects inside of them cannot
    interact with objects outside. All events recieved by the objects inside
    are renewed. For this reason containers should not overlap unless they
    are hidden.
    Containers themselves cannot be dragged, but they are interactable. 
    """

    def __init__(self,
                 hitbox,
                 renderable_list=[],
                 hidden=False,
                 bgcolor=pygame.color.THECOLORS["black"]):
        # Create a copy of the renderable_list and make sure it is of type list
        self.renderable_list = list(renderable_list)
        self.bgcolor = bgcolor
        super().__init__(hitbox=hitbox,
                         hidden=hidden)

    @property
    def renderable_list(self):
        return self._renderable_list

    @renderable_list.setter
    def renderable_list(self, renderable_list):
        self._renderable_list = list(renderable_list)
        # It is assumed that something has changed to the list
        self.dirty = True

    @property
    def bgcolor(self):
        return self._bgcolor

    @bgcolor.setter
    def bgcolor(self, bgcolor):
        if isinstance(bgcolor, (tuple, list, pygame.color.Color)):
            self._bgcolor = pygame.color.Color(*bgcolor)
        else:
            self._bgcolor = pygame.color.Color(bgcolor)
        self.dirty = True

    def update_renderable_list(self):
        # Used if the renderable list itself needs to change
        pass

    def update_surface(self):
        super().update_surface()
        self.surface.fill(self.bgcolor)

        self.update_renderable_list()

        for r in reversed(self.renderable_list):
            self.surface.blit(r.render_surface(), r.top_left)

        if self.selected:
            outline_color = pygame.color.Color(0, 255, 255)
        else:
            outline_color = pygame.color.Color(0, 0, 255)
        outline = pygame.rect.Rect(0, 0, self.hitbox.w, self.hitbox.h)
        pygame.gfxdraw.rectangle(self.surface, outline, outline_color)

    def update(self, others, keys, events):
        def shift_event_positions(old_events):
            """
            Shifts the position of events have a pos attribute.
            """
            new_events = []
            for event in old_events:
                if event.type in (pygame.MOUSEBUTTONDOWN,
                                  pygame.MOUSEBUTTONUP,
                                  pygame.MOUSEMOTION,
                                  MOUSEBUTTONDOWN_NEW,
                                  MOUSEBUTTONUP_NEW,
                                  MOUSEMOTION_NEW):
                    event_dict = event.dict.copy()
                    event_dict["pos"] = (event.dict["pos"][0] - self.x,
                                         event.dict["pos"][1] - self.y)
                    event = pygame.fastevent.Event(event.type, event_dict)
                new_events.append(event)
            return new_events

        if not self.hidden:
            # Objects inside the container are independant to those outside
            my_others = self.renderable_list
            my_events = shift_event_positions(events)
            my_events = new_events(my_events)
            for r in self.renderable_list:
                r.update(my_others, keys, my_events)

            # Updating all objects in renderable_list may have made them dirty
            # The container is dirty if it is already dirty
            # Or if not all of the list is not dirty
            #print(self.dirty, any(r.dirty for r in self.renderable_list))
            self.dirty = self.dirty or any(
                r.dirty for r in self.renderable_list)
            super().update(others, keys, events)

    def pre_pickle(self):
        super().pre_pickle()
        # All objects need to be pre_pickled
        for r in self.renderable_list:
            r.pre_pickle()
