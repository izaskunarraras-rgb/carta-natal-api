
#!/usr/bin/env python3
"""
Carta Natal Base — Arquitectura Interna
Una lectura orientada a comprender tus tendencias principales,
tu forma de funcionar y los procesos de crecimiento
más importantes de tu carta natal.
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
    "Sueles adaptarte bien a situaciones cambiantes y aprender rápido cuando algo despierta tu curiosidad. "
    "Las ideas, las conversaciones y la variedad suelen ser importantes para ti."
),

"Cáncer": (
    "Con el Sol en Cáncer, el vínculo, la cercanía y la sensación de confianza suelen tener mucha importancia para ti. "
    "Tiendes a percibir rápidamente cómo están las personas y el ambiente que te rodea. "
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
    "Con el Sol en Escorpio, suele haber necesidad de profundidad, implicación real e intensidad emocional. "
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
    "Con el Sol en Piscis, suele haber bastante sensibilidad hacia el entorno y hacia lo que ocurre alrededor. "
    "Percibes matices, estados o necesidades que otras personas pueden pasar por alto. "
    "La empatía y la capacidad de conectar emocionalmente suelen tener bastante importancia en tu vida."
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
    "Con el Sol en Casa 2, necesitas construir estabilidad y confianza a través de lo que haces, sostienes o desarrollas por ti. "
    "Los recursos, los valores personales y la sensación de autonomía suelen tener bastante peso en tu vida. "
    "Muchas veces necesitas sentir que puedes apoyarte en algo sólido construido desde ti."
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
    "Cuando hay espacio para la autenticidad y el disfrute, normalmente sueles sentirte más vital."
),

6: (
    "Con el Sol en Casa 6, el trabajo cotidiano, los hábitos y la necesidad de sentir utilidad suelen ser importantes para ti. "
    "Tu energía normalmente se organiza mejor cuando hay cierta estructura o algo concreto de lo que ocuparte. "
    "Muchas veces cuidar los ritmos y el día a día influye directamente en cómo te sientes contigo."
),

7: (
    "Con el Sol en Casa 7, los vínculos y las relaciones suelen tener un impacto importante en tu vida. "
    "Muchas veces conocerte mejor implica también verte a través del encuentro con otras personas. "
    "Las asociaciones, relaciones o colaboraciones significativas suelen influir mucho en tu desarrollo."
),

8: (
    "Con el Sol en Casa 8, suele haber necesidad de profundidad, intensidad e implicación emocional. "
    "Las experiencias importantes normalmente tienden a afectarte de forma profunda, aunque no siempre lo muestres hacia fuera. "
    "Muchas veces necesitas sentir conexión real para implicarte de verdad con algo o con alguien."
),

9: (
    "Con el Sol en Casa 9, necesitas sentir que tu vida se abre hacia nuevas perspectivas, aprendizajes o formas de comprender el mundo. "
    "Aprender, explorar o ampliar horizontes suele ayudarte a recuperar energía y dirección. "
    "Normalmente funcionas mejor cuando lo que haces tiene sentido para ti."
),

10: (
    "Con el Sol en Casa 10, la vocación, el reconocimiento y la construcción de algo visible suelen tener bastante importancia en tu vida. "
    "Necesitas sentir que lo que haces tiene coherencia con quién eres y hacia dónde quieres ir. "
    "Muchas veces el desarrollo profesional influye directamente en tu sensación de dirección y estabilidad."
),

11: (
    "Con el Sol en Casa 11, los grupos, amistades y proyectos compartidos suelen ocupar un lugar importante en tu vida. "
    "Muchas veces funcionas mejor cuando sientes conexión con personas, ideas o espacios con visión de futuro. "
    "Compartir intereses o formar parte de algo colectivo suele tener bastante significado para ti."
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
    "Muchas veces necesitas movimiento mental y variedad para no sentirte estancado emocionalmente."
),

"Cáncer": (
    "Con la Luna en Cáncer, hay mucha sensibilidad hacia el entorno emocional y hacia las personas importantes para ti. "
    "La cercanía, el cuidado y la sensación de confianza suelen tener bastante peso en cómo te sientes. "
    "Cuando el ambiente es acogedor y seguro, normalmente te resulta más fácil relajarte y abrirte."
),

"Leo": (
    "Con la Luna en Leo, las emociones suelen expresarse de forma cálida, visible y bastante espontánea. "
    "Sentirte apreciado, valorado o tenido en cuenta influye mucho en tu bienestar emocional. "
    "La creatividad, la expresión personal y los vínculos donde puedes mostrarte con libertad suelen ayudarte a sentirte bien."
),

"Virgo": (
    "Con la Luna en Virgo, tiendes a observar y analizar bastante cómo te encuentras emocionalmente. "
    "El orden, la claridad y la sensación de que las cosas funcionan ayudan a que puedas sentirte más tranquilo. "
    "Muchas veces necesitas entender lo que ocurre para sentir estabilidad interna."
),

"Libra": (
    "Con la Luna en Libra, el equilibrio en las relaciones y en el entorno influye mucho en cómo te sientes. "
    "Sueles percibir rápidamente el clima emocional de las situaciones y de las personas cercanas. "
    "La armonía, el diálogo y los vínculos donde hay reciprocidad suelen ayudarte a recuperar bienestar."
),

"Escorpio": (
    "Con la Luna en Escorpio, las emociones suelen vivirse con bastante intensidad aunque no siempre lo muestres hacia fuera. "
    "Necesitas tiempo y confianza antes de abrirte del todo emocionalmente. "
    "Cuando algo te afecta de verdad, normalmente lo vives de forma profunda."
),

"Sagitario": (
    "Con la Luna en Sagitario, necesitas espacio, movimiento y sensación de amplitud para sentirte bien emocionalmente. "
    "Sueles recuperar equilibrio cuando puedes cambiar de perspectiva, aprender algo nuevo o abrir horizontes. "
    "La sensación de crecimiento y dirección suele influir bastante en tu estado emocional."
),

"Capricornio": (
    "Con la Luna en Capricornio, normalmente tiendes a contener bastante lo que sientes antes de mostrarlo hacia fuera. "
    "La estabilidad, la responsabilidad y la sensación de construir algo sólido suelen darte seguridad emocional. "
    "Muchas veces necesitas tiempo antes de sentir suficiente confianza para mostrar vulnerabilidad."
),

"Acuario": (
    "Con la Luna en Acuario, necesitas cierta libertad emocional y espacio propio para sentirte bien. "
    "Cuando las emociones son demasiado intensas o invasivas, puedes necesitar tomar distancia para entender lo que te ocurre. "
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
    "Muchas veces lo que sientes se refleja rápidamente en la forma de reaccionar, en el cuerpo o en la presencia."
),

2: (
    "Con la Luna en Casa 2, la estabilidad y la sensación de seguridad suelen influir mucho en cómo te sientes emocionalmente. "
    "Los recursos, el cuerpo y aquello que puedes sostener de forma concreta suelen tener bastante importancia para ti."
),

3: (
    "Con la Luna en Casa 3, las emociones suelen procesarse a través de la palabra, el pensamiento o la necesidad de compartir lo que ocurre. "
    "Hablar, escribir o entender mentalmente lo que sientes puede ayudarte bastante a encontrar claridad."
),

4: (
    "Con la Luna en Casa 4, la intimidad, el hogar y la sensación de protección emocional suelen ocupar un lugar muy importante en tu vida. "
    "El entorno cercano influye bastante en cómo te sientes y en tu capacidad de descansar realmente."
),

5: (
    "Con la Luna en Casa 5, la expresión emocional suele estar conectada con la creatividad, el disfrute y la necesidad de mostrar lo que sientes. "
    "Los espacios donde puedes expresarte con autenticidad suelen ayudarte mucho emocionalmente."
),

6: (
    "Con la Luna en Casa 6, el cuerpo, los hábitos y el día a día suelen influir directamente en cómo te encuentras emocionalmente. "
    "Muchas veces una rutina más ordenada o ciertos cuidados cotidianos ayudan bastante a que puedas sentirte mejor."
),

7: (
    "Con la Luna en Casa 7, los vínculos y las relaciones cercanas suelen tener mucho impacto en tu mundo emocional. "
    "Las relaciones importantes normalmente influyen bastante en cómo te sientes contigo y con tu vida."
),

8: (
    "Con la Luna en Casa 8, las emociones suelen vivirse con bastante intensidad aunque no siempre se expresen fácilmente. "
    "Los vínculos profundos y las experiencias importantes tienden a afectarte más de lo que otras personas perciben desde fuera."
),

9: (
    "Con la Luna en Casa 9, necesitas sentir cierta amplitud, dirección o sentido para encontrarte bien emocionalmente. "
    "Aprender, explorar o abrir nuevas perspectivas suele ayudarte bastante a recuperar equilibrio."
),

10: (
    "Con la Luna en Casa 10, la vocación, los objetivos y el reconocimiento suelen influir bastante en tu estado emocional. "
    "Muchas veces lo profesional o lo visible hacia fuera tiene un impacto importante en cómo te sientes."
),

11: (
    "Con la Luna en Casa 11, las amistades, los grupos y la sensación de pertenecer a algo compartido suelen tener bastante importancia emocional para ti. "
    "Sentirte conectado con personas o proyectos con visión de futuro normalmente influye mucho en tu bienestar."
),

12: (
    "Con la Luna en Casa 12, gran parte de lo emocional suele vivirse de forma reservada o difícil de expresar rápidamente. "
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
    "Las demás personas suelen percibir solidez y cierta sensación de competencia desde el principio."
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

    print("EPHE_PATH:", EPHE_PATH)
    print("EXISTE EPHE:", os.path.exists(EPHE_PATH))
    print("ARCHIVOS EPHE:", os.listdir(EPHE_PATH))

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

    print("DEBUG QUIRÓN")
    print("  Lon:", planetas["Quirón"]["lon"])
    print("  Signo:", planetas["Quirón"]["signo"])
    print("  Grado:", grado_a_dms(planetas["Quirón"]["grado"]))
    print("  Casa:", planetas["Quirón"]["casa"])
    print("  Aproximado:", planetas["Quirón"].get("aprox", False))
    print("  ASC:", asc["signo"] if "asc" in locals() else signo_asc,
          grado_a_dms(grado_asc))

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
# ─── RUEDA ASTROLÓGICA ────────────────────────────────────────────────────────

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

    # ─── TÍTULO ─────────────────────────────────────────────────────────────

    plt.title(
        f"Carta natal base — {nombre_persona}",
        fontsize=14,
        fontweight="bold",
        pad=15
    )

    plt.tight_layout()

    plt.savefig(
        archivo_salida,
        dpi=150,
        bbox_inches="tight",
        facecolor="white",
        edgecolor="none"
    )

    plt.close()


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


def texto_vision_general(carta, conteo_elem, conteo_modal):
    mc_signo = carta["mc"]["signo"]

    def _fpt(v):
        return str(int(v)) if v == int(v) else str(v)

    ordenado = sorted(conteo_elem.items(), key=lambda x: -x[1])
    alto = [e for e, n in ordenado if n >= 5.5]
    bajo = [e for e, n in ordenado if n <= 2.0]

    texto = (
        f"Tu carta muestra esta distribución de elementos: "
        f"Fuego {_fpt(conteo_elem['Fuego'])}, "
        f"Tierra {_fpt(conteo_elem['Tierra'])}, "
        f"Aire {_fpt(conteo_elem['Aire'])}, "
        f"Agua {_fpt(conteo_elem['Agua'])}. "
    )

    if alto:
        desc = " y ".join([f"{e} ({_desc_elemento(e)})" for e in alto])
        texto += (
            f"El elemento más presente es {desc}. "
            f"Esto señala un registro que suele aparecer con facilidad en tu forma de funcionar. "
        )

    if bajo:
        desc = " y ".join([f"{e} ({_desc_elemento(e)})" for e in bajo])
        texto += (
            f"El elemento menos presente es {desc}. "
            f"No significa ausencia, sino una cualidad que puede necesitar más atención consciente. "
        )

    modal_max = max(conteo_modal, key=conteo_modal.get)

    if conteo_modal[modal_max] >= 4:
        desc_modal = {
            "Cardinal": (
                "Predomina la modalidad cardinal, asociada a la iniciativa, el comienzo y la capacidad de activar procesos. "
            ),
            "Fija": (
                "Predomina la modalidad fija, asociada a la constancia, la continuidad y la capacidad de sostener lo importante. "
            ),
            "Mutable": (
                "Predomina la modalidad mutable, asociada a la adaptación, la flexibilidad y el movimiento entre distintas situaciones. "
            ),
        }

        texto += desc_modal.get(modal_max, "")

    mc_desc = MC_SIGNO.get(mc_signo, "una forma propia de orientarte hacia el mundo externo")

    texto += (
        f"Tu Medio Cielo en {mc_signo} orienta tu presencia pública hacia la {mc_desc}"
    )

    return texto


def nivel_elemento(valor):
    if valor >= 4.5:
        return "alto"
    if valor >= 2.5:
        return "equilibrado"
    return "bajo"


TEXTOS_ELEMENTOS_PDF = {
    "Aire": {
        "alto": (
            "La mente está muy activa. Piensas rápido y conectas ideas con facilidad. "
            "Puedes darle muchas vueltas a las cosas o adelantarte demasiado.\n\n"
            "\\textbf{Observa:}\n"
            "\\begin{itemize}\n"
            "\\item cuándo no paras de pensar\n"
            "\\item si piensas en lugar de hacer o sentir\n"
            "\\item si te cuesta desconectar la cabeza\n"
            "\\end{itemize}"
        ),
        "equilibrado": (
            "Puedes pensar cuando lo necesitas y parar cuando no hace falta. "
            "La mente está disponible, pero no te arrastra.\n\n"
            "\\textbf{Observa:}\n"
            "\\begin{itemize}\n"
            "\\item cuándo usas la cabeza para resolver algo\n"
            "\\item cuándo sigues pensando sin necesidad\n"
            "\\item si puedes parar y descansar la mente\n"
            "\\end{itemize}"
        ),
        "bajo": (
            "No pasas tanto por la cabeza. Tiendes a ir directa a lo que haces o sientes sin pensarlo mucho. "
            "Puede costar ordenar ideas o explicar lo que te pasa.\n\n"
            "\\textbf{Observa:}\n"
            "\\begin{itemize}\n"
            "\\item si te cuesta explicar lo que sientes o piensas\n"
            "\\item si necesitas más tiempo para entender lo que te ocurre\n"
            "\\item en qué momentos te vendría bien parar y pensar un poco\n"
            "\\end{itemize}"
        ),
    },

    "Tierra": {
        "alto": (
            "Necesitas tener control y estabilidad. Te apoyas en lo que es seguro y conocido. "
            "Puedes volverte rígida o exigirte demasiado.\n\n"
            "\\textbf{Observa:}\n"
            "\\begin{itemize}\n"
            "\\item cuánto necesitas tener todo bajo control\n"
            "\\item si te cuesta cambiar planes o improvisar\n"
            "\\item si te exiges más de lo necesario\n"
            "\\end{itemize}"
        ),
        "equilibrado": (
            "Puedes organizarte y también adaptarte. Sabes cuándo mantener algo y cuándo cambiarlo.\n\n"
            "\\textbf{Observa:}\n"
            "\\begin{itemize}\n"
            "\\item cómo te organizas en tu día a día\n"
            "\\item cuándo mantienes algo aunque ya no sirve\n"
            "\\item cuándo cambias sin problema\n"
            "\\end{itemize}"
        ),
        "bajo": (
            "Te cuesta mantener rutinas o seguir algo en el tiempo. "
            "Puedes empezar cosas pero no siempre sostenerlas.\n\n"
            "\\textbf{Observa:}\n"
            "\\begin{itemize}\n"
            "\\item si te cuesta mantener horarios o hábitos\n"
            "\\item si dejas cosas a medias\n"
            "\\item qué te ayudaría a tener más orden en tu día\n"
            "\\end{itemize}"
        ),
    },

    "Agua": {
        "alto": (
            "Sientes mucho. Lo que pasa por dentro tiene mucho peso. "
            "Puedes saturarte o quedarte enganchada en lo emocional.\n\n"
            "\\textbf{Observa:}\n"
            "\\begin{itemize}\n"
            "\\item cuándo te afecta demasiado lo que pasa\n"
            "\\item si te cuesta separar lo tuyo de lo de los demás\n"
            "\\item cómo te calmas cuando algo te desborda\n"
            "\\end{itemize}"
        ),
        "equilibrado": (
            "Puedes sentir sin perderte en lo que sientes. Hay conexión emocional, pero también espacio.\n\n"
            "\\textbf{Observa:}\n"
            "\\begin{itemize}\n"
            "\\item cómo reaccionas cuando algo te afecta\n"
            "\\item si puedes tomar distancia cuando lo necesitas\n"
            "\\item cómo vuelves a un estado más tranquilo\n"
            "\\end{itemize}"
        ),
        "bajo": (
            "No siempre conectas fácilmente con lo que sientes. "
            "Puede costar identificar o expresar emociones.\n\n"
            "\\textbf{Observa:}\n"
            "\\begin{itemize}\n"
            "\\item si te cuesta saber qué estás sintiendo\n"
            "\\item si evitas lo emocional\n"
            "\\item en qué momentos conectas más con ello\n"
            "\\end{itemize}"
        ),
    },

    "Fuego": {
        "alto": (
            "Tienes mucha energía para actuar. Te mueves rápido y tomas iniciativa. "
            "Puedes ir demasiado deprisa o no sostener lo que empiezas.\n\n"
            "\\textbf{Observa:}\n"
            "\\begin{itemize}\n"
            "\\item si te lanzas sin pensar\n"
            "\\item si empiezas cosas y luego las dejas\n"
            "\\item cuándo necesitas bajar el ritmo\n"
            "\\end{itemize}"
        ),
        "equilibrado": (
            "Puedes actuar cuando hace falta y parar cuando no. "
            "No estás siempre en marcha, pero tampoco bloqueada.\n\n"
            "\\textbf{Observa:}\n"
            "\\begin{itemize}\n"
            "\\item cuándo te pones en marcha\n"
            "\\item si te cuesta empezar algo\n"
            "\\item cómo regulas tu ritmo\n"
            "\\end{itemize}"
        ),
        "bajo": (
            "Te cuesta arrancar o tomar iniciativa. Necesitas más tiempo para empezar algo.\n\n"
            "\\textbf{Observa:}\n"
            "\\begin{itemize}\n"
            "\\item qué te frena al empezar\n"
            "\\item qué te ayuda a activarte\n"
            "\\item si esperas demasiado antes de actuar\n"
            "\\end{itemize}"
        ),
    },
}


def bloque_elementos_pdf(conteo_elem):
    orden = ["Aire", "Tierra", "Agua", "Fuego"]

    partes = []

    for elem in orden:
        valor = conteo_elem.get(elem, 0)
        nivel = nivel_elemento(valor)
        titulo_nivel = {
            "alto": "alto",
            "equilibrado": "equilibrado",
            "bajo": "bajo"
        }[nivel]

        partes.append(
            f"\\subsection{{{elem} {titulo_nivel}}}\n\n"
            f"{TEXTOS_ELEMENTOS_PDF[elem][nivel]}\n\n"
            "\\vspace{0.4cm}\n"
            "\\Needspace{5\\baselineskip}\n"
        )

    partes.append(
        "\\subsection{Integración}\n\n"
        "Esto no define quién eres. Solo muestra cómo tiendes a funcionar.\n\n"
        "No hay nada que cambiar. Se trata de verlo y aprender a manejarlo mejor.\n\n"
        "\\vspace{0.4cm}\n\n"
        "\\begin{center}\n"
        "{\\small\\itshape\n"
        "Ten en cuenta que tienes que hacer la amalgama de todos los elementos. "
        "Por ejemplo, si tienes Fuego muy alto pero también mucha Tierra, "
        "puede que no dejes proyectos a medias.\n"
        "}\n"
        "\\end{center}\n"
    )

    return "\n".join(partes)


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



# ─── SECCIÓN: ESTRUCTURA Y TENSIÓN ───────────────────────────────────────────

def texto_estructura_tension(aspectos_ordenados):
    planetas_clave = {"Sol","Luna","Mercurio","Venus","Marte","Ascendente","Saturno","Júpiter","Plutón"}
    vistos = set()
    exactos = []
    estructurales = []

    for asp in aspectos_ordenados:
        p1, p2, tipo = asp["p1"], asp["p2"], asp["simbolo"]
        clave1 = (p1, p2, tipo); clave2 = (p2, p1, tipo)
        if clave1 in vistos or clave2 in vistos: continue
        texto_asp = ASPECTOS_CLAVE.get(clave1) or ASPECTOS_CLAVE.get(clave2)
        tiene_clave = p1 in planetas_clave or p2 in planetas_clave

        if asp.get("relevancia") == "exacto":
            if texto_asp:
                exactos.append((asp, texto_asp)); vistos.add(clave1)

        elif asp.get("relevancia") == "estructural" and tiene_clave:
            if texto_asp:
                estructurales.append((asp, texto_asp)); vistos.add(clave1)

    return {"exactos": exactos, "estructurales": estructurales}


# ─── CIERRE CARTA BASE ───────────────────────────────────────────────────────

CIERRE_CARTA_BASE = (
    "Esta carta no busca definirte ni cerrar una interpretación completa sobre ti. "
    "Es una primera aproximación a tus tendencias principales: cómo se activa tu energía, "
    "cómo se expresa tu mundo emocional y cómo sueles entrar en contacto con la vida. "
    "La lectura ampliada desarrolla con más profundidad los vínculos, la acción, los patrones repetitivos, "
    "las tensiones internas, la dirección de crecimiento y las configuraciones principales de la carta."
)



# ─── ESCAPADO LATEX ────────────────────────────────────────────────────────

def esc(texto):
    if texto is None:
        return ""

    reemplazos = [
        ("\\", r"\textbackslash{}"),
        ("&",  r"\&"),
        ("%",  r"\%"),
        ("$",  r"\$"),
        ("#",  r"\#"),
        ("_",  r"\_"),
        ("{",  r"\{"),
        ("}",  r"\}"),
        ("~",  r"\textasciitilde{}"),
        ("^",  r"\^{}"),
    ]

    for orig, repl in reemplazos:
        texto = texto.replace(orig, repl)

    return texto


# ─── GENERACIÓN LATEX · CARTA BASE ──────────────────────────────────────────

def generar_latex_ai(carta, nombre, año, mes, dia, hora, minuto,
                     ciudad, lat, lon, tz_name, ruta_rueda):

    planetas = carta["planetas"]
    asc = carta["asc"]
    mc  = carta["mc"]

    ruta_rueda = os.path.basename(ruta_rueda).replace("\\", "/")

    fecha_str = f"{dia:02d}/{mes:02d}/{año}"
    hora_str  = f"{hora:02d}:{minuto:02d}"

    tz_obj = pytz.timezone(tz_name)
    dt_local = tz_obj.localize(datetime(año, mes, dia, hora, minuto))
    utc_off  = dt_local.strftime("%z")
    utc_str  = f"UTC{utc_off[:3]}:{utc_off[3:]}"

    nom_esc = esc(nombre)
    ciu_esc = esc(ciudad)

    # ── Interpretación base ───────────────────────────────────────────────

    conteo_elem  = analizar_elementos(
        planetas,
        asc["signo"],
        hora_conocida=(minuto is not None)
    )

    conteo_modal = analizar_modalidades(planetas)

    vision = texto_vision_general(
        carta,
        conteo_elem,
        conteo_modal
    )

    elementos_pdf = bloque_elementos_pdf(conteo_elem)

    ejes = texto_ejes_principales(carta)


    # ── Posiciones resumidas ──────────────────────────────────────────────

    sol   = planetas.get("Sol", {})
    luna  = planetas.get("Luna", {})

    posiciones = (
        f"Sol en {sol.get('signo','')} — Casa {sol.get('casa','')}\\\\\n"
        f"Luna en {luna.get('signo','')} — Casa {luna.get('casa','')}\\\\\n"
        f"Ascendente {asc.get('signo','')}\\\\\n"
        f"Medio Cielo en {mc.get('signo','')}"
    )

    # ── Documento ─────────────────────────────────────────────────────────

    latex = f"""
