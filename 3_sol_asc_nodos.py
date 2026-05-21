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
    "Sueles vivir las cosas de forma rápida e inmediata. "
    "Muchas veces necesitas moverte, actuar o reaccionar para entender realmente lo que te está pasando.\n\n"
    
    "Cuando pasas demasiado tiempo conteniéndote, esperando o sin poder actuar, es fácil que la tensión se acumule en el cuerpo. "
    "Puede aparecer irritación, impaciencia o una sensación constante de presión interna.\n\n"
    
    "Te ayuda poder iniciar, probar, equivocarte y ajustar sobre la marcha. "
    "Cuando todo queda detenido durante demasiado tiempo, también se bloquea la forma en la que procesas lo que te ocurre."
),

"Tauro": (
    "Necesitas tiempo para registrar lo que te ocurre. "
    "La experiencia suele asentarse primero en el cuerpo y en las sensaciones antes de que puedas entenderla del todo.\n\n"
    
    "Las prisas, los cambios bruscos o la presión para responder rápidamente suelen hacer que te desconectes de lo que realmente sientes. "
    "A veces puedes reaccionar demasiado rápido hacia afuera y darte cuenta después de que eso no era exactamente lo que querías.\n\n"
    
    "Te ayuda tener estabilidad, tiempo para asimilar y entornos donde no tengas que vivir en alerta constante."
),

"Géminis": (
    "Necesitas movimiento para entender lo que vives. "
    "Necesitas pensar, preguntar, hablar o relacionar lo que ocurre con otras ideas para poder entenderlo.\n\n"
    
    "Cuando no puedes expresarte o explorar lo que piensas, la inquietud empieza a crecer por dentro. "
    "Es fácil que aparezca ruido mental, dispersión o sensación de tener demasiadas cosas abiertas al mismo tiempo.\n\n"
    
    "Te ayuda poder hablar sobre lo que vives y darle espacio antes de sacar conclusiones demasiado rápido."
),

"Cáncer": (
    "Tu primera reacción suele ser percibir si hay seguridad o no en lo que está ocurriendo. "
    "Antes incluso de pensarlo, tu cuerpo ya está leyendo el ambiente y evaluando cuánto puede relajarse.\n\n"
    
    "Cuando no sientes seguridad o el entorno es ambiguo, es fácil cerrarte, protegerte o tomar distancia aunque sigas presente hacia afuera.\n\n"
    
    "Necesitas espacios donde puedas bajar la guardia y sentir suficiente confianza para vivir lo que te pasa sin cerrarte."
),

"Leo": (
    "Sueles conectar primero con lo que vives antes de poder entenderlo del todo."
    "Necesitas sentir que hay algo vivo, importante o auténtico para implicarte de verdad.\n\n"
    
    "Cuando todo se vuelve demasiado impersonal o sientes que no puedes expresarte con naturalidad, es fácil desconectarte poco a poco.\n\n"
    
    "Te ayuda sentir que puedes participar desde un lugar propio y no solamente cumplir una función vacía dentro del entorno."
),

"Virgo": (
    "Sueles necesitar comprender, ordenar o ajustar lo que estás viviendo para poder procesarlo bien."
    "Muchas veces observas rápidamente los detalles, lo que falta o lo que podría hacerse mejor.\n\n"
    
    "Cuando el entorno es muy caótico o no hay tiempo para procesar lo que ocurre, puede aparecer ansiedad, irritación o sensación de tener algo pendiente todo el tiempo.\n\n"
    
    "Te ayuda sentir cierta claridad, coherencia y espacio para entender bien las cosas antes de seguir acumulando experiencia."
),

"Libra": (
    "Lo que vives suele tomar forma a través de las relaciones y del contacto con otras personas."
    "Necesitas contraste, intercambio y cierta referencia externa para aclarar cómo te posicionas frente a lo que ocurre.\n\n"
    
    "Cuando pasas demasiado tiempo sin diálogo, sin referencias o en relaciones tensas y desequilibradas, es fácil quedarte en suspensión y no saber bien hacia dónde moverte.\n\n"
    
    "Te ayuda poder pensar junto a otras personas y sentir que hay espacio para el acuerdo, el ajuste y la negociación."
),

"Escorpio": (
    "Sueles percibir rápidamente lo que no se está diciendo de forma explícita. "
    "Muchas veces captas el fondo emocional, las tensiones o las contradicciones antes incluso que las palabras.\n\n"
    
    "Cuando el entorno tiene dobles mensajes, falta de honestidad o tensión constante, es difícil relajarte del todo. "
    "La vigilancia puede quedarse encendida incluso cuando ya no hace falta.\n\n"
    
    "Te ayuda sentir profundidad, coherencia y vínculos donde no tengas que estar interpretando continuamente lo que ocurre debajo de la superficie."
),

"Sagitario": (
    "Necesitas entender el sentido de lo que vives para poder integrarlo de verdad. "
    "Sueles entender mejor lo que vives cuando puedes conectarlo con algo más amplio.\n\n"
    
    "Cuando todo se vuelve repetitivo, limitado o carente de propósito, aparece rápidamente inquietud, impaciencia o sensación de desconexión.\n\n"
    
    "Te ayuda aprender, explorar y sentir que lo que haces forma parte de algo que tiene significado para ti."
),

