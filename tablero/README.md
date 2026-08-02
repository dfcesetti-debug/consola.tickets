# Consola de Soporte CMQ — Base de Conocimiento

Aplicación web (un solo archivo HTML) para el soporte de la mesa de ayuda de Jira,
con conexión en vivo a los proyectos **Quilmes (SG)** y **Cervepar (CERVEPAR)**.
Reúne el historial de tickets, una matriz de respuestas para Nivel 1, análisis de
tiempos y métricas, todo separado por cliente.

---

## Archivos del proyecto

| Archivo | Qué es |
|---|---|
| `Consola_Soporte_CMQ.html` | La app. Un solo archivo. Se usa publicada o local — ver "Cómo usarla" abajo. |
| `worker/` | Conector de Jira en la nube (Cloudflare Workers) — el que usa la versión publicada. El token de Jira vive ahí como secreto cifrado, nunca en el HTML. |
| `tablero/main.py` + `tablero/run_local.py` | Mismo conector de Jira, pero para correr en tu PC (Flask) — solo hace falta para desarrollo/pruebas, no para el uso diario del equipo. |
| `tablero/DOCUMENTACION_TECNICA.md` | Arquitectura completa (Firebase, Cloudflare Worker, GitHub Pages) y el contrato de datos del conector. |
| `tablero/kb_state.json` | Ya no se usa para guardar (desde v30 eso va a Firebase). Resabio de versiones previas de esta carpeta. |
| `README.md` | Este documento. |

> El token de Jira nunca está en el HTML ni viaja al navegador de quien usa la Consola: en producción vive como secreto de Cloudflare (`worker/`); en desarrollo local, en `tablero/token_local.json` (no se sube a git).

---

## Cómo usarla

**Uso normal (todo el equipo):** entrar a `https://dfcesetti-debug.github.io/consola.tickets/Consola_Soporte_CMQ.html` e iniciar sesión con tu cuenta `@cesetti.com.ar`. No hace falta instalar nada — los tickets se traen del conector en la nube y todo lo demás (clientes, fichas, Telemática, tu perfil) se sincroniza solo entre quienes la usan.

**Para desarrollar o probar cambios antes de publicarlos**, se puede abrir el archivo local y correr el conector en tu PC:

1. Instalar Python (marcando "Add Python to PATH") y la extensión **Python** de VS Code.
2. Instalar Flask una sola vez: `pip install flask`.
3. Crear `tablero/token_local.json` con tu API token de Jira vigente (no se sube a git — ver `.gitignore`).
4. Correr `python tablero/run_local.py` — tiene que decir `Escuchando en http://localhost:8787`. Dejá esa terminal abierta.
5. Abrir `Consola_Soporte_CMQ.html` como **archivo local** (doble clic) → **Configuración → Conexión de datos → Configuración avanzada** → pegar `http://localhost:8787` → **Traer datos**.

> Importante: `http://localhost:8787` solo funciona abriendo la Consola como archivo local — un navegador bloquea que una página `https://` (como la publicada) le hable a `localhost` (contenido mixto).

---

## Conexión con Jira (parámetros de la consulta)

Tanto el conector en la nube (`worker/`) como el local (`tablero/main.py`) entienden los mismos parámetros `?query=...&proyecto=...` — contrato de datos completo en `tablero/DOCUMENTACION_TECNICA.md` (sección 3.5).

- **Consultas** (`query`): `todos`, `abiertos`, `en_progreso`, `resueltos_semana` / `_mes`, `creados_semana`, `sin_asignar`, `alta_prioridad`.
- **Proyecto** (`proyecto`): vacío = ambos, `CMQ` (clave real `SG`) o `CERVEPAR`.
- **Modo reemplazo**: cada consulta **reemplaza** la base para que los números coincidan exacto con Jira (no se acumula). Botón **Vaciar base** para empezar de cero.
- **Paginado**: el conector en la nube devuelve de a páginas de 100 tickets (`paged=1`) para no cortarse en conexiones lentas — la Consola ya lo maneja sola.

---

## Sincronización de datos (Firebase)

Todo lo que se edita en la Consola (clientes, fichas técnicas, tickets de Telemática, tu perfil, la configuración de conexión) se guarda automáticamente en **Firebase Firestore** — un único documento compartido por todo el equipo (`kb_state/main`). Se lee al abrir la Consola y se escribe con cada guardado; no hace falta ningún servidor propio corriendo para esto.

Los **tickets de Jira en sí no se guardan ahí** — se traen en vivo cada vez que alguien usa "Traer datos" (Configuración → Conexión de datos).

