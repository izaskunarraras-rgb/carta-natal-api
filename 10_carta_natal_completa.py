#!/usr/bin/env python3
"""
Carta Natal Completa — Arquitectura Interna
Interpretación psicológica evolutiva basada en el método Arquitectura Interna:
un método para sostener cuerpo, energía y vida con coherencia.
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
    "Aries":"Cardinal","Tauro":"Fijo","Géminis":"Mutable","Cáncer":"Cardinal",
    "Leo":"Fijo","Virgo":"Mutable","Libra":"Cardinal","Escorpio":"Fijo",
    "Sagitario":"Mutable","Capricornio":"Cardinal","Acuario":"Fijo","Piscis":"Mutable"
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
    # Fuego
    "Sol":"#CC2200","Marte":"#CC2200","Júpiter":"#CC2200",
    # Tierra
    "Venus":"#2E7D32","Saturno":"#2E7D32",
    # Aire
    "Mercurio":"#E67E00","Urano":"#E67E00",
    # Agua
    "Luna":"#1A5FA8","Neptuno":"#1A5FA8","Plutón":"#1A5FA8",
    # Especiales
    "Quirón":"#7B2D8B","Lilith":"#7B2D8B",
    "Nodo Norte":"#888800","Nodo Sur":"#888800",
}

# ─── TEXTOS: SOL POR SIGNO ─────────────────────────────────────────────────────

SOL_SIGNO = {
"Aries": (
    "Tu Sol en Aries necesita pasar a la acción antes de que todo esté listo. "
    "Tu energía se enciende sola ante un reto o un proyecto nuevo, y puede apagarse si no hay movimiento. "
    "Sin algo en marcha o una dirección clara, puedes sentir irritación, vacío o necesidad de activar algo rápidamente. "
    "El riesgo no es la falta de energía sino arrancar sin base suficiente y quedarte vacío después del impulso."
),
"Tauro": (
    "Tu Sol en Tauro construye tu forma de ser a través de lo concreto: lo que tienes, lo que conoces por experiencia directa, "
    "lo que has levantado con paciencia. Tu energía no responde bien a la presión externa, "
    "pero cuando algo te importa de verdad puedes mantenerte durante mucho tiempo. "
    "El riesgo aparece cuando la necesidad de estabilidad se convierte en resistencia a cualquier cambio."
),
"Géminis": (
    "Tu Sol en Géminis se construye a través de las conexiones, las ideas y el movimiento entre distintos mundos. "
    "Necesitas estimulación mental y te adaptas bien a situaciones cambiantes. "
    "Necesitas movimiento mental, conversaciones, estímulos y sensación de circulación. "
    "El riesgo aparece cuando la variedad no encuentra profundidad: puedes dispersarte y perder el centro."
),
"Cáncer": (
    "Tu Sol en Cáncer se construye a través del vínculo, la cercanía y la necesidad de sentir protección y confianza. "
    "Sueles percibir rápidamente el estado emocional del entorno y reaccionar a él incluso antes de pensarlo. "
    "Tu capacidad de sostener y cuidar puede ser muy alta, especialmente cuando alguien te importa de verdad. "
    "El riesgo aparece cuando cargas demasiado tiempo con lo de los demás y acabas agotándote sin darte cuenta."
),
"Leo": (
    "Tu Sol en Leo necesita espacios donde puedas expresarte, crear y recibir reconocimiento real. "
    "Hay generosidad natural que, cuando está bien sostenida, puede ser muy poderosa. "
    "El riesgo no es el orgullo sino depender demasiado de lo que los demás devuelven: "
    "cuando ese reconocimiento desaparece, puedes desorganizarte emocionalmente más rápido de lo que parece desde fuera."
),
"Virgo": (
    "Tu Sol en Virgo construye tu identidad a través del análisis, la mejora y la utilidad práctica. "
    "Tu energía se activa cuando hay algo concreto que ordenar, mejorar o entender bien. "
    "El rigor y la competencia son tus formas de afirmarte. "
    "El riesgo es el perfeccionismo: la autoexigencia puede volverse más dura que el error que intenta corregir."
),
"Libra": (
    "Tu Sol en Libra funciona en relación con los demás. "
    "Tiendes a percibir rápidamente el clima de una situación y cómo afecta a las personas implicadas. "
    "La capacidad de mediar, ajustar y buscar equilibrio suele aparecer de forma natural. "
    "El riesgo aparece cuando mantener la armonía se vuelve más importante que sostener tu propia posición. "
    "En determinados momentos puede costarte tomar decisiones que generen demasiado desequilibrio alrededor."
),
"Escorpio": (
    "Tu Sol en Escorpio funciona con intensidad y necesidad de implicación real. "
    "No te resulta fácil hacer las cosas a medias ni permanecer mucho tiempo en situaciones que sientes vacías o superficiales. "
    "Cuando algo importa, tiendes a implicarte profundamente y a percibir rápidamente las tensiones ocultas. "
    "El riesgo aparece cuando la necesidad de protegerte te lleva a controlar demasiado o a cerrarte antes de tiempo."
),
"Sagitario": (
    "Tu Sol en Sagitario necesita sentir que lo que haces tiene dirección y sentido para ti. "
    "Funcionas mejor cuando hay movimiento, aprendizaje o sensación de expansión. "
    "La capacidad de entusiasmarte y abrir perspectivas suele aparecer de forma natural. "
    "El riesgo aparece cuando la necesidad de avanzar hace difícil detenerte en lo cotidiano o sostener procesos lentos."
),
"Capricornio": (
    "Tu Sol en Capricornio construye quién eres a través del esfuerzo sostenido, la responsabilidad "
    "y construir algo sólido. Tu energía puede parecer lenta al principio, pero tienes una capacidad de perseverar "
    "que pocos signos igualan. Tu autoridad real viene de la experiencia, no del título. "
    "El riesgo es confundir tu valor con tus logros: cuando los resultados fallan, puedes tambalearte."
),
"Acuario": (
    "Tu Sol en Acuario necesita espacio para pensar diferente y cuestionar lo establecido. "
    "Sueles ver posibilidades, conexiones o alternativas que otras personas no consideran tan rápido. "
    "La independencia y la necesidad de hacer las cosas a tu manera pueden ser muy importantes para ti. "
    "El riesgo aparece cuando te quedas demasiado en las ideas y pierdes contacto con el cuerpo, lo cotidiano o las personas cercanas."
),
"Piscis": (
    "Tu Sol en Piscis funciona con mucha apertura al entorno. "
    "Percibes matices, estados y necesidades que no siempre están expresados de forma clara. "
    "Eso puede darte sensibilidad y facilidad para conectar con lo que ocurre alrededor, pero también puede hacer que te adaptes demasiado. "
    "La dificultad aparece cuando no hay límites suficientes: puedes perder claridad sobre lo que quieres tú."
),
}

# ─── TEXTOS: SOL POR CASA ──────────────────────────────────────────────────────

SOL_CASA = {
1: "En Casa 1, la identidad se expresa directamente a través del cuerpo y la presencia física. "
   "Se consolida al proyectarse en el mundo con iniciativa propia. Los demás "
   "suelen percibir rápidamente tu presencia incluso antes de conocerte bien, y una necesidad de sentir reconocimiento por lo que eres, no por lo que representas.",
2: "En Casa 2, necesitas consolidar tu identidad a través del contacto con tus propios recursos, "
   "valores y capacidades concretas. Tu seguridad interior suele estar ligada a lo que puedes generar por tus propios medios. "
   "Necesitas sentir que puedes sostenerte con recursos propios y confiar en lo que eres capaz de construir de forma autónoma: necesitas una base propia construida desde adentro.",
3: "En Casa 3, tu identidad se sostiene a través de la comunicación, el aprendizaje y el intercambio "
   "con tu entorno próximo. Necesitas que tus ideas tengan peso en los círculos cercanos. "
   "Pensar, hablar, preguntar y compartir ideas forma parte natural de cómo te orientas en el mundo.",
4: "En Casa 4, necesitas una base emocional estable desde la que moverte. "
   "La sensación de hogar, intimidad y protección tiene mucho peso en cómo te desarrollas. "
   "Sueles necesitar espacios donde bajar la guardia y sentir que no tienes que sostener nada hacia afuera constantemente. "
   "Cuando esa base falta, el desgaste aparece aunque externamente todo parezca funcionar.",
5: "En Casa 5, la creatividad, el juego y la expresión auténtica son dimensiones estructurales de tu identidad. "
   "Necesitas crear algo que lleve tu marca. "
   "Sin espacios de expresión genuina, puedes apagarte o perder motivación.",
6: "En Casa 6, la identidad se consolida a través del trabajo concreto, el servicio y la atención "
   "al cuerpo y los hábitos cotidianos. El sentido de propósito se activa cuando hay algo útil que hacer. "
   "El rigor y la mejora continua son formas de sentir estabilidad y dirección.",
7: "En Casa 7, muchas de las cosas importantes de tu vida se activan a través del vínculo con otras personas. "
   "Las relaciones, asociaciones y encuentros significativos suelen tener un impacto directo en cómo te ves. "
   "El contacto con el la otra persona te ayuda a reconocer aspectos propios que quizá no verías por tu cuenta. "
   "El riesgo aparece cuando adaptarte al vínculo pesa más que sostener tu propia posición.",
8: "En Casa 8, no te resulta fácil permanecer en lo superficial. "
   "Las situaciones intensas, los cambios importantes y los vínculos profundos suelen afectarte mucho más de lo que muestras desde fuera. "
   "Cuando atraviesas momentos difíciles, tiendes a cambiar profundamente a partir de ellos. "
   "El riesgo aparece cuando la intensidad ocupa demasiado espacio y hace difícil descansar o soltar el control.",
9: "En Casa 9, necesitas sentir que tu vida avanza hacia algo más amplio que la rutina inmediata. "
   "Aprender, viajar, estudiar o abrir nuevas perspectivas suele ayudarte a recuperar energía y dirección. "
   "Funcionas mejor cuando puedes conectar lo cotidiano con algo que tenga sentido para ti. "
   "El riesgo aparece cuando la necesidad de expansión hace difícil sostener los límites o las obligaciones más concretas.",
10: "En Casa 10, tu identidad está ligada al espacio público, la vocación y el reconocimiento social. "
    "Tienes una necesidad real de construir algo visible que tenga coherencia contigo. "
    "Tu desarrollo profesional no es solo carrera: tiene un peso directo en tu forma de estar en el mundo.",
11: "En Casa 11, los grupos, proyectos compartidos y redes de personas tienen un peso importante en tu vida. "
    "Sueles funcionar mejor cuando sientes que formas parte de algo con dirección o sentido colectivo. "
    "Las amistades y los espacios donde puedes compartir ideas suelen influir mucho en tu desarrollo. "
    "El riesgo aparece cuando adaptarte al grupo hace que pierdas contacto con lo que realmente necesitas tú.",
12: "En Casa 12, gran parte de lo que te mueve ocurre de forma silenciosa. "
    "Tienes una dimensión interior muy rica que no siempre encuentra expresión directa. "
    "La soledad productiva y la contemplación son territorios donde puedes consolidarte.",
}

# ─── TEXTOS: LUNA POR SIGNO ───────────────────────────────────────────────────

LUNA_SIGNO = {
"Aries": (
    "Tu Luna en Aries reacciona antes de evaluar: el impulso emocional se activa con rapidez "
    "y necesita salida en movimiento o en acción directa. "
    "Cuando sientes que dependes demasiado de los demás, aparece irritación o necesidad de recuperar espacio propio."
    "Lo que regula es el movimiento propio; lo que desregula, la quietud forzada o la espera sin capacidad de hacer."
),
"Tauro": (
    "Tu Luna en Tauro se mueve despacio pero con profundidad. "
    "Las emociones que entran se instalan — no se sueltan con presión. "
    "La constancia del entorno y el contacto físico ayudan a estabilizarte; cuando ese suelo se mueve, "
    "tu mundo emocional tarda en reubicarse. "
    "La resistencia al cambio emocional no es obstinación: es la forma en que te proteges."
),
"Géminis": (
    "Tu Luna en Géminis procesa las emociones a través de la palabra y el pensamiento. "
    "Lo que no se nombra no se asienta bien. "
    "El estado emocional cambia con rapidez y puede pasar de un registro al otro sin aviso. "
    "La dificultad aparece cuando la movilidad mental sustituye a la profundidad: "
    "la emoción se piensa mucho pero no siempre llega a sentirse del todo."
),
"Cáncer": (
    "Tu Luna en Cáncer tiene mucha sensibilidad hacia el entorno emocional. "
    "Lo que ocurre alrededor te afecta más de lo que suele verse desde fuera. "
    "Hay necesidad de cercanía, cuidado y sensación de protección en los vínculos importantes. "
    "Cuando el entorno cercano es inestable o frío, puede aparecer confusión emocional aunque intentes sostenerte."
),
"Leo": (
    "Tu Luna en Leo necesita ser vista y reconocida para funcionar con estabilidad. "
    "Las emociones se expresan con generosidad y visibilidad. "
    "Hay sensibilidad particular hacia la frialdad del entorno: la falta de apreciación "
    "impacta directamente en el estado emocional. "
    "Cuando hay espacio para la expresión genuina y una respuesta cálida, sueles recuperar equilibrio con bastante facilidad."
),
"Virgo": (
    "Tu Luna en Virgo procesa las emociones a través del análisis y la búsqueda de orden. "
    "Sueles observar y evaluar constantemente cómo estás. "
    "Eso puede ser útil o puede convertirse en un obstáculo cuando la emoción necesita "
    "ser sentida antes de ser analizada. "
    "La claridad en el entorno cotidiano y la sensación de utilidad funcionan como suelo."
),
"Libra": (
    "Tu Luna en Libra regula su estado a través del equilibrio relacional. "
    "El conflicto en el entorno cercano impacta directamente en el estado emocional. "
    "Hay sensibilidad particular hacia la injusticia y la asimetría. "
    "El riesgo aparece cuando el equilibrio externo se busca a costa de lo que realmente necesitas tú: "
    "la armonía visible puede costar estabilidad interior."
),
"Escorpio": (
    "Tu Luna en Escorpio vive las emociones con mucha intensidad aunque no siempre las muestre. "
    "Necesitas tiempo y confianza antes de abrirte del todo. "
    "Cuando algo te afecta, suele quedarse dentro durante bastante tiempo y no te resulta fácil soltarlo rápidamente. "
    "La desconfianza o la sensación de exposición pueden hacer que te cierres incluso cuando necesitas apoyo."
),
"Sagitario": (
    "Tu Luna en Sagitario necesita movimiento, perspectiva y sentido. "
    "Cuando algo te afecta, te ayuda entender para qué sirve, hacia dónde te lleva o qué puedes hacer con ello. "
    "Si no encuentras una salida, el estado emocional puede convertirse en inquietud, impaciencia o necesidad de cambiar de escenario. "
    "El movimiento, el cambio de perspectiva y la sensación de amplitud te ayudan a recuperar estabilidad."
),
"Capricornio": (
    "Tu Luna en Capricornio contiene antes de expresar. "
    "Las emociones se procesan internamente — hay una evaluación de si es seguro mostrar "
    "el estado interior antes de hacerlo. "
    "La expresión emocional espontánea puede sentirse como vulnerabilidad. "
    "El logro y la construcción de algo duradero actúan como suelo."
),
"Acuario": (
    "Tu Luna en Acuario necesita espacio emocional y cierta distancia para procesar lo que siente. "
    "Cuando las emociones son demasiado intensas o invasivas, puedes retirarte o irte rápidamente a la cabeza para intentar entenderlas. "
    "La libertad dentro de los vínculos es importante para que puedas sentirte bien emocionalmente. "
    "Cuando sientes demasiada presión emocional, aparece necesidad de alejarte o desconectarte."
),
"Piscis": (
    "Tu Luna en Piscis tiene mucha sensibilidad hacia el entorno emocional. "
    "Puedes absorber fácilmente estados, tensiones o necesidades de otras personas sin darte cuenta al momento. "
    "Eso puede darte mucha empatía, pero también hacer difícil distinguir qué es realmente tuyo y qué pertenece al entorno. "
    "Cuando no hay límites claros o espacios de descanso, terminas saturándote con facilidad."
),
}

# ─── TEXTOS: LUNA POR CASA ────────────────────────────────────────────────────

LUNA_CASA = {
1: "En Casa 1, tus necesidades emocionales tienden a expresarse directamente a través del cuerpo y la presencia. "
   "Lo que sientes suele reflejarse rápidamente en el cuerpo, la postura o la forma de reaccionar al entorno.",
2: "En Casa 2, tu seguridad emocional suele estar conectada con la estabilidad de tus propios recursos. "
   "Las inestabilidades materiales o la sensación de no poder sostenerte generan inseguridad rápidamente.",
3: "En Casa 3, procesas las emociones a través del habla, el pensamiento y el intercambio cercano. "
   "Nombrar lo que sientes suele ayudarte a entenderlo mejor. El entorno próximo tiene peso emocional significativo.",
4: "En Casa 4, lo emocional tiene mucha relación con el hogar, la intimidad y la sensación de protección. "
   "El entorno cercano influye profundamente en cómo te sientes y en la capacidad de descansar de verdad. "
   "Cuando la base emocional o doméstica es inestable, el desgaste suele aparecer rápidamente aunque intentes seguir funcionando.",
5: "En Casa 5, tu seguridad emocional se activa a través de la expresión creativa, el juego y el amor. "
   "Necesitas que tu vida emocional tenga un componente de disfrute y de expresión auténtica.",
6: "En Casa 6, tus necesidades emocionales tienden a expresarse a través del trabajo, el servicio y los ritmos cotidianos. "
   "Tu estado interior suele reflejarse en el cuerpo y en la relación con la salud. Una rutina bien construida ayuda mucho a estabilizarte.",
7: "En Casa 7, los vínculos cercanos influyen mucho en cómo te sientes. "
   "Las relaciones importantes pueden ayudarte a estabilizarte o alterarte profundamente según cómo estén funcionando. "
   "Cuando no hay suficiente apoyo interno, puede aparecer tendencia a buscar demasiada estabilidad emocional en la otra persona.",
8: "En Casa 8, las emociones suelen vivirse con intensidad y profundidad aunque no siempre se expresen fácilmente. "
   "Los vínculos importantes, las pérdidas o las situaciones límite tienden a afectarte mucho más de lo que parece desde fuera. "
   "Cuando algo te toca emocionalmente, no te resulta fácil quedarte en la superficie.",
9: "En Casa 9, te ayuda sentir que lo que vives tiene sentido o dirección. "
   "Aprender, viajar, estudiar o abrir nuevas perspectivas suele ayudarte a recuperar estabilidad emocional. "
   "Cuando todo se vuelve demasiado pequeño o repetitivo, aparece inquietud con facilidad.",
10: "En Casa 10, tu estado emocional suele estar conectado con el espacio vocacional y el reconocimiento público. "
    "Los logros y los reveses profesionales afectan mucho a cómo te sientes. "
    "La visibilidad pública puede ser tanto un apoyo como una fuente de exposición.",
11: "En Casa 11, tu seguridad emocional se activa a través de la pertenencia a grupos y la conexión con proyectos colectivos. "
    "Las amistades y redes de apoyo influyen mucho en tu equilibrio emocional.",
12: "En Casa 12, muchas emociones se viven de forma silenciosa o difícil de explicar en el momento. "
    "Necesitas espacios de soledad, descanso o desconexión para entender realmente cómo estás. "
    "Cuando acumulas demasiado sin parar, el cansancio emocional puede aparecer de forma difusa y difícil de identificar. "
    "La creatividad, el silencio o ciertos momentos de aislamiento suelen ayudarte a recuperar equilibrio.",
}

# ─── TEXTOS: ASCENDENTE POR SIGNO ────────────────────────────────────────────

ASC_SIGNO = {
"Aries": (
    "Tu Ascendente en Aries hace que te muestres al mundo de forma directa, impulsiva y con energía. "
    "Tiendes a actuar rápido y a tomar la iniciativa con facilidad. "
    "Puede haber una distancia entre esta primera impresión activa y la complejidad interior que el resto "
    "de tu carta describe."
),
"Tauro": (
    "Tu Ascendente en Tauro hace que los demás te vean como una persona estable, tranquila y de movimientos medidos. "
    "Sueles proyectar calma y una presencia física consistente. "
    "El entorno suele sentirte como alguien que no se apresura y que necesita su propio ritmo."
),
"Géminis": (
    "Tu Ascendente en Géminis hace que te muestres al mundo como una persona ágil, curiosa y comunicativa. "
    "Entras al entorno con preguntas y conexiones. "
    "Puede haber una brecha entre esta ligereza aparente y la profundidad de lo que realmente sientes o piensas."
),
"Cáncer": (
    "Tu Ascendente en Cáncer hace que te presentes ante los demás de forma receptiva, empática y algo protectora. "
    "Tienes una sensibilidad de fondo que observa el entorno emocional antes de abrirte. "
    "Tu primera impresión puede ser de suavidad o de reserva, según el contexto."
),
"Leo": (
    "Tu Ascendente en Leo hace que te muestres al mundo con calidez, presencia y una orientación natural "
    "a ocupar el espacio con seguridad. Entras al entorno con una energía que otros notan. "
    "La necesidad de expresarte y ocupar espacio suele percibirse desde el primer contacto."
),
"Virgo": (
    "Tu Ascendente en Virgo hace que los demás te vean como una persona analítica, discreta y orientada al detalle. "
    "Observa y evalúa antes de participar. "
    "Puede haber una distancia inicial que no refleja la calidez que aparece cuando coges confianza."
),
"Libra": (
    "Tu Ascendente en Libra hace que te muestres al mundo de forma armoniosa, diplomática y socialmente hábil. "
    "La facilidad natural para el primer contacto y para entender rápidamente cómo relacionarte con cada persona. "
    "La necesidad de equilibrio puede generar cierta indecisión visible desde fuera."
),
"Escorpio": (
    "Tu Ascendente en Escorpio hace que los demás te perciban como una persona reservada, intensa y difícil de leer al principio. "
    "Sueles observar mucho antes de mostrarte con naturalidad y no tiendes a confiar rápidamente. "
    "La primera impresión puede ser seria o distante, incluso cuando por dentro estás muy atento a todo lo que ocurre."
),
"Sagitario": (
    "Tu Ascendente en Sagitario hace que te muestres al mundo con entusiasmo, directamente y con apertura. "
    "Tienes una energía expansiva que hace fácil el primer contacto. "
    "Sueles entrar al entorno con convicción y con capacidad de inspirar."
),
"Capricornio": (
    "Tu Ascendente en Capricornio hace que los demás te vean como una persona seria, contenida y competente. "
    "Tu primera impresión puede ser de distancia o de autoridad. "
    "Con el tiempo, la solidez de tu presencia suele generar confianza."
),
"Acuario": (
    "Tu Ascendente en Acuario hace que los demás te perciban como alguien independiente, algo distante y difícil de encajar en lo esperado. "
    "Sueles observar primero y participar cuando sientes suficiente espacio o libertad. "
    "La primera impresión puede parecer fría o racional, aunque internamente haya mucha más sensibilidad de la que se muestra al principio."
),
"Piscis": (
    "Tu Ascendente en Piscis hace que los demás te perciban como una persona sensible, adaptable y difícil de definir rápidamente. "
    "Sueles captar el ambiente antes de decidir cómo mostrarte o actuar. "
    "La empatía y la capacidad de conexión pueden ser muy altas, pero cuando hay demasiada presión externa puedes acabar adaptándote más de la cuenta."
),
}

# ─── TEXTOS: ASPECTOS CLAVE ──────────────────────────────────────────────────

# Clave: (planeta1, planeta2, tipo_aspecto)  — orden sin importar
ASPECTOS_CLAVE = {
("Luna","Saturno","□"): (
    "La cuadratura Luna-Saturno marca una tensión entre lo que necesitas sentir y lo que te permites mostrar. "
    "Puede aparecer como contención emocional, dificultad para pedir apoyo o tendencia a exigirte estar bien antes de recibir cuidado. "
    "Desde fuera quizá pareces más fuerte de lo que realmente estás. "
    "La clave está en reconocer cuándo la exigencia interna te está costando más que la situación real."
),
("Luna","Saturno","☍"): (
    "La oposición Luna-Saturno suele vivirse como una alternancia entre necesidad de apoyo y retirada. "
    "Puedes querer cercanía, pero al mismo tiempo protegerte anticipando distancia, juicio o falta de respuesta. "
    "El trabajo con este aspecto no es volverte autosuficiente, sino aprender a pedir sin sentir que pierdes autoridad o control."
),
("Luna","Saturno","="): (
    "La conjunción Luna-Saturno une emoción y contención. "
    "Antes de mostrar lo que sientes, suele aparecer una evaluación interna: si conviene, si es seguro, si será recibido. "
    "Esto puede darte madurez emocional, pero también hacer que reprimas demasiado pronto necesidades legítimas."
),

("Venus","Neptuno","□"): (
    "La cuadratura Venus-Neptuno puede hacer que idealices el vínculo antes de verlo con claridad. "
    "Puedes percibir posibilidades, belleza o profundidad donde todavía no hay suficiente realidad concreta. "
    "El riesgo aparece cuando sostienes una imagen de la relación más que la relación tal como es. "
    "Te ayuda mirar los hechos sin perder sensibilidad."
),
("Venus","Neptuno","☍"): (
    "La oposición Venus-Neptuno marca tensión entre el vínculo real y el vínculo imaginado. "
    "Puedes sentirte atraído por relaciones que prometen mucho en el plano emocional o simbólico, pero que después no sostienen lo cotidiano. "
    "La clave está en no confundir intensidad, inspiración o compasión con disponibilidad real."
),
("Venus","Neptuno","="): (
    "La conjunción Venus-Neptuno aumenta la sensibilidad afectiva y la capacidad de entrega. "
    "Puedes vivir los vínculos con mucha apertura, pero también confundirte cuando no hay límites claros. "
    "Te ayuda distinguir entre lo que te conmueve y lo que realmente puede sostenerse en una relación concreta."
),

("Luna","Marte","△"): (
    "El trígono Luna-Marte facilita que lo que sientes encuentre salida en la acción. "
    "Cuando algo te mueve de verdad, puedes responder con rapidez y convertir el estado emocional en movimiento útil. "
    "Este aspecto puede ser un recurso de regulación: moverte, actuar o hacer algo concreto antes de quedarte dentro de la emoción."
),
("Luna","Marte","□"): (
    "La cuadratura Luna-Marte puede generar reacciones rápidas cuando algo te afecta. "
    "La emoción y el impulso se activan casi al mismo tiempo, y a veces actúas antes de tener claro qué necesitas. "
    "Te ayuda separar unos segundos la reacción de la acción para no convertir una emoción pasajera en un conflicto mayor."
),

("Marte","Saturno","⚻"): (
    "El quincuncio Marte-Saturno señala un ajuste constante entre impulso y límite. "
    "Puedes sentir ganas de actuar y, al mismo tiempo, encontrarte con condiciones que obligan a frenar, ordenar o esperar. "
    "No es un bloqueo simple: es una tensión que pide calibrar cuánto empujar y cuándo sostener. "
    "Cuando se trabaja bien, permite pasar del impulso rápido a una acción más estable y precisa."
),
("Marte","Saturno","□"): (
    "La cuadratura Marte-Saturno marca fricción entre acción y contención. "
    "Puedes sentir que avanzas con el freno puesto, o que tu impulso choca con obligaciones, límites o miedo a equivocarte. "
    "La dificultad no está en tener poca fuerza, sino en encontrar una forma de usarla sin agotarte ni bloquearte."
),

("Mercurio","Júpiter","△"): (
    "El trígono Mercurio-Júpiter facilita conectar detalles con visión amplia. "
    "Puedes comprender el sentido general de una situación y explicarlo de forma que otras personas lo entiendan. "
    "Es un buen aspecto para aprender, enseñar, escribir o transmitir ideas. "
    "El riesgo aparece cuando ves tan rápido el conjunto que dejas sin ordenar algunos detalles importantes."
),

("Venus","Urano","△"): (
    "El trígono Venus-Urano da una forma relacional independiente y poco convencional. "
    "Sueles necesitar libertad dentro de los vínculos y te atraen relaciones donde haya autenticidad, diferencia o espacio propio. "
    "Lo demasiado previsible puede apagarte, pero lo inestable tampoco siempre te sostiene. "
    "La clave está en diferenciar libertad real de distancia emocional."
),

("Saturno","Quirón","△"): (
    "El trígono Saturno-Quirón indica que la estructura puede ayudarte a sostener zonas sensibles de tu vida. "
    "Cuando tienes ritmo, límites y responsabilidades claras, manejas mejor aquello que normalmente te hace sentir inseguridad o exposición. "
    "No se trata de endurecerte, sino de crear un contenedor suficientemente estable para no quedarte en la vulnerabilidad."
),

("Neptuno","Lilith","△"): (
    "El trígono Neptuno-Lilith puede dar acceso a partes muy intuitivas, creativas o difíciles de nombrar. "
    "Lo que no encaja fácilmente en la norma puede encontrar salida a través de imágenes, arte, sensibilidad o percepción sutil. "
    "El riesgo está en dejarlo demasiado difuso. "
    "Te ayuda darle una forma concreta para que no se quede solo como sensación."
),

("Urano","Lilith","□"): (
    "La cuadratura Urano-Lilith puede activar reacciones bruscas cuando algo contenido durante demasiado tiempo ya no puede seguir oculto. "
    "Puede aparecer como necesidad repentina de romper, cortar, decir algo o salir de una situación. "
    "No siempre llega de forma gradual: a veces se manifiesta cuando la tensión ya lleva tiempo acumulándose. "
    "Te ayuda detectar antes qué estás tolerando en silencio."
),

("Sol","Júpiter","□"): (
    "La cuadratura Sol-Júpiter puede llevarte a ampliar más de lo que puedes sostener. "
    "Hay entusiasmo, visión y capacidad de crecimiento, pero también tendencia a asumir demasiado o confiar en que podrás con todo. "
    "El límite no viene a apagar la expansión, sino a darle una forma que no te desgaste."
),

("Sol","Neptuno","△"): (
    "El trígono Sol-Neptuno aporta sensibilidad, imaginación y capacidad para percibir matices que no son evidentes. "
    "Puede favorecer lo creativo, lo contemplativo o el acompañamiento de otras personas. "
    "El riesgo aparece si esa apertura no se traduce en algo concreto. "
    "Te ayuda dar forma práctica a lo que percibes."
),

("Sol","Plutón","☍"): (
    "La oposición Sol-Plutón marca una tensión intensa entre afirmarte y atravesar procesos que no puedes controlar del todo. "
    "Puede haber momentos en los que la vida te obliga a revisar quién eres, qué deseas y qué poder estás entregando o reteniendo. "
    "No es una tensión ligera: suele pedir honestidad, límites y capacidad de sostener cambios importantes sin destruirte por dentro."
),

("Luna","Quirón","⚻"): (
    "El quincuncio Luna-Quirón señala un ajuste delicado entre lo que necesitas emocionalmente y una zona sensible que se activa con facilidad. "
    "Puedes sentir que lo que te calma en un momento no sirve en otro, o que ciertas situaciones despiertan una vulnerabilidad difícil de explicar. "
    "La clave está en observar qué activa esa sensibilidad antes de intentar resolverla demasiado rápido."
),

("Venus","Plutón","□"): (
    "La cuadratura Venus-Plutón intensifica la forma de vincularte. "
    "Cuando una relación importa, puede remover miedo a perder, necesidad de asegurar el vínculo o dificultad para soltar el control. "
    "No habla de relaciones ligeras: habla de vínculos que tocan capas profundas de deseo, apego y poder personal. "
    "Te ayuda reconocer cuándo la intensidad está ocupando más espacio que la relación real."
),

("Plutón","Nodo Sur","⚻"): (
    "El quincuncio Plutón-Nodo Sur señala una tensión entre patrones conocidos y procesos intensos que piden cambio. "
    "Puedes permanecer demasiado tiempo en situaciones densas porque, aunque desgasten, resultan familiares. "
    "La salida no siempre es romper de golpe; a veces empieza por reconocer cuándo algo ya no transforma, sino que absorbe demasiada energía."
),

("Sol","Marte","="): (
    "La conjunción Sol-Marte une identidad y acción. "
    "Cuando tienes una dirección clara, puedes actuar con rapidez, iniciativa y mucha fuerza disponible. "
    "Cuando no hay salida concreta, esa fuerza puede convertirse en impaciencia, tensión o necesidad de intervenir. "
    "Este aspecto pide objetivos claros para que la acción no se transforme en desgaste."
),
}
# ─── FUNCIONES DE CÁLCULO (reutilizadas de carta_astral.py) ─────────────────

def geocodificar(ciudad):
    geolocator = Nominatim(user_agent="carta_natal_completa_ai")
    location = geolocator.geocode(ciudad, language="es")
    if not location:
        raise ValueError(f"No se pudo encontrar: {ciudad}")
    return location.latitude, location.longitude

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
    h = dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0
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

def nivel_grado_critico(grado):
    """
    Detecta grados finales de signo.
    - 29°00' a 29°59': grado anarético
    - 28°00' a 28°59': grado previo al anarético
    """
    if grado >= 29.0:
        return "anaretico"
    elif grado >= 28.0:
        return "pre_anaretico"
    return ""


def detectar_grados_criticos(carta):
    planetas = carta["planetas"]
    puntos = []

    for nombre, p in planetas.items():
        nivel = nivel_grado_critico(p.get("grado", 0))
        if nivel:
            puntos.append({
                "tipo": "planeta",
                "nombre": nombre,
                "signo": p["signo"],
                "grado": p["grado"],
                "casa": p.get("casa", ""),
                "nivel": nivel,
            })

    asc = carta["asc"]
    nivel_asc = nivel_grado_critico(asc.get("grado", 0))
    if nivel_asc:
        puntos.append({
            "tipo": "eje",
            "nombre": "Ascendente",
            "signo": asc["signo"],
            "grado": asc["grado"],
            "casa": "",
            "nivel": nivel_asc,
        })

        signo_dc = SIGNOS[(SIGNOS.index(asc["signo"]) + 6) % 12]
        puntos.append({
            "tipo": "eje",
            "nombre": "Descendente",
            "signo": signo_dc,
            "grado": asc["grado"],
            "casa": "",
            "nivel": nivel_asc,
        })

    mc = carta["mc"]
    nivel_mc = nivel_grado_critico(mc.get("grado", 0))
    if nivel_mc:
        puntos.append({
            "tipo": "eje",
            "nombre": "Medio Cielo",
            "signo": mc["signo"],
            "grado": mc["grado"],
            "casa": "",
            "nivel": nivel_mc,
        })

        signo_ic = SIGNOS[(SIGNOS.index(mc["signo"]) + 6) % 12]
        puntos.append({
            "tipo": "eje",
            "nombre": "Fondo del Cielo",
            "signo": signo_ic,
            "grado": mc["grado"],
            "casa": "",
            "nivel": nivel_mc,
        })

    return puntos

def _chiron_kepler(jd):
    jd_peri, period, e, peri_lon = 2450128.5, 18412.3, 0.383, 188.76
    M = math.radians(((jd - jd_peri) / period * 360.0) % 360.0)
    E = M
    for _ in range(50):
        dE = (M - E + e*math.sin(E)) / (1.0 - e*math.cos(E))
        E += dE
        if abs(dE) < 1e-10:
            break
    f = 2.0 * math.atan(math.sqrt((1+e)/(1-e)) * math.tan(E/2.0))
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
        planetas[nombre] = {"simbolo":simbolo,"lon":pos[0],"signo":signo,"grado":grado,"retrogrado":pos[3]<0}

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


    # Lilith
    pos_li, _ = swe.calc_ut(jd, LILITH_ID, swe.FLG_SPEED)
    signo_li, grado_li = grados_a_signo(pos_li[0])
    planetas["Lilith"] = {"simbolo":"⚸","lon":pos_li[0],"signo":signo_li,"grado":grado_li,"retrogrado":False}

    # Nodos (True Node)
    pos_nn, _ = swe.calc_ut(jd, swe.TRUE_NODE, swe.FLG_SPEED)
    signo_nn, grado_nn = grados_a_signo(pos_nn[0])
    lon_ns = (pos_nn[0]+180) % 360
    signo_ns, grado_ns = grados_a_signo(lon_ns)
    planetas["Nodo Norte"] = {"simbolo":"☊","lon":pos_nn[0],"signo":signo_nn,"grado":grado_nn,"retrogrado":False}
    planetas["Nodo Sur"]   = {"simbolo":"☋","lon":lon_ns,"signo":signo_ns,"grado":grado_ns,"retrogrado":False}

    # Casas Placidus
    cuspides, ascmc = swe.houses(jd, lat, lon, b'P')
    asc_lon, mc_lon = ascmc[0], ascmc[1]
    signo_asc, grado_asc = grados_a_signo(asc_lon)
    signo_mc,  grado_mc  = grados_a_signo(mc_lon)

    def casa_de(p_lon):
        for i in range(12):
            c_ini = cuspides[i]
            c_fin = cuspides[(i+1)%12]
            if c_ini <= c_fin:
                if c_ini <= p_lon < c_fin: return i+1
            else:
                if p_lon >= c_ini or p_lon < c_fin: return i+1
        return 12

    for nombre in planetas:
        planetas[nombre]["casa"] = casa_de(planetas[nombre]["lon"])

    # Signos interceptados: signos cuyo tramo completo (30°) cae dentro de una casa
    # (ninguna cúspide aterriza en ese signo)
    interceptados = {}   # {signo: casa}
    duplicados    = {}   # {signo: [casa1, casa2]} — signos que aparecen en dos cúspides
    for idx_signo in range(12):
        lon_ini_signo = idx_signo * 30.0
        lon_fin_signo = lon_ini_signo + 30.0
        cusps_en_signo = []
        for i, c in enumerate(cuspides):
            c_norm = c % 360
            if lon_ini_signo <= c_norm < lon_fin_signo:
                cusps_en_signo.append(i+1)
        nombre_signo = SIGNOS[idx_signo]
        if len(cusps_en_signo) == 0:
            interceptados[nombre_signo] = casa_de(lon_ini_signo + 0.001)
        elif len(cusps_en_signo) >= 2:
            duplicados[nombre_signo] = cusps_en_signo

    # Marcar si cada planeta está en signo interceptado
    for nombre in planetas:
        signo_p = planetas[nombre]["signo"]
        planetas[nombre]["interceptado"] = signo_p in interceptados

    return {
        "planetas":      planetas,
        "cuspides":      list(cuspides),
        "asc":           {"lon":asc_lon,"signo":signo_asc,"grado":grado_asc},
        "mc":            {"lon":mc_lon, "signo":signo_mc, "grado":grado_mc},
        "interceptados": interceptados,   # {signo: casa}
        "duplicados":    duplicados,      # {signo: [casas]}
        "jd":            jd
    }

def calcular_aspectos(planetas):
    ASPECTOS = {
        0:   ("Conjunción", "=", 10),
        60:  ("Sextil", "✶", 6),
        90:  ("Cuadratura", "□", 8),
        120: ("Trígono", "△", 8),
        150: ("Quincuncio", "⚻", 4),
        180: ("Oposición", "☍", 8),
    }

    nombres = list(planetas.keys())
    aspectos = []

    for i in range(len(nombres)):
        for j in range(i + 1, len(nombres)):
            n1, n2 = nombres[i], nombres[j]

            diff = abs(planetas[n1]["lon"] - planetas[n2]["lon"])
            if diff > 180:
                diff = 360 - diff

            for angulo, (nombre_asp, simbolo_asp, orbe) in ASPECTOS.items():

                orbe_real = orbe

                # Oposición ampliada a 10° si participa Sol o Luna
                if (
                    simbolo_asp == "☍"
                    and (n1 in ("Sol", "Luna") or n2 in ("Sol", "Luna"))
                ):
                    orbe_real = 10

                if abs(diff - angulo) <= orbe_real:
                    orbe_val = round(abs(diff - angulo), 2)

                    aspectos.append({
                        "p1": n1,
                        "p2": n2,
                        "nombre": nombre_asp,
                        "simbolo": simbolo_asp,
                        "orbe": orbe_val,
                        "relevancia": "exacto" if orbe_val <= 1.0 else "estructural",
                    })
                    break

    return sorted(aspectos, key=lambda x: x["orbe"])

# ─── RUEDA ASTROLÓGICA ────────────────────────────────────────────────────────

def dibujar_rueda(carta, nombre_persona, archivo_salida):
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
        "□":"#CC2200",
        "☍":"#CC2200",
        "△":"#1A5FA8",
        "✶":"#1A5FA8",
        "⚻":"#2E7D32",
        "=":"#7B2D8B"
    }

    _ASP_LW = {
        "□":1.0,
        "☍":1.0,
        "△":0.9,
        "✶":0.8,
        "⚻":0.7,
        "=":1.2
    }

    _ASP_ALPHA = {
        "□":0.55,
        "☍":0.55,
        "△":0.50,
        "✶":0.45,
        "⚻":0.35,
        "=":0.75
    }

    R_ASP = R_CASA_IN - 0.02

    for asp in calcular_aspectos(carta["planetas"]):
        if asp["orbe"] > 8.5:
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
            [math.cos(a1) * R_ASP, math.cos(a2) * R_ASP],
            [math.sin(a1) * R_ASP, math.sin(a2) * R_ASP],
            color=_ASP_COLORES[sim],
            linewidth=_ASP_LW[sim],
            alpha=_ASP_ALPHA[sim],
            linestyle="solid",
            zorder=2,
        )

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
            e = ELEMENTO_SIGNO.get(planetas[nombre]["signo"],"")
            if e: conteo[e] += peso
    # Ascendente: 2 puntos (solo si se conoce la hora)
    if hora_conocida:
        e_asc = ELEMENTO_SIGNO.get(asc_signo,"")
        if e_asc: conteo[e_asc] += 2
        # +1 al elemento del regente del Ascendente
        regente = _REGENTE_ASC.get(asc_signo,"")
        if regente and regente in planetas:
            e_reg = ELEMENTO_SIGNO.get(planetas[regente]["signo"],"")
            if e_reg: conteo[e_reg] += 1
    return conteo

def analizar_modalidades(planetas):
    conteo = {"Cardinal":0,"Fijo":0,"Mutable":0}
    for nombre in ["Sol","Luna","Mercurio","Venus","Marte","Júpiter","Saturno"]:
        if nombre in planetas:
            m = MODALIDAD_SIGNO.get(planetas[nombre]["signo"],"")
            if m: conteo[m] += 1
    return conteo

def _desc_elemento(elem):
    return {
        "Fuego": "vitalidad, iniciativa, necesidad de sentido y movimiento hacia la acción",
        "Agua":  "profundidad emocional, capacidad de resonancia, sensibilidad abierta",
        "Aire":  "desapego, análisis, pensamiento relacional y capacidad de perspectiva",
        "Tierra":"arraigo en lo concreto, estructura material, ritmo sostenido y contacto con el cuerpo"
    }.get(elem,"")

MC_SIGNO = {
"Aries": (
    "la iniciativa directa, el liderazgo propio y la capacidad de iniciar. "
    "Tu presencia profesional tiende a percibirse como activa e independiente."
),

"Tauro": (
    "la constancia, la paciencia y la construcción de algo sólido con el tiempo. "
    "Tu presencia pública suele percibirse como estable y fiable."
),

"Géminis": (
    "la comunicación, el aprendizaje y la capacidad de moverte entre distintos temas o personas. "
    "Funcionas bien en entornos donde la palabra, el intercambio y la circulación de ideas son importantes."
),

"Cáncer": (
    "el cuidado, la sensibilidad hacia las necesidades del entorno y la capacidad de sostener procesos humanos. "
    "Tu presencia profesional suele percibirse como cercana y protectora."
),

"Leo": (
    "la creatividad, la expresión personal y la capacidad de hacerte visible con naturalidad. "
    "Tu figura pública tiende a destacar cuando puedes mostrar algo auténticamente propio."
),

"Virgo": (
    "el análisis, la mejora continua y el trabajo bien hecho. "
    "Funcionas bien donde se necesita precisión, atención al detalle y capacidad de organización."
),

"Libra": (
    "el equilibrio, la diplomacia y la capacidad de facilitar acuerdos entre personas o posiciones distintas. "
    "Tu presencia pública suele percibirse como armoniosa y cuidadosa en el trato."
),

"Escorpio": (
    "la capacidad de trabajar con situaciones complejas, tensas o delicadas sin apartar la mirada. "
    "Tu presencia pública puede percibirse como intensa, reservada y difícil de ignorar."
),

"Sagitario": (
    "la transmisión de visión y perspectiva, la amplitud de mirada y el conocimiento. "
    "Funcionas bien en entornos de enseñanza, expansión o exploración."
),

"Capricornio": (
    "la responsabilidad, la estructura y la construcción a largo plazo. "
    "Tu presencia profesional se fortalece con el tiempo y la experiencia."
),

"Acuario": (
    "la independencia de criterio, la capacidad de pensar diferente y la apertura a nuevas formas de hacer las cosas. "
    "Tu presencia pública suele destacar por salirse de lo esperado."
),

"Piscis": (
    "la creatividad, la sensibilidad hacia el entorno y la capacidad de adaptarte a distintos contextos humanos. "
    "Funcionas bien en espacios donde hace falta imaginación, escucha o flexibilidad."
),
}
def texto_vision_general(carta, conteo_elem, conteo_modal):
    planetas = carta["planetas"]
    asc_signo = carta["asc"]["signo"]
    mc_signo  = carta["mc"]["signo"]

    def _fpt(v): return str(int(v)) if v == int(v) else str(v)

    total = sum(conteo_elem.values())
    ordenado = sorted(conteo_elem.items(), key=lambda x:-x[1])
    alto = [e for e,n in ordenado if n >= 5.5]
    bajo = [e for e,n in ordenado if n <= 2.0]

    texto = (
        f"Tu carta muestra la siguiente distribución de elementos: "
        f"Fuego {_fpt(conteo_elem['Fuego'])}, Tierra {_fpt(conteo_elem['Tierra'])}, "
        f"Aire {_fpt(conteo_elem['Aire'])}, Agua {_fpt(conteo_elem['Agua'])}. "
    )

    if alto:
        desc = " y ".join([f"{e} ({_desc_elemento(e)})" for e in alto])
        texto += (
            f"{desc}: ahí está el peso de tu carta. "
            f"Es el registro desde el que tu energía se activa con más fluidez y sin esfuerzo consciente. "
        )

    if bajo:
        desc = " y ".join([f"{e} ({_desc_elemento(e)})" for e in bajo])
        texto += (
            f"{desc} está poco representado en tu carta. "
            f"Ese territorio puede pedirte un esfuerzo consciente, especialmente cuando la presión sube. "
        )

    # Modalidades
    modal_max = max(conteo_modal, key=conteo_modal.get)
    if conteo_modal[modal_max] >= 4:
        desc_modal = {
            "Mutable": (
                "La mayoría de tus planetas están en signos mutables: hay facilidad para adaptarte, cambiar y responder a lo que ocurre alrededor. "
                "Sueles moverte bien cuando las situaciones evolucionan o requieren flexibilidad. "
                "La dificultad aparece cuando todo cambia al mismo tiempo y cuesta mantener una dirección estable durante suficiente tiempo."
            ),
            "Cardinal": (
                "La mayoría de tus planetas están en signos cardinales: hay tendencia natural a iniciar, activar y poner cosas en marcha. "
                "Te resulta más fácil empezar que esperar pasivamente. "
                "La dificultad aparece cuando el entusiasmo inicial baja y toca sostener procesos más lentos o repetitivos."
            ),
            "Fijo": (
                "La mayoría de tus planetas están en signos fijos: hay capacidad de persistencia, estabilidad y continuidad. "
                "Cuando algo tiene sentido para ti, puedes sostenerlo durante mucho tiempo incluso en condiciones difíciles. "
                "La dificultad aparece cuando hace falta cambiar de dirección y una parte de ti sigue intentando mantener lo conocido."
            ),
        }
        texto += desc_modal.get(modal_max, "")

    # MC
    mc_desc = MC_SIGNO.get(mc_signo, "las cualidades de ese signo en el mundo externo")
    texto += f" Tu Medio Cielo en {mc_signo}: {mc_desc[0].upper() + mc_desc[1:]}"

    return texto

# ─── SECCIÓN: EJES PRINCIPALES ───────────────────────────────────────────────

_REGENTE_SIGNO_TONO = {
    "Aries":       "directa, rápida y orientada a la acción",
    "Tauro":       "estable, tranquila y de ritmo constante",
    "Géminis":     "ágil, curiosa y comunicativa",
    "Cáncer":      "receptiva, protectora y muy sensible al ambiente emocional",
    "Leo":         "cálida, expresiva y con necesidad de hacerse visible",
    "Virgo":       "observadora, discreta y orientada al detalle",
    "Libra":       "armoniosa, diplomática y cuidadosa en el trato",
    "Escorpio":    "reservada, intensa y difícil de leer rápidamente",
    "Sagitario":   "expansiva, entusiasta y orientada a ampliar horizontes",
    "Capricornio": "seria, constante y orientada a construir a largo plazo",
    "Acuario":     "independiente, analítica y poco convencional",
    "Piscis":      "sensible, adaptable y muy influida por el entorno",
}

_REGENTE_CASA_CONTEXTO = {
    1:  "la forma en que te muestras y entras en contacto con el entorno",
    2:  "los recursos, el valor propio y la capacidad de sostenerte por tus propios medios",
    3:  "la comunicación, el aprendizaje y el intercambio cercano",
    4:  "el hogar, la intimidad y la necesidad de una base emocional estable",
    5:  "la creatividad, la expresión personal y la capacidad de disfrutar",
    6:  "el trabajo cotidiano, los hábitos y la relación con el cuerpo",
    7:  "las relaciones importantes, las asociaciones y el vínculo con la otra persona",
    8:  "los vínculos intensos, las pérdidas y las situaciones difíciles de controlar",
    9:  "el aprendizaje, la búsqueda de perspectiva y la necesidad de ampliar horizontes",
    10: "la vocación, la responsabilidad y el espacio público",
    11: "las amistades, los grupos y los proyectos compartidos",
    12: "la vida interior, la necesidad de retiro y lo que cuesta mostrar directamente",
}

def texto_ejes_principales(carta):
    planetas = carta["planetas"]
    asc      = carta["asc"]
    mc       = carta["mc"]

    sol   = planetas.get("Sol",{})
    luna  = planetas.get("Luna",{})

    s_sol_signo = SOL_SIGNO.get(sol.get("signo",""),"")
    s_sol_casa  = SOL_CASA.get(sol.get("casa",0),"")
    s_luna_signo= LUNA_SIGNO.get(luna.get("signo",""),"")
    s_luna_casa = LUNA_CASA.get(luna.get("casa",0),"")
    s_asc       = ASC_SIGNO.get(asc.get("signo",""),"")

    # Regente del Ascendente
    regentes = {
        "Aries":"Marte","Tauro":"Venus","Géminis":"Mercurio","Cáncer":"Luna",
        "Leo":"Sol","Virgo":"Mercurio","Libra":"Venus","Escorpio":"Plutón",
        "Sagitario":"Júpiter","Capricornio":"Saturno","Acuario":"Urano","Piscis":"Neptuno"
    }
    regente = regentes.get(asc.get("signo",""),"")

    info_regente = ""
    if regente and regente in planetas:
        r = planetas[regente]
        tono = _REGENTE_SIGNO_TONO.get(r["signo"], "particular")
        contexto = _REGENTE_CASA_CONTEXTO.get(r["casa"], "tu vida")

        ARTICULOS_PLANETAS = {
            "Sol": "el Sol",
            "Luna": "la Luna",
            "Marte": "Marte",
            "Venus": "Venus",
            "Mercurio": "Mercurio",
            "Júpiter": "Júpiter",
            "Saturno": "Saturno",
            "Urano": "Urano",
            "Neptuno": "Neptuno",
            "Plutón": "Plutón",
        }

        regente_txt = ARTICULOS_PLANETAS.get(regente, regente)

        info_regente = (
            f" Su regente es {regente_txt}, en {r['signo']} y Casa {r['casa']}. "
            f"El Ascendente toma el tono de {r['signo']}: {tono}. "
            f"Esa energía opera principalmente desde {contexto}."
        )

    texto = {
        "sol": f"{s_sol_signo} {s_sol_casa}",
        "luna": f"{s_luna_signo} {s_luna_casa}",
        "asc": s_asc + info_regente,
    }
    return texto

def texto_grados_criticos(carta):
    puntos = detectar_grados_criticos(carta)

    if not puntos:
        return ""

    def fmt(p):
        casa = f", Casa {p['casa']}" if p.get("casa") else ""
        return f"{p['nombre']} en {p['signo']} {grado_a_dms(p['grado'])}{casa}"

    def texto_punto(p):
        nombre = p["nombre"]
        signo = p["signo"]
        casa = p.get("casa", "")
        nivel = p["nivel"]

        intensidad = (
            "en grado anarético"
            if nivel == "anaretico"
            else "en grado previo al anarético"
        )

        base = (
            f"{nombre} en {signo} {grado_a_dms(p['grado'])}"
            f"{f', Casa {casa}' if casa else ''} aparece {intensidad}. "
        )

        textos = {
            "Ascendente": (
            base +
                f"Esto hace que la forma en que entras en la vida y respondes al entorno se viva con mucha intensidad. "
                f"Puedes sentir que necesitas adaptarte rápido, entender qué ocurre y encontrar tu lugar constantemente. "
                f"A veces puede haber sensación de no terminar de encajar en una única forma de ser, como si siempre hubiera algo en movimiento dentro de ti. "
                f"Tu cuerpo y tu percepción captan muy rápido el ambiente, y por eso necesitas pausa antes de reaccionar automáticamente."
            ),

            "Descendente": (
                base +
                f"Las relaciones tienen mucho peso en tu vida y rara vez se viven de forma superficial o neutra. "
                f"Los vínculos pueden mostrarte con mucha claridad dónde hay dependencia, necesidad de aprobación o miedo a perder libertad. "
                f"Algunas personas llegan a tu vida como verdaderos puntos de cambio o crecimiento. "
                f"El aprendizaje está en no perderte dentro de la relación y construir vínculos donde también puedas sostenerte a ti."
            ),
 
            "Medio Cielo": (
                base +
                f"La relación con tu dirección profesional y con el lugar que ocupas en el mundo se vive con mucha intensidad. "
                f"Puede haber una sensación de exigencia interna respecto a lo que vienes a construir o aportar. "
                f"No suele bastar con funcionar hacia fuera: necesitas sentir que lo que haces tiene sentido real para ti. "
                f"Cuando esa coherencia falta, el cansancio o la presión pueden sentirse muy profundos."
            ),

            "Fondo del Cielo": (
                base +
                f"La sensación de hogar, raíz y seguridad interna no suele construirse de forma simple. "
                f"Puede haber procesos largos de búsqueda de estabilidad emocional o de sensación de pertenencia. "
                f"El descanso real no depende solo del espacio físico, sino de sentir que existe un lugar interno donde puedas bajar la guardia. "
                f"Cuando esa base falla, el desorden emocional puede sentirse muy profundo."
            ),

            "Sol": (
                base +
                f"Puede haber una sensación constante de que no basta con vivir en automático. "
                f"Algo dentro de ti pide más coherencia, más verdad y una forma más consciente de ocupar tu lugar en la vida. "
                f"A veces esto puede sentirse como presión interna o autoexigencia, especialmente cuando sigues sosteniendo formas de vivir que ya no encajan contigo. "
                f"El aprendizaje está en dejar de empujarte constantemente y empezar a construir desde más claridad y menos lucha."
            ),

            "Luna": (
                base +
                f"Tu mundo emocional se vive con mucha intensidad. "
                f"Las necesidades de cuidado, descanso, seguridad o pertenencia no suelen poder ignorarse durante mucho tiempo. "
                f"Puede haber emociones acumuladas o formas antiguas de protegerte que siguen activándose automáticamente. "
                f"El aprendizaje está en aprender a cuidarte sin repetir siempre los mismos mecanismos de defensa."
            ),

            "Mercurio": (
                base +
                f"La mente puede funcionar con mucha intensidad y actividad interna. "
                f"Puede haber necesidad de entender, analizar, nombrar o anticipar lo que ocurre antes de poder relajarte. "
                f"Pensar puede convertirse en una gran herramienta, pero también en una fuente de sobrecarga cuando intentas resolverlo todo desde la cabeza. "
                f"Necesitas espacios donde no haga falta entenderlo todo inmediatamente."
            ), 

            "Venus": (
                base +
                f"La forma de amar, vincularte y buscar bienestar se vive con mucha intensidad. "
                f"No suelen servirte los vínculos tibios, ambiguos o vacíos de presencia real. "
                f"Puede haber cansancio de adaptarte demasiado a otras personas o de sostener relaciones que ya no alimentan tu vitalidad. "
                f"El aprendizaje está en reconocer qué personas, espacios y elecciones tienen vida real para ti."
            ),

            "Marte": (
                base +
                f"Tu manera de actuar y reaccionar puede sentirse muy intensa, como si hubiera poco margen para hacer las cosas a medias. "
                f"Puede haber urgencia por resolver, avanzar o cortar con lo que bloquea. "
                f"Cuando esa energía no encuentra salida, puede transformarse en tensión, irritación o sensación interna de lucha constante. "
                f"Necesitas movimiento y descarga, pero también aprender a dirigir esa fuerza sin agotarte."
            ),

            "Júpiter": (
                base +
                f"La necesidad de crecer, expandirte y encontrar sentido aparece con mucha fuerza. "
                f"Puede costarte permanecer mucho tiempo en experiencias que sientes pequeñas, limitadas o vacías de propósito. "
                f"A veces puedes buscar siempre el siguiente horizonte antes de terminar de integrar lo que ya estás viviendo. "
                f"El aprendizaje está en encontrar amplitud sin perder estabilidad."
            ),

            "Saturno": (
                base +
                f"Puedes tener una gran capacidad para sostener responsabilidades y seguir adelante incluso cuando estás cansado. "
                f"El problema es que a veces aguantas demasiado antes de parar. "
                f"Puede costarte darte permiso para descansar sin sentir que estás fallando o perdiendo el control. "
                f"Parte del aprendizaje aquí consiste en entender que cuidarte también es una forma de responsabilidad."
            ),

            "Urano": (
                base +
                f"La necesidad de libertad, autenticidad y cambio puede sentirse muy intensa. "
                f"Hay poca tolerancia a lo que se vive como rígido, repetitivo o demasiado cerrado. "
                f"Cuando algo te hace sentir atrapado, la necesidad de romper o alejarte puede aparecer muy rápido. "
                f"El aprendizaje está en crear espacio y movimiento sin tener que llegar siempre al corte brusco."
            ),

            "Neptuno": (
                base +
                f"Eres especialmente sensible al ambiente, a las emociones de otras personas y a todo lo que ocurre alrededor. "  
                f"Cuando no hay suficiente descanso, silencio o límites claros, puedes terminar absorbiendo demasiado y perder claridad sobre lo que realmente necesitas. "
                f"No todo lo que sientes es necesariamente tuyo. "
                f"Aprender a diferenciarlo cambia mucho tu equilibrio interno."
            ),

            "Plutón": (
                base +
                f"Vives los procesos importantes con mucha intensidad y profundidad. "
                f"Cuando algo se mueve dentro de ti, rara vez se queda en la superficie. "
                f"Puede haber una relación intensa con el control, las pérdidas, los cambios profundos o la necesidad de transformación. "
                f"El aprendizaje está en atravesar esa profundidad con recursos y apoyo, sin quedarte atrapado dentro de ella."
            ),

            "Quirón": (
                base +
                f"Hay una zona especialmente sensible en tu vida que puede sentirse vulnerable o expuesta desde hace mucho tiempo. "
                f"Esa sensibilidad puede doler, pero también darte una capacidad muy profunda para comprender procesos similares en otras personas. "
                f"No se trata de eliminar esa parte de ti, sino de dejar de vivirla como un defecto."
            ),

            "Lilith": (
                base +
                f"Hay una parte muy instintiva y difícil de domesticar dentro de ti que necesita espacio real para existir. "
                f"Puedes reaccionar con mucha intensidad frente a dinámicas que se sienten falsas, impuestas o demasiado controladoras. "
                f"Cuando esa energía no tiene lugar consciente, puede salir como irritación, rechazo o necesidad brusca de cortar. "
                f"El aprendizaje está en reconocer esa fuerza sin dejar que tome el control desde la reacción automática."
            ),

            "Nodo Norte": (
                base +
                f"Tu dirección de crecimiento se vive con mucha intensidad, como algo que te llama aunque también dé miedo. "
                f"Avanzar hacia ahí suele implicar dejar atrás formas antiguas de seguridad o funcionamiento. "
                f"No es un camino cómodo al principio, porque pide consciencia, práctica y decisión sostenida. "
                f"El crecimiento real no ocurre por presión, sino por capacidad de sostener el cambio."
            ),

            "Nodo Sur": (
                base +
                f"Hay formas antiguas de reaccionar, protegerte o buscar seguridad que salen de manera muy automática. "
                f"Esas dinámicas pueden darte sensación de familiaridad, aunque ya no te ayuden realmente a crecer. "
                f"No se trata de rechazar esa parte de ti, sino de dejar de vivir únicamente desde ahí. "
                f"El aprendizaje está en usar esa experiencia acumulada como apoyo, no como lugar donde quedarse atrapado."
            ),
        }

        return textos.get(nombre, base + "Esta posición señala una función que se vive con especial intensidad y pide más consciencia en su forma de expresión.")

    anareticos = [p for p in puntos if p["nivel"] == "anaretico"]
    pre = [p for p in puntos if p["nivel"] == "pre_anaretico"]

    partes = []

    intro = (
        "Los grados finales de signo suelen hablar de zonas de la carta donde hay mucha experiencia acumulada y sensación de       cierre de etapa. "
        "La energía no se vive de forma ligera o automática: suele haber más intensidad, más consciencia y la sensación de que una forma antigua de funcionar ya no termina de encajar igual.\n\n"
        "No significa algo negativo ni indica un destino fijo. "
        "Simplemente muestra lugares donde la vida suele pedir más presencia, más maduración y una manera distinta de responder."
    )

    partes.append(intro)

    if anareticos:
        partes.append(
            "En esta carta aparecen posiciones en grado anarético (29°). "
            "Estos grados suelen sentirse como puntos de máxima intensidad dentro de un signo. "
            "Hay mucha experiencia acumulada, pero también sensación de presión interna, cansancio de repetir ciertos patrones o necesidad de cambio.\n\n"
            "A veces se vive como si ya no fuera posible seguir respondiendo exactamente igual que antes."
        )
  
        for p in anareticos:
            partes.append(texto_punto(p))

    if pre:
        partes.append(
            "También aparecen posiciones en grados previos al anarético. "
            "No suelen sentirse tan extremos como el grado 29, pero sí muestran zonas donde ya existe bastante maduración y donde empiezan a aparecer señales de cambio o agotamiento de una forma antigua de funcionar."
        )

        for p in pre:
            partes.append(texto_punto(p))

    partes.append(
        "Cuando varios puntos de la carta están al final de signo, la vida puede sentirse más intensa o vivirse con menos sensación de margen interno. "
        "A veces aparece urgencia, cansancio de ciertas dinámicas o sensación de estar cerca de cambios importantes incluso aunque externamente todo siga igual.\n\n"
        "No significa que la vida vaya a ser más difícil. "
        "Significa que esas zonas necesitan más consciencia, más pausa y una forma más presente de responder, en lugar de seguir funcionando únicamente desde hábitos automáticos."
    )

    return "\n\n".join(partes)

# ─── SECCIÓN: ORGANIZACIÓN DE LA ENERGÍA ─────────────────────────────────────

MERCURIO_SIGNO = {
"Aries":    "Tu Mercurio en Aries piensa rápido y va directo a la acción. Captas lo esencial con facilidad, pero puede costarte detenerte en matices o escuchar demasiado tiempo antes de responder. Te ayuda dejar un pequeño espacio entre la idea y la reacción.",
"Tauro":    "Tu Mercurio en Tauro necesita tiempo para procesar. No suele llegar a conclusiones por impulso, pero cuando algo se asienta, resulta difícil moverlo. Piensas mejor cuando hay calma, continuidad y contacto con lo concreto.",
"Géminis":  "Tu Mercurio en Géminis se mueve con rapidez entre ideas, conversaciones y estímulos. Aprendes conectando cosas distintas y necesitas variedad mental. El riesgo aparece cuando hay demasiados frentes abiertos y cuesta profundizar en uno solo.",
"Cáncer":   "Tu Mercurio en Cáncer piensa muy influido por cómo te sientes. Recuerdas bien lo que ha tenido carga emocional y captas fácilmente el tono de una conversación. El riesgo aparece cuando una emoción del momento condiciona demasiado la interpretación de lo que ocurre.",
"Leo":      "Tu Mercurio en Leo necesita expresar sus ideas con presencia y claridad. Piensas mejor cuando puedes poner algo propio en lo que dices. El riesgo aparece cuando la necesidad de que te escuchen dificulta recibir otras perspectivas.",
"Virgo":    "Tu Mercurio en Virgo observa, ordena y detecta detalles con facilidad. Tienes capacidad para analizar lo que no funciona y mejorarlo. El riesgo aparece cuando la mente se queda demasiado tiempo corrigiendo, revisando o buscando el fallo.",
"Libra":    "Tu Mercurio en Libra piensa teniendo en cuenta varias posiciones a la vez. Puedes ver con facilidad lo que cada parte necesita o defiende. El riesgo aparece cuando considerar demasiadas opciones retrasa una decisión que ya necesita tomarse.",
"Escorpio": "Tu Mercurio en Escorpio no se queda fácilmente en la superficie. Tiendes a buscar lo que hay detrás de las palabras, los silencios o las contradicciones. El riesgo aparece cuando la mente entra en sospecha o intensidad y le cuesta soltar una idea.",
"Sagitario":"Tu Mercurio en Sagitario necesita entender el sentido general de las cosas. Piensas mejor cuando puedes ver el panorama completo y conectar una experiencia con algo más amplio. El riesgo aparece cuando el conjunto interesa tanto que los detalles quedan sin revisar.",
"Capricornio":"Tu Mercurio en Capricornio piensa de forma práctica, ordenada y orientada a resultados. Necesitas estructura, claridad y pasos concretos para organizar bien una idea. El riesgo aparece cuando la mente se vuelve demasiado rígida o tarda en permitirse probar algo nuevo.",
"Acuario":  "Tu Mercurio en Acuario piensa de forma independiente y poco convencional. Puedes ver alternativas que otras personas no contemplan y cuestionar estructuras con facilidad. El riesgo aparece cuando la idea se queda demasiado arriba y cuesta bajarla a algo aplicable.",
"Piscis":   "Tu Mercurio en Piscis percibe más por imágenes, sensaciones y asociaciones que por lógica lineal. Puedes captar matices sutiles, pero no siempre resulta fácil explicarlos con orden. Te ayuda dar forma poco a poco a lo que percibes antes de intentar comunicarlo.",
}

VENUS_SIGNO = {
"Aries":    "Tu Venus en Aries se vincula con impulso, franqueza y necesidad de movimiento. Te atraen los vínculos vivos, donde hay deseo, iniciativa y espacio para actuar. El riesgo aparece cuando la intensidad inicial baja y cuesta sostener ritmos más lentos.",
"Tauro":    "Tu Venus en Tauro necesita estabilidad, presencia y gestos concretos. El afecto se sostiene mejor cuando hay continuidad, confianza y contacto real. El riesgo aparece cuando la necesidad de seguridad dificulta cambiar una dinámica que ya no nutre.",
"Géminis":  "Tu Venus en Géminis necesita comunicación, curiosidad y estímulo mental en los vínculos. La palabra, el humor y el intercambio mantienen vivo el interés. El riesgo aparece cuando la variedad sustituye a la profundidad o cuando el vínculo se queda solo en lo mental.",
"Cáncer":   "Tu Venus en Cáncer se vincula desde el cuidado, la memoria y la necesidad de sentirse en casa con otra persona. La cercanía emocional tiene mucho peso. El riesgo aparece cuando cuidar demasiado hace que olvides comprobar qué necesitas tú.",
"Leo":      "Tu Venus en Leo necesita expresión, reconocimiento y cierta alegría compartida en el vínculo. El afecto se activa cuando puedes mostrarte y sentir una respuesta cálida. El riesgo aparece cuando la falta de reconocimiento se vive como falta de amor.",
"Virgo":    "Tu Venus en Virgo expresa afecto a través de detalles, cuidado práctico y atención a lo cotidiano. Puedes amar mejorando, ayudando o estando pendiente de lo que hace falta. El riesgo aparece cuando el deseo de cuidar se convierte en exigencia, crítica o sensación de no ser suficiente.",
"Libra":    "Tu Venus en Libra busca equilibrio, reciprocidad y buen trato. Necesitas sentir que el vínculo tiene proporción y que ambas partes cuentan. El riesgo aparece cuando evitar el conflicto se vuelve más importante que decir con claridad lo que necesitas.",
"Escorpio": "Tu Venus en Escorpio se vincula con intensidad y necesidad de confianza real. No te alimentan los vínculos superficiales cuando algo importa de verdad. El riesgo aparece cuando el miedo a perder o a quedar expuesto lleva a controlar más de lo necesario.",
"Sagitario":"Tu Venus en Sagitario necesita libertad, movimiento y sentido compartido. El vínculo se fortalece cuando hay crecimiento, aprendizaje o una dirección que ilusiona. El riesgo aparece cuando cualquier límite se vive como encierro, incluso cuando el vínculo necesita estructura.",
"Capricornio":"Tu Venus en Capricornio se vincula con seriedad, compromiso y hechos concretos. El afecto no siempre se expresa de forma expansiva, pero puede ser muy constante. El riesgo aparece cuando protegerte demasiado hace difícil mostrar necesidad o ternura.",
"Acuario":  "Tu Venus en Acuario necesita libertad, espacio propio y una conexión que no se sienta posesiva. Te atraen los vínculos donde puedes ser diferente sin tener que explicarte todo el tiempo. El riesgo aparece cuando la distancia emocional se confunde con autonomía.",
"Piscis":   "Tu Venus en Piscis se vincula con mucha sensibilidad y apertura. Puedes entregarte con facilidad cuando sientes conexión, pero también adaptarte demasiado a la otra persona. El riesgo aparece cuando la compasión, el deseo de unión o la idealización borran tus propios límites.",
}

MARTE_SIGNO = {
"Aries":    "Tu Marte en Aries actúa rápido, con iniciativa y poca espera. Cuando algo se activa, necesitas moverte o intervenir. El riesgo aparece cuando la acción se adelanta a la evaluación y terminas gastando fuerza antes de tener una dirección clara.",
"Tauro":    "Tu Marte en Tauro actúa despacio, pero con mucha persistencia. No se activa por cualquier cosa, pero cuando toma dirección puede sostenerla durante mucho tiempo. El riesgo aparece cuando la resistencia al cambio te mantiene en una posición más de lo necesario.",
"Géminis":  "Tu Marte en Géminis actúa a través de la palabra, las ideas y la movilidad. Puedes hacer varias cosas a la vez y reaccionar rápido ante estímulos distintos. El riesgo aparece cuando hay demasiadas direcciones abiertas y la energía se dispersa.",
"Cáncer":   "Tu Marte en Cáncer actúa desde lo que siente. La motivación aparece cuando algo toca tu mundo emocional, tu hogar o tus vínculos cercanos. El riesgo aparece cuando la acción se vuelve indirecta, defensiva o condicionada por estados emocionales cambiantes.",
"Leo":      "Tu Marte en Leo actúa con presencia, creatividad y necesidad de implicarse personalmente. La energía aumenta cuando puedes poner algo propio en lo que haces. El riesgo aparece cuando la falta de reconocimiento apaga la motivación o convierte la acción en demostración.",
"Virgo":    "Tu Marte en Virgo dirige la acción hacia mejorar, ordenar y resolver. Tienes capacidad para trabajar con detalle y corregir lo que no funciona. El riesgo aparece cuando la acción se atasca por exceso de revisión, autocrítica o búsqueda de perfección.",
"Libra":    "Tu Marte en Libra actúa mejor cuando hay acuerdo, colaboración o una dirección compartida. Antes de moverte, sueles tener en cuenta a la otra persona. El riesgo aparece cuando esperar equilibrio o aprobación retrasa una acción que ya necesita hacerse.",
"Escorpio": "Tu Marte en Escorpio actúa con intensidad, resistencia y mucha concentración cuando algo importa. No se mueve de forma ligera: necesita implicación real. El riesgo aparece cuando la fuerza se convierte en control, tensión acumulada o dificultad para soltar una batalla.",
"Sagitario":"Tu Marte en Sagitario actúa con entusiasmo, impulso y necesidad de expansión. La energía aumenta cuando hay un objetivo con sentido o una posibilidad de avanzar. El riesgo aparece cuando la acción se dispersa por exceso de apertura o falta de concreción.",
"Capricornio":"Tu Marte en Capricornio actúa con estrategia, disciplina y orientación a largo plazo. Puede sostener esfuerzos prolongados cuando hay una meta clara. El riesgo aparece cuando la exigencia se vuelve demasiado dura y la acción pierde flexibilidad.",
"Acuario":  "Tu Marte en Acuario actúa de forma independiente y poco convencional. Necesitas sentir que lo que haces tiene sentido propio y no responde solo a una orden externa. El riesgo aparece cuando la resistencia a lo impuesto dificulta colaborar o sostener un ritmo común.",
"Piscis":   "Tu Marte en Piscis actúa mejor cuando hay inspiración, sensibilidad o una motivación interna clara. La acción puede volverse difusa si el objetivo es demasiado rígido o no tiene sentido emocional. Te ayuda concretar pasos pequeños para que la energía no se disuelva antes de ponerse en marcha.",
}

MERC_CASA = {
1:  "En Casa 1, la mente forma parte visible de cómo te presentas. Sueles pensar mucho sobre ti, sobre cómo actuar y sobre la impresión que generas. La comunicación tiene un peso importante en tu forma de entrar en contacto con el mundo.",

2:  "En Casa 2, la mente tiende a centrarse en recursos, estabilidad y formas concretas de sostenerte. Piensas mucho en lo que tiene valor, en cómo generar seguridad y en qué merece realmente tu energía.",

3:  "En Casa 3, Mercurio está en un territorio muy natural para él. Aprendes rápido a través de la conversación, el intercambio y el movimiento cercano. La curiosidad y la necesidad de entender lo que ocurre alrededor suelen estar muy activas.",

4:  "En Casa 4, el pensamiento está muy influido por el mundo privado, la memoria y el entorno emocional cercano. Sueles procesar las cosas internamente antes de compartirlas con otras personas.",

5:  "En Casa 5, la mente necesita creatividad, expresión y cierta libertad para funcionar bien. Piensas mejor cuando hay entusiasmo, juego o posibilidad de poner algo personal en lo que haces.",

6:  "En Casa 6, la mente se orienta fácilmente al análisis práctico y a resolver problemas concretos. Hay capacidad para organizar, mejorar y detectar lo que no funciona en lo cotidiano.",

7:  "En Casa 7, el pensamiento se activa mucho a través de otras personas. Las conversaciones, los vínculos y los intercambios importantes estimulan tu forma de pensar y ayudan a ordenar ideas.",

8:  "En Casa 8, la mente tiende a profundizar y no quedarse fácilmente en la superficie. Hay interés por entender lo que otras personas callan, lo complejo o lo que genera intensidad emocional.",

9:  "En Casa 9, la mente necesita amplitud, perspectiva y sensación de aprendizaje continuo. Piensas mejor cuando puedes conectar lo cotidiano con una visión más amplia.",

10: "En Casa 10, la forma de pensar y comunicarte influye directamente en tu espacio profesional o público. Tus ideas, palabras o capacidad de organización pueden tener impacto visible en tu trayectoria.",

11: "En Casa 11, la mente se activa en grupos, proyectos compartidos y espacios colectivos. Sueles conectar ideas fácilmente y pensar bien cuando hay intercambio con otras personas.",

12: "En Casa 12, muchas ideas necesitan silencio y tiempo interno antes de tomar forma clara. Sueles pensar mejor en soledad o cuando hay suficiente espacio para bajar el ruido externo.",
}


VENUS_CASA = {
1:  "En Casa 1, la forma de relacionarte se percibe rápidamente desde fuera. El vínculo, la atracción y la manera de conectar forman parte importante de cómo te muestras al mundo.",

2:  "En Casa 2, el afecto necesita estabilidad, continuidad y sensación de seguridad. Valoras mucho los gestos concretos, la presencia real y los vínculos que ayudan a construir algo sólido.",

3:  "En Casa 3, el afecto fluye especialmente a través de la conversación, la cercanía y el intercambio cotidiano. La comunicación tiene mucho peso en cómo se construyen tus relaciones.",

4:  "En Casa 4, el vínculo necesita intimidad, confianza y sensación de hogar. El espacio privado y emocional es donde el afecto se vuelve realmente importante para ti.",

5:  "En Casa 5, el amor necesita expresión, disfrute y cierta sensación de entusiasmo. Los vínculos se fortalecen cuando hay creatividad, juego o alegría compartida.",

6:  "En Casa 6, el afecto suele expresarse a través del cuidado cotidiano y los gestos prácticos. Estar pendiente de lo que hace falta puede ser una forma importante de mostrar amor.",

7:  "En Casa 7, las relaciones tienen un peso central en tu vida. Los vínculos importantes influyen mucho en cómo te ves y en tu equilibrio emocional.",

8:  "En Casa 8, los vínculos necesitan profundidad, confianza y sensación de entrega real. Las relaciones superficiales suelen dejarte vacío cuando algo importa de verdad.",

9:  "En Casa 9, el vínculo necesita crecimiento, libertad y una visión compartida. Las relaciones se fortalecen cuando hay aprendizaje, expansión o sensación de avanzar juntos.",

10: "En Casa 10, el reconocimiento, la admiración o el espacio profesional pueden influir mucho en la vida relacional. Algunas relaciones importantes pueden aparecer a través del trabajo o de la vocación.",

11: "En Casa 11, el afecto se desarrolla mejor cuando hay amistad, intercambio y proyectos compartidos. Necesitas sentir que la relación también funciona como espacio de libertad y conexión humana.",

12: "En Casa 12, los vínculos suelen vivirse de forma muy interna o difícil de explicar completamente. Puedes entregarte mucho emocionalmente y necesitar momentos de soledad para entender realmente lo que sientes.",
}


MARTE_CASA = {
1:  "En Casa 1, la energía de acción se muestra directamente. Sueles reaccionar rápido, tomar iniciativa y entrar en movimiento antes de esperar permiso o confirmación externa.",

2:  "En Casa 2, la acción se dirige a construir estabilidad, recursos y autonomía. Hay impulso real para defender lo propio y sostenerte por tus propios medios.",

3:  "En Casa 3, la energía se expresa mucho a través de la palabra, las ideas y el movimiento cotidiano. El debate, el intercambio o la necesidad de responder rápido pueden activarse fácilmente.",

4:  "En Casa 4, la acción está muy ligada al hogar, la intimidad y la necesidad de proteger tu espacio privado. Hay mucha fuerza disponible cuando se trata de defender lo que sientes como propio.",

5:  "En Casa 5, la energía necesita creatividad, juego y emoción para activarse del todo. Funcionas mejor cuando puedes poner entusiasmo, deseo o expresión personal en lo que haces.",

6:  "En Casa 6, la acción se orienta fácilmente al trabajo, los hábitos y la resolución práctica de problemas. Hay capacidad para sostener esfuerzo y mantener actividad constante en lo cotidiano.",

7:  "En Casa 7, la energía se activa mucho a través de otras personas. Los vínculos importantes pueden generar tanto colaboración intensa como confrontación directa cuando hay tensión.",

8:  "En Casa 8, la acción aparece con mucha fuerza en situaciones intensas, límites o momentos de crisis. Hay capacidad de resistencia y dificultad para hacer las cosas a medias cuando algo importa.",

9:  "En Casa 9, la energía necesita expansión, aprendizaje y sensación de movimiento. Actúas con más fuerza cuando hay algo nuevo que explorar o comprender.",

10: "En Casa 10, la acción se orienta fuertemente hacia objetivos, reconocimiento y construcción profesional. Hay capacidad para sostener esfuerzo cuando existe una meta clara.",

11: "En Casa 11, la energía se moviliza fácilmente en proyectos colectivos, grupos o causas compartidas. Puedes implicarte mucho cuando sientes que algo merece ser defendido en común.",

12: "En Casa 12, gran parte de la energía funciona de forma interna o poco visible desde fuera. Necesitas momentos de retirada, silencio o trabajo en soledad para ordenar bien el impulso antes de actuar.",
}

def texto_organizacion_energia(carta):
    planetas = carta["planetas"]
    merc = planetas.get("Mercurio",{})
    venus= planetas.get("Venus",{})
    marte= planetas.get("Marte",{})

    s_merc  = MERCURIO_SIGNO.get(merc.get("signo",""),"")
    s_venus = VENUS_SIGNO.get(venus.get("signo",""),"")
    s_marte = MARTE_SIGNO.get(marte.get("signo",""),"")

    s_merc_casa  = MERC_CASA.get(merc.get("casa",0),"") if merc else ""
    s_venus_casa = VENUS_CASA.get(venus.get("casa",0),"") if venus else ""
    s_marte_casa = MARTE_CASA.get(marte.get("casa",0),"") if marte else ""

    return (
        f"{s_merc} {s_merc_casa} "
        f"{s_venus} {s_venus_casa} "
        f"{s_marte} {s_marte_casa}"
    )

# ─── SECCIÓN: STELLIUM ───────────────────────────────────────────────────────

def texto_stellium(planetas):
    ORDEN = ["Sol","Luna","Mercurio","Venus","Marte","Júpiter","Saturno",
             "Urano","Neptuno","Plutón","Quirón","Nodo Norte","Nodo Sur","Lilith"]

    STELLIUM_CASA = {
        1:  "la forma de mostrarse y ocupar espacio",
        2:  "los recursos, la estabilidad y el valor propio",
        3:  "la comunicación, el aprendizaje y el entorno cercano",
        4:  "el hogar, la intimidad y la base emocional",
        5:  "la creatividad, el disfrute y la expresión personal",
        6:  "el trabajo cotidiano, los hábitos y la relación con el cuerpo",
        7:  "las relaciones importantes y el vínculo con otra persona",
        8:  "los vínculos intensos, las pérdidas y las situaciones difíciles de controlar",
        9:  "el aprendizaje, la expansión y la necesidad de ampliar horizontes",
        10: "la vocación, la responsabilidad y el espacio público",
        11: "las amistades, los grupos y los proyectos compartidos",
        12: "la vida privada, la necesidad de retiro y los procesos internos",
    }
    por_casa = {}
    for nombre, p in planetas.items():
        c = p["casa"]
        if c not in por_casa:
            por_casa[c] = []
        por_casa[c].append(nombre)

    stellia = sorted(
        [(c, ns) for c, ns in por_casa.items() if len(ns) >= 3],
        key=lambda x: -len(x[1])
    )
    if not stellia:
        return ""

    parrafos = []

    for i, (casa, nombres) in enumerate(stellia):
        nombres_ord = sorted(nombres, key=lambda n: ORDEN.index(n) if n in ORDEN else 99)

        if len(nombres_ord) >= 2:
            nombres_str = ", ".join(nombres_ord[:-1]) + " y " + nombres_ord[-1]
        else:
            nombres_str = nombres_ord[0]

        area = STELLIUM_CASA.get(casa, f"el área de la casa {casa}")

        if i == 0:
            parrafos.append(
                f"Hay una concentración notable en Casa {casa}: {nombres_str}. "
                f"Cuando varios planetas ocupan la misma casa, esa área absorbe buena parte de la actividad vital. "
                f"En esta carta, el foco de {area} funciona como núcleo central: ahí se acumula la presión, "
                f"la demanda es mayor y también hay más recursos disponibles para operar. "
                f"No es necesariamente un conflicto, pero sí un punto de alta intensidad sostenida."
            )
        elif i == 1:
            parrafos.append(
                f"También hay una concentración significativa en Casa {casa}: {nombres_str}. "
                f"En este caso, el foco se desplaza hacia {area}. "
                f"Es un ámbito donde la exigencia aumenta, donde se concentra parte de la presión "
                f"y donde también existe capacidad real de sostener procesos importantes. "
                f"Tampoco es en sí un problema, pero sí un área de intensidad mantenida."
            )
        else:
            parrafos.append(
                f"Otra zona de concentración aparece en Casa {casa}: {nombres_str}. "
                f"Este ámbito, relacionado con {area}, reúne varias funciones de la carta en un mismo territorio de vida."
            )

    return "\n\n".join(parrafos)

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

# ─── SECCIÓN: SOSTÉN Y EQUILIBRIO ────────────────────────────────────────────

CHIRON_SIGNO = {
"Aries":      "la iniciativa propia, la capacidad de afirmarte y el derecho a ocupar espacio. Puede que en algún momento hayas sentido que actuar, decidir o ir primero generaba conflicto o rechazo",

"Tauro":      "la estabilidad, el valor propio y la relación con lo que necesitas para sostenerte. Puede que hayas vivido inseguridad material o sensación de no merecer descanso, placer o apoyo suficiente",

"Géminis":    "la comunicación, el aprendizaje y la capacidad de expresarte con libertad. Puede que hayas sentido que tus palabras no eran escuchadas o que pensar diferente generaba incomodidad",

"Cáncer":     "el cuidado, la pertenencia y la necesidad de sentirte protegido emocionalmente. Puede que te haya costado sentir verdadero refugio o confianza en el entorno cercano",

"Leo":        "la expresión personal, el reconocimiento y la posibilidad de mostrarte tal como eres. Puede que aprendieras a contenerte para no destacar demasiado o para evitar exponerte",

"Virgo":      "la utilidad, la organización y la sensación de hacer las cosas correctamente. Puede que hayas asociado tu valor personal con rendir bien, ayudar o no equivocarte",

"Libra":      "el vínculo, el equilibrio y la posibilidad de pedir lo que necesitas sin romper la relación. Puede que te hayas acostumbrado a priorizar la armonía antes que tu propia posición",

"Escorpio":   "la confianza, la intimidad y la capacidad de atravesar situaciones intensas sin perderte en ellas. Puede que algunas experiencias te hayan hecho difícil relajarte del todo en el vínculo",

"Sagitario":  "la confianza en tu visión, en tus ideas y en la posibilidad de avanzar con dirección propia. Puede que hayas sentido dudas sobre tu lugar, tus creencias o tu capacidad de encontrar un rumbo claro",

"Capricornio":"la autoridad, la responsabilidad y la sensación de tener que sostener demasiado peso sin ayuda de nadie. Puede que hayas aprendido pronto a exigirte más de la cuenta para sentir que merecías tu lugar",

"Acuario":    "la diferencia, la pertenencia y la sensación de encajar dentro de un grupo sin dejar de ser tú. Puede que te hayas sentido extraño, fuera de lugar o demasiado diferente",

"Piscis":     "los límites, la sensibilidad y la dificultad para diferenciar lo propio de lo ajeno. Puede que te haya costado sostener claridad cuando el entorno emocional era muy intenso",
}


CHIRON_CASA = {
1:  "especialmente en la forma de mostrarte y afirmarte directamente",

2:  "especialmente en el valor propio, la estabilidad y los recursos",

3:  "especialmente en la comunicación, el aprendizaje y el entorno cercano",

4:  "especialmente en el hogar, la intimidad y la base emocional",

5:  "especialmente en la expresión personal, el disfrute y la creatividad",

6:  "especialmente en el trabajo cotidiano, los hábitos y la relación con el cuerpo",

7:  "especialmente en los vínculos importantes y la forma de relacionarte",

8:  "especialmente en la intimidad, las pérdidas y las situaciones emocionalmente intensas",

9:  "especialmente en las creencias, el aprendizaje y la necesidad de encontrar dirección",

10: "especialmente en la vocación, la responsabilidad y el reconocimiento",

11: "especialmente en la pertenencia a grupos y los proyectos compartidos",

12: "especialmente en la vida privada, la necesidad de retiro y lo que cuesta mostrar",
}


NODO_SUR_SIGNO = {
"Aries":      "la tendencia a hacerlo todo sin ayuda o compañía, reaccionar rápido o no apoyarte suficientemente en otras personas",

"Tauro":      "la necesidad de mantener estabilidad incluso cuando una situación ya necesita cambiar",

"Géminis":    "la dispersión, el exceso de estímulo y la dificultad para sostener una dirección clara",

"Cáncer":     "la tendencia a refugiarte demasiado en lo conocido o en la seguridad emocional",

"Leo":        "la necesidad de reconocimiento o de sentir que tienes que destacar constantemente",

"Virgo":      "el exceso de control, perfeccionismo o autoexigencia para sentir valor personal",

"Libra":      "la dificultad para decidir desde tu interior cuando hay riesgo de conflicto o desacuerdo",

"Escorpio":   "la intensidad constante, el control o la dificultad para soltar situaciones desgastadas",

"Sagitario":  "la tendencia a irte demasiado lejos de lo concreto buscando algo más grande o ideal",

"Capricornio":"la rigidez, la autoexigencia y la sensación de tener que sostenerlo todo sin ayuda",

"Acuario":    "la distancia emocional o el refugio en la diferencia para no sentir demasiada cercanía",

"Piscis":     "la falta de límites claros, la adaptación excesiva o la tendencia a perderte en el entorno",
}


NODO_NORTE_SIGNO = {
"Aries":      "desarrollar iniciativa propia y capacidad de actuar desde tu propio centro sin esperar siempre aprobación",

"Tauro":      "construir estabilidad real, paciencia y una relación más sencilla con lo concreto",

"Géminis":    "desarrollar curiosidad, flexibilidad y capacidad de escuchar distintas perspectivas",

"Cáncer":     "permitirte cuidar y que te cuiden sin vivirlo como debilidad",

"Leo":        "mostrarte más auténticamente y confiar en lo que nace de ti",

"Virgo":      "desarrollar orden, presencia en lo cotidiano y capacidad de concretar",

"Libra":      "aprender a construir vínculos más equilibrados y menos defensivos",

"Escorpio":   "atravesar cambios importantes sin quedarte solo en lo conocido o controlable",

"Sagitario":  "desarrollar visión amplia y capacidad de avanzar con más confianza en tu dirección",

"Capricornio":"construir estructura, responsabilidad sana y estabilidad a largo plazo",

"Acuario":    "desarrollar independencia de pensamiento y aprender a participar en lo colectivo sin perderte",

"Piscis":     "desarrollar más sensibilidad, flexibilidad y capacidad de soltar control cuando ya no sirve",
}


NODO_CASA_DESC = {
1:  "en tu forma de afirmarte y mostrarte",

2:  "en el valor propio y la estabilidad material o emocional",

3:  "en la comunicación y el entorno cercano",

4:  "en el hogar, la intimidad y la base emocional",

5:  "en la creatividad, el disfrute y la expresión personal",

6:  "en los hábitos, el trabajo cotidiano y la relación con el cuerpo",

7:  "en las relaciones importantes y el vínculo con otra persona",

8:  "en la intimidad y las situaciones emocionalmente intensas",

9:  "en el aprendizaje, las creencias y la necesidad de ampliar horizontes",

10: "en la vocación, la responsabilidad y el espacio público",

11: "en los grupos, amistades y proyectos compartidos",

12: "en la vida privada, la necesidad de retiro y lo que cuesta mostrar directamente",
}

def texto_equilibrio_interno (carta, aspectos_ordenados):
    planetas = carta["planetas"]

    # Identificar tensiones principales
    tensiones = [
        (a["p1"], a["p2"], a["simbolo"], a["orbe"])
        for a in aspectos_ordenados
        if a["simbolo"] in ("□", "☍", "⚻")
    ]

    quiron = planetas.get("Quirón", {})
    nodo_norte = planetas.get("Nodo Norte", {})
    nodo_sur = planetas.get("Nodo Sur", {})

    # ─── Texto sobre Quirón ───────────────────────────────────────────────

    s_quir = ""

    if quiron:
        quir_signo_desc = CHIRON_SIGNO.get(
            quiron['signo'],
            "temas relacionados con ese signo"
        )

        quir_casa_desc = CHIRON_CASA.get(
            quiron['casa'],
            "en los temas de esa casa"
        )

        s_quir = (
            f"Tu Quirón en {quiron['signo']}, Casa {quiron['casa']}, señala una zona sensible relacionada con "
            f"{quir_signo_desc}. "
            f"Esto suele notarse {quir_casa_desc}. "
            f"No significa que tengas límites en ese terreno, pero sí que probablemente necesites más tiempo, cuidado o consciencia para sentir estabilidad ahí."
        )

    # ─── Texto sobre Nodos ────────────────────────────────────────────────

    s_nodo = ""

    if nodo_norte and nodo_sur:

        ns_desc = NODO_SUR_SIGNO.get(
            nodo_sur['signo'],
            "formas conocidas de funcionar"
        )

        nn_desc = NODO_NORTE_SIGNO.get(
            nodo_norte['signo'],
            "formas nuevas de desarrollarte"
        )

        casa_sur = NODO_CASA_DESC.get(
            nodo_sur['casa'],
            "en esa parte de tu vida"
        )

        casa_norte = NODO_CASA_DESC.get(
            nodo_norte['casa'],
            "en esa parte de tu vida"
        )

        s_nodo = (
            f"Tu Nodo Sur en {nodo_sur['signo']}, Casa {nodo_sur['casa']}, muestra una tendencia a moverte desde "
            f"{ns_desc}, especialmente {casa_sur}. "
            f"Suele ser una forma de funcionar conocida o automática para ti. "
            f"Tu Nodo Norte en {nodo_norte['signo']}, Casa {nodo_norte['casa']}, señala la necesidad de "
            f"{nn_desc}, especialmente {casa_norte}. "
            f"No se trata de rechazar lo anterior, sino de ampliar tu forma habitual de responder."
        )

    # ─── Texto de regulación ──────────────────────────────────────────────

    conteo_elem = analizar_elementos(planetas, carta["asc"]["signo"])

    elem_bajo = [e for e, n in conteo_elem.items() if n <= 1]

    s_reg = ""

    if elem_bajo:

        rutas = {
            "Tierra": "el contacto con el cuerpo, la rutina y lo concreto",
            "Aire":   "la perspectiva, el espacio mental y las conversaciones que ordenan",
            "Fuego":  "el movimiento, la acción y recuperar motivación o dirección",
            "Agua":   "la intimidad, el descanso emocional y los espacios donde puedes sentir sin presión",
        }

        ruta = " o ".join(
            [rutas.get(e, "") for e in elem_bajo if rutas.get(e)]
        )

        if ruta:
            s_reg = (
                f"En tu carta hay poca presencia de {', '.join(elem_bajo)}. "
                f"Cuando aparece saturación, bloqueo o sensación de desorganización interna, suele ayudarte volver a espacios relacionados con {ruta}. "
                f"Eso puede darte más estabilidad y ayudarte a recuperar claridad."
            )

    return {
        "quiron": s_quir,
        "nodo": s_nodo,
        "regulacion": s_reg
    }

# ─── SECCIÓN: SIGNOS INTERCEPTADOS ──────────────────────────────────────────

def texto_interceptados(carta):

    interceptados = carta.get("interceptados", {})

    if not interceptados:
        return ""

    planetas = carta["planetas"]

    partes = []
    vistos = set()

    for signo, casa in interceptados.items():

        if signo in vistos:
            continue

        idx = SIGNOS.index(signo)
        opuesto = SIGNOS[(idx + 6) % 12]

        vistos.add(signo)
        vistos.add(opuesto)

        # Planetas dentro del signo interceptado
        planetas_en = [
            n for n, p in planetas.items()
            if p.get("signo") == signo
        ]

        casa_op = interceptados.get(opuesto, "")

        planetas_op = [
            n for n, p in planetas.items()
            if p.get("signo") == opuesto
        ]

        desc_signo = (
            f"{signo} (Casa {casa})"
            + (f" con {', '.join(planetas_en)}" if planetas_en else "")
        )

        desc_opuesto = (
            f"{opuesto} (Casa {casa_op})"
            + (f" con {', '.join(planetas_op)}" if planetas_op else "")
        ) if opuesto in interceptados else ""

        partes.append(
            (desc_signo, desc_opuesto, planetas_en, planetas_op)
        )

    lineas = []

    for desc_s, desc_o, p_s, p_o in partes:

        todos = p_s + p_o

        if todos:

            desc_planetas = ", ".join(todos)

            lineas.append(
                f"Los signos {desc_s}"
                + (f" y {desc_o}" if desc_o else "")
                + f" aparecen interceptados: su expresión puede sentirse menos inmediata o menos natural al principio. "
                f"Esto influye especialmente en {desc_planetas}, que pueden necesitar más tiempo, experiencia o situaciones concretas para sentirse plenamente desarrollados. "
                f"Muchas veces estas posiciones no se muestran rápido desde fuera, pero ganan fuerza y claridad con los años."
            )

        else:

            lineas.append(
                f"Los signos {desc_s}"
                + (f" y {desc_o}" if desc_o else "")
                + f" aparecen interceptados: algunas cualidades relacionadas con esos signos pueden tardar más en expresarse con naturalidad o confianza."
            )

    return " ".join(lineas)

# ─── SECCIÓN: ORIENTACIÓN ────────────────────────────────────────────────────

def texto_orientacion(carta, aspectos_ordenados):

    planetas = carta["planetas"]
    asc_signo = carta["asc"]["signo"]

    tensiones_exactas = [
        a for a in aspectos_ordenados
        if a["simbolo"] in ("□", "☍", "⚻")
    ]

    recursos_exactos = [
        a for a in aspectos_ordenados
        if a["simbolo"] in ("△", "✶", "=")
    ]

    # ─── OBSERVAR ────────────────────────────────────────────────────────

    s_observar = (
        f"Tu Ascendente en {asc_signo} describe la forma en que otras personas suelen percibirte al principio. "
        f"Eso no siempre coincide con cómo vives las cosas internamente o con las tensiones más importantes de tu carta. "
        f"Cuando hay demasiada distancia entre lo que muestras y lo que realmente te ocurre, aparece desgaste."
    )

    # ─── LO QUE MÁS TE DESORGANIZA ──────────────────────────────────────

    s_desregula = (
        "Lo que suele desorganizarte más fácilmente es acumular demasiada tensión sin suficiente espacio para parar, ordenar o descargar."
    )

    if tensiones_exactas:

        nombres = ", ".join(
            [f"{a['p1']}-{a['p2']}" for a in tensiones_exactas[:3]]
        )

        s_desregula = (
            f"Hay ciertas tensiones en tu carta que pueden activarse con bastante fuerza: {nombres}. "
            f"Cuando varias coinciden al mismo tiempo, puede aparecer sensación de saturación, reacción excesiva o dificultad para mantener claridad."
        )

    # ─── LO QUE MÁS TE AYUDA ────────────────────────────────────────────

    s_sostiene = (
        "Lo que más suele ayudarte es recuperar contacto con lo que realmente tiene valor para ti y volver a ritmos más simples y concretos."
    )

    sol = planetas.get("Sol", {})

    if sol:

        s_sostiene = (
            f"Tu Sol en {sol['signo']}, Casa {sol['casa']}, muestra un terreno importante de estabilidad para ti. "
            f"Cuando tu forma de actuar está alineada con lo que realmente valoras, suele aparecer más claridad y menos dispersión."
        )

    # ─── ORIENTACIÓN PRÁCTICA ───────────────────────────────────────────

    s_practica = (
        "Una orientación práctica: cuando todo se activa demasiado, no intentes resolverlo todo desde la cabeza. "
        "Empieza por algo pequeño y concreto que te devuelva presencia: caminar, ordenar una parte de tu espacio, cocinar, respirar con calma o hacer algo físico y sencillo. "
        "Muchas veces el cuerpo recupera claridad antes que la mente."
    )

    # Personalización por elemento bajo

    conteo_elem = analizar_elementos(planetas, asc_signo)

    if conteo_elem.get("Tierra", 0) <= 1:

        s_practica = (
            "Una orientación práctica: en tu carta hay poca Tierra. "
            "Cuando aparece saturación o exceso de actividad mental, suele ayudarte volver a cosas muy concretas y físicas: mover el cuerpo, cocinar, ordenar, caminar o sostener una rutina sencilla durante varios días seguidos. "
            "Lo importante no es hacerlo perfecto, sino recuperar sensación de estabilidad."
        )

    elif conteo_elem.get("Aire", 0) <= 1:

        s_practica = (
            "Una orientación práctica: en tu carta hay poco Aire. "
            "Cuando las emociones o las tensiones aumentan, puede costarte tomar distancia y ordenar lo que te ocurre. "
            "Escribir, hablar con alguien de confianza o darte tiempo antes de reaccionar puede ayudarte mucho más de lo que parece."
        )

    elif conteo_elem.get("Agua", 0) <= 1:

        s_practica = (
            "Una orientación práctica: en tu carta hay poca Agua. "
            "A veces puedes seguir funcionando aunque lleves tiempo acumulando cansancio emocional. "
            "Parar, descansar de verdad o permitirte sentir antes de seguir avanzando puede ayudarte a no endurecerte demasiado."
        )

    elif conteo_elem.get("Fuego", 0) <= 1:

        s_practica = (
            "Una orientación práctica: en tu carta hay poco Fuego. "
            "Cuando aparece bloqueo o agotamiento, muchas veces necesitas recuperar movimiento, dirección o motivación antes que seguir pensando. "
            "Pequeñas acciones concretas suelen ayudarte más que esperar a tenerlo todo claro."
        )

    return {
        "observar": s_observar,
        "desregula": s_desregula,
        "sostiene": s_sostiene,
        "practica": s_practica,
    }

# ─── ESCAPADO LATEX ───────────────────────────────────────────────────────────

def esc(texto):
    for orig, repl in [('&',r'\&'),('%',r'\%'),('$',r'\$'),('#',r'\#'),
                       ('_',r'\_'),('{',r'\{'),('}',r'\}'),
                       ('~',r'\textasciitilde{}'),('\\',r'\textbackslash{}')]:
        texto = texto.replace(orig, repl)
    return texto

# ─── GENERACIÓN LATEX ─────────────────────────────────────────────────────────

def generar_latex_ai(carta, nombre, año, mes, dia, hora, minuto,
                     ciudad, lat, lon, tz_name, ruta_rueda, aspectos):
    planetas = carta["planetas"]
    asc = carta["asc"]; mc = carta["mc"]
    # Usar solo el nombre de archivo para que pdflatex lo encuentre en cwd
    ruta_rueda = os.path.basename(ruta_rueda).replace("\\", "/")
    fecha_str = f"{dia:02d}/{mes:02d}/{año}"
    hora_str  = f"{hora:02d}:{minuto:02d}"
    tz_obj = pytz.timezone(tz_name)
    dt_local = tz_obj.localize(datetime(año,mes,dia,hora,minuto))
    utc_off  = dt_local.strftime("%z")
    utc_str  = f"UTC{utc_off[:3]}:{utc_off[3:]}"
    nom_esc  = esc(nombre); ciu_esc = esc(ciudad)

    # Análisis
    conteo_elem  = analizar_elementos(planetas, asc["signo"], hora_conocida=(minuto is not None))
    conteo_modal = analizar_modalidades(planetas)
    asp_ord      = aspectos  # ya ordenados por orbe

    vision   = texto_vision_general(carta, conteo_elem, conteo_modal)
    ejes     = texto_ejes_principales(carta)
    org      = texto_organizacion_energia(carta)
    grados_criticos = texto_grados_criticos(carta)
    tens_raw = texto_estructura_tension(asp_ord)    
    stellium = texto_stellium(planetas)
    sost     = texto_equilibrio_interno(carta, asp_ord)
    orient   = texto_orientacion(carta, asp_ord)
    interc   = texto_interceptados(carta)

    # Tabla de planetas
    orden_tabla = ["Sol","Luna","Mercurio","Venus","Marte","Júpiter","Saturno",
                   "Urano","Neptuno","Plutón","Quirón","Lilith","Nodo Norte","Nodo Sur"]
    filas = []
    for nombre_p in orden_tabla:
        if nombre_p not in planetas: continue
        p = planetas[nombre_p]
        retro      = "R" if p.get("retrogrado") else ""
        interc_mark = "*" if p.get("interceptado") else ""
        elem   = ELEMENTO_SIGNO.get(p["signo"],"—")
        filas.append(
            f"  {esc(nombre_p)} & "
            f"{esc(p['signo'])}{interc_mark} & {grado_a_dms(p['grado'])} & "
            f"{p['casa']} & {elem} & {retro} \\\\"
        )
    tabla = "\n".join(filas)

    # Nota sobre signos interceptados
    interceptados = carta.get("interceptados", {})
    if interceptados:
        pares = []
        vistos = set()
        for s, c in interceptados.items():
            if s not in vistos:
                # buscar el signo opuesto (siempre vienen en pares)
                idx = SIGNOS.index(s)
                opuesto = SIGNOS[(idx+6)%12]
                c_op = interceptados.get(opuesto, "")
                if opuesto in interceptados and opuesto not in vistos:
                    pares.append(f"{esc(s)} (casa {c}) -- {esc(opuesto)} (casa {c_op})")
                    vistos.add(s); vistos.add(opuesto)
                else:
                    pares.append(f"{esc(s)} (casa {c})")
                    vistos.add(s)
        items_interc = "\n".join(f"  \\item {p}" for p in pares)
        nota_interceptados = (
            f"  \\item \\textbf{{Signos interceptados}} (marcados con * en la tabla):\n"
            f"  \\begin{{itemize}}\n{items_interc}\n  \\end{{itemize}}\n"
        )
    else:
        nota_interceptados = ""

    # Signos interceptados en interpretación
    interc_tex = (
        "\\subsubsection*{Signos interceptados}\n" + esc(interc)
    ) if interc else ""

    _ASP_TEX = {"=":"conjunción","☍":"oposición","□":"cuadratura","△":"trígono","✶":"sextil","⚻":"quincuncio"}

    def _fmt_asp(lista):
        out = ""
        for asp, texto_asp in lista:
            sim_tex = _ASP_TEX.get(asp["simbolo"], asp["simbolo"])
            p1_info = planetas.get(asp["p1"], {})
            p2_info = planetas.get(asp["p2"], {})
            p1_casa = f" (Casa {p1_info['casa']})" if p1_info.get("casa") else ""
            p2_casa = f" (Casa {p2_info['casa']})" if p2_info.get("casa") else ""

            out += (
                "\\Needspace{3\\baselineskip}\n"
                f"\\subsubsection*{{{esc(asp['p1'])}{p1_casa} {sim_tex} {esc(asp['p2'])}{p2_casa} "
                f"--- orbe {asp['orbe']}\\textdegree}}\n"
                f"{esc(texto_asp).strip()}\n\n"
            )
        return out

    _exactos_tex     = _fmt_asp(tens_raw.get("exactos", []))
    _estructural_tex = _fmt_asp(tens_raw.get("estructurales", []))

    tension_intro = (
        "Los aspectos aparecen organizados en dos niveles. "
        "Los aspectos exactos (orbe igual o menor a 1°) suelen notarse con más intensidad y frecuencia. "
        "Los aspectos estructurales tienen un orbe más amplio, pero siguen describiendo dinámicas importantes que se repiten a lo largo de la vida.\n\n"
    )

    tension_tex = ""

    tension_tex += (
        "\\vspace{0.8cm}\n"
        "\\Needspace{5\\baselineskip}\n"
        "\\subsubsection*{Aspectos exactos}\n"
    )

    if _exactos_tex.strip():
        tension_tex += _exactos_tex
    else:
        tension_tex += (
           "No aparecen aspectos exactos especialmente fuertes dentro del orbe definido para esta lectura. "
           "Eso no significa ausencia de tensión o profundidad, sino que gran parte de las dinámicas importantes de la carta se construyen de forma más amplia y progresiva. "
           "En este caso, cobran más importancia los aspectos estructurales y la combinación general de posiciones.\n\n"
        )

    tension_tex += (
        "\\vspace{0.8cm}\n"
        "\\Needspace{5\\baselineskip}\n"
        "\\subsubsection*{Aspectos estructurales}\n"
    )

    if _estructural_tex.strip():
        tension_tex += _estructural_tex
    else:
        tension_tex += (
            "No aparecen aspectos estructurales especialmente dominantes en esta carta. "
            "Por eso, la lectura se apoya más en otros factores como las casas, los ejes, la distribución de elementos y las áreas donde se agrupan varios planetas.\n\n"
        )
    
    stellium_tex = ""
    if stellium:
        stellium_tex = (
            "\\subsubsection*{Concentración de energía}\n\n"
            + esc(stellium).strip()
            + "\n\n"
        )

    tension_intro_tex = (
        "Los aspectos aparecen organizados en dos niveles. "
        "Los aspectos exactos (orbe igual o menor a 1°) suelen sentirse de forma más inmediata y constante en la vida cotidiana. "
        "Los aspectos estructurales tienen un orbe más amplio, pero siguen describiendo dinámicas importantes que se repiten a lo largo de la vida.\n\n"
    )

    grados_criticos_tex = ""
    if grados_criticos:
        grados_criticos_tex = (
            "\\subsubsection*{Grados finales de signo}\n"
            + esc(grados_criticos).strip()
            + "\n\n"
        )


    latex = f"""\\documentclass[11pt,a4paper]{{article}}\\usepackage[utf8]{{inputenc}}