\\documentclass[11pt,a4paper]{{article}}

\\usepackage[utf8]{{inputenc}}
\\usepackage[T1]{{fontenc}}
\\usepackage[spanish]{{babel}}

\\usepackage{{tgpagella}}
\\usepackage{{geometry}}
\\usepackage{{graphicx}}
\\usepackage{{xcolor}}
\\usepackage{{titlesec}}
\\usepackage{{fancyhdr}}
\\usepackage[parfill]{{parskip}}
\\usepackage[expansion=false]{{microtype}}
\\usepackage{{hyperref}}
\\usepackage{{setspace}}
\\usepackage{{needspace}}

\\geometry{{top=3.0cm,bottom=3.0cm,left=3.5cm,right=3.5cm}}

\\setlength{{\\parskip}}{{0.65em}}
\\setlength{{\\parindent}}{{0em}}

\\definecolor{{azulai}}{{RGB}}{{30,80,140}}
\\definecolor{{doradoai}}{{RGB}}{{140,90,0}}
\\definecolor{{grisai}}{{RGB}}{{70,70,70}}

\\titleformat{{\\section}}
{{\\Large\\bfseries\\color{{azulai}}}}
{{}}{{0em}}{{}}
[{{\\color{{azulai}}\\titlerule[0.5pt]}}]

