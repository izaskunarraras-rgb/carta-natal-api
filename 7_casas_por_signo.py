#!/usr/bin/env python3
"""
7. Casas por signo — Ejes e interceptaciones — Arquitectura Interna
Aquí se desarrolla cómo se distribuye la energía en las distintas áreas de tu vida,
qué temas suelen ocupar más espacio,
desde dónde tiendes a vivir determinadas experiencias
y qué tensiones o aprendizajes aparecen en los ejes principales de la carta.

También se exploran los signos interceptados,
que a menudo muestran partes internas que necesitan más tiempo, recorrido o consciencia para poder expresarse con claridad.
"""

import sys, os, math, subprocess
from collections import Counter
from datetime import datetime
import swisseph as swe
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import pytz
import matplotlib.pyplot as plt
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ─── CONSTANTES ────────────────────────────────────────────────────────────────

SIGNOS = ["Aries","Tauro","Géminis","Cáncer","Leo","Virgo",
          "Libra","Escorpio","Sagitario","Capricornio","Acuario","Piscis"]

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

PLANETAS_IDS = [
    (swe.SUN,    "Sol",      "☉"),
    (swe.MOON,   "Luna",     "☽"),
    (swe.MERCURY,"Mercurio", "☿"),
    (swe.VENUS,  "Venus",    "♀"),
    (swe.MARS,   "Marte",    "♂"),
    (swe.JUPITER,"Júpiter",  "♃"),
    (swe.SATURN, "Saturno",  "♄"),
    (swe.URANUS, "Urano",    "♅"),
    (swe.NEPTUNE,"Neptuno",  "♆"),
    (swe.PLUTO,  "Plutón",   "♇"),
]
CHIRON_ID = swe.CHIRON
LILITH_ID = swe.MEAN_APOG

PLANETA_SIMBOLO = {
    "Sol":"☉",
    "Luna":"☽",
    "Mercurio":"☿",
    "Venus":"♀",
    "Marte":"♂",
    "Júpiter":"♃",
    "Saturno":"♄",
    "Urano":"♅",
    "Neptuno":"♆",
    "Plutón":"♇",
    "Nodo Norte":"☊",
    "Quirón":"⚷",
    "Lilith":"⚸"
}

SIMBOLOS_SIGNOS = ["♈","♉","♊","♋","♌","♍","♎","♏","♐","♑","♒","♓"]
COLORES_ELEMENTO = {"Fuego":"#CC2200","Tierra":"#2E7D32","Aire":"#E67E00","Agua":"#1A5FA8"}
COLORES_PLANETA = {
    "Sol":"#CC2200","Marte":"#CC2200","Júpiter":"#CC2200",
    "Venus":"#2E7D32","Saturno":"#2E7D32",
    "Mercurio":"#E67E00","Urano":"#E67E00",
    "Luna":"#1A5FA8","Neptuno":"#1A5FA8","Plutón":"#1A5FA8",
    "Quirón":"#7B2D8B","Lilith":"#7B2D8B",
    "Nodo Norte":"#888800","Nodo Sur":"#888800",
}


# ─── LABELS DE CASAS ──────────────────────────────────────────────────────────

CASA_LABEL = {
    1:  "Identidad y presencia",
    2:  "Recursos y seguridad",
    3:  "Comunicación y entorno cercano",
    4:  "Base y hogar",
    5:  "Expresión y creatividad",
    6:  "Vida cotidiana y salud",
    7:  "Vínculos y relaciones",
    8:  "Transformación y profundidad",
    9:  "Horizonte y expansión",
    10: "Dirección y proyección",
    11: "Redes y colectivo",
    12: "Mundo interior",
}

CASA_AREA = {
    1: (
        "La Casa 1 habla de cómo entras en la vida y de la impresión que sueles generar "
        "de forma espontánea. "
        "Tiene relación con la presencia, el cuerpo y la manera en que tiendes a posicionarte "
        "cuando algo comienza."
    ),

    2: (
        "La Casa 2 muestra tu relación con la seguridad, los recursos y aquello que necesitas "
        "para sentir estabilidad. "
        "Aquí aparecen tanto lo material como la sensación interna de sostén."
    ),

    3: (
        "La Casa 3 se relaciona con la comunicación cotidiana, el pensamiento habitual "
        "y el entorno cercano. "
        "Habla de cómo procesas lo inmediato y de la manera en que intercambias información "
        "con lo que te rodea."
    ),

    4: (
        "La Casa 4 habla de la base emocional y del lugar interno desde el que necesitas sostenerte. "
        "Tiene relación con el hogar, las raíces, la intimidad "
        "y aquello que te ayuda a sentir refugio."
    ),

    5: (
        "La Casa 5 muestra cómo tiendes a expresarte cuando hay espacio para hacerlo libremente. "
        "Aquí aparece la creatividad, el disfrute, el impulso de crear "
        "y aquello que nace desde ti sin obligación."
    ),

    6: (
        "La Casa 6 se relaciona con la vida cotidiana, los hábitos y la manera en que cuidas "
        "tu energía en el día a día. "
        "También habla de la relación con el trabajo cotidiano "
        "y con aquello que ayuda a sostener equilibrio y continuidad."
    ),

    7: (
        "La Casa 7 habla de los vínculos cercanos y de lo que aparece cuando entras "
        "en relación directa con otras personas. "
        "Aquí se desarrollan los acuerdos, las asociaciones "
        "y las dinámicas de espejo."
    ),

    8: (
        "La Casa 8 se relaciona con los procesos profundos de cambio y transformación. "
        "Habla de lo compartido, de lo intenso "
        "y de aquello que suele remover capas internas importantes."
    ),

    9: (
        "La Casa 9 muestra la necesidad de ampliar mirada y abrir horizonte. "
        "Tiene relación con el aprendizaje profundo, la búsqueda de sentido, "
        "los viajes y aquello que expande tu manera de comprender la vida."
    ),

    10: (
        "La Casa 10 habla de dirección, proyección y construcción visible. "
        "Aquí aparece la manera en que buscas desarrollar tu camino "
        "y el lugar que deseas ocupar hacia afuera."
    ),

    11: (
        "La Casa 11 se relaciona con los grupos, las redes y los proyectos compartidos. "
        "Habla de cómo te vinculas con lo colectivo "
        "y de aquello que deseas construir junto a otras personas."
    ),

    12: (
        "La Casa 12 habla del mundo interior y de los procesos que necesitan silencio, retiro "
        "o más tiempo para poder comprenderse. "
        "Aquí aparecen muchas veces lo inconsciente, el descanso "
        "y las partes más difíciles de ver con claridad inmediata."
    ),
}

# ─── TEXTOS: SIGNO EN CASA ────────────────────────────────────────────────────
# Cómo se vive un área de la vida cuando un signo está en su cúspide.

