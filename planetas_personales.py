#!/usr/bin/env python3
"""
4. Planetas Personales — Arquitectura Interna

Interpreta el procesamiento de la información (Mercurio),
la forma de valorar y vincularte (Venus),
y la capacidad de actuar y afirmarte (Marte)
dentro de la carta natal.
"""

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
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
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
COLORES_ELEMENTO = {"Fuego":"#CC2200","Tierra":"#2E7D32","Aire":"#E67E00","Agua":"#1A5FA8"}
COLORES_PLANETA  = {
    "Sol":"#CC2200","Marte":"#CC2200","Júpiter":"#CC2200",
    "Venus":"#2E7D32","Saturno":"#2E7D32",
    "Mercurio":"#E67E00","Urano":"#E67E00",
    "Luna":"#1A5FA8","Neptuno":"#1A5FA8","Plutón":"#1A5FA8",
    "Quirón":"#7B2D8B","Lilith":"#7B2D8B",
    "Nodo Norte":"#888800","Nodo Sur":"#888800",
}


# ─── TEXTOS: MERCURIO ─────────────────────────────────────────────
MERCURIO_SIGNO = {

"Aries": (
    "Tu manera de pensar necesita movimiento. Comprendes mejor cuando puedes explorar, preguntar, probar y sacar tus propias conclusiones. "
    "Las ideas suelen aparecer deprisa y muchas veces las expresas casi al mismo tiempo que las descubres.\n\n"

    "También tiendes a comunicarte de forma directa. Prefieres las conversaciones vivas, donde las ideas pueden moverse con libertad, y te cuesta mantener el interés cuando todo se vuelve excesivamente lento, repetitivo o lleno de rodeos. "
    "No necesitas tener todas las respuestas antes de hablar. Muchas veces piensas mientras conversas.\n\n"

    "Cuando la impaciencia toma el control puedes responder antes de haber escuchado del todo o dar por cerrada una idea demasiado pronto. "
    "No porque te falte capacidad de reflexión, sino porque tu mente necesita sentir que avanza. Aprender a detenerte unos instantes antes de responder suele darte una comprensión mucho más completa sin perder espontaneidad."
),

"Tauro": (
    "Tu manera de pensar necesita tiempo para asentarse. No acostumbras a cambiar de opinión con facilidad, pero cuando comprendes algo suele quedarse contigo de forma profunda y estable. "
    "Prefieres construir el conocimiento poco a poco antes que acumular información sin orden.\n\n"

    "Te comunicas de una forma serena y bastante práctica. Sueles escoger bien las palabras y no tienes necesidad de hablar por hablar. "
    "Valoras las conversaciones que aportan algo útil o que permiten profundizar sin prisas, más que los intercambios rápidos o superficiales.\n\n"

    "Los cambios constantes de criterio, la presión por decidir deprisa o la sensación de que todo cambia continuamente pueden hacer que te cierres o que necesites más tiempo para integrar lo que ocurre. "
    "Cuando respetas tu propio ritmo, desarrollas una gran capacidad para convertir las ideas en algo sólido y aplicable."
),

"Géminis": (
    "Tu manera de pensar es curiosa, rápida y abierta. Necesitas hacer preguntas, relacionar ideas y descubrir conexiones para comprender el mundo. "
    "Aprendes conversando, leyendo, observando y dejando que una idea te lleve a la siguiente.\n\n"

    "La comunicación ocupa un lugar muy importante en tu vida. Expresar lo que piensas, escuchar perspectivas distintas y jugar con las palabras forma parte de tu manera de aprender. "
    "Muchas veces una conversación te ayuda a entender algo que todavía no habías terminado de ordenar por dentro.\n\n"

    "El reto aparece cuando hay demasiados estímulos al mismo tiempo. Puedes abrir muchas líneas de pensamiento y terminar sintiendo que ninguna llega a desarrollarse del todo. "
    "Encontrar un hilo conductor no limita tu curiosidad; al contrario, permite que toda esa riqueza mental encuentre una dirección."
),

"Cáncer": (
    "Tu manera de pensar está profundamente unida a lo que sientes. Comprendes mejor cuando puedes conectar la información con tu experiencia y darle un significado personal. "
    "No sueles separar fácilmente la mente del mundo emocional.\n\n"

    "Al comunicarte buscas cercanía y confianza. Es más fácil que expreses lo que realmente piensas cuando te sientes seguro y percibes que hay escucha al otro lado. "
    "Las conversaciones frías, demasiado impersonales o excesivamente racionales pueden dejarte con la sensación de que falta algo importante.\n\n"

    "Cuando te sientes herido o emocionalmente desbordado puedes guardar silencio, interpretar las palabras desde la sensibilidad o dar demasiadas vueltas a una misma situación. "
    "Con el tiempo aprendes que expresar lo que necesitas con claridad suele acercarte mucho más a los demás que intentar protegerte detrás del silencio."
),

"Leo": (
    "Tu manera de pensar necesita sentirse libre para crear, expresar y aportar algo propio. "
    "No te conformas con repetir lo que ya existe; buscas comprender desde una mirada personal y encontrar una forma única de comunicarlo. "
    "Cuando una idea despierta tu entusiasmo, eres capaz de contagiarla con mucha fuerza.\n\n"

    "Sueles comunicarte de manera cálida, expresiva y cercana. Te gusta que las conversaciones tengan vida y que haya espacio para compartir opiniones, experiencias y creatividad. "
    "Cuando sientes que puedes mostrarte tal como eres, las palabras fluyen con naturalidad.\n\n"

    "Lo que más bloquea tu mente es sentir que tu voz no cuenta o que necesitas esconder continuamente lo que piensas para adaptarte a los demás. "
    "Cuando recuperas la confianza para expresarte desde la autenticidad, tu comunicación se convierte en una fuente de inspiración para quienes te rodean."
),

"Virgo": (
    "Tu manera de pensar busca comprender cómo funcionan las cosas. "
    "Necesitas analizar, ordenar y diferenciar los pequeños matices antes de sacar conclusiones. "
    "Tu atención suele dirigirse hacia los detalles que otras personas pasan por alto.\n\n"

    "Te comunicas de forma precisa. Sueles intentar que las palabras sean claras y útiles, evitando confusiones o interpretaciones ambiguas. "
    "Disfrutas de las conversaciones donde es posible profundizar, hacer preguntas y encontrar soluciones concretas.\n\n"

    "Cuando la exigencia se vuelve excesiva puedes entrar en un análisis interminable, corrigiendo una y otra vez lo que dices o pensando que nunca está suficientemente bien explicado. "
    "Con el tiempo descubres que comunicar con claridad no significa buscar la perfección, sino ofrecer lo mejor de lo que sabes en ese momento."
),

"Libra": (
    "Tu manera de pensar crece cuando puede contrastarse con otras personas. "
    "Necesitas escuchar diferentes puntos de vista para construir una comprensión más amplia de la realidad. "
    "Muchas veces una buena conversación te ayuda a descubrir ideas que no habrían aparecido pensando a solas.\n\n"

    "Sueles comunicarte con tacto y buscando el equilibrio. Te importa que exista un verdadero intercambio y procuras expresar tus opiniones sin romper el vínculo con quien tienes delante. "
    "Tienes facilidad para comprender varias perspectivas al mismo tiempo.\n\n"

    "El reto aparece cuando intentas agradar tanto que dejas de expresar lo que realmente piensas o cuando retrasas una decisión esperando encontrar la respuesta perfecta para todos. "
    "Aprender a sostener el desacuerdo sin perder la conexión permite que tu voz gane fuerza y autenticidad."
),

"Escorpio": (
    "Tu manera de pensar busca llegar al fondo de las cosas. "
    "Las explicaciones superficiales rara vez te satisfacen. Necesitas comprender qué mueve realmente a las personas, qué hay detrás de los acontecimientos y qué permanece oculto bajo la superficie.\n\n"

    "Cuando hablas, prefieres las conversaciones sinceras a los intercambios vacíos. "
    "No siempre dices todo lo que piensas, pero observas mucho antes de expresar una opinión. "
    "Tu comunicación suele tener intensidad y capacidad para señalar aquello que otras personas prefieren evitar.\n\n"

    "Cuando desaparece la confianza puedes guardar demasiado para ti, interpretar las palabras desde la sospecha o dar vueltas una y otra vez a una conversación. "
    "A medida que aprendes a compartir lo que descubres sin necesidad de protegerte constantemente, tu capacidad para comprender y transformar a través de la palabra se vuelve extraordinaria."
),

"Sagitario": (
    "Tu manera de pensar necesita amplitud. Comprendes mejor cuando puedes relacionar las ideas entre sí y descubrir el sentido que hay detrás de los acontecimientos. "
    "No te interesa únicamente acumular información; necesitas entender para qué sirve y cómo encaja dentro de una visión más amplia de la vida.\n\n"

    "Sueles comunicarte con entusiasmo y naturalidad. Te gusta compartir lo que aprendes, abrir conversaciones que inviten a reflexionar y contagiar a otras personas aquello que te inspira. "
    "Disfrutas cuando las palabras pueden abrir horizontes, cuestionar creencias o despertar nuevas posibilidades.\n\n"

    "El reto aparece cuando das por cierta una idea antes de haberla contrastado o cuando el entusiasmo te lleva a simplificar cuestiones complejas. "
    "Aprender a combinar tu capacidad para ver el conjunto con la atención a los pequeños detalles hace que tu comunicación gane profundidad sin perder frescura."
),

"Capricornio": (
    "Tu manera de pensar busca estructura y coherencia. Necesitas comprender cómo funcionan las cosas para poder construir sobre ellas con seguridad. "
    "Sueles valorar el conocimiento que resiste el paso del tiempo y que puede aplicarse de forma práctica en la vida cotidiana.\n\n"

    "Te comunicas de forma clara, prudente y bastante medida. Antes de hablar acostumbras a pensar lo que quieres decir y no tienes necesidad de intervenir continuamente para sentirte presente. "
    "Cuando compartes una opinión suele estar bien fundamentada.\n\n"

    "Puedes volverte demasiado exigente contigo y sentir que todavía no sabes lo suficiente como para expresar una idea. "
    "Con el tiempo descubres que la claridad no nace de saberlo todo, sino de atreverte a compartir aquello que realmente has comprendido."
),

"Acuario": (
    "Tu manera de pensar necesita libertad. Comprendes mejor cuando puedes observar la realidad desde ángulos diferentes y cuestionar aquello que otras personas dan por sentado. "
    "Te resulta natural conectar ideas muy distintas y encontrar relaciones que no siempre son evidentes para los demás.\n\n"

    "Tu comunicación suele ser original y estimulante. Disfrutas intercambiando puntos de vista, imaginando nuevas posibilidades y participando en conversaciones donde cada persona aporta una mirada diferente. "
    "Las ideas cobran vida cuando pueden compartirse y evolucionar en contacto con otras personas.\n\n"

    "El reto aparece cuando te desconectas emocionalmente de lo que comunicas o cuando te centras tanto en la innovación que olvidas comprobar si los demás pueden seguir el hilo de tu razonamiento. "
    "Cuando unes originalidad y cercanía, tu capacidad para abrir nuevas formas de comprender resulta profundamente inspiradora."
),

"Piscis": (
    "Tu manera de pensar es intuitiva y muy receptiva. Muchas veces comprendes algo antes de poder explicarlo con palabras, porque tu percepción capta matices que no siempre siguen un razonamiento lineal. "
    "Necesitas tiempo para traducir en ideas aquello que primero aparece como una sensación o una imagen interior.\n\n"

    "Tu comunicación suele ser sensible, empática y llena de matices. Tienes facilidad para conectar con el mundo emocional de otras personas y expresar aquello que resulta difícil poner en palabras. "
    "Cuando encuentras el lenguaje adecuado, puedes transmitir experiencias muy profundas de una forma sencilla.\n\n"

    "El reto aparece cuando absorbes demasiada información del entorno, mezclas tus propias ideas con las de los demás o te cuesta expresar con claridad lo que percibes. "
    "Aprender a poner límites también en la comunicación permite que tu intuición se convierta en una fuente de comprensión, en lugar de generar confusión."
),
}

