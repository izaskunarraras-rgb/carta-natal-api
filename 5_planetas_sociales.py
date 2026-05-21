#!/usr/bin/env python3
"""
5. Planetas Sociales — Júpiter y Saturno — Arquitectura Interna
Interpreta cómo el sistema se expande en el mundo (Júpiter)
y cómo se estructura y limita en su relación con él (Saturno).
"""

import sys, os, math, subprocess
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np

import swisseph as swe
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import pytz

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── RUEDA ASTROLÓGICA ────────────────────────────────────────────────────────

def dibujar_rueda(carta, nombre_persona, ruta_rueda):
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
    _ASP_COLORES = {"□":"#CC2200","☍":"#CC2200","△":"#1A5FA8","✶":"#1A5FA8","⚻":"#2E7D32"}
    _ASP_LW      = {"□":1.0,"☍":1.0,"△":0.9,"✶":0.8,"⚻":0.7}
    _ASP_ALPHA   = {"□":0.55,"☍":0.55,"△":0.50,"✶":0.45,"⚻":0.35}

    R_ASP = R_CASA_IN - 0.02

    aspectos_rueda = calcular_aspectos_sociales(carta["planetas"])

    planetas_con_aspecto = set()
    for asp in aspectos_rueda:
        planetas_con_aspecto.add(asp["p1"])
        planetas_con_aspecto.add(asp["p2"])

    for asp in aspectos_rueda:
        if asp["orbe"] > 8.5:
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
            [math.cos(a1)*R_ASP, math.cos(a2)*R_ASP],
            [math.sin(a1)*R_ASP, math.sin(a2)*R_ASP],
            color=_ASP_COLORES[sim],
            linewidth=_ASP_LW[sim],
            alpha=_ASP_ALPHA[sim],
            zorder=2
        )

    orden_base = [
        "Júpiter", "Saturno",
        "Sol", "Luna", "Mercurio", "Venus", "Marte",
        "Quirón", "Lilith",
        "Nodo Norte", "Nodo Sur"
    ]

    orden = [
        p for p in orden_base
        if p in (
            "Júpiter", "Saturno",
            "Sol", "Luna", "Mercurio", "Venus", "Marte",
            "Quirón", "Lilith"
            "Nodo Norte", "Nodo Sur"
        ) and (
            p in ("Júpiter", "Saturno")
            or p in planetas_con_aspecto
        )
    ]

    # Todos los planetas deben permanecer en el anillo central.
    # Estos límites evitan que un planeta cercano se meta dentro del círculo interior.
    RADIO_MIN = R_CASA_IN + 0.08
    RADIO_MAX = R_SIGN_IN - 0.08
    RADIO_SEP = 0.08

    lones_usados = []
    radios = {}

    for nombre_planeta in orden:
        if nombre_planeta not in carta["planetas"]:
            continue

        lon = carta["planetas"][nombre_planeta]["lon"]
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
        radios[nombre_planeta] = radio

    for nombre_planeta in orden:
        if nombre_planeta not in carta["planetas"]:
            continue

        p = carta["planetas"][nombre_planeta]
        ang = lon_a_angulo(p["lon"])
        r = radios[nombre_planeta]
        color = COLORES_PLANETA.get(nombre_planeta, "#333")
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
    plt.savefig(ruta_rueda, dpi=150, bbox_inches="tight", facecolor="white", edgecolor="none")
    plt.close()



# ─── CONSTANTES ────────────────────────────────────────────────────────────────

SIGNOS = [
    "Aries","Tauro","Géminis","Cáncer",
    "Leo","Virgo","Libra","Escorpio",
    "Sagitario","Capricornio","Acuario","Piscis"
]

ELEMENTO_SIGNO = {
    "Aries":"Fuego",
    "Tauro":"Tierra",
    "Géminis":"Aire",
    "Cáncer":"Agua",

    "Leo":"Fuego",
    "Virgo":"Tierra",
    "Libra":"Aire",
    "Escorpio":"Agua",

    "Sagitario":"Fuego",
    "Capricornio":"Tierra",
    "Acuario":"Aire",
    "Piscis":"Agua"
}

SIMBOLOS_SIGNOS = [
    "♈","♉","♊","♋",
    "♌","♍","♎","♏",
    "♐","♑","♒","♓"
]

COLORES_ELEMENTO = {"Fuego":"#CC2200","Tierra":"#2E7D32","Aire":"#E67E00","Agua":"#1A5FA8"}

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

PLANETAS_IDS = [
    (swe.SUN,     "Sol",       "☉"),
    (swe.MOON,    "Luna",      "☽"),
    (swe.MERCURY, "Mercurio",  "☿"),
    (swe.VENUS,   "Venus",     "♀"),
    (swe.MARS,    "Marte",     "♂"),
    (swe.JUPITER, "Júpiter",   "♃"),
    (swe.SATURN,  "Saturno",   "♄"),
    (swe.URANUS,  "Urano",     "♅"),
    (swe.NEPTUNE, "Neptuno",   "♆"),
    (swe.PLUTO,   "Plutón",    "♇"),
]

PLANETAS_SOCIALES = [
    "Júpiter",
    "Saturno"
]

CHIRON_ID = swe.CHIRON
LILITH_ID = swe.MEAN_APOG


# ─── ASPECTOS PRINCIPALES ─────────────────────────────────────────────────────

def calcular_aspectos_sociales(planetas):

    ASPECTOS = {
        0:   ("Conjunción", "=", 10),
        60:  ("Sextil", "✶", 6),
        90:  ("Cuadratura", "□", 8),
        120: ("Trígono", "△", 8),
        180: ("Oposición", "☍", 8),
    }

    nombres = list(planetas.keys())
    aspectos = []

    for i in range(len(nombres)):
        for j in range(i + 1, len(nombres)):
            n1, n2 = nombres[i], nombres[j]

            diff = abs(planetas[n1]["lon"] - planetas[n2]["lon"])
            if diff > 180:
                diff = 360 - diff

            for angulo, (nombre_asp, simbolo_asp, orbe) in ASPECTOS.items():

                orbe_real = orbe

                # Oposición ampliada a 10° si participa Sol o Luna
                if (
                    simbolo_asp == "☍"
                    and (n1 in ("Sol", "Luna") or n2 in ("Sol", "Luna"))
                ):
                    orbe_real = 10

                if abs(diff - angulo) <= orbe_real:
                    orbe_val = round(abs(diff - angulo), 2)

                    aspectos.append({
                        "p1": n1,
                        "p2": n2,
                        "nombre": nombre_asp,
                        "simbolo": simbolo_asp,
                        "orbe": orbe_val,
                        "relevancia": "exacto" if orbe_val <= 1.0 else "estructural",
                    })
                    break

    return sorted(aspectos, key=lambda x: x["orbe"])

# ─── TEXTOS: JÚPITER POR SIGNO ────────────────────────────────────────────────
# Cómo tiendes a expandirte, qué puede llevarte al desbordamiento
# y qué suele bloquear o frenar el crecimiento.

