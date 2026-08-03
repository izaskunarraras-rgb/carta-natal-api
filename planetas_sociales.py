#!/usr/bin/env python3
"""
5. Planetas Sociales — Arquitectura Interna

Interpreta la forma de ampliar tu perspectiva, encontrar sentido
y desarrollar confianza en tus propios recursos (Júpiter),
junto con la capacidad de construir estructura, asumir responsabilidad
y sostener tus procesos en el tiempo (Saturno)
dentro de la carta natal.
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


# ─── TEXTOS: JÚPITER ─────────────────────────────────────────────
JUPITER_SIGNO = {

"Aries":
"""Necesitas sentir que puedes crecer iniciando caminos propios. La confianza suele aparecer cuando actúas, exploras y te permites abrir experiencias sin esperar a tener todas las respuestas.

Es habitual que desarrolles una actitud optimista frente a los desafíos y que prefieras aprender a través de la acción antes que desde la teoría. Sueles descubrir tus capacidades mientras avanzas.

Cuando esta energía se desregula puede aparecer la tendencia a precipitarte, asumir más de lo que realmente puedes sostener o confiar únicamente en el impulso del momento.

Recuperas mejor el equilibrio cuando conservas la iniciativa sin perder la capacidad de reflexionar sobre la dirección que estás tomando.""",

"Tauro":
"""Necesitas sentir que el crecimiento tiene una base sólida y que cada paso puede integrarse de forma estable en tu vida. La confianza suele construirse lentamente, a medida que compruebas por experiencia lo que realmente funciona para ti.

Tiendes a valorar los procesos constantes y a desarrollar tus recursos de forma paciente, disfrutando de todo aquello que aporta seguridad y continuidad.

Cuando esta energía pierde equilibrio puede aparecer una excesiva necesidad de conservar lo conocido o cierta resistencia a ampliar horizontes por miedo a perder estabilidad.

La expansión resulta más natural cuando permites que la seguridad sea un punto de apoyo y no un límite para seguir creciendo.""",

"Géminis":
"""Necesitas comprender el mundo desde muchos puntos de vista. Tu crecimiento suele aparecer cuando puedes hacer preguntas, intercambiar ideas y mantener viva la curiosidad.

Aprendes con facilidad a través de conversaciones, lecturas y experiencias variadas, encontrando conexiones entre temas muy diferentes.

Cuando esta energía se dispersa puedes acumular información sin llegar a profundizar realmente o cambiar constantemente de dirección buscando siempre algo nuevo.

Tu confianza aumenta cuando conviertes la curiosidad en conocimiento integrado y das tiempo a que las ideas maduren antes de seguir buscando respuestas.""",

"Cáncer":
"""Necesitas sentir que el crecimiento protege también tu mundo emocional. La confianza suele desarrollarse cuando puedes cuidar, pertenecer y construir vínculos que aporten seguridad.

Tiendes a ampliar tu vida fortaleciendo aquello que consideras un hogar, ya sea una familia, una comunidad o cualquier espacio donde puedas sentir una acogida profunda.

Cuando esta energía se desregula puedes buscar protección en exceso o limitar nuevas experiencias por temor a perder esa seguridad emocional.

La expansión aparece con mayor facilidad cuando descubres que cuidar de ti también implica permitirte explorar lo desconocido.""",

"Leo":
"""Necesitas sentir que puedes expresar lo mejor de ti sin esconder tu luz. La confianza suele crecer cuando desarrollas tus talentos y encuentras espacios donde compartirlos con autenticidad.

Es habitual que inspires a otras personas a través de tu entusiasmo y que disfrutes creando, liderando o aportando algo que lleve tu sello personal.

Cuando esta energía pierde equilibrio puede aparecer la necesidad de reconocimiento constante o la sensación de que solo puedes crecer si recibes validación externa.

Recuperas tu centro cuando recuerdas que el verdadero brillo nace de expresar quién eres, no de demostrar constantemente tu valor.""",

"Virgo":
"""Necesitas sentir que cada experiencia puede ayudarte a mejorar y comprender mejor cómo funcionan las cosas. La confianza suele desarrollarse a través del aprendizaje constante y la práctica.

Tiendes a crecer refinando habilidades, organizando recursos y encontrando maneras más eficaces de resolver problemas cotidianos.

Cuando esta energía se desregula puedes centrarte tanto en lo que aún falta por perfeccionar que te cueste reconocer todo lo que ya has construido.

La expansión se vuelve más sólida cuando aceptas que crecer también implica valorar el camino recorrido y no únicamente aquello que queda por mejorar.""",

"Libra":
"""Necesitas descubrir el crecimiento a través del encuentro con otras personas. La confianza suele fortalecerse cuando puedes compartir perspectivas, cooperar y construir relaciones equilibradas.

Tiendes a ampliar tu visión escuchando opiniones diferentes y buscando puntos de encuentro que enriquezcan a todas las partes.

Cuando esta energía pierde equilibrio puedes depender demasiado de la aprobación ajena o evitar decisiones difíciles para mantener la armonía.

Recuperas el equilibrio cuando recuerdas que una relación sana también necesita que tu propia voz tenga espacio.""",

"Escorpio":
"""Necesitas comprender aquello que transforma profundamente la vida. Tu crecimiento suele surgir cuando atraviesas procesos intensos que te obligan a mirar más allá de las apariencias.

Es habitual que desarrolles una gran capacidad para descubrir significados ocultos y para encontrar recursos incluso en momentos de cambio o crisis.

Cuando esta energía se desregula puedes buscar intensidad de forma constante o desconfiar de aquello que parece demasiado sencillo.

La confianza aumenta cuando comprendes que no toda transformación necesita producirse desde el sufrimiento; también puede surgir desde la consciencia y la integración.""",

"Sagitario":
"""Necesitas sentir que la vida siempre puede abrir nuevos horizontes. La confianza aparece cuando amplías conocimientos, exploras otros lugares o encuentras ideas que den sentido a tu experiencia.

Sueles desarrollar una visión optimista y una capacidad natural para conectar acontecimientos individuales con una perspectiva más amplia.

Cuando esta energía pierde equilibrio puedes perseguir continuamente el siguiente horizonte sin detenerte a integrar todo lo aprendido o asumir más de lo que realmente puedes abarcar.

Recuperas el equilibrio cuando permites que cada experiencia encuentre un lugar dentro de tu propia historia antes de buscar la siguiente.""",

"Capricornio":
"""Necesitas comprobar que el crecimiento puede construirse paso a paso. La confianza suele desarrollarse cuando alcanzas objetivos mediante esfuerzo, constancia y compromiso con lo que consideras importante.

Tiendes a ampliar tus recursos organizando bien el tiempo, asumiendo responsabilidades y desarrollando una visión estratégica de largo plazo.

Cuando esta energía se desregula puedes medir tu valor únicamente por los resultados o sentir que nunca es suficiente lo conseguido.

La expansión se vuelve más saludable cuando recuerdas que el camino también forma parte del logro y no solo la meta alcanzada.""",

"Acuario":
"""Necesitas sentir que crecer implica ampliar la forma de comprender el mundo. La confianza suele aparecer cuando puedes pensar con independencia y aportar ideas diferentes.

Tiendes a descubrir oportunidades allí donde otras personas solo ven costumbre, disfrutando de los cambios, la innovación y las perspectivas poco convencionales.

Cuando esta energía pierde equilibrio puedes distanciarte emocionalmente o rechazar cualquier estructura simplemente por necesidad de diferenciarte.

Recuperas el equilibrio cuando combinas tu capacidad de innovación con una conexión real con las personas que te rodean.""",

"Piscis":
"""Necesitas sentir que el crecimiento también incluye aquello que no siempre puede explicarse con palabras. La confianza suele desarrollarse cuando conectas con la sensibilidad, la imaginación y una percepción amplia de la vida.

Es habitual que encuentres significado a través del arte, la espiritualidad, la creatividad o la capacidad de comprender profundamente las experiencias humanas.

Cuando esta energía se desregula puedes perder claridad, idealizar determinadas situaciones o confiar más en las posibilidades que en la realidad presente.

La expansión encuentra un apoyo sólido cuando permites que tu sensibilidad camine de la mano del discernimiento y de los límites que necesitas para cuidar de ti."""
}

JUPITER_CASA = {

1:
"""Necesitas sentir que crecer forma parte de quién eres. La confianza suele aparecer cuando te permites explorar la vida con apertura, desarrollar nuevas experiencias y ampliar constantemente la imagen que tienes de ti.

Es habitual que transmitas entusiasmo, optimismo o una sensación de posibilidades que otras personas perciben con facilidad. Tu manera de afrontar la vida suele invitar a seguir avanzando incluso cuando aparecen dificultades.

Cuando esta energía se desregula puedes confiar demasiado en que todo terminará resolviéndose por sí solo, asumir más de lo que realmente puedes sostener o vivir en un crecimiento permanente sin detenerte a integrar lo aprendido.

Recuperas el equilibrio cuando permites que el entusiasmo vaya acompañado de presencia, realismo y compromiso con aquello que decides construir.""",

2:
"""Necesitas comprobar que el crecimiento también puede traducirse en recursos, estabilidad y una mayor confianza en tus capacidades. Sueles ampliar tu seguridad a través de aquello que desarrollas con tu propio esfuerzo.

Es habitual que valores la abundancia entendida como la posibilidad de disponer de tiempo, conocimientos, dinero o herramientas que te permitan vivir con mayor libertad.

Cuando esta energía pierde equilibrio puedes medir tu crecimiento únicamente por lo que consigues acumular o confiar demasiado en que siempre habrá recursos disponibles.

La expansión se vuelve más sólida cuando reconoces que tu mayor riqueza nace de todo aquello que has aprendido a desarrollar dentro de ti.""",

3:
"""Necesitas aprender continuamente para sentir que avanzas. La confianza suele crecer cuando puedes hacer preguntas, conversar, leer, enseñar o descubrir nuevas formas de comprender el mundo.

