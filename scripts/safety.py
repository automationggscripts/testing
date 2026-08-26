"""Controles reutilizables para los archivos producidos por la automatización."""

from pathlib import Path


ALLOWED_EXTENSIONS = {".py", ".md", ".txt", ".json", ".csv", ".yml", ".yaml"}
FORBIDDEN_ROOTS = {".github", ".git", "scripts"}


def validate_generated_path(filepath):
    """Acepta solo archivos seguros, relativos y dentro de las áreas de trabajo."""
    path = Path(filepath)
    if (
        not path.parts
        or path.is_absolute()
        or ".." in path.parts
        or path.parts[0] in FORBIDDEN_ROOTS
    ):
        raise ValueError(f"Ruta no permitida: {filepath}")
    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Tipo de archivo no permitido: {filepath}")
    return path


def validate_python_files(files):
    """Comprueba la sintaxis Python antes de que un cambio llegue al pull request."""
    for filename in files:
        path = Path(filename)
        if path.suffix.lower() == ".py":
            try:
                compile(path.read_text(encoding="utf-8"), str(path), "exec")
            except SyntaxError as error:
                raise ValueError(f"Python inválido en {path}: {error}") from error