JUPITER_SIGNO = {

"Aries": (
    "Tiendes a crecer a través de la iniciativa, el movimiento y la exploración de territorio nuevo. "
    "La expansión aparece cuando puedes empezar algo, abrir camino o avanzar hacia lo desconocido. "
    "Necesitas sentir impulso, dirección y margen de acción para que la energía de crecimiento se active.\n\n"

    "En situaciones de desbordamiento: puedes abrir más frentes de los que realmente puedes sostener. "
    "La energía se dispersa entre comienzos, impulsos o proyectos que no siempre llegan a consolidarse. "

    "En momentos de estancamiento: necesitas demasiado estímulo, reto o sensación de avance para mantenerte en movimiento. "
    "Si no hay una dirección clara hacia la que ir, puede aparecer actividad constante sin sensación real de crecimiento."
),

"Tauro": (
    "Tiendes a crecer consolidando, estabilizando y profundizando en lo que ya existe. "
    "La expansión aparece cuando puedes construir algo sólido, útil y sostenible en el tiempo. "
    "Necesitas sentir continuidad y cierta seguridad para avanzar.\n\n"

    "En situaciones de desbordamiento: puedes aferrarte demasiado a estructuras, vínculos o formas de funcionamiento que ya han cumplido su ciclo. "
    "La necesidad de conservar dificulta hacer espacio para lo nuevo. "

    "En momentos de estancamiento: puedes necesitar demasiadas garantías antes de dar un paso importante. "
    "El miedo a perder estabilidad puede retrasar movimientos necesarios."
),

"Géminis": (
    "Tiendes a crecer a través del intercambio, el aprendizaje y la variedad de estímulos. "
    "La expansión aparece cuando puedes explorar ideas nuevas, relacionarte con perspectivas distintas y mantener la mente en movimiento. "
    "Necesitas circulación, curiosidad y flexibilidad.\n\n"

    "En situaciones de desbordamiento: puedes dispersarte entre demasiadas ideas, conversaciones o direcciones abiertas a la vez. "
    "Acumular información no siempre significa integrarla en algo coherente. "

    "En momentos de estancamiento: la falta de novedad o movimiento mental puede hacer que pierdas interés rápidamente. "
    "Puede haber mucha actividad interna sin sensación real de avance."
),

"Cáncer": (
    "Tiendes a crecer a través del cuidado, la pertenencia y la construcción de vínculos significativos. "
    "La expansión aparece cuando sientes conexión emocional con lo que haces, construyes o sostienes. "
    "Necesitas seguridad afectiva para abrirte al crecimiento.\n\n"

    "En situaciones de desbordamiento: puedes asumir más responsabilidad emocional de la que realmente puedes sostener. "
    "La necesidad de cuidar puede hacer que te olvides de tus propios límites. "

    "En momentos de estancamiento: si no sientes suficiente seguridad o protección, tiendes a cerrarte antes que a expandirte. "
    "La necesidad de resguardo puede frenar movimientos importantes."
),

"Leo": (
    "Tiendes a crecer a través de la expresión, la creatividad y la posibilidad de mostrar algo propio. "
    "La expansión aparece cuando puedes crear, compartir y sentir que lo que haces tiene presencia o impacto. "
    "Necesitas espacio para expresarte con autenticidad.\n\n"

    "En situaciones de desbordamiento: la necesidad de reconocimiento puede ocupar demasiado espacio. "
    "Puedes aumentar el esfuerzo esperando una validación externa que no siempre llega como imaginas. "

    "En momentos de estancamiento: si no encuentras espacios donde sentirte vista o escuchada, la motivación puede disminuir mucho. "
    "Puedes quedar esperando respuesta del entorno en lugar de generar nuevas formas de expresión."
),

"Virgo": (
    "Tiendes a crecer a través de la mejora, el refinamiento y la búsqueda de coherencia. "
    "La expansión aparece cuando puedes ordenar, perfeccionar o hacer algo de forma más precisa y útil. "
    "Necesitas sentir que lo que haces tiene sentido práctico y calidad real.\n\n"

    "En situaciones de desbordamiento: puedes entrar en corrección constante, exceso de análisis o autoexigencia permanente. "
    "La necesidad de mejorar ocupa más energía de la que realmente aporta. "

    "En momentos de estancamiento: puedes sentir que todavía falta algo antes de avanzar. "
    "La búsqueda de perfección puede retrasar decisiones o movimientos importantes."
),

"Libra": (
    "Tiendes a crecer a través del intercambio, la relación y la construcción de equilibrio con otras personas. "
    "La expansión aparece cuando puedes compartir, contrastar y crear vínculos donde exista reciprocidad. "
    "Necesitas relación para desarrollar perspectiva.\n\n"

    "En situaciones de desbordamiento: puedes adaptarte demasiado a lo que otras personas esperan, necesitan o aceptan. "
    "La búsqueda de armonía puede alejarte de tu propio eje. "

    "En momentos de estancamiento: tomar decisiones en soledad puede resultar difícil o desgastante. "
    "Sin diálogo o intercambio, la dirección de crecimiento pierde claridad."
),

"Escorpio": (
    "Tiendes a crecer a través de la profundidad, la transformación y el contacto con lo que no siempre es visible. "
    "La expansión aparece cuando puedes atravesar procesos intensos y comprender capas más profundas de la realidad o de ti misma. "
    "Necesitas sentir que lo que haces tiene densidad y verdad.\n\n"

    "En situaciones de desbordamiento: la intensidad puede convertirse en control, invasión o exceso emocional. "
    "Puedes intentar profundizar más allá de lo que realmente puedes sostener. "

    "En momentos de estancamiento: la desconfianza dificulta abrirte a experiencias nuevas. "
    "La necesidad de protegerte termina limitando el crecimiento."
),

"Sagitario": (
    "Tiendes a crecer a través del movimiento, la exploración y la búsqueda de sentido. "
    "La expansión aparece cuando hay horizonte, posibilidad y sensación de apertura hacia algo mayor. "
    "Necesitas amplitud, aprendizaje y dirección para sentir vitalidad.\n\n"

    "En situaciones de desbordamiento: puedes abrir demasiadas posibilidades al mismo tiempo. "
    "La amplitud supera la capacidad de concretar y el movimiento termina sustituyendo a la integración. "

    "En momentos de estancamiento: si no encuentras un horizonte suficientemente amplio o estimulante, puedes perder dirección rápidamente. "
    "La energía queda suspendida entre posibilidades sin terminar de encarnarse en ninguna."
),

"Capricornio": (
    "Tiendes a crecer construyendo, organizando y sosteniendo procesos a largo plazo. "
    "La expansión aparece cuando puedes avanzar hacia objetivos concretos y desarrollar algo sólido con el tiempo. "
    "Necesitas estructura, dirección y sensación de utilidad real.\n\n"

    "En situaciones de desbordamiento: puedes asumir demasiadas responsabilidades o cargar con más de lo que realmente puedes sostener. "
    "El crecimiento termina convirtiéndose en peso o rigidez. "

    "En momentos de estancamiento: puedes sentir que todavía no existen las condiciones adecuadas para avanzar. "
    "La prudencia excesiva puede frenar movimientos importantes."
),

"Acuario": (
    "Tiendes a crecer a través de la innovación, la apertura mental y la posibilidad de aportar algo diferente. "
    "La expansión aparece cuando puedes cuestionar estructuras existentes y participar en algo más amplio que lo estrictamente personal. "
    "Necesitas libertad mental y espacio para pensar distinto.\n\n"

    "En situaciones de desbordamiento: puedes perder contacto con lo concreto y quedar atrapada en ideas que nunca llegan a materializarse. "
    "La distancia emocional o la abstracción excesiva dificultan la integración real. "

    "En momentos de estancamiento: si no encuentras un contexto donde sentir que tu visión tiene sentido, la motivación disminuye mucho. "
    "La falta de conexión con algo colectivo o significativo puede bloquear la dirección de crecimiento."
),

"Piscis": (
    "Tiendes a crecer a través de la sensibilidad, la apertura y la conexión con dimensiones más amplias o difíciles de delimitar. "
    "La expansión aparece cuando puedes relajarte, confiar y permitir que la vida te atraviese sin intentar controlarlo todo. "
    "Necesitas espacio para sentir, imaginar y conectar con lo intangible.\n\n"

    "En situaciones de desbordamiento: puedes perder límites, dirección o capacidad de diferenciar lo propio de lo ajeno. "
    "La apertura se convierte en dispersión o dificultad para sostener forma concreta. "

    "En momentos de estancamiento: la falta de claridad dificulta iniciar movimiento. "
    "Cuando todo permanece demasiado abierto o indefinido, puede costarte dar un paso concreto."
),

}

# ─── TEXTOS: JÚPITER POR CASA ─────────────────────────────────────────────────

JUPITER_CASA = {

1: (
    "Tiendes a crecer a través de la presencia directa, la iniciativa y la expresión personal. "
    "La expansión aparece cuando puedes ocupar espacio, actuar desde tu propio impulso "
    "y desarrollar una identidad visible y autónoma. "
    "Lo que haces suele tener impacto inmediato en el entorno."
),

2: (
    "Tiendes a crecer construyendo recursos, estabilidad y sensación de valor propio. "
    "La expansión aparece cuando puedes desarrollar capacidades concretas "
    "y generar una base material o emocional más sólida. "
    "Necesitas sentir que lo que haces tiene utilidad y consistencia real."
),

3: (
    "Tiendes a crecer a través del aprendizaje, la comunicación y el intercambio de ideas. "
    "La expansión aparece cuando puedes conversar, enseñar, estudiar o conectar perspectivas diferentes. "
    "Necesitas movimiento mental, curiosidad y circulación de información."
),

4: (
    "Tiendes a crecer desde la base interior, la intimidad y la sensación de pertenencia. "
    "La expansión aparece cuando existe suficiente seguridad emocional y un espacio propio desde el que sostenerte. "
    "Necesitas raíces sólidas antes de extenderte hacia fuera."
),

5: (
    "Tiendes a crecer a través de la creatividad, la expresión y el disfrute de lo que haces. "
    "La expansión aparece cuando puedes crear, jugar, compartir algo propio "
    "y sentir vitalidad en lo que expresas. "
    "Necesitas espacio para desarrollar espontaneidad y presencia."
),

6: (
    "Tiendes a crecer a través del trabajo cotidiano, el aprendizaje práctico y la mejora constante. "
    "La expansión aparece cuando puedes desarrollar habilidades útiles "
    "y organizar tu vida de forma más eficiente y coherente. "
    "Necesitas sentir que lo que haces tiene función y aporta algo concreto."
),

7: (
    "Tiendes a crecer a través de las relaciones, el intercambio y el contacto con otras personas. "
    "La expansión aparece en el vínculo, la colaboración y la posibilidad de construir perspectiva compartida. "
    "Necesitas diálogo, reciprocidad y apertura hacia lo diferente."
),

8: (
    "Tiendes a crecer atravesando procesos profundos de transformación y cambio. "
    "La expansión aparece cuando puedes entrar en contacto con capas menos visibles de la experiencia "
    "y desarrollar mayor profundidad emocional o psicológica. "
    "Necesitas intensidad, verdad y capacidad de atravesar procesos complejos."
),

9: (
    "Tiendes a crecer a través del conocimiento, la exploración y la búsqueda de sentido. "
    "La expansión aparece cuando puedes ampliar horizontes, viajar, estudiar o desarrollar una visión más amplia de la vida. "
    "Necesitas dirección, posibilidad y sensación de apertura hacia algo mayor."
),

10: (
    "Tiendes a crecer construyendo algo visible y reconocible en el mundo. "
    "La expansión aparece cuando puedes asumir responsabilidad, desarrollar una dirección clara "
    "y avanzar hacia objetivos que tengan impacto o proyección externa. "
    "Necesitas sentir que lo que haces ocupa un lugar real."
),

11: (
    "Tiendes a crecer a través de grupos, redes y proyectos compartidos. "
    "La expansión aparece cuando puedes participar en algo colectivo "
    "y aportar tu visión a espacios más amplios que lo estrictamente personal. "
    "Necesitas conexión con ideas, personas o proyectos que miren hacia el futuro."
),

12: (
    "Tiendes a crecer en espacios de introspección, silencio y contacto con dimensiones menos visibles de la vida. "
    "La expansión aparece cuando puedes retirarte, integrar y desarrollar comprensión interna sin exceso de estímulo externo. "
    "Necesitas tiempo de soledad y profundidad para que el crecimiento pueda asentarse."
),

}


# ─── TEXTOS: SATURNO POR SIGNO ────────────────────────────────────────────────
# Cómo tiendes a estructurarte, dónde aparece el límite
# y qué suele ocurrir cuando la estructura deja de sostenerse.