Tiendes a ampliar tu perspectiva conectando ideas muy diferentes entre sí y disfrutando de los intercambios intelectuales con otras personas.

Cuando esta energía se desregula puedes dispersarte entre demasiados intereses o acumular información sin dedicar tiempo suficiente a integrarla.

Recuperas el equilibrio cuando conviertes el conocimiento en experiencia y permites que cada aprendizaje transforme realmente tu manera de mirar la vida.""",

4:
"""Necesitas que el crecimiento tenga raíces profundas. La confianza suele desarrollarse cuando construyes una base emocional sólida desde la que poder expandirte con tranquilidad.

Es habitual que encuentres sentido fortaleciendo tus vínculos familiares, creando un hogar acogedor o desarrollando una sensación interna de pertenencia.

Cuando esta energía pierde equilibrio puedes buscar protección en exceso o posponer nuevas experiencias esperando sentirte completamente seguro.

La expansión aparece con mayor facilidad cuando descubres que una base firme no impide avanzar, sino que precisamente hace posible hacerlo.""",

5:
"""Necesitas sentir que la vida puede disfrutarse y expresarse con libertad. La confianza suele crecer cuando desarrollas tu creatividad, compartes tus talentos o permites que aparezca el juego y la espontaneidad.

Tiendes a inspirar entusiasmo y a transmitir una actitud vital que anima a otras personas a conectar con aquello que les ilusiona.

Cuando esta energía se desregula puedes buscar experiencias intensas de forma constante, asumir riesgos innecesarios o depender demasiado de la validación que recibes.

Recuperas el equilibrio cuando recuerdas que crear también implica sostener aquello que nace de ti y no únicamente iniciar algo nuevo.""",

6:
"""Necesitas comprobar que el crecimiento también se construye en lo cotidiano. La confianza suele desarrollarse cuando mejoras habilidades, organizas tus recursos y encuentras formas más eficaces de cuidar de ti.

Es habitual que disfrutes aprendiendo, perfeccionando procesos y ampliando aquello que sabes hacer.

Cuando esta energía pierde equilibrio puedes asumir demasiadas responsabilidades, exigirte constantemente más rendimiento o creer que siempre queda algo por optimizar.

La expansión resulta mucho más saludable cuando permites que el cuidado personal forme parte de tu desarrollo y no solo la productividad.""",

7:
"""Necesitas descubrir nuevas perspectivas a través de las relaciones. La confianza suele crecer cuando compartes proyectos, colaboras con otras personas y permites que el encuentro amplíe tu forma de comprender la vida.

Es habitual que atraigas personas que estimulan tu crecimiento o que desempeñen un papel importante en momentos de aprendizaje.

Cuando esta energía pierde equilibrio puedes idealizar determinadas relaciones o esperar que otras personas aporten aquello que solo tú puedes desarrollar.

Recuperas el equilibrio cuando entiendes que una relación enriquecedora amplía tu mundo sin sustituir tu propio camino.""",

8:
"""Necesitas comprender aquello que transforma profundamente a las personas. La confianza suele desarrollarse cuando atraviesas cambios importantes, integras pérdidas o descubres recursos que antes desconocías en ti.

Tiendes a ampliar tu visión explorando temas complejos y buscando significado incluso en las experiencias más intensas.

Cuando esta energía se desregula puedes sentir atracción por procesos excesivamente extremos o mantener la sensación de que solo se crece a través de la dificultad.

La expansión encuentra un apoyo más sólido cuando reconoces que la transformación también puede producirse desde la consciencia, la intimidad y la confianza.""",

9:
"""Necesitas ampliar constantemente tu horizonte. La confianza suele crecer cuando estudias, viajas, conoces otras culturas o encuentras ideas que aportan un sentido más amplio a tu experiencia.

Es habitual que disfrutes explorando nuevas formas de pensar y conectando conocimientos que enriquecen tu visión del mundo.

Cuando esta energía pierde equilibrio puedes perseguir continuamente nuevos horizontes sin detenerte a integrar todo lo aprendido o creer que siempre existe una respuesta definitiva en otro lugar.

Recuperas el equilibrio cuando permites que cada experiencia encuentre un espacio dentro de tu propia forma de comprender la vida.""",

10:
"""Necesitas sentir que tu crecimiento tiene una expresión visible en el mundo. La confianza suele desarrollarse cuando construyes una trayectoria coherente con aquello que consideras importante y aportas algo valioso a la sociedad.

Es habitual que desarrolles una visión amplia de tus objetivos y que asumas responsabilidades con la intención de generar un impacto positivo.

Cuando esta energía pierde equilibrio puedes identificar tu valor únicamente con el reconocimiento externo o asumir metas cada vez mayores sin preguntarte si realmente responden a tus necesidades.

La expansión resulta más estable cuando el éxito deja de medirse solo por lo conseguido y también incluye la coherencia con la persona en la que te estás convirtiendo.""",

11:
"""Necesitas crecer compartiendo ideas, proyectos y sueños con otras personas. La confianza suele aparecer cuando formas parte de grupos que favorecen el intercambio, la innovación y el aprendizaje colectivo.

Tiendes a ampliar tu visión conectando con personas muy diferentes entre sí y encontrando oportunidades allí donde otros solo ven límites.

Cuando esta energía se desregula puedes dispersarte entre demasiados proyectos o confiar más en las posibilidades futuras que en los pasos concretos del presente.

Recuperas el equilibrio cuando conviertes tus ideales en acciones sostenibles que puedan integrarse en tu vida cotidiana.""",

12:
"""Necesitas sentir que el crecimiento también ocurre en los espacios de silencio, introspección y conexión contigo. La confianza suele desarrollarse cuando permites que la vida interior tenga un lugar importante dentro de tu proceso.

Es habitual que encuentres significado a través de la contemplación, la creatividad, la espiritualidad o la capacidad de comprender profundamente el mundo emocional.

Cuando esta energía pierde equilibrio puedes idealizar determinadas experiencias, perder claridad sobre tus propios límites o refugiarte demasiado en el mundo interior.

