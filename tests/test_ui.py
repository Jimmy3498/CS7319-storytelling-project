import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HAS_STREAMLIT = importlib.util.find_spec("streamlit") is not None


@unittest.skipUnless(HAS_STREAMLIT, "Install requirements.txt for Streamlit AppTest")
class PreviewTests(unittest.TestCase):
    def test_all_pages_in_both_architecture_entrypoints(self):
        from streamlit.testing.v1 import AppTest

        from shared.ui.shell import PAGES

        for architecture in ("layered", "event_based"):
            app = AppTest.from_file(str(ROOT / architecture / "streamlit_app.py")).run(timeout=20)
            self.assertEqual(len(app.exception), 0, str(app.exception))
            for page in PAGES:
                with self.subTest(architecture=architecture, page=page):
                    app.radio[0].set_value(page).run(timeout=20)
                    self.assertEqual(len(app.exception), 0, str(app.exception))
                    for button in app.button:
                        if button.label not in ("Probe command route", "Refresh probe status"):
                            self.assertTrue(button.disabled, button.label)

    def test_each_app_has_fixed_architecture_and_probe(self):
        from streamlit.testing.v1 import AppTest

        self.assertFalse((ROOT / "app.py").exists())
        for package, label in (("layered", "Layered"), ("event_based", "Event-Based")):
            app = AppTest.from_file(str(ROOT / package / "streamlit_app.py")).run(timeout=20)
            self.assertEqual(len(app.exception), 0)
            self.assertFalse(any(widget.label == "Architecture" for widget in app.selectbox))
            self.assertTrue(any(c.value == f"Running: {label}" for c in app.caption))
            next(b for b in app.button if b.label == "Probe command route").click().run(timeout=20)
            self.assertEqual(len(app.exception), 0)
            next(b for b in app.button if b.label == "Refresh probe status").click().run(timeout=20)
            self.assertEqual(len(app.exception), 0)
            expected = {"unimplemented"} if package == "layered" else {"pending", "unimplemented"}
            self.assertTrue(any(str(m.value).strip() in expected for m in app.markdown))
            self.assertFalse(any(str(m.value).strip() == "completed" for m in app.markdown))