"Capricornio": (
    "Muchas veces lo primero que haces al vivir algo es evaluar qué requiere de ti y cómo responder de la mejor manera posible."
    "Necesitas tiempo para medir, ordenar y entender qué está ocurriendo antes de abrirte completamente.\n\n"
    
    "Cuando el entorno es muy caótico o exige respuestas emocionales inmediatas, es fácil que tomes distancia o te cierres más de lo que desearías.\n\n"
    
    "Te ayuda sentir estructura, claridad y cierta estabilidad para poder relajarte y vivir las cosas con más calma."
),

"Acuario": (
    "Muchas veces necesitas entender lo que ocurre antes de conectar emocionalmente con ello. "
    "Tu mente suele intentar ordenar, observar o encontrar perspectiva antes de reaccionar.\n\n"
    
    "Cuando el entorno exige respuestas emocionales inmediatas o demasiado intensas, es fácil que te alejes hacia la observación y parezcas más distante de lo que realmente estás.\n\n"
    
    "Te ayuda tener espacio para pensar, comprender y encontrar tu propia forma de relacionarte con lo que vives."
),

"Piscis": (
    "Sueles vivir las cosas de una forma muy abierta."
    "Muchas veces percibes no solo lo que te ocurre a ti, sino también el ambiente emocional y el estado de las personas alrededor.\n\n"
    
    "Cuando el entorno está muy saturado o no tienes espacios para descansar y desconectar, es fácil confundirte, agotarte o perder claridad sobre lo que realmente necesitas.\n\n"
    
    "Te ayuda tener momentos de silencio, pausa y lugares donde puedas volver a sentir qué es verdaderamente tuyo y qué no."
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
    """Calcula aspectos entre Sol, Nodos y Ascendente."""
    sol = planetas.get("Sol")
    nn  = planetas.get("Nodo Norte")
    ns  = planetas.get("Nodo Sur")

    if not asc or "lon" not in asc:
        return []

    asc_lon = asc["lon"]
    aspectos = []

    pares = []

    if sol:
        if nn:
            pares.append(("Sol", "Nodo Norte", sol["lon"], nn["lon"]))
        if ns:
            pares.append(("Sol", "Nodo Sur", sol["lon"], ns["lon"]))
        pares.append(("Sol", "Ascendente", sol["lon"], asc_lon))

    if nn:
        pares.append(("Nodo Norte", "Ascendente", nn["lon"], asc_lon))

    if ns:
        pares.append(("Nodo Sur", "Ascendente", ns["lon"], asc_lon))

    for p1_nombre, p2_nombre, lon1, lon2 in pares:
        diff = abs(lon1 - lon2) % 360
        if diff > 180:
            diff = 360 - diff

        for tipo, angulo, orbe_max, simbolo in ASPECTOS_DEF:
            if abs(diff - angulo) <= orbe_max:
                orbe_val = round(abs(diff - angulo), 2)
                aspectos.append({
                    "p1": p1_nombre,
                    "p2": p2_nombre,
                    "tipo": tipo,
                    "simbolo": simbolo,
                    "orbe": orbe_val,
                    "relevancia": "exacto" if orbe_val <= 1.0 else "estructural",
                })
                break

    return sorted(aspectos, key=lambda x: x["orbe"])


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
            f"El Sol en {sol_signo}, Casa {sol_casa}, no tiene un aspecto directo con los Nodos. "
            f"La tensión entre el Nodo Norte en {nn_signo}, Casa {nn_casa}, y el Nodo Sur en {ns_signo}, Casa {ns_casa}, "
            f"se expresa de una forma más independiente respecto a la dirección solar."
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

def texto_ascendente(carta, aspectos=None):
    if aspectos is None:
        aspectos = []

    planetas = carta["planetas"]
    asc = carta.get("asc", {})
    asc_signo = asc.get("signo", "")
    asc_grado = asc.get("grado", "")

    t = ASC_SIGNO.get(asc_signo, "")

    # Regente del Ascendente y su posición
    regente = REGENTE_SIGNO.get(asc_signo, "")
    if regente and regente in planetas:
        r = planetas[regente]
        elem_r = ELEMENTO_SIGNO.get(r["signo"], "")
        elem_asc = ELEMENTO_SIGNO.get(asc_signo, "")

        if elem_r == elem_asc:
            tono = (
                "pertenece al mismo elemento que el Ascendente. "
                "Esto suele dar continuidad entre tu primera reacción y la forma en que después elaboras lo que ocurre"
            )
        elif {elem_r, elem_asc} in ({"Fuego", "Aire"}, {"Tierra", "Agua"}):
            tono = (
                "pertenece a un elemento compatible con el Ascendente. "
                "Esto puede facilitar que tu primera reacción y la forma en que después elaboras lo que ocurre se apoyen con cierta fluidez"
            )
        else:
            tono = (
                "pertenece a un elemento con una lógica diferente a la del Ascendente. "
                f"Esto puede hacer que vivas las cosas de una forma, mientras otra parte de ti necesita orientarse desde un ritmo completamente diferente."
            )

        t += (
            f"\n\nEl regente del Ascendente es {regente}, situado en {r['signo']}, Casa {r['casa']}. "
            f"{regente} {tono}. "
            f"La Casa {r['casa']} muestra un territorio importante desde el que organizas tu forma de entrar en la vida."
        )

    # Aspectos al Ascendente: Sol y Nodos
    for asp in aspectos:
        clave1 = (asp["p1"], asp["p2"], asp["simbolo"])
        clave2 = (asp["p2"], asp["p1"], asp["simbolo"])

        texto_asp = (
            ASPECTOS_SOL_ASC.get(clave1)
            or ASPECTOS_SOL_ASC.get(clave2)
            or ASPECTOS_NODO_NORTE_ASC.get(clave1)
            or ASPECTOS_NODO_NORTE_ASC.get(clave2)
            or ASPECTOS_NODO_SUR_ASC.get(clave1)
            or ASPECTOS_NODO_SUR_ASC.get(clave2)
        )

        if texto_asp:
            t += f"\n\n{texto_asp}"

    return t

def texto_nodos(carta, aspectos):
    planetas = carta["planetas"]

    nn = planetas.get("Nodo Norte", {})
    ns = planetas.get("Nodo Sur", {})

    nn_signo = nn.get("signo", "")
    nn_casa  = nn.get("casa", 1)

    ns_signo = ns.get("signo", "")
    ns_casa  = ns.get("casa", 1)

    t = ""

    # Nodo Norte
    texto_nn_signo = NODO_NORTE_SIGNO.get(nn_signo, "")
    if texto_nn_signo:
        t += texto_nn_signo

    texto_nn_casa = NODO_NORTE_CASA.get(nn_casa, "")
    if texto_nn_casa:
        t += "\n\n" + texto_nn_casa

    # Nodo Sur
    texto_ns_signo = NODO_SUR_SIGNO.get(ns_signo, "")
    if texto_ns_signo:
        t += "\n\n" + texto_ns_signo

    texto_ns_casa = NODO_SUR_CASA.get(ns_casa, "")
    if texto_ns_casa:
        t += "\n\n" + texto_ns_casa

    # Aspectos relevantes
    asp_relevantes = [
        a for a in aspectos
        if (
            a.get("p1") in ("Sol", "Nodo Norte", "Nodo Sur", "Ascendente")
            or
            a.get("p2") in ("Sol", "Nodo Norte", "Nodo Sur", "Ascendente")
        )
    ]

    for asp in asp_relevantes:

        clave1 = (asp["p1"], asp["p2"], asp["simbolo"])
        clave2 = (asp["p2"], asp["p1"], asp["simbolo"])

        texto_asp = (
            ASPECTOS_SOL_NODOS.get(clave1)
            or ASPECTOS_SOL_NODOS.get(clave2)
            or ASPECTOS_NODO_NORTE_ASC.get(clave1)
            or ASPECTOS_NODO_NORTE_ASC.get(clave2)
            or ASPECTOS_NODO_SUR_ASC.get(clave1)
            or ASPECTOS_NODO_SUR_ASC.get(clave2)
        )

        if texto_asp and texto_asp not in t:
            t += f"\n\n{texto_asp}"

    return t

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
    planetas = carta["planetas"]
    asc = carta.get("asc", {})
    asc_signo = asc.get("signo", "")

    sol = planetas.get("Sol", {})
    nn  = planetas.get("Nodo Norte", {})
    ns  = planetas.get("Nodo Sur", {})

    sol_signo = sol.get("signo", "")
    sol_casa  = sol.get("casa", 1)

    nn_signo = nn.get("signo", "")
    nn_casa  = nn.get("casa", 1)

    ns_signo = ns.get("signo", "")
    ns_casa  = ns.get("casa", 1)

    elem_sol = ELEMENTO_SIGNO.get(sol_signo, "")
    elem_asc = ELEMENTO_SIGNO.get(asc_signo, "")
    elem_nn  = ELEMENTO_SIGNO.get(nn_signo, "")

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

    partes = []

    # Sol–Ascendente
    if elem_sol and elem_asc and elem_sol == elem_asc:
        partes.append(
            f"El Ascendente en {asc_signo} y el Sol en {sol_signo} pertenecen al mismo elemento. "
            f"Esto suele hacer que tu forma más espontánea de vivir la vida y tu dirección principal estén bastante alineadas."
            f"Cuando esta coherencia funciona bien, puedes pasar de la reacción inicial a la acción con bastante naturalidad. "
            f"El reto está en no confundir esa facilidad con consciencia real: algo puede salirte de forma natural y aun así necesitar más atención."
        )
    elif elem_sol and elem_asc and {elem_sol, elem_asc} in ({"Fuego", "Aire"}, {"Tierra", "Agua"}):
        partes.append(
            f"El Ascendente en {asc_signo} y el Sol en {sol_signo} pertenecen a elementos compatibles. "
            f"Esto puede ayudar a que tu primera forma de reaccionar y tu dirección principal se apoyen con cierta fluidez. "
            f"No significa que todo sea automático, pero sí que hay una base de entendimiento entre cómo empiezas las cosas y hacia dónde necesitas orientarte."
        )
    else:
        partes.append(
            f"El Ascendente en {asc_signo} y el Sol en {sol_signo} pertenecen a elementos con lógicas diferentes. "
            f"Esto puede hacer que una parte de ti quiera vivir las cosas de una forma, mientras otra necesita avanzar desde un ritmo completamente diferente."
            f"Cuando no hay espacio para traducir esas dos formas internas, puedes sentir que reaccionas por un lado y deseas orientarte por otro. "
            f"El trabajo está en no forzarte a elegir una sola parte, sino en aprender a darles un lugar más coherente."
        )

    if asp_sol_asc:
        partes.append(
            f"Además, el Sol hace {asp_sol_asc['tipo'].lower()} con el Ascendente "
            f"(orbe {asp_sol_asc['orbe']}°). "
            f"Esto refuerza la importancia de observar cómo se relacionan tu manera de entrar en la vida y tu dirección principal."
        )

    # Sol–Nodos
    if sol_signo == nn_signo:
        partes.append(
            f"El Sol y el Nodo Norte están en {nn_signo}. "
            f"Esto une tu dirección principal con una zona importante de crecimiento. "
            f"Puede darte una sensación más clara de hacia dónde avanzar, pero no significa que ese camino ya esté integrado. "
            f"El reto está en no dar por hecho que lo natural ya está plenamente desarrollado."
        )
    elif sol_signo == ns_signo:
        partes.append(
            f"El Sol está en el mismo signo que el Nodo Sur, {ns_signo}. "
            f"Esto hace que los patrones conocidos tengan mucha fuerza y puedan sentirse muy naturales. "
            f"Moverte hacia el Nodo Norte en {nn_signo}, Casa {nn_casa}, requiere más consciencia, decisión y práctica. "
            f"No se trata de rechazar lo conocido, sino de no quedarte viviendo únicamente desde ahí."
        )
    elif asp_sol_nn:
        es_tenso = asp_sol_nn["simbolo"] in ("□", "☍", "⚻")
        if es_tenso:
            partes.append(
                f"El Sol en {sol_signo} hace {asp_sol_nn['tipo'].lower()} con el Nodo Norte en {nn_signo} "
                f"(orbe {asp_sol_nn['orbe']}°). "
                f"Esto puede traer fricción entre lo que te sale de forma más natural y aquello que necesitas desarrollar. "
                f"El crecimiento no suele aparecer evitando esa tensión, sino aprendiendo a atravesarla con más claridad."
            )
        else:
            partes.append(
                f"El Sol en {sol_signo} hace {asp_sol_nn['tipo'].lower()} con el Nodo Norte en {nn_signo} "
                f"(orbe {asp_sol_nn['orbe']}°). "
                f"Esto puede facilitar el contacto con tu dirección de crecimiento. "
                f"El reto está en no dejar esa facilidad solo como potencial, sino convertirla en decisiones y práctica real."
            )
    elif asp_sol_ns:
        partes.append(
            f"El Sol en {sol_signo} hace {asp_sol_ns['tipo'].lower()} con el Nodo Sur en {ns_signo} "
            f"(orbe {asp_sol_ns['orbe']}°). "
            f"Esto muestra que tu dirección principal está muy conectada con patrones conocidos. "
            f"Puede darte recursos importantes, pero también hacer que vuelvas a lugares familiares cuando hay cansancio, miedo o presión."
        )

    # Ascendente–Nodo Norte
    if elem_asc and elem_nn and elem_asc == elem_nn:
        partes.append(
            f"El Ascendente en {asc_signo} y el Nodo Norte en {nn_signo} pertenecen al mismo elemento. "
            f"La forma en la que vives las cosas de manera natural puede ayudarte a avanzar hacia tu dirección de crecimiento, siempre que haya consciencia en ello."
            f"El reto está en no repetir automáticamente lo que ya conoces solo porque se parece a lo que también necesitas desarrollar."
        )
    elif elem_asc and elem_nn and {elem_asc, elem_nn} in ({"Fuego", "Aire"}, {"Tierra", "Agua"}):
        partes.append(
            f"El Ascendente en {asc_signo} y el Nodo Norte en {nn_signo} pertenecen a elementos compatibles. "
            f"Esto puede facilitar que tu forma de reaccionar y tu dirección de crecimiento encuentren una vía de colaboración. "
            f"Aun así, esa posibilidad necesita elección consciente para no quedarse solo en tendencia."
        )
    else:
        partes.append(
            f"El Ascendente en {asc_signo} y el Nodo Norte en {nn_signo} pertenecen a elementos con lógicas diferentes. "
            f"Esto puede hacer que crecer te pida actuar de una manera que no siempre coincide con tu primera reacción. "
            f"El trabajo está en aprender a no obedecer siempre al primer impulso y dejar espacio a una dirección más nueva."
        )

    if asp_nn_asc:
        partes.append(
            f"Además, el Nodo Norte hace {asp_nn_asc['tipo'].lower()} con el Ascendente "
            f"(orbe {asp_nn_asc['orbe']}°). "
            f"Esto hace que la dirección de crecimiento toque directamente tu forma de posicionarte en la vida."
        )

    if asp_ns_asc:
        partes.append(
            f"El Nodo Sur hace {asp_ns_asc['tipo'].lower()} con el Ascendente "
            f"(orbe {asp_ns_asc['orbe']}°). "
            f"Esto muestra que algunos patrones conocidos pueden estar muy incorporados en tu forma espontánea de reaccionar."
        )

    return "\n\n".join(partes)


def texto_orientacion(carta, aspectos):
    planetas = carta["planetas"]
    asc = carta.get("asc", {})
    asc_signo = asc.get("signo", "")

    sol = planetas.get("Sol", {})
    nn  = planetas.get("Nodo Norte", {})
    ns  = planetas.get("Nodo Sur", {})

    sol_signo = sol.get("signo", "")
    sol_casa  = sol.get("casa", 1)

    nn_signo = nn.get("signo", "")
    nn_casa  = nn.get("casa", 1)

    ns_signo = ns.get("signo", "")
    ns_casa  = ns.get("casa", 1)

    elem_asc = ELEMENTO_SIGNO.get(asc_signo, "")
    elem_sol = ELEMENTO_SIGNO.get(sol_signo, "")

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

    inicio_map = {
        "Fuego": (
            f"Desde el Ascendente en {asc_signo}: empezar con un gesto concreto, aunque no esté todo resuelto. "
            f"Tu claridad suele aparecer cuando te pones en movimiento, no antes."
        ),
        "Tierra": (
            f"Desde el Ascendente en {asc_signo}: dar un paso concreto, pequeño y verificable. "
            f"Te ayuda tocar la realidad antes de intentar entenderlo todo mentalmente."
        ),
        "Aire": (
            f"Desde el Ascendente en {asc_signo}: poner en palabras lo que está ocurriendo. "
            f"Hablar sobre ello, escribirlo o compartirlo con alguien puede ayudarte a comprender mejor lo que estás viviendo."
        ),
        "Agua": (
            f"Desde el Ascendente en {asc_signo}: registrar primero cómo te está afectando algo. "
            f"Antes de actuar, necesitas escuchar qué se ha movido por dentro."
        ),
    }

    desde_donde = inicio_map.get(
        elem_asc,
        f"Desde el Ascendente en {asc_signo}: darte tiempo para vivir y comprender lo que te pasa antes de intentar responder."
    )

    if asp_sol_asc:
        desde_donde += (
            f" El Sol hace {asp_sol_asc['tipo'].lower()} con el Ascendente "
            f"(orbe {asp_sol_asc['orbe']}°), así que conviene observar especialmente cómo se relacionan tu primera reacción y tu dirección principal."
        )

    sostener_map = {
        "Fuego": (
            f"El Sol en {sol_signo}, Casa {sol_casa}, necesita una dirección activa: algo que iniciar, decidir o llevar adelante. "
            f"Si no hay movimiento real, la energía puede convertirse en irritación, urgencia o acción sin rumbo claro."
        ),
        "Tierra": (
            f"El Sol en {sol_signo}, Casa {sol_casa}, necesita construir algo concreto y sostenible. "
            f"Te ayuda avanzar paso a paso y ver que lo que haces va tomando forma."
        ),
        "Aire": (
            f"El Sol en {sol_signo}, Casa {sol_casa}, necesita pensamiento en movimiento, intercambio y variedad de estímulos. "
            f"Si no hay espacio para procesar o comunicar, puede aparecer dispersión o inquietud mental."
        ),
        "Agua": (
            f"El Sol en {sol_signo}, Casa {sol_casa}, necesita espacio de elaboración interna. "
            f"Te ayuda tener tiempo para sentir, integrar y moverte desde una base más clara."
        ),
    }

    sostener = sostener_map.get(
        elem_sol,
        f"El Sol en {sol_signo}, Casa {sol_casa}, muestra una dirección principal que necesita ser sostenida con atención."
    )

    evitar = (
        f"Evita funcionar únicamente desde el Nodo Sur en {ns_signo}, Casa {ns_casa}. "
        f"Ese lugar puede resultarte conocido y eficaz, pero no debería convertirse en la única respuesta disponible. "
        f"La señal de alerta aparece cuando resuelves siempre desde lo que ya sabes hacer, sin preguntarte si esa respuesta sigue siendo adecuada.\n\n"
        f"El Nodo Norte en {nn_signo}, Casa {nn_casa}, pide desarrollar una forma nueva de orientarte, aunque al principio resulte menos automática."
    )

    tensiones = []
    for asp in (asp_sol_nn, asp_sol_ns, asp_sol_asc, asp_nn_asc, asp_ns_asc):
        if asp and asp.get("simbolo") in ("□", "☍", "⚻"):
            tensiones.append(asp)

    if tensiones:
        asp = tensiones[0]
        evitar += (
            f"\n\nHay una tensión importante entre {asp['p1']} y {asp['p2']} "
            f"por {asp['tipo'].lower()} (orbe {asp['orbe']}°). "
            f"No hace falta resolverla de golpe. Lo importante es aprender a reconocer cuándo esa tensión te bloquea "
            f"y cuándo puede convertirse en una forma más consciente de elegir."
        )

    if asp_nn_asc:
        evitar += (
            f"\n\nEl Nodo Norte hace {asp_nn_asc['tipo'].lower()} con el Ascendente "
            f"(orbe {asp_nn_asc['orbe']}°). "
            f"Esto hace que tu dirección de crecimiento esté muy ligada a la manera en que te posicionas ante la vida."
        )

    if asp_ns_asc:
        evitar += (
            f"\n\nEl Nodo Sur hace {asp_ns_asc['tipo'].lower()} con el Ascendente "
            f"(orbe {asp_ns_asc['orbe']}°). "
            f"Observa especialmente las respuestas que salen solas, porque pueden tener mucho peso en tu forma habitual de actuar."
        )

    return {
        "desde_donde": desde_donde,
        "sostener": sostener,
        "evitar": evitar,
    }

# ─── RUEDA SIMPLIFICADA: SOL + ASC + NODOS ───────────────────────────────────

def dibujar_rueda_sol_asc_nodos(carta, archivo_salida):
    """Rueda simplificada: Sol, Ascendente, Nodo Norte, Nodo Sur."""
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

    puntos_aspecto = {
        "Sol": planetas.get("Sol"),
        "Nodo Norte": planetas.get("Nodo Norte"),
        "Nodo Sur": planetas.get("Nodo Sur"),
        "Ascendente": {"lon": carta["asc"]["lon"]},
    }

    pares_aspecto = [
        ("Sol", "Nodo Norte"),
        ("Sol", "Nodo Sur"),
        ("Sol", "Ascendente"),
        ("Nodo Norte", "Ascendente"),
        ("Nodo Sur", "Ascendente"),
    ]

    for p1, p2 in pares_aspecto:
        obj1 = puntos_aspecto.get(p1)
        obj2 = puntos_aspecto.get(p2)

        if not obj1 or not obj2:
            continue

        diff = abs(obj1["lon"] - obj2["lon"]) % 360
        if diff > 180:
            diff = 360 - diff

        for tipo, angulo, orbe_max, simbolo in ASPECTOS_DEF:
            if abs(diff - angulo) <= orbe_max and simbolo in _ASP_COL:
                a1 = lon_a_angulo(obj1["lon"])
                a2 = lon_a_angulo(obj2["lon"])

                linestyle = "dashed" if "Nodo Sur" in (p1, p2) else "solid"
                alpha = 0.45 if "Nodo Sur" in (p1, p2) else 0.60

                ax.plot(
                    [math.cos(a1) * R_ASP, math.cos(a2) * R_ASP],
                    [math.sin(a1) * R_ASP, math.sin(a2) * R_ASP],
                    color=_ASP_COL[simbolo],
                    linewidth=_ASP_LW[simbolo],
                    alpha=alpha,
                    linestyle=linestyle,
                    zorder=2,
                )
                break

    puntos = {
        "Sol": planetas.get("Sol"),
        "Ascendente": {
            "simbolo": "AC",
            "lon": carta["asc"]["lon"],
            "signo": carta["asc"]["signo"],
            "grado": carta["asc"]["grado"],
        },
        "Nodo Norte": planetas.get("Nodo Norte"),
        "Nodo Sur": planetas.get("Nodo Sur"),
    }

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
        fs = 22 if nombre == "Sol" else 16 if nombre == "Ascendente" else 18

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

    plt.title("Sol · Ascendente · Nodos", fontsize=12, fontweight="bold", pad=12, color="#1E508C")
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
                  ciudad, lat, lon, tz_name, aspectos, ruta_rueda):
    planetas  = carta["planetas"]
    cuspides  = carta["cuspides"]
    asc       = carta["asc"]
    mc        = carta["mc"]
    ruta_rueda = os.path.basename(ruta_rueda).replace("\\", "/")

    sol = planetas.get("Sol", {})
    nn  = planetas.get("Nodo Norte", {})
    ns  = planetas.get("Nodo Sur", {})

    fecha_str  = f"{dia:02d}/{mes:02d}/{anio}"
    hora_str   = f"{hora:02d}:{minuto:02d}"
    tz_obj     = pytz.timezone(tz_name)
    dt_local   = tz_obj.localize(datetime(anio, mes, dia, hora, minuto))
    utc_off    = dt_local.strftime("%z")
    utc_str    = f"UTC{utc_off[:3]}:{utc_off[3:]}"
    nom_esc    = esc(nombre)
    ciu_esc    = esc(ciudad)

    sol_signo  = sol.get("signo", "")
    sol_casa   = sol.get("casa", "")
    sol_grado  = sol.get("grado", 0)
    nn_signo   = nn.get("signo", "")
    nn_casa    = nn.get("casa", "")
    nn_grado   = nn.get("grado", 0)
    ns_signo   = ns.get("signo", "")
    ns_casa    = ns.get("casa", "")
    ns_grado   = ns.get("grado", 0)

    regente_asc = REGENTE_SIGNO.get(asc["signo"], "")

    t_dir   = texto_direccion_general(carta, aspectos)
    t_sol   = texto_sol(carta, aspectos)
    t_interceptaciones = texto_interceptaciones(carta)
    t_asc   = texto_ascendente(carta, aspectos)
    t_nodos = texto_nodos(carta, aspectos)
    t_anareticos = texto_grados_anareticos(carta)
    t_integ = texto_integracion(carta, aspectos)
    t_or    = texto_orientacion(carta, aspectos)

    # Tabla de aspectos
    asp_rows = ""
    for a in aspectos:
        asp_rows += (
            f"  {esc(a['p1'])} & {esc(a['simbolo'])} & {esc(a['p2'])} & "
            f"{esc(a['tipo'])} & {a['orbe']:.1f}° \\\\\n"
        )

    # Bloque de aspectos
    if asp_rows.strip():
        tabla_aspectos = (
            "\\begin{center}\n"
            "\\begin{tabular}{lllll}\n"
            "  \\toprule\n"
            "  \\textbf{Planeta 1} & \\textbf{Asp.} & \\textbf{Planeta 2} & \\textbf{Tipo} & \\textbf{Orbe} \\\\\n"
            "  \\midrule\n"
            f"{asp_rows}"
            "  \\bottomrule\n"
            "\\end{tabular}\n"
            "\\end{center}"
        )
    else:
        tabla_aspectos = (
            "\\vspace{0.3cm}\n"
            "\\textit{No aparecen aspectos directos entre Sol, Ascendente y Nodos dentro de los orbes definidos. "
            "Esto no significa ausencia de relación entre estos puntos, sino que la lectura se apoya principalmente "
            "en sus signos, casas, elementos e integración general.}"
        )

    def parrafos(texto):
        return "\n\n".join(esc(p) for p in texto.split("\n\n") if p.strip())

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
\\titlespacing*{{\\section}}{{0pt}}{{1.8em}}{{0.8em}}
\\titleformat{{\\subsection}}{{\\large\\bfseries\\color{{doradoai}}}}{{}}{{0em}}{{}}
\\titlespacing*{{\\subsection}}{{0pt}}{{1.4em}}{{0.5em}}
\\titleformat{{\\subsubsection}}{{\\normalsize\\bfseries\\color{{grisai}}}}{{}}{{0em}}{{}}
\\titlespacing*{{\\subsubsection}}{{0pt}}{{1.0em}}{{0.3em}}