La expansión se vuelve más equilibrada cuando tu sensibilidad encuentra formas concretas de expresarse y puede convivir con la realidad cotidiana."""
}


JUPITER_COMBINACIONES = {

    "Sol": (
        "Tu manera de crecer, encontrar sentido y confiar en la vida está estrechamente relacionada con la construcción de tu identidad. "
        "Necesitas sentir que puedes desarrollar tus capacidades, ampliar tus posibilidades y avanzar en una dirección coherente con quien eres.\n\n"

        "Cuando ambas partes colaboran, aparece una confianza natural en tus recursos y una mayor facilidad para reconocer oportunidades de desarrollo. "
        "Tu entusiasmo puede ayudarte a afirmar tu presencia y a compartir con otras personas una visión amplia de lo que es posible.\n\n"

        "Esta combinación te invita a distinguir entre confiar en ti y sentir que necesitas demostrar constantemente tu valor. "
        "La seguridad interior crece cuando puedes reconocer tus posibilidades sin perder de vista tus límites, tus dudas y todo aquello que todavía estás aprendiendo."
    ),

    "Luna": (
        "Tu forma de encontrar sentido y ampliar tu vida está conectada con tus necesidades emocionales. "
        "La confianza suele crecer cuando puedes sentirte en un lugar seguro, comprender lo que te ocurre y construir una experiencia interna suficientemente estable desde la que explorar.\n\n"

        "Cuando ambas partes colaboran, desarrollas una actitud generosa, protectora y capaz de transmitir esperanza en momentos emocionalmente complejos. "
        "También puedes encontrar significado en tus vivencias y convertirlas en una fuente de comprensión.\n\n"

        "Esta combinación te invita a observar cuándo el optimismo te ayuda a sostener una emoción y cuándo lo utilizas para evitar sentirla. "
        "Encontrar una explicación no siempre sustituye la necesidad de permanecer un tiempo junto a lo que te está ocurriendo."
    ),

    "Mercurio": (
        "Tu manera de pensar busca amplitud, significado y una visión que permita comprender el conjunto. "
        "Las ideas crecen cuando puedes relacionarlas con preguntas importantes, nuevos conocimientos o formas diferentes de interpretar la vida.\n\n"

        "Cuando ambas partes colaboran, puedes comunicar con entusiasmo, transmitir confianza y ayudar a otras personas a descubrir posibilidades que antes no habían considerado.\n\n"

        "Esta combinación te invita a equilibrar la visión amplia con la atención a los hechos. "
        "Una idea inspiradora gana profundidad cuando también puede contrastarse, concretarse y sostenerse en la realidad."
    ),

    "Venus": (
        "Tu forma de crecer está vinculada con aquello que valoras, disfrutas y eliges compartir. "
        "La confianza suele aumentar cuando puedes relacionarte desde la apertura, descubrir nuevas formas de belleza y ampliar tu experiencia a través del encuentro con otras personas.\n\n"

        "Cuando ambas partes colaboran, aparece generosidad afectiva, capacidad para disfrutar de lo que la vida ofrece y una disposición natural a crear relaciones que favorezcan el desarrollo mutuo.\n\n"

        "Esta combinación te invita a observar si identificas el bienestar con tener siempre más, recibir aprobación o evitar cualquier incomodidad. "
        "Disfrutar no exige ignorar los límites ni convertir cada deseo en una necesidad."
    ),

    "Marte": (
        "Tu impulso de actuar está conectado con la necesidad de crecer, explorar y avanzar hacia objetivos que tengan sentido para ti. "
        "Cuando confías en una posibilidad, es habitual que aparezca también la energía necesaria para perseguirla.\n\n"

        "Cuando ambas partes colaboran, puedes actuar con entusiasmo, asumir desafíos y movilizar recursos con una gran convicción. "
        "Tu iniciativa se fortalece cuando existe una dirección amplia que orienta el esfuerzo.\n\n"

        "Esta combinación te invita a observar cuánto espacio existe entre la confianza y la acción. "
        "Creer que algo es posible no significa que debas hacerlo todo, hacerlo de inmediato o asumir riesgos que superen tus recursos actuales."
    ),

    "Saturno": (
        "Tu necesidad de crecer mantiene un diálogo constante con la parte de ti que busca estructura, prudencia y resultados sostenibles. "
        "Una función amplía las posibilidades; la otra comprueba qué puede sostenerse realmente en el tiempo.\n\n"

        "Cuando ambas partes colaboran, puedes convertir una visión amplia en un proyecto concreto, desarrollar confianza a través de la experiencia y avanzar sin perder de vista las responsabilidades que has asumido.\n\n"

        "Esta combinación te invita a evitar dos extremos: limitarte antes de haberlo intentado o expandirte sin una base capaz de sostener lo que inicias. "
        "El crecimiento se vuelve más sólido cuando la esperanza acepta trabajar con la realidad."
    ),

    "Urano": (
        "Tu forma de crecer está conectada con la necesidad de descubrir perspectivas nuevas y cuestionar aquello que se ha quedado pequeño. "
        "La confianza aumenta cuando puedes pensar con independencia, explorar alternativas y abrir caminos que no estaban previstos.\n\n"

        "Cuando ambas partes colaboran, aparece una gran capacidad para reconocer oportunidades de cambio, comprender tendencias colectivas y ampliar la visión de otras personas mediante ideas innovadoras.\n\n"

        "Esta combinación te invita a observar cuándo la búsqueda de libertad favorece tu desarrollo y cuándo te lleva a abandonar procesos antes de haber descubierto todo lo que podían ofrecerte. "
        "No toda expansión necesita romper con lo anterior."
    ),

    "Neptuno": (
        "Tu búsqueda de sentido está conectada con la sensibilidad, la imaginación y la percepción de una realidad más amplia que la experiencia inmediata. "
        "Necesitas confiar en que la vida contiene significados que no siempre pueden comprenderse únicamente desde la lógica.\n\n"

        "Cuando ambas partes colaboran, puedes desarrollar una visión compasiva, inspiradora y capaz de encontrar posibilidades incluso en situaciones inciertas. "
        "La creatividad, la contemplación o la dimensión simbólica pueden convertirse en fuentes importantes de crecimiento.\n\n"

        "Esta combinación te invita a diferenciar entre una confianza profunda y la tendencia a creer aquello que deseas que sea cierto. "
        "La inspiración encuentra una base más segura cuando convive con el discernimiento y la observación de los hechos."
    ),

    "Plutón": (
        "Tu forma de crecer está relacionada con experiencias que transforman profundamente tu manera de comprender la vida. "
        "No siempre encuentras sentido en respuestas simples: necesitas explorar las motivaciones, los conflictos y los procesos que operan bajo la superficie.\n\n"

        "Cuando ambas partes colaboran, desarrollas una gran capacidad para encontrar recursos en momentos críticos, ampliar tu comprensión psicológica y convertir experiencias intensas en una fuente de conocimiento.\n\n"

        "Esta combinación te invita a observar si la necesidad de transformación te lleva a buscar constantemente experiencias extremas o verdades definitivas. "
        "Crecer no siempre exige atravesar una crisis; también puede implicar integrar con profundidad lo que ya has comprendido."
    ),

    "Ascendente": (
        "Cuando Júpiter y el Ascendente interactúan, tu forma de crecer, confiar y ampliar horizontes influye directamente en la manera en que te presentas ante la vida. "
        "Es posible que transmitas apertura, entusiasmo o una sensación de posibilidades que otras personas perciben con facilidad.\n\n"

        "Esta combinación invita a desarrollar una presencia capaz de inspirar sin necesidad de exagerar, convencer o ocupar más espacio del necesario. "
        "La confianza se vuelve más auténtica cuando refleja una experiencia interior y no únicamente una imagen de seguridad."
    ),

    "Nodo Norte": (
        "Cuando Júpiter y el Nodo Norte se relacionan, ampliar tu perspectiva, desarrollar confianza y encontrar un sentido propio adquiere una importancia especial en tu proceso de crecimiento. "
        "Las experiencias que te sacan de una visión limitada pueden ayudarte a descubrir recursos que todavía no habías reconocido.\n\n"

        "Esta combinación recuerda que avanzar no consiste únicamente en buscar más oportunidades. "
        "También implica revisar las creencias desde las que interpretas la vida y elegir aquellas que realmente favorecen tu desarrollo."
    ),

    "Nodo Sur": (
        "Cuando Júpiter y el Nodo Sur interactúan, existe una forma conocida de buscar sentido, confiar o interpretar la realidad a la que puedes recurrir con facilidad. "
        "Tus creencias, conocimientos o experiencias acumuladas pueden convertirse en una fuente importante de orientación.\n\n"

        "Esta combinación invita a utilizar esa visión como un recurso sin asumir que contiene todas las respuestas. "
        "Lo que ya sabes alcanza una nueva profundidad cuando permanece abierto a ser revisado, ampliado y actualizado."
    ),

    "Quirón": (
        "Cuando Júpiter y Quirón se relacionan, la confianza, las creencias o la capacidad de encontrar sentido pueden estar atravesadas por experiencias que dejaron una sensación de pérdida, insuficiencia o desorientación. "
        "Puede resultarte difícil confiar plenamente en la vida o sentir que tus posibilidades son tan amplias como las de otras personas.\n\n"

        "Con el tiempo, aquello que cuestionó tu confianza puede ayudarte a desarrollar una visión más humana, realista y comprensiva del crecimiento. "
        "Esta combinación recuerda que no necesitas mantener una actitud optimista en todo momento para conservar la esperanza."
    ),

    "Lilith": (
        "Cuando Júpiter y Lilith interactúan, tu búsqueda de sentido puede llevarte a cuestionar creencias, normas o discursos que no representan tu experiencia. "
        "Existe una necesidad de ampliar la mirada hacia territorios que suelen quedar fuera de lo aceptado o de lo que otras personas consideran razonable.\n\n"

        "Esta combinación puede aportar valentía para sostener una visión propia y reconocer posibilidades donde antes solo había prohibiciones o juicios.\n\n"

        "También te invita a observar cuándo la necesidad de defender tu verdad se convierte en rigidez, superioridad o rechazo automático de cualquier límite. "
        "Una visión libre gana profundidad cuando puede seguir dialogando con perspectivas diferentes."
    ),
}

JUPITER_TEXTOS_TIPO_ASPECTO = {

    "Conjunción": (
        "Júpiter se encuentra muy unido a esta parte de ti, de modo que tu forma de crecer, confiar y buscar sentido tiende a expresarse a través de ella. "
        "Ambas funciones participan simultáneamente en muchas de tus decisiones y pueden resultar difíciles de separar.\n\n"

        "Esta unión amplifica la experiencia y concede una presencia importante a todo lo relacionado con esta combinación. "
        "Puede aportar entusiasmo, amplitud y una fuerte necesidad de desarrollo, aunque también favorecer que algunas posibilidades se exageren o se den por seguras demasiado pronto.\n\n"

        "El equilibrio aparece cuando reconoces qué aporta cada función por separado. "
        "Así puedes utilizar la confianza como una fuerza de crecimiento sin perder la capacidad de valorar la realidad, los límites y los recursos disponibles."
    ),

    "Sextil": (
        "Júpiter mantiene con esta parte de ti una relación que facilita el aprendizaje, la apertura y el desarrollo de nuevos recursos. "
        "La posibilidad de colaboración está disponible, aunque necesita oportunidades concretas para desplegarse plenamente.\n\n"

        "Cuando activas esta conexión de forma consciente, puedes ampliar tu perspectiva y descubrir maneras más constructivas de utilizar ambas funciones. "
        "La confianza crece a través de la práctica, el intercambio y la disposición a explorar posibilidades que al principio quizá no resultaban evidentes.\n\n"

        "El aprendizaje consiste en no dejar esta facilidad únicamente como una posibilidad. "
        "Cuanto más la incorporas a tus decisiones cotidianas, más puede convertirse en un apoyo real para tu desarrollo."
    ),

    "Trígono": (
        "Júpiter y esta parte de ti tienden a colaborar de manera espontánea. "
        "Existe una facilidad natural para encontrar sentido, confiar en tus recursos y ampliar las posibilidades relacionadas con ambas funciones.\n\n"

        "Esta fluidez puede ayudarte a desenvolverte con optimismo y a reconocer oportunidades con rapidez. "
        "También es posible que aquello que se te da con naturalidad pase inadvertido o que confíes en que siempre estará disponible sin necesidad de desarrollarlo.\n\n"

        "El equilibrio consiste en reconocer esta capacidad y darle una dirección consciente. "
        "La facilidad se convierte en un recurso más sólido cuando la acompañas de criterio, constancia y atención a sus efectos reales."
    ),

    "Cuadratura": (
        "Júpiter y esta parte de ti no siempre encuentran con facilidad una dirección común. "
        "La necesidad de crecer, confiar o ampliar horizontes puede entrar en conflicto con otras necesidades internas, generando exceso, dudas o decisiones difíciles de sostener.\n\n"

        "En algunos momentos puedes avanzar más de lo que tus recursos permiten; en otros, la tensión puede hacer que cuestiones tus posibilidades o que busques respuestas demasiado amplias para resolver una dificultad concreta.\n\n"

        "Esta fricción te impulsa a construir una confianza más consciente. "
        "El aprendizaje consiste en desarrollar sin exagerar, ampliar sin dispersarte y encontrar una forma de crecer que también pueda sostenerse en la realidad."
    ),

    "Oposición": (
        "Júpiter y esta parte de ti buscan un equilibrio que no siempre resulta inmediato. "
        "Es posible que alternes entre confiar plenamente en tus posibilidades y sentir que la seguridad, el sentido o las oportunidades dependen de personas y circunstancias externas.\n\n"

        "También puedes encontrarte con relaciones o situaciones que reflejan cualidades que todavía estás desarrollando en ti: una visión más amplia, una mayor confianza o una forma diferente de interpretar la experiencia.\n\n"

        "El aprendizaje consiste en recuperar para ti lo que inicialmente reconoces fuera. "
        "Cuando ambas funciones pueden dialogar, la expansión deja de vivirse como un extremo y empieza a integrar perspectivas distintas sin perder tu propio criterio."
    ),

    "Quincuncio": (
        "La relación entre Júpiter y esta parte de ti requiere ajustes frecuentes. "
        "Tu necesidad de crecer, confiar o encontrar sentido no siempre parece compatible con la manera en que funciona la otra energía, y puede costarte identificar de dónde procede la incomodidad.\n\n"

        "Es posible que una expectativa demasiado amplia necesite adaptarse a circunstancias concretas, o que una parte de ti avance mientras la otra todavía no dispone de los recursos necesarios para acompañarla.\n\n"

        "El aprendizaje se construye mediante pequeñas correcciones y una observación precisa de tus límites, creencias y decisiones. "
        "Con el tiempo puedes desarrollar una forma muy personal de ampliar tu vida sin desatender aquello que necesita más cuidado o adaptación."
    ),
}


JUPITER_INTEGRACION = {

    "necesidades": {
        "titulo": "Lo que Júpiter necesita",

        "texto": (
            "Cada Júpiter encuentra una forma diferente de crecer, confiar y ampliar su perspectiva, "
            "pero todos comparten una misma necesidad: sentir que la vida puede abrirse más allá de lo conocido.\n\n"

            "Júpiter necesita experiencias que permitan aprender, descubrir posibilidades y conectar lo vivido con un significado más amplio. "
            "Necesita sentir que existe una dirección, aunque todavía no pueda ver con claridad todo el recorrido.\n\n"

            "No toda expansión alimenta a Júpiter. Acumular experiencias, conocimientos o proyectos no siempre produce crecimiento. "
            "Con frecuencia necesita tiempo para integrar lo aprendido, revisar sus creencias y distinguir entre aquello que realmente amplía la vida y aquello que únicamente la llena de actividad.\n\n"

            "Cuando respetas la forma en que construyes confianza y encuentras sentido, Júpiter deja de buscar constantemente una respuesta fuera y recupera su capacidad para reconocer posibilidades dentro de la realidad que ya estás viviendo."
        )
    },

    "cuidar": {
        "titulo": "Cómo cuidar tu Júpiter",

        "texto": (
            "Cuidar de Júpiter no significa pensar en positivo ni buscar continuamente nuevas experiencias. "
            "Significa crear las condiciones para que puedas crecer sin perder contacto con la realidad.\n\n"

            "Júpiter se fortalece cuando aprendes algo que amplía tu mirada, compartes ideas que te inspiran, exploras un entorno diferente o te permites imaginar posibilidades que antes no habías considerado.\n\n"

            "También necesita medida. Cuando todo parece posible, puede resultar difícil reconocer qué merece realmente tu energía, tu tiempo y tu compromiso. "
            "Elegir una dirección no limita necesariamente el crecimiento: muchas veces es lo que permite que una posibilidad llegue a desarrollarse.\n\n"

            "Cuidar esta función implica revisar las creencias desde las que tomas decisiones. "
            "No todas las ideas que te ayudaron en otro momento siguen siendo adecuadas hoy, y no toda expectativa necesita convertirse en un objetivo."
        )
    },

    "equilibrio": {
        "titulo": "Cuando Júpiter encuentra equilibrio",

        "texto": (
            "Cuando Júpiter funciona de manera equilibrada, la confianza no depende de que todo salga bien. "
            "Nace de la sensación de que puedes aprender, adaptarte y encontrar recursos incluso cuando el camino no responde exactamente a lo que esperabas.\n\n"

            "Existe apertura sin dispersión, entusiasmo sin exceso y capacidad para reconocer oportunidades sin convertir cada posibilidad en una obligación.\n\n"

            "Puedes mirar una situación concreta sin perder de vista el conjunto, mantener la esperanza sin negar las dificultades y compartir tu visión sin asumir que debe ser válida para todo el mundo.\n\n"

            "No significa vivir con certeza permanente. "
            "Significa conservar una relación suficientemente amplia con la vida como para que la duda, el error y los cambios de dirección también puedan formar parte del crecimiento."
        )
    },

    "desregulacion": {
        "titulo": "Cuando Júpiter pierde equilibrio",

        "texto": (
            "Cuando Júpiter pierde equilibrio, la necesidad de crecer puede convertirse en exceso.\n\n"

            "Puede aparecer la tendencia a asumir más de lo que puedes sostener, confiar en que las dificultades se resolverán por sí solas o perseguir continuamente nuevas posibilidades sin terminar de desarrollar ninguna.\n\n"

            "En otras ocasiones ocurre lo contrario: se pierde la confianza, el horizonte se estrecha y resulta difícil encontrar sentido o imaginar que algo pueda cambiar. "
            "También puede surgir rigidez alrededor de ciertas creencias, como si cuestionarlas pusiera en riesgo toda la estructura desde la que comprendes la vida.\n\n"

            "No significa que hayas perdido tu capacidad para crecer. "
            "Con frecuencia indica que necesitas revisar la distancia entre tus expectativas, tus recursos actuales y la realidad concreta desde la que estás intentando avanzar."
        )
    },

    "pregunta": {
        "titulo": "Una pregunta para observarte",

        "texto": (
            "Mientras leías este capítulo quizá has reconocido formas habituales de buscar sentido, confiar o ampliar tu vida. "
            "También es posible que algunas aparezcan solo en determinados momentos o ámbitos.\n\n"

            "Más allá de la posición de Júpiter en tu carta, la pregunta importante es otra:\n\n"

            "¿Qué está ampliando realmente tu vida en este momento?\n\n"

            "Puede ser un aprendizaje, una conversación, una decisión, un cambio de perspectiva o la posibilidad de mirar de otra manera algo que ya conocías.\n\n"

            "También puede ayudarte observar qué expectativas ocupan mucho espacio sin ofrecer un crecimiento real. "
            "Distinguir entre expansión y exceso es una forma de utilizar tu energía con mayor consciencia."
        )
    },

    "integracion": {
        "titulo": "Integración",

        "texto": (
            "Crecer no consiste únicamente en llegar más lejos.\n\n"

            "También implica ampliar la manera en que comprendes lo vivido, revisar las creencias que orientan tus decisiones y reconocer recursos que antes no sabías que estaban disponibles.\n\n"

            "Conocer tu Júpiter no pretende decirte dónde encontrarás suerte ni asegurar que determinadas experiencias serán fáciles. "
            "Pretende ayudarte a comprender cómo construyes confianza, qué tipo de experiencias amplían tu perspectiva y en qué momentos la necesidad de expansión puede llevarte a perder medida o dirección.\n\n"

            "Cada vez que una experiencia modifica tu manera de interpretar la vida, algo dentro de ti encuentra más espacio.\n\n"

            "Porque la forma en que creces también determina cuánto puede ampliarse la arquitectura desde la que construyes tu vida."
        )
    }
}

# ─── TEXTOS: SATURNO ─────────────────────────────────────────────
SATURNO_SIGNO = {

"Aries":
"""Necesitas aprender a construir tu propia autoridad sin depender únicamente del impulso. Saturno en Aries te invita a desarrollar una forma de actuar que combine iniciativa con responsabilidad.

