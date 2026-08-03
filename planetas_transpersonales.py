#!/usr/bin/env python3
"""
6. Planetas Transpersonales — Arquitectura Interna

Interpreta la forma en que desarrollas libertad, autenticidad
y capacidad de cambio a través de Urano; la sensibilidad,
la intuición y el discernimiento asociados a Neptuno;
y los procesos de transformación, integración y regeneración
representados por Plutón dentro de la carta natal.
"""

import gc
import math
import os
import subprocess
import sys
from datetime import datetime

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pytz
import swisseph as swe
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

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


# ─── CONSTANTES ────────────────────────────────────────────────────────────────

SIGNOS = ["Aries","Tauro","Géminis","Cáncer","Leo","Virgo",
          "Libra","Escorpio","Sagitario","Capricornio","Acuario","Piscis"]

ELEMENTO_SIGNO = {
    "Aries":"Fuego","Tauro":"Tierra","Géminis":"Aire","Cáncer":"Agua",
    "Leo":"Fuego","Virgo":"Tierra","Libra":"Aire","Escorpio":"Agua",
    "Sagitario":"Fuego","Capricornio":"Tierra","Acuario":"Aire","Piscis":"Agua"
}

REGENTE_SIGNO = {
    "Aries":"Marte","Tauro":"Venus","Géminis":"Mercurio","Cáncer":"la Luna",
    "Leo":"el Sol","Virgo":"Mercurio","Libra":"Venus","Escorpio":"Plutón",
    "Sagitario":"Júpiter","Capricornio":"Saturno","Acuario":"Urano","Piscis":"Neptuno"
}

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

ASPECTOS_DEF = [
    ("Conjunción", 0,   10.0, "="),
    ("Sextil",     60,  6.0, "✶"),
    ("Cuadratura", 90,  8.0, "□"),
    ("Trígono",    120, 8.0, "△"),
    ("Oposición",  180, 10.0, "☍"),
    ("Quincuncio", 150, 4.0, "⚻"),
]

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


# ─── TEXTOS: URANO ─────────────────────────────────────────────
URANO_SIGNO = {

"Aries":
"""Necesitas sentir que puedes actuar con libertad y abrir caminos propios sin depender constantemente de lo que otras personas esperan de ti. Los cambios suelen llegar cuando te permites responder con autenticidad a lo que nace dentro de ti.

Es habitual que afrontes las novedades con iniciativa y que no tengas miedo de experimentar cuando percibes que algo necesita renovarse. Sueles reaccionar con rapidez ante las oportunidades que invitan a avanzar de una manera diferente.

Cuando esta energía se desregula puede aparecer la impulsividad, la dificultad para sostener proyectos en el tiempo o la tendencia a romper con situaciones antes de comprender realmente qué necesitas transformar.

Recuperas mejor el equilibrio cuando distingues entre actuar desde la libertad y reaccionar únicamente por necesidad de romper con los límites o escapar de ellos.""",


"Tauro":
"""Necesitas sentir que los cambios respetan tus propios ritmos y que puedes construir una forma de vivir más libre sin perder aquello que realmente tiene valor para ti. La transformación suele producirse cuando descubres nuevas maneras de crear seguridad.

Es habitual que cuestiones las formas tradicionales de entender los recursos, el trabajo o la estabilidad, buscando soluciones más coherentes con tus propios valores que con las expectativas del entorno.

Cuando esta energía se desregula puede aparecer una resistencia excesiva a cualquier cambio o, por el contrario, la necesidad de alterar continuamente aquello que te aporta estabilidad simplemente para sentir que nada te limita.

Recuperas mejor el equilibrio cuando permites que la estabilidad y la innovación colaboren entre sí, en lugar de vivirlas como fuerzas opuestas.""",


"Géminis":
"""Necesitas sentir que tu mente puede explorar nuevas ideas sin quedar atrapada en una única forma de comprender la realidad. Los cambios suelen comenzar cuando descubres perspectivas diferentes que amplían tu manera de pensar.

Es habitual que disfrutes aprendiendo, conectando conceptos y cuestionando aquello que otras personas dan por hecho. Tu curiosidad suele llevarte a encontrar relaciones originales entre ideas muy distintas.

Cuando esta energía se desregula puedes cambiar constantemente de opinión, dispersarte entre demasiados intereses o cuestionarlo todo sin llegar a construir una visión propia.

Recuperas mejor el equilibrio cuando utilizas tu capacidad de innovación para generar comprensión, en lugar de buscar únicamente aquello que resulte diferente o inesperado.""",


"Cáncer":
"""Necesitas sentir que puedes construir seguridad emocional sin permitir que viejos patrones, expectativas familiares o formas heredadas de entender el cuidado condicionen tu manera de vivir. Los cambios más importantes suelen comenzar dentro de ti, aunque tarden en hacerse visibles desde fuera.

Es habitual que desarrolles una forma muy personal de crear vínculos y de entender lo que significa pertenecer. Con el tiempo descubres que sentirte en casa tiene más que ver con la autenticidad que con cumplir determinados modelos.

Cuando esta energía se desregula puede aparecer una necesidad de protegerte mediante el distanciamiento emocional o, por el contrario, romper con todo aquello que te resulta familiar sin haber comprendido realmente qué necesitas dejar atrás.

Recuperas mejor el equilibrio cuando te permites transformar tu mundo emocional sin perder la capacidad de construir raíces que también puedan sostenerte.""",


"Leo":
"""Necesitas sentir que puedes expresar quién eres con libertad, sin adaptar constantemente tu forma de brillar a lo que otras personas esperan de ti. Tu creatividad suele despertar cuando te permites mostrar aquello que te hace diferente.

Es habitual que desarrolles una manera original de liderar, crear o inspirar, aportando una identidad propia allí donde participas. No buscas destacar por llamar la atención, sino por sentir que lo que expresas nace realmente de ti.

Cuando esta energía se desregula puede aparecer la necesidad de diferenciarte a cualquier precio, el rechazo a cualquier referencia externa o la sensación de que solo puedes ser tú si rompes constantemente con lo establecido.

Recuperas mejor el equilibrio cuando comprendes que la autenticidad no necesita demostrarse; simplemente necesita tener espacio para expresarse.""",


"Virgo":
"""Necesitas sentir que puedes mejorar las cosas sin limitarte a repetir métodos conocidos. Los cambios suelen llegar cuando encuentras formas más eficaces, sencillas o coherentes de organizar la realidad.

Es habitual que observes detalles que otras personas pasan por alto y que disfrutes introduciendo mejoras prácticas en aquello que haces. Tu capacidad de innovación suele expresarse a través de pequeños cambios que terminan produciendo grandes diferencias.

Cuando esta energía se desregula puedes cuestionar continuamente los procedimientos sin llegar a consolidar ninguno o sentir frustración porque nada parece suficientemente eficiente.

Recuperas mejor el equilibrio cuando utilizas tu mirada crítica para construir soluciones útiles, en lugar de buscar cambios únicamente por inconformismo.""",


"Libra":
"""Necesitas sentir que las relaciones dejan espacio para que cada persona pueda ser plenamente quien es. Los cambios suelen aparecer cuando descubres nuevas formas de vincularte desde la igualdad y el respeto mutuo.

Es habitual que cuestiones modelos tradicionales de pareja, colaboración o convivencia, buscando relaciones más libres, honestas y equilibradas. Sueles aportar perspectivas diferentes que ayudan a renovar la forma en que las personas se encuentran.

Cuando esta energía se desregula puede aparecer la tendencia a evitar el compromiso por miedo a perder autonomía o a romper vínculos cada vez que sientes que limitan tu libertad.

Recuperas mejor el equilibrio cuando comprendes que una relación sana no reduce tu independencia, sino que también puede convertirse en un espacio donde expresarla con autenticidad.""",


"Escorpio":
"""Necesitas comprender aquello que permanece oculto bajo la superficie y no conformarte con explicaciones sencillas. Los cambios suelen llegar de forma intensa, impulsándote a transformar aquello que ya no resulta verdadero para ti.

Es habitual que desarrolles una gran capacidad para detectar lo que necesita renovarse, incluso antes de que sea evidente para las demás personas. No sueles temer los procesos profundos cuando percibes que conducen a una mayor autenticidad.

Cuando esta energía se desregula puede aparecer la necesidad de provocar cambios constantes, romper por impulso o vivir cada transformación como una lucha contra el entorno.

Recuperas mejor el equilibrio cuando permites que la transformación nazca de una comprensión profunda y no únicamente de la necesidad de destruir lo anterior.""",


"Sagitario":
"""Necesitas sentir que siempre existe una nueva forma de comprender la realidad. Tu libertad crece cuando puedes ampliar horizontes, explorar ideas diferentes y cuestionar las creencias que limitan tu manera de mirar el mundo.

Es habitual que te interese descubrir otras culturas, filosofías o formas de entender la vida, integrando aquello que realmente amplía tu perspectiva sin aceptar una idea únicamente porque sea tradicional.

Cuando esta energía se desregula puedes rechazar cualquier referencia estable, cambiar constantemente de rumbo intelectual o defender la diferencia como un fin en sí mismo.

Recuperas mejor el equilibrio cuando mantienes la mente abierta sin perder la capacidad de dar profundidad y coherencia a aquello que eliges incorporar a tu vida.""",


"Capricornio":
"""Necesitas sentir que las estructuras sobre las que construyes tu vida pueden evolucionar contigo. No sueles aceptar una norma únicamente porque siempre haya sido así; necesitas comprobar si sigue teniendo sentido.

Es habitual que introduzcas cambios de forma estratégica, buscando maneras más eficaces, flexibles o coherentes de asumir responsabilidades. Tu capacidad de innovación suele expresarse transformando sistemas que han quedado obsoletos.

Cuando esta energía se desregula puede aparecer el rechazo a cualquier autoridad, la dificultad para comprometerte con proyectos a largo plazo o la necesidad de romper estructuras antes de haber construido otras que puedan sostenerte.

Recuperas mejor el equilibrio cuando utilizas tu capacidad de cuestionar para construir nuevas bases, en lugar de limitarte a derribar las anteriores.""",


"Acuario":
"""Necesitas sentir que puedes vivir de acuerdo con tus propias convicciones y aportar algo diferente al mundo que te rodea. La libertad no suele ser para ti un deseo puntual, sino una necesidad profunda para desarrollar todo tu potencial.

Es habitual que percibas posibilidades donde otras personas solo ven costumbre y que te resulte natural imaginar formas distintas de organizar la vida, el trabajo o las relaciones. Sueles contribuir al cambio aportando ideas originales que amplían la mirada colectiva.

Cuando esta energía se desregula puede aparecer una excesiva necesidad de diferenciarte, el distanciamiento emocional o el rechazo automático de cualquier tradición simplemente por el hecho de serlo.

Recuperas mejor el equilibrio cuando recuerdas que innovar no consiste en ser diferente a toda costa, sino en aportar aquello que realmente puede enriquecer la vida de las personas.""",


"Piscis":
"""Necesitas sentir que la libertad también incluye la posibilidad de seguir tu intuición y de abrirte a formas de comprensión que van más allá de lo evidente. Los cambios suelen comenzar cuando conectas con aquello que percibes de manera profunda, aunque todavía no puedas explicarlo con palabras.

Es habitual que desarrolles una mirada muy abierta hacia la realidad y que te resulte natural cuestionar los límites rígidos desde la sensibilidad, la creatividad o la compasión. Sueles intuir nuevas posibilidades antes de que puedan verse con claridad.

Cuando esta energía se desregula puede aparecer la dificultad para distinguir entre intuición y evasión, la tendencia a desconectar de la realidad cotidiana o la sensación de vivir siempre un paso por delante de lo que puedes integrar.

Recuperas mejor el equilibrio cuando das una forma concreta a tu sensibilidad y permites que tu intuición encuentre también un espacio en la realidad cotidiana."""

}


URANO_CASA = {

1:
"""Necesitas sentir que puedes mostrarte tal como eres, sin construir una identidad para responder a las expectativas de otras personas. Los cambios más importantes suelen comenzar cuando te permites actuar desde la autenticidad.

Es habitual que proyectes una imagen independiente, original o difícil de encasillar. Sueles atravesar etapas en las que redefinir quién eres forma parte natural de tu evolución.

Cuando esta energía se desregula puede aparecer la necesidad de diferenciarte constantemente, cambiar de dirección de forma impulsiva o rechazar cualquier referencia externa por miedo a perder libertad.

Recuperas mejor el equilibrio cuando comprendes que la autenticidad no consiste en ser diferente, sino en permitir que tu forma de ser evolucione con naturalidad.""",


2:
"""Necesitas construir seguridad sin renunciar a la libertad. Tu relación con los recursos, el trabajo o el dinero suele transformarse a medida que descubres nuevas formas de generar estabilidad.

Es habitual que cuestiones modelos tradicionales sobre el valor, las posesiones o la economía, buscando caminos más acordes con tus propios principios.

Cuando esta energía se desregula pueden aparecer cambios económicos bruscos, dificultad para sostener proyectos o la sensación de que cualquier compromiso limita tu independencia.

Recuperas mejor el equilibrio cuando construyes una estabilidad suficientemente flexible como para acompañar tu necesidad de evolución.""",


3:
"""Necesitas sentir que tu mente puede explorar nuevas ideas sin quedar limitada por formas rígidas de pensar. Aprendes mejor cuando descubres aquello que despierta tu curiosidad.

Es habitual que tengas una forma original de comunicarte, aprender o relacionarte con el conocimiento. Sueles establecer conexiones que otras personas no perciben con facilidad.

Cuando esta energía se desregula puede aparecer dispersión mental, exceso de estímulos o dificultad para sostener una misma línea de pensamiento.

Recuperas mejor el equilibrio cuando das espacio a tu creatividad mental sin perder capacidad para integrar lo que descubres.""",


4:
"""Necesitas construir un lugar en el que puedas sentirte libre para ser quien eres. A lo largo de la vida es frecuente que cambie tu manera de entender el hogar, la familia o el sentido de pertenencia.

Es habitual que cuestiones dinámicas familiares heredadas y que busques construir una forma propia de vivir los vínculos más íntimos.

Cuando esta energía se desregula puede aparecer inestabilidad emocional, dificultad para echar raíces o necesidad de romper continuamente con aquello que te resulta conocido.

Recuperas mejor el equilibrio cuando descubres que también es posible crear un hogar que respete tu necesidad de libertad.""",


5:
"""Necesitas expresar tu creatividad de forma auténtica, sin adaptarla constantemente a las expectativas del entorno. La inspiración suele aparecer cuando te permites experimentar.

Es habitual que desarrolles intereses originales y que disfrutes creando, jugando o enamorándote de maneras poco convencionales.

Cuando esta energía se desregula puede aparecer una búsqueda constante de estímulos, dificultad para sostener proyectos creativos o relaciones marcadas por cambios repentinos.

Recuperas mejor el equilibrio cuando permites que tu creatividad encuentre continuidad sin perder espontaneidad.""",


6:
"""Necesitas que tu vida cotidiana tenga espacio para la libertad y la innovación. Los cambios suelen aparecer cuando una rutina deja de tener sentido para ti.

Es habitual que busques nuevas formas de trabajar, organizarte o cuidar de tu bienestar, introduciendo mejoras que hagan tu día a día más coherente contigo.

Cuando esta energía se desregula puede resultar difícil mantener hábitos estables o sostener responsabilidades que percibes como excesivamente rígidas.

Recuperas mejor el equilibrio cuando construyes rutinas flexibles que apoyen tu evolución en lugar de limitarla.""",


7:
"""Necesitas relaciones en las que ambas personas puedan crecer sin perder su individualidad. La libertad suele convertirse en un ingrediente esencial para que los vínculos puedan mantenerse vivos.

Es habitual que atraigas personas independientes, poco convencionales o que impulsan cambios importantes en tu manera de relacionarte.

Cuando esta energía se desregula pueden aparecer relaciones inestables, dificultad para comprometerte o necesidad de tomar distancia cuando sientes que pierdes autonomía.

Recuperas mejor el equilibrio cuando descubres que el compromiso y la libertad no tienen por qué excluirse mutuamente.""",


8:
"""Necesitas comprender profundamente los procesos de cambio que transforman la vida. Las grandes crisis suelen convertirse también en oportunidades para renovarte desde dentro.

Es habitual que desarrolles una capacidad especial para detectar aquello que necesita evolucionar, incluso cuando permanece oculto bajo la superficie.

Cuando esta energía se desregula pueden aparecer cambios bruscos, necesidad de controlar lo imprevisible o dificultad para confiar durante los procesos de transformación.

Recuperas mejor el equilibrio cuando permites que la transformación siga su propio ritmo sin intentar anticiparlo todo.""",


9:
"""Necesitas ampliar continuamente tu manera de comprender el mundo. Tu visión cambia a medida que descubres nuevas ideas, culturas o formas de interpretar la realidad.

Es habitual que cuestiones creencias establecidas y que desarrolles una filosofía de vida construida a partir de tu propia experiencia.

Cuando esta energía se desregula puedes rechazar cualquier referencia estable o cambiar constantemente de visión sin llegar a integrar lo aprendido.

Recuperas mejor el equilibrio cuando mantienes una mente abierta sin perder profundidad ni coherencia.""",


10:
"""Necesitas desarrollar una trayectoria profesional coherente con quien eres, aunque eso implique apartarte de los caminos más habituales. Los cambios importantes suelen marcar tu forma de construir la vocación.

Es habitual que aportes innovación en tu profesión o que desarrolles una carrera poco convencional, adaptándote a diferentes etapas de tu vida.

Cuando esta energía se desregula puede aparecer dificultad para mantener proyectos a largo plazo o una necesidad constante de reinventarte sin consolidar lo construido.

Recuperas mejor el equilibrio cuando permites que tu evolución profesional tenga tanto libertad como continuidad.""",


11:
"""Necesitas formar parte de grupos donde puedas aportar tu visión sin renunciar a tu individualidad. Suelen motivarte los proyectos que impulsan cambios colectivos o nuevas formas de colaboración.

Es habitual que encuentres personas con intereses poco convencionales y que participes en redes donde las ideas circulan con libertad.

Cuando esta energía se desregula puedes sentir que no encajas en ningún grupo o romper vínculos cada vez que aparecen diferencias.

Recuperas mejor el equilibrio cuando descubres que colaborar no implica dejar de ser quien eres.""",


12:
"""Necesitas escuchar aquello que emerge desde el mundo interior antes de hacerse consciente. Muchos de tus cambios comienzan silenciosamente, transformando poco a poco la manera en que comprendes la vida.

Es habitual que percibas intuiciones repentinas o que necesites periodos de retiro para integrar procesos internos profundos antes de darles una expresión externa.

Cuando esta energía se desregula puede aparecer sensación de desconexión, inquietud difícil de explicar o necesidad de aislarte sin comprender qué está ocurriendo.

Recuperas mejor el equilibrio cuando das espacio a tu mundo interior y permites que los cambios maduren antes de intentar comprenderlos racionalmente."""
}