SATURNO_SIGNO = {

"Aries": (
    "Tiendes a estructurarte a través de la acción y la experiencia directa. "
    "Aprendes haciendo: la claridad aparece mientras avanzas, no necesariamente antes. "
    "Necesitas movimiento, iniciativa y capacidad de actuar por ti misma para desarrollar estructura.\n\n"

    "El límite suele aparecer en la velocidad y en la dificultad para detenerte antes de agotarte. "
    "Puedes seguir empujando incluso cuando el cuerpo o la realidad ya están marcando un freno.\n\n"

    "Cuando la estructura deja de sostenerse: puedes intentar resolverlo haciendo todavía más. "
    "El esfuerzo aumenta, pero la organización interna pierde estabilidad y aparece desgaste."
),

"Tauro": (
    "Tiendes a estructurarte construyendo estabilidad, continuidad y seguridad concreta. "
    "Necesitas tiempo para consolidar lo que haces y desarrollar una base sólida antes de abrir nuevos movimientos. "
    "La estructura suele fortalecerse lentamente, pero con mucha permanencia.\n\n"

    "El límite aparece en la capacidad real de sostener lo acumulado. "
    "No todo lo que construyes puede mantenerse indefinidamente.\n\n"

    "Cuando la estructura deja de sostenerse: puedes aferrarte a formas, vínculos o dinámicas que ya no funcionan. "
    "La necesidad de conservar estabilidad termina convirtiéndose en rigidez."
),

"Géminis": (
    "Tiendes a estructurarte organizando información, conexiones e ideas. "
    "Necesitas comprender, relacionar y clasificar lo que ocurre para sentir orden interno. "
    "La estructura aparece cuando puedes traducir la complejidad en algo comprensible.\n\n"

    "El límite aparece cuando hay más estímulos o información de la que realmente puedes organizar. "
    "La mente intenta sostener demasiadas cosas al mismo tiempo.\n\n"

    "Cuando la estructura deja de sostenerse: aparece dispersión, ruido mental o dificultad para priorizar. "
    "Puedes recibir mucho input sin conseguir transformarlo en dirección clara."
),

"Cáncer": (
    "Tiendes a estructurarte a través de la protección emocional y la construcción de espacios seguros. "
    "Necesitas sentir contención, intimidad y cierto resguardo para sostenerte de forma estable. "
    "La estructura aparece delimitando qué puedes sostener emocionalmente y qué no.\n\n"

    "El límite aparece en la cantidad de carga emocional que puedes absorber antes de saturarte. "
    "No todo puede entrar dentro de tu espacio interno.\n\n"

    "Cuando la estructura deja de sostenerse: puedes cerrarte defensivamente o reaccionar desde la protección. "
    "La necesidad de resguardo sustituye la capacidad de procesar lo que ocurre."
),

"Leo": (
    "Tiendes a estructurarte a través de la expresión sostenida y la construcción de una identidad coherente. "
    "Necesitas sentir continuidad entre lo que eres, lo que haces y la forma en que eso puede mostrarse al mundo. "
    "La estructura aparece desarrollando algo propio con consistencia.\n\n"

    "El límite aparece cuando el reconocimiento externo no acompaña el esfuerzo que estás realizando. "
    "No siempre el entorno puede responder en la medida esperada.\n\n"

    "Cuando la estructura deja de sostenerse: puedes aumentar demasiado el esfuerzo buscando validación o perder motivación si la respuesta externa desaparece. "
    "La dependencia del reconocimiento vuelve más frágil la estabilidad interna."
),

"Virgo": (
    "Tiendes a estructurarte a través del orden, la precisión y la mejora constante. "
    "Necesitas procedimientos claros, coherencia funcional y sensación de utilidad real para sostenerte. "
    "La estructura aparece refinando continuamente lo que haces.\n\n"

    "El límite aparece en el desgaste de intentar mantener estándares demasiado altos de forma permanente. "
    "No todo puede estar completamente bajo control.\n\n"

    "Cuando la estructura deja de sostenerse: aparece exceso de análisis, ansiedad funcional o necesidad de corregir continuamente. "
    "La organización consume más energía de la que realmente aporta."
),

"Libra": (
    "Tiendes a estructurarte a través de los acuerdos, el equilibrio y la reciprocidad. "
    "Necesitas relaciones relativamente estables y sensación de intercambio justo para sentir coherencia. "
    "La estructura aparece en la capacidad de sostener vínculos funcionales.\n\n"

    "El límite aparece cuando el intercambio deja de ser equilibrado. "
    "Las asimetrías prolongadas desgastan mucho tu capacidad de sostén.\n\n"

    "Cuando la estructura deja de sostenerse: puedes adaptarte demasiado al otro o paralizarte esperando equilibrio antes de avanzar. "
    "Sostener relaciones desequilibradas termina agotándote."
),

"Escorpio": (
    "Tiendes a estructurarte a través del control de lo importante y la profundidad emocional. "
    "Necesitas sentir que puedes confiar en lo que entra dentro de tu vida y comprender lo que ocurre bajo la superficie. "
    "La estructura aparece delimitando cuidadosamente qué merece acceso a tu espacio interno.\n\n"

    "El límite aparece en la dificultad para confiar plenamente o soltar el control. "
    "No todo puede verificarse antes de abrirse.\n\n"

    "Cuando la estructura deja de sostenerse: el control reemplaza la capacidad de organizar y contener. "
    "La vigilancia constante termina consumiendo mucha energía y dificultando la flexibilidad."
),

"Sagitario": (
    "Tiendes a estructurarte a través del sentido, la visión y los marcos que dan orientación a la vida. "
    "Necesitas sentir que lo que haces encaja dentro de una dirección más amplia y coherente. "
    "La estructura aparece cuando existe significado suficiente para sostener el movimiento.\n\n"

    "El límite aparece cuando la realidad deja de encajar dentro del marco desde el que estabas organizándote. "
    "No siempre las ideas pueden contener todo lo que ocurre.\n\n"

    "Cuando la estructura deja de sostenerse: puedes intentar forzar la realidad para que encaje en tu visión o perder completamente la orientación. "
    "Sin sentido claro, cuesta sostener dirección y coherencia."
),

"Capricornio": (
    "Tiendes a estructurarte a través de la disciplina, la responsabilidad y la construcción a largo plazo. "
    "Necesitas objetivos claros, organización y sensación de avance progresivo para sostenerte. "
    "La estructura suele desarrollarse con consistencia y capacidad de resistencia.\n\n"

    "El límite aparece en el coste continuo de mantener lo construido. "
    "La estabilidad requiere esfuerzo sostenido durante mucho tiempo.\n\n"

    "Cuando la estructura deja de sostenerse: puedes continuar manteniendo formas que ya no tienen función real solo porque costó mucho construirlas. "
    "La solidez se convierte en rigidez."
),

"Acuario": (
    "Tiendes a estructurarte a través de principios, ideas y comprensión sistémica. "
    "Necesitas libertad mental y marcos amplios que permitan organizar múltiples elementos a la vez. "
    "La estructura aparece cuando puedes comprender cómo encajan las cosas dentro de un conjunto más grande.\n\n"

    "El límite aparece cuando las ideas no encuentran forma concreta de materializarse. "
    "No todo puede sostenerse únicamente desde lo conceptual.\n\n"

    "Cuando la estructura deja de sostenerse: puedes quedar atrapada organizando ideas sin aterrizarlas en acciones concretas. "
    "La coherencia existe mentalmente, pero no termina de convertirse en realidad operativa."
),

"Piscis": (
    "Tiendes a estructurarte a través de la sensibilidad, la apertura y la capacidad de adaptarte a lo que emerge. "
    "Necesitas cierto margen de fluidez y permeabilidad para sentir coherencia interna. "
    "La estructura aparece más acompañando procesos que intentando controlarlos completamente.\n\n"

    "El límite aparece en la cantidad de indefinición que puedes sostener sin perder claridad o dirección. "
    "Demasiada apertura puede dificultar mantener forma estable.\n\n"

    "Cuando la estructura deja de sostenerse: aparecen dispersión, desorganización o sensación de pérdida de rumbo. "
    "Lo que no tiene límites suficientes termina diluyéndose."
),

}

# ─── TEXTOS: SATURNO POR CASA ─────────────────────────────────────────────────

SATURNO_CASA = {

1: (
    "Tiendes a estructurarte a través de la presencia personal y la forma en que ocupas espacio en el mundo. "
    "La estabilidad se construye desarrollando una identidad coherente, sólida y capaz de sostenerse frente al entorno. "
    "Necesitas sentir consistencia entre quién eres, cómo actúas y cómo te presentas.\n\n"

    "El límite aparece cuando intentas sostener una imagen o una forma de funcionar que ya no encaja contigo. "
    "No puedes separarte demasiado de tu propia estructura sin pagar un coste interno."
),

2: (
    "Tiendes a estructurarte a través de los recursos, la estabilidad y la gestión de lo que tiene valor para ti. "
    "La seguridad suele construirse lentamente, mediante constancia y acumulación progresiva. "
    "Necesitas sentir que existe una base concreta sobre la que apoyarte.\n\n"

    "El límite aparece cuando intentas sostener más de lo que tus recursos reales permiten. "
    "La estabilidad depende de la capacidad de administrar energía, tiempo y recursos de forma sostenible."
),

3: (
    "Tiendes a estructurarte organizando información, pensamiento y comunicación. "
    "Necesitas comprender, ordenar y expresar con claridad para sentir estabilidad mental. "
    "La estructura aparece desarrollando criterio y precisión en la forma de pensar.\n\n"

    "El límite aparece cuando la cantidad de estímulo o información supera tu capacidad de organización. "
    "Demasiadas ideas simultáneas pueden generar saturación y pérdida de claridad."
),

4: (
    "Tiendes a estructurarte desde la base emocional, la intimidad y el espacio privado. "
    "Necesitas construir una sensación interna de sostén antes de poder abrirte plenamente hacia fuera. "
    "La estabilidad depende mucho de la calidad del espacio interior que desarrollas.\n\n"

    "El límite aparece en la capacidad de contención emocional y en lo que realmente puedes sostener dentro de tu vida privada. "
    "Cuando no existe suficiente base interna, todo lo externo se vuelve más difícil de sostener."
),

5: (
    "Tiendes a estructurarte a través de la creatividad, la expresión y lo que produces personalmente. "
    "Necesitas sentir que lo que haces tiene calidad, coherencia y consistencia en el tiempo. "
    "La expresión suele pasar por un filtro interno exigente.\n\n"

    "El límite aparece cuando la autoexigencia supera la capacidad real de disfrute o producción. "
    "Puedes bloquearte intentando alcanzar un estándar demasiado alto antes de permitirte crear libremente."
),

6: (
    "Tiendes a estructurarte a través de la rutina, el trabajo cotidiano y la organización práctica de la vida. "
    "Necesitas hábitos relativamente claros y sensación de utilidad para sentir estabilidad. "
    "La estructura aparece desarrollando disciplina en lo pequeño y en lo repetido.\n\n"

    "El límite aparece en el desgaste acumulado de sostener demasiada exigencia cotidiana. "
    "Puedes agotarte más por el rigor constante que por el trabajo en sí mismo."
),

7: (
    "Tiendes a estructurarte a través de los compromisos y las relaciones de largo plazo. "
    "Necesitas vínculos relativamente sólidos, claros y sostenibles para sentir coherencia. "
    "Las relaciones suelen vivirse con seriedad y sentido de responsabilidad.\n\n"

    "El límite aparece en los vínculos que no pueden sostener reciprocidad, compromiso o estabilidad suficiente. "
    "Las relaciones demasiado ambiguas o inconsistentes generan mucho desgaste."
),

8: (
    "Tiendes a estructurarte a través de la profundidad emocional y la gestión cuidadosa de lo compartido. "
    "Necesitas sentir confianza, control relativo y capacidad de integración antes de abrir espacios profundos con otras personas. "
    "La estabilidad depende de cómo manejas los procesos intensos y transformadores.\n\n"

    "El límite aparece cuando la intensidad emocional supera tu capacidad de integración. "
    "No todo puede sostenerse indefinidamente sin afectar tu equilibrio interno."
),

9: (
    "Tiendes a estructurarte a través del conocimiento, la filosofía y los marcos que dan sentido a la vida. "
    "Necesitas desarrollar criterios sólidos y una comprensión coherente de la realidad para sentir dirección. "
    "La estructura aparece construyendo pensamiento profundo y bien fundamentado.\n\n"

    "El límite aparece cuando las ideas o creencias dejan de poder contener lo que estás viviendo. "
    "La necesidad de coherencia puede volverse rígida si cuesta revisar el propio marco."
),

10: (
    "Tiendes a estructurarte a través de la responsabilidad, la construcción profesional y la posición que ocupas en el mundo. "
    "Necesitas desarrollar algo sólido, visible y sostenible en el tiempo. "
    "La estabilidad suele apoyarse en la capacidad de asumir compromiso y mantener dirección a largo plazo.\n\n"

    "El límite aparece en el coste de sostener lo construido. "
    "Todo lo que desarrollas requiere mantenimiento, disciplina y continuidad para permanecer estable."
),

11: (
    "Tiendes a estructurarte a través de grupos, proyectos colectivos y redes de colaboración. "
    "Necesitas sentir que formas parte de algo más amplio y que existe coherencia entre tus principios y los espacios en los que participas. "
    "La estructura aparece organizando vínculos y objetivos compartidos.\n\n"

    "El límite aparece cuando la realidad de los grupos no coincide con los ideales que intentas sostener. "
    "La distancia entre visión y funcionamiento real puede generar frustración o desconexión."
),

12: (
    "Tiendes a estructurarte en espacios internos, silenciosos o poco visibles desde fuera. "
    "Necesitas tiempo de retiro, introspección y elaboración interna para desarrollar estabilidad profunda. "
    "Gran parte de la estructura se construye lejos de la mirada externa.\n\n"

    "El límite aparece cuando necesitas sostener forma sin reconocimiento, validación o referencia externa clara. "
    "Puede resultar difícil confiar en procesos que solo son visibles para ti."
),

}