Es habitual que la afirmación personal requiera tiempo y experiencia. Con frecuencia descubres que la verdadera fortaleza no consiste en reaccionar rápidamente, sino en decidir con claridad hacia dónde dirigir tu energía.

Cuando esta función pierde equilibrio puedes frenar tus iniciativas por miedo a equivocarte o, por el contrario, actuar con rigidez para demostrar que eres capaz.

La estabilidad aparece cuando comprendes que no necesitas demostrar constantemente tu fuerza. La verdadera confianza nace de sostener aquello que decides comenzar.""",

"Tauro":
"""Necesitas construir seguridad sobre bases reales y duraderas. Saturno en Tauro busca desarrollar recursos que puedan sostenerse con el paso del tiempo y ofrecer una sensación de estabilidad profunda.

Tiendes a valorar la constancia, la paciencia y todo aquello que puede consolidarse mediante esfuerzo continuado. Los procesos lentos suelen enseñarte más que los resultados inmediatos.

Cuando esta función pierde equilibrio puede aparecer resistencia al cambio, miedo a perder lo construido o dificultad para asumir riesgos necesarios para seguir creciendo.

Recuperas el equilibrio cuando descubres que la estabilidad no depende únicamente de conservar lo que tienes, sino también de confiar en tu capacidad para reconstruir cuando sea necesario.""",

"Géminis":
"""Necesitas desarrollar una forma de pensar clara, estructurada y coherente. Saturno en Géminis invita a construir conocimiento sólido, distinguiendo aquello que realmente comprendes de lo que simplemente has escuchado.

Es habitual que el aprendizaje requiera tiempo y que valores especialmente las ideas que han sido comprobadas mediante la experiencia.

Cuando esta función pierde equilibrio puedes dudar excesivamente de tus conocimientos, sentir inseguridad al comunicarte o exigirte tener siempre la respuesta correcta antes de expresar una opinión.

La confianza crece cuando permites que el aprendizaje sea un proceso continuo y no una prueba constante de tu capacidad.""",

"Cáncer":
"""Necesitas construir una seguridad emocional que no dependa únicamente de las circunstancias externas. Saturno en Cáncer te invita a desarrollar una base interna capaz de sostenerte incluso en momentos de vulnerabilidad.

Es habitual que aprendas muy pronto el valor del compromiso, el cuidado o la responsabilidad hacia las personas importantes para ti.

Cuando esta función pierde equilibrio puedes asumir más responsabilidades emocionales de las que realmente te corresponden o protegerte tanto que resulte difícil mostrar lo que sientes.

Recuperas el equilibrio cuando descubres que cuidar también incluye permitirte recibir apoyo y reconocer tus propias necesidades.""",

"Leo":
"""Necesitas desarrollar una autoestima que pueda sostenerse más allá del reconocimiento externo. Saturno en Leo invita a construir una expresión personal basada en la autenticidad y no únicamente en la aprobación.

