#!/usr/bin/env python3
"""
8. Plutón · Casa 8 · Casa 12 · Quirón · Lilith — Arquitectura Interna

Este programa observa algunas de las zonas más profundas,
sensibles e intensas de la carta.

Hay partes de la vida que no pueden sostenerse únicamente
desde la voluntad, la lógica o el control.

A veces aparecen procesos que remueven por dentro,
etapas en las que algo se rompe,
se vuelve demasiado intenso
o deja de poder vivirse de la misma manera.

Plutón muestra dónde puedes vivir experiencias de intensidad,
control, pérdida, obsesión o transformación profunda.

La Casa 8 habla de vínculos intensos,
exposición emocional,
miedo a perder,
necesidad de control
y procesos internos que suelen remover mucho más de lo que parece desde fuera.

La Casa 12 muestra lugares de retirada,
agotamiento,
hipersensibilidad,
confusión,
aislamiento
o dificultad para poner en palabras lo que ocurre dentro de ti.

Quirón señala heridas difíciles de tocar directamente,
zonas donde puedes sentirte especialmente sensible,
insuficiente o expuesto,
y donde muchas veces aprendes a protegerte antes incluso de darte cuenta.

Lilith muestra partes de ti que no encajan fácilmente
en lo esperado,
lo correcto
o lo controlable.

No habla de “oscuridad” en un sentido dramático,
ni de rasgos fijos de personalidad.

Habla de lugares internos que suelen activarse
cuando atraviesas crisis,
cambios profundos,
vínculos intensos
o etapas que te obligan a mirarte de otra manera.
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

    aspectos_rueda = calcular_aspectos_sombra(carta["planetas"])

    planetas_con_aspecto = set()
    for asp in aspectos_rueda:
        planetas_con_aspecto.add(asp["p1"])
        planetas_con_aspecto.add(asp["p2"])

    for asp in aspectos_rueda:
        if asp["orbe"] > 10.0:
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
        "Plutón", "Quirón", "Lilith",
        "Sol", "Luna", "Mercurio", "Venus", "Marte",
        "Júpiter", "Saturno", "Urano", "Neptuno"
    ]

    orden = [
        p for p in orden_base
        if p in ("Plutón", "Quirón", "Lilith") or p in planetas_con_aspecto
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

PUNTOS_SOMBRA = [
    "Plutón",
    "Quirón",
    "Lilith"
]

PLANETAS_PERSONALES = [
    "Sol",
    "Luna",
    "Mercurio",
    "Venus",
    "Marte"
]

PLANETAS_SOCIALES = [
    "Júpiter",
    "Saturno"
]

PLANETAS_TRANSPERSONALES = [
    "Urano",
    "Neptuno",
    "Plutón"
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


# ─── TEXTOS: PLUTÓN POR SIGNO ────────────────────────────────────────────────
# Dónde aparece la intensidad, el miedo a perder el control,
# la defensa profunda y la necesidad de transformación.

PLUTON_SIGNO = {

"Aries": (
    "Plutón en Aries muestra una intensidad profunda ligada a la voluntad, la acción y la necesidad de afirmarte. "
    "Puede haber una parte de ti que sienta que tiene que luchar para existir, decidir rápido o defender su lugar antes de ser desplazada.\n\n"

    "La sombra puede aparecer como impulsividad, dureza, rabia contenida o dificultad para ceder cuando algo toca tu autonomía. "
    "A veces puedes vivir la vulnerabilidad como una amenaza y responder desde el ataque, la huida o la autosuficiencia extrema.\n\n"

    "La transformación pasa por descubrir que no necesitas estar siempre en combate para tener fuerza. "
    "Tu poder crece cuando puedes actuar sin destruirte ni convertir cada límite en una guerra."
),

"Tauro": (
    "Plutón en Tauro muestra una intensidad profunda ligada a la seguridad, el cuerpo, el apego y la necesidad de sostén. "
    "Puede haber mucho miedo a perder lo que te da estabilidad, incluso cuando eso mismo ya no te permite respirar bien.\n\n"

    "La sombra puede aparecer como resistencia al cambio, posesividad, rigidez o necesidad de controlar lo material, el placer, el ritmo o los vínculos. "
    "A veces puedes aferrarte a algo porque soltarlo te enfrenta a una sensación muy antigua de vacío o desprotección.\n\n"

    "La transformación pasa por aprender a habitar la seguridad sin convertirla en prisión. "
    "Tu poder crece cuando el cuerpo deja de ser un lugar de defensa y empieza a ser un lugar donde puedes volver a ti."
),

"Geminis": (
    "Plutón en Géminis muestra una intensidad profunda ligada a la mente, la palabra, la interpretación y la necesidad de entender. "
    "Puede haber una tendencia a analizar mucho lo que ocurre, como si comprenderlo todo fuera una forma de mantenerte a salvo.\n\n"

    "La sombra puede aparecer como desconfianza mental, manipulación a través de la palabra, pensamientos obsesivos o dificultad para descansar de la propia cabeza. "
    "A veces puedes usar la explicación para no sentir directamente lo que duele.\n\n"

    "La transformación pasa por dejar que la palabra no solo controle, sino también revele. "
    "Tu poder crece cuando puedes decir la verdad sin utilizar la lucidez como una armadura."
),

"Cáncer": (
    "Plutón en Cáncer muestra una intensidad profunda ligada a la pertenencia, la familia, la memoria emocional y la necesidad de protección. "
    "Puede haber zonas muy sensibles en torno al abandono, la dependencia, el cuidado o el miedo a no tener un lugar seguro al que volver.\n\n"

    "La sombra puede aparecer como apego, cierre emocional, necesidad de proteger demasiado o dificultad para soltar historias antiguas. "
    "A veces puedes confundir amor con supervivencia, o cuidado con control.\n\n"

    "La transformación pasa por mirar de frente qué heridas siguen organizando tu manera de vincularte. "
    "Tu poder crece cuando puedes cuidar sin retener, recordar sin quedarte atrapade y pertenecer sin perderte."
),

"Leo": (
    "Plutón en Leo muestra una intensidad profunda ligada a la identidad, la expresión, el deseo de ser viste y el miedo a no importar. "
    "Puede haber una relación muy potente con el reconocimiento, la creatividad o la necesidad de ocupar un lugar propio.\n\n"

    "La sombra puede aparecer como orgullo defensivo, dramatización, miedo a la humillación o necesidad de controlar cómo te perciben. "
    "A veces puedes esconder tu fragilidad detrás de fuerza, brillo o autosuficiencia.\n\n"

    "La transformación pasa por dejar de vivir la exposición como una prueba de valor personal. "
    "Tu poder crece cuando puedes mostrarte sin tener que demostrar tanto."
),

"Virgo": (
    "Plutón en Virgo muestra una intensidad profunda ligada al control, la mejora, el cuerpo, el trabajo y la necesidad de hacerlo bien. "
    "Puede haber una exigencia interna fuerte, como si cualquier error pudiera abrir una grieta difícil de sostener.\n\n"

    "La sombra puede aparecer como perfeccionismo, culpa, autoobservación dura o dificultad para descansar si algo no está resuelto. "
    "A veces puedes intentar ordenar por fuera una angustia que en realidad pide ser escuchada por dentro.\n\n"

    "La transformación pasa por dejar de utilizar la corrección como forma de protegerte del miedo. "
    "Tu poder crece cuando puedes habitar lo imperfecto sin sentir que pierdes valor."
),

"Libra": (
    "Plutón en Libra muestra una intensidad profunda ligada al vínculo, el deseo, la dependencia, la comparación y el miedo al conflicto. "
    "Las relaciones pueden tocar zonas muy hondas de ti, especialmente cuando aparece la posibilidad de pérdida, rechazo o desequilibrio.\n\n"

    "La sombra puede aparecer como complacencia, manipulación sutil, dependencia afectiva o necesidad de controlar la armonía para no sentir amenaza. "
    "A veces puedes ceder demasiado y luego resentirte por dentro.\n\n"

    "La transformación pasa por mirar qué parte de ti negocia su verdad para no perder vínculo. "
    "Tu poder crece cuando puedes amar, elegir y relacionarte sin abandonar tu centro."
),

"Escorpio": (
    "Plutón en Escorpio intensifica los temas propios de Plutón: deseo, control, pérdida, intimidad, miedo, poder y transformación. "
    "Puede haber una vida interna muy profunda, con emociones que rara vez son superficiales o fáciles de atravesar.\n\n"

    "La sombra puede aparecer como obsesión, desconfianza, necesidad de controlar, dificultad para soltar o tendencia a vivirlo todo con una intensidad extrema. "
    "A veces puedes detectar la herida ajena con mucha claridad, pero proteger ferozmente la tuya.\n\n"

    "La transformación pasa por dejar de confundir intensidad con verdad absoluta. "
    "Tu poder crece cuando puedes entrar en lo profundo sin quedarte atrapade en la herida."
),

"Sagitario": (
    "Plutón en Sagitario muestra una intensidad profunda ligada a la verdad, las creencias, el sentido y la necesidad de encontrar una dirección. "
    "Puede haber una búsqueda fuerte de respuestas, como si vivir sin significado resultara especialmente difícil.\n\n"

    "La sombra puede aparecer como rigidez ideológica, necesidad de tener razón, rechazo a la duda o huida hacia grandes explicaciones para no tocar una herida más concreta. "
    "A veces puedes usar la visión amplia para alejarte de lo que duele en lo inmediato.\n\n"

    "La transformación pasa por permitir que tus creencias también mueran, cambien o se vuelvan más humildes. "
    "Tu poder crece cuando la verdad deja de ser una defensa y se convierte en una forma honesta de mirar."
),

"Capricornio": (
    "Plutón en Capricornio muestra una intensidad profunda ligada al control, la responsabilidad, la autoridad y la necesidad de sostenerte con firmeza. "
    "Puede haber miedo al derrumbe, al fracaso o a perder la posición que te permite sentir que todo está bajo control.\n\n"

    "La sombra puede aparecer como dureza, autoexigencia, frialdad defensiva o dificultad para pedir ayuda. "
    "A veces puedes cargar demasiado porque detenerte te enfrenta a una vulnerabilidad que no quieres mostrar.\n\n"

    "La transformación pasa por revisar qué precio pagas por mantenerte fuerte todo el tiempo. "
    "Tu poder crece cuando puedes sostener sin endurecerte y asumir responsabilidad sin desaparecer dentro de ella."
),

"Acuario": (
    "Plutón en Acuario muestra una intensidad profunda ligada a la diferencia, la libertad, la distancia emocional y la necesidad de no quedar atrapade. "
    "Puede haber una parte de ti que necesite observar desde fuera para no sentirse invadida o absorbida por lo que ocurre.\n\n"

    "La sombra puede aparecer como desconexión, frialdad, aislamiento, rebeldía defensiva o dificultad para dejar que alguien se acerque demasiado. "
    "A veces puedes protegerte convirtiendo la intensidad emocional en análisis, distancia o independencia extrema.\n\n"

    "La transformación pasa por descubrir que la libertad no tiene por qué implicar desconexión. "
    "Tu poder crece cuando puedes conservar tu singularidad sin vivir el vínculo como una amenaza."
),

"Piscis": (
    "Plutón en Piscis muestra una intensidad profunda ligada a la sensibilidad, la entrega, la disolución y los límites emocionales. "
    "Puede haber una percepción muy fina de lo invisible, de lo no dicho o de lo que otras personas cargan sin expresarlo claramente.\n\n"

    "La sombra puede aparecer como confusión, evasión, sacrificio, idealización o dificultad para distinguir qué es tuyo y qué pertenece a otras personas. "
    "A veces puedes desaparecer en lo que sientes, en lo que imaginas o en lo que intentas salvar.\n\n"

    "La transformación pasa por aprender a no perderte en la sensibilidad. "
    "Tu poder crece cuando puedes abrirte sin diluirte y amar sin convertir el dolor ajeno en tu propia identidad."
),

}

# ─── TEXTOS: PLUTÓN POR CASA ────────────────────────────────────────────────
# Dónde aparecen procesos intensos de transformación,
# control, vulnerabilidad y cambio profundo.

PLUTON_CASA = {

1: (
    "Plutón en casa 1 suele dar una presencia intensa, incluso cuando no intentas llamar la atención. "
    "Muchas veces las personas perciben algo fuerte en ti antes de que hayas dicho demasiado.\n\n"

    "Puede haber necesidad de controlar cómo te muestras, dificultad para sentirte vulnerable o sensación de tener que sostenerte con mucha fuerza frente al mundo. "
    "A veces atraviesas cambios profundos de identidad que hacen que ciertas versiones de ti ya no puedan mantenerse.\n\n"

    "La transformación pasa por dejar de vivir la exposición como amenaza constante. "
    "Tu presencia se vuelve más sólida cuando no necesitas protegerla todo el tiempo."
),

2: (
    "Plutón en casa 2 muestra una relación intensa con la seguridad, el valor personal, el dinero o la necesidad de sostenerte por ti misme. "
    "Puede haber miedo profundo a depender, perder estabilidad o no tener suficiente.\n\n"

    "A veces intentas controlar demasiado lo material porque debajo hay una sensación difícil de inseguridad o vulnerabilidad. "
    "También puede haber etapas de reconstrucción fuerte en la economía o en la forma en que valoras tu propia capacidad.\n\n"

    "La transformación pasa por revisar cuánto de tu valor está apoyado únicamente en lo que produces, sostienes o controlas."
),

3: (
    "Plutón en casa 3 muestra una mente intensa, observadora y difícil de engañar. "
    "Sueles percibir lo que otras personas callan, contradicen o intentan suavizar.\n\n"

    "Puede haber tendencia a pensar demasiado, analizar compulsivamente o utilizar la palabra como forma de defensa. "
    "A veces decir lo que realmente piensas puede sentirse peligroso, especialmente si aprendiste pronto que ciertas verdades generaban conflicto.\n\n"

    "La transformación pasa por permitir que la comunicación deje de ser solo control o vigilancia. "
    "Tu voz gana fuerza cuando no necesita protegerse constantemente."
),

4: (
    "Plutón en casa 4 muestra procesos profundos ligados a la infancia, la familia, el hogar y la sensación de pertenencia. "
    "Puede haber memorias emocionales intensas o ambientes familiares donde ciertas cosas no podían hablarse claramente.\n\n"

    "A veces existe necesidad de controlar mucho el espacio personal porque el cuerpo no termina de relajarse del todo. "
    "También puede aparecer miedo a depender emocionalmente o dificultad para sentir verdadera seguridad interna.\n\n"

    "La transformación pasa por revisar qué parte de tu vida sigue organizada alrededor de heridas antiguas. "
    "Construir hogar deja de ser protegerte de todo y empieza a ser poder descansar."
),

5: (
    "Plutón en casa 5 muestra intensidad en la expresión personal, el deseo, la creatividad y los vínculos afectivos. "
    "Lo que sientes rara vez es superficial, especialmente cuando algo toca el amor, el reconocimiento o la necesidad de ser viste.\n\n"

    "Puede haber miedo al rechazo, necesidad de controlar cómo te expones o dificultad para disfrutar sin sentir riesgo emocional. "
    "A veces las relaciones afectivas remueven zonas muy profundas de autoestima o poder personal.\n\n"

    "La transformación pasa por permitirte crear y amar sin convertir cada experiencia emocional en una prueba de valor."
),

6: (
    "Plutón en casa 6 muestra intensidad en la relación con el trabajo, el cuerpo, las rutinas y la necesidad de control cotidiano. "
    "Puede haber mucha exigencia interna y dificultad para descansar realmente.\n\n"

    "A veces intentas sostener demasiado durante demasiado tiempo hasta llegar al agotamiento. "
    "También puede aparecer hipervigilancia corporal, obsesión con hacerlo bien o sensación de que si aflojas algo importante podría derrumbarse.\n\n"

    "La transformación pasa por dejar de utilizar la productividad como única forma de sentir seguridad o valor personal."
),

7: (
    "Plutón en casa 7 muestra relaciones intensas, transformadoras y difíciles de vivir desde la superficie. "
    "Los vínculos importantes suelen remover partes muy profundas de ti.\n\n"

    "Puede haber miedo al abandono, necesidad de control, dependencia emocional o atracción hacia relaciones donde aparecen dinámicas de poder difíciles de sostener. "
    "A veces el vínculo se convierte en el lugar donde aparecen heridas que normalmente permanecían ocultas.\n\n"

    "La transformación pasa por aprender a relacionarte sin perderte ni intentar controlar completamente al otro."
),

8: (
    "Plutón en casa 8 intensifica profundamente los temas de vulnerabilidad, intimidad, pérdida, deseo, control y transformación emocional. "
    "Sueles vivir ciertos procesos internos con mucha profundidad, incluso cuando desde fuera no se percibe.\n\n"

    "Puede haber miedo a la traición, dificultad para confiar del todo o necesidad de mantener cierto control emocional para no sentirte expueste. "
    "A veces lo que más deseas también es lo que más miedo te da perder.\n\n"

    "La transformación pasa por permitir cercanía sin vivir cada vínculo como un riesgo de destrucción. "
    "Tu profundidad deja de ser sufrimiento cuando no necesitas defenderla constantemente."
),

9: (
    "Plutón en casa 9 muestra una búsqueda intensa de sentido, verdad y comprensión profunda de la vida. "
    "Las creencias no suelen ser algo superficial para ti: pueden convertirse en estructuras muy importantes de orientación.\n\n"

    "Puede haber necesidad de encontrar respuestas absolutas, dificultad para tolerar la incertidumbre o etapas donde una visión completa de la vida se derrumba. "
    "A veces una crisis interna obliga a revisar todo aquello que parecía darte dirección.\n\n"

    "La transformación pasa por permitir que tus ideas evolucionen sin sentir que pierdes completamente el suelo bajo los pies."
),

10: (
    "Plutón en casa 10 muestra intensidad en la relación con la imagen pública, el reconocimiento, la autoridad y la necesidad de construir algo sólido. "
    "Puede haber mucha presión interna respecto a lo que debes lograr o sostener.\n\n"

    "A veces el trabajo, la posición o la responsabilidad se convierten en lugares donde intentas demostrar valor, control o fortaleza. "
    "También puede haber miedo profundo al fracaso o a perder aquello que te daba identidad social.\n\n"

    "La transformación pasa por revisar cuánto de tu vida está organizado alrededor de la necesidad de sostener una imagen fuerte."
),

11: (
    "Plutón en casa 11 muestra intensidad en la relación con grupos, amistades, pertenencia y proyectos colectivos. "
    "Puede costarte sentirte realmente dentro sin mantener cierta distancia protectora.\n\n"

    "A veces aparecen experiencias intensas en amistades o grupos donde surgen dinámicas de exclusión, poder o decepción. "
    "También puede haber necesidad de diferenciarte mucho para no sentir que el entorno te absorbe.\n\n"

    "La transformación pasa por descubrir que pertenecer no tiene por qué implicar perder individualidad."
),

12: (
    "Plutón en casa 12 muestra una vida interna muy profunda, sensible y difícil de explicar completamente con palabras. "
    "Hay emociones, miedos o recuerdos que muchas veces permanecen ocultos incluso para ti.\n\n"

    "Puede haber tendencia a contener muchísimo, aislarte emocionalmente o vivir procesos internos muy intensos en silencio. "
    "A veces lo reprimido termina apareciendo de golpe, especialmente cuando llevas demasiado tiempo intentando sostenerlo desde el control.\n\n"

    "La transformación pasa por dejar de luchar constantemente contra lo que ocurre dentro. "
    "Tu profundidad deja de sentirse amenazante cuando puedes mirarla sin necesidad de esconderla o negarla."
),

}


# ─── TEXTOS: QUIRÓN POR SIGNO ───────────────────────────────────────────────
# Dónde aparece una sensibilidad profunda,
# sensación de insuficiencia o necesidad de protegerte.

QUIRON_SIGNO = {

"Aries": (
    "Quirón en Aries suele mostrar una herida ligada a la afirmación personal, la iniciativa y el derecho a ocupar espacio. "
    "Puede costarte actuar con espontaneidad cuando sientes que podrías equivocarte, molestar o exponerte demasiado.\n\n"

    "A veces aparece miedo al conflicto, inseguridad respecto a tu fuerza o sensación de tener que demostrar constantemente que puedes por ti misme. "
    "También puede existir una relación ambivalente con la rabia: contenerla demasiado o expresarla de golpe cuando ya no puedes sostenerla.\n\n"

    "El aprendizaje pasa por permitirte existir sin tener que justificar continuamente tu presencia, tu deseo o tu manera de actuar."
),

"Tauro": (
    "Quirón en Tauro suele mostrar sensibilidad en torno al valor personal, la seguridad y la sensación de merecer estabilidad o bienestar. "
    "Puede haber miedo profundo a no tener suficiente o perder aquello que te sostiene.\n\n"

    "A veces intentas construir seguridad desde el control, la acumulación o la autosuficiencia extrema. "
    "También puede costarte relajarte realmente en el cuerpo si dentro hay sensación constante de amenaza o carencia.\n\n"

    "El aprendizaje pasa por descubrir que tu valor no depende únicamente de lo que produces, sostienes o consigues conservar."
),

"Géminis": (
    "Quirón en Géminis suele mostrar sensibilidad en torno a la palabra, la comunicación y la sensación de que te comprendan. "
    "Puede haber miedo a expresarte mal, decir algo incorrecto o sentir que tu forma de pensar no encaja del todo.\n\n"

    "A veces observas demasiado cómo hablas, explicas o respondes. "
    "También puede aparecer dificultad para confiar en tu propia percepción, especialmente si creciste sintiendo que lo que pensabas era minimizado o cuestionado.\n\n"

    "El aprendizaje pasa por permitirte comunicar desde un lugar más vivo y menos defensivo. "
    "Tu voz gana fuerza cuando deja de intentar protegerse constantemente."
),

"Cáncer": (
    "Quirón en Cáncer suele mostrar heridas ligadas al cuidado, la pertenencia y la seguridad emocional. "
    "Puede existir una sensibilidad muy profunda al rechazo, al abandono o a la sensación de no haber recibido el sostén emocional que necesitabas.\n\n"

    "A veces cuidas mucho a otras personas porque te resulta difícil reconocer cuánto necesitas tú también ser cuidada. "
    "También puede aparecer miedo a depender emocionalmente o dificultad para relajarte del todo en el vínculo.\n\n"

    "El aprendizaje pasa por permitirte necesitar sin sentir vergüenza por ello."
),

"Leo": (
    "Quirón en Leo suele mostrar sensibilidad en torno a la identidad, la expresión personal y la necesidad de ser viste tal como eres. "
    "Puede haber miedo a exponerte, a hacer el ridículo o a no sentirte suficientemente importante.\n\n"

    "A veces escondes partes muy auténticas de ti para evitar juicio, rechazo o humillación. "
    "También puede aparecer necesidad de reconocimiento mezclada con miedo profundo a depender de él.\n\n"

    "El aprendizaje pasa por dejar de medir tu valor según cuánto destaque tu presencia o cuánto recibas de fuera."
),

"Virgo": (
    "Quirón en Virgo suele mostrar una herida ligada a la exigencia, la utilidad y la sensación de no hacerlo nunca suficientemente bien. "
    "Puede haber mucha autoobservación y dificultad para descansar sin sentir culpa.\n\n"

    "A veces intentas corregirte constantemente para evitar error, crítica o sensación de insuficiencia. "
    "También puede aparecer hipersensibilidad respecto al cuerpo, la salud o el rendimiento cotidiano.\n\n"

    "El aprendizaje pasa por permitirte ser humana sin convertir cada imperfección en una prueba de fracaso."
),

"Libra": (
    "Quirón en Libra suele mostrar sensibilidad profunda en las relaciones y en la sensación de equilibrio con otras personas. "
    "Puede haber miedo al rechazo, dificultad para sostener conflicto o tendencia a adaptarte demasiado para conservar vínculo.\n\n"

    "A veces intentas mantener armonía incluso cuando algo dentro de ti ya no está bien. "
    "También puede costarte saber qué deseas realmente si eso implica decepcionar o incomodar a alguien.\n\n"

    "El aprendizaje pasa por descubrir que vincularte no debería exigirte desaparecer dentro de la relación."
),

"Escorpio": (
    "Quirón en Escorpio suele mostrar heridas profundas ligadas a la confianza, la vulnerabilidad y el miedo a ser dañade emocionalmente. "
    "Puede existir mucha sensibilidad alrededor de la traición, el control o la exposición emocional.\n\n"

    "A veces proteges tanto ciertas partes de ti que terminas aislándote incluso cuando deseas cercanía. "
    "También puede aparecer necesidad de controlar lo que sientes para no experimentar pérdida, dependencia o dolor.\n\n"

    "El aprendizaje pasa por descubrir que abrirte no significa necesariamente perder poder o quedar indefense."
),

"Sagitario": (
    "Quirón en Sagitario suele mostrar sensibilidad en torno al sentido, las creencias y la necesidad de encontrar dirección. "
    "Puede haber miedo profundo a equivocarte de camino o sensación de no terminar de encontrar un lugar interno desde el que orientarte.\n\n"

    "A veces buscas respuestas enormes para aliviar una inseguridad más íntima y difícil de nombrar. "
    "También puede aparecer frustración cuando la realidad no encaja con la visión que imaginabas.\n\n"

    "El aprendizaje pasa por permitirte no tener todas las respuestas sin sentir que pierdes completamente el rumbo."
),

"Capricornio": (
    "Quirón en Capricornio suele mostrar heridas ligadas a la responsabilidad, la exigencia y la necesidad de demostrar fortaleza. "
    "Puede haber sensación de tener que sostener demasiado desde muy pronto.\n\n"

    "A veces te cuesta pedir ayuda porque mostrar necesidad puede sentirse peligroso o vergonzoso. "
    "También puede aparecer autoexigencia muy fuerte, especialmente cuando sientes que tu valor depende de lo que logras o sostienes.\n\n"

    "El aprendizaje pasa por permitirte existir más allá de la utilidad, el rendimiento o el control."
),

"Acuario": (
    "Quirón en Acuario suele mostrar sensibilidad en torno a la diferencia, la pertenencia y la sensación de encajar. "
    "Puede haber una parte de ti que se sienta distinta incluso estando acompañada.\n\n"

    "A veces mantienes distancia emocional para protegerte del rechazo o de la sensación de que no te comprendan del todo. "
    "También puede aparecer dificultad para sentir verdadera pertenencia sin perder individualidad.\n\n"

    "El aprendizaje pasa por descubrir que no necesitas dejar de ser quien eres para poder formar parte de algo."
),

"Piscis": (
    "Quirón en Piscis suele mostrar una sensibilidad muy profunda hacia el dolor, el sufrimiento o lo que otras personas sienten alrededor. "
    "Puede costarte distinguir claramente dónde terminas tú y dónde empieza lo ajeno.\n\n"

    "A veces absorbes demasiado, te desbordas emocionalmente o intentas salvar a otras personas para no mirar tu propia herida. "
    "También puede haber tendencia a escapar, desconectarte o desaparecer cuando algo resulta demasiado intenso.\n\n"

    "El aprendizaje pasa por desarrollar compasión sin sacrificarte ni perderte dentro de lo que sientes."
),

}

# ─── TEXTOS: QUIRÓN POR CASA ────────────────────────────────────────────────
# Dónde aparece sensibilidad profunda,
# inseguridad, vergüenza o necesidad de protección.

QUIRON_CASA = {

1: (
    "Quirón en casa 1 suele mostrar sensibilidad respecto a la identidad, la presencia y la forma en que te muestras al mundo. "
    "Puede haber sensación de exponerte demasiado simplemente por existir o por ocupar espacio.\n\n"

    "A veces dudas de tu manera de actuar, de decidir o incluso de cómo impactas en otras personas. "
    "También puede aparecer tendencia a esconder partes de ti para evitar juicio, rechazo o conflicto.\n\n"

    "El aprendizaje pasa por permitirte ser visible sin sentir que tienes que justificar continuamente quién eres."
),

2: (
    "Quirón en casa 2 suele mostrar heridas ligadas al valor personal, la seguridad y la sensación de merecer estabilidad o bienestar. "
    "Puede haber miedo profundo a no tener suficiente o a no ser suficientemente válida.\n\n"

    "A veces intentas compensar esa inseguridad produciendo mucho, sosteniéndolo todo o evitando depender de otras personas. "
    "También puede costarte disfrutar plenamente si dentro hay sensación constante de amenaza o carencia.\n\n"

    "El aprendizaje pasa por descubrir que tu valor no depende únicamente de lo que haces, consigues o sostienes."
),

3: (
    "Quirón en casa 3 suele mostrar sensibilidad respecto a la palabra, la comunicación y la forma de expresar lo que piensas. "
    "Puede haber miedo a decir algo incorrecto, a que no te entiendan o a sentir que tu voz no tiene suficiente peso.\n\n"

    "A veces observas demasiado cómo hablas, explicas o respondes. "
    "También puede aparecer inseguridad intelectual o dificultad para confiar plenamente en tu propia percepción.\n\n"

    "El aprendizaje pasa por permitir que tu voz exista sin exigirle perfección constante."
),

4: (
    "Quirón en casa 4 suele mostrar heridas profundas relacionadas con la pertenencia, el hogar y la seguridad emocional. "
    "Puede haber sensación de no haber tenido un lugar donde relajarte del todo o sentirte completamente sostenide.\n\n"

    "A veces proteges mucho tu intimidad porque ciertas vulnerabilidades siguen muy vivas por dentro. "
    "También puede existir dificultad para pedir cuidado o permitir verdadera cercanía emocional.\n\n"

    "El aprendizaje pasa por construir espacios donde no tengas que estar siempre en defensa."
),

5: (
    "Quirón en casa 5 suele mostrar sensibilidad respecto a la expresión personal, la creatividad y la necesidad de ser viste. "
    "Puede haber miedo a exponerte demasiado o sensación de que mostrarte auténticamente implica riesgo emocional.\n\n"

    "A veces escondes partes muy vivas de ti para evitar juicio, rechazo o vergüenza. "
    "También puede aparecer dificultad para disfrutar plenamente si sientes que te están observando o evaluando.\n\n"

    "El aprendizaje pasa por permitirte crear, jugar y expresarte sin convertir cada exposición en una prueba de valor personal."
),

6: (
    "Quirón en casa 6 suele mostrar heridas relacionadas con la exigencia, el cuerpo, el trabajo y la necesidad de hacerlo bien. "
    "Puede haber sensación de no llegar nunca al nivel que te exiges internamente.\n\n"

    "A veces intentas corregirte constantemente para evitar error, crítica o sensación de insuficiencia. "
    "También puede aparecer mucha autoobservación corporal o dificultad para descansar sin culpa.\n\n"

    "El aprendizaje pasa por dejar de convertir la perfección en condición para sentirte válida."
),

7: (
    "Quirón en casa 7 suele mostrar sensibilidad profunda en los vínculos y en la forma en que te relacionas con otras personas. "
    "Puede haber miedo al rechazo, a no ser elegide o a perderte dentro de la relación.\n\n"

    "A veces te adaptas demasiado para conservar vínculo o evitas mostrar ciertas necesidades por temor a generar distancia. "
    "También puede doler especialmente sentir desequilibrio, indiferencia o desconexión emocional.\n\n"

    "El aprendizaje pasa por descubrir que el vínculo no debería exigirte abandonar tu verdad."
),

8: (
    "Quirón en casa 8 suele mostrar heridas profundas ligadas a la vulnerabilidad, la intimidad y la confianza emocional. "
    "Puede costarte abrir ciertas partes de ti porque la exposición emocional se siente especialmente delicada.\n\n"

    "A veces deseas mucha cercanía pero al mismo tiempo aparece miedo intenso a depender, perder control o que te dañen. "
    "También puede existir tendencia a proteger lo más sensible de forma muy silenciosa.\n\n"

    "El aprendizaje pasa por descubrir que abrirte emocionalmente no implica necesariamente quedar indefense."
),

9: (
    "Quirón en casa 9 suele mostrar sensibilidad respecto al sentido, las creencias y la necesidad de orientación interna. "
    "Puede haber miedo a equivocarte de camino o sensación de no terminar de encontrar una dirección clara.\n\n"

    "A veces buscas respuestas enormes para aliviar una inseguridad más íntima y difícil de nombrar. "
    "También puede aparecer frustración cuando una visión importante de la vida deja de sostenerse.\n\n"

    "El aprendizaje pasa por permitirte avanzar incluso cuando no tienes todas las certezas."
),

10: (
    "Quirón en casa 10 suele mostrar heridas ligadas al reconocimiento, la autoridad y la sensación de valor frente al mundo. "
    "Puede haber mucha sensibilidad respecto al éxito, el fracaso o la percepción externa.\n\n"

    "A veces sientes que necesitas demostrar constantemente capacidad, fortaleza o competencia para sentirte segura. "
    "También puede costarte mucho mostrar vulnerabilidad en espacios donde sientes que te observan.\n\n"

    "El aprendizaje pasa por descubrir que tu valor no depende únicamente de lo que logras o sostienes hacia fuera."
),

11: (
    "Quirón en casa 11 suele mostrar sensibilidad respecto a la pertenencia, la amistad y la sensación de encajar dentro de grupos o entornos colectivos. "
    "Puede existir una sensación persistente de ser diferente incluso estando en compañía.\n\n"

    "A veces mantienes cierta distancia emocional para protegerte de la exclusión o del miedo a que no te comprendan completamente. "
    "También puede doler especialmente sentir rechazo dentro de espacios donde esperabas afinidad o conexión.\n\n"

    "El aprendizaje pasa por permitirte pertenecer sin renunciar a tu singularidad."
),

12: (
    "Quirón en casa 12 suele mostrar heridas muy profundas y difíciles de explicar completamente con palabras. "
    "Puede haber una sensibilidad interna enorme que muchas veces intentas contener en silencio.\n\n"

    "A veces cargas emociones durante mucho tiempo sin compartirlas o te aíslas cuando algo resulta demasiado intenso. "
    "También puede aparecer sensación de desconexión, agotamiento emocional o dificultad para entender exactamente qué te ocurre.\n\n"

    "El aprendizaje pasa por dejar de esconder continuamente lo que duele. "
    "Tu sensibilidad deja de sentirse tan amenazante cuando puedes mirarla con más honestidad y menos vergüenza."
),

}

# ─── TEXTOS: LILITH POR SIGNO ───────────────────────────────────────────────
# Dónde aparece una parte de ti difícil de domesticar,
# controlar o encajar completamente en lo esperado.

LILITH_SIGNO = {

"Aries": (
    "Lilith en Aries muestra una parte de ti muy instintiva, directa y difícil de contener cuando siente amenaza o limitación. "
    "Puede haber rechazo profundo a sentir que te controlan, frenan o ser dependiente.\n\n"

    "A veces reaccionas antes de pensar demasiado porque algo dentro necesita proteger su autonomía rápidamente. "
    "También puede aparecer rabia acumulada cuando llevas mucho tiempo cediendo, adaptándote o conteniéndote.\n\n"

    "El aprendizaje pasa por relacionarte con tu fuerza sin convertir cada límite o desacuerdo en una lucha constante."
),

"Tauro": (
    "Lilith en Tauro muestra una relación intensa con el deseo, el cuerpo, el placer y la necesidad de estabilidad. "
    "Puede haber una parte de ti que rechaza profundamente sentirse obligada a vivir desconectada de lo que necesita realmente.\n\n"

    "A veces aparece resistencia fuerte al cambio, apego a ciertos vínculos o necesidad de controlar aquello que te da seguridad. "
    "También puede existir tensión entre el deseo de estabilidad y el miedo a quedar atrapade dentro de ella.\n\n"

    "El aprendizaje pasa por permitirte disfrutar, sostener y desear sin convertir la seguridad en prisión."
),

"Géminis": (
    "Lilith en Géminis muestra una mente difícil de domesticar completamente. "
    "Puede haber una parte de ti que cuestiona, observa y necesita pensar por sí misma incluso cuando eso incomoda al entorno.\n\n"

    "A veces utilizas la ironía, la distancia mental o el cambio constante de perspectiva como forma de protegerte. "
    "También puede aparecer rechazo profundo hacia discursos rígidos, explicaciones cerradas o formas demasiado limitantes de comunicación.\n\n"

    "El aprendizaje pasa por permitir que tu pensamiento sea libre sin utilizar la distancia intelectual para desconectarte emocionalmente."
),

"Cáncer": (
    "Lilith en Cáncer muestra una sensibilidad muy intensa respecto al cuidado, la intimidad y la necesidad de protección emocional. "
    "Puede haber una parte de ti que desea mucha cercanía y al mismo tiempo teme profundamente depender.\n\n"

    "A veces proteges tanto lo que sientes que terminas aislándote emocionalmente. "
    "También puede aparecer rabia silenciosa cuando percibes invasión, falta de cuidado o exigencias emocionales difíciles de sostener.\n\n"

    "El aprendizaje pasa por permitir cercanía sin sentir que necesitas desaparecer o defenderte constantemente."
),

"Leo": (
    "Lilith en Leo muestra una parte de ti que necesita expresarse de forma auténtica y rechaza profundamente sentir que te anulan o invisibilizan. "
    "Puede haber mucha intensidad respecto al reconocimiento, la creatividad y el derecho a ocupar espacio.\n\n"

    "A veces alternas entre mostrarte muchísimo y esconderte completamente por miedo a la exposición o al juicio. "
    "También puede aparecer necesidad de controlar cómo te perciben para proteger una vulnerabilidad muy profunda.\n\n"

    "El aprendizaje pasa por permitirte brillar sin vivir la mirada ajena como una amenaza constante."
),

"Virgo": (
    "Lilith en Virgo muestra una parte de ti muy sensible al desorden, la incoherencia o la sensación de pérdida de control. "
    "Puede haber rechazo profundo a equivocarte, depender demasiado o sentirte vulnerable frente al caos.\n\n"

    "A veces intentas sostenerlo todo desde la exigencia, el perfeccionismo o el control minucioso. "
    "También puede aparecer irritación fuerte cuando algo rompe el orden interno que necesitas para sentir estabilidad.\n\n"

    "El aprendizaje pasa por permitirte ser humana sin convertir la imperfección en amenaza."
),

"Libra": (
    "Lilith en Libra muestra una tensión intensa entre la necesidad de vínculo y el rechazo profundo a perderte dentro de la relación. "
    "Puede haber mucha sensibilidad respecto al equilibrio, el deseo y las dinámicas de poder afectivo.\n\n"

    "A veces buscas cercanía y luego necesitas distancia para recuperar espacio propio. "
    "También puede aparecer incomodidad muy fuerte frente a relaciones donde sientes dependencia, desigualdad o presión emocional.\n\n"

    "El aprendizaje pasa por relacionarte sin desaparecer dentro de la necesidad de agradar o mantener armonía."
),

"Escorpio": (
    "Lilith en Escorpio intensifica profundamente los temas de deseo, control, vulnerabilidad y poder emocional. "
    "Puede haber una percepción muy fina de lo oculto, lo ambiguo o lo que otras personas intentan contener.\n\n"

    "A veces reaccionas intensamente cuando sientes traición, manipulación o pérdida de control emocional. "
    "También puede existir miedo profundo a mostrar ciertas partes de ti por temor a quedar expueste o que te dañen.\n\n"

    "El aprendizaje pasa por descubrir que profundidad no significa vivir permanentemente en defensa o intensidad extrema."
),

"Sagitario": (
    "Lilith en Sagitario muestra una parte de ti que necesita amplitud, libertad mental y posibilidad de explorar sin sentirse encerrade. "
    "Puede haber rechazo muy fuerte hacia normas, creencias o estructuras que percibes como limitantes.\n\n"

    "A veces reaccionas alejándote rápidamente cuando algo empieza a sentirse demasiado cerrado o restrictivo. "
    "También puede aparecer dificultad para permanecer mucho tiempo en situaciones que ya no te permiten crecer.\n\n"

    "El aprendizaje pasa por sostener libertad sin necesidad de huir constantemente de todo lo que incomoda."
),

"Capricornio": (
    "Lilith en Capricornio muestra una relación intensa con el control, la responsabilidad y la necesidad de sostenerte con firmeza. "
    "Puede haber rechazo profundo a depender de otras personas o a mostrar vulnerabilidad en espacios donde sientes exigencia.\n\n"

    "A veces te endureces demasiado para protegerte del miedo al fracaso, a la debilidad o a perder estabilidad. "
    "También puede aparecer tensión constante entre el deseo de control y el agotamiento que produce mantenerlo todo bajo vigilancia.\n\n"

    "El aprendizaje pasa por descubrir que fortaleza no significa vivir en una contención permanente."
),

"Acuario": (
    "Lilith en Acuario muestra una parte de ti difícil de encajar completamente dentro de expectativas colectivas o normas sociales rígidas. "
    "Puede haber necesidad muy fuerte de conservar independencia mental y espacio propio.\n\n"

    "A veces mantienes distancia emocional para no sentir que otras personas te atrapadan o te absorben. "
    "También puede aparecer rebeldía intensa cuando percibes control, presión grupal o pérdida de libertad.\n\n"

    "El aprendizaje pasa por permitir vínculo y cercanía sin sentir que necesitas renunciar a tu singularidad."
),

"Piscis": (
    "Lilith en Piscis muestra una sensibilidad muy intensa hacia lo emocional, lo invisible y lo difícil de nombrar claramente. "
    "Puede haber una parte de ti que rechaza profundamente los límites rígidos o las formas demasiado frías de vivir.\n\n"

    "A veces absorbes demasiado del entorno o desapareces emocionalmente cuando algo resulta demasiado intenso. "
    "También puede aparecer dificultad para distinguir entre intuición, miedo, deseo o proyección emocional.\n\n"

    "El aprendizaje pasa por desarrollar límites más conscientes sin perder sensibilidad ni profundidad."
),

}

# ─── TEXTOS: LILITH POR CASA ────────────────────────────────────────────────
# Dónde aparece una parte de ti difícil de controlar,
# domesticar o reducir a lo esperado.

LILITH_CASA = {

1: (
    "Lilith en casa 1 suele dar una presencia intensa, difícil de neutralizar o pasar desapercibida del todo. "
    "Puede haber una parte de ti que rechaza profundamente sentir que te controlan, corregin o reeducan.\n\n"

    "A veces reaccionas con mucha fuerza cuando percibes invasión, juicio o limitación. "
    "También puede aparecer tensión entre el deseo de mostrarte auténticamente y el miedo a cómo puedan responder otras personas.\n\n"

    "El aprendizaje pasa por permitirte existir con fuerza sin vivir constantemente en defensa."
),

2: (
    "Lilith en casa 2 muestra una relación intensa con el valor personal, la seguridad y el derecho a sostener tus propias necesidades. "
    "Puede haber rechazo profundo a depender económicamente o a sentir que otras personas controlan tu estabilidad.\n\n"

    "A veces aparece apego fuerte a ciertas seguridades o dificultad para soltar aquello que te hace sentir protegide. "
    "También puede existir tensión entre el deseo de estabilidad y la necesidad de conservar libertad personal.\n\n"

    "El aprendizaje pasa por construir seguridad sin convertirla en una forma de encierro."
),

3: (
    "Lilith en casa 3 muestra una mente difícil de domesticar completamente. "
    "Puede haber una parte de ti que cuestiona mucho, observa lo que otras personas no dicen y rechaza discursos demasiado cerrados.\n\n"

    "A veces utilizas la ironía, la distancia mental o la provocación como forma de protegerte. "
    "También puede aparecer incomodidad intensa cuando sientes que no puedes expresar lo que realmente piensas.\n\n"

    "El aprendizaje pasa por permitir que tu voz sea libre sin necesitar convertir cada conversación en una defensa constante."
),

4: (
    "Lilith en casa 4 muestra una sensibilidad muy intensa respecto a la intimidad, el hogar y la necesidad de protección emocional. "
    "Puede haber partes de tu vida emocional que proteges ferozmente y que rara vez muestras del todo.\n\n"

    "A veces reaccionas con mucha intensidad cuando sientes invasión emocional, falta de espacio o presión afectiva. "
    "También puede existir ambivalencia entre necesitar cercanía y querer desaparecer cuando alguien se acerca demasiado.\n\n"

    "El aprendizaje pasa por permitir intimidad sin sentir que necesitas defender constantemente tu espacio interno."
),

5: (
    "Lilith en casa 5 muestra una parte de ti muy intensa en la expresión personal, el deseo y la creatividad. "
    "Puede haber necesidad profunda de mostrarte auténticamente y rechazo fuerte hacia cualquier forma de anulación o control.\n\n"

    "A veces alternas entre exponerte muchísimo y retirarte por completo cuando aparece miedo al juicio o a la vulnerabilidad. "
    "También puede existir tensión entre el deseo de reconocimiento y la incomodidad de depender de él.\n\n"

    "El aprendizaje pasa por permitirte disfrutar y expresarte sin convertir cada mirada externa en amenaza."
),

6: (
    "Lilith en casa 6 muestra una relación intensa con el trabajo, el cuerpo, las rutinas y la necesidad de control cotidiano. "
    "Puede haber irritación fuerte frente a exigencias constantes, normas rígidas o sensación de estar atrapade en obligaciones interminables.\n\n"

    "A veces intentas sostener demasiado hasta que el cuerpo o el cansancio terminan reaccionando. "
    "También puede aparecer tensión entre la necesidad de orden y el rechazo profundo a sentir completamente controlade por él.\n\n"

    "El aprendizaje pasa por encontrar formas más humanas de sostener la vida cotidiana."
),

7: (
    "Lilith en casa 7 muestra intensidad en los vínculos y sensibilidad muy fuerte respecto a las dinámicas de dependencia, control o pérdida de libertad. "
    "Puede haber una parte de ti que desea mucha cercanía y al mismo tiempo teme profundamente quedar atrapade dentro de la relación.\n\n"

    "A veces necesitas tomar distancia cuando el vínculo se vuelve demasiado invasivo o emocionalmente exigente. "
    "También puede aparecer atracción hacia relaciones intensas donde se activan dinámicas de poder difíciles de sostener.\n\n"

    "El aprendizaje pasa por permitir vínculo sin sentir que necesitas desaparecer o defenderte constantemente."
),

8: (
    "Lilith en casa 8 intensifica profundamente los temas de deseo, vulnerabilidad, intimidad y control emocional. "
    "Puede haber una percepción muy fina de lo oculto, lo ambiguo o lo que otras personas intentan contener.\n\n"

    "A veces proteges ciertas partes de ti con muchísima fuerza porque mostrar vulnerabilidad puede sentirse peligroso. "
    "También puede existir atracción hacia experiencias intensas mezclada con miedo profundo a perder control o quedar expueste.\n\n"

    "El aprendizaje pasa por descubrir que profundidad no significa vivir permanentemente en defensa."
),

9: (
    "Lilith en casa 9 muestra una parte de ti que necesita libertad mental y espacio para explorar sin sentirse encerrade dentro de una única visión. "
    "Puede haber rechazo fuerte hacia normas rígidas, dogmas o formas demasiado cerradas de entender la vida.\n\n"

    "A veces reaccionas alejándote rápidamente cuando algo empieza a sentirse limitante o asfixiante. "
    "También puede aparecer necesidad constante de ampliar horizontes para no sentirte atrapade.\n\n"

    "El aprendizaje pasa por sostener libertad sin necesidad de huir continuamente de todo lo que incomoda."
),

10: (
    "Lilith en casa 10 muestra intensidad respecto al reconocimiento, la autoridad y la imagen que proyectas hacia fuera. "
    "Puede haber una parte de ti que rechaza profundamente sentir que te controlan, evaluan o reeducan expectativas externas.\n\n"

    "A veces sostienes una imagen muy fuerte mientras ocultas zonas mucho más vulnerables o cansadas. "
    "También puede aparecer tensión entre el deseo de construir algo importante y el rechazo a las estructuras demasiado rígidas.\n\n"

    "El aprendizaje pasa por permitirte existir públicamente sin convertir la fortaleza en una obligación permanente."
),

11: (
    "Lilith en casa 11 muestra una relación intensa con la diferencia, la pertenencia y los espacios colectivos. "
    "Puede haber una parte de ti que necesita sentirse libre incluso dentro de grupos o amistades.\n\n"

    "A veces mantienes distancia emocional porque temes perder individualidad o que el entorno te absorba. "
    "También puede aparecer incomodidad fuerte frente a dinámicas grupales rígidas o expectativas colectivas demasiado cerradas.\n\n"

    "El aprendizaje pasa por descubrir que pertenecer no implica dejar de ser quien eres."
),

12: (
    "Lilith en casa 12 muestra una vida interna muy intensa, sensible y difícil de mostrar completamente hacia fuera. "
    "Puede haber emociones, deseos o impulsos que has aprendido a esconder incluso de ti misme.\n\n"

    "A veces contienes muchísimo hasta que algo termina emergiendo de golpe. "
    "También puede aparecer sensación de aislamiento interno, agotamiento emocional o dificultad para entender ciertas reacciones profundas.\n\n"

    "El aprendizaje pasa por dejar de tratar ciertas partes de ti como si fueran algo que necesita permanecer oculto para siempre."
),

}


# ─── TEXTOS: CASA 8 POR SIGNO ───────────────────────────────────────────────
# Cómo se viven la vulnerabilidad, la intimidad,
# la confianza, el control y los procesos de transformación.

CASA8_SIGNO = {

"Aries": (
    "La casa 8 en Aries suele vivir la vulnerabilidad de forma intensa e impulsiva. "
    "Puede costarte permanecer mucho tiempo en situaciones emocionalmente ambiguas o donde sientes pérdida de control.\n\n"

    "A veces reaccionas rápidamente para protegerte cuando algo toca miedo, dependencia o exposición emocional. "
    "También puede aparecer tensión entre el deseo de intimidad y la necesidad de mantener autonomía.\n\n"

    "El aprendizaje pasa por permitir cercanía sin sentir que tienes que defender constantemente tu espacio personal."
),

"Tauro": (
    "La casa 8 en Tauro suele vivir los procesos emocionales profundos de manera lenta pero muy intensa. "
    "Puede haber mucho apego a lo que da seguridad, especialmente en vínculos importantes.\n\n"

    "A veces cuesta soltar relaciones, dinámicas o formas de sostén emocional incluso cuando ya generan sufrimiento. "
    "También puede aparecer miedo fuerte a la pérdida, al cambio o a la sensación de inestabilidad.\n\n"

    "El aprendizaje pasa por descubrir que abrirte al cambio no implica perder completamente el suelo bajo los pies."
),

"Géminis": (
    "La casa 8 en Géminis suele intentar comprender emocionalmente lo que ocurre antes de sentirlo del todo. "
    "Puede haber necesidad de analizar mucho los vínculos, las emociones o las dinámicas de intimidad.\n\n"

    "A veces utilizas la mente para tomar distancia de experiencias demasiado intensas. "
    "También puede aparecer dificultad para sostener silencio emocional o incomodidad frente a emociones difíciles de explicar racionalmente.\n\n"

    "El aprendizaje pasa por permitir que ciertas experiencias se vivan sin necesidad de entenderlas inmediatamente."
),

"Cáncer": (
    "La casa 8 en Cáncer suele vivir la intimidad y la vulnerabilidad de forma muy profunda. "
    "Los vínculos importantes pueden remover memorias emocionales antiguas y necesidades de protección difíciles de ignorar.\n\n"

    "A veces aparece mucho miedo al abandono, a la pérdida emocional o a no sentir suficiente cuidado dentro de la relación. "
    "También puede costarte distinguir entre cercanía emocional y dependencia.\n\n"

    "El aprendizaje pasa por permitir intimidad sin convertir el vínculo en un lugar donde necesitas protegerte constantemente."
),

"Leo": (
    "La casa 8 en Leo suele vivir la vulnerabilidad ligada al orgullo, la identidad y la necesidad de sentirte importante para la otra persona. "
    "Puede doler especialmente no sentir reconocimiento emocional o percibir indiferencia.\n\n"

    "A veces intentas sostener una imagen fuerte incluso cuando algo dentro está profundamente removido. "
    "También puede aparecer necesidad de controlar cómo te perciben cuando te sientes emocionalmente expueste.\n\n"

    "El aprendizaje pasa por permitirte mostrar fragilidad sin sentir que pierdes valor o dignidad."
),

"Virgo": (
    "La casa 8 en Virgo suele vivir los procesos emocionales profundos con mucha observación y necesidad de control. "
    "Puede haber dificultad para relajarte completamente en experiencias donde no puedes prever lo que ocurrirá.\n\n"

    "A veces analizas demasiado lo que sientes o intentas ordenar emocionalmente algo que en realidad necesita ser atravesado. "
    "También puede aparecer hipervigilancia respecto a la vulnerabilidad propia o ajena.\n\n"

    "El aprendizaje pasa por descubrir que no todo lo importante puede resolverse únicamente desde el control o la comprensión mental."
),

"Libra": (
    "La casa 8 en Libra suele vivir mucha intensidad en los vínculos y en las dinámicas de intimidad emocional. "
    "Puede haber gran sensibilidad respecto al equilibrio, la reciprocidad y el miedo a perder conexión.\n\n"

    "A veces intentas mantener armonía incluso cuando algo dentro ya se siente incómodo o desequilibrado. "
    "También puede aparecer dificultad para expresar ciertas necesidades por temor a romper el vínculo.\n\n"

    "El aprendizaje pasa por permitir relaciones profundas sin abandonar tu verdad para conservar cercanía."
),

"Escorpio": (
    "La casa 8 en Escorpio intensifica profundamente los temas de intimidad, deseo, vulnerabilidad y transformación emocional. "
    "Las experiencias importantes suelen vivirse con mucha profundidad y rara vez desde la superficie.\n\n"

    "Puede haber miedo fuerte a la traición, necesidad de control emocional o dificultad para abrir ciertas partes de ti. "
    "También puede existir tendencia a vivir los vínculos desde intensidad extrema, incluso cuando eso resulta agotador.\n\n"

    "El aprendizaje pasa por descubrir que profundidad no significa permanecer permanentemente en tensión o defensa."
),

"Sagitario": (
    "La casa 8 en Sagitario suele necesitar sentido y amplitud incluso en procesos emocionales intensos. "
    "Puede costarte permanecer mucho tiempo en dinámicas emocionales cerradas, pesadas o sin horizonte.\n\n"

    "A veces buscas explicaciones amplias o filosóficas para aliviar emociones difíciles de sostener directamente. "
    "También puede aparecer necesidad de distancia cuando la intensidad emocional empieza a sentirse demasiado absorbente.\n\n"

    "El aprendizaje pasa por permitir profundidad emocional sin sentir que pierdes libertad interna."
),

"Capricornio": (
    "La casa 8 en Capricornio suele vivir la vulnerabilidad con mucha contención y necesidad de control. "
    "Puede resultar difícil mostrar fragilidad o depender emocionalmente de otras personas.\n\n"

    "A veces sostienes muchísimo por miedo a perder estabilidad, control o posición dentro del vínculo. "
    "También puede aparecer dureza emocional defensiva cuando algo toca inseguridades profundas.\n\n"

    "El aprendizaje pasa por descubrir que abrirte emocionalmente no significa perder fortaleza."
),

"Acuario": (
    "La casa 8 en Acuario suele vivir tensión entre la necesidad de intimidad y el miedo a sentirse atrapade emocionalmente. "
    "Puede haber mucha necesidad de espacio incluso dentro de vínculos profundos.\n\n"

    "A veces tomas distancia cuando la intensidad emocional empieza a sentirse invasiva o demasiado demandante. "
    "También puede aparecer tendencia a racionalizar emociones muy profundas para no sentir que éstas te absorben.\n\n"

    "El aprendizaje pasa por permitir cercanía sin sentir que necesitas desaparecer para conservar libertad."
),

"Piscis": (
    "La casa 8 en Piscis suele vivir la vulnerabilidad de forma muy sensible y permeable. "
    "Puede costarte distinguir claramente qué sientes tú y qué pertenece emocionalmente a otras personas.\n\n"

    "A veces te fusionas demasiado con el dolor, el deseo o las necesidades ajenas. "
    "También puede aparecer tendencia a idealizar vínculos intensos o perder claridad emocional cuando algo te afecta profundamente.\n\n"

    "El aprendizaje pasa por desarrollar límites más conscientes sin cerrar completamente tu sensibilidad."
),

}


# ─── TEXTOS: CASA 12 POR SIGNO ───────────────────────────────────────────────
# Cómo se viven el retiro, la sensibilidad,
# el agotamiento emocional y lo difícil de poner en palabras.

CASA12_SIGNO = {

"Aries": (
    "La casa 12 en Aries suele contener mucha energía interna difícil de expresar directamente. "
    "Puede haber impulsos, rabia o necesidad de afirmarte que durante mucho tiempo aprendiste a contener.\n\n"

    "A veces sigues funcionando hacia fuera mientras por dentro existe agotamiento acumulado o tensión constante. "
    "También puede aparecer irritación difícil de identificar claramente hasta que ya resulta demasiado intensa.\n\n"

    "El aprendizaje pasa por reconocer antes lo que necesitas, en lugar de esperar siempre al límite para darte cuenta."
),

"Tauro": (
    "La casa 12 en Tauro suele necesitar mucho descanso, silencio y estabilidad para poder relajarse realmente. "
    "El cuerpo puede absorber más tensión de la que parece desde fuera.\n\n"

    "A veces te aferras a rutinas, espacios o seguridades porque el cambio interno resulta más desestabilizador de lo que muestras. "
    "También puede costarte identificar necesidades emocionales profundas hasta que el agotamiento aparece físicamente.\n\n"

    "El aprendizaje pasa por desarrollar seguridad interna sin depender únicamente de lo externo para sentir calma."
),

"Géminis": (
    "La casa 12 en Géminis suele mostrar una mente muy activa incluso en momentos de descanso. "
    "Puede haber dificultad para desconectar completamente del pensamiento, la observación o la necesidad de entender.\n\n"

    "A veces piensas tanto lo que sientes que terminas alejándote de la experiencia emocional directa. "
    "También puede aparecer cansancio mental acumulado o sensación de ruido interno constante.\n\n"

    "El aprendizaje pasa por permitir silencio mental sin sentir que necesitas resolverlo todo inmediatamente."
),

"Cáncer": (
    "La casa 12 en Cáncer suele vivir la sensibilidad emocional de forma muy profunda y silenciosa. "
    "Puede haber emociones antiguas que continúan activándose incluso cuando aparentemente ya quedaron atrás.\n\n"

    "A veces absorbes demasiado del entorno o cargas emocionalmente situaciones que otras personas ni siquiera perciben. "
    "También puede aparecer necesidad muy fuerte de refugio emocional cuando algo resulta demasiado intenso.\n\n"

    "El aprendizaje pasa por cuidar tu sensibilidad sin convertir el aislamiento en única forma de protección."
),

"Leo": (
    "La casa 12 en Leo suele contener partes muy auténticas de ti que durante mucho tiempo pudieron sentirse difíciles de mostrar libremente. "
    "Puede haber tensión entre la necesidad de expresarte y el miedo profundo a la exposición.\n\n"

    "A veces escondes creatividad, deseo o necesidad de reconocimiento para evitar juicio, vergüenza o sensación de vulnerabilidad. "
    "También puede aparecer agotamiento cuando sostienes una imagen demasiado fuerte hacia fuera.\n\n"

    "El aprendizaje pasa por permitirte existir con más autenticidad y menos miedo a ser viste."
),

"Virgo": (
    "La casa 12 en Virgo suele vivir mucho cansancio interno ligado a la autoexigencia, el control y la necesidad de sostenerlo todo correctamente. "
    "Puede costarte descansar de verdad porque siempre hay algo pendiente de resolver.\n\n"

    "A veces intentas ordenar mentalmente emociones que en realidad necesitan ser escuchadas o atravesadas. "
    "También puede aparecer ansiedad silenciosa respecto al cuerpo, el rendimiento o la sensación de no llegar suficientemente bien.\n\n"

    "El aprendizaje pasa por permitirte imperfecta sin sentir que todo se derrumba por ello."
),

"Libra": (
    "La casa 12 en Libra suele mostrar mucha sensibilidad respecto al vínculo, el equilibrio emocional y la necesidad de armonía. "
    "Puede afectarte profundamente el conflicto, incluso cuando hacia fuera intentas sostener calma.\n\n"

    "A veces callas demasiado para evitar tensión o desconexión con otras personas. "
    "También puede aparecer agotamiento emocional por adaptarte continuamente al entorno.\n\n"

    "El aprendizaje pasa por reconocer tus propias necesidades antes de desaparecer dentro de lo que otras personas esperan de ti."
),

"Escorpio": (
    "La casa 12 en Escorpio suele contener emociones muy profundas, intensas y difíciles de compartir completamente. "
    "Puede haber miedo a mostrar ciertas partes de ti por temor a sentirte vulnerable o expueste.\n\n"

    "A veces sostienes muchísimo en silencio hasta que algo termina desbordándose de golpe. "
    "También puede existir hipervigilancia emocional o necesidad constante de controlar lo que ocurre dentro.\n\n"

    "El aprendizaje pasa por descubrir que no necesitas vivir permanentemente en defensa emocional."
),

"Sagitario": (
    "La casa 12 en Sagitario suele necesitar amplitud interna, silencio y espacio para recuperar sentido cuando algo emocionalmente se vuelve demasiado pesado. "
    "Puede haber agotamiento profundo cuando sientes que pierdes dirección o perspectiva.\n\n"

    "A veces intentas escapar mentalmente hacia ideas, proyectos o explicaciones grandes para no quedarte demasiado tiempo en emociones difíciles. "
    "También puede aparecer frustración silenciosa cuando la vida no encaja con la visión que esperabas.\n\n"

    "El aprendizaje pasa por permitirte atravesar incertidumbre sin necesitar encontrar inmediatamente una salida o explicación."
),

"Capricornio": (
    "La casa 12 en Capricornio suele mostrar mucha contención emocional y dificultad para relajarte completamente. "
    "Puede haber sensación interna de tener que sostener demasiado incluso cuando estás agotade.\n\n"

    "A veces te cuesta reconocer cansancio, necesidad o vulnerabilidad porque una parte de ti siente que no puede permitirse aflojar. "
    "También puede aparecer soledad emocional silenciosa detrás de una imagen fuerte o muy responsable.\n\n"

    "El aprendizaje pasa por descubrir que descansar también es una forma de sostenerte."
),

"Acuario": (
    "La casa 12 en Acuario suele mostrar una vida interna muy activa, observadora y difícil de compartir completamente. "
    "Puede haber sensación de diferencia o distancia incluso estando rodeade de personas.\n\n"

    "A veces necesitas retirarte mucho para recuperar claridad o sensación de espacio propio. "
    "También puede aparecer tendencia a racionalizar emociones profundas para no sentir que éstas te absorben.\n\n"

    "El aprendizaje pasa por permitir conexión emocional sin sentir que necesitas perder libertad o individualidad."
),

"Piscis": (
    "La casa 12 en Piscis intensifica mucho la sensibilidad emocional y la permeabilidad al entorno. "
    "Puede costarte distinguir claramente qué pertenece a tu mundo interno y qué estás absorbiendo alrededor.\n\n"

    "A veces necesitas retirarte porque todo resulta demasiado intenso, ruidoso o emocionalmente invasivo. "
    "También puede aparecer tendencia a desaparecer emocionalmente, desconectarte o perder claridad cuando algo te sobrepasa.\n\n"

    "El aprendizaje pasa por desarrollar límites más conscientes sin cerrar completamente tu sensibilidad."
),

}


# ─── TEXTOS: PLANETAS EN CASA 8 ─────────────────────────────────────────────
# Cómo vive cada planeta la vulnerabilidad,
# la intimidad, la transformación y la exposición emocional.

PLANETAS_CASA8 = {

"Sol": (
    "El Sol en casa 8 suele vivir la identidad de forma intensa y transformadora. "
    "Las experiencias importantes rara vez pasan por tu vida sin dejar huella profunda.\n\n"

    "Puede haber necesidad de comprender lo que ocurre por debajo de la superficie y dificultad para sostener relaciones completamente superficiales. "
    "También puede aparecer miedo a perder control emocional o sensación de quedar demasiado expueste cuando algo te importa de verdad.\n\n"

    "El aprendizaje pasa por descubrir que mostrar vulnerabilidad no disminuye tu fuerza."
),

"Luna": (
    "La Luna en casa 8 suele vivir las emociones con muchísima profundidad. "
    "Puede haber gran sensibilidad respecto a la confianza, el abandono, la intimidad o la pérdida emocional.\n\n"

    "A veces sientes más de lo que muestras y proteges mucho lo que ocurre dentro de ti. "
    "También puede aparecer miedo intenso a depender emocionalmente o a quedar demasiado vulnerable frente a otras personas.\n\n"

    "El aprendizaje pasa por permitir cercanía sin sentir que necesitas controlar completamente lo que sientes."
),

"Mercurio": (
    "Mercurio en casa 8 suele mostrar una mente observadora, profunda y muy sensible a lo oculto o implícito. "
    "Puede haber necesidad de entender lo que otras personas callan, esconden o no expresan claramente.\n\n"

    "A veces analizas mucho los vínculos, las emociones o las dinámicas de poder para sentir mayor seguridad. "
    "También puede aparecer tendencia a pensar compulsivamente situaciones emocionalmente intensas.\n\n"

    "El aprendizaje pasa por permitir que ciertas experiencias se vivan sin intentar controlarlas completamente desde la mente."
),

"Venus": (
    "Venus en casa 8 suele vivir el amor y el vínculo con mucha intensidad emocional. "
    "Las relaciones importantes pueden remover partes muy profundas de ti.\n\n"

    "Puede haber necesidad de cercanía muy fuerte mezclada con miedo a la pérdida, al rechazo o a la traición. "
    "También puede aparecer dificultad para vivir el afecto de forma ligera cuando algo toca emocionalmente de verdad.\n\n"

    "El aprendizaje pasa por permitir amor profundo sin convertir el vínculo en un lugar de vigilancia o defensa constante."
),

"Marte": (
    "Marte en casa 8 suele contener mucha intensidad emocional y energética. "
    "Puede haber reacciones muy fuertes cuando sientes amenaza, pérdida de control o vulnerabilidad.\n\n"

    "A veces acumulas tensión durante mucho tiempo hasta que termina saliendo de golpe. "
    "También puede aparecer necesidad de controlar emocionalmente ciertas situaciones para no sentirte expueste o indefense.\n\n"

    "El aprendizaje pasa por reconocer antes lo que ocurre dentro de ti sin esperar siempre al límite."
),

"Júpiter": (
    "Júpiter en casa 8 suele buscar comprensión profunda de los procesos emocionales, psicológicos o transformadores. "
    "Puede haber necesidad de encontrar sentido incluso dentro de experiencias difíciles o intensas.\n\n"

    "A veces tiendes a ampliar emocionalmente ciertas situaciones o a vivir procesos internos con mucha intensidad filosófica o existencial. "
    "También puede existir capacidad importante para acompañar a otras personas en momentos complejos.\n\n"

    "El aprendizaje pasa por sostener profundidad sin perder completamente ligereza o perspectiva."
),

"Saturno": (
    "Saturno en casa 8 suele vivir la vulnerabilidad con mucha contención y cautela. "
    "Puede resultar difícil confiar plenamente o mostrar ciertas necesidades emocionales.\n\n"

    "A veces controlas muchísimo lo que sientes porque abrirte puede vivirse como algo arriesgado o inseguro. "
    "También puede aparecer miedo profundo a depender, perder estabilidad o quedar emocionalmente expueste.\n\n"

    "El aprendizaje pasa por descubrir que protegerte constantemente también puede aislarte."
),

"Urano": (
    "Urano en casa 8 suele vivir tensión entre la necesidad de intimidad y la necesidad de libertad emocional. "
    "Puede costarte sostener dinámicas afectivas demasiado rígidas o emocionalmente absorbentes.\n\n"

    "A veces necesitas tomar distancia de forma repentina cuando algo empieza a sentirse invasivo o demasiado intenso. "
    "También puede haber cambios emocionales bruscos o procesos internos difíciles de prever incluso para ti.\n\n"

    "El aprendizaje pasa por permitir profundidad emocional sin sentir que necesitas romper el vínculo para conservar espacio propio."
),

"Neptuno": (
    "Neptuno en casa 8 suele vivir la intimidad y la vulnerabilidad de forma muy sensible y permeable. "
    "Puede costarte distinguir claramente entre lo que sientes tú y lo que absorbes emocionalmente de otras personas.\n\n"

    "A veces idealizas vínculos intensos o pierdes claridad emocional cuando algo te afecta profundamente. "
    "También puede aparecer tendencia a fusionarte demasiado con el dolor, el deseo o las necesidades ajenas.\n\n"

    "El aprendizaje pasa por desarrollar límites más conscientes sin cerrar completamente tu sensibilidad."
),

"Plutón": (
    "Plutón en casa 8 intensifica profundamente todos los temas ligados a la vulnerabilidad, la intimidad y la transformación emocional. "
    "Las experiencias importantes suelen vivirse con mucha profundidad y rara vez desde la superficie.\n\n"

    "Puede haber miedo fuerte a la pérdida, necesidad de control emocional o dificultad para confiar plenamente. "
    "También puede existir tendencia a vivir los vínculos desde intensidad extrema o hipervigilancia emocional.\n\n"

    "El aprendizaje pasa por descubrir que profundidad no significa permanecer permanentemente en tensión o defensa."
),

"Quirón": (
    "Quirón en casa 8 suele mostrar heridas profundas ligadas a la confianza, la intimidad y la exposición emocional. "
    "Puede costarte abrir ciertas partes de ti por miedo a que te dañen, rechacen o malinterpreten.\n\n"

    "A veces deseas mucha cercanía mientras otra parte de ti se protege constantemente de ella. "
    "También puede haber sensibilidad muy fuerte respecto a pérdida, dependencia o traición.\n\n"

    "El aprendizaje pasa por permitir vulnerabilidad sin sentir que eso te deja indefense."
),

"Lilith": (
    "Lilith en casa 8 intensifica mucho la relación con el deseo, la vulnerabilidad y las dinámicas de poder emocional. "
    "Puede haber una percepción muy fina de lo oculto, lo ambiguo o lo que otras personas contienen.\n\n"

    "A veces proteges ferozmente ciertas partes de ti porque mostrar vulnerabilidad se siente peligroso. "
    "También puede aparecer tensión entre el deseo de profundidad emocional y el miedo a perder control.\n\n"

    "El aprendizaje pasa por descubrir que intensidad no tiene por qué convertirse siempre en defensa."
),

}


# ─── TEXTOS: PLANETAS EN CASA 12 ────────────────────────────────────────────
# Cómo vive cada planeta la sensibilidad,
# el retiro, el agotamiento emocional y lo difícil de expresar.

PLANETAS_CASA12 = {

"Sol": (
    "El Sol en casa 12 suele vivir la identidad de forma muy interna y difícil de mostrar completamente hacia fuera. "
    "Puede haber partes importantes de ti que durante mucho tiempo permanecen ocultas, contenidas o poco reconocidas incluso por ti misme.\n\n"

    "A veces te cuesta sentir claramente quién eres cuando estás demasiado pendiente del entorno o absorbiendo lo que ocurre alrededor. "
    "También puede aparecer necesidad fuerte de retirarte para recuperar claridad interna.\n\n"

    "El aprendizaje pasa por permitirte existir con más visibilidad y menos miedo a mostrar lo que realmente eres."
),

"Luna": (
    "La Luna en casa 12 suele vivir las emociones de forma muy profunda y silenciosa. "
    "Puede haber muchísima sensibilidad hacia el entorno, incluso cuando hacia fuera pareces tranquila.\n\n"

    "A veces absorbes emociones ajenas sin darte cuenta o guardas lo que sientes durante demasiado tiempo. "
    "También puede aparecer necesidad fuerte de aislamiento emocional cuando algo resulta demasiado intenso.\n\n"

    "El aprendizaje pasa por reconocer antes lo que sientes en lugar de contenerlo hasta el agotamiento."
),

"Mercurio": (
    "Mercurio en casa 12 suele mostrar una mente muy activa internamente, aunque muchas veces difícil de expresar con claridad hacia fuera. "
    "Puede haber tendencia a pensar muchísimo en silencio.\n\n"

    "A veces das vueltas mentalmente a emociones o situaciones que no terminas de compartir completamente. "
    "También puede aparecer dificultad para ordenar ciertos pensamientos porque una parte de ellos opera de manera muy intuitiva o poco racional.\n\n"

    "El aprendizaje pasa por permitir que lo interno encuentre palabras sin exigir claridad absoluta desde el principio."
),

"Venus": (
    "Venus en casa 12 suele vivir el afecto y la necesidad emocional de forma muy sensible, reservada o difícil de mostrar directamente. "
    "Puede costarte expresar ciertas necesidades afectivas por miedo al rechazo, a incomodar o a sentir demasiada vulnerabilidad.\n\n"

    "A veces amas en silencio, sostienes demasiado o priorizas emocionalmente a otras personas antes que a ti. "
    "También puede aparecer tendencia a idealizar vínculos o a desaparecer emocionalmente cuando algo duele mucho.\n\n"

    "El aprendizaje pasa por permitirte necesitar y recibir sin esconder continuamente lo que sientes."
),

"Marte": (
    "Marte en casa 12 suele contener mucha energía emocional o rabia acumulada que no siempre encuentra salida clara. "
    "Puede costarte expresar enfado directamente, especialmente si aprendiste pronto que hacerlo generaba conflicto o peligro.\n\n"

    "A veces sostienes demasiado hasta que la tensión termina saliendo de golpe o transformándose en agotamiento interno. "
    "También puede aparecer irritación difícil de identificar claramente mientras todavía está contenida.\n\n"

    "El aprendizaje pasa por reconocer antes lo que necesitas defender o expresar."
),

"Júpiter": (
    "Júpiter en casa 12 suele mostrar una vida interna amplia, intuitiva y muy conectada con la necesidad de encontrar sentido profundo a la experiencia. "
    "Puede haber capacidad importante para comprender emocionalmente procesos complejos.\n\n"

    "A veces necesitas mucho silencio o retiro para recuperar perspectiva y claridad. "
    "También puede aparecer tendencia a refugiarte demasiado en ideas, espiritualidad o mundos internos cuando la realidad resulta difícil de sostener.\n\n"

    "El aprendizaje pasa por integrar profundidad interna sin desaparecer completamente de la vida cotidiana."
),

"Saturno": (
    "Saturno en casa 12 suele vivir el mundo interno con mucha contención y dificultad para relajarse completamente. "
    "Puede haber sensación silenciosa de carga emocional o responsabilidad constante.\n\n"

    "A veces te cuesta reconocer cansancio, tristeza o necesidad porque una parte de ti siente que debe seguir sosteniéndolo todo. "
    "También puede aparecer aislamiento emocional o dificultad para pedir ayuda incluso cuando realmente la necesitas.\n\n"

    "El aprendizaje pasa por descubrir que mostrar vulnerabilidad no significa perder dignidad ni fortaleza."
),

"Urano": (
    "Urano en casa 12 suele mostrar una vida interna muy activa, cambiante y difícil de controlar completamente. "
    "Puede haber pensamientos repentinos, intuiciones intensas o necesidad fuerte de espacio mental y emocional.\n\n"

    "A veces necesitas retirarte bruscamente cuando algo empieza a sentirse demasiado invasivo o saturante. "
    "También puede aparecer tensión entre el deseo de conexión y la necesidad profunda de independencia interna.\n\n"

    "El aprendizaje pasa por permitir libertad emocional sin convertir el aislamiento en única forma de protección."
),

"Neptuno": (
    "Neptuno en casa 12 intensifica muchísimo la sensibilidad emocional y la permeabilidad al entorno. "
    "Puede costarte distinguir claramente qué pertenece a tu experiencia interna y qué estás absorbiendo alrededor.\n\n"

    "A veces te desbordas emocionalmente sin entender exactamente por qué. "
    "También puede aparecer necesidad de escapar, desconectarte o desaparecer cuando algo resulta demasiado intenso.\n\n"

    "El aprendizaje pasa por desarrollar límites más conscientes sin cerrar completamente tu sensibilidad."
),

"Plutón": (
    "Plutón en casa 12 suele contener procesos emocionales muy profundos y difíciles de expresar completamente. "
    "Puede haber miedo a mostrar ciertas partes de ti o necesidad de mantener mucho control sobre lo que ocurre internamente.\n\n"

    "A veces sostienes emociones intensas en silencio durante mucho tiempo hasta que algo termina desbordándose. "
    "También puede aparecer hipervigilancia emocional o sensación de estar constantemente protegiendo algo muy vulnerable dentro de ti.\n\n"

    "El aprendizaje pasa por dejar de luchar continuamente contra lo que ocurre dentro."
),

"Quirón": (
    "Quirón en casa 12 suele mostrar heridas muy profundas y difíciles de nombrar claramente. "
    "Puede haber sensación de cargar emociones, vergüenzas o dolores que rara vez compartes completamente.\n\n"

    "A veces te aíslas cuando algo duele demasiado o intentas sostener en silencio lo que realmente necesitaría ser acompañado. "
    "También puede aparecer sensación de desconexión emocional difícil de explicar incluso estando rodeade de personas.\n\n"

    "El aprendizaje pasa por permitir que ciertas heridas dejen de existir únicamente en soledad."
),

"Lilith": (
    "Lilith en casa 12 suele contener emociones, deseos o impulsos muy profundos que durante mucho tiempo pudieron sentirse difíciles de aceptar o mostrar. "
    "Puede haber una parte de ti que vive intensamente por dentro mientras hacia fuera permanece mucho más contenida.\n\n"

    "A veces reprimes demasiado ciertas emociones hasta que terminan apareciendo de forma abrupta o difícil de controlar. "
    "También puede existir miedo a mostrar partes de ti que sientes demasiado intensas, incómodas o difíciles de explicar.\n\n"

    "El aprendizaje pasa por dejar de tratar ciertas zonas de ti como si necesitaran permanecer ocultas para siempre."
),

}




# ─── TEXTOS: ASPECTOS BASE ──────────────────────────────────────────────────
# Matiz general del tipo de aspecto.

ASPECTOS_BASE = {
    "=": (
        "La conjunción intensifica mucho esta combinación. "
        "Ambas partes tienden a mezclarse, por lo que puede costar separarlas o tomar distancia de lo que activan juntas."
    ),

    "□": (
        "La cuadratura suele generar tensión interna. "
        "Hay algo que necesita integrarse, pero normalmente no se vive de forma cómoda ni automática."
    ),

    "☍": (
        "La oposición suele vivirse como polaridad. "
        "A veces una parte de ti tira hacia un extremo y otra parte aparece reflejada en vínculos, conflictos o situaciones externas."
    ),

    "△": (
        "El trígono facilita que esta combinación fluya con más naturalidad. "
        "No elimina la profundidad del aspecto, pero puede hacer que encuentres recursos internos con mayor facilidad."
    ),

    "✶": (
        "El sextil abre una posibilidad de aprendizaje consciente. "
        "Puede no activarse solo, pero cuando le prestas atención permite trabajar esta combinación de una forma más manejable."
    ),
}


# ─── TEXTOS: PLUTÓN EN ASPECTO ──────────────────────────────────────────────

PLUTON_ASPECTO = {

"Sol": (
    "Plutón en aspecto con el Sol toca directamente la identidad, la voluntad y la manera en que ocupas tu lugar. "
    "Puede haber intensidad en torno al poder personal, miedo a perder control o necesidad de transformarte profundamente a lo largo de la vida.\n\n"
    "A veces puedes vivir ciertas etapas como crisis de identidad, momentos en los que una versión de ti deja de poder sostenerse."
),

"Luna": (
    "Plutón en aspecto con la Luna intensifica mucho la vida emocional. "
    "Puede haber emociones profundas, miedo al abandono, necesidad de control afectivo o dificultad para relajarte del todo en la intimidad.\n\n"
    "A veces sientes más de lo que muestras, o proteges mucho lo que ocurre dentro de ti."
),

"Mercurio": (
    "Plutón en aspecto con Mercurio da una mente intensa, penetrante y difícil de conformar con explicaciones superficiales. "
    "Puede haber tendencia a analizar demasiado, detectar lo oculto o dar muchas vueltas a lo que no se dice.\n\n"
    "A veces la mente intenta controlar lo que en realidad necesita ser sentido."
),

"Venus": (
    "Plutón en aspecto con Venus intensifica mucho el amor, el deseo, el apego y la manera en que te vinculas. "
    "Las relaciones pueden remover zonas profundas de vulnerabilidad, miedo a la pérdida o necesidad de control.\n\n"
    "A veces lo afectivo se vive con mucha intensidad, incluso cuando intentas mantenerlo ligero."
),

"Marte": (
    "Plutón en aspecto con Marte intensifica la fuerza, la rabia, el deseo y la capacidad de actuar. "
    "Puede haber mucha potencia interna, pero también dificultad para manejar la frustración, el conflicto o la sensación de amenaza.\n\n"
    "A veces reaccionas con mucha fuerza cuando algo toca una zona de vulnerabilidad."
),

"Júpiter": (
    "Plutón en aspecto con Júpiter intensifica las creencias, la búsqueda de sentido y la necesidad de expansión. "
    "Puede haber grandes cambios de visión, crisis de fe o momentos en los que una verdad interna se transforma radicalmente.\n\n"
    "A veces necesitas llegar hasta el fondo de una experiencia para poder comprenderla."
),

"Saturno": (
    "Plutón en aspecto con Saturno toca zonas profundas de control, miedo, responsabilidad y resistencia. "
    "Puede haber sensación de carga, dureza interna o necesidad de sostenerte incluso en situaciones muy exigentes.\n\n"
    "A veces puedes confundir fortaleza con aguantar demasiado."
),

"Urano": (
    "Plutón en aspecto con Urano une transformación profunda con necesidad de ruptura o liberación. "
    "Puede haber cambios internos bruscos, rechazo a estructuras opresivas o etapas donde algo se rompe para que puedas respirar de otra manera.\n\n"
    "A veces la transformación llega de forma repentina, antes de que puedas ordenarla del todo."
),

"Neptuno": (
    "Plutón en aspecto con Neptuno intensifica la sensibilidad, la percepción profunda y la relación con lo invisible o difícil de explicar. "
    "Puede haber mucha permeabilidad emocional, intuición o dificultad para distinguir entre deseo, miedo y fantasía.\n\n"
    "A veces necesitas poner límites claros a lo que absorbes o idealizas."
),

"Quirón": (
    "Plutón en aspecto con Quirón toca heridas profundas y procesos de transformación difíciles de atravesar de forma superficial. "
    "Puede haber zonas de dolor antiguo, vergüenza o vulnerabilidad que se activan con mucha intensidad.\n\n"
    "A veces la herida se convierte en un lugar de defensa antes de poder convertirse en consciencia."
),

"Lilith": (
    "Plutón en aspecto con Lilith intensifica la relación con el deseo, la sombra, el control y las partes de ti que no quieren ser domesticadas. "
    "Puede haber reacciones muy fuertes cuando algo toca tu libertad, tu vulnerabilidad o tu poder personal.\n\n"
    "A veces lo que más intentas controlar es precisamente lo que más necesita ser mirado."
),

}


# ─── TEXTOS: QUIRÓN EN ASPECTO ──────────────────────────────────────────────

QUIRON_ASPECTO = {

"Sol": (
    "Quirón en aspecto con el Sol toca la identidad, la autoestima y el derecho a ocupar tu lugar. "
    "Puede haber sensación de no ser suficiente, miedo a exponerte o dificultad para confiar plenamente en tu propia presencia.\n\n"
    "A veces intentas demostrar valor cuando en realidad necesitas dejar de dudar tanto de él."
),

"Luna": (
    "Quirón en aspecto con la Luna toca heridas emocionales profundas. "
    "Puede haber sensibilidad al abandono, al rechazo, al cuidado insuficiente o a la sensación de que no te han sostenido como necesitabas.\n\n"
    "A veces cuidas mucho a otras personas mientras te cuesta reconocer tu propia necesidad."
),

"Mercurio": (
    "Quirón en aspecto con Mercurio toca la voz, la palabra y la confianza en tu manera de pensar. "
    "Puede haber miedo a expresarte mal, a que no te entiendan o a que lo que dices no tenga valor.\n\n"
    "A veces la herida aparece en forma de duda constante sobre tu propia percepción."
),

"Venus": (
    "Quirón en aspecto con Venus toca heridas vinculadas al amor, el deseo, el merecimiento y la capacidad de recibir. "
    "Puede haber miedo al rechazo, dificultad para sentirte elegide o tendencia a adaptarte demasiado para conservar afecto.\n\n"
    "A veces cuesta creer que pueden quererte sin tener que ganártelo continuamente."
),

"Marte": (
    "Quirón en aspecto con Marte toca la acción, la rabia, la defensa y la capacidad de afirmarte. "
    "Puede haber miedo al conflicto, dificultad para poner límites o sensación de que tu fuerza no es segura.\n\n"
    "A veces contienes demasiado hasta que la energía sale de golpe."
),

"Júpiter": (
    "Quirón en aspecto con Júpiter toca la fe, el sentido y la confianza en la vida. "
    "Puede haber heridas ligadas a creencias, expectativas rotas o dificultad para sostener esperanza cuando algo duele.\n\n"
    "A veces buscas respuestas grandes para aliviar una herida más íntima."
),

"Saturno": (
    "Quirón en aspecto con Saturno toca la exigencia, la responsabilidad y el miedo a fallar. "
    "Puede haber sensación de tener que demostrar mucho, sostener demasiado o no permitirte mostrar fragilidad.\n\n"
    "A veces la herida se esconde detrás de una gran capacidad de aguante."
),

"Urano": (
    "Quirón en aspecto con Urano toca la diferencia, la pertenencia y la dificultad para sentirte completamente dentro de lo común. "
    "Puede haber sensación de rareza, distancia o rechazo a encajar en formas que no respetan tu singularidad.\n\n"
    "A veces te proteges alejándote antes de comprobar si realmente había espacio para ti."
),

"Neptuno": (
    "Quirón en aspecto con Neptuno toca la sensibilidad, la compasión y los límites emocionales. "
    "Puede haber tendencia a absorber demasiado, idealizar, salvar o perderte en el dolor ajeno.\n\n"
    "A veces la herida se mezcla con una enorme capacidad de sentir lo que otras personas no dicen."
),

"Plutón": (
    "Quirón en aspecto con Plutón toca heridas profundas, difíciles de mirar de forma ligera. "
    "Puede haber dolor antiguo, miedo a la vulnerabilidad o defensas muy fuertes alrededor de lo que todavía duele.\n\n"
    "A veces la transformación empieza precisamente donde más intentabas protegerte."
),

"Lilith": (
    "Quirón en aspecto con Lilith toca heridas ligadas al rechazo, la vergüenza y las partes de ti que aprendiste a esconder. "
    "Puede haber sensibilidad intensa cuando algo te hace sentir incorrecte, excesive o difícil de aceptar.\n\n"
    "A veces lo que más duele es también lo que más necesita recuperar dignidad."
),

}


# ─── TEXTOS: LILITH EN ASPECTO ──────────────────────────────────────────────

LILITH_ASPECTO = {

"Sol": (
    "Lilith en aspecto con el Sol toca la identidad, la expresión y el derecho a existir sin que te reduzcan expectativas externas. "
    "Puede haber una parte de ti que rechaza profundamente que te controlen, moldeen o invisibilicen.\n\n"
    "A veces mostrarte tal como eres despierta fuerza, pero también miedo a incomodar o que te juzguen."
),

"Luna": (
    "Lilith en aspecto con la Luna intensifica la vida emocional y la necesidad de protección interna. "
    "Puede haber sensibilidad extrema al abandono, la invasión emocional o la dependencia.\n\n"
    "A veces deseas cercanía y al mismo tiempo reaccionas fuerte cuando algo se acerca demasiado."
),

"Mercurio": (
    "Lilith en aspecto con Mercurio da una mente incisiva, libre y difícil de domesticar. "
    "Puede haber necesidad de decir lo que otras personas evitan, cuestionar discursos cerrados o pensar desde lugares poco convencionales.\n\n"
    "A veces la palabra puede volverse defensa, provocación o forma de recuperar poder."
),

"Venus": (
    "Lilith en aspecto con Venus intensifica el amor, el deseo y la necesidad de no perderte dentro del vínculo. "
    "Puede haber atracción hacia relaciones intensas, pero también rechazo profundo a sentir dependencia o control afectivo.\n\n"
    "A veces el deseo y la defensa aparecen mezclados."
),

"Marte": (
    "Lilith en aspecto con Marte intensifica la fuerza, la rabia, el deseo y la reacción instintiva. "
    "Puede haber una energía muy potente cuando sientes amenaza, injusticia o invasión.\n\n"
    "A veces reaccionas antes de poder ordenar del todo lo que estás defendiendo."
),

"Júpiter": (
    "Lilith en aspecto con Júpiter toca la libertad, las creencias y el rechazo a vivir dentro de marcos demasiado estrechos. "
    "Puede haber necesidad de ampliar, cuestionar o romper con verdades heredadas.\n\n"
    "A veces la búsqueda de libertad se vuelve tan fuerte que cualquier límite se siente insoportable."
),

"Saturno": (
    "Lilith en aspecto con Saturno toca la tensión entre control y libertad. "
    "Puede haber rechazo profundo a la autoridad, la obligación o la exigencia, pero también miedo a soltar del todo el control.\n\n"
    "A veces una parte de ti se endurece para no sentirse sometida."
),

"Urano": (
    "Lilith en aspecto con Urano intensifica la diferencia, la independencia y el rechazo a encajar en lo esperado. "
    "Puede haber necesidad muy fuerte de espacio propio y de vivir según reglas internas.\n\n"
    "A veces la cercanía se vuelve difícil cuando sientes que amenaza tu libertad."
),

"Neptuno": (
    "Lilith en aspecto con Neptuno intensifica la sensibilidad, el deseo de disolución y la dificultad para poner límites claros. "
    "Puede haber magnetismo, intuición y mucha permeabilidad emocional.\n\n"
    "A veces cuesta distinguir entre entrega, idealización, deseo y huida."
),

"Plutón": (
    "Lilith en aspecto con Plutón toca zonas muy profundas de deseo, control, sombra y poder personal. "
    "Puede haber intensidad emocional, miedo a perder control o reacciones fuertes cuando algo toca tu vulnerabilidad.\n\n"
    "A veces lo que intentas contener vuelve con más fuerza precisamente porque necesita ser mirado."
),

"Quirón": (
    "Lilith en aspecto con Quirón toca heridas ligadas al rechazo, la vergüenza y la sensación de no encajar. "
    "Puede haber partes de ti que aprendiste a esconder porque parecían demasiado intensas, raras o incómodas para el entorno.\n\n"
    "A veces sanar no significa suavizarte, sino dejar de rechazar lo que eres."
),

}



# ─── CÁLCULO ASTROLÓGICO ──────────────────────────────────────────────────────

def geocodificar(ciudad):
    g = Nominatim(user_agent="ai_planetas_sombra_profunda", timeout=10)
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


def calcular_aspectos_sombra(planetas):

    ASPECTOS_PLUTON = {
        0:   ("Conjunción", "=", 10),
        60:  ("Sextil", "✶", 6),
        90:  ("Cuadratura", "□", 8),
        120: ("Trígono", "△", 8),
        180: ("Oposición", "☍", 8),
    }

    ASPECTOS_QUIRON = {
        0:   ("Conjunción", "=", 5),
        60:  ("Sextil", "✶", 3),
        90:  ("Cuadratura", "□", 4),
        120: ("Trígono", "△", 4),
        180: ("Oposición", "☍", 4),
    }

    ASPECTOS_LILITH = {
        0:   ("Conjunción", "=", 4),
        60:  ("Sextil", "✶", 2),
        90:  ("Cuadratura", "□", 3),
        120: ("Trígono", "△", 3),
        180: ("Oposición", "☍", 3),
    }

    ORBES_POR_PUNTO = {
        "Plutón": ASPECTOS_PLUTON,
        "Quirón": ASPECTOS_QUIRON,
        "Lilith": ASPECTOS_LILITH,
    }

    foco = ["Plutón", "Quirón", "Lilith"]
    aspectos = []
    nombres = list(planetas.keys())

    for p1 in foco:
        if p1 not in planetas:
            continue

        for p2 in nombres:
            if p2 == p1:
                continue

            # Evitar duplicar aspectos entre Plutón, Quirón y Lilith
            if p2 in foco and foco.index(p2) < foco.index(p1):
                continue

            diff = abs(planetas[p1]["lon"] - planetas[p2]["lon"])
            if diff > 180:
                diff = 360 - diff

            aspectos_def_p1 = ORBES_POR_PUNTO[p1]
            aspectos_def_p2 = ORBES_POR_PUNTO.get(p2)

            for angulo, (nombre_asp, simbolo_asp, orbe_p1) in aspectos_def_p1.items():

                # Si el otro punto también es Plutón/Quirón/Lilith,
                # usamos el orbe más restrictivo entre ambos.
                if aspectos_def_p2:
                    _, _, orbe_p2 = aspectos_def_p2[angulo]
                    orbe_real = min(orbe_p1, orbe_p2)
                else:
                    orbe_real = orbe_p1

                # Plutón: oposición ampliada a 10° solo con Sol o Luna.
                # No se aplica si el otro punto es Quirón o Lilith.
                if (
                    p1 == "Plutón"
                    and p2 in ("Sol", "Luna")
                    and simbolo_asp == "☍"
                ):
                    orbe_real = 10

                orbe_val = round(abs(diff - angulo), 2)

                if orbe_val <= orbe_real:
                    aspectos.append({
                        "p1": p1,
                        "p2": p2,
                        "aspecto": nombre_asp,
                        "simbolo": simbolo_asp,
                        "orbe": orbe_val,
                        "angulo": angulo,
                        "relevancia": "exacto" if orbe_val <= 1.0 else "estructural",
                    })
                    break

    return sorted(
        aspectos,
        key=lambda x: (foco.index(x["p1"]), x["orbe"])
    )

def interpretar_aspecto_sombra(asp):
    p1 = asp["p1"]
    p2 = asp["p2"]
    simbolo = asp["simbolo"]
    orbe = asp.get("orbe", None)

    if p1 == "Plutón":
        base = PLUTON_ASPECTO.get(p2, "")
    elif p1 == "Quirón":
        base = QUIRON_ASPECTO.get(p2, "")
    elif p1 == "Lilith":
        base = LILITH_ASPECTO.get(p2, "")
    else:
        base = ""

    matiz = ASPECTOS_BASE.get(simbolo, "")

    if orbe is not None:
        if orbe <= 1:
            intensidad = (
                "\n\nEste aspecto es muy cerrado, por lo que suele sentirse con bastante fuerza. "
                "No aparece como algo lejano o secundario, sino como una dinámica que puede activarse con claridad en momentos importantes."
            )
        elif orbe <= 3:
            intensidad = (
                "\n\nEl orbe es relativamente cercano, así que esta combinación puede sentirse de forma bastante reconocible."
            )
        else:
            intensidad = (
                "\n\nAunque el orbe es más amplio, el aspecto puede seguir apareciendo como un matiz importante dentro de la carta."
            )
    else:
        intensidad = ""

    return base + "\n\n" + matiz + intensidad


# ─── TEXTOS DE SECCIÓN ────────────────────────────────────────────────────────

def _get_asp(aspectos, p1, p2):
    return next(
        (a for a in aspectos
         if (a["p1"] == p1 and a["p2"] == p2) or (a["p1"] == p2 and a["p2"] == p1)),
        None
    )


def _fmt_aspecto(asp):
    return f"{asp['p1']}–{asp['p2']} en {asp['aspecto'].lower()} (orbe {asp['orbe']}°)"


def planetas_en_casa(planetas, casa):
    excluir = {"Nodo Norte", "Nodo Sur"}
    return [
        nombre for nombre, datos in planetas.items()
        if datos.get("casa") == casa and nombre not in excluir
    ]


def signo_cuspide_casa(cuspides, num_casa):
    lon = cuspides[num_casa - 1]
    signo, grado = grados_a_signo(lon)
    return signo


def texto_marco_general(carta, aspectos):
    planetas = carta["planetas"]
    cuspides = carta["cuspides"]

    plu = planetas.get("Plutón", {})
    qui = planetas.get("Quirón", {})
    lil = planetas.get("Lilith", {})

    plu_sig, plu_casa = plu.get("signo", ""), plu.get("casa", "")
    qui_sig, qui_casa = qui.get("signo", ""), qui.get("casa", "")
    lil_sig, lil_casa = lil.get("signo", ""), lil.get("casa", "")

    signo_c8 = signo_cuspide_casa(cuspides, 8)
    signo_c12 = signo_cuspide_casa(cuspides, 12)

    texto = (
        "Este documento entra en zonas de la carta que suelen vivirse con más intensidad, más defensa o más dificultad para nombrar. "
        "No describe una identidad fija ni una condena personal. "
        "Se acerca a lugares donde pueden aparecer miedo, control, vergüenza, deseo, aislamiento, dependencia, heridas antiguas o reacciones difíciles de comprender desde fuera.\n\n"

        f"Plutón en {plu_sig}, Casa {plu_casa}: muestra dónde puedes vivir procesos intensos de transformación, pérdida de control, apego, defensa o profundidad emocional.\n"
        f"Quirón en {qui_sig}, Casa {qui_casa}: muestra una zona especialmente sensible, donde puede haber herida, inseguridad, vergüenza o necesidad de protección.\n"
        f"Lilith en {lil_sig}, Casa {lil_casa}: muestra una parte de ti menos domesticable, más instintiva, que puede reaccionar con fuerza cuando se siente atrapada, reducida o invadida.\n\n"

        f"La Casa 8 en {signo_c8} habla de cómo atraviesas la vulnerabilidad, la intimidad, la pérdida, la confianza y los vínculos que remueven profundamente.\n"
        f"La Casa 12 en {signo_c12} habla de cómo vives el retiro, la sensibilidad, el agotamiento emocional, lo inconsciente y aquello que cuesta poner en palabras."
    )

    if aspectos:
        lista = ", ".join(_fmt_aspecto(a) for a in aspectos)
        texto += f"\n\nAspectos principales observados en este bloque: {lista}."

    return texto


def texto_pluton(carta, aspectos):
    planetas = carta["planetas"]
    plu = planetas.get("Plutón", {})
    sig = plu.get("signo", "")
    casa = plu.get("casa", 1)
    ret = plu.get("retrogrado", False)

    t = PLUTON_SIGNO.get(sig, "")
    t += "\n\n" + PLUTON_CASA.get(casa, "")

    if ret:
        t += (
            "\n\nPlutón está retrógrado. La intensidad tiende a dirigirse primero hacia dentro. "
            "Puede haber procesos profundos que no se ven claramente desde fuera, pero que por dentro acumulan mucha fuerza. "
            "A veces tardas en mostrar lo que está ocurriendo, aunque internamente algo ya esté transformándose."
        )

    for asp in aspectos:
        if asp["p1"] == "Plutón" or asp["p2"] == "Plutón":
            interp = interpretar_aspecto_sombra(asp)
            if interp:
                t += f"\n\n{_fmt_aspecto(asp)}.\n{interp}"

    return t


def texto_quiron(carta, aspectos):
    planetas = carta["planetas"]
    qui = planetas.get("Quirón", {})
    sig = qui.get("signo", "")
    casa = qui.get("casa", 1)
    ret = qui.get("retrogrado", False)

    t = QUIRON_SIGNO.get(sig, "")
    t += "\n\n" + QUIRON_CASA.get(casa, "")

    if ret:
        t += (
            "\n\nQuirón está retrógrado. La herida tiende a vivirse de manera muy interna. "
            "Puede costarte mostrar con claridad dónde duele, incluso cuando esa sensibilidad está muy presente. "
            "A veces aprendes a protegerte antes de entender del todo qué parte de ti necesitaba cuidado."
        )

    for asp in aspectos:
        if asp["p1"] == "Quirón" or asp["p2"] == "Quirón":
            interp = interpretar_aspecto_sombra(asp)
            if interp:
                t += f"\n\n{_fmt_aspecto(asp)}.\n{interp}"

    return t


def texto_lilith(carta, aspectos):
    planetas = carta["planetas"]
    lil = planetas.get("Lilith", {})
    sig = lil.get("signo", "")
    casa = lil.get("casa", 1)

    t = LILITH_SIGNO.get(sig, "")
    t += "\n\n" + LILITH_CASA.get(casa, "")

    for asp in aspectos:
        if asp["p1"] == "Lilith" or asp["p2"] == "Lilith":
            interp = interpretar_aspecto_sombra(asp)
            if interp:
                t += f"\n\n{_fmt_aspecto(asp)}.\n{interp}"

    return t


def texto_casa8(carta):
    planetas = carta["planetas"]
    cuspides = carta["cuspides"]

    signo = signo_cuspide_casa(cuspides, 8)
    t = CASA8_SIGNO.get(signo, "")

    dentro = planetas_en_casa(planetas, 8)

    if dentro:
        t += "\n\nEn tu carta, la Casa 8 contiene los siguientes planetas o puntos: "
        t += ", ".join(dentro) + "."

        for nombre in dentro:
            interp = PLANETAS_CASA8.get(nombre, "")
            if interp:
                t += f"\n\n{nombre} en Casa 8.\n{interp}"
    else:
        t += (
            "\n\nEn tu carta no hay planetas principales dentro de la Casa 8. "
            "Aun así, esta casa sigue hablando de cómo atraviesas la intimidad, la vulnerabilidad, la confianza y los procesos emocionales profundos."
        )

    return t


def texto_casa12(carta):
    planetas = carta["planetas"]
    cuspides = carta["cuspides"]

    signo = signo_cuspide_casa(cuspides, 12)
    t = CASA12_SIGNO.get(signo, "")

    dentro = planetas_en_casa(planetas, 12)

    if dentro:
        t += "\n\nEn tu carta, la Casa 12 contiene los siguientes planetas o puntos: "
        t += ", ".join(dentro) + "."

        for nombre in dentro:
            interp = PLANETAS_CASA12.get(nombre, "")
            if interp:
                t += f"\n\n{nombre} en Casa 12.\n{interp}"
    else:
        t += (
            "\n\nEn tu carta no hay planetas principales dentro de la Casa 12. "
            "Aun así, esta casa sigue hablando de cómo vives el retiro, la sensibilidad, el agotamiento emocional y aquello que cuesta poner en palabras."
        )

    return t


def texto_integracion(carta, aspectos):
    planetas = carta["planetas"]
    cuspides = carta["cuspides"]

    plu = planetas.get("Plutón", {})
    qui = planetas.get("Quirón", {})
    lil = planetas.get("Lilith", {})

    signo_c8 = signo_cuspide_casa(cuspides, 8)
    signo_c12 = signo_cuspide_casa(cuspides, 12)

    partes = []

    partes.append(
        f"En conjunto, este bloque muestra una zona de lectura especialmente profunda de la carta. "
        f"Plutón en {plu.get('signo', '')}, Casa {plu.get('casa', '')}, señala dónde la intensidad puede obligarte a atravesar procesos de transformación real. "
        f"Quirón en {qui.get('signo', '')}, Casa {qui.get('casa', '')}, muestra una sensibilidad que no siempre se deja tocar fácilmente. "
        f"Lilith en {lil.get('signo', '')}, Casa {lil.get('casa', '')}, señala una parte de ti que no acepta ser reducida, controlada o domesticada sin reaccionar."
    )

    partes.append(
        f"La Casa 8 en {signo_c8} describe cómo te acercas a la intimidad, la pérdida de control, la confianza y los vínculos que remueven. "
        f"La Casa 12 en {signo_c12} muestra cómo se viven el cansancio profundo, el retiro, la sensibilidad y aquello que a veces permanece oculto incluso para ti."
    )

    if aspectos:
        tensos = [a for a in aspectos if a["simbolo"] in ("□", "☍")]
        fluidos = [a for a in aspectos if a["simbolo"] in ("△", "✶")]
        conj = [a for a in aspectos if a["simbolo"] == "="]

        if tensos:
            partes.append(
                "Los aspectos tensos de este bloque indican zonas donde la intensidad, la herida o la reacción defensiva pueden aparecer con más fricción. "
                "No significan algo negativo en sí mismo, pero sí muestran lugares donde puede costarte integrar lo que sientes sin entrar en control, cierre o lucha interna."
            )

        if conj:
            partes.append(
                "Las conjunciones intensifican mucho lo que tocan. "
                "Cuando Plutón, Quirón o Lilith están unidos a otro punto de la carta, esa parte de ti puede vivirse con más profundidad, más sensibilidad o más dificultad para tomar distancia."
            )

        if fluidos:
            partes.append(
                "Los aspectos fluidos muestran recursos internos para atravesar estas zonas con más naturalidad. "
                "No eliminan la intensidad, pero pueden facilitar comprensión, integración y mayor honestidad contigo."
            )

    partes.append(
        "La clave de este documento no es corregir estas zonas ni convertirlas en algo más amable de manera artificial. "
        "La clave es poder mirarlas sin rechazo, reconocer cuándo se activan y dejar de vivirlas únicamente desde la defensa, el silencio o el control."
    )

    return "\n\n".join(partes)


def texto_orientacion(carta, aspectos):
    planetas = carta["planetas"]
    cuspides = carta["cuspides"]

    plu = planetas.get("Plutón", {})
    qui = planetas.get("Quirón", {})
    lil = planetas.get("Lilith", {})

    signo_c8 = signo_cuspide_casa(cuspides, 8)
    signo_c12 = signo_cuspide_casa(cuspides, 12)

    reconocer = (
        "Puedes reconocer que este bloque está activo cuando una situación toca una zona desproporcionadamente sensible: "
        "miedo a perder el control, dificultad para confiar, necesidad de desaparecer, vergüenza, rabia contenida, deseo intenso, cierre emocional o sensación de amenaza interna.\n\n"

        f"Plutón en Casa {plu.get('casa', '')} suele activarse cuando algo te obliga a mirar una intensidad que no puedes resolver solo desde la voluntad. "
        f"Quirón en Casa {qui.get('casa', '')} suele activarse cuando una experiencia toca una herida antigua o una sensación de insuficiencia. "
        f"Lilith en Casa {lil.get('casa', '')} suele activarse cuando sientes invasión, reducción, control o pérdida de libertad interna."
    )

    casa8 = (
        f"La Casa 8 en {signo_c8} se activa especialmente en vínculos intensos, procesos de intimidad, pérdidas, dependencias, secretos, duelos o experiencias donde aparece vulnerabilidad real. "
        "Cuando esta zona se mueve, puedes sentir que algo dentro de ti necesita protegerse antes incluso de entender exactamente qué está ocurriendo."
    )

    casa12 = (
        f"La Casa 12 en {signo_c12} se activa especialmente en momentos de cansancio profundo, retiro, saturación emocional, confusión interna o necesidad de silencio. "
        "Cuando esta zona se mueve, puede costarte explicar lo que te pasa, pero eso no significa que no esté ocurriendo algo importante."
    )

    si_no = (
        "Cuando estas zonas no se reconocen, es fácil vivirlas como problemas aislados: una relación que duele, una reacción excesiva, una etapa de agotamiento, una obsesión, una necesidad de control o una retirada que no sabes explicar.\n\n"
        "Pero muchas veces no se trata solo de lo que ocurre fuera. Algo interno ha sido tocado y necesita ser mirado con más honestidad."
    )

    cuidado = (
        "La orientación no es forzarte a abrir lo que todavía necesita protección. "
        "Tampoco se trata de justificar cualquier reacción porque venga de una herida. "
        "Se trata de reconocer con más precisión qué se activa, qué estás defendiendo y qué parte de ti necesita tiempo, verdad y cuidado."
    )

    return {
        "reconocer": reconocer,
        "casa8": casa8,
        "casa12": casa12,
        "si_no": si_no,
        "cuidado": cuidado,
    }


# ─── GENERACIÓN LATEX ─────────────────────────────────────────────────────────

def esc(texto):
    if not texto:
        return ""

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

def generar_latex(carta, nombre, anio, mes, dia, hora, minuto,
                  ciudad, lat, lon, tz_name, ruta_rueda, aspectos):
    planetas = carta["planetas"]
    cuspides = carta["cuspides"]
    asc = carta["asc"]
    mc = carta["mc"]

    plu = planetas.get("Plutón", {})
    qui = planetas.get("Quirón", {})
    lil = planetas.get("Lilith", {})

    signo_c8 = signo_cuspide_casa(cuspides, 8)
    signo_c12 = signo_cuspide_casa(cuspides, 12)

    fecha_str = f"{dia:02d}/{mes:02d}/{anio}"
    hora_str = f"{hora:02d}:{minuto:02d}"
    tz_obj = pytz.timezone(tz_name)
    dt_local = tz_obj.localize(datetime(anio, mes, dia, hora, minuto))
    utc_off = dt_local.strftime("%z")
    utc_str = f"UTC{utc_off[:3]}:{utc_off[3:]}"
    nom_esc = esc(nombre)
    ciu_esc = esc(ciudad)

    def signo_casa(p):
        return f"{esc(p.get('signo',''))} — Casa {p.get('casa','')} {grado_a_dms(p.get('grado',0))}"

    def parrafos(texto):
        return "\n\n".join(esc(p) for p in texto.split("\n\n") if p.strip())

    t_marco = texto_marco_general(carta, aspectos)
    t_plu = texto_pluton(carta, aspectos)
    t_qui = texto_quiron(carta, aspectos)
    t_lil = texto_lilith(carta, aspectos)
    t_c8 = texto_casa8(carta)
    t_c12 = texto_casa12(carta)
    t_integ = texto_integracion(carta, aspectos)
    t_or = texto_orientacion(carta, aspectos)

    _ASP_TEX = {"=": "conj", "☍": "opo", "□": "cua", "△": "tri", "✶": "sex"}

    asp_rows = ""
    for a in aspectos:
        asp_rows += (
            f"  {esc(a['p1'])} & {esc(_ASP_TEX.get(a['simbolo'], a['simbolo']))} & "
            f"{esc(a['p2'])} & {esc(a['aspecto'])} & {a['orbe']:.1f}° \\\\\n"
        )

    if asp_rows.strip():
        tabla_aspectos = (
            "\\begin{center}\n"
            "\\begin{tabular}{lllll}\n"
            "  \\toprule\n"
            "  \\textbf{Punto 1} & \\textbf{Asp.} & \\textbf{Punto 2} "
            "& \\textbf{Aspecto} & \\textbf{Orbe} \\\\\n"
            "  \\midrule\n"
            f"{asp_rows}"
            "  \\bottomrule\n"
            "\\end{tabular}\n"
            "\\end{center}"
        )
    else:
        tabla_aspectos = "\\vspace{0.3cm}\\textit{No hay aspectos en los orbes definidos.}"

    ret_plu = " (retrógrado)" if plu.get("retrogrado") else ""
    ret_qui = " (retrógrado)" if qui.get("retrogrado") else ""

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
\\lhead{{\\textcolor{{grisai}}{{\\small Plutón · Casa 8 · Casa 12 · Quirón · Lilith}}}}
\\cfoot{{\\textcolor{{grisai}}{{\\small\\thepage}}}}
\\renewcommand{{\\headrulewidth}}{{0.3pt}}

\\hypersetup{{colorlinks=true,linkcolor=azulai,urlcolor=azulai}}
\\setstretch{{1.25}}
\\tolerance=1500
\\emergencystretch=4em

\\begin{{document}}

\\begin{{titlepage}}
  \\centering
  \\vspace*{{1.5cm}}
  {{\\Huge\\bfseries\\color{{azulai}} Plutón · Casa 8 · Casa 12}}\\\\[0.35cm]
  {{\\Huge\\bfseries\\color{{azulai}} Quirón · Lilith}}\\\\[0.5cm]
  {{\\large\\color{{grisai}} Arquitectura Interna}}\\\\[0.3cm]
  {{\\small\\itshape\\color{{grisai}} Sombra, herida, intimidad y profundidad psíquica}}\\\\[2cm]
  {{\\huge\\color{{doradoai}} {nom_esc}}}\\\\[1.5cm]
  {{\\Large {fecha_str} \\quad {hora_str}}}\\\\[0.3cm]
  {{\\Large {ciu_esc}}}\\\\[0.3cm]
  {{\\normalsize Lat: {lat:.4f}° \\quad Lon: {lon:.4f}° \\quad {utc_str}}}\\\\[0.3cm]
  {{\\normalsize Ascendente: {esc(asc['signo'])} {grado_a_dms(asc['grado'])} \\quad
    MC: {esc(mc['signo'])} {grado_a_dms(mc['grado'])}}}\\\\[2cm]

  \\begin{{tabular}}{{ll}}
    \\textbf{{Plutón:}}  & {signo_casa(plu)}{ret_plu} \\\\
    \\textbf{{Quirón:}}  & {signo_casa(qui)}{ret_qui} \\\\
    \\textbf{{Lilith:}}  & {signo_casa(lil)} \\\\
    \\textbf{{Casa 8:}}  & {esc(signo_c8)} \\\\
    \\textbf{{Casa 12:}} & {esc(signo_c12)} \\\\
  \\end{{tabular}}\\\\[2cm]

  \\vfill
  {{\\small Generado el {datetime.now().strftime("%d/%m/%Y")}}}
\\end{{titlepage}}

\\tableofcontents
\\newpage

\\section{{Datos de referencia}}

\\begin{{center}}
\\begin{{tabular}}{{llll}}
  \\toprule
  \\textbf{{Punto}} & \\textbf{{Signo}} & \\textbf{{Casa}} & \\textbf{{Posición}} \\\\
  \\midrule
  Plutón{ret_plu} & {esc(plu.get('signo',''))} & {plu.get('casa','')} & {grado_a_dms(plu.get('grado',0))} \\\\
  Quirón{ret_qui} & {esc(qui.get('signo',''))} & {qui.get('casa','')} & {grado_a_dms(qui.get('grado',0))} \\\\
  Lilith          & {esc(lil.get('signo',''))} & {lil.get('casa','')} & {grado_a_dms(lil.get('grado',0))} \\\\
  Casa 8          & {esc(signo_c8)}             & ---                  & --- \\\\
  Casa 12         & {esc(signo_c12)}            & ---                  & --- \\\\
  Ascendente      & {esc(asc['signo'])}         & ---                  & {grado_a_dms(asc['grado'])} \\\\
  Medio Cielo     & {esc(mc['signo'])}          & ---                  & {grado_a_dms(mc['grado'])} \\\\
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

\\section{{Interpretación}}

\\begin{{center}}
{{\\small\\itshape
Este documento no busca definirte. Se acerca a zonas donde pueden aparecer intensidad,\\\\
defensa, herida, vulnerabilidad, deseo, retiro o dificultad para poner en palabras lo que ocurre.
}}
\\end{{center}}

\\vspace{{0.8cm}}

\\Needspace{{10\\baselineskip}}
\\vspace{{0.4cm}}

\\subsection{{1. Marco general}}

{parrafos(t_marco)}

\\Needspace{{10\\baselineskip}}
\\vspace{{0.4cm}}

\\subsection{{2. Plutón — Intensidad, control y transformación}}

\\Needspace{{6\\baselineskip}}
\\subsubsection*{{Plutón en {esc(plu.get('signo',''))} — Casa {plu.get('casa','')}{ret_plu}}}

{parrafos(t_plu)}

\\Needspace{{10\\baselineskip}}
\\vspace{{0.4cm}}

\\subsection{{3. Quirón — Herida, sensibilidad y protección}}

\\Needspace{{6\\baselineskip}}
\\subsubsection*{{Quirón en {esc(qui.get('signo',''))} — Casa {qui.get('casa','')}{ret_qui}}}

{parrafos(t_qui)}

\\Needspace{{10\\baselineskip}}
\\vspace{{0.4cm}}

\\subsection{{4. Lilith — Lo no domesticado}}

\\Needspace{{6\\baselineskip}}
\\subsubsection*{{Lilith en {esc(lil.get('signo',''))} — Casa {lil.get('casa','')}}}

{parrafos(t_lil)}

\\Needspace{{10\\baselineskip}}
\\vspace{{0.4cm}}

\\subsection{{5. Casa 8 — Intimidad, pérdida y vulnerabilidad}}

\\Needspace{{6\\baselineskip}}
\\subsubsection*{{Casa 8 en {esc(signo_c8)}}}

{parrafos(t_c8)}

\\Needspace{{10\\baselineskip}}
\\vspace{{0.4cm}}

\\subsection{{6. Casa 12 — Retiro, sensibilidad y mundo interno}}

\\Needspace{{6\\baselineskip}}
\\subsubsection*{{Casa 12 en {esc(signo_c12)}}}

{parrafos(t_c12)}

\\Needspace{{10\\baselineskip}}
\\vspace{{0.4cm}}

\\subsection{{7. Integración}}

{parrafos(t_integ)}

\\Needspace{{10\\baselineskip}}
\\vspace{{0.4cm}}

\\subsection{{8. Orientación}}

\\Needspace{{6\\baselineskip}}
\\subsubsection*{{Cómo reconocer que esta zona está activa}}
{parrafos(t_or['reconocer'])}

\\Needspace{{6\\baselineskip}}
\\subsubsection*{{Casa 8}}
{parrafos(t_or['casa8'])}

\\Needspace{{6\\baselineskip}}
\\subsubsection*{{Casa 12}}
{parrafos(t_or['casa12'])}

\\Needspace{{6\\baselineskip}}
\\subsubsection*{{Cuando no se reconoce}}
{parrafos(t_or['si_no'])}

\\Needspace{{6\\baselineskip}}
\\subsubsection*{{Una forma más cuidadosa de mirarlo}}
{parrafos(t_or['cuidado'])}

\\vspace{{1cm}}
\\begin{{center}}
{{\\small\\itshape\\color{{grisai}}
La astrología se usa aquí como lenguaje simbólico de observación, no como definición cerrada de la persona.\\
Este documento no sustituye ningún proceso terapéutico ni constituye un diagnóstico.
}}
\\end{{center}}

\\end{{document}}
"""

    return latex


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print("═" * 68)
    print("  PLUTÓN · CASA 8 · CASA 12 · QUIRÓN · LILITH")
    print("═" * 68)
    print()

    nombre = input("Nombre completo: ").strip()

    if not nombre:
        print("El nombre no puede estar vacío.")
        sys.exit(1)

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

    # ── Geocodificación ─────────────────────────────────────────────────────

    try:
        lat, lon = geocodificar(ciudad)
        print(f"  Coordenadas: {lat:.4f}, {lon:.4f}")

    except Exception as e:
        print(f"Error de geocodificación: {e}")
        sys.exit(1)

    # ── Zona horaria ───────────────────────────────────────────────────────

    try:
        tz_name = obtener_timezone(lat, lon)
        print(f"  Zona horaria: {tz_name}")

    except Exception as e:
        print(f"Error de zona horaria: {e}")
        sys.exit(1)

    # ── Carta ──────────────────────────────────────────────────────────────

    try:
        carta = calcular_carta(
            anio, mes, dia,
            hora, minuto,
            lat, lon,
            tz_name
        )

        planetas = carta["planetas"]
        cuspides = carta["cuspides"]

        asc = carta["asc"]

        plu = planetas.get("Plutón", {})
        qui = planetas.get("Quirón", {})
        lil = planetas.get("Lilith", {})

        signo_c8 = signo_cuspide_casa(cuspides, 8)
        signo_c12 = signo_cuspide_casa(cuspides, 12)

        print(f"  ASC:      {asc['signo']} {grado_a_dms(asc['grado'])}")

        print(
            f"  Plutón:   {plu.get('signo','')} "
            f"{grado_a_dms(plu.get('grado',0))} "
            f"— Casa {plu.get('casa','')}"
        )

        print(
            f"  Quirón:   {qui.get('signo','')} "
            f"{grado_a_dms(qui.get('grado',0))} "
            f"— Casa {qui.get('casa','')}"
        )

        print(
            f"  Lilith:   {lil.get('signo','')} "
            f"{grado_a_dms(lil.get('grado',0))} "
            f"— Casa {lil.get('casa','')}"
        )

        print(f"  Casa 8:   {signo_c8}")
        print(f"  Casa 12:  {signo_c12}")

    except Exception as e:
        print(f"Error en cálculo astrológico: {e}")
        sys.exit(1)

    # ── Aspectos ───────────────────────────────────────────────────────────

    aspectos = calcular_aspectos_sombra(carta["planetas"])

    print(f"  Aspectos calculados: {len(aspectos)}")

    # ── Rutas ──────────────────────────────────────────────────────────────

    nombre_f = nombre.replace(" ", "_").replace("/", "-")

    ruta_base = os.path.join(
        BASE_DIR,
        nombre_f + "_Sombra_Profunda"
    )

    ruta_tex = ruta_base + ".tex"
    ruta_pdf = ruta_base + ".pdf"

    ruta_rueda = os.path.join(
        BASE_DIR,
        nombre_f + "_rueda.png"
    )

    # ── Rueda ──────────────────────────────────────────────────────────────

    dibujar_rueda(carta, nombre, ruta_rueda)

    # ── Generación LaTeX ──────────────────────────────────────────────────

    print("  Generando interpretación...")

    latex = generar_latex(
        carta,
        nombre,
        anio,
        mes,
        dia,
        hora,
        minuto,
        ciudad,
        lat,
        lon,
        tz_name,
        ruta_rueda,
        aspectos
    )

    with open(ruta_tex, "w", encoding="utf-8") as f:
        f.write(latex)

    print(f"  LaTeX guardado: {ruta_tex}")

    # ── PDF ────────────────────────────────────────────────────────────────

    print("  Compilando PDF...")

    try:
        for _ in range(2):
            subprocess.run(
                [
                    "pdflatex",
                    "-interaction=nonstopmode",
                    os.path.basename(ruta_tex)
                ],
                capture_output=True,
                timeout=180,
                cwd=BASE_DIR
            )

        if os.path.exists(ruta_pdf):
            print()
            print("  PDF generado correctamente:")
            print(f"  {ruta_pdf}")

        else:
            print("  PDF no generado. Revisa el archivo .tex.")

    except FileNotFoundError:
        print("  pdflatex no encontrado. El .tex está listo.")

    except Exception as e:
        print(f"  Error al compilar: {e}")

    print()
    print("Proceso completado.")


if __name__ == "__main__":
    main()