URANO_COMBINACIONES = {

"Sol": (
    "Tu necesidad de libertad está profundamente unida a la construcción de tu identidad. Necesitas sentir que puedes vivir de acuerdo con quien realmente eres, aunque eso implique apartarte de expectativas, modelos o caminos que otras personas consideran adecuados.\n\n"

    "Cuando ambas partes colaboran, desarrollas una gran capacidad para actuar con autenticidad, impulsar cambios y abrir nuevas posibilidades tanto para ti como para quienes te rodean. Tu individualidad encuentra una forma natural de expresarse sin necesidad de buscar constantemente la diferencia.\n\n"

    "Esta combinación te invita a distinguir entre serte fiel y rechazar cualquier límite por el simple hecho de existir. La verdadera libertad no consiste en oponerse a todo, sino en elegir conscientemente aquello que realmente representa quién eres."
),

"Luna": (
    "Tu necesidad de libertad también alcanza tu mundo emocional. Necesitas sentir que puedes experimentar, expresar y comprender tus emociones sin engancharte en viejos patrones afectivos o formas heredadas de vivir los vínculos.\n\n"

    "Cuando ambas partes colaboran, desarrollas una gran capacidad para adaptarte a los cambios, responder con flexibilidad y construir una relación más libre y consciente con tu mundo interior. Tu sensibilidad puede convertirse en una fuente de renovación tanto para ti como para las personas que te rodean.\n\n"

    "Esta combinación te invita a observar cuándo proteger tu independencia emocional favorece tu bienestar y cuándo se convierte en una forma de evitar la intimidad o la vulnerabilidad. La libertad emocional también puede construirse compartiendo lo que sientes."
),

"Mercurio": (
    "Tu manera de pensar necesita espacio para cuestionar, experimentar y descubrir nuevas perspectivas. Rara vez aceptas una idea únicamente porque siempre haya sido así; necesitas comprenderla antes de hacerla propia.\n\n"

    "Cuando ambas partes colaboran, desarrollas una mente original, rápida y especialmente capaz de establecer conexiones que otras personas no perciben. Sueles aportar ideas innovadoras y encontrar soluciones diferentes a problemas conocidos.\n\n"

    "Esta combinación te invita a distinguir entre pensar de forma independiente y cuestionarlo todo de manera automática. La originalidad gana profundidad cuando también puede dialogar con la experiencia, el conocimiento y la realidad."
),


"Venus": (
    "Tu necesidad de libertad influye directamente en la forma en que construyes tus relaciones, expresas el afecto y descubres aquello que realmente valoras. Necesitas sentir que los vínculos respetan tu individualidad y te permiten seguir creciendo como persona.\n\n"

    "Cuando ambas partes colaboran, desarrollas una forma auténtica de relacionarte, abierta a nuevas maneras de compartir, disfrutar y construir cercanía. Sueles valorar la honestidad, la espontaneidad y el respeto mutuo por encima de las convenciones.\n\n"

    "Esta combinación te invita a distinguir entre una relación que limita tu libertad y el miedo a permanecer en un vínculo cuando aparecen la rutina, el compromiso o las diferencias. La autenticidad también puede construirse dentro de una relación estable."
),

"Marte": (
    "Tu impulso de actuar necesita libertad para elegir su propio camino. Te resulta más fácil movilizar energía cuando sientes que las decisiones nacen de ti y no únicamente de expectativas o imposiciones externas.\n\n"

    "Cuando ambas partes colaboran, actúas con iniciativa, rapidez y una gran capacidad para responder a situaciones nuevas. Sueles encontrar soluciones originales y desenvolverte con soltura allí donde es necesario improvisar o abrir caminos diferentes.\n\n"

    "Esta combinación te invita a observar cuándo la necesidad de actuar con independencia favorece tu desarrollo y cuándo puede convertirse en impulsividad, impaciencia o dificultad para sostener el esfuerzo a largo plazo. La libertad también necesita dirección."
),

"Saturno": (
    "Urano y Saturno representan dos necesidades igualmente importantes: una busca abrir nuevos caminos y la otra construir una base sólida sobre la que sostenerlos. Una impulsa el cambio; la otra aporta continuidad, estructura y experiencia.\n\n"

    "Cuando ambas partes colaboran, puedes transformar aquello que ha quedado obsoleto sin perder de vista lo que merece conservarse. Tienes la capacidad de introducir cambios profundos de forma responsable, convirtiendo las ideas innovadoras en proyectos capaces de mantenerse en el tiempo.\n\n"

    "Esta combinación te invita a evitar dos extremos: aferrarte a estructuras que ya no favorecen tu desarrollo o romperlas antes de haber construido unas nuevas. La verdadera innovación no consiste únicamente en cambiar, sino en crear algo que también pueda sostenerse."
),


"Neptuno": (
    "La necesidad de libertad de Urano se encuentra con la sensibilidad y la capacidad de trascender los límites de Neptuno. Una parte de ti busca despertar nuevas posibilidades; la otra percibe aquello que todavía no puede explicarse con claridad.\n\n"

    "Cuando ambas partes colaboran, desarrollas una gran capacidad para intuir cambios, inspirar nuevas formas de comprender la realidad y abrir espacios donde la creatividad y la innovación pueden convivir. La imaginación encuentra caminos originales para tomar forma.\n\n"

    "Esta combinación te invita a distinguir entre una intuición que amplía tu consciencia y la tendencia a perder contacto con la realidad. La inspiración se vuelve más valiosa cuando también puede encontrar una expresión concreta."
),

"Plutón": (
    "Urano y Plutón comparten la necesidad de transformar aquello que ha dejado de tener sentido, aunque cada uno lo hace de una manera diferente. Urano impulsa el cambio abriendo nuevas posibilidades; Plutón lo hace atravesando procesos profundos de transformación.\n\n"

    "Cuando ambas partes colaboran, desarrollas una gran capacidad para impulsar cambios significativos, comprender el momento en que una etapa ha terminado y participar activamente en procesos de renovación tanto personales como colectivos.\n\n"

    "Esta combinación te invita a observar si el deseo de transformar puede llevarte a vivir en un cambio permanente. No toda evolución exige romper continuamente con el pasado; muchas veces también consiste en integrar profundamente aquello que ya ha cambiado."
),

"Ascendente": (
    "Cuando Urano y el Ascendente interactúan, tu forma de presentarte al mundo transmite independencia, autenticidad y una cierta dificultad para encajar en moldes prefijados. Las personas suelen percibir en ti una manera propia de mirar la vida.\n\n"

    "Esta combinación favorece una presencia capaz de abrir nuevas perspectivas, cuestionar inercias y aportar originalidad sin necesidad de buscar protagonismo. Tu forma de estar invita a otras personas a contemplar posibilidades diferentes.\n\n"

    "La integración aparece cuando permites que esa autenticidad se exprese con naturalidad, sin sentir la necesidad de demostrar constantemente que eres diferente."
),

"Nodo Norte": (
    "Cuando Urano y el Nodo Norte se relacionan, aprender a vivir con mayor autenticidad forma parte importante de tu proceso evolutivo. La vida suele invitarte a cuestionar patrones conocidos para descubrir una manera más libre y consciente de expresar quién eres.\n\n"

    "Esta combinación favorece aquellas experiencias que amplían tu perspectiva, despiertan nuevas posibilidades y te animan a construir un camino propio, incluso cuando eso implique alejarte de lo esperado.\n\n"

    "El crecimiento aparece cuando utilizas la libertad para acercarte a quien realmente eres y no únicamente para alejarte de aquello que ya conoces."
),

"Nodo Sur": (
    "Cuando Urano y el Nodo Sur interactúan, es posible que exista una tendencia conocida a buscar independencia, cuestionar lo establecido o distanciarte de aquello que percibes como limitante. Esa capacidad puede convertirse en un recurso importante cuando se utiliza de forma consciente.\n\n"

    "Esta combinación invita a reconocer todo lo que ya sabes sobre la libertad sin engancharte en la necesidad de demostrar continuamente tu autonomía o de romper con cualquier estructura.\n\n"

    "La evolución consiste en conservar tu capacidad para pensar con independencia mientras desarrollas también nuevas formas de construir estabilidad y cooperación."
),

"Quirón": (
    "Cuando Urano y Quirón se relacionan, la experiencia de sentir que tu diferencia no era comprendida o de encontrarte fuera de lugar puede haber dejado una huella importante. En algunos momentos puedes haber vivido la autenticidad como algo que te alejaba de otras personas en lugar de favorecer el encuentro.\n\n"

    "Con el tiempo, esa misma experiencia puede ayudarte a desarrollar una comprensión profunda del valor que tiene respetar la individualidad de cada persona. Tu propia diferencia puede convertirse en una fuente de creatividad, empatía y renovación.\n\n"

    "Esta combinación recuerda que no necesitas ocultar aquello que te diferencia ni convertirlo en una barrera frente al mundo. La autenticidad encuentra su mayor fuerza cuando puede expresarse sin aislarte."
),

"Lilith": (
    "Cuando Urano y Lilith interactúan, existe una fuerte necesidad de cuestionar normas, límites o expectativas que no representan tu experiencia. Resulta difícil aceptar una autoridad únicamente porque siempre haya estado ahí; necesitas comprobar qué tiene sentido conservar y qué necesita cambiar.\n\n"

    "Cuando ambas partes colaboran, desarrollas una gran capacidad para abrir conversaciones que otras personas evitan, defender la libertad de ser quien eres y dar espacio a formas de vivir que no siempre encuentran reconocimiento.\n\n"

    "Esta combinación te invita a recordar que cuestionar una norma no exige rechazar todas las demás. La libertad gana profundidad cuando nace de la consciencia y no únicamente de la oposición."
),
}


URANO_TEXTOS_TIPO_ASPECTO = {

    "Conjunción": (
        "Urano se encuentra muy unido a esta parte de ti, de modo que la necesidad de libertad, autenticidad y cambio se expresa directamente a través de ella. "
        "Ambas funciones actúan de forma inseparable y participan conjuntamente en muchas de tus decisiones.\n\n"

        "Esta unión aporta una gran capacidad para cuestionar inercias, abrir nuevas posibilidades y responder con creatividad cuando una situación necesita renovarse. "
        "También puede hacer que los cambios aparezcan con intensidad o que resulte difícil aceptar aquello que limita tu necesidad de independencia.\n\n"

        "La integración aparece cuando permites que la libertad impulse tu evolución sin convertir el cambio en una necesidad permanente. "
        "No todo necesita transformarse; algunas estructuras también pueden sostener aquello que deseas construir."
    ),

    "Sextil": (
        "Urano mantiene con esta parte de ti una relación que facilita la innovación y la apertura a nuevas posibilidades. "
        "Existe una colaboración natural que suele activarse cuando decides explorar caminos diferentes o cuestionar aquello que ha dejado de tener sentido.\n\n"

        "Cuando aprovechas conscientemente esta conexión, puedes introducir cambios de forma flexible, encontrar soluciones originales y adaptarte con rapidez a situaciones nuevas. "
        "La creatividad encuentra un espacio práctico para desarrollarse.\n\n"

        "El aprendizaje consiste en no dejar esta capacidad únicamente como una posibilidad. "
        "Cuanto más incorporas la innovación a tu vida cotidiana, más natural resulta evolucionar sin necesidad de esperar a que las circunstancias te obliguen a cambiar."
    ),

    "Trígono": (
        "Urano y esta parte de ti colaboran con naturalidad. "
        "La autenticidad, la creatividad y la capacidad de adaptación suelen surgir de forma espontánea cuando ambas funciones trabajan juntas.\n\n"

        "Esta facilidad favorece una actitud abierta ante los cambios y una notable capacidad para descubrir soluciones que otras personas quizá no contemplan. "
        "También puede hacer que des por sentada una cualidad que constituye uno de tus recursos más valiosos.\n\n"

        "El equilibrio consiste en utilizar conscientemente esa capacidad innovadora. "
        "La originalidad adquiere mayor valor cuando encuentra una dirección clara y una aplicación concreta."
    ),

    "Cuadratura": (
        "Urano y esta parte de ti no siempre avanzan en la misma dirección. "
        "La necesidad de libertad o de introducir cambios puede entrar en tensión con otras necesidades internas, generando inquietud, impulsividad o dificultad para encontrar estabilidad.\n\n"

        "En algunos momentos puedes sentir que cualquier límite resulta excesivo; en otros, los cambios aparecen de forma brusca cuando una situación lleva demasiado tiempo sin evolucionar.\n\n"

        "Esta tensión te invita a descubrir una forma más consciente de transformar tu vida. "
        "La libertad gana profundidad cuando no necesita surgir únicamente como reacción frente a aquello que limita."
    ),

    "Oposición": (
        "Urano y esta parte de ti buscan un equilibrio que suele desarrollarse con el tiempo. "
        "Es posible que inicialmente percibas la libertad, la originalidad o la capacidad de romper inercias reflejadas en otras personas o en situaciones externas.\n\n"

        "También puedes alternar entre periodos de gran necesidad de independencia y otros en los que buscas estabilidad o referencias más conocidas. "
        "Ambas experiencias forman parte del mismo proceso de integración.\n\n"

        "El aprendizaje consiste en reconocer dentro de ti aquello que primero identificas fuera. "
        "Cuando ambas funciones pueden dialogar, la libertad deja de depender de las circunstancias y se convierte en una forma consciente de vivir."
    ),

    "Quincuncio": (
        "La relación entre Urano y esta parte de ti requiere ajustes frecuentes. "
        "La necesidad de cambio no siempre encaja fácilmente con el ritmo de la otra función, por lo que es habitual atravesar periodos de adaptación antes de encontrar un equilibrio estable.\n\n"

        "Es posible que algunas transformaciones necesiten más tiempo del que inicialmente desearías o que descubras nuevas posibilidades mientras todavía estás consolidando las anteriores.\n\n"

        "El aprendizaje consiste en respetar los tiempos de cada proceso. "
        "La innovación encuentra una base mucho más sólida cuando puede integrarse poco a poco en tu vida, en lugar de exigir una transformación inmediata."
    ),
}


URANO_INTEGRACION = {

    "necesidades": {
        "titulo": "Lo que Urano necesita",

        "texto": (
            "Cada Urano encuentra una forma diferente de buscar libertad, cuestionar lo establecido y abrir nuevas posibilidades, "
"pero existe una necesidad común: disponer de espacio para evolucionar sin que estructuras que ya no representan quién eres limiten ese proceso.\n\n"

            "Urano necesita espacio para pensar de otra manera, explorar alternativas y responder con autenticidad a los cambios internos que van apareciendo. "
            "Necesita sentir que existe margen para revisar decisiones, transformar hábitos y construir una forma de vida más coherente.\n\n"

            "No todo cambio libera a Urano. Romper, abandonar o rechazar una estructura no siempre conduce a una mayor autenticidad. "
            "Con frecuencia necesita tiempo para distinguir entre una transformación necesaria y una reacción impulsiva frente a la incomodidad, el límite o la rutina.\n\n"

            "Cuando respetas tu necesidad de libertad sin convertirla en una exigencia permanente, Urano deja de buscar continuamente una salida y recupera su capacidad para introducir cambios que realmente amplían tu forma de vivir."
        )
    },

    "cuidar": {
        "titulo": "Cómo cuidar tu Urano",

        "texto": (
            "Cuidar de Urano no significa cambiarlo todo ni vivir en una búsqueda constante de novedades. "
            "Significa crear espacio para que tu individualidad pueda expresarse y evolucionar sin quedar anulada por la costumbre o las expectativas externas.\n\n"

            "Urano se fortalece cuando cuestionas una idea que ya no encaja contigo, pruebas una forma diferente de hacer las cosas, compartes tiempo con personas que amplían tu mirada o introduces pequeñas variaciones en una rutina que se ha vuelto demasiado rígida.\n\n"

            "También necesita continuidad. Una posibilidad nueva no siempre puede integrarse de inmediato, y una idea original necesita tiempo, práctica y estructura para convertirse en algo real.\n\n"

            "Cuidar esta función implica escuchar la inquietud antes de que se convierta en ruptura. "
            "No toda incomodidad exige abandonar lo que estás viviendo, pero sí puede estar señalando que algo necesita revisarse, actualizarse o encontrar más espacio."
        )
    },

    "equilibrio": {
        "titulo": "Cuando Urano encuentra equilibrio",

        "texto": (
            "Cuando Urano funciona de manera equilibrada, la libertad no depende de rechazar todo límite ni de demostrar constantemente que eres diferente.\n\n"

            "Existe apertura al cambio sin impulsividad, independencia sin aislamiento y capacidad para cuestionar lo conocido sin despreciar aquello que todavía puede resultar útil.\n\n"

            "Puedes reconocer cuándo una estructura necesita renovarse, introducir cambios sin destruir lo que sí funciona y expresar tu individualidad sin convertirla en una distancia permanente respecto a las demás personas.\n\n"

            "No significa vivir sin estabilidad. "
            "Significa construir una estabilidad suficientemente flexible como para seguir evolucionando sin dejar de sostener lo que tiene valor para ti."
        )
    },

    "desregulacion": {
        "titulo": "Cuando Urano pierde equilibrio",

        "texto": (
            "Cuando Urano pierde equilibrio, la necesidad de libertad puede convertirse en inquietud, ruptura o rechazo automático de cualquier límite.\n\n"

            "Puede aparecer la tendencia a cambiar de dirección antes de haber comprendido qué necesitabas transformar, abandonar procesos cuando empiezan a exigir continuidad o vivir la rutina como una amenaza para tu identidad.\n\n"

            "En otras ocasiones ocurre lo contrario: se contiene durante demasiado tiempo la necesidad de cambio, hasta que la tensión se expresa de forma brusca, inesperada o difícil de integrar. "
            "También puede aparecer distanciamiento emocional, dificultad para comprometerte o una sensación persistente de no encajar en ningún lugar.\n\n"

            "No significa que tu necesidad de libertad sea excesiva. "
            "Con frecuencia indica que necesitas encontrar una forma más consciente de introducir cambios, expresar tu diferencia y revisar los límites antes de sentir que la única opción posible es romper con todo."
        )
    },

    "pregunta": {
        "titulo": "Una pregunta para observarte",

        "texto": (
            "Mientras leías este capítulo quizá has reconocido formas habituales de buscar independencia, responder a los cambios o cuestionar aquello que ya no tiene sentido para ti. "
            "También es posible que algunas aparezcan únicamente en determinados vínculos, decisiones o etapas de tu vida.\n\n"

            "Más allá de la posición de Urano en tu carta, la pregunta importante es otra:\n\n"

            "¿En qué parte de tu vida necesitas hoy más libertad para ser quien eres?\n\n"

            "Puede tratarse de una relación, una rutina, una forma de trabajar, una idea sobre ti o una decisión que llevas tiempo posponiendo.\n\n"

            "También puede ayudarte observar dónde estás buscando un cambio externo cuando lo que realmente necesitas es modificar tu forma de responder. "
            "Distinguir entre libertad y huida es una manera de transformar tu vida con mayor consciencia."
        )
    },

    "integracion": {
        "titulo": "Integración",

        "texto": (
            "Ser libre no consiste únicamente en romper con lo conocido.\n\n"

            "También implica reconocer qué necesita cambiar, qué merece conservarse y qué nuevas estructuras pueden sostener mejor la persona en la que te estás convirtiendo.\n\n"

            "Conocer tu Urano no pretende decirte cuándo llegarán cambios inesperados ni describirte como alguien rebelde o imprevisible. "
            "Pretende ayudarte a comprender dónde necesitas más espacio, cómo respondes cuando algo limita tu autenticidad y en qué momentos la necesidad de independencia puede llevarte a actuar antes de haber escuchado todo lo que estaba ocurriendo.\n\n"

            "Cada vez que cuestionas una forma de vivir que ya no te representa y construyes una alternativa más coherente, algo dentro de ti recupera movimiento.\n\n"

            "Porque la libertad no consiste en vivir sin estructura, sino en participar conscientemente en la construcción de una vida que también pueda evolucionar contigo."
        )
    }
}


