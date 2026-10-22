# Software y servicios de internet: fundamentos técnicos para la práctica profesional

## Introducción

El software dejó de ser un artefacto auxiliar para convertirse en la infraestructura sobre la que operan las organizaciones. Un sistema de facturación, una pasarela de pagos o el simple registro de inventario de una microempresa son hoy puntos de contacto entre procesos de negocio y servicios de internet: alguien escribe un dato en una interfaz, ese dato viaja por una red, se valida en un servidor y se persiste en una base de datos, y todo ello ocurre en milisegundos y bajo expectativas de disponibilidad cercanas al 99,9 %. Comprender qué hay detrás de esa cadena no es un ejercicio académico: es la diferencia entre diseñar un sistema que resiste el uso real y uno que falla en el primer pico de tráfico, o entre proteger la información de un cliente y exponerla por una decisión de configuración tomada sin criterio.

En el contexto técnico-profesional, el estudio del software y de los servicios de internet tiene tres justificaciones concretas. La primera es económica: las decisiones de arquitectura (monolito o microservicios, servidor propio o nube gestionada, software propietario o libre) determinan el costo total de propiedad durante años, no solo el costo inicial de desarrollo. La segunda es de riesgo: la mayoría de los incidentes de seguridad explotados en producción —interceptación de credenciales, manipulación de respuestas, exposición de bases de datos— se apoya en fallos comprensibles solo si se entiende el protocolo, el modelo de responsabilidad del proveedor cloud y la superficie de ataque del cliente. La tercera es de calidad: clasificar correctamente un sistema permite elegir las métricas, las pruebas y el modelo de mantenimiento adecuados; no se evalúa igual un firmware embebido que un SaaS multiinquilino.

Este documento desarrolla esos tres ejes con profundidad técnica. Primero presenta una clasificación del software desde criterios funcionales, de licenciamiento y de despliegue; después analiza la arquitectura cliente-servidor y sus variantes contemporáneas; a continuación contrasta HTTP con HTTPS a nivel de protocolo, cifrado y cadena de certificados; y finalmente compara los modelos de servicio en la nube (IaaS, PaaS y SaaS) desde la perspectiva de la responsabilidad compartida. El cierre integra los conceptos en un caso de decisión real: el sistema de gestión para una microempresa comercial.

## Desarrollo teórico y análisis técnico

### 1. Clasificación del software

Clasificar software exige elegir el criterio, porque ninguna taxonomía única lo cubre todo. El criterio **funcional** distingue el *software de sistema* (sistemas operativos, controladores, hipervisores, gestores de arranque), que administra el hardware y provee la abstracción sobre la que corre todo lo demás; el *software de aplicación* (ERP, CRM, navegadores, editores), orientado a tareas del usuario final; el *middleware* (servidores de aplicación, brokers de mensajes, API gateways), que conecta componentes distribuidos; las *herramientas de desarrollo* (compiladores, entornos integrados, sistemas de control de versiones) y el *firmware*, almacenado en memoria no volátil y ejecutado directamente por dispositivos embebidos.

El criterio de **licenciamiento** separa el software propietario —código cerrado, uso regulado por contrato, sin derecho de modificación— del software libre y de código abierto (FOSS), donde el acceso al código fuente habilita cuatro libertades: ejecutar, estudiar, redistribuir y mejorar. Dentro del FOSS las licencias no son equivalentes: la GPL es *copyleft* fuerte y obliga a liberar las obras derivadas bajo los mismos términos; la LGPL lo suaviza para bibliotecas enlazadas dinámicamente; MIT, BSD y Apache 2.0 son permisivas y permiten incorporar el código en productos cerrados, con la diferencia de que Apache 2.0 añade una concesión explícita de patentes. Esta distinción tiene consecuencias jurídicas y de negocio directas al elegir dependencias: introducir una librería GPL en un producto propietario puede obligar a abrir el código o a rediseñar el componente.

El criterio de **despliegue y arquitectura** es el más relevante para el diseño moderno. Un *monolito* empaqueta toda la aplicación en una unidad desplegable: es simple de desarrollar y depurar, pero escala como un todo y acopla los ciclos de liberación. Un *monolito modular* conserva un único despliegue pero impone fronteras internas explícitas (módulos con interfaces y dependencias controladas), lo que suele ser el punto de partida recomendable. Los *microservicios* dividen el sistema en servicios autónomos, desplegables de forma independiente y comunicados por red; ganan en escalabilidad selectiva y aislamiento de fallos, pero introducen complejidad distribuida: latencia de red, consistencia eventual, trazas, reintentos idempotentes y observabilidad obligatoria. El modelo *serverless* (funciones como servicio) delega el escalado y el ciclo de vida del servidor en el proveedor, a cambio de límites de ejecución, arranque en frío (*cold start*) y dependencia del ecosistema.