---

## Cómo está organizada la información

**Clientes por prefijo del ticket.** El cliente se detecta por el código:
`SG-` → **Quilmes**, `CERVEPAR-` → **Cervepar**. Se configura en la pestaña **Clientes**
(nombre, prefijo, color, y palabras clave de respaldo). Se puede reasignar un ticket a mano.

**Interno vs. cliente** (para métricas de respuesta):
- Equipo interno (soporte): Diego Ferreira, Lucas Di Luca, Melisa Aranda, Agustina Vallejos, Marcos Marin, Julian Toros, Oscar Fuentealba, Soporte Técnico.
- Contactos de cliente (no cuentan como soporte): paula cerrudo, Nahir Duarte, Gustavo Vergara, y el resto de remitentes externos.

**Secciones:**
- **Panel**: KPIs + todos los gráficos + tiempos. Reacciona a los filtros; cada tarjeta y barra es desplegable y lleva a los tickets detrás de ese dato.
- **Matriz N1**: por tipo de desagío — síntoma, datos a pedir, pasos, plantilla de respuesta (copiable), a quién escalar y tickets de referencia.
- **Tickets**: historial con filtros multi-selección (tipo, estado, responsable) y contadores dinámicos; búsqueda; reasignación de cliente.
- **Clientes**: Lista (configuración y detección) + Fichas (ficha técnica histórica por cliente) + Cartera por ejecutivo.
- **Telemática**: registro manual de solicitudes para clientes sin Jira (o coordinaciones que no pasan por Jira), con sus propias métricas.
- **Configuración**: conexión de datos con Jira (traer tickets, subir archivos, exportar), apariencia (modo claro/oscuro), y tu perfil.

**Filtros interactivos**: multi-selección en tipo, estado y responsable; actualizan KPIs y gráficos del Panel; los contadores de cada filtro se ajustan según lo ya filtrado (facetas). El selector de cliente (arriba) acota todo por proyecto.

**Tiempos** (con las fechas reales de Jira vía API): 1ª respuesta interna, 1ª respuesta del cliente, y resolución total (creación → resolución). Se cuentan **solo en horario hábil: lunes a viernes de 8:00 a 17:00** — sábado, domingo y las horas fuera de ese rango no suman. Se muestran en horas si son menos de un día hábil (9h), o en días hábiles si son más. Hay un desglose de 1ª respuesta interna por tipo para ver dónde mejorar.

---

## Análisis: filtro por responder → historial

En "Quién respondió los tickets" (Panel) hay un filtro **Todos / Internos / Clientes**, y
al hacer clic en una persona te lleva al historial de los tickets que respondió, con las
respuestas abiertas y resaltadas.

---

## Seguridad

- **Login obligatorio** (Firebase Authentication, desde v57): solo entran cuentas `@cesetti.com.ar` de la lista blanca. Las reglas de seguridad de Firestore exigen esto también del lado del servidor, no solo en la pantalla de login.
- El token de Jira nunca está en el HTML ni en el navegador: vive como secreto cifrado de Cloudflare (producción) o en `tablero/token_local.json`, que no se sube a git (desarrollo local).

---

## Referencia rápida (producción)

| Elemento | Valor |
|---|---|
| App publicada | `https://dfcesetti-debug.github.io/consola.tickets/Consola_Soporte_CMQ.html` |
| Repositorio | `https://github.com/dfcesetti-debug/consola.tickets` |
| Conector de Jira (nube) | `https://consola-cmq-jira-proxy.df-cesetti.workers.dev` |
| Proyecto Firebase | `tickets-be0af` (Firestore, doc `kb_state/main`) |

Arquitectura completa y diagrama de flujo: `tablero/DOCUMENTACION_TECNICA.md`.

---

## Registro de cambios (resumen)

La Consola tiene 67 versiones a esta fecha. Para no hacer eterno este documento, acá quedan
solo los **hitos importantes** — los cambios que movieron la aguja en arquitectura, seguridad
o cómo se usa la app día a día. El detalle versión por versión (bugs puntuales, qué se probó,
decisiones chicas de diseño) sigue existiendo íntegro en el **historial de git**: cada commit
del repo corresponde a una versión y trae ese detalle en su propio mensaje —
`git log --oneline` para la lista, `git show <hash>` para el detalle de una en particular.