# ─── TEXTOS: NEPTUNO ─────────────────────────────────────────────
NEPTUNO_SIGNO = {

    "Aries": (
        "Neptuno en Aries necesita sentir que la inspiración puede convertirse en movimiento. "
        "Tu sensibilidad no se conforma con permanecer en el terreno de las ideas o de la imaginación: necesita encontrar una acción, una iniciativa o una experiencia a través de la que expresarse.\n\n"

        "Cuando esta posición funciona de manera equilibrada, puedes actuar guiándote por una intuición muy inmediata. "
        "Existe capacidad para iniciar proyectos inspiradores, defender ideales y abrir caminos que nacen de una percepción difícil de explicar, pero profundamente movilizadora.\n\n"

        "La desregulación puede aparecer cuando confundes intuición con impulso, actúas antes de comprender lo que estás sintiendo o persigues una imagen ideal sin valorar sus consecuencias. "
        "También puedes alternar entre una gran intensidad inicial y la pérdida repentina de dirección.\n\n"

        "Recuperas equilibrio cuando introduces una pausa entre lo que imaginas y lo que haces. "
        "Dar una forma concreta a la inspiración, avanzar paso a paso y comprobar cómo responde la realidad permite que tu sensibilidad se convierta en una fuerza creadora."
    ),

    "Tauro": (
        "Neptuno en Tauro necesita que la sensibilidad encuentre una forma concreta, estable y sensorial de expresarse. "
        "La belleza, la naturaleza, el cuerpo, la música o el contacto con la materia pueden ayudarte a percibir aquello que no siempre puedes explicar con palabras.\n\n"

        "Cuando esta posición funciona de manera equilibrada, desarrollas una gran capacidad para transmitir calma, crear belleza y convertir una percepción sutil en algo tangible. "
        "Puedes encontrar profundidad en experiencias sencillas y reconocer el valor emocional o simbólico de aquello que te rodea.\n\n"

        "La desregulación puede aparecer cuando buscas seguridad idealizando personas, recursos o situaciones, o cuando utilizas el placer y la comodidad para evitar emociones difíciles. "
        "También puede costarte reconocer que algo necesita cambiar cuando te proporciona una sensación conocida de estabilidad.\n\n"

        "Recuperas equilibrio cuando vuelves al cuerpo y a la realidad concreta. "
        "Observar tus necesidades reales, cuidar tus ritmos y diferenciar entre lo que verdaderamente te nutre y lo que solo te ayuda a evadirte permite que tu sensibilidad encuentre una base sólida."
    ),

    "Géminis": (
        "Neptuno en Géminis necesita explorar el poder de las palabras, las ideas y las conexiones mentales. "
        "Tu imaginación puede abrir múltiples asociaciones y captar matices que no siempre siguen una lógica lineal.\n\n"

        "Cuando esta posición funciona de manera equilibrada, desarrollas una comunicación intuitiva, creativa y especialmente sensible a lo que no se dice de forma explícita. "
        "Puedes traducir emociones, imágenes o percepciones complejas en relatos, conversaciones o ideas capaces de inspirar a otras personas.\n\n"

        "La desregulación puede aparecer cuando se mezclan intuición, suposición y realidad, dificultando distinguir qué sabes, qué imaginas y qué has interpretado. "
        "También puede haber dispersión, mensajes ambiguos o tendencia a adaptar tu pensamiento a cada entorno hasta perder tu propio criterio.\n\n"

        "Recuperas equilibrio cuando verificas la información, ordenas tus ideas y expresas con claridad qué es un hecho y qué es una percepción. "
        "Escribir, conversar y poner nombre a lo que sientes ayuda a que la imaginación se convierta en comprensión."
    ),

    "Cáncer": (
        "Neptuno en Cáncer necesita una conexión emocional profunda y un espacio que te ofrezca protección sin dejar de percibir lo que ocurre alrededor. "
        "Tu sensibilidad está especialmente vinculada a la memoria, los vínculos familiares y la necesidad de pertenencia.\n\n"

        "Cuando esta posición funciona de manera equilibrada, puedes comprender con gran delicadeza las necesidades emocionales de otras personas. "
        "Existe capacidad para cuidar, acompañar y crear ambientes en los que la vulnerabilidad encuentra acogida.\n\n"

        "La desregulación puede aparecer cuando absorbes estados emocionales ajenos, idealizas el pasado o asumes responsabilidades afectivas que no te corresponden. "
        "También puedes protegerte refugiándote en recuerdos, fantasías o vínculos que ofrecen seguridad, pero dificultan tu desarrollo.\n\n"

        "Recuperas equilibrio cuando distingues entre sentir con alguien y sentir por esa persona. "
        "Cuidar tus límites emocionales, reconocer tus propias necesidades y construir una seguridad interna permite que la empatía no se convierta en sobrecarga."
    ),

    "Leo": (
        "Neptuno en Leo necesita expresar la imaginación, la sensibilidad y el mundo interior de una forma creativa y personal. "
        "Existe una necesidad profunda de dar vida a algo que refleje tu visión y permita que otras personas conecten con ella.\n\n"

        "Cuando esta posición funciona de manera equilibrada, puedes inspirar a través del arte, la presencia, la creatividad o una forma especialmente cálida de compartir lo que sientes. "
        "Tu capacidad expresiva puede ayudar a hacer visible aquello que otras personas apenas alcanzan a intuir.\n\n"

        "La desregulación puede aparecer cuando buscas reconocimiento a través de una imagen idealizada de ti, confundes admiración con afecto o depositas demasiadas expectativas en tu capacidad para inspirar o salvar a otras personas. "
        "También puede costarte aceptar una respuesta menos intensa de la que imaginabas.\n\n"

        "Recuperas equilibrio cuando creas por la necesidad de expresar algo verdadero, no únicamente para recibir confirmación. "
        "Aceptar tus límites, permitirte aprender y sostener la creatividad incluso cuando no existe reconocimiento inmediato fortalece tu centro."
    ),

    "Virgo": (
        "Neptuno en Virgo necesita encontrar una forma útil y concreta de expresar su sensibilidad. "
        "Tu percepción se orienta hacia los detalles, las necesidades cotidianas y aquello que puede mejorar, aliviarse u organizarse.\n\n"

        "Cuando esta posición funciona de manera equilibrada, puedes unir intuición y capacidad práctica. "
        "Existe una sensibilidad especial para detectar lo que falta, comprender necesidades poco visibles y ofrecer ayuda de una manera precisa y cuidadosa.\n\n"

        "La desregulación puede aparecer cuando intentas alcanzar una perfección imposible, te haces cargo de todo lo que percibes o utilizas la actividad constante para no detenerte a sentir. "
        "También puedes dudar de tu intuición si no encuentras una explicación racional inmediata.\n\n"

        "Recuperas equilibrio cuando aceptas que no todo puede corregirse, resolverse o controlarse. "
        "Establecer prioridades, cuidar tus rutinas sin rigidizarlas y permitir espacios de descanso ayuda a que tu sensibilidad se convierta en servicio sin transformarse en agotamiento."
    ),

    "Libra": (
        "Neptuno en Libra necesita experimentar belleza, armonía y una conexión profunda dentro de los vínculos. "
        "Tu sensibilidad se activa especialmente en el encuentro con otras personas y en la búsqueda de relaciones que reflejen un ideal de comprensión y equilibrio.\n\n"

        "Cuando esta posición funciona de manera equilibrada, puedes percibir con gran delicadeza los matices de una relación, mediar entre perspectivas distintas y crear espacios de encuentro basados en la empatía y el respeto.\n\n"

        "La desregulación puede aparecer cuando idealizas a otras personas, evitas el conflicto para conservar una imagen de armonía o adaptas demasiado tus necesidades con tal de mantener el vínculo. "
        "También puedes enamorarte de lo que una relación podría llegar a ser más que de lo que realmente está siendo.\n\n"

        "Recuperas equilibrio cuando observas los vínculos tal como son, no únicamente como deseas que sean. "
        "Expresar tus límites, sostener las diferencias y reconocer tus propias necesidades permite que la conexión no dependa de desaparecer dentro de la relación."
    ),

    "Escorpio": (
        "Neptuno en Escorpio necesita explorar aquello que permanece oculto bajo la superficie. "
        "Tu sensibilidad puede orientarse hacia emociones intensas, procesos de transformación y dimensiones de la experiencia que otras personas prefieren evitar.\n\n"

        "Cuando esta posición funciona de manera equilibrada, desarrollas una gran capacidad para acompañar crisis, comprender motivaciones profundas y percibir los cambios internos antes de que puedan expresarse con claridad.\n\n"

        "La desregulación puede aparecer cuando se difuminan los límites dentro de relaciones intensas, confundes conexión con fusión o te enganchas a temores, sospechas o fantasías difíciles de contrastar. "
        "También puede existir fascinación por situaciones que generan intensidad, aunque no proporcionen bienestar.\n\n"

        "Recuperas equilibrio cuando das nombre a lo que percibes y diferencias entre intuición, miedo y deseo. "
        "Compartir la vulnerabilidad sin renunciar a tus límites permite que la profundidad se convierta en transformación y no en pérdida de ti."
    ),

    "Sagitario": (
        "Neptuno en Sagitario necesita conectar la experiencia con una visión amplia de la vida. "
        "Tu sensibilidad busca significado, inspiración y una perspectiva que permita comprender lo vivido más allá de sus circunstancias inmediatas.\n\n"

        "Cuando esta posición funciona de manera equilibrada, puedes transmitir esperanza, despertar nuevas preguntas y abrir la mirada hacia realidades diferentes. "
        "La imaginación, la filosofía, los viajes o la exploración de otros sistemas de pensamiento pueden ampliar profundamente tu percepción.\n\n"

        "La desregulación puede aparecer cuando idealizas una creencia, una enseñanza o una promesa de futuro y dejas de contrastarla con tu experiencia real. "
        "También puedes buscar respuestas demasiado amplias para evitar atender una dificultad concreta.\n\n"

        "Recuperas equilibrio cuando permites que tus ideales dialoguen con los hechos. "
        "Revisar tus creencias, aceptar la incertidumbre y aplicar lo que comprendes a la vida cotidiana ayuda a que la búsqueda de sentido no se convierta en evasión."
    ),

    "Capricornio": (
        "Neptuno en Capricornio necesita dar estructura a sus ideales y comprobar que aquello que imagina puede sostenerse en la realidad. "
        "Tu sensibilidad puede dirigirse hacia los sistemas, las responsabilidades y la construcción de proyectos con una finalidad más amplia.\n\n"

        "Cuando esta posición funciona de manera equilibrada, puedes convertir una visión en una estructura útil, introducir sensibilidad en entornos exigentes y construir proyectos que combinen propósito, organización y compromiso.\n\n"

        "La desregulación puede aparecer cuando idealizas el éxito, la autoridad o la estabilidad, o cuando sostienes responsabilidades que no reflejan tus verdaderas necesidades. "
        "También puedes intentar controlar mediante la planificación aquello que en realidad requiere escucha, flexibilidad o aceptación.\n\n"

        "Recuperas equilibrio cuando revisas si la estructura que mantienes sigue representando tus valores. "
        "Definir límites realistas, aceptar la vulnerabilidad y traducir tus ideales en pasos concretos permite que la visión no se pierda dentro de la exigencia."
    ),

    "Acuario": (
        "Neptuno en Acuario necesita imaginar nuevas formas de convivencia, participación y conexión colectiva. "
        "Tu sensibilidad puede orientarse hacia el futuro, los grupos y las posibilidades de construir una realidad más abierta e inclusiva.\n\n"

        "Cuando esta posición funciona de manera equilibrada, puedes percibir movimientos colectivos antes de que se hagan evidentes, inspirar nuevas formas de colaboración y aportar una visión capaz de conectar a personas muy diferentes.\n\n"

        "La desregulación puede aparecer cuando idealizas un grupo, una causa o una idea de futuro y pierdes de vista las necesidades concretas de quienes participan. "
        "También puedes refugiarte en lo colectivo para evitar la intimidad o sentir decepción cuando las personas reales no responden al ideal que imaginabas.\n\n"

        "Recuperas equilibrio cuando conectas la visión colectiva con acciones cercanas y relaciones concretas. "
        "Participar sin disolver tu individualidad y aceptar las imperfecciones humanas permite que el ideal se convierta en una contribución posible."
    ),

    "Piscis": (
        "Neptuno en Piscis necesita espacio para percibir, imaginar y conectar con dimensiones de la experiencia que no siempre pueden ordenarse racionalmente. "
        "La sensibilidad, la intuición y la capacidad de resonar con el entorno adquieren una presencia especialmente intensa.\n\n"

        "Cuando esta posición funciona de manera equilibrada, puedes desarrollar una profunda empatía, una gran riqueza imaginativa y una capacidad natural para acompañar procesos emocionales, creativos o espirituales.\n\n"

        "La desregulación puede aparecer cuando absorbes demasiado lo que ocurre a tu alrededor, evitas la realidad refugiándote en fantasías o te cuesta reconocer dónde terminan las necesidades ajenas y comienzan las tuyas. "
        "También puedes sentir que los estímulos, las emociones o las percepciones difíciles de organizar te sobrepasan.\n\n"

        "Recuperas equilibrio cuando construyes límites amables y mantienes apoyos concretos en la vida cotidiana. "
        "El descanso, el cuerpo, las rutinas sencillas y la expresión creativa ayudan a que tu sensibilidad pueda circular sin desbordarte."
    ),
}


NEPTUNO_CASA = {

    "Casa 1": (
        "Neptuno en la Casa 1 necesita que puedas expresar tu sensibilidad sin sentir que debes ocultarla o justificarla. Tu manera de presentarte al mundo suele estar impregnada de intuición, empatía y una percepción especialmente abierta hacia el entorno.\n\n"

        "Cuando esta posición funciona de manera equilibrada, transmites cercanía, inspiración y una presencia que facilita que otras personas se sientan comprendidas. Existe una capacidad natural para adaptarte sin perder la delicadeza con la que percibes la realidad.\n\n"

        "La desregulación puede aparecer cuando te identificas demasiado con las expectativas de los demás, te cuesta definir quién eres o adaptas continuamente tu forma de ser para responder al entorno.\n\n"

        "Recuperas equilibrio cuando desarrollas una identidad que también puede sostener límites. Conectar con tu cuerpo, reconocer tus necesidades y diferenciar lo que sientes de lo que absorbes permite que tu sensibilidad encuentre una base más estable."
    ),

    "Casa 2": (
        "Neptuno en la Casa 2 necesita que tus recursos y tus valores reflejen aquello que realmente da sentido a tu vida. La seguridad no suele construirse únicamente desde lo material, sino también desde la coherencia con tus ideales y tu mundo interior.\n\n"

        "Cuando esta posición funciona de manera equilibrada, puedes descubrir formas muy creativas de generar recursos y valorar aspectos de la vida que no siempre pueden medirse económicamente. Tu sensibilidad puede convertirse en un talento práctico cuando encuentra una dirección clara.\n\n"

        "La desregulación puede aparecer cuando idealizas la seguridad, descuidas la organización económica o te cuesta reconocer el valor real de tu trabajo y de tus capacidades.\n\n"

        "Recuperas equilibrio cuando unes inspiración y realidad. Organizar tus recursos, valorar objetivamente lo que aportas y construir estabilidad sin renunciar a tus valores fortalece esta posición."
    ),

    "Casa 3": (
        "Neptuno en la Casa 3 necesita expresar una forma de pensar intuitiva, imaginativa y abierta a múltiples significados. Tu percepción suele captar matices que otras personas pasan por alto.\n\n"

        "Cuando esta posición funciona de manera equilibrada, puedes comunicar ideas complejas con sensibilidad, utilizar la creatividad en el aprendizaje y comprender aquello que no siempre puede explicarse únicamente mediante la lógica.\n\n"

        "La desregulación puede aparecer cuando se mezclan intuición, interpretación y hechos, dificultando la claridad en la comunicación o generando confusión mental.\n\n"

        "Recuperas equilibrio cuando ordenas tus ideas, contrastas la información y das espacio tanto a la intuición como al pensamiento crítico."
    ),

    "Casa 4": (
        "Neptuno en la Casa 4 necesita construir un lugar donde la sensibilidad pueda descansar y sentirse protegida. El mundo emocional, la familia y las raíces ocupan un espacio profundo dentro de tu experiencia.\n\n"

        "Cuando esta posición funciona de manera equilibrada, puedes crear ambientes acogedores, comprender con delicadeza las dinámicas familiares y desarrollar una profunda conexión con tu mundo interior.\n\n"

        "La desregulación puede aparecer cuando idealizas el pasado, cargas con emociones familiares que no te pertenecen o buscas refugio en recuerdos y fantasías que dificultan el presente.\n\n"

        "Recuperas equilibrio cuando diferencias tu historia de la de tu familia y construyes un hogar emocional basado en tus propias necesidades actuales."
    ),

    "Casa 5": (
        "Neptuno en la Casa 5 necesita expresar la imaginación a través de la creatividad, el juego, el arte o cualquier actividad que permita dar forma a tu mundo interior.\n\n"

        "Cuando esta posición funciona de manera equilibrada, puedes inspirar a otras personas mediante tu capacidad creativa y disfrutar de una expresión espontánea, sensible y profundamente auténtica.\n\n"

        "La desregulación puede aparecer cuando idealizas el amor, depositas demasiadas expectativas en la creatividad o buscas reconocimiento a través de una imagen difícil de sostener.\n\n"

        "Recuperas equilibrio cuando disfrutas del proceso creativo sin exigir un resultado perfecto ni depender de la aprobación externa."
    ),

    "Casa 6": (
        "Neptuno en la Casa 6 necesita encontrar sentido en la vida cotidiana. Tu sensibilidad se expresa a través del trabajo, el cuidado y la manera en que organizas tus hábitos diarios.\n\n"

        "Cuando esta posición funciona de manera equilibrada, puedes desarrollar una forma de servicio profundamente humana, percibir necesidades poco visibles y aportar sensibilidad allí donde otras personas solo ven tareas.\n\n"

        "La desregulación puede aparecer cuando te sobrecargas intentando ayudar a todo el mundo, pierdes tus propios límites o el desorden cotidiano termina afectando a tu bienestar.\n\n"

        "Recuperas equilibrio cuando cuidas tus rutinas, respetas tus tiempos de descanso y recuerdas que servir no significa olvidarte de ti."
    ),

    "Casa 7": (
        "Neptuno en la Casa 7 necesita vivir relaciones donde exista una conexión profunda, sensible y auténtica. Los vínculos suelen convertirse en un espacio importante para desarrollar tu capacidad de empatía y comprensión.\n\n"

        "Cuando esta posición funciona de manera equilibrada, puedes construir relaciones basadas en la confianza, la escucha y una gran sensibilidad hacia la otra persona.\n\n"

        "La desregulación puede aparecer cuando idealizas a tu pareja, te cuesta ver las relaciones tal como son o sacrificas tus necesidades para mantener una imagen de unión o armonía.\n\n"

        "Recuperas equilibrio cuando reconoces tanto las cualidades como las limitaciones de cada vínculo y permites que la cercanía conviva con límites claros."
    ),

    "Casa 8": (
        "Neptuno en la Casa 8 necesita comprender los procesos profundos de transformación, pérdida y cambio desde una mirada sensible. Existe una gran capacidad para percibir aquello que permanece oculto bajo la superficie.\n\n"

        "Cuando esta posición funciona de manera equilibrada, puedes acompañar procesos difíciles con compasión, comprender emociones intensas y desarrollar una profunda confianza en los ciclos de transformación.\n\n"

        "La desregulación puede aparecer cuando se difuminan los límites emocionales, absorbes el dolor ajeno o te atrapas en miedos, dependencias o fantasías difíciles de contrastar.\n\n"

        "Recuperas equilibrio cuando respetas tus límites, compartes aquello que sientes y distingues entre lo que realmente te pertenece y lo que estás sosteniendo por otras personas."
    ),

    "Casa 9": (
        "Neptuno en la Casa 9 necesita ampliar la consciencia a través del conocimiento, la filosofía, los viajes o la búsqueda de significado. Existe una necesidad profunda de comprender la vida desde una perspectiva más amplia.\n\n"

        "Cuando esta posición funciona de manera equilibrada, puedes integrar intuición y aprendizaje, inspirar a otras personas y mantener una búsqueda honesta de sentido.\n\n"

        "La desregulación puede aparecer cuando idealizas una enseñanza, una tradición o una figura de autoridad, o cuando utilizas las grandes respuestas para evitar preguntas personales más concretas.\n\n"

        "Recuperas equilibrio cuando permites que tus creencias evolucionen junto con tu experiencia y mantienes un diálogo constante entre inspiración y realidad."
    ),

    "Casa 10": (
        "Neptuno en la Casa 10 necesita que tu vocación exprese algo que tenga sentido para ti. El reconocimiento pierde valor cuando no existe una verdadera conexión con aquello que haces.\n\n"

        "Cuando esta posición funciona de manera equilibrada, puedes desarrollar una profesión inspiradora, aportar sensibilidad en tu trabajo y orientar tu actividad hacia proyectos que beneficien también a otras personas.\n\n"

        "La desregulación puede aparecer cuando idealizas el éxito, dudas continuamente sobre tu dirección profesional o adaptas tu imagen pública a expectativas ajenas.\n\n"

        "Recuperas equilibrio cuando defines qué significa realmente el éxito para ti y construyes una trayectoria coherente con tus valores."
    ),

    "Casa 11": (
        "Neptuno en la Casa 11 necesita participar en proyectos colectivos que reflejen una visión compartida. Existe sensibilidad hacia los grupos, las causas comunes y la posibilidad de construir un futuro diferente.\n\n"

        "Cuando esta posición funciona de manera equilibrada, puedes inspirar a otras personas, favorecer la colaboración y participar en iniciativas que unen creatividad, empatía y compromiso.\n\n"

        "La desregulación puede aparecer cuando idealizas un grupo, una amistad o una causa, perdiendo de vista las limitaciones naturales de cualquier proyecto colectivo.\n\n"

        "Recuperas equilibrio cuando mantienes tu criterio personal dentro del grupo y recuerdas que las personas reales siempre serán más complejas que cualquier ideal."
    ),

    "Casa 12": (
        "Neptuno en la Casa 12 necesita espacios de silencio, recogimiento y conexión con el mundo interior. Tu sensibilidad suele orientarse hacia aquello que permanece fuera de la consciencia inmediata.\n\n"

        "Cuando esta posición funciona de manera equilibrada, puedes desarrollar una profunda capacidad de introspección, creatividad, compasión y comprensión de los procesos internos propios y ajenos.\n\n"

        "La desregulación puede aparecer cuando te aíslas en exceso, utilizas la fantasía para escapar de la realidad o absorbes emociones difíciles de distinguir como propias.\n\n"

        "Recuperas equilibrio cuando alternas los espacios de introspección con una vida cotidiana bien estructurada. El cuerpo, las rutinas y las relaciones conscientes ayudan a que tu mundo interior encuentre una expresión saludable."
    ),

}