| Criterio | Categorías | Implicación práctica |
|---|---|---|
| Función | Sistema, aplicación, middleware, herramientas, firmware | Define el tipo de pruebas y el perfil de mantenimiento |
| Licencia | Propietario, permisivo (MIT/Apache), copyleft (GPL/LGPL) | Afecta la distribución y la propiedad intelectual |
| Despliegue | On-premise, nube, web, móvil, embebido | Determina el modelo operativo y los costos |
| Arquitectura | Monolito, modular, microservicios, serverless | Condiciona escalabilidad, latencia y complejidad operativa |

### 2. Arquitectura cliente-servidor

La arquitectura cliente-servidor organiza el cómputo en dos roles: el **cliente** inicia la comunicación y formula solicitudes; el **servidor** escucha en un puerto, procesa y responde. El servidor no conoce al cliente de antemano, lo que permite atender a muchos simultáneamente y convierte la comunicación en un ciclo *petición–respuesta* sobre un protocolo acordado (habitualmente TCP/IP). El cliente se identifica mediante una dirección IP y un puerto, y resuelve nombres a direcciones mediante DNS. Este desacoplamiento es la razón por la que un solo backend puede servir a una aplicación web, una app móvil y una integración con terceros.

La variante **de tres capas** es el patrón dominante en aplicaciones de negocio. La capa de **presentación** (navegador, SPA, app móvil) solo se ocupa de la interacción y no debe contener reglas de negocio; la capa de **lógica** (API, servicios, validaciones, autorización) concentra el dominio y es la única que decide; la capa de **datos** (SGBD relacional o no relacional, almacenamiento de objetos, caché) garantiza persistencia y concurrencia. Separar estas capas permite escalar la presentación con CDN, replicar la lógica sin estado y escalar la base de datos con réplicas de lectura, además de aislar el impacto de un cambio.

Un principio central es la **ausencia de estado en el servidor** (*statelessness*): si cada petición transporta las credenciales necesarias (por ejemplo, un token firmado), cualquier instancia puede atenderla y el balanceo de carga se vuelve trivial. El estado de sesión se desplaza al cliente o a un almacén compartido (Redis). Esto habilita el **escalado horizontal** —añadir instancias en lugar de potenciar una sola máquina— y la tolerancia a fallos mediante reemplazo de instancias.

El modelo también tiene límites. La comunicación síncrona encadena latencias y propaga fallos: si el servidor tarda, el cliente espera; si cae, la operación se pierde salvo que existan reintentos idempotentes y *timeouts*. Por eso los sistemas maduros incorporan mecanismos complementarios: colas de mensajes para trabajo asíncrono, *caché* para lecturas repetidas, *circuit breakers* para detener cascadas de error y *rate limiting* para protegerse de abuso. Existen además arquitecturas alternativas: **peer-to-peer**, sin servidor central; **event-driven**, donde los componentes reaccionan a eventos publicados; y **streaming**, para datos continuos. En entornos móviles y de IoT, el patrón puede invertirse parcialmente con *long polling*, **WebSocket** (canal bidireccional persistente) o MQTT (publicación/suscripción sobre TCP, con bajo consumo).

### 3. HTTP frente a HTTPS: la diferencia técnica

**HTTP** (HyperText Transfer Protocol) es un protocolo de la capa de aplicación, sin estado, basado en un modelo de petición y respuesta con métodos que expresan la intención: `GET` para recuperar, `POST` para crear, `PUT`/`PATCH` para reemplazar o modificar, `DELETE` para eliminar, `HEAD` y `OPTIONS` para metadatos y negociación. Las respuestas se identifican con códigos de estado agrupados por clase: 2xx éxito, 3xx redirección, 4xx error del cliente, 5xx error del servidor. Las cabeceras transportan metadatos (tipo de contenido, caché, autenticación, idioma) y son parte esencial del contrato entre cliente y servidor.

HTTP viaja normalmente sobre TCP en el puerto 80 y **no ofrece confidencialidad ni integridad**: cualquier nodo intermedio —un router Wi-Fi, un proxy corporativo, un proveedor de red— puede leer y modificar el contenido en tránsito. Esto hace inviable enviar contraseñas, tokens o datos personales por HTTP. HTTP/1.1 introdujo conexiones persistentes y *pipelining* limitado; HTTP/2 añadió multiplexación de flujos sobre una sola conexión TCP, compresión de cabeceras (HPACK) y *server push*; HTTP/3 sustituye TCP por QUIC sobre UDP para reducir la latencia de establecimiento y evitar el bloqueo de cabeza de línea.

