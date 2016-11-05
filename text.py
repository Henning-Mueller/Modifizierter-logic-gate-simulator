"""
Wrappers around pygame.freetype for easy text rendering.

Also supports expressions with overbars and truth tables.
"""
import pygame
import pygame.gfxdraw
import pygame.freetype

import alignment
import interfaces
import boolean

# TODO: Add normal tables
# TODO: Use textwrap to wrap text

# pygame.init does not call pygame.freetype.init
pygame.freetype.init()


# Text be itself should not be interactable or draggable, but if you need it then
# create a new class that inherits from both Text and IInteractable/IDraggable
class Text(interfaces.IRenderable):

    """
    A container for text that can be rendered.

    This is a wrapper for pygame.freetype.Font, with the small addition of being
    able to render multiple lines of text.
    """

    def __init__(self,
                 text,
                 hitbox,            # (x, y) or (x, y, w, h)
                 hidden=False,
                 size=50,           # font size
                 fgcolor=pygame.color.THECOLORS["black"],
                 bgcolor=pygame.color.THECOLORS["white"],
                 underline=False,
                 strong=False,      # bold
                 oblique=False,     # italic
                 name="Calibri"):
        # TODO: Consider caching fonts
        # Fonts could be cached but that would mean changing
        # their attributes before rendering for every Text instance
        file = pygame.freetype.match_font(name)
        self.font = pygame.freetype.Font(file)
        self.size = size
        self.text = text
        self.bgcolor = bgcolor
        self.fgcolor = fgcolor
        self.underline = underline
        self.strong = strong
        self.oblique = oblique

        # Hitbox can either be (x, y, w, h) or (x, y)
        # When it is (x, y), we need to fit the surface to the hitbox
        if len(hitbox) == 2:
            hitbox += self.fit_surface()
        super().__init__(hitbox, hidden)

    def __repr__(self):
        return "<{name}({hitbox}, {text})>".format(name=self.__class__.__name__,
                                                   hitbox=repr(self.hitbox),
                                                   text=repr(self.text))

    # More wrappers, this time around font's attributes
    @property
    def size(self):
        return self.font.size

    @size.setter
    def size(self, size):
        self.font.size = size
        self.dirty = True

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, string):
        # Although there is no need to worry about storing a direct copy, this
        # ensures that _text is of type string for when we call text.split in
        #fit_surface and update_surface
        self._text = str(string)
        self.dirty = True

    # bgcolor is not an attribute saved in font, but is passed when calling
    # font.render_to
    @property
    def bgcolor(self):
        return self._bgcolor

    @bgcolor.setter
    def bgcolor(self, bgcolor):
        # For some odd reason, pygame.color.THECOLORS[<color_name>] returns
        # a tuple instead of a pygame.color.Color
        # pygame.color.Color takes a name, rgba or rgbavalue
        if isinstance(bgcolor, (tuple, list, pygame.color.Color)):
            # Unpack the tuple or list
            # Create a new color, to ensure that we don't store a direct copy
            # of the tuple and bypass this function
            self._bgcolor = pygame.color.Color(*bgcolor)
        else:
            # this is if bgcolor is a name or rgbavalue
            self._bgcolor = pygame.color.Color(bgcolor)
        self.dirty = True

    @property
    def fgcolor(self):
        return self.font.fgcolor

    @fgcolor.setter
    def fgcolor(self, fgcolor):
        # The same as bgcolor
        if isinstance(fgcolor, (tuple, list, pygame.color.Color)):
            self.font.fgcolor = pygame.color.Color(*fgcolor)
        else:
            self.font.fgcolor = pygame.color.Color(fgcolor)
        self.dirty = True

    @property
    def underline(self):
        return self.font.underline

    @underline.setter
    def underline(self, underline):
        self.font.underline = underline
        self.dirty = True

    @property
    def strong(self):
        return self.font.strong

    @strong.setter
    def strong(self, strong):
        self.font.strong = strong
        self.dirty = True

    @property
    def oblique(self):
        return self.font.oblique

    @oblique.setter
    def oblique(self, oblique):
        self.font.oblique = oblique
        self.dirty = True

    def fit_surface(self):
        """
        Returns the width and height for a surface that would perfectly fit the text.

        The returned value leaves a 1px border around the text.
        """
        lines = self.text.split("\n")

        max_height = max_height = max(
            self.font.get_rect(line).h for line in lines)
        w = max(self.font.get_rect(line).w for line in lines)
        h = (len(lines) - 1) * max_height + self.font.get_rect(lines[-1]).h

        # When pygame.freetype.Font.render_to is given a bgcolor, it goes over
        # by 1 pixels of the actual font, the extra is to add a small border
        return (w + 2, h + 2)

    def update_surface(self):
        super().update_surface()
        # pygame.freetype.Font.render_to only fills the boxes for each line
        self.surface.fill(self.bgcolor)

        # Render Text
        lines = self.text.split("\n")
        max_height = max(self.font.get_rect(line).h for line in lines)
        for i in range(len(lines)):
            x = 1
            y = 1 + max_height * i
            # Add a small border around the font to prevent the text bleeding
            # if blitted onto a surface of the same color
            # giving a bgcolor makes the font more "sharp"
            self.font.render_to(self.surface,
                                (x, y),
                                lines[i],
                                bgcolor=self.bgcolor)