NEPTUNO_COMBINACIONES = {

    "Sol": (
        "Tu identidad está profundamente vinculada a la sensibilidad, la imaginación y la necesidad de vivir de acuerdo con un ideal que dé sentido a lo que haces. "
        "No siempre te resulta fácil definirte mediante categorías cerradas, porque tu percepción de quién eres puede transformarse según las experiencias y los entornos que atraviesas.\n\n"

        "Cuando ambas funciones colaboran, desarrollas una gran capacidad para inspirar, crear y expresar dimensiones de la experiencia que no siempre pueden explicarse racionalmente. "
        "Tu identidad puede convertirse en un espacio flexible desde el que comprender diferentes realidades sin perder profundidad.\n\n"

        "Esta combinación te invita a distinguir entre adaptarte con sensibilidad y modificarte continuamente para responder a las expectativas ajenas. "
        "La empatía se vuelve más estable cuando también puedes reconocer tus deseos, tus límites y aquello que verdaderamente te representa."
    ),

    "Luna": (
        "Tu mundo emocional es especialmente receptivo a los ambientes, los vínculos y los estados internos de otras personas. "
        "Necesitas espacios donde poder sentir sin exigirte comprender o explicar inmediatamente todo lo que ocurre dentro de ti.\n\n"

        "Cuando ambas funciones colaboran, desarrollas una gran empatía, una imaginación profunda y una capacidad natural para acompañar emociones complejas. "
        "Puedes percibir necesidades que apenas han sido expresadas y ofrecer una presencia especialmente delicada.\n\n"

        "Esta combinación te invita a diferenciar entre tus emociones y aquello que absorbes del entorno. "
        "La sensibilidad no necesita convertirse en sobrecarga: descansar, retirarte cuando lo necesitas y establecer límites emocionales permite que puedas cuidar sin perderte."
    ),

    "Mercurio": (
        "Tu forma de pensar combina intuición, imaginación y una percepción muy sensible de los matices. "
        "No siempre llegas a una comprensión siguiendo un razonamiento lineal; a menudo captas primero una imagen, una impresión o una sensación que después necesitas ordenar.\n\n"

        "Cuando ambas funciones colaboran, puedes comunicar emociones complejas, desarrollar una gran riqueza simbólica y traducir lo intangible en palabras, imágenes o relatos que otras personas puedan comprender.\n\n"

        "Esta combinación te invita a distinguir entre percepción, interpretación y hecho. "
        "Contrastar la información, aclarar los mensajes y dar una estructura a tus ideas permite que la intuición se convierta en una fuente de comprensión y no de confusión."
    ),

    "Venus": (
        "Tu manera de vincularte está profundamente influida por la sensibilidad, la imaginación y la búsqueda de una conexión que trascienda lo cotidiano. "
        "Necesitas sentir que existe belleza, comprensión y una dimensión emocional significativa dentro de tus relaciones.\n\n"

        "Cuando ambas funciones colaboran, puedes amar con una gran delicadeza, percibir la belleza en formas poco evidentes y expresar el afecto a través del arte, la empatía o una presencia profundamente receptiva.\n\n"

        "Esta combinación te invita a observar cuándo estás relacionándote con la persona real y cuándo con la posibilidad que imaginas en ella. "
        "La conexión gana profundidad cuando puede incluir límites, diferencias y aspectos cotidianos que quizá no coincidan con el ideal."
    ),

    "Marte": (
        "Tu impulso de actuar está influido por la intuición, la sensibilidad y la necesidad de sentir que tus acciones responden a algo significativo. "
        "Puede resultarte difícil movilizarte cuando no encuentras una conexión emocional con aquello que haces.\n\n"

        "Cuando ambas funciones colaboran, puedes actuar con empatía, creatividad y una gran capacidad para responder a necesidades que otras personas no perciben. "
        "Tu energía encuentra fuerza cuando se dirige hacia una causa, una creación o una actividad que conecta con tus valores más profundos.\n\n"

        "Esta combinación te invita a reconocer cuándo estás siguiendo una intuición y cuándo evitas definir una dirección concreta. "
        "Dar pasos claros, establecer prioridades y expresar abiertamente lo que deseas ayuda a que la sensibilidad no diluya tu capacidad de acción."
    ),

    "Júpiter": (
        "La búsqueda de sentido de Júpiter se encuentra con la sensibilidad y la amplitud imaginativa de Neptuno. "
        "Existe una necesidad profunda de comprender la vida desde una perspectiva que incluya aquello que no puede reducirse únicamente a hechos o explicaciones racionales.\n\n"

        "Cuando ambas funciones colaboran, puedes desarrollar una gran confianza en la capacidad humana para aprender, crear y encontrar significado. "
        "Tu visión puede inspirar a otras personas y abrir posibilidades que amplían la manera de interpretar la experiencia.\n\n"

        "Esta combinación te invita a diferenciar entre una esperanza que te ayuda a avanzar y una expectativa que evita reconocer la realidad. "
        "Los ideales se vuelven más valiosos cuando pueden dialogar con los hechos, los límites y las consecuencias concretas de tus decisiones."
    ),

    "Saturno": (
        "Neptuno y Saturno representan dos necesidades que pueden parecer opuestas, pero que se necesitan mutuamente. "
        "Neptuno percibe posibilidades, imágenes e ideales; Saturno busca darles forma, establecer límites y construir una estructura capaz de sostenerlos.\n\n"

        "Cuando ambas funciones colaboran, puedes convertir una intuición en un proyecto, dar continuidad a una inspiración y construir espacios donde la sensibilidad tenga una expresión concreta. "
        "La imaginación encuentra un cauce sin perder su profundidad.\n\n"

        "Esta combinación te invita a evitar dos extremos: intentar controlar todo aquello que no puede definirse por completo o mantener tus ideales en un terreno tan abstracto que nunca puedan realizarse. "
        "La estructura no tiene que limitar la sensibilidad; puede ayudarla a tomar forma."
    ),

    "Urano": (
        "La capacidad de Urano para abrir nuevas posibilidades se encuentra con la sensibilidad y la imaginación de Neptuno. "
        "Una parte de ti cuestiona las formas conocidas; la otra intuye realidades que todavía no han encontrado una expresión clara.\n\n"

        "Cuando ambas funciones colaboran, puedes percibir cambios antes de que resulten evidentes, imaginar alternativas originales e inspirar nuevas maneras de comprender la vida individual y colectiva.\n\n"

        "Esta combinación te invita a distinguir entre una visión que abre posibilidades y una idea que todavía no dispone de suficiente contacto con la realidad. "
        "Dar tiempo, estructura y aplicación concreta a lo que percibes permite que la inspiración se convierta en una transformación posible."
    ),

    "Plutón": (
        "La sensibilidad de Neptuno se encuentra con la profundidad transformadora de Plutón. "
        "Existe una capacidad intensa para percibir emociones, dinámicas ocultas y procesos internos que no siempre pueden expresarse de forma inmediata.\n\n"

        "Cuando ambas funciones colaboran, puedes acompañar experiencias de pérdida, crisis o transformación con una gran comprensión de su dimensión emocional. "
        "También puedes convertir vivencias profundas en creatividad, empatía y una percepción más amplia de la condición humana.\n\n"

        "Esta combinación te invita a diferenciar entre empatizar con el dolor y dejar que te absorba. "
        "Reconocer tus límites, dar nombre a lo que percibes y buscar apoyos concretos permite que la profundidad transforme sin desbordarte."
    ),

    "Ascendente": (
        "Cuando Neptuno y el Ascendente interactúan, tu manera de presentarte al mundo transmite sensibilidad, receptividad y una cualidad difícil de definir con precisión. "
        "Las personas pueden percibir en ti aspectos diferentes según el vínculo, el momento o el entorno compartido.\n\n"

        "Esta combinación favorece una presencia empática, imaginativa y capaz de adaptarse con delicadeza a distintas situaciones. "
        "También puede aportar una gran sensibilidad hacia la imagen, el ambiente y la forma en que otras personas reciben tu presencia.\n\n"

        "La integración aparece cuando la capacidad de adaptarte no te obliga a diluir tu identidad. "
        "Reconocer tus necesidades, escuchar el cuerpo y establecer límites claros ayuda a que tu sensibilidad se exprese sin quedar definida por la mirada ajena."
    ),

    "Nodo Norte": (
        "Cuando Neptuno y el Nodo Norte se relacionan, aprender a confiar en tu sensibilidad forma parte importante de tu proceso de desarrollo. "
        "La vida puede invitarte a reconocer percepciones, emociones o dimensiones creativas que no siempre pueden comprenderse únicamente mediante la lógica.\n\n"

        "Esta combinación favorece experiencias que amplían tu empatía, tu imaginación y tu capacidad para aceptar la incertidumbre sin necesitar una respuesta inmediata para todo.\n\n"

        "El desarrollo aparece cuando la intuición se acompaña de discernimiento. "
        "No se trata de seguir cualquier impresión, sino de aprender a reconocer cuáles de ellas te acercan a una vida más coherente y cuáles pueden alejarte de la realidad."
    ),

    "Nodo Sur": (
        "Cuando Neptuno y el Nodo Sur interactúan, la sensibilidad, la imaginación y la capacidad para adaptarte pueden resultar recursos muy conocidos. "
        "Es posible que percibas con facilidad los estados ajenos o que hayas aprendido a responder al entorno antes de identificar tus propias necesidades.\n\n"

        "Esta combinación invita a conservar tu empatía sin recurrir automáticamente a la renuncia, la idealización o la tendencia a desaparecer dentro de una relación, una expectativa o una experiencia.\n\n"

        "La evolución consiste en utilizar la sensibilidad como un recurso consciente mientras desarrollas mayor claridad, dirección y capacidad para establecer límites."
    ),

    "Quirón": (
        "Cuando Neptuno y Quirón se relacionan, la sensibilidad puede estar vinculada a experiencias de desilusión, incomprensión o dificultad para sentir protección frente a lo que ocurre a tu alrededor.\n\n"

        "Con el tiempo, estas experiencias pueden ayudarte a comprender el dolor ajeno con una gran profundidad y a desarrollar formas delicadas de acompañar, crear o cuidar. "
        "Tu capacidad para reconocer aquello que no siempre se expresa puede convertirse en un recurso valioso.\n\n"

        "Esta combinación te invita a recordar que comprender el sufrimiento de otra persona no te obliga a repararlo ni a asumirlo como propio. "
        "La compasión necesita límites para no convertirse en sacrificio."
    ),

    "Lilith": (
        "Cuando Neptuno y Lilith interactúan, la sensibilidad se encuentra con aspectos de ti que quizá no encajan fácilmente en las expectativas externas. "
        "Puede existir una percepción intensa de deseos, emociones o realidades que otras personas prefieren mantener fuera de la conversación.\n\n"

        "Cuando ambas funciones colaboran, puedes dar expresión a experiencias silenciadas, cuestionar imágenes idealizadas y reconocer la complejidad que existe detrás de aquello que suele presentarse de manera más aceptable o armoniosa.\n\n"

        "Esta combinación te invita a distinguir entre escuchar una verdad profunda y dejar que las fantasías, los temores o las proyecciones difíciles de contrastar condicionen tu percepción. "

        "La sensibilidad gana fuerza cuando puede convivir con honestidad, discernimiento y límites claros."
    ),
}


NEPTUNO_TEXTOS_TIPO_ASPECTO = {

    "Conjunción": (
        "Neptuno se encuentra muy unido a esta parte de ti, de modo que la sensibilidad, la imaginación y la percepción intuitiva se expresan directamente a través de ella. "
        "Ambas funciones actúan de forma inseparable y pueden resultar difíciles de distinguir.\n\n"

        "Esta unión amplifica la receptividad y concede una presencia importante a todo lo relacionado con esta combinación. "
        "Puede aportar inspiración, empatía y una gran riqueza simbólica, aunque también favorecer la idealización, la confusión o la dificultad para reconocer con claridad qué pertenece a cada función.\n\n"

        "La integración aparece cuando das espacio a la sensibilidad sin renunciar al discernimiento. "
        "Reconocer qué estás percibiendo, qué estás imaginando y qué está ocurriendo realmente permite que la intuición se convierta en un recurso más consciente."
    ),

    "Sextil": (
        "Neptuno mantiene con esta parte de ti una relación que facilita la sensibilidad, la imaginación y la comprensión de matices poco evidentes. "
        "La posibilidad de colaboración está disponible, aunque necesita una expresión concreta para desplegarse plenamente.\n\n"

        "Cuando activas esta conexión de forma consciente, puedes integrar intuición y realidad, encontrar cauces creativos para lo que percibes y responder con empatía sin perder claridad.\n\n"

        "El aprendizaje consiste en no dejar esta facilidad únicamente como una posibilidad. "
        "Cuanto más la incorporas a decisiones, vínculos o procesos creativos concretos, más puede convertirse en un recurso estable."
    ),

    "Trígono": (
        "Neptuno y esta parte de ti tienden a colaborar de manera espontánea. "
        "Existe una facilidad natural para percibir, imaginar, empatizar y conectar con dimensiones de la experiencia que no siempre se expresan de forma directa.\n\n"

        "Esta fluidez puede favorecer una gran sensibilidad creativa y una comprensión intuitiva de personas y situaciones. "
        "También puede hacer que des por sentada una capacidad que forma parte importante de tus recursos.\n\n"

        "El equilibrio consiste en reconocer esta sensibilidad y darle una dirección consciente. "
        "La intuición gana profundidad cuando puede encontrar límites, lenguaje y una forma concreta de expresión."
    ),

    "Cuadratura": (
        "Neptuno y esta parte de ti no siempre encuentran con facilidad una forma común de funcionar. "
        "La sensibilidad, la imaginación o la necesidad de conexión pueden entrar en tensión con otras necesidades internas, generando confusión, idealización o dificultad para actuar con claridad.\n\n"

        "En algunos momentos puedes interpretar la realidad desde lo que esperas o deseas; en otros, la incertidumbre puede hacer que dudes de tus propias percepciones o evites tomar una posición definida.\n\n"

        "Esta fricción te impulsa a desarrollar un discernimiento más preciso. "
        "El aprendizaje consiste en escuchar lo que percibes sin convertir cada impresión en una certeza y en mantener contacto con los hechos sin negar tu sensibilidad."
    ),

    "Oposición": (
        "Neptuno y esta parte de ti buscan un equilibrio que no siempre resulta inmediato. "
        "Es posible que inicialmente reconozcas la sensibilidad, la idealización o la confusión a través de otras personas o de situaciones externas.\n\n"

        "También puedes alternar entre una gran apertura emocional y la necesidad de protegerte, o entre confiar plenamente en una percepción y dudar después de ella.\n\n"

        "El aprendizaje consiste en recuperar para ti aquello que primero identificas fuera. "
        "Cuando ambas funciones pueden dialogar, la sensibilidad deja de depender de lo que ocurre alrededor y encuentra una forma más consciente de relacionarse con la realidad."
    ),

    "Quincuncio": (
        "La relación entre Neptuno y esta parte de ti requiere ajustes frecuentes. "
        "La sensibilidad y la imaginación no siempre encajan fácilmente con la manera en que funciona la otra energía, y puede costarte identificar de dónde procede la incomodidad.\n\n"

        "Es posible que percibas más de lo que puedes ordenar en ese momento, o que una parte de ti necesite claridad mientras la otra todavía se mueve entre impresiones, emociones o posibilidades poco definidas.\n\n"

        "El aprendizaje se construye mediante pequeñas correcciones y una observación precisa de lo que sientes, interpretas y necesitas. "
        "Con el tiempo puedes desarrollar una forma muy personal de integrar intuición y realidad sin sacrificar ninguna de las dos."
    ),
}


