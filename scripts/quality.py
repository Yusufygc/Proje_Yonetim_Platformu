"""Single entry point for local quality checks."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    # Bu dosya scripts/ altında; proje kökü bir üst dizindedir.
    root = Path(__file__).resolve().parent.parent
    checks = [
        [sys.executable, "-m", "compileall", "-q", "-x", r".*(\.venv|\.git).*", str(root)],
        [sys.executable, "-m", "pytest", str(root / "tests"), "-q"],
        [sys.executable, "-m", "ruff", "check", str(root)],
        [
            sys.executable,
            "-m",
            "mypy",
            "--ignore-missing-imports",
            *(str(root / package) for package in (
                "app", "controllers", "core", "domain", "infrastructure", "services", "presentation/viewmodels",
            )),
        ],
    ]
    for command in checks:
        result = subprocess.run(command, check=False)
        if result.returncode != 0:
            return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
