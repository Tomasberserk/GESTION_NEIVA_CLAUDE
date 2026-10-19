---
description: |
  Diseña y construye frontends premium, humanos, accesibles y de alto
  rendimiento para Gestión Neiva: un POS y sistema de gestión comercial
  para tenderos, micromercados y pequeños negocios de Colombia. Úsala al
  crear, rediseñar, auditar o implementar landing pages, onboarding,
  POS, inventario, reportes y componentes de producto. Prioriza claridad
  para usuarios con alfabetización digital variable y rendimiento en
  Android económico.
name: gestion-neiva-frontend-craft
---

# Gestión Neiva Frontend Craft

## Misión

Crear interfaces que se sientan contemporáneas, suaves y deliberadas
---con curvas orgánicas, transiciones discretas y tipografía
excelente--- sin copiar literalmente a otras marcas ni sacrificar
velocidad, legibilidad o facilidad de uso.

El producto sirve a tenderos y pequeños comerciantes de Neiva y del sur
de Colombia. El éxito no se mide por cuánto movimiento tiene la página,
sino por si una persona entiende el beneficio, encuentra la acción
correcta y puede usar el sistema en un teléfono económico con conexión
limitada.

## Principios no negociables

1.  **Primero la tarea, después el efecto.** Cada componente debe ayudar
    a entender, decidir, navegar o completar una tarea.
2.  **Producto real antes que decoración.** Mostrar la interfaz real de
    Gestión Neiva, ejemplos de inventario y flujos de venta. No inventar
    métricas, testimonios ni resultados.
3.  **Suavidad sin exceso de glassmorphism.** Curvas orgánicas,
    superficies cálidas y sombras ligeras; evitar blur extenso, capas de
    vidrio por todas partes y tarjetas dentro de tarjetas.
4.  **Móvil de gama baja como primera clase.** La experiencia esencial
    debe funcionar sin animaciones, vídeo, canvas ni imágenes grandes.
5.  **Una jerarquía por pantalla.** Un mensaje principal, una acción
    primaria y una acción secundaria como máximo.
6.  **Accesibilidad incorporada.** Teclado, foco visible, semántica,
    contraste WCAG AA, texto ampliable y `prefers-reduced-motion`.
7.  **No simular capacidades.** No crear gráficas, ventas, clientes,
    testimonios, insignias de seguridad ni integraciones ficticias como
    si fueran datos reales.
8.  **Respetar el stack existente.** React 19, Vite, Tailwind CSS v4 y
    `motion` si ya está instalado. No añadir dependencias grandes sin
    justificar su coste.
9.  **Performance como requisito de diseño.** Evitar trabajo continuo en
    segundo plano, imágenes sin optimizar, layout shifts y JavaScript
    innecesario.
10. **La identidad no es una copia.** Aprender principios de referentes,
    no reproducir su composición, textos, ilustraciones ni marca.

## Benchmark: diez referentes y qué aprender de ellos

Esta es una selección curada de patrones de productos digitales
conocidos, no un ranking universal ni una afirmación de que sean los
diez mejores sitios en todos los criterios. Inspecciona las páginas
actuales antes de implementar una referencia.

  ----------------------------------------------------------------------------------
  Referente                 Patrón que estudiar  Adaptación válida No copiar
                                                 para Gestión      
                                                 Neiva             
  ------------------------- -------------------- ----------------- -----------------
  Linear ---                Jerarquía precisa,   Mostrar una venta Oscuridad total,
  https://linear.app        interfaz de producto o una consulta    densidad para
                            como protagonista,   real del POS con  desarrolladores o
                            microinteracciones   foco visual claro animaciones
                            contenidas                             cinemáticas por
                                                                   defecto

  Stripe ---                Mensaje directo,     Explicar valor    Mesh gradients
  https://stripe.com        confianza, visuales  con una           costosos, jerga
                            de producto y        demostración      financiera o
                            composición por      breve y datos     densidad
                            capas                comprensibles     empresarial

  Vercel ---                Ritmo visual,        Navegación        Efectos técnicos
  https://vercel.com        claridad de          predecible y      que no aportan al
                            navegación,          estructura        tendero
                            documentación y      consistente entre 
                            producto coherentes  landing y         
                                                 aplicación        

  Notion ---                Lenguaje cercano,    Explicar cada     Convertir todo en
  https://www.notion.so     modularidad, baja    función con       tarjetas o
                            intimidación         palabras          depender de
                                                 cotidianas y      ilustraciones
                                                 ejemplos del      genéricas
                                                 negocio           

  Framer ---                Calidad de acabado,  Transiciones      Animación pesada,
  https://www.framer.com    composición          cortas y          scroll hijacking
                            editorial y          composición con   o páginas que
                            movimiento           personalidad      tardan en revelar
                            intencional                            contenido

  Ramp --- https://ramp.com Sistema visual       Crear reglas      Estética
                            consistente y        repetibles para   corporativa
                            agrupación por       botones,          financiera que no
                            prioridades          tarjetas, estados encaje con el
                                                 y cifras          comercio de
                                                                   barrio

  Shopify ---               Presentación de      Mostrar el flujo  Complejidad
  https://www.shopify.com   comercio y recorrido de registrar      omnicanal que no
                            de adopción          productos, vender pertenezca al MVP
                                                 y revisar         
                                                 resultados        

  Square ---                Comunicación directa Mostrar el punto  Prometer
  https://squareup.com      de POS y             de venta en       dispositivos,
                            hardware/flujo       contexto y        pagos o
                            comercial            explicar qué      integraciones que
                                                 resuelve          Gestión Neiva no
                                                                   ofrece

  Figma ---                 Demostración del     Enseñar el flujo  Interacciones de
  https://www.figma.com     producto, estados    real en pasos     editor complejo
                            visuales claros y    cortos y con      en una landing
                            consistencia de      controles         sencilla
                            componentes          legibles          

  Arc --- https://arc.net   Formas orgánicas,    Usar curvas       Copiar su
                            asimetría y una      suaves, recortes  lenguaje gráfico
                            identidad visual     fotográficos y    o crear layouts
                            reconocible          composición       difíciles de leer
                                                 asimétrica con    en móvil
                                                 moderación        
  ----------------------------------------------------------------------------------