# ─── ASPECTOS ENTRE PLANETAS SOCIALES ─────────────────────────────────────────

ASPECTOS_SOCIALES = {

# ── Júpiter – Saturno ─────────────────────────────────────────────────────────

("Júpiter", "Saturno", "="): (
    "Júpiter y Saturno en conjunción: crecimiento y estructura funcionan desde el mismo lugar. "
    "Tiendes a construir mientras avanzas y a expandirte buscando estabilidad al mismo tiempo. "
    "Cuando ambos trabajan coordinados, puedes desarrollar algo sólido sin perder movimiento.\n\n"

    "Cuando no hay coordinación: la exigencia de estructura puede frenar el crecimiento "
    "o la necesidad de expansión puede sobrepasar lo que realmente puedes sostener."
),

("Júpiter", "Saturno", "□"): (
    "Júpiter cuadratura Saturno: crecimiento y estructura están en tensión constante. "
    "Puedes sentir que una parte de ti quiere ampliar, probar o abrir posibilidades "
    "mientras otra necesita controlar, contener o limitar el movimiento.\n\n"

    "A veces puedes expandirte más allá de lo que realmente puedes sostener; "
    "otras veces puedes frenarte demasiado antes de permitirte crecer. "
    "El trabajo suele estar en reconocer cuándo estás en cada extremo."
),

("Júpiter", "Saturno", "☍"): (
    "Júpiter oposición Saturno: expansión y estructura tienden a funcionar como fuerzas opuestas. "
    "Cuando priorizas crecimiento, libertad o apertura, puede costarte mantener estabilidad. "
    "Cuando priorizas control o estructura, la expansión pierde espacio.\n\n"

    "Necesitas aprender a alternar conscientemente entre momentos de apertura "
    "y momentos de consolidación, sin exigir que ambos ocurran siempre al mismo tiempo."
),

("Júpiter", "Saturno", "△"): (
    "Júpiter trígono Saturno: crecimiento y estructura tienden a colaborar de forma natural. "
    "Puedes expandirte sin perder estabilidad y construir sin sentir que todo se detiene. "
    "Suele existir buena capacidad para desarrollar algo de forma progresiva y sostenible.\n\n"

    "El riesgo es confiar demasiado en que todo fluirá solo "
    "y no revisar cuándo hace falta ajustar ritmo, límites o dirección."
),

("Júpiter", "Saturno", "✶"): (
    "Júpiter sextil Saturno: existe compatibilidad entre crecimiento y estructura. "
    "Cuando desarrollas consciencia y coordinación entre ambos, "
    "puedes avanzar de forma estable y sostenida."
),

# ── Júpiter – Sol ─────────────────────────────────────────────────────────────

("Júpiter", "Sol", "="): (
    "Júpiter en conjunción con el Sol: la necesidad de crecimiento amplifica mucho tu dirección vital. "
    "Tiendes a avanzar con amplitud, entusiasmo y sensación de posibilidad.\n\n"

    "El riesgo aparece cuando te comprometes con más de lo que realmente puedes sostener "
    "o cuando el impulso de expansión supera los límites reales de tiempo, energía o estructura."
),

("Júpiter", "Sol", "□"): (
    "Júpiter cuadratura Sol: la necesidad de crecer y la dirección que intentas sostener generan tensión. "
    "Puedes querer expandirte más allá de lo que realmente puedes integrar "
    "o sentir que la dirección actual resulta demasiado estrecha para lo que necesitas desarrollar.\n\n"

    "La dificultad suele aparecer al medir límites, ritmos y capacidad real de sostén."
),

("Júpiter", "Sol", "☍"): (
    "Júpiter oposición Sol: dirección y expansión no siempre avanzan en la misma dirección. "
    "Cuando priorizas crecimiento, apertura o nuevas posibilidades, puede costarte mantener foco claro. "
    "Cuando sostienes dirección concreta, puedes sentir que pierdes amplitud o libertad.\n\n"

    "Necesitas aprender cuándo abrir posibilidades y cuándo concentrar energía."
),

("Júpiter", "Sol", "△"): (
    "Júpiter trígono Sol: crecimiento y dirección vital colaboran con relativa facilidad. "
    "Suele existir sensación de coherencia entre lo que quieres desarrollar y la forma en que avanzas hacia ello."
),

("Júpiter", "Sol", "✶"): (
    "Júpiter sextil Sol: existe buena compatibilidad entre dirección y crecimiento. "
    "Cuando activas ambos conscientemente, pueden reforzarse mutuamente."
),

# ── Júpiter – Luna ────────────────────────────────────────────────────────────

("Júpiter", "Luna", "="): (
    "Júpiter en conjunción con la Luna: crecimiento y vida emocional están muy conectados. "
    "Tiendes a abrirte emocionalmente con facilidad y a absorber mucho de lo que ocurre alrededor.\n\n"

    "El riesgo aparece cuando das más espacio emocional del que realmente puedes contener o integrar."
),

("Júpiter", "Luna", "□"): (
    "Júpiter cuadratura Luna: la necesidad de crecimiento y la regulación emocional generan tensión. "
    "A veces lo que deseas expandir no coincide con lo que emocionalmente puedes sostener.\n\n"

    "Puedes sentir que el crecimiento desregula emocionalmente "
    "o que ciertos estados emocionales frenan tu capacidad de avanzar."
),

("Júpiter", "Luna", "☍"): (
    "Júpiter oposición Luna: expansión y regulación emocional tienden a competir entre sí. "
    "Cuando te abres a nuevas experiencias o posibilidades, puede costarte mantener estabilidad emocional. "
    "Cuando necesitas recogimiento o regulación, la expansión pierde fuerza.\n\n"

    "Necesitas aprender a reconocer cuándo priorizar apertura y cuándo priorizar cuidado."
),

("Júpiter", "Luna", "△"): (
    "Júpiter trígono Luna: crecimiento y regulación emocional suelen colaborar de forma natural. "
    "Puedes abrirte a nuevas experiencias sin perder fácilmente estabilidad interna."
),

("Júpiter", "Luna", "✶"): (
    "Júpiter sextil Luna: existe compatibilidad entre apertura emocional y crecimiento. "
    "Cuando desarrollas ambos conscientemente, pueden apoyarse mutuamente."
),

# ── Saturno – Sol ─────────────────────────────────────────────────────────────

("Saturno", "Sol", "="): (
    "Saturno en conjunción con el Sol: dirección vital y necesidad de estructura están profundamente unidas. "
    "Tiendes a tomarte en serio lo que construyes y a desarrollar identidad a través del esfuerzo, la responsabilidad o la consistencia.\n\n"

    "El riesgo aparece cuando la exigencia estructural ocupa tanto espacio "
    "que la dirección termina reducida únicamente a sostener obligaciones."
),

("Saturno", "Sol", "□"): (
    "Saturno cuadratura Sol: dirección y estructura generan tensión persistente. "
    "Puedes sentir que una parte de ti quiere avanzar mientras otra duda, limita o exige más preparación.\n\n"

    "A veces la estructura frena el desarrollo; "
    "otras veces intentas avanzar más rápido de lo que realmente puedes sostener."
),

("Saturno", "Sol", "☍"): (
    "Saturno oposición Sol: dirección y estructura tienden a tirar en sentidos diferentes. "
    "Cuando avanzas hacia lo que quieres desarrollar, puedes sentir peso, límite o resistencia. "
    "Cuando priorizas estabilidad o control, la dirección vital pierde fuerza.\n\n"

    "Necesitas aprender a construir sin apagar completamente el impulso vital."
),

("Saturno", "Sol", "△"): (
    "Saturno trígono Sol: dirección y estructura colaboran con relativa estabilidad. "
    "Suele existir capacidad para sostener procesos largos, construir con coherencia "
    "y desarrollar algo de forma consistente."
),

("Saturno", "Sol", "✶"): (
    "Saturno sextil Sol: existe buena compatibilidad entre dirección y estructura. "
    "Cuando desarrollas ambos conscientemente, pueden fortalecerse mutuamente."
),

# ── Saturno – Luna ────────────────────────────────────────────────────────────

("Saturno", "Luna", "="): (
    "Saturno en conjunción con la Luna: regulación emocional y necesidad de estructura están muy unidas. "
    "Tiendes a contener, controlar o administrar cuidadosamente lo emocional.\n\n"

    "El riesgo aparece cuando la contención sustituye el procesamiento emocional "
    "y ciertas necesidades quedan demasiado restringidas."
),

("Saturno", "Luna", "□"): (
    "Saturno cuadratura Luna: estructura y regulación emocional están en tensión. "
    "Puedes sentir que necesitas controlarte para sostener estabilidad "
    "o que lo emocional interrumpe la estructura que intentas construir.\n\n"

    "La dificultad suele estar en permitir emoción sin perder sostén "
    "y sostén sin bloquear completamente la emoción."
),

("Saturno", "Luna", "☍"): (
    "Saturno oposición Luna: necesidad emocional y necesidad de estructura compiten entre sí. "
    "Cuando priorizas control, responsabilidad o estabilidad, puede costarte acceder a lo emocional. "
    "Cuando lo emocional ocupa más espacio, sostener estructura se vuelve más difícil.\n\n"

    "Necesitas aprender cuándo contener y cuándo permitir mayor flexibilidad emocional."
),

("Saturno", "Luna", "△"): (
    "Saturno trígono Luna: regulación emocional y estructura suelen colaborar bien. "
    "Existe capacidad para sostener emocionalmente procesos largos "
    "sin perder fácilmente estabilidad interna."
),

("Saturno", "Luna", "✶"): (
    "Saturno sextil Luna: emoción y estructura pueden integrarse de forma constructiva. "
    "Cuando desarrollas ambos conscientemente, pueden apoyarse mutuamente."
),

}