NEPTUNO_INTEGRACION = {

    "necesidades": {
        "titulo": "Lo que Neptuno necesita",

        "texto": (
            "Cada Neptuno encuentra una forma diferente de expresar la sensibilidad, la imaginación y la capacidad de percibir aquello que no siempre resulta evidente, "
"pero existe una necesidad común: disponer de un espacio donde lo más profundo del mundo interior pueda encontrar una expresión auténtica.\n\n"

            "Neptuno necesita tiempo para escuchar, crear, imaginar y conectar con aquello que da profundidad a la experiencia. "
            "Necesita momentos de silencio, inspiración y contacto con aquello que despierta sensibilidad, belleza o compasión.\n\n"

            "No toda sensibilidad alimenta a Neptuno. Absorber continuamente lo que ocurre alrededor, vivir pendiente de las necesidades ajenas o permanecer en la fantasía tampoco permite que esta función encuentre equilibrio. "
            "Con frecuencia necesita aprender a distinguir entre lo que realmente percibe y aquello que proyecta, imagina o idealiza.\n\n"

            "Cuando respetas tu sensibilidad sin dejar que ocupe todo el espacio, Neptuno deja de buscar refugio en la evasión y recupera su capacidad para inspirar, comprender y conectar profundamente con la realidad."
        )
    },

    "cuidar": {
        "titulo": "Cómo cuidar tu Neptuno",

        "texto": (
            "Cuidar de Neptuno no significa alejarte del mundo ni buscar continuamente experiencias extraordinarias. "
            "Significa reservar espacios donde la sensibilidad pueda expresarse sin quedar anulada por el ruido, la prisa o las exigencias cotidianas.\n\n"

            "Neptuno se fortalece cuando disfrutas del arte, la música, la naturaleza, la creatividad, la contemplación o cualquier experiencia que permita a tu mundo interior encontrar una forma de expresión. "
            "También puede nutrirse mediante conversaciones profundas, momentos de silencio o actividades que despierten tu capacidad de empatía.\n\n"

            "Al mismo tiempo necesita realidad. La inspiración encuentra más fuerza cuando puede convivir con rutinas, límites y decisiones concretas que permitan sostenerla.\n\n"

            "Cuidar esta función implica escuchar lo que sientes sin asumir automáticamente que toda emoción, intuición o percepción describe la realidad tal como es. "
            "La sensibilidad se vuelve más estable cuando también puede apoyarse en la claridad."
        )
    },

    "equilibrio": {
        "titulo": "Cuando Neptuno encuentra equilibrio",

        "texto": (
            "Cuando Neptuno funciona de manera equilibrada, la sensibilidad deja de ser una fuente de confusión para convertirse en una forma profunda de comprender la vida.\n\n"

            "Existe empatía sin perder los propios límites, imaginación sin desconectarse de la realidad y capacidad para inspirarse sin necesidad de idealizar lo que ocurre.\n\n"

            "Puedes conectar con otras personas sin absorber completamente sus emociones, disfrutar de la creatividad sin exigirte perfección y aceptar la incertidumbre sin necesitar respuestas inmediatas para todo.\n\n"

            "No significa dejar de sentir intensamente. "
            "Significa que la sensibilidad encuentra una estructura suficientemente estable para expresarse sin desbordarte."
        )
    },

    "desregulacion": {
        "titulo": "Cuando Neptuno pierde equilibrio",

        "texto": (
            "Cuando Neptuno pierde equilibrio, la sensibilidad puede transformarse en confusión, idealización o dificultad para distinguir entre lo que realmente ocurre y aquello que imaginas, deseas o temes.\n\n"

            "Puede aparecer la tendencia a absorber emociones ajenas, refugiarte en fantasías, evitar decisiones difíciles o mantener expectativas que la realidad lleva tiempo mostrando como poco sostenibles.\n\n"

            "En otras ocasiones ocurre lo contrario: para protegerte de tanta sensibilidad puedes desconectarte de tus emociones, endurecerte o dejar de confiar en tu intuición.\n\n"

            "No significa que tu sensibilidad sea un problema. "
            "Con frecuencia indica que necesitas recuperar límites, descanso y claridad para que aquello que percibes pueda encontrar una forma más consciente de expresarse."
        )
    },

    "pregunta": {
        "titulo": "Una pregunta para observarte",

        "texto": (
            "Mientras leías este capítulo quizá has reconocido formas habituales de imaginar, conectar, inspirarte o percibir aquello que sucede bajo la superficie de las cosas. "
            "También es posible que algunas aparezcan únicamente en determinados momentos o ámbitos de tu vida.\n\n"

            "Más allá de la posición de Neptuno en tu carta, la pregunta importante es otra:\n\n"

            "¿Qué necesita hoy tu sensibilidad para expresarse sin perder contacto con la realidad?\n\n"

            "Puede tratarse de descanso, creatividad, silencio, una conversación sincera, una decisión pendiente o simplemente la posibilidad de reconocer lo que verdaderamente estás sintiendo.\n\n"

            "También puede ayudarte observar dónde estás confundiendo una esperanza, un miedo o una imagen ideal con lo que realmente está ocurriendo. "
            "Distinguir entre percepción e idealización es una forma de cuidar tu sensibilidad."
        )
    },

    "integracion": {
        "titulo": "Integración",

        "texto": (
            "Ser sensible no consiste únicamente en sentir más.\n\n"

            "También implica aprender a reconocer aquello que percibes, diferenciar lo que pertenece a tu mundo interior de lo que absorbes del entorno y encontrar una forma de expresar esa sensibilidad sin perder claridad.\n\n"

            "Conocer tu Neptuno no pretende decirte si eres más espiritual ni explicar todos los misterios de tu intuición. "
            "Pretende ayudarte a comprender cómo funciona tu capacidad para imaginar, empatizar e inspirarte, qué condiciones permiten que esa sensibilidad florezca y en qué momentos puede llevarte a idealizar, confundirte o perder tus propios límites.\n\n"

            "Cada vez que escuchas tu mundo interior sin dejar de sostenerte en la realidad, algo dentro de ti encuentra más profundidad.\n\n"

            "Porque la sensibilidad alcanza su mayor fuerza cuando puede convertirse en una forma consciente de habitar la vida."
        )
    }

}


# ─── TEXTOS: PLUTÓN ─────────────────────────────────────────────
PLUTON_SIGNO = {

    "Aries": (
        "Plutón en Aries necesita transformar profundamente la manera en que afirmas tu voluntad, utilizas tu fuerza y defiendes aquello que consideras importante. A lo largo de la vida pueden aparecer experiencias que cuestionen cómo ejerces tu poder personal y qué lugar ocupa la iniciativa dentro de tus decisiones.\n\n"

        "Cuando esta posición funciona de manera equilibrada, desarrollas una enorme capacidad para actuar con determinación, afrontar cambios difíciles y reconstruirte después de situaciones que exigen valentía. La fuerza deja de surgir como reacción y empieza a convertirse en una expresión consciente de quién eres.\n\n"

        "La desregulación puede aparecer cuando intentas controlar constantemente las situaciones, reaccionas desde la impulsividad o sientes que debes demostrar fortaleza incluso cuando necesitas ayuda. También puede ocurrir lo contrario: renunciar a tu capacidad de actuar por miedo a las consecuencias del conflicto.\n\n"

        "Recuperas equilibrio cuando comprendes que el verdadero poder no consiste en imponerte ni en resistir continuamente. Surge cuando puedes actuar desde la consciencia, sostener tus límites y utilizar tu fuerza para construir en lugar de defenderte constantemente."
    ),


    "Tauro": (
        "Plutón en Tauro necesita transformar la relación que mantienes con la seguridad, los recursos y aquello que te proporciona estabilidad. La vida puede invitarte a revisar repetidamente qué merece permanecer y qué necesita cambiar para que puedas seguir creciendo.\n\n"

        "Cuando esta posición funciona de manera equilibrada, desarrollas una gran capacidad para construir estabilidad incluso después de atravesar pérdidas o cambios importantes. Aprendes que la verdadera seguridad no depende únicamente de lo que posees, sino también de la confianza que desarrollas en tus propios recursos.\n\n"

        "La desregulación puede aparecer cuando te aferras a situaciones, bienes o relaciones que ya han agotado su función, o cuando intentas controlar el entorno para evitar cualquier sensación de incertidumbre. También puede surgir miedo a perder aquello que te sostiene.\n\n"

        "Recuperas equilibrio cuando descubres que transformar no significa perder. Soltar aquello que ya no puede acompañarte abre espacio para construir una estabilidad más profunda y auténtica."
    ),


    "Géminis": (
        "Plutón en Géminis necesita transformar la manera en que comprendes la realidad. Tus ideas, tu forma de comunicarte y tus creencias pueden atravesar cambios profundos que modifican por completo tu forma de interpretar la vida.\n\n"

        "Cuando esta posición funciona de manera equilibrada, desarrollas una mente especialmente penetrante, capaz de descubrir aquello que permanece oculto tras las palabras y comprender procesos complejos con gran profundidad. Existe una gran capacidad para investigar, analizar y comunicar transformaciones importantes.\n\n"

        "La desregulación puede aparecer cuando intentas controlar la información, desconfías constantemente de lo que escuchas o utilizas el conocimiento como una forma de protegerte. También puede resultar difícil abandonar ideas que durante mucho tiempo definieron tu forma de entender el mundo.\n\n"

        "Recuperas equilibrio cuando permites que tus propias ideas evolucionen. La transformación intelectual no consiste únicamente en aprender más, sino en atreverte a pensar de una manera diferente cuando la experiencia lo hace necesario."
    ),


    "Cáncer": (
        "Plutón en Cáncer necesita transformar profundamente la manera en que construyes seguridad emocional y perteneces a una familia, un hogar o una historia compartida. Muchas de las transformaciones más importantes de tu vida pueden estar vinculadas al mundo afectivo.\n\n"

        "Cuando esta posición funciona de manera equilibrada, desarrollas una enorme capacidad para sanar vínculos, comprender procesos emocionales complejos y construir una seguridad interna que ya no depende únicamente de las circunstancias externas.\n\n"

        "La desregulación puede aparecer cuando intentas protegerte controlando los vínculos, mantienes dinámicas familiares que ya no favorecen tu desarrollo o cargas con responsabilidades emocionales que no te corresponden.\n\n"

        "Recuperas equilibrio cuando aceptas que cuidar también implica permitir que algunas formas de relación evolucionen. Tu fortaleza crece cuando puedes sostener el cambio sin perder el contacto con tu mundo emocional."
    ),


    "Leo": (
        "Plutón en Leo necesita transformar la forma en que expresas tu individualidad, tu creatividad y el lugar que ocupas dentro de la vida. A lo largo del tiempo puedes revisar profundamente qué significa recibir reconocimiento y desde dónde deseas mostrar quién eres.\n\n"

        "Cuando esta posición funciona de manera equilibrada, desarrollas una presencia intensa, auténtica y capaz de inspirar a otras personas desde la coherencia y no desde la necesidad de aprobación. Tu creatividad adquiere una fuerza transformadora.\n\n"

        "La desregulación puede aparecer cuando el reconocimiento se convierte en una necesidad constante, intentas controlar la imagen que proyectas o sientes que mostrar vulnerabilidad pone en riesgo tu valor personal.\n\n"

        "Recuperas equilibrio cuando descubres que la verdadera fuerza nace de expresar quién eres, incluso cuando no existe garantía de reconocimiento. La autenticidad termina generando una influencia mucho más profunda que cualquier imagen construida."
    ),


    "Virgo": (
        "Plutón en Virgo necesita transformar profundamente la manera en que organizas tu vida, cuidas de ti y buscas mejorar aquello que haces. A lo largo del tiempo puedes descubrir que la verdadera transformación no consiste en alcanzar la perfección, sino en revisar constantemente aquello que ya no resulta útil.\n\n"

        "Cuando esta posición funciona de manera equilibrada, desarrollas una enorme capacidad para observar detalles, comprender procesos complejos y mejorar sistemas de forma paciente y profunda. Tu capacidad de análisis se convierte en una herramienta de transformación muy valiosa.\n\n"

        "La desregulación puede aparecer cuando intentas controlar cada detalle, te exiges más de lo que puedes sostener o sientes que nunca es suficiente. También puedes utilizar el trabajo o la mejora constante para evitar enfrentarte a procesos emocionales más profundos.\n\n"

        "Recuperas equilibrio cuando aceptas que transformar no significa controlar. Algunas partes de la vida necesitan atención y otras simplemente necesitan ser vividas. La verdadera eficacia aparece cuando el cuidado también incluye descanso y flexibilidad."
    ),

    "Libra": (
        "Plutón en Libra necesita transformar profundamente la forma en que construyes tus relaciones y compartes el poder con otras personas. Los vínculos importantes suelen convertirse en escenarios de aprendizaje donde descubres nuevas formas de cooperar, negociar y mantener tu individualidad.\n\n"

        "Cuando esta posición funciona de manera equilibrada, desarrollas relaciones especialmente honestas, profundas y capaces de evolucionar con el tiempo. Existe una gran capacidad para afrontar conflictos sin perder el respeto ni la voluntad de construir acuerdos más conscientes.\n\n"

        "La desregulación puede aparecer cuando intentas controlar la relación, evitas cualquier conflicto por miedo a perder el vínculo o depositas demasiado poder en la otra persona. También puede existir dificultad para abandonar relaciones que ya han agotado su función.\n\n"

        "Recuperas equilibrio cuando comprendes que una relación sana no elimina las diferencias. La verdadera transformación aparece cuando cada persona puede cambiar sin dejar de reconocer a la otra."
    ),

    "Escorpio": (
        "Plutón en Escorpio necesita atravesar procesos de transformación profunda. Existe una capacidad natural para mirar allí donde otras personas prefieren no detenerse y comprender que algunos cambios solo pueden producirse cuando se acepta atravesar aquello que resulta incómodo.\n\n"

        "Cuando esta posición funciona de manera equilibrada, desarrollas una enorme fortaleza para regenerarte después de las pérdidas, comprender procesos emocionales intensos y acompañar transformaciones propias y ajenas sin perder estabilidad. Tu profundidad se convierte en una fuente de claridad y no únicamente de intensidad.\n\n"

        "La desregulación puede aparecer cuando intentas controlar aquello que temes perder, desconfías constantemente o mantienes luchas de poder que consumen una gran cantidad de energía. También puede costarte cerrar etapas que emocionalmente siguen muy presentes.\n\n"

        "Recuperas equilibrio cuando descubres que el poder no consiste en controlar el cambio, sino en permitir que aquello que ya ha terminado encuentre un cierre consciente. Cada transformación bien integrada libera una enorme cantidad de energía para construir algo nuevo."
    ),

    "Sagitario": (
        "Plutón en Sagitario necesita transformar la manera en que comprendes el mundo, construyes tus creencias y das sentido a la experiencia. La vida puede llevarte a revisar profundamente aquello que durante mucho tiempo considerabas una verdad incuestionable.\n\n"

        "Cuando esta posición funciona de manera equilibrada, desarrollas una visión amplia, crítica y profundamente transformadora. Puedes cuestionar sistemas de pensamiento, abrir nuevas perspectivas y ayudar a otras personas a replantearse aquello que parecía inamovible.\n\n"

        "La desregulación puede aparecer cuando intentas imponer tus propias convicciones, rechazas cualquier visión diferente o buscas una verdad absoluta que elimine toda incertidumbre. También puedes sentir una necesidad constante de demostrar que tienes razón.\n\n"

        "Recuperas equilibrio cuando permites que tus creencias evolucionen junto con tu experiencia. La verdadera transformación no consiste en encontrar respuestas definitivas, sino en mantener la capacidad de seguir aprendiendo."
    ),

    "Capricornio": (
        "Plutón en Capricornio necesita transformar profundamente la relación que mantienes con la responsabilidad, la autoridad y el éxito. A lo largo de la vida puedes revisar repetidamente qué estructuras merecen mantenerse y cuáles necesitan evolucionar.\n\n"

        "Cuando esta posición funciona de manera equilibrada, desarrollas una enorme capacidad para liderar procesos complejos, asumir responsabilidades importantes y construir proyectos sólidos capaces de adaptarse a los cambios sin perder estabilidad.\n\n"

        "La desregulación puede aparecer cuando intentas controlar todos los resultados, sostienes cargas que ya no te corresponden o identificas tu valor únicamente con el rendimiento y los logros alcanzados.\n\n"

        "Recuperas equilibrio cuando descubres que la verdadera autoridad no nace del control, sino de la coherencia. Transformar una estructura también puede significar hacerla más humana, más flexible y más capaz de sostener la vida."
    ),

    "Acuario": (
        "Plutón en Acuario necesita transformar la manera en que participas en los grupos, comprendes el cambio colectivo y contribuyes al futuro. Existe una necesidad profunda de revisar sistemas, ideas y formas de organización que han dejado de responder a las necesidades actuales.\n\n"

        "Cuando esta posición funciona de manera equilibrada, desarrollas una gran capacidad para impulsar cambios colectivos, cuestionar modelos obsoletos y construir nuevas formas de colaboración que integran innovación y compromiso.\n\n"

        "La desregulación puede aparecer cuando rechazas cualquier estructura por el simple hecho de existir, te distancias emocionalmente de las personas o depositas todas tus expectativas en una idea de futuro que nunca termina de concretarse.\n\n"

        "Recuperas equilibrio cuando recuerdas que toda transformación colectiva comienza también por cambios personales. Las grandes ideas adquieren fuerza cuando encuentran una aplicación concreta en la realidad cotidiana."
    ),

    "Piscis": (
        "Plutón en Piscis necesita transformar profundamente la relación que mantienes con la sensibilidad, la compasión y el mundo interior. A lo largo de la vida puedes atravesar experiencias que te inviten a revisar la forma en que conectas con el dolor, la empatía y aquello que no siempre puede explicarse racionalmente.\n\n"

        "Cuando esta posición funciona de manera equilibrada, desarrollas una enorme capacidad para integrar experiencias difíciles, comprender el sufrimiento humano y convertir procesos muy profundos en creatividad, compasión y sabiduría. Tu sensibilidad deja de ser una carga para convertirse en una fuente de transformación.\n\n"

        "La desregulación puede aparecer cuando absorbes demasiado el dolor ajeno, te refugias en la evasión para evitar lo que resulta difícil o sientes que debes salvar continuamente a otras personas. También puede costarte reconocer dónde terminan las necesidades ajenas y comienzan las tuyas.\n\n"

        "Recuperas equilibrio cuando comprendes que acompañar no significa cargar con todo. La compasión encuentra su mayor fuerza cuando puede sostenerse sobre límites claros y una profunda conexión contigo."
    ),

}



