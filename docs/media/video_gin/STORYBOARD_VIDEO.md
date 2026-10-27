# STORYBOARD V2 — Video GIN con CLIPS (Veo/Gemini, 10 s por clip)

> **Estado:** ✅ registrado 2026-10-27 (decisión del dueño).
> **Qué cambia:** las 6 imágenes del V1 quedan DESCARTADAS (el dueño no liked el look:
> tiendas sucias/de barrio maluco). Ahora se generan **clips de video de ~10 s** con el
> modelo de Gemini, y en el montaje se recortan a 7–9 s each.
> **Reglas duras del dueño:**
> 1. Los negocios se ven **normales, bonitos y limpios** — NEVER dirty, aislados, deteriorados.
> 2. Varios negocios y dueños **distintos** entre sí → GIN sirve para cualquier tipo de negocio y persona.
> 3. **Consistencia narrativa:** el video **abre con los mismos 4 personajes** que **cierra** en el clip final.

---

## Casting fijo — los 4 protagonistas (idénticos en TODOS sus clips)

| Personaje | Negocio | Descripción (copiar tal cual en cada prompt) |
|---|---|---|
| **MARÍA** | Tienda moderna de barrio (abarrotes, bonita y limpia) | a welcoming woman in her mid-40s, shoulder-length dark hair with subtle gray streaks, warm olive skin, wearing a clean olive-green apron over a cream top |
| **DON CARLOS** | Ferretería ordenada | a gentle older man with short gray hair and a neat gray mustache, wearing a clean denim work apron over a light blue shirt |
| **ANA** | Cafetería/panadería luminosa | a cheerful young woman in her late 20s with brown curly hair, wearing a clean terracotta apron over a white t-shirt |
| **JUAN** | Papelería fría y bienvenida | a friendly man in his mid-30s wearing glasses, dressed in a tidy light-green polo shirt |

**Regla de continuidad:** cada personaje NUNCA cambia de look ni de negocio entre clips.
En los prompts, sobra con copiar la columna "Descripción".

---

## Los 6 clips (10 s cada uno)

> ⭐ = línea de voz dictada por el dueño (texto sagrado). Las demás son líneas puente
> (pendientes de su OK — se ajustan sin tocar las dictadas).

### V1 — "Cuatro negocios, un mismo día" (apertura: la calle con los 4)
**Duración gen:** 10 s · **VO (0–10 s):** *"Cuatro negocios. Cuatro dueños distintos. Y algo que todos comparten: llevar la cuenta del día."* (puente)
**Prompt Veo (EN):**
> Cinematic establishing shot, early morning on a bright, clean commercial street: four small
> beautiful shops side by side — a modern corner grocery store, a well-organized hardware store,
> a warm bakery café, and a tidy stationery store. In front, the four owners arrive to open:
> a welcoming woman in her mid-40s, shoulder-length dark hair with subtle gray streaks, warm olive
> skin, wearing a clean olive-green apron over a cream top; a gentle older man with short gray hair
> and a neat gray mustache, wearing a clean denim work apron over a light blue shirt; a cheerful
> young woman in her late 20s with brown curly hair, wearing a clean terracotta apron over a white
> t-shirt; and a friendly man in his mid-30s wearing glasses, dressed in a tidy light-green polo
> shirt. They roll up shutters and unlock doors, greeting each other. Slow lateral dolly move,
> warm golden morning light, photorealistic, 16:9, shallow depth of field, clean and modern
> storefronts, no on-screen text, no logos, no dialogue.

### V2 — "El peso del cuaderno" (el dolor — MARÍA en su tienda)
**Duración gen:** 10 s · **VO (0–10 s):** *"Cuadernos, hojas sueltas, la memoria… a final de día quedan las dudas."* (puente)
**Prompt Veo (EN):**
> Documentary shot inside a bright, clean, modern corner grocery store with tidy white shelves
> and warm lighting, a welcoming woman in her mid-40s, shoulder-length dark hair with subtle gray
> streaks, warm olive skin, wearing a clean olive-green apron over a cream top, standing behind
> her counter flipping through a worn notebook full of numbers, glancing at loose receipt papers,
> her expression shifting from focus to slight confusion as a customer picks up items in the
> background. Gentle push-in camera move, photorealistic, 16:9, warm natural light, no on-screen
> text, no logos, no dialogue.

### V3 — "Qué tienes" (el stock en el celular — ANA en la cafetería/panadería)
**Duración gen:** 10 s · **VO (0–10 s):** ⭐ *"Tu negocio no necesita página web ni sistemas complicados. Necesita un registro confiable: qué tienes…"*
**Prompt Veo (EN):**
> Cinematic over-the-shoulder shot inside a warm, clean bakery café with fresh pastries in a
> glass cabinet, a cheerful young woman in her late 20s with brown curly hair, wearing a clean
> terracotta apron over a white t-shirt, calmly reviewing her smartphone showing a clean minimal
> inventory list interface with simple product rows and quantities. She nods, satisfied, and
> looks up at her shelves. Slow arc camera move, soft warm morning light through the window,
> photorealistic, 16:9, neutral UI mockup, no on-screen text, no brand logos, no dialogue.

