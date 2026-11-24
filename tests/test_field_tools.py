"""Field tools: deterministic clock and state transitions."""
import sys
import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from acpa_msmda.field_tools import Timer, change_count, rotation_assignments, observation_change, next_rotation

class FieldTests(unittest.TestCase):
    def test_timer_pause_resume(self):
        timer = Timer.new(60).start(100)
        self.assertEqual(timer.seconds_left(110), 50)
        paused = timer.pause(110)
        self.assertEqual(paused.seconds_left(500), 50)
        resumed = paused.start(500)
        self.assertEqual(resumed.seconds_left(549.1), 1)
        self.assertEqual(resumed.seconds_left(550), 0)
        self.assertEqual(resumed.seconds_left(800), 0)
        self.assertEqual(resumed.pause(800).remaining, 0)
        with self.assertRaises(ValueError):
            Timer.new(0)

    def test_counter_invariants(self):
        self.assertEqual(change_count(0,-1), 0)
        self.assertEqual(observation_change(0,0,1,1), (0,0))
        self.assertEqual(observation_change(3,3,0,-1), (2,2))
        self.assertEqual(observation_change(3,2,1,1), (3,3))
        self.assertEqual(observation_change(3,0,1,-1), (3,0))

    def test_rotations(self):
        for count in range(1,9):
            for group in range(count):
                self.assertEqual({rotation_assignments(count,step)[group] for step in range(count)}, set(range(1,count+1)))
        timer = Timer.new(60).start(100)
        self.assertEqual(next_rotation(0,3,timer,159)[0], 0)
        step, new = next_rotation(0,3,timer,160)
        self.assertEqual(step,1)
        self.assertIsNone(new.started)
        self.assertEqual(new.seconds_left(500),60)
        self.assertEqual(next_rotation(2,3,timer,200)[0],2)

    def test_page_opens_and_counters(self):
        app = AppTest.from_file(str(ROOT / "pages/6_Mode_Terrain.py"), default_timeout=30)
        app.session_state["lang"] = "fr"
        app.run()
        self.assertFalse(app.exception)
        app.radio[0].set_value("Compteurs").run()
        self.assertFalse(app.exception)
        app.button(key="field_count_0plus").click().run()
        app.button(key="field_count_1plus").click().run()
        app.button(key="field_count_1plus").click().run()
        self.assertEqual(app.session_state["acpa_store"]["field_count_1"],1)
        app.radio[0].set_value("Rotations").run()
        self.assertFalse(app.exception)
