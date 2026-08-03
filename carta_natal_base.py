
#!/usr/bin/env python3
"""
Carta Natal Base — Arquitectura Interna
Una lectura orientada a comprender tus tendencias principales,
tu forma de funcionar y los procesos de crecimiento
más importantes de tu carta natal.
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak,
    Table, TableStyle, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import cm
from reportlab.lib import colors



import sys, os, math, gc
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
    "Aries":"Cardinal","Tauro":"Fija","Géminis":"Mutable","Cáncer":"Cardinal",
    "Leo":"Fija","Virgo":"Mutable","Libra":"Cardinal","Escorpio":"Fija",
    "Sagitario":"Mutable","Capricornio":"Cardinal","Acuario":"Fija","Piscis":"Mutable"
}
COLORES_ELEMENTO = {"Fuego":"#CC2200","Tierra":"#2E7D32","Aire":"#E67E00","Agua":"#1A5FA8"}

PLANETAS_IDS = [
    (swe.SUN,"Sol","☉"),(swe.MOON,"Luna","☽"),(swe.MERCURY,"Mercurio","☿"),
    (swe.VENUS,"Venus","♀"),(swe.MARS,"Marte","♂"),(swe.JUPITER,"Júpiter","♃"),
    (swe.SATURN,"Saturno","♄"),(swe.URANUS,"Urano","♅"),
    (swe.NEPTUNE,"Neptuno","♆"),(swe.PLUTO,"Plutón","♇"),
]
CHIRON_ID  = swe.CHIRON
LILITH_ID  = swe.MEAN_APOG

COLORES_PLANETA = {
    "Sol":"#CC2200","Marte":"#CC2200","Júpiter":"#CC2200",
    "Venus":"#2E7D32","Saturno":"#2E7D32",
    "Mercurio":"#E67E00","Urano":"#E67E00",
    "Luna":"#1A5FA8","Neptuno":"#1A5FA8","Plutón":"#1A5FA8",
    "Quirón":"#7B2D8B","Lilith":"#7B2D8B",
    "Nodo Norte":"#888800","Nodo Sur":"#888800",
}

# ─── TEXTOS: SOL POR SIGNO ─────────────────────────────────────────────────────

SOL_SIGNO = {
"Aries": (
    "Con el Sol en Aries, necesitas movimiento, iniciativa y sensación de avance. "
    "Tu energía suele activarse rápidamente cuando algo te entusiasma o supone un reto. "
    "Muchas veces funcionas mejor actuando y corrigiendo sobre la marcha que esperando demasiado tiempo."
),

"Tauro": (
    "Con el Sol en Tauro, necesitas cierta estabilidad para sentirte bien con lo que construyes y con el ritmo de tu vida. "
    "Sueles valorar lo concreto, lo sencillo y aquello que puede sostenerse de forma real en el tiempo. "
    "Cuando algo te importa de verdad, normalmente puedes mantenerte con bastante constancia."
),

"Géminis": (
    "Con el Sol en Géminis, necesitas movimiento mental, estímulos y sensación de conexión con lo que ocurre alrededor. "
    "Sueles adaptarte bien a situaciones cambiantes y aprender con rápidez cuando algo despierta tu curiosidad. "
    "Las ideas, las conversaciones y la variedad suelen ser importantes para ti."
),

"Cáncer": (
    "Con el Sol en Cáncer, el vínculo, la cercanía y la sensación de confianza suelen tener mucha importancia para ti. "
    "Tiendes a percibir rápidamente cómo se encuentran las personas y el ambiente que te rodea. "
    "La capacidad de cuidar, sostener o acompañar suele aparecer de forma bastante natural."
),

"Leo": (
    "Con el Sol en Leo, necesitas espacios donde puedas expresarte, crear o mostrar lo que llevas dentro. "
    "Suele haber una necesidad natural de sentir reconocimiento o respuesta por parte del entorno. "
    "Cuando puedes expresarte con libertad, tu energía normalmente crece mucho."
),

"Virgo": (
    "Con el Sol en Virgo, tiendes a orientarte hacia lo que puede mejorarse, ordenarse o hacerse de forma más precisa. "
    "Sueles fijarte en los detalles y buscar utilidad en lo que haces. "
    "Tu energía suele activarse cuando hay algo concreto que entender, organizar o resolver."
),

"Libra": (
    "Con el Sol en Libra, las relaciones y el equilibrio con el entorno suelen ser importantes para ti. "
    "Tiendes a percibir rápidamente cómo afectan las situaciones a las personas implicadas. "
    "La capacidad de ajustar, mediar o buscar armonía suele aparecer de forma bastante natural."
),

"Escorpio": (
    "Con el Sol en Escorpio, suele haber una necesidad de profundidad, implicación real e intensidad emocional. "
    "No te resulta fácil permanecer mucho tiempo en situaciones que sientes vacías o superficiales. "
    "Cuando algo te importa de verdad, normalmente tiendes a implicarte profundamente."
),

"Sagitario": (
    "Con el Sol en Sagitario, necesitas sentir que lo que haces tiene dirección, sentido o posibilidad de crecimiento. "
    "Sueles funcionar mejor cuando hay movimiento, aprendizaje o apertura hacia algo nuevo. "
    "La capacidad de entusiasmarte y ampliar perspectivas suele aparecer de forma natural."
),

"Capricornio": (
    "Con el Sol en Capricornio, tiendes a construir tu vida de forma gradual, responsable y sostenida. "
    "Sueles valorar el esfuerzo, la experiencia y aquello que puede mantenerse de forma sólida en el tiempo. "
    "Tu energía puede parecer lenta al principio, pero normalmente gana fuerza con la constancia."
),

"Acuario": (
    "Con el Sol en Acuario, necesitas espacio para pensar a tu manera y mantener cierta independencia. "
    "Sueles ver posibilidades o enfoques distintos antes que muchas personas de tu entorno. "
    "La libertad y la autenticidad suelen ser especialmente importantes para ti."
),

"Piscis": (
    "Con el Sol en Piscis, suele haber una gran sensibilidad hacia el entorno y hacia lo que ocurre alrededor. "
    "Percibes matices, estados o necesidades que otras personas pueden pasar por alto. "
    "La empatía y la capacidad de conectar emocionalmente suelen ocupar un lugar importante en tu vida.."
),
}

# ─── TEXTOS: SOL POR CASA ──────────────────────────────────────────────────────

SOL_CASA = {
1: (
    "Con el Sol en Casa 1, tu forma de estar en el mundo suele percibirse de manera bastante directa. "
    "La iniciativa, la presencia y la necesidad de mostrarte de forma auténtica suelen tener mucha importancia para ti. "
    "Muchas veces necesitas sentir que puedes expresarte sin depender demasiado de lo que otras personas esperan."
),

2: (
    "Con el Sol en Casa 2, necesitas construir estabilidad y confianza a través de lo que haces, sostienes o desarrollas con tus propios recursos. "
    "Los recursos, los valores personales y la sensación de autonomía suelen tener bastante peso en tu vida. "
    "Muchas veces necesitas sentir que puedes apoyarte en algo sólido construido por ti."
),

3: (
    "Con el Sol en Casa 3, la comunicación, el aprendizaje y el intercambio con el entorno suelen ser especialmente importantes para ti. "
    "Pensar, hablar, preguntar o compartir ideas forma parte natural de cómo te orientas en la vida. "
    "Normalmente necesitas sentir movimiento mental y conexión con lo que ocurre alrededor."
),

4: (
    "Con el Sol en Casa 4, la intimidad, la sensación de hogar y la vida interior suelen tener mucho peso en tu desarrollo. "
    "Necesitas espacios donde puedas bajar la guardia y sentir cierta seguridad emocional. "
    "Muchas veces lo privado o lo emocional influye más en ti de lo que otras personas perciben desde fuera."
),

5: (
    "Con el Sol en Casa 5, la creatividad, la expresión personal y la necesidad de disfrutar lo que haces suelen ocupar un lugar importante en tu vida. "
    "Necesitas sentir que puedes crear, compartir o expresar algo propio. "
    "Cuando hay espacio para la autenticidad y el disfrute, sueles sentirte más vital."
),

6: (
    "Con el Sol en Casa 6, el trabajo cotidiano, los hábitos y la necesidad de sentir que lo que haces es útil suelen ser importantes para ti "
    "Tu energía normalmente se organiza mejor cuando hay cierta estructura o algo concreto de lo que ocuparte. "
    "Muchas veces cuidar tus ritmos y el día a día influye directamente en cómo te sientes."
),

7: (
    "Con el Sol en Casa 7, los vínculos y las relaciones suelen tener un peso importante en tu vida. "
    "Muchas veces conocerte mejor implica también verte a través del encuentro con otras personas. "
    "Las asociaciones y colaboraciones significativas suelen influir mucho en tu desarrollo."
),

8: (
    "Con el Sol en Casa 8, suele haber una necesidad de profundidad, intensidad e implicación emocional. "
    "Lo que vives como importante tiende a afectarte profundamente, aunque no siempre lo muestres hacia fuera. "
    "Muchas veces necesitas sentir conexión real para implicarte de verdad con algo o con alguien."
),

9: (
    "Con el Sol en Casa 9, necesitas sentir que tu vida se abre hacia nuevas perspectivas, aprendizajes o formas de comprender el mundo. "
    "Aprender, explorar o ampliar horizontes suele ayudarte a recuperar energía y dirección. "
    "Normalmente funcionas mejor cuando lo que haces tiene sentido para ti."
),

10: (
    "Con el Sol en Casa 10, la vocación, el reconocimiento y la construcción de algo visible suelen ocupar un lugar importante en tu vida. "
    "Necesitas sentir que lo que haces tiene coherencia con quién eres y hacia dónde quieres ir. "
    "Muchas veces el desarrollo profesional influye directamente en tu sensación de dirección y estabilidad."
),

11: (
    "Con el Sol en Casa 11, los grupos, amistades y proyectos compartidos suelen ocupar un lugar importante en tu vida. "
    "Muchas veces funcionas mejor cuando sientes conexión con personas, ideas o espacios con visión de futuro. "
    "Compartir intereses o formar parte de algo colectivo suele ser significativo para ti."
),

12: (
    "Con el Sol en Casa 12, gran parte de lo que ocurre dentro de ti suele vivirse de forma reservada o silenciosa. "
    "La vida interior, la introspección y los espacios de retirada pueden ser especialmente importantes para ti. "
    "Muchas veces necesitas momentos de soledad o distancia del ruido externo para sentirte realmente bien."
),
}

# ─── TEXTOS: LUNA POR SIGNO ───────────────────────────────────────────────────

LUNA_SIGNO = {
"Aries": (
    "Con la Luna en Aries, las emociones suelen aparecer de forma rápida y directa. "
    "Necesitas sentir espacio, movimiento y capacidad de actuar cuando algo te afecta. "
    "Muchas veces te ayuda más hacer algo con lo que sientes que quedarte demasiado tiempo dándole vueltas."
),

"Tauro": (
    "Con la Luna en Tauro, normalmente necesitas estabilidad, calma y cierta continuidad emocional para sentirte bien. "
    "Las emociones suelen asentarse despacio y no te resulta fácil cambiar rápidamente de estado interno. "
    "El contacto con lo conocido, lo sencillo o lo corporal suele ayudarte a recuperar equilibrio."
),

"Géminis": (
    "Con la Luna en Géminis, las emociones suelen pasar mucho por el pensamiento, la palabra y la necesidad de entender lo que ocurre. "
    "Hablar, preguntar o poner en palabras lo que sientes puede ayudarte bastante. "
    "Muchas veces necesitas movimiento mental y variedad para que tus emociones no se estanquen."
),

"Cáncer": (
    "Con la Luna en Cáncer, hay mucha sensibilidad hacia el entorno emocional y hacia las personas importantes para ti. "
    "La cercanía, el cuidado y la sensación de confianza suelen influir mucho en cómo te sientes. "
    "Cuando el ambiente es acogedor y seguro, normalmente te resulta más fácil relajarte y abrirte."
),

"Leo": (
    "Con la Luna en Leo, las emociones suelen expresarse de forma cálida, visible y bastante espontánea. "
    "Sentir aprecio, reconocimiento y atención por parte de los demás influye mucho en tu bienestar emocional. "
    "La creatividad, la expresión personal y los vínculos donde puedes mostrarte con libertad suelen ayudarte a sentirte bien."
),

"Virgo": (
    "Con la Luna en Virgo, tiendes a observar y analizar bastante cómo te encuentras emocionalmente. "
    "El orden, la claridad y la sensación de que las cosas funcionan te ayudan a recuperar tranquilidad. "
    "Muchas veces necesitas entender lo que ocurre para sentir estabilidad interna."
),

"Libra": (
    "Con la Luna en Libra, el equilibrio en las relaciones y en el entorno influye mucho en cómo te sientes. "
    "Sueles percibir rápidamente el clima emocional de las situaciones y de las personas cercanas. "
    "La armonía, el diálogo y los vínculos donde hay reciprocidad suelen ayudarte a recuperar bienestar."
),

"Escorpio": (
    "Con la Luna en Escorpio, las emociones suelen vivirse con bastante intensidad, aunque no siempre las muestres hacia fuera. "
    "Necesitas tiempo y confianza antes de abrirte del todo emocionalmente. "
    "Cuando algo te afecta de verdad, sueles vivirlo con profundidad."
),

"Sagitario": (
    "Con la Luna en Sagitario, necesitas espacio, movimiento y sensación de amplitud para sentirte bien emocionalmente. "
    "Sueles recuperar equilibrio cuando puedes cambiar de perspectiva, aprender algo nuevo o abrir horizontes. "
    "La sensación de crecimiento y dirección suele influir bastante en tu estado emocional."
),

"Capricornio": (
    "Con la Luna en Capricornio, tiendes a contener bastante lo que sientes antes de mostrarlo hacia fuera. "
    "La estabilidad, la responsabilidad y la sensación de construir algo sólido suelen darte seguridad emocional. "
    "Muchas veces necesitas tiempo antes de sentir suficiente confianza para mostrar vulnerabilidad."
),

"Acuario": (
    "Con la Luna en Acuario, necesitas cierta libertad emocional y espacio propio para sentirte bien. "
    "Cuando las emociones son demasiado intensas o invasivas, puedes necesitar cierta distancia para entender lo que te ocurre. "
    "Los vínculos donde hay respeto por la individualidad suelen ser especialmente importantes para ti."
),

"Piscis": (
    "Con la Luna en Piscis, suele haber mucha sensibilidad hacia el entorno y hacia lo que sienten otras personas. "
    "Percibes fácilmente matices emocionales que a veces pasan desapercibidos para quienes te rodean. "
    "Los espacios tranquilos, la conexión emocional y los momentos de descanso suelen ayudarte a recuperar equilibrio."
),
}

# ─── TEXTOS: LUNA POR CASA ────────────────────────────────────────────────────

LUNA_CASA = {
1: (
    "Con la Luna en Casa 1, las emociones suelen expresarse de forma bastante visible y directa. "
    "Muchas veces, lo que sientes se refleja rápidamente en tu forma de reaccionar, en el cuerpo o en tu manera de estar."
),

2: (
    "Con la Luna en Casa 2, la estabilidad y la sensación de seguridad suelen influir mucho en cómo te sientes emocionalmente. "
    "Los recursos, el cuerpo y aquello que puedes sostener de forma concreta suelen ocupar un lugar importante en tu vida."
),

3: (
    "Con la Luna en Casa 3, las emociones suelen procesarse a través de la palabra, el pensamiento o la necesidad de compartir lo que te ocurre. "
    "Hablar, escribir o entender mentalmente lo que sientes puede ayudarte bastante a encontrar claridad."
),

4: (
    "Con la Luna en Casa 4, la intimidad, el hogar y la sensación de protección emocional suelen ocupar un lugar muy importante en tu vida. "
    "El entorno cercano influye bastante en cómo te sientes y en tu capacidad de descansar realmente."
),

5: (
    "Con la Luna en Casa 5, la expresión emocional suele estar conectada con la creatividad, el disfrute y la necesidad de mostrar lo que sientes. "
    "Los espacios donde puedes expresarte con autenticidad suelen favorecer tu bienestar emocional."
),

6: (
    "Con la Luna en Casa 6, el cuerpo, los hábitos y el día a día suelen influir directamente en cómo te encuentras emocionalmente. "
    "Muchas veces, una rutina más ordenada o ciertos cuidados cotidianos te ayudan a sentirte mejor."
),

7: (
    "Con la Luna en Casa 7, los vínculos y las relaciones cercanas suelen influir mucho en tu mundo emocional. "
    "Las relaciones importantes suelen influir bastante en cómo te sientes y en la percepción que tienes de tu vida."
),

8: (
    "Con la Luna en Casa 8, las emociones suelen vivirse con bastante intensidad aunque no siempre se expresen fácilmente. "
    "Los vínculos profundos y lo que vives como significativo tienden a afectarte más de lo que otras personas perciben desde fuera."
),

9: (
    "Con la Luna en Casa 9, necesitas sentir cierta amplitud, dirección o sentido para encontrarte bien emocionalmente. "
    "Aprender, explorar o abrir nuevas perspectivas suele ayudarte bastante a recuperar equilibrio."
),

10: (
    "Con la Luna en Casa 10, la vocación, los objetivos y el reconocimiento suelen influir bastante en tu estado emocional. "
    "Muchas veces, tu vida profesional o la imagen que proyectas influyen de forma importante en cómo te sientes."
),

11: (
    "Con la Luna en Casa 11, las amistades, los grupos y la sensación de pertenecer a algo compartido suelen ocupar un lugar importante en tu mundo emocional. "
    "La conexión con personas o proyectos con visión de futuro suele influir mucho en tu bienestar."
),

12: (
    "Con la Luna en Casa 12, gran parte de lo que sientes suele vivirse de forma reservada o puede resultar difícil de expresar en el momento. "
    "Los espacios de silencio, descanso o retirada suelen ayudarte bastante a entender cómo te encuentras realmente."
),
}

# ─── TEXTOS: ASCENDENTE POR SIGNO ────────────────────────────────────────────

ASC_SIGNO = {
"Aries": (
    "Con Ascendente en Aries, sueles entrar en los entornos de forma directa, rápida y con bastante iniciativa. "
    "Las demás personas normalmente perciben una presencia activa y con energía desde el primer momento. "
    "Muchas veces necesitas sentir libertad para actuar a tu manera."
),

"Tauro": (
    "Con Ascendente en Tauro, normalmente transmites una sensación de calma, estabilidad y presencia tranquila. "
    "Sueles entrar en los entornos de forma gradual, observando antes de moverte demasiado rápido. "
    "Las demás personas suelen percibirte como alguien consistente y con un ritmo propio bastante claro."
),

"Géminis": (
    "Con Ascendente en Géminis, sueles mostrarte de forma curiosa, comunicativa y mentalmente ágil. "
    "Tiendes a conectar rápido con el entorno a través de la conversación, las ideas o las preguntas. "
    "Las demás personas suelen percibir bastante movimiento y flexibilidad en tu forma de entrar en contacto."
),

"Cáncer": (
    "Con Ascendente en Cáncer, normalmente te muestras de forma receptiva, sensible y bastante atenta al entorno. "
    "Sueles observar primero cómo es el ambiente antes de abrirte del todo. "
    "Las demás personas pueden percibir cierta suavidad o reserva en el primer contacto."
),

"Leo": (
    "Con Ascendente en Leo, normalmente transmites presencia, calidez y cierta seguridad natural al entrar en los entornos. "
    "Las demás personas suelen notar rápidamente tu forma de expresarte o de ocupar el espacio. "
    "Muchas veces necesitas sentir que puedes mostrarte de forma auténtica y visible."
),

"Virgo": (
    "Con Ascendente en Virgo, sueles mostrarte de forma observadora, discreta y bastante atenta a los detalles. "
    "Normalmente analizas primero el entorno antes de participar del todo. "
    "Las demás personas suelen percibir una actitud cuidadosa y reservada en el primer contacto."
),

"Libra": (
    "Con Ascendente en Libra, normalmente te muestras de forma amable, diplomática y orientada al vínculo con otras personas. "
    "Sueles percibir rápidamente cómo relacionarte con cada entorno o situación. "
    "Las demás personas suelen sentir facilidad y armonía en el primer contacto contigo."
),

"Escorpio": (
    "Con Ascendente en Escorpio, normalmente transmites una presencia intensa, reservada o difícil de leer al principio. "
    "Sueles observar bastante antes de mostrarte con naturalidad. "
    "Las demás personas pueden percibir profundidad o cierta distancia en el primer contacto."
),

"Sagitario": (
    "Con Ascendente en Sagitario, normalmente te muestras de forma abierta, espontánea y bastante directa. "
    "Sueles entrar en los entornos con energía, entusiasmo o sensación de movimiento. "
    "Las demás personas suelen percibir facilidad para conectar y amplitud en tu forma de relacionarte."
),

"Capricornio": (
    "Con Ascendente en Capricornio, normalmente transmites una imagen seria, contenida y bastante responsable. "
    "Sueles entrar en los entornos con prudencia y observación antes de mostrarte del todo. "
    "Las demás personas suelen percibir solidez y cierta sensación de capacidad desde el principio."
),

"Acuario": (
    "Con Ascendente en Acuario, normalmente te muestras de forma independiente, observadora y algo difícil de encajar en lo esperado. "
    "Sueles necesitar espacio y libertad para sentirte con comodidad en los entornos nuevos. "
    "Las demás personas pueden percibir cierta distancia o una forma distinta de estar y relacionarte."
),

"Piscis": (
    "Con Ascendente en Piscis, normalmente transmites sensibilidad, adaptabilidad y bastante percepción del entorno. "
    "Sueles captar primero el ambiente antes de decidir cómo actuar o mostrarte. "
    "Las demás personas suelen percibir una presencia suave, empática o difícil de definir rápidamente."
),
}

DINAMICA_GENERAL = {
"mucho_fuego": (
    "En tu carta aparece bastante energía de acción, iniciativa y necesidad de movimiento. "
    "Sueles responder mejor cuando puedes avanzar, decidir o sentir que algo se pone en marcha."
),

"mucho_tierra": (
    "En tu carta hay una necesidad importante de estabilidad, estructura y concreción. "
    "Normalmente te ayuda sentir que las cosas tienen una base clara y pueden sostenerse de forma real en el tiempo."
),

"mucho_aire": (
    "En tu carta aparece bastante movimiento mental, necesidad de comprender y conexión con el entorno. "
    "Las ideas, las conversaciones y la sensación de circulación suelen tener bastante importancia para ti."
),

"mucha_agua": (
    "En tu carta hay bastante sensibilidad emocional y percepción del entorno. "
    "Muchas veces lo que ocurre alrededor influye más en ti de lo que se percibe desde fuera."
),

"predominio_cardinal": (
    "Suele haber bastante iniciativa y necesidad de movimiento. "
    "Muchas veces te resulta más fácil empezar algo que permanecer demasiado tiempo en la espera o la indefinición."
),

"predominio_fijo": (
    "En tu carta aparece bastante necesidad de estabilidad y continuidad. "
    "Cuando algo tiene sentido para ti, normalmente puedes sostenerlo con constancia."
),

"predominio_mutable": (
    "En tu carta hay bastante capacidad de adaptación y movimiento entre distintos registros o situaciones. "
    "Muchas veces necesitas variedad, flexibilidad o sensación de cambio para sentirte activo."
),

"energia_equilibrada": (
    "Tu carta combina distintos elementos y formas de funcionamiento sin que uno domine claramente sobre los demás. "
    "Eso puede darte bastante flexibilidad para adaptarte a situaciones diferentes según el momento."
),

"fuego_y_agua": (
    "En tu carta conviven impulso emocional y sensibilidad. "
    "Puede haber momentos de mucha intensidad interna junto a necesidad de actuar o responder rápidamente."
),

"aire_y_tierra": (
    "En tu carta aparece una combinación entre análisis y necesidad de concreción. "
    "Sueles necesitar entender las cosas, pero también sentir que pueden aplicarse de forma práctica."
),

"agua_y_tierra": (
    "En tu carta aparece una combinación importante entre sensibilidad y necesidad de estabilidad. "
    "Muchas veces necesitas sentir seguridad emocional y cierta base clara para poder relajarte de verdad."
),

"fuego_y_aire": (
    "En tu carta aparece bastante movimiento, iniciativa y necesidad de estímulo. "
    "Las ideas nuevas, los proyectos y la sensación de avance suelen activar mucho tu energía."
),
}

TEXTOS_ELEMENTOS_PDF = {
"Aire": {
    "alto": (
        "El Aire representa la forma de pensar, comunicar y establecer conexiones entre ideas. "
        "Cuando tiene mucha presencia, suele aportar curiosidad, capacidad de análisis y facilidad "
        "para comprender distintas perspectivas.<br/><br/>"
        "En algunos momentos, esa actividad mental puede hacer que dediques mucho tiempo a pensar, "
        "analizar o anticipar posibilidades antes de pasar a la acción.<br/><br/>"
        "<b>Observa:</b><br/>"
        "• cuándo pensar te ayuda a comprender y cuándo empieza a alejarte de lo que estás viviendo<br/>"
        "• cómo equilibras reflexión y acción<br/>"
        "• qué espacios permiten que tu mente también pueda descansar"
    ),

    "equilibrado": (
        "El Aire representa la capacidad de comprender, comunicar y relacionar ideas. "
        "Con una presencia equilibrada, suele existir facilidad para reflexionar, intercambiar "
        "puntos de vista y adaptarte a nuevas formas de comprender la realidad.<br/><br/>"
        "Puedes utilizar el pensamiento como una herramienta útil sin que llegue a ocupar todo "
        "el espacio de tu vida.<br/><br/>"
        "<b>Observa:</b><br/>"
        "• cómo integras lo que piensas con lo que sientes<br/>"
        "• qué conversaciones enriquecen realmente tu visión<br/>"
        "• cuándo una explicación deja paso a vivir las cosas directamente"
    ),

    "bajo": (
        "El Aire representa la forma de pensar, comunicar y organizar las ideas. "
        "Cuando aparece con menor presencia, es posible que prefieras comprender las cosas "
        "desde la experiencia directa antes que desde el análisis continuo.<br/><br/>"
        "Esto no significa falta de capacidad intelectual ni dificultad para comunicarte. "
        "Simplemente puede indicar que tu forma de entender el mundo nace más de lo vivido "
        "que de darle muchas vueltas a una idea.<br/><br/>"
        "<b>Observa:</b><br/>"
        "• qué situaciones te ayudan a expresar con claridad lo que piensas<br/>"
        "• cuándo merece la pena detenerse a reflexionar un poco más<br/>"
        "• cómo encuentras equilibrio entre experiencia y comprensión"
    ),
},

"Tierra": {
    "alto": (
        "La Tierra representa la capacidad de concretar, organizar y dar continuidad "
        "a lo que construyes. Cuando tiene mucha presencia, suele aportar sentido práctico, "
        "constancia y necesidad de contar con una base estable.<br/><br/>"
        "En algunos momentos, esa búsqueda de seguridad puede llevarte a mantener demasiado "
        "control, exigirte más de lo necesario o sentir incomodidad ante los cambios imprevistos.<br/><br/>"
        "<b>Observa:</b><br/>"
        "• qué estructuras te ayudan realmente a sentir estabilidad<br/>"
        "• cuándo la organización se convierte en rigidez<br/>"
        "• si puedes adaptarte sin sentir que pierdes tu base"
    ),

    "equilibrado": (
        "La Tierra representa la capacidad de concretar, organizar y sostener procesos "
        "en el tiempo. Con una presencia equilibrada, puedes apoyarte en lo práctico "
        "sin necesitar que todo permanezca siempre igual.<br/><br/>"
        "Suele existir una relación bastante flexible entre estructura y adaptación: "
        "puedes mantener lo que funciona y modificarlo cuando deja de ser útil.<br/><br/>"
        "<b>Observa:</b><br/>"
        "• qué te ayuda a dar continuidad a lo que empiezas<br/>"
        "• cuándo una estructura sigue sosteniéndote y cuándo empieza a limitarte<br/>"
        "• cómo encuentras equilibrio entre estabilidad y cambio"
    ),

    "bajo": (
        "La Tierra representa la capacidad de concretar, organizar y sostener procesos "
        "en el tiempo. Cuando aparece con menor presencia, la estructura puede no surgir "
        "de forma automática y quizá necesite construirse de manera más consciente.<br/><br/>"
        "Esto no significa falta de responsabilidad ni incapacidad para mantener compromisos. "
        "Indica que los ritmos, los hábitos y las referencias concretas suelen funcionar mejor "
        "cuando los eliges y los adaptas a tu forma real de vivir.<br/><br/>"
        "<b>Observa:</b><br/>"
        "• qué te ayuda a mantener continuidad sin sentirte limitada<br/>"
        "• cuándo una idea necesita convertirse en un paso concreto<br/>"
        "• qué estructuras te sostienen sin volverse rígidas"
    ),
},

"Agua": {
    "alto": (
        "El Agua representa la sensibilidad, la percepción emocional y la capacidad "
        "de conectar con lo que ocurre dentro de ti y a tu alrededor. Cuando tiene mucha "
        "presencia, suele aportar intuición, profundidad y una gran receptividad.<br/><br/>"
        "En algunos momentos, esa apertura puede hacer que vivas ciertas experiencias con mucha "
        "intensidad, que te cueste tomar distancia o que absorbas con facilidad el clima emocional "
        "de otras personas y situaciones.<br/><br/>"
        "<b>Observa:</b><br/>"
        "• qué emociones son realmente tuyas y cuáles pueden venir del entorno<br/>"
        "• cuándo necesitas retirarte para recuperar claridad<br/>"
        "• qué te ayuda a sentir sin quedarte atrapada en lo que sientes"
    ),

    "equilibrado": (
        "El Agua representa la sensibilidad, la percepción emocional y la capacidad "
        "de conectar con lo que ocurre dentro de ti y a tu alrededor. Con una presencia "
        "equilibrada, puedes registrar lo emocional sin que ocupe necesariamente todo el espacio.<br/><br/>"
        "Suele existir una buena capacidad para sentir, comprender lo que te afecta y recuperar "
        "perspectiva cuando lo necesitas.<br/><br/>"
        "<b>Observa:</b><br/>"
        "• cómo reconoces lo que estás sintiendo<br/>"
        "• cuándo necesitas cercanía y cuándo necesitas distancia<br/>"
        "• qué te ayuda a volver a un estado de mayor calma"
    ),

    "bajo": (
        "El Agua representa la sensibilidad, la percepción emocional y la capacidad "
        "de conectar con lo que ocurre dentro de ti y a tu alrededor. Cuando aparece con "
        "menor presencia, lo emocional puede necesitar más tiempo o más espacio para hacerse visible.<br/><br/>"
        "Esto no significa falta de sensibilidad. Puede indicar que tiendes a procesar primero "
        "desde otros registros y que reconocer o expresar lo que sientes requiere una atención "
        "más consciente.<br/><br/>"
        "<b>Observa:</b><br/>"
        "• qué situaciones te ayudan a conectar con lo que sientes<br/>"
        "• si necesitas tiempo antes de poder poner nombre a una emoción<br/>"
        "• cómo puedes dar espacio a lo emocional sin sentirte invadida"
    ),
},

"Fuego": {
    "alto": (
        "El Fuego representa el impulso para iniciar, actuar y avanzar hacia aquello que resulta "
        "significativo. Cuando tiene mucha presencia, suele aportar entusiasmo, iniciativa y facilidad "
        "para movilizar energía.<br/><br/>"
        "En algunos momentos, ese impulso puede llevarte a querer avanzar antes de que todo esté preparado "
        "o a perder interés cuando desaparece la sensación de novedad.<br/><br/>"
        "<b>Observa:</b><br/>"
        "• qué proyectos mantienen viva tu motivación a largo plazo<br/>"
        "• cuándo merece la pena detenerse antes de actuar<br/>"
        "• cómo sostienes el impulso inicial a lo largo del tiempo"
    ),

    "equilibrado": (
        "El Fuego representa la capacidad de iniciar, movilizar recursos y responder a los desafíos. "
        "Con una presencia equilibrada, suele existir una buena combinación entre iniciativa y capacidad "
        "para valorar el momento adecuado para actuar.<br/><br/>"
        "Puedes ilusionarte con nuevos proyectos sin necesidad de vivir en un estado constante de acción, "
        "alternando movimiento y pausa cuando la situación lo requiere.<br/><br/>"
        "<b>Observa:</b><br/>"
        "• qué alimenta tu motivación de forma sostenida<br/>"
        "• cómo equilibras entusiasmo y constancia<br/>"
        "• cuándo actuar y cuándo esperar resulta igual de valioso"
    ),

    "bajo": (
        "El Fuego representa el impulso para iniciar, actuar y avanzar hacia lo que deseas. "
        "Cuando aparece con menor presencia, la motivación puede necesitar más tiempo para activarse "
        "o surgir con mayor claridad cuando existe un propósito que realmente te conecta.<br/><br/>"
        "Esto no significa falta de energía ni de capacidad para emprender proyectos. Puede indicar que "
        "tu impulso no siempre aparece de manera inmediata y que necesitas encontrar un sentido profundo "
        "antes de ponerte en marcha.<br/><br/>"
        "<b>Observa:</b><br/>"
        "• qué despierta realmente tus ganas de actuar<br/>"
        "• cómo puedes favorecer el inicio de aquello que es importante para ti<br/>"
        "• qué diferencia existe entre esperar el momento adecuado y posponer indefinidamente"
    ),
},

}

# ─── FUNCIONES DE CÁLCULO ────────────────────────────────────────────────────

import time
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut


def geocodificar(ciudad):

    geolocator = Nominatim(
        user_agent="arquitectura_interna_astrologia_2026",
        timeout=20
    )

    for intento in range(5):

        try:

            print(f"Intento geocodificación {intento + 1}...")

            location = geolocator.geocode(
                ciudad,
                language="es",
                exactly_one=True
            )

            if location:

                print("Lugar encontrado:")
                print(location.address)

                return location.latitude, location.longitude

        except GeocoderTimedOut:

            print("Timeout. Reintentando...")
            time.sleep(3)

        except Exception as e:

            print("Error geocodificación:", e)
            time.sleep(3)

    raise ValueError(f"No se pudo encontrar: {ciudad}")

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

    return (
        SIGNOS[idx % 12],
        lon - idx * 30
    )


def grado_a_dms(grado):
    d = int(grado)
    m = int(round((grado - d) * 60))

    if m == 60:
        d += 1
        m = 0

    return f"{d}°{m:02d}'"

def _chiron_kepler(jd):
    jd_peri, period, e, peri_lon = 2450128.5, 18412.3, 0.383, 188.76

    M = math.radians(
        ((jd - jd_peri) / period * 360.0) % 360.0
    )

    E = M

    for _ in range(50):
        dE = (
            (M - E + e * math.sin(E))
            / (1.0 - e * math.cos(E))
        )

        E += dE

        if abs(dE) < 1e-10:
            break

    f = 2.0 * math.atan(
        math.sqrt((1 + e) / (1 - e))
        * math.tan(E / 2.0)
    )

    return (math.degrees(f) + peri_lon) % 360.0


def calcular_carta(año, mes, dia, hora, minuto, lat, lon, tz_name):

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    EPHE_PATH = os.path.join(BASE_DIR, "ephe")

    swe.set_ephe_path(EPHE_PATH)

    FLAGS = swe.FLG_SWIEPH | swe.FLG_SPEED

    jd = fecha_a_jd(
        año, mes, dia,
        hora, minuto,
        tz_name
    )

    planetas = {}

    # ─── PLANETAS PRINCIPALES ───────────────────────────────────────────────
    for pid, nombre, simbolo in PLANETAS_IDS:
        pos, _ = swe.calc_ut(jd, pid, FLAGS)

        signo, grado = grados_a_signo(pos[0])

        planetas[nombre] = {
            "simbolo": simbolo,
            "lon": pos[0],
            "signo": signo,
            "grado": grado,
            "retrogrado": pos[3] < 0
        }

    # ─── QUIRÓN ──────────────────────────────────────────────────────────────
    try:
        pos_ch, _ = swe.calc_ut(jd, CHIRON_ID, FLAGS)

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

    # ─── LILITH ──────────────────────────────────────────────────────────────
    pos_li, _ = swe.calc_ut(jd, LILITH_ID, FLAGS)
    signo_li, grado_li = grados_a_signo(pos_li[0])

    planetas["Lilith"] = {
        "simbolo": "⚸",
        "lon": pos_li[0],
        "signo": signo_li,
        "grado": grado_li,
        "retrogrado": False
    }

    # ─── NODOS ───────────────────────────────────────────────────────────────
    pos_nn, _ = swe.calc_ut(jd, swe.TRUE_NODE, FLAGS)

    signo_nn, grado_nn = grados_a_signo(pos_nn[0])
    lon_ns = (pos_nn[0] + 180) % 360
    signo_ns, grado_ns = grados_a_signo(lon_ns)

    planetas["Nodo Norte"] = {
        "simbolo": "☊",
        "lon": pos_nn[0],
        "signo": signo_nn,
        "grado": grado_nn,
        "retrogrado": False
    }

    planetas["Nodo Sur"] = {
        "simbolo": "☋",
        "lon": lon_ns,
        "signo": signo_ns,
        "grado": grado_ns,
        "retrogrado": False
    }

    # ─── CASAS PLACIDUS ──────────────────────────────────────────────────────
    cuspides, ascmc = swe.houses(jd, lat, lon, b'P')

    asc_lon = ascmc[0]
    mc_lon  = ascmc[1]
    armc    = ascmc[2]

    signo_asc, grado_asc = grados_a_signo(asc_lon)
    signo_mc, grado_mc   = grados_a_signo(mc_lon)

    # Oblicuidad verdadera
    eps_data, _ = swe.calc_ut(jd, swe.ECL_NUT)
    eps = eps_data[0]

    def casa_de(p_lon):
        """
        Calcula la casa usando Swiss Ephemeris.
        Evita errores cerca del Ascendente/Descendente
        y en cartas con casas desiguales.
        """

        hpos = swe.house_pos(
            armc,
            lat,
            eps,
            (p_lon, 0.0),
            b'P'
        )

        return int(hpos)

    for nombre in planetas:
        planetas[nombre]["casa"] = casa_de(planetas[nombre]["lon"])



    return {
        "planetas": planetas,
        "cuspides": list(cuspides),
        "asc": {
            "lon": asc_lon,
            "signo": signo_asc,
            "grado": grado_asc
        },
        "mc": {
            "lon": mc_lon,
            "signo": signo_mc,
            "grado": grado_mc
        },
        "jd": jd,
    }


# ─────────────────────────────────────────────────────────────
# RUEDA ASTROLÓGICA
# ─────────────────────────────────────────────────────────────

def dibujar_rueda(carta, nombre_persona, archivo_salida):

    fig, ax = plt.subplots(1, 1, figsize=(12, 12))

    ax.set_aspect('equal')
    ax.axis('off')

    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)

    R_EXT      = 1.35
    R_SIGNO    = 1.20
    R_SIGN_IN  = 1.05

    R_CASA_OUT = 1.02
    R_CASA_IN  = 0.65

    R_PLANETA  = 0.82

    asc_lon = carta["asc"]["lon"]

    def lon_a_angulo(lon):
        return math.radians(
            180 + (lon - asc_lon)
        )

    # ─── ANILLO DE SIGNOS ───────────────────────────────────────────────────

    for i, signo in enumerate(SIGNOS):

        elem  = ELEMENTO_SIGNO[signo]
        color = COLORES_ELEMENTO[elem]

        ang_ini = lon_a_angulo(i * 30)
        ang_fin = lon_a_angulo((i + 1) * 30)

        theta = np.linspace(ang_ini, ang_fin, 50)

        xs = (
            [math.cos(a) * R_EXT for a in theta]
            + [math.cos(a) * R_SIGN_IN for a in reversed(theta)]
        )

        ys = (
            [math.sin(a) * R_EXT for a in theta]
            + [math.sin(a) * R_SIGN_IN for a in reversed(theta)]
        )

        ax.fill(
            xs,
            ys,
            color=color,
            alpha=0.35,
            zorder=1
        )

    # ─── CÍRCULOS PRINCIPALES ───────────────────────────────────────────────

    for r, lw, c in [
        (R_EXT, 2, '#333'),
        (R_SIGN_IN, 1.5, '#333'),
        (R_CASA_IN, 1.5, '#555'),
        (0.25, 1, '#888')
    ]:

        ax.add_patch(
            plt.Circle(
                (0, 0),
                r,
                fill=False,
                color=c,
                linewidth=lw,
                zorder=2
            )
        )

    # ─── DIVISIONES DE SIGNOS ───────────────────────────────────────────────

    for i in range(12):

        ang = lon_a_angulo(i * 30)

        ax.plot(
            [math.cos(ang) * R_SIGN_IN, math.cos(ang) * R_EXT],
            [math.sin(ang) * R_SIGN_IN, math.sin(ang) * R_EXT],
            color='#555',
            linewidth=0.8,
            zorder=2
        )

    # ─── SÍMBOLOS DE SIGNOS ─────────────────────────────────────────────────

    for i, (signo, simbolo) in enumerate(zip(SIGNOS, SIMBOLOS_SIGNOS)):

        ang_mid = lon_a_angulo(i * 30 + 15)

        r_mid = (R_SIGN_IN + R_EXT) / 2

        elem = ELEMENTO_SIGNO[signo]

        ax.text(
            math.cos(ang_mid) * r_mid,
            math.sin(ang_mid) * r_mid,
            simbolo,
            ha='center',
            va='center',
            fontsize=20,
            color=COLORES_ELEMENTO[elem],
            fontweight='bold',
            zorder=5
        )

    # ─── MARCAS DE GRADOS ───────────────────────────────────────────────────

    for deg in range(360):

        if deg % 30 == 0:
            continue

        ang = lon_a_angulo(deg)

        if deg % 10 == 0:
            r_in, lw = R_SIGN_IN - 0.055, 1.0

        elif deg % 5 == 0:
            r_in, lw = R_SIGN_IN - 0.035, 0.7

        else:
            r_in, lw = R_SIGN_IN - 0.018, 0.4

        ax.plot(
            [math.cos(ang) * R_SIGN_IN, math.cos(ang) * r_in],
            [math.sin(ang) * R_SIGN_IN, math.sin(ang) * r_in],
            color='#555',
            linewidth=lw,
            zorder=2
        )

    # ─── CASAS ──────────────────────────────────────────────────────────────

    cuspides = carta["cuspides"]

    for i, cusp in enumerate(cuspides):

        ang = lon_a_angulo(cusp)

        lw  = 2.0 if i in (0, 3, 6, 9) else 0.8
        col = '#111' if i in (0, 3, 6, 9) else '#666'

        ax.plot(
            [math.cos(ang) * R_CASA_IN, math.cos(ang) * R_CASA_OUT],
            [math.sin(ang) * R_CASA_IN, math.sin(ang) * R_CASA_OUT],
            color=col,
            linewidth=lw,
            zorder=3
        )

        ang_num = lon_a_angulo(cusp + 4.0)

        r_num = (R_CASA_IN + 0.25) / 2 + 0.12

        ax.text(
            math.cos(ang_num) * r_num,
            math.sin(ang_num) * r_num,
            str(i + 1),
            ha='center',
            va='center',
            fontsize=7,
            color='#444',
            zorder=4
        )

    # ─── PLANETAS ───────────────────────────────────────────────────────────

    orden = [
        "Sol","Luna","Mercurio","Venus","Marte","Júpiter","Saturno",
        "Urano","Neptuno","Plutón","Quirón","Lilith","Nodo Norte","Nodo Sur"
    ]

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

                radio = max(
                    RADIO_MIN,
                    min(candidato, RADIO_MAX)
                )

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

        simbolo = p["simbolo"] + (
            "ᴿ" if p.get("retrogrado") else ""
        )

        ax.text(
            math.cos(ang) * r,
            math.sin(ang) * r,
            simbolo,
            ha="center",
            va="center",
            fontsize=17,
            color=color,
            fontweight="bold",
            zorder=6
        )

        # Línea hacia casas

        ax.plot(
            [math.cos(ang) * (r - 0.07), math.cos(ang) * (R_CASA_IN - 0.02)],
            [math.sin(ang) * (r - 0.07), math.sin(ang) * (R_CASA_IN - 0.02)],
            color=color,
            linewidth=0.5,
            alpha=0.5,
            zorder=3
        )

        # Línea hacia signos

        ax.plot(
            [math.cos(ang) * (r + 0.07), math.cos(ang) * (R_SIGN_IN + 0.01)],
            [math.sin(ang) * (r + 0.07), math.sin(ang) * (R_SIGN_IN + 0.01)],
            color=color,
            linewidth=0.8,
            alpha=0.8,
            zorder=3
        )

    # ─── EJES ───────────────────────────────────────────────────────────────

    for etiqueta, lon_pt in [
        ("AC", carta["asc"]["lon"]),
        ("DC", (carta["asc"]["lon"] + 180) % 360),
        ("MC", carta["mc"]["lon"]),
        ("IC", (carta["mc"]["lon"] + 180) % 360)
    ]:

        ang = lon_a_angulo(lon_pt)

        ax.text(
            math.cos(ang) * (R_EXT + 0.09),
            math.sin(ang) * (R_EXT + 0.09),
            etiqueta,
            ha="center",
            va="center",
            fontsize=13,
            fontweight="bold",
            color="#111",
            zorder=7
        )

    # ─── NOMBRE CENTRAL ─────────────────────────────────────────────────────

    ax.text(
        0,
        0,
        nombre_persona.replace(" ", "\n"),
        ha="center",
        va="center",
        fontsize=8,
        color="#333",
        style="italic",
        zorder=7
    )

    # ─── GUARDAR IMAGEN ─────────────────────────────────────────────────────

    ax.set_title("")
    fig.suptitle("")

    plt.tight_layout()

    plt.savefig(
        archivo_salida,
        dpi=150,
        bbox_inches="tight",
        facecolor="white",
        edgecolor="none"
    )

    plt.close(fig)


# ─────────────────────────────────────────────────────────────
# ANÁLISIS ASTROLÓGICO
# ─────────────────────────────────────────────────────────────

# ─── ANÁLISIS DE ELEMENTOS Y MODALIDADES ─────────────────────────────────────

_REGENTE_ASC = {
    "Aries":"Marte","Tauro":"Venus","Géminis":"Mercurio","Cáncer":"Luna",
    "Leo":"Sol","Virgo":"Mercurio","Libra":"Venus","Escorpio":"Plutón",
    "Sagitario":"Júpiter","Capricornio":"Saturno","Acuario":"Urano","Piscis":"Neptuno",
}

def analizar_elementos(planetas, asc_signo, hora_conocida=True):
    PESOS = {
        "Sol":2,"Luna":2,
        "Mercurio":1.5,"Venus":1.5,"Marte":1.5,
        "Júpiter":1,"Saturno":1,"Urano":1,"Neptuno":1,"Plutón":1,
    }

    conteo = {"Fuego":0.0,"Tierra":0.0,"Aire":0.0,"Agua":0.0}

    for nombre, peso in PESOS.items():
        if nombre in planetas:
            e = ELEMENTO_SIGNO.get(planetas[nombre]["signo"], "")
            if e:
                conteo[e] += peso

    if hora_conocida:
        e_asc = ELEMENTO_SIGNO.get(asc_signo, "")
        if e_asc:
            conteo[e_asc] += 2

        regente = _REGENTE_ASC.get(asc_signo, "")
        if regente and regente in planetas:
            e_reg = ELEMENTO_SIGNO.get(planetas[regente]["signo"], "")
            if e_reg:
                conteo[e_reg] += 1

    return conteo


def analizar_modalidades(planetas):
    conteo = {"Cardinal":0,"Fija":0,"Mutable":0}

    for nombre in ["Sol","Luna","Mercurio","Venus","Marte","Júpiter","Saturno"]:
        if nombre in planetas:
            m = MODALIDAD_SIGNO.get(planetas[nombre]["signo"], "")
            if m:
                conteo[m] += 1

    return conteo


def _desc_elemento(elem):
    return {
        "Fuego": "iniciativa, impulso y necesidad de movimiento",
        "Tierra": "estabilidad, concreción y contacto con lo práctico",
        "Aire": "pensamiento, comunicación y necesidad de perspectiva",
        "Agua": "sensibilidad, percepción emocional y conexión con el entorno",
    }.get(elem, "")


MC_SIGNO = {
"Aries": "iniciativa, autonomía y capacidad para abrir camino.",
"Tauro": "constancia, estabilidad y construcción gradual.",
"Géminis": "comunicación, aprendizaje e intercambio de ideas.",
"Cáncer": "cuidado, sensibilidad y atención a las necesidades humanas.",
"Leo": "creatividad, expresión y presencia visible.",
"Virgo": "precisión, organización y mejora continua.",
"Libra": "equilibrio, mediación y capacidad de relación.",
"Escorpio": "profundidad, intensidad y manejo de situaciones complejas.",
"Sagitario": "visión, aprendizaje y apertura de horizontes.",
"Capricornio": "responsabilidad, estructura y construcción a largo plazo.",
"Acuario": "independencia, innovación y mirada diferente.",
"Piscis": "sensibilidad, imaginación y capacidad de adaptación.",
}

def texto_apertura(conteo_elem):

    orden = sorted(
        conteo_elem.items(),
        key=lambda x: -x[1]
    )

    dominante = orden[0][0]

    return (
        "Toda carta tiene una forma particular de organizar la energía.<br/><br/>"
        "En la tuya aparece una manera muy concreta de responder a la vida, de iniciar los procesos y de relacionarte con lo que ocurre alrededor.<br/><br/>"
        "Lo que vas a leer a continuación no pretende definir quién eres. "
        "Pretende ofrecer una primera mirada sobre aquello que parece organizar el conjunto de tu carta."
    )


def texto_vision_general(carta, conteo_elem, conteo_modal):

    ordenado = sorted(
        conteo_elem.items(),
        key=lambda x: -x[1]
    )

    elementos_altos = [
        elemento
        for elemento, valor in ordenado
        if valor >= 5.5
    ]

    elementos_bajos = [
        elemento
        for elemento, valor in ordenado
        if valor <= 2.0
    ]

    modal_max = max(
        conteo_modal,
        key=conteo_modal.get
    )

    mc_signo = carta["mc"]["signo"]

    parrafos = []

    parrafos.append(
        "Si tuviéramos que resumir tu carta en unas pocas ideas, "
        "probablemente empezaríamos por aquí."
    )

    if len(elementos_altos) >= 2:

        elemento_1 = elementos_altos[0]
        elemento_2 = elementos_altos[1]

        parrafos.append(
            f"En ella aparecen dos fuerzas especialmente presentes: "
            f"<b>{elemento_1}</b> y <b>{elemento_2}</b>."
        )

        combinaciones = {
            ("Fuego", "Agua"): (
                "El Fuego impulsa a actuar, iniciar y avanzar. "
                "El Agua percibe, siente y conecta profundamente con lo que ocurre "
                "dentro y fuera de ti. Cuando ambas energías trabajan juntas, "
                "pueden dar lugar a una gran capacidad para implicarte con intensidad "
                "en aquello que consideras importante. Pero también pueden hacer que "
                "algunas experiencias se vivan con mucha fuerza y necesiten más tiempo "
                "para integrarse."
            ),
            ("Agua", "Fuego"): (
                "El Agua percibe, siente y conecta profundamente con lo que ocurre "
                "dentro y fuera de ti. El Fuego impulsa a actuar, iniciar y avanzar. "
                "Cuando ambas energías trabajan juntas, pueden dar lugar a una gran "
                "capacidad para implicarte con intensidad en aquello que consideras "
                "importante. Pero también pueden hacer que algunas experiencias se "
                "vivan con mucha fuerza y necesiten más tiempo para integrarse."
            ),
            ("Fuego", "Aire"): (
                "El Fuego impulsa a actuar, iniciar y avanzar. "
                "El Aire aporta ideas, perspectiva y necesidad de comprender. "
                "Cuando ambas energías trabajan juntas, suelen generar rapidez, "
                "curiosidad y capacidad para poner en marcha posibilidades nuevas."
            ),
            ("Aire", "Fuego"): (
                "El Aire aporta ideas, perspectiva y necesidad de comprender. "
                "El Fuego impulsa a actuar, iniciar y avanzar. "
                "Cuando ambas energías trabajan juntas, suelen generar rapidez, "
                "curiosidad y capacidad para poner en marcha posibilidades nuevas."
            ),
            ("Agua", "Tierra"): (
                "El Agua aporta sensibilidad y percepción emocional. "
                "La Tierra busca estabilidad, concreción y continuidad. "
                "Cuando ambas energías trabajan juntas, puede existir una gran "
                "capacidad para cuidar, sostener y dar forma concreta a aquello "
                "que tiene valor emocional."
            ),
            ("Tierra", "Agua"): (
                "La Tierra busca estabilidad, concreción y continuidad. "
                "El Agua aporta sensibilidad y percepción emocional. "
                "Cuando ambas energías trabajan juntas, puede existir una gran "
                "capacidad para cuidar, sostener y dar forma concreta a aquello "
                "que tiene valor emocional."
            ),
            ("Aire", "Tierra"): (
                "El Aire aporta ideas, análisis y perspectiva. "
                "La Tierra busca concreción, estabilidad y resultados que puedan "
                "sostenerse en el tiempo. Cuando ambas energías trabajan juntas, "
                "pueden facilitar una buena relación entre pensamiento y aplicación práctica."
            ),
            ("Tierra", "Aire"): (
                "La Tierra busca concreción, estabilidad y resultados que puedan "
                "sostenerse en el tiempo. El Aire aporta ideas, análisis y perspectiva. "
                "Cuando ambas energías trabajan juntas, pueden facilitar una buena "
                "relación entre pensamiento y aplicación práctica."
            ),
        }

        parrafos.append(
            combinaciones.get(
                (elemento_1, elemento_2),
                (
                    f"{elemento_1} y {elemento_2} aparecen con bastante presencia. "
                    "La manera en que ambas energías se relacionan forma parte importante "
                    "de tu forma de responder a la vida."
                )
            )
        )

    elif len(elementos_altos) == 1:

        elemento = elementos_altos[0]

        parrafos.append(
            f"El elemento con mayor presencia es <b>{elemento}</b>. "
            f"Esto señala que {_desc_elemento(elemento)} tiende a aparecer "
            "con bastante facilidad en tu forma de funcionar."
        )

    else:

        parrafos.append(
            "La distribución de elementos aparece bastante repartida. "
            "Esto puede darte acceso a distintas formas de responder según el momento, "
            "sin que una sola cualidad domine claramente sobre las demás."
        )

    if elementos_bajos:

        if len(elementos_bajos) == 1:

            elemento = elementos_bajos[0]

            parrafos.append(
                f"Mientras tanto, <b>{elemento}</b> aparece con menor presencia."
            )

            textos_bajos = {
                "Tierra": (
                    "No es una carencia. Tampoco algo que haya que corregir. "
                    "Simplemente indica que la estabilidad, los ritmos, la organización "
                    "o la capacidad de sostener procesos quizá necesiten construirse "
                    "de forma más consciente, en lugar de surgir automáticamente."
                ),
                "Agua": (
                    "No significa que no exista sensibilidad. Puede indicar que reconocer, "
                    "expresar o permanecer en contacto con lo emocional necesita más tiempo, "
                    "espacio y atención consciente."
                ),
                "Aire": (
                    "No significa falta de inteligencia ni de capacidad para comprender. "
                    "Puede indicar que tomar distancia, ordenar lo que piensas o ponerlo "
                    "en palabras necesita más intención."
                ),
                "Fuego": (
                    "No significa falta de energía o iniciativa. Puede indicar que el impulso, "
                    "la confianza para empezar o la capacidad de actuar necesitan una razón "
                    "clara para ponerse en movimiento."
                ),
            }

            parrafos.append(
                textos_bajos.get(
                    elemento,
                    "No se trata de una carencia, sino de una cualidad que puede necesitar "
                    "más atención consciente para desarrollarse."
                )
            )

        else:

            texto_elementos = " y ".join(elementos_bajos)

            parrafos.append(
                f"<b>{texto_elementos}</b> aparecen con menor presencia. "
                "No se trata de carencias, sino de cualidades que pueden necesitar "
                "más intención y consciencia para integrarse en tu forma habitual de funcionar."
            )

    textos_modalidad = {
        "Cardinal": (
            "A todo ello se suma una modalidad predominantemente <b>cardinal</b>, "
            "que aporta iniciativa, capacidad para comenzar y tendencia a activar procesos."
        ),
        "Fija": (
            "A todo ello se suma una modalidad predominantemente <b>fija</b>, "
            "que aporta constancia, continuidad y capacidad para sostener aquello "
            "que consideras importante."
        ),
        "Mutable": (
            "A todo ello se suma una modalidad predominantemente <b>mutable</b>, "
            "que aporta flexibilidad, adaptación y facilidad para moverte entre "
            "distintas etapas, ideas o circunstancias."
        ),
    }

    if conteo_modal.get(modal_max, 0) >= 4:
        parrafos.append(
            textos_modalidad.get(modal_max, "")
        )

    mc_desc = MC_SIGNO.get(
        mc_signo,
        "una forma propia de orientarte hacia el mundo externo"
    )

    parrafos.append(
        f"Y, como telón de fondo, un <b>Medio Cielo en {mc_signo}</b>, "
        f"que orienta tu presencia pública hacia {mc_desc}"
    )

    parrafos.append(
        "No es una descripción completa de quién eres. "
        "Es una primera aproximación a la manera en que tu energía "
        "tiende a organizarse."
    )

    return "\n\n".join(parrafos)


def nivel_elemento(valor):
    if valor >= 4.5:
        return "alto"
    if valor >= 2.5:
        return "equilibrado"
    return "bajo"


def textos_elementos_reportlab(conteo_elem):

    orden = ["Aire", "Tierra", "Agua", "Fuego"]

    etiquetas_nivel = {
        "Aire": {
            "alto": "alto",
            "equilibrado": "equilibrado",
            "bajo": "bajo"
        },
        "Tierra": {
            "alto": "alta",
            "equilibrado": "equilibrada",
            "bajo": "baja"
        },
        "Agua": {
            "alto": "alta",
            "equilibrado": "equilibrada",
            "bajo": "baja"
        },
        "Fuego": {
            "alto": "alto",
            "equilibrado": "equilibrado",
            "bajo": "bajo"
        },
    }

    bloques = []

    for elem in orden:

        valor = conteo_elem.get(elem, 0)
        nivel = nivel_elemento(valor)
        texto = TEXTOS_ELEMENTOS_PDF[elem][nivel]

        texto = texto.replace(
            "<br/><br/>",
            "<br/>"
        )

        texto = texto.replace(
            "<br/>• ",
            "<br/>&nbsp;&nbsp;&nbsp;&nbsp;• "
        )

        etiqueta = etiquetas_nivel[elem][nivel]

        bloques.append(
            (
                f"{elem} {etiqueta}",
                texto
            )
        )

    return bloques



def bloque_portada(
    nombre,
    fecha_str,
    hora_str,
    ciudad,
    asc,
    titulo,
    centro
):

    elementos = []

    elementos.append(Spacer(1, 2*cm))

    frase_portada = ParagraphStyle(
        "FrasePortadaAI",
        parent=centro,
        fontName="Times-Italic",
        fontSize=11,
        leading=16,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#666666"),
        spaceAfter=12
    )

    elementos.append(Paragraph("Carta Natal Base", titulo))
    elementos.append(Paragraph("Arquitectura Interna", centro))
    elementos.append(Spacer(1, 0.4*cm))
    elementos.append(Paragraph(
        "<i>Un mapa inicial para observar cómo se organiza tu energía.</i>",
        frase_portada        
    ))

    elementos.append(Spacer(1, 1*cm))

    elementos.append(Paragraph(f"<b>{nombre}</b>", centro))
    elementos.append(Paragraph(f"{fecha_str} · {hora_str}", centro))
    elementos.append(Paragraph(ciudad, centro))

    elementos.append(Spacer(1, 0.5*cm))

    elementos.append(PageBreak())

    return elementos

def bloque_introduccion(subtitulo, cuerpo):

    elementos = []

    elementos.append(Paragraph("Introducción", subtitulo))

    elementos.append(Paragraph(
        """
    <b>Toda carta tiene una forma particular de organizar la energía.</b> La astrología puede llegar a ser muy detallada. Pero antes de profundizar, merece la pena reconocer algunas de las fuerzas principales que organizan tu manera de funcionar.<br/><br/>

    <b>No necesitas saber astrología para recorrer estas páginas.</b> Este cuaderno no está pensado para que aprendas un lenguaje nuevo, sino para ayudarte a mirarte de otra manera. La carta se convierte aquí en un mapa de observación: una forma de reconocer algunos patrones, recursos y desafíos que pueden estar presentes en tu vida.<br/><br/>

    No busques encajar en cada frase. Quédate con aquello que resuene contigo y permite que el resto simplemente quede abierto. Algunas partes tendrán sentido desde la primera lectura. Otras quizá lo hagan más adelante, cuando lo que vayas viviendo les dé un nuevo significado.
        """,
        cuerpo
    ))

    elementos.append(Paragraph(
        "No se trata de una lectura predictiva ni de una identidad fija. "
        "Es un mapa inicial de orientación.",
        cuerpo
    ))

    return elementos


def bloque_rueda(
    ruta_rueda,
    sol,
    luna,
    asc,
    mc,
    subtitulo,
    centro
):

    elementos = []

    # Más separación respecto al texto anterior
    elementos.append(
        Spacer(1, 0.7*cm)
    )

    # Rueda más grande
    elementos.append(
        Image(
            ruta_rueda,
            width=13.2*cm,
            height=13.2*cm
        )
    )

    # Espacio antes del siguiente bloque
    elementos.append(
        Spacer(1, 0.4*cm)
    )

    return elementos


def bloque_pilares(
    sol,
    luna,
    asc,
    ejes,
    subtitulo,
    subtitulo2,
    cuerpo
):

    elementos = []

    elementos.append(Paragraph("Los tres pilares", subtitulo))

    elementos.append(
        Paragraph(
            "Hasta ahora hemos mirado la carta desde cierta distancia. "
            "Eso nos ha permitido reconocer algunas de las dinámicas que organizan tu energía.<br/><br/>"
            "Ahora vamos a acercarnos a tres de sus puntos más importantes.<br/><br/>"
            "El <b>Sol</b>, la <b>Luna</b> y el <b>Ascendente</b> actúan como tres pilares fundamentales "
            "de cualquier carta natal. Cada uno responde a una pregunta diferente:<br/><br/>"
            "<b>¿Hacia dónde tiendes a dirigirte?</b><br/>"
            "<b>¿Qué necesitas para sentir seguridad emocional?</b><br/>"
            "<b>¿Cómo entras en contacto con el mundo?</b><br/><br/>"
            "Comprender estos tres pilares no explica toda tu carta, pero sí ofrece una base sólida "
            "desde la que empezar a comprenderte.",
            cuerpo
        )
    )

    elementos.append(
        Spacer(1, 0.35*cm)
    )

    elementos.append(KeepTogether([
        Paragraph(f"Sol en {sol.get('signo','')}", subtitulo2),
        Paragraph(ejes["sol"], cuerpo)
    ]))

    elementos.append(KeepTogether([
        Paragraph(f"Luna en {luna.get('signo','')}", subtitulo2),
        Paragraph(ejes["luna"], cuerpo)
    ]))

    elementos.append(KeepTogether([
        Paragraph(f"Ascendente {asc.get('signo','')}", subtitulo2),
        Paragraph(ejes["asc"], cuerpo)
    ]))

    return elementos


def bloque_vision_general(
    vision,
    subtitulo,
    cuerpo
):

    elementos = []

    elementos.append(Paragraph("Una primera mirada", subtitulo))

    for parrafo in vision.split("\n\n"):

        if parrafo.strip():

            elementos.append(
                Paragraph(
                    parrafo.strip(),
                    cuerpo
                )
            )

    return elementos


# ─── SECCIÓN: EJES PRINCIPALES ───────────────────────────────────────────────

def texto_ejes_principales(carta):
    planetas = carta["planetas"]
    asc = carta["asc"]

    sol = planetas.get("Sol", {})
    luna = planetas.get("Luna", {})

    s_sol_signo = SOL_SIGNO.get(sol.get("signo", ""), "")
    s_sol_casa  = SOL_CASA.get(sol.get("casa", 0), "")

    s_luna_signo = LUNA_SIGNO.get(luna.get("signo", ""), "")
    s_luna_casa  = LUNA_CASA.get(luna.get("casa", 0), "")

    s_asc = ASC_SIGNO.get(asc.get("signo", ""), "")

    return {
        "sol": f"{s_sol_signo} {s_sol_casa}",
        "luna": f"{s_luna_signo} {s_luna_casa}",
        "asc": s_asc,
    }



# ─── ESTILOS Y BLOQUES REPORTLAB ─────────────────────────

def crear_estilos_reportlab():
    estilos = getSampleStyleSheet()

    titulo = ParagraphStyle(
        "TituloAI",
        parent=estilos["Title"],
        fontName="Times-Bold",
        fontSize=28,
        leading=34,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1E508C"),
        spaceAfter=20
    )

    subtitulo = ParagraphStyle(
        "SubtituloAI",
        parent=estilos["Heading2"],
        fontName="Times-Bold",
        fontSize=18,
        leading=23,
        textColor=colors.HexColor("#8C5A00"),
        spaceBefore=18,
        spaceAfter=10
    )

    subtitulo2 = ParagraphStyle(
        "Subtitulo2AI",
        parent=estilos["Heading3"],
        fontName="Times-Bold",
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#1E508C"),
        spaceBefore=12,
        spaceAfter=6
    )

    cuerpo = ParagraphStyle(
        "CuerpoAI",
        parent=estilos["BodyText"],
        fontName="Times-Roman",
        fontSize=11,
        leading=16,
        spaceAfter=10
    )

    cuerpo_elementos = ParagraphStyle(
        "CuerpoElementosAI",
        parent=cuerpo,
        spaceAfter=10
    )

    centro = ParagraphStyle(
        "CentroAI",
        parent=cuerpo,
        alignment=TA_CENTER
    )


    return {
        "titulo": titulo,
        "subtitulo": subtitulo,
        "subtitulo2": subtitulo2,
        "cuerpo": cuerpo,
        "cuerpo_elementos": cuerpo_elementos,
        "centro": centro,
    }


def bloque_distribucion_energetica(
    conteo_elem,
    conteo_modal,
    subtitulo,
    cuerpo
):

    elementos = []

    tabla_datos = [
        ["Elemento", "Valor", "Modalidad", "Valor"],
        [
            "Fuego",
            conteo_elem.get("Fuego", 0),
            "Cardinal",
            conteo_modal.get("Cardinal", 0)
        ],
        [
            "Tierra",
            conteo_elem.get("Tierra", 0),
            "Fija",
            conteo_modal.get("Fija", 0)
        ],
        [
            "Aire",
            conteo_elem.get("Aire", 0),
            "Mutable",
            conteo_modal.get("Mutable", 0)
        ],
        [
            "Agua",
            conteo_elem.get("Agua", 0),
            "",
            ""
        ],
    ]

    tabla = Table(
        tabla_datos,
        colWidths=[
            3.2*cm,
            2*cm,
            3.2*cm,
            2*cm
        ]
    )

    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDE3D3")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1E508C")),

        ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Times-Roman"),

        ("FONTSIZE", (0, 0), (-1, -1), 10),

        ("ALIGN", (1, 1), (1, -1), "CENTER"),
        ("ALIGN", (3, 1), (3, -1), "CENTER"),

        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#C8B89E")),
        ("BOX", (0, 0), (-1, -1), 1.2, colors.HexColor("#8C5A00")),

        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))

    bloque_completo = KeepTogether([
        Paragraph(
            "Distribución energética",
            subtitulo
        ),

        Paragraph(
            "Cada carta organiza su energía de una manera diferente. "
            "Esta distribución nos permite reconocer esa organización antes de observar "
            "con más detalle el papel de cada elemento.",
            cuerpo
        ),

        Spacer(1, 0.15*cm),

        tabla
    ])

    elementos.append(bloque_completo)

    return elementos


def bloque_resumen_carta(
    sol,
    luna,
    asc,
    mc,
    subtitulo
):

    elementos = []

    tabla_datos = [
        ["Punto", "Signo", "Casa"],
        [
            "Sol",
            sol.get("signo", ""),
            sol.get("casa", "")
        ],
        [
            "Luna",
            luna.get("signo", ""),
            luna.get("casa", "")
        ],
        [
            "Ascendente",
            asc.get("signo", ""),
            ""
        ],
        [
            "Medio Cielo",
            mc.get("signo", ""),
            ""
        ],
    ]

    tabla = Table(
        tabla_datos,
        colWidths=[
            4.2*cm,
            4.2*cm,
            2.4*cm
        ]
    )

    tabla.setStyle(TableStyle([

        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDE3D3")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1E508C")),

        ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Times-Roman"),

        ("FONTSIZE", (0, 0), (-1, -1), 10),

        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D8CBB8")),
        ("BOX", (0, 0), (-1, -1), 1.2, colors.HexColor("#8C5A00")),

        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (2, 1), (2, -1), "CENTER"),

        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),

    ]))

    bloque_completo = KeepTogether([
        Paragraph("Claves principales", subtitulo),

        Paragraph(
            "Antes de profundizar, conviene situar los cuatro puntos desde los que "
            "empieza esta primera lectura de tu carta.",
            ParagraphStyle(
                "IntroduccionClavesAI",
                parent=subtitulo,
                fontName="Times-Roman",
                fontSize=11,
                leading=16,
                textColor=colors.HexColor("#333333"),
                spaceBefore=0,
                spaceAfter=8
            )
        ),

        Spacer(1, 0.15*cm),

        tabla
    ])

    elementos.append(bloque_completo)

    return elementos

def texto_integracion_elementos(conteo_elem):

    ordenados = sorted(
        conteo_elem.items(),
        key=lambda item: item[1],
        reverse=True
    )

    principal = ordenados[0][0]
    secundario = ordenados[1][0]
    menor = ordenados[-1][0]

    funciones = {
        "Fuego": "impulso, iniciativa y necesidad de movimiento",
        "Tierra": "estabilidad, concreción y capacidad de sostener",
        "Aire": "perspectiva, pensamiento y comunicación",
        "Agua": "sensibilidad, percepción emocional y conexión"
    }

    texto = (
        f"Ningún elemento funciona de manera aislada. En tu carta, "
        f"{principal} y {secundario} aparecen con especial fuerza. "
        f"{principal} aporta {funciones[principal]}, mientras que "
        f"{secundario} incorpora {funciones[secundario]}. "
        "La manera en la que ambas energías se relacionan forma parte importante "
        "de tu modo de responder a la vida."
    )

    if conteo_elem.get(menor, 0) <= 2.0:

        texto += (
            f"<br/><br/>{menor} aparece con menor presencia. "
            f"Esto no significa que te falten {funciones[menor]}. "
            "Significa que estas cualidades quizá necesiten desarrollarse de una forma "
            "mmás consciente para poder sostener el conjunto de tu energía."
        )

    texto += (
        "<br/><br/>La clave no está en potenciar todavía más aquello que ya aparece "
        "con facilidad, sino en aprender a relacionar todas estas cualidades de una "
        "forma más coherente. Lo que una parte de ti inicia, otra necesita poder "
        "comprenderlo, sentirlo o sostenerlo."
    )

    return texto

def bloque_lectura_elementos(
    conteo_elem,
    subtitulo,
    subtitulo2,
    cuerpo
):

    elementos = []

    elementos.append(
        Paragraph(
            "Lectura por elementos",
            subtitulo
        )
    )

    for titulo_elem, texto_elem in textos_elementos_reportlab(conteo_elem):

        bloque_elemento = KeepTogether([
            Paragraph(
                titulo_elem,
                subtitulo2
            ),
            Paragraph(
                texto_elem,
                cuerpo
            )
        ])

        elementos.append(bloque_elemento)

    elementos.append(
        Paragraph(
            "Cuando todas las piezas se relacionan",
            subtitulo
        )
    )

    elementos.append(
        Paragraph(
            texto_integracion_elementos(conteo_elem),
            cuerpo
        )
    )

    return elementos


def bloque_cierre(
    subtitulo,
    cuerpo
):

    elementos = []

    elementos.append(
        Paragraph(
            "Cierre",
            subtitulo
        )
    )

    elementos.append(
        Paragraph(
            "Esta carta es solo el comienzo.<br/><br/>"
            "Quizá algunas partes te hayan resultado evidentes. "
            "Otras pueden necesitar tiempo para cobrar sentido. "
            "Eso también forma parte del camino.<br/><br/>"
            "Una carta natal no se comprende de una sola vez. "
            "Se va revelando poco a poco, a medida que vas viviendo y "
            "reconociendo aquello que antes pasaba desapercibido.<br/><br/>"
            "Este cuaderno no busca responder todas las preguntas, sino ofrecerte "
            "un primer mapa desde el que empezar a observar cómo estas dinámicas "
            "aparecen en tu vida cotidiana.<br/><br/>"
            "Si deseas seguir profundizando, el siguiente paso natural es la <b>Luna</b>.<br/><br/>"
            "Si en estas páginas hemos observado cómo se organiza tu energía de forma general, "
            "la Luna nos invita a un lugar mucho más íntimo: la forma en la que buscas seguridad, "
            "procesas lo que sientes y aprendes a cuidar de ti.<br/><br/>"
            "Comprender cómo funcionas es importante. "
            "Aprender a vivir desde esa comprensión puede cambiar profundamente la manera en que te relacionas contigo, con los demás y con la vida.",
            cuerpo
        )
    )

    return elementos



def generar_pdf_reportlab_base(
    ruta_pdf, carta, nombre, año, mes, dia, hora, minuto,
    ciudad, lat, lon, tz_name, ruta_rueda
):
    
    planetas = carta["planetas"]
    asc = carta["asc"]
    mc = carta["mc"]

    conteo_elem = analizar_elementos(planetas, asc["signo"], hora_conocida=True)
    conteo_modal = analizar_modalidades(planetas)

    vision = texto_vision_general(carta, conteo_elem, conteo_modal)
    ejes = texto_ejes_principales(carta)

    sol = planetas.get("Sol", {})
    luna = planetas.get("Luna", {})

    fecha_str = f"{dia:02d}/{mes:02d}/{año}"
    hora_str = f"{hora:02d}:{minuto:02d}"

    doc = SimpleDocTemplate(
        ruta_pdf,
        pagesize=A4,
        rightMargin=2.5*cm,
        leftMargin=2.5*cm,
        topMargin=2.5*cm,
        bottomMargin=2.5*cm
    )

    estilos_ai = crear_estilos_reportlab()

    titulo = estilos_ai["titulo"]
    subtitulo = estilos_ai["subtitulo"]
    subtitulo2 = estilos_ai["subtitulo2"]
    cuerpo = estilos_ai["cuerpo"]
    centro = estilos_ai["centro"]
    cuerpo_elementos = estilos_ai["cuerpo_elementos"]


    contenido = []

    # Portada
    contenido.extend(
        bloque_portada(
            nombre,
            fecha_str,
            hora_str,
            ciudad,
            asc,
            titulo,
            centro
        )
    )

    # Introducción
    contenido.extend(
        bloque_introduccion(
            subtitulo,
            cuerpo
        )
    )

    # Rueda
    contenido.extend(
        bloque_rueda(
            ruta_rueda,
            sol,
            luna,
            asc,
            mc,
            subtitulo,
            centro
        )
    )



    # Tabla
    contenido.extend(
	    bloque_resumen_carta(
        	sol,
	        luna,
        	asc,
	        mc,
        	subtitulo
	    )
	)

    contenido.append(Spacer(1, 0.45*cm))

    # Visión general
    contenido.extend(
        bloque_vision_general(
            vision,
            subtitulo,
            cuerpo
        )
    )

    # Distribución de elementos y modalidades
    contenido.extend(
	    bloque_distribucion_energetica(
        	conteo_elem,
	        conteo_modal,
        	subtitulo,
	        cuerpo
	    )
	)

    contenido.append(Spacer(1, 0.8*cm))

    # Elementos y modalidades
    contenido.extend(
            bloque_lectura_elementos(
            conteo_elem,
            subtitulo,
            subtitulo2,
            cuerpo_elementos
        )
    )



    contenido.append(PageBreak())

    # Tres pilares
    contenido.extend(
        bloque_pilares(
            sol,
            luna,
            asc,
            ejes,
            subtitulo,
            subtitulo2,
            cuerpo
        )
    )

    contenido.append(PageBreak())

    # Cierre
    contenido.extend(
        bloque_cierre(
            subtitulo,
            cuerpo
        )
    )

    doc.build(contenido)


def generar_carta_api(nombre, fecha, hora, lugar, lat=None, lon=None, tz_name=None):

    print("Generando carta para:", nombre)

    try:

        # ── FECHA ─────────────────────────────────────────────

        dia, mes, año = map(int, fecha.split("/"))

        print("Fecha recibida:", fecha)
        print("Lugar recibido:", lugar)

        # ── HORA ──────────────────────────────────────────────

        print("Hora recibida:", hora)

        partes = hora.split(":")

        hora = int(partes[0])
        minuto = int(partes[1])

        # ── GEOLOCALIZACIÓN ──────────────────────────────────

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

        # ── CÁLCULO CARTA ────────────────────────────────────

        carta = calcular_carta(
            año, mes, dia,
            hora, minuto,
            lat, lon,
            tz_name
        )


        # ── RUTAS ────────────────────────────────────────────

        nombre_f = (
            nombre
            .replace(" ", "_")
            .replace("/", "-")
            .replace("\\", "-")
        )

        dir_sal = os.path.dirname(os.path.abspath(__file__))

        ruta_base = os.path.join(dir_sal, nombre_f + "_carta_base")

        ruta_png = ruta_base + "_rueda.png"
        ruta_pdf = ruta_base + ".pdf"

        # ── RUEDA ────────────────────────────────────────────

        dibujar_rueda(carta, nombre, ruta_png)


        # ── PDF REPORTLAB ─────────────────────────────────────

        generar_pdf_reportlab_base(
            ruta_pdf, carta, nombre,
            año, mes, dia,
            hora, minuto,
            lugar, lat, lon, tz_name,
            ruta_png
        )


        # ── RESPUESTA ────────────────────────────────────────

        if os.path.exists(ruta_pdf):

            return {
                "ok": True,
                "pdf": f"/descargas/{os.path.basename(ruta_pdf)}"
            }

        else:

            return {
                "ok": False,
                "error": "No se generó el PDF"
            }

    except Exception as e:

        return {
            "ok": False,
            "error": str(e)
        }

    finally:

        plt.close("all")
        gc.collect()


def main():
    print("=" * 60)
    print("   CARTA NATAL BASE — Arquitectura Interna")
    print("=" * 60)
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
    print("Calculando carta natal base...")

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
        carta = calcular_carta(
            año, mes, dia,
            hora, minuto,
            lat, lon,
            tz_name
        )

        print(
            f"  Ascendente: "
            f"{carta['asc']['signo']} {grado_a_dms(carta['asc']['grado'])}"
        )

        print(
            f"  Medio Cielo: "
            f"{carta['mc']['signo']} {grado_a_dms(carta['mc']['grado'])}"
        )

    except Exception as e:
        print(f"Error en cálculo astrológico: {e}")
        sys.exit(1)

    nombre_f = (
        nombre
        .replace(" ", "_")
        .replace("/", "-")
        .replace("\\", "-")
    )

    dir_sal = os.path.dirname(os.path.abspath(__file__))

    ruta_base = os.path.join(dir_sal, nombre_f + "_carta_base")
    ruta_png  = ruta_base + "_rueda.png"
    ruta_pdf  = ruta_base + ".pdf"

    print("  Dibujando rueda astrológica...")

    try:
        dibujar_rueda(carta, nombre, ruta_png)
        print(f"  Rueda guardada: {ruta_png}")
    except Exception as e:
        print(f"Error al dibujar la rueda: {e}")
        sys.exit(1)

    print("  Generando carta natal base...")

    print("  Generando PDF con ReportLab...")

    generar_pdf_reportlab_base(
        ruta_pdf, carta, nombre,
        año, mes, dia,
        hora, minuto,
        ciudad, lat, lon, tz_name,
        ruta_png
    )

    if os.path.exists(ruta_pdf):
        print(f"  PDF generado: {ruta_pdf}")

    else:
        print("  Error: no se generó el PDF.")


    print()
    print("=" * 60)
    print(f"  Carta natal base de {nombre} generada.")
    print(f"  Ficheros en: {dir_sal}")
    print(f"    - {nombre_f}_carta_base_rueda.png")
    print(f"    - {nombre_f}_carta_base.pdf")
    print("=" * 60)


if __name__ == "__main__":
    main()