MERCURIO_CASA = {

1: (
    "Tu manera de pensar forma parte de la imagen que proyectas al mundo. Necesitas comprender por experiencia propia antes de aceptar una idea como verdadera y rara vez te limitas a repetir lo que otros dicen. Tu curiosidad suele estar muy presente desde el primer contacto con cualquier experiencia.\n\n"

    "La comunicación ocupa un lugar importante en tu forma de relacionarte. Las personas suelen percibirte como alguien con opiniones propias, que hace preguntas y que necesita expresar lo que piensa para terminar de comprenderlo. Muchas veces ordenas tus ideas mientras las compartes.\n\n"

    "El aprendizaje consiste en recordar que escuchar también forma parte de comunicar. Cuando consigues equilibrar la expresión de tus propias ideas con una verdadera apertura hacia las de los demás, tu capacidad para inspirar, enseñar y generar conversaciones se multiplica."
),

2: (
    "Necesitas comprender aquello que aporta estabilidad y valor a tu vida. Tu mente suele dirigirse hacia conocimientos que pueden aplicarse de forma práctica, ayudarte a desarrollar recursos o darte mayor seguridad para desenvolverte en el mundo.\n\n"

    "Sueles comunicarte con calma y prefieres hablar de aquello que conoces bien. No acostumbras a cambiar de opinión por presión externa y valoras que las conversaciones tengan un contenido útil, realista o que pueda llevarse a la práctica.\n\n"

    "Cuando sientes inseguridad puedes aferrarte a ideas conocidas simplemente porque te resultan familiares. Con el tiempo descubres que abrirte a nuevas perspectivas no pone en riesgo tu estabilidad; al contrario, amplía los recursos con los que puedes construirla."
),

3: (
    "Esta es una de las posiciones más naturales para Mercurio. Tu mente necesita movimiento, intercambio y aprendizaje constante. Las preguntas, las conversaciones, la lectura, la escritura o cualquier forma de adquirir conocimientos forman parte de tu manera de crecer.\n\n"

    "Te resulta natural comunicarte, compartir ideas y aprender del entorno cercano. Muchas veces una conversación cotidiana puede despertar una comprensión importante porque tu mente disfruta estableciendo conexiones entre personas, experiencias e información.\n\n"

    "El reto aparece cuando acumulas demasiados estímulos o saltas de un tema a otro sin terminar de profundizar. Encontrar momentos para integrar todo lo aprendido permite que tu curiosidad se convierta en verdadero conocimiento."
),

4: (
    "Tu manera de pensar está profundamente influida por tu mundo interior. Necesitas comprender tus emociones, tu historia y aquello que da sentido a tus raíces antes de poder construir una visión estable del presente.\n\n"

    "Te resulta más fácil expresar lo que realmente piensas cuando existe confianza. Las conversaciones íntimas suelen ser mucho más importantes para ti que los intercambios superficiales, porque necesitas sentir que puedes hablar desde un lugar auténtico.\n\n"

    "Cuando las emociones quedan sin expresar, la mente puede quedarse dando vueltas una y otra vez sobre las mismas situaciones. Aprender a poner palabras a lo que sientes ayuda a ordenar tanto el mundo emocional como el pensamiento."
),

5: (
    "Tu manera de pensar necesita crear, jugar y expresarse. Comprendes mejor cuando puedes experimentar con las ideas, aportar algo propio y dejar espacio para la imaginación. Aprender no consiste solo en adquirir conocimientos, sino también en disfrutar del proceso y convertirlo en una forma de expresión.\n\n"

    "Tu comunicación suele ser cercana, cálida y creativa. Te resulta natural explicar las cosas de una forma que despierte interés, emocione o invite a participar. Las conversaciones cobran vida cuando puedes mostrar entusiasmo y compartir aquello que realmente te apasiona.\n\n"

    "El reto aparece cuando buscas el reconocimiento a través de tus ideas o cuando dejas de expresarte por miedo a que lo que aportas no sea apreciado. Descubrir que el verdadero valor de tu comunicación nace de la autenticidad, y no de la aprobación, permite que tu creatividad fluya con mucha más libertad."
),

6: (
    "Tu manera de pensar necesita comprender cómo mejorar las cosas. Observas con facilidad los detalles, detectas lo que puede optimizarse y disfrutas encontrando soluciones prácticas para el día a día. Aprendes especialmente bien cuando puedes aplicar lo que sabes de forma útil y concreta.\n\n"

    "Tu comunicación suele ser clara, organizada y orientada a resolver problemas. Te gusta explicar las cosas de manera comprensible y eres capaz de convertir cuestiones complejas en pasos sencillos cuando encuentras el método adecuado.\n\n"

    "El reto aparece cuando la mente se centra únicamente en los errores, las obligaciones o aquello que todavía falta por hacer. Aprender a reconocer también lo que funciona aporta equilibrio a tu pensamiento y evita que la autoexigencia termine agotando tu claridad mental."
),

7: (
    "Tu manera de pensar crece a través del encuentro con otras personas. Necesitas escuchar, contrastar opiniones y abrirte a perspectivas diferentes para ampliar tu comprensión de la realidad. Muchas veces descubres lo que realmente piensas mientras dialogas con alguien.\n\n"

    "La comunicación ocupa un lugar fundamental en tus relaciones. Valoras el intercambio sincero, la escucha mutua y las conversaciones que permiten construir puentes entre puntos de vista distintos. Sueles tener facilidad para comprender cómo piensa la otra persona.\n\n"

    "El reto aparece cuando adaptas demasiado tu discurso para evitar el conflicto o cuando dejas que sean los demás quienes definan tus propias ideas. Aprender a expresar tu verdad sin romper el vínculo fortalece tanto tu comunicación como tus relaciones."
),

8: (
    "Tu manera de pensar necesita ir más allá de las apariencias. Sientes una curiosidad natural por comprender aquello que permanece oculto: las motivaciones profundas, las emociones difíciles, las transformaciones y los procesos internos que no siempre son visibles.\n\n"

    "No sueles conformarte con conversaciones superficiales. Prefieres los diálogos donde existe honestidad, profundidad y la posibilidad de descubrir algo verdadero sobre ti o sobre la otra persona. Cuando encuentras ese espacio, tu capacidad para comprender resulta extraordinaria.\n\n"

    "El reto aparece cuando la desconfianza hace que guardes demasiado para ti o cuando analizas una situación hasta perder la capacidad de tomar distancia. Aprender a compartir tus descubrimientos con apertura permite que tu profundidad se convierta en una fuente de transformación y no de aislamiento."
),

9: (
    "Tu manera de pensar necesita ampliar horizontes. No te basta con conocer los hechos; buscas comprender el sentido que hay detrás de ellos. Te atraen las grandes preguntas, las diferentes formas de entender la vida y todo aquello que te permite mirar el mundo desde una perspectiva más amplia.\n\n"

    "Tu comunicación suele ser inspiradora y orientada a compartir aquello que has descubierto. Disfrutas intercambiando ideas, enseñando, aprendiendo de otras culturas o explorando nuevos enfoques que amplíen la comprensión de la realidad. Las conversaciones que invitan a reflexionar alimentan especialmente tu mente.\n\n"

    "El reto aparece cuando las grandes ideas te hacen perder de vista la realidad más cercana o cuando das por ciertas algunas conclusiones sin haberlas contrastado suficientemente. Aprender a unir amplitud de visión y sentido práctico convierte tu conocimiento en una verdadera fuente de crecimiento para ti y para quienes te rodean."
),

10: (
    "Tu manera de pensar busca construir algo sólido y dejar una aportación en el mundo. Necesitas comprender cómo funcionan las estructuras, organizar los conocimientos y desarrollar una forma de comunicar que inspire confianza y credibilidad. El aprendizaje suele orientarse hacia objetivos concretos y de largo recorrido.\n\n"

    "Sueles expresarte de manera clara y responsable. Antes de compartir una opinión acostumbras a reflexionar sobre ella, porque te importa que tus palabras tengan peso y sean coherentes con quien eres. Con frecuencia otras personas valoran tu criterio y buscan tu consejo.\n\n"

    "El reto aparece cuando sientes que debes demostrar constantemente cuánto sabes o cuando el miedo a equivocarte termina limitando tu espontaneidad. Descubrir que la autoridad nace de la autenticidad y no de la perfección permite que tu voz encuentre una fuerza mucho más natural."
),

11: (
    "Tu manera de pensar se enriquece al compartir ideas con otras personas. Necesitas intercambiar puntos de vista, participar en proyectos colectivos y abrirte a nuevas formas de comprender el mundo. Tu mente suele orientarse hacia el futuro, imaginando posibilidades y caminos que todavía no existen.\n\n"

    "La comunicación encuentra su mejor expresión cuando puede contribuir al crecimiento de un grupo o generar conexiones entre personas con intereses comunes. Disfrutas aprendiendo de quienes piensan diferente y construyendo conocimiento de forma compartida.\n\n"

    "El reto aparece cuando las ideas permanecen únicamente en el plano teórico o cuando el deseo de innovar hace que pierdas el contacto con las necesidades reales de las personas. Integrar visión de futuro y cercanía humana permite que tus propuestas tengan un impacto mucho más profundo."
),

12: (
    "Tu manera de pensar se mueve con facilidad entre la intuición, la imaginación y el mundo interior. Muchas veces comprendes algo antes de poder explicarlo con palabras, porque tu percepción capta aspectos que no siempre resultan evidentes para la mente racional. Necesitas momentos de silencio para ordenar todo lo que recibes.\n\n"

    "Tu comunicación suele ser sensible y llena de matices. Puedes encontrar palabras para expresar experiencias profundas o acompañar a otras personas desde una escucha muy intuitiva. Con frecuencia percibes lo que no se dice tanto como aquello que se expresa abiertamente.\n\n"

    "El reto aparece cuando absorbes demasiadas influencias externas, dudas de tu propia percepción o te cuesta traducir en palabras lo que intuyes. Aprender a confiar en tu voz interior y darle una forma clara permite que tu sensibilidad se convierta en una herramienta de enorme valor para comprender y acompañar a los demás."
),
}

MERCURIO_COMBINACIONES = {

    "Sol": (
        "Tu manera de pensar y la forma en que construyes tu identidad están estrechamente relacionadas. "
        "Necesitas comprender lo que vives, ponerle palabras y desarrollar ideas que sean coherentes con quien eres.\n\n"

        "Cuando ambas partes colaboran, puedes expresar tus opiniones con claridad y reconocer tu propia voz entre las expectativas o discursos del entorno. "
        "Las palabras se convierten entonces en una forma de afirmar tu presencia y dar sentido a tu experiencia.\n\n"

        "Esta combinación te invita a observar hasta qué punto te identificas con tus pensamientos. "
        "Cambiar de opinión, aprender algo nuevo o reconocer que estabas equivocado no disminuye tu identidad: permite que siga creciendo."
    ),

    "Luna": (
        "Tu manera de pensar y tu mundo emocional mantienen un diálogo constante. "
        "La forma en que interpretas lo que ocurre está influida por lo que sientes, y tus emociones también buscan expresarse a través de las palabras.\n\n"

        "Cuando existe colaboración entre ambas partes, puedes comprender tus estados internos, comunicarte con sensibilidad y encontrar palabras para experiencias que no siempre son fáciles de explicar.\n\n"

        "Esta combinación te invita a distinguir entre lo que estás pensando y lo que estás sintiendo, sin obligarte a elegir entre ambas cosas. "
        "La claridad aparece cuando la mente escucha a la emoción sin quedar completamente absorbida por ella."
    ),

    "Venus": (
        "Tu manera de pensar está conectada con tus valores, tu sensibilidad y tu forma de relacionarte. "
        "Las palabras no son únicamente un vehículo para transmitir información: también crean cercanía, expresan afecto y muestran aquello que consideras importante.\n\n"

        "Cuando ambas partes colaboran, puedes comunicarte con tacto, reconocer diferentes puntos de vista y encontrar una forma de decir la verdad sin perder la consideración hacia quien tienes delante.\n\n"

        "Esta combinación te invita a observar si suavizas demasiado lo que piensas para evitar el desacuerdo o si necesitas la aprobación de otras personas para confiar en tus propias ideas. "
        "La armonía no exige renunciar a tu voz."
    ),

    "Marte": (
        "Tus ideas tienden a movilizar energía. "
        "No acostumbras a quedarte únicamente en el terreno de la reflexión: cuando algo tiene sentido para ti, aparece también el impulso de decirlo, defenderlo o llevarlo a la práctica.\n\n"

        "Cuando ambas partes colaboran, puedes tomar decisiones con rapidez, comunicarte con determinación y utilizar el pensamiento para abrir camino y resolver situaciones.\n\n"

        "Esta combinación te invita a observar la distancia entre pensar, hablar y actuar. "
        "Detenerte un instante antes de responder no apaga tu fuerza: puede ayudarte a dirigirla con mucha más precisión."
    ),

    "Júpiter": (
        "Tu mente busca amplitud, significado y una visión que permita comprender el conjunto. "
        "Las ideas crecen cuando puedes relacionarlas con preguntas importantes, nuevos conocimientos o maneras diferentes de interpretar la vida.\n\n"

        "Cuando ambas partes colaboran, puedes comunicar con entusiasmo, transmitir confianza y ayudar a otras personas a descubrir posibilidades que antes no habían considerado.\n\n"

        "Esta combinación te invita a equilibrar la visión amplia con la atención a los hechos. "
        "Una idea inspiradora gana profundidad cuando también puede contrastarse, concretarse y sostenerse en la realidad."
    ),

    "Saturno": (
        "Tu manera de pensar busca estructura, coherencia y solidez. "
        "Necesitas ordenar las ideas, comprobar lo que sabes y construir conclusiones que puedan mantenerse con el paso del tiempo.\n\n"

        "Cuando ambas partes colaboran, desarrollas concentración, responsabilidad al comunicar y capacidad para profundizar en conocimientos complejos sin abandonar el proceso a mitad de camino.\n\n"

        "Esta combinación te invita a observar la exigencia con la que juzgas tu propia mente. "
        "No necesitas tener todas las respuestas ni expresarte de forma perfecta para que tus palabras tengan valor."
    ),

    "Urano": (
        "Tu mente necesita libertad para cuestionar, investigar y encontrar conexiones poco evidentes. "
        "No te resulta natural aceptar una idea únicamente porque siempre se haya pensado de esa manera.\n\n"

        "Cuando ambas partes colaboran, aparecen originalidad, rapidez para descubrir alternativas y capacidad para introducir nuevas perspectivas en una conversación o en un proyecto.\n\n"

        "Esta combinación te invita a dar una forma comprensible a tus ideas sin renunciar a su singularidad. "
        "La innovación puede llegar más lejos cuando también encuentra un lenguaje capaz de crear puentes con otras personas."
    ),

    "Neptuno": (
        "Tu manera de pensar está conectada con la intuición, la imaginación y la percepción de aquello que no siempre puede explicarse de forma lógica. "
        "A menudo captas primero una impresión, una imagen o una sensación y solo después encuentras las palabras.\n\n"

        "Cuando ambas partes colaboran, puedes comunicar con sensibilidad, comprender matices muy sutiles y expresar experiencias que normalmente resultan difíciles de nombrar.\n\n"

        "Esta combinación te invita a distinguir entre intuición, deseo, temor e información objetiva. "
        "La sensibilidad mental se convierte en un recurso valioso cuando dispone también de espacios para comprobar, ordenar y aclarar lo percibido."
    ),

    "Plutón": (
        "Tu mente busca comprender lo que permanece oculto bajo la superficie. "
        "No te conformas fácilmente con una explicación superficial y puedes sentir una fuerte necesidad de investigar las motivaciones, contradicciones o verdades que no se expresan abiertamente.\n\n"

        "Cuando ambas partes colaboran, desarrollas una enorme capacidad de concentración, profundidad psicológica y una palabra capaz de señalar aspectos esenciales de una situación.\n\n"

        "Esta combinación te invita a observar cuándo la necesidad de comprender se transforma en control, sospecha o pensamiento repetitivo. "
        "No todo necesita resolverse de inmediato para poder ser atravesado con consciencia."
    ),

    "Ascendente": (
        "Cuando Mercurio y el Ascendente trabajan en sintonía, tu manera de pensar y tu forma de presentarte al mundo avanzan en la misma dirección. "
        "Las ideas encuentran una expresión natural y la comunicación se convierte en una extensión auténtica de quién eres.\n\n"

        "Esta combinación invita a desarrollar una forma de comunicar que refleje tu verdadera manera de comprender la vida. "
        "Cuanto mayor es la coherencia entre lo que piensas y lo que expresas, más fácil resulta conectar con los demás desde la autenticidad."
    ),

    "Nodo Norte": (
        "Cuando Mercurio y el Nodo Norte colaboran, el aprendizaje, la comunicación y la capacidad de comprender la realidad se convierten en herramientas esenciales para tu evolución. "
        "Desarrollar una nueva manera de pensar y de interpretar la experiencia forma parte del camino que tu vida te invita a recorrer.\n\n"

        "Esta combinación recuerda que evolucionar también implica cuestionar antiguas certezas. "
        "Cada nueva comprensión abre la puerta a una versión más consciente de quien eres."
    ),

    "Nodo Sur": (
        "Cuando Mercurio y el Nodo Sur se encuentran, tu mente recurre con facilidad a formas de pensar, aprender o comunicar que ya conoces profundamente. "
        "Existe una inteligencia adquirida y una manera natural de interpretar la realidad que puede convertirse en un gran recurso, pero también en una zona de comodidad.\n\n"

        "Esta combinación invita a aprovechar ese conocimiento sin quedar limitado por él. "
        "La experiencia acumulada alcanza todo su valor cuando sirve como base para seguir aprendiendo, en lugar de impedir que aparezcan nuevas perspectivas."
    ),

    "Quirón": (
        "Cuando Mercurio y Quirón interactúan, la forma de pensar, aprender o comunicar puede convertirse en un lugar donde aparecen antiguas heridas, pero también un enorme potencial de comprensión. "
        "Las dificultades vividas alrededor de la palabra, el conocimiento o la expresión pueden transformarse con el tiempo en una fuente de sabiduría y empatía.\n\n"

        "Esta combinación recuerda que aquello que un día resultó doloroso también puede convertirse en el puente que permita acompañar y comprender mejor a otras personas."
    ),

    "Lilith": (
        "Cuando Mercurio y Lilith se encuentran, surge la necesidad de pensar y expresar aquello que no siempre encaja con lo esperado o socialmente aceptado. "
        "La mente busca explorar territorios incómodos, cuestionar discursos establecidos y dar voz a aquello que habitualmente permanece oculto.\n\n"

        "Esta combinación invita a utilizar esa capacidad crítica con consciencia. "
        "La autenticidad encuentra toda su fuerza cuando puede expresar la verdad sin necesidad de convertir cada conversación en un enfrentamiento."
    ),
}


