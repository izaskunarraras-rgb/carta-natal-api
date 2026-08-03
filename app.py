from flask import Flask, request, jsonify, send_from_directory

from carta_natal_base import generar_carta_api
from luna_casa4_casa6 import generar_carta_api as generar_luna_api
from sol_asc_nodos import generar_carta_api as generar_sol_asc_nodos_api
from planetas_personales import (
    generar_carta_api as generar_planetas_personales_api
)
from planetas_sociales import (
    generar_carta_api as generar_planetas_sociales_api
)
from planetas_transpersonales import (
    generar_carta_api as generar_planetas_transpersonales_api
)
from casas_por_signo import (
    generar_carta_api as generar_casas_por_signo_api
)

from pypdf import PdfWriter

import os
import re
import time
import unicodedata


app = Flask(__name__)

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


# ───────────────────── CONFIGURACIÓN ─────────────────────

INDIVIDUALES = [
    "opLuna",
    "opSolAscNodos",
    "opPersonales",
    "opSociales",
    "opTranspersonales",
    "opCasas"
]


OPCIONES_VALIDAS = [
    "opCartaBase",
    "opMapaCompleto",
    *INDIVIDUALES
]


TIPOS_PEDIDO_VALIDOS = [
    "carta_base",
    "informe_individual",
    "varios_informes",
    "mapa_completo"
]


# Orden editorial de los documentos.
GENERADORES = {
    "opCartaBase": {
        "nombre": "Carta Base",
        "generador": generar_carta_api
    },

    "opLuna": {
        "nombre": "Luna · Casa 4 · Casa 6",
        "generador": generar_luna_api
    },

    "opSolAscNodos": {
        "nombre": "Sol · Ascendente · Nodos",
        "generador": generar_sol_asc_nodos_api
    },

    "opPersonales": {
        "nombre": "Planetas Personales",
        "generador": generar_planetas_personales_api
    },

    "opSociales": {
        "nombre": "Planetas Sociales",
        "generador": generar_planetas_sociales_api
    },

    "opTranspersonales": {
        "nombre": "Planetas Transpersonales",
        "generador": generar_planetas_transpersonales_api
    },

    "opCasas": {
        "nombre": "Casas por Signo",
        "generador": generar_casas_por_signo_api
    }
}


# El Mapa Completo es un producto independiente.
# Internamente reúne la Carta Base y los seis cuadernos.
OPCIONES_MAPA_COMPLETO = [
    "opCartaBase",
    "opLuna",
    "opSolAscNodos",
    "opPersonales",
    "opSociales",
    "opTranspersonales",
    "opCasas"
]


# ───────────────────── RUTAS ─────────────────────

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


# ───────────────────── FUNCIONES AUXILIARES ─────────────────────

def limpiar_nombre_archivo(texto):
    """
    Convierte un nombre en una cadena segura para archivos.
    """

    texto = str(texto or "arquitectura_interna")

    texto = unicodedata.normalize(
        "NFKD",
        texto
    )

    texto = texto.encode(
        "ascii",
        "ignore"
    ).decode("ascii")

    texto = texto.lower()

    texto = re.sub(
        r"[^a-z0-9]+",
        "_",
        texto
    )

    texto = texto.strip("_")

    return texto or "arquitectura_interna"


def obtener_tipo_pedido(opciones):
    """
    Determina el tipo de pedido a partir de las opciones.
    """

    incluye_mapa_completo = (
        "opMapaCompleto" in opciones
    )

    individuales_seleccionados = [
        opcion
        for opcion in opciones
        if opcion in INDIVIDUALES
    ]

    if incluye_mapa_completo:
        return "mapa_completo"

    if len(individuales_seleccionados) >= 2:
        return "varios_informes"

    if len(individuales_seleccionados) == 1:
        return "informe_individual"

    if "opCartaBase" in opciones:
        return "carta_base"

    return "desconocido"


