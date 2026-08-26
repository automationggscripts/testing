"""Pruebas de los controles que protegen el repositorio de salida de la IA."""

import unittest

from scripts.safety import validate_generated_path


class ValidateGeneratedPathTests(unittest.TestCase):
    def test_accepts_a_safe_python_file(self):
        self.assertEqual(
            validate_generated_path("generated/report.py").as_posix(),
            "generated/report.py",
        )

    def test_rejects_sensitive_and_escaping_paths(self):
        for filepath in (".github/workflows/ci.yml", "../secret.py", "scripts/run_groq.py"):
            with self.subTest(filepath=filepath):
                with self.assertRaises(ValueError):
                    validate_generated_path(filepath)

    def test_rejects_an_executable_file(self):
        with self.assertRaises(ValueError):
            validate_generated_path("generated/install.exe")
