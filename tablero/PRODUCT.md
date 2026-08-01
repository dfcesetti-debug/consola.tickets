# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Dos roles confirmados, sin otros roles activos hoy:

- **Equipo de soporte (mesa de ayuda) de Cesetti**: uso diario para triage y resolución de tickets de Jira, y para cargar trabajo manual en Telemática cuando el cliente/tarea no pasa por Jira.
- **Gerencia**: entra puntualmente a Panel Telemática para medir tiempos del equipo por tarea, responsable y cliente — esta vista es la fuente de verdad de seguimiento de tiempos de Telemática, no un placeholder secundario.

## Product Purpose

Centralizar el soporte de mesa de ayuda para los clientes Quilmes y Cervepar: historial de tickets de Jira en vivo, un módulo manual (Telemática) para trabajo con esos mismos clientes que no pasa por Jira, fichas técnicas por cliente, y paneles de métricas/tiempos de respuesta y resolución. Éxito = que el equipo de soporte tenga todo en un solo lugar sin licencias adicionales, y que gerencia pueda medir tiempos de Telemática con datos reales y precisos.

## Positioning

Unifica en una sola vista por cliente lo que antes vivía separado: los tickets reales de Jira (con SLA) y el trabajo de Quilmes/Cervepar que no pasa por Jira (Telemática, antes llevado aparte, sin esta vista combinada). Ningún competidor que solo mire Jira puede mostrar tickets + trabajo manual + tiempos de Telemática en el mismo lugar, por cliente.

## Operating Context

- Uso diario desde el navegador, publicada en GitHub Pages, sin instalación para el equipo.
- Login obligatorio desde v57 (Firebase Authentication, restringido a cuentas `@cesetti.com.ar`).
- Los tickets de Jira se traen en vivo vía un conector propio en Cloudflare Workers; el token de Jira nunca llega al navegador.
- El resto del estado compartido (clientes, fichas técnicas, tareas de Telemática, perfiles, configuración de conexión) vive en Firebase Firestore y se sincroniza en tiempo real entre todo el equipo.
- Existe un camino de desarrollo local (Flask, `run_local.py`) solo para pruebas antes de publicar — no es parte del uso diario.

## Capabilities and Constraints

- Un solo archivo HTML (`Consola_Soporte_CMQ.html`), sin build step ni framework — cualquier cambio se edita directo en el archivo.
- Dos clientes con Jira real: Quilmes (`SG`) y Cervepar (`CERVEPAR`); el prefijo de cliente en Clientes duplica como project key literal de Jira — cambiarlo rompe el auto-tagging de tickets y "Traer datos".
- Telemática (trabajo sin Jira) usa un prefijo separado (`prefixTele`) para no colisionar con claves reales de Jira.
- El Panel de Jira (KPIs, SLA, tiempos) y el Panel Telemática se calculan por separado a propósito — no se mezclan dos formas distintas de medir tiempo.
- Máquina de desarrollo: Node.js está instalado pero no siempre en el PATH de la sesión de shell activa — restricción del entorno local, no del producto.

## Brand Commitments

Nombre de marca: **"Televidentes"** (rebranding desde v48), producto interno de Cesetti. Identidad visual (paleta clara/oscura, tipografía Plus Jakarta Sans, densidad tipo dashboard) ya establecida en el código — la captura formal del sistema de diseño queda para `/impeccable document`, no para este archivo.

## Evidence on Hand

No hay assets de marketing, testimonios ni casos de estudio — es una herramienta interna, no un producto de cara al público. La evidencia real es el uso diario del equipo y el historial de versiones (`README.md` → Registro de cambios, y `git log`).

## Product Principles

1. Un solo lugar por cliente: tickets de Jira y trabajo de Telemática conviven, pero sus métricas de tiempo nunca se mezclan.
2. Gerencia mide tiempos reales de Telemática desde Panel Telemática — su precisión es prioridad, no un detalle secundario.
3. El token de Jira nunca sale de la nube; el login restringe todo a cuentas `@cesetti.com.ar`.
4. Iterar rápido con versiones chicas y verificables (ver Registro de cambios) antes que releases grandes.
5. WCAG AA (contraste 4.5:1, navegación por teclado, labels asociados, touch targets ≥44px) es un piso permanente para todo trabajo de diseño futuro, no una pasada puntual.

## Accessibility & Inclusion

Estándar confirmado: **WCAG AA como piso permanente** (contraste mínimo 4.5:1, navegación completa por teclado con foco visible, labels de formulario asociados, targets táctiles ≥44×44px). Ya auditado y corregido una vez en v70; todo trabajo de diseño futuro debe mantenerlo, no solo lo ya corregido.
