import sys
sys.path.append("..")

import unittest
import text


class RenderError(Exception):
    pass


class TextTestCase(unittest.TestCase):

    def test_creation(self):
        t = text.Text("abcdefgh\nijklmnopqrstuvwxyz", (0, 0))
        t = text.Text("abcdefg\nhijkl\nmnopqrst\nuvwxyz", (0, 0, 500, 500))

    def test_properties(self):
        t = text.Text("abcdefghijklmnopqrstuvwxyz", (0, 0))
        t.dirty = False

        t.size = t.size + 5
        self.assertTrue(t.dirty)
        t.dirty = False

        t.text = t.text.upper()
        self.assertTrue(t.dirty)
        t.dirty = False

        t.bgcolor = (0, 0, 0)
        self.assertTrue(t.dirty)
        t.dirty = False

        t.bgcolor = [255, 255, 255, 255]
        self.assertTrue(t.dirty)
        t.dirty = False

        t.bgcolor = text.pygame.color.Color("red")
        self.assertTrue(t.dirty)
        t.dirty = False

        t.bgcolor = "black"
        self.assertTrue(t.dirty)
        t.dirty = False

        t.fgcolor = (0, 0, 0)
        self.assertTrue(t.dirty)
        t.dirty = False

        t.fgcolor = [255, 255, 255, 255]
        self.assertTrue(t.dirty)
        t.dirty = False

        t.fgcolor = text.pygame.color.Color("red")
        self.assertTrue(t.dirty)
        t.dirty = False

        t.fgcolor = "white"
        self.assertTrue(t.dirty)
        t.dirty = False

        t.underline = not t.underline
        self.assertTrue(t.dirty)
        t.dirty = False

        t.strong = not t.strong
        self.assertTrue(t.dirty)
        t.dirty = False

        t.oblique = not t.oblique
        self.assertTrue(t.dirty)

    def test_check_render(self):
        t = ("abcdefgh\nijklmnopqrs\ntuvwxyz\n"
             "ABCDE\nFGHIJKL\nMNOPQ\nRSTUVW\nXYZ")
        t = text.Text(t, (0, 0))

        text.pygame.image.save(t.render_surface(), "text.png")
        if bool(input(("\nCheck text.png.\n"
                       "If it rendered correctly then press enter.\n"
                       "If not type a key before pressing enter."))):
            raise RenderError(str(t))


class ExpressionTestCase(unittest.TestCase):

    def test_creation(self):
        t = text.Expression("~A*~(A+A)+~(~A*A)+~~~(~A+~~(A*~~A))", (0, 0))
        t = text.Expression("~(~(~(A+~F)*~G)+~B+~~C)*~~(~~(~D*~E)+~(~F+~~D))",
                            (0, 0, 500, 500))

    def test_properties(self):
        t = text.Expression("A", (0, 0))
        t.text = "A+B+C"
        self.assertTrue(t.dirty)
        t.dirty = False
        t.expression = text.boolean.parse("C+D*E")
        self.assertTrue(t.dirty)

    def test_check_render(self):
        t = text.Expression("~(~(~(A+~F)*~G)+~B+~~C)*~~(~~(~D*~E)+~(~F+~~D))",
                            (0, 0))

        text.pygame.image.save(t.render_surface(), "text.png")
        if bool(input(("\nCheck text.png.\n"
                       "If it rendered correctly then press enter.\n"
                       "If not type a key before pressing enter."))):
            raise RenderError(str(t))


class TruthTableTestCase(unittest.TestCase):

    def test_creation(self):
        t = text.TruthTable("~A*~(A+A)+~(~A*A)+~~~(~A+~~(A*~~A))", (0, 0))
        t = text.TruthTable("~(~(~(A+~F)*~G)+~B+~~C)*~~(~~(~D*~E)+~(~F+~~D))",
                            (0, 0, 500, 500))

    def test_properties(self):
        t = text.TruthTable("A", (0, 0))
        t.text = "A+B+C"
        self.assertTrue(t.dirty)
        t.dirty = False
        t.expression = text.boolean.parse("C+D*E")
        self.assertTrue(t.dirty)

    def test_check_render(self):
        t = text.TruthTable("~A*~(A+A)+~(~A*A)+~~~(~A+~~(A*~~A))", (0, 0))

        text.pygame.image.save(t.render_surface(), "text.png")
        if bool(input(("\nCheck text.png.\n"
                       "If it rendered correctly then press enter.\n"
                       "If not type a key before pressing enter."))):
            raise RenderError(str(t))

if __name__ == "__main__":
    unittest.main(verbosity=2)
