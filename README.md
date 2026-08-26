# Asistente de automatizaciones

Este repositorio convierte pedidos de trabajo en issues de GitHub en pull requests
revisables. La implementación se genera con Groq; ciertos pedidos autorizados de
Google Ads producen un archivo Excel de solo lectura con métricas de campañas.

## Uso

1. Abrí un issue con una descripción clara del resultado esperado.
2. Un mantenedor revisa el pedido y agrega `auto-generate` para código, o
   `google-ads-report` para un reporte de Google Ads.
3. El flujo crea una rama `auto/issue-<número>` y abre un pull request.
4. Revisá el PR, sus pruebas y el contenido generado antes de fusionarlo.

Abrir un issue por sí solo no ejecuta código ni expone secretos. Los reportes de
Google Ads solo se ejecutan con la etiqueta específica; las palabras del issue no
pueden activarlos.

## Configuración

Configurá estos secretos en GitHub: `GROQ_API_KEY`, `GOOGLE_ADS_DEVELOPER_TOKEN`,
`GOOGLE_ADS_CLIENT_ID`, `GOOGLE_ADS_CLIENT_SECRET`, `GOOGLE_ADS_REFRESH_TOKEN`,
`GOOGLE_ADS_CUSTOMER_ID` y, si corresponde, `GOOGLE_ADS_LOGIN_CUSTOMER_ID`.
`GITHUB_TOKEN` lo proporciona GitHub Actions automáticamente.

Para ejecutar comprobaciones locales:

```bash
python -m pip install -r requirements.txt
python -m compileall scripts
```

## Límites de seguridad

La automatización solo acepta archivos de código y documentación en rutas
permitidas. Rechaza cambios a la configuración de GitHub, rutas ocultas y rutas
fuera del repositorio. Los pull requests requieren revisión humana.

## Mantenimiento

Dependabot propone semanalmente actualizaciones para las dependencias de Python y
las acciones de GitHub. Configurá en GitHub una regla de protección para `main`
que exija pull requests y una aprobación antes de fusionar cambios; la gestión de
permisos para aplicar las etiquetas de autorización también se realiza desde la
configuración de colaboradores del repositorio.
