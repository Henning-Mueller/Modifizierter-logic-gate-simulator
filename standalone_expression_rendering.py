"""
This module implements expression rendering without any external libraries.
"""
import pygame
import pygame.freetype

# Constants for boolean expressions
TRUE = "1"
FALSE = "0"
AND = "∙"
OR = "+"
NOT = "~"
OPEN_P = "("
CLOSE_P = ")"
OPERATORS = (TRUE, FALSE, AND, OR, NOT, OPEN_P, CLOSE_P)
# Symbols/Inputs can only be capital letters
INPUTS = tuple(chr(i) for i in range(ord("A"), ord("Z")))


def bNotCount(string) -> int:
    '''
    Returns the number of NOTs at the start of the string.

    If none are found, returns 0.
    This function does not test "string" to see if it is a valid binary expression.
    '''
    notCount = 0
    for c in string:
        if c == NOT:
            notCount += 1
        else:
            return notCount
    return notCount


def bParentheses(string) -> str:
    '''
    Finds and returns the closing parentheses for the first open parentheses,
    returning the string between them.

    The parentheses are not returned with the string.
    This function does not test "string" to see if it is a valid binary expression,
    but if it does not find any opening parenthesis or a closing parenthesis,
    it will raise a ValueError.
    '''
    index = string.find(OPEN_P)
    if index == -1:
        raise ValueError(
            '"' + string + '"' + "does not contain any opening parentheses.")
    depth = 1
    for i in range(index + 1, len(string)):
        if string[i] == OPEN_P:
            depth += 1
        if string[i] == CLOSE_P:
            depth -= 1
        if depth == 0:
            return string[index + 1:i]
    raise ValueError(
        '"' + string + '"' + "does not close its opening parentheses")


def bSplitInfix(string) -> str:
    '''
    Takes a given string containing any kind of expression seperated by infix operators
    and returns an array of expressions.

    The string must should not have outer parenthesis.
    This function does not test "string" to see if it is a valid binary expression.
    '''
    depth = 0
    array = []
    for i in range(len(string)):
        if string[i] == OPEN_P:
            depth += 1
        if string[i] == CLOSE_P:
            depth -= 1
        if depth == 0 and string[i] in (AND, OR):
            array.append(string[:i])
            array += bSplitInfix(string[i + 1:])
            break
    if depth == 0 and array == []:
        array.append(string)
    return array


def bExpression(string) -> str:
    '''
    Returns the first binary expression found in string.

    This function does not test "string" to see if it is a valid binary expression.
    '''
    # forward until no more NOTs
    # forward until depth == 0 and
    first = [string.find(I) for I in INPUTS if string.find(I) != -1]
    if string.find(OPEN_P) != -1:
        first.append(string.find(OPEN_P))
    first = min(first)

    depth = 0
    for i in range(first, len(string)):
        if string[i] == OPEN_P:
            depth += 1
        if string[i] == CLOSE_P:
            depth -= 1
        if depth == 0:
            if string[i] in (AND, OR):
                return string[:i]
            if string[i] == CLOSE_P:
                return string[:i + 1]
            if string[i] in INPUTS:
                return string[:i + 1]
    return string

pygame.freetype.init()


# A wrapper around pygame.freetype.font
class font:
    """
    A base class for text.
    """
    # X:
    LEFT = 0
    MIDDLE = 1
    RIGHT = 2
    # Y:
    TOP = 0
    CENTER = 1
    BOTTOM = 2

    def __init__(self,
                 text,
                 size=24,  # float size or (float size, float stretch up/down)
                 position=(0, 0),
                 align = (0, 0),
                 fgcolor = pygame.color.THECOLORS["black"],
                 bgcolor = pygame.color.THECOLORS["white"],
                 underline = False,
                 strong = False,  # bold
                 oblique = False,  # italic
                 name = "Calibri"):
        self.font = pygame.freetype.SysFont(name, size, strong, oblique)
        self.font.underline = underline
        self.font.fgcolor = fgcolor
        self.position = position
        self.bgcolor = bgcolor
        self.align = align
        self._text = ""

        self.text = text

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, string):
        self._text = str(string)

    def getActualPosition(self, line):
        lines = self._text.split("\n")

        if self.align[0] == self.TOP:
            y = self.position[1] + line * \
                self.font.get_rect(lines[line]).height
        elif self.align[0] == self.CENTER:
            y = self.position[
                1] + self.font.get_rect(lines[line]).height * (line - len(lines) / 2)
        elif self.align[0] == self.BOTTOM:
            y = self.position[
                1] + self.font.get_rect(lines[line]).height * (line - len(lines))

        if self.align[1] == self.LEFT:
            x = self.position[0]
        elif self.align[1] == self.MIDDLE:
            x = self.position[0] - \
                int(self.font.get_rect(lines[line]).width / 2)
        elif self.align[1] == self.RIGHT:
            x = self.position[0] - self.font.get_rect(lines[line]).width

        return (x, y)

    def render(self, surface):
        lines = self._text.split("\n")

        for i in range(len(lines)):
            self.font.render_to(surface,
                                self.getActualPosition(i),
                                lines[i],
                                bgcolor=self.bgcolor)