def obtener_ruta_pdf(resultado):
    """
    Extrae la ruta del PDF devuelta por cualquiera
    de los generadores actuales.

    Admite rutas locales o URL de descarga.
    """

    if not isinstance(resultado, dict):
        raise ValueError(
            "El generador no ha devuelto un resultado válido."
        )

    if resultado.get("ok") is False:
        raise ValueError(
            resultado.get("error") or
            "El generador ha devuelto un error."
        )

    posibles_claves = [
        "ruta_pdf",
        "pdf_path",
        "archivo",
        "pdf",
        "pdf_url",
        "url"
    ]

    valor_pdf = None

    for clave in posibles_claves:
        if resultado.get(clave):
            valor_pdf = resultado[clave]
            break

    if not valor_pdf:
        raise ValueError(
            "El generador no ha devuelto la ruta del PDF."
        )

    valor_pdf = str(valor_pdf)


    # Si devuelve una URL o una ruta /descargas/archivo.pdf,
    # utilizamos únicamente el nombre del archivo.
    if "/descargas/" in valor_pdf:
        nombre_archivo = valor_pdf.split(
            "/descargas/"
        )[-1]

        ruta_pdf = os.path.join(
            BASE_DIR,
            nombre_archivo
        )

    elif valor_pdf.startswith("http"):
        nombre_archivo = valor_pdf.rstrip(
            "/"
        ).split("/")[-1]

        ruta_pdf = os.path.join(
            BASE_DIR,
            nombre_archivo
        )

    elif os.path.isabs(valor_pdf):
        ruta_pdf = valor_pdf

    else:
        ruta_pdf = os.path.join(
            BASE_DIR,
            valor_pdf
        )


    ruta_pdf = os.path.abspath(
        ruta_pdf
    )


    if not os.path.isfile(ruta_pdf):
        raise FileNotFoundError(
            f"No se ha encontrado el PDF generado: {ruta_pdf}"
        )

    return ruta_pdf


def generar_documento(
    opcion,
    nombre,
    fecha,
    hora,
    lugar,
    lat,
    lon,
    tz_name
):
    """
    Ejecuta el generador correspondiente a una opción
    y devuelve la ruta local del PDF.
    """

    configuracion = GENERADORES.get(
        opcion
    )

    if not configuracion:
        raise ValueError(
            f"No existe un generador para la opción {opcion}."
        )

    print(
        f"Generando: {configuracion['nombre']}"
    )

    generador = configuracion[
        "generador"
    ]

    resultado = generador(
        nombre,
        fecha,
        hora,
        lugar,
        lat=lat,
        lon=lon,
        tz_name=tz_name
    )

    print(
        f"Resultado de {opcion}:",
        resultado
    )

    return obtener_ruta_pdf(
        resultado
    )


def unir_pdfs(
    rutas_pdf,
    nombre_archivo
):
    """
    Une varios PDFs en un único archivo.
    """

    if not rutas_pdf:
        raise ValueError(
            "No hay documentos para unir."
        )

    ruta_salida = os.path.join(
        BASE_DIR,
        nombre_archivo
    )

    writer = PdfWriter()

    try:
        for ruta_pdf in rutas_pdf:
            writer.append(
                ruta_pdf
            )

        with open(
            ruta_salida,
            "wb"
        ) as archivo_salida:
            writer.write(
                archivo_salida
            )

    finally:
        writer.close()

    if not os.path.isfile(ruta_salida):
        raise FileNotFoundError(
            "No se ha creado el PDF conjunto."
        )

    return ruta_salida


def crear_respuesta_pdf(
    ruta_pdf,
    tipo_pedido,
    opciones_generadas
):
    """
    Crea la respuesta común para Wix.
    """

    nombre_archivo = os.path.basename(
        ruta_pdf
    )

    url_pdf = (
        f"/descargas/{nombre_archivo}"
    )

    return {
        "ok": True,
        "pdf": url_pdf,
        "pdf_url": url_pdf,
        "url": url_pdf,
        "tipoPedido": tipo_pedido,
        "opcionesGeneradas": opciones_generadas
    }


# ───────────────────── GENERAR CARTA ─────────────────────

