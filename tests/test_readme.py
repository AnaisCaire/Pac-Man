"""Subject-mandated README structure checks."""

from __future__ import annotations

from pathlib import Path
import unittest


class ReadmeTests(unittest.TestCase):
    """Keep the mandatory contributor line and English sections present."""

    def test_required_first_line_and_sections_are_present(self) -> None:
        """Protect the Chapter IX README contract from documentation drift."""
        readme = Path("README.md").read_text(encoding="utf-8")
        lines = readme.splitlines()

        self.assertEqual(
            lines[0],
            "*This project has been created as part of the 42 curriculum by "
            "masenjo, acaire-d.*",
        )
        for heading in (
            "## Description",
            "## Instructions",
            "## Resources",
            "## Configuration",
            "## Highscore",
            "## Maze Generation",
            "## Implementation",
            "## General Software Architecture",
            "## Project Management",
        ):
            self.assertIn(heading, lines)


if __name__ == "__main__":
    unittest.main()
