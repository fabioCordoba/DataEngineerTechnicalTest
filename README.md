# 🚖 Proyecto de Procesamiento de Datos de Taxi Zones

Este proyecto carga, transforma y une datasets de viajes de taxi con la tabla de zonas de la ciudad de Nueva York (Taxi Zone Lookup Table).  
Utiliza **Python**, **Flask** para servir respuestas HTTP y **Pandas** para la manipulación de datos.

En el cual econtraras un cuanderno jupiter con el codgo necesaro para el ejerccio Untitled-1.ipynb y junto encontraras un fichero llamado pipeline con la logica del servicio.

En este caso se opto por crear el pipelne y desplegarlo en el servco de gcloud, y as cualquier persona puee tener aceso a la informacon de este.

decidi tomar el dataset de Google BigQuery: El dataset bigquery-public-data.new_york_taxi_trips
que contiene datos equivalentes (https://console.cloud.google.com/marketplace/product/city-of-new-york/nyc-tlc-trips?hl=es-419).

---

## 📦 Instalación

1. **Clona el repositorio:**

```bash
git@github.com:fabioCordoba/DataEngineerTechnicalTest.git
cd tu_repositorio\pipeline
```

2. **Crea un entorno virtual:**

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. **Instala las dependencias:**

```bash
pip install -r requirements.txt
```

Asegúrate de tener Python 3.8+ instalado.

4. **Configura las credenciales de Google Cloud:**

Coloca tu archivo de credenciales en la raíz o en el directorio correspondiente, y asegúrate que en el código
`os.environ["GOOGLE_APPLICATION_CREDENTIALS"]` apunte a la ruta correcta.

## 🚀 Ejecución

Para correr la API localmente:

```bash
python main.py
```

La aplicación quedará disponible en:

```bash
http://127.0.0.1:8000
```

Puedes probar los endpoints usando Postman, Curl o directamente en el navegador.

Para correr la API localmente usando Docker:

```bash
docker run -p 80:8000 fabiocordobadev/personal:taxi-pipelin
```

La aplicación quedará disponible en:

```bash
http://127.0.0.1:80
```

Puedes probar los endpoints usando Postman, Curl o directamente en el navegador.

## 🏛️ Arquitectura del Proyecto

```plaintext
├── main.py                 # Archivo principal de la aplicación Flask
├── utils/
│   ├── __init__.py         # Inicializador del módulo utils
│   ├── utils.py            # Funciones de utilidades como carga de datasets, validaciones
│   └── taxi_zone_lookup.csv # Dataset de zonas de taxi
├── requirements.txt        # Lista de dependencias Python
├── articulate-case-452516-d6-dc4fd1dda930.json # Credenciales (NO subir a producción)
└── README.md               # Este documento

```

`app.py:` Define las rutas de la API y gestiona la lógica principal.

`utils/:` Contiene funciones auxiliares para limpieza, carga y procesamiento de datos.

`requirements.txt:` Incluye todas las librerías necesarias (Flask, Pandas, Gunicorn, etc).

## ⚙️ Dependencias principales

- Flask: Para crear el servidor web

- Pandas: Para procesamiento de datos

- Google Cloud SDK: Si se conectan recursos de GCP

## 📋 Notas importantes

- Este proyecto carga datos desde archivos .csv. Asegúrate que la ruta del archivo sea correcta según tu estructura.
- Se recomienda usar Docker para facilitar el despliegue (en futuras versiones).
