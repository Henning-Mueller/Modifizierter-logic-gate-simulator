"""
Simple guis.

This module provides simple guis. Currently is includes two GUIs, an input box
and a text button.
"""
import string

import pygame

import alignment
import interfaces
import text


class InputBox(interfaces.IContainer):

    """
    A baisc input box.

    Input boxes are interactable gui elements that allow the user to enter
    text. Input boxes cannot display special characters like tab, therefore
    there is a whitlist of chracters that can be entered. You can set this by
    modifying the allowed_characters property.

    Text will align to center left by default unless there is too much text for
    the box. If this is the case then they will align center right. If too much
    text is entered, this will throw:
    pygame.error("Width or height is too large")

    There is no cursor or repeat key feature. Pressing delete delete all the
    text inside of a input box.
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
        self._default_text = default_text
        self.allowed_characters = string.ascii_letters +\
            string.digits +\
            string.punctuation +\
            "£ ¬"
        self.render_text = text.Text(default_text,
                                     (1, 1),
                                     hidden=hidden,
                                     size=font_size,
                                     fgcolor=fgcolor,
                                     bgcolor=bgcolor,
                                     underline=underline,
                                     strong=strong,
                                     oblique=oblique,
                                     name=name)
        if len(hitbox) == 2:
            hitbox += (self.render_text.w + 2, self.render_text.h + 2)
        elif len(hitbox) == 3:
            # 3rd is height
            hitbox = hitbox[:2] + (self.render_text.w + 2, hitbox[-1])
        super().__init__(hitbox,
                         [self.render_text],
                         hidden,
                         bgcolor)
        self.text = default_text

    @property
    def text(self):
        return self.render_text.text

    @text.setter
    def text(self, string):
        self.render_text.text = str(string)
        # This throws an error if the surface is too big.
        w, h = self.render_text.fit_surface()
        self.render_text.w = w
        self.render_text.h = h
        if w > self.w:
            align = alignment.middle_right
        else:
            align = alignment.middle_left
        self.render_text.align((1, 1, self.w - 2, self.h - 2), align)
        self.dirty = True

    def mouse_up(self, others, keys, event, events):
        # Input boxes do not get deselected on mouse up, instead you must click
        # elsewhere
        # This allow the user to enter text without holding the mouse button
        pass

    def mouse_down(self, others, keys, event, events):
        # This is required because input boxes are not deselected on mouse up
        if event.button == 1:
            if not self.hitbox.collidepoint(event.pos):
                self.selected = False
        super().mouse_down(others, keys, event, events)

    def on_select(self, others, keys, events):
        # Convenience for the user
        if self.text == self._default_text:
            self.text = ""

    def on_deselect(self, others, keys, events):
        # The default text can be used as help text to tell the user what to
        # enter
        if self.text == "":
            self.text = self._default_text

    def while_selected(self, others, keys, events):
        for event in (e for e in events
                      if e.type in (interfaces.KEYDOWN_NEW,)):
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            # This may not be a good idea, but there is no easy way to delete
            # all the text
            elif event.key == pygame.K_DELETE:
                self.text = ""
            elif event.key in (pygame.K_RETURN, ):
                self.selected = False
            elif event.unicode in self.allowed_characters:
                self.text += event.unicode

            index = events.index(event)
            events[index] = interfaces.normal_event(event)


class TextButton(interfaces.IContainer):

    """
    A text button.

    Text buttons call functions on mouse down. This is different from windows
    buttons with call their respecive function on mouse up.

    Text inside of text buttons are centered. 
    """

    def __init__(self,
                 display_text,
                 hitbox,
                 function=lambda s, o, k, e: None,
                 hidden=False,
                 font_size=50,
                 fgcolor=pygame.color.THECOLORS["black"],
                 bgcolor=pygame.color.THECOLORS["white"],
                 underline=False,
                 strong=False,
                 oblique=False,
                 name="Calibri"):
        self.function = function
        self.render_text = text.Text(display_text,
                                     (1, 1),
                                     hidden=hidden,
                                     size=font_size,
                                     fgcolor=fgcolor,
                                     bgcolor=bgcolor,
                                     underline=underline,
                                     strong=strong,
                                     oblique=oblique,
                                     name=name)
        if len(hitbox) == 2:
            hitbox += (self.render_text.w + 2, self.render_text.h + 2)
        elif len(hitbox) == 3:
            # 3rd is height
            hitbox = hitbox[:2] + (self.render_text.w + 2, hitbox[-1])
        super().__init__(hitbox,
                         [self.render_text],
                         hidden,
                         bgcolor)
        self.text = display_text

    @property
    def text(self):
        return self.render_text.text

    # This will not resize the outer surface, meaning that if the text is too
    # large to display, it will just get cut off
    @text.setter
    def text(self, string):
        self.render_text.text = str(string)
        w, h = self.render_text.fit_surface()
        self.render_text.w = w
        self.render_text.h = h
        self.render_text.align((0, 0, self.w, self.h),
                               alignment.middle_middle)
        self.dirty = True

    # On select occurs on the same tick as the mouse down event
    def on_select(self, others, keys, events):
        self.function(self, others, keys, events)
        super().on_select(others, keys, events)