SIGNO_EN_CASA = {

"Aries": (
    "Con Aries en la cúspide, esta área de la vida suele moverse rápido. "
    "Tiendes a entrar antes de tenerlo todo claro y muchas veces necesitas descubrir sobre la marcha qué hacer con lo que aparece.\n\n"

    "Aquí suele haber iniciativa, impulso y necesidad de avanzar, "
    "aunque a veces puede costar sostener lo empezado cuando desaparece la motivación inicial."
),

"Tauro": (
    "Con Tauro en la cúspide, esta parte de la vida necesita tiempo para asentarse. "
    "No sueles moverte deprisa aquí, pero cuando algo echa raíces puede mantenerse durante mucho tiempo.\n\n"

    "La estabilidad tiene mucha importancia en este ámbito, "
    "aunque a veces puede costar hacer cambios incluso cuando ya serían necesarios."
),

"Géminis": (
    "Con Géminis en la cúspide, esta área suele vivirse desde la curiosidad, el movimiento "
    "y la necesidad de variedad. "
    "Tiendes a aprender rápido y a conectar fácilmente con distintas ideas o personas.\n\n"

    "Aquí suele haber agilidad mental y facilidad para adaptarte, "
    "aunque mantener una única dirección durante mucho tiempo puede hacerse más difícil."
),

"Cáncer": (
    "Con Cáncer en la cúspide, esta parte de la vida suele vivirse de forma muy sensible y personal. "
    "Necesitas sentir seguridad emocional antes de abrirte o avanzar realmente en este ámbito.\n\n"

    "Aquí tiene mucha importancia la protección, el cuidado y la sensación de pertenencia, "
    "aunque a veces puedes cerrarte si no sientes suficiente confianza."
),

"Leo": (
    "Con Leo en la cúspide, esta área suele cobrar fuerza cuando puedes expresarte "
    "con creatividad y sentir que lo que haces tiene valor o impacto. "
    "Suele haber bastante energía en este ámbito cuando puedes mostrarte con autenticidad.\n\n"

    "Aquí puede aparecer necesidad de reconocimiento o de sentirte visto, "
    "aunque a veces el miedo a no recibir respuesta puede hacer que te retraigas más de lo que parece."
),

"Virgo": (
    "Con Virgo en la cúspide, esta área suele vivirse desde la observación, el detalle "
    "y la necesidad de mejorar las cosas poco a poco. "
    "Tiendes a fijarte fácilmente en lo que podría ajustarse o hacerse de una manera más precisa.\n\n"

    "Aquí suele haber responsabilidad y atención práctica, "
    "aunque a veces puedes exigirte más de lo que realmente puedes sostener."
),

"Libra": (
    "Con Libra en la cúspide, esta área suele tomar forma a través de los vínculos "
    "y de la relación con otras personas. "
    "Necesitas cierto equilibrio o sensación de reciprocidad para sentirte bien aquí.\n\n"

    "Aquí suele haber capacidad para dialogar, mediar o buscar armonía, "
    "aunque a veces puede costar tomar decisiones sin tener en cuenta constantemente a la otra persona."
),

"Escorpio": (
    "Con Escorpio en la cúspide, esta área suele vivirse con intensidad y profundidad. "
    "Suele haber dificultad para vivir superficialmente lo que ocurre aquí: "
    "cuando algo importa, suele implicar una implicación real.\n\n"

    "Aquí suelen aparecer procesos de transformación importantes, "
    "aunque a veces también puede haber necesidad de control o dificultad para soltar."
),

"Sagitario": (
    "Con Sagitario en la cúspide, esta área necesita amplitud, sentido y sensación de crecimiento. "
    "Tiendes a moverte mejor cuando sientes que algo te abre horizonte o te permite avanzar más allá de lo conocido.\n\n"

    "Aquí suele haber entusiasmo y necesidad de expansión, "
    "aunque a veces puede costar concretar o sostener todo lo que se inicia."
),

"Capricornio": (
    "Con Capricornio en la cúspide, esta área suele vivirse con responsabilidad y visión a largo plazo. "
    "Tiendes a construir despacio, paso a paso, buscando resultados sólidos y duraderos.\n\n"

    "Aquí suele haber constancia y capacidad de esfuerzo, "
    "aunque a veces puedes cargar con demasiado peso o sentir que nunca es suficiente."
),

"Acuario": (
    "Con Acuario en la cúspide, esta área suele vivirse de una manera distinta a la habitual. "
    "Necesitas libertad, espacio propio o una forma personal de hacer las cosas.\n\n"

    "Aquí suele haber necesidad de independencia y mirada amplia, "
    "aunque a veces puede costar conectar con lo emocional o con lo más inmediato de este ámbito."
),

"Piscis": (
    "Con Piscis en la cúspide, esta área suele vivirse de forma sensible, abierta y cambiante. "
    "Tiendes a percibir muchas capas a la vez y a dejarte afectar fácilmente por el ambiente o por lo que ocurre alrededor.\n\n"

    "Aquí suele haber empatía, imaginación y capacidad de adaptación, "
    "aunque a veces puede costar poner límites claros o dar forma concreta a lo que sientes."
),

}

# ─── TEXTOS: ASCENDENTE POR SIGNO ─────────────────────────────────────────────
# Cómo sueles entrar en la vida y relacionarte con el mundo.

ASC_TEXTO = {

"Aries": (
    "Con Ascendente en Aries, sueles entrar en la vida de forma directa y rápida. "
    "Tiendes a actuar antes de tener todas las respuestas, "
    "y muchas veces descubres el camino mientras ya estás avanzando.\n\n"

    "Las demás personas suelen percibirte como una persona con iniciativa, energía "
    "o capacidad para moverse hacia adelante. "
    "A veces, sin embargo, la velocidad puede hacer que te cueste parar "
    "y registrar realmente lo que estás sintiendo o viviendo."
),

"Tauro": (
    "Con Ascendente en Tauro, sueles entrar en la vida de una forma más tranquila y estable. "
    "Necesitas tiempo para asentarte en los lugares, las relaciones o las situaciones nuevas.\n\n"

    "Las demás personas suelen percibirte como una persona consistente, calmada "
    "o difícil de mover cuando algo ya ha echado raíces. "
    "A veces puede costarte hacer cambios rápidos, incluso cuando una parte de ti sabe que serían necesarios."
),

"Géminis": (
    "Con Ascendente en Géminis, tiendes a entrar en la vida a través de la curiosidad, la comunicación "
    "y el intercambio con lo que te rodea. "
    "Sueles adaptarte rápido a los contextos y conectar fácilmente con distintas personas.\n\n"

    "Las demás personas suelen percibirte como una persona ágil, cercana o fácil de tratar. "
    "A veces, sin embargo, puedes mostrar facetas muy distintas según el entorno "
    "y sentir que cuesta mantener una dirección completamente estable."
),

"Cáncer": (
    "Con Ascendente en Cáncer, sueles entrar en la vida de forma sensible y cautelosa. "
    "Necesitas sentir cierta seguridad antes de abrirte realmente hacia fuera.\n\n"

    "Las demás personas suelen percibirte como una persona protectora, reservada "
    "o emocionalmente receptiva. "
    "Cuando no te sientes en confianza, puedes tender a cerrarte "
    "o retirarte antes de avanzar."
),

"Leo": (
    "Con Ascendente en Leo, tiendes a entrar en la vida con presencia y necesidad de expresión. "
    "Sueles mostrarte de forma visible cuando sientes confianza en lo que eres o en lo que haces.\n\n"

    "Las demás personas suelen percibirte como una persona cálida, creativa "
    "o difícil de ignorar. "
    "A veces puede aparecer necesidad de reconocimiento "
    "o miedo a no recibir respuesta del entorno."
),

"Virgo": (
    "Con Ascendente en Virgo, sueles entrar en la vida observando primero lo que ocurre. "
    "Tiendes a fijarte fácilmente en los detalles y en aquello que podría hacerse de una manera más precisa.\n\n"

    "Las demás personas suelen percibirte como una persona responsable, cuidadosa "
    "o competente. "
    "A veces, sin embargo, puedes quedarte demasiado tiempo analizando "
    "antes de dar el paso."
),

"Libra": (
    "Con Ascendente en Libra, tiendes a entrar en la vida a través del vínculo y de la relación con otras personas. "
    "Necesitas cierto equilibrio en el entorno para sentirte realmente bien.\n\n"

    "Las demás personas suelen percibirte como una persona amable, receptiva "
    "o diplomática. "
    "A veces puede costarte posicionarte con claridad "
    "si sientes demasiada tensión o desacuerdo alrededor."
),

"Escorpio": (
    "Con Ascendente en Escorpio, sueles entrar en la vida de forma intensa pero reservada. "
    "No tiendes a mostrarlo todo desde el principio "
    "y necesitas observar antes de confiar realmente.\n\n"

    "Las demás personas suelen percibirte como una persona profunda, magnética "
    "o difícil de leer. "
    "A veces puede haber necesidad de control "
    "o dificultad para relajarte en lo desconocido."
),

"Sagitario": (
    "Con Ascendente en Sagitario, tiendes a entrar en la vida de forma abierta y expansiva. "
    "Necesitas movimiento, horizonte y sensación de crecimiento para sentirte con vitalidad.\n\n"

    "Las demás personas suelen percibirte como una persona optimista, espontánea "
    "o con facilidad para mirar hacia adelante. "
    "A veces, sin embargo, puede costar sostener profundidad "
    "o permanencia en ciertas situaciones."
),

"Capricornio": (
    "Con Ascendente en Capricornio, sueles entrar en la vida de forma más contenida y responsable. "
    "Tiendes a tomarte las cosas en serio "
    "y a construir poco a poco antes de mostrarte plenamente.\n\n"

    "Las demás personas suelen percibirte como una persona sólida, disciplinada "
    "o fiable. "
    "A veces puede costarte relajarte "
    "o sentir que ya has hecho suficiente."
),

"Acuario": (
    "Con Ascendente en Acuario, tiendes a entrar en la vida desde una mirada propia y poco convencional. "
    "Necesitas libertad para ser quien eres "
    "y espacio para hacer las cosas a tu manera.\n\n"

    "Las demás personas suelen percibirte como una persona independiente, original "
    "o difícil de encajar en categorías simples. "
    "A veces puede costarte conectar con lo emocional más inmediato "
    "o sentirte cómoda en dinámicas demasiado rígidas."
),

"Piscis": (
    "Con Ascendente en Piscis, tiendes a entrar en la vida de forma sensible, abierta y muy receptiva al entorno. "
    "Percibes fácilmente lo que ocurre alrededor "
    "y eso influye mucho en cómo te muestras.\n\n"

    "Las demás personas suelen percibirte como una persona empática, suave "
    "o difícil de definir del todo. "
    "A veces puede costarte mantener límites claros "
    "o sostener una sensación estable de dirección."
),

}

# ─── TEXTOS: DESCENDENTE POR SIGNO ────────────────────────────────────────────
# Cómo tiendes a vivir el encuentro con otras personas.

