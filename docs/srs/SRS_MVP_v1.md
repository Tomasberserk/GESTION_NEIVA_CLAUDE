# Especificación de Requisitos de Software (SRS) — Gestión Neiva
## Sistema POS SaaS Multi-Tenant para Micro-Negocios de Barrio

**Versión:** 1.0  
**Fecha:** 26 de mayo de 2026  
**Estado:** Borrador (Bloque 1)  
**Programa:** Análisis y Desarrollo de Software (ADSO) - SENA  

---

## Introducción.

El presente documento describe los requisitos del Sistema de Gestión y Punto de Venta (POS) SaaS Multi-Tenant "Gestión Neiva", el cual tiene como finalidad optimizar los procesos de administración de inventarios, registro de ventas, control de alertas (vencimiento y stock) y cálculo de utilidades financieras en micro-negocios y tiendas de barrio en la ciudad de Neiva, garantizando eficiencia, control y facilidad de adopción para usuarios no técnicos.
Este documento servirá como base para el diseño, desarrollo, implementación y validación del software.

## Planteamiento del problema.

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

## Propósito.

El propósito de este documento es:
* Definir de manera clara y estructurada los requisitos del sistema.
* Establecer el alcance funcional del software.
* Servir como guía para desarrolladores, diseñadores y stakeholders.
* Reducir ambigüedades durante el desarrollo.
* Facilitar la validación y aceptación del sistema ante el SENA.

## Justificación.

La implementación de un sistema especializado para micro-negocios y tiendas de barrio permitirá:
* Automatizar el control de existencias en tiempo real mediante el registro de ventas.
* Reducir pérdidas financieras mediante alertas automatizadas de vencimiento de productos (límite de 15 días).
* Facilitar el registro ágil de productos utilizando escáner de códigos de barras mediante la cámara de dispositivos móviles.
* Generar reportes financieros de ventas y utilidad neta en tiempo real.
* Aumentar la resiliencia del negocio ante problemas de conectividad mediante una interfaz optimizada para bajo consumo de datos móviles.
* Proveer una arquitectura multi-inquilino (multi-tenant) que reduzca los costos de alojamiento de datos para los usuarios finales.

Además, el sistema permitirá una administración moderna, ágil y trazable sin requerir hardware costoso de gran escala.

## Objetivo General.

Desarrollar un sistema de gestión y punto de venta (POS) SaaS Multi-Tenant optimizado para dispositivos móviles que permita administrar de manera eficiente las ventas, el inventario, las alertas de vencimiento y los informes financieros de micro-negocios en la ciudad de Neiva.

## Objetivos específicos.

* Diseñar un módulo multi-inquilino (multi-tenant) para el aislamiento y protección segura de los datos de cada comercio.
* Implementar un módulo de inventario simplificado con soporte para productos por unidad y a granel (fraccionamiento por peso).
* Desarrollar un sistema de ventas rápido (POS) con integración de escáner de códigos de barras a través de la cámara del celular.
* Implementar un módulo de alertas automáticas para stock mínimo y control de fechas de vencimiento de mercancía.
* Diseñar un panel de control (Dashboard) con gráficas de rendimiento financiero que calcule ingresos y utilidad diaria real.
* Habilitar la exportación del historial de transacciones e informes a formatos de hoja de cálculo (Excel).
* Implementar control de accesos basado en roles (Administrador/Tendero y Cajero/Ayudante).

## Alcance.

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

## Personal involucrado.

| Nombre | Rol | Categoría Profesional | Responsabilidad | Información de contacto |
|--------|-----|-----------------------|-----------------|-------------------------|
| [Nombre del Instructor] | Instructor | Ingeniero en sistemas | Supervisión técnica | correoinstructor@sena.edu.co |
| Tomás [Apellido] | Analista / Desarrollador | Aprendiz del tecnólogo en ADSO | Análisis de información, diseño, programación y despliegue | correoaprendiz1@gmail.com |
| [Nombre del Compañero] | Desarrollador | Aprendiz del tecnólogo en ADSO | Programación, pruebas y documentación | correoaprendiz2@gmail.com |

| Rol | Responsabilidad |
|-----|-----------------|
| Product Owner (Tenderos) | Definir requerimientos del negocio y prioridades de usabilidad. |
| Administrador (Dueño de tienda) | Registrar productos, compras, configurar alertas y validar la utilidad financiera. |
| Cajero / Ayudante | Registrar transacciones diarias en el POS y consultar disponibilidad física. |
| Desarrollador Backend | Implementar la lógica del servidor, base de datos relacional y aislamiento de datos por tenant. |
| Desarrollador Frontend | Implementar la interfaz responsiva, el flujo del carrito de compras y la integración del escáner. |
| QA Tester | Validar el funcionamiento global, el control de accesos por roles y la precisión matemática de los reportes. |

## Definiciones, acrónimos y abreviaturas.

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

## Referencias.

| Título del Documento | Referencia |
|----------------------|------------|
| Standard IEEE 830 - 1998 | IEEE (Prácticas recomendadas para especificación de requisitos). |
| Repositorio del Proyecto | Código fuente funcional (app/main.py, models.py, frontend/src). |

## Resumen.

Este documento define los requisitos iniciales para el desarrollo del Sistema de Gestión y Punto de Venta (POS) SaaS Multi-Tenant "Gestión Neiva", el cual busca centralizar, simplificar y automatizar los procesos de administración de inventarios y registro de ventas para micro-negocios en Neiva. El sistema garantiza la resiliencia en conexiones de red móvil, alertas tempranas de pérdida de stock o vencimiento y cálculo automático de utilidades diarias sin requerir hardware costoso, promoviendo una gestión moderna, accesible y 100% digital para los tenderos.
