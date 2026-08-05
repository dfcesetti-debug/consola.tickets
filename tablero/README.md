# Consola de Soporte CMQ — Base de Conocimiento

Aplicación web (un solo archivo HTML) para el soporte de la mesa de ayuda de Jira,
con conexión en vivo a los proyectos **Quilmes (SG)** y **Cervepar (CERVEPAR)**.
Reúne el historial de tickets, una matriz de respuestas para Nivel 1, análisis de
tiempos y métricas, todo separado por cliente.

> **Estado de la documentación:** este README cubre hasta **v103**. Para el detalle
> histórico completo ver [`tablero/CHANGELOG.md`](tablero/CHANGELOG.md) y `git log`.

---

## Índice

1. [Archivos del proyecto](#archivos-del-proyecto)
2. [Cómo usarla](#cómo-usarla)
3. [Conexión con Jira (parámetros de la consulta)](#conexión-con-jira-parametros-de-la-consulta)
4. [Sincronización de datos (Firebase)](#sincronización-de-datos-firebase)
5. [Cómo está organizada la información](#cómo-está-organizada-la-información)
6. [Seguridad](#seguridad)
7. [Solución de problemas](#solución-de-problemas)
8. [Referencia rápida (producción)](#referencia-rápida-producción)
9. [Desarrollo y contribución](#desarrollo-y-contribución)
10. [Registro de cambios (resumido)](#registro-de-cambios-resumido)

---

## Archivos del proyecto

| Archivo | Qué es |
|---|---|
| `Consola_Soporte_CMQ.html` | La app. Un solo archivo. Se usa publicada o local — ver "Cómo usarla" abajo. |
| `vendor/chart.umd.min.js` | Chart.js 4.5.1, vendorizado (sin CDN, sin npm en producción) — motor de los gráficos dinámicos de Panel Telemática desde v102. Única dependencia externa de la app además de Firebase. |
| `worker/` | Conector de Jira en la nube (Cloudflare Workers) — el que usa la versión publicada. El token de Jira vive ahí como secreto cifrado, nunca en el HTML. |
| `tablero/main.py` + `tablero/run_local.py` | Mismo conector de Jira, pero para correr en tu PC (Flask) — solo hace falta para desarrollo/pruebas, no para el uso diario del equipo. |
| `tablero/wssp.py` + `tablero/run_wssp_chromium.py` | Scripts auxiliares (scraping de WhatsApp Web) para carga de datos de Telemática. No forman parte del uso diario de la Consola. |
| `tablero/importar_horas_telematica.py` | Script offline (corre en tu PC) que convierte un Excel externo de horas a un `.json` listo para el uploader de Configuración → Conexión de datos. Ver v103 abajo. |
| `tablero/DOCUMENTACION_TECNICA.md` | Arquitectura completa (Firebase, Cloudflare Worker, GitHub Pages) y el contrato de datos del conector. ⚠️ Congelada en v74 — ver nota abajo. |
| `tablero/MANUAL_USUARIOS.md` | Guía práctica para el equipo: cómo entrar, por qué hay que cargar el perfil antes de usar Telemática, y cómo se usa cada sección día a día. |
| `tablero/PRODUCT.md` | Para quién es la Consola, qué resuelve y los principios permanentes (WCAG AA, un solo lugar por cliente, etc.). |
| `tablero/DESIGN.md` + `tablero/.impeccable/design.json` | Sistema de diseño capturado del código (paleta, tipografía, reglas nombradas). Norte creativo "The Situation Room". |
| `tablero/kb_state.json` | Ya no se usa para guardar (desde v30 eso va a Firebase). Resabio de versiones previas de esta carpeta. |
| `tablero/token_local.json` | Token de Jira para desarrollo local (no se sube a git). |
| `tablero/CHANGELOG.md` | Detalle completo versión por versión (v1–v103 y siguientes). El README mantiene solo el resumen de hitos. |
| `README.md` | Este documento. |

> ⚠️ **Nota de desfase:** `DOCUMENTACION_TECNICA.md` describe la plataforma hasta **v74**
> y `MANUAL_USUARIOS.md` hasta **v94**, mientras que este README cubre hasta **v103**.
> La doc técnica deberá actualizarse cuando haya un cambio estructural (arquitectura,
> pestañas, contrato de datos). Consultá siempre el changelog para lo más reciente.

> El token de Jira nunca está en el HTML ni viaja al navegador de quien usa la Consola: en producción vive como secreto de Cloudflare (`worker/`); en desarrollo local, en `tablero/token_local.json` (no se sube a git).

---

## Cómo usarla

**Uso normal (todo el equipo):** entrar a `https://dfcesetti-debug.github.io/consola.tickets/Consola_Soporte_CMQ.html` e iniciar sesión con tu cuenta `@cesetti.com.ar`. No hace falta instalar nada — los tickets se traen del conector en la nube y todo lo demás (clientes, fichas, Telemática, tu perfil) se sincroniza solo entre quienes la usan.

**Primer paso obligatorio al entrar:** la Consola te pide cargar tu perfil (Nombre y Apellido) en **Configuración → Mi perfil** antes de dejarte usar el resto. Tu nombre se usa automáticamente como responsable de las tareas de Telemática y como firma en el historial. Guía paso a paso en [`MANUAL_USUARIOS.md`](tablero/MANUAL_USUARIOS.md).

> **Sesión:** la sesión se cierra sola a los **30 minutos sin actividad** (clic, tecla o toque la reinician). Podés cerrarla vos en cualquier momento desde "Cerrar sesión", abajo del menú lateral.

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
- **Carga automática**: al iniciar sesión la Consola trae los tickets "Abiertos" de ambos clientes Jira en segundo plano (v72), sin esperar a que alguien toque "Traer datos".

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

**Secciones (menú lateral):**
- **Panel**: selector arriba **Panel Jira / Panel Telemática** (v69) para medir los tiempos de cada fuente por separado.
  - **Panel Jira**: KPIs de tiempo con tendencia vs. semana/periodo previo y sparkline (v76/v78), tarjetas seleccionables que llevan al detalle (v79), gráficos y tiempos de respuesta/resolución con SLA real de Jira.
  - **Panel Telemática**: KPIs de tiempo total, promedio semanal, cliente/responsable con más carga (v76/v80); filtros globales de la vista (Categoría/Sub categoría/Cliente/Responsable/rango) arriba de todo (v91) y rango exacto **Desde/Hasta** (v92). Es la vista que usa gerencia para seguimiento.
- **Matriz N1**: por tipo de solicitud — síntoma, datos a pedir, pasos, plantilla de respuesta (copiable), a quién escalar y tickets de referencia.
- **Tickets**: historial de Jira mezclado con las tareas de Telemática (etiquetadas "Telemática", v68), con filtros multi-selección (tipo, estado, responsable, origen) y contadores dinámicos; búsqueda; reasignación de cliente.
- **Clientes**: 4 sub-pestañas — **Lista** (configuración y detección), **Fichas** (ficha técnica histórica por cliente, con árbol de grupos Geotab), **Cartera** por ejecutivo, e **Implementación** (seguimiento de clientes en Demo/desarrollo, v82).
- **Telemática**: registro manual de solicitudes para clientes sin Jira (o coordinaciones que no pasan por Jira), con sus propias métricas.
- **Configuración**: 4 sub-pestañas — **Conexión de datos** (traer tickets, subir archivos, exportar), **Apariencia** (modo claro/oscuro), **Mi perfil**, e **Historial de cambios** (auditoría global, v86).

**Filtros interactivos**: multi-selección en tipo, estado y responsable; actualizan KPIs y gráficos del Panel; los contadores de cada filtro se ajustan según lo ya filtrado (facetas). El selector de cliente (arriba) acota todo por proyecto. Todo filtro activo se puede quitar desde el Panel con su **✕** (v82).

**Tiempos** (con las fechas reales de Jira vía API): 1ª respuesta interna, 1ª respuesta del cliente, y resolución total (creación → resolución). Se cuentan **solo en horario hábil: lunes a viernes de 8:00 a 17:00** — sábado, domingo y las horas fuera de ese rango no suman. Se muestran en horas si son menos de un día hábil (9h), o en días hábiles si son más. Hay un desglose de 1ª respuesta interna por tipo para ver dónde mejorar.

---

## Análisis: filtro por responder → historial

En "Quién respondió los tickets" (Panel) hay un filtro **Todos / Internos / Clientes**, y
al hacer clic en una persona te lleva al historial de los tickets que respondió, con las
respuestas abiertas y resaltadas.

---

## Seguridad

- **Login obligatorio** (Firebase Authentication, desde v57): solo entran cuentas `@cesetti.com.ar` de la lista blanca. Las reglas de seguridad de Firestore exigen esto también del lado del servidor, no solo en la pantalla de login.
- **Sesión con vencimiento por inactividad** (v88): 30 minutos sin actividad cierran la sesión sola.
- **Cierre de sesión que purga datos** (v89): al cerrar sesión (manual o por inactividad) la página **recarga entera**, para que los tickets, clientes, fichas e historial no queden en memoria ni en el HTML.
- **Perfil obligatorio** (v90): cargar Nombre y Apellido es requisito para usar la Consola; se usa como responsable y firma en el historial.
- **Autoservicio de contraseña** (v93): link "Creá tu contraseña por email" en el login permite a cada usuario definir su propia contraseña.
- El token de Jira nunca está en el HTML ni en el navegador: vive como secreto cifrado de Cloudflare (producción) o en `tablero/token_local.json`, que no se sube a git (desarrollo local).

---

## Solución de problemas

| Problema | Qué hacer |
|---|---|
| "Se cerró sola la sesión mientras trabajaba" | Pasaron 30 minutos sin actividad. Volvé a iniciar sesión — no perdés nada, todo está sincronizado. |
| No aparece mi nombre en "Responsable" (aparece mi email) | Todavía no cargaste el perfil: Configuración → Mi perfil → completá Nombre y Apellido. |
| `http://localhost:8787` no trae datos | Solo funciona abriendo la Consola como archivo local; una página `https://` no puede hablar con `localhost` (contenido mixto). |
| Me olvidé la contraseña (o es mi primera vez) | En el login, escribí tu email y tocá **"Creá tu contraseña por email"**. |
| Cargué un cliente/ficha/tarea por error | Editá o eliminá (siempre pide confirmación) desde su propia pantalla. Queda en el Historial de cambios. |

Más detalle y el paso a paso de Telemática en [`MANUAL_USUARIOS.md`](tablero/MANUAL_USUARIOS.md).

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

## Desarrollo y contribución

- **El sistema de diseño vive en `tablero/DESIGN.md`** y `tablero/.impeccable/design.json` (paleta, tipografía, reglas nombradas). Los cambios de diseño se hacen dentro de ese sistema, no rediseñando al margen.
- **Principios permanentes** en `tablero/PRODUCT.md`: un solo lugar por cliente, métricas de Jira y Telemática nunca mezcladas, token de Jira nunca en el navegador, y **WCAG AA como piso** (contraste 4.5:1, navegación por teclado, touch targets ≥44px).
- **Para correr local:** ver "Cómo usarla" (sección de desarrollo). Solo hace falta para probar cambios antes de publicar.
- **Para publicar:** el repo se sube a GitHub Pages (rama `main`). Nunca se sube `token_local.json` ni `kb_state.json` (datos viejos con contacto real) — ver `.gitignore`.
- **Nota de infraestructura (v78):** hay copias gitignoreadas de `PRODUCT.md`/`DESIGN.md`/`.impeccable/` en la raíz del repo (para poder correr el skill `impeccable` en modo `live`). **Pendiente definir una fuente única** (raíz vs `tablero/`) para no desincronizar.

---

## Registro de cambios (resumido)

La Consola tiene **103 versiones** a esta fecha. Para no hacer eterno este documento, acá quedan
solo los **hitos importantes** — los cambios que movieron la aguja en arquitectura, seguridad
o cómo se usa la app día a día. El **detalle completo versión por versión** (v1–v103 y siguientes)
vive en [`tablero/CHANGELOG.md`](tablero/CHANGELOG.md), y también en git: cada commit del repo
corresponde a una versión y trae ese detalle en su propio mensaje —
`git log --oneline` para la lista, `git show <hash>` para el detalle de una en particular.

**Hitos principales (resumen):**

- **v1–v13** — Primera Consola en HTML: matriz N1, parser de tickets, filtros multi-selección, conexión real y estable con Jira (paginación, SLA real, Request Type), módulo Ejecutivos/Fichas.
- **v17–v23** — Consolidación de pestañas (de 7 a 5) y módulo **Telemática**.
- **v30–v35** — Datos compartidos a **Firebase**, publicación en **GitHub Pages**, y token de Jira protegido detrás del conector en **Cloudflare Workers** (nunca en el navegador).
- **v47–v57** — Rediseño (modo oscuro, rebranding), Telemática madura, y **login obligatorio** (solo cuentas `@cesetti.com.ar`).
- **v62–v69** — Tipografía Plus Jakarta Sans, drill-down desde el Panel, separación **Panel Jira / Panel Telemática**, tareas de Telemática mezcladas en Tickets.
- **v70–v76** — Accesibilidad WCAG AA, sistema de diseño `impeccable`, KPI de tiempo con tendencia y sparkline, optimización móvil.
- **v77–v82** — Tablas por cliente, filtros removibles desde el Panel, árbol de grupos Geotab, módulo **Implementación**.
- **v83–v86** — Historial firmado por usuario, menú colapsable, tags clickeables, filtro de categoría, **Historial de cambios global** y confirmación unificada al eliminar.
- **v88–v93** — Sesión de 30 min por inactividad, cierre que purga datos, **perfil obligatorio**, filtros globales de Telemática, rango exacto Desde/Hasta, **autoservicio de contraseña**.
- **v94–v99** — Ficha del cliente: tipo de logística rápido, copiar configuración por sección, GO Focus Plus / Surfsight AI-12 simplificados (checks independientes alineados en tabla de verdad).
- **v100–v101** — Auditoría y endurecimiento de seguridad: se vació el seed de datos de ejemplo que tenía PII real de clientes, se cerró un vector de inyección JQL en el conector de Jira (nube y local), y se versionaron las reglas de Firestore (`firestore.rules`/`firebase.json`) que antes solo existían desplegadas, sin poder auditarlas desde el repo.
- **v102** — Gráficos dinámicos en Panel Telemática: la tarjeta "Tiempos por categoría, sub categoría, responsable y cliente" pasa de barras a mano a **Chart.js** (vendorizado, sin CDN) con selector Barras/Columnas/Tendencia/Dona, mismo filtro cruzado de siempre al hacer clic, y una leyenda de botones reales como control accesible (el `<canvas>` no es operable por teclado).
- **v103** — Export con filtros aplicados (Tickets, Telemática, Panel Telemática) e **import de horas desde un Excel externo**: script offline `tablero/importar_horas_telematica.py` (mapeo de columnas configurable + validación) que convierte el `.xlsx` a un `.json`, y un uploader nuevo en Configuración con **vista previa, detección de duplicados y confirmación** antes de cargar de verdad a Telemática.

---

*Para el detalle completo versión por versión (v1–v103 y siguientes), ver [`tablero/CHANGELOG.md`](tablero/CHANGELOG.md) y `git log`.*
