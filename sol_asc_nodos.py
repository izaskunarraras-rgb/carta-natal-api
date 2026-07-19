#!/usr/bin/env python3
"""
3. Sol, Ascendente y Nodos — Arquitectura Interna
Interpreta la dirección (Sol), el punto de entrada al sistema (Ascendente)
y la tensión evolutiva (Nodos) de la carta natal.
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

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak,
    Table, TableStyle, KeepTogether
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


# ─── TEXTOS: SOL POR SIGNO ─────────────────────────────────────────────
SOL_SIGNO = {
"Aries": (
    "Tu dirección se activa cuando puedes empezar algo. "
    "Necesitas movimiento, iniciativa y la sensación de que hay un objetivo hacia el que avanzar. "
    "Cuando pasas demasiado tiempo esperando, conteniéndote o sin poder actuar, la energía empieza a acumularse y suele salir en forma de irritación, impulsividad o agotamiento.\n\n"
    
    "No suele faltarte impulso. Lo difícil aparece cuando arrancas demasiado rápido, sin suficiente base o sin tener claro qué quieres sostener realmente. "
    "Puedes empezar muchas cosas con fuerza y perder conexión con ellas a mitad de camino.\n\n"
    
    "Te desgasta sentir que no puedes avanzar, depender constantemente del ritmo de otras personas o tener que esperar demasiado para actuar. "
    "Cuando no encuentras una dirección clara, es fácil acabar moviéndote por tensión más que por verdadera decisión."
),

"Tauro": (
    "Tu dirección se activa cuando puedes construir algo poco a poco. "
    "Necesitas estabilidad, continuidad y sentir que el esfuerzo tiene una forma concreta. "
    "Las prisas suelen bloquearte más de lo que ayudan.\n\n"
    
    "Funcionas mejor cuando tienes tiempo para consolidar lo que haces, entender tus ritmos y avanzar de manera gradual. "
    "Cuando todo cambia demasiado rápido o el entorno exige respuestas inmediatas, puedes cerrarte, resistirte o quedarte parado más tiempo del que desearías.\n\n"
    
    "Te afecta mucho perder aquello que habías construido, sentir que no hay suelo firme o vivir cambios constantes sin preparación. "
    "La dirección aparece cuando puedes echar raíces en lo que haces."
),

"Géminis": (
    "Tu dirección se activa a través del movimiento mental, las conversaciones y el intercambio de ideas. "
    "Necesitas estímulo, curiosidad y la posibilidad de pensar en voz alta para sentir que avanzas.\n\n"
    
    "El problema no suele ser la falta de opciones, sino tener demasiadas abiertas al mismo tiempo. "
    "Puedes interesarte por muchas cosas a la vez y terminar dispersándote si no encuentras un eje claro que organice toda esa información.\n\n"
    
    "Cuando no puedes expresarte, aprender o compartir lo que piensas, aparece inquietud interna. "
    "Te cuesta sostener direcciones demasiado rígidas o cerradas. Necesitas movimiento, pero también algo que dé coherencia a todo lo que vas abriendo."
),

"Cáncer": (
    "Tu dirección nace desde dentro. "
    "Necesitas sentir cierta seguridad emocional y cierta conexión con tu espacio interno para poder avanzar hacia afuera. "
    "Cuando eso no existe, gran parte de tu energía se va en protegerte, adaptarte o intentar sostener el entorno.\n\n"
    
    "No siempre muestras rápidamente hacia dónde quieres ir. "
    "A menudo necesitas tiempo para sentirte cómodo antes de exponerte o tomar decisiones importantes.\n\n"
    
    "Te desgasta mucho no tener intimidad, sentirte emocionalmente invadido o vivir demasiado tiempo en entornos donde no puedes descansar de verdad. "
    "Cuando no encuentras un lugar interno desde el que sostenerte, es fácil replegarte y perder claridad sobre tu dirección."
),

"Leo": (
    "Tu dirección se activa cuando puedes expresar lo que eres de una forma visible y propia. "
    "Necesitas sentir que lo que haces tiene valor, presencia y una huella personal.\n\n"
    
    "No se trata solamente de reconocimiento externo. "
    "Lo importante es sentir que hay algo auténtico de ti en lo que haces. "
    "Cuando ocupas lugares donde eres completamente intercambiable o invisible, la motivación suele apagarse.\n\n"
    
    "Te afecta mucho sentir que lo que aportas no importa, compararte constantemente o depender demasiado de la validación externa. "
    "Cuando pierdes conexión con tu propia expresión, puedes acabar actuando para ser visto en lugar de actuar desde algo real."
),

"Virgo": (
    "Tu dirección se activa cuando puedes mejorar algo concreto. "
    "Necesitas sentir que lo que haces sirve para algo, que aporta orden, claridad o utilidad real.\n\n"
    
    "Sueles orientarte bien cuando puedes distinguir qué funciona y qué no. "
    "La confusión sostenida, la falta de criterio o los entornos caóticos tienden a agotarte profundamente.\n\n"
    
    "Cuando no encuentras una aplicación práctica para tu energía, es fácil entrar en exceso de análisis, preocupación o autoexigencia. "
    "Necesitas sentir que tu esfuerzo tiene sentido y que puede convertirse en algo tangible."
),

"Libra": (
    "Tu dirección se activa en relación con otras personas. "
    "Necesitas intercambio, contraste y diálogo para aclarar qué quieres realmente.\n\n"
    
    "Esto no significa dependencia. "
    "Muchas veces simplemente piensas mejor, decides mejor o entiendes mejor tu posición cuando puedes verla reflejada en otra persona o en un vínculo.\n\n"
    
    "Te desgasta vivir demasiado tiempo en conflicto, en desequilibrios sostenidos o teniendo que decidir todo completamente solo. "
    "Cuando no hay referencias relacionales claras, puedes quedarte dudando mucho tiempo antes de moverte."
),

"Escorpio": (
    "Tu dirección se activa cuando sientes que hay algo verdadero en juego. "
    "Necesitas profundidad, intensidad y contacto con lo que transforma de verdad.\n\n"
    
    "Las dinámicas superficiales o vacías suelen agotarte rápidamente. "
    "Cuando no encuentras profundidad en lo que haces, puedes acabar controlándolo todo, desconfiando o acumulando tensión por dentro.\n\n"
    
    "Te afecta mucho la traición, la pérdida de confianza o sentir que no puedes transformar algo importante en tu vida. "
    "Cuando la energía no encuentra salida, puede volverse contra ti en forma de obsesión, desgaste o bloqueo emocional."
),

"Sagitario": (
    "Tu dirección se activa cuando sientes que hay un horizonte hacia el que crecer. "
    "Necesitas sentido, expansión y la sensación de que tu vida se mueve hacia algo más amplio.\n\n"
    
    "La rutina por sí sola rara vez te sostiene. "
    "Necesitas comprender por qué haces lo que haces y sentir que hay una dirección con significado detrás.\n\n"
    
    "Puedes entusiasmarte con muchas posibilidades al mismo tiempo y perder fuerza intentando abarcar demasiado. "
    "También te afecta vivir en contextos demasiado cerrados, repetitivos o limitados. "
    "Cuando pierdes sentido, aparece desorientación antes que tristeza."
),

"Capricornio": (
    "Tu dirección se activa cuando puedes construir algo sólido a largo plazo. "
    "Necesitas objetivos claros, estructura y la sensación de que el esfuerzo actual servirá para algo en el futuro.\n\n"
    
    "Sueles sostener bien procesos largos, pero te desgasta muchísimo trabajar sin dirección o invertir energía en cosas que no llevan a ningún lugar. "
    "La sensación de inutilidad puede agotarte más que el esfuerzo en sí.\n\n"
    
    "Te afecta perder la estructura que organizaba tu vida, sentir que todo depende únicamente de ti o no ver resultados después de mucho tiempo sosteniendo algo. "
    "Necesitas sentir que estás construyendo sobre una base real."
),

"Acuario": (
    "Tu dirección se activa cuando puedes pensar diferente y conectar eso con algo más grande que tú. "
    "Necesitas espacio mental, libertad y la sensación de formar parte de una visión, una red o un proyecto con sentido colectivo.\n\n"
    
    "Cuando el entorno es demasiado rígido, repetitivo o cerrado, puedes desconectarte emocionalmente o alejarte por dentro aunque sigas presente.\n\n"
    
    "También puedes perder dirección si tus ideas no encuentran ninguna forma concreta de aplicarse en la realidad. "
    "Necesitas sentir que lo que piensas puede conectarse con algo vivo y compartido."
),

"Piscis": (
    "Tu dirección se activa cuando puedes conectar con algo que va más allá de lo inmediato y lo puramente práctico. "
    "Necesitas sensibilidad, imaginación, inspiración o espacios donde puedas sentir sin tener que definirlo todo constantemente.\n\n"
    
    "Cuando no existe un canal para expresar eso que percibes, es fácil dispersarte, adaptarte demasiado al entorno o perder claridad sobre lo que realmente quieres.\n\n"
    
    "Te desgastan mucho los entornos excesivamente rígidos, saturados de exigencias o sin espacio para parar y respirar. "
    "A veces puedes seguir funcionando hacia afuera mientras por dentro ya has perdido completamente la conexión con tu dirección real."
),
}


# ─── TEXTOS: SOL POR CASA ─────────────────────────────────────────────
SOL_CASA = {
1: (
    "Tu dirección aparece cuando puedes actuar desde tu centro y ocupar espacio de forma visible. "
    "Necesitas sentir que puedes iniciar, decidir y moverte con cierta autonomía.\n\n"
    
    "Cuando te contienes demasiado, dependes constantemente de la reacción del entorno o no encuentras lugar para expresarte con naturalidad, es fácil perder fuerza y claridad.\n\n"
    
    "Sueles orientarte mejor cuando puedes actuar directamente sobre la realidad en lugar de esperar durante demasiado tiempo."
),

2: (
    "Tu dirección se fortalece cuando desarrollas algo propio y estable. "
    "Necesitas construir recursos, capacidades o formas de sostenerte que puedas reconocer como tuyas.\n\n"
    
    "La sensación de dependencia constante, inestabilidad o falta de valor personal suele desgastarte profundamente. "
    "Te ayuda avanzar poco a poco, consolidando lo que haces y viendo resultados concretos.\n\n"
    
    "Cuando no puedes apoyarte en algo sólido, es fácil perder motivación o sentir que toda la energía se dispersa."
),

3: (
    "Tu dirección se activa a través del intercambio con el entorno cercano. "
    "Necesitas hablar, aprender, pensar, conectar ideas o moverte entre distintas conversaciones y estímulos.\n\n"
    
    "Cuando no puedes expresarte o sientes que tu mente se queda encerrada demasiado tiempo en lo mismo, aparece inquietud rápidamente.\n\n"
    
    "Sueles encontrar claridad mientras hablas, escribes, preguntas o compartes lo que piensas. "
    "La dirección aparece en movimiento, no en aislamiento prolongado."
),

4: (
    "Tu dirección nace desde la base interna y el espacio privado. "
    "Necesitas sentir cierta seguridad emocional y cierta estabilidad íntima para poder avanzar hacia afuera.\n\n"
    
    "Cuando no tienes un lugar donde descansar de verdad o sientes que debes estar constantemente disponible para el exterior, es fácil perder fuerza y replegarte.\n\n"
    
    "Muchas veces necesitas más tiempo que otras personas para aclarar qué quieres realmente. "
    "La dirección aparece cuando puedes sostenerte desde dentro."
),

5: (
    "Tu dirección se activa cuando puedes crear, expresar o aportar algo propio. "
    "Necesitas sentir que hay una parte auténtica de ti en lo que haces.\n\n"
    
    "Los espacios demasiado impersonales o donde no puedes dejar huella suelen apagarte poco a poco. "
    "También te afecta mucho sentir que lo que haces no importa o pasa desapercibido.\n\n"
    
    "Cuando puedes jugar, crear o implicarte de verdad en algo, recuperas rápidamente energía y claridad."
),

6: (
    "Tu dirección se fortalece a través de la rutina, el trabajo concreto y la sensación de utilidad. "
    "Necesitas estructura cotidiana y cierta coherencia práctica para sostenerte bien.\n\n"
    
    "El caos, la desorganización o los ritmos completamente irregulares suelen agotarte más de lo que parece. "
    "También puedes perder dirección cuando todo se queda en teoría y no llega a aplicarse en la vida real.\n\n"
    
    "Te ayuda sentir que lo que haces sirve para algo concreto y puede sostenerse en el tiempo."
),

7: (
    "Tu dirección se activa en relación con otras personas. "
    "Necesitas intercambio, diálogo y vínculos que te ayuden a verte con más claridad.\n\n"
    
    "Muchas veces entiendes mejor lo que quieres cuando puedes contrastarlo con alguien más. "
    "Sin referencias relacionales, puedes quedarte dudando o perder orientación.\n\n"
    
    "El reto aparece cuando acabas dependiendo demasiado de la mirada o las decisiones de otras personas para sostener tu propia dirección."
),

8: (
    "Tu dirección aparece cuando puedes atravesar procesos de cambio reales y profundos. "
    "Necesitas sentir que lo que haces transforma algo importante.\n\n"
    
    "Las dinámicas superficiales o demasiado controladas suelen dejarte vacío rápidamente. "
    "También te afecta mucho acumular emociones, tensión o situaciones no resueltas durante demasiado tiempo.\n\n"
    
    "Cuando puedes entrar en profundidad y transformar lo que ya no sirve, recuperas fuerza y claridad."
),

9: (
    "Tu dirección se activa cuando sientes que estás creciendo, aprendiendo o ampliando tu mirada sobre la vida. "
    "Necesitas horizonte, sentido y la sensación de que hay algo más allá de lo inmediato.\n\n"
    
    "La rutina sin propósito suele agotarte profundamente. "
    "También puedes perder fuerza cuando dejas de creer en aquello que antes daba sentido a tu camino.\n\n"
    
    "Te ayuda explorar, estudiar, viajar o abrir espacios que te permitan seguir creciendo por dentro y por fuera."
),

10: (
    "Tu dirección se fortalece cuando puedes construir un lugar claro en el mundo. "
    "Necesitas sentir que avanzas hacia algo reconocible, sólido y con proyección.\n\n"
    
    "Te afecta mucho no saber hacia dónde estás construyendo o sentir que todo el esfuerzo queda suspendido sin forma.\n\n"
    
    "Sueles sostener bien las responsabilidades cuando tienen sentido para ti. "
    "La dirección aparece con más claridad cuando puedes asumir tu lugar y desarrollar una vocación propia."
),

11: (
    "Tu dirección se activa cuando puedes formar parte de algo colectivo o compartir una visión con otras personas. "
    "Necesitas sentir conexión con proyectos, redes o ideas que vayan más allá de lo individual.\n\n"
    
    "Cuando te aíslas demasiado o sientes que no encajas en ningún espacio colectivo, es fácil desconectarte también de tu propia dirección.\n\n"
    
    "Te ayuda mucho participar en proyectos compartidos donde puedas aportar algo propio sin perder libertad."
),

12: (
    "Tu dirección nace desde procesos internos difíciles de explicar rápidamente. "
    "Necesitas momentos de retiro, silencio o distancia del ruido externo para entender qué te está pasando realmente.\n\n"
    
    "Cuando vives demasiado tiempo expuesto, saturado o sin espacio para procesar lo que sientes, es fácil perder claridad y agotarte profundamente.\n\n"
    
    "Muchas veces necesitas integrar primero lo que estás viviendo antes de poder actuar con dirección real."
),
}


# ─── TEXTOS: ASCENDENTE POR SIGNO ─────────────────────────────────────────────
ASC_SIGNO = {
"Aries": (
    "Con Ascendente en Aries, tu primera respuesta ante la vida suele ser actuar. Cuando aparece una situación nueva, "
    "necesitas sentir que puedes hacer algo, tomar la iniciativa o avanzar aunque todavía no tengas todas las respuestas. "
    "La inmovilidad suele generar más incomodidad que el riesgo de equivocarte.\n\n"

    "Te resulta más fácil desenvolverte cuando sientes que tienes margen para decidir, experimentar y comprobar por ti "
    "misma qué funciona. Esperar demasiado o depender constantemente del ritmo de otras personas puede hacer que aparezca "
    "frustración o impaciencia.\n\n"

    "Cuando algo te desborda, la tendencia suele ser acelerar. Puedes responder antes de haber comprendido del todo lo "
    "que está ocurriendo o intentar resolver rápidamente situaciones que en realidad necesitan tiempo. A veces esa rapidez "
    "protege del miedo a sentir vulnerabilidad o incertidumbre.\n\n"

    "Con el paso del tiempo, el aprendizaje consiste en descubrir que actuar y reflexionar no son caminos opuestos. "
    "Cuando esta energía madura, conservas tu capacidad para abrir caminos y tomar decisiones, pero lo haces desde una "
    "mayor claridad y no únicamente desde el impulso del momento."
),

"Tauro": (
    "Con Ascendente en Tauro, necesitas sentir estabilidad antes de dar un paso importante. Tu primera respuesta suele "
    "ser observar si el terreno es seguro, si existen recursos suficientes y si merece la pena invertir energía en lo "
    "que tienes delante.\n\n"

    "Te resulta más fácil desenvolverte cuando puedes hacer las cosas a tu ritmo, sin prisas innecesarias y con tiempo "
    "para asimilar los cambios. La constancia suele darte mejores resultados que la velocidad.\n\n"

    "Cuando la vida cambia demasiado deprisa o aparecen situaciones imprevisibles, es posible que tu reacción sea aferrarte "
    "a lo conocido. Mantener hábitos, rutinas o certezas puede convertirse en una forma de recuperar seguridad, aunque a "
    "veces también retrase cambios que ya son necesarios.\n\n"

    "Cuando esta energía madura, desarrollas una gran capacidad para construir proyectos sólidos y sostener procesos a largo "
    "plazo. Tu estabilidad deja de ser resistencia al cambio y se convierte en una base firme desde la que avanzar con confianza."
),

"Géminis": (
    "Con Ascendente en Géminis, necesitas comprender lo que ocurre para orientarte. Tu primera reacción suele ser observar, "
    "hacer preguntas, comparar posibilidades y reunir información antes de decidir cómo responder.\n\n"

    "Te resulta más fácil desenvolverte cuando puedes aprender, conversar y mantener la mente activa. Explorar diferentes "
    "formas de entender una misma situación te ayuda a sentir que dispones de más recursos para afrontarla.\n\n"

    "Cuando aparece la incertidumbre o el exceso de presión, puedes refugiarte en el pensamiento. Analizar una situación desde "
    "todos los ángulos aporta sensación de control, aunque a veces también dificulte tomar una decisión o mantener una dirección "
    "estable.\n\n"

    "Cuando esta energía madura, tu curiosidad se convierte en una gran capacidad de adaptación. Puedes comprender rápidamente "
    "lo que ocurre, comunicarte con claridad y encontrar soluciones creativas sin perderte entre posibilidades infinitas."
),

"Cáncer": (
    "Con Ascendente en Cáncer, necesitas sentir que existe un lugar seguro desde el que afrontar la vida. "
    "Tu primera reacción suele ser percibir el ambiente, observar cómo se encuentran las personas que te rodean "
    "y comprobar si puedes relajarte o si conviene permanecer en alerta.\n\n"

    "Te resulta más fácil desenvolverte cuando existe cercanía, confianza y sensación de pertenencia. Antes de "
    "abrirte por completo, necesitas comprobar que el entorno ofrece la seguridad suficiente para mostrarte con naturalidad.\n\n"

    "Cuando algo te desborda, puedes protegerte cerrándote emocionalmente, retirándote o intentando cuidar de otras "
    "personas antes que de ti. En ocasiones resulta más sencillo atender las necesidades ajenas que reconocer las propias.\n\n"

    "Con el tiempo, el aprendizaje consiste en descubrir que protegerte no implica esconderte. Cuando esta energía "
    "madura, desarrollas una enorme capacidad para sostener, cuidar y crear espacios donde otras personas también "
    "pueden sentirse seguras, sin dejar de atender tus propias necesidades."
),

"Leo": (
    "Con Ascendente en Leo, necesitas sentir que puedes ocupar tu lugar con naturalidad. Tu primera reacción suele ser "
    "buscar una forma de participar activamente en lo que ocurre, expresando quién eres y aportando algo propio.\n\n"

    "Te resulta más fácil desenvolverte cuando existe espacio para mostrar tus capacidades, tomar iniciativas y sentir "
    "que lo que haces tiene un valor real. Necesitas implicarte de corazón en aquello que consideras importante.\n\n"

    "Cuando aparece la inseguridad o el miedo a no ser suficiente, puedes esforzarte por demostrar constantemente tu "
    "valor o, por el contrario, esconder una parte de ti para evitar sentirte expuesta al juicio de otras personas. "
    "Ambas respuestas nacen de la misma necesidad de reconocimiento.\n\n"

    "Cuando esta energía madura, descubres que no necesitas demostrar continuamente quién eres. Tu presencia transmite "
    "confianza de forma natural y puedes liderar, inspirar y animar a otras personas desde la autenticidad, sin depender "
    "de la aprobación externa."
),

"Virgo": (
    "Con Ascendente en Virgo, necesitas comprender cómo funciona una situación antes de sentirte completamente tranquila. "
    "Tu primera reacción suele ser observar los detalles, detectar lo que falta y buscar la forma más útil y ordenada de "
    "afrontar lo que tienes delante.\n\n"

    "Te resulta más fácil desenvolverte cuando existe cierta organización, cuando sabes qué se espera de ti y cuando puedes "
    "mejorar poco a poco aquello en lo que participas. Avanzar paso a paso suele darte más seguridad que improvisar.\n\n"

    "Cuando algo te desborda, puedes intentar recuperar el control analizando cada detalle o exigiéndote hacer las cosas "
    "cada vez mejor. A veces esa búsqueda constante de mejora termina convirtiéndose en autoexigencia o en la sensación de "
    "que nunca es suficiente.\n\n"

    "Cuando esta energía madura, tu capacidad de observar se transforma en discernimiento. Puedes detectar lo importante "
    "sin perderte en lo accesorio, organizar con eficacia y poner tus capacidades al servicio de lo que realmente merece tu energía."
),

"Libra": (
    "Con Ascendente en Libra, necesitas comprender cómo afecta lo que haces a las personas que te rodean. "
    "Tu primera reacción suele ser observar el ambiente, medir el equilibrio de una situación y buscar una forma "
    "de actuar que tenga en cuenta tanto tus necesidades como las de quienes participan en ella.\n\n"

    "Te resulta más fácil desenvolverte cuando existe diálogo, respeto y posibilidad de construir acuerdos. "
    "Antes de tomar una decisión importante, necesitas valorar diferentes puntos de vista y sentir que la elección "
    "mantiene cierta armonía con el conjunto.\n\n"

    "Cuando aparece el conflicto o la tensión, puedes intentar sostener la paz incluso a costa de dejar en segundo plano "
    "lo que realmente necesitas. A veces resulta más sencillo adaptarte que afrontar el riesgo de generar incomodidad "
    "o decepcionar a otras personas.\n\n"

    "Cuando esta energía madura, descubres que el verdadero equilibrio no consiste en evitar los conflictos, sino en "
    "relacionarte desde la honestidad. Puedes cooperar, escuchar y construir vínculos sanos sin renunciar a tu propio criterio."
),

"Escorpio": (
    "Con Ascendente en Escorpio, necesitas percibir qué ocurre bajo la superficie antes de confiar plenamente. "
    "Tu primera reacción suele ser observar con profundidad, captar lo que no se dice y valorar si el entorno ofrece "
    "la seguridad suficiente para mostrarte tal como eres.\n\n"

    "Te resulta más fácil desenvolverte cuando sientes que puedes comprender las verdaderas motivaciones de las personas "
    "y de las situaciones. Lo superficial rara vez te basta. Necesitas sentir que existe autenticidad y profundidad en "
    "lo que construyes.\n\n"

    "Cuando algo te desborda, puedes intentar recuperar seguridad anticipándote a todo lo que podría ocurrir o manteniendo "
    "un mayor control sobre lo que sucede a tu alrededor. A veces esa vigilancia nace del deseo de evitar volver a sentirte "
    "vulnerable o desprotegida.\n\n"

    "Cuando esta energía madura, tu capacidad de percibir lo esencial se convierte en una gran fortaleza. Puedes atravesar "
    "los cambios con profundidad, acompañar procesos difíciles y sostener una enorme intensidad emocional sin necesidad "
    "de vivir permanentemente en estado de alerta."
),

"Sagitario": (
    "Con Ascendente en Sagitario, necesitas encontrar un sentido a lo que vives. Tu primera reacción suele ser ampliar "
    "la mirada, buscar una perspectiva más amplia y tratar de comprender cómo encaja cada experiencia dentro de un camino "
    "más grande.\n\n"

    "Te resulta más fácil desenvolverte cuando existe posibilidad de aprender, explorar y seguir creciendo. Sentir que "
    "la vida avanza y que siempre hay algo nuevo por descubrir alimenta tu confianza y tu motivación.\n\n"

    "Cuando aparecen las dificultades, puedes protegerte buscando rápidamente una explicación que devuelva el optimismo "
    "o fijando la atención en lo que todavía es posible. En ocasiones esta tendencia puede hacer que minimices el dolor "
    "o que quieras pasar demasiado deprisa por procesos que necesitan ser vividos con calma.\n\n"

    "Cuando esta energía madura, desarrollas una gran capacidad para inspirar y abrir horizontes. Puedes mantener la "
    "confianza sin negar la realidad y transmitir esperanza desde una comprensión profunda de la vida, no desde el optimismo fácil."
),

"Capricornio": (
    "Con Ascendente en Capricornio, necesitas comprender cuál es la mejor forma de afrontar una situación antes de dar un paso. "
    "Tu primera reacción suele ser valorar las consecuencias, medir los recursos disponibles y buscar una manera sólida de avanzar. "
    "Rara vez te sientes cómoda actuando sin una dirección clara.\n\n"

    "Te resulta más fácil desenvolverte cuando existe estructura, cuando sabes qué depende de ti y cuando puedes construir "
    "las cosas poco a poco. La sensación de estar haciendo algo con sentido y de manera consistente suele darte mucha seguridad.\n\n"

    "Cuando aparecen la incertidumbre o la presión, puedes responder asumiendo más responsabilidades de las que realmente te "
    "corresponden o exigiéndote mantener el control de todo. A veces resulta difícil permitirte descansar o reconocer que también "
    "necesitas apoyo.\n\n"

    "Cuando esta energía madura, descubres que la fortaleza no consiste en cargar siempre con todo. Puedes sostener procesos "
    "importantes con serenidad, asumir responsabilidades sin perder flexibilidad y convertirte en una presencia estable para ti "
    "y para quienes te rodean."
),

"Acuario": (
    "Con Ascendente en Acuario, necesitas comprender lo que ocurre antes de reaccionar. Tu primera respuesta suele ser observar, "
    "tomar cierta distancia y buscar una explicación que te permita entender el conjunto antes de implicarte por completo.\n\n"

    "Te resulta más fácil desenvolverte cuando puedes pensar con libertad y llegar a tus propias conclusiones. Cuando sientes que "
    "debes responder de una determinada manera o adaptarte constantemente a las expectativas de otras personas, es habitual que "
    "aparezca incomodidad o necesidad de marcar distancia.\n\n"

    "Ante situaciones intensas o emocionalmente complejas, tu tendencia suele ser analizar lo que está ocurriendo antes de actuar. "
    "Comprender te ayuda a recuperar seguridad y claridad. No porque sientas menos, sino porque necesitas entender primero para "
    "saber cómo responder.\n\n"

    "El reto aparece cuando esa capacidad de observar se convierte en desconexión. A veces puedes protegerte tanto desde la distancia "
    "que termina siendo difícil mostrar lo que realmente te está pasando o permitir que otras personas se acerquen a esa parte más "
    "vulnerable.\n\n"

    "Cuando esta energía madura, tu capacidad de observar se convierte en una de tus mayores fortalezas. Puedes mantener tu "
    "independencia, pensar con claridad y actuar con autenticidad sin necesidad de alejarte emocionalmente de la vida ni de quienes "
    "te rodean."
),

"Piscis": (
    "Con Ascendente en Piscis, necesitas percibir el ambiente antes de decidir cómo responder. Tu primera reacción suele ser captar "
    "lo que ocurre de una forma muy intuitiva, incluso antes de poder explicarlo con palabras. Muchas veces sientes primero y comprendes después.\n\n"

    "Te resulta más fácil desenvolverte cuando puedes actuar con sensibilidad, creatividad y cierta libertad para seguir lo que "
    "intuyes. Necesitas espacios donde no todo esté completamente definido y donde exista margen para adaptarte a lo que va surgiendo.\n\n"

    "Cuando la realidad se vuelve demasiado dura o exigente, puedes protegerte alejándote mentalmente de aquello que resulta difícil "
    "de sostener. A veces esa distancia aparece en forma de evasión, idealización o dificultad para poner límites claros, especialmente "
    "cuando sientes que otras personas esperan demasiado de ti.\n\n"

    "Cuando esta energía madura, tu sensibilidad deja de ser una fuente de confusión para convertirse en una forma profunda de comprensión. "
    "Puedes conectar con lo que viven otras personas sin perderte en ello, mantener la empatía sin renunciar a tus propios límites y "
    "confiar en tu intuición sin dejar de mirar la realidad con claridad."
),
}

# ─── TEXTOS: REGENTE DEL ASCENDENTE POR CASA ────────────────────────────────
# La casa del regente muestra el ámbito de vida donde la forma de afrontar
# la realidad encuentra uno de sus principales apoyos.

REGENTE_ASC_CASA = {

    1: (
        "Tu manera de afrontar la vida encuentra uno de sus principales apoyos en la capacidad "
        "de actuar desde ti. Necesitas sentir que puedes tomar decisiones propias, comprobar por "
        "ti misma lo que funciona y mantener contacto con tu criterio personal.\n\n"

        "Cuando te alejas demasiado de lo que realmente quieres o delegas continuamente tu "
        "dirección en otras personas, es fácil perder claridad. Recuperas estabilidad cuando "
        "vuelves a tu cuerpo, a tu presencia y a la posibilidad de intervenir directamente "
        "sobre lo que está ocurriendo."
    ),

    2: (
        "Tu manera de afrontar la vida necesita apoyarse en una base firme. La estabilidad "
        "material, el cuerpo, los recursos disponibles y la sensación de que puedes sostenerte "
        "por tus propios medios influyen mucho en la confianza con la que respondes a lo que ocurre.\n\n"

        "Cuando esa base se debilita, puede aparecer inseguridad o necesidad de aferrarte a lo "
        "conocido. Recuperas claridad cuando construyes poco a poco, reconoces el valor de tus "
        "capacidades y dispones de algo concreto sobre lo que apoyarte."
    ),

    3: (
        "Tu manera de afrontar la vida se fortalece cuando puedes comprender, preguntar y poner "
        "en palabras lo que está ocurriendo. La conversación, el aprendizaje y el contacto con "
        "el entorno cercano te ayudan a orientarte.\n\n"

        "Cuando no puedes expresar lo que piensas o acumulas demasiada información sin ordenarla, "
        "es fácil que aparezca inquietud. Recuperas estabilidad cuando puedes hablar, escribir, "
        "contrastar ideas y encontrar una explicación suficientemente clara para seguir avanzando."
    ),

    4: (
        "Tu manera de afrontar la vida necesita una base emocional segura. La intimidad, el hogar, "
        "la pertenencia y la posibilidad de retirarte a un espacio propio influyen profundamente "
        "en la forma en la que respondes al mundo.\n\n"

        "Cuando no existe un lugar donde bajar la guardia, gran parte de tu energía puede quedarse "
        "ocupada en protegerte. Recuperas estabilidad cuando puedes descansar, atender lo que se "
        "mueve por dentro y sentir que existe un espacio en el que no necesitas estar sosteniéndolo todo."
    ),

    5: (
        "Tu manera de afrontar la vida encuentra apoyo cuando puedes expresar algo propio. La creatividad, "
        "el deseo, el juego y la posibilidad de implicarte de corazón en lo que haces fortalecen tu confianza.\n\n"

        "Cuando no hay espacio para mostrarte o todo se vuelve excesivamente impersonal, puedes perder "
        "motivación. Recuperas estabilidad cuando vuelves a aquello que te entusiasma y permites que haya "
        "una huella personal en tus decisiones y proyectos."
    ),

    6: (
        "Tu manera de afrontar la vida se sostiene mejor cuando existe cierta organización cotidiana. "
        "Las rutinas, el cuidado del cuerpo, el trabajo concreto y la sensación de utilidad ayudan a que "
        "tu respuesta ante la realidad sea más clara y estable.\n\n"

        "Cuando el día a día se desordena o acumulas demasiadas tareas sin estructura, puede aumentar la "
        "sensación de desbordamiento. Recuperas equilibrio cuando ordenas lo inmediato, ajustas tus ritmos "
        "y conviertes las intenciones en acciones concretas."
    ),

    7: (
        "Tu manera de afrontar la vida encuentra uno de sus principales apoyos en el vínculo. El diálogo, "
        "la colaboración y la posibilidad de contrastar tu mirada con otra persona te ayudan a comprender "
        "mejor cómo posicionarte.\n\n"

        "Cuando intentas resolverlo todo en solitario o cuando una relación ocupa demasiado espacio, puedes "
        "perder claridad. Recuperas estabilidad cuando existe intercambio real, límites comprensibles y una "
        "forma de construir junto a otras personas sin dejarte fuera."
    ),

    8: (
        "Tu manera de afrontar la vida se fortalece cuando puedes comprender lo que ocurre en profundidad. "
        "Los procesos de cambio, la intimidad, la confianza y la posibilidad de atravesar aquello que no puede "
        "resolverse de forma superficial tienen un peso importante.\n\n"

        "Cuando intentas mantener todo bajo control o evitar una transformación necesaria, la tensión puede "
        "aumentar. Recuperas estabilidad cuando reconoces lo que está cambiando, afrontas lo que permanece "
        "oculto y permites que algunas etapas terminen de verdad."
    ),

    9: (
        "Tu manera de afrontar la vida necesita apoyarse en una visión amplia. Aprender, viajar, estudiar, "
        "cuestionar creencias y encontrar un sentido más profundo en lo que vives ayudan a organizar tu dirección.\n\n"

        "Cuando la vida se reduce únicamente a obligaciones inmediatas o pierdes conexión con aquello que da "
        "significado a tu camino, puede aparecer desorientación. Recuperas estabilidad cuando amplías la mirada "
        "y vuelves a relacionar lo cotidiano con una comprensión más grande de tu vida."
    ),

    10: (
        "Tu manera de afrontar la vida se fortalece cuando existe una dirección clara hacia la que construir. "
        "La vocación, la responsabilidad, los objetivos y la posibilidad de ocupar un lugar reconocible en el "
        "mundo aportan estructura a tu forma de responder.\n\n"

        "Cuando no sabes hacia dónde estás avanzando o sientes que el esfuerzo no conduce a ningún lugar, puede "
        "aparecer una gran pérdida de confianza. Recuperas estabilidad cuando defines prioridades, asumes tu lugar "
        "y construyes algo que pueda sostenerse a largo plazo."
    ),

    11: (
        "Tu manera de afrontar la vida encuentra apoyo en los proyectos compartidos, las redes y la posibilidad "
        "de formar parte de algo más amplio. Sentir que puedes aportar una mirada propia dentro de un grupo o una "
        "visión colectiva fortalece tu orientación.\n\n"

        "Cuando te aíslas demasiado o intentas encajar renunciando a tu singularidad, es fácil perder claridad. "
        "Recuperas estabilidad cuando encuentras espacios donde puedes colaborar, compartir ideas y mantener al "
        "mismo tiempo tu independencia."
    ),

    12: (
        "Tu manera de afrontar la vida necesita momentos de silencio, retirada y elaboración interna. No todo puede "
        "comprenderse mientras sigues respondiendo a las exigencias externas; algunas cosas necesitan tiempo para "
        "madurar fuera de la mirada de otras personas.\n\n"

        "Cuando vives demasiado tiempo sin descanso o sin espacio para escuchar lo que ocurre por dentro, puedes "
        "sentirte desorientada o desconectada. Recuperas estabilidad cuando paras, reduces el ruido y permites que "
        "la claridad aparezca sin forzarla."
    ),
}


# ─── TEXTOS: REGENTE DEL ASCENDENTE POR SIGNO ───────────────────────────────

REGENTE_ASC_SIGNO = {

    "Aries": (
        "Buscas esa estabilidad tomando la iniciativa. Necesitas comprobar por ti misma lo que funciona, "
        "actuar cuando algo es importante y sentir que puedes abrir camino sin depender constantemente del "
        "ritmo de otras personas.\n\n"

        "Cuando dudas demasiado o permaneces mucho tiempo esperando, es fácil perder claridad. Recuperas "
        "confianza cuando vuelves a la acción consciente y recuerdas que no todo necesita estar resuelto "
        "antes de dar el primer paso."
    ),

    "Tauro": (
        "Buscas esa estabilidad de una forma paciente y constante. Necesitas construir paso a paso, "
        "consolidar aquello que tiene valor para ti y sentir que existe una base firme sobre la que apoyar "
        "tus decisiones.\n\n"

        "Cuando todo cambia demasiado deprisa, puedes necesitar más tiempo para adaptarte. Recuperas "
        "seguridad cuando respetas tus propios ritmos y vuelves a aquello que realmente resulta estable."
    ),

    "Géminis": (
        "Buscas esa estabilidad comprendiendo lo que ocurre. Necesitas preguntar, contrastar ideas, poner "
        "en palabras lo que piensas y mantener la mente en movimiento para orientarte con claridad.\n\n"

        "Cuando aparecen demasiadas posibilidades al mismo tiempo, puedes perder dirección entre opciones "
        "y explicaciones. Recuperas seguridad cuando ordenas la información, eliges qué merece atención "
        "y transformas el pensamiento en una decisión concreta."
    ),

    "Cáncer": (
        "Buscas esa estabilidad protegiendo aquello que consideras importante. Necesitas sentir cercanía, "
        "confianza y una base emocional desde la que poder responder a lo que ocurre sin permanecer en alerta.\n\n"

        "Cuando no existe suficiente seguridad, puedes replegarte o centrarte demasiado en cuidar el entorno. "
        "Recuperas claridad cuando reconoces tus propias necesidades, encuentras un lugar donde bajar la guardia "
        "y permites que el cuidado también te incluya."
    ),

    "Leo": (
        "Buscas esa estabilidad expresándote de una forma personal y visible. Necesitas sentir que puedes "
        "aportar algo propio, implicarte de corazón y reconocer valor en aquello que haces.\n\n"

        "Cuando no encuentras espacio para mostrarte o dependes demasiado de la aprobación externa, puede "
        "debilitarse tu confianza. Recuperas seguridad cuando vuelves a lo que te inspira y actúas desde una "
        "convicción interna, no únicamente desde la necesidad de ser reconocida."
    ),

    "Virgo": (
        "Buscas esa estabilidad organizando, comprendiendo y mejorando lo que tienes delante. Necesitas "
        "distinguir qué funciona, qué necesita ajuste y cuál es el siguiente paso concreto.\n\n"

        "Cuando la incertidumbre aumenta, puedes intentar controlarlo todo mediante el análisis o la exigencia. "
        "Recuperas seguridad cuando separas lo esencial de lo accesorio y aceptas que avanzar con suficiente "
        "claridad suele ser más útil que esperar una perfección imposible."
    ),

    "Libra": (
        "Buscas esa estabilidad a través del equilibrio y del intercambio. Necesitas escuchar diferentes puntos "
        "de vista, comprender el efecto de tus decisiones y encontrar una forma de avanzar que no te deje fuera "
        "ni ignore a las demás personas.\n\n"

        "Cuando aparece tensión, puedes retrasar decisiones o adaptarte demasiado para evitar conflicto. Recuperas "
        "claridad cuando recuerdas que la armonía real también necesita honestidad, límites y un criterio propio."
    ),

    "Escorpio": (
        "Buscas esa estabilidad comprendiendo lo que permanece oculto. Necesitas profundizar, cuestionar "
        "lo aparente y descubrir qué está ocurriendo realmente antes de confiar plenamente en una situación.\n\n"

        "Las transformaciones importantes forman parte de tu manera de construir seguridad. Cuando aceptas "
        "que algunas etapas necesitan terminar para que otras puedan comenzar, recuperas una sensación de "
        "dirección mucho más sólida que la que podría ofrecer el simple intento de mantener todo igual."
    ),

    "Sagitario": (
        "Buscas esa estabilidad ampliando la mirada y encontrando sentido. Necesitas comprender hacia dónde "
        "conduce lo que estás viviendo, aprender de ello y relacionarlo con una visión más amplia de tu vida.\n\n"

        "Cuando pierdes horizonte, puede aparecer inquietud o necesidad de escapar rápidamente hacia una nueva "
        "posibilidad. Recuperas seguridad cuando vuelves a una dirección con significado y permites que la confianza "
        "se apoye también en la realidad, no solo en la promesa de lo que podría ocurrir."
    ),

    "Capricornio": (
        "Buscas esa estabilidad construyendo estructura. Necesitas saber qué depende de ti, qué objetivo merece "
        "esfuerzo y cómo avanzar de una forma consistente y sostenible.\n\n"

        "Cuando aumenta la presión, puedes asumir demasiada responsabilidad o endurecerte para seguir funcionando. "
        "Recuperas seguridad cuando ordenas prioridades, distribuyes mejor las cargas y recuerdas que sostener algo "
        "no significa hacerlo todo sin ayuda."
    ),

    "Acuario": (
        "Buscas esa estabilidad pensando con libertad. Necesitas conservar una mirada propia, cuestionar "
        "lo establecido y encontrar respuestas que tengan sentido para ti, incluso cuando son diferentes "
        "a las del entorno.\n\n"

        "Recuperas claridad cuando puedes observar las situaciones con perspectiva y permitirte pensar sin "
        "la presión de tener que adaptarte constantemente a las expectativas de otras personas."
    ),

    "Piscis": (
        "Buscas esa estabilidad escuchando lo que percibes de una forma intuitiva. Necesitas sensibilidad, "
        "espacio interno y margen para comprender aquello que no siempre puede explicarse de inmediato.\n\n"

        "Cuando el entorno se vuelve demasiado exigente o confuso, puedes absorber más de lo que te corresponde "
        "o perder claridad entre necesidades propias y ajenas. Recuperas seguridad cuando pones límites, reduces "
        "el ruido y das una forma concreta a aquello que intuyes."
    ),
}


# ─── TEXTOS: NODO NORTE POR SIGNO ────────────────────────────────────────────
# Dirección que pide esfuerzo consciente + tensión con el Nodo Sur (patrón automático).

NODO_NORTE_SIGNO = {

"Aries": (
    "Tu dirección pide aprender a actuar desde tu propio impulso, incluso cuando no existe acuerdo completo alrededor. Necesitas desarrollar más iniciativa, capacidad de decisión y confianza para empezar cosas sin esperar siempre validación externa. "
    "Lo conocido suele llevarte a medir constantemente el efecto de tus movimientos en otras personas, buscar equilibrio o ajustar demasiado lo que haces para evitar conflicto o incomodidad relacional. "
    "El reto no está en dejar de relacionarte, sino en no perderte dentro de la necesidad de consenso permanente. "
    "Crecer hacia este Nodo Norte implica tolerar la incomodidad de actuar aunque no todo esté completamente resuelto con el entorno."
),

"Tauro": (
    "Tu dirección pide construir algo estable, sencillo y sostenible en el tiempo. Aprender a confiar más en lo concreto, desarrollar recursos propios y permitirte ir más despacio sin sentir que pierdes profundidad. "
    "Lo conocido suele llevarte hacia la intensidad emocional, las crisis o los procesos de transformación constante. Puede existir una sensación de que solo aquello que remueve mucho es verdaderamente importante o real. "
    "El reto está en descubrir que la calma, la estabilidad y lo cotidiano también pueden contener muchísima profundidad. "
    "Crecer hacia este Nodo Norte implica dejar de necesitar continuamente situaciones límite para sentir que algo tiene valor."
),

"Géminis": (
    "Tu dirección pide curiosidad, escucha y capacidad de moverte en lo pequeño y en lo inmediato. Aprender a preguntar antes de cerrar respuestas y permitirte cambiar de idea sin sentir que eso invalida lo anterior. "
    "Lo conocido suele llevarte rápidamente hacia grandes conclusiones, certezas o visiones amplias sobre la vida. Puede costarte permanecer en la duda o convivir con información incompleta. "
    "El reto está en descubrir que no necesitas entenderlo todo desde el principio ni llegar enseguida a una verdad definitiva. "
    "Crecer hacia este Nodo Norte implica recoger información poco a poco y permitir que las respuestas aparezcan más adelante."
),

"Cáncer": (
    "Tu dirección pide acercarte más a lo emocional, al cuidado y a las necesidades humanas reales. Aprender a sostenerte también desde la sensibilidad y no únicamente desde la exigencia, el control o el rendimiento. "
    "Lo conocido suele llevarte hacia la autosuficiencia y la necesidad de seguir funcionando incluso cuando por dentro hay cansancio, vulnerabilidad o necesidad de apoyo. "
    "El reto está en permitirte necesitar descanso, cercanía o cuidado sin vivirlo como una debilidad. "
    "Crecer hacia este Nodo Norte implica dejar de convertir toda necesidad emocional en una obligación de seguir resistiendo."
),

"Leo": (
    "Tu dirección pide ocupar espacio de una forma más personal y visible. Necesitas expresarte más desde lo que eres y menos desde la adaptación constante al grupo, al entorno o a lo que otras personas esperan. "
    "Lo conocido suele llevarte hacia cierta distancia emocional, observación o tendencia a diluir tu individualidad dentro de lo colectivo. "
    "El reto está en permitirte destacar sin sentir que tienes que justificar continuamente tu presencia o minimizar lo que eres. "
    "Crecer hacia este Nodo Norte implica asumir que también tienes derecho a ocupar el centro de tu propia vida."
),

"Virgo": (
    "Tu dirección pide orden, claridad y capacidad de distinguir qué funciona realmente para ti. Aprender a poner límites, desarrollar criterio y dar forma concreta a lo que haces en lugar de dejar todo indefinido. "
    "Lo conocido suele llevarte hacia la dispersión, la ambigüedad o la tendencia a mantener demasiadas posibilidades abiertas durante demasiado tiempo. "
    "El reto está en aceptar que elegir, organizar y definir no destruye la sensibilidad ni la profundidad. "
    "Crecer hacia este Nodo Norte implica aterrizar más en la realidad cotidiana y sostener mejor lo concreto."
),

"Libra": (
    "Tu dirección pide aprender a incluir más al otro dentro de tus decisiones y movimientos. Necesitas desarrollar diálogo, cooperación y capacidad de construir junto a otras personas sin sentir que eso elimina tu autonomía. "
    "Lo conocido suele llevarte hacia la acción rápida, la autosuficiencia o la tendencia a avanzar sin tener demasiado en cuenta el impacto relacional de lo que haces. "
    "El reto está en descubrir que considerar al otro no significa perder tu dirección personal. "
    "Crecer hacia este Nodo Norte implica aprender a relacionarte sin vivir el vínculo como un freno a tu movimiento."
),

"Escorpio": (
    "Tu dirección pide entrar en procesos de transformación reales y aprender a soltar aquello que ya no puede sostenerse de la misma manera. Necesitas desarrollar más capacidad para atravesar cambios profundos sin intentar conservar constantemente lo conocido. "
    "Lo familiar suele llevarte hacia la búsqueda de estabilidad, seguridad y control sobre aquello que ya conoces. Puede haber dificultad para dejar atrás situaciones, vínculos o estructuras incluso cuando ya no tienen vida. "
    "El reto está en tolerar el cambio sin necesitar todas las garantías antes de moverte. "
    "Crecer hacia este Nodo Norte implica aceptar que algunas etapas terminan antes de que exista claridad completa sobre lo siguiente."
),

"Sagitario": (
    "Tu dirección pide desarrollar una visión más amplia y comprometerte con algo que tenga sentido profundo para ti. Aprender a elegir dirección en lugar de permanecer únicamente en la exploración constante o en el movimiento continuo. "
    "Lo conocido suele llevarte hacia la dispersión, la acumulación de información o la necesidad de mantener demasiadas posibilidades abiertas al mismo tiempo. "
    "El reto está en aceptar que elegir un camino también implica renunciar a otros. "
    "Crecer hacia este Nodo Norte implica dejar de vivir solamente en el movimiento y empezar a construir una orientación más clara y coherente."
),

"Capricornio": (
    "Tu dirección pide construir estructura, asumir responsabilidad y desarrollar un lugar propio dentro del mundo visible. Necesitas aprender a sostener procesos a largo plazo y dar forma concreta a aquello que quieres construir. "
    "Lo conocido suele llevarte hacia el repliegue, la protección emocional o la necesidad de permanecer en espacios seguros, íntimos y familiares. "
    "El reto está en exponerte más a la realidad externa sin abandonar tu sensibilidad interna. "
    "Crecer hacia este Nodo Norte implica atreverte a ocupar espacio público sin sentir que para hacerlo tienes que endurecerte completamente."
),

"Acuario": (
    "Tu dirección pide ampliar la mirada y participar en algo que vaya más allá de lo puramente personal. Necesitas aprender a colaborar, compartir visión y construir también desde lo colectivo sin sentir que eso borra tu identidad. "
    "Lo conocido suele llevarte hacia la necesidad de reconocimiento individual o hacia la sensación de que todo depende exclusivamente de tu propia expresión personal. "
    "El reto está en contribuir sin necesitar constantemente confirmación externa sobre tu valor o tu importancia. "
    "Crecer hacia este Nodo Norte implica descubrir que formar parte de algo mayor no elimina lo que eres."
),

"Piscis": (
    "Tu dirección pide aprender a soltar más el control y tolerar mejor la incertidumbre. Necesitas abrirte a espacios donde no todo pueda entenderse, corregirse o resolverse inmediatamente. "
    "Lo conocido suele llevarte hacia la autoexigencia, el análisis constante o la necesidad de que todo permanezca ordenado y bajo control. "
    "El reto está en aceptar que no todo puede organizarse perfectamente ni sostenerse desde la vigilancia continua. "
    "Crecer hacia este Nodo Norte implica permitir más descanso, más confianza y menos necesidad de supervisar constantemente todo lo que ocurre."
),

}

# ─── TEXTOS: NODO NORTE POR CASA ─────────────────────────────────────────────

NODO_NORTE_CASA = {

1: (
    "Tu dirección pide desarrollar más presencia propia, iniciativa y capacidad de actuar desde ti. Aprender a ocupar espacio sin esperar continuamente permiso, validación o referencia externa para moverte. "
    "Muchas veces el crecimiento aparece cuando te permites empezar, decidir o actuar aunque no tengas todas las garantías ni todo completamente resuelto alrededor. "
    "También cuando dejas de colocarte constantemente en función de lo que necesitan o esperan las demás personas. "
    "El reto suele estar en tolerar la visibilidad y asumir que no todo movimiento necesita consenso previo para ser legítimo."
),

2: (
    "Tu dirección pide construir estabilidad, recursos propios y una relación más sólida contigo y con lo que puedes sostener en la realidad concreta. "
    "El crecimiento aparece cuando desarrollas algo tangible, aprendes a confiar más en tus capacidades y dejas de depender tanto de lo externo para sentir seguridad o valor personal. "
    "Muchas veces el reto está en bajar el nivel de intensidad constante y descubrir que la vida también puede construirse desde lo simple, lo estable y lo cotidiano sin perder profundidad."
),

3: (
    "Tu dirección pide acercarte más a lo inmediato: hablar, preguntar, escuchar, aprender y relacionarte con el entorno cercano de forma más directa y sencilla. "
    "El crecimiento aparece cuando puedes moverte con curiosidad sin necesitar grandes respuestas antes de empezar y cuando permites que las conversaciones y los pequeños intercambios tengan valor por sí mismos. "
    "El reto suele estar en no vivir únicamente dentro de grandes ideas o visiones amplias olvidando la realidad concreta y cotidiana del día a día."
),

4: (
    "Tu dirección pide construir una base interna más sólida y habitable. Aprender a sostenerte desde dentro y no únicamente desde lo que haces, produces o sostienes hacia afuera. "
    "El crecimiento aparece cuando das espacio al descanso, a la intimidad y a la vida emocional real, y cuando empiezas a construir un lugar interno que no dependa completamente del reconocimiento externo. "
    "El reto suele estar en dejar de vivir únicamente desde la exigencia, la productividad o la necesidad de funcionar constantemente."
),

5: (
    "Tu dirección pide expresarte más desde un lugar personal y creativo. Necesitas permitir que haya algo verdaderamente tuyo visible en lo que haces, en lugar de esconderte continuamente detrás del grupo, del rol o de la distancia emocional. "
    "El crecimiento aparece cuando recuperas juego, deseo, creatividad y capacidad de disfrutar de lo que haces sin justificar constantemente tu presencia. "
    "El reto suele estar en atreverte a ocupar espacio personal sin reducir automáticamente tu brillo para sentirte con más seguridad."
),

6: (
    "Tu dirección pide desarrollar más orden, estructura cotidiana y capacidad de sostener procesos concretos en la realidad diaria. "
    "El crecimiento aparece cuando construyes hábitos, cuidas mejor tus ritmos y aprendes a aterrizar las cosas en la vida real en lugar de dejarlas únicamente en intención o posibilidad. "
    "El reto suele estar en no perderte constantemente en lo abstracto, en la dispersión o en la sensación de que todo debe permanecer abierto e indefinido."
),

7: (
    "Tu dirección pide aprender a construir junto a otras personas y no solamente desde la autosuficiencia o la independencia absoluta. "
    "El crecimiento aparece cuando desarrollas diálogo, cooperación y capacidad de incluir la mirada del otro sin sentir que eso amenaza tu dirección o tu identidad. "
    "El reto suele estar en no resolverlo todo solo ni convertir la independencia en una manera de evitar el vínculo, la negociación o la vulnerabilidad relacional."
),

8: (
    "Tu dirección pide entrar más profundamente en los procesos de cambio y transformación. Aprender a soltar lo que ya terminó y atravesar etapas donde no todo puede permanecer bajo control. "
    "El crecimiento aparece cuando puedes dejar atrás viejas seguridades y permitir que algunas partes de tu vida cambien de verdad en lugar de sostenerlas únicamente por miedo a perder estabilidad. "
    "El reto suele estar en no quedarte únicamente en lo conocido o en lo seguro por miedo a atravesar incertidumbre o intensidad emocional."
),

9: (
    "Tu dirección pide ampliar la mirada y construir una orientación más profunda sobre la vida. Necesitas aprender a comprometerte con aquello que realmente tiene sentido para ti en lugar de permanecer únicamente en la exploración constante. "
    "El crecimiento aparece cuando desarrollas visión, perspectiva y una dirección más clara a largo plazo. "
    "El reto suele estar en no dispersarte continuamente en información, estímulos o posibilidades sin llegar a construir una orientación propia y sostenida."
),

10: (
    "Tu dirección pide construir un lugar visible en el mundo y desarrollar una vocación, estructura o dirección propia hacia afuera. "
    "El crecimiento aparece cuando asumes responsabilidad sobre lo que quieres construir y empiezas a ocupar espacio de forma más clara dentro de lo colectivo y lo visible. "
    "El reto suele estar en no refugiarte únicamente en lo privado, en lo familiar o en espacios donde no exista exposición ni responsabilidad externa."
),

11: (
    "Tu dirección pide conectar más con proyectos colectivos, redes y espacios compartidos. Necesitas aprender a colaborar, aportar visión y sentir que formas parte de algo más amplio que tu experiencia individual. "
    "El crecimiento aparece cuando puedes construir junto a otras personas sin vivirlo como una pérdida de identidad personal. "
    "El reto suele estar en no quedar atrapado únicamente en la necesidad de reconocimiento individual o en una expresión demasiado centrada en ti."
),

12: (
    "Tu dirección pide desarrollar más espacio interno, silencio y capacidad de escuchar procesos que no siempre pueden explicarse o resolverse rápidamente. "
    "El crecimiento aparece cuando aprendes a parar, descansar y permitir que algunas cosas maduren sin necesidad de controlarlas continuamente. "
    "El reto suele estar en no vivir permanentemente desde la hiperactividad, la exigencia o la necesidad de tener respuestas inmediatas para todo lo que ocurre."
),

}

# ─── TEXTOS: SUR POR SIGNO ─────────────────────────────────────────────
NODO_SUR_SIGNO = {

"Aries": (
    "Tiendes a apoyarte en la autosuficiencia, la rapidez para actuar y la necesidad de resolver las cosas por tu cuenta. Hay facilidad para iniciar, decidir y moverte sin depender demasiado de otras personas ni esperar demasiado tiempo antes de actuar. "
    "El problema aparece cuando toda situación relacional empieza a vivirse como una posible pérdida de autonomía o de libertad personal. "
    "Puede costarte parar, negociar o permitir que otras personas participen realmente en tus decisiones y movimientos. "
    "A veces avanzas tan rápido que no llegas a registrar del todo el efecto que ese movimiento tiene sobre ti o sobre el entorno."
),

"Tauro": (
    "Tiendes a buscar estabilidad, control sobre lo conocido y seguridad en aquello que puedes sostener de forma concreta. Hay facilidad para conservar, resistir y construir lentamente en el tiempo, pero también dificultad para entrar en cambios profundos cuando implican perder referencias conocidas. "
    "Muchas veces aparece tendencia a mantener situaciones, vínculos o estructuras simplemente porque ofrecen sensación de estabilidad o continuidad. "
    "El problema surge cuando permanecer en lo seguro se vuelve más importante que reconocer que algo ya necesita transformarse."
),

"Géminis": (
    "Tiendes a moverte entre muchas ideas, estímulos y posibilidades al mismo tiempo. Hay facilidad para adaptarte, aprender rápido y mantener varias opciones abiertas sin sentir necesidad inmediata de elegir una sola dirección. "
    "El problema aparece cuando acumulas información sin construir realmente un rumbo claro o cuando cambias constantemente de enfoque para evitar comprometerte con algo más profundo y sostenido. "
    "A veces la mente continúa moviéndose incluso cuando internamente ya sería necesario detenerse, simplificar y elegir."
),

"Cáncer": (
    "Tiendes a protegerte, replegarte hacia lo conocido y sostenerte desde lo íntimo antes que exponerte demasiado hacia afuera. Hay facilidad para cuidar, percibir necesidades emocionales y crear sensación de refugio, pero también tendencia a quedarte demasiado tiempo dentro de espacios seguros y familiares. "
    "Muchas veces lo conocido emocionalmente se siente más habitable que aquello que implicaría mayor exposición o responsabilidad externa. "
    "El problema aparece cuando protegerte se convierte en una forma de evitar crecimiento, movimiento o apertura hacia nuevas experiencias."
),

"Leo": (
    "Tiendes a buscar reconocimiento, centralidad o validación a través de lo que expresas y haces visible. Hay facilidad para crear, destacar y dejar una huella personal en lo que haces, pero también riesgo de depender demasiado de la mirada externa para sostener el propio valor. "
    "Puede aparecer necesidad constante de sentirte visto, importante o reconocido para confirmar que lo que haces tiene sentido. "
    "El problema surge cuando toda la experiencia empieza a girar alrededor de la validación externa o del lugar que ocupas frente a otras personas."
),

"Virgo": (
    "Tiendes a detectar rápidamente lo que falta, lo que podría mejorar o aquello que no termina de funcionar del todo. Hay facilidad para analizar, ordenar y resolver problemas concretos, pero también tendencia a vivir en autoexigencia constante o sensación de insuficiencia permanente. "
    "Muchas veces aparece necesidad de controlar incertidumbre a través del perfeccionismo, la supervisión continua o el exceso de análisis. "
    "El problema surge cuando ya no existe espacio para descansar porque todo parece necesitar todavía más corrección o mejora."
),

"Libra": (
    "Tiendes a orientarte mucho a través del vínculo y de la reacción de otras personas. Hay facilidad para adaptarte, negociar y mantener equilibrio en las relaciones, pero también tendencia a dejar demasiado espacio a lo que el entorno necesita o espera. "
    "El problema aparece cuando evitar conflicto se vuelve más importante que expresar claramente lo que tú quieres, piensas o necesitas realmente. "
    "A veces puedes esperar demasiado antes de actuar por miedo a generar desequilibrio, incomodidad o tensión alrededor."
),

"Escorpio": (
    "Sueles vivir lo que te pasa con mucha intensidad y profundidad, como si las experiencias necesitaran transformarte de alguna manera. Hay facilidad para entrar en lo complejo, sostener crisis o percibir lo que otras personas no ven, pero también tendencia a permanecer en tensión emocional constante. "
    "Puede aparecer sensación de que solo aquello que remueve mucho, duele o tiene gran intensidad emocional es verdaderamente importante o real. "
    "El problema surge cuando necesitas conflicto, profundidad extrema o intensidad permanente para sentir conexión con la vida."
),

"Sagitario": (
    "Tiendes a buscar rápidamente sentido, dirección o explicaciones amplias sobre lo que ocurre. Hay facilidad para construir visión, conectar ideas y moverte hacia horizontes grandes, pero también tendencia a alejarte demasiado de lo inmediato y concreto. "
    "Puede costarte permanecer plenamente dentro de experiencias pequeñas, cotidianas o ambiguas sin intentar convertirlas enseguida en una gran conclusión o aprendizaje. "
    "El problema aparece cuando necesitas respuestas enormes para poder habitar cosas simples o presentes."
),

"Capricornio": (
    "Tiendes a sostenerte desde la exigencia, el control y la necesidad de funcionar incluso en momentos de cansancio, vulnerabilidad o sobrecarga. Hay facilidad para asumir responsabilidad, organizarte y seguir adelante, pero también tendencia a endurecerte demasiado o medir tu valor únicamente por lo que produces y sostienes. "
    "Muchas veces descansar, necesitar apoyo o bajar el ritmo puede sentirse internamente como pérdida de estructura o de control. "
    "El problema surge cuando la capacidad de sostener se convierte en incapacidad para detenerte."
),

"Acuario": (
    "Tiendes a tomar distancia emocional y a refugiarte en la observación, las ideas o la necesidad de mantener independencia. Hay facilidad para pensar diferente, ver perspectivas amplias y moverte con libertad mental, pero también tendencia a desconectarte emocionalmente cuando algo empieza a implicarte demasiado. "
    "Muchas veces proteger tu autonomía puede volverse más importante que permitir verdadera cercanía o intimidad emocional. "
    "El problema aparece cuando la distancia deja de ser espacio saludable y empieza a convertirse en desconexión."
),

"Piscis": (
    "Tiendes a adaptarte mucho al entorno, absorber lo que ocurre alrededor y moverte en espacios abiertos o poco definidos. Hay facilidad para percibir matices, conectar con lo sensible y acompañar procesos complejos, pero también dificultad para sostener límites claros o distinguir qué pertenece realmente a tu experiencia y qué viene del ambiente. "
    "Puede aparecer tendencia a evitar demasiada estructura, definición o concreción para no sentirte limitado. "
    "El problema surge cuando esa falta de contorno termina generando más confusión, agotamiento o pérdida de dirección interna."
),

}


# ─── TEXTOS: NODO SUR POR CASA ─────────────────────────────────────────────
NODO_SUR_CASA = {

1: (
    "Tiendes a apoyarte en la autosuficiencia, la iniciativa propia y la necesidad de resolver desde ti antes que incluir fácilmente a otras personas en el proceso. Hay facilidad para actuar, empezar y sostener autonomía, pero también riesgo de vivir demasiado desde la individualidad o desde la sensación de que todo depende únicamente de ti. "
    "Muchas veces pedir apoyo, colaborar o negociar puede sentirse como pérdida de fuerza, control o libertad personal. "
    "El problema aparece cuando la independencia deja de ser un recurso y empieza a convertirse en aislamiento o exceso de carga sostenida en solitario."
),

2: (
    "Tiendes a buscar seguridad en lo conocido, en lo estable y en aquello que puedes controlar, conservar o sostener de forma concreta. Hay facilidad para construir recursos y mantener continuidad en el tiempo, pero también dificultad para entrar en cambios profundos cuando implican incertidumbre o pérdida de referencias conocidas. "
    "Muchas veces aparece necesidad de aferrarte a estructuras, vínculos o situaciones que ofrecen estabilidad aunque ya no estén verdaderamente vivos. "
    "El problema surge cuando mantener seguridad se vuelve más importante que reconocer que algo necesita transformarse."
),

3: (
    "Tiendes a moverte constantemente entre ideas, conversaciones, información y estímulos cercanos. Hay facilidad para adaptarte, aprender rápido y mantener varias posibilidades abiertas al mismo tiempo, pero también riesgo de dispersarte o quedar atrapado únicamente en lo inmediato. "
    "La mente puede seguir acumulando información incluso cuando internamente ya sería necesario simplificar, profundizar o construir una dirección más clara. "
    "El problema aparece cuando el movimiento mental constante sustituye la posibilidad de verdadero compromiso o enfoque."
),

4: (
    "Tiendes a buscar refugio en lo privado, en lo conocido o en espacios donde puedes protegerte emocionalmente del exceso de exposición externa. Hay facilidad para cuidar, sostener vínculos íntimos y construir sensación de hogar, pero también tendencia a evitar demasiado aquello que implica visibilidad, responsabilidad externa o movimiento hacia afuera. "
    "Muchas veces lo emocionalmente seguro pesa más que la necesidad de expansión o crecimiento. "
    "El problema aparece cuando protegerte se convierte en una forma de no avanzar."
),

5: (
    "Tiendes a orientarte mucho desde la necesidad de expresión personal, reconocimiento o validación sobre lo que haces y muestras. Hay facilidad para crear, destacar y ocupar espacio visible, pero también riesgo de depender demasiado de la mirada externa para sostener el propio valor. "
    "Puede aparecer necesidad constante de sentirte importante, especial o reconocido para confirmar que lo que haces tiene sentido. "
    "El problema surge cuando toda experiencia empieza a girar alrededor de la necesidad de ser visto."
),

6: (
    "Tiendes a apoyarte en el control cotidiano, la organización y la necesidad de que todo funcione correctamente. Hay facilidad para sostener rutinas, resolver problemas y hacerte cargo de responsabilidades concretas, pero también tendencia a vivir en autoexigencia permanente o vigilancia continua sobre lo que falta por corregir. "
    "Muchas veces descansar, improvisar o salir un poco del control puede generar ansiedad o sensación de desorden interno. "
    "El problema aparece cuando el cuerpo ya no encuentra espacio suficiente para relajarse porque todo parece requerir supervisión constante."
),

7: (
    "Tiendes a orientarte mucho a través de las relaciones y de la reacción de otras personas. Hay facilidad para negociar, adaptarte y construir vínculos, pero también riesgo de perder claridad sobre lo que realmente quieres cuando el entorno tiene demasiado peso emocional. "
    "Muchas veces sostener el vínculo puede volverse más importante que sostenerte a ti mismo o expresar con claridad lo que necesitas. "
    "El problema aparece cuando la adaptación constante termina alejándote de tu propio centro."
),

8: (
    "Tiendes a vivir desde la intensidad emocional, los procesos profundos o las dinámicas de transformación constante. Hay facilidad para atravesar crisis, entrar en profundidad y percibir lo que permanece oculto, pero también riesgo de vivir demasiado tiempo en tensión, desgaste emocional o estados internos extremos. "
    "Puede aparecer sensación de que solo aquello que tiene intensidad o profundidad emocional es verdaderamente importante. "
    "El problema surge cuando la calma, la estabilidad o la sencillez empiezan a sentirse vacías o insuficientes."
),

9: (
    "Tiendes a buscar rápidamente sentido, dirección o respuestas amplias sobre la vida. Hay facilidad para construir visión, conectar experiencias y moverte dentro de marcos más grandes de comprensión, pero también riesgo de alejarte demasiado de lo inmediato y concreto. "
    "Muchas veces aparece necesidad de entender el significado completo de las cosas antes incluso de habitar plenamente lo que está ocurriendo aquí y ahora. "
    "El problema aparece cuando la búsqueda de grandes respuestas dificulta la presencia en la experiencia cotidiana."
),

10: (
    "Tiendes a sostenerte desde la responsabilidad, la productividad o la necesidad de construir algo visible hacia afuera. Hay facilidad para asumir exigencia, seguir adelante y funcionar incluso en momentos difíciles, pero también tendencia a desconectarte de necesidades emocionales básicas o del propio cansancio. "
    "Muchas veces el valor personal queda demasiado ligado a lo que haces, produces o consigues sostener externamente. "
    "El problema aparece cuando descansar, parar o necesitar apoyo empieza a sentirse como pérdida de valor o de estructura."
),

11: (
    "Tiendes a buscar pertenencia en grupos, redes o espacios colectivos. Hay facilidad para colaborar, pensar en lo compartido y adaptarte a dinámicas grupales, pero también riesgo de diluir demasiado tu individualidad dentro de lo colectivo. "
    "Muchas veces pertenecer o mantener conexión con el grupo puede pesar más que preguntarte qué deseas realmente tú o qué dirección personal necesitas tomar. "
    "El problema aparece cuando la necesidad de encajar termina alejándote de tu propia expresión individual."
),

12: (
    "Tiendes a replegarte hacia el mundo interno, el aislamiento o la necesidad de escapar del exceso de realidad externa. Hay facilidad para conectar con lo sensible, percibir lo invisible y sostener procesos internos complejos, pero también riesgo de desconectarte demasiado de la acción concreta y de la realidad cotidiana. "
    "Muchas veces retirarte puede sentirse más seguro que tomar decisiones claras o asumir límites y dirección definida. "
    "El problema aparece cuando el refugio interno se convierte en una forma de evitar movimiento, responsabilidad o presencia en la vida concreta."
),

}

# ─── TEXTOS: ASPECTOS SOL NODOS ─────────────────────────────────────────────
ASPECTOS_SOL_NODOS = {

("Sol", "Nodo Norte", "="): (
    "El Sol y el Nodo Norte apuntan hacia la misma dirección. Existe una sensación más natural de avanzar hacia aquello que necesitas desarrollar y muchas veces ciertas decisiones importantes se sienten coherentes internamente incluso cuando requieren esfuerzo o implican atravesar incomodidad. "
    "La dirección suele percibirse con más claridad que en otras configuraciones y puede existir sensación de que algunas experiencias importantes encajan profundamente con lo que necesitas construir. "
    "El reto está en no confundir facilidad con trabajo ya realizado. A veces el crecimiento parece tan natural que cuesta ver cuándo sigues funcionando desde patrones antiguos o demasiado conocidos."
),

("Sol", "Nodo Norte", "☍"): (
    "El Sol y el Nodo Norte están en tensión directa. Muchas veces aquello que te sale de forma más natural no coincide con la dirección que más crecimiento te pide desarrollar. "
    "Lo conocido suele sentirse más cómodo, más inmediato o más estable, mientras que avanzar hacia el Nodo Norte puede generar sensación de ir contra una parte importante de tu identidad o de tu manera habitual de funcionar. "
    "El reto está en aceptar que aquí crecer requiere decisiones conscientes y repetidas, no solamente seguir el impulso más automático."
),

("Sol", "Nodo Norte", "□"): (
    "El Sol y los Nodos forman una tensión importante. Muchas veces aparece sensación de contradicción entre lo que haces naturalmente, lo que ya conoces y la dirección hacia la que necesitas crecer. "
    "Puede haber momentos de bloqueo, dudas constantes o dificultad para sentir que alguna dirección termina de encajar completamente. "
    "A veces parece que cualquier decisión deja algo importante fuera. "
    "El reto está en no quedarte paralizado intentando resolver toda la contradicción antes de avanzar. Aquí el crecimiento suele aparecer precisamente mientras atraviesas la tensión."
),

("Sol", "Nodo Norte", "△"): (
    "El Sol y el Nodo Norte se relacionan de forma fluida. La dirección de crecimiento suele sentirse más accesible o más integrada en tu forma natural de moverte por la vida. "
    "Muchas veces puedes avanzar hacia experiencias importantes sin sentir que estás forzando continuamente las cosas ni luchando contra ti mismo. "
    "Existe sensación de coherencia entre identidad y dirección de desarrollo. "
    "El reto está en no acomodarte únicamente en lo que resulta fácil. Aunque exista fluidez, sigue siendo necesario desarrollar consciencia y profundidad en esa dirección."
),

("Sol", "Nodo Norte", "✶"): (
    "El Sol y el Nodo Norte tienen una relación de apertura y posibilidad. Existen recursos internos importantes para avanzar hacia la dirección de crecimiento, especialmente cuando decides implicarte conscientemente en ello. "
    "No suele sentirse como bloqueo constante, pero tampoco como algo completamente automático. "
    "Hay oportunidades reales de desarrollo que aparecen cuando eliges darles espacio y sostenerlas en el tiempo. "
    "El reto está en no dejar esas posibilidades solamente en potencial o en intención."
),

("Sol", "Nodo Norte", "⚻"): (
    "El Sol y el Nodo Norte necesitan ajustes continuos entre sí. Muchas veces puedes sentir que avanzar hacia una dirección importante requiere reorganizar constantemente distintas partes de tu vida o de tu identidad. "
    "Puede existir sensación de incomodidad o de no terminar de encontrar una forma completamente estable de integrar ambas partes. "
    "El reto está en aceptar que aquí el crecimiento rara vez es lineal. La dirección suele aparecer a través de reajustes repetidos más que de una sensación fija de estabilidad."
),

("Sol", "Nodo Sur", "="): (
    "El Sol y el Nodo Sur coinciden en el mismo lugar. Lo conocido, lo automático y aquello que ya sabes hacer tiene muchísima fuerza dentro de tu identidad y de tu manera natural de moverte por la vida. "
    "Muchas veces puedes sentirte muy cómodo funcionando desde patrones antiguos o desde dinámicas que ya controlas bien porque ahí existe sensación de dominio y familiaridad. "
    "El reto está en no quedarte atrapado únicamente en aquello que ya sabes sostener. "
    "Moverte hacia el Nodo Norte requiere salir conscientemente de zonas muy conocidas incluso cuando parecen seguras."
),

("Sol", "Nodo Sur", "☍"): (
    "El Sol se opone al Nodo Sur y apunta hacia el Nodo Norte. La dirección de crecimiento suele sentirse mucho más visible y alineada con tu impulso vital y con aquello que necesitas construir hacia adelante. "
    "Aun así, el Nodo Sur continúa funcionando como un lugar de regreso automático en momentos de cansancio, miedo o exceso de presión. "
    "Lo antiguo sigue teniendo fuerza aunque ya no sea el lugar principal de desarrollo. "
    "El reto está en no idealizar únicamente la dirección de crecimiento olvidando que también necesitas comprender y ordenar aquello que dejas atrás."
),

("Sol", "Nodo Sur", "□"): (
    "El Sol y los Nodos forman una tensión importante. Muchas veces aparece sensación de estar dividido entre distintas direcciones internas sin encontrar un lugar completamente estable donde apoyarte. "
    "Puede haber dificultad para salir de patrones conocidos, pero también incomodidad al permanecer demasiado tiempo dentro de ellos. "
    "Existe sensación de contradicción entre lo que resulta familiar y aquello que intenta abrirse como crecimiento. "
    "El reto está en desarrollar una orientación más consciente sin esperar que toda la contradicción desaparezca primero."
),

("Sol", "Nodo Sur", "△"): (
    "El Sol y el Nodo Sur se relacionan de forma fluida. Lo conocido resulta especialmente accesible, cómodo y fácil de sostener, y muchas capacidades desarrolladas anteriormente aparecen de forma muy natural dentro de tu identidad. "
    "Muchas veces puedes funcionar muy bien dentro de patrones antiguos sin notar rápidamente la necesidad de cambio o transformación. "
    "El reto está en no permanecer demasiado tiempo en lugares que ya dominas solamente porque ahí todo parece más sencillo o estable."
),

("Sol", "Nodo Sur", "✶"): (
    "El Sol y el Nodo Sur tienen una relación de facilidad y apoyo mutuo. Los recursos desarrollados anteriormente pueden ayudarte mucho a construir estabilidad, confianza y sensación de capacidad personal. "
    "Hay habilidades que salen de forma muy natural y que pueden convertirse en una base importante para avanzar hacia nuevas etapas. "
    "El reto está en utilizar esos recursos como apoyo y no como excusa para evitar direcciones nuevas o procesos de crecimiento más incómodos."
),

("Sol", "Nodo Sur", "⚻"): (
    "El Sol y el Nodo Sur necesitan reajustes continuos entre lo que te resulta familiar y la persona que estás intentando construir en el presente. "
    "A veces puedes sentir que vuelves automáticamente a dinámicas conocidas incluso cuando ya no encajan completamente con tu vida actual o con la dirección que necesitas tomar. "
    "Existe tensión entre comodidad y evolución. "
    "El reto está en reconocer qué partes del pasado todavía te sostienen realmente y cuáles empiezan a limitar tu crecimiento."
),

}

# ─── TEXTOS: ASPECTOS SOL ASCENDENTE ─────────────────────────────────────────────
ASPECTOS_SOL_ASC = {

("Sol", "Ascendente", "="): (
    "El Sol y el Ascendente apuntan en la misma dirección. Suele existir bastante coherencia entre cómo vives las experiencias y lo que realmente necesitas desarrollar en tu vida. "
    "Muchas veces actúas de una forma bastante alineada con aquello que sientes importante, y la presencia externa y la dirección interna tienden a reforzarse mutuamente. "
    "Eso puede dar sensación de autenticidad, claridad y continuidad entre lo que muestras y lo que eres. "
    "El reto está en no identificarte completamente con una única manera de ser o de moverte por la vida, dejando espacio también para el cambio y la evolución."
),

("Sol", "Ascendente", "☍"): (
    "El Sol y el Ascendente están en tensión directa. Puede haber diferencia entre cómo te muestras o reaccionas espontáneamente y lo que realmente necesitas construir para sentir coherencia interna. "
    "A veces puedes actuar desde hábitos muy visibles hacia afuera mientras una parte más profunda intenta dirigirse hacia otro lugar o desarrollar otra forma de vivir. "
    "Eso puede generar sensación de desajuste entre la imagen que sostienes y lo que verdaderamente necesita crecer dentro de ti. "
    "El reto está en integrar ambas partes sin sentir que debes elegir completamente entre una y otra."
),

("Sol", "Ascendente", "□"): (
    "El Sol y el Ascendente forman una tensión importante. Muchas veces aparece sensación de fricción entre tu manera espontánea de actuar y la dirección que realmente da más sentido a tu vida. "
    "Puede haber momentos donde reaccionar naturalmente no produce los resultados que esperabas o donde la identidad parece estar continuamente en construcción y reajuste. "
    "A veces lo que sale automáticamente no coincide con lo que más coherencia interna genera a largo plazo. "
    "El reto está en desarrollar una forma más consciente de posicionarte sin perder espontaneidad ni vitalidad."
),

("Sol", "Ascendente", "△"): (
    "El Sol y el Ascendente se relacionan de forma fluida. Suele existir facilidad para expresar hacia afuera aquello que sientes auténtico, importante o coherente contigo. "
    "La manera de actuar y la dirección vital tienden a apoyarse mutuamente y eso puede generar sensación de continuidad interna bastante natural. "
    "Muchas veces las personas perciben con claridad algo de tu identidad real a través de tu presencia o forma de moverte. "
    "El reto está en no acomodarte únicamente en lo que resulta fácil, conocido o espontáneamente accesible."
),

("Sol", "Ascendente", "✶"): (
    "El Sol y el Ascendente tienen una relación de apertura y colaboración. Existen recursos importantes para construir coherencia entre tu forma de actuar y la dirección que quieres desarrollar en la vida. "
    "Muchas veces puedes ajustar con relativa facilidad cómo te posicionas según lo que cada etapa necesita, integrando experiencia y crecimiento de una forma bastante flexible. "
    "No suele sentirse como una tensión constante, pero sí requiere implicación consciente para aprovechar realmente ese potencial. "
    "El reto está en utilizar activamente esa capacidad y no dejarla solamente como posibilidad."
),

("Sol", "Ascendente", "⚻"): (
    "El Sol y el Ascendente necesitan reajustes continuos entre lo que haces espontáneamente y la dirección más profunda de tu vida. "
    "Puede existir sensación de tener que modificar constantemente la manera de actuar, relacionarte o posicionarte para sentir más coherencia interna. "
    "A veces lo que surge automáticamente no termina de encajar del todo con lo que realmente necesitas construir o desarrollar a largo plazo. "
    "El reto está en aceptar que aquí el equilibrio rara vez aparece de una vez para siempre y suele construirse poco a poco mediante ajustes repetidos."
),

}

# ─── TEXTOS: ASPECTOS NODO NORTE ASCENDENTE ─────────────────────────────────────────────
ASPECTOS_NODO_NORTE_ASC = {

("Nodo Norte", "Ascendente", "="): (
    "La dirección de crecimiento está muy visible en tu manera de entrar en la vida. Muchas veces las experiencias importantes aparecen directamente a través de cómo actúas, decides y te posicionas frente a lo que ocurre. "
    "Existe sensación de que el movimiento hacia adelante pasa precisamente por atreverte a ocupar espacio y desarrollar nuevas formas de presencia. "
    "El crecimiento suele activarse rápidamente cuando tomas iniciativa y te implicas de manera directa en la experiencia. "
    "El reto está en sostener conscientemente ese desarrollo y no vivirlo solamente desde impulso automático o reacción inmediata."
),

("Nodo Norte", "Ascendente", "☍"): (
    "La dirección de crecimiento desafía formas muy habituales de reaccionar o posicionarte frente a la vida. Muchas veces crecer implica actuar de maneras que no te salen espontáneamente o que inicialmente se sienten incómodas. "
    "Lo automático suele llevarte hacia posiciones conocidas, mientras que avanzar requiere probar otras formas de relacionarte con la experiencia y con las personas. "
    "Puede existir sensación de tensión entre lo familiar y aquello que realmente impulsa desarrollo. "
    "El reto está en no volver constantemente a posiciones conocidas solo porque resultan más cómodas o previsibles."
),

("Nodo Norte", "Ascendente", "□"): (
    "La dirección de crecimiento genera fricción con hábitos muy incorporados en tu manera de actuar y posicionarte. Puede haber sensación de contradicción entre lo que te sale naturalmente y aquello que más desarrollo te pide construir. "
    "Muchas veces lo automático parece tirar hacia un lugar mientras la vida insiste en abrir otro movimiento distinto. "
    "Eso puede generar bloqueo, dudas o sensación de no terminar de encontrar una posición completamente estable. "
    "El reto está en atravesar esa tensión sin paralizarte y sin esperar que toda contradicción desaparezca antes de avanzar."
),

("Nodo Norte", "Ascendente", "△"): (
    "La dirección de crecimiento fluye con relativa facilidad hacia tu forma natural de moverte por la vida. Muchas veces puedes avanzar hacia experiencias importantes sintiendo bastante coherencia interna entre lo que haces y lo que necesitas desarrollar. "
    "La manera de posicionarte suele favorecer el movimiento hacia adelante y abrir oportunidades de crecimiento de forma bastante natural. "
    "Existe sensación de continuidad entre presencia, decisiones y desarrollo vital. "
    "El reto está en no confundir facilidad con profundidad ya desarrollada y seguir implicándote conscientemente en el proceso."
),

("Nodo Norte", "Ascendente", "✶"): (
    "Existe apertura entre tu manera de actuar y la dirección de crecimiento. Hay recursos disponibles para desarrollar nuevas formas de posicionarte cuando eliges hacerlo conscientemente y muchas veces aparecen oportunidades que ayudan a avanzar paso a paso. "
    "No suele sentirse como una tensión permanente, pero sí requiere cierta participación activa para que el crecimiento realmente tome forma. "
    "La vida suele ofrecer espacios donde probar nuevas maneras de actuar o relacionarte contigo y con el entorno. "
    "El reto está en aprovechar conscientemente esas oportunidades y no dejarlas únicamente como posibilidad."
),

("Nodo Norte", "Ascendente", "⚻"): (
    "La dirección de crecimiento requiere ajustes constantes en tu forma habitual de reaccionar y posicionarte frente a la vida. Muchas veces crecer implica modificar patrones muy automáticos de comportamiento o maneras antiguas de responder a lo que ocurre. "
    "Puede existir sensación de incomodidad porque aquello que antes funcionaba ya no termina de encajar completamente con la dirección actual de desarrollo. "
    "El crecimiento aquí rara vez se siente completamente estable y suele aparecer a través de pequeños reajustes repetidos. "
    "El reto está en aceptar que esa incomodidad forma parte natural del proceso y no significa necesariamente que estés yendo en la dirección equivocada."
),

}

# ─── TEXTOS: ASPECTOS NODO SUR ASCENDENTE ─────────────────────────────────────────────
ASPECTOS_NODO_SUR_ASC = {

("Nodo Sur", "Ascendente", "="): (
    "Los patrones conocidos están muy incorporados en tu manera de actuar y presentarte hacia afuera. Muchas respuestas automáticas salen con gran facilidad y pueden sentirse extremadamente naturales, familiares o difíciles de cuestionar porque forman parte de tu forma habitual de moverte por la vida. "
    "Existe tendencia a reaccionar desde dinámicas muy aprendidas incluso antes de darte tiempo para revisar si siguen encajando realmente con el momento actual. "
    "Eso puede darte sensación de seguridad o de identidad clara, pero también hacer más difícil abrir espacio a nuevas formas de posicionarte. "
    "El reto está en no construir toda la identidad únicamente alrededor de lo ya conocido."
),

("Nodo Sur", "Ascendente", "☍"): (
    "Los patrones conocidos aparecen en tensión con la manera en que necesitas posicionarte actualmente. Muchas veces puedes sentir distancia entre lo que te sale automáticamente y la persona que estás intentando construir o desarrollar en esta etapa de tu vida. "
    "Lo antiguo sigue teniendo fuerza y puede reaparecer especialmente en momentos de cansancio, inseguridad o exceso de presión. "
    "Existe sensación de ir hacia adelante mientras otra parte vuelve constantemente hacia formas anteriores de reaccionar. "
    "El reto está en no regresar automáticamente a dinámicas antiguas solo porque resultan más familiares o previsibles."
),

("Nodo Sur", "Ascendente", "□"): (
    "Los patrones automáticos generan una fricción importante con tu forma de actuar en el presente. Puede haber sensación de repetición, bloqueo o dificultad para salir de dinámicas conocidas incluso cuando ya no funcionan realmente para tu vida actual. "
    "Muchas veces una parte de ti intenta avanzar mientras otra responde desde hábitos profundamente incorporados que siguen apareciendo de forma automática. "
    "Eso puede generar cansancio, contradicción o sensación de estar atrapado en respuestas que ya no representan completamente quién eres. "
    "El reto está en desarrollar mayor consciencia sobre esas reacciones automáticas para no vivirlas como algo inevitable."
),

("Nodo Sur", "Ascendente", "△"): (
    "Existe mucha facilidad para moverte desde dinámicas conocidas y respuestas muy incorporadas. Muchas cosas salen de forma natural y puedes sentir bastante continuidad entre tu manera de actuar y patrones ya desarrollados anteriormente. "
    "Eso puede darte sensación de capacidad, estabilidad o familiaridad frente a distintas situaciones. "
    "Al mismo tiempo, también puede aparecer tendencia a permanecer demasiado tiempo dentro de zonas cómodas o conocidas simplemente porque ahí todo parece funcionar con facilidad. "
    "El reto está en no confundir comodidad con verdadera dirección de crecimiento."
),

("Nodo Sur", "Ascendente", "✶"): (
    "Los recursos desarrollados previamente pueden ayudarte a sostenerte y orientarte con relativa facilidad en distintas etapas de la vida. Hay capacidades conocidas que funcionan como apoyo importante y que pueden darte sensación de confianza o estabilidad cuando las utilizas conscientemente. "
    "Muchas veces puedes apoyarte en experiencias anteriores para construir nuevas formas de avanzar sin necesidad de empezar completamente desde cero. "
    "Existe apertura para integrar lo aprendido sin quedar completamente atrapado en ello. "
    "El reto está en utilizar esos recursos como base de apoyo y no permanecer únicamente dentro de ellos."
),

("Nodo Sur", "Ascendente", "⚻"): (
    "Existe una sensación de ajuste continuo entre respuestas automáticas antiguas y la manera en que necesitas actuar actualmente. A veces puedes notar que ciertas formas de reaccionar ya no encajan completamente con tu vida presente aunque sigan apareciendo de forma inmediata y familiar. "
    "Puede existir sensación de incomodidad o desajuste porque una parte de ti intenta reorganizarse mientras otra continúa funcionando desde hábitos muy antiguos. "
    "El proceso suele sentirse gradual y requiere bastante observación consciente de tus propias reacciones. "
    "El reto está en permitir que la identidad se reorganice poco a poco sin aferrarte constantemente a lo ya conocido."
),

}

# ─── CÁLCULO ASTROLÓGICO ──────────────────────────────────────────────────────

def geocodificar(ciudad):
    g = Nominatim(user_agent="ai_sol_asc_nodos", timeout=10)
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
        "simbolo": "⚸", "lon": pos_li[0], "signo": signo_li, "grado": grado_li, "retrogrado": False
    }

    pos_nn, _ = swe.calc_ut(jd, swe.TRUE_NODE, FLAGS)
    signo_nn, grado_nn = grados_a_signo(pos_nn[0])
    lon_ns = (pos_nn[0] + 180) % 360
    signo_ns, grado_ns = grados_a_signo(lon_ns)
    planetas["Nodo Norte"] = {
        "simbolo": "☊", "lon": pos_nn[0], "signo": signo_nn, "grado": grado_nn, "retrogrado": False
    }
    planetas["Nodo Sur"] = {
        "simbolo": "☋", "lon": lon_ns, "signo": signo_ns, "grado": grado_ns, "retrogrado": False
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


def grados_a_signo_lon(lon):
    """Retorna (signo, grado) con el número de signo (índice 0-11)."""
    return grados_a_signo(lon)

def signo_cuspide_casa(cuspides, num_casa):
    lon = cuspides[num_casa - 1]
    signo, _ = grados_a_signo(lon)
    return signo

def es_anaretico(grado):
    return grado >= 29

def signos_en_cuspides(cuspides):
    return [grados_a_signo(c)[0] for c in cuspides]

def signo_interceptado(signo, cuspides):
    signos_cuspides = signos_en_cuspides(cuspides)
    return signo not in signos_cuspides

def calcular_aspectos_sol_asc_nodos(planetas, asc):
    """
    Calcula los aspectos relevantes de los tres puntos meta:

    - Sol con planetas, Ascendente y Nodo Norte.
    - Ascendente con planetas y Nodo Norte.
    - Nodo Norte con planetas, Sol y Ascendente.

    El Nodo Sur no se calcula como un segundo eje independiente porque
    siempre está exactamente opuesto al Nodo Norte. Una oposición al
    Nodo Norte equivale a una conjunción al Nodo Sur, y viceversa.
    """

    sol = planetas.get("Sol")
    nodo_norte = planetas.get("Nodo Norte")
    nodo_sur = planetas.get("Nodo Sur")

    if not sol or not asc or "lon" not in asc:
        return []

    aspectos = []
    pares = []
    pares_vistos = set()

    # Los cuerpos que pueden formar aspectos relevantes.
    cuerpos = {
        nombre: objeto
        for nombre, objeto in planetas.items()
        if (
            objeto
            and "lon" in objeto
            and nombre not in ("Nodo Norte", "Nodo Sur")
        )
    }

    def agregar_par(nombre1, lon1, nombre2, lon2):
        """
        Añade un par una sola vez, independientemente del orden
        en el que aparezcan sus dos puntos.
        """
        clave = tuple(sorted((nombre1, nombre2)))

        if nombre1 == nombre2 or clave in pares_vistos:
            return

        pares_vistos.add(clave)
        pares.append((nombre1, nombre2, lon1, lon2))

    # ── Sol con el resto de la carta ─────────────────────────────────
    for nombre, objeto in cuerpos.items():
        if nombre == "Sol":
            continue

        agregar_par(
            "Sol",
            sol["lon"],
            nombre,
            objeto["lon"],
        )

    agregar_par(
        "Sol",
        sol["lon"],
        "Ascendente",
        asc["lon"],
    )

    if nodo_norte:
        agregar_par(
            "Sol",
            sol["lon"],
            "Nodo Norte",
            nodo_norte["lon"],
        )

    if nodo_sur:
        agregar_par(
            "Sol",
            sol["lon"],
            "Nodo Sur",
            nodo_sur["lon"],
        )

    # ── Ascendente con los planetas ──────────────────────────────────
    for nombre, objeto in cuerpos.items():
        agregar_par(
            "Ascendente",
            asc["lon"],
            nombre,
            objeto["lon"],
        )

    if nodo_norte:
        agregar_par(
            "Ascendente",
            asc["lon"],
            "Nodo Norte",
            nodo_norte["lon"],
        )

    if nodo_sur:
        agregar_par(
            "Ascendente",
            asc["lon"],
            "Nodo Sur",
            nodo_sur["lon"],
        )

    # ── Nodos con la Luna ────────────────────────────────────────────
    # Sol–Nodos y Ascendente–Nodos se añaden en sus bloques respectivos.
    # Aquí incorporamos únicamente Luna–Nodo Norte y Luna–Nodo Sur.

    luna = planetas.get("Luna")

    if luna and "lon" in luna:
 
        if nodo_norte and "lon" in nodo_norte:
            agregar_par(
                "Nodo Norte",
                nodo_norte["lon"],
                "Luna",
                luna["lon"],
            )

        if nodo_sur and "lon" in nodo_sur:
            agregar_par(
                "Nodo Sur",
                nodo_sur["lon"],
                "Luna",
                luna["lon"],
            )

    # ── Identificación de los aspectos ───────────────────────────────
    for nombre1, nombre2, lon1, lon2 in pares:
        diferencia = abs(lon1 - lon2) % 360

        if diferencia > 180:
            diferencia = 360 - diferencia

        for tipo, angulo, orbe_maximo, simbolo in ASPECTOS_DEF:
            orbe = abs(diferencia - angulo)

            if orbe <= orbe_maximo:
                orbe_redondeado = round(orbe, 2)

                aspectos.append({
                    "p1": nombre1,
                    "p2": nombre2,
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


# ─── INTERPRETACIÓN DE LOS ASPECTOS SOLARES CON EL RESTO DE LA CARTA ─────────

ASPECTOS_SOL_PLANETAS = {

    # ── SOL · JÚPITER ────────────────────────────────────────────────

    ("Sol", "Júpiter", "□"): (
        "La cuadratura entre el Sol y Júpiter puede hacer que la necesidad de crecer "
        "vaya por delante de los recursos disponibles. Puedes asumir más de lo que "
        "realmente puedes sostener, ampliar demasiado rápido un proyecto o confiar "
        "en que el entusiasmo bastará para mantenerlo en el tiempo.\n\n"
        "El aprendizaje no consiste en reducir tu deseo de expansión, sino en darle "
        "una estructura suficiente. Cuando aprendes a medir mejor el alcance de tus "
        "decisiones, esta tensión puede convertirse en una gran capacidad para crecer "
        "sin perder estabilidad."
    ),

    # ── SOL · LILITH ─────────────────────────────────────────────────

    ("Sol", "Lilith", "△"): (
        "El trígono entre el Sol y Lilith conecta tu dirección vital con una parte "
        "instintiva, libre y poco dispuesta a someterse a formas que siente artificiales. "
        "Existe una facilidad natural para reconocer aquello que no encaja contigo y "
        "para actuar desde una autenticidad difícil de domesticar.\n\n"
        "Cuando esta energía encuentra una vía consciente, aporta valentía para ocupar "
        "tu lugar y cuestionar mandatos que ya no representan quién eres. El reto no "
        "suele estar en contactar con esa fuerza, sino en expresarla sin convertirla "
        "automáticamente en rechazo, confrontación o aislamiento."
    ),

    # ── SOL · NEPTUNO ────────────────────────────────────────────────

    ("Sol", "Neptuno", "△"): (
        "El trígono entre el Sol y Neptuno aporta sensibilidad, intuición e imaginación "
        "a tu manera de orientarte. Muchas decisiones pueden nacer primero como una "
        "sensación difícil de explicar y encontrar su forma concreta solo más adelante.\n\n"
        "Esta configuración favorece la inspiración, la creatividad y la capacidad de "
        "percibir significados que no siempre son evidentes. Cuando esa sensibilidad "
        "se acompaña de realidad y estructura, puede convertirse en una fuente profunda "
        "de dirección. Sin una base concreta, también puede llevarte a idealizar caminos "
        "o seguir intuiciones sin comprobar si realmente pueden sostenerse."
    ),

    # ── SOL · PLUTÓN ─────────────────────────────────────────────────

    ("Sol", "Plutón", "☍"): (
        "La oposición entre el Sol y Plutón convierte el desarrollo de la identidad "
        "en un proceso de transformación profunda. A lo largo de la vida pueden aparecer "
        "etapas en las que avanzar implique dejar atrás formas anteriores de ser, "
        "vínculos, posiciones o estructuras que ya no tienen fuerza real.\n\n"
        "Esta dinámica puede vivirse a través de luchas de poder, relaciones intensas "
        "o momentos en los que parece que otra persona tiene demasiado peso sobre tu "
        "dirección. El trabajo consiste en reconocer tu propio poder sin intentar "
        "controlarlo todo ni entregar completamente la capacidad de decidir sobre tu vida."
    ),
}

_FUNCION_PLANETA_SOL = {
    "Luna": "tu mundo emocional, tus necesidades de seguridad y tu manera de reaccionar",
    "Mercurio": "tu pensamiento, tu forma de comprender y tu manera de expresar lo que vives",
    "Venus": "tu forma de vincularte, valorar, disfrutar y recibir afecto",
    "Marte": "tu impulso, tu capacidad de actuar, defenderte y movilizar energía",
    "Júpiter": "tu forma de crecer, confiar, ampliar horizontes y encontrar sentido",
    "Saturno": "tu relación con los límites, la responsabilidad, la exigencia y el tiempo",
    "Urano": "tu necesidad de libertad, cambio, diferencia y renovación",
    "Neptuno": "tu sensibilidad, imaginación, idealización y apertura a lo intangible",
    "Plutón": "tu intensidad, tu necesidad de transformación y tu relación con el poder interno",
    "Quirón": "una zona especialmente sensible que puede convertirse en aprendizaje y comprensión",
    "Lilith": "una parte instintiva, incómoda o poco domesticada que necesita ser reconocida",
}

_DINAMICA_ASPECTO_SOL = {
    "=": (
        "Ambas funciones aparecen muy unidas y tienden a expresarse como una sola fuerza. "
        "Esto aumenta su potencia, pero también puede hacer más difícil distinguir qué necesita cada parte por separado."
    ),
    "✶": (
        "Existe una vía de colaboración accesible entre ambas funciones. "
        "El recurso está disponible, aunque necesita decisiones concretas para no quedarse únicamente como posibilidad."
    ),
    "△": (
        "La relación entre ambas funciones suele fluir con naturalidad. "
        "Puede convertirse en un apoyo importante, siempre que la facilidad no haga que dejes de desarrollarla conscientemente."
    ),
    "□": (
        "Existe fricción entre ambas funciones y no siempre quieren avanzar al mismo ritmo. "
        "La tensión puede generar bloqueo o sobreesfuerzo, pero también empuja a construir una forma más consciente de integrarlas."
    ),
    "☍": (
        "Las dos funciones pueden vivirse como polos opuestos que se activan alternativamente o a través de otras personas. "
        "El trabajo consiste en dejar de elegir siempre un extremo y aprender a sostener la relación entre ambos."
    ),
    "⚻": (
        "La relación exige ajustes continuos. Lo que funciona en una etapa puede necesitar una medida diferente en otra. "
        "No suele haber una solución fija, sino una escucha constante de cuánto espacio necesita cada parte."
    ),
}


def texto_aspecto_sol_planeta(aspecto):
    """
    Devuelve una interpretación específica para un aspecto del Sol.

    Si todavía no existe un texto específico, utiliza temporalmente
    una interpretación general como respaldo.
    """

    p1 = aspecto.get("p1")
    p2 = aspecto.get("p2")
    simbolo = aspecto.get("simbolo")

    if p1 == "Sol":
        otro = p2
    elif p2 == "Sol":
        otro = p1
    else:
        return ""

    # Primero busca un texto específico
    clave1 = ("Sol", otro, simbolo)
    clave2 = (otro, "Sol", simbolo)

    texto_especifico = (
        ASPECTOS_SOL_PLANETAS.get(clave1)
        or ASPECTOS_SOL_PLANETAS.get(clave2)
    )

    if texto_especifico:
        return texto_especifico

    # Respaldo temporal para aspectos aún no escritos
    funcion = _FUNCION_PLANETA_SOL.get(otro)
    if not funcion:
        return ""

    dinamica = _DINAMICA_ASPECTO_SOL.get(simbolo, "")
    tipo = aspecto.get("tipo", "aspecto").lower()

    return (
        f"El Sol forma {tipo} con {otro}. "
        f"Esta relación conecta tu dirección vital con {funcion}. "
        f"{dinamica}"
    )


# ─── TEXTOS DE SECCIÓN ────────────────────────────────────────────────────────

def texto_direccion_general(carta, aspectos):
    planetas = carta["planetas"]
    asc = carta.get("asc", {})
    asc_signo = asc.get("signo", "")

    sol = planetas.get("Sol", {})
    nn  = planetas.get("Nodo Norte", {})
    ns  = planetas.get("Nodo Sur", {})

    sol_signo = sol.get("signo", "")
    sol_casa  = sol.get("casa", "")
    nn_signo  = nn.get("signo", "")
    nn_casa   = nn.get("casa", "")
    ns_signo  = ns.get("signo", "")
    ns_casa   = ns.get("casa", "")

    elem_sol = ELEMENTO_SIGNO.get(sol_signo, "")
    elem_asc = ELEMENTO_SIGNO.get(asc_signo, "")

    def buscar_aspecto(p1, p2):
        return next(
            (a for a in aspectos if {a.get("p1"), a.get("p2")} == {p1, p2}),
            None
        )

    asp_sol_nn  = buscar_aspecto("Sol", "Nodo Norte")
    asp_sol_ns  = buscar_aspecto("Sol", "Nodo Sur")
    asp_sol_asc = buscar_aspecto("Sol", "Ascendente")
    asp_nn_asc  = buscar_aspecto("Nodo Norte", "Ascendente")
    asp_ns_asc  = buscar_aspecto("Nodo Sur", "Ascendente")

    if elem_sol and elem_asc and elem_sol == elem_asc:
        rel_sol_asc = (
            f"El Sol en {sol_signo} y el Ascendente en {asc_signo} pertenecen al mismo elemento. "
            f"Esto suele hacer que la forma en la que vives la vida y tu dirección principal estén bastante alineadas."
        )
    elif elem_sol and elem_asc and {elem_sol, elem_asc} in ({"Fuego", "Aire"}, {"Tierra", "Agua"}):
        rel_sol_asc = (
            f"El Sol en {sol_signo} y el Ascendente en {asc_signo} pertenecen a elementos compatibles. "
            f"Esto puede ayudar a que tu manera de reaccionar y tu dirección principal se apoyen con cierta fluidez."
        )
    else:
        rel_sol_asc = (
            f"El Sol en {sol_signo} y el Ascendente en {asc_signo} pertenecen a elementos con lógicas diferentes. "
            f"Esto puede hacer que vivas las cosas de una forma, mientras otra parte de ti necesita orientarse desde un ritmo completamente diferente."
        )

    if asp_sol_asc:
        rel_sol_asc += (
            f" Además, el Sol hace {asp_sol_asc['tipo'].lower()} con el Ascendente "
            f"(orbe {asp_sol_asc['orbe']}°), por lo que esta relación tiene un peso especial en la carta."
        )

    if sol_signo == nn_signo:
        rel_nodos = (
            f"El Sol y el Nodo Norte están en {nn_signo}. "
            f"Esto une tu dirección principal con una zona importante de crecimiento. "
            f"Puede haber una sensación más clara de hacia dónde avanzar, aunque eso no significa que el trabajo ya esté hecho."
        )
    elif sol_signo == ns_signo:
        rel_nodos = (
            f"El Sol está en el mismo signo que el Nodo Sur, {ns_signo}. "
            f"Esto refuerza patrones conocidos y formas de funcionar que pueden sentirse muy naturales. "
            f"El movimiento hacia el Nodo Norte en {nn_signo} requiere más consciencia y decisión."
        )
    elif asp_sol_nn:
        rel_nodos = (
            f"El Sol en {sol_signo} hace {asp_sol_nn['tipo'].lower()} con el Nodo Norte en {nn_signo} "
            f"(orbe {asp_sol_nn['orbe']}°). "
            f"Esta relación muestra cómo tu dirección principal dialoga con aquello que necesitas desarrollar."
        )
    elif asp_sol_ns:
        rel_nodos = (
            f"El Sol en {sol_signo} hace {asp_sol_ns['tipo'].lower()} con el Nodo Sur en {ns_signo} "
            f"(orbe {asp_sol_ns['orbe']}°). "
            f"Esta relación muestra cómo tu dirección principal se conecta con patrones conocidos que pueden seguir teniendo mucho peso."
        )

    else:
        rel_nodos = (
            f"El Sol en {sol_signo}, Casa {sol_casa}, no forma aspectos mayores con los Nodos. "
            f"Esto indica que la dirección solar y el recorrido evolutivo descrito por los Nodos "
            f"funcionan como capas relativamente independientes dentro de la carta. "
            f"No significa que no se relacionen, sino que esa relación no está marcada por un aspecto directo."
        )

    rel_nodos_asc = ""

    if asp_nn_asc:
        rel_nodos_asc += (
            f"\n\nEl Nodo Norte hace {asp_nn_asc['tipo'].lower()} con el Ascendente "
            f"(orbe {asp_nn_asc['orbe']}°). "
            f"Esto indica que la dirección de crecimiento también toca directamente tu manera de entrar en la vida y posicionarte."
        )

    if asp_ns_asc:
        rel_nodos_asc += (
            f"\n\nEl Nodo Sur hace {asp_ns_asc['tipo'].lower()} con el Ascendente "
            f"(orbe {asp_ns_asc['orbe']}°). "
            f"Esto muestra que algunos patrones conocidos pueden estar muy incorporados en tu forma espontánea de reaccionar."
        )

    return (
        f"El Sol está en {sol_signo}, Casa {sol_casa}. "
        f"El Ascendente está en {asc_signo}. "
        f"El Nodo Norte está en {nn_signo}, Casa {nn_casa}, y el Nodo Sur en {ns_signo}, Casa {ns_casa}.\n\n"
        f"{rel_sol_asc}\n\n"
        f"{rel_nodos}"
        f"{rel_nodos_asc}"
    )

def texto_sol(carta, aspectos):
    planetas = carta["planetas"]

    sol = planetas.get("Sol", {})
    sol_signo = sol.get("signo", "")
    sol_casa  = sol.get("casa", 1)

    t = ""

    texto_signo = SOL_SIGNO.get(sol_signo, "")
    if texto_signo:
        t += texto_signo

    texto_casa = SOL_CASA.get(sol_casa, "")
    if texto_casa:
        t += "\n\n" + texto_casa

    # Aspectos del Sol
    asp_relevantes = [
        a for a in aspectos
        if a.get("p1") == "Sol" or a.get("p2") == "Sol"
    ]

    for asp in asp_relevantes:

        clave1 = (asp["p1"], asp["p2"], asp["simbolo"])
        clave2 = (asp["p2"], asp["p1"], asp["simbolo"])

        texto_asp = None

        # Sol ↔ Nodos
        texto_asp = (
            ASPECTOS_SOL_NODOS.get(clave1)
            or ASPECTOS_SOL_NODOS.get(clave2)
        )

        # Sol ↔ Ascendente
        if not texto_asp:
            texto_asp = (
                ASPECTOS_SOL_ASC.get(clave1)
                or ASPECTOS_SOL_ASC.get(clave2)
            )

        # Sol ↔ resto de planetas
        if not texto_asp:
            texto_asp = texto_aspecto_sol_planeta(asp)

        if texto_asp:
            t += f"\n\n{texto_asp}"

    return t

def texto_interceptaciones(carta):
    partes = []
    cuspides = carta["cuspides"]
    sol = carta["planetas"].get("Sol", {})

    sol_signo = sol.get("signo", "")
    sol_casa = sol.get("casa", "")

    if sol_signo and signo_interceptado(sol_signo, cuspides):
        partes.append(
            f"El Sol está en {sol_signo} interceptado, en Casa {sol_casa}. "
            f"Esto puede hacer que la dirección solar no salga de forma inmediata o evidente. "
            f"La fuerza está, pero puede necesitar más tiempo, más consciencia y mejores condiciones para expresarse con claridad. "
            f"No indica ausencia de dirección, sino una dirección que requiere ser desbloqueada poco a poco y llevada a la vida de una forma más deliberada."
        )

    return "\n\n".join(partes)

def aspectos_de_punto(aspectos, nombre_punto):
    """
    Devuelve todos los aspectos en los que participa un punto concreto.
    """

    return [
        aspecto
        for aspecto in aspectos
        if nombre_punto in (
            aspecto.get("p1"),
            aspecto.get("p2"),
        )
    ]

def otro_punto_del_aspecto(aspecto, nombre_punto):
    """
    Devuelve el otro planeta o punto implicado en el aspecto.
    """

    if aspecto.get("p1") == nombre_punto:
        return aspecto.get("p2", "")

    if aspecto.get("p2") == nombre_punto:
        return aspecto.get("p1", "")

    return ""

ASPECTOS_ASC_PLANETAS = {

# ───────────────────────────────────────────────────────────────
# CONJUNCIONES
# ───────────────────────────────────────────────────────────────

("Ascendente", "Sol", "="): (
    "El Ascendente y el Sol avanzan en la misma dirección. La forma en la que afrontas la vida y aquello "
    "que necesitas desarrollar para sentirte plenamente tú suelen apoyarse mutuamente.\n\n"

    "Esta coherencia facilita actuar con autenticidad y mostrarte de una forma bastante natural. El aprendizaje "
    "consiste en seguir desarrollando esa dirección conscientemente, sin darla por hecha."
),

("Ascendente", "Luna", "="): (
    "La forma en la que afrontas la vida y tus necesidades emocionales están profundamente conectadas. Lo que "
    "sientes influye directamente en la manera en la que respondes al mundo.\n\n"

    "Cuando existe equilibrio emocional, tu forma de actuar resulta mucho más fluida. El reto aparece cuando el "
    "estado de ánimo termina marcando todas tus decisiones."
),

("Ascendente", "Mercurio", "="): (
    "Comprender lo que ocurre forma parte de tu manera natural de afrontar la vida. Necesitas pensar, preguntar "
    "y poner palabras a lo que sucede para encontrar una respuesta coherente.\n\n"

    "La mente se convierte en una gran aliada siempre que el análisis no sustituya completamente a la experiencia."
),

("Ascendente", "Venus", "="): (
    "La armonía, los vínculos y aquello que valoras forman parte de tu manera espontánea de responder al mundo. "
    "Necesitas sentir cierta coherencia entre lo que haces y aquello que realmente aprecias.\n\n"

    "Cuando existe belleza, equilibrio o disfrute, tu confianza aumenta y resulta más sencillo afrontar lo que ocurre."
),

("Ascendente", "Marte", "="): (
    "La acción forma parte de tu respuesta natural ante la vida. Necesitas sentir que puedes intervenir, decidir "
    "y poner en marcha aquello que consideras importante.\n\n"

    "La iniciativa suele convertirse en uno de tus principales recursos, siempre que la rapidez no sustituya a la reflexión."
),

("Ascendente", "Júpiter", "="): (
    "Tiendes a afrontar la vida con una mirada amplia y abierta al crecimiento. Buscar posibilidades, aprender y "
    "encontrar sentido suele ayudarte a responder con confianza.\n\n"

    "Cuando esta energía encuentra equilibrio, aporta entusiasmo y capacidad para abrir caminos sin perder contacto con la realidad."
),

("Ascendente", "Saturno", "="): (
    "La prudencia, la responsabilidad y la necesidad de construir sobre bases sólidas forman parte de tu manera de "
    "afrontar la vida. Antes de actuar, necesitas sentir que existe cierta estabilidad.\n\n"

    "Con el tiempo, esta energía puede convertirse en una gran fortaleza, siempre que la cautela no termine frenando "
    "excesivamente tu capacidad para avanzar."
),

("Ascendente", "Urano", "="): (
    "Necesitas afrontar la vida desde tu propio criterio. La libertad para pensar, cuestionar y explorar caminos "
    "diferentes forma parte de tu manera natural de responder al mundo.\n\n"

    "Cuando puedes mantener esa independencia sin aislarte de las demás personas, esta energía aporta creatividad, "
    "autenticidad y una gran capacidad de adaptación."
),

("Ascendente", "Neptuno", "="): (
    "La intuición y la sensibilidad acompañan tu forma de afrontar la vida. Muchas veces percibes el ambiente antes "
    "de comprenderlo racionalmente, y esa percepción influye en tus respuestas.\n\n"

    "El aprendizaje consiste en confiar en esa sensibilidad sin perder claridad sobre lo que realmente está ocurriendo."
),

("Ascendente", "Plutón", "="): (
    "Tu manera de afrontar la vida posee una gran intensidad. Sueles percibir rápidamente aquello que necesita cambiar "
    "y rara vez permaneces indiferente ante los procesos de transformación.\n\n"

    "Cuando esta energía madura, aporta una enorme capacidad para atravesar cambios profundos sin perder el contacto contigo misma."
),


("Ascendente", "Quirón", "="): (
    "La conjunción entre el Ascendente y Quirón sitúa una zona especialmente sensible muy cerca "
    "de tu manera espontánea de afrontar la vida. Algunas situaciones pueden activar con rapidez "
    "la sensación de no encajar, quedar expuesta o no disponer de una respuesta suficientemente "
    "segura ante lo que ocurre.\n\n"

    "Esta sensibilidad influye en la forma en la que te muestras, te posicionas y reaccionas ante "
    "situaciones nuevas. Con el tiempo puede convertirse también en una capacidad profunda para "
    "comprender experiencias humanas que otras personas no siempre saben nombrar. La cuestión no "
    "es dejar de sentir esa vulnerabilidad, sino evitar que termine organizando por completo tu "
    "manera de relacionarte con la vida."
),

("Ascendente", "Lilith", "="): (
    "La conjunción entre el Ascendente y Lilith incorpora una fuerza instintiva y difícil de domesticar "
    "a tu manera de afrontar la vida. Puedes percibir rápidamente cuándo una situación exige adaptarte "
    "de una forma que contradice algo esencial en ti, y la respuesta puede aparecer antes incluso de que "
    "sepas explicarla racionalmente.\n\n"

    "Esta configuración aporta autenticidad y capacidad para cuestionar expectativas que resultan "
    "artificiales, aunque también puede intensificar la necesidad de proteger tu independencia. Su mejor "
    "expresión aparece cuando esa fuerza te ayuda a posicionarte con claridad sin convertir toda diferencia "
    "en enfrentamiento o distancia."
),

# ───────────────────────────────────────────────────────────────
# SEXTILES
# ───────────────────────────────────────────────────────────────

("Ascendente", "Sol", "✶"): (
    "El sextil entre el Ascendente y el Sol facilita que tu manera de afrontar la vida y tu dirección "
    "vital colaboren entre sí. Sueles encontrar oportunidades para expresar quién eres de una forma "
    "bastante natural.\n\n"

    "Esta facilidad necesita ser utilizada conscientemente. Cuanto más alineas tus decisiones con lo "
    "que realmente tiene sentido para ti, mayor coherencia encuentras en tu camino."
),

("Ascendente", "Luna", "✶"): (
    "El sextil entre el Ascendente y la Luna facilita la colaboración entre tu manera de responder a la "
    "vida y tus necesidades emocionales. Suele existir una vía disponible para reconocer cómo te afecta "
    "una situación y encontrar una forma de actuar que no te deje completamente fuera.\n\n"

    "Este aspecto puede ayudarte a transmitir cercanía y adaptarte sin perder el contacto con lo que "
    "sientes. La facilidad necesita ser utilizada conscientemente para convertirse en un verdadero apoyo."
),

("Ascendente", "Mercurio", "✶"): (
    "El sextil entre el Ascendente y Mercurio favorece la comprensión de lo que estás viviendo. Pensar, "
    "dialogar y poner palabras a lo que ocurre suele ayudarte a responder con mayor claridad.\n\n"

    "La comunicación puede convertirse en uno de tus principales recursos siempre que utilices esa "
    "capacidad para acercarte a la realidad y no únicamente para analizarla."
),

("Ascendente", "Venus", "✶"): (
    "El sextil entre el Ascendente y Venus facilita que el disfrute, la armonía y los vínculos aporten "
    "estabilidad a tu manera de afrontar la vida.\n\n"

    "Cuando existe belleza, equilibrio o relaciones cuidadas, te resulta más sencillo responder con "
    "confianza a los desafíos cotidianos. Esta facilidad crece cuanto más valoras aquello que realmente "
    "nutre tu vida."
),

("Ascendente", "Marte", "✶"): (
    "El sextil entre el Ascendente y Marte aporta iniciativa a tu manera de afrontar la vida. Cuando "
    "necesitas reaccionar, suele haber una vía bastante directa entre lo que percibes y la capacidad "
    "para actuar sobre ello.\n\n"

    "Este aspecto favorece la decisión y el movimiento, siempre que esa energía se utilice de forma "
    "consciente y no únicamente desde el impulso."
),

("Ascendente", "Júpiter", "✶"): (
    "El sextil entre el Ascendente y Júpiter facilita responder a la vida con una mirada amplia. "
    "Aprender, crecer y encontrar nuevas posibilidades suele fortalecer tu confianza.\n\n"

    "La facilidad aparece cuando mantienes el entusiasmo unido al sentido práctico, permitiendo que "
    "las oportunidades se conviertan en experiencias reales."
),

("Ascendente", "Saturno", "✶"): (
    "El sextil entre el Ascendente y Saturno favorece construir respuestas sólidas ante la vida. "
    "La responsabilidad, la constancia y la paciencia pueden convertirse en aliados importantes.\n\n"

    "Cuando aceptas que algunas cosas necesitan tiempo para desarrollarse, este aspecto aporta una "
    "gran estabilidad sin impedir el movimiento."
),

("Ascendente", "Urano", "✶"): (
    "El sextil entre el Ascendente y Urano facilita adaptarte a los cambios sin perder tu identidad. "
    "La creatividad, la independencia y la capacidad para encontrar soluciones diferentes suelen "
    "estar disponibles cuando las necesitas.\n\n"

    "La innovación deja de ser una necesidad de romper con todo y se convierte en una forma flexible "
    "de evolucionar."
),

("Ascendente", "Neptuno", "✶"): (
    "El sextil entre el Ascendente y Neptuno favorece que la intuición acompañe tu manera de afrontar "
    "la vida. Puedes captar matices que otras personas pasan por alto y utilizar esa sensibilidad como "
    "un recurso valioso.\n\n"

    "Cuando mantienes los pies en la realidad, esta percepción aporta profundidad y comprensión sin "
    "generar confusión."
),

("Ascendente", "Plutón", "✶"): (
    "El sextil entre el Ascendente y Plutón facilita afrontar los cambios con profundidad. Existe una "
    "capacidad natural para transformar aquello que ya no tiene sentido y adaptarte a nuevas etapas.\n\n"

    "Esta energía se convierte en un gran apoyo cuando aceptas que crecer también implica dejar atrás "
    "formas antiguas de responder a la vida."
),

("Ascendente", "Quirón", "✶"): (
    "El sextil entre el Ascendente y Quirón ofrece una vía disponible para transformar ciertas "
    "experiencias sensibles en comprensión y recursos propios. Tu manera de afrontar la vida puede "
    "ayudarte a acercarte gradualmente a aquello que en otros momentos generó inseguridad, exposición "
    "o sensación de no encajar.\n\n"

    "Esta relación favorece que la vulnerabilidad no sea únicamente un lugar de dificultad, sino "
    "también una fuente de sensibilidad hacia lo que viven otras personas. El recurso se desarrolla "
    "cuando eliges acercarte conscientemente a esa zona en lugar de limitarte a evitarla."
),

("Ascendente", "Lilith", "✶"): (
    "El sextil entre el Ascendente y Lilith ofrece una vía para incorporar tu parte más instintiva y libre "
    "a la forma en la que respondes a la vida. Existe una capacidad disponible para reconocer lo que no "
    "encaja contigo y encontrar maneras propias de posicionarte sin necesidad de romper continuamente con "
    "el entorno.\n\n"

    "Este recurso necesita ser utilizado conscientemente. Cuando escuchas esa incomodidad y la traduces en "
    "límites, decisiones o cambios concretos, puede ayudarte a vivir con mayor autenticidad sin quedar "
    "atrapada únicamente en la oposición."
),

# ───────────────────────────────────────────────────────────────
# CUADRATURAS
# ───────────────────────────────────────────────────────────────

("Ascendente", "Sol", "□"): (
    "La cuadratura entre el Ascendente y el Sol puede hacer que la forma espontánea en la que respondes a la vida "
    "y la dirección que necesitas desarrollar no siempre avancen al mismo ritmo. A veces reaccionas de una manera "
    "mientras otra parte de ti necesita algo diferente para sentirse plenamente realizada.\n\n"

    "Esta tensión impulsa a revisar quién responde y desde dónde lo hace. El aprendizaje consiste en construir una "
    "forma de vivir donde tu manera de actuar y tu dirección vital puedan colaborar en lugar de competir."
),

("Ascendente", "Luna", "□"): (
    "La cuadratura entre el Ascendente y la Luna puede hacer que tus necesidades emocionales y tu forma de responder "
    "al mundo no siempre coincidan. En algunos momentos puedes actuar dejando tus emociones en segundo plano; en otros, "
    "el estado emocional puede condicionar excesivamente tus respuestas.\n\n"

    "El trabajo consiste en aprender a escuchar lo que sientes sin que ello impida responder con claridad a lo que "
    "la situación necesita."
),

("Ascendente", "Mercurio", "□"): (
    "La cuadratura entre el Ascendente y Mercurio puede generar tensión entre la necesidad de comprender y la de actuar. "
    "A veces puedes pensar demasiado antes de responder; otras, responder y comprender después.\n\n"

    "El aprendizaje consiste en integrar pensamiento y acción, permitiendo que ambos colaboren en lugar de bloquearse mutuamente."
),

("Ascendente", "Venus", "□"): (
    "La cuadratura entre el Ascendente y Venus puede hacer que aquello que valoras, deseas o disfrutas no siempre coincida "
    "con la forma en la que afrontas determinadas situaciones. En ocasiones puedes adaptarte demasiado para mantener la armonía "
    "o reaccionar olvidando aquello que realmente tiene valor para ti.\n\n"

    "La integración aparece cuando tus decisiones respetan tanto tus necesidades como las de las personas que te rodean."
),

("Ascendente", "Marte", "□"): (
    "La cuadratura entre el Ascendente y Marte puede hacer que la iniciativa aparezca con demasiada intensidad o que, por el "
    "contrario, quede bloqueada en los momentos en los que más la necesitas. Encontrar el ritmo adecuado para actuar suele ser "
    "uno de los principales aprendizajes de este aspecto.\n\n"

    "Con el tiempo puedes desarrollar una forma de responder firme y decidida sin necesidad de vivir permanentemente en tensión."
),

("Ascendente", "Júpiter", "□"): (
    "La cuadratura entre el Ascendente y Júpiter puede hacer que la confianza y la expansión no siempre acompañen a tu manera "
    "espontánea de afrontar la vida. A veces puedes asumir más de lo que realmente puedes sostener; otras, limitarte por miedo "
    "a equivocarte.\n\n"

    "El aprendizaje consiste en construir una confianza basada en la experiencia y no únicamente en el entusiasmo o en la prudencia."
),

("Ascendente", "Saturno", "□"): (
    "La cuadratura entre el Ascendente y Saturno puede hacer que la responsabilidad, la exigencia o el miedo al error condicionen "
    "tu forma de responder a la vida. Es posible sentir que siempre hay algo que demostrar o controlar antes de dar un paso.\n\n"

    "Con el tiempo esta tensión puede transformarse en una gran capacidad para actuar con serenidad, aceptando que la seguridad "
    "también se construye mientras avanzas."
),

("Ascendente", "Urano", "□"): (
    "La cuadratura entre el Ascendente y Urano puede generar tensión entre la necesidad de estabilidad y el deseo de cambio. "
    "En algunos momentos puedes romper demasiado deprisa con lo conocido; en otros, resistirte a cambios que ya están pidiendo paso.\n\n"

    "El aprendizaje consiste en permitir que la evolución forme parte de tu vida sin que cada cambio implique romper con todo lo anterior."
),

("Ascendente", "Neptuno", "□"): (
    "La cuadratura entre el Ascendente y Neptuno puede hacer que la intuición, la imaginación o la sensibilidad dificulten a veces "
    "distinguir con claridad qué está ocurriendo realmente. Algunas situaciones pueden vivirse desde expectativas, idealizaciones "
    "o percepciones poco definidas.\n\n"

    "La integración llega cuando aprendes a escuchar tu intuición sin dejar de apoyarte en la realidad y en la experiencia concreta."
),

("Ascendente", "Plutón", "□"): (
    "La cuadratura entre el Ascendente y Plutón puede hacer que algunos cambios se vivan con gran intensidad. La necesidad de protegerte, "
    "controlar o resistirte a determinadas transformaciones puede condicionar tu forma de responder a la vida.\n\n"

    "El aprendizaje consiste en descubrir que no toda transformación supone una amenaza. Cuando aceptas el cambio como parte del proceso, "
    "aparece una fortaleza mucho más profunda y estable."
),

("Ascendente", "Quirón", "□"): (
    "La cuadratura entre el Ascendente y Quirón señala una zona sensible en la manera de mostrarte, "
    "actuar u ocupar espacio frente a otras personas. Algunas situaciones pueden activar rápidamente "
    "la sensación de no encajar, no saber cómo posicionarte o quedar expuesta de una forma incómoda.\n\n"

    "Esta tensión también puede desarrollar una gran capacidad para comprender a quienes atraviesan "
    "dificultades parecidas. El trabajo consiste en no construir toda tu forma de afrontar la vida "
    "alrededor de evitar esa herida, sino permitir que la experiencia vaya creando una posición más "
    "propia y menos condicionada por el miedo a no ser comprendida."
),

("Ascendente", "Lilith", "□"): (
    "La cuadratura entre el Ascendente y Lilith puede generar tensión entre la manera en la que intentas "
    "desenvolverte en el mundo y una parte de ti que se resiste profundamente a ciertas normas, expectativas "
    "o formas de adaptación.\n\n"

    "En algunos momentos puedes contener demasiado esa fuerza para evitar conflicto y, en otros, expresarla "
    "de una manera que dificulta el diálogo. La integración aparece cuando puedes reconocer qué límite necesita "
    "ser defendido sin convertir automáticamente toda incomodidad en rechazo o confrontación."
),

# ───────────────────────────────────────────────────────────────
# TRÍGONOS
# ───────────────────────────────────────────────────────────────

("Ascendente", "Sol", "△"): (
    "El trígono entre el Ascendente y el Sol favorece una relación fluida entre la manera en la que "
    "afrontas la vida y la dirección que necesitas desarrollar. Con frecuencia te resulta natural actuar "
    "de acuerdo con aquello que da sentido a tu camino.\n\n"

    "Esta facilidad puede convertirse en una gran fortaleza siempre que no des por supuesto ese equilibrio "
    "y continúes desarrollándolo de forma consciente."
),

("Ascendente", "Luna", "△"): (
    "El trígono entre el Ascendente y la Luna facilita que tus emociones y tu manera de responder al mundo "
    "colaboren entre sí. Sueles reconocer con bastante facilidad qué necesitas y actuar en consecuencia.\n\n"

    "Cuando escuchas tu mundo emocional sin depender completamente de él, esta armonía aporta una gran "
    "sensación de coherencia y estabilidad."
),

("Ascendente", "Mercurio", "△"): (
    "El trígono entre el Ascendente y Mercurio favorece comprender rápidamente lo que está ocurriendo. "
    "Pensamiento, comunicación y acción suelen apoyarse mutuamente.\n\n"

    "Esta facilidad puede ayudarte a aprender, explicar y adaptarte con rapidez, siempre que no sustituya "
    "la experiencia por el análisis constante."
),

("Ascendente", "Venus", "△"): (
    "El trígono entre el Ascendente y Venus facilita responder a la vida desde el equilibrio y el respeto "
    "por aquello que realmente valoras. Existe una tendencia natural a buscar armonía sin perder de vista "
    "tus propias necesidades.\n\n"

    "Cuando desarrollas conscientemente esta energía, los vínculos y el disfrute se convierten en un apoyo "
    "importante para afrontar los desafíos cotidianos."
),

("Ascendente", "Marte", "△"): (
    "El trígono entre el Ascendente y Marte favorece actuar con decisión cuando una situación lo requiere. "
    "La iniciativa suele aparecer con naturalidad y ayudarte a avanzar sin demasiados bloqueos.\n\n"

    "Esta energía resulta especialmente útil cuando se pone al servicio de aquello que realmente merece tu esfuerzo."
),

("Ascendente", "Júpiter", "△"): (
    "El trígono entre el Ascendente y Júpiter facilita afrontar la vida con confianza y amplitud de miras. "
    "Sueles encontrar oportunidades para aprender, crecer y ampliar horizontes sin perder fácilmente la motivación.\n\n"

    "Cuando esta energía se desarrolla conscientemente, aporta optimismo sereno y capacidad para avanzar "
    "sin necesidad de exagerar posibilidades."
),

("Ascendente", "Saturno", "△"): (
    "El trígono entre el Ascendente y Saturno favorece construir una forma de afrontar la vida estable y "
    "bien organizada. La responsabilidad y la constancia suelen convertirse en apoyos naturales.\n\n"

    "Esta facilidad permite sostener procesos largos con paciencia, siempre que no termine convirtiéndose "
    "en una rigidez innecesaria."
),

("Ascendente", "Urano", "△"): (
    "El trígono entre el Ascendente y Urano facilita adaptarte a los cambios conservando tu autenticidad. "
    "La independencia de criterio y la creatividad suelen integrarse de forma natural en tu manera de responder.\n\n"

    "Cuando aprovechas esta energía conscientemente, puedes evolucionar con libertad sin necesidad de romper "
    "constantemente con lo anterior."
),

("Ascendente", "Neptuno", "△"): (
    "El trígono entre el Ascendente y Neptuno favorece una sensibilidad que puede convertirse en una gran guía. "
    "La intuición suele acompañar tus decisiones y ayudarte a percibir aspectos que otras personas pasan por alto.\n\n"

    "Cuando mantienes el contacto con la realidad, esta energía aporta una comprensión profunda y una gran "
    "capacidad de empatía."
),

("Ascendente", "Plutón", "△"): (
    "El trígono entre el Ascendente y Plutón facilita atravesar los cambios con profundidad y fortaleza. "
    "Existe una capacidad natural para transformar aquello que ya no tiene sentido sin perder el centro.\n\n"

    "Cuando desarrollas conscientemente esta energía, cada transformación se convierte en una oportunidad "
    "para responder a la vida desde un lugar más auténtico."
),

("Ascendente", "Quirón", "△"): (
    "El trígono entre el Ascendente y Quirón facilita que ciertas experiencias sensibles encuentren "
    "una vía natural de expresión y elaboración. Puedes reconocer con bastante facilidad aquello que "
    "te afecta y desarrollar una comprensión profunda sobre las dificultades que atraviesan otras personas.\n\n"

    "Esta sensibilidad puede convertirse en un recurso importante para acompañar, orientar o sostener, "
    "aunque existe el riesgo de acostumbrarte tanto a convivir con ella que no atiendas tus propias "
    "necesidades. Su mejor expresión aparece cuando la comprensión hacia otras personas también incluye "
    "el cuidado de tu propia vulnerabilidad."
),


("Ascendente", "Lilith", "△"): (
    "El trígono entre el Ascendente y Lilith facilita una relación natural con tu parte más instintiva, libre "
    "y poco dispuesta a someterse a formas que siente artificiales. Suele existir bastante coherencia entre "
    "lo que percibes internamente y la manera en la que te posicionas ante el mundo.\n\n"

    "Esta fluidez aporta autenticidad y capacidad para cuestionar mandatos que ya no tienen sentido, aunque "
    "también puede hacer que algunas respuestas se den por válidas únicamente porque resultan espontáneas. "
    "Desarrollada conscientemente, esta energía permite defender tu lugar sin necesidad de aislarte."
),

# ───────────────────────────────────────────────────────────────
# OPOSICIONES
# ───────────────────────────────────────────────────────────────

("Ascendente", "Sol", "☍"): (
    "La oposición entre el Ascendente y el Sol puede hacer que la dirección que necesitas desarrollar "
    "aparezca muchas veces a través de otras personas o de situaciones que desafían tu forma habitual "
    "de responder a la vida.\n\n"

    "El aprendizaje consiste en dejar de vivir ambas energías como polos enfrentados y descubrir que tu "
    "manera de afrontar la vida también puede evolucionar a medida que desarrollas tu verdadera dirección."
),

("Ascendente", "Luna", "☍"): (
    "La oposición entre el Ascendente y la Luna puede hacer que tus necesidades emocionales y tu manera "
    "de responder a la vida parezcan tirar en direcciones distintas. En algunos momentos priorizas la "
    "adaptación al entorno; en otros, la necesidad emocional ocupa todo el espacio.\n\n"

    "El aprendizaje consiste en reconocer ambas necesidades sin permitir que una anule completamente a la otra."
),

("Ascendente", "Mercurio", "☍"): (
    "La oposición entre el Ascendente y Mercurio puede hacer que la necesidad de comprender y la necesidad "
    "de actuar aparezcan en momentos diferentes. A veces piensas demasiado antes de responder; otras, la "
    "respuesta llega antes de haber terminado de comprender la situación.\n\n"

    "El reto consiste en permitir que pensamiento y acción colaboren, en lugar de alternarse continuamente."
),

("Ascendente", "Venus", "☍"): (
    "La oposición entre el Ascendente y Venus puede hacer que aquello que valoras o necesitas en tus vínculos "
    "aparezca reflejado a través de otras personas. Algunas relaciones pueden mostrarte aspectos de ti que "
    "todavía necesitan integrarse.\n\n"

    "El aprendizaje consiste en construir relaciones donde la armonía no dependa de dejar de lado tus propias necesidades."
),

("Ascendente", "Marte", "☍"): (
    "La oposición entre el Ascendente y Marte puede hacer que la iniciativa, el conflicto o la capacidad para "
    "actuar aparezcan con frecuencia proyectados en el entorno. Algunas personas pueden mostrar una firmeza que "
    "a ti te cuesta expresar en determinados momentos.\n\n"

    "El trabajo consiste en recuperar esa capacidad de acción sin necesidad de enfrentarte constantemente al mundo."
),

("Ascendente", "Júpiter", "☍"): (
    "La oposición entre el Ascendente y Júpiter puede hacer que la expansión, la confianza o las grandes "
    "posibilidades aparezcan a través de otras personas. Es posible que el entorno te anime a crecer, arriesgar "
    "o mirar más lejos de lo que harías desde tu reacción inicial.\n\n"

    "El reto está en no delegar completamente fuera la confianza o la dirección. Cuando integras esta energía, "
    "puedes ampliar tu manera de afrontar la vida sin perder contacto con tus propios límites."
),

("Ascendente", "Saturno", "☍"): (
    "La oposición entre el Ascendente y Saturno puede hacer que los límites, la responsabilidad o la exigencia "
    "aparezcan representados por personas o circunstancias externas. A veces puedes sentir que el mundo pone más "
    "obstáculos de los que realmente existen.\n\n"

    "Con el tiempo descubres que la verdadera seguridad no depende únicamente de las condiciones externas, sino "
    "de la capacidad para sostener tus propios compromisos."
),

("Ascendente", "Urano", "☍"): (
    "La oposición entre el Ascendente y Urano puede hacer que el cambio, la necesidad de libertad o lo inesperado "
    "aparezcan con frecuencia a través de otras personas. Algunas relaciones pueden impulsarte a salir de formas "
    "de vida que ya habían dejado de tener sentido.\n\n"

    "El aprendizaje consiste en incorporar esa libertad a tu propia manera de responder, sin esperar siempre que "
    "sea el entorno quien provoque el cambio."
),

("Ascendente", "Neptuno", "☍"): (
    "La oposición entre el Ascendente y Neptuno puede hacer que la sensibilidad, la idealización o la confusión "
    "aparezcan especialmente en las relaciones y en la forma de interpretar a otras personas.\n\n"

    "El trabajo consiste en desarrollar una mirada compasiva sin perder claridad sobre la realidad, aprendiendo a "
    "distinguir entre intuición, deseo y hechos."
),

("Ascendente", "Plutón", "☍"): (
    "La oposición entre el Ascendente y Plutón puede hacer que los procesos de transformación, el poder o la "
    "intensidad aparezcan frecuentemente a través de otras personas. Algunas relaciones pueden remover aspectos "
    "muy profundos de tu manera de afrontar la vida.\n\n"

    "El aprendizaje consiste en reconocer esa fuerza transformadora como una capacidad propia, evitando que el "
    "cambio dependa siempre de circunstancias externas o de vínculos especialmente intensos."
),

("Ascendente", "Quirón", "☍"): (
    "La oposición entre el Ascendente y Quirón puede hacer que determinadas heridas o inseguridades "
    "aparezcan reflejadas con especial intensidad a través de otras personas. Algunos vínculos pueden "
    "activar la sensación de no encajar, no ser comprendida o quedar expuesta en aspectos que preferirías "
    "mantener protegidos.\n\n"

    "La relación con el entorno puede convertirse así en un territorio de gran sensibilidad, pero también "
    "de comprensión y reparación. La clave está en reconocer qué parte de esa vulnerabilidad pertenece "
    "realmente al vínculo presente y qué parte procede de experiencias anteriores que todavía influyen "
    "en tu forma de posicionarte."
),


("Ascendente", "Lilith", "☍"): (
    "La oposición entre el Ascendente y Lilith puede hacer que la rebeldía, la incomodidad o la necesidad "
    "de libertad aparezcan con frecuencia representadas por otras personas. Algunos vínculos pueden mostrarte "
    "una fuerza que te cuesta reconocer como propia o activar un rechazo intenso hacia comportamientos que "
    "tocan una parte no integrada de ti.\n\n"

    "El proceso consiste en recuperar esa capacidad de cuestionar y poner límites sin necesitar que siempre "
    "sea el entorno quien la exprese. Cuanto más reconoces esa parte como propia, menos depende de relaciones "
    "especialmente tensas o polarizadas."
),


# ───────────────────────────────────────────────────────────────
# QUINCUNCIOS
# ───────────────────────────────────────────────────────────────

("Ascendente", "Sol", "⚻"): (
    "El quincuncio entre el Ascendente y el Sol puede hacer que tu manera espontánea de afrontar la vida "
    "y la dirección que necesitas desarrollar no siempre se comprendan entre sí. Ninguna de las dos está "
    "equivocada, pero funcionan con ritmos diferentes.\n\n"

    "A lo largo de la vida irás realizando pequeños reajustes que permitan responder de una forma cada vez "
    "más coherente con quien realmente estás llegando a ser."
),

("Ascendente", "Luna", "⚻"): (
    "El quincuncio entre el Ascendente y la Luna puede hacer que tus necesidades emocionales cambien más "
    "rápido que tu forma habitual de responder al mundo. En algunos momentos puedes darte cuenta de lo que "
    "necesitas cuando ya has reaccionado.\n\n"

    "El aprendizaje consiste en introducir pequeños ajustes que permitan cuidar tu mundo emocional sin tener "
    "que cambiar completamente tu manera de actuar."
),

("Ascendente", "Mercurio", "⚻"): (
    "El quincuncio entre el Ascendente y Mercurio puede hacer que pensamiento y acción necesiten reajustes "
    "constantes. Hay momentos en los que comprendes demasiado tarde una situación y otros en los que el análisis "
    "retrasa respuestas que necesitaban ser más sencillas.\n\n"

    "La integración aparece cuando permites que comprender y actuar encuentren un ritmo más parecido."
),

("Ascendente", "Venus", "⚻"): (
    "El quincuncio entre el Ascendente y Venus puede hacer que tus valores o la forma en la que construyes "
    "los vínculos necesiten revisiones periódicas para seguir acompañando tu manera de afrontar la vida.\n\n"

    "No se trata de elegir entre agradar o actuar, sino de ir ajustando ambas necesidades para que puedan "
    "convivir con mayor naturalidad."
),

("Ascendente", "Marte", "⚻"): (
    "El quincuncio entre el Ascendente y Marte puede hacer que la iniciativa aparezca en momentos diferentes "
    "a aquellos en los que realmente la necesitas. A veces actúas demasiado pronto; otras, demasiado tarde.\n\n"

    "El aprendizaje consiste en afinar progresivamente el momento de intervenir, encontrando un equilibrio "
    "entre impulso y reflexión."
),

("Ascendente", "Júpiter", "⚻"): (
    "El quincuncio entre el Ascendente y Júpiter puede hacer que la confianza y tu manera de responder a la "
    "vida no siempre evolucionen al mismo ritmo. Hay momentos en los que asumes más de lo que puedes sostener "
    "y otros en los que limitas posibilidades que sí estaban a tu alcance.\n\n"

    "La experiencia irá enseñándote a ajustar mejor el tamaño de cada paso."
),

("Ascendente", "Saturno", "⚻"): (
    "El quincuncio entre el Ascendente y Saturno puede hacer que la responsabilidad y la espontaneidad necesiten "
    "reajustes frecuentes. En algunos momentos puedes sentir que la prudencia limita respuestas que necesitaban "
    "más movimiento; en otros, descubres que hacía falta más preparación.\n\n"

    "El aprendizaje consiste en encontrar una forma de avanzar que respete tanto la libertad como la responsabilidad."
),

("Ascendente", "Urano", "⚻"): (
    "El quincuncio entre el Ascendente y Urano puede hacer que la necesidad de cambio aparezca de maneras poco "
    "previsibles. Algunas etapas pedirán estabilidad mientras otra parte de ti ya necesita evolucionar.\n\n"

    "Con el tiempo aprenderás a introducir cambios graduales, evitando que la única alternativa sea romper con todo."
),

("Ascendente", "Neptuno", "⚻"): (
    "El quincuncio entre el Ascendente y Neptuno puede hacer que intuición y realidad necesiten reajustes "
    "continuos. A veces percibes con mucha claridad aspectos sutiles; otras, resulta difícil distinguir qué "
    "pertenece a la intuición y qué nace de expectativas o deseos.\n\n"

    "La integración consiste en permitir que sensibilidad y claridad se apoyen mutuamente."
),

("Ascendente", "Plutón", "⚻"): (
    "El quincuncio entre el Ascendente y Plutón puede hacer que los procesos de transformación aparezcan de "
    "forma gradual, obligándote a revisar periódicamente la manera en la que respondes a la vida.\n\n"

    "Cada ajuste te permite soltar antiguas formas de protegerte y responder desde un lugar cada vez más auténtico."
),

("Ascendente", "Quirón", "⚻"): (
    "El quincuncio entre el Ascendente y Quirón puede exigir reajustes continuos entre tu manera habitual "
    "de afrontar la vida y una zona interna especialmente sensible. En algunos momentos puedes reaccionar "
    "intentando protegerte demasiado; en otros, exponerte antes de disponer de los recursos necesarios "
    "para sostener lo que se activa.\n\n"

    "No existe una respuesta única que resuelva esta relación para siempre. El proceso consiste en ajustar "
    "gradualmente la forma de mostrarte, poner límites y reconocer tu vulnerabilidad, evitando tanto ocultarla "
    "por completo como permitir que determine cada una de tus decisiones."
),

("Ascendente", "Lilith", "⚻"): (
    "El quincuncio entre el Ascendente y Lilith exige ajustes frecuentes entre tu manera de desenvolverte y "
    "una parte instintiva que no siempre acepta las condiciones necesarias para adaptarse a una situación. "
    "Puede haber momentos en los que cedes demasiado y otros en los que necesitas romper con lo establecido "
    "para recuperar sensación de autenticidad.\n\n"

    "La cuestión no es elegir entre adaptación y libertad, sino revisar continuamente qué concesiones permiten "
    "construir y cuáles empiezan a alejarte demasiado de ti. Esta relación encuentra mayor equilibrio cuando "
    "la incomodidad puede transformarse en criterio y no únicamente en reacción."
),
}

# ─── TEXTOS: ASPECTOS NODO NORTE · LUNA ──────────────────────────────────────

ASPECTOS_NODO_NORTE_LUNA = {

    ("Nodo Norte", "Luna", "="): (
        "La Luna y el Nodo Norte se encuentran en el mismo lugar, de modo que tus necesidades "
        "emocionales y la dirección de crecimiento están profundamente vinculadas. Aquello que "
        "necesitas desarrollar no aparece únicamente como una idea o una orientación externa, "
        "sino que toca directamente tu manera de buscar seguridad, pertenencia y cuidado.\n\n"

        "Esta configuración puede hacer que algunas experiencias emocionales tengan un peso "
        "especial en tu desarrollo. Los vínculos, la familia, la forma de cuidarte o la manera "
        "de reaccionar ante la vulnerabilidad pueden convertirse en espacios decisivos para "
        "avanzar. El reto está en distinguir entre una necesidad emocional auténtica y una "
        "respuesta automática que simplemente resulta familiar. Crecer no significa dejar de "
        "escucharte, sino aprender a reconocer qué formas de cuidado sostienen realmente la "
        "persona que estás intentando construir."
    ),

    ("Nodo Norte", "Luna", "✶"): (
        "El sextil entre la Luna y el Nodo Norte ofrece una vía de colaboración entre tus "
        "necesidades emocionales y la dirección de crecimiento. Existe una capacidad disponible "
        "para encontrar vínculos, espacios de cuidado y formas de sostenerte que faciliten el "
        "desarrollo de aquello que todavía necesita más presencia en tu vida.\n\n"

        "Esta relación no funciona necesariamente de manera automática. Puede haber oportunidades "
        "para crecer a través de la intimidad, la familia, el cuidado del cuerpo o una escucha más "
        "honesta de lo que sientes, pero necesitan ser reconocidas y utilizadas conscientemente. "
        "Cuando das espacio a tus necesidades sin convertirlas en una razón para permanecer en lo "
        "conocido, el mundo emocional se convierte en un apoyo importante para avanzar."
    ),

    ("Nodo Norte", "Luna", "□"): (
        "La cuadratura entre la Luna y el Nodo Norte muestra una tensión entre aquello que "
        "emocionalmente resulta familiar y la dirección que más crecimiento necesita. Es posible "
        "que algunas decisiones importantes remuevan tu sensación de seguridad, pertenencia o "
        "estabilidad, incluso cuando sabes que forman parte de un movimiento necesario.\n\n"

        "En ciertos momentos puedes sentir que avanzar implica alejarte de algo que emocionalmente "
        "te sostiene, mientras que permanecer en lo conocido limita una parte importante de tu "
        "desarrollo. La integración no consiste en ignorar lo que sientes ni en obligarte a crecer "
        "a cualquier precio, sino en construir nuevas formas de cuidado capaces de acompañar los "
        "cambios que la vida te está pidiendo."
    ),

    ("Nodo Norte", "Luna", "△"): (
        "El trígono entre la Luna y el Nodo Norte facilita que tus necesidades emocionales y la "
        "dirección de crecimiento puedan apoyarse de una forma bastante natural. Muchas veces "
        "encuentras seguridad en experiencias, vínculos o decisiones que también favorecen el "
        "desarrollo de cualidades nuevas.\n\n"

        "Esta fluidez puede ayudarte a reconocer intuitivamente qué situaciones te acercan a una "
        "vida más coherente. Sin embargo, aquello que resulta natural también puede pasar "
        "desapercibido o permanecer poco desarrollado si no se utiliza conscientemente. Cuando "
        "escuchas lo que sientes y lo conviertes en decisiones concretas, el mundo emocional puede "
        "actuar como una base estable desde la que seguir creciendo."
    ),

    ("Nodo Norte", "Luna", "☍"): (
        "La oposición entre la Luna y el Nodo Norte sitúa a la Luna cerca del Nodo Sur, por lo que "
        "las respuestas emocionales conocidas pueden tener una fuerza especial. La seguridad suele "
        "buscarse en formas de cuidado, pertenencia o reacción que has utilizado durante mucho "
        "tiempo y que resultan difíciles de abandonar, incluso cuando ya no acompañan plenamente "
        "la dirección que necesitas desarrollar.\n\n"

        "El crecimiento puede sentirse como una separación de lo familiar o como la necesidad de "
        "responder de una manera que al principio ofrece menos seguridad emocional. No se trata de "
        "rechazar tu historia ni de dejar atrás toda forma conocida de cuidado, sino de evitar que "
        "el miedo, la nostalgia o la necesidad de protección decidan siempre la dirección de tu "
        "vida. El trabajo consiste en llevar contigo los recursos emocionales del pasado sin "
        "permitir que definan por completo lo que todavía puedes llegar a construir."
    ),

    ("Nodo Norte", "Luna", "⚻"): (
        "El quincuncio entre la Luna y el Nodo Norte exige ajustes frecuentes entre tus necesidades "
        "emocionales y la dirección de crecimiento. Es posible que aquello que te ayuda a sentir "
        "seguridad en una etapa deje de ser suficiente en otra, o que determinados cambios necesiten "
        "una reorganización profunda de tus ritmos, vínculos y formas de cuidado.\n\n"

        "No suele existir una solución definitiva que permita mantener ambas dimensiones siempre "
        "equilibradas. El proceso consiste en escuchar qué necesitas en cada momento sin utilizar "
        "esa necesidad para evitar todo movimiento, y en avanzar sin dejar de atender el impacto "
        "emocional de cada cambio. Poco a poco puedes construir una forma de crecimiento que no "
        "dependa ni de permanecer siempre en lo conocido ni de exigirte una transformación que no "
        "puedes sostener."
    ),
}


ASPECTOS_NODO_NORTE_LUNA = {

("Nodo Sur", "Luna", "="): (
    "La Luna y el Nodo Sur se encuentran unidos, por lo que una parte importante de tu mundo emocional "
    "se apoya en respuestas que llevas mucho tiempo utilizando. La forma de buscar seguridad, pertenencia "
    "o protección suele aparecer de manera muy automática y puede convertirse en un lugar al que recurres "
    "siempre que la vida genera incertidumbre.\n\n"

    "Estos recursos no son un problema en sí mismos. De hecho, probablemente te han permitido sostener "
    "muchas etapas importantes. Sin embargo, cuando toda respuesta emocional nace únicamente de lo conocido, "
    "es fácil que algunas experiencias nuevas resulten más difíciles de integrar. El desarrollo no consiste "
    "en rechazar tu forma habitual de cuidarte, sino en ampliar poco a poco el espacio disponible para otras "
    "maneras de responder que también puedan ofrecer seguridad."
),

("Nodo Sur", "Luna", "✶"): (
    "El sextil entre la Luna y el Nodo Sur muestra que tus recursos emocionales más conocidos pueden "
    "convertirse en un apoyo importante para afrontar la vida. Existe una forma de cuidarte, protegerte "
    "y recuperar estabilidad que has desarrollado con el tiempo y que suele estar disponible cuando la "
    "necesitas.\n\n"

    "Esta facilidad puede ayudarte a atravesar momentos difíciles con una sensación de continuidad y "
    "confianza. Sin embargo, también existe el riesgo de recurrir siempre a las mismas respuestas aunque "
    "la situación ya necesite algo diferente. La experiencia acumulada puede ser una base muy valiosa, "
    "siempre que no impida explorar formas nuevas de relacionarte contigo y con el mundo."
),

("Nodo Sur", "Luna", "□"): (
    "La cuadratura entre la Luna y el Nodo Sur muestra una tensión entre tus necesidades emocionales y "
    "algunas formas conocidas de buscar seguridad. Puede ocurrir que determinados hábitos, vínculos o "
    "maneras de reaccionar ya no respondan completamente a lo que necesitas en la etapa actual, aunque "
    "continúen apareciendo por la sensación de protección que ofrecieron en el pasado.\n\n"

    "Esta configuración invita a revisar con honestidad qué aspectos de tu forma habitual de cuidarte "
    "siguen siendo un apoyo real y cuáles empiezan a limitar la posibilidad de responder de una manera "
    "más ajustada al presente. No se trata de abandonar tu historia emocional, sino de permitir que siga "
    "evolucionando."
),

("Nodo Sur", "Luna", "△"): (
    "El trígono entre la Luna y el Nodo Sur indica que existe una relación muy fluida entre tu mundo "
    "emocional y los recursos que has ido desarrollando a lo largo de la vida. Muchas respuestas aparecen "
    "de forma espontánea porque forman parte de una manera de protegerte que conoces profundamente.\n\n"

    "Esta facilidad aporta estabilidad y capacidad para sostener momentos difíciles, pero también puede "
    "hacer que algunas formas de reaccionar pasen desapercibidas precisamente porque resultan muy "
    "naturales. La verdadera riqueza de este aspecto aparece cuando utilizas esa experiencia como un "
    "apoyo para seguir creciendo, y no únicamente como un lugar al que regresar."
),

("Nodo Sur", "Luna", "☍"): (
    "La oposición entre la Luna y el Nodo Sur sitúa a la Luna cerca del Nodo Norte, por lo que "
    "tu mundo emocional no se organiza únicamente desde respuestas conocidas. Existe una parte de "
    "ti que necesita desarrollar nuevas formas de cuidado, seguridad y pertenencia, aunque esas "
    "formas no siempre resulten familiares al principio.\n\n"

    "Lo conocido puede seguir teniendo mucho peso, especialmente en momentos de cansancio, miedo o "
    "incertidumbre, pero no necesariamente coincide con aquello que emocionalmente necesitas construir "
    "en esta etapa. Esta configuración invita a diferenciar entre la protección que te ayudó en otros "
    "momentos y la forma de sostenerte que ahora puede permitirte avanzar con mayor coherencia."
),

("Nodo Sur", "Luna", "⚻"): (
    "El quincuncio entre la Luna y el Nodo Sur muestra que tus necesidades emocionales y algunas "
    "respuestas conocidas no siempre encajan de una forma estable. Puede ocurrir que recurras a maneras "
    "habituales de protegerte y descubras después que ya no ofrecen el mismo alivio o que dejan fuera "
    "una parte importante de lo que realmente necesitas.\n\n"

    "Esta relación pide ajustes progresivos en la forma de cuidarte, vincularte y recuperar seguridad. "
    "No se trata de abandonar por completo tus recursos emocionales anteriores, sino de revisar su medida "
    "y su función para que puedan seguir siendo útiles sin obligarte a responder siempre desde estructuras "
    "que pertenecen a otra etapa de tu vida."
),
}


def texto_ascendente(carta, aspectos=None):
    """
    Interpreta el Ascendente como cúspide de la Casa 1.

    No se le asigna una casa porque el Ascendente es precisamente
    el punto que inicia la Casa 1. Se interpreta mediante:

    - signo;
    - grado;
    - regente y posición del regente;
    - aspectos al Ascendente.
    """

    if aspectos is None:
        aspectos = []

    planetas = carta["planetas"]
    asc = carta.get("asc", {})

    asc_signo = asc.get("signo", "")
    asc_grado = asc.get("grado", 0)

    partes = []

    # Introducción común al Ascendente
    partes.append(
        "El Ascendente describe la manera más espontánea de responder a lo que la vida va poniendo delante. "
        "No habla tanto de la personalidad como de la forma habitual de interpretar lo que ocurre, "
        "de reaccionar ante situaciones nuevas y de afrontar el mundo.\n\n"

        "Conocer esta tendencia no sirve para cambiarla, sino para reconocer cuándo resulta útil "
        "y cuándo está funcionando simplemente como un mecanismo automático de protección."
    )


    # ── Ascendente por signo ─────────────────────────────────────────
    texto_signo = ASC_SIGNO.get(asc_signo, "")

    if texto_signo:
        partes.append(texto_signo)

    # ── Grado del Ascendente ─────────────────────────────────────────
    partes.append(
        f"El Ascendente se encuentra a {grado_a_dms(asc_grado)} "
        f"de {asc_signo}. Este grado concreta la forma en la que "
        f"el signo se expresa en tu manera de interpretar lo que ocurre, "
        f"posicionarte y responder ante situaciones nuevas."
    )


    # ── El regente del Ascendente ───────────────────────────────────────

    regente = REGENTE_SIGNO.get(asc_signo, "")
    posicion_regente = planetas.get(regente)

    if regente and posicion_regente:
        signo_regente = posicion_regente.get("signo", "")
        casa_regente = posicion_regente.get("casa", "")
        grado_regente = posicion_regente.get("grado", 0)

        texto_casa = REGENTE_ASC_CASA.get(casa_regente, "")

        if texto_casa:
            partes.append(texto_casa)

        texto_signo_regente = REGENTE_ASC_SIGNO.get(signo_regente, "")

        if texto_signo_regente:
            partes.append(texto_signo_regente)


    # ── Aspectos al Ascendente ───────────────────────────────────────
    aspectos_ascendente = aspectos_de_punto(
        aspectos,
        "Ascendente",
    )

    for aspecto in aspectos_ascendente:
        otro = otro_punto_del_aspecto(
            aspecto,
            "Ascendente",
        )

        clave1 = (
            aspecto["p1"],
            aspecto["p2"],
            aspecto["simbolo"],
        )

        clave2 = (
            aspecto["p2"],
            aspecto["p1"],
            aspecto["simbolo"],
        )

        # Textos específicos que ya existían.
        texto_aspecto = (
            ASPECTOS_SOL_ASC.get(clave1)
            or ASPECTOS_SOL_ASC.get(clave2)
            or ASPECTOS_NODO_NORTE_ASC.get(clave1)
            or ASPECTOS_NODO_NORTE_ASC.get(clave2)
        )

        # Los aspectos con planetas se incorporarán mediante
        # textos específicos, sin utilizar una plantilla repetitiva.
        if not texto_aspecto:
            texto_aspecto = ASPECTOS_ASC_PLANETAS.get(
                ("Ascendente", otro, aspecto["simbolo"]),
                "",
            )

        if texto_aspecto and texto_aspecto not in partes:
            partes.append(texto_aspecto)

    return "\n\n".join(partes)


def texto_nodos(carta, aspectos):
    """
    Interpreta el eje nodal dando prioridad al Nodo Norte como dirección
    de crecimiento y utilizando el Nodo Sur como patrón conocido.

    Los aspectos se organizan desde el Nodo Norte para evitar duplicar
    la misma información con el Nodo Sur, que siempre está en oposición.
    """

    planetas = carta["planetas"]

    nn = planetas.get("Nodo Norte", {})
    ns = planetas.get("Nodo Sur", {})

    nn_signo = nn.get("signo", "")
    nn_casa = nn.get("casa", 1)

    ns_signo = ns.get("signo", "")
    ns_casa = ns.get("casa", 1)

    partes = []

    partes.append(
        "<font color='#1E508C'><b>La dirección que necesita desarrollarse</b></font>"
    )

    # ── Nodo Norte por signo ─────────────────────────────────────────
    texto_nn_signo = NODO_NORTE_SIGNO.get(nn_signo, "")
    if texto_nn_signo:
        partes.append(texto_nn_signo)

    # ── Nodo Norte por casa ──────────────────────────────────────────
    texto_nn_casa = NODO_NORTE_CASA.get(nn_casa, "")
    if texto_nn_casa:
        partes.append(texto_nn_casa)

    partes.append(
        "<font color='#1E508C'><b>Los recursos conocidos y la zona de seguridad</b></font>"
    )

    # ── Nodo Sur por signo ───────────────────────────────────────────
    texto_ns_signo = NODO_SUR_SIGNO.get(ns_signo, "")
    if texto_ns_signo:
        partes.append(texto_ns_signo)

    # ── Nodo Sur por casa ────────────────────────────────────────────
    texto_ns_casa = NODO_SUR_CASA.get(ns_casa, "")
    if texto_ns_casa:
        partes.append(texto_ns_casa)


    # ── Aspectos del Nodo Norte ──────────────────────────────────────
    aspectos_nodo_norte = [
        aspecto
        for aspecto in aspectos_de_punto(aspectos, "Nodo Norte")
        if otro_punto_del_aspecto(aspecto, "Nodo Norte")
        in ("Sol", "Luna", "Ascendente")
    ]

    if aspectos_nodo_norte:
        partes.append(
            "<b>Cómo dialoga la dirección de crecimiento con el resto de tu arquitectura</b>"
        )

    for aspecto in aspectos_nodo_norte:
        otro = otro_punto_del_aspecto(
            aspecto,
            "Nodo Norte",
        )

        clave1 = (
            aspecto["p1"],
            aspecto["p2"],
            aspecto["simbolo"],
        )

        clave2 = (
            aspecto["p2"],
            aspecto["p1"],
            aspecto["simbolo"],
        )

        texto_aspecto = (
            ASPECTOS_SOL_NODOS.get(clave1)
            or ASPECTOS_SOL_NODOS.get(clave2)
            or ASPECTOS_NODO_NORTE_ASC.get(clave1)
            or ASPECTOS_NODO_NORTE_ASC.get(clave2)
        )

        if not texto_aspecto:
            texto_aspecto = ASPECTOS_NODO_NORTE_LUNA.get(
                (
                    "Nodo Norte",
                    otro,
                    aspecto["simbolo"],
                ),
                "",
            )

        if texto_aspecto and texto_aspecto not in partes:
            partes.append(texto_aspecto)

    # ── Aspectos del Nodo Sur ────────────────────────────────────────
    aspectos_nodo_sur = [
        aspecto
        for aspecto in aspectos_de_punto(aspectos, "Nodo Sur")
        if otro_punto_del_aspecto(aspecto, "Nodo Sur")
        in ("Sol", "Luna", "Ascendente")
    ]

    if aspectos_nodo_sur:
        partes.append(
            "<b>Cómo participa lo conocido en tu manera de vivir</b>"
        )

    for aspecto in aspectos_nodo_sur:
        otro = otro_punto_del_aspecto(
            aspecto,
            "Nodo Sur",
        )

        clave1 = (
            aspecto["p1"],
            aspecto["p2"],
            aspecto["simbolo"],
        )

        clave2 = (
            aspecto["p2"],
            aspecto["p1"],
            aspecto["simbolo"],
        )

        texto_aspecto = (
            ASPECTOS_SOL_NODOS.get(clave1)
            or ASPECTOS_SOL_NODOS.get(clave2)
            or ASPECTOS_NODO_SUR_ASC.get(clave1)
            or ASPECTOS_NODO_SUR_ASC.get(clave2)
        )

        if not texto_aspecto:
            texto_aspecto = ASPECTOS_NODO_SUR_LUNA.get(
                (
                    "Nodo Sur",
                    otro,
                    aspecto["simbolo"],
                ),
                "",
            )

        if texto_aspecto and texto_aspecto not in partes:
            partes.append(texto_aspecto)

    return "\n\n".join(partes)


def texto_grados_anareticos(carta):
    partes = []
    planetas = carta["planetas"]

    for nombre in ["Sol", "Nodo Norte", "Nodo Sur"]:
        p = planetas.get(nombre, {})
        grado = p.get("grado", 0)
        signo = p.get("signo", "")

        if es_anaretico(grado):
            partes.append(
                f"{nombre} está en grado anaretico de {signo}. "
                f"Esto puede intensificar la forma en que se expresa este punto. "
                f"No lo vuelve más difícil por sí mismo, pero sí indica que esa función puede vivirse con menos margen, "
                f"como si pidiera más consciencia, más precisión y más capacidad de sostener lo que activa."
            )

    for nombre, punto in [("Ascendente", carta["asc"]), ("Medio Cielo", carta["mc"])]:
        grado = punto.get("grado", 0)
        signo = punto.get("signo", "")

        if es_anaretico(grado):
            partes.append(
                f"El {nombre} está en grado anaretico de {signo}. "
                f"Esto señala una zona sensible de orientación: puede haber una sensación de cierre, culminación o exigencia especial "
                f"en la manera en que este eje se expresa."
            )

    return "\n\n".join(partes)

def texto_integracion(carta, aspectos):
    """
    Integra Sol, Ascendente y eje nodal en una lectura narrativa.

    El objetivo no es repetir las interpretaciones anteriores, sino explicar
    cómo colaboran la dirección solar, la forma espontánea de afrontar la vida
    y el recorrido de desarrollo señalado por los Nodos.
    """

    planetas = carta["planetas"]
    asc = carta.get("asc", {})

    sol = planetas.get("Sol", {})
    luna = planetas.get("Luna", {})
    nn = planetas.get("Nodo Norte", {})
    ns = planetas.get("Nodo Sur", {})

    sol_signo = sol.get("signo", "")
    sol_casa = sol.get("casa", "")

    asc_signo = asc.get("signo", "")

    nn_signo = nn.get("signo", "")
    nn_casa = nn.get("casa", "")

    ns_signo = ns.get("signo", "")
    ns_casa = ns.get("casa", "")

    elem_sol = ELEMENTO_SIGNO.get(sol_signo, "")
    elem_asc = ELEMENTO_SIGNO.get(asc_signo, "")
    elem_nn = ELEMENTO_SIGNO.get(nn_signo, "")

    def buscar_aspecto(punto1, punto2):
        return next(
            (
                aspecto
                for aspecto in aspectos
                if {
                    aspecto.get("p1"),
                    aspecto.get("p2"),
                } == {
                    punto1,
                    punto2,
                }
            ),
            None,
        )

    asp_sol_asc = buscar_aspecto("Sol", "Ascendente")
    asp_sol_nn = buscar_aspecto("Sol", "Nodo Norte")
    asp_nn_asc = buscar_aspecto("Nodo Norte", "Ascendente")
    asp_nn_luna = buscar_aspecto("Nodo Norte", "Luna")

    partes = []

    # ── Introducción integradora ──────────────────────────────────────

    partes.append(
        "El Sol, el Ascendente y el eje nodal no describen tres caminos "
        "independientes, sino tres dimensiones de una misma vida. El Sol en "
        f"{sol_signo}, Casa {sol_casa}, muestra la dirección que necesita "
        "desarrollarse para que tu energía encuentre sentido y continuidad. "
        f"El Ascendente en {asc_signo} describe la manera espontánea desde la "
        "que interpretas lo que ocurre y respondes a las situaciones nuevas. "
        f"El recorrido entre el Nodo Sur en {ns_signo}, Casa {ns_casa}, y el "
        f"Nodo Norte en {nn_signo}, Casa {nn_casa}, señala la diferencia entre "
        "los recursos que ya conoces y una forma de vivir que todavía necesita "
        "más atención, práctica y participación consciente."
    )

    # ── Integración Sol–Ascendente ────────────────────────────────────

    if elem_sol and elem_asc and elem_sol == elem_asc:
        texto_sol_asc = (
            f"El Sol en {sol_signo} y el Ascendente en {asc_signo} pertenecen "
            f"al elemento {elem_sol}, por lo que existe una continuidad natural "
            "entre tu manera inmediata de afrontar la vida y la dirección que "
            "necesitas desarrollar. Es probable que muchas decisiones surjan "
            "con una sensación clara de coherencia interna, porque la forma de "
            "responder y aquello hacia lo que quieres avanzar utilizan un "
            "lenguaje parecido. Esta afinidad no significa que todo esté "
            "integrado de antemano; también puede hacer que algunas reacciones "
            "se den por válidas únicamente porque resultan naturales, sin "
            "detenerte a comprobar si siguen respondiendo a la vida que quieres "
            "construir."
        )

    elif elem_sol and elem_asc and {
        elem_sol,
        elem_asc,
    } in (
        {"Fuego", "Aire"},
        {"Tierra", "Agua"},
    ):
        texto_sol_asc = (
            f"El Sol en {sol_signo} y el Ascendente en {asc_signo} pertenecen "
            "a elementos que pueden apoyarse mutuamente. Tu manera espontánea "
            "de responder no es idéntica a tu dirección solar, pero suele "
            "ofrecer recursos que facilitan el movimiento hacia ella. La "
            "integración aparece cuando utilizas esa complementariedad de forma "
            "consciente, permitiendo que la primera reacción abra el camino sin "
            "convertirse automáticamente en la única manera posible de actuar."
        )

    else:
        texto_sol_asc = (
            f"El Sol en {sol_signo} y el Ascendente en {asc_signo} pertenecen "
            "a elementos con necesidades diferentes. Esto puede hacer que tu "
            "primera forma de reaccionar no coincida siempre con la dirección "
            "que termina aportando mayor sentido a tu vida. Una parte puede "
            "necesitar rapidez mientras otra pide tiempo, o buscar claridad "
            "mental cuando la dirección profunda requiere atender el cuerpo, "
            "la emoción o la experiencia concreta. La integración no exige "
            "escoger una de las dos, sino aprender a reconocer qué función "
            "cumple cada una y permitir que la respuesta inicial pueda "
            "reorganizarse cuando la situación necesita algo diferente."
        )

    if asp_sol_asc:
        simbolo = asp_sol_asc.get("simbolo", "")
        tipo = asp_sol_asc.get("tipo", "").lower()
        orbe = asp_sol_asc.get("orbe", "")

        if simbolo in ("□", "☍", "⚻"):
            texto_sol_asc += (
                f" La {tipo} entre el Sol y el Ascendente, con un orbe de "
                f"{orbe}°, refuerza este trabajo de ajuste. La tensión no señala "
                "que una parte sea correcta y la otra equivocada, sino que la "
                "coherencia necesita construirse mediante decisiones que tengan "
                "en cuenta tanto tu forma habitual de responder como aquello "
                "que deseas sostener a largo plazo."
            )
        else:
            texto_sol_asc += (
                f" La {tipo} entre el Sol y el Ascendente, con un orbe de "
                f"{orbe}°, ofrece una vía de colaboración especialmente "
                "disponible. Esta facilidad se convierte en un recurso real "
                "cuando no se queda únicamente en una sensación interna de "
                "coherencia, sino que se traduce en decisiones, límites y "
                "acciones concretas."
            )

    partes.append(texto_sol_asc)

    # ── Integración Sol–Nodo Norte ────────────────────────────────────

    if sol_signo == nn_signo:
        texto_sol_nodo = (
            f"El Sol y el Nodo Norte se encuentran en {nn_signo}, de modo que "
            "la dirección que alimenta tu vitalidad y la cualidad que necesitas "
            "desarrollar comparten una base común. Esto puede ayudarte a "
            "reconocer con mayor claridad qué experiencias merecen tu energía, "
            "aunque también puede hacer que confundas afinidad con desarrollo "
            "ya realizado. Que una dirección resulte natural no significa que "
            "esté plenamente construida; necesita tiempo, elección y una forma "
            "concreta de sostenerse en la vida cotidiana."
        )

    elif sol_signo == ns_signo:
        texto_sol_nodo = (
            f"El Sol se encuentra en {sol_signo}, el mismo signo que el Nodo "
            "Sur, por lo que una parte importante de tu vitalidad se apoya en "
            "capacidades y formas de funcionar que ya conoces bien. Estos "
            "recursos no necesitan ser rechazados, porque forman parte de tu "
            "estructura y pueden ofrecer seguridad, experiencia y competencia. "
            f"Sin embargo, el Nodo Norte en {nn_signo}, Casa {nn_casa}, pide "
            "que no organices toda tu vida alrededor de lo que ya dominas. El "
            "crecimiento aparece cuando utilizas lo conocido como base desde la "
            "que avanzar, en lugar de convertirlo en el único lugar posible "
            "desde el que vivir."
        )

    elif elem_sol and elem_nn and elem_sol == elem_nn:
        texto_sol_nodo = (
            f"El Sol en {sol_signo} y el Nodo Norte en {nn_signo} pertenecen "
            f"al elemento {elem_sol}. La dirección solar y el recorrido de "
            "crecimiento comparten una forma parecida de movilizar la energía, "
            "lo que puede facilitar que algunas decisiones importantes se "
            "sientan internamente coherentes. Aun así, el Nodo Norte representa "
            "una capacidad que necesita desarrollarse conscientemente, por lo "
            "que no basta con reconocerla o comprenderla: necesita encontrar "
            "una forma estable de participar en tus elecciones."
        )

    elif elem_sol and elem_nn and {
        elem_sol,
        elem_nn,
    } in (
        {"Fuego", "Aire"},
        {"Tierra", "Agua"},
    ):
        texto_sol_nodo = (
            f"El Sol en {sol_signo} y el Nodo Norte en {nn_signo} pertenecen "
            "a elementos compatibles. Aquello que aporta vitalidad puede "
            "convertirse en un apoyo para desarrollar la dirección nodal, "
            "aunque esa colaboración necesita ser activada mediante decisiones "
            "concretas. La posibilidad está disponible, pero el crecimiento no "
            "se produce únicamente porque ambas partes puedan entenderse; toma "
            "forma cuando eliges sostener experiencias que amplían tu manera "
            "habitual de vivir."
        )

    else:
        texto_sol_nodo = (
            f"El Sol en {sol_signo} y el Nodo Norte en {nn_signo} funcionan "
            "desde lógicas diferentes. Es posible que aquello que te da energía "
            "y confianza no coincida inmediatamente con la dirección que más "
            "crecimiento te pide. Esto puede generar etapas en las que avanzar "
            "hacia lo nuevo se sienta menos natural que permanecer en una forma "
            "de vida conocida. La integración consiste en no obligar al Sol a "
            "desaparecer para seguir el camino nodal, sino en permitir que tu "
            "dirección vital vaya ampliándose hasta ser capaz de incluir una "
            "forma nueva de actuar, relacionarte y tomar decisiones."
        )

    if asp_sol_nn:
        simbolo = asp_sol_nn.get("simbolo", "")
        tipo = asp_sol_nn.get("tipo", "").lower()
        orbe = asp_sol_nn.get("orbe", "")

        if simbolo in ("□", "☍", "⚻"):
            texto_sol_nodo += (
                f" La {tipo} entre el Sol y el Nodo Norte, con un orbe de "
                f"{orbe}°, hace especialmente visible esta diferencia de "
                "ritmos. El desarrollo puede requerir reajustes repetidos y "
                "decisiones que al principio no se sienten completamente "
                "naturales, pero esa incomodidad no indica necesariamente una "
                "dirección equivocada; muchas veces señala que una forma nueva "
                "de organizar tu vida todavía está intentando consolidarse."
            )
        else:
            texto_sol_nodo += (
                f" La {tipo} entre el Sol y el Nodo Norte, con un orbe de "
                f"{orbe}°, facilita la comunicación entre ambas direcciones. "
                "Existe una posibilidad real de avanzar con coherencia, siempre "
                "que esa fluidez no se quede únicamente en comprensión o buena "
                "disposición y termine convirtiéndose en una participación "
                "concreta en tu propia vida."
            )

    partes.append(texto_sol_nodo)

    # ── Integración Ascendente–Nodo Norte ─────────────────────────────

    if elem_asc and elem_nn and elem_asc == elem_nn:
        texto_asc_nodo = (
            f"El Ascendente en {asc_signo} y el Nodo Norte en {nn_signo} "
            f"pertenecen al elemento {elem_asc}. Tu manera espontánea de "
            "afrontar la realidad puede ofrecer recursos útiles para avanzar "
            "hacia la dirección de crecimiento. Sin embargo, compartir elemento "
            "no convierte ambos puntos en equivalentes. El Ascendente describe "
            "una respuesta ya disponible, mientras que el Nodo Norte señala una "
            "cualidad que necesita mayor desarrollo; por eso resulta importante "
            "distinguir cuándo estás creciendo realmente y cuándo simplemente "
            "repites una forma conocida de actuar que se le parece."
        )

    elif elem_asc and elem_nn and {
        elem_asc,
        elem_nn,
    } in (
        {"Fuego", "Aire"},
        {"Tierra", "Agua"},
    ):
        texto_asc_nodo = (
            f"El Ascendente en {asc_signo} y el Nodo Norte en {nn_signo} "
            "pertenecen a elementos compatibles. Tu manera habitual de responder "
            "puede abrir oportunidades para desarrollar la dirección nodal, "
            "especialmente cuando utilizas conscientemente los recursos que ya "
            "posees. El crecimiento aparece al permitir que la respuesta "
            "espontánea sea un punto de partida, pero no una conclusión cerrada "
            "sobre quién eres ni sobre cómo debes actuar siempre."
        )

    else:
        texto_asc_nodo = (
            f"El Ascendente en {asc_signo} y el Nodo Norte en {nn_signo} "
            "responden a necesidades diferentes. La primera reacción puede "
            "llevarte hacia una forma conocida de protegerte, organizarte o "
            "resolver lo que ocurre, mientras el Nodo Norte propone una respuesta "
            "menos automática. Esto no invalida tu Ascendente, porque sigue "
            "siendo una herramienta fundamental para relacionarte con la vida. "
            "El proceso consiste en ampliar su repertorio para que no tenga que "
            "resolver todas las situaciones del mismo modo y pueda acompañar una "
            "dirección que todavía está desarrollándose."
        )

    if asp_nn_asc:
        simbolo = asp_nn_asc.get("simbolo", "")
        tipo = asp_nn_asc.get("tipo", "").lower()
        orbe = asp_nn_asc.get("orbe", "")

        if simbolo in ("□", "☍", "⚻"):
            texto_asc_nodo += (
                f" La {tipo} entre el Nodo Norte y el Ascendente, con un orbe "
                f"de {orbe}°, intensifica la necesidad de revisar respuestas "
                "automáticas. Algunas formas de actuar que antes ofrecían "
                "seguridad pueden necesitar modificaciones para seguir siendo "
                "útiles en la etapa actual."
            )
        else:
            texto_asc_nodo += (
                f" La {tipo} entre el Nodo Norte y el Ascendente, con un orbe "
                f"de {orbe}°, facilita que tu forma de posicionarte abra caminos "
                "de crecimiento. La colaboración existe, aunque necesita ser "
                "utilizada deliberadamente para no permanecer únicamente como "
                "una capacidad potencial."
            )

    partes.append(texto_asc_nodo)

    # ── Relación opcional Luna–Nodo Norte ─────────────────────────────

    if asp_nn_luna:
        simbolo = asp_nn_luna.get("simbolo", "")
        tipo = asp_nn_luna.get("tipo", "").lower()
        orbe = asp_nn_luna.get("orbe", "")

        if simbolo in ("□", "☍", "⚻"):
            partes.append(
                f"La {tipo} entre la Luna y el Nodo Norte, con un orbe de "
                f"{orbe}°, muestra que el recorrido de crecimiento no siempre "
                "coincide con aquello que emocionalmente resulta familiar o "
                "seguro. Algunas decisiones pueden ser necesarias para avanzar "
                "y, al mismo tiempo, remover necesidades profundas de protección, "
                "pertenencia o estabilidad. La cuestión no es ignorar esas "
                "necesidades, sino construir condiciones internas que permitan "
                "atravesar lo nuevo sin abandonarte emocionalmente durante el "
                "proceso."
            )
        else:
            partes.append(
                f"La {tipo} entre la Luna y el Nodo Norte, con un orbe de "
                f"{orbe}°, ofrece una colaboración entre tus necesidades "
                "emocionales y la dirección de crecimiento. Esta relación puede "
                "ayudarte a reconocer qué experiencias, vínculos o condiciones "
                "internas sostienen mejor el proceso, siempre que el cuidado no "
                "se convierta en una razón para permanecer únicamente dentro de "
                "lo conocido."
            )

    # ── Cierre narrativo ──────────────────────────────────────────────

    partes.append(
        "Integrar esta arquitectura no significa conseguir que todas las partes "
        "de ti quieran siempre lo mismo ni eliminar cualquier contradicción. "
        "Significa comprender que cada una cumple una función distinta y que la "
        "coherencia se construye cuando ninguna necesita imponerse sobre las "
        "demás. El Sol aporta una dirección capaz de organizar tu energía; el "
        "Ascendente ofrece una forma inmediata de relacionarte con la realidad; "
        "el Nodo Sur conserva recursos que forman parte de tu historia, y el "
        "Nodo Norte introduce cualidades que necesitan más espacio para crecer. "
        "La transformación comienza cuando esta comprensión deja de ser una idea "
        "y empieza a participar en la manera en la que eliges, estableces límites, "
        "sostienes procesos y respondes a lo que la vida va poniendo delante. No "
        "se trata de convertirte en otra persona, sino de construir una vida "
        "capaz de sostener de una forma cada vez más consciente todo aquello que "
        "ya forma parte de ti."
    )

    return "\n\n".join(partes)


def texto_orientacion(carta, aspectos):
    planetas = carta["planetas"]
    asc = carta.get("asc", {})

    asc_signo = asc.get("signo", "")
    sol = planetas.get("Sol", {})
    nn = planetas.get("Nodo Norte", {})
    ns = planetas.get("Nodo Sur", {})

    sol_signo = sol.get("signo", "")
    sol_casa = sol.get("casa", 1)

    nn_signo = nn.get("signo", "")
    nn_casa = nn.get("casa", 1)

    ns_signo = ns.get("signo", "")
    ns_casa = ns.get("casa", 1)

    elem_asc = ELEMENTO_SIGNO.get(asc_signo, "")
    elem_sol = ELEMENTO_SIGNO.get(sol_signo, "")

    def buscar_aspecto(p1, p2):
        return next(
            (
                aspecto
                for aspecto in aspectos
                if {aspecto.get("p1"), aspecto.get("p2")} == {p1, p2}
            ),
            None,
        )

    asp_sol_asc = buscar_aspecto("Sol", "Ascendente")
    asp_sol_nn = buscar_aspecto("Sol", "Nodo Norte")
    asp_nn_asc = buscar_aspecto("Nodo Norte", "Ascendente")
    asp_nn_luna = buscar_aspecto("Nodo Norte", "Luna")

    inicio_map = {
        "Fuego": (
            f"Con el Ascendente en {asc_signo}, suele ayudarte comenzar por una acción concreta "
            "que te permita comprobar qué ocurre al moverte. No necesitas resolver toda la situación "
            "antes de actuar, pero sí distinguir entre una decisión consciente y una respuesta nacida "
            "únicamente de la urgencia. Elige un paso pequeño, realizable y suficientemente claro como "
            "para que la experiencia pueda ofrecerte nueva información."
        ),
        "Tierra": (
            f"Con el Ascendente en {asc_signo}, conviene comenzar ordenando lo inmediato y eligiendo "
            "un paso concreto que puedas sostener. Revisar los recursos disponibles, reducir el problema "
            "a una medida manejable y establecer una prioridad suele darte más claridad que intentar "
            "resolverlo todo de una vez."
        ),
        "Aire": (
            f"Con el Ascendente en {asc_signo}, poner en palabras lo que ocurre puede ayudarte a salir "
            "de una percepción demasiado difusa o cerrada. Escribir, hablar con alguien capaz de escuchar "
            "sin decidir por ti o formular con precisión la pregunta que intentas responder puede ordenar "
            "la experiencia. Después será importante traducir esa comprensión en una decisión concreta "
            "para que el pensamiento no se convierta en una forma de permanecer a distancia."
        ),
        "Agua": (
            f"Con el Ascendente en {asc_signo}, antes de actuar necesitas registrar de qué manera te está "
            "afectando la situación. Dar nombre a la emoción, reconocer qué necesidad está implicada y "
            "diferenciar lo propio de lo que pertenece al entorno puede evitar respuestas nacidas del "
            "desbordamiento. Una vez recuperado cierto contacto interno, resultará más sencillo elegir "
            "una respuesta que también tenga en cuenta la realidad."
        ),
    }

    desde_donde = inicio_map.get(
        elem_asc,
        (
            f"Con el Ascendente en {asc_signo}, empieza observando qué respuesta aparece de forma "
            "automática y pregúntate si sigue siendo adecuada para la situación actual. No se trata "
            "de corregirte, sino de disponer de un pequeño margen antes de actuar."
        ),
    )

    if asp_sol_asc:
        desde_donde += (
            f" El Sol forma {asp_sol_asc['tipo'].lower()} con el Ascendente, con un orbe de "
            f"{asp_sol_asc['orbe']}°. Por eso conviene observar especialmente si tu primera "
            "reacción acompaña la dirección que deseas construir o si necesita algún ajuste."
        )

    sostener_map = {
        "Fuego": (
            f"El Sol en {sol_signo}, Casa {sol_casa}, necesita una dirección activa y visible. "
            "Te beneficia sostener un proyecto, decisión o responsabilidad en la que puedas movilizar "
            "energía de una forma concreta, evitando empezar continuamente caminos nuevos sin darles "
            "tiempo para adquirir estructura. Antes de ampliar, comprueba qué merece realmente continuidad."
        ),
        "Tierra": (
            f"El Sol en {sol_signo}, Casa {sol_casa}, necesita construir algo concreto y estable. "
            "Te ayuda definir ritmos sostenibles, reconocer los avances aunque sean graduales y mantener "
            "contacto con los recursos reales de los que dispones. La continuidad será más importante "
            "que la intensidad inicial."
        ),
        "Aire": (
            f"El Sol en {sol_signo}, Casa {sol_casa}, necesita intercambio, comprensión y movimiento "
            "mental, pero también un eje que organice toda esa apertura. Elige qué conversación, aprendizaje "
            "o idea merece convertirse en una línea de trabajo sostenida y evita que la variedad impida "
            "profundizar en aquello que ya ha demostrado tener sentido."
        ),
        "Agua": (
            f"El Sol en {sol_signo}, Casa {sol_casa}, necesita una dirección conectada con lo que sientes "
            "y con aquello que tiene significado interno. Te beneficia reservar espacio para elaborar la "
            "experiencia, pero también dar una forma concreta a lo que descubres para que la sensibilidad "
            "no permanezca únicamente dentro de ti."
        ),
    }

    sostener = sostener_map.get(
        elem_sol,
        (
            f"El Sol en {sol_signo}, Casa {sol_casa}, muestra una dirección que necesita continuidad. "
            "Escoge una forma concreta de sostenerla durante el tiempo suficiente como para comprobar "
            "qué puede llegar a construir."
        ),
    )

    evitar = (
        f"El Nodo Sur en {ns_signo}, Casa {ns_casa}, contiene recursos que conoces bien y que pueden "
        "seguir siendo valiosos. Obsérvalos especialmente cuando aparecen cansancio, inseguridad o presión, "
        "porque en esos momentos es más fácil convertir una capacidad conocida en la única respuesta disponible. "
        f"El Nodo Norte en {nn_signo}, Casa {nn_casa}, no te pide rechazar lo anterior, sino ampliar tu manera "
        "de vivir incorporando una cualidad menos automática. Pregúntate qué decisión pequeña podría acercarte "
        "a esa dirección sin obligarte a transformar toda tu vida de una sola vez."
    )

    tensiones = [
        aspecto
        for aspecto in (asp_sol_nn, asp_nn_asc, asp_nn_luna)
        if aspecto and aspecto.get("simbolo") in ("□", "☍", "⚻")
    ]

    if tensiones:
        aspecto = tensiones[0]
        evitar += (
            f" La {aspecto['tipo'].lower()} entre {aspecto['p1']} y {aspecto['p2']}, con un orbe "
            f"de {aspecto['orbe']}°, indica que este movimiento puede requerir reajustes y generar "
            "incomodidad. No necesitas interpretar esa tensión como una señal de fracaso; puede ser "
            "la forma en la que una estructura nueva empieza a encontrar lugar dentro de tu vida."
        )

    return {
        "desde_donde": desde_donde,
        "sostener": sostener,
        "evitar": evitar,
    }

# ─── RUEDA SIMPLIFICADA: SOL + ASC + NODOS ───────────────────────────────────

def dibujar_rueda_sol_asc_nodos(carta, aspectos, archivo_salida):
    """Rueda focal: Sol, Ascendente, Nodos y todos los planetas aspectados por el Sol."""
    planetas = carta["planetas"]
    cuspides = carta["cuspides"]
    asc_lon  = carta["asc"]["lon"]

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

    for i, signo in enumerate(SIGNOS):
        elem = ELEMENTO_SIGNO[signo]
        color = COLORES_ELEMENTO[elem]
        ang_ini = lon_a_angulo(i * 30)
        ang_fin = lon_a_angulo((i + 1) * 30)
        theta = np.linspace(ang_ini, ang_fin, 50)

        xs = [math.cos(a) * R_EXT for a in theta] + [math.cos(a) * R_SIGN_IN for a in reversed(theta)]
        ys = [math.sin(a) * R_EXT for a in theta] + [math.sin(a) * R_SIGN_IN for a in reversed(theta)]

        ax.fill(xs, ys, color=color, alpha=0.20, zorder=1)

    for r, lw, c in [
        (R_EXT, 2, "#333"),
        (R_SIGN_IN, 1.5, "#333"),
        (R_CASA_IN, 1.5, "#555"),
        (0.25, 1, "#888"),
    ]:
        ax.add_patch(plt.Circle((0, 0), r, fill=False, color=c, linewidth=lw, zorder=2))

    for i in range(12):
        ang = lon_a_angulo(i * 30)
        ax.plot(
            [math.cos(ang) * R_SIGN_IN, math.cos(ang) * R_EXT],
            [math.sin(ang) * R_SIGN_IN, math.sin(ang) * R_EXT],
            color="#666",
            linewidth=0.7,
            zorder=2,
        )

    for i, (signo, simbolo) in enumerate(zip(SIGNOS, SIMBOLOS_SIGNOS)):
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

    for i, cusp in enumerate(cuspides):
        ang = lon_a_angulo(cusp)
        lw = 1.8 if i in (0, 3, 6, 9) else 0.5
        col = "#111" if i in (0, 3, 6, 9) else "#999"

        ax.plot(
            [math.cos(ang) * R_CASA_IN, math.cos(ang) * R_CASA_OUT],
            [math.sin(ang) * R_CASA_IN, math.sin(ang) * R_CASA_OUT],
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

    puntos_aspecto = {nombre: objeto for nombre, objeto in planetas.items() if objeto}
    puntos_aspecto["Ascendente"] = {"lon": carta["asc"]["lon"]}

    # Dibuja exactamente los aspectos calculados, evitando que la rueda y el texto
    # utilicen lógicas diferentes.
    for aspecto in aspectos:
        p1 = aspecto["p1"]
        p2 = aspecto["p2"]
        obj1 = puntos_aspecto.get(p1)
        obj2 = puntos_aspecto.get(p2)
        simbolo = aspecto.get("simbolo")

        if not obj1 or not obj2 or simbolo not in _ASP_COL:
            continue

        a1 = lon_a_angulo(obj1["lon"])
        a2 = lon_a_angulo(obj2["lon"])
        con_nodo_sur = "Nodo Sur" in (p1, p2)

        ax.plot(
            [math.cos(a1) * R_ASP, math.cos(a2) * R_ASP],
            [math.sin(a1) * R_ASP, math.sin(a2) * R_ASP],
            color=_ASP_COL[simbolo],
            linewidth=_ASP_LW[simbolo],
            alpha=0.45 if con_nodo_sur else 0.64,
            linestyle="dashed" if con_nodo_sur else "solid",
            zorder=2,
        )

    nombres_visibles = {
        "Sol",
        "Nodo Norte",
        "Nodo Sur",
    }

    for aspecto in aspectos:
        for nombre in (aspecto["p1"], aspecto["p2"]):

            # El Ascendente ya está representado por el eje AC–DC,
            # así que no dibujamos un símbolo interior.
            if nombre == "Ascendente":
                continue

            if nombre in planetas:
                nombres_visibles.add(nombre)

    puntos = {}

    for nombre in nombres_visibles:
        if nombre in planetas:
            puntos[nombre] = planetas[nombre]

    lones_usados = []
    radios = {}

    for nombre, p in puntos.items():
        if not p:
            continue

        lon = p["lon"]
        radio = R_PLANETA

        for lp, rp in lones_usados:
            d = abs(lon - lp) % 360
            if d > 180:
                d = 360 - d

            if d < 8:
                radio = rp - 0.10 if rp - 0.10 > 0.45 else rp + 0.10
                break

        lones_usados.append((lon, radio))
        radios[nombre] = radio

    for nombre, p in puntos.items():
        if not p:
            continue

        ang = lon_a_angulo(p["lon"])
        r = radios[nombre]
        color = COLORES_PLANETA.get(nombre, "#333")
        simbolo = p["simbolo"]
        fs = 22 if nombre == "Sol" else 16 if nombre == "Ascendente" else 18 if nombre in ("Nodo Norte", "Nodo Sur") else 15

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
            [math.cos(ang) * (r + 0.07), math.cos(ang) * (R_SIGN_IN + 0.01)],
            [math.sin(ang) * (r + 0.07), math.sin(ang) * (R_SIGN_IN + 0.01)],
            color=color,
            linewidth=0.9,
            alpha=0.70,
            zorder=3,
        )

    for etq, lon_pt, bold, size in [
        ("AC", carta["asc"]["lon"], True, 13),
        ("DC", (carta["asc"]["lon"] + 180) % 360, False, 10),
        ("MC", carta["mc"]["lon"], False, 10),
        ("IC", (carta["mc"]["lon"] + 180) % 360, False, 10),
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


def crear_estilos_reportlab():
    """Usa los estilos comunes de la colección cuando estilos_pdf.py está disponible."""
    if crear_estilos_pdf is not None:
        return crear_estilos_pdf()

    # Respaldo para poder ejecutar el archivo de forma independiente.
    estilos = getSampleStyleSheet()
    titulo = ParagraphStyle(
        "TituloAI", parent=estilos["Title"], fontName="Times-Bold",
        fontSize=28, leading=34, alignment=TA_CENTER,
        textColor=colors.HexColor("#1E508C"), spaceAfter=20,
    )
    estilo_frase_final = ParagraphStyle(
        "FraseFinal", parent=estilos["BodyText"], fontName="Times-Italic",
        fontSize=10, leading=14, textColor=colors.HexColor("#666666"),
        alignment=TA_CENTER,
    )
    subtitulo = ParagraphStyle(
        "SubtituloAI", parent=estilos["Heading2"], fontName="Times-Bold",
        fontSize=18, leading=23, textColor=colors.HexColor("#8C5A00"),
        spaceBefore=18, spaceAfter=10, keepWithNext=True,
    )
    subtitulo2 = ParagraphStyle(
        "Subtitulo2AI", parent=estilos["Heading3"], fontName="Times-Bold",
        fontSize=14, leading=18, textColor=colors.HexColor("#1E508C"),
        spaceBefore=12, spaceAfter=6, keepWithNext=True,
    )
    cuerpo = ParagraphStyle(
        "CuerpoAI", parent=estilos["BodyText"], fontName="Times-Roman",
        fontSize=11, leading=16, spaceAfter=10, alignment=TA_JUSTIFY,
    )
    centro = ParagraphStyle("CentroAI", parent=cuerpo, alignment=TA_CENTER)
    titulo_aspecto = ParagraphStyle(
        "TituloAspectoAI", parent=cuerpo, fontName="Times-Bold",
        textColor=colors.HexColor("#333333"), spaceBefore=8,
        spaceAfter=4, keepWithNext=True,
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
        canvas.drawRightString(19 * cm, 1.2 * cm, str(numero))
    canvas.restoreState()


def _parrafos_reportlab(texto, estilo):
    return [Paragraph(p.strip(), estilo) for p in texto.split("\n\n") if p.strip()]


def bloque_portada_sol(nombre, fecha_str, hora_str, ciudad, estilos):
    return [
        Spacer(1, 1.7 * cm),
        Paragraph("Sol · Ascendente · Nodos", estilos["titulo"]),
        Paragraph("Arquitectura Interna", estilos["centro"]),
        Spacer(1, 0.45 * cm),
        Paragraph(
            "Una lectura sobre dirección vital, forma de relacionarte con la vida y camino de desarrollo.",
            estilos["estilo_frase_final"],
        ),
        Spacer(1, 2.2 * cm),
        Paragraph(
            nombre,
            ParagraphStyle(
                "NombrePortada", parent=estilos["centro"], fontName="Times-Roman",
                fontSize=24, leading=29, textColor=colors.HexColor("#8C5A00"),
            ),
        ),
        Spacer(1, 1.15 * cm),
        Paragraph(f"{fecha_str} · {hora_str}", estilos["centro"]),
        Paragraph(ciudad, estilos["centro"]),
        Spacer(1, 10 * cm),
        Paragraph(
            "Arquitectura Interna · Un método para sostener cuerpo, energía y vida con coherencia",
            estilos["estilo_frase_final"],
        ),
        PageBreak(),
    ]


def bloque_bienvenida_sol(estilos):
    texto = (
        "Toda vida necesita una dirección. No un destino fijo ni una respuesta cerrada, "
        "sino una orientación interna que permita reconocer qué merece tu energía "
        "y qué camino resulta verdaderamente coherente contigo.\n\n"

        "En este informe, el Sol representa la dirección que necesita desarrollarse "
        "para sentir vitalidad. El Ascendente muestra la forma espontánea en la que "
        "interpretas lo que ocurre y respondes ante situaciones nuevas. Los Nodos describen el recorrido entre aquello que ya conoces "
        "y lo que necesitas aprender.\n\n"

        "Este cuaderno no pretende decirte quién eres. Pretende ayudarte a observar "
        "cómo se organiza tu dirección vital y qué partes de ti necesitan colaborar "
        "para construir una vida más coherente."
    )

    elementos = [
        Paragraph("Bienvenida", estilos["subtitulo"])
    ]

    elementos += _parrafos_reportlab(
        texto,
        estilos["cuerpo"]
    )

    elementos.append(
        Paragraph(
            "Antes de empezar",
            estilos["subtitulo"]
        )
    )

    elementos.append(
        Paragraph(
            "Cómo leer este cuaderno",
            estilos["subtitulo2"]
        )
    )

    elementos += _parrafos_reportlab(
        "No necesitas que todo encaje desde la primera página. Léelo despacio, "
        "subraya aquello que te haga pensar y vuelve a él cuando la experiencia "
        "te permita comprenderlo desde otro lugar.",
        estilos["cuerpo"],
    )

    return elementos


def bloque_rueda_sol(ruta_rueda, estilos):
    return [
        Spacer(1, 0.6 * cm),
        Image(ruta_rueda, width=12 * cm, height=12 * cm),
        PageBreak(),
    ]


def bloque_resumen_sol(carta, estilos):
    planetas = carta["planetas"]
    sol = planetas.get("Sol", {})
    nn = planetas.get("Nodo Norte", {})
    ns = planetas.get("Nodo Sur", {})
    asc = carta["asc"]
    regente_asc = REGENTE_SIGNO.get(asc.get("signo", ""), "")

    tabla_datos = [
        ["Capa", "Signo", "Casa / Regente", "Función"],
        ["Sol", sol.get("signo", ""), f"Casa {sol.get('casa', '')}", "Dirección, identidad y vitalidad"],
        ["Ascendente", asc.get("signo", ""), regente_asc, "Forma de relacionarte con la vida"],
        ["Nodo Norte", nn.get("signo", ""), f"Casa {nn.get('casa', '')}", "Dirección de crecimiento"],
        ["Nodo Sur", ns.get("signo", ""), f"Casa {ns.get('casa', '')}", "Patrón conocido y recursos adquiridos"],
    ]
    tabla = Table(tabla_datos, colWidths=[2.3*cm, 2.5*cm, 3.0*cm, 5.2*cm])
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
    return [Paragraph("La arquitectura de tu dirección vital", estilos["subtitulo"]), Spacer(1, 0.9*cm), tabla]


def bloque_referencias_tecnicas(carta, aspectos, estilos):
    """Añade aspectos, grados sensibles e interceptaciones sin recargar la tabla principal."""
    elementos = [Spacer(1, 0.95 * cm)]

    elementos.append(Paragraph("Aspectos principales", estilos["subtitulo2"]))

    elementos.append(Spacer(1, 0.45 * cm))

    angulo_aspecto = {
        "=": "0°",
        "✶": "60°",
        "□": "90°",
        "△": "120°",
        "⚻": "150°",
        "☍": "180°",
    }

    if aspectos:
        datos = [["Punto", "Aspecto", "Punto", "Tipo", "Orbe"]]
        for aspecto in aspectos:
            datos.append([
                aspecto["p1"],
                angulo_aspecto.get(aspecto["simbolo"], ""),
                aspecto["p2"],
                aspecto["tipo"],
                f'{aspecto["orbe"]:.1f}°',
            ])

        tabla = Table(
            datos,
            colWidths=[3.0 * cm, 1.4 * cm, 3.0 * cm, 3.0 * cm, 1.5 * cm],
            repeatRows=1,
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
            ("ALIGN", (1, 0), (1, -1), "CENTER"),
            ("ALIGN", (4, 0), (4, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        elementos.append(tabla)

    else:
        elementos.append(Paragraph(
            "No aparecen aspectos directos del Sol ni aspectos estructurales entre el Ascendente y los Nodos dentro de los orbes definidos. "
            "Esto no significa que estos puntos no se relacionen, sino que la interpretación se apoya principalmente "
            "en sus signos, casas, elementos y dinámica general.",
            estilos["cuerpo"],
        ))

    elementos.append(Spacer(1, 0.7 * cm))

    texto_grados = texto_grados_anareticos(carta)
    if texto_grados.strip():
        elementos.append(Paragraph("Grados sensibles", estilos["subtitulo2"]))
        elementos.extend(_parrafos_reportlab(texto_grados, estilos["cuerpo"]))

    texto_inter = texto_interceptaciones(carta)
    if texto_inter.strip():
        elementos.append(Paragraph("Signos interceptados", estilos["subtitulo2"]))
        elementos.extend(_parrafos_reportlab(texto_inter, estilos["cuerpo"]))

    return elementos


def bloque_texto(titulo, texto, estilos, subtitulo_interno=None):
    elementos = [Spacer(1, 0.35*cm), Paragraph(titulo, estilos["subtitulo"])]
    if subtitulo_interno:
        elementos.append(Paragraph(subtitulo_interno, estilos["subtitulo2"]))
    elementos += _parrafos_reportlab(texto, estilos["cuerpo"])
    return elementos


def generar_pdf_sol_asc_nodos(
    ruta_pdf, carta, nombre, anio, mes, dia, hora, minuto,
    ciudad, lat, lon, tz_name, aspectos, ruta_rueda
):
    estilos = crear_estilos_reportlab()
    planetas = carta["planetas"]
    asc = carta["asc"]
    sol = planetas.get("Sol", {})
    nn = planetas.get("Nodo Norte", {})
    ns = planetas.get("Nodo Sur", {})
    regente_asc = REGENTE_SIGNO.get(asc.get("signo", ""), "")

    t_sol = texto_sol(carta, aspectos)
    t_interceptaciones = texto_interceptaciones(carta)
    t_asc = texto_ascendente(carta, aspectos)
    t_nodos = texto_nodos(carta, aspectos)
    t_integ = texto_integracion(carta, aspectos)
    t_or = texto_orientacion(carta, aspectos)

    doc = SimpleDocTemplate(
        ruta_pdf, pagesize=A4, rightMargin=2.5*cm, leftMargin=2.5*cm,
        topMargin=2.5*cm, bottomMargin=2.5*cm,
    )
    contenido = []
    fecha_str = f"{dia:02d}/{mes:02d}/{anio}"
    hora_str = f"{hora:02d}:{minuto:02d}"

    contenido += bloque_portada_sol(nombre, fecha_str, hora_str, ciudad, estilos)
    contenido += bloque_bienvenida_sol(estilos)
    contenido += bloque_rueda_sol(ruta_rueda, estilos)
    contenido += bloque_resumen_sol(carta, estilos)
    contenido += bloque_referencias_tecnicas(carta, aspectos, estilos)

    contenido += bloque_texto(
        "El Sol · Tu dirección principal",
        t_sol,
        estilos,
        f"Sol en {sol.get('signo','')} · Casa {sol.get('casa','')}",
    )
    contenido += bloque_texto(
        "El Ascendente · Cómo te relacionas con la vida", t_asc, estilos,
        f"Ascendente en {asc.get('signo','')} · Regente: {regente_asc}",
    )
    contenido += bloque_texto(
        "Los Nodos · Entre lo conocido y lo que necesita crecer", t_nodos, estilos,
        f"Nodo Norte en {nn.get('signo','')} · Casa {nn.get('casa','')} · Nodo Sur en {ns.get('signo','')} · Casa {ns.get('casa','')}",
    )
    contenido += bloque_texto("Cuando todas las piezas empiezan a unirse", t_integ, estilos)

    contenido.append(Spacer(1, 0.35*cm))
    contenido.append(Paragraph("Una orientación práctica", estilos["subtitulo"]))
    for titulo, clave in [
        ("Desde dónde empezar", "desde_donde"),
        ("Qué conviene sostener", "sostener"),
        ("Qué conviene observar", "evitar"),
    ]:
        contenido.append(Paragraph(titulo, estilos["subtitulo2"]))
        contenido += _parrafos_reportlab(t_or[clave], estilos["cuerpo"])

    contenido.append(Spacer(1, 0.15*cm))
    contenido.append(KeepTogether([
        Paragraph("Cierre", estilos["subtitulo"]),
        Paragraph("Comprender tu carta puede cambiar la forma en la que te miras.", estilos["cuerpo"]),
        Paragraph(
            "Lo que transforme tu vida dependerá de cómo decidas habitarla a partir de ahora.",
            estilos["cuerpo"],
        ),
    ]))
    contenido.append(Spacer(1, 0.35*cm))
    contenido.append(KeepTogether([
        Paragraph("Arquitectura Interna", estilos["subtitulo2"]),
        Paragraph("Un método para sostener cuerpo, energía y vida con coherencia", estilos["cuerpo"]),
    ]))

    doc.build(contenido, onFirstPage=agregar_pagina, onLaterPages=agregar_pagina)


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print("═" * 55)
    print("  SOL · ASCENDENTE · NODOS — Arquitectura Interna")
    print("═" * 55)
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

    print("\nCalculando carta natal...")
    try:
        lat, lon = geocodificar(ciudad)
        tz_name = obtener_timezone(lat, lon)
        carta = calcular_carta(anio, mes, dia, hora, minuto, lat, lon, tz_name)
    except Exception as e:
        print(f"Error al calcular la carta: {e}"); sys.exit(1)

    aspectos = calcular_aspectos_sol_asc_nodos(carta["planetas"], carta["asc"])
    nombre_f = nombre.replace(" ", "_").replace("/", "-")
    ruta_base = os.path.join(BASE_DIR, nombre_f + "_Sol_ASC_Nodos")
    ruta_pdf = ruta_base + ".pdf"
    ruta_rueda = ruta_base + "_rueda.png"

    print("  Generando rueda...")
    dibujar_rueda_sol_asc_nodos(carta, aspectos, ruta_rueda)
    print("  Generando PDF con ReportLab...")
    generar_pdf_sol_asc_nodos(
        ruta_pdf, carta, nombre, anio, mes, dia, hora, minuto,
        ciudad, lat, lon, tz_name, aspectos, ruta_rueda,
    )
    print(f"\nPDF generado correctamente:\n{ruta_pdf}")


def generar_carta_api(
    nombre,
    fecha,
    hora,
    lugar,
    lat=None,
    lon=None,
    tz_name=None
):
    print("Generando informe Sol · Ascendente · Nodos para:", nombre)

    try:
        # ── FECHA ─────────────────────────────────────────────
        dia, mes, anio = map(int, fecha.split("/"))

        # ── HORA ──────────────────────────────────────────────
        partes_hora = hora.split(":")
        hora_num = int(partes_hora[0])
        minuto = int(partes_hora[1])

        # ── GEOLOCALIZACIÓN ───────────────────────────────────
        if lat is not None and lon is not None:
            lat = float(lat)
            lon = float(lon)

            if not tz_name:
                tz_name = obtener_timezone(lat, lon)
        else:
            lat, lon = geocodificar(lugar)
            tz_name = obtener_timezone(lat, lon)

        # ── CÁLCULO ───────────────────────────────────────────
        carta = calcular_carta(
            anio,
            mes,
            dia,
            hora_num,
            minuto,
            lat,
            lon,
            tz_name
        )

        aspectos = calcular_aspectos_sol_asc_nodos(
            carta["planetas"],
            carta["asc"]
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
            nombre_f + "_Sol_ASC_Nodos"
        )

        ruta_pdf = ruta_base + ".pdf"
        ruta_rueda = ruta_base + "_rueda.png"

        dibujar_rueda_sol_asc_nodos(
            carta,
            aspectos,
            ruta_rueda
        )

        generar_pdf_sol_asc_nodos(
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
            ruta_rueda
        )

        if not os.path.exists(ruta_pdf):
            return {
                "ok": False,
                "error": "No se ha podido crear el PDF."
            }

        nombre_archivo = os.path.basename(ruta_pdf)

        return {
            "ok": True,
            "pdf": f"/descargas/{nombre_archivo}",
            "pdf_url": f"/descargas/{nombre_archivo}"
        }

    except Exception as error:
        print(
            "Error generando Sol · Ascendente · Nodos:",
            error
        )

        return {
            "ok": False,
            "error": str(error)
        }


if __name__ == "__main__":
    main()
