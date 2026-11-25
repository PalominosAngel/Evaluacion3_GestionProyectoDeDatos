"""Public Streamlit behavior checks for the EV3 dashboard."""

import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "dashboard" / "app.py"


class DashboardFiltersTest(unittest.TestCase):
    def test_genre_filter_and_reset(self):
        app = AppTest.from_file(str(APP), default_timeout=25).run(timeout=25)
        self.assertFalse(app.exception)
        self.assertEqual(len(app.tabs), 3)
        app.multiselect(key="filter_genres").set_value(["Drama"]).run(timeout=25)
        self.assertFalse(app.exception)
        self.assertEqual(app.multiselect(key="filter_genres").value, ["Drama"])
        self.assertTrue(any("14.772" in item.value for item in app.markdown))
        app.toggle(key="filter_only_rated").set_value(True).run(timeout=25)
        app.button[0].click().run(timeout=25)
        self.assertFalse(app.exception)
        self.assertEqual(app.multiselect(key="filter_types").value, ["Películas", "Series"])
        for key in ("filter_genres", "filter_countries", "filter_languages", "filter_ratings"):
            self.assertEqual(app.multiselect(key=key).value, [])
        self.assertEqual(app.slider(key="filter_years").value, (2010, 2025))
        self.assertFalse(app.toggle(key="filter_only_rated").value)
        self.assertTrue(any("32.000" in item.value for item in app.markdown))

    def test_sparse_genre_selection_and_empty_selection(self):
        app = AppTest.from_file(str(APP), default_timeout=25).run(timeout=25)
        app.multiselect(key="filter_countries").set_value(["United States of America"]).run(timeout=25)
        app.multiselect(key="filter_languages").set_value(["zh"]).run(timeout=25)
        self.assertFalse(app.exception)
        self.assertTrue(any("Ningún género" in item.value for item in app.info))
        app.button[0].click().run(timeout=25)
        app.multiselect(key="filter_types").set_value([]).run(timeout=25)
        self.assertFalse(app.exception)
        # No type selected means no restriction, as with the other optional filters.
        self.assertTrue(any("32.000" in item.value for item in app.markdown))
        app.multiselect(key="filter_types").set_value(["Películas"]).run(timeout=25)
        app.multiselect(key="filter_genres").set_value(["Soap"]).run(timeout=25)
        self.assertFalse(app.exception)
        self.assertTrue(any("no contiene títulos" in item.value for item in app.warning))


if __name__ == "__main__":
    unittest.main()