PLUTON_CASA = {

    "Casa 1": (
        "Plutón en la Casa 1 necesita transformar profundamente la manera en que construyes tu identidad y ocupas tu lugar en el mundo. La vida puede llevarte a revisar repetidamente quién eres, cómo utilizas tu fuerza y qué parte de tu personalidad necesita dejar atrás viejas formas de funcionar.\n\n"

        "Cuando esta posición funciona de manera equilibrada, desarrollas una gran capacidad para reinventarte sin perder autenticidad. Las experiencias difíciles fortalecen tu identidad en lugar de debilitarla, y aprendes a ejercer tu influencia desde la coherencia más que desde el control.\n\n"

        "La desregulación puede aparecer cuando intentas controlar constantemente la imagen que proyectas, reaccionas desde la necesidad de protegerte o sientes que debes mantener una versión de ti que ya ha dejado de representarte.\n\n"

        "Recuperas equilibrio cuando aceptas que tu identidad también puede evolucionar. Cada transformación bien integrada te acerca más a quien realmente eres."
    ),

    "Casa 2": (
        "Plutón en la Casa 2 necesita transformar la relación que mantienes con la seguridad, los recursos y el valor que reconoces en ti. La vida puede invitarte a revisar qué sostiene realmente tu estabilidad y qué necesita cambiar para que deje de depender únicamente de factores externos.\n\n"

        "Cuando esta posición funciona de manera equilibrada, desarrollas una gran capacidad para reconstruirte después de pérdidas, reorganizar tus recursos y descubrir fortalezas que permanecían ocultas. La seguridad deja de apoyarse exclusivamente en lo que posees.\n\n"

        "La desregulación puede aparecer cuando el miedo a perder conduce al control, al apego o a la dificultad para cerrar etapas económicas o materiales.\n\n"

        "Recuperas equilibrio cuando descubres que tu mayor recurso no siempre está fuera, sino en la capacidad de reconstruir aquello que parecía haberse perdido."
    ),

    "Casa 3": (
        "Plutón en la Casa 3 necesita transformar la forma en que piensas, aprendes y comunicas. Tus ideas pueden atravesar cambios profundos que modifican por completo la manera en que interpretas la realidad.\n\n"

        "Cuando esta posición funciona de manera equilibrada, desarrollas una mente especialmente penetrante, capaz de comprender procesos complejos, investigar con profundidad y comunicar aquello que otras personas apenas alcanzan a percibir.\n\n"

        "La desregulación puede aparecer cuando utilizas el conocimiento para controlar, dudas constantemente de las intenciones ajenas o te aferras a formas de pensar que ya no responden a tu experiencia.\n\n"

        "Recuperas equilibrio cuando permites que tus ideas evolucionen junto contigo. Comprender también significa dejar espacio para cambiar de perspectiva."
    ),

    "Casa 4": (
        "Plutón en la Casa 4 necesita transformar profundamente la relación con el hogar, la familia y las raíces emocionales. Algunas de las transformaciones más importantes de tu vida pueden surgir precisamente de ese mundo íntimo.\n\n"

        "Cuando esta posición funciona de manera equilibrada, desarrollas una gran capacidad para sanar dinámicas familiares, construir una seguridad emocional más consciente y crear un hogar que refleje quién eres hoy y no únicamente de dónde vienes.\n\n"

        "La desregulación puede aparecer cuando continúas sosteniendo historias familiares que ya han terminado, intentas controlar los vínculos afectivos o cargas con responsabilidades emocionales que no te corresponden.\n\n"

        "Recuperas equilibrio cuando aceptas que honrar tus raíces no significa repetirlas. Transformar también puede ser una forma de cuidar."
    ),

    "Casa 5": (
        "Plutón en la Casa 5 necesita transformar la forma en que expresas tu creatividad, disfrutas de la vida y compartes aquello que nace de ti. La creación puede convertirse en un proceso profundamente transformador.\n\n"

        "Cuando esta posición funciona de manera equilibrada, desarrollas una creatividad intensa, auténtica y capaz de provocar cambios tanto en ti como en quienes reciben aquello que expresas. Tu capacidad creadora adquiere una gran profundidad.\n\n"

        "La desregulación puede aparecer cuando el reconocimiento se convierte en una necesidad constante, intentas controlar el resultado de todo lo que haces o depositas demasiado de tu valor personal en tus creaciones.\n\n"

        "Recuperas equilibrio cuando disfrutas del acto de crear sin exigir que cada expresión confirme quién eres. La creatividad transforma precisamente porque nace de un lugar verdadero."
    ),

    "Casa 6": (
        "Plutón en la Casa 6 necesita transformar la manera en que trabajas, cuidas de ti y organizas tu vida cotidiana. Los pequeños hábitos pueden convertirse en el escenario de cambios muy profundos.\n\n"

        "Cuando esta posición funciona de manera equilibrada, desarrollas una enorme capacidad para mejorar procesos, reconstruir rutinas y encontrar nuevas formas de cuidar tu salud y tu energía con mayor consciencia.\n\n"

        "La desregulación puede aparecer cuando intentas controlar todos los detalles, te exiges más de lo que puedes sostener o utilizas el trabajo como una forma de evitar otros procesos internos.\n\n"

        "Recuperas equilibrio cuando comprendes que transformar la vida cotidiana no consiste en hacerlo todo mejor, sino en construir hábitos que también puedan sostenerte."
    ),

    "Casa 7": (
        "Plutón en la Casa 7 necesita transformar profundamente la manera en que construyes relaciones. Los vínculos importantes suelen convertirse en escenarios donde aprendes sobre confianza, poder, intimidad y cooperación.\n\n"

        "Cuando esta posición funciona de manera equilibrada, puedes desarrollar relaciones muy profundas, honestas y capaces de evolucionar con el tiempo. Existe una gran capacidad para atravesar conflictos sin renunciar al vínculo cuando las dos personas desean seguir construyéndolo.\n\n"

        "La desregulación puede aparecer cuando aparecen luchas de poder, dependencia, necesidad de controlar la relación o dificultad para aceptar que algunas personas ya han cumplido su función en tu vida.\n\n"

        "Recuperas equilibrio cuando comprendes que amar no significa controlar. Las relaciones más profundas son aquellas donde cada persona puede transformarse sin dejar de respetar a la otra."
    ),

    "Casa 8": (
        "Plutón en la Casa 8 necesita atravesar procesos profundos de transformación emocional. Existe una capacidad natural para comprender los finales, los cambios y todo aquello que exige dejar atrás una etapa para construir otra diferente.\n\n"

        "Cuando esta posición funciona de manera equilibrada, desarrollas una enorme fortaleza para regenerarte, integrar pérdidas y acompañar procesos complejos sin perder estabilidad. Tu profundidad se convierte en una fuente de crecimiento para ti y para quienes te rodean.\n\n"

        "La desregulación puede aparecer cuando el miedo a perder conduce al control, la desconfianza o la dificultad para cerrar procesos que ya han terminado.\n\n"

        "Recuperas equilibrio cuando permites que aquello que ha cumplido su función encuentre un cierre consciente. Cada final bien integrado libera espacio para una nueva etapa."
    ),

    "Casa 9": (
        "Plutón en la Casa 9 necesita transformar profundamente tus creencias, tu filosofía de vida y la manera en que construyes significado. Algunas experiencias pueden cambiar por completo tu forma de comprender el mundo.\n\n"

        "Cuando esta posición funciona de manera equilibrada, desarrollas una visión profunda, crítica y abierta al cambio. Puedes revisar tus propias convicciones sin perder la capacidad de encontrar sentido en la experiencia.\n\n"

        "La desregulación puede aparecer cuando defiendes una única verdad, rechazas cualquier perspectiva diferente o buscas respuestas absolutas para eliminar toda incertidumbre.\n\n"

        "Recuperas equilibrio cuando permites que tus creencias evolucionen junto con tu vida. La transformación también consiste en ampliar la mirada."
    ),

    "Casa 10": (
        "Plutón en la Casa 10 necesita transformar la relación con la vocación, la autoridad y el lugar que ocupas dentro de la sociedad. La trayectoria profesional puede convertirse en uno de los principales escenarios de evolución.\n\n"

        "Cuando esta posición funciona de manera equilibrada, desarrollas una gran capacidad para liderar cambios, reconstruir proyectos y asumir responsabilidades desde una autoridad basada en la coherencia.\n\n"

        "La desregulación puede aparecer cuando identificas tu valor únicamente con el éxito, intentas controlar constantemente los resultados o sostienes estructuras profesionales que hace tiempo dejaron de representar quién eres.\n\n"

        "Recuperas equilibrio cuando recuerdas que el verdadero reconocimiento nace de la coherencia entre lo que haces y quien eres."
    ),

    "Casa 11": (
        "Plutón en la Casa 11 necesita transformar la manera en que participas en grupos, amistades y proyectos colectivos. Algunas de las transformaciones más importantes de tu vida pueden surgir precisamente a través de las personas con las que compartes una visión de futuro.\n\n"

        "Cuando esta posición funciona de manera equilibrada, puedes impulsar cambios colectivos muy profundos, participar en procesos de renovación social y construir vínculos basados en la autenticidad y el compromiso compartido.\n\n"

        "La desregulación puede aparecer cuando aparecen luchas de poder dentro de los grupos, desconfianza hacia las personas o dificultad para abandonar proyectos que ya han cumplido su función.\n\n"

        "Recuperas equilibrio cuando aceptas que también las comunidades evolucionan. Permanecer no siempre significa crecer, y marcharte no siempre significa perder."
    ),

    "Casa 12": (
        "Plutón en la Casa 12 necesita transformar profundamente el mundo interior. Existe una capacidad especial para reconocer procesos inconscientes, integrar experiencias difíciles y comprender aspectos de ti que durante mucho tiempo permanecieron ocultos.\n\n"

        "Cuando esta posición funciona de manera equilibrada, desarrollas una enorme fortaleza interior, una gran capacidad de introspección y la posibilidad de transformar viejos patrones antes de que condicionen nuevamente tu vida.\n\n"

        "La desregulación puede aparecer cuando te enganchas a culpas, miedos o experiencias pasadas que continúan actuando desde la sombra, o cuando evitas mirar aquello que necesita ser reconocido.\n\n"

        "Recuperas equilibrio cuando aceptas que conocerte también implica acercarte con honestidad a aquello que durante mucho tiempo preferiste no mirar. La verdadera transformación comienza cuando la consciencia alcanza esos espacios."
    ),

}


PLUTON_COMBINACIONES = {

    "Sol": (
        "La relación entre Plutón y el Sol habla de la transformación de tu identidad y de la forma en que desarrollas tu voluntad. "
        "A lo largo de la vida puedes atravesar experiencias que te lleven a revisar profundamente quién eres, qué lugar ocupas y desde dónde ejerces tu capacidad de decidir.\n\n"

        "Cuando esta combinación encuentra equilibrio, desarrollas una identidad sólida, auténtica y capaz de evolucionar sin perder coherencia. "
        "La confianza deja de depender del control y nace de una comprensión más profunda de ti."
    ),

    "Luna": (
        "La relación entre Plutón y la Luna habla de la transformación del mundo emocional. "
        "Las experiencias afectivas suelen convertirse en oportunidades para revisar antiguos patrones, sanar heridas y construir una forma más consciente de vivir tus emociones.\n\n"

        "Cuando esta combinación funciona de manera equilibrada, desarrollas una enorme capacidad para integrar emociones intensas sin engancharte a ellas. "
        "La profundidad emocional se convierte en una fuente de fortaleza y no únicamente de intensidad."
    ),

    "Mercurio": (
        "La relación entre Plutón y Mercurio habla de la transformación de tu manera de pensar, comprender y comunicar. "
        "Existe una tendencia natural a cuestionar aquello que parece evidente y a buscar explicaciones cada vez más profundas.\n\n"

        "Cuando esta combinación encuentra equilibrio, desarrollas una mente especialmente penetrante, capaz de investigar, comprender procesos complejos y comunicar cambios importantes con claridad y profundidad."
    ),

    "Venus": (
        "La relación entre Plutón y Venus habla de la transformación de tus vínculos, de tus valores y de la manera en que experimentas el afecto. "
        "Las relaciones importantes suelen impulsarte a revisar qué significa realmente amar, confiar y compartir.\n\n"

        "Cuando esta combinación funciona de manera equilibrada, desarrollas vínculos más conscientes, donde la profundidad puede convivir con el respeto, la libertad y el crecimiento mutuo."
    ),

    "Marte": (
        "La relación entre Plutón y Marte habla de la transformación de la fuerza, la iniciativa y la forma en que actúas para conseguir aquello que deseas. "
        "La vida puede enseñarte a utilizar tu energía con mayor consciencia y menos necesidad de imponer o resistir.\n\n"

        "Cuando esta combinación encuentra equilibrio, desarrollas una enorme capacidad para sostener procesos difíciles, actuar con determinación y utilizar tu fuerza para construir cambios duraderos."
    ),

    "Júpiter": (
        "La relación entre Plutón y Júpiter habla de la transformación de tus creencias, de tu visión del mundo y de aquello que da sentido a tu crecimiento. "
        "Es posible que algunas de tus convicciones más importantes evolucionen profundamente a lo largo de la vida.\n\n"

        "Cuando esta combinación funciona de manera equilibrada, desarrollas una visión amplia, crítica y profundamente transformadora, capaz de integrar nuevas perspectivas sin perder coherencia."
    ),

    "Saturno": (
        "La relación entre Plutón y Saturno habla de la transformación de las estructuras sobre las que construyes tu vida. "
        "Responsabilidades, límites y formas de organización pueden necesitar revisarse para responder a una etapa diferente de tu desarrollo.\n\n"

        "Cuando esta combinación encuentra equilibrio, desarrollas una gran capacidad para reconstruir estructuras sólidas, flexibles y preparadas para sostener cambios importantes."
    ),

    "Urano": (
        "La relación entre Plutón y Urano habla de la transformación del cambio. "
        "Existe una capacidad especial para impulsar renovaciones profundas, cuestionar aquello que ha dejado de funcionar y abrir espacio a nuevas posibilidades.\n\n"

        "Cuando esta combinación funciona de manera equilibrada, la innovación deja de ser una ruptura impulsiva para convertirse en una evolución consciente y profundamente transformadora."
    ),

    "Neptuno": (
        "La relación entre Plutón y Neptuno habla de la transformación de la sensibilidad, la imaginación y el mundo interior. "
        "La vida puede invitarte a revisar antiguas idealizaciones para construir una conexión más consciente contigo y con la realidad.\n\n"

        "Cuando esta combinación encuentra equilibrio, desarrollas una sensibilidad profunda capaz de inspirar, comprender y acompañar procesos complejos sin perder claridad."
    ),

    "Ascendente": (
        "La relación entre Plutón y el Ascendente habla de la transformación de la manera en que te muestras al mundo. "
        "Tu forma de iniciar experiencias y de construir tu identidad visible puede cambiar profundamente a lo largo de la vida.\n\n"

        "Cuando esta combinación funciona de manera equilibrada, proyectas una presencia auténtica, coherente y capaz de inspirar confianza precisamente porque refleja procesos internos ya integrados."
    ),

    "Nodo Norte": (
        "La relación entre Plutón y el Nodo Norte habla de transformaciones que favorecen tu desarrollo. "
        "Algunas de las experiencias que impulsan tu crecimiento pueden exigir dejar atrás antiguas formas de funcionar para construir otras más coherentes con quien estás llegando a ser.\n\n"

        "Cuando esta combinación encuentra equilibrio, cada cambio importante se convierte en una oportunidad para avanzar con mayor autenticidad hacia tu propio camino."
    ),

    "Nodo Sur": (
        "La relación entre Plutón y el Nodo Sur habla de la transformación de patrones profundamente arraigados. "
        "La vida puede invitarte repetidamente a revisar hábitos, mecanismos de protección o formas de actuar que fueron útiles en otro momento, pero que ya no favorecen tu desarrollo.\n\n"

        "Cuando esta combinación funciona de manera equilibrada, puedes conservar la experiencia adquirida sin que el pasado limite tu desarrollo, permitiendo que nuevas formas de vivir ocupen su lugar."
    ),

    "Quirón": (
        "La relación entre Plutón y Quirón habla de la transformación de aquellas heridas que han marcado profundamente tu historia. "
        "El proceso no consiste en borrar el dolor, sino en integrarlo de una manera que deje de dirigir tu vida desde la sombra.\n\n"

        "Cuando esta combinación encuentra equilibrio, desarrollas una gran capacidad para convertir experiencias difíciles en comprensión, fortaleza y acompañamiento para otras personas."
    ),

    "Lilith": (
        "La relación entre Plutón y Lilith habla de la transformación de aquellas partes de ti que durante mucho tiempo pudieron permanecer ocultas, rechazadas o difíciles de expresar. "
        "Existe una invitación constante a reconocer esos aspectos sin necesidad de combatirlos ni negarlos.\n\n"

        "Cuando esta combinación funciona de manera equilibrada, recuperas una parte importante de tu poder personal al integrar aspectos de tu identidad que antes permanecían separados de la imagen que tenías de ti."
    )

}


PLUTON_TEXTOS_TIPO_ASPECTO = {

    "Conjunción": (
        "La conjunción concentra la energía de ambos símbolos y hace que sus procesos de transformación se vivan de manera especialmente intensa. "
        "Existe una sensación de que ambas funciones evolucionan juntas y de que los cambios que afectan a una repercuten inmediatamente sobre la otra.\n\n"

        "Cuando esta energía encuentra equilibrio, puede convertirse en una enorme capacidad para renovarte profundamente, integrar experiencias difíciles y construir formas de funcionamiento mucho más conscientes. "
        "El reto consiste en permitir que la transformación ocurra sin intentar controlar constantemente el proceso."
    ),

    "Sextil": (
        "El sextil crea oportunidades naturales para transformar esta parte de tu vida de una manera gradual y consciente. "
        "Las circunstancias suelen ofrecer recursos, personas o experiencias que facilitan el cambio sin necesidad de grandes rupturas.\n\n"

        "Cuando aprovechas esta energía, la transformación se integra de forma estable y puede convertirse en una fuente de crecimiento profundo que se desarrolla paso a paso."
    ),

    "Trígono": (
        "El trígono permite que la capacidad de transformación fluya con relativa naturalidad. "
        "Existe facilidad para comprender cuándo una etapa ha terminado y para construir otra nueva sin engancharte excesivamente al pasado.\n\n"

        "Aunque esta energía suele resultar fluida, también conviene recordar que incluso los procesos más naturales necesitan participación consciente para desarrollar todo su potencial."
    ),

    "Cuadratura": (
        "La cuadratura genera una tensión que impulsa cambios importantes. "
        "Con frecuencia aparecen situaciones que cuestionan antiguos patrones y obligan a revisar formas de actuar que durante mucho tiempo parecían funcionar.\n\n"

        "Aunque estos procesos puedan resultar exigentes, también suelen convertirse en algunos de los mayores motores de crecimiento. "
        "Cada dificultad ofrece la posibilidad de construir una forma más consciente y sólida de relacionarte con esta parte de tu vida."
    ),

    "Oposición": (
        "La oposición invita a encontrar equilibrio entre dos fuerzas que inicialmente parecen avanzar en direcciones diferentes. "
        "Las transformaciones suelen producirse a través de relaciones, acontecimientos o experiencias que muestran perspectivas distintas a las propias.\n\n"

        "Cuando esta energía se integra, deja de vivirse como un conflicto permanente y comienza a convertirse en una oportunidad para ampliar la mirada y construir soluciones más completas."
    ),

    "Quincuncio": (
        "El quincuncio suele señalar ajustes profundos que no siempre resultan evidentes al principio. "
        "Existe la sensación de que ambas funciones necesitan aprender a adaptarse mutuamente hasta encontrar una forma más coherente de trabajar juntas.\n\n"

        "La transformación aparece poco a poco, a medida que realizas pequeños cambios sostenidos en el tiempo. "
        "La flexibilidad y la disposición para revisar antiguos hábitos suelen ser las herramientas que permiten integrar mejor esta energía."
    )

}