\\titlespacing*{{\\section}}{{0pt}}{{1.8em}}{{0.8em}}

\\titleformat{{\\subsection}}
{{\\large\\bfseries\\color{{doradoai}}}}
{{}}{{0em}}{{}}

\\titlespacing*{{\\subsection}}{{0pt}}{{1.2em}}{{0.4em}}

\\pagestyle{{fancy}}
\\fancyhf{{}}

\\rhead{{\\textcolor{{grisai}}{{\\small {nom_esc} — Arquitectura Interna}}}}
\\lhead{{\\textcolor{{grisai}}{{\\small Carta Natal Base}}}}

\\cfoot{{\\textcolor{{grisai}}{{\\small\\thepage}}}}

\\renewcommand{{\\headrulewidth}}{{0.3pt}}

\\hypersetup{{
colorlinks=true,
linkcolor=azulai,
urlcolor=azulai
}}

\\setstretch{{1.4}}

\\begin{{document}}

% ── PORTADA ──────────────────────────────────────────────────────────────

\\begin{{titlepage}}

\\centering

\\vspace*{{1.5cm}}

{{\\Huge\\bfseries\\color{{azulai}} Carta Natal Base}}\\\\[0.5cm]

{{\\large\\color{{grisai}} Arquitectura Interna}}\\\\[0.4cm]

