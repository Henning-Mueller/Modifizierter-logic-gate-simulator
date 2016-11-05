import sys
sys.path.append("..")

import unittest
import logic_circuit as lc


class ComponentTestCase(unittest.TestCase):

    def test_component(self):
        c = lc.Component()
        self.assertEqual(c.inputs, {})
        self.assertEqual(c.output, None)
        self.assertEqual(c.expression, None)
        self.assertEqual(c.empty_input_keys, ())


class GateTestCase(unittest.TestCase):

    def test_propagation(self):
        s = lc.Switch()

        g = lc.Gate("A")
        self.assertNotEqual(g.empty_input_keys, ())
        self.assertEqual(g.empty_input_keys, (g.expression,))
        self.assertEqual(g.inputs, {g.expression: None})
        self.assertEqual(g.output, None)
        g.inputs[g.empty_input_keys[0]] = s
        g.update()
        self.assertEqual(g.output, False)
        s.output = True
        g.update()
        self.assertEqual(g.output, True)
        s.output = False
        self.assertEqual(g.output, True)

    def test_remove(self):
        s = lc.Switch()
        g = lc.Gate("A", {"A": s})
        b = [s, g]
        self.assertNotEqual(g.empty_input_keys, (g.expression,))
        s.remove(b)
        self.assertEqual(g.empty_input_keys, (g.expression,))

        s = lc.Switch()
        g = lc.Gate("A", {"A": s})
        b = [s, g]
        self.assertNotEqual(g.empty_input_keys, (g.expression,))
        g.remove(b)
        self.assertEqual(g.empty_input_keys, (g.expression,))

    def test_anonymous(self):
        s = lc.Switch()

        g = lc.Gate("A", {"A": s}, False)
        self.assertEqual(g.empty_input_keys, ())
        self.assertEqual(str(g.expression), "A")
        self.assertTrue(lc.boolean.Symbol("A") in g.inputs.keys())
        self.assertTrue(s in g.inputs.values())
        self.assertIsInstance(list(g.inputs.keys())[0], lc.boolean.Expression)


class FunctionGateTestCase(unittest.TestCase):

    def test_and(self):
        s1 = lc.Switch()
        s2 = lc.Switch()

        g = lc.And((s1, s2))
        self.assertEqual(g.output, None)
        g.update()
        self.assertEqual(g.output, False)
        s1.output = True
        g.update()
        self.assertEqual(g.output, False)
        s2.output = True
        g.update()
        self.assertEqual(g.output, True)
        s1.output = False
        g.update()
        self.assertEqual(g.output, False)

    def test_or(self):
        s1 = lc.Switch()
        s2 = lc.Switch()

        g = lc.Or((s1, s2))
        self.assertEqual(g.output, None)
        g.update()
        self.assertEqual(g.output, False)
        s1.output = True
        g.update()
        self.assertEqual(g.output, True)
        s2.output = True
        g.update()
        self.assertEqual(g.output, True)
        s1.output = False
        g.update()
        self.assertEqual(g.output, True)

    def test_not(self):
        s1 = lc.Switch()

        g = lc.Not(s1)
        self.assertEqual(g.output, None)
        g.update()
        self.assertEqual(g.output, True)
        s1.output = True
        g.update()
        self.assertEqual(g.output, False)

        g = lc.Not()
        g._output = True
        g.inputs[g.empty_input_keys[0]] = g
        self.assertEqual(g.output, True)
        g.update()
        self.assertEqual(g.output, False)
        g.update()
        self.assertEqual(g.output, True)


class CircuitBoardTestCase(unittest.TestCase):

    def test_board(self):
        s = lc.Switch()
        w = lc.Wire(s)
        b = lc.Bulb(w)

        cb = lc.CircuitBoard([s, w, b])

        self.assertEqual(s.output, False)
        self.assertEqual(w.output, None)
        self.assertEqual(w.output, None)

        cb.update()

        self.assertEqual(s.output, False)
        self.assertEqual(w.output, False)
        self.assertEqual(w.output, False)

        s.output = True
        cb.update()

        self.assertEqual(s.output, True)
        self.assertEqual(w.output, True)
        self.assertEqual(w.output, True)


class ConvertTestCase(unittest.TestCase):

    def test_expression(self):
        self.assertIsInstance(lc.expression(lc.And()), lc.boolean.AND)
        self.assertIsInstance(lc.expression(lc.Bulb()), lc.boolean.Symbol)
        self.assertIsInstance(lc.expression(lc.Switch()), lc.boolean.Symbol)
        i = lc.Input()
        self.assertIsInstance(lc.expression(lc.And((i, i))).eval(),
                              lc.boolean.Symbol)

        self.assertEqual(lc.expression(lc.And()),
                         lc.boolean.parse("A*B"))
        self.assertNotEqual(lc.expression(lc.And(), True),
                            lc.boolean.parse("A*B"))

        self.assertTrue(
            all(
                True for s in lc.expression(lc.And()).symbols
                if s is None)
        )

    def test_circuit_board(self):
        self.assertIsInstance(lc.circuit_board("A"), lc.CircuitBoard)

        expr_list = (lc.boolean.parse("A"),
                     lc.boolean.parse("A+B"),
                     lc.boolean.parse("A+(B*~C)"),
                     lc.boolean.parse("~(A+B)"),
                     lc.boolean.parse("~A+~B+~C+~D"))
        for expr in expr_list:
            self.assertEqual(expr,
                             lc.expression(lc.circuit_board(expr)[-1]).eval())


if __name__ == "__main__":
    unittest.main(verbosity=2)
