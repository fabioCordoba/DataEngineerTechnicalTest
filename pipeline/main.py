from google.cloud import bigquery
from flask import Flask, jsonify, abort
import pandas as pd
import logging
import time
import os
import requests

from utils.utils import Utils

app = Flask(__name__)


@app.route("/")
def run():
    # Tiempos de ejecución por etapa
    start_time = time.time()
    try:
        utl = Utils()
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
            "articulate-case-452516-d6-dc4fd1dda930.json"
        )

        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )

        # Raw Layer

        extract_start = time.time()
        df = utl.extract_data()
        df_raw = df
        df_init = df
        extract_end = time.time()

        # Trusted Layer (Clean & Enrich)
        transform_start = time.time()
        df_trus = utl.trusted_method(df_raw)
        transform_end = time.time()

        # Refined Layer
        load_start = time.time()
        df_refined = utl.refined_method(df_trus)
        resumen = utl.refined_resum(df_refined)
        kpis_por_zona = utl.refined_efficiency(df_refined)
        top_ten_rent = utl.top_ten_rentables(kpis_por_zona)

        data_quality_impact = utl.data_quality_impact(df_init, df_refined)

        load_end = time.time()

        # Report
        tiempos = {
            "extract_seconds": round(extract_end - extract_start, 2),
            "transform_seconds": round(transform_end - transform_start, 2),
            "load_seconds": round(load_end - load_start, 2),
            "total_seconds": round(time.time() - start_time, 2),
        }

        data_report = utl.report_general(data_quality_impact, tiempos, kpis_por_zona)

        data = {
            "data": f"Consulta ejecutada correctamente. Total registros: {len(df)}",
            "df": len(df),
            "df_trus": len(df_trus),
            "data_quality_impact": data_quality_impact,
            "data_report": data_report,
        }
        return jsonify(data)

    except Exception as e:
        logging.error(
            "Ocurrió un error durante la ejecución de la consulta", exc_info=True
        )
        return jsonify({"error": "No se encontró el recurso solicitado"}), 404


if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 8000)), host="0.0.0.0", debug=True)