DSC_TEXTO = {

"Aries": (
    "Con Descendente en Aries, tiendes a buscar vínculos con personas directas, activas "
    "o con capacidad para tomar iniciativa. "
    "Muchas veces las relaciones te empujan a moverte, decidir o salir de la pasividad.\n\n"

    "Suele haber atracción hacia personas con fuerza o autonomía, "
    "aunque a veces puedes delegar demasiado en la otra persona la capacidad de actuar "
    "o de marcar dirección dentro del vínculo."
),

"Tauro": (
    "Con Descendente en Tauro, tiendes a buscar vínculos estables, tranquilos "
    "y construidos poco a poco. "
    "La confianza suele aparecer cuando hay continuidad, calma y sensación de seguridad.\n\n"

    "Suele haber mucha valoración de la constancia y la fiabilidad en las relaciones, "
    "aunque a veces puedes mantener vínculos que ya no te hacen bien "
    "simplemente porque cuesta cambiar lo conocido."
),

"Géminis": (
    "Con Descendente en Géminis, tiendes a buscar relaciones donde haya conversación, intercambio "
    "y movimiento mental. "
    "Necesitas sentir que puedes comunicarte y compartir ideas con libertad.\n\n"

    "Suele haber atracción hacia personas curiosas, ágiles o estimulantes, "
    "aunque a veces puede haber mucha conexión mental "
    "y más dificultad para sostener profundidad emocional."
),

"Cáncer": (
    "Con Descendente en Cáncer, tiendes a buscar vínculos donde exista cuidado, cercanía "
    "y sensación de refugio emocional. "
    "Las relaciones suelen tocar partes muy sensibles.\n\n"

    "Suele haber mucha valoración de la ternura, la disponibilidad emocional "
    "y la sensación de hogar compartido, "
    "aunque a veces puede aparecer necesidad de más contención emocional "
    "de la que el vínculo realmente puede ofrecer."
),

"Leo": (
    "Con Descendente en Leo, tiendes a buscar relaciones vivas, expresivas "
    "y con presencia emocional. "
    "Necesitas sentir que hay calidez, atención y reconocimiento mutuo dentro del vínculo.\n\n"

    "Suele haber atracción hacia personas creativas, generosas "
    "o con una presencia fuerte, "
    "aunque a veces puede aparecer demasiada dependencia de la validación afectiva del otro lado."
),

"Virgo": (
    "Con Descendente en Virgo, tiendes a buscar relaciones construidas desde lo práctico, "
    "el cuidado cotidiano y la atención a los detalles. "
    "Muchas veces el amor aparece en las pequeñas cosas.\n\n"

    "Suele haber valoración de personas responsables, organizadas "
    "o capaces de sostener el día a día, "
    "aunque a veces puede aparecer exceso de exigencia "
    "o tendencia a fijarte demasiado en lo que falta."
),

"Libra": (
    "Con Descendente en Libra, tiendes a buscar relaciones equilibradas y recíprocas. "
    "Necesitas sentir que hay diálogo, escucha y cierta armonía en el vínculo.\n\n"

    "Suele haber mucha importancia en la capacidad de llegar a acuerdos "
    "y construir desde el respeto mutuo, "
    "aunque a veces puedes evitar el conflicto incluso cuando sería necesario atravesarlo."
),

"Escorpio": (
    "Con Descendente en Escorpio, tiendes a vivir las relaciones con intensidad y profundidad. "
    "Los vínculos importantes suelen movilizar mucho internamente.\n\n"

    "Suele haber atracción hacia personas intensas, profundas "
    "o emocionalmente complejas, "
    "aunque a veces pueden aparecer dinámicas de control, miedo a perder "
    "o dificultad para relajarte dentro del vínculo."
),

"Sagitario": (
    "Con Descendente en Sagitario, tiendes a buscar relaciones donde exista crecimiento, libertad "
    "y apertura hacia algo más amplio. "
    "Necesitas sentir que el vínculo permite seguir expandiéndote.\n\n"

    "Suele haber valoración de personas optimistas, abiertas "
    "o con ganas de explorar la vida, "
    "aunque a veces puede costar sostener relaciones demasiado cerradas o rutinarias."
),

"Capricornio": (
    "Con Descendente en Capricornio, tiendes a buscar relaciones serias, estables "
    "y construidas a largo plazo. "
    "La confianza suele aparecer lentamente y necesita tiempo para consolidarse.\n\n"

    "Suele haber valoración de personas responsables, maduras "
    "o comprometidas, "
    "aunque a veces puedes vivir los vínculos con demasiada exigencia "
    "o dificultad para relajarte emocionalmente."
),

"Acuario": (
    "Con Descendente en Acuario, tiendes a buscar relaciones donde exista libertad, autenticidad "
    "y espacio individual. "
    "Necesitas sentir que puedes ser tú mismo dentro del vínculo.\n\n"

    "Suele haber atracción hacia personas originales, independientes "
    "o poco convencionales, "
    "aunque a veces puede costar sostener la cercanía emocional continua "
    "o las dinámicas demasiado demandantes."
),

"Piscis": (
    "Con Descendente en Piscis, tiendes a buscar relaciones sensibles, empáticas "
    "y emocionalmente abiertas. "
    "Los vínculos suelen vivirse desde mucha permeabilidad y conexión emocional.\n\n"

    "Suele haber atracción hacia personas sensibles, intuitivas "
    "o emocionalmente profundas, "
    "aunque a veces puede costar poner límites claros "
    "o ver la relación tal y como realmente es."
),

}

MC_TEXTO = {

"Aries": (
    "Con Medio Cielo en Aries, sueles orientarte hacia el mundo de forma directa y activa. "
    "Muchas veces necesitas iniciar, abrir camino o moverte con autonomía en lo profesional.\n\n"

    "La sensación de avance suele llegarte a través de la acción y del movimiento constante. "
    "Este Medio Cielo suele funcionar mejor cuando existen retos nuevos, iniciativa propia "
    "y margen para actuar con rapidez."
),

"Tauro": (
    "Con Medio Cielo en Tauro, sueles orientarte profesionalmente de forma lenta pero constante. "
    "La necesidad de construir algo sólido y duradero suele tener mucha importancia para ti.\n\n"

    "Aquí sueles valorar la estabilidad, la fiabilidad y la continuidad en el tiempo. "
    "Muchas veces el reconocimiento llega despacio, "
    "pero con más capacidad de mantenerse."
),

"Géminis": (
    "Con Medio Cielo en Géminis, sueles orientarte hacia actividades relacionadas con la comunicación, "
    "las ideas, el aprendizaje o el intercambio de información.\n\n"

    "Aquí suele haber necesidad de variedad y movimiento intelectual. "
    "Muchas veces tienes facilidad para conectar distintas áreas o personas, "
    "aunque a veces también puede costarte mantener una única dirección durante mucho tiempo."
),

"Cáncer": (
    "Con Medio Cielo en Cáncer, sueles orientarte profesionalmente hacia el cuidado, "
    "la protección o la creación de espacios de confianza.\n\n"

    "Aquí suele tener mucha importancia el componente emocional del trabajo "
    "y la sensación de pertenencia con lo que haces. "
    "Muchas veces el recorrido profesional funciona mejor "
    "cuando existe una base emocional suficientemente estable."
),

"Leo": (
    "Con Medio Cielo en Leo, suele haber necesidad de expresar creatividad, presencia "
    "o autenticidad en el mundo profesional. "
    "Muchas veces aparece deseo de desarrollar algo propio y visible.\n\n"

    "Aquí suele cobrar importancia sentir que lo que haces tiene valor "
    "y puede ser reconocido por otras personas. "
    "La motivación suele crecer cuando existe espacio para mostrar lo que nace de ti."
),

"Virgo": (
    "Con Medio Cielo en Virgo, sueles orientarte hacia el detalle, la precisión "
    "y el deseo de hacer las cosas bien. "
    "Muchas veces el reconocimiento llega a través de la utilidad o de la calidad del trabajo realizado.\n\n"

    "Aquí suele haber responsabilidad, atención práctica "
    "y capacidad para mejorar procesos poco a poco, "
    "aunque a veces puede aparecer exceso de exigencia."
),

"Libra": (
    "Con Medio Cielo en Libra, sueles orientarte hacia trabajos donde los vínculos, "
    "la colaboración o la capacidad de generar equilibrio tienen importancia.\n\n"

    "Aquí suele funcionar bien todo lo relacionado con acuerdos, mediación "
    "o trabajo conjunto con otras personas. "
    "Muchas veces el crecimiento profesional aparece más fácilmente en colaboración que en aislamiento."
),

"Escorpio": (
    "Con Medio Cielo en Escorpio, sueles orientarte hacia procesos profundos, intensos "
    "o transformadores. "
    "Muchas veces existe necesidad de trabajar con temas que tengan peso emocional o capacidad de cambio real.\n\n"

    "Aquí suele haber tendencia a implicarte profundamente en lo que haces, "
    "aunque a veces también puede aparecer dificultad para tomar distancia "
    "o relajarte dentro del ámbito profesional."
),

"Sagitario": (
    "Con Medio Cielo en Sagitario, suele haber necesidad de expansión, aprendizaje "
    "y sensación de horizonte en lo profesional. "
    "Muchas veces el trabajo necesita tener sentido o permitirte crecimiento personal.\n\n"

    "Aquí suele haber entusiasmo, visión amplia "
    "y deseo de avanzar hacia algo más grande, "
    "aunque a veces puede costarte sostener estructuras demasiado limitantes o repetitivas."
),

"Capricornio": (
    "Con Medio Cielo en Capricornio, sueles orientarte profesionalmente de forma seria, constante "
    "y construida a largo plazo. "
    "Muchas veces existe necesidad de consolidar algo sólido con el tiempo.\n\n"

    "Aquí suele haber disciplina, responsabilidad "
    "y capacidad de esfuerzo sostenido. "
    "El reconocimiento suele llegar lentamente, "
    "pero con más estabilidad y profundidad."
),

"Acuario": (
    "Con Medio Cielo en Acuario, suele haber necesidad de desarrollar un camino propio y poco convencional. "
    "Muchas veces aparece orientación hacia ideas nuevas, proyectos colectivos "
    "o formas distintas de entender lo profesional.\n\n"

    "Aquí suele haber independencia, innovación "
    "y necesidad de libertad para hacer las cosas de otra manera. "
    "Muchas veces el trabajo necesita sentirse coherente con una visión más amplia."
),

"Piscis": (
    "Con Medio Cielo en Piscis, sueles orientarte profesionalmente de forma sensible, intuitiva "
    "o difícil de encajar en estructuras demasiado rígidas. "
    "Muchas veces aparece necesidad de trabajar desde la inspiración, la creatividad "
    "o la conexión emocional.\n\n"

    "Aquí suele haber capacidad de adaptación y percepción sutil, "
    "aunque a veces puede costarte definir límites claros "
    "o sostener una dirección profesional completamente estable."
),

}

