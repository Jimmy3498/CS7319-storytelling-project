"""Check source files for machine paths, credential patterns and broken links."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {".venv", ".git", ".ruff_cache", ".pytest_cache", "__pycache__", ".local", "dist"}
TEXT_SUFFIXES = {".py", ".md", ".json", ".sql", ".toml", ".mmd", ".yml", ".txt"}
problems = []
source_files = []
for path in sorted(ROOT.rglob("*")):
    relative = path.relative_to(ROOT)
    if path.name == ".DS_Store":
        continue
    if not path.is_file() or any(part in EXCLUDED for part in relative.parts):
        continue
    source_files.append(path)
    if path.is_symlink():
        problems.append(f"Symlink needs manual review: {relative}")
        continue
    if path.name == ".env" or path.suffix in {".db", ".sqlite", ".sqlite3", ".pem", ".key"}:
        problems.append(f"Private/runtime artifact in public source view: {relative}")
    if path.suffix not in TEXT_SUFFIXES and path.name not in {".gitignore", ".env.example"}:
        continue
    text = path.read_text()
    # Detect accidental local-machine references without embedding those strings in this scanner.
    if ("/" + "Users/") in text or ("/var/" + "folders/") in text:
        problems.append(f"Machine-specific path: {relative}")
    if re.search(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|sk-[A-Za-z0-9_-]{32,}", text):
        problems.append(f"Credential-like material: {relative}")
    if path.suffix == ".md":
        for link in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
            if re.match(r"[a-z]+://|#", link):
                continue
            target = link.split("#", 1)[0]
            if target and not (path.parent / target).exists():
                problems.append(f"Broken document link: {relative} -> {target}")
if problems:
    raise SystemExit("\n".join(problems))
print(f"Source and link checks passed: {len(source_files)} files.")
