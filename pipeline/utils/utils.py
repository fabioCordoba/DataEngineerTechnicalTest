from datetime import datetime
import logging
import time
from google.cloud import bigquery
import pandas as pd
from flask import jsonify, abort


class Utils:

    # Función para eliminar outliers por IQR
    def eliminar_outliers(self, dfx, columna):
        dfx[columna] = pd.to_numeric(dfx[columna], errors="coerce")
        dfx = dfx.dropna(subset=[columna])
        Q1 = dfx[columna].quantile(0.25)
        Q3 = dfx[columna].quantile(0.75)
        IQR = Q3 - Q1
        limite_inferior = Q1 - 1.5 * IQR
        limite_superior = Q3 + 1.5 * IQR
        return dfx[
            (dfx[columna] >= limite_inferior) & (dfx[columna] <= limite_superior)
        ]

    def extract_data(self):
        try:
            logging.info("Inicializando cliente de BigQuery...")
            client = bigquery.Client()

            query = """
                SELECT * 
                FROM `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2022`
                WHERE EXTRACT(YEAR FROM pickup_datetime) = 2022
                LIMIT 10000
            """

            logging.info("Ejecutando consulta SQL...")
            df = client.query(query).to_dataframe()
            logging.info(f"Consulta completada. Registros cargados: {len(df)}")

            return df

        except Exception as e:
            logging.error("Ocurrió un error durante la ejecución de la consulta")
            abort(404, description="No se encontró el recurso solicitado")

    def trusted_method(self, df_raw):
        try:
            logging.info("Iniciando validacion de registros...")
            df_trus = df_raw
            # Asegurarse de que las columnas sean tipo datetime
            df_trus["pickup_datetime"] = pd.to_datetime(df_trus["pickup_datetime"])
            df_trus["dropoff_datetime"] = pd.to_datetime(df_trus["dropoff_datetime"])

            # Verificar que todos los registros tengan pickup < dropoff
            condicion = df_trus["pickup_datetime"] < df_trus["dropoff_datetime"]

            logging.info("Ejecutando validacon...")
            # Mostrar resultados inválidos (si los hay)
            registros_invalidos = df_trus[~condicion]
            logging.info(f"Número de registros inválidos: {len(registros_invalidos)}")

            # Elimnar resultados invalidos
            logging.info("Elimnando resultados invalidos...")
            df_trus = df_trus[df_trus["pickup_datetime"] < df_trus["dropoff_datetime"]]
            # df_trus.set_index('vendor_id', inplace=True)

            # Verificar que trip_distance y fare_amount sean mayores a cero
            condicion_valida = (df_trus["trip_distance"] > 0) & (
                df_trus["fare_amount"] > 0
            )
            registros_invalidos = df_trus[~condicion_valida]
            logging.info(f"Número de registros inválidos: {len(registros_invalidos)}")

            # Eliminar los registros invalidos
            logging.info("Elimnando resultados invalidos...")
            df_trus = df_trus[
                (df_trus["trip_distance"] > 0) & (df_trus["fare_amount"] > 0)
            ]

            logging.info("Eliminando outliers")
            # Aplicar sobre columnas relevantes
            df_trus = self.eliminar_outliers(df_trus, "trip_distance")
            df_trus = self.eliminar_outliers(df_trus, "fare_amount")

            logging.info("Eliminando filas con valores nulos...")
            # Eliminar filas con valores nulos
            df_trus = df_trus.dropna(
                subset=[
                    "pickup_datetime",
                    "dropoff_datetime",
                    "trip_distance",
                    "fare_amount",
                ]
            )

            logging.info("Asignando valores por defecto...")
            # Asignar valores por defecto
            df_trus["passenger_count"] = df_trus["passenger_count"].fillna(1)

            logging.info("Quitar outliers extremos...")
            # Quitar outliers extremos
            df_trus = df_trus[
                (df_trus["trip_distance"] < 100) & (df_trus["fare_amount"] < 500)
            ]

            # Diccionario de nombres equivalentes
            column_rename_map = {
                "tpep_pickup_datetime": "pickup_datetime",
                "tpep_dropoff_datetime": "dropoff_datetime",
                "trip_distance": "trip_distance",
            }
            logging.info("Renombrar las columnas presentes...")
            # Renombrar las columnas presentes
            df_trus = df_trus.rename(
                columns={
                    k: v for k, v in column_rename_map.items() if k in df_trus.columns
                }
            )

            # Convertir columnas datetime
            df_trus["pickup_datetime"] = pd.to_datetime(
                df_trus["pickup_datetime"], errors="coerce"
            )
            df_trus["dropoff_datetime"] = pd.to_datetime(
                df_trus["dropoff_datetime"], errors="coerce"
            )

            # Asegurar que trip_distance sea float
            df_trus["trip_distance"] = pd.to_numeric(
                df_trus["trip_distance"], errors="coerce"
            )

            logging.info("Eliminando filas con datos importantes faltantes...")
            df_trus = df_trus.dropna(
                subset=["pickup_datetime", "dropoff_datetime", "trip_distance"]
            )

            df_trus = self.join_table(df_trus)

            return df_trus
        except Exception as e:
            logging.error(
                "Ocurrió un error durante la ejecución de la consulta", exc_info=True
            )

    def join_table(self, df_trus):
        try:
            # Dataset de copia
            df_trips = df_trus

            logging.info("Cargando Dataset de zonas (Taxi Zone Lookup Table)...")
            df_zones = pd.read_csv("utils/taxi_zone_lookup.csv")

            logging.info("Formateando el valor de las variables a entero...")
            df_trips["pickup_location_id"] = df_trips["pickup_location_id"].astype(int)
            df_zones["LocationID"] = df_zones["LocationID"].astype(int)

            logging.info("Realizar join con la tabla de Taxi Zone Unión Lookup...")
            df_trips = df_trips.merge(
                df_zones,
                how="left",
                left_on="pickup_location_id",
                right_on="LocationID",
            )
            return df_trips
        except Exception as e:
            logging.error(
                "Ocurrió un error durante la ejecución de la consulta", exc_info=True
            )

    # Defnicon de franjas horarias
    def clasificar_franja_horaria(self, hora):
        if 6 <= hora < 10:
            return "Mañana (Pico)"
        elif 10 <= hora < 16:
            return "Mediodía (Valle)"
        elif 16 <= hora < 20:
            return "Tarde (Pico)"
        elif 20 <= hora < 24:
            return "Noche (Valle)"
        else:
            return "Madrugada"

    def refined_method(self, df_trips):
        try:
            logging.info("Creando columnas derivadas...")
            df_ref = df_trips
            df_ref["hour"] = df_ref["pickup_datetime"].dt.hour
            df_ref["day_of_week"] = df_ref["pickup_datetime"].dt.day_name()
            df_ref["trip_duration"] = (
                df_ref["dropoff_datetime"] - df_ref["pickup_datetime"]
            ).dt.total_seconds() / 60

            logging.info("Clasificacion por franja horara...")
            df_ref["franja_horaria"] = df_ref["hour"].apply(
                self.clasificar_franja_horaria
            )

            return df_ref
        except Exception as e:
            logging.error(
                "Ocurrió un error durante la ejecución de la consulta", exc_info=True
            )

    def refined_resum(self, df_ref):
        try:
            logging.info("Resumen estadisticas KPIs por día y franja horaria")
            resumen = (
                df_ref.groupby(["day_of_week", "franja_horaria"])
                .agg(
                    cantidad_viajes=("pickup_datetime", "count"),
                    duracion_promedio_min=("trip_duration", "mean"),
                    tarifa_promedio_usd=("fare_amount", "mean"),
                )
                .reset_index()
            )

            return resumen
        except Exception as e:
            logging.error(
                "Ocurrió un error durante la ejecución de la consulta", exc_info=True
            )

    def refined_efficiency(self, df_ref):
        # Analizar la eficiencia operativa y económica por zona o borough.
        try:
            logging.info("Crear columna de duración en minutos y horas...")
            df_ref["trip_duration_min"] = (
                df_ref["dropoff_datetime"] - df_ref["pickup_datetime"]
            ).dt.total_seconds() / 60
            df_ref["trip_duration_hr"] = df_ref["trip_duration_min"] / 60

            logging.info("Filtrar datos inválidos...")
            df_valid = df_ref[
                (df_ref["trip_distance"] > 0)
                & (df_ref["fare_amount"] > 0)
                & (
                    df_ref["trip_duration_min"] > 1
                )  # evitar viajes extremadamente cortos o erróneos
            ]

            logging.info("Crear columnas de KPIs...")
            df_valid["fare_per_mile"] = (
                df_valid["fare_amount"] / df_valid["trip_distance"]
            )
            df_valid["fare_per_min"] = (
                df_valid["fare_amount"] / df_valid["trip_duration_min"]
            )
            df_valid["speed_mph"] = (
                df_valid["trip_distance"] / df_valid["trip_duration_hr"]
            )

            logging.info("Agrupando por zona y calcular promedios...")
            kpis_por_zona = (
                df_valid.groupby(["Zone", "Borough"])
                .agg(
                    cantidad_viajes=("fare_amount", "count"),
                    ingreso_promedio_milla=("fare_per_mile", "mean"),
                    ingreso_promedio_minuto=("fare_per_min", "mean"),
                    velocidad_promedio_mph=("speed_mph", "mean"),
                )
                .reset_index()
            )

            logging.info("Ranking de zonas más rentables...")
            kpis_por_zona["ranking_rentabilidad"] = kpis_por_zona[
                "ingreso_promedio_milla"
            ].rank(ascending=False)
            kpis_por_zona["ranking_eficiencia"] = kpis_por_zona[
                "velocidad_promedio_mph"
            ].rank(ascending=False)

            return kpis_por_zona
        except Exception as e:
            logging.error(
                "Ocurrió un error durante la ejecución de la consulta", exc_info=True
            )

    def top_ten_rentables(self, kpis_por_zona):
        try:
            logging.info("Top 10 zonas más rentables...")
            top_rentables = kpis_por_zona.sort_values(
                by="ingreso_promedio_milla", ascending=False
            ).head(10)
            top_rentables[
                ["Zone", "Borough", "ingreso_promedio_milla", "cantidad_viajes"]
            ]
            return top_rentables
        except Exception as e:
            logging.error(
                "Ocurrió un error durante la ejecución de la consulta", exc_info=True
            )

    def data_quality_impact(self, df_init, df_ref):
        try:
            logging.info("Total de registros iniciales...")
            total_registros_raw = df_init.shape[0]
            ingreso_total_raw = df_init["fare_amount"].sum()

            logging.info("Total de Registros finales...")
            total_registros_limpios = df_ref.shape[0]
            ingreso_total_limpio = df_ref["fare_amount"].sum()

            logging.info("Cálculando de métricas...")
            registros_descartados = total_registros_raw - total_registros_limpios
            porcentaje_descartados = registros_descartados / total_registros_raw * 100
            impacto_ingresos = (
                (float(ingreso_total_raw) - float(ingreso_total_limpio))
                / float(ingreso_total_raw)
                * 100
            )

            data = {
                "total_registros_raw": total_registros_raw,
                "ingreso_total_limpio": ingreso_total_limpio,
                "registros_descartados": registros_descartados,
                "registros_descartados_por": f"{porcentaje_descartados:.2f}%",
                "ingreso_bruto": float(ingreso_total_raw),
                "ingreso_neto": ingreso_total_limpio,
                "impacto_ingresos": impacto_ingresos,
            }

            logging.info("Mostrar resultados...")
            logging.info(f"Total de registros iniciales: {total_registros_raw}")
            logging.info(f"Total de registros finale: {ingreso_total_limpio}")
            logging.info(
                f"Registros descartados: {registros_descartados} ({porcentaje_descartados:.2f}%)"
            )
            logging.info(f"Ingreso bruto (raw): ${ingreso_total_raw:,.2f}")
            logging.info(f"Ingreso neto (limpio): ${ingreso_total_limpio:,.2f}")
            logging.info(f"Impacto en ingresos por limpieza: -{impacto_ingresos:.2f}%")

            return data

        except Exception as e:
            logging.error(
                "Ocurrió un error durante la ejecución de la consulta", exc_info=True
            )

    def report_general(self, data_quality_impact, tiempos, kpis_por_zona):
        try:
            reporte = {
                "fecha_ejecucion": datetime.now().isoformat(),
                "registros": {
                    "total_procesados": data_quality_impact["total_registros_raw"],
                    "descartados": data_quality_impact["registros_descartados"],
                    "ingreso_bruto": data_quality_impact["ingreso_bruto"],
                    "ingreso_neto": data_quality_impact["ingreso_neto"],
                    "corregidos": data_quality_impact["ingreso_total_limpio"],
                    "Impacto_ingresos_limpieza": data_quality_impact[
                        "impacto_ingresos"
                    ],  # %
                },
                "tiempos": tiempos,
                "KPIs": {
                    "ingreso_promedio_por_milla": kpis_por_zona[
                        "ingreso_promedio_milla"
                    ].mean(),
                    "ingreso_promedio_por_minuto": kpis_por_zona[
                        "ingreso_promedio_minuto"
                    ].mean(),
                    "velocidad_promedio_kmph": kpis_por_zona[
                        "velocidad_promedio_mph"
                    ].mean(),
                },
            }

            return reporte

            logging.info("Reporte generado: execution_report.json")
        except Exception as e:
            logging.error(
                "Ocurrió un error durante la ejecución de la consulta", exc_info=True
            )
