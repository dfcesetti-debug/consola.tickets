---
name: Consola de Soporte CMQ (Televidentes)
description: Consola interna de soporte tipo sala de control — tickets de Jira y trabajo manual de Telemática en una sola vista densa por cliente.
colors:
  signal-teal: "#0aa2c0"
  signal-teal-deep: "#087f96"
  confirm-green: "#16b364"
  client-amber: "#b4690e"
  danger-red: "#c0392b"
  ink: "#0b1220"
  quiet-slate: "#5c6b82"
  soft-slate: "#667490"
  fog-bg: "#eef2f7"
  panel-white: "#ffffff"
  hairline-edge: "#dbe3ee"
  whisper-edge: "#eef2f8"
typography:
  display:
    fontFamily: "ui-monospace, 'SF Mono', 'Cascadia Code', 'JetBrains Mono', Consolas, monospace"
    fontSize: "26px"
    fontWeight: 800
    lineHeight: 1.1
    letterSpacing: "-0.5px"
  headline:
    fontFamily: "'Plus Jakarta Sans', -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    fontSize: "22px"
    fontWeight: 700
    lineHeight: 1.2
  title:
    fontFamily: "'Plus Jakarta Sans', -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    fontSize: "17px"
    fontWeight: 750
    lineHeight: 1.3
  body:
    fontFamily: "'Plus Jakarta Sans', -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "'Plus Jakarta Sans', -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    fontSize: "10.5px"
    fontWeight: 800
    letterSpacing: "0.06em"
rounded:
  xs: "6px"
  sm: "8px"
  md: "9px"
  button: "11px"
  card: "14px"
  modal: "16px"
  pill: "20px"
spacing:
  xs: "6px"
  sm: "10px"
  md: "14px"
  lg: "20px"
  xl: "26px"
components:
  button-primary:
    backgroundColor: "{colors.signal-teal}"
    textColor: "#ffffff"
    rounded: "{rounded.button}"
    padding: "10px 14px"
  button-primary-hover:
    backgroundColor: "{colors.signal-teal-deep}"
  button-secondary:
    backgroundColor: "{colors.panel-white}"
    textColor: "{colors.ink}"
    rounded: "{rounded.button}"
    padding: "10px 14px"
  button-secondary-hover:
    textColor: "{colors.signal-teal-deep}"
  card:
    backgroundColor: "{colors.panel-white}"
    rounded: "{rounded.card}"
    padding: "18px 20px"
  chip:
    backgroundColor: "{colors.panel-white}"
    textColor: "{colors.quiet-slate}"
    rounded: "{rounded.pill}"
    padding: "6px 13px"
  chip-selected:
    backgroundColor: "{colors.signal-teal}"
    textColor: "#ffffff"
---

# Design System: Consola de Soporte CMQ (Televidentes)

## Overview

**Creative North Star: "The Situation Room"**

La Consola se piensa como una sala de control: un rail de navegación que ancla al costado, tarjetas de KPI que funcionan como lecturas de instrumento (números grandes en monoespaciada, peso 800, como si fueran displays digitales), y un único color de señal — el teal — que marca lo activo, lo interactivo, lo que pide atención. Todo lo demás se mantiene neutro y silencioso para que esos puntos de señal se noten.

El tono es denso y confiable, sin ruido: prioriza que se puedan leer muchos datos por pantalla antes que dejar espacio en blanco decorativo. Anti-referente confirmado: dashboards SaaS genéricos de tarjetas gigantes con mucho espacio vacío — la Consola va en la dirección opuesta, con densidad tipo panel de control, no tipo landing page de producto.

**Key Characteristics:**
- Densidad alta: mucha información por pantalla, tipografía compacta (14px base), sin relleno decorativo.
- Los números son los protagonistas: cualquier valor cuantitativo (KPIs, contadores, horas, %) usa tipografía monoespaciada en negrita, nunca la tipografía de texto corrido.
- Un solo acento de color (teal/cian) para todo lo interactivo/activo; el resto de la paleta es neutra.
- Superficies planas en reposo; la sombra aparece solo como respuesta a hover/focus, nunca como decoración.
- Modo claro y oscuro con tokens semánticos propios por tema (no es una inversión automática de colores).

## Colors

Paleta mayormente neutra (grises azulados) con un único acento de señal (teal) y dos colores semánticos (verde de confirmación, ámbar de estado). Cada token tiene una variante de modo oscuro con valores propios, no invertidos.