class bFont(font):
    """
    Class for rendering boolean expressions.
    """

    def __init__(self,
                 text,
                 size=24,  # float size or (float size, float stretch up/down)
                 position=(0, 0),
                 align = (0, 0),
                 fgcolor = pygame.color.THECOLORS["black"],
                 bgcolor = pygame.color.THECOLORS["white"],
                 underline = False,
                 strong = False,  # bold
                 oblique = False,  # italic
                 name = "Calibri"):
        if text.find("\n") != -1:
            raise ValueError(text + " contains newline characters")
        self.expression = text
        super().__init__(text,
                         size,
                         position,
                         align,
                         fgcolor,
                         bgcolor,
                         underline,
                         strong,
                         oblique,
                         name)

    @property
    def text(self):
        return self.expression

    @text.setter
    def text(self, string):
        if self._text.find("\n") != -1:
            raise ValueError(text + " contains newline characters")
        self.expression = str(string)
        self._text = string.replace(NOT, "")

    # given part of an expression, return the height multiplier
    @staticmethod
    def getHeightMultiplier(expression):
        heightMultiplier = bNotCount(expression)
        expression = expression[heightMultiplier:]
        if expression[0] == OPEN_P:
            expression = bParentheses(expression)
            array = bSplitInfix(expression)
            array = [bFont.getHeightMultiplier(e) for e in array]
            heightMultiplier += max(array)
        return heightMultiplier

    # TODO?: Cache values for font from 1-some_value when this is loaded
    # TODO: make lines of different colors to match
    def render(self, surface):
        oldUnderline = self.font.underline
        oldUnderlineAdjustment = self.font.underline_adjustment
        self.font.underline = True
        self.font.underline_adjustment = -1

        testSurface = self.font.render(self._text, bgcolor=self.bgcolor)[0]

        for i in range(testSurface.get_rect().h):
            if testSurface.get_at((0, i)) == self.bgcolor:
                overbarHeight = i
                break
        overbarAbove = testSurface.get_rect().h - \
            self.font.get_rect(self._text).h

        index = self.expression.rfind(NOT)
        while index != -1:
            beforeRect = self.font.get_rect(
                self.expression[:index].replace(NOT, "")).width
            textLength = len(bExpression(self.expression[index:]))
            textRect = self.font.get_rect(
                self.expression[:index + textLength].replace(NOT, "")).width
            x, y = self.getActualPosition(0)  # (x, y)
            overbar = pygame.Rect(x + beforeRect,
                                  y -
                                  (overbarAbove *
                                   self.getHeightMultiplier(self.expression[index:])),
                                  textRect - beforeRect,
                                  overbarHeight)

            pygame.draw.rect(surface, self.font.fgcolor, overbar)
            index = self.expression[:index].rfind(NOT)

        # freetype.render uses _text for rendering
        self.font.underline = oldUnderline
        self.font.underline_adjustment = oldUnderlineAdjustment

        super().render(surface)


if __name__ == "__main__":
    import threading

    pygame.init()
    pygame.display.init()

    pygame.display.set_mode((1080, 300), pygame.DOUBLEBUF)

    f = bFont(text="~A∙~(A+A)+~(~A∙A)+~~~(~A+~~(A∙~~A))",
              size=60,
              position=(1080 / 2, 300 / 3 + 300 / 6),
              align = (bFont.MIDDLE, bFont.CENTER))
    fReal = font(f.text,
                 f.font.size,
                 (1080 / 2, 2 * 300 / 3 + 300 / 6),
                 f.align)
    s = pygame.display.get_surface()

    running = True

    class editTextThread(threading.Thread):

        def __init__(self, font):
            super().__init__()
            self.font = font

        def run(self):
            print(
                "This program might crash if you do not enter a valid boolean expression")
            print()
            print("Use capital letters (A-Z) as inputs")
            print("Use \"~\" as NOT and \"(\" and \")\" as parentheses")
            print("Use + as OR and * as AND, which will be replaced with dot")
            print("Enter Q to quit.")
            print()
            global running
            while running:
                # hack to fix what was broken by super hack
                text = input("Enter a binary expression: ").replace("*", AND)
                text = text.replace("!", "~")
                if text.upper().startswith("Q"):
                    running = False
                else:
                    self.font.text = text
    thread1 = editTextThread(f)
    thread1.start()

    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
                break
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
                    break
        s.fill(pygame.color.THECOLORS["white"])

        fReal.text = f.text
        fReal.render(s)
        f.render(s)

        pygame.display.flip()