# ─── CÁLCULO ASTROLÓGICO ──────────────────────────────────────────────────────

def geocodificar(ciudad):
    g = Nominatim(user_agent="ai_planetas_sociales", timeout=10)
    loc = g.geocode(ciudad, language="es")
    if not loc:
        raise ValueError(f"No se encontró la ciudad: {ciudad}")
    return loc.latitude, loc.longitude

def obtener_timezone(lat, lon):
    tf = TimezoneFinder()
    tz = tf.timezone_at(lat=lat, lng=lon)
    if not tz:
        raise ValueError("No se pudo determinar la zona horaria")
    return tz

def fecha_a_jd(anio, mes, dia, hora, minuto, tz_name):
    tz = pytz.timezone(tz_name)
    dt = tz.localize(datetime(anio, mes, dia, hora, minuto))
    dt_utc = dt.astimezone(pytz.utc)
    h = dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0
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

def _chiron_kepler(jd):
    jd_peri, period, e, peri_lon = 2450128.5, 18412.3, 0.383, 188.76
    M = math.radians(((jd - jd_peri) / period * 360.0) % 360.0)
    E = M
    for _ in range(50):
        dE = (M - E + e * math.sin(E)) / (1.0 - e * math.cos(E))
        E += dE
        if abs(dE) < 1e-10:
            break
    f = 2.0 * math.atan(math.sqrt((1 + e) / (1 - e)) * math.tan(E / 2.0))
    return (math.degrees(f) + peri_lon) % 360.0

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
        planetas[nombre] = {
            "simbolo": simbolo, "lon": pos[0], "signo": signo,
            "grado": grado, "retrogrado": pos[3] < 0
        }

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


    pos_li, _ = swe.calc_ut(jd, LILITH_ID, FLAGS)
    signo_li, grado_li = grados_a_signo(pos_li[0])
    planetas["Lilith"] = {
        "simbolo": "⚸", "lon": pos_li[0], "signo": signo_li,
        "grado": grado_li, "retrogrado": False
    }

    pos_nn, _ = swe.calc_ut(jd, swe.TRUE_NODE, FLAGS)
    signo_nn, grado_nn = grados_a_signo(pos_nn[0])
    lon_ns = (pos_nn[0] + 180) % 360
    signo_ns, grado_ns = grados_a_signo(lon_ns)
    planetas["Nodo Norte"] = {
        "simbolo": "☊", "lon": pos_nn[0], "signo": signo_nn,
        "grado": grado_nn, "retrogrado": False
    }
    planetas["Nodo Sur"] = {
        "simbolo": "☋", "lon": lon_ns, "signo": signo_ns,
        "grado": grado_ns, "retrogrado": False
    }

    cuspides, ascmc = swe.houses(jd, lat, lon, b'P')
    asc_lon, mc_lon = ascmc[0], ascmc[1]
    signo_asc, grado_asc = grados_a_signo(asc_lon)
    signo_mc,  grado_mc  = grados_a_signo(mc_lon)

    def casa_de(p_lon):
        for i in range(12):
            c_ini = cuspides[i]
            c_fin = cuspides[(i + 1) % 12]
            if c_ini <= c_fin:
                if c_ini <= p_lon < c_fin: return i + 1
            else:
                if p_lon >= c_ini or p_lon < c_fin: return i + 1
        return 12

    for nombre_planeta in planetas:
        planetas[nombre_planeta]["casa"] = casa_de(planetas[nombre_planeta]["lon"])

    return {
        "planetas": planetas,
        "cuspides": list(cuspides),
        "asc": {"lon": asc_lon, "signo": signo_asc, "grado": grado_asc},
        "mc":  {"lon": mc_lon,  "signo": signo_mc,  "grado": grado_mc},
        "jd":  jd,
    }


def calcular_aspectos_sociales(planetas):
    """Calcula aspectos de Júpiter y Saturno con personales."""

    ASPECTOS = {
        0:   ("Conjunción", "=", 10),
        60:  ("Sextil", "✶", 6),
        90:  ("Cuadratura", "□", 8),
        120: ("Trígono", "△", 8),
        180: ("Oposición", "☍", 8),
    }

    pares = [
        ("Júpiter", "Saturno"),
        ("Júpiter", "Sol"),
        ("Júpiter", "Luna"),
        ("Júpiter", "Mercurio"),
        ("Júpiter", "Venus"),
        ("Júpiter", "Marte"),
        ("Júpiter", "Quirón"),
        ("Saturno", "Sol"),
        ("Saturno", "Luna"),
        ("Saturno", "Mercurio"),
        ("Saturno", "Venus"),
        ("Saturno", "Marte"),
        ("Saturno", "Quirón"),
    ]

    aspectos = []

    for p1_nom, p2_nom in pares:
        p1 = planetas.get(p1_nom)
        p2 = planetas.get(p2_nom)

        if not p1 or not p2:
            continue

        diff = abs(p1["lon"] - p2["lon"]) % 360
        if diff > 180:
            diff = 360 - diff

        for angulo, (tipo, simbolo, orbe_max) in ASPECTOS.items():

            orbe_real = orbe_max

            if (
                simbolo == "☍"
                and (p1_nom in ("Sol", "Luna") or p2_nom in ("Sol", "Luna"))
            ):
                orbe_real = 10

            orbe_val = round(abs(diff - angulo), 2)

            if orbe_val <= orbe_real:
                aspectos.append({
                    "p1": p1_nom,
                    "p2": p2_nom,
                    "tipo": tipo,
                    "nombre": tipo,
                    "simbolo": simbolo,
                    "orbe": orbe_val,
                    "relevancia": "exacto" if orbe_val <= 1.0 else "estructural",
                })
                break

    return sorted(aspectos, key=lambda x: x["orbe"])

# ─── TEXTOS DE SECCIÓN ────────────────────────────────────────────────────────

def _get_asp(aspectos, p1, p2):
    return next(
        (a for a in aspectos
         if (a["p1"] == p1 and a["p2"] == p2) or (a["p1"] == p2 and a["p2"] == p1)),
        None
    )


def _texto_asp(p1, p2, asp):
    if asp is None:
        return None
    clave1 = (p1, p2, asp["simbolo"])
    clave2 = (p2, p1, asp["simbolo"])
    return ASPECTOS_SOCIALES.get(clave1) or ASPECTOS_SOCIALES.get(clave2)


def texto_estructura_general(carta, aspectos):
    planetas = carta["planetas"]
    jup = planetas.get("Júpiter", {})
    sat = planetas.get("Saturno", {})

    jup_sig  = jup.get("signo", "")
    jup_casa = jup.get("casa", "")
    sat_sig  = sat.get("signo", "")
    sat_casa = sat.get("casa", "")

    elem_jup = ELEMENTO_SIGNO.get(jup_sig, "")
    elem_sat = ELEMENTO_SIGNO.get(sat_sig, "")

    texto = (
        f"Júpiter está en {jup_sig}, Casa {jup_casa}: "
        f"muestra cómo tiendes a crecer, abrir posibilidades y ampliar tu relación con el mundo.\n"
        f"Saturno está en {sat_sig}, Casa {sat_casa}: "
        f"muestra cómo tiendes a estructurarte, sostener límites y construir estabilidad."
    )

    if elem_jup == elem_sat:
        texto += (
            f"\n\nExpansión y estructura operan en el mismo elemento ({elem_jup}). "
            f"Esto suele facilitar que crecimiento y sostén compartan un mismo lenguaje interno. "
            f"Cuando están alineados, pueden reforzarse mucho; cuando se desequilibran, "
            f"también pueden intensificar el mismo exceso."
        )
    elif {elem_jup, elem_sat} in ({"Fuego", "Aire"}, {"Tierra", "Agua"}):
        texto += (
            f"\n\nExpansión ({jup_sig}, {elem_jup}) y estructura ({sat_sig}, {elem_sat}) "
            f"operan en elementos compatibles. Esto puede facilitar que crecimiento y sostén "
            f"colaboren con relativa naturalidad, aunque cada uno tenga un ritmo distinto."
        )
    else:
        texto += (
            f"\n\nExpansión ({jup_sig}, {elem_jup}) y estructura ({sat_sig}, {elem_sat}) "
            f"operan en elementos que crean tensión. Puede haber momentos en los que crecer "
            f"y sostenerte requieran movimientos internos diferentes, por lo que la integración "
            f"necesita más atención consciente."
        )

    asp_textos = []
    for p1, p2 in [
        ("Júpiter", "Saturno"),

        ("Júpiter", "Sol"),
        ("Júpiter", "Luna"),
        ("Júpiter", "Mercurio"),
        ("Júpiter", "Venus"),
        ("Júpiter", "Marte"),

        ("Saturno", "Sol"),
        ("Saturno", "Luna"),
        ("Saturno", "Mercurio"),
        ("Saturno", "Venus"),
        ("Saturno", "Marte"),
    ]:
        asp = _get_asp(aspectos, p1, p2)
        if asp:
            asp_textos.append(f"{p1}–{p2} en {asp['tipo'].lower()} (orbe {asp['orbe']}°)")

    if asp_textos:
        texto += f"\n\nAspectos relevantes: {', '.join(asp_textos)}."

    return texto

