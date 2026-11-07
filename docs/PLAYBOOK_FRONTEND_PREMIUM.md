# Playbook Front-end Premium — Forenses de ORIVIA + Receta replicable

> Análisis forense de https://orivia.tobaru.xyz (página ganadora de la hackathon)
> y cómo replicarla en Gestión Neiva. Documento vivo — Graham/AI, 2026-10-18.

---

## 1. Qué stack usa ORIVIA (evidencia real, no suposición)

Inspeccioné el HTML servido, el CSS completo (94 KB) y los chunks JS (125 KB).
Esto es lo que hay por debajo:

**Tabla 1**  
*Registro estructurado de especificaciones técnicas ( Sección 1 )*

| Componente | Tecnología | Evidencia |
|-----------|------------|-----------|
| Framework | **Next.js App Router, export estático** | `/_next/static/chunks/*`, RSC payload inline |
| Estilos | **Tailwind CSS v4.3.3** | Header `/*! tailwindcss v4.3.3 */` en el CSS |
| Animación | **Framer Motion** (hoy: paquete `motion`) | `useScroll`, `useTransform`, `useSpring`, `useMotionValueEvent`, `useReducedMotion` minificados en el chunk de `LandingPage` |
| Scroll-telling | **Secuencia de 151 frames `.webp` en canvas 2D** | Config: `pattern:"/media/proceso/viaje/v{n}.webp", frames:151, pad:3` + `getContext("2d")` + `drawImage` |
| Reveals | IntersectionObserver + clases CSS (propio, ~222 B de "safety net") | Script `/reveal.js` solo ponía `orivia-js-ready`; el CSS esconde/muestra el contenido |
| Tipografía | **Montserrat** con pesos 300–700 | `--default-font-family` |
| Temas | Claro/oscuro vía `data-tema` + `prefers-color-scheme` | Bloques `[data-tema=oscuro]` |
| Texturas/Ambiente | **Keyframes CSS custom** | `ken-burns 22s`, `mist 38s` (vapor), `mote 14s` (partículas), `sway`, `destello`, `dash` (SVG draw), `logo-glow` |
| Gradient mesh | Radiales multipunto custom | `<radialGradient>` con paletas `profundo/medio/claro` |
| **CERO** | GSAP, Lenis, Three.js, WebGL, Locomotive, iframes | No aparecen en globals (`window`) ni en `fetch` de scripts |

*Nota.* Especificación técnica sincronizada con la arquitectura vigente del proyecto. Fuente: Elaboración propia (2026).

**Conclusión 1:** la calidad NO viene de librerías caras o exóticas. Viene de
Tailwind + Framer Motion + **sistema de diseño propio** + **coreografía de scroll**
+ **layers de textura**. Todo es gratis y conocible.

**Conclusión 2:** el hero "se ve como video" porque ES una secuencia:
151 fotogramas webp (≈6 s de video a 25 fps) pre-cargados y dibujados en un
`<canvas>` con la posición del scroll. Eso es exactamente la técnica estilo
Apple/Website de Apple (AirPods). El "consejo de Veo/Gemini" que te dieron está
correcto en el pipeline: **generar el clip con Veo → extraer frames con ffmpeg →
scrub por scroll**. (El nombre de la secuencia es literal "viaje": es el viaje
del cacao de la finca al producto.)

---

## 2. Por qué se distingue de una "página AI básica" (checklist de matices)

1. **Tokens de marca, no defaults.** Paleta con nombre narrativo:
   `bosque #1b3d2e`, `crema #f5efe6`, `tierra #6b3f2a`, `ámbar #c98a2b`,
   `cereza #a3262a`, `arena #d9c9b1`, carbón, card, ink, ink-soft, line.
   Las páginas AI-default usan slate/purple + white. Esta tiene **identidad eidética**.
2. **Textura ambiental siempre activa.** Tres capas de grano: motas flotantes
   (posiciones pseudo-random deterministas, 24 partículas con delay/duración),
   niebla/mist en 38 s, ken-burns de 22 s sobre las fotos. La página "respira".
3. **Coreografía de scroll con física.** El progreso no es lineal: pasa por
   `useSpring({stiffness:38–110, damping:5–26})` → movimiento con inercia, jamás robótico.
4. **Estructura narrativa numérica, no de landing genérica.**
   `origen → proceso (scroll-telling 620svh sticky) → trazabilidad → analítica → historia → productos → contacto`.
   Cada sección tiene layout distinto (nada de filas de cards iguales).
5. **Micro-copy auténtico.** "Finca La Esperanza", "Algeciras, Huila",
   lote `CAC001`, evento con **hash FNV-1a decorativo** (`evento #a1f8…`), contadores
   `PASO 03/05` en fuente mono. La especificidad se lee como "empresa real".