Es habitual que el liderazgo, la creatividad o la visibilidad se conviertan en aprendizajes importantes a lo largo de tu vida.

Cuando esta función pierde equilibrio puedes esconder tus talentos por miedo a la exposición o exigirte demostrar constantemente tu valor mediante logros o reconocimiento.

La estabilidad aparece cuando expresarte deja de ser una forma de buscar validación y se convierte simplemente en una manera honesta de mostrar quién eres.""",

"Virgo":
"""Necesitas construir una vida organizada, funcional y coherente con la realidad cotidiana. Saturno en Virgo desarrolla la capacidad de mejorar, ordenar y asumir responsabilidades de forma práctica.

Tiendes a valorar el trabajo bien hecho, la precisión y los procesos que permiten avanzar paso a paso.

Cuando esta función pierde equilibrio puedes caer en una autoexigencia constante, centrarte únicamente en lo que falta por mejorar o sentir que nunca haces suficiente.

Recuperas el equilibrio cuando comprendes que la excelencia no consiste en eliminar cualquier error, sino en seguir construyendo incluso cuando las cosas no son perfectas.""",

"Libra":
"""Necesitas aprender a construir relaciones equilibradas y compromisos sostenibles. Saturno en Libra invita a desarrollar una forma madura de vincularte, donde exista espacio tanto para la cooperación como para la responsabilidad compartida.

Es habitual que valores la justicia, el diálogo y la búsqueda de acuerdos duraderos.

Cuando esta función pierde equilibrio puedes posponer decisiones importantes para evitar conflictos o asumir más responsabilidad por la relación que la otra persona.

La estabilidad aparece cuando descubres que un vínculo sano también necesita límites claros y una presencia auténtica por parte de ambos.""",

"Escorpio":
"""Necesitas desarrollar una relación madura con el cambio, la pérdida y la transformación. Saturno en Escorpio invita a construir fortaleza allí donde la vida exige atravesar procesos profundos.

Es habitual que desarrolles una gran capacidad para sostener situaciones complejas y comprender aquello que permanece oculto bajo la superficie.

Cuando esta función pierde equilibrio puedes intentar controlar excesivamente las situaciones, desconfiar con facilidad o resistirte a procesos inevitables de transformación.

Recuperas el equilibrio cuando aceptas que no todo puede controlarse y descubres que la verdadera fortaleza también incluye aprender a soltar.""",

"Sagitario":
"""Necesitas construir una visión de la vida basada en la experiencia y no únicamente en las creencias. Saturno en Sagitario invita a desarrollar un sentido propio que pueda sostenerse frente a la realidad.

Es habitual que cuestiones ideas, filosofías o sistemas de pensamiento hasta encontrar aquello que realmente tiene sentido para ti.

Cuando esta función pierde equilibrio puedes sentir dificultad para confiar en el futuro, exigir certezas imposibles antes de avanzar o aferrarte rígidamente a determinadas creencias.

La estabilidad aparece cuando comprendes que encontrar sentido no consiste en tener todas las respuestas, sino en seguir aprendiendo con apertura y criterio.""",

"Capricornio":
"""Necesitas construir una estructura sólida desde la que desarrollar tus objetivos. Saturno en Capricornio encuentra su fuerza cuando el compromiso, la constancia y la responsabilidad se convierten en herramientas para crear algo duradero.

Tiendes a asumir responsabilidades con naturalidad y a comprender que algunos logros requieren tiempo, disciplina y paciencia.

Cuando esta función pierde equilibrio puedes identificar tu valor únicamente con lo que produces, asumir cargas excesivas o sentir que nunca es suficiente lo conseguido.

Recuperas el equilibrio cuando recuerdas que la estructura está al servicio de la vida y no al revés. Los logros tienen más sentido cuando también pueden disfrutarse.""",

"Acuario":
"""Necesitas aprender a construir libertad de una manera responsable. Saturno en Acuario invita a desarrollar ideas nuevas sin perder el contacto con la realidad y con las personas que las hacen posibles.

Es habitual que cuestiones estructuras establecidas y busques formas diferentes de organizar la vida, los grupos o los proyectos colectivos.

Cuando esta función pierde equilibrio puedes distanciarte emocionalmente, rechazar cualquier norma por principio o sentir que debes hacerlo todo de manera completamente distinta.

La estabilidad aparece cuando descubres que innovar también requiere constancia, colaboración y compromiso con aquello que deseas transformar.""",

"Piscis":
"""Necesitas desarrollar límites claros sin perder sensibilidad. Saturno en Piscis invita a construir una estructura capaz de sostener la intuición, la empatía y el mundo interior sin perderte en ellos.

Es habitual que aprendas a diferenciar poco a poco entre lo que sientes, lo que imaginas y aquello que realmente te corresponde sostener.

Cuando esta función pierde equilibrio puedes sentir dificultad para poner límites, cargar con problemas ajenos o perder claridad cuando las emociones se intensifican.

Recuperas el equilibrio cuando descubres que la sensibilidad necesita estructura para convertirse en un recurso y no en una fuente constante de desgaste."""
}

SATURNO_CASA = {

1:
"""Necesitas construir una identidad sólida y una forma de estar en el mundo que pueda sostenerse con el paso del tiempo. La confianza suele desarrollarse a través de la experiencia, la responsabilidad y el conocimiento progresivo de tus propios límites y capacidades.

Es habitual que asumas la vida con seriedad y que prefieras avanzar sobre bases firmes antes que actuar únicamente por impulso. Con el tiempo puedes desarrollar una gran capacidad para afrontar situaciones complejas con estabilidad.

Cuando esta función pierde equilibrio puedes exigirte demasiado, sentir que siempre debes demostrar tu valía o cargar con responsabilidades que terminan alejándote de tu espontaneidad.

La estabilidad aparece cuando descubres que construir una identidad también implica permitirte aprender, equivocarte y evolucionar sin convertir cada paso en un examen.""",

2:
"""Necesitas desarrollar una relación estable con tus recursos, tus capacidades y aquello que te aporta seguridad. Saturno en esta casa invita a construir una sensación de valor basada en la experiencia y no únicamente en los resultados.

Es habitual que aprendas poco a poco a administrar tus recursos con responsabilidad y que valores especialmente aquello que has conseguido mediante esfuerzo y constancia.

Cuando esta función pierde equilibrio puedes sentir que nunca es suficiente lo que tienes o lo que haces, o medir tu valor únicamente por lo que eres capaz de producir.

Recuperas el equilibrio cuando recuerdas que la verdadera seguridad también nace de confiar en tus capacidades y no solo en aquello que consigues conservar.""",

3:
"""Necesitas construir una forma de pensar clara, ordenada y consistente. La comunicación, el aprendizaje y la manera en que organizas tus ideas forman parte de un proceso de maduración importante.

Es habitual que desarrolles conocimiento de forma progresiva y que prefieras comprender profundamente un tema antes de darlo por aprendido.

Cuando esta función pierde equilibrio puedes dudar de tus propias ideas, sentir dificultad para expresarte con libertad o exigirte una precisión que termina bloqueando la comunicación.

La estabilidad aparece cuando permites que el aprendizaje sea un camino continuo y no una obligación de saber siempre la respuesta correcta.""",

4:
"""Necesitas construir una base emocional capaz de sostenerte a lo largo de la vida. Saturno en esta casa invita a desarrollar un hogar interior donde puedas sentir estabilidad incluso cuando las circunstancias cambian.

Es habitual que cuestiones profundamente qué significa para ti la seguridad, la pertenencia o el cuidado, y que dediques tiempo a construir esos pilares desde dentro.

Cuando esta función pierde equilibrio puedes cargar con responsabilidades familiares excesivas, protegerte emocionalmente en exceso o sentir dificultad para pedir ayuda.

Recuperas el equilibrio cuando comprendes que una base sólida también puede incluir vulnerabilidad, descanso y apoyo compartido.""",

5:
"""Necesitas aprender a expresar tu creatividad y tu individualidad con responsabilidad y autenticidad. Saturno en esta casa invita a construir una forma de disfrutar y crear que no dependa únicamente del reconocimiento externo.

Es habitual que desarrolles tus talentos mediante práctica, paciencia y compromiso, descubriendo que aquello que realmente permanece necesita tiempo para madurar.

Cuando esta función pierde equilibrio puedes contener demasiado tu espontaneidad, sentir miedo a exponerte o creer que solo puedes disfrutar cuando todo está bajo control.

La estabilidad aparece cuando permites que la disciplina y la creatividad trabajen juntas en lugar de enfrentarse.""",

6:
"""Necesitas construir una vida cotidiana que pueda sostenerte a largo plazo. Saturno en esta casa desarrolla la capacidad para organizar responsabilidades, cuidar de tus recursos y asumir compromisos de manera constante.

Es habitual que encuentres satisfacción mejorando procesos, desarrollando habilidades y creando rutinas que aporten estabilidad.

Cuando esta función pierde equilibrio puedes caer en una autoexigencia permanente, sentir que nunca descansas lo suficiente o convertir la productividad en la única medida de tu valor.

Recuperas el equilibrio cuando comprendes que la sostenibilidad también requiere pausas, flexibilidad y cuidado personal.""",

7:
"""Necesitas aprender a construir relaciones basadas en el compromiso, la responsabilidad compartida y el respeto mutuo. Los vínculos importantes suelen convertirse en escenarios de maduración y aprendizaje.

Es habitual que valores especialmente las relaciones que pueden sostenerse con el tiempo y que asumas los acuerdos con seriedad.

Cuando esta función pierde equilibrio puedes permanecer en vínculos únicamente por responsabilidad, exigir demasiado a otras personas o asumir cargas que no te corresponden.

La estabilidad aparece cuando descubres que un compromiso sano también necesita libertad, reciprocidad y límites claros.""",

8:
"""Necesitas desarrollar una relación madura con los cambios profundos, las pérdidas y todo aquello que escapa a tu control. Saturno en esta casa invita a construir fortaleza allí donde la vida exige transformación.

Es habitual que aprendas a sostener procesos intensos con una gran capacidad de resistencia y profundidad.