def texto_jupiter(carta, aspectos):
    planetas = carta["planetas"]
    jup  = planetas.get("Júpiter", {})
    sig  = jup.get("signo", "")
    casa = jup.get("casa", 1)
    ret  = jup.get("retrogrado", False)

    t = JUPITER_SIGNO.get(sig, "")
    t += "\n\n" + JUPITER_CASA.get(casa, "")

    if ret:
        t += (
            "\n\nJúpiter está retrógrado. El crecimiento tiende a desarrollarse "
            "de forma más interna y menos visible externamente al principio. "
            "Puedes necesitar más tiempo para traducir expansión o comprensión "
            "en movimientos concretos hacia fuera."
        )

    for p2 in (
        "Sol",
        "Luna",
        "Mercurio",
        "Venus",
        "Marte",
    ):
        asp = _get_asp(aspectos, "Júpiter", p2)
        t_asp = _texto_asp("Júpiter", p2, asp)
        if t_asp:
            t += f"\n\n{t_asp}"

    return t


def texto_saturno(carta, aspectos):
    planetas = carta["planetas"]

    sat  = planetas.get("Saturno", {})
    sig  = sat.get("signo", "")
    casa = sat.get("casa", 1)
    ret  = sat.get("retrogrado", False)

    t = SATURNO_SIGNO.get(sig, "")
    t += "\n\n" + SATURNO_CASA.get(casa, "")

    if ret:
        t += (
            "\n\nSaturno está retrógrado. La construcción de estructura suele desarrollarse "
            "de forma más interna y menos visible desde fuera al principio. "
            "Puedes necesitar tiempo antes de mostrar externamente algo que por dentro "
            "todavía estás consolidando."
        )

    for p2 in (
        "Sol",
        "Luna",
        "Mercurio",
        "Venus",
        "Marte",
    ):

        asp = _get_asp(aspectos, "Saturno", p2)
        t_asp = _texto_asp("Saturno", p2, asp)

        if t_asp:
            t += f"\n\n{t_asp}"

    return t


def texto_integracion(carta, aspectos):
    planetas = carta["planetas"]
    jup = planetas.get("Júpiter", {})
    sat = planetas.get("Saturno", {})

    jup_sig = jup.get("signo", "")
    sat_sig = sat.get("signo", "")

    elem_jup = ELEMENTO_SIGNO.get(jup_sig, "")
    elem_sat = ELEMENTO_SIGNO.get(sat_sig, "")

    partes = []

    asp_js = _get_asp(aspectos, "Júpiter", "Saturno")
    if asp_js:
        t_asp = _texto_asp("Júpiter", "Saturno", asp_js)
        if t_asp:
            partes.append(t_asp)
    else:
        if {elem_jup, elem_sat} not in ({"Fuego","Aire"}, {"Tierra","Agua"}) and elem_jup != elem_sat:
            partes.append(
                f"Júpiter en {jup_sig} ({elem_jup}) y Saturno en {sat_sig} ({elem_sat}) "
                f"no forman aspecto directo, pero operan en elementos que crean tensión. "
                f"Esto puede hacer que crecer y sostenerte requieran movimientos internos diferentes. "
                f"La expansión y la estructura no se alimentan de forma automática; "
                f"necesitas integrarlas de manera consciente para no abrir posibilidades sin sostén "
                f"ni construir estructuras sin crecimiento real."
            )
        else:
            partes.append(
                f"Júpiter en {jup_sig} y Saturno en {sat_sig} no forman aspecto directo "
                f"y operan en elementos compatibles. "
                f"La integración entre crecimiento y estructura tiene menor fricción de base. "
                f"Precisamente por eso, conviene no asumir que se regulan solas: "
                f"puedes entrar en sobreextensión o en rigidez progresiva sin detectarlo "
                f"hasta que el coste ya es alto."
            )

    JUP_EXCESO = {
        "Fuego":  "puedes iniciar más de lo que realmente puedes sostener, dispersando energía en varios frentes sin completar ninguno",
        "Tierra": "puedes acumular más de lo que puedes gestionar, generando peso sin avance real",
        "Aire":   "puedes multiplicar perspectivas, ideas y conexiones sin que ninguna llegue a profundizar o tomar forma",
        "Agua":   "puedes absorber demasiado emocionalmente hasta perder la referencia de lo propio",
    }

    SAT_EXCESO = {
        "Fuego":  "la acción puede frenarse antes de producir resultado y la vitalidad queda contenida demasiado pronto",
        "Tierra": "puedes acumular tanta estructura que la forma termina impidiendo el movimiento",
        "Aire":   "la organización puede volverse tan densa que la comunicación y el intercambio se ralentizan",
        "Agua":   "la contención puede suprimir lo que necesita circular, y lo no expresado se acumula",
    }

    partes.append(
        f"Cuando Júpiter domina: {JUP_EXCESO.get(elem_jup, 'la expansión puede superar la capacidad de sostén')}. "
        f"La estructura de Saturno en {sat_sig} no compensa con suficiente rapidez "
        f"y lo que ganas en amplitud empieza a perder forma.\n\n"
        f"Cuando Saturno domina: {SAT_EXCESO.get(elem_sat, 'la estructura puede restringir demasiado el crecimiento')}. "
        f"La expansión de Júpiter en {jup_sig} no encuentra espacio para activarse "
        f"y puedes mantener lo que ya existe sin crecer hacia lo que sería posible."
    )

  

    # ── Bucle de retroalimentación ──────────────────────────────────────────────

    SAT_CEDE = {
        "Fuego":  "el ritmo de acción supera la capacidad real de organización",
        "Tierra": "pierdes estructura antes de haber construido una nueva base que la sustituya",
        "Aire":   "los acuerdos, ideas o referencias que daban orden empiezan a fragmentarse",
        "Agua":   "los límites emocionales se diluyen y deja de existir suficiente contención",
    }

    JUP_SIN_FORMA = {
        "Fuego":  "abres múltiples direcciones al mismo tiempo sin terminar de consolidar ninguna",
        "Tierra": "acumulas carga, tareas o responsabilidades sin que exista una estructura clara que las sostenga",
        "Aire":   "multiplicas conexiones, ideas o perspectivas sin que lleguen a integrarse de forma coherente",
        "Agua":   "absorbes demasiado de lo que ocurre alrededor sin poder procesarlo o diferenciarlo bien",
    }

    partes.append(
        f"Bajo presión suele aparecer una secuencia bastante reconocible. "
        f"Primero, Saturno en {sat_sig} empieza a ceder: "
        f"{SAT_CEDE.get(elem_sat, 'la estructura empieza a perder estabilidad')}. "
        f"Después, Júpiter en {jup_sig} ocupa ese espacio: "
        f"{JUP_SIN_FORMA.get(elem_jup, 'la expansión aumenta sin suficiente sostén')}. "
        f"Desde ahí puedes intentar recuperar estabilidad rápidamente, "
        f"pero lo que construyes en ese estado suele ser más rígido, reactivo o agotador de sostener. "
        f"Si el patrón no se reconoce a tiempo, el ciclo tiende a repetirse."
    )

    return "\n\n".join(partes)