\\usepackage[T1]{{fontenc}}
\\usepackage{{tgpagella}}
\\usepackage[spanish]{{babel}}
\\usepackage{{geometry}}
\\usepackage{{graphicx}}
\\usepackage{{booktabs}}
\\usepackage{{array}}
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

\\titleformat{{\\section}}{{\\Large\\bfseries\\color{{azulai}}}}{{}}{{0em}}{{}}[{{\\color{{azulai}}\\titlerule[0.5pt]\\nopagebreak[4]}}]
\\titlespacing*{{\\section}}{{0pt}}{{1.8em}}{{0.8em}}
\\titleformat{{\\subsection}}{{\\large\\bfseries\\color{{doradoai}}}}{{}}{{0em}}{{}}[{{\\nopagebreak[4]}}]
\\titlespacing*{{\\subsection}}{{0pt}}{{1.4em}}{{0.5em}}
\\titleformat{{\\subsubsection}}{{\\normalsize\\bfseries\\color{{grisai}}}}{{}}{{0em}}{{}}[{{\\nopagebreak[4]}}]
\\titlespacing*{{\\subsubsection}}{{0pt}}{{1.0em}}{{0.3em}}

\\pagestyle{{fancy}}\\fancyhf{{}}
\\rhead{{\\textcolor{{grisai}}{{\\small {nom_esc} — Arquitectura Interna}}}}
\\lhead{{\\textcolor{{grisai}}{{\\small Carta Natal Completa}}}}
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
  {{\\Huge\\bfseries\\color{{azulai}} Carta Natal Completa}}\\\\[0.5cm]
  {{\\large\\color{{grisai}} Arquitectura Interna}}\\\\[0.3cm]
  {{\\small\\itshape\\color{{grisai}} Un método para sostener cuerpo, energía y vida con coherencia}}\\\\[2cm]
  {{\\huge\\color{{doradoai}} {nom_esc}}}\\\\[1.5cm]
  {{\\Large {fecha_str} \\quad {hora_str}}}\\\\[0.3cm]
  {{\\Large {ciu_esc}}}\\\\[0.3cm]
  {{\\normalsize Lat: {lat:.4f}° \\quad Lon: {lon:.4f}° \\quad {utc_str}}}\\\\[0.3cm]
  {{\\normalsize Ascendente: {esc(asc['signo'])} {grado_a_dms(asc['grado'])} \\quad
    MC: {esc(mc['signo'])} {grado_a_dms(mc['grado'])}}}\\\\[2.5cm]
  \\vfill
  {{\\small Generado el {datetime.now().strftime("%d/%m/%Y")}}}
