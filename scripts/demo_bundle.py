"""Packaging utilities used independently by each application's build target."""

import argparse
import hashlib
import json
import shutil
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {"__pycache__", ".venv", ".git", ".local", ".ruff_cache", ".pytest_cache"}


@dataclass(frozen=True)
class BuildSpec:
    package: str
    label: str
    port: int

    @property
    def name(self) -> str:
        return self.package.replace("_", "-") + "-demo"

    @property
    def entrypoint(self) -> str:
        return f"{self.package}/streamlit_app.py"


def source_files(root: Path, spec: BuildSpec) -> list[Path]:
    """Read the target and common inputs, without inspecting another application."""
    if not spec.package.isidentifier():
        raise ValueError("The application package must be a Python identifier")
    files = [root / name for name in ("requirements.txt", "CONTRIBUTING.md")]
    for directory, suffixes in (
        ("shared", {".py", ".sql"}),
        (spec.package, {".py"}),
        ("fixtures", {".json", ".md"}),
        ("docs", {".md", ".mmd"}),
    ):
        base = root / directory
        if not base.is_dir() or base.is_symlink():
            raise ValueError(f"Expected source directory: {directory}")
        for path in sorted(base.rglob("*")):
            relative = path.relative_to(root)
            if any(part in EXCLUDED or part.startswith(".") for part in relative.parts):
                continue
            if path.is_symlink():
                raise ValueError(f"Symlinks are excluded from builds: {relative}")
            if path == base / "build.py" and directory == spec.package:
                continue
            if path.is_file() and path.suffix in suffixes:
                files.append(path)
    for path in files:
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"Expected source file: {path.relative_to(root)}")
    if root / spec.entrypoint not in files:
        raise ValueError(f"Expected application entrypoint: {spec.entrypoint}")
    return sorted(files)


def bundle_readme(spec: BuildSpec) -> str:
    return f"""# {spec.label} demo

Built from the {spec.label} application and shared components in the project repository.

## Run

Use Python 3.12+ from this directory:

```sh
python3 -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run {spec.entrypoint}
```

Open [the local demo](http://127.0.0.1:{spec.port}). Local data belongs in
`.local/{spec.package}`. This application has no architecture selector.

Business features are scaffold TODOs; see [implementation status](docs/STATUS.md).
Develop and test in the full repository, then rebuild with `python -m {spec.package}.build`.
`BUILD.json` records this package's files and checksums.

The initial scaffold and fixture adaptation were AI-assisted. A project license has not yet been selected.
"""


def build_demo(spec: BuildSpec, output: Path, source_root: Path = ROOT) -> Path:
    inputs = source_files(source_root, spec)
    output = output.absolute()
    destination = output / spec.name
    archive = output / f"{spec.name}.zip"
    for path in (destination, archive):
        if path.exists() or path.is_symlink():
            raise FileExistsError(f"Build output already exists: {path}")
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f".build-{spec.package}-", dir=output) as temporary:
        bundle = Path(temporary) / spec.name
        bundle.mkdir()
        for source in inputs:
            target = bundle / source.relative_to(source_root)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        config = bundle / ".streamlit/config.toml"
        config.parent.mkdir()
        config.write_text(
            '[browser]\ngatherUsageStats = false\n[server]\naddress = "127.0.0.1"\n'
            f"headless = true\nport = {spec.port}\n",
            encoding="utf-8",
        )
        (bundle / "README.md").write_text(bundle_readme(spec), encoding="utf-8")
        records = [
            {
                "path": path.relative_to(bundle).as_posix(),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
            for path in sorted(bundle.rglob("*"))
            if path.is_file()
        ]
        manifest = {
            "schema": "cs7319.demo-bundle.v2",
            "architecture": spec.label,
            "package": spec.package,
            "entrypoint": spec.entrypoint,
            "build_target": f"python -m {spec.package}.build",
            "python": "3.12+",
            "port": spec.port,
            "files": records,
        }
        (bundle / "BUILD.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        temporary_archive = Path(temporary) / archive.name
        with zipfile.ZipFile(temporary_archive, "x", compression=zipfile.ZIP_DEFLATED) as handle:
            for path in sorted(bundle.rglob("*")):
                if path.is_file():
                    handle.write(path, f"{spec.name}/{path.relative_to(bundle).as_posix()}")
        bundle.rename(destination)
        temporary_archive.rename(archive)
    return archive


def main(spec: BuildSpec) -> None:
    parser = argparse.ArgumentParser(description=f"Build the {spec.label} demo only.")
    parser.add_argument("--output", type=Path, default=ROOT / "dist", help="Build output parent")
    args = parser.parse_args()
    try:
        archive = build_demo(spec, args.output)
    except (FileExistsError, ValueError) as error:
        parser.exit(
            1, f"Build stopped: {error}\nUse a fresh --output path to rebuild this target.\n"
        )
    print(archive)