\\pagestyle{{fancy}}\\fancyhf{{}}
\\rhead{{\\textcolor{{grisai}}{{\\small {nom_esc} — Arquitectura Interna}}}}
\\lhead{{\\textcolor{{grisai}}{{\\small Sol · Ascendente · Nodos}}}}
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
  {{\\Huge\\bfseries\\color{{azulai}} Sol · Ascendente · Nodos}}\\\\[0.5cm]
  {{\\large\\color{{grisai}} Arquitectura Interna}}\\\\[0.3cm]
  {{\\small\\itshape\\color{{grisai}} Dirección vital, punto de entrada y eje de desarrollo}}\\\\[2cm]
  {{\\huge\\color{{doradoai}} {nom_esc}}}\\\\[1.5cm]
  {{\\Large {fecha_str} \\quad {hora_str}}}\\\\[0.3cm]
  {{\\Large {ciu_esc}}}\\\\[0.3cm]
  {{\\normalsize Lat: {lat:.4f}° \\quad Lon: {lon:.4f}° \\quad {utc_str}}}\\\\[0.3cm]
  {{\\normalsize Ascendente: {esc(asc['signo'])} {grado_a_dms(asc['grado'])} \\quad
    MC: {esc(mc['signo'])} {grado_a_dms(mc['grado'])}}}\\\\[2cm]
  \\begin{{tabular}}{{lll}}
    \\textbf{{Sol:}} & {esc(sol_signo)} & Casa {sol_casa} \\\\
    \\textbf{{Ascendente:}} & {esc(asc['signo'])} & Punto de entrada principal: {esc(regente_asc)} \\\\
    \\textbf{{Nodo Norte:}} & {esc(nn_signo)} & Casa {nn_casa} \\\\
    \\textbf{{Nodo Sur:}}   & {esc(ns_signo)} & Casa {ns_casa} \\\\
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
  \\textbf{{Punto}} & \\textbf{{Signo}} & \\textbf{{Casa}} & \\textbf{{Posición}} \\\\
  \\midrule
  Sol           & {esc(sol_signo)} & {sol_casa} & {grado_a_dms(sol_grado)} \\\\
  Ascendente    & {esc(asc['signo'])} & --- & {grado_a_dms(asc['grado'])} \\\\
  Medio Cielo   & {esc(mc['signo'])} & --- & {grado_a_dms(mc['grado'])} \\\\
  Nodo Norte    & {esc(nn_signo)} & {nn_casa} & {grado_a_dms(nn_grado)} \\\\
  Nodo Sur      & {esc(ns_signo)} & {ns_casa} & {grado_a_dms(ns_grado)} \\\\
  \\bottomrule