### Primary
- **Signal Teal** (`#0aa2c0` — dark: `#22c3e2`): acento único del sistema. Botones primarios, estados activos/seleccionados, foco, barras de progreso, links de dato clickeable. Se usa con moderación — es la única fuente de color intencional en una pantalla mayormente neutra.
- **Signal Teal Deep** (`#087f96` — dark: `#4fd2ea`): variante hover/texto-sobre-fondo-claro del acento; también el color por defecto para números de mono destacados (ticket keys, fechas, valores) cuando no están en un fondo sólido.

### Secondary (semántico)
- **Confirm Green** (`#16b364` — dark: `#34d399`): estado "Resuelto", checkmarks de selección, indicadores de éxito.
- **Client Amber** (`#b4690e` — dark: `#e0954a`): estado "Demo" en fichas de cliente, SLA incumplido (warning), avisos del log de Actividad.
- **Danger Red** (`#c0392b` — dark: `#e57373`, con `--dangerbg` de fondo `#fdece9`/`#2a1512`): acciones destructivas (error de login, "Quitar cliente" al hover, eliminar tarea de Telemática, errores del log). Antes vivía como hex suelto sin tokenizar y sin variante de modo oscuro (v73) — no reusar `--cli` (ámbar) para esto, son roles distintos: ámbar es advertencia/estado, rojo es acción destructiva o error real.

### Neutral
- **Ink** (`#0b1220` — dark: `#e9eff8`): texto principal.
- **Quiet Slate** (`#5c6b82` — dark: `#9fb0c8`): texto secundario (subtítulos, texto de ayuda).
- **Soft Slate** (`#667490` — dark: `#7f93b0`): texto terciario — títulos de tarjeta, encabezados de tabla, labels de campo. Corregido en v70 desde `#8593a8` porque no cumplía contraste AA (4.5:1) en modo claro; no volver a aclarar este token.
- **Fog Background** (`#eef2f7` — dark: `#0b1220`): fondo general de la app.
- **Panel White** (`#ffffff` — dark: `#141f33`): fondo de tarjetas, inputs, superficies elevadas.
- **Hairline Edge** (`#dbe3ee` — dark: `#28374f`): bordes de tarjetas, inputs, divisores fuertes.
- **Whisper Edge** (`#eef2f8` — dark: `#1c2a40`): divisores sutiles, fondos de fila alterna.

### Named Rules
**The One Signal Rule.** El teal es la única fuente de color intencional para indicar interactividad o estado activo. Un nuevo componente no debería introducir un segundo acento "porque sí" — si hace falta distinguir algo más, se resuelve con peso tipográfico, tamaño o los dos colores semánticos ya existentes (verde/ámbar), no con un color nuevo.

**The Readout Rule.** Todo valor numérico que representa un dato real (conteos, horas, %, fechas, claves de ticket) se tipografía en `var(--mono)`, nunca en la tipografía de texto corrido — así el ojo distingue al instante "esto es un dato" de "esto es una etiqueta o texto".

## Typography

**Display/Readout Font:** `ui-monospace, 'SF Mono', 'Cascadia Code', 'JetBrains Mono', Consolas, monospace` — reservada a datos, no a títulos.
**Body/Headline Font:** `'Plus Jakarta Sans'` (con system-ui de respaldo).

**Character:** Plus Jakarta Sans aporta calidez geométrica sin perder neutralidad — funciona a 14px sin perder legibilidad. La monoespaciada nunca se usa como cuerpo de texto, solo como "voz de instrumento" para datos.

### Hierarchy
- **Display/Readout** (800, 26px mono, letter-spacing -0.5px): valores de KPI grandes en Panel.
- **Headline** (700, 20–22px sans): títulos de vista (`h2.vt`) y de documentos exportados (`h1`).
- **Title** (750, 17px sans): títulos de sección dentro de un módulo (ej. `.mtitle` en Matriz N1).
- **Body** (400, 14px sans, line-height 1.5): texto corrido y base de la app.
- **Label** (800, 10.5px sans, uppercase, letter-spacing 0.06em): eyebrows de tarjeta (`.lab`), encabezados de tabla, labels de campo de formulario.

### Named Rules
**The Instrument Weight Rule.** Los pesos saltan directo de 400 (cuerpo) a 700–800 (títulos, labels, números) — no hay un escalón intermedio de 500/600 para jerarquía. La distinción se hace con tamaño y color, no con pesos intermedios.