\\end{{titlepage}}

\\tableofcontents
\\newpage

% ── Rueda ─────────────────────────────────────────────────────────────────────
\\section{{Carta Natal}}
\\begin{{figure}}[h!]
  \\centering
  \\includegraphics[width=0.90\\textwidth]{{{ruta_rueda}}}
  \\caption{{Carta natal de {nom_esc} — {fecha_str} {hora_str} — {ciu_esc}}}
\\end{{figure}}

\\newpage

% ── Tabla de posiciones ───────────────────────────────────────────────────────
\\section{{Posiciones Planetarias}}

\\begin{{center}}
\\begin{{tabular}}{{llrrlll}}
  \\toprule
  \\textbf{{Planeta}} & \\textbf{{Signo}} & \\textbf{{Grado}} & \\textbf{{Casa}} &
  \\textbf{{Elemento}} & \\textbf{{R}} \\\\
  \\midrule
{tabla}
  \\bottomrule
\\end{{tabular}}
\\end{{center}}

\\vspace{{0.5cm}}
\\begin{{itemize}}
  \\item \\textbf{{Ascendente:}} {esc(asc['signo'])} {grado_a_dms(asc['grado'])}
  \\item \\textbf{{Medio Cielo:}} {esc(mc['signo'])} {grado_a_dms(mc['grado'])}
{nota_interceptados}\\end{{itemize}}