TEXTOS_TIPO_ASPECTO = {

    "Conjunción": (
        "Estas dos partes de ti se encuentran muy unidas y tienden a expresarse de manera simultánea. "
        "En ocasiones puede resultar difícil distinguir dónde termina una y comienza la otra, porque ambas participan en una misma respuesta.\n\n"

        "Esta unión concentra mucha energía y hace que la relación entre ambas tenga una presencia importante en tu forma de vivir. "
        "El aprendizaje consiste en reconocerlas por separado para que puedan colaborar sin que una quede completamente absorbida por la otra."
    ),

    "Sextil": (
        "Entre ambas existe una posibilidad natural de colaboración. "
        "La conexión está disponible, pero suele desarrollarse con mayor claridad cuando la utilizas de forma consciente y le das espacio en la vida cotidiana.\n\n"

        "Cada vez que pones en relación estas dos partes de ti aparecen nuevos recursos. "
        "El aprendizaje consiste en no esperar que esa facilidad se despliegue sola, sino participar activamente en su desarrollo."
    ),

    "Trígono": (
        "Estas dos partes de ti tienden a apoyarse de manera espontánea. "
        "Existe una fluidez natural que facilita que una refuerce a la otra sin generar demasiada fricción interna.\n\n"

        "Precisamente por resultar tan familiar, es posible que no siempre reconozcas todo su valor. "
        "El aprendizaje consiste en hacer consciente esta facilidad y utilizarla como uno de tus recursos internos."
    ),

    "Cuadratura": (
        "Estas dos partes de ti no siempre avanzan en la misma dirección. "
        "En determinados momentos pueden generar tensión, respuestas contradictorias o la sensación de que atender una implica descuidar la otra.\n\n"

        "Esa incomodidad no representa un fallo, sino una fuerza que te impulsa a desarrollar nuevas respuestas. "
        "El aprendizaje consiste en construir una forma propia de integrar ambas necesidades sin intentar eliminar ninguna."
    ),

    "Oposición": (
        "Estas dos partes de ti buscan constantemente un punto de equilibrio. "
        "Es posible que, en diferentes momentos, una tome todo el protagonismo mientras la otra parezca quedar proyectada en las personas o situaciones que encuentras fuera de ti.\n\n"

        "El aprendizaje no consiste en elegir una de las dos, sino en reconocer que ambas forman parte de tu experiencia. "
        "Cuando pueden dialogar, dejan de vivirse como extremos enfrentados y comienzan a complementarse."
    ),

    "Quincuncio": (
        "La relación entre estas dos partes de ti suele requerir ajustes continuos. "
        "No siempre resulta evidente qué tienen que ver entre sí o cómo atenderlas al mismo tiempo, por lo que pueden producir una sensación difícil de identificar.\n\n"

        "El aprendizaje se desarrolla mediante la observación, la adaptación y pequeños cambios sostenidos. "
        "Con el tiempo puedes construir una manera muy personal y precisa de dar espacio a ambas."
    ),
}

MERCURIO_INTEGRACION = {

    "necesidades": {
        "titulo": "Lo que Mercurio necesita",

        "texto": (
            "Cada Mercurio tiene una forma diferente de aprender, comprender y organizar la información, "
            "pero todos comparten una misma necesidad: disponer del espacio suficiente para transformar la experiencia en comprensión.\n\n"

            "Mercurio necesita tiempo para hacer preguntas, revisar ideas, cambiar de opinión cuando descubre algo nuevo y expresar aquello que ocurre en su mundo interno. "
            "Cuando esa posibilidad desaparece, la mente suele intentar compensarlo pensando más, preocupándose más o buscando respuestas inmediatas.\n\n"

            "No todas las conversaciones alimentan a Mercurio. Tampoco toda la información aporta claridad. "
            "Con frecuencia necesita silencio, curiosidad, lectura, escritura o un diálogo tranquilo que permita ordenar lo vivido sin sentirse juzgado.\n\n"

            "Cada vez que respetas el ritmo natural con el que tu mente comprende la realidad, Mercurio deja de luchar por controlar lo que ocurre y recupera su capacidad para aprender, comunicar y construir significado."
        )
    },

    "cuidar": {
        "titulo": "Cómo cuidar tu Mercurio",

        "texto": (
            "Cuidar de Mercurio no significa aprender más ni pensar mejor. "
            "Significa crear las condiciones para que tu mente pueda hacer aquello para lo que está diseñada: comprender.\n\n"

            "Cada vez que dispones de tiempo para reflexionar, mantener conversaciones que te nutren, leer, escribir o simplemente observar sin necesidad de responder de inmediato, Mercurio encuentra un espacio donde recuperar su equilibrio.\n\n"

            "También necesita descanso. Una mente saturada de información, estímulos o exigencias termina perdiendo claridad, incluso cuando posee una gran capacidad intelectual.\n\n"

            "Aprender a distinguir entre información y comprensión es una de las formas más profundas de cuidar esta función. No necesitas saber más para entender mejor. A menudo necesitas detenerte lo suficiente para que todo aquello que ya has vivido encuentre un lugar dentro de ti."
        )
    },

    "equilibrio": {
        "titulo": "Cuando Mercurio encuentra equilibrio",

        "texto": (
            "Cuando Mercurio funciona de manera equilibrada, la mente deja de ser únicamente un lugar donde se acumulan pensamientos para convertirse en una herramienta que ayuda a comprender la realidad.\n\n"

            "Existe curiosidad sin necesidad de saberlo todo, capacidad para escuchar antes de responder y flexibilidad para revisar una idea cuando aparece una nueva comprensión.\n\n"

            "Las palabras encuentran su momento, las conversaciones se convierten en espacios de intercambio y el aprendizaje deja de vivirse como una obligación para transformarse en una forma natural de crecer.\n\n"

            "No significa pensar siempre con claridad ni tener todas las respuestas. Significa confiar en que tu mente puede explorar, ordenar y dar sentido a lo que vives sin quedar atrapada en el ruido."
        )
    },

    "desregulacion": {
        "titulo": "Cuando Mercurio pierde equilibrio",

        "texto": (
            "Cuando Mercurio pierde equilibrio, la mente puede llenarse de ruido.\n\n"

            "En algunas personas aparece un pensamiento que no se detiene y analiza una misma situación una y otra vez. En otras surge la necesidad de responder con rapidez, sin haber terminado de comprender lo que ocurre. También puede manifestarse como dificultad para escuchar, saturación mental, preocupación constante o una sensación de confusión ante un exceso de información.\n\n"

            "No significa que exista un problema en tu forma de pensar. Con frecuencia es la señal de que tu mente está intentando encontrar claridad mientras sostiene más estímulos, incertidumbre o presión de la que puede integrar en ese momento.\n\n"

            "Recuperar el equilibrio no consiste en dejar de pensar, sino en volver a construir una relación más serena con tus propias ideas."
        )
    },

    "pregunta": {
        "titulo": "Una pregunta para observarte",

        "texto": (
            "Mientras leías este capítulo quizá te has reconocido en algunas descripciones y en otras no. "
            "Eso es completamente normal. Ninguna función permanece igual todos los días ni se expresa de la misma manera en todas las etapas de la vida.\n\n"

            "Más allá de la posición de Mercurio en tu carta, la pregunta importante es otra:\n\n"

            "¿Qué necesita hoy tu mente para recuperar claridad?\n\n"

            "A veces será silencio. Otras veces una conversación, un libro, escribir lo que sientes o simplemente darte permiso para no encontrar todavía la respuesta.\n\n"

            "Observar esa necesidad con honestidad es una forma de empezar a construir una relación diferente con tu propia mente."
        )
    },

    "integracion": {
        "titulo": "Integración",

        "texto": (
            "Pensar es mucho más que producir ideas.\n\n"

            "Es la forma en que interpretas lo que ocurre, das significado a tus experiencias y construyes la historia que te cuentas sobre el mundo y sobre ti.\n\n"

            "Conocer tu Mercurio no pretende decirte cómo deberías pensar. Pretende ayudarte a reconocer cómo funciona tu mente cuando encuentra equilibrio, qué necesita para aprender, cómo se comunica y qué situaciones tienden a generar más ruido que claridad.\n\n"

            "Cada conversación, cada pregunta y cada nueva comprensión modifica la manera en que habitas la realidad.\n\n"

            "Porque la forma en que piensas también forma parte de la arquitectura desde la que construyes tu vida."
        )
    }
}