\\end{{tabular}}
\\end{{center}}

\\vspace{{0.5cm}}
\\textbf{{Regente del Ascendente ({esc(asc['signo'])}):}} 
{esc(regente_asc)} —
{esc(planetas.get(regente_asc, {}).get('signo',''))}, 
Casa {planetas.get(regente_asc, {}).get('casa','')}

\\vspace{{0.5cm}}
\\textbf{{Aspectos entre Sol, Ascendente y Nodos:}}

{tabla_aspectos}

\\needspace{{3\\baselineskip}}
\\subsection*{{Grados sensibles}}

{parrafos(t_anareticos)}

\\vspace{{0.7cm}}

\\begin{{center}}
\\includegraphics[width=0.72\\textwidth]{{{ruta_rueda}}}
\\end{{center}}


\\vspace{{0.3cm}}
\\Needspace{{5\\baselineskip}}

% ── Interpretación ────────────────────────────────────────────────────────────
\\section{{Interpretación — Arquitectura Interna}}

\\begin{{center}}
{{\\small\\itshape
No se trata de definir quién eres. Se trata de observar cómo se organiza tu dirección,
cómo atraviesas la vida y qué tensión influye en tu forma de avanzar.
}}
\\end{{center}}

\\vspace{{0.5cm}}
\\Needspace{{5\\baselineskip}}


