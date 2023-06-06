<h1 align="center">
  <br>
  <a href=# name="readme-top">Proyecto Planner</a>
</h1>

<p align="center">
     <!-- Badges Here -->
</p>

<p align="center">
  <a href="#Descripción">Descripción</a> •
  <a href="#Uso">Uso</a> •
  <a href="#Contribuir">Contribuir</a> •
  <a href="#Equipo">Equipo</a> •
  <a href="#Licencia">Licencia</a>
</p>

<h4 align="center">
  <a href=# name="readme-top"><img src="./docs/img/demo_gif.gif" width="700px" alt="banner"></a>
</Es>

---

## Descripción

Este es el hogar para el desarrollo del nuevo Planner de Ingeniería UC, hecho por estudiantes para estudiantes.

Tras varios años en ideación, este proyecto se lanzó como [una propuesta conjunta](https://drive.google.com/file/d/1IxAJ8cCzDkayPwnju5kgc2oKc7g9fvwf/view) entre la Consejería Académica de Ingeniería y Open Source UC, con el propósito de reemplazar el [actual planner de Ingeniería](https://planner.ing.puc.cl/). La propuesta, tras ser aprobada por la Escuela de Ingeniería, dió comienzo al proyecto en modalidad de marcha blanca. A principios del 2023, y con un MVP listo, la Dirección de Pregrado oficialmente aprobó la continuación del desarrollo del proyecto.

## Uso

La forma óptima de correr el proyecto, sin tener que instalar todas las dependencias, es utilizar el devcontainer directo en VSCode, con acciones para correr el backend, frontend y servidor CAS mock. Existen tareas para reiniciar o migrar la base de datos y otras de utilidad.

### Pasos sugeridos

1. Teniendo Docker instalado, al abrir el proyecto en VSCode la extensión [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) debería reconocer la carpeta `.devcontainer` presente en el repo y aparece un _pop up_ entregando la opción de "Reabrir en el contenedor".
2. Espera a que se corra la tarea de inicio `just init`. Esto instala las depedencias y crea archivos como `.env` y `cas-mock-users.json`, que son necesarios para correr el proyecto.
   - El proyecto se integra con dos servicios externos: SIDING (para acceder a mallas y datos de estudiantes) y CAS (para el login UC). Ambos son configurables por medio de variables de entorno.
   - Se proveen mocks para ambos servicios en caso de no tener credenciales para acceder a ellos.
   - Para SIDING se provee un mock que se activa automáticamente en ausencia de credenciales.
   - Para CAS, se provee el servicio `cas-server-mock` que corre automáticamente junto a la app. Las cuentas de usuario disponibles son configurables en el archivo `data/cas-mock-users.json`.
3. Al correr el comando `Tasks: Run Task` en VSCode se abren una serie de tareas útiles como: instalar dependencias del backend, dependencias del frontend, crear migraciones en la db, reiniciar la db, etc.
4. En la sección "Run and Debug" de VSCode aparecerán acciones para correr cada servicio de la app por separado, o todos al mismo tiempo (`Launch all 🚀`).

<p align="right">(<a href="#readme-top">volver arriba</a>)</p>

## Contribuir

### Workflow

> El workflow es PR a development -> Revisar preview y checks -> Asignar reviewers -> Aprobación -> Merge a development

La información detallada sobre cómo contribuir se puede encontrar en [contributing.md](contributing.md).

### Bug Reports & Feature Requests

La app aún está en una etapa muy temprana del desarrollo por lo que podrían haber cosas que no funcionan correctamente o difieren de la documentación, por lo que cualquier lector siéntase libre a colaborar :rocket:. Toda ayuda es bienvenida :)

## Equipo

- [@shantifabri](https://github.com/shantifabri) - Coordinación / Frontend
- [@Diegothx](https://github.com/Diegothx) - Frontend
- [@negamartin](https://github.com/negamartin) - Backend
- [@fagiannoni](https://github.com/fagiannoni) - Backend
- [@agucova](https://github.com/agucova) - Apoyo Backend/Frontend

## Licencia

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](./license.md)

<p align="right">(<a href="#readme-top">volver arriba</a>)</p>
