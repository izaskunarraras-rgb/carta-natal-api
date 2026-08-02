#!/usr/bin/env python3
"""
7. Casas por Signo — Arquitectura Interna

Explora cómo se organiza cada una de las áreas de tu vida a través
del signo que ocupa la cúspide de cada casa.

Cada casa muestra un ámbito distinto de experiencia —los vínculos,
el trabajo, la creatividad, el hogar, los recursos o el mundo interior—,
mientras que el signo describe la actitud, las necesidades y la manera
en que tiendes a vivir ese territorio.

El módulo también analiza los ejes principales de la carta, la
arquitectura general de las casas y la presencia de signos
interceptados, integrando toda esta información para mostrar cómo se articula la estructura interna de tu carta.
"""

import math
import os
import subprocess
import sys
from datetime import datetime

import traceback

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pytz
import swisseph as swe
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from collections import Counter

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from matplotlib import font_manager

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

try:
    from estilos_pdf import crear_estilos_pdf
except ImportError:
    crear_estilos_pdf = None


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def registrar_fuente_simbolos():
    try:
        ruta_fuente = font_manager.findfont(
            "DejaVu Sans"
        )

        pdfmetrics.registerFont(
            TTFont(
                "DejaVuSansAstro",
                ruta_fuente,
            )
        )

        return "DejaVuSansAstro"

    except Exception as error:
        print(
            "No se pudo registrar la fuente de símbolos:",
            error,
        )

        return "Helvetica"


FUENTE_SIMBOLOS = registrar_fuente_simbolos()



# ─── CONSTANTES ────────────────────────────────────────────────────────────────

SIGNOS = ["Aries","Tauro","Géminis","Cáncer","Leo","Virgo",
          "Libra","Escorpio","Sagitario","Capricornio","Acuario","Piscis"]


PLANETAS_IDS = [
    (swe.SUN,    "Sol",       "☉"),
    (swe.MOON,   "Luna",      "☽"),
    (swe.MERCURY,"Mercurio",  "☿"),
    (swe.VENUS,  "Venus",     "♀"),
    (swe.MARS,   "Marte",     "♂"),
    (swe.JUPITER,"Júpiter",   "♃"),
    (swe.SATURN, "Saturno",   "♄"),
    (swe.URANUS, "Urano",     "♅"),
    (swe.NEPTUNE,"Neptuno",   "♆"),
    (swe.PLUTO,  "Plutón",    "♇"),
]

CHIRON_ID = swe.CHIRON
LILITH_ID = swe.MEAN_APOG


SIMBOLOS_SIGNOS = ["♈","♉","♊","♋","♌","♍","♎","♏","♐","♑","♒","♓"]

COLORES_ELEMENTO = {
    "Fuego":"#CC2200",
    "Tierra":"#2E7D32",
    "Aire":"#E67E00",
    "Agua":"#1A5FA8"
}

COLORES_PLANETA = {
    "Sol":"#CC2200","Marte":"#CC2200","Júpiter":"#CC2200",
    "Venus":"#2E7D32","Saturno":"#2E7D32",
    "Mercurio":"#E67E00","Urano":"#E67E00",
    "Luna":"#1A5FA8","Neptuno":"#1A5FA8","Plutón":"#1A5FA8",
    "Quirón":"#7B2D8B","Lilith":"#7B2D8B",
    "Nodo Norte":"#888800","Nodo Sur":"#888800",
}

REGENTE_SIGNO = {
    "Aries": "Marte",
    "Tauro": "Venus",
    "Géminis": "Mercurio",
    "Cáncer": "Luna",
    "Leo": "Sol",
    "Virgo": "Mercurio",
    "Libra": "Venus",
    "Escorpio": "Plutón",
    "Sagitario": "Júpiter",
    "Capricornio": "Saturno",
    "Acuario": "Urano",
    "Piscis": "Neptuno",
}

SIMBOLO_PLANETA = {
    "Sol": "☉",
    "Luna": "☽",
    "Mercurio": "☿",
    "Venus": "♀",
    "Marte": "♂",
    "Júpiter": "♃",
    "Saturno": "♄",
    "Urano": "♅",
    "Neptuno": "♆",
    "Plutón": "♇",
}

ELEMENTO_SIGNO = {
    "Aries": "Fuego",
    "Tauro": "Tierra",
    "Géminis": "Aire",
    "Cáncer": "Agua",
    "Leo": "Fuego",
    "Virgo": "Tierra",
    "Libra": "Aire",
    "Escorpio": "Agua",
    "Sagitario": "Fuego",
    "Capricornio": "Tierra",
    "Acuario": "Aire",
    "Piscis": "Agua",
}

MODALIDAD_SIGNO = {
    "Aries": "Cardinal",
    "Tauro": "Fija",
    "Géminis": "Mutable",
    "Cáncer": "Cardinal",
    "Leo": "Fija",
    "Virgo": "Mutable",
    "Libra": "Cardinal",
    "Escorpio": "Fija",
    "Sagitario": "Mutable",
    "Capricornio": "Cardinal",
    "Acuario": "Fija",
    "Piscis": "Mutable",
}

# ───────────────────────────── CASAS ─────────────────────────────

CASA_LABEL = {
    1:  "Identidad y presencia",
    2:  "Recursos y valor",
    3:  "Comunicación y aprendizaje",
    4:  "Raíces y sostén",
    5:  "Creatividad y expresión",
    6:  "Hábitos y bienestar",
    7:  "Vínculos y relaciones",
    8:  "Transformación y profundidad",
    9:  "Sentido y expansión",
    10: "Vocación y proyección",
    11: "Comunidad y proyectos",
    12: "Interioridad e integración",
}


CASA_AREA = {

    1: (
        "La Casa 1 representa la identidad que desarrollas al relacionarte con el mundo. "
        "Describe la forma en que afirmas tu presencia, inicias nuevas experiencias y "
        "respondes de manera espontánea a lo que la vida te propone. Es el punto de partida "
        "desde el que comienzas a construir tu relación con el entorno."
    ),

    2: (
        "Construir una sensación de estabilidad es la función principal de la Casa 2. "
        "Aquí se refleja la relación con tus recursos, con el valor que reconoces en ti "
        "y con todo aquello que contribuye a generar seguridad, tanto en el plano material "
        "como en el interno."
    ),

    3: (
        "Comprender el mundo comienza por la experiencia más cercana. La Casa 3 muestra "
        "cómo aprendes, comunicas y organizas tus ideas, así como la manera en que te "
        "relacionas con el entorno cotidiano y das sentido a lo que sucede a tu alrededor."
    ),

    4: (
        "Toda persona necesita un lugar interno desde el que sentirse sostenida. La Casa 4 "
        "representa ese espacio de intimidad, raíces y pertenencia donde encuentras refugio, "
        "recuperas fuerzas y construyes la base emocional sobre la que se apoya el resto de "
        "tu experiencia."
    ),

    5: (
        "Expresarte de forma auténtica es el territorio de la Casa 5. Aquí se desarrollan "
        "la creatividad, el disfrute y la capacidad de compartir aquello que nace de manera "
        "genuina en ti, permitiéndote experimentar la alegría de crear y mostrarte tal como eres."
    ),

    6: (
        "La vida cotidiana se convierte en un espacio de crecimiento a través de la Casa 6. "
        "Describe cómo organizas tus hábitos, cuidas tu bienestar y desarrollas aquellas "
        "rutinas que aportan equilibrio, continuidad y eficacia a tu día a día."
    ),

    7: (
        "El encuentro con los demás ocupa el centro de la Casa 7. A través de las relaciones, "
        "las asociaciones y los compromisos, descubres nuevas formas de comprenderte, "
        "aprendiendo a construir vínculos donde existe reciprocidad y reconocimiento mutuo."
    ),

    8: (
        "Hay experiencias que invitan a transformarte profundamente, y ese es el territorio "
        "de la Casa 8. Aquí aparecen los procesos de cambio, la confianza, los recursos "
        "compartidos y la capacidad de atravesar etapas que modifican tu manera de vivir "
        "y de comprender la realidad."
    ),

    9: (
        "Ampliar la mirada y encontrar un sentido más profundo a la vida es la función "
        "de la Casa 9. Refleja el deseo de aprender, explorar nuevas perspectivas y desarrollar "
        "una comprensión cada vez más amplia de la vida y de tu propio recorrido."
    ),

    10: (
        "La Casa 10 señala la dirección hacia la que orientas tu energía. Habla de la "
        "vocación, de la responsabilidad y de la manera en que deseas aportar algo valioso "
        "al mundo, construyendo una trayectoria coherente con aquello que aspiras a llegar a ser."
    ),

    11: (
        "Ningún camino se construye completamente en solitario. La Casa 11 representa la "
        "relación con la comunidad, los proyectos compartidos y las personas con quienes "
        "imaginas el futuro, mostrando cómo contribuyes al desarrollo de algo que trasciende "
        "el ámbito exclusivamente personal."
    ),

    12: (
        "La Casa 12 invita a dirigir la atención hacia el mundo interior. Es el espacio de "
        "la introspección, del silencio y de la integración, donde determinadas experiencias "
        "necesitan tiempo, descanso y consciencia para revelar su significado e incorporarse de manera profunda a tu proceso de crecimiento."
    ),

}


# ───────────────────────── SIGNO EN CÚSPIDE ─────────────────────────
# La cualidad que el signo aporta al área de experiencia representada
# por la casa cuya cúspide ocupa.

SIGNO_EN_CUSPIDE = {

"Aries": (
    "Cuando Aries ocupa la cúspide de una casa, ese ámbito de tu vida suele "
    "vivirse con iniciativa, impulso y necesidad de actuar. Existe una tendencia a "
    "ponerse en marcha antes de tener todas las respuestas, confiando en que será la "
    "propia experiencia la que vaya mostrando el camino.\n\n"

    "La espontaneidad favorece que este ámbito permanezca vivo y en constante movimiento, "
    "aunque también puede aparecer cierta impaciencia cuando los procesos requieren más "
    "tiempo del deseado. El aprendizaje consiste en conservar la iniciativa sin perder "
    "la capacidad de sostener lo que realmente merece desarrollarse."
),

"Tauro": (
    "Cuando Tauro ocupa la cúspide de una casa, esa área de la vida busca estabilidad, "
    "continuidad y una base sólida sobre la que crecer. Antes de avanzar suele ser "
    "importante sentir confianza en el proceso y comprobar que existen condiciones "
    "suficientemente seguras.\n\n"

    "La constancia permite construir resultados duraderos, aunque el apego a lo conocido "
    "puede hacer más difíciles los cambios cuando dejan de aportar crecimiento. El reto "
    "es encontrar estabilidad sin convertirla en inmovilidad."
),

"Géminis": (
    "Cuando Géminis ocupa la cúspide de una casa, la curiosidad se convierte en el motor "
    "principal de ese ámbito. Existe una necesidad natural de comprender, intercambiar "
    "ideas y explorar distintas posibilidades antes de fijar una dirección definitiva.\n\n"

    "La flexibilidad facilita adaptarse a situaciones cambiantes y descubrir nuevas "
    "posibilidades, aunque la abundancia de intereses puede dispersar la atención. El "
    "aprendizaje consiste en combinar apertura mental con capacidad de profundizar."
),

"Cáncer": (
    "Cuando Cáncer ocupa la cúspide de una casa, la vivencia de ese territorio adquiere "
    "un fuerte componente emocional. Antes de abrirse plenamente suele aparecer la "
    "necesidad de sentir confianza, protección y un entorno que permita mostrarse con "
    "autenticidad.\n\n"

    "La sensibilidad favorece una conexión profunda con lo que realmente importa, aunque "
    "también puede llevar a protegerse en exceso frente a experiencias que despiertan "
    "vulnerabilidad. El crecimiento pasa por cuidar sin dejar que el miedo limite tu "
    "capacidad para expresarte."
),

"Leo": (
    "Cuando Leo ocupa la cúspide de una casa, esa parte de la vida necesita convertirse "
    "en un espacio donde expresar la propia identidad. Existe el deseo de aportar algo "
    "personal, creativo y reconocible, sintiendo que la forma de vivir ese ámbito refleja quién eres.\n\n"

    "La confianza inspira y moviliza, pero puede verse condicionada cuando el reconocimiento "
    "externo se convierte en la única medida del propio valor. El aprendizaje consiste en "
    "expresarte desde la autenticidad, independientemente de la respuesta que recibas."
),

"Virgo": (
    "Cuando Virgo ocupa la cúspide de una casa, la atención se dirige de manera natural "
    "hacia los detalles, el orden y la mejora continua. Existe una disposición constante "
    "a observar qué puede ajustarse para que ese ámbito de la vida resulte más funcional y "
    "coherente.\n\n"

    "La capacidad de análisis aporta precisión y eficacia, aunque también puede generar "
    "una exigencia excesiva cuando todo parece susceptible de perfeccionarse. El reto "
    "consiste en valorar el progreso sin esperar una perfección imposible."
),

"Libra": (
    "Cuando Libra ocupa la cúspide de una casa, el desarrollo de esa experiencia suele "
    "producirse a través del encuentro con otras personas. El diálogo, la cooperación y "
    "la búsqueda de equilibrio se convierten en recursos fundamentales para avanzar.\n\n"

    "La capacidad de comprender distintos puntos de vista favorece relaciones armoniosas, "
    "aunque el deseo de evitar el conflicto puede dificultar algunas decisiones. El "
    "aprendizaje consiste en mantener el equilibrio sin perder el propio centro."
),

"Escorpio": (
    "Cuando Escorpio ocupa la cúspide de una casa, ese ámbito se vive con intensidad y "
    "profundidad. Las experiencias importantes rara vez pasan desapercibidas, ya que "
    "suelen despertar procesos internos de transformación y cambio.\n\n"

    "La capacidad para implicarte plenamente permite desarrollar una gran fortaleza "
    "interior, aunque también puede aparecer resistencia a soltar aquello que ya ha "
    "cumplido su función. El crecimiento llega cuando la transforamción deja de percibirse "
    "como una pérdida y comienza a entenderse como una evolución."
),

"Sagitario": (
    "Cuando Sagitario ocupa la cúspide de una casa, ese territorio necesita expansión, "
    "sentido y posibilidades de crecimiento. La vida adquiere mayor vitalidad "
    "cuando abre nuevas perspectivas y permite descubrir horizontes más amplios.\n\n"

    "El entusiasmo impulsa a avanzar con confianza, aunque a veces puede resultar más "
    "atractivo iniciar nuevos caminos que consolidar los ya emprendidos. El aprendizaje "
    "consiste en mantener la amplitud de visión sin perder el compromiso con el proceso."
),

"Capricornio": (
    "Cuando Capricornio ocupa la cúspide de una casa, el desarrollo de ese ámbito suele "
    "construirse de manera gradual, responsable y sostenida. Existe una tendencia a pensar "
    "en el largo plazo, valorando el esfuerzo como parte natural del crecimiento.\n\n"

    "La disciplina permite alcanzar objetivos sólidos, aunque también puede aparecer la "
    "sensación de cargar con más responsabilidades de las necesarias. El reto consiste en "
    "construir con constancia sin convertir la exigencia en una carga permanente."
),

"Acuario": (
    "Cuando Acuario ocupa la cúspide de una casa, esa parte de la vida necesita libertad "
    "para desarrollarse de una manera propia. Existe una inclinación natural a cuestionar "
    "lo establecido y buscar formas diferentes de comprender y vivir ese ámbito de la vida.\n\n"

    "La originalidad favorece soluciones innovadoras y una mirada amplia, aunque en "
    "ocasiones puede crear cierta distancia respecto a las necesidades emocionales más "
    "inmediatas. El aprendizaje consiste en integrar independencia y cercanía."
),

"Piscis": (
    "Cuando Piscis ocupa la cúspide de una casa, ese territorio se vive con sensibilidad, "
    "intuición y una gran capacidad para percibir matices que no siempre resultan evidentes. "
    "La manera de vivir ese ámbito suele desarrollarse de forma flexible, adaptándose a lo que cada "
    "situación necesita.\n\n"

    "La empatía y la imaginación enriquecen profundamente este ámbito, aunque también "
    "puede costar establecer límites claros cuando las circunstancias o las emociones se "
    "mezclan. El crecimiento consiste en conservar la apertura sin perder claridad ni "
    "dirección."
),

}



# ─── TEXTOS: CASAS ─────────────────────────────────────────────
CASA_1 = {

"Aries": (
    "La identidad necesita aquí expresarse con libertad y movimiento. Existe una tendencia "
    "natural a responder de forma inmediata ante lo que ocurre, como si la vida "
    "cobrara sentido únicamente cuando puede vivirse en primera persona. Antes que observar "
    "desde la distancia, prefieres implicarte, probar, descubrir y aprender mientras avanzas. "
    "La iniciativa suele aparecer de forma espontánea y, con frecuencia, eres tú quien abre "
    "el camino cuando una situación permanece bloqueada o nadie se decide a dar el primer paso.\n\n"

    "Esta posición favorece una presencia directa y difícil de pasar por alto. Tiendes a "
    "mostrarte tal como eres, sin invertir demasiada energía en construir una imagen que "
    "agrade a todo el mundo. Hay autenticidad en esa forma de presentarte, aunque a veces "
    "también cierta impaciencia cuando el entorno responde con un ritmo distinto al tuyo. "
    "Esperar, dudar o permanecer demasiado tiempo en una misma situación puede resultarte "
    "más exigente que afrontar un desafío completamente nuevo.\n\n"

    "A menudo descubres quién eres precisamente a través de la acción. Cada experiencia "
    "te ayuda a descubrir quién eres y contribuye a fortalecer tu identidad. Por eso "
    "es posible que necesites iniciar proyectos, explorar caminos o aceptar retos que otras "
    "personas evitarían. No se trata únicamente de buscar novedad, sino de sentir que avanzas, "
    "creces y desarrollas tu capacidad para responder a la vida con autonomía.\n\n"

    "La fortaleza de esta combinación reside en el coraje para comenzar. Allí donde otras "
    "personas esperan condiciones perfectas, tú puedes confiar en que el aprendizaje llegará durante "
    "el recorrido. Esa disposición convierte los cambios en oportunidades y favorece una "
    "gran capacidad para recuperarte después de los errores, sin permitir que estos condicionen "
    "durante demasiado tiempo tus siguientes pasos. La iniciativa, la sinceridad y la determinación "
    "suelen convertirse en cualidades que inspiran a quienes te rodean.\n\n"

    "Sin embargo, cuando esta energía pierde equilibrio, la necesidad de afirmar la propia "
    "identidad puede transformarse en impulsividad o en una reacción constante frente a todo "
    "lo que parece limitar tu libertad. Puede surgir la sensación de que detenerte equivale "
    "a retroceder, o de que pedir ayuda compromete tu independencia. En esos momentos existe "
    "el riesgo de iniciar más procesos de los que realmente puedes sostener o de abandonar "
    "aquello que todavía necesita tiempo para desarrollarse.\n\n"

    "Con el paso de los años, esta posición suele invitar a descubrir que la verdadera fuerza "
    "no consiste únicamente en abrir caminos, sino también en permanecer cuando algo merece "
    "ser construido. La iniciativa alcanza entonces una nueva dimensión: deja de ser solo el "
    "impulso de empezar y se convierte en la capacidad de sostener una dirección elegida con "
    "consciencia. Cuando integras ambas cualidades, tu presencia transmite confianza, valentía "
    "y una profunda capacidad para inspirar movimiento sin perder el contacto contigo."
),


"Tauro": (
    "Cuando Tauro ocupa la cúspide de la Casa 1, la identidad suele construirse de forma "
    "gradual y estable. Antes de dar un paso importante necesitas sentir que existe una "
    "base firme sobre la que apoyarte, por lo que rara vez actúas únicamente por impulso. "
    "Tu presencia transmite serenidad, constancia y una sensación de solidez que inspira "
    "confianza en quienes te rodean. Prefieres avanzar a tu propio ritmo antes que dejarte "
    "arrastrar por las prisas o por expectativas ajenas.\n\n"

    "La relación contigo se fortalece con el tiempo y a través de lo que vas viviendo. No sueles "
    "sentir la necesidad de demostrar quién eres constantemente; te resulta más natural que "
    "sean tus actos, tu coherencia y tu capacidad para mantener el rumbo quienes hablen por "
    "ti. Con frecuencia desarrollas una identidad profundamente vinculada a aquello que "
    "consideras valioso, buscando construir una vida que refleje tus principios y te aporte "
    "seguridad tanto emocional como material.\n\n"

    "Existe una especial capacidad para perseverar allí donde otras personas abandonan. La paciencia, "
    "la constancia y el compromiso permiten que muchos de tus logros nazcan de procesos "
    "lentos pero sólidos. Cuando decides implicarte en algo, sueles hacerlo con la intención "
    "de desarrollarlo en profundidad, dedicándole el tiempo necesario para que pueda crecer "
    "de manera natural y estable.\n\n"

    "Esta posición también favorece una relación muy consciente con el cuerpo y con los "
    "sentidos. A menudo necesitas experimentar la realidad de forma tangible, disfrutando "
    "de aquello que aporta calma, belleza o bienestar. La identidad encuentra aquí una vía "
    "de expresión a través de la presencia física, del contacto con la naturaleza, de los "
    "ritmos pausados y de todo aquello que permite sentir que la vida puede disfrutarse sin "
    "necesidad de vivir permanentemente con prisas.\n\n"

    "Sin embargo, esa búsqueda de estabilidad puede convertirse en resistencia cuando los "
    "cambios llegan sin haber sido elegidos. Puede costar abandonar situaciones conocidas, "
    "incluso cuando han dejado de favorecer tu crecimiento, simplemente porque ofrecen una "
    "sensación de seguridad. En determinados momentos también puede aparecer cierta rigidez "
    "o dificultad para modificar opiniones, ritmos o formas de actuar que durante mucho "
    "tiempo han funcionado.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera estabilidad "
    "no depende únicamente de conservar lo conocido, sino también de desarrollar la confianza "
    "necesaria para adaptarte cuando la vida cambia. La identidad madura cuando comprende que "
    "la firmeza y la flexibilidad no son cualidades opuestas, sino complementarias. Entonces "
    "tu presencia transmite una sensación de calma, coherencia y fortaleza que permite a "
    "otros encontrar un punto de apoyo sin que tú tengas que renunciar a seguir evolucionando."
),


"Géminis": (
    "Cuando Géminis ocupa la cúspide de la Casa 1, la identidad se desarrolla a través de la "
    "curiosidad y del intercambio constante con el entorno. Comprender, preguntar, observar "
    "y descubrir nuevas perspectivas forma parte de la manera en que construyes tu relación con el mundo. "
    "Más que aferrarte a una única definición de quién eres, necesitas sentir "
    "que puedes evolucionar, aprender y ampliar continuamente tu forma de mirar la realidad.\n\n"

    "Tu presencia suele percibirse cercana, dinámica y abierta. Existe facilidad para iniciar "
    "conversaciones, conectar con personas muy diferentes y adaptarte a contextos cambiantes. "
    "La palabra se convierte en una herramienta natural para explorar el mundo y también para "
    "comprender lo que ocurre dentro de ti. Muchas veces descubres lo que piensas precisamente "
    "mientras lo expresas.\n\n"

    "La identidad encuentra aquí una vía de crecimiento a través de la diversidad de "
    "experiencias. Aprender disciplinas distintas, cambiar de intereses o explorar caminos "
    "que parecen poco relacionados entre sí no responde necesariamente a una falta de "
    "constancia, sino a una necesidad genuina de ampliar horizontes y reunir nuevas piezas "
    "que enriquezcan tu comprensión de la vida.\n\n"

    "Esta combinación favorece una gran capacidad para adaptarte a situaciones nuevas. "
    "Sueles encontrar soluciones creativas, comprender rápidamente el funcionamiento de los "
    "entornos y establecer puentes entre ideas aparentemente desconectadas. Tu flexibilidad "
    "intelectual permite responder con agilidad allí donde otras personas pueden quedarse "
    "bloqueadas por la rigidez.\n\n"

    "Sin embargo, la facilidad para abrir múltiples caminos puede dificultar la permanencia "
    "cuando una experiencia exige profundidad, repetición o silencio. En algunos momentos "
    "puede surgir la sensación de que siempre existe una posibilidad más interesante que la "
    "actual, generando dispersión o cierta dificultad para consolidar una dirección propia. "
    "También puede aparecer la tendencia a explicar las emociones antes que permitirte "
    "sentirlas plenamente.\n\n"

    "La madurez de esta posición llega cuando descubres que la libertad de aprender no está "
    "reñida con la capacidad de comprometerte. Tu identidad se fortalece al integrar la "
    "curiosidad con la profundidad, permitiéndote conservar la apertura mental sin perder el "
    "contacto con aquello que realmente da sentido a tu camino. Entonces tu presencia inspira "
    "diálogo, creatividad y una extraordinaria capacidad para conectar mundos diferentes."
),


"Cáncer": (
    "Cuando Cáncer ocupa la cúspide de la Casa 1, la identidad se construye a través de la "
    "sensibilidad y de la necesidad de sentir una conexión auténtica con lo que vives. "
    "Tu forma de presentarte al mundo no nace únicamente de una decisión consciente, sino "
    "también de aquello que percibes, intuyes y experimentas emocionalmente. Antes de abrirte "
    "por completo, suele ser importante comprobar que existe un entorno donde puedas sentir "
    "seguridad y aceptación tal como eres.\n\n"

    "La presencia transmite cercanía, calidez y una disposición natural al cuidado. Las "
    "personas suelen percibir en ti una capacidad para acoger, escuchar o generar confianza, "
    "aunque esa misma sensibilidad hace que también registres con facilidad los cambios de "
    "ambiente, las emociones ajenas o las dinámicas invisibles que otras personas pasan por "
    "alto. Tu manera de relacionarte con el mundo está profundamente vinculada a lo que "
    "sientes, incluso cuando no siempre lo expresas con palabras.\n\n"

    "La identidad evoluciona aquí a través de la experiencia emocional. Cada vínculo, cada "
    "cambio y cada etapa importante dejan una huella que contribuye a definir quién eres. "
    "Existe una memoria interna muy viva que te permite aprender del pasado y desarrollar una "
    "gran capacidad para comprender las necesidades propias y ajenas desde la empatía más que "
    "desde el juicio.\n\n"

    "Esta posición favorece una intuición especialmente desarrollada. Muchas decisiones "
    "importantes nacen de una percepción difícil de explicar racionalmente, pero que suele "
    "orientarte con bastante precisión. Cuando confías en esa sensibilidad sin dejarte "
    "arrastrar por ella, desarrollas una forma de estar en el mundo profundamente humana y "
    "capaz de generar vínculos muy auténticos.\n\n"

    "Sin embargo, la necesidad de protegerte puede hacer que en determinados momentos levantes "
    "barreras antes incluso de comprobar si realmente son necesarias. El miedo a que puedan "
    "hacerte daño puede favorecer actitudes defensivas, cambios de humor o cierta tendencia a "
    "refugiarte en lo conocido cuando las circunstancias despiertan inseguridad. También puede "
    "costar diferenciar entre lo que verdaderamente sientes y aquello que absorbes del entorno.\n\n"

    "Con el tiempo, esta posición invita a descubrir que la sensibilidad no necesita esconderse "
    "para convertirse en una fortaleza. La identidad madura cuando comprendes que abrirte al "
    "mundo no significa perder protección, sino aprender a sostenerte desde dentro. Entonces "
    "tu presencia transmite una mezcla muy valiosa de ternura, profundidad y fortaleza serena, "
    "capaz de ofrecer refugio sin dejar de avanzar en tu propio camino."
),


"Leo": (
    "Cuando Leo ocupa la cúspide de la Casa 1, la identidad necesita expresarse de una manera "
    "visible, auténtica y creativa. Existe un impulso natural a mostrar quién eres sin "
    "esconder aquello que te hace diferente, buscando desarrollar una presencia que refleje "
    "con fidelidad tu individualidad. No se trata únicamente de destacar, sino de sentir que "
    "la vida te permite manifestar plenamente tu esencia.\n\n"

    "Tu forma de relacionarte con el mundo suele transmitir vitalidad, entusiasmo y confianza. "
    "Hay una inclinación espontánea a asumir un papel activo, inspirar a otras personas o "
    "convertirte en un referente cuando una situación necesita dirección. La identidad crece "
    "cuando tienes espacio para crear, liderar o aportar algo que lleve tu sello personal.\n\n"

    "Esta posición favorece una conexión muy estrecha con la autoestima y con el reconocimiento "
    "del propio valor. Necesitas sentir que aquello que haces tiene significado y que puedes "
    "expresarte sin renunciar a tu autenticidad. Cuando existe esa coherencia entre lo que eres "
    "y lo que muestras, aparece una fuerza interior que moviliza tanto tu desarrollo como el de "
    "quienes te rodean.\n\n"

    "La creatividad no siempre se manifiesta a través del arte o de la expresión escénica. En "
    "muchos casos aparece como la capacidad de aportar una visión personal, encontrar soluciones "
    "originales o contagiar entusiasmo allí donde otras personas solo perciben dificultades. Tu manera "
    "de ocupar el espacio suele animar a los demás a confiar también en sus propios talentos.\n\n"

    "El desafío aparece cuando el reconocimiento externo comienza a ocupar el lugar de la propia "
    "valoración. Puede surgir entonces una necesidad excesiva de aprobación o el temor a no estar "
    "a la altura de la imagen que deseas proyectar. Paradójicamente, cuanto más intentas demostrar "
    "tu valor, más fácil resulta perder el contacto con él.\n\n"

    "La madurez llega cuando descubres que la verdadera autoridad nace de la autenticidad y no "
    "de la admiración ajena. Cuando expresas quién eres sin necesidad de competir ni de demostrar "
    "constantemente tu importancia, tu presencia adquiere una fuerza tranquila que inspira, "
    "motiva y ayuda a que otras personas también se atrevan a ocupar su propio lugar."
),


"Virgo": (
    "Cuando Virgo ocupa la cúspide de la Casa 1, la identidad se desarrolla a través de la "
    "observación, el aprendizaje continuo y el deseo de mejorar aquello que haces. Existe una "
    "tendencia natural a mirar la realidad con atención, identificando pequeños matices que "
    "otras personas pasan por alto y buscando comprender cómo pueden hacerse las cosas de una "
    "forma más consciente, eficiente o coherente. Tu presencia suele transmitir discreción, "
    "serenidad y una actitud práctica ante la vida.\n\n"

    "No acostumbras a construir tu identidad desde la necesidad de llamar la atención, sino "
    "desde la satisfacción de sentir que aquello que haces tiene utilidad y está bien realizado. "
    "Con frecuencia prefieres que sean los hechos quienes hablen por ti antes que las palabras. "
    "Existe una inclinación natural a responsabilizarte de lo que está en tus manos, aportando "
    "orden allí donde hay confusión y encontrando soluciones concretas a problemas cotidianos.\n\n"

    "La relación contigo se fortalece a través del aprendizaje. Cada experiencia "
    "se convierte en una oportunidad para conocerte mejor, desarrollar nuevas habilidades y "
    "refinar tu manera de actuar. La identidad no se vive como algo fijo, sino como un proceso "
    "que puede perfeccionarse poco a poco mediante la práctica, la reflexión y la experiencia.\n\n"

    "Esta posición favorece una gran capacidad de análisis y discernimiento. Sueles detectar "
    "rápidamente aquello que necesita atención, comprender el funcionamiento de los procesos y "
    "organizar la realidad con sentido práctico. Esa mirada cuidadosa puede convertirte en una "
    "persona muy fiable, capaz de sostener responsabilidades con constancia y dedicación.\n\n"

    "Sin embargo, el deseo de mejorar puede transformarse en una exigencia difícil de satisfacer. "
    "Es posible que dediques más energía a señalar aquello que falta que a reconocer lo que ya "
    "has conseguido. En algunos momentos también puede aparecer el miedo a equivocarte o la "
    "sensación de que todavía te falta preparación antes de dar un paso importante. "
    "Cuando la autocrítica ocupa demasiado espacio, la espontaneidad termina debilitándose.\n\n"

    "Con el tiempo, esta posición invita a descubrir que crecer no significa alcanzar la "
    "perfección, sino aprender a valorar el propio recorrido. La identidad madura cuando "
    "comprendes que el error también forma parte del aprendizaje y que tu valor no depende de "
    "hacerlo todo impecablemente. Entonces tu presencia transmite humildad, competencia y una "
    "capacidad muy valiosa para mejorar la realidad sin perder la cercanía contigo."
),


"Libra": (
    "Cuando Libra ocupa la cúspide de la Casa 1, la identidad se construye a través del diálogo constante "
    "con los demás. El encuentro con otras personas no solo enriquece tu experiencia, sino que "
    "también te ayuda a descubrir aspectos de ti que difícilmente aparecerían en soledad. "
    "Tu forma de presentarte al mundo suele transmitir cordialidad, apertura y una disposición "
    "natural para crear puentes entre puntos de vista diferentes.\n\n"

    "Existe una sensibilidad especial hacia el equilibrio en las relaciones. Tiendes a percibir "
    "con facilidad cómo afectan tus acciones al entorno y buscas generar espacios donde el "
    "respeto, la cooperación y el entendimiento sean posibles. Más que imponerte, prefieres "
    "construir acuerdos y encontrar soluciones que tengan en cuenta las distintas necesidades "
    "implicadas.\n\n"

    "La identidad evoluciona aquí a través del intercambio. Cada conversación, cada vínculo y "
    "cada diferencia de opinión representan una oportunidad para ampliar tu mirada y comprender "
    "la realidad desde perspectivas distintas. Esa capacidad favorece una personalidad flexible, "
    "capaz de integrar matices sin necesidad de reducirlo todo a una única verdad.\n\n"

    "Esta posición suele aportar diplomacia, sensibilidad estética y una gran habilidad para "
    "generar armonía en los entornos que habitas. Sabes reconocer el valor de la cooperación y "
    "comprendes que muchas veces el crecimiento no depende de competir, sino de aprender a crear "
    "relaciones donde todas las personas puedan desarrollarse.\n\n"

    "El desafío aparece cuando el deseo de mantener el equilibrio lleva a posponer decisiones "
    "importantes o a adaptar en exceso tu comportamiento para evitar conflictos. En algunos "
    "momentos puede resultar difícil distinguir entre el auténtico acuerdo y la renuncia a tus "
    "propias necesidades. Buscar la armonía deja de ser saludable cuando implica perder el "
    "contacto con tu propio criterio.\n\n"

    "Con el paso del tiempo, esta posición invita a descubrir que una relación verdaderamente "
    "equilibrada solo es posible cuando ambas personas pueden mostrarse con autenticidad. La "
    "identidad madura al comprender que afirmar tu propia voz no rompe la armonía, sino que la "
    "hace más real y profunda. Entonces tu presencia transmite elegancia, respeto y una capacidad "
    "natural para unir sin dejar de ser quien eres."
),


"Escorpio": (
    "Cuando Escorpio ocupa la cúspide de la Casa 1, la identidad se desarrolla a través de "
    "experiencias que invitan a transformarte profundamente. Existe una tendencia natural a "
    "vivir la vida con intensidad, buscando comprender aquello que permanece oculto bajo la "
    "superficie y evitando las relaciones o situaciones que percibes como superficiales. Tu "
    "presencia suele transmitir profundidad, reserva y una fuerza interior que no siempre "
    "necesita hacerse evidente para sentirse.\n\n"

    "No acostumbras a mostrar todas tus facetas desde el primer momento. Prefieres observar, "
    "comprender el contexto y decidir cuándo abrirte realmente. Esa prudencia no nace "
    "necesariamente de la desconfianza, sino de la necesidad de sentir que los vínculos y las "
    "experiencias poseen suficiente autenticidad como para implicarte plenamente. Cuando "
    "entregas tu confianza, sueles hacerlo con una intensidad poco habitual.\n\n"

    "La identidad evoluciona aquí mediante procesos de cambio que obligan a dejar atrás "
    "versiones anteriores de quién eres. A lo largo de la vida es frecuente atravesar etapas de "
    "gran transformación personal, en las que aquello que parecía definirte deja de tener "
    "sentido para dar paso a una comprensión más profunda de quién eres realmente. Tu fuerza "
    "no nace de evitar las crisis, sino de la capacidad para atravesarlas y renacer de ellas.\n\n"

    "Esta posición favorece una enorme capacidad de observación, intuición y fortaleza "
    "emocional. Percibes con facilidad aquello que otras personas intentan ocultar y sueles "
    "comprender las motivaciones profundas que hay detrás de muchos comportamientos. Esa mirada "
    "te permite desarrollar una gran lucidez y acompañar procesos complejos con una serenidad "
    "que inspira confianza.\n\n"

    "El desafío aparece cuando la necesidad de proteger tu mundo interior se convierte en "
    "control, rigidez o dificultad para confiar. El miedo a sentirte vulnerable puede llevarte "
    "a mantener demasiadas defensas o a intentar sostener situaciones que ya han cumplido su "
    "función. En ocasiones también puede costar aceptar que algunas transformaciones requieren "
    "soltar antes de poder reconstruir.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera fortaleza no "
    "consiste en controlar el cambio, sino en colaborar con él. La identidad madura cuando "
    "comprendes que cada transformación revela una parte más auténtica de quién eres. Entonces "
    "tu presencia transmite profundidad, integridad y una capacidad extraordinaria para afrontar "
    "la vida sin perder el contacto con tu propia verdad."
),


"Sagitario": (
    "Cuando Sagitario ocupa la cúspide de la Casa 1, la identidad necesita crecer, explorar y "
    "ampliar constantemente sus horizontes. Existe un impulso natural a buscar nuevas "
    "experiencias, descubrir otros modos de comprender la realidad y encontrar un sentido que "
    "dé coherencia al propio camino. Tu presencia suele transmitir entusiasmo, apertura y una "
    "confianza espontánea en las posibilidades que ofrece la vida.\n\n"

    "Difícilmente sientes que estás plenamente presente cuando todo permanece igual durante "
    "demasiado tiempo. Aprender, viajar, estudiar o simplemente cuestionar lo conocido forman "
    "parte del proceso mediante el cual vas construyendo tu identidad. Más que acumular experiencias, "
    "necesitas sentir que cada una de ellas amplía tu comprensión del mundo y de quién eres.\n\n"

    "La identidad evoluciona aquí a través de la búsqueda de significado. No basta con hacer; "
    "también necesitas comprender por qué merece la pena hacerlo. Esa necesidad de encontrar un "
    "hilo conductor favorece una visión amplia de la existencia y una capacidad especial para "
    "integrar conocimientos, culturas o formas de pensar aparentemente muy diferentes.\n\n"

    "Esta posición aporta optimismo, generosidad y una facilidad natural para contagiar "
    "confianza a quienes te rodean. Sueles mirar hacia delante incluso en momentos difíciles y "
    "recordar que toda experiencia puede convertirse en una oportunidad de aprendizaje. Esa "
    "mirada amplia inspira a otras personas a salir de sus propios límites.\n\n"

    "El desafío aparece cuando el deseo de expansión dificulta el compromiso con procesos que "
    "requieren paciencia o profundidad. Puede surgir cierta inquietud ante la rutina o la "
    "sensación de que siempre existe un horizonte más interesante que el presente. En ocasiones "
    "también puede resultar fácil defender las propias convicciones con tanta fuerza que otras "
    "miradas queden en segundo plano.\n\n"

    "La madurez llega cuando descubres que la verdadera expansión no depende únicamente de "
    "llegar más lejos, sino también de profundizar en aquello que eliges recorrer. Entonces la "
    "identidad integra entusiasmo y sabiduría, permitiéndote avanzar con libertad sin perder la "
    "coherencia con aquello que realmente da sentido a tu vida."
),


"Capricornio": (
    "Cuando Capricornio ocupa la cúspide de la Casa 1, la identidad se construye de forma "
    "gradual, constante y consciente. Existe una tendencia natural a asumir responsabilidades "
    "desde edades tempranas o a sentir que el propio crecimiento depende del esfuerzo, la "
    "disciplina y la capacidad para sostener los compromisos adquiridos. Tu presencia suele "
    "transmitir serenidad, prudencia y una fortaleza que inspira confianza.\n\n"

    "No acostumbras a definirte por impulsos pasajeros. Prefieres construir una identidad "
    "sólida, basada en aquello que realmente puedes demostrar con tus actos. Existe una "
    "necesidad de avanzar paso a paso, consolidando cada etapa antes de iniciar la siguiente. "
    "Eso favorece una gran capacidad para perseverar incluso cuando los resultados tardan en "
    "aparecer.\n\n"

    "La identidad evoluciona aquí a través de los desafíos. Cada responsabilidad asumida, cada "
    "objetivo alcanzado y cada dificultad superada fortalecen la confianza en tus propios "
    "recursos. Con frecuencia descubres quién eres precisamente cuando la vida exige madurez, "
    "paciencia y capacidad para sostener el rumbo.\n\n"

    "Esta posición aporta organización, sentido práctico y una notable habilidad para convertir "
    "los proyectos en realidades concretas. Sueles valorar aquello que permanece en el tiempo y "
    "comprendes que muchas construcciones importantes requieren constancia antes que rapidez. "
    "Esa actitud convierte tu trabajo en una fuente de crecimiento personal.\n\n"

    "El desafío aparece cuando la responsabilidad se transforma en autoexigencia permanente o "
    "cuando el miedo al error dificulta disfrutar del camino. Puede surgir la sensación de que "
    "siempre falta algo por conseguir antes de permitirte descansar o reconocer los propios "
    "logros. En algunos momentos también puede costar mostrar vulnerabilidad por temor a parecer "
    "débil.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera madurez no "
    "consiste en cargar con todo el peso, sino en construir una vida donde la responsabilidad y "
    "el bienestar puedan convivir. Entonces tu presencia transmite autoridad serena, coherencia "
    "y una capacidad extraordinaria para convertir los sueños en realidad sin perder la "
    "humanidad en el proceso."
),


"Acuario": (
    "Cuando Acuario ocupa la cúspide de la Casa 1, la identidad necesita desarrollarse con "
    "libertad y autenticidad. Existe una inclinación natural a cuestionar lo establecido y a "
    "buscar una manera propia de comprender la realidad, incluso cuando eso implique recorrer "
    "caminos diferentes a los de la mayoría. Tu presencia suele transmitir originalidad, "
    "independencia y una mirada abierta hacia lo nuevo.\n\n"

    "Más que adaptarte para encajar, necesitas descubrir aquello que realmente te representa. "
    "La identidad crece cuando puedes expresar tus ideas con honestidad y sentir que dispones "
    "del espacio suficiente para evolucionar sin limitaciones de expectativas ajenas. Esa "
    "libertad interior suele convertirse en una de las bases más importantes de tu desarrollo.\n\n"

    "La vida te lleva con frecuencia a explorar perspectivas poco habituales, conectar "
    "con personas diferentes o participar en proyectos que buscan aportar algo nuevo a la "
    "sociedad. Existe una facilidad especial para observar la realidad desde cierta distancia, "
    "identificando posibilidades de cambio allí donde otras personas únicamente ven costumbre.\n\n"

    "Esta posición favorece una actitud innovadora y una gran capacidad para adaptarte a contextos "
    "cambiantes sin perder tu esencia. Tu independencia anima a otras personas a cuestionar sus "
    "propios límites y demuestra que existen muchas formas válidas de construir una identidad.\n\n"

    "El desafío aparece cuando el deseo de preservar tu libertad genera distancia emocional o "
    "dificulta implicarte plenamente en determinados vínculos. En algunos momentos también puede "
    "surgir la necesidad de diferenciarte por sistema, confundiendo originalidad con oposición. "
    "La autenticidad deja de ser creativa cuando necesita demostrar constantemente que es distinta.\n\n"

    "La madurez llega cuando descubres que ser libre no implica alejarte de los demás, sino "
    "relacionarte desde una identidad plenamente consciente de sí misma. Entonces tu presencia "
    "transmite innovación, apertura y una profunda confianza en que cada persona puede encontrar "
    "su propia manera de contribuir al mundo."
),


"Piscis": (
    "Cuando Piscis ocupa la cúspide de la Casa 1, la identidad se desarrolla a través de una "
    "profunda sensibilidad hacia la vida y de una gran capacidad para percibir aquello que no "
    "siempre resulta evidente. Tu manera de presentarte al mundo nace menos de una imagen que "
    "deseas proyectar y más de la forma en que experimentas lo que sucede a tu alrededor. Existe "
    "una disposición natural a conectar con las personas, con los ambientes y con las emociones, "
    "como si la separación entre tú y el entorno fuera más sutil que para la mayoría.\n\n"

    "La identidad suele construirse de forma flexible, adaptándose a las distintas etapas y "
    "circunstancias que atraviesas. Más que aferrarte a una definición rígida de quién eres, "
    "necesitas sentir que puedes evolucionar, integrar nuevas experiencias y dejar espacio a "
    "aquello que todavía está tomando forma. Esa apertura favorece una personalidad receptiva, "
    "capaz de comprender la complejidad humana sin reducirla a respuestas simples.\n\n"

    "Tu presencia transmite cercanía, empatía y una sensación de aceptación que facilita que "
    "otras personas se sientan comprendidas. Con frecuencia percibes matices emocionales antes "
    "de que sean expresados y desarrollas una intuición que orienta muchas de tus decisiones. "
    "Cuando aprendes a confiar en esa percepción sin perder el contacto con la realidad, se "
    "convierte en una de tus mayores fortalezas.\n\n"

    "Esta posición favorece una gran imaginación y una notable capacidad para inspirarte en lo "
    "simbólico, lo artístico o aquello que trasciende lo puramente racional. Existe facilidad "
    "para conectar con diferentes maneras de entender la vida y para descubrir belleza y sentido "
    "allí donde otras personas únicamente perciben hechos cotidianos. La identidad encuentra así "
    "una fuente constante de crecimiento en la creatividad, la espiritualidad o el servicio a los "
    "demás.\n\n"

    "El desafío aparece cuando la sensibilidad dificulta establecer límites claros o cuando las "
    "emociones del entorno terminan confundiendo tu propia percepción. En determinados momentos "
    "puede resultar más sencillo adaptarte a las expectativas ajenas que preguntarte qué deseas "
    "realmente. También puede surgir la tendencia a evitar aquello que genera dolor o conflicto, "
    "confiando en que desaparecerá por sí solo si no se afronta directamente.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera compasión comienza "
    "por incluirte también. La identidad madura cuando comprendes que abrirte al mundo "
    "no implica perderte en él, sino desarrollar una presencia consciente capaz de mantener la "
    "sensibilidad sin renunciar a la claridad. Entonces tu forma de estar en la vida transmite "
    "serenidad, inspiración y una profunda capacidad para acompañar a otras personas desde la "
    "autenticidad y el equilibrio."
),
}


CASA_2 = {

"Aries": (
    "Cuando Aries ocupa la cúspide de la Casa 2, la sensación de seguridad suele construirse "
    "a través de la acción y de la capacidad para generar recursos de manera autónoma. Existe una "
    "necesidad profunda de sentir que puedes responder a los desafíos de la vida con tus propios recursos, "
    "confiando más en tu iniciativa que en la estabilidad proporcionada por las circunstancias "
    "externas. La seguridad nace aquí de la experiencia de comprobar que eres capaz de empezar "
    "de nuevo siempre que sea necesario.\n\n"

    "El valor personal suele fortalecerse cuando tienes la oportunidad de actuar, emprender o "
    "abrir caminos propios. Permanecer demasiado tiempo en situaciones donde todo está decidido "
    "por otras personas puede generar la sensación de que pierdes contacto con tus propios "
    "recursos. Necesitas comprobar que puedes influir en la realidad mediante tus decisiones y "
    "que tu esfuerzo tiene un efecto tangible sobre aquello que construyes.\n\n"

    "Esta posición favorece una actitud valiente frente a los recursos materiales. Sueles mostrar "
    "iniciativa ante situaciones que otras personas considerarían demasiado arriesgadas, "
    "confiando en tu capacidad para encontrar soluciones incluso cuando el camino todavía no está "
    "completamente definido. Esa disposición puede favorecer una gran capacidad de resolución "
    "cuando aparecen cambios inesperados o es necesario comenzar desde cero.\n\n"

    "Más allá del plano económico, la Casa 2 también habla del valor que reconoces en ti. "
    "Con Aries, esa autoestima suele alimentarse de los logros conquistados mediante la propia "
    "acción. Superar desafíos, desarrollar independencia o comprobar que puedes sostenerte con "
    "tus propios recursos fortalece profundamente la confianza en tus capacidades.\n\n"

    "El desafío aparece cuando la necesidad de demostrar autosuficiencia lleva a rechazar ayuda "
    "incluso cuando sería beneficiosa. También puede existir cierta impulsividad en la gestión de "
    "los recursos, priorizando la rapidez sobre la planificación o iniciando proyectos sin valorar "
    "completamente el tiempo que necesitarán para consolidarse. En algunos momentos, el deseo de "
    "actuar puede confundirse con la necesidad de reaccionar constantemente.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera seguridad no nace "
    "solo de la capacidad para conquistar nuevos recursos, sino también de aprender a conservar, "
    "administrar y desarrollar aquello que ya has construido. Cuando integras iniciativa y "
    "constancia, aparece una confianza mucho más profunda: la de saber que puedes crear valor sin "
    "necesidad de demostrar continuamente tu fortaleza."
),


"Tauro": (
    "Cuando Tauro ocupa la cúspide de la Casa 2, la seguridad se construye de forma gradual, "
    "estable y consciente. Existe una necesidad profunda de disponer de una base sólida sobre "
    "la que apoyar la vida, tanto en el plano material como en el emocional. Más que buscar "
    "resultados rápidos, prefieres desarrollar aquello que pueda sostenerse en el tiempo y "
    "proporcionarte una sensación duradera de tranquilidad.\n\n"

    "Tu relación con los recursos suele caracterizarse por la constancia y el sentido práctico. "
    "Valoras aquello que has construido con esfuerzo y tiendes a administrar lo que posees con "
    "prudencia, procurando evitar cambios innecesarios que puedan comprometer la estabilidad "
    "alcanzada. Esa actitud favorece una capacidad natural para consolidar proyectos y hacer "
    "crecer aquello que realmente merece la pena.\n\n"

    "En un plano más profundo, esta posición habla también del valor que reconoces en ti. "
    "La autoestima suele fortalecerse cuando percibes coherencia entre lo que haces, lo que "
    "eres y aquello que construyes. Necesitas sentir que tus capacidades tienen una aplicación "
    "real y que puedes generar bienestar mediante tus propios recursos. Esa experiencia aporta "
    "una confianza serena que no depende tanto de la aprobación externa como de la sensación de "
    "haber creado algo auténtico.\n\n"

    "Existe además una especial capacidad para disfrutar de lo sencillo y reconocer el valor de "
    "las experiencias que aportan bienestar, belleza o calma. El contacto con la naturaleza, "
    "los ritmos pausados o los pequeños placeres cotidianos suelen convertirse en fuentes "
    "importantes de equilibrio. Para ti, la abundancia no siempre se mide por la cantidad, sino "
    "por la posibilidad de vivir con estabilidad y plenitud.\n\n"

    "El desafío aparece cuando la necesidad de conservar lo conseguido dificulta aceptar los "
    "cambios que la vida propone. Puede surgir apego a determinadas situaciones, relaciones o "
    "formas de obtener seguridad simplemente porque resultan conocidas, incluso cuando ya no "
    "favorecen tu crecimiento. En algunos momentos también puede costar asumir riesgos que, bien "
    "gestionados, abrirían nuevas posibilidades.\n\n"

    "Con el tiempo, esta posición invita a descubrir que la verdadera estabilidad no consiste en "
    "evitar cualquier cambio, sino en desarrollar una confianza interior capaz de sostenerte "
    "también cuando las circunstancias evolucionan. Entonces el valor deja de apoyarse únicamente "
    "en lo que posees y pasa a nacer de la certeza de que siempre podrás volver a construir una "
    "base firme allí donde la vida te lleve."
),


"Géminis": (
    "Cuando Géminis ocupa la cúspide de la Casa 2, la sensación de seguridad nace del aprendizaje, "
    "la capacidad de adaptación y la confianza en tus propios recursos intelectuales. Más que "
    "apoyarte exclusivamente en estructuras estables, necesitas sentir que podrás encontrar una "
    "respuesta creativa ante cualquier cambio. La seguridad se construye aquí a través de la "
    "flexibilidad y del conocimiento adquirido con la experiencia.\n\n"

    "Tu relación con los recursos suele ser dinámica. Existe facilidad para descubrir nuevas "
    "oportunidades, diversificar intereses o desarrollar distintas habilidades que amplían tus "
    "posibilidades de crecimiento. Con frecuencia prefieres no depender de una única fuente de "
    "seguridad, sino cultivar diferentes capacidades que te permitan adaptarte a escenarios muy "
    "variados.\n\n"

    "La autoestima se fortalece cuando puedes aprender, comunicar y comprobar que tus ideas "
    "aportan valor a los demás. Comprender una situación, encontrar soluciones ingeniosas o "
    "establecer conexiones entre conocimientos diferentes alimenta profundamente la confianza "
    "en tus capacidades. Tu mayor recurso suele ser la capacidad para seguir aprendiendo.\n\n"

    "Esta posición favorece una gran agilidad mental para gestionar cambios, detectar nuevas "
    "posibilidades y desenvolverte en contextos diversos. Sabes encontrar información útil, "
    "adaptarte rápidamente y transformar el conocimiento en una herramienta práctica. Esa "
    "versatilidad puede convertirse en uno de tus recursos más valiosos a lo largo de la vida.\n\n"

    "El desafío aparece cuando la necesidad de explorar constantemente dificulta consolidar "
    "aquello que ya funciona. Puede surgir dispersión, dificultad para mantener una misma "
    "dirección o la sensación de que siempre existe una alternativa mejor esperando a ser "
    "descubierta. En algunos momentos también puede aparecer la tendencia a valorar más el "
    "conocimiento acumulado que la experiencia realmente integrada.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera riqueza no depende "
    "solo de saber muchas cosas, sino de convertir ese conocimiento en una base estable sobre la "
    "que construir tu vida. Cuando integras curiosidad y constancia, descubres que tu mayor "
    "seguridad reside en la capacidad de aprender sin perder el rumbo."
),



"Cáncer": (
    "Cuando Cáncer ocupa la cúspide de la Casa 2, la sensación de seguridad se construye "
    "principalmente a través del bienestar emocional y del sentimiento de pertenencia. Más "
    "allá de los recursos materiales, necesitas percibir que existe una base afectiva capaz de "
    "sostenerte en los momentos de cambio. Tu forma de generar estabilidad está profundamente "
    "relacionada con los vínculos, la memoria y todo aquello que despierta una sensación de hogar.\n\n"

    "La relación con los recursos suele estar marcada por un fuerte deseo de protección. Existe "
    "una tendencia natural a cuidar lo que has construido, procurando crear reservas o entornos "
    "que transmitan tranquilidad y continuidad. Para ti, la abundancia no consiste únicamente en "
    "tener más, sino en sentir que aquello que tienes puede ofrecer seguridad tanto a ti como a "
    "las personas que consideras importantes.\n\n"

    "En un plano interno, la autoestima se fortalece cuando puedes cuidar, acompañar y contribuir al "
    "bienestar de quienes te rodean. Descubres parte de tu propio valor al comprobar que eres "
    "capaz de crear espacios donde otras personas se sienten acogidas, comprendidas o protegidas. "
    "Esa sensibilidad constituye uno de tus recursos más valiosos cuando se encuentra bien "
    "integrada.\n\n"

    "Esta posición favorece una gran intuición para percibir qué necesita cada situación y cómo "
    "administrar los recursos de forma que aporten estabilidad a largo plazo. Sueles comprender "
    "que la verdadera seguridad no depende únicamente de acumular bienes, sino también de cuidar "
    "los vínculos, las raíces y todo aquello que sostiene emocionalmente una vida.\n\n"

    "El desafío aparece cuando el miedo a perder seguridad lleva a aferrarte a personas, objetos "
    "o circunstancias que ya han dejado de cumplir esa función. También puede surgir la tendencia "
    "a valorar demasiado la aprobación de quienes amas, haciendo que tu autoestima dependa en "
    "exceso del reconocimiento afectivo. En algunos momentos proteger puede convertirse, sin "
    "darte cuenta, en una forma de evitar el cambio.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la seguridad más profunda nace "
    "de la capacidad para sostenerte emocionalmente, incluso cuando las circunstancias cambian. "
    "Cuando desarrollas esa confianza interior, comprendes que tu verdadero valor no depende de "
    "retener aquello que amas, sino de la capacidad de seguir construyendo hogar allí donde la "
    "vida te lleve."
),



"Leo": (
    "Cuando Leo ocupa la cúspide de la Casa 2, la sensación de valor se fortalece cuando puedes "
    "expresar tus talentos de forma auténtica y comprobar que aquello que aportas tiene un lugar "
    "en el mundo. Más allá de los recursos materiales, necesitas sentir que tus capacidades son "
    "reconocidas y que puedes construir una vida coherente con lo que realmente eres. La seguridad "
    "nace aquí de la experiencia de desarrollar plenamente tu potencial.\n\n"

    "Tu relación con los recursos suele estar marcada por el deseo de crear algo que lleve tu "
    "propio sello. Existe una inclinación natural a invertir energía en proyectos donde puedas "
    "expresarte con libertad, aportar creatividad o desarrollar una visión personal. Para ti, el "
    "trabajo y los recursos adquieren verdadero significado cuando representan una extensión de tu "
    "identidad y no únicamente una obligación.\n\n"

    "La autoestima crece cuando reconoces el valor de tus cualidades sin necesidad de compararte "
    "constantemente con otras personas. Existe una profunda necesidad de sentir orgullo por el "
    "camino recorrido y de comprobar que aquello que construyes refleja tu autenticidad. Cuando "
    "esa coherencia aparece, desarrollas una confianza que inspira también a quienes te rodean.\n\n"

    "Esta posición favorece una actitud generosa frente a la abundancia. Sueles comprender que el "
    "valor aumenta cuando puede compartirse y que los recursos también sirven para crear, cuidar o "
    "impulsar aquello en lo que crees. Existe facilidad para motivar a otras personas y para "
    "transformar los propios talentos en una fuente de crecimiento colectivo.\n\n"

    "El desafío aparece cuando el reconocimiento externo se convierte en la medida principal del "
    "propio valor. Puede surgir la sensación de que nunca es suficiente o la necesidad de demostrar "
    "continuamente tus capacidades para sentir seguridad. En algunos momentos también puede existir "
    "la tendencia a sostener un estilo de vida que refleje éxito más que bienestar auténtico.\n\n"

    "Con el tiempo, esta posición invita a descubrir que el verdadero valor no depende del aplauso "
    "ni de la admiración ajena, sino de la capacidad para reconocer tus propios talentos y ponerlos "
    "al servicio de una vida con sentido. Cuando esa seguridad nace desde dentro, la abundancia deja "
    "de ser una demostración y se convierte en una consecuencia natural de expresar quién eres con "
    "autenticidad."
),


"Virgo": (
    "Cuando Virgo ocupa la cúspide de la Casa 2, la sensación de seguridad se construye a "
    "través del orden, la utilidad y la confianza en las propias capacidades. Necesitas sentir "
    "que sabes desenvolverte con eficacia en la vida cotidiana y que puedes aportar algo "
    "valioso mediante tu trabajo, tus conocimientos o tu dedicación. La estabilidad nace aquí "
    "de la experiencia de ser competente y de comprobar que aquello que haces tiene una "
    "utilidad real.\n\n"

    "Tu relación con los recursos suele caracterizarse por la prudencia y la planificación. "
    "Tiendes a observar con atención cómo administras el tiempo, la energía o el dinero, "
    "procurando evitar excesos y aprovechando al máximo aquello de lo que dispones. Existe una "
    "capacidad natural para optimizar procesos, organizar prioridades y construir seguridad a "
    "través de pequeños avances sostenidos en el tiempo.\n\n"

    "La autoestima se fortalece cuando puedes desarrollar habilidades, aprender algo nuevo o "
    "mejorar aquello que ya sabes hacer. Con frecuencia valoras más el crecimiento continuo que "
    "los grandes reconocimientos, encontrando satisfacción en la sensación de avanzar paso a "
    "paso. Tu mayor riqueza suele residir en aquello que eres capaz de hacer con dedicación y "
    "constancia.\n\n"

    "Esta posición favorece una actitud responsable hacia el trabajo y una gran capacidad para "
    "identificar aquello que necesita atención. Sabes detectar oportunidades de mejora y poner "
    "orden allí donde existe desorganización, convirtiendo esa mirada analítica en uno de tus "
    "principales recursos para construir estabilidad.\n\n"

    "El desafío aparece cuando el deseo de hacerlo todo correctamente termina convirtiéndose en "
    "una medida del propio valor. Puede surgir la sensación de que siempre falta algo por "
    "aprender o perfeccionar antes de sentirte suficiente. En algunos momentos también puedes "
    "dar más importancia a los errores que a todo lo que ya has conseguido construir.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que el verdadero valor no depende "
    "de alcanzar la perfección, sino de reconocer la calidad de aquello que ya eres capaz de "
    "aportar. Cuando integras exigencia y aceptación, desarrollas una seguridad tranquila que "
    "te permite seguir creciendo sin dejar de valorar el camino recorrido."
),


"Libra": (
    "Cuando Libra ocupa la cúspide de la Casa 2, la sensación de seguridad se construye a "
    "través del equilibrio y de la calidad de los vínculos que estableces. Más allá de los "
    "recursos materiales, necesitas sentir que existe armonía entre lo que das, lo que recibes "
    "y la manera en que compartes la vida con otras personas. La estabilidad nace aquí de la "
    "experiencia de vivir relaciones donde el intercambio resulta justo y enriquecedor.\n\n"

    "Tu relación con los recursos suele estar guiada por un fuerte sentido de la cooperación. "
    "Comprendes con facilidad que muchas oportunidades aparecen gracias a las alianzas, al "
    "diálogo o a la capacidad de construir acuerdos beneficiosos para todas las partes. Más que "
    "acumular, tiendes a valorar aquello que puede sostenerse mediante el entendimiento y la "
    "colaboración.\n\n"

    "La autoestima se fortalece cuando reconoces que tus cualidades aportan equilibrio, belleza "
    "o bienestar a tu entorno. Existe una sensibilidad especial para apreciar el valor de las "
    "personas y de las situaciones desde una mirada amplia, evitando juicios precipitados. Esa "
    "capacidad para integrar perspectivas diferentes constituye uno de tus recursos más valiosos.\n\n"

    "Esta posición favorece el desarrollo de habilidades relacionadas con la negociación, la "
    "mediación y el trabajo en equipo. Sabes generar confianza, crear ambientes agradables y "
    "encontrar soluciones donde otras personas únicamente perciben diferencias. La armonía deja "
    "de ser una idea abstracta para convertirse en una forma concreta de construir estabilidad.\n\n"

    "El desafío aparece cuando el deseo de agradar o mantener el equilibrio hace que tu propio "
    "valor dependa demasiado de la aceptación de los demás. Puede resultar difícil poner precio "
    "a tu trabajo, defender tus necesidades o reconocer tus capacidades sin buscar primero la "
    "confirmación externa. En algunos momentos también puedes ceder más de lo conveniente con "
    "tal de evitar el conflicto.\n\n"

    "Con el tiempo, esta posición invita a descubrir que el verdadero equilibrio comienza por "
    "reconocer tu propio valor. Cuando aprendes a sostener tus decisiones con serenidad, sin "
    "renunciar al diálogo ni a la cooperación, construyes una seguridad mucho más profunda. "
    "Entonces tus relaciones dejan de ser la fuente de tu valor para convertirse en el espacio "
    "donde puedes compartirlo libremente."
),


"Escorpio": (
    "Cuando Escorpio ocupa la cúspide de la Casa 2, la relación con la seguridad y los recursos "
    "se desarrolla a través de procesos profundos de transformación. La sensación de estabilidad "
    "no suele depender únicamente de conservar aquello que ya existe, sino de descubrir la propia "
    "capacidad para regenerarte, adaptarte y reconstruir cuando las circunstancias cambian. "
    "Existe una comprensión intuitiva de que el verdadero valor no siempre se encuentra en lo "
    "visible, sino también en la fortaleza interna que desarrollas a través de las experiencias "
    "vividas.\n\n"

    "Tu relación con los recursos puede estar marcada por una gran intensidad y consciencia "
    "estratégica. Sueles valorar aquello que tiene profundidad, utilidad real y capacidad para "
    "sostener procesos importantes a largo plazo. Antes que acumular por acumular, necesitas "
    "sentir que aquello que posees, desarrollas o compartes tiene un significado y responde a "
    "una necesidad auténtica. La gestión de los recursos suele implicar una mirada cuidadosa y "
    "una fuerte percepción de lo que merece tu energía.\n\n"

    "La autoestima se fortalece cuando reconoces tu capacidad para atravesar desafíos y salir "
    "con una comprensión renovada de ellos. Muchas veces descubres tu propio valor precisamente en momentos que "
    "exigen adaptación, profundidad o valentía emocional. Existe una fuerza interna que crece "
    "cada vez que compruebas que puedes afrontar cambios importantes sin perder tu esencia.\n\n"

    "Esta posición favorece una gran capacidad para comprender el valor oculto de las cosas. "
    "Puedes tener facilidad para investigar, profundizar, detectar oportunidades que otras "
    "personas no perciben o administrar recursos compartidos con una visión estratégica. La "
    "seguridad nace aquí de la consciencia de que siempre existe la posibilidad de transformar "
    "una situación y encontrar nuevas formas de generar valor.\n\n"

    "El desafío aparece cuando la necesidad de proteger tus recursos o tu propio valor interior "
    "se convierte en control, desconfianza o dificultad para compartir. Puede existir miedo a "
    "perder aquello que has conseguido o tendencia a aferrarte a situaciones que ya han terminado "
    "su ciclo porque representan una fuente conocida de seguridad. En algunos momentos también "
    "puede aparecer una relación demasiado intensa con el poder, el dinero o la necesidad de "
    "sentirte imprescindible.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera riqueza no "
    "depende de controlar aquello que posees, sino de confiar en tu capacidad para transformarte "
    "y volver a crear. Cuando integras profundidad y desapego, desarrollas una seguridad mucho "
    "más sólida: la certeza de que tu mayor recurso no está únicamente en lo que tienes, sino en "
    "la capacidad interna para evolucionar y regenerarte."
),


"Sagitario": (
    "Cuando Sagitario ocupa la cúspide de la Casa 2, la sensación de seguridad se construye a "
    "través del crecimiento, la expansión y la confianza en las propias posibilidades. Existe una "
    "necesidad de sentir que tus recursos pueden abrir caminos, ampliar horizontes y permitirte "
    "explorar nuevas experiencias. La estabilidad no se entiende tanto como permanencia, sino "
    "como la certeza de que siempre puedes aprender, desarrollarte y encontrar nuevas "
    "oportunidades.\n\n"

    "Tu relación con los recursos suele estar vinculada al conocimiento, la experiencia y la "
    "capacidad para descubrir posibilidades allí donde otras personas solo ven límites. Puedes sentir "
    "especial motivación por invertir en formación, viajes, proyectos o cualquier experiencia que amplíe "
    "tu comprensión del mundo. Para ti, aquello que aporta crecimiento posee un valor especial, "
    "incluso cuando no produce resultados inmediatos.\n\n"

    "La autoestima se fortalece cuando reconoces tu capacidad para avanzar, adaptarte y confiar "
    "en la vida. Existe una fuerza interna asociada a la visión amplia y a la convicción de que "
    "cada experiencia puede aportar aprendizaje. Tu valor personal crece cuando conectas tus "
    "talentos con un propósito que va más allá de la simple acumulación de recursos.\n\n"

    "Esta posición favorece una actitud generosa y una visión abundante de la realidad. Sueles "
    "percibir que compartir conocimientos, oportunidades o experiencias puede multiplicar el "
    "valor de aquello que tienes. Existe facilidad para inspirar a otras personas y para "
    "encontrar sentido en la manera en que utilizas tus recursos.\n\n"

    "El desafío aparece cuando el deseo de expansión dificulta la administración consciente de "
    "lo que ya posees. Puede surgir cierta tendencia a confiar demasiado en que siempre aparecerá "
    "una nueva oportunidad, sin dedicar suficiente atención a consolidar las bases actuales. "
    "También puede existir dificultad para reconocer límites cuando una experiencia promete "
    "crecimiento o aventura.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera abundancia no "
    "consiste únicamente en ampliar posibilidades, sino también en valorar y desarrollar aquello "
    "que ya forma parte de tu camino. Cuando integras visión y responsabilidad, conviertes tu "
    "capacidad de expansión en una fuente estable de crecimiento, aprendiendo que la libertad "
    "también necesita una base desde la que poder desplegarse."
),


"Capricornio": (
    "Cuando Capricornio ocupa la cúspide de la Casa 2, la sensación de seguridad se construye "
    "a través de la responsabilidad, la planificación y la capacidad para desarrollar recursos "
    "sólidos a largo plazo. Existe una necesidad profunda de sentir que aquello que tienes y "
    "aquello que construyes posee una base firme. La estabilidad nace del esfuerzo sostenido, "
    "de la experiencia acumulada y de la confianza que surge al comprobar que eres capaz de "
    "crear estructuras que permanecen en el tiempo.\n\n"

    "Tu relación con los recursos suele estar marcada por la prudencia y la visión estratégica. "
    "Tiendes a valorar más aquello que puede mantenerse y crecer con el paso de los años que "
    "aquello que ofrece resultados rápidos pero poco consistentes. La paciencia y la capacidad "
    "para organizar prioridades pueden convertirse en herramientas fundamentales para alcanzar "
    "objetivos materiales y personales.\n\n"

    "La autoestima se fortalece cuando reconoces tu capacidad para asumir responsabilidades y "
    "convertir los desafíos en aprendizajes. Existe una necesidad interna de sentir que puedes "
    "desenvolverte con autonomía y responder con madurez ante las circunstancias. Cada logro alcanzado "
    "a través de tu esfuerzo refuerza una sensación profunda de competencia y confianza personal.\n\n"

    "Esta posición favorece una relación consciente con el valor del tiempo, la experiencia y "
    "la constancia. Sueles comprender que muchos recursos importantes no aparecen de forma "
    "inmediata, sino que necesitan dedicación, disciplina y compromiso para desarrollarse. Esa "
    "visión permite construir una estabilidad que no depende únicamente de las circunstancias "
    "externas, sino de la capacidad interna para sostener procesos.\n\n"

    "El desafío aparece cuando la necesidad de seguridad se transforma en una carga excesiva de "
    "responsabilidad o en una dificultad para disfrutar de lo conseguido. Puede surgir la "
    "sensación de que siempre falta un objetivo más por alcanzar antes de permitirte descansar "
    "o valorar tus propios logros. En algunos momentos también puede existir miedo a asumir "
    "riesgos por temor a perder la estabilidad construida con tanto esfuerzo.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera seguridad no "
    "consiste únicamente en controlar los resultados, sino en confiar en la propia capacidad "
    "para adaptarte y seguir construyendo. Cuando integras disciplina y flexibilidad, desarrollas "
    "una relación más equilibrada con los recursos, donde la responsabilidad deja de ser una "
    "carga y se convierte en una expresión consciente de tu madurez."
),


"Acuario": (
    "Cuando Acuario ocupa la cúspide de la Casa 2, la sensación de seguridad se construye a "
    "través de la libertad, la innovación y la confianza en formas diferentes de generar valor. "
    "Existe una necesidad de desarrollar recursos de una manera propia, al margen de "
    "modelos tradicionales o expectativas externas. La estabilidad nace aquí de saber que puedes "
    "adaptarte, crear nuevas soluciones y encontrar caminos alternativos cuando las circunstancias "
    "cambian.\n\n"

    "Tu relación con los recursos suele ser poco convencional. Puedes sentir atracción por "
    "nuevas tecnologías, ideas innovadoras, proyectos colectivos o formas de trabajo que permitan "
    "mayor autonomía. Más que acumular por seguridad, tiendes a valorar aquello que amplía tus "
    "posibilidades de expresión y te permite participar en algo que tenga una visión de futuro.\n\n"

    "La autoestima se fortalece cuando reconoces aquello que te hace diferente y comprendes que "
    "tu manera particular de pensar constituye uno de tus principales recursos. La originalidad, "
    "la facilidad para conectar ideas y la disposición para cuestionar lo establecido pueden "
    "convertirse en fuentes importantes de crecimiento personal y material.\n\n"

    "Esta posición favorece una relación flexible con los recursos. Sueles comprender que el "
    "valor no siempre se encuentra en lo que permanece igual, sino también en la capacidad para "
    "evolucionar y responder a los cambios. Puedes tener facilidad para detectar nuevas "
    "posibilidades, anticipar tendencias o encontrar soluciones creativas ante situaciones "
    "complejas.\n\n"

    "El desafío aparece cuando la necesidad de independencia dificulta crear una base estable o "
    "mantener compromisos a largo plazo. Puede surgir cierta resistencia hacia las estructuras "
    "tradicionales, incluso cuando ofrecen apoyo útil. En algunos momentos también puede aparecer "
    "una relación demasiado mental con los recursos, olvidando las necesidades concretas de "
    "seguridad y bienestar cotidiano.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la libertad necesita también "
    "una estructura que permita sostenerla. Cuando integras innovación y estabilidad, comprendes "
    "que construir recursos propios no significa rechazar lo establecido, sino elegir de forma "
    "consciente aquello que realmente favorece tu evolución. Entonces tu manera de generar valor "
    "se convierte en una expresión auténtica de tu individualidad."
),


"Piscis": (
    "Cuando Piscis ocupa la cúspide de la Casa 2, la relación con la seguridad y los recursos "
    "se desarrolla a través de la sensibilidad, la intuición y la capacidad para percibir valores "
    "que no siempre son visibles de forma inmediata. Existe una manera más fluida de comprender "
    "la abundancia, donde los recursos no se limitan únicamente a lo material, sino que también "
    "incluyen la creatividad, la empatía, la inspiración y la capacidad para conectar con aquello "
    "que tiene significado profundo.\n\n"

    "Tu relación con los recursos suele estar guiada por una percepción intuitiva de lo que "
    "merece atención y energía. Puedes sentir especial motivación por actividades que aportan sentido, "
    "ayudan a otros o permiten expresar una dimensión creativa y sensible. La seguridad aparece "
    "cuando sientes que aquello que haces está alineado con tus valores internos y no únicamente "
    "con criterios externos de éxito.\n\n"

    "La autoestima se fortalece cuando reconoces el valor de tu sensibilidad y comprendes que "
    "tu capacidad para imaginar, acompañar o percibir matices constituye un recurso real. "
    "Muchas veces aquello que aportas no siempre resulta fácil de medir, pero puede generar un "
    "impacto profundo en las personas y situaciones con las que entras en contacto.\n\n"

    "Esta posición favorece una relación intuitiva y creativa con la generación de recursos. "
    "Existe facilidad para encontrar soluciones poco convencionales, inspirarte en diferentes "
    "fuentes y aportar una mirada más humana a los proyectos que desarrollas. La riqueza puede "
    "aparecer especialmente cuando logras unir sensibilidad y capacidad práctica.\n\n"

    "El desafío aparece cuando la apertura y la confianza dificultan establecer límites claros "
    "en la gestión de los recursos. Puede existir tendencia a dar más de lo conveniente, confiar "
    "demasiado en que las circunstancias se resolverán por sí mismas o no valorar suficientemente "
    "aquello que aportas. En algunos momentos también puede resultar difícil diferenciar entre "
    "generosidad auténtica y renuncia a tus propias necesidades.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera abundancia nace "
    "cuando la sensibilidad se une a la claridad. Cuando aprendes a reconocer el valor de lo "
    "intangible sin descuidar los aspectos concretos de la vida, desarrollas una relación más "
    "equilibrada con los recursos. Entonces tu capacidad para percibir, crear y acompañar se "
    "convierte en una fuente profunda de riqueza interior y exterior."
),
}


CASA_3 = {

"Aries": (
    "Cuando Aries ocupa la cúspide de la Casa 3, la forma de aprender y comunicarse se "
    "desarrolla a través de la acción, la iniciativa y la experiencia directa. Existe una "
       "necesidad natural de descubrir las cosas a través de tu propia experiencia, probando, explorando y "
    "obteniendo conocimiento a través del contacto inmediato con la realidad. Las ideas "
    "cobran fuerza cuando pueden ponerse en movimiento y convertirse en algo práctico.\n\n"

    "Tu manera de comunicar suele ser directa, espontánea y orientada a la acción. Tiendes "
    "a expresar aquello que piensas con rapidez, sin demasiados filtros previos, confiando "
    "en la sinceridad como una forma de conexión. Las conversaciones adquieren más valor "
    "cuando permiten avanzar, resolver algo o abrir nuevas posibilidades.\n\n"

    "El aprendizaje se fortalece mediante los desafíos y la experimentación. Sueles asimilar "
    "mejor aquello que puedes vivir, practicar o descubrir a través de tu propia experiencia "
    "que aquello que permanece únicamente en el plano teórico. La curiosidad aparece como un "
    "impulso que te lleva a investigar, preguntar y buscar respuestas sin esperar necesariamente "
    "a tener todas las condiciones preparadas.\n\n"

    "Esta posición favorece una mente rápida y una gran capacidad para iniciar conversaciones, "
    "proyectos o procesos de aprendizaje. Puedes aportar entusiasmo a los intercambios y "
    "estimular a otras personas a pasar de la idea a la acción. Tu forma de comunicar tiene "
    "la capacidad de activar movimiento y despertar motivación en el entorno.\n\n"

    "El desafío aparece cuando la rapidez mental y la necesidad de avanzar dificultan escuchar "
    "otros ritmos o profundizar en una idea antes de pasar a la siguiente. Puede surgir "
    "impaciencia con explicaciones demasiado extensas, procesos lentos o perspectivas que "
    "requieren más tiempo de integración. En algunos momentos la respuesta inmediata puede "
    "ocupar el espacio que necesita la reflexión.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera fuerza de la "
    "comunicación no reside únicamente en expresar con claridad, sino también en saber recibir "
    "y elaborar lo que llega del exterior. Cuando integras impulso y escucha, tu pensamiento "
    "se convierte en una herramienta poderosa para abrir caminos, compartir ideas y generar "
    "movimiento consciente."
),


"Tauro": (
    "Cuando Tauro ocupa la cúspide de la Casa 3, la forma de aprender y comunicar se desarrolla "
    "de manera gradual, práctica y basada en la experiencia. Necesitas tiempo para asimilar "
    "nuevas ideas y prefieres construir el conocimiento sobre bases sólidas antes que aceptar "
    "información sin haber comprobado su valor. Tu mente busca comprender aquello que puede "
    "aplicarse y permanecer en el tiempo.\n\n"

    "Tu comunicación suele transmitir calma, coherencia y una tendencia a elegir cuidadosamente "
    "las palabras. No acostumbras a hablar únicamente por llenar espacios; tiendes a valorar "
    "aquello que tiene sentido y aporta algo concreto. Cuando expresas una idea, suele existir "
    "una intención de que pueda sostenerse y resultar útil para quien la recibe.\n\n"

    "El aprendizaje se fortalece a través de la repetición, la práctica y la conexión con "
    "experiencias reales. Puedes desarrollar una gran capacidad para consolidar conocimientos "
    "cuando dispones del tiempo necesario para integrarlos. Lo que aprendes tiende a convertirse "
    "en una referencia estable desde la que continuar creciendo.\n\n"

    "Esta posición favorece una forma de pensamiento paciente y constructiva. Existe facilidad "
    "para organizar información, desarrollar habilidades poco a poco y convertir conocimientos "
    "en recursos concretos. Tu manera de comprender la realidad suele apoyarse en aquello que "
    "puede observarse, comprobarse y experimentarse directamente.\n\n"

    "El desafío aparece cuando la necesidad de seguridad intelectual dificulta abrirte a ideas "
    "nuevas o perspectivas diferentes. Puede existir resistencia inicial ante cambios de opinión "
    "o formas de aprendizaje que no siguen métodos conocidos. En algunos momentos también puede "
    "aparecer cierta lentitud para adaptarte a información nueva cuando llega demasiado rápido.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que una mente estable no necesita "
    "permanecer cerrada, sino desarrollar raíces suficientemente fuertes para poder explorar "
    "nuevas posibilidades. Cuando integras constancia y apertura, tu comunicación transmite "
    "claridad, profundidad y una capacidad especial para convertir ideas en conocimientos "
    "duraderos."
),


"Géminis": (
    "Cuando Géminis ocupa la cúspide de la Casa 3, la comunicación y el aprendizaje se "
    "convierten en un territorio especialmente activo y estimulante. Existe una necesidad "
    "natural de preguntar, investigar, intercambiar información y descubrir diferentes formas "
    "de comprender la realidad. La mente encuentra energía en el movimiento constante de las "
    "ideas y en la posibilidad de conectar conceptos diversos.\n\n"

    "Tu manera de comunicar suele ser curiosa, flexible y abierta al diálogo. Disfrutas "
    "explorando conversaciones, recogiendo perspectivas distintas y descubriendo nuevos "
    "puntos de vista. La palabra se convierte en una herramienta para pensar, relacionarte y "
    "dar forma a aquello que todavía estás comprendiendo.\n\n"

    "El aprendizaje se desarrolla a través de la variedad y la experimentación intelectual. "
    "Puedes sentir una gran motivación por estudiar temas diferentes, adquirir conocimientos "
    "diversos y establecer conexiones entre áreas aparentemente separadas. Tu capacidad para "
    "adaptarte mentalmente permite encontrar información útil con rapidez.\n\n"

    "Esta posición favorece una gran agilidad para comprender situaciones, explicar conceptos "
    "y crear puentes entre personas o ideas. Puedes convertirte en un transmisor natural de "
    "información, alguien capaz de traducir contenidos complejos y hacerlos accesibles para "
    "otros.\n\n"

    "El desafío aparece cuando la abundancia de estímulos dificulta profundizar o mantener la "
    "atención durante suficiente tiempo. Puede surgir dispersión, acumulación de información "
    "sin verdadera integración o una tendencia a buscar siempre una nueva idea antes de "
    "desarrollar plenamente la actual. En algunos momentos pensar mucho puede sustituir a "
    "experimentar aquello que realmente quieres comprender.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera inteligencia "
    "no depende únicamente de acumular datos, sino de transformar la información en comprensión. "
    "Cuando integras curiosidad y profundidad, tu mente se convierte en un espacio creativo "
    "capaz de conectar mundos diferentes y generar nuevas formas de ver la realidad."
),


"Cáncer": (
    "Cuando Cáncer ocupa la cúspide de la Casa 3, la forma de aprender y comunicar se "
    "desarrolla a través de la sensibilidad, la memoria y la conexión emocional con la "
    "información. No solo incorporas conocimientos mediante la lógica, sino también a través "
    "de aquello que despierta una resonancia interna. Las experiencias, las historias y los "
    "vínculos cercanos suelen convertirse en una fuente esencial de comprensión.\n\n"

    "Tu manera de comunicar suele estar marcada por la cercanía y la capacidad para percibir "
    "el estado emocional de quienes te escuchan. Existe una sensibilidad especial hacia el "
    "tono, el contexto y aquello que no siempre se expresa directamente con palabras. La "
    "comunicación adquiere profundidad cuando existe confianza y un espacio donde las personas "
    "pueden mostrarse con autenticidad.\n\n"

    "El aprendizaje se fortalece cuando puedes relacionar lo nuevo con experiencias previas. "
    "La memoria juega un papel importante, permitiéndote conservar detalles, sensaciones y "
    "conocimientos vinculados a momentos significativos. Tiendes a comprender mejor aquello "
    "que tiene una historia detrás o que conecta con algo que ya forma parte de tu mundo interno.\n\n"

    "Esta posición favorece una gran capacidad para escuchar, acompañar y transmitir ideas de "
    "una manera humana y comprensible. Puedes tener facilidad para captar las necesidades de "
    "los demás y adaptar tu forma de comunicar para crear seguridad y cercanía. Tus palabras "
    "pueden convertirse en un espacio de acogida para quienes necesitan ser comprendidos.\n\n"

    "El desafío aparece cuando las emociones influyen demasiado en la interpretación de la "
    "información o cuando determinadas experiencias del pasado condicionan la manera de "
    "comprender el presente. Puede existir tendencia a tomar las palabras de forma demasiado "
    "personal o dificultad para separar lo que realmente sucede de aquello que despierta "
    "recuerdos y sensaciones antiguas.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la sensibilidad y la claridad "
    "pueden convivir. Cuando aprendes a escuchar tus emociones sin permitir que te guíen por completo, "
    "desarrollas una comunicación profunda y empática, capaz de unir conocimiento "
    "y experiencia emocional de una manera especialmente enriquecedora."
),


"Leo": (
    "Cuando Leo ocupa la cúspide de la Casa 3, la comunicación y el aprendizaje se desarrollan "
    "a través de la expresión personal, la creatividad y el deseo de aportar una visión propia. "
    "Existe una necesidad natural de que las ideas lleven tu sello, de encontrar una forma "
    "particular de interpretar y compartir aquello que descubres. Aprender adquiere más fuerza "
    "cuando puedes implicarte desde la identidad y la pasión.\n\n"

    "Tu manera de comunicar suele ser expresiva, cálida y orientada a generar impacto. Existe "
    "facilidad para contar historias, transmitir entusiasmo o presentar ideas de una forma que "
    "despierte interés en otras personas. Las palabras se convierten en una herramienta para "
    "mostrar quién eres y compartir aquello que consideras valioso.\n\n"

    "El aprendizaje se fortalece cuando existe creatividad y espacio para experimentar. Sueles "
    "asimilar mejor aquello que permite participar activamente, desarrollar una perspectiva "
    "propia o encontrar una forma personal de expresarlo. El conocimiento necesita sentirse "
    "vivo, no simplemente acumulado.\n\n"

    "Esta posición favorece una gran capacidad para inspirar mediante la comunicación. Puedes "
    "tener facilidad para enseñar, motivar o transmitir confianza cuando compartes algo que "
    "realmente te entusiasma. Tu forma de explicar puede aportar claridad y energía a los "
    "procesos de aprendizaje de otras personas.\n\n"

    "El desafío aparece cuando la necesidad de expresar tu propia visión dificulta escuchar "
    "otras interpretaciones o aceptar que existen diferentes maneras de comprender una misma "
    "realidad. Puede surgir cierta identificación con las propias ideas o una búsqueda excesiva "
    "de reconocimiento por aquello que comunicas.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que una voz verdaderamente "
    "creativa no necesita imponerse para tener valor. Cuando integras expresión y escucha, tu "
    "comunicación se convierte en una fuente de inspiración capaz de iluminar ideas propias y "
    "también abrir espacio para las de los demás."
),


"Virgo": (
    "Cuando Virgo ocupa la cúspide de la Casa 3, la comunicación y el aprendizaje se desarrollan "
    "a través del análisis, la observación y la búsqueda constante de precisión. Existe una "
    "tendencia natural a examinar la información, ordenar los datos y comprender cómo funcionan "
    "las cosas antes de sacar conclusiones. La mente busca coherencia y utilidad en aquello que "
    "aprende.\n\n"

    "Tu manera de comunicar suele ser clara, detallada y orientada a aportar soluciones. "
    "Tiendes a valorar las palabras bien elegidas y los mensajes que contienen información "
    "práctica. Más que hablar por hablar, prefieres que la comunicación tenga un propósito y "
    "pueda ayudar a mejorar una situación concreta.\n\n"

    "El aprendizaje se fortalece mediante la práctica, la organización y la atención a los "
    "pequeños detalles. Puedes desarrollar una gran capacidad para investigar, perfeccionar "
    "habilidades y adquirir conocimientos especializados. Tu mente encuentra seguridad cuando "
    "comprende los procesos paso a paso.\n\n"

    "Esta posición favorece una gran capacidad para detectar errores, encontrar matices y "
    "ordenar información compleja. Puedes convertirte en una persona de referencia cuando se "
    "necesita analizar una situación, estructurar conocimientos o encontrar una manera más "
    "eficiente de hacer algo.\n\n"

    "El desafío aparece cuando el deseo de precisión se convierte en exceso de análisis o en "
    "una exigencia demasiado elevada hacia tus propias ideas y expresiones. Puede surgir miedo "
    "a equivocarte, necesidad de revisar continuamente lo que comunicas o dificultad para "
    "permitirte aprender mediante la experimentación y el error.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que el conocimiento no necesita "
    "ser perfecto para ser valioso. Cuando integras análisis y confianza, desarrollas una mente "
    "precisa pero flexible, capaz de aportar claridad sin perder espontaneidad ni curiosidad."
),


"Libra": (
    "Cuando Libra ocupa la cúspide de la Casa 3, la comunicación y el aprendizaje se "
    "desarrollan a través del intercambio, la escucha y la búsqueda de equilibrio entre "
    "diferentes perspectivas. Existe una necesidad natural de comprender otros puntos de "
    "vista y encontrar conexiones entre ideas aparentemente distintas. El conocimiento "
    "crece especialmente cuando puede compartirse y enriquecerse mediante el diálogo.\n\n"

    "Tu manera de comunicar suele ser amable, diplomática y orientada a crear puentes. "
    "Tiendes a considerar cómo reciben los demás aquello que expresas, buscando palabras "
    "que favorezcan el entendimiento y reduzcan las tensiones. La conversación adquiere "
    "valor cuando permite acercar posiciones y descubrir nuevas formas de mirar una misma "
    "situación.\n\n"

    "El aprendizaje se fortalece mediante la comparación, la observación de diferentes "
    "opiniones y la posibilidad de integrar matices. Puedes desarrollar una gran capacidad "
    "para comprender perspectivas diversas sin necesidad de rechazar automáticamente "
    "aquello que difiere de tu propia visión. La inteligencia se expresa aquí a través "
    "de la capacidad para relacionar y armonizar información.\n\n"

    "Esta posición favorece habilidades relacionadas con la mediación, la negociación y "
    "la expresión estética o creativa. Puedes tener facilidad para explicar ideas de "
    "manera accesible, encontrar puntos comunes entre personas diferentes y aportar una "
    "mirada equilibrada en conversaciones complejas.\n\n"

    "El desafío aparece cuando el deseo de mantener la armonía dificulta expresar una "
    "opinión propia con claridad. Puede existir tendencia a adaptar demasiado el discurso "
    "según la persona que tienes delante o a evitar conversaciones incómodas para no "
    "generar conflicto. En algunos momentos la búsqueda de todos los puntos de vista puede "
    "retrasar la toma de decisiones.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera comunicación "
    "equilibrada no consiste en agradar siempre, sino en unir respeto y autenticidad. "
    "Cuando integras escucha y afirmación personal, tu forma de comunicar se convierte en "
    "un espacio donde las diferencias pueden encontrarse sin perder claridad."
),


"Escorpio": (
    "Cuando Escorpio ocupa la cúspide de la Casa 3, la comunicación y el aprendizaje se "
    "desarrollan a través de la profundidad, la investigación y la necesidad de comprender "
    "aquello que se encuentra más allá de la superficie. Existe una inclinación natural a "
    "buscar significados ocultos, descubrir motivaciones y explorar los aspectos de la "
    "realidad que requieren una mirada más penetrante.\n\n"

    "Tu manera de comunicar suele ser intensa, selectiva y cargada de intención. No siempre "
    "necesitas hablar mucho, pero cuando compartes algo suele existir un motivo profundo "
    "detrás. Tiendes a valorar las conversaciones auténticas, aquellas que permiten ir más "
    "allá de lo evidente y alcanzar una comprensión más completa de las experiencias humanas.\n\n"

    "El aprendizaje se fortalece mediante la investigación y la inmersión profunda en los "
    "temas que despiertan tu interés. No acostumbras a conformarte con respuestas superficiales; "
    "necesitas comprender los procesos internos, las causas y las conexiones invisibles que "
    "explican cómo funcionan las cosas.\n\n"

    "Esta posición favorece una gran capacidad de observación y análisis psicológico. Puedes "
    "percibir matices que otras personas pasan por alto y desarrollar una intuición especial "
    "para comprender lo que no está siendo expresado directamente. Tu pensamiento puede "
    "convertirse en una herramienta poderosa para investigar, transformar y revelar nuevas "
    "perspectivas.\n\n"

    "El desafío aparece cuando la profundidad se transforma en desconfianza, exceso de análisis "
    "o dificultad para aceptar explicaciones sencillas. Puede surgir tendencia a buscar siempre "
    "un significado oculto o a proteger demasiado aquello que piensas y sientes. En algunos "
    "momentos también puede costar compartir ideas antes de sentir que están completamente "
    "elaboradas.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera profundidad "
    "también incluye apertura y flexibilidad. Cuando integras investigación y confianza, tu "
    "comunicación adquiere una capacidad transformadora: no solo transmite información, sino "
    "que ayuda a comprender aquello que necesita ser visto con mayor consciencia."
),


"Sagitario": (
    "Cuando Sagitario ocupa la cúspide de la Casa 3, la comunicación y el aprendizaje se "
    "desarrollan a través de la exploración, la búsqueda de significado y la ampliación de "
    "horizontes. Existe una necesidad natural de comprender la realidad desde una perspectiva "
    "más amplia, conectando experiencias, conocimientos y diferentes formas de interpretar "
    "la vida.\n\n"

    "Tu manera de comunicar suele ser abierta, entusiasta y orientada a compartir aquello que "
    "descubres. Las conversaciones adquieren valor cuando permiten aprender algo nuevo, "
    "intercambiar ideas inspiradoras o abrir posibilidades que antes no habías considerado. "
    "Existe una tendencia a transmitir lo aprendido con generosidad.\n\n"

    "El aprendizaje se fortalece mediante la exploración y la conexión entre conocimientos "
    "diversos. Puedes sentir especial interés por culturas, filosofías, estudios o experiencias "
    "que amplían tu comprensión del mundo. La mente necesita sentir que cada nueva información "
    "forma parte de una visión más grande.\n\n"

    "Esta posición favorece una comunicación inspiradora y una capacidad natural para enseñar "
    "o transmitir perspectivas amplias. Puedes motivar a otras personas a cuestionar sus propios "
    "límites y descubrir nuevas posibilidades gracias a tu manera de relacionar ideas y "
    "experiencias.\n\n"

    "El desafío aparece cuando la búsqueda constante de expansión dificulta atender los detalles "
    "más cercanos o profundizar en aquello que requiere paciencia. Puede surgir tendencia a "
    "centrarte más en la visión general que en los matices concretos, o a defender una idea "
    "con tanta convicción que otras perspectivas queden temporalmente excluidas.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera sabiduría nace "
    "cuando la amplitud se une a la profundidad. Cuando integras entusiasmo y atención, tu "
    "comunicación se convierte en una vía para compartir conocimiento, inspirar crecimiento y "
    "conectar experiencias aparentemente separadas."
),


"Capricornio": (
    "Cuando Capricornio ocupa la cúspide de la Casa 3, la comunicación y el aprendizaje se "
    "desarrollan de manera estructurada, responsable y orientada a construir conocimientos "
    "útiles. Existe una tendencia natural a tomarte en serio aquello que aprendes, buscando "
    "comprender los temas con profundidad y convertir la información adquirida en herramientas "
    "que puedan aplicarse en la realidad.\n\n"

    "Tu forma de comunicar suele ser prudente, precisa y cuidadosamente elaborada. No siempre "
    "sientes la necesidad de hablar de inmediato; prefieres observar, organizar tus ideas y "
    "expresarlas cuando consideras que tienen una base sólida. Tus palabras suelen transmitir "
    "seriedad y fiabilidad, especialmente cuando hablas desde la experiencia adquirida.\n\n"

    "El aprendizaje se fortalece mediante la constancia y la disciplina. Puedes desarrollar una "
    "gran capacidad para dominar conocimientos complejos gracias a tu disposición para avanzar "
    "paso a paso y sostener el esfuerzo durante largos periodos de tiempo. La mente encuentra "
    "seguridad cuando puede ordenar la información y establecer una estructura clara.\n\n"

    "Esta posición favorece una inteligencia práctica y estratégica. Sueles tener facilidad para "
    "identificar qué información resulta realmente importante, organizar procesos y transmitir "
    "ideas de forma eficiente. Tu manera de pensar busca resultados concretos y puede convertirse "
    "en una referencia de estabilidad para quienes necesitan claridad.\n\n"

    "El desafío aparece cuando la necesidad de precisión y control limita la espontaneidad mental. "
    "Puede existir cierta rigidez ante ideas nuevas que todavía no han demostrado su utilidad o "
    "una tendencia a valorar demasiado la corrección frente a la curiosidad. En algunos momentos "
    "puede aparecer miedo a equivocarte al expresar lo que piensas.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que el conocimiento también crece "
    "a través de la experimentación y del intercambio abierto. Cuando integras estructura y "
    "flexibilidad, tu comunicación adquiere una gran autoridad natural: una forma de expresar "
    "ideas que une profundidad, experiencia y capacidad para construir algo duradero."
),


"Acuario": (
    "Cuando Acuario ocupa la cúspide de la Casa 3, la comunicación y el aprendizaje se "
    "desarrollan a través de la curiosidad, la innovación y la búsqueda de nuevas formas de "
    "comprender la realidad. Existe una necesidad natural de explorar ideas diferentes, "
    "cuestionar lo establecido y descubrir conexiones que permitan observar el mundo desde "
    "perspectivas poco habituales.\n\n"

    "Tu manera de comunicar suele ser original, independiente y abierta a conceptos nuevos. "
    "No acostumbras a aceptar una idea únicamente porque sea tradicional o ampliamente "
    "compartida; necesitas comprender su lógica y comprobar si sigue teniendo sentido. "
    "Las conversaciones adquieren valor cuando permiten intercambiar visiones diferentes y "
    "generar nuevas posibilidades.\n\n"

    "El aprendizaje se fortalece mediante la experimentación y la libertad intelectual. "
    "Puedes sentir especial atracción por tecnologías, conocimientos innovadores o temas "
    "que amplían la comprensión colectiva. La mente necesita espacio para investigar, "
    "conectar información diversa y encontrar soluciones alternativas.\n\n"

    "Esta posición favorece una capacidad especial para observar los problemas desde cierta "
    "distancia y encontrar enfoques que otras personas no habían considerado. Puedes aportar "
    "ideas renovadoras, facilitar cambios de perspectiva y comunicar conceptos complejos de "
    "una manera diferente a la habitual.\n\n"

    "El desafío aparece cuando la necesidad de independencia intelectual genera distancia "
    "respecto a las ideas de otras personas o cuando la búsqueda de originalidad se convierte "
    "en rechazo automático de lo conocido. En algunos momentos también puede existir una "
    "tendencia a vivir más en el mundo de las ideas que en la experiencia concreta del día a día.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera innovación no "
    "consiste únicamente en diferenciarse, sino en aportar algo que pueda integrarse y ser útil. "
    "Cuando unes visión de futuro y conexión humana, tu comunicación se convierte en un puente "
    "entre nuevas ideas y posibilidades reales de transformación."
),


"Piscis": (
    "Cuando Piscis ocupa la cúspide de la Casa 3, la comunicación y el aprendizaje se "
    "desarrollan a través de la sensibilidad, la intuición y la capacidad para percibir "
    "significados más allá de la información evidente. La mente funciona de una manera "
    "especialmente receptiva, captando matices, símbolos y conexiones que no siempre pueden "
    "explicarse únicamente mediante la lógica.\n\n"

    "Tu forma de comunicar suele estar impregnada de imaginación, empatía y una gran capacidad "
    "para conectar con las emociones de quienes te escuchan. Más que transmitir únicamente "
    "datos, buscas compartir experiencias, sensaciones o comprensiones que tengan un significado "
    "más profundo. La palabra puede convertirse en una herramienta creativa y sanadora.\n\n"

    "El aprendizaje se fortalece cuando existe una conexión emocional con aquello que estudias "
    "o exploras. Necesitas sentir que el conocimiento tiene un propósito y que puede integrarse "
    "dentro de una visión más amplia de la vida. La imaginación, la intuición y la capacidad "
    "para asociar ideas aparentemente alejadas son algunos de tus recursos más valiosos.\n\n"

    "Esta posición favorece una gran sensibilidad para comprender diferentes lenguajes, tanto "
    "verbales como simbólicos. Puedes desarrollar facilidad para la expresión artística, la "
    "narración, la escucha profunda o cualquier forma de comunicación donde sea importante "
    "captar aquello que permanece implícito.\n\n"

    "El desafío aparece cuando la receptividad dificulta establecer límites claros en la "
    "información que recibes. Puede existir tendencia a absorber demasiado las opiniones del "
    "entorno, perder claridad entre tus propias ideas y las de otras personas o evitar "
    "concretar pensamientos que todavía permanecen en un plano más intuitivo. En algunos "
    "momentos también puede costar organizar la información de manera práctica.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que sensibilidad y claridad no "
    "son cualidades opuestas. Cuando integras intuición y estructura, tu comunicación adquiere "
    "una profundidad especial: la capacidad de expresar aquello que muchas personas sienten, "
    "pero todavía no han encontrado palabras para nombrar."
),
}


CASA_4 = {

"Aries": (
    "Cuando Aries ocupa la cúspide de la Casa 4, las raíces y la sensación de hogar se "
    "construyen a través de la autonomía, la acción y la necesidad de disponer de un espacio "
    "propio donde poder desarrollarte libremente. El mundo interno necesita sentirse vivo, "
    "dinámico y capaz de renovarse constantemente. La seguridad emocional nace cuando sientes "
    "que puedes tomar iniciativa sobre tu propia vida y construir tu base desde tus propias "
    "decisiones.\n\n"

    "La relación con el pasado suele estar marcada por un fuerte impulso hacia la independencia. "
    "Desde etapas tempranas puede existir la necesidad de diferenciarte, encontrar tu propio "
    "camino o desarrollar una identidad que no dependa completamente de las estructuras "
    "familiares. El hogar adquiere valor cuando se convierte en un lugar donde puedes expresarte con "
    "autenticidad y libertad.\n\n"

    "Esta posición favorece una gran capacidad para crear nuevos comienzos. Incluso después de "
    "periodos difíciles, existe una fuerza interna que impulsa a reconstruir, iniciar una nueva "
    "etapa y recuperar la confianza en la propia capacidad para salir adelante. Tus raíces no "
    "se dependen únicamente de la permanencia, sino también con la valentía para transformar "
    "aquello que ya no sostiene tu crecimiento.\n\n"

    "En el ámbito familiar puedes asumir con frecuencia un papel activo, protector o impulsor "
    "del movimiento. Existe una tendencia a querer resolver, iniciar cambios o abrir caminos "
    "cuando percibes que algo permanece estancado. Esa energía puede convertirse en una fuerza "
    "renovadora dentro del sistema familiar.\n\n"

    "El desafío aparece cuando la necesidad de independencia dificulta aceptar apoyo emocional "
    "o permanecer en contacto con la vulnerabilidad. Puede existir tendencia a reaccionar antes "
    "de escuchar plenamente lo que sientes, o a vivir el hogar como un espacio del que necesitas "
    "escapar para afirmar tu identidad. En algunos momentos los conflictos familiares pueden "
    "activar respuestas impulsivas.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que construir raíces no significa "
    "perder libertad. La verdadera estabilidad aparece cuando puedes sostener tu individualidad "
    "sin necesidad de romper los vínculos que forman parte de tu historia. Entonces creas un "
    "hogar interno basado en la confianza, la autonomía y la capacidad de comenzar de nuevo."
),


"Tauro": (
    "Cuando Tauro ocupa la cúspide de la Casa 4, las raíces y el sentido de pertenencia se "
    "construyen a través de la estabilidad, la continuidad y la creación de un entorno seguro. "
    "Existe una necesidad profunda de disponer de una base firme desde la que poder desarrollarte, "
    "un lugar físico y emocional donde recuperar energía y sentir que perteneces.\n\n"

    "La relación con el hogar suele estar vinculada al deseo de preservar aquello que aporta "
    "seguridad y bienestar. Valoras los espacios acogedores, los ritmos tranquilos y todo aquello "
    "que permite sentir conexión con lo esencial. La estabilidad familiar o la creación de un "
    "entorno propio pueden convertirse en pilares fundamentales de tu equilibrio interno.\n\n"

    "Tus raíces se fortalecen mediante la constancia. No sueles necesitar grandes cambios para "
    "encontrar realización; muchas veces encuentras profundidad en aquello que permanece y en los "
    "vínculos que se construyen con el paso del tiempo. Existe una capacidad natural para cuidar "
    "y sostener aquello que consideras importante.\n\n"

    "Esta posición favorece una relación especial con la memoria y con los lugares significativos. "
    "Los objetos, los espacios familiares o las tradiciones pueden adquirir un valor emocional "
    "profundo, funcionando como puntos de conexión con tu historia personal y con aquello que "
    "te proporciona sensación de continuidad.\n\n"

    "El desafío aparece cuando la necesidad de estabilidad se transforma en resistencia al cambio. "
    "Puede resultar difícil abandonar dinámicas familiares conocidas, incluso cuando ya no "
    "favorecen tu evolución. En algunos momentos también puede existir apego excesivo a recuerdos "
    "o situaciones del pasado por la seguridad emocional que representan.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que las verdaderas raíces no "
    "dependen de conservar siempre las mismas circunstancias, sino de desarrollar una sensación "
    "interna de estabilidad capaz de acompañarte en cualquier transformación. Entonces el hogar "
    "se convierte menos en un lugar externo y más en una cualidad interior de calma y confianza."
),


"Géminis": (
    "Cuando Géminis ocupa la cúspide de la Casa 4, las raíces y el sentido de pertenencia se "
    "construyen a través del intercambio, la comprensión y la necesidad de mantener vivo el "
    "movimiento interno. El hogar no se define únicamente por un lugar físico, sino también "
    "por la presencia de conversaciones, ideas y estímulos que favorezcan una sensación de conexión.\n\n"

    "La historia personal suele estar marcada por una gran curiosidad hacia el entorno familiar "
    "y por la necesidad de comprender los distintos relatos que forman parte de tus raíces. "
    "Puedes desarrollar una mirada muy observadora sobre tu pasado, intentando descubrir cómo "
    "las experiencias vividas han influido en la persona que eres.\n\n"

    "El espacio íntimo necesita libertad mental. Es posible que valores hogares donde exista "
    "comunicación, intercambio de ideas y posibilidad de adaptar el entorno según tus necesidades "
    "cambiantes. La sensación de pertenencia aparece cuando puedes expresarte y compartir tu "
    "mundo interno con naturalidad.\n\n"

    "Esta posición favorece la capacidad para integrar diferentes perspectivas familiares y "
    "comprender que cada persona posee su propia versión de la historia compartida. Puedes "
    "convertirte en un puente entre miembros de la familia gracias a tu capacidad para escuchar "
    "y traducir diferentes puntos de vista.\n\n"

    "El desafío aparece cuando la necesidad de movimiento dificulta crear una sensación profunda "
    "de arraigo. Puede existir tendencia a racionalizar las emociones familiares en lugar de "
    "sentirlas plenamente o a mantener cierta distancia cuando la intimidad requiere presencia "
    "emocional.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que las raíces también pueden "
    "construirse a través de la palabra y la comprensión. Cuando integras curiosidad y conexión "
    "emocional, desarrollas un hogar interno donde pasado y presente pueden dialogar sin que "
    "ninguno de ellos te retenga."
),


"Cáncer": (
    "Cuando Cáncer ocupa la cúspide de la Casa 4, las raíces y el sentido de pertenencia se "
    "encuentran en el centro de la experiencia vital. Existe una profunda necesidad de crear "
    "un espacio de protección, intimidad y conexión emocional donde puedas experimentar una profunda sensación de "
    "acogida. El hogar representa mucho más que un lugar físico: es un refugio interno donde "
    "recuperas energía y contacto contigo.\n\n"

    "La relación con la historia personal suele ser especialmente significativa. Los recuerdos, "
    "los vínculos familiares y las experiencias de la infancia pueden tener una gran influencia "
    "en la construcción de tu identidad emocional. Existe una memoria profunda capaz de conservar "
    "sensaciones, aprendizajes y huellas del pasado durante mucho tiempo.\n\n"

    "Esta posición favorece una gran capacidad para cuidar y sostener emocionalmente a quienes "
    "forman parte de tu mundo cercano. Crear ambientes donde las personas puedan sentirse seguras "
    "y comprendidas suele ser una expresión natural de tu manera de amar y relacionarte.\n\n"

    "El hogar puede convertirse en una fuente esencial de equilibrio. Necesitas sentir que existe "
    "un espacio donde puedes bajar las defensas, mostrar tus emociones y recibir el mismo cuidado "
    "que ofreces a los demás. Cuando esa base está presente, desarrollas una gran fortaleza "
    "interior.\n\n"

    "El desafío aparece cuando el vínculo con el pasado se vuelve demasiado determinante o cuando "
    "la necesidad de protegerte dificulta abrirte a nuevas experiencias. Puede existir tendencia "
    "a cargar con emociones familiares que no corresponden completamente a tu propio camino o a "
    "buscar seguridad únicamente en lo conocido.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que el verdadero hogar no depende "
    "solo de las personas o lugares que forman parte de tu historia, sino de la capacidad para "
    "crear dentro de ti un espacio seguro. Entonces la sensibilidad deja de ser una vulnerabilidad "
    "y se convierte en una profunda fuente de fortaleza y conexión."
),


"Leo": (
    "Cuando Leo ocupa la cúspide de la Casa 4, las raíces y el sentido de pertenencia se "
    "construyen a través de la expresión personal, la creatividad y la necesidad de sentir "
    "que el espacio íntimo refleja quién eres realmente. El hogar se convierte en un lugar "
    "donde desarrollar tu identidad, mostrar tus talentos y experimentar orgullo por aquello "
    "que has construido.\n\n"

    "La historia familiar puede tener un papel importante en la formación de tu autoestima. "
    "Existe una necesidad profunda de sentir reconocimiento dentro del núcleo cercano, de "
    "percibir que tus cualidades son vistas y valoradas por las personas que forman parte "
    "de tu vida íntima. Las raíces adquieren fuerza cuando incluyen aceptación y celebración.\n\n"

    "Esta posición favorece la creación de ambientes cálidos, luminosos y llenos de vida. "
    "Puedes sentir especial satisfacción al reunir personas, compartir momentos importantes "
    "o convertir tu hogar en un espacio donde otras personas también puedan expresarse. Existe una "
    "capacidad natural para aportar entusiasmo y vitalidad al entorno familiar.\n\n"

    "En muchos casos, la construcción de la identidad pasa por diferenciarte de la historia "
    "recibida y encontrar una manera propia de brillar. Puede existir un fuerte deseo de "
    "crear algo que continúe tu legado personal y que refleje aquello que consideras valioso.\n\n"

    "El desafío aparece cuando la necesidad de reconocimiento dentro del ámbito familiar se "
    "convierte en una búsqueda constante de aprobación. Puede resultar difícil aceptar no "
    "ocupar siempre un lugar protagonista o sentir que tu valor disminuye cuando no recibes "
    "atención. También puede existir orgullo excesivo respecto a la propia historia.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que el verdadero reconocimiento "
    "nace de la propia aceptación. Cuando construyes un hogar interno donde puedes valorarte "
    "sin depender de la mirada externa, tu presencia se convierte en una fuente de calidez, "
    "generosidad y confianza para quienes te rodean."
),


"Virgo": (
    "Cuando Virgo ocupa la cúspide de la Casa 4, las raíces y el sentido de pertenencia se "
    "construyen a través del orden, el cuidado y la necesidad de crear un entorno funcional "
    "donde cada elemento encuentre su lugar. El hogar se convierte en un espacio de equilibrio "
    "desde el que organizar la vida y recuperar claridad interior.\n\n"

    "La historia familiar suele observarse con una mirada analítica y consciente. Existe una "
    "tendencia a comprender los patrones heredados, identificar qué aspectos han sido útiles "
    "y reconocer cuáles necesitan ser transformados para construir una base más saludable. "
    "El pasado se convierte en una fuente de aprendizaje y mejora continua.\n\n"

    "Esta posición favorece una gran capacidad para cuidar mediante acciones concretas. Más "
    "que expresar afecto únicamente con palabras, puedes demostrarlo resolviendo problemas, "
    "atendiendo detalles y creando condiciones que faciliten el bienestar de quienes forman "
    "parte de tu entorno cercano.\n\n"

    "El hogar adquiere valor cuando funciona como un espacio organizado, tranquilo y coherente "
    "con tus necesidades. Existe una sensibilidad especial hacia los pequeños gestos cotidianos "
    "que aportan estabilidad: rutinas, orden, hábitos saludables y formas prácticas de sostener "
    "la vida diaria.\n\n"

    "El desafío aparece cuando la búsqueda de perfección dentro del entorno familiar genera "
    "exceso de exigencia o dificultad para aceptar que los vínculos humanos no pueden organizarse "
    "como un sistema perfecto. Puede surgir tendencia a preocuparte demasiado por aquello que "
    "falta o por lo que podría hacerse mejor.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que un hogar verdaderamente "
    "sostenedor no necesita ser impecable, sino habitable. Cuando integras cuidado y aceptación, "
    "desarrollas una base interna donde puedes descansar sin sentir que siempre existe algo que "
    "corregir o mejorar."
),


"Libra": (
    "Cuando Libra ocupa la cúspide de la Casa 4, las raíces y el sentido de pertenencia se "
    "construyen a través de la armonía, la cooperación y la calidad emocional de los vínculos "
    "cercanos. El hogar necesita sentirse como un espacio de equilibrio donde las personas "
    "puedan encontrarse desde el respeto y la comprensión mutua.\n\n"

    "La historia familiar puede vivirse a través de una búsqueda constante de reconciliación. "
    "Existe una tendencia natural a observar las diferentes posiciones dentro del sistema "
    "familiar e intentar comprender las necesidades de cada persona, buscando puntos de unión "
    "incluso en situaciones complejas.\n\n"

    "Esta posición favorece la creación de espacios bellos, acogedores y cuidados. El entorno "
    "físico puede tener una importancia especial, ya que la belleza, la armonía y la sensación "
    "de equilibrio influyen directamente en tu bienestar emocional. Necesitas sentir que el "
    "lugar donde habitas refleja paz y coherencia.\n\n"

    "Las raíces se fortalecen mediante relaciones basadas en el diálogo y la reciprocidad. "
    "Puedes desarrollar una gran capacidad para suavizar tensiones familiares y aportar una "
    "mirada objetiva cuando existen diferencias entre las personas cercanas.\n\n"

    "El desafío aparece cuando el deseo de mantener la armonía lleva a evitar conflictos "
    "necesarios o a asumir demasiado la responsabilidad de que todos estén bien. Puede existir "
    "tendencia a adaptarte en exceso al ambiente familiar, dejando en segundo plano tus propias "
    "necesidades emocionales.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera armonía no nace "
    "de evitar las diferencias, sino de poder expresarlas con respeto. Cuando construyes un "
    "hogar donde también existe espacio para tu propia voz, las relaciones se vuelven más "
    "auténticas y equilibradas."
),


"Escorpio": (
    "Cuando Escorpio ocupa la cúspide de la Casa 4, las raíces y el sentido de pertenencia se "
    "construyen a través de procesos profundos de transformación emocional. El hogar representa "
    "un territorio íntimo donde se guardan experiencias intensas, memorias importantes y "
    "aspectos de la historia personal que necesitan ser comprendidos y transformados.\n\n"

    "La relación con el pasado suele ser poderosa. Puede existir una gran sensibilidad hacia "
    "los patrones familiares heredados, las emociones no expresadas y aquello que permanece "
    "oculto dentro del sistema familiar. Existe una capacidad natural para percibir las capas "
    "más profundas de la propia historia.\n\n"

    "Esta posición favorece una enorme fortaleza interna. Las experiencias familiares, incluso "
    "las más complejas, pueden convertirse con el tiempo en una fuente de comprensión, madurez "
    "y capacidad para acompañar procesos emocionales intensos. Tus raíces no son algo estático, "
    "sino un territorio de continua evolución.\n\n"

    "El hogar necesita ser un espacio donde exista autenticidad y confianza profunda. No suelen "
    "satisfacerte los vínculos superficiales; buscas relaciones donde pueda existir entrega, "
    "honestidad y la posibilidad de compartir aquello que normalmente permanece protegido.\n\n"

    "El desafío aparece cuando la intensidad emocional del pasado dificulta soltar antiguas "
    "historias o cuando la necesidad de protegerte genera control dentro del ámbito familiar. "
    "Puede existir tendencia a guardar demasiado, cargar con secretos emocionales o sentir que "
    "debes sostener procesos que pertenecen a otras personas.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que sanar las raíces no significa "
    "negar la historia, sino integrarla. Cuando integras tu historia con consciencia, construyes "
    "un hogar interno mucho más libre, donde la profundidad se convierte en una fuente de poder "
    "y renovación."
),


"Sagitario": (
    "Cuando Sagitario ocupa la cúspide de la Casa 4, las raíces y el sentido de pertenencia "
    "se construyen a través de la expansión, la libertad y la búsqueda de un significado más "
    "amplio para la propia historia. El hogar necesita sentirse como un espacio que permita "
    "crecer, explorar y mantener viva la sensación de descubrimiento.\n\n"

    "La relación con el pasado suele estar marcada por la necesidad de comprender la historia "
    "personal dentro de un contexto más amplio. Puedes sentir curiosidad por tus orígenes, por "
    "otras culturas o por diferentes formas de entender la familia y el concepto de hogar. "
    "Las raíces no se viven únicamente como algo heredado, sino como un punto de partida desde "
    "el que seguir ampliando horizontes.\n\n"

    "Esta posición favorece la creación de hogares abiertos, dinámicos y enriquecidos por "
    "experiencias diversas. Puede existir una necesidad de vivir en espacios donde haya "
    "movimiento, aprendizaje o contacto con nuevas ideas. El hogar se convierte en una puerta "
    "hacia el mundo, más que en un lugar de aislamiento.\n\n"

    "La seguridad emocional nace cuando sientes que puedes mantener tu libertad interior. "
    "Necesitas que los vínculos familiares permitan evolución y crecimiento, sin sentir que "
    "las expectativas heredadas limitan tu desarrollo. Con frecuencia descubres tu propia "
    "identidad al cuestionar y ampliar aquello que recibiste.\n\n"

    "El desafío aparece cuando la necesidad de expansión dificulta establecer raíces profundas "
    "o mantener la conexión con la intimidad emocional. Puede existir tendencia a buscar siempre "
    "un nuevo horizonte antes de integrar completamente la experiencia actual, o a evitar "
    "determinadas emociones refugiándote en ideas, creencias o nuevos proyectos.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que las raíces no son una "
    "limitación, sino la base desde la que puedes explorar con mayor libertad. Cuando integras "
    "pertenencia y expansión, construyes un hogar interno donde la experiencia acumulada se "
    "transforma en sabiduría."
),


"Capricornio": (
    "Cuando Capricornio ocupa la cúspide de la Casa 4, las raíces y el sentido de pertenencia "
    "se construyen a través de la responsabilidad, la estructura y la necesidad de crear una "
    "base sólida sobre la que sostener la vida. Existe una tendencia natural a tomarte muy en "
    "serio aquello que forma parte de tu historia y a buscar estabilidad mediante el esfuerzo "
    "y la constancia.\n\n"

    "La relación con el pasado puede estar marcada por un fuerte sentido del deber. Es posible "
    "que desde etapas tempranas hayas percibido la necesidad de asumir responsabilidades, "
    "madurar rápidamente o desarrollar una gran capacidad de autosuficiencia. Las experiencias "
    "familiares contribuyen profundamente a formar tu manera de entender la seguridad.\n\n"

    "Esta posición favorece la construcción de un hogar estable y duradero. Existe capacidad "
    "para crear estructuras que proporcionen protección y continuidad, valorando aquello que "
    "puede mantenerse en el tiempo. El hogar no solo representa descanso, sino también un "
    "espacio donde consolidar logros y construir un legado personal.\n\n"

    "Las raíces adquieren fuerza cuando existe compromiso y sentido de responsabilidad. Puedes "
    "convertirte en una figura de referencia dentro del entorno familiar, alguien capaz de "
    "sostener situaciones complejas y aportar estabilidad cuando otros atraviesan momentos de "
    "incertidumbre.\n\n"

    "El desafío aparece cuando la responsabilidad se convierte en carga emocional o cuando "
    "resulta difícil permitirte recibir cuidado y apoyo. Puede existir tendencia a sentir que "
    "debes ser fuerte todo el tiempo, ocultando necesidades propias por considerar que primero "
    "hay que cumplir con las obligaciones.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera fortaleza "
    "también incluye la capacidad de descansar y mostrarse vulnerable. Cuando integras "
    "responsabilidad y ternura, construyes unas raíces firmes sin convertirlas en un peso "
    "que limite tu libertad emocional."
),


"Acuario": (
    "Cuando Acuario ocupa la cúspide de la Casa 4, las raíces y el sentido de pertenencia "
    "se construyen a través de la libertad, la autenticidad y la necesidad de crear una forma "
    "propia de entender el hogar. Existe una inclinación natural a cuestionar los modelos "
    "familiares heredados y buscar una manera más consciente de relacionarte con tus orígenes.\n\n"

    "La historia personal puede vivirse desde cierta distancia de observación. Tiendes a "
    "analizar los patrones familiares intentando comprenderlos desde una perspectiva amplia, "
    "identificando aquello que deseas conservar y aquello que necesita evolucionar. Las raíces "
    "se convierten en algo que puedes revisar y transformar.\n\n"

    "Esta posición favorece la creación de hogares poco convencionales, donde exista espacio "
    "para la individualidad de cada persona. Necesitas sentir que el entorno íntimo respeta "
    "la libertad, las diferencias y la posibilidad de que cada miembro pueda desarrollarse "
    "sin que las expectativas rígidas condicionen su crecimiento.\n\n"

    "La sensación de pertenencia puede encontrarse también en comunidades elegidas, grupos de "
    "afinidad o personas con quienes compartes una visión común. Para ti, la familia puede "
    "trascender los vínculos tradicionales y adquirir formas más amplias basadas en la conexión "
    "con valores compartidos.\n\n"

    "El desafío aparece cuando la necesidad de independencia genera cierta desconexión emocional "
    "o dificultad para implicarte plenamente en la intimidad familiar. Puede existir tendencia "
    "a observar los sentimientos desde la mente en lugar de permitirte experimentarlos "
    "directamente, especialmente cuando aparecen emociones intensas.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la libertad y la pertenencia "
    "no son opuestas. Cuando aceptas tus raíces sin sentir que limitan tu individualidad, "
    "construyes un hogar interno basado en la autenticidad, la aceptación y la libertad de ser "
    "quien realmente eres."
),


"Piscis": (
    "Cuando Piscis ocupa la cúspide de la Casa 4, las raíces y el sentido de pertenencia se "
    "construyen a través de la sensibilidad, la conexión emocional y una profunda percepción "
    "de los vínculos invisibles que unen a las personas. El hogar representa un espacio de "
    "recogimiento, intuición y conexión con aquello que proporciona una sensación profunda "
    "de unidad.\n\n"

    "La relación con la historia personal suele estar cargada de sensibilidad e imaginación. "
    "Puedes conservar recuerdos, emociones y sensaciones de manera muy intensa, incluso "
    "aquellas experiencias que otras personas considerarían pequeñas o difíciles de explicar. "
    "El pasado permanece vivo como una fuente de significado y comprensión.\n\n"

    "Esta posición favorece una gran capacidad para crear espacios acogedores donde las personas "
    "puedan sentirse aceptadas y comprendidas. Existe una sensibilidad especial hacia las "
    "necesidades emocionales del entorno y una disposición natural a ofrecer apoyo, escucha y "
    "compasión.\n\n"

    "Las raíces pueden estar relacionadas con una dimensión simbólica o espiritual de la vida. "
    "Necesitas sentir que tu hogar no solo cubre necesidades prácticas, sino que también alimenta "
    "tu mundo interior. La música, el arte, la naturaleza o los espacios de silencio e intimidad pueden "
    "tener un valor especialmente reparador.\n\n"

    "El desafío aparece cuando la sensibilidad hace difícil diferenciar entre tus propias "
    "emociones y las que pertenecen al entorno familiar. Puede existir tendencia a absorber "
    "demasiado las necesidades de los demás, idealizar el pasado o evitar conflictos para "
    "preservar una sensación de paz.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera conexión no "
    "requiere perder tus propios límites. Cuando integras sensibilidad y claridad, construyes "
    "un hogar interno donde la empatía puede expresarse sin sacrificio y donde tus raíces se "
    "convierten en una fuente profunda de inspiración y serenidad."
),

}



CASA_5 = {

"Aries": (
    "Cuando Aries ocupa la cúspide de la Casa 5, la creatividad se expresa a través de la "
    "acción, la iniciativa y la necesidad de experimentar directamente aquello que nace de "
    "ti. Existe un impulso natural a crear sin esperar demasiado tiempo a que todo esté "
    "perfectamente preparado. La inspiración aparece cuando puedes moverte, probar y "
    "descubrir mediante la experiencia.\n\n"

    "Tu manera de expresarte suele ser espontánea y llena de energía. Necesitas sentir que "
    "aquello que haces contiene una parte auténtica de ti y que puedes desarrollar tus ideas "
    "con libertad. Los proyectos personales adquieren fuerza cuando representan un desafío, "
    "una aventura o una oportunidad para descubrir de lo que eres capaz.\n\n"

    "Esta posición favorece una gran capacidad para iniciar procesos creativos. Sueles aportar "
    "entusiasmo, valentía y una disposición natural para abrir caminos donde todavía no existe "
    "una dirección clara. La creatividad no nace tanto de la planificación como del impulso "
    "de comenzar y descubrir qué puede surgir durante el recorrido.\n\n"

    "El disfrute está relacionado con la sensación de movimiento y conquista. Necesitas "
    "actividades que despierten tu vitalidad y te permitan sentir que estás creciendo. Los "
    "juegos, los retos y las experiencias donde puedas poner a prueba tus capacidades suelen "
    "convertirse en fuentes importantes de motivación.\n\n"

    "El desafío aparece cuando la necesidad de novedad hace difícil mantener el compromiso con "
    "aquello que requiere tiempo y maduración. Puede surgir impaciencia si los resultados no "
    "aparecen rápidamente o tendencia a abandonar una creación justo cuando comienza la fase "
    "de consolidación. En algunos momentos, competir o demostrar puede sustituir al verdadero "
    "placer de crear.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la creatividad no solo está "
    "en iniciar, sino también en aprender a sostener aquello que has encendido. Cuando integras "
    "impulso y perseverancia, tu capacidad creadora se convierte en una fuerza capaz de abrir "
    "nuevos caminos e inspirar movimiento en quienes te rodean."
),


"Tauro": (
    "Cuando Tauro ocupa la cúspide de la Casa 5, la creatividad se desarrolla a través de la "
    "paciencia, la sensibilidad y la capacidad para transformar una idea inicial en algo "
    "concreto y duradero. Existe una necesidad de crear desde el disfrute, conectando con los "
    "sentidos y permitiendo que cada proceso madure a su propio ritmo.\n\n"

    "Tu expresión personal suele buscar calidad, belleza y coherencia. No acostumbras a crear "
    "desde la urgencia, sino desde una relación profunda con aquello que deseas desarrollar. "
    "La creatividad aparece cuando puedes dedicar tiempo, atención y cuidado a algo que "
    "consideras verdaderamente valioso.\n\n"

    "Esta posición favorece una gran capacidad artística o creativa vinculada a lo tangible. "
    "Puedes encontrar inspiración en la naturaleza, la materia, la estética, la música, la "
    "cocina, la artesanía o cualquier actividad donde sea posible dar forma visible a una "
    "sensación interna.\n\n"

    "El disfrute ocupa un lugar importante en tu manera de vivir. Necesitas experiencias que "
    "aporten placer, calma y una sensación de conexión con la vida. La creatividad se alimenta "
    "cuando permites que el proceso sea tan importante como el resultado final.\n\n"

    "El desafío aparece cuando el deseo de seguridad dificulta arriesgarte o experimentar con "
    "formas nuevas de expresión. Puede existir resistencia a mostrar algo hasta sentir que "
    "está suficientemente desarrollado, retrasando la manifestación de talentos que necesitan "
    "precisamente ser compartidos para crecer.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera creación no "
    "depende de alcanzar una forma perfecta, sino de permitir que aquello que nace de ti "
    "encuentre su propia expresión. Cuando unes paciencia y apertura, tu creatividad puede "
    "convertirse en una fuente estable de belleza y disfrute."
),


"Géminis": (
    "Cuando Géminis ocupa la cúspide de la Casa 5, la creatividad surge a través de la "
    "curiosidad, la experimentación y la capacidad para conectar ideas diferentes. Existe una "
    "necesidad natural de jugar con posibilidades, explorar caminos alternativos y descubrir "
    "nuevas formas de expresión mediante la palabra, el conocimiento o el intercambio.\n\n"

    "Tu manera de crear suele ser dinámica y cambiante. Puedes sentir inspiración a través de "
    "muchas fuentes diferentes y disfrutar especialmente del proceso de descubrir, aprender y "
    "compartir aquello que vas comprendiendo. La creatividad se activa cuando existe libertad "
    "mental y espacio para probar sin que una única dirección limite tu expresión.\n\n"

    "Esta posición favorece la expresión comunicativa. La escritura, la enseñanza, los medios "
    "de comunicación, las conversaciones o cualquier actividad donde las ideas puedan circular "
    "pueden convertirse en canales naturales para desarrollar tu potencial creativo.\n\n"

    "El juego ocupa un papel importante en tu desarrollo. Necesitas mantener viva la curiosidad "
    "y sentir que la vida continúa ofreciendo estímulos nuevos. La diversión aparece cuando "
    "puedes aprender algo mientras disfrutas, mezclando conocimiento y espontaneidad.\n\n"

    "El desafío aparece cuando la abundancia de intereses dificulta profundizar en una creación "
    "concreta. Puede surgir dispersión, comenzar muchos proyectos y dejar algunos sin terminar, "
    "o buscar constantemente una nueva idea antes de haber dado suficiente espacio a la actual. "
    "En ocasiones también puede existir tendencia a analizar demasiado la creatividad en lugar "
    "de entregarte a ella.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la curiosidad alcanza su "
    "máximo potencial cuando encuentra una dirección donde concentrarse. Cuando integras "
    "variedad y profundidad, tu creatividad se convierte en una herramienta poderosa para "
    "conectar ideas, personas y nuevas formas de comprender la realidad."
),


"Cáncer": (
    "Cuando Cáncer ocupa la cúspide de la Casa 5, la creatividad nace de la sensibilidad, "
    "la memoria emocional y la capacidad para expresar aquello que sientes profundamente. "
    "Existe una necesidad de crear desde un lugar íntimo, conectando con experiencias, "
    "recuerdos y emociones que forman parte de tu mundo interior.\n\n"

    "Tu expresión personal suele estar vinculada a aquello que despierta una respuesta "
    "emocional. La creatividad aparece cuando puedes transmitir algo que tenga significado, "
    "que conecte con otras personas o que conserve una parte de tu historia. Crear no es "
    "solo producir algo nuevo, sino dar forma a aquello que llevas dentro.\n\n"

    "Esta posición favorece una gran imaginación y una sensibilidad especial para captar "
    "matices emocionales. Puedes encontrar inspiración en la infancia, la familia, las "
    "tradiciones, la naturaleza o cualquier experiencia que despierte una sensación de "
    "pertenencia. Tu creatividad suele tener una cualidad protectora y capaz de nutrir a "
    "quienes la reciben.\n\n"

    "El disfrute aparece cuando puedes expresarte en espacios donde existe confianza y "
    "seguridad emocional. Necesitas sentir que aquello que compartes es recibido con "
    "sensibilidad y comprensión. Los proyectos personales adquieren fuerza cuando contienen "
    "un componente afectivo o cuando permiten cuidar, acompañar o generar conexión.\n\n"

    "El desafío aparece cuando el miedo a mostrar tu mundo interno limita la expresión "
    "creativa. Puede existir tendencia a proteger demasiado aquello que nace de ti, esperando "
    "un momento perfecto o una respuesta emocional segura antes de compartirlo. En algunos "
    "casos, la nostalgia puede mantener la conexión con formas antiguas de expresión que ya "
    "necesitan evolucionar.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la vulnerabilidad es una "
    "fuente de creación y no una debilidad. Cuando permites que tus emociones encuentren una "
    "forma de expresión libre, tu creatividad se convierte en un puente capaz de generar "
    "profunda conexión humana."
),


"Leo": (
    "Cuando Leo ocupa la cúspide de la Casa 5, la creatividad se convierte en una de las "
    "principales vías de expresión de la identidad. Existe una necesidad natural de crear, "
    "mostrar y compartir aquello que lleva tu sello personal. Esta posición busca una vida "
    "donde exista espacio para brillar desde la autenticidad y desarrollar los talentos "
    "propios con confianza.\n\n"

    "Tu manera de expresarte suele ser cálida, generosa y llena de presencia. Necesitas "
    "sentir que aquello que haces tiene una parte de ti y que puedes aportar algo único. "
    "La creatividad no se limita a una actividad concreta; puede aparecer en la forma de "
    "liderar, inspirar, enseñar o dar vida a cualquier proyecto personal.\n\n"

    "Esta posición favorece una gran capacidad para conectar con el disfrute y con la alegría "
    "de crear. Existe una relación especial con el juego, la expresión artística y todas "
    "aquellas experiencias que permiten recuperar la espontaneidad y el contacto con el niño "
    "interior. Crear es una manera de celebrar la propia existencia.\n\n"

    "Los proyectos personales suelen necesitar reconocimiento y espacio para desarrollarse. "
    "Cuando sientes que tu aportación es valorada, aparece una enorme capacidad para entregar "
    "energía, entusiasmo y dedicación. Puedes convertirte en una fuente de inspiración para "
    "otras personas al mostrarles que también ellas pueden desarrollar sus talentos.\n\n"

    "El desafío aparece cuando la necesidad de reconocimiento externo comienza a condicionar "
    "la expresión creativa. Puede surgir miedo a no destacar, comparación con otras personas "
    "o dificultad para disfrutar del proceso si no existe una respuesta positiva del entorno. "
    "La creatividad pierde fuerza cuando necesita demostrar constantemente su valor.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera expresión "
    "personal nace cuando creas por amor a aquello que haces, no únicamente para recibir reconocimiento. "
    "Cuando integras humildad y confianza, tu capacidad creativa se convierte en una fuerza "
    "radiante que ilumina sin necesidad de buscar aprobación."
),


"Virgo": (
    "Cuando Virgo ocupa la cúspide de la Casa 5, la creatividad se desarrolla a través de la "
    "observación, la precisión y el deseo de perfeccionar aquello que haces. Existe una "
    "tendencia natural a analizar los procesos creativos, buscando comprender cómo mejorar "
    "una idea hasta convertirla en algo útil, coherente y bien elaborado.\n\n"

    "Tu expresión personal suele estar relacionada con la dedicación y el cuidado por los "
    "detalles. No acostumbras a crear únicamente por impulso; necesitas sentir que aquello "
    "que desarrollas tiene una función, aporta valor o responde a una necesidad concreta. "
    "La creatividad encuentra sentido cuando puede aplicarse de manera práctica.\n\n"

    "Esta posición favorece una gran capacidad para desarrollar habilidades mediante la "
    "práctica constante. Puedes destacar en actividades donde la técnica, la organización "
    "o la atención minuciosa sean importantes. Tu talento crece con el tiempo porque sabes "
    "observar, corregir y mejorar cada nueva versión del proceso.\n\n"

    "El disfrute aparece cuando sientes que estás aprendiendo y evolucionando. Crear puede "
    "convertirse en una vía de crecimiento personal, ya que cada proyecto representa una "
    "oportunidad para descubrir nuevas capacidades y aportar algo más refinado al mundo.\n\n"

    "El desafío aparece cuando la exigencia interna bloquea la espontaneidad. Puede surgir "
    "miedo a equivocarte, sensación de que nunca está suficientemente bien o dificultad para "
    "mostrar algo antes de considerarlo terminado. La búsqueda de calidad puede convertirse "
    "en una barrera si impide experimentar.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la creatividad también "
    "necesita espacio para jugar y equivocarse. Cuando integras precisión y libertad, tu "
    "capacidad creadora alcanza una expresión especialmente valiosa: transformar ideas en "
    "realidades concretas con sensibilidad y maestría."
),


"Libra": (
    "Cuando Libra ocupa la cúspide de la Casa 5, la creatividad se expresa a través de la "
    "armonía, la belleza y la capacidad para crear algo que conecte con otras personas. "
    "Existe una necesidad natural de encontrar formas de expresión equilibradas, donde la "
    "sensibilidad estética y la relación con el entorno tengan un papel importante.\n\n"

    "Tu manera de crear suele estar influida por la percepción de lo bello, lo agradable y "
    "lo que puede generar encuentro. La creatividad aparece con fuerza cuando puedes "
    "compartir ideas, colaborar con otras personas o participar en proyectos donde exista "
    "intercambio y enriquecimiento mutuo.\n\n"

    "Esta posición favorece una gran sensibilidad artística y una capacidad especial para "
    "combinar elementos diferentes hasta encontrar una composición equilibrada. La música, "
    "el diseño, la imagen, las relaciones humanas o cualquier actividad donde exista una "
    "búsqueda de armonía pueden convertirse en canales naturales de expresión.\n\n"

    "El disfrute está relacionado con la conexión y la belleza compartida. Necesitas "
    "experiencias donde puedas celebrar la vida junto a otras personas, creando espacios "
    "agradables y significativos. Los proyectos adquieren mayor fuerza cuando existe un "
    "sentido de cooperación y una visión común.\n\n"

    "El desafío aparece cuando la necesidad de agradar condiciona la expresión personal. "
    "Puede existir tendencia a adaptar demasiado tu creatividad a lo que crees que otros "
    "esperan o dificultad para mostrar una visión propia si existe riesgo de generar "
    "desacuerdo. En ocasiones puedes buscar la forma perfecta antes de permitir que algo "
    "simplemente nazca.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera armonía no "
    "surge de evitar diferencias, sino de integrarlas. Cuando confías en tu propia mirada, "
    "tu creatividad se convierte en una forma de unir belleza, sensibilidad y autenticidad."
),


"Escorpio": (
    "Cuando Escorpio ocupa la cúspide de la Casa 5, la creatividad surge desde la profundidad, "
    "la intensidad emocional y la necesidad de expresar aquello que transforma. Existe un "
    "impulso natural a crear desde experiencias significativas, explorando aspectos de la "
    "vida que invitan a mirar más allá de la superficie.\n\n"

    "Tu expresión personal suele estar marcada por una gran carga emocional y simbólica. "
    "No acostumbras a crear únicamente para entretener, sino para transmitir algo que tenga "
    "fuerza, significado o capacidad de generar un cambio. La creatividad puede convertirse "
    "en una vía para comprenderte y atravesar procesos internos importantes.\n\n"

    "Esta posición favorece una gran capacidad para investigar, profundizar y transformar "
    "experiencias complejas en formas de expresión. El arte, la escritura, la psicología, "
    "la investigación o cualquier actividad donde puedas revelar lo oculto pueden convertirse "
    "en espacios naturales para desarrollar tu potencial.\n\n"

    "El disfrute aparece cuando existe una implicación profunda. Necesitas sentir que aquello "
    "a lo que dedicas energía tiene autenticidad y que conecta con algo verdadero dentro de ti. "
    "Los proyectos superficiales pueden dejarte indiferente; buscas experiencias capaces de "
    "despertar pasión y compromiso.\n\n"

    "El desafío aparece cuando la intensidad emocional dificulta disfrutar del proceso. Puede "
    "surgir miedo a mostrar aquello que creas por temor a revelar demasiado de tu mundo interior, "
    "o una tendencia a controlar excesivamente la expresión para proteger tu vulnerabilidad. También "
    "puede aparecer apego a una forma de crear que ya necesita transformarse.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera fuerza creativa "
    "nace al permitir la transformación. Cuando confías en el proceso y aceptas mostrar tu "
    "profundidad, tu expresión puede convertirse en una fuente de transformación e inspiración "
    "para ti y para quienes reciben tu creación."
),


"Sagitario": (
    "Cuando Sagitario ocupa la cúspide de la Casa 5, la creatividad se expresa a través de la "
    "exploración, la aventura y la necesidad de ampliar horizontes. Existe un impulso natural "
    "a experimentar nuevas formas de expresión, aprender constantemente y encontrar un sentido "
    "más amplio a aquello que creas.\n\n"

    "Tu manera de crear suele estar vinculada a la curiosidad y al descubrimiento. La inspiración "
    "puede aparecer a través de viajes, estudios, culturas diferentes o experiencias que te "
    "permiten observar la realidad desde perspectivas nuevas. Crear es una forma de explorar "
    "el mundo y comprender mejor la vida.\n\n"

    "Esta posición favorece una expresión generosa, entusiasta y capaz de transmitir ideas "
    "amplias. Puedes destacar en actividades relacionadas con la enseñanza, la comunicación, "
    "la divulgación o cualquier ámbito donde puedas compartir conocimientos y despertar "
    "nuevas posibilidades en otras personas.\n\n"

    "El disfrute aparece cuando existe libertad para experimentar. Necesitas sentir que tus "
    "proyectos mantienen vivo el entusiasmo y que cada creación abre una puerta hacia algo "
    "nuevo. La rutina excesiva puede apagar la inspiración si no existe una sensación de "
    "crecimiento.\n\n"

    "El desafío aparece cuando la búsqueda constante de nuevas experiencias dificulta terminar "
    "o consolidar aquello que empiezas. Puede existir tendencia a enamorarte más de la idea "
    "inicial que del proceso necesario para desarrollarla completamente. En algunos momentos "
    "también puede aparecer exceso de confianza o dificultad para aceptar límites.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera expansión no "
    "depende de comenzar siempre algo nuevo, sino de profundizar en aquello que realmente "
    "aporta sentido. Cuando integras entusiasmo y compromiso, tu creatividad se convierte en "
    "una fuente de inspiración y crecimiento continuo."
),


"Capricornio": (
    "Cuando Capricornio ocupa la cúspide de la Casa 5, la creatividad se desarrolla mediante "
    "la disciplina, la paciencia y la capacidad para convertir una inspiración inicial en algo "
    "estructurado y duradero. Existe una tendencia natural a tomarte en serio aquello que "
    "creas y a buscar resultados que puedan mantenerse en el tiempo.\n\n"

    "Tu expresión personal suele madurar con los años. Puede que no sientas la necesidad de "
    "mostrar tus talentos inmediatamente, prefiriendo desarrollar experiencia, conocimiento "
    "y dominio antes de exponer tu trabajo. La creatividad se fortalece a través del compromiso "
    "y la práctica constante.\n\n"

    "Esta posición favorece la capacidad para construir proyectos sólidos. Puedes destacar en "
    "ámbitos donde sea necesario combinar visión creativa con organización, responsabilidad y "
    "perseverancia. Tu talento reside muchas veces en dar forma concreta a ideas que necesitan "
    "estructura para manifestarse.\n\n"

    "El disfrute aparece cuando percibes progreso y evolución. Necesitas sentir que aquello que "
    "haces tiene propósito y que tu esfuerzo conduce hacia una construcción significativa. La "
    "creatividad se convierte en un camino de realización personal y desarrollo de capacidades.\n\n"

    "El desafío aparece cuando la exigencia o el miedo al error bloquean la espontaneidad. "
    "Puede existir dificultad para jugar, improvisar o crear simplemente por placer, como si "
    "todo tuviera que responder a una finalidad concreta. En ocasiones puedes juzgar demasiado "
    "pronto tus propias ideas antes de permitirles crecer.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la creatividad también "
    "necesita espacio para la alegría y la experimentación. Cuando integras estructura y "
    "libertad, eres capaz de crear proyectos con profundidad, madurez y una gran "
    "capacidad de permanencia."
),


"Acuario": (
    "Cuando Acuario ocupa la cúspide de la Casa 5, la creatividad se expresa a través de la "
    "originalidad, la innovación y la necesidad de encontrar formas diferentes de manifestar "
    "quién eres. Existe una inclinación natural a cuestionar los modelos tradicionales y "
    "explorar caminos creativos poco habituales.\n\n"

    "Tu expresión personal necesita libertad. Las ideas aparecen cuando puedes pensar de "
    "manera independiente, experimentar con libertad y conectar conceptos que para "
    "otras personas podrían parecer separados. La creatividad surge como una forma de aportar "
    "algo nuevo y ampliar posibilidades.\n\n"

    "Esta posición favorece una mirada innovadora y una capacidad especial para imaginar "
    "futuros diferentes. Puedes sentir afinidad por la tecnología, los grupos creativos, las "
    "nuevas corrientes culturales o cualquier espacio donde sea posible transformar la manera "
    "habitual de hacer las cosas.\n\n"

    "El disfrute aparece cuando existe sorpresa, descubrimiento y sensación de libertad. "
    "Necesitas proyectos que despierten tu curiosidad y permitan que tu individualidad se "
    "exprese sin quedar reducida a expectativas externas.\n\n"

    "El desafío aparece cuando la necesidad de diferencia puede alejarte del disfrute sencillo "
    "o generar rechazo hacia formas más tradicionales de expresión. Puede existir tendencia a "
    "priorizar lo novedoso sobre aquello que realmente tiene valor, o cierta distancia emocional "
    "respecto a la propia creatividad.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera originalidad "
    "no consiste únicamente en hacer algo distinto, sino en aportar una visión auténtica. "
    "Cuando integras innovación y conexión emocional, tu creatividad puede convertirse en "
    "una fuerza transformadora para ti y para tu entorno."
),


"Piscis": (
    "Cuando Piscis ocupa la cúspide de la Casa 5, la creatividad se expresa a través de la "
    "imaginación, la sensibilidad y la capacidad para conectar con dimensiones profundas de "
    "la experiencia humana. Existe una facilidad natural para crear desde la intuición, "
    "percibiendo matices que no siempre pueden explicarse con palabras.\n\n"

    "Tu expresión personal suele estar vinculada al mundo simbólico, emocional y espiritual. "
    "La inspiración puede aparecer a través de sueños, sensaciones, imágenes internas o "
    "experiencias que despiertan una conexión especial con algo que trasciende tu propia "
    "individualidad. "
    "Crear se convierte en una forma de traducir lo invisible.\n\n"

    "Esta posición favorece una gran sensibilidad artística y una capacidad para transmitir "
    "emociones universales. La música, el arte, la fotografía, la escritura o cualquier medio "
    "que permita expresar estados internos pueden convertirse en canales naturales de "
    "realización creativa.\n\n"

    "El disfrute aparece cuando puedes entregarte al proceso sin intentar controlarlo todo. "
    "Necesitas momentos de inspiración, silencio y conexión interior para permitir que las "
    "ideas encuentren su propia forma. La creatividad surge más fácilmente cuando existe "
    "espacio para la imaginación y la receptividad.\n\n"

    "El desafío aparece cuando la sensibilidad dificulta poner límites, terminar proyectos o "
    "dar una estructura concreta a las ideas. Puede existir tendencia a idealizar una creación "
    "sin pasar por la fase práctica necesaria para manifestarla, o a depender demasiado de la "
    "inspiración del momento.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la inspiración necesita un "
    "canal para expresarse. Cuando integras sensibilidad y estructura, tu creatividad puede "
    "convertirse en una vía profunda de conexión, belleza y transformación emocional."
),

}


CASA_6 = {

"Aries": (
    "Cuando Aries ocupa la cúspide de la Casa 6, la vida cotidiana necesita movimiento, "
    "iniciativa y sensación de acción constante. Existe una tendencia natural a afrontar las "
    "tareas diarias de manera directa, buscando resolver, avanzar y encontrar soluciones "
    "rápidas ante aquello que requiere atención. La rutina funciona mejor cuando incluye "
    "retos, autonomía y espacio para tomar decisiones propias.\n\n"

    "Tu relación con el trabajo cotidiano suele estar marcada por la capacidad de actuar "
    "con rapidez y poner en marcha procesos que permanecían bloqueados. Tiendes a responder "
    "bien ante situaciones que requieren energía, determinación o capacidad de reacción. "
    "La sensación de ser útil aparece especialmente cuando puedes intervenir de forma activa "
    "y comprobar que tus acciones generan un resultado concreto.\n\n"

    "Los hábitos necesitan mantenerse dinámicos para favorecer tu bienestar. Las rutinas "
    "excesivamente rígidas pueden generar sensación de limitación, mientras que los sistemas "
    "que incorporan movimiento, ejercicio o nuevos desafíos suelen ayudarte a mantener la "
    "motivación. Tu energía aumenta cuando sientes que estás construyendo algo y no simplemente "
    "repitiendo acciones automáticas.\n\n"

    "Esta posición favorece una actitud resolutiva frente a las responsabilidades diarias. "
    "Sueles tener facilidad para detectar qué necesita hacerse y actuar sin esperar demasiado "
    "tiempo. En entornos laborales puedes aportar iniciativa, capacidad de liderazgo y una "
    "gran energía para comenzar proyectos o mejorar procesos.\n\n"

    "El desafío aparece cuando la necesidad de actuar constantemente dificulta la paciencia "
    "o el descanso. Puede existir tendencia a sobrecargar la agenda, comenzar demasiadas "
    "tareas a la vez o ignorar señales del cuerpo cuando el impulso de avanzar es más fuerte "
    "que la necesidad de recuperar energía. La eficacia disminuye cuando todo depende de la "
    "urgencia y la reacción inmediata.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que el verdadero dominio de "
    "la energía no consiste solo en avanzar, sino también en aprender a regular el ritmo. "
    "Cuando integras iniciativa y constancia, conviertes tu capacidad de acción en una "
    "herramienta poderosa para construir bienestar y desarrollar una vida cotidiana más "
    "consciente."
),


"Tauro": (
    "Cuando Tauro ocupa la cúspide de la Casa 6, el bienestar se construye a través de la "
    "estabilidad, la constancia y la creación de ritmos sostenibles. Existe una necesidad "
    "natural de organizar la vida cotidiana de manera que aporte seguridad y permita avanzar "
    "sin depender de cambios constantes. Los hábitos adquieren valor cuando proporcionan "
    "equilibrio y continuidad.\n\n"

    "Tu relación con el trabajo diario suele caracterizarse por la paciencia y la capacidad "
    "para mantener el esfuerzo durante largos periodos de tiempo. No necesitas resultados "
    "inmediatos para comprometerte con una tarea; confías en que la dedicación constante "
    "produce frutos cuando existe una base sólida. Tu fortaleza aparece especialmente en "
    "procesos que requieren perseverancia.\n\n"

    "Los hábitos tienen un papel fundamental en tu bienestar. Las rutinas relacionadas con "
    "la alimentación, el descanso, el cuidado corporal o el contacto con la naturaleza "
    "pueden convertirse en fuentes importantes de equilibrio. Necesitas sentir que tu día "
    "a día tiene un ritmo humano, donde exista espacio para disfrutar además de cumplir.\n\n"

    "Esta posición favorece una gran capacidad para desarrollar habilidades prácticas y "
    "perfeccionar procesos con el tiempo. Sueles aportar fiabilidad, paciencia y una actitud "
    "constructiva en los entornos laborales. Cuando encuentras una forma de hacer las cosas "
    "que funciona, puedes mantenerla con gran dedicación.\n\n"

    "El desafío aparece cuando la búsqueda de estabilidad dificulta introducir cambios "
    "necesarios. Puede existir resistencia a modificar hábitos conocidos aunque ya no sean "
    "los más adecuados, o tendencia a permanecer en situaciones laborales simplemente porque "
    "ofrecen seguridad. La comodidad puede convertirse en un límite cuando impide evolucionar.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que una verdadera estabilidad "
    "incluye la capacidad de adaptarse. Cuando integras constancia y flexibilidad, tus hábitos "
    "se convierten en una base firme desde la que crecer, no en una estructura que limite tus "
    "posibilidades."
),


"Géminis": (
    "Cuando Géminis ocupa la cúspide de la Casa 6, la vida cotidiana necesita variedad, "
    "aprendizaje y movimiento mental para mantenerse equilibrada. Existe una tendencia "
    "natural a organizar las tareas mediante la información, la comunicación y la búsqueda "
    "constante de nuevas soluciones. La rutina funciona mejor cuando permite cierta "
    "flexibilidad y estimulación intelectual.\n\n"

    "Tu relación con el trabajo diario suele estar marcada por la capacidad de adaptarte "
    "rápidamente a diferentes tareas y contextos. Puedes desenvolverte bien en entornos "
    "donde sea necesario gestionar información, conectar personas o resolver problemas "
    "mediante la comunicación. La diversidad suele aumentar tu motivación.\n\n"

    "Los hábitos necesitan incorporar variedad para resultar sostenibles. Las rutinas "
    "demasiado repetitivas pueden generar aburrimiento o sensación de estancamiento, "
    "mientras que pequeños cambios y nuevos aprendizajes ayudan a mantener tu energía "
    "activa. El bienestar aparece cuando existe equilibrio entre estímulo y descanso mental.\n\n"

    "Esta posición favorece una gran capacidad para mejorar procesos mediante ideas nuevas. "
    "Puedes detectar rápidamente alternativas, encontrar información útil y adaptar métodos "
    "existentes para hacerlos más eficientes. Tu mente se convierte en una herramienta "
    "importante dentro del trabajo cotidiano.\n\n"

    "El desafío aparece cuando la dispersión dificulta establecer una organización estable. "
    "Puede existir tendencia a comenzar muchas tareas sin terminarlas, cambiar de método "
    "constantemente o vivir con demasiados estímulos simultáneos. En algunos momentos la "
    "mente puede permanecer activa incluso cuando el cuerpo necesita descanso.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la flexibilidad alcanza "
    "su máximo potencial cuando encuentra una estructura que la sostenga. Cuando integras "
    "curiosidad y disciplina, desarrollas una forma de trabajar ágil, inteligente y capaz "
    "de adaptarse sin perder dirección."
),


"Cáncer": (
    "Cuando Cáncer ocupa la cúspide de la Casa 6, el bienestar cotidiano se construye a "
    "través del cuidado emocional, la sensación de pertenencia y la creación de un entorno "
    "que te proporcione protección. La rutina no es únicamente una organización práctica, "
    "sino también un espacio donde recuperar equilibrio y nutrirte internamente.\n\n"

    "Tu relación con el trabajo diario suele estar influida por la necesidad de sentir que "
    "aquello que haces tiene un valor humano. Te implicas especialmente en tareas donde "
    "puedas cuidar, acompañar, proteger o aportar bienestar a otras personas. La sensación "
    "de utilidad aumenta cuando existe una conexión emocional con aquello a lo que dedicas "
    "tu energía.\n\n"

    "Los hábitos tienen una relación directa con tu estado emocional. Necesitas rutinas que "
    "respeten tus ritmos internos y que proporcionen sensación de seguridad. El descanso, la "
    "alimentación, el contacto con espacios acogedores y los momentos de recogimiento pueden "
    "ser fundamentales para mantener tu equilibrio.\n\n"

    "Esta posición favorece una gran capacidad para percibir las necesidades del entorno y "
    "responder con sensibilidad. En el trabajo puedes aportar empatía, memoria, intuición y "
    "una especial atención hacia aquello que otras personas pueden necesitar incluso antes "
    "de expresarlo.\n\n"

    "El desafío aparece cuando la implicación emocional con las responsabilidades diarias "
    "hace difícil separar lo propio de lo ajeno. Puede existir tendencia a cargar con "
    "problemas de otras personas, buscar seguridad a través de la utilidad o descuidar tus "
    "propias necesidades mientras atiendes las de los demás.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que cuidar también implica "
    "cuidarte. Cuando integras sensibilidad y límites saludables, tus hábitos se convierten "
    "en una fuente de equilibrio y tu capacidad de servicio puede expresarse sin agotamiento."
),


"Leo": (
    "Cuando Leo ocupa la cúspide de la Casa 6, el bienestar cotidiano se fortalece cuando "
    "puedes aportar creatividad, expresión personal y sentido de propósito a aquello que "
    "haces cada día. Existe una necesidad de sentir que tus tareas no son simplemente "
    "obligaciones, sino espacios donde puedes desarrollar tus talentos y aportar algo "
    "propio.\n\n"

    "Tu relación con el trabajo diario suele estar marcada por el deseo de implicarte con "
    "entusiasmo y dejar una huella personal. Necesitas sentir reconocimiento por aquello "
    "que aportas y encuentras mayor satisfacción cuando puedes asumir responsabilidades "
    "donde tu iniciativa y capacidad creativa tengan espacio para expresarse.\n\n"

    "Los hábitos relacionados con el bienestar funcionan mejor cuando incluyen disfrute y "
    "motivación. Las rutinas demasiado mecánicas pueden perder sentido si no existe una "
    "conexión con algo que te inspire. Necesitas sentir que el cuidado personal también "
    "es una forma de valorar tu propia existencia.\n\n"

    "Esta posición favorece una actitud generosa y vital dentro del entorno laboral. Puedes "
    "aportar entusiasmo, liderazgo y capacidad para animar a otras personas. Sueles rendir "
    "mejor cuando sientes que tu presencia es significativa y que tu contribución tiene un "
    "impacto visible.\n\n"

    "El desafío aparece cuando la necesidad de reconocimiento condiciona la relación con el "
    "trabajo o con los hábitos diarios. Puede surgir frustración si tus esfuerzos pasan "
    "desapercibidos o tendencia a asumir demasiadas responsabilidades para demostrar tu "
    "valor. El bienestar se debilita cuando la productividad sustituye al disfrute.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que el valor de lo que haces "
    "no depende únicamente de la respuesta externa. Cuando integras humildad y expresión "
    "personal, conviertes la vida cotidiana en un espacio donde crear, servir y desarrollarte "
    "van de la mano."
),


"Virgo": (
    "Cuando Virgo ocupa la cúspide de la Casa 6, esta área encuentra una expresión "
    "especialmente natural. Existe una conexión directa con la organización, la mejora "
    "continua y la necesidad de desarrollar hábitos que permitan funcionar de una manera "
    "más consciente y eficiente. La vida cotidiana se convierte en un espacio de aprendizaje "
    "y perfeccionamiento.\n\n"

    "Tu relación con el trabajo diario suele caracterizarse por la responsabilidad, la "
    "atención al detalle y la capacidad para detectar aquello que necesita ser ajustado. "
    "Tienes facilidad para comprender procesos, organizar recursos y aportar soluciones "
    "prácticas que mejoran el funcionamiento de cualquier entorno.\n\n"

    "Los hábitos adquieren una importancia fundamental en tu bienestar. Necesitas cierta "
    "estructura para sentir equilibrio, y las pequeñas acciones repetidas con constancia "
    "pueden convertirse en grandes herramientas de crecimiento. La alimentación, el orden, "
    "el descanso y el cuidado del cuerpo suelen beneficiarse de una atención consciente.\n\n"

    "Esta posición favorece una gran capacidad de servicio. Encuentras sentido cuando puedes "
    "ser útil, aportar conocimientos o mejorar una situación concreta. Tu forma de ayudar "
    "suele manifestarse mediante soluciones prácticas más que mediante grandes gestos, "
    "aportando precisión y eficacia allí donde hacen falta.\n\n"

    "El desafío aparece cuando la búsqueda de mejora se transforma en exigencia permanente. "
    "Puede surgir autocrítica excesiva, preocupación por pequeños errores o dificultad para "
    "aceptar que algunos procesos necesitan tiempo y margen de imperfección. El deseo de "
    "hacerlo bien puede convertirse en una fuente de tensión.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera eficacia "
    "incluye aceptación y equilibrio. Cuando integras disciplina y flexibilidad, desarrollas "
    "hábitos sostenibles que no solo mejoran tu rendimiento, sino también tu relación contigo."
),


"Libra": (
    "Cuando Libra ocupa la cúspide de la Casa 6, el bienestar cotidiano se construye a "
    "través del equilibrio, la armonía y la calidad de las relaciones que forman parte de "
    "la vida diaria. Existe una necesidad de que el entorno donde trabajas o desarrollas "
    "tus rutinas sea agradable, cooperativo y esté basado en el respeto mutuo. La forma en "
    "que organizas tu día influye directamente en tu sensación de bienestar.\n\n"

    "Tu relación con el trabajo suele enriquecerse cuando existe colaboración y posibilidad "
    "de intercambiar ideas con otras personas. Tiendes a aportar diplomacia, capacidad para "
    "mediar y una sensibilidad especial para crear ambientes donde las personas puedan "
    "funcionar mejor juntas. Las tareas realizadas en aislamiento prolongado pueden perder "
    "motivación si no existe una dimensión relacional.\n\n"

    "Los hábitos necesitan incorporar belleza, equilibrio y momentos de recuperación. Tu "
    "bienestar aumenta cuando encuentras una relación armónica entre esfuerzo y descanso, "
    "responsabilidad y disfrute. Los espacios agradables, el cuidado estético del entorno y "
    "las actividades que favorecen la calma pueden tener un papel importante en tu equilibrio "
    "diario.\n\n"

    "Esta posición favorece una gran capacidad para comprender las necesidades de quienes te "
    "rodean y adaptar tu forma de colaborar. En el ámbito laboral puedes destacar creando "
    "puentes, facilitando acuerdos y aportando una mirada que contempla diferentes puntos "
    "de vista antes de tomar decisiones.\n\n"

    "El desafío aparece cuando el deseo de mantener la armonía lleva a evitar conversaciones "
    "necesarias o a asumir más responsabilidades de las que corresponden. Puede existir "
    "tendencia a priorizar el bienestar de los demás antes que el propio, generando cierto "
    "desequilibrio entre dar y recibir. También puede resultar difícil establecer límites "
    "claros cuando existe temor a generar conflicto.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que el verdadero equilibrio "
    "comienza por incluir tus propias necesidades. Cuando aprendes a cooperar sin renunciar "
    "a tu criterio, construyes rutinas más saludables y relaciones laborales donde la "
    "armonía nace de la autenticidad."
),


"Escorpio": (
    "Cuando Escorpio ocupa la cúspide de la Casa 6, la vida cotidiana se convierte en un "
    "espacio de transformación profunda. Existe una tendencia a implicarte intensamente en "
    "aquello que haces, buscando comprender los procesos ocultos y mejorar aquello que no "
    "funciona desde la raíz. Las rutinas adquieren sentido cuando están conectadas con una "
    "evolución personal real.\n\n"

    "Tu relación con el trabajo suele estar marcada por la concentración, la entrega y una "
    "gran capacidad para afrontar situaciones complejas. Puedes desarrollar una notable "
    "fortaleza en contextos donde es necesario investigar, resolver problemas o acompañar "
    "procesos de cambio. No sueles conformarte con soluciones superficiales cuando percibes "
    "que existe algo más profundo que necesita ser atendido.\n\n"

    "Los hábitos relacionados con el bienestar pueden vivir etapas de transformación "
    "importante. Es posible que atravieses procesos donde necesitas cambiar completamente "
    "determinadas costumbres para recuperar equilibrio. Tu relación con el cuerpo y con la "
    "salud suele beneficiarse cuando existe una comprensión profunda de las causas que hay "
    "detrás de aquello que necesita ser modificado.\n\n"

    "Esta posición aporta una gran capacidad de resistencia y compromiso. Cuando encuentras "
    "un propósito que consideras importante, puedes dedicar una enorme cantidad de energía "
    "hasta alcanzar aquello que buscas. Tu intensidad puede convertirse en una herramienta "
    "extraordinaria para superar dificultades y regenerar situaciones estancadas.\n\n"

    "El desafío aparece cuando esa intensidad se convierte en exceso de control, obsesión o "
    "dificultad para descansar. Puede existir tendencia a mantener una vigilancia constante "
    "sobre todo aquello que debe mejorar, olvidando que algunos procesos también necesitan "
    "espacio, confianza y tiempo para desarrollarse.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la transformación más "
    "profunda nace de la colaboración con los procesos naturales de la vida. Cuando integras "
    "disciplina y capacidad de soltar, tus rutinas se convierten en una vía de regeneración "
    "y crecimiento consciente."
),


"Sagitario": (
    "Cuando Sagitario ocupa la cúspide de la Casa 6, el bienestar cotidiano necesita incluir "
    "aprendizaje, movimiento y sensación de crecimiento. Las rutinas demasiado rígidas pueden "
    "resultar limitantes si no dejan espacio para explorar, descubrir nuevas formas de hacer "
    "las cosas o ampliar conocimientos. La vida diaria encuentra sentido cuando mantiene una "
    "dimensión de expansión.\n\n"

    "Tu relación con el trabajo suele enriquecerse cuando puedes desarrollar ideas, aprender "
    "constantemente o sentir que aquello que haces tiene una finalidad más amplia. Necesitas "
    "comprender el propósito de tus tareas y conectar la actividad cotidiana con una visión "
    "que vaya más allá de la simple obligación.\n\n"

    "Los hábitos funcionan mejor cuando incluyen variedad y libertad dentro de cierta "
    "estructura. Puedes beneficiarte de rutinas que permitan movimiento, contacto con nuevos "
    "entornos o incorporación continua de conocimientos. El aprendizaje y la exploración "
    "pueden convertirse en fuentes importantes de equilibrio.\n\n"

    "Esta posición favorece una actitud positiva frente a los desafíos diarios. Sueles "
    "encontrar oportunidades de crecimiento en las experiencias comunes y puedes aportar "
    "entusiasmo al entorno laboral. Tu capacidad para ver posibilidades amplias ayuda a "
    "mantener la motivación incluso cuando aparecen dificultades.\n\n"

    "El desafío aparece cuando la necesidad de expansión dificulta sostener hábitos constantes "
    "o aceptar tareas repetitivas que también forman parte del proceso. Puede surgir cierta "
    "inquietud frente a la rutina o tendencia a buscar siempre una nueva dirección antes de "
    "consolidar aquello que ya está funcionando.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la libertad también puede "
    "existir dentro de una estructura elegida conscientemente. Cuando integras entusiasmo y "
    "compromiso, conviertes las tareas diarias en un camino de aprendizaje y desarrollo "
    "personal."
),


"Capricornio": (
    "Cuando Capricornio ocupa la cúspide de la Casa 6, el bienestar cotidiano se construye "
    "mediante la disciplina, la responsabilidad y la capacidad para desarrollar sistemas "
    "eficaces. Existe una tendencia natural a comprender que los resultados importantes "
    "requieren constancia, por lo que las pequeñas acciones sostenidas en el tiempo adquieren "
    "un gran valor.\n\n"

    "Tu relación con el trabajo suele estar marcada por el compromiso y la perseverancia. "
    "Puedes asumir responsabilidades con seriedad y desarrollar una gran capacidad para "
    "organizar procesos complejos. Te resulta natural buscar métodos que permitan mejorar la "
    "eficiencia y alcanzar objetivos concretos.\n\n"

    "Los hábitos representan una base fundamental para tu equilibrio. Necesitas cierta "
    "estructura para sentir que avanzas y puedes beneficiarte especialmente de rutinas "
    "planificadas que ayuden a distribuir adecuadamente tu energía. La constancia suele ser "
    "uno de tus mayores recursos para mantener el bienestar a largo plazo.\n\n"

    "Esta posición favorece una actitud madura hacia el servicio y las obligaciones diarias. "
    "Sueles comprender que incluso las tareas aparentemente pequeñas forman parte de una "
    "construcción mayor. Esa visión permite desarrollar una gran fiabilidad y capacidad para "
    "sostener compromisos importantes.\n\n"

    "El desafío aparece cuando la responsabilidad se convierte en una carga permanente o "
    "cuando la exigencia dificulta escuchar las necesidades del cuerpo y del mundo emocional. "
    "Puede existir tendencia a valorar el descanso únicamente cuando todo está terminado, "
    "aunque siempre haya nuevas obligaciones esperando.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera eficacia no "
    "consiste en hacer más, sino en aprender a administrar sabiamente la energía disponible. "
    "Cuando integras disciplina y cuidado personal, construyes una relación con el trabajo "
    "y las rutinas basada en la estabilidad y no en la exigencia."
),


"Acuario": (
    "Cuando Acuario ocupa la cúspide de la Casa 6, el bienestar cotidiano necesita "
    "desarrollarse de una manera libre, flexible y diferente a los modelos establecidos. "
    "Existe una tendencia natural a cuestionar las rutinas tradicionales y buscar sistemas "
    "propios que permitan organizar la vida de una forma más coherente con tus necesidades "
    "individuales.\n\n"

    "Tu relación con el trabajo suele enriquecerse cuando existe autonomía, innovación y "
    "espacio para aportar ideas originales. Las estructuras excesivamente rígidas pueden "
    "resultar limitantes si no permiten experimentar nuevas formas de resolver problemas o "
    "introducir mejoras. Necesitas sentir que aquello que haces contribuye a una evolución "
    "más amplia.\n\n"

    "Los hábitos relacionados con el bienestar funcionan mejor cuando incluyen variedad y "
    "posibilidad de adaptación. Es probable que necesites diseñar tus propias rutinas en lugar "
    "de seguir modelos establecidos, descubriendo qué formas de cuidado encajan realmente con "
    "tu manera particular de funcionar. La libertad dentro de la organización puede ser clave "
    "para mantener la constancia.\n\n"

    "Esta posición favorece una visión amplia de los procesos cotidianos. Puedes tener facilidad "
    "para detectar maneras diferentes de mejorar un sistema, optimizar recursos o introducir "
    "cambios que beneficien al conjunto. En el entorno laboral puedes aportar creatividad, "
    "objetividad y una mirada capaz de anticipar nuevas posibilidades.\n\n"

    "El desafío aparece cuando la necesidad de independencia dificulta sostener compromisos "
    "diarios o aceptar estructuras necesarias para determinados procesos. Puede surgir cierta "
    "resistencia hacia la repetición o la sensación de que cualquier rutina limita tu libertad. "
    "También puede existir tendencia a desconectarte de las señales más inmediatas del cuerpo "
    "por concentrar demasiado la atención en ideas o proyectos futuros.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera libertad no "
    "consiste en rechazar toda estructura, sino en crear aquellas que permiten desarrollar tu "
    "potencial. Cuando integras innovación y constancia, tus hábitos se convierten en una "
    "herramienta de evolución personal y colectiva."
),


"Piscis": (
    "Cuando Piscis ocupa la cúspide de la Casa 6, el bienestar cotidiano se construye a través "
    "de la sensibilidad, la conexión interior y la capacidad de adaptarte a los ritmos de la "
    "vida. Las rutinas necesitan tener un sentido más profundo que la simple organización, "
    "ya que buscas sentir que aquello que haces cada día está alineado con tus valores y con "
    "una percepción más amplia de la existencia.\n\n"

    "Tu relación con el trabajo suele enriquecerse cuando existe un componente humano, "
    "creativo o de servicio. Te implicas especialmente en actividades donde puedes acompañar, "
    "inspirar o aportar algo que tenga significado para otras personas. La sensación de "
    "propósito es un elemento esencial para mantener la motivación.\n\n"

    "Los hábitos necesitan adaptarse a tus ritmos internos. Puedes beneficiarte de prácticas "
    "que incluyan descanso consciente, espacios de silencio, creatividad o conexión con lo "
    "que te ayuda a recuperar equilibrio. Las rutinas demasiado exigentes o desconectadas de "
    "tus necesidades emocionales pueden generar sensación de agotamiento o pérdida de energía.\n\n"

    "Esta posición favorece una gran intuición para percibir el ambiente laboral y las "
    "necesidades de quienes te rodean. Puedes desarrollar una forma de servicio basada en la "
    "empatía, la comprensión y la capacidad para aportar calma en situaciones donde existe "
    "confusión o dificultad.\n\n"

    "El desafío aparece cuando la sensibilidad hace difícil establecer límites claros en las "
    "responsabilidades diarias. Puede existir tendencia a absorber tensiones del entorno, "
    "postergar tus propias necesidades o adaptarte demasiado a lo que otras personas esperan "
    "de ti. También puede resultar complicado mantener constancia cuando falta una conexión "
    "emocional con aquello que haces.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la sensibilidad necesita "
    "una estructura que la sostenga. Cuando integras inspiración y organización, desarrollas "
    "hábitos que respetan tu naturaleza y una forma de trabajar donde la entrega no implica "
    "perderte en el proceso."
),

}



CASA_7 = {

"Aries": (
    "Cuando Aries ocupa la cúspide de la Casa 7, los vínculos se viven como espacios de "
    "encuentro, movimiento y descubrimiento personal. Las relaciones importantes tienden a "
    "activar tu energía, impulsarte a crecer y mostrarte aspectos de ti que quizá no "
    "aparecerían en la experiencia individual. La otra persona se convierte en un estímulo que "
    "despierta acción y evolución.\n\n"

    "Necesitas relaciones donde exista autenticidad, espontaneidad y libertad para que cada "
    "persona pueda expresarse tal como es. La conexión suele fortalecerse cuando hay iniciativa, "
    "entusiasmo y una sensación de avanzar juntos hacia nuevas experiencias. Los vínculos "
    "demasiado pasivos o carentes de movimiento pueden generar sensación de estancamiento.\n\n"

    "Esta posición favorece una forma directa de relacionarte. Sueles valorar la sinceridad y "
    "la capacidad de afrontar las situaciones sin demasiados rodeos. Cuando existe un vínculo "
    "importante, tiendes a implicarte con intensidad y a defender aquello que consideras "
    "valioso dentro de la relación.\n\n"

    "Las asociaciones y colaboraciones pueden convertirse en motores de crecimiento. El "
    "encuentro con personas activas, independientes o con iniciativa puede abrirte caminos "
    "nuevos y ayudarte a desarrollar cualidades que necesitan expresarse a través del "
    "intercambio con otros.\n\n"

    "El desafío aparece cuando la necesidad de autonomía entra en conflicto con el compromiso "
    "relacional. Puede surgir impaciencia ante los ritmos de la otra persona, tendencia a "
    "querer imponer la propia dirección o dificultad para escuchar antes de actuar. En algunos "
    "momentos el vínculo puede convertirse en un espacio de lucha más que de cooperación.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que una relación no limita la "
    "individualidad, sino que puede convertirse en un espacio donde dos personas fuertes "
    "crecen juntas. Cuando integras iniciativa y escucha, construyes vínculos basados en la "
    "pasión, la sinceridad y el respeto mutuo."
),


"Tauro": (
    "Cuando Tauro ocupa la cúspide de la Casa 7, los vínculos importantes buscan estabilidad, "
    "confianza y una base sólida sobre la que poder crecer. Las relaciones adquieren valor "
    "cuando transmiten seguridad, continuidad y una sensación de construcción compartida. "
    "Tiendes a valorar los compromisos que pueden desarrollarse con tiempo y profundidad, "
    "evitando aquello que resulta demasiado cambiante o imprevisible.\n\n"

    "Necesitas relaciones donde exista presencia, lealtad y una expresión concreta del afecto. "
    "Las palabras tienen importancia, pero los hechos suelen ser la verdadera medida del "
    "vínculo. La confianza se construye a través de la constancia, de los pequeños gestos "
    "cotidianos y de la sensación de que la otra persona permanece disponible cuando es "
    "necesario.\n\n"

    "Esta posición favorece una gran capacidad para sostener relaciones a largo plazo. Cuando "
    "eliges compartir tu camino con alguien, sueles hacerlo buscando profundidad y estabilidad. "
    "Puedes aportar paciencia, compromiso y una presencia tranquila que ayuda a consolidar "
    "vínculos duraderos.\n\n"

    "Las asociaciones y colaboraciones funcionan mejor cuando existe una base práctica y "
    "objetivos comunes. Tiendes a valorar acuerdos claros, responsabilidades definidas y "
    "proyectos donde ambas partes puedan beneficiarse de forma equilibrada. La cooperación "
    "adquiere sentido cuando genera algo estable y tangible.\n\n"

    "El desafío aparece cuando la necesidad de seguridad dificulta aceptar cambios inevitables "
    "dentro de una relación. Puede surgir apego a situaciones conocidas, resistencia a cerrar "
    "etapas o tendencia a mantener vínculos simplemente porque ofrecen estabilidad. En algunos "
    "momentos también puede costar expresar necesidades nuevas si alteran el equilibrio "
    "existente.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera estabilidad "
    "nace de la capacidad para adaptarse sin perder los valores esenciales. Cuando integras "
    "firmeza y flexibilidad, construyes relaciones donde la seguridad no proviene del miedo "
    "al cambio, sino de la confianza en lo que ambos sois capaces de crear."
),


"Géminis": (
    "Cuando Géminis ocupa la cúspide de la Casa 7, los vínculos se desarrollan a través de la "
    "comunicación, la curiosidad y el intercambio constante de ideas. La relación con otras "
    "personas se convierte en una vía fundamental para aprender, ampliar perspectivas y "
    "descubrir nuevas formas de comprender la realidad.\n\n"

    "Necesitas relaciones donde exista conversación, movimiento mental y libertad para "
    "explorar diferentes puntos de vista. La conexión suele fortalecerse cuando puedes "
    "compartir pensamientos, descubrir intereses comunes y sentir que la otra persona también "
    "estimula tu crecimiento intelectual.\n\n"

    "Esta posición favorece una gran capacidad para adaptarte a distintos tipos de personas. "
    "Puedes establecer puentes con facilidad, comprender perspectivas diversas y encontrar "
    "formas creativas de resolver diferencias. El diálogo suele ser una de tus principales "
    "herramientas para construir cercanía.\n\n"

    "Las asociaciones funcionan especialmente bien cuando permiten aprendizaje mutuo, "
    "intercambio de conocimientos o proyectos donde las ideas puedan circular libremente. "
    "La colaboración se vuelve más enriquecedora cuando existe espacio para cuestionar, "
    "experimentar y evolucionar juntos.\n\n"

    "El desafío aparece cuando la necesidad de variedad dificulta profundizar en un vínculo. "
    "Puede surgir inquietud ante relaciones demasiado previsibles o tendencia a analizar "
    "constantemente lo que sientes en lugar de permitirte vivir plenamente la experiencia "
    "emocional. También puede existir dificultad para sostener conversaciones incómodas "
    "cuando requieren una implicación más profunda.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la comunicación más "
    "valiosa no consiste únicamente en intercambiar ideas, sino también en compartir la "
    "propia vulnerabilidad. Cuando integras curiosidad y presencia emocional, construyes "
    "relaciones donde la mente y el corazón pueden encontrarse."
),


"Cáncer": (
    "Cuando Cáncer ocupa la cúspide de la Casa 7, los vínculos importantes se viven desde "
    "la necesidad de crear seguridad emocional, pertenencia y una sensación profunda de "
    "hogar compartido. Las relaciones no son únicamente espacios de intercambio, sino "
    "lugares donde buscas encontrar acogida, comprensión y una conexión profunda.\n\n"

    "Necesitas vínculos donde exista sensibilidad, cuidado y disponibilidad emocional. "
    "La confianza se construye progresivamente a través de pequeños gestos, presencia "
    "constante y la sensación de que la otra persona puede convertirse en un refugio "
    "seguro en los momentos importantes. Las relaciones frías o excesivamente racionales "
    "pueden resultar difíciles de sostener.\n\n"

    "Esta posición favorece una gran capacidad para cuidar dentro de la relación. Sueles "
    "percibir con facilidad los estados emocionales de la otra persona y puedes desarrollar "
    "una actitud muy protectora hacia quienes forman parte de tu vida. La empatía y la "
    "capacidad de acompañar se convierten en cualidades fundamentales dentro de tus "
    "vínculos.\n\n"

    "Las asociaciones importantes suelen estar marcadas por la confianza y por la creación "
    "de una base común. Te implicas especialmente en proyectos donde existe una dimensión "
    "humana y donde las personas sienten que forman parte de algo compartido. La cooperación "
    "adquiere sentido cuando existe un vínculo de pertenencia.\n\n"

    "El desafío aparece cuando la necesidad de seguridad emocional lleva a depender demasiado "
    "de la respuesta de la otra persona. Puede surgir temor al rechazo, tendencia a proteger "
    "en exceso o dificultad para aceptar que los vínculos también necesitan espacio y "
    "autonomía. En algunos momentos puedes confundir cuidar una relación con sostenerla "
    "constantemente por miedo a perderla.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera intimidad "
    "nace cuando dos personas pueden cuidarse sin dejar de ser individuos completos. Cuando "
    "integras sensibilidad y autonomía, construyes relaciones profundas donde el afecto se "
    "expresa desde la libertad y no desde la necesidad."
),


"Leo": (
    "Cuando Leo ocupa la cúspide de la Casa 7, los vínculos importantes se convierten en "
    "espacios donde expresar identidad, creatividad y reconocimiento mutuo. Existe una "
    "necesidad de relaciones que permitan a ambas personas sentirse valoradas y donde cada "
    "una pueda aportar su esencia sin tener que reducirse para adaptarse al otro.\n\n"

    "Necesitas vínculos donde exista admiración, generosidad y una expresión abierta del "
    "afecto. La relación adquiere fuerza cuando puedes sentir orgullo por la persona que "
    "acompaña tu camino y cuando también percibes que tus cualidades son reconocidas. "
    "La indiferencia o la ausencia de entusiasmo pueden debilitar la conexión.\n\n"

    "Esta posición favorece una forma cálida y generosa de relacionarte. Sueles aportar "
    "lealtad, protección y deseo de impulsar a la otra persona para que desarrolle su "
    "potencial. Cuando existe confianza, puedes convertirte en una fuente importante de "
    "motivación y apoyo para quienes comparten tu vida.\n\n"

    "Las asociaciones funcionan mejor cuando existe un propósito común y espacio para que "
    "cada persona aporte sus talentos. Puedes destacar en colaboraciones donde sea necesario "
    "inspirar, liderar o dar una dirección creativa al proyecto compartido.\n\n"

    "El desafío aparece cuando la necesidad de reconocimiento ocupa demasiado espacio dentro "
    "del vínculo. Puede surgir deseo de protagonismo, dificultad para aceptar críticas o "
    "sensación de que tu valor no recibe suficiente reconocimiento cuando la atención no está dirigida hacia "
    "ti. También puede aparecer la tendencia a ofrecer mucho esperando recibir la misma "
    "cantidad de admiración a cambio.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que el amor y la colaboración "
    "no necesitan demostrar constantemente el valor de cada persona. Cuando integras "
    "generosidad y humildad, construyes relaciones donde ambos pueden brillar sin competir "
    "por el lugar central."
),


"Virgo": (
    "Cuando Virgo ocupa la cúspide de la Casa 7, los vínculos importantes se desarrollan a "
    "través de la cooperación práctica, la confianza construida mediante hechos y la "
    "capacidad de mejorar juntos. Las relaciones adquieren valor cuando existe compromiso, "
    "atención a los detalles y una voluntad compartida de cuidar aquello que se está "
    "construyendo.\n\n"

    "Necesitas vínculos donde exista coherencia entre las palabras y las acciones. La "
    "confianza no suele surgir únicamente de las declaraciones afectivas, sino de comprobar "
    "que la otra persona es responsable, está presente y participa activamente en la relación. "
    "Valoras especialmente la capacidad de apoyarse mutuamente en la vida cotidiana.\n\n"

    "Esta posición favorece una gran capacidad para comprender las necesidades del otro y "
    "aportar soluciones concretas dentro del vínculo. Puedes demostrar afecto mediante la "
    "ayuda, la atención y la disposición a mejorar las circunstancias compartidas. Tu forma "
    "de cuidar suele expresarse más a través de acciones que de grandes demostraciones.\n\n"

    "Las asociaciones funcionan mejor cuando existe organización, objetivos claros y una "
    "sensación de que cada persona aporta algo útil al conjunto. Tienes facilidad para "
    "detectar aquello que puede optimizarse y para contribuir al crecimiento de proyectos "
    "compartidos desde una mirada práctica.\n\n"

    "El desafío aparece cuando la búsqueda de perfección afecta a la relación. Puede surgir "
    "tendencia a analizar demasiado a la otra persona, señalar constantemente aquello que "
    "podría mejorarse o exigir una coherencia imposible. En algunos momentos también puede "
    "costar aceptar el amor cuando no llega en la forma exacta que esperabas.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que una relación saludable "
    "no necesita ser perfecta para ser valiosa. Cuando integras discernimiento y aceptación, "
    "desarrollas vínculos donde el crecimiento compartido nace del apoyo y no de la crítica."
),


"Libra": (
    "Cuando Libra ocupa la cúspide de la Casa 7, esta área encuentra una expresión "
    "especialmente natural, ya que los vínculos, la cooperación y el encuentro con los "
    "demás forman parte esencial de su propio lenguaje. Existe una necesidad profunda de "
    "compartir la experiencia de la vida, descubrirse a través del otro y construir "
    "relaciones basadas en el equilibrio y la reciprocidad.\n\n"

    "Necesitas vínculos donde exista diálogo, respeto y una verdadera disposición a tener "
    "en cuenta las necesidades de ambas personas. La relación ideal no se construye desde "
    "la dependencia, sino desde la capacidad de crear un espacio común donde cada individuo "
    "pueda desarrollarse manteniendo su propia identidad.\n\n"

    "Esta posición favorece una gran habilidad para comprender diferentes puntos de vista y "
    "buscar soluciones que contemplen el bienestar compartido. Sueles aportar diplomacia, "
    "sensibilidad y una disposición natural para generar acuerdos. El encuentro con otras "
    "personas puede convertirse en una fuente constante de aprendizaje y evolución.\n\n"

    "Las asociaciones adquieren especial importancia en tu camino. Puedes desarrollarte "
    "plenamente en proyectos donde exista colaboración, intercambio de ideas y construcción "
    "conjunta. La capacidad de unir talentos y crear puentes entre personas constituye uno "
    "de tus recursos más valiosos.\n\n"

    "El desafío aparece cuando la búsqueda de armonía lleva a evitar diferencias necesarias "
    "o a colocar las necesidades del otro por encima de las propias. Puede surgir dificultad "
    "para tomar decisiones independientes, expresar desacuerdos o sostener una postura "
    "personal cuando existe riesgo de generar tensión.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que el verdadero equilibrio "
    "no consiste en evitar cualquier conflicto, sino en aprender a atravesarlo con respeto. "
    "Cuando integras cooperación y afirmación personal, construyes relaciones donde la "
    "armonía nace de la autenticidad de ambas partes."
),


"Escorpio": (
    "Cuando Escorpio ocupa la cúspide de la Casa 7, los vínculos importantes se viven con "
    "gran intensidad emocional y capacidad de transformación. Las relaciones significativas "
    "rara vez permanecen en un nivel superficial; tienden a convertirse en experiencias que "
    "revelan aspectos profundos de tu mundo interior y generan procesos de cambio interno.\n\n"

    "Necesitas vínculos donde exista autenticidad, confianza y una conexión que vaya más "
    "allá de lo aparente. La entrega emocional requiere sentir que la relación posee "
    "profundidad y que ambas personas están dispuestas a mostrarse con honestidad. Los "
    "intercambios demasiado ligeros pueden resultar poco satisfactorios a largo plazo.\n\n"

    "Esta posición favorece una gran capacidad para comprender las motivaciones profundas "
    "de quienes te rodean. Puedes percibir matices que no siempre son expresados y "
    "acompañar procesos complejos con una intensidad que transforma la manera en que las "
    "personas se relacionan contigo.\n\n"

    "Las asociaciones importantes pueden convertirse en espacios de transformación y evolución "
    "mutua. Los proyectos compartidos adquieren fuerza cuando existe compromiso, confianza y "
    "la voluntad de atravesar juntos las etapas de cambio que inevitablemente forman parte "
    "de cualquier construcción a largo plazo.\n\n"

    "El desafío aparece cuando la intensidad emocional se transforma en necesidad de control, "
    "miedo a la vulnerabilidad o dificultad para aceptar la autonomía del otro. Puede surgir "
    "tendencia a poner a prueba los vínculos o a mantener defensas incluso cuando ya existe "
    "confianza suficiente.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera profundidad "
    "no nace de controlar la relación, sino de permitir que ambas personas puedan mostrarse "
    "plenamente. Cuando integras entrega y libertad, construyes vínculos capaces de "
    "transformar sin perder el respeto por la individualidad."
),


"Sagitario": (
    "Cuando Sagitario ocupa la cúspide de la Casa 7, los vínculos importantes se convierten "
    "en caminos de expansión, aprendizaje y descubrimiento. Las relaciones adquieren mayor "
    "vitalidad cuando permiten crecer juntos, compartir experiencias nuevas y ampliar la "
    "forma de comprender la vida.\n\n"

    "Necesitas vínculos donde exista libertad, confianza y una sensación de movimiento. "
    "La relación se fortalece cuando ambas personas pueden evolucionar, explorar nuevas "
    "posibilidades y mantener una visión amplia del futuro. Los compromisos que se sienten "
    "como limitaciones pueden generar inquietud o sensación de pérdida de espacio personal.\n\n"

    "Esta posición favorece encuentros con personas que aportan nuevas perspectivas, "
    "conocimientos o formas diferentes de ver el mundo. Las relaciones pueden convertirse "
    "en verdaderas experiencias de aprendizaje, ayudándote a ampliar tus horizontes y "
    "descubrir aspectos desconocidos de quién eres.\n\n"

    "Las asociaciones funcionan especialmente bien cuando existe una visión compartida y "
    "un propósito que trasciende los intereses individuales. Puedes aportar entusiasmo, "
    "confianza y capacidad para inspirar a quienes colaboran contigo, impulsando proyectos "
    "que buscan crecer y desarrollarse.\n\n"

    "El desafío aparece cuando la necesidad de libertad dificulta la profundidad del "
    "compromiso. Puede surgir tendencia a idealizar nuevas experiencias, buscar siempre "
    "algo diferente o evitar vínculos que requieren presencia constante y responsabilidad "
    "emocional. En algunos momentos también puede existir dificultad para aceptar puntos "
    "de vista distintos a los propios.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera expansión "
    "no depende de mantener todas las puertas abiertas, sino de elegir conscientemente "
    "aquellos caminos que merecen ser recorridos. Cuando integras libertad y compromiso, "
    "construyes relaciones que inspiran crecimiento mutuo."
),


"Capricornio": (
    "Cuando Capricornio ocupa la cúspide de la Casa 7, los vínculos importantes se construyen "
    "a través del compromiso, la responsabilidad y la capacidad de crear algo sólido a largo "
    "plazo. Las relaciones adquieren verdadero valor cuando existe confianza, madurez y una "
    "disposición compartida para afrontar tanto los momentos favorables como los desafíos.\n\n"

    "Necesitas vínculos donde exista estabilidad y coherencia. La confianza suele desarrollarse "
    "con el tiempo, a través de experiencias compartidas que demuestran la capacidad de ambas "
    "personas para sostener sus compromisos. Las relaciones demasiado impulsivas o carentes de "
    "dirección pueden resultar poco satisfactorias.\n\n"

    "Esta posición favorece una actitud seria y responsable dentro de los vínculos. Sueles "
    "valorar la lealtad, la palabra dada y la capacidad de construir conjuntamente. Puedes "
    "aportar perseverancia, apoyo constante y una visión práctica que ayuda a consolidar "
    "proyectos compartidos.\n\n"

    "Las asociaciones importantes pueden convertirse en pilares fundamentales de crecimiento. "
    "Existe facilidad para trabajar junto a otras personas con objetivos definidos, especialmente "
    "cuando la colaboración permite desarrollar algo que tenga continuidad y proyección futura. "
    "La cooperación adquiere sentido cuando se basa en la confianza y la responsabilidad mutua.\n\n"

    "El desafío aparece cuando la necesidad de seguridad lleva a vivir los vínculos desde la "
    "obligación o el exceso de control. Puede surgir dificultad para mostrar vulnerabilidad, "
    "expresar necesidades emocionales o permitir que una relación sea también un espacio de "
    "espontaneidad y disfrute. En algunos momentos puedes asumir más peso del que corresponde "
    "por sentir que eres quien debe sostener la estructura.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera solidez de una "
    "relación no depende únicamente de resistir dificultades, sino también de cultivar cercanía "
    "y apertura emocional. Cuando integras responsabilidad y sensibilidad, construyes vínculos "
    "maduros donde el compromiso se convierte en una elección libre."
),


"Acuario": (
    "Cuando Acuario ocupa la cúspide de la Casa 7, los vínculos importantes necesitan basarse "
    "en la libertad, la autenticidad y el reconocimiento de la individualidad de cada persona. "
    "Las relaciones adquieren mayor sentido cuando permiten que ambas partes evolucionen sin "
    "tener que renunciar a su propia manera de ser.\n\n"

    "Necesitas vínculos donde exista amistad, complicidad mental y espacio para compartir ideas "
    "diferentes. La conexión suele fortalecerse cuando la otra persona respeta tu necesidad de "
    "independencia y, al mismo tiempo, participa en una construcción común basada en la "
    "confianza y la igualdad.\n\n"

    "Esta posición favorece encuentros con personas poco convencionales, creativas o capaces "
    "de aportar nuevas perspectivas. Las relaciones pueden convertirse en espacios donde "
    "cuestionar creencias, ampliar horizontes y descubrir formas diferentes de comprender "
    "la convivencia.\n\n"

    "Las asociaciones funcionan especialmente bien cuando existe una visión compartida de futuro "
    "y cuando cada integrante puede aportar su originalidad al proyecto común. Puedes destacar "
    "en colaboraciones donde sean importantes la innovación, la cooperación y la búsqueda de "
    "soluciones nuevas.\n\n"

    "El desafío aparece cuando la necesidad de preservar la libertad genera distancia emocional "
    "o dificultad para implicarte plenamente. Puede surgir tendencia a racionalizar demasiado "
    "los sentimientos, mantener cierta separación para proteger la independencia o rechazar "
    "estructuras relacionales simplemente porque parecen limitarte.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la libertad más profunda no "
    "consiste en mantener cierta distancia, sino en poder elegir conscientemente el vínculo que deseas "
    "construir. Cuando integras independencia y presencia emocional, creas relaciones donde la "
    "diferencia se convierte en una fuente de enriquecimiento."
),


"Piscis": (
    "Cuando Piscis ocupa la cúspide de la Casa 7, los vínculos importantes se viven desde la "
    "sensibilidad, la empatía y una profunda necesidad de conexión emocional. Las relaciones "
    "pueden convertirse en espacios donde experimentar una unión que va más allá de lo "
    "racional, permitiendo descubrir dimensiones más sutiles de la experiencia compartida.\n\n"

    "Necesitas vínculos donde exista comprensión, aceptación y una sensación de conexión "
    "profunda. La relación adquiere significado cuando ambas personas pueden mostrarse con "
    "sensibilidad y acompañarse desde la compasión. Los intercambios demasiado fríos o "
    "exclusivamente prácticos pueden dejar una sensación de falta de profundidad.\n\n"

    "Esta posición favorece una gran capacidad para percibir las necesidades emocionales de "
    "la otra persona. Puedes aportar escucha, intuición y una disposición natural para "
    "acompañar procesos importantes. Tu forma de vincularte suele estar guiada por la empatía "
    "más que por el cálculo racional.\n\n"

    "Las asociaciones adquieren mayor fuerza cuando existe inspiración compartida, creatividad "
    "o una motivación que trasciende los intereses individuales. Puedes desarrollarte en "
    "colaboraciones donde sea importante la imaginación, la sensibilidad humana o la capacidad "
    "de conectar con algo más amplio que el objetivo inmediato.\n\n"

    "El desafío aparece cuando la sensibilidad dificulta establecer límites claros dentro del "
    "vínculo. Puede existir tendencia a idealizar a la otra persona, adaptarte demasiado a sus "
    "necesidades o confundir empatía con responsabilidad sobre el mundo emocional del otro. "
    "En algunos momentos puede resultar difícil distinguir entre amor y sacrificio.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera unión nace "
    "cuando dos personas pueden encontrarse desde la plenitud y no desde la necesidad de "
    "salvarse mutuamente. Cuando integras sensibilidad y claridad, construyes relaciones "
    "profundas donde la conexión emocional convive con la libertad personal."
),

}



CASA_8 = {

"Aries": (
    "Cuando Aries ocupa la cúspide de la Casa 8, los procesos de transformación se viven "
    "con intensidad, iniciativa y una necesidad profunda de afrontar los cambios de manera "
    "directa. Existe una tendencia natural a enfrentarte a las experiencias que exigen "
    "renovación, como si cada crisis contuviera una oportunidad para descubrir una versión "
    "más fuerte de quien eres.\n\n"

    "Los procesos de cambio rara vez se viven desde la pasividad. Necesitas participar "
    "activamente en tu propia evolución, tomando decisiones y actuando cuando percibes que "
    "una etapa ha llegado a su límite. La transformación adquiere sentido cuando sientes "
    "que puedes recuperar el control de tu camino y abrir una nueva dirección.\n\n"

    "Esta posición favorece una gran capacidad para atravesar momentos intensos y recuperarte "
    "después de experiencias difíciles. Las crisis pueden convertirse en motores de crecimiento, "
    "despertando una fuerza interior que quizá permanecía oculta. Tu capacidad de comenzar de "
    "nuevo constituye uno de tus recursos más importantes.\n\n"

    "En los vínculos profundos existe una necesidad de autenticidad y entrega. Las relaciones "
    "superficiales suelen resultar poco satisfactorias, ya que buscas experiencias que permitan "
    "un intercambio verdadero y transformador. Cuando confías, puedes implicarte con gran "
    "intensidad y compromiso.\n\n"

    "El desafío aparece cuando la necesidad de transformación se convierte en una búsqueda "
    "constante de intensidad o conflicto. Puede existir dificultad para aceptar los tiempos "
    "naturales de los procesos, intentando acelerar cambios que necesitan maduración. También "
    "puede aparecer una tendencia a querer controlar aquello que, por naturaleza, requiere "
    "entrega y confianza.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera fuerza no "
    "consiste únicamente en luchar contra las dificultades, sino también en permitir que los "
    "procesos internos ocurran. Cuando integras iniciativa y aceptación, la transformación "
    "se convierte en una fuente de renovación consciente y profunda."
),


"Tauro": (
    "Cuando Tauro ocupa la cúspide de la Casa 8, los procesos de transformación necesitan "
    "desarrollarse con tiempo, seguridad y una sensación de estabilidad interna. Los cambios "
    "profundos pueden vivirse como procesos que requieren preparación, ya que existe una "
    "fuerte necesidad de comprender qué se conserva y qué debe ser dejado atrás.\n\n"

    "La transformación no suele producirse de manera impulsiva, sino a través de una evolución "
    "gradual. Necesitas sentir que las nuevas estructuras que aparecen pueden ofrecer una base "
    "sólida antes de abandonar aquello que anteriormente proporcionaba seguridad. Los grandes "
    "cambios suelen llegar cuando comprendes que la estabilidad también puede encontrarse en "
    "tu interior.\n\n"

    "Esta posición aporta una gran capacidad para sostener procesos largos y atravesar etapas "
    "complejas con paciencia. Existe resistencia, pero también una enorme fortaleza para "
    "mantenerte firme cuando la vida exige atravesar períodos de transformación profunda.\n\n"

    "En los intercambios emocionales y materiales buscas confianza, lealtad y coherencia. "
    "La intimidad se construye poco a poco, mediante la demostración constante de que el otro "
    "es un espacio seguro. Cuando existe esa confianza, puedes desarrollar vínculos muy "
    "profundos y estables.\n\n"

    "El desafío aparece cuando el apego a lo conocido dificulta aceptar aquello que necesita "
    "cambiar. Puede existir tendencia a mantener situaciones agotadas simplemente porque "
    "ofrecen seguridad o porque abandonar lo construido genera incertidumbre. La transformación "
    "puede sentirse amenazante antes de revelar nuevas posibilidades.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera seguridad no "
    "depende de conservar siempre la misma forma, sino de confiar en la capacidad para crear "
    "nuevos apoyos cuando la vida cambia. Entonces la transformación deja de vivirse como "
    "pérdida y se convierte en una forma más profunda de crecimiento."
),


"Géminis": (
    "Cuando Géminis ocupa la cúspide de la Casa 8, la transformación se desarrolla a través "
    "de la comprensión, la observación y la capacidad para encontrar nuevos significados en "
    "las experiencias profundas. Necesitas comprender qué ocurre dentro de ti y alrededor "
    "tuyo antes de poder integrar completamente un cambio importante.\n\n"

    "Los procesos de crisis suelen activar una intensa búsqueda de información y nuevas "
    "perspectivas. Preguntar, analizar y conversar pueden convertirse en herramientas "
    "fundamentales para atravesar etapas de transformación. Necesitas poner palabras a lo "
    "que sucede para poder asimilarlo.\n\n"

    "Esta posición favorece una gran capacidad para observar los procesos internos con cierta "
    "distancia y comprender las diferentes dimensiones de una experiencia. Puedes encontrar "
    "conexiones entre acontecimientos aparentemente separados y extraer aprendizajes valiosos "
    "de situaciones complejas.\n\n"

    "En los vínculos profundos existe una necesidad de intercambio mental además de emocional. "
    "La intimidad crece cuando puedes compartir pensamientos, inquietudes y descubrimientos. "
    "La comunicación se convierte en una vía esencial para construir confianza y cercanía.\n\n"

    "El desafío aparece cuando la necesidad de comprender todo racionalmente dificulta la "
    "entrega emocional. Puede existir tendencia a analizar el dolor en lugar de sentirlo, "
    "buscar explicaciones antes de permitir que una experiencia revele su significado o "
    "mantener cierta distancia frente a emociones demasiado intensas.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que comprender y sentir no son "
    "procesos opuestos. Cuando integras la claridad mental con la profundidad emocional, "
    "desarrollas una capacidad extraordinaria para transformar experiencias difíciles en "
    "conocimiento y crecimiento personal."
),


"Cáncer": (
    "Cuando Cáncer ocupa la cúspide de la Casa 8, los procesos de transformación están "
    "profundamente vinculados con la vida emocional, los vínculos íntimos y la capacidad "
    "para atravesar experiencias que modifican la manera en que te relacionas contigo "
    "y con los demás. Los cambios importantes suelen tocar capas profundas de la memoria, "
    "las raíces personales y aquello que necesitas sentir para experimentar verdadera seguridad.\n\n"

    "La transformación ocurre a través de la conexión emocional. No sueles cambiar únicamente "
    "por comprender una situación desde la mente, sino cuando una experiencia logra tocarte "
    "internamente y despierta una nueva comprensión de tus necesidades. Los momentos de "
    "transición pueden convertirse en oportunidades para sanar antiguas heridas y liberar "
    "formas de protección que ya no son necesarias.\n\n"

    "Esta posición favorece una gran capacidad para acompañar procesos profundos, tanto propios "
    "como ajenos. Existe una sensibilidad especial para percibir lo que ocurre detrás de las "
    "palabras y comprender las emociones que atraviesan una situación. La intimidad se convierte "
    "en un espacio de transformación donde el intercambio afectivo tiene un enorme poder "
    "regenerador.\n\n"

    "En los recursos compartidos y en los vínculos de confianza necesitas sentir seguridad "
    "emocional. La entrega profunda requiere tiempo y la certeza de que existe un espacio "
    "donde puedes mostrar tu vulnerabilidad sin sentir que pierdes protección. Cuando esa "
    "confianza está presente, desarrollas una capacidad extraordinaria para crear lazos "
    "profundos y nutritivos.\n\n"

    "El desafío aparece cuando el miedo a perder aquello que amas dificulta los procesos "
    "naturales de cambio. Puede existir tendencia a aferrarte al pasado, conservar vínculos "
    "por lealtad emocional o asumir cargas que pertenecen a otras personas. En algunos "
    "momentos proteger puede convertirse en una forma de evitar la transformación necesaria.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera seguridad "
    "emocional nace de la capacidad para sostenerte incluso cuando algo cambia. Cuando "
    "aprendes a soltar sin perder el amor, la transformación se convierte en una fuente de "
    "renovación profunda y en una forma de conectar con tu propia fortaleza interior."
),


"Leo": (
    "Cuando Leo ocupa la cúspide de la Casa 8, los procesos de transformación están ligados "
    "a la necesidad de descubrir una identidad más auténtica y profunda. Los cambios "
    "importantes suelen invitarte a revisar quién eres, qué deseas expresar y qué partes de "
    "ti necesitan evolucionar para permitir una manifestación más completa de tu esencia.\n\n"

    "La transformación puede vivirse como un proceso de reconstrucción personal. Cada etapa "
    "intensa de la vida ofrece la oportunidad de abandonar versiones anteriores de quién eres y "
    "recuperar una expresión más genuina de tu fuerza creativa. Las crisis pueden convertirse "
    "en momentos donde descubres capacidades que permanecían ocultas.\n\n"

    "Esta posición favorece una gran capacidad para regenerarte después de experiencias "
    "desafiantes. Existe una fuerza interna relacionada con la confianza en la propia capacidad "
    "de volver a empezar y con la voluntad de encontrar un sentido creativo incluso en "
    "circunstancias complejas.\n\n"

    "En los vínculos profundos necesitas sentir que existe reconocimiento mutuo y una entrega "
    "auténtica. La intimidad adquiere mayor significado cuando permite que ambas personas "
    "puedan mostrarse plenamente, sin perder individualidad ni necesidad de ocultar sus "
    "verdaderas cualidades.\n\n"

    "El desafío aparece cuando el orgullo dificulta atravesar los procesos de cambio. Puede "
    "existir resistencia a mostrar vulnerabilidad, aceptar ayuda o reconocer que algunas "
    "etapas necesitan terminar. En ocasiones puede resultar doloroso descubrir que la imagen "
    "que tienes de quién eres ya no representa tu evolución actual.\n\n"

    "Con el paso de los años, esta posición invita a comprender que la verdadera fuerza no "
    "consiste en mantener siempre una imagen de poder, sino en permitirte transformar esa "
    "imagen cuando la vida lo requiere. Cuando integras humildad y confianza, tu capacidad "
    "de renacer se convierte en una fuente de inspiración para otros."
),


"Virgo": (
    "Cuando Virgo ocupa la cúspide de la Casa 8, los procesos de transformación se viven "
    "a través de la comprensión, la depuración y la necesidad de mejorar aquello que ya no "
    "funciona. Existe una tendencia natural a observar con detalle las experiencias profundas "
    "para descubrir qué aspectos necesitan ser ajustados, sanados o reorganizados.\n\n"

    "Los cambios importantes suelen abordarse mediante análisis y reflexión. Necesitas "
    "comprender los mecanismos que están actuando antes de poder entregarte plenamente al "
    "proceso. Esta capacidad de observación permite atravesar etapas complejas con una mirada "
    "práctica y orientada hacia la evolución.\n\n"

    "Esta posición favorece una gran capacidad para sanar, reorganizar y transformar patrones "
    "profundos. Puedes detectar aquello que permanece oculto, identificar hábitos emocionales "
    "que necesitan revisión y desarrollar estrategias concretas para avanzar hacia una mayor "
    "coherencia interna.\n\n"

    "En los vínculos íntimos valoras la honestidad, la confianza y la posibilidad de crecer "
    "juntos. La entrega profunda suele construirse a través de pequeños gestos de cuidado y "
    "de una atención constante hacia las necesidades reales de la relación. La intimidad "
    "encuentra seguridad en la presencia y la dedicación.\n\n"

    "El desafío aparece cuando la necesidad de comprender o mejorar todo dificulta aceptar "
    "los procesos tal como son. Puede surgir exceso de análisis, dificultad para soltar el "
    "control o una tendencia a buscar qué está mal incluso en experiencias que simplemente "
    "necesitan ser vividas. La transformación no siempre puede organizarse paso a paso.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la evolución profunda no "
    "consiste únicamente en corregir aquello que no funciona, sino también en aceptar y "
    "valorar los procesos naturales de cambio. Cuando integras discernimiento y confianza, "
    "desarrollas una gran capacidad para convertir las crisis en oportunidades de crecimiento."
),


"Libra": (
    "Cuando Libra ocupa la cúspide de la Casa 8, los procesos de transformación se desarrollan "
    "a través de los vínculos profundos, el intercambio emocional y la capacidad para encontrar "
    "equilibrio en situaciones que implican cambio. Las experiencias más intensas de la vida "
    "suelen invitarte a revisar la manera en que compartes, confías y te entregas a los demás.\n\n"

    "La transformación adquiere un sentido especialmente relacional. Muchas de tus grandes "
    "evoluciones pueden surgir a través de encuentros significativos que muestran aspectos de "
    "ti que permanecían ocultos. Los vínculos íntimos se convierten en espejos donde "
    "descubres nuevas formas de comprender tus necesidades, tus límites y tu manera de amar.\n\n"

    "Esta posición favorece una gran capacidad para atravesar procesos complejos buscando "
    "comprensión y cooperación. Existe facilidad para mediar, acompañar crisis o encontrar "
    "puntos de equilibrio cuando las circunstancias parecen dividir a las personas. La "
    "transformación se vuelve más consciente cuando puede compartirse desde el diálogo.\n\n"

    "En los recursos compartidos y en la intimidad existe una necesidad de reciprocidad. "
    "La confianza aumenta cuando percibes que existe un intercambio justo, donde ambas partes "
    "pueden aportar y recibir sin perder su autonomía. Los vínculos profundos necesitan "
    "mantener un equilibrio entre entrega y respeto por las necesidades individuales.\n\n"

    "El desafío aparece cuando el deseo de mantener la armonía dificulta atravesar conflictos "
    "necesarios para crecer. Puede existir tendencia a evitar conversaciones incómodas, ceder "
    "demasiado para preservar la relación o buscar una solución equilibrada antes de reconocer "
    "plenamente lo que realmente sientes. Algunas transformaciones requieren aceptar cierta "
    "incomodidad inicial.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que el verdadero equilibrio no "
    "consiste en evitar toda tensión, sino en aprender a atravesarla con consciencia. Cuando "
    "integras cooperación y autenticidad, los vínculos se convierten en espacios de profunda "
    "evolución y crecimiento compartido."
),


"Escorpio": (
    "Cuando Escorpio ocupa la cúspide de la Casa 8, los procesos de transformación se viven "
    "con una intensidad especialmente profunda. Existe una capacidad natural para atravesar "
    "crisis, explorar los aspectos ocultos de la vida y renacer después de etapas que "
    "modifican por completo la manera de comprenderte y comprender el mundo.\n\n"

    "La transformación forma parte esencial del camino. Las experiencias importantes rara vez "
    "te dejan igual, ya que tienden a activar procesos internos que invitan a abandonar versiones "
    "anteriores de quién eres y descubrir recursos que permanecían dormidos. La vida puede "
    "llevarte a atravesar varias etapas de muerte simbólica y renovación.\n\n"

    "Esta posición aporta una enorme capacidad de regeneración. Cuando atraviesas momentos "
    "difíciles, puedes desarrollar una fortaleza interior que surge precisamente de haber "
    "conocido tus propios límites y haberlos transformado. Existe una comprensión profunda "
    "de que cada crisis contiene una posibilidad de evolución.\n\n"

    "En los vínculos íntimos buscas autenticidad absoluta. Las relaciones superficiales suelen "
    "resultar poco satisfactorias porque necesitas sentir una conexión que permita compartir "
    "las partes más profundas de la experiencia humana. Cuando existe confianza, puedes "
    "entregarte con una intensidad y una lealtad extraordinarias.\n\n"

    "El desafío aparece cuando la profundidad se transforma en necesidad de controlar o "
    "mantener una vigilancia constante sobre aquello que podría cambiar. Puede existir miedo "
    "a la vulnerabilidad, dificultad para soltar vínculos o situaciones del pasado, o una "
    "tendencia a vivir determinadas experiencias desde la lucha en lugar de desde la entrega.\n\n"

    "Con el paso de los años, esta posición invita a comprender que el verdadero poder no nace "
    "del control, sino de la capacidad para confiar en los ciclos de transformación. Cuando "
    "aceptas el movimiento natural de la vida, tu intensidad se convierte en sabiduría, "
    "profundidad y una extraordinaria capacidad para acompañar procesos de cambio."
),


"Sagitario": (
    "Cuando Sagitario ocupa la cúspide de la Casa 8, los procesos de transformación se viven "
    "como oportunidades de expansión y descubrimiento. Incluso las experiencias más intensas "
    "pueden convertirse en caminos hacia una comprensión más amplia de la vida, siempre que "
    "encuentres un sentido que permita integrar aquello que has atravesado.\n\n"

    "La transformación necesita abrir nuevas perspectivas. Los momentos de crisis pueden "
    "despertar preguntas profundas sobre tus creencias, tu visión del mundo y el significado "
    "de tus experiencias. Aprender de lo vivido se convierte en una forma esencial de "
    "renovarte y continuar creciendo.\n\n"

    "Esta posición favorece una gran capacidad para encontrar oportunidades dentro de los "
    "cambios. Incluso cuando una etapa termina, sueles buscar qué conocimiento, aprendizaje "
    "o nueva posibilidad puede surgir de esa transición. La confianza en que la vida tiene "
    "un propósito mayor puede convertirse en un recurso importante.\n\n"

    "En los vínculos profundos necesitas compartir una visión de crecimiento. La intimidad "
    "se fortalece cuando existe libertad para evolucionar, explorar nuevas experiencias y "
    "ampliar juntos la comprensión de la realidad. Las relaciones demasiado limitantes pueden "
    "sentirse como una pérdida de vitalidad.\n\n"

    "El desafío aparece cuando la necesidad de expansión dificulta permanecer presente en "
    "procesos emocionales más intensos o complejos. Puede surgir tendencia a buscar rápidamente "
    "una explicación positiva sin permitirte atravesar completamente el dolor o la incertidumbre. "
    "En ocasiones también puede existir dificultad para aceptar límites inevitables.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera expansión nace "
    "también de la profundidad. Cuando integras confianza y compromiso con el proceso, cada "
    "transformación se convierte en una fuente de sabiduría y en una ampliación real de tu "
    "consciencia."
),


"Capricornio": (
    "Cuando Capricornio ocupa la cúspide de la Casa 8, los procesos de transformación se "
    "viven de manera gradual, profunda y orientada hacia la construcción de una mayor "
    "fortaleza interna. Los cambios importantes suelen requerir tiempo de integración, ya "
    "que necesitas comprender qué estructuras deben mantenerse y cuáles han cumplido ya "
    "su función.\n\n"

    "La transformación se desarrolla a través de la responsabilidad y la capacidad para "
    "afrontar aquello que la vida pone delante. No sueles buscar cambios por impulso, sino "
    "que tiendes a atravesar los procesos intensos con una actitud consciente, intentando "
    "extraer de ellos un aprendizaje que pueda convertirse en una base más sólida para el "
    "futuro.\n\n"

    "Esta posición favorece una gran resistencia ante las etapas difíciles. Existe una "
    "capacidad natural para sostener situaciones complejas, asumir responsabilidades "
    "profundas y reconstruirte poco a poco cuando las circunstancias exigen una nueva "
    "estructura. Tu fortaleza suele hacerse visible precisamente en momentos de desafío.\n\n"

    "En los vínculos íntimos necesitas confianza, compromiso y una sensación de seguridad "
    "mutua. La entrega profunda suele desarrollarse con el tiempo, cuando compruebas que "
    "la otra persona es capaz de sostener la relación con madurez y responsabilidad. "
    "Valoras los vínculos que pueden atravesar dificultades sin perder estabilidad.\n\n"

    "El desafío aparece cuando la necesidad de mantener el control o la estructura dificulta "
    "la entrega emocional. Puede existir tendencia a cargar con demasiado peso, asumir que "
    "debes resolverlo todo sin ayuda o sentir que mostrar vulnerabilidad puede debilitar "
    "tu posición. En algunos momentos puede costar aceptar que ciertos procesos requieren "
    "soltar antes de poder reconstruir.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera fortaleza "
    "no consiste únicamente en resistir, sino también en permitirte transformar aquello que "
    "ya no necesita permanecer. Cuando integras disciplina y apertura, desarrollas una "
    "capacidad profunda para convertir las crisis en madurez y sabiduría."
),


"Acuario": (
    "Cuando Acuario ocupa la cúspide de la Casa 8, los procesos de transformación se viven "
    "a través de cambios profundos que cuestionan antiguas formas de comprender la realidad. "
    "Existe una necesidad natural de evolucionar, liberarte de patrones heredados y descubrir "
    "nuevas maneras de relacionarte con la intimidad, el poder personal y los procesos de "
    "renovación.\n\n"

    "La transformación suele llegar cuando algo rompe con lo establecido y te obliga a mirar "
    "la vida desde una perspectiva diferente. Los cambios inesperados pueden convertirse "
    "en puertas hacia una mayor libertad interior, especialmente cuando permiten abandonar "
    "estructuras que ya no representan quién eres.\n\n"

    "Esta posición favorece una gran capacidad para observar los procesos de cambio desde una "
    "mirada amplia y objetiva. Puedes comprender las crisis como etapas evolutivas más que "
    "como simples pérdidas, encontrando posibilidades nuevas allí donde otras personas solo "
    "perciben ruptura o incertidumbre.\n\n"

    "En los vínculos profundos necesitas una intimidad que respete la individualidad de ambas "
    "personas. La entrega emocional funciona mejor cuando existe libertad, autenticidad y "
    "espacio para que cada integrante pueda seguir desarrollándose en libertad.\n\n"

    "El desafío aparece cuando la necesidad de independencia genera cierta distancia frente "
    "a emociones demasiado intensas. Puede existir tendencia a analizar los procesos desde "
    "la mente, desconectándote temporalmente de aquello que necesitas sentir, o rechazar "
    "determinados cambios simplemente porque parecen amenazar tu autonomía.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera libertad "
    "también incluye la capacidad de implicarte profundamente. Cuando integras independencia "
    "y entrega, la transformación se convierte en una vía para descubrir una versión más "
    "auténtica y consciente de quién eres."
),


"Piscis": (
    "Cuando Piscis ocupa la cúspide de la Casa 8, los procesos de transformación se viven "
    "desde una profunda sensibilidad hacia las experiencias emocionales, simbólicas y "
    "espirituales de la vida. Existe una capacidad natural para percibir los movimientos "
    "internos más sutiles y comprender que algunos cambios requieren tiempo, aceptación y "
    "entrega.\n\n"

    "La transformación ocurre muchas veces a través de procesos que no pueden explicarse "
    "únicamente desde la lógica. Intuyes que determinadas etapas necesitan ser atravesadas "
    "más que controladas, permitiendo que nuevas comprensiones aparezcan cuando llega el "
    "momento adecuado. La vida interior se convierte en un espacio esencial de evolución.\n\n"

    "Esta posición favorece una gran capacidad de regeneración emocional y una profunda "
    "empatía hacia los procesos de los demás. Puedes acompañar momentos de crisis con "
    "sensibilidad y comprensión, percibiendo aspectos que permanecen ocultos para una mirada "
    "más superficial.\n\n"

    "En los vínculos íntimos buscas una conexión que trascienda lo cotidiano. La confianza "
    "se construye cuando existe apertura emocional, aceptación y la posibilidad de compartir "
    "aquello que normalmente permanece protegido. La intimidad puede convertirse en un espacio "
    "de sanación y crecimiento mutuo.\n\n"

    "El desafío aparece cuando la sensibilidad dificulta establecer límites claros dentro de "
    "los procesos de transformación. Puede existir tendencia a absorber demasiado las emociones "
    "ajenas, idealizar determinadas experiencias o esperar que los cambios ocurran sin necesidad "
    "de tomar decisiones concretas. En algunos momentos puede resultar difícil diferenciar "
    "entre intuición y deseo.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la entrega verdadera no "
    "significa perderte en los procesos, sino participar conscientemente en ellos. Cuando "
    "integras sensibilidad y claridad, la transformación se convierte en una fuente de "
    "profunda comprensión, compasión y conexión con la vida."
),

}


CASA_9 = {

"Aries": (
    "Cuando Aries ocupa la cúspide de la Casa 9, la búsqueda de sentido se vive como una "
    "experiencia activa y dinámica. Existe una necesidad profunda de explorar, descubrir y "
    "abrir caminos propios de comprensión. Aprender no consiste únicamente en acumular "
    "conocimientos, sino en experimentar directamente aquello que despierta tu curiosidad "
    "y amplía tu visión de la vida.\n\n"

    "Tu relación con las creencias, los estudios y las nuevas perspectivas suele estar marcada "
    "por la iniciativa. Tiendes a investigar de manera autónoma, cuestionar lo establecido y formar "
    "tus propias conclusiones a través de tu propia experiencia. Necesitas sentir que aquello que "
    "comprendes tiene una aplicación real y puede transformar tu manera de vivir.\n\n"

    "Esta posición favorece una actitud valiente frente a lo desconocido. Los viajes, los "
    "aprendizajes y los encuentros con otras culturas o formas de pensar pueden convertirse "
    "en escenarios donde descubres nuevas dimensiones de tu identidad. El crecimiento aparece "
    "cuando aceptas el desafío de ir más allá de tus límites habituales.\n\n"

    "Existe una capacidad natural para inspirar a otros mediante tus descubrimientos y "
    "compartir aquello que has aprendido. Puedes desarrollar una visión personal de la vida "
    "basada en la experiencia directa, transmitiendo entusiasmo y motivación hacia nuevos "
    "horizontes.\n\n"

    "El desafío aparece cuando la necesidad de encontrar respuestas rápidas puede llevarte a "
    "afirmar conclusiones antes de haber explorado todos los matices. Puede existir cierta "
    "impaciencia ante perspectivas diferentes o dificultad para permanecer en procesos de "
    "aprendizaje que requieren tiempo y profundidad.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera expansión no "
    "consiste solo en conquistar nuevos territorios, sino también en desarrollar una mirada "
    "más amplia y consciente. Cuando integras iniciativa y apertura, tu búsqueda de sentido "
    "se convierte en una fuente de crecimiento continuo."
),


"Tauro": (
    "Cuando Tauro ocupa la cúspide de la Casa 9, la búsqueda de sentido se construye a través "
    "de experiencias que puedan integrarse de manera estable y profunda. No buscas únicamente "
    "acumular conocimientos o explorar ideas nuevas, sino encontrar comprensiones que tengan "
    "valor práctico y puedan formar parte de tu manera de vivir.\n\n"

    "Tu relación con los estudios, las creencias y las grandes preguntas de la existencia "
    "suele desarrollarse de forma gradual. Prefieres construir una visión del mundo basada "
    "en experiencias comprobadas, aprendizajes que hayan demostrado su utilidad y principios "
    "que puedan sostenerse con el tiempo.\n\n"

    "Esta posición favorece una gran capacidad para profundizar en aquello que realmente "
    "despierta tu interés. Cuando encuentras un camino de aprendizaje que conecta contigo, "
    "puedes desarrollarlo con paciencia y constancia hasta convertirlo en una fuente sólida "
    "de conocimiento y sabiduría.\n\n"

    "Los viajes y los encuentros con otras culturas pueden tener un valor especial cuando "
    "permiten conectar con formas de vida que aportan estabilidad, belleza o una comprensión "
    "más sencilla y esencial de la existencia. La expansión ocurre a través de la experiencia "
    "sensorial y de la conexión con lo concreto.\n\n"

    "El desafío aparece cuando la necesidad de seguridad dificulta abrirte a ideas diferentes "
    "o cuestionar creencias ya establecidas. Puede existir tendencia a mantener una visión "
    "determinada simplemente porque ha proporcionado estabilidad, incluso cuando nuevas "
    "perspectivas podrían enriquecer tu comprensión.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que una verdad profunda no "
    "pierde fuerza por evolucionar. Cuando integras estabilidad y apertura, desarrollas una "
    "sabiduría práctica capaz de unir experiencia, disfrute y comprensión de la vida."
),


"Géminis": (
    "Cuando Géminis ocupa la cúspide de la Casa 9, la búsqueda de sentido se desarrolla a "
    "través de la curiosidad, el aprendizaje constante y la exploración de múltiples formas "
    "de comprender la realidad. Existe una necesidad natural de ampliar la mirada mediante "
    "ideas, conversaciones y experiencias diferentes.\n\n"

    "Tu relación con el conocimiento es dinámica. Aprender, investigar y conectar información "
    "procedente de distintas fuentes forma parte esencial de tu manera de crecer. No sueles "
    "conformarte con una única explicación, ya que necesitas comparar perspectivas y descubrir "
    "la complejidad de cada tema.\n\n"

    "Esta posición favorece una gran capacidad para transmitir conocimientos y crear puentes "
    "entre ideas diferentes. Puedes destacar compartiendo información, enseñando, escribiendo "
    "o facilitando que otras personas comprendan conceptos complejos desde una mirada más "
    "accesible.\n\n"

    "Los viajes, tanto físicos como intelectuales, tienen un papel importante en tu expansión. "
    "Cada nuevo entorno, conversación o descubrimiento puede convertirse en una pieza más dentro "
    "de una visión del mundo cada vez más amplia y flexible.\n\n"

    "El desafío aparece cuando la variedad de intereses dificulta profundizar en una dirección "
    "concreta. Puede existir tendencia a acumular información sin integrarla completamente o "
    "buscar constantemente una nueva perspectiva antes de permitir que una comprensión madure.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera sabiduría no "
    "consiste solo en conocer muchas posibilidades, sino en encontrar conexiones profundas "
    "entre ellas. Cuando integras curiosidad y profundidad, tu mente se convierte en un espacio "
    "de expansión continua."
),



"Cáncer": (
    "Cuando Cáncer ocupa la cúspide de la Casa 9, la búsqueda de sentido se encuentra "
    "profundamente vinculada con la memoria, las raíces emocionales y la necesidad de "
    "sentir una conexión personal con aquello que aprendes y descubres. No buscas únicamente "
    "respuestas intelectuales, sino comprensiones que tengan un significado emocional y "
    "puedan integrarse dentro de tu propia historia.\n\n"

    "Tu relación con las creencias, la filosofía y el conocimiento suele estar influida por "
    "las experiencias vividas y por aquello que has recibido de tus raíces. Las enseñanzas "
    "que realmente transforman tu visión del mundo son aquellas que conectan con tu sensibilidad "
    "y aportan una sensación de pertenencia o comprensión profunda de la vida.\n\n"

    "Esta posición favorece una gran capacidad para aprender desde la experiencia emocional. "
    "Puedes desarrollar una sabiduría basada en la observación de los ciclos humanos, en la "
    "comprensión de las necesidades de las personas y en la capacidad para reconocer que cada "
    "historia individual forma parte de algo más amplio.\n\n"

    "Los viajes y los encuentros con otras culturas pueden adquirir un significado especial "
    "cuando permiten sentir una conexión con otros lugares, tradiciones o formas de vivir. "
    "La expansión ocurre cuando descubres que el concepto de hogar puede ampliarse más allá "
    "de los límites conocidos.\n\n"

    "El desafío aparece cuando la necesidad de seguridad emocional dificulta abrirte a ideas "
    "o experiencias que cuestionan aquello que conoces. Puede existir tendencia a proteger "
    "determinadas creencias por su valor afectivo, incluso cuando necesitan evolucionar. "
    "En algunos momentos, el pasado puede ejercer una influencia mayor de la necesaria sobre "
    "la manera de interpretar el presente.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que las raíces no están para "
    "limitar el crecimiento, sino para ofrecer una base desde la que explorar. Cuando integras "
    "memoria y apertura, desarrollas una comprensión de la vida profundamente humana, capaz de "
    "unir experiencia personal y sabiduría universal."
),


"Leo": (
    "Cuando Leo ocupa la cúspide de la Casa 9, la búsqueda de sentido se desarrolla a través "
    "de la expresión personal, la creatividad y la necesidad de encontrar una visión de la "
    "vida que refleje quién eres realmente. El conocimiento adquiere valor cuando permite "
    "desarrollar tu identidad y expresar una perspectiva propia del mundo.\n\n"

    "Existe un impulso natural hacia la exploración de ideas, filosofías o experiencias que "
    "permitan ampliar tus horizontes. Necesitas sentir inspiración en aquello que estudias "
    "o descubres, ya que el aprendizaje se vuelve más significativo cuando despierta pasión "
    "y entusiasmo interior.\n\n"

    "Esta posición favorece una capacidad especial para transmitir conocimientos e inspirar "
    "a otras personas. Puedes convertirte en alguien que comparte una visión, enseña desde "
    "la experiencia o ayuda a otros a descubrir nuevas posibilidades. Tu comprensión de la "
    "vida suele buscar una dimensión creativa y motivadora.\n\n"

    "Los viajes y los encuentros con diferentes culturas pueden convertirse en escenarios "
    "donde descubres nuevas formas de expresar tu identidad. La expansión no consiste solo "
    "en conocer otros lugares, sino en permitir que esas experiencias amplíen la manera en "
    "que manifiestas quién eres.\n\n"

    "El desafío aparece cuando la propia visión del mundo se convierte en la única referencia "
    "válida. Puede existir dificultad para escuchar perspectivas diferentes o necesidad de "
    "sentir reconocimiento por las propias ideas y creencias. En algunos momentos puedes "
    "defender una verdad personal con tanta intensidad que pierdas curiosidad por otras "
    "posibilidades.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que una verdadera visión "
    "inspiradora no necesita imponerse para tener valor. Cuando integras confianza y humildad, "
    "tu búsqueda de sentido se convierte en una fuente de creatividad, generosidad y apertura "
    "hacia la diversidad de experiencias humanas."
),


"Virgo": (
    "Cuando Virgo ocupa la cúspide de la Casa 9, la búsqueda de sentido se desarrolla mediante "
    "el análisis, el aprendizaje práctico y la necesidad de comprender cómo funcionan las "
    "cosas en profundidad. No buscas únicamente grandes ideas, sino conocimientos que puedan "
    "aplicarse y mejorar de alguna manera la realidad cotidiana.\n\n"

    "Tu relación con los estudios, las creencias y la filosofía suele estar marcada por la "
    "observación y el discernimiento. Necesitas encontrar coherencia entre aquello que crees "
    "y aquello que realmente puede comprobarse mediante la experiencia. La sabiduría nace "
    "para ti de la integración entre comprensión y utilidad.\n\n"

    "Esta posición favorece una gran capacidad para investigar, ordenar información y extraer "
    "conclusiones precisas. Puedes desarrollar conocimientos especializados y convertirte en "
    "alguien capaz de aportar claridad en ámbitos donde existe complejidad o exceso de "
    "información.\n\n"

    "Los viajes y las experiencias de expansión adquieren mayor valor cuando ofrecen aprendizaje "
    "real y enriquecimiento práctico. No necesariamente buscas acumular experiencias por sí "
    "mismas, sino encontrar aquello que pueda ayudarte a crecer, mejorar o comprender mejor "
    "tu manera de vivir.\n\n"

    "El desafío aparece cuando la necesidad de encontrar respuestas correctas limita la apertura "
    "a perspectivas más simbólicas o intuitivas. Puede existir tendencia a analizar demasiado "
    "las experiencias antes de permitir que simplemente transformen tu manera de ver la vida. "
    "En algunos momentos, la búsqueda de perfección puede impedir disfrutar del proceso de "
    "aprendizaje.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la sabiduría no depende de "
    "tener todas las respuestas, sino de mantener una actitud abierta y consciente ante la "
    "vida. Cuando integras análisis y confianza, desarrollas una comprensión profunda capaz "
    "de unir conocimiento, servicio y crecimiento personal."
),


"Libra": (
    "Cuando Libra ocupa la cúspide de la Casa 9, la búsqueda de sentido se desarrolla a través "
    "del intercambio, la apertura hacia otras perspectivas y la necesidad de comprender la "
    "realidad desde diferentes puntos de vista. El conocimiento adquiere mayor valor cuando "
    "permite establecer puentes, generar diálogo y descubrir formas más equilibradas de "
    "relacionarse con el mundo.\n\n"

    "Tu manera de explorar ideas, creencias y filosofías suele estar marcada por la búsqueda "
    "de armonía. Antes de aceptar una visión determinada, necesitas observar cómo encaja con "
    "otras posibilidades y qué aporta al conjunto. Existe una capacidad natural para reconocer "
    "matices y encontrar puntos de encuentro entre perspectivas aparentemente diferentes.\n\n"

    "Esta posición favorece una gran sensibilidad hacia otras culturas, formas de pensamiento "
    "y sistemas de valores. Los viajes, los estudios y las experiencias que amplían tu mirada "
    "pueden convertirse en oportunidades para comprender mejor la diversidad humana y descubrir "
    "nuevas formas de cooperación.\n\n"

    "La expansión personal ocurre especialmente a través del encuentro con otras personas. "
    "Aprendes mediante conversaciones, intercambios y relaciones que desafían tu manera de "
    "interpretar la realidad. Muchas de tus comprensiones más importantes pueden surgir al "
    "escuchar una perspectiva distinta a la tuya.\n\n"

    "El desafío aparece cuando la búsqueda de equilibrio lleva a evitar tomar una posición "
    "clara o a intentar integrar tantas perspectivas que resulta difícil definir una propia. "
    "Puede existir cierta tendencia a buscar la respuesta más aceptada o armoniosa, incluso "
    "cuando una experiencia requiere defender una visión personal.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera apertura no "
    "consiste en no tener una mirada propia, sino en sostenerla con respeto hacia otras formas "
    "de comprender la vida. Cuando integras equilibrio y autenticidad, tu visión del mundo se "
    "convierte en un espacio de encuentro, belleza y comprensión compartida."
),


"Escorpio": (
    "Cuando Escorpio ocupa la cúspide de la Casa 9, la búsqueda de sentido se vive con "
    "intensidad y profundidad. No suele bastar con aceptar respuestas superficiales; existe "
    "una necesidad de investigar aquello que se encuentra detrás de las apariencias y descubrir "
    "las fuerzas más profundas que dan forma a la experiencia humana.\n\n"

    "Tu relación con las creencias, la filosofía y el conocimiento suele estar marcada por "
    "procesos de transformación. Las ideas que realmente te impactan son aquellas capaces de "
    "modificar tu manera de comprender la vida y cuestionar antiguos sistemas de pensamiento. "
    "Aprender implica aquí una evolución interna, no solo una acumulación de información.\n\n"

    "Esta posición favorece una gran capacidad para profundizar en temas complejos, investigar "
    "lo oculto y comprender dimensiones psicológicas, simbólicas o existenciales de la realidad. "
    "Puedes sentir atracción por conocimientos que exploran los grandes misterios de la vida, "
    "los procesos de cambio y aquello que normalmente permanece invisible.\n\n"

    "Los viajes y las experiencias de expansión pueden actuar como momentos de renacimiento "
    "personal. Más que buscar simplemente conocer otros lugares, necesitas atravesar experiencias "
    "que transformen tu visión del mundo y te permitan regresar con una comprensión más profunda "
    "de quién eres.\n\n"

    "El desafío aparece cuando la intensidad de la búsqueda puede llevar a desconfiar de ideas "
    "que no encajan con tu propia percepción o a mantener una relación demasiado rígida con "
    "determinadas creencias. En algunos momentos puede existir una necesidad de encontrar una "
    "verdad definitiva que reduzca la incertidumbre propia de la vida.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la sabiduría no surge de "
    "poseer una verdad absoluta, sino de permitir que la vida transforme continuamente "
    "tu comprensión. Cuando integras profundidad y apertura, desarrollas una visión poderosa "
    "capaz de acompañar procesos de cambio y revelar significados ocultos."
),


"Sagitario": (
    "Cuando Sagitario ocupa la cúspide de la Casa 9, la búsqueda de sentido se convierte en "
    "una necesidad fundamental. Existe un impulso natural hacia la exploración, el aprendizaje "
    "y la ampliación constante de horizontes. La vida adquiere sentido cuando puedes descubrir "
    "nuevas perspectivas y sentir que tu camino continúa expandiéndose.\n\n"

    "Tu relación con el conocimiento suele estar marcada por la curiosidad y el entusiasmo. "
    "Aprender no es únicamente adquirir información, sino abrir puertas hacia nuevas formas "
    "de comprender la existencia. Puedes sentir una fuerte conexión con la filosofía, la "
    "espiritualidad, otras culturas o cualquier campo que permita ampliar tu visión.\n\n"

    "Esta posición favorece una actitud optimista y una gran capacidad para inspirar a otras "
    "personas con tus ideas. Sueles buscar el significado más amplio de las experiencias y "
    "comprender los acontecimientos dentro de un contexto mayor. Tu visión puede ayudarte a "
    "mantener esperanza incluso en momentos de incertidumbre.\n\n"

    "Los viajes, los estudios y los encuentros con diferentes formas de vida adquieren un papel "
    "transformador. Cada nueva experiencia puede convertirse en una oportunidad para cuestionar "
    "límites anteriores y descubrir una versión más amplia de quién eres.\n\n"

    "El desafío aparece cuando la necesidad de expansión dificulta profundizar en aquello que "
    "ya tienes delante. Puede surgir cierta inquietud ante la rutina o una tendencia a buscar "
    "siempre una nueva experiencia antes de integrar completamente la anterior. También puede "
    "existir el riesgo de convertir las propias creencias en certezas difíciles de cuestionar.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera expansión no "
    "consiste únicamente en recorrer grandes distancias, sino en desarrollar una comprensión "
    "cada vez más profunda de la vida. Cuando integras entusiasmo y compromiso, tu visión se "
    "convierte en una fuente de inspiración, aprendizaje y crecimiento continuo."
),


"Capricornio": (
    "Cuando Capricornio ocupa la cúspide de la Casa 9, la búsqueda de sentido se desarrolla "
    "de forma gradual, estructurada y orientada hacia la construcción de una visión sólida de "
    "la vida. No sueles aceptar ideas únicamente porque resulten inspiradoras; necesitas "
    "comprobar su coherencia, su utilidad y su capacidad para sostenerse con el paso del tiempo.\n\n"

    "Tu relación con el conocimiento, los estudios y las creencias suele estar marcada por la "
    "responsabilidad y la perseverancia. Puedes dedicar muchos años a desarrollar una comprensión "
    "profunda de un tema, valorando especialmente aquello que requiere esfuerzo, disciplina y "
    "compromiso. La sabiduría nace aquí de la experiencia acumulada y de las lecciones aprendidas "
    "a través del recorrido vital.\n\n"

    "Esta posición favorece una visión realista y madura del mundo. Tiendes a buscar principios "
    "que puedan aplicarse en la práctica y que ayuden a construir una vida con dirección y "
    "propósito. Más que acumular conocimientos por curiosidad, necesitas que aquello que aprendes "
    "forme parte de una estructura que aporte significado y orientación.\n\n"

    "Los viajes y las experiencias de expansión suelen adquirir valor cuando contribuyen a tu "
    "desarrollo personal o profesional. Puedes sentir una especial atracción por lugares, culturas "
    "o tradiciones que poseen historia, profundidad o una enseñanza capaz de transformar tu manera "
    "de comprender la realidad.\n\n"

    "El desafío aparece cuando la necesidad de seguridad intelectual puede limitar la apertura "
    "a nuevas perspectivas. En algunos momentos puedes aferrarte demasiado a aquello que ha "
    "demostrado funcionar o sentir que solo las ideas construidas con esfuerzo tienen verdadero "
    "valor. También puede existir una tendencia a tomarte demasiado en serio la búsqueda de "
    "respuestas.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la sabiduría no depende solo "
    "de acumular experiencia, sino también de mantener la capacidad de sorprenderte y aprender. "
    "Cuando integras estructura y apertura, desarrollas una visión profunda y serena capaz de "
    "convertir el conocimiento en una verdadera guía de vida."
),


"Acuario": (
    "Cuando Acuario ocupa la cúspide de la Casa 9, la búsqueda de sentido se desarrolla a través "
    "de la exploración de ideas diferentes, perspectivas innovadoras y formas alternativas de "
    "comprender la realidad. Existe una necesidad natural de cuestionar aquello que se da por "
    "establecido y descubrir nuevas posibilidades que amplíen la visión del mundo.\n\n"

    "Tu relación con el conocimiento suele ser libre y poco convencional. Puedes sentir "
    "atracción por teorías, disciplinas o sistemas de pensamiento que desafían las estructuras "
    "tradicionales y ofrecen una mirada más amplia sobre la humanidad y su evolución. Aprender "
    "significa para ti abrir espacios nuevos de comprensión.\n\n"

    "Esta posición favorece una gran capacidad para conectar ideas aparentemente alejadas y "
    "observar la realidad desde perspectivas originales. Puedes desarrollar una visión muy "
    "personal sobre la vida, combinando diferentes fuentes de conocimiento y creando una "
    "comprensión propia que no depende completamente de lo establecido.\n\n"

    "Los viajes y los encuentros con otras culturas pueden ampliar especialmente tu percepción "
    "de la sociedad y del futuro. Sueles sentir interés por comunidades, movimientos colectivos "
    "o experiencias que muestran nuevas formas de organizar la vida y relacionarse con el mundo.\n\n"

    "El desafío aparece cuando la necesidad de independencia intelectual puede generar distancia "
    "respecto a conocimientos más tradicionales o experiencias emocionales más cercanas. En "
    "algunos momentos puede existir una tendencia a valorar más lo novedoso que aquello que ha "
    "demostrado profundidad con el tiempo. También puede aparecer cierta dificultad para "
    "comprometerte con una visión concreta al querer mantener siempre todas las posibilidades "
    "abiertas.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera innovación nace "
    "cuando las nuevas ideas pueden dialogar con la experiencia acumulada. Cuando integras "
    "libertad y conexión, tu búsqueda de sentido se convierte en una fuente de inspiración "
    "para comprender la evolución humana y aportar nuevas formas de mirar la realidad."
),


"Piscis": (
    "Cuando Piscis ocupa la cúspide de la Casa 9, la búsqueda de sentido se desarrolla a través "
    "de la intuición, la sensibilidad y la percepción de una realidad que va más allá de lo "
    "visible. Existe una necesidad profunda de encontrar una conexión espiritual o simbólica "
    "con la vida, comprendiendo que la experiencia humana contiene dimensiones que no siempre "
    "pueden explicarse únicamente mediante la razón.\n\n"

    "Tu relación con el conocimiento y las creencias suele estar guiada por la experiencia "
    "interior. Más que acumular conceptos, buscas aquello que pueda tocarte emocionalmente y "
    "transformar tu manera de sentir la existencia. Las enseñanzas adquieren valor cuando "
    "despiertan una comprensión profunda y una sensación de unidad con algo más amplio.\n\n"

    "Esta posición favorece una gran imaginación, empatía y capacidad para percibir conexiones "
    "sutiles entre diferentes experiencias. Puedes sentir afinidad por caminos espirituales, "
    "artísticos o simbólicos que permitan explorar dimensiones profundas de la consciencia y "
    "la naturaleza humana.\n\n"

    "Los viajes y las experiencias de expansión pueden convertirse en procesos internos además "
    "de externos. No siempre necesitas alejarte físicamente para descubrir nuevos mundos; a "
    "menudo son los cambios de percepción, los encuentros significativos o las experiencias "
    "inspiradoras los que amplían verdaderamente tu horizonte.\n\n"

    "El desafío aparece cuando la apertura y la sensibilidad dificultan establecer criterios "
    "claros sobre aquello que realmente integra sabiduría y aquello que solo resulta atractivo "
    "emocionalmente. Puede existir tendencia a idealizar determinadas creencias o a buscar "
    "respuestas que eviten enfrentarte a aspectos más concretos de la realidad.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera conexión "
    "espiritual no necesita separarse de la experiencia cotidiana. Cuando integras intuición "
    "y discernimiento, desarrollas una visión compasiva y profunda capaz de encontrar sentido "
    "en la totalidad de la experiencia humana."
),

}


CASA_10 = {

"Aries": (
    "Cuando Aries ocupa la cúspide de la Casa 10, la vocación se desarrolla a través de la "
    "iniciativa, la autonomía y el deseo de abrir caminos propios. Existe una necesidad "
    "profunda de sentir que tu trayectoria profesional o social refleja tu capacidad para "
    "actuar, decidir y poner en marcha proyectos que lleven tu propia dirección. La realización "
    "aparece cuando puedes asumir retos y participar activamente en la construcción de tu futuro.\n\n"

    "Tu relación con los objetivos y la proyección pública suele estar marcada por el impulso "
    "de avanzar. Difícilmente te satisface permanecer en posiciones donde no puedes aportar, "
    "liderar o experimentar un margen suficiente de libertad. Necesitas sentir que tu esfuerzo "
    "genera movimiento y que tus decisiones tienen una influencia directa sobre aquello que "
    "construyes.\n\n"

    "Esta posición favorece una actitud emprendedora y una gran capacidad para iniciar procesos. "
    "Puedes destacar especialmente en situaciones donde sea necesario tomar la iniciativa, "
    "afrontar desafíos o actuar con rapidez ante nuevas oportunidades. Tu desarrollo profesional "
    "se fortalece cuando confías en tu capacidad para abrir posibilidades allí donde todavía no "
    "existen caminos definidos.\n\n"

    "La imagen que proyectas hacia el exterior suele estar relacionada con la determinación y "
    "la capacidad de acción. Las personas pueden percibir en ti una energía directa, resolutiva "
    "y orientada hacia los resultados. Existe una tendencia natural a asumir responsabilidades "
    "cuando una situación necesita dirección o alguien que dé el primer paso.\n\n"

    "El desafío aparece cuando la necesidad de avanzar rápidamente dificulta aceptar procesos "
    "más lentos o colaborativos. Puede surgir impaciencia ante estructuras que requieren tiempo, "
    "así como cierta dificultad para reconocer que algunos logros importantes necesitan ser "
    "construidos junto a otras personas. En algunos momentos, querer demostrar capacidad puede "
    "llevarte a asumir más responsabilidades de las que realmente puedes sostener.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que liderar no consiste únicamente "
    "en iniciar, sino también en desarrollar la capacidad de mantener una dirección elegida con "
    "madurez. Cuando integras impulso y perseverancia, tu trayectoria se convierte en una "
    "expresión auténtica de valentía, iniciativa y capacidad para inspirar movimiento en los "
    "demás."
),


"Tauro": (
    "Cuando Tauro ocupa la cúspide de la Casa 10, la vocación se construye de manera gradual, "
    "estable y orientada hacia resultados que puedan mantenerse en el tiempo. Existe una "
    "necesidad profunda de desarrollar una trayectoria sólida, donde el esfuerzo realizado "
    "pueda convertirse en algo concreto y duradero. La realización llega cuando percibes que "
    "estás creando un valor real y sostenible.\n\n"

    "Tu relación con los objetivos profesionales suele estar marcada por la constancia y la "
    "paciencia. Prefieres avanzar paso a paso, consolidando cada etapa antes de iniciar la "
    "siguiente. Más que buscar reconocimientos rápidos, tiendes a valorar aquello que puede "
    "construirse con dedicación y que mantiene su importancia con el paso del tiempo.\n\n"

    "Esta posición favorece una gran capacidad para desarrollar proyectos a largo plazo y "
    "administrar recursos con sentido práctico. Puedes destacar en ámbitos donde sean "
    "necesarias la perseverancia, la estabilidad, la calidad y la capacidad para transformar "
    "una idea inicial en una realidad concreta.\n\n"

    "La imagen que proyectas hacia el exterior suele transmitir confianza, serenidad y "
    "fiabilidad. Otras personas pueden percibir en ti una capacidad natural para sostener "
    "responsabilidades y mantener el compromiso incluso cuando los resultados requieren "
    "tiempo. Tu presencia profesional suele asociarse con la coherencia y la solidez.\n\n"

    "El desafío aparece cuando la búsqueda de seguridad puede dificultar aceptar cambios "
    "necesarios en la trayectoria profesional. Puede existir resistencia a abandonar caminos "
    "conocidos aunque ya no aporten crecimiento, simplemente porque representan una base "
    "estable. En algunos momentos también puede aparecer una tendencia a valorar demasiado "
    "la comodidad frente a nuevas posibilidades.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera estabilidad "
    "no depende únicamente de conservar lo construido, sino de confiar en la propia capacidad "
    "para crear valor en diferentes circunstancias. Cuando integras constancia y flexibilidad, "
    "tu trayectoria transmite una sensación de permanencia, calidad y crecimiento auténtico."
),


"Géminis": (
    "Cuando Géminis ocupa la cúspide de la Casa 10, la vocación se desarrolla a través del "
    "aprendizaje, la comunicación y la capacidad para adaptarte a contextos cambiantes. "
    "Existe una necesidad profunda de mantener la mente activa y de construir una trayectoria "
    "donde puedas explorar diferentes intereses, conectar conocimientos y evolucionar "
    "constantemente.\n\n"

    "Tu relación con el mundo profesional suele enriquecerse mediante el intercambio de ideas "
    "y la posibilidad de desempeñar funciones variadas. Las estructuras demasiado rígidas "
    "pueden limitar tu motivación, mientras que los entornos donde existe movimiento, "
    "información y contacto con diferentes personas favorecen tu desarrollo.\n\n"

    "Esta posición favorece habilidades relacionadas con la comunicación, la enseñanza, la "
    "investigación, la escritura o cualquier ámbito donde la información pueda convertirse en "
    "una herramienta de conexión. Tu capacidad para aprender rápidamente y relacionar conceptos "
    "diversos puede convertirse en uno de tus principales recursos profesionales.\n\n"

    "La imagen que proyectas hacia el exterior suele estar vinculada con la inteligencia, la "
    "curiosidad y la capacidad de comprender diferentes perspectivas. Las personas pueden percibir en ti a "
    "alguien versátil, capaz de moverse entre distintos ambientes y aportar soluciones desde "
    "una mirada amplia.\n\n"

    "El desafío aparece cuando la variedad de intereses dificulta consolidar una dirección "
    "profesional concreta. Puede surgir dispersión, dificultad para mantener un mismo objetivo "
    "durante mucho tiempo o la sensación de que elegir un camino implica renunciar a demasiadas "
    "posibilidades. En algunos momentos, la búsqueda constante de novedades puede alejarte de "
    "procesos que requieren profundidad.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la versatilidad alcanza su "
    "mayor valor cuando encuentra una estructura donde expresarse. Cuando integras curiosidad "
    "y compromiso, tu trayectoria profesional se convierte en un espacio de aprendizaje "
    "continuo, comunicación y conexión entre diferentes mundos."
),



"Cáncer": (
    "Cuando Cáncer ocupa la cúspide de la Casa 10, la vocación se desarrolla a través del "
    "cuidado, la sensibilidad y la capacidad para generar espacios donde otras personas puedan "
    "sentirse sostenidas. Existe una necesidad profunda de encontrar un propósito profesional "
    "que tenga una dimensión humana y que permita aportar protección, comprensión o bienestar "
    "a quienes forman parte de tu entorno.\n\n"

    "Tu relación con la trayectoria profesional suele estar vinculada con el sentido de "
    "pertenencia. No basta con realizar una actividad; necesitas sentir que aquello a lo que "
    "dedicas tu energía tiene una conexión emocional y representa algo importante para ti. "
    "Los proyectos que permiten crear vínculos, acompañar procesos o construir algo con raíces "
    "profundas suelen despertar una motivación especial.\n\n"

    "Esta posición favorece una gran capacidad para comprender las necesidades del entorno y "
    "adaptarte a los cambios que surgen dentro de un equipo o una comunidad. Puedes desarrollar "
    "talento en ámbitos relacionados con la atención a personas, la educación, el acompañamiento "
    "o cualquier actividad donde la sensibilidad constituya una verdadera herramienta.\n\n"

    "La imagen que proyectas hacia el exterior suele transmitir cercanía, confianza y una "
    "disposición natural para cuidar. Otras personas pueden percibir en ti una presencia "
    "acogedora, alguien capaz de sostener responsabilidades desde la empatía y no únicamente "
    "desde la autoridad formal.\n\n"

    "El desafío aparece cuando la implicación emocional con el trabajo dificulta establecer "
    "límites claros. Puede surgir una tendencia a cargar con responsabilidades ajenas, buscar "
    "demasiada aprobación o sentir que tu valor depende de cuánto eres capaz de aportar a los "
    "demás. En algunos momentos, proteger aquello que has construido puede dificultar abrirte "
    "a nuevas etapas profesionales.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que cuidar a otros comienza por "
    "reconocer también tus propias necesidades. Cuando integras sensibilidad y límites sanos, "
    "tu trayectoria profesional se convierte en una expresión de humanidad, capacidad de "
    "acompañamiento y una forma profunda de contribuir al mundo."
),


"Leo": (
    "Cuando Leo ocupa la cúspide de la Casa 10, la vocación se desarrolla a través de la "
    "expresión personal, la creatividad y el deseo de aportar algo que lleve tu sello propio. "
    "Existe una necesidad profunda de sentir que tu trayectoria refleja quién eres y que puedes "
    "ocupar un lugar donde tus talentos sean visibles y tengan la oportunidad de desarrollarse.\n\n"

    "Tu relación con los objetivos profesionales suele estar marcada por la búsqueda de "
    "significado y reconocimiento. No se trata únicamente de alcanzar una posición destacada, "
    "sino de sentir orgullo por aquello que construyes y saber que tu esfuerzo expresa una "
    "parte auténtica de ti. La motivación aumenta cuando puedes crear, liderar o inspirar.\n\n"

    "Esta posición favorece capacidades relacionadas con la dirección, la creatividad, la "
    "comunicación y la capacidad para motivar a otras personas. Puedes destacar en ámbitos "
    "donde sea importante aportar una visión personal, asumir protagonismo o transmitir "
    "entusiasmo hacia un proyecto compartido.\n\n"

    "La imagen que proyectas hacia el exterior suele estar asociada con la confianza, la "
    "presencia y la capacidad de ocupar un espacio propio. Las personas pueden percibir en ti "
    "una energía inspiradora y una disposición natural para asumir responsabilidades cuando "
    "sientes conexión con aquello que realizas.\n\n"

    "El desafío aparece cuando la necesidad de reconocimiento externo comienza a definir el "
    "valor de tu trayectoria. Puede surgir presión por demostrar constantemente tus capacidades "
    "o dificultad para aceptar etapas donde el crecimiento ocurre de manera más silenciosa. "
    "También puede aparecer resistencia a compartir protagonismo cuando una situación requiere "
    "un liderazgo más colectivo.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera autoridad nace "
    "de la autenticidad y no únicamente de la visibilidad. Cuando integras creatividad y "
    "humildad, tu vocación se convierte en una fuente de inspiración capaz de iluminar también "
    "el potencial de quienes te rodean."
),


"Virgo": (
    "Cuando Virgo ocupa la cúspide de la Casa 10, la vocación se desarrolla a través del "
    "servicio, la mejora continua y la capacidad para aportar soluciones concretas. Existe "
    "una necesidad profunda de sentir que tu trabajo tiene utilidad y que aquello que haces "
    "contribuye a perfeccionar, ordenar o hacer más eficiente algún aspecto de la realidad.\n\n"

    "Tu relación con la trayectoria profesional suele estar marcada por la dedicación y el "
    "aprendizaje constante. Prefieres construir una reputación basada en la competencia, la "
    "responsabilidad y la calidad de lo que aportas antes que en la búsqueda de reconocimiento "
    "rápido. El valor profesional nace de la experiencia desarrollada con el tiempo.\n\n"

    "Esta posición favorece una gran capacidad de análisis, organización y atención al detalle. "
    "Puedes destacar en ámbitos donde sean importantes la precisión, la investigación, la "
    "gestión de procesos o la capacidad para detectar aquello que necesita ser mejorado. Tu "
    "mirada práctica se convierte en un recurso fundamental para resolver problemas.\n\n"

    "La imagen que proyectas hacia el exterior suele transmitir profesionalidad, fiabilidad y "
    "compromiso. Otras personas pueden percibir en ti rigor, preparación y capacidad "
    "para asumir responsabilidades con seriedad. Tu credibilidad suele construirse mediante hechos "
    "más que mediante una necesidad de destacar.\n\n"

    "El desafío aparece cuando la exigencia profesional se convierte en una medida constante "
    "del propio valor. Puede surgir perfeccionismo, dificultad para reconocer logros o sensación "
    "de que siempre falta algo antes de contar con suficiente preparación. En algunos momentos, "
    "el deseo de hacerlo bien puede limitar la espontaneidad o la confianza en tus capacidades.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la excelencia no requiere "
    "perfección, sino presencia y consciencia en el proceso. Cuando integras disciplina y "
    "aceptación, tu trayectoria profesional expresa una combinación muy valiosa de servicio, "
    "conocimiento y capacidad para mejorar el mundo que te rodea."
),


"Libra": (
    "Cuando Libra ocupa la cúspide de la Casa 10, la vocación se desarrolla a través de la "
    "cooperación, el equilibrio y la capacidad para crear vínculos significativos dentro del "
    "mundo profesional. Existe una necesidad profunda de construir una trayectoria donde las "
    "relaciones, la colaboración y el sentido de armonía tengan un papel importante. La "
    "realización aparece cuando puedes aportar belleza, diálogo o comprensión al entorno.\n\n"

    "Tu relación con los objetivos profesionales suele estar marcada por la búsqueda de "
    "acuerdos y espacios donde diferentes perspectivas puedan convivir. Las estructuras "
    "excesivamente competitivas o rígidas pueden resultar poco motivadoras, mientras que los "
    "ambientes donde existe intercambio, negociación y cooperación favorecen tu desarrollo.\n\n"

    "Esta posición favorece capacidades relacionadas con la mediación, la comunicación, la "
    "estética, las relaciones públicas y cualquier ámbito donde sea necesario comprender las "
    "necesidades de diferentes personas. Tu habilidad para observar varios puntos de vista "
    "puede convertirse en una herramienta profesional de gran valor.\n\n"

    "La imagen que proyectas hacia el exterior suele transmitir diplomacia, elegancia y "
    "capacidad para generar confianza. Otras personas pueden percibir en ti una presencia "
    "conciliadora, alguien capaz de encontrar soluciones equilibradas y favorecer entornos "
    "donde la cooperación sea posible.\n\n"

    "El desafío aparece cuando el deseo de mantener la armonía puede dificultar tomar "
    "decisiones firmes o defender una dirección propia. Puede surgir una tendencia a adaptar "
    "demasiado tu trayectoria a las expectativas externas o a buscar aprobación antes de "
    "reconocer el valor de tus propias elecciones. En algunos momentos, evitar el conflicto "
    "puede retrasar cambios necesarios para tu crecimiento.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera colaboración "
    "nace cuando cada persona aporta su identidad completa. Cuando integras diplomacia y "
    "autenticidad, tu trayectoria profesional se convierte en un espacio donde unir personas, "
    "crear equilibrio y aportar una visión más armónica al mundo."
),


"Escorpio": (
    "Cuando Escorpio ocupa la cúspide de la Casa 10, la vocación se desarrolla a través de la "
    "transformación, la profundidad y la capacidad para afrontar procesos complejos. Existe una "
    "necesidad profunda de dedicar tu energía a algo que tenga significado y que permita generar "
    "un cambio real, tanto en tu propia vida como en el entorno donde participas.\n\n"

    "Tu relación con la trayectoria profesional suele estar marcada por la intensidad y el "
    "compromiso. Difícilmente encuentras satisfacción en actividades que percibes como vacías o "
    "superficiales; necesitas sentir que aquello que haces tiene una dimensión profunda y que "
    "puede contribuir a resolver, transformar o regenerar alguna realidad.\n\n"

    "Esta posición favorece una gran capacidad para investigar, comprender motivaciones ocultas "
    "y manejar situaciones donde se requiere fortaleza emocional. Puedes destacar en ámbitos "
    "relacionados con la psicología, la investigación, la gestión de crisis, la transformación "
    "social o cualquier área donde sea necesario atravesar procesos de cambio.\n\n"

    "La imagen que proyectas hacia el exterior suele transmitir intensidad, determinación y "
    "una presencia difícil de ignorar. Otras personas pueden percibir en ti una capacidad "
    "natural para sostener situaciones complejas y mirar más allá de las apariencias, incluso "
    "cuando otros prefieren evitar determinados temas.\n\n"

    "El desafío aparece cuando la necesidad de control o profundidad puede convertirse en "
    "rigidez frente a los cambios profesionales. Puede existir dificultad para soltar etapas "
    "que ya han cumplido su función o tendencia a cargar con demasiada responsabilidad en "
    "procesos de transformación. En algunos momentos, la intensidad con la que vives tus "
    "objetivos puede dificultar el descanso o la flexibilidad.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera fuerza no "
    "consiste en controlar todos los procesos, sino en confiar en la capacidad de renovarte. "
    "Cuando integras profundidad y apertura, tu trayectoria se convierte en una expresión de "
    "poder transformador, consciencia y capacidad para generar cambios significativos."
),


"Sagitario": (
    "Cuando Sagitario ocupa la cúspide de la Casa 10, la vocación se desarrolla a través de "
    "la expansión, la búsqueda de sentido y la necesidad de participar en proyectos que amplíen "
    "horizontes. Existe un impulso natural a construir una trayectoria que no se limite a "
    "cumplir funciones, sino que permita transmitir conocimientos, explorar posibilidades y "
    "contribuir con una visión más amplia.\n\n"

    "Tu relación con los objetivos profesionales suele estar marcada por el entusiasmo y la "
    "búsqueda de crecimiento. Necesitas sentir que avanzas, que aprendes y que tu camino mantiene "
    "una conexión con algo que consideras importante. Las actividades demasiado repetitivas o "
    "sin posibilidad de evolución pueden reducir tu motivación.\n\n"

    "Esta posición favorece capacidades relacionadas con la enseñanza, la comunicación de ideas, "
    "la investigación, los viajes, la cultura o cualquier ámbito donde puedas compartir una "
    "visión amplia de la realidad. Existe una facilidad natural para inspirar a otras personas y transmitir "
    "confianza en las posibilidades futuras.\n\n"

    "La imagen que proyectas hacia el exterior suele estar asociada con optimismo, apertura y "
    "capacidad para ver más allá de las circunstancias inmediatas. Otras personas pueden percibir "
    "en ti una energía motivadora, alguien capaz de aportar perspectiva cuando una situación "
    "parece limitada o difícil de comprender.\n\n"

    "El desafío aparece cuando el deseo de expansión puede dificultar consolidar una dirección "
    "concreta. Puede surgir tendencia a buscar constantemente nuevas oportunidades antes de "
    "desarrollar plenamente las actuales, o cierta dificultad para aceptar las estructuras "
    "necesarias para alcanzar objetivos a largo plazo. En algunos momentos, la confianza puede "
    "llevar a subestimar detalles importantes del proceso.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera expansión no "
    "depende solo de alcanzar nuevos horizontes, sino de profundizar en aquello que eliges "
    "construir. Cuando integras entusiasmo y compromiso, tu vocación se convierte en una fuente "
    "de inspiración, aprendizaje y crecimiento compartido."
),


"Capricornio": (
    "Cuando Capricornio ocupa la cúspide de la Casa 10, la vocación se desarrolla a través de "
    "la construcción gradual, la responsabilidad y la capacidad para alcanzar objetivos a largo "
    "plazo. Existe una necesidad profunda de crear una trayectoria sólida, basada en el esfuerzo, "
    "la constancia y la sensación de estar desarrollando algo que pueda permanecer en el tiempo.\n\n"

    "Tu relación con el mundo profesional suele estar marcada por el compromiso y la ambición "
    "entendida como deseo de crecimiento. No acostumbras a buscar únicamente resultados "
    "inmediatos, sino que prefieres avanzar mediante etapas que permitan consolidar experiencia, "
    "conocimiento y autoridad. Para ti, la confianza en una trayectoria se construye demostrando "
    "con hechos aquello que eres capaz de aportar.\n\n"

    "Esta posición favorece una gran capacidad organizativa, sentido estratégico y perseverancia "
    "ante los desafíos. Puedes desarrollar una especial habilidad para asumir responsabilidades, "
    "gestionar proyectos complejos y convertir objetivos abstractos en estructuras concretas. "
    "La paciencia y la disciplina se convierten en herramientas fundamentales para alcanzar "
    "aquello que te propones.\n\n"

    "La imagen que proyectas hacia el exterior suele transmitir seriedad, madurez y fiabilidad. "
    "Otras personas pueden percibir en ti una presencia capaz de sostener responsabilidades y "
    "mantener el rumbo incluso cuando aparecen dificultades. Con frecuencia desarrollas una "
    "reputación basada en la coherencia, la profesionalidad y la capacidad para cumplir aquello "
    "que asumes.\n\n"

    "El desafío aparece cuando la responsabilidad puede convertirse en una carga excesiva o "
    "cuando la necesidad de alcanzar determinados objetivos hace que olvides disfrutar del "
    "proceso. Puede surgir una tendencia a medir tu valor únicamente por tus logros, tu posición "
    "o aquello que consigues construir. En algunos momentos también puede existir temor a "
    "equivocarte o a mostrar aspectos más vulnerables de tu mundo interior en el ámbito profesional.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera autoridad no "
    "depende únicamente del reconocimiento externo, sino de la integración entre experiencia, "
    "sabiduría y autenticidad. Cuando permites que el éxito incluya también bienestar y sentido "
    "personal, tu trayectoria se convierte en una expresión de madurez, liderazgo consciente y "
    "capacidad para construir algo valioso."
),


"Acuario": (
    "Cuando Acuario ocupa la cúspide de la Casa 10, la vocación se desarrolla a través de la "
    "innovación, la independencia y la necesidad de aportar una visión diferente al mundo. "
    "Existe un impulso natural a cuestionar modelos establecidos y encontrar nuevas formas de "
    "participar en la sociedad, buscando una trayectoria profesional que conserve espacio para "
    "la libertad y la originalidad.\n\n"

    "Tu relación con los objetivos profesionales suele estar marcada por la necesidad de sentir "
    "que aquello que haces tiene una dimensión colectiva o aporta una mejora significativa. "
    "Difícilmente encuentras satisfacción en estructuras demasiado rígidas donde no existe "
    "posibilidad de proponer, experimentar o introducir nuevas perspectivas.\n\n"

    "Esta posición favorece capacidades relacionadas con la tecnología, la innovación, los "
    "proyectos sociales, la investigación, la comunicación de ideas y cualquier ámbito donde "
    "sea necesario imaginar posibilidades futuras. Existe facilidad para detectar tendencias, "
    "conectar conceptos diferentes y aportar soluciones poco convencionales.\n\n"

    "La imagen que proyectas hacia el exterior suele transmitir independencia, creatividad y "
    "una manera propia de entender la realidad. Otras personas pueden percibir en ti una "
    "personalidad diferente, alguien que no teme explorar caminos alternativos cuando los "
    "existentes ya no responden a las necesidades del momento.\n\n"

    "El desafío aparece cuando la necesidad de libertad puede dificultar la adaptación a ciertas "
    "estructuras o compromisos necesarios para desarrollar una trayectoria. Puede surgir cierta "
    "resistencia hacia la autoridad, las normas establecidas o los procesos demasiado "
    "tradicionales. En algunos momentos, la necesidad de diferenciarte puede llevarte a rechazar "
    "opciones válidas simplemente porque no representan una ruptura suficiente con lo conocido.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que innovar no significa "
    "oponerse constantemente a lo existente, sino aportar una nueva visión capaz de integrarse "
    "con aquello que funciona. Cuando unes independencia y cooperación, tu trayectoria puede "
    "convertirse en un espacio donde las ideas del futuro encuentran una forma concreta de "
    "manifestarse en el mundo."
),


"Piscis": (
    "Cuando Piscis ocupa la cúspide de la Casa 10, la vocación se desarrolla a través de la "
    "sensibilidad, la intuición y la necesidad de aportar significado a aquello que haces. "
    "Existe una búsqueda profunda de una trayectoria que no sea únicamente funcional, sino que "
    "también conecte con valores internos, creatividad o una sensación de contribución hacia "
    "algo más amplio que el propio interés personal.\n\n"

    "Tu relación con el mundo profesional suele estar guiada por la percepción y la inspiración. "
    "Necesitas sentir una conexión emocional con tus objetivos y encontrar un sentido que "
    "trascienda la simple consecución de resultados. Las actividades donde puedes acompañar, "
    "crear, sanar, imaginar o aportar sensibilidad suelen despertar una motivación especial.\n\n"

    "Esta posición favorece capacidades relacionadas con el arte, la ayuda a otras personas, "
    "la espiritualidad, la creatividad, la imaginación y todos aquellos ámbitos donde la "
    "intuición y la comprensión profunda de la experiencia humana tienen valor. Existe una "
    "facilidad especial para captar necesidades colectivas y responder desde la empatía.\n\n"

    "La imagen que proyectas hacia el exterior suele transmitir sensibilidad, humanidad y una "
    "cierta cualidad inspiradora. Otras personas pueden percibir en ti una presencia capaz de "
    "comprender realidades complejas sin reducirlas únicamente a datos o explicaciones "
    "racionales. Tu manera de aportar puede influir más por la conexión que generas que por la "
    "imposición de una dirección concreta.\n\n"

    "El desafío aparece cuando la sensibilidad puede dificultar establecer límites claros en el "
    "ámbito profesional. Puede surgir tendencia a adaptarte demasiado a las circunstancias, "
    "asumir responsabilidades ajenas o perder de vista tus propios objetivos al intentar "
    "responder a las necesidades del entorno. En algunos momentos también puede resultar difícil "
    "definir una dirección concreta cuando existen demasiadas posibilidades abiertas.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la inspiración necesita una "
    "estructura para poder manifestarse plenamente. Cuando integras intuición y organización, "
    "tu vocación se convierte en un canal capaz de unir sensibilidad, creatividad y servicio, "
    "aportando al mundo una mirada más humana, profunda y consciente."
),

}


CASA_11 = {

"Aries": (
    "Cuando Aries ocupa la cúspide de la Casa 11, la relación con los grupos, las amistades "
    "y los proyectos colectivos se vive desde la iniciativa y la necesidad de participar "
    "activamente. Existe un impulso natural a formar parte de movimientos donde puedas aportar "
    "energía, abrir caminos o impulsar nuevas ideas. No suelen resultarte cómodos los espacios "
    "donde únicamente se espera que sigas una dirección marcada por otros.\n\n"

    "Los vínculos sociales adquieren mayor sentido cuando existe movimiento, entusiasmo y una "
    "sensación de estar construyendo algo hacia el futuro. Tiendes a acercarte a personas "
    "dinámicas, independientes o con espíritu emprendedor, ya que los intercambios que más "
    "te enriquecen son aquellos que despiertan acción y crecimiento.\n\n"

    "Esta posición favorece la capacidad para liderar grupos, iniciar proyectos colectivos y "
    "convertirte en una fuerza impulsora dentro de una comunidad. A menudo puedes ser quien "
    "propone una nueva dirección, quien impulsa a dar el primer paso o quien moviliza recursos "
    "cuando un objetivo compartido necesita energía renovadora.\n\n"

    "Tu visión del futuro suele construirse a través de la experiencia directa. Aprendes sobre "
    "los demás participando, colaborando y comprobando en la práctica qué relaciones y proyectos "
    "responden realmente a tus valores. La comunidad se convierte en un espacio donde descubres "
    "nuevas facetas de tu identidad.\n\n"

    "El desafío aparece cuando la necesidad de actuar rápidamente puede dificultar escuchar "
    "otros ritmos o integrar perspectivas diferentes. Puede surgir cierta impaciencia dentro "
    "de los grupos o una tendencia a asumir demasiadas iniciativas sin considerar si todas "
    "pueden sostenerse a largo plazo. En algunos momentos, la autonomía puede entrar en tensión "
    "con la cooperación.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que liderar no significa avanzar "
    "por delante de todos, sino crear un impulso donde otras personas también puedan participar. "
    "Cuando integras iniciativa y colaboración, tu presencia dentro de los grupos se convierte "
    "en una fuente de motivación, movimiento y renovación colectiva."
),


"Tauro": (
    "Cuando Tauro ocupa la cúspide de la Casa 11, la relación con las amistades, los grupos y "
    "los proyectos colectivos se construye desde la confianza, la estabilidad y la necesidad de "
    "crear vínculos duraderos. No buscas simplemente pertenecer a muchos espacios, sino formar "
    "parte de comunidades donde exista una sensación real de apoyo, continuidad y valores "
    "compartidos.\n\n"

    "Los vínculos sociales suelen desarrollarse lentamente, pero con una gran capacidad de "
    "permanencia. Prefieres relaciones que puedan cultivarse con el tiempo, basadas en la "
    "lealtad y en experiencias compartidas. La confianza se convierte en el elemento que "
    "permite que una amistad o un proyecto colectivo adquiera verdadera profundidad.\n\n"

    "Esta posición favorece la capacidad para construir proyectos sólidos junto a otras "
    "personas. Aportas constancia, paciencia y una visión práctica que ayuda a transformar "
    "ideas generales en realidades concretas. Dentro de un grupo puedes aportar estabilidad "
    "cuando existen demasiadas propuestas pero falta una base firme sobre la que desarrollarlas.\n\n"

    "Tu visión del futuro suele estar relacionada con aquello que puede crecer de manera "
    "sostenible. No acostumbras a perseguir únicamente novedades o cambios constantes, sino "
    "proyectos que tengan valor real y que puedan mantenerse en el tiempo. La comunidad cobra "
    "sentido cuando ofrece una construcción compartida y no solo una experiencia pasajera.\n\n"

    "El desafío aparece cuando la necesidad de seguridad puede dificultar abrirte a grupos "
    "nuevos, ideas diferentes o formas alternativas de organización. Puede existir resistencia "
    "a modificar estructuras que funcionan, incluso cuando la evolución requiere cierta "
    "flexibilidad. En algunos momentos también puede aparecer apego excesivo a determinadas "
    "personas o comunidades por la historia compartida.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la estabilidad más valiosa "
    "no depende de conservar siempre las mismas formas, sino de reconocer qué valores merecen "
    "seguir creciendo. Cuando integras constancia y apertura, tu presencia dentro de los grupos "
    "se convierte en una fuerza de cohesión, confianza y construcción a largo plazo."
),


"Géminis": (
    "Cuando Géminis ocupa la cúspide de la Casa 11, la relación con las comunidades, amistades "
    "y proyectos colectivos se desarrolla a través del intercambio de ideas y la curiosidad "
    "por conocer personas diferentes. Existe una necesidad natural de conectar con múltiples "
    "entornos, aprender de distintas perspectivas y mantener una red amplia de contactos que "
    "enriquezca tu visión del mundo.\n\n"

    "Las amistades suelen tener un componente mental importante. Te atraen las personas con "
    "quienes puedes conversar, compartir conocimientos y explorar nuevas posibilidades. Más que "
    "la pertenencia basada únicamente en la cercanía emocional, valoras aquellos vínculos que "
    "estimulan tu pensamiento y te permiten descubrir nuevas formas de comprender la realidad.\n\n"

    "Esta posición favorece una gran capacidad para comunicar dentro de grupos, conectar "
    "personas entre sí y actuar como puente entre diferentes ámbitos. Puedes desempeñar un "
    "papel importante difundiendo información, generando conversaciones o facilitando que "
    "distintas ideas encuentren puntos de encuentro.\n\n"

    "Tu visión del futuro suele mantenerse abierta y cambiante. Los proyectos colectivos "
    "adquieren fuerza cuando existe espacio para experimentar, aprender y modificar el rumbo "
    "según aparecen nuevos datos o posibilidades. La comunidad se convierte en una fuente "
    "constante de aprendizaje y renovación intelectual.\n\n"

    "El desafío aparece cuando la diversidad de intereses puede dificultar profundizar en "
    "determinados vínculos o compromisos colectivos. Puede surgir dispersión, tendencia a "
    "participar en demasiados espacios a la vez o dificultad para mantener una dirección "
    "cuando las circunstancias cambian. En algunos momentos, comprender muchas perspectivas "
    "puede hacer más complejo elegir una sola.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que conectar muchas ideas no "
    "significa necesariamente permanecer en la superficie. Cuando integras curiosidad y "
    "profundidad, tu capacidad para comunicar, unir personas y compartir conocimiento se "
    "convierte en una verdadera aportación dentro de cualquier comunidad."
),


"Cáncer": (
    "Cuando Cáncer ocupa la cúspide de la Casa 11, la relación con las amistades, los grupos "
    "y los proyectos colectivos se construye desde el sentimiento de pertenencia y la necesidad "
    "de crear vínculos que tengan una dimensión emocional profunda. No buscas únicamente "
    "compartir intereses, sino formar parte de espacios donde exista una sensación de acogida, "
    "confianza y apoyo mutuo.\n\n"

    "Las amistades suelen ocupar un lugar importante en tu experiencia vital, especialmente "
    "aquellas relaciones que con el tiempo adquieren una cualidad similar a la familia. Existe "
    "una gran capacidad para cuidar a las personas que forman parte de tu círculo y para generar "
    "ambientes donde los demás puedan sentirse escuchados, protegidos y valorados.\n\n"

    "Esta posición favorece la creación de comunidades basadas en la sensibilidad, la cooperación "
    "y el cuidado colectivo. Puedes aportar una comprensión profunda de las necesidades emocionales "
    "de un grupo, percibiendo aquello que necesita ser atendido incluso antes de que sea expresado "
    "claramente.\n\n"

    "Tu visión del futuro suele estar relacionada con la construcción de espacios donde las "
    "personas puedan sentirse conectadas y sostenidas. Los proyectos adquieren mayor significado "
    "cuando contribuyen a generar bienestar compartido, fortalecer vínculos o crear una sensación "
    "de hogar más allá del ámbito estrictamente personal.\n\n"

    "El desafío aparece cuando la necesidad de pertenencia puede llevar a proteger demasiado los "
    "vínculos conocidos o a mantener relaciones simplemente por la historia compartida. Puede "
    "resultar difícil alejarte de grupos que ya no favorecen tu crecimiento, especialmente si "
    "existe un fuerte sentimiento de responsabilidad emocional hacia sus integrantes.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que pertenecer no significa "
    "permanecer siempre en los mismos lugares, sino reconocer dónde existe una verdadera conexión. "
    "Cuando integras cuidado y libertad, tu presencia dentro de las comunidades se convierte en "
    "una fuente de unión, sensibilidad y profunda capacidad para crear redes humanas."
),


"Leo": (
    "Cuando Leo ocupa la cúspide de la Casa 11, la relación con las amistades, los grupos y los "
    "proyectos colectivos se desarrolla a través de la creatividad, la expresión personal y el "
    "deseo de aportar algo único a la comunidad. Existe una necesidad natural de participar en "
    "espacios donde puedas mostrar tus talentos, inspirar a otros y sentir que tu contribución "
    "tiene un valor reconocible.\n\n"

    "Los vínculos sociales suelen enriquecerse cuando existe entusiasmo, generosidad y una "
    "sensación de celebración compartida. Te atraen comunidades donde las personas puedan "
    "expresarse con autenticidad y donde exista espacio para reconocer los talentos individuales "
    "sin perder el sentido de colaboración.\n\n"

    "Esta posición favorece la capacidad para dinamizar grupos, liderar proyectos creativos y "
    "motivar a otras personas desde la confianza y la inspiración. Puedes convertirte en una "
    "figura que impulsa la participación, anima a mostrar capacidades propias y ayuda a que "
    "otros reconozcan también su potencial.\n\n"

    "Tu visión del futuro suele incluir la posibilidad de crear algo que deje una huella personal. "
    "Los proyectos colectivos adquieren mayor sentido cuando permiten expresar una identidad "
    "compartida y desarrollar una visión donde cada persona pueda aportar aquello que la hace "
    "especial.\n\n"

    "El desafío aparece cuando la necesidad de reconocimiento puede interferir con la verdadera "
    "colaboración. Puede surgir cierta sensibilidad ante la falta de valoración o una tendencia "
    "a asumir demasiado protagonismo dentro de un grupo. En algunos momentos puede resultar "
    "difícil aceptar que un proyecto colectivo no pertenece a una sola persona, sino al conjunto "
    "de quienes participan en él.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que el brillo personal alcanza su "
    "máxima expresión cuando también ilumina a los demás. Cuando integras creatividad y humildad, "
    "tu presencia dentro de las comunidades se convierte en una fuerza inspiradora capaz de "
    "generar entusiasmo, confianza y expresión compartida."
),


"Virgo": (
    "Cuando Virgo ocupa la cúspide de la Casa 11, la relación con las amistades, los grupos y "
    "los proyectos colectivos se desarrolla a través de la colaboración práctica, el servicio y "
    "la necesidad de aportar algo útil. Existe una tendencia natural a observar qué necesita un "
    "grupo para funcionar mejor y ofrecer soluciones concretas que ayuden a organizar, mejorar "
    "o perfeccionar los procesos compartidos.\n\n"

    "Los vínculos sociales suelen construirse desde la confianza que nace al compartir objetivos "
    "y responsabilidades. Más que buscar únicamente afinidad emocional, valoras las relaciones "
    "donde existe compromiso, intercambio de conocimientos y una voluntad común de contribuir a "
    "algo significativo.\n\n"

    "Esta posición favorece la capacidad para organizar comunidades, coordinar proyectos y "
    "aportar una mirada analítica dentro de los equipos. Puedes detectar detalles importantes, "
    "mejorar sistemas de trabajo y ayudar a que las ideas colectivas encuentren una estructura "
    "más eficiente.\n\n"

    "Tu visión del futuro suele estar relacionada con la mejora progresiva de la realidad. "
    "Los proyectos adquieren sentido cuando tienen una aplicación concreta y pueden generar un "
    "beneficio real para las personas implicadas. Existe una inclinación hacia comunidades donde "
    "el conocimiento, el aprendizaje o el servicio ocupan un lugar central.\n\n"

    "El desafío aparece cuando la capacidad de análisis puede transformarse en una actitud "
    "demasiado crítica hacia los grupos o hacia las personas que los forman. Puede resultar "
    "difícil aceptar que no todo necesita estar perfectamente organizado para tener valor. En "
    "algunos momentos también puedes asumir más responsabilidades de las que realmente te "
    "corresponden por querer garantizar que todo funcione correctamente.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que contribuir no significa "
    "corregir constantemente, sino aportar desde la aceptación y la cooperación. Cuando integras "
    "discernimiento y confianza, tu presencia dentro de las comunidades se convierte en una "
    "fuerza de mejora, organización y crecimiento compartido."
),


"Libra": (
    "Cuando Libra ocupa la cúspide de la Casa 11, la relación con las amistades, los grupos y "
    "los proyectos colectivos se desarrolla a través de la cooperación, el diálogo y la búsqueda "
    "de equilibrio. Existe una necesidad profunda de formar parte de comunidades donde las "
    "personas puedan relacionarse desde el respeto, la reciprocidad y la valoración mutua.\n\n"

    "Las amistades suelen tener un papel importante en tu evolución personal, ya que a través "
    "del intercambio con otras personas descubres nuevas perspectivas y amplías tu manera de "
    "comprender la realidad. Tiendes a valorar especialmente aquellos vínculos donde existe "
    "escucha, afinidad intelectual y una sensación de construcción conjunta.\n\n"

    "Esta posición favorece la capacidad para unir personas, facilitar acuerdos y crear espacios "
    "donde diferentes intereses puedan convivir. Dentro de un grupo puedes desempeñar un papel "
    "mediador, ayudando a encontrar puntos de encuentro cuando aparecen diferencias o visiones "
    "contrapuestas.\n\n"

    "Tu visión del futuro suele estar relacionada con la creación de sociedades más equilibradas "
    "y relaciones más conscientes. Los proyectos colectivos adquieren mayor sentido cuando "
    "permiten mejorar la convivencia, desarrollar la cooperación o aportar belleza, armonía y "
    "comprensión al entorno.\n\n"

    "El desafío aparece cuando el deseo de mantener la armonía puede llevarte a evitar conflictos "
    "necesarios o a adaptar demasiado tu posición para conservar la aprobación del grupo. Puede "
    "existir dificultad para expresar desacuerdos o para elegir caminos propios cuando estos "
    "pueden generar cierta incomodidad dentro de la comunidad.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera colaboración "
    "necesita personas capaces de aportar su propia voz. Cuando integras diplomacia y "
    "autenticidad, tu presencia en los grupos se convierte en una fuerza de unión, equilibrio y "
    "creación de vínculos donde cada persona puede desarrollarse plenamente."
),


"Escorpio": (
    "Cuando Escorpio ocupa la cúspide de la Casa 11, la relación con las amistades, los grupos "
    "y los proyectos colectivos se desarrolla a través de la profundidad, la transformación y "
    "los vínculos intensos. No buscas simplemente pertenecer a un grupo, sino formar parte de "
    "espacios donde exista autenticidad, compromiso y una conexión que vaya más allá de lo "
    "superficial.\n\n"

    "Las amistades suelen vivir procesos de gran intensidad. Tiendes a seleccionar cuidadosamente "
    "a las personas que forman parte de tu círculo, valorando la lealtad, la confianza y la "
    "capacidad de compartir experiencias significativas. Los vínculos importantes pueden "
    "convertirse en agentes de profunda transformación personal.\n\n"

    "Esta posición favorece la capacidad para participar en proyectos que implican cambio, "
    "investigación o regeneración colectiva. Puedes aportar una mirada penetrante sobre los "
    "problemas de un grupo, detectar aquello que necesita transformarse y acompañar procesos "
    "donde se requiere compromiso y fortaleza emocional.\n\n"

    "Tu visión del futuro suele estar relacionada con una transformación profunda de la realidad. "
    "No acostumbras a conformarte con pequeñas modificaciones superficiales; necesitas sentir "
    "que aquello en lo que participas tiene capacidad para generar una evolución significativa "
    "en las personas o en la sociedad.\n\n"

    "El desafío aparece cuando la intensidad emocional puede convertirse en necesidad de control "
    "dentro de los vínculos colectivos. Puede surgir dificultad para confiar plenamente, miedo "
    "a la traición o tendencia a mantener relaciones que ya han perdido su sentido por la fuerza "
    "de la historia compartida. En algunos momentos también puede aparecer una visión demasiado "
    "crítica hacia los grupos que no cumplen tus expectativas de profundidad.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera transformación "
    "colectiva comienza con la capacidad de abrirse al cambio sin intentar controlarlo todo. "
    "Cuando integras intensidad y confianza, tu presencia dentro de las comunidades se convierte "
    "en una fuerza de regeneración, consciencia y evolución compartida."
),


"Sagitario": (
    "Cuando Sagitario ocupa la cúspide de la Casa 11, la relación con las amistades, los grupos "
    "y los proyectos colectivos se desarrolla a través de la expansión, el aprendizaje y la "
    "búsqueda de nuevos horizontes. Existe una necesidad natural de conectar con personas y "
    "comunidades que amplíen tu visión del mundo y te permitan descubrir nuevas posibilidades.\n\n"

    "Las amistades suelen enriquecerse mediante el intercambio de ideas, experiencias y "
    "perspectivas diferentes. Te atraen personas con inquietudes amplias, procedencias diversas "
    "o formas de pensar que cuestionan lo conocido. La comunidad se convierte en un espacio de "
    "crecimiento y descubrimiento constante.\n\n"

    "Esta posición favorece la capacidad para inspirar grupos, transmitir conocimientos y "
    "participar en proyectos con una dimensión educativa, cultural o social. Puedes aportar "
    "entusiasmo, visión de futuro y una capacidad natural para recordar que siempre existen "
    "nuevos caminos por explorar.\n\n"

    "Tu visión del futuro suele estar orientada hacia la expansión y la posibilidad de crear "
    "algo que trascienda los límites habituales. Los proyectos colectivos adquieren sentido "
    "cuando abren puertas, conectan realidades diferentes o contribuyen a ampliar la consciencia "
    "de quienes participan en ellos.\n\n"

    "El desafío aparece cuando el deseo de expansión puede dificultar el compromiso con una "
    "dirección concreta. Puede surgir tendencia a participar en demasiados proyectos, buscar "
    "constantemente nuevas experiencias o perder interés cuando una comunidad requiere "
    "continuidad y esfuerzo sostenido. En algunos momentos también puede existir cierta "
    "convicción excesiva sobre la propia visión del futuro.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que expandirse también significa "
    "profundizar en aquello que eliges construir junto a otros. Cuando integras entusiasmo y "
    "compromiso, tu presencia en las comunidades se convierte en una fuente de inspiración, "
    "aprendizaje y apertura hacia nuevas posibilidades."
),


"Capricornio": (
    "Cuando Capricornio ocupa la cúspide de la Casa 11, la relación con las amistades, los "
    "grupos y los proyectos colectivos se desarrolla a través del compromiso, la responsabilidad "
    "y la construcción a largo plazo. No buscas simplemente formar parte de una comunidad, sino "
    "participar en espacios donde exista una dirección clara, objetivos concretos y la posibilidad "
    "de crear algo que permanezca en el tiempo.\n\n"

    "Las amistades suelen construirse de manera gradual y selectiva. Valoras especialmente los "
    "vínculos basados en la confianza, la coherencia y la capacidad de compartir responsabilidades. "
    "Aunque tu círculo puede no ser excesivamente amplio, las relaciones que consideras importantes "
    "tienden a adquirir profundidad y estabilidad con los años.\n\n"

    "Esta posición favorece la capacidad para organizar proyectos colectivos, asumir funciones de "
    "responsabilidad dentro de grupos y aportar una visión estratégica al trabajo compartido. "
    "Puedes convertirte en una figura de referencia cuando una comunidad necesita estructura, "
    "planificación y capacidad para transformar una idea en un objetivo alcanzable.\n\n"

    "Tu visión del futuro suele construirse desde la prudencia y la previsión. Antes de comprometer "
    "energía con un proyecto colectivo necesitas valorar si tiene una base sólida y posibilidades "
    "reales de desarrollo. Te interesa participar en iniciativas que puedan generar resultados "
    "duraderos y aportar algo significativo a largo plazo.\n\n"

    "El desafío aparece cuando la necesidad de estructura puede hacer que te resulte difícil "
    "participar en grupos más espontáneos o aceptar procesos que todavía no tienen una forma "
    "definida. Puede surgir cierta distancia emocional o tendencia a valorar demasiado la "
    "utilidad de las relaciones, olvidando que la conexión humana también necesita espacio para "
    "la sencillez y el disfrute.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que una comunidad sólida no solo "
    "se construye con objetivos y responsabilidades, sino también con confianza y apertura. "
    "Cuando integras compromiso y cercanía, tu presencia dentro de los grupos se convierte en "
    "una fuerza de estabilidad, madurez y capacidad para construir futuro junto a otros."
),


"Acuario": (
    "Cuando Acuario ocupa la cúspide de la Casa 11, la relación con las amistades, los grupos "
    "y los proyectos colectivos se desarrolla desde la necesidad de libertad, innovación y "
    "participación en comunidades que miran hacia el futuro. Esta posición encuentra su espacio "
    "natural en redes donde las personas puedan aportar ideas diferentes, cuestionar lo establecido "
    "y colaborar desde la individualidad.\n\n"

    "Las amistades suelen estar formadas por personas diversas, poco convencionales o con "
    "intereses que amplían tu manera de comprender el mundo. Existe una facilidad especial para "
    "conectar con quienes aportan perspectivas nuevas, ya que valoras más la autenticidad y la "
    "riqueza del intercambio que la necesidad de pertenecer a un único círculo definido.\n\n"

    "Esta posición favorece la participación en proyectos innovadores, sociales, tecnológicos o "
    "colectivos donde sea necesario imaginar nuevas formas de organización. Puedes aportar una "
    "visión amplia, capacidad para detectar tendencias y facilidad para comprender cómo diferentes "
    "elementos pueden conectarse para crear algo nuevo.\n\n"

    "Tu visión del futuro suele estar orientada hacia el cambio y la evolución colectiva. Los "
    "proyectos adquieren sentido cuando permiten mejorar la sociedad, ampliar posibilidades o "
    "generar una forma más libre y consciente de relacionarse. Existe una inclinación natural a "
    "pensar más allá de las necesidades inmediatas y contemplar procesos a largo plazo.\n\n"

    "El desafío aparece cuando la necesidad de independencia puede dificultar la implicación "
    "emocional profunda en determinados grupos. Puede surgir cierta sensación de distancia, "
    "preferencia por observar desde fuera o resistencia ante comunidades que establecen demasiadas "
    "normas. En algunos momentos, la búsqueda de originalidad puede convertirse en una necesidad "
    "de diferenciarte constantemente.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera libertad no "
    "consiste en mantenerse separado, sino en participar desde una identidad propia. Cuando "
    "integras independencia y conexión, tu presencia dentro de las comunidades se convierte en "
    "una fuerza de innovación, apertura y transformación colectiva."
),


"Piscis": (
    "Cuando Piscis ocupa la cúspide de la Casa 11, la relación con las amistades, los grupos y "
    "los proyectos colectivos se desarrolla a través de la sensibilidad, la empatía y la "
    "percepción de una conexión profunda entre las personas. Existe una necesidad natural de "
    "formar parte de comunidades donde puedas sentir que compartes valores, ideales o una visión "
    "más amplia de la vida.\n\n"

    "Las amistades suelen estar marcadas por una gran apertura emocional. Puedes conectar con "
    "personas muy diferentes y percibir con facilidad aquello que une más allá de las "
    "diferencias externas. Los vínculos adquieren significado cuando existe comprensión, apoyo "
    "mutuo y una sensación de compartir algo que trasciende lo individual.\n\n"

    "Esta posición favorece la participación en proyectos relacionados con la ayuda, la "
    "creatividad, la sensibilidad colectiva o cualquier iniciativa donde sea importante comprender "
    "las necesidades humanas desde una perspectiva amplia. Aportas intuición, imaginación y una "
    "capacidad especial para captar el espíritu de un grupo.\n\n"

    "Tu visión del futuro suele estar vinculada a ideales de unidad, cooperación y evolución "
    "humana. Los proyectos colectivos adquieren fuerza cuando responden a una inspiración profunda "
    "y cuando permiten crear espacios donde las personas puedan sentirse conectadas con algo más "
    "grande que ellas mismas.\n\n"

    "El desafío aparece cuando la sensibilidad puede dificultar establecer límites claros dentro "
    "de las comunidades. Puede surgir tendencia a absorber demasiado las emociones del grupo, "
    "idealizar personas o proyectos, o mantener vínculos que ya no favorecen tu crecimiento por "
    "un fuerte sentimiento de compasión o responsabilidad.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la conexión auténtica también "
    "necesita claridad y presencia consciente. Cuando integras empatía y límites saludables, tu "
    "participación en las comunidades se convierte en una fuente de inspiración, comprensión y "
    "profunda capacidad para unir a las personas desde valores compartidos."
),

}



CASA_12 = {

"Aries": (
    "Cuando Aries ocupa la cúspide de la Casa 12, la relación con el mundo interior se "
    "desarrolla a través de un proceso de descubrimiento de la propia fuerza interna. Existe "
    "una energía profunda que necesita encontrar una vía de expresión consciente, aunque no "
    "siempre resulte evidente desde el exterior. Parte importante de tu crecimiento consiste "
    "en reconocer impulsos, deseos y necesidades que actúan desde niveles más internos de la "
    "experiencia.\n\n"

    "La vida interior puede estar marcada por una gran actividad inconsciente. Incluso en "
    "momentos de aparente quietud, existe un movimiento interno intenso que busca comprender "
    "qué deseas realmente y hacia dónde dirigir tu energía. El descanso, la introspección y "
    "los espacios de silencio pueden convertirse en momentos donde recuperas una conexión "
    "profunda contigo.\n\n"

    "Esta posición favorece la capacidad para atravesar procesos internos de renovación. "
    "Existe una fuerza de regeneración que aparece especialmente cuando necesitas enfrentarte "
    "a miedos, bloqueos o etapas donde la acción externa ya no ofrece todas las respuestas. "
    "Aprendes que también existe poder en esperar, observar y permitir que determinados "
    "procesos maduren antes de actuar.\n\n"

    "Tu mundo interior puede convertirse en una fuente de gran valentía cuando aprendes a "
    "escuchar aquello que surge desde dentro. La intuición de tus propios impulsos puede "
    "orientarte hacia cambios importantes, aunque a veces necesites tiempo para comprender "
    "qué dirección quieren mostrarte.\n\n"

    "El desafío aparece cuando la energía de Aries permanece demasiado contenida o no encuentra "
    "una expresión consciente. Puede surgir impaciencia interna, dificultad para aceptar los "
    "ritmos naturales de ciertos procesos o tendencia a luchar contra aquello que requiere "
    "aceptación y entrega. En algunos momentos puede existir una sensación de estar actuando "
    "contra obstáculos invisibles que en realidad invitan a una transformación interior.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera fuerza no nace "
    "únicamente de conquistar el exterior, sino de aprender a dirigir conscientemente la energía "
    "interna. Cuando integras acción e introspección, desarrollas una presencia capaz de actuar "
    "desde una conexión profunda con tu propia esencia."
),


"Tauro": (
    "Cuando Tauro ocupa la cúspide de la Casa 12, la relación con el mundo interior se desarrolla "
    "a través de la búsqueda de calma, estabilidad y conexión con aquello que aporta una sensación "
    "profunda de paz. Existe una necesidad de encontrar espacios internos donde puedas descansar "
    "del ritmo externo y recuperar una sensación de arraigo contigo.\n\n"

    "La vida interior suele estar relacionada con los sentidos, la naturaleza y la capacidad "
    "para encontrar valor en experiencias sencillas y silenciosas. Los momentos de pausa, el "
    "contacto con el cuerpo y la conexión con ritmos más lentos pueden convertirse en fuentes "
    "importantes de equilibrio y regeneración.\n\n"

    "Esta posición favorece una gran capacidad para sostener procesos internos con paciencia. "
    "No siempre necesitas respuestas inmediatas; muchas comprensiones llegan a través del "
    "tiempo, la observación y la experiencia acumulada. Existe una sabiduría interna que se "
    "desarrolla de forma gradual y profunda.\n\n"

    "El mundo interior puede convertirse en un refugio desde el que recuperar confianza y "
    "fortaleza. Aprendes que la seguridad más profunda no depende únicamente de conservar lo "
    "externo, sino de desarrollar una sensación interna de estabilidad que permanece incluso "
    "cuando las circunstancias cambian.\n\n"

    "El desafío aparece cuando la necesidad de tranquilidad puede convertirse en resistencia "
    "frente a procesos internos de transformación. Puede existir dificultad para soltar viejas "
    "seguridades, emociones acumuladas o formas conocidas de protegerte. En algunos momentos, "
    "la búsqueda de paz puede confundirse con evitar aquello que necesita ser revisado.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera estabilidad "
    "nace de aceptar también los movimientos internos de la vida. Cuando integras calma y "
    "capacidad de transformación, tu mundo interior se convierte en una fuente de serenidad, "
    "presencia y profunda conexión contigo."
),


"Géminis": (
    "Cuando Géminis ocupa la cúspide de la Casa 12, la relación con el mundo interior se "
    "desarrolla a través de la observación, la reflexión y la necesidad de comprender los "
    "procesos invisibles de la mente. Existe una gran actividad interna relacionada con ideas, "
    "recuerdos, asociaciones y pensamientos que se mueven incluso cuando aparentemente estás "
    "en calma.\n\n"

    "La vida interior puede convertirse en un espacio de constante exploración. Existe una "
    "facilidad natural para conectar experiencias pasadas, descubrir nuevos significados y "
    "observar cómo funcionan tus propios patrones mentales. El silencio no siempre significa "
    "ausencia de movimiento; en tu caso puede ser un territorio lleno de preguntas y "
    "descubrimientos.\n\n"

    "Esta posición favorece la capacidad para comprender aspectos psicológicos, simbólicos o "
    "sutiles de la experiencia humana. Puedes desarrollar una mirada muy rica hacia aquello "
    "que ocurre detrás de las palabras, percibiendo matices que ayudan a comprender mejor tus "
    "propios procesos y los de otras personas.\n\n"

    "El mundo interior se fortalece cuando encuentras vías para expresar y ordenar todo aquello "
    "que percibes. Escribir, estudiar, reflexionar o compartir conocimientos pueden convertirse "
    "en formas de integrar experiencias que inicialmente parecen difíciles de organizar.\n\n"

    "El desafío aparece cuando la actividad mental puede dificultar el descanso interno. Puede "
    "existir tendencia a analizar demasiado las emociones, buscar explicaciones constantes o "
    "permanecer en el pensamiento cuando la experiencia requiere simplemente ser sentida. En "
    "algunos momentos también puede aparecer dispersión entre muchas ideas internas sin llegar "
    "a integrarlas completamente.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que comprender no significa "
    "controlarlo todo mentalmente. Cuando integras curiosidad y silencio, desarrollas una "
    "capacidad profunda para observar la vida interior con claridad, transformando el "
    "conocimiento en consciencia."
),


"Cáncer": (
    "Cuando Cáncer ocupa la cúspide de la Casa 12, la relación con el mundo interior se "
    "desarrolla a través de una profunda conexión con las emociones, la memoria y las "
    "experiencias que han dejado huella a lo largo del camino. Existe una sensibilidad "
    "especial hacia todo aquello que permanece en niveles profundos de la consciencia, "
    "incluyendo recuerdos, necesidades emocionales y vínculos que siguen formando parte "
    "de tu historia personal.\n\n"

    "La vida interior suele tener una gran riqueza emocional. Necesitas momentos de recogimiento "
    "donde puedas escuchar lo que sientes y recuperar una sensación de protección interna. "
    "El silencio, la intimidad y los espacios donde puedes ser quien eres sin exigencias externas "
    "se convierten en fuentes importantes de regeneración y equilibrio.\n\n"

    "Esta posición favorece una gran capacidad para conectar con dimensiones profundas de la "
    "experiencia humana. Existe una intuición natural para percibir estados emocionales, "
    "necesidades no expresadas y aquello que otras personas pueden estar atravesando incluso "
    "sin decirlo directamente. Esa sensibilidad puede convertirse en una forma de comprensión "
    "y acompañamiento muy valiosa.\n\n"

    "El mundo interior actúa aquí como un espacio donde integrar la propia historia. Las "
    "experiencias familiares, las raíces emocionales y los recuerdos importantes pueden "
    "convertirse en claves fundamentales para comprender quién eres y qué necesitas para "
    "experimentar una verdadera sensación de sostén.\n\n"

    "El desafío aparece cuando la sensibilidad hacia el pasado dificulta permanecer plenamente "
    "en el presente. Puede existir tendencia a guardar emociones durante mucho tiempo, cargar "
    "con recuerdos que ya han cumplido su función o absorber estados emocionales ajenos sin "
    "diferenciarlos claramente de los propios. En algunos momentos, protegerte puede convertirse "
    "en una forma de aislarte demasiado.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que el verdadero refugio no está "
    "únicamente en lo conocido, sino en la capacidad de sostener tus propias emociones con "
    "madurez. Cuando integras sensibilidad y fortaleza interior, desarrollas una presencia "
    "profundamente compasiva, capaz de cuidar sin perderte en aquello que cuidas."
),


"Leo": (
    "Cuando Leo ocupa la cúspide de la Casa 12, la relación con el mundo interior se desarrolla "
    "a través del descubrimiento de una identidad más profunda que no depende únicamente de la "
    "expresión externa o del reconocimiento recibido. Existe una necesidad de conectar con una "
    "fuente interna de creatividad, confianza y autenticidad que permanece incluso cuando no "
    "está siendo visible para los demás.\n\n"

    "La vida interior puede albergar un gran potencial creativo. Muchas veces aquello que nace "
    "en los espacios de silencio, imaginación o introspección contiene una fuerza expresiva "
    "importante que necesita tiempo para desarrollarse antes de mostrarse al mundo. La "
    "inspiración puede surgir precisamente cuando no existe una necesidad inmediata de demostrar "
    "nada.\n\n"

    "Esta posición favorece una profunda conexión con el propio valor interno. El aprendizaje "
    "consiste en descubrir que tu esencia no pierde fuerza cuando no recibe atención externa, "
    "sino que puede fortalecerse en contacto contigo. La confianza más auténtica nace "
    "cuando reconoces tu propia luz sin necesitar constantemente que alguien más la confirme.\n\n"

    "El mundo interior puede convertirse en un espacio de gran riqueza simbólica e imaginativa. "
    "Existe facilidad para conectar con la creatividad, la expresión artística o formas de "
    "comprensión que permiten transformar experiencias internas en algo que puede inspirar a "
    "otros.\n\n"

    "El desafío aparece cuando una parte de ti puede sentir que permanece oculta o no reconocida. "
    "Puede surgir frustración por no recibir la valoración esperada o dificultad para mostrar "
    "determinados talentos por miedo a no ser suficientemente apreciado. En algunos momentos, "
    "la necesidad de proteger la propia identidad puede llevar a esconder precisamente aquello "
    "que deseas compartir.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera expresión nace "
    "cuando ya no depende de ser vista. Cuando integras creatividad e interioridad, tu luz deja "
    "de buscar reconocimiento y se convierte en una fuente natural de inspiración, generosidad "
    "y autenticidad."
),


"Virgo": (
    "Cuando Virgo ocupa la cúspide de la Casa 12, la relación con el mundo interior se "
    "desarrolla a través de la observación, la comprensión de los procesos internos y la "
    "necesidad de encontrar orden incluso en aquello que no resulta visible. Existe una "
    "tendencia natural a analizar las experiencias profundas, buscando comprender cómo funcionan "
    "tus emociones, pensamientos y patrones inconscientes.\n\n"

    "La vida interior puede convertirse en un espacio de constante revisión y aprendizaje. "
    "Necesitas momentos de silencio donde puedas organizar lo vivido, extraer conclusiones y "
    "encontrar maneras de mejorar tu relación contigo. La introspección adquiere un "
    "carácter práctico: no se trata únicamente de comprender, sino de integrar aquello que "
    "descubres para vivir de una forma más coherente.\n\n"

    "Esta posición favorece una gran capacidad para percibir detalles sutiles del mundo interno. "
    "Puedes identificar pequeños movimientos emocionales, pensamientos repetitivos o hábitos "
    "inconscientes que necesitan ser observados. Esa atención puede convertirse en una poderosa "
    "herramienta de crecimiento personal cuando se acompaña de aceptación.\n\n"

    "Existe una disposición natural hacia el servicio silencioso y hacia la ayuda que no siempre "
    "busca reconocimiento. Muchas veces encuentras sentido al poner tus capacidades al servicio "
    "de procesos de mejora, acompañamiento o cuidado, incluso desde lugares discretos o poco "
    "visibles.\n\n"

    "El desafío aparece cuando la observación interior se transforma en autocrítica constante. "
    "Puede existir tendencia a buscar aquello que necesita corregirse antes que reconocer lo "
    "que ya está integrado. En algunos momentos también puede aparecer dificultad para aceptar "
    "la incertidumbre propia de los procesos internos, intentando encontrar una explicación "
    "perfecta para todo lo que sucede.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la integración no nace de "
    "arreglar cada aspecto de quién eres, sino de aprender a acompañarte con comprensión. Cuando "
    "equilibras discernimiento y aceptación, desarrollas una profunda capacidad para sanar, "
    "ordenar y transformar la experiencia de la vida desde dentro."
),


"Libra": (
    "Cuando Libra ocupa la cúspide de la Casa 12, la relación con el mundo interior se "
    "desarrolla a través de la búsqueda de equilibrio, armonía y comprensión profunda de los "
    "vínculos que forman parte de tu historia. Existe una sensibilidad especial hacia las "
    "dinámicas relacionales invisibles, hacia aquello que ocurre entre las personas incluso "
    "cuando no se expresa directamente.\n\n"

    "La vida interior necesita espacios de calma donde puedas recuperar tu propio centro. "
    "Existe una tendencia natural a percibir las necesidades, emociones y estados de quienes "
    "te rodean, por lo que los momentos de silencio pueden ser fundamentales para distinguir "
    "qué pertenece realmente a tu experiencia y qué has incorporado del entorno.\n\n"

    "Esta posición favorece una profunda capacidad para comprender diferentes perspectivas. "
    "En el mundo interno puedes desarrollar una mirada muy amplia hacia las relaciones, "
    "observando patrones, encuentros y aprendizajes que han marcado tu recorrido. Existe una "
    "necesidad de encontrar un sentido más elevado a los vínculos vividos, incluso a aquellos "
    "que fueron difíciles o dejaron preguntas abiertas.\n\n"

    "El mundo interior puede convertirse en un espacio donde integrar experiencias de relación "
    "y reconciliar aspectos de ti que parecen opuestos. La creatividad, la belleza, el "
    "arte o cualquier forma de expresión simbólica pueden actuar como caminos para recuperar "
    "armonía y conectar con una sensación más profunda de unidad.\n\n"

    "El desafío aparece cuando el deseo de mantener la paz interna lleva a evitar conflictos "
    "necesarios o a guardar emociones para no alterar el equilibrio externo. Puede existir "
    "tendencia a adaptarte demasiado a las necesidades ajenas o dificultad para reconocer "
    "aquello que deseas cuando no coincide con las expectativas de otras personas.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera armonía no "
    "consiste en eliminar toda tensión, sino en aprender a integrar las diferencias. Cuando "
    "desarrollas un equilibrio interno más sólido, tus relaciones dejan de ser un lugar donde "
    "buscar completarte y se convierten en espacios donde compartir una identidad ya consciente."
),


"Escorpio": (
    "Cuando Escorpio ocupa la cúspide de la Casa 12, la relación con el mundo interior se "
    "desarrolla a través de procesos profundos de transformación, regeneración y encuentro "
    "con aquello que permanece oculto bajo la superficie. Existe una intensidad emocional e "
    "inconsciente que puede llevarte a explorar aspectos de la experiencia humana que otras "
    "personas prefieren evitar.\n\n"

    "La vida interior posee una gran fuerza transformadora. Los periodos de silencio, "
    "introspección o retiro pueden convertirse en momentos de profunda renovación, donde "
    "emergen comprensiones importantes sobre tus propios patrones, miedos y capacidades. "
    "Existe una tendencia natural a buscar la raíz de las cosas, no conformándote con "
    "explicaciones superficiales.\n\n"

    "Esta posición favorece una gran capacidad para atravesar procesos internos complejos. "
    "Aunque determinadas etapas puedan sentirse intensas, suelen convertirse en oportunidades "
    "para desprenderte de antiguas formas de ser y descubrir recursos internos que permanecían "
    "desconocidos. La transformación forma parte esencial de tu camino de integración.\n\n"

    "El mundo interior puede convertirse en una fuente de enorme fortaleza. Existe una "
    "capacidad intuitiva para percibir aquello que no se dice, comprender motivaciones "
    "profundas y acompañar procesos de cambio tanto propios como ajenos. La experiencia "
    "personal puede otorgarte una sabiduría nacida de haber atravesado tus propias "
    "profundidades.\n\n"

    "El desafío aparece cuando el contacto con las emociones más intensas genera miedo a "
    "perder el control o tendencia a protegerte mediante la reserva, la desconfianza o la "
    "necesidad de mantener todo bajo vigilancia. En algunos momentos puede resultar difícil "
    "aceptar que ciertas transformaciones requieren soltar antiguas estructuras antes de "
    "poder crear algo nuevo.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera profundidad "
    "no nace de luchar contra la oscuridad interna, sino de integrarla con consciencia. Cuando "
    "transformas la intensidad en comprensión, desarrollas una gran capacidad de regeneración "
    "y una presencia que transmite fortaleza, autenticidad y poder interior."
),


"Sagitario": (
    "Cuando Sagitario ocupa la cúspide de la Casa 12, la relación con el mundo interior se "
    "desarrolla a través de la búsqueda de significado, comprensión y conexión con una visión "
    "más amplia de la existencia. Existe una necesidad profunda de encontrar un sentido que "
    "integre las experiencias vividas y permita comprender el recorrido personal desde una "
    "perspectiva más elevada.\n\n"

    "La vida interior se nutre del aprendizaje, la reflexión y la exploración de ideas que "
    "amplían la consciencia. Aunque pueda existir una inclinación hacia la búsqueda externa de "
    "conocimiento, muchas de las respuestas más importantes llegan a través de la observación "
    "interna y de la capacidad para escuchar la propia sabiduría acumulada.\n\n"

    "Esta posición favorece una conexión natural con la filosofía, la espiritualidad o los "
    "sistemas de comprensión que permiten encontrar un significado profundo a la experiencia "
    "humana. Existe una tendencia a percibir la vida como un proceso de crecimiento continuo "
    "donde incluso las dificultades pueden convertirse en aprendizajes importantes.\n\n"

    "El mundo interior puede convertirse en un espacio de expansión ilimitada. La imaginación, "
    "la intuición y la capacidad para contemplar diferentes perspectivas permiten desarrollar "
    "una comprensión amplia de los propios procesos internos. Muchas veces descubres nuevas "
    "verdades cuando permites que tu proceso madure sin intentar forzar respuestas "
    "inmediatas.\n\n"

    "El desafío aparece cuando la búsqueda constante de significado puede llevar a escapar de "
    "la realidad concreta o a buscar respuestas demasiado lejos de aquello que ocurre en el "
    "presente. También puede existir dificultad para aceptar los momentos de incertidumbre "
    "donde todavía no aparece una explicación clara.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera expansión no "
    "consiste únicamente en alcanzar nuevas comprensiones, sino en integrar la sabiduría "
    "adquirida en la vida cotidiana. Cuando unes visión amplia y presencia consciente, tu "
    "mundo interior se convierte en una fuente de confianza, inspiración y sentido profundo."
),


"Capricornio": (
    "Cuando Capricornio ocupa la cúspide de la Casa 12, la relación con el mundo interior se "
    "desarrolla a través de la responsabilidad, la maduración y la construcción paciente de "
    "una estructura interna sólida. Existe una tendencia natural a tomarte en serio tus propios "
    "procesos, buscando comprender qué aprendizajes surgen de las experiencias que atraviesas "
    "y cómo pueden ayudarte a desarrollar una mayor fortaleza interior.\n\n"

    "La vida interior puede estar marcada por una sensación de exigencia o por la necesidad "
    "de encontrar un sentido práctico incluso en aquello que pertenece al ámbito emocional o "
    "espiritual. Necesitas sentir que tus procesos internos tienen una dirección y que el "
    "tiempo dedicado a la introspección puede traducirse en crecimiento real y transformación "
    "personal.\n\n"

    "Esta posición favorece una gran capacidad para sostener etapas de recogimiento, silencio "
    "o retiro cuando son necesarios. Aunque puedas no buscar siempre mostrar tus procesos "
    "internos, existe una profunda actividad de construcción personal que ocurre en espacios "
    "privados. Muchas de tus mayores comprensiones pueden surgir precisamente cuando asumes "
    "la responsabilidad de mirar hacia dentro.\n\n"

    "El mundo interior puede convertirse en una fuente de madurez y sabiduría. Las dificultades "
    "vividas, los periodos de soledad o los momentos donde has tenido que recurrir a tus propios recursos "
    "pueden desarrollar una gran capacidad de sostén interno y una comprensión profunda de "
    "los ciclos de la vida.\n\n"

    "El desafío aparece cuando la responsabilidad interna se transforma en peso o cuando "
    "sientes que incluso tus emociones deben estar bajo control. Puede existir tendencia a "
    "juzgarte con dureza, ocultar necesidades emocionales o sentir que descansar y dejarte "
    "acompañar son signos de debilidad. En algunos momentos puedes asumir cargas que no "
    "corresponden únicamente a ti.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera fortaleza no "
    "consiste en sostenerlo todo en soledad, sino en desarrollar una relación madura con la "
    "propia vulnerabilidad. Cuando integras disciplina y apertura emocional, tu mundo interior "
    "se convierte en una fuente de estabilidad, profundidad y autoridad serena."
),


"Acuario": (
    "Cuando Acuario ocupa la cúspide de la Casa 12, la relación con el mundo interior se "
    "desarrolla a través de una forma de consciencia amplia, original y poco convencional. "
    "Existe una tendencia natural a observar la vida desde una perspectiva diferente, "
    "buscando comprender patrones colectivos, ideas universales y conexiones que van más allá "
    "de la experiencia individual.\n\n"

    "La vida interior puede estar llena de imágenes, ideas e intuiciones que aparecen de forma "
    "inesperada. Existe una gran actividad mental y simbólica que puede llevarte a percibir "
    "posibilidades nuevas o comprender aspectos de la realidad que no siempre resultan "
    "evidentes para otras personas. La inspiración suele llegar cuando permites espacio a "
    "la libertad interna.\n\n"

    "Esta posición favorece una relación profunda con la dimensión colectiva de la experiencia humana. "
    "Puedes sentir una conexión especial con grupos, movimientos, causas o ideas que buscan "
    "generar evolución y cambio. Parte de tu proceso interior consiste en comprender cómo tu "
    "individualidad forma parte de algo más amplio.\n\n"

    "El mundo interior puede convertirse en un laboratorio de nuevas formas de comprender la "
    "vida. La imaginación, la observación desapegada y la capacidad para cuestionar creencias "
    "heredadas permiten desarrollar una visión muy personal sobre la existencia. Muchas "
    "comprensiones importantes pueden surgir cuando te permites pensar de manera diferente.\n\n"

    "El desafío aparece cuando la necesidad de independencia interna genera distancia respecto "
    "a las propias emociones o a las necesidades más humanas y cercanas. Puede existir una "
    "tendencia a comprender intelectualmente aquello que primero necesita ser sentido. En "
    "algunos momentos, proteger tu libertad puede llevarte a desconectar de la intimidad "
    "emocional.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la verdadera libertad no "
    "consiste en mantenerte al margen, sino en encontrar una forma auténtica de pertenecer sin "
    "perder la individualidad. Cuando integras visión y sensibilidad, tu mundo interior se "
    "convierte en una fuente de innovación, consciencia y conexión con algo mayor."
),


"Piscis": (
    "Cuando Piscis ocupa la cúspide de la Casa 12, la relación con el mundo interior se "
    "desarrolla a través de una profunda sensibilidad, intuición y conexión con dimensiones "
    "sutiles de la vida. Existe una percepción natural de aquello que ocurre más allá "
    "de lo evidente, como si una parte de ti estuviera constantemente escuchando los matices "
    "emocionales, simbólicos y energéticos de la vida.\n\n"

    "La vida interior posee una enorme riqueza imaginativa y espiritual. Necesitas espacios "
    "de silencio, contemplación y conexión contigo para recuperar equilibrio y sentirte "
    "en armonía con tu propia naturaleza. La creatividad, la música, el arte, la meditación o "
    "cualquier vía de expresión simbólica pueden convertirse en caminos importantes de "
    "integración.\n\n"

    "Esta posición favorece una gran capacidad para comprender la experiencia humana desde la "
    "empatía y la compasión. Existe una sensibilidad especial hacia el sufrimiento, los "
    "procesos invisibles y aquello que muchas veces permanece sin palabras. Tu mundo interior "
    "puede convertirse en un espacio donde integrar múltiples perspectivas y encontrar una "
    "comprensión más amplia de la existencia.\n\n"

    "El contacto con tu interioridad puede revelar una profunda sabiduría intuitiva. Muchas "
    "veces las respuestas más importantes no llegan mediante el análisis racional, sino a "
    "través de una percepción interna que necesita tiempo, silencio y confianza para hacerse "
    "consciente. La conexión con esa sensibilidad constituye uno de tus mayores recursos.\n\n"

    "El desafío aparece cuando la apertura emocional dificulta establecer límites claros o "
    "cuando puedes absorber demasiado aquello que pertenece al entorno. Puede existir tendencia "
    "a escapar de situaciones dolorosas, idealizar determinadas experiencias o confiar más en "
    "la intuición que en la necesidad de mantener una base práctica y concreta.\n\n"

    "Con el paso de los años, esta posición invita a descubrir que la sensibilidad alcanza su "
    "mayor fuerza cuando está acompañada de presencia y claridad. Cuando integras apertura y "
    "arraigo, tu mundo interior se convierte en una fuente de inspiración, comprensión profunda "
    "y capacidad para acompañar la vida desde una conexión auténtica."
),

}


TEXTOS_CASAS = {
    1: CASA_1,
    2: CASA_2,
    3: CASA_3,
    4: CASA_4,
    5: CASA_5,
    6: CASA_6,
    7: CASA_7,
    8: CASA_8,
    9: CASA_9,
    10: CASA_10,
    11: CASA_11,
    12: CASA_12,
}


TEXTO_INTRO_ANGULOS = (
    "Los cuatro ángulos forman la estructura principal de orientación de la carta. "
    "Señalan cuatro puntos fundamentales desde los que organizas tu vida: "
    "la manera en que apareces ante el mundo, la forma en que te relacionas, las "
    "raíces que te sostienen y la dirección hacia la que orientas tu desarrollo.\n\n"

    "El Ascendente y el Descendente forman un eje relacionado con la identidad y "
    "el encuentro. El Fondo del Cielo y el Medio Cielo forman otro eje vinculado "
    "con la intimidad, las raíces, la vocación y la proyección exterior.\n\n"

    "No se interpretan aquí como aspectos astrológicos, sino como relaciones "
    "estructurales. Cada ángulo necesita al opuesto para expresarse de forma "
    "equilibrada, y los cuatro participan en una misma arquitectura."
)


EJE_ASC_DSC = {
    ("Aries", "Libra"): (
        "Tu eje de identidad y vínculo se organiza entre Aries y Libra. "
        "El Ascendente en Aries necesita construir una forma de estar en el mundo "
        "basada en la iniciativa, la autonomía y la capacidad para actuar desde el "
        "propio deseo. Existe una tendencia natural a responder con rapidez, abrir "
        "caminos y confiar en la experiencia directa como una forma de descubrir "
        "quién eres.\n\n"

        "El Descendente en Libra muestra que los vínculos importantes introducen "
        "otra necesidad: aprender a considerar al otro, negociar diferencias y "
        "construir espacios donde exista reciprocidad. Las relaciones te invitan a "
        "descubrir que no toda decisión necesita tomarse de manera individual y que "
        "la cooperación puede ampliar tus posibilidades sin disminuir tu autonomía.\n\n"

        "La tensión de este eje puede aparecer cuando la necesidad de actuar con "
        "libertad entra en conflicto con el deseo de mantener el equilibrio dentro "
        "del vínculo. En algunos momentos puedes avanzar sin tener suficientemente "
        "en cuenta a la otra persona; en otros, intentar preservar la armonía puede "
        "llevarte a posponer una decisión o alejarte de aquello que realmente deseas.\n\n"

        "El equilibrio aparece cuando comprendes que afirmarte no implica excluir "
        "al otro y que cooperar no exige renunciar a tu propia dirección. Aries "
        "aporta iniciativa, claridad y capacidad para comenzar; Libra aporta escucha, "
        "perspectiva y capacidad para construir acuerdos. Cuando ambos polos "
        "colaboran, puedes relacionarte desde una identidad firme sin perder la "
        "apertura necesaria para crear vínculos verdaderamente recíprocos."
    ),


    ("Tauro", "Escorpio"): (
        "Tu eje de identidad y vínculo se organiza entre Tauro y Escorpio. "
        "El Ascendente en Tauro necesita construir una forma de estar en el mundo "
        "basada en la estabilidad, la continuidad y la confianza en aquello que puede "
        "sostenerse con el tiempo. Existe una tendencia natural a avanzar de manera "
        "gradual, consolidar cada paso y buscar una base segura desde la que relacionarte "
        "con la vida.\n\n"

        "El Descendente en Escorpio muestra que los vínculos importantes introducen "
        "una dimensión más intensa y transformadora. Las relaciones pueden llevarte "
        "hacia territorios donde no basta con conservar lo conocido: aparecen procesos "
        "de cambio, intimidad y confianza que te invitan a profundizar y a permitir "
        "que algunas formas de seguridad se transformen.\n\n"

        "La tensión de este eje puede aparecer cuando la necesidad de preservar la "
        "estabilidad entra en conflicto con experiencias relacionales que exigen cambio "
        "o una mayor implicación emocional. Puedes aferrarte a situaciones conocidas "
        "para evitar la incertidumbre o, en el extremo contrario, vivir determinados "
        "vínculos con una intensidad que altera profundamente la seguridad que necesitas "
        "para sentirte en equilibrio.\n\n"

        "El equilibrio aparece cuando descubres que estabilidad y transformación no "
        "son necesidades incompatibles. Tauro aporta arraigo, paciencia y capacidad "
        "para sostener; Escorpio aporta profundidad, honestidad y capacidad para renovar "
        "aquello que ha dejado de servir. Cuando ambos polos colaboran, puedes construir "
        "vínculos profundos sin perder tu centro y atravesar los cambios sin renunciar "
        "a aquello que verdaderamente te sostiene."
    ),


    ("Géminis", "Sagitario"): (
        "Tu eje de identidad y vínculo se organiza entre Géminis y Sagitario. "
        "El Ascendente en Géminis necesita construir una forma de estar en el mundo "
        "basada en la curiosidad, el intercambio y la capacidad para observar la "
        "realidad desde diferentes perspectivas. Existe una tendencia natural a "
        "preguntar, explorar posibilidades y adaptar tu manera de responder a medida "
        "que incorporas nueva información.\n\n"

        "El Descendente en Sagitario muestra que los vínculos importantes introducen "
        "una necesidad de amplitud, dirección y sentido. Las relaciones pueden acercarte "
        "a personas, ideas o experiencias que amplían tu horizonte y te invitan a ir "
        "más allá de lo inmediato. A través del encuentro descubres que conocer muchas "
        "posibilidades resulta más enriquecedor cuando puedes reconocer cuáles tienen "
        "un significado verdadero para ti.\n\n"

        "La tensión de este eje puede aparecer entre la necesidad de mantener abiertas "
        "distintas opciones y el deseo de encontrar una dirección más definida. En "
        "algunos momentos puedes permanecer en la exploración sin llegar a comprometerte "
        "con una perspectiva; en otros, una idea que parece dar sentido a la vida "
        "puede volverse demasiado rígida y dejar poco espacio para nuevas preguntas.\n\n"

        "El equilibrio aparece cuando curiosidad y sentido pueden alimentarse mutuamente. "
        "Géminis aporta flexibilidad, capacidad para preguntar y atención a los matices; "
        "Sagitario aporta perspectiva, dirección y capacidad para integrar lo aprendido "
        "en una visión más amplia. Cuando ambos polos colaboran, puedes mantener una "
        "mente abierta sin perder orientación y construir vínculos donde el intercambio "
        "no solo aporta información, sino también nuevas formas de comprender la vida."
    ),


    ("Cáncer", "Capricornio"): (
        "Tu eje de identidad y vínculo se organiza entre Cáncer y Capricornio. "
        "El Ascendente en Cáncer necesita construir una forma de estar en el mundo "
        "basada en la sensibilidad, la protección y la capacidad para reconocer lo "
        "que necesitas emocionalmente. Existe una tendencia natural a percibir el "
        "entorno desde una gran receptividad y a buscar espacios donde puedas sentir "
        "pertenencia, confianza y seguridad.\n\n"

        "El Descendente en Capricornio muestra que los vínculos importantes introducen "
        "una necesidad de estructura, responsabilidad y compromiso. Las relaciones te "
        "invitan a construir acuerdos capaces de sostenerse en el tiempo y a descubrir "
        "que la seguridad emocional también necesita límites claros, estabilidad y "
        "una implicación concreta por parte de quienes participan en el vínculo.\n\n"

        "La tensión de este eje puede aparecer cuando la necesidad de protección y "
        "cercanía emocional entra en conflicto con la exigencia de asumir responsabilidades "
        "o establecer límites. En algunos momentos puedes buscar refugio en lo conocido "
        "cuando una situación requiere mayor autonomía; en otros, intentar mantener el "
        "control o responder a las obligaciones puede llevarte a dejar en segundo plano "
        "necesidades emocionales importantes.\n\n"

        "El equilibrio aparece cuando cuidado y responsabilidad dejan de funcionar como "
        "fuerzas opuestas. Cáncer aporta sensibilidad, capacidad para nutrir y conexión "
        "con las necesidades emocionales; Capricornio aporta estructura, límites y "
        "capacidad para sostener compromisos. Cuando ambos polos colaboran, puedes crear "
        "vínculos donde la cercanía encuentra una estructura que la protege y el compromiso "
        "no necesita construirse a costa de la sensibilidad."
    ),


    ("Leo", "Acuario"): (
        "Tu eje de identidad y vínculo se organiza entre Leo y Acuario. "
        "El Ascendente en Leo necesita construir una forma de estar en el mundo "
        "basada en la autenticidad, la expresión personal y la confianza en aquello "
        "que te hace único. Existe una tendencia natural a desarrollar una presencia "
        "propia, mostrar tus capacidades y encontrar formas de participar en la vida "
        "que reflejen con claridad quién eres.\n\n"

        "El Descendente en Acuario muestra que los vínculos importantes introducen "
        "una necesidad de libertad, igualdad y apertura hacia formas diferentes de "
        "relacionarse. Las relaciones pueden acercarte a personas que cuestionan tus "
        "referencias habituales, amplían tu perspectiva y te invitan a reconocer que "
        "cada integrante del vínculo necesita conservar su individualidad.\n\n"

        "La tensión de este eje puede aparecer entre la necesidad de sentir reconocimiento "
        "por aquello que eres y la necesidad de construir relaciones donde ninguna "
        "persona ocupe el centro. En algunos momentos puedes buscar "
        "confirmación externa de tu valor; en otros, tomar demasiada distancia puede "
        "convertirse en una forma de protegerte frente a la vulnerabilidad que implica "
        "mostrarte y dejarte ver dentro de una relación.\n\n"

        "El equilibrio aparece cuando expresión individual y libertad compartida dejan "
        "de competir entre sí. Leo aporta presencia, creatividad y capacidad para "
        "implicarte desde el corazón; Acuario aporta perspectiva, autonomía y capacidad "
        "para reconocer el valor de la diferencia. Cuando ambos polos colaboran, puedes "
        "ocupar tu lugar sin necesitar reducir el espacio del otro y construir vínculos "
        "donde cada persona pueda expresarse con autenticidad."
    ),


    ("Virgo", "Piscis"): (
        "Tu eje de identidad y vínculo se organiza entre Virgo y Piscis. "
        "El Ascendente en Virgo necesita construir una forma de estar en el mundo "
        "basada en la observación, el discernimiento y la capacidad para comprender "
        "cómo funcionan las cosas. Existe una tendencia natural a analizar la "
        "experiencia, detectar aquello que necesita atención y desarrollar recursos "
        "que te permitan responder de manera práctica y eficaz.\n\n"

        "El Descendente en Piscis muestra que los vínculos importantes introducen "
        "una dimensión más sensible, intuitiva y difícil de organizar únicamente "
        "desde la razón. Las relaciones pueden invitarte a confiar en aquello que "
        "no siempre puede explicarse, aceptar cierta incertidumbre y reconocer "
        "necesidades emocionales que requieren comprensión más que soluciones "
        "inmediatas.\n\n"

        "La tensión de este eje puede aparecer entre la necesidad de comprender, "
        "ordenar y definir lo que sucede y aquellas experiencias relacionales que "
        "no admiten respuestas precisas. En algunos momentos puedes intentar analizar "
        "en exceso aquello que necesita ser sentido; en otros, una apertura demasiado "
        "grande hacia las necesidades ajenas puede dificultar distinguir qué te "
        "corresponde sostener y qué pertenece a la otra persona.\n\n"

        "El equilibrio aparece cuando discernimiento y sensibilidad pueden trabajar "
        "juntos. Virgo aporta claridad, criterio y capacidad para traducir las "
        "necesidades en acciones concretas; Piscis aporta empatía, intuición y "
        "capacidad para aceptar aquello que no puede controlarse por completo. "
        "Cuando ambos polos colaboran, puedes cuidar los detalles sin perder la "
        "visión del conjunto y construir vínculos sensibles donde la comprensión "
        "no implique renunciar a límites claros."
    ),


    ("Libra", "Aries"): (
        "Tu eje de identidad y vínculo se organiza entre Libra y Aries. "
        "El Ascendente en Libra necesita construir una forma de estar en el mundo "
        "basada en la relación, la búsqueda de equilibrio y la capacidad para tener "
        "en cuenta diferentes perspectivas. Existe una tendencia natural a observar "
        "cómo tus decisiones afectan al entorno, buscar puntos de encuentro y cuidar "
        "la forma en que estableces contacto con otras personas.\n\n"

        "El Descendente en Aries muestra que los vínculos importantes introducen "
        "una necesidad de afirmación, iniciativa y claridad respecto al propio deseo. "
        "Las relaciones pueden acercarte a personas directas, independientes o capaces "
        "de tomar decisiones con rapidez, confrontándote con una energía que te invita "
        "a reconocer también qué quieres tú y hasta dónde quieres negociar.\n\n"

        "La tensión de este eje puede aparecer cuando el deseo de mantener el equilibrio "
        "dificulta tomar una posición clara o cuando la afirmación individual irrumpe "
        "en el vínculo de una manera demasiado brusca. En algunos momentos puedes "
        "adaptarte en exceso para evitar el conflicto; en otros, la necesidad acumulada "
        "de recuperar tu propio espacio puede expresarse con más intensidad de la "
        "necesaria.\n\n"

        "El equilibrio aparece cuando relación y afirmación dejan de funcionar como "
        "necesidades opuestas. Libra aporta escucha, perspectiva y capacidad para "
        "construir acuerdos; Aries aporta iniciativa, claridad y conexión con el propio "
        "deseo. Cuando ambos polos colaboran, puedes tener en cuenta al otro sin "
        "desdibujarte y defender tu posición sin convertir cada diferencia en una "
        "confrontación."
    ),


    ("Escorpio", "Tauro"): (
        "Tu eje de identidad y vínculo se organiza entre Escorpio y Tauro. "
        "El Ascendente en Escorpio necesita construir una forma de estar en el mundo "
        "basada en la profundidad, la capacidad de transformación y una percepción "
        "muy sensible de aquello que sucede más allá de lo evidente. Existe una "
        "tendencia natural a implicarte intensamente en la experiencia de la vida y a proteger "
        "aquello que consideras íntimo hasta que existe suficiente confianza para "
        "mostrarlo.\n\n"

        "El Descendente en Tauro muestra que los vínculos importantes introducen "
        "una necesidad de estabilidad, sencillez y continuidad. Las relaciones pueden "
        "enseñarte el valor de aquello que se construye poco a poco, permanece y no "
        "necesita estar transformándose constantemente. A través del encuentro aparece "
        "la posibilidad de encontrar seguridad en la presencia, la constancia y la "
        "confianza que se desarrolla con el tiempo.\n\n"

        "La tensión de este eje puede aparecer entre la intensidad con la que vives "
        "determinadas experiencias y la necesidad de conservar una base estable dentro "
        "del vínculo. En algunos momentos puedes buscar profundidad allí donde sería "
        "suficiente permitir que las cosas sean más sencillas; en otros, aferrarte a "
        "una situación segura puede dificultar atravesar un cambio que resulta necesario "
        "para que la relación siga evolucionando.\n\n"

        "El equilibrio aparece cuando transformación y estabilidad pueden sostenerse "
        "mutuamente. Escorpio aporta profundidad, honestidad y capacidad para atravesar "
        "los cambios; Tauro aporta arraigo, paciencia y capacidad para conservar aquello "
        "que tiene verdadero valor. Cuando ambos polos colaboran, puedes implicarte "
        "profundamente sin vivir cada cambio como una amenaza y construir vínculos "
        "estables que también tengan espacio para transformarse."
    ),


    ("Sagitario", "Géminis"): (
        "Tu eje de identidad y vínculo se organiza entre Sagitario y Géminis. "
        "El Ascendente en Sagitario necesita construir una forma de estar en el mundo "
        "basada en la exploración, la amplitud de perspectiva y la búsqueda de un sentido "
        "que permita orientar tu vida. Existe una tendencia natural a mirar más "
        "allá de lo inmediato, seguir aquello que despierta entusiasmo y desarrollar "
        "una visión propia a partir de lo que descubres en el camino.\n\n"

        "El Descendente en Géminis muestra que los vínculos importantes introducen "
        "una necesidad de intercambio, curiosidad y apertura hacia perspectivas "
        "diferentes. Las relaciones pueden acercarte a personas que hacen preguntas, "
        "aportan nuevos datos o cuestionan algunas de tus certezas, invitándote a "
        "mantener viva la capacidad de revisar aquello que creías comprender.\n\n"

        "La tensión de este eje puede aparecer entre la necesidad de encontrar una "
        "dirección clara y la diversidad de posibilidades que surgen a través del "
        "encuentro. En algunos momentos puedes aferrarte a una visión demasiado definida "
        "y perder de vista matices importantes; en otros, atender a demasiadas opciones "
        "puede dispersar la energía y dificultar reconocer qué camino tiene verdadero "
        "sentido para ti.\n\n"

        "El equilibrio aparece cuando visión y curiosidad pueden enriquecerse mutuamente. "
        "Sagitario aporta perspectiva, dirección y capacidad para integrar la experiencia humana "
        "en una comprensión más amplia; Géminis aporta flexibilidad, preguntas y atención "
        "a los matices. Cuando ambos polos colaboran, puedes sostener una dirección sin "
        "convertirla en una certeza rígida y construir vínculos donde las nuevas ideas "
        "amplían tu visión en lugar de amenazarla."
    ),


    ("Capricornio", "Cáncer"): (
        "Tu eje de identidad y vínculo se organiza entre Capricornio y Cáncer. "
        "El Ascendente en Capricornio necesita construir una forma de estar en el mundo "
        "basada en la autonomía, la responsabilidad y la capacidad para sostener una "
        "dirección propia. Existe una tendencia natural a observar lo que una situación "
        "requiere, asumir responsabilidades y avanzar mediante objetivos que puedan "
        "construirse de manera gradual y consistente.\n\n"

        "El Descendente en Cáncer muestra que los vínculos importantes introducen "
        "una necesidad de cercanía, cuidado y seguridad emocional. Las relaciones "
        "pueden acercarte a una dimensión más sensible de la experiencia humana, invitándote "
        "a reconocer necesidades que no siempre pueden resolverse mediante esfuerzo, "
        "control o responsabilidad y que requieren confianza, receptividad y capacidad "
        "para dejarte cuidar.\n\n"

        "La tensión de este eje puede aparecer cuando la necesidad de mantener el "
        "control, cumplir con las responsabilidades o mostrar fortaleza dificulta "
        "expresar vulnerabilidad dentro del vínculo. En algunos momentos puedes asumir "
        "más de lo que te corresponde para conservar la estabilidad; en otros, una "
        "necesidad emocional no reconocida puede terminar condicionando decisiones "
        "que intentabas abordar únicamente desde criterios prácticos.\n\n"

        "El equilibrio aparece cuando responsabilidad y sensibilidad pueden sostenerse "
        "mutuamente. Capricornio aporta estructura, autonomía y capacidad para mantener "
        "compromisos; Cáncer aporta cuidado, receptividad y conexión con las necesidades "
        "emocionales. Cuando ambos polos colaboran, puedes construir una vida sólida "
        "sin convertir la autosuficiencia en aislamiento y crear vínculos donde cuidar "
        "y dejarte cuidar formen parte de una misma experiencia de seguridad."
    ),


    ("Acuario", "Leo"): (
        "Tu eje de identidad y vínculo se organiza entre Acuario y Leo. "
        "El Ascendente en Acuario necesita construir una forma de estar en el mundo "
        "basada en la libertad, la autenticidad y la capacidad para pensar de manera "
        "independiente. Existe una tendencia natural a diferenciarte, cuestionar lo "
        "establecido y buscar una expresión propia que no dependa de encajar en modelos "
        "ajenos.\n\n"

        "El Descendente en Leo muestra que los vínculos importantes activan otra necesidad: "
        "sentir reconocimiento y valoración dentro de la relación. Aunque una parte de ti "
        "protege su autonomía y necesita espacio, otra descubre a través del encuentro el "
        "deseo de compartir afecto, creatividad, presencia y una implicación más visible.\n\n"

        "La tensión de este eje puede aparecer cuando la independencia se convierte en "
        "distancia o cuando la necesidad de reconocimiento dentro del vínculo genera una "
        "dependencia excesiva de la respuesta de la otra persona. En algunos momentos puede resultar "
        "más sencillo mantenerte en una posición observadora que mostrar plenamente lo que "
        "sientes; en otros, el vínculo puede despertar una necesidad intensa de sentir "
        "que ocupas un lugar especial.\n\n"

        "El equilibrio aparece cuando comprendes que diferenciarte no exige desconectarte y "
        "que vincularte no implica renunciar a tu individualidad. Acuario aporta libertad, "
        "perspectiva y autenticidad; Leo aporta calidez, presencia y capacidad para implicarte "
        "desde el corazón. Cuando ambos polos colaboran, puedes construir relaciones donde "
        "cada persona conserva su singularidad y, al mismo tiempo, se siente plenamente "
        "reconocida."
    ),


    ("Piscis", "Virgo"): (
        "Tu eje de identidad y vínculo se organiza entre Piscis y Virgo. "
        "El Ascendente en Piscis necesita construir una forma de estar en el mundo "
        "basada en la sensibilidad, la intuición y la capacidad para percibir matices "
        "que no siempre pueden explicarse de manera racional. Existe una tendencia "
        "natural a responder de forma receptiva a lo que sucede a tu alrededor y a "
        "dejar que la vida revele su significado antes de intentar definirla "
        "por completo.\n\n"

        "El Descendente en Virgo muestra que los vínculos importantes introducen "
        "una necesidad de claridad, discernimiento y concreción. Las relaciones pueden "
        "acercarte a personas o situaciones que te invitan a distinguir mejor qué "
        "necesitas, establecer límites y traducir aquello que sientes en decisiones "
        "y acciones capaces de sostenerse en la vida cotidiana.\n\n"

        "La tensión de este eje puede aparecer cuando la apertura hacia lo que sucede "
        "dificulta establecer criterios claros o cuando la necesidad de comprender y "
        "ordenar termina reduciendo experiencias que necesitan más tiempo para mostrar "
        "su sentido. En algunos momentos puedes adaptarte demasiado a las necesidades "
        "del entorno; en otros, intentar definir cada detalle puede convertirse en una "
        "forma de protegerte frente a la incertidumbre.\n\n"

        "El equilibrio aparece cuando sensibilidad y discernimiento pueden trabajar "
        "juntos. Piscis aporta intuición, empatía y capacidad para percibir el conjunto; "
        "Virgo aporta criterio, límites y capacidad para convertir una percepción en "
        "algo concreto. Cuando ambos polos colaboran, puedes mantener una actitud abierta a la "
        "experiencia sin perder claridad y construir vínculos donde cuidar y comprender "
        "al otro no implique dejar de reconocer tus propias necesidades."
    ),
}


EJE_MC_IC = {
    ("Aries", "Libra"): (
        "Tu eje de raíces y proyección se organiza entre Libra y Aries. "
        "El Medio Cielo en Aries señala una necesidad de construir una dirección "
        "propia, tomar iniciativa y abrir caminos en la forma en que ocupas tu lugar "
        "en el mundo. Tu desarrollo hacia lo público puede requerir autonomía, capacidad "
        "para decidir y suficiente libertad para actuar de acuerdo con aquello que "
        "consideras importante, especialmente cuando necesitas iniciar una etapa nueva "
        "o avanzar sin referencias previamente establecidas.\n\n"

        "El Fondo de Cielo en Libra muestra una base interna que busca equilibrio, "
        "armonía y capacidad para convivir con diferentes perspectivas. En el ámbito "
        "más íntimo necesitas espacios donde sea posible bajar la intensidad, encontrar "
        "puntos de encuentro y sentir que las relaciones cercanas pueden sostenerse "
        "desde la reciprocidad y el respeto mutuo.\n\n"

        "La tensión de este eje puede aparecer cuando la necesidad de avanzar con "
        "determinación hacia una dirección propia entra en conflicto con el deseo de "
        "mantener el equilibrio en tu entorno más cercano. En algunos momentos puedes "
        "posponer una decisión para evitar alterar una relación; en otros, concentrarte "
        "demasiado en avanzar puede hacer que pierdas de vista la necesidad de cuidar "
        "la base desde la que estás construyendo.\n\n"

        "El equilibrio aparece cuando comprendes que iniciativa y cooperación pueden "
        "formar parte de una misma estructura. Aries aporta decisión, impulso y "
        "capacidad para abrir camino en tu proyección; Libra aporta escucha, equilibrio "
        "y capacidad para construir una base relacional estable. Cuando ambos polos "
        "colaboran, puedes avanzar hacia una dirección propia sin desvincularte de "
        "aquello que sostiene tu equilibrio interno."
    ),


    ("Tauro", "Escorpio"): (
        "Tu eje de raíces y proyección se organiza entre Escorpio y Tauro. "
        "El Medio Cielo en Tauro señala una necesidad de construir una dirección "
        "estable, consistente y capaz de sostenerse con el tiempo. Tu desarrollo "
        "hacia lo público tiende a necesitar procesos graduales, resultados concretos "
        "y suficiente continuidad para consolidar aquello que estás construyendo. "
        "Más que avanzar mediante cambios constantes, necesitas reconocer qué merece "
        "tu energía y darle tiempo para adquirir solidez.\n\n"

        "El Fondo de Cielo en Escorpio muestra una base interna más intensa y "
        "transformadora. En el ámbito íntimo pueden existir procesos profundos de "
        "cambio, una fuerte necesidad de proteger tu vulnerabilidad y una percepción "
        "especialmente sensible de aquello que sucede bajo la superficie. Tu sensación "
        "de seguridad no depende únicamente de conservar lo conocido, sino también de "
        "poder atravesar transformaciones internas sin perder el contacto contigo.\n\n"

        "La tensión de este eje puede aparecer cuando la necesidad de construir "
        "estabilidad en el exterior convive con procesos internos que periódicamente "
        "obligan a revisar, soltar o transformar aquello sobre lo que te estabas "
        "apoyando. En algunos momentos puedes intentar mantener una estructura porque "
        "te proporciona seguridad aunque internamente ya haya comenzado un cambio; "
        "en otros, una transformación profunda puede dificultar sostener la continuidad "
        "que necesitas en tu dirección externa.\n\n"

        "El equilibrio aparece cuando estabilidad y transformación dejan de percibirse "
        "como movimientos incompatibles. Tauro aporta constancia, paciencia y capacidad "
        "para materializar una dirección; Escorpio aporta profundidad, honestidad y "
        "capacidad para renovar las bases cuando dejan de sostenerte. Cuando ambos polos "
        "colaboran, puedes construir algo duradero precisamente porque eres capaz de "
        "transformar desde dentro aquello que necesita cambiar."
    ),


    ("Géminis", "Sagitario"): (
        "Tu eje de raíces y proyección se organiza entre Sagitario y Géminis. "
        "El Medio Cielo en Géminis señala una necesidad de construir una dirección "
        "flexible, abierta al aprendizaje y capaz de evolucionar a medida que incorporas "
        "nueva información. Tu desarrollo hacia lo público puede desplegarse a través "
        "de la comunicación, el intercambio de ideas o la conexión entre ámbitos "
        "diferentes. Más que seguir necesariamente una única trayectoria, necesitas "
        "sentir que puedes aprender, explorar y mantener activa tu curiosidad.\n\n"

        "El Fondo de Cielo en Sagitario muestra una base interna que necesita amplitud, "
        "sentido y una perspectiva desde la que comprender la vida. En el ámbito "
        "más íntimo resulta importante sentir que tu vida forma parte de un horizonte "
        "más amplio y que aquello que haces mantiene alguna relación con tus convicciones, "
        "tu manera de comprender el mundo o aquello que da significado a tu recorrido.\n\n"

        "La tensión de este eje puede aparecer cuando la diversidad de posibilidades "
        "que encuentras en tu desarrollo externo dificulta mantener una dirección con "
        "sentido o cuando una visión interna demasiado definida limita tu capacidad "
        "para explorar alternativas. En algunos momentos puedes dispersarte entre "
        "distintos intereses; en otros, intentar encajar cada experiencia dentro de "
        "una explicación previa puede impedirte descubrir algo nuevo.\n\n"

        "El equilibrio aparece cuando curiosidad y sentido pueden alimentarse "
        "mutuamente. Géminis aporta flexibilidad, intercambio y capacidad para conectar "
        "informaciones diferentes en tu proyección; Sagitario aporta perspectiva, "
        "orientación y una base interna desde la que reconocer qué merece ser explorado. "
        "Cuando ambos polos colaboran, puedes mantener una dirección significativa sin "
        "cerrarte a nuevos caminos y permitir que lo que aprendes transforme también "
        "tu manera de comprender hacia dónde quieres avanzar."
    ),


    ("Cáncer", "Capricornio"): (
        "Tu eje de raíces y proyección se organiza entre Capricornio y Cáncer. "
        "El Medio Cielo en Cáncer señala una necesidad de construir una dirección "
        "en la que la sensibilidad, el cuidado y la capacidad para generar confianza "
        "tengan un lugar importante. Tu desarrollo hacia lo público puede estar "
        "vinculado con crear espacios de pertenencia, acompañar procesos o aportar "
        "una forma de presencia que tenga en cuenta las necesidades humanas de quienes "
        "participan en aquello que construyes.\n\n"

        "El Fondo de Cielo en Capricornio muestra una base interna que necesita "
        "estructura, autonomía y sensación de solidez. En el ámbito más íntimo puede "
        "existir una fuerte necesidad de sentir que puedes sostenerte, organizar tu "
        "vida y responder ante las dificultades con recursos propios. La seguridad "
        "interna se fortalece cuando existen límites claros y una estructura desde "
        "la que afrontar lo que ocurre.\n\n"

        "La tensión de este eje puede aparecer cuando la sensibilidad que orienta tu "
        "proyección entra en conflicto con una base interna acostumbrada a contener, "
        "responsabilizarse o mantener el control. En algunos momentos puedes asumir "
        "demasiadas responsabilidades y dejar poco espacio para reconocer lo que "
        "necesitas; en otros, implicarte emocionalmente en aquello que haces puede "
        "dificultar establecer los límites necesarios para sostenerlo a largo plazo.\n\n"

        "El equilibrio aparece cuando sensibilidad y estructura pueden trabajar juntas. "
        "Cáncer aporta cuidado, receptividad y capacidad para generar pertenencia en tu "
        "proyección; Capricornio aporta límites, responsabilidad y una base interna "
        "capaz de sostener lo construido. Cuando ambos polos colaboran, puedes ocupar "
        "un lugar en el mundo donde cuidar no signifique cargar con todo y donde la "
        "fortaleza no requiera desconectarte de aquello que sientes."
    ),


    ("Leo", "Acuario"): (
        "Tu eje de raíces y proyección se organiza entre Acuario y Leo. "
        "El Medio Cielo en Leo señala una necesidad de construir una dirección "
        "en la que puedas expresar algo propio, desarrollar tus capacidades y "
        "sentir que aquello que aportas lleva una huella personal reconocible. "
        "Tu desarrollo hacia lo público necesita espacio para la creatividad, "
        "la iniciativa y una participación suficientemente visible como para "
        "reconocer que estás ocupando un lugar que realmente te representa.\n\n"

        "El Fondo de Cielo en Acuario muestra una base interna que necesita libertad, "
        "autonomía y espacio para construir sus propias referencias. En el ámbito "
        "más íntimo resulta importante poder tomar cierta distancia de expectativas "
        "o modelos heredados y descubrir qué forma de vida responde verdaderamente "
        "a tu manera de entender el mundo. La seguridad interna aumenta cuando puedes "
        "sentirte parte de algo sin perder tu individualidad.\n\n"

        "La tensión de este eje puede aparecer cuando la necesidad de expresarte y "
        "ocupar un lugar propio entra en conflicto con una parte interna que necesita "
        "distancia, independencia o libertad respecto a la mirada externa. En algunos "
        "momentos puedes buscar reconocimiento para confirmar el valor de aquello que "
        "haces; en otros, tomar demasiada distancia puede dificultar implicarte "
        "plenamente y mostrar aquello que podrías aportar.\n\n"

        "El equilibrio aparece cuando expresión individual y libertad interna pueden "
        "sostenerse mutuamente. Leo aporta creatividad, presencia y capacidad para "
        "dar una forma visible a lo que nace de ti; Acuario aporta independencia, "
        "perspectiva y capacidad para construir desde referencias propias. Cuando "
        "ambos polos colaboran, puedes ocupar un lugar visible sin depender por "
        "completo del reconocimiento externo y desarrollar una dirección personal "
        "que conserve suficiente libertad para seguir evolucionando."
    ),


    ("Virgo", "Piscis"): (
        "Tu eje de raíces y proyección se organiza entre Piscis y Virgo. "
        "El Medio Cielo en Virgo señala una necesidad de construir una dirección "
        "basada en la utilidad, el discernimiento y la capacidad para mejorar aquello "
        "en lo que participas. Tu desarrollo hacia lo público puede necesitar tareas "
        "concretas, procesos que puedas comprender y una sensación clara de que tus "
        "capacidades sirven para organizar, resolver o contribuir de forma útil dentro del "
        "entorno en el que te desarrollas.\n\n"

        "El Fondo de Cielo en Piscis muestra una base interna mucho más sensible, "
        "receptiva y difícil de organizar mediante criterios estrictamente racionales. "
        "En el ámbito más íntimo necesitas espacios donde puedas bajar las exigencias, "
        "permitir que la experiencia de la vida se asiente y permanecer en contacto con aquello "
        "que sientes sin tener que encontrar inmediatamente una explicación o una "
        "solución concreta.\n\n"

        "La tensión de este eje puede aparecer cuando la necesidad de ser eficaz, "
        "ordenar o responder correctamente en el exterior deja poco espacio para una "
        "vida interna que necesita mayor flexibilidad. En algunos momentos puedes "
        "exigirte respuestas precisas cuando todavía necesitas tiempo para comprender "
        "qué está ocurriendo; en otros, una falta de claridad interna puede dificultar "
        "establecer prioridades y sostener una dirección concreta hacia fuera.\n\n"

        "El equilibrio aparece cuando discernimiento y sensibilidad pueden trabajar "
        "juntos. Virgo aporta criterio, precisión y capacidad para convertir una "
        "necesidad en una acción concreta; Piscis aporta intuición, receptividad y "
        "capacidad para percibir dimensiones de la vida que no siempre pueden "
        "medirse o explicarse. Cuando ambos polos colaboran, puedes construir una "
        "dirección útil y organizada sin desconectarte de tu mundo interno ni convertir "
        "la eficacia en una exigencia permanente."
    ),


    ("Libra", "Aries"): (
        "Tu eje de raíces y proyección se organiza entre Aries y Libra. "
        "El Medio Cielo en Libra señala una necesidad de construir una dirección "
        "en la que la cooperación, el equilibrio y la capacidad para relacionar "
        "perspectivas diferentes tengan un lugar importante. Tu desarrollo hacia "
        "lo público puede apoyarse en la creación de acuerdos, la mediación o la "
        "capacidad para generar contextos donde distintas personas puedan encontrarse "
        "sin perder sus propias posiciones.\n\n"

        "El Fondo de Cielo en Aries muestra una base interna que necesita autonomía, "
        "iniciativa y libertad para responder desde el propio impulso. En el ámbito "
        "más íntimo resulta importante disponer de un espacio donde puedas actuar "
        "sin tener que negociar constantemente tus decisiones y recuperar el contacto "
        "con aquello que quieres antes de considerar las expectativas del entorno.\n\n"

        "La tensión de este eje puede aparecer cuando la necesidad de construir una "
        "proyección equilibrada y tener en cuenta diferentes intereses entra en "
        "conflicto con una base interna que necesita decidir con mayor rapidez y "
        "autonomía. En algunos momentos puedes dedicar demasiada energía a encontrar "
        "la posición adecuada para todos; en otros, una necesidad acumulada de actuar "
        "por tu cuenta puede llevarte a romper equilibrios que todavía podrían haberse "
        "negociado.\n\n"

        "El equilibrio aparece cuando cooperación y autonomía dejan de funcionar como "
        "fuerzas opuestas. Libra aporta escucha, perspectiva y capacidad para construir "
        "acuerdos en tu proyección; Aries aporta iniciativa, decisión y una base interna "
        "desde la que reconocer qué quieres. Cuando ambos polos colaboran, puedes "
        "construir junto a otras personas sin perder dirección propia y afirmar tus "
        "decisiones sin renunciar a la capacidad de encontrar puntos de encuentro."
    ),


    ("Escorpio", "Tauro"): (
        "Tu eje de raíces y proyección se organiza entre Tauro y Escorpio. "
        "El Medio Cielo en Escorpio señala una necesidad de construir una dirección "
        "que permita profundizar, transformar y trabajar con aquello que no siempre "
        "resulta visible a primera vista. Tu desarrollo hacia lo público puede llevarte "
        "a contextos que requieren atravesar procesos complejos, comprender dinámicas "
        "profundas o participar en transformaciones capaces de modificar de manera "
        "significativa una situación existente.\n\n"

        "El Fondo de Cielo en Tauro muestra una base interna que necesita estabilidad, "
        "continuidad y contacto con aquello que proporciona una sensación concreta de "
        "seguridad. En el ámbito más íntimo resulta importante disponer de ritmos "
        "previsibles, referencias estables y espacios donde puedas descansar de la "
        "intensidad externa. Tu equilibrio interno se fortalece cuando puedes reconocer "
        "qué necesitas conservar y qué recursos te ayudan a permanecer en tu centro.\n\n"

        "La tensión de este eje puede aparecer cuando una proyección orientada hacia "
        "procesos de cambio y transformación altera la estabilidad que necesitas en "
        "tu base. En algunos momentos puedes implicarte en situaciones intensas hasta "
        "perder contacto con tus propios ritmos; en otros, la necesidad de conservar "
        "lo conocido puede dificultar asumir una transformación necesaria para seguir "
        "avanzando en tu dirección externa.\n\n"

        "El equilibrio aparece cuando transformación y estabilidad pueden sostenerse "
        "mutuamente. Escorpio aporta profundidad, capacidad para atravesar cambios y "
        "disposición para llegar al núcleo de una situación; Tauro aporta arraigo, "
        "paciencia y una base interna desde la que esos procesos pueden ser sostenidos. "
        "Cuando ambos polos colaboran, puedes participar en transformaciones profundas "
        "sin vivir permanentemente en la intensidad y conservar estabilidad sin "
        "convertirla en resistencia al cambio."
    ),


    ("Sagitario", "Géminis"): (
        "Tu eje de raíces y proyección se organiza entre Géminis y Sagitario. "
        "El Medio Cielo en Sagitario señala una necesidad de construir una dirección "
        "que amplíe tus horizontes y mantenga una conexión clara con aquello que da "
        "sentido a lo que haces. Tu desarrollo hacia lo público puede llevarte a "
        "explorar nuevos ámbitos, transmitir una visión, ampliar conocimientos o "
        "participar en experiencias que te permitan crecer más allá de referencias "
        "previamente conocidas.\n\n"

        "El Fondo de Cielo en Géminis muestra una base interna que necesita curiosidad, "
        "movimiento mental e intercambio. En el ámbito más íntimo resulta importante "
        "poder preguntar, conversar y contemplar diferentes posibilidades sin sentir "
        "que debes llegar inmediatamente a una conclusión. Tu seguridad interna puede "
        "fortalecerse cuando existe espacio para revisar ideas y comprender lo que "
        "vives desde distintos puntos de vista.\n\n"

        "La tensión de este eje puede aparecer cuando la necesidad de construir una "
        "dirección con sentido lleva a definir demasiado pronto una visión, mientras "
        "tu base interna continúa necesitando explorar otras posibilidades. En algunos "
        "momentos puedes sentir que debes saber hacia dónde vas antes de haber reunido "
        "toda la información necesaria; en otros, mantener abiertas demasiadas opciones "
        "puede dificultar comprometerte con una dirección y desarrollarla en profundidad.\n\n"

        "El equilibrio aparece cuando sentido y curiosidad pueden alimentarse "
        "mutuamente. Sagitario aporta perspectiva, orientación y capacidad para dar "
        "una dirección amplia a tu proyección; Géminis aporta preguntas, flexibilidad "
        "y una base interna capaz de revisar lo que creías saber. Cuando ambos polos "
        "colaboran, puedes avanzar hacia un horizonte significativo sin convertirlo "
        "en una verdad cerrada y permitir que cada nueva experiencia amplíe también "
        "tu manera de comprender el camino."
    ),


    ("Capricornio", "Cáncer"): (
        "Tu eje de raíces y proyección se organiza entre Cáncer y Capricornio. "
        "El Medio Cielo en Capricornio señala una necesidad de construir una dirección "
        "basada en la responsabilidad, la autonomía y la capacidad para desarrollar "
        "algo sólido a lo largo del tiempo. Tu proyección puede requerir objetivos "
        "claros, compromiso y la posibilidad de comprobar que el esfuerzo realizado "
        "se traduce en una estructura cada vez más consistente.\n\n"

        "El Fondo de Cielo en Cáncer muestra una base interna que necesita cuidado, "
        "pertenencia y seguridad emocional. En el ámbito más íntimo resulta importante "
        "disponer de espacios donde puedas bajar las exigencias, reconocer lo que "
        "necesitas y sentir que no todo depende de tu capacidad para responder o "
        "hacerte cargo. Tu estabilidad interna se fortalece cuando puedes mantener "
        "contacto con aquello que te nutre y te proporciona una sensación de sostén.\n\n"

        "La tensión de este eje puede aparecer cuando las responsabilidades, los "
        "objetivos o la necesidad de mantener una estructura hacia fuera dejan poco "
        "espacio para atender lo que sucede dentro. En algunos momentos puedes asumir "
        "más de lo necesario porque sientes que debes poder sostenerlo; en otros, una "
        "necesidad emocional no atendida puede hacer más difícil mantener la dirección "
        "y la constancia que buscas en tu desarrollo externo.\n\n"

        "El equilibrio aparece cuando responsabilidad y cuidado pueden sostenerse "
        "mutuamente. Capricornio aporta estructura, perseverancia y capacidad para "
        "construir una dirección estable; Cáncer aporta sensibilidad, pertenencia y "
        "una base interna desde la que recuperar recursos. Cuando ambos polos colaboran, "
        "puedes asumir responsabilidades sin convertirlas en una exigencia permanente "
        "y construir algo sólido hacia fuera sin dejar de cuidar aquello que te "
        "sostiene por dentro."
    ),


    ("Acuario", "Leo"): (
        "Tu eje de raíces y proyección se organiza entre Leo y Acuario. "
        "El Medio Cielo en Acuario señala una necesidad de construir una dirección "
        "propia, abierta al cambio y suficientemente libre como para no quedar limitada "
        "por modelos establecidos. Tu desarrollo hacia lo público puede llevarte a "
        "cuestionar formas conocidas de hacer las cosas, introducir perspectivas "
        "diferentes o participar en proyectos donde la innovación, la autonomía y "
        "la construcción colectiva tengan un lugar importante.\n\n"

        "El Fondo de Cielo en Leo muestra una base interna que necesita calidez, "
        "expresión personal y reconocimiento de aquello que nace genuinamente de ti. "
        "En el ámbito más íntimo resulta importante disponer de espacios donde puedas "
        "mostrarte sin tener que justificar constantemente quién eres y mantener "
        "contacto con aquello que despierta creatividad, entusiasmo y una sensación "
        "profunda de vitalidad.\n\n"

        "La tensión de este eje puede aparecer cuando la necesidad de desarrollar "
        "una dirección independiente o diferente hacia fuera entra en conflicto con "
        "una base interna que necesita implicación personal y sentirse reconocida. "
        "En algunos momentos puedes tomar distancia para preservar tu libertad y "
        "terminar desconectándote de aquello que realmente te importa; en otros, "
        "la necesidad de que tu aportación sea valorada puede dificultar participar "
        "en proyectos donde el protagonismo necesita ser compartido.\n\n"

        "El equilibrio aparece cuando libertad y expresión personal pueden sostenerse "
        "mutuamente. Acuario aporta independencia, perspectiva y capacidad para "
        "imaginar nuevas formas de participar en el mundo; Leo aporta creatividad, "
        "implicación y una base interna conectada con aquello que tiene significado "
        "personal para ti. Cuando ambos polos colaboran, puedes contribuir a algo más "
        "amplio sin diluir tu singularidad y mostrar lo que tienes para aportar sin "
        "necesitar ocupar siempre el centro."
    ),


    ("Piscis", "Virgo"): (
        "Tu eje de raíces y proyección se organiza entre Virgo y Piscis. "
        "El Medio Cielo en Piscis señala una necesidad de construir una dirección "
        "que mantenga espacio para la sensibilidad, la intuición y una percepción "
        "amplia de aquello que sucede. Tu desarrollo hacia lo público puede llevarte "
        "a contextos donde acompañar, inspirar, crear o comprender dimensiones de la "
        "experiencia que no siempre pueden reducirse a resultados concretos. Necesitas "
        "sentir que aquello que haces conserva una conexión profunda con lo que tiene "
        "sentido para ti.\n\n"

        "El Fondo de Cielo en Virgo muestra una base interna que necesita orden, "
        "claridad y referencias concretas desde las que organizar la vida. "
        "En el ámbito más íntimo resulta importante poder distinguir qué necesitas, "
        "establecer prioridades y disponer de hábitos o estructuras cotidianas que "
        "te ayuden a recuperar estabilidad cuando el entorno se vuelve demasiado "
        "abierto, intenso o difícil de definir.\n\n"

        "La tensión de este eje puede aparecer cuando una proyección guiada por la "
        "intuición o por una dirección todavía difícil de concretar entra en conflicto "
        "con una base interna que necesita comprender qué está ocurriendo y saber cómo "
        "actuar. En algunos momentos puedes intentar definir demasiado pronto aquello "
        "que todavía está tomando forma; en otros, confiar únicamente en lo que sientes "
        "puede dificultar convertir una percepción valiosa en una dirección que pueda "
        "sostenerse en la práctica.\n\n"

        "El equilibrio aparece cuando intuición y discernimiento pueden trabajar "
        "juntos. Piscis aporta sensibilidad, visión de conjunto y capacidad para "
        "percibir posibilidades que todavía no tienen una forma definida; Virgo aporta "
        "criterio, organización y una base interna capaz de traducir esas percepciones "
        "en acciones concretas. Cuando ambos polos colaboran, puedes construir una "
        "dirección sensible y significativa sin perder estructura y utilizar el orden "
        "como un soporte para dar forma a aquello que intuyes."
    ),

}



INTEGRACION_MODALIDADES_ANGULARES = {

    ("Cardinal", "Cardinal"): (
        "Los dos ejes principales de tu carta se organizan desde una modalidad cardinal. "
        "Esto hace que identidad, vínculos, raíces y proyección compartan una misma necesidad "
        "de movimiento, iniciativa y capacidad para abrir nuevas etapas. Existe una tendencia "
        "a responder a la vida poniendo procesos en marcha, tomando decisiones y "
        "buscando una dirección activa frente a aquello que sucede.\n\n"

        "Cuando esta modalidad se concentra en los cuatro ángulos, la vida puede sentirse "
        "marcada por momentos de inicio, cambio de rumbo y necesidad de actuar. La fortaleza "
        "está en la capacidad para movilizar situaciones y no permanecer demasiado tiempo "
        "en estados de bloqueo. El desafío aparece cuando cada área intenta avanzar al mismo "
        "tiempo y resulta difícil sostener, consolidar o dar continuidad a lo ya comenzado.\n\n"

        "La integración consiste en conservar la iniciativa sin convertir cada tensión en "
        "una señal de que es necesario empezar de nuevo. Cuando la energía cardinal encuentra "
        "una dirección clara y aprende a sostener los procesos que pone en marcha, los cuatro "
        "ángulos pueden funcionar como una estructura dinámica, capaz de generar movimiento "
        "sin perder coherencia."
    ),


    ("Cardinal", "Fija"): (
        "El eje de identidad y vínculo se organiza desde una modalidad cardinal, "
        "mientras que el eje de raíces y proyección responde a una modalidad fija. "
        "Esto crea una arquitectura en la que la forma de situarte ante la vida "
        "y relacionarte con los demás necesita movimiento, iniciativa y capacidad para "
        "abrir nuevas etapas, mientras que tu base interna y la dirección que construyes "
        "hacia el exterior buscan continuidad, estabilidad y tiempo para consolidarse.\n\n"

        "Esta combinación puede generar una dinámica particular entre avanzar y sostener. "
        "Puedes responder con rapidez ante nuevas situaciones, tomar decisiones o modificar "
        "la forma en que te posicionas y te relacionas, mientras que los cambios vinculados "
        "con tus raíces o con una dirección importante de vida necesitan procesos más "
        "graduales. No todo dentro de tu arquitectura cambia al mismo ritmo.\n\n"

        "La tensión puede aparecer cuando una parte de ti está preparada para iniciar un "
        "movimiento mientras otra necesita conservar aquello que ya ha construido. "
        "Forzar cambios profundos antes de que exista una base suficiente puede generar "
        "resistencia; pero mantener una estructura únicamente porque resulta conocida "
        "puede terminar limitando movimientos que ya necesitan producirse.\n\n"

        "La integración consiste en permitir que la modalidad cardinal abra caminos y "
        "que la modalidad fija les dé continuidad. Cuando ambas funciones colaboran, "
        "puedes iniciar cambios sin desmontar innecesariamente tus bases y utilizar la "
        "estabilidad no como resistencia, sino como el soporte desde el que una nueva "
        "dirección puede desarrollarse y adquirir consistencia."
    ),


    ("Cardinal", "Mutable"): (
        "El eje de identidad y vínculo se organiza desde una modalidad cardinal, "
        "mientras que el eje de raíces y proyección responde a una modalidad mutable. "
        "Esto crea una arquitectura en la que tu forma de situarte ante la vida "
        "y relacionarte con los demás necesita iniciativa, movimiento y capacidad para "
        "abrir nuevas etapas, mientras que tu base interna y la dirección que construyes "
        "hacia el exterior necesitan flexibilidad, aprendizaje y margen para reajustarse "
        "a medida que las circunstancias cambian.\n\n"

        "Esta combinación favorece una estructura especialmente dinámica. La modalidad "
        "cardinal impulsa a poner procesos en marcha, mientras que la mutable permite "
        "revisarlos, adaptarlos y encontrar alternativas cuando la realidad introduce "
        "nuevas variables. Puede existir facilidad para responder al cambio, aunque no "
        "siempre resulte sencillo determinar cuándo una dirección necesita ser modificada "
        "y cuándo conviene mantenerla el tiempo suficiente para que pueda desarrollarse.\n\n"

        "La tensión puede aparecer cuando la necesidad de iniciar un movimiento se combina "
        "con una tendencia posterior a reconsiderar sus posibilidades. En algunos momentos "
        "puedes abrir una etapa antes de haber definido suficientemente hacia dónde conduce; "
        "en otros, la capacidad para adaptarte puede mantener demasiadas opciones disponibles "
        "y dificultar que una decisión llegue a adquirir continuidad.\n\n"

        "La integración consiste en permitir que la modalidad cardinal marque el comienzo "
        "y que la modalidad mutable ajuste el recorrido sin perder de vista la dirección. "
        "Cuando ambas funciones colaboran, puedes iniciar cambios con decisión y conservar "
        "la flexibilidad necesaria para aprender durante el proceso, sin interpretar cada "
        "reajuste como la necesidad de comenzar de nuevo."
    ),



    ("Fija", "Fija"): (
        "Los dos ejes principales de tu carta se organizan desde una modalidad fija. "
        "Esto hace que identidad, vínculos, raíces y proyección compartan una misma "
        "necesidad de continuidad, estabilidad y capacidad para sostener aquello que "
        "consideras importante. Existe una tendencia natural a construir con tiempo, "
        "profundizar en lo que eliges y mantener una dirección una vez que has reconocido "
        "su valor.\n\n"

        "Cuando esta modalidad se concentra en los cuatro ángulos, la arquitectura "
        "adquiere una gran capacidad de permanencia. No sueles necesitar cambiar de "
        "dirección constantemente para sentir que avanzas; el crecimiento aparece muchas "
        "veces a través de la constancia, la repetición y la consolidación progresiva de "
        "experiencias que van adquiriendo profundidad con el tiempo.\n\n"

        "La tensión puede aparecer cuando una estructura ya consolidada necesita modificarse. "
        "La misma capacidad que permite sostener vínculos, raíces o proyectos durante largos "
        "periodos puede convertirse en resistencia si el cambio se vive como una amenaza a "
        "la estabilidad conseguida. En algunos momentos puede resultar más fácil perseverar "
        "que reconocer que una forma de organizar la vida ha cumplido su función.\n\n"

        "La integración consiste en conservar la fortaleza de la modalidad fija sin "
        "confundir estabilidad con inmovilidad. Cuando aprendes a distinguir qué merece "
        "permanecer y qué necesita transformarse, los cuatro ángulos pueden funcionar como "
        "una estructura especialmente sólida: capaz de sostener procesos largos, profundizar "
        "en ellos y atravesar los cambios sin perder el centro."
    ),


    ("Fija", "Mutable"): (
        "El eje de identidad y vínculo se organiza desde una modalidad fija, "
        "mientras que el eje de raíces y proyección responde a una modalidad mutable. "
        "Esto crea una arquitectura en la que tu forma de situarte ante la vida "
        "y relacionarte con los demás necesita continuidad, estabilidad y tiempo para "
        "consolidarse, mientras que tu base interna y la dirección que construyes hacia "
        "el exterior necesitan mayor flexibilidad, aprendizaje y capacidad para "
        "reajustarse a medida que las circunstancias cambian.\n\n"

        "Esta combinación puede hacer que mantengas posiciones personales o vínculos "
        "con bastante continuidad mientras otras dimensiones de tu vida atraviesan "
        "procesos de revisión y adaptación. Tu dirección externa puede evolucionar, "
        "incorporar nuevas posibilidades o cambiar de forma sin que eso implique "
        "necesariamente modificar con la misma rapidez aquello que reconoces como "
        "parte estable de tu identidad.\n\n"

        "La tensión puede aparecer cuando los cambios en tus raíces o en tu dirección "
        "requieren revisar posiciones, dinámicas relacionales o formas de responder "
        "que necesitan más tiempo para modificarse. En algunos momentos puedes intentar "
        "mantener una referencia estable mientras el contexto continúa cambiando; en "
        "otros, una adaptación constante en determinadas áreas puede generar la sensación "
        "de que falta una estructura suficientemente firme desde la que orientarte.\n\n"

        "La integración consiste en permitir que la modalidad mutable introduzca "
        "flexibilidad sin desorganizar aquello que necesita continuidad. La modalidad "
        "fija aporta profundidad, constancia y capacidad para conservar referencias "
        "estables; la mutable aporta adaptación, aprendizaje y capacidad para revisar "
        "el recorrido. Cuando ambas funciones colaboran, puedes mantener un centro "
        "consistente mientras tus raíces y tu dirección evolucionan con la experiencia de la vida."
    ),


    ("Mutable", "Cardinal"): (
        "El eje de identidad y vínculo se organiza desde una modalidad mutable, "
        "mientras que el eje de raíces y proyección responde a una modalidad cardinal. "
        "Esto crea una arquitectura en la que tu forma de situarte ante la vida "
        "y relacionarte con los demás necesita flexibilidad, aprendizaje y capacidad "
        "para adaptarse, mientras que tu base interna y la dirección que construyes "
        "hacia el exterior introducen una necesidad mayor de iniciativa, decisión y "
        "apertura de nuevas etapas.\n\n"

        "Esta combinación puede hacer que los movimientos importantes comiencen en "
        "tus raíces o en tu dirección vital y que después necesites un tiempo para "
        "reorganizar tu manera de posicionarte y relacionarte dentro de la nueva "
        "situación. La modalidad cardinal pone procesos en marcha, mientras que la "
        "mutable permite explorar distintas formas de responder a aquello que esos "
        "cambios van generando.\n\n"

        "La tensión puede aparecer cuando una nueva etapa exige decisiones antes de "
        "que hayas tenido tiempo suficiente para explorar todas sus implicaciones. "
        "En algunos momentos puedes adaptarte rápidamente a un cambio sin haber "
        "definido todavía cuál es tu posición dentro de él; en otros, contemplar "
        "demasiadas posibilidades puede dificultar responder con claridad cuando "
        "una situación requiere tomar una dirección concreta.\n\n"

        "La integración consiste en permitir que la modalidad cardinal abra el "
        "movimiento y que la modalidad mutable encuentre la forma más adecuada de "
        "habitarlo. La primera aporta iniciativa y capacidad para generar nuevas "
        "etapas; la segunda aporta flexibilidad, aprendizaje y capacidad para ajustar "
        "la respuesta durante el recorrido. Cuando ambas funciones colaboran, puedes "
        "atravesar cambios importantes sin necesitar tener todas las respuestas desde "
        "el principio y adaptar tu manera de estar y relacionarte sin perder la "
        "dirección que ha puesto el proceso en marcha."
    ),


    ("Mutable", "Fija"): (
        "El eje de identidad y vínculo se organiza desde una modalidad mutable, "
        "mientras que el eje de raíces y proyección responde a una modalidad fija. "
        "Esto crea una arquitectura en la que tu forma de situarte ante la vida "
        "y relacionarte con los demás necesita flexibilidad, aprendizaje y capacidad "
        "para adaptarse, mientras que tu base interna y la dirección que construyes "
        "hacia el exterior buscan continuidad, estabilidad y tiempo para consolidarse.\n\n"

        "Esta combinación permite modificar la forma en que respondes a las situaciones "
        "o te relacionas con otras personas sin que cada reajuste tenga que alterar las "
        "bases sobre las que organizas tu vida. Puedes explorar diferentes maneras de "
        "posicionarte, incorporar nuevas perspectivas y aprender de la experiencia "
        "mientras mantienes referencias internas o direcciones externas que necesitan "
        "mayor permanencia.\n\n"

        "La tensión puede aparecer cuando aquello que vas descubriendo a través de la "
        "experiencia empieza a cuestionar una estructura que lleva tiempo consolidada. "
        "En algunos momentos puedes adaptarte a las circunstancias sin revisar si la "
        "base desde la que estás actuando sigue teniendo sentido; en otros, la necesidad "
        "de preservar una dirección estable puede limitar cambios en tu forma de estar "
        "o relacionarte que ya necesitan encontrar espacio.\n\n"

        "La integración consiste en utilizar la flexibilidad de la modalidad mutable "
        "para revisar y enriquecer una estructura que no necesita cambiar constantemente. "
        "La modalidad mutable aporta capacidad de aprendizaje, adaptación y apertura "
        "hacia nuevas perspectivas; la fija aporta profundidad, constancia y capacidad "
        "para sostener una dirección. Cuando ambas funciones colaboran, puedes evolucionar "
        "en tu manera de estar y relacionarte sin perder las referencias que te sostienen, "
        "y modificar esas referencias cuando la experiencia muestra que ya no responden "
        "a lo que necesitas."
    ),


    ("Mutable", "Mutable"): (
        "Los dos ejes principales de tu carta se organizan desde una modalidad mutable. "
        "Esto hace que identidad, vínculos, raíces y proyección compartan una misma "
        "necesidad de adaptación, aprendizaje y capacidad para reajustarse a medida "
        "que la vida introduce nuevas posibilidades. Existe una tendencia "
        "natural a observar, comparar, modificar y encontrar distintas formas de "
        "responder antes de considerar que una dirección está definitivamente cerrada.\n\n"

        "Cuando esta modalidad se concentra en los cuatro ángulos, la arquitectura "
        "adquiere una gran flexibilidad. Puedes adaptarte con rapidez a contextos "
        "cambiantes, incorporar nueva información y reorganizar tu manera de estar "
        "en el mundo sin necesidad de mantener siempre las mismas referencias. "
        "La fortaleza está en la capacidad para aprender durante el recorrido y "
        "encontrar alternativas cuando una estructura deja de resultar útil.\n\n"

        "La tensión puede aparecer cuando la adaptación constante dificulta consolidar "
        "una dirección o reconocer cuándo un proceso necesita continuidad en lugar de "
        "otra revisión. En algunos momentos puede resultar sencillo comprender muchas "
        "posibilidades pero más difícil elegir una; en otros, el movimiento continuo "
        "puede generar la sensación de que siempre falta una referencia suficientemente "
        "estable desde la que organizar la vida.\n\n"

        "La integración consiste en conservar la flexibilidad sin convertirla en "
        "dispersión. Cuando la modalidad mutable encuentra referencias internas claras, "
        "los cuatro ángulos pueden funcionar como una estructura especialmente capaz "
        "de evolucionar, aprender y responder a los cambios sin perder coherencia. "
        "Adaptarte deja entonces de significar cambiar constantemente de dirección y "
        "se convierte en la capacidad de ajustar el recorrido sin perder de vista "
        "aquello que realmente estás construyendo."
    ),

}



# ─── SIGNOS DUPLICADOS ──────────────────────────────────────────────────────

SIGNO_DUPLICADO = {

"Aries": (
    "Cuando Aries aparece en dos cúspides consecutivas, el principio de la iniciativa se "
    "convierte en un hilo conductor que organiza dos áreas importantes de la vida. "
    "Ambos territorios tienden a desarrollarse mediante la acción, la autonomía y la capacidad "
    "de abrir caminos propios, creando una continuidad natural entre ellos.\n\n"

    "Esta repetición no implica que Aries sea más fuerte que el resto de los signos de la "
    "carta, sino que su forma de afrontar la realidad conecta dos funciones diferentes de la "
    "personalidad. Lo que aprendes en una de esas áreas suele facilitar también el desarrollo "
    "de la otra, como si ambas compartieran un mismo lenguaje interno.\n\n"

    "Con el tiempo descubres que la iniciativa no necesita manifestarse como una reacción "
    "permanente frente a la vida, sino como la confianza para comenzar aquello que realmente "
    "merece ser construido. Cuando esa continuidad se integra, Aries aporta dinamismo, "
    "coherencia y una gran capacidad para impulsar procesos de crecimiento."
),

"Tauro": (
    "Cuando Tauro aparece en dos cúspides consecutivas, la necesidad de construir estabilidad, "
    "consolidar recursos y avanzar con constancia se convierte en un principio organizador de "
    "dos ámbitos diferentes de la carta. Ambos territorios evolucionan siguiendo ritmos "
    "similares, favoreciendo una sensación de continuidad entre ellos.\n\n"

    "La repetición del signo indica que determinadas experiencias se desarrollan apoyándose en "
    "las mismas cualidades: paciencia, perseverancia y capacidad para construir sobre bases "
    "sólidas. El aprendizaje realizado en una casa suele fortalecer también la otra, generando "
    "una sensación de coherencia en el modo de afrontar esos espacios de la vida.\n\n"

    "Con el tiempo comprendes que la verdadera estabilidad no consiste únicamente en conservar "
    "lo ya conocido, sino también en desarrollar la confianza necesaria para seguir creciendo. "
    "Cuando esta continuidad se integra, Tauro aporta solidez, serenidad y una capacidad muy "
    "estable para sostener procesos importantes."
),

"Géminis": (
    "Cuando Géminis aparece en dos cúspides consecutivas, la curiosidad, el aprendizaje y la "
    "adaptabilidad organizan conjuntamente dos áreas de experiencia. Ambos territorios se "
    "alimentan mutuamente mediante el intercambio de ideas, la observación y la capacidad para "
    "establecer conexiones entre experiencias diferentes.\n\n"

    "Esta continuidad hace que el desarrollo de una casa enriquezca también la otra, ya que "
    "ambas comparten una misma manera de comprender la realidad. La comunicación, el movimiento "
    "y la flexibilidad se convierten en herramientas que permiten integrar ambos espacios de "
    "forma natural.\n\n"

    "Con el paso del tiempo descubres que la verdadera riqueza de Géminis no consiste en "
    "acumular experiencias, sino en convertirlas en comprensión. Cuando esta continuidad madura, "
    "aparece una notable capacidad para aprender, adaptarte y conectar ámbitos diferentes de tu "
    "vida con una gran agilidad."
),


"Cáncer": (
    "Cuando Cáncer aparece en dos cúspides consecutivas, la sensibilidad, el cuidado y la "
    "necesidad de construir una base emocional sólida se convierten en el principio que organiza "
    "dos áreas consecutivas de la vida. Ambos territorios tienden a desarrollarse mediante "
    "la intuición, el vínculo y la búsqueda de un entorno donde sea posible crecer con seguridad.\n\n"

    "Esta repetición no indica una mayor intensidad de Cáncer, sino una continuidad en la forma "
    "de abordar esas dos dimensiones de la vida. Lo que aprendes sobre confianza, pertenencia o "
    "cuidado en una de ellas suele tener un efecto directo sobre la otra, favoreciendo un "
    "desarrollo coherente entre ambas.\n\n"

    "Con el tiempo descubres que la verdadera seguridad no depende únicamente de proteger aquello "
    "que amas, sino también de desarrollar un refugio interior capaz de acompañarte en cualquier "
    "circunstancia. Cuando esta continuidad se integra, Cáncer aporta sensibilidad, estabilidad "
    "emocional y una profunda capacidad para sostener tanto tu propio crecimiento como el de "
    "quienes te rodean."
),


"Leo": (
    "Cuando Leo aparece en dos cúspides consecutivas, la expresión de la identidad, la creatividad "
    "y la necesidad de desarrollar los propios talentos se convierten en un hilo conductor entre "
    "dos áreas importantes de la carta. Ambos ámbitos encuentran su desarrollo cuando existe "
    "espacio para actuar con autenticidad y aportar algo verdaderamente personal.\n\n"

    "La repetición del signo crea una continuidad natural entre ambas experiencias. La confianza "
    "que desarrollas en una de ellas suele fortalecer también la otra, permitiendo que la "
    "autoexpresión se convierta en un principio organizador de ese tramo de la vida. Más que dos "
    "procesos independientes, ambas casas colaboran en la construcción de una misma sensación de "
    "identidad.\n\n"

    "Con el paso del tiempo descubres que el verdadero reconocimiento nace de expresar quién eres "
    "con honestidad y no de responder a expectativas externas. Cuando esta continuidad madura, "
    "Leo aporta creatividad, autoestima y una presencia capaz de inspirar a otras personas desde "
    "la autenticidad."
),


"Virgo": (
    "Cuando Virgo aparece en dos cúspides consecutivas, la capacidad para observar, organizar y "
    "mejorar la realidad se convierte en el criterio que estructura dos ámbitos consecutivos de la "
    "experiencia. Ambos territorios evolucionan mediante el aprendizaje continuo, la atención a "
    "los detalles y la construcción paciente de habilidades útiles.\n\n"

    "Esta continuidad permite que los avances realizados en una casa repercutan también en la "
    "otra, ya que ambas comparten una misma forma de crecer: mediante pequeños ajustes que, con "
    "el tiempo, producen transformaciones significativas. La vida se organiza así desde la "
    "coherencia, más que desde los cambios bruscos.\n\n"

    "Con el tiempo comprendes que mejorar no significa perseguir la perfección, sino desarrollar "
    "una relación cada vez más consciente con aquello que haces. Cuando esta continuidad se "
    "integra, Virgo aporta claridad, eficacia y una notable capacidad para construir una vida "
    "ordenada sin perder flexibilidad."
),


"Libra": (
    "Cuando Libra aparece en dos cúspides consecutivas, la búsqueda de equilibrio, el diálogo y "
    "la cooperación organizan conjuntamente dos áreas de la vida. Ambos territorios se "
    "desarrollan mediante el encuentro con otras personas y la capacidad para construir relaciones "
    "basadas en el respeto y la reciprocidad.\n\n"

    "La repetición del signo crea una continuidad entre ambas casas, haciendo que lo aprendido en "
    "una relación o situación contribuya también al desarrollo de la otra. Poco a poco descubres "
    "que la armonía no consiste en evitar las diferencias, sino en aprender a integrarlas sin "
    "perder tu propio centro.\n\n"

    "Cuando esta continuidad madura, Libra aporta diplomacia, sentido de la justicia y una gran "
    "capacidad para crear puentes entre personas, ideas o experiencias aparentemente diferentes."
),


"Escorpio": (
    "Cuando Escorpio aparece en dos cúspides consecutivas, la transformación, la profundidad y la "
    "capacidad para regenerarte se convierten en el principio que articula dos ámbitos importantes "
    "de la carta. Ambos territorios evolucionan a través de procesos que invitan a mirar más allá "
    "de la superficie y a permitir que los cambios produzcan una evolución auténtica.\n\n"

    "Esta continuidad hace que las experiencias vividas en una de las casas influyan "
    "profundamente en la otra. Las etapas de crisis, crecimiento o renovación suelen tener un "
    "efecto integrador, permitiendo que ambas áreas evolucionen conjuntamente a medida que tú "
    "también lo haces.\n\n"

    "Con el paso del tiempo descubres que la transformación no es un episodio aislado, sino una "
    "forma de crecimiento permanente. Cuando esta continuidad se integra, Escorpio aporta "
    "fortaleza interior, autenticidad y una extraordinaria capacidad para convertir cada cambio "
    "en una oportunidad de evolución."
),


"Sagitario": (
    "Cuando Sagitario aparece en dos cúspides consecutivas, la búsqueda de sentido, el deseo de "
    "expandir horizontes y la confianza en el aprendizaje se convierten en el principio que "
    "organiza dos áreas consecutivas de la vida. Ambos territorios evolucionan cuando "
    "existe espacio para explorar, comprender y ampliar la mirada sobre la vida, generando una "
    "continuidad natural entre ellos.\n\n"

    "La repetición del signo no significa que Sagitario tenga más peso que otros signos de la "
    "carta, sino que ambas casas comparten una misma forma de desarrollarse. Lo aprendido en una "
    "de ellas suele enriquecer también la otra, permitiendo que cada nueva experiencia aporte una "
    "comprensión más amplia del conjunto. Poco a poco aparece la sensación de que ambos ámbitos "
    "forman parte de un mismo recorrido de crecimiento.\n\n"

    "Con el tiempo descubres que la verdadera expansión no consiste únicamente en llegar más "
    "lejos, sino en comprender cada vez con mayor profundidad el sentido de aquello que vives. "
    "Cuando esta continuidad se integra, Sagitario aporta entusiasmo, visión de conjunto y una "
    "gran capacidad para inspirar crecimiento tanto en ti como en quienes te rodean."
),


"Capricornio": (
    "Cuando Capricornio aparece en dos cúspides consecutivas, la construcción paciente, la "
    "responsabilidad y la capacidad para desarrollar estructuras sólidas organizan conjuntamente "
    "dos áreas importantes de la carta. Ambos territorios evolucionan mediante procesos graduales "
    "que favorecen la estabilidad, el compromiso y la consolidación a largo plazo.\n\n"

    "La continuidad del signo hace que el desarrollo alcanzado en una casa fortalezca también la "
    "otra, ya que ambas comparten una misma manera de crecer: paso a paso, integrando la "
    "experiencia y construyendo sobre bases firmes. Más que buscar resultados inmediatos, existe "
    "una disposición natural a dar tiempo a los procesos para que puedan madurar.\n\n"

    "Con el paso de los años descubres que la verdadera solidez no depende únicamente del esfuerzo, "
    "sino también de construir una vida coherente con tus propios valores. Cuando esta continuidad "
    "se integra, Capricornio aporta madurez, perseverancia y una extraordinaria capacidad para "
    "convertir proyectos importantes en realidades duraderas."
),


"Acuario": (
    "Cuando Acuario aparece en dos cúspides consecutivas, la independencia, la innovación y la "
    "búsqueda de nuevas perspectivas se convierten en el principio organizador de dos ámbitos de "
    "la vida. Ambos territorios evolucionan mediante la libertad para cuestionar lo "
    "establecido, explorar caminos propios y desarrollar una visión amplia de la realidad.\n\n"

    "La repetición del signo crea una continuidad que permite que las transformaciones vividas en "
    "una casa impulsen también la evolución de la otra. Poco a poco descubres que ambas áreas "
    "comparten una misma necesidad de autenticidad y de apertura hacia formas diferentes de vivir, "
    "pensar o relacionarte con el mundo.\n\n"

    "Con el tiempo comprendes que la verdadera libertad no consiste en separarte de todo, sino en "
    "desarrollar una identidad suficientemente sólida como para elegir tu propio camino. Cuando "
    "esta continuidad se integra, Acuario aporta creatividad, visión de futuro y una capacidad "
    "natural para impulsar cambios con sentido."
),


"Piscis": (
    "Cuando Piscis aparece en dos cúspides consecutivas, la sensibilidad, la intuición y la "
    "capacidad para conectar con dimensiones profundas de la vida organizan conjuntamente "
    "dos áreas importantes de la carta. Ambos territorios evolucionan mediante una comprensión "
    "cada vez más amplia de la vida, favoreciendo una continuidad basada en la empatía, la "
    "imaginación y la integración.\n\n"

    "Esta repetición no indica una mayor intensidad de Piscis, sino que ambas casas comparten una "
    "misma forma de desarrollarse. Lo que aprendes en una de ellas suele enriquecer también la "
    "otra, permitiendo que la sensibilidad actúe como un puente entre dos dimensiones distintas "
    "de tu experiencia. Poco a poco ambas áreas comienzan a funcionar de manera cada vez más "
    "coordinada.\n\n"

    "Con el paso del tiempo descubres que la apertura no necesita confundirse con la falta de "
    "límites. Cuando esta continuidad se integra, Piscis aporta inspiración, compasión y una "
    "profunda capacidad para dar unidad a experiencias aparentemente diferentes, ayudándote a "
    "percibir el sentido que las conecta."
),

}



INTERCEPTACION_SIGNO = {
    "Aries": (
        "Aries representa la capacidad de iniciar, afirmarte, actuar desde el deseo "
        "propio y defender tu derecho a ocupar espacio. Cuando este signo está "
        "interceptado, estas funciones existen, pero no siempre encuentran una vía "
        "directa y espontánea de expresión.\n\n"

        "Es posible que durante una parte de tu vida te resulte difícil reconocer "
        "con claridad qué quieres, tomar la iniciativa sin esperar una señal externa "
        "o mostrar abiertamente tu enfado y tu desacuerdo. La acción puede demorarse "
        "mientras valoras las consecuencias, buscas aprobación o intentas adaptarte "
        "a lo que la situación parece requerir.\n\n"

        "Esto no significa que te falten fuerza, impulso o capacidad de decisión. "
        "Con frecuencia, la energía ariana se acumula internamente hasta que encuentra "
        "una salida. Entonces puede manifestarse con mucha intensidad, mediante "
        "decisiones repentinas, reacciones contundentes o una necesidad urgente de "
        "recuperar el espacio que has ido cediendo.\n\n"

        "El desarrollo de Aries interceptado requiere aprender a escuchar el deseo "
        "antes de que se convierta en frustración. Te ayuda practicar decisiones "
        "pequeñas, expresar el desacuerdo cuando todavía es manejable y actuar sin "
        "necesitar una seguridad absoluta sobre el resultado.\n\n"

        "A medida que esta función encuentra una vía consciente, la iniciativa deja "
        "de aparecer únicamente como reacción. Puedes afirmar lo que necesitas, "
        "poner límites y abrir caminos propios sin vivir cada gesto de autonomía "
        "como una ruptura con los demás."
    ),


"Tauro": (
    "Tauro representa la capacidad de construir estabilidad, reconocer el propio "
    "valor y desarrollar una relación sólida con los recursos, el cuerpo y aquello "
    "que aporta seguridad. Cuando este signo está interceptado, estas funciones "
    "necesitan más tiempo para consolidarse y encontrar una forma estable de "
    "expresarse.\n\n"

    "Es posible que durante una parte de tu vida te resulte difícil confiar en tus "
    "propios recursos o sentir que aquello que haces es suficiente. La sensación de "
    "seguridad puede depender con facilidad de factores externos, haciendo que el "
    "bienestar parezca algo que se consigue más que algo que se construye desde "
    "dentro.\n\n"

    "También puede existir una relación cambiante con el cuerpo, el descanso, el "
    "dinero o el disfrute. En ocasiones puedes postergar tus propias necesidades "
    "materiales y emocionales mientras atiendes otras prioridades, perdiendo de "
    "vista aquello que realmente te sostiene en el día a día.\n\n"

    "Esto no significa que carezcas de estabilidad o de capacidad para construirla. "
    "Con frecuencia ocurre lo contrario: a medida que esta función madura, desarrollas "
    "una solidez especialmente profunda porque no depende únicamente de las "
    "circunstancias externas, sino de una confianza interna que ha tenido que "
    "cultivarse conscientemente.\n\n"

    "El desarrollo de Tauro interceptado consiste en reconocer el valor de lo simple, "
    "escuchar las necesidades del cuerpo, permitirte disfrutar sin sentir que debes "
    "justificarlo y aprender a confiar en aquello que ya has construido. Poco a poco "
    "la seguridad deja de ser una meta lejana para convertirse en una base desde la "
    "que puedes vivir con mayor calma, continuidad y presencia."
),


"Géminis": (
    "Géminis representa la capacidad de observar, preguntar, aprender, comunicar y "
    "establecer conexiones entre ideas, personas y experiencias. Cuando este signo "
    "está interceptado, estas funciones suelen desarrollarse de una forma más "
    "interior, requiriendo tiempo para adquirir confianza y expresarse con naturalidad.\n\n"

    "Es posible que durante una parte de tu vida hayas sentido que te cuesta poner "
    "palabras a lo que piensas o compartir tus ideas con la espontaneidad que ves en "
    "otras personas. Puede aparecer la sensación de que necesitas comprender mucho "
    "antes de atreverte a hablar, o de que tus preguntas resultan inoportunas cuando, "
    "en realidad, forman parte de tu manera natural de aprender.\n\n"

    "También puede existir cierta tendencia a guardar pensamientos, revisar una y "
    "otra vez lo que vas a decir o buscar la formulación perfecta antes de expresar "
    "una opinión. Esto puede hacer que la comunicación pierda frescura o que otras "
    "personas no lleguen a conocer la riqueza de tu mundo mental.\n\n"

    "Sin embargo, la función geminiana no está ausente. A medida que encuentra un "
    "espacio seguro para desarrollarse, suele manifestarse como una capacidad de "
    "análisis especialmente fina, una curiosidad constante y una forma de comunicar "
    "que nace de la reflexión más que de la improvisación. Lo que en un principio "
    "parecía una dificultad puede convertirse en una gran profundidad para comprender "
    "matices y establecer conexiones que otros pasan por alto.\n\n"

    "El desarrollo de Géminis interceptado consiste en permitir que la curiosidad "
    "tenga más peso que la necesidad de acertar. Te ayuda expresar ideas aún "
    "incompletas, hacer preguntas sin exigirte conocer previamente la respuesta y "
    "recordar que la comunicación también es un proceso de descubrimiento. Con el "
    "tiempo, tu voz encuentra un cauce propio y la mente deja de ser un espacio donde "
    "todo se revisa para convertirse en una herramienta viva de intercambio y aprendizaje."
),


"Cáncer": (
    "Cáncer representa la capacidad de sentir, cuidar, nutrir y construir un lugar "
    "interno donde poder descansar y recuperar seguridad. Cuando este signo está "
    "interceptado, estas funciones no desaparecen, pero suelen desarrollarse de "
    "forma más lenta y consciente, necesitando tiempo para encontrar una expresión "
    "auténtica.\n\n"

    "Es posible que durante una parte de tu vida hayas aprendido a contener lo que "
    "sientes antes que a expresarlo. Puede costarte reconocer tus propias "
    "necesidades emocionales o pedir apoyo cuando lo necesitas, como si cuidar de "
    "los demás resultara más sencillo que permitir que otros te cuiden a ti.\n\n"

    "También puede existir cierta dificultad para sentir que perteneces plenamente "
    "a un lugar, una familia o un grupo. En ocasiones buscas seguridad adaptándote "
    "a lo que los demás esperan, mientras dejas en un segundo plano aquello que tu "
    "mundo emocional realmente necesita para sentirse en calma.\n\n"

    "Sin embargo, la sensibilidad canceriana permanece intacta. Con frecuencia se "
    "desarrolla de una manera especialmente profunda, convirtiéndose con los años "
    "en una gran capacidad para comprender las emociones propias y ajenas, crear "
    "espacios de confianza y sostener a otras personas desde una presencia serena y "
    "auténtica.\n\n"

    "El desarrollo de Cáncer interceptado consiste en aprender a tratar tus propias "
    "emociones con la misma atención con la que cuidas las de quienes te rodean. Te "
    "ayuda escuchar lo que sientes antes de minimizarlo, permitirte recibir apoyo y "
    "construir entornos donde no necesites protegerte constantemente. Poco a poco, "
    "la seguridad deja de depender de las circunstancias externas y comienza a "
    "nacer de la relación que desarrollas contigo."
),


"Leo": (
    "Leo representa la capacidad de mostrarte tal como eres, expresar tu creatividad, "
    "ocupar un lugar propio y permitir que tu identidad sea vista y reconocida. "
    "Cuando este signo está interceptado, estas funciones suelen necesitar más "
    "tiempo para desarrollarse y encontrar una forma natural de manifestarse.\n\n"

    "Es posible que durante una parte de tu vida hayas sentido cierta incomodidad al "
    "convertirte en el centro de atención o al mostrar aquello que realmente te hace "
    "único. Puede aparecer la tendencia a minimizar tus logros, restar importancia a "
    "tus talentos o pensar que expresar con claridad quién eres podría interpretarse "
    "como vanidad o exceso de protagonismo.\n\n"

    "También puede costarte confiar plenamente en tu capacidad creativa. En ocasiones "
    "esperas tenerlo todo preparado antes de compartir una idea, un proyecto "
    "o una parte de ti, retrasando una expresión que en realidad necesita ejercitarse "
    "para fortalecerse.\n\n"

    "Sin embargo, la energía leonina permanece intacta. Cuando encuentra un espacio "
    "seguro para desarrollarse, suele manifestarse como una presencia cálida, una "
    "creatividad genuina y una capacidad para inspirar a otras personas sin necesidad "
    "de buscar reconocimiento constantemente. El brillo deja de depender de la mirada "
    "externa y nace de la confianza en tu propia autenticidad.\n\n"

    "El desarrollo de Leo interceptado consiste en permitirte ocupar espacio sin pedir "
    "permiso para existir. Te ayuda mostrar tus capacidades antes de sentir que son "
    "perfectas, disfrutar del proceso creativo más que del resultado y recordar que "
    "compartir lo que eres no resta valor a nadie. Con el tiempo, el reconocimiento "
    "deja de ser una necesidad constante para convertirse en una consecuencia natural "
    "de expresar tu identidad con honestidad."
),


"Virgo": (
    "Virgo representa la capacidad de observar con detalle, organizar la vida, "
    "aprender mediante la práctica y mejorar aquello que haces con constancia y "
    "discernimiento. Cuando este signo está interceptado, estas funciones suelen "
    "desarrollarse de una manera más interna, necesitando tiempo para encontrar un "
    "equilibrio entre la exigencia y la confianza.\n\n"

    "Es posible que durante una parte de tu vida hayas sentido que nunca cuentas "
    "con suficiente preparación o que aquello que haces siempre podría ser mejor. "
    "Puede costarte reconocer el valor de tu trabajo porque tu atención se dirige "
    "con facilidad hacia lo que falta por corregir o perfeccionar, en lugar de hacia "
    "todo lo que ya has construido.\n\n"

    "También puede aparecer cierta dificultad para establecer hábitos estables o para "
    "confiar en tu propio criterio al resolver los problemas cotidianos. En ocasiones "
    "la búsqueda de hacerlo bien retrasa la acción, haciendo que la perfección termine "
    "convirtiéndose en un obstáculo para el aprendizaje.\n\n"

    "Sin embargo, la función virginiana permanece plenamente disponible. Cuando madura, "
    "suele manifestarse como una gran capacidad de análisis, un profundo sentido del "
    "detalle y una habilidad poco común para mejorar procesos, acompañar a otras "
    "personas y convertir la experiencia en conocimiento práctico. Lo que al principio "
    "parecía inseguridad puede transformarse en una competencia sólida y serena.\n\n"

    "El desarrollo de Virgo interceptado consiste en aceptar que aprender forma parte "
    "del camino y que la excelencia no nace de evitar los errores, sino de integrar "
    "cada experiencia con humildad y constancia. Te ayuda valorar los pequeños avances, "
    "confiar más en el proceso que en el resultado y recordar que no necesitas hacerlo "
    "todo perfecto para que tenga verdadero valor."
),


"Libra": (
    "Libra representa la capacidad de relacionarte desde el equilibrio, escuchar "
    "otras perspectivas, cooperar y construir vínculos donde exista reciprocidad. "
    "Cuando este signo está interceptado, estas funciones necesitan más tiempo para "
    "desarrollarse y encontrar una forma de expresión auténtica.\n\n"

    "Es posible que durante una parte de tu vida hayas sentido dificultad para "
    "encontrar el punto de equilibrio entre tus propias necesidades y las de los "
    "demás. En ocasiones puedes adaptarte demasiado para preservar la armonía o, "
    "por el contrario, mantener cierta distancia por miedo a perder tu propio "
    "centro dentro de la relación.\n\n"

    "También puede costarte tomar decisiones cuando existen varias opciones "
    "igualmente válidas. No porque te falte criterio, sino porque eres capaz de "
    "percibir los matices de cada alternativa y comprender razones que, a menudo, "
    "parecen contradictorias entre sí. Esa amplitud de mirada puede hacer que la "
    "elección se demore más de lo deseado.\n\n"

    "Sin embargo, la función libriana permanece intacta. A medida que madura, suele "
    "convertirse en una gran capacidad para comprender diferentes puntos de vista, "
    "crear espacios de diálogo y construir relaciones basadas en el respeto mutuo. "
    "La búsqueda de equilibrio deja de consistir en evitar el conflicto para "
    "convertirse en la capacidad de sostenerlo con serenidad cuando es necesario.\n\n"

    "El desarrollo de Libra interceptado consiste en descubrir que la armonía no "
    "depende de complacer a todo el mundo, sino de mantenerte fiel a lo que necesitas "
    "mientras mantienes una actitud abierta al encuentro con el otro. Te ayuda expresar tus "
    "preferencias con claridad, aceptar que no todas las decisiones agradarán a "
    "todos y comprender que un vínculo auténtico puede incluir diferencias sin "
    "perder por ello su equilibrio."
),


"Escorpio": (
    "Escorpio representa la capacidad de transformarte, atravesar las crisis, "
    "comprometerte profundamente con la vida y sostener procesos de cambio que no "
    "siempre pueden controlarse desde la razón. Cuando este signo está interceptado, "
    "estas funciones suelen necesitar más tiempo para desplegarse y encontrar una "
    "forma consciente de expresión.\n\n"

    "Es posible que durante una parte de tu vida hayas intentado mantener el control "
    "de lo que sientes o de las situaciones que generan incertidumbre. Puede costarte "
    "confiar plenamente en los procesos de cambio, mostrando cierta tendencia a "
    "protegerte antes que a exponerte emocionalmente. En ocasiones prefieres mantener "
    "la intensidad bajo control antes que descubrir hasta dónde podría llevarte.\n\n"

    "También puede existir una relación ambivalente con la vulnerabilidad. Mostrar "
    "aquello que te afecta profundamente puede vivirse como un riesgo, haciendo que "
    "guardes partes importantes de tu mundo interno o que solo las compartas cuando "
    "la confianza es absoluta. Esto puede hacer que otras personas perciban una mayor "
    "reserva de la que realmente existe.\n\n"

    "Sin embargo, la función escorpiana permanece plenamente disponible. Cuando madura, "
    "suele convertirse en una extraordinaria capacidad para acompañar procesos de "
    "transformación, comprender lo que permanece oculto y mantener la serenidad allí "
    "donde otras personas se sienten desbordadas. La intensidad deja de vivirse como una amenaza "
    "para convertirse en una fuente de profundidad y autenticidad.\n\n"

    "El desarrollo de Escorpio interceptado consiste en descubrir que transformarte no "
    "significa perderte, sino permitir que algunas partes de ti evolucionen para dar "
    "paso a otras más conscientes. Te ayuda confiar gradualmente en la intimidad, aceptar "
    "que no todo puede controlarse y comprender que las crisis también pueden convertirse "
    "en espacios de regeneración. Con el tiempo, desarrollas una fortaleza que nace no de "
    "evitar el cambio, sino de aprender a atravesarlo."
),


"Sagitario": (
    "Sagitario representa la capacidad de ampliar horizontes, buscar sentido, "
    "confiar en la vida y construir una visión que dé coherencia a la experiencia humana. "
    "Cuando este signo está interceptado, estas funciones suelen desarrollarse de "
    "forma más pausada, necesitando tiempo para encontrar una dirección que nazca "
    "de la propia experiencia y no únicamente de las referencias externas.\n\n"

    "Es posible que durante una parte de tu vida hayas sentido dificultad para "
    "confiar plenamente en tu propio camino. Puede aparecer la sensación de que "
    "siempre falta algo más por aprender antes de dar el siguiente paso o la "
    "tendencia a buscar respuestas definitivas que disipen toda incertidumbre. En "
    "ocasiones esto puede hacer que retrases decisiones importantes mientras "
    "esperas encontrar una certeza absoluta.\n\n"

    "También puede costarte sostener una visión amplia cuando las circunstancias se "
    "vuelven complejas. Es posible alternar periodos de gran entusiasmo con otros "
    "en los que el sentido parece perderse momentáneamente, obligándote a revisar "
    "una y otra vez tus creencias, tus objetivos o la dirección que deseas dar a "
    "tu vida.\n\n"

    "Sin embargo, la función sagitariana permanece plenamente disponible. Cuando "
    "madura, suele manifestarse como una sabiduría profundamente vivida, que no se "
    "apoya en teorías aprendidas sino en aquello que has comprobado a través de tu "
    "propia experiencia. "
    "Tu confianza deja de depender de respuestas cerradas y nace de la capacidad "
    "para seguir caminando incluso cuando no conoces todo el recorrido.\n\n"

    "El desarrollo de Sagitario interceptado consiste en descubrir que el sentido "
    "no siempre aparece al principio del camino, sino que muchas veces se revela "
    "mientras avanzas. Te ayuda permitirte explorar sin exigir certezas completas, "
    "confiar en la experiencia como maestra y comprender que crecer no significa "
    "tener todas las respuestas, sino mantener viva la disposición a seguir "
    "aprendiendo. Con el tiempo, desarrollas una confianza serena que nace de la "
    "coherencia entre lo que comprendes y la forma en que eliges vivir."
),


"Capricornio": (
    "Capricornio representa la capacidad de asumir responsabilidades, construir una "
    "estructura sólida y desarrollar una autoridad que nace de la experiencia y la "
    "madurez. Cuando este signo está interceptado, estas funciones suelen necesitar "
    "más tiempo para consolidarse y encontrar una expresión propia, libre de modelos "
    "o expectativas externas.\n\n"

    "Es posible que durante una parte de tu vida hayas sentido una relación ambivalente "
    "con la responsabilidad. En ocasiones puedes asumir más peso del que realmente te "
    "corresponde, mientras que en otras te cuesta reconocer que ya cuentas con los recursos "
    "necesarios para dar un paso adelante. Puede aparecer la sensación de tener que demostrar "
    "constantemente tu valía antes de permitirte ocupar un lugar de referencia.\n\n"

    "También puede resultar difícil reconocer tu propia autoridad. Es posible que "
    "busques validación en figuras externas o que midas tu valor en función de los "
    "resultados obtenidos, olvidando que la verdadera solidez se construye desde la "
    "coherencia entre lo que eres, lo que haces y las decisiones que sostienes en el "
    "tiempo.\n\n"

    "Sin embargo, la función capricorniana permanece plenamente disponible. Cuando "
    "madura, suele convertirse en una gran capacidad para construir proyectos "
    "duraderos, sostener compromisos con serenidad y ejercer el liderazgo desde la "
    "integridad más que desde el control. La disciplina deja de vivirse como una "
    "exigencia para convertirse en una herramienta al servicio de aquello que "
    "consideras verdaderamente importante.\n\n"

    "El desarrollo de Capricornio interceptado consiste en descubrir que la autoridad "
    "no se recibe desde fuera, sino que se construye poco a poco mediante la experiencia. "
    "Te ayuda reconocer tus propios logros, aceptar responsabilidades acordes a tu "
    "momento vital y permitirte ocupar el lugar que has ido conquistando con el tiempo. "
    "Así, la seguridad deja de depender del reconocimiento externo y nace de la confianza "
    "en tu propia capacidad para sostener lo que construyes."
),


"Acuario": (
    "Acuario representa la capacidad de pensar con independencia, desarrollar una "
    "mirada propia y aportar algo diferente al mundo sin necesidad de ajustarse "
    "constantemente a las expectativas del entorno. Cuando este signo está "
    "interceptado, estas funciones suelen necesitar más tiempo para desplegarse "
    "con naturalidad y convertirse en una expresión consciente de tu identidad.\n\n"

    "Es posible que durante una parte de tu vida hayas sentido que percibes la "
    "realidad de una manera distinta a quienes te rodean, pero que no siempre te "
    "resulta sencillo expresar esa diferencia. En ocasiones puedes adaptar tus "
    "ideas para evitar sentirte al margen o, por el contrario, ocultar parte de tu "
    "originalidad por temor a que otras personas no la comprendan. Esto puede generar la sensación "
    "de que una parte importante de ti permanece invisible.\n\n"

    "También puede aparecer cierta dificultad para encontrar tu lugar dentro de los "
    "grupos o comunidades. Puedes alternar momentos en los que buscas integrarte con "
    "otros en los que necesitas tomar distancia para preservar tu independencia. El "
    "reto no suele ser elegir entre pertenecer o ser libre, sino descubrir que ambas "
    "necesidades pueden convivir.\n\n"

    "Sin embargo, la función acuariana permanece plenamente disponible. Cuando "
    "madura, suele manifestarse como una notable capacidad para observar la realidad "
    "desde perspectivas originales, cuestionar aquello que ya no funciona y abrir "
    "caminos que otras personas todavía no habían considerado. Tu diferencia deja de "
    "vivirse como una rareza para convertirse en una aportación valiosa.\n\n"

    "El desarrollo de Acuario interceptado consiste en confiar progresivamente en tu "
    "propia mirada, incluso cuando no coincide con la de la mayoría. Te ayuda rodearte "
    "de personas con las que puedas pensar en libertad, expresar tus ideas antes de "
    "tener todas las respuestas y comprender que pertenecer no implica renunciar a tu "
    "singularidad. Con el tiempo, descubres que precisamente aquello que te hace "
    "diferente es también una de tus mayores contribuciones."
),


"Piscis": (
    "Piscis representa la capacidad de conectar con aquello que trasciende el control, "
    "abrirse a la intuición, cultivar la compasión y reconocer que no toda la realidad "
    "puede comprenderse únicamente desde la lógica. Cuando este signo está "
    "interceptado, estas funciones suelen desarrollarse de forma gradual, necesitando "
    "tiempo para integrarse sin generar confusión o sensación de desbordamiento.\n\n"

    "Es posible que durante una parte de tu vida hayas aprendido a desconfiar de tu "
    "intuición o de aquello que no puede explicarse con facilidad. Puede resultarte "
    "difícil dar valor a tus percepciones más sutiles, relegándolas a un segundo plano "
    "mientras buscas certezas más objetivas. En otras ocasiones ocurre lo contrario: "
    "la sensibilidad es tan intensa que cuesta distinguir entre lo que realmente te "
    "pertenece y aquello que absorbes del entorno.\n\n"

    "También puede aparecer una tendencia a cargar con el sufrimiento ajeno, intentando "
    "comprender, sostener o aliviar a otras personas antes de atender tus propios "
    "límites. La empatía, cuando no está acompañada de discernimiento, puede hacer que "
    "pierdas temporalmente el contacto con tus propias necesidades o con la dirección "
    "que deseas seguir.\n\n"

    "Sin embargo, la función pisciana permanece plenamente disponible. Cuando madura, "
    "suele convertirse en una profunda capacidad para percibir lo esencial más allá de "
    "las apariencias, acompañar a otras personas con verdadera compasión y confiar en "
    "los procesos de la vida sin necesidad de controlar cada detalle. La sensibilidad "
    "deja de vivirse como una vulnerabilidad para convertirse en una forma de conocimiento.\n\n"

    "El desarrollo de Piscis interceptado consiste en aprender a confiar en tu intuición "
    "sin renunciar al discernimiento. Te ayuda reservar espacios de silencio, escuchar "
    "lo que emerge de tu mundo interior y recordar que la compasión también incluye "
    "cuidarte. Con el tiempo, descubres que abrirte al misterio de la vida "
    "no significa perderte en él, sino desarrollar una confianza serena que te permite "
    "fluir sin dejar de permanecer presente."
),

}


ANARETICO_SIGNO = {

    "Aries": (
        "Cuando una cúspide se encuentra en el grado 29 de Aries, la iniciativa, "
        "la afirmación personal y la capacidad de actuar necesitan alcanzar una forma "
        "más consciente y madura. Puede existir una sensación de urgencia por decidir, "
        "comenzar o defender una dirección propia, como si determinadas experiencias "
        "pidieran una respuesta clara antes de poder avanzar hacia una nueva etapa."
    ),

    "Tauro": (
        "Cuando una cúspide se encuentra en el grado 29 de Tauro, los temas de estabilidad, "
        "seguridad y permanencia adquieren una especial intensidad. Puede existir una fuerte "
        "necesidad de consolidar aquello que proporciona sostén, pero también de reconocer "
        "cuándo una forma de seguridad ha dejado de acompañar el crecimiento. La maduración "
        "consiste en distinguir entre aquello que merece conservarse y aquello que necesita "
        "transformarse para que la estabilidad no se convierta en inmovilidad."
    ),

    "Géminis": (
        "Cuando una cúspide se encuentra en el grado 29 de Géminis, la forma de comprender, "
        "comunicar y relacionar ideas necesita alcanzar mayor claridad y profundidad. Puede "
        "existir una acumulación de información, posibilidades o perspectivas que exige "
        "seleccionar qué resulta realmente significativo. La maduración pasa por transformar "
        "la curiosidad en comprensión y aprender a dar dirección a aquello que has descubierto."
    ),

    "Cáncer": (
        "Cuando una cúspide se encuentra en el grado 29 de Cáncer, los temas vinculados con "
        "la seguridad emocional, la pertenencia y el cuidado alcanzan un punto de especial "
        "maduración. Puede existir una necesidad intensa de proteger aquello que aporta sostén, "
        "pero también de revisar formas de apego o protección que ya no permiten evolucionar. "
        "El aprendizaje consiste en conservar la sensibilidad sin permitir que el miedo "
        "a perder lo conocido limite tu evolución."
    ),

    "Leo": (
        "Cuando una cúspide se encuentra en el grado 29 de Leo, la expresión personal, "
        "la creatividad y la necesidad de reconocimiento requieren una forma más madura de "
        "manifestación. Puede existir una fuerte necesidad de mostrar quién eres o de ocupar "
        "tu lugar con claridad, pero el aprendizaje consiste en hacerlo desde la autenticidad "
        "y no desde la dependencia de la mirada externa."
    ),

    "Virgo": (
        "Cuando una cúspide se encuentra en el grado 29 de Virgo, la necesidad de ordenar, "
        "mejorar y comprender los detalles puede alcanzar una intensidad especial. Existe una "
        "invitación a distinguir entre lo que realmente necesita ser corregido y aquello que "
        "puede ser aceptado tal como es. La maduración aparece cuando el discernimiento deja "
        "de convertirse en exigencia y se transforma en una herramienta de integración."
    ),

    "Libra": (
        "Cuando una cúspide se encuentra en el grado 29 de Libra, los temas de equilibrio, "
        "reciprocidad y relación con los demás requieren una definición más consciente. Puede "
        "existir una necesidad intensa de encontrar armonía o consenso, pero también situaciones "
        "que obligan a elegir sin poder satisfacer todas las perspectivas. La maduración consiste "
        "en sostener el vínculo sin renunciar al propio criterio."
    ),

    "Escorpio": (
        "Cuando una cúspide se encuentra en el grado 29 de Escorpio, los procesos de cambio, "
        "profundidad y desapego adquieren una intensidad especial. Puede existir una sensación "
        "de estar ante situaciones que exigen cerrar ciclos, soltar antiguas formas de control "
        "o atravesar transformaciones que ya no pueden posponerse. La maduración consiste en "
        "confiar en que dejar atrás una estructura no significa perder fuerza, sino permitir "
        "que aparezca una forma más profunda de poder personal."
    ),

    "Sagitario": (
        "Cuando una cúspide se encuentra en el grado 29 de Sagitario, la búsqueda de sentido, "
        "expansión y comprensión necesita alcanzar una forma más integrada. Puede existir una "
        "necesidad intensa de encontrar respuestas, ampliar horizontes o definir una visión de "
        "vida, pero el aprendizaje consiste en transformar la acumulación de experiencias en "
        "sabiduría y reconocer qué dirección merece realmente ser sostenida."
    ),

    "Capricornio": (
        "Cuando una cúspide se encuentra en el grado 29 de Capricornio, los temas de "
        "responsabilidad, estructura y construcción a largo plazo alcanzan un punto de especial "
        "maduración. Puede existir una fuerte necesidad de cumplir, consolidar o demostrar "
        "capacidad, pero también de revisar qué cargas siguen teniendo sentido. La maduración "
        "consiste en mantener el compromiso sin convertir la responsabilidad en una exigencia "
        "permanente."
    ),

    "Acuario": (
        "Cuando una cúspide se encuentra en el grado 29 de Acuario, la necesidad de libertad, "
        "autenticidad e innovación requiere una definición más consciente. Puede existir una "
        "fuerte necesidad de diferenciarte o romper con estructuras que ya no representan tu "
        "manera de pensar. La maduración consiste en transformar la diferencia en una aportación "
        "real, integrando independencia y capacidad de participar en una realidad compartida."
    ),

    "Piscis": (
        "Cuando una cúspide se encuentra en el grado 29 de Piscis, la sensibilidad, la intuición "
        "y la capacidad de entrega alcanzan un punto de especial culminación. Puede existir una "
        "necesidad profunda de cerrar experiencias, soltar expectativas o integrar procesos que "
        "han permanecido abiertos durante mucho tiempo. La maduración consiste en conservar la "
        "receptividad sin perder claridad, límites ni dirección personal."
    ),

}


ANARETICO_CASA = {

    1: (
        "En la Casa 1, esta culminación se expresa en la construcción de la identidad "
        "y en la manera de ocupar tu lugar en el mundo. Puede señalar etapas en las que "
        "necesitas revisar profundamente cómo te presentas, qué parte de tu identidad sigue "
        "siendo auténtica y qué forma de expresarte ha quedado pequeña para la persona en "
        "la que te estás convirtiendo."
    ),

    2: (
        "En la Casa 2, esta culminación afecta a la relación con los recursos, la seguridad "
        "y el valor personal. Puede llevarte a revisar aquello en lo que has apoyado tu "
        "estabilidad y a reconocer qué recursos necesitan consolidarse, transformarse o dejar "
        "de funcionar como medida de tu propio valor."
    ),

    3: (
        "En la Casa 3, esta culminación se manifiesta en la manera de aprender, comunicar "
        "y organizar tus ideas. Puede señalar una necesidad de abandonar formas de pensamiento "
        "que ya no permiten avanzar y desarrollar una manera más madura de expresar aquello "
        "que has comprendido."
    ),

    4: (
        "En la Casa 4, este proceso se vive en las raíces, el hogar y la sensación interna "
        "de sostén. Puede implicar revisar qué formas de seguridad heredadas siguen siendo "
        "necesarias y cuáles necesitan evolucionar para que el pasado pueda convertirse en "
        "una base, en lugar de funcionar como un límite."
    ),

    5: (
        "En la Casa 5, esta culminación afecta a la creatividad, el disfrute y la expresión "
        "personal. Puede aparecer la necesidad de abandonar formas de mostrarte que ya no "
        "representan quién eres y encontrar una expresión más madura, libre y coherente con "
        "tu identidad actual."
    ),

    6: (
        "En la Casa 6, este proceso se expresa a través de los hábitos, la vida cotidiana "
        "y la relación con el bienestar. Puede señalar momentos en los que determinadas "
        "rutinas han cumplido su función y necesitan ser revisadas para construir una forma "
        "más consciente y sostenible de organizar la vida diaria."
    ),

    7: (
        "En la Casa 7, esta culminación se manifiesta en los vínculos y las relaciones "
        "significativas. Puede llevarte a revisar maneras de relacionarte que ya no permiten "
        "un encuentro auténtico y a desarrollar vínculos donde compromiso, reciprocidad e "
        "individualidad puedan convivir de una forma más madura."
    ),

    8: (
        "En la Casa 8, este proceso se expresa en la intimidad, los recursos compartidos "
        "y las transformaciones profundas. Puede señalar experiencias que obligan a soltar "
        "formas antiguas de control, confianza o dependencia para permitir una relación más "
        "consciente con la vulnerabilidad y el cambio."
    ),

    9: (
        "En la Casa 9, esta culminación afecta a las creencias, la búsqueda de sentido y la "
        "forma de comprender la vida. Puede indicar momentos en los que una visión del mundo "
        "ha llegado a su límite y necesita ampliarse para integrar experiencias que ya no "
        "encajan dentro de las respuestas anteriores."
    ),

    10: (
        "En la Casa 10, este proceso se manifiesta en la vocación, la responsabilidad y la "
        "dirección de tu desarrollo. Puede señalar etapas en las que una forma de proyectarte "
        "o construir tu trayectoria ha llegado a su límite y necesitas redefinir qué deseas "
        "aportar realmente al mundo."
    ),

    11: (
        "En la Casa 11, esta culminación se expresa en los proyectos de futuro, la comunidad "
        "y la relación con la comunidad. Puede llevarte a revisar qué grupos, objetivos o "
        "visiones compartidas continúan representando tu evolución y cuáles pertenecen ya "
        "a una etapa que necesita cerrarse."
    ),

    12: (
        "En la Casa 12, este proceso tiene una dimensión especialmente interna. Puede señalar "
        "la necesidad de integrar experiencias, cerrar ciclos y dejar atrás formas de sostener "
        "el mundo interior que ya han cumplido su función. La maduración ocurre muchas veces "
        "en silencio, antes de que pueda expresarse externamente."
    ),

}


CIERRE_CASAS_POR_SIGNO = (
    "Tu carta no está formada por doce áreas independientes. Cada casa ocupa un lugar "
    "dentro de una estructura mayor y se relaciona con las demás para construir una "
    "forma particular de habitar la vida.\n\n"

    "A lo largo de este recorrido has podido observar cómo cambia esa estructura según "
    "el signo que abre cada casa, cómo se organizan los grandes ejes de la carta y qué "
    "particularidades pueden modificar su distribución. Algunas áreas necesitan iniciativa, "
    "otras continuidad, adaptación, profundidad o tiempo. Ninguna funciona por separado.\n\n"

    "Comprender esta arquitectura permite dejar de mirar cada ámbito de tu vida como un "
    "problema aislado. La forma en que construyes seguridad influye en tus vínculos; tus "
    "raíces participan en la dirección que eliges; tu manera de expresarte modifica los "
    "espacios que compartes; y aquello que sucede en tu mundo interior también forma parte "
    "de la manera en que te relacionas con el exterior.\n\n"

    "No necesitas desarrollar todas estas áreas de la misma manera ni al mismo tiempo. "
    "No necesitas desarrollar todas estas áreas de la misma manera ni al mismo tiempo. Cada etapa de la vida pone el foco en unas experiencias diferentes. La invitación es reconocer qué necesita cada espacio de tu vida y ofrecerle las condiciones para desarrollarse, sin perder de vista la estructura completa que da sentido al conjunto."
)



# ─── MAPAS DE TEXTOS DEL MÓDULO ────────────────────────────────

TEXTOS_CASAS = {
    1: CASA_1,
    2: CASA_2,
    3: CASA_3,
    4: CASA_4,
    5: CASA_5,
    6: CASA_6,
    7: CASA_7,
    8: CASA_8,
    9: CASA_9,
    10: CASA_10,
    11: CASA_11,
    12: CASA_12,
}



# ─── CÁLCULO ASTROLÓGICO ──────────────────────────────────────────────────────

def geocodificar(ciudad):
    g = Nominatim(
        user_agent="ai_casas_por_signo",
        timeout=10
    )
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

    h = (
        dt_utc.hour
        + dt_utc.minute / 60.0
        + dt_utc.second / 3600.0
    )

    return swe.julday(
        dt_utc.year,
        dt_utc.month,
        dt_utc.day,
        h
    )


def grados_a_signo(lon):
    idx = int(lon / 30)
    return SIGNOS[idx % 12], lon - idx * 30


def grado_a_dms(grado):
    d = int(grado)
    m = int(round((grado - d) * 60))

    if m == 60:
        d += 1
        m = 0

    return f"{d}°{m:02d}'"


def signos_en_cuspides(cuspides):
    return [
        grados_a_signo(cuspide)[0]
        for cuspide in cuspides
    ]


def signos_duplicados(cuspides):
    """
    Devuelve los signos que aparecen en dos cúspides
    indicando en qué casas aparecen.
    """

    signos = signos_en_cuspides(cuspides)

    resultado = {}

    contador = Counter(signos)

    for signo, veces in contador.items():

        if veces == 2:

            casas = [
                i + 1
                for i, s in enumerate(signos)
                if s == signo
            ]

            resultado[signo] = casas

    return resultado


def signos_interceptados(cuspides):
    """
    Devuelve los signos que no aparecen
    en ninguna cúspide.
    """

    presentes = set(signos_en_cuspides(cuspides))

    resultado = {}

    for signo in SIGNOS:

        if signo not in presentes:

            resultado[signo] = None

    return resultado



def siguiente_signo(signo):

    idx = SIGNOS.index(signo)

    return SIGNOS[(idx + 1) % 12]



def signo_siguiente(signo, pasos):

    idx = SIGNOS.index(signo)

    return SIGNOS[(idx + pasos) % 12]


def signos_contenidos(cuspides):
    """
    Devuelve únicamente los signos completamente contenidos
    dentro de una casa.

    Un signo está contenido cuando sus 30 grados completos
    quedan entre la cúspide inicial y la cúspide siguiente.
    """

    resultado = {
        casa: []
        for casa in range(1, 13)
    }

    for casa in range(12):

        lon_inicio = cuspides[casa] % 360
        lon_fin = cuspides[(casa + 1) % 12] % 360

        if lon_fin <= lon_inicio:
            lon_fin += 360

        for indice_signo, signo in enumerate(SIGNOS):

            inicio_signo = indice_signo * 30.0
            fin_signo = inicio_signo + 30.0

            # Ajustamos el signo al mismo ciclo zodiacal
            # que el intervalo de la casa.
            while fin_signo <= lon_inicio:
                inicio_signo += 360
                fin_signo += 360

            completamente_contenido = (
                inicio_signo >= lon_inicio + 1e-7
                and fin_signo <= lon_fin - 1e-7
            )

            if completamente_contenido:
                resultado[casa + 1].append(signo)

    return resultado


def casas_interceptadas(cuspides):

    contenidos = signos_contenidos(cuspides)

    resultado = {}

    for casa, signos in contenidos.items():

        for signo in signos:

            resultado[signo] = casa

    return resultado


def calcular_arquitectura_casas(cuspides):

    return {

        "signos_cuspides":
            signos_en_cuspides(cuspides),

        "signos_duplicados":
            signos_duplicados(cuspides),

        "contenidos":
            signos_contenidos(cuspides),

        "signos_interceptados":
            casas_interceptadas(cuspides),

        "casas_anareticas":
            casas_anareticas(cuspides),

    }



def bloque_singularidades_arquitectura(
    carta,
    estilos,
):
    bloque_interceptados = bloque_signos_interceptados(
        carta,
        estilos,
    )

    bloque_duplicados = bloque_signos_duplicados(
        carta,
        estilos,
    )

    bloque_anareticas = bloque_casas_anareticas(
        carta,
        estilos,
    )

    bloque_integracion = bloque_integracion_singularidades(
        carta,
        estilos,
    )

    if (
        not bloque_interceptados
        and not bloque_duplicados
        and not bloque_anareticas
        and not bloque_integracion
    ):
        return []

    elementos = [
        Paragraph(
            "Las singularidades de tu arquitectura",
            estilos["subtitulo"],
        ),

        Paragraph(
            (
                "Además de la estructura general de la carta, existen algunas "
                "particularidades que hacen que cada arquitectura sea única. "
                "No aparecen en todas las cartas y, cuando están presentes, "
                "aportan matices importantes sobre la forma en que determinadas "
                "funciones psicológicas se desarrollan a lo largo de la vida."
            ),
            estilos["cuerpo"],
        ),
    ]

    elementos += bloque_interceptados
    elementos += bloque_duplicados
    elementos += bloque_anareticas
    elementos += bloque_integracion

    # Próximamente:
    # elementos += bloque_concentraciones(carta, estilos)
    # elementos += bloque_simetrias(carta, estilos)

    return elementos


def bloque_signos_interceptados(
    carta,
    estilos,
):
    arquitectura = carta["arquitectura_casas"]

    signos_interceptados = arquitectura.get(
        "signos_interceptados",
        {},
    )

    if not signos_interceptados:
        return []

    elementos = [
        Paragraph(
            "Signos interceptados",
            estilos["subtitulo2"],
        ),

        Paragraph(
            (
                "Cuando un signo queda completamente contenido dentro de una casa, "
                "su signo opuesto también queda interceptado en la casa opuesta. "
                "Por eso esta configuración no se interpreta como dos casos "
                "independientes, sino como un eje cuyos dos polos necesitan encontrar "
                "una vía más consciente de expresión. A continuación se desarrolla "
                "cada signo por separado para comprender cómo se manifiesta cada parte "
                "de ese eje."
            ),
            estilos["cuerpo"],
        ),

    ]


    for signo, casa in signos_interceptados.items():
        elementos.append(
            Paragraph(
                signo,
                estilos["subtitulo3"],
            )
        )


        elementos.append(
            Paragraph(
                (
                    f"{signo} está interceptado "
                    f"en la Casa {casa}: "
                    f"{CASA_LABEL[casa]}."
                ),
                estilos["cuerpo"],
            )
        )


        texto = INTERCEPTACION_SIGNO[signo]

        elementos += _parrafos_reportlab(
            texto,
            estilos["cuerpo"],
        )


    return elementos


def bloque_signos_duplicados(
    carta,
    estilos,
):
    arquitectura = carta[
        "arquitectura_casas"
    ]


    signos_duplicados = arquitectura.get(
        "signos_duplicados",
        {},
    )

    if not signos_duplicados:
        return []

    elementos = [
        Paragraph(
            "Signos duplicados",
            estilos["subtitulo2"],
        ),

        Paragraph(
            (
                "Cuando un mismo signo aparece en dos cúspides consecutivas, "
                "su signo opuesto también ocupa dos cúspides consecutivas en el lado "
                "opuesto de la rueda. Por eso esta configuración no se interpreta como "
                "dos duplicaciones independientes, sino como un eje que conecta de forma "
                "simétrica varios ámbitos de la carta. Cada signo se desarrolla a "
                "continuación por separado para comprender cómo organiza las dos casas "
                "que comparten su misma cualidad."
            ),
            estilos["cuerpo"],
        ),

    ]
    

    for signo, casas in signos_duplicados.items():

        elementos.append(
            Paragraph(
                signo,
                estilos["subtitulo3"],
            )
        )


        if len(casas) >= 2:
            casa_1 = casas[0]
            casa_2 = casas[1]

            elementos.append(
                Paragraph(
                    (
                        f"{signo} aparece en las cúspides de las "
                        f"casas {casa_1} y {casa_2}."
                    ),
                    estilos["cuerpo"],
                )
            )

        texto = SIGNO_DUPLICADO[signo]

        elementos += _parrafos_reportlab(
            texto,
            estilos["cuerpo"],
        )

        if len(casas) >= 2:
            casa_1 = casas[0]
            casa_2 = casas[1]


            elementos.append(
                Paragraph(
                    texto_conexion_casas(
                        casa_1,
                        casa_2,
                    ),
                    estilos["cuerpo"],
                )
            )

    return elementos


def texto_conexion_casas(
    casa_1,
    casa_2,
):
    area_1 = CASA_LABEL.get(
        casa_1,
        f"Casa {casa_1}",
    )

    area_2 = CASA_LABEL.get(
        casa_2,
        f"Casa {casa_2}",
    )

    return (
        f"En tu carta, esta repetición conecta "
        f"<b>{area_1.lower()}</b> con "
        f"<b>{area_2.lower()}</b>. "
        f"Ambas áreas comparten una misma forma de organizar "
        f"la vida, por lo que lo que sucede en una puede "
        f"repercutir directamente en la otra. El desarrollo de "
        f"una de ellas puede convertirse también en una vía para "
        f"comprender y fortalecer la otra."
    )


def bloque_casas_anareticas(
    carta,
    estilos,
):
    arquitectura = carta[
        "arquitectura_casas"
    ]

    casas_anareticas = arquitectura.get(
        "casas_anareticas",
        {},
    )

    if not casas_anareticas:
        return []

    elementos = [
        Paragraph(
            "Cúspides en grado anarético",
            estilos["subtitulo2"],
        ),

        Paragraph(
            (
                "Algunas cúspides pueden encontrarse en el último grado "
                "de un signo. El grado 29 señala una zona de culminación: "
                "la cualidad del signo necesita desarrollarse con especial "
                "consciencia antes de dar paso al signo siguiente. Cuando "
                "aparece en la cúspide de una casa, este matiz se expresa "
                "en el ámbito de vida representado por ella. "
                "Al tratarse de una estructura simétrica, esta condición "
                "también estará presente en la cúspide opuesta, en el mismo "
                "grado del signo contrario. Por eso se interpreta como una "
                "condición del eje, aunque su expresión adquiera matices "
                "diferentes en cada una de las dos casas."
            ),
            estilos["cuerpo"],
        ),

    ]

    for numero_casa, datos in casas_anareticas.items():

        signo = datos[
            "signo"
        ]

        grado = datos[
            "grado"
        ]

        grados_enteros = int(
            grado
        )

        minutos = int(
            round(
                (grado - grados_enteros) * 60
            )
        )

        # Evita mostrar 29°60'
        if minutos == 60:
            grados_enteros += 1
            minutos = 0

        elementos.append(
            Paragraph(
                (
                    f"Casa {numero_casa} · "
                    f"{grados_enteros}°{minutos:02d}' "
                    f"de {signo}"
                ),
                estilos["subtitulo3"],
            )
        )

        elementos.append(
            Paragraph(
                CASA_LABEL[numero_casa],
                estilos["estilo_frase_final"],
            )
        )

        texto_anaretico = ANARETICO_SIGNO[
            signo
        ]

        elementos += _parrafos_reportlab(
            texto_anaretico,
            estilos["cuerpo"],
        )

        texto_casa_anaretica = ANARETICO_CASA[
            numero_casa
        ]

        elementos += _parrafos_reportlab(
            texto_casa_anaretica,
            estilos["cuerpo"],
        )

    return elementos


def bloque_integracion_singularidades(
    carta,
    estilos,
):
    arquitectura = carta[
        "arquitectura_casas"
    ]

    interceptados = arquitectura.get(
        "signos_interceptados",
        {},
    )

    duplicados = arquitectura.get(
        "signos_duplicados",
        {},
    )

    anareticas = arquitectura.get(
        "casas_anareticas",
        {},
    )

    if not interceptados and not duplicados and not anareticas:
        return []

    if (
        interceptados
        and duplicados
        and anareticas
    ):
        texto_apertura = (
            "En tu carta aparecen varias particularidades estructurales que se "
            "relacionan entre sí. Leídas en conjunto, permiten comprender con mayor "
            "profundidad cómo se distribuyen determinadas funciones entre las casas "
            "y qué procesos de maduración adquieren un peso especial."
        )

    elif (
        sum([
            bool(interceptados),
            bool(duplicados),
            bool(anareticas),
        ]) >= 2
    ):
        texto_apertura = (
            "En tu carta aparecen distintas particularidades estructurales que conviene "
            "leer de manera relacionada. Más que funcionar como elementos aislados, "
            "introducen matices específicos en la forma en que algunas áreas de experiencia "
            "se organizan y se desarrollan."
        )

    else:
        texto_apertura = (
            "En tu carta aparece una particularidad estructural que introduce un matiz "
            "específico en la forma en que determinadas áreas de experiencia se organizan "
            "y evolucionan."
        )

    elementos = [
        Paragraph(
            "Integración de las singularidades",
            estilos["subtitulo2"],
        ),

        Paragraph(
            texto_apertura,
            estilos["cuerpo"],
        ),
    ]

    # ─────────────────────────────
    # EJES ESTRUCTURALES
    # ─────────────────────────────

    eje_interceptado = obtener_eje_interceptado(
        interceptados
    )

    eje_duplicado = obtener_eje_duplicado(
        duplicados
    )

    # ─────────────────────────────
    # EJE ANARÉTICO
    # ─────────────────────────────

    eje_anaretico = obtener_eje_anaretico(
        anareticas
    )

    eje_anaretico_coincide_duplicado = False

    if eje_anaretico and eje_duplicado:
        signos_anareticos = set(
            eje_anaretico["signos"]
        )

        signos_duplicados = set(
            eje_duplicado["signos"]
        )

        casas_anareticas = set(
            eje_anaretico["casas"]
        )

        casas_duplicadas = {
            casa
            for grupo_casas in eje_duplicado["casas"]
            for casa in grupo_casas
        }

        if (
            signos_anareticos == signos_duplicados
            and casas_anareticas.issubset(
                casas_duplicadas
            )
        ):
            eje_anaretico_coincide_duplicado = True

    if (
        eje_anaretico
        and eje_anaretico_coincide_duplicado
    ):
        signo_1, signo_2 = eje_anaretico[
            "signos"
        ]

        casa_1, casa_2 = eje_anaretico[
            "casas"
        ]

        grado_1 = eje_anaretico[
            "grado"
        ]

        grados_enteros = int(
            grado_1
        )

        minutos = int(
            round(
                (grado_1 - grados_enteros) * 60
            )
        )

        if minutos == 60:
            grados_enteros += 1
            minutos = 0

        texto_coincidencia = (
            f"En esta configuración aparece además una particularidad adicional: "
            f"la cúspide de la Casa {casa_1} se encuentra en "
            f"{grados_enteros}°{minutos:02d}' de {signo_1} y su cúspide opuesta, "
            f"la de la Casa {casa_2}, en el mismo grado de {signo_2}. "
            f"Al tratarse de cúspides opuestas, no son dos grados anaréticos "
            f"independientes, sino una misma condición estructural del eje "
            f"{signo_1}–{signo_2}. Esto añade un matiz de especial maduración "
            f"a los dos extremos de esta relación."
        )


        elementos.append(
            Paragraph(
                texto_coincidencia,
                estilos["cuerpo"],
            )
        )


    if (
        eje_anaretico
        and not eje_anaretico_coincide_duplicado
    ):
        signo_1, signo_2 = eje_anaretico[
            "signos"
        ]

        casa_1, casa_2 = eje_anaretico[
            "casas"
        ]

        grado_1 = eje_anaretico[
            "grado"
        ]

        grados_enteros = int(
            grado_1
        )

        minutos = int(
            round(
                (grado_1 - grados_enteros) * 60
            )
        )

        if minutos == 60:
            grados_enteros += 1
            minutos = 0

        texto_anaretico_independiente = (
            f"El eje formado por las Casas {casa_1}–{casa_2} presenta además "
            f"una condición anarética: la cúspide de la Casa {casa_1} se encuentra "
            f"en {grados_enteros}°{minutos:02d}' de {signo_1} y la cúspide opuesta "
            f"en el mismo grado de {signo_2}. Esta particularidad no coincide con "
            f"el eje duplicado, por lo que introduce un proceso de maduración "
            f"específico en la relación entre estas dos áreas de experiencia."
        )


        elementos.append(
            Paragraph(
                texto_anaretico_independiente,
                estilos["cuerpo"],
            )
        )



    # ─────────────────────────────
    # RELACIÓN INTERCEPTADO–DUPLICADO
    # ─────────────────────────────

    if eje_interceptado and eje_duplicado:
        signo_int_1, signo_int_2 = eje_interceptado[
            "signos"
        ]

        casa_int_1, casa_int_2 = eje_interceptado[
            "casas"
        ]

        signo_dup_1, signo_dup_2 = eje_duplicado[
            "signos"
        ]

        texto_relacion_ejes = (
            f"El eje interceptado {signo_int_1}–{signo_int_2} "
            f"y el eje duplicado {signo_dup_1}–{signo_dup_2} "
            f"forman parte de una misma distribución de las casas. "
            f"La interceptación en las Casas {casa_int_1}–{casa_int_2} "
            f"hace que ambos signos queden completamente contenidos dentro de "
            f"esas áreas, mientras que {signo_dup_1} y {signo_dup_2} ocupan "
            f"dos cúspides consecutivas en los sectores opuestos de la rueda. "
            f"No son fenómenos independientes, sino dos expresiones complementarias "
            f"de una misma configuración estructural."
        )


        elementos.append(
            Paragraph(
                texto_relacion_ejes,
                estilos["cuerpo"],
            )
        )

    # ─────────────────────────────
    # CIERRE
    # ─────────────────────────────

    particularidades_presentes = []

    if interceptados:
        particularidades_presentes.append(
            "la interceptación"
        )

    if duplicados:
        particularidades_presentes.append(
            "la duplicación"
        )

    if anareticas:
        particularidades_presentes.append(
            "el grado anarético"
        )

    if len(particularidades_presentes) == 1:
        texto_particularidades = (
            particularidades_presentes[0]
        )

    elif len(particularidades_presentes) == 2:
        texto_particularidades = (
            particularidades_presentes[0]
            + " y "
            + particularidades_presentes[1]
        )

    else:
        texto_particularidades = (
            ", ".join(
                particularidades_presentes[:-1]
            )
            + " y "
            + particularidades_presentes[-1]
        )

    texto_cierre = (
        "Leída en conjunto, esta arquitectura muestra que algunas funciones necesitan "
        "más tiempo y consciencia para encontrar una vía propia de expresión, mientras "
        "otras generan continuidad entre áreas que se desarrollan de manera relacionada. "
        f"En esta carta, {texto_particularidades} "
        "forma parte de una organización interna que adquiere sentido al observarse "
        "dentro del conjunto. La clave no está en corregir estas particularidades, sino "
        "en comprender qué tipo de maduración introducen y cómo participan en la "
        "arquitectura completa de la carta."
    )


    elementos.append(
        Paragraph(
            texto_cierre,
            estilos["cuerpo"],
        )
    )

    return elementos



# ──────────────────────────────────────────────────────────────
# ARQUITECTURA DE LOS EJES
# ──────────────────────────────────────────────────────────────
def calcular_arquitectura_ejes(cuspides):
    """
    Devuelve la arquitectura estructural de los ejes de la carta.

    Incluye:

    - Los cuatro ángulos.
    - Los ejes ASC–DSC y MC–IC.
    - La distribución de cuadrantes.
    - La distribución de hemisferios.

    No realiza interpretaciones; únicamente organiza la
    estructura geométrica de la carta.
    """

    asc = cuspides[0]
    ic = cuspides[3]
    dsc = cuspides[6]
    mc = cuspides[9]

    return {

        "angulos": {
            "asc": asc,
            "dsc": dsc,
            "mc": mc,
            "ic": ic,
        },

        "ejes": {

            "horizontal": {
                "inicio": asc,
                "fin": dsc,
            },

            "vertical": {
                "inicio": mc,
                "fin": ic,
            },

        },

        "cuadrantes": {

            "I": {
                "casas": (1, 2, 3),
            },

            "II": {
                "casas": (4, 5, 6),
            },

            "III": {
                "casas": (7, 8, 9),
            },

            "IV": {
                "casas": (10, 11, 12),
            },

        },

        "hemisferios": {

            "oriental": {
                "casas": (10, 11, 12, 1, 2, 3),
            },

            "occidental": {
                "casas": (4, 5, 6, 7, 8, 9),
            },

            "superior": {
                "casas": (7, 8, 9, 10, 11, 12),
            },

            "inferior": {
                "casas": (1, 2, 3, 4, 5, 6),
            },

        },

    }



def calcular_carta(
    anio,
    mes,
    dia,
    hora,
    minuto,
    lat,
    lon,
    tz_name
):
    ephe_path = os.path.join(BASE_DIR, "ephe")
    swe.set_ephe_path(ephe_path)

    flags = swe.FLG_SPEED
    jd = fecha_a_jd(
        anio,
        mes,
        dia,
        hora,
        minuto,
        tz_name
    )

    planetas = {}

    for pid, nombre, simbolo in PLANETAS_IDS:
        pos, _ = swe.calc_ut(jd, pid, flags)
        signo, grado = grados_a_signo(pos[0])

        planetas[nombre] = {
            "simbolo": simbolo,
            "lon": pos[0],
            "signo": signo,
            "grado": grado,
            "retrogrado": pos[3] < 0,
        }

    try:
        pos_ch, _ = swe.calc_ut(
            jd,
            CHIRON_ID,
            flags
        )

    except Exception as error:
        raise RuntimeError(
            f"No se pudo calcular Quirón con precisión: {error}"
        ) from error

    signo_ch, grado_ch = grados_a_signo(pos_ch[0])

    planetas["Quirón"] = {
        "simbolo": "⚷",
        "lon": pos_ch[0],
        "signo": signo_ch,
        "grado": grado_ch,
        "retrogrado": pos_ch[3] < 0,
    }

    pos_li, _ = swe.calc_ut(
        jd,
        LILITH_ID,
        flags
    )

    signo_li, grado_li = grados_a_signo(pos_li[0])

    planetas["Lilith"] = {
        "simbolo": "⚸",
        "lon": pos_li[0],
        "signo": signo_li,
        "grado": grado_li,
        "retrogrado": pos_li[3] < 0,
    }

    pos_nn, _ = swe.calc_ut(
        jd,
        swe.TRUE_NODE,
        flags
    )

    signo_nn, grado_nn = grados_a_signo(pos_nn[0])

    lon_ns = (pos_nn[0] + 180) % 360
    signo_ns, grado_ns = grados_a_signo(lon_ns)

    planetas["Nodo Norte"] = {
        "simbolo": "☊",
        "lon": pos_nn[0],
        "signo": signo_nn,
        "grado": grado_nn,
        "retrogrado": pos_nn[3] < 0,
    }

    planetas["Nodo Sur"] = {
        "simbolo": "☋",
        "lon": lon_ns,
        "signo": signo_ns,
        "grado": grado_ns,
        "retrogrado": pos_nn[3] < 0,
    }

    cuspides, ascmc = swe.houses(
        jd,
        lat,
        lon,
        b"P"
    )

    arquitectura_casas = calcular_arquitectura_casas(cuspides)
    arquitectura_ejes = calcular_arquitectura_ejes(cuspides)

    asc_lon = ascmc[0]
    mc_lon = ascmc[1]

    signo_asc, grado_asc = grados_a_signo(asc_lon)
    signo_mc, grado_mc = grados_a_signo(mc_lon)

    def casa_de(p_lon):
        for i in range(12):
            c_ini = cuspides[i]
            c_fin = cuspides[(i + 1) % 12]

            if c_ini <= c_fin:
                if c_ini <= p_lon < c_fin:
                    return i + 1

            elif p_lon >= c_ini or p_lon < c_fin:
                return i + 1

        return 12

    for objeto in planetas.values():
        objeto["casa"] = casa_de(objeto["lon"])

    return {
        "planetas": planetas,
        "cuspides": list(cuspides),
        "arquitectura_casas": arquitectura_casas,
        "arquitectura_ejes": arquitectura_ejes,
        "asc": {
            "lon": asc_lon,
            "signo": signo_asc,
            "grado": grado_asc,
        },
        "mc": {
            "lon": mc_lon,
            "signo": signo_mc,
            "grado": grado_mc,
        },
        "jd": jd,
    }



def signo_cuspide_casa(cuspides, num_casa):
    lon = cuspides[num_casa - 1]
    signo, _ = grados_a_signo(lon)
    return signo


def es_anaretico(grado):
    return grado >= 29



def casas_anareticas(cuspides):
    resultado = {}

    for i, lon in enumerate(cuspides):
        signo, grado = grados_a_signo(lon)

        if grado >= 29:
            resultado[i + 1] = {
                "signo": signo,
                "grado": grado,
            }

    return resultado


# ─── CONSTRUCCIÓN DE LA INTERPRETACIÓN ─────────────────────────

def construir_cuspides(carta):
    """
    Construye las interpretaciones correspondientes
    a las doce cúspides de la carta.
    """

    bloques = []

    cuspides = carta["cuspides"]

    for casa in range(1, 13):

        signo = signo_cuspide_casa(
            cuspides,
            casa
        )

        bloques.append({

            "tipo": "cuspide",

            "casa": casa,

            "signo": signo,
     
            "titulo": f"Casa {casa} en {signo}",

            "texto": TEXTOS_CASAS[casa][signo],

        })

    return bloques



def construir_signos_interceptados(carta):

    bloques = []

    interceptados = carta["arquitectura_casas"]["signos_interceptados"]

    for signo, casa in interceptados.items():

        bloques.append({

            "tipo": "interceptado",

            "casa": casa,

            "signo": signo,

            "titulo": f"{signo} interceptado en Casa {casa}",

            "texto": INTERCEPTACION_SIGNO[signo],

        })

    return bloques


def construir_signos_duplicados(carta):

    bloques = []

    duplicados = carta["arquitectura_casas"]["signos_duplicados"]

    for signo, casas in duplicados.items():

        casa1, casa2 = casas

        bloques.append({

            "tipo": "duplicado",

            "signo": signo,

            "casas": casas,

            "titulo": (
                f"{signo} duplicado "
                f"entre Casa {casa1} y Casa {casa2}"
            ),

            "texto": SIGNO_DUPLICADO[signo],

        })

    return bloques


def construir_interpretacion_casas(carta):
    """
    Construye todas las interpretaciones del módulo
    Casas por Signo.
    """

    return {

        "cuspides":
            construir_cuspides(carta),

        "interceptados":
            construir_signos_interceptados(carta),

        "duplicados":
            construir_signos_duplicados(carta),

    }



# ─── RUEDA: ARQUITECTURA DE LAS CASAS ───────────────────────────

def dibujar_arquitectura_casas(
    carta,
    archivo_salida,
):

    """
    Dibuja la rueda astrológica para el módulo
    Casas por Signo.

    Representa:

    - signos zodiacales
    - cúspides
    - ejes principales
    - planetas
    - arquitectura de las casas
    """

    planetas = carta["planetas"]
    cuspides = carta["cuspides"]
    asc_lon = carta["asc"]["lon"]

    arquitectura_casas = carta["arquitectura_casas"]

    signos_contenidos_rueda = {
        signo
        for signos in arquitectura_casas["contenidos"].values()
        for signo in signos
    }

    signos_interceptados_rueda = set(
        arquitectura_casas["signos_interceptados"].keys()
    )

    casas_duplicadas_rueda = {
        casa
        for casas in arquitectura_casas["signos_duplicados"].values()
        for casa in casas
    }


    puntos = {
        nombre: objeto
        for nombre, objeto in planetas.items()
        if objeto
    }


    def lon_a_angulo(lon):
        return math.radians(
            180 + (lon - asc_lon)
        )

    R_EXT = 1.35
    R_SIGN_IN = 1.05
    R_CASA_OUT = 1.02
    R_CASA_IN = 0.65
    R_PLANETA = 0.82

    R_MARCA_CONTENIDO = 1.10
    R_MARCA_INTERCEPTADO = 1.15
    R_MARCA_DUPLICADO = 0.98


    fig, ax = plt.subplots(
        1,
        1,
        figsize=(10, 10),
    )

    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(-1.58, 1.58)
    ax.set_ylim(-1.58, 1.58)

    # Anillo de signos
    for i, signo in enumerate(SIGNOS):
        elem = ELEMENTO_SIGNO[signo]
        color = COLORES_ELEMENTO[elem]

        ang_ini = lon_a_angulo(i * 30)
        ang_fin = lon_a_angulo((i + 1) * 30)

        theta = np.linspace(
            ang_ini,
            ang_fin,
            50,
        )

        xs = (
            [
                math.cos(a) * R_EXT
                for a in theta
            ]
            + [
                math.cos(a) * R_SIGN_IN
                for a in reversed(theta)
            ]
        )

        ys = (
            [
                math.sin(a) * R_EXT
                for a in theta
            ]
            + [
                math.sin(a) * R_SIGN_IN
                for a in reversed(theta)
            ]
        )

        ax.fill(
            xs,
            ys,
            color=color,
            alpha=0.20,
            zorder=1,
        )

    # Círculos principales
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

    # Separadores de signos
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
            color="#666",
            linewidth=0.7,
            zorder=2,
        )

    # Símbolos zodiacales
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
            fontsize=16,
            color=COLORES_ELEMENTO[elem],
            fontweight="bold",
            alpha=0.60,
            zorder=5,
        )


        # Marca de signo interceptado
        if signo in signos_interceptados_rueda:
            ax.scatter(
                math.cos(ang_mid) * R_MARCA_INTERCEPTADO,
                math.sin(ang_mid) * R_MARCA_INTERCEPTADO,
                s=24,
                marker="D",
                color="#7A1F1F",
                edgecolors="none",
                zorder=8,
            )


    # Líneas de las cúspides y números de las casas
    for i, cusp in enumerate(cuspides):

        ang = lon_a_angulo(cusp)

        es_angular = i in (0, 3, 6, 9)

        ax.plot(
            [
                math.cos(ang) * R_CASA_IN,
                math.cos(ang) * R_CASA_OUT,
            ],
            [
                math.sin(ang) * R_CASA_IN,
                math.sin(ang) * R_CASA_OUT,
            ],
            color=(
                "#111111"
                if es_angular
                else "#AAAAAA"
            ),
            linewidth=(
                1.8
                if es_angular
                else 0.65
            ),
            zorder=3,
        )

        # Marca doble para las cúspides cuyo signo está duplicado
        if i + 1 in casas_duplicadas_rueda:

            radio_centro = R_MARCA_DUPLICADO
            separacion = 0.035
            semilargo = 0.035

            perpendicular_x = -math.sin(ang)
            perpendicular_y = math.cos(ang)

            centro_1_x = (
                math.cos(ang)
                * (radio_centro - separacion)
            )
            centro_1_y = (
                math.sin(ang)
                * (radio_centro - separacion)
            )

            ax.plot(
                [
                    centro_1_x
                    - perpendicular_x * semilargo,
                    centro_1_x
                    + perpendicular_x * semilargo,
                ],
                [
                    centro_1_y
                    - perpendicular_y * semilargo,
                    centro_1_y
                    + perpendicular_y * semilargo,
                ],
                color="#6B6256",
                linewidth=1.4,
                zorder=7,
            )

            centro_2_x = (
                math.cos(ang)
                * (radio_centro + separacion)
            )
            centro_2_y = (
                math.sin(ang)
                * (radio_centro + separacion)
            )
  
            ax.plot(
                [
                    centro_2_x
                    - perpendicular_x * semilargo,
                    centro_2_x
                    + perpendicular_x * semilargo,
                ],
                [
                    centro_2_y
                    - perpendicular_y * semilargo,
                    centro_2_y
                    + perpendicular_y * semilargo,
                ],
                color="#6B6256",
                linewidth=1.4,
                zorder=7,
            )

        # Número de la casa situado en el centro real del sector
        cuspide_inicio = cuspides[i] % 360
        cuspide_fin = cuspides[(i + 1) % 12] % 360
 
        if cuspide_fin <= cuspide_inicio:
            cuspide_fin += 360
 
        lon_centro_casa = (
            cuspide_inicio
            + (cuspide_fin - cuspide_inicio) / 2
        ) % 360

        ang_num = lon_a_angulo(
            lon_centro_casa
        )

        r_num = R_CASA_IN + 0.08

        ax.text(
            math.cos(ang_num) * r_num,
            math.sin(ang_num) * r_num,
            str(i + 1),
            ha="center",
            va="center",
            fontsize=8,
            color="#444",
            fontweight=(
                "bold"
                if i in (0, 3, 6, 9)
                else "normal"
            ),
            zorder=4,
        )
 

    # Distribución radial para evitar solapamientos
    lones_usados = []
    radios = {}

    # Ordenamos por longitud para que la distribución
    # sea estable y no dependa del orden del conjunto.
    puntos_ordenados = sorted(
        puntos.items(),
        key=lambda item: item[1]["lon"],
    )

    for nombre, p in puntos_ordenados:
        lon = p["lon"]
        radio = R_PLANETA

        for (
            lon_previa,
            radio_previo,
        ) in lones_usados:
            distancia = abs(
                lon - lon_previa
            ) % 360

            if distancia > 180:
                distancia = (
                    360 - distancia
                )

            if distancia < 8:
                if (
                    radio_previo - 0.10
                    > 0.45
                ):
                    radio = (
                        radio_previo - 0.10
                    )
                else:
                    radio = (
                        radio_previo + 0.10
                    )

                break

        lones_usados.append(
            (lon, radio)
        )

        radios[nombre] = radio

    # Símbolos planetarios
    for nombre, p in puntos_ordenados:
        ang = lon_a_angulo(
            p["lon"]
        )

        r = radios[nombre]

        color = COLORES_PLANETA.get(
            nombre,
            "#333",
        )

        simbolo = p["simbolo"]


        fs = 16

        ax.text(
            math.cos(ang) * r,
            math.sin(ang) * r,
            simbolo,
            ha="center",
            va="center",
            fontsize=fs,
            color=color,
            fontweight="bold",
            zorder=6,
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
            linewidth=0.9,
            alpha=0.70,
            zorder=3,
        )

    # Ejes principales
    for etq, lon_pt, bold, size in [
        (
            "AC",
            carta["asc"]["lon"],
            True,
            13,
        ),
        (
            "DC",
            (
                carta["asc"]["lon"]
                + 180
            ) % 360,
            False,
            10,
        ),
        (
            "MC",
            carta["mc"]["lon"],
            False,
            10,
        ),
        (
            "IC",
            (
                carta["mc"]["lon"]
                + 180
            ) % 360,
            False,
            10,
        ),
    ]:
        ang = lon_a_angulo(
            lon_pt
        )

        fw = (
            "bold"
            if bold
            else "normal"
        )

        col = (
            "#111"
            if bold
            else "#555"
        )

        ax.text(
            math.cos(ang)
            * (R_EXT + 0.12),
            math.sin(ang)
            * (R_EXT + 0.12),
            etq,
            ha="center",
            va="center",
            fontsize=size,
            fontweight=fw,
            color=col,
            zorder=7,
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



def obtener_eje_interceptado(
    interceptados,
):
    if not interceptados:
        return None

    for signo_1, casa_1 in interceptados.items():

        signo_2 = signo_opuesto(
            signo_1
        )

        casa_2 = casa_opuesta(
            casa_1
        )

        if (
            signo_2 in interceptados
            and interceptados[signo_2] == casa_2
        ):
            return {
                "signos": (
                    signo_1,
                    signo_2,
                ),
                "casas": (
                    casa_1,
                    casa_2,
                ),
            }

    return None

def signo_opuesto(signo):
    indice = SIGNOS.index(signo)
    return SIGNOS[(indice + 6) % 12]


def casa_opuesta(casa):
    return ((casa + 5) % 12) + 1



def obtener_eje_duplicado(
    duplicados,
):
    if not duplicados:
        return None

    for signo_1, casas_1 in duplicados.items():

        signo_2 = signo_opuesto(
            signo_1
        )

        if signo_2 not in duplicados:
            continue

        casas_2 = duplicados[
            signo_2
        ]

        if len(casas_1) < 2 or len(casas_2) < 2:
            continue

        casas_opuestas_1 = {
            casa_opuesta(casa)
            for casa in casas_1
        }

        if casas_opuestas_1 == set(casas_2):
            return {
                "signos": (
                    signo_1,
                    signo_2,
                ),
                "casas": (
                    casas_1,
                    casas_2,
                ),
            }

    return None


def obtener_eje_anaretico(
    anareticas,
):
    if not anareticas:
        return None

    for casa_1, datos_1 in anareticas.items():

        casa_2 = casa_opuesta(
            casa_1
        )

        if casa_2 not in anareticas:
            continue

        datos_2 = anareticas[
            casa_2
        ]

        signo_1 = datos_1[
            "signo"
        ]

        signo_2 = datos_2[
            "signo"
        ]

        if signo_2 != signo_opuesto(
            signo_1
        ):
            continue

        grado_1 = datos_1[
            "grado"
        ]

        grado_2 = datos_2[
            "grado"
        ]

        if abs(
            grado_1 - grado_2
        ) > 0.01:
            continue

        return {
            "signos": (
                signo_1,
                signo_2,
            ),
            "casas": (
                casa_1,
                casa_2,
            ),
            "grado": grado_1,
        }

    return None


def obtener_arquitectura_angular(
    carta,
):
    arquitectura = carta[
        "arquitectura_casas"
    ]

    signos_cuspides = arquitectura[
        "signos_cuspides"
    ]

    signo_asc = signos_cuspides[0]
    signo_ic = signos_cuspides[3]
    signo_dsc = signos_cuspides[6]
    signo_mc = signos_cuspides[9]

    return {
        "asc": {
            "signo": signo_asc,
            "modalidad": MODALIDAD_SIGNO[
                signo_asc
            ],
            "elemento": ELEMENTO_SIGNO[
                signo_asc
            ],
        },

        "dsc": {
            "signo": signo_dsc,
            "modalidad": MODALIDAD_SIGNO[
                signo_dsc
            ],
            "elemento": ELEMENTO_SIGNO[
                signo_dsc
            ],
        },

        "mc": {
            "signo": signo_mc,
            "modalidad": MODALIDAD_SIGNO[
                signo_mc
            ],
            "elemento": ELEMENTO_SIGNO[
                signo_mc
            ],
        },

        "ic": {
            "signo": signo_ic,
            "modalidad": MODALIDAD_SIGNO[
                signo_ic
            ],
            "elemento": ELEMENTO_SIGNO[
                signo_ic
            ],
        },
    }


def obtener_relacion_modalidades_angulares(
    carta,
):
    angular = obtener_arquitectura_angular(
        carta
    )

    modalidad_asc = angular[
        "asc"
    ]["modalidad"]

    modalidad_mc = angular[
        "mc"
    ]["modalidad"]

    clave = (
        modalidad_asc,
        modalidad_mc,
    )

    return {
        "clave": clave,
        "modalidad_asc_dsc": modalidad_asc,
        "modalidad_mc_ic": modalidad_mc,
    }


def bloque_cierre_casas_por_signo(
    estilos,
):
    elementos = [
        PageBreak(),

        Paragraph(
            "Habitar tu arquitectura",
            estilos["subtitulo"],
        ),

    ]

    elementos += _parrafos_reportlab(
        CIERRE_CASAS_POR_SIGNO,
        estilos["cuerpo"],
    )


    return elementos


# ─── GENERACIÓN PDF (REPORTLAB) ───────────────────────────────────────────────

def crear_estilos_reportlab():
    """Usa los estilos comunes de la colección cuando estilos_pdf.py está disponible."""
    if crear_estilos_pdf is not None:
        return crear_estilos_pdf()

    # Respaldo para poder ejecutar el archivo de forma independiente.
    estilos = getSampleStyleSheet()

    titulo = ParagraphStyle(
        "TituloAI",
        parent=estilos["Title"],
        fontName="Times-Bold",
        fontSize=28,
        leading=34,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1E508C"),
        spaceAfter=20,
    )

    estilo_frase_final = ParagraphStyle(
        "FraseFinal",
        parent=estilos["BodyText"],
        fontName="Times-Italic",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#666666"),
        alignment=TA_CENTER,
    )

    subtitulo = ParagraphStyle(
        "SubtituloAI",
        parent=estilos["Heading2"],
        fontName="Times-Bold",
        fontSize=18,
        leading=23,
        textColor=colors.HexColor("#8C5A00"),
        spaceBefore=18,
        spaceAfter=10,
        keepWithNext=True,
    )

    subtitulo2 = ParagraphStyle(
        "Subtitulo2AI",
        parent=estilos["Heading3"],
        fontName="Times-Bold",
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#1E508C"),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True,
    )

    subtitulo3 = ParagraphStyle(
        "Subtitulo3AI",
        parent=estilos["Heading4"],
        fontName="Times-Bold",
        fontSize=11.5,
        leading=15,
        textColor=colors.HexColor("#333333"),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True,
    )

    cuerpo = ParagraphStyle(
        "CuerpoAI",
        parent=estilos["BodyText"],
        fontName="Times-Roman",
        fontSize=11,
        leading=16,
        spaceAfter=10,
        alignment=TA_JUSTIFY,
        widowControl=1,
        allowWidows=0,
        allowOrphans=0,
    )

    centro = ParagraphStyle(
        "CentroAI",
        parent=cuerpo,
        alignment=TA_CENTER,
    )

    titulo_aspecto = ParagraphStyle(
        "TituloAspectoAI",
        parent=cuerpo,
        fontName="Times-Bold",
        textColor=colors.HexColor("#333333"),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True,
    )

    return {
        "titulo": titulo,
        "subtitulo": subtitulo,
        "subtitulo2": subtitulo2,
        "subtitulo3": subtitulo3,
        "cuerpo": cuerpo,
        "centro": centro,
        "titulo_aspecto": titulo_aspecto,
        "estilo_frase_final": estilo_frase_final,
    }


def agregar_pagina(canvas, doc):
    canvas.saveState()
    numero = canvas.getPageNumber() - 1

    if numero > 0:
        canvas.setFont("Times-Roman", 9)
        canvas.setFillColor(colors.HexColor("#777777"))
        canvas.drawRightString(
            19 * cm,
            1.2 * cm,
            str(numero),
        )

    canvas.restoreState()


def _parrafos_reportlab(texto, estilo):
    return [
        Paragraph(p.strip(), estilo)
        for p in texto.split("\n\n")
        if p.strip()
    ]


def bloque_portada_casas_por_signo(
    nombre,
    fecha_str,
    hora_str,
    ciudad,
    estilos,
):
    return [
        Spacer(
            1,
            1.7 * cm,
        ),

        Paragraph(
            "Casas por Signo",
            estilos["titulo"],
        ),

        Paragraph(
            "La arquitectura de las áreas de tu vida",
            estilos["centro"],
        ),

        Spacer(
            1,
            0.45 * cm,
        ),

        Paragraph(
            "Una lectura sobre cómo se organizan los distintos ámbitos "
            "de tu experiencia y la forma particular en que tiendes "
            "a habitarlos.",
            estilos["estilo_frase_final"],
        ),

        Spacer(
            1,
            2.2 * cm,
        ),

        Paragraph(
            nombre,
            ParagraphStyle(
                "NombrePortadaCasas",
                parent=estilos["centro"],
                fontName="Times-Roman",
                fontSize=24,
                leading=29,
                textColor=colors.HexColor("#8C5A00"),
            ),
        ),

        Spacer(
            1,
            1.15 * cm,
        ),

        Paragraph(
            f"{fecha_str} · {hora_str}",
            estilos["centro"],
        ),

        Paragraph(
            ciudad,
            estilos["centro"],
        ),

        Spacer(
            1,
            10 * cm,
        ),

        Paragraph(
            "Arquitectura Interna · Un método para sostener cuerpo, "
            "energía y vida con coherencia",
            estilos["estilo_frase_final"],
        ),

        PageBreak(),
    ]


def bloque_introduccion_angulos(
    estilos,
):
    return [
        Paragraph(
            "Los cuatro ángulos",
            estilos["subtitulo"],
        ),

        *_parrafos_reportlab(
            TEXTO_INTRO_ANGULOS,
            estilos["cuerpo"],
        ),

    ]


def bloque_eje_asc_dsc(
    carta,
    estilos,
):
    arquitectura = carta[
        "arquitectura_casas"
    ]

    signos_cuspides = arquitectura[
        "signos_cuspides"
    ]

    signo_asc = signos_cuspides[0]
    signo_dsc = signos_cuspides[6]

    texto = EJE_ASC_DSC.get(
        (
            signo_asc,
            signo_dsc,
        ),
        "",
    )

    elementos = [
        Paragraph(
            "El eje ASC–DSC",
            estilos["subtitulo"],
        ),
        Paragraph(
            f"{signo_asc} – {signo_dsc}",
            estilos["subtitulo2"],
        ),

    ]

    if texto:
        elementos += _parrafos_reportlab(
            texto,
            estilos["cuerpo"],
        )

    else:
        elementos.append(
            Paragraph(
                "Esta combinación todavía no dispone de una "
                "interpretación específica.",
                estilos["cuerpo"],
            )
        )

    return elementos


def bloque_eje_mc_ic(
    carta,
    estilos,
):
    arquitectura = carta[
        "arquitectura_casas"
    ]

    signos_cuspides = arquitectura[
        "signos_cuspides"
    ]

    signo_ic = signos_cuspides[3]
    signo_mc = signos_cuspides[9]

    texto = EJE_MC_IC.get(
        (
            signo_mc,
            signo_ic,
        ),
        "",
    )

    elementos = [
        Paragraph(
            "El eje MC–IC",
            estilos["subtitulo"],
        ),
        Paragraph(
            f"{signo_mc} – {signo_ic}",
            estilos["subtitulo2"],
        ),
    ]

    if texto:
        elementos += _parrafos_reportlab(
            texto,
            estilos["cuerpo"],
        )

    return elementos


def bloque_integracion_cuatro_angulos(
    carta,
    estilos,
):
    arquitectura = carta[
        "arquitectura_casas"
    ]

    signos_cuspides = arquitectura[
        "signos_cuspides"
    ]

    signo_asc = signos_cuspides[0]
    signo_ic = signos_cuspides[3]
    signo_dsc = signos_cuspides[6]
    signo_mc = signos_cuspides[9]

    relacion_modalidades = obtener_relacion_modalidades_angulares(
        carta
    )

    clave_modalidades = relacion_modalidades[
        "clave"
    ]

    texto_modalidades = INTEGRACION_MODALIDADES_ANGULARES.get(
        clave_modalidades,
        "",
    )

    elementos = [
        Paragraph(
            "La relación entre los cuatro ángulos",
            estilos["subtitulo"],
        ),
        Paragraph(
            (
                f"{signo_asc} – {signo_dsc} "
                f"· {signo_mc} – {signo_ic}"
            ),
            estilos["subtitulo2"],
        ),

    ]

    if texto_modalidades:
        elementos += _parrafos_reportlab(
            texto_modalidades,
            estilos["cuerpo"],
        )

    return elementos


def bloque_bienvenida_casas_por_signo(
    estilos,
):
    return [
        Paragraph(
            "Bienvenida",
            estilos["subtitulo"],
        ),

        Paragraph(
            "Una carta natal no se organiza únicamente a través de los "
            "planetas. También necesita un espacio donde cada función pueda "
            "expresarse. Ese espacio está representado por las casas.",
            estilos["cuerpo"],
        ),

        Paragraph(
            "Cada casa describe un ámbito concreto de experiencia: la "
            "identidad, los recursos, la comunicación, el hogar, la "
            "creatividad, los hábitos, los vínculos, la transformación, "
            "la búsqueda de sentido, la vocación, la comunidad o el mundo "
            "interior.",
            estilos["cuerpo"],
        ),

        Paragraph(
            "El signo situado en la cúspide de cada casa muestra la forma "
            "en que tiendes a entrar en contacto con ese territorio. Señala "
            "qué cualidades necesitas desarrollar, qué actitud aparece de "
            "manera espontánea y qué dificultades pueden surgir cuando esa "
            "energía pierde equilibrio.",
            estilos["cuerpo"],
        ),

        Paragraph(
            "Por eso, una misma casa puede vivirse de maneras muy distintas. "
            "La Casa 4 siempre habla de raíces, pertenencia y sostén, pero no "
            "se expresa igual cuando su cúspide está en Aries que cuando está "
            "en Tauro, Libra o Piscis.",
            estilos["cuerpo"],
        ),

        Paragraph(
            "Este informe recorre las doce casas de tu carta y observa cómo "
            "se organiza cada una de ellas a través del signo que ocupa su "
            "cúspide. La intención no es describir áreas aisladas, sino ayudarte "
            "a comprender la estructura completa que sostiene tu manera de "
            "habitar la vida.",
            estilos["cuerpo"],
        ),


        Paragraph(
            "Antes de empezar",
            estilos["subtitulo"],
        ),

        Paragraph(
            "Cómo leer este cuaderno",
            estilos["subtitulo2"],
        ),

        Paragraph(
            "No necesitas identificarte con cada frase ni comprenderlo todo "
            "en una primera lectura. Algunas partes describirán patrones muy "
            "visibles; otras quizá necesiten tiempo o aparezcan únicamente en "
            "determinadas etapas de tu vida.",
            estilos["cuerpo"],
        ),

        Paragraph(
            "Lee cada casa como una parte de una estructura mayor. Ningún "
            "ámbito funciona completamente separado de los demás. La identidad "
            "influye en los vínculos, los recursos condicionan la seguridad, "
            "las raíces sostienen la vocación y el mundo interior modifica la "
            "forma en que respondes a la vida.",
            estilos["cuerpo"],
        ),

        Paragraph(
            "La lectura gana profundidad cuando puedes observar no solo qué "
            "dice cada casa, sino también cómo dialoga con el resto de la carta.",
            estilos["cuerpo"],
        ),

        PageBreak(),
    ]



def bloque_tabla_resumen_casas(
    carta,
    estilos,
):
    arquitectura = carta["arquitectura_casas"]

    signos_cuspides = arquitectura[
        "signos_cuspides"
    ]

    duplicados = arquitectura.get(
        "signos_duplicados",
        {},
    )

    interceptados = arquitectura.get(
        "signos_interceptados",
        {},
    )

    anareticas = arquitectura.get(
        "casas_anareticas",
        {},
    )

    estilo_tabla_cuerpo = ParagraphStyle(
        "TablaCuerpoCasas",
        parent=estilos["cuerpo"],
        fontName="Times-Roman",
        fontSize=7.7,
        leading=9.1,
        spaceAfter=0,
        alignment=TA_LEFT,
    )

    estilo_tabla_centro = ParagraphStyle(
        "TablaCentroCasas",
        parent=estilo_tabla_cuerpo,
        alignment=TA_CENTER,
    )

    estilo_tabla_simbolo = ParagraphStyle(
        "TablaSimboloCasas",
        parent=estilo_tabla_centro,
        fontName=FUENTE_SIMBOLOS,
        fontSize=12,
        leading=13,
        textColor=colors.HexColor("#7B5526"),
        alignment=TA_CENTER,
    )

    estilo_tabla_cabecera = ParagraphStyle(
        "TablaCabeceraCasas",
        parent=estilo_tabla_cuerpo,
        fontName="Times-Bold",
        textColor=colors.HexColor("#1E508C"),
        alignment=TA_CENTER,
    )

    datos = [
        [
            Paragraph(
                "Casa",
                estilo_tabla_cabecera,
            ),
            Paragraph(
                "Área",
                estilo_tabla_cabecera,
            ),
            Paragraph(
                "Cúspide",
                estilo_tabla_cabecera,
            ),
            Paragraph(
                "Regente",
                estilo_tabla_cabecera,
            ),
            Paragraph(
                "Glifo",
                estilo_tabla_cabecera,
            ),
            Paragraph(
                "Particularidades",
                estilo_tabla_cabecera,
            ),
        ]
    ]

    for numero_casa in range(
        1,
        13,
    ):
        signo = signos_cuspides[
            numero_casa - 1
        ]

        regente = REGENTE_SIGNO[
            signo
        ]

        simbolo_regente = SIMBOLO_PLANETA.get(
            regente,
            "",
        )

        anotaciones = []

        if signo in duplicados:
            anotaciones.append(
                "Cúspide duplicada"
            )

        signos_interceptados_casa = []

        for signo_interceptado, casa in interceptados.items():
            if casa == numero_casa:
                signos_interceptados_casa.append(
                    signo_interceptado
                )

        if signos_interceptados_casa:
            cantidad = len(
                signos_interceptados_casa
            )

            termino = (
                "interceptado"
                if cantidad == 1
                else "interceptados"
            )

            anotaciones.append(
                "Contiene "
                + ", ".join(
                    signos_interceptados_casa
                )
                + f" {termino}"
            )

        if numero_casa in anareticas:
            datos_anareticos = anareticas[
                numero_casa
            ]

            grado = datos_anareticos[
                "grado"
            ]

            grados_enteros = int(grado)

            minutos = int(
                round(
                    (grado - grados_enteros) * 60
                )
            )

            if minutos == 60:
                grados_enteros += 1
                minutos = 0

            anotaciones.append(
                f"Grado anarético {grados_enteros}°{minutos:02d}'"
            )

        texto_anotaciones = (
            " · ".join(
                anotaciones
            )
            if anotaciones
            else "—"
        )

        datos.append(
            [
                Paragraph(
                    str(numero_casa),
                    estilo_tabla_centro,
                ),
                Paragraph(
                    CASA_LABEL[
                        numero_casa
                    ],
                    estilo_tabla_cuerpo,
                ),
                Paragraph(
                    signo,
                    estilo_tabla_centro,
                ),
                Paragraph(
                    regente,
                    estilo_tabla_centro,
                ),
                Paragraph(
                    simbolo_regente,
                    estilo_tabla_simbolo,
                ),
                Paragraph(
                    texto_anotaciones,
                    estilo_tabla_cuerpo,
                ),
            ]
        )

    tabla = Table(
        datos,
        colWidths=[
            1.05 * cm,
            3.35 * cm,
            2.05 * cm,
            2.0 * cm,
            1.05 * cm,
            5.6 * cm,
        ],
        repeatRows=1,
    )

    tabla.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#EFE4D2"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#7B5526"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (0, -1),
                    "CENTER",
                ),
                (
                    "ALIGN",
                    (2, 1),
                    (4, -1),
                    "CENTER",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.35,
                    colors.HexColor("#D8CCBC"),
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    3.5,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    3.5,
                ),
            ]
        )
    )

    return [
        Spacer(
            1,
            0.2 * cm,
        ),
        Paragraph(
            "Tu mapa de casas",
            estilos["subtitulo2"],
        ),
        Spacer(
            1,
            0.1 * cm,
        ),
        tabla,
    ]


def generar_casas_por_signo(
    ruta_pdf,
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
):
    estilos = crear_estilos_reportlab()

    doc = SimpleDocTemplate(
        ruta_pdf,
        pagesize=A4,
        rightMargin=2.5 * cm,
        leftMargin=2.5 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2.5 * cm,
    )

    contenido = []

    fecha_str = f"{dia:02d}/{mes:02d}/{anio}"
    hora_str = f"{hora:02d}:{minuto:02d}"


    contenido += bloque_portada_casas_por_signo(
        nombre,
        fecha_str,
        hora_str,
        ciudad,
        estilos,
    )

    contenido += bloque_bienvenida_casas_por_signo(
        estilos,
    )


    # ── RUEDA ────────────────────────────────────────────────

    contenido.append(
        Paragraph(
            "La arquitectura de tu carta",
            estilos["subtitulo"],
        )
    )

    if ruta_rueda and os.path.exists(ruta_rueda):
        imagen_rueda = Image(
            ruta_rueda,
            width=11.8 * cm,
            height=11.8 * cm,
        )

        imagen_rueda.hAlign = "CENTER"

        contenido.append(
            imagen_rueda
        )

    # Tabla resumen
    contenido += bloque_tabla_resumen_casas(
        carta,
        estilos,
    )

    contenido.append(
        PageBreak()
    )



    # ── CASAS ────────────────────────────────────────────────

    for numero_casa in range(1, 13):

        signo_cuspide = carta[
            "arquitectura_casas"
        ][
            "signos_cuspides"
        ][numero_casa - 1]

        texto_especifico = TEXTOS_CASAS[
            numero_casa
        ].get(
            signo_cuspide,
            "",
        )

        parrafos_area = _parrafos_reportlab(
            CASA_AREA[numero_casa],
            estilos["cuerpo"],
        )

        # Encabezado de la casa y presentación del área.
        # Se mantienen juntos para evitar títulos aislados.
        bloque_encabezado = [
            Paragraph(
                f"Casa {numero_casa}",
                estilos["titulo"],
            ),

            Paragraph(
                CASA_LABEL[numero_casa],
                estilos["estilo_frase_final"],
            ),

            Spacer(
                1,
                0.55 * cm,
            ),

            Paragraph(
                f"{signo_cuspide} en la cúspide",
                estilos["subtitulo"],
            ),
        ]

        bloque_encabezado += parrafos_area

        contenido.append(
            KeepTogether(
                bloque_encabezado
            )
        )

        contenido.append(
            Paragraph(
                f"Casa {numero_casa} en {signo_cuspide}",
                estilos["subtitulo2"],
            )
        )

        if texto_especifico:

            parrafos_texto = _parrafos_reportlab(
                texto_especifico,
                estilos["cuerpo"],
            )

            if len(parrafos_texto) == 1:

                contenido.append(
                    KeepTogether(
                        parrafos_texto
                    )
                )

            else:

                # Los párrafos centrales pueden distribuirse
                # normalmente entre páginas.
                contenido += parrafos_texto[:-1]

                # El último párrafo se mantiene completo para evitar
                # que una frase final quede sola en otra página.
                contenido.append(
                    KeepTogether([
                        parrafos_texto[-1],
                    ])
                )

        else:

            contenido.append(
                Paragraph(
                    "Esta combinación todavía no dispone de una "
                    "interpretación específica.",
                    estilos["cuerpo"],
                )
            )

        if numero_casa < 12:

            contenido.append(
                PageBreak()
            )


    # ── ARQUITECTURA GENERAL ─────────────────────────────────

    contenido.append(
        PageBreak()
    )

    contenido.append(
        Paragraph(
            "Arquitectura general de la carta",
            estilos["titulo"],
        )
    )

    contenido.append(
        Spacer(
            1,
            0.45 * cm,
        )
    )


    contenido += bloque_introduccion_angulos(
        estilos,
    )


    contenido += bloque_eje_asc_dsc(
        carta,
        estilos,
    )

    contenido += bloque_eje_mc_ic(
        carta,
        estilos,
    )

    contenido += bloque_integracion_cuatro_angulos(
        carta,
        estilos,
    )

    contenido += bloque_singularidades_arquitectura(
        carta,
        estilos,
    )


    # ── CIERRE ────────────────────────────────────────────────

    contenido += bloque_cierre_casas_por_signo(
        estilos,
    )

    contenido.append(
        Spacer(
            1,
            0.8 * cm,
        )
    )

    contenido.append(
        KeepTogether([
            Paragraph(
                "Arquitectura Interna",
                estilos["subtitulo2"],
            ),
            Paragraph(
                "Un método para sostener cuerpo, energía y vida con coherencia",
                estilos["cuerpo"],
            ),
        ])
    )

    doc.build(
        contenido,
        onFirstPage=agregar_pagina,
        onLaterPages=agregar_pagina,
    )


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
        "Generando informe Casas por Signo para:",
        nombre,
    )

    try:
        # ── FECHA ─────────────────────────────────────────────

        partes_fecha = fecha.split("/")

        if len(partes_fecha) != 3:
            raise ValueError(
                "La fecha debe tener el formato DD/MM/AAAA."
            )

        dia = int(partes_fecha[0])
        mes = int(partes_fecha[1])
        anio = int(partes_fecha[2])

        datetime(
            anio,
            mes,
            dia,
        )

        # ── HORA ──────────────────────────────────────────────

        partes_hora = hora.split(":")

        if len(partes_hora) != 2:
            raise ValueError(
                "La hora debe tener el formato HH:MM."
            )

        hora_num = int(partes_hora[0])
        minuto = int(partes_hora[1])

        if not 0 <= hora_num <= 23:
            raise ValueError(
                "La hora debe estar entre 0 y 23."
            )

        if not 0 <= minuto <= 59:
            raise ValueError(
                "Los minutos deben estar entre 0 y 59."
            )

        # ── GEOLOCALIZACIÓN ───────────────────────────────────

        if lat is not None and lon is not None:
            lat = float(lat)
            lon = float(lon)

            if not tz_name:
                tz_name = obtener_timezone(
                    lat,
                    lon,
                )

        else:
            lat, lon = geocodificar(
                lugar
            )

            tz_name = obtener_timezone(
                lat,
                lon,
            )

        # ── CÁLCULO DE LA CARTA ───────────────────────────────

        carta = calcular_carta(
            anio,
            mes,
            dia,
            hora_num,
            minuto,
            lat,
            lon,
            tz_name,
        )

        # ── ARCHIVOS ──────────────────────────────────────────

        nombre_f = (
            nombre
            .replace(" ", "_")
            .replace("/", "-")
            .replace("\\", "-")
        )

        ruta_base = os.path.join(
            BASE_DIR,
            nombre_f + "_Casas_por_Signo",
        )

        ruta_pdf = ruta_base + ".pdf"
        ruta_rueda = ruta_base + "_rueda.png"

        # ── RUEDA ─────────────────────────────────────────────

        dibujar_arquitectura_casas(
            carta,
            ruta_rueda,
        )

        if not os.path.exists(ruta_rueda):
            return {
                "ok": False,
                "error": "No se ha podido crear la rueda.",
            }

        # ── PDF ───────────────────────────────────────────────

        generar_casas_por_signo(
            ruta_pdf=ruta_pdf,
            carta=carta,
            nombre=nombre,
            anio=anio,
            mes=mes,
            dia=dia,
            hora=hora_num,
            minuto=minuto,
            ciudad=lugar,
            lat=lat,
            lon=lon,
            tz_name=tz_name,
            ruta_rueda=ruta_rueda,
        )

        if not os.path.exists(ruta_pdf):
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
        }

    except Exception as error:
        print(
            "Error generando Casas por Signo:",
            error,
        )

        return {
            "ok": False,
            "error": str(error),
        }



# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print("═" * 55)
    print("  CASAS POR SIGNO — Arquitectura Interna")
    print("═" * 55)
    print()

    nombre = input("Nombre completo: ").strip()

    if not nombre:
        print("El nombre no puede estar vacío.")
        sys.exit(1)

    while True:
        try:
            partes = (
                input("Fecha de nacimiento (DD/MM/AAAA): ")
                .strip()
                .split("/")
            )

            if len(partes) != 3:
                raise ValueError

            dia = int(partes[0])
            mes = int(partes[1])
            anio = int(partes[2])

            datetime(
                anio,
                mes,
                dia,
            )

            break

        except (ValueError, IndexError):
            print("Formato incorrecto. Usa DD/MM/AAAA.")

    while True:
        try:
            hora = int(
                input("Hora de nacimiento (0-23): ").strip()
            )

            if 0 <= hora <= 23:
                break

            print("Introduce un valor entre 0 y 23.")

        except ValueError:
            print("Introduce un número entero.")

    while True:
        try:
            minuto = int(
                input("Minuto de nacimiento (0-59): ").strip()
            )

            if 0 <= minuto <= 59:
                break

            print("Introduce un valor entre 0 y 59.")

        except ValueError:
            print("Introduce un número entero.")

    ciudad = input(
        "Lugar de nacimiento (ciudad, país): "
    ).strip()

    if not ciudad:
        print("El lugar no puede estar vacío.")
        sys.exit(1)

    print("\nCalculando carta natal...")

    try:
        lat, lon = geocodificar(
            ciudad
        )

        tz_name = obtener_timezone(
            lat,
            lon,
        )

        carta = calcular_carta(
            anio,
            mes,
            dia,
            hora,
            minuto,
            lat,
            lon,
            tz_name,
        )

    except Exception as error:
        print(
            f"Error al calcular la carta: {error}"
        )
        sys.exit(1)

    nombre_f = (
        nombre
        .replace(" ", "_")
        .replace("/", "-")
        .replace("\\", "-")
    )

    ruta_base = os.path.join(
        BASE_DIR,
        nombre_f + "_Casas_por_Signo",
    )

    ruta_rueda = ruta_base + "_rueda.png"

    print("\nGenerando rueda...")

    try:
        dibujar_arquitectura_casas(
            carta,
            ruta_rueda,
        )

    except Exception as error:
        print(
            f"Error al generar la rueda: {error}"
        )
        sys.exit(1)

    if not os.path.exists(
        ruta_rueda
    ):
        print(
            "No se ha podido crear el archivo de la rueda."
        )
        sys.exit(1)

    print(
        f"\nRueda generada correctamente:\n{ruta_rueda}"
    )

    ruta_pdf = ruta_base + ".pdf"

    print(
        "\nGenerando PDF de Casas por Signo..."
    )

    print(
        f"Ruta prevista:\n{os.path.abspath(ruta_pdf)}"
    )

    try:
        generar_casas_por_signo(
            ruta_pdf=ruta_pdf,
            carta=carta,
            nombre=nombre,
            anio=anio,
            mes=mes,
            dia=dia,
            hora=hora,
            minuto=minuto,
            ciudad=ciudad,
            lat=lat,
            lon=lon,
            tz_name=tz_name,
            ruta_rueda=ruta_rueda,
        )

    except Exception as error:
        print(
            "\nError al generar el PDF:"
        )
        print(
            f"{type(error).__name__}: {error}"
        )
        sys.exit(1)

    if not os.path.exists(
        ruta_pdf
    ):
        print(
            "\nEl proceso terminó, pero no se encontró el archivo PDF."
        )
        sys.exit(1)

    print(
        "\nPDF generado correctamente:"
    )

    print(
        os.path.abspath(
            ruta_pdf
        )
    )

    print(
        f"Tamaño: {os.path.getsize(ruta_pdf)} bytes"
    )


if __name__ == "__main__":
    main()