Cuando esta función pierde equilibrio puedes intentar controlar aquello que inevitablemente cambia, desconfiar de los demás o mantener demasiado tiempo situaciones que ya han cumplido su función.

Recuperas el equilibrio cuando descubres que la verdadera seguridad no consiste en evitar el cambio, sino en confiar en tu capacidad para atravesarlo.""",

9:
"""Necesitas construir una visión de la vida basada en la experiencia, la reflexión y el pensamiento propio. Saturno en esta casa invita a desarrollar creencias que puedan sostenerse más allá del entusiasmo inicial.

Es habitual que cuestiones ideas, filosofías o conocimientos hasta encontrar aquello que realmente resiste el paso del tiempo.

Cuando esta función pierde equilibrio puedes exigir certezas absolutas antes de avanzar, limitar tus posibilidades por miedo a equivocarte o aferrarte rígidamente a determinadas formas de entender la realidad.

La estabilidad aparece cuando comprendes que una visión sólida no necesita ser inamovible para seguir siendo valiosa.""",

10:
"""Necesitas construir una trayectoria coherente con tus responsabilidades y con aquello que consideras importante aportar al mundo. Saturno encuentra aquí uno de sus espacios naturales para desarrollar compromiso, perseverancia y visión de largo plazo.

Es habitual que asumas objetivos importantes y que desarrolles una gran capacidad para sostener proyectos que requieren tiempo y constancia.

Cuando esta función pierde equilibrio puedes identificar tu valor únicamente con el éxito profesional, asumir responsabilidades excesivas o sentir que nunca alcanzas el nivel que esperas de ti.

Recuperas el equilibrio cuando recuerdas que construir una vida también incluye disfrutar del camino y no únicamente alcanzar metas.""",

11:
"""Necesitas construir relaciones, proyectos colectivos e ideales que puedan sostenerse en la realidad. Saturno en esta casa invita a transformar las buenas ideas en compromisos concretos.

Es habitual que selecciones cuidadosamente las personas con las que compartes tus proyectos y que valores especialmente la confianza construida con el tiempo.

Cuando esta función pierde equilibrio puedes sentir una cierta desconexión dentro de los grupos, desconfiar excesivamente de los demás o abandonar ideales porque parecen demasiado difíciles de alcanzar.

La estabilidad aparece cuando descubres que los grandes cambios también necesitan pequeños pasos sostenidos y colaboración constante.""",

12:
"""Necesitas construir una relación consciente con tu mundo interior. Saturno en esta casa invita a desarrollar una estructura que permita contener la sensibilidad, el silencio y los procesos internos sin perderte en ellos.

Es habitual que una parte importante de tu maduración ocurra lejos del reconocimiento externo, a través de procesos de introspección, aceptación y profundo autoconocimiento.

Cuando esta función pierde equilibrio puedes cargar en silencio con preocupaciones, aislarte demasiado o sentir que debes resolver todo sin ayuda.