# ─── TEXTOS: FONDO DEL CIELO POR SIGNO ───────────────────────────────────────
# Cómo el signo del IC organiza la base privada y la raíz interior.

IC_TEXTO = {

"Aries": (
    "Con Fondo del Cielo en Aries, tu mundo interior suele sostenerse mejor cuando puedes moverte, actuar "
    "o sentir autonomía. "
    "Muchas veces necesitas sentir que puedes avanzar por ti mismo antes que permanecer demasiado tiempo quieto.\n\n"

    "Aquí suele haber una base interna activa e inquieta. "
    "Muchas veces recuperas energía a través del movimiento, la iniciativa "
    "o la sensación de estar abriendo camino."
),

"Tauro": (
    "Con Fondo del Cielo en Tauro, tu base interior suele necesitar estabilidad, calma "
    "y sensación de continuidad. "
    "Muchas veces lo que más te sostiene es aquello que permanece y puede mantenerse en el tiempo.\n\n"

    "Aquí suele haber necesidad de seguridad concreta y de espacios tranquilos y previsibles. "
    "Muchas veces recuperas energía en contacto con lo simple, lo estable "
    "y aquello que transmite sensación de solidez."
),

"Géminis": (
    "Con Fondo del Cielo en Géminis, tu mundo interior suele moverse mucho a través de los pensamientos, "
    "las ideas y el intercambio mental. "
    "Muchas veces necesitas hablar, comprender o poner palabras a lo que te ocurre.\n\n"

    "Aquí suele haber necesidad de movimiento intelectual y estímulo mental. "
    "Muchas veces recuperas energía cuando puedes pensar, conversar "
    "o conectar con distintas perspectivas."
),

"Cáncer": (
    "Con Fondo del Cielo en Cáncer, tu base interior suele estar muy ligada a la necesidad de refugio emocional, "
    "protección y pertenencia. "
    "Muchas veces necesitas sentirte en casa emocionalmente para poder relajarte de verdad.\n\n"

    "Aquí suele haber mucha sensibilidad en lo íntimo y en los vínculos cercanos. "
    "Muchas veces recuperas energía cuando sientes cuidado, confianza "
    "y seguridad emocional."
),

"Leo": (
    "Con Fondo del Cielo en Leo, tu mundo interior suele necesitar expresión, creatividad "
    "y reconocimiento también en lo privado. "
    "Muchas veces necesitas sentir que puedes ser tú mismo sin esconder partes importantes de lo que eres.\n\n"

    "Aquí suele haber una necesidad profunda de expresarte con autenticidad. "
    "Muchas veces recuperas energía cuando puedes mostrarte de forma libre y espontánea."
),

"Virgo": (
    "Con Fondo del Cielo en Virgo, tu base interior suele sostenerse mejor cuando existe cierto orden, claridad "
    "y sensación de que las cosas están en su lugar. "
    "Muchas veces lo cotidiano influye muchísimo en cómo te sientes por dentro.\n\n"

    "Aquí suele haber necesidad de organización y estabilidad práctica. "
    "Muchas veces recuperas energía cuando el entorno inmediato está cuidado "
    "y las pequeñas cosas funcionan con armonía."
),

"Libra": (
    "Con Fondo del Cielo en Libra, tu mundo interior suele necesitar equilibrio y armonía en los vínculos cercanos. "
    "Muchas veces lo que ocurre en las relaciones influye directamente en tu sensación interna de bienestar.\n\n"

    "Aquí suele haber necesidad de calma relacional y de espacios agradables emocionalmente. "
    "Muchas veces recuperas energía cuando existe reciprocidad, escucha "
    "y sensación de armonía alrededor."
),

"Escorpio": (
    "Con Fondo del Cielo en Escorpio, tu mundo interior suele vivirse con mucha intensidad y profundidad. "
    "Muchas veces necesitas privacidad y espacios donde puedas sentir sin exponerte constantemente.\n\n"

    "Aquí suele haber emociones profundas y procesos internos muy transformadores. "
    "Muchas veces recuperas energía en la intimidad, el silencio "
    "o los espacios donde puedes bajar defensas."
),

"Sagitario": (
    "Con Fondo del Cielo en Sagitario, tu base interior suele necesitar horizonte, sentido "
    "y sensación de crecimiento. "
    "Muchas veces necesitas sentir que la vida se mueve hacia algún lugar para poder sentirte realmente bien.\n\n"

    "Aquí suele haber necesidad de amplitud y libertad interna. "
    "Muchas veces recuperas energía cuando puedes abrir mirada, aprender "
    "o conectar con algo que te inspire."
),

"Capricornio": (
    "Con Fondo del Cielo en Capricornio, tu mundo interior suele sostenerse a través de la estructura, "
    "la responsabilidad y la sensación de haber construido algo sólido. "
    "Muchas veces necesitas sentir estabilidad y control sobre tu propia vida.\n\n"

    "Aquí suele haber una base interna exigente y muy orientada a sostener. "
    "Muchas veces recuperas energía cuando sientes orden, estabilidad "
    "y continuidad en lo que has construido."
),

"Acuario": (
    "Con Fondo del Cielo en Acuario, tu base interior suele necesitar libertad, espacio propio "
    "y coherencia contigo mismo. "
    "Muchas veces necesitas sentir que puedes vivir a tu manera incluso en lo más íntimo.\n\n"

    "Aquí suele haber necesidad de independencia y autenticidad interna. "
    "Muchas veces recuperas energía cuando puedes alejarte de expectativas externas "
    "y conectar con tu propia forma de ver las cosas."
),

"Piscis": (
    "Con Fondo del Cielo en Piscis, tu mundo interior suele ser muy sensible, permeable "
    "y difícil de separar completamente de lo que ocurre alrededor. "
    "Muchas veces necesitas silencio, descanso o momentos de desconexión para poder regularte.\n\n"

    "Aquí suele haber mucha sensibilidad emocional e intuición. "
    "Muchas veces recuperas energía en espacios tranquilos, creativos "
    "o donde no sientes exigencia constante."
),

}

# ─── TEXTOS: SIGNOS INTERCEPTADOS ─────────────────────────────────────────────
# Qué implica que un signo no esté en ninguna cúspide.