class Expression(Text):

    """
    Renderable boolean expressions.

    Boolean expressions that are rendered includes the proper overbars.
    """

    def __init__(self,
                 expression,
                 hitbox,
                 hidden=False,
                 size=50,
                 fgcolor=pygame.color.THECOLORS["black"],
                 bgcolor=pygame.color.THECOLORS["white"],
                 name="Calibri"):
        # align = alignment.top_left):
        super().__init__(expression,
                         hitbox,
                         hidden=hidden,
                         size=size,
                         fgcolor=fgcolor,
                         bgcolor=bgcolor,
                         name=name)

    # Ignore the programmer if he wants to set any of the following values
    # That also means that assigning these does not make the object dirty
    @property
    def underline(self):
        return super().underline

    @underline.setter
    def underline(self, underline):
        self.font.underline = False

    @property
    def strong(self):
        return super().strong

    @strong.setter
    def strong(self, strong):
        self.font.strong = False

    @property
    def oblique(self):
        return super().oblique

    @oblique.setter
    def oblique(self, oblique):
        self.font.oblique = False

    # Assign expression
    @property
    def text(self):
        return str(self.expression)

    @text.setter
    def text(self, string):
        self.expression = string

    @property
    def expression(self):
        return self._expression

    @expression.setter
    def expression(self, expression):
        if isinstance(expression, str):
            expression = boolean.parse(expression, False)
        if not isinstance(expression, boolean.Expression):
            raise TypeError("Argument must be str or Expression but it is {}"
                            .format(expression.__class__))
        self._expression = expression
        self.dirty = True

    @staticmethod
    def max_not_count(expr):
        """
        Recursively calculates the maximum multiplier needed when drawing an overbar.
        """
        if isinstance(expr, boolean.BaseElement):
            return 0
        if isinstance(expr, boolean.Symbol):
            return 0
        if isinstance(expr, boolean.NOT):
            return 1 + max(Expression.max_not_count(e) for e in expr.args)
        return max(Expression.max_not_count(e) for e in expr.args)

    def overbar_surface(self):
        """
        Returns a surface containing an overbar that would fit the entire expression.

        The overbar scales with the text size.
        """
        old_underline = self.font.underline
        old_underline_adjustment = self.font.underline_adjustment
        # As we are using an overbar for each NOT, we need to remove them
        text = self.text.replace(boolean.NOT.operator, "")

        without_overbar = self.font.get_rect(text)

        # Underline adjustment of -1 makes the underline become an overbar
        self.font.underline = True
        self.font.underline_adjustment = -1

        with_overbar = self.font.render(text, bgcolor=self.bgcolor)

        # font.render returns (<surface>, <rect>)
        width = with_overbar[1].w
        height = with_overbar[1].h - without_overbar.h
        overbar_surface = pygame.surface.Surface((width, height))
        overbar_surface.blit(with_overbar[0], (0, 0), (0, 0, width, height))

        self.font.underline = old_underline
        self.font.underline_adjustment = old_underline_adjustment

        return overbar_surface

    def fit_surface(self):
        # As we are using an overbar for each NOT, we need to remove them
        w = self.font.get_rect(self.text.replace(boolean.NOT.operator, "")).w
        # adjust hight for every overbar we need
        overbar_height = self.max_not_count(
            self.expression) * self.overbar_surface().get_rect().h
        h = self.font.get_rect(
            self.text.replace(boolean.NOT.operator, "")).h + overbar_height
        # 1px border on each side
        return (w + 2, h + 2)

    def update_surface(self):
        # Text.update_surface renders the text so that it starts at the top left of the
        # bounding box, instead we want to move it down if there are any overbars that need
        # to be drawn.
        # update_overbar will modify self.render_surface, which is created here
        # to be safe.
        interfaces.IRenderable.update_surface(self)

        # Cache the overbar surface before the update_overbar function. The overbar surface
        # depends on the font size and expression, so it should not change during an
        # update_surface call.
        overbar_surface = self.overbar_surface()

        # pygame.freetype.Font.render_to only fills the boxes for each line
        self.surface.fill(self.bgcolor)

        # Recursively draw overbars
        # TODO?: clean + optimize this code, without breaking it
        def update_overbar(expr, top_left):
            # I'm going to leave t here as it'll be really useful when trying
            # to refactor / clean / optimize this code
            # DEBUG CODE
            # DEBUG_TEXT_SIZE = str(expr).replace(boolean.NOT.operator, "")
            # DEBUG_TEXT_SIZE = self.font.get_rect(DEBUG_TEXT_SIZE)
            # DEBUG_TEXT_SIZE = (DEBUG_TEXT_SIZE.w, DEBUG_TEXT_SIZE.h)
            # pygame.gfxdraw.rectangle(
            # self.surface, pygame.rect.Rect(top_left, DEBUG_TEXT_SIZE),
            # DEBUG_ORANGE)
            if isinstance(expr, boolean.NOT):
                overbar_height = self.max_not_count(
                    expr) * overbar_surface.get_rect().h
                dest = (top_left[0], top_left[1] - overbar_height)

                text = str(expr).replace(boolean.NOT.operator, "")
                expr_rect = self.font.get_rect(text)
                area = (0, 0, expr_rect.w, overbar_surface.get_rect().h)

                self.surface.blit(overbar_surface, dest, area)
                if isinstance(expr.args[0], boolean.NOT):
                    update_overbar(expr.args[0], top_left)
                elif isinstance(expr.args[0], boolean.DualBase):
                    # The "size" of a character depends on the next character
                    # If the argument of a NOT is a DualBase, it will always have parenthesis
                    # surrounding it
                    arg_rect = self.font.get_rect(text[1:])
                    parenthesis_w = expr_rect.w - arg_rect.w
                    new_top_left = (top_left[0] + parenthesis_w, top_left[1])
                    update_overbar(expr.args[0], new_top_left)
            elif isinstance(expr, boolean.DualBase):
                # The actual printed args, with extra parenthesis
                args = []
                for arg in expr.args:
                    if arg.isliteral or isinstance(arg, boolean.NOT):
                        args.append(str(arg).replace(boolean.NOT.operator, ""))
                    else:
                        args.append(
                            "({})".format(str(arg).replace(boolean.NOT.operator, "")))

                for arg in expr.args:
                    if isinstance(arg, boolean.Symbol) or isinstance(arg, boolean.BaseElement):
                        # End of the line, don't need to do anything
                        continue
                    # Bounding box for the whole expression
                    expr_rect = self.font.get_rect(
                        str(expr).replace(boolean.NOT.operator, ""))
                    # Text for the arg and every arg after it
                    after_text = expr.operator.join(
                        args[i] for i in range(expr.args.index(arg), len(expr.args)))
                    # Bounding box for the arg and every arg after it
                    after_rect = self.font.get_rect(after_text)
                    # Character size depends the next character
                    w = expr_rect.w - after_rect.w
                    new_top_left = (top_left[0] + w, top_left[1])
                    # Literals are not surrounded by parenthesis
                    # The NOT function puts an overbar around the parenthesis
                    if arg.isliteral or isinstance(arg, boolean.NOT):
                        update_overbar(arg, new_top_left)
                    else:
                        # Correct poisition for extra parenthesis
                        expr_rect = after_rect
                        after_rect = self.font.get_rect(after_text[1:])
                        parenthesis_w = expr_rect.w - after_rect.w
                        new_top_left = (
                            new_top_left[0] + parenthesis_w, new_top_left[1])
                        update_overbar(arg, new_top_left)

        text = self.text.replace(boolean.NOT.operator, "")
        overbar_height = self.max_not_count(
            self.expression) * overbar_surface.get_rect().h
        x = 1
        y = 1 + overbar_height
        # Draw the expression
        self.font.render_to(self.surface,
                            (x, y),
                            text,
                            bgcolor=self.bgcolor)
        # Actually draw the overbar
        update_overbar(self.expression, (x, y))