6. **Detalle/estados reales.** Badges de estado con color semántico
   (`LIBERADO`→`bg-bosque/85`, `BLOQUEADO`→`bg-cereza/90`), `backdrop-blur`,
   audio-jump a cada paso con `scrollTo({behavior:"smooth"})`.
7. **Accesibilidad y resiliencia.** `useReducedMotion()` en todos los bindings
   (fallback estático si `prefers-reduced-motion`), `aria-label`s, seguridad de
   Escape, y el `reveal.js` garantía de contenido visible sin JS.
8. **Parallax simétrico sutil.** `useTransform(scrollYProgress, [0,1], [40,-40])`
   en imágenes — desplazamientos chicos (±40px), nunca escandalosos.

---

## 3. Receta replicable (para nuestro stack React + Vite + Tailwind v4)

Nuestro `frontend/` ya es React 19 + Vite + Tailwind v4 + Radix. Faltan:

```bash
npm install motion      # framer-motion v11+ (mismo paquete de ORIVIA)
```

### 3.1 Tokens de marca primero (no escribir una sola línea de UI sin esto)

En `src/index.css` (Tailwind v4 usa `@theme`):

```css
@theme {
  /* Paleta con NARRATIVA, tomada del negocio real */
  --color-bosque:  #1b3d2e;   /* verde institucional */
  --color-crema:   #f5efe6;   /* fondo claro cálido  */
  --color-tierra:  #6b3f2a;   /* acento cálido       */
  --color-ambar:   #c98a2b;
  --color-cereza:  #a3262a;   /* error / estado      */
  --color-carbon:  #1a1a1a;   /* dark surface        */
  --color-card:    --alpha(var(--color-crema) / 92%);
  --color-ink:     #1d2b24;
  --color-ink-soft:#5b6760;
  --color-line:    #e3d8c7;

  --font-sans: "Montserrat", ui-sans-serif, system-ui, sans-serif;

  --animate-ken-burns: ken-burns 22s ease-in-out infinite alternate;
  --animate-mist:      mist 38s linear infinite;
  --animate-mote:      mote 14s linear infinite;
  --animate-sway:      sway 5s ease-in-out infinite;
}
```

Punto clave: **Los nombres comparten idioma con el negocio.** En Neiva:
`café / panela / cambuche / riel de auditoría` probablemente; ORIVIA usa cacao.

### 3.2 El componente estrella: FrameSequencePlayer (scroll-telling)

Un solo componente reutilizable, portado del chunk de ORIVIA:

```jsx
// src/components/landing/FrameSequence.jsx
import { useRef, useEffect } from "react";
import { motion, useScroll, useSpring, useTransform,
         useMotionValueEvent, useReducedMotion } from "motion/react";

export default function FrameSequence({
  steps,           // [{ id, label, title, description }]
  pattern = "/media/viaje/v{n}.webp",
  frames = 151, pad = 3,
}) {
  const sectionRef = useRef(null);
  const canvasRef  = useRef(null);
  const reduce     = useReducedMotion();

  const { scrollYProgress } = useScroll({ target: sectionRef });
  const smooth = useSpring(scrollYProgress, {
    stiffness: 90, damping: 20, mass: 0.5,
  });

  // Pre-carga con buffer de 6 frames
  const cache = useRef(Array(frames));
  const draw = (idx) => {
    const c = canvasRef.current, ctx = c?.getContext("2d");
    if (!c || !ctx) return;
    const img = cache.current[idx];
    if (img?.complete && img?.naturalWidth) {
      c.width = img.naturalWidth; c.height = img.naturalHeight;
      ctx.drawImage(img, 0, 0);       // + cover-fit manual según aspect
    }
  };
  useEffect(() => {
    let loadPtr = 0;
    const tick = () => {
      const target = Math.round(smooth.get() * (frames - 1));
      for (let i = 0; i < 6; i++) {
        const n = Math.max(0, Math.min(frames - 1, loadPtr));
        if (!cache.current[n]) {
          const img = new Image();
          img.src = pattern.replace("{n}", String(n).padStart(pad, "0"));
          cache.current[n] = img;
        }
        loadPtr++;
        if (loadPtr >= frames) break;
      }
      draw(target);
    };
    const unsub = smooth.on("change", tick);
    return () => unsub?.();
  }, []);

  // Step actual según rangos [0,.36],[.36,.67]...
  useMotionValueEvent(smooth, "change", (v) => {
    const i = stepRanges.findIndex(([a, b]) => v >= a && v < b);
    setActive(i);
  });

  // 620svh sticky: la sección logra 6 pantallas de scroll,
  // el canvas queda pegado (sticky top-0 h-screen) — a lo Apple
  return (
    <section ref={sectionRef} className="relative h-[620svh]" id="proceso">
      <div className="sticky top-0 h-screen overflow-hidden">
        <canvas ref={canvasRef} className="absolute inset-0 size-full object-cover" />
        {/* Cards de narrativa por step, crossfade con opacity */}
      </div>
    </section>
  );
}
```