# ─── TEXTOS: VENUS ─────────────────────────────────────────────
VENUS_SIGNO = {

    "Aries": (
        "Con Venus en Aries, el vínculo nace del impulso, la autenticidad y el deseo de sentirse vivo. "
        "Necesitas sentir que las relaciones, los proyectos y aquello que amas conservan movimiento, espontaneidad y la posibilidad de descubrir algo nuevo.\n\n"

        "Disfrutas cuando puedes tomar la iniciativa, expresar con claridad lo que sientes y vivir el afecto sin excesivas vueltas ni estrategias. "
        "La sinceridad suele resultarte más valiosa que la perfección y prefieres una relación donde ambas personas puedan mostrarse tal y como son.\n\n"

        "Cuando Venus encuentra equilibrio en Aries, el deseo impulsa el encuentro sin convertirse en una lucha. "
        "Puedes defender aquello que valoras sin necesidad de imponerte y disfrutar de la independencia sin perder la capacidad de construir un vínculo.\n\n"

        "Esta posición te invita a recordar que el entusiasmo necesita también continuidad. "
        "El amor no solo comienza cuando aparece la chispa; también crece cuando existe espacio para permanecer."
    ),

    "Tauro": (
        "Con Venus en Tauro, el vínculo nace de la estabilidad, la presencia y la capacidad de disfrutar plenamente de lo que la vida ofrece. "
        "Necesitas sentir que aquello que amas puede sostenerse en el tiempo y convertirse en un lugar seguro donde descansar.\n\n"

        "Disfrutas de las experiencias que despiertan los sentidos: una conversación tranquila, una comida compartida, el contacto físico, la naturaleza o cualquier forma de belleza que pueda vivirse sin prisa. "
        "Cuando algo tiene verdadero valor para ti, prefieres cuidarlo con constancia antes que perseguir emociones pasajeras.\n\n"

        "Cuando Venus encuentra equilibrio en Tauro, puedes construir relaciones profundas, fieles y serenas, disfrutando de lo cotidiano sin necesidad de que todo sea extraordinario. "
        "La seguridad deja de depender del control y nace de la confianza en lo que se ha ido construyendo paso a paso.\n\n"

        "Esta posición te invita a recordar que proteger aquello que amas no significa retenerlo. "
        "El verdadero vínculo también necesita espacio para respirar, transformarse y seguir creciendo."
    ),

    "Géminis": (
        "Con Venus en Géminis, el vínculo nace de la curiosidad, la conversación y el intercambio de ideas. "
        "Necesitas sentir que las relaciones permanecen vivas, que existe interés mutuo por descubrir al otro y que siempre hay algo nuevo que compartir.\n\n"

        "Disfrutas aprendiendo, riendo, haciendo preguntas y encontrando personas con las que puedas hablar con libertad. "
        "La conexión intelectual suele convertirse en una puerta de entrada hacia el afecto, porque comprender y sentir que te comprenden alimenta tu manera de vincularte.\n\n"

        "Cuando Venus encuentra equilibrio en Géminis, la comunicación fortalece las relaciones y la variedad no impide el compromiso. "
        "Puedes adaptarte a personas y situaciones diferentes sin perder tu autenticidad ni dispersarte entre demasiadas posibilidades.\n\n"

        "Esta posición te invita a recordar que la intimidad también necesita silencio y profundidad. "
        "No todas las respuestas aparecen hablando; algunas solo llegan cuando permites que la experiencia madure dentro de ti."
    ),

    "Cáncer": (
        "Con Venus en Cáncer, el vínculo nace del cuidado, la confianza y la sensación de pertenecer. "
        "Necesitas sentir que puedes bajar las defensas y compartir aquello que eres sin miedo a que desaparezca esa sensación de acogida.\n\n"

        "Disfrutas creando espacios donde las personas puedan sentirse seguras, protegidas y escuchadas. "
        "Los pequeños gestos, la cercanía cotidiana y los recuerdos compartidos suelen tener para ti un valor mucho mayor que las grandes demostraciones.\n\n"

        "Cuando Venus encuentra equilibrio en Cáncer, puedes cuidar sin olvidarte de ti y recibir el afecto con la misma naturalidad con la que lo ofreces. "
        "El amor deja de convertirse en una responsabilidad para transformarse en un intercambio donde ambas personas pueden sostenerse mutuamente.\n\n"

        "Esta posición te invita a recordar que proteger tu corazón no significa levantar muros a su alrededor. "
        "La verdadera seguridad nace cuando puedes mostrar tu vulnerabilidad sin dejar de sostenerte."
    ),

    "Leo": (
        "Con Venus en Leo, el vínculo nace del reconocimiento, la generosidad y la alegría de compartir lo que eres. "
        "Necesitas sentir que puedes expresarte con autenticidad y que aquello que entregas encuentra una respuesta sincera al otro lado.\n\n"

        "Disfrutas creando momentos especiales, celebrando la vida y mostrando afecto de forma abierta y cálida. "
        "Cuando amas, sueles hacerlo con entusiasmo y con el deseo de que la otra persona también pueda sentirse valiosa y única.\n\n"

        "Cuando Venus encuentra equilibrio en Leo, el brillo personal deja espacio para que también brillen quienes te rodean. "
        "La autoestima se convierte en una fuente de generosidad y no depende constantemente de la aprobación externa.\n\n"

        "Esta posición te invita a recordar que el amor no necesita demostrarse continuamente para seguir existiendo. "
        "A veces los vínculos más profundos también crecen en la sencillez de lo cotidiano."
    ),

    "Virgo": (
        "Con Venus en Virgo, el vínculo nace del cuidado consciente, la atención a los pequeños detalles y el deseo de contribuir al bienestar de quienes amas. "
        "Necesitas sentir que el afecto puede expresarse de forma útil, concreta y coherente con tus valores.\n\n"

        "Disfrutas cuando puedes ayudar, acompañar y construir relaciones donde ambas personas se cuidan mutuamente. "
        "Los gestos cotidianos, la presencia constante y la confianza que se gana poco a poco suelen tener para ti mucho más valor que las grandes promesas.\n\n"

        "Cuando Venus encuentra equilibrio en Virgo, comprendes que el amor no necesita ser perfecto para ser profundo. "
        "Puedes ofrecer lo mejor de ti sin exigirte alcanzar un ideal imposible ni medir constantemente si haces lo suficiente.\n\n"

        "Esta posición te invita a recordar que también mereces recibir el mismo cuidado que ofreces a los demás. "
        "El vínculo se fortalece cuando el amor deja de ser una responsabilidad para convertirse en un intercambio."
    ),

    "Libra": (
        "Con Venus en Libra, el vínculo nace del encuentro, la cooperación y el deseo de construir relaciones equilibradas. "
        "Necesitas sentir que existe reciprocidad, respeto y una disposición mutua para comprenderse y crecer juntos.\n\n"

        "Disfrutas de la belleza compartida, de las conversaciones donde ambas personas pueden expresarse y de los espacios donde la armonía facilita el acercamiento. "
        "Para ti, el vínculo florece cuando nadie necesita imponerse para sentir que cuenta dentro de la relación.\n\n"

        "Cuando Venus encuentra equilibrio en Libra, puedes escuchar sin perder tu propia voz y buscar acuerdos sin renunciar a aquello que verdaderamente tiene valor para ti. "
        "La armonía deja de depender de evitar el conflicto y nace de la honestidad con la que ambas personas sostienen la relación.\n\n"

        "Esta posición te invita a recordar que cuidar un vínculo también implica atreverte a expresar el desacuerdo cuando es necesario. "
        "La verdadera paz no nace del silencio, sino de la autenticidad."
    ),

    "Escorpio": (
        "Con Venus en Escorpio, el vínculo nace de la profundidad, la entrega y el deseo de conocer aquello que permanece oculto bajo la superficie. "
        "Necesitas sentir que las relaciones tienen verdad, intensidad y la capacidad de transformarte.\n\n"

        "Disfrutas cuando puedes compartir aquello que normalmente permanece protegido y descubrir que la otra persona también se atreve a mostrarse sin máscaras. "
        "La confianza, para ti, no aparece de inmediato: se construye cuando el vínculo demuestra que puede sostener tanto la luz como la sombra.\n\n"

        "Cuando Venus encuentra equilibrio en Escorpio, la intensidad deja de convertirse en control y se transforma en una enorme capacidad para crear intimidad, compromiso y lealtad. "
        "Puedes abrir el corazón sin sentir que para hacerlo debes perder poder o protección.\n\n"

        "Esta posición te invita a recordar que amar no significa poseer. "
        "Los vínculos más profundos no nacen del control, sino de la confianza que permite a cada persona seguir siendo libre."
    ),

    "Sagitario": (
        "Con Venus en Sagitario, el vínculo nace de la libertad, el crecimiento y el deseo de compartir experiencias que amplían la mirada sobre la vida. "
        "Necesitas sentir que las relaciones inspiran, abren caminos y dejan espacio para seguir descubriendo el mundo y quien eres.\n\n"

        "Disfrutas aprendiendo junto a otras personas, viajando, explorando nuevas ideas o simplemente compartiendo conversaciones que despiertan curiosidad y entusiasmo. "
        "Para ti, el amor crece cuando ambos pueden seguir evolucionando sin dejar de caminar en la misma dirección.\n\n"

        "Cuando Venus encuentra equilibrio en Sagitario, la libertad deja de vivirse como distancia y se convierte en confianza mutua. "
        "Puedes comprometerte sin sentir que renuncias a tu expansión personal.\n\n"

        "Esta posición te invita a recordar que la aventura también puede encontrarse en la profundidad de un vínculo que continúa creciendo con el paso del tiempo."
    ),

    "Capricornio": (
        "Con Venus en Capricornio, el vínculo nace del compromiso, la confianza y la construcción paciente de aquello que realmente tiene valor. "
        "Necesitas sentir que las relaciones tienen una base sólida, que las palabras se sostienen con hechos y que el tiempo fortalece aquello que se comparte.\n\n"

        "Disfrutas construyendo proyectos en común, cuidando de quienes forman parte de tu vida y demostrando afecto a través de la constancia más que de las grandes declaraciones. "
        "Para ti, el amor crece cuando existe responsabilidad mutua y ambas personas pueden apoyarse en los momentos importantes.\n\n"

        "Cuando Venus encuentra equilibrio en Capricornio, descubres que la fortaleza no está reñida con la ternura. "
        "Puedes abrirte emocionalmente sin sentir que eso pone en riesgo tu estabilidad ni tu capacidad para sostenerte.\n\n"

        "Esta posición te invita a recordar que el afecto también necesita espontaneidad. "
        "No todo lo valioso se construye únicamente con esfuerzo; algunas de las experiencias más profundas nacen cuando permites que el corazón descanse y disfrute del camino."
    ),

    "Acuario": (
        "Con Venus en Acuario, el vínculo nace de la libertad, la autenticidad y el respeto por la individualidad de cada persona. "
        "Necesitas sentir que puedes relacionarte sin dejar de ser quien eres y que el afecto no exige renunciar a tu propia esencia.\n\n"

        "Disfrutas compartiendo ideas, proyectos e inquietudes con personas que despiertan tu curiosidad y amplían tu forma de ver la vida. "
        "La amistad, la complicidad y la admiración mutua suelen convertirse en pilares fundamentales de tus relaciones.\n\n"

        "Cuando Venus encuentra equilibrio en Acuario, puedes combinar independencia y cercanía sin vivirlas como fuerzas opuestas. "
        "El vínculo deja espacio para que ambas personas evolucionen y, precisamente por ello, se fortalece.\n\n"

        "Esta posición te invita a recordar que abrir el corazón no limita tu libertad. "
        "La verdadera independencia también incluye la capacidad de dejarte cuidar y permitir que otras personas ocupen un lugar importante en tu vida."
    ),

    "Piscis": (
        "Con Venus en Piscis, el vínculo nace de la sensibilidad, la compasión y la capacidad de percibir aquello que muchas veces permanece invisible para los demás. "
        "Necesitas sentir que las relaciones pueden convertirse en un espacio de comprensión profunda, donde el afecto trasciende las palabras y se expresa también a través de la presencia.\n\n"

        "Disfrutas conectando con la belleza, el arte, la imaginación y todas aquellas experiencias que despiertan la emoción y el sentido de unidad. "
        "Cuando amas, tiendes a hacerlo con una gran apertura de corazón y con el deseo de aliviar el sufrimiento o acompañar el crecimiento de quienes quieres.\n\n"

        "Cuando Venus encuentra equilibrio en Piscis, la sensibilidad se convierte en una fuente de empatía sin perder el contacto contigo. "
        "Puedes entregarte sin confundirte con la otra persona y amar sin necesidad de olvidarte de tus propios límites.\n\n"

        "Esta posición te invita a recordar que el amor más profundo no nace del sacrificio, sino de una presencia consciente que sabe cuidar a quien tienes delante sin dejar de cuidar también tus propias necesidades."
    )
}

VENUS_CASA = {

    1: (
        "Con Venus en la casa 1, el vínculo comienza por la relación que construyes contigo. "
        "La manera en que te presentas al mundo, cuidas tu imagen y expresas tu sensibilidad influye directamente en la forma en que otras personas se acercan a ti.\n\n"

        "Necesitas sentir que puedes relacionarte sin ocultar quién eres. Cuando existe autenticidad, el afecto fluye con mayor naturalidad y las relaciones dejan de convertirse en un esfuerzo por agradar.\n\n"

        "Esta posición te invita a reconocer que tu forma de estar presente también es una forma de amar. Cuanto más habitas tu propia esencia, más fáciles resultan los vínculos que nacen desde ella."
    ),

    2: (
        "Con Venus en la casa 2, el vínculo se construye a través de aquello que aporta estabilidad, bienestar y sensación de valor. "
        "Necesitas sentir que lo que amas puede sostenerse en la realidad y formar parte de una vida que resulte segura y coherente contigo.\n\n"

        "Disfrutas cuidando aquello que consideras importante, ya sean personas, proyectos, recursos o talentos. La belleza suele aparecer cuando puedes vivir con calma, rodearte de lo que aprecias y reconocer tu propio valor.\n\n"

        "Esta posición te invita a recordar que tu valor no depende únicamente de lo que posees o produces. El merecimiento nace primero dentro de ti y, desde ahí, transforma la manera en que te relacionas con el mundo."
    ),

    3: (
        "Con Venus en la casa 3, el vínculo nace de la conversación, el aprendizaje compartido y el placer de descubrir nuevas formas de comprender la vida junto a otras personas. "
        "Necesitas sentir que existe intercambio, curiosidad y cercanía en la comunicación.\n\n"

        "Disfrutas hablando, escuchando, leyendo, escribiendo o compartiendo ideas que enriquecen la relación. Con frecuencia el afecto aparece primero a través de la palabra y encuentra en ella una forma natural de crecer.\n\n"

        "Esta posición te invita a recordar que comunicar también implica escuchar. Los vínculos se fortalecen cuando las palabras no solo expresan lo que piensas, sino que también dejan espacio para comprender al otro."
    ),

    4: (
        "Con Venus en la casa 4, el vínculo busca convertirse en un hogar. "
        "Necesitas sentir que existe un lugar donde puedas descansar emocionalmente, bajar las defensas y compartir tu mundo más íntimo con seguridad.\n\n"

        "Disfrutas creando espacios acogedores, cuidando de quienes forman parte de tu vida y construyendo relaciones donde la confianza crece con el paso del tiempo. El afecto suele expresarse a través de la cercanía cotidiana y la sensación de pertenencia.\n\n"

        "Esta posición te invita a recordar que un hogar no se construye únicamente cuidando de los demás. También necesita incluirte a ti, tus necesidades y la posibilidad de sentir que también puedes recibir apoyo sin tener que hacerlo todo por tu cuenta."
    ),

    5: (
        "Con Venus en la casa 5, el vínculo nace del disfrute, la creatividad y la alegría de compartir aquello que hace que te sientas vivo. "
        "Necesitas sentir que el amor puede expresarse con espontaneidad, juego y entusiasmo, sin perder su autenticidad.\n\n"

        "Disfrutas creando, celebrando, seduciendo, riendo y compartiendo experiencias que despiertan ilusión. La belleza aparece cuando puedes mostrar tu parte más creativa y sentir que es recibida con naturalidad.\n\n"

        "Esta posición te invita a recordar que el amor no necesita vivirse como una representación constante. También crece en la sencillez, cuando puedes dejar de impresionar y simplemente disfrutar de la presencia compartida."
    ),

    6: (
        "Con Venus en la casa 6, el vínculo se construye a través del cuidado cotidiano, la presencia constante y los pequeños gestos que sostienen una relación con el paso del tiempo. "
        "Necesitas sentir que el afecto también se expresa en aquello que se hace cada día.\n\n"

        "Disfrutas ayudando, acompañando y creando rutinas que aportan bienestar tanto a ti como a quienes forman parte de tu vida. Para ti, el amor suele manifestarse más en los hechos que en las palabras.\n\n"

        "Esta posición te invita a recordar que cuidar no significa asumir toda la responsabilidad del vínculo. También necesitas permitir que otras personas puedan cuidarte y sostenerte cuando lo necesites."
    ),

    7: (
        "Con Venus en la casa 7, el vínculo ocupa un lugar central en tu forma de crecer y comprenderte. "
        "Necesitas sentir que las relaciones se construyen desde el respeto, la reciprocidad y el deseo de caminar junto a otra persona sin dejar de ser quien eres.\n\n"

        "Disfrutas compartiendo decisiones, construyendo acuerdos y aprendiendo a través del encuentro con quienes piensan, sienten o viven de una manera diferente a la tuya. Las relaciones suelen convertirse en uno de tus principales espacios de aprendizaje.\n\n"

        "Esta posición te invita a recordar que un vínculo sano no exige desaparecer dentro del otro. Cuanto más sólida es la relación contigo, más libre y auténtico puede ser el encuentro con los demás."
    ),

    8: (
        "Con Venus en la casa 8, el vínculo busca profundidad, transformación y una intimidad que vaya mucho más allá de lo superficial. "
        "Necesitas sentir que las relaciones tienen la capacidad de tocar aquello que normalmente permanece protegido.\n\n"

        "Disfrutas cuando existe confianza suficiente para compartir miedos, deseos, heridas y procesos de cambio sin necesidad de ocultarlos. Para ti, el amor suele convertirse en una experiencia que transforma a quienes la viven.\n\n"

        "Esta posición te invita a recordar que la verdadera intimidad no nace del control ni de la intensidad constante. Surge cuando ambas personas pueden mostrarse vulnerables sin dejar de sentirse libres y seguras."
    ),

    9: (
        "Con Venus en la casa 9, el vínculo nace del crecimiento, la inspiración y el deseo de descubrir juntos nuevos horizontes. "
        "Necesitas sentir que las relaciones amplían tu manera de comprender la vida y alimentan tu curiosidad por seguir aprendiendo.\n\n"

        "Disfrutas compartiendo viajes, estudios, experiencias o conversaciones que invitan a mirar más allá de lo conocido. Para ti, el amor florece cuando ambas personas pueden evolucionar sin limitar el camino de la otra.\n\n"

        "Esta posición te invita a recordar que la verdadera expansión también sucede en la profundidad. No siempre es necesario buscar nuevos horizontes; a veces el mayor viaje consiste en seguir descubriendo a la misma persona con el paso del tiempo."
    ),

    10: (
        "Con Venus en la casa 10, el vínculo busca construir algo que deje huella en el mundo. "
        "Necesitas sentir que aquello que amas puede integrarse en tu propósito, en tus responsabilidades y en la dirección que deseas dar a tu vida.\n\n"

        "Disfrutas desarrollando proyectos sólidos, colaborando con personas que admiras y creando relaciones basadas en el respeto mutuo y la confianza. El reconocimiento suele tener valor para ti cuando nace como consecuencia natural de hacer las cosas con coherencia.\n\n"

        "Esta posición te invita a recordar que el éxito pierde parte de su sentido cuando no puede compartirse. Tu vida pública y tus vínculos no tienen por qué competir; pueden convertirse en pilares que se fortalecen mutuamente."
    ),

    11: (
        "Con Venus en la casa 11, el vínculo nace de la amistad, los ideales compartidos y el deseo de formar parte de algo que trasciende el interés individual. "
        "Necesitas sentir que las relaciones respetan la libertad de cada persona y, al mismo tiempo, contribuyen a construir un futuro compartido.\n\n"

        "Disfrutas colaborando, participando en proyectos colectivos y rodeándote de personas con las que puedas intercambiar ideas, sueños e inquietudes. La afinidad intelectual y los valores comunes suelen convertirse en una base importante para el afecto.\n\n"

        "Esta posición te invita a recordar que la cercanía emocional también necesita espacio dentro de los grupos y las amistades. La conexión más profunda aparece cuando permites que algunas personas crucen la puerta de tu mundo más personal."
    ),

    12: (
        "Con Venus en la casa 12, el vínculo nace de la compasión, la sensibilidad y la capacidad de conectar con aquello que no siempre puede explicarse con palabras. "
        "Necesitas sentir que el amor incluye aceptación, silencio y una profunda comprensión de la dimensión más íntima del ser humano.\n\n"

        "Disfrutas encontrando belleza en lo sencillo, acompañando procesos de transformación y conectando con experiencias que despiertan la inspiración, la espiritualidad o la creatividad. Con frecuencia percibes matices emocionales que otras personas pasan por alto.\n\n"

        "Esta posición te invita a recordar que la entrega no implica desaparecer dentro del otro. El amor más profundo surge cuando puedes ofrecer tu sensibilidad sin renunciar a tus propios límites, necesidades e identidad."
    )
}