# TODO: Make the boxes different sizes so the truth table takes less space
class TruthTable(interfaces.IContainer):

    """
    A renderable truth table.
    """

    def __init__(self,
                 expression,
                 hitbox,
                 hidden=False,
                 font_size=50,
                 fgcolor=pygame.color.THECOLORS["black"],
                 bgcolor=pygame.color.THECOLORS["white"],
                 font_name="Calibri"):
        self.expression = expression
        self.fgcolor = fgcolor
        self.font_name = font_name
        self.font_size = font_size

        if len(hitbox) == 2:
            hitbox += self.fit_surface()
        super().__init__(hitbox,
                         hidden=hidden,
                         bgcolor=bgcolor)

    def __repr__(self):
        return "<{name}({hitbox}, {text})>".format(name=self.__class__.__name__,
                                                   hitbox=repr(self.hitbox),
                                                   text=repr(self.text))

    @property
    def text(self):
        return str(self.expression)

    @text.setter
    def text(self, string):
        self.expression = string

    @property
    def expression(self):
        return self._expression

    @expression.setter
    def expression(self, expression):
        if isinstance(expression, str):
            expression = boolean.parse(expression, False)
        if not isinstance(expression, boolean.Expression):
            raise TypeError(
                "Argument must be str or Expression but it is {}"
                .format(expression.__class__))
        self._expression = expression
        self.table = expression

    # Table is in the format:
    # [
    #     {<column_heading>:<value>, <column_heading>:<value>},
    #     {<column_heading>:<value>, <column_heading>:<value>},
    #     ...
    # ]
    # Each index of the array is dictionary which contains the values of a different row.
    # Columns are given headings which can also the a number.
    @property
    def table(self):
        return self._table

    @table.setter
    def table(self, table):
        if isinstance(table, str):
            table = boolean.parse(table, False)
        if isinstance(table, boolean.Expression):
            table = boolean.truth_table(table)
        else:
            raise TypeError(
                "Argument must be Expression but it is {}"
                .format(table.__class__))
        # Table should not be directly modified
        self._table = tuple(table)
        self.dirty = True

    @property
    def font_size(self):
        return self._font_size

    @font_size.setter
    def font_size(self, font_size):
        self._font_size = float(font_size)
        self.dirty = True

    @property
    def fgcolor(self):
        return self._fgcolor

    @fgcolor.setter
    def fgcolor(self, fgcolor):
        if isinstance(fgcolor, (tuple, list, pygame.color.Color)):
            self._fgcolor = pygame.color.Color(*fgcolor)
        else:
            self._fgcolor = pygame.color.Color(fgcolor)
        self.dirty = True

    @property
    def font_name(self):
        return self._font_name

    # I'm not sure why you'd want to do this...
    @font_name.setter
    def font_name(self, font_name):
        # Throws an error if the font doesn't exist
        if pygame.freetype.match_font(font_name) is None:
            raise ValueError(
                "Font of name {name} not found".format(name=font_name))
        self._font_name = str(font_name)
        self.dirty = True

    def box_size(self):
        # Helper function to create a new expression quickly
        # Font color and background color don't matter if you just
        # want the size
        def new_expression(expr, pos=(0, 0)):
            return Expression(expr,
                              pos,
                              size=self.font_size,
                              name=self.font_name)

        all_text = [new_expression(e) for e in self.table[0].keys()] +\
                   [new_expression(boolean.TRUE),
                    new_expression(boolean.FALSE)]

        box_w = max(e.w for e in all_text)
        box_h = max(e.h for e in all_text)

        return (box_w + 2, box_h + 2)

    def fit_surface(self):
        box_size = self.box_size()

        w = box_size[0] * len(self.table[0].keys())
        h = box_size[1] * (len(self.table) + 1)

        return (w + 2, h + 2)

    def update_renderable_list(self):
        def new_expression(expr, pos=(0, 0)):
            return Expression(expr,
                              pos,
                              size=self.font_size,
                              fgcolor=self.fgcolor,
                              bgcolor=self.bgcolor,
                              name=self.font_name)

        def sort_key(expr):
            symbol_length = len(expr.symbols)
            string_length = len(str(expr))
            string_value = float("inf")
            if isinstance(expr, boolean.Symbol):
                string_value = str(expr)
            return (symbol_length, string_length, string_value)

        renderable_list = []

        sorted_column_headings = sorted(self.table[0].keys(),
                                        key=sort_key)

        box_size = self.box_size()
        box_w = box_size[0]
        box_h = box_size[1]

        # TODO: Use enumerate instead
        x = 1
        for column in sorted_column_headings:
            y = 1

            heading = new_expression(column)
            heading.top_left = (x, y)
            heading.align((x, y, box_w, box_h), alignment.center_middle)

            renderable_list.append(heading)

            for row in self.table:
                y += box_h

                value = new_expression(row[column])
                value.top_left = (x, y)
                value.align((x, y, box_w, box_h), alignment.center_middle)

                renderable_list.append(value)
            x += box_w

        self.renderable_list = renderable_list

    def update_surface(self):
        super().update_surface()

        box_size = self.box_size()
        box_w = box_size[0]
        box_h = box_size[1]

        # Draw the lines 
        for i in range(len(self.table[0].keys()) + 1):
            x = box_w * i if i != 0 else 1
            pygame.gfxdraw.line(
                self.surface, x, 1, x, self.h - 2, self.fgcolor)
        for i in range(len(self.table) + 2):
            y = box_h * i if i != 0 else 1
            pygame.gfxdraw.line(
                self.surface, 1, y, self.w - 2, y, self.fgcolor)