**HTTPS** no es un protocolo distinto en su semántica: es HTTP transportado sobre **TLS** (Transport Layer Security) en el puerto 443. TLS aporta tres garantías:

1. **Confidencialidad**: el contenido se cifra con cifrado simétrico (AES-GCM o ChaCha20-Poly1305), mucho más rápido que el asimétrico.
2. **Integridad**: cada registro incluye un código de autenticación (AEAD) que detecta alteraciones; un atacante no puede modificar un byte sin invalidar el mensaje.
3. **Autenticación del servidor**: el servidor presenta un certificado X.509 firmado por una autoridad de certificación (CA) incluida en el almacén de confianza del cliente. El certificado vincula un nombre de dominio con una clave pública; el cliente verifica la cadena de firmas, la vigencia, la revocación (OCSP/CRL) y que el nombre coincida.

El **handshake** de TLS 1.3 (RFC 8446) reduce el intercambio a un viaje de ida y vuelta: cliente y servidor acuerdan versión y *suite* criptográfica, realizan un intercambio Diffie-Hellman efímero (lo que aporta *forward secrecy*: comprometer la clave privada del servidor en el futuro no descifra sesiones pasadas), validan el certificado y derivan claves simétricas de sesión. TLS 1.2 requería dos viajes y permitía suites más débiles; por eso hoy se recomienda 1.3, con 1.2 como mínimo aceptable y versiones anteriores deshabilitadas. Mecanismos complementarios refuerzan el modelo: **SNI** permite alojar varios dominios en una IP y presentar el certificado correcto; **HSTS** obliga al navegador a usar HTTPS durante un periodo y bloquea el downgrade; **ALPN** negocia HTTP/2 o HTTP/3 dentro del mismo puerto.

| Aspecto | HTTP | HTTPS |
|---|---|---|
| Puerto por defecto | 80 | 443 |
| Cifrado en tránsito | No | Sí (TLS simétrico + asimétrico en el handshake) |
| Integridad | No verificable | Sí (AEAD) |
| Autenticación del servidor | No | Sí, vía certificado X.509 y CA |
| Resistencia a *sniffing* / MITM | Nula | Alta, si la configuración es correcta |
| Costo computacional | Bajo | Mayor en el handshake; despreciable con sesiones reutilizadas |
| Requisito operativo | Ninguno | Certificado válido y renovación automatizada |

Conviene precisar el alcance de la garantía: HTTPS protege el tramo entre cliente y servidor, pero **no protege los datos en reposo**, no impide que un servidor malicioso o comprometido los use indebidamente, y no sustituye controles de aplicación como la validación de entrada, la autorización por recurso, la protección contra XSS o CSRF, ni el cifrado de la base de datos. Un sitio con candado puede seguir siendo vulnerable; el candado certifica identidad y cifrado del canal, no corrección del software. Por eso la práctica profesional exige HTTPS como línea base —hoy gratuito mediante Let's Encrypt y automatizable con ACME— y, sobre ella, una higiene de aplicación completa.

### 4. Modelos de servicio en la nube

El NIST (SP 800-145) define la computación en nube por cinco características esenciales: autoservicio bajo demanda, acceso amplio por red, agrupación de recursos, elasticidad rápida y servicio medido. Sobre esa base se distinguen tres modelos de servicio según dónde se sitúa la frontera de responsabilidad.

**IaaS** (Infrastructure as a Service) entrega recursos virtualizados: máquinas, redes, volúmenes, balanceadores. El proveedor gestiona el hardware, la virtualización y el centro de datos; el cliente gestiona el sistema operativo, los parches, el runtime, la aplicación y sus datos. Ejemplos: Amazon EC2, Azure Virtual Machines, Google Compute Engine. Ofrece máximo control y portabilidad conceptual, pero exige capacidad operativa real: alguien debe parchear, monitorizar y asegurar cada instancia.

**PaaS** (Platform as a Service) entrega un entorno de ejecución gestionado: el cliente despliega código y el proveedor se ocupa del sistema operativo, el escalado, el balanceo y, a menudo, la base de datos gestionada. Ejemplos: Heroku, Google App Engine, Azure App Service, Vercel. Reduce drásticamente la carga operativa y acelera la entrega, a cambio de menor control sobre el entorno y mayor acoplamiento a las API del proveedor (*vendor lock-in*).

**SaaS** (Software as a Service) entrega la aplicación completa: el cliente solo consume la funcionalidad mediante un navegador o API, y el proveedor gestiona toda la pila, incluidos datos y actualizaciones. Ejemplos: Gmail, Microsoft 365, Salesforce. Maximiza la simplicidad y traslada el mantenimiento al proveedor, pero limita la personalización profunda, la soberanía sobre los datos y la capacidad de integración a lo que el producto exponga.

