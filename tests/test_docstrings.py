"""Documentation compliance checks required by the subject."""

from __future__ import annotations

import ast
from pathlib import Path
import unittest


class DocstringTests(unittest.TestCase):
    """Every production class and function explains its purpose."""

    def test_all_classes_and_functions_have_docstrings(self) -> None:
        """Reject undocumented definitions anywhere under the source tree."""
        missing: list[str] = []
        for path in Path("src").rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(
                    node,
                    (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef),
                ) and ast.get_docstring(node) is None:
                    missing.append(f"{path}:{node.lineno} {node.name}")

        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