\\newpage

% ── Interpretación ────────────────────────────────────────────────────────────
\\section{{Interpretación — Arquitectura Interna}}

\\begin{{center}}
{{\\small\\itshape
No se trata de definirte. Se trata de observar cómo se organiza tu energía,\\
dónde puedes perder equilibrio y qué apoyos te ayudan a sostenerte.
}}
\\end{{center}}

\\vspace{{0.5cm}}

\\subsection{{1. Visión General}}

{esc(vision)}

\\vspace{{0.8cm}}
\\Needspace{{5\\baselineskip}}

\\subsection{{2. Ejes Principales}}

\\subsubsection*{{Sol en {esc(planetas.get('Sol',{}).get('signo',''))} — Casa {planetas.get('Sol',{}).get('casa','')}}}
{esc(ejes['sol'])}

\\subsubsection*{{Luna en {esc(planetas.get('Luna',{}).get('signo',''))} — Casa {planetas.get('Luna',{}).get('casa','')}}}
{esc(ejes['luna'])}

\\subsubsection*{{Ascendente {esc(asc['signo'])}}}
{esc(ejes['asc'])}

{grados_criticos_tex}
{interc_tex}

\\vspace{{0.8cm}}
\\Needspace{{5\\baselineskip}}

\\subsection{{3. Organización de la Energía}}

