# 🎭 Rapsodia


![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-Framework-092E20?style=for-the-badge&logo=django&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

> **Rapsodia** es una aplicación web diseñada para la gestión y reserva de mesas en restaurantes. El sistema está enfocado en dos tipos de usuarios:
> **Clientes:** Les permite registrarse e iniciar sesión, consultar la disponibilidad de mesas en tiempo real según la fecha, hora y cantidad de personas, realizar reservas que bloquean la mesa por 3 horas, modificar o cancelar sus reservas, recibir confirmaciones por correo electrónico y revisar su historial de reservas.
> **Administradores:** Les ofrece un panel de control (dashboard) para visualizar todas las reservas y métricas del restaurante, filtrar estadísticas por semana o mes con gráficas de consumo, y monitorear en tiempo real el estado de las mesas (libres, ocupadas o reservadas) mediante un mapa interactivo. 

---

## Características Destacadas

1. Funcionalidades para el Cliente
   - Consulta de Disponibilidad en Tiempo Real: Filtra mesas por fecha, hora elegida y número de comensales (respetando la capacidad máxima de cada mesa).
   - Control Inteligente de Horarios: Al confirmar una reserva, el sistema bloquea automáticamente la mesa seleccionada por un bloque de 3 horas (180 minutos), evitando cruces de horarios o sobre-reservas.
   - Gestión Flexible de Reservas: Permite realizar, modificar o cancelar la cita siempre que se haga con una antelación mínima de 24 horas.
   - Notificaciones por Correo Estilizado: Envía un correo electrónico en formato HTML con la identidad corporativa del restaurante, detallando los datos de la reserva e incluyendo un botón directo para gestionar o cancelar la cita.
   - Historial Completo: Panel donde el cliente puede revisar sus reservas pasadas, activas y canceladas, con la opción de limpiar el historial de reservas canceladas.
2. Módulo de Administración (Dashboard)
   - Mapa Interactivo de Mesas en Tiempo Real: Representación visual del plano del restaurante que indica de forma dinámica el estado actual de cada mesa: Libre, Ocupada o Reservada.
   - Métricas y Métodos de Filtrado: Tablero de control con métricas globales sobre el total de reservas (activas, canceladas y pasadas).
   - Gráficas de Rendimiento por Tiempo: Gráficos estadísticos que permiten visualizar la afluencia de reservas comparando periodos por semana (últimos 7 días) o por mes (últimos 30 días), así como la distribución según el día de la semana.
3. Aspectos Técnicos Destacados
   - Arquitectura Decoplada: Backend robusto en Django REST Framework integrado con un Frontend dinámico en ReactJS y PostgreSQL como motor de datos.
   - Calidad Garantizada (TDD & CI/CD): Cobertura mediante pruebas unitarias, de integración y end-to-end (E2E), respaldado con canal de integración continua en GitHub.
   - Pruebas de Carga y Rendimiento: Evaluación de capacidad de respuesta con simulaciones de hasta 100 usuarios concurrentes (vía Locust), asegurando respuestas rápidas en el 95% de las solicitudes.

---

## Stack Tecnológico

- **Backend:** Python / Django (Patrón MVT)
- **Frontend:** HTML5, CSS3, JavaScript Vanilla
- **Base de Datos:** SQLite / PostgreSQL
- **Media:** Gestión de archivos estáticos y multimedia con Django

---

## Guía de Instalación Rápida

1. **Clonar el proyecto:**
   ```bash
   git clone [https://github.com/JGMoony/Rapsodia.git](https://github.com/JGMoony/Rapsodia.git)
   cd Rapsodia