VENUS_COMBINACIONES = {

    "Sol": (
        "Cuando Venus y el Sol trabajan en sintonía, aquello que valoras se convierte en una expresión natural de quién eres. "
        "Tu identidad encuentra coherencia con tus afectos, tus decisiones y la manera en que eliges relacionarte con el mundo.\n\n"

        "Esta combinación invita a construir una vida donde no exista separación entre lo que eres y lo que amas. "
        "Cuanto mayor es esa coherencia, más sencilla resulta la sensación de plenitud."
    ),

    "Luna": (
        "Cuando Venus y la Luna colaboran, el mundo emocional y la forma de vincularte se alimentan mutuamente. "
        "El afecto se convierte en un lugar donde puedes sentirte acogido, comprender tus necesidades y ofrecer cuidado sin perderte en el proceso.\n\n"

        "Esta combinación recuerda que amar también implica permitirte recibir. "
        "El vínculo se fortalece cuando existe un equilibrio entre cuidar y dejarte cuidar."
    ),

    "Mercurio": (
        "Cuando Venus y Mercurio encuentran un lenguaje común, las relaciones se enriquecen gracias a la comunicación, la escucha y el intercambio de ideas. "
        "Comprender y expresar aquello que valoras fortalece la confianza y acerca a las personas.\n\n"

        "Esta combinación invita a recordar que las palabras construyen vínculos cuando nacen de la autenticidad y del deseo sincero de comprender al otro."
    ),

    "Marte": (
        "Cuando Venus y Marte colaboran, el deseo y el afecto avanzan en la misma dirección. "
        "Puedes actuar para proteger aquello que amas, expresar tus sentimientos con claridad y transformar la atracción en acciones coherentes.\n\n"

        "Esta combinación recuerda que la verdadera fuerza no consiste en conquistar, sino en sostener con decisión aquello que realmente tiene valor para ti."
    ),

    "Júpiter": (
        "Cuando Venus y Júpiter se potencian mutuamente, el amor, la generosidad y la confianza encuentran espacio para crecer. "
        "Los vínculos se convierten en una oportunidad para compartir, aprender y ampliar la mirada sobre la vida.\n\n"

        "Esta combinación invita a disfrutar de la abundancia sin olvidar que el verdadero crecimiento también necesita presencia, gratitud y equilibrio."
    ),

    "Saturno": (
        "Cuando Venus y Saturno trabajan juntos, el vínculo se fortalece a través del compromiso, la constancia y la capacidad de construir relaciones que puedan sostenerse en el tiempo. "
        "El afecto encuentra profundidad cuando existe responsabilidad mutua y disposición para cuidar aquello que realmente importa.\n\n"

        "Esta combinación invita a comprender que la estabilidad no nace únicamente del esfuerzo. "
        "También necesita confianza, ternura y la capacidad de disfrutar del camino que se construye junto a otras personas."
    ),

    "Urano": (
        "Cuando Venus y Urano colaboran, el amor encuentra nuevas formas de expresarse sin perder autenticidad. "
        "Las relaciones se convierten en un espacio donde la libertad, la creatividad y el respeto por la individualidad permiten que ambas personas sigan evolucionando.\n\n"

        "Esta combinación recuerda que un vínculo puede ser estable sin dejar de transformarse. "
        "La innovación también puede formar parte del compromiso cuando existe respeto por la individualidad de ambas personas."
    ),

    "Neptuno": (
        "Cuando Venus y Neptuno se encuentran, el afecto se abre a la sensibilidad, la inspiración y la capacidad de percibir la belleza que existe más allá de lo evidente. "
        "Las relaciones pueden convertirse en una fuente de compasión, creatividad y profunda conexión emocional.\n\n"

        "Esta combinación invita a mantener el corazón abierto sin perder el contacto con la realidad. "
        "La sensibilidad alcanza toda su fuerza cuando puede convivir con unos límites claros y conscientes."
    ),

    "Plutón": (
        "Cuando Venus y Plutón trabajan en sintonía, el amor se convierte en una fuerza capaz de transformar profundamente tu manera de relacionarte contigo y con otras personas. "
        "Los vínculos ponen de manifiesto aquello que necesita sanar, soltar o renacer para construir relaciones más auténticas.\n\n"

        "Esta combinación recuerda que la verdadera profundidad no nace del control ni de la intensidad permanente. "
        "Surge cuando existe la confianza suficiente para transformarse sin perder la libertad de seguir siendo fiel a quien eres."
    ),

    "Ascendente": (
        "Cuando Venus y el Ascendente trabajan en sintonía, la forma en que te muestras al mundo refleja con naturalidad aquello que valoras y la manera en que te relacionas. "
        "La calidez, la belleza y el afecto encuentran una expresión auténtica en tu presencia, facilitando vínculos que nacen desde la coherencia.\n\n"

        "Esta combinación invita a recordar que no necesitas construir una imagen para reconocer tu propio valor. "
        "Cuanto más te permites mostrar quién eres, más fácil resulta que las relaciones conecten con tu verdadera esencia."
    ),

    "Nodo Norte": (
        "Cuando Venus y el Nodo Norte colaboran, las relaciones, los valores y la capacidad de disfrutar forman parte de tu camino de evolución. "
        "Aprender a amar de una manera más consciente, reconocer tu propio valor y elegir vínculos coherentes con quien estás llegando a ser constituye una parte importante de tu desarrollo.\n\n"

        "Esta combinación recuerda que cada relación significativa puede convertirse en una oportunidad para crecer. "
        "La manera de amar evoluciona cuando te atreves a elegir aquello que realmente te nutre."
    ),

    "Nodo Sur": (
        "Cuando Venus y el Nodo Sur se encuentran, existe una forma de amar, vincularte o valorar la vida que resulta profundamente familiar. "
        "Hay talentos afectivos y una manera natural de crear relaciones que forman parte de tu experiencia, aunque en ocasiones también pueden llevarte a repetir dinámicas conocidas por simple inercia.\n\n"

        "Esta combinación invita a conservar la riqueza de lo ya aprendido sin seguir repitiendo antiguos patrones. "
        "El pasado puede ofrecer estabilidad, siempre que no limite la posibilidad de construir nuevas formas de amar."
    ),

    "Quirón": (
        "Cuando Venus y Quirón interactúan, el amor, el merecimiento o la capacidad de recibir afecto pueden despertar antiguas heridas que piden ser reconocidas e integradas. "
        "Precisamente esas experiencias pueden convertirse con el tiempo en una fuente de profunda sensibilidad, comprensión y humanidad.\n\n"

        "Esta combinación recuerda que sanar no significa dejar de sentir. "
        "Significa descubrir que el corazón puede volver a abrirse sin necesidad de protegerse constantemente del dolor."
    ),

    "Lilith": (
        "Cuando Venus y Lilith se encuentran, el deseo de pertenecer convive con una profunda necesidad de vivir los vínculos desde la autenticidad. "
        "Puede aparecer una tensión entre adaptarte a lo que se espera de ti y expresar aquello que realmente deseas, valoras o necesitas.\n\n"

        "Esta combinación invita a construir relaciones donde no sea necesario renunciar a una parte de ti para sentir que mereces amor. "
        "El amor encuentra toda su fuerza cuando nace de la libertad de mostrarte tal como eres, sin ocultar ninguna parte de ti, incluso en aquello que resulta menos convencional."
    ),
}


VENUS_INTEGRACION = {

    "necesidades": {
        "titulo": "Lo que Venus necesita",
        "texto": (
            "Venus necesita sentir que existe espacio para disfrutar, crear vínculos auténticos y reconocer aquello que realmente tiene valor para ti. "
            "No se alimenta únicamente del amor romántico, sino también de la belleza, el placer, la armonía y todas aquellas experiencias que hacen que la vida merezca ser vivida.\n\n"

            "Cuando Venus encuentra ese alimento, las relaciones dejan de convertirse en una búsqueda constante de validación y pasan a ser una expresión natural de una vida que ya posee riqueza por sí misma."
        )
    },

    "cuidar": {
        "titulo": "Cómo cuidar tu Venus",
        "texto": (
            "Cuidar esta función implica reservar espacio para aquello que nutre tu corazón. "
            "Disfrutar sin culpa, cultivar relaciones donde exista reciprocidad, rodearte de belleza y aprender a recibir con la misma naturalidad con la que das forman parte de ese cuidado.\n\n"

            "Venus florece cuando el afecto deja de vivirse como una obligación y se convierte en una experiencia consciente de presencia y disfrute."
        )
    },

    "equilibrio": {
        "titulo": "Cuando Venus está en equilibrio",
        "texto": (
            "Cuando Venus funciona de forma equilibrada, puedes construir relaciones donde existe cercanía sin dependencia, compromiso sin pérdida de libertad y disfrute sin necesidad de exceso. "
            "Reconoces tu propio valor y, desde ahí, eliges aquello que verdaderamente merece un lugar en tu vida.\n\n"

            "El amor deja de ser una necesidad que intenta llenar un vacío y se convierte en una forma de compartir la plenitud que ya habita en ti."
        )
    },

    "desregulacion": {
        "titulo": "Cuando Venus pierde el equilibrio",
        "texto": (
            "Cuando esta función se desregula, puede aparecer la necesidad de buscar fuera el reconocimiento, el afecto o la sensación de valor que resulta difícil sostener desde dentro. "
            "También pueden surgir relaciones desequilibradas, dificultades para poner límites o una tendencia a confundir amor con sacrificio, dependencia o control.\n\n"

            "En otras ocasiones ocurre lo contrario: el corazón se protege tanto que acaba alejándose precisamente de aquello que más necesita."
        )
    },

    "pregunta": {
        "titulo": "Una pregunta para observarte",
        "texto": (
            "¿Aquello que hoy llamas amor, también te permite ser plenamente tú?"
        )
    },

    "integracion": {
        "titulo": "Integrar Venus",
        "texto": (
            "Integrar Venus no consiste en aprender a gustar más a los demás. "
            "Consiste en reconocer qué tiene verdadero valor para ti y construir una vida donde el amor, la belleza y el disfrute dejen de depender de las circunstancias externas.\n\n"

            "Cuando Venus ocupa su lugar, el corazón deja de pedir permiso para abrirse. Reconoce aquello que tiene verdadero valor y decide cuidarlo."
        )
    }

}