### V4 — "Qué se movió" (la venta anotada — DON CARLOS en la ferretería)
**Duración gen:** 10 s · **VO (0–10 s):** ⭐ *"…qué se movió:"* (dueño) + *"cada venta, cada entrega, anotada en segundos."* (puente)
**Prompt Veo (EN):**
> Documentary shot inside a bright, well-organized hardware store with neat aisles of tools and
> paint cans, a gentle older man with short gray hair and a neat gray mustache, wearing a clean
> denim work apron over a light blue shirt, completing a quick sale at the counter to a smiling
> customer: he receives a small item, taps his smartphone showing a simple green confirmation
> checkmark screen, hands over the item, and the customer walks away satisfied. Fixed medium shot
> with a slight dolly toward the screen tap, warm amber light, photorealistic, 16:9, candid
> moment, no on-screen text, no brand logos, no dialogue.

### V5 — "Cómo va" (números claros en el celular — JUAN en la papelería)
**Duración gen:** 10 s · **VO (0–10 s):** ⭐ *"…y cómo va"* (dueño) + *"tu negocio, sin la cabeza: ganancias y stock, en un solo lugar."* (puente)
**Prompt Veo (EN):**
> Cinematic shot inside a bright, tidy stationery store with colorful but perfectly organized
> shelves, a friendly man in his mid-30s wearing glasses, dressed in a tidy light-green polo shirt,
> standing at his counter at closing time, looking at his smartphone showing a minimal summary
> dashboard with simple bars and figures, his expression turning from tired to confident,
> a small smile. Soft late-afternoon light, slight slow zoom toward the phone screen reflection,
> photorealistic, 16:9, neutral UI mockup, no on-screen text, no brand logos, no dialogue.

### V6 — "Desde donde estés" (cierre: los 4 de vuelta, la marca)
**Duración gen:** 10 s · **VO (0–10 s):** ⭐ *"Gestión de Inventario Inteligente — GIN — guarda tus números y te los muestra desde donde estés."*
**Prompt Veo (EN):**
> Cinematic night montage: a calm dim living room — the welcoming woman in her mid-40s with
> shoulder-length dark hair with subtle gray streaks relaxing on a couch reviewing her smartphone
> peacefully; a cut to a bright home terrace — the gentle older man with short gray hair and a
> neat gray mustache checking his phone with a calm smile; another brief cut — the young woman in
> her late 20s with brown curly hair and the man in his mid-30s with glasses, each in cozy home
> settings, glancing at their phones with tranquil expressions as city lights glow softly in the
> background. Smooth matched cuts between the four, warm yellow accents, shallow depth of field,
> photorealistic, 16:9, peaceful atmosphere, space on the right side of the frame for a logo,
> no on-screen text, no logos, no dialogue.

---

## Reglas de generación (que los 6 clips se vean como UNA campaña)

1. **Casting fijo:** copiar la descripción del personaje tal cual (tabla de arriba) — los clips
   protagonizados por cada dueño usan SIEMPRE su misma ficha.
2. **Tiendas limpias y bonitas, SIEMPRE:** "bright, clean, well-organized, modern" en cada prompt.
   Nada de deterioro, suciedad, rejas oxidadas ni pobreza visual (decisión del dueño 2026-10-27).
3. **Sin audio del modelo:** los clips se generan con `no dialogue` — la voz y los subtítulos
   se montan encima (VO del guion + caps).
4. **Aspect 16:9** en todos. Si playas la versión 9:16 para redes, regenera o recorta con cabeza libre.
5. **Sin texto legible en pantalla** del modelo; el único texto llega del montaje (subs + wordmark GIN).
6. Global y universal: ninguna bandera, logo o geografía identificable.

## Montaje

1. Recortar cada clip generado de 10 s a **7–9 s** según el ritmo del VO.
2. Transiciones: cross-fade 0.4–0.5 s entre clips.
3. VO sincronizada por clip (guion de arriba; ⭐ = texto dictado por el dueño, intocable).
4. Subtítulos grandes (accesibilidad + playback muted).
5. Cierre V6: wordmark **GIN** + CTA **"Empieza a anotar tu negocio hoy"** (3–4 s adicionales,
   pueden venir del final del mismo clip V6).
6. Export: MP4 H.264 ~2–4 MB web + versión 9:16 redes.

**Duración estimada final:** ~45–55 s (6 clips × 7–9 s = 42–54 s + cierre de marca).

**Estado:** ⏳ V1-video: generación de los 6 clips (tareas del dueño con el modelo Gemini).
Luego V2-video: montaje narrado + poster en landing.
