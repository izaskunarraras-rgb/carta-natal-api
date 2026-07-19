from flask import Flask, request, jsonify, send_from_directory

from carta_natal_base import generar_carta_api
from luna_casa4_casa6 import generar_carta_api as generar_luna_api
from sol_asc_nodos import generar_carta_api as generar_sol_asc_nodos_api

import os


app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@app.route("/")
def home():
    return "API carta natal funcionando"


@app.route("/descargas/<path:nombre_archivo>")
def descargar_pdf(nombre_archivo):
    return send_from_directory(
        BASE_DIR,
        nombre_archivo,
        as_attachment=True
    )


@app.route("/generar-carta", methods=["POST"])
def generar_carta():
    datos = request.json or {}

    nombre = datos.get("nombre")
    fecha = datos.get("fecha")
    hora = datos.get("hora")
    lugar = datos.get("lugar")

    # Wix envía estos campos con estos nombres.
    lat = datos.get("latitud")
    lon = datos.get("longitud")
    tz_name = datos.get("tz_name")

    opciones = datos.get("opciones", [])

    print(
        "Datos recibidos:",
        nombre,
        fecha,
        hora,
        lugar,
        lat,
        lon,
        tz_name,
        opciones
    )

    if "opLuna" in opciones:
        print("Generando informe Luna")

        resultado = generar_luna_api(
            nombre,
            fecha,
            hora,
            lugar,
            lat=lat,
            lon=lon,
            tz_name=tz_name
        )

    elif "opSolAscNodos" in opciones:
        print("Generando informe Sol · Ascendente · Nodos")

        resultado = generar_sol_asc_nodos_api(
            nombre,
            fecha,
            hora,
            lugar,
            lat=lat,
            lon=lon,
            tz_name=tz_name
        )

    else:
        print("Generando Carta Base")

        resultado = generar_carta_api(
            nombre,
            fecha,
            hora,
            lugar,
            lat=lat,
            lon=lon,
            tz_name=tz_name
        )

    return jsonify(resultado)


if __name__ == "__main__":
    app.run(debug=True)