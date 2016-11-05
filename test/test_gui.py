import sys
sys.path.append("..")

import unittest
import gui


class InputBoxTestCase(unittest.TestCase):

    def test_size(self):
        ib = gui.InputBox("Some Long Default Text", (0, 0))
        fr = ib.render_text.font.get_rect("Some Default Text")
        self.assertTrue(ib.w > fr.w)
        self.assertTrue(ib.h > fr.h)

        ib.text = "Less Text"
        self.assertTrue(ib.render_text.hitbox.topleft[0] in (1, 0))
        ib.text = "More Text Than The Default Text To Align Right"
        self.assertTrue(
            ib.render_text.hitbox.topright[0] in (ib.hitbox.w, ib.hitbox.w - 1))

        ib = gui.InputBox("Some Default Text",
                          (0, 0, 30))
        fr = ib.render_text.font.get_rect("Some Default Text")
        self.assertTrue(ib.w > fr.w)
        self.assertEqual(ib.h, 30)

    def test_select_deselect(self):
        ib = gui.InputBox("Some Long Default Text", (0, 0))
        l = []

        md = gui.interfaces.new_event(
            gui.pygame.event.Event(
                gui.pygame.MOUSEBUTTONDOWN,
                {"pos": (1, 1), "button": 1}))
        l.append(md)
        ib.update([ib], [0], l)
        self.assertTrue(ib.selected)
        self.assertEqual(ib.text, "")
        l.pop()

        mu = gui.interfaces.new_event(
            gui.pygame.event.Event(
                gui.pygame.MOUSEBUTTONUP,
                {"pos": (1, 1), "button": 1}))
        l.append(mu)
        ib.update([ib], [0], l)
        self.assertTrue(ib.selected)
        l.pop()

        md = gui.interfaces.new_event(
            gui.pygame.event.Event(
                gui.pygame.MOUSEBUTTONDOWN,
                {"pos": (-1, -1), "button": 1}))
        l.append(md)
        ib.update([ib], [0], l)
        self.assertFalse(ib.selected)
        self.assertEqual(ib.text, ib._default_text)

    def test_key_presses(self):
        ib = gui.InputBox("Some Long Default Text", (0, 0))
        l = []

        md = gui.interfaces.new_event(
            gui.pygame.event.Event(
                gui.pygame.MOUSEBUTTONDOWN,
                {"pos": (1, 1), "button": 1}))
        l.append(md)
        ib.update([ib], [0], l)
        l.pop()

        old_text = ib.text
        kd = gui.interfaces.new_event(
            gui.pygame.event.Event(
                gui.pygame.KEYDOWN,
                {"key": 0, "unicode": chr(0)}))
        l.append(kd)
        ib.update([ib], [1], l)
        self.assertEqual(old_text, ib.text)

        kd = gui.interfaces.new_event(
            gui.pygame.event.Event(
                gui.pygame.KEYDOWN,
                {"key": ord("A"), "unicode": "A"}))
        l.append(kd)
        ib.update([ib], [1], l)
        self.assertEqual(ib.text, "A")

        kd = gui.interfaces.new_event(
            gui.pygame.event.Event(
                gui.pygame.KEYDOWN,
                {"key": ord("B"), "unicode": "B"}))
        l.append(kd)
        ib.update([ib], [1], l)
        self.assertEqual(ib.text, "AB")

        kd = gui.interfaces.new_event(
            gui.pygame.event.Event(
                gui.pygame.KEYDOWN,
                {"key": gui.pygame.K_BACKSPACE,
                 "unicode": chr(gui.pygame.K_BACKSPACE)}))
        l.append(kd)
        ib.update([ib], [1], l)
        self.assertEqual(ib.text, "A")

        kd = gui.interfaces.new_event(
            gui.pygame.event.Event(
                gui.pygame.KEYDOWN,
                {"key": gui.pygame.K_DELETE,
                 "unicode": chr(gui.pygame.K_DELETE)}))
        l.append(kd)
        ib.update([ib], [1], l)
        self.assertEqual(ib.text, "")

        kd = gui.interfaces.new_event(
            gui.pygame.event.Event(
                gui.pygame.KEYDOWN,
                {"key": gui.pygame.K_RETURN,
                 "unicode": chr(gui.pygame.K_RETURN)}))
        l.append(kd)
        ib.update([ib], [1], l)
        self.assertFalse(ib.selected)
        self.assertEqual(ib.text, ib._default_text)


class TextButtonTestCase(unittest.TestCase):

    def test_size(self):
        tb = gui.TextButton("Some Long Default Text", (0, 0))
        fr = tb.render_text.font.get_rect("Some Default Text")
        self.assertTrue(tb.w > fr.w)
        self.assertTrue(tb.h > fr.h)

        tb = gui.TextButton("Some Default Text",
                            (0, 0, 30))
        fr = tb.render_text.font.get_rect("Some Default Text")
        self.assertTrue(tb.w > fr.w)
        self.assertEqual(tb.h, 30)

    def test_function_call(self):
        def foo(a, b, c, d):
            global ga
            global gb
            global gc
            global gd
            ga = a
            gb = b
            gc = c
            gd = d

        tb = gui.TextButton("Some Text",
                            (0, 0),
                            foo)
        l = []

        md = gui.interfaces.new_event(
            gui.pygame.event.Event(
                gui.pygame.MOUSEBUTTONDOWN,
                {"pos": (1, 1), "button": 1}))
        l.append(md)
        tb.update([tb], [0], l)
        self.assertEqual(ga, tb)
        self.assertEqual(gb, [tb])
        self.assertEqual(gc, [0])
        self.assertEqual(gd, gui.interfaces.normal_events(l))

if __name__ == "__main__":
    unittest.main(verbosity=2)
