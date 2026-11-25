"""Public Streamlit behavior checks for the Mall Customers dashboard."""

import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "dashboard" / "app.py"
TIMEOUT = 60


def run_app() -> AppTest:
    return AppTest.from_file(str(APP), default_timeout=TIMEOUT).run(timeout=TIMEOUT)


def rendered_text(app: AppTest) -> str:
    return " ".join(item.value for item in app.markdown)


class DashboardFiltersTest(unittest.TestCase):
    def test_initial_render_shows_all_customers_and_three_views(self):
        app = run_app()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.tabs), 3)
        self.assertIn("100,0% de la muestra total", rendered_text(app))

    def test_filters_narrow_selection_and_reset_restores_defaults(self):
        app = run_app()
        app.multiselect(key="filter_genders").set_value(["Mujer"]).run(timeout=TIMEOUT)
        app.toggle(key="filter_exclude_unknown").set_value(True).run(timeout=TIMEOUT)
        self.assertFalse(app.exception)
        self.assertNotIn("100,0% de la muestra total", rendered_text(app))

        app.button[0].click().run(timeout=TIMEOUT)
        self.assertFalse(app.exception)
        for key in ("filter_genders", "filter_education", "filter_marital"):
            self.assertEqual(app.multiselect(key=key).value, [])
        self.assertEqual(app.slider(key="filter_age").value, (18, 70))
        self.assertEqual(app.slider(key="filter_income").value, (15, 137))
        self.assertEqual(app.slider(key="filter_spending").value, (1, 99))
        self.assertFalse(app.toggle(key="filter_exclude_unknown").value)
        self.assertIn("100,0% de la muestra total", rendered_text(app))

    def test_empty_selection_shows_warning_without_error(self):
        app = run_app()
        app.slider(key="filter_age").set_value((18, 18)).run(timeout=TIMEOUT)
        app.slider(key="filter_income").set_value((137, 137)).run(timeout=TIMEOUT)
        self.assertFalse(app.exception)
        self.assertTrue(any("no contiene clientes" in item.value for item in app.warning))


class DashboardPrivacyTest(unittest.TestCase):
    """RNF01: the shared dashboard exposes only aggregated results, never CustomerID."""

    def test_no_table_or_chart_exposes_customer_id(self):
        app = run_app()
        self.assertFalse(app.exception)
        for table in app.dataframe:
            columns = {str(column).lower() for column in table.value.columns}
            self.assertFalse(columns & {"customerid", "customer_id"}, columns)
        for chart in app.get("plotly_chart"):
            spec = chart.proto.spec
            self.assertNotIn("customer_id", spec)
            self.assertNotIn("CustomerID", spec)


if __name__ == "__main__":
    unittest.main()