PLUTON_INTEGRACION = {

    "necesidades": {
        "titulo": "Lo que Plutón necesita",

        "texto": (
            "Cada Plutón transforma un ámbito diferente de la vida, pero existe una necesidad común: permitir que aquello que ya ha cumplido su función pueda evolucionar.\n\n"

            "Plutón necesita profundidad. Necesita tiempo para comprender los procesos, revisar antiguos patrones y reconocer aquellas formas de actuar que durante mucho tiempo ofrecieron seguridad, pero que hoy limitan tu crecimiento.\n\n"

            "No busca el cambio por el cambio. Tampoco pretende destruir aquello que funciona. Su movimiento aparece cuando una estructura ya no puede sostener la vida que estás construyendo.\n\n"

            "Cuando respetas ese proceso, la transformación deja de sentirse como una pérdida y comienza a convertirse en una forma de recuperar energía, claridad y poder personal."
        )
    },

    "cuidar": {
        "titulo": "Cómo cuidar tu Plutón",

        "texto": (
            "Cuidar de Plutón no consiste en buscar continuamente grandes cambios. Significa desarrollar la capacidad de observar con honestidad qué partes de tu vida siguen creciendo contigo y cuáles permanecen únicamente por costumbre, miedo o necesidad de control.\n\n"

            "Plutón se fortalece cuando aceptas revisar tus propias reacciones, cuestionar patrones repetitivos y permitir que algunas etapas encuentren un cierre consciente. También necesita espacios donde puedas elaborar emocionalmente aquello que estás viviendo, sin precipitar las respuestas ni evitar lo que resulta incómodo.\n\n"

            "La transformación necesita tiempo. No siempre ocurre de forma visible, pero suele comenzar mucho antes de que aparezcan los cambios externos.\n\n"

            "Cuidar esta función implica confiar en que soltar una forma antigua de vivir no significa perderte, sino dejar espacio para construir otra más coherente contigo."
        )
    },

    "equilibrio": {
        "titulo": "Cuando Plutón encuentra equilibrio",

        "texto": (
            "Cuando Plutón funciona de manera equilibrada, desarrollas una gran capacidad para atravesar cambios importantes sin perder el contacto contigo. Comprendes que toda transformación implica un periodo de adaptación y no necesitas controlar cada paso del proceso.\n\n"

            "Existe fortaleza para cerrar etapas cuando han terminado, revisar aquello que necesita evolucionar y reconstruir tu vida desde una comprensión más profunda de quién eres.\n\n"

            "La intensidad deja de convertirse en una lucha constante y pasa a ser una fuente de claridad. Puedes mirar aquello que resulta difícil sin engancharte a ello.\n\n"

            "La transformación deja entonces de sentirse como una amenaza y empieza a convertirse en una herramienta de crecimiento consciente."
        )
    },

    "desregulacion": {
        "titulo": "Cuando Plutón pierde equilibrio",

        "texto": (
            "Cuando Plutón pierde equilibrio, puede aparecer la necesidad de controlar aquello que temes perder, resistirte a cambios que hace tiempo comenzaron o mantener luchas que ya no contribuyen a tu bienestar.\n\n"

            "En ocasiones puedes aferrarte a una versión de ti, de una relación o de un proyecto que ya ha agotado su función. Otras veces ocurre lo contrario: impulsar cambios constantes sin darte tiempo para integrar lo vivido.\n\n"

            "También puede resultar difícil confiar en los procesos, aceptar los finales o reconocer que algunas transformaciones no pueden acelerarse.\n\n"

            "No significa que estés haciendo algo mal. Con frecuencia indica que una parte de tu vida necesita ser revisada con mayor honestidad para que pueda evolucionar sin depender únicamente del esfuerzo o del control."
        )
    },

    "pregunta": {
        "titulo": "Una pregunta para observarte",

        "texto": (
            "Mientras leías este capítulo quizá has reconocido cambios importantes que ya forman parte de tu historia y otros que todavía continúan desarrollándose.\n\n"

            "Más allá de la posición de Plutón en tu carta, la pregunta importante es otra:\n\n"

            "¿Qué parte de tu vida sigue pidiendo una transformación que llevas tiempo posponiendo?\n\n"

            "Puede tratarse de una forma de relacionarte, de trabajar, de protegerte, de pensar o incluso de mirarte.\n\n"

            "No siempre es necesario hacer cambios inmediatos. A veces el primer paso consiste simplemente en reconocer con honestidad aquello que ya no puede seguir sosteniéndose de la misma manera."
        )
    },

    "integracion": {
        "titulo": "Integración",

        "texto": (
            "Transformarse no significa convertirse en alguien diferente.\n\n"

            "Con frecuencia significa dejar de sostener formas de vivir, pensar o relacionarte que fueron necesarias en otro momento, pero que hoy ya no reflejan quién eres.\n\n"

            "Conocer tu Plutón no pretende anunciar crisis inevitables ni convertir cada cambio en un acontecimiento extraordinario. Pretende ayudarte a comprender dónde la vida te invita a evolucionar con mayor profundidad, qué patrones necesitan revisarse y qué recursos pueden ayudarte a construir una versión más consciente de ti.\n\n"

            "Cada transformación bien integrada libera una parte de tu energía para ponerla al servicio de la vida que realmente deseas construir.\n\n"

            "Porque el verdadero poder no nace de controlar el cambio, sino de permitir que aquello que ya no eres pueda dar paso, conscientemente, a aquello en lo que te estás convirtiendo."
        )
    }

}


# ─── CÁLCULO ASTROLÓGICO ──────────────────────────────────────────────────────