- **v1–v7** — Primera Consola en HTML: matriz de respuestas N1, parser de tickets en el navegador, filtros multi-selección, conexión por API en modo reemplazo, sincronización automática de ajustes.
- **v8–v11** — Conexión real y estable con Jira: paginación sin límite, SLA real de Jira Service Management, Request Type real (no el tipo genérico de Jira), reintentos ante fallas de red.
- **v12–v13** — Módulo **Ejecutivos**: ficha técnica histórica por cliente (equipos, referentes, configuración), con historial de cambios y exportación a PDF.
- **v17** — Consolidación de pestañas: de 7 a 5 (se fusionan "Clientes Jira" en Clientes, y "Cargar Jira" en Tickets).
- **v23** — Módulo **Telemática**: registro manual de solicitudes para clientes sin Jira (y coordinaciones que no pasan por Jira), con sus propias métricas de tiempo.
- **v30** — Los datos compartidos (clientes, fichas, tickets de Telemática) pasan a guardarse en **Firebase (Firestore)** en vez del navegador de cada uno — necesario para que todo el equipo vea lo mismo.
- **v31** — La Consola queda **publicada en GitHub Pages** (`dfcesetti-debug.github.io/consola.tickets`), accesible sin instalar nada.
- **v33** — El token de Jira se protege detrás de un conector propio en **Cloudflare Workers** — cualquiera con el link ve tickets reales, sin que el token viaje al navegador de nadie.
- **v34–v35** — "Traer datos" más simple (tildes en vez de URL cruda) y más confiable (el conector pagina de a 100 tickets, para no cortarse en conexiones lentas).
- **v38** — Fichas técnicas: configuración detallada de cámaras Surfsight AI-12 y GO Focus Plus, alerta por alerta.
- **v47–v48** — Rediseño de interfaz: íconos de navegación, tarjetas de cliente, **modo oscuro completo**, y rebranding a **"Televidentes"**.
- **v49–v56** — Telemática madura: carga por fecha + horas, métricas de % por tipo/cliente, carga de varias tareas en una sola tanda.
- **v57** — **Login obligatorio** (Firebase Authentication, solo cuentas `@cesetti.com.ar`) — antes cualquiera con el link podía leer y escribir los datos.
- **v62** — Tipografía consistente (Plus Jakarta Sans) en toda la consola, embebida sin depender de Google Fonts.
- **v63–v67** — Consola más dinámica: clic en una barra/celda del Panel o Telemática lleva directo a los tickets detrás de ese dato (drill-down), tarjetas y KPIs desplegables, botón Atrás del navegador funcional entre pestañas, y módulo nuevo **Configuración** (conexión de datos, apariencia, mi perfil).
- **v68** — Las tareas cargadas en Telemática ahora también aparecen mezcladas en la pestaña **Tickets**, del cliente que corresponda, con los mismos filtros y buscador — etiquetadas "Telemática" para distinguirlas de las de Jira (sin SLA ni comentarios, muestran cantidad de horas). El Panel (KPIs, gráficos, SLA) sigue calculándose solo con tickets de Jira, para no mezclar dos formas distintas de medir tiempo. Su clave usa el prefijo configurado en Clientes (ej. "CN-1", "CN-2"). En clientes de origen Jira (Quilmes/Cervepar) el prefijo real nunca se reusa (colisionaría con la clave de un ticket real) — en su lugar se agregó un **segundo campo "Prefijo Telemática"** en la tarjeta de cada cliente Jira, específico para esto; si no se carga, la clave cae al nombre del cliente tal cual (ej. "Quilmes-1"). Se sumó también un filtro **Origen (Jira / Telemática)** en Tickets, con los mismos contadores cruzados que ya tienen Tipo/Estado/Responsable.
- **v69** — El **Panel se separó en "Panel Jira" y "Panel Telemática"** (selector arriba, mismo cliente/alcance de siempre) para medir los tiempos de cada fuente por separado — Panel Telemática es el que usa gerencia para seguimiento. Panel Jira quedó igual que antes (se le sacó la tarjeta "vía Referente Telemática", que se mudó al nuevo). Panel Telemática tiene 3 tarjetas nuevas, todas desplegables: **"Tiempos por tarea, responsable y cliente"** (un selector cambia la dimensión y otro entre total/promedio semanal), **"Tiempo total por cliente en la semana"** (no se acota por el cliente elegido arriba, es para comparar entre todos; incluye columna **%** con la participación de cada cliente sobre el total), y **"Tiempos por categoría, sub categoría, responsable y cliente"** — gráfico de barras interactivo: 4 filtros cruzados (Categoría/Sub categoría/Cliente/Responsable, mismo patrón que Tickets/Telemática), un rango de fecha (Día/Semana/Mes/Trimestre/Semestre/Año) y un selector de qué dimensión graficar; clic en una barra la suma o saca como filtro (se combina con los de arriba); cada barra muestra además el **% que representa sobre el total mostrado**, al lado de la duración. Empezó como árbol desplegable pero el usuario pidió verlo en formato gráfico con filtros después de probarlo — quedó así en la misma ronda.
- **v70** — Ronda de accesibilidad y UX (auditoría con el skill UI/UX Pro Max): las barras de drill-down, filas de comparación de clientes, filas de ticket en los desplegables de KPI y los ítems de los filtros multi-select ahora son operables por teclado (Tab + Enter/Espacio, con foco visible); el color de texto secundario `--mut2` en modo claro se oscureció para cumplir contraste mínimo 4.5:1 (afectaba títulos de tarjeta, encabezados de tabla y etiquetas); los campos de Email/Contraseña (login) y Nombre/Apellido/Correo/Teléfono (Mi perfil) pasaron a usar `<label for>` real en vez de texto suelto; los campos de nombre/prefijo de cliente sumaron `aria-label`; el botón "Quitar cliente" pasó de 24×24px a 44×44px (mínimo táctil) con `aria-label`; el botón **"Traer datos"** (conexión con Jira) ahora se deshabilita y muestra "Consultando…" mientras la consulta está en curso, para que no se pueda disparar dos veces la misma carga por impaciencia; el campo Teléfono de Mi perfil usa `type="tel"` (teclado numérico en celular); y los campos de texto (`.finput`) suben a 16px en pantallas chicas para evitar el zoom automático de iOS al tocarlos.
- **v71** — Se instaló el skill de diseño **`impeccable`** y se corrió por primera vez sobre este proyecto: `tablero/PRODUCT.md` (para quién es la Consola, qué resuelve, principios permanentes como WCAG AA) y `tablero/DESIGN.md` + `tablero/.impeccable/design.json` (sistema de diseño capturado del código actual — norte creativo "The Situation Room", paleta, tipografía, reglas nombradas). De ahí salió un cambio real: el **rail de navegación** quedaba siempre oscuro sin importar el tema — ahora sigue el modo claro/oscuro como el resto de la app (nuevos tokens `--railbg1/2`, `--railtx`, `--railon`, `--railhover`, `--railborder`, `--railfootmut`; se sacó `--rail`, que estaba declarada pero nunca usada).
- **v72** — Al **iniciar sesión, la Consola trae automáticamente los tickets "Abiertos"** de ambos clientes Jira, sin esperar a que alguien toque "Traer datos" (corre en segundo plano, no bloquea el login). El campo de URL del conector nunca queda vacío: si no hay ninguna configurada todavía, cae sola al conector de producción (`https://consola-cmq-jira-proxy.df-cesetti.workers.dev`). La carga automática y la manual comparten el mismo estado de carga del botón "Traer datos" — si una está en curso, la otra no puede pisarla.
- **v73** — Pasada de diseño con el skill `impeccable` (comandos `colorize · typeset · animate · layout · delight · overdrive`), refinando dentro del sistema ya documentado en `DESIGN.md`, no rediseñando: **colorize** — nuevo token `--danger`/`--dangerbg` (claro y oscuro) reemplaza 3 rojos sueltos sin tokenizar (error de login, log, "Eliminar" en Telemática) y el hover de "Quitar cliente" (antes usaba el ámbar de "Demo", un rol distinto). **typeset** — títulos de vista (`h1`/`h2.vt`) con `font-weight` explícito en vez de heredar el bold del navegador. **animate** — confirmación con una pequeña animación al guardar el perfil. **layout** — se unificó el espaciado entre las dos grillas de KPI (`.kpis`/`.tkpi`), que usaban 14px y 12px para la misma relación visual. **delight** — los 4 estados vacíos que usaban glifos Unicode como ícono (☎ ◈ ▤ ★) pasan a SVG propio con el mismo trazo del rail; el de Telemática además señala la próxima acción ("Abrí 'Carga de tarea' arriba..."). **overdrive** — la carga de tickets (manual o automática al iniciar sesión) ahora **muestra el contador de "Tickets" subiendo en vivo** a medida que llegan las páginas del conector, en vez de saltar de golpe al número final al terminar toda la consulta — telemetría en vivo, no un efecto cosmético (respeta `prefers-reduced-motion`). El resultado final es idéntico a antes; es una capa perceptual sobre la misma lógica de datos.