# ─── TEXTOS: MARTE ─────────────────────────────────────────────
MARTE_SIGNO = {

    "Aries": (
        "Con Marte en Aries, la acción nace del impulso, la iniciativa y la necesidad de avanzar sin esperar a que las circunstancias sean perfectas. "
        "Necesitas sentir que puedes decidir, actuar y abrir caminos desde tu propia iniciativa.\n\n"

        "Tu energía suele activarse rápidamente cuando aparece un reto o una oportunidad. Disfrutas iniciando proyectos, resolviendo situaciones con rapidez y enfrentándote a aquello que requiere valentía. La acción directa suele resultarte más natural que la espera prolongada.\n\n"

        "Cuando Marte encuentra equilibrio en Aries, la fuerza deja de convertirse en precipitación y se transforma en liderazgo. Puedes actuar con decisión sin necesidad de competir constantemente ni responder desde la impulsividad.\n\n"

        "Esta posición te invita a recordar que la verdadera fortaleza no consiste únicamente en empezar. También implica sostener aquello que has decidido construir."
    ),

    "Tauro": (
        "Con Marte en Tauro, la acción nace de la constancia, la paciencia y la capacidad de avanzar con paso firme hacia aquello que consideras importante. "
        "Necesitas sentir que tus esfuerzos construyen algo sólido y que la energía invertida tiene un propósito claro.\n\n"

        "No sueles actuar por impulso. Prefieres observar, valorar la situación y comprometerte cuando sabes que merece la pena. Una vez tomas una decisión, tu perseverancia suele convertirse en una de tus mayores fortalezas.\n\n"

        "Cuando Marte encuentra equilibrio en Tauro, la estabilidad deja de convertirse en resistencia al cambio y se transforma en una enorme capacidad para sostener procesos largos sin perder el rumbo.\n\n"

        "Esta posición te invita a recordar que la seguridad también puede encontrarse en el movimiento. A veces avanzar requiere soltar aquello que ya ha cumplido su función."
    ),

    "Géminis": (
        "Con Marte en Géminis, la acción nace de la curiosidad, el intercambio de ideas y la necesidad de comprender antes de actuar. "
        "Necesitas sentir que puedes explorar diferentes posibilidades y adaptarte a los cambios con agilidad.\n\n"

        "Tu energía suele expresarse a través de la palabra, el aprendizaje, la comunicación y la capacidad de conectar conceptos. Disfrutas resolviendo problemas, improvisando soluciones y manteniendo la mente en movimiento.\n\n"

        "Cuando Marte encuentra equilibrio en Géminis, la versatilidad deja de convertirse en dispersión y se transforma en una gran capacidad para responder con inteligencia y creatividad a cada situación.\n\n"

        "Esta posición te invita a recordar que no todas las decisiones necesitan mantenerse abiertas indefinidamente. También llega un momento en el que pensar debe dar paso a actuar."
    ),

    "Cáncer": (
        "Con Marte en Cáncer, la acción nace de la necesidad de proteger, cuidar y defender aquello que tiene un profundo valor emocional para ti. "
        "Necesitas sentir que tus esfuerzos contribuyen a crear seguridad, pertenencia y bienestar para las personas que amas.\n\n"

        "Tu energía suele activarse cuando percibes que alguien necesita apoyo o cuando algo importante para ti requiere ser protegido. Actúas con más fuerza cuando existe una implicación emocional que da sentido a lo que haces.\n\n"

        "Cuando Marte encuentra equilibrio en Cáncer, la sensibilidad deja de frenar la acción y se convierte en una poderosa fuente de compromiso y fortaleza interior. Puedes defender tus necesidades sin sentir que por ello dejas de cuidar a los demás.\n\n"

        "Esta posición te invita a recordar que proteger también incluye poner límites. Cuidar no significa asumir todas las cargas ni olvidar tus propias necesidades."
    ),

    "Leo": (
        "Con Marte en Leo, la acción nace del deseo de expresar tu potencial, crear, liderar e inspirar a través de aquello que haces. "
        "Necesitas sentir que tus esfuerzos tienen un significado y que puedes dejar una huella personal en aquello que construyes.\n\n"

        "Tu energía suele activarse cuando existe un reto que despierta tu entusiasmo o una oportunidad para mostrar tus capacidades. Disfrutas tomando la iniciativa, motivando a otras personas y afrontando los desafíos con confianza y determinación.\n\n"

        "Cuando Marte encuentra equilibrio en Leo, la fuerza deja de buscar reconocimiento constante y se convierte en una expresión natural de tu identidad. Lideras desde el ejemplo, impulsando a los demás sin necesidad de competir por ocupar el centro.\n\n"

        "Esta posición te invita a recordar que la verdadera autoridad no necesita demostrarse continuamente. La confianza más sólida nace cuando actúas con autenticidad, incluso cuando nadie está mirando."
    ),

    "Virgo": (
        "Con Marte en Virgo, la acción nace del deseo de mejorar, ordenar y hacer que las cosas funcionen de la mejor manera posible. "
        "Necesitas sentir que tu energía contribuye a resolver problemas y aporta un beneficio concreto tanto para ti como para quienes te rodean.\n\n"

        "Tu impulso suele expresarse a través del trabajo bien hecho, la planificación y la atención a los detalles. Disfrutas perfeccionando procesos, encontrando soluciones prácticas y avanzando paso a paso hacia un objetivo claro.\n\n"

        "Cuando Marte encuentra equilibrio en Virgo, la exigencia deja de convertirse en bloqueo y se transforma en excelencia. Puedes actuar con precisión sin que la necesidad de que todo sea perfecto antes de empezar termine bloqueándote.\n\n"

        "Esta posición te invita a recordar que la acción imperfecta suele transformar más la realidad que la perfección que nunca llega a ponerse en marcha."
    ),

    "Libra": (
        "Con Marte en Libra, la acción nace del deseo de cooperar, encontrar acuerdos y construir soluciones donde todas las partes puedan sentirse escuchadas. "
        "Necesitas sentir que avanzar no implica necesariamente enfrentarte a los demás, sino aprender a caminar junto a ellos.\n\n"

        "Tu energía suele dirigirse hacia la negociación, la colaboración y la búsqueda de equilibrio. Antes de actuar, acostumbras a valorar distintas perspectivas para encontrar el camino más armonioso posible.\n\n"

        "Cuando Marte encuentra equilibrio en Libra, la capacidad de dialogar deja de convertirse en indecisión y se transforma en una forma inteligente de construir consensos sin renunciar a tus propias necesidades.\n\n"

        "Esta posición te invita a recordar que actuar también implica tomar partido. Buscar el equilibrio no significa posponer indefinidamente las decisiones importantes."
    ),

    "Escorpio": (
        "Con Marte en Escorpio, la acción nace de una profunda intensidad interior y del deseo de transformar aquello que consideras esencial. "
        "Necesitas sentir que tu energía tiene un propósito claro y que aquello por lo que luchas merece realmente el esfuerzo que exige.\n\n"

        "Tu fuerza suele manifestarse con perseverancia, estrategia y una gran capacidad para sostener procesos complejos. Cuando decides avanzar, rara vez abandonas el camino antes de haber llegado al fondo de la cuestión.\n\n"

        "Cuando Marte encuentra equilibrio en Escorpio, la intensidad deja de convertirse en lucha constante y se transforma en una enorme capacidad de regeneración. Puedes afrontar las crisis como oportunidades para reconstruir desde una base más auténtica.\n\n"

        "Esta posición te invita a recordar que no todas las batallas necesitan librarse. A veces la mayor muestra de fortaleza consiste en elegir cuidadosamente dónde merece la pena invertir tu energía."
    ),

    "Sagitario": (
        "Con Marte en Sagitario, la acción nace del deseo de crecer, explorar y avanzar hacia nuevos horizontes. "
        "Necesitas sentir que cada paso amplía tu comprensión de la vida y te acerca a una versión más libre y consciente de quien eres.\n\n"

        "Tu energía suele activarse cuando aparece un reto que despierta tu entusiasmo, una oportunidad para aprender o un camino que todavía no ha sido recorrido. Disfrutas emprendiendo proyectos, asumiendo desafíos y transmitiendo confianza a quienes te acompañan.\n\n"

        "Cuando Marte encuentra equilibrio en Sagitario, el impulso deja de convertirse en dispersión y se transforma en una fuerza capaz de sostener una dirección con convicción. La libertad ya no consiste en cambiar constantemente de rumbo, sino en elegir con claridad hacia dónde quieres avanzar.\n\n"

        "Esta posición te invita a recordar que los grandes horizontes también se alcanzan dando un paso cada día. La inspiración necesita encontrar una forma concreta de convertirse en acción."
    ),

    "Capricornio": (
        "Con Marte en Capricornio, la acción nace de la disciplina, la responsabilidad y la capacidad de construir objetivos que puedan sostenerse en el tiempo. "
        "Necesitas sentir que cada esfuerzo tiene un propósito y que tus decisiones contribuyen a levantar una estructura sólida para el futuro.\n\n"

        "Tu energía suele expresarse con serenidad, constancia y una notable capacidad para mantener el rumbo incluso cuando el camino exige paciencia. Prefieres avanzar paso a paso antes que depender únicamente del impulso del momento.\n\n"

        "Cuando Marte encuentra equilibrio en Capricornio, la exigencia deja de convertirse en rigidez y se transforma en una enorme capacidad para materializar proyectos importantes sin perder el contacto con tus necesidades personales.\n\n"

        "Esta posición te invita a recordar que la eficacia no está reñida con el descanso. También recuperas fuerza cuando permites que el esfuerzo conviva con el disfrute."
    ),

    "Acuario": (
        "Con Marte en Acuario, la acción nace del deseo de innovar, cuestionar lo establecido y abrir nuevas posibilidades para el futuro. "
        "Necesitas sentir que tu energía contribuye a generar cambios que beneficien no solo a ti, sino también al conjunto de las personas que te rodean.\n\n"

        "Tu impulso suele dirigirse hacia proyectos originales, ideas diferentes y formas de actuar que rompen con viejos esquemas. Disfrutas encontrando soluciones creativas y colaborando con otras personas para construir algo nuevo.\n\n"

        "Cuando Marte encuentra equilibrio en Acuario, la independencia deja de convertirse en distancia y se transforma en una capacidad para liderar cambios respetando la diversidad y la libertad de cada persona.\n\n"

        "Esta posición te invita a recordar que transformar el mundo también requiere construir puentes con quienes piensan de manera diferente. La innovación alcanza toda su fuerza cuando logra convertirse en una realidad compartida."
    ),

    "Piscis": (
        "Con Marte en Piscis, la acción nace de la intuición, la sensibilidad y la conexión con aquello que da un sentido profundo a lo que haces. "
        "Necesitas sentir que tus esfuerzos responden a algo que trasciende el simple resultado y conecta con tus valores más íntimos.\n\n"

        "Tu energía suele activarse cuando percibes que puedes ayudar, inspirar o contribuir a aliviar el sufrimiento de otras personas. También encuentras fuerza en la creatividad, la espiritualidad y todas aquellas actividades que permiten expresar tu mundo interior.\n\n"

        "Cuando Marte encuentra equilibrio en Piscis, la sensibilidad deja de convertirse en duda o evasión y se transforma en una enorme capacidad para actuar con compasión, intuición y coherencia. Descubres que la firmeza también puede expresarse con suavidad.\n\n"

        "Esta posición te invita a recordar que la inspiración necesita encontrar una dirección concreta. Los sueños comienzan a transformar la realidad cuando das el primer paso para hacerlos posibles."
    )

}


MARTE_CASA = {

    1: (
        "Con Marte en la casa 1, la acción comienza contigo. "
        "Necesitas sentir que puedes tomar la iniciativa, decidir tu propio camino y responder a la vida desde tu autenticidad. Tu energía busca expresarse de forma directa, impulsándote a abrir caminos en lugar de esperar a que otros lo hagan por ti.\n\n"

        "Disfrutas enfrentándote a nuevos retos, poniendo en marcha proyectos y comprobando que eres capaz de transformar la realidad con tus propias acciones. La independencia y la capacidad de decidir suelen convertirse en importantes fuentes de motivación.\n\n"

        "Esta posición te invita a recordar que la verdadera iniciativa no consiste únicamente en actuar primero. También implica aprender a escuchar, sostener el ritmo y permitir que otras personas puedan acompañarte cuando el camino lo requiera."
    ),

    2: (
        "Con Marte en la casa 2, la acción se orienta hacia la construcción de estabilidad, recursos y seguridad personal. "
        "Necesitas sentir que tus esfuerzos generan resultados tangibles y que la energía invertida contribuye a crear una vida sólida y coherente con tus valores.\n\n"

        "Tu impulso suele expresarse a través del trabajo constante, la perseverancia y la capacidad para materializar objetivos. Cuando encuentras una meta que consideras valiosa, puedes mantener el esfuerzo durante largos periodos de tiempo.\n\n"

        "Esta posición te invita a recordar que el verdadero valor no depende únicamente de lo que produces. Tu capacidad de actuar también necesita espacios donde el descanso y el disfrute formen parte del equilibrio."
    ),

    3: (
        "Con Marte en la casa 3, la acción encuentra su fuerza en la comunicación, el aprendizaje y el intercambio de ideas. "
        "Necesitas sentir que puedes expresar lo que piensas, defender tus argumentos y participar activamente en aquello que despierta tu curiosidad.\n\n"

        "Tu energía suele manifestarse a través de la palabra, la rapidez mental y la capacidad para encontrar soluciones con agilidad. Los debates, el estudio y los nuevos conocimientos pueden convertirse en motores importantes para tu acción.\n\n"

        "Esta posición te invita a recordar que comunicar también implica escuchar. La palabra adquiere mayor fuerza cuando deja espacio para comprender otras perspectivas antes de responder."
    ),

    4: (
        "Con Marte en la casa 4, la acción se dirige hacia la protección de tus raíces, tu hogar y aquello que te proporciona seguridad emocional. "
        "Necesitas sentir que puedes construir una base firme desde la que sostener el resto de tu vida.\n\n"

        "Tu energía suele activarse cuando percibes que es necesario cuidar a quienes forman parte de tu mundo más íntimo o cuando surge la oportunidad de fortalecer aquello que consideras esencial. La familia, el hogar o la vida privada pueden convertirse en escenarios donde expresas gran parte de tu fuerza.\n\n"

        "Esta posición te invita a recordar que proteger también implica cuidar de ti. Una base sólida no se construye únicamente sosteniendo a los demás, sino creando un lugar donde tú también puedas descansar y recuperar energía."
    ),

    5: (
        "Con Marte en la casa 5, la acción nace del deseo de crear, expresarte y disfrutar de aquello que despierta tu entusiasmo. "
        "Necesitas sentir que puedes poner tu energía al servicio de proyectos que te ilusionan y que reflejan quién eres.\n\n"

        "Tu impulso suele dirigirse hacia la creatividad, el juego, el liderazgo y todas aquellas experiencias donde puedes expresar tu iniciativa con libertad. Cuando algo enciende tu motivación, eres capaz de contagiar entusiasmo y movilizar también a quienes te rodean.\n\n"

        "Esta posición te invita a recordar que crear no significa demostrar constantemente tu valía. Tu fuerza encuentra su mayor expresión cuando actúas por el placer de construir, no por la necesidad de obtener reconocimiento."
    ),

    6: (
        "Con Marte en la casa 6, la acción se expresa a través del trabajo, la organización y la mejora continua. "
        "Necesitas sentir que tu energía contribuye a resolver problemas, generar bienestar y hacer que las cosas funcionen de una manera más eficiente.\n\n"

        "Tu impulso suele manifestarse en la disciplina cotidiana, la capacidad de asumir responsabilidades y el compromiso con las tareas que consideras importantes. Los pequeños avances sostenidos en el tiempo suelen convertirse en una de tus mayores fortalezas.\n\n"

        "Esta posición te invita a recordar que la productividad también necesita descanso. La energía se mantiene viva cuando existe un equilibrio entre el esfuerzo, el cuidado personal y la recuperación."
    ),

    7: (
        "Con Marte en la casa 7, la acción se desarrolla a través de la relación con otras personas. "
        "Necesitas sentir que los vínculos te impulsan a crecer, afrontar desafíos y aprender a defender tus necesidades sin dejar de construir acuerdos.\n\n"

        "Tu energía suele activarse en la colaboración, el diálogo y también en aquellas situaciones donde es necesario posicionarte con claridad. Las relaciones se convierten en un escenario importante para desarrollar tu capacidad de iniciativa y afirmación personal.\n\n"

        "Esta posición te invita a recordar que cooperar no significa renunciar a tu propia fuerza. Un vínculo sano permite que ambas personas puedan expresar sus necesidades sin que una tenga que imponerse sobre la otra."
    ),

    8: (
        "Con Marte en la casa 8, la acción busca transformar, profundizar y afrontar aquello que otras personas prefieren evitar. "
        "Necesitas sentir que tu energía sirve para atravesar las crisis, comprender aquello que normalmente permanece oculto y generar cambios que tengan un verdadero impacto.\n\n"

        "Tu impulso suele manifestarse con intensidad, perseverancia y una gran capacidad para sostener procesos complejos. Cuando decides implicarte en algo, rara vez te conformas con soluciones superficiales.\n\n"

        "Esta posición te invita a recordar que no toda transformación requiere una lucha permanente. La mayor fortaleza aparece cuando aprendes a distinguir qué merece realmente tu energía y qué puede ser soltado."
    ),

    9: (
        "Con Marte en la casa 9, la acción nace del deseo de explorar, aprender y ampliar tus propios límites. "
        "Necesitas sentir que cada experiencia te acerca a una comprensión más profunda de la vida y que tus esfuerzos tienen la capacidad de abrir nuevos horizontes.\n\n"

        "Tu energía suele dirigirse hacia el conocimiento, los viajes, la formación o cualquier proyecto que suponga crecimiento y expansión. Disfrutas emprendiendo caminos desconocidos y enfrentándote a retos que te invitan a evolucionar.\n\n"

        "Esta posición te invita a recordar que las grandes ideas solo transforman la realidad cuando encuentran una forma concreta de ponerse en práctica. La inspiración alcanza todo su potencial cuando se convierte en acción."
    ),

    10: (
        "Con Marte en la casa 10, la acción busca construir, liderar y dejar una huella visible en el mundo. "
        "Necesitas sentir que tus esfuerzos contribuyen a desarrollar un propósito sólido y que tu trabajo tiene un impacto real en aquello que deseas alcanzar.\n\n"

        "Tu energía suele manifestarse a través de la responsabilidad, la capacidad de asumir desafíos y la determinación para avanzar hacia objetivos importantes. Los proyectos de largo recorrido despiertan especialmente tu compromiso cuando conectan con aquello que consideras valioso.\n\n"

        "Esta posición te invita a recordar que el éxito no depende únicamente de llegar lejos. También necesita construirse de una manera que respete tus ritmos, tus valores y tu bienestar."
    ),

    11: (
        "Con Marte en la casa 11, la acción encuentra su fuerza en los proyectos compartidos, la colaboración y el deseo de contribuir a un futuro mejor. "
        "Necesitas sentir que tu energía forma parte de algo que trasciende el interés individual y genera un beneficio más amplio.\n\n"

        "Tu impulso suele dirigirse hacia los grupos, las iniciativas colectivas y las ideas innovadoras que pueden transformar la realidad. Disfrutas participando en proyectos donde cada persona aporta lo mejor de sí para construir un objetivo común.\n\n"

        "Esta posición te invita a recordar que colaborar no significa diluir tu propia voz. Tu contribución adquiere más fuerza cuando compartes tus ideas sin dejar de respetar la diversidad del grupo."
    ),

    12: (
        "Con Marte en la casa 12, la acción nace de un movimiento interior profundo que muchas veces necesita silencio antes de manifestarse hacia el exterior. "
        "Necesitas sentir que tus esfuerzos responden a un propósito con significado y que existe coherencia entre lo que haces y aquello que percibes en tu mundo interior.\n\n"

        "Tu energía suele activarse cuando puedes ayudar, acompañar procesos de transformación o dedicarte a actividades que requieren sensibilidad, intuición o creatividad. Con frecuencia, gran parte de tu fuerza se desarrolla lejos del reconocimiento externo.\n\n"

        "Esta posición te invita a recordar que la acción también necesita hacerse visible. La intuición y la inspiración encuentran todo su potencial cuando se traducen en decisiones concretas capaces de transformar la realidad."
    )

}

