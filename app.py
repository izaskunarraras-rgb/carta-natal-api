from flask import (
    Flask,
    jsonify,
    request,
    send_from_directory,
)

from pypdf import PdfWriter

import json
import os
import re
import requests
import subprocess
import sys
import time
import unicodedata
import uuid
import threading

from concurrent.futures import ThreadPoolExecutor


app = Flask(__name__)

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

def notificar_wix(datos):
    """
    Notifica a Wix el resultado final de la generación.

    Devuelve True si Wix confirma la recepción
    y False si no ha sido posible notificar.
    """

    url_callback = os.environ.get(
        "WIX_CALLBACK_URL"
    )

    secreto_callback = os.environ.get(
        "RENDER_CALLBACK_SECRET"
    )

    if not url_callback:
        print(
            "Falta la variable WIX_CALLBACK_URL.",
            flush=True,
        )

        return False

    if not secreto_callback:
        print(
            "Falta la variable RENDER_CALLBACK_SECRET.",
            flush=True,
        )

        return False

    try:
        respuesta = requests.post(
            url_callback,
            headers={
                "Content-Type": "application/json",
                "x-render-secret": secreto_callback,
            },
            json=datos,
            timeout=60,
        )

        print(
            "Respuesta del callback de Wix:",
            respuesta.status_code,
            respuesta.text,
            flush=True,
        )

        if not respuesta.ok:
            return False

        try:
            contenido = respuesta.json()

            return contenido.get("ok") is True

        except ValueError:
            return False

    except Exception as error:
        print(
            "Error notificando a Wix:",
            repr(error),
            flush=True,
        )

        return False

# ───────────────────── TRABAJOS EN SEGUNDO PLANO ─────────────────────

TRABAJOS = {}

BLOQUEO_TRABAJOS = threading.Lock()

EJECUTOR = ThreadPoolExecutor(
    max_workers=1
)


# ───────────────────── CONFIGURACIÓN ─────────────────────

INDIVIDUALES = [
    "opLuna",
    "opSolAscNodos",
    "opPersonales",
    "opSociales",
    "opTranspersonales",
    "opCasas",
]


OPCIONES_VALIDAS = [
    "opCartaBase",
    "opMapaCompleto",
    *INDIVIDUALES,
]


TIPOS_PEDIDO_VALIDOS = [
    "carta_base",
    "informe_individual",
    "varios_informes",
    "mapa_completo",
]


# Orden editorial y módulo Python de cada informe.
GENERADORES = {
    "opCartaBase": {
        "nombre": "Carta Base",
        "modulo": "carta_natal_base",
    },

    "opLuna": {
        "nombre": "Luna · Casa 4 · Casa 6",
        "modulo": "luna_casa4_casa6",
    },

    "opSolAscNodos": {
        "nombre": "Sol · Ascendente · Nodos",
        "modulo": "sol_asc_nodos",
    },

    "opPersonales": {
        "nombre": "Planetas Personales",
        "modulo": "planetas_personales",
    },

    "opSociales": {
        "nombre": "Planetas Sociales",
        "modulo": "planetas_sociales",
    },

    "opTranspersonales": {
        "nombre": "Planetas Transpersonales",
        "modulo": "planetas_transpersonales",
    },

    "opCasas": {
        "nombre": "Casas por Signo",
        "modulo": "casas_por_signo",
    },
}


ORDEN_EDITORIAL = [
    "opCartaBase",
    "opLuna",
    "opSolAscNodos",
    "opPersonales",
    "opSociales",
    "opTranspersonales",
    "opCasas",
]


# El Mapa Completo es un producto independiente.
# Internamente contiene la Carta Base y los seis cuadernos.
OPCIONES_MAPA_COMPLETO = [
    "opCartaBase",
    "opLuna",
    "opSolAscNodos",
    "opPersonales",
    "opSociales",
    "opTranspersonales",
    "opCasas",
]


# Marcador utilizado para localizar la respuesta JSON
# entre los mensajes impresos por cada generador.
MARCADOR_RESULTADO = "__RESULTADO_GENERADOR__"


# Tiempo máximo para generar un único cuaderno.
TIMEOUT_GENERADOR_SEGUNDOS = 360


# ───────────────────── RUTAS ─────────────────────