INTERCEPTADO_TEXTO = {

"Aries": (
    "Aries está interceptado: la iniciativa directa, la acción rápida y la capacidad de empezar sin tenerlo todo claro "
    "pueden no salir de forma inmediata en ti. "
    "Es posible que esa fuerza exista, pero que necesite más consciencia para poder expresarse.\n\n"

    "En el área donde se encuentra Aries, puede costarte tomar impulso al principio "
    "o actuar desde tu propio deseo sin esperar una señal externa. "
    "Cuando esta energía se integra, suele aparecer más capacidad para decidir, iniciar "
    "y ocupar tu lugar con más claridad."
),

"Tauro": (
    "Tauro está interceptado: la estabilidad, la calma y la construcción lenta "
    "pueden no estar disponibles de forma espontánea en ti. "
    "Es posible que te cueste reconocer qué te da seguridad real o qué necesita tiempo para asentarse.\n\n"

    "En el área donde se encuentra Tauro, puede costarte sostener continuidad "
    "o confiar en los ritmos lentos. "
    "Cuando esta energía se integra, suele aparecer más capacidad para cuidar tus recursos, habitar el cuerpo "
    "y construir algo más sólido."
),

"Géminis": (
    "Géminis está interceptado: la comunicación, la curiosidad y la capacidad de poner palabras "
    "pueden no aparecer de forma inmediata en ti. "
    "Es posible que existan muchas ideas dentro, pero que cueste expresarlas con claridad o darles circulación.\n\n"

    "En el área donde se encuentra Géminis, puede costarte preguntar, hablar, contrastar "
    "o moverte con ligereza entre distintas opciones. "
    "Cuando esta energía se integra, suele aparecer más agilidad mental, más capacidad de diálogo "
    "y más facilidad para nombrar lo que ocurre."
),

"Cáncer": (
    "Cáncer está interceptado: la sensibilidad, el cuidado y la necesidad de pertenencia "
    "pueden no expresarse de forma inmediata en ti. "
    "Es posible que exista una vida emocional profunda, pero que cueste reconocerla, mostrarla "
    "o pedir sostén cuando hace falta.\n\n"

    "En el área donde se encuentra Cáncer, puede costarte proteger lo vulnerable "
    "o identificar qué te da verdadera seguridad emocional. "
    "Cuando esta energía se integra, suele aparecer más capacidad de cuidado, ternura "
    "y conexión con tus propias necesidades afectivas."
),

"Leo": (
    "Leo está interceptado: la expresión, la creatividad y la necesidad de mostrar lo propio "
    "pueden no salir de forma natural en ti. "
    "Es posible que exista deseo de brillar o crear, pero que cueste ocupar espacio sin pedir permiso.\n\n"

    "En el área donde se encuentra Leo, puede costarte mostrarte, disfrutar "
    "o reconocer el valor de lo que nace de ti. "
    "Cuando esta energía se integra, suele aparecer más presencia, más creatividad "
    "y más permiso interno para expresarte con autenticidad."
),

"Virgo": (
    "Virgo está interceptado: la claridad práctica, el orden y la capacidad de ajustar los detalles "
    "pueden no estar disponibles desde el principio en ti. "
    "Es posible que te cueste ver qué necesita mejora o cómo ordenar lo que está disperso.\n\n"

    "En el área donde se encuentra Virgo, puede costarte crear hábitos, establecer método "
    "o sostener una atención práctica sin caer en exigencia excesiva. "
    "Cuando esta energía se integra, suele aparecer más discernimiento, más precisión "
    "y más capacidad para cuidar lo cotidiano."
),

"Libra": (
    "Libra está interceptado: el equilibrio, la reciprocidad y la capacidad de crear acuerdos "
    "pueden no aparecer de forma espontánea en ti. "
    "Es posible que te cueste reconocer qué lugar ocupa la otra persona sin perder tu propio centro.\n\n"

    "En el área donde se encuentra Libra, puede costarte negociar, pedir equilibrio "
    "o sostener vínculos desde una medida justa. "
    "Cuando esta energía se integra, suele aparecer más capacidad de diálogo, cooperación "
    "y relación consciente."
),

"Escorpio": (
    "Escorpio está interceptado: la profundidad, la intensidad emocional y la capacidad de transformación "
    "pueden no ser fáciles de contactar al principio en ti. "
    "Es posible que exista mucho movimiento interno, pero que cueste entrar en él sin miedo o sin intentar controlarlo demasiado.\n\n"

    "En el área donde se encuentra Escorpio, puede costarte soltar, confiar "
    "o atravesar procesos que requieren entrega. "
    "Cuando esta energía se integra, suele aparecer más honestidad emocional, más profundidad "
    "y más capacidad para transformarte desde dentro."
),

"Sagitario": (
    "Sagitario está interceptado: la confianza, la expansión y la búsqueda de sentido "
    "pueden no aparecer de forma inmediata en ti. "
    "Es posible que te cueste abrir horizonte o confiar en una dirección más amplia.\n\n"

    "En el área donde se encuentra Sagitario, puede costarte mirar más lejos, creer en tu propio camino "
    "o permitir que la vida se abra más allá de lo conocido. "
    "Cuando esta energía se integra, suele aparecer más visión, más entusiasmo "
    "y más capacidad para avanzar con sentido."
),

"Capricornio": (
    "Capricornio está interceptado: la estructura, la responsabilidad y la construcción a largo plazo "
    "pueden no activarse de forma natural en ti. "
    "Es posible que te cueste ordenar el esfuerzo, sostener una dirección o reconocer tu propia autoridad.\n\n"

    "En el área donde se encuentra Capricornio, puede costarte poner límites, asumir responsabilidad "
    "o construir con paciencia sin endurecerte demasiado. "
    "Cuando esta energía se integra, suele aparecer más madurez, más estabilidad "
    "y más capacidad para dar forma real a lo importante."
),

"Acuario": (
    "Acuario está interceptado: la libertad, la mirada propia y la capacidad de pensar de forma diferente "
    "pueden no salir de manera inmediata en ti. "
    "Es posible que te cueste mostrar lo que te hace distinto o confiar plenamente en tu propia visión.\n\n"

    "En el área donde se encuentra Acuario, puede costarte sentir libertad real "
    "o permitirte hacer las cosas de una manera diferente a la esperada. "
    "Cuando esta energía se integra, suele aparecer más autenticidad, más independencia "
    "y más capacidad para seguir tu propio criterio."
),

"Piscis": (
    "Piscis está interceptado: la sensibilidad, la apertura y la conexión con lo sutil "
    "pueden no expresarse de forma espontánea en ti. "
    "Es posible que exista mucha percepción emocional o intuición, pero que cueste confiar en ella.\n\n"

    "En el área donde se encuentra Piscis, puede costarte relajarte, soltar el control "
    "o permitirte sentir sin intentar entenderlo todo de inmediato. "
    "Cuando esta energía se integra, suele aparecer más compasión, más intuición "
    "y más capacidad para conectar con lo que no puede explicarse solo desde la lógica."
),

}

# ─── CÁLCULO ASTROLÓGICO ──────────────────────────────────────────────────────

def geocodificar(ciudad):
    g = Nominatim(user_agent="ai_casas_signo", timeout=10)
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