MARTE_COMBINACIONES = {

    "Sol": (
        "Cuando Marte y el Sol trabajan en sintonía, la acción y la identidad avanzan en la misma dirección. "
        "Lo que decides hacer nace de una profunda coherencia con quien eres, permitiéndote actuar con determinación y propósito.\n\n"

        "Esta combinación invita a recordar que la verdadera fuerza no consiste únicamente en hacer más. "
        "Consiste en dirigir tu energía hacia aquello que realmente expresa tu esencia."
    ),

    "Luna": (
        "Cuando Marte y la Luna colaboran, la acción y las emociones dejan de vivirse como fuerzas opuestas. "
        "Puedes responder a lo que sientes sin dejarte arrastrar por el impulso del momento, utilizando tu energía para proteger aquello que realmente importa.\n\n"

        "Esta combinación recuerda que actuar con sensibilidad no es una muestra de debilidad. "
        "La firmeza alcanza su mayor fuerza cuando también sabe escuchar al mundo emocional."
    ),

    "Mercurio": (
        "Cuando Marte y Mercurio trabajan juntos, el pensamiento encuentra la capacidad de convertirse en acción. "
        "Las ideas dejan de permanecer únicamente en el plano mental y se transforman en decisiones, iniciativas y soluciones concretas.\n\n"

        "Esta combinación invita a equilibrar rapidez y reflexión. "
        "Pensar antes de actuar fortalece la acción, y actuar después de pensar permite que el conocimiento cobre verdadero sentido."
    ),

    "Venus": (
        "Cuando Marte y Venus colaboran, el deseo y el afecto encuentran una dirección común. "
        "Puedes luchar por aquello que amas, proteger lo que valoras y construir relaciones donde la iniciativa y la sensibilidad se complementan.\n\n"

        "Esta combinación recuerda que la fuerza encuentra su mayor expresión cuando está al servicio de aquello que verdaderamente merece ser cuidado."
    ),

    "Júpiter": (
        "Cuando Marte y Júpiter se potencian mutuamente, la acción se llena de confianza, entusiasmo y deseo de crecer. "
        "Los desafíos se convierten en oportunidades para ampliar tus capacidades y explorar nuevos caminos.\n\n"

        "Esta combinación invita a actuar con valentía sin perder la capacidad de valorar las consecuencias. "
        "La expansión más sólida es aquella que también sabe avanzar con criterio."
    ),

    "Saturno": (
        "Cuando Marte y Saturno trabajan en sintonía, la energía encuentra estructura, disciplina y capacidad para sostener el esfuerzo a largo plazo. "
        "La determinación deja de depender del impulso inicial y se convierte en una fuerza constante que permite construir objetivos duraderos.\n\n"

        "Esta combinación recuerda que la perseverancia no consiste en avanzar sin descanso, sino en mantener el compromiso respetando también tus propios límites."
    ),

    "Urano": (
        "Cuando Marte y Urano colaboran, la acción impulsa el cambio, la innovación y la búsqueda de nuevas soluciones. "
        "La iniciativa encuentra formas originales de transformar la realidad y romper con aquello que ya no favorece el crecimiento.\n\n"

        "Esta combinación invita a utilizar la libertad con responsabilidad. "
        "Las transformaciones más profundas no solo nacen de romper con el pasado, sino también de construir un futuro más coherente."
    ),

    "Neptuno": (
        "Cuando Marte y Neptuno trabajan juntos, la acción se inspira en ideales, intuiciones y valores profundos. "
        "La energía encuentra sentido cuando aquello que haces conecta con algo que trasciende el beneficio inmediato.\n\n"

        "Esta combinación recuerda que la inspiración necesita convertirse en decisiones concretas para poder transformar la realidad."
    ),

    "Plutón": (
        "Cuando Marte y Plutón colaboran, la voluntad adquiere una enorme capacidad de transformación. "
        "Puedes afrontar procesos intensos, sostener cambios profundos y movilizar recursos internos que hasta entonces permanecían sin desarrollar.\n\n"

        "Esta combinación invita a recordar que la verdadera fuerza no necesita imponerse. "
        "Su mayor poder aparece cuando utiliza la intensidad para construir, regenerar y abrir nuevos caminos."
    ),

    "Ascendente": (
        "Cuando Marte y el Ascendente trabajan en sintonía, tu manera de actuar refleja con claridad quién eres y cómo decides abrirte camino en el mundo. "
        "La iniciativa surge de forma natural y transmite una sensación de autenticidad y determinación.\n\n"

        "Esta combinación invita a desarrollar una acción coherente con tu identidad. "
        "Cuanto más alineadas están tus decisiones con tu verdadera forma de ser, mayor es la fuerza con la que avanzas."
    ),

    "Nodo Norte": (
        "Cuando Marte y el Nodo Norte colaboran, aprender a actuar de una manera nueva forma parte esencial de tu evolución. "
        "La vida te invita a desarrollar una voluntad más consciente, capaz de elegir con claridad y dirigir tu energía hacia aquello que favorece tu crecimiento.\n\n"

        "Esta combinación recuerda que evolucionar también implica atreverse a actuar de formas que al principio resultan desconocidas."
    ),

    "Nodo Sur": (
        "Cuando Marte y el Nodo Sur se encuentran, existe una forma de actuar profundamente conocida y una manera de responder a los desafíos que surge con gran naturalidad. "
        "Es una fuerza que puede convertirse en un valioso recurso, aunque también puede llevarte a repetir antiguas estrategias cuando ya no resultan necesarias.\n\n"

        "Esta combinación invita a conservar la experiencia adquirida sin dejar que el pasado limite nuevas formas de actuar y avanzar."
    ),

    "Quirón": (
        "Cuando Marte y Quirón interactúan, la capacidad de actuar, afirmarte o defender tus necesidades puede estar unida a antiguas heridas que piden ser comprendidas e integradas. "
        "Precisamente ese recorrido puede convertirte en una persona capaz de actuar con una enorme sensibilidad hacia los procesos de los demás.\n\n"

        "Esta combinación recuerda que sanar no significa perder fuerza. "
        "Significa descubrir una forma de actuar que nace de la consciencia y no de la herida."
    ),

    "Lilith": (
        "Cuando Marte y Lilith se encuentran, la acción busca expresar aquello que durante mucho tiempo pudo permanecer contenido, rechazado o silenciado. "
        "Existe una poderosa necesidad de actuar con autenticidad, incluso cuando eso implique cuestionar expectativas o romper viejos condicionamientos.\n\n"

        "Esta combinación invita a utilizar esa fuerza con consciencia. "
        "La libertad alcanza su mayor poder cuando deja de reaccionar contra el pasado y comienza a construir desde una elección plenamente consciente."
    )

}

MARTE_INTEGRACION = {

    "necesidades": {
        "titulo": "Lo que Marte necesita",
        "texto": (
            "Marte necesita sentir que su energía tiene una dirección. "
            "No se alimenta del movimiento constante, sino de la posibilidad de actuar con intención, tomar decisiones y comprobar que sus acciones producen cambios reales.\n\n"

            "Cuando encuentra un propósito claro, la fuerza deja de dispersarse. La voluntad se organiza, la motivación aumenta y aparece la sensación de avanzar hacia una vida construida desde la coherencia."
        )
    },

    "cuidar": {
        "titulo": "Cómo cuidar tu Marte",
        "texto": (
            "Cuidar esta función implica mantener una relación sana con tu propia energía. "
            "El cuerpo necesita movimiento, pero también descanso. La voluntad necesita retos, pero también momentos para recuperar fuerzas. Y la acción necesita objetivos que realmente merezcan tu implicación.\n\n"

            "Marte se fortalece cuando aprendes a decidir dónde poner tu energía y dónde conservarla. No todo requiere una batalla, ni toda oportunidad merece el mismo esfuerzo."
        )
    },

    "equilibrio": {
        "titulo": "Cuando Marte está en equilibrio",
        "texto": (
            "Cuando Marte funciona de forma equilibrada, puedes actuar con firmeza sin perder la calma. Tomas decisiones con mayor claridad, sostienes el esfuerzo cuando es necesario y sabes poner límites sin necesidad de entrar en conflicto permanente.\n\n"

            "La acción deja de surgir como una reacción impulsiva y se convierte en una elección consciente. Tu energía trabaja a favor de aquello que deseas construir."
        )
    },

    "desregulacion": {
        "titulo": "Cuando Marte pierde el equilibrio",
        "texto": (
            "Cuando esta función se desregula, la energía suele oscilar entre dos extremos. "
            "A veces aparece la impulsividad, la prisa, la irritabilidad o la sensación de tener que luchar continuamente. Otras veces ocurre lo contrario: cuesta iniciar proyectos, tomar decisiones, defender las propias necesidades o mantener el impulso en el tiempo.\n\n"

            "En ambos casos, el desafío no consiste en tener más fuerza, sino en recuperar una dirección clara para que la energía vuelva a estar al servicio de tu vida y no de la reacción automática."
        )
    },

    "pregunta": {
        "titulo": "Una pregunta para observarte",
        "texto": (
            "¿La manera en que utilizas tu energía está construyendo la vida que deseas o simplemente responde a las exigencias, la costumbre o la inercia?"
        )
    },

    "integracion": {
        "titulo": "Integrar Marte",
        "texto": (
            "Integrar Marte no consiste en hacer más cosas ni en demostrar fortaleza constantemente. "
            "Consiste en desarrollar una voluntad consciente, capaz de elegir dónde implicarse, cuándo avanzar, cuándo detenerse y qué merece realmente tu energía.\n\n"

            "Cuando Marte ocupa su lugar, la acción deja de nacer de la urgencia y comienza a surgir desde la coherencia. Entonces cada decisión, por pequeña que sea, contribuye a construir una vida más sólida, más libre y más alineada contigo."
        )
    }

}



# ─── CÁLCULO ASTROLÓGICO ──────────────────────────────────────────────────────

def geocodificar(ciudad):
    g = Nominatim(user_agent="ai_planetas_personales", timeout=10)
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


def signos_en_cuspides(cuspides):
    return [grados_a_signo(c)[0] for c in cuspides]

def signo_interceptado(signo, cuspides):
    signos_cuspides = signos_en_cuspides(cuspides)
    return signo not in signos_cuspides


def calcular_carta(anio, mes, dia, hora, minuto, lat, lon, tz_name):
    ephe_path = os.path.join(BASE_DIR, "ephe")
    swe.set_ephe_path(ephe_path)

    flags = swe.FLG_SPEED
    jd = fecha_a_jd(anio, mes, dia, hora, minuto, tz_name)
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
        pos_ch, _ = swe.calc_ut(jd, CHIRON_ID, flags)
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

    pos_li, _ = swe.calc_ut(jd, LILITH_ID, flags)
    signo_li, grado_li = grados_a_signo(pos_li[0])
    planetas["Lilith"] = {
        "simbolo": "⚸",
        "lon": pos_li[0],
        "signo": signo_li,
        "grado": grado_li,
        "retrogrado": pos_li[3] < 0,
    }

    pos_nn, _ = swe.calc_ut(jd, swe.TRUE_NODE, flags)
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

    cuspides, ascmc = swe.houses(jd, lat, lon, b"P")
    asc_lon, mc_lon = ascmc[0], ascmc[1]
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
        "asc": {"lon": asc_lon, "signo": signo_asc, "grado": grado_asc},
        "mc": {"lon": mc_lon, "signo": signo_mc, "grado": grado_mc},
        "jd": jd,
    }


def grados_a_signo_lon(lon):
    """Retorna (signo, grado) con el número de signo (índice 0-11)."""
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



