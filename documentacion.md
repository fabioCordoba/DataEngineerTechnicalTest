# Documentación Técnica: Decisiones, Reglas y Estrategias

## 1. Decisiones Técnicas

Esta pueba tecnica se desarrollo usando python como lenguaje de programacion, docker para despliegue a produccion, el dataset que se utlza para este proyecto se accede desde el servicio de Google BigQuery, utilizando una cuenta con capa gratuta de los servcos de google se creo un proyecto, en el cual se crea una cuenta de servcio la cual debe tener los permisos necesarios para trabajar con el agente de Google BigQuery luego se procede a crear un par de claves para poder acceder al recurso del dataset. estas claves son en formato json y deben usarse para poder tener acceso al dataset.

### 1.1 Elección de la arquitectura

La arquitectura seleccionada para este proyecto es una arquitectura de microservicios. Las razones principales para esta elección son:

- **Escalabilidad:** Los microservicios permiten escalar individualmente componentes de la aplicación según las necesidades.
- **Desarrollo Independiente:** Equipos independientes pueden trabajar en distintos servicios sin interferir entre sí.
- **Mantenimiento Simplificado:** Facilita la actualización de componentes sin afectar al sistema global.

### 1.2 Elección del stack tecnológico

El stack tecnológico elegido para el desarrollo incluye:

- **Backend:** Flask para servicios RESTful debido a su rendimiento y facilidad de integración.
- **Contenedores:** Docker para la contenedorización de servicios, garantizando un entorno coherente en desarrollo, pruebas y producción.

## 2. Reglas de Transformación

### 2.1 Transformación de datos

Durante el proceso de ingestión de datos, se deben aplicar las siguientes reglas de transformación:

- **Normalización de datos:** Se deben normalizar las entradas de datos antes de procesar para garantizar consistencia.
- **Validación de entradas:** Se deben validar los datos de entrada para evitar que datos incorrectos sean procesados.
- **Enriquecimiento de datos:** Si los datos provienen de múltiples fuentes, se enriquecerán con información adicional.

### 2.2 Estrategias de procesamiento

El procesamiento de datos se llevará a cabo de forma asincrónica

## 3. Estrategias de Observabilidad

### 3.1 Monitoreo de Aplicación

Para garantizar que el sistema esté funcionando correctamente, se implementarán las siguientes estrategias de monitoreo:

- **Métricas:** Cloud Run de google cloud ofrece la posblidad de monitorear y recopilará métricas clave como el tiempo de respuesta de las API, tasa de error, y uso de recursos (CPU, memoria).
- **Logs:** Cloud Run tambien se usa para la gestión y análisis de logs. Todos los servicios generarán logs estructurados que permitirán identificar rápidamente problemas.

## 4. Conclusión

Las decisiones técnicas tomadas para la realizacion de esta prueba tecnica buscan equilibrar eficiencia, escalabilidad y facilidad de mantenimiento, apoyándose en un stack tecnológico moderno como google cloud ya que ofrece herramientas de observabilidad para asegurar que el sistema sea robusto, fiable y fácilmente mantenible. Las reglas de transformación y las estrategias de monitoreo tratan de seguir los estandares comunmente usados para garantizarán que los datos sean procesados correctamente y que el rendimiento del sistema sea siempre monitoreado.
