"""
Version con conector a Google Ads.
Flujo:
1. Lee el issue (titulo + cuerpo) para saber que se pide.
2. Si el pedido menciona Google Ads / metricas / campanias, consulta
   la API de Google Ads y arma un Excel con los datos.
3. Si no, sigue el flujo anterior (Groq genera codigo).
4. Sube todo a una rama nueva y abre un Pull Request.
"""

import os
import re
import subprocess
from openai import OpenAI
from github import Github
from google.ads.googleads.client import GoogleAdsClient
import openpyxl
from openpyxl.styles import Font

# ---- Configuracion general ----
GROQ_API_KEY = os.environ["GROQ_API_KEY"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
ISSUE_TITLE = os.environ["ISSUE_TITLE"]
ISSUE_BODY = os.environ.get("ISSUE_BODY", "") or ""
ISSUE_NUMBER = os.environ["ISSUE_NUMBER"]
REPO_NAME = os.environ["REPO"]

# ---- Configuracion Google Ads (solo se usa si el pedido lo requiere) ----
GOOGLE_ADS_DEVELOPER_TOKEN = os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN")
GOOGLE_ADS_CLIENT_ID = os.environ.get("GOOGLE_ADS_CLIENT_ID")
GOOGLE_ADS_CLIENT_SECRET = os.environ.get("GOOGLE_ADS_CLIENT_SECRET")
GOOGLE_ADS_REFRESH_TOKEN = os.environ.get("GOOGLE_ADS_REFRESH_TOKEN")
GOOGLE_ADS_CUSTOMER_ID = os.environ.get("GOOGLE_ADS_CUSTOMER_ID", "6717076350")  # sin guiones
GOOGLE_ADS_LOGIN_CUSTOMER_ID = os.environ.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID")  # customer ID del MCC, sin guiones

client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")

# ---- Detectar si el pedido es sobre Google Ads ----
texto_pedido = f"{ISSUE_TITLE} {ISSUE_BODY}".lower()
palabras_clave_ads = ["google ads", "campaña", "campanias", "campañas", "ads", "publicidad", "anuncios"]
es_pedido_de_ads = any(palabra in texto_pedido for palabra in palabras_clave_ads)

changed_files = []
branch_name = f"auto/issue-{ISSUE_NUMBER}"

subprocess.run(["git", "config", "user.name", "auto-bot"])
subprocess.run(["git", "config", "user.email", "auto-bot@users.noreply.github.com"])
subprocess.run(["git", "checkout", "-b", branch_name])


def consultar_google_ads():
    """
    Se conecta a Google Ads (solo lectura) y trae metricas basicas de
    campanias de los ultimos 30 dias: nombre, impresiones, clics, costo.
    """
    config = {
        "developer_token": GOOGLE_ADS_DEVELOPER_TOKEN,
        "client_id": GOOGLE_ADS_CLIENT_ID,
        "client_secret": GOOGLE_ADS_CLIENT_SECRET,
        "refresh_token": GOOGLE_ADS_REFRESH_TOKEN,
        "login_customer_id": GOOGLE_ADS_LOGIN_CUSTOMER_ID,
        "use_proto_plus": True,
    }
    ads_client = GoogleAdsClient.load_from_dict(config)
    ga_service = ads_client.get_service("GoogleAdsService")

    query = """
        SELECT
            campaign.name,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros
        FROM campaign
        WHERE segments.date DURING LAST_30_DAYS
    """

    response = ga_service.search(customer_id=GOOGLE_ADS_CUSTOMER_ID, query=query)

    filas = []
    for row in response:
        filas.append({
            "campania": row.campaign.name,
            "impresiones": row.metrics.impressions,
            "clics": row.metrics.clicks,
            "costo": row.metrics.cost_micros / 1_000_000,  # micros a moneda real
        })
    return filas


def generar_excel(filas, nombre_archivo):
    """Arma un Excel simple y legible con las metricas de las campanias."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Metricas Google Ads"

    encabezados = ["Campaña", "Impresiones", "Clics", "Costo"]
    ws.append(encabezados)
    for cell in ws[1]:
        cell.font = Font(bold=True)

    for fila in filas:
        ws.append([fila["campania"], fila["impresiones"], fila["clics"], fila["costo"]])

    for columna in ws.columns:
        ancho = max(len(str(c.value)) for c in columna if c.value is not None) + 2
        ws.column_dimensions[columna[0].column_letter].width = ancho

    os.makedirs("reportes", exist_ok=True)
    ruta = f"reportes/{nombre_archivo}"
    wb.save(ruta)
    return ruta


if es_pedido_de_ads:
    print("Pedido identificado como consulta de Google Ads. Consultando API...")
    filas = consultar_google_ads()
    ruta_excel = generar_excel(filas, f"reporte_ads_issue_{ISSUE_NUMBER}.xlsx")
    changed_files.append(ruta_excel)
    titulo_pr = f"Reporte de Google Ads: {ISSUE_TITLE}"
    cuerpo_pr = (
        f"Reporte generado automaticamente a partir del issue #{ISSUE_NUMBER}.\n\n"
        f"Se consultaron {len(filas)} campañas de los ultimos 30 dias.\n"
        f"Archivo: {ruta_excel}"
    )
else:
    # ---- Flujo anterior: generar codigo con Groq ----
    context = ""
    if os.path.exists("context.md"):
        with open("context.md", "r", encoding="utf-8") as f:
            context = f.read()

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
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
    )
    output = completion.choices[0].message.content

    pattern = r"### FILE: (.+?)\n```(?:\w*\n)?(.*?)```"
    matches = re.findall(pattern, output, re.DOTALL)

    if not matches:
        print("Groq no devolvio archivos en el formato esperado. Salida cruda:")
        print(output)
        exit(1)

    for filepath, content in matches:
        filepath = filepath.strip()
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\n")
        changed_files.append(filepath)

    titulo_pr = f"Groq: {ISSUE_TITLE}"
    cuerpo_pr = (
        f"Generado automaticamente a partir del issue #{ISSUE_NUMBER}.\n\nArchivos modificados:\n"
        + "\n".join(f"- {f}" for f in changed_files)
    )

# ---- Commit, push y Pull Request (comun a los dos casos) ----
subprocess.run(["git", "add"] + changed_files)
subprocess.run(["git", "commit", "-m", titulo_pr])
subprocess.run(["git", "push", "origin", branch_name])

gh = Github(GITHUB_TOKEN)
repo = gh.get_repo(REPO_NAME)
pr = repo.create_pull(title=titulo_pr, body=cuerpo_pr, head=branch_name, base="main")

print(f"Pull request creado: {pr.html_url}")