def texto_orientacion(carta, aspectos):
    planetas = carta["planetas"]

    jup = planetas.get("Júpiter", {})
    sat = planetas.get("Saturno", {})

    jup_sig  = jup.get("signo", "")
    jup_casa = jup.get("casa", 1)

    sat_sig  = sat.get("signo", "")
    sat_casa = sat.get("casa", 1)

    elem_jup = ELEMENTO_SIGNO.get(jup_sig, "")
    elem_sat = ELEMENTO_SIGNO.get(sat_sig, "")

    # ── Desde dónde empezar ───────────────────────────────────────────────────

    orden_activacion = {
        "Fuego": 0,
        "Aire": 1,
        "Tierra": 2,
        "Agua": 3
    }

    if orden_activacion.get(elem_jup, 2) <= orden_activacion.get(elem_sat, 2):
        entrada_nombre = "expansión"
        entrada_sig    = jup_sig
        entrada_casa   = jup_casa
        entrada_elem   = elem_jup
    else:
        entrada_nombre = "estructura"
        entrada_sig    = sat_sig
        entrada_casa   = sat_casa
        entrada_elem   = elem_sat

    inicio_detail = {
        "Fuego":  "activar movimiento antes de tener todo completamente resuelto",
        "Aire":   "poner en palabras, compartir o mover lo que ya está disponible",
        "Tierra": "llevar lo que ocurre a algo concreto, verificable y práctico",
        "Agua":   "dar tiempo y espacio suficiente para registrar lo que está ocurriendo",
    }

    desde_donde = (
        f"El punto de entrada más accesible suele estar en la {entrada_nombre} "
        f"({entrada_sig}, Casa {entrada_casa}). "
        f"De las dos funciones, esta requiere menos resistencia para activarse. "
        f"La forma más natural de empezar es "
        f"{inicio_detail.get(entrada_elem, 'seguir el movimiento natural de esta función')}. "
        f"Cuando todo parece bloqueado, comenzar por aquí suele facilitar "
        f"que la otra función también pueda ponerse en marcha."
    )

    # ── Qué sostener ──────────────────────────────────────────────────────────

    sostener_detail = {
        "Fuego":  "recordar el objetivo que da sentido al esfuerzo",
        "Tierra": "mantener una estructura concreta aunque sea pequeña o sencilla",
        "Aire":   "sostener acuerdos, referencias y claridad en el intercambio",
        "Agua":   "mantener límites emocionales suficientes para no saturarte",
    }

    sostener = (
        f"Lo más importante de sostener aparece en Saturno "
        f"({sat_sig}, Casa {sat_casa}). "
        f"Bajo presión puedes abrir posibilidades o reaccionar antes de mantener forma estable. "
        f"Conviene cuidar especialmente "
        f"{sostener_detail.get(elem_sat, 'la estructura básica que sostiene estabilidad')}. "
        f"Muchas veces la primera señal de desgaste aparece cuando sigues haciendo cosas, "
        f"pero ya no existe suficiente estructura para sostenerlas bien."
    )

    # ── Qué evitar ────────────────────────────────────────────────────────────

    asp_js = _get_asp(aspectos, "Júpiter", "Saturno")

    if asp_js and asp_js["simbolo"] in ("□", "☍"):

        evitar = (
            f"Conviene evitar alternar entre abrir posibilidades sin sostén "
            f"y sostener estructura sin permitir crecimiento. "
            f"Con Júpiter–Saturno en {asp_js['tipo'].lower()}, "
            f"crecimiento y estructura no siempre pueden sostenerse "
            f"al mismo nivel de intensidad al mismo tiempo. "
            f"Suele ayudar más reconocer qué necesita atención en cada momento "
            f"que intentar mantener equilibrio constante en todo."
        )

    elif asp_js and asp_js["simbolo"] == "=":

        evitar = (
            f"Conviene evitar confundir expansión con estabilidad real. "
            f"Con Júpiter–Saturno en conjunción, crecimiento y estructura operan muy unidos "
            f"y la sobreextensión puede parecer estabilidad hasta que aparecen los límites."
        )

    elif {elem_jup, elem_sat} not in (
        {"Fuego","Aire"},
        {"Tierra","Agua"}
    ) and elem_jup != elem_sat:

        evitar = (
            f"Conviene evitar que la función más activa en cada momento desplace completamente a la otra. "
            f"Con Júpiter en {jup_sig} ({elem_jup}) y Saturno en {sat_sig} ({elem_sat}), "
            f"crecimiento y estructura no se activan automáticamente juntos. "
            f"Necesitas reconocer conscientemente cuándo hace falta abrir más espacio "
            f"y cuándo hace falta construir más sostén."
        )

    else:

        evitar = (
            f"Conviene evitar asumir que la compatibilidad entre crecimiento y estructura "
            f"garantiza integración automática. "
            f"Cuando no existe fricción visible, ciertos desequilibrios pueden acumularse "
            f"durante bastante tiempo antes de hacerse evidentes."
        )

    # ── Si no se integra ──────────────────────────────────────────────────────

    si_no = (
        "Cuando crecimiento y estructura dejan de colaborar, "
        "puede aparecer expansión sin suficiente sostén "
        "o estabilidad sin movimiento real. "
        "En ambos casos se pierde parte de lo que realmente podría desarrollarse "
        "si ambas funciones trabajaran en la misma dirección."
    )

    # ── Primera señal ─────────────────────────────────────────────────────────

    SENAL_DETAIL = {
        "Fuego":  "el ritmo aumenta más rápido que la capacidad de consolidar",
        "Tierra": "la acumulación empieza a superar la capacidad real de gestión",
        "Aire":   "los acuerdos, referencias o intercambios empiezan a fragmentarse",
        "Agua":   "los límites emocionales dejan de contener suficientemente",
    }

    senal = (
        f"La primera señal suele aparecer en Saturno ({sat_sig}): "
        f"{SENAL_DETAIL.get(elem_sat, 'la estructura empieza a perder estabilidad')}. "
        f"Cuando eso ocurre, Júpiter ({jup_sig}) tiende a ocupar rápidamente el espacio disponible "
        f"y la expansión puede acelerarse más de lo que realmente puedes sostener. "
        f"Detectar la señal temprano suele evitar entrar en ciclos más agotadores."
    )

    return {
        "desde_donde": desde_donde,
        "sostener":    sostener,
        "evitar":      evitar,
        "si_no":       si_no,
        "senal":       senal,
    }


# ─── GENERACIÓN LATEX ─────────────────────────────────────────────────────────

def esc(texto):
    if not texto:
        return ""
    for orig, repl in [
        ('\\', r'\textbackslash{}'),
        ('&', r'\&'), ('%', r'\%'), ('$', r'\$'), ('#', r'\#'),
        ('_', r'\_'), ('{', r'\{'), ('}', r'\}'),
        ('~', r'\textasciitilde{}'),
    ]:
        texto = texto.replace(orig, repl)
    return texto


