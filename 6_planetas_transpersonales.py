#!/usr/bin/env python3
"""
6. Planetas Transpersonales — Urano, Neptuno y Plutón — Arquitectura Interna

Este programa observa las fuerzas que modifican profundamente
tu forma habitual de vivir y sostener la vida.

- Urano muestra dónde necesitas cambio, espacio o libertad,
  y qué tiende a romper estructuras que ya no pueden mantenerse igual.

- Neptuno muestra dónde los límites se vuelven más sensibles,
  difusos o permeables, y dónde puede costarte distinguir
  con claridad qué necesitas realmente.

- Plutón muestra dónde vives procesos intensos,
  difíciles de controlar o imposibles de sostener de la misma manera para siempre.

No habla de rasgos fijos de personalidad.
Habla de procesos que cambian la forma en que vives,
te organizas y atraviesas determinadas etapas de la vida.
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
    _ASP_COLORES = {
    "=":"#666666",
    "□":"#CC2200",
    "☍":"#CC2200",
    "△":"#1A5FA8",
    "✶":"#1A5FA8",
    "⚻":"#2E7D32"
    }

    _ASP_LW = {
    "=":0.8,
    "□":1.0,
    "☍":1.0,
    "△":0.9,
    "✶":0.8,
    "⚻":0.7
    }

    _ASP_ALPHA = {
    "=":0.35,
    "□":0.55,
    "☍":0.55,
    "△":0.50,
    "✶":0.45,
    "⚻":0.35
    }

    R_ASP = R_CASA_IN - 0.02

    aspectos_rueda = calcular_aspectos_trans(carta["planetas"])

    planetas_con_aspecto = set()
    for asp in aspectos_rueda:
        planetas_con_aspecto.add(asp["p1"])
        planetas_con_aspecto.add(asp["p2"])

    for asp in aspectos_rueda:
        if asp["orbe"] > 8.0:
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
        "Urano", "Neptuno", "Plutón",
        "Sol", "Luna", "Mercurio", "Venus", "Marte",
        "Júpiter", "Saturno",
        "Quirón", "Lilith"
    ]

    orden = [
        p for p in orden_base
        if p in ("Urano", "Neptuno", "Plutón") or p in planetas_con_aspecto
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

SIGNOS = ["Aries","Tauro","Géminis","Cáncer","Leo","Virgo",
          "Libra","Escorpio","Sagitario","Capricornio","Acuario","Piscis"]

ELEMENTO_SIGNO = {
    "Aries":"Fuego","Tauro":"Tierra","Géminis":"Aire","Cáncer":"Agua",
    "Leo":"Fuego","Virgo":"Tierra","Libra":"Aire","Escorpio":"Agua",
    "Sagitario":"Fuego","Capricornio":"Tierra","Acuario":"Aire","Piscis":"Agua"
}

PLANETAS_TRANSPERSONALES = [
    "Urano",
    "Neptuno",
    "Plutón"
]

PLANETAS_PERSONALES = [
    "Sol",
    "Luna",
    "Mercurio",
    "Venus",
    "Marte"
]

PUNTOS_SENSIBLES = [
    "Quirón",
    "Lilith"
]

PLANETAS_IDS = [
    (swe.SUN,     "Sol",      "☉"),
    (swe.MOON,    "Luna",     "☽"),
    (swe.MERCURY, "Mercurio", "☿"),
    (swe.VENUS,   "Venus",    "♀"),
    (swe.MARS,    "Marte",    "♂"),
    (swe.JUPITER, "Júpiter",  "♃"),
    (swe.SATURN,  "Saturno",  "♄"),
    (swe.URANUS,  "Urano",    "♅"),
    (swe.NEPTUNE, "Neptuno",  "♆"),
    (swe.PLUTO,   "Plutón",   "♇"),
]

CHIRON_ID = swe.CHIRON
LILITH_ID = swe.MEAN_APOG

SIMBOLOS_SIGNOS = [
    "♈","♉","♊","♋",
    "♌","♍","♎","♏",
    "♐","♑","♒","♓"
]

COLORES_ELEMENTO = {
    "Fuego":"#CC2200",
    "Tierra":"#2E7D32",
    "Aire":"#E67E00",
    "Agua":"#1A5FA8"
}

COLORES_PLANETA = {
    "Sol":"#CC2200",
    "Marte":"#CC2200",
    "Júpiter":"#CC2200",

    "Venus":"#2E7D32",
    "Saturno":"#2E7D32",

    "Mercurio":"#E67E00",
    "Urano":"#E67E00",

    "Luna":"#1A5FA8",
    "Neptuno":"#1A5FA8",
    "Plutón":"#1A5FA8",

    "Quirón":"#7B2D8B",
    "Lilith":"#7B2D8B",
    "Nodo Norte":"#888800",
    "Nodo Sur":"#888800",
}

# Aspectos principales utilizados en este módulo.
# No incluimos quincuncio para mantener una lectura más limpia.
ASPECTOS_DEF = [
    ("Conjunción", 0,   10.0, "="),
    ("Sextil",     60,  6.0, "✶"),
    ("Cuadratura", 90,  8.0, "□"),
    ("Trígono",    120, 8.0, "△"),
    ("Oposición",  180, 8.0, "☍"),

]


# ─── TEXTOS: URANO POR SIGNO ──────────────────────────────────────────────────
# Dónde aparece la necesidad de cambio, qué tiende a romperse
# y qué necesita actualizarse para que puedas seguir avanzando.

URANO_SIGNO = {

"Aries": (
    "Urano en Aries muestra una necesidad profunda de actuar con libertad y abrir espacio para hacer las cosas de otra manera. "
    "Los cambios suelen aparecer cuando llevas demasiado tiempo sosteniendo una dirección que ya no sientes viva.\n\n"

    "Puede haber decisiones rápidas, cortes repentinos o necesidad de moverte antes de tener todo claro. "
    "A veces rompes con una situación de forma brusca porque ya no puedes seguir funcionando igual dentro de ella.\n\n"

    "El aprendizaje no está en evitar el cambio, sino en reconocer antes qué necesita actualizarse "
    "para no llegar siempre al punto de ruptura."
),

"Tauro": (
    "Urano en Tauro muestra cambios profundos en la forma en que construyes estabilidad, seguridad y sostén material. "
    "Lo que parecía fijo o permanente puede dejar de servirte antes de que hayas encontrado una alternativa clara.\n\n"

    "A veces necesitas soltar formas de vida, ritmos o seguridades que habías mantenido durante mucho tiempo "
    "aunque ya no encajen realmente contigo.\n\n"

    "El aprendizaje pasa por construir estabilidad más flexible, capaz de adaptarse sin derrumbarse cada vez que algo cambia."
),

"Géminis": (
    "Urano en Géminis muestra una mente inquieta, rápida y difícil de mantener dentro de estructuras demasiado rígidas. "
    "Necesitas revisar constantemente la forma en que piensas, aprendes o te comunicas.\n\n"

    "Los cambios suelen aparecer a través de nuevas ideas, giros inesperados o formas distintas de entender las cosas. "
    "A veces pasas de una perspectiva a otra muy rápido y te cuesta sostener continuidad mental.\n\n"

    "El aprendizaje está en permitir movimiento sin perder completamente el hilo de lo que realmente quieres desarrollar."
),

"Cáncer": (
    "Urano en Cáncer muestra cambios importantes en la forma en que vives la intimidad, la pertenencia y la seguridad emocional. "
    "Puede costarte mantener durante mucho tiempo estructuras afectivas que se sienten demasiado cerradas o inmóviles.\n\n"

    "A veces los cambios llegan precisamente en aquello que pensabas que te protegía o te daba estabilidad. "
    "Lo emocional necesita actualizarse aunque una parte de ti quiera conservarlo igual.\n\n"

    "El aprendizaje está en construir vínculos y espacios donde puedas sentir cercanía sin perder libertad interna."
),

"Leo": (
    "Urano en Leo muestra necesidad de expresarte de una manera auténtica y difícil de encajar en formas demasiado prefijadas. "
    "Los cambios suelen aparecer cuando sientes que ya no puedes seguir sosteniendo una forma de mostrarte que no te representa.\n\n"

    "Puede haber etapas de mucha creatividad, giros expresivos o necesidad de romper con expectativas externas. "
    "A veces abandonas algo importante justo cuando parecía consolidarse.\n\n"

    "El aprendizaje pasa por crear desde un lugar más libre, sin necesitar romperlo todo cada vez que cambia tu forma de expresarte."
),

"Virgo": (
    "Urano en Virgo muestra necesidad de revisar continuamente la manera en que organizas tu vida, tu trabajo o tus rutinas. "
    "Lo que antes funcionaba puede quedarse obsoleto muy rápido.\n\n"

    "Puede haber cambios inesperados en hábitos, formas de trabajar o maneras de sostener el día a día. "
    "A veces intentas reorganizarlo todo de golpe porque ya no soportas seguir funcionando igual.\n\n"

    "El aprendizaje está en permitir ajustes progresivos antes de llegar al agotamiento o al rechazo completo de la estructura."
),

"Libra": (
    "Urano en Libra muestra necesidad de libertad dentro de los vínculos y dificultad para sostener relaciones demasiado rígidas o previsibles. "
    "Los cambios suelen aparecer cuando la forma de relacionarte deja de sentirse viva o auténtica.\n\n"

    "Puede haber giros importantes en relaciones, acuerdos o maneras de vincularte. "
    "A veces necesitas tomar distancia para poder recuperar claridad sobre lo que realmente quieres compartir.\n\n"

    "El aprendizaje pasa por construir relaciones donde exista espacio para el cambio sin que cada transformación implique una ruptura."
),

"Escorpio": (
    "Urano en Escorpio muestra cambios intensos y difíciles de controlar en procesos emocionales profundos. "
    "Hay una necesidad constante de transformación, incluso cuando una parte de ti preferiría mantener el control.\n\n"

    "Puede haber rupturas internas importantes, descubrimientos difíciles de ignorar o momentos donde algo cambia de forma irreversible. "
    "A veces lo que intentabas contener termina emergiendo de golpe.\n\n"

    "El aprendizaje está en permitir transformación sin vivir cada cambio como una amenaza que necesitas controlar completamente."
),

"Sagitario": (
    "Urano en Sagitario muestra necesidad de revisar creencias, direcciones y formas de entender la vida. "
    "Los cambios suelen aparecer cuando una visión deja de darte sentido o amplitud.\n\n"

    "Puede haber giros fuertes en ideas, estudios, filosofía de vida o proyectos que parecían definir tu dirección. "
    "A veces cambias de horizonte muy rápido porque necesitas volver a sentir apertura y movimiento.\n\n"

    "El aprendizaje pasa por permitir nuevas perspectivas sin perder completamente la continuidad de tu camino."
),

"Capricornio": (
    "Urano en Capricornio muestra cambios importantes en estructuras que parecían estables: trabajo, responsabilidades, posición o formas de construir a largo plazo. "
    "Lo que has sostenido durante años puede necesitar transformarse aunque haya costado mucho construirlo.\n\n"

    "A veces los cambios llegan precisamente en aquello donde más esfuerzo habías invertido. "
    "Puede costarte soltar estructuras que funcionaron durante mucho tiempo pero ya no tienen la misma vida.\n\n"

    "El aprendizaje está en construir de forma más flexible, sin identificar estabilidad con rigidez."
),

"Acuario": (
    "Urano en Acuario intensifica la necesidad de libertad, cambio y diferenciación. "
    "Te resulta difícil sostener durante demasiado tiempo estructuras que sientes rígidas, repetitivas o demasiado convencionales.\n\n"

    "Puede haber necesidad constante de actualizar ideas, espacios, vínculos o formas de vida. "
    "A veces cambias rápido porque percibes antes que otras personas lo que ya no tiene futuro.\n\n"

    "El aprendizaje pasa por crear cambios que también puedan sostenerse en el tiempo, "
    "sin vivir en ruptura permanente con todo."
),

"Piscis": (
    "Urano en Piscis muestra cambios profundos en la sensibilidad, los límites y la forma en que percibes lo que ocurre a tu alrededor. "
    "Puede costarte mantener referencias estables cuando algo interno necesita transformarse.\n\n"

    "A veces aparecen etapas de mucha apertura, intuición o sensación de desbordamiento difícil de explicar. "
    "Lo que antes parecía claro puede volverse confuso de forma bastante rápida.\n\n"

    "El aprendizaje está en desarrollar límites más conscientes sin perder sensibilidad ni capacidad de conexión."
),

}

# ─── TEXTOS: URANO POR CASA ───────────────────────────────────────────────────
# En qué parte de la vida aparecen cambios difíciles de controlar,
# necesidad de libertad o rupturas de patrón.

URANO_CASA = {

1: (
    "Urano en Casa 1 muestra necesidad de vivir desde mayor libertad y autenticidad. "
    "Puede costarte sostener durante mucho tiempo formas de actuar o mostrarte que ya no sientes vivas.\n\n"

    "Los cambios suelen verse rápidamente desde fuera: etapas donde modificas dirección, imagen, actitud o manera de posicionarte. "
    "A veces necesitas romper con una versión anterior de ti para poder seguir avanzando.\n\n"

    "El aprendizaje está en permitir evolución sin sentir que necesitas destruir todo lo anterior cada vez que cambias."
),

2: (
    "Urano en Casa 2 muestra cambios importantes en la relación con la estabilidad, los recursos y la seguridad material. "
    "Puede costarte sostener estructuras económicas o formas de vida demasiado rígidas.\n\n"

    "A veces aparecen etapas irregulares: cambios de ingresos, de prioridades o de manera de organizar tus recursos. "
    "Lo que antes parecía seguro puede dejar de tener sentido bastante rápido.\n\n"

    "El aprendizaje pasa por construir una estabilidad más flexible, capaz de adaptarse sin derrumbarse con cada cambio."
),

3: (
    "Urano en Casa 3 muestra una mente rápida, inquieta y difícil de mantener dentro de formas demasiado repetitivas. "
    "Necesitas revisar constantemente la manera en que piensas, aprendes o te comunicas.\n\n"

    "Puede haber cambios bruscos de ideas, intereses o maneras de entender las cosas. "
    "A veces haces conexiones muy rápidas, pero también puedes perder interés igual de rápido.\n\n"

    "El aprendizaje está en permitir movimiento mental sin desconectarte completamente de lo que quieres desarrollar."
),

4: (
    "Urano en Casa 4 muestra cambios importantes en la vida privada, la sensación de hogar o la forma en que buscas estabilidad emocional. "
    "Puede costarte sostener durante mucho tiempo estructuras familiares o domésticas demasiado rígidas.\n\n"

    "A veces aparecen mudanzas, cambios de base o necesidad de reorganizar profundamente tu espacio vital. "
    "Lo que antes sentías como refugio puede dejar de servirte de la misma manera.\n\n"

    "El aprendizaje pasa por construir una base más viva y adaptable, no únicamente estable desde fuera."
),

5: (
    "Urano en Casa 5 muestra necesidad de expresarte de forma libre, auténtica y poco convencional. "
    "Puede costarte sostener formas creativas demasiado previsibles o repetitivas.\n\n"

    "A veces aparecen etapas de mucha inspiración seguidas de cortes bruscos o cambios de dirección. "
    "También puede haber giros importantes en la forma de vivir el deseo, la creatividad o la necesidad de reconocimiento.\n\n"

    "El aprendizaje está en sostener la creatividad sin necesitar romper constantemente con lo que estabas construyendo."
),

6: (
    "Urano en Casa 6 muestra cambios frecuentes en rutinas, trabajo o formas de organizar el día a día. "
    "Puede resultarte difícil sostener estructuras demasiado rígidas en la vida cotidiana.\n\n"

    "A veces reorganizas horarios, hábitos o maneras de trabajar de forma bastante abrupta porque ya no puedes seguir funcionando igual. "
    "Lo que antes te servía puede quedarse obsoleto muy rápido.\n\n"

    "El aprendizaje pasa por crear formas de organización más flexibles y vivas, capaces de evolucionar contigo."
),

7: (
    "Urano en Casa 7 muestra necesidad de libertad y autenticidad dentro de los vínculos. "
    "Puede costarte sostener relaciones demasiado cerradas, rígidas o previsibles.\n\n"

    "A veces aparecen cambios importantes en relaciones, acuerdos o maneras de vincularte. "
    "Puede haber necesidad de más espacio o periodos donde revisas profundamente qué significa compartir con otra persona.\n\n"

    "El aprendizaje está en construir relaciones donde exista libertad sin que cada cambio implique ruptura."
),

8: (
    "Urano en Casa 8 muestra cambios intensos en procesos emocionales profundos, recursos compartidos o formas de transformación interna. "
    "Puede haber etapas donde algo cambia de manera brusca y ya no puede seguir funcionando igual.\n\n"

    "A veces emergen emociones, verdades o procesos difíciles de controlar racionalmente. "
    "Lo que parecía estable puede transformarse mucho más rápido de lo esperado.\n\n"

    "El aprendizaje pasa por permitir transformación sin intentar controlar completamente cada proceso profundo."
),

9: (
    "Urano en Casa 9 muestra necesidad de revisar ideas, creencias y formas de entender la vida. "
    "Puede costarte sostener durante mucho tiempo visiones demasiado cerradas o rígidas.\n\n"

    "A veces cambias de perspectiva de forma bastante rápida porque necesitas volver a sentir amplitud y apertura. "
    "También puede haber giros importantes en estudios, filosofía de vida o dirección vital.\n\n"

    "El aprendizaje está en abrir nuevas perspectivas sin perder completamente el hilo de tu propio camino."
),

10: (
    "Urano en Casa 10 muestra cambios importantes en la dirección profesional, la posición pública o la manera en que construyes tu vida hacia fuera. "
    "Puede resultarte difícil sostener trayectorias demasiado rígidas o previsibles.\n\n"

    "A veces aparecen giros laborales, cambios de dirección o necesidad de reorganizar completamente lo que estabas construyendo. "
    "Lo que parecía estable puede transformarse bastante rápido.\n\n"

    "El aprendizaje pasa por construir una dirección profesional más coherente con quién eres ahora, no solo con lo que construiste antes."
),

11: (
    "Urano en Casa 11 muestra necesidad de libertad dentro de grupos, proyectos y espacios colectivos. "
    "Puede costarte sostener durante mucho tiempo vínculos grupales demasiado rígidos o poco auténticos.\n\n"

    "A veces entras y sales de grupos, amistades o proyectos de forma bastante rápida porque necesitas sentir movimiento y renovación. "
    "También puede haber cambios importantes en tus ideales o en la forma de imaginar el futuro.\n\n"

    "El aprendizaje está en participar en lo colectivo sin perder independencia ni necesidad de autenticidad."
),

12: (
    "Urano en Casa 12 muestra cambios internos profundos que muchas veces empiezan mucho antes de hacerse visibles desde fuera. "
    "Puede haber etapas donde algo se reorganiza por dentro sin que todavía puedas explicarlo claramente.\n\n"

    "A veces sientes necesidad de retirarte, desconectarte o tomar distancia antes de un cambio importante. "
    "Lo que parecía estable internamente puede transformarse silenciosamente hasta que ya no puede seguir igual.\n\n"

    "El aprendizaje pasa por escuchar antes las señales internas para no llegar siempre al cambio desde el agotamiento o la ruptura."
),

}


# ─── TEXTOS: NEPTUNO POR SIGNO ────────────────────────────────────────────────
# Dónde los límites se vuelven más sensibles o difusos,
# qué tiende a perder claridad y qué necesita más consciencia.

NEPTUNO_SIGNO = {

"Aries": (
    "Neptuno en Aries puede hacer que te cueste mantener claridad en la acción o en la dirección que quieres tomar. "
    "A veces sientes impulso o motivación, pero al intentar concretarlo algo se dispersa o pierde fuerza.\n\n"

    "Puede haber dificultad para saber cuándo actuar, cómo avanzar o hacia dónde dirigir la energía. "
    "En algunos momentos reaccionas rápido y en otros te cuesta muchísimo arrancar.\n\n"

    "El aprendizaje está en desarrollar una dirección más consciente, sin exigirte claridad absoluta antes de empezar a moverte."
),

"Tauro": (
    "Neptuno en Tauro vuelve más sensibles los temas relacionados con estabilidad, seguridad y recursos. "
    "Puede costarte distinguir con claridad qué te sostiene realmente y qué solo te da sensación momentánea de estabilidad.\n\n"

    "A veces mantienes estructuras materiales, económicas o afectivas porque parecen seguras, "
    "aunque internamente ya no tengan tanta consistencia.\n\n"

    "El aprendizaje pasa por construir seguridad desde algo más vivo y consciente, "
    "no solo desde lo que parece estable hacia fuera."
),

"Géminis": (
    "Neptuno en Géminis puede hacer que la mente funcione de forma muy intuitiva pero también bastante dispersa. "
    "A veces percibes muchas posibilidades al mismo tiempo y te cuesta ordenar qué es importante realmente.\n\n"

    "Puede haber confusión mental, exceso de información o dificultad para expresar con precisión lo que intentas transmitir. "
    "También puedes cambiar fácilmente de perspectiva según el entorno o el estado emocional.\n\n"

    "El aprendizaje está en desarrollar más claridad mental sin perder sensibilidad ni capacidad imaginativa."
),

"Cáncer": (
    "Neptuno en Cáncer vuelve muy sensibles los límites emocionales. "
    "Puede costarte distinguir qué sientes tú y qué estás absorbiendo del entorno o de otras personas.\n\n"

    "A veces necesitas mucho refugio emocional y otras veces te desbordas sin entender bien por qué. "
    "La necesidad de pertenencia puede hacer que mantengas vínculos o dinámicas poco claras durante demasiado tiempo.\n\n"

    "El aprendizaje pasa por desarrollar límites emocionales más conscientes sin cerrar la sensibilidad."
),

"Leo": (
    "Neptuno en Leo puede hacer que la expresión personal, la creatividad o la necesidad de reconocimiento se vuelvan menos claras. "
    "A veces dudas sobre cómo mostrarte o sobre qué parte de lo que expresas realmente te representa.\n\n"

    "Puede haber idealización de la propia imagen o dificultad para sostener una identidad estable durante mucho tiempo. "
    "En algunos momentos necesitas expresarte mucho y en otros desaparece completamente el impulso.\n\n"

    "El aprendizaje está en crear desde un lugar más auténtico, sin depender tanto de la imagen o de la validación externa."
),

"Virgo": (
    "Neptuno en Virgo puede hacer que te cueste encontrar suficiente claridad en la organización, los detalles o el funcionamiento cotidiano. "
    "A veces intentas ordenar algo que internamente todavía no tiene forma definida.\n\n"

    "Puede haber sensación de confusión en rutinas, trabajo, hábitos o maneras de organizar la vida diaria. "
    "Cuanto más intentas controlar cada detalle, más sensación de desorden puede aparecer.\n\n"

    "El aprendizaje pasa por desarrollar estructura sin exigir precisión absoluta en todo momento."
),

"Libra": (
    "Neptuno en Libra vuelve más sensibles y difusos los temas relacionados con vínculos y acuerdos. "
    "Puede costarte ver con claridad qué ocurre realmente en una relación o qué necesita cada parte.\n\n"

    "A veces sostienes relaciones, expectativas o acuerdos poco definidos porque deseas mantener armonía o conexión. "
    "También puedes idealizar fácilmente a otras personas.\n\n"

    "El aprendizaje está en construir relaciones más claras y conscientes sin perder sensibilidad hacia el otro."
),

"Escorpio": (
    "Neptuno en Escorpio vuelve más difusos los límites en procesos emocionales profundos. "
    "Puede costarte distinguir con claridad qué necesitas controlar y qué necesita transformarse.\n\n"

    "A veces aparecen emociones intensas, procesos difíciles de explicar o sensación de estar atravesando algo que no puedes comprender del todo racionalmente. "
    "También puede haber mucha sensibilidad hacia lo oculto o lo no visible.\n\n"

    "El aprendizaje pasa por permitir profundidad emocional sin perder completamente la referencia de ti."
),

"Sagitario": (
    "Neptuno en Sagitario puede hacer que busques sentido, dirección o verdad en lugares que después resultan menos sólidos de lo que parecían. "
    "A veces necesitas creer en algo para sentir orientación, incluso cuando todavía no está claro.\n\n"

    "Puede haber idealización de caminos, proyectos, filosofías o personas que parecen ofrecer amplitud o propósito. "
    "También puedes cambiar varias veces de dirección buscando una referencia más auténtica.\n\n"

    "El aprendizaje está en desarrollar una visión más consciente sin perder apertura ni capacidad de inspiración."
),

"Capricornio": (
    "Neptuno en Capricornio vuelve más difusos los límites relacionados con estructura, responsabilidad y dirección de vida. "
    "Puede costarte distinguir qué construcciones siguen teniendo sentido y cuáles mantienes solo por inercia.\n\n"

    "A veces sostienes demasiado tiempo responsabilidades, trabajos o formas de vida que internamente ya se han vaciado. "
    "También puede haber sensación de desorientación respecto al futuro o al lugar que ocupas.\n\n"

    "El aprendizaje pasa por construir una estructura más coherente con lo que realmente tiene vida para ti."
),

"Acuario": (
    "Neptuno en Acuario puede hacer que las ideas colectivas, los grupos o las visiones de futuro se vuelvan menos claras. "
    "A veces proyectas demasiadas expectativas sobre proyectos, personas o espacios colectivos.\n\n"

    "Puede haber idealización de causas, amistades o formas de cambio que después muestran menos coherencia real de la que imaginabas. "
    "También puedes sentir dificultad para encontrar un lugar colectivo que realmente encaje contigo.\n\n"

    "El aprendizaje está en participar en lo colectivo sin perder discernimiento ni referencia personal."
),

"Piscis": (
    "Neptuno en Piscis intensifica muchísimo la sensibilidad y la permeabilidad emocional. "
    "Los límites pueden sentirse más abiertos de lo habitual y a veces te cuesta distinguir claramente entre lo que es tuyo y lo que viene del entorno.\n\n"

    "Puede haber mucha intuición, imaginación y capacidad de conexión, pero también etapas de confusión, desbordamiento o sensación de no tener suficiente referencia interna. "
    "Lo emocional y lo simbólico tienen mucho peso en tu experiencia.\n\n"

    "El aprendizaje pasa por desarrollar límites más conscientes sin perder sensibilidad ni profundidad."
),

}


# ─── TEXTOS: NEPTUNO POR CASA ─────────────────────────────────────────────────
# En qué parte de la vida aparecen más sensibilidad, confusión,
# permeabilidad o dificultad para mantener límites claros.

NEPTUNO_CASA = {

1: (
    "Neptuno en Casa 1 puede hacer que tu forma de mostrarte cambie bastante según el entorno, el momento vital o el estado emocional. "
    "A veces te cuesta definir con claridad quién eres o cómo quieres presentarte.\n\n"

    "Puede haber mucha sensibilidad hacia cómo te perciben otras personas, "
    "o sensación de adaptarte demasiado a lo que ocurre alrededor.\n\n"

    "El aprendizaje pasa por desarrollar una presencia más consciente y estable sin perder sensibilidad."
),

2: (
    "Neptuno en Casa 2 vuelve más sensibles los temas relacionados con estabilidad, dinero y recursos personales. "
    "Puede costarte ver con claridad qué te sostiene realmente o qué tiene valor verdadero para ti.\n\n"

    "A veces hay confusión en temas económicos, sensación de inseguridad difícil de explicar "
    "o tendencia a idealizar ciertas formas de estabilidad.\n\n"

    "El aprendizaje está en construir una relación más consciente con lo material sin buscar seguridad absoluta."
),

3: (
    "Neptuno en Casa 3 puede hacer que la mente funcione de forma muy intuitiva y asociativa, "
    "pero también bastante dispersa en algunos momentos.\n\n"

    "Puede haber dificultad para organizar ideas, explicar con precisión lo que quieres decir "
    "o mantener claridad mental cuando hay demasiada información o estímulos.\n\n"

    "El aprendizaje pasa por desarrollar más foco y claridad sin perder sensibilidad ni imaginación."
),

4: (
    "Neptuno en Casa 4 vuelve muy sensibles los temas relacionados con hogar, intimidad y base emocional. "
    "Puede costarte sentir límites claros entre lo que necesitas tú y lo que absorbes del entorno familiar o emocional.\n\n"

    "A veces hay sensación de no encontrar del todo un lugar interno estable o de buscar refugio en espacios que después resultan menos sólidos de lo esperado.\n\n"

    "El aprendizaje está en construir una base emocional más consciente y diferenciada."
),

5: (
    "Neptuno en Casa 5 puede hacer que la creatividad, el deseo o la expresión personal funcionen de forma muy inspirada pero difícil de sostener continuamente. "
    "A veces sientes mucho potencial creativo y otras veces todo parece dispersarse.\n\n"

    "Puede haber idealización del amor, de la expresión artística o de ciertas experiencias emocionales intensas. "
    "También puede costarte distinguir entre inspiración real y proyección.\n\n"

    "El aprendizaje pasa por dar forma concreta a lo que imaginas sin perder sensibilidad creativa."
),

6: (
    "Neptuno en Casa 6 vuelve más difusos los límites relacionados con trabajo, hábitos y funcionamiento cotidiano. "
    "Puede costarte mantener rutinas claras o reconocer a tiempo cuándo algo te está agotando.\n\n"

    "A veces hay confusión en horarios, organización o formas de cuidar el cuerpo y la energía. "
    "También puedes absorber demasiado del ambiente laboral o de las exigencias externas.\n\n"

    "El aprendizaje está en desarrollar hábitos más conscientes y sostenibles sin rigidizarte."
),

7: (
    "Neptuno en Casa 7 vuelve muy sensibles los vínculos y las relaciones cercanas. "
    "Puede costarte ver con claridad qué ocurre realmente en una relación o qué necesita cada persona.\n\n"

    "A veces idealizas vínculos, proyectas expectativas muy altas o mantienes relaciones poco definidas durante demasiado tiempo. "
    "También puedes adaptarte demasiado para evitar perder conexión.\n\n"

    "El aprendizaje pasa por construir relaciones más claras sin perder sensibilidad ni capacidad de entrega."
),

8: (
    "Neptuno en Casa 8 puede hacer que los procesos emocionales profundos sean difíciles de entender racionalmente. "
    "A veces atraviesas cambios internos intensos sin tener todavía palabras claras para explicarlos.\n\n"

    "Puede haber mucha sensibilidad hacia lo oculto, lo emocional o lo no visible. "
    "También puede costarte distinguir con claridad qué necesitas compartir y qué necesitas proteger.\n\n"

    "El aprendizaje está en desarrollar más consciencia emocional sin intentar controlar completamente lo profundo."
),

9: (
    "Neptuno en Casa 9 puede hacer que busques sentido, dirección o verdad en experiencias, ideas o caminos que después resultan menos claros de lo que parecían. "
    "A veces necesitas creer en algo para sentir orientación.\n\n"

    "Puede haber idealización de filosofías, estudios, personas o proyectos que parecen ofrecer propósito o amplitud. "
    "También puedes cambiar varias veces de visión buscando una referencia más auténtica.\n\n"

    "El aprendizaje pasa por desarrollar una dirección más consciente sin perder apertura ni inspiración."
),

10: (
    "Neptuno en Casa 10 vuelve más difusos los temas relacionados con dirección profesional, reconocimiento y lugar en el mundo. "
    "Puede costarte ver con claridad hacia dónde quieres construir o qué estructura profesional tiene realmente sentido para ti.\n\n"

    "A veces sostienes proyectos, trabajos o metas que desde fuera parecen sólidos pero internamente ya no tienen tanta vida. "
    "También puede haber sensación de desorientación respecto al futuro.\n\n"

    "El aprendizaje está en construir una dirección más coherente con lo que realmente quieres vivir."
),

11: (
    "Neptuno en Casa 11 puede hacer que idealices grupos, amistades o proyectos colectivos. "
    "A veces buscas pertenecer a espacios que parecen muy inspiradores pero después muestran menos claridad o coherencia real.\n\n"

    "Puede costarte distinguir qué vínculos colectivos son realmente sostenibles y cuáles funcionan más desde expectativa o proyección.\n\n"

    "El aprendizaje pasa por participar en lo colectivo sin perder discernimiento ni referencia propia."
),

12: (
    "Neptuno en Casa 12 intensifica muchísimo la sensibilidad interna y la conexión con procesos difíciles de explicar racionalmente. "
    "A veces percibes muchas cosas de forma intuitiva antes de poder entenderlas claramente.\n\n"

    "Puede haber etapas de retiro, confusión, mucha apertura emocional o sensación de estar atravesando algo invisible hacia fuera pero muy intenso por dentro. "
    "También necesitas momentos de silencio y desconexión para recuperar claridad.\n\n"

    "El aprendizaje está en desarrollar límites internos más conscientes sin perder profundidad ni sensibilidad."
),

}

# ─── TEXTOS: PLUTÓN POR SIGNO ─────────────────────────────────────────────────
# Dónde aparecen procesos intensos de transformación,
# qué ya no puede seguir igual y qué pide profundidad real.

PLUTON_SIGNO = {

"Aries": (
    "Plutón en Aries intensifica muchísimo la necesidad de actuar, afirmarte y abrir camino propio. "
    "Los procesos de transformación suelen aparecer a través de decisiones, conflictos o situaciones donde ya no puedes seguir reaccionando igual.\n\n"

    "Puede haber etapas de mucha intensidad en la acción, impulsos difíciles de contener "
    "o sensación de estar siempre empujando algo hacia adelante.\n\n"

    "El aprendizaje pasa por desarrollar fuerza sin vivir permanentemente en lucha o tensión."
),

"Tauro": (
    "Plutón en Tauro lleva al límite temas relacionados con seguridad, estabilidad y apego a lo que sostiene tu vida. "
    "Las transformaciones suelen aparecer precisamente en aquello que parecía más estable.\n\n"

    "Puede costarte muchísimo soltar formas de vida, vínculos o seguridades que ya no tienen vida real. "
    "A veces sostienes demasiado tiempo algo por miedo a perder estabilidad.\n\n"

    "El aprendizaje está en construir seguridad desde algo más profundo que el control o la acumulación."
),

"Géminis": (
    "Plutón en Géminis intensifica el pensamiento, la necesidad de entender y la búsqueda de verdad detrás de las apariencias. "
    "Las ideas rara vez se quedan en superficie.\n\n"

    "Puede haber obsesión por comprender, necesidad de analizar profundamente "
    "o dificultad para dejar de pensar en algo una vez se activa internamente.\n\n"

    "El aprendizaje pasa por permitir profundidad mental sin quedar atrapade en análisis constantes."
),

"Cáncer": (
    "Plutón en Cáncer intensifica muchísimo los temas emocionales, familiares y de pertenencia. "
    "Las transformaciones suelen aparecer en vínculos, bases emocionales o formas de buscar protección.\n\n"

    "Puede haber miedo a perder lo que amas, necesidad intensa de proteger "
    "o dificultad para soltar patrones emocionales muy antiguos.\n\n"

    "El aprendizaje está en construir seguridad emocional sin vivir permanentemente desde el miedo a perderla."
),

"Leo": (
    "Plutón en Leo intensifica la necesidad de expresión, reconocimiento y autenticidad. "
    "Las transformaciones suelen aparecer cuando ya no puedes sostener una forma de mostrarte que no corresponde a lo que eres realmente.\n\n"

    "Puede haber mucha intensidad creativa, necesidad de ser visto "
    "o sensación de que expresar quién eres tiene consecuencias profundas.\n\n"

    "El aprendizaje pasa por expresarte desde un lugar más auténtico y menos dependiente de validación externa."
),

"Virgo": (
    "Plutón en Virgo intensifica muchísimo la relación con trabajo, exigencia, control y necesidad de mejora. "
    "Puede costarte descansar internamente porque siempre parece haber algo que corregir o perfeccionar.\n\n"

    "A veces llevas el esfuerzo y la autoexigencia al límite "
    "hasta que el cuerpo o la vida obligan a transformar la manera de funcionar.\n\n"

    "El aprendizaje está en desarrollar orden y compromiso sin convertir la exigencia en una forma permanente de presión."
),

"Libra": (
    "Plutón en Libra intensifica profundamente los vínculos y la necesidad de equilibrio real en las relaciones. "
    "Las transformaciones suelen aparecer a través de acuerdos, rupturas o dinámicas relacionales difíciles de sostener superficialmente.\n\n"

    "Puede haber miedo a perder vínculos importantes, relaciones muy intensas "
    "o dificultad para mantener relaciones donde no existe reciprocidad verdadera.\n\n"

    "El aprendizaje pasa por construir vínculos más honestos y profundos sin quedar atrapade en dinámicas de dependencia o control."
),

"Escorpio": (
    "Plutón en Escorpio intensifica muchísimo los procesos emocionales profundos, la necesidad de transformación y el contacto con lo que no puede mantenerse en superficie. "
    "Las experiencias suelen vivirse con mucha intensidad.\n\n"

    "Puede haber necesidad de controlar lo que ocurre internamente, miedo a perder poder "
    "o sensación de atravesar procesos que cambian completamente tu forma de vivir determinadas cosas.\n\n"

    "El aprendizaje está en permitir transformación profunda sin vivir constantemente desde la tensión o el control."
),

"Sagitario": (
    "Plutón en Sagitario intensifica la búsqueda de sentido, verdad y dirección vital. "
    "Las transformaciones suelen aparecer cuando una creencia, visión o camino deja de sostenerse frente a la experiencia real.\n\n"

    "Puede haber necesidad intensa de encontrar propósito, profundidad o una verdad que realmente tenga sentido para ti. "
    "También pueden producirse cambios muy fuertes de dirección o filosofía de vida.\n\n"

    "El aprendizaje pasa por sostener una búsqueda profunda sin convertir cada verdad en algo absoluto."
),

"Capricornio": (
    "Plutón en Capricornio intensifica muchísimo los temas relacionados con estructura, logro y responsabilidad. "
    "Las transformaciones suelen aparecer en aquello que has construido con más esfuerzo.\n\n"

    "Puede haber mucha necesidad de control, resistencia a perder estabilidad "
    "o dificultad para reconocer cuándo una estructura ya no tiene vida aunque siga funcionando hacia fuera.\n\n"

    "El aprendizaje está en construir desde mayor coherencia interna y no solo desde resistencia o capacidad de sostén."
),

"Acuario": (
    "Plutón en Acuario intensifica los cambios colectivos, las transformaciones sociales y la necesidad de revisar estructuras que ya no pueden sostenerse igual. "
    "Puede haber mucha tensión entre libertad y necesidad de pertenencia.\n\n"

    "A veces necesitas romper profundamente con formas de pensar, grupos o dinámicas que ya no encajan contigo. "
    "También puede haber intensidad en ideales, proyectos o necesidad de cambio.\n\n"

    "El aprendizaje pasa por participar en la transformación sin vivir permanentemente desde la ruptura."
),

"Piscis": (
    "Plutón en Piscis intensifica muchísimo la sensibilidad, la permeabilidad emocional y los procesos difíciles de explicar racionalmente. "
    "Las transformaciones suelen ocurrir en niveles muy internos y poco visibles hacia fuera.\n\n"

    "Puede haber sensación de atravesar etapas de mucha apertura emocional, pérdida de referencias antiguas "
    "o contacto profundo con emociones y estados difíciles de delimitar claramente.\n\n"

    "El aprendizaje está en desarrollar límites internos más conscientes sin perder profundidad ni sensibilidad."
),

}


# ─── TEXTOS: PLUTÓN POR CASA ──────────────────────────────────────────────────
# En qué parte de la vida aparecen procesos intensos,
# transformaciones profundas o situaciones que ya no pueden seguir igual.

PLUTON_CASA = {

1: (
    "Plutón en Casa 1 hace que los procesos de transformación afecten directamente a tu identidad, tu presencia y tu forma de posicionarte en la vida. "
    "Es difícil sostener durante mucho tiempo versiones de ti que ya no tienen verdad interna.\n\n"

    "Puede haber etapas de cambios profundos en la manera de actuar, mostrarte o relacionarte con el entorno. "
    "También puedes generar impacto intenso en otras personas incluso sin buscarlo.\n\n"

    "El aprendizaje está en permitir transformación sin vivir constantemente desde la tensión o la necesidad de control."
),

2: (
    "Plutón en Casa 2 intensifica muchísimo los temas relacionados con seguridad, recursos y estabilidad material. "
    "Las transformaciones suelen aparecer precisamente en aquello que intentas sostener como base segura.\n\n"

    "Puede haber miedo a perder estabilidad, necesidad de controlar recursos "
    "o dificultad para soltar estructuras materiales que ya no tienen vida real.\n\n"

    "El aprendizaje pasa por construir seguridad desde algo más profundo que la acumulación o el control."
),

3: (
    "Plutón en Casa 3 intensifica el pensamiento, la comunicación y la necesidad de comprender lo que hay debajo de las apariencias. "
    "Te cuesta quedarte en conversaciones o ideas demasiado superficiales.\n\n"

    "Puede haber pensamientos obsesivos, necesidad de investigar profundamente "
    "o intensidad al comunicar lo que percibes.\n\n"

    "El aprendizaje está en permitir profundidad mental sin quedar atrapade en análisis constantes."
),

4: (
    "Plutón en Casa 4 intensifica muchísimo la vida emocional profunda, la historia familiar y la sensación de base interna. "
    "Las transformaciones suelen afectar directamente a lo que sentías como refugio o estabilidad emocional.\n\n"

    "Puede haber necesidad de revisar patrones muy antiguos, emociones profundas "
    "o formas de protección que ya no funcionan igual.\n\n"

    "El aprendizaje pasa por construir una base más consciente sin intentar mantener intacto lo que necesita transformarse."
),

5: (
    "Plutón en Casa 5 intensifica la creatividad, el deseo y la necesidad de expresarte de forma auténtica. "
    "Las experiencias relacionadas con amor, creación o reconocimiento suelen vivirse con mucha profundidad.\n\n"

    "Puede haber intensidad emocional en vínculos afectivos, necesidad fuerte de expresión "
    "o dificultad para crear desde un lugar ligero o superficial.\n\n"

    "El aprendizaje está en expresar lo que eres sin convertir cada experiencia emocional en una lucha de intensidad."
),

6: (
    "Plutón en Casa 6 intensifica muchísimo la relación con trabajo, hábitos, exigencia y funcionamiento cotidiano. "
    "Puede costarte bajar el nivel de control o de presión interna sobre cómo haces las cosas.\n\n"

    "A veces llevas el cuerpo, la rutina o la autoexigencia hasta el límite "
    "antes de permitir cambios reales en la manera de vivir el día a día.\n\n"

    "El aprendizaje pasa por desarrollar formas de organización más sostenibles y menos basadas en tensión constante."
),

7: (
    "Plutón en Casa 7 intensifica profundamente los vínculos y las relaciones cercanas. "
    "Las relaciones rara vez se viven desde la superficialidad.\n\n"

    "Puede haber miedo a perder vínculos importantes, dinámicas intensas de control o dependencia "
    "o necesidad de transformación profunda dentro de las relaciones.\n\n"

    "El aprendizaje está en construir vínculos honestos y profundos sin quedar atrapade en dinámicas de poder o tensión permanente."
),

8: (
    "Plutón en Casa 8 intensifica muchísimo los procesos emocionales profundos, las transformaciones internas y todo lo relacionado con pérdida, cambio y regeneración. "
    "Las experiencias suelen vivirse con gran intensidad emocional.\n\n"

    "Puede haber necesidad de comprender lo oculto, atravesar procesos internos muy profundos "
    "o sensación de que determinadas etapas cambian completamente tu forma de vivir.\n\n"

    "El aprendizaje pasa por permitir transformación profunda sin vivir constantemente desde el control o la amenaza."
),

9: (
    "Plutón en Casa 9 intensifica la búsqueda de sentido, verdad y dirección vital. "
    "Las creencias y visiones de vida rara vez permanecen iguales después de ciertas experiencias.\n\n"

    "Puede haber necesidad intensa de encontrar propósito real, revisar profundamente ideas antiguas "
    "o atravesar cambios muy fuertes de visión y dirección.\n\n"

    "El aprendizaje está en sostener una búsqueda profunda sin convertir cada verdad en algo absoluto."
),

10: (
    "Plutón en Casa 10 intensifica muchísimo la relación con logro, responsabilidad y dirección profesional. "
    "Las transformaciones suelen afectar directamente a lo que construyes hacia fuera.\n\n"

    "Puede haber necesidad de control sobre la dirección de vida, miedo a perder posición "
    "o sensación de que determinadas etapas obligan a reconstruir completamente la forma de vivir el trabajo o el reconocimiento.\n\n"

    "El aprendizaje pasa por construir desde mayor coherencia interna y no solo desde esfuerzo o resistencia."
),

11: (
    "Plutón en Casa 11 intensifica la relación con grupos, proyectos colectivos e ideales de futuro. "
    "Las experiencias colectivas suelen vivirse con mucha profundidad y pocas veces desde la superficialidad.\n\n"

    "Puede haber rupturas importantes con grupos, necesidad de transformación en amistades "
    "o tensión entre pertenecer y mantener autenticidad propia.\n\n"

    "El aprendizaje está en participar en lo colectivo sin perder libertad ni quedar atrapade en dinámicas grupales intensas."
),

12: (
    "Plutón en Casa 12 intensifica muchísimo los procesos internos y las transformaciones que ocurren lejos de la mirada externa. "
    "Muchas veces los cambios más profundos empiezan mucho antes de hacerse visibles.\n\n"

    "Puede haber etapas de retiro, procesos emocionales difíciles de explicar "
    "o sensación de estar atravesando algo muy profundo sin poder entenderlo completamente al principio.\n\n"

    "El aprendizaje pasa por desarrollar más consciencia interna sin vivir permanentemente desde la acumulación silenciosa de tensión."
),

}

# ─── ASPECTOS ENTRE PLANETAS TRANSPERSONALES Y PERSONALES ─────────────────────
# Urano/Neptuno/Plutón × Sol/Luna/Mercurio/Venus/Marte

ASPECTOS_TRANS = {

# ── Urano – Sol ───────────────────────────────────────────────────────────────

("Urano", "Sol", "="): (
    "Urano en conjunción con el Sol hace que los cambios afecten directamente a tu dirección de vida y a la forma en que necesitas afirmarte. "
    "Es difícil sostener durante mucho tiempo caminos, decisiones o identidades que ya no sientes vivas.\n\n"

    "Puede haber necesidad constante de cambio, etapas de giros importantes "
    "o dificultad para mantener una dirección estable durante largos periodos.\n\n"

    "El aprendizaje está en permitir evolución sin sentir que necesitas romperlo todo cada vez que algo cambia."
),

("Urano", "Sol", "□"): (
    "Urano en cuadratura al Sol genera tensión entre necesidad de estabilidad y necesidad de cambio. "
    "Una parte de ti intenta mantener dirección y continuidad, mientras otra necesita romper con lo que ya no encaja.\n\n"

    "Puede haber etapas de cambios bruscos, decisiones inesperadas "
    "o sensación de no poder sostener durante mucho tiempo la misma orientación.\n\n"

    "El aprendizaje pasa por reconocer antes qué necesita actualizarse para no llegar siempre al cambio desde la ruptura."
),

("Urano", "Sol", "☍"): (
    "Urano en oposición al Sol intensifica la tensión entre mantener una dirección clara y permitir cambios profundos. "
    "A veces sientes que cuando logras estabilidad aparece inmediatamente la necesidad de modificar algo.\n\n"

    "Puede haber dificultad para sostener continuidad sin sentir limitación, "
    "o cambios importantes que alteran la dirección que parecía definida.\n\n"

    "El aprendizaje está en encontrar una forma de avanzar que incluya movimiento y actualización sin perder completamente el centro."
),

("Urano", "Sol", "△"): (
    "Urano en trígono al Sol facilita integrar cambio, autenticidad y dirección personal. "
    "Las transformaciones suelen sentirse más naturales y menos destructivas.\n\n"

    "Puedes adaptarte bien a nuevas etapas, actualizar decisiones con rapidez "
    "y permitir evolución sin sentir que pierdes completamente estabilidad.\n\n"

    "El aprendizaje pasa por usar esa capacidad de renovación de forma consciente y sostenida."
),

("Urano", "Sol", "✶"): (
    "Urano en sextil al Sol facilita abrir cambios y nuevas posibilidades sin necesidad de ruptura constante. "
    "Existe capacidad para introducir movimiento y actualización de manera bastante consciente.\n\n"

    "Las oportunidades de cambio suelen aparecer cuando te permites salir un poco de lo habitual "
    "sin necesidad de destruir lo que ya funciona.\n\n"

    "El aprendizaje está en aprovechar esa apertura al cambio antes de que la vida tenga que forzarla."
),

# ── Urano – Luna ──────────────────────────────────────────────────────────────

("Urano", "Luna", "="): (
    "Urano en conjunción con la Luna hace que los cambios afecten directamente a tu mundo emocional y a la forma en que buscas estabilidad interna. "
    "Puede costarte sostener durante mucho tiempo estados emocionales demasiado previsibles o estructuras afectivas rígidas.\n\n"

    "A veces hay cambios emocionales rápidos, necesidad de más espacio "
    "o sensación de que algo interno se mueve antes de que puedas entenderlo del todo.\n\n"

    "El aprendizaje está en desarrollar estabilidad emocional sin intentar eliminar completamente el cambio."
),

("Urano", "Luna", "□"): (
    "Urano en cuadratura a la Luna genera tensión entre necesidad de estabilidad emocional y necesidad de cambio. "
    "Una parte de ti busca seguridad, continuidad o refugio, mientras otra necesita movimiento y renovación.\n\n"

    "Puede haber cambios emocionales bruscos, dificultad para sostener ritmos estables "
    "o sensación de desregulación cuando algo empieza a volverse demasiado fijo.\n\n"

    "El aprendizaje pasa por introducir cambios antes de llegar al desbordamiento o a la ruptura emocional."
),

("Urano", "Luna", "☍"): (
    "Urano en oposición a la Luna intensifica la tensión entre estabilidad emocional y necesidad de libertad. "
    "A veces sientes que cuando algo empieza a darte seguridad aparece inmediatamente la necesidad de tomar distancia o cambiar.\n\n"

    "Puede haber dificultad para sostener vínculos, espacios o dinámicas demasiado previsibles "
    "sin sentir limitación emocional.\n\n"

    "El aprendizaje está en construir estabilidad sin sentir que eso implica perder libertad interna."
),

("Urano", "Luna", "△"): (
    "Urano en trígono a la Luna facilita integrar cambio y estabilidad emocional. "
    "Sueles adaptarte bien a nuevas etapas sin perder completamente el equilibrio interno.\n\n"

    "Los cambios emocionales pueden ayudarte a renovarte en lugar de desestabilizarte profundamente.\n\n"

    "El aprendizaje pasa por usar esa capacidad de adaptación de forma consciente y sostenida."
),

("Urano", "Luna", "✶"): (
    "Urano en sextil a la Luna facilita introducir cambios emocionales de manera bastante natural. "
    "Existe capacidad para renovar dinámicas internas sin necesidad de ruptura constante.\n\n"

    "Las nuevas experiencias suelen ayudarte a comprender mejor lo que necesitas emocionalmente.\n\n"

    "El aprendizaje está en escuchar antes las señales de cambio para no esperar a que todo tenga que romperse."
),

# ── Urano – Mercurio ──────────────────────────────────────────────────────────

("Urano", "Mercurio", "="): (
    "Urano en conjunción con Mercurio hace que la mente funcione de forma rápida, intuitiva y poco lineal. "
    "Las ideas aparecen de golpe y muchas veces necesitas cambiar de perspectiva constantemente.\n\n"

    "Puede haber mucha creatividad mental, asociaciones inesperadas "
    "o dificultad para sostener formas de pensamiento demasiado rígidas.\n\n"

    "El aprendizaje pasa por ordenar las ideas sin perder frescura ni capacidad de innovación."
),

("Urano", "Mercurio", "□"): (
    "Urano en cuadratura a Mercurio genera tensión entre necesidad de claridad mental y necesidad de cambio constante. "
    "A veces la mente va tan rápido que cuesta mantener continuidad o terminar lo que empiezas a desarrollar.\n\n"

    "Puede haber pensamientos acelerados, cambios bruscos de idea "
    "o dificultad para sostener una dirección mental durante mucho tiempo.\n\n"

    "El aprendizaje está en encontrar más estabilidad mental sin apagar la creatividad ni la capacidad de ver nuevas posibilidades."
),

("Urano", "Mercurio", "☍"): (
    "Urano en oposición a Mercurio intensifica la tensión entre pensamiento estructurado y necesidad de romper esquemas mentales. "
    "A veces sientes que cuando intentas ordenar algo aparece inmediatamente una nueva posibilidad que cambia la perspectiva.\n\n"

    "Puede haber dificultad para mantener foco, exceso de estímulo mental "
    "o sensación de que la mente nunca descansa del todo.\n\n"

    "El aprendizaje pasa por permitir apertura mental sin dispersarte constantemente."
),

("Urano", "Mercurio", "△"): (
    "Urano en trígono a Mercurio facilita pensar de forma original, flexible y creativa. "
    "Las nuevas ideas suelen aparecer con bastante naturalidad.\n\n"

    "Existe capacidad para adaptarte rápido a cambios, aprender cosas nuevas "
    "y encontrar soluciones poco convencionales.\n\n"

    "El aprendizaje está en dar continuidad a las ideas para que puedan desarrollarse realmente."
),

("Urano", "Mercurio", "✶"): (
    "Urano en sextil a Mercurio facilita introducir nuevas perspectivas sin necesidad de romper completamente con lo anterior. "
    "La mente suele responder bien a la innovación y al cambio.\n\n"

    "Puede haber curiosidad constante, facilidad para conectar ideas "
    "y apertura hacia formas distintas de pensar.\n\n"

    "El aprendizaje pasa por usar esa flexibilidad mental de manera más enfocada y consciente."
),

# ── Urano – Venus ─────────────────────────────────────────────────────────────

("Urano", "Venus", "="): (
    "Urano en conjunción con Venus hace que necesites libertad y autenticidad en los vínculos. "
    "Puede costarte sostener relaciones demasiado previsibles o estructuras afectivas que sientes estancadas.\n\n"

    "A veces aparecen cambios repentinos en relaciones, gustos o formas de vincularte. "
    "La necesidad de espacio puede ser muy importante para ti.\n\n"

    "El aprendizaje está en construir vínculos donde exista libertad sin necesidad de ruptura constante."
),

("Urano", "Venus", "□"): (
    "Urano en cuadratura a Venus genera tensión entre necesidad de estabilidad afectiva y necesidad de cambio. "
    "Una parte de ti busca cercanía y continuidad, mientras otra necesita espacio, movimiento y renovación.\n\n"

    "Puede haber relaciones intensas pero difíciles de estabilizar "
    "o cambios importantes en la manera de vincularte.\n\n"

    "El aprendizaje pasa por construir relaciones más flexibles sin vivir cada cambio como amenaza o ruptura."
),

("Urano", "Venus", "☍"): (
    "Urano en oposición a Venus intensifica la tensión entre vínculo y libertad personal. "
    "A veces cuando una relación empieza a sentirse estable aparece la necesidad de tomar distancia o cambiar algo.\n\n"

    "Puede haber dificultad para sostener dinámicas demasiado previsibles "
    "o necesidad de mucho espacio dentro de los vínculos.\n\n"

    "El aprendizaje está en encontrar formas de relación donde libertad y cercanía puedan convivir."
),

("Urano", "Venus", "△"): (
    "Urano en trígono a Venus facilita vivir los vínculos desde mayor libertad y autenticidad. "
    "Los cambios afectivos suelen integrarse con más naturalidad.\n\n"

    "Puede haber apertura a relaciones poco convencionales "
    "o facilidad para adaptarte a nuevas formas de compartir.\n\n"

    "El aprendizaje pasa por sostener los vínculos también en el tiempo, no solo en la intensidad del cambio."
),

("Urano", "Venus", "✶"): (
    "Urano en sextil a Venus facilita introducir renovación y movimiento en las relaciones de manera bastante consciente. "
    "Existe capacidad para transformar vínculos sin necesidad de ruptura permanente.\n\n"

    "Las nuevas experiencias afectivas suelen ayudarte a comprender mejor qué necesitas realmente.\n\n"

    "El aprendizaje está en permitir cambios graduales antes de llegar al corte brusco."
),

# ── Urano – Marte ─────────────────────────────────────────────────────────────

("Urano", "Marte", "="): (
    "Urano en conjunción con Marte intensifica muchísimo la necesidad de actuar con libertad y rapidez. "
    "Puede costarte contener impulsos o sostener durante mucho tiempo acciones demasiado lentas o limitantes.\n\n"

    "A veces actúas de forma repentina, cambias de dirección rápidamente "
    "o necesitas movimiento constante para sentir vitalidad.\n\n"

    "El aprendizaje está en canalizar la energía sin vivir permanentemente desde la impulsividad o la ruptura."
),

("Urano", "Marte", "□"): (
    "Urano en cuadratura a Marte genera tensión entre impulso de acción y cambios inesperados. "
    "Muchas veces cuando intentas avanzar en una dirección aparece algo que altera el ritmo o modifica el camino.\n\n"

    "Puede haber impulsividad, dificultad para sostener continuidad "
    "o sensación de actuar demasiado rápido y corregir después.\n\n"

    "El aprendizaje pasa por desarrollar más consciencia antes de reaccionar automáticamente."
),

("Urano", "Marte", "☍"): (
    "Urano en oposición a Marte intensifica la tensión entre necesidad de actuar y necesidad de romper con lo que limita. "
    "A veces sientes mucha energía disponible pero dificultad para dirigirla de forma estable.\n\n"

    "Puede haber acciones bruscas, cambios repentinos de dirección "
    "o dificultad para sostener ritmos constantes.\n\n"

    "El aprendizaje está en encontrar formas de movimiento más conscientes y menos reactivas."
),

("Urano", "Marte", "△"): (
    "Urano en trígono a Marte facilita actuar con rapidez, flexibilidad y capacidad de adaptación. "
    "Los cambios suelen sentirse más estimulantes que amenazantes.\n\n"

    "Existe facilidad para reaccionar rápido, innovar "
    "y moverte hacia nuevas experiencias sin demasiado miedo.\n\n"

    "El aprendizaje pasa por sostener la dirección el tiempo suficiente para consolidar lo que empiezas."
),

("Urano", "Marte", "✶"): (
    "Urano en sextil a Marte facilita introducir cambios en la acción de manera bastante natural. "
    "Existe capacidad para reaccionar rápido sin perder completamente el equilibrio.\n\n"

    "Las nuevas experiencias suelen activar motivación, movimiento "
    "y ganas de probar caminos distintos.\n\n"

    "El aprendizaje está en usar esa capacidad de cambio de forma más enfocada y consciente."
),

# ── Neptuno – Sol ─────────────────────────────────────────────────────────────

("Neptuno", "Sol", "="): (
    "Neptuno en conjunción con el Sol puede hacer que te cueste definir con claridad quién eres o hacia dónde quieres dirigir tu vida. "
    "A veces sientes una dirección muy inspiradora y otras veces todo parece perder forma.\n\n"

    "Puede haber mucha sensibilidad, imaginación o necesidad de encontrar algo que tenga sentido profundo para ti, "
    "pero también momentos de confusión respecto a identidad, propósito o dirección.\n\n"

    "El aprendizaje está en construir una dirección más consciente sin exigirte claridad absoluta en todo momento."
),

("Neptuno", "Sol", "□"): (
    "Neptuno en cuadratura al Sol genera tensión entre necesidad de claridad y tendencia a la dispersión o la confusión. "
    "Una parte de ti busca dirección definida, mientras otra necesita abrirse a algo más amplio o difícil de concretar.\n\n"

    "Puede haber sensación de desorientación, dificultad para sostener decisiones "
    "o etapas donde lo que parecía claro deja de tener forma.\n\n"

    "El aprendizaje pasa por reconocer antes cuándo algo ya no tiene suficiente verdad para seguir sosteniéndolo."
),

("Neptuno", "Sol", "☍"): (
    "Neptuno en oposición al Sol intensifica la tensión entre dirección personal y tendencia a perder claridad o límites. "
    "A veces sientes que cuanto más intentas definir algo, más difuso se vuelve.\n\n"

    "Puede haber idealización de caminos, personas o proyectos "
    "que después muestran menos consistencia real de la que parecía.\n\n"

    "El aprendizaje está en desarrollar más discernimiento sin perder sensibilidad ni capacidad de inspiración."
),

("Neptuno", "Sol", "△"): (
    "Neptuno en trígono al Sol facilita integrar sensibilidad, intuición y dirección personal. "
    "La imaginación y la inspiración suelen alimentar tu camino de forma bastante natural.\n\n"

    "Puede haber capacidad para conectar con experiencias profundas "
    "sin perder completamente la referencia de quién eres o hacia dónde vas.\n\n"

    "El aprendizaje pasa por dar forma concreta a lo que imaginas o percibes internamente."
),

("Neptuno", "Sol", "✶"): (
    "Neptuno en sextil al Sol facilita abrir sensibilidad e inspiración sin perder completamente claridad interna. "
    "Existe capacidad para integrar intuición y dirección de manera bastante consciente.\n\n"

    "Las experiencias emocionales, simbólicas o creativas suelen ayudarte a comprender mejor tu camino.\n\n"

    "El aprendizaje está en sostener esa conexión interna también en lo cotidiano y concreto."
),

# ── Neptuno – Luna ────────────────────────────────────────────────────────────

("Neptuno", "Luna", "="): (
    "Neptuno en conjunción con la Luna intensifica muchísimo la sensibilidad emocional. "
    "Puede costarte distinguir claramente qué sientes tú y qué estás absorbiendo del entorno.\n\n"

    "A veces hay mucha empatía, intuición y conexión emocional, "
    "pero también etapas de confusión, desbordamiento o sensación de perderte en lo que sienten otras personas.\n\n"

    "El aprendizaje está en desarrollar límites emocionales más conscientes sin cerrar la sensibilidad."
),

("Neptuno", "Luna", "□"): (
    "Neptuno en cuadratura a la Luna genera tensión entre necesidad de estabilidad emocional y tendencia a la dispersión o la permeabilidad emocional. "
    "Una parte de ti busca seguridad y otra absorbe constantemente lo que ocurre alrededor.\n\n"

    "Puede haber dificultad para entender lo que sientes realmente, "
    "idealización emocional o sensación de agotamiento cuando no existen suficientes límites.\n\n"

    "El aprendizaje pasa por cuidar mejor tu energía emocional sin endurecerte internamente."
),

("Neptuno", "Luna", "☍"): (
    "Neptuno en oposición a la Luna intensifica la tensión entre necesidad de estabilidad emocional y tendencia a disolver límites internos. "
    "A veces sientes mucha conexión emocional con el entorno pero poca claridad sobre tus propias necesidades.\n\n"

    "Puede haber confusión emocional, dificultad para sostener estabilidad "
    "o tendencia a absorber demasiado de otras personas o ambientes.\n\n"

    "El aprendizaje está en desarrollar más diferenciación emocional sin perder sensibilidad."
),

("Neptuno", "Luna", "△"): (
    "Neptuno en trígono a la Luna facilita integrar sensibilidad emocional e intuición de manera bastante natural. "
    "Existe capacidad para conectar profundamente con lo emocional sin perder completamente estabilidad interna.\n\n"

    "La empatía, la imaginación y la sensibilidad suelen sentirse fluidas y naturales.\n\n"

    "El aprendizaje pasa por sostener límites saludables incluso cuando todo parece fluir fácilmente."
),

("Neptuno", "Luna", "✶"): (
    "Neptuno en sextil a la Luna facilita abrir sensibilidad emocional e intuición de forma bastante consciente. "
    "Las experiencias emocionales profundas suelen ayudarte a comprenderte mejor.\n\n"

    "Puede haber mucha capacidad de empatía, conexión emocional "
    "o sensibilidad hacia lo simbólico y lo no verbal.\n\n"

    "El aprendizaje está en mantener claridad emocional sin cerrar esa apertura interna."
),

# ── Neptuno – Mercurio ────────────────────────────────────────────────────────

("Neptuno", "Mercurio", "="): (
    "Neptuno en conjunción con Mercurio hace que la mente funcione de forma muy intuitiva, imaginativa y asociativa. "
    "A veces percibes muchas cosas a la vez y cuesta ordenar todo con claridad.\n\n"

    "Puede haber gran sensibilidad mental, creatividad o capacidad simbólica, "
    "pero también dificultad para sostener precisión o foco constante.\n\n"

    "El aprendizaje está en desarrollar más claridad mental sin perder imaginación ni intuición."
),

("Neptuno", "Mercurio", "□"): (
    "Neptuno en cuadratura a Mercurio genera tensión entre claridad mental e intuición difusa. "
    "Una parte de ti necesita precisión y otra funciona desde sensaciones, imágenes o percepciones difíciles de explicar racionalmente.\n\n"

    "Puede haber confusión mental, dispersión "
    "o dificultad para distinguir claramente entre intuición y proyección.\n\n"

    "El aprendizaje pasa por desarrollar discernimiento sin desconectarte de la sensibilidad mental."
),

("Neptuno", "Mercurio", "☍"): (
    "Neptuno en oposición a Mercurio intensifica la tensión entre pensamiento racional e intuición. "
    "A veces la mente intenta entender algo que internamente todavía no tiene forma clara.\n\n"

    "Puede haber cambios de percepción, dificultad para mantener foco "
    "o sensación de no poder explicar del todo lo que percibes.\n\n"

    "El aprendizaje está en permitir sensibilidad mental sin perder completamente claridad y estructura."
),

("Neptuno", "Mercurio", "△"): (
    "Neptuno en trígono a Mercurio facilita integrar intuición, imaginación y pensamiento. "
    "Las ideas suelen surgir de manera muy inspirada y conectada.\n\n"

    "Puede haber creatividad mental, sensibilidad artística "
    "o capacidad para comprender dimensiones más simbólicas o emocionales de la experiencia.\n\n"

    "El aprendizaje pasa por aterrizar las ideas para que puedan tomar forma concreta."
),

("Neptuno", "Mercurio", "✶"): (
    "Neptuno en sextil a Mercurio facilita conectar intuición y pensamiento de forma bastante natural. "
    "Existe capacidad para abrir nuevas perspectivas sin perder completamente claridad.\n\n"

    "La imaginación y la sensibilidad suelen enriquecer mucho la manera de pensar y comunicar.\n\n"

    "El aprendizaje está en sostener más foco y continuidad en las ideas."
),

# ── Neptuno – Venus ───────────────────────────────────────────────────────────

("Neptuno", "Venus", "="): (
    "Neptuno en conjunción con Venus intensifica muchísimo la sensibilidad afectiva y la tendencia a idealizar vínculos o experiencias emocionales. "
    "Puede costarte ver con claridad qué ocurre realmente en una relación.\n\n"

    "A veces hay mucha entrega, romanticismo o necesidad de conexión profunda, "
    "pero también dificultad para sostener límites claros.\n\n"

    "El aprendizaje está en amar sin perder completamente la referencia de ti."
),

("Neptuno", "Venus", "□"): (
    "Neptuno en cuadratura a Venus genera tensión entre necesidad de vínculo y dificultad para mantener claridad emocional y afectiva. "
    "Una parte de ti busca conexión ideal y otra necesita reconocer la realidad de lo que está viviendo.\n\n"

    "Puede haber idealización de relaciones, dificultad para poner límites "
    "o tendencia a sostener vínculos poco claros durante demasiado tiempo.\n\n"

    "El aprendizaje pasa por construir relaciones más conscientes sin cerrar la sensibilidad afectiva."
),

("Neptuno", "Venus", "☍"): (
    "Neptuno en oposición a Venus intensifica la tensión entre amor idealizado y realidad emocional. "
    "A veces necesitas creer profundamente en un vínculo incluso cuando algo interno percibe confusión.\n\n"

    "Puede haber dificultad para distinguir claramente entre entrega, proyección y necesidad emocional.\n\n"

    "El aprendizaje está en desarrollar más claridad afectiva sin perder capacidad de amor y sensibilidad."
),

("Neptuno", "Venus", "△"): (
    "Neptuno en trígono a Venus facilita integrar sensibilidad, amor y conexión emocional profunda. "
    "Los vínculos suelen vivirse con mucha empatía e inspiración.\n\n"

    "Puede haber gran sensibilidad artística o afectiva "
    "y capacidad para conectar emocionalmente de forma muy profunda.\n\n"

    "El aprendizaje pasa por sostener límites sanos incluso dentro de relaciones muy intensas emocionalmente."
),

("Neptuno", "Venus", "✶"): (
    "Neptuno en sextil a Venus facilita abrir sensibilidad afectiva y emocional de manera bastante natural. "
    "Existe capacidad para conectar profundamente sin perder completamente estabilidad.\n\n"

    "Las experiencias emocionales suelen ayudarte a comprender mejor qué valoras realmente.\n\n"

    "El aprendizaje está en mantener claridad emocional también cuando el vínculo es muy intenso."
),

# ── Neptuno – Marte ───────────────────────────────────────────────────────────

("Neptuno", "Marte", "="): (
    "Neptuno en conjunción con Marte puede hacer que la energía y la acción funcionen de forma muy inspirada pero difícil de sostener con claridad constante. "
    "A veces sientes mucho impulso y otras veces parece desaparecer completamente.\n\n"

    "Puede haber dificultad para dirigir la energía con precisión "
    "o sensación de actuar desde intuiciones difíciles de explicar racionalmente.\n\n"

    "El aprendizaje está en desarrollar dirección y foco sin desconectarte de la sensibilidad."
),

("Neptuno", "Marte", "□"): (
    "Neptuno en cuadratura a Marte genera tensión entre acción clara y tendencia a la dispersión o la falta de dirección. "
    "Una parte de ti quiere avanzar y otra pierde fuerza cuando el camino deja de sentirse inspirado.\n\n"

    "Puede haber cansancio, confusión respecto a objetivos "
    "o sensación de invertir energía en algo que después pierde sentido.\n\n"

    "El aprendizaje pasa por actuar desde mayor claridad sin exigir certeza absoluta antes de moverte."
),

("Neptuno", "Marte", "☍"): (
    "Neptuno en oposición a Marte intensifica la tensión entre impulso de acción y tendencia a perder dirección o límites claros. "
    "A veces quieres avanzar con fuerza pero algo interno disuelve rápidamente la motivación o el objetivo.\n\n"

    "Puede haber dificultad para sostener continuidad en la acción "
    "o sensación de moverte desde impulsos difíciles de concretar.\n\n"

    "El aprendizaje está en encontrar una forma de actuar más consciente y conectada con lo que realmente tiene sentido para ti."
),

("Neptuno", "Marte", "△"): (
    "Neptuno en trígono a Marte facilita integrar intuición, sensibilidad y acción. "
    "La energía suele fluir mejor cuando actúas desde inspiración o conexión interna.\n\n"

    "Puede haber creatividad, sensibilidad corporal "
    "o capacidad para actuar con bastante intuición y flexibilidad.\n\n"

    "El aprendizaje pasa por sostener dirección y constancia también cuando la inspiración baja."
),

("Neptuno", "Marte", "✶"): (
    "Neptuno en sextil a Marte facilita actuar desde sensibilidad e intuición sin perder completamente eficacia. "
    "Existe capacidad para adaptar la acción según lo que sientes internamente.\n\n"

    "Las experiencias emocionales y simbólicas suelen ayudarte a comprender hacia dónde dirigir la energía.\n\n"

    "El aprendizaje está en mantener más claridad y continuidad en lo que decides impulsar."
),

# ── Plutón – Sol ──────────────────────────────────────────────────────────────

("Plutón", "Sol", "="): (
    "Plutón en conjunción con el Sol intensifica muchísimo la necesidad de vivir con autenticidad y profundidad. "
    "Es difícil sostener durante mucho tiempo direcciones de vida que ya no tienen verdad interna.\n\n"

    "Puede haber etapas de transformación muy profundas, necesidad de control "
    "o sensación de que determinadas experiencias cambian completamente quién eres.\n\n"

    "El aprendizaje está en permitir transformación sin vivir permanentemente desde la tensión o la intensidad extrema."
),

("Plutón", "Sol", "□"): (
    "Plutón en cuadratura al Sol genera tensión entre la dirección que intentas sostener y procesos de transformación que ya no pueden evitarse. "
    "A veces una parte de ti quiere mantener control y otra necesita cambiar profundamente.\n\n"

    "Puede haber crisis importantes, sensación de presión interna "
    "o etapas donde determinadas estructuras dejan de sostenerse.\n\n"

    "El aprendizaje pasa por reconocer antes qué necesita transformarse para no llegar siempre al límite."
),

("Plutón", "Sol", "☍"): (
    "Plutón en oposición al Sol intensifica la tensión entre identidad personal y procesos profundos de cambio. "
    "A veces sientes que cuanto más intentas sostener una dirección fija, más fuerza aparece empujando hacia la transformación.\n\n"

    "Puede haber relaciones intensas con poder, control "
    "o experiencias que cambian profundamente tu manera de vivir.\n\n"

    "El aprendizaje está en encontrar una forma de sostenerte sin necesitar controlar completamente cada proceso."
),

("Plutón", "Sol", "△"): (
    "Plutón en trígono al Sol facilita integrar profundidad, transformación y dirección personal. "
    "Los cambios importantes suelen sentirse intensos pero naturales.\n\n"

    "Existe capacidad para atravesar procesos profundos "
    "sin perder completamente estabilidad ni claridad interna.\n\n"

    "El aprendizaje pasa por usar esa capacidad de transformación de manera consciente y constructiva."
),

("Plutón", "Sol", "✶"): (
    "Plutón en sextil al Sol facilita abrir procesos de transformación sin necesidad de llegar siempre a situaciones extremas. "
    "Existe capacidad para reconocer antes lo que necesita cambiar.\n\n"

    "Las experiencias intensas suelen ayudarte a comprender mejor quién eres "
    "y hacia dónde quieres dirigir tu vida.\n\n"

    "El aprendizaje está en permitir cambios graduales antes de que la vida tenga que forzarlos."
),

# ── Plutón – Luna ─────────────────────────────────────────────────────────────

("Plutón", "Luna", "="): (
    "Plutón en conjunción con la Luna intensifica muchísimo la vida emocional y los procesos internos profundos. "
    "Las emociones rara vez se viven de manera superficial.\n\n"

    "Puede haber gran sensibilidad emocional, necesidad de control interno "
    "o sensación de atravesar cambios emocionales muy profundos a lo largo de la vida.\n\n"

    "El aprendizaje está en permitir transformación emocional sin vivir permanentemente desde la intensidad o la amenaza."
),

("Plutón", "Luna", "□"): (
    "Plutón en cuadratura a la Luna genera tensión entre necesidad de estabilidad emocional y procesos internos de transformación profunda. "
    "A veces intentas sostener seguridad emocional mientras algo dentro de ti ya necesita cambiar.\n\n"

    "Puede haber emociones muy intensas, dificultad para soltar determinadas dinámicas "
    "o sensación de acumulación emocional.\n\n"

    "El aprendizaje pasa por reconocer antes lo que necesitas transformar emocionalmente."
),

("Plutón", "Luna", "☍"): (
    "Plutón en oposición a la Luna intensifica la tensión entre estabilidad emocional y profundidad emocional extrema. "
    "A veces cuando buscas calma o seguridad aparece algo interno que remueve todo nuevamente.\n\n"

    "Puede haber miedo a perder control emocional, vínculos intensos "
    "o dificultad para sostener equilibrio en determinadas etapas.\n\n"

    "El aprendizaje está en desarrollar seguridad emocional sin intentar controlar completamente lo que sientes."
),

("Plutón", "Luna", "△"): (
    "Plutón en trígono a la Luna facilita integrar profundidad emocional y capacidad de transformación interna. "
    "Las emociones intensas suelen ayudarte a crecer y comprenderte mejor.\n\n"

    "Existe capacidad para atravesar procesos emocionales profundos "
    "sin perder completamente estabilidad interna.\n\n"

    "El aprendizaje pasa por utilizar esa profundidad emocional de forma consciente y constructiva."
),

("Plutón", "Luna", "✶"): (
    "Plutón en sextil a la Luna facilita abrir procesos emocionales profundos sin necesidad de llegar siempre al extremo. "
    "Existe capacidad para transformar patrones emocionales de manera bastante consciente.\n\n"

    "Las experiencias emocionales intensas suelen ayudarte a conocerte con más profundidad.\n\n"

    "El aprendizaje está en permitir cambios emocionales graduales antes de acumular demasiada tensión interna."
),

# ── Plutón – Mercurio ─────────────────────────────────────────────────────────

("Plutón", "Mercurio", "="): (
    "Plutón en conjunción con Mercurio intensifica muchísimo la mente y la necesidad de comprender lo que hay debajo de las apariencias. "
    "Te cuesta quedarte en explicaciones superficiales.\n\n"

    "Puede haber pensamientos obsesivos, gran capacidad de análisis "
    "o necesidad de investigar profundamente determinados temas.\n\n"

    "El aprendizaje está en permitir profundidad mental sin quedar atrapade en análisis constantes."
),

("Plutón", "Mercurio", "□"): (
    "Plutón en cuadratura a Mercurio genera tensión entre necesidad de claridad mental y tendencia a intensificar demasiado el pensamiento. "
    "A veces la mente entra en procesos muy profundos difíciles de detener.\n\n"

    "Puede haber pensamientos repetitivos, dificultad para soltar ideas "
    "o tendencia a analizar excesivamente determinadas situaciones.\n\n"

    "El aprendizaje pasa por desarrollar más descanso mental sin perder profundidad."
),

("Plutón", "Mercurio", "☍"): (
    "Plutón en oposición a Mercurio intensifica la tensión entre pensamiento racional y necesidad de comprender lo oculto o profundo. "
    "A veces cuanto más intentas entender algo, más complejidad aparece.\n\n"

    "Puede haber intensidad mental, dificultad para relativizar "
    "o necesidad de encontrar verdad absoluta en determinadas cuestiones.\n\n"

    "El aprendizaje está en permitir profundidad sin convertir cada pensamiento en una lucha interna."
),

("Plutón", "Mercurio", "△"): (
    "Plutón en trígono a Mercurio facilita integrar profundidad mental, análisis y capacidad de comprensión. "
    "La mente suele funcionar con intensidad pero también con bastante claridad.\n\n"

    "Existe capacidad para investigar, comprender procesos complejos "
    "y atravesar temas profundos sin perder completamente equilibrio mental.\n\n"

    "El aprendizaje pasa por usar esa profundidad de forma constructiva y no solo compulsiva."
),

("Plutón", "Mercurio", "✶"): (
    "Plutón en sextil a Mercurio facilita abrir procesos de comprensión profunda de manera bastante consciente. "
    "Existe capacidad para transformar la forma de pensar sin necesidad de crisis constantes.\n\n"

    "Las experiencias intensas suelen ayudarte a comprender mejor determinadas verdades internas.\n\n"

    "El aprendizaje está en equilibrar profundidad y ligereza mental."
),

# ── Plutón – Venus ────────────────────────────────────────────────────────────

("Plutón", "Venus", "="): (
    "Plutón en conjunción con Venus intensifica muchísimo los vínculos, el deseo y la necesidad de conexión profunda. "
    "Las relaciones rara vez se viven desde la superficialidad.\n\n"

    "Puede haber gran intensidad afectiva, miedo a perder vínculos importantes "
    "o dificultad para sostener relaciones poco profundas.\n\n"

    "El aprendizaje está en amar profundamente sin convertir el vínculo en una forma de control o dependencia."
),

("Plutón", "Venus", "□"): (
    "Plutón en cuadratura a Venus genera tensión entre necesidad de vínculo y procesos emocionales intensos que transforman la forma de relacionarte. "
    "A veces intentas sostener una relación mientras algo interno ya necesita cambiar profundamente.\n\n"

    "Puede haber relaciones intensas, celos, miedo a perder "
    "o dificultad para encontrar equilibrio emocional en los vínculos.\n\n"

    "El aprendizaje pasa por construir relaciones más conscientes y menos basadas en control o intensidad constante."
),

("Plutón", "Venus", "☍"): (
    "Plutón en oposición a Venus intensifica la tensión entre amor, apego y transformación emocional. "
    "A veces los vínculos activan procesos internos muy profundos difíciles de sostener desde la calma.\n\n"

    "Puede haber relaciones transformadoras, emociones extremas "
    "o sensación de que determinados vínculos cambian completamente tu vida.\n\n"

    "El aprendizaje está en sostener profundidad afectiva sin perder completamente estabilidad interna."
),

("Plutón", "Venus", "△"): (
    "Plutón en trígono a Venus facilita integrar profundidad emocional y capacidad de transformación en los vínculos. "
    "Las relaciones suelen vivirse con mucha intensidad pero también con capacidad de crecimiento.\n\n"

    "Existe profundidad afectiva, autenticidad emocional "
    "y capacidad para atravesar cambios importantes dentro de las relaciones.\n\n"

    "El aprendizaje pasa por usar esa intensidad para construir y no solo para remover."
),

("Plutón", "Venus", "✶"): (
    "Plutón en sextil a Venus facilita transformar vínculos y patrones afectivos de manera bastante consciente. "
    "Existe capacidad para reconocer antes qué relaciones o dinámicas necesitan cambiar.\n\n"

    "Las experiencias emocionales profundas suelen ayudarte a comprender mejor qué valoras realmente.\n\n"

    "El aprendizaje está en permitir transformación afectiva sin esperar siempre a llegar al límite."
),

# ── Plutón – Marte ────────────────────────────────────────────────────────────

("Plutón", "Marte", "="): (
    "Plutón en conjunción con Marte intensifica muchísimo la energía, la voluntad y la necesidad de actuar con fuerza. "
    "La intensidad suele sentirse directamente en la acción.\n\n"

    "Puede haber gran resistencia, mucha capacidad de esfuerzo "
    "o tendencia a actuar desde tensión acumulada.\n\n"

    "El aprendizaje está en usar la fuerza de manera consciente sin vivir permanentemente desde la presión o el combate."
),

("Plutón", "Marte", "□"): (
    "Plutón en cuadratura a Marte genera tensión entre impulso de acción y acumulación de intensidad interna. "
    "A veces cuanto más fuerza aplicas, más resistencia aparece.\n\n"

    "Puede haber enfado acumulado, necesidad de control "
    "o sensación de vivir determinadas situaciones como lucha constante.\n\n"

    "El aprendizaje pasa por desarrollar formas de acción menos basadas en tensión y confrontación."
),

("Plutón", "Marte", "☍"): (
    "Plutón en oposición a Marte intensifica la tensión entre necesidad de actuar y fuerzas internas o externas que generan resistencia. "
    "A veces sientes mucha energía disponible pero también mucha presión acumulada.\n\n"

    "Puede haber conflictos intensos, impulsividad "
    "o sensación de que determinadas acciones desencadenan procesos difíciles de controlar.\n\n"

    "El aprendizaje está en canalizar la fuerza sin convertir cada situación en una batalla."
),

("Plutón", "Marte", "△"): (
    "Plutón en trígono a Marte facilita integrar intensidad, voluntad y capacidad de transformación. "
    "La energía suele sentirse fuerte, enfocada y resistente.\n\n"

    "Existe capacidad para atravesar situaciones difíciles "
    "sin perder completamente dirección ni fuerza interna.\n\n"

    "El aprendizaje pasa por usar esa potencia de manera constructiva y no únicamente desde exigencia o control."
),

("Plutón", "Marte", "✶"): (
    "Plutón en sextil a Marte facilita canalizar intensidad y energía de manera bastante consciente. "
    "Existe capacidad para transformar formas de actuar sin necesidad de llegar siempre al extremo.\n\n"

    "Las experiencias intensas suelen ayudarte a desarrollar más fuerza interna y claridad en la acción.\n\n"

    "El aprendizaje está en permitir cambios graduales en lugar de esperar siempre a situaciones límite."
),
}


# ─── ASPECTOS ENTRE TRANSPERSONALES Y SOCIALES ────────────────────────────────

ASPECTOS_TRANS_SOCIALES = {

# ── Urano – Júpiter ───────────────────────────────────────────────────────────

("Urano", "Júpiter", "="): (
    "Urano en conjunción con Júpiter amplifica la necesidad de expansión, cambio y apertura a nuevas posibilidades. "
    "Puede costarte sostener durante mucho tiempo caminos demasiado previsibles o limitantes."
),

("Urano", "Júpiter", "□"): (
    "Urano en cuadratura a Júpiter genera tensión entre necesidad de expansión y dificultad para sostener continuidad. "
    "A veces aparecen cambios bruscos de dirección o exceso de impulso hacia nuevas posibilidades."
),

("Urano", "Júpiter", "☍"): (
    "Urano en oposición a Júpiter intensifica la tensión entre estabilidad y necesidad de apertura o cambio. "
    "Puede haber etapas de grandes giros vitales o dificultad para encontrar un equilibrio entre libertad y dirección."
),

("Urano", "Júpiter", "△"): (
    "Urano en trígono a Júpiter facilita integrar cambio, expansión y nuevas oportunidades. "
    "La apertura a nuevas experiencias suele sentirse estimulante y natural."
),

("Urano", "Júpiter", "✶"): (
    "Urano en sextil a Júpiter facilita introducir cambios y crecimiento de manera bastante consciente. "
    "Las nuevas posibilidades suelen aparecer cuando te permites salir de lo habitual."
),

# ── Urano – Saturno ───────────────────────────────────────────────────────────

("Urano", "Saturno", "="): (
    "Urano en conjunción con Saturno mezcla necesidad de estructura y necesidad de cambio. "
    "A veces alternas entre construir estabilidad y sentir necesidad de romper con ella para poder seguir creciendo."
),

("Urano", "Saturno", "□"): (
    "Urano en cuadratura a Saturno genera tensión entre estabilidad y transformación. "
    "Puede costarte sostener estructuras demasiado rígidas, pero también mantener continuidad cuando todo cambia demasiado rápido."
),

("Urano", "Saturno", "☍"): (
    "Urano en oposición a Saturno intensifica la tensión entre control y libertad. "
    "Una parte de ti necesita seguridad y otra necesita romper límites o estructuras establecidas."
),

("Urano", "Saturno", "△"): (
    "Urano en trígono a Saturno facilita integrar cambio y estabilidad. "
    "Existe capacidad para transformar estructuras sin necesidad de destruirlas completamente."
),

("Urano", "Saturno", "✶"): (
    "Urano en sextil a Saturno facilita introducir cambios graduales en la estructura de vida. "
    "La renovación puede producirse de manera más consciente y sostenible."
),

# ── Neptuno – Júpiter ─────────────────────────────────────────────────────────

("Neptuno", "Júpiter", "="): (
    "Neptuno en conjunción con Júpiter amplifica la sensibilidad, la inspiración y la búsqueda de sentido. "
    "Puede haber gran apertura espiritual o emocional, pero también tendencia a idealizar determinados caminos o creencias."
),

("Neptuno", "Júpiter", "□"): (
    "Neptuno en cuadratura a Júpiter genera tensión entre expansión y claridad. "
    "A veces cuesta distinguir entre intuición profunda e idealización."
),

("Neptuno", "Júpiter", "☍"): (
    "Neptuno en oposición a Júpiter intensifica la tensión entre búsqueda de sentido y dificultad para mantener referencias claras. "
    "Puede haber cambios importantes en creencias, ideales o dirección vital."
),

("Neptuno", "Júpiter", "△"): (
    "Neptuno en trígono a Júpiter facilita integrar inspiración, sensibilidad y apertura de conciencia. "
    "La búsqueda de sentido suele sentirse fluida y natural."
),

("Neptuno", "Júpiter", "✶"): (
    "Neptuno en sextil a Júpiter facilita abrir nuevas perspectivas internas de manera bastante consciente. "
    "Las experiencias sensibles o simbólicas suelen ayudarte a ampliar la visión de la vida."
),

# ── Neptuno – Saturno ─────────────────────────────────────────────────────────

("Neptuno", "Saturno", "="): (
    "Neptuno en conjunción con Saturno mezcla necesidad de estructura y sensibilidad profunda. "
    "Puede costarte encontrar formas de vida suficientemente sólidas sin sentir rigidez o vacío interno."
),

("Neptuno", "Saturno", "□"): (
    "Neptuno en cuadratura a Saturno genera tensión entre claridad estructural y sensación de incertidumbre o dispersión. "
    "A veces lo que intentas sostener pierde forma antes de consolidarse."
),

("Neptuno", "Saturno", "☍"): (
    "Neptuno en oposición a Saturno intensifica la tensión entre control y disolución de límites. "
    "Puede haber dificultad para encontrar equilibrio entre estructura y sensibilidad."
),

("Neptuno", "Saturno", "△"): (
    "Neptuno en trígono a Saturno facilita integrar sensibilidad y estructura. "
    "Existe capacidad para dar forma concreta a experiencias profundas o intuitivas."
),

("Neptuno", "Saturno", "✶"): (
    "Neptuno en sextil a Saturno facilita construir estructuras más sensibles y coherentes internamente. "
    "La intuición puede ayudarte a reorganizar la vida de manera más consciente."
),

# ── Plutón – Júpiter ──────────────────────────────────────────────────────────

("Plutón", "Júpiter", "="): (
    "Plutón en conjunción con Júpiter intensifica muchísimo la necesidad de crecimiento, expansión y transformación. "
    "Las creencias, metas o direcciones de vida suelen atravesar cambios profundos."
),

("Plutón", "Júpiter", "□"): (
    "Plutón en cuadratura a Júpiter genera tensión entre expansión y necesidad de control o transformación profunda. "
    "A veces los procesos de crecimiento llegan acompañados de crisis importantes."
),

("Plutón", "Júpiter", "☍"): (
    "Plutón en oposición a Júpiter intensifica la tensión entre apertura y transformación profunda. "
    "Determinadas experiencias cambian radicalmente la manera de entender la vida o el sentido."
),

("Plutón", "Júpiter", "△"): (
    "Plutón en trígono a Júpiter facilita integrar transformación profunda y crecimiento personal. "
    "Las crisis o cambios importantes suelen convertirse en oportunidades de evolución."
),

("Plutón", "Júpiter", "✶"): (
    "Plutón en sextil a Júpiter facilita transformar creencias, dirección y visión de vida de manera bastante consciente. "
    "Existe capacidad para crecer profundamente sin necesidad de llegar siempre al límite."
),

# ── Plutón – Saturno ──────────────────────────────────────────────────────────

("Plutón", "Saturno", "="): (
    "Plutón en conjunción con Saturno intensifica muchísimo los temas relacionados con estructura, control y responsabilidad. "
    "Determinadas etapas obligan a transformar profundamente formas de vida que ya no pueden sostenerse igual."
),

("Plutón", "Saturno", "□"): (
    "Plutón en cuadratura a Saturno genera tensión entre necesidad de estabilidad y procesos de transformación inevitables. "
    "Puede costarte soltar estructuras antiguas incluso cuando ya no tienen vida."
),

("Plutón", "Saturno", "☍"): (
    "Plutón en oposición a Saturno intensifica la tensión entre control y transformación profunda. "
    "A veces cuanto más intentas sostener algo, más presión aparece para que cambie."
),

("Plutón", "Saturno", "△"): (
    "Plutón en trígono a Saturno facilita integrar transformación y capacidad de sostén. "
    "Existe fuerza para atravesar cambios profundos sin perder completamente estructura."
),

("Plutón", "Saturno", "✶"): (
    "Plutón en sextil a Saturno facilita reorganizar estructuras importantes de manera bastante consciente. "
    "Los cambios profundos pueden realizarse con más estabilidad y claridad."
),

}


# ─── ASPECTOS ENTRE TRANSPERSONALES ───────────────────────────────────────────

ASPECTOS_TRANS_TRANS = {

# ── Urano – Neptuno ───────────────────────────────────────────────────────────

("Urano", "Neptuno", "="): (
    "Urano en conjunción con Neptuno mezcla necesidad de cambio con gran sensibilidad e intuición. "
    "Puede haber búsqueda de nuevas formas de vida, percepción o consciencia difíciles de encajar en estructuras tradicionales."
),

("Urano", "Neptuno", "□"): (
    "Urano en cuadratura a Neptuno genera tensión entre necesidad de cambio y dificultad para mantener claridad o estabilidad interna. "
    "A veces los cambios aparecen más rápido de lo que puedes integrar emocionalmente."
),

("Urano", "Neptuno", "☍"): (
    "Urano en oposición a Neptuno intensifica la tensión entre ruptura y disolución de referencias antiguas. "
    "Puede haber sensación de cambio constante sin suficiente suelo interno."
),

("Urano", "Neptuno", "△"): (
    "Urano en trígono a Neptuno facilita integrar intuición, cambio y apertura a nuevas formas de percepción. "
    "La sensibilidad y la innovación pueden colaborar entre sí."
),

("Urano", "Neptuno", "✶"): (
    "Urano en sextil a Neptuno facilita abrir nuevas perspectivas internas de manera gradual y consciente. "
    "Existe capacidad para transformar la visión de la vida sin ruptura constante."
),

# ── Urano – Plutón ────────────────────────────────────────────────────────────

("Urano", "Plutón", "="): (
    "Urano en conjunción con Plutón intensifica muchísimo la necesidad de transformación y ruptura con estructuras que ya no tienen vida. "
    "Los cambios importantes suelen vivirse con mucha intensidad."
),

("Urano", "Plutón", "□"): (
    "Urano en cuadratura a Plutón genera tensión entre necesidad de cambio y procesos profundos difíciles de controlar. "
    "A veces las transformaciones llegan de forma brusca o extrema."
),

("Urano", "Plutón", "☍"): (
    "Urano en oposición a Plutón intensifica la tensión entre ruptura y control. "
    "Puede haber cambios radicales que obligan a reorganizar profundamente determinadas áreas de vida."
),

("Urano", "Plutón", "△"): (
    "Urano en trígono a Plutón facilita integrar cambio profundo y capacidad de transformación. "
    "Existe facilidad para dejar atrás estructuras antiguas y abrir nuevas etapas."
),

("Urano", "Plutón", "✶"): (
    "Urano en sextil a Plutón facilita transformar aspectos importantes de la vida de manera más consciente y progresiva. "
    "Los cambios suelen sentirse intensos pero manejables."
),

# ── Neptuno – Plutón ──────────────────────────────────────────────────────────

("Neptuno", "Plutón", "="): (
    "Neptuno en conjunción con Plutón intensifica muchísimo la sensibilidad profunda y los procesos internos de transformación. "
    "Puede haber percepción intensa de lo emocional, lo simbólico o lo invisible."
),

("Neptuno", "Plutón", "□"): (
    "Neptuno en cuadratura a Plutón genera tensión entre necesidad de transformación y dificultad para mantener claridad emocional o interna. "
    "Algunos procesos profundos pueden sentirse difíciles de comprender racionalmente."
),

("Neptuno", "Plutón", "☍"): (
    "Neptuno en oposición a Plutón intensifica la tensión entre profundidad emocional y pérdida de referencias antiguas. "
    "Puede haber etapas de transformación muy intensas y difíciles de definir con claridad."
),

("Neptuno", "Plutón", "△"): (
    "Neptuno en trígono a Plutón facilita integrar sensibilidad profunda y transformación interna. "
    "Existe capacidad para atravesar cambios importantes con bastante consciencia emocional."
),

("Neptuno", "Plutón", "✶"): (
    "Neptuno en sextil a Plutón facilita abrir procesos profundos de transformación de manera gradual. "
    "La intuición y la sensibilidad pueden ayudarte a comprender cambios internos importantes."
),

}


# ─── ASPECTOS SENSIBLES ───────────────────────────────────────────────────────
# Quirón y Lilith con personales y transpersonales.
# Textos breves y directos.

ASPECTOS_SENSIBLES = {


# ── Quirón – Urano ────────────────────────────────────────────────────────────

("Quirón", "Urano", "="): (
    "Quirón en conjunción con Urano une herida y cambio. "
    "Las experiencias de ruptura, diferencia o inestabilidad pueden haberte obligado a cambiar antes de sentirte preparade.\n\n"

    "Puede haber sensación de no poder sostener demasiado tiempo estructuras, vínculos o etapas que dejan de sentirse auténticas, "
    "aunque romper con ellas también genere inseguridad.\n\n"

    "El aprendizaje está en permitir cambios sin convertir cada transformación en una ruptura total contigo."
),

("Quirón", "Urano", "□"): (
    "Quirón en cuadratura a Urano genera tensión entre necesidad de estabilidad y necesidad de cambio. "
    "Una parte de ti intenta protegerse de lo imprevisible, mientras otra necesita romper con lo que siente limitante.\n\n"

    "Los cambios bruscos pueden remover heridas antiguas relacionadas con rechazo, diferencia o sensación de no pertenecer.\n\n"

    "El aprendizaje pasa por construir formas de cambio más conscientes y menos destructivas para ti."
),

("Quirón", "Urano", "☍"): (
    "Quirón en oposición a Urano intensifica la tensión entre apertura al cambio y sensación de vulnerabilidad. "
    "A veces los movimientos de liberación llegan acompañados de inseguridad o desorientación.\n\n"

    "Puede haber etapas donde necesitas elegir entre mantener algo conocido o permitir una transformación importante.\n\n"

    "El aprendizaje está en descubrir que cambiar no siempre implica perderte."
),

("Quirón", "Urano", "△"): (
    "Quirón en trígono a Urano facilita transformar heridas a través de nuevas formas de vivir, comprender o expresarte. "
    "Los cambios importantes pueden ayudarte a crecer en lugar de desestructurarte.\n\n"

    "Existe capacidad para actualizarte, salir de patrones antiguos "
    "y convertir experiencias difíciles en comprensión útil para ti y para otras personas."
),

("Quirón", "Urano", "✶"): (
    "Quirón en sextil a Urano facilita abrir cambios que ayudan a sanar viejas limitaciones. "
    "Cuando te permites probar caminos distintos, aparecen nuevas posibilidades de comprensión y reparación.\n\n"

    "El aprendizaje está en no esperar a que la vida fuerce el cambio para permitirte moverte."
),


# ── Quirón – Neptuno ──────────────────────────────────────────────────────────

("Quirón", "Neptuno", "="): (
    "Quirón en conjunción con Neptuno une sensibilidad y herida. "
    "Puede haber mucha permeabilidad emocional y dificultad para separar lo que sientes tú de lo que absorbes del entorno.\n\n"

    "Las decepciones, pérdidas de claridad o experiencias de confusión pueden dejar una huella profunda "
    "si no encuentras formas de sostenerte con suficiente realidad y cuidado.\n\n"

    "El aprendizaje está en desarrollar sensibilidad sin perder completamente los límites."
),

("Quirón", "Neptuno", "□"): (
    "Quirón en cuadratura a Neptuno genera tensión entre necesidad de claridad y tendencia a la difuminación. "
    "Puede haber momentos donde cuesta distinguir intuición de idealización, "
    "o realidad de expectativa.\n\n"

    "La sensación de desorientación puede activar heridas relacionadas con decepción, abandono o pérdida de referencia.\n\n"

    "El aprendizaje pasa por construir más claridad interna sin cerrar completamente la sensibilidad."
),

("Quirón", "Neptuno", "☍"): (
    "Quirón en oposición a Neptuno intensifica la tensión entre sensibilidad y realidad concreta. "
    "A veces puedes sentir que algo dentro de ti busca entregarse o abrirse, "
    "mientras otra parte teme perderse en ello.\n\n"

    "Puede haber dificultad para sostener límites claros cuando hay implicación emocional profunda.\n\n"

    "El aprendizaje está en mantener conexión con lo sensible sin desaparecer dentro de ello."
),

("Quirón", "Neptuno", "△"): (
    "Quirón en trígono a Neptuno facilita transformar experiencias sensibles o dolorosas en comprensión profunda. "
    "Existe capacidad para acompañar procesos emocionales complejos sin perder completamente el centro.\n\n"

    "La intuición, la empatía y la sensibilidad pueden convertirse en herramientas de integración "
    "cuando están sostenidas con suficiente realidad."
),

("Quirón", "Neptuno", "✶"): (
    "Quirón en sextil a Neptuno facilita encontrar formas suaves y conscientes de reparar heridas emocionales. "
    "La sensibilidad puede abrir caminos de comprensión y profundidad "
    "sin necesidad de entrar siempre en confusión o desbordamiento.\n\n"

    "El aprendizaje está en dar estructura y realidad a lo que percibes y sientes."
),


# ── Quirón – Plutón ───────────────────────────────────────────────────────────

("Quirón", "Plutón", "="): (
    "Quirón en conjunción con Plutón une herida e intensidad profunda. "
    "Hay experiencias que no puedes vivir de forma superficial: "
    "lo que te afecta deja huella y te transforma profundamente.\n\n"

    "Puede haber contacto temprano con situaciones intensas, pérdidas, control, presión emocional "
    "o dinámicas que te obligaron a desarrollar mucha capacidad de resistencia.\n\n"

    "El aprendizaje está en transformar esa intensidad sin vivir permanentemente desde la tensión o la defensa."
),

("Quirón", "Plutón", "□"): (
    "Quirón en cuadratura a Plutón genera tensión entre necesidad de protegerte y procesos de transformación que no puedes evitar. "
    "A veces intentas mantener control sobre lo que sientes o sostienes, "
    "pero la vida acaba llevando la presión al punto donde algo necesita cambiar.\n\n"

    "Las heridas profundas pueden activarse especialmente en situaciones de intensidad emocional, pérdida, poder o vulnerabilidad.\n\n"

    "El aprendizaje pasa por permitir transformación sin sentir que necesitas destruirte para cambiar."
),

("Quirón", "Plutón", "☍"): (
    "Quirón en oposición a Plutón intensifica la tensión entre vulnerabilidad e intensidad. "
    "Puede haber miedo a perder control, a exponerte demasiado "
    "o a entrar en procesos emocionales que sientes difíciles de manejar.\n\n"

    "Las relaciones y experiencias importantes suelen remover capas muy profundas "
    "que no pueden mantenerse ocultas indefinidamente.\n\n"

    "El aprendizaje está en descubrir que profundidad no significa necesariamente peligro."
),

("Quirón", "Plutón", "△"): (
    "Quirón en trígono a Plutón facilita transformar experiencias difíciles en fortaleza y comprensión profunda. "
    "Existe capacidad para atravesar procesos intensos sin romperte completamente por dentro.\n\n"

    "Puedes desarrollar una comprensión muy real de la transformación humana "
    "y acompañar cambios profundos con más consciencia y estabilidad."
),

("Quirón", "Plutón", "✶"): (
    "Quirón en sextil a Plutón facilita trabajar heridas profundas de forma gradual y consciente. "
    "La intensidad puede convertirse en motor de transformación "
    "cuando no intentas evitar constantemente lo que necesitas mirar.\n\n"

    "El aprendizaje está en usar la profundidad para construir más verdad y coherencia en tu vida."
),

# ── Lilith – Urano ────────────────────────────────────────────────────────────

("Lilith", "Urano", "="): (
    "Lilith en conjunción con Urano une necesidad de libertad y ruptura de límites. "
    "Hay una parte de ti que rechaza de forma muy fuerte todo lo que siente artificial, impuesto o excesivamente rígido.\n\n"

    "Puede haber dificultad para sostener estructuras, vínculos o situaciones donde sientes que pierdes autenticidad o espacio propio.\n\n"

    "El aprendizaje está en encontrar formas de libertad que no te obliguen a romper constantemente con todo."
),

("Lilith", "Urano", "□"): (
    "Lilith en cuadratura a Urano genera tensión entre necesidad de estabilidad y necesidad de romper con lo establecido. "
    "A veces puedes sentir impulsos bruscos de cambio, distancia o liberación "
    "cuando algo empieza a sentirse limitante.\n\n"

    "La incomodidad frente a normas, expectativas o formas demasiado cerradas puede ser muy intensa.\n\n"

    "El aprendizaje pasa por construir cambios más conscientes y menos reactivos."
),

("Lilith", "Urano", "☍"): (
    "Lilith en oposición a Urano intensifica la tensión entre pertenecer y mantener libertad personal. "
    "Puede haber dificultad para sostener vínculos o estructuras sin sentir pérdida de autonomía.\n\n"

    "Los cambios importantes suelen aparecer cuando algo deja de sentirse auténtico o vivo.\n\n"

    "El aprendizaje está en descubrir que libertad y vínculo no siempre son incompatibles."
),

("Lilith", "Urano", "△"): (
    "Lilith en trígono a Urano facilita expresar autenticidad de forma natural y poco dependiente de aprobación externa. "
    "Existe capacidad para cambiar, renovarte y salir de patrones limitantes sin destruir necesariamente lo anterior.\n\n"

    "La diferencia personal puede convertirse en una fuente de creatividad y verdad."
),

("Lilith", "Urano", "✶"): (
    "Lilith en sextil a Urano facilita abrir espacios de libertad y autenticidad de forma consciente. "
    "Cuando te permites salir un poco de lo esperado, aparecen nuevas formas de vivir más coherentes contigo.\n\n"

    "El aprendizaje está en usar esa apertura para construir vida propia, no solo para reaccionar contra lo externo."
),


# ── Lilith – Neptuno ──────────────────────────────────────────────────────────

("Lilith", "Neptuno", "="): (
    "Lilith en conjunción con Neptuno une sensibilidad profunda y dificultad para encajar en formas rígidas o artificiales. "
    "Hay una parte de ti muy intuitiva, permeable y difícil de definir completamente.\n\n"

    "Puede haber tendencia a idealizar, fusionarte emocionalmente o perder claridad "
    "cuando algo te toca muy profundamente.\n\n"

    "El aprendizaje está en sostener sensibilidad y profundidad sin perder completamente los límites."
),

("Lilith", "Neptuno", "□"): (
    "Lilith en cuadratura a Neptuno genera tensión entre necesidad de claridad y tendencia a la confusión o idealización. "
    "A veces puedes sentir que algo dentro de ti rechaza las formas establecidas, "
    "pero sin tener todavía una referencia clara de hacia dónde ir.\n\n"

    "Puede haber etapas de desorientación emocional, expectativas irreales "
    "o dificultad para distinguir intuición de proyección."
),

("Lilith", "Neptuno", "☍"): (
    "Lilith en oposición a Neptuno intensifica la tensión entre realidad concreta y necesidad de conexión profunda con algo más amplio o más libre. "
    "Puede haber sensación de no encajar del todo en las formas habituales de relación, sensibilidad o vida.\n\n"

    "A veces resulta difícil sostener límites claros sin sentir pérdida de profundidad o autenticidad.\n\n"

    "El aprendizaje está en desarrollar sensibilidad sin desaparecer dentro de ella."
),

("Lilith", "Neptuno", "△"): (
    "Lilith en trígono a Neptuno facilita integrar sensibilidad, intuición y autenticidad de forma bastante natural. "
    "Existe capacidad para conectar con dimensiones profundas de la experiencia "
    "sin perder completamente la referencia de ti.\n\n"

    "La creatividad, la intuición y la percepción simbólica pueden convertirse en una fuente importante de verdad interior."
),

("Lilith", "Neptuno", "✶"): (
    "Lilith en sextil a Neptuno facilita abrir espacios de sensibilidad y profundidad de manera consciente. "
    "La intuición puede ayudarte a detectar lo que no encaja contigo "
    "antes de que la situación se vuelva demasiado desgastante.\n\n"

    "El aprendizaje está en dar forma concreta a lo que percibes y sientes."
),


# ── Lilith – Plutón ───────────────────────────────────────────────────────────

("Lilith", "Plutón", "="): (
    "Lilith en conjunción con Plutón une intensidad, profundidad y una necesidad muy fuerte de verdad. "
    "Hay experiencias que remueven capas profundas de ti "
    "y que no puedes sostener desde la superficialidad.\n\n"

    "Puede haber magnetismo, intensidad emocional "
    "o dificultad para permanecer en situaciones donde sientes control, falsedad o manipulación.\n\n"

    "El aprendizaje está en relacionarte con la intensidad sin vivir permanentemente en tensión o confrontación."
),

("Lilith", "Plutón", "□"): (
    "Lilith en cuadratura a Plutón genera tensión entre necesidad de autenticidad y dinámicas de intensidad o control. "
    "Las relaciones y experiencias importantes pueden activar luchas de poder, miedo a la vulnerabilidad "
    "o necesidad de proteger partes muy profundas de ti.\n\n"

    "La intensidad emocional puede acumularse durante mucho tiempo "
    "hasta que algo necesita cambiar de forma radical."
),

("Lilith", "Plutón", "☍"): (
    "Lilith en oposición a Plutón intensifica la tensión entre apertura y defensa profunda. "
    "Puede haber miedo a perder poder personal, a exponerte demasiado "
    "o a entrar en vínculos donde sientas que desapareces.\n\n"

    "Las experiencias importantes suelen remover capas muy profundas "
    "que no pueden mantenerse ocultas indefinidamente.\n\n"

    "El aprendizaje está en descubrir que profundidad no significa necesariamente destrucción."
),

("Lilith", "Plutón", "△"): (
    "Lilith en trígono a Plutón facilita integrar intensidad, autenticidad y transformación profunda. "
    "Existe capacidad para atravesar cambios importantes "
    "sin perder completamente el centro.\n\n"

    "La profundidad emocional puede convertirse en una fuente de fuerza, claridad y verdad interior."
),

("Lilith", "Plutón", "✶"): (
    "Lilith en sextil a Plutón facilita transformar partes profundas de ti de forma gradual y consciente. "
    "La intensidad puede ayudarte a reconocer lo que ya no es auténtico "
    "sin necesidad de destruir todo lo anterior.\n\n"

    "El aprendizaje está en usar la profundidad para construir una vida más coherente contigo."
),
}

# ─── CÁLCULO ASTROLÓGICO ──────────────────────────────────────────────────────

def geocodificar(ciudad):
    g = Nominatim(user_agent="ai_planetas_trans", timeout=10)
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

    for nombre in planetas:
        planetas[nombre]["casa"] = casa_de(planetas[nombre]["lon"])

    return {
        "planetas": planetas,
        "cuspides": list(cuspides),
        "asc": {"lon": asc_lon, "signo": signo_asc, "grado": grado_asc},
        "mc":  {"lon": mc_lon,  "signo": signo_mc,  "grado": grado_mc},
        "jd":  jd,
    }


def calcular_aspectos_trans(planetas):
    """Calcula aspectos relevantes para el módulo de transpersonales."""

    pares_personales = [
        ("Urano", "Sol"), ("Urano", "Luna"), ("Urano", "Mercurio"), ("Urano", "Venus"), ("Urano", "Marte"),
        ("Neptuno", "Sol"), ("Neptuno", "Luna"), ("Neptuno", "Mercurio"), ("Neptuno", "Venus"), ("Neptuno", "Marte"),
        ("Plutón", "Sol"), ("Plutón", "Luna"), ("Plutón", "Mercurio"), ("Plutón", "Venus"), ("Plutón", "Marte"),
    ]

    pares_sociales = [
        ("Urano", "Júpiter"), ("Urano", "Saturno"),
        ("Neptuno", "Júpiter"), ("Neptuno", "Saturno"),
        ("Plutón", "Júpiter"), ("Plutón", "Saturno"),
    ]

    pares_trans_trans = [
        ("Urano", "Neptuno"),
        ("Urano", "Plutón"),
        ("Neptuno", "Plutón"),
    ]

    pares_sensibles = [
        ("Quirón", "Neptuno"), ("Quirón", "Urano"), ("Quirón", "Plutón"),
        ("Lilith", "Neptuno"), ("Lilith", "Urano"), ("Lilith", "Plutón"),
    ]

    pares = pares_personales + pares_sociales + pares_trans_trans + pares_sensibles
    aspectos = []

    for p1_nom, p2_nom in pares:
        p1 = planetas.get(p1_nom)
        p2 = planetas.get(p2_nom)

        if not p1 or not p2:
            continue

        diff = abs(p1["lon"] - p2["lon"]) % 360
        if diff > 180:
            diff = 360 - diff

        for tipo, angulo, orbe_max, simbolo in ASPECTOS_DEF:

            orbe_real = orbe_max

            # Oposición ampliada a 10° si participa Sol o Luna
            if (
                simbolo == "☍"
                and (
                    p1_nom in ("Sol", "Luna")
                    or p2_nom in ("Sol", "Luna")
                )
            ):
                orbe_real = 10.0

            orbe_val = round(abs(diff - angulo), 2)
 
            if orbe_val <= orbe_real:

                aspectos.append({
                    "p1": p1_nom,
                    "p2": p2_nom,
                    "tipo": tipo,
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
    return (
        ASPECTOS_TRANS.get(clave1) or ASPECTOS_TRANS.get(clave2)
        or ASPECTOS_TRANS_SOCIALES.get(clave1) or ASPECTOS_TRANS_SOCIALES.get(clave2)
        or ASPECTOS_TRANS_TRANS.get(clave1) or ASPECTOS_TRANS_TRANS.get(clave2)
        or ASPECTOS_SENSIBLES.get(clave1) or ASPECTOS_SENSIBLES.get(clave2)
    )


def texto_marco_general(carta, aspectos):
    planetas = carta["planetas"]
    ur  = planetas.get("Urano",   {})
    nep = planetas.get("Neptuno", {})
    plu = planetas.get("Plutón",  {})

    ur_sig   = ur.get("signo", "")
    ur_casa  = ur.get("casa",  "")
    nep_sig  = nep.get("signo", "")
    nep_casa = nep.get("casa",  "")
    plu_sig  = plu.get("signo", "")
    plu_casa = plu.get("casa",  "")

    texto = (
        "Urano, Neptuno y Plutón no describen lo más cotidiano o visible de tu carta. "
        "Muestran procesos más profundos, menos controlables, que pueden modificar tu forma de vivir, sostenerte y atravesar determinadas etapas.\n\n"

        f"Urano en {ur_sig}, Casa {ur_casa}: muestra dónde aparecen cambios, interrupciones o necesidad de libertad. "
        "Cuando se activa, algo que antes funcionaba puede dejar de hacerlo igual.\n"

        f"Neptuno en {nep_sig}, Casa {nep_casa}: muestra dónde los límites se vuelven más sensibles, difusos o permeables. "
        "Cuando se activa, algo que parecía claro puede perder forma.\n"

        f"Plutón en {plu_sig}, Casa {plu_casa}: muestra dónde aparecen procesos intensos de transformación. "
        "Cuando se activa, algo que se sostenía de una manera ya no puede seguir igual."
    )

    asp_textos = []
    for p1 in ("Urano", "Neptuno", "Plutón"):
        for p2 in ("Sol", "Luna", "Mercurio", "Venus", "Marte"):
            asp = _get_asp(aspectos, p1, p2)
            if asp:
                asp_textos.append(
                    f"{p1}–{p2} en {asp['tipo'].lower()} (orbe {asp['orbe']}°)"
                )
    if asp_textos:
        texto += f"\n\nAspectos activos con planetas personales: {', '.join(asp_textos)}."

    return texto


def texto_urano(carta, aspectos):
    planetas = carta["planetas"]
    ur   = planetas.get("Urano", {})
    sig  = ur.get("signo", "")
    casa = ur.get("casa", 1)
    ret  = ur.get("retrogrado", False)

    t = URANO_SIGNO.get(sig, "")
    t += "\n\n" + URANO_CASA.get(casa, "")

    if ret:
        t += (
            "\n\nUrano está retrógrado. Los cambios tienden a sentirse primero por dentro. "
            "Puede pasar tiempo antes de que se vean fuera, pero internamente algo ya está moviéndose, "
            "reorganizándose o dejando de funcionar como antes."
        )

    for p2 in ("Sol", "Luna", "Mercurio", "Venus", "Marte"):
        asp = _get_asp(aspectos, "Urano", p2)
        t_asp = _texto_asp("Urano", p2, asp)
        if t_asp:
            t += f"\n\n{t_asp}"

    return t


def texto_neptuno(carta, aspectos):
    planetas = carta["planetas"]
    nep  = planetas.get("Neptuno", {})
    sig  = nep.get("signo", "")
    casa = nep.get("casa", 1)
    ret  = nep.get("retrogrado", False)

    t = NEPTUNO_SIGNO.get(sig, "")
    t += "\n\n" + NEPTUNO_CASA.get(casa, "")

    if ret:
        t += (
            "\n\nNeptuno está retrógrado. La sensibilidad, la confusión o la pérdida de claridad tienden a vivirse primero internamente. "
            "Puede costarte detectar desde fuera cuándo algo está perdiendo forma, porque el proceso empieza en capas más silenciosas."
            )

    for p2 in ("Sol", "Luna", "Mercurio", "Venus", "Marte"):
        asp = _get_asp(aspectos, "Neptuno", p2)
        t_asp = _texto_asp("Neptuno", p2, asp)
        if t_asp:
            t += f"\n\n{t_asp}"

    return t


def texto_pluton(carta, aspectos):
    planetas = carta["planetas"]
    plu  = planetas.get("Plutón", {})
    sig  = plu.get("signo", "")
    casa = plu.get("casa", 1)
    ret  = plu.get("retrogrado", False)

    t = PLUTON_SIGNO.get(sig, "")
    t += "\n\n" + PLUTON_CASA.get(casa, "")

    if ret:
        t += (
            "\n\nPlutón está retrógrado. La intensidad y la transformación tienden a dirigirse primero hacia dentro. "
            "Puede haber procesos profundos que no se ven claramente desde fuera hasta que ya han acumulado mucha fuerza."
        )

    for p2 in ("Sol", "Luna", "Mercurio", "Venus", "Marte"):
        asp = _get_asp(aspectos, "Plutón", p2)
        t_asp = _texto_asp("Plutón", p2, asp)
        if t_asp:
            t += f"\n\n{t_asp}"

    return t


def texto_integracion(carta, aspectos):
    planetas = carta["planetas"]
    ur  = planetas.get("Urano",   {})
    nep = planetas.get("Neptuno", {})
    plu = planetas.get("Plutón",  {})

    ur_sig  = ur.get("signo",  "")
    nep_sig = nep.get("signo", "")
    plu_sig = plu.get("signo", "")
    ur_casa  = ur.get("casa",  "")
    nep_casa = nep.get("casa", "")
    plu_casa = plu.get("casa", "")

    elem_ur  = ELEMENTO_SIGNO.get(ur_sig,  "")
    elem_nep = ELEMENTO_SIGNO.get(nep_sig, "")
    elem_plu = ELEMENTO_SIGNO.get(plu_sig, "")

    partes = []

    # Relación entre los tres en el sistema
    partes.append(
        f"Urano, Neptuno y Plutón actúan de formas distintas y no siempre coordinadas. "
        f"Urano en {ur_sig}, Casa {ur_casa}, muestra dónde aparecen cambios, interrupciones o necesidad de libertad. "
        f"Cuando se activa, algo que antes funcionaba puede dejar de hacerlo igual. "
        f"Neptuno en {nep_sig}, Casa {nep_casa}, muestra dónde los límites se vuelven más sensibles, difusos o difíciles de sostener. "
        f"Cuando se activa, algo que parecía claro puede perder forma. "
        f"Plutón en {plu_sig}, Casa {plu_casa}, muestra dónde aparecen procesos intensos de transformación. "
        f"Cuando se activa, algo que sostenías de una manera ya no puede seguir igual."
    )

    # Cómo se combinan en el sistema de este individuo (por elemento)
    AFECTA_INTERNO = {
        "Fuego":  "tiendes a desbordarte por exceso de impulso o dificultad para frenar a tiempo",
        "Tierra": "puedes mantener situaciones o estructuras mucho más tiempo del que realmente necesitas",
        "Aire":   "puedes dispersarte intentando pensar, comprender o sostener demasiadas cosas a la vez",
        "Agua":   "tiendes a absorber emocionalmente más de lo que puedes sostener con facilidad",
    }

    AFECTA_DIRECCION = {
        "Fuego":  "los cambios aparecen cuando cambia el impulso que te mueve",
        "Tierra": "los cambios aparecen cuando lo que sostenía estabilidad deja de sentirse sólido",
        "Aire":   "los cambios aparecen cuando cambia tu manera de pensar o comprender las cosas",
        "Agua":   "los cambios aparecen cuando cambia lo que sientes profundamente",
    }

    partes.append(
        f"Neptuno en {nep_sig} muestra una sensibilidad especial en ciertas áreas de tu vida: "
        f"{AFECTA_INTERNO.get(elem_nep, 'puedes perder claridad o límites internos con más facilidad de lo habitual')}. "
        f"Urano en {ur_sig} muestra cómo suelen producirse los cambios importantes: "
        f"{AFECTA_DIRECCION.get(elem_ur, 'los cambios aparecen cuando algo deja de poder sostenerse igual')}. "
        f"Plutón en {plu_sig} concentra la intensidad en procesos que no pueden quedarse igual indefinidamente: "
        f"determinadas experiencias terminan empujándote a transformar algo en profundidad."
    )

    # Dinámica de cascada bajo presión
    UR_ROMPE = {
        "Fuego":  "los impulsos cambian antes de que puedas completar lo que habías iniciado",
        "Tierra": "algo que parecía estable deja de sostenerse de forma inesperada",
        "Aire":   "tu manera de pensar o entender una situación cambia bruscamente",
        "Agua":   "cambian vínculos, emociones o sensaciones de pertenencia de forma repentina",
    }

    NEP_OCUPA = {
        "Fuego":  "la energía pierde dirección y cuesta saber hacia dónde moverte",
        "Tierra": "lo que parecía sólido deja de sentirse tan claro o seguro",
        "Aire":   "aparecen dudas, confusión o sensación de dispersión mental",
        "Agua":   "te cuesta distinguir entre lo que sientes tú y lo que absorbes del entorno",
    }

    PLU_CONCENTRA = {
        "Fuego":  "la intensidad se acumula alrededor de decisiones, impulsos o acciones importantes",
        "Tierra": "la presión se concentra en estructuras, recursos o seguridades que necesitan cambiar",
        "Aire":   "la intensidad se concentra en pensamientos, conversaciones o formas de comprender la vida",
        "Agua":   "la intensidad se concentra en emociones profundas y vínculos importantes",
    }

    partes.append(
        f"En determinados momentos, estas tres fuerzas pueden activarse de forma encadenada. "
        f"Urano en {ur_sig} suele aparecer primero: {UR_ROMPE.get(elem_ur, 'algo cambia de forma inesperada')}. "
        f"Después, Neptuno en {nep_sig} puede hacer que aparezca sensación de confusión, pérdida de claridad o dificultad para entender bien qué está pasando: "
        f"{NEP_OCUPA.get(elem_nep, 'algo deja de sentirse claro o definido')}. "
        f"Finalmente, Plutón en {plu_sig} concentra la intensidad en aquello que ya no puede seguir igual: "
        f"{PLU_CONCENTRA.get(elem_plu, 'la intensidad obliga a atravesar un proceso de transformación')}. "
        f"Por eso, determinadas etapas pueden sentirse especialmente intensas: no estás viviendo una sola cosa, sino varios procesos moviéndose al mismo tiempo."
    )

    return "\n\n".join(partes)

def texto_orientacion(carta, aspectos):
    planetas = carta["planetas"]
    ur  = planetas.get("Urano",   {})
    nep = planetas.get("Neptuno", {})
    plu = planetas.get("Plutón",  {})

    ur_sig   = ur.get("signo",  "")
    ur_casa  = ur.get("casa",   "")
    nep_sig  = nep.get("signo", "")
    nep_casa = nep.get("casa",  "")
    plu_sig  = plu.get("signo", "")
    plu_casa = plu.get("casa",  "")

    elem_ur  = ELEMENTO_SIGNO.get(ur_sig,  "")
    elem_nep = ELEMENTO_SIGNO.get(nep_sig, "")
    elem_plu = ELEMENTO_SIGNO.get(plu_sig, "")

    # Señales de activación por planeta
    UR_SENAL = {
        "Fuego":  "aparecen impulsos repentinos de cambio o necesidad de romper con algo rápidamente",
        "Tierra": "algo que parecía estable deja de sostenerse igual",
        "Aire":   "cambia bruscamente tu manera de pensar, comprender o comunicar algo",
        "Agua":   "aparecen cambios emocionales o relacionales difíciles de prever",
    }

    NEP_SENAL = {
        "Fuego":  "pierdes claridad sobre hacia dónde quieres dirigirte",
        "Tierra": "lo que parecía seguro o estable deja de sentirse tan sólido",
        "Aire":   "aparece dispersión, confusión o exceso de pensamientos difíciles de ordenar",
        "Agua":   "te cuesta distinguir entre lo que sientes tú y lo que absorbes del entorno",
    }

    PLU_SENAL = {
        "Fuego":  "aparece una intensidad difícil de frenar en decisiones o acciones importantes",
        "Tierra": "la presión se concentra en estructuras, trabajo, recursos o seguridades importantes",
        "Aire":   "determinados pensamientos o conversaciones adquieren mucha intensidad y profundidad",
        "Agua":   "emociones y vínculos importantes atraviesan procesos muy intensos de transformación",
    }

    reconocer_urano = (
        f"Urano suele activarse cuando: "
        f"{UR_SENAL.get(elem_ur, 'algo cambia de forma inesperada')}. "
        f"Esto suele sentirse especialmente en temas relacionados con la Casa {ur_casa}."
    )

    reconocer_neptuno = (
        f"Neptuno suele activarse cuando: "
        f"{NEP_SENAL.get(elem_nep, 'algo pierde claridad o definición')}. "
        f"Esto suele sentirse especialmente en temas relacionados con la Casa {nep_casa}."
    )

    reconocer_pluton = (
        f"Plutón suele activarse cuando: "
        f"{PLU_SENAL.get(elem_plu, 'aparece una intensidad difícil de ignorar')}. "
        f"Esto suele sentirse especialmente en temas relacionados con la Casa {plu_casa}."
    )

    # Qué ocurre si no se reconocen
    si_no = (
        "Cuando estos procesos no se reconocen, es fácil vivirlos únicamente como problemas externos o mala suerte. "
        "Sin embargo, muchas veces están mostrando que algo necesita cambiar, redefinirse o transformarse más profundamente.\n\n"

        "Intentar sostener exactamente igual algo que internamente ya está cambiando suele generar más desgaste, "
        "más confusión o más sensación de bloqueo."
    )

    # Patrón de acumulación si se ignoran
    si_ignoran = (
        f"Si estos procesos se ignoran durante mucho tiempo, suelen intensificarse. "
        f"Urano puede traer cambios cada vez más bruscos. "
        f"Neptuno puede aumentar la sensación de confusión, desgaste o pérdida de claridad. "
        f"Plutón puede concentrar tanta intensidad que determinadas situaciones ya no puedan seguir sosteniéndose igual.\n\n"

        f"Por eso, reconocer antes lo que está cambiando suele ayudar a atravesar estas etapas con más consciencia y menos ruptura."
    )

    return {
        "reconocer_urano": reconocer_urano,
        "reconocer_neptuno": reconocer_neptuno,
        "reconocer_pluton": reconocer_pluton,
        "si_no": si_no,
        "si_ignoran": si_ignoran,
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
    ur  = planetas.get("Urano",   {})
    nep = planetas.get("Neptuno", {})
    plu = planetas.get("Plutón",  {})
    sol  = planetas.get("Sol",    {})
    luna = planetas.get("Luna",   {})

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

    t_marco  = texto_marco_general(carta, aspectos)
    t_ur     = texto_urano(carta, aspectos)
    t_nep    = texto_neptuno(carta, aspectos)
    t_plu    = texto_pluton(carta, aspectos)
    t_integ  = texto_integracion(carta, aspectos)
    t_or     = texto_orientacion(carta, aspectos)

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

    ret_ur  = " (retrógrado)" if ur.get("retrogrado")  else ""
    ret_nep = " (retrógrado)" if nep.get("retrogrado") else ""
    ret_plu = " (retrógrado)" if plu.get("retrogrado") else ""

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
\\usepackage{{graphicx}}
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

\\titleformat{{\\section}}{{\\Large\\bfseries\\color{{azulai}}}}{{}}{{0em}}{{}}[{{\\color{{azulai}}\\titlerule[0.5pt]}}]
\\titlespacing*{{\\section}}{{0pt}}{{1.4em}}{{0.5em}}

\\titleformat{{\\subsection}}{{\\large\\bfseries\\color{{doradoai}}}}{{}}{{0em}}{{}}
\\titlespacing*{{\\subsection}}{{0pt}}{{1.0em}}{{0.35em}}

\\titleformat{{\\subsubsection}}{{\\normalsize\\bfseries\\color{{grisai}}}}{{}}{{0em}}{{}}
\\titlespacing*{{\\subsubsection}}{{0pt}}{{0.7em}}{{0.25em}}

\\pagestyle{{fancy}}\\fancyhf{{}}
\\rhead{{\\textcolor{{grisai}}{{\\small {nom_esc} — Arquitectura Interna}}}}
\\lhead{{\\textcolor{{grisai}}{{\\small Urano · Neptuno · Plutón}}}}
\\cfoot{{\\textcolor{{grisai}}{{\\small\\thepage}}}}
\\renewcommand{{\\headrulewidth}}{{0.3pt}}

\\hypersetup{{colorlinks=true,linkcolor=azulai,urlcolor=azulai}}
\\setstretch{{1.25}}
\\tolerance=1500
\\emergencystretch=4em

\\begin{{document}}

% ── Portada ──────────────────────────────────────────────────────────────────
\\begin{{titlepage}}
  \\centering
  \\vspace*{{1.5cm}}
  {{\\Huge\\bfseries\\color{{azulai}} Urano · Neptuno · Plutón}}\\\\[0.5cm]
  {{\\large\\color{{grisai}} Arquitectura Interna}}\\\\[0.3cm]
  {{\\small\\itshape\\color{{grisai}} Procesos profundos de cambio, sensibilidad y transformación}}\\\\[2cm]
  {{\\huge\\color{{doradoai}} {nom_esc}}}\\\\[1.5cm]
  {{\\Large {fecha_str} \\quad {hora_str}}}\\\\[0.3cm]
  {{\\Large {ciu_esc}}}\\\\[0.3cm]
  {{\\normalsize Lat: {lat:.4f}° \\quad Lon: {lon:.4f}° \\quad {utc_str}}}\\\\[0.3cm]
  {{\\normalsize Ascendente: {esc(asc['signo'])} {grado_a_dms(asc['grado'])} \\quad
    MC: {esc(mc['signo'])} {grado_a_dms(mc['grado'])}}}\\\\[2cm]
  \\begin{{tabular}}{{ll}}
    \\textbf{{Urano:}}   & {signo_casa(ur)}{ret_ur}  \\\\
    \\textbf{{Neptuno:}} & {signo_casa(nep)}{ret_nep} \\\\
    \\textbf{{Plutón:}}  & {signo_casa(plu)}{ret_plu} \\\\
  \\end{{tabular}}\\\\[2cm]
  \\vfill
  {{\\small Generado el {datetime.now().strftime("%d/%m/%Y")}}}
\\end{{titlepage}}

\\tableofcontents
\\newpage

% ── Datos de referencia ───────────────────────────────────────────────────────
\\section{{Datos de referencia}}

\\begin{{center}}
\\begin{{tabular}}{{llll}}
  \\toprule
  \\textbf{{Planeta}} & \\textbf{{Signo}} & \\textbf{{Casa}} & \\textbf{{Posición}} \\\\
  \\midrule
  Urano{ret_ur}    & {esc(ur.get('signo',''))}   & {ur.get('casa','')}   & {grado_a_dms(ur.get('grado',0))}  \\\\
  Neptuno{ret_nep} & {esc(nep.get('signo',''))}  & {nep.get('casa','')}  & {grado_a_dms(nep.get('grado',0))} \\\\
  Plutón{ret_plu}  & {esc(plu.get('signo',''))}  & {plu.get('casa','')}  & {grado_a_dms(plu.get('grado',0))} \\\\
  Sol              & {esc(sol.get('signo',''))}  & {sol.get('casa','')}  & {grado_a_dms(sol.get('grado',0))} \\\\
  Luna             & {esc(luna.get('signo',''))} & {luna.get('casa','')} & {grado_a_dms(luna.get('grado',0))} \\\\
  Ascendente       & {esc(asc['signo'])}          & ---                   & {grado_a_dms(asc['grado'])} \\\\
  Medio Cielo      & {esc(mc['signo'])}           & ---                   & {grado_a_dms(mc['grado'])} \\\\
  \\bottomrule
\\end{{tabular}}
\\end{{center}}

\\vspace{{0.5cm}}
\\textbf{{Aspectos relevantes:}}

{tabla_aspectos}

\\begin{{center}}
\\includegraphics[width=0.72\\textwidth]{{{os.path.basename(ruta_rueda)}}}
\\end{{center}}

\\Needspace{{3\\baselineskip}}


% ── Interpretación ────────────────────────────────────────────────────────────
\\section{{Interpretación — Arquitectura Interna}}

\\begin{{center}}
{{\\small\\itshape
No se trata de describir la personalidad. Se trata de mostrar qué procesos\\\\
de cambio, sensibilidad y transformación pueden activarse en tu vida.
}}
\\end{{center}}

\\vspace{{0.8cm}}
\\Needspace{{5\\baselineskip}}

% ── 1. Marco general ──────────────────────────────────────────────────────────
\\subsection{{1. Marco general}}

{parrafos(t_marco)}

\\vspace{{0.8cm}}
\\Needspace{{5\\baselineskip}}


% ── 2. Urano ──────────────────────────────────────────────────────────────────
\\subsection{{2. Urano — Ruptura y cambio de patrón}}

\\subsubsection*{{Urano en {esc(ur.get('signo',''))} — Casa {ur.get('casa','')}{ret_ur}}}

{parrafos(t_ur)}

\\vspace{{0.8cm}}
\\Needspace{{5\\baselineskip}}

% ── 3. Neptuno ────────────────────────────────────────────────────────────────
\\subsection{{3. Neptuno — Disolución y pérdida de forma}}

\\subsubsection*{{Neptuno en {esc(nep.get('signo',''))} — Casa {nep.get('casa','')}{ret_nep}}}

{parrafos(t_nep)}

\\vspace{{0.8cm}}
\\Needspace{{5\\baselineskip}}

% ── 4. Plutón ─────────────────────────────────────────────────────────────────
\\subsection{{4. Plutón — Intensidad y transformación profunda}}

\\subsubsection*{{Plutón en {esc(plu.get('signo',''))} — Casa {plu.get('casa','')}{ret_plu}}}

{parrafos(t_plu)}

\\vspace{{0.8cm}}
\\Needspace{{5\\baselineskip}}

% ── 5. Integración ────────────────────────────────────────────────────────────
\\subsection{{5. Integración — Las tres fuerzas en tu carta}}

{parrafos(t_integ)}

\\vspace{{0.8cm}}
\\Needspace{{5\\baselineskip}}

% ── 6. Orientación ────────────────────────────────────────────────────────────
\\subsection{{6. Orientación}}

\\subsubsection*{{Cuando Urano está activo}}
{parrafos(t_or['reconocer_urano'])}

\\subsubsection*{{Cuando Neptuno está activo}}
{parrafos(t_or['reconocer_neptuno'])}

\\subsubsection*{{Cuando Plutón está activo}}
{parrafos(t_or['reconocer_pluton'])}

\\subsubsection*{{Cuando no se reconocen}}
{parrafos(t_or['si_no'])}

\\vspace{{0.6cm}}
{parrafos(t_or['si_ignoran'])}

\\vspace{{1cm}}
\\begin{{center}}
{{\\small\\itshape\\color{{grisai}}
La astrología se usa aquí como lenguaje simbólico de observación, no como definición de la persona.\\
Este documento es una aproximación funcional, no un diagnóstico.
}}
\\end{{center}}

\\end{{document}}
"""

    return latex


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print("═" * 57)
    print("  URANO · NEPTUNO · PLUTÓN — Arquitectura Interna")
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
        print(f"  Coordenadas: {lat:.4f}°N, {lon:.4f}°E")
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
        ur     = carta["planetas"].get("Urano",   {})
        nep    = carta["planetas"].get("Neptuno", {})
        plu    = carta["planetas"].get("Plutón",  {})
        print(f"  ASC:     {asc['signo']} {grado_a_dms(asc['grado'])}")
        print(f"  Urano:   {ur.get('signo','') } {grado_a_dms(ur.get('grado',0))}  — Casa {ur.get('casa','')}")
        print(f"  Neptuno: {nep.get('signo','')} {grado_a_dms(nep.get('grado',0))} — Casa {nep.get('casa','')}")
        print(f"  Plutón:  {plu.get('signo','') } {grado_a_dms(plu.get('grado',0))} — Casa {plu.get('casa','')}")
    except Exception as e:
        print(f"Error en cálculo astrológico: {e}"); sys.exit(1)

    aspectos = calcular_aspectos_trans(carta["planetas"])
    print(f"  Aspectos calculados: {len(aspectos)}")

    nombre_f  = nombre.replace(" ", "_").replace("/", "-")
    ruta_base = os.path.join(BASE_DIR, nombre_f + "_Planetas_Transpersonales")
    ruta_tex  = ruta_base + ".tex"
    ruta_pdf  = ruta_base + ".pdf"
    ruta_rueda  = os.path.join(BASE_DIR, nombre_f + "_rueda.png")

    dibujar_rueda(carta, nombre, ruta_rueda)

    print("  Generando interpretación...")
    latex = generar_latex(carta, nombre, anio, mes, dia, hora, minuto,
                          ciudad, lat, lon, tz_name, ruta_rueda, aspectos)
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
