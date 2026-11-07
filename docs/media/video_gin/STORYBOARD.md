# STORYBOARD — Video GIN "Tu registro confiable" (6 shots Gemini)

> **Formato objetivo:** vídeo de landing (~35–45 s) — montaje de **hasta 6 imágenes individuales
> generadas con Gemini** + narración en voz ("habla" al viewer) + subtítulos grandes.
> **Marca:** GIN — Gestión de Inventario Inteligente. Cobertura **GLOBAL** (sin referencia a Neiva).
> **Estilo visual:** fotorrealista, cálido, luz natural; negocios pequeños UNIVERSALES (cualquier
> país/cultura) — nada localista, nada corporativo. UI en pantalla siempre genérica `(mock simple,
> sin copiar el diseño real de la app)`.

---

## Guion de voz (aprobado por el dueño) — mapeo por shot

**Tabla 1**  
*Registro estructurado de especificaciones técnicas ( Sección 1 )*

| Shot | Voz (segundos ~) |
|---|---|
| S1 | "Tu negocio no necesita página web ni sistemas complicados." |
| S2 | "Hoy tus números viven en cuadernos, hojas sueltas… o solo en tu memoria." |
| S3 | "Lo que necesitas es un registro confiable: **qué tienes**…" |
| S4 | "…**qué se movió**…" |
| S5 | "…y **cómo va** tu negocio." |
| S6 | "Gestión de Inventario Inteligente — **GIN** — guarda tus números y te los muestra desde donde estés." |

*Nota.* Especificación técnica sincronizada con la arquitectura vigente del proyecto. Fuente: Elaboración propia (2026).

*(El shot S6 termina con el logotipo/wordmark "GIN" y un único CTA visual: "Empieza a anotar tu negocio hoy".)*

---

## Los 6 shots

### S1 — "Empieza tu día" (hook universal)
**Qué muestra:** persiano/reja de un pequeño negocio abriendo al amanecer; luz cálida; un dueño
genérico (cualquier etnia) empuja la reja hacia arriba. Planos lejanos vistos desde la calle.
**Prompt Gemini (EN):**
> Cinematic photo, early morning outside a small family-run corner shop in a generic neighborhood,
> a 45-year-old shop owner with short dark hair with subtle gray at the temples, warm olive skin,
> wearing a dark forest-green canvas work apron over a neutral beige t-shirt, rolling up the metal
> security shutter from inside, warm golden sunlight, shallow depth of field, documentary style,
> 16:9 aspect ratio, photorealistic, no text

**Nota:** el shutter/reja es el gesto globalmente reconocible de "abrir mi negocio" en mercados
populares de TODO el mundo (Asia, América, África) — por eso abre el video.

### S2 — "El peso del cuaderno" (el dolor)
**Qué muestra:** mismo dueño en el mostrador, cuaderno con números, monedas y muchas hojas sueltas;
expresión de estar calculando de más. Cercano, nivel de tabla.
**Prompt:**
> Documentary photo, a 45-year-old shop owner with short dark hair with subtle gray at the temples,
> warm olive skin, wearing a dark forest-green canvas work apron over a neutral beige t-shirt,
> standing at his counter counting coins with a worn notebook full of handwritten numbers, loose
> receipt papers scattered around, afternoon light, shallow depth of field, 16:9 aspect ratio,
> photorealistic, warm tones, no brand names, no readable text

### S3 — "Qué tienes" (stock en celular)
**Qué muestra:** primer plano del celular EN la mano del dueño sobre el mostrador: en pantalla un
panel simple de productos con nombres y cantidades `(mock neutro, tipografía genérica)`.
**Prompt:**
> Over-the-shoulder photo of a 45-year-old shop owner with short dark hair with subtle gray at the
> temples, warm olive skin, wearing a dark forest-green canvas work apron over a neutral beige
> t-shirt, holding a smartphone showing a clean minimal inventory list interface (simple product
> rows with quantities), blurred shop shelves in the background, warm amber natural light, 16:9
> aspect ratio, photorealistic, neutral UI mockup, no brand logos, no readable text