% ── 1. Dirección general ──────────────────────────────────────────────────────
\\needspace{{3\\baselineskip}}
\\subsection{{1. Dirección general}}

{parrafos(t_dir)}

\\vspace{{0.5cm}}
\\Needspace{{5\\baselineskip}}


% ── 2. Sol ────────────────────────────────────────────────────────────────────
\\needspace{{3\\baselineskip}}
\\subsection{{2. El Sol — Dirección principal}}

\\needspace{{3\\baselineskip}}
\\subsubsection*{{Sol en {esc(sol_signo)} · Casa {sol_casa}}}

{parrafos(t_sol)}
{parrafos(t_interceptaciones)}

\\vspace{{0.5cm}}
\\Needspace{{5\\baselineskip}}


% ── 3. Ascendente ─────────────────────────────────────────────────────────────
\\needspace{{3\\baselineskip}}
\\subsection{{3. El Ascendente — Forma de relacionarte con la vida}}

\\needspace{{3\\baselineskip}}
\\subsubsection*{{{esc(asc['signo'])} · Regente: {esc(regente_asc)}}}

{parrafos(t_asc)}

\\vspace{{0.5cm}}
\\Needspace{{5\\baselineskip}}


% ── 4. Nodos ──────────────────────────────────────────────────────────────────
\\needspace{{3\\baselineskip}}
\\subsection{{4. Nodo Norte y Nodo Sur — Dirección de crecimiento}}

