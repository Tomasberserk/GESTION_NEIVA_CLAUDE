# Especificación de Requisitos de Software (SRS) — Gestión Neiva
## Sistema POS SaaS Multi-Tenant para Micro-Negocios de Barrio

**Versión:** 1.0  
**Fecha:** 26 de mayo de 2026  
**Estado:** Borrador (Bloque 1)  
**Programa:** Análisis y Desarrollo de Software (ADSO) - SENA  

---

## Introducción
El presente documento describe los requisitos del Sistema de Gestión y Punto de Venta (POS) SaaS Multi-Tenant "Gestión Neiva", el cual tiene como finalidad optimizar los procesos de administración de inventarios, registro de ventas, control de alertas (vencimiento y stock) y cálculo de utilidades financieras en micro-negocios y tiendas de barrio en la ciudad de Neiva, garantizando eficiencia, control y facilidad de adopción para usuarios no técnicos.
Este documento servirá como base para el diseño, desarrollo, implementación y validación del software.

## Planteamiento del problema
Los micro-negocios y tiendas de barrio en la ciudad de Neiva presentan dificultades frecuentes en:
* Control y seguimiento manual de inventarios.
* Dependencia absoluta de la memoria del tendero para el abastecimiento.
* Pérdida de capital debido a productos perecederos que vencen en los estantes sin control.
* Desabastecimiento frecuente (quiebres de stock) de productos de alta demanda.
* Falta de cálculo de la utilidad neta real diaria del negocio.
* Ausencia de herramientas adaptadas a la baja conectividad (uso de datos móviles).
* Carga operativa excesiva en el conteo manual diario de productos.

Muchos micro-negocios utilizan herramientas dispersas como la memoria, cuadernos físicos o calculadoras tradicionales sin registros históricos, lo que genera:
* Errores en cuentas y cobros a clientes.
* Viajes de emergencia y costos adicionales de transporte a centrales de abasto (ej. Surabasto).
* Desperdicio y merma de productos vencidos.
* Pérdida de información histórica ante el extravío o deterioro físico de apuntes.
* Desconocimiento del estado financiero real y rentabilidad del negocio.

Se hace necesario un sistema centralizado, accesible desde dispositivos móviles, que permita gestionar de manera integral y ágil las ventas y el inventario de las tiendas de barrio.

## Propósito
El propósito de este documento es:
* Definir de manera clara y estructurada los requisitos del sistema.
* Establecer el alcance funcional del software.
* Servir como guía para desarrolladores, diseñadores y stakeholders.
* Reducir ambigüedades durante el desarrollo.
* Facilitar la validación y aceptación del sistema ante el SENA.

## Justificación
La implementación de un sistema especializado para micro-negocios y tiendas de barrio permitirá:
* Automatizar el control de existencias en tiempo real mediante el registro de ventas.
* Reducir pérdidas financieras mediante alertas automatizadas de vencimiento de productos (límite de 15 días).
* Facilitar el registro ágil de productos utilizando escáner de códigos de barras mediante la cámara de dispositivos móviles.
* Generar reportes financieros de ventas y utilidad neta en tiempo real.
* Aumentar la resiliencia del negocio ante problemas de conectividad mediante una interfaz optimizada para bajo consumo de datos móviles.
* Proveer una arquitectura multi-inquilino (multi-tenant) que reduzca los costos de alojamiento de datos para los usuarios finales.

Además, el sistema permitirá una administración moderna, ágil y trazable sin requerir hardware costoso de gran escala.

## Objetivo General
Desarrollar un sistema de gestión y punto de venta (POS) SaaS Multi-Tenant optimizado para dispositivos móviles que permita administrar de manera eficiente las ventas, el inventario, las alertas de vencimiento y los informes financieros de micro-negocios en la ciudad de Neiva.

## Objetivos específicos
* Diseñar un módulo multi-inquilino (multi-tenant) para el aislamiento y protección segura de los datos de cada comercio.
* Implementar un módulo de inventario simplificado con soporte para productos por unidad y a granel (fraccionamiento por peso).
* Desarrollar un sistema de ventas rápido (POS) con integración de escáner de códigos de barras a través de la cámara del celular.
* Implementar un módulo de alertas automáticas para stock mínimo y control de fechas de vencimiento de mercancía.
* Diseñar un panel de control (Dashboard) con gráficas de rendimiento financiero que calcule ingresos y utilidad diaria real.
* Habilitar la exportación del historial de transacciones e informes a formatos de hoja de cálculo (Excel).
* Implementar control de accesos basado en roles (Administrador/Tendero y Cajero/Ayudante).

## Alcance
El sistema permitirá:
* Registro y administración de múltiples empresas (tiendas independientes).
* Registro de productos con código de barras, categoría, precio de costo, precio de venta, fecha de vencimiento y unidad de medida.
* Escaneo de códigos de barras (EAN/UPC) utilizando la cámara trasera del dispositivo móvil.
* Gestión de categorías y marcas para organización de estanterías virtuales.
* Módulo de ventas con carrito interactivo que descuenta de forma automática el stock correspondiente.
* Soporte para venta de productos por fracciones numéricas (granel).
* Panel financiero (Dashboard) que muestra el total de ingresos, productos bajos de stock y alertas críticas de vencimiento.
* Historial de ventas detallado con filtros por rango de fechas (hoy, semana, meses).
* Exportación de reportes de cuadre de caja a Microsoft Excel.
* Gestión de usuarios con control de roles (Administrador vs Cajero).