### S4 — "Qué se movió" (la venta anotada)
**Qué muestra:** intercambio en el mostrador con un cliente sonriente; en segundo plano difuso el
celular con una confirmación simple. Energy: dignidad + rapidez.
**Prompt (FIJADO por el dueño, 2026-10-24 — servirá también de base para el resto de los shots):**
> Documentary medium shot, a 45-year-old shop owner with short dark hair with subtle gray at the
> temples, warm olive skin, wearing a dark forest-green canvas work apron over a neutral beige
> t-shirt, completing a quick sale at the counter to a smiling customer, handing over a plain
> brown paper bag, blurred smartphone on the counter in foreground showing a simple green
> confirmation check screen, warm amber natural light, 16:9 aspect ratio, photorealistic, candid
> moment, no brand names, no readable text.

### S5 — "Cómo va" (reabastecimiento)
**Qué muestra:** cajas de mercancía nueva entrando; dueño mirando el celular con lista de
"recibido hoy" `(mock neutro)`. Contraluz suave.
**Prompt:**
> Photo of cardboard delivery boxes at the entrance of a small neighborhood shop, a 45-year-old
> shop owner with short dark hair with subtle gray at the temples, warm olive skin, wearing a dark
> forest-green canvas work apron over a neutral beige t-shirt, checking a smartphone with a minimal
> restock checklist interface, soft warm amber natural light from the doorway, 16:9 aspect ratio,
> photorealistic, warm documentary feel, no brand names, no readable text

### S6 — "Desde donde estés" (cierre + marca)
**Qué muestra:** noche; el dueño sentado en el sofá de su casa revisando el celular tranquilo;
panel confiable en pantalla `(mock neutro)`; composición deja espacio a la derecha para el wordmark.
**Prompt:**
> Cinematic night photo, a 45-year-old shop owner with short dark hair with subtle gray at the
> temples, warm olive skin, now relaxing at home on a couch (without the apron, wearing a simple
> casual shirt) calmly reviewing a smartphone with a minimal summary dashboard, city lights soft
> in the background, peaceful expression, shallow depth of field, 16:9 aspect ratio,
> photorealistic, uncomplicated, warm yellow accents, no brand names, no readable text

---

## Reglas para la generación (que las 6 fotos se vean como UNA campaña)

1. **Consistencia del protagonista (FICHA DE CASTING FIJADA — prompt S4 del dueño):** en S1–S6 usa
   SIEMPRE la misma persona descrita exactamente igual:
   *"a 45-year-old shop owner with short dark hair with subtle gray at the temples, warm olive
   skin, wearing a dark forest-green canvas work apron over a neutral beige t-shirt"*.
   Esta cadena se copia tal cual dentro de cada prompt de shot (S1–S3 y S5–S6 reemplazan
   "the shop owner" / "a shop owner" por esa descripción completa). El delantal verde + beige es
   la marca visual del personaje — nadie más en las fotos lo lleva.
2. **Paleta:** ámbar/nº cálido + verdes oscuros (coincide con los tokens dark-first del landing).
3. **Aspect:** 16:9 todas (`--ar 16:9` o similar en el modelo). Si se planea versión 9:16 para
   redes, generar las 6 en ambas trama o tala el corte vertical.
4. **NO texto legible engorrazado:** los prompts llevan "no readable text" — el único texto llega
   del montaje (subtítulos + wordmark GIN), siempre nítido.
5. Sin logos de terceros, sin marcas visibles, sin banderas ni escenas idenitificables a una ciudad.

## Montaje (después de tener las 6 fotos)