def geocodificar(ciudad):
    g = Nominatim(
        user_agent="ai_planetas_transpersonales",
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


def signo_interceptado(signo, cuspides):
    signos_cuspides = signos_en_cuspides(cuspides)
    return signo not in signos_cuspides


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


def grados_a_signo_lon(lon):
    """Devuelve el signo y el grado dentro del signo."""
    return grados_a_signo(lon)


def signo_cuspide_casa(cuspides, num_casa):
    lon = cuspides[num_casa - 1]
    signo, _ = grados_a_signo(lon)
    return signo


def es_anaretico(grado):
    return grado >= 29


# ─── CÁLCULO GENÉRICO DE ASPECTOS POR MÓDULO ────────────────────────────────

def calcular_aspectos_modulo(planetas, asc, planetas_focales):
    """
    Calcula los aspectos de uno o varios planetas focales con el resto
    de los cuerpos y puntos relevantes de la carta.

    Incluye aspectos con todos los elementos disponibles en `planetas`:

    - Sol
    - Luna
    - Mercurio
    - Venus
    - Marte
    - Júpiter
    - Saturno
    - Urano
    - Neptuno
    - Plutón
    - Nodo Norte
    - Nodo Sur
    - Quirón
    - Lilith

    También incluye los aspectos con el Ascendente.

    Cada combinación se calcula una sola vez,
    independientemente del orden de los cuerpos.
    """

    aspectos = []
    pares = []
    pares_vistos = set()

    # Todos los cuerpos disponibles que tengan longitud válida.
    cuerpos = {
        nombre: objeto
        for nombre, objeto in planetas.items()
        if objeto and objeto.get("lon") is not None
    }

    def agregar_par(nombre1, lon1, nombre2, lon2):
        """
        Añade una combinación una sola vez,
        independientemente del orden de sus cuerpos.
        """

        if nombre1 == nombre2:
            return

        if lon1 is None or lon2 is None:
            return

        clave = tuple(sorted((nombre1, nombre2)))

        if clave in pares_vistos:
            return

        pares_vistos.add(clave)

        pares.append({
            "p1": nombre1,
            "p2": nombre2,
            "lon1": lon1,
            "lon2": lon2,
        })

    # Cada planeta focal se compara con todos los cuerpos disponibles.
    for nombre_focal in planetas_focales:
        objeto_focal = cuerpos.get(nombre_focal)

        if not objeto_focal:
            continue

        lon_focal = objeto_focal.get("lon")

        if lon_focal is None:
            continue

        for nombre_otro, objeto_otro in cuerpos.items():
            agregar_par(
                nombre_focal,
                lon_focal,
                nombre_otro,
                objeto_otro.get("lon"),
            )

        # Aspecto con el Ascendente.
        if asc and asc.get("lon") is not None:
            agregar_par(
                nombre_focal,
                lon_focal,
                "Ascendente",
                asc["lon"],
            )

    # Identificación del tipo de aspecto.
    for par in pares:
        diferencia = abs(par["lon1"] - par["lon2"]) % 360

        if diferencia > 180:
            diferencia = 360 - diferencia

        for tipo, angulo, orbe_maximo, simbolo in ASPECTOS_DEF:
            orbe = abs(diferencia - angulo)

            if orbe <= orbe_maximo:
                orbe_redondeado = round(orbe, 2)

                aspectos.append({
                    "p1": par["p1"],
                    "p2": par["p2"],
                    "tipo": tipo,
                    "simbolo": simbolo,
                    "orbe": orbe_redondeado,
                    "relevancia": (
                        "exacto"
                        if orbe_redondeado <= 1.0
                        else "estructural"
                    ),
                })

                break

    return sorted(
        aspectos,
        key=lambda aspecto: (
            aspecto["orbe"],
            aspecto["p1"],
            aspecto["p2"],
        ),
    )


def obtener_texto_aspecto(
    combinaciones,
    textos_tipo_aspecto,
    planeta,
    tipo_aspecto,
):
    """
    Construye la interpretación de un aspecto combinando:

    1. El significado de la relación entre ambos cuerpos.
    2. La manera en que se expresa según el tipo de aspecto.

    Los diccionarios se reciben como argumentos para permitir
    que cada planeta focal tenga una voz propia.
    """

    texto_combinacion = combinaciones.get(planeta)
    texto_aspecto = textos_tipo_aspecto.get(tipo_aspecto)

    if not texto_combinacion or not texto_aspecto:
        return ""

    return f"{texto_combinacion}\n\n{texto_aspecto}"


def calcular_aspectos_planetas_transpersonales(planetas, asc):
    return calcular_aspectos_modulo(
        planetas,
        asc,
        ("Urano", "Neptuno", "Plutón"),
    )


# ─── RUEDA SIMPLIFICADA: URANO + NEPTUNO + PLUTÓN ────────────────────────────

def dibujar_rueda_planetas_transpersonales(
    carta,
    aspectos,
    archivo_salida,
):
    """
    Rueda focal de Planetas Transpersonales.

    Muestra Urano, Neptuno y Plutón junto con los planetas,
    Nodos o ángulos con los que forman aspectos.
    """

    planetas = carta["planetas"]
    cuspides = carta["cuspides"]
    asc_lon = carta["asc"]["lon"]

    planetas_focales = {
        "Urano",
        "Neptuno",
        "Plutón",
    }

    # Conserva solamente los aspectos en los que participa
    # Urano, Neptuno o Plutón.
    aspectos_transpersonales = [
        aspecto
        for aspecto in aspectos
        if aspecto.get("p1") in planetas_focales
        or aspecto.get("p2") in planetas_focales
    ]

    def lon_a_angulo(lon):
        return math.radians(
            180 + (lon - asc_lon)
        )

    R_EXT = 1.35
    R_SIGN_IN = 1.05
    R_CASA_OUT = 1.02
    R_CASA_IN = 0.65
    R_PLANETA = 0.82

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

    # Casas
    for i, cusp in enumerate(cuspides):
        ang = lon_a_angulo(cusp)

        lw = (
            1.8
            if i in (0, 3, 6, 9)
            else 0.5
        )

        col = (
            "#111"
            if i in (0, 3, 6, 9)
            else "#999"
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

        if i in (0, 3, 6, 9):
            ang_num = lon_a_angulo(
                cusp + 4.0
            )

            r_num = (
                R_CASA_IN + 0.25
            ) / 2 + 0.12

            ax.text(
                math.cos(ang_num) * r_num,
                math.sin(ang_num) * r_num,
                str(i + 1),
                ha="center",
                va="center",
                fontsize=8,
                color="#444",
                fontweight="bold",
                zorder=4,
            )

    # Colores de los aspectos
    _ASP_COL = {
        "□": "#CC2200",
        "☍": "#CC2200",
        "△": "#1A5FA8",
        "✶": "#1A5FA8",
        "⚻": "#2E7D32",
        "=": "#7B2D8B",
    }

    _ASP_LW = {
        "□": 1.4,
        "☍": 1.4,
        "△": 1.1,
        "✶": 1.0,
        "⚻": 0.9,
        "=": 1.2,
    }

    R_ASP = R_CASA_IN - 0.02

    puntos_aspecto = {
        nombre: objeto
        for nombre, objeto in planetas.items()
        if objeto
    }

    puntos_aspecto["Ascendente"] = {
        "lon": carta["asc"]["lon"]
    }

    puntos_aspecto["Medio Cielo"] = {
        "lon": carta["mc"]["lon"]
    }

    # Líneas de aspectos
    for aspecto in aspectos_transpersonales:
        p1 = aspecto["p1"]
        p2 = aspecto["p2"]

        obj1 = puntos_aspecto.get(p1)
        obj2 = puntos_aspecto.get(p2)

        simbolo = aspecto.get("simbolo")

        if (
            not obj1
            or not obj2
            or simbolo not in _ASP_COL
        ):
            continue

        a1 = lon_a_angulo(
            obj1["lon"]
        )

        a2 = lon_a_angulo(
            obj2["lon"]
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
            color=_ASP_COL[simbolo],
            linewidth=_ASP_LW[simbolo],
            alpha=0.64,
            linestyle="solid",
            zorder=2,
        )

    # Urano, Neptuno y Plutón siempre aparecen.
    nombres_visibles = {
        "Urano",
        "Neptuno",
        "Plutón",
    }

    # Añadimos todos los cuerpos que estén aspectados
    # con alguno de los tres planetas transpersonales.
    for aspecto in aspectos_transpersonales:
        for nombre in (
            aspecto["p1"],
            aspecto["p2"],
        ):
            # El Ascendente y el Medio Cielo ya aparecen
            # representados mediante sus ejes.
            if nombre in {
                "Ascendente",
                "Medio Cielo",
            }:
                continue

            if nombre in planetas:
                nombres_visibles.add(nombre)

    puntos = {}

    for nombre in nombres_visibles:
        if (
            nombre in planetas
            and planetas[nombre]
        ):
            puntos[nombre] = planetas[nombre]

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

        # Los planetas transpersonales
        # quedan ligeramente destacados.
        if nombre in planetas_focales:
            fs = 21

        elif nombre in {
            "Nodo Norte",
            "Nodo Sur",
        }:
            fs = 18

        elif nombre == "Sol":
            fs = 18

        else:
            fs = 15

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

    cuerpo = ParagraphStyle(
        "CuerpoAI",
        parent=estilos["BodyText"],
        fontName="Times-Roman",
        fontSize=11,
        leading=16,
        spaceAfter=10,
        alignment=TA_JUSTIFY,
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


def bloque_portada_transpersonales(
    nombre,
    fecha_str,
    hora_str,
    ciudad,
    estilos,
):
    return [
        Spacer(1, 1.7 * cm),

        Paragraph(
            "Planetas Transpersonales",
            estilos["titulo"],
        ),

        Paragraph(
            "Urano · Neptuno · Plutón",
            estilos["centro"],
        ),

        Spacer(1, 0.45 * cm),

        Paragraph(
            "Una lectura sobre cómo expresas tu necesidad de libertad, "
            "cómo habitas tu sensibilidad y cómo transformas aquello "
            "que ya no puede seguir siendo igual.",
            estilos["estilo_frase_final"],
        ),

        Spacer(1, 2.2 * cm),

        Paragraph(
            nombre,
            ParagraphStyle(
                "NombrePortada",
                parent=estilos["centro"],
                fontName="Times-Roman",
                fontSize=24,
                leading=29,
                textColor=colors.HexColor("#8C5A00"),
            ),
        ),

        Spacer(1, 1.15 * cm),

        Paragraph(
            f"{fecha_str} · {hora_str}",
            estilos["centro"],
        ),

        Paragraph(
            ciudad,
            estilos["centro"],
        ),

        Spacer(1, 10 * cm),

        Paragraph(
            "Arquitectura Interna · Un método para sostener cuerpo, "
            "energía y vida con coherencia",
            estilos["estilo_frase_final"],
        ),

        PageBreak(),
    ]


def bloque_bienvenida_transpersonales(estilos):
    texto = (
        "Hay procesos que no dependen únicamente de lo que decides de forma consciente. "
        "A veces aparece una necesidad profunda de vivir con mayor libertad, una sensibilidad "
        "que amplía tu percepción o una transformación interna que te obliga a revisar formas "
        "de vida que ya no te representan.\n\n"

        "En este informe recorrerás tres funciones que actúan más allá de la identidad cotidiana. "
        "Urano muestra dónde necesitas desarrollar mayor autenticidad, libertad y capacidad de cambio. "
        "Neptuno habla de sensibilidad, intuición, imaginación y de la necesidad de encontrar límites "
        "que te permitan habitar todo ello sin perder claridad. Plutón señala los ámbitos donde la vida "
        "te invita a transformar patrones profundos, integrar experiencias y recuperar una relación "
        "más consciente con tu propio poder.\n\n"

        "Estas funciones no actúan de forma aislada. La libertad necesita dirección para no convertirse "
        "en ruptura constante. La sensibilidad necesita límites para no confundirse con desbordamiento. "
        "La transformación necesita tiempo para no convertirse en una exigencia permanente de cambio.\n\n"

        "Comprender cómo trabajan Urano, Neptuno y Plutón en tu carta puede ayudarte a reconocer qué "
        "necesita evolucionar, dónde aparecen tus principales recursos y qué formas de regulación "
        "te permiten integrar estos procesos en tu vida cotidiana."
    )

    elementos = [
        Paragraph(
            "Bienvenida",
            estilos["subtitulo"],
        )
    ]

    elementos += _parrafos_reportlab(
        texto,
        estilos["cuerpo"],
    )

    elementos.append(
        Paragraph(
            "Antes de empezar",
            estilos["subtitulo"],
        )
    )

    elementos.append(
        Paragraph(
            "Cómo leer este cuaderno",
            estilos["subtitulo2"],
        )
    )

    elementos += _parrafos_reportlab(
        "No necesitas comprenderlo todo en una primera lectura. "
        "Recorre el informe con curiosidad y observa qué partes describen mejor "
        "el momento que estás viviendo. Urano, Neptuno y Plutón no hablan de "
        "acontecimientos inevitables, sino de funciones internas que evolucionan "
        "a lo largo de la vida y que pueden expresarse de maneras muy diferentes "
        "según el nivel de consciencia, equilibrio y regulación con que las habites.",
        estilos["cuerpo"],
    )

    return elementos


def bloque_rueda_transpersonales(
    ruta_rueda,
    estilos,
):
    return [
        Spacer(1, 0.15 * cm),
        Image(
            ruta_rueda,
            width=13.5 * cm,
            height=13.5 * cm,
        ),
    ]


def bloque_resumen_transpersonales(
    carta,
    estilos,
):
    planetas = carta["planetas"]

    urano = planetas.get("Urano", {})
    neptuno = planetas.get("Neptuno", {})
    pluton = planetas.get("Plutón", {})

    estilo_celda = ParagraphStyle(
        "CeldaResumenTranspersonales",
        parent=estilos["cuerpo"],
        fontName="Times-Roman",
        fontSize=8.5,
        leading=10.5,
        spaceAfter=0,
        alignment=TA_LEFT,
    )

    estilo_celda_centro = ParagraphStyle(
        "CeldaResumenTranspersonalesCentro",
        parent=estilo_celda,
        alignment=TA_CENTER,
    )

    estilo_cabecera = ParagraphStyle(
        "CabeceraResumenTranspersonales",
        parent=estilo_celda,
        fontName="Times-Bold",
        textColor=colors.HexColor("#1E508C"),
        alignment=TA_CENTER,
    )

    tabla_datos = [
        [
            Paragraph("Planeta", estilo_cabecera),
            Paragraph("Signo", estilo_cabecera),
            Paragraph("Casa", estilo_cabecera),
            Paragraph("Función", estilo_cabecera),
        ],
        [
            Paragraph("Urano", estilo_celda),
            Paragraph(
                urano.get("signo", ""),
                estilo_celda_centro,
            ),
            Paragraph(
                f"Casa {urano.get('casa', '')}",
                estilo_celda_centro,
            ),
            Paragraph(
                "Libertad, autenticidad y cambio consciente",
                estilo_celda,
            ),
        ],
        [
            Paragraph("Neptuno", estilo_celda),
            Paragraph(
                neptuno.get("signo", ""),
                estilo_celda_centro,
            ),
            Paragraph(
                f"Casa {neptuno.get('casa', '')}",
                estilo_celda_centro,
            ),
            Paragraph(
                "Sensibilidad, intuición, imaginación y discernimiento",
                estilo_celda,
            ),
        ],
        [
            Paragraph("Plutón", estilo_celda),
            Paragraph(
                pluton.get("signo", ""),
                estilo_celda_centro,
            ),
            Paragraph(
                f"Casa {pluton.get('casa', '')}",
                estilo_celda_centro,
            ),
            Paragraph(
                "Transformación, integración y regeneración",
                estilo_celda,
            ),
        ],
    ]

    tabla = Table(
        tabla_datos,
        colWidths=[
            2.1 * cm,
            2.2 * cm,
            2.1 * cm,
            6.6 * cm,
        ],
    )

    tabla.setStyle(TableStyle([
        (
            "BACKGROUND",
            (0, 0),
            (-1, 0),
            colors.HexColor("#EDE3D3"),
        ),
        (
            "TEXTCOLOR",
            (0, 0),
            (-1, 0),
            colors.HexColor("#1E508C"),
        ),
        (
            "GRID",
            (0, 0),
            (-1, -1),
            0.25,
            colors.HexColor("#D8CBB8"),
        ),
        (
            "BOX",
            (0, 0),
            (-1, -1),
            1.2,
            colors.HexColor("#8C5A00"),
        ),
        (
            "VALIGN",
            (0, 0),
            (-1, -1),
            "MIDDLE",
        ),
        (
            "LEFTPADDING",
            (0, 0),
            (-1, -1),
            6,
        ),
        (
            "RIGHTPADDING",
            (0, 0),
            (-1, -1),
            6,
        ),
        (
            "TOPPADDING",
            (0, 0),
            (-1, -1),
            7,
        ),
        (
            "BOTTOMPADDING",
            (0, 0),
            (-1, -1),
            7,
        ),
    ]))

    return [
        Paragraph(
            "La arquitectura de tus funciones transpersonales",
            estilos["subtitulo"],
        ),
        Spacer(
            1,
            0.9 * cm,
        ),
        tabla,
        PageBreak(),
    ]




def bloque_aspectos_principales_transpersonales(
    aspectos,
    estilos,
):
    """
    Muestra una tabla resumen con todos los aspectos de
    Urano, Neptuno y Plutón.

    Cada pareja aparece una sola vez porque la lista de aspectos
    ya se genera sin duplicados.
    """

    elementos = [
        Spacer(1, 0.8 * cm),
        Paragraph(
            "Aspectos principales",
            estilos["subtitulo2"],
        ),
        Spacer(1, 0.45 * cm),
    ]

    angulo_aspecto = {
        "=": "0°",
        "✶": "60°",
        "□": "90°",
        "△": "120°",
        "⚻": "150°",
        "☍": "180°",
    }

    if not aspectos:
        elementos.append(
            Paragraph(
                "No aparecen aspectos principales de Urano, Neptuno o Plutón "
                "dentro de los orbes utilizados en este informe.",
                estilos["cuerpo"],
            )
        )

        return elementos

    datos = [
        [
            "Planeta",
            "Aspecto",
            "Punto",
            "Tipo",
            "Orbe",
        ]
    ]

    for aspecto in aspectos:
        datos.append([
            aspecto.get("p1", ""),
            angulo_aspecto.get(
                aspecto.get("simbolo", ""),
                "",
            ),
            aspecto.get("p2", ""),
            aspecto.get("tipo", ""),
            f'{aspecto.get("orbe", 0):.1f}°',
        ])

    tabla = Table(
        datos,
        colWidths=[
            3.0 * cm,
            1.4 * cm,
            3.0 * cm,
            3.0 * cm,
            1.5 * cm,
        ],
        repeatRows=1,
    )

    tabla.setStyle(TableStyle([
        (
            "BACKGROUND",
            (0, 0),
            (-1, 0),
            colors.HexColor("#EDE3D3"),
        ),
        (
            "TEXTCOLOR",
            (0, 0),
            (-1, 0),
            colors.HexColor("#1E508C"),
        ),
        (
            "FONTNAME",
            (0, 0),
            (-1, 0),
            "Times-Bold",
        ),
        (
            "FONTNAME",
            (0, 1),
            (-1, -1),
            "Times-Roman",
        ),
        (
            "FONTSIZE",
            (0, 0),
            (-1, -1),
            9,
        ),
        (
            "GRID",
            (0, 0),
            (-1, -1),
            0.25,
            colors.HexColor("#D8CBB8"),
        ),
        (
            "BOX",
            (0, 0),
            (-1, -1),
            1.2,
            colors.HexColor("#8C5A00"),
        ),
        (
            "VALIGN",
            (0, 0),
            (-1, -1),
            "MIDDLE",
        ),
        (
            "ALIGN",
            (1, 0),
            (1, -1),
            "CENTER",
        ),
        (
            "ALIGN",
            (4, 0),
            (4, -1),
            "CENTER",
        ),
        (
            "TOPPADDING",
            (0, 0),
            (-1, -1),
            6,
        ),
        (
            "BOTTOMPADDING",
            (0, 0),
            (-1, -1),
            6,
        ),
    ]))

    elementos.append(tabla)

    return elementos


# ─── BLOQUES DE CONTENIDO: PLANETAS TRANSPERSONALES ──────────────────────────

PLANETAS_TRANSPERSONALES = {
    "Urano",
    "Neptuno",
    "Plutón",
}

ORDEN_PLANETAS_TRANSPERSONALES = {
    "Urano": 1,
    "Neptuno": 2,
    "Plutón": 3,
}


def obtener_aspectos_de_planeta(aspectos, planeta):
    """
    Devuelve todos los aspectos en los que participa el planeta indicado,
    ordenados desde el orbe más exacto hasta el más amplio.
    """
    aspectos_planeta = []

    for aspecto in aspectos:
        p1 = aspecto.get("p1")
        p2 = aspecto.get("p2")

        if planeta not in (p1, p2):
            continue

        otro_punto = p2 if p1 == planeta else p1

        aspectos_planeta.append({
            "otro_punto": otro_punto,
            "tipo": aspecto.get("tipo", ""),
            "simbolo": aspecto.get("simbolo", ""),
            "orbe": aspecto.get("orbe", 0),
            "relevancia": aspecto.get("relevancia", ""),
        })

    return sorted(
        aspectos_planeta,
        key=lambda aspecto: aspecto["orbe"],
    )


def bloque_posicion_planeta(
    planeta,
    carta,
    textos_signo,
    textos_casa,
    estilos,
):
    """
    Genera la lectura del planeta por signo y por casa.
    """
    datos_planeta = carta["planetas"].get(planeta)

    if not datos_planeta:
        return []

    signo = datos_planeta.get("signo", "")
    casa = datos_planeta.get("casa", "")

    texto_signo = textos_signo.get(signo, "")

    texto_casa = (
        textos_casa.get(casa)
        or textos_casa.get(f"Casa {casa}", "")
    )

    elementos = [
        Paragraph(
            f"{planeta} en tu carta",
            estilos["subtitulo"],
        ),
        Paragraph(
            f"{planeta} en {signo} · Casa {casa}",
            estilos["subtitulo2"],
        ),
    ]

    if texto_signo:
        elementos.append(
            Paragraph(
                f"{planeta} en {signo}",
                estilos["titulo_aspecto"],
            )
        )

        elementos += _parrafos_reportlab(
            texto_signo,
            estilos["cuerpo"],
        )

    if texto_casa:
        elementos.append(
            Paragraph(
                f"{planeta} en la Casa {casa}",
                estilos["titulo_aspecto"],
            )
        )

        elementos += _parrafos_reportlab(
            texto_casa,
            estilos["cuerpo"],
        )

    return elementos


def bloque_aspectos_planeta(
    planeta,
    aspectos,
    combinaciones,
    textos_tipo_aspecto,
    estilos,
):
    """
    Genera las interpretaciones de los aspectos de un planeta.
    """
    aspectos_planeta = obtener_aspectos_de_planeta(
        aspectos,
        planeta,
    )

    elementos = [
        Paragraph(
            f"Los aspectos de {planeta}",
            estilos["subtitulo"],
        ),
    ]

    if not aspectos_planeta:
        elementos.append(
            Paragraph(
                f"No se han encontrado aspectos principales de {planeta} "
                "dentro de los orbes utilizados en este informe.",
                estilos["cuerpo"],
            )
        )

        return elementos

    aspectos_con_texto = 0

    for aspecto in aspectos_planeta:
        otro_punto = aspecto["otro_punto"]
        tipo = aspecto["tipo"]

        # Evita repetir los aspectos entre Urano, Neptuno y Plutón.
        #
        # Orden de interpretación:
        # Urano interpreta sus vínculos con Neptuno y Plutón.
        # Neptuno interpreta su vínculo con Plutón.
        # Los planetas posteriores no repiten el mismo aspecto.

        if (
            planeta in PLANETAS_TRANSPERSONALES
            and otro_punto in PLANETAS_TRANSPERSONALES
            and ORDEN_PLANETAS_TRANSPERSONALES[planeta]
            > ORDEN_PLANETAS_TRANSPERSONALES[otro_punto]
        ):
            continue

        texto = obtener_texto_aspecto(
            combinaciones,
            textos_tipo_aspecto,
            otro_punto,
            tipo,
        )

        if not texto:
            continue

        aspectos_con_texto += 1

        titulo = (
            f"{planeta} con {otro_punto} "
            f"— {tipo}"
        )

        elementos.append(
            Paragraph(
                titulo,
                estilos["subtitulo2"],
            )
        )

        elementos += _parrafos_reportlab(
            texto,
            estilos["cuerpo"],
        )

    if aspectos_con_texto == 0:
        elementos.append(
            Paragraph(
                f"Los aspectos encontrados para {planeta} todavía no disponen "
                "de una interpretación asociada en este módulo.",
                estilos["cuerpo"],
            )
        )

    return elementos


def bloque_integracion_planeta(
    planeta,
    integracion,
    estilos,
):
    """
    Genera las secciones de necesidades, cuidado, equilibrio,
    desregulación, observación e integración del planeta.
    """
    elementos = [
        Paragraph(
            f"Integrar tu {planeta}",
            estilos["subtitulo"],
        )
    ]

    orden_bloques = [
        "necesidades",
        "cuidar",
        "equilibrio",
        "desregulacion",
        "pregunta",
        "integracion",
    ]

    for clave in orden_bloques:
        bloque = integracion.get(clave)

        if not bloque:
            continue

        titulo = bloque.get("titulo", "")
        texto = bloque.get("texto", "")

        if titulo:
            elementos.append(
                Paragraph(
                    titulo,
                    estilos["subtitulo2"],
                )
            )

        if texto:
            elementos += _parrafos_reportlab(
                texto,
                estilos["cuerpo"],
            )

    return elementos


def bloque_planeta_transpersonal(
    planeta,
    carta,
    aspectos,
    textos_signo,
    textos_casa,
    combinaciones,
    textos_tipo_aspecto,
    integracion,
    subtitulo_capitulo,
    estilos,
):
    """
    Genera el capítulo completo de un planeta transpersonal:

    - apertura del capítulo;
    - interpretación por signo;
    - interpretación por casa;
    - aspectos;
    - necesidades;
    - cuidado;
    - equilibrio;
    - desregulación;
    - pregunta de observación;
    - integración final.
    """

    elementos = [
        PageBreak(),
        Paragraph(
            planeta,
            estilos["titulo"],
        ),
        Paragraph(
            subtitulo_capitulo,
            estilos["estilo_frase_final"],
        ),
        Spacer(
            1,
            0.6 * cm,
        ),
    ]

    elementos += bloque_posicion_planeta(
        planeta=planeta,
        carta=carta,
        textos_signo=textos_signo,
        textos_casa=textos_casa,
        estilos=estilos,
    )

    elementos += bloque_aspectos_planeta(
        planeta=planeta,
        aspectos=aspectos,
        combinaciones=combinaciones,
        textos_tipo_aspecto=textos_tipo_aspecto,
        estilos=estilos,
    )

    elementos += bloque_integracion_planeta(
        planeta=planeta,
        integracion=integracion,
        estilos=estilos,
    )

    return elementos


def bloque_urano(
    carta,
    aspectos,
    estilos,
):
    return bloque_planeta_transpersonal(
        planeta="Urano",
        carta=carta,
        aspectos=aspectos,
        textos_signo=URANO_SIGNO,
        textos_casa=URANO_CASA,
        combinaciones=URANO_COMBINACIONES,
        textos_tipo_aspecto=URANO_TEXTOS_TIPO_ASPECTO,
        integracion=URANO_INTEGRACION,
        subtitulo_capitulo=(
            "La forma en que necesitas desarrollar libertad, autenticidad "
            "y capacidad para introducir cambios conscientes en tu vida."
        ),
        estilos=estilos,
    )


def bloque_neptuno(
    carta,
    aspectos,
    estilos,
):
    return bloque_planeta_transpersonal(
        planeta="Neptuno",
        carta=carta,
        aspectos=aspectos,
        textos_signo=NEPTUNO_SIGNO,
        textos_casa=NEPTUNO_CASA,
        combinaciones=NEPTUNO_COMBINACIONES,
        textos_tipo_aspecto=NEPTUNO_TEXTOS_TIPO_ASPECTO,
        integracion=NEPTUNO_INTEGRACION,
        subtitulo_capitulo=(
            "La forma en que habitas tu sensibilidad, desarrollas intuición "
            "y encuentras límites que te permiten conservar claridad."
        ),
        estilos=estilos,
    )


def bloque_pluton(
    carta,
    aspectos,
    estilos,
):
    return bloque_planeta_transpersonal(
        planeta="Plutón",
        carta=carta,
        aspectos=aspectos,
        textos_signo=PLUTON_SIGNO,
        textos_casa=PLUTON_CASA,
        combinaciones=PLUTON_COMBINACIONES,
        textos_tipo_aspecto=PLUTON_TEXTOS_TIPO_ASPECTO,
        integracion=PLUTON_INTEGRACION,
        subtitulo_capitulo=(
            "La forma en que transformas patrones profundos, integras "
            "lo vivido y recuperas una relación consciente con tu poder."
        ),
        estilos=estilos,
    )


def generar_pdf_planetas_transpersonales(
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
    aspectos,
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

    contenido += bloque_portada_transpersonales(
        nombre,
        fecha_str,
        hora_str,
        ciudad,
        estilos,
    )

    contenido += bloque_bienvenida_transpersonales(
        estilos,
    )

    contenido += bloque_rueda_transpersonales(
        ruta_rueda,
        estilos,
    )

    contenido += bloque_resumen_transpersonales(
        carta,
        estilos,
    )

    contenido += bloque_aspectos_principales_transpersonales(
        aspectos,
        estilos,
    )

    contenido += bloque_urano(
        carta,
        aspectos,
        estilos,
    )

    contenido += bloque_neptuno(
        carta,
        aspectos,
        estilos,
    )

    contenido += bloque_pluton(
        carta,
        aspectos,
        estilos,
    )



    # ── CIERRE ────────────────────────────────────────────────────

    contenido.append(
        KeepTogether([
            Paragraph(
                "Cierre",
                estilos["subtitulo"],
            ),
            Paragraph(
                "Comprender cómo necesitas diferenciarte, cómo habitas tu sensibilidad "
                "y de qué manera transformas los patrones que ya no te representan puede "
                "ayudarte a relacionarte con tus procesos internos de una forma más consciente.",
                estilos["cuerpo"],
            ),
            Paragraph(
                "Urano, Neptuno y Plutón no describen fuerzas separadas. Urano impulsa "
                "la autenticidad y el cambio; Neptuno amplía la sensibilidad y la percepción; "
                "Plutón transforma, integra y regenera. Cuando estas funciones encuentran "
                "una forma equilibrada de expresarse, puedes evolucionar sin romperte, "
                "sentir sin perder claridad y transformarte sin dejar de reconocerte.",
                estilos["cuerpo"],
            ),
        ])
    )

    contenido.append(
        Spacer(
            1,
            0.35 * cm,
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


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print("═" * 55)
    print("  URANO · NEPTUNO · PLUTÓN — Arquitectura Interna")
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
        lat, lon = geocodificar(ciudad)

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

    aspectos = calcular_aspectos_planetas_transpersonales(
        carta["planetas"],
        carta["asc"],
    )

    nombre_f = (
        nombre
        .replace(" ", "_")
        .replace("/", "-")
        .replace("\\", "-")
    )

    ruta_base = os.path.join(
        BASE_DIR,
        nombre_f + "_Planetas_Transpersonales",
    )

    ruta_pdf = ruta_base + ".pdf"
    ruta_rueda = ruta_base + "_rueda.png"

    print("Generando rueda...")

    dibujar_rueda_planetas_transpersonales(
        carta,
        aspectos,
        ruta_rueda,
    )

    print("Generando PDF con ReportLab...")

    generar_pdf_planetas_transpersonales(
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
        aspectos,
        ruta_rueda,
    )

    print(
        f"\nPDF generado correctamente:\n{ruta_pdf}"
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
        "Generando informe Urano · Neptuno · Plutón para:",
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

        # ── ASPECTOS DE URANO, NEPTUNO Y PLUTÓN ───────────────

        aspectos = calcular_aspectos_planetas_transpersonales(
            carta["planetas"],
            carta["asc"],
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
            nombre_f + "_Planetas_Transpersonales",
        )

        ruta_pdf = ruta_base + ".pdf"
        ruta_rueda = ruta_base + "_rueda.png"

        # ── RUEDA ─────────────────────────────────────────────

        dibujar_rueda_planetas_transpersonales(
            carta,
            aspectos,
            ruta_rueda,
        )

        # ── PDF ───────────────────────────────────────────────

        generar_pdf_planetas_transpersonales(
            ruta_pdf,
            carta,
            nombre,
            anio,
            mes,
            dia,
            hora_num,
            minuto,
            lugar,
            lat,
            lon,
            tz_name,
            aspectos,
            ruta_rueda,
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
            "Error generando Urano · Neptuno · Plutón:",
            error,
        )

        return {
            "ok": False,
            "error": str(error),
        }

    finally:
        plt.close("all")
        gc.collect()


if __name__ == "__main__":
    main()