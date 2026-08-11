"""
Version con Groq (API compatible con OpenAI) en vez de Gemini.
Misma logica: lee el issue, lee context.md, genera codigo, abre un PR.
"""

import os
import re
import subprocess
from openai import OpenAI
from github import Github

# ---- Configuracion ----
GROQ_API_KEY = os.environ["GROQ_API_KEY"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
ISSUE_TITLE = os.environ["ISSUE_TITLE"]
ISSUE_BODY = os.environ.get("ISSUE_BODY", "") or ""
ISSUE_NUMBER = os.environ["ISSUE_NUMBER"]
REPO_NAME = os.environ["REPO"]

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)

# ---- 1. Leer el contexto fijo del proyecto ----
context = ""
if os.path.exists("context.md"):
    with open("context.md", "r", encoding="utf-8") as f:
        context = f.read()

# ---- 2. Armar el prompt completo ----
prompt = f"""Sos un asistente de programacion que trabaja dentro de un repositorio de GitHub.

Reglas y contexto del proyecto:
{context}

Tarea pedida por el usuario:
Titulo: {ISSUE_TITLE}
Detalle: {ISSUE_BODY}

Respondé ÚNICAMENTE con bloques de código, uno por archivo, usando este formato exacto
para cada archivo que quieras crear o modificar:

### FILE: ruta/al/archivo.py
```
contenido completo del archivo
```

No agregues explicaciones fuera de ese formato.
"""

# ---- 3. Llamar a Groq ----
completion = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": prompt}],
)
output = completion.choices[0].message.content

# ---- 4. Parsear la respuesta y escribir los archivos ----
pattern = r"### FILE: (.+?)\n```(?:\w*\n)?(.*?)```"
matches = re.findall(pattern, output, re.DOTALL)

if not matches:
    print("Groq no devolvio archivos en el formato esperado. Salida cruda:")
    print(output)
    exit(1)

branch_name = f"groq/issue-{ISSUE_NUMBER}"
subprocess.run(["git", "config", "user.name", "groq-bot"])
subprocess.run(["git", "config", "user.email", "groq-bot@users.noreply.github.com"])
subprocess.run(["git", "checkout", "-b", branch_name])

changed_files = []
for filepath, content in matches:
    filepath = filepath.strip()
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    changed_files.append(filepath)

subprocess.run(["git", "add"] + changed_files)
subprocess.run(["git", "commit", "-m", f"Groq: {ISSUE_TITLE}"])
subprocess.run(["git", "push", "origin", branch_name])

# ---- 5. Abrir el Pull Request ----
gh = Github(GITHUB_TOKEN)
repo = gh.get_repo(REPO_NAME)
pr = repo.create_pull(
    title=f"Groq: {ISSUE_TITLE}",
    body=f"Generado automaticamente a partir del issue #{ISSUE_NUMBER}.\n\nArchivos modificados:\n"
    + "\n".join(f"- {f}" for f in changed_files),
    head=branch_name,
    base="main",
)

print(f"Pull request creado: {pr.html_url}")
