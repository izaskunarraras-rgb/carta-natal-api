HUBER_QUIRALIDAD_TRAMPOLIN_DECO = True
HUBER_ORDEN_ZODIACAL_APLICADO = True
HUBER_SEMISEXTIL_VERDE_V22 = True
HUBER_FASE3_APLICADA = True
#!/usr/bin/env python3
"""
8. Figuras y configuraciones — Arquitectura Interna

Este documento observa la arquitectura profunda de la carta.

No se centra en posiciones aisladas, sino en cómo varios planetas
se conectan entre sí formando patrones mayores: tensiones, apoyos,
circuitos de repetición, puntos de descarga y zonas de integración.

Las figuras muestran cómo se organiza la energía cuando hay presión:
dónde tiendes a sostener demasiado,
dónde aparece movimiento,
dónde se acumula tensión
y qué partes de la carta pueden ayudarte a no romperte por dentro.

No habla de destino fijo.
Habla de estructuras internas que pueden hacerse más conscientes
cuando aprendes a reconocer cómo funcionan.
"""

import sys, os, re, math, subprocess
from datetime import datetime
import swisseph as swe
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import pytz
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# ─── CONSTANTES ────────────────────────────────────────────────────────────────

SIGNOS = ["Aries","Tauro","Géminis","Cáncer","Leo","Virgo",
          "Libra","Escorpio","Sagitario","Capricornio","Acuario","Piscis"]
SIMBOLOS_SIGNOS = ["♈","♉","♊","♋","♌","♍","♎","♏","♐","♑","♒","♓"]

ELEMENTO_SIGNO = {
    "Aries":"Fuego","Tauro":"Tierra","Géminis":"Aire","Cáncer":"Agua",
    "Leo":"Fuego","Virgo":"Tierra","Libra":"Aire","Escorpio":"Agua",
    "Sagitario":"Fuego","Capricornio":"Tierra","Acuario":"Aire","Piscis":"Agua"
}
MODALIDAD_SIGNO = {
    "Aries":"Cardinal","Tauro":"Fijo","Géminis":"Mutable","Cáncer":"Cardinal",
    "Leo":"Fijo","Virgo":"Mutable","Libra":"Cardinal","Escorpio":"Fijo",
    "Sagitario":"Mutable","Capricornio":"Cardinal","Acuario":"Fijo","Piscis":"Mutable"
}
COLORES_ELEMENTO = {"Fuego":"#CC2200","Tierra":"#2E7D32","Aire":"#E67E00","Agua":"#1A5FA8"}

PLANETAS_IDS = [
    (swe.SUN,"Sol","☉"),(swe.MOON,"Luna","☽"),(swe.MERCURY,"Mercurio","☿"),
    (swe.VENUS,"Venus","♀"),(swe.MARS,"Marte","♂"),(swe.JUPITER,"Júpiter","♃"),
    (swe.SATURN,"Saturno","♄"),(swe.URANUS,"Urano","♅"),
    (swe.NEPTUNE,"Neptuno","♆"),(swe.PLUTO,"Plutón","♇"),
]

PUNTOS_EJE = [
    ("Ascendente", "AC"),
    ("Medio Cielo", "MC"),
]

PLANETAS_PERSONALES = [
    "Sol", "Luna", "Mercurio", "Venus", "Marte"
]

PLANETAS_SOCIALES = [
    "Júpiter", "Saturno"
]

PLANETAS_TRANSPERSONALES = [
    "Urano", "Neptuno", "Plutón"
]

PUNTOS_SENSIBLES = [
    "Quirón", "Lilith"
]

PUNTOS_NUCLEARES = [
    "Sol", "Luna",
    "Mercurio", "Venus", "Marte",
    "Júpiter", "Saturno",
    "Urano", "Neptuno", "Plutón",
]

PUNTOS_ESTRUCTURALES = [
    "Ascendente",
    "Medio Cielo",
    "Nodo Norte",
    "Nodo Sur",
]

CHIRON_ID  = swe.CHIRON
LILITH_ID  = swe.MEAN_APOG

COLORES_PLANETA = {
    # Fuego
    "Sol":"#CC2200","Marte":"#CC2200","Júpiter":"#CC2200",
    # Tierra
    "Venus":"#2E7D32","Saturno":"#2E7D32",
    # Aire
    "Mercurio":"#E67E00","Urano":"#E67E00",
    # Agua
    "Luna":"#1A5FA8","Neptuno":"#1A5FA8","Plutón":"#1A5FA8",
    # Especiales
    "Quirón":"#7B2D8B","Lilith":"#7B2D8B",
    "Nodo Norte":"#888800","Nodo Sur":"#888800",
}

ASPECTOS_FIGURAS = {
    0:   ("Conjunción", "=", 10),
    30:  ("Semisextil", "⚺", 3),
    60:  ("Sextil", "✶", 7),
    90:  ("Cuadratura", "□", 8),
    120: ("Trígono", "△", 9),
    150: ("Quincuncio", "⚻", 4),
    180: ("Oposición", "☍", 10),
}

ORBES_EJES = {
    "=": 10,
    "☍": 10,
    "□": 8,
    "△": 9,
    "✶": 7,
    "⚻": 4,
    "⚺": 3,
}

# Quirón y Lilith se tratan como puntos sensibles. Sus aspectos
# no deben heredar los orbes amplios de planetas y luminarias.
ORBES_PUNTOS_SENSIBLES = {
    "=": 5,
    "☍": 5,
    "□": 4,
    "△": 4,
    "✶": 4,
    "⚻": 4,
    "⚺": 3,
}

TIPOS_FIGURA = [
    "T-cuadrada",
    "Gran trígono",
    "Cometa",
    "Yod",
    "Stellium",
    "Triángulo de aprendizaje",
    "Triángulo de aprendizaje pequeño",
    "Triángulo de aprendizaje mediano",
    "Triángulo de aprendizaje grande",
    "Ojo pequeño",
    "Red de aprendizaje",
    "T-cuadrada compuesta",
    "Yod con Ojo pequeño en la base",
]


CATALOGO_FIGURAS = {
    "T-cuadrada": {
        "nombre_canonico": "Triángulo de rendimiento",
        "familia": "rendimiento",
        "colores": ["rojo"],
        "dinamica_base": (
            "La oposición acumula tensión y las cuadraturas la conducen "
            "hacia el ápice, donde busca acción, producción o resolución."
        ),
    },
    "Gran trígono": {
        "nombre_canonico": "Triángulo de talento grande",
        "familia": "talento",
        "colores": ["azul"],
        "dinamica_base": (
            "Reúne una capacidad estable y disponible; necesita activación "
            "consciente para que la facilidad no se convierta en inercia."
        ),
    },
    "Cometa": {
        "nombre_canonico": "Cometa",
        "familia": "ambivalencia y talento",
        "colores": ["rojo", "azul"],
        "dinamica_base": (
            "La oposición moviliza el talento del gran triángulo y concentra "
            "su expresión a través del eje central de la figura."
        ),
    },
    "Triángulo de aprendizaje pequeño": {
        "nombre_canonico": "Triángulo de aprendizaje pequeño",
        "familia": "aprendizaje",
        "colores": ["rojo", "verde", "azul"],
        "dinamica_base": (
            "La tensión interna activa una búsqueda rápida de información "
            "y un reajuste práctico que tiende a repetirse con frecuencia."
        ),
    },
    "Triángulo de aprendizaje mediano": {
        "nombre_canonico": "Triángulo de aprendizaje mediano",
        "familia": "aprendizaje",
        "colores": ["rojo", "verde", "azul"],
        "dinamica_base": (
            "Parte de una capacidad o tranquilidad interna que el entorno "
            "cuestiona, obligando a informarse, actuar y recuperar equilibrio."
        ),
    },
    "Triángulo de aprendizaje grande": {
        "nombre_canonico": "Triángulo de aprendizaje grande",
        "familia": "aprendizaje",
        "colores": ["rojo", "verde", "azul"],
        "dinamica_base": (
            "El conflicto estimula una búsqueda prolongada de comprensión; "
            "las soluciones demasiado fáciles pueden dejar intacta la duda."
        ),
    },
    "Triángulo de aprendizaje": {
        "nombre_canonico": "Triángulo dominante",
        "familia": "aprendizaje y transformación",
        "colores": ["rojo", "verde", "azul"],
        "dinamica_base": (
            "La tensión cuestiona una capacidad previamente asentada y abre "
            "un proceso profundo de búsqueda, transformación y nueva expresión."
        ),
    },
    "Ojo pequeño": {
        "nombre_canonico": "Figura de información (ojo)",
        "familia": "información",
        "colores": ["verde", "azul"],
        "dinamica_base": (
            "Capta, relaciona y organiza señales del entorno con gran "
            "sensibilidad; necesita discriminar qué información es relevante."
        ),
    },
}




CATALOGO_HUBER_20 = {
    "Cuadrado de rendimiento": {"familia":"rendimiento","colores":["rojo"],"vertices":4,"estado_detector":"implementado"},
    "Triángulo de rendimiento": {"familia":"rendimiento","colores":["rojo"],"vertices":3,"estado_detector":"implementado","alias_interno":"T-cuadrada"},
    "Triángulo de talento grande": {"familia":"talento","colores":["azul"],"vertices":3,"estado_detector":"implementado","alias_interno":"Gran trígono"},
    "Triángulo de talento pequeño": {"familia":"talento","colores":["azul"],"vertices":3,"estado_detector":"implementado"},
    "Triángulo de ambivalencia": {"familia":"ambivalencia","colores":["rojo","azul"],"vertices":3,"estado_detector":"implementado"},
    "Figura de ambivalencia doble": {"familia":"ambivalencia","colores":["rojo","azul"],"vertices":4,"estado_detector":"implementado"},
    "Rectángulo de rectitud": {"familia":"ambivalencia","colores":["rojo","azul"],"vertices":4,"estado_detector":"implementado"},
    "Cometa": {"familia":"ambivalencia y talento","colores":["rojo","azul"],"vertices":4,"estado_detector":"implementado","alias_interno":"Cometa"},
    "Cuna": {"familia":"ambivalencia","colores":["rojo","azul"],"vertices":4,"estado_detector":"implementado"},
    "Triángulo de excitación": {"familia":"excitación","colores":["rojo","verde"],"vertices":3,"estado_detector":"implementado"},
    "Rectángulo de excitación": {"familia":"excitación","colores":["rojo","verde"],"vertices":4,"estado_detector":"implementado"},
    "Figura de búsqueda": {"familia":"información","colores":["azul","verde"],"vertices":3,"estado_detector":"implementado"},
    "Figura de proyección": {"familia":"información","colores":["azul","verde"],"vertices":3,"estado_detector":"implementado","alias_interno":"Yod"},
    "Figura de información (ojo)": {"familia":"información","colores":["azul","verde"],"vertices":3,"estado_detector":"implementado","alias_interno":"Ojo pequeño"},
    "Triángulo de aprendizaje pequeño": {"familia":"aprendizaje","colores":["rojo","verde","azul"],"vertices":3,"estado_detector":"implementado","alias_interno":"Triángulo de aprendizaje pequeño"},
    "Triángulo de aprendizaje mediano": {"familia":"aprendizaje","colores":["rojo","verde","azul"],"vertices":3,"estado_detector":"implementado","alias_interno":"Triángulo de aprendizaje mediano"},
    "Triángulo de aprendizaje grande": {"familia":"aprendizaje","colores":["rojo","verde","azul"],"vertices":3,"estado_detector":"implementado","alias_interno":"Triángulo de aprendizaje grande"},
    "Triángulo dominante": {"familia":"aprendizaje y transformación","colores":["rojo","verde","azul"],"vertices":3,"estado_detector":"implementado","alias_interno":"Triángulo de aprendizaje"},
    "Trapecio": {"familia":"aprendizaje","colores":["rojo","verde","azul"],"vertices":4,"estado_detector":"implementado"},
    "Figura de aspiración": {"familia":"aprendizaje","colores":["rojo","verde","azul"],"vertices":4,"estado_detector":"implementado"},
}

CATALOGO_COMPLEMENTARIO_AI = {
    "Stellium": {"sistema":"Arquitectura Interna","familia":"concentración","estado_detector":"implementado"},
}

ALIAS_HUBER_POR_TIPO_INTERNO = {
    datos.get("alias_interno"): nombre
    for nombre, datos in CATALOGO_HUBER_20.items()
    if datos.get("alias_interno")
}

def normalizar_figura_huber(figura):
    tipo = figura.get("tipo", "")

    # Las piezas nuevas de la fase 2 ya nacen con el nombre
    # canónico Huber como tipo.
    if tipo in CATALOGO_HUBER_20:
        datos = CATALOGO_HUBER_20[tipo]
        figura.setdefault("sistema", "Huber")
        figura.setdefault("nombre_canonico", tipo)
        figura.setdefault("familia_huber", datos.get("familia"))
        figura.setdefault("colores_huber", datos.get("colores", []))
        figura.setdefault("nivel_catalogo", "basica")
        return figura
    if tipo in ALIAS_HUBER_POR_TIPO_INTERNO:
        canonico = ALIAS_HUBER_POR_TIPO_INTERNO[tipo]
        datos = CATALOGO_HUBER_20[canonico]
        figura.setdefault("sistema", "Huber")
        figura.setdefault("nombre_canonico", canonico)
        figura.setdefault("familia_huber", datos.get("familia"))
        figura.setdefault("colores_huber", datos.get("colores", []))
        figura.setdefault("nivel_catalogo", "basica")
        return figura
    if 'CATALOGO_HUBER_VARIANTES_26' in globals() and tipo in CATALOGO_HUBER_VARIANTES_26:
        datos = CATALOGO_HUBER_VARIANTES_26[tipo]
        figura.setdefault('sistema','Huber')
        figura.setdefault('nombre_canonico',tipo)
        figura.setdefault('nivel_catalogo','variante')
        figura.setdefault('grupo_huber',datos.get('grupo'))
        figura.setdefault('pagina_fuente_huber',datos.get('pagina'))
        return figura
    if tipo in CATALOGO_COMPLEMENTARIO_AI:
        figura.setdefault("sistema", "Arquitectura Interna")
        figura.setdefault("nombre_canonico", tipo)
        figura.setdefault("nivel_catalogo", "complementaria")
        return figura
    figura.setdefault("sistema", "Arquitectura Interna")
    figura.setdefault("nombre_canonico", tipo)
    figura.setdefault("nivel_catalogo", "compuesta_editorial")
    return figura


# ─── FUNCIONES DE CÁLCULO (reutilizadas de carta_astral.py) ─────────────────

def geocodificar(ciudad):
    geolocator = Nominatim(user_agent="figuras_configuraciones_ai")
    location = geolocator.geocode(ciudad, language="es")
    if not location:
        raise ValueError(f"No se pudo encontrar: {ciudad}")
    return location.latitude, location.longitude

def obtener_timezone(lat, lon):
    tf = TimezoneFinder()
    tz = tf.timezone_at(lat=lat, lng=lon)
    if not tz:
        raise ValueError("No se pudo determinar la zona horaria")
    return tz

def fecha_a_jd(año, mes, dia, hora, minuto, tz_name):
    tz = pytz.timezone(tz_name)
    dt = tz.localize(datetime(año, mes, dia, hora, minuto))
    dt_utc = dt.astimezone(pytz.utc)
    h = dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0
    return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, h)

def grados_a_signo(lon):
    idx = int(lon / 30)
    return SIGNOS[idx % 12], lon - idx * 30

def grado_a_dms(grado):
    d = int(grado)
    m = int(round((grado - d) * 60))
    if m == 60:
        d += 1; m = 0
    return f"{d}°{m:02d}'"

def nivel_grado_critico(grado):
    """
    Detecta grados finales de signo.
    - 29°00' a 29°59': grado anarético
    - 28°00' a 28°59': grado previo al anarético
    """
    if grado >= 29.0:
        return "anaretico"
    elif grado >= 28.0:
        return "pre_anaretico"
    return ""


def detectar_grados_criticos(carta):
    planetas = carta["planetas"]
    puntos = []

    for nombre, p in planetas.items():
        nivel = nivel_grado_critico(p.get("grado", 0))
        if nivel:
            puntos.append({
                "tipo": "planeta",
                "nombre": nombre,
                "signo": p["signo"],
                "grado": p["grado"],
                "casa": p.get("casa", ""),
                "nivel": nivel,
            })

    asc = carta["asc"]
    nivel_asc = nivel_grado_critico(asc.get("grado", 0))
    if nivel_asc:
        puntos.append({
            "tipo": "eje",
            "nombre": "Ascendente",
            "signo": asc["signo"],
            "grado": asc["grado"],
            "casa": "",
            "nivel": nivel_asc,
        })

        signo_dc = SIGNOS[(SIGNOS.index(asc["signo"]) + 6) % 12]
        puntos.append({
            "tipo": "eje",
            "nombre": "Descendente",
            "signo": signo_dc,
            "grado": asc["grado"],
            "casa": "",
            "nivel": nivel_asc,
        })

    mc = carta["mc"]
    nivel_mc = nivel_grado_critico(mc.get("grado", 0))
    if nivel_mc:
        puntos.append({
            "tipo": "eje",
            "nombre": "Medio Cielo",
            "signo": mc["signo"],
            "grado": mc["grado"],
            "casa": "",
            "nivel": nivel_mc,
        })

        signo_ic = SIGNOS[(SIGNOS.index(mc["signo"]) + 6) % 12]
        puntos.append({
            "tipo": "eje",
            "nombre": "Fondo del Cielo",
            "signo": signo_ic,
            "grado": mc["grado"],
            "casa": "",
            "nivel": nivel_mc,
        })

    return puntos


def calcular_carta(año, mes, dia, hora, minuto, lat, lon, tz_name):

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    EPHE_PATH = os.path.join(BASE_DIR, "ephe")

    swe.set_ephe_path(EPHE_PATH)

    FLAGS = swe.FLG_SPEED

    jd = fecha_a_jd(
        año, mes, dia,
        hora, minuto,
        tz_name
    )

    planetas = {}

    for pid, nombre, simbolo in PLANETAS_IDS:
        pos, _ = swe.calc_ut(jd, pid, FLAGS)
        signo, grado = grados_a_signo(pos[0])
        planetas[nombre] = {"simbolo":simbolo,"lon":pos[0],"signo":signo,"grado":grado,"retrogrado":pos[3]<0}

    # ─── QUIRÓN ──────────────────────────────────────────────────────────────
    try:
        pos_ch, _ = swe.calc_ut(jd, CHIRON_ID, FLAGS)

        if pos_ch[0] == 0.0:
            raise ValueError()

        signo_ch, grado_ch = grados_a_signo(pos_ch[0])

        planetas["Quirón"] = {
            "simbolo": "⚷",
            "lon": pos_ch[0],
            "signo": signo_ch,
            "grado": grado_ch,
            "retrogrado": pos_ch[3] < 0
        }

    except Exception as e:
        raise RuntimeError(
            f"No se pudo calcular Quirón con precisión: {e}"
        )


    # Lilith
    pos_li, _ = swe.calc_ut(jd, LILITH_ID, swe.FLG_SPEED)
    signo_li, grado_li = grados_a_signo(pos_li[0])
    planetas["Lilith"] = {"simbolo":"⚸","lon":pos_li[0],"signo":signo_li,"grado":grado_li,"retrogrado":False}

    # Nodos (True Node)
    pos_nn, _ = swe.calc_ut(jd, swe.TRUE_NODE, swe.FLG_SPEED)
    signo_nn, grado_nn = grados_a_signo(pos_nn[0])
    lon_ns = (pos_nn[0]+180) % 360
    signo_ns, grado_ns = grados_a_signo(lon_ns)
    planetas["Nodo Norte"] = {"simbolo":"☊","lon":pos_nn[0],"signo":signo_nn,"grado":grado_nn,"retrogrado":False}
    planetas["Nodo Sur"]   = {"simbolo":"☋","lon":lon_ns,"signo":signo_ns,"grado":grado_ns,"retrogrado":False}

    # Casas Placidus
    cuspides, ascmc = swe.houses(jd, lat, lon, b'P')
    asc_lon, mc_lon = ascmc[0], ascmc[1]
    signo_asc, grado_asc = grados_a_signo(asc_lon)
    signo_mc,  grado_mc  = grados_a_signo(mc_lon)

    # ─── EJES COMO PUNTOS ESTRUCTURALES ─────────────────────────────────────

    planetas["Ascendente"] = {
        "simbolo": "AC",
        "lon": asc_lon,
        "signo": signo_asc,
        "grado": grado_asc,
        "retrogrado": False,
        "casa": 1
    }

    planetas["Medio Cielo"] = {
        "simbolo": "MC",
        "lon": mc_lon,
        "signo": signo_mc,
        "grado": grado_mc,
        "retrogrado": False,
        "casa": 10
    }

    def casa_de(p_lon):
        for i in range(12):
            c_ini = cuspides[i]
            c_fin = cuspides[(i+1)%12]
            if c_ini <= c_fin:
                if c_ini <= p_lon < c_fin: return i+1
            else:
                if p_lon >= c_ini or p_lon < c_fin: return i+1
        return 12

    for nombre in planetas:
        planetas[nombre]["casa"] = casa_de(planetas[nombre]["lon"])

    # Signos interceptados: signos cuyo tramo completo (30°) cae dentro de una casa
    # (ninguna cúspide aterriza en ese signo)
    interceptados = {}   # {signo: casa}
    duplicados    = {}   # {signo: [casa1, casa2]} — signos que aparecen en dos cúspides
    for idx_signo in range(12):
        lon_ini_signo = idx_signo * 30.0
        lon_fin_signo = lon_ini_signo + 30.0
        cusps_en_signo = []
        for i, c in enumerate(cuspides):
            c_norm = c % 360
            if lon_ini_signo <= c_norm < lon_fin_signo:
                cusps_en_signo.append(i+1)
        nombre_signo = SIGNOS[idx_signo]
        if len(cusps_en_signo) == 0:
            interceptados[nombre_signo] = casa_de(lon_ini_signo + 0.001)
        elif len(cusps_en_signo) >= 2:
            duplicados[nombre_signo] = cusps_en_signo

    # Marcar si cada planeta está en signo interceptado
    for nombre in planetas:
        signo_p = planetas[nombre]["signo"]
        planetas[nombre]["interceptado"] = signo_p in interceptados

    return {
        "planetas":      planetas,
        "cuspides":      list(cuspides),
        "asc":           {"lon":asc_lon,"signo":signo_asc,"grado":grado_asc},
        "mc":            {"lon":mc_lon, "signo":signo_mc, "grado":grado_mc},
        "interceptados": interceptados,   # {signo: casa}
        "duplicados":    duplicados,      # {signo: [casas]}
        "jd":            jd
    }

def calcular_aspectos_figuras(planetas):
    nombres = [
        "Sol", "Luna", "Mercurio", "Venus", "Marte",
        "Júpiter", "Saturno", "Urano", "Neptuno", "Plutón",
        "Quirón", "Lilith", "Nodo Norte", "Nodo Sur",
        "Ascendente", "Medio Cielo"
    ]

    nombres = [n for n in nombres if n in planetas]
    aspectos = []

    for i in range(len(nombres)):
        for j in range(i + 1, len(nombres)):
            n1, n2 = nombres[i], nombres[j]

            diff = abs(planetas[n1]["lon"] - planetas[n2]["lon"])
            if diff > 180:
                diff = 360 - diff

            for angulo, (nombre_asp, simbolo_asp, orbe_base) in ASPECTOS_FIGURAS.items():
                def orbe_del_extremo(nombre, otro):

                    # Los ejes conservan sus márgenes específicos.
                    if (
                        nombre in (
                            "Ascendente",
                            "Medio Cielo",
                        )
                        or otro in (
                            "Ascendente",
                            "Medio Cielo",
                        )
                    ):
                        return ORBES_EJES.get(
                            simbolo_asp,
                            orbe_base,
                        )

                    # Planetas y nodos utilizan el mismo orbe
                    # general definido en ASPECTOS_FIGURAS.
                    return orbe_base

                orbe_n1 = orbe_del_extremo(n1, n2)
                orbe_n2 = orbe_del_extremo(n2, n1)

                # Quirón y Lilith siguen siendo una ampliación propia y
                # conservan los márgenes reducidos que ya habíamos acordado.
                # Quirón y Lilith conservan un orbe reducido
                # únicamente en su propio extremo del aspecto.
                # El otro planeta mantiene su orbe correspondiente.
                limite_sensible = (
                    ORBES_PUNTOS_SENSIBLES.get(
                        simbolo_asp,
                        orbe_base,
                    )
                )

                if n1 in ("Quirón", "Lilith"):
                    orbe_n1 = min(
                        orbe_n1,
                        limite_sensible,
                    )

                if n2 in ("Quirón", "Lilith"):
                    orbe_n2 = min(
                        orbe_n2,
                        limite_sensible,
                    )

                orbe_val = round(abs(diff - angulo), 2)
                n1_en_orbe = orbe_val <= orbe_n1
                n2_en_orbe = orbe_val <= orbe_n2

                # Quirón y Lilith tienen orbe propio y VINCULANTE.
                # Si uno de ellos participa en el aspecto, no basta con que
                # el otro extremo admita un orbe mayor: el punto sensible
                # también debe estar dentro de su límite reducido.
                sensibles_presentes = [
                    nombre
                    for nombre in (n1, n2)
                    if nombre in ("Quirón", "Lilith")
                ]
                sensibles_en_orbe = all(
                    (
                        n1_en_orbe if nombre == n1 else n2_en_orbe
                    )
                    for nombre in sensibles_presentes
                )

                aceptado_por_extremos = n1_en_orbe or n2_en_orbe
                aspecto_aceptado = (
                    aceptado_por_extremos
                    and sensibles_en_orbe
                )

                if aspecto_aceptado:
                    bidireccional = n1_en_orbe and n2_en_orbe
                    desde = []

                    if n1_en_orbe:
                        desde.append(n1)

                    if n2_en_orbe:
                        desde.append(n2)

                    aspectos.append({
                        "p1": n1,
                        "p2": n2,
                        # Posiciones reales de los extremos. Se conservan en
                        # el aspecto para poder clasificar el TAMAÑO espacial
                        # de las figuras según el criterio Huber
                        # (grande / mediana / pequeña), sin depender del nombre.
                        "lon_p1": round(float(planetas[n1]["lon"]) % 360.0, 6),
                        "lon_p2": round(float(planetas[n2]["lon"]) % 360.0, 6),
                        "nombre": nombre_asp,
                        "simbolo": simbolo_asp,
                        "orbe": orbe_val,
                        "orbe_p1": orbe_n1,
                        "orbe_p2": orbe_n2,
                        "p1_en_orbe": n1_en_orbe,
                        "p2_en_orbe": n2_en_orbe,
                        "bidireccional": bidireccional,
                        "direccion": (
                            "bidireccional"
                            if bidireccional
                            else "unidireccional"
                        ),
                        "desde": desde,
                        "angulo": angulo,
                        "relevancia": "exacto" if orbe_val <= 1.0 else "estructural",
                    })
                    break

    return sorted(aspectos, key=lambda x: x["orbe"])


# ─── RUEDA ASTROLÓGICA ────────────────────────────────────────────────────────

def dibujar_rueda(carta, nombre_persona, archivo_salida):
    fig, ax = plt.subplots(1, 1, figsize=(12,12))
    ax.set_aspect('equal'); ax.axis('off')
    ax.set_xlim(-1.5,1.5); ax.set_ylim(-1.5,1.5)

    R_EXT=1.35; R_SIGNO=1.20; R_SIGN_IN=1.05
    R_CASA_OUT=1.02; R_CASA_IN=0.65; R_PLANETA=0.82

    asc_lon = carta["asc"]["lon"]

    def lon_a_angulo(lon):
        return math.radians(180+(lon-asc_lon))

    for i,signo in enumerate(SIGNOS):
        elem = ELEMENTO_SIGNO[signo]
        color = COLORES_ELEMENTO[elem]
        ang_ini = lon_a_angulo(i*30)
        ang_fin = lon_a_angulo((i+1)*30)
        theta = np.linspace(ang_ini, ang_fin, 50)
        xs = [math.cos(a)*R_EXT for a in theta]+[math.cos(a)*R_SIGN_IN for a in reversed(theta)]
        ys = [math.sin(a)*R_EXT for a in theta]+[math.sin(a)*R_SIGN_IN for a in reversed(theta)]
        ax.fill(xs, ys, color=color, alpha=0.35, zorder=1)

    for r,lw,c in [(R_EXT,2,'#333'),(R_SIGN_IN,1.5,'#333'),(R_CASA_IN,1.5,'#555'),(0.25,1,'#888')]:
        ax.add_patch(plt.Circle((0,0),r,fill=False,color=c,linewidth=lw,zorder=2))

    for i in range(12):
        ang = lon_a_angulo(i*30)
        ax.plot([math.cos(ang)*R_SIGN_IN,math.cos(ang)*R_EXT],
                [math.sin(ang)*R_SIGN_IN,math.sin(ang)*R_EXT],color='#555',linewidth=0.8,zorder=2)

    for i,(signo,simbolo) in enumerate(zip(SIGNOS,SIMBOLOS_SIGNOS)):
        ang_mid = lon_a_angulo(i*30+15)
        r_mid = (R_SIGN_IN+R_EXT)/2
        elem = ELEMENTO_SIGNO[signo]
        ax.text(math.cos(ang_mid)*r_mid,math.sin(ang_mid)*r_mid,simbolo,
                ha='center',va='center',fontsize=20,color=COLORES_ELEMENTO[elem],fontweight='bold',zorder=5)

    # Marcas de grados en el borde interior del anillo de signos
    for deg in range(360):
        if deg % 30 == 0: continue  # ya marcado por la línea de signo
        ang = lon_a_angulo(deg)
        if deg % 10 == 0:
            r_in, lw = R_SIGN_IN - 0.055, 1.0
        elif deg % 5 == 0:
            r_in, lw = R_SIGN_IN - 0.035, 0.7
        else:
            r_in, lw = R_SIGN_IN - 0.018, 0.4
        ax.plot([math.cos(ang)*R_SIGN_IN, math.cos(ang)*r_in],
                [math.sin(ang)*R_SIGN_IN, math.sin(ang)*r_in],
                color='#555', linewidth=lw, zorder=2)

    cuspides = carta["cuspides"]
    for i,cusp in enumerate(cuspides):
        ang = lon_a_angulo(cusp)
        lw = 2.0 if i in (0,3,6,9) else 0.8
        col = '#111' if i in (0,3,6,9) else '#666'
        ax.plot([math.cos(ang)*R_CASA_IN,math.cos(ang)*R_CASA_OUT],
                [math.sin(ang)*R_CASA_IN,math.sin(ang)*R_CASA_OUT],color=col,linewidth=lw,zorder=3)
        # Número de casa junto a la cúspide, dentro del anillo planetario.
        # Un pequeño desplazamiento angular evita montarlo sobre la línea.
        ang_num = lon_a_angulo(cusp + 2.2)
        r_num = R_CASA_IN + 0.035
        ax.text(math.cos(ang_num)*r_num, math.sin(ang_num)*r_num, str(i+1),
                ha='center', va='center', fontsize=8, color='#444',
                fontweight='bold', zorder=8)

    # ── Líneas de aspecto ────────────────────────────────────────────────────
    _ASP_COLORES = {
        "□":"#CC2200",
        "☍":"#CC2200",
        "△":"#1A5FA8",
        "✶":"#1A5FA8",
        "⚺":"#2E7D32",
        "⚻":"#2E7D32",
        "=":"#7B2D8B"
    }

    _ASP_LW = {
        "□":1.0,
        "☍":1.0,
        "△":0.9,
        "✶":0.8,
        "⚺":0.7,
        "⚻":0.7,
        "=":1.2
    }

    _ASP_ALPHA = {
        "□":0.55,
        "☍":0.55,
        "△":0.50,
        "✶":0.45,
        "⚺":0.35,
        "⚻":0.35,
        "=":0.75
    }

    R_ASP = R_CASA_IN - 0.02

    for asp in calcular_aspectos_figuras(carta["planetas"]):
        if asp["orbe"] > 10:
            continue

        sim = asp["simbolo"]
        if sim not in _ASP_COLORES:
            continue

        p1, p2 = asp["p1"], asp["p2"]
        if p1 not in carta["planetas"] or p2 not in carta["planetas"]:
            continue

        a1 = lon_a_angulo(carta["planetas"][p1]["lon"])
        a2 = lon_a_angulo(carta["planetas"][p2]["lon"])

        ax.plot(
            [math.cos(a1) * R_ASP, math.cos(a2) * R_ASP],
            [math.sin(a1) * R_ASP, math.sin(a2) * R_ASP],
            color=_ASP_COLORES[sim],
            linewidth=_ASP_LW[sim],
            alpha=_ASP_ALPHA[sim],
            linestyle="solid",
            zorder=2,
        )

   

    orden = [
        "Sol","Luna","Mercurio","Venus","Marte","Júpiter","Saturno",
        "Urano","Neptuno","Plutón","Quirón","Lilith","Nodo Norte","Nodo Sur",
        "Ascendente","Medio Cielo"
    ]

    # Todos los planetas deben permanecer en el anillo central.
    # Estos límites evitan que un planeta cercano se meta dentro del círculo interior.
    RADIO_MIN = R_CASA_IN + 0.08
    RADIO_MAX = R_SIGN_IN - 0.08
    RADIO_SEP = 0.08

    lones_usados = []
    radios = {}

    for nombre in orden:
        if nombre not in carta["planetas"]:
            continue

        lon = carta["planetas"][nombre]["lon"]
        radio = R_PLANETA

        for lp, rp in lones_usados:
            d = abs(lon - lp) % 360
            if d > 180:
                d = 360 - d

            if d < 8:
                candidato = rp - RADIO_SEP

                if candidato < RADIO_MIN:
                    candidato = rp + RADIO_SEP

                radio = max(RADIO_MIN, min(candidato, RADIO_MAX))
                break

        lones_usados.append((lon, radio))
        radios[nombre] = radio

    for nombre in orden:

        if nombre not in carta["planetas"]:
            continue

        if nombre in (
            "Ascendente",
            "Medio Cielo",
        ):
            continue

        p = carta["planetas"][nombre]

        ang = lon_a_angulo(
            p["lon"]
        )

        r = radios[nombre]

        color = COLORES_PLANETA.get(nombre, "#333")
        simbolo = p["simbolo"]

        x_planeta = math.cos(ang) * r
        y_planeta = math.sin(ang) * r

        ax.text(
            x_planeta,
            y_planeta,
            simbolo,
            ha="center",
            va="center",
            fontsize=17,
            color=color,
            fontweight="bold",
            zorder=6
        )

        # Retrogradación: se dibuja como una R normal, separada del glifo.
        # Así no dependemos de que la fuente soporte el superíndice Unicode ᴿ.
        if p.get("retrogrado"):
            ax.text(
                x_planeta + 0.035,
                y_planeta + 0.035,
                "R",
                ha="left",
                va="bottom",
                fontsize=8,
                color=color,
                fontweight="bold",
                zorder=7,
            )

        # Línea hacia el círculo interior de casas
        ax.plot(
            [math.cos(ang)*(r-0.07), math.cos(ang)*(R_CASA_IN-0.02)],
            [math.sin(ang)*(r-0.07), math.sin(ang)*(R_CASA_IN-0.02)],
            color=color,
            linewidth=0.5,
            alpha=0.5,
            zorder=3
        )

        # Línea hacia los grados del anillo de signos
        ax.plot(
            [math.cos(ang)*(r+0.07), math.cos(ang)*(R_SIGN_IN+0.01)],
            [math.sin(ang)*(r+0.07), math.sin(ang)*(R_SIGN_IN+0.01)],
            color=color,
            linewidth=0.8,
            alpha=0.8,
            zorder=3
        )

    for etiqueta, lon_pt in [
        ("AC", carta["asc"]["lon"]),
        ("DC", (carta["asc"]["lon"] + 180) % 360),
        ("MC", carta["mc"]["lon"]),
        ("IC", (carta["mc"]["lon"] + 180) % 360)
    ]:
        ang = lon_a_angulo(lon_pt)

        ax.text(
            math.cos(ang)*(R_EXT+0.09),
            math.sin(ang)*(R_EXT+0.09),
            etiqueta,
            ha="center",
            va="center",
            fontsize=13,
            fontweight="bold",
            color="#111",
            zorder=7
        )

    ax.text(
        0,
        0,
        nombre_persona.replace(" ","\n"),
        ha="center",
        va="center",
        fontsize=8,
        color="#333",
        style="italic",
        zorder=7
    )

    plt.title(f"Carta Natal — {nombre_persona}", fontsize=14, fontweight="bold", pad=15)
    plt.tight_layout()
    plt.savefig(archivo_salida, dpi=150, bbox_inches="tight", facecolor="white", edgecolor="none")
    plt.close()


def dibujar_rueda_arquitectura(
    carta,
    aspectos_relevantes,
    puntos_organizadores,
    nombre_persona,
    archivo_salida,
):
    fig, ax = plt.subplots(
        1,
        1,
        figsize=(12, 12)
    )

    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)

    R_EXT = 1.35
    R_SIGNO = 1.20
    R_SIGN_IN = 1.05
    R_CASA_OUT = 1.02
    R_CASA_IN = 0.65
    R_PLANETA = 0.82

    asc_lon = carta["asc"]["lon"]

    def lon_a_angulo(lon):
        return math.radians(
            180 + (lon - asc_lon)
        )

    # ── SIGNOS ──────────────────────────────

    for i, signo in enumerate(SIGNOS):
        elem = ELEMENTO_SIGNO[signo]
        color = COLORES_ELEMENTO[elem]

        ang_ini = lon_a_angulo(i * 30)
        ang_fin = lon_a_angulo((i + 1) * 30)

        theta = np.linspace(
            ang_ini,
            ang_fin,
            50
        )

        xs = (
            [
                math.cos(a) * R_EXT
                for a in theta
            ]
            +
            [
                math.cos(a) * R_SIGN_IN
                for a in reversed(theta)
            ]
        )

        ys = (
            [
                math.sin(a) * R_EXT
                for a in theta
            ]
            +
            [
                math.sin(a) * R_SIGN_IN
                for a in reversed(theta)
            ]
        )

        ax.fill(
            xs,
            ys,
            color=color,
            alpha=0.35,
            zorder=1,
        )

    # ── CÍRCULOS ────────────────────────────

    for r, lw, c in [
        (R_EXT, 2, "#333"),
        (R_SIGN_IN, 1.5, "#333"),
        (R_CASA_IN, 1.5, "#555"),
        (0.25, 1, "#888"),
    ]:
        ax.add_patch(
            plt.Circle(
                (0, 0),
                r,
                fill=False,
                color=c,
                linewidth=lw,
                zorder=2,
            )
        )

    # ── DIVISIONES DE SIGNOS ────────────────

    for i in range(12):
        ang = lon_a_angulo(i * 30)

        ax.plot(
            [
                math.cos(ang) * R_SIGN_IN,
                math.cos(ang) * R_EXT,
            ],
            [
                math.sin(ang) * R_SIGN_IN,
                math.sin(ang) * R_EXT,
            ],
            color="#555",
            linewidth=0.8,
            zorder=2,
        )

    # ── SÍMBOLOS DE SIGNOS ──────────────────

    for i, (signo, simbolo) in enumerate(
        zip(
            SIGNOS,
            SIMBOLOS_SIGNOS,
        )
    ):
        ang_mid = lon_a_angulo(
            i * 30 + 15
        )

        r_mid = (
            R_SIGN_IN + R_EXT
        ) / 2

        elem = ELEMENTO_SIGNO[signo]

        ax.text(
            math.cos(ang_mid) * r_mid,
            math.sin(ang_mid) * r_mid,
            simbolo,
            ha="center",
            va="center",
            fontsize=20,
            color=COLORES_ELEMENTO[elem],
            fontweight="bold",
            zorder=5,
        )

    # ── MARCAS DE GRADOS ────────────────────

    for deg in range(360):

        if deg % 30 == 0:
            continue

        ang = lon_a_angulo(deg)

        if deg % 10 == 0:
            r_in = R_SIGN_IN - 0.055
            lw = 1.0

        elif deg % 5 == 0:
            r_in = R_SIGN_IN - 0.035
            lw = 0.7

        else:
            r_in = R_SIGN_IN - 0.018
            lw = 0.4

        ax.plot(
            [
                math.cos(ang) * R_SIGN_IN,
                math.cos(ang) * r_in,
            ],
            [
                math.sin(ang) * R_SIGN_IN,
                math.sin(ang) * r_in,
            ],
            color="#555",
            linewidth=lw,
            zorder=2,
        )

    # ── CASAS ───────────────────────────────

    cuspides = carta["cuspides"]

    for i, cusp in enumerate(cuspides):

        ang = lon_a_angulo(cusp)

        lw = (
            2.0
            if i in (0, 3, 6, 9)
            else 0.8
        )

        col = (
            "#111"
            if i in (0, 3, 6, 9)
            else "#666"
        )

        ax.plot(
            [
                math.cos(ang) * R_CASA_IN,
                math.cos(ang) * R_CASA_OUT,
            ],
            [
                math.sin(ang) * R_CASA_IN,
                math.sin(ang) * R_CASA_OUT,
            ],
            color=col,
            linewidth=lw,
            zorder=3,
        )

        # Número de casa junto a su cúspide, dentro del anillo planetario.
        # Se desplaza solo 2.2° hacia el interior de la casa para que
        # quede claramente asociado a la línea sin superponerse a ella.
        ang_num = lon_a_angulo(
            cusp + 2.2
        )

        r_num = R_CASA_IN + 0.035

        ax.text(
            math.cos(ang_num) * r_num,
            math.sin(ang_num) * r_num,
            str(i + 1),
            ha="center",
            va="center",
            fontsize=8,
            color="#444",
            fontweight="bold",
            zorder=8,
        )

    # ── ASPECTOS DE LA CARTA ──────────────────
    # La rueda principal muestra todos los aspectos calculados por el
    # motor. ``aspectos_relevantes`` se conserva como parámetro por
    # compatibilidad, pero no limita el dibujo.
    aspectos_dibujo = calcular_aspectos_figuras(
        carta["planetas"]
    )

    ASP_COLORES = {
        "□": "#CC2200",
        "☍": "#CC2200",
        "△": "#1A5FA8",
        "✶": "#1A5FA8",
        "⚺": "#2E7D32",
        "⚻": "#2E7D32",
        "=": "#7B2D8B",
    }

    R_ASP = R_CASA_IN - 0.02

    claves_relevantes = {
        (
            frozenset((asp.get("p1"), asp.get("p2"))),
            asp.get("simbolo"),
        ): len(asp.get("figuras") or [])
        for asp in (aspectos_relevantes or [])
    }

    for asp in aspectos_dibujo:

        sim = asp.get("simbolo")

        if sim not in ASP_COLORES:
            continue

        p1 = asp.get("p1")
        p2 = asp.get("p2")

        if (
            p1 not in carta["planetas"]
            or
            p2 not in carta["planetas"]
        ):
            continue

        numero_figuras = claves_relevantes.get(
            (frozenset((p1, p2)), sim),
            0,
        )

        # Se dibujan TODOS los aspectos. Los que además participan
        # en la arquitectura reconocida reciben más peso visual.
        if numero_figuras >= 2:
            linewidth = 2.2
            alpha = 0.85
        elif numero_figuras == 1:
            linewidth = 1.5
            alpha = 0.65
        else:
            linewidth = 0.8
            alpha = 0.32

        a1 = lon_a_angulo(
            carta["planetas"][p1]["lon"]
        )

        a2 = lon_a_angulo(
            carta["planetas"][p2]["lon"]
        )

        ax.plot(
            [
                math.cos(a1) * R_ASP,
                math.cos(a2) * R_ASP,
            ],
            [
                math.sin(a1) * R_ASP,
                math.sin(a2) * R_ASP,
            ],
            color=ASP_COLORES[sim],
            linewidth=linewidth,
            alpha=alpha,
            linestyle="solid",
            zorder=2,
        )

    # ── PLANETAS Y PUNTOS ───────────────────

    orden = [
        "Sol",
        "Luna",
        "Mercurio",
        "Venus",
        "Marte",
        "Júpiter",
        "Saturno",
        "Urano",
        "Neptuno",
        "Plutón",
        "Quirón",
        "Lilith",
        "Nodo Norte",
        "Nodo Sur",
        "Ascendente",
        "Medio Cielo",
    ]

    RADIO_MIN = R_CASA_IN + 0.08
    RADIO_MAX = R_SIGN_IN - 0.08
    RADIO_SEP = 0.08

    lones_usados = []
    radios = {}

    for nombre in orden:

        if nombre not in carta["planetas"]:
            continue

        if nombre in (
            "Ascendente",
            "Medio Cielo",
        ):
            continue

        lon = carta["planetas"][nombre]["lon"]
        radio = R_PLANETA

        for lp, rp in lones_usados:

            d = abs(lon - lp) % 360

            if d > 180:
                d = 360 - d

            if d < 8:
                candidato = (
                    rp - RADIO_SEP
                )

                if candidato < RADIO_MIN:
                    candidato = (
                        rp + RADIO_SEP
                    )

                radio = max(
                    RADIO_MIN,
                    min(
                        candidato,
                        RADIO_MAX,
                    ),
                )

                break

        lones_usados.append(
            (lon, radio)
        )

        radios[nombre] = radio

    for nombre in orden:

        if nombre not in carta["planetas"]:
            continue

        # AC y MC siguen existiendo en la carta
        # para calcular y dibujar sus aspectos,
        # pero no se muestran como puntos
        # adicionales dentro del anillo.
        if nombre in (
            "Ascendente",
            "Medio Cielo",
        ):
            continue

        p = carta["planetas"][nombre]

        ang = lon_a_angulo(
            p["lon"]
        )

        r = radios[nombre]

        color = COLORES_PLANETA.get(
            nombre,
            "#333",
        )

        simbolo = p["simbolo"]

        # ── PUNTO ORGANIZADOR ─────────────────

        organizador = next(
            (
                item
                for item in puntos_organizadores
                if item.get("punto") == nombre
            ),
            None,
        )

        if organizador:

            jerarquia = organizador.get(
                "jerarquia_global"
            )

            if jerarquia == "dominante":
                tamano = 520
                grosor = 2.2
                alpha_org = 0.85

            elif jerarquia == "relevante":
                tamano = 430
                grosor = 1.2
                alpha_org = 0.55

            else:
                tamano = None

            if tamano:

                ax.scatter(
                    [math.cos(ang) * r],
                    [math.sin(ang) * r],
                    s=tamano,
                    facecolors="none",
                    edgecolors=color,
                    linewidths=grosor,
                    alpha=alpha_org,
                    zorder=5,
                )

        x_planeta = math.cos(ang) * r
        y_planeta = math.sin(ang) * r

        ax.text(
            x_planeta,
            y_planeta,
            simbolo,
            ha="center",
            va="center",
            fontsize=17,
            color=color,
            fontweight="bold",
            zorder=6,
        )

        # Retrogradación visible en la rueda de arquitectura.
        # Usamos una R ASCII normal para máxima compatibilidad de fuente.
        if p.get("retrogrado"):
            ax.text(
                x_planeta + 0.035,
                y_planeta + 0.035,
                "R",
                ha="left",
                va="bottom",
                fontsize=8,
                color=color,
                fontweight="bold",
                zorder=7,
            )

        ax.plot(
            [
                math.cos(ang) * (r - 0.07),
                math.cos(ang)
                * (R_CASA_IN - 0.02),
            ],
            [
                math.sin(ang) * (r - 0.07),
                math.sin(ang)
                * (R_CASA_IN - 0.02),
            ],
            color=color,
            linewidth=0.5,
            alpha=0.5,
            zorder=3,
        )

        ax.plot(
            [
                math.cos(ang) * (r + 0.07),
                math.cos(ang)
                * (R_SIGN_IN + 0.01),
            ],
            [
                math.sin(ang) * (r + 0.07),
                math.sin(ang)
                * (R_SIGN_IN + 0.01),
            ],
            color=color,
            linewidth=0.8,
            alpha=0.8,
            zorder=3,
        )

    # ── EJES ────────────────────────────────

    for etiqueta, lon_pt, nombre_punto in [
        (
            "AC",
            carta["asc"]["lon"],
            "Ascendente",
        ),
        (
            "DC",
            (
                carta["asc"]["lon"]
                + 180
            ) % 360,
            None,
        ),
        (
            "MC",
            carta["mc"]["lon"],
            "Medio Cielo",
        ),
        (
            "IC",
            (
                carta["mc"]["lon"]
                + 180
            ) % 360,
            None,
        ),
    ]:

        ang = lon_a_angulo(lon_pt)

        organizador = None

        if nombre_punto:
            organizador = next(
                (
                    item
                    for item in puntos_organizadores
                    if item.get("punto")
                    == nombre_punto
                ),
                None,
            )

        if organizador:

            jerarquia = organizador.get(
                "jerarquia_global"
            )

            if jerarquia == "dominante":
                tamano_eje = 520
                grosor_eje = 2.6
                alpha_eje = 0.9

            elif jerarquia == "relevante":
                tamano_eje = 430
                grosor_eje = 1.4
                alpha_eje = 0.6

            else:
                tamano_eje = None

            if tamano_eje:

                r_etiqueta = (
                    R_EXT + 0.09
                )

                ax.scatter(
                    [
                        math.cos(ang)
                        * r_etiqueta
                    ],
                    [
                        math.sin(ang)
                        * r_etiqueta
                    ],
                    s=tamano_eje,
                    facecolors="none",
                    edgecolors="#333",
                    linewidths=grosor_eje,
                    alpha=alpha_eje,
                    zorder=6,
                )

        ax.text(
            math.cos(ang)
            * (R_EXT + 0.09),
            math.sin(ang)
            * (R_EXT + 0.09),
            etiqueta,
            ha="center",
            va="center",
            fontsize=13,
            fontweight="bold",
            color="#111",
            zorder=7,
        )

    # ── NOMBRE ──────────────────────────────

    ax.text(
        0,
        0,
        nombre_persona.replace(
            " ",
            "\n",
        ),
        ha="center",
        va="center",
        fontsize=8,
        color="#333",
        style="italic",
        zorder=7,
    )

    plt.title(
        f"Arquitectura natal — {nombre_persona}",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )

    plt.tight_layout()

    plt.savefig(
        archivo_salida,
        dpi=150,
        bbox_inches="tight",
        facecolor="white",
        edgecolor="none",
    )

    plt.close()

def obtener_aspectos_de_figura(
    figura,
    aspectos_relevantes,
):
    """
    Devuelve únicamente los aspectos que pertenecen
    a una figura concreta.

    Funciona para cualquier tipo de figura y
    cualquier carta natal.
    """

    tipo_figura = figura.get(
        "tipo"
    )

    puntos_figura = set(
        figura.get(
            "puntos",
            []
        )
    )

    aspectos_figura = []

    for aspecto in aspectos_relevantes:

        p1 = aspecto.get("p1")
        p2 = aspecto.get("p2")

        figuras_aspecto = (
            aspecto.get("figuras")
            or []
        )

        # Los dos extremos deben pertenecer
        # a esta figura.
        if (
            p1 not in puntos_figura
            or p2 not in puntos_figura
        ):
            continue

        # Además, el motor debe haber marcado
        # este aspecto como participante
        # de este tipo de figura.
        if tipo_figura not in figuras_aspecto:
            continue

        aspectos_figura.append(
            aspecto
        )

    return aspectos_figura

def dibujar_mini_figura(
    carta,
    figura,
    aspectos_relevantes,
    archivo_salida,
):
    """
    Genera una mini-rueda de una figura astrológica.

    La función es genérica:
    - sirve para cualquier carta;
    - sirve para cualquier figura detectada;
    - muestra solo los puntos que forman la figura;
    - muestra solo los aspectos pertenecientes
      a esa figura.

    No muestra el resto de aspectos de la carta.
    """

    puntos_figura = figura.get(
        "puntos",
        []
    )

    if not puntos_figura:
        raise ValueError(
            "La figura no contiene puntos."
        )

    aspectos_figura = (
        obtener_aspectos_de_figura(
            figura,
            aspectos_relevantes,
        )
    )

    fig, ax = plt.subplots(
        1,
        1,
        figsize=(5, 5),
    )

    ax.set_aspect("equal")
    ax.axis("off")

    ax.set_xlim(
        -1.42,
        1.42,
    )

    ax.set_ylim(
        -1.42,
        1.42,
    )

    R_EXT = 1.25
    R_SIGN_IN = 1.02
    R_PUNTO = 0.79
    R_ASP = 0.67

    asc_lon = carta["asc"]["lon"]

    def lon_a_angulo(lon):
        return math.radians(
            180 + (lon - asc_lon)
        )

    vertices_dibujo = figura.get("vertices") or [
        {
            "tipo": "Punto",
            "puntos": [punto],
        }
        for punto in puntos_figura
    ]
    datos_vertices = []
    angulos_puntos = {}

    for vertice in vertices_dibujo:
        miembros = [
            punto
            for punto in vertice.get("puntos", [])
            if punto in carta["planetas"]
        ]

        if not miembros:
            continue

        longitudes = [
            carta["planetas"][punto]["lon"]
            for punto in miembros
        ]
        seno_medio = sum(
            math.sin(math.radians(lon))
            for lon in longitudes
        ) / len(longitudes)
        coseno_medio = sum(
            math.cos(math.radians(lon))
            for lon in longitudes
        ) / len(longitudes)
        longitud_vertice = (
            math.degrees(
                math.atan2(seno_medio, coseno_medio)
            )
            % 360
        )
        angulo_vertice = lon_a_angulo(
            longitud_vertice
        )

        for punto in miembros:
            angulos_puntos[punto] = angulo_vertice

        datos_vertices.append({
            "tipo": vertice.get("tipo", "Punto"),
            "puntos": miembros,
            "angulo": angulo_vertice,
        })

    # ── ANILLO EXTERIOR ───────────────────────────────

    ax.add_patch(
        plt.Circle(
            (0, 0),
            R_EXT,
            fill=False,
            color="#444",
            linewidth=1.4,
            zorder=2,
        )
    )

    ax.add_patch(
        plt.Circle(
            (0, 0),
            R_SIGN_IN,
            fill=False,
            color="#777",
            linewidth=0.8,
            zorder=2,
        )
    )

    # ── SIGNOS ────────────────────────────────────────

    for i, signo in enumerate(SIGNOS):

        ang = lon_a_angulo(
            i * 30
        )

        ax.plot(
            [
                math.cos(ang) * R_SIGN_IN,
                math.cos(ang) * R_EXT,
            ],
            [
                math.sin(ang) * R_SIGN_IN,
                math.sin(ang) * R_EXT,
            ],
            color="#999",
            linewidth=0.45,
            alpha=0.8,
            zorder=1,
        )

        ang_mid = lon_a_angulo(
            i * 30 + 15
        )

        r_mid = (
            R_SIGN_IN + R_EXT
        ) / 2

        elem = ELEMENTO_SIGNO[
            signo
        ]

        ax.text(
            math.cos(ang_mid) * r_mid,
            math.sin(ang_mid) * r_mid,
            SIMBOLOS_SIGNOS[i],
            ha="center",
            va="center",
            fontsize=10,
            color=COLORES_ELEMENTO[
                elem
            ],
            fontweight="bold",
            zorder=5,
        )

    # ── COLORES DE ASPECTOS ───────────────────────────

    colores_aspectos = {
        "Cuadratura": "#CC2200",
        "Oposición": "#CC2200",
        "Trígono": "#1A5FA8",
        "Sextil": "#1A5FA8",
        "Semisextil": "#2E7D32",
        "Quincuncio": "#2E7D32",
        "Conjunción": "#7B2D8B",
    }

    # ── ASPECTOS DE ESTA FIGURA ───────────────────────

    for aspecto in aspectos_figura:

        p1 = aspecto.get(
            "p1"
        )

        p2 = aspecto.get(
            "p2"
        )

        if (
            p1 not in carta["planetas"]
            or
            p2 not in carta["planetas"]
        ):
            continue

        a1 = angulos_puntos.get(
            p1,
            lon_a_angulo(
                carta["planetas"][p1]["lon"]
            ),
        )

        a2 = angulos_puntos.get(
            p2,
            lon_a_angulo(
                carta["planetas"][p2]["lon"]
            ),
        )

        # Los aspectos internos de un stellium pertenecen al
        # contenido del vértice, no se dibujan como una arista.
        if abs(a1 - a2) < 1e-9:
            continue

        tipo = aspecto.get(
            "tipo",
            ""
        )

        color = colores_aspectos.get(
            tipo,
            "#555",
        )

        ax.plot(
            [
                math.cos(a1) * R_ASP,
                math.cos(a2) * R_ASP,
            ],
            [
                math.sin(a1) * R_ASP,
                math.sin(a2) * R_ASP,
            ],
            color=color,
            linewidth=1.5,
            alpha=0.85,
            zorder=3,
        )

    # ── PUNTOS QUE FORMAN LA FIGURA ───────────────────

    for vertice in datos_vertices:

        miembros = vertice["puntos"]
        ang = vertice["angulo"]
        es_colectivo = len(miembros) > 1

        if es_colectivo:
            color = "#7B2D8B"
            simbolos = []

            for nombre in miembros:
                punto = carta["planetas"][nombre]
                simbolo_miembro = punto.get("simbolo", nombre[:2])
                if punto.get("retrogrado"):
                    simbolo_miembro += "ᴿ"
                simbolos.append(simbolo_miembro)

            mitad = (len(simbolos) + 1) // 2
            simbolo = (
                " ".join(simbolos[:mitad])
                + "\n"
                + " ".join(simbolos[mitad:])
            ).strip()
            tamano_fuente = 7

        else:
            nombre = miembros[0]
            punto = carta["planetas"][nombre]
            color = COLORES_PLANETA.get(
                nombre,
                "#333",
            )

            if nombre == "Ascendente":
                simbolo = "AC"

            elif nombre == "Medio Cielo":
                simbolo = "MC"

            else:
                simbolo = punto.get(
                    "simbolo",
                    nombre[:2],
                )
                if punto.get("retrogrado"):
                    simbolo += "ᴿ"

            tamano_fuente = 10

        # Línea desde el punto hasta la figura.
        ax.plot(
            [
                math.cos(ang)
                * (R_PUNTO - 0.08),

                math.cos(ang)
                * R_ASP,
            ],
            [
                math.sin(ang)
                * (R_PUNTO - 0.08),

                math.sin(ang)
                * R_ASP,
            ],
            color=color,
            linewidth=0.7,
            alpha=0.6,
            zorder=2,
        )


        # Símbolo o abreviatura.
        ax.text(
            math.cos(ang)
            * R_PUNTO,

            math.sin(ang)
            * R_PUNTO,

            simbolo,

            ha="center",
            va="center",
            fontsize=tamano_fuente,
            color=color,
            fontweight="bold",
            zorder=6,
        )

    # ── GUARDADO ──────────────────────────────────────

    plt.tight_layout(
        pad=0.1
    )

    plt.savefig(
        archivo_salida,
        dpi=180,
        bbox_inches="tight",
        facecolor="white",
        edgecolor="none",
        pad_inches=0.05,
    )

    plt.close()

    return archivo_salida

def generar_miniaturas_figuras(
    carta,
    figuras,
    aspectos_relevantes,
    carpeta_salida,
):
    """
    Genera una miniatura PNG para cada figura detectada.

    Devuelve una lista con:
    - tipo de figura;
    - puntos;
    - ruta de la imagen.

    Funciona para cualquier carta.
    """

    os.makedirs(
        carpeta_salida,
        exist_ok=True,
    )

    miniaturas = []

    for indice, figura in enumerate(
        figuras,
        start=1,
    ):

        tipo = (
            figura.get("nombre_canonico")
            or figura.get("tipo", "Figura")
        )

        puntos = figura.get(
            "puntos",
            [],
        )

        if not puntos:
            continue

        nombre_seguro = re.sub(
            r"[^A-Za-z0-9_-]+",
            "_",
            tipo,
        ).strip("_")

        archivo_salida = os.path.join(
            carpeta_salida,
            (
                f"figura_{indice:02d}_"
                f"{nombre_seguro}.png"
            ),
        )

        dibujar_mini_figura(
            carta=carta,
            figura=figura,
            aspectos_relevantes=aspectos_relevantes,
            archivo_salida=archivo_salida,
        )

        miniaturas.append({
            "indice": indice,
            "tipo": tipo,
            "puntos": puntos,
            "ruta": archivo_salida,
        })

    return miniaturas


# ─── UTILIDADES PARA FIGURAS ─────────────────────────────────────────────────

ORDEN_PUNTOS = [
    "Sol", "Luna", "Mercurio", "Venus", "Marte",
    "Júpiter", "Saturno", "Urano", "Neptuno", "Plutón",
    "Quirón", "Lilith", "Nodo Norte", "Nodo Sur",
    "Ascendente", "Medio Cielo"
]

PESO_PUNTO = {
    "Sol": 5,
    "Luna": 5,
    "Ascendente": 5,
    "Medio Cielo": 5,

    "Mercurio": 4,
    "Venus": 4,
    "Marte": 4,

    "Júpiter": 3,
    "Saturno": 3,

    "Urano": 2,
    "Neptuno": 2,
    "Plutón": 2,

    "Quirón": 2,
    "Lilith": 2,

    "Nodo Norte": 2,
    "Nodo Sur": 2,
}


def ordenar_puntos(nombres):
    return sorted(
        nombres,
        key=lambda n: ORDEN_PUNTOS.index(n) if n in ORDEN_PUNTOS else 99
    )


def nombres_humanos(nombres):
    nombres = ordenar_puntos(nombres)

    if not nombres:
        return ""

    if len(nombres) == 1:
        return nombres[0]

    return ", ".join(nombres[:-1]) + " y " + nombres[-1]


def aspecto_entre(aspectos, p1, p2, simbolo=None):
    for asp in aspectos:
        mismo = (
            (asp["p1"] == p1 and asp["p2"] == p2)
            or
            (asp["p1"] == p2 and asp["p2"] == p1)
        )

        if not mismo:
            continue

        if simbolo is None or asp["simbolo"] == simbolo:
            return asp

    return None


def anotar_catalogo_y_dinamica(carta, figura):
    """Añade nombre, significado base y recorrido verificable a una figura."""
    datos = CATALOGO_FIGURAS.get(figura.get("tipo", ""), {})

    for clave, valor in datos.items():
        figura.setdefault(clave, valor)

    if figura.get("familia") not in (
        "aprendizaje",
        "aprendizaje y transformación",
    ):
        return figura

    por_simbolo = {
        aspecto.get("simbolo"): aspecto
        for aspecto in figura.get("aspectos", [])
    }
    rojo = por_simbolo.get("□")
    verde = por_simbolo.get("⚺") or por_simbolo.get("⚻")
    azul = por_simbolo.get("✶") or por_simbolo.get("△")

    if not rojo or not verde or not azul:
        return figura

    extremos_rojo = {rojo.get("p1"), rojo.get("p2")}
    extremos_verde = {verde.get("p1"), verde.get("p2")}
    extremos_azul = {azul.get("p1"), azul.get("p2")}
    inicio = next(iter(extremos_rojo & extremos_azul), None)

    if not inicio:
        return figura

    despues_rojo = next(iter(extremos_rojo - {inicio}), None)

    if despues_rojo not in extremos_verde:
        return figura

    despues_verde = next(
        iter(extremos_verde - {despues_rojo}),
        None,
    )

    if not despues_rojo or not despues_verde:
        return figura

    planetas = carta.get("planetas", {})

    if inicio not in planetas or despues_rojo not in planetas:
        return figura

    avance_zodiacal = (
        planetas[despues_rojo]["lon"]
        - planetas[inicio]["lon"]
    ) % 360
    directo = 0 < avance_zodiacal < 180
    figura["secuencia_crecimiento"] = {
        "fases": [
            {
                "aspecto": rojo.get("nombre", "Cuadratura"),
                "funcion": "conflicto, tensión o necesidad de actuar",
                "desde": inicio,
                "hasta": despues_rojo,
            },
            {
                "aspecto": verde.get("nombre", "Aspecto verde"),
                "funcion": "búsqueda, elaboración y ampliación de consciencia",
                "desde": despues_rojo,
                "hasta": despues_verde,
            },
            {
                "aspecto": azul.get("nombre", "Aspecto azul"),
                "funcion": "integración, capacidad o nuevo equilibrio",
                "desde": despues_verde,
                "hasta": inicio,
            },
        ],
        "orden": "rojo → verde → azul",
        "sentido": "antihorario" if directo else "horario",
        "variante": (
            "reconocimiento_directo"
            if directo
            else "experiencia_retrograda"
        ),
    }

    return figura


def puntuacion_figura(puntos):
    return sum(PESO_PUNTO.get(p, 1) for p in puntos)


def casas_de_puntos(carta, puntos):
    planetas = carta["planetas"]

    casas = []
    for p in puntos:
        if p in planetas and planetas[p].get("casa"):
            casas.append(planetas[p]["casa"])

    return sorted(set(casas))


def signos_de_puntos(carta, puntos):
    planetas = carta["planetas"]

    signos = []
    for p in puntos:
        if p in planetas and planetas[p].get("signo"):
            signos.append(planetas[p]["signo"])

    return sorted(set(signos), key=lambda s: SIGNOS.index(s) if s in SIGNOS else 99)


def descripcion_casas(casas):
    if not casas:
        return ""

    if len(casas) == 1:
        return f"Casa {casas[0]}"

    return "Casas " + ", ".join(str(c) for c in casas)


def descripcion_signos(signos):
    if not signos:
        return ""

    if len(signos) == 1:
        return signos[0]

    return ", ".join(signos[:-1]) + " y " + signos[-1]


# ─── ESCAPADO LATEX ───────────────────────────────────────────────────────────

def esc(texto):
    if texto is None:
        return ""

    texto = str(texto)

    for orig, repl in [
        ('\\', r'\textbackslash{}'),
        ('&', r'\&'),
        ('%', r'\%'),
        ('$', r'\$'),
        ('#', r'\#'),
        ('_', r'\_'),
        ('{', r'\{'),
        ('}', r'\}'),
        ('~', r'\textasciitilde{}'),
        ('^', r'\textasciicircum{}'),
    ]:
        texto = texto.replace(orig, repl)

    return texto

# ─── DETECCIÓN DE FIGURAS ────────────────────────────────────────────────────


# ─── PATRONES GEOMÉTRICOS HUBER — FASE 2 ─────────────────────────────────────

ASPECTO_POR_PASOS_HUBER = {
    0: "=",
    1: "⚺",
    2: "✶",
    3: "□",
    4: "△",
    5: "⚻",
    6: "☍",
}

PATRONES_HUBER_FASE2 = {
    "Cuadrado de rendimiento": {
        "pasos": [0, 3, 6, 9],
    },
    "Triángulo de talento pequeño": {
        "pasos": [0, 2, 4],
    },
    "Triángulo de ambivalencia": {
        "pasos": [0, 2, 6],
    },
    "Figura de ambivalencia doble": {
        "pasos": [0, 3, 6, 10],
        "pares_opcionales": {(1, 3)},
    },
    "Rectángulo de rectitud": {
        "pasos": [0, 2, 6, 8],
    },
    "Cuna": {
        "pasos": [0, 2, 4, 6],
    },
    "Triángulo de excitación": {
        "pasos": [0, 1, 6],
    },
    "Rectángulo de excitación": {
        "pasos": [0, 1, 6, 7],
    },
    "Figura de búsqueda": {
        "pasos": [0, 1, 5],
    },
    "Trapecio": {
        "pasos": [0, 3, 5, 8],
    },
    "Figura de aspiración": {
        "pasos": [0, 5, 6, 7],
    },
}

def _distancia_pasos_huber(a, b):
    diferencia = abs(a - b) % 12
    return min(diferencia, 12 - diferencia)

def _simbolo_esperado_huber(paso_a, paso_b):
    return ASPECTO_POR_PASOS_HUBER[
        _distancia_pasos_huber(paso_a, paso_b)
    ]

def _firma_patron_huber(pasos):
    firma = []
    for i in range(len(pasos)):
        for j in range(i + 1, len(pasos)):
            firma.append(
                (
                    i,
                    j,
                    _simbolo_esperado_huber(
                        pasos[i],
                        pasos[j],
                    ),
                )
            )
    return firma


def _distancia_circular_grados_huber(a, b):
    d = abs((a - b) % 360.0)
    return min(d, 360.0 - d)


def _asignacion_respeta_geometria_huber(carta, asignacion, pasos, nombre_figura=None, tolerancia=12.0):
    planetas = carta.get("planetas", {})

    try:
        longitudes = [float(planetas[punto]["lon"]) for punto in asignacion]
    except (KeyError, TypeError, ValueError):
        return False

    if len(longitudes) != len(pasos):
        return False

    # Trampolín y Deco son geometrías quirales entre sí:
    # una es la imagen especular de la otra. En estos dos
    # nombres el espejo NO es equivalente; sólo admitimos
    # rotaciones de la orientación catalogada.
    if nombre_figura in ('Trampolín', 'Deco'):
        sentidos = (1,)
    else:
        sentidos = (1, -1)

    for sentido in sentidos:
        valida = True

        for i in range(len(pasos)):
            for j in range(i + 1, len(pasos)):
                delta_real = (longitudes[j] - longitudes[i]) % 360.0
                delta_esperado = (
                    sentido * (pasos[j] - pasos[i]) * 30.0
                ) % 360.0

                diferencia = abs((delta_real - delta_esperado) % 360.0)
                diferencia = min(diferencia, 360.0 - diferencia)

                if diferencia > tolerancia:
                    valida = False
                    break

            if not valida:
                break

        if valida:
            return True

    return False


def detectar_patron_huber(
    carta,
    aspectos,
    nombre_figura,
    pasos,
    pares_opcionales=None,
):
    from itertools import combinations, permutations

    pares_opcionales = set(
        pares_opcionales or set()
    )

    puntos_disponibles = [
        punto
        for punto in ORDEN_PUNTOS
        if punto in carta.get("planetas", {})
    ]

    numero_vertices = len(pasos)
    firma = _firma_patron_huber(pasos)

    figuras = []
    vistas = set()

    for seleccion in combinations(
        puntos_disponibles,
        numero_vertices,
    ):
        encontrada_para_seleccion = None

        for asignacion in permutations(seleccion):
            if not _asignacion_respeta_geometria_huber(
                carta,
                asignacion,
                pasos,
                nombre_figura=nombre_figura,
            ):
                continue

            aspectos_figura = []
            valida = True

            for i, j, simbolo in firma:
                p1 = asignacion[i]
                p2 = asignacion[j]
                par_indices = (i, j)

                if (
                    simbolo == "☍"
                    and {p1, p2}
                    == {"Nodo Norte", "Nodo Sur"}
                ):
                    valida = False
                    break

                aspecto = aspecto_entre(
                    aspectos,
                    p1,
                    p2,
                    simbolo,
                )

                if aspecto is None:
                    if par_indices in pares_opcionales:
                        continue

                    valida = False
                    break

                aspectos_figura.append(aspecto)

            if not valida:
                continue

            puntos_reales = ordenar_puntos(
                list(seleccion)
            )
            clave = (
                nombre_figura,
                tuple(puntos_reales),
            )

            if clave in vistas:
                break

            vistas.add(clave)

            # La figura conserva exclusivamente sus vértices geométricos
            # reales. Un stellium no se expande automáticamente por compartir
            # uno de sus miembros; las figuras compuestas tienen detectores
            # específicos cuando un vértice colectivo es realmente necesario.
            puntos_geometricos = puntos_reales

            figura = {
                "tipo": nombre_figura,
                "puntos": puntos_geometricos,
                "aspectos": aspectos_figura,
                "peso": puntuacion_figura(
                    puntos_geometricos
                ),
                "patron_huber_pasos": list(pasos),
                "vertices_huber": [
                    {
                        "indice": indice,
                        "paso": pasos[indice],
                        "punto": asignacion[indice],
                    }
                    for indice in range(numero_vertices)
                ],
            }

            if nombre_figura == "Figura de ambivalencia doble":
                figura["quincuncio_diagonal_presente"] = any(
                    aspecto.get("simbolo") == "⚻"
                    for aspecto in aspectos_figura
                )

            encontrada_para_seleccion = figura
            break

        if encontrada_para_seleccion:
            figuras.append(
                encontrada_para_seleccion
            )

    return sorted(
        figuras,
        key=lambda figura: -figura.get("peso", 0),
    )

def detectar_figuras_huber_fase2(carta, aspectos):
    figuras = []

    for nombre, datos in PATRONES_HUBER_FASE2.items():
        figuras.extend(
            detectar_patron_huber(
                carta=carta,
                aspectos=aspectos,
                nombre_figura=nombre,
                pasos=datos["pasos"],
                pares_opcionales=datos.get(
                    "pares_opcionales"
                ),
            )
        )

    return figuras



# ─── HUBER FASE 3: 26 VARIANTES / COMBINACIONES ─────────────────────────────
CATALOGO_HUBER_VARIANTES_26 = {'Caja de Pandora': {'grupo': 'diez_variantes', 'pagina': 349, 'vertices': 5}, 'Bañera': {'grupo': 'diez_variantes', 'pagina': 352, 'vertices': 4}, 'Mariposa': {'grupo': 'diez_variantes', 'pagina': 354, 'vertices': 4}, 'Nasa': {'grupo': 'diez_variantes', 'pagina': 355, 'vertices': 4}, 'Trampolín': {'grupo': 'diez_variantes', 'pagina': 356, 'vertices': 4}, 'Corredor (saltador)': {'grupo': 'diez_variantes', 'pagina': 358, 'vertices': 4}, 'Telescopio-Microscopio': {'grupo': 'diez_variantes', 'pagina': 359, 'vertices': 4}, 'Amortiguador': {'grupo': 'diez_variantes', 'pagina': 361, 'vertices': 4}, 'Escudo': {'grupo': 'diez_variantes', 'pagina': 362, 'vertices': 4}, 'Diamante': {'grupo': 'diez_variantes', 'pagina': 363, 'vertices': '8+'}, 'Megáfono': {'grupo': 'cuadrangulares_con_oposicion', 'pagina': 373, 'vertices': 4}, 'Animat': {'grupo': 'cuadrangulares_con_oposicion', 'pagina': 374, 'vertices': 4}, 'Provocat': {'grupo': 'cuadrangulares_con_oposicion', 'pagina': 376, 'vertices': 4}, 'Arena': {'grupo': 'cuadrangulares_con_oposicion', 'pagina': 378, 'vertices': 4}, 'Canalizador': {'grupo': 'cuadrangulares_con_oposicion', 'pagina': 379, 'vertices': 4}, 'Deco': {'grupo': 'cuadrangulares_con_oposicion', 'pagina': 381, 'vertices': 4}, 'Bijou': {'grupo': 'cuadrangulares_con_oposicion', 'pagina': 383, 'vertices': 4}, 'Detect': {'grupo': 'trapezoides_con_talento', 'pagina': 386, 'vertices': 4}, 'Grabadora': {'grupo': 'trapezoides_con_talento', 'pagina': 388, 'vertices': 4}, 'Model': {'grupo': 'trapezoides_con_talento', 'pagina': 390, 'vertices': 4}, 'Represent': {'grupo': 'trapezoides_con_talento', 'pagina': 392, 'vertices': 4}, 'Escenario': {'grupo': 'cuadrangulares_poco_comunes', 'pagina': 396, 'vertices': 4}, 'Gorro mágico': {'grupo': 'cuadrangulares_poco_comunes', 'pagina': 398, 'vertices': 4}, 'Ovni': {'grupo': 'cuadrangulares_poco_comunes', 'pagina': 401, 'vertices': 4}, 'Surfista': {'grupo': 'cuadrangulares_poco_comunes', 'pagina': 403, 'vertices': 4}, 'Oscilo': {'grupo': 'cuadrangulares_poco_comunes', 'pagina': 405, 'vertices': 4}}
PATRONES_HUBER_VARIANTES_COMPLETAS = {'Bañera': [3, 5, 8, 10], 'Nasa': [2, 3, 7, 10], 'Trampolín': [3, 5, 8, 9], 'Telescopio-Microscopio': [1, 4, 5, 8], 'Escudo': [6, 7, 9, 10], 'Megáfono': [1, 2, 3, 9], 'Animat': [0, 1, 3, 9], 'Provocat': [0, 2, 3, 9], 'Arena': [0, 3, 4, 9], 'Canalizador': [3, 8, 9, 11], 'Deco': [1, 3, 9, 10], 'Bijou': [1, 3, 8, 9], 'Detect': [3, 5, 6, 7], 'Grabadora': [3, 4, 6, 8], 'Model': [1, 3, 5, 8], 'Represent': [0, 1, 4, 8], 'Escenario': [3, 4, 8, 9], 'Gorro mágico': [0, 1, 10, 11], 'Ovni': [0, 2, 9, 11], 'Surfista': [2, 5, 6, 7], 'Oscilo': [1, 5, 6, 8]}
PATRONES_HUBER_VARIANTES_LINEALES = {'Mariposa': {'pasos': [0, 4, 7, 11], 'aristas': [(0, 1, '△'), (0, 2, '⚻'), (3, 1, '⚻'), (3, 2, '△')], 'ausentes': [(0, 3), (1, 2)]}, 'Corredor (saltador)': {'pasos': [1, 2, 5, 10], 'aristas': [(3, 0, '□'), (1, 2, '□'), (3, 1, '△'), (0, 2, '△')], 'ausentes': [(0, 1), (2, 3)]}, 'Amortiguador': {'pasos': [6, 7, 9, 10], 'aristas': [(3, 1, '□'), (2, 0, '□'), (3, 0, '△'), (2, 1, '✶')], 'ausentes': [(0, 1), (2, 3)]}}

def detectar_figura_lineal_huber(carta, aspectos, nombre_figura, datos):
    from itertools import combinations, permutations
    puntos = [p for p in ORDEN_PUNTOS if p in carta.get('planetas', {})]
    figuras, vistas = [], set()
    for seleccion in combinations(puntos, 4):
        encontrada = None
        for asignacion in permutations(seleccion):
            ars, valida = [], True
            for i, j, simbolo in datos['aristas']:
                p1, p2 = asignacion[i], asignacion[j]
                if simbolo == '☍' and {p1,p2} == {'Nodo Norte','Nodo Sur'}:
                    valida = False; break
                asp = aspecto_entre(aspectos, p1, p2, simbolo)
                if asp is None:
                    valida = False; break
                ars.append(asp)
            if not valida:
                continue
            for i, j in datos['ausentes']:
                if aspecto_entre(aspectos, asignacion[i], asignacion[j]) is not None:
                    valida = False; break
            if not valida:
                continue
            reales = ordenar_puntos(list(seleccion))
            clave = (nombre_figura, tuple(reales))
            if clave in vistas:
                break
            vistas.add(clave)
            encontrada = {
                'tipo': nombre_figura,
                'sistema': 'Huber',
                'nivel_catalogo': 'variante',
                'puntos': reales,
                'aspectos': ars,
                'peso': puntuacion_figura(reales),
                'figura_completa': False,
                'figura_lineal': True,
                'criterio_detector': 'topologia_lineal_huber',
            }
            break
        if encontrada:
            figuras.append(encontrada)
    return figuras


def detectar_caja_pandora(carta, aspectos):
    """
    Detecta la Caja de Pandora por su GEOMETRÍA HUBER exacta.

    La figura de referencia tiene cinco vértices con pasos zodiacales
    equivalentes a [0, 2, 5, 7, 10] (admite rotación y espejo):

        - tapa azul:
            0-2  sextil
            0-10 sextil
            2-10 trígono
        - base azul:
            5-7 sextil
        - laterales rojos:
            2-5  cuadratura
            7-10 cuadratura
        - interior verde:
            0-5  quincuncio
            0-7  quincuncio
            2-7  quincuncio
            5-10 quincuncio

    Por tanto, NO basta con contar colores.
    Deben existir las DIEZ relaciones del pentágono con esta topología
    y la distribución angular debe corresponder al patrón Huber.
    """
    patron = [0, 2, 5, 7, 10]

    figuras = detectar_patron_huber(
        carta=carta,
        aspectos=aspectos,
        nombre_figura="Caja de Pandora",
        pasos=patron,
    )

    for figura in figuras:
        figura["sistema"] = "Huber"
        figura["nivel_catalogo"] = "variante"
        figura["figura_completa"] = True
        figura["criterio_detector"] = "topologia_geometrica_huber_pandora_v3"
        figura["patron_huber_pasos"] = list(patron)
        figura["numero_relaciones_esperadas"] = 10

    return figuras


HUBER_FASE11_DIAMANTE_ESTRICTO = True

PUNTOS_DIAMANTE_HUBER = (
    "Sol", "Luna", "Mercurio", "Venus", "Marte",
    "Júpiter", "Saturno", "Urano", "Neptuno", "Plutón",
    "Nodo Norte",
)


def detectar_diamantes_huber(carta, aspectos):
    import itertools

    puntos_disponibles = set((carta.get("planetas") or {}).keys())
    candidatos = [
        p for p in PUNTOS_DIAMANTE_HUBER
        if p in puntos_disponibles
    ]

    if len(candidatos) < 8:
        return []

    simbolos_linea = {"⚺", "✶", "□", "△", "⚻", "☍"}
    arista_por_par = {}

    for aspecto in aspectos:
        p1 = aspecto.get("p1")
        p2 = aspecto.get("p2")
        simbolo = aspecto.get("simbolo")

        if p1 not in PUNTOS_DIAMANTE_HUBER or p2 not in PUNTOS_DIAMANTE_HUBER:
            continue
        if p1 == p2:
            continue
        if simbolo not in simbolos_linea:
            continue

        arista_por_par.setdefault(frozenset((p1, p2)), aspecto)

    def es_clique(puntos):
        return all(
            frozenset((p1, p2)) in arista_por_par
            for p1, p2 in itertools.combinations(puntos, 2)
        )

    cliques = []

    for n in range(len(candidatos), 7, -1):
        for combinacion in itertools.combinations(candidatos, n):
            conjunto = set(combinacion)

            if any(conjunto < existente for existente in cliques):
                continue

            if es_clique(combinacion):
                cliques.append(conjunto)

    figuras = []

    for conjunto in cliques:
        puntos = ordenar_puntos(list(conjunto))
        aspectos_figura = []

        for p1, p2 in itertools.combinations(puntos, 2):
            aspectos_figura.append(
                arista_por_par[frozenset((p1, p2))]
            )

        n = len(puntos)
        esperadas = n * (n - 1) // 2

        if len(aspectos_figura) != esperadas:
            continue

        figuras.append({
            "tipo": "Diamante",
            "sistema": "Huber",
            "nivel_catalogo": "variante",
            "puntos": puntos,
            "aspectos": aspectos_figura,
            "peso": puntuacion_figura(puntos),
            "numero_angulos": n,
            "numero_relaciones": len(aspectos_figura),
            "relaciones_esperadas": esperadas,
            "figura_completa": True,
            "criterio_diamante": "clique_completa_huber",
        })

    return sorted(
        figuras,
        key=lambda f: (-f.get("numero_angulos", 0), -f.get("peso", 0)),
    )

def detectar_figuras_huber_fase3(carta, aspectos):
    figuras=[]
    for nombre,pasos in PATRONES_HUBER_VARIANTES_COMPLETAS.items():
        nuevas=detectar_patron_huber(carta,aspectos,nombre,pasos)
        for f in nuevas:
            f['sistema']='Huber'; f['nivel_catalogo']='variante'; f['figura_completa']=True
        figuras.extend(nuevas)
    for nombre,datos in PATRONES_HUBER_VARIANTES_LINEALES.items():
        figuras.extend(detectar_figura_lineal_huber(carta,aspectos,nombre,datos))
    figuras.extend(detectar_caja_pandora(carta,aspectos))
    figuras.extend(detectar_diamantes_huber(carta,aspectos))
    unicas={}
    for f in figuras:
        clave=(f.get('tipo',''),tuple(puntos_reales_figura(f)))
        unicas.setdefault(clave,f)
    return list(unicas.values())


def detectar_stelliums(carta):
    planetas = carta["planetas"]
    excluir = {"Ascendente", "Medio Cielo"}

    puntos_base = [
        "Sol", "Luna", "Mercurio", "Venus", "Marte",
        "Júpiter", "Saturno", "Urano", "Neptuno", "Plutón",
        "Quirón", "Lilith", "Nodo Norte", "Nodo Sur"
    ]

    puntos = [
        p for p in puntos_base
        if p in planetas and p not in excluir
    ]

    if not puntos:
        return []

    # Un stellium se construye mediante conjunciones reales
    # calculadas por el motor. La mera proximidad dentro de una
    # cadena de 12 grados no basta para incluir un punto.
    aspectos_calculados = calcular_aspectos_figuras(
        planetas
    )

    puntos_validos = set(puntos)

    vecinos = {
        punto: set()
        for punto in puntos
    }

    for aspecto in aspectos_calculados:

        if aspecto.get("simbolo") != "=":
            continue

        p1 = aspecto.get("p1")
        p2 = aspecto.get("p2")

        if (
            p1 not in puntos_validos
            or p2 not in puntos_validos
        ):
            continue

        vecinos[p1].add(p2)
        vecinos[p2].add(p1)

    grupos = []
    visitados = set()

    for punto in puntos:

        if punto in visitados:
            continue

        pendientes = [punto]
        grupo = []

        while pendientes:

            actual = pendientes.pop()

            if actual in visitados:
                continue

            visitados.add(actual)
            grupo.append(actual)

            pendientes.extend(
                vecinos.get(actual, set())
                - visitados
            )

        grupos.append(grupo)

    figuras = []

    vistos = set()

    for grupo in grupos:
        grupo_unico = []
        for p in grupo:
            if p not in grupo_unico:
                grupo_unico.append(p)

        if len(grupo_unico) < 3:
            continue

        clave = tuple(sorted(grupo_unico))
        if clave in vistos:
            continue

        vistos.add(clave)

        grupo_ord = ordenar_puntos(grupo_unico)
        casas = casas_de_puntos(carta, grupo_ord)
        signos = signos_de_puntos(carta, grupo_ord)

        longitudes = sorted(
            planetas[p]["lon"]
            for p in grupo_ord
        )

        # Amplitud mínima sobre el círculo zodiacal.
        # Esto también funciona si el stellium cruza 0° Aries.
        if len(longitudes) >= 2:
            huecos = []

            for i in range(len(longitudes) - 1):
                huecos.append(
                    longitudes[i + 1] - longitudes[i]
                )

            huecos.append(
                (longitudes[0] + 360) - longitudes[-1]
            )

            hueco_mayor = max(huecos)
            amplitud = 360 - hueco_mayor

        else:
            amplitud = 0.0

        figuras.append({
            "tipo": "Stellium",
            "puntos": grupo_ord,
            "casa": casas[0] if casas else "",
            "casas": casas,
            "signos": signos,
            "peso": puntuacion_figura(grupo_ord),

            # Anchura real ocupada por el stellium
            "amplitud": round(amplitud, 2),
        })

    return sorted(figuras, key=lambda f: (-len(f["puntos"]), -f["peso"]))

def mapa_stelliums(carta):
    stelliums = detectar_stelliums(carta)
    mapa = {}

    for st in stelliums:
        for p in st["puntos"]:
            mapa[p] = st["puntos"]

    return mapa


def expandir_por_stellium(carta, puntos):
    mapa = mapa_stelliums(carta)
    expandidos = []

    for p in puntos:
        if p in mapa:
            expandidos.extend(mapa[p])
        else:
            expandidos.append(p)

    return ordenar_puntos(list(dict.fromkeys(expandidos)))


def detectar_t_cuadradas(carta, aspectos):
    puntos = ORDEN_PUNTOS
    figuras = []
    vistas = set()

    for a in puntos:
        for b in puntos:
            if b == a:
                continue

            # El eje Nodo Norte–Nodo Sur es una oposición por definición.
	    # No debe generar una T-cuadrada planetaria "normal".
            if {a, b} == {"Nodo Norte", "Nodo Sur"}:
                continue

            oposicion = aspecto_entre(aspectos, a, b, "☍")
            if not oposicion:
                continue

            for c in puntos:
                if c in (a, b):
                    continue

                cuad1 = aspecto_entre(aspectos, c, a, "□")
                cuad2 = aspecto_entre(aspectos, c, b, "□")

                if cuad1 and cuad2:
                    puntos_exp = ordenar_puntos([a, b, c])
                    clave = tuple(sorted(puntos_exp))

                    if clave in vistas:
                        continue

                    vistas.add(clave)

                    figuras.append({
                        "tipo": "T-cuadrada",
                        "oposicion": (a, b),
                        "apice": c,
                        "puntos": puntos_exp,
                        "aspectos": [oposicion, cuad1, cuad2],
                        "peso": puntuacion_figura(puntos_exp),
                    })

    return sorted(figuras, key=lambda f: -f["peso"])


def aspectos_entre_grupos(aspectos, grupo_1, grupo_2, simbolo):
    """Devuelve los aspectos de un tipo que conectan dos vértices colectivos."""
    conjunto_1 = set(grupo_1)
    conjunto_2 = set(grupo_2)

    return [
        aspecto
        for aspecto in aspectos
        if aspecto.get("simbolo") == simbolo
        and (
            (
                aspecto.get("p1") in conjunto_1
                and aspecto.get("p2") in conjunto_2
            )
            or (
                aspecto.get("p2") in conjunto_1
                and aspecto.get("p1") in conjunto_2
            )
        )
        and {
            aspecto.get("p1"),
            aspecto.get("p2"),
        } != {"Nodo Norte", "Nodo Sur"}
    ]


def detectar_t_cuadradas_con_stellium(carta, aspectos):
    """
    Detecta T-cuadradas cuyo vértice o polo funciona como concentración.

    En un stellium, la oposición puede recaer sobre uno de sus miembros
    y la cuadratura sobre otro. Geométricamente ambos pertenecen al mismo
    vértice colectivo, aunque no exista una T-cuadrada atómica formada
    por un único planeta del grupo.
    """
    stelliums = detectar_stelliums(carta)

    if not stelliums:
        return []

    grupos_stellium = [
        tuple(stellium.get("puntos", []))
        for stellium in stelliums
        if len(stellium.get("puntos", [])) >= 3
    ]
    puntos_agrupados = {
        punto
        for grupo in grupos_stellium
        for punto in grupo
    }
    vertices = grupos_stellium + [
        (punto,)
        for punto in ORDEN_PUNTOS
        if punto not in puntos_agrupados
    ]
    figuras = []
    vistas = set()

    for i in range(len(vertices)):
        for j in range(i + 1, len(vertices)):
            polo_1 = vertices[i]
            polo_2 = vertices[j]
            oposiciones = aspectos_entre_grupos(
                aspectos,
                polo_1,
                polo_2,
                "☍",
            )

            if not oposiciones:
                continue

            for k, apice in enumerate(vertices):
                if k in (i, j):
                    continue

                cuadrados_1 = aspectos_entre_grupos(
                    aspectos,
                    apice,
                    polo_1,
                    "□",
                )
                cuadrados_2 = aspectos_entre_grupos(
                    aspectos,
                    apice,
                    polo_2,
                    "□",
                )

                if not cuadrados_1 or not cuadrados_2:
                    continue

                # Si una misma oposición real ya recibe las dos
                # cuadraturas desde un mismo punto del ápice, la
                # T-cuadrada ordinaria ya representa esta geometría.
                # Aquí solo añadimos el cierre que depende de tratar
                # una concentración como vértice colectivo.
                existe_t_atomica = any(
                    aspecto_entre(
                        aspectos,
                        punto_apice,
                        oposicion.get("p1"),
                        "□",
                    )
                    and aspecto_entre(
                        aspectos,
                        punto_apice,
                        oposicion.get("p2"),
                        "□",
                    )
                    for oposicion in oposiciones
                    for punto_apice in apice
                )

                if existe_t_atomica:
                    continue

                # Esta función solo añade la geometría colectiva;
                # las T-cuadradas de tres puntos ya se detectan antes.
                if all(
                    len(grupo) == 1
                    for grupo in (polo_1, polo_2, apice)
                ):
                    continue

                puntos = ordenar_puntos(
                    list(dict.fromkeys(
                        list(polo_1)
                        + list(polo_2)
                        + list(apice)
                    ))
                )
                clave = (
                    tuple(sorted(polo_1)),
                    tuple(sorted(polo_2)),
                    tuple(sorted(apice)),
                )

                if clave in vistas:
                    continue

                vistas.add(clave)
                aspectos_figura = []
                claves_aspectos = set()

                for aspecto in (
                    oposiciones
                    + cuadrados_1
                    + cuadrados_2
                ):
                    clave_aspecto_actual = clave_aspecto(aspecto)

                    if clave_aspecto_actual in claves_aspectos:
                        continue

                    claves_aspectos.add(clave_aspecto_actual)
                    aspectos_figura.append(aspecto)

                figuras.append({
                    "tipo": "T-cuadrada compuesta",
                    "oposicion": (
                        ordenar_puntos(list(polo_1)),
                        ordenar_puntos(list(polo_2)),
                    ),
                    "apice": ordenar_puntos(list(apice)),
                    "puntos": puntos,
                    "aspectos": aspectos_figura,
                    "vertices_colectivos": True,
                    "vertices": [
                        {
                            "tipo": (
                                "Stellium"
                                if len(polo_1) > 1
                                else "Punto"
                            ),
                            "puntos": ordenar_puntos(list(polo_1)),
                        },
                        {
                            "tipo": (
                                "Stellium"
                                if len(polo_2) > 1
                                else "Punto"
                            ),
                            "puntos": ordenar_puntos(list(polo_2)),
                        },
                        {
                            "tipo": (
                                "Stellium"
                                if len(apice) > 1
                                else "Punto"
                            ),
                            "puntos": ordenar_puntos(list(apice)),
                        },
                    ],
                    "componentes": [
                        {
                            "tipo": "Polo colectivo",
                            "puntos": ordenar_puntos(list(polo_1)),
                        },
                        {
                            "tipo": "Polo colectivo",
                            "puntos": ordenar_puntos(list(polo_2)),
                        },
                        {
                            "tipo": "Ápice colectivo",
                            "puntos": ordenar_puntos(list(apice)),
                        },
                    ],
                    "relacion_componentes": (
                        "La oposición y las dos cuadraturas se cierran "
                        "entre vértices colectivos de la carta."
                    ),
                    "peso": puntuacion_figura(puntos),
                })

    return sorted(figuras, key=lambda f: -f["peso"])


def detectar_grandes_trigonos(carta, aspectos):
    puntos = ORDEN_PUNTOS
    figuras = []
    vistas = set()

    for i in range(len(puntos)):
        for j in range(i + 1, len(puntos)):
            for k in range(j + 1, len(puntos)):
                a, b, c = puntos[i], puntos[j], puntos[k]

                t1 = aspecto_entre(aspectos, a, b, "△")
                t2 = aspecto_entre(aspectos, a, c, "△")
                t3 = aspecto_entre(aspectos, b, c, "△")

                if t1 and t2 and t3:
                    puntos_exp = ordenar_puntos([a, b, c])
                    clave = tuple(sorted(puntos_exp))

                    if clave in vistas:
                        continue

                    vistas.add(clave)

                    figuras.append({
                        "tipo": "Gran trígono",
                        "puntos": puntos_exp,
                        "aspectos": [t1, t2, t3],
                        "peso": puntuacion_figura(puntos_exp),
                    })

    return sorted(figuras, key=lambda f: -f["peso"])


def detectar_cometas(carta, aspectos):
    grandes = detectar_grandes_trigonos(carta, aspectos)
    puntos = ORDEN_PUNTOS
    figuras = []
    vistas = set()

    for gt in grandes:
        # Base real del gran trígono antes de expansión por stellium
        base_real = []

        for asp in gt.get("aspectos", []):
            base_real.extend([asp["p1"], asp["p2"]])

        base_real = ordenar_puntos(list(dict.fromkeys(base_real)))

        if len(base_real) != 3:
            continue

        for foco in puntos:
            if foco in base_real:
                continue

            oposiciones = [
                p for p in base_real
                if aspecto_entre(aspectos, foco, p, "☍")
            ]

            if len(oposiciones) != 1:
                continue

            punto_opuesto = oposiciones[0]
            otros = [p for p in base_real if p != punto_opuesto]

            if len(otros) != 2:
                continue

            sex1 = aspecto_entre(aspectos, foco, otros[0], "✶")
            sex2 = aspecto_entre(aspectos, foco, otros[1], "✶")

            if sex1 and sex2:
                puntos_exp = ordenar_puntos(base_real + [foco])
                clave = tuple(sorted(puntos_exp))

                if clave in vistas:
                    continue

                vistas.add(clave)

                figuras.append({
                    "tipo": "Cometa",
                    "gran_trigono": ordenar_puntos(base_real),
                    "base_real": base_real,
                    "foco": foco,
                    "oposicion_a": punto_opuesto,
                    "puntos": puntos_exp,
                    "aspectos": gt["aspectos"] + [
                        aspecto_entre(aspectos, foco, punto_opuesto, "☍"),
                        sex1,
                        sex2,
                    ],
                    "peso": puntuacion_figura(puntos_exp),
                })

    return sorted(figuras, key=lambda f: -f["peso"])

def detectar_triangulos_aprendizaje(carta, aspectos):
    puntos = ORDEN_PUNTOS
    figuras = []
    vistas = set()

    for i in range(len(puntos)):
        for j in range(i + 1, len(puntos)):
            for k in range(j + 1, len(puntos)):
                a, b, c = puntos[i], puntos[j], puntos[k]

                pares = [(a, b), (a, c), (b, c)]

                quincuncios = []
                trigonos = []
                cuadraturas = []

                for p1, p2 in pares:
                    q = aspecto_entre(aspectos, p1, p2, "⚻")
                    t = aspecto_entre(aspectos, p1, p2, "△")
                    c_ = aspecto_entre(aspectos, p1, p2, "□")

                    if q:
                        quincuncios.append(q)
                    if t:
                        trigonos.append(t)
                    if c_:
                        cuadraturas.append(c_)

                if len(quincuncios) == 1 and len(trigonos) == 1 and len(cuadraturas) == 1:
                    puntos_exp = ordenar_puntos([a, b, c])
                    clave = tuple(sorted(puntos_exp))

                    if clave in vistas:
                        continue

                    vistas.add(clave)

                    figuras.append({
                        "tipo": "Triángulo de aprendizaje",
                        "puntos": puntos_exp,
                        "aspectos": quincuncios + trigonos + cuadraturas,
                        "peso": puntuacion_figura(puntos_exp),
                    })

    return sorted(figuras, key=lambda f: -f["peso"])


def detectar_triangulos_aprendizaje_pequenos(carta, aspectos):
    """
    Detecta el triángulo de aprendizaje pequeño:

    - una cuadratura;
    - un sextil;
    - un semisextil con orbe máximo de 1,5°.

    El semisextil solo adquiere relevancia estructural dentro
    de esta figura. No se interpreta ni puntúa como aspecto
    independiente.
    """
    puntos = ORDEN_PUNTOS
    figuras = []
    vistas = set()

    for i in range(len(puntos)):
        for j in range(i + 1, len(puntos)):
            for k in range(j + 1, len(puntos)):
                a, b, c = puntos[i], puntos[j], puntos[k]
                pares = [(a, b), (a, c), (b, c)]

                semisextiles = []
                sextiles = []
                cuadraturas = []

                for p1, p2 in pares:
                    ss = aspecto_entre(aspectos, p1, p2, "⚺")
                    s = aspecto_entre(aspectos, p1, p2, "✶")
                    c_ = aspecto_entre(aspectos, p1, p2, "□")

                    if ss:
                        semisextiles.append(ss)
                    if s:
                        sextiles.append(s)
                    if c_:
                        cuadraturas.append(c_)

                if (
                    len(semisextiles) == 1
                    and len(sextiles) == 1
                    and len(cuadraturas) == 1
                ):
                    puntos_exp = ordenar_puntos([a, b, c])
                    clave = tuple(sorted(puntos_exp))

                    if clave in vistas:
                        continue

                    vistas.add(clave)

                    figuras.append({
                        "tipo": "Triángulo de aprendizaje pequeño",
                        "puntos": puntos_exp,
                        "aspectos": (
                            semisextiles
                            + sextiles
                            + cuadraturas
                        ),
                        "peso": puntuacion_figura(puntos_exp),
                    })

    return sorted(figuras, key=lambda f: -f["peso"])


def detectar_triangulos_aprendizaje_medianos(carta, aspectos):
    """
    Detecta el triángulo de aprendizaje mediano:

    - una cuadratura;
    - un trígono;
    - un semisextil con orbe máximo de 1,5°.
    """
    puntos = ORDEN_PUNTOS
    figuras = []
    vistas = set()

    for i in range(len(puntos)):
        for j in range(i + 1, len(puntos)):
            for k in range(j + 1, len(puntos)):
                a, b, c = puntos[i], puntos[j], puntos[k]
                pares = [(a, b), (a, c), (b, c)]

                semisextiles = []
                trigonos = []
                cuadraturas = []

                for p1, p2 in pares:
                    ss = aspecto_entre(aspectos, p1, p2, "⚺")
                    t = aspecto_entre(aspectos, p1, p2, "△")
                    c_ = aspecto_entre(aspectos, p1, p2, "□")

                    if ss:
                        semisextiles.append(ss)
                    if t:
                        trigonos.append(t)
                    if c_:
                        cuadraturas.append(c_)

                if (
                    len(semisextiles) == 1
                    and len(trigonos) == 1
                    and len(cuadraturas) == 1
                ):
                    puntos_exp = ordenar_puntos([a, b, c])
                    clave = tuple(sorted(puntos_exp))

                    if clave in vistas:
                        continue

                    vistas.add(clave)

                    figuras.append({
                        "tipo": "Triángulo de aprendizaje mediano",
                        "puntos": puntos_exp,
                        "aspectos": (
                            semisextiles
                            + trigonos
                            + cuadraturas
                        ),
                        "peso": puntuacion_figura(puntos_exp),
                    })

    return sorted(figuras, key=lambda f: -f["peso"])


def detectar_triangulos_aprendizaje_grandes(carta, aspectos):
    """Detecta el triángulo grande: cuadratura, sextil y quincuncio."""
    puntos = ORDEN_PUNTOS
    figuras = []
    vistas = set()

    for i in range(len(puntos)):
        for j in range(i + 1, len(puntos)):
            for k in range(j + 1, len(puntos)):
                seleccion = [puntos[i], puntos[j], puntos[k]]
                pares = [
                    (seleccion[0], seleccion[1]),
                    (seleccion[0], seleccion[2]),
                    (seleccion[1], seleccion[2]),
                ]
                encontrados = {
                    simbolo: [
                        aspecto_entre(aspectos, p1, p2, simbolo)
                        for p1, p2 in pares
                    ]
                    for simbolo in ("□", "✶", "⚻")
                }
                encontrados = {
                    simbolo: [a for a in lista if a]
                    for simbolo, lista in encontrados.items()
                }

                if not all(len(encontrados[s]) == 1 for s in encontrados):
                    continue

                puntos_exp = ordenar_puntos(list(seleccion))
                clave = tuple(sorted(puntos_exp))

                if clave in vistas:
                    continue

                vistas.add(clave)
                figuras.append({
                    "tipo": "Triángulo de aprendizaje grande",
                    "puntos": puntos_exp,
                    "aspectos": (
                        encontrados["□"]
                        + encontrados["⚻"]
                        + encontrados["✶"]
                    ),
                    "peso": puntuacion_figura(puntos_exp),
                })

    return sorted(figuras, key=lambda f: -f["peso"])


def detectar_ojos_pequenos(carta, aspectos):
    """
    Detecta el Ojo pequeño o figura de información:

    - dos semisextiles con orbe máximo de 1,5°;
    - un sextil.

    Los tres aspectos solo se incorporan a la lectura cuando
    forman conjuntamente esta geometría.
    """
    puntos = ORDEN_PUNTOS
    figuras = []
    vistas = set()

    for i in range(len(puntos)):
        for j in range(i + 1, len(puntos)):
            for k in range(j + 1, len(puntos)):
                a, b, c = puntos[i], puntos[j], puntos[k]
                pares = [(a, b), (a, c), (b, c)]

                semisextiles = []
                sextiles = []

                for p1, p2 in pares:
                    ss = aspecto_entre(aspectos, p1, p2, "⚺")
                    s = aspecto_entre(aspectos, p1, p2, "✶")

                    if ss:
                        semisextiles.append(ss)
                    if s:
                        sextiles.append(s)

                if len(semisextiles) == 2 and len(sextiles) == 1:
                    puntos_exp = ordenar_puntos([a, b, c])
                    clave = tuple(sorted(puntos_exp))

                    if clave in vistas:
                        continue

                    vistas.add(clave)

                    figuras.append({
                        "tipo": "Ojo pequeño",
                        "puntos": puntos_exp,
                        "aspectos": semisextiles + sextiles,
                        "peso": puntuacion_figura(puntos_exp),
                    })

    return sorted(figuras, key=lambda f: -f["peso"])


def detectar_yods(carta, aspectos):
    puntos = ORDEN_PUNTOS
    figuras = []
    vistas = set()

    for apex in puntos:
        for i in range(len(puntos)):
            for j in range(i + 1, len(puntos)):
                p1, p2 = puntos[i], puntos[j]

                if apex in (p1, p2):
                    continue

                q1 = aspecto_entre(aspectos, apex, p1, "⚻")
                q2 = aspecto_entre(aspectos, apex, p2, "⚻")
                sex = aspecto_entre(aspectos, p1, p2, "✶")

                if q1 and q2 and sex:
                    puntos_exp = ordenar_puntos([apex, p1, p2])
                    clave = tuple(sorted(puntos_exp))

                    if clave in vistas:
                        continue

                    vistas.add(clave)

                    figuras.append({
                        "tipo": "Yod",
                        "apice": apex,
                        "base": (p1, p2),
                        "puntos": puntos_exp,
                        "aspectos": [q1, q2, sex],
                        "peso": puntuacion_figura(puntos_exp),
                    })

    return sorted(figuras, key=lambda f: -f["peso"])


def filtrar_figuras_absorbidas(figuras):
    """
    Elimina únicamente figuras realmente redundantes.

    IMPORTANTE:
    La comparación se realiza con los puntos geométricos
    reales de cada figura, no con los puntos añadidos por
    expansión de stellium.
    """

    filtradas = []

    prioridad = {
        "Cometa": 6,
        "T-cuadrada": 5,
        "Gran trígono": 4,
        "Yod": 3,
        "Triángulo de aprendizaje": 2,
        "Triángulo de aprendizaje pequeño": 2,
        "Triángulo de aprendizaje mediano": 2,
        "Triángulo de aprendizaje grande": 2,
        "Ojo pequeño": 1,
        "Stellium": 1,
    }

    figuras_ordenadas = sorted(
        figuras,
        key=lambda f: (
            -prioridad.get(
                f.get("tipo", ""),
                0
            ),
            -len(
                puntos_reales_figura(f)
            ),
            -f.get("peso", 0),
        )
    )

    for fig in figuras_ordenadas:

        tipo_fig = fig.get(
            "tipo",
            ""
        )

        puntos_fig = set(
            puntos_reales_figura(
                fig
            )
        )

        absorbida = False

        for otra in filtradas:

            tipo_otra = otra.get(
                "tipo",
                ""
            )

            puntos_otra = set(
                puntos_reales_figura(
                    otra
                )
            )

            # ─────────────────────────────────────
            # GRAN TRÍGONO DENTRO DE UN COMETA
            # ─────────────────────────────────────
            #
            # Un Cometa contiene estructuralmente
            # un Gran trígono. Solo en ese caso
            # evitamos duplicarlo.
            #
            if (
                tipo_fig == "Gran trígono"
                and tipo_otra == "Cometa"
            ):

                base_cometa = set(
                    otra.get(
                        "base_real",
                        []
                    )
                )

                if (
                    base_cometa
                    and puntos_fig
                    == base_cometa
                ):
                    absorbida = True
                    break

            # ─────────────────────────────────────
            # DUPLICADOS EXACTOS
            # ─────────────────────────────────────
            #
            # Dos figuras del mismo tipo y con los
            # mismos vértices reales son redundantes.
            #
            if (
                tipo_fig == tipo_otra
                and puntos_fig == puntos_otra
            ):

                # En T-cuadradas comprobamos además
                # que tengan el mismo ápice y oposición.
                if tipo_fig == "T-cuadrada":

                    mismo_apice = (
                        fig.get("apice")
                        == otra.get("apice")
                    )

                    oposicion_fig = set(
                        fig.get(
                            "oposicion",
                            ()
                        )
                        or ()
                    )

                    oposicion_otra = set(
                        otra.get(
                            "oposicion",
                            ()
                        )
                        or ()
                    )

                    if (
                        mismo_apice
                        and oposicion_fig
                        == oposicion_otra
                    ):
                        absorbida = True
                        break

                    continue

                # En Yods comprobamos ápice y base.
                if tipo_fig == "Yod":

                    mismo_apice = (
                        fig.get("apice")
                        == otra.get("apice")
                    )

                    base_fig = set(
                        fig.get(
                            "base",
                            ()
                        )
                        or ()
                    )

                    base_otra = set(
                        otra.get(
                            "base",
                            ()
                        )
                        or ()
                    )

                    if (
                        mismo_apice
                        and base_fig
                        == base_otra
                    ):
                        absorbida = True
                        break

                    continue

                absorbida = True
                break

        if not absorbida:
            filtradas.append(
                fig
            )

    return sorted(
        filtradas,
        key=lambda f: (
            -prioridad.get(
                f.get("tipo", ""),
                0
            ),
            -f.get("peso", 0),
            f.get("tipo", ""),
        )
    )


def clave_aspecto(aspecto):
    """Devuelve una clave estable para comparar aspectos reales."""
    if not aspecto:
        return None

    p1 = aspecto.get("p1")
    p2 = aspecto.get("p2")
    simbolo = aspecto.get("simbolo")

    if not p1 or not p2 or not simbolo:
        return None

    return tuple(sorted((p1, p2))) + (simbolo,)


def resumir_componente_figura(figura):
    """Conserva la geometría técnica de una subfigura."""
    resumen = {
        "tipo": figura.get("tipo", ""),
        "puntos": puntos_reales_figura(figura),
    }

    for campo in ("apice", "base", "oposicion"):
        if campo in figura:
            resumen[campo] = figura[campo]

    resumen["aspectos"] = [
        {
            "p1": aspecto.get("p1"),
            "p2": aspecto.get("p2"),
            "nombre": aspecto.get("nombre"),
            "simbolo": aspecto.get("simbolo"),
            "orbe": aspecto.get("orbe"),
        }
        for aspecto in figura.get("aspectos", [])
    ]

    return resumen


def construir_figura_compuesta(tipo, componentes, relacion):
    """Construye una única unidad editorial sin perder componentes."""
    aspectos = []
    claves_vistas = set()

    for componente in componentes:
        for aspecto in componente.get("aspectos", []):
            clave = clave_aspecto(aspecto)

            if not clave or clave in claves_vistas:
                continue

            claves_vistas.add(clave)
            aspectos.append(aspecto)

    puntos = ordenar_puntos(
        list({
            punto
            for componente in componentes
            for punto in puntos_reales_figura(componente)
        })
    )

    return {
        "tipo": tipo,
        "puntos": puntos,
        "aspectos": aspectos,
        "componentes": [
            resumir_componente_figura(componente)
            for componente in componentes
        ],
        "relacion_componentes": relacion,
        "peso": max(
            (componente.get("peso", 0) for componente in componentes),
            default=0,
        ) + len(componentes),
    }


def mapa_conjunciones(aspectos):
    """Agrupa puntos unidos por conjunción para comparar roles equivalentes."""
    vecinos = {}

    for aspecto in aspectos or []:
        if aspecto.get("simbolo") != "=":
            continue

        p1 = aspecto.get("p1")
        p2 = aspecto.get("p2")

        if not p1 or not p2:
            continue

        vecinos.setdefault(p1, set()).add(p2)
        vecinos.setdefault(p2, set()).add(p1)

    mapa = {}

    for punto in vecinos:
        if punto in mapa:
            continue

        pendientes = [punto]
        componente = set()

        while pendientes:
            actual = pendientes.pop()

            if actual in componente:
                continue

            componente.add(actual)
            pendientes.extend(vecinos.get(actual, set()))

        representante = tuple(ordenar_puntos(list(componente)))

        for miembro in componente:
            mapa[miembro] = representante

    return mapa


def rol_por_conjuncion(punto, mapa):
    return mapa.get(punto, (punto,))


def enriquecer_figura_con_aspectos_internos(figura, aspectos):
    """Añade enlaces reales omitidos entre los puntos de una figura compuesta."""
    puntos = set(figura.get("puntos", []))
    claves = {
        clave_aspecto(aspecto)
        for aspecto in figura.get("aspectos", [])
    }

    for aspecto in aspectos or []:
        if (
            aspecto.get("p1") in puntos
            and aspecto.get("p2") in puntos
        ):
            clave = clave_aspecto(aspecto)

            if clave and clave not in claves:
                figura.setdefault("aspectos", []).append(aspecto)
                claves.add(clave)

    return figura


def unificar_figuras_compuestas(figuras, aspectos=None):
    """
    Convierte solapamientos geométricos fuertes en unidades editoriales.

    No fusiona figuras por compartir solamente puntos. Exige una relación
    estructural concreta: misma base, misma cuadratura de aprendizaje o
    mismo ápice y brazo en varias T-cuadradas.
    """
    consumidas = set()
    compuestas = []
    conjunciones = mapa_conjunciones(aspectos)

    # 1. Yod con un Ojo pequeño que subdivide exactamente su sextil de base.
    for i, yod in enumerate(figuras):
        if yod.get("tipo") != "Yod" or i in consumidas:
            continue

        base_yod = next(
            (
                clave_aspecto(aspecto)
                for aspecto in yod.get("aspectos", [])
                if aspecto.get("simbolo") == "✶"
            ),
            None,
        )

        if not base_yod:
            continue

        ojos = []

        for j, ojo in enumerate(figuras):
            if ojo.get("tipo") != "Ojo pequeño" or j in consumidas:
                continue

            claves_ojo = {
                clave_aspecto(aspecto)
                for aspecto in ojo.get("aspectos", [])
            }

            if base_yod in claves_ojo:
                ojos.append((j, ojo))

        if ojos:
            componentes = [yod] + [ojo for _, ojo in ojos]
            compuestas.append(
                enriquecer_figura_con_aspectos_internos(
                    construir_figura_compuesta(
                    "Yod con Ojo pequeño en la base",
                    componentes,
                    "El Ojo pequeño subdivide el sextil que forma la base del Yod.",
                    ),
                    aspectos,
                )
            )
            consumidas.add(i)
            consumidas.update(j for j, _ in ojos)

    # 2. Cometas equivalentes cuando una conjunción ocupa el mismo vértice.
    grupos_cometas = {}

    for i, figura in enumerate(figuras):
        if i in consumidas or figura.get("tipo") != "Cometa":
            continue

        base = tuple(sorted(
            rol_por_conjuncion(punto, conjunciones)
            for punto in figura.get("base_real", [])
        ))
        clave = (
            base,
            rol_por_conjuncion(figura.get("foco"), conjunciones),
            rol_por_conjuncion(
                figura.get("oposicion_a"),
                conjunciones,
            ),
        )
        grupos_cometas.setdefault(clave, []).append((i, figura))

    for grupo in grupos_cometas.values():
        if len(grupo) < 2:
            continue

        compuesta = construir_figura_compuesta(
            "Cometa",
            [figura for _, figura in grupo],
            (
                "Varias cometas comparten la misma geometría y una "
                "conjunción ocupa uno de sus vértices."
            ),
        )
        compuesta["vertices_colectivos"] = True
        compuestas.append(
            enriquecer_figura_con_aspectos_internos(
                compuesta,
                aspectos,
            )
        )
        consumidas.update(i for i, _ in grupo)


    resultado = [
        figura
        for i, figura in enumerate(figuras)
        if i not in consumidas
    ]
    resultado.extend(compuestas)

    # Dos agrupaciones distintas pueden desembocar en la misma
    # unidad editorial: mismo tipo compuesto y mismos puntos. En
    # ese caso se consolidan sin perder componentes ni aspectos.
    consolidadas = {}

    for figura in resultado:
        clave_figura = (
            figura.get("tipo", ""),
            tuple(puntos_reales_figura(figura)),
        )

        if clave_figura not in consolidadas:
            consolidadas[clave_figura] = figura
            continue

        existente = consolidadas[clave_figura]

        claves_aspectos = {
            clave_aspecto(aspecto)
            for aspecto in existente.get("aspectos", [])
        }

        for aspecto in figura.get("aspectos", []):
            clave = clave_aspecto(aspecto)

            if clave and clave not in claves_aspectos:
                existente.setdefault("aspectos", []).append(aspecto)
                claves_aspectos.add(clave)

        componentes_existentes = existente.setdefault(
            "componentes",
            [],
        )
        claves_componentes = {
            (
                componente.get("tipo", ""),
                tuple(componente.get("puntos", [])),
            )
            for componente in componentes_existentes
        }

        for componente in figura.get("componentes", []):
            clave_componente = (
                componente.get("tipo", ""),
                tuple(componente.get("puntos", [])),
            )

            if clave_componente not in claves_componentes:
                componentes_existentes.append(componente)
                claves_componentes.add(clave_componente)

        existente["peso"] = max(
            existente.get("peso", 0),
            figura.get("peso", 0),
        )

    return list(consolidadas.values())


def filtrar_subfiguras_contenidas(figuras):
    """Oculta unidades ya explicadas dentro de una figura mayor.

    Una figura menor se absorbe únicamente cuando todos sus aspectos y
    participantes están contenidos en otra figura con más geometría. No se
    elimina por compartir solo algunos puntos.
    """
    tipos_contenedores = {
        "Red de aprendizaje",
        "T-cuadrada compuesta",
        "Yod con Ojo pequeño en la base",
        "Cometa",
    }
    datos = []

    for indice, figura in enumerate(figuras):
        claves = {
            clave_aspecto(aspecto)
            for aspecto in figura.get("aspectos", [])
            if clave_aspecto(aspecto)
        }
        datos.append({
            "indice": indice,
            "figura": figura,
            "aspectos": claves,
            "puntos": set(puntos_participantes_figura(figura)),
        })

    absorbidas = set()

    for menor in datos:
        figura_menor = menor["figura"]

        if figura_menor.get("tipo") == "Stellium" or not menor["aspectos"]:
            continue

        candidatas = []

        for mayor in datos:
            if mayor["indice"] == menor["indice"]:
                continue

            if mayor["figura"].get("tipo") not in tipos_contenedores:
                continue

            if len(mayor["aspectos"]) <= len(menor["aspectos"]):
                continue

            if not menor["aspectos"].issubset(mayor["aspectos"]):
                continue

            if not menor["puntos"].issubset(mayor["puntos"]):
                continue

            candidatas.append(mayor)

        if not candidatas:
            continue

        contenedora = min(
            candidatas,
            key=lambda item: len(item["aspectos"]),
        )
        absorbidas.add(menor["indice"])
        contenedora["figura"].setdefault(
            "subfiguras_absorbidas",
            [],
        ).append({
            "tipo": figura_menor.get("tipo", ""),
            "puntos": puntos_reales_figura(figura_menor),
        })

    return [
        figura
        for indice, figura in enumerate(figuras)
        if indice not in absorbidas
    ]



def asignar_vertices_stellium(carta, figuras, aspectos=None):
    """
    Representa stelliums y conjunciones como vértices colectivos.

    Primero se detecta la geometría Huber con puntos concretos.
    Después, si uno de esos puntos pertenece a un stellium o a una
    conjunción, el vértice se amplía al grupo completo.

    Esto no crea una figura nueva: refina el contenido del vértice
    conservando por separado los puntos geométricos originales.
    """
    stelliums = [
        ordenar_puntos(stellium.get("puntos", []))
        for stellium in detectar_stelliums(carta)
        if len(stellium.get("puntos", [])) >= 3
    ]

    grupos_conjuncion = []
    vistos = set()

    for grupo in mapa_conjunciones(aspectos).values():
        grupo = tuple(ordenar_puntos(list(grupo)))

        if len(grupo) < 2 or grupo in vistos:
            continue

        vistos.add(grupo)

        if any(
            set(grupo).issubset(set(stellium))
            for stellium in stelliums
        ):
            continue

        grupos_conjuncion.append(list(grupo))

    for figura in figuras:
        if figura.get("tipo") == "Stellium":
            puntos_st = ordenar_puntos(
                figura.get("puntos", [])
            )
            figura["puntos_geometricos"] = list(puntos_st)
            figura["vertices"] = [{
                "tipo": "Stellium",
                "puntos": list(puntos_st),
                "miembros_geometricos": list(puntos_st),
            }]
            figura["vertices_colectivos"] = True
            continue

        puntos_originales = set(
            puntos_reales_figura(figura)
        )

        figura["puntos_geometricos"] = ordenar_puntos(
            list(puntos_originales)
        )

        vertices = []
        consumidos = set()
        puntos_expandidos = set(puntos_originales)

        for grupo in stelliums:
            conjunto = set(grupo)
            presentes = conjunto & puntos_originales

            if not presentes:
                continue

            vertices.append({
                "tipo": "Stellium",
                "puntos": list(grupo),
                "miembros_geometricos": ordenar_puntos(
                    list(presentes)
                ),
            })
            consumidos.update(presentes)
            puntos_expandidos.update(conjunto)

        for grupo in grupos_conjuncion:
            conjunto = set(grupo)
            presentes = (
                conjunto
                & puntos_originales
                - consumidos
            )

            if not presentes:
                continue

            vertices.append({
                "tipo": "Conjunción",
                "puntos": list(grupo),
                "miembros_geometricos": ordenar_puntos(
                    list(presentes)
                ),
            })
            consumidos.update(presentes)
            puntos_expandidos.update(conjunto)

        for punto in ordenar_puntos(
            list(puntos_originales - consumidos)
        ):
            vertices.append({
                "tipo": "Punto",
                "puntos": [punto],
                "miembros_geometricos": [punto],
            })

        figura["puntos"] = ordenar_puntos(
            list(puntos_expandidos)
        )
        figura["vertices"] = vertices
        figura["vertices_colectivos"] = any(
            v.get("tipo") in ("Stellium", "Conjunción")
            for v in vertices
        )

    return figuras


def _clave_colectiva_figura(figura):
    tipo = figura.get("tipo", "")

    if tipo == "Stellium":
        return (
            tipo,
            ("Stellium", tuple(
                ordenar_puntos(figura.get("puntos", []))
            )),
        )

    vertices = []

    for vertice in figura.get("vertices", []) or []:
        puntos = tuple(
            ordenar_puntos(
                vertice.get("puntos", [])
            )
        )

        if puntos:
            vertices.append(
                (
                    vertice.get("tipo", "Punto"),
                    puntos,
                )
            )

    if not vertices:
        vertices = [
            ("Punto", (punto,))
            for punto in puntos_reales_figura(figura)
        ]

    return (
        tipo,
        tuple(sorted(vertices)),
    )


def _orbe_medio_geometria_figura(figura):
    orbes = [
        a.get("orbe")
        for a in figura.get("aspectos", []) or []
        if isinstance(a.get("orbe"), (int, float))
    ]
    if not orbes:
        return 999.0
    return sum(orbes) / len(orbes)


def _resumen_variante_geometrica_colectiva(figura):
    return {
        "puntos_geometricos": list(
            figura.get("puntos_geometricos")
            or puntos_reales_figura(figura)
        ),
        "aspectos": [
            {
                "p1": a.get("p1"),
                "p2": a.get("p2"),
                "simbolo": a.get("simbolo"),
                "orbe": a.get("orbe"),
            }
            for a in figura.get("aspectos", []) or []
        ],
        "orbe_medio": round(
            _orbe_medio_geometria_figura(figura),
            4,
        ),
    }


def _fusionar_miembros_geometricos_vertices(destino, origen):
    """
    Une únicamente la información de qué miembros de un vértice colectivo
    pueden representar geométricamente ese vértice.

    NO mezcla las aristas de dos realizaciones atómicas distintas.
    """
    vertices_destino = destino.get("vertices", []) or []
    vertices_origen = origen.get("vertices", []) or []

    for vd in vertices_destino:
        clave_d = (
            vd.get("tipo", "Punto"),
            tuple(ordenar_puntos(vd.get("puntos", []) or [])),
        )

        for vo in vertices_origen:
            clave_o = (
                vo.get("tipo", "Punto"),
                tuple(ordenar_puntos(vo.get("puntos", []) or [])),
            )
            if clave_o != clave_d:
                continue

            miembros = set(vd.get("miembros_geometricos", []) or [])
            miembros.update(vo.get("miembros_geometricos", []) or [])
            vd["miembros_geometricos"] = ordenar_puntos(list(miembros))
            break


def consolidar_figuras_por_vertices_colectivos(figuras):
    """
    Consolida duplicados producidos por stelliums/conjunciones sin deformar
    la geometría Huber.

    Problema que evita:
    -------------------
    Si Venus y Marte pertenecen al mismo stellium, una misma figura colectiva
    puede detectarse una vez usando Venus como representante y otra usando
    Marte. Antes se fusionaban TODAS las aristas de ambas realizaciones dentro
    de ``figura['aspectos']``. Una figura de cuatro vértices podía terminar con
    8 o 9 "líneas", aunque geométricamente solo puede tener como máximo 6
    pares de vértices. Eso contaminaba reserva/rescate e interpretación.

    Regla nueva:
    ------------
    - la figura colectiva se conserva una sola vez;
    - se elige UNA realización geométrica canónica (menor orbe medio);
    - sus aristas permanecen intactas y son las únicas que participan en
      reserva/rescate;
    - las realizaciones alternativas quedan como METADATOS de apoyo;
    - los miembros del stellium que pueden ocupar el mismo vértice se unen en
      ``miembros_geometricos``, sin crear aristas nuevas.
    """
    consolidadas = {}

    for figura in figuras:
        clave = _clave_colectiva_figura(figura)

        if clave not in consolidadas:
            figura.setdefault(
                "variantes_geometricas_colectivas",
                [_resumen_variante_geometrica_colectiva(figura)],
            )
            figura.setdefault(
                "aspectos_apoyo_vertice_colectivo",
                [],
            )
            consolidadas[clave] = figura
            continue

        existente = consolidadas[clave]

        variantes = existente.setdefault(
            "variantes_geometricas_colectivas",
            [],
        )
        resumen_nueva = _resumen_variante_geometrica_colectiva(figura)
        firma_nueva = (
            tuple(resumen_nueva.get("puntos_geometricos", [])),
            tuple(
                sorted(
                    (
                        a.get("p1"),
                        a.get("p2"),
                        a.get("simbolo"),
                    )
                    for a in resumen_nueva.get("aspectos", [])
                )
            ),
        )
        firmas = {
            (
                tuple(v.get("puntos_geometricos", [])),
                tuple(
                    sorted(
                        (
                            a.get("p1"),
                            a.get("p2"),
                            a.get("simbolo"),
                        )
                        for a in v.get("aspectos", [])
                    )
                ),
            )
            for v in variantes
        }
        if firma_nueva not in firmas:
            variantes.append(resumen_nueva)

        # Conservamos para interpretación las aristas alternativas, pero
        # separadas de la geometría canónica y fuera de reserva/rescate.
        claves_base = {
            clave_aspecto(a)
            for a in existente.get("aspectos", []) or []
            if clave_aspecto(a)
        }
        apoyo = existente.setdefault(
            "aspectos_apoyo_vertice_colectivo",
            [],
        )
        claves_apoyo = {
            clave_aspecto(a)
            for a in apoyo
            if clave_aspecto(a)
        }
        for aspecto in figura.get("aspectos", []) or []:
            ca = clave_aspecto(aspecto)
            if not ca or ca in claves_base or ca in claves_apoyo:
                continue
            apoyo.append(aspecto)
            claves_apoyo.add(ca)

        # Elegimos como realización canónica la de menor orbe medio. En caso
        # de empate mantenemos la primera para asegurar determinismo.
        if _orbe_medio_geometria_figura(figura) < _orbe_medio_geometria_figura(existente):
            # Antes de sustituir, preservamos todos los metadatos colectivos
            # acumulados hasta ahora.
            variantes_previas = variantes
            apoyo_previo = apoyo
            vertices_previos = existente.get("vertices", []) or []

            nueva = figura
            nueva["variantes_geometricas_colectivas"] = variantes_previas
            nueva["aspectos_apoyo_vertice_colectivo"] = apoyo_previo

            # La realización nueva pasa a ser canónica, pero conserva la
            # amplitud de miembros geométricos del vértice colectivo.
            _fusionar_miembros_geometricos_vertices(nueva, existente)
            consolidadas[clave] = nueva
            existente = nueva
        else:
            _fusionar_miembros_geometricos_vertices(existente, figura)

        existente["puntos"] = ordenar_puntos(
            list(
                set(existente.get("puntos", []))
                | set(figura.get("puntos", []))
            )
        )
        existente["peso"] = max(
            existente.get("peso", 0),
            figura.get("peso", 0),
        )

    return list(consolidadas.values())


# ─── HUBER FASE 4: JERARQUÍA Y COMPOSICIÓN ───────────────────────────────────

HUBER_FASE4_JERARQUIA_APLICADA = True

CONTENCIONES_HUBER = {
    "Cuadrado de rendimiento": {
        "T-cuadrada",
    },
    "Figura de ambivalencia doble": {
        "T-cuadrada",
        "Triángulo de ambivalencia",
        "Triángulo de aprendizaje",
        "Triángulo de aprendizaje grande",
    },
    "Rectángulo de rectitud": {
        "Triángulo de ambivalencia",
    },
    "Cometa": {
        "Gran trígono",
        "Triángulo de ambivalencia",
        "Triángulo de talento pequeño",
    },
    "Cuna": {
        "Triángulo de ambivalencia",
        "Triángulo de talento pequeño",
    },
    "Rectángulo de excitación": {
        "Triángulo de excitación",
    },
    "Trapecio": {
        "Triángulo de aprendizaje",
        "Triángulo de aprendizaje grande",
    },
    "Figura de aspiración": {
        "Ojo pequeño",
        "Triángulo de excitación",
        "Yod",
    },
    "Bañera": {
        "Triángulo de aprendizaje grande",
        "Yod",
    },
    "Nasa": {
        "Figura de búsqueda",
        "Triángulo de aprendizaje",
    },
    "Trampolín": {
        "Triángulo de ambivalencia",
        "Triángulo de aprendizaje grande",
        "Triángulo de aprendizaje mediano",
        "Triángulo de excitación",
    },
    "Telescopio-Microscopio": {
        "Triángulo de aprendizaje",
        "Triángulo de aprendizaje mediano",
    },
    "Escudo": {
        "Triángulo de aprendizaje mediano",
        "Triángulo de aprendizaje pequeño",
    },
    "Megáfono": {
        "Figura de búsqueda",
        "Ojo pequeño",
        "Triángulo de ambivalencia",
        "Triángulo de excitación",
    },
    "Animat": {
        "T-cuadrada",
        "Triángulo de ambivalencia",
        "Triángulo de aprendizaje mediano",
        "Triángulo de aprendizaje pequeño",
    },
    "Provocat": {
        "T-cuadrada",
        "Triángulo de aprendizaje grande",
        "Triángulo de aprendizaje pequeño",
        "Triángulo de excitación",
    },
    "Arena": {
        "T-cuadrada",
        "Triángulo de aprendizaje",
        "Triángulo de aprendizaje mediano",
        "Triángulo de excitación",
    },
    "Canalizador": {
        "Triángulo de ambivalencia",
        "Triángulo de aprendizaje",
        "Triángulo de aprendizaje pequeño",
        "Triángulo de excitación",
    },
    "Deco": {
        "Triángulo de ambivalencia",
        "Triángulo de aprendizaje grande",
        "Triángulo de aprendizaje mediano",
        "Triángulo de excitación",
    },
    "Bijou": {
        "Figura de búsqueda",
        "Triángulo de ambivalencia",
        "Triángulo de excitación",
        "Yod",
    },
    "Detect": {
        "Ojo pequeño",
        "Triángulo de aprendizaje mediano",
        "Triángulo de aprendizaje pequeño",
        "Triángulo de talento pequeño",
    },
    "Grabadora": {
        "Figura de búsqueda",
        "Triángulo de aprendizaje grande",
        "Triángulo de aprendizaje pequeño",
        "Triángulo de talento pequeño",
    },
    "Model": {
        "Triángulo de aprendizaje",
        "Triángulo de aprendizaje grande",
        "Triángulo de talento pequeño",
        "Yod",
    },
    "Represent": {
        "Figura de búsqueda",
        "Gran trígono",
        "Triángulo de aprendizaje",
        "Triángulo de aprendizaje mediano",
    },
    "Escenario": {
        "Figura de búsqueda",
        "Triángulo de excitación",
    },
    "Gorro mágico": {
        "Ojo pequeño",
        "Triángulo de aprendizaje pequeño",
    },
    "Ovni": {
        "Triángulo de aprendizaje grande",
        "Triángulo de aprendizaje pequeño",
    },
    "Surfista": {
        "Figura de búsqueda",
        "Ojo pequeño",
        "Triángulo de aprendizaje grande",
        "Triángulo de aprendizaje mediano",
    },
    "Oscilo": {
        "Figura de búsqueda",
        "Triángulo de aprendizaje",
        "Triángulo de aprendizaje pequeño",
        "Yod",
    },
}


def _id_figura_composicion(figura, indice=None):
    puntos = tuple(sorted(puntos_reales_figura(figura)))
    texto = "|".join([
        str(figura.get("tipo", "")),
        ",".join(puntos),
        str(figura.get("apice") or ""),
    ])
    if indice is not None:
        texto += f"|{indice}"
    return texto


def _ref_figura_composicion(figura, indice=None):
    return {
        "id": _id_figura_composicion(figura, indice),
        "tipo": figura.get("tipo", ""),
        "nombre_canonico": figura.get(
            "nombre_canonico",
            figura.get("tipo", ""),
        ),
        "puntos": list(puntos_reales_figura(figura)),
    }


def _es_contencion_huber_valida(figura_mayor, figura_menor):
    tipo_padre = figura_mayor.get("tipo", "")
    tipo_hijo = figura_menor.get("tipo", "")

    permitidas = CONTENCIONES_HUBER.get(tipo_padre, set())
    if tipo_hijo not in permitidas:
        return False

    puntos_padre = set(puntos_reales_figura(figura_mayor))
    puntos_hijo = set(puntos_reales_figura(figura_menor))

    if not puntos_padre or not puntos_hijo:
        return False

    if len(puntos_hijo) >= len(puntos_padre):
        return False

    return puntos_hijo.issubset(puntos_padre)


def anotar_jerarquia_composicion_huber(figuras):
    if not figuras:
        return figuras

    for i, figura in enumerate(figuras):
        figura["id_estructural"] = _id_figura_composicion(figura, i)
        figura["contenida_en"] = []
        figura["subfiguras"] = []
        figura["estado_estructural"] = "independiente"
        figura["nivel_composicion"] = 0

    for i, padre in enumerate(figuras):
        for j, hijo in enumerate(figuras):
            if i == j:
                continue

            if not _es_contencion_huber_valida(padre, hijo):
                continue

            ref_hijo = _ref_figura_composicion(hijo, j)
            ref_padre = _ref_figura_composicion(padre, i)

            if not any(
                r.get("id") == ref_hijo["id"]
                for r in padre["subfiguras"]
            ):
                padre["subfiguras"].append(ref_hijo)

            if not any(
                r.get("id") == ref_padre["id"]
                for r in hijo["contenida_en"]
            ):
                hijo["contenida_en"].append(ref_padre)

    for figura in figuras:
        if figura["contenida_en"]:
            figura["estado_estructural"] = "contenida"
        elif figura["subfiguras"]:
            figura["estado_estructural"] = "principal"
        else:
            figura["estado_estructural"] = "independiente"

    mapa_ids = {
        figura["id_estructural"]: figura
        for figura in figuras
    }

    cambiado = True
    vueltas = 0
    max_vueltas = len(figuras) + 1

    while cambiado and vueltas < max_vueltas:
        cambiado = False
        vueltas += 1

        for figura in figuras:
            padres = figura.get("contenida_en", [])
            if not padres:
                continue

            niveles = []

            for ref in padres:
                padre = mapa_ids.get(ref.get("id"))
                if padre is not None:
                    niveles.append(
                        padre.get("nivel_composicion", 0) + 1
                    )

            if niveles:
                nuevo = min(niveles)
                if nuevo != figura.get("nivel_composicion", 0):
                    figura["nivel_composicion"] = nuevo
                    cambiado = True

    return figuras

# ─── FIN HUBER FASE 4 ─────────────────────────────────────────────────────────


def validar_geometria_huber_detectada(figura):
    """
    Barrera estructural mínima para impedir que una figura Huber cambie
    de número de vértices por expansiones editoriales accidentales.
    """
    tipo = figura.get("tipo", "")
    if tipo == "Stellium":
        return True

    esperados = None

    if tipo in CATALOGO_HUBER_20:
        esperados = CATALOGO_HUBER_20[tipo].get("vertices")
    elif tipo in CATALOGO_HUBER_VARIANTES_26:
        esperados = CATALOGO_HUBER_VARIANTES_26[tipo].get("vertices")

    if not isinstance(esperados, int):
        return True

    puntos_reales = puntos_reales_figura(figura)

    if len(puntos_reales) != esperados:
        return False

    # Control específico de Pandora: cinco vértices y las DIEZ
    # relaciones de la geometría Huber completa.
    if tipo == "Caja de Pandora":
        aspectos_pandora = figura.get("aspectos", []) or []

        if len(aspectos_pandora) != 10:
            return False

        colores = {"rojo": 0, "verde": 0, "azul": 0}
        for asp in aspectos_pandora:
            simbolo = asp.get("simbolo")
            if simbolo in ("□", "☍"):
                colores["rojo"] += 1
            elif simbolo in ("⚺", "⚻"):
                colores["verde"] += 1
            elif simbolo in ("✶", "△"):
                colores["azul"] += 1

        # En la figura real hay:
        # 2 rojos + 4 verdes + 4 azules (incluido el sextil inferior).
        if colores != {"rojo": 2, "verde": 4, "azul": 4}:
            return False

        if figura.get("patron_huber_pasos") != [0, 2, 5, 7, 10]:
            return False

    return True



# ─── RESCATE COLECTIVO DE ARISTAS HUÉRFANAS POR STELLIUM ───────────────────
#
# Regla deliberadamente restrictiva:
# - NO se usa el stellium para redetectar toda la carta;
# - solo se examinan aspectos natales que no pertenecen a NINGUNA figura
#   geométrica atómica ya detectada;
# - una arista huérfana solo puede crear una estructura colectiva si, al
#   elevar uno de sus extremos a un stellium, cierra un triángulo cuyas otras
#   dos aristas YA están representadas por figuras seleccionadas;
# - se crea como máximo un cierre por arista huérfana y nunca si ya existe una
#   figura con los mismos tres vértices colectivos.
#
# Esto evita multiplicar figuras por el simple hecho de compartir stellium y
# cubre el caso en el que una línea real (p. ej. Venus–Neptuno) queda aislada
# atómicamente pero completa una estructura solo al considerar el stellium
# como unidad.

def _mapa_colectivo_global_cierres_stellium(carta, aspectos):
    """
    Construye el mismo lenguaje de vértices colectivos que usa el motor
    principal al asignar Stelliums y Conjunciones.

    Prioridad:
    1. Stellium (>= 3 puntos);
    2. Conjunción que no esté completamente contenida en un Stellium;
    3. Punto atómico.

    Un punto ya absorbido por un Stellium no se reasigna a una conjunción.
    Esto replica la prioridad de ``asignar_vertices_stellium`` y evita que
    el rescate colectivo trate, por ejemplo, Urano y Ascendente como dos
    vértices separados cuando el resto del motor ya los representa como una
    Conjunción colectiva.
    """
    stelliums = [
        tuple(ordenar_puntos(f.get("puntos", [])))
        for f in detectar_stelliums(carta)
        if len(f.get("puntos", [])) >= 3
    ]
    stelliums.sort(key=lambda g: (-len(g), tuple(g)))

    mapa = {}

    # Primero Stelliums: son la agrupación colectiva prioritaria.
    for grupo in stelliums:
        token = ("Stellium", grupo)
        for punto in grupo:
            mapa.setdefault(punto, token)

    # Después conjunciones, exactamente con la misma fuente que
    # ``asignar_vertices_stellium``.
    grupos_conjuncion = []
    vistos = set()

    for grupo in mapa_conjunciones(aspectos).values():
        grupo = tuple(ordenar_puntos(list(grupo)))
        if len(grupo) < 2 or grupo in vistos:
            continue
        vistos.add(grupo)

        # Una conjunción completamente incluida en un Stellium no constituye
        # un segundo vértice colectivo.
        if any(
            set(grupo).issubset(set(stellium))
            for stellium in stelliums
        ):
            continue

        grupos_conjuncion.append(grupo)

    grupos_conjuncion.sort(key=lambda g: (-len(g), tuple(g)))

    for grupo in grupos_conjuncion:
        token = ("Conjunción", grupo)
        for punto in grupo:
            # No deshacer la prioridad de un Stellium ya asignado.
            mapa.setdefault(punto, token)

    return mapa


# Alias interno conservado por compatibilidad con parches o diagnósticos
# anteriores. A partir de ahora necesita también ``aspectos`` para reconocer
# conjunciones colectivas de forma coherente con el motor principal.
def _token_colectivo_global_stellium(carta, aspectos=None):
    return _mapa_colectivo_global_cierres_stellium(
        carta,
        aspectos or [],
    )


def _token_punto_global_stellium(punto, mapa):
    return mapa.get(punto, ("Punto", (punto,)))


def _par_tokens_colectivos(aspecto, mapa):
    p1 = aspecto.get("p1")
    p2 = aspecto.get("p2")
    if not p1 or not p2:
        return None
    t1 = _token_punto_global_stellium(p1, mapa)
    t2 = _token_punto_global_stellium(p2, mapa)
    if t1 == t2:
        # Aspecto interno al mismo vértice colectivo.
        return None
    return tuple(sorted((t1, t2), key=repr))


def _token_desde_vertice_explicito(vertice):
    if not isinstance(vertice, dict):
        return None

    puntos = tuple(
        ordenar_puntos(
            list(vertice.get("puntos", []) or [])
        )
    )
    if not puntos:
        return None

    tipo = str(
        vertice.get("tipo")
        or "Punto"
    ).strip()

    return (tipo, puntos)


def _vertices_colectivos_globales_figura(figura, mapa):
    """
    Firma colectiva real de una figura seleccionada.

    Si la figura ya trae ``vertices`` (caso normal después de
    ``asignar_vertices_stellium``), esos vértices son la autoridad. Solo se
    reconstruye desde puntos atómicos como compatibilidad para figuras antiguas.

    Esta diferencia es crítica para no perder conjunciones colectivas como
    Urano+Ascendente al comprobar duplicación o contención.
    """
    vertices_explicitos = []
    for vertice in figura.get("vertices", []) or []:
        token = _token_desde_vertice_explicito(vertice)
        if token is not None:
            vertices_explicitos.append(token)

    if vertices_explicitos:
        return frozenset(vertices_explicitos)

    tokens = {
        _token_punto_global_stellium(p, mapa)
        for p in puntos_reales_figura(figura)
    }
    return frozenset(tokens)


def _trio_contenido_en_figura_seleccionada(
    trio,
    vertices_existentes,
):
    """
    Un cierre colectivo no merece bloque propio si sus tres vértices ya están
    incluidos en una figura seleccionada mayor.

    Se usa inclusión de vértices colectivos, no igualdad estricta. Así una
    figura de cuatro o más vértices puede absorber un triángulo colectivo
    interno aunque este aparezca por representantes atómicos distintos.
    """
    return any(
        trio.issubset(vertices_figura)
        for vertices_figura in vertices_existentes
        if vertices_figura
    )


def rescatar_cierres_colectivos_stellium(
    carta,
    aspectos,
    candidatas_atomicas,
    seleccionadas,
):
    """
    Rescata únicamente aristas natales totalmente huérfanas que cierran una
    estructura al considerar un Stellium como vértice colectivo.

    Reglas de seguridad:
    - no redetecta toda la carta;
    - solo parte de una arista que no pertenece a ninguna geometría atómica;
    - respeta Stelliums Y Conjunciones como vértices colectivos;
    - no crea un cierre si sus tres vértices ya están contenidos en una figura
      seleccionada mayor;
    - crea como máximo un cierre por arista huérfana;
    - el resultado es Arquitectura Interna, no una figura Huber canónica.
    """
    mapa = _mapa_colectivo_global_cierres_stellium(
        carta,
        aspectos,
    )

    # Esta función existe específicamente para expansión por Stellium.
    if not any(token[0] == "Stellium" for token in mapa.values()):
        return []

    # 1) Aspectos que ya pertenecen a cualquier geometría atómica detectada.
    atomicas_en_figura = set()
    for figura in candidatas_atomicas or []:
        if figura.get("tipo") == "Stellium":
            continue
        for asp in figura.get("aspectos", []) or []:
            clave = clave_aspecto(asp)
            if clave:
                atomicas_en_figura.add(clave)

    # 2) Grafo colectivo YA representado por las figuras seleccionadas.
    # Conservamos, para cada par de vértices, el aspecto real de menor orbe.
    soporte_por_par = {}
    for figura in seleccionadas or []:
        if figura.get("tipo") == "Stellium":
            continue
        for asp in figura.get("aspectos", []) or []:
            par = _par_tokens_colectivos(asp, mapa)
            if par is None:
                continue
            actual = soporte_por_par.get(par)
            if (
                actual is None
                or float(asp.get("orbe", 999.0))
                < float(actual.get("orbe", 999.0))
            ):
                soporte_por_par[par] = asp

    if len(soporte_por_par) < 2:
        return []

    # Autoridad para duplicación/contención: los vértices explícitos de las
    # figuras seleccionadas, que ya incluyen conjunciones colectivas.
    vertices_existentes = [
        _vertices_colectivos_globales_figura(figura, mapa)
        for figura in (seleccionadas or [])
        if figura.get("tipo") != "Stellium"
    ]

    rescates = []
    trios_ya_creados = set()

    for huerfana in sorted(
        (aspectos or []),
        key=lambda a: (
            float(a.get("orbe", 999.0)),
            str(a.get("p1", "")),
            str(a.get("p2", "")),
            str(a.get("simbolo", "")),
        ),
    ):
        clave_h = clave_aspecto(huerfana)
        if not clave_h or clave_h in atomicas_en_figura:
            continue

        par_h = _par_tokens_colectivos(huerfana, mapa)
        if par_h is None:
            continue

        u, v = par_h

        # La excepción solo existe si interviene al menos un Stellium real.
        if u[0] != "Stellium" and v[0] != "Stellium":
            continue

        # Si esa misma línea colectiva ya está representada, no es huérfana
        # desde el punto de vista de la arquitectura final.
        if par_h in soporte_por_par:
            continue

        vertices_soporte = set()
        for par in soporte_por_par:
            vertices_soporte.update(par)

        opciones = []
        for tercero in vertices_soporte:
            if tercero in (u, v):
                continue

            par_ut = tuple(sorted((u, tercero), key=repr))
            par_vt = tuple(sorted((v, tercero), key=repr))
            asp_ut = soporte_por_par.get(par_ut)
            asp_vt = soporte_por_par.get(par_vt)
            if asp_ut is None or asp_vt is None:
                continue

            trio = frozenset((u, v, tercero))

            # 1) No duplicar otro cierre ya creado.
            if trio in trios_ya_creados:
                continue

            # 2) No crear una subfigura colectiva que ya esté contenida en una
            #    figura seleccionada mayor. Antes solo se comprobaba igualdad,
            #    por lo que un triángulo interno podía reaparecer dentro de
            #    Arena, Trapecio, etc.
            if _trio_contenido_en_figura_seleccionada(
                trio,
                vertices_existentes,
            ):
                continue

            # Comprobar que el cierre depende realmente de la expansión por
            # Stellium: al menos una arista de apoyo debe usar un miembro del
            # Stellium distinto del miembro que aporta la arista huérfana.
            miembros_h = {huerfana.get("p1"), huerfana.get("p2")}
            depende_de_expansion = False
            for asp_soporte in (asp_ut, asp_vt):
                for punto in (asp_soporte.get("p1"), asp_soporte.get("p2")):
                    token = _token_punto_global_stellium(punto, mapa)
                    if (
                        token in (u, v)
                        and token[0] == "Stellium"
                        and punto not in miembros_h
                    ):
                        depende_de_expansion = True
                        break
                if depende_de_expansion:
                    break

            if not depende_de_expansion:
                continue

            score = (
                float(asp_ut.get("orbe", 999.0))
                + float(asp_vt.get("orbe", 999.0)),
                repr(tercero),
            )
            opciones.append((score, tercero, asp_ut, asp_vt, trio))

        if not opciones:
            continue

        # Máximo un cierre por arista huérfana: elegimos el soporte más exacto.
        _, tercero, asp_ut, asp_vt, trio = min(opciones, key=lambda x: x[0])

        tokens = [u, v, tercero]
        vertices = []
        puntos_expandidos = set()

        puntos_usados_geometricamente = {
            p
            for asp in (huerfana, asp_ut, asp_vt)
            for p in (asp.get("p1"), asp.get("p2"))
            if p
        }

        for token in sorted(tokens, key=repr):
            tipo, puntos_token = token
            puntos_token = list(puntos_token)
            puntos_expandidos.update(puntos_token)
            vertices.append({
                "tipo": tipo,
                "puntos": puntos_token,
                "miembros_geometricos": ordenar_puntos([
                    p
                    for p in puntos_token
                    if p in puntos_usados_geometricamente
                ]),
            })

        aspectos_cierre = [asp_ut, asp_vt, huerfana]
        puntos_geometricos = ordenar_puntos(list({
            p
            for asp in aspectos_cierre
            for p in (asp.get("p1"), asp.get("p2"))
            if p
        }))

        claves_reutilizadas = [
            clave_aspecto(asp)
            for asp in (asp_ut, asp_vt)
            if clave_aspecto(asp)
        ]
        clave_nueva = clave_aspecto(huerfana)

        figura = {
            "tipo": "Cierre colectivo de stellium",
            "nombre_canonico": "Cierre colectivo de stellium",
            "sistema": "Arquitectura Interna",
            "nivel_catalogo": "compuesta_editorial",
            "puntos": ordenar_puntos(list(puntos_expandidos)),
            "puntos_geometricos": puntos_geometricos,
            "aspectos": aspectos_cierre,
            "vertices": vertices,
            "vertices_colectivos": True,
            "cierre_colectivo_stellium": True,
            "aspecto_huerfano_cierre": {
                "p1": huerfana.get("p1"),
                "p2": huerfana.get("p2"),
                "simbolo": huerfana.get("simbolo"),
                "orbe": huerfana.get("orbe"),
            },
            "estado_estructural": "rescate_colectivo",
            "jerarquia": "seleccionada",
            "puntuacion_jerarquia": 0,
            # El intérprete debe saber que es un RESCATE y no una figura
            # Huber principal.
            "seleccion_huber_2026": "rescate",
            "fase_seleccion_huber_2026": "rescate_colectivo_stellium",
            "motivo_seleccion_huber_2026": (
                "arista_huerfana_cierra_geometria_solo_con_vertice_stellium"
            ),
            "aspectos_nuevos_huber_2026": (
                [clave_nueva] if clave_nueva else []
            ),
            "aspectos_reutilizados_huber_2026": claves_reutilizadas,
            "peso": puntuacion_figura(puntos_geometricos),
        }

        # Metadatos homogéneos con el resto del motor.
        normalizar_figura_huber(figura)
        anotar_catalogo_y_dinamica(carta, figura)
        categoria = clasificar_categoria_figura(figura)
        consistencia = clasificar_consistencia_figura(figura)
        figura["categoria"] = categoria["categoria"]
        figura["puntos_nucleares"] = categoria["nucleares"]
        figura["puntos_estructurales"] = categoria["estructurales"]
        figura["puntos_sensibles"] = categoria["sensibles"]
        figura["consistencia"] = consistencia["consistencia"]
        figura["orbe_medio"] = consistencia["orbe_medio"]
        figura["orbe_maximo"] = consistencia["orbe_maximo"]
        figura["eje_nodal_implicado"] = contiene_eje_nodal(figura)
        figura["nodos_implicados"] = nodos_reales_figura(figura)
        figura["tipo_implicacion_nodal"] = clasificar_implicacion_nodal(figura)

        rescates.append(figura)
        trios_ya_creados.add(trio)

    return rescates


def detectar_figuras_estructurales(carta, aspectos):
    figuras = []
    figuras.extend(detectar_cometas(carta, aspectos))
    figuras.extend(detectar_t_cuadradas(carta, aspectos))
    figuras.extend(detectar_t_cuadradas_con_stellium(carta, aspectos))
    figuras.extend(detectar_grandes_trigonos(carta, aspectos))
    figuras.extend(detectar_yods(carta, aspectos))
    figuras.extend(detectar_triangulos_aprendizaje(carta, aspectos))
    figuras.extend(detectar_triangulos_aprendizaje_pequenos(carta, aspectos))
    figuras.extend(detectar_triangulos_aprendizaje_medianos(carta, aspectos))
    figuras.extend(detectar_triangulos_aprendizaje_grandes(carta, aspectos))
    figuras.extend(detectar_ojos_pequenos(carta, aspectos))

    # 11 piezas básicas Huber añadidas en la fase 2.
    figuras.extend(
        detectar_figuras_huber_fase2(
            carta,
            aspectos,
        )
    )

    figuras.extend(detectar_figuras_huber_fase3(carta, aspectos))

    figuras.extend(detectar_stelliums(carta))

    # Barrera de integridad: una figura Huber no entra en la
    # arquitectura si su geometría real no coincide con el catálogo.
    figuras = [
        figura
        for figura in figuras
        if validar_geometria_huber_detectada(figura)
    ]

    unicas = {}
    for figura in figuras:
        clave = (
            figura.get("tipo", ""),
            tuple(puntos_reales_figura(figura)),
            figura.get("apice"),
            tuple(sorted(figura.get("base", ()) or ())),
        )
        if clave not in unicas:
            unicas[clave] = figura

    figuras = list(unicas.values())

    figuras = asignar_vertices_stellium(
        carta,
        figuras,
        aspectos,
    )

    figuras = consolidar_figuras_por_vertices_colectivos(
        figuras
    )

    for figura in figuras:
        normalizar_figura_huber(figura)
        anotar_catalogo_y_dinamica(carta, figura)

        categoria = clasificar_categoria_figura(figura)
        consistencia = clasificar_consistencia_figura(figura)

        figura["categoria"] = categoria["categoria"]
        figura["puntos_nucleares"] = categoria["nucleares"]
        figura["puntos_estructurales"] = categoria["estructurales"]
        figura["puntos_sensibles"] = categoria["sensibles"]
        figura["consistencia"] = consistencia["consistencia"]
        figura["orbe_medio"] = consistencia["orbe_medio"]
        figura["orbe_maximo"] = consistencia["orbe_maximo"]
        figura["eje_nodal_implicado"] = contiene_eje_nodal(figura)
        figura["nodos_implicados"] = nodos_reales_figura(figura)
        figura["tipo_implicacion_nodal"] = clasificar_implicacion_nodal(figura)

        jerarquia = clasificar_jerarquia_figura(figura)
        figura["jerarquia"] = jerarquia["jerarquia"]
        figura["puntuacion_jerarquia"] = jerarquia["puntuacion_jerarquia"]

    figuras = anotar_jerarquia_composicion_huber(figuras)

    # Conservamos las candidatas atómicas antes de la selección. Se usan solo
    # para identificar aspectos que NO pertenecían a ninguna figura real.
    candidatas_atomicas_antes_seleccion = list(figuras)

    figuras = seleccionar_arquitectura_huber_2026(figuras, aspectos)

    # Rescate excepcional: una arista completamente huérfana puede cerrar una
    # estructura únicamente al considerar un stellium como vértice colectivo.
    # No reabre la detección general ni permite duplicar figuras existentes.
    cierres_colectivos = rescatar_cierres_colectivos_stellium(
        carta,
        aspectos,
        candidatas_atomicas_antes_seleccion,
        figuras,
    )
    if cierres_colectivos:
        figuras.extend(cierres_colectivos)

    # Fase 6: añadir conocimiento interpretativo sin modificar
    # detección, jerarquía ni selección editorial.
    for figura in figuras:
        enriquecer_figura_con_guia_huber(figura)

    return figuras




# ─── HUBER FASE 6: CATÁLOGO INTERPRETATIVO — 20 FUNDAMENTALES ────────────────

HUBER_FASE6_INTERPRETACION_20_APLICADA = True

CATALOGO_INTERPRETATIVO_HUBER_20 = {'Cuadrado de rendimiento': {'alias_internos': ['Cuadrado de rendimiento'], 'familia_color': 'rojo', 'forma': 'cuadrangular', 'tipo_dinamica': 'estática', 'aspectos_clave': ['oposición', 'cuadratura'], 'dinamica_central': 'Gran reserva de energía de acción contenida en una estructura estable; la presión interna tiende a transformarse en rendimiento sostenido.', 'potencial': 'Constancia, resistencia, capacidad de trabajo, perseverancia y fuerza para llevar tareas hasta el final.', 'riesgo': 'Rigidez, exceso de control, dificultad para relajarse y tendencia a mantenerse en actividad aun cuando sería conveniente parar.', 'clave_integracion': 'Aprender a regular el esfuerzo y a introducir descanso, flexibilidad y elección consciente de dónde invertir la energía.', 'foco_interpretativo': 'Observar qué planetas sostienen las oposiciones y cuadraturas y en qué ámbitos se concentra la necesidad de actuar, controlar o producir.', 'pagina_fuente_huber': '235-241'}, 'Triángulo de rendimiento': {'alias_internos': ['T-cuadrada'], 'familia_color': 'rojo', 'forma': 'triangular', 'tipo_dinamica': 'dinámica', 'aspectos_clave': ['oposición', 'cuadratura'], 'dinamica_central': 'La tensión acumulada en la oposición busca una salida rápida a través del vértice de rendimiento; es una figura orientada a resolver y alcanzar metas.', 'potencial': 'Impulso, capacidad de reacción, alta productividad por períodos y facilidad para movilizar energía hacia un objetivo.', 'riesgo': 'Impaciencia, sobreesfuerzo, actuar antes de elaborar suficientemente la situación o vivir la presión como exigencia permanente.', 'clave_integracion': 'Dar dirección consciente al impulso y alternar acción intensa con recuperación real.', 'foco_interpretativo': 'El vértice de las cuadraturas es decisivo: sus planetas muestran dónde y cómo se descarga la tensión de la oposición.', 'pagina_fuente_huber': '242-247'}, 'Triángulo de talento grande': {'alias_internos': ['Gran trígono'], 'familia_color': 'azul', 'forma': 'triangular', 'tipo_dinamica': 'dinámica armónica', 'aspectos_clave': ['trígono'], 'dinamica_central': 'Capacidad o cualidad disponible de forma natural, con sensación de suficiencia y facilidad para permanecer en un estado conocido.', 'potencial': 'Talento estable, comprensión, confianza en capacidades propias y posibilidad de desarrollar una cualidad hasta un grado elevado.', 'riesgo': 'Comodidad, inercia, autosuficiencia o dejar sin utilizar un talento porque funciona con demasiada facilidad.', 'clave_integracion': 'Encontrar una tarea con sentido que obligue a poner el talento en circulación y convertir capacidad latente en expresión creativa.', 'foco_interpretativo': 'Los planetas y el elemento/signos implicados indican la naturaleza concreta del talento y el campo donde puede materializarse.', 'pagina_fuente_huber': '248-251'}, 'Triángulo de talento pequeño': {'alias_internos': ['Triángulo de talento pequeño'], 'familia_color': 'azul', 'forma': 'triangular', 'tipo_dinamica': 'dinámica armónica', 'aspectos_clave': ['trígono', 'sextil'], 'dinamica_central': 'Talento armónico más móvil y orientado que el gran triángulo; la asimetría dirige la capacidad hacia un vértice concreto.', 'potencial': 'Facilidad práctica, continuidad, creatividad aplicada y capacidad de emplear recursos con poco desgaste.', 'riesgo': 'Confiar demasiado en lo que sale solo, acomodarse a la facilidad o depender de estímulos externos para activar la capacidad.', 'clave_integracion': 'Usar conscientemente la dirección marcada por el vértice y convertir la facilidad en una contribución concreta.', 'foco_interpretativo': 'El vértice del triángulo funciona como dirección de salida o meta; sus planetas muestran dónde se concentra la manifestación del talento.', 'pagina_fuente_huber': '252-254'}, 'Triángulo de ambivalencia': {'alias_internos': ['Triángulo de ambivalencia'], 'familia_color': 'rojo-azul', 'forma': 'triangular', 'tipo_dinamica': 'dinámica ambivalente', 'aspectos_clave': ['oposición', 'trígono', 'sextil'], 'dinamica_central': 'Alternancia entre un polo de tensión/conflicto y un polo armónico que busca comodidad, placer o distensión.', 'potencial': 'Capacidad de reconocer dos modos de respuesta y utilizar el vértice azul como punto de regulación entre los extremos de la oposición.', 'riesgo': 'Oscilar entre tensión y evasión, pensar en términos de todo o nada o refugiarse en la zona cómoda sin elaborar el conflicto.', 'clave_integracion': 'Convertir el tercer vértice en un regulador consciente que permita sostener la tensión sin quedar atrapado ni huir de ella.', 'foco_interpretativo': 'Distinguir los planetas de la oposición del planeta del vértice azul y describir qué función puede mediar entre ambos polos.', 'pagina_fuente_huber': '255-258'}, 'Figura de ambivalencia doble': {'alias_internos': ['Figura de ambivalencia doble'], 'familia_color': 'rojo-azul con posible verde', 'forma': 'cuadrangular', 'tipo_dinamica': 'estática con oscilación', 'aspectos_clave': ['oposición', 'cuadratura', 'trígono', 'sextil', 'quincuncio opcional'], 'dinamica_central': 'Dos dinámicas de ambivalencia quedan enlazadas en una estructura mayor, aumentando la alternancia entre presión de acción y zonas de distensión.', 'potencial': 'Capacidad para movilizar cambios y combinar rendimiento con recursos o talentos disponibles.', 'riesgo': 'Contradicciones internas, sobrecompensación y ciclos de activación y retirada; sin la diagonal verde puede faltar coordinación consciente.', 'clave_integracion': 'Reconocer el patrón completo y coordinar conscientemente los dos polos; si existe quincuncio, usarlo como vía de planificación y desarrollo.', 'foco_interpretativo': 'Comprobar expresamente si está presente el quincuncio diagonal y qué planetas enlaza, porque modifica la coordinación de toda la figura.', 'pagina_fuente_huber': '259-266'}, 'Rectángulo de rectitud': {'alias_internos': ['Rectángulo de rectitud'], 'familia_color': 'rojo-azul', 'forma': 'cuadrangular', 'tipo_dinamica': 'estática', 'aspectos_clave': ['oposición', 'trígono', 'sextil'], 'dinamica_central': 'Una envolvente armónica y estable protege dos oposiciones internas cargadas de tensión; hacia fuera puede predominar la apariencia de equilibrio.', 'potencial': 'Talento múltiple, capacidad de sostener tensiones internas y transformarlas en una forma estable o creativa.', 'riesgo': 'Ocultar o encapsular el conflicto, aferrarse a la armonía exterior o hacer difícil que otras personas perciban la tensión real.', 'clave_integracion': "Abrir conscientemente el contenido del 'sobre': reconocer las oposiciones y utilizar los recursos azules para elaborarlas, no para taparlas.", 'foco_interpretativo': 'Interpretar por separado las dos oposiciones y luego observar qué sextiles/trígonos ofrecen vías de integración y expresión.', 'pagina_fuente_huber': '267-272'}, 'Cometa': {'alias_internos': ['Cometa'], 'familia_color': 'rojo-azul', 'forma': 'cuadrangular', 'tipo_dinamica': 'estática orientada', 'aspectos_clave': ['oposición', 'trígono', 'sextil'], 'dinamica_central': 'Predominio de sustancia y armonía azul atravesado por una oposición que introduce una tarea de desarrollo y una dirección concreta.', 'potencial': 'Talento amplio, capacidad de estabilizar recursos y de darles dirección mediante el eje de oposición.', 'riesgo': 'Quedarse en lo ya logrado, proteger demasiado el estado armónico o desatender la temática incómoda que activa el crecimiento.', 'clave_integracion': 'Trabajar conscientemente la temática del planeta de la cola/oposición y permitir que la tensión movilice el potencial del gran trígono.', 'foco_interpretativo': 'La oposición es el motor y la cola tiene especial importancia; las subfiguras de talento deben leerse como recursos integrados en el Cometa.', 'pagina_fuente_huber': '272-279'}, 'Cuna': {'alias_internos': ['Cuna'], 'familia_color': 'rojo-azul', 'forma': 'cuadrangular abierta', 'tipo_dinamica': 'estática protectora', 'aspectos_clave': ['oposición', 'trígono', 'sextil'], 'dinamica_central': 'Acumulación de talento y armonía en una mitad del espacio, con fuerte necesidad de seguridad y protección frente a la zona abierta.', 'potencial': 'Capacidad de armonizar, contener, reflejar y producir un efecto estabilizador o reparador en el entorno.', 'riesgo': 'Refugiarse en lo conocido, retirarse ante el conflicto, reprimir dolor o evitar la exposición que exige la zona vacía.', 'clave_integracion': 'Salir progresivamente de la seguridad de la cuna y usar los talentos contenidos para afrontar lo que queda fuera de la estructura protegida.', 'foco_interpretativo': 'La orientación espacial es esencial: observar hacia qué hemisferio está abierta y qué eje forma la oposición.', 'pagina_fuente_huber': '279-288'}, 'Triángulo de excitación': {'alias_internos': ['Triángulo de excitación'], 'familia_color': 'rojo-verde', 'forma': 'triangular', 'tipo_dinamica': 'dinámica excitada', 'aspectos_clave': ['oposición', 'quincuncio', 'semisextil'], 'dinamica_central': 'Tensión sin amortiguación azul: la presión roja mantiene activos los aspectos verdes y obliga a buscar, percibir, aprender o modificar la situación.', 'potencial': 'Gran capacidad de aprendizaje bajo presión, creatividad ante obstáculos y disposición a transformar la inquietud en búsqueda.', 'riesgo': 'Nerviosismo, irritabilidad, sensación de no poder descansar, reacción excesiva ante estímulos o convertir la búsqueda en agitación permanente.', 'clave_integracion': 'Usar la tensión como combustible para ampliar conciencia y encontrar respuestas, sin descargarla indiscriminadamente sobre el entorno.', 'foco_interpretativo': 'Identificar la oposición que concentra la presión y seguir el recorrido de los aspectos verdes hacia el punto donde se busca una solución.', 'pagina_fuente_huber': '288-293'}, 'Rectángulo de excitación': {'alias_internos': ['Rectángulo de excitación'], 'familia_color': 'rojo-verde', 'forma': 'cuadrangular', 'tipo_dinamica': 'estática excitada', 'aspectos_clave': ['oposición', 'quincuncio', 'semisextil'], 'dinamica_central': 'La tensión queda estabilizada en una figura simétrica que busca información y aprendizaje de forma constante para transformar presión en conciencia.', 'potencial': 'Atención despierta, capacidad para detectar interconexiones, investigación persistente y desarrollo continuado de conocimiento.', 'riesgo': 'Rigidez mental, presión sobre el entorno, fanatismo, bloqueo comunicativo o búsqueda compulsiva de confirmación.', 'clave_integracion': 'Dirigir la tensión hacia el propio desarrollo, ampliando tolerancia y movilidad mental en vez de intentar imponer una solución exterior.', 'foco_interpretativo': 'El eje de las oposiciones y la zona recorrida por los aspectos verdes muestran dónde se concentra la búsqueda de información y transformación.', 'pagina_fuente_huber': '293-298'}, 'Figura de búsqueda': {'alias_internos': ['Figura de búsqueda'], 'familia_color': 'azul-verde', 'forma': 'triangular', 'tipo_dinamica': 'dinámica receptiva', 'aspectos_clave': ['trígono', 'quincuncio', 'semisextil'], 'dinamica_central': 'Una base de capacidad o comprensión busca ampliarse mediante información, sensibilidad y nuevas alternativas, sin presión roja que obligue a actuar.', 'potencial': 'Curiosidad profunda, refinamiento de la percepción, ampliación de conocimientos y capacidad para imaginar posibilidades diferentes.', 'riesgo': 'Quedarse en la búsqueda, la fantasía o la alternativa mental sin materializar; dificultad para poner límites si la estructura global es débil.', 'clave_integracion': 'Convertir la información acumulada en elección y experiencia concreta, aportando estructura y límites a la apertura perceptiva.', 'foco_interpretativo': 'El trígono muestra la base disponible; los aspectos verdes indican hacia dónde se amplía, cuestiona o sensibiliza esa base.', 'pagina_fuente_huber': '299-305'}, 'Figura de proyección': {'alias_internos': ['Yod'], 'familia_color': 'azul-verde', 'forma': 'triangular', 'tipo_dinamica': 'dinámica orientada', 'aspectos_clave': ['sextil', 'quincuncio'], 'dinamica_central': 'Una imagen, idea o potencial contenido en la base se dirige hacia un vértice mediante dos quincuncios, generando una fuerte orientación proyectiva.', 'potencial': 'Imaginación, capacidad de proyectar posibilidades, pensamiento creativo e innovación cuando existe suficiente diferenciación consciente.', 'riesgo': 'Atribuir al exterior contenidos propios, idealizar, interpretar la realidad a través de imágenes internas o depender demasiado de cómo se es percibido.', 'clave_integracion': 'Distinguir conscientemente entre imagen interna y realidad externa y transformar la proyección en proyecto creativo.', 'foco_interpretativo': 'El planeta ápice y el eje espacial de la figura son centrales; describir qué contenido de la base se proyecta y hacia qué ámbito.', 'pagina_fuente_huber': '305-317'}, 'Figura de información (ojo)': {'alias_internos': ['Ojo pequeño'], 'familia_color': 'azul-verde', 'forma': 'triangular pequeña', 'tipo_dinamica': 'dinámica perceptiva', 'aspectos_clave': ['sextil', 'semisextil'], 'dinamica_central': 'Figura muy pequeña y concentrada que explora una zona vital, capta información y registra detalles de forma continua.', 'potencial': 'Observación, especialización, curiosidad, flexibilidad mental y capacidad para detectar datos o conexiones que pueden pasar inadvertidos.', 'riesgo': 'Hipervigilancia, curiosidad dispersa, acumulación indiscriminada de información o quedar demasiado condicionado por estímulos del entorno.', 'clave_integracion': 'Seleccionar y elaborar la información captada, convirtiendo observación en comprensión útil.', 'foco_interpretativo': 'Precisar la casa o pequeña zona que abarca el ojo: ahí se concentra el radar perceptivo y la especialización.', 'pagina_fuente_huber': '317-322'}, 'Triángulo de aprendizaje pequeño': {'alias_internos': ['Triángulo de aprendizaje pequeño'], 'familia_color': 'rojo-verde-azul', 'forma': 'triangular', 'tipo_dinamica': 'dinámica de aprendizaje', 'aspectos_clave': ['cuadratura', 'semisextil', 'sextil'], 'dinamica_central': 'Ciclo frecuente de crisis pequeña: tensión o insatisfacción, búsqueda de información y retorno provisional a una situación más armónica.', 'potencial': 'Aprendizaje continuo, capacidad de corregir mediante experiencia y maduración progresiva en un ámbito concreto.', 'riesgo': 'Repetir una y otra vez el mismo circuito, vivir con inquietud crónica o depender excesivamente de señales externas para resolver el conflicto.', 'clave_integracion': 'Reconocer el patrón repetitivo y extraer conscientemente el aprendizaje para que cada vuelta del ciclo produzca una modificación real.', 'foco_interpretativo': 'La cuadratura señala el conflicto; el semisextil busca información y el sextil muestra el estado al que se intenta volver.', 'pagina_fuente_huber': '325-327'}, 'Triángulo de aprendizaje mediano': {'alias_internos': ['Triángulo de aprendizaje mediano'], 'familia_color': 'rojo-verde-azul', 'forma': 'triangular', 'tipo_dinamica': 'dinámica de aprendizaje', 'aspectos_clave': ['trígono', 'cuadratura', 'semisextil'], 'dinamica_central': 'Parte de una tranquilidad o suficiencia interna que es interrumpida por exigencias externas; la persona busca información y actúa para recuperar equilibrio.', 'potencial': 'Capacidad para responder a desafíos, aprender del intercambio y combinar recursos internos con adaptación activa.', 'riesgo': 'Reactividad, nerviosismo ante interrupciones, resistencia a abandonar la comodidad o vivir las demandas externas como molestias constantes.', 'clave_integracion': 'Aceptar la ruptura de la comodidad como parte del proceso y utilizar contacto, información y acción para actualizar la propia estabilidad.', 'foco_interpretativo': 'El trígono describe la base interna; cuadratura y semisextil muestran qué estímulos externos rompen esa calma y activan el aprendizaje.', 'pagina_fuente_huber': '327-328'}, 'Triángulo de aprendizaje grande': {'alias_internos': ['Triángulo de aprendizaje grande'], 'familia_color': 'rojo-verde-azul', 'forma': 'triangular', 'tipo_dinamica': 'dinámica de desarrollo', 'aspectos_clave': ['quincuncio', 'cuadratura', 'sextil'], 'dinamica_central': 'El quincuncio orientado al centro convierte la expansión de conciencia, el aprendizaje y el desarrollo en motivación principal dentro de una zona concreta.', 'potencial': 'Búsqueda consciente de crecimiento, disposición a entrar en conflictos productivos y capacidad de desarrollar soluciones mediante aprendizaje.', 'riesgo': 'Polarizar las respuestas, aceptar soluciones demasiado fáciles o convertir el crecimiento en una búsqueda interminable sin síntesis.', 'clave_integracion': 'Sostener la pregunta del quincuncio el tiempo suficiente para que la tensión produzca comprensión y no una salida rápida.', 'foco_interpretativo': 'El quincuncio es el eje del proceso; las casas y planetas implicados delimitan el ámbito en que se busca expansión de conciencia.', 'pagina_fuente_huber': '328-329'}, 'Triángulo dominante': {'alias_internos': ['Triángulo de aprendizaje'], 'familia_color': 'rojo-verde-azul', 'forma': 'triangular envolvente', 'tipo_dinamica': 'dinámica de desarrollo central', 'aspectos_clave': ['oposición', 'quincuncio', 'trígono'], 'dinamica_central': 'Gran triángulo de aprendizaje que envuelve el centro; el proceso de crisis y aprendizaje se relaciona con la orientación global del yo y adquiere mayor profundidad.', 'potencial': 'Creatividad, irradiación, capacidad de transformación personal y posibilidad de encontrar respuestas desde el propio centro.', 'riesgo': 'Vivir crisis amplias como luchas externas, buscar soluciones fuera o quedar atrapado en procesos largos de prueba y error.', 'clave_integracion': 'Volver al centro propio para encontrar la dirección y transformar la crisis en una meta auténtica; atender también al sentido de giro.', 'foco_interpretativo': 'Determinar el sentido de giro y distinguir proceso de reconocimiento/experiencia; al envolver el centro, no debe tratarse como un aprendizaje local.', 'pagina_fuente_huber': '329-335'}, 'Trapecio': {'alias_internos': ['Trapecio'], 'familia_color': 'rojo-verde-azul', 'forma': 'cuadrangular', 'tipo_dinamica': 'estática con crecimiento interno', 'aspectos_clave': ['cuadratura', 'quincuncio', 'trígono', 'sextil'], 'dinamica_central': 'Integra triángulos de aprendizaje dentro de una estructura cuadrangular: busca seguridad y estabilidad, pero necesita mantener un crecimiento permanente.', 'potencial': 'Capacidad para perfeccionar, materializar ideas con detalle y sostener procesos de desarrollo a largo plazo.', 'riesgo': 'Querer controlar el proceso de crecimiento, tensar demasiado la diferencia entre idea y forma o quedar atrapado en perfeccionamiento constante.', 'clave_integracion': 'Permitir que estabilidad y aprendizaje cooperen: crear formas suficientemente sólidas sin detener la renovación.', 'foco_interpretativo': 'La dirección se lee por el eje de simetría; las subfiguras de aprendizaje deben interpretarse como componentes de la figura mayor, no como bloques aislados.', 'pagina_fuente_huber': '335-339'}, 'Figura de aspiración': {'alias_internos': ['Figura de aspiración'], 'familia_color': 'rojo-verde-azul', 'forma': 'cuadrangular dinámica', 'tipo_dinamica': 'mixta', 'aspectos_clave': ['oposición', 'sextil', 'quincuncio', 'semisextil'], 'dinamica_central': 'Combina proyección y ojo alrededor de una oposición: une visión, captación de información, tensión y deseo de desarrollo en una estructura orientada.', 'potencial': 'Aspiración sostenida, capacidad para investigar, proyectar y movilizar recursos hacia una meta o desarrollo.', 'riesgo': 'Ambición excesiva, inquietud, proyección de metas poco realistas o mantener una tensión continua por querer avanzar siempre.', 'clave_integracion': 'Alinear aspiración con percepción realista: usar la información del ojo para corregir la proyección y la oposición como motor, no como presión ciega.', 'foco_interpretativo': 'Leer conjuntamente la figura de proyección, el ojo y la oposición, respetando que son componentes integrados de una estructura mayor.', 'pagina_fuente_huber': '339-343'}}

INDICE_INTERPRETATIVO_HUBER_20 = {}

for _nombre_huber, _guia_huber in CATALOGO_INTERPRETATIVO_HUBER_20.items():
    INDICE_INTERPRETATIVO_HUBER_20[_nombre_huber] = _nombre_huber
    for _alias_huber in _guia_huber.get("alias_internos", []):
        INDICE_INTERPRETATIVO_HUBER_20[_alias_huber] = _nombre_huber


def obtener_guia_interpretativa_huber(figura_o_tipo):
    """
    Devuelve una COPIA de la guía interpretativa Huber de las 20 figuras
    fundamentales. No habilita por sí misma la figura en la salida editorial.
    """
    if isinstance(figura_o_tipo, dict):
        candidatos = [
            figura_o_tipo.get("nombre_canonico"),
            figura_o_tipo.get("tipo"),
        ]
    else:
        candidatos = [figura_o_tipo]

    nombre = None
    for candidato in candidatos:
        if candidato in INDICE_INTERPRETATIVO_HUBER_20:
            nombre = INDICE_INTERPRETATIVO_HUBER_20[candidato]
            break

    if nombre is None:
        return None

    guia = dict(CATALOGO_INTERPRETATIVO_HUBER_20[nombre])
    guia["nombre_huber"] = nombre
    guia["fuente"] = {
        "obra": "Astrología de la figura de aspectos",
        "autores": "Bruno Huber, Louise Huber, Michael-Alexander Huber",
        "edicion": "API Ediciones España, 2003",
        "pagina": guia.get("pagina_fuente_huber"),
    }
    return guia


def enriquecer_figura_con_guia_huber(figura):
    """
    Añade metadatos interpretativos deterministas a una figura ya detectada.
    No altera geometría, puntuación, jerarquía ni visibilidad editorial.
    """
    guia = obtener_guia_interpretativa_huber(figura)
    if guia is None:
        figura.pop("guia_interpretativa_huber", None)
        figura["soporte_interpretativo_huber"] = False
        return figura

    figura["guia_interpretativa_huber"] = guia
    figura["soporte_interpretativo_huber"] = True
    figura["nombre_interpretativo_huber"] = guia["nombre_huber"]
    return figura

# ─── FIN HUBER FASE 6 ─────────────────────────────────────────────────────────



# ─── HUBER FASE 7: CATÁLOGO INTERPRETATIVO — 26 VARIANTES ───────────────────

HUBER_FASE7_INTERPRETACION_26_APLICADA = True

CATALOGO_INTERPRETATIVO_HUBER_26 = {'Caja de Pandora': {'familia_catalogo': 'Diez figuras de aspectos nuevas', 'familia_color': 'tricolor', 'forma': 'pentágono irregular', 'tipo_dinamica': 'estática con fluctuación interna', 'dinamica_central': 'Seguridad exterior y ambivalencia visible conviven con un interior verde mucho más incierto, sensible y diferenciador.', 'potencial': 'Capacidad de sostener complejidad, diferenciar matices y descubrir un contenido valioso tras contradicciones o juicios inicialmente polarizados.', 'riesgo': 'Expresarse con excesiva seguridad mientras internamente existen dudas, producir mensajes contradictorios o defenderse mediante juicios tajantes.', 'clave_integracion': 'Reconocer la inseguridad interior y convertirla en capacidad consciente de diferenciación, en vez de ocultarla tras certezas rígidas.', 'foco_interpretativo': "Distinguir la envolvente rojo-azul del contenido verde y observar qué planetas forman la 'tapa' azul y el eje de simetría.", 'pagina_fuente_huber': '349-351'}, 'Bañera': {'familia_catalogo': 'Diez figuras de aspectos nuevas', 'familia_color': 'tricolor con predominio verde', 'forma': 'cuadrangular abierta', 'tipo_dinamica': 'receptiva y sensitiva', 'dinamica_central': 'Alta sensibilidad y receptividad que absorben experiencias del entorno y las procesan de manera muy personal.', 'potencial': 'Percepción fina, aprendizaje por experiencia y capacidad de absorber gran cantidad de información o estímulo.', 'riesgo': 'Hipersensibilidad, poca practicidad, pasividad frente a lo que llega o aprendizaje a través de experiencias dolorosas.', 'clave_integracion': 'Desarrollar criterios propios y transformar lo percibido en experiencia elaborada, sin quedar a merced del entorno.', 'foco_interpretativo': 'Observar las zonas abiertas y vulnerables y qué planetas forman la parte receptiva verde frente a los apoyos azules y rojos.', 'pagina_fuente_huber': '352-353'}, 'Mariposa': {'familia_catalogo': 'Diez figuras de aspectos nuevas', 'familia_color': 'azul-verde', 'forma': 'lineal en ocho', 'tipo_dinamica': 'púlsar repetitivo', 'dinamica_central': 'Movimiento continuo que regresa una y otra vez sobre sí mismo, acumulando percepción e información sin presión roja de realización.', 'potencial': 'Movilidad, capacidad de adaptación, percepción continuada y transmisión sutil de estímulos.', 'riesgo': 'Repetir movimientos, pensamientos o hábitos sin producir algo nuevo; convertir actividad en automatismo.', 'clave_integracion': 'Introducir dirección consciente y propósito en el movimiento para que la repetición genere aprendizaje y no mero reflejo.', 'foco_interpretativo': 'Leerla como figura lineal/púlsar y comprobar dónde se repite el circuito azul-verde.', 'pagina_fuente_huber': '354'}, 'Nasa': {'familia_catalogo': 'Diez figuras de aspectos nuevas', 'familia_color': 'azul-verde', 'forma': 'cuadrangular abierta', 'tipo_dinamica': 'receptiva y acumulativa', 'dinamica_central': 'Recoge estímulos e información del entorno, los retiene y los procesa internamente de forma personal.', 'potencial': 'Gran capacidad de captar, almacenar y relacionar información de manera placentera y flexible.', 'riesgo': 'Acumulación sin aplicación, comodidad excesiva o dificultad para saber qué hacer con lo recogido.', 'clave_integracion': 'Seleccionar y utilizar activamente la información acumulada, conectándola con una finalidad concreta.', 'foco_interpretativo': 'Las zonas abiertas indican por dónde entra el estímulo; los aspectos azules muestran la capacidad de retención.', 'pagina_fuente_huber': '355'}, 'Trampolín': {'familia_catalogo': 'Diez figuras de aspectos nuevas', 'familia_color': 'rojo-verde con interior azul', 'forma': 'cuadrangular', 'tipo_dinamica': 'reactiva y altamente sensitiva', 'dinamica_central': 'Gran sensibilidad exterior y reacción rápida combinadas con una visión interna idealista y coherente.', 'potencial': 'Atención muy despierta, aprendizaje continuo, capacidad de recoger conocimiento y responder con rapidez.', 'riesgo': 'Excitabilidad, hipersensibilidad, incapacidad para adoptar posiciones rígidas o acumular conocimiento sin convertirlo en acción.', 'clave_integracion': 'Usar la sensibilidad como resorte de aprendizaje y añadir dirección consciente para que el conocimiento pueda materializarse.', 'foco_interpretativo': 'Diferenciar el suelo rojo, los apoyos cruzados y los tres lados verdes; mantener su orientación quiral frente a Deco.', 'pagina_fuente_huber': '356-357'}, 'Corredor (saltador)': {'familia_catalogo': 'Diez figuras de aspectos nuevas', 'familia_color': 'rojo-azul', 'forma': 'lineal', 'tipo_dinamica': 'púlsar reactivo', 'dinamica_central': 'La presión pone inmediatamente en marcha el movimiento; la energía de las cuadraturas impulsa a actuar o hacer actuar.', 'potencial': 'Rapidez de reacción, resistencia al esfuerzo y capacidad de activar procesos y personas.', 'riesgo': 'Ejercer presión sobre los demás mientras se reacciona con gran sensibilidad cuando la presión viene de fuera; automatismos difíciles de detener.', 'clave_integracion': 'Reconocer el mecanismo automático y decidir cuándo moverse y cuándo no responder al estímulo.', 'foco_interpretativo': 'Leer las cuadraturas como motor del circuito y comprobar si la figura está integrada en otra estructura mayor que module su automatismo.', 'pagina_fuente_huber': '358-359'}, 'Telescopio-Microscopio': {'familia_catalogo': 'Diez figuras de aspectos nuevas', 'familia_color': 'tricolor equilibrado', 'forma': 'cuadrangular axial', 'tipo_dinamica': 'sensitiva y focal', 'dinamica_central': 'Capacidad de enfocar tanto la globalidad como el detalle, amplificando aquello hacia lo que se orienta la percepción.', 'potencial': 'Comprender lo grande a partir de lo pequeño, diferenciar con precisión y reconocer conexiones amplias.', 'riesgo': 'Efecto lupa, pérdida de proporción o unilateralidad: ver sólo los detalles o sólo la visión global.', 'clave_integracion': 'Desarrollar consciencia de la propia focalización y aprender a cambiar deliberadamente entre perspectiva amplia y detalle.', 'foco_interpretativo': 'La orientación del quincuncio distingue función telescopio/microscopio; semisextil y quincuncio deben leerse como escalas perceptivas complementarias.', 'pagina_fuente_huber': '359-361'}, 'Amortiguador': {'familia_catalogo': 'Diez figuras de aspectos nuevas', 'familia_color': 'rojo-azul', 'forma': 'lineal', 'tipo_dinamica': 'púlsar elástico', 'dinamica_central': 'Alterna estados complementarios y transforma impactos externos mediante un mecanismo elástico de absorción y recuperación.', 'potencial': 'Gran capacidad de recuperación, adaptación energética y transformación de golpes o presión en experiencia.', 'riesgo': 'Buscar inconscientemente impactos para activar el mecanismo, perder energía por los lados abiertos o reiniciar continuamente el mismo ciclo.', 'clave_integracion': 'Reconocer cuándo el mecanismo de respuesta está activándose por hábito y conservar la energía transformada en vez de perderla.', 'foco_interpretativo': 'Leer el trígono y sextil paralelos como suspensión azul y las cuadraturas cruzadas como mecanismo de impacto.', 'pagina_fuente_huber': '361'}, 'Escudo': {'familia_catalogo': 'Diez figuras de aspectos nuevas', 'familia_color': 'rojo-verde-azul', 'forma': 'cuadrangular protectora', 'tipo_dinamica': 'defensiva y absorbente', 'dinamica_central': 'Protege frente a la pérdida de energía absorbiendo impactos y transformándolos en sustancia interior.', 'potencial': 'Resistencia, capacidad para soportar golpes fuertes y convertir experiencias difíciles en estabilidad.', 'riesgo': 'Rigidez defensiva, gestos de amenaza, acusación o dramatización para mantener a otros a distancia.', 'clave_integracion': 'Usar la protección para contener y transformar, no para mantener una postura defensiva permanente.', 'foco_interpretativo': 'Los semisextiles indican sensibilidad lateral; comprobar si el escudo es completo o presenta una zona vulnerable.', 'pagina_fuente_huber': '362'}, 'Diamante': {'familia_catalogo': 'Diez figuras de aspectos nuevas', 'familia_color': 'multicolor con exceso verde', 'forma': 'poligonal de ocho o más ángulos', 'tipo_dinamica': 'compleja y altamente conectada', 'dinamica_central': 'Una red muy densa de funciones y conexiones produce enorme sensibilidad, comunicación y complejidad operativa.', 'potencial': 'Versatilidad, capacidad de aprendizaje, intercambio y coordinación de múltiples funciones.', 'riesgo': 'Sobrecarga, lentitud para integrar tantos estímulos, pérdida de control o retirada frente a la complejidad de la vida ordinaria.', 'clave_integracion': 'Simplificar, priorizar y aceptar que no todas las conexiones pueden funcionar simultáneamente.', 'foco_interpretativo': 'Considerar el número total de vértices, densidad y predominio verde; no reducirla a una sola subfigura.', 'pagina_fuente_huber': '363-366'}, 'Megáfono': {'familia_catalogo': 'Siete figuras cuadrangulares con oposición', 'familia_color': 'tricolor', 'forma': 'semicuadrangular puntiaguda', 'tipo_dinamica': 'rápida y comunicativa', 'dinamica_central': 'Capta, filtra y amplifica información; combina sensibilidad y escucha en una zona con dureza o inaccesibilidad en la opuesta.', 'potencial': 'Pensamiento rápido, comprobación de información, comunicación eficaz y capacidad de distinguir lo relevante.', 'riesgo': 'Dependencias comunicativas, contraste excesivo entre apertura y dureza o amplificar información sin suficiente elaboración.', 'clave_integracion': 'Usar la capacidad de escucha y filtrado antes de amplificar, manteniendo equilibrio entre receptividad y afirmación.', 'foco_interpretativo': 'La mitad del horóscopo ocupada por la figura es esencial para definir dónde opera su sensibilidad y proyección.', 'pagina_fuente_huber': '373-374'}, 'Animat': {'familia_catalogo': 'Siete figuras cuadrangulares con oposición', 'familia_color': 'tricolor', 'forma': 'cuadrangular orientada', 'tipo_dinamica': 'constructiva y emprendedora', 'dinamica_central': 'Pone en movimiento lo que estaba quieto y orienta energía, talento y pensamiento práctico hacia resultados concretos.', 'potencial': 'Imaginación aplicada, perseverancia, espíritu emprendedor y gran capacidad de llevar ideas a la práctica.', 'riesgo': 'Dominación, exceso de control sobre materia o personas y priorizar rendimiento por encima de comunicación o disfrute.', 'clave_integracion': 'Mantener la capacidad de construcción sin convertirla en necesidad de controlar todo el proceso.', 'foco_interpretativo': 'El vértice más agudo concentra la dirección de avance; distinguir la zona de escucha azul-verde de la zona de acción roja.', 'pagina_fuente_huber': '374-376'}, 'Provocat': {'familia_catalogo': 'Siete figuras cuadrangulares con oposición', 'familia_color': 'rojo-verde con base azul', 'forma': 'cuadrangular', 'tipo_dinamica': 'provocadora y orientada al rendimiento', 'dinamica_central': 'Detecta lo que no funciona y provoca movimiento para sacar a la luz asuntos ocultos o vencer resistencias.', 'potencial': 'Valor para señalar problemas, concentración intensa, pensamiento crítico y capacidad de impulsar mejoras.', 'riesgo': 'Intranquilidad permanente, visión en túnel, convertir detalles irrelevantes en problemas o despreciar descanso y placer.', 'clave_integracion': 'Usar la provocación al servicio del aprendizaje y recordar periódicamente que una mirada intensa también necesita perspectiva.', 'foco_interpretativo': 'La estructura combina rendimiento y pensamiento; observar qué planeta concentra la presión y qué línea azul almacena experiencia.', 'pagina_fuente_huber': '376-378'}, 'Arena': {'familia_catalogo': 'Siete figuras cuadrangulares con oposición', 'familia_color': 'tricolor', 'forma': 'cuadrangular', 'tipo_dinamica': 'conflictiva-mediadora', 'dinamica_central': 'Entra en situaciones de confrontación para comprender posiciones opuestas y encontrar condiciones aceptables para ambas partes.', 'potencial': 'Mediación, capacidad estratégica, comprensión de conflictos y habilidad para combinar poder con conocimiento.', 'riesgo': 'Meterse innecesariamente en disputas, vivir en confrontación o depender de conflictos externos para activar el aprendizaje.', 'clave_integracion': 'Elegir conscientemente qué conflictos merecen implicación y usar la confrontación para construir acuerdos.', 'foco_interpretativo': 'La oposición define los contendientes; las subfiguras de aprendizaje muestran las vías para comprender y negociar.', 'pagina_fuente_huber': '378-379'}, 'Canalizador': {'familia_catalogo': 'Siete figuras cuadrangulares con oposición', 'familia_color': 'tricolor equilibrado', 'forma': 'cuadrangular', 'tipo_dinamica': 'conductora y reguladora', 'dinamica_central': 'Percibe corrientes y sabe moverse dentro de ellas, dirigirlas o canalizar fuerzas, tendencias y estados colectivos.', 'potencial': 'Equilibrio entre rendimiento, sensibilidad y sustancia; capacidad de conducir procesos complejos sin perder estabilidad.', 'riesgo': 'Manipulación, invasión de la intimidad, exceso de voluntad o aislamiento por manejar fuerzas que otros viven como intensas.', 'clave_integracion': 'Canalizar sin apropiarse: respetar autonomía y límites mientras se orienta la energía disponible.', 'foco_interpretativo': 'Los tres colores están equilibrados; observar qué corriente representa la oposición y hacia dónde la estructura la conduce.', 'pagina_fuente_huber': '379-381'}, 'Deco': {'familia_catalogo': 'Siete figuras cuadrangulares con oposición', 'familia_color': 'tricolor con exterior rojo', 'forma': 'cuadrangular quiral', 'tipo_dinamica': 'decodificadora y perfeccionista', 'dinamica_central': 'Filtra, ordena y traduce señales complejas, detectando defectos, procedencias y patrones que otros no perciben.', 'potencial': 'Capacidad de decodificación, diplomacia, discriminación fina y traducción de contenidos complejos a formas comprensibles.', 'riesgo': 'Perfeccionismo, reserva excesiva, búsqueda interminable de solución o rigidez en el propio sistema de orden.', 'clave_integracion': 'Aceptar soluciones suficientemente buenas y usar la capacidad crítica para clarificar, no para perseguir una perfección imposible.', 'foco_interpretativo': 'Mantener su orientación quiral frente a Trampolín; distinguir exterior rojo e interior azul/verde.', 'pagina_fuente_huber': '381-383'}, 'Bijou': {'familia_catalogo': 'Siete figuras cuadrangulares con oposición', 'familia_color': 'azul-verde con componente roja', 'forma': 'cuadrangular', 'tipo_dinamica': 'armónica-mental', 'dinamica_central': 'Combina sustancia armónica con alta sensibilidad mental y capacidad para resolver conflictos mediante comprensión y argumentación.', 'potencial': 'Sabiduría aplicada, objetividad, diplomacia, capacidad de convicción y resolución intelectual de tensiones.', 'riesgo': 'Perfeccionismo, sensación de superioridad, aislamiento o permitir que otros se apoyen demasiado en su estabilidad.', 'clave_integracion': 'Compartir comprensión sin convertirse en sostén permanente de los demás ni separarse emocionalmente.', 'foco_interpretativo': 'Diferenciar el lado azul de sustancia del lado verde de sensibilidad y la oposición que exige mediación.', 'pagina_fuente_huber': '383-385'}, 'Detect': {'familia_catalogo': 'Cuatro trapezoides con talento', 'familia_color': 'tricolor', 'forma': 'trapezoide periférico', 'tipo_dinamica': 'móvil y perceptiva', 'dinamica_central': 'Detecta información y la incorpora rápidamente a estructuras de conocimiento ya disponibles.', 'potencial': 'Observación, rapidez de aprendizaje, higiene mental y capacidad de instalarse o adaptarse con facilidad.', 'riesgo': 'Orientarse demasiado hacia tareas del entorno, descuidar desarrollo propio o sentirse expuesto en la gran zona abierta.', 'clave_integracion': 'Mantener la excelente capacidad de detección al servicio también del propio proceso, no sólo de demandas externas.', 'foco_interpretativo': 'La gran zona abierta y la posición periférica son esenciales; sus subfiguras de ojo, aprendizaje y talento son funciones integradas.', 'pagina_fuente_huber': '386-388'}, 'Grabadora': {'familia_catalogo': 'Cuatro trapezoides con talento', 'familia_color': 'tricolor', 'forma': 'trapezoide', 'tipo_dinamica': 'acumulativa y estable', 'dinamica_central': 'Registra, ordena y almacena conocimientos o experiencias, manteniendo atención sostenida hasta haber aprendido suficiente.', 'potencial': 'Memoria funcional, aprendizaje sistemático, capacidad de ordenar información y construir experiencia estable.', 'riesgo': 'Persistir demasiado tiempo en una misma cuestión, acumular sin renovar o dirigirse hacia objetivos poco definidos.', 'clave_integracion': 'Saber cuándo el aprendizaje está completo y permitir el paso a una nueva área sin perder lo almacenado.', 'foco_interpretativo': 'El talento pequeño funciona como almacén; las figuras de búsqueda/aprendizaje aportan el material que se registra.', 'pagina_fuente_huber': '388-390'}, 'Model': {'familia_catalogo': 'Cuatro trapezoides con talento', 'familia_color': 'tricolor', 'forma': 'trapezoide', 'tipo_dinamica': 'formativa y transformadora', 'dinamica_central': 'Construye modelos, prototipos o formas y los modifica hasta que pueden representar o materializar una idea.', 'potencial': 'Modelado creativo, capacidad para remodelar estructuras, transformar conocimiento en forma y aprender mediante prototipos.', 'riesgo': 'Quedar atrapado en el modelo, confundir representación con realidad o perfeccionar indefinidamente antes de materializar.', 'clave_integracion': 'Usar el modelo como herramienta provisional y permitir que la experiencia real corrija la forma.', 'foco_interpretativo': 'Observar cómo se enlazan talento, búsqueda y aprendizaje y qué planeta recibe el impulso de remodelación.', 'pagina_fuente_huber': '390-392'}, 'Represent': {'familia_catalogo': 'Cuatro trapezoides con talento', 'familia_color': 'tricolor', 'forma': 'trapezoide', 'tipo_dinamica': 'representativa y comprometida', 'dinamica_central': 'Toma partido, hace visible una idea o valor y puede representarlo ante una colectividad con presencia y convicción.', 'potencial': 'Autenticidad, capacidad de representación, presencia, percepción despierta y compromiso con una idea o función.', 'riesgo': 'Identificación rígida con una causa, convicción excesiva o fanatización de aquello que se representa.', 'clave_integracion': 'Representar sin confundirse completamente con lo representado y conservar apertura a revisión.', 'foco_interpretativo': 'La dirección de la figura muestra qué contenido se presenta al mundo; integrar gran trígono y triángulos de aprendizaje como recursos.', 'pagina_fuente_huber': '392-394'}, 'Escenario': {'familia_catalogo': 'Cinco figuras cuadrangulares poco comunes', 'familia_color': 'tricolor con predominio verde', 'forma': 'trapecio', 'tipo_dinamica': 'relacional y polar', 'dinamica_central': 'Explora roles, subpersonalidades y polaridades humanas, actuando como puente entre mundos o perspectivas diferentes.', 'potencial': 'Gran comprensión de personas, capacidad de explicar estructuras humanas y flexibilidad para moverse entre roles y puntos de vista.', 'riesgo': 'Distancia personal, coleccionar roles sin implicarse o quedar atrapado en la observación de polaridades.', 'clave_integracion': 'Mantener apertura a múltiples roles sin perder una referencia interior propia.', 'foco_interpretativo': 'Contiene tres polaridades; observar la mitad vacía del horóscopo y los dos triángulos de excitación superpuestos.', 'pagina_fuente_huber': '396-398'}, 'Gorro mágico': {'familia_catalogo': 'Cinco figuras cuadrangulares poco comunes', 'familia_color': 'verde-azul con rojo', 'forma': 'trapecio pequeño', 'tipo_dinamica': 'discreta y perceptiva', 'dinamica_central': 'Se mueve con discreción entre personas y ambientes, recoge información y aprende sin necesidad de dejar una huella fuerte.', 'potencial': 'Escucha, discreción, servicio desinteresado, adaptación emocional e integración rápida de información.', 'riesgo': 'Invisibilizarse demasiado, evitar compromiso, vivir de forma excesivamente indirecta o retirarse cuando aparece una huella personal.', 'clave_integracion': 'Conservar la libertad y discreción sin renunciar a ocupar un lugar propio cuando sea necesario.', 'foco_interpretativo': 'Dos ojos y dos triángulos de aprendizaje pequeños funcionan conjuntamente como sistema de captación y aprendizaje.', 'pagina_fuente_huber': '398-401'}, 'Ovni': {'familia_catalogo': 'Cinco figuras cuadrangulares poco comunes', 'familia_color': 'tricolor', 'forma': 'cuadrangular', 'tipo_dinamica': 'interior potente, exterior adaptable', 'dinamica_central': 'Una envoltura sensible y armónica oculta una intensa carga interior capaz de intervenir con contundencia cuando algo esencial lo exige.', 'potencial': 'Profundidad, capacidad de individualización, adaptación al entorno y fuerza para afrontar tareas difíciles.', 'riesgo': 'Contraste brusco entre apariencia suave y respuesta tajante, aislamiento o acumular demasiada presión antes de actuar.', 'clave_integracion': 'Hacer visible gradualmente la fuerza interior para que no aparezca sólo en momentos extremos.', 'foco_interpretativo': 'Distinguir envoltura azul-verde de las diagonales rojas cruzadas y atender al quincuncio cercano al centro.', 'pagina_fuente_huber': '401-403'}, 'Surfista': {'familia_catalogo': 'Cinco figuras cuadrangulares poco comunes', 'familia_color': 'tricolor', 'forma': 'cuadrangular puntiaguda', 'tipo_dinamica': 'muy dinámica y orientada a meta', 'dinamica_central': 'Percibe el equilibrio de fuerzas y se lanza con precisión hacia una meta, adaptándose a dinámicas cambiantes.', 'potencial': 'Desarrollo rápido, fuerte orientación, sensibilidad al equilibrio y capacidad de encontrar posibilidades de cambio en situaciones difíciles.', 'riesgo': 'Ir demasiado directamente al objetivo, ignorar elementos laterales o no valorar suficientemente lo alcanzado.', 'clave_integracion': 'Mantener la dirección sin perder visión periférica ni la sensibilidad hacia aquello que queda fuera del objetivo.', 'foco_interpretativo': 'El planeta tricolor del ángulo agudo es central y concentra autocontrol, dirección y conciencia.', 'pagina_fuente_huber': '403-405'}, 'Oscilo': {'familia_catalogo': 'Cinco figuras cuadrangulares poco comunes', 'familia_color': 'verde-azul con tensión interna', 'forma': 'cuadrangular zigzagueante', 'tipo_dinamica': 'sensitiva y oscilante', 'dinamica_central': 'Registra oscilaciones del entorno, las refleja y vuelve periódicamente sobre procesos para comprobar su estado.', 'potencial': 'Percepción global de sentimientos, paciencia, previsión, vigilancia de procesos y capacidad para detectar patrones inconscientes.', 'riesgo': 'Tensión interna difícil de identificar, revisiones repetitivas, incomprensión por parte de otros o exceso de vigilancia.', 'clave_integracion': 'Confiar en la percepción sin convertirla en comprobación permanente y expresar de forma comprensible lo que se detecta.', 'foco_interpretativo': 'El zigzag verde funciona como amplificador perceptivo; leer conjuntamente tres líneas verdes y dos azules.', 'pagina_fuente_huber': '405-407'}}


def _registrar_catalogo_interpretativo_huber_26():
    for _nombre, _guia in CATALOGO_INTERPRETATIVO_HUBER_26.items():
        INDICE_INTERPRETATIVO_HUBER_20[_nombre] = _nombre


_registrar_catalogo_interpretativo_huber_26()


def obtener_guia_interpretativa_huber_completa(figura_o_tipo):
    """
    Resuelve una guía interpretativa de cualquiera de las 46 figuras Huber.
    Devuelve copia independiente y metadatos de fuente.
    """
    if isinstance(figura_o_tipo, dict):
        candidatos = [
            figura_o_tipo.get("nombre_canonico"),
            figura_o_tipo.get("tipo"),
        ]
    else:
        candidatos = [figura_o_tipo]

    for candidato in candidatos:
        if candidato in CATALOGO_INTERPRETATIVO_HUBER_26:
            guia = dict(CATALOGO_INTERPRETATIVO_HUBER_26[candidato])
            guia["nombre_huber"] = candidato
            guia["nivel_catalogo_interpretativo"] = "variante"
            guia["fuente"] = {
                "obra": "Astrología de la figura de aspectos",
                "autores": "Bruno Huber, Louise Huber, Michael-Alexander Huber",
                "edicion": "API Ediciones España, 2003",
                "pagina": guia.get("pagina_fuente_huber"),
            }
            return guia

    guia = obtener_guia_interpretativa_huber(figura_o_tipo)
    if guia is not None:
        guia["nivel_catalogo_interpretativo"] = "fundamental"
    return guia


def enriquecer_figura_con_guia_huber_completa(figura):
    guia = obtener_guia_interpretativa_huber_completa(figura)

    if guia is None:
        figura.pop("guia_interpretativa_huber", None)
        figura["soporte_interpretativo_huber"] = False
        figura.pop("nombre_interpretativo_huber", None)
        return figura

    figura["guia_interpretativa_huber"] = guia
    figura["soporte_interpretativo_huber"] = True
    figura["nombre_interpretativo_huber"] = guia["nombre_huber"]
    figura["nivel_catalogo_interpretativo"] = guia[
        "nivel_catalogo_interpretativo"
    ]
    return figura

# Compatibilidad: desde Fase 7, el enriquecedor público usa el catálogo completo.
enriquecer_figura_con_guia_huber = enriquecer_figura_con_guia_huber_completa

# ─── FIN HUBER FASE 7 ─────────────────────────────────────────────────────────



# ─── HUBER FASE 8: PAQUETE DETERMINISTA PARA INTERPRETACIÓN IA ───────────────

HUBER_FASE8_PAQUETE_IA_APLICADA = True


def _copiar_ref_huber(ref):
    return {
        "id": ref.get("id"),
        "tipo": ref.get("tipo", ""),
        "nombre_canonico": ref.get(
            "nombre_canonico",
            ref.get("tipo", ""),
        ),
        "puntos": list(ref.get("puntos", []) or []),
    }



def _aspectos_por_simbolo_huber(figura, simbolo):
    return [
        a
        for a in (figura.get("aspectos", []) or [])
        if a.get("simbolo") == simbolo
    ]


def _puntos_aspecto_huber(aspecto):
    if not aspecto:
        return []
    return [
        aspecto.get("p1"),
        aspecto.get("p2"),
    ]


def _tercer_punto_huber(figura, p1, p2):
    puntos = puntos_reales_figura(figura)
    otros = [
        p
        for p in puntos
        if p not in (p1, p2)
    ]
    return otros[0] if len(otros) == 1 else None


def _vertice_comun_huber(aspectos):
    """
    Devuelve el punto común a dos o más aspectos.
    """
    if not aspectos:
        return None

    comunes = None

    for aspecto in aspectos:
        puntos = {
            aspecto.get("p1"),
            aspecto.get("p2"),
        }
        puntos.discard(None)

        comunes = (
            puntos
            if comunes is None
            else comunes & puntos
        )

    if comunes and len(comunes) == 1:
        return next(iter(comunes))

    return None


def _datos_espaciales_punto_huber(carta, punto):
    """
    Datos espaciales calculados, sin interpretación.
    """
    if not carta or not punto:
        return None

    datos = None

    if punto in (carta.get("planetas", {}) or {}):
        datos = carta["planetas"][punto]
    elif punto == "Ascendente":
        datos = carta.get("asc")
    elif punto == "Medio Cielo":
        datos = carta.get("mc")

    if not isinstance(datos, dict):
        return None

    salida = {}

    if datos.get("lon") is not None:
        salida["longitud"] = round(float(datos["lon"]) % 360.0, 4)

    if datos.get("signo") is not None:
        salida["signo"] = datos.get("signo")

    if datos.get("grado") is not None:
        salida["grado"] = round(float(datos.get("grado")), 2)

    if datos.get("casa") is not None:
        salida["casa"] = datos.get("casa")

    return salida or None


def calcular_roles_direccionales_huber(figura, carta=None):
    """
    Calcula SOLO direcciones y roles que se deducen de la geometría
    ya validada por Python.

    No interpreta psicológicamente la dirección.
    No decide por imagen.
    No confunde este concepto con la dirección de orbe de un aspecto.

    Los nombres de los roles siguen el foco interpretativo del catálogo
    Huber incorporado al programa.
    """
    tipo = str(
        figura.get("nombre_canonico")
        or figura.get("tipo")
        or ""
    ).strip()

    roles = {}

    # ------------------------------------------------------------
    # T-cuadrada / Triángulo de rendimiento
    # ------------------------------------------------------------
    if tipo in ("T-cuadrada", "T-cuadrada compuesta"):
        apice = figura.get("apice")

        if apice:
            roles["apice_descarga"] = (
                list(apice)
                if isinstance(apice, tuple)
                else apice
            )

        oposicion = figura.get("oposicion")
        if oposicion:
            roles["base_oposicion"] = (
                [list(x) if isinstance(x, tuple) else x for x in oposicion]
                if isinstance(oposicion, tuple)
                else oposicion
            )

        if apice:
            roles["direccion_funcional"] = "oposicion_hacia_apice"

    # ------------------------------------------------------------
    # Yod / Figura de proyección
    # ------------------------------------------------------------
    if tipo in ("Yod", "Figura de proyección"):
        apice = figura.get("apice") or figura.get("ápice")
        base = figura.get("base")

        if not apice:
            qs = _aspectos_por_simbolo_huber(figura, "⚻")
            if len(qs) == 2:
                apice = _vertice_comun_huber(qs)

        if not base:
            sextiles = _aspectos_por_simbolo_huber(figura, "✶")
            if sextiles:
                base = tuple(_puntos_aspecto_huber(sextiles[0]))

        if apice:
            roles["apice_proyeccion"] = apice
            roles["direccion_funcional"] = "base_hacia_apice"

        if base:
            roles["base"] = list(base) if isinstance(base, tuple) else base

    # ------------------------------------------------------------
    # Cometa
    # ------------------------------------------------------------
    if tipo == "Cometa":
        foco = figura.get("foco")
        opuesto = figura.get("oposicion_a")

        if foco and opuesto:
            roles["eje_oposicion"] = [opuesto, foco]
            roles["punto_unido_por_dos_sextiles"] = foco
            roles["polo_opuesto_del_gran_trigono"] = opuesto

            # El catálogo establece que el eje de oposición da dirección.
            # No llamamos "cabeza/cola" a los extremos porque esa etiqueta
            # no está resuelta inequívocamente por el detector actual.
            roles["direccion_funcional"] = "a_lo_largo_del_eje_de_oposicion"

    # ------------------------------------------------------------
    # Triángulo de talento pequeño
    # Trígono = base; dos sextiles = dirección de salida.
    # ------------------------------------------------------------
    if tipo == "Triángulo de talento pequeño":
        sextiles = _aspectos_por_simbolo_huber(figura, "✶")
        trigonos = _aspectos_por_simbolo_huber(figura, "△")

        if len(sextiles) == 2:
            salida = _vertice_comun_huber(sextiles)
            if salida:
                roles["vertice_salida"] = salida
                roles["direccion_funcional"] = "base_armonica_hacia_vertice_salida"

        if len(trigonos) == 1:
            roles["base_armonica"] = _puntos_aspecto_huber(trigonos[0])

    # ------------------------------------------------------------
    # Triángulo de ambivalencia
    # La oposición es la tensión; el tercer vértice azul regula.
    # ------------------------------------------------------------
    if tipo == "Triángulo de ambivalencia":
        opos = _aspectos_por_simbolo_huber(figura, "☍")

        if len(opos) == 1:
            p1, p2 = _puntos_aspecto_huber(opos[0])
            tercero = _tercer_punto_huber(figura, p1, p2)

            roles["oposicion"] = [p1, p2]

            if tercero:
                roles["vertice_regulador"] = tercero
                roles["direccion_funcional"] = "oposicion_hacia_vertice_regulador"

    # ------------------------------------------------------------
    # Figuras de aprendizaje: no inventamos un sentido psicológico
    # horario/antihorario. Sí damos la secuencia geométrica exacta
    # de tipos de aspecto que el libro utiliza.
    # ------------------------------------------------------------
    secuencias = {
        "Triángulo de aprendizaje pequeño": ["□", "⚺", "✶"],
        "Triángulo de aprendizaje mediano": ["△", "□", "⚺"],
        "Triángulo de aprendizaje grande": ["⚻", "□", "✶"],
    }

    if tipo in secuencias:
        pasos = []

        for simbolo in secuencias[tipo]:
            encontrados = _aspectos_por_simbolo_huber(figura, simbolo)

            if len(encontrados) == 1:
                a = encontrados[0]
                pasos.append({
                    "aspecto": simbolo,
                    "entre": _puntos_aspecto_huber(a),
                })

        if pasos:
            roles["secuencia_geometrica"] = pasos

    # Triángulo de aprendizaje genérico (quincuncio + trígono + cuadratura)
    if tipo == "Triángulo de aprendizaje":
        pasos = []

        for simbolo in ("□", "⚻", "△"):
            encontrados = _aspectos_por_simbolo_huber(figura, simbolo)

            if len(encontrados) == 1:
                a = encontrados[0]
                pasos.append({
                    "aspecto": simbolo,
                    "entre": _puntos_aspecto_huber(a),
                })

        if pasos:
            roles["secuencia_geometrica"] = pasos

    # ------------------------------------------------------------
    # Figura de búsqueda
    # ------------------------------------------------------------
    if tipo == "Figura de búsqueda":
        trigonos = _aspectos_por_simbolo_huber(figura, "△")

        if len(trigonos) == 1:
            base = _puntos_aspecto_huber(trigonos[0])
            roles["base_disponible"] = base

            tercero = _tercer_punto_huber(figura, base[0], base[1])
            if tercero:
                roles["vertice_busqueda"] = tercero
                roles["direccion_funcional"] = "base_hacia_vertice_busqueda"

    # ------------------------------------------------------------
    # Ojo pequeño / Figura de información
    # ------------------------------------------------------------
    if tipo in ("Ojo pequeño", "Figura de información (ojo)"):
        semis = _aspectos_por_simbolo_huber(figura, "⚺")
        sextiles = _aspectos_por_simbolo_huber(figura, "✶")

        if len(semis) == 2:
            foco = _vertice_comun_huber(semis)
            if foco:
                roles["vertice_observacion"] = foco

        if len(sextiles) == 1:
            roles["base_informacion"] = _puntos_aspecto_huber(sextiles[0])

    # ------------------------------------------------------------
    # Información espacial objetiva de los roles calculados.
    # ------------------------------------------------------------
    puntos_roles = set()

    def recoger(valor):
        if isinstance(valor, str) and valor in ORDEN_PUNTOS:
            puntos_roles.add(valor)
        elif isinstance(valor, (list, tuple)):
            for x in valor:
                recoger(x)
        elif isinstance(valor, dict):
            for x in valor.values():
                recoger(x)

    recoger(roles)

    if puntos_roles and carta:
        espacial = {}

        for punto in ordenar_puntos(list(puntos_roles)):
            datos = _datos_espaciales_punto_huber(carta, punto)
            if datos:
                espacial[punto] = datos

        if espacial:
            roles["posicion_roles"] = espacial

    return roles


def _roles_geometricos_huber(figura, carta=None):
    """
    Reúne roles ya presentes y añade roles direccionales calculables
    de forma determinista desde la geometría.
    """
    claves = (
        "apice",
        "ápice",
        "vertice",
        "vértice",
        "vertices",
        "base",
        "oposicion",
        "oposición",
        "fuente",
        "destino",
        "direccion",
        "dirección",
        "sentido",
        "eje",
        "cola",
        "cabeza",
        "punto_focal",
        "planeta_focal",
        "planeta_apice",
        "planeta_ápice",
    )

    salida = {}

    for clave in claves:
        if clave in figura and figura.get(clave) not in (None, "", [], {}):
            valor = figura.get(clave)
            salida[clave] = (
                list(valor)
                if isinstance(valor, tuple)
                else valor
            )

    direccionales = calcular_roles_direccionales_huber(
        figura,
        carta=carta,
    )

    if direccionales:
        salida["direccion_huber_calculada"] = direccionales

    return salida


def construir_paquete_interpretacion_huber(
    figura,
    figuras_estructurales=None,
    carta=None,
):
    """
    Construye el contrato de datos que puede recibir la IA.

    Principios:
    - la geometría procede exclusivamente de Python;
    - la guía procede del catálogo Huber validado;
    - las subfiguras se aportan como contexto, no como bloques duplicados;
    - no se inventan roles geométricos ausentes;
    - no decide por sí mismo qué figuras se publican.
    """
    guia = obtener_guia_interpretativa_huber_completa(figura)

    if guia is None:
        return None

    puntos = list(puntos_reales_figura(figura))
    por_id = {}

    if figuras_estructurales:
        por_id = {
            f.get("id_estructural"): f
            for f in figuras_estructurales
            if f.get("id_estructural")
        }

    subfiguras = []
    vistos = set()

    refs = list(figura.get("subfiguras", []) or [])

    # Fase 5 puede haber añadido contexto editorial ya integrado.
    refs.extend(
        figura.get("subfiguras_editoriales_integradas", []) or []
    )

    for ref in refs:
        clave = (ref.get("id"), ref.get("tipo"))
        if clave in vistos:
            continue
        vistos.add(clave)

        hija = por_id.get(ref.get("id"))
        tipo_hija = (
            hija.get("tipo", "")
            if hija is not None
            else ref.get("tipo", "")
        )

        guia_hija = (
            obtener_guia_interpretativa_huber_completa(hija)
            if hija is not None
            else obtener_guia_interpretativa_huber_completa(tipo_hija)
        )

        subfiguras.append({
            "id": ref.get("id"),
            "tipo": tipo_hija,
            "puntos": (
                list(puntos_reales_figura(hija))
                if hija is not None
                else list(ref.get("puntos", []) or [])
            ),
            "guia_huber": guia_hija,
            "funcion_en_paquete": "contexto_integrado",
        })

    familia_editorial = (
        figura.get("familia_editorial_huber_2026")
        or {}
    )
    puntos_editoriales = list(
        figura.get("puntos_editoriales_familia_huber_2026")
        or familia_editorial.get("puntos_editoriales_permitidos")
        or puntos
    )

    paquete = {
        "version_contrato": "huber-ia-v3-familias-editoriales",
        "id_estructural": figura.get("id_estructural"),
        "seleccion_huber_2026": figura.get("seleccion_huber_2026"),
        "fase_seleccion_huber_2026": figura.get("fase_seleccion_huber_2026"),
        "motivo_seleccion_huber_2026": figura.get("motivo_seleccion_huber_2026"),
        "aspectos_nuevos_huber_2026": figura.get("aspectos_nuevos_huber_2026", []),
        "aspectos_reutilizados_huber_2026": figura.get("aspectos_reutilizados_huber_2026", []),
        "aspectos_apoyo_vertice_colectivo": [
            {
                "p1": a.get("p1"),
                "p2": a.get("p2"),
                "nombre": a.get("nombre"),
                "simbolo": a.get("simbolo"),
                "orbe": a.get("orbe"),
            }
            for a in figura.get("aspectos_apoyo_vertice_colectivo", []) or []
        ],
        "variantes_geometricas_colectivas": figura.get(
            "variantes_geometricas_colectivas",
            [],
        ),
        "estado_composicion_huber": figura.get("estado_composicion_huber"),
        "id_estructural": figura.get("id_estructural"),
        "tipo_interno": figura.get("tipo", ""),
        "nombre_huber": guia.get("nombre_huber"),
        "nombre_canonico": figura.get(
            "nombre_canonico",
            guia.get("nombre_huber"),
        ),
        "nivel_catalogo_interpretativo": guia.get(
            "nivel_catalogo_interpretativo"
        ),
        "estado_estructural": figura.get(
            "estado_estructural",
            "independiente",
        ),
        "estado_editorial": figura.get("estado_editorial"),
        "nivel_composicion": figura.get("nivel_composicion", 0),
        "puntos": puntos,
        "puntos_editoriales_permitidos": puntos_editoriales,
        "familia_editorial_huber_2026": familia_editorial or None,
        "variantes_integradas_huber_2026": list(
            figura.get("variantes_integradas_huber_2026", [])
            or []
        ),
        "roles_geometricos": _roles_geometricos_huber(figura, carta=carta),
        "guia_huber": guia,
        "subfiguras_integradas": subfiguras,
        "contenida_en": [
            _copiar_ref_huber(ref)
            for ref in figura.get("contenida_en", []) or []
        ],
        "reglas_redaccion": {
            "geometria_es_autoritativa": True,
            "no_inventar_aspectos": True,
            "no_inventar_roles": True,
            "no_reinterpretar_subfiguras_como_bloques_independientes": True,
            "integrar_planetas_con_dinamica_de_la_figura": True,
            "usar_guia_huber_como_marco_no_como_texto_literal": True,
        },
    }

    return paquete


def construir_paquetes_editoriales_huber(
    figuras_editoriales,
    figuras_estructurales=None,
):
    """
    Genera un paquete IA por cada figura que ya haya superado la selección
    editorial. No altera la selección.
    """
    paquetes = []

    for figura in figuras_editoriales:
        paquete = construir_paquete_interpretacion_huber(
            figura,
            figuras_estructurales=figuras_estructurales,
        )
        if paquete is not None:
            paquetes.append(paquete)

    return paquetes

# ─── FIN HUBER FASE 8 ─────────────────────────────────────────────────────────



# ─── HUBER FASE 10: APERTURA EDITORIAL COMPLETA ───────────────────────────────
HUBER_FASE10_APERTURA_EDITORIAL_46 = True

TIPOS_EDITORIALES_COMPLEMENTARIOS = {
    "T-cuadrada compuesta",
    "Yod con Ojo pequeño en la base",
    "Stellium",
    "Red de aprendizaje",
}

TIPOS_EDITORIALES_ALIAS_HUBER = {
    alias
    for alias in ALIAS_HUBER_POR_TIPO_INTERNO
    if alias
}

TIPOS_EDITORIALES_SOPORTADOS = (
    set(CATALOGO_HUBER_20.keys())
    | set(CATALOGO_HUBER_VARIANTES_26.keys())
    | TIPOS_EDITORIALES_ALIAS_HUBER
    | TIPOS_EDITORIALES_COMPLEMENTARIOS
)


def figura_soportada_editorialmente(figura):
    tipo = figura.get("tipo", "")

    if tipo not in TIPOS_EDITORIALES_SOPORTADOS:
        return False

    if (
        tipo in CATALOGO_HUBER_20
        or tipo in CATALOGO_HUBER_VARIANTES_26
        or tipo in TIPOS_EDITORIALES_ALIAS_HUBER
    ):
        return (
            obtener_guia_interpretativa_huber_completa(figura)
            is not None
        )

    return True

# ─── FIN HUBER FASE 10 ────────────────────────────────────────────────────────



# ─── HUBER FASE 5: SELECCIÓN EDITORIAL CON JERARQUÍA ─────────────────────────

HUBER_FASE5_EDITORIAL_APLICADA = True


def _ref_editorial_integrada(figura):
    return {
        "id": figura.get("id_estructural"),
        "tipo": figura.get("tipo", ""),
        "nombre_canonico": figura.get(
            "nombre_canonico",
            figura.get("tipo", ""),
        ),
        "puntos": list(puntos_reales_figura(figura)),
    }


def seleccionar_por_jerarquia_huber_editorial(figuras_estructurales):
    """
    Aplica la jerarquía de Fase 4 a la salida editorial sin perder
    información todavía no soportada por el texto/IA.

    Regla:
    - una figura no soportada editorialmente nunca sale;
    - una figura soportada e independiente sale;
    - una figura soportada contenida en otra figura SOPORTADA se integra
      en el padre y no genera un bloque editorial separado;
    - una figura soportada contenida únicamente en padres NO soportados
      se conserva provisionalmente para no hacer desaparecer información.

    No modifica la lista estructural original.
    """
    figuras = [dict(f) for f in figuras_estructurales]

    por_id = {
        f.get("id_estructural"): f
        for f in figuras
        if f.get("id_estructural")
    }

    candidatas = [
        f for f in figuras
        if figura_soportada_editorialmente(f)
    ]

    salida = []

    for figura in candidatas:
        padres_editoriales = []
        padres_bloqueados = []

        for ref in figura.get("contenida_en", []) or []:
            padre = por_id.get(ref.get("id"))

            # Si no podemos resolver el padre por ID, usamos el tipo
            # de la referencia como respaldo. La Fase 4 normalmente
            # proporciona IDs resolubles.
            tipo_padre = (
                padre.get("tipo", "")
                if padre is not None
                else ref.get("tipo", "")
            )

            if tipo_padre in TIPOS_EDITORIALES_SOPORTADOS:
                padres_editoriales.append((ref, padre))
            else:
                padres_bloqueados.append(ref)

        if padres_editoriales:
            figura["estado_editorial"] = "integrada"

            ref_hijo = _ref_editorial_integrada(figura)

            for ref_padre, padre in padres_editoriales:
                if padre is None:
                    continue

                integradas = padre.setdefault(
                    "subfiguras_editoriales_integradas",
                    [],
                )

                if not any(
                    existente.get("id") == ref_hijo.get("id")
                    and existente.get("tipo") == ref_hijo.get("tipo")
                    for existente in integradas
                ):
                    integradas.append(dict(ref_hijo))

            continue

        if padres_bloqueados:
            figura["estado_editorial"] = "visible_por_blindaje"
            figura["contenedores_no_editoriales"] = [
                {
                    "id": ref.get("id"),
                    "tipo": ref.get("tipo", ""),
                    "nombre_canonico": ref.get(
                        "nombre_canonico",
                        ref.get("tipo", ""),
                    ),
                    "puntos": list(ref.get("puntos", []) or []),
                }
                for ref in padres_bloqueados
            ]
        elif figura.get("estado_estructural") == "principal":
            figura["estado_editorial"] = "principal"
        else:
            figura["estado_editorial"] = "independiente"

        salida.append(figura)

    # Los padres soportados que recibieron subfiguras integradas deben
    # estar presentes en salida. Como son objetos copiados compartidos
    # dentro de `figuras`, la metadata añadida arriba ya está disponible.
    return salida

# ─── FIN HUBER FASE 5 ─────────────────────────────────────────────────────────



def obtener_ultimo_diagnostico_huber_2026():
    """Devuelve una copia serializable del último diagnóstico de selección."""
    import copy
    return copy.deepcopy(ULTIMO_DIAGNOSTICO_HUBER_2026)



def seleccionar_figuras_editoriales(carta, aspectos, figuras_estructurales):
    """
    Compatibilidad con código antiguo.

    Desde Huber 2026 la selección geométrica principal/rescate es la ÚNICA
    selección final. Esta función ya no aplica la vieja cadena:
    jerarquía editorial → absorción → unificación → subfiguras contenidas.

    Si recibe figuras ya seleccionadas, las devuelve sin volver a filtrarlas.
    Si recibe candidatas sin selección 2026, aplica la selección nueva.
    """
    aspectos_geo = filtrar_aspectos_geometria_huber_2026(aspectos)

    figuras = list(figuras_estructurales or [])

    if not all(
        figura.get("seleccion_huber_2026")
        for figura in figuras
    ):
        figuras = seleccionar_arquitectura_huber_2026(
            figuras,
            aspectos_geo,
        )

    for figura in figuras:
        normalizar_figura_huber(figura)
        anotar_catalogo_y_dinamica(carta, figura)

    return figuras





# ─── HUBER 2026: PRIORIDAD GEOMÉTRICA OBJETIVA + RESERVA + RESCATE ──────────────────
HUBER_2026_RESERVA_RESCATE_APLICADO = True

ULTIMO_DIAGNOSTICO_HUBER_2026 = {}

PUNTOS_HUBER_AMPLIADO_2026 = {
    "Sol", "Luna", "Mercurio", "Venus", "Marte",
    "Júpiter", "Saturno", "Urano", "Neptuno", "Plutón",
    "Ascendente", "Quirón", "Lilith", "Nodo Norte", "Nodo Sur",
}
PUNTOS_EXCLUIDOS_GEOMETRIA_HUBER_2026 = {"Medio Cielo"}

def _aspecto_clave_huber_2026(aspecto):
    p1, p2 = aspecto.get("p1"), aspecto.get("p2")
    if not p1 or not p2:
        return None
    a, b = sorted((p1, p2))
    return (a, b, aspecto.get("simbolo", ""))

def _es_eje_nodal_puro_huber_2026(aspecto):
    return {aspecto.get("p1"), aspecto.get("p2")} == {"Nodo Norte", "Nodo Sur"}

def filtrar_aspectos_geometria_huber_2026(aspectos):
    resultado = []
    for aspecto in aspectos:
        p1, p2 = aspecto.get("p1"), aspecto.get("p2")
        if p1 in PUNTOS_EXCLUIDOS_GEOMETRIA_HUBER_2026 or p2 in PUNTOS_EXCLUIDOS_GEOMETRIA_HUBER_2026:
            continue
        if _es_eje_nodal_puro_huber_2026(aspecto):
            continue
        if p1 not in PUNTOS_HUBER_AMPLIADO_2026 or p2 not in PUNTOS_HUBER_AMPLIADO_2026:
            continue
        resultado.append(aspecto)
    return resultado

def _claves_aspectos_figura_huber_2026(figura):
    claves = set()
    for aspecto in figura.get("aspectos", []) or []:
        clave = _aspecto_clave_huber_2026(aspecto)
        if clave is not None:
            claves.add(clave)
    return claves

def _numero_vertices_reales_huber_2026(figura):
    vertices = figura.get("vertices_huber") or []
    if vertices:
        return len(vertices)
    try:
        return len(set(puntos_reales_figura(figura)))
    except Exception:
        return len(set(figura.get("puntos", []) or []))


# Prioridad OPERATIVA derivada exclusivamente de la geometría detectada.
#
# No existe una tabla manual de nombres ni números de importancia. La figura
# que reserva primero sus aspectos se decide con datos estructurales que ya
# están presentes en la propia detección:
#
#   1. cuántas subfiguras Huber contiene/representa (contención geométrica);
#   2. cuántas líneas geométricas propias necesita;
#   3. cuántos vértices reales tiene;
#   4. menor orbe medio como desempate;
#   5. nombre/puntos únicamente para asegurar determinismo.
#
# Esto evita imponer una jerarquía psicológica o una lista arbitraria de
# prioridades. Una figura mayor gana únicamente cuando su geometría demuestra
# ser más integradora/compleja.

def _conteo_contencion_huber_2026(figura):
    """
    Devuelve dos medidas objetivas de contención:

    - descendientes: número total de subfiguras Huber representadas directa o
      indirectamente por la figura;
    - directas: número de subfiguras contenidas de primer nivel.

    ``anotar_jerarquia_composicion_huber`` ya ha calculado ``subfiguras`` antes
    de llegar a la selección. No se inventa ninguna prioridad nueva aquí.
    """
    directas = {
        ref.get("id")
        for ref in (figura.get("subfiguras", []) or [])
        if ref.get("id")
    }

    # Cada referencia puede contener a su vez metadatos de descendencia solo
    # en la figura original, no en el resumen. Para una prioridad estable y
    # local contamos las subfiguras directas y, como segunda señal, el nivel
    # de composición ya anotado. El número de directas es la medida principal.
    return len(directas)


def _orbe_medio_seleccion_huber_2026(figura):
    orbe_medio = figura.get("orbe_medio")
    if orbe_medio is None:
        orbes = [
            a.get("orbe")
            for a in figura.get("aspectos", []) or []
            if isinstance(a.get("orbe"), (int, float))
        ]
        orbe_medio = sum(orbes) / len(orbes) if orbes else 99.0

    try:
        return float(orbe_medio)
    except (TypeError, ValueError):
        return 99.0


def _longitudes_geometria_huber_2026(figura):
    """Longitudes reales de los vértices atómicos usados por la geometría."""
    por_punto = {}

    for aspecto in (figura.get("aspectos", []) or []):
        p1 = aspecto.get("p1")
        p2 = aspecto.get("p2")
        lon1 = aspecto.get("lon_p1")
        lon2 = aspecto.get("lon_p2")

        if p1 and isinstance(lon1, (int, float)):
            por_punto[p1] = float(lon1) % 360.0
        if p2 and isinstance(lon2, (int, float)):
            por_punto[p2] = float(lon2) % 360.0

    return sorted(por_punto.values())


def _tamano_espacial_huber_2026(figura):
    """
    Clasifica la figura por TAMAÑO espacial siguiendo el criterio de Huber.

    Huber distingue:
      - grande: envuelve el centro y se extiende por el horóscopo;
      - mediana: ocupa aproximadamente media carta y corta el centro;
      - pequeña: no entra en contacto con el centro.

    Traducción geométrica usada aquí:
      * GRANDE: los vértices no caben en ningún semicírculo (arco mínimo > 180°).
      * MEDIANA: no envuelve el centro, pero contiene una oposición, que es la
        relación que atraviesa/corta la zona central de la figura.
      * PEQUEÑA: el resto.

    No es una jerarquía por nombre de figura. Se calcula para cada aparición
    concreta a partir de la posición real de sus vértices.
    """
    longitudes = _longitudes_geometria_huber_2026(figura)

    # Si una estructura antigua no trae longitudes, no inventamos tamaño.
    # La dejamos en el nivel menor y los demás criterios actuarán de desempate.
    if len(longitudes) < 3:
        return "pequena", 1, None

    longitudes = sorted(set(round(x, 6) for x in longitudes))
    if len(longitudes) < 3:
        return "pequena", 1, None

    gaps = []
    for i, lon in enumerate(longitudes):
        siguiente = longitudes[(i + 1) % len(longitudes)]
        if i == len(longitudes) - 1:
            siguiente += 360.0
        gaps.append(siguiente - lon)

    max_gap = max(gaps)
    arco_minimo = 360.0 - max_gap

    # Tolerancia mínima solo para evitar ruido numérico, no para convertir
    # oposiciones amplias en figuras grandes.
    if arco_minimo > 180.0 + 1e-6:
        return "grande", 3, arco_minimo

    tiene_oposicion = any(
        (a.get("nombre") == "Oposición")
        or (a.get("simbolo") == "☍")
        or (a.get("angulo") == 180)
        for a in (figura.get("aspectos", []) or [])
    )

    if tiene_oposicion:
        return "mediana", 2, arco_minimo

    return "pequena", 1, arco_minimo


def _prioridad_geometrica_huber_2026(figura):
    """
    Orden operativo basado primero en el criterio de TAMAÑO de Huber.

    Huber indica expresamente que las figuras grandes tienen un papel más
    importante y que las medianas y pequeñas actúan como complementos,
    ampliaciones o modificaciones. Por eso la reserva de aspectos sigue:

      1) tamaño espacial real: grande > mediana > pequeña;
      2) más líneas geométricas propias;
      3) más vértices reales;
      4) menor orbe medio;
      5) nombre/puntos solo como desempate determinista.

    No existe una tabla manual de nombres ni una supuesta jerarquía psicológica
    1–46 atribuida a Huber.
    """
    nombre = (
        figura.get("nombre_canonico")
        or figura.get("tipo")
        or ""
    )

    tamano, rango_tamano, arco_minimo = _tamano_espacial_huber_2026(figura)
    n_lineas = len(_claves_aspectos_figura_huber_2026(figura))
    n_vertices = _numero_vertices_reales_huber_2026(figura)
    orbe_medio = _orbe_medio_seleccion_huber_2026(figura)

    # Metadatos diagnósticos: no cambian la geometría ni la interpretación.
    figura["tamano_huber_2026"] = tamano
    figura["arco_minimo_huber_2026"] = (
        round(arco_minimo, 3) if isinstance(arco_minimo, (int, float)) else None
    )

    return (
        -rango_tamano,
        -n_lineas,
        -n_vertices,
        orbe_medio,
        nombre,
        tuple(sorted(puntos_reales_figura(figura))),
    )

def _marcar_estado_huber_2026(figura, estado, fase, nuevas=None, reutilizadas=None, motivo=None):
    figura["seleccion_huber_2026"] = estado
    figura["fase_seleccion_huber_2026"] = fase
    figura["aspectos_nuevos_huber_2026"] = sorted(nuevas or [])
    figura["aspectos_reutilizados_huber_2026"] = sorted(reutilizadas or [])
    if motivo:
        figura["motivo_seleccion_huber_2026"] = motivo
    return figura


def _descendientes_composicion_huber_2026(figura, mapa_ids):
    """
    Devuelve los IDs de subfiguras representadas por una figura mayor.

    Se usa únicamente para valorar integridad geométrica durante la selección.
    No es una jerarquía psicológica ni interpretativa.
    """
    vistos = set()
    pendientes = [
        ref.get("id")
        for ref in (figura.get("subfiguras", []) or [])
        if ref.get("id")
    ]

    while pendientes:
        actual = pendientes.pop()
        if actual in vistos:
            continue
        vistos.add(actual)
        hija = mapa_ids.get(actual)
        if hija is None:
            continue
        pendientes.extend(
            ref.get("id")
            for ref in (hija.get("subfiguras", []) or [])
            if ref.get("id") and ref.get("id") not in vistos
        )

    return vistos


def _valor_candidata_global_huber_2026(figura, mapa_ids):
    """
    Valor OPERATIVO de una candidata para comparar CONJUNTOS completos.

    La puntuación favorece, de forma general y no por nombre de figura:
    - cubrir relaciones geométricas reales;
    - conservar una figura que representa subfiguras contenidas;
    - evitar fragmentar una geometría mayor en varias piezas menores;
    - usar número de vértices y orbe solo como desempates.

    No expresa importancia psicológica.
    """
    claves = _claves_aspectos_figura_huber_2026(figura)
    n_lineas = len(claves)
    descendientes = _descendientes_composicion_huber_2026(
        figura,
        mapa_ids,
    )
    n_desc = len(descendientes)
    n_vertices = _numero_vertices_reales_huber_2026(figura)

    orbes = [
        a.get("orbe")
        for a in (figura.get("aspectos", []) or [])
        if isinstance(a.get("orbe"), (int, float))
    ]
    orbe_medio = (
        sum(orbes) / len(orbes)
        if orbes
        else 99.0
    )

    # Integridad = relaciones propias + geometrías contenidas que la figura
    # mayor representa sin necesidad de fragmentarlas en piezas separadas.
    integridad = n_lineas + n_desc

    return {
        "integridad": integridad,
        "lineas": n_lineas,
        "subfiguras_representadas": n_desc,
        "vertices": n_vertices,
        "orbe_medio": float(orbe_medio),
    }


def _sumar_score_huber_2026(a, b):
    return tuple(x + y for x, y in zip(a, b))


def _mejor_score_huber_2026(a, b):
    """Devuelve True si el score lexicográfico a es mejor que b."""
    return b is None or a > b


def _componentes_conflicto_huber_2026(indices, conflictos):
    pendientes = set(indices)
    componentes = []

    while pendientes:
        inicio = min(pendientes)
        pila = [inicio]
        pendientes.remove(inicio)
        comp = []

        while pila:
            actual = pila.pop()
            comp.append(actual)
            vecinos = conflictos[actual] & pendientes
            for vecino in sorted(vecinos):
                pendientes.remove(vecino)
                pila.append(vecino)

        componentes.append(sorted(comp))

    return componentes


def _optimizar_principales_huber_2026(geometricas):
    """
    Resuelve globalmente el conjunto de figuras principales.

    Es un problema de set-packing: dos figuras principales no pueden usar
    la misma línea geométrica. En lugar de aceptar la primera candidata que
    aparece en una lista ordenada, se compara el conjunto completo.

    Objetivo lexicográfico del conjunto:
    1) máxima integridad geométrica total (líneas + subfiguras representadas),
    2) máxima cobertura de líneas,
    3) menos fragmentación (menos figuras para representar lo mismo),
    4) mayor número total de vértices,
    5) menor orbe acumulado.

    Ninguno de estos criterios es una jerarquía psicológica Huber.
    """
    if not geometricas:
        return []

    mapa_ids = {
        f.get("id_estructural"): f
        for f in geometricas
        if f.get("id_estructural")
    }

    claves = [
        _claves_aspectos_figura_huber_2026(f)
        for f in geometricas
    ]
    valores = [
        _valor_candidata_global_huber_2026(f, mapa_ids)
        for f in geometricas
    ]

    conflictos = [set() for _ in geometricas]
    for i in range(len(geometricas)):
        if not claves[i]:
            continue
        for j in range(i + 1, len(geometricas)):
            if claves[i] & claves[j]:
                conflictos[i].add(j)
                conflictos[j].add(i)

    indices_validos = [
        i for i, ks in enumerate(claves)
        if ks
    ]

    componentes = _componentes_conflicto_huber_2026(
        indices_validos,
        conflictos,
    )

    seleccion_total = []

    for componente in componentes:
        # Los componentes pequeños se resuelven exactamente mediante
        # memoización sobre el conjunto de candidatas todavía disponibles.
        local = list(componente)
        pos_local = {idx: pos for pos, idx in enumerate(local)}
        conflicto_bits = [0] * len(local)

        for pos, idx in enumerate(local):
            bits = 0
            for vecino in conflictos[idx]:
                if vecino in pos_local:
                    bits |= 1 << pos_local[vecino]
            conflicto_bits[pos] = bits

        score_individual = []
        for idx in local:
            v = valores[idx]
            # El tercer campo es -1: a igualdad de integridad/cobertura,
            # preferimos menos piezas y por tanto menos fragmentación.
            score_individual.append((
                v["integridad"],
                v["lineas"],
                -1,
                v["vertices"],
                -v["orbe_medio"],
            ))

        memo = {}

        def resolver(mask):
            if mask == 0:
                return (0, 0, 0, 0, 0.0), 0
            if mask in memo:
                return memo[mask]

            # Elegimos el nodo con más conflictos activos para reducir antes
            # el espacio de búsqueda.
            posiciones = [
                p for p in range(len(local))
                if mask & (1 << p)
            ]
            p = max(
                posiciones,
                key=lambda q: (
                    (conflicto_bits[q] & mask).bit_count(),
                    score_individual[q],
                    -q,
                ),
            )
            bit = 1 << p

            # Rama 1: excluir.
            score_ex, sel_ex = resolver(mask & ~bit)

            # Rama 2: incluir y retirar todos sus conflictos.
            mask_in = mask & ~bit & ~conflicto_bits[p]
            score_rest, sel_rest = resolver(mask_in)
            score_in = _sumar_score_huber_2026(
                score_individual[p],
                score_rest,
            )
            sel_in = sel_rest | bit

            if _mejor_score_huber_2026(score_in, score_ex):
                resultado = (score_in, sel_in)
            else:
                resultado = (score_ex, sel_ex)

            memo[mask] = resultado
            return resultado

        mask_inicial = (1 << len(local)) - 1
        _, seleccion_bits = resolver(mask_inicial)

        for pos, idx in enumerate(local):
            if seleccion_bits & (1 << pos):
                seleccion_total.append(geometricas[idx])

    # Orden determinista de presentación técnica.
    seleccion_total.sort(key=_prioridad_geometrica_huber_2026)
    return seleccion_total


def _optimizar_rescates_huber_2026(pendientes, huerfanas, ocupadas):
    """
    Selecciona globalmente el conjunto mínimo de rescates necesario para
    cubrir los aspectos integrables todavía huérfanos.

    A igualdad de número de figuras, favorece mayor integridad geométrica,
    menos reutilización de líneas ya ocupadas y menor orbe.
    """
    if not huerfanas:
        return []

    candidatos = []
    figuras_contenidas_eliminadas = [
        item["menor"]
        for item in contenciones_aplicadas
    ]

    pendientes_finales = (
        list(pendientes)
        + list(rescates_redundantes)
        + list(figuras_contenidas_eliminadas)
    )

    for figura in pendientes_finales:
        # Los rescates redundantes ya tienen un motivo más preciso.
        if figura.get("fase_seleccion_huber_2026") in {
            "depuracion_final_rescates",
            "contencion_entre_seleccionadas",
        }:
            continue

        claves = _claves_aspectos_figura_huber_2026(figura)
        cubre = claves & huerfanas
        if cubre:
            candidatos.append((figura, claves, cubre))

    if not candidatos:
        return []

    universo = sorted(huerfanas)
    bit_por_clave = {
        clave: 1 << i
        for i, clave in enumerate(universo)
    }
    objetivo = (1 << len(universo)) - 1

    mapa_ids = {
        f.get("id_estructural"): f
        for f, _, _ in candidatos
        if f.get("id_estructural")
    }

    masks = []
    scores = []
    for figura, claves, cubre in candidatos:
        mask = 0
        for clave in cubre:
            mask |= bit_por_clave[clave]
        masks.append(mask)

        valor = _valor_candidata_global_huber_2026(
            figura,
            mapa_ids,
        )
        reutilizadas = len(claves & ocupadas)
        scores.append((
            valor["integridad"],
            -reutilizadas,
            valor["vertices"],
            -valor["orbe_medio"],
        ))

    por_bit = [[] for _ in universo]
    for i, mask in enumerate(masks):
        for bit_pos in range(len(universo)):
            if mask & (1 << bit_pos):
                por_bit[bit_pos].append(i)

    memo = {}

    def resolver(restante):
        if restante == 0:
            # score: (-n_figuras, integridad, -reutilizacion, vertices, -orbe)
            return (0, 0, 0, 0, 0.0), ()
        if restante in memo:
            return memo[restante]

        bits_restantes = [
            b for b in range(len(universo))
            if restante & (1 << b)
        ]
        # Elegimos primero el huérfano con menos figuras capaces de cubrirlo.
        bit_obj = min(
            bits_restantes,
            key=lambda b: len(por_bit[b]),
        )

        mejor_score = None
        mejor_sel = None

        for i in por_bit[bit_obj]:
            nuevo_restante = restante & ~masks[i]
            score_rest, sel_rest = resolver(nuevo_restante)
            s = scores[i]
            score_total = (
                score_rest[0] - 1,
                score_rest[1] + s[0],
                score_rest[2] + s[1],
                score_rest[3] + s[2],
                score_rest[4] + s[3],
            )
            sel_total = tuple(sorted(sel_rest + (i,)))

            if (
                _mejor_score_huber_2026(score_total, mejor_score)
                or (
                    score_total == mejor_score
                    and (mejor_sel is None or sel_total < mejor_sel)
                )
            ):
                mejor_score = score_total
                mejor_sel = sel_total

        if mejor_score is None:
            resultado = ((-10**9, 0, 0, 0, -10**9), ())
        else:
            resultado = (mejor_score, mejor_sel)

        memo[restante] = resultado
        return resultado

    _, seleccion_indices = resolver(objetivo)
    seleccion = [
        candidatos[i][0]
        for i in dict.fromkeys(seleccion_indices)
    ]

    seleccion.sort(
        key=lambda f: (
            -len(_claves_aspectos_figura_huber_2026(f) & huerfanas),
            _prioridad_geometrica_huber_2026(f),
        )
    )
    return seleccion



def _mapa_vertice_colectivo_huber_2026(figura):
    """
    Mapea cada punto atómico al vértice visual/colectivo al que pertenece.

    Esto permite comparar dos figuras tal como realmente se dibujan:
    si Venus y Nodo Sur forman una conjunción usada como un único vértice,
    una arista que use Venus y otra que use Nodo Sur pueden representar la
    misma línea estructural del dibujo.
    """
    mapa = {}

    vertices = figura.get("vertices", []) or []
    for vertice in vertices:
        puntos = ordenar_puntos(
            list(vertice.get("puntos", []) or [])
        )
        if not puntos:
            continue

        token = (
            vertice.get("tipo", "Punto"),
            tuple(puntos),
        )
        for punto in puntos:
            mapa[punto] = token

    # Barrera de compatibilidad para figuras antiguas o sin ``vertices``.
    for punto in puntos_reales_figura(figura):
        mapa.setdefault(
            punto,
            ("Punto", (punto,)),
        )

    return mapa


def _claves_aspectos_colectivas_huber_2026(figura):
    """
    Devuelve las aristas de una figura normalizadas por VÉRTICE COLECTIVO.

    A diferencia de ``_claves_aspectos_figura_huber_2026`` no compara solo
    nombres atómicos. Compara la geometría que realmente llega a la miniatura.
    Dos realizaciones que usan miembros distintos del mismo stellium o
    conjunción producen la misma clave colectiva.
    """
    mapa = _mapa_vertice_colectivo_huber_2026(figura)
    claves = set()

    for aspecto in figura.get("aspectos", []) or []:
        p1 = aspecto.get("p1")
        p2 = aspecto.get("p2")
        simbolo = aspecto.get("simbolo")

        if not p1 or not p2 or not simbolo:
            continue

        v1 = mapa.get(p1, ("Punto", (p1,)))
        v2 = mapa.get(p2, ("Punto", (p2,)))

        # Un aspecto interno al mismo vértice colectivo no es una arista de
        # la figura; tampoco se dibuja como tal en la miniatura.
        if v1 == v2:
            continue

        extremos = tuple(sorted((repr(v1), repr(v2))))
        claves.add((extremos[0], extremos[1], simbolo))

    return claves


def _claves_seleccion_huber_2026(figura):
    """
    Clave ÚNICA de línea para reserva, rescate, cobertura y contención.

    La selección debe comparar la geometría tal como realmente se representa:
    un Stellium o una Conjunción funcionan como un único vértice colectivo.
    Por eso Venus–Plutón y Marte–Plutón son la misma línea estructural cuando
    Venus y Marte pertenecen al mismo vértice colectivo.

    Si una figura antigua no trae vértices colectivos, se conserva la clave
    atómica original como compatibilidad.
    """
    colectivas = _claves_aspectos_colectivas_huber_2026(figura)
    if colectivas:
        return colectivas
    return _claves_aspectos_figura_huber_2026(figura)


def integrar_subfiguras_seleccionadas_huber_2026(figuras):
    """Integra subfiguras realmente contenidas tras la selección global.

    La comparación se hace en DOS niveles:

    1. aristas atómicas exactas;
    2. aristas normalizadas por vértices colectivos (stellium/conjunción).

    El segundo nivel es imprescindible porque dos figuras pueden verse como
    la misma geometría o una geometría contenida aunque internamente una use,
    por ejemplo, Mercurio y otra Luna dentro del mismo stellium.

    Una figura menor se integra únicamente cuando:
      * ambas son figuras geométricas seleccionadas (no Stellium);
      * todas sus aristas estructurales están contenidas en la mayor;
      * la mayor aporta al menos una arista adicional;
      * o bien existe una contención Huber documentada y la inclusión se
        verifica en la geometría colectiva.

    El simple solapamiento de algunas líneas NO basta.
    """
    figuras = list(figuras or [])
    geometricas = [f for f in figuras if f.get("tipo") != "Stellium"]
    complementarias = [f for f in figuras if f.get("tipo") == "Stellium"]

    datos = []
    for i, figura in enumerate(geometricas):
        atomicas = _claves_aspectos_figura_huber_2026(figura)
        colectivas = _claves_aspectos_colectivas_huber_2026(figura)
        if atomicas or colectivas:
            datos.append({
                "indice": i,
                "figura": figura,
                "atomicas": atomicas,
                "colectivas": colectivas,
            })

    absorbidas = set()
    contenedor_de = {}
    criterio_de = {}

    def contiene(menor, mayor):
        a_m = menor["atomicas"]
        a_M = mayor["atomicas"]
        c_m = menor["colectivas"]
        c_M = mayor["colectivas"]

        # Contención literal: la regla más fuerte.
        if a_m and a_m < a_M:
            return "aristas_atomicas"

        # Contención visual/estructural después de colapsar vértices
        # colectivos. Requiere superconjunto ESTRICTO.
        if c_m and c_m < c_M:
            return "aristas_vertices_colectivos"

        return None

    # Buscamos la contenedora inmediata: la estructura más pequeña que
    # contiene completamente a la menor.
    for menor in datos:
        i = menor["indice"]
        candidatas = []

        for mayor in datos:
            j = mayor["indice"]
            if i == j:
                continue

            criterio = contiene(menor, mayor)
            if not criterio:
                continue

            tam = len(
                mayor["colectivas"]
                or mayor["atomicas"]
            )
            candidatas.append(
                (
                    tam,
                    str(mayor["figura"].get("tipo", "")),
                    j,
                    mayor,
                    criterio,
                )
            )

        if not candidatas:
            continue

        candidatas.sort(key=lambda x: (x[0], x[1], x[2]))
        _, _, j, mayor, criterio = candidatas[0]
        absorbidas.add(i)
        contenedor_de[i] = j
        criterio_de[i] = criterio

    # Si una contenedora también queda integrada, elevamos la subfigura hasta
    # la raíz que sí aparecerá en el informe.
    def raiz(j):
        vistos = set()
        while j in contenedor_de and j not in vistos:
            vistos.add(j)
            j = contenedor_de[j]
        return j

    for i in sorted(absorbidas):
        menor = geometricas[i]
        j = raiz(contenedor_de[i])
        mayor = geometricas[j]

        registro = {
            "tipo": menor.get("tipo", ""),
            "nombre_canonico": menor.get(
                "nombre_canonico",
                menor.get("tipo", ""),
            ),
            "puntos": list(
                menor.get("puntos", [])
                or puntos_reales_figura(menor)
            ),
            "puntos_geometricos": puntos_reales_figura(menor),
            "seleccion_original_huber_2026": menor.get(
                "seleccion_huber_2026"
            ),
            "fase_original_huber_2026": menor.get(
                "fase_seleccion_huber_2026"
            ),
            "aspectos": sorted(
                _claves_aspectos_figura_huber_2026(menor)
            ),
            "aspectos_colectivos": sorted(
                _claves_aspectos_colectivas_huber_2026(menor)
            ),
            "criterio_contencion": criterio_de.get(i),
            "motivo": (
                "geometria_completamente_contenida_en_"
                "figura_seleccionada_mayor"
            ),
        }

        mayor.setdefault(
            "subfiguras_integradas_huber_2026",
            [],
        ).append(registro)

        menor["seleccion_huber_2026"] = "subfigura_integrada"
        menor["fase_seleccion_huber_2026"] = "postseleccion_contencion"
        menor["motivo_seleccion_huber_2026"] = registro["motivo"]
        menor["contenida_en_huber_2026"] = mayor.get(
            "nombre_canonico",
            mayor.get("tipo", ""),
        )

    finales = [
        f
        for i, f in enumerate(geometricas)
        if i not in absorbidas
    ]
    finales.extend(complementarias)

    return (
        finales,
        [geometricas[i] for i in sorted(absorbidas)],
    )


def _vertices_colectivos_figura_huber_2026(figura):
    """
    Firma de vértices colectivos que llega realmente a la miniatura.

    Un stellium o conjunción cuenta como UN vértice, aunque internamente
    contenga varios puntos. Esto permite detectar familias de figuras que
    describen la misma zona estructural con una variación de un solo vértice.
    """
    mapa = _mapa_vertice_colectivo_huber_2026(figura)
    vertices = set()

    for punto in puntos_reales_figura(figura):
        vertices.add(
            mapa.get(
                punto,
                ("Punto", (punto,)),
            )
        )

    return vertices


def _resumen_miembro_familia_editorial_huber_2026(figura):
    return {
        "tipo": figura.get("tipo", ""),
        "nombre_canonico": figura.get(
            "nombre_canonico",
            figura.get("tipo", ""),
        ),
        "puntos": list(
            figura.get("puntos", [])
            or puntos_reales_figura(figura)
        ),
        "puntos_geometricos": list(
            puntos_reales_figura(figura)
        ),
        "seleccion_original_huber_2026": figura.get(
            "seleccion_huber_2026"
        ),
        "fase_original_huber_2026": figura.get(
            "fase_seleccion_huber_2026"
        ),
        "aspectos_nuevos_huber_2026": list(
            figura.get("aspectos_nuevos_huber_2026", [])
            or []
        ),
        "aspectos_reutilizados_huber_2026": list(
            figura.get("aspectos_reutilizados_huber_2026", [])
            or []
        ),
        "vertices_colectivos": [
            repr(v)
            for v in sorted(
                _vertices_colectivos_figura_huber_2026(figura),
                key=repr,
            )
        ],
        "aspectos": [
            {
                "p1": a.get("p1"),
                "p2": a.get("p2"),
                "nombre": a.get("nombre"),
                "simbolo": a.get("simbolo"),
                "orbe": a.get("orbe"),
            }
            for a in figura.get("aspectos", []) or []
        ],
    }


def _score_cabecera_familia_editorial_huber_2026(figura):
    """
    Prioridad exclusivamente EDITORIAL para escoger la cabecera de una
    familia estructural. No expresa importancia psicológica.

    Orden:
    1. principal antes que rescate;
    2. más líneas nuevas;
    3. más aristas geométricas;
    4. menos líneas reutilizadas;
    5. menor orbe medio.
    """
    rol = figura.get("seleccion_huber_2026")
    prioridad_rol = {
        "principal": 3,
        "rescate": 2,
        "complementaria": 1,
    }.get(rol, 0)

    nuevas = len(
        figura.get("aspectos_nuevos_huber_2026", [])
        or []
    )
    reutilizadas = len(
        figura.get("aspectos_reutilizados_huber_2026", [])
        or []
    )
    aristas = len(
        _claves_aspectos_colectivas_huber_2026(figura)
        or _claves_aspectos_figura_huber_2026(figura)
    )

    try:
        orbe = float(
            figura.get("orbe_medio")
            if figura.get("orbe_medio") is not None
            else _orbe_medio_geometria_figura(figura)
        )
    except (TypeError, ValueError):
        orbe = 999.0

    return (
        prioridad_rol,
        nuevas,
        aristas,
        -reutilizadas,
        -orbe,
        str(
            figura.get("nombre_canonico")
            or figura.get("tipo")
            or ""
        ),
    )


def agrupar_familias_editoriales_huber_2026(figuras):
    """
    Agrupa figuras seleccionadas que son variantes de una misma ZONA
    ESTRUCTURAL, sin alterar la detección geométrica.

    Esta capa es deliberadamente conservadora:
    - no toca Stellium;
    - solo agrupa figuras con al menos 4 vértices colectivos;
    - dos figuras entran en la misma familia si comparten al menos
      3 vértices colectivos y ese solapamiento representa al menos
      el 75 % de la figura más pequeña;
    - el agrupamiento es transitivo: A puede enlazar con B y B con C.

    La figura cabecera conserva su miniatura y su bloque interpretativo.
    Las demás quedan disponibles como variantes integradas dentro de la
    cabecera, pero no generan capítulos independientes.

    Así se evita que, por ejemplo, varias figuras de cuatro vértices que
    solo cambian un vértice cuenten cuatro veces la misma dinámica.
    """
    figuras = list(figuras or [])

    geometricas = [
        f for f in figuras
        if f.get("tipo") != "Stellium"
    ]
    complementarias = [
        f for f in figuras
        if f.get("tipo") == "Stellium"
    ]

    vertices = {
        id(f): _vertices_colectivos_figura_huber_2026(f)
        for f in geometricas
    }

    # Grafo de solapamiento estructural fuerte.
    vecinos = {
        id(f): set()
        for f in geometricas
    }

    for i in range(len(geometricas)):
        a = geometricas[i]
        va = vertices[id(a)]

        if len(va) < 4:
            continue

        for j in range(i + 1, len(geometricas)):
            b = geometricas[j]
            vb = vertices[id(b)]

            if len(vb) < 4:
                continue

            comunes = va & vb
            menor = min(len(va), len(vb))

            if menor <= 0:
                continue

            proporcion = len(comunes) / menor

            if len(comunes) >= 3 and proporcion >= 0.75:
                vecinos[id(a)].add(id(b))
                vecinos[id(b)].add(id(a))

    por_id = {
        id(f): f
        for f in geometricas
    }

    visitados = set()
    componentes = []

    for figura in geometricas:
        fid = id(figura)

        if fid in visitados:
            continue

        pendientes = [fid]
        componente = []

        while pendientes:
            actual = pendientes.pop()

            if actual in visitados:
                continue

            visitados.add(actual)
            componente.append(actual)
            pendientes.extend(
                vecinos.get(actual, set())
                - visitados
            )

        componentes.append(componente)

    integradas_ids = set()
    familias = []

    for numero, componente in enumerate(componentes, 1):
        if len(componente) < 2:
            continue

        miembros = [
            por_id[fid]
            for fid in componente
        ]

        cabecera = max(
            miembros,
            key=_score_cabecera_familia_editorial_huber_2026,
        )

        variantes = [
            f for f in miembros
            if f is not cabecera
        ]

        if not variantes:
            continue

        union_puntos = ordenar_puntos(
            list({
                punto
                for f in miembros
                for punto in (
                    f.get("puntos", [])
                    or puntos_reales_figura(f)
                )
            })
        )

        id_familia = (
            "familia-editorial-huber-2026-"
            + str(numero)
        )

        registros = [
            _resumen_miembro_familia_editorial_huber_2026(f)
            for f in variantes
        ]

        cabecera["familia_editorial_huber_2026"] = {
            "id": id_familia,
            "criterio": (
                "solapamiento_fuerte_de_vertices_colectivos_"
                "tres_de_cuatro_o_mas"
            ),
            "figura_cabecera": cabecera.get(
                "nombre_canonico",
                cabecera.get("tipo", ""),
            ),
            "puntos_editoriales_permitidos": union_puntos,
            "variantes_integradas": registros,
            "numero_variantes_integradas": len(registros),
            "regla_interpretacion": (
                "Interpretar una sola vez la dinámica compartida. "
                "Las variantes integradas solo deben aportar el matiz "
                "que introduce su vértice o relación diferencial; no "
                "deben reconstruirse como capítulos independientes."
            ),
        }

        cabecera["puntos_editoriales_familia_huber_2026"] = union_puntos
        cabecera["variantes_integradas_huber_2026"] = registros

        for variante in variantes:
            integradas_ids.add(id(variante))
            variante["seleccion_huber_2026"] = "familia_integrada"
            variante["fase_seleccion_huber_2026"] = (
                "postseleccion_familia_editorial"
            )
            variante["motivo_seleccion_huber_2026"] = (
                "solapamiento_estructural_fuerte_con_figura_cabecera"
            )
            variante["integrada_en_familia_huber_2026"] = {
                "id": id_familia,
                "figura_cabecera": cabecera.get(
                    "nombre_canonico",
                    cabecera.get("tipo", ""),
                ),
            }

        familias.append({
            "id": id_familia,
            "cabecera": cabecera.get(
                "nombre_canonico",
                cabecera.get("tipo", ""),
            ),
            "miembros": [
                f.get(
                    "nombre_canonico",
                    f.get("tipo", ""),
                )
                for f in miembros
            ],
            "puntos_editoriales_permitidos": union_puntos,
        })

    finales = [
        f for f in geometricas
        if id(f) not in integradas_ids
    ]
    finales.extend(complementarias)

    return (
        finales,
        [
            f for f in geometricas
            if id(f) in integradas_ids
        ],
        familias,
    )


# ─── HUBER 2026: LISTA MAESTRA DE PRIORIDAD ─────────────────────────────────
#
# REGLA EDITORIAL FIJA
# --------------------
# 1) GRANDES > MEDIANAS > PEQUEÑAS.
# 2) Dentro de cada tamaño: ROJO > VERDE > AZUL.
#
# La prioridad NO se recalcula para cada carta. Se calcula una sola vez a
# partir de la geometría canónica de cada uno de los 46 tipos Huber y queda
# convertida en una lista maestra estable.
#
# Tamaño canónico:
#   - grande: la geometría ideal envuelve el centro (arco > 180°);
#   - mediana: ocupa media carta / corta el centro (oposición, arco = 180°);
#   - pequeña: no toca el centro (arco < 180°).
#
# Color prioritario:
#   - se usa el color con mayor número de líneas en la geometría canónica;
#   - si hay empate se aplica la regla editorial acordada rojo > verde > azul.
#
# IMPORTANTE: esta tabla sirve SOLO para ordenar la búsqueda de figuras. No
# convierte el color en una jerarquía psicológica Huber.

DATOS_PRIORIDAD_FIGURAS_HUBER_2026 = {
    # 20 fundamentales
    "Cuadrado de rendimiento":      {"tamano":"grande",  "lineas":{"rojo":6,"verde":0,"azul":0}},
    "Triángulo de rendimiento":     {"tamano":"mediana", "lineas":{"rojo":3,"verde":0,"azul":0}},
    "Triángulo de talento grande":  {"tamano":"grande",  "lineas":{"rojo":0,"verde":0,"azul":3}},
    "Triángulo de talento pequeño": {"tamano":"pequena", "lineas":{"rojo":0,"verde":0,"azul":3}},
    "Triángulo de ambivalencia":    {"tamano":"mediana", "lineas":{"rojo":1,"verde":0,"azul":2}},
    "Figura de ambivalencia doble": {"tamano":"grande",  "lineas":{"rojo":3,"verde":1,"azul":2}},
    "Rectángulo de rectitud":       {"tamano":"grande",  "lineas":{"rojo":2,"verde":0,"azul":4}},
    "Cometa":                       {"tamano":"grande",  "lineas":{"rojo":1,"verde":0,"azul":5}},
    "Cuna":                         {"tamano":"mediana", "lineas":{"rojo":1,"verde":0,"azul":5}},
    "Triángulo de excitación":      {"tamano":"mediana", "lineas":{"rojo":1,"verde":2,"azul":0}},
    "Rectángulo de excitación":     {"tamano":"grande",  "lineas":{"rojo":2,"verde":4,"azul":0}},
    "Figura de búsqueda":           {"tamano":"pequena", "lineas":{"rojo":0,"verde":2,"azul":1}},
    "Figura de proyección":         {"tamano":"grande",  "lineas":{"rojo":0,"verde":2,"azul":1}},
    "Figura de información (ojo)":  {"tamano":"pequena", "lineas":{"rojo":0,"verde":2,"azul":1}},
    "Triángulo de aprendizaje pequeño":{"tamano":"pequena","lineas":{"rojo":1,"verde":1,"azul":1}},
    "Triángulo de aprendizaje mediano":{"tamano":"pequena","lineas":{"rojo":1,"verde":1,"azul":1}},
    "Triángulo de aprendizaje grande": {"tamano":"pequena","lineas":{"rojo":1,"verde":1,"azul":1}},
    "Triángulo dominante":          {"tamano":"grande",  "lineas":{"rojo":1,"verde":1,"azul":1}},
    "Trapecio":                     {"tamano":"grande",  "lineas":{"rojo":2,"verde":2,"azul":2}},
    "Figura de aspiración":         {"tamano":"grande",  "lineas":{"rojo":1,"verde":4,"azul":1}},

    # 26 variantes
    # Pandora: para prioridad se respeta el predominio verde explícito de la
    # fuente Huber (2 rojas, 4 verdes, 3 azules). El detector conserva la
    # geometría ampliada acordada en el proyecto y no se modifica aquí.
    "Caja de Pandora":              {"tamano":"grande",  "lineas":{"rojo":2,"verde":4,"azul":3}},
    "Bañera":                       {"tamano":"grande",  "lineas":{"rojo":1,"verde":3,"azul":2}},
    "Mariposa":                     {"tamano":"grande",  "lineas":{"rojo":0,"verde":2,"azul":2}},
    "Nasa":                         {"tamano":"grande",  "lineas":{"rojo":1,"verde":3,"azul":2}},
    "Trampolín":                    {"tamano":"mediana", "lineas":{"rojo":2,"verde":2,"azul":2}},
    "Corredor (saltador)":          {"tamano":"grande",  "lineas":{"rojo":2,"verde":0,"azul":2}},
    "Telescopio-Microscopio":       {"tamano":"grande",  "lineas":{"rojo":2,"verde":2,"azul":2}},
    "Amortiguador":                 {"tamano":"pequena", "lineas":{"rojo":2,"verde":0,"azul":2}},
    "Escudo":                       {"tamano":"pequena", "lineas":{"rojo":2,"verde":2,"azul":2}},
    "Diamante":                     {"tamano":"grande",  "lineas":{"rojo":2,"verde":4,"azul":3}},
    "Megáfono":                     {"tamano":"mediana", "lineas":{"rojo":1,"verde":3,"azul":2}},
    "Animat":                       {"tamano":"mediana", "lineas":{"rojo":3,"verde":1,"azul":2}},
    "Provocat":                     {"tamano":"mediana", "lineas":{"rojo":3,"verde":2,"azul":1}},
    "Arena":                        {"tamano":"grande",  "lineas":{"rojo":3,"verde":2,"azul":1}},
    "Canalizador":                  {"tamano":"grande",  "lineas":{"rojo":2,"verde":2,"azul":2}},
    "Deco":                         {"tamano":"mediana", "lineas":{"rojo":2,"verde":2,"azul":2}},
    "Bijou":                        {"tamano":"grande",  "lineas":{"rojo":1,"verde":3,"azul":2}},
    "Detect":                       {"tamano":"pequena", "lineas":{"rojo":1,"verde":2,"azul":3}},
    "Grabadora":                    {"tamano":"pequena", "lineas":{"rojo":1,"verde":2,"azul":3}},
    "Model":                        {"tamano":"grande",  "lineas":{"rojo":1,"verde":2,"azul":3}},
    "Represent":                    {"tamano":"grande",  "lineas":{"rojo":1,"verde":2,"azul":3}},
    "Escenario":                    {"tamano":"mediana", "lineas":{"rojo":1,"verde":4,"azul":1}},
    "Gorro mágico":                 {"tamano":"pequena", "lineas":{"rojo":1,"verde":3,"azul":2}},
    "Ovni":                         {"tamano":"pequena", "lineas":{"rojo":2,"verde":2,"azul":2}},
    "Surfista":                     {"tamano":"pequena", "lineas":{"rojo":1,"verde":3,"azul":2}},
    "Oscilo":                       {"tamano":"grande",  "lineas":{"rojo":1,"verde":3,"azul":2}},
}

# -----------------------------------------------------------------------------
# ORDEN EDITORIAL MAESTRO — EL ARTE DE ENCARNARTE
# -----------------------------------------------------------------------------
# Este orden NO pretende ser una jerarquía doctrinal Huber. Es la prioridad
# editorial definida para El Arte de Encarnarte por Izaskun:
#
#   1) primero las figuras con mayor "roce" o capacidad de crecimiento;
#   2) después las estructuras de aprendizaje/integración;
#   3) los talentos quedan al final, no porque sean menos importantes, sino
#      porque su facilidad puede convertirse en una zona conocida y agradable
#      en la que quedarse, evitando entrar en figuras de mayor fricción.
#
# El selector debe respetar ESTE ORDEN literalmente. No se recalcula por tamaño,
# color, número de vértices ni ningún otro criterio.
#
# Nota de nombres: en la conversación se usaron las formas abreviadas
# "Trapecio microscopio", "Bjou", "Corredor" y "Ojo". En código se
# conservan los nombres canónicos ya usados por los detectores.

ORDEN_PRIORIDAD_FIGURAS_HUBER_2026 = [
    "Diamante",
    "Caja de Pandora",
    "Cuadrado de rendimiento",
    "Figura de ambivalencia doble",
    "Arena",
    "Animat",
    "Provocat",
    "Triángulo de rendimiento",
    "Rectángulo de rectitud",
    "Rectángulo de excitación",
    "Canalizador",
    "Deco",
    "Trapecio",
    "Telescopio-Microscopio",
    "Cometa",
    "Cuna",
    "Megáfono",
    "Bijou",
    "Triángulo de ambivalencia",
    "Escenario",
    "Figura de aspiración",
    "Triángulo de excitación",
    "Nasa",
    "Represent",
    "Oscilo",
    "Model",
    "Triángulo dominante",
    "Bañera",
    "Ovni",
    "Surfista",
    "Grabadora",
    "Triángulo de aprendizaje grande",
    "Escudo",
    "Corredor (saltador)",
    "Amortiguador",
    "Trampolín",
    "Detect",
    "Triángulo de aprendizaje mediano",
    "Gorro mágico",
    "Triángulo de aprendizaje pequeño",
    "Mariposa",
    "Figura de proyección",
    "Figura de búsqueda",
    "Figura de información (ojo)",
    "Triángulo de talento grande",
    "Triángulo de talento pequeño",
]

INDICE_PRIORIDAD_FIGURAS_HUBER_2026 = {
    nombre: indice
    for indice, nombre in enumerate(ORDEN_PRIORIDAD_FIGURAS_HUBER_2026)
}

# Se conserva la clasificación geométrica de V15 únicamente como metadato y
# para decidir cuál es la figura más pequeña durante el rescate final. NO
# interviene en el orden de la pasada principal.
CLASIFICACION_PRIORIDAD_FIGURAS_HUBER_2026 = {
    nombre: {
        "tamano": datos["tamano"],
        "color_prioritario": max(
            ("rojo", "verde", "azul"),
            key=lambda c: (datos["lineas"].get(c, 0), {"rojo": 2, "verde": 1, "azul": 0}[c]),
        ),
        "lineas_color": dict(datos["lineas"]),
    }
    for nombre, datos in DATOS_PRIORIDAD_FIGURAS_HUBER_2026.items()
}


def _validar_orden_prioridad_huber_2026():
    """Comprueba que el orden editorial contiene exactamente las 46 figuras."""
    esperadas = set(CATALOGO_HUBER_20) | set(CATALOGO_HUBER_VARIANTES_26)
    recibidas = set(ORDEN_PRIORIDAD_FIGURAS_HUBER_2026)

    if len(ORDEN_PRIORIDAD_FIGURAS_HUBER_2026) != len(recibidas):
        raise RuntimeError("ORDEN_PRIORIDAD_FIGURAS_HUBER_2026 contiene duplicados.")

    if esperadas != recibidas or len(recibidas) != 46:
        raise RuntimeError(
            "El orden editorial Huber 2026 debe contener exactamente las 46 figuras. "
            f"faltan={sorted(esperadas-recibidas)}; "
            f"sobran={sorted(recibidas-esperadas)}; total={len(recibidas)}"
        )


_validar_orden_prioridad_huber_2026()


def _nombre_prioridad_huber_2026(figura):
    """Devuelve el nombre canónico usado por la lista maestra."""
    nombre = figura.get("nombre_canonico") or figura.get("tipo") or ""
    alias = {
        "T-cuadrada": "Triángulo de rendimiento",
        "Gran trígono": "Triángulo de talento grande",
        "Yod": "Figura de proyección",
        "Ojo pequeño": "Figura de información (ojo)",
        "Triángulo de aprendizaje": "Triángulo dominante",
    }
    return alias.get(nombre, nombre)


def _prioridad_lista_huber_2026(figura):
    """
    Orden de la PASADA PRINCIPAL.

    1. Tipo de figura según el orden editorial fijo decidido por Izaskun.
    2. Si hay varias apariciones del MISMO tipo: menor orbe medio.
    3. Puntos geométricos solo como desempate estable.
    """
    nombre = _nombre_prioridad_huber_2026(figura)
    indice = INDICE_PRIORIDAD_FIGURAS_HUBER_2026.get(nombre, 10_000)
    orbe = _orbe_medio_seleccion_huber_2026(figura)
    puntos = tuple(sorted(puntos_reales_figura(figura)))
    return (indice, orbe, puntos)


def _clave_figura_mas_pequena_para_rescate_huber_2026(figura):
    """
    Orden exclusivo de la PASADA FINAL de rescate.

    Para un aspecto que quedó libre se elige la figura válida MÁS PEQUEÑA
    que pueda contenerlo, permitiendo usar líneas ya reservadas como soporte.

    Pequeñez se decide así:
      1) pequeña < mediana < grande;
      2) menos líneas geométricas;
      3) menos vértices geométricos;
      4) posición en la lista maestra;
      5) menor orbe medio.
    """
    nombre = _nombre_prioridad_huber_2026(figura)
    datos = CLASIFICACION_PRIORIDAD_FIGURAS_HUBER_2026.get(
        nombre,
        {"tamano": "grande", "color_prioritario": "azul"},
    )
    rango_tamano_rescate = {
        "pequena": 0,
        "mediana": 1,
        "grande": 2,
    }
    return (
        rango_tamano_rescate.get(datos.get("tamano"), 9),
        len(_claves_aspectos_figura_huber_2026(figura)),
        len(puntos_reales_figura(figura)),
        INDICE_PRIORIDAD_FIGURAS_HUBER_2026.get(nombre, 10_000),
        _orbe_medio_seleccion_huber_2026(figura),
        tuple(sorted(puntos_reales_figura(figura))),
    )


HUBER_2026_DIAGNOSTICO_RESCATE_ACTIVO = True
HUBER_2026_RESCATE_SIN_REDUNDANCIAS_V18 = True
HUBER_2026_CONTENCION_REAL_V19 = True
HUBER_2026_CONTENCION_VARIABLES_SEGURAS_V20 = True
HUBER_2026_LINEAS_COLECTIVAS_V21 = True

def _texto_aspecto_diag_huber_2026(clave):
    if not clave:
        return "?"
    try:
        p1, p2, simbolo = clave
        return f"{p1} {simbolo} {p2}".strip()
    except Exception:
        return str(clave)

def _resumen_opcion_rescate_diag_huber_2026(figura, huerfanas, ocupadas):
    claves = _claves_aspectos_figura_huber_2026(figura)
    nombre = _nombre_prioridad_huber_2026(figura)
    clas = CLASIFICACION_PRIORIDAD_FIGURAS_HUBER_2026.get(nombre, {})
    return {
        "nombre": nombre,
        "puntos": list(puntos_reales_figura(figura)),
        "tamano": clas.get("tamano"),
        "numero_lineas": len(claves),
        "numero_vertices": len(puntos_reales_figura(figura)),
        "nuevas": sorted(claves & huerfanas),
        "reutilizadas": sorted(claves & ocupadas),
        "clave_minimo": list(_clave_figura_mas_pequena_para_rescate_huber_2026(figura)),
    }

def _imprimir_traza_rescate_huber_2026(traza):
    if not HUBER_2026_DIAGNOSTICO_RESCATE_ACTIVO:
        return
    print("\n" + "=" * 86)
    print("DIAGNÓSTICO DETALLADO DEL RESCATE HUBER 2026")
    print("La selección principal NO se modifica. Esta salida solo explica la pasada B.")
    print("=" * 86)
    for i, paso in enumerate(traza, 1):
        print(f"\nPASO {i:02d} · ASPECTO LIBRE: {_texto_aspecto_diag_huber_2026(paso['aspecto_objetivo'])}")
        opciones = paso.get("opciones", [])
        if not opciones:
            print("  Sin figura válida en stand by que lo contenga.")
            continue
        for j, op in enumerate(opciones, 1):
            marca = "  <-- ELEGIDA" if j == paso.get("indice_elegida") else ""
            puntos = ", ".join(op.get("puntos", []))
            print(
                f"  {j:02d}. {op['nombre']} | {puntos} | "
                f"tamaño={op.get('tamano')} | líneas={op['numero_lineas']} | "
                f"vértices={op['numero_vertices']} | "
                f"nuevas={len(op['nuevas'])} | reutilizadas={len(op['reutilizadas'])}{marca}"
            )
        e = paso.get("elegida")
        if e:
            print("  Resultado: " + e["nombre"] + " · nuevas: " + ", ".join(_texto_aspecto_diag_huber_2026(x) for x in e["nuevas"]))
    print("\n" + "=" * 86)
    print("FIN DIAGNÓSTICO DE RESCATES")
    print("=" * 86 + "\n")


def _depurar_rescates_redundantes_huber_2026(
    principales,
    rescates,
    integrables,
):
    """
    Elimina únicamente rescates que, al terminar toda la pasada B,
    ya no son necesarios para representar ningún aspecto integrable.

    Importante:
    - NO toca figuras principales.
    - NO cambia detectores ni geometría.
    - NO aplica un filtro editorial por parecido.
    - Solo elimina un rescate si TODAS sus líneas están ya cubiertas
      por principales y/u otros rescates que permanecen.
    - Se revisan en orden inverso para conservar, siempre que sea posible,
      las decisiones de rescate tomadas antes.
    """
    principales = list(principales or [])
    rescates_activos = list(rescates or [])
    eliminados = []

    cobertura_principal = set()
    for figura in principales:
        cobertura_principal |= _claves_seleccion_huber_2026(figura)

    for figura in list(reversed(rescates_activos)):
        cobertura_otros = set(cobertura_principal)

        for otra in rescates_activos:
            if otra is figura:
                continue
            cobertura_otros |= _claves_seleccion_huber_2026(otra)

        claves_figura = _claves_seleccion_huber_2026(figura)
        aportacion_exclusiva = (
            (claves_figura & set(integrables))
            - cobertura_otros
        )

        if aportacion_exclusiva:
            continue

        rescates_activos = [
            otra
            for otra in rescates_activos
            if otra is not figura
        ]

        _marcar_estado_huber_2026(
            figura,
            "absorbida",
            "depuracion_final_rescates",
            reutilizadas=(claves_figura & cobertura_otros),
            motivo="rescate_redundante_tras_cobertura_posterior",
        )
        figura["estado_estructural"] = "absorbida"
        figura["jerarquia"] = "absorbida"
        figura["puntuacion_jerarquia"] = 0
        eliminados.append(figura)

    eliminados.reverse()
    return rescates_activos, eliminados



def _eliminar_contenidas_entre_seleccionadas_huber_2026(
    seleccionadas,
):
    """
    Elimina subfiguras realmente contenidas dentro de una figura mayor
    YA seleccionada.

    Criterio estricto:
    - la figura menor debe estar permitida como subfigura del tipo mayor
      según CONTENCIONES_HUBER;
    - todos sus puntos geométricos deben estar incluidos en la mayor;
    - todos sus aspectos geométricos deben estar incluidos en la mayor;
    - la mayor debe tener más aspectos que la menor.

    Esto evita eliminar figuras solo por compartir puntos o por parecido.
    """
    seleccionadas = list(seleccionadas or [])
    absorbidas = set()
    relaciones = []

    for i, menor in enumerate(seleccionadas):
        if menor.get("tipo") == "Stellium":
            continue

        tipo_menor = menor.get("tipo", "")
        vertices_menor = _vertices_colectivos_figura_huber_2026(menor)
        aspectos_menor = _claves_seleccion_huber_2026(menor)

        if not vertices_menor or not aspectos_menor:
            continue

        candidatas = []

        for j, mayor in enumerate(seleccionadas):
            if i == j:
                continue

            tipo_mayor = mayor.get("tipo", "")
            permitidas = CONTENCIONES_HUBER.get(tipo_mayor, set())

            if tipo_menor not in permitidas:
                continue

            vertices_mayor = _vertices_colectivos_figura_huber_2026(mayor)
            aspectos_mayor = _claves_seleccion_huber_2026(mayor)

            if len(aspectos_mayor) <= len(aspectos_menor):
                continue

            if not vertices_menor.issubset(vertices_mayor):
                continue

            if not aspectos_menor.issubset(aspectos_mayor):
                continue

            candidatas.append(
                (
                    len(aspectos_mayor),
                    len(vertices_mayor),
                    j,
                    mayor,
                )
            )

        if not candidatas:
            continue

        _, _, j_mayor, mayor = min(candidatas)
        absorbidas.add(i)

        mayor.setdefault(
            "subfiguras_absorbidas_seleccion_huber_2026",
            [],
        ).append({
            "tipo": menor.get("tipo", ""),
            "nombre_canonico": menor.get(
                "nombre_canonico",
                menor.get("tipo", ""),
            ),
            "puntos_geometricos": list(puntos_reales_figura(menor)),
            "aspectos": [
                list(clave)
                for clave in sorted(aspectos_menor)
            ],
        })

        _marcar_estado_huber_2026(
            menor,
            "absorbida",
            "contencion_entre_seleccionadas",
            reutilizadas=aspectos_menor,
            motivo=f"contenida_en_{mayor.get('tipo','figura_mayor')}",
        )
        menor["estado_estructural"] = "absorbida"
        menor["jerarquia"] = "absorbida"
        menor["puntuacion_jerarquia"] = 0

        relaciones.append({
            "menor": menor,
            "mayor": mayor,
        })

    salida = [
        figura
        for i, figura in enumerate(seleccionadas)
        if i not in absorbidas
    ]

    return salida, relaciones


def seleccionar_arquitectura_huber_2026(figuras, aspectos_geometricos):
    # V20: valores seguros para todas las ramas del selector.
    # Se rellenan con datos reales cuando se ejecutan las fases correspondientes.
    rescates_redundantes = []
    contenciones_aplicadas = []
    figuras_contenidas_eliminadas = []

    """
    Selección Huber 2026 por ORDEN EDITORIAL MAESTRO + STAND BY + RESCATE MÍNIMO.

    PASADA A — recorrido literal del orden editorial de 46 figuras
    ------------------------------------------------
    1. El motor ya ha detectado TODAS las figuras posibles de la carta.
    2. Se recorren los tipos exactamente en el orden editorial fijado por Izaskun.
       No se recalcula prioridad por tamaño, color, vértices ni ningún otro criterio.
    3. Si un tipo aparece varias veces con planetas distintos, se procesan TODAS
       sus apariciones antes de pasar al tipo siguiente.
    4. Una aparición entra si TODAS sus líneas están libres.
    5. Sus líneas quedan reservadas (stand by).
    6. Si necesita una línea ya reservada, esa aparición queda en espera.

    PASADA B — aspecto libre → figura más pequeña posible
    ------------------------------------------------------
    7. Al finalizar se buscan aspectos integrables todavía libres.
    8. Se toma cada aspecto libre y, entre las figuras en espera que lo contienen,
       se elige la figura MÁS PEQUEÑA posible.
    9. Esa figura puede reutilizar líneas reservadas únicamente como soporte para
       incorporar el aspecto libre.
    10. Al seleccionarla puede cubrir además otros aspectos libres de esa figura.
    11. Una figura que no aporta ningún aspecto libre nunca reaparece.

    Stellium sigue siendo una estructura complementaria y no compite por líneas.
    """
    global ULTIMO_DIAGNOSTICO_HUBER_2026

    candidatas = list(figuras or [])

    for figura in candidatas:
        figura.setdefault(
            "estado_composicion_huber",
            figura.get("estado_estructural", "independiente"),
        )

    stelliums = [f for f in candidatas if f.get("tipo") == "Stellium"]
    geometricas = [f for f in candidatas if f.get("tipo") != "Stellium"]

    for figura in geometricas:
        for clave in (
            "seleccion_huber_2026",
            "fase_seleccion_huber_2026",
            "motivo_seleccion_huber_2026",
            "aspectos_nuevos_huber_2026",
            "aspectos_reutilizados_huber_2026",
            "familia_editorial_huber_2026",
            "puntos_editoriales_familia_huber_2026",
            "variantes_integradas_huber_2026",
            "integrada_en_familia_huber_2026",
        ):
            figura.pop(clave, None)

    # Importante: esto agrupa también todas las apariciones del mismo tipo.
    geometricas.sort(key=_prioridad_lista_huber_2026)

    principales = []
    en_espera = []
    ocupadas = set()
    cubiertas = set()

    # ── PASADA A: LISTA → RESERVA → STAND BY ────────────────────────────
    for figura in geometricas:
        claves = _claves_seleccion_huber_2026(figura)

        if not claves:
            _marcar_estado_huber_2026(
                figura,
                "no_seleccionada",
                "pasada_a_lista_tamano_color",
                motivo="sin_lineas_geometricas",
            )
            continue

        solapadas = claves & ocupadas

        if solapadas:
            _marcar_estado_huber_2026(
                figura,
                "stand_by",
                "pasada_a_lista_tamano_color",
                reutilizadas=solapadas,
                motivo="espera_por_aspectos_ya_reservados",
            )
            en_espera.append(figura)
            continue

        _marcar_estado_huber_2026(
            figura,
            "principal",
            "pasada_a_lista_tamano_color",
            nuevas=claves,
            motivo="figura_encontrada_en_su_turno_con_todas_las_lineas_libres",
        )
        figura["estado_estructural"] = "principal"
        figura["jerarquia"] = "seleccionada"
        figura["puntuacion_jerarquia"] = 0

        principales.append(figura)
        ocupadas |= claves
        cubiertas |= claves

    # Un aspecto solo es rescatable si participa en al menos una geometría válida.
    claves_en_alguna_figura = set()
    for figura in geometricas:
        claves_en_alguna_figura |= _claves_seleccion_huber_2026(figura)

    # Todas estas claves proceden de aspectos natales ya validados por los
    # detectores. Para selección usamos su IDENTIDAD ESTRUCTURAL colectiva;
    # cruzarlas de nuevo con claves atómicas natales rompería la equivalencia
    # entre miembros de un mismo Stellium/Conjunción.
    integrables = set(claves_en_alguna_figura)
    huerfanas = set(integrables - cubiertas)
    huerfanas_iniciales = set(huerfanas)

    # ── PASADA B: CADA ASPECTO LIBRE BUSCA LA FIGURA MÁS PEQUEÑA ───────
    rescates = []
    pendientes = list(en_espera)
    imposibles_de_rescatar = set()
    traza_rescate = []

    while huerfanas:
        disponibles = sorted(huerfanas - imposibles_de_rescatar)
        if not disponibles:
            break

        aspecto_objetivo = disponibles[0]

        candidatas_rescate = [
            figura
            for figura in pendientes
            if aspecto_objetivo in _claves_seleccion_huber_2026(figura)
        ]

        if not candidatas_rescate:
            traza_rescate.append({
                "aspecto_objetivo": aspecto_objetivo,
                "opciones": [],
                "indice_elegida": None,
                "elegida": None,
            })
            imposibles_de_rescatar.add(aspecto_objetivo)
            continue

        candidatas_ordenadas = sorted(
            candidatas_rescate,
            key=_clave_figura_mas_pequena_para_rescate_huber_2026,
        )
        elegida = candidatas_ordenadas[0]
        opciones_diag = [
            _resumen_opcion_rescate_diag_huber_2026(f, huerfanas, ocupadas)
            for f in candidatas_ordenadas
        ]

        claves_elegida = _claves_seleccion_huber_2026(elegida)
        nuevas = claves_elegida & huerfanas
        reutilizadas = claves_elegida & ocupadas

        traza_rescate.append({
            "aspecto_objetivo": aspecto_objetivo,
            "opciones": opciones_diag,
            "indice_elegida": 1,
            "elegida": {
                "nombre": _nombre_prioridad_huber_2026(elegida),
                "puntos": list(puntos_reales_figura(elegida)),
                "nuevas": sorted(nuevas),
                "reutilizadas": sorted(reutilizadas),
            },
        })

        if not nuevas:
            pendientes = [f for f in pendientes if f is not elegida]
            continue

        _marcar_estado_huber_2026(
            elegida,
            "rescate",
            "pasada_b_figura_minima_para_aspecto_libre",
            nuevas=nuevas,
            reutilizadas=reutilizadas,
            motivo="figura_mas_pequena_posible_que_incorpora_aspecto_libre",
        )
        elegida["estado_estructural"] = "rescate"
        elegida["jerarquia"] = "seleccionada"
        elegida["puntuacion_jerarquia"] = 0
        rescates.append(elegida)

        ocupadas |= claves_elegida
        cubiertas |= claves_elegida
        huerfanas -= nuevas
        pendientes = [f for f in pendientes if f is not elegida]

    # ── PASADA B2: ELIMINAR RESCATES QUE HAN QUEDADO REDUNDANTES ────────
    #
    # Un rescate podía ser necesario cuando entró y dejar de serlo después
    # porque rescates posteriores reutilizaran sus líneas mientras añadían
    # otras nuevas. Si al final TODAS sus líneas ya están representadas por
    # otras figuras seleccionadas, no aporta ninguna pieza propia y se retira.
    #
    # Esto forma parte de la propia selección geométrica; no es un filtro
    # editorial posterior por parecido.
    rescates, rescates_redundantes = (
        _depurar_rescates_redundantes_huber_2026(
            principales=principales,
            rescates=rescates,
            integrables=integrables,
        )
    )

    # Recalcular cobertura real después de retirar rescates redundantes.
    ocupadas = set()
    cubiertas = set()

    for figura in principales + rescates:
        claves_figura = _claves_seleccion_huber_2026(figura)
        ocupadas |= claves_figura
        cubiertas |= claves_figura

    huerfanas = set(integrables - cubiertas)

    # ── PASADA C: CONTENCIÓN REAL ENTRE FIGURAS YA SELECCIONADAS ───────
    #
    # Aquí no eliminamos por semejanza ni por compartir vértices.
    # Solo retiramos una figura menor si su geometría completa
    # (puntos + aspectos) está contenida en una figura mayor compatible
    # según CONTENCIONES_HUBER.
    seleccionadas_sin_stellium = principales + rescates

    (
        seleccionadas_sin_contenidas,
        contenciones_aplicadas,
    ) = _eliminar_contenidas_entre_seleccionadas_huber_2026(
        seleccionadas_sin_stellium
    )

    figuras_contenidas_eliminadas = [
        item["menor"]
        for item in contenciones_aplicadas
    ]

    ids_principales = {id(f) for f in principales}
    principales = [
        f for f in seleccionadas_sin_contenidas
        if id(f) in ids_principales
    ]
    rescates = [
        f for f in seleccionadas_sin_contenidas
        if id(f) not in ids_principales
    ]

    # Recalcular otra vez la cobertura tras la contención.
    ocupadas = set()
    cubiertas = set()

    for figura in principales + rescates:
        claves_figura = _claves_seleccion_huber_2026(figura)
        ocupadas |= claves_figura
        cubiertas |= claves_figura

    huerfanas = set(integrables - cubiertas)

    # Las restantes son repetición: no aportan ninguna línea que siga libre.
    for figura in pendientes:
        claves = _claves_seleccion_huber_2026(figura)
        _marcar_estado_huber_2026(
            figura,
            "absorbida",
            "final_lista_tamano_color",
            reutilizadas=(claves & ocupadas),
            motivo="no_necesaria_para_cubrir_aspectos_libres",
        )

    for stellium in stelliums:
        _marcar_estado_huber_2026(
            stellium,
            "complementaria",
            "stellium",
            motivo="estructura_colectiva_no_compite_por_lineas",
        )
        stellium["estado_estructural"] = "complementaria"
        stellium["jerarquia"] = "complementaria"
        stellium["puntuacion_jerarquia"] = 0

    seleccionadas = principales + rescates + stelliums

    resumen = {
        "version": "huber-2026-orden-editorial-izaskun-lineas-colectivas-v21",
        "algoritmo_principal": "orden_editorial_46_roce_crecimiento_antes_talentos",
        "algoritmo_rescate": "lineas_colectivas_unicas_reserva_rescate_depura_redundancias_y_contencion_real",
        "numero_candidatas": len(candidatas),
        "numero_principales": len(principales),
        "numero_rescates": len(rescates),
        "numero_rescates_redundantes_eliminados": len(rescates_redundantes),
        "numero_figuras_contenidas_eliminadas": len(figuras_contenidas_eliminadas),
        "figuras_contenidas_eliminadas": [
            {
                "tipo": f.get("tipo"),
                "nombre_canonico": f.get("nombre_canonico", f.get("tipo")),
                "puntos_geometricos": list(puntos_reales_figura(f)),
                "motivo": f.get("motivo_seleccion_huber_2026"),
            }
            for f in figuras_contenidas_eliminadas
        ],
        "rescates_redundantes_eliminados": [
            {
                "tipo": f.get("tipo"),
                "nombre_canonico": f.get("nombre_canonico", f.get("tipo")),
                "puntos_geometricos": list(puntos_reales_figura(f)),
                "motivo": f.get("motivo_seleccion_huber_2026"),
            }
            for f in rescates_redundantes
        ],
        "numero_stelliums": len(stelliums),
        "numero_en_stand_by_inicial": len(en_espera),
        "numero_absorbidas": len(candidatas) - len(seleccionadas),
        "aspectos_ocupados": sorted(ocupadas),
        "aspectos_integrables": sorted(integrables),
        "aspectos_huerfanos_iniciales": sorted(huerfanas_iniciales),
        "aspectos_integrables_no_cubiertos": sorted(huerfanas),
        "aspectos_sin_rescate_posible": sorted(imposibles_de_rescatar),
        "orden_prioridad_figuras": list(ORDEN_PRIORIDAD_FIGURAS_HUBER_2026),
        "clasificacion_prioridad_figuras": dict(CLASIFICACION_PRIORIDAD_FIGURAS_HUBER_2026),
        "numero_subfiguras_integradas": 0,
        "numero_figuras_integradas_en_familias": 0,
        "numero_familias_editoriales": 0,
        "familias_editoriales": [],
    }

    for figura in seleccionadas:
        figura["resumen_seleccion_huber_2026"] = dict(resumen)

    candidatos_diag = []
    for figura in geometricas + stelliums:
        nombre_prioridad = (
            _nombre_prioridad_huber_2026(figura)
            if figura.get("tipo") != "Stellium"
            else "Stellium"
        )
        clasificacion = CLASIFICACION_PRIORIDAD_FIGURAS_HUBER_2026.get(
            nombre_prioridad,
            {},
        )
        candidatos_diag.append({
            "tipo": figura.get("tipo"),
            "nombre_canonico": figura.get("nombre_canonico", figura.get("tipo")),
            "nombre_prioridad": nombre_prioridad,
            "posicion_prioridad": (
                INDICE_PRIORIDAD_FIGURAS_HUBER_2026.get(nombre_prioridad)
                if figura.get("tipo") != "Stellium"
                else None
            ),
            "tamano_prioridad": clasificacion.get("tamano"),
            "color_prioritario": clasificacion.get("color_prioritario"),
            "puntos_geometricos": puntos_reales_figura(figura),
            "puntos": list(figura.get("puntos", []) or []),
            "seleccion_huber_2026": figura.get("seleccion_huber_2026"),
            "fase_seleccion_huber_2026": figura.get("fase_seleccion_huber_2026"),
            "motivo": figura.get("motivo_seleccion_huber_2026"),
            "aspectos_nuevos": figura.get("aspectos_nuevos_huber_2026", []),
            "aspectos_reutilizados": figura.get("aspectos_reutilizados_huber_2026", []),
        })

    ULTIMO_DIAGNOSTICO_HUBER_2026 = {
        "resumen": resumen,
        "candidatas": candidatos_diag,
        "traza_rescate": traza_rescate,
    }

    _imprimir_traza_rescate_huber_2026(traza_rescate)
    return seleccionadas

# ─── FIN HUBER 2026 ─────────────────────────────────────────────────────────



def detectar_figuras(carta, aspectos):
    """
    Entrada pública única del motor de figuras.

    1. Filtra únicamente para GEOMETRÍA:
       - MC fuera;
       - ASC, Quirón, Lilith, NN y NS dentro;
       - oposición automática NN-NS fuera.
    2. Detecta y normaliza todas las candidatas.
    3. Aplica una sola selección final secuencial:
       prioridad → reserva (stand by) → rescate de aspectos sueltos.
    4. No vuelve a pasar por la antigua jerarquía editorial.
    """
    aspectos_geo = filtrar_aspectos_geometria_huber_2026(aspectos)
    return detectar_figuras_estructurales(
        carta,
        aspectos_geo,
    )



# ─── TEXTOS DE FIGURAS ───────────────────────────────────────────────────────

def texto_intro_figuras(figuras):
    if not figuras:
        return (
            "En esta carta no aparecen figuras geométricas mayores dentro de los orbes definidos. "
            "Esto no significa que no haya tensión, recursos o estructura interna, sino que la carta funciona más por aspectos aislados, posiciones y acumulaciones parciales que por grandes configuraciones cerradas."
        )

    return (
        "Las figuras muestran cómo varios puntos de la carta se conectan entre sí formando patrones mayores. "
        "No describen rasgos sueltos, sino modos completos de circulación interna: dónde se acumula tensión, dónde hay apoyo, qué zonas buscan salida y qué partes de la carta tienden a activarse juntas."
    )


# ─── TEXTOS BASE POR TIPO DE FIGURA ──────────────────────────────────────────

TEXTO_TIPO_FIGURA = {

"T-cuadrada": (
    "La T-cuadrada concentra tensión, presión y necesidad de respuesta. "
    "No deja que la energía permanezca quieta: algo dentro de ti busca resolver, compensar o encontrar salida.\n\n"
    "La oposición marca una polaridad interna. El ápice muestra el punto donde esa tensión se descarga con más fuerza. "
    "Cuando esta figura funciona de forma automática, puedes sentir exigencia, bloqueo, reacción o sensación de tener que sostener demasiado. "
    "Cuando se vuelve más consciente, puede darte una enorme capacidad de acción, maduración y claridad."
),

"Gran trígono": (
    "El gran trígono crea un circuito de apoyo interno. "
    "La energía circula con más facilidad entre los puntos implicados, como si esas partes de ti se reconocieran entre sí y pudieran sostenerse con menos fricción.\n\n"
    "No es solo talento ni facilidad. También puede convertirse en un circuito cerrado: una forma conocida de responder que te estabiliza, pero que a veces evita el movimiento necesario. "
    "Su valor aparece cuando usas ese apoyo como base, no como refugio permanente."
),

"Cometa": (
    "El cometa combina sostén y dirección. "
    "Tiene la base fluida del gran trígono, pero también una oposición que introduce tensión, impulso y necesidad de salida.\n\n"
    "Esta figura no permite que el apoyo interno se quede encerrado en sí mismo. "
    "Algo necesita orientarse, tomar forma o expresarse hacia fuera. "
    "Puede ser una configuración muy fértil cuando no se usa para compensar presión, sino para dirigir energía con más consciencia."
),

"Stellium": (
    "El stellium muestra una concentración de energía en una zona concreta de la carta. "
    "No se activa una sola parte de ti: se activa un conjunto entero.\n\n"
    "Por eso esa casa o territorio vital puede sentirse muy cargado, central o difícil de vivir con neutralidad. "
    "Ahí hay intensidad, recursos, presión y también una demanda mayor de presencia."
),

"Yod": (
    "El Yod señala una configuración de ajuste fino y dirección incómoda. "
    "No funciona como tensión frontal, sino como una presión interna que obliga a recolocar la respuesta.\n\n"
    "La base ofrece una posibilidad de apoyo, pero el ápice recibe una exigencia de adaptación que puede sentirse difícil de nombrar. "
    "Suele pedir precisión, escucha y maduración progresiva."
),

"Triángulo de aprendizaje": (
    "El triángulo de aprendizaje describe una dinámica de ajuste progresivo. "
    "No funciona como facilidad pura ni como conflicto frontal. "
    "Tiene algo que empuja, algo que sostiene y algo que obliga a recolocar la respuesta.\n\n"
    "Suele madurar con la experiencia. No se resuelve de una vez, sino a través de repetición, prueba, error y refinamiento."
),

"Triángulo de aprendizaje pequeño": (
    "El triángulo de aprendizaje pequeño describe una dinámica de ajuste gradual. "
    "La cuadratura introduce una tensión concreta, el sextil ofrece una vía de apoyo "
    "y el semisextil señala un enlace sutil que necesita atención para poder integrarse.\n\n"
    "Su funcionamiento suele hacerse visible en los pequeños reajustes de la experiencia. "
    "No actúa con la intensidad de una gran configuración, pero puede mostrar un mecanismo "
    "repetido de aprendizaje, prueba y afinación."
),

"Triángulo de aprendizaje mediano": (
    "El triángulo de aprendizaje mediano combina una tensión concreta con una vía amplia de apoyo "
    "y un enlace sutil que introduce información nueva. La cuadratura activa el movimiento, el trígono "
    "ofrece una capacidad disponible y el semisextil impulsa pequeños reajustes de percepción.\n\n"
    "La integración suele producirse cuando la facilidad del trígono no evita la tensión, sino que se "
    "utiliza conscientemente para elaborar lo que la cuadratura pone en movimiento."
),

"Ojo pequeño": (
    "El Ojo pequeño es una figura de percepción e información formada por dos semisextiles y un sextil. "
    "Conecta tres puntos mediante enlaces sutiles y una vía de cooperación más visible.\n\n"
    "Su funcionamiento puede expresarse como atención fina, curiosidad y capacidad para captar matices. "
    "La información circula en pequeños pasos hasta encontrar un cauce que permite relacionarla y darle forma."
),

}


# ─── MATICES SEGÚN PUNTOS IMPLICADOS ────────────────────────────────────────

TEXTO_PUNTO_FIGURA = {

    "Sol": (
        "La identidad, la dirección vital y la necesidad de construir una vida coherente "
        "quedan directamente implicadas en esta figura. "
        "Las decisiones importantes rara vez se viven de forma superficial."
    ),

    "Luna": (
        "El mundo emocional participa directamente en esta configuración. "
        "Las necesidades de seguridad, descanso y regulación pueden activarse con mucha intensidad."
    ),

    "Mercurio": (
        "La mente y la forma de comprender la experiencia quedan muy implicadas. "
        "Pensar, interpretar o intentar entender lo que ocurre puede convertirse en parte central del proceso."
    ),

    "Venus": (
        "Los vínculos, el bienestar y la capacidad de sentir equilibrio relacional forman parte importante de esta figura. "
        "Las relaciones suelen convertirse en espacios de aprendizaje profundo."
    ),

    "Marte": (
        "La acción, la reacción y la forma de defender espacio propio quedan muy activadas. "
        "Puede haber dificultad para dosificar la energía o encontrar un ritmo estable de acción."
    ),

    "Júpiter": (
        "La necesidad de expansión, crecimiento y sentido participa directamente en esta configuración. "
        "Puede costar permanecer mucho tiempo en experiencias que se sienten limitantes o demasiado pequeñas."
    ),

    "Saturno": (
        "La exigencia, la responsabilidad y la necesidad de estructura tienen mucho peso dentro de esta figura. "
        "Parte del aprendizaje pasa por construir sostén sin endurecerte constantemente."
    ),

    "Urano": (
        "Los cambios, la necesidad de libertad y la ruptura de patrones conocidos participan activamente aquí. "
        "Puede haber poca tolerancia a dinámicas rígidas o excesivamente cerradas."
    ),

    "Neptuno": (
        "La sensibilidad, la permeabilidad emocional y la dificultad para sostener límites claros forman parte importante de esta configuración. "
        "Necesitas distinguir mejor qué pertenece realmente a tu experiencia y qué absorbes del entorno."
    ),

    "Plutón": (
        "La intensidad y los procesos profundos de transformación ocupan un lugar central dentro de esta figura. "
        "Las experiencias importantes suelen remover capas muy profundas de tu sistema."
    ),

    "Quirón": (
        "Hay una sensibilidad importante implicada en esta figura. "
        "Determinadas experiencias pueden tocar zonas vulnerables, pero también abrir una comprensión muy profunda de ciertos procesos humanos."
    ),

    "Lilith": (
        "Hay una parte muy instintiva y difícil de domesticar implicada aquí. "
        "La reacción aparece especialmente cuando algo se siente invasivo, falso o excesivamente controlador."
    ),

    "Nodo Norte": (
        "Esta figura está conectada con procesos importantes de crecimiento y evolución. "
        "Lo que ocurre aquí no suele sentirse accesorio: empuja hacia una dirección de desarrollo."
    ),

    "Nodo Sur": (
        "Aquí aparecen dinámicas antiguas y formas conocidas de responder que tienden a activarse automáticamente. "
        "Parte del trabajo consiste en no quedar atrapado únicamente en lo familiar."
    ),

    "Ascendente": (
        "La forma en que entras en la experiencia y respondes al entorno queda directamente implicada en esta configuración. "
        "La figura afecta de manera visible a tu forma de moverte por la vida."
    ),

    "Medio Cielo": (
        "La dirección vital, la vocación y la relación con el lugar que ocupas en el mundo participan directamente en esta figura. "
        "Las decisiones importantes suelen tener impacto profundo en tu camino externo."
    ),
}


# ─── MATICES SEGÚN CASAS IMPLICADAS ─────────────────────────────────────────

TEXTO_CASA_FIGURA = {

    1: (
        "Esta figura afecta directamente a la identidad, al cuerpo y a la forma en que entras en la experiencia. "
        "Las tensiones o apoyos internos suelen sentirse rápidamente en tu manera de actuar, reaccionar o posicionarte."
    ),

    2: (
        "La figura se vive especialmente en temas de valor personal, estabilidad y capacidad de sostener recursos. "
        "La relación con la seguridad material y con el propio valor interno adquiere mucho peso."
    ),

    3: (
        "La comunicación, el pensamiento y el intercambio cotidiano quedan muy implicados. "
        "La mente puede convertirse en uno de los principales lugares donde esta figura se activa."
    ),

    4: (
        "La figura toca profundamente la base emocional, la sensación de hogar y las necesidades de seguridad interna. "
        "Lo familiar y lo íntimo suelen tener mucho impacto en cómo se vive esta configuración."
    ),

    5: (
        "La creatividad, la expresión personal y la necesidad de sentir vitalidad forman parte importante de esta figura. "
        "Necesitas sentir que puedes expresarte con autenticidad."
    ),

    6: (
        "La figura afecta especialmente a los hábitos, el cuerpo y el funcionamiento cotidiano. "
        "El equilibrio depende mucho de cómo organizas ritmos, descanso y exigencia diaria."
    ),

    7: (
        "Las relaciones importantes y el vínculo con otras personas son uno de los escenarios principales donde esta figura se activa. "
        "Los demás suelen actuar como espejos importantes de estos procesos."
    ),

    8: (
        "La intensidad emocional, las pérdidas, los vínculos profundos y las situaciones difíciles de controlar forman parte central de esta figura. "
        "Los procesos importantes rara vez se viven superficialmente."
    ),

    9: (
        "La necesidad de comprensión, expansión y búsqueda de sentido participa activamente aquí. "
        "La figura suele empujarte a revisar creencias, perspectivas o formas de entender la vida."
    ),

    10: (
        "La vocación, la responsabilidad y el lugar que ocupas en el mundo quedan muy implicados. "
        "Las decisiones importantes suelen tener consecuencias visibles en tu dirección vital."
    ),

    11: (
        "La relación con grupos, amistades y proyectos compartidos participa directamente en esta figura. "
        "Necesitas revisar cuidadosamente qué espacios colectivos sostienen realmente tu energía."
    ),

    12: (
        "La figura se mueve mucho en capas internas, silenciosas o difíciles de ver inmediatamente. "
        "Puede haber procesos profundos que necesitan tiempo, pausa y retirada antes de poder comprenderse del todo."
    ),
}


def texto_matices_puntos(puntos):
    partes = []

    for p in ordenar_puntos(puntos):
        txt = TEXTO_PUNTO_FIGURA.get(p, "")
        if txt:
            partes.append(f"{p}: {txt}")

    return "\n\n".join(partes)


def texto_matices_casas(carta, puntos):
    casas = casas_de_puntos(carta, puntos)
    partes = []

    for c in casas:
        txt = TEXTO_CASA_FIGURA.get(c, "")
        if txt:
            partes.append(f"Casa {c}: {txt}")

    return "\n\n".join(partes)


def aspecto_de_figura(figura, simbolo):
    return [a for a in figura.get("aspectos", []) if a.get("simbolo") == simbolo]


def tiene_puntos(figura, *puntos):
    pts = set(figura.get("puntos", []))
    return all(p in pts for p in puntos)


def texto_casas_resumen(carta, puntos):
    casas = casas_de_puntos(carta, puntos)
    if not casas:
        return ""
    return descripcion_casas(casas)


def texto_figura(carta, figura):

    tipo = figura["tipo"]
    puntos = figura.get("puntos", [])
    puntos_txt = nombres_humanos(puntos)

    casas = descripcion_casas(casas_de_puntos(carta, puntos))
    signos = descripcion_signos(signos_de_puntos(carta, puntos))

    partes = []

    encabezado = f"{tipo}: {puntos_txt}."

    if casas:
        encabezado += f" Se activa principalmente en {casas}."

    partes.append(encabezado)

    # ─────────────────────────────────────────────────────────────
    # COMETA
    # ─────────────────────────────────────────────────────────────

    if tipo == "Cometa":

        foco = figura["foco"]
        oposicion_a = figura["oposicion_a"]
        base = nombres_humanos(figura["gran_trigono"])

        # Caso específico: Sol oposición Plutón
        if tiene_puntos(figura, "Sol", "Plutón") and foco == "Plutón":
            partes.append(
                "Esta figura es una de las más potentes de la carta porque organiza una tensión profunda entre identidad, valor propio, control, pérdida y transformación."
            )

            partes.append(
                "La oposición Sol–Plutón no describe una incomodidad menor. Muestra una presión interna fuerte entre la necesidad de afirmarte, ocupar tu lugar y sostener tu propio valor, y una capa más profunda que te obliga a atravesar intensidad, crisis, vínculos de poder o experiencias donde no todo puede controlarse."
            )

            partes.append(
                f"El gran trígono entre {base} da recursos para sostener esa intensidad: sensibilidad, intuición, fuerza expresiva y capacidad de leer lo que ocurre por debajo de la superficie. "
                "Pero ese apoyo no debería usarse para aguantar más de la cuenta, sino para transformar la manera en que respondes cuando algo toca tu seguridad profunda."
            )

            partes.append(
                "La energía de esta figura va hacia Plutón: hacia una transformación real de la relación con el poder, el deseo, la entrega, el control y la supervivencia emocional. "
                "Cuando no se integra, puede aparecer como hipervigilancia, intensidad relacional, miedo a perder el control o sensación de tener que protegerte demasiado."
            )

            partes.append(
                "La resolución no consiste en suavizar Plutón ni en apagar el Sol. Consiste en construir una identidad capaz de atravesar profundidad sin quedar atrapada en lucha, defensa o desconfianza. "
                "Cuando esta figura madura, puede convertirse en una enorme capacidad para sostener procesos intensos sin destruirte por dentro."
            )

        else:
            partes.append(
                f"La base de esta figura está formada por un gran trígono entre {base}. "
                f"Ahí existe una circulación relativamente fluida de energía: recursos, capacidades y una forma bastante natural de sostener determinadas experiencias."
            )

            partes.append(
                f"Sin embargo, la oposición entre {foco} y {oposicion_a} impide que esa energía quede cerrada sobre sí misma. "
                f"La tensión empuja hacia movimiento, definición y dirección concreta."
            )

            partes.append(
                f"El foco real de la figura está en {foco}. "
                f"Ahí suele concentrarse la necesidad de respuesta, visibilidad o transformación. "
                f"Cuando esta energía no encuentra salida consciente, puede aparecer sensación de sobrecarga, exceso de presión interna o dificultad para dosificar."
            )

            partes.append(
                "La integración no pasa por eliminar la tensión, sino por usar el sostén del gran trígono como base para dirigir energía hacia algo concreto y vivo."
            )

    # ─────────────────────────────────────────────────────────────
    # T-CUADRADA
    # ─────────────────────────────────────────────────────────────

    elif tipo == "T-cuadrada":

        op1, op2 = figura["oposicion"]
        apice = figura["apice"]

        if "Nodo Norte" in puntos and "Nodo Sur" in puntos and apice == "Neptuno":
            partes.append(
                "Esta T-cuadrada no habla solo de tensión relacional o mental. "
                "Organiza una presión evolutiva fuerte entre una forma antigua de refugiarte, adaptarte o diluirte, y una dirección de crecimiento que pide más límite, discernimiento y presencia."
            )

            partes.append(
                "El eje Nodo Sur–Nodo Norte marca una polaridad de fondo: una parte de ti conoce muy bien ciertos modos de protección, sensibilidad o respuesta automática; otra parte necesita avanzar hacia una forma más clara, concreta y discriminada de estar en el vínculo y en la vida."
            )

            partes.append(
                "Neptuno en el ápice recibe la presión de esa polaridad. "
                "Ahí puede aparecer confusión, idealización, exceso de permeabilidad, cansancio por absorber demasiado o dificultad para saber qué es realmente tuyo y qué pertenece al entorno."
            )

            partes.append(
                "Como el stellium está implicado, esta tensión no se queda en una sola zona. "
                "Atraviesa la mente, el deseo de armonía, la acción y formas antiguas de responder. "
                "Por eso puede sentirse como una mezcla de lucidez, impulso, entrega y agotamiento si no hay suficiente límite."
            )

            partes.append(
                "La resolución no consiste en dejar de ser sensible. "
                "Consiste en que la sensibilidad tenga borde. "
                "Cuando esta figura madura, la intuición deja de funcionar como absorción y empieza a convertirse en orientación clara."
            )

        else:
            partes.append(
                f"La oposición entre {op1} y {op2} crea una polaridad interna importante. "
                f"Las dos partes necesitan cosas distintas y rara vez se estabilizan del todo."
            )

            partes.append(
                f"La energía de la figura descarga principalmente en {apice}. "
                f"Ahí suele aparecer la reacción, la sensación de presión o el intento de resolver rápidamente lo que se activa."
            )

            partes.append(
                "Esta configuración genera mucho movimiento interno. "
                "Puede dar capacidad de respuesta, resistencia y fuerza de transformación, pero también tendencia a vivir en exigencia constante o en sensación de urgencia."
            )

            partes.append(
                "La resolución no consiste en elegir uno de los polos y rechazar el otro. "
                "Consiste en construir suficiente estructura interna para sostener ambos sin reaccionar automáticamente."
            )

    # ─────────────────────────────────────────────────────────────
    # GRAN TRÍGONO
    # ─────────────────────────────────────────────────────────────

    elif tipo == "Gran trígono":

        partes.append(
            "Esta figura crea un circuito de apoyo interno. "
            "La energía circula con relativa facilidad entre los puntos implicados, como si esas partes de la carta se reconocieran entre sí."
        )

        partes.append(
            "Puede funcionar como sostén, talento natural o capacidad espontánea de regulación. "
            "En momentos difíciles suele convertirse en una zona de apoyo importante."
        )

        partes.append(
            "El riesgo aparece cuando esta facilidad se convierte en circuito cerrado. "
            "La persona puede apoyarse siempre en la misma dinámica y evitar movimientos necesarios o situaciones que obliguen a salir de lo conocido."
        )

        partes.append(
            "La integración aparece cuando este sostén se usa como base para crecer, no como refugio permanente."
        )

    # ─────────────────────────────────────────────────────────────
    # TRIÁNGULO DE APRENDIZAJE
    # ─────────────────────────────────────────────────────────────

    elif tipo in (
        "Triángulo de aprendizaje",
        "Triángulo de aprendizaje pequeño",
        "Triángulo de aprendizaje mediano",
    ):

        asp_q = next((a for a in figura["aspectos"] if a["simbolo"] == "⚻"), None)
        asp_c = next((a for a in figura["aspectos"] if a["simbolo"] == "□"), None)
        asp_t = next((a for a in figura["aspectos"] if a["simbolo"] == "△"), None)
        asp_s = next((a for a in figura["aspectos"] if a["simbolo"] == "✶"), None)
        asp_ss = next((a for a in figura["aspectos"] if a["simbolo"] == "⚺"), None)

        if asp_c:
            partes.append(
                f"La tensión principal aparece en la cuadratura entre {asp_c['p1']} y {asp_c['p2']}. "
                "Ahí suele haber fricción, exigencia o sensación de incompatibilidad entre dos formas de responder."
            )

        if asp_q:
            partes.append(
                f"El quincuncio entre {asp_q['p1']} y {asp_q['p2']} obliga a reajustar constantemente la respuesta. "
                "No se resuelve desde control directo, sino desde observación fina y capacidad de adaptación."
            )

        if asp_t:
            partes.append(
                f"El trígono entre {asp_t['p1']} y {asp_t['p2']} funciona como apoyo interno. "
                "Ahí existe una posibilidad de sostén, comprensión o regulación que ayuda a integrar la figura."
            )

        if asp_s:
            partes.append(
                f"El sextil entre {asp_s['p1']} y {asp_s['p2']} ofrece una vía de apoyo y cooperación. "
                "No resuelve por sí solo la tensión, pero facilita recursos para trabajarla."
            )

        if asp_ss:
            partes.append(
                f"El semisextil entre {asp_ss['p1']} y {asp_ss['p2']} introduce un enlace sutil. "
                "Su integración depende de pequeños reajustes, atención y afinación progresiva."
            )

        partes.append(
            "Este tipo de configuración suele madurar lentamente. "
            "No se resuelve de una vez: se afina con experiencia, repetición y capacidad de reconocer cuándo estás reaccionando desde automatismo."
        )

    # ─────────────────────────────────────────────────────────────
    # OJO PEQUEÑO
    # ─────────────────────────────────────────────────────────────

    elif tipo == "Ojo pequeño":

        semisextiles = [
            a
            for a in figura["aspectos"]
            if a["simbolo"] == "⚺"
        ]
        asp_s = next(
            (
                a
                for a in figura["aspectos"]
                if a["simbolo"] == "✶"
            ),
            None,
        )

        for asp_ss in semisextiles:
            partes.append(
                f"El semisextil entre {asp_ss['p1']} y {asp_ss['p2']} aporta un enlace sutil que necesita atención. "
                "La relación se construye mediante pequeños pasos de observación y ajuste."
            )

        if asp_s:
            partes.append(
                f"El sextil entre {asp_s['p1']} y {asp_s['p2']} ofrece el cauce más accesible de la figura. "
                "Permite relacionar y elaborar la información recogida por los dos semisextiles."
            )

        partes.append(
            "Esta figura funciona mejor como una antena de matices que como una presión frontal. "
            "Su recurso está en observar, relacionar y dar forma progresivamente a lo percibido."
        )

    # ─────────────────────────────────────────────────────────────
    # STELLIUM
    # ─────────────────────────────────────────────────────────────

    elif tipo == "Stellium":

        casa = figura.get("casa", "")

        partes.append(
            f"Esta figura concentra mucha energía en Casa {casa}. "
            "No se activa una sola función psicológica: se moviliza un bloque entero de la carta."
        )

        partes.append(
            "Por eso este territorio puede sentirse especialmente intenso, absorbente o central en la vida. "
            "Ahí suele acumularse atención, presión, aprendizaje y necesidad de respuesta."
        )

        partes.append(
            "Cuando esta concentración no tiene suficiente regulación, puede aparecer saturación, exceso de identificación o dificultad para tomar distancia."
        )

        partes.append(
            "La integración pasa por aprender a dosificar la energía y evitar que toda la identidad quede atrapada dentro de un único territorio vital."
        )

    # ─────────────────────────────────────────────────────────────
    # YOD
    # ─────────────────────────────────────────────────────────────

    elif tipo == "Yod":

        apice = figura["apice"]
        base1, base2 = figura["base"]

        partes.append(
            f"La base formada entre {base1} y {base2} crea una posibilidad de apoyo o compensación relativamente estable."
        )

        partes.append(
            f"Sin embargo, toda la figura apunta hacia {apice}. "
            "Ahí aparece una presión difícil de controlar racionalmente, como si una parte de la carta necesitara reajustarse continuamente."
        )

        partes.append(
            "El Yod no suele sentirse como conflicto frontal. "
            "Opera más bien como una incomodidad persistente, una sensación de que algo necesita recolocarse aunque no siempre resulte fácil entender exactamente qué."
        )

        partes.append(
            "La integración llega cuando dejas de intentar forzar respuestas inmediatas y empiezas a trabajar con más precisión, escucha y capacidad de ajuste."
        )

    return "\n\n".join(partes)


def es_figura_mayor(figura):
    tipo = figura.get("tipo", "")
    puntos = set(figura.get("puntos", []))
    peso = figura.get("peso", 0)

    if tipo == "Cometa":
        return True

    if tipo == "T-cuadrada" and peso >= 16:
        return True

    if tipo == "Yod" and peso >= 18:
        return True

    if "Sol" in puntos and ("Plutón" in puntos or "Saturno" in puntos):
        return True

    if "Luna" in puntos and ("Saturno" in puntos or "Plutón" in puntos):
        return True

    if "Ascendente" in puntos or "Medio Cielo" in puntos:
        if tipo in ("Cometa", "T-cuadrada", "Yod", "Gran trígono"):
            return True

    return False



def clasificar_figuras(figuras):
    """
    Clasificación para el análisis global posterior a Huber 2026.

    No vuelve a decidir qué figura es importante. Todas las figuras
    geométricas que llegan aquí ya han superado la selección 2026.
    Stellium queda como estructura colectiva complementaria.
    """
    principales = []
    secundarias = []
    derivadas = []

    for figura in figuras:
        rol = figura.get("seleccion_huber_2026")

        if figura.get("tipo") == "Stellium" or rol == "complementaria":
            secundarias.append(figura)
        else:
            principales.append(figura)

    return principales, secundarias, derivadas



# ─── ANÁLISIS GLOBAL DE LA ARQUITECTURA ──────────────────────────────────────
def puntos_reales_figura(figura):
    """
    Devuelve únicamente los puntos que forman geométricamente la figura.

    Si la figura ha sido expandida por pertenencia a un stellium,
    evita contar los demás componentes del stellium como si fueran
    vértices reales de la configuración.
    """

    tipo = figura.get("tipo", "")

    if figura.get("puntos_geometricos"):
        return ordenar_puntos(
            figura.get("puntos_geometricos", [])
        )

    # El stellium sí está formado realmente por todos sus puntos
    if tipo == "Stellium":
        return ordenar_puntos(figura.get("puntos", []))

    # En el resto de figuras reconstruimos los puntos
    # directamente desde los aspectos que forman la geometría.
    puntos = []

    for asp in figura.get("aspectos", []):
        p1 = asp.get("p1")
        p2 = asp.get("p2")

        if p1:
            puntos.append(p1)

        if p2:
            puntos.append(p2)

    return ordenar_puntos(
        list(dict.fromkeys(puntos))
    )


def puntos_participantes_figura(figura):
    """Puntos que aportan estructura, sin inflar un stellium expandido.

    Los extremos de los aspectos cuentan siempre. Una conjunción usada como
    vértice aporta todos sus miembros porque constituye una unidad real. En
    cambio, los miembros de un stellium añadidos solo para mostrar el vértice
    no se atribuyen automáticamente a todas sus figuras derivadas.
    """
    if figura.get("tipo") == "Stellium":
        return ordenar_puntos(figura.get("puntos", []))

    puntos = []

    for aspecto in figura.get("aspectos", []):
        for clave in ("p1", "p2"):
            punto = aspecto.get(clave)

            if punto:
                puntos.append(punto)

    for vertice in figura.get("vertices", []):
        if vertice.get("tipo") in ("Conjunción", "Stellium"):
            puntos.extend(
                vertice.get("puntos", [])
            )

    return ordenar_puntos(
        list(dict.fromkeys(puntos))
    )

def contiene_eje_nodal(figura):
    puntos = set(puntos_reales_figura(figura))

    return (
        "Nodo Norte" in puntos
        or "Nodo Sur" in puntos
    )

def nodos_reales_figura(figura):
    puntos = set(puntos_reales_figura(figura))

    nodos = []

    if "Nodo Norte" in puntos:
        nodos.append("Nodo Norte")

    if "Nodo Sur" in puntos:
        nodos.append("Nodo Sur")

    return nodos

def clasificar_implicacion_nodal(figura):
    """
    Clasifica cómo participan los nodos dentro de una figura.

    Devuelve:
    - "ninguna"
    - "nodo_norte"
    - "nodo_sur"
    - "eje_nodal_completo"
    """

    nodos = nodos_reales_figura(figura)

    if not nodos:
        return "ninguna"

    if "Nodo Norte" in nodos and "Nodo Sur" in nodos:
        return "eje_nodal_completo"

    if "Nodo Norte" in nodos:
        return "nodo_norte"

    if "Nodo Sur" in nodos:
        return "nodo_sur"

    return "ninguna"


def clasificar_jerarquia_figura(figura):
    """
    Compatibilidad con campos antiguos.

    Desde Huber 2026 NO asignamos una jerarquía psicológica a una figura
    a partir de una suma arbitraria de categoría + orbe + tipo.

    La decisión de qué figuras permanecen se toma después mediante
    geometría → reserva → rescate. Estos campos se conservan para no romper
    consumidores antiguos, pero ya no deben utilizarse para seleccionar.
    """
    return {
        "jerarquia": "candidata",
        "puntuacion_jerarquia": 0,
    }


def clasificar_categoria_figura(figura):
    puntos = puntos_reales_figura(figura)

    nucleares = [
        p for p in puntos
        if p in PUNTOS_NUCLEARES
    ]

    estructurales = [
        p for p in puntos
        if p in PUNTOS_ESTRUCTURALES
    ]

    sensibles = [
        p for p in puntos
        if p in PUNTOS_SENSIBLES
    ]

    n_nucleares = len(nucleares)
    n_estructurales = len(estructurales)

    if n_nucleares >= 3:
        categoria = "nuclear"

    elif n_nucleares >= 2:
        categoria = "estructural"

    elif (
        n_nucleares >= 1
        and n_estructurales >= 1
    ):
        categoria = "estructural"

    elif n_nucleares == 1:
        categoria = "sensible"

    else:
        categoria = "auxiliar"

    return {
        "categoria": categoria,
        "nucleares": nucleares,
        "estructurales": estructurales,
        "sensibles": sensibles,
    }


def clasificar_consistencia_figura(figura):
    tipo = figura.get("tipo", "")

    # ── STELLIUM ────────────────────────────────────────────────
    if tipo == "Stellium":
        puntos = figura.get("puntos", [])

        if len(puntos) < 3:
            return {
                "orbe_medio": None,
                "orbe_maximo": None,
                "consistencia": "no_aplica",
            }

        amplitud = figura.get("amplitud")

        if amplitud is None:
            return {
                "orbe_medio": None,
                "orbe_maximo": None,
                "consistencia": "pendiente",
            }

        if amplitud <= 10:
            consistencia = "muy_alta"

        elif amplitud <= 15:
            consistencia = "alta"

        elif amplitud <= 20:
            consistencia = "media"

        else:
            consistencia = "amplia"

        return {
            "orbe_medio": None,
            "orbe_maximo": round(amplitud, 2),
            "consistencia": consistencia,
        }

    # ── RESTO DE FIGURAS ───────────────────────────────────────
    aspectos = figura.get("aspectos", [])

    if not aspectos:
        return {
            "orbe_medio": None,
            "orbe_maximo": None,
            "consistencia": "no_aplica",
        }

    orbes = [
        a["orbe"]
        for a in aspectos
        if a.get("orbe") is not None
    ]

    if not orbes:
        return {
            "orbe_medio": None,
            "orbe_maximo": None,
            "consistencia": "no_aplica",
        }

    orbe_medio = sum(orbes) / len(orbes)
    orbe_maximo = max(orbes)

    if orbe_medio <= 3 and orbe_maximo <= 5:
        consistencia = "muy_alta"

    elif orbe_medio <= 4.5 and orbe_maximo <= 7:
        consistencia = "alta"

    elif orbe_medio <= 6 and orbe_maximo <= 9:
        consistencia = "media"

    else:
        consistencia = "amplia"

    return {
        "orbe_medio": round(orbe_medio, 2),
        "orbe_maximo": round(orbe_maximo, 2),
        "consistencia": consistencia,
    }


def detectar_nucleos_compartidos(figuras):
    """
    Detecta núcleos estructurales respetando stelliums y conjunciones.

    Regla principal:
    - un Stellium o una Conjunción se trata como UNA UNIDAD;
    - no se descompone en todos sus pares internos;
    - no se crean seis núcleos diferentes dentro de un stellium de
      cuatro miembros;
    - los pares atómicos solo se calculan entre puntos que no forman
      parte de un vértice colectivo repetido.

    Esto reduce cantidad y aumenta refinamiento.
    """

    # ------------------------------------------------------------
    # 1. Contar vértices colectivos repetidos.
    # ------------------------------------------------------------
    colectivos = {}

    for figura in figuras:
        for vertice in figura.get("vertices", []) or []:
            tipo_vertice = vertice.get("tipo")

            if tipo_vertice not in ("Stellium", "Conjunción"):
                continue

            puntos = tuple(
                ordenar_puntos(
                    vertice.get("puntos", [])
                )
            )

            if len(puntos) < 2:
                continue

            clave = (
                tipo_vertice,
                puntos,
            )

            if clave not in colectivos:
                colectivos[clave] = {
                    "tipo_nucleo": tipo_vertice.lower(),
                    "puntos_nucleo": list(puntos),
                    "figuras": [],
                    "apariciones": 0,
                }

            colectivos[clave]["figuras"].append({
                "tipo": figura.get("tipo", ""),
                "jerarquia": figura.get("jerarquia", ""),
                "consistencia": figura.get("consistencia", ""),
                "puntuacion_jerarquia": figura.get(
                    "puntuacion_jerarquia", 0
                ),
            })

            colectivos[clave]["apariciones"] += 1

    # Todos los puntos que pertenecen a un colectivo repetido.
    # Si el colectivo aparece en varias figuras, sus miembros no
    # deben generar además núcleos pareados internos.
    miembros_colectivos_repetidos = set()

    for datos in colectivos.values():
        if datos["apariciones"] >= 2:
            miembros_colectivos_repetidos.update(
                datos["puntos_nucleo"]
            )

    # ------------------------------------------------------------
    # 2. Núcleos atómicos entre puntos independientes.
    # ------------------------------------------------------------
    nucleos_atomicos = {}

    for figura in figuras:
        puntos_independientes = []

        # Usamos los vértices, no la lista expandida de puntos.
        for vertice in figura.get("vertices", []) or []:
            tipo_vertice = vertice.get("tipo")
            puntos_vertice = ordenar_puntos(
                vertice.get("puntos", [])
            )

            if tipo_vertice in ("Stellium", "Conjunción"):
                # El colectivo se trata como una sola unidad y no
                # se descompone aquí.
                continue

            if (
                tipo_vertice == "Punto"
                and len(puntos_vertice) == 1
            ):
                puntos_independientes.append(
                    puntos_vertice[0]
                )

        # Compatibilidad con figuras antiguas sin vertices.
        if not figura.get("vertices"):
            puntos_independientes = [
                p
                for p in puntos_reales_figura(figura)
                if p not in miembros_colectivos_repetidos
            ]

        puntos_independientes = ordenar_puntos(
            list(dict.fromkeys(puntos_independientes))
        )

        for i in range(len(puntos_independientes)):
            for j in range(i + 1, len(puntos_independientes)):
                p1 = puntos_independientes[i]
                p2 = puntos_independientes[j]

                # Si ambos pertenecen a la misma concentración
                # colectiva repetida, nunca los convertimos en
                # núcleo separado.
                if (
                    p1 in miembros_colectivos_repetidos
                    and p2 in miembros_colectivos_repetidos
                ):
                    continue

                clave = tuple(sorted([p1, p2]))

                if clave not in nucleos_atomicos:
                    nucleos_atomicos[clave] = {
                        "tipo_nucleo": "pareja",
                        "puntos_nucleo": list(clave),
                        "figuras": [],
                        "apariciones": 0,
                    }

                nucleos_atomicos[clave]["figuras"].append({
                    "tipo": figura.get("tipo", ""),
                    "jerarquia": figura.get("jerarquia", ""),
                    "consistencia": figura.get("consistencia", ""),
                    "puntuacion_jerarquia": figura.get(
                        "puntuacion_jerarquia", 0
                    ),
                })

                nucleos_atomicos[clave]["apariciones"] += 1

    # ------------------------------------------------------------
    # 3. Reunir solo elementos realmente repetidos.
    # ------------------------------------------------------------
    candidatos = []

    for datos in colectivos.values():
        if datos["apariciones"] >= 2:
            candidatos.append(datos)

    for datos in nucleos_atomicos.values():
        if datos["apariciones"] >= 2:
            candidatos.append(datos)

    # ------------------------------------------------------------
    # 4. Puntuación.
    # ------------------------------------------------------------
    for datos in candidatos:
        puntuacion_figuras = sum(
            f.get("puntuacion_jerarquia", 0)
            for f in datos["figuras"]
        )

        bonus_repeticion = max(
            0,
            datos["apariciones"] - 1
        ) * 2

        # Ligero bonus para un colectivo real porque representa
        # una unidad estructural comprobada, no una pareja inferida.
        bonus_colectivo = (
            4
            if datos.get("tipo_nucleo")
            in ("stellium", "conjunción", "conjuncion")
            else 0
        )

        datos["puntuacion_nucleo"] = (
            puntuacion_figuras
            + bonus_repeticion
            + bonus_colectivo
        )

        if datos["puntuacion_nucleo"] >= 26:
            datos["jerarquia_nucleo"] = "dominante"
        elif datos["puntuacion_nucleo"] >= 20:
            datos["jerarquia_nucleo"] = "relevante"
        else:
            datos["jerarquia_nucleo"] = "secundario"

    # ------------------------------------------------------------
    # 5. Unicidad canónica.
    # ------------------------------------------------------------
    unicos = {}

    for nucleo in candidatos:
        tipo_nucleo = nucleo.get(
            "tipo_nucleo",
            "pareja"
        )

        puntos = tuple(
            ordenar_puntos(
                nucleo.get("puntos_nucleo", [])
            )
        )

        clave = (
            tipo_nucleo,
            puntos,
        )

        existente = unicos.get(clave)

        if existente is None:
            nucleo["puntos_nucleo"] = list(puntos)
            unicos[clave] = nucleo
            continue

        criterio_nuevo = (
            nucleo.get("puntuacion_nucleo", 0),
            nucleo.get("apariciones", 0),
        )
        criterio_existente = (
            existente.get("puntuacion_nucleo", 0),
            existente.get("apariciones", 0),
        )

        if criterio_nuevo > criterio_existente:
            nucleo["puntos_nucleo"] = list(puntos)
            unicos[clave] = nucleo

    resultado = list(unicos.values())

    resultado.sort(
        key=lambda x: (
            -x.get("puntuacion_nucleo", 0),
            -x.get("apariciones", 0),
            -len(x.get("puntos_nucleo", [])),
        )
    )

    return resultado

def detectar_familias_nucleos(nucleos):
    """
    Agrupa núcleos compartidos que tienen un punto en común.

    Permite detectar familias estructurales mayores:
    varios núcleos distintos organizados alrededor
    de un mismo punto.
    """

    familias = {}

    for nucleo in nucleos:

        puntos = nucleo.get("puntos_nucleo", [])

        for punto in puntos:

            if punto not in familias:
                familias[punto] = {
                    "punto_central": punto,
                    "nucleos": [],
                    "puntos_relacionados": set(),
                    "puntuacion_total": 0,
                }

            familias[punto]["nucleos"].append(nucleo)

            for otro in puntos:
                if otro != punto:
                    familias[punto]["puntos_relacionados"].add(otro)

            familias[punto]["puntuacion_total"] += nucleo.get(
                "puntuacion_nucleo", 0
            )

    resultado = []

    for datos in familias.values():

        # Solo consideramos familia cuando el punto central
        # participa en al menos dos núcleos compartidos.
        if len(datos["nucleos"]) < 2:
            continue

        datos["puntos_relacionados"] = ordenar_puntos(
            list(datos["puntos_relacionados"])
        )

        datos["numero_nucleos"] = len(datos["nucleos"])

        if datos["puntuacion_total"] >= 65:
            datos["jerarquia_familia"] = "dominante"

        elif datos["puntuacion_total"] >= 45:
            datos["jerarquia_familia"] = "relevante"

        else:
            datos["jerarquia_familia"] = "secundaria"

        resultado.append(datos)

    resultado.sort(
        key=lambda x: (
            -x["puntuacion_total"],
            -x["numero_nucleos"]
        )
    )

    return resultado

def detectar_puntos_organizadores(
    puntos_estructurales,
    familias_nucleos
):
    """
    Combina la importancia estructural individual de cada punto
    con su papel como centro de una familia de núcleos.

    Devuelve los puntos que funcionan como organizadores
    globales de la arquitectura de la carta.
    """

    mapa_familias = {
        f["punto_central"]: f
        for f in familias_nucleos
    }

    resultado = []

    for punto in puntos_estructurales:

        nombre = punto["punto"]

        puntuacion_estructural = punto.get(
            "puntuacion", 0
        )

        familia = mapa_familias.get(nombre)

        if familia:
            puntuacion_familia = familia.get(
                "puntuacion_total", 0
            )

            numero_nucleos = familia.get(
                "numero_nucleos", 0
            )

            jerarquia_familia = familia.get(
                "jerarquia_familia", ""
            )

        else:
            puntuacion_familia = 0
            numero_nucleos = 0
            jerarquia_familia = None

        # La familia pesa, pero no usamos toda su puntuación
        # para evitar que eclipse completamente
        # la importancia estructural individual.
        puntuacion_global = (
            puntuacion_estructural
            + puntuacion_familia * 0.5
        )

        resultado.append({
            "punto": nombre,

            "puntuacion_estructural": puntuacion_estructural,
            "puntuacion_familia": puntuacion_familia,

            "numero_nucleos": numero_nucleos,
            "jerarquia_familia": jerarquia_familia,

            "puntuacion_global": round(
                puntuacion_global, 2
            ),
        })

    resultado.sort(
        key=lambda x: (
            -x["puntuacion_global"],
            -x["puntuacion_estructural"]
        )
    )

    return resultado

def clasificar_puntos_organizadores(puntos_organizadores):

    resultado = []

    if not puntos_organizadores:
        return resultado

    puntuacion_maxima = max(
        p.get("puntuacion_global", 0)
        for p in puntos_organizadores
    )

    for indice, p in enumerate(puntos_organizadores):

        puntuacion = p["puntuacion_global"]

        if (
            indice < 2
            and puntuacion >= 40
            and puntuacion >= puntuacion_maxima * 0.82
        ):
            jerarquia = "dominante"

        elif (
            indice < 5
            and puntuacion >= 30
            and puntuacion >= puntuacion_maxima * 0.65
        ):
            jerarquia = "relevante"

        elif indice < 8 and puntuacion >= 20:
            jerarquia = "secundario"

        else:
            jerarquia = "periferico"

        nuevo = dict(p)
        nuevo["jerarquia_global"] = jerarquia

        resultado.append(nuevo)

    return resultado

def calcular_casas_estructurales(carta, figuras):
    """
    Calcula el peso estructural de las casas según
    las figuras reales en las que participan sus puntos.

    No todas las apariciones pesan igual:
    se tiene en cuenta la jerarquía de cada figura.
    """

    planetas = carta["planetas"]

    peso_jerarquia = {
        "central": 4,
        "relevante": 3,
        "secundaria": 2,
        "periferica": 1,
    }

    casas = {}

    for figura in figuras:

        puntos = puntos_participantes_figura(figura)

        peso_figura = peso_jerarquia.get(
            figura.get("jerarquia", ""),
            1
        )

        for punto in puntos:

            if punto not in planetas:
                continue

            casa = planetas[punto].get("casa")

            if not casa:
                continue

            if casa not in casas:
                casas[casa] = {
                    "casa": casa,
                    "apariciones": 0,
                    "puntuacion": 0,
                    "figuras": [],
                }

            casas[casa]["apariciones"] += 1
            casas[casa]["puntuacion"] += peso_figura

            casas[casa]["figuras"].append({
                "tipo": figura.get("tipo", ""),
                "jerarquia": figura.get("jerarquia", ""),
            })

    resultado = list(casas.values())

    resultado.sort(
        key=lambda x: (
            -x["puntuacion"],
            -x["apariciones"],
            x["casa"]
        )
    )

    return resultado

def clasificar_casas_estructurales(casas_estructurales):

    resultado = []

    for casa in casas_estructurales:

        puntuacion = casa["puntuacion"]

        if puntuacion >= 22:
            jerarquia = "dominante"

        elif puntuacion >= 14:
            jerarquia = "relevante"

        elif puntuacion >= 7:
            jerarquia = "secundaria"

        else:
            jerarquia = "periferica"

        nuevo = dict(casa)
        nuevo["jerarquia_casa"] = jerarquia

        resultado.append(nuevo)

    return resultado

def calcular_ejes_casas(casas_estructurales):

    mapa = {
        c["casa"]: c
        for c in casas_estructurales
    }

    pares = [
        (1, 7),
        (2, 8),
        (3, 9),
        (4, 10),
        (5, 11),
        (6, 12),
    ][:5]

    resultado = []

    for casa_a, casa_b in pares:

        datos_a = mapa.get(casa_a, {
            "puntuacion": 0,
            "apariciones": 0,
        })

        datos_b = mapa.get(casa_b, {
            "puntuacion": 0,
            "apariciones": 0,
        })

        puntuacion_total = (
            datos_a.get("puntuacion", 0)
            + datos_b.get("puntuacion", 0)
        )

        apariciones_total = (
            datos_a.get("apariciones", 0)
            + datos_b.get("apariciones", 0)
        )

        resultado.append({
            "eje": f"{casa_a}-{casa_b}",
            "casa_1": casa_a,
            "casa_2": casa_b,
            "puntuacion_total": puntuacion_total,
            "apariciones_total": apariciones_total,
        })

    resultado.sort(
        key=lambda x: (
            -x["puntuacion_total"],
            -x["apariciones_total"]
        )
    )

    return resultado

def clasificar_ejes_casas(ejes_casas):

    resultado = []

    for eje in ejes_casas:

        puntuacion = eje["puntuacion_total"]

        if puntuacion >= 40:
            jerarquia = "dominante"

        elif puntuacion >= 20:
            jerarquia = "relevante"

        elif puntuacion >= 10:
            jerarquia = "secundario"

        else:
            jerarquia = "periferico"

        nuevo = dict(eje)
        nuevo["jerarquia_eje"] = jerarquia

        resultado.append(nuevo)

    return resultado


def construir_resumen_estructural(
    figuras,
    puntos_organizadores,
    casas_estructurales,
    ejes_casas,
    nucleos_compartidos,
    familias_nucleos,
):
    """
    Síntesis estructurada para IA.

    Desde Huber 2026 NO filtra figuras mediante la antigua puntuación
    central/relevante. La lista recibida ya es la lista final seleccionada
    por geometría, reserva y rescate.
    """

    figuras_seleccionadas = []

    orden_rol = {
        "principal": 0,
        "rescate": 1,
        "complementaria": 2,
    }

    for figura in figuras:
        rol = figura.get("seleccion_huber_2026") or "principal"

        figura_resumen = {
            "tipo": figura.get("tipo", ""),
            "nombre_canonico": figura.get(
                "nombre_canonico",
                figura.get("tipo", ""),
            ),
            "puntos": ordenar_puntos(
                figura.get(
                    "puntos",
                    puntos_reales_figura(figura),
                )
            ),
            "puntos_geometricos": puntos_reales_figura(figura),
            "categoria": figura.get("categoria", ""),
            "consistencia": figura.get("consistencia", ""),
            "seleccion_huber_2026": rol,
            "fase_seleccion_huber_2026": figura.get(
                "fase_seleccion_huber_2026"
            ),
            "estado_composicion_huber": figura.get(
                "estado_composicion_huber"
            ),
            "eje_nodal_implicado": figura.get(
                "eje_nodal_implicado",
                False,
            ),
            "tipo_implicacion_nodal": figura.get(
                "tipo_implicacion_nodal",
                "ninguna",
            ),
        }

        for campo_geometrico in (
            "apice",
            "base",
            "oposicion",
            "vertices",
            "componentes",
            "relacion_componentes",
        ):
            if campo_geometrico in figura:
                figura_resumen[campo_geometrico] = figura[campo_geometrico]

        figuras_seleccionadas.append(figura_resumen)

    figuras_seleccionadas.sort(
        key=lambda item: (
            orden_rol.get(item.get("seleccion_huber_2026"), 9),
            item.get("nombre_canonico", item.get("tipo", "")),
        )
    )

    puntos_seleccionados = [
        p
        for p in puntos_organizadores
        if p.get("jerarquia_global") in ("dominante", "relevante")
    ][:5]

    casas_seleccionadas = [
        c
        for c in casas_estructurales
        if c.get("jerarquia_casa") in ("dominante", "relevante")
    ]

    ejes_seleccionados = [
        e
        for e in ejes_casas
        if e.get("jerarquia_eje") in ("dominante", "relevante")
    ]

    nucleos_seleccionados = [
        n
        for n in nucleos_compartidos
        if n.get("jerarquia_nucleo") in ("dominante", "relevante")
    ][:6]

    familias_seleccionadas = [
        f
        for f in familias_nucleos
        if f.get("jerarquia_familia") in ("dominante", "relevante")
    ][:4]

    return {
        "figuras": figuras_seleccionadas,
        "puntos_organizadores": puntos_seleccionados,
        "casas": casas_seleccionadas,
        "ejes_casas": ejes_seleccionados,
        "nucleos": nucleos_seleccionados,
        "familias": familias_seleccionadas,
    }


def analizar_arquitectura_carta(carta, aspectos, figuras):
    """
    Analiza cómo se organiza la carta como conjunto.

    No interpreta todavía el significado psicológico.
    Su función es detectar:

    - qué puntos aparecen repetidamente en las figuras;
    - qué casas concentran más actividad estructural;
    - qué figuras comparten puntos;
    - qué configuraciones parecen formar parte del mismo núcleo;
    - qué puntos funcionan como organizadores de la carta.

    Devuelve datos estructurados para que después puedan ser
    interpretados por la IA.
    """

    planetas = carta["planetas"]

    principales, secundarias, derivadas = clasificar_figuras(figuras)

    nucleos_compartidos = detectar_nucleos_compartidos(figuras)

    familias_nucleos = detectar_familias_nucleos(nucleos_compartidos)

    casas_estructurales = calcular_casas_estructurales(
        carta,
        figuras
    )

    casas_estructurales = clasificar_casas_estructurales(
        casas_estructurales
    )

    ejes_casas = calcular_ejes_casas(
        casas_estructurales
    )

    ejes_casas = clasificar_ejes_casas(
        ejes_casas
    )

    # ─────────────────────────────────────────────────────────────
    # 1. FRECUENCIA DE CADA PUNTO EN LAS FIGURAS
    # ─────────────────────────────────────────────────────────────

    frecuencia_puntos = {}

    for figura in figuras:
        for punto in puntos_participantes_figura(figura):
            frecuencia_puntos[punto] = frecuencia_puntos.get(punto, 0) + 1

    # ─────────────────────────────────────────────────────────────
    # FRECUENCIA Y PESO DE LOS PUNTOS EN ASPECTOS
    # ─────────────────────────────────────────────────────────────

    frecuencia_aspectos = {}
    peso_aspectos = {}

    for aspecto in aspectos:

        p1 = aspecto["p1"]
        p2 = aspecto["p2"]
        orbe = aspecto["orbe"]

        # El semisextil solo tiene peso cuando completa una
        # figura reconocida. Como aspecto aislado no aumenta
        # la frecuencia ni la puntuación estructural.
        if aspecto.get("simbolo") == "⚺":
            continue

        # La oposición entre los dos nodos es automática
        # y no debe aumentar su peso estructural.
        if {p1, p2} == {"Nodo Norte", "Nodo Sur"}:
            continue

        # Número de aspectos en los que participa cada punto
        frecuencia_aspectos[p1] = frecuencia_aspectos.get(p1, 0) + 1
        frecuencia_aspectos[p2] = frecuencia_aspectos.get(p2, 0) + 1

        # Cuanto más exacto el aspecto, mayor peso.
        if orbe <= 1:
            peso_orbe = 3
        elif orbe <= 3:
            peso_orbe = 2
        elif orbe <= 6:
            peso_orbe = 1
        else:
            peso_orbe = 0.5

        peso_aspectos[p1] = peso_aspectos.get(p1, 0) + peso_orbe
        peso_aspectos[p2] = peso_aspectos.get(p2, 0) + peso_orbe

    puntos_repetidos = [
        {
            "punto": punto,
            "apariciones": apariciones,
            "peso_base": PESO_PUNTO.get(punto, 1),
            "puntuacion": apariciones * PESO_PUNTO.get(punto, 1),
        }
        for punto, apariciones in frecuencia_puntos.items()
        if apariciones >= 2
    ]

    puntos_repetidos.sort(
        key=lambda x: (
            -x["puntuacion"],
            -x["apariciones"],
            -x["peso_base"]
        )
    )

    # ─────────────────────────────────────────────────────────────
    # 2. CASAS MÁS IMPLICADAS EN FIGURAS
    # ─────────────────────────────────────────────────────────────

    frecuencia_casas = {}

    for figura in figuras:
        puntos_figura = puntos_participantes_figura(figura)

        for punto in puntos_figura:
            if punto not in planetas:
                continue

            casa = planetas[punto].get("casa")

            if not casa:
                continue

            frecuencia_casas[casa] = frecuencia_casas.get(casa, 0) + 1

    casas_dominantes = [
        {
            "casa": casa,
            "apariciones": apariciones,
        }
        for casa, apariciones in frecuencia_casas.items()
    ]

    casas_dominantes.sort(
        key=lambda x: (-x["apariciones"], x["casa"])
    )

    # ─────────────────────────────────────────────────────────────
    # 3. FIGURAS QUE SE SOLAPAN
    # ─────────────────────────────────────────────────────────────

    solapamientos = []

    for i in range(len(figuras)):
        for j in range(i + 1, len(figuras)):

            figura_a = figuras[i]
            figura_b = figuras[j]

            puntos_a = set(puntos_participantes_figura(figura_a))
            puntos_b = set(puntos_participantes_figura(figura_b))

            comunes = puntos_a.intersection(puntos_b)

            # Compartir un único planeta no significa necesariamente
            # que las dos figuras formen un mismo núcleo estructural.
            if len(comunes) < 2:
                continue

            union = puntos_a.union(puntos_b)

            porcentaje_a = (
                len(comunes) / len(puntos_a)
                if puntos_a else 0
            )

            porcentaje_b = (
                len(comunes) / len(puntos_b)
                if puntos_b else 0
            )

            solapamientos.append({
                "figura_1": figura_a.get("tipo", ""),
                "figura_2": figura_b.get("tipo", ""),
                "puntos_figura_1": ordenar_puntos(list(puntos_a)),
                "puntos_figura_2": ordenar_puntos(list(puntos_b)),
                "puntos_comunes": ordenar_puntos(list(comunes)),
                "puntos_totales": ordenar_puntos(list(union)),
                "porcentaje_figura_1": round(porcentaje_a, 2),
                "porcentaje_figura_2": round(porcentaje_b, 2),
            })

    solapamientos.sort(
        key=lambda x: -len(x["puntos_comunes"])
    )

    # ─────────────────────────────────────────────────────────────
    # 4. PUNTOS ESTRUCTURALES PRINCIPALES
    # ─────────────────────────────────────────────────────────────

    puntos_estructurales = []

    todos_puntos_arquitectura = set(frecuencia_puntos) | set(frecuencia_aspectos)

    for punto in todos_puntos_arquitectura:

        apariciones = frecuencia_puntos.get(punto, 0)
        aspectos_totales = frecuencia_aspectos.get(punto, 0)
        puntuacion_aspectos = peso_aspectos.get(punto, 0)

        peso = PESO_PUNTO.get(punto, 1)

        en_principales = sum(
            1
            for figura in principales
            if punto in puntos_participantes_figura(figura)
        )

        en_secundarias = sum(
            1
            for figura in secundarias
            if punto in puntos_participantes_figura(figura)
        )

        en_derivadas = sum(
            1
            for figura in derivadas
            if punto in puntos_participantes_figura(figura)
        )

        puntuacion_figuras = (
            peso
            + apariciones
            + en_principales * 4
            + en_secundarias * 2
            + en_derivadas
        )

        puntuacion = puntuacion_figuras + puntuacion_aspectos

        puntos_estructurales.append({
            "punto": punto,
            "apariciones": apariciones,
            "aspectos": aspectos_totales,
            "peso_aspectos": round(puntuacion_aspectos, 2),
            "figuras_principales": en_principales,
            "figuras_secundarias": en_secundarias,
            "figuras_derivadas": en_derivadas,
            "peso_base": peso,
            "puntuacion_figuras": puntuacion_figuras,
            "puntuacion": round(puntuacion, 2),
        })

    # ─────────────────────────────────────────────────────────────
    # 5. PUNTOS ORGANIZADORES GLOBALES
    # ─────────────────────────────────────────────────────────────

    puntos_organizadores = detectar_puntos_organizadores(
        puntos_estructurales,
        familias_nucleos
    )

    puntos_organizadores = clasificar_puntos_organizadores(
        puntos_organizadores
    )

    # ─────────────────────────────────────────────────────────────
    # 6. RESUMEN ESTRUCTURAL PARA IA
    # ─────────────────────────────────────────────────────────────

    resumen_estructural = construir_resumen_estructural(
        figuras,
        puntos_organizadores,
        casas_estructurales,
        ejes_casas,
        nucleos_compartidos,
        familias_nucleos,
    )

    # ─────────────────────────────────────────────────────────────
    # 7. SALIDA ESTRUCTURADA
    # ─────────────────────────────────────────────────────────────

    return {
        "figuras_principales": principales,
        "figuras_secundarias": secundarias,
        "figuras_derivadas": derivadas,

        "frecuencia_puntos": frecuencia_puntos,
        "puntos_repetidos": puntos_repetidos,

        "frecuencia_casas": frecuencia_casas,
        "casas_dominantes": casas_dominantes,
        "casas_estructurales": casas_estructurales,
	"ejes_casas": ejes_casas,

        "solapamientos": solapamientos,

        "puntos_estructurales": puntos_estructurales,
        "nucleos_compartidos": nucleos_compartidos,
        "familias_nucleos": familias_nucleos,
	"puntos_organizadores": puntos_organizadores,

	"resumen_estructural": resumen_estructural,
    }


def texto_dinamica_central(carta, figuras):
    principales, secundarias, derivadas = clasificar_figuras(figuras)

    partes = []

    partes.append(
        "La carta no se organiza como una suma de figuras independientes. "
        "Hay configuraciones que funcionan como núcleo y otras que actúan como derivaciones, apoyos o zonas de ajuste."
    )

    if principales:
        nombres = "; ".join(
            f"{f['tipo']} con {nombres_humanos(f.get('puntos', []))}"
            for f in principales[:3]
        )

        partes.append(
            f"Las configuraciones principales son: {nombres}. "
            "No se ordenan solo por cantidad de puntos o peso numérico, sino por la fuerza estructural que tienen dentro de la carta. "
            "Una figura con Sol, Plutón, Luna, Ascendente o Medio Cielo puede ser central aunque tenga menos puntos implicados, porque toca lugares que organizan identidad, dirección, cuerpo, intensidad o destino vital."
        )

    hay_stellium = any(f.get("tipo") == "Stellium" for f in figuras)

    if hay_stellium:
        st = next(f for f in figuras if f.get("tipo") == "Stellium")
        partes.append(
            f"El stellium formado por {nombres_humanos(st.get('puntos', []))} no debería leerse como una figura secundaria. "
            "Funciona como un núcleo de concentración desde el que se activan varias configuraciones. "
            "Por eso muchas figuras del documento no son procesos separados, sino distintas expresiones de ese mismo bloque interno."
        )

    if any(f.get("tipo") == "Cometa" for f in principales):
        partes.append(
            "La presencia de cometas indica que la carta no solo busca sostén: también necesita dirección. "
            "Hay recursos internos disponibles, pero la tensión de la oposición empuja a darles forma concreta."
        )

    if any(f.get("tipo") == "T-cuadrada" for f in principales):
        partes.append(
            "La T-cuadrada principal muestra una presión que no puede resolverse solo desde comprensión mental. "
            "Necesita una forma de integración práctica: reconocer los dos polos, sostener la tensión y no descargarla siempre en el mismo punto."
        )

    partes.append(
        "Por eso, la lectura más importante no es cuántas figuras aparecen, sino qué estructura se repite: "
        "un núcleo concentrado, varios canales de sostén y una tensión que pide dirección consciente."
    )

    return "\n\n".join(partes)

def jerarquizar_aspecto_independiente(aspecto):
    """
    Calcula la importancia de un aspecto natal independiente.

    La puntuación combina:
    - importancia natal de los dos puntos implicados;
    - exactitud del aspecto.

    No se utiliza el tipo de aspecto para decidir su importancia:
    una cuadratura no es estructuralmente más importante que un
    trígono solo por ser cuadratura.
    """

    p1 = aspecto.get("p1")
    p2 = aspecto.get("p2")
    orbe = aspecto.get("orbe", 99)

    peso_puntos = (
        PESO_PUNTO.get(p1, 1)
        + PESO_PUNTO.get(p2, 1)
    )

    # Peso por exactitud
    if orbe <= 1:
        peso_orbe = 6
    elif orbe <= 2:
        peso_orbe = 5
    elif orbe <= 3:
        peso_orbe = 4
    elif orbe <= 4:
        peso_orbe = 3
    elif orbe <= 5:
        peso_orbe = 2
    elif orbe <= 6:
        peso_orbe = 1
    elif orbe <= 7:
        peso_orbe = 0
    elif orbe <= 8:
        peso_orbe = -1
    else:
        peso_orbe = -2

    puntuacion = peso_puntos + peso_orbe

    if puntuacion >= 11:
        jerarquia = "principal"
    elif puntuacion >= 8:
        jerarquia = "relevante"
    else:
        jerarquia = "secundario"

    return {
        "puntuacion": puntuacion,
        "jerarquia": jerarquia,
        "peso_puntos": peso_puntos,
        "peso_orbe": peso_orbe,
    }




# ─── HUBER FASE 9: TRANSPORTE DEL PAQUETE IA AL CONTEXTO ─────────────────────
HUBER_FASE9_CONTEXT_TRANSPORT_APLICADO = True


def _buscar_figura_original_para_resumen(
    arquitectura,
    figura_resumen,
):
    tipo = figura_resumen.get("tipo", "")
    puntos = set(figura_resumen.get("puntos", []) or [])

    candidatas = (
        arquitectura.get("figuras_principales", [])
        + arquitectura.get("figuras_secundarias", [])
        + arquitectura.get("figuras_derivadas", [])
    )

    for figura in candidatas:
        if figura.get("tipo") != tipo:
            continue

        if set(puntos_reales_figura(figura)) == puntos:
            return figura

    return None


def _inyectar_paquetes_huber_en_resumen(
    arquitectura,
    resumen,
    carta=None,
):
    figuras_resumen = resumen.get("figuras", [])
    figuras_estructurales = []

    for clave in (
        "figuras_principales",
        "figuras_secundarias",
        "figuras_derivadas",
    ):
        for figura in arquitectura.get(clave, []):
            if figura not in figuras_estructurales:
                figuras_estructurales.append(figura)

    for figura_resumen in figuras_resumen:
        original = _buscar_figura_original_para_resumen(
            arquitectura,
            figura_resumen,
        )

        if original is None:
            figura_resumen["paquete_huber_ia"] = None
            continue

        figura_resumen["paquete_huber_ia"] = (
            construir_paquete_interpretacion_huber(
                original,
                figuras_estructurales=figuras_estructurales,
                carta=carta,
            )
        )

    return resumen

# ─── FIN HUBER FASE 9 ─────────────────────────────────────────────────────────


def preparar_datos_para_ia(carta, aspectos, arquitectura):
    """
    Prepara un paquete estructurado y compacto para la IA.

    Incluye:
    - posiciones esenciales de la carta natal;
    - arquitectura estructural ya filtrada;
    - aspectos relevantes de las figuras seleccionadas.

    No interpreta.
    Solo organiza la información que necesitará la IA.
    """

    planetas = carta["planetas"]



    # ─────────────────────────────────────────────────────────────
    # 1. POSICIONES ESENCIALES
    # ─────────────────────────────────────────────────────────────

    posiciones = {}

    for nombre, datos in planetas.items():

        posiciones[nombre] = {
            "signo": datos.get("signo"),
            "grado": round(datos.get("grado", 0), 2),
            "casa": datos.get("casa"),
            "retrogrado": datos.get("retrogrado", False),
        }

    # ─────────────────────────────────────────────────────────────
    # 2. ARQUITECTURA YA FILTRADA
    # ─────────────────────────────────────────────────────────────

    resumen = arquitectura.get(
        "resumen_estructural",
        {}
    )


    resumen = _inyectar_paquetes_huber_en_resumen(
        arquitectura,
        resumen,
        carta=carta,
    )

    # ─────────────────────────────────────────────────────────────
    # 3. ASPECTOS NECESARIOS PARA LAS FIGURAS SELECCIONADAS
    # ─────────────────────────────────────────────────────────────

    aspectos_relevantes = []

    for figura_resumen in resumen.get("figuras", []):

        tipo_figura = figura_resumen.get("tipo", "")
        puntos_figura = set(
            figura_resumen.get(
                "puntos_geometricos",
                figura_resumen.get("puntos", []),
            )
        )

        # Localizamos la figura completa original
        # para recuperar los aspectos que realmente la forman.
        figura_original = None

        for figura in arquitectura.get(
            "figuras_principales", []
        ) + arquitectura.get(
            "figuras_secundarias", []
        ) + arquitectura.get(
            "figuras_derivadas", []
        ):

            if figura.get("tipo") != tipo_figura:
                continue

            if set(puntos_reales_figura(figura)) == puntos_figura:
                figura_original = figura
                break

        if not figura_original:
            continue

        for aspecto in figura_original.get("aspectos", []):

            p1 = aspecto.get("p1")
            p2 = aspecto.get("p2")
            simbolo = aspecto.get("simbolo")

            clave = tuple(
                sorted([p1, p2])
            ) + (simbolo,)

            # Evitar duplicar un mismo aspecto
            # cuando participa en varias figuras.
            nombre_aspecto = {
                "=": "Conjunción",
                "⚺": "Semisextil",
                "✶": "Sextil",
                "□": "Cuadratura",
                "△": "Trígono",
                "⚻": "Quincuncio",
                "☍": "Oposición",
            }.get(simbolo, "Aspecto")

            # Si el aspecto ya apareció en otra figura,
            # añadimos la nueva figura a su lista.
            existente = next(
                (
                    a
                    for a in aspectos_relevantes
                    if a["clave"] == clave
                ),
                None
            )

            if existente:

                if tipo_figura not in existente["figuras"]:
                    existente["figuras"].append(tipo_figura)

                continue

            aspectos_relevantes.append({
                "clave": clave,
                "p1": p1,
                "p2": p2,
                "tipo": nombre_aspecto,
                "simbolo": simbolo,
                "orbe": aspecto.get("orbe"),
                "direccion": aspecto.get("direccion"),
                "desde": aspecto.get("desde", []),
                "bidireccional": aspecto.get("bidireccional"),
                "figuras": [tipo_figura],
                "origen": "figura",
            })

    # ─────────────────────────────────────────────────────────────
    # 3B. ASPECTOS INDEPENDIENTES
    # ─────────────────────────────────────────────────────────────
    #
    # Hasta aquí se han recogido únicamente los aspectos que
    # construyen las figuras seleccionadas.
    #
    # Añadimos ahora los demás aspectos natales válidos para que
    # no desaparezcan de la lectura de la arquitectura.
    #
    # Un aspecto que ya pertenece a una figura NO se duplica.
    # Simplemente conserva las figuras en las que participa.

    for aspecto in aspectos:

        p1 = aspecto.get("p1")
        p2 = aspecto.get("p2")
        simbolo = aspecto.get("simbolo")

        if not p1 or not p2 or not simbolo:
            continue

        # Los semisextiles aislados no se incorporan a la
        # interpretación. Si forman parte de una figura ya
        # habrán sido añadidos en el bloque anterior.
        if simbolo == "⚺":
            continue

        # La oposición Nodo Norte - Nodo Sur es automática
        # por definición y no aporta información independiente.
        if {p1, p2} == {"Nodo Norte", "Nodo Sur"}:
            continue

        clave = tuple(
            sorted([p1, p2])
        ) + (simbolo,)

        # Si ya está porque forma parte de una figura,
        # no lo volvemos a añadir.
        existente = next(
            (
                a
                for a in aspectos_relevantes
                if a["clave"] == clave
            ),
            None
        )

        if existente:
            continue

        nombre_aspecto = {
            "=": "Conjunción",
            "⚺": "Semisextil",
            "✶": "Sextil",
            "□": "Cuadratura",
            "△": "Trígono",
            "⚻": "Quincuncio",
            "☍": "Oposición",
        }.get(simbolo, "Aspecto")

        datos_jerarquia = jerarquizar_aspecto_independiente(
            aspecto
        )

        aspectos_relevantes.append({
            "clave": clave,
            "p1": p1,
            "p2": p2,
            "tipo": nombre_aspecto,
            "simbolo": simbolo,
            "orbe": aspecto.get("orbe"),
            "direccion": aspecto.get("direccion"),
            "desde": aspecto.get("desde", []),
            "bidireccional": aspecto.get("bidireccional"),
            "figuras": [],
            "origen": "independiente",
            "puntuacion": datos_jerarquia["puntuacion"],
            "jerarquia": datos_jerarquia["jerarquia"],
            "peso_puntos": datos_jerarquia["peso_puntos"],
            "peso_orbe": datos_jerarquia["peso_orbe"],
        })

    # ─────────────────────────────────────────────────────────────
    # 3C. AGRUPACIÓN DE ASPECTOS AL EJE NODAL
    # ─────────────────────────────────────────────────────────────
    #
    # Cuando un mismo punto aspecta simultáneamente a Nodo Norte
    # y Nodo Sur, ambas relaciones describen una única implicación
    # con el eje nodal.
    #
    # Conservamos los dos aspectos originales dentro de "componentes",
    # pero enviamos a la IA una sola relación estructural.

    independientes = [
        a for a in aspectos_relevantes
        if a.get("origen") == "independiente"
    ]

    grupos_nodales = {}

    for aspecto in independientes:

        p1 = aspecto.get("p1")
        p2 = aspecto.get("p2")

        if p1 in ("Nodo Norte", "Nodo Sur"):
            otro = p2
            nodo = p1

        elif p2 in ("Nodo Norte", "Nodo Sur"):
            otro = p1
            nodo = p2

        else:
            continue

        grupos_nodales.setdefault(
            otro,
            {}
        )[nodo] = aspecto

    for punto, grupo in grupos_nodales.items():

        if (
            "Nodo Norte" not in grupo
            or "Nodo Sur" not in grupo
        ):
            continue

        aspecto_norte = grupo["Nodo Norte"]
        aspecto_sur = grupo["Nodo Sur"]

        # Eliminamos las dos entradas independientes originales.
        aspectos_relevantes = [
            a
            for a in aspectos_relevantes
            if a is not aspecto_norte
            and a is not aspecto_sur
        ]

        # La jerarquía del eje conserva la mayor puntuación
        # de sus dos componentes, no las suma.
        puntuacion = max(
            aspecto_norte.get("puntuacion", 0),
            aspecto_sur.get("puntuacion", 0),
        )

        if puntuacion >= 11:
            jerarquia = "principal"
        elif puntuacion >= 8:
            jerarquia = "relevante"
        else:
            jerarquia = "secundario"

        aspectos_relevantes.append({
            "clave": (
                punto,
                "Eje nodal",
                "eje_nodal",
            ),
            "p1": punto,
            "p2": "Eje nodal",
            "tipo": "Aspecto al eje nodal",
            "simbolo": "",
            "orbe": min(
                aspecto_norte.get("orbe", 99),
                aspecto_sur.get("orbe", 99),
            ),
            "figuras": [],
            "origen": "independiente",
            "puntuacion": puntuacion,
            "jerarquia": jerarquia,

            "peso_puntos": max(
                aspecto_norte.get("peso_puntos", 0),
                aspecto_sur.get("peso_puntos", 0),
            ),
            "peso_orbe": max(
                aspecto_norte.get("peso_orbe", 0),
                aspecto_sur.get("peso_orbe", 0),
            ),

            "componentes": [
                {
                    "nodo": "Nodo Norte",
                    "tipo": aspecto_norte.get("tipo"),
                    "simbolo": aspecto_norte.get("simbolo"),
                    "orbe": aspecto_norte.get("orbe"),
                },
                {
                    "nodo": "Nodo Sur",
                    "tipo": aspecto_sur.get("tipo"),
                    "simbolo": aspecto_sur.get("simbolo"),
                    "orbe": aspecto_sur.get("orbe"),
                },
            ],
        })


    # ─────────────────────────────────────────────────────────────
    # 4. LIMPIEZA FINAL
    # ─────────────────────────────────────────────────────────────

    for aspecto in aspectos_relevantes:
        aspecto.pop("clave", None)

    # ─────────────────────────────────────────────────────────────
    # 5. SALIDA PARA IA
    # ─────────────────────────────────────────────────────────────

    retrogrados = [
        nombre
        for nombre, datos in posiciones.items()
        if datos.get("retrogrado")
    ]

    # La retrogradación no aumenta por sí sola el peso estructural de un
    # planeta, pero sí modifica la forma de expresión de los puntos que ya
    # son relevantes. Dejamos esta información preparada de forma explícita
    # para que la capa interpretativa no la pierda.
    puntos_organizadores_resumen = {
        str(item.get("punto"))
        for item in (resumen.get("puntos_organizadores", []) or [])
        if item.get("punto")
    }

    participacion_figuras_retro = {}
    for figura in (resumen.get("figuras", []) or []):
        for punto in (figura.get("puntos", []) or []):
            if punto in retrogrados:
                participacion_figuras_retro[punto] = (
                    participacion_figuras_retro.get(punto, 0) + 1
                )

    retrogradacion_estructural = {
        "planetas_retrogrados": retrogrados,
        "organizadores_retrogrados": [
            punto
            for punto in retrogrados
            if punto in puntos_organizadores_resumen
        ],
        "participacion_en_figuras": participacion_figuras_retro,
        "regla": (
            "La retrogradación no crea ni elimina figuras ni aumenta por sí "
            "sola la jerarquía. Matiza la expresión de un punto ya relevante "
            "hacia mayor interiorización, revisión o reelaboración."
        ),
    }

    return {
        "posiciones_natales": posiciones,
        "retrogrados": retrogrados,
        "retrogradacion_estructural": retrogradacion_estructural,
        "arquitectura": resumen,
        "aspectos_relevantes": aspectos_relevantes,
    }

# ─── GENERACIÓN LATEX ─────────────────────────────────────────────────────────

def generar_latex_ai(carta, nombre, año, mes, dia, hora, minuto,
                     ciudad, lat, lon, tz_name, ruta_rueda, aspectos):

    planetas = carta["planetas"]
    asc = carta["asc"]
    mc = carta["mc"]

    ruta_rueda = os.path.basename(ruta_rueda).replace("\\", "/")

    fecha_str = f"{dia:02d}/{mes:02d}/{año}"
    hora_str = f"{hora:02d}:{minuto:02d}"

    tz_obj = pytz.timezone(tz_name)
    dt_local = tz_obj.localize(datetime(año, mes, dia, hora, minuto))
    utc_off = dt_local.strftime("%z")
    utc_str = f"UTC{utc_off[:3]}:{utc_off[3:]}"

    nom_esc = esc(nombre)
    ciu_esc = esc(ciudad)

    figuras = detectar_figuras(carta, aspectos)

    print()
    print("CLASIFICACIÓN DE FIGURAS:")

    for figura in figuras:

        categoria = clasificar_categoria_figura(figura)
        consistencia = clasificar_consistencia_figura(figura)

        puntos_reales = puntos_reales_figura(figura)

        nodal = (
            " — EJE NODAL"
            if figura.get("eje_nodal_implicado", False)
            else ""
        )

        print(
            f"  {figura['tipo']} — "
            f"{nombres_humanos(puntos_reales)} — "
            f"categoría: {categoria['categoria']} — "
            f"consistencia: {consistencia['consistencia']} — "
            f"jerarquía: {figura.get('jerarquia', '')} — "
            f"puntuación: {figura.get('puntuacion_jerarquia', '')} — "
            f"orbe medio: {consistencia['orbe_medio']} — "
            f"orbe máximo: {consistencia['orbe_maximo']}"
            f"{nodal}"
        )

    arquitectura = analizar_arquitectura_carta(
        carta,
        aspectos,
        figuras
    )

    datos_ia = preparar_datos_para_ia(
        carta,
        aspectos,
        arquitectura
    )

    print()
    print("PUNTOS ESTRUCTURALES:")

    for p in arquitectura["puntos_estructurales"][:10]:
        print(
            f"  {p['punto']}: "
            f"puntuación {p['puntuacion']} | "
            f"apariciones {p['apariciones']} | "
            f"principales {p['figuras_principales']}"
        )

    print()
    print("CASAS DOMINANTES:")

    for c in arquitectura["casas_dominantes"]:
        print(
            f"  Casa {c['casa']} "
            f"→ apariciones {c['apariciones']} "
        )

    print()
    print("CASAS ESTRUCTURALES:")

    for c in arquitectura["casas_estructurales"]:
        print(
            f"  Casa {c['casa']} "
            f"→ {c['jerarquia_casa']} "
            f"→ apariciones {c['apariciones']} "
            f"→ puntuación {c['puntuacion']}"
        )

    print()
    print("EJES DE CASAS:")

    for e in arquitectura["ejes_casas"]:
        print(
            f"  Eje {e['eje']} "
            f"→ {e['jerarquia_eje']} "
            f"→ apariciones {e['apariciones_total']} "
            f"→ puntuación {e['puntuacion_total']}"
        )

    print()
    print("SOLAPAMIENTOS:")

    for s in arquitectura["solapamientos"]:
        print(
            f"  {s['figura_1']} + {s['figura_2']} "
            f"→ comunes: {', '.join(s['puntos_comunes'])}"
        )

    intro = texto_intro_figuras(figuras)


    nucleos = detectar_nucleos_compartidos(figuras)

    print()
    print("NÚCLEOS COMPARTIDOS:")

    for n in nucleos:
        tipos = ", ".join(
            f["tipo"]
            for f in n["figuras"]
        )

        print(
            f"  {', '.join(n['puntos_nucleo'])} "
            f"→ {n['apariciones']} apariciones "
            f"→ puntuación {n['puntuacion_nucleo']} "
            f"→ {n['jerarquia_nucleo']} "
            f"→ {tipos}"
        )

    familias = detectar_familias_nucleos(nucleos)

    print()
    print("FAMILIAS DE NÚCLEOS:")

    for f in familias:

        relacionados = ", ".join(
            f["puntos_relacionados"]
        )

        print(
            f"  {f['punto_central']} "
            f"→ {f['numero_nucleos']} núcleos "
            f"→ puntuación total {f['puntuacion_total']} "
            f"→ {f['jerarquia_familia']} "
            f"→ relacionados con: {relacionados}"
        )

    print()
    print("PUNTOS ORGANIZADORES GLOBALES:")

    for p in arquitectura["puntos_organizadores"]:
        print(
            f"  {p['punto']} "
            f"→ {p['jerarquia_global']} "
            f"→ estructural {p['puntuacion_estructural']} "
            f"→ familia {p['puntuacion_familia']} "
            f"→ núcleos {p['numero_nucleos']} "
            f"→ global {p['puntuacion_global']}"
        )

    print()
    print("RESUMEN ESTRUCTURAL PARA IA:")

    resumen = arquitectura["resumen_estructural"]

    print()
    print("DATOS PREPARADOS PARA IA:")

    print()
    print("POSICIONES NATALES:")
    for nombre, datos in datos_ia["posiciones_natales"].items():
        print(
            f"  {nombre} "
            f"→ {datos['signo']} "
            f"→ grado {datos['grado']} "
            f"→ casa {datos['casa']} "
            f"→ R {datos['retrogrado']}"
        )

    print()
    print("ASPECTOS RELEVANTES:")
    for a in datos_ia["aspectos_relevantes"]:

        figuras_aspecto = ", ".join(
            a.get("figuras", [])
        )

        print(
            f"  {a['p1']} {a['simbolo']} {a['p2']} "
            f"→ {a['tipo']} "
            f"→ orbe {a['orbe']} "
            f"→ figuras: {figuras_aspecto}"
        )

    print()
    print("FIGURAS:")
    for f in resumen["figuras"]:
        print(
            f"  {f['tipo']} "
            f"→ {', '.join(f['puntos'])} "
            f"→ {f['categoria']} "
            f"→ {f['consistencia']} "
            f"→ {f['jerarquia']} "
            f"→ puntuación {f['puntuacion']}"
        )

    print()
    print("PUNTOS ORGANIZADORES:")
    for p in resumen["puntos_organizadores"]:
        print(
            f"  {p['punto']} "
            f"→ {p['jerarquia_global']} "
            f"→ global {p['puntuacion_global']}"
        )

    print()
    print("CASAS:")
    for c in resumen["casas"]:
        print(
            f"  Casa {c['casa']} "
            f"→ {c['jerarquia_casa']} "
            f"→ puntuación {c['puntuacion']}"
        )

    print()
    print("EJES:")
    for e in resumen["ejes_casas"]:
        print(
            f"  Eje {e['eje']} "
            f"→ {e['jerarquia_eje']} "
            f"→ puntuación {e['puntuacion_total']}"
        )

    print()
    print("NÚCLEOS:")
    for n in resumen["nucleos"]:
        print(
            f"  {', '.join(n['puntos_nucleo'])} "
            f"→ {n['jerarquia_nucleo']} "
            f"→ puntuación {n['puntuacion_nucleo']}"
        )

    print()
    print("FAMILIAS:")
    for f in resumen["familias"]:
        print(
            f"  {f['punto_central']} "
            f"→ {f['jerarquia_familia']} "
            f"→ puntuación {f['puntuacion_total']}"
        )

    # ── Tabla de puntos principales ──────────────────────────────────────────

    orden_tabla = [
        "Sol", "Luna", "Mercurio", "Venus", "Marte",
        "Júpiter", "Saturno", "Urano", "Neptuno", "Plutón",
        "Quirón", "Lilith", "Nodo Norte", "Nodo Sur",
        "Ascendente", "Medio Cielo"
    ]

    filas = []

    for nombre_p in orden_tabla:
        if nombre_p not in planetas:
            continue

        p = planetas[nombre_p]
        retro = "R" if p.get("retrogrado") else ""
        elem = ELEMENTO_SIGNO.get(p.get("signo", ""), "—")

        filas.append(
            f"  {esc(nombre_p)} & "
            f"{esc(p.get('signo',''))} & "
            f"{grado_a_dms(p.get('grado',0))} & "
            f"{p.get('casa','')} & "
            f"{esc(elem)} & "
            f"{esc(retro)} \\\\"
        )

    tabla = "\n".join(filas)

    # ── Resumen de figuras ──────────────────────────────────────────────────

    if figuras:
        filas_figuras = []
        for f in figuras:
            tipo = f.get("tipo", "")
            puntos = nombres_humanos(f.get("puntos", []))
            casas = descripcion_casas(casas_de_puntos(carta, f.get("puntos", [])))
            peso = f.get("peso", "")

            filas_figuras.append(
                f"  {esc(tipo)} & "
                f"{esc(puntos)} & "
                f"{esc(casas)} & "
                f"{peso} \\\\"
            )

        tabla_figuras = (
            "\\begin{center}\n"
            "\\begin{tabular}{p{3.2cm}p{7.2cm}p{2.8cm}r}\n"
            "  \\toprule\n"
            "  \\textbf{Figura} & \\textbf{Puntos implicados} & \\textbf{Casas} & \\textbf{Peso} \\\\\n"
            "  \\midrule\n"
            f"{chr(10).join(filas_figuras)}\n"
            "  \\bottomrule\n"
            "\\end{tabular}\n"
            "\\end{center}"
        )
    else:
        tabla_figuras = "\\textit{No se han detectado figuras mayores dentro de los orbes definidos.}"

    # ── Desarrollo de figuras ────────────────────────────────────────────────

    desarrollo_figuras = ""

    if figuras:
        principales, secundarias, derivadas = clasificar_figuras(figuras)

        desarrollo_figuras += (
            "\\subsection*{Dinámica central}\n"
            f"{esc(texto_dinamica_central(carta, figuras))}\n\n"
        )

        if principales:
            desarrollo_figuras += "\\subsection*{Configuraciones principales}\n\n"

            for figura in principales:
                titulo = figura.get("tipo", "Figura")
                puntos = nombres_humanos(figura.get("puntos", []))
                texto = texto_figura(carta, figura)

                desarrollo_figuras += (
                    "\\Needspace{10\\baselineskip}\n"
                    f"\\subsubsection*{{{esc(titulo)} — {esc(puntos)}}}\n"
                    f"{esc(texto)}\n\n"
                )

        if secundarias:
            desarrollo_figuras += "\\subsection*{Configuraciones de sostén y concentración}\n\n"

            for figura in secundarias:
                titulo = figura.get("tipo", "Figura")
                puntos = nombres_humanos(figura.get("puntos", []))
                texto = texto_figura(carta, figura)

                desarrollo_figuras += (
                    "\\Needspace{10\\baselineskip}\n"
                    f"\\subsubsection*{{{esc(titulo)} — {esc(puntos)}}}\n"
                    f"{esc(texto)}\n\n"
                )

        if derivadas:
            desarrollo_figuras += (
                "\\subsection*{Figuras de ajuste}\n"
                "Estas configuraciones no pesan tanto como estructura central, "
                "pero muestran zonas donde la carta necesita afinar respuestas, "
                "recolocar tensión o madurar patrones concretos.\n\n"
            )

            for figura in derivadas:
                titulo = figura.get("tipo", "Figura")
                puntos = nombres_humanos(figura.get("puntos", []))
                texto = texto_figura(carta, figura)

                desarrollo_figuras += (
                    "\\Needspace{8\\baselineskip}\n"
                    f"\\subsubsection*{{{esc(titulo)} — {esc(puntos)}}}\n"
                    f"{esc(texto)}\n\n"
                )

    else:
        desarrollo_figuras = (
            "No aparecen configuraciones mayores especialmente dominantes en esta carta."
        )

    latex = f"""\\documentclass[11pt,a4paper]{{article}}

\\usepackage[utf8]{{inputenc}}
\\usepackage[T1]{{fontenc}}
\\usepackage{{tgpagella}}
\\usepackage[spanish]{{babel}}
\\usepackage{{geometry}}
\\usepackage{{graphicx}}
\\usepackage{{booktabs}}
\\usepackage{{array}}
\\usepackage{{xcolor}}
\\usepackage{{titlesec}}
\\usepackage{{fancyhdr}}
\\usepackage[parfill]{{parskip}}
\\usepackage[expansion=false]{{microtype}}
\\usepackage{{hyperref}}
\\usepackage{{setspace}}
\\usepackage{{needspace}}

\\widowpenalty=10000
\\clubpenalty=10000
\\displaywidowpenalty=10000

\\geometry{{top=3.0cm,bottom=3.0cm,left=3.5cm,right=3.5cm}}
\\setlength{{\\parskip}}{{0.65em}}
\\setlength{{\\parindent}}{{0em}}

\\definecolor{{azulai}}{{RGB}}{{30,80,140}}
\\definecolor{{doradoai}}{{RGB}}{{140,90,0}}
\\definecolor{{grisai}}{{RGB}}{{70,70,70}}

\\titleformat{{\\section}}{{\\Large\\bfseries\\color{{azulai}}}}{{}}{{0em}}{{}}[{{\\color{{azulai}}\\titlerule[0.5pt]\\nopagebreak[4]}}]
\\titlespacing*{{\\section}}{{0pt}}{{1.8em}}{{0.8em}}

\\titleformat{{\\subsection}}{{\\large\\bfseries\\color{{doradoai}}}}{{}}{{0em}}{{}}[{{\\nopagebreak[4]}}]
\\titlespacing*{{\\subsection}}{{0pt}}{{1.4em}}{{0.5em}}

\\titleformat{{\\subsubsection}}{{\\normalsize\\bfseries\\color{{grisai}}}}{{}}{{0em}}{{}}[{{\\nopagebreak[4]}}]
\\titlespacing*{{\\subsubsection}}{{0pt}}{{1.0em}}{{0.3em}}

\\pagestyle{{fancy}}\\fancyhf{{}}
\\rhead{{\\textcolor{{grisai}}{{\\small {nom_esc} — Arquitectura Interna}}}}
\\lhead{{\\textcolor{{grisai}}{{\\small Figuras y configuraciones}}}}
\\cfoot{{\\textcolor{{grisai}}{{\\small\\thepage}}}}
\\renewcommand{{\\headrulewidth}}{{0.3pt}}

\\hypersetup{{colorlinks=true,linkcolor=azulai,urlcolor=azulai}}
\\setstretch{{1.35}}
\\tolerance=1500
\\emergencystretch=4em

\\begin{{document}}

\\begin{{titlepage}}
  \\centering
  \\vspace*{{1.5cm}}

  {{\\Huge\\bfseries\\color{{azulai}} Figuras y configuraciones}}\\\\[0.5cm]
  {{\\large\\color{{grisai}} Arquitectura Interna}}\\\\[0.3cm]
  {{\\small\\itshape\\color{{grisai}} Arquitectura profunda de la carta natal}}\\\\[2cm]

  {{\\huge\\color{{doradoai}} {nom_esc}}}\\\\[1.5cm]

  {{\\Large {fecha_str} \\quad {hora_str}}}\\\\[0.3cm]
  {{\\Large {ciu_esc}}}\\\\[0.3cm]

  {{\\normalsize Lat: {lat:.4f}° \\quad Lon: {lon:.4f}° \\quad {utc_str}}}\\\\[0.3cm]

  {{\\normalsize Ascendente: {esc(asc['signo'])} {grado_a_dms(asc['grado'])} \\quad
    MC: {esc(mc['signo'])} {grado_a_dms(mc['grado'])}}}\\\\[2cm]

  \\vfill
  {{\\small Generado el {datetime.now().strftime("%d/%m/%Y")}}}
\\end{{titlepage}}

\\tableofcontents
\\newpage

\\section{{Rueda natal}}

\\begin{{figure}}[h!]
  \\centering
  \\includegraphics[width=0.90\\textwidth]{{{ruta_rueda}}}
  \\caption{{Carta natal de {nom_esc} — {fecha_str} {hora_str} — {ciu_esc}}}
\\end{{figure}}

\\newpage

\\section{{Puntos de referencia}}

\\begin{{center}}
\\begin{{tabular}}{{llrrll}}
  \\toprule
  \\textbf{{Punto}} & \\textbf{{Signo}} & \\textbf{{Grado}} & \\textbf{{Casa}} &
  \\textbf{{Elemento}} & \\textbf{{R}} \\\\
  \\midrule
{tabla}
  \\bottomrule
\\end{{tabular}}
\\end{{center}}

\\newpage

\\section{{Figuras detectadas}}

{tabla_figuras}

\\vspace{{0.8cm}}

{esc(intro)}

\\newpage

\\section{{Interpretación de las configuraciones}}

{desarrollo_figuras}

\\Needspace{{10\\baselineskip}}
\\section{{Integración}}

\\vspace{{1cm}}

\\begin{{center}}
{{\\small\\itshape\\color{{grisai}}
La astrología se usa aquí como lenguaje simbólico de observación, no como una definición cerrada de la persona.\\\\
Este documento muestra patrones de organización interna, no un destino fijo.
}}
\\end{{center}}

\\end{{document}}
"""

    return latex


def generar_carta_api(
    nombre,
    fecha,
    hora,
    lugar,
    lat=None,
    lon=None,
    tz_name=None,
):
    print(
        "Generando informe Figuras y configuraciones para:",
        nombre,
    )

    try:
        # ── FECHA ─────────────────────────────────────────

        dia, mes, año = map(
            int,
            fecha.split("/")
        )

        # ── HORA ──────────────────────────────────────────

        partes_hora = hora.split(":")

        hora_num = int(
            partes_hora[0]
        )

        minuto = int(
            partes_hora[1]
        )

        # ── GEOLOCALIZACIÓN ───────────────────────────────

        if lat is not None and lon is not None:

            lat = float(lat)
            lon = float(lon)

            if not tz_name:
                tz_name = obtener_timezone(
                    lat,
                    lon
                )

        else:

            lat, lon = geocodificar(
                lugar
            )

            tz_name = obtener_timezone(
                lat,
                lon
            )

        # ── CARTA ─────────────────────────────────────────

        carta = calcular_carta(
            año,
            mes,
            dia,
            hora_num,
            minuto,
            lat,
            lon,
            tz_name,
        )

        # ── ASPECTOS Y FIGURAS ────────────────────────────

        aspectos = calcular_aspectos_figuras(
            carta["planetas"]
        )

        figuras = detectar_figuras(
            carta,
            aspectos
        )

        arquitectura = analizar_arquitectura_carta(
            carta,
            aspectos,
            figuras
        )

        contenido_ia = preparar_datos_para_ia(
            carta,
            aspectos,
            arquitectura
        )

        # ── ARCHIVOS ──────────────────────────────────────

        nombre_f = (
            nombre
            .replace(" ", "_")
            .replace("/", "-")
            .replace("\\", "-")
        )

        ruta_base = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            nombre_f + "_Figuras_Configuraciones",
        )

        ruta_png = ruta_base + "_rueda.png"
        ruta_tex = ruta_base + ".tex"
        ruta_pdf = ruta_base + ".pdf"

        dibujar_rueda(
            carta,
            nombre,
            ruta_png
        )

        latex = generar_latex_ai(
            carta,
            nombre,
            año,
            mes,
            dia,
            hora_num,
            minuto,
            lugar,
            lat,
            lon,
            tz_name,
            ruta_png,
            aspectos
        )

        with open(
            ruta_tex,
            "w",
            encoding="utf-8"
        ) as f:
            f.write(
                latex
            )

        tex_nombre = os.path.basename(
            ruta_tex
        )

        for _ in range(2):
            subprocess.run(
                [
                    "pdflatex",
                    "-interaction=nonstopmode",
                    tex_nombre,
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=180,
                cwd=os.path.dirname(
                    os.path.abspath(__file__)
                )
            )

        if not os.path.exists(
            ruta_pdf
        ):
            return {
                "ok": False,
                "error": "No se ha podido crear el PDF.",
            }

        nombre_archivo = os.path.basename(
            ruta_pdf
        )

        return {
            "ok": True,
            "pdf": f"/descargas/{nombre_archivo}",
            "pdf_url": f"/descargas/{nombre_archivo}",
            "contenido_ia": contenido_ia,
        }

    except Exception as error:
        print(
            "Error generando Figuras:",
            error,
        )

        return {
            "ok": False,
            "error": str(error),
        }

    finally:
        plt.close("all")


# ─── PROGRAMA PRINCIPAL ───────────────────────────────────────────────────────

def main():
    print("=" * 68)
    print("   FIGURAS Y CONFIGURACIONES — Arquitectura Interna")
    print("=" * 68)
    print()

    nombre = input("Nombre completo: ").strip()
    if not nombre:
        print("El nombre no puede estar vacío.")
        sys.exit(1)

    while True:
        try:
            fecha_str = input("Fecha de nacimiento (DD/MM/AAAA): ").strip()
            dia, mes, año = map(int, fecha_str.split("/"))
            datetime(año, mes, dia)
            break
        except Exception:
            print("Formato incorrecto. Usa DD/MM/AAAA")

    while True:
        try:
            hora = int(input("Hora de nacimiento (0-23): ").strip())
            if 0 <= hora <= 23:
                break
            print("Valor entre 0 y 23.")
        except ValueError:
            print("Introduce un número entero.")

    while True:
        try:
            minuto = int(input("Minuto de nacimiento (0-59): ").strip())
            if 0 <= minuto <= 59:
                break
            print("Valor entre 0 y 59.")
        except ValueError:
            print("Introduce un número entero.")

    ciudad = input("Lugar de nacimiento (ciudad, país): ").strip()
    if not ciudad:
        print("El lugar no puede estar vacío.")
        sys.exit(1)

    print()
    print("Calculando carta natal...")

    try:
        lat, lon = geocodificar(ciudad)
        print(f"  Coordenadas: {lat:.4f}, {lon:.4f}")
    except Exception as e:
        print(f"Error de geocodificación: {e}")
        sys.exit(1)

    try:
        tz_name = obtener_timezone(lat, lon)
        print(f"  Zona horaria: {tz_name}")
    except Exception as e:
        print(f"Error de zona horaria: {e}")
        sys.exit(1)

    try:
        carta = calcular_carta(año, mes, dia, hora, minuto, lat, lon, tz_name)
        print(f"  Ascendente:  {carta['asc']['signo']} {grado_a_dms(carta['asc']['grado'])}")
        print(f"  Medio Cielo: {carta['mc']['signo']} {grado_a_dms(carta['mc']['grado'])}")
    except Exception as e:
        print(f"Error en cálculo astrológico: {e}")
        sys.exit(1)

    aspectos = calcular_aspectos_figuras(carta["planetas"])
    figuras = detectar_figuras(carta, aspectos)

    print(f"  Aspectos calculados: {len(aspectos)}")
    print(f"  Figuras detectadas: {len(figuras)}")

    if figuras:
        for f in figuras:
            print(f"   - {f['tipo']}: {nombres_humanos(f.get('puntos', []))}")

    nombre_f = nombre.replace(" ", "_").replace("/", "-")
    dir_sal = os.path.dirname(os.path.abspath(__file__))

    ruta_base = os.path.join(dir_sal, nombre_f + "_Figuras_Configuraciones")
    ruta_png = ruta_base + "_rueda.png"
    ruta_tex = ruta_base + ".tex"
    ruta_pdf = ruta_base + ".pdf"

    print("  Dibujando rueda astrológica...")

    try:
        dibujar_rueda(carta, nombre, ruta_png)
        print(f"  Rueda guardada: {ruta_png}")
    except Exception as e:
        print(f"Error al dibujar la rueda: {e}")
        sys.exit(1)

    print("  Generando documento de figuras...")

    latex = generar_latex_ai(
        carta,
        nombre,
        año,
        mes,
        dia,
        hora,
        minuto,
        ciudad,
        lat,
        lon,
        tz_name,
        ruta_png,
        aspectos
    )

    with open(ruta_tex, "w", encoding="utf-8") as f:
        f.write(latex)

    print(f"  LaTeX guardado: {ruta_tex}")

    print("  Compilando PDF...")

    try:
        tex_nombre = os.path.basename(ruta_tex)

        for _ in range(2):
            resultado = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", tex_nombre],
                capture_output=True,
                text=True,
                timeout=180,
                cwd=dir_sal
            )

        if os.path.exists(ruta_pdf):
            print(f"  PDF generado: {ruta_pdf}")
        else:
            print("  Error: no se generó el PDF.")

            log_path = ruta_base + ".log"
            if os.path.exists(log_path):
                print(f"  Revisa el log en: {log_path}")

                with open(log_path, encoding="latin-1", errors="replace") as f:
                    lineas = f.readlines()

                errores = [
                    l for l in lineas
                    if l.startswith("!") or "Error" in l
                ]

                if errores:
                    print("  Errores encontrados:")
                    for e in errores[:10]:
                        print("   ", e.rstrip())

            else:
                print("  Salida de pdflatex:")
                print(resultado.stdout[-2000:] if resultado.stdout else "(vacía)")

    except subprocess.TimeoutExpired:
        print("  Timeout al compilar LaTeX.")

    except FileNotFoundError:
        print("  pdflatex no encontrado. El archivo .tex está listo para compilar.")

    for ext in [".aux", ".toc", ".out"]:
        try:
            os.remove(ruta_base + ext)
        except FileNotFoundError:
            pass

    if os.path.exists(ruta_pdf):
        try:
            os.remove(ruta_base + ".log")
        except FileNotFoundError:
            pass

    print()
    print("=" * 68)
    print(f"  Figuras y configuraciones de {nombre} generadas.")
    print(f"  Ficheros en: {dir_sal}")
    print(f"    - {nombre_f}_Figuras_Configuraciones_rueda.png")
    print(f"    - {nombre_f}_Figuras_Configuraciones.pdf")
    print("=" * 68)


if __name__ == "__main__":
    main()
