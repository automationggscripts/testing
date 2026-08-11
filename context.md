# Contexto del proyecto

Este repositorio se usa para generar automatizaciones y scripts a través de
un flujo con IA (Groq). Cada issue nuevo es un pedido de código.

## Tipos de tareas frecuentes
- Scripts de automatización y utilidades generales
- Análisis de datos
- Marketing digital (scraping, reportes, integraciones con APIs, generación
  de contenido, análisis de métricas, etc.)
- Proyectos variados según necesidad puntual

## Estilo de código
- Python como lenguaje principal, salvo que se indique lo contrario en el issue.
- Comentarios DETALLADOS: explicar qué hace cada bloque de código y por qué,
  no solo qué línea hace qué. Alguien sin contexto previo tiene que poder
  entender el script leyendo los comentarios.
- Priorizar código claro y legible por sobre código muy optimizado o compacto.
- Manejar errores de forma explícita (try/except con mensajes claros) en vez
  de dejar que el script falle sin explicación.
- Si el script necesita una librería externa, indicarlo en un comentario al
  inicio del archivo con el comando de instalación (ej: `# pip install requests`).

## Convenciones
- Sin convenciones fijas de nombres o estructura todavía: usar buenas
  prácticas estándar de Python (snake_case, nombres descriptivos) salvo que
  el issue pida algo distinto.

## Notas generales
- Nunca hardcodear claves de API o credenciales en el código: siempre leerlas
  de variables de entorno.
- Si la tarea es ambigua, priorizar la interpretación más simple y directa
  del pedido antes que asumir funcionalidades extra no pedidas.