El sistema no incluye inicialmente:
* Integración bancaria automática con datáfonos (fase futura).
* Facturación electrónica directa con la DIAN (fase posterior).
* Aplicación móvil nativa en tiendas de aplicaciones - iOS/Android (fase posterior, se utilizará Web App adaptada/PWA).

## Personal involucrado
**Tabla 1**  
*Registro estructurado de especificaciones técnicas ( Sección 1 )*

| Nombre | Rol | Categoría Profesional | Responsabilidad | Información de contacto |
|--------|-----|-----------------------|-----------------|-------------------------|
| [Nombre del Instructor] | Instructor | Ingeniero en sistemas | Supervisión técnica | correoinstructor@sena.edu.co |
| Tomás [Apellido] | Analista / Desarrollador | Aprendiz del tecnólogo en ADSO | Análisis de información, diseño, programación y despliegue | correoaprendiz1@gmail.com |
| [Nombre del Compañero] | Desarrollador | Aprendiz del tecnólogo en ADSO | Programación, pruebas y documentación | correoaprendiz2@gmail.com |

*Nota.* Especificación técnica sincronizada con la arquitectura vigente del proyecto. Fuente: Elaboración propia (2026).

**Tabla 2**  
*Registro estructurado de especificaciones técnicas ( Sección 2 )*

| Rol | Responsabilidad |
|-----|-----------------|
| Product Owner (Tenderos) | Definir requerimientos del negocio y prioridades de usabilidad. |
| Administrador (Dueño de tienda) | Registrar productos, compras, configurar alertas y validar la utilidad financiera. |
| Cajero / Ayudante | Registrar transacciones diarias en el POS y consultar disponibilidad física. |
| Desarrollador Backend | Implementar la lógica del servidor, base de datos relacional y aislamiento de datos por tenant. |
| Desarrollador Frontend | Implementar la interfaz responsiva, el flujo del carrito de compras y la integración del escáner. |
| QA Tester | Validar el funcionamiento global, el control de accesos por roles y la precisión matemática de los reportes. |

*Nota.* Especificación técnica sincronizada con la arquitectura vigente del proyecto. Fuente: Elaboración propia (2026).

## Definiciones, acrónimos y abreviaturas
**Tabla 3**  
*Registro estructurado de especificaciones técnicas ( Sección 3 )*

| Nombre | Descripción |
|--------|-------------|
| Usuario | Persona que interactúa con la aplicación (Administrador/Tendero o Cajero). |
| SRS / ERS | Especificación de Requisitos de Software. |
| SENA | Servicio Nacional de Aprendizaje. |
| POS | Point of Sale (Punto de venta). |
| SaaS | Software as a Service (Software como servicio). |
| Multi-Tenant | Arquitectura que permite servir a múltiples clientes con una única instancia de la aplicación. |
| Tenant | Inquilino o empresa registrada de forma aislada e independiente en el sistema. |
| JWT | JSON Web Token (Mecanismo seguro de autenticación por tokens). |
| Surabasto | Central mayorista de abasto y distribución de alimentos de Neiva, Huila. |
| Granel | Venta fraccionada de productos sueltos por peso (gramos, libras, kilos). |
| EAN / UPC | Estándares de códigos de barras leídos por el escáner de la aplicación. |
| UI | User Interface (Interfaz de Usuario). |
| UX | User Experience (Experiencia de Usuario). |
| Backend | Lógica del servidor y almacenamiento de datos. |
| Frontend | Interfaz gráfica y lógica ejecutada en el cliente. |
| API | Interfaz de Programación de Aplicaciones. |
| BD | Base de Datos (Sistema de almacenamiento relacional estructurado). |

*Nota.* Especificación técnica sincronizada con la arquitectura vigente del proyecto. Fuente: Elaboración propia (2026).

## Referencias
**Tabla 4**  
*Registro estructurado de especificaciones técnicas ( Sección 4 )*

| Título del Documento | Referencia |
|----------------------|------------|
| Standard IEEE 830 - 1998 | IEEE (Prácticas recomendadas para especificación de requisitos). |
| Repositorio del Proyecto | Código fuente funcional (app/main.py, models.py, frontend/src). |

*Nota.* Especificación técnica sincronizada con la arquitectura vigente del proyecto. Fuente: Elaboración propia (2026).

## Resumen
Este documento define los requisitos iniciales para el desarrollo del Sistema de Gestión y Punto de Venta (POS) SaaS Multi-Tenant "Gestión Neiva", el cual busca centralizar, simplificar y automatizar los procesos de administración de inventarios y registro de ventas para micro-negocios en Neiva. El sistema garantiza la resiliencia en conexiones de red móvil, alertas tempranas de pérdida de stock o vencimiento y cálculo automático de utilidades diarias sin requerir hardware costoso, promoviendo una gestión moderna, accesible y 100% digital para los tenderos.

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