## Layout

Rail de navegación fijo de 210px + contenido principal de ancho máximo 1180px, centrado, con padding 20px 26px. El rail es `position` fijo en altura completa (100vh) con scroll propio; el contenido principal tiene su propio scroll independiente y un `topbar` sticky con blur de fondo.

Densidad tipo dashboard: la escala de espaciado va de 6px (separaciones mínimas dentro de un componente) a 26px (padding del contenedor principal), sin saltos grandes — nada de los 64–96px típicos de una landing page. Las tarjetas usan 18–20px de padding interno; los KPI, un poco menos (15–17px).

Responsive: dos breakpoints por content, no por dispositivo. `@media(max-width:640px)` ajusta la grilla de la tabla de comparación de clientes y sube los inputs a 16px para evitar el zoom automático de iOS (v70). `@media(max-width:720px)` (v74) convierte el rail en una barra inferior fija (scroll horizontal, labels en una sola línea, respeta `env(safe-area-inset-bottom)` para el home indicator de iPhone) y apila la barra de búsqueda + botones (`.toprow`) en vez de compartir una sola fila — antes de v74 esa fila se aplastaba en pantallas angostas y la búsqueda quedaba casi inusable. Se activa por ancho de viewport, así que un teléfono en horizontal (~667px+) puede caer en cualquiera de los dos layouts según el ancho real, no según "es celular" — a los 812px+ (iPhone apaisado típico) ya entra el layout de escritorio completo y funciona bien tal cual.

## Elevation & Depth

Sistema plano por defecto: las tarjetas, KPIs y botones no tienen sombra en reposo (`.card` solo tiene `0 1px 2px` casi imperceptible). La sombra aparece únicamente como respuesta a una interacción — hover en un KPI o un botón, o la superficie flotante de un modal/login — nunca como decoración fija.

### Shadow Vocabulary
- **Resting** (`box-shadow: 0 1px 2px rgba(16,32,60,.04)`): borde casi invisible en tarjetas en reposo — apenas separa del fondo.
- **Hover lift** (`box-shadow: 0 10px 26px rgba(16,32,60,.1)`): KPIs al pasar el mouse, junto con `translateY(-2px)`.
- **Button hover** (`box-shadow: 0 3px 10px rgba(16,32,60,.08)`): botones al pasar el mouse, junto con `translateY(-1px)`.
- **Floating surface** (`box-shadow: 0 20px 60px rgba(0,0,0,.18)` a `0 24px 70px rgba(0,0,0,.35)`): login box y modales — la única familia de sombra que sí es prominente, porque marca una superficie que flota sobre todo lo demás.

### Named Rules
**The Flat-At-Rest Rule.** Ninguna superficie de la app tiene sombra decorativa en reposo. La sombra siempre comunica una de dos cosas: "esto reacciona a tu cursor/foco" o "esto flota por encima del resto de la interfaz" (modal/login). Confirmado como regla permanente en la sesión de `document` (2026-08-01).

## Shapes

Escala de radios consistente, del elemento más chico al más grande: 6–9px (chips pequeños, pills de conteo), 11px (botones), 14px (`--r`, tarjetas y KPIs), 16px (login box, modales), y 20px — completamente redondeado — para chips, tags, pills y badges (cualquier elemento tipo "cápsula"). No hay esquinas cuadradas (0px) en ningún componente interactivo.

## Components

Carácter general: preciso y sin fricción — bordes definidos, esquinas moderadas, transiciones rápidas (150–250ms, `cubic-bezier(.16,1,.3,1)`) que dan sensación de respuesta inmediata sin ser juguetonas.

### Buttons
- **Shape:** 11px de radio, borde de 1.5px.
- **Primary:** fondo Signal Teal, texto blanco, hover pasa a Signal Teal Deep.
- **Secondary (default):** fondo panel, borde neutro, texto ink; hover cambia borde y texto a teal y levanta 1px con sombra sutil.
- **Hover / Focus:** `translateY(-1px)` + sombra sutil en hover; `scale(.97)` en active. Los inputs usan un anillo de foco vía `box-shadow` (no `outline`) en teal translúcido.

### Chips / Pills / Tags
- **Style:** siempre 20px de radio (cápsula completa), fondo panel o `--accdim` (teal muy diluido) según si está seleccionado.
- **State:** chip seleccionado pasa a fondo teal sólido + texto blanco; los `.mselItem` (ítems de filtro multi-select) muestran un check verde (`--sig`) cuando están activos, sin cambiar el fondo.