### 3.3 generar los frames con Veo + ffmpeg (el pipeline que te recomendaron)

1. Prompt en **Veo 3** (Google AI Studio / Flow): un clip de ~6 s con cámara
   en movimiento consistente y un solo plano-secuencia (ej.: "drone descendiendo
   sobre finca cafetera del Huila al amanecer, luz cálida, 4k").
2. Extraer frames y comprimir:

```bash
ffmpeg -i viaje_veo.mp4 -vf "fps=25,scale=1600:-1" -qscale:v 70 media/viaje/v%03d.webp
# metamucho: 151 frames ≈ 3–6 MB total si van a 1600px webp
```

3. Fallback: primer frame como `poster` sólo si el JS no carga (el canvas queda
   oculto) + `loading="lazy"` no aplica en Image(), controlar preload.

### 3.4 Parallax/Reveals estándar (los 3 patrones que usan recursivamente)

```jsx
// Parallax simétrico de una imagen
const { scrollYProgress } = useScroll({ target: ref,
  offset: ["start end", "end start"] });
const y     = useTransform(scrollYProgress, [0, 1], [40, -40]);
const scale = useTransform(scrollYProgress, [0, 1], [1,   1.15]);
const o     = useTransform(scrollYProgress, [0, .45], [0, 1]);

// Ken-Burns CSS en hero (más barato que JS)
<img className="animate-ken-burns" ... />  // keyframes 22s alternate

// Header que cambia a ~1.35 viewport-height
const solid = window.scrollY > 1.35 * window.innerHeight;
```

### 3.5 Textura ambiental (grano sin librerías)

- **Motas:** 24–30 divs con posiciones `(left, top) = (37*i % 100, 35+53*i % 60)`
  deterministas + `animate-mote` con delay escalonado.
- **Mist/Vapor:** 3 divs radiales blur con drift de 38 s.
- **Gradient mesh:** `<radialGradient>` SVG con 3 focos + máscara de opacidad
  ligada a scroll.

### 3.6 Capa "reveal" con cero dependencias

Sistema de dos clases + un script de 10 líneas (como ORIVIA):

```js
// src/lib/reveal.js — progressive enhancement
document.documentElement.classList.add("js-ready");
new IntersectionObserver((entries) => {
  for (const e of entries) e.isIntersecting && e.target.classList.add("in-view");
}, { threshold: 0.12 })
  .observe(document.querySelectorAll("[data-reveal]"));
```

Regla de oro: **todo contenido server/estático llega visible por CSS si JS
lw falla.** (En ORIVIA el `<h1>` tenía `opacity:0` inline que se activaba al
cargar — riesgoso, pero su `reveal.js` es la red de seguridad.)

---

## 4. Plan concreto para el landing de Gestión Neiva

1. `npm i motion` en `frontend/`.
2. Crear `docs/landing/DESIGN.md` con la paleta narrativa de Neiva
   (probablemente verde institucional + crema + un acento de producto).
3. Sustituir hero por `FrameSequence` con clip Veo de "operación logística/
   bodega/inventario del Huila" → 120–151 frames.
4. Agregar los 3 patrones ambientales: ken-burns en imágenes + motas + mist.
5. Secciones numéricas de narrativa real (éste es el ADN): nombres propios,
   lotes, hashes de auditoría, badges de estado — la app YA tiene estos datos
   (inventario, auditoría, CRM): **usarlos de verdad en el landing.**
6. Checklist de QA anti-"AI-slop" (§2) antes de publicar.

---

## 5. Deuda técnica / avisos honestos

- El scroll-telling con 151 frames carga ~4 MB de webp si no se comprime bien.
  ORIVIA solo dibuja frames "cargados" (buffer 6): si el scroll va muy rápido,
  los frames finales no aparecen. Es un trade-off aceptable en 4G, pero hay que
  verificar en móvil real.
- `h-[620svh]` ocupa 6 pantallas: en móvil, hay que medir que no culmine
  en "fatiga de scroll" — ORIVIA agrega navegación con salto suave por step.
- `opacity:0` inline en hero sin clase de seguridad = blank-page si JS falla:
  NUNCA replicar sin fallback CSS.

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