| Modelo | Gestiona el proveedor | Gestiona el cliente | Control | Esfuerzo operativo |
|---|---|---|---|---|
| IaaS | Hardware, red, virtualización | SO, runtime, app, datos | Alto | Alto |
| PaaS | Hasta el runtime y el escalado | Código, configuración, datos | Medio | Medio |
| SaaS | Toda la pila | Uso, identidades, configuración | Bajo | Bajo |

Junto a los tres modelos clásicos aparece **FaaS/serverless**, una especialización de PaaS donde la unidad de despliegue es una función activada por eventos, con escalado a cero y facturación por invocación. Es excelente para cargas intermitentes y tareas de integración, y problemático para procesos de larga duración o con estado.

La elección entre modelos no es ideológica, sino de encaje. Deben evaluarse: el grado de control requerido (cumplimiento normativo, cifrado con claves propias, versiones específicas del motor de base de datos), el costo total de propiedad incluyendo horas de operación, la latencia hacia los usuarios, la resiliencia exigida, la madurez del equipo y el riesgo de dependencia del proveedor. Los **modelos de despliegue** —nube pública, privada, híbrida y comunitaria— son un eje independiente: una empresa puede ejecutar un SaaS de nómina sobre una nube pública y, a la vez, mantener datos sensibles en una nube privada conectada por VPN.

### 5. Integración: decisiones en un sistema de gestión para microempresa

El caso de un sistema de inventario y ventas para una microempresa permite ver cómo se articulan los conceptos. La arquitectura adecuada es **cliente-servidor de tres capas**: una interfaz web o móvil (presentación), una API que concentra reglas como descuentos de stock y validación de precios (lógica) y una base de datos relacional con transacciones (datos). El backend debe ser *stateless* y autenticar con tokens firmados, de modo que pueda escalar horizontalmente si el negocio crece. Toda comunicación va por **HTTPS** con TLS 1.3 y certificado renovado automáticamente; HTTP queda restringido a redirección o deshabilitado. El software puede construirse sobre componentes de código abierto con licencias permisivas, lo que reduce costo y evita obligaciones de copyleft, siempre que se audite la cadena de dependencias.

En cuanto al modelo de servicio, un equipo pequeño sin operaciones dedicadas obtiene mejor relación costo-riesgo con **PaaS** (aplicación y base de datos gestionadas) que con IaaS, donde tendría que administrar parches y copias de seguridad. SaaS solo sería preferible si existiera un producto estándar que cubriera el proceso sin adaptaciones; en cuanto se requiere lógica propia —por ejemplo, facturación con reglas locales—, la rigidez del SaaS se convierte en un costo. La decisión correcta no maximiza una métrica aislada: equilibra control, esfuerzo operativo y riesgo de dependencia, y se revisa cuando cambian el volumen de datos o los requisitos regulatorios.

## Conclusiones

El software se entiende mejor como una cadena de decisiones interconectadas que como un conjunto de archivos. La clasificación permite nombrar con precisión qué se está construyendo y qué obligaciones —licencias, pruebas, operación— conlleva. La arquitectura cliente-servidor, con separación de capas y servidores sin estado, sigue siendo el esqueleto de la mayoría de los sistemas profesionales, incluso cuando se descompone en servicios o funciones. HTTP y HTTPS no son versiones de una misma cosa con un candado añadido: HTTPS es HTTP más una capa criptográfica que garantiza confidencialidad, integridad y autenticación, y cuyo valor depende de una configuración correcta y de controles de aplicación complementarios. Finalmente, IaaS, PaaS y SaaS describen dónde termina la responsabilidad del proveedor y empieza la del equipo; elegir bien exige medir control, costo operativo y dependencia, no solo precio de lista.

## Referencias

- Fielding, R., Nottingham, M., y Reschke, J. (2022). *RFC 9110: HTTP Semantics*. IETF.
- Rescorla, E. (2018). *RFC 8446: The Transport Layer Security (TLS) Protocol Version 1.3*. IETF.
- Mell, P., y Grance, T. (2011). *The NIST Definition of Cloud Computing* (SP 800-145). NIST.
- ISO/IEC 25010:2011. *Systems and software Quality Requirements and Evaluation (SQuaRE) — Quality models*.
- Sommerville, I. (2016). *Software Engineering* (10.ª ed.). Pearson.
- Pressman, R., y Maxim, B. (2020). *Software Engineering: A Practitioner's Approach* (9.ª ed.). McGraw-Hill.