@app.route("/")
def home():
    return "API carta natal funcionando"


@app.route("/descargas/<path:nombre_archivo>")
def descargar_pdf(nombre_archivo):
    return send_from_directory(
        BASE_DIR,
        nombre_archivo,
        as_attachment=True,
    )


# ───────────────────── FUNCIONES AUXILIARES ─────────────────────

def limpiar_nombre_archivo(texto):
    """
    Convierte un nombre en una cadena segura para archivos.
    """

    texto = str(
        texto or "arquitectura_interna"
    )

    texto = unicodedata.normalize(
        "NFKD",
        texto,
    )

    texto = texto.encode(
        "ascii",
        "ignore",
    ).decode("ascii")

    texto = texto.lower()

    texto = re.sub(
        r"[^a-z0-9]+",
        "_",
        texto,
    )

    texto = texto.strip("_")

    return (
        texto
        or "arquitectura_interna"
    )


def obtener_tipo_pedido(opciones):
    """
    Determina el tipo de pedido a partir de las opciones.

    La Carta Base no cuenta como informe individual para
    decidir el tipo de correo o redirección.
    """

    if "opMapaCompleto" in opciones:
        return "mapa_completo"

    individuales_seleccionados = [
        opcion
        for opcion in opciones
        if opcion in INDIVIDUALES
    ]

    if len(individuales_seleccionados) >= 2:
        return "varios_informes"

    if len(individuales_seleccionados) == 1:
        return "informe_individual"

    if "opCartaBase" in opciones:
        return "carta_base"

    return "desconocido"


def obtener_opciones_a_generar(
    opciones,
    tipo_pedido,
):
    """
    Devuelve los documentos que deben generarse,
    respetando el orden editorial.
    """

    if tipo_pedido == "mapa_completo":
        return list(
            OPCIONES_MAPA_COMPLETO
        )

    return [
        opcion
        for opcion in ORDEN_EDITORIAL
        if opcion in opciones
    ]


