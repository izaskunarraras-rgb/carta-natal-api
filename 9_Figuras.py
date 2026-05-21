#!/usr/bin/env python3
"""
9. Figuras y configuraciones — Arquitectura Interna

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

import sys, os, math, subprocess
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
    0:   ("Conjunción", "=", 8),
    60:  ("Sextil", "✶", 6),
    90:  ("Cuadratura", "□", 7),
    120: ("Trígono", "△", 8),
    150: ("Quincuncio", "⚻", 4),
    180: ("Oposición", "☍", 8),
}

ORBES_EJES = {
    "=": 5,
    "☍": 5,
    "□": 4,
    "△": 4,
    "✶": 3,
}

TIPOS_FIGURA = [
    "T-cuadrada",
    "Gran trígono",
    "Cometa",
    "Yod",
    "Stellium",
    "Triángulo de aprendizaje",
]



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
                orbe_real = orbe_base

                if n1 in ("Ascendente", "Medio Cielo") or n2 in ("Ascendente", "Medio Cielo"):
                    orbe_real = ORBES_EJES.get(simbolo_asp, orbe_base)

                    if (
                        simbolo_asp == "☍"
                        and (n1 in ("Sol", "Luna", "Júpiter") or n2 in ("Sol", "Luna", "Júpiter"))
                    ):
                        orbe_real = 8

                elif (
                    simbolo_asp == "△"
                    and (n1 in ("Sol", "Luna") or n2 in ("Sol", "Luna"))
                ):
                    orbe_real = 9

                elif (
                    simbolo_asp == "="
                    and (
                        n1 in ("Mercurio", "Venus", "Marte", "Nodo Sur")
                        and n2 in ("Mercurio", "Venus", "Marte", "Nodo Sur")
                    )
                ):
                    orbe_real = 12


                elif (
                    simbolo_asp in ("=", "☍")
                    and (n1 in ("Sol", "Luna") or n2 in ("Sol", "Luna"))
                ):
                    orbe_real = 10


                orbe_val = round(abs(diff - angulo), 2)

                if orbe_val <= orbe_real:
                    aspectos.append({
                        "p1": n1,
                        "p2": n2,
                        "nombre": nombre_asp,
                        "simbolo": simbolo_asp,
                        "orbe": orbe_val,
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
        ang_num = lon_a_angulo(cusp + 4.0)   # 4° después de la cúspide
        r_num = (R_CASA_IN + 0.25) / 2 + 0.12
        ax.text(math.cos(ang_num)*r_num, math.sin(ang_num)*r_num, str(i+1),
                ha='center', va='center', fontsize=7, color='#444', zorder=4)

    # ── Líneas de aspecto ────────────────────────────────────────────────────
    _ASP_COLORES = {
        "□":"#CC2200",
        "☍":"#CC2200",
        "△":"#1A5FA8",
        "✶":"#1A5FA8",
        "⚻":"#2E7D32",
        "=":"#7B2D8B"
    }

    _ASP_LW = {
        "□":1.0,
        "☍":1.0,
        "△":0.9,
        "✶":0.8,
        "⚻":0.7,
        "=":1.2
    }

    _ASP_ALPHA = {
        "□":0.55,
        "☍":0.55,
        "△":0.50,
        "✶":0.45,
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

        p = carta["planetas"][nombre]
        ang = lon_a_angulo(p["lon"])
        r = radios[nombre]
        color = COLORES_PLANETA.get(nombre, "#333")
        simbolo = p["simbolo"] + ("ᴿ" if p.get("retrogrado") else "")

        ax.text(
            math.cos(ang)*r,
            math.sin(ang)*r,
            simbolo,
            ha="center",
            va="center",
            fontsize=17,
            color=color,
            fontweight="bold",
            zorder=6
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

    ORBE_STELLIUM_ENTRE_PUNTOS = 12.0

    puntos_ordenados = sorted(
        puntos,
        key=lambda p: planetas[p]["lon"]
    )

    grupos = []
    grupo_actual = [puntos_ordenados[0]]

    for i in range(1, len(puntos_ordenados)):
        anterior = puntos_ordenados[i - 1]
        actual = puntos_ordenados[i]

        diff = planetas[actual]["lon"] - planetas[anterior]["lon"]

        if diff <= ORBE_STELLIUM_ENTRE_PUNTOS:
            grupo_actual.append(actual)
        else:
            grupos.append(grupo_actual)
            grupo_actual = [actual]

    grupos.append(grupo_actual)

    # Unir si el último grupo y el primero forman cadena cruzando 360° → 0°
    if len(grupos) > 1:
        primer_grupo = grupos[0]
        ultimo_grupo = grupos[-1]

        primero = primer_grupo[0]
        ultimo = ultimo_grupo[-1]

        diff_cierre = (planetas[primero]["lon"] + 360) - planetas[ultimo]["lon"]

        if diff_cierre <= ORBE_STELLIUM_ENTRE_PUNTOS:
            grupos[0] = ultimo_grupo + primer_grupo
            grupos.pop()

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

        figuras.append({
            "tipo": "Stellium",
            "puntos": grupo_ord,
            "casa": casas[0] if casas else "",
            "casas": casas,
            "signos": signos,
            "peso": puntuacion_figura(grupo_ord),
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

            oposicion = aspecto_entre(aspectos, a, b, "☍")
            if not oposicion:
                continue

            for c in puntos:
                if c in (a, b):
                    continue

                cuad1 = aspecto_entre(aspectos, c, a, "□")
                cuad2 = aspecto_entre(aspectos, c, b, "□")

                if cuad1 and cuad2:
                    puntos_exp = expandir_por_stellium(carta, [a, b, c])
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
                    puntos_exp = expandir_por_stellium(carta, [a, b, c])
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
                puntos_exp = expandir_por_stellium(carta, base_real + [foco])
                clave = tuple(sorted(puntos_exp))

                if clave in vistas:
                    continue

                vistas.add(clave)

                figuras.append({
                    "tipo": "Cometa",
                    "gran_trigono": expandir_por_stellium(carta, base_real),
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
                    puntos_exp = expandir_por_stellium(carta, [a, b, c])
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
                    puntos_exp = expandir_por_stellium(carta, [apex, p1, p2])
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
    filtradas = []

    prioridad = {
        "Cometa": 5,
        "T-cuadrada": 4,
        "Gran trígono": 3,
        "Triángulo de aprendizaje": 2,
        "Stellium": 1,
    }

    figuras_ordenadas = sorted(
        figuras,
        key=lambda f: (
            -prioridad.get(f["tipo"], 0),
            -len(f.get("puntos", [])),
            -f.get("peso", 0)
        )
    )

    for fig in figuras_ordenadas:
        puntos_fig = set(fig.get("puntos", []))
        tipo_fig = fig.get("tipo", "")

        absorbida = False

        for otra in filtradas:
            puntos_otra = set(otra.get("puntos", []))
            tipo_otra = otra.get("tipo", "")

            if puntos_fig and puntos_fig.issubset(puntos_otra):
                if tipo_fig != "Stellium":
                    absorbida = True
                    break

            # Si un gran trígono está contenido en un cometa, no lo repetimos
            if tipo_fig == "Gran trígono" and tipo_otra == "Cometa":
                if puntos_fig.issubset(puntos_otra):
                    absorbida = True
                    break

            # Si una T-cuadrada pequeña queda dentro de una T-cuadrada ampliada, no la repetimos
            if tipo_fig == "T-cuadrada" and tipo_otra == "T-cuadrada":
                if puntos_fig.issubset(puntos_otra):
                    absorbida = True
                    break

            # Si dos T-cuadradas comparten el mismo ápice y una contiene más puntos,
            # dejamos solo la más amplia.
            if tipo_fig == "T-cuadrada" and tipo_otra == "T-cuadrada":
                if fig.get("apice") == otra.get("apice"):
                    if len(puntos_fig) <= len(puntos_otra):
                        absorbida = True
                        break


        if not absorbida:
            filtradas.append(fig)

    return sorted(
        filtradas,
        key=lambda f: (
            -prioridad.get(f["tipo"], 0),
            -f.get("peso", 0),
            f.get("tipo", "")
        )
    )


def detectar_figuras(carta, aspectos):
    figuras = []

    figuras.extend(detectar_cometas(carta, aspectos))
    figuras.extend(detectar_t_cuadradas(carta, aspectos))
    figuras.extend(detectar_grandes_trigonos(carta, aspectos))
    figuras.extend(detectar_yods(carta, aspectos))
    figuras.extend(detectar_triangulos_aprendizaje(carta, aspectos))
    figuras.extend(detectar_stelliums(carta))

    return filtrar_figuras_absorbidas(figuras)


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

    elif tipo == "Triángulo de aprendizaje":

        asp_q = next((a for a in figura["aspectos"] if a["simbolo"] == "⚻"), None)
        asp_c = next((a for a in figura["aspectos"] if a["simbolo"] == "□"), None)
        asp_t = next((a for a in figura["aspectos"] if a["simbolo"] == "△"), None)

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

        partes.append(
            "Este tipo de configuración suele madurar lentamente. "
            "No se resuelve de una vez: se afina con experiencia, repetición y capacidad de reconocer cuándo estás reaccionando desde automatismo."
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
    principales = []
    secundarias = []
    derivadas = []

    for f in figuras:
        tipo = f.get("tipo", "")

        if es_figura_mayor(f):
            principales.append(f)
        elif tipo in ("Gran trígono", "Stellium"):
            secundarias.append(f)
        else:
            derivadas.append(f)

    return principales, secundarias, derivadas

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

    intro = texto_intro_figuras(figuras)


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