{esc(org)}

\\vspace{{0.8cm}}
\\Needspace{{5\\baselineskip}}

\\subsection{{4. Estructura y Tensión}}

{stellium_tex}

{esc(tension_intro_tex)}

{tension_tex}

\\vspace{{0.8cm}}
\\Needspace{{5\\baselineskip}}

\\subsection{{5. Sostén y Equilibrio}}

{esc(sost['quiron'])}

\\vspace{{0.3cm}}
{esc(sost['nodo'])}

\\vspace{{0.3cm}}
{esc(sost['regulacion'])}

\\vspace{{0.8cm}}
\\Needspace{{5\\baselineskip}}

\\subsection{{6. Orientación}}

\\subsubsection*{{Qué observar}}
{esc(orient['observar'])}

\\subsubsection*{{Qué puede desestabilizar}}
{esc(orient['desregula'])}

\\subsubsection*{{Qué estructura y sostiene}}
{esc(orient['sostiene'])}

\\subsubsection*{{Orientación práctica}}
{esc(orient['practica'])}

\\vspace{{1cm}}
\\begin{{center}}
{{\\small\\itshape\\color{{grisai}}
La astrología se usa aquí como lenguaje simbólico de observación, no como una definición de quién eres.\\\\
Esta interpretación es tu mapa de posibilidades, no tu destino fijo.
}}
\\end{{center}}