{{\\small\\itshape\\color{{grisai}}
Un método para sostener cuerpo, energía y vida con coherencia
}}\\\\[2cm]

{{\\huge\\color{{doradoai}} {nom_esc}}}\\\\[1.5cm]

{{\\Large {fecha_str} \\quad {hora_str}}}\\\\[0.3cm]

{{\\Large {ciu_esc}}}\\\\[0.3cm]

{{\\normalsize
Lat: {lat:.4f}° \\quad
Lon: {lon:.4f}° \\quad
{utc_str}
}}\\\\[0.5cm]

{{\\normalsize
Ascendente: {esc(asc['signo'])} {grado_a_dms(asc['grado'])}
}}\\\\[2.5cm]

\\vfill

{{\\small Generado el {datetime.now().strftime("%d/%m/%Y")}}}

\\end{{titlepage}}


% ── INTRODUCCIÓN ─────────────────────────────────────────────────────────────

\\section*{{Introducción}}

Esta carta natal base no busca definir quién eres.

La astrología se utiliza aquí como lenguaje de observación:
una forma de mirar cómo se organiza tu energía,
qué registros aparecen con más facilidad
y qué dinámicas pueden influir en tu manera de vivir, sostenerte y relacionarte con el entorno.

No se trata de una lectura predictiva ni de una identidad fija.
Es un mapa inicial de orientación.