\\needspace{{3\\baselineskip}}
\\subsubsection*{{Nodo Norte en {esc(nn_signo)} · Casa {nn_casa} \\\\
Nodo Sur en {esc(ns_signo)} · Casa {ns_casa}}}

{parrafos(t_nodos)}

\\vspace{{0.5cm}}
\\Needspace{{5\\baselineskip}}


% ── 5. Integración ────────────────────────────────────────────────────────────
\\needspace{{3\\baselineskip}}
\\subsection{{5. Integración — Cómo se relacionan las distintas partes}}

{parrafos(t_integ)}

\\vspace{{0.5cm}}
\\Needspace{{5\\baselineskip}}


% ── 6. Orientación práctica ───────────────────────────────────────────────────
\\needspace{{3\\baselineskip}}
\\subsection{{6. Orientación práctica}}

\\needspace{{3\\baselineskip}}
\\subsubsection*{{Desde dónde empezar}}
{parrafos(t_or['desde_donde'])}

\\needspace{{3\\baselineskip}}
\\subsubsection*{{Qué conviene sostener}}
{parrafos(t_or['sostener'])}

\\needspace{{3\\baselineskip}}
\\subsubsection*{{Qué conviene observar}}
{parrafos(t_or['evitar'])}

\\vspace{{1cm}}