def signo_desde_longitud(lon):
    idx = int(lon // 30) % 12
    return SIGNOS[idx]

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

    asc_lon = cuspides[0]
    mc_lon  = cuspides[9]

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


# ─── ANÁLISIS DE CASAS ────────────────────────────────────────────────────────

def _house_contains(c_ini, c_fin, lon):
    """True si la longitud lon está dentro del arco de casa [c_ini, c_fin)."""
    if c_ini <= c_fin:
        return c_ini <= lon < c_fin
    else:
        return lon >= c_ini or lon < c_fin

def analizar_casas(carta):
    planetas = carta["planetas"]
    cuspides = carta["cuspides"]

    # Sign of each cusp
    cusp_info = {}
    for i, c in enumerate(cuspides):
        s, g = grados_a_signo(c)
        cusp_info[i + 1] = {"signo": s, "grado": g, "lon": c}

    # Planets per house
    planetas_por_casa = {i: [] for i in range(1, 13)}
    planetas_principales = ["Sol", "Luna", "Mercurio", "Venus", "Marte",
                             "Júpiter", "Saturno", "Urano", "Neptuno", "Plutón"]
    for nombre in planetas_principales:
        p = planetas.get(nombre)
        if p and p.get("casa"):
            planetas_por_casa[p["casa"]].append(nombre)

    # Intercepted signs: signs not appearing on any cusp
    signos_en_cuspide = set(cusp_info[i]["signo"] for i in range(1, 13))
    interceptados = []
    for signo in SIGNOS:
        if signo not in signos_en_cuspide:
            sig_idx = SIGNOS.index(signo)
            sig_lon = sig_idx * 30.0
            for i in range(1, 13):
                c_ini = cuspides[i - 1]
                c_fin = cuspides[i % 12]
                if _house_contains(c_ini, c_fin, sig_lon):
                    interceptados.append((signo, i))
                    break

    # Duplicate signs (on two cusps)
    sign_counts = Counter(cusp_info[i]["signo"] for i in range(1, 13))
    duplicados = sorted([s for s, cnt in sign_counts.items() if cnt > 1])

    # Hemisphere counts
    planetas_lower = sum(len(planetas_por_casa[i]) for i in range(1, 7))
    planetas_upper = sum(len(planetas_por_casa[i]) for i in range(7, 13))
    # East (12,1,2,3,4,5 roughly) vs West (6,7,8,9,10,11)
    planetas_east = sum(len(planetas_por_casa[i]) for i in [12, 1, 2, 3, 4, 5])
    planetas_west = sum(len(planetas_por_casa[i]) for i in [6, 7, 8, 9, 10, 11])

    return {
        "cusp_info":       cusp_info,
        "planetas_por_casa": planetas_por_casa,
        "interceptados":   interceptados,
        "duplicados":      duplicados,
        "planetas_lower":  planetas_lower,
        "planetas_upper":  planetas_upper,
        "planetas_east":   planetas_east,
        "planetas_west":   planetas_west,
    }


# ─── TEXTOS DE SECCIÓN ────────────────────────────────────────────────────────

def texto_estructura_general(carta, analisis):
    ppc       = analisis["planetas_por_casa"]
    lower     = analisis["planetas_lower"]
    upper     = analisis["planetas_upper"]
    east      = analisis["planetas_east"]
    west      = analisis["planetas_west"]
    total     = lower + upper

    partes = []

    if total > 0:
        if lower > upper + 2:
            partes.append(
                f"La mayor parte de los planetas principales ({lower} de {total}) "
                f"están en las casas 1–6. "
                f"Esto suele indicar que buena parte de tu energía se orienta hacia la vida personal, "
                f"el cuerpo, lo cotidiano y los procesos más íntimos antes que hacia la exposición pública."
            )
        elif upper > lower + 2:
            partes.append(
                f"La mayor parte de los planetas principales ({upper} de {total}) "
                f"están en las casas 7–12. "
                f"Esto suele indicar que buena parte de tu energía se despliega a través del contacto con otras personas, "
                f"los vínculos, el mundo exterior y la dimensión social o colectiva."
            )
        else:
            partes.append(
                f"Los planetas se distribuyen de forma bastante equilibrada entre las casas 1–6 ({lower}) "
                f"y las casas 7–12 ({upper}). "
                f"Esto sugiere que tu vida necesita atender tanto lo íntimo y cotidiano "
                f"como lo vincular, social o visible."
            )

        if east > west + 2:
            partes.append(
                f"La mayor parte de los planetas están en el sector oriental de la carta (casas 12–5: {east}). "
                f"Esto suele mostrar una vida más orientada por iniciativa propia, impulso interno "
                f"y necesidad de decidir desde ti."
            )
        elif west > east + 2:
            partes.append(
                f"La mayor parte de los planetas están en el sector occidental de la carta (casas 6–11: {west}). "
                f"Esto suele mostrar una vida donde los vínculos, las respuestas del entorno "
                f"y lo que ocurre con otras personas tienen mucho peso."
            )

    casas_cargadas = sorted(
        [(n, len(pps)) for n, pps in ppc.items() if len(pps) >= 2],
        key=lambda x: -x[1]
    )

    if casas_cargadas:
        lineas = []
        for casa_n, cnt in casas_cargadas[:3]:
            nombres = ", ".join(ppc[casa_n])
            lineas.append(
                f"Casa {casa_n} ({CASA_LABEL[casa_n]}): {nombres} — "
                f"{'área especialmente importante' if cnt >= 3 else 'área con presencia relevante'}"
            )

        partes.append(
            "Casas con mayor concentración de planetas:\n" + "\n".join(lineas) +
            "\n\nLas casas con más planetas señalan áreas de vida donde se concentra mucha atención, "
            "movimiento interno y aprendizaje. No significa que sean las únicas importantes, "
            "pero sí que suelen tener más peso en tu manera de vivir, decidir y organizarte."
        )

    casas_vacias = [n for n in range(1, 13) if not ppc[n]]
    if len(casas_vacias) >= 6:
        partes.append(
            f"Las casas {', '.join(str(n) for n in casas_vacias)} no tienen planetas principales. "
            f"Esto no significa que esas áreas estén vacías o no importen. "
            f"Simplemente suelen vivirse de una forma más sencilla, a través del signo que aparece en la cúspide, "
            f"sin tanta carga planetaria directa."
        )

    return "\n\n".join(partes)


def texto_ejes(carta, analisis):
    asc = carta["asc"]
    mc  = carta["mc"]

    asc_sig = asc["signo"]
    mc_sig  = mc["signo"]

    asc_idx = SIGNOS.index(asc_sig)
    mc_idx  = SIGNOS.index(mc_sig)
    dsc_sig = SIGNOS[(asc_idx + 6) % 12]
    ic_sig  = SIGNOS[(mc_idx  + 6) % 12]

    elem_asc = ELEMENTO_SIGNO.get(asc_sig, "")
    elem_mc  = ELEMENTO_SIGNO.get(mc_sig,  "")

    t_asc = ASC_TEXTO.get(asc_sig, "")
    t_dsc = DSC_TEXTO.get(dsc_sig, "")
    t_mc  = MC_TEXTO.get(mc_sig,  "")
    t_ic  = IC_TEXTO.get(ic_sig,  "")

    ELEM_COMPAT = {frozenset(["Fuego","Aire"]), frozenset(["Tierra","Agua"])}
    mismos = (elem_asc == elem_mc)
    compat = frozenset([elem_asc, elem_mc]) in ELEM_COMPAT

    if mismos:
        tension_texto = (
            f"Ascendente ({asc_sig}, {elem_asc}) y Medio Cielo ({mc_sig}, {elem_mc}) "
            f"están en el mismo elemento. "
            f"Esto suele indicar bastante coherencia entre la forma en que entras en la vida "
            f"y la dirección hacia la que tiendes a orientarte. "
            f"Tu presencia y tu camino visible suelen apoyarse en una energía parecida."
        )
    elif compat:
        tension_texto = (
            f"Ascendente ({asc_sig}, {elem_asc}) y Medio Cielo ({mc_sig}, {elem_mc}) "
            f"están en elementos compatibles. "
            f"Esto suele facilitar que tu manera de presentarte y tu dirección profesional o vital "
            f"puedan acompañarse sin demasiada fricción."
        )
    else:
        tension_texto = (
            f"Ascendente ({asc_sig}, {elem_asc}) y Medio Cielo ({mc_sig}, {elem_mc}) "
            f"están en elementos que pueden crear tensión. "
            f"Puede haber diferencia entre cómo entras en las situaciones "
            f"y lo que necesitas construir o mostrar hacia fuera. "
            f"A veces esto hace que las demás personas perciban una parte de ti "
            f"mientras tu dirección profunda va por otro lugar."
        )

    return {
        "asc_sig": asc_sig, "dsc_sig": dsc_sig,
        "mc_sig":  mc_sig,  "ic_sig":  ic_sig,
        "asc_grado": asc["grado"], "mc_grado": mc["grado"],
        "t_asc": t_asc, "t_dsc": t_dsc,
        "t_mc":  t_mc,  "t_ic":  t_ic,
        "tension": tension_texto,
    }


def texto_casas(carta, analisis):
    cusp_info = analisis["cusp_info"]
    ppc       = analisis["planetas_por_casa"]
    textos    = {}

    for n in range(1, 13):
        info  = cusp_info[n]
        signo = info["signo"]
        planetas_aqui = ppc[n]

        t = CASA_AREA.get(n, "") + "\n\n" + SIGNO_EN_CASA.get(signo, "")

        if planetas_aqui:
            if len(planetas_aqui) > 1:
                t += (
                    f"\n\nPlanetas en esta casa: {', '.join(planetas_aqui)}. "
                    f"La presencia de varios planetas hace que esta área tenga mucho peso en tu carta. "
                    f"Suele ser un lugar donde se concentran aprendizajes, decisiones y movimiento interno."
                )
            else:
                t += (
                    f"\n\nPlanetas en esta casa: {planetas_aqui[0]}. "
                    f"Este planeta añade una capa importante a la manera en que vives esta área."
                )

        textos[n] = t

    return textos


def texto_interceptados(carta, analisis):
    interceptados = analisis["interceptados"]
    duplicados    = analisis["duplicados"]

    if not interceptados:
        return None

    partes = []

    for signo, casa in interceptados:
        partes.append({
            "signo": signo,
            "casa":  casa,
            "texto": INTERCEPTADO_TEXTO.get(signo, ""),
        })

    if duplicados:
        dup_str = " y ".join(duplicados)
        partes_dup = (
            f"Como consecuencia de las interceptaciones, "
            f"{'los signos' if len(duplicados) > 1 else 'el signo'} {dup_str} "
            f"{'aparecen' if len(duplicados) > 1 else 'aparece'} en dos cúspides consecutivas. "
            f"Esto puede hacer que dos áreas de tu vida se expresen desde una energía parecida, "
            f"como si compartieran una misma manera de empezar, reaccionar o tomar forma."
        )
    else:
        partes_dup = None

    return {"interceptados": partes, "duplicados_texto": partes_dup}


def texto_integracion(carta, analisis, ejes):
    asc_sig = ejes["asc_sig"]
    mc_sig  = ejes["mc_sig"]
    ic_sig  = ejes["ic_sig"]

    cusp_info = analisis["cusp_info"]
    ppc       = analisis["planetas_por_casa"]
    interceptados = analisis["interceptados"]

    elem_asc = ELEMENTO_SIGNO.get(asc_sig, "")
    elem_ic  = ELEMENTO_SIGNO.get(ic_sig,  "")

    partes = []

    partes.append(ejes["tension"])

    ELEM_COMPAT = {frozenset(["Fuego","Aire"]), frozenset(["Tierra","Agua"])}

    if elem_asc == elem_ic:
        partes.append(
            f"La base interna ({ic_sig}, IC) y la forma en que entras en la vida ({asc_sig}, ASC) "
            f"están en el mismo elemento. "
            f"Esto suele indicar coherencia entre lo que necesitas por dentro "
            f"y la manera en que te muestras hacia fuera."
        )
    elif frozenset([elem_asc, elem_ic]) not in ELEM_COMPAT:
        partes.append(
            f"La base interna ({ic_sig}, IC) y la forma en que entras en la vida ({asc_sig}, ASC) "
            f"están en elementos que pueden crear tensión. "
            f"Puede que lo que te sostiene por dentro no coincida del todo con la manera en que te muestras. "
            f"Por eso puede ser importante darte tiempo para traducir lo interno hacia fuera "
            f"sin forzarte a parecer de una forma que no respeta tu raíz."
        )

    casas_cargadas = [(n, pps) for n, pps in ppc.items() if len(pps) >= 2]
    if casas_cargadas:
        for casa_n, pps in sorted(casas_cargadas, key=lambda x: -len(x[1]))[:2]:
            signo_casa = cusp_info[casa_n]["signo"]
            partes.append(
                f"La Casa {casa_n} ({CASA_LABEL[casa_n]}, {signo_casa}) concentra "
                f"{len(pps)} planetas ({', '.join(pps)}). "
                f"Esta área tiene mucho peso en tu carta y suele pedir atención especial. "
                f"Cuando esta parte de la vida está cuidada, puede darte mucha fuerza. "
                f"Cuando se carga demasiado, también puede absorber más energía de la que parece."
            )

    if interceptados:
        sigs_int = [s for s, _ in interceptados]
        partes.append(
            f"Los signos interceptados ({', '.join(sigs_int)}) señalan cualidades que están en ti, "
            f"pero que quizá no salen de forma inmediata. "
            f"No están ausentes: necesitan más consciencia, tiempo y práctica para poder expresarse "
            f"con naturalidad en las áreas donde aparecen."
        )

    return "\n\n".join(partes)


def texto_orientacion(carta, analisis, ejes):
    cusp_info = analisis["cusp_info"]
    ppc       = analisis["planetas_por_casa"]
    asc_sig   = ejes["asc_sig"]
    mc_sig    = ejes["mc_sig"]
    interceptados = analisis["interceptados"]

    elem_asc = ELEMENTO_SIGNO.get(asc_sig, "")
    elem_mc  = ELEMENTO_SIGNO.get(mc_sig, "")

    casas_cargadas = sorted(ppc.items(), key=lambda x: -len(x[1]))
    casa_inicio_n  = casas_cargadas[0][0] if casas_cargadas[0][1] else 1
    signo_inicio   = cusp_info[casa_inicio_n]["signo"]

    INICIO_DETAIL = {
        "Fuego":  "empezar por activar movimiento, aunque no esté todo resuelto; la claridad puede llegar al avanzar",
        "Tierra": "empezar por un paso concreto, simple y verificable; lo pequeño y estable ordena el resto",
        "Aire":   "empezar por poner en palabras lo que ocurre y contrastarlo; nombrarlo puede darte claridad",
        "Agua":   "empezar por escuchar lo que sientes antes de exigirte una respuesta externa inmediata",
    }

    desde_donde = (
        f"El área con mayor concentración es la Casa {casa_inicio_n} "
        f"({CASA_LABEL[casa_inicio_n]}, {signo_inicio}). "
        f"Puede ayudarte {INICIO_DETAIL.get(ELEMENTO_SIGNO.get(signo_inicio,''), 'empezar desde la cualidad propia de esta casa')}."
    )

    ESTRUCTURA_DETAIL = {
        "Fuego":  "dar dirección al impulso, para que no sea solo velocidad o arranque",
        "Tierra": "crear una base concreta y sostenible antes de intentar crecer demasiado rápido",
        "Aire":   "ordenar ideas, acuerdos y conversaciones para que la dirección no se disperse",
        "Agua":   "cuidar el sostén emocional que necesitas para avanzar sin agotarte por dentro",
    }

    que_estructurar = (
        f"La Casa 10 ({CASA_LABEL[10]}, {mc_sig}) muestra una parte importante de tu orientación hacia fuera. "
        f"Lo primero que puede necesitar estructura aquí es "
        f"{ESTRUCTURA_DETAIL.get(elem_mc, 'la forma concreta que quieres construir en el mundo')}. "
        f"Sin esa claridad, puede haber mucha energía disponible pero poca dirección de salida."
    )

    ELEM_COMPAT = {frozenset(["Fuego","Aire"]), frozenset(["Tierra","Agua"])}

    if ELEMENTO_SIGNO.get(asc_sig) != elem_mc and frozenset([ELEMENTO_SIGNO.get(asc_sig,""), elem_mc]) not in ELEM_COMPAT:
        evitar = (
            f"Conviene evitar exigirte que tu forma de presentarte ({asc_sig}) "
            f"y tu manera de construir dirección ({mc_sig}) sean iguales. "
            f"Son energías diferentes y pueden necesitar ritmos, decisiones y cuidados distintos."
        )
    else:
        evitar = (
            f"Conviene evitar dar por hecho que, por haber coherencia entre el ASC ({asc_sig}) "
            f"y el MC ({mc_sig}), todo se ordena solo. "
            f"Incluso cuando hay afinidad, cada área necesita atención, límites y dirección."
        )

    if interceptados:
        evitar += (
            f" Los signos interceptados ({', '.join(s for s, _ in interceptados)}) "
            f"no conviene ignorarlos. "
            f"Son cualidades disponibles en ti, pero pueden necesitar práctica consciente "
            f"para no quedar ocultas o poco utilizadas."
        )

    si_no = (
        "Si no atiendes la distribución de las casas, las áreas más cargadas pueden absorber demasiada energía, "
        "mientras otras partes de la vida quedan poco cuidadas. "
        "La clave no es hacerlo todo con la misma intensidad, sino reconocer dónde hay más peso "
        "y qué zonas necesitan una atención más sencilla, clara y constante."
    )

    return {
        "desde_donde":     desde_donde,
        "que_estructurar": que_estructurar,
        "evitar":          evitar,
        "si_no":           si_no,
    }

def dibujar_rueda_casas(carta, nombre_persona, archivo_salida):
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


    orden = [
        "Sol","Luna","Mercurio","Venus","Marte","Júpiter","Saturno",
        "Urano","Neptuno","Plutón","Quirón","Lilith","Nodo Norte","Nodo Sur"
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
                  ciudad, lat, lon, tz_name, analisis, ruta_rueda):
    planetas  = carta["planetas"]
    asc       = carta["asc"]
    mc        = carta["mc"]
    cusp_info = analisis["cusp_info"]

    fecha_str = f"{dia:02d}/{mes:02d}/{anio}"
    hora_str  = f"{hora:02d}:{minuto:02d}"
    tz_obj    = pytz.timezone(tz_name)
    dt_local  = tz_obj.localize(datetime(anio, mes, dia, hora, minuto))
    utc_off   = dt_local.strftime("%z")
    utc_str   = f"UTC{utc_off[:3]}:{utc_off[3:]}"
    nom_esc   = esc(nombre)
    ciu_esc   = esc(ciudad)
    ruta_rueda_latex = os.path.basename(ruta_rueda).replace("\\", "/")

    asc_idx = SIGNOS.index(asc["signo"])
    mc_idx  = SIGNOS.index(mc["signo"])
    dsc_sig = SIGNOS[(asc_idx + 6) % 12]
    ic_sig  = SIGNOS[(mc_idx  + 6) % 12]
    ic_grado = (mc["grado"])  # IC has same degree as MC but opposite sign

    # Compute text sections
    t_gral   = texto_estructura_general(carta, analisis)
    ejes     = texto_ejes(carta, analisis)
    t_casas  = texto_casas(carta, analisis)
    t_int    = texto_interceptados(carta, analisis)
    t_integ  = texto_integracion(carta, analisis, ejes)
    t_or     = texto_orientacion(carta, analisis, ejes)

    def parrafos(texto):
        if not texto:
            return ""
        return "\n\n".join(esc(p) for p in texto.split("\n\n") if p.strip())

    # House table
    ppc = analisis["planetas_por_casa"]
    cusp_rows = ""
    for n in range(1, 13):
        info = cusp_info[n]
        planetas_aqui = ppc[n]
        pstr = ", ".join(planetas_aqui) if planetas_aqui else "—"
        cusp_rows += (
            f"  {n} & {esc(CASA_LABEL[n])} & {esc(info['signo'])} & "
            f"{grado_a_dms(info['grado'])} & {esc(pstr)} \\\\\n"
        )

    # Intercepted signs summary for data section
    interceptados = analisis["interceptados"]
    if interceptados:
        int_str = "; ".join(
            f"{esc(s)} (Casa {c})" for s, c in interceptados
        )
        int_nota = f"\\vspace{{0.3cm}}\\textbf{{Signos interceptados:}} {int_str}"
    else:
        int_nota = "\\vspace{0.3cm}\\textit{No hay signos interceptados en esta carta.}"

    # Sections for houses (section 3)
    casas_latex = ""
    for n in range(1, 13):
        info   = cusp_info[n]
        signo  = info["signo"]
        casas_latex += (
            f"\\subsubsection*{{Casa {n} — {esc(CASA_LABEL[n])} · {esc(signo)}}}\n"
            f"{parrafos(t_casas[n])}\n\n"
        )

    # Section 4: intercepted signs
    if t_int:
        int_latex = ""
        for item in t_int["interceptados"]:
            int_latex += (
                f"\\subsubsection*{{{esc(item['signo'])} interceptado — Casa {item['casa']}}}\n"
                f"{parrafos(item['texto'])}\n\n"
            )
        if t_int["duplicados_texto"]:
            int_latex += (
                f"\\subsubsection*{{Signos duplicados}}\n"
                f"{parrafos(t_int['duplicados_texto'])}\n\n"
            )
        int_section = int_latex
    else:
        int_section = (
            "\\textit{No hay signos interceptados en esta carta. "
            "Los doce signos zodiacales están presentes en las cúspides de las doce casas.}\n"
        )

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
\\usepackage[table]{{xcolor}}
\\usepackage{{booktabs}}
\\usepackage{{array}}
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
\\lhead{{\\textcolor{{grisai}}{{\\small Casas por signo}}}}
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
  \\vspace*{{1.5cm}}
  {{\\Huge\\bfseries\\color{{azulai}} Casas por signo}}\\\\[0.5cm]
  {{\\large\\color{{grisai}} Arquitectura Interna}}\\\\[0.3cm]
  {{\\small\\itshape\\color{{grisai}} Organización de la vida: ejes, distribución e interceptaciones}}\\\\[2cm]
  {{\\huge\\color{{doradoai}} {nom_esc}}}\\\\[1.5cm]
  {{\\Large {fecha_str} \\quad {hora_str}}}\\\\[0.3cm]
  {{\\Large {ciu_esc}}}\\\\[0.3cm]
  {{\\normalsize Lat: {lat:.4f}° \\quad Lon: {lon:.4f}° \\quad {utc_str}}}\\\\[0.3cm]
  {{\\normalsize Ascendente: {esc(asc['signo'])} {grado_a_dms(asc['grado'])} \\quad
    MC: {esc(mc['signo'])} {grado_a_dms(mc['grado'])}}}\\\\[2cm]
  \\begin{{tabular}}{{ll}}
    \\textbf{{ASC (Casa 1):}}  & {esc(asc['signo'])} {grado_a_dms(asc['grado'])} \\\\
    \\textbf{{DSC (Casa 7):}}  & {esc(dsc_sig)} {grado_a_dms(asc['grado'])} \\\\
    \\textbf{{MC (Casa 10):}}  & {esc(mc['signo'])} {grado_a_dms(mc['grado'])} \\\\
    \\textbf{{IC (Casa 4):}}   & {esc(ic_sig)} {grado_a_dms(ic_grado)} \\\\
  \\end{{tabular}}\\\\[2cm]
  \\vfill
  {{\\small Generado el {datetime.now().strftime("%d/%m/%Y")}}}
\\end{{titlepage}}

\\tableofcontents
\\newpage

\\begin{{center}}
\\includegraphics[width=0.88\\textwidth]{{{ruta_rueda_latex}}}
\\end{{center}}

\\newpage

% ── Datos de referencia ───────────────────────────────────────────────────────
\\section{{Datos de referencia}}

\\begin{{center}}
\\begin{{tabular}}{{rllll}}
  \\toprule
  \\textbf{{Casa}} & \\textbf{{Área}} & \\textbf{{Signo}} & \\textbf{{Cúspide}} & \\textbf{{Planetas}} \\\\
  \\midrule
{cusp_rows}  \\bottomrule
\\end{{tabular}}
\\end{{center}}

{int_nota}

\\newpage

% ── Interpretación ────────────────────────────────────────────────────────────
\\section{{Interpretación — Arquitectura Interna}}

\\begin{{center}}
{{\\small\\itshape
No se trata de describir la personalidad.\\\\ Se trata de mostrar cómo está organizada la vida y qué implica esa organización.
}}
\\end{{center}}

\\vspace{{0.5cm}}
\\Needspace{{5\\baselineskip}}

% ── 1. Estructura general ──────────────────────────────────────────────────────
\\needspace{{3\\baselineskip}}
\\subsection{{1. Estructura general de casas}}

{parrafos(t_gral)}

\\vspace{{0.5cm}}
\\Needspace{{5\\baselineskip}}

% ── 2. Ejes principales ───────────────────────────────────────────────────────
\\needspace{{3\\baselineskip}}
\\subsection{{2. Ejes principales}}

\\subsubsection*{{Ascendente — {esc(ejes['asc_sig'])} ({grado_a_dms(ejes['asc_grado'])})}}
{parrafos(ejes['t_asc'])}

\\subsubsection*{{Descendente — {esc(ejes['dsc_sig'])}}}
{parrafos(ejes['t_dsc'])}

\\subsubsection*{{Medio Cielo — {esc(ejes['mc_sig'])} ({grado_a_dms(ejes['mc_grado'])})}}
{parrafos(ejes['t_mc'])}

\\subsubsection*{{Fondo del Cielo — {esc(ejes['ic_sig'])}}}
{parrafos(ejes['t_ic'])}

\\subsubsection*{{La relación entre los ejes}}
{parrafos(ejes['tension'])}

\\vspace{{0.5cm}}
\\Needspace{{5\\baselineskip}}

% ── 3. Signos por casas ───────────────────────────────────────────────────────
\\needspace{{3\\baselineskip}}
\\subsection{{3. Distribución de signos por casas}}

{casas_latex}

\\vspace{{0.5cm}}
\\Needspace{{5\\baselineskip}}

% ── 4. Signos interceptados ───────────────────────────────────────────────────
\\needspace{{3\\baselineskip}}
\\subsection{{4. Signos interceptados}}

{int_section}

\\vspace{{0.5cm}}
\\Needspace{{5\\baselineskip}}

% ── 5. Integración ────────────────────────────────────────────────────────────
\\needspace{{3\\baselineskip}}
\\subsection{{5. Integración}}

{parrafos(t_integ)}

\\vspace{{0.5cm}}
\\Needspace{{5\\baselineskip}}

% ── 6. Orientación práctica ───────────────────────────────────────────────────
\\needspace{{3\\baselineskip}}
\\subsection{{6. Orientación práctica}}

\\subsubsection*{{Desde dónde empezar}}
{parrafos(t_or['desde_donde'])}

\\subsubsection*{{Qué estructurar primero}}
{parrafos(t_or['que_estructurar'])}

\\subsubsection*{{Qué evitar}}
{parrafos(t_or['evitar'])}

\\vspace{{0.6cm}}
{parrafos(t_or['si_no'])}

\\vspace{{0.5cm}}
\\Needspace{{5\\baselineskip}}
\\begin{{center}}
{{\\small\\itshape\\color{{grisai}}
La astrología se usa aquí como lenguaje simbólico de observación, no como definición de la persona.\\\\
El sistema es una aproximación funcional, no un diagnóstico.
}}
\\end{{center}}

\\end{{document}}
"""

    return latex


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print("═" * 57)
    print("  CASAS POR SIGNO — Arquitectura Interna")
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
        carta = calcular_carta(anio, mes, dia, hora, minuto, lat, lon, tz_name)
        asc   = carta["asc"]
        mc    = carta["mc"]
        print(f"  ASC: {asc['signo']} {grado_a_dms(asc['grado'])}")
        print(f"  MC:  {mc['signo']}  {grado_a_dms(mc['grado'])}")
    except Exception as e:
        print(f"Error en cálculo astrológico: {e}"); sys.exit(1)

    analisis = analizar_casas(carta)
    interceptados = analisis["interceptados"]
    if interceptados:
        print(f"  Signos interceptados: {', '.join(f'{s} (Casa {c})' for s,c in interceptados)}")
    else:
        print("  No hay signos interceptados.")

    nombre_f  = nombre.replace(" ", "_").replace("/", "-")
    ruta_base = os.path.join(BASE_DIR, nombre_f + "_Casas_por_Signo")
    ruta_tex  = ruta_base + ".tex"
    ruta_pdf  = ruta_base + ".pdf"
    ruta_rueda = os.path.join(BASE_DIR, "rueda_casas.png")
    dibujar_rueda_casas(carta, nombre, ruta_rueda)

    print("  Generando interpretación...")
    latex = generar_latex(carta, nombre, anio, mes, dia, hora, minuto,
                          ciudad, lat, lon, tz_name, analisis, ruta_rueda)
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