Las siguientes páginas muestran únicamente las capas principales de la carta:
los ejes más visibles,
la distribución general de la energía
y algunos patrones básicos desde los que sueles moverte.

\\vspace{{0.4cm}}

\\newpage


% ── RUEDA ────────────────────────────────────────────────────────────────

\\section{{Carta Natal}}

\\begin{{center}}
\\includegraphics[width=0.8\\textwidth]{{{ruta_rueda}}}
\\end{{center}}

\\vspace{{0.8cm}}

% ── POSICIONES PRINCIPALES ───────────────────────────────────────────────

\\section{{Posiciones principales}}

\\begin{{center}}

{posiciones}

\\end{{center}}

\\vspace{{0.5cm}}

{{\\small\\itshape
La lectura ampliada desarrolla el mapa completo de posiciones,
aspectos y configuraciones de la carta.
}}

\\vspace{{0.8cm}}
\\Needspace{{5\\baselineskip}}

% ── VISIÓN GENERAL ───────────────────────────────────────────────────────

\\section{{Visión general}}

{esc(vision)}

\\vspace{{0.8cm}}
\\Needspace{{5\\baselineskip}}


% ── LECTURA DE LOS ELEMENTOS ────────────────────────────────────────────

\\section{{Lectura de los elementos}}

{elementos_pdf}

