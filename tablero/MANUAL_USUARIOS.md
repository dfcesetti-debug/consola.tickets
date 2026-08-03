# Consola de Soporte CMQ — Manual de uso para el equipo

**Para quién es este documento:** cualquier persona del equipo de soporte/telemática que va a usar la Consola día a día. Si buscás arquitectura técnica (Firebase, Cloudflare Worker, contrato de datos), eso está en `DOCUMENTACION_TECNICA.md`. Este documento es la guía práctica: cómo entrar, qué cargar primero y por qué, y cómo se usa cada sección.

Fecha: 03/08/2026. Cubre hasta v90.

---

## 1. Cómo entrar

Entrá a `https://dfcesetti-debug.github.io/consola.tickets/Consola_Soporte_CMQ.html` con tu cuenta `@cesetti.com.ar`. No hace falta instalar nada.

- Solo entran cuentas del dominio `@cesetti.com.ar` — cualquier otro correo queda rechazado.
- Si te equivocás la contraseña, la Consola te avisa "Email o contraseña incorrectos." Si no tenés cuenta o la olvidaste, pedísela a quien administra el acceso — la Consola no tiene un flujo de "recuperar contraseña" propio.
- **La sesión se cierra sola a los 30 minutos sin actividad** (sin clics, sin escribir, sin tocar la pantalla) y te vuelve a pedir que inicies sesión, con el aviso "Tu sesión se cerró por 30 minutos de inactividad." Mientras estés usando la Consola normalmente, el conteo se reinicia solo y no pasa nada. Podés cerrar sesión vos mismo en cualquier momento desde el link **Cerrar sesión**, abajo del todo en el menú lateral.

---

## 2. Primer paso obligatorio: cargar tu perfil

**Es un paso realmente obligatorio, no una sugerencia**: si tu perfil no tiene Nombre y Apellido cargados, la Consola te lleva directo a **Configuración → Mi perfil** apenas entrás, y te deja ahí — cualquier intento de ir a otra sección (menú lateral, un link que hace drill-down, atrás/adelante del navegador) te devuelve a esta pantalla, con un aviso explicando por qué. Completá **Nombre** y **Apellido** (el teléfono es opcional) y guardá con **Guardar perfil** — apenas lo hacés, la Consola te lleva sola al Panel y podés navegar libre.

**¿Por qué es obligatorio?** Tu nombre de perfil es lo que la Consola usa automáticamente, sin que tengas que escribirlo cada vez, en tres lugares:

1. **Telemática → Carga de tarea**: el campo **Responsable** de cada tarea nueva se completa solo con tu nombre — así el tiempo cargado queda asignado a quien realmente lo trabajó, sin que dependa de que cada uno se acuerde de escribirlo.
2. **Ficha del cliente → "Guardado por"**: firma automáticamente cada cambio que guardás en la ficha técnica de un cliente.
3. **Configuración → Historial de cambios**: el registro global de auditoría (quién cambió qué y cuándo) también usa tu nombre de perfil.

Antes de que este paso fuera obligatorio, quien no cargaba su perfil aparecía en esos tres lugares con su email en crudo (ej. `nuevo@cesetti.com.ar`) en vez de su nombre.

Tu perfil se guarda por email y te sigue si entrás desde otra PC.

---

## 3. Recorrido por las secciones (menú lateral)

El menú lateral se puede **colapsar** a solo íconos con la flecha en su borde (útil en pantallas chicas) — el estado elegido se recuerda entre sesiones. Cada pestaña también se puede abrir en una **pestaña nueva del navegador** con clic derecho, Ctrl/Cmd+clic o clic central.

