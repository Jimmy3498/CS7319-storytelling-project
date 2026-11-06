import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import tomllib
import unittest
import zipfile
from pathlib import Path

from event_based.build import SPEC as EVENT_BASED
from layered.build import SPEC as LAYERED
from scripts.demo_bundle import ROOT, build_demo

HAS_STREAMLIT = importlib.util.find_spec("streamlit") is not None
SPECS = (LAYERED, EVENT_BASED)


class DemoBuildTests(unittest.TestCase):
    def test_each_target_creates_only_its_own_bundle_with_matching_checksums(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "build"
            for spec in SPECS:
                archive_path = build_demo(spec, output)
                bundle = output / spec.name
                other = "event_based" if spec.package == "layered" else "layered"
                self.assertTrue((bundle / spec.entrypoint).is_file())
                self.assertFalse((bundle / other).exists())
                self.assertFalse((bundle / "app.py").exists())
                self.assertFalse((bundle / spec.package / "build.py").exists())
                self.assertFalse((bundle / ".local").exists())
                self.assertEqual(
                    (bundle / spec.entrypoint).read_bytes(), (ROOT / spec.entrypoint).read_bytes()
                )
                manifest = json.loads((bundle / "BUILD.json").read_text())
                self.assertEqual(manifest["architecture"], spec.label)
                self.assertEqual(manifest["entrypoint"], spec.entrypoint)
                for record in manifest["files"]:
                    data = (bundle / record["path"]).read_bytes()
                    self.assertEqual(hashlib.sha256(data).hexdigest(), record["sha256"])
                config = tomllib.loads((bundle / ".streamlit/config.toml").read_text())
                self.assertEqual(config["server"]["port"], spec.port)
                self.assertEqual(config["server"]["address"], "127.0.0.1")
                with zipfile.ZipFile(archive_path) as archive:
                    self.assertIsNone(archive.testzip())
                    expected = {
                        f"{spec.name}/{path.relative_to(bundle).as_posix()}": path.read_bytes()
                        for path in bundle.rglob("*")
                        if path.is_file()
                    }
                    self.assertEqual(set(archive.namelist()), set(expected))
                    for filename, content in expected.items():
                        self.assertEqual(archive.read(filename), content)
                if spec is LAYERED:
                    self.assertEqual(
                        {p.name for p in output.iterdir()}, {spec.name, f"{spec.name}.zip"}
                    )
            self.assertEqual(
                (output / "layered-demo/fixtures/thornmere.json").read_bytes(),
                (output / "event-based-demo/fixtures/thornmere.json").read_bytes(),
            )

    def test_target_build_needs_only_own_source_and_shared_inputs(self):
        probe = textwrap.dedent("""
            import importlib.util
            import runpy
            import sys
            from pathlib import Path

            root, package, output = Path(sys.argv[1]).resolve(), sys.argv[2], sys.argv[3]
            sys.path.insert(0, str(root))
            opposite = "event_based" if package == "layered" else "layered"
            assert not (root / opposite).exists()
            assert importlib.util.find_spec(opposite) is None
            sys.argv = [package + ".build", "--output", output]
            runpy.run_module(package + ".build", run_name="__main__")
            assert not any(name.split(".")[0] == opposite for name in sys.modules)
            print("Target built without the other architecture's source or imports")
        """)
        with tempfile.TemporaryDirectory() as temporary:
            for spec in SPECS:
                source = Path(temporary) / spec.package
                source.mkdir()
                for directory in (spec.package, "shared", "fixtures", "docs"):
                    shutil.copytree(
                        ROOT / directory,
                        source / directory,
                        ignore=shutil.ignore_patterns("__pycache__", ".DS_Store"),
                    )
                (source / "scripts").mkdir()
                shutil.copyfile(ROOT / "scripts/demo_bundle.py", source / "scripts/demo_bundle.py")
                for name in ("requirements.txt", "CONTRIBUTING.md"):
                    shutil.copyfile(ROOT / name, source / name)
                output = Path(temporary) / f"dist-{spec.package}"
                result = subprocess.run(
                    [
                        sys.executable,
                        "-I",
                        "-B",
                        "-c",
                        probe,
                        str(source),
                        spec.package,
                        str(output),
                    ],
                    cwd=source,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("Target built without the other architecture", result.stdout)
                self.assertEqual(
                    {p.name for p in output.iterdir()}, {spec.name, f"{spec.name}.zip"}
                )

    @unittest.skipUnless(HAS_STREAMLIT, "Install requirements.txt for Streamlit AppTest")
    def test_extracted_demos_launch_in_isolated_python_processes(self):
        probe = textwrap.dedent("""
            import importlib
            import importlib.util
            import sys
            from pathlib import Path
            from streamlit.testing.v1 import AppTest

            root, package, label = Path(sys.argv[1]).resolve(), sys.argv[2], sys.argv[3]
            sys.path.insert(0, str(root))
            opposite = "event_based" if package == "layered" else "layered"
            assert importlib.util.find_spec(opposite) is None
            factory = importlib.import_module(package + ".bootstrap")
            assert Path(factory.__file__).resolve().is_relative_to(root)
            from shared.commands import RegisterAccount
            from shared.models.common import RequestContext, SecretInput
            from shared.ui.shell import PAGES
            host = factory.build() if package == "layered" else factory.build(start_worker=False)
            try:
                context = RequestContext("bundle-test", None, "bundle-test")
                receipt = host.submit(context, RegisterAccount("test", SecretInput("test-input")), "r1")
                if package == "event_based":
                    assert receipt.status.value == "pending"
                    host.bus.dispatch_one()
                    receipt = host.poll(context, receipt.operation_id)
                assert receipt.status.value == "unimplemented"
            finally:
                host.close()
            app = AppTest.from_file(str(root / package / "streamlit_app.py")).run(timeout=20)
            for page in PAGES:
                app.radio[0].set_value(page).run(timeout=20)
                assert not app.exception, str(app.exception)
                assert all(widget.label != "Architecture" for widget in app.selectbox)
                assert any(c.value == "Running: " + label for c in app.caption)
            assert not any(name.split(".")[0] == opposite for name in sys.modules)
            assert not (root / ".local").exists()
            print(label + ": isolated launch, seven pages and dispatch passed")
        """)
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "build"
            for spec in SPECS:
                archive_path = build_demo(spec, output)
                destination = Path(temporary) / f"extracted-{spec.package}"
                with zipfile.ZipFile(archive_path) as archive:
                    archive.extractall(destination)
                bundle = destination / spec.name
                result = subprocess.run(
                    [
                        sys.executable,
                        "-I",
                        "-B",
                        "-c",
                        probe,
                        str(bundle),
                        spec.package,
                        spec.label,
                    ],
                    cwd=bundle,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("isolated launch, seven pages and dispatch passed", result.stdout)

    def test_existing_target_output_is_preserved(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            existing = output / LAYERED.name
            existing.mkdir()
            marker = existing / "keep.txt"
            marker.write_text("existing work")
            with self.assertRaises(FileExistsError):
                build_demo(LAYERED, output)
            self.assertEqual(marker.read_text(), "existing work")
            self.assertEqual(list(output.iterdir()), [existing])
            archive = build_demo(EVENT_BASED, output)
            before = archive.read_bytes()
            with self.assertRaises(FileExistsError):
                build_demo(EVENT_BASED, output)
            self.assertEqual(archive.read_bytes(), before)
            self.assertEqual(marker.read_text(), "existing work")

    def test_local_configuration_and_data_are_excluded(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source"
            shutil.copytree(
                ROOT,
                source,
                ignore=shutil.ignore_patterns("dist", ".venv", ".local", ".git", "__pycache__"),
            )
            canary = "LOCAL-ONLY-BUILD-CANARY"
            (source / ".env").write_text(canary)
            (source / ".streamlit/secrets.toml").write_text(canary)
            (source / "shared/runtime.sqlite3").write_text(canary)
            output = Path(temporary) / "build"
            for spec in SPECS:
                with zipfile.ZipFile(build_demo(spec, output, source)) as archive:
                    for name in archive.namelist():
                        self.assertNotIn(canary.encode(), archive.read(name))

    @unittest.skipIf(os.name == "nt", "Symlink creation requires additional Windows privileges")
    def test_symlink_inputs_are_rejected_before_writing_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source"
            shutil.copytree(
                ROOT,
                source,
                ignore=shutil.ignore_patterns("dist", ".venv", ".local", ".git", "__pycache__"),
            )
            (source / "docs/link.md").symlink_to(source / "README.md")
            output = Path(temporary) / "build"
            for spec in SPECS:
                with self.assertRaisesRegex(ValueError, "Symlinks"):
                    build_demo(spec, output, source)
                self.assertFalse(output.exists())