\\vspace{{0.8cm}}
\\Needspace{{10\\baselineskip}}


% ── LOS TRES PILARES ────────────────────────────────────────────────────

\\section{{Los tres pilares}}

\\Needspace{{14\\baselineskip}}
\\subsection{{Sol en {esc(sol.get('signo',''))}}}

{esc(ejes['sol'])}

\\vspace{{0.8cm}}
\\Needspace{{5\\baselineskip}}

\\Needspace{{10\\baselineskip}}
\\subsection{{Luna en {esc(luna.get('signo',''))}}}

{esc(ejes['luna'])}

\\vspace{{0.8cm}}
\\Needspace{{5\\baselineskip}}

\\Needspace{{10\\baselineskip}}
\\subsection{{Ascendente {esc(asc['signo'])}}}

{esc(ejes['asc'])}

\\vspace{{0.8cm}}
\\Needspace{{5\\baselineskip}}

% ── CIERRE ───────────────────────────────────────────────────────────────

\\section{{Cierre}}

Esta carta no busca definirte ni darte una identidad fija.

La astrología se utiliza aquí como lenguaje de observación:
una forma de mirar tendencias, ritmos y maneras de relacionarte con la vida.

La lectura ampliada desarrolla con más profundidad:
los vínculos,
la regulación emocional,
los patrones repetitivos,
la dirección de crecimiento,
las tensiones internas
y las configuraciones principales de la carta.