def obtener_texto_aspecto(combinaciones, planeta, tipo_aspecto):
    """
    Construye la interpretación de un aspecto combinando:

    1. El significado de la combinación entre ambos cuerpos.
    2. La manera en que se expresa según el tipo de aspecto.
    """

    texto_combinacion = combinaciones.get(planeta)
    texto_aspecto = TEXTOS_TIPO_ASPECTO.get(tipo_aspecto)

    if not texto_combinacion or not texto_aspecto:
        return ""

    return f"{texto_combinacion}\n\n{texto_aspecto}"



def calcular_aspectos_planetas_personales(planetas, asc):
    return calcular_aspectos_modulo(
        planetas,
        asc,
        ("Mercurio", "Venus", "Marte"),
    )



# ─── RUEDA SIMPLIFICADA: MERCURIO + VENUS + MARTE ────────────────────────────

def dibujar_rueda_planetas_personales(carta, aspectos, archivo_salida):
    """
    Rueda focal de Planetas Personales.

    Muestra Mercurio, Venus y Marte, junto con los planetas,
    Nodos o ángulos con los que forman aspectos.
    """
    planetas = carta["planetas"]
    cuspides = carta["cuspides"]
    asc_lon = carta["asc"]["lon"]

    planetas_focales = {
        "Mercurio",
        "Venus",
        "Marte",
    }

    # Conserva solamente los aspectos en los que participa
    # Mercurio, Venus o Marte.
    aspectos_personales = [
        aspecto
        for aspecto in aspectos
        if aspecto.get("p1") in planetas_focales
        or aspecto.get("p2") in planetas_focales
    ]

    def lon_a_angulo(lon):
        return math.radians(180 + (lon - asc_lon))

    R_EXT = 1.35
    R_SIGN_IN = 1.05
    R_CASA_OUT = 1.02
    R_CASA_IN = 0.65
    R_PLANETA = 0.82

    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
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
        theta = np.linspace(ang_ini, ang_fin, 50)

        xs = (
            [math.cos(a) * R_EXT for a in theta]
            + [
                math.cos(a) * R_SIGN_IN
                for a in reversed(theta)
            ]
        )

        ys = (
            [math.sin(a) * R_EXT for a in theta]
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
        zip(SIGNOS, SIMBOLOS_SIGNOS)
    ):
        ang_mid = lon_a_angulo(i * 30 + 15)
        r_mid = (R_SIGN_IN + R_EXT) / 2
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

        lw = 1.8 if i in (0, 3, 6, 9) else 0.5
        col = "#111" if i in (0, 3, 6, 9) else "#999"

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
            ang_num = lon_a_angulo(cusp + 4.0)
            r_num = (R_CASA_IN + 0.25) / 2 + 0.12

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
    for aspecto in aspectos_personales:
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

        a1 = lon_a_angulo(obj1["lon"])
        a2 = lon_a_angulo(obj2["lon"])

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

    # Los tres planetas personales siempre aparecen.
    nombres_visibles = {
        "Mercurio",
        "Venus",
        "Marte",
    }

    # Añadimos todos los cuerpos que estén aspectados
    # con alguno de los tres planetas personales.
    for aspecto in aspectos_personales:
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
        if nombre in planetas and planetas[nombre]:
            puntos[nombre] = planetas[nombre]

    # Distribución radial para evitar solapamientos
    lones_usados = []
    radios = {}

    for nombre, p in puntos.items():
        lon = p["lon"]
        radio = R_PLANETA

        for lon_previa, radio_previo in lones_usados:
            distancia = abs(lon - lon_previa) % 360

            if distancia > 180:
                distancia = 360 - distancia

            if distancia < 8:
                if radio_previo - 0.10 > 0.45:
                    radio = radio_previo - 0.10
                else:
                    radio = radio_previo + 0.10

                break

        lones_usados.append(
            (lon, radio)
        )

        radios[nombre] = radio

    # Símbolos planetarios
    for nombre, p in puntos.items():
        ang = lon_a_angulo(p["lon"])
        r = radios[nombre]

        color = COLORES_PLANETA.get(
            nombre,
            "#333",
        )

        simbolo = p["simbolo"]

        # Mercurio, Venus y Marte quedan ligeramente destacados.
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
                math.cos(ang) * (R_SIGN_IN + 0.01),
            ],
            [
                math.sin(ang) * (r + 0.07),
                math.sin(ang) * (R_SIGN_IN + 0.01),
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
            (carta["asc"]["lon"] + 180) % 360,
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
            (carta["mc"]["lon"] + 180) % 360,
            False,
            10,
        ),
    ]:
        ang = lon_a_angulo(lon_pt)

        fw = "bold" if bold else "normal"
        col = "#111" if bold else "#555"

        ax.text(
            math.cos(ang) * (R_EXT + 0.12),
            math.sin(ang) * (R_EXT + 0.12),
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


def bloque_portada_personales(
    nombre,
    fecha_str,
    hora_str,
    ciudad,
    estilos,
):
    return [
        Spacer(1, 1.7 * cm),

        Paragraph(
            "Planetas Personales",
            estilos["titulo"],
        ),

        Paragraph(
            "Mercurio · Venus · Marte",
            estilos["centro"],
        ),

        Spacer(1, 0.45 * cm),

        Paragraph(
            "Una lectura sobre cómo piensas, cómo valoras y cómo movilizas tu energía.",
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
            "Arquitectura Interna · Un método para sostener cuerpo, energía y vida con coherencia",
            estilos["estilo_frase_final"],
        ),

        PageBreak(),
    ]


def bloque_bienvenida_personales(estilos):

    texto = (
        "Hay funciones que utilizas todos los días sin darte cuenta. "
        "Cómo piensas, cómo decides, qué valor das a las personas, a las experiencias "
        "y a quien eres, o de qué manera pasas a la acción. Todo ello forma parte de una "
        "arquitectura interna que sostiene tu forma de estar en el mundo.\n\n"

        "En este informe recorrerás tres funciones esenciales. Mercurio muestra cómo "
        "observas la realidad, cómo organizas la información y cómo elaboras tus ideas. "
        "Venus describe aquello que valoras, la forma en que construyes los vínculos y "
        "los criterios desde los que eliges. Marte representa el impulso que te lleva "
        "a actuar, afirmar tus límites y dirigir tu energía.\n\n"

        "Este cuaderno no pretende definir tu personalidad. Pretende ayudarte a reconocer "
        "cómo colaboran estas tres funciones, dónde encuentran apoyo mutuo y dónde pueden "
        "aparecer tensiones que condicionen tu manera de vivir."
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
        "Recorre el informe con curiosidad, detente en aquello que resuene contigo "
        "y vuelve a estas páginas cuando tu propia experiencia les dé un significado nuevo.",
        estilos["cuerpo"],
    )

    return elementos


def bloque_rueda_personales(
    ruta_rueda,
    estilos,
):
    return [
        Spacer(1, 0.3 * cm),
        Image(
            ruta_rueda,
            width=11.5 * cm,
            height=11.5 * cm,
        ),
        PageBreak(),
    ]


def bloque_resumen_personales(
    carta,
    estilos,
):
    planetas = carta["planetas"]

    mercurio = planetas.get("Mercurio", {})
    venus = planetas.get("Venus", {})
    marte = planetas.get("Marte", {})

    tabla_datos = [
        ["Planeta", "Signo", "Casa", "Función"],
        [
            "Mercurio",
            mercurio.get("signo", ""),
            f"Casa {mercurio.get('casa', '')}",
            "Pensamiento, lenguaje y comprensión",
        ],
        [
            "Venus",
            venus.get("signo", ""),
            f"Casa {venus.get('casa', '')}",
            "Valores, vínculo y capacidad de recibir",
        ],
        [
            "Marte",
            marte.get("signo", ""),
            f"Casa {marte.get('casa', '')}",
            "Acción, deseo y afirmación",
        ],
    ]

    tabla = Table(
        tabla_datos,
        colWidths=[
            2.4 * cm,
            2.6 * cm,
            2.4 * cm,
            5.6 * cm,
        ],
    )

    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDE3D3")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1E508C")),
        ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Times-Roman"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D8CBB8")),
        ("BOX", (0, 0), (-1, -1), 1.2, colors.HexColor("#8C5A00")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (2, 0), (2, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    return [
        Paragraph(
            "La arquitectura de tus funciones personales",
            estilos["subtitulo"],
        ),
        Spacer(1, 0.9 * cm),
        tabla,
    ]

def bloque_aspectos_principales_personales(
    aspectos,
    estilos,
):
    """
    Muestra una tabla resumen con todos los aspectos de
    Mercurio, Venus y Marte.

    Cada pareja aparece una sola vez porque la lista de aspectos
    ya se genera sin duplicados.
    """

    elementos = [
        Spacer(1, 0.8 * cm),
        Paragraph(
            "Aspectos relevantes",
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
                "No aparecen aspectos relevantes de Mercurio, Venus o Marte "
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


# ─── BLOQUES DE CONTENIDO: PLANETAS PERSONALES ────────────────────────────────
PLANETAS_PERSONALES = {
    "Mercurio",
    "Venus",
    "Marte",
}

ORDEN_PLANETAS_PERSONALES = {
    "Mercurio": 1,
    "Venus": 2,
    "Marte": 3,
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
    texto_casa = textos_casa.get(casa, "")

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
                f"No se han encontrado aspectos relevantes de {planeta} "
                "dentro de los orbes utilizados en este informe.",
                estilos["cuerpo"],
            )
        )

        return elementos

    aspectos_con_texto = 0

    for aspecto in aspectos_planeta:
        otro_punto = aspecto["otro_punto"]
        tipo = aspecto["tipo"]
        orbe = aspecto["orbe"]

        # Evita repetir aspectos entre Mercurio, Venus y Marte.
        #
        # Orden de interpretación:
        # Mercurio interpreta sus aspectos con Venus y Marte.
        # Venus interpreta su aspecto con Marte.
        # Marte no vuelve a interpretar esos vínculos.

    if (
        planeta in PLANETAS_PERSONALES
        and otro_punto in PLANETAS_PERSONALES
        and ORDEN_PLANETAS_PERSONALES[planeta]
           > ORDEN_PLANETAS_PERSONALES[otro_punto]
    ):
        continue

        texto = obtener_texto_aspecto(
            combinaciones,
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


def bloque_planeta_personal(
    planeta,
    carta,
    aspectos,
    textos_signo,
    textos_casa,
    combinaciones,
    integracion,
    subtitulo_capitulo,
    estilos,
):
    """
    Genera el capítulo completo de un planeta personal:

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
        estilos=estilos,
    )

    elementos += bloque_integracion_planeta(
        planeta=planeta,
        integracion=integracion,
        estilos=estilos,
    )

    return elementos


def bloque_mercurio(
    carta,
    aspectos,
    estilos,
):
    return bloque_planeta_personal(
        planeta="Mercurio",
        carta=carta,
        aspectos=aspectos,
        textos_signo=MERCURIO_SIGNO,
        textos_casa=MERCURIO_CASA,
        combinaciones=MERCURIO_COMBINACIONES,
        integracion=MERCURIO_INTEGRACION,
        subtitulo_capitulo=(
            "La forma en que observas, comprendes y das significado a lo que vives."
        ),
        estilos=estilos,
    )


def bloque_venus(
    carta,
    aspectos,
    estilos,
):
    return bloque_planeta_personal(
        planeta="Venus",
        carta=carta,
        aspectos=aspectos,
        textos_signo=VENUS_SIGNO,
        textos_casa=VENUS_CASA,
        combinaciones=VENUS_COMBINACIONES,
        integracion=VENUS_INTEGRACION,
        subtitulo_capitulo=(
            "La forma en que valoras, te vinculas y reconoces aquello que merece un lugar en tu vida."
        ),
        estilos=estilos,
    )


def bloque_marte(
    carta,
    aspectos,
    estilos,
):
    return bloque_planeta_personal(
        planeta="Marte",
        carta=carta,
        aspectos=aspectos,
        textos_signo=MARTE_SIGNO,
        textos_casa=MARTE_CASA,
        combinaciones=MARTE_COMBINACIONES,
        integracion=MARTE_INTEGRACION,
        subtitulo_capitulo=(
            "La forma en que actúas, afirmas tus límites y diriges tu energía."
        ),
        estilos=estilos,
    )


def generar_pdf_planetas_personales(
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

    contenido += bloque_portada_personales(
        nombre,
        fecha_str,
        hora_str,
        ciudad,
        estilos,
    )

    contenido += bloque_bienvenida_personales(
        estilos,
    )

    contenido += bloque_rueda_personales(
        ruta_rueda,
        estilos,
    )

    contenido += bloque_resumen_personales(
        carta,
        estilos,
    )

    contenido += bloque_aspectos_principales_personales(
        aspectos,
        estilos,
    )


    # ── CAPÍTULO DE PERSONALES ──────────────────────────────────────

    contenido += bloque_mercurio(
        carta,
        aspectos,
        estilos,
    )

    contenido += bloque_venus(
        carta,
        aspectos,
        estilos,
    )

    contenido += bloque_marte(
        carta,
        aspectos,
        estilos,
    )


    # ── CIERRE ────────────────────────────────────────────────────

    contenido.append(
        PageBreak()
    )

    contenido.append(
        KeepTogether([
            Paragraph(
                "Cierre",
                estilos["subtitulo"],
            ),
            Paragraph(
                "Comprender cómo piensas, qué valoras y de qué manera actúas puede cambiar la relación que mantienes contigo.",
                estilos["cuerpo"],
            ),
            Paragraph(
                "La forma en que estas tres funciones colaboren dependerá de cómo aprendas a escucharlas, equilibrarlas y ponerlas al servicio de la vida que deseas construir.",
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
    print("  MERCURIO · VENUS · MARTE — Arquitectura Interna")
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

    aspectos = calcular_aspectos_planetas_personales(
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
        nombre_f + "_Planetas_Personales",
    )

    ruta_pdf = ruta_base + ".pdf"
    ruta_rueda = ruta_base + "_rueda.png"

    print("Generando rueda...")

    dibujar_rueda_planetas_personales(
        carta,
        aspectos,
        ruta_rueda,
    )

    print("Generando PDF con ReportLab...")

    generar_pdf_planetas_personales(
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
        "Generando informe Mercurio · Venus · Marte para:",
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
            lat, lon = geocodificar(lugar)

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

        # ── ASPECTOS DE MERCURIO, VENUS Y MARTE ───────────────

        aspectos = calcular_aspectos_planetas_personales(
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
            nombre_f + "_Planetas_Personales",
        )

        ruta_pdf = ruta_base + ".pdf"
        ruta_rueda = ruta_base + "_rueda.png"

        # ── RUEDA ─────────────────────────────────────────────

        dibujar_rueda_planetas_personales(
            carta,
            aspectos,
            ruta_rueda,
        )

        # ── PDF ───────────────────────────────────────────────

        generar_pdf_planetas_personales(
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
            "Error generando Mercurio · Venus · Marte:",
            error,
        )

        return {
            "ok": False,
            "error": str(error),
        }


if __name__ == "__main__":
    main()