import sys
sys.path.append("..")

import unittest
import interfaces


class EventTestCase(unittest.TestCase):

    def test_events_shifters(self):
        events = [interfaces.pygame.event.Event(i)
                  for i in range(interfaces.pygame.USEREVENT)]
        self.assertEqual(events,
                         interfaces.normal_events(
                             interfaces.new_events(events)))


class RenderableTestCase(unittest.TestCase):

    def test_hidden(self):
        r = interfaces.IRenderable((100, 100, 100, 100))

        s = r.render_surface()
        self.assertFalse(r.dirty)
        self.assertEqual((s.get_rect().w, s.get_rect().h),
                         (r.w, r.h))

        r.hidden = True
        s = r.render_surface()
        self.assertEqual((s.get_rect().w, s.get_rect().h),
                         (0, 0))

    def text_new(self):
        r = interfaces.IRenderable((100, 100, 100, 100))
        self.assertTrue(r.dirty)

    def test_move(self):
        r = interfaces.IRenderable((100, 100, 100, 100))
        old_top_left = r.top_left
        r.move((10, 10))
        self.assertEqual(r.top_left,
                         (old_top_left[0] + 10, old_top_left[0] + 10))

    def test_align(self):
        r = interfaces.IRenderable((100, 100, 100, 100))
        pos = (0, 0)

        r.align(pos, interfaces.alignment.top_left)
        self.assertEqual(r.hitbox.topleft, pos)
        r.align(pos, interfaces.alignment.top_middle)
        self.assertEqual(r.hitbox.topleft, (pos[0] - r.w / 2, pos[1]))
        r.align(pos, interfaces.alignment.top_right)
        self.assertEqual(r.hitbox.topright, pos)

        r.align(pos, interfaces.alignment.middle_left)
        self.assertEqual(r.hitbox.midleft, pos)
        r.align(pos, interfaces.alignment.middle_middle)
        self.assertEqual(r.hitbox.midleft, (pos[1] - r.w / 2, pos[1]))
        r.align(pos, interfaces.alignment.middle_right)
        self.assertEqual(r.hitbox.midright, pos)

        r.align(pos, interfaces.alignment.bottom_left)
        self.assertEqual(r.hitbox.bottomleft, pos)
        r.align(pos, interfaces.alignment.bottom_middle)
        self.assertEqual(r.hitbox.bottomleft, (pos[1] - r.w / 2, pos[1]))
        r.align(pos, interfaces.alignment.bottom_right)
        self.assertEqual(r.hitbox.bottomright, pos)

    def test_pickle(self):
        import pickle
        r = interfaces.IRenderable((100, 100, 100, 100))
        r.pickle("test_interfaces.pickle")
        with open("test_interfaces.pickle", "rb") as f:
            r1 = pickle.load(f)

        self.assertEqual(r1.dirty, r.dirty)
        self.assertEqual(r1.hidden, r.hidden)
        self.assertEqual(r1.hitbox, r.hitbox)
        for x, y in zip(range(r.w), range(r.h)):
            self.assertEqual(r1.render_surface().get_at((x, y)),
                             r.render_surface().get_at((x, y)))


class InteractableTestCase(unittest.TestCase):

    def test_outline(self):
        i = interfaces.IInteractable((100, 100, 100, 100))
        s = i.render_surface()
        for x in range(i.w):
            self.assertEqual((0, 0, 255, 255), s.get_at((x, 0)))
            self.assertEqual((0, 0, 255, 255), s.get_at((x, i.h - 1)))
        i.selected = True
        s = i.render_surface()
        for x in range(i.w):
            self.assertEqual((0, 255, 255, 255), s.get_at((x, 0)))
            self.assertEqual((0, 255, 255, 255), s.get_at((x, i.h - 1)))

    def test_select(self):
        r = interfaces.IInteractable((100, 100, 100, 100))
        l = []

        md = interfaces.new_event(
            interfaces.pygame.event.Event(
                interfaces.pygame.MOUSEBUTTONDOWN,
                {"pos": (150, 150), "button": 1}))
        l.append(md)
        r.update([r], [0], l)
        self.assertTrue(r.selected)
        l.pop()

        mm = interfaces.new_event(
            interfaces.pygame.event.Event(
                interfaces.pygame.MOUSEMOTION,
                {"pos": (150, 150), "button": 1, "rel": (1, 1)}))
        l.append(mm)
        r.update([r], [0], l)
        self.assertEqual(l[0].type, interfaces.pygame.MOUSEMOTION)

        mu = interfaces.new_event(
            interfaces.pygame.event.Event(
                interfaces.pygame.MOUSEBUTTONUP,
                {"pos": (150, 150), "button": 1}))
        l.append(mu)
        r.update([r], [0], l)
        self.assertFalse(r.selected)


class DraggableTestCase(unittest.TestCase):

    def test_drag(self):
        r = interfaces.IDraggable((100, 100, 100, 100))
        l = []

        md = interfaces.new_event(
            interfaces.pygame.event.Event(
                interfaces.pygame.MOUSEBUTTONDOWN,
                {"pos": (150, 150), "button": 1}))
        l.append(md)
        r.update([r], [0], l)
        self.assertTrue(r.selected)
        l.pop()

        old_pos = r.top_left
        mm = interfaces.new_event(
            interfaces.pygame.event.Event(
                interfaces.pygame.MOUSEMOTION,
                {"pos": (150, 150), "buttons": (1, 0, 0), "rel": (1, 1)}))
        l.append(mm)
        r.update([r], [0], l)
        self.assertEqual(l[0].type, interfaces.pygame.MOUSEMOTION)
        self.assertEqual((old_pos[0] + 1, old_pos[1] + 1), r.top_left)

        mu = interfaces.new_event(
            interfaces.pygame.event.Event(
                interfaces.pygame.MOUSEBUTTONUP,
                {"pos": (150, 150), "button": 1}))
        l.append(mu)
        r.update([r], [0], l)
        self.assertFalse(r.selected)


class ContainerTestCase(unittest.TestCase):

    def test_dirty(self):
        r1 = interfaces.IInteractable((50, 50, 100, 100))
        r2 = interfaces.IInteractable((50, 50, 100, 100))
        c = interfaces.IContainer((0, 0, 200, 200), [r1, r2])

        c.render_surface()
        self.assertFalse(r1.dirty)
        self.assertFalse(c.dirty)

        e = []

        r1.dirty = True
        c.update([c], [0], e)
        self.assertTrue(c.dirty)

        md = interfaces.new_event(
            interfaces.pygame.event.Event(
                interfaces.pygame.MOUSEBUTTONDOWN,
                {"pos": (100, 100), "button": 1}))
        e.append(md)
        c.update([c], [0], e)
        self.assertTrue(r1.selected)
        self.assertFalse(r2.selected)

    def test_pickle(self):
        import pickle
        r = interfaces.IInteractable((50, 50, 100, 100))
        c = interfaces.IContainer((0, 0, 200, 200), [r])

        c.pickle("test_interfaces.pickle")
        with open("test_interfaces.pickle", "rb") as f:
            c1 = pickle.load(f)

        self.assertEqual(c1.dirty, c.dirty)
        self.assertEqual(c1.hidden, c.hidden)
        self.assertEqual(c1.hitbox, c.hitbox)
        for x, y in zip(range(c.w), range(c.h)):
            self.assertEqual(c1.render_surface().get_at((x, y)),
                             c.render_surface().get_at((x, y)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