def obtener_ruta_pdf(resultado):
    """
    Extrae la ruta local del PDF devuelta por un generador.
    """

    if not isinstance(resultado, dict):
        raise ValueError(
            "El generador no ha devuelto un resultado válido."
        )

    if resultado.get("ok") is not True:
        raise ValueError(
            resultado.get("error")
            or "El generador ha devuelto un error."
        )

    posibles_claves = [
        "ruta_pdf",
        "pdf_path",
        "archivo",
        "pdf",
        "pdf_url",
        "url",
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

    valor_pdf = str(
        valor_pdf
    )


    if "/descargas/" in valor_pdf:
        nombre_archivo = valor_pdf.split(
            "/descargas/"
        )[-1]

        ruta_pdf = os.path.join(
            BASE_DIR,
            nombre_archivo,
        )

    elif valor_pdf.startswith(
        ("http://", "https://")
    ):
        nombre_archivo = valor_pdf.rstrip(
            "/"
        ).split("/")[-1]

        ruta_pdf = os.path.join(
            BASE_DIR,
            nombre_archivo,
        )

    elif os.path.isabs(valor_pdf):
        ruta_pdf = valor_pdf

    else:
        ruta_pdf = os.path.join(
            BASE_DIR,
            valor_pdf,
        )


    ruta_pdf = os.path.abspath(
        ruta_pdf
    )


    if not os.path.isfile(ruta_pdf):
        raise FileNotFoundError(
            "No se ha encontrado el PDF generado: "
            f"{ruta_pdf}"
        )

    return ruta_pdf


def generar_documento_en_proceso(
    opcion,
    nombre,
    fecha,
    hora,
    lugar,
    lat,
    lon,
    tz_name,
):
    """
    Genera un informe en un proceso Python independiente.

    De esta forma, al terminar cada documento, el sistema
    operativo libera completamente la memoria utilizada por:

    - Matplotlib;
    - ReportLab;
    - los textos del módulo;
    - la carta calculada;
    - las imágenes;
    - las fuentes.
    """

    configuracion = GENERADORES.get(
        opcion
    )

    if not configuracion:
        raise ValueError(
            f"No existe generador para la opción {opcion}."
        )

    nombre_informe = configuracion[
        "nombre"
    ]

    modulo = configuracion[
        "modulo"
    ]

    print(
        f"Generando en proceso aislado: {nombre_informe}",
        flush=True,
    )


    datos_generador = {
        "nombre": nombre,
        "fecha": fecha,
        "hora": hora,
        "lugar": lugar,
        "lat": lat,
        "lon": lon,
        "tz_name": tz_name,
    }


    codigo_hijo = f"""
import importlib
import json
import traceback

MARCADOR = {MARCADOR_RESULTADO!r}

try:
    datos = json.loads(input())

    modulo = importlib.import_module(
        {modulo!r}
    )

    generador = getattr(
        modulo,
        "generar_carta_api"
    )

    resultado = generador(
        datos.get("nombre"),
        datos.get("fecha"),
        datos.get("hora"),
        datos.get("lugar"),
        lat=datos.get("lat"),
        lon=datos.get("lon"),
        tz_name=datos.get("tz_name"),
    )

except Exception as error:
    traceback.print_exc()

    resultado = {{
        "ok": False,
        "error": str(error),
    }}

print(
    MARCADOR + json.dumps(
        resultado,
        ensure_ascii=False,
    ),
    flush=True,
)
"""


    try:
        proceso = subprocess.run(
            [
                sys.executable,
                "-c",
                codigo_hijo,
            ],
            input=json.dumps(
                datos_generador,
                ensure_ascii=False,
            ) + "\n",
            text=True,
            capture_output=True,
            cwd=BASE_DIR,
            timeout=TIMEOUT_GENERADOR_SEGUNDOS,
            env={
                **os.environ,
                "MPLBACKEND": "Agg",
            },
        )

    except subprocess.TimeoutExpired as error:
        raise TimeoutError(
            f"La generación de {nombre_informe} "
            "ha superado el tiempo máximo permitido."
        ) from error


    if proceso.stdout:
        print(
            proceso.stdout,
            end="",
            flush=True,
        )

    if proceso.stderr:
        print(
            proceso.stderr,
            end="",
            flush=True,
        )


    if proceso.returncode != 0:
        raise RuntimeError(
            f"El proceso de {nombre_informe} "
            f"ha terminado con código {proceso.returncode}."
        )


    linea_resultado = None

    for linea in reversed(
        proceso.stdout.splitlines()
    ):
        if linea.startswith(
            MARCADOR_RESULTADO
        ):
            linea_resultado = linea[
                len(MARCADOR_RESULTADO):
            ]

            break


    if not linea_resultado:
        raise RuntimeError(
            f"No se ha recibido el resultado de {nombre_informe}."
        )


    try:
        resultado = json.loads(
            linea_resultado
        )

    except json.JSONDecodeError as error:
        raise RuntimeError(
            f"La respuesta de {nombre_informe} "
            "no contiene un JSON válido."
        ) from error


    print(
        f"Resultado de {opcion}:",
        resultado,
        flush=True,
    )


    return obtener_ruta_pdf(
        resultado
    )


def unir_pdfs(
    rutas_pdf,
    nombre_archivo,
):
    """
    Une varios PDFs en un único documento.
    """

    if not rutas_pdf:
        raise ValueError(
            "No hay documentos para unir."
        )

    ruta_salida = os.path.join(
        BASE_DIR,
        nombre_archivo,
    )

    writer = PdfWriter()

    try:
        for ruta_pdf in rutas_pdf:
            writer.append(
                ruta_pdf
            )

        with open(
            ruta_salida,
            "wb",
        ) as archivo_salida:
            writer.write(
                archivo_salida
            )

    finally:
        writer.close()


    if not os.path.isfile(
        ruta_salida
    ):
        raise FileNotFoundError(
            "No se ha creado el PDF conjunto."
        )

    return ruta_salida


def crear_respuesta_pdf(
    ruta_pdf,
    tipo_pedido,
    opciones_generadas,
):
    """
    Crea la respuesta común que recibe Wix.
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
        "opcionesGeneradas": opciones_generadas,
    }


def ejecutar_trabajo_generacion(
    trabajo_id,
    pedido_id,
    nombre,
    email,
    fecha,
    hora,
    lugar,
    lat,
    lon,
    tz_name,
    opciones,
    productos,
    tipo_pedido,
):
    """
    Genera los documentos en segundo plano.

    Cuando termina:
    - guarda el resultado en memoria;
    - notifica a Wix;
    - Wix actualiza el pedido y envía el correo.

    Si falla:
    - guarda el error;
    - notifica a Wix.
    """

    try:
        with BLOQUEO_TRABAJOS:
            TRABAJOS[trabajo_id]["estado"] = "procesando"
            TRABAJOS[trabajo_id]["actualizado"] = time.time()

        opciones_a_generar = obtener_opciones_a_generar(
            opciones,
            tipo_pedido,
        )

        if not opciones_a_generar:
            raise ValueError(
                "No hay documentos válidos para generar."
            )

        rutas_generadas = []

        for indice, opcion in enumerate(
            opciones_a_generar,
            start=1,
        ):
            with BLOQUEO_TRABAJOS:
                TRABAJOS[trabajo_id]["progreso"] = {
                    "actual": indice,
                    "total": len(opciones_a_generar),
                    "opcion": opcion,
                }

                TRABAJOS[trabajo_id]["actualizado"] = (
                    time.time()
                )

            ruta_pdf = generar_documento_en_proceso(
                opcion=opcion,
                nombre=nombre,
                fecha=fecha,
                hora=hora,
                lugar=lugar,
                lat=lat,
                lon=lon,
                tz_name=tz_name,
            )

            rutas_generadas.append(
                ruta_pdf
            )

        if len(rutas_generadas) == 1:
            ruta_final = rutas_generadas[0]

        else:
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

            ruta_final = unir_pdfs(
                rutas_pdf=rutas_generadas,
                nombre_archivo=nombre_archivo,
            )

        resultado = crear_respuesta_pdf(
            ruta_pdf=ruta_final,
            tipo_pedido=tipo_pedido,
            opciones_generadas=opciones_a_generar,
        )

        with BLOQUEO_TRABAJOS:
            TRABAJOS[trabajo_id]["estado"] = "completado"
            TRABAJOS[trabajo_id]["resultado"] = resultado
            TRABAJOS[trabajo_id]["error"] = None
            TRABAJOS[trabajo_id]["progreso"] = {
                "actual": len(opciones_a_generar),
                "total": len(opciones_a_generar),
                "opcion": None,
            }
            TRABAJOS[trabajo_id]["actualizado"] = time.time()

        print(
            f"Trabajo {trabajo_id} completado.",
            flush=True,
        )

        base_url = os.environ.get(
            "PUBLIC_BASE_URL",
            "https://carta-natal-api-fhh0.onrender.com",
        ).rstrip("/")

        ruta_pdf_publica = (
            resultado.get("pdf_url")
            or resultado.get("pdf")
            or resultado.get("url")
        )

        if not ruta_pdf_publica:
            raise ValueError(
                "No se ha obtenido la URL del PDF generado."
            )

        if ruta_pdf_publica.startswith(
            ("http://", "https://")
        ):
            url_pdf_completa = ruta_pdf_publica

        else:
            url_pdf_completa = (
                f"{base_url}{ruta_pdf_publica}"
            )

        callback_correcto = notificar_wix({
            "pedidoId": pedido_id,
            "estado": "Generado",
            "pdfUrl": url_pdf_completa,
            "nombre": nombre,
            "email": email,
            "opciones": opciones,
            "productos": productos,
            "tipoPedido": tipo_pedido,
        })

        if not callback_correcto:
            print(
                f"El trabajo {trabajo_id} terminó, "
                "pero Wix no confirmó el callback.",
                flush=True,
            )

    except Exception as error:
        print(
            f"Error en el trabajo {trabajo_id}:",
            repr(error),
            flush=True,
        )

        with BLOQUEO_TRABAJOS:
            if trabajo_id in TRABAJOS:
                TRABAJOS[trabajo_id]["estado"] = "error"
                TRABAJOS[trabajo_id]["error"] = str(error)
                TRABAJOS[trabajo_id]["actualizado"] = time.time()

        callback_correcto = notificar_wix({
            "pedidoId": pedido_id,
            "estado": "Error de generación",
            "errorGeneracion": str(error),
        })

        if not callback_correcto:
            print(
                f"No se ha podido notificar a Wix "
                f"el error del trabajo {trabajo_id}.",
                flush=True,
            )
@app.route(
    "/iniciar-generacion",
    methods=["POST"],
)
def iniciar_generacion():
    try:
        datos = request.get_json(
            silent=True
        ) or {}

        pedido_id = datos.get("pedidoId")
        nombre = datos.get("nombre")
        email = datos.get("email")
        fecha = datos.get("fecha")
        hora = datos.get("hora")
        lugar = datos.get("lugar")
        lat = datos.get("latitud")
        lon = datos.get("longitud")
        tz_name = datos.get("tz_name")

        opciones_recibidas = datos.get(
            "opciones",
            [],
        )

        productos = datos.get(
            "productos",
            [],
        )

        # ───── VALIDACIONES ─────────────────────────────
        if not pedido_id:
            return jsonify({
                "ok": False,
                "error":
                    "Falta el identificador del pedido.",
            }), 400


        if not nombre:
            return jsonify({
                "ok": False,
                "error": "Falta el nombre.",
            }), 400

        if not email:
            return jsonify({
                "ok": False,
                "error":
                    "Falta el correo electrónico.",
            }), 400

        if not fecha:
            return jsonify({
                "ok": False,
                "error":
                    "Falta la fecha de nacimiento.",
            }), 400

        if not hora:
            return jsonify({
                "ok": False,
                "error":
                    "Falta la hora de nacimiento.",
            }), 400

        if not lugar:
            return jsonify({
                "ok": False,
                "error":
                    "Falta el lugar de nacimiento.",
            }), 400

        if lat is None or lon is None:
            return jsonify({
                "ok": False,
                "error":
                    "Faltan las coordenadas "
                    "del lugar de nacimiento.",
            }), 400

        if not isinstance(
            opciones_recibidas,
            list,
        ):
            return jsonify({
                "ok": False,
                "error":
                    "El formato de las opciones "
                    "no es válido.",
            }), 400

        if not isinstance(
            productos,
            list,
        ):
            return jsonify({
                "ok": False,
                "error":
                    "El formato de los productos no es válido.",
            }), 400

        opciones = []

        for opcion in opciones_recibidas:
            if (
                opcion in OPCIONES_VALIDAS
                and opcion not in opciones
            ):
                opciones.append(
                    opcion
                )

        if not opciones:
            return jsonify({
                "ok": False,
                "error":
                    "No se ha seleccionado ningún informe.",
            }), 400

        if (
            "opMapaCompleto" in opciones
            and len(opciones) > 1
        ):
            return jsonify({
                "ok": False,
                "error":
                    "El Mapa Completo es un producto "
                    "independiente y no puede combinarse "
                    "con otros informes.",
            }), 400

        tipo_pedido = obtener_tipo_pedido(
            opciones
        )

        if tipo_pedido == "desconocido":
            return jsonify({
                "ok": False,
                "error":
                    "No se ha podido identificar "
                    "el tipo de pedido.",
            }), 400

        # ───── CREAR TRABAJO ────────────────────────────

        trabajo_id = str(
            uuid.uuid4()
        )

        ahora = time.time()

        with BLOQUEO_TRABAJOS:
            TRABAJOS[trabajo_id] = {
                "pedidoId": pedido_id,
                "estado": "pendiente",
                "creado": ahora,
                "actualizado": ahora,
                "resultado": None,
                "error": None,
                "progreso": {
                    "actual": 0,
                    "total": 0,
                    "opcion": None,
                },
            }

        EJECUTOR.submit(
            ejecutar_trabajo_generacion,
            trabajo_id,
            pedido_id,
            nombre,
            email,
            fecha,
            hora,
            lugar,
            lat,
            lon,
            tz_name,
            opciones,
            productos,
            tipo_pedido,
        )

        return jsonify({
            "ok": True,
            "trabajoId": trabajo_id,
            "estado": "pendiente",
        }), 202

    except Exception as error:
        print(
            "Error iniciando generación:",
            repr(error),
            flush=True,
        )

        return jsonify({
            "ok": False,
            "error": str(error),
        }), 500


@app.route(
    "/estado-generacion/<trabajo_id>",
    methods=["GET"],
)
def estado_generacion(trabajo_id):
    try:
        with BLOQUEO_TRABAJOS:
            trabajo = TRABAJOS.get(
                trabajo_id
            )

            if trabajo is None:
                return jsonify({
                    "ok": False,
                    "error":
                        "No se ha encontrado el trabajo solicitado.",
                }), 404

            respuesta = {
                "ok": True,
                "trabajoId": trabajo_id,
                "estado": trabajo.get(
                    "estado"
                ),
                "progreso": trabajo.get(
                    "progreso"
                ),
            }

            if trabajo.get("estado") == "completado":
                respuesta["resultado"] = trabajo.get(
                    "resultado"
                )

            elif trabajo.get("estado") == "error":
                respuesta["error"] = trabajo.get(
                    "error"
                )

        return jsonify(
            respuesta
        )

    except Exception as error:
        print(
            "Error consultando trabajo:",
            repr(error),
            flush=True,
        )

        return jsonify({
            "ok": False,
            "error": str(error),
        }), 500


# ───────────────────── GENERAR CARTA ─────────────────────

@app.route(
    "/generar-carta",
    methods=["POST"],
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
            "",
        )


        # ───── VALIDACIÓN DE DATOS ─────────────────────

        if not nombre:
            return jsonify({
                "ok": False,
                "error": "Falta el nombre.",
            }), 400

        if not fecha:
            return jsonify({
                "ok": False,
                "error":
                    "Falta la fecha de nacimiento.",
            }), 400

        if not hora:
            return jsonify({
                "ok": False,
                "error":
                    "Falta la hora de nacimiento.",
            }), 400

        if not lugar:
            return jsonify({
                "ok": False,
                "error":
                    "Falta el lugar de nacimiento.",
            }), 400

        if lat is None or lon is None:
            return jsonify({
                "ok": False,
                "error":
                    "Faltan las coordenadas "
                    "del lugar de nacimiento.",
            }), 400

        if not isinstance(
            opciones_recibidas,
            list,
        ):
            return jsonify({
                "ok": False,
                "error":
                    "El formato de las opciones "
                    "no es válido.",
            }), 400


        # Elimina opciones inválidas y duplicadas.
        opciones = []

        for opcion in opciones_recibidas:
            if (
                opcion in OPCIONES_VALIDAS
                and opcion not in opciones
            ):
                opciones.append(
                    opcion
                )


        if not opciones:
            return jsonify({
                "ok": False,
                "error":
                    "No se ha seleccionado ningún informe.",
            }), 400


        # ───── MAPA COMPLETO INDEPENDIENTE ─────────────

        if (
            "opMapaCompleto" in opciones
            and len(opciones) > 1
        ):
            return jsonify({
                "ok": False,
                "error":
                    "El Mapa Completo es un producto "
                    "independiente y no puede combinarse "
                    "con otros informes.",
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
                tipo_calculado,
                flush=True,
            )

            tipo_pedido = (
                tipo_calculado
            )


        if tipo_pedido == "desconocido":
            return jsonify({
                "ok": False,
                "error":
                    "No se ha podido identificar "
                    "el tipo de pedido.",
            }), 400


        opciones_a_generar = (
            obtener_opciones_a_generar(
                opciones,
                tipo_pedido,
            )
        )


        if not opciones_a_generar:
            return jsonify({
                "ok": False,
                "error":
                    "No hay documentos válidos "
                    "para generar.",
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
                "tipo_pedido": tipo_pedido,
                "opciones_a_generar":
                    opciones_a_generar,
            },
            flush=True,
        )


        # ───── GENERAR DOCUMENTOS AISLADOS ─────────────

        rutas_generadas = []

        for opcion in opciones_a_generar:
            ruta_pdf = generar_documento_en_proceso(
                opcion=opcion,
                nombre=nombre,
                fecha=fecha,
                hora=hora,
                lugar=lugar,
                lat=lat,
                lon=lon,
                tz_name=tz_name,
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
                    opciones_generadas=
                        opciones_a_generar,
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
            nombre_archivo=nombre_archivo,
        )


        return jsonify(
            crear_respuesta_pdf(
                ruta_pdf=ruta_unida,
                tipo_pedido=tipo_pedido,
                opciones_generadas=
                    opciones_a_generar,
            )
        )


    except Exception as error:
        print(
            "Error generando la carta:",
            repr(error),
            flush=True,
        )

        return jsonify({
            "ok": False,
            "error": str(error),
        }), 500


if __name__ == "__main__":
    app.run(
        debug=True
    )