### Cards / Containers
- **Corner Style:** 14px (`--r`).
- **Background:** panel blanco (modo claro) / azul muy oscuro (modo oscuro).
- **Shadow Strategy:** ver Elevation & Depth — plano en reposo.
- **Border:** 1px sólido, color `hairline-edge`.
- **Internal Padding:** 18–20px.

### Inputs / Fields
- **Style:** borde 1px neutro, fondo panel, radio ~9px, texto 13px.
- **Focus:** el borde pasa a Signal Teal + anillo de `box-shadow` de 3–4px en teal diluido (nunca `outline` liso).
- **Error / Disabled:** disabled baja opacidad a 0.35–0.5 + cursor `not-allowed`; no hay un estado de error de campo formalizado todavía (los errores de formulario hoy se resuelven vía `confirm()`/log, no inline por campo).

### Navigation (rail)
- **Style:** sigue el tema claro/oscuro como el resto de la app (corregido en v71 — antes quedaba fijo oscuro sin importar el tema, era una inconsistencia, no una decisión de marca). Tokens propios (`--railbg1/2`, `--railtx`, `--railon`, `--railhover`, `--railborder`, `--railfootmut`) para que el contraste se mantenga en ambos modos. Ítem activo: gradiente horizontal teal translúcido + sombra interior de 3px en el borde izquierdo (`inset 3px 0 0 var(--accent)`). Cada ítem combina ícono SVG + label + badge de conteo opcional (nunca solo ícono) — el badge reusa el estilo pill teal (`--accdim`/`--accent2`) en vez de un gris propio.

### Empty states
- **Style:** ícono SVG centrado (mismo trazo que los íconos del rail: `stroke-width:1.5`, esquinas redondeadas, sin relleno) a 34px, opacidad .5, seguido de un título en negrita y una línea secundaria en `--mut`. Reemplazaron glifos Unicode sueltos (v73) — no volver a usar un carácter Unicode como ícono acá.
- **Copy:** en estados de "primer uso" (nada cargado todavía), la segunda línea nombra la acción concreta a seguir (ej. "Abrí 'Carga de tarea' arriba"), no solo "no hay datos". En estados de filtro-sin-resultados, alcanza con nombrar la ausencia — no hace falta una acción sugerida.

## Do's and Don'ts

### Do:
- **Do** usar `var(--mono)` para cualquier valor numérico real (conteos, horas, %, fechas, claves de ticket) — nunca la tipografía de texto corrido.
- **Do** mantener las superficies planas en reposo; la sombra solo aparece en hover/focus o en superficies flotantes (modal/login).
- **Do** usar 20px de radio para cualquier elemento tipo cápsula (chip/tag/pill/badge) y 14px para tarjetas — no introducir un tercer valor de radio para el mismo rol.
- **Do** mantener WCAG AA como piso en cualquier componente nuevo (contraste 4.5:1, foco visible vía `box-shadow` no `outline: none` sin reemplazo, targets táctiles ≥44px) — confirmado en PRODUCT.md como principio permanente, no solo la corrección de v70.
- **Do** transiciones de 150–250ms con `cubic-bezier(.16,1,.3,1)` para cualquier cambio de estado nuevo, para no romper el ritmo de movimiento ya establecido.
- **Do** usar `--danger`/`--dangerbg` (nunca un hex suelto) para errores y acciones destructivas — ver Danger Red en Colors.
- **Do** animar un número que cambia por una acción real (ej. el contador de tickets mientras "Traer datos" trae páginas) en vez de saltar de golpe — ver el contador en vivo de v73 (`animateTicketCount`, ~400ms, respeta `prefers-reduced-motion`). No animar números que cambian por navegación/filtros de rutina.

### Don't:
- **Don't** introducir un segundo color de acento — el teal es la única señal de interactividad/estado activo (ver The One Signal Rule).
- **Don't** agregar sombra decorativa a una tarjeta o superficie en reposo — rompe The Flat-At-Rest Rule.
- **Don't** usar tarjetas gigantes con mucho espacio en blanco tipo landing SaaS — la densidad alta es intencional (ver Overview, anti-referente confirmado).
- **Don't** usar un carácter Unicode como ícono (glifo, emoji) en contenido nuevo — dibujar un SVG propio con el mismo trazo que ya usan el rail y los estados vacíos.