1. 6 clips de ~5–6 s (pan suave/zoom sutil cada foto para dar vida — efecto Ken Burns son hazy)
2. Transiciones: cross-fade 0.5 s
3. VO: lectura del guion (TTS o grabación del dueño, pendiente elegir)
4. Subtítulos grandes sincronizados por shot (accesibilidad + modo muted)
5. Wordmark GIN + CTA "Empieza a anotar tu negocio hoy" en el cierre (3–4 s extra)
6. Export: MP4 H.264 ~2–4 MB (web, carga bajo demanda como hoy) + versión 9:16 para redes

**Estado:** ⏳ esperar generación de las 6 imágenes (tarea V1 del plan) → montaje V2.

---

## Declaración de Uso de Inteligencia Artificial Generativa y Derechos de Autor (Norma APA 7.ª Edición)

En cumplimiento de las políticas de integridad académica y propiedad intelectual del Servicio Nacional de Aprendizaje (SENA — Programa ADSO) y los estándares de citación de la American Psychological Association (APA, 7.ª ed., 2020), el equipo de desarrollo integrado por Tomás Barrera Ortiz (`@Tomasberserk`), Santiago Javela Ospino (`@SantiagoJavelaOspino`) y Juan Pablo Doria Caviedes (`@Doritotes444`) declara de manera explícita y transparente el uso ético y supervisado de herramientas de Inteligencia Artificial Generativa (IAG):

1. **Alcance del apoyo con IA:** Los modelos de lenguaje fueron utilizados como asistentes de programación en pareja (*pair programming*), generación de código repetitivo (*boilerplate* de esquemas Pydantic y migraciones Alembic), estructuración inicial de plantillas documentales bajo el marco SDD (*Specification-Driven Development*), auditoría estática de seguridad OWASP y pruebas automatizadas. Toda la arquitectura de negocio, reglas de dominio del comercio minorista en Neiva (`BR-01` a `BR-12`), validación funcional y decisiones técnicas fueron diseñadas, verificadas y aprobadas íntegramente por los aprendices autores.
2. **Modelos utilizados y atribución técnica:**
   - *Anthropic Claude Sonnet 4.6 y Claude Haiku 4.5* (Anthropic, 2026): Asistencia en refactorización modular, generación de esquemas, contratos de fachada y coautoría declarada en metadatos de commits (`Co-Authored-By`).
   - *Google Gemini 2.5 Flash / 3.6 Flash* (Google DeepMind, 2026): Procesamiento de lenguaje natural en el módulo `agente_ia`, análisis de contexto de repositorio y revisión de calidad documental.
   - *Groq Cloud Whisper Large v3* (Groq Inc., 2026): Transcripción automática de voz a texto (STT) en tiempo real para el Modo Mostrador del punto de venta.
   - *OpenAI ChatGPT (GPT-4o)* (OpenAI, 2026) y *Google Veo*: Consultoría de optimización de rendimiento frontend (`code-splitting`) y apoyo en guionización visual de la página de aterrizaje.
3. **Derechos de autor y licencias de terceros:** El código fuente original de **Gestión Neiva (TiendApp POS SaaS)** es propiedad intelectual de sus autores humanos (Barrera Ortiz, Javela Ospino y Doria Caviedes, 2026). Las librerías de terceros (FastAPI, SQLAlchemy, React 19, TailwindCSS, Radix UI, Lucide Icons, ZXing) se utilizan bajo sus respectivas licencias de código abierto (MIT / Apache 2.0 / BSD), y los recursos fotográficos de demostración provienen de bancos libres de regalías (Pexels / Picsum Photos) conforme a sus términos de atribución.

**Referencias de modelos IA (Formato APA 7):**
- Anthropic. (2026). *Claude (Versiones Sonnet 4.6 y Haiku 4.5)* [Modelo de lenguaje grande]. https://www.anthropic.com
- Google. (2026). *Gemini (Versión 2.5 Flash)* [Modelo multimodal de inteligencia artificial]. https://deepmind.google/technologies/gemini/
- OpenAI. (2026). *ChatGPT (Versión GPT-4o)* [Modelo de lenguaje grande]. https://chat.openai.com
