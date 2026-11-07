"""Reproducible public-build contract tests."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PackagingTests(unittest.TestCase):
    """The repository exposes one documented native packaging entry point."""

    def test_packaging_files_and_make_target_exist(self) -> None:
        """Keep the root spec, user instructions, script and Make target
        together.
        """
        for relative_path in (
            "pac-man.spec",
            "PACKAGE-INSTRUCTIONS.txt",
            "scripts/package.py",
        ):
            self.assertTrue((ROOT / relative_path).is_file(), relative_path)

        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
        self.assertIn("package:", makefile)

    def test_packaging_script_has_a_clean_help_command(self) -> None:
        """The packaging adapter is inspectable without running a build."""
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "package.py"), "--help"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("PyInstaller", result.stdout)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