def generar_latex(carta, nombre, anio, mes, dia, hora, minuto,
                  ciudad, lat, lon, tz_name, ruta_rueda, aspectos):
    planetas  = carta["planetas"]
    asc       = carta["asc"]
    mc        = carta["mc"]
    jup  = planetas.get("Júpiter",  {})
    sat  = planetas.get("Saturno",  {})
    sol  = planetas.get("Sol",      {})
    luna = planetas.get("Luna",     {})
    mercurio = planetas.get("Mercurio", {})
    venus    = planetas.get("Venus",    {})
    marte    = planetas.get("Marte",    {})

    fecha_str = f"{dia:02d}/{mes:02d}/{anio}"
    hora_str  = f"{hora:02d}:{minuto:02d}"
    tz_obj    = pytz.timezone(tz_name)
    dt_local  = tz_obj.localize(datetime(anio, mes, dia, hora, minuto))
    utc_off   = dt_local.strftime("%z")
    utc_str   = f"UTC{utc_off[:3]}:{utc_off[3:]}"
    nom_esc   = esc(nombre)
    ciu_esc   = esc(ciudad)

    def signo_casa(p):
        return f"{esc(p.get('signo',''))} — Casa {p.get('casa','')} {grado_a_dms(p.get('grado',0))}"

    t_gral  = texto_estructura_general(carta, aspectos)
    t_jup   = texto_jupiter(carta, aspectos)
    t_sat   = texto_saturno(carta, aspectos)
    t_integ = texto_integracion(carta, aspectos)
    t_or    = texto_orientacion(carta, aspectos)

    _ASP_TEX = {"=":"conj","☍":"opo","□":"cua","△":"tri","✶":"sex"}
    asp_rows = ""
    for a in aspectos:
        asp_rows += (
            f"  {esc(a['p1'])} & {esc(_ASP_TEX.get(a['simbolo'], a['simbolo']))} & "
            f"{esc(a['p2'])} & {esc(a['tipo'])} & {a['orbe']:.1f}° \\\\\n"
        )

    if asp_rows.strip():
        tabla_aspectos = (
            "\\begin{center}\n"
            "\\begin{tabular}{lllll}\n"
            "  \\toprule\n"
            "  \\textbf{Planeta 1} & \\textbf{Asp.} & \\textbf{Planeta 2} "
            "& \\textbf{Tipo} & \\textbf{Orbe} \\\\\n"
            "  \\midrule\n"
            f"{asp_rows}"
            "  \\bottomrule\n"
            "\\end{tabular}\n"
            "\\end{center}"
        )
    else:
        tabla_aspectos = "\\vspace{0.3cm}\\textit{No hay aspectos en los orbes definidos.}"

    def parrafos(texto):
        return "\n\n".join(esc(p) for p in texto.split("\n\n") if p.strip())

    ret_jup = " (Retrógrado)" if jup.get("retrogrado") else ""
    ret_sat = " (Retrógrado)" if sat.get("retrogrado") else ""

    latex = f"""\\documentclass[11pt,a4paper]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[T1]{{fontenc}}
\\usepackage{{tgpagella}}
\\usepackage[spanish]{{babel}}
\\usepackage{{geometry}}
\\usepackage{{booktabs}}
\\usepackage{{xcolor}}
\\usepackage{{titlesec}}
\\usepackage{{fancyhdr}}
\\usepackage[parfill]{{parskip}}
\\usepackage[expansion=false]{{microtype}}
\\usepackage{{hyperref}}
\\usepackage{{setspace}}
\\usepackage{{needspace}}
\\usepackage{{graphicx}}
\\widowpenalty=10000
\\clubpenalty=10000
\\displaywidowpenalty=10000

\\geometry{{top=3.0cm,bottom=3.0cm,left=3.5cm,right=3.5cm}}
\\setlength{{\\parskip}}{{0.65em}}
\\setlength{{\\parindent}}{{0em}}

\\definecolor{{azulai}}{{RGB}}{{30,80,140}}
\\definecolor{{doradoai}}{{RGB}}{{140,90,0}}
\\definecolor{{grisai}}{{RGB}}{{70,70,70}}

\\titleformat{{\\section}}{{\\Large\\bfseries\\color{{azulai}}}}{{}}{{0em}}{{}}[{{\\color{{azulai}}\\titlerule[0.5pt]}}]
\\titlespacing*{{\\section}}{{0pt}}{{1.8em}}{{0.8em}}
\\titleformat{{\\subsection}}{{\\large\\bfseries\\color{{doradoai}}}}{{}}{{0em}}{{}}
\\titlespacing*{{\\subsection}}{{0pt}}{{1.4em}}{{0.5em}}
\\titleformat{{\\subsubsection}}{{\\normalsize\\bfseries\\color{{grisai}}}}{{}}{{0em}}{{}}
\\titlespacing*{{\\subsubsection}}{{0pt}}{{1.0em}}{{0.3em}}

\\pagestyle{{fancy}}\\fancyhf{{}}
\\rhead{{\\textcolor{{grisai}}{{\\small {nom_esc} — Arquitectura Interna}}}}
\\lhead{{\\textcolor{{grisai}}{{\\small Júpiter · Saturno}}}}
\\cfoot{{\\textcolor{{grisai}}{{\\small\\thepage}}}}
\\renewcommand{{\\headrulewidth}}{{0.3pt}}

\\hypersetup{{colorlinks=true,linkcolor=azulai,urlcolor=azulai}}
\\setstretch{{1.45}}
\\tolerance=1500
\\emergencystretch=4em

\\begin{{document}}

% ── Portada ──────────────────────────────────────────────────────────────────

\\begin{{titlepage}}
\\centering

\\vspace*{{2cm}}

{{\\Huge\\bfseries\\color{{azulai}} Júpiter · Saturno}}\\\\[0.4cm]

{{\\large\\color{{grisai}} Arquitectura Interna}}\\\\[0.25cm]

{{\\small\\itshape\\color{{grisai}}
Crecimiento, estructura y organización interna
}}\\\\[1.8cm]

{{\\huge\\color{{doradoai}} {nom_esc}}}\\\\[1.2cm]

{{\\Large {fecha_str} \\quad {hora_str}}}\\\\[0.25cm]

{{\\Large {ciu_esc}}}\\\\[0.25cm]

{{\\normalsize
Lat: {lat:.4f}° \\quad
Lon: {lon:.4f}° \\quad
{utc_str}
}}\\\\[0.4cm]

{{\\normalsize
Ascendente: {esc(asc['signo'])} {grado_a_dms(asc['grado'])}
\\quad
MC: {esc(mc['signo'])} {grado_a_dms(mc['grado'])}
}}\\\\[1.6cm]

\\begin{{tabular}}{{ll}}
\\textbf{{Júpiter:}} & {signo_casa(jup)}{ret_jup} \\\\
\\textbf{{Saturno:}} & {signo_casa(sat)}{ret_sat} \\\\
\\end{{tabular}}

\\vfill

{{\\small\\color{{grisai}}
Generado el {datetime.now().strftime("%d/%m/%Y")}
}}

\\end{{titlepage}}

\tableofcontents
\vspace{{0.8cm}}

% ── Datos de referencia ──────────────────────────────────────────────────────

\\section{{Datos de referencia}}

\\begin{{center}}
\\begin{{tabular}}{{llll}}
\\toprule
\\textbf{{Punto}} & \\textbf{{Signo}} & \\textbf{{Casa}} & \\textbf{{Posición}} \\\\
\\midrule

Júpiter{ret_jup} &
{esc(jup.get('signo',''))} &
Casa {jup.get('casa','')} &
{grado_a_dms(jup.get('grado',0))} \\\\

Saturno{ret_sat} &
{esc(sat.get('signo',''))} &
Casa {sat.get('casa','')} &
{grado_a_dms(sat.get('grado',0))} \\\\

Sol &
{esc(sol.get('signo',''))} &
Casa {sol.get('casa','')} &
{grado_a_dms(sol.get('grado',0))} \\\\

Luna &
{esc(luna.get('signo',''))} &
Casa {luna.get('casa','')} &
{grado_a_dms(luna.get('grado',0))} \\\\

Mercurio &
{esc(mercurio.get('signo',''))} &
Casa {mercurio.get('casa','')} &
{grado_a_dms(mercurio.get('grado',0))} \\\\

Venus &
{esc(venus.get('signo',''))} &
Casa {venus.get('casa','')} &
{grado_a_dms(venus.get('grado',0))} \\\\

Marte &
{esc(marte.get('signo',''))} &
Casa {marte.get('casa','')} &
{grado_a_dms(marte.get('grado',0))} \\\\

Ascendente &
{esc(asc['signo'])} &
--- &
{grado_a_dms(asc['grado'])} \\\\

Medio Cielo &
{esc(mc['signo'])} &
--- &
{grado_a_dms(mc['grado'])} \\\\

\\bottomrule
\\end{{tabular}}
\\end{{center}}

\\vspace{{0.8cm}}

\\subsection*{{Aspectos entre funciones}}

{tabla_aspectos}

\\vspace{{1cm}}

\\begin{{center}}
\\includegraphics[width=0.72\\textwidth]{{{os.path.basename(ruta_rueda)}}}
\\end{{center}}

\\vspace{{0.8cm}}
\\Needspace{{5\\baselineskip}}


% ── Interpretación ───────────────────────────────────────────────────────────

\\section{{Interpretación — Arquitectura Interna}}

\\begin{{center}}
{{\\small\\itshape
No se trata de definir quién eres.\\\\
Se trata de observar cómo tiendes a crecer, estructurarte\\\\
y sostener tu relación con el mundo.
}}
\\end{{center}}

\\vspace{{0.8cm}}
\\Needspace{{5\\baselineskip}}

% ── 1. Estructura general ────────────────────────────────────────────────────

\\subsection{{1. Estructura general}}

{parrafos(t_gral)}

\\vspace{{0.8cm}}
\\Needspace{{5\\baselineskip}}

% ── 2. Júpiter ───────────────────────────────────────────────────────────────

\\subsection{{2. Júpiter — Expansión y crecimiento}}

\\subsubsection*{{
Júpiter en {esc(jup.get('signo',''))}
— Casa {jup.get('casa','')}{ret_jup}
}}

{parrafos(t_jup)}

\\vspace{{0.8cm}}
\\Needspace{{5\\baselineskip}}

% ── 3. Saturno ───────────────────────────────────────────────────────────────

\\subsection{{3. Saturno — Estructura y sostén}}

\\subsubsection*{{
Saturno en {esc(sat.get('signo',''))}
— Casa {sat.get('casa','')}{ret_sat}
}}

{parrafos(t_sat)}

\\vspace{{0.8cm}}
\\Needspace{{5\\baselineskip}}

% ── 4. Integración ───────────────────────────────────────────────────────────

\\subsection{{4. Integración — Crecimiento y estructura}}

{parrafos(t_integ)}

\\vspace{{0.8cm}}
\\Needspace{{5\\baselineskip}}

% ── 5. Orientación práctica ──────────────────────────────────────────────────

\\subsection{{5. Orientación práctica}}

\\subsubsection*{{Desde dónde empezar}}

{parrafos(t_or['desde_donde'])}

\\subsubsection*{{Qué sostener}}

{parrafos(t_or['sostener'])}

\\subsubsection*{{Qué evitar}}

{parrafos(t_or['evitar'])}

\\subsubsection*{{Si no se integra}}

{parrafos(t_or['si_no'])}

\\subsubsection*{{Señal temprana}}

{parrafos(t_or['senal'])}

\\vfill

\\begin{{center}}
{{\\small\\itshape\\color{{grisai}}
La astrología se utiliza aquí como herramienta simbólica de observación\\\\
y no como una definición cerrada de la persona.
}}
\\end{{center}}

\\end{{document}}
"""

    return latex


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print("═" * 57)
    print("  JÚPITER · SATURNO — Arquitectura Interna")
    print("═" * 57)
    print()

    nombre = input("Nombre completo: ").strip()
    if not nombre:
        print("El nombre no puede estar vacío."); sys.exit(1)

    while True:
        try:
            partes = input("Fecha de nacimiento (DD/MM/AAAA): ").strip().split("/")
            dia, mes, anio = int(partes[0]), int(partes[1]), int(partes[2])
            datetime(anio, mes, dia)
            break
        except Exception:
            print("Formato incorrecto. Usa DD/MM/AAAA")

    while True:
        try:
            hora = int(input("Hora de nacimiento (0-23): ").strip())
            if 0 <= hora <= 23: break
            print("Valor entre 0 y 23.")
        except ValueError:
            print("Introduce un número entero.")

    while True:
        try:
            minuto = int(input("Minuto de nacimiento (0-59): ").strip())
            if 0 <= minuto <= 59: break
            print("Valor entre 0 y 59.")
        except ValueError:
            print("Introduce un número entero.")

    ciudad = input("Lugar de nacimiento (ciudad, país): ").strip()
    if not ciudad:
        print("El lugar no puede estar vacío."); sys.exit(1)

    print()
    print("Calculando carta natal...")

    try:
        lat, lon = geocodificar(ciudad)
        print(f"  Coordenadas: {lat:.4f}, {lon:.4f}")
    except Exception as e:
        print(f"Error de geocodificación: {e}"); sys.exit(1)

    try:
        tz_name = obtener_timezone(lat, lon)
        print(f"  Zona horaria: {tz_name}")
    except Exception as e:
        print(f"Error de zona horaria: {e}"); sys.exit(1)

    try:
        carta  = calcular_carta(anio, mes, dia, hora, minuto, lat, lon, tz_name)
        asc    = carta["asc"]
        jup    = carta["planetas"].get("Júpiter",  {})
        sat    = carta["planetas"].get("Saturno",  {})
        print(f"  ASC:     {asc['signo']} {grado_a_dms(asc['grado'])}")
        print(f"  Júpiter: {jup.get('signo','')} {grado_a_dms(jup.get('grado',0))} — Casa {jup.get('casa','')}")
        print(f"  Saturno: {sat.get('signo','')} {grado_a_dms(sat.get('grado',0))} — Casa {sat.get('casa','')}")
    except Exception as e:
        print(f"Error en cálculo astrológico: {e}"); sys.exit(1)

    aspectos = calcular_aspectos_sociales(carta["planetas"])
    print(f"  Aspectos calculados: {len(aspectos)}")

    nombre_f = "".join(
        c if c.isalnum() or c in ("_", "-") else "_"
        for c in nombre.strip().replace(" ", "_")
    )

    ruta_base   = os.path.join(BASE_DIR, nombre_f + "_Planetas_Sociales")
    ruta_tex    = ruta_base + ".tex"
    ruta_pdf    = ruta_base + ".pdf"
    ruta_rueda  = os.path.join(BASE_DIR, nombre_f + "_rueda.png")

    dibujar_rueda(carta, nombre, ruta_rueda)

    print("  Generando interpretación...")

    latex = generar_latex(
        carta, nombre, anio, mes, dia,
        hora, minuto, ciudad,
        lat, lon, tz_name,
        ruta_rueda,
        aspectos
    )
    with open(ruta_tex, "w", encoding="utf-8") as f:
        f.write(latex)
    print(f"  LaTeX guardado: {ruta_tex}")

    print("  Compilando PDF...")
    try:
        for _ in range(2):
            subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", os.path.basename(ruta_tex)],
                capture_output=True, timeout=180, cwd=BASE_DIR
            )
        if os.path.exists(ruta_pdf):
            print(f"\n  PDF generado correctamente:")
            print(f"  {ruta_pdf}")
        else:
            print("  PDF no generado. Revisa el archivo .tex para más detalles.")
    except FileNotFoundError:
        print("  pdflatex no encontrado. El archivo .tex está listo para compilar.")
    except Exception as e:
        print(f"  Error al compilar: {e}")

    print()
    print("Proceso completado.")


if __name__ == "__main__":
    main()