\\begin{{center}}
{{\\small\\itshape\\color{{grisai}}
La astrología se utiliza aquí como una herramienta de observación y orientación.
No define quién eres ni determina lo que va a ocurrir.
}}
\\end{{center}}

\\end{{document}}
"""

    return latex

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
        asc = carta["asc"]
        sol = carta["planetas"].get("Sol", {})
        nn  = carta["planetas"].get("Nodo Norte", {})

        print(f"  ASC: {asc['signo']} {grado_a_dms(asc['grado'])}")
        print(f"  Sol: {sol.get('signo','')} {grado_a_dms(sol.get('grado',0))} — Casa {sol.get('casa','')}")
        print(f"  NN:  {nn.get('signo','')} {grado_a_dms(nn.get('grado',0))} — Casa {nn.get('casa','')}")

    except Exception as e:
        print(f"Error en cálculo astrológico: {e}")
        sys.exit(1)

    aspectos = calcular_aspectos_sol_asc_nodos(carta["planetas"], carta["asc"])
    print(f"  Aspectos Sol–Ascendente–Nodos: {len(aspectos)}")

    nombre_f   = nombre.replace(" ", "_").replace("/", "-")
    ruta_base  = os.path.join(BASE_DIR, nombre_f + "_Sol_ASC_Nodos")
    ruta_tex   = ruta_base + ".tex"
    ruta_pdf   = ruta_base + ".pdf"

    ruta_rueda = ruta_base + "_rueda.png"

    print("  Generando rueda...")
    dibujar_rueda_sol_asc_nodos(carta, ruta_rueda)

    print("  Generando interpretación...")
    latex = generar_latex(carta, nombre, anio, mes, dia, hora, minuto,
                          ciudad, lat, lon, tz_name, aspectos, ruta_rueda)
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
