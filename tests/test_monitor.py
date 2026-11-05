"""Synthetic monitor fixtures only; these tests never contact a compositor."""
import unittest
from unittest.mock import patch

import monitor


class PositionTests(unittest.TestCase):
    def setUp(self):
        self.target = dict(name="TEST-EXTERNAL", width=2400, height=1600,
                           scale=1, transform=0, refreshRate=60, x=0, y=0)
        self.reference = dict(name="TEST-INTERNAL", width=1600, height=1000,
                              scale=1, transform=0, refreshRate=60, x=100, y=50)

    def test_every_edge_and_alignment(self):
        expected = {
            "left": [(-2300, 50), (-2300, -250), (-2300, -550)],
            "right": [(1700, 50), (1700, -250), (1700, -550)],
            "above": [(100, -1550), (-300, -1550), (-700, -1550)],
            "below": [(100, 1050), (-300, 1050), (-700, 1050)],
        }
        for side, coordinates in expected.items():
            for alignment, xy in zip(("start", "center", "end"), coordinates):
                with self.subTest(side=side, alignment=alignment):
                    self.assertEqual(monitor.position(self.target, self.reference,
                                                      side, alignment), xy)

    def test_scaled_rotated_display(self):
        self.target.update(scale=2, transform=1)
        self.assertEqual(monitor.size(self.target), (800, 1200))
        self.assertEqual(monitor.position(self.target, self.reference,
                                         "right", "center"), (1700, -50))

    def test_plan_never_moves_display(self):
        with patch.object(monitor, "monitors", return_value=[self.target, self.reference]), \
                patch.object(monitor, "move") as move:
            result = monitor.main(["plan", "TEST-EXTERNAL", "TEST-INTERNAL", "above", "end"])
            self.assertEqual(result["position"], [-700, -1550])
            move.assert_not_called()

    def test_disconnected_or_same_display_rejected(self):
        with patch.object(monitor, "monitors", return_value=[self.target, self.reference]):
            for name in ("TEST-INTERNAL", "TEST-MISSING"):
                with self.subTest(target=name), self.assertRaises(ValueError):
                    monitor.main(["move", name, "TEST-INTERNAL", "right", "center"])

    def test_move_uses_lua_and_preserves_mode(self):
        with patch.object(monitor, "hypr", return_value="ok") as hypr:
            monitor.move(self.target, -2300, 50)
            command, code = hypr.call_args.args
            self.assertEqual(command, "eval")
            self.assertIn('position = "-2300x50"', code)
            self.assertIn('mode = "2400x1600@60.00000"', code)
            self.assertIn('output = "TEST-EXTERNAL"', code)

    def test_compositor_error_is_reported(self):
        with patch.object(monitor, "hypr", return_value="Lua error"), self.assertRaises(ValueError):
            monitor.move(self.target, 0, 0)

    def test_restore_uses_current_monitor(self):
        with patch.object(monitor, "monitors", return_value=[self.target]), \
                patch.object(monitor, "move") as move:
            monitor.main(["restore", '{"name":"TEST-EXTERNAL","x":-500,"y":200}'])
            move.assert_called_once_with(self.target, -500, 200)


if __name__ == "__main__":
    unittest.main()