### Regla de interpretación

Los referentes aportan principios, no una plantilla acumulativa. No
combines simultáneamente el gradiente de Stripe, el minimalismo oscuro
de Linear, la modularidad de Notion y la animación de Framer. Escoge una
dirección visual dominante y una o dos influencias secundarias.

Para Gestión Neiva, la dirección recomendada es:

**"Calma comercial cálida"**: crema y blanco cálido, verde profundo como
ancla de confianza, verde menta para estados positivos, ámbar reservado
para énfasis, fotografía documental auténtica y formas orgánicas grandes
de bajo contraste.

## Sistema visual recomendado

### Paleta de partida

Usar estos tokens como punto de partida y verificar contrastes con los
colores finales y estados interactivos:

-   `--gn-ink: #14251F` --- texto principal y superficies oscuras.
-   `--gn-forest: #1E493B` --- marca y secciones de énfasis.
-   `--gn-green: #087F5B` --- acción primaria.
-   `--gn-mint: #DDF5E9` --- superficies positivas suaves.
-   `--gn-cream: #FAF8F2` --- fondo cálido.
-   `--gn-paper: #FFFFFF` --- superficies de contenido.
-   `--gn-muted: #5D6B65` --- texto secundario; validar contraste.
-   `--gn-amber: #B96E13` --- acento sobre fondos claros.
-   `--gn-line: #E5E9E5` --- separadores discretos.
-   `--gn-danger: #B42318` --- errores; no comunicar errores solo con
    color.

No utilizar ámbar claro como texto sobre crema. El texto normal debe
cumplir al menos 4.5:1 y el texto grande al menos 3:1 según WCAG AA.

### Curvas y superficies

-   Radio de control: `10–14px`.
-   Radio de tarjeta: `16–22px`.
-   Radio de panel editorial: `28–40px`.
-   Píldoras solo para estados, categorías breves y acciones que
    realmente lo justifiquen.
-   Sombra base muy sutil; los bordes no deben rodear todas las
    tarjetas.
-   No encerrar cada párrafo o icono en una caja.
-   Evitar el blur grande como elemento permanente. Preferir gradientes
    estáticos y superficies opacas.
-   Usar fotografía real de comercios locales cuando exista
    autorización; no presentar imágenes generadas como clientes reales.

### Tipografía y layout

-   H1 móvil: `36–42px`, line-height `1.05–1.15`.
-   H1 escritorio: `48–60px`.
-   H2 móvil: `28–32px`; escritorio: `34–42px`.
-   Texto de lectura: mínimo `16px`, line-height `1.5–1.7`.
-   Texto auxiliar: preferiblemente `14px` o más; nunca esconder
    instrucciones importantes en texto minúsculo.
-   Ancho de lectura: `60–68ch`.
-   Contenedor principal: máximo aproximado `1120–1200px`.
-   Espaciado con una escala consistente de 4/8 px; dejar más aire entre
    secciones que entre elementos relacionados.
-   En móvil, una columna; no reducir las tarjetas de escritorio hasta
    convertirlas en bloques estrechos e ilegibles.

## Patrones por tipo de pantalla

### 1. Landing pública

Orden recomendado:

1.  Hero: quién es el producto, para quién y beneficio principal.
2.  Evidencia del producto: captura o demo real del POS.
3.  Tres problemas concretos que resuelve.
4.  Tres capacidades principales, no un catálogo de todo el sistema.
5.  Cómo empezar en tres o cuatro pasos.
6.  Testimonios reales y autorizados, si existen.
7.  FAQ para objeciones reales.
8.  CTA final y footer sencillo.

Reglas: - Un CTA principal, por ejemplo "Crear cuenta"; un secundario,
por ejemplo "Ver cómo funciona". - No añadir un vídeo autoplay ni un
canvas como requisito para entender el producto. - Fusionar secciones
que repitan la misma promesa. - Usar datos concretos solo si se pueden
verificar. - El formulario de registro debe explicar qué se necesita y
qué ocurrirá después.

### 2. POS y registro de venta

-   Priorizar el campo de búsqueda, lector de código de barras,
    productos, total y acción de cobrar.
-   Botones grandes, claros y fáciles de alcanzar con el pulgar.
-   Evitar animaciones que retrasen la confirmación de una venta.
-   Mantener visible el estado de la operación y prevenir dobles envíos.
-   Estados vacíos con una acción siguiente clara.
-   Errores expresados en lenguaje cotidiano y con recuperación posible.
-   No depender solo de color, sonido o movimiento para confirmar una
    operación.

### 3. Inventario

-   Buscar y filtrar antes que mostrar controles secundarios.
-   Distinguir visualmente stock bajo, agotado y normal, con texto/icono
    además del color.
-   Mostrar primero nombre, existencia y acción útil.
-   Mostrar precio de costo únicamente a roles autorizados; no confiar
    en ocultarlo solo con CSS.
-   Evitar tablas anchas en móviles: utilizar filas compactas o tarjetas
    de datos con jerarquía consistente.

### 4. Reportes

-   Empezar con la pregunta que el comerciante quiere responder, no con
    una pared de gráficas.
-   Dar prioridad a totales, periodo, explicación sencilla y comparación
    útil.
-   Etiquetar moneda y rango de fechas.
-   Gráficas solo si mejoran la comprensión; siempre ofrecer resumen
    textual.
-   Nunca fabricar datos para llenar una visualización de demostración
    sin etiquetarlos como datos de ejemplo.

### 5. Onboarding

-   Una decisión importante por paso.
-   Mostrar progreso y permitir volver sin perder datos.
-   Usar ejemplos de productos y ventas solo como demostración
    claramente identificada.
-   Explicar términos como "inventario" o "ganancia" con palabras
    conocidas cuando sea necesario.
-   Priorizar la primera tarea exitosa: crear el negocio, agregar un
    producto y registrar una venta de prueba.

## Motion: una gramática de movimiento pequeña

No animar por defecto cada elemento. El movimiento debe comunicar
entrada, respuesta, progreso o cambio de estado.

### Tokens recomendados

``` css
:root {
  --gn-motion-fast: 180ms;
  --gn-motion-enter: 420ms;
  --gn-motion-ease: cubic-bezier(0.22, 1, 0.36, 1);
}

.gn-reveal {
  opacity: 0;
  transform: translateY(10px);
  transition:
    opacity var(--gn-motion-enter) var(--gn-motion-ease),
    transform var(--gn-motion-enter) var(--gn-motion-ease);
}

.gn-reveal.is-visible {
  opacity: 1;
  transform: translateY(0);
}

@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    scroll-behavior: auto !important;
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }

  .gn-reveal,
  .gn-reveal.is-visible {
    opacity: 1;
    transform: none;
  }
}
```

-   Interacciones pequeñas: 140--200 ms.
-   Reveal de sección: 320--420 ms y desplazamiento de 8--12 px.
-   Stagger: 30--50 ms, como máximo tres pasos.
-   Ken Burns: solo si la fotografía lo necesita; preferiblemente uno
    por página, no en todos los fondos.
-   Springs solo para elementos interactivos que deban sentirse
    elásticos; no para sincronizar el scroll con frames.
-   Nunca retrasar una venta, una confirmación, una navegación o la
    lectura del contenido por una animación.
-   Pausar tareas fuera del viewport y cuando
    `document.visibilityState !== "visible"`.
-   No usar `will-change` de forma permanente en muchos elementos.
-   No introducir GSAP, Three.js, Lottie o WebGL por defecto.

## Presupuesto de rendimiento

Son presupuestos de proyecto, no garantías automáticas:

-   Core Web Vitals objetivo en campo, percentil 75: LCP ≤ 2.5 s, INP ≤
    200 ms, CLS ≤ 0.1.
-   JavaScript inicial comprimido: objetivo ≤ 150 kB cuando la
    arquitectura lo permita; medir antes de imponerlo como gate
    definitivo.
-   Imagen LCP móvil: objetivo aproximado de 100--180 kB, según
    contenido y calidad.
