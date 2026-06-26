"""Single entry point for local quality checks."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    # Bu dosya scripts/ altında; proje kökü bir üst dizindedir.
    root = Path(__file__).resolve().parent.parent
    checks = [
        [sys.executable, "-m", "compileall", "-q", "-x", r".*(\.venv|\.git|graphify-out).*", str(root)],
        [sys.executable, "-m", "pytest", str(root / "tests"), "-q"],
        [sys.executable, "-m", "ruff", "check", str(root)],
        [
            sys.executable,
            "-m",
            "mypy",
            "--ignore-missing-imports",
            "--follow-imports=silent",
            str(root / "core" / "managers" / "backup_manager.py"),
            str(root / "core" / "managers" / "secret_manager.py"),
            str(root / "infrastructure" / "database" / "alembic_runner.py"),
            str(root / "domain" / "dtos" / "forms.py"),
        ],
    ]
    for command in checks:
        result = subprocess.run(command, check=False)
        if result.returncode != 0:
            return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