La lectura completa no busca darte más información.
Busca ayudarte a entender cómo sostener tu vida sin romperte por dentro.

\\vspace{{1cm}}

\\begin{{center}}

{{\\small\\itshape\\color{{grisai}}
Arquitectura Interna
}}

\\end{{center}}

\\end{{document}}
"""

    return latex


# ─── PROGRAMA PRINCIPAL ───────────────────────────────────────────────────────

def generar_pdf_reportlab_base(
    ruta_pdf, carta, nombre, año, mes, dia, hora, minuto,
    ciudad, lat, lon, tz_name, ruta_rueda
):
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.units import cm
    from reportlab.lib import colors

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
        fontSize=17,
        leading=22,
        textColor=colors.HexColor("#8C5A00"),
        spaceBefore=18,
        spaceAfter=8
    )

    cuerpo = ParagraphStyle(
        "CuerpoAI",
        parent=estilos["BodyText"],
        fontName="Times-Roman",
        fontSize=11,
        leading=16,
        spaceAfter=10
    )

    centro = ParagraphStyle(
        "CentroAI",
        parent=cuerpo,
        alignment=TA_CENTER
    )

    contenido = []

    # Portada
    contenido.append(Spacer(1, 2*cm))
    contenido.append(Paragraph("Carta Natal Base", titulo))
    contenido.append(Paragraph("Arquitectura Interna", centro))
    contenido.append(Spacer(1, 1*cm))
    contenido.append(Paragraph(f"<b>{nombre}</b>", centro))
    contenido.append(Paragraph(f"{fecha_str} · {hora_str}", centro))
    contenido.append(Paragraph(ciudad, centro))
    contenido.append(Spacer(1, 0.5*cm))
    contenido.append(Paragraph(
        f"Ascendente: {asc['signo']} {grado_a_dms(asc['grado'])}",
        centro
    ))
    contenido.append(PageBreak())

    # Introducción
    contenido.append(Paragraph("Introducción", subtitulo))
    contenido.append(Paragraph(
        "Esta carta natal base no busca definir quién eres. "
        "La astrología se utiliza aquí como lenguaje de observación: "
        "una forma de mirar cómo se organiza tu energía, qué registros aparecen "
        "con más facilidad y qué dinámicas pueden influir en tu manera de vivir, "
        "sostenerte y relacionarte con el entorno.",
        cuerpo
    ))
    contenido.append(Paragraph(
        "No se trata de una lectura predictiva ni de una identidad fija. "
        "Es un mapa inicial de orientación.",
        cuerpo
    ))

    contenido.append(PageBreak())

    # Rueda
    contenido.append(Paragraph("Carta Natal", subtitulo))
    contenido.append(Image(ruta_rueda, width=13*cm, height=13*cm))
    contenido.append(Spacer(1, 0.5*cm))

    contenido.append(Paragraph("Posiciones principales", subtitulo))
    contenido.append(Paragraph(
        f"Sol en {sol.get('signo','')} — Casa {sol.get('casa','')}<br/>"
        f"Luna en {luna.get('signo','')} — Casa {luna.get('casa','')}<br/>"
        f"Ascendente {asc.get('signo','')}<br/>"
        f"Medio Cielo en {mc.get('signo','')}",
        centro
    ))

    contenido.append(PageBreak())

    # Visión general
    contenido.append(Paragraph("Visión general", subtitulo))
    contenido.append(Paragraph(vision, cuerpo))

    # Tres pilares
    contenido.append(Paragraph("Los tres pilares", subtitulo))

    contenido.append(Paragraph(f"Sol en {sol.get('signo','')}", subtitulo))
    contenido.append(Paragraph(ejes["sol"], cuerpo))

    contenido.append(Paragraph(f"Luna en {luna.get('signo','')}", subtitulo))
    contenido.append(Paragraph(ejes["luna"], cuerpo))

    contenido.append(Paragraph(f"Ascendente {asc.get('signo','')}", subtitulo))
    contenido.append(Paragraph(ejes["asc"], cuerpo))

    # Cierre
    contenido.append(PageBreak())
    contenido.append(Paragraph("Cierre", subtitulo))
    contenido.append(Paragraph(
        "Esta carta no busca definirte ni darte una identidad fija. "
        "La astrología se utiliza aquí como lenguaje de observación: "
        "una forma de mirar tendencias, ritmos y maneras de relacionarte con la vida.",
        cuerpo
    ))
    contenido.append(Paragraph(
        "La lectura completa no busca darte más información. "
        "Busca ayudarte a entender cómo sostener tu vida sin romperte por dentro.",
        cuerpo
    ))

    doc.build(contenido)


def generar_carta_api(nombre, fecha, hora, lugar):

    print("Generando carta para:", nombre)

    try:

        # ── FECHA ─────────────────────────────────────────────

        dia, mes, año = map(int, fecha.split("/"))

        # ── HORA ──────────────────────────────────────────────

        hora_txt, minuto_txt = hora.split(":")
        hora = int(hora_txt)
        minuto = int(minuto_txt)

        # ── GEOLOCALIZACIÓN ──────────────────────────────────

        lat, lon = geocodificar(lugar)

        tz_name = obtener_timezone(lat, lon)

        # ── CÁLCULO CARTA ────────────────────────────────────

        carta = calcular_carta(
            año, mes, dia,
            hora, minuto,
            lat, lon,
            tz_name
        )

        print("DEBUG API")
        print("Fecha:", dia, mes, año)
        print("Hora:", hora, minuto)
        print("Lugar:", lugar)
        print("Lat/Lon:", lat, lon)
        print("TZ:", tz_name)
        print("Sol:", carta["planetas"]["Sol"]["signo"], grado_a_dms(carta["planetas"]["Sol"]["grado"]))
        print("Luna:", carta["planetas"]["Luna"]["signo"], grado_a_dms(carta["planetas"]["Luna"]["grado"]))
        print("ASC:", carta["asc"]["signo"], grado_a_dms(carta["asc"]["grado"]))

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
        ruta_tex = ruta_base + ".tex"
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
    ruta_tex  = ruta_base + ".tex"
    ruta_pdf  = ruta_base + ".pdf"

    print("  Dibujando rueda astrológica...")

    try:
        dibujar_rueda(carta, nombre, ruta_png)
        print(f"  Rueda guardada: {ruta_png}")
    except Exception as e:
        print(f"Error al dibujar la rueda: {e}")
        sys.exit(1)

    print("  Generando carta natal base...")

    latex = generar_latex_ai(
        carta,
        nombre,
        año, mes, dia,
        hora, minuto,
        ciudad,
        lat, lon,
        tz_name,
        ruta_png
    )

    with open(ruta_tex, "w", encoding="utf-8") as f:
        f.write(latex)

    print(f"  LaTeX guardado: {ruta_tex}")

    print("  Compilando PDF...")

    try:
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

            log_path = ruta_base + ".log"

            if os.path.exists(log_path):
                print(f"  Revisa el log en: {log_path}")

                with open(
                    log_path,
                    encoding="latin-1",
                    errors="replace"
                ) as f:
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
                print(
                    resultado.stdout[-2000:]
                    if resultado.stdout
                    else "(vacía)"
                )

    except subprocess.TimeoutExpired:
        print("  Timeout al compilar LaTeX.")

    except FileNotFoundError:
        print("  pdflatex no encontrado.")
        print("  En Windows instala MiKTeX: https://miktex.org/download")
        print("  En Linux/WSL: sudo apt install texlive-full")

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
    print("=" * 60)
    print(f"  Carta natal base de {nombre} generada.")
    print(f"  Ficheros en: {dir_sal}")
    print(f"    - {nombre_f}_carta_base_rueda.png")
    print(f"    - {nombre_f}_carta_base.pdf")
    print("=" * 60)


if __name__ == "__main__":
    main()