- **Panel** — resumen operativo. Selector arriba **Jira / Telemática** para medir cada fuente por separado. Las tarjetas de KPI son clickeables: seleccionan la tarjeta y bajan directo al detalle correspondiente.
- **Matriz N1** — guía rápida de respuesta para Nivel 1: por tipo de ticket frecuente, qué preguntar y qué plantilla usar.
- **Tickets** — historial completo de Jira, mezclado con las tareas cargadas en Telemática (etiquetadas aparte). Buscable y filtrable por tipo, estado, responsable, origen.
- **Clientes** — cuatro sub-pestañas: **Lista** (alta/edición de clientes), **Fichas** (ficha técnica completa por cliente, con el árbol de grupos estilo Geotab y su propio historial), **Cartera por ejecutivo**, e **Implementación** (seguimiento de clientes en Demo o en desarrollo, contabilizando tareas/reuniones/reportes hasta el cierre).
- **Telemática** — carga manual de trabajo con clientes sin Jira. Ver paso a paso en la sección 4.
- **Configuración** — cuatro sub-pestañas: **Conexión de datos** (traer tickets de Jira), **Apariencia** (modo claro/oscuro), **Mi perfil** (sección 2), y **Historial de cambios** (sección 5).

---

## 4. Cómo cargar una tarea en Telemática, paso a paso

1. Andá a la pestaña **Telemática**.
2. Abrí **Carga de tarea** (desplegable, arriba).
3. Cargá la **Fecha** (es compartida por todas las tareas que cargues juntas en esta tanda).
4. Por cada tarea, completá una fila: **Cliente**, **Categoría** → **Sub tipo**, **Cantidad de horas**, **Estado**, y **Detalle** (opcional). El campo **Responsable** ya viene con tu nombre (ver sección 2) — solo tocalo si la tarea corresponde a otro compañero.
5. Con **+ Agregar tarea** podés sumar más filas a la misma tanda (misma fecha).
6. Guardá. La lista de abajo ("Tickets cargados") muestra todo lo cargado, de más reciente a más antiguo, con filtros por **Categoría**, **Tipo**, **Cliente** y **Responsable**.
7. Para editar o eliminar una tarea ya cargada, usá **Ver / Editar** o **Eliminar** en su tarjeta — eliminar siempre pide confirmación.

---

## 5. Buenas prácticas

- **Eliminar siempre pide confirmación** ("¿Estás seguro de que querés eliminar…?") en toda la Consola: fichas, tareas de Telemática, clientes, grupos del árbol Geotab, filas de Configuración técnica y Referentes. Si tocaste eliminar por error, cancelá en ese cartel.
- **Configuración → Historial de cambios** junta en una sola lista, filtrable por Tipo/Cliente/Usuario, todo lo que se modificó en la Consola (fichas, tareas de Telemática, altas/bajas de clientes, vaciar/restablecer la base) — es el lugar para revisar qué cambió alguien y cuándo, sin tener que entrar cliente por cliente.
- En el Panel, cualquier filtro activo (cliente, tipo, estado, responsable, búsqueda) se puede sacar con el **✕** que aparece junto al título, sin tener que ir a buscarlo a su selector original.
- La barra de cliente arriba de todo se puede esconder con la flecha, para ganar espacio en pantallas chicas.

---

## 6. Preguntas frecuentes

**No aparece mi nombre en "Responsable", aparece mi email.**
Todavía no cargaste tu perfil — andá a Configuración → Mi perfil y completá Nombre y Apellido (sección 2).

**Se cerró sola la sesión mientras trabajaba.**
Pasaron 30 minutos sin ninguna acción en la Consola (clic, tecla, toque). Volvé a iniciar sesión con tu cuenta — no perdiste nada, todo lo guardado ya está sincronizado.

**Cargué un cliente/ficha/tarea por error.**
Podés editarlo o eliminarlo (con confirmación) desde su propia pantalla. Los cambios y eliminaciones quedan visibles en Configuración → Historial de cambios.

**Entré desde otra PC y no veo mis datos de perfil.**
Tu perfil se guarda por email en la nube — si no aparece, volvé a cargarlo una vez desde esa PC; después va a estar disponible en cualquier equipo con el mismo login.