Recuperas el equilibrio cuando permites que tu mundo interior encuentre espacios seguros donde expresarse y descubres que pedir apoyo también forma parte de una fortaleza madura."""
}


SATURNO_COMBINACIONES = {

    "Sol": (
        "Tu identidad y tu sentido de la responsabilidad mantienen un diálogo constante. "
        "Necesitas construir una imagen de ti basada en la experiencia, el compromiso y aquello que realmente puedes sostener con el paso del tiempo.\n\n"

        "Cuando ambas partes colaboran, desarrollas una gran capacidad para perseverar, asumir responsabilidades y convertir tus objetivos en proyectos sólidos. "
        "La confianza deja de depender únicamente de los resultados y empieza a apoyarse en la persona que has ido construyendo.\n\n"

        "Esta combinación te invita a distinguir entre responsabilidad y autoexigencia. "
        "No necesitas demostrar constantemente tu valor para ocupar tu lugar."
    ),

    "Luna": (
        "Tu mundo emocional y tu necesidad de construir estabilidad están profundamente relacionados. "
        "La seguridad suele aparecer cuando puedes comprender lo que sientes y desarrollar una base emocional suficientemente firme para sostenerte.\n\n"

        "Cuando ambas partes colaboran, puedes afrontar momentos difíciles con serenidad, cuidar de otras personas sin perderte a ti y desarrollar una gran madurez emocional.\n\n"

        "Esta combinación te invita a observar si sostienes demasiado tiempo aquello que te pesa o si te cuesta mostrar vulnerabilidad por miedo a que pueda interpretarse como debilidad. "
        "La fortaleza también incluye permitirte sentir y pedir apoyo cuando lo necesitas."
    ),

    "Mercurio": (
        "Tu manera de pensar busca estructura, coherencia y solidez. "
        "Necesitas ordenar las ideas, comprobar lo que sabes y construir conclusiones que puedan mantenerse con el paso del tiempo.\n\n"

        "Cuando ambas partes colaboran, desarrollas concentración, responsabilidad al comunicar y capacidad para profundizar en conocimientos complejos sin abandonar el proceso a mitad de camino.\n\n"

        "Esta combinación te invita a observar la exigencia con la que juzgas tu propia mente. "
        "No necesitas tener todas las respuestas ni expresarte de forma perfecta para que tus palabras tengan valor."
    ),

    "Venus": (
        "Tu forma de vincularte y aquello que valoras buscan estabilidad, compromiso y continuidad. "
        "Las relaciones y los afectos adquieren profundidad cuando pueden sostenerse sobre bases reales y no únicamente sobre la emoción del momento.\n\n"

        "Cuando ambas partes colaboran, desarrollas lealtad, constancia y una capacidad especial para construir vínculos duraderos. "
        "También puedes aprender a valorar aquello que realmente permanece con el paso del tiempo.\n\n"

        "Esta combinación te invita a observar si identificas el amor con la responsabilidad o si te cuesta disfrutar cuando todo no está completamente bajo control. "
        "El compromiso no necesita eliminar la ligereza ni la ternura."
    ),

    "Marte": (
        "Tu forma de actuar está estrechamente relacionada con la disciplina, la planificación y la capacidad para sostener el esfuerzo. "
        "Necesitas sentir que tu energía tiene una dirección clara y un propósito que justifique el trabajo realizado.\n\n"

        "Cuando ambas partes colaboran, puedes desarrollar una enorme perseverancia, afrontar proyectos complejos y mantener el esfuerzo incluso cuando los resultados tardan en aparecer.\n\n"

        "Esta combinación te invita a distinguir entre actuar con constancia y exigirte más de lo que realmente puedes sostener. "
        "La disciplina resulta más eficaz cuando también respeta tus ritmos."
    ),

    "Júpiter": (
        "Tu necesidad de crecer mantiene un diálogo constante con la parte de ti que busca estructura, prudencia y resultados sostenibles. "
        "Una función amplía las posibilidades; la otra comprueba qué puede sostenerse realmente en el tiempo.\n\n"

        "Cuando ambas partes colaboran, puedes convertir una visión amplia en un proyecto concreto, desarrollar confianza a través de la experiencia y avanzar sin perder de vista las responsabilidades que has asumido.\n\n"

        "Esta combinación te invita a evitar dos extremos: limitarte antes de haberlo intentado o expandirte sin una base capaz de sostener lo que inicias. "
        "El crecimiento se vuelve más sólido cuando la esperanza acepta trabajar con la realidad."
    ),

    "Urano": (
        "Tu necesidad de construir estabilidad convive con una parte de ti que busca innovación, libertad y cambio. "
        "Puede parecer que ambas funciones avanzan en direcciones distintas, aunque en realidad ambas intentan ayudarte a evolucionar.\n\n"

        "Cuando colaboran, puedes desarrollar estructuras flexibles, introducir mejoras duraderas y transformar aquello que ya no funciona sin destruir lo que sigue siendo valioso.\n\n"

        "Esta combinación te invita a no elegir entre estabilidad o cambio. "
        "Las transformaciones más profundas suelen aparecer cuando ambas pueden trabajar juntas."
    ),

    "Neptuno": (
        "Tu necesidad de construir una estructura sólida se relaciona con una parte de ti que percibe la vida desde la sensibilidad, la intuición y la imaginación. "
        "El reto consiste en permitir que ambas funciones se enriquezcan mutuamente.\n\n"

        "Cuando colaboran, puedes convertir ideales en realidades, dar forma a proyectos inspiradores y desarrollar una espiritualidad o una creatividad capaces de integrarse en la vida cotidiana.\n\n"

        "Esta combinación te invita a observar cuándo intentas controlar lo que necesita ser sentido y cuándo confías en algo sin darle una base suficiente. "
        "La sensibilidad encuentra más fuerza cuando dispone de una estructura que la sostenga."
    ),

    "Plutón": (
        "Tu forma de construir estabilidad está profundamente relacionada con los procesos de transformación. "
        "Las experiencias intensas pueden convertirse en oportunidades para desarrollar una fortaleza mucho más profunda que la basada únicamente en el control.\n\n"

        "Cuando ambas partes colaboran, desarrollas una enorme capacidad para sostener cambios difíciles, reconstruirte después de las pérdidas y crear estructuras mucho más auténticas.\n\n"

        "Esta combinación te invita a observar cuándo la necesidad de controlar impide que aparezca una transformación necesaria. "
        "La verdadera estabilidad también sabe adaptarse a aquello que cambia."
    ),

    "Ascendente": (
        "Cuando Saturno y el Ascendente colaboran, la manera en que te presentas al mundo transmite solidez, responsabilidad y una presencia que suele generar confianza. "
        "Es posible que otras personas perciban en ti una actitud seria o comprometida incluso antes de conocerte en profundidad.\n\n"

        "Esta combinación invita a construir una forma de estar en el mundo que refleje tu verdadera madurez sin convertir la responsabilidad en una carga permanente. "
        "La firmeza también puede convivir con la cercanía y la naturalidad."
    ),

    "Nodo Norte": (
        "Cuando Saturno y el Nodo Norte se relacionan, desarrollar estructura, responsabilidad y compromiso forma parte importante de tu proceso de crecimiento. "
        "Las experiencias que exigen constancia suelen convertirse en escenarios donde aparece una parte esencial de tu evolución.\n\n"

        "Esta combinación recuerda que avanzar no siempre significa hacerlo más rápido. "
        "Con frecuencia consiste en construir paso a paso una base suficientemente sólida para sostener aquello que realmente deseas desarrollar."
    ),

    "Nodo Sur": (
        "Cuando Saturno y el Nodo Sur interactúan, existe una tendencia natural a apoyarte en formas conocidas de asumir responsabilidades, organizar tu vida o afrontar las dificultades. "
        "Esa experiencia puede convertirse en un gran recurso cuando permanece abierta al cambio.\n\n"

        "Esta combinación invita a reconocer todo lo que ya sabes sostener sin convertirlo en la única manera posible de hacer las cosas. "
        "La experiencia alcanza su mayor valor cuando sigue evolucionando."
    ),

    "Quirón": (
        "Cuando Saturno y Quirón se relacionan, la responsabilidad, la autoridad o la sensación de no ser suficiente pueden convertirse en temas especialmente sensibles. "
        "Es posible que determinadas experiencias hayan dejado la impresión de tener que esforzarte más que otras personas para reconocer tu propio valor.\n\n"

        "Con el tiempo, aquello que un día viviste como una limitación puede ayudarte a desarrollar una enorme capacidad para acompañar procesos de crecimiento con realismo, paciencia y comprensión.\n\n"

        "Esta combinación recuerda que la madurez no consiste en dejar de ser vulnerable. "
        "Consiste en aprender a sostener esa vulnerabilidad con respeto hacia ti."
    ),

    "Lilith": (
        "Cuando Saturno y Lilith interactúan, aparecen preguntas importantes sobre los límites, las normas y la autoridad. "
        "Puede existir una necesidad profunda de revisar aquello que consideras obligatorio y diferenciar entre las estructuras que realmente te sostienen y aquellas que simplemente has heredado.\n\n"

        "Esta combinación puede aportar una gran capacidad para construir una autoridad propia, basada en la experiencia y no únicamente en las expectativas externas.\n\n"

        "También te invita a observar cuándo el rechazo de cualquier norma termina convirtiéndose en otra forma de rigidez. "
        "La verdadera libertad puede incluir elegir conscientemente las estructuras que deseas mantener."
    ),
}

SATURNO_TEXTOS_TIPO_ASPECTO = {
    "Conjunción": (
        "Ambas funciones actúan de manera muy unida. "
        "La experiencia de Saturno se mezcla directamente con la del otro planeta, "
        "de modo que sus necesidades, tensiones y recursos tienden a expresarse como una sola dinámica."
    ),

    "Sextil": (
        "Existe una colaboración natural entre ambas funciones. "
        "La relación puede facilitar que la estructura, la responsabilidad y la capacidad de sostener "
        "se desarrollen de una manera más flexible y consciente."
    ),

    "Trígono": (
        "Ambas funciones tienden a integrarse con facilidad. "
        "Saturno puede aportar estabilidad, constancia y madurez sin que el proceso se viva necesariamente "
        "como una exigencia permanente."
    ),

    "Cuadratura": (
        "Entre ambas funciones puede aparecer una tensión que exige ajustes. "
        "La necesidad de control, seguridad o estructura puede entrar en conflicto con la forma de actuar "
        "del otro planeta, generando bloqueos, presión o sensación de insuficiencia."
    ),

    "Oposición": (
        "Las dos funciones pueden sentirse separadas o enfrentadas. "
        "El aprendizaje consiste en encontrar una forma de atender ambas sin identificarse por completo "
        "con uno de los extremos."
    ),

    "Quincuncio": (
        "La relación entre ambas funciones requiere ajustes continuos. "
        "Puede resultar difícil encontrar una forma estable de coordinarlas, por lo que será necesario "
        "revisar expectativas, ritmos y responsabilidades."
    ),
}

SATURNO_INTEGRACION = {

    "necesidades": {
        "titulo": "Lo que Saturno necesita",

        "texto": (
            "Cada Saturno construye la estabilidad de una manera diferente, "
            "pero todos comparten una misma necesidad: desarrollar una estructura capaz de sostener la vida con el paso del tiempo.\n\n"

            "Saturno necesita compromiso, continuidad y experiencias que permitan convertir el aprendizaje en algo sólido. "
            "No busca resultados inmediatos, sino construir recursos internos que permanezcan cuando las circunstancias cambian.\n\n"

            "No toda responsabilidad fortalece a Saturno. Cargar con más peso del que realmente te corresponde, exigirte constantemente o intentar controlarlo todo suele producir el efecto contrario. "
            "Con frecuencia necesita distinguir entre aquello que puedes sostener y aquello que no depende de ti.\n\n"

            "Cuando respetas el ritmo con el que maduras y construyes tu propia autoridad, Saturno deja de vivir la responsabilidad como una carga y recupera su capacidad para ofrecer estabilidad, criterio y confianza."
        )
    },

    "cuidar": {
        "titulo": "Cómo cuidar tu Saturno",

        "texto": (
            "Cuidar de Saturno no significa exigirte más ni asumir nuevas responsabilidades. "
            "Significa crear una estructura que realmente pueda sostener tu vida.\n\n"

            "Saturno encuentra equilibrio cuando existen límites claros, compromisos realistas y tiempo suficiente para desarrollar aquello que es importante sin vivir en una sensación permanente de urgencia.\n\n"

            "También necesita descanso. Una estructura que nunca se detiene termina perdiendo flexibilidad y acaba sosteniéndose únicamente por esfuerzo. "
            "La estabilidad no depende de hacer más, sino de encontrar un ritmo que puedas mantener sin agotarte.\n\n"

            "Cuidar esta función implica revisar aquello que consideras una obligación. "
            "No toda responsabilidad es realmente tuya, y no todo lo importante necesita resolverse de inmediato."
        )
    },

    "equilibrio": {
        "titulo": "Cuando Saturno encuentra equilibrio",

        "texto": (
            "Cuando Saturno funciona de manera equilibrada, la responsabilidad deja de sentirse como un peso para convertirse en una fuente de estabilidad.\n\n"

            "Existe paciencia para construir paso a paso, capacidad para asumir compromisos sin perder de vista tus propios límites y una relación más serena con el esfuerzo.\n\n"

            "Puedes diferenciar aquello que depende de ti de lo que no, sostener procesos largos sin necesidad de obtener resultados inmediatos y confiar en que las estructuras sólidas necesitan tiempo para consolidarse.\n\n"

            "No significa vivir sin dificultades ni hacerlo todo perfectamente. "
            "Significa desarrollar una confianza tranquila en tu capacidad para afrontar la realidad con criterio, constancia y flexibilidad."
        )
    },

    "desregulacion": {
        "titulo": "Cuando Saturno pierde equilibrio",

        "texto": (
            "Cuando Saturno pierde equilibrio, la estructura puede convertirse en rigidez.\n\n"

            "Puede aparecer una autoexigencia constante, la sensación de que nunca es suficiente lo que haces o la necesidad de controlar todos los detalles para sentir seguridad. "
            "En otras ocasiones surge el efecto contrario: cuesta asumir responsabilidades, se posponen decisiones importantes o aparece una sensación de bloqueo ante cualquier desafío.\n\n"

            "No significa que exista un problema en tu capacidad para sostener la vida. "
            "Con frecuencia indica que llevas demasiado tiempo funcionando desde la obligación, el miedo al error o unas expectativas que ya no responden a la realidad actual.\n\n"

            "Recuperar el equilibrio no consiste en eliminar la responsabilidad, sino en construir una relación más consciente y más amable con ella."
        )
    },

    "pregunta": {
        "titulo": "Una pregunta para observarte",

        "texto": (
            "Mientras leías este capítulo quizá has reconocido distintas formas de asumir responsabilidades, poner límites o construir estabilidad. "
            "También es posible que algunas solo aparezcan en determinados momentos de tu vida.\n\n"

            "Más allá de la posición de Saturno en tu carta, la pregunta importante es otra:\n\n"

            "¿Qué necesita hoy tu vida para sentirse verdaderamente sostenida?\n\n"

            "Puede ser un límite, una decisión pendiente, una conversación, pedir ayuda o permitirte descansar después de un largo periodo de esfuerzo.\n\n"

            "Observar esa necesidad con honestidad puede ayudarte a diferenciar entre aquello que realmente fortalece tu estructura y aquello que simplemente mantiene una carga que ya no necesitas seguir sosteniendo."
        )
    },

    "integracion": {
        "titulo": "Integración",

        "texto": (
            "Construir una vida no consiste únicamente en avanzar.\n\n"

            "También implica desarrollar una estructura capaz de sostener lo que eres, lo que haces y todo aquello que deseas construir con el paso del tiempo.\n\n"

            "Conocer tu Saturno no pretende decirte dónde encontrarás dificultades ni qué deberías hacer. "
            "Pretende ayudarte a comprender cómo desarrollas estabilidad, qué tipo de responsabilidades favorecen tu crecimiento, dónde aparecen los límites que necesitas construir y de qué manera puedes fortalecer tu propia autoridad.\n\n"

            "Cada compromiso que eliges conscientemente contribuye a crear una base más sólida desde la que vivir.\n\n"

            "Porque la forma en que sostienes tu vida también forma parte de la arquitectura desde la que construyes todo lo demás."
        )
    }
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


def calcular_aspectos_planetas_sociales(planetas, asc):
    return calcular_aspectos_modulo(
        planetas,
        asc,
        ("Júpiter", "Saturno"),
    )


# ─── RUEDA SIMPLIFICADA: JÚPITER + SATURNO ───────────────────────────────────

def dibujar_rueda_planetas_sociales(carta, aspectos, archivo_salida):
    """
    Rueda focal de Planetas Sociales.

    Muestra Júpiter y Saturno, junto con los planetas,
    Nodos o ángulos con los que forman aspectos.
    """

    planetas = carta["planetas"]
    cuspides = carta["cuspides"]
    asc_lon = carta["asc"]["lon"]

    planetas_focales = {
        "Júpiter",
        "Saturno",
    }

    # Conserva solamente los aspectos en los que participa
    # Júpiter o Saturno.
    aspectos_sociales = [
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
    for aspecto in aspectos_sociales:
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

    # Júpiter y Saturno siempre aparecen.
    nombres_visibles = {
        "Júpiter",
        "Saturno",
    }

    # Añadimos todos los cuerpos que estén aspectados
    # con alguno de los dos planetas sociales.
    for aspecto in aspectos_sociales:
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

    # Ordenamos por longitud para que la distribución sea más estable
    # y no dependa del orden interno del conjunto.
    puntos_ordenados = sorted(
        puntos.items(),
        key=lambda item: item[1]["lon"],
    )

    for nombre, p in puntos_ordenados:
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
    for nombre, p in puntos_ordenados:
        ang = lon_a_angulo(p["lon"])
        r = radios[nombre]

        color = COLORES_PLANETA.get(
            nombre,
            "#333",
        )

        simbolo = p["simbolo"]

        # Júpiter y Saturno quedan ligeramente destacados.
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


def bloque_portada_sociales(
    nombre,
    fecha_str,
    hora_str,
    ciudad,
    estilos,
):
    return [
        Spacer(1, 1.7 * cm),

        Paragraph(
            "Planetas Sociales",
            estilos["titulo"],
        ),

        Paragraph(
            "Júpiter · Saturno",
            estilos["centro"],
        ),

        Spacer(1, 0.45 * cm),

        Paragraph(
            "Una lectura sobre cómo amplías tu perspectiva y cómo construyes una estructura capaz de sostener ese crecimiento.",
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


def bloque_bienvenida_sociales(estilos):

    texto = (
        "Hay momentos en los que la vida te invita a ampliar horizontes, aprender algo nuevo o abrirte a posibilidades que antes no contemplabas. "
        "Y hay otros en los que lo importante no es crecer más, sino construir una estructura capaz de sostener todo lo que ya has desarrollado. "
        "Ambos movimientos forman parte de una misma arquitectura interna.\n\n"

        "En este informe recorrerás dos funciones fundamentales. Júpiter representa la capacidad para ampliar la perspectiva, encontrar sentido a la experiencia y desarrollar confianza en la vida. "
        "Saturno muestra cómo construyes estabilidad, cómo asumes responsabilidades y de qué manera desarrollas una estructura que pueda sostenerse con el paso del tiempo.\n\n"

        "Ninguna de estas funciones actúa de forma aislada. La expansión necesita una base firme para no dispersarse, y la estructura necesita apertura para no convertirse en rigidez. "
        "Comprender cómo colaboran ambas puede ayudarte a reconocer de qué manera creces, qué fortalece realmente tu estabilidad y dónde aparecen los desafíos que forman parte de tu proceso de maduración."
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
        "Recorre el informe con curiosidad y observa qué partes describen mejor el momento que estás viviendo. "
        "Con el tiempo descubrirás que Júpiter y Saturno no hablan únicamente de quién eres, sino también de cómo evolucionan tu manera de crecer y la forma en que construyes una vida capaz de sostener ese crecimiento.",
        estilos["cuerpo"],
    )

    return elementos

def bloque_rueda_sociales(
    ruta_rueda,
    estilos,
):
    return [
        Spacer(1, 0.15 * cm),
        Image(
            ruta_rueda,
            width=10 * cm,
            height=10 * cm,
        ),
        PageBreak(),
    ]


def bloque_resumen_sociales(
    carta,
    estilos,
):
    planetas = carta["planetas"]

    jupiter = planetas.get("Júpiter", {})
    saturno = planetas.get("Saturno", {})

    estilo_celda = ParagraphStyle(
        "CeldaResumenSociales",
        parent=estilos["cuerpo"],
        fontName="Times-Roman",
        fontSize=8.5,
        leading=10.5,
        spaceAfter=0,
        alignment=TA_LEFT,
    )

    estilo_celda_centro = ParagraphStyle(
        "CeldaResumenSocialesCentro",
        parent=estilo_celda,
        alignment=TA_CENTER,
    )

    estilo_cabecera = ParagraphStyle(
        "CabeceraResumenSociales",
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
            Paragraph("Júpiter", estilo_celda),
            Paragraph(
                jupiter.get("signo", ""),
                estilo_celda_centro,
            ),
            Paragraph(
                f"Casa {jupiter.get('casa', '')}",
                estilo_celda_centro,
            ),
            Paragraph(
                "Sentido, confianza y ampliación de perspectiva",
                estilo_celda,
            ),
        ],
        [
            Paragraph("Saturno", estilo_celda),
            Paragraph(
                saturno.get("signo", ""),
                estilo_celda_centro,
            ),
            Paragraph(
                f"Casa {saturno.get('casa', '')}",
                estilo_celda_centro,
            ),
            Paragraph(
                "Estructura, responsabilidad y sostenibilidad",
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
            "La arquitectura de tus funciones sociales",
            estilos["subtitulo"],
        ),
        Spacer(
            1,
            0.9 * cm,
        ),
        tabla,
    ]

def bloque_aspectos_principales_sociales(
    aspectos,
    estilos,
):
    """
    Muestra una tabla resumen con todos los aspectos de
    Júpiter y Saturno.

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
                "No aparecen aspectos principales de Júpiter o Saturno "
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