@app.route(
    "/generar-carta",
    methods=["POST"]
)
def generar_carta():
    try:
        datos = request.get_json(
            silent=True
        ) or {}

        nombre = datos.get(
            "nombre"
        )

        fecha = datos.get(
            "fecha"
        )

        hora = datos.get(
            "hora"
        )

        lugar = datos.get(
            "lugar"
        )

        lat = datos.get(
            "latitud"
        )

        lon = datos.get(
            "longitud"
        )

        tz_name = datos.get(
            "tz_name"
        )

        opciones_recibidas = datos.get(
            "opciones",
            []
        )

        tipo_pedido_recibido = datos.get(
            "tipoPedido",
            ""
        )


        # ───── VALIDACIÓN DE DATOS ─────────────────────

        if not nombre:
            return jsonify({
                "ok": False,
                "error": "Falta el nombre."
            }), 400

        if not fecha:
            return jsonify({
                "ok": False,
                "error": "Falta la fecha de nacimiento."
            }), 400

        if not hora:
            return jsonify({
                "ok": False,
                "error": "Falta la hora de nacimiento."
            }), 400

        if not lugar:
            return jsonify({
                "ok": False,
                "error": "Falta el lugar de nacimiento."
            }), 400

        if lat is None or lon is None:
            return jsonify({
                "ok": False,
                "error":
                    "Faltan las coordenadas del lugar de nacimiento."
            }), 400

        if not isinstance(
            opciones_recibidas,
            list
        ):
            return jsonify({
                "ok": False,
                "error":
                    "El formato de las opciones no es válido."
            }), 400


        opciones = []

        for opcion in opciones_recibidas:
            if (
                opcion in OPCIONES_VALIDAS and
                opcion not in opciones
            ):
                opciones.append(
                    opcion
                )


        if not opciones:
            return jsonify({
                "ok": False,
                "error":
                    "No se ha seleccionado ningún informe."
            }), 400


        # ───── VALIDAR MAPA COMPLETO ───────────────────

        incluye_mapa_completo = (
            "opMapaCompleto" in opciones
        )

        individuales_seleccionados = [
            opcion
            for opcion in opciones
            if opcion in INDIVIDUALES
        ]


        if (
            incluye_mapa_completo and
            individuales_seleccionados
        ):
            return jsonify({
                "ok": False,
                "error":
                    "El Mapa Completo no puede combinarse con informes individuales."
            }), 400


        # ───── TIPO DE PEDIDO ──────────────────────────

        tipo_calculado = obtener_tipo_pedido(
            opciones
        )

        if (
            tipo_pedido_recibido
            in TIPOS_PEDIDO_VALIDOS
        ):
            tipo_pedido = (
                tipo_pedido_recibido
            )
        else:
            tipo_pedido = (
                tipo_calculado
            )


        if tipo_pedido != tipo_calculado:
            print(
                "Tipo recibido distinto del calculado:",
                tipo_pedido_recibido,
                tipo_calculado
            )

            tipo_pedido = tipo_calculado


        if tipo_pedido == "desconocido":
            return jsonify({
                "ok": False,
                "error":
                    "No se ha podido identificar el tipo de pedido."
            }), 400


        print(
            "Datos recibidos:",
            {
                "nombre": nombre,
                "fecha": fecha,
                "hora": hora,
                "lugar": lugar,
                "lat": lat,
                "lon": lon,
                "tz_name": tz_name,
                "opciones": opciones,
                "tipo_pedido": tipo_pedido
            }
        )


        # ───── MAPA COMPLETO ───────────────────────────

        if tipo_pedido == "mapa_completo":
            opciones_a_generar = (
                OPCIONES_MAPA_COMPLETO
            )


        # ───── VARIOS INFORMES ─────────────────────────

        elif tipo_pedido == "varios_informes":
            opciones_a_generar = [
                opcion
                for opcion in GENERADORES
                if opcion in opciones
            ]


        # ───── INFORME INDIVIDUAL ──────────────────────

        elif tipo_pedido == "informe_individual":
            opciones_a_generar = [
                opcion
                for opcion in INDIVIDUALES
                if opcion in opciones
            ]


        # ───── CARTA BASE ──────────────────────────────

        else:
            opciones_a_generar = [
                "opCartaBase"
            ]


        if not opciones_a_generar:
            return jsonify({
                "ok": False,
                "error":
                    "No hay documentos válidos para generar."
            }), 400


        # ───── GENERAR DOCUMENTOS ──────────────────────

        rutas_generadas = []

        for opcion in opciones_a_generar:
            ruta_pdf = generar_documento(
                opcion=opcion,
                nombre=nombre,
                fecha=fecha,
                hora=hora,
                lugar=lugar,
                lat=lat,
                lon=lon,
                tz_name=tz_name
            )

            rutas_generadas.append(
                ruta_pdf
            )


        # ───── UN SOLO DOCUMENTO ───────────────────────

        if len(rutas_generadas) == 1:
            return jsonify(
                crear_respuesta_pdf(
                    ruta_pdf=rutas_generadas[0],
                    tipo_pedido=tipo_pedido,
                    opciones_generadas=opciones_a_generar
                )
            )


        # ───── UNIR VARIOS DOCUMENTOS ──────────────────

        nombre_seguro = limpiar_nombre_archivo(
            nombre
        )

        marca_tiempo = int(
            time.time()
        )


        if tipo_pedido == "mapa_completo":
            nombre_archivo = (
                f"mapa_completo_"
                f"{nombre_seguro}_"
                f"{marca_tiempo}.pdf"
            )

        else:
            nombre_archivo = (
                f"arquitectura_interna_"
                f"{nombre_seguro}_"
                f"{marca_tiempo}.pdf"
            )


        ruta_unida = unir_pdfs(
            rutas_pdf=rutas_generadas,
            nombre_archivo=nombre_archivo
        )


        return jsonify(
            crear_respuesta_pdf(
                ruta_pdf=ruta_unida,
                tipo_pedido=tipo_pedido,
                opciones_generadas=opciones_a_generar
            )
        )


    except Exception as error:
        print(
            "Error generando la carta:",
            repr(error)
        )

        return jsonify({
            "ok": False,
            "error": str(error)
        }), 500


if __name__ == "__main__":
    app.run(
        debug=True
    )