\\end{{document}}
"""
    return latex

# ─── PROGRAMA PRINCIPAL ───────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("   CARTA NATAL COMPLETA — Arquitectura Interna")
    print("=" * 60)
    print()

    nombre = input("Nombre completo: ").strip()
    if not nombre:
        print("El nombre no puede estar vacío."); sys.exit(1)

    while True:
        try:
            fecha_str = input("Fecha de nacimiento (DD/MM/AAAA): ").strip()
            dia, mes, año = map(int, fecha_str.split("/"))
            datetime(año, mes, dia); break
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
        carta = calcular_carta(año, mes, dia, hora, minuto, lat, lon, tz_name)
        print(f"  Ascendente: {carta['asc']['signo']} {grado_a_dms(carta['asc']['grado'])}")
        print(f"  Medio Cielo: {carta['mc']['signo']} {grado_a_dms(carta['mc']['grado'])}")
    except Exception as e:
        print(f"Error en cálculo astrológico: {e}"); sys.exit(1)

    aspectos = calcular_aspectos(carta["planetas"])
    print(f"  Aspectos calculados: {len(aspectos)}")
    if carta.get("interceptados"):
        for s, c in carta["interceptados"].items():
            print(f"  Signo interceptado: {s} en casa {c}")
    else:
        print("  Sin signos interceptados")

    nombre_f = nombre.replace(" ","_").replace("/","-")
    dir_sal  = os.path.dirname(os.path.abspath(__file__))
    ruta_base = os.path.join(dir_sal, nombre_f + "_AI")
    ruta_png  = ruta_base + "_rueda.png"
    ruta_tex  = ruta_base + ".tex"
    ruta_pdf  = ruta_base + ".pdf"

    print("  Dibujando rueda astrológica...")
    try:
        dibujar_rueda(carta, nombre, ruta_png)
        print(f"  Rueda guardada: {ruta_png}")
    except Exception as e:
        print(f"Error al dibujar la rueda: {e}"); sys.exit(1)

    print("  Generando interpretación Arquitectura Interna...")
    latex = generar_latex_ai(carta, nombre, año, mes, dia, hora, minuto,
                             ciudad, lat, lon, tz_name, ruta_png, aspectos)
    with open(ruta_tex, "w", encoding="utf-8") as f:
        f.write(latex)
    print(f"  LaTeX guardado: {ruta_tex}")

    print("  Compilando PDF...")
    try:
        tex_nombre = os.path.basename(ruta_tex)
        for _ in range(2):
            resultado = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", tex_nombre],
                capture_output=True, text=True, timeout=90, cwd=dir_sal
            )
        if os.path.exists(ruta_pdf):
            print(f"  PDF generado: {ruta_pdf}")
        else:
            print("  Error: no se generó el PDF.")
            log_path = ruta_base + ".log"
            if os.path.exists(log_path):
                print(f"  Revisa el log en: {log_path}")
                # Mostrar las últimas líneas relevantes del log
                with open(log_path, encoding="latin-1", errors="replace") as f:
                    lineas = f.readlines()
                errores = [l for l in lineas if l.startswith("!") or "Error" in l]
                if errores:
                    print("  Errores encontrados:")
                    for e in errores[:10]:
                        print("   ", e.rstrip())
            else:
                print("  Salida de pdflatex:")
                print(resultado.stdout[-2000:] if resultado.stdout else "(vacía)")
    except subprocess.TimeoutExpired:
        print("  Timeout al compilar LaTeX (más de 90 s).")
    except FileNotFoundError:
        print("  pdflatex no encontrado.")
        print("  En Windows instala MiKTeX: https://miktex.org/download")
        print("  En Linux/WSL: sudo apt install texlive-full")

    for ext in [".aux",".toc",".out"]:
        try: os.remove(ruta_base + ext)
        except FileNotFoundError: pass
    if os.path.exists(ruta_pdf):
        try: os.remove(ruta_base + ".log")
        except FileNotFoundError: pass

    print()
    print("=" * 60)
    print(f"  Carta Natal Completa de {nombre} generada.")
    print(f"  Ficheros en: {dir_sal}")
    print(f"    - {nombre_f}_AI_rueda.png")
    print(f"    - {nombre_f}_AI.pdf")
    print("=" * 60)

if __name__ == "__main__":
    main()