-   Imágenes secundarias: optimizadas, dimensionadas y con carga
    diferida si están fuera de pantalla.
-   Vídeo: no descargar hasta que el usuario lo solicite, salvo que
    exista una justificación medida.
-   Reservar dimensiones para imágenes, vídeos y componentes diferidos
    para evitar CLS.
-   Cargar componentes pesados solo cuando la ruta o la interacción los
    requiera.
-   Evitar decodificar o descargar imágenes dentro de callbacks de
    scroll.
-   En canvas con secuencias: poster inmediato, frames cercanos bajo
    demanda, caché limitada y fallback estático.
-   El contenido y las acciones esenciales deben funcionar sin motion.

## Accesibilidad y confianza

Antes de dar una pantalla por terminada, verificar:

-   Contraste WCAG AA.
-   Foco de teclado visible y orden lógico.
-   Targets táctiles cómodos, con objetivo de 44 × 44 CSS px para
    controles principales.
-   Etiquetas accesibles en botones, inputs e iconos.
-   Mensajes de error y éxito comprensibles.
-   Compatibilidad con zoom del navegador al 200%.
-   `prefers-reduced-motion`.
-   Alternativas textuales para imágenes informativas y canvas.
-   Subtítulos para vídeo con voz.
-   No comunicar estado únicamente por color.
-   No mostrar testimonios, cifras de clientes, certificaciones o
    promesas sin evidencia.
-   No revelar información sensible de negocio a usuarios sin permiso.

## Workflow obligatorio para el agente

### Fase 1 --- Descubrir antes de diseñar

1.  Inspeccionar el repositorio, package scripts, rutas, componentes,
    tokens, estilos y dependencias existentes.
2.  Identificar si se trabaja en landing pública o en una pantalla
    operativa del POS.
3.  Determinar la tarea primaria, el usuario y el dispositivo más
    restrictivo.
4.  Confirmar qué datos y capacidades existen realmente.
5.  No reemplazar arquitectura ni instalar dependencias antes de
    explicar por qué hacen falta.

### Fase 2 --- Definir una dirección

Proponer una sola dirección visual dominante y describir: - concepto
visual en una frase; - paleta y tipografía; - estructura de
información; - componentes reutilizables; - movimiento permitido; -
presupuesto de performance; - riesgos de accesibilidad.

Para Gestión Neiva, comenzar con "Calma comercial cálida" salvo que el
usuario pida explícitamente otra dirección.

### Fase 3 --- Implementar por capas

1.  Estructura semántica y contenido real.
2.  Layout responsive.
3.  Tokens y componentes compartidos.
4.  Estados de carga, error, vacío, éxito y permisos.
5.  Motion discreto.
6.  Optimización y accesibilidad.
7.  Verificación en build de producción.

### Fase 4 --- Validar

Ejecutar los scripts existentes de lint, tests y build. Si no existen,
indicar claramente qué se pudo verificar y qué no. Revisar: - consola y
errores de runtime; - ancho de 320--360 px; - tablet y escritorio; -
teclado y reduced motion; - tamaños de recursos y chunks; - estados
vacíos y fallos de red; - roles y permisos; - datos falsos accidentales.

No afirmar "aprobado en Android de 2 GB" sin probar ese dispositivo o un
entorno físico equivalente. Lighthouse y throttling son una
aproximación, no una sustitución total del hardware real.

## Definition of Done

Una entrega solo está lista cuando:

-   El beneficio y la acción principal se entienden en cinco segundos.
-   El diseño se reconoce como Gestión Neiva, no como copia de una
    referencia.
-   Los componentes se comportan bien en móvil y escritorio.
-   El contenido esencial no depende de animaciones.
-   No se añadieron dependencias pesadas sin justificación.
-   Los colores y textos cumplen contraste accesible.
-   Las imágenes tienen tamaños adecuados y dimensiones reservadas.
-   Las interacciones incluyen loading, error, success y disabled cuando
    corresponda.
-   No se inventaron datos ni testimonios.
-   El build y las pruebas disponibles pasan, o los fallos pendientes
    están documentados.

## Formato de entrega que debe producir la skill

Al terminar una tarea de frontend, informar:

1.  **Dirección de diseño:** concepto y decisiones principales.
2.  **Cambios realizados:** archivos y componentes.
3.  **Decisiones de UX:** cómo ayuda al tendero a completar la tarea.
4.  **Rendimiento:** chunks, recursos y mediciones reales disponibles.
5.  **Accesibilidad:** verificaciones ejecutadas y pendientes.
6.  **Pruebas:** comandos ejecutados y resultado.
7.  **Deuda restante:** solo los riesgos que realmente importan.

No declarar un resultado perfecto sin evidencia. Preferir una interfaz
sencilla, rápida y confiable a una demostración espectacular pero
frágil.