# ─── BLOQUES DE CONTENIDO: PLANETAS SOCIALES ──────────────────────────────────

PLANETAS_SOCIALES = {
    "Júpiter",
    "Saturno",
}

ORDEN_PLANETAS_SOCIALES = {
    "Júpiter": 1,
    "Saturno": 2,
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

        # Evita repetir el aspecto Júpiter–Saturno.
        #
        # Orden de interpretación:
        # Júpiter interpreta su aspecto con Saturno.
        # Saturno no vuelve a interpretar ese mismo vínculo.

        if (
            planeta in PLANETAS_SOCIALES
            and otro_punto in PLANETAS_SOCIALES
            and ORDEN_PLANETAS_SOCIALES[planeta]
            > ORDEN_PLANETAS_SOCIALES[otro_punto]
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


def bloque_planeta_social(
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
    Genera el capítulo completo de un planeta social:

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


def bloque_jupiter(
    carta,
    aspectos,
    estilos,
):
    return bloque_planeta_social(
        planeta="Júpiter",
        carta=carta,
        aspectos=aspectos,
        textos_signo=JUPITER_SIGNO,
        textos_casa=JUPITER_CASA,
        combinaciones=JUPITER_COMBINACIONES,
        textos_tipo_aspecto=JUPITER_TEXTOS_TIPO_ASPECTO,
        integracion=JUPITER_INTEGRACION,
        subtitulo_capitulo=(
            "La forma en que amplías tu perspectiva, encuentras sentido "
            "y desarrollas confianza en tus posibilidades."
        ),
        estilos=estilos,
    )


def bloque_saturno(
    carta,
    aspectos,
    estilos,
):
    return bloque_planeta_social(
        planeta="Saturno",
        carta=carta,
        aspectos=aspectos,
        textos_signo=SATURNO_SIGNO,
        textos_casa=SATURNO_CASA,
        combinaciones=SATURNO_COMBINACIONES,
        textos_tipo_aspecto=SATURNO_TEXTOS_TIPO_ASPECTO,
        integracion=SATURNO_INTEGRACION,
        subtitulo_capitulo=(
            "La forma en que construyes estabilidad, asumes responsabilidad "
            "y desarrollas una estructura capaz de sostenerte."
        ),
        estilos=estilos,
    )


def generar_pdf_planetas_sociales(
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

    contenido += bloque_portada_sociales(
        nombre,
        fecha_str,
        hora_str,
        ciudad,
        estilos,
    )

    contenido += bloque_bienvenida_sociales(
        estilos,
    )

    contenido += bloque_rueda_sociales(
        ruta_rueda,
        estilos,
    )

    contenido += bloque_resumen_sociales(
        carta,
        estilos,
    )

    contenido += bloque_aspectos_principales_sociales(
        aspectos,
        estilos,
    )

    contenido += bloque_jupiter(
        carta,
        aspectos,
        estilos,
    )

    contenido += bloque_saturno(
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
                "Comprender cómo buscas sentido, cómo amplías tu mirada y de qué manera construyes estabilidad puede transformar la relación que mantienes con tu propio proceso de crecimiento.",
                estilos["cuerpo"],
            ),
            Paragraph(
                "Júpiter y Saturno no representan fuerzas opuestas. Uno te invita a expandirte; el otro te ayuda a construir una estructura capaz de sostener esa expansión. Cuando ambas funciones colaboran, el crecimiento deja de depender del impulso del momento y puede convertirse en una forma de vivir más consciente, estable y coherente.",
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
    print("  JÚPITER · SATURNO — Arquitectura Interna")
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

    aspectos = calcular_aspectos_planetas_sociales(
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
        nombre_f + "_Planetas_Sociales",
    )

    ruta_pdf = ruta_base + ".pdf"
    ruta_rueda = ruta_base + "_rueda.png"

    print("Generando rueda...")

    dibujar_rueda_planetas_sociales(
        carta,
        aspectos,
        ruta_rueda,
    )

    print("Generando PDF con ReportLab...")

    generar_pdf_planetas_sociales(
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
        "Generando informe Júpiter · Saturno para:",
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

        # ── ASPECTOS DE JÚPITER Y SATURNO ─────────────────────

        aspectos = calcular_aspectos_planetas_sociales(
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
            nombre_f + "_Planetas_Sociales",
        )

        ruta_pdf = ruta_base + ".pdf"
        ruta_rueda = ruta_base + "_rueda.png"

        # ── RUEDA ─────────────────────────────────────────────

        dibujar_rueda_planetas_sociales(
            carta,
            aspectos,
            ruta_rueda,
        )

        # ── PDF ───────────────────────────────────────────────

        generar_pdf_planetas_sociales(
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
            "Error generando Júpiter · Saturno:",
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