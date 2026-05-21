#!/usr/bin/env python3
"""
2. Luna, Casa 4 y Casa 6 — Arquitectura Interna
Interpreta la función emocional (Luna), la raíz interna (Casa 4)
y la regulación cotidiana (Casa 6) de la carta natal.
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
    "Aries":"Marte","Tauro":"Venus","Géminis":"Mercurio","Cáncer":"Luna",
    "Leo":"Sol","Virgo":"Mercurio","Libra":"Venus","Escorpio":"Plutón",
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
COLORES_PLANETA = {
    "Sol":"#CC2200","Marte":"#CC2200","Júpiter":"#CC2200",
    "Venus":"#2E7D32","Saturno":"#2E7D32",
    "Mercurio":"#E67E00","Urano":"#E67E00",
    "Luna":"#1A5FA8","Neptuno":"#1A5FA8","Plutón":"#1A5FA8",
    "Quirón":"#7B2D8B","Lilith":"#7B2D8B",
    "Nodo Norte":"#888800","Nodo Sur":"#888800",
}


# ─── TEXTOS: LUNA POR SIGNO (función emocional) ───────────────────────────────

LUNA_SIGNO = {

"Aries": (
    "Cuando algo te afecta, tu cuerpo reacciona antes de que tengas tiempo de pensarlo.\n\n"

    "Primero aparece tensión y después necesidad de hacer algo con eso. "
    "Permanecer demasiado tiempo inmóvil con una emoción dentro suele aumentar la irritación, "
    "porque necesitas movimiento para volver a sentir espacio interno.\n\n"

    "La intensidad emocional puede subir rápido, pero también bajar rápido cuando encuentra una vía de salida clara. "
    "El problema aparece cuando no puedes actuar, decidir o moverte. "
    "Entonces la energía empieza a quedarse atrapada dentro y, cuanto más tiempo permanece así, "
    "más difícil resulta bajar el nivel de activación.\n\n"

    "La regulación suele aparecer cuando existe dirección, movimiento y posibilidad de actuar sobre lo que está ocurriendo. "
    "En cambio, las situaciones de bloqueo, exceso de límite o sensación de no tener margen de acción "
    "tienden a aumentar rápidamente la tensión interna."
),

"Tauro": (
    "Los procesos emocionales necesitan tiempo para asentarse. "
    "Lo que te afecta no desaparece rápido: se queda dentro mientras tu cuerpo intenta procesarlo a su ritmo.\n\n"

    "Muchas veces notas antes la tensión física que la emoción en sí. "
    "Puede sentirse como cansancio, necesidad de descanso, rigidez o sensación de pesadez acumulada.\n\n"

    "Los cambios bruscos suelen desorganizarte más de lo que parece desde fuera, "
    "porque necesitas continuidad para recolocarte internamente. "
    "Cuando existe demasiada presión para acelerar procesos emocionales, "
    "la respuesta suele ser todavía más resistencia.\n\n"

    "La estabilidad, los ritmos previsibles y la sensación de seguridad concreta te ayudan a recuperar regulación. "
    "En cambio, los cambios repentinos, la presión externa o la sensación de perder estabilidad "
    "tienden a generar desorganización emocional."
),

"Géminis": (
    "Necesitas entender y nombrar lo que sientes para poder integrarlo.\n\n"

    "Cuando algo no puede hablarse, escribirse o pensarse, se queda dando vueltas dentro. "
    "La saturación emocional suele aparecer entonces como ruido mental: pensamientos constantes, dispersión "
    "o necesidad de cambiar de foco continuamente.\n\n"

    "Puede costarte permanecer mucho tiempo dentro de una misma emoción sin moverte hacia otra cosa. "
    "Y cuando acumulas demasiadas experiencias sin expresarlas, "
    "tu cuerpo empieza a responder con inquietud y dificultad para detenerse.\n\n"

    "La regulación mejora cuando puedes poner palabras a lo que ocurre, compartirlo o darle forma mental. "
    "En cambio, el silencio sostenido, el aislamiento mental o guardarte demasiado tiempo lo que te pasa "
    "tienden a aumentar la saturación interna."
),

"Cáncer": (
    "Tu mundo emocional absorbe mucho más del entorno de lo que suele percibirse desde fuera.\n\n"

    "El estado de las personas cercanas, la tensión en un espacio o el clima emocional de una relación "
    "te afectan rápidamente aunque no siempre lo expreses. "
    "Muchas veces el cansancio aparece sin entender del todo por qué, "
    "y la causa suele estar en haber sostenido demasiada carga emocional alrededor.\n\n"

    "Tu memoria emocional es profunda y persistente. "
    "Hay experiencias que pueden seguir activándose dentro mucho tiempo después de haber ocurrido.\n\n"

    "Cuando no existe un lugar donde sentir seguridad emocional, "
    "tu cuerpo suele notarlo enseguida. "
    "La regulación aparece más fácilmente cuando hay intimidad, refugio y vínculos donde puedes bajar la guardia. "
    "En cambio, la tensión afectiva constante, los cambios emocionales continuos o la sensación de no tener dónde descansar internamente "
    "tienden a desgastarte rápidamente."
),

"Leo": (
    "Necesitas poder expresar lo que sientes para mantener vitalidad emocional.\n\n"

    "Cuando lo que ocurre dentro no encuentra espacio, reconocimiento o respuesta, "
    "la tensión empieza a crecer poco a poco. "
    "La sensación de no ser visto puede afectarte mucho más profundamente de lo que aparentas desde fuera.\n\n"

    "Si pasas demasiado tiempo sintiendo que tienes que esconder una parte de ti, "
    "la energía empieza a apagarse y el cuerpo pierde apertura.\n\n"

    "No necesitas atención constante. "
    "Necesitas sentir que puedes existir emocionalmente sin tener que reducirte o contener partes importantes de lo que eres.\n\n"

    "La regulación mejora cuando existe expresión auténtica, creatividad y reconocimiento genuino. "
    "En cambio, la indiferencia emocional, la frialdad o la sensación de no encontrar acogida afectiva "
    "tienden a aumentar el desgaste interno."
),

"Virgo": (
    "Tiendes a analizar lo que sientes antes de terminar de sentirlo.\n\n"

    "Tu mente intenta entender rápidamente si la emoción tiene sentido, "
    "si es razonable o si debería estar ocurriendo. "
    "Muchas veces, lo que no consigues procesar emocionalmente termina desplazándose hacia el cuerpo.\n\n"

    "La tensión suele aparecer entonces como cansancio, sobrecarga mental o sensación de no llegar a todo. "
    "También puede existir una tendencia constante a corregirte internamente sin darte cuenta.\n\n"

    "La regulación mejora cuando existe orden simple, estructura cotidiana y atención concreta al cuerpo. "
    "En cambio, el exceso de exigencia, el sobreanálisis o la sensación de que nunca es suficiente "
    "tienden a aumentar la presión interna."
),

"Libra": (
    "Tu estado emocional cambia mucho según cómo estén tus vínculos cercanos.\n\n"

    "Cuando existe armonía y reciprocidad, aparece sensación de estabilidad interna. "
    "Cuando una relación importante entra en tensión, lo notas rápidamente.\n\n"

    "Muchas veces intentas sostener el equilibrio evitando conflicto o adaptándote más de la cuenta, "
    "pero lo que no expresas termina acumulándose dentro.\n\n"

    "Tu cuerpo suele responder al conflicto con bloqueo, indecisión o agotamiento emocional.\n\n"

    "La regulación mejora cuando hay claridad, equilibrio y reciprocidad en los vínculos. "
    "En cambio, la tensión sostenida, la ambigüedad afectiva o las relaciones desequilibradas "
    "tienden a alterar rápidamente el equilibrio interno."
),

"Escorpio": (
    "No muestras fácilmente todo lo que sientes.\n\n"

    "Hay emociones que puedes sostener dentro durante muchísimo tiempo sin que casi nadie lo note. "
    "Tiendes a observar, contener y procesar emocionalmente en privado.\n\n"

    "El problema es que la intensidad sigue acumulándose aunque no salga hacia fuera. "
    "Y cuando algo rompe la sensación de control emocional —una traición, una pérdida o una exposición inesperada— "
    "puede aparecer una intensidad difícil de contener.\n\n"

    "Tu cuerpo suele registrar esa acumulación como tensión constante o dificultad para relajarse del todo.\n\n"

    "La regulación mejora cuando existe intimidad real, confianza profunda y sensación de seguridad emocional. "
    "En cambio, la manipulación, la traición o sentirte expuesto sin protección "
    "tienden a activar rápidamente mecanismos de defensa."
),

"Sagitario": (
    "Necesitas sentir que lo que estás viviendo tiene dirección.\n\n"

    "Cuando una emoción encuentra sentido o movimiento, puedes atravesarla mucho mejor. "
    "El problema aparece cuando sientes algo que no sabes hacia dónde va "
    "o que parece no conducir a ningún lugar.\n\n"

    "Entonces suele aparecer inquietud, necesidad de escapar, cambiar de aire o salir de la situación de alguna manera. "
    "Tu cuerpo necesita espacio, movimiento y sensación de horizonte.\n\n"

    "Cuando pasas demasiado tiempo sintiendo que no existe libertad o amplitud suficiente, "
    "la activación empieza a acumularse.\n\n"

    "La regulación mejora cuando existe dirección, expansión y posibilidad de avanzar. "
    "En cambio, la sensación de límite, encierro o falta de sentido "
    "tiende a aumentar rápidamente la inquietud interna."
),

"Capricornio": (
    "No muestras fácilmente lo que sientes.\n\n"

    "Antes de abrirte emocionalmente, una parte de ti evalúa si es seguro hacerlo. "
    "Muchas veces acabas procesando en soledad lo que te ocurre.\n\n"

    "Puedes sostener tensión emocional durante muchísimo tiempo sin derrumbarte, "
    "pero eso no significa que no exista un coste. "
    "El cuerpo suele registrar la carga acumulada como cansancio sostenido, rigidez o dificultad para relajarse.\n\n"

    "La desregulación suele aparecer más como agotamiento que como explosión emocional.\n\n"

    "La regulación mejora cuando existe estructura, estabilidad y sensación de poder sostener la propia vida. "
    "En cambio, la sobrecarga prolongada, el exceso de responsabilidad o sentir que no puedes bajar la guardia "
    "tienden a desgastarte profundamente."
),

"Acuario": (
    "Tiendes a observar lo que sientes desde cierta distancia.\n\n"

    "Muchas veces entiendes emocionalmente lo que te ocurre antes de terminar de habitarlo. "
    "Eso puede darte claridad, pero también hacer que tus propias necesidades emocionales lleguen tarde.\n\n"

    "Cuando la intensidad emocional supera cierto límite, "
    "puede aparecer desconexión repentina. "
    "Tu cuerpo suele pedir distancia antes incluso de que seas plenamente consciente de la saturación.\n\n"

    "Necesitas espacio interno y margen para procesar lo que sientes a tu manera.\n\n"

    "La regulación mejora cuando existe autonomía, tiempo a solas y libertad emocional. "
    "En cambio, la invasión emocional, el exceso de intensidad o sentirte sin escapatoria dentro de dinámicas ajenas "
    "tienden a generar desconexión y retirada."
),

"Piscis": (
    "Absorbes mucho más emocionalmente de lo que aparentas.\n\n"

    "Los estados emocionales de otras personas, la atmósfera de un lugar o incluso cosas que nadie ha dicho "
    "pueden quedarse dentro de ti sin que siempre seas consciente de ello.\n\n"

    "Muchas veces aparece saturación sin tener claro exactamente qué la provocó. "
    "Tu cuerpo suele responder entonces con cansancio difuso, necesidad de retirarte o sensación de estar demasiado abierto emocionalmente.\n\n"

    "Necesitas momentos reales de silencio, descanso y descarga emocional. "
    "Cuando pasas demasiado tiempo absorbiendo sin vaciar, "
    "la sobrecarga empieza a acumularse silenciosamente.\n\n"

    "La regulación mejora cuando existen espacios de retirada, descanso profundo y límites claros. "
    "En cambio, los ambientes emocionalmente cargados, el exceso de exposición o la falta de separación con el entorno "
    "tienden a generar saturación interna."
),

}

# ─── TEXTOS: LUNA POR CASA ────────────────────────────────────────────────────

LUNA_CASA = {

1: (
    "Lo que sientes suele hacerse visible rápidamente. Tu cuerpo, el tono con el que hablas o tu forma de reaccionar muestran muchas veces cómo estás antes incluso de haber terminado de darte cuenta del todo. "
    "Las personas cercanas suelen percibir enseguida cuándo algo te afecta. Eso puede darte sensación de autenticidad y conexión con lo que expresas, pero también hacer que a veces sientas demasiada exposición emocional, como si fuera difícil ocultar lo que te ocurre por dentro. "
    "Cuando pasas mucho tiempo intentando contener lo que sientes, la tensión suele terminar saliendo igualmente de alguna manera, aunque intentes mantenerla bajo control. "
    "Te ayuda poder expresar lo que te pasa con naturalidad, sin sentir que tienes que vigilar constantemente cómo te muestras o cuánto enseñas de ti. "
    "En cambio, contenerte continuamente o sentir que no puedes mostrar cómo estás suele hacer que la tensión interna vaya creciendo poco a poco."
),

2: (
    "Tu estabilidad emocional está muy ligada a la sensación de seguridad concreta. Cuando aparece incertidumbre económica, cambios materiales o dudas sobre tu propio valor, todo dentro suele moverse rápidamente. "
    "No se vive solo como una preocupación mental. Puede aparecer tensión física, necesidad de controlar más las cosas o sensación de perder suelo interno. "
    "Necesitas cierta continuidad y estabilidad para relajarte de verdad. Cuando todo cambia demasiado rápido, puedes permanecer en alerta aunque desde fuera parezca que sigues funcionando con normalidad. "
    "Te ayuda sentir que existe una base suficiente sobre la que apoyarte y que la vida tiene cierta estabilidad. En cambio, las pérdidas, la inseguridad o sentir que no tienes dónde sostenerte suelen generar mucho desorden interno."
),

3: (
    "Necesitas poner palabras a lo que sientes para poder aclararlo dentro de ti. Cuando algo no puede hablarse, escribirse o expresarse, suele quedarse dando vueltas en la cabeza durante mucho tiempo. "
    "Muchas veces la emoción acaba transformándose en pensamiento repetitivo, ruido mental o necesidad constante de entender qué está pasando. "
    "El entorno cotidiano tiene además un impacto muy fuerte sobre cómo te sientes: las conversaciones, los mensajes, los intercambios y los vínculos cercanos te afectan más de lo que suele parecer. "
    "Cuando acumulas demasiadas cosas sin expresarlas, la mente rara vez consigue descansar del todo. "
    "Te ayuda hablar, escribir o sentir que alguien realmente te escucha. En cambio, guardar demasiado tiempo lo que te pasa o no encontrar espacio para expresarlo suele aumentar mucho la saturación interna."
),

4: (
    "Tu mundo emocional está profundamente unido a la sensación de hogar y pertenencia. Los cambios familiares, las tensiones en casa o la pérdida de referencias afectivas te afectan mucho más de lo que suele verse desde fuera. "
    "Cuando algo te descoloca, tiendes a ir hacia dentro: buscar refugio, aislarte un poco o volver a lo conocido para recuperar sensación de seguridad. "
    "Necesitas sentir que existe un lugar donde puedes bajar la guardia de verdad. Cuando esa sensación de refugio falta, el cuerpo permanece mucho más tiempo en tensión. "
    "Te ayuda la intimidad, la estabilidad emocional y sentir que tienes una base a la que volver. En cambio, la tensión familiar, la pérdida de seguridad afectiva o sentir que no tienes refugio suele hacer que aparezca mucha desprotección interna."
),

5: (
    "Necesitas expresar lo que sientes para mantenerte vivo por dentro. La creatividad, el juego, el disfrute o la posibilidad de ser espontáneo no son algo superficial para ti: forman parte de lo que te ayuda a sentirte bien emocionalmente. "
    "Cuando pasas demasiado tiempo reprimiendo esa parte de ti, la energía empieza a acumularse y pueden aparecer irritabilidad, vacío o sensación de desconexión contigo mismo. "
    "Tu cuerpo suele apagarse cuando la vida pierde espacio para el disfrute auténtico o para la expresión personal. "
    "Te ayuda crear, disfrutar y sentir que puedes expresarte libremente. En cambio, la exigencia constante, la represión emocional o sentir que no tienes espacio para ser quien eres suele desgastarte profundamente."
),

6: (
    "Tu cuerpo nota rápidamente aquello que emocionalmente se queda dentro demasiado tiempo. Lo que no expresas o no consigues colocar acaba apareciendo muchas veces como cansancio, tensión o alteración del ritmo cotidiano. "
    "La rutina tiene un impacto muy directo sobre cómo te sientes. Cuando pierdes hábitos, descanso o cierta continuidad corporal, todo dentro empieza a moverse más fácilmente. "
    "Necesitas una vida cotidiana relativamente estable para sentirte bien de verdad, porque el cuerpo necesita orden, descanso y cuidado para poder sostener lo que vas viviendo. "
    "Te ayuda tener pequeños hábitos, descanso suficiente y momentos reales de cuidado corporal. En cambio, la sobrecarga, el desorden diario o acumular tensión durante demasiado tiempo suele terminar afectándote rápidamente."
),

7: (
    "Tus relaciones cercanas influyen muchísimo en cómo te sientes por dentro. Cuando un vínculo importante está bien, suele aparecer mucha más calma y estabilidad. Cuando entra en tensión, lo notas enseguida. "
    "Muchas veces intentas sostener la relación incluso cuando emocionalmente ya casi no quedan recursos disponibles, porque la necesidad de armonía puede hacer que postergues durante demasiado tiempo lo que tú necesitas. "
    "El conflicto sostenido suele dejarte cansado, bloqueado o con dificultad para relajarte de verdad. "
    "Te ayuda sentir reciprocidad, claridad emocional y estabilidad en los vínculos. En cambio, las relaciones desequilibradas, la ambigüedad afectiva o vivir demasiado tiempo en conflicto suele generar mucho desgaste interno."
),

8: (
    "Las emociones superficiales rara vez te movilizan demasiado. Lo que realmente te afecta suelen ser las experiencias intensas: la intimidad profunda, las pérdidas, las crisis o los vínculos donde hay algo importante en juego. "
    "Tiendes a vivir muchas emociones intensamente en privado y, cuando no existe un espacio seguro para atravesar todo eso, la tensión empieza a acumularse dentro poco a poco. "
    "Hay experiencias que puedes sostener en silencio durante muchísimo tiempo sin que casi nadie lo note. "
    "Te ayuda sentir confianza profunda, intimidad real y seguridad emocional. En cambio, la traición, las pérdidas emocionales o atravesar demasiada intensidad sin apoyo suele dejar estados internos difíciles de relajar."
),

9: (
    "Necesitas encontrar sentido a lo que estás viviendo. Cuando comprendes hacia dónde te lleva una experiencia, puedes atravesarla con mucha más amplitud emocional. "
    "La dificultad aparece cuando algo duele y no consigues encontrar ningún significado posible. Ahí puede surgir inquietud, necesidad de escapar o sensación de no poder sostener lo que estás sintiendo. "
    "Tu cuerpo suele pedir movimiento, aire o distancia cuando siente que no existe suficiente libertad emocional. "
    "Te ayuda sentir dirección, comprensión y horizonte. En cambio, el vacío, el encierro o vivir algo que no consigues colocar dentro de una visión más amplia suele aumentar rápidamente la inquietud interna."
),

10: (
    "Lo que ocurre en tu vida profesional o pública te afecta emocionalmente mucho más de lo que aparentas. El reconocimiento puede darte una sensación profunda de estabilidad interna, mientras que la crítica o la exposición pueden impactarte muchísimo aunque no siempre lo muestres. "
    "Muchas veces la sensación de valor personal se conecta con cómo sientes que ocupas tu lugar frente al mundo. "
    "Cuando desaparece la dirección o el reconocimiento, la energía emocional puede caer muy rápido. "
    "Te ayuda sentir propósito, coherencia y reconocimiento genuino. En cambio, la exposición excesiva, la sensación de fracaso o la inseguridad pública suele afectar profundamente tu estabilidad emocional."
),

11: (
    "Necesitas sentir que formas parte de algo más amplio. Cuando existe conexión con amistades, grupos o proyectos compartidos, tu mundo emocional encuentra mucha más estabilidad y sostén. "
    "El aislamiento suele afectarte más profundamente de lo que parece desde fuera, porque necesitas intercambio, red y sensación de pertenencia. "
    "Cuando esa conexión desaparece, puede aparecer vacío emocional o sensación de desconexión interna. "
    "Te ayuda sentir comunidad, amistad y participación compartida. En cambio, el aislamiento, la desconexión o sentir que no tienes lugar dentro de un grupo suele generar mucha sensación de separación emocional."
),

12: (
    "Muchas de tus emociones se mueven dentro de ti antes incluso de que consigas entenderlas del todo. A veces aparece cansancio, saturación o tristeza sin una causa completamente clara. "
    "Necesitas períodos reales de silencio y retirada para vaciar todo lo que se va acumulando dentro. Cuando pasas demasiado tiempo expuesto a ruido, demandas o estímulos externos, tu mundo interior empieza a saturarse aunque desde fuera parezca que sigues funcionando. "
    "Tu cuerpo suele necesitar descanso profundo con más frecuencia de la que imaginas. "
    "Te ayuda tener momentos de soledad elegida, silencio y suficiente espacio interior. En cambio, el exceso de exposición, el ruido constante o no disponer de tiempo para desconectar suele generar mucha saturación emocional."
),
}

# ─── TEXTOS: CASA 4 — SIGNO EN CÚSPIDE ───────────────────────────────────────

CASA4_SIGNO = {

"Aries": (
    "Cuando algo amenaza tu estabilidad interna, reaccionas rápidamente. El impulso suele ser actuar, resolver o moverte, porque permanecer demasiado tiempo dentro de una situación tensa sin poder hacer nada con ella suele aumentar mucho la tensión. "
    "Necesitas sentir que existe margen de acción frente a lo que ocurre. Cuando aparecen límites, dependencia o sensación de no tener salida, el cuerpo entra rápidamente en alerta. "
    "La autonomía tiene un impacto enorme sobre tu sensación de seguridad interna y, cuanto más espacio sientes para decidir y moverte, más fácil resulta recuperar estabilidad. "
    "Te ayuda poder actuar, decidir y sentir movimiento interno. En cambio, el bloqueo, la inmovilidad o sentir que no puedes salir de una situación suele aumentar rápidamente la tensión."
),

"Tauro": (
    "Necesitas estabilidad para sentir seguridad interna. Los cambios bruscos en el hogar, en las condiciones de vida o en la sensación de seguridad te afectan mucho más de lo que suele verse desde fuera. "
    "Cuando algo importante cambia demasiado rápido, puede aparecer una sensación muy profunda de haber perdido suelo. "
    "Tiendes a buscar lo conocido, la repetición y cierta continuidad para volver a sentir calma. Por eso no suele resultar fácil relajarte cuando todo alrededor cambia constantemente. "
    "Te ayuda la calma, la estabilidad y sentir que existe un ritmo previsible en tu vida. En cambio, la incertidumbre, los cambios repentinos o sentir que pierdes tu base suele generar mucha inseguridad interna."
),

"Géminis": (
    "Tu estabilidad interna depende mucho de entender qué está pasando a tu alrededor. Cuando aparecen silencios ambiguos, confusión o situaciones poco claras, la mente empieza a acelerarse intentando encontrar una explicación. "
    "Necesitas hablar, preguntar o poner palabras a lo que ocurre para recuperar cierta calma. Muchas veces analizas las situaciones antes incluso de terminar de sentirlas por completo. "
    "Cuando pasas demasiado tiempo intentando comprender algo sin conseguir claridad, el cuerpo empieza a tensarse y la inquietud mental aumenta cada vez más. "
    "Te ayuda la comunicación clara, las conversaciones honestas y sentir que existe comprensión mutua. En cambio, la ambigüedad, los silencios prolongados o la sensación de confusión emocional suele generar mucho desorden interno."
),

"Cáncer": (
    "Tu mundo interno responde profundamente al clima emocional del entorno cercano. Cuando existe tensión en casa, en la familia o en las personas que sientes como propias, el cuerpo suele notarlo enseguida. "
    "Necesitas sentir que existe un lugar emocionalmente seguro donde puedas bajar la guardia de verdad. Cuando aparece desbordamiento emocional, tiendes a buscar refugio en lo conocido para recuperar sensación de protección. "
    "Volver a lo familiar suele ayudarte a sentir estabilidad otra vez. "
    "Te ayuda la intimidad, la cercanía emocional y sentir que tienes un refugio real. En cambio, la inestabilidad afectiva, la tensión familiar o sentir que no tienes dónde apoyarte suele mantenerte en alerta durante demasiado tiempo."
),

"Leo": (
    "Necesitas sentir calidez emocional dentro de tu espacio íntimo. Cuando no sientes que te ven, te valoran o te reciben emocionalmente, algo dentro empieza a apagarse aunque externamente sigas funcionando. "
    "La frialdad emocional suele afectarte mucho más de lo que aparentas, porque necesitas sentir que puedes existir emocionalmente sin reducirte ni esconder partes importantes de ti. "
    "Cuando pasas demasiado tiempo sintiendo indiferencia emocional alrededor, la sensación de seguridad interna empieza a resentirse poco a poco. "
    "Te ayuda el afecto claro, el reconocimiento genuino y sentir calidez emocional en tu entorno cercano. En cambio, la frialdad, la indiferencia o sentir que no tienes un lugar emocional real suele desgastar profundamente tu estabilidad."
),

"Virgo": (
    "Cuando aparece sensación de desorden dentro de ti, muchas veces intentas recuperar estabilidad organizando algo fuera. Ordenar, limpiar, resolver tareas o estructurar el entorno puede ayudarte a bajar momentáneamente la tensión interna. "
    "La dificultad aparece cuando pasas demasiado tiempo intentando corregir lo externo sin terminar de entrar en lo que realmente te está ocurriendo por dentro. "
    "Tu sensación de seguridad aumenta cuando la vida cotidiana tiene cierto orden y funcionalidad. Cuando todo alrededor se vuelve caótico, el cuerpo entra rápidamente en sobrecarga. "
    "Te ayuda sentir estructura simple, orden y claridad en lo cotidiano. En cambio, el caos, la sobreexigencia o sentir que nunca llegas a todo suele generar mucha tensión interna."
),

"Libra": (
    "Tu estabilidad interna depende muchísimo de cómo estén tus vínculos cercanos. Cuando existe armonía en las relaciones importantes, resulta mucho más fácil sentir calma y equilibrio por dentro. "
    "Cuando aparece conflicto sostenido, desequilibrio emocional o tensión relacional, el cuerpo lo registra rápidamente. "
    "Muchas veces intentas sostener la paz adaptándote más de lo que realmente puedes, pero lo que callas o postergas termina acumulándose dentro. "
    "Te ayuda la armonía, la reciprocidad y sentir equilibrio emocional en las relaciones. En cambio, el conflicto constante, la tensión vincular o sentir que tienes que adaptarte continuamente suele generar mucho agotamiento interno."
),

"Escorpio": (
    "Percibes muy rápido lo que ocurre debajo de la superficie. Las tensiones no dichas, las emociones contenidas o las dinámicas ocultas te afectan incluso cuando nadie las nombra. "
    "Eso hace que muchas veces permanezcas en vigilancia aunque externamente todo parezca tranquilo. "
    "Necesitas sentir confianza profunda para relajarte de verdad. Cuando percibes manipulación, secretos o falta de honestidad emocional, el cuerpo vuelve rápidamente al estado de alerta. "
    "Te ayuda la intimidad real, la honestidad emocional y la sensación de confianza profunda. En cambio, la manipulación, las tensiones ocultas o sentir amenaza emocional suele activar mucha intensidad interna."
),

"Sagitario": (
    "Necesitas sentir que tu vida tiene dirección para experimentar estabilidad interna. Cuando existe horizonte, expansión o sensación de crecimiento, tu mundo interno se sostiene mucho mejor. "
    "La dificultad aparece cuando la vida empieza a sentirse demasiado estrecha, repetitiva o sin sentido. Entonces puede surgir inquietud, necesidad de escapar o sensación de encierro interno. "
    "Muchas veces intentas recuperar estabilidad tomando distancia, moviéndote o buscando aire y perspectiva. "
    "Te ayuda la libertad, el movimiento y sentir que existe propósito en lo que vives. En cambio, sentir límites constantes, falta de salida o vivir algo que no tiene sentido para ti suele aumentar rápidamente la tensión interna."
),

"Capricornio": (
    "Muy pronto apareció la necesidad de sostenerte emocionalmente con muy poco apoyo. Muchas veces resulta más fácil resistir que pedir ayuda, porque la sensación de seguridad suele estar muy ligada a sentir que puedes hacerte cargo de lo que venga. "
    "La dificultad aparece cuando sostienes demasiado peso durante demasiado tiempo antes de reconocer que también necesitas apoyo y descanso. "
    "El cuerpo suele acumular muchísimo cansancio antes de detenerse realmente. "
    "Te ayuda sentir estructura, estabilidad y cierta sensación de capacidad interna. En cambio, la sobrecarga prolongada, el exceso de responsabilidad o sentir que todo depende de ti suele desgastar profundamente la energía."
),

"Acuario": (
    "Existe una parte de ti que observa lo que siente desde cierta distancia. Muchas veces entiendes emocionalmente lo que ocurre antes de terminar de habitarlo por completo. "
    "Necesitas bastante espacio interno para sentir seguridad y estabilidad emocional. Cuando los vínculos se vuelven demasiado invasivos o absorbentes, el cuerpo empieza a retirarse aunque emocionalmente sigas presente. "
    "La independencia tiene muchísimo peso en tu sensación de estabilidad interna. "
    "Te ayuda la autonomía, el espacio personal y sentir libertad emocional. En cambio, la invasión emocional, la dependencia excesiva o sentir que pierdes espacio interno suele generar desconexión y tensión."
),

"Piscis": (
    "Tu mundo interno absorbe muchísimo del entorno. Las emociones ajenas, la atmósfera de un lugar o incluso tensiones que nadie expresa pueden quedarse dentro sin que te des cuenta inmediatamente. "
    "Cuando pasas demasiado tiempo en ambientes confusos o emocionalmente cargados, la sensación de estabilidad empieza a diluirse poco a poco. "
    "Muchas veces necesitas retirarte, descansar o aislarte un tiempo para volver a sentir claridad interna. "
    "No siempre necesitas entender exactamente qué te ocurre para empezar a sentirte mejor. A veces simplemente necesitas silencio, descanso y menos exposición emocional alrededor. "
    "Te ayudan los límites claros, los espacios de retiro y el descanso profundo. En cambio, la saturación emocional, los ambientes caóticos o el exceso de exposición suele generar muchísima sobrecarga interna."
),

}

# ─── TEXTOS: CASA 6 — SIGNO EN CÚSPIDE ───────────────────────────────────────

CASA6_SIGNO = {

"Aries": (
    "Necesitas movimiento para sentirte bien. Cuando pasas demasiado tiempo acumulando tensión sin descargarla físicamente, el cuerpo empieza a tensarse muy rápido. "
    "Primero suele aparecer irritación, después impaciencia y más tarde la sensación de que cualquier cosa molesta más de lo normal. "
    "Pensar más rara vez resuelve ese exceso de intensidad. Lo que realmente ayuda es mover el cuerpo y darle salida a lo que se ha ido acumulando dentro. "
    "El movimiento físico tiene un impacto directo sobre cómo te sientes. Cuando no puedes moverte —por cansancio, enfermedad o bloqueo— la tensión empieza a quedarse atrapada dentro. "
    "Te ayuda la acción física, el movimiento y poder descargar corporalmente lo que vas acumulando. En cambio, la inmovilidad, contener demasiado tiempo lo que sientes o sentirte bloqueado suele aumentar rápidamente la tensión interna."
),

"Tauro": (
    "Tu cuerpo necesita estabilidad y repetición para sentirse seguro. Los cambios bruscos en horarios, sueño, alimentación o rutina te afectan mucho más de lo que suele verse desde fuera. "
    "Cuando pierdes continuidad, todo tarda bastante tiempo en volver a relajarse del todo, porque necesitas ritmos previsibles para sentir verdadera calma corporal. "
    "La repetición no funciona como una limitación para ti, sino como una forma de sostén. "
    "Tu cuerpo responde especialmente bien a lo constante, a lo simple y a aquello que puede mantenerse en el tiempo sin exceso de exigencia. "
    "Te ayudan las rutinas estables, el descanso regular y los hábitos sostenidos. En cambio, el desorden, los cambios repentinos o la sensación de inestabilidad cotidiana suele generar mucha tensión física y emocional."
),

"Géminis": (
    "Necesitas movimiento mental y estímulo constante para sentirte despierto por dentro. Cuando falta variedad, conversación o aprendizaje, la mente empieza a girar sobre sí misma. "
    "La dificultad no suele ser falta de energía, sino demasiadas cosas abiertas al mismo tiempo. Puedes pasar días con muchísima actividad mental mientras el cuerpo queda completamente en segundo plano. "
    "La sobrecarga suele aparecer como inquietud, dificultad para desconectar o sensación de que la mente nunca termina de apagarse del todo. "
    "Necesitas alternar estímulo y pausa de forma mucho más consciente de lo que imaginas. "
    "Te ayudan la variedad, el aprendizaje y sentir movimiento mental con cierto orden. En cambio, el exceso de estímulos, la dispersión constante o no desconectar nunca suele saturarte rápidamente."
),

"Cáncer": (
    "Tu cuerpo y tu estado emocional están profundamente unidos. Cuando algo te afecta emocionalmente, el cuerpo suele notarlo enseguida. "
    "La digestión, el descanso, la energía o la sensación de agotamiento cambian rápidamente según cómo estén tus vínculos cercanos y el clima emocional que te rodea. "
    "Necesitas sentir cuidado y cierta seguridad emocional para sentirte bien físicamente de verdad. "
    "Los pequeños rituales cotidianos tienen muchísimo impacto sobre ti: la comida, el descanso, el hogar o la sensación de refugio. "
    "Cuando pasas demasiado tiempo sosteniendo tensión emocional, el cuerpo termina expresándolo de alguna manera. "
    "Te ayudan el cuidado cotidiano, la intimidad y sentir hogar alrededor. En cambio, la tensión relacional, la falta de descanso emocional o los ambientes afectivamente inestables suele desgastar rápidamente tu energía."
),

"Leo": (
    "Tu energía cotidiana necesita algo que sientas verdaderamente propio. Cuando toda la vida se reduce a obligación, rutina o gestión, algo dentro empieza a apagarse poco a poco. "
    "Puedes seguir funcionando durante mucho tiempo, pero sin sensación real de vitalidad. "
    "Necesitas espacios donde puedas expresarte, crear o sentir conexión auténtica contigo. "
    "Cuando pasas demasiado tiempo lejos de esa parte interna, el cuerpo empieza a vaciarse antes incluso de que puedas ponerle nombre a lo que te ocurre. "
    "Te ayudan la creatividad, la expresión auténtica y sentir conexión personal con lo que haces. En cambio, la rutina mecánica, el exceso de obligación o no tener espacio propio suele apagar progresivamente la energía."
),

"Virgo": (
    "Tu cuerpo detecta señales muy rápidamente. Muchas veces notas antes que algo no va bien incluso antes de que sea evidente para los demás. "
    "Eso puede ayudarte muchísimo a cuidarte, pero también hacer que vivas en observación constante. "
    "Cuando algo se descoloca, la tendencia suele ser analizarlo, corregirlo o intentar mejorarlo enseguida. "
    "La dificultad aparece cuando el cuerpo necesita descanso y recibe todavía más exigencia o supervisión. "
    "Puedes agotarte intentando hacerlo todo correctamente durante demasiado tiempo. "
    "Te ayudan el orden simple, los hábitos claros y el cuidado corporal real. En cambio, el perfeccionismo, el exceso de análisis o vivir permanentemente intentando corregirte suele generar muchísima tensión."
),

"Libra": (
    "Tu cuerpo responde muchísimo al entorno que te rodea. Cuando existe tensión cotidiana, conflicto o ambientes agresivos, todo dentro lo absorbe rápidamente. "
    "La armonía no es un lujo para ti, sino una necesidad real para sentir bienestar físico y emocional. "
    "Necesitas cierta sensación de equilibrio, belleza y calma alrededor para poder relajarte de verdad. "
    "Cuando pasas demasiado tiempo adaptándote a entornos tensos o relaciones desgastantes, el cuerpo termina agotándose. "
    "Te ayudan la armonía, el equilibrio y los ambientes agradables. En cambio, el conflicto constante, la tensión ambiental o los vínculos muy desgastantes suele afectar profundamente tu energía."
),

"Escorpio": (
    "Tu cuerpo funciona mucho por acumulación y descarga. Cuando acumulas demasiada intensidad sin darle salida, la tensión empieza a quedarse dentro. "
    "Las prácticas demasiado suaves muchas veces no son suficientes para ti. Necesitas descargar de verdad: sudar, atravesar intensidad o entrar en períodos de silencio profundo. "
    "Cuando no existe esa descarga, el cuerpo empieza a endurecerse y la energía queda retenida durante demasiado tiempo. "
    "Entonces pueden aparecer tensión constante, dificultad para dormir o sensación de pesadez acumulada. "
    "Te ayudan la descarga profunda, la intensidad bien canalizada y los espacios de silencio real. En cambio, acumular emociones, contener demasiado tiempo lo que sientes o no tener salida para ello suele generar muchísima presión interna."
),

"Sagitario": (
    "Necesitas sentir que tus hábitos tienen sentido. Las rutinas sostenidas únicamente por obligación suelen agotarte o durar muy poco tiempo. "
    "Cuando conectas con algo que realmente te importa, la energía aparece mucho más fácilmente. "
    "La dificultad surge cuando desaparece el entusiasmo, porque muchas veces también desaparece toda la estructura cotidiana. "
    "Entonces el cuerpo termina pagando el coste de la irregularidad acumulada. "
    "Necesitas construir hábitos mínimos capaces de sostenerse incluso en momentos de poca motivación. "
    "Te ayudan la dirección, el propósito y sentir movimiento en tu vida. En cambio, la rutina vacía, la desmotivación o la irregularidad constante suele desorganizar rápidamente la energía."
),

"Capricornio": (
    "Puedes sostener muchísimo más de lo que la mayoría imagina. La dificultad es que también puedes ignorar las señales de cansancio durante demasiado tiempo. "
    "Existe tendencia a seguir funcionando incluso cuando el cuerpo ya está pidiendo parar. Muchas veces las responsabilidades aparecen antes que la recuperación. "
    "No porque no sientas el agotamiento, sino porque el umbral interno para detenerte suele ser muy alto. "
    "El desgaste suele aparecer de golpe, cuando la acumulación ya supera lo que podías sostener. "
    "Te ayudan los límites claros, el descanso suficiente y una estructura estable. En cambio, la sobrecarga prolongada, el exceso de responsabilidad o no permitirte parar suele desgastar profundamente el cuerpo."
),

"Acuario": (
    "Necesitas hacer las cosas a tu manera para poder sostenerlas en el tiempo. Las rutinas demasiado rígidas o impuestas desde fuera suelen agotarte rápidamente. "
    "Eres especialmente sensible al exceso de estímulos, ruido o demandas constantes, por eso necesitas períodos reales de desconexión para volver a sentir claridad interna. "
    "Cuando pasas demasiado tiempo adaptándote a ritmos externos que no sientes propios, el cuerpo empieza a saturarse poco a poco. "
    "Entender por qué haces algo tiene muchísimo impacto sobre tu capacidad para sostenerlo. "
    "Te ayudan la autonomía, el espacio mental y la libertad de ritmo. En cambio, la sobreestimulación, la imposición externa o no disponer de tiempo para desconectar suele generar muchísima saturación."
),

"Piscis": (
    "Tu cuerpo absorbe muchísimo del entorno. Muchas veces aparece cansancio extremo sin que exista una causa física completamente clara. "
    "La saturación emocional, el exceso de estímulos o los ambientes cargados se quedan dentro aunque no siempre seas consciente de ello. "
    "Necesitas momentos reales de silencio, retirada y vaciado emocional para volver a sentirte bien. "
    "Cuando no existen espacios para soltar lo acumulado, la fatiga empieza a crecer lentamente. "
    "Tu cuerpo suele necesitar descanso profundo con más frecuencia de la que imaginas. "
    "Te ayudan el silencio, el descanso, la suavidad y los espacios de retiro. En cambio, la saturación ambiental, el exceso de exposición o no disponer de momentos de descarga suele generar muchísima sobrecarga."
),

}

# ─── TEXTOS: PLANETAS EN CASA 4 ───────────────────────────────────────────────

PLANETA_CASA4 = {

"Sol": (
    "Necesitas sentir que puedes ser plenamente quien eres dentro de tu espacio más íntimo. Cuando existe demasiada distancia entre lo que muestras hacia fuera y lo que realmente sucede dentro de ti, algo empieza a desgastarse lentamente. "
    "No suele ayudarte sostener una imagen que no tiene raíces reales en tu vida cotidiana, porque tu mundo interno necesita coherencia y verdad emocional. "
    "El hogar no funciona solo como un lugar físico. Es el espacio donde deberías poder bajar la exigencia y existir sin tener que sostener constantemente una versión de ti que no se siente auténtica. "
    "Cuando no existe ese lugar de autenticidad y descanso interno, la energía empieza a agotarse silenciosamente."
),

"Luna": (
    "Tu mundo emocional está profundamente unido a tus raíces y al entorno donde vives. Cuando hay tensión en casa o inestabilidad emocional alrededor, recuperar calma se vuelve mucho más difícil. "
    "Necesitas intimidad, refugio y cierta sensación de seguridad emocional para descansar de verdad. "
    "Los cambios en el hogar no te afectan solo de forma práctica. También se mueven profundamente por dentro y el cuerpo suele notarlo muy rápido cuando algo altera tu espacio emocional. "
    "Cuando el entorno íntimo pierde estabilidad, todo dentro necesita mucho más tiempo para volver a sentirse seguro."
),

"Mercurio": (
    "Necesitas entender y poner palabras a lo que ocurre dentro de ti. Cuando hay emociones, recuerdos o conflictos internos que no consigues expresar claramente, la mente empieza a girar alrededor de ellos una y otra vez. "
    "Muchas veces aparece tendencia a intentar comprender algo emocionalmente antes incluso de terminar de sentirlo por completo. "
    "Hablar, escribir o expresar lo que ocurre dentro suele ayudarte a recuperar claridad y sensación de orden interno. "
    "Cuando todo permanece demasiado tiempo sin nombrarse, aparece ruido mental, saturación y sensación de desorden dentro de ti."
),

"Venus": (
    "Necesitas belleza, armonía y afecto real para sentir bienestar interno. Tu mundo emocional responde muchísimo a la calidad afectiva y estética del espacio donde vives. "
    "Cuando el entorno íntimo se vuelve frío, descuidado o carente de cuidado genuino, algo dentro empieza a apagarse lentamente aunque no siempre resulte fácil explicar exactamente qué falta. "
    "El cuerpo y la energía suelen notarlo enseguida. "
    "Necesitas sentir suavidad, cuidado y conexión auténtica dentro del territorio más íntimo de tu vida para poder relajarte de verdad."
),

"Marte": (
    "Cuando algo amenaza tu espacio emocional o tu sensación de seguridad, la reacción suele aparecer muy rápido. El cuerpo entra fácilmente en defensa cuando percibe invasión, tensión o conflicto dentro del entorno íntimo. "
    "Muchas veces la respuesta llega antes incluso de haber comprobado del todo si el peligro es real, porque la necesidad de proteger tu espacio interno es muy fuerte. "
    "La sensación de tener un lugar propio y protegido resulta especialmente importante para ti. "
    "Cuando no existe esa sensación de resguardo, la tensión interna suele subir rápidamente."
),

"Júpiter": (
    "Tu mundo interior vive las experiencias a gran escala. Cuando algo toca tu base emocional, todo puede expandirse muchísimo por dentro. "
    "Existe una necesidad muy profunda de encontrar un lugar que realmente se sienta hogar, y muchas veces ningún espacio externo parece cubrir completamente esa necesidad. "
    "Cuando aparece inseguridad emocional, la tendencia suele ser expandirte: buscar más sentido, más espacio o nuevas posibilidades donde sentir amplitud otra vez. "
    "Necesitas amplitud también dentro de tu vida íntima y emocional."
),

"Saturno": (
    "Aprendiste pronto a sostenerte emocionalmente sin depender demasiado de otras personas. Puede que en el entorno de origen no hubiera demasiado espacio para mostrar vulnerabilidad libremente. "
    "Eso generó fortaleza, pero también cierta dificultad para relajarte completamente o recibir apoyo sin medirlo antes. "
    "Muchas veces aparece la sensación de tener que merecer el descanso, el cuidado o incluso la ayuda. "
    "Tu sensación de seguridad interna suele construirse lentamente, a través del tiempo, la experiencia y todo aquello que demuestra estabilidad real."
),

"Urano": (
    "Tu sensación de hogar nunca ha sido completamente estable. Puede haber habido cambios, rupturas o dinámicas imprevisibles dentro del entorno de origen, y eso dejó una necesidad muy fuerte de libertad incluso dentro de lo íntimo. "
    "Existe una parte de ti que necesita movimiento y espacio, y al mismo tiempo otra parte que necesita profundamente sentir suelo y estabilidad. "
    "Cuando una relación o un entorno empiezan a sentirse demasiado cerrados, puede aparecer necesidad de distancia o escape casi de inmediato. "
    "Te resulta difícil sostener estabilidad cuando sientes que pierdes libertad interior."
),

"Neptuno": (
    "Tu mundo interno no siempre tiene límites completamente definidos. Muchas veces cuesta entender exactamente qué necesitas emocionalmente o distinguir con claridad qué es tuyo y qué pertenece al entorno. "
    "Puedes absorber dinámicas, emociones o confusiones ajenas sin darte cuenta enseguida. "
    "Cuando el espacio íntimo es caótico, ambiguo o emocionalmente confuso, la sensación de estabilidad empieza a diluirse poco a poco. "
    "Necesitas calma, silencio y espacios emocionalmente limpios para recuperar claridad interna."
),

"Plutón": (
    "Tu base emocional ha atravesado experiencias intensas que dejaron una huella profunda. Hay procesos que transformaron radicalmente tu forma de entender la seguridad emocional y eso te dio muchísima capacidad de resistencia. "
    "Al mismo tiempo, ciertas emociones pueden seguir teniendo una intensidad enorme cuando algo las activa. "
    "Cuando aparecen temas relacionados con el hogar, la pérdida o el control emocional, la reacción interna puede ser extremadamente poderosa. "
    "Tu mundo interior tiene muchísima profundidad y una fuerza emocional difícil de medir desde fuera."
),

"Quirón": (
    "Existe una sensibilidad muy profunda relacionada con el hogar, la pertenencia y la sensación de tener un lugar seguro. Hay una parte de ti que puede sentir fácilmente que no termina de encajar del todo. "
    "Esa sensibilidad duele mucho más cuando intentas esconderla o corregirla constantemente. "
    "Cuando empiezas a reconocerla sin rechazarla, también aparece una enorme capacidad para comprender emocionalmente a otras personas. "
    "Muchas veces aquello que más ha dolido termina convirtiéndose precisamente en lo que más profundidad y humanidad aporta."
),

"Lilith": (
    "Existe una parte de ti que aprendió muy pronto a no mostrarse completamente dentro del entorno íntimo. Puede aparecer irritación, rechazo hacia ciertas dinámicas familiares o sensación de no encajar del todo en el lugar donde debería existir seguridad. "
    "Muchas veces esa parte intenta endurecerse, esconderse o reaccionar antes de sentirse vulnerable. "
    "Pero cuanto más intentas expulsarla o negarla, más fuerza toma internamente. "
    "Necesitas reconocer esa parte sin convertirla en enemiga."
),

"Nodo Norte": (
    "Una parte importante de tu crecimiento tiene que ver con construir raíz interna. Aprender a sentirte en casa dentro de tu propia vida y desarrollar un espacio emocional propio que no dependa constantemente de validación externa. "
    "Eso no ocurre de golpe. Se construye poco a poco, a través de decisiones conscientes y experiencias reales que van creando sensación de pertenencia interna. "
    "Tu dirección de crecimiento apunta hacia dentro."
),

"Nodo Sur": (
    "Existe una parte de ti que conoce muy bien el territorio del hogar, la raíz y la vida interior. Buscar refugio, volver a lo conocido o sostenerte en lo familiar puede surgir de manera muy automática. "
    "Eso aporta sensibilidad y profundidad hacia el mundo íntimo, pero también puede hacer que permanezcas demasiado tiempo en lugares, vínculos o dinámicas que ya no ayudan a crecer. "
    "Tu base interna es importante, pero no puede convertirse en el único lugar desde donde vivir. "
    "Necesitas honrar lo que fue hogar sin quedarte atrapado ahí."
),

}

PLANETA_CASA6 = {

"Sol": (
    "Necesitas sentir que lo que haces cada día tiene sentido. Cuando la vida cotidiana se convierte únicamente en obligación o rutina vacía, la energía empieza a apagarse lentamente. "
    "Puedes seguir funcionando durante bastante tiempo, pero el cuerpo termina notando cuándo estás viviendo sin conexión real con lo que haces. "
    "Tu vitalidad está profundamente ligada a la sensación de propósito y coherencia. "
    "Cuando existe alineación entre lo que haces y lo que sientes importante, la energía cambia completamente."
),

"Luna": (
    "Tu cuerpo y tu estado emocional funcionan profundamente unidos. Cuando algo se mueve emocionalmente, el cuerpo suele reaccionar antes incluso de que puedas explicarlo con claridad. "
    "El cansancio, la digestión, el descanso o la energía diaria cambian mucho según cómo estés por dentro y según el clima emocional que te rodea. "
    "Necesitas cierta estabilidad emocional para sentir también estabilidad física. "
    "Cuando llevas demasiado tiempo sosteniendo tensión emocional, el cuerpo termina hablándolo por ti."
),

"Mercurio": (
    "Tu mente puede ayudarte muchísimo a sentir claridad y equilibrio, pero también agotarte profundamente. Cuando algo no funciona en el cuerpo, en los hábitos o en la rutina, la mente empieza rápidamente a analizarlo. "
    "A veces eso ayuda a encontrar soluciones y otras veces te deja en observación constante, intentando entender o corregir todo lo que ocurre. "
    "Necesitas momentos donde no todo tenga que ser comprendido, supervisado o resuelto mentalmente. "
    "Cuando la mente no descansa realmente, el cuerpo tampoco termina de hacerlo."
),

"Venus": (
    "Necesitas cierto bienestar real dentro de la vida cotidiana para sentirte bien físicamente. No suele ayudarte vivir únicamente desde la obligación. "
    "La belleza, el disfrute sencillo, la armonía o sentir comodidad en el entorno tienen muchísimo impacto sobre tu energía. "
    "Cuando el día a día se vuelve demasiado frío, mecánico o puramente productivo, el cuerpo empieza a vaciarse lentamente. "
    "Necesitas que exista algo agradable, humano y habitable dentro de la rutina para poder sostenerla de verdad."
),

"Marte": (
    "Tu relación con el cuerpo es intensa y exigente. Puedes empujarte muchísimo más allá de lo que otras personas soportarían y seguir funcionando incluso cuando ya se está acumulando demasiada tensión. "
    "El problema es que muchas veces la señal de parar llega demasiado tarde. "
    "Necesitas movimiento y descarga física, pero también aprender a reconocer los límites antes de agotarte completamente. "
    "Cuando no existe salida para toda la energía acumulada, la irritación y la tensión corporal suelen aumentar muy rápido."
),

"Júpiter": (
    "Te cuesta notar automáticamente cuándo algo ya es suficiente. Puedes trabajar más, hacer más o exigirte más de lo que realmente necesitas sin darte cuenta enseguida. "
    "No siempre ocurre por ambición consciente. Muchas veces simplemente no aparece el límite de forma natural. "
    "El problema es que el cuerpo sí tiene límite, aunque tardes en percibirlo. "
    "Necesitas construir conscientemente momentos de pausa, moderación y descanso. "
    "Cuando no existe esa sensación de medida, la expansión continúa hasta que el cuerpo empieza a pasar factura."
),

"Saturno": (
    "Tienes muchísima capacidad para sostener hábitos y responsabilidades durante largos períodos de tiempo. El problema es que también puedes acostumbrarte a vivir en exigencia constante. "
    "Muchas veces el descanso no aparece espontáneamente y tiene que convertirse en una decisión consciente. "
    "Tu cuerpo puede soportar mucho, pero eso no significa que no exista un coste por mantener ese ritmo durante demasiado tiempo. "
    "Existe tendencia a seguir funcionando incluso cuando ya no quedan fuerzas reales. "
    "Necesitas aprender que parar también forma parte de construir estabilidad."
),

"Urano": (
    "Las rutinas demasiado rígidas terminan agotándote. Necesitas sentir que eliges la forma de hacer las cosas y que existe espacio para moverte a tu manera dentro de la vida cotidiana. "
    "Cuando una estructura se vuelve demasiado repetitiva o impuesta, el cuerpo empieza a resistirse poco a poco. "
    "Necesitas libertad, espacio mental y períodos reales de desconexión para volver a sentir claridad interna. "
    "Muchas veces puedes regularte muy bien a través de métodos poco convencionales si sientes que realmente encajan contigo. "
    "Cuando vives demasiado tiempo al ritmo de otras personas, la saturación aparece rápidamente."
),

"Neptuno": (
    "Muchas veces te cuesta notar claramente dónde termina el esfuerzo y dónde empieza el agotamiento. Puedes absorber la carga emocional del entorno sin darte cuenta enseguida y seguir funcionando mientras el cuerpo se va saturando lentamente. "
    "Necesitas espacios reales de descanso, silencio y cierre emocional para vaciar todo lo que vas acumulando. "
    "Cuando no existe ese vaciado, la fatiga empieza a crecer aunque no haya una causa física evidente. "
    "Tu cuerpo necesita mucha más recuperación emocional de la que suele parecer desde fuera."
),

"Plutón": (
    "Tu relación con el cuerpo y los hábitos suele vivirse con mucha intensidad. Las rutinas superficiales o automáticas rara vez consiguen sostenerte durante mucho tiempo, porque necesitas sentir transformación real y profundidad en lo que haces. "
    "Cuando atraviesas una crisis física o emocional, tu capacidad de regeneración puede ser enorme. "
    "Pero antes de regenerarte, muchas veces atraviesas procesos muy intensos que lo remueven todo profundamente. "
    "Tu cuerpo no suele funcionar a medias."
),

"Quirón": (
    "Existe una sensibilidad especial en la relación con el cuerpo, la salud y la exigencia cotidiana. Puede que hayas aprendido muy pronto a exigirte incluso cuando lo que realmente necesitabas era cuidado. "
    "Hay una parte especialmente vulnerable frente a la presión, el cansancio o la sensación de no funcionar correctamente. "
    "La dificultad aparece cuando intentas tratar esa sensibilidad como si fuera un defecto que hay que corregir. "
    "Cuando empiezas a escucharla en lugar de combatirla, también aparece una enorme capacidad para comprender el sufrimiento de otras personas."
),

"Lilith": (
    "Tu cuerpo no siempre responde bien a normas impuestas desde fuera. Existe una parte muy instintiva en tu manera de relacionarte con la salud, el descanso y el cuidado cotidiano. "
    "Muchas veces necesitas descubrir personalmente qué es lo que realmente te funciona y qué no encaja contigo aunque aparentemente sea lo correcto. "
    "Cuando intentas forzarte continuamente a seguir modelos ajenos, el cuerpo acaba reaccionando de alguna manera. "
    "Escuchar lo que necesitas de verdad suele ser mucho más importante que intentar cumplir expectativas externas."
),

"Nodo Norte": (
    "Una parte importante de tu crecimiento pasa por aprender a construir estabilidad dentro de la vida cotidiana. No basta con entender las cosas internamente o esperar a sentir una base suficiente. "
    "Aquí el aprendizaje necesita bajar al cuerpo, a los hábitos y a la realidad concreta de cada día. "
    "Desarrollar rutinas sostenibles, cuidar tu energía y aprender a escuchar las necesidades reales del cuerpo forma parte directa de tu evolución. "
    "Muchas veces el crecimiento aparece en cosas muy pequeñas: repetir algo simple, sostener procesos lentamente o aprender a escucharte antes de llegar al límite. "
    "Tu dirección no apunta hacia hacer más, sino hacia construir una vida que el cuerpo realmente pueda sostener."
),

"Nodo Sur": (
    "Existe tendencia a vivir con más conexión con lo interno, lo emocional o lo simbólico que con las necesidades concretas del cuerpo y de la vida cotidiana. "
    "Puede resultar más natural refugiarte en estados internos amplios, en la imaginación o en lo emocionalmente conocido que sostener rutinas constantes y realistas. "
    "El problema es que, cuando el cuerpo queda demasiado tiempo en segundo plano, el desgaste termina apareciendo igualmente. "
    "Hay hábitos, ritmos y formas de cuidado que quizá parezcan demasiado simples o limitantes para una parte de ti. "
    "Y sin embargo, precisamente ahí puede existir una parte muy importante del equilibrio: aprender a habitar lo cotidiano sin escapar continuamente de ello."
),

}

# ─── TEXTOS: ASPECTOS LUNARES ─────────────────────────────────────────────────

ASPECTOS_LUNA = {

("Luna","Sol","="): (
    "Lo que sientes y la dirección de tu vida suelen moverse muy unidas. Cuando emocionalmente hay estabilidad, aparece también más energía, claridad y sensación de propósito. Y cuando algo se rompe por dentro, la vitalidad suele notarlo enseguida. "
    "No separas fácilmente quién eres de cómo te sientes en cada momento. Eso puede darte mucha coherencia interna, pero también hacer que los períodos difíciles te atraviesen con más profundidad."
),

("Luna","Sol","□"): (
    "A veces lo que necesitas emocionalmente y lo que quieres construir no avanzan en la misma dirección. Puede haber momentos en los que una parte de ti quiera seguir adelante mientras otra necesita parar, protegerse o retirarse. "
    "Cuando intentas escuchar solo una de esas partes, la tensión interna aumenta rápidamente. "
    "El aprendizaje no consiste en elegir una y negar la otra, sino en reconocer ambas necesidades sin convertirlas en enemigas."
),

("Luna","Sol","☍"): (
    "Hay momentos en los que lo que sientes y lo que decides hacer parecen ir en direcciones opuestas. El cuerpo puede pedir descanso o cuidado mientras la voluntad intenta seguir adelante. Y otras veces una parte quiere avanzar mientras algo emocional todavía necesita tiempo. "
    "La sensación de equilibrio aparece cuando ambas partes pueden escucharse sin que una tenga que anular completamente a la otra."
),

("Luna","Sol","△"): (
    "Lo que sientes y la forma en que afirmas tu vida suelen colaborar entre sí. Cuando algo te afecta emocionalmente, no suele aparecer tanta división interna y tu identidad y tu mundo emocional tienden a moverse en una dirección compatible. "
    "Eso puede convertirse en un recurso importante, porque te ayuda a recuperar coherencia con más facilidad en momentos de presión."
),

("Luna","Sol","✶"): (
    "Existe una conexión bastante accesible entre lo que sientes y la dirección que necesitas tomar. Cuando escuchas tu estado emocional con atención, suele aparecer también más claridad sobre hacia dónde avanzar. "
    "Tu mundo emocional y tu identidad pueden ayudarse mutuamente si les das espacio suficiente. "
    "Te ayuda permitir que lo emocional informe el rumbo sin que tenga que ocuparlo todo."
),

("Luna","Sol","⚻"): (
    "Existe un ajuste constante entre lo que sientes y la dirección que intentas sostener. Hay momentos en los que emocionalmente necesitas una cosa mientras la vida parece pedir otra distinta. "
    "Eso rara vez se resuelve de una vez para siempre y suele requerir reajustes continuos. "
    "La clave está en modificar el rumbo cuando hace falta sin vivirlo como una traición a ti mismo."
),

("Luna","Mercurio","="): (
    "Pensar y sentir ocurren casi al mismo tiempo. Necesitas poner palabras a lo que te pasa para terminar de integrarlo, porque cuando algo no puede expresarse la emoción sigue girando dentro de la mente y cuesta más que encuentre calma. "
    "Hablar, escribir o compartir lo que sientes puede ayudarte muchísimo a recuperar claridad interna."
),

("Luna","Mercurio","□"): (
    "A veces lo que sientes y lo que piensas no se ordenan al mismo ritmo. Puede aparecer la necesidad de entender una emoción antes incluso de haberla sentido completamente. "
    "Cuando la mente ocupa demasiado espacio, el cuerpo puede quedarse sosteniendo aquello que todavía no ha podido expresarse. "
    "El aprendizaje no consiste en pensar menos, sino en permitir que el pensamiento acompañe la emoción sin sustituirla."
),

("Luna","Mercurio","☍"): (
    "Hay momentos en los que una parte de ti necesita sentir y otra necesita explicarlo todo. Puedes oscilar entre hablar demasiado de lo que te ocurre o no saber cómo ponerlo en palabras. "
    "La mente intenta ordenar, pero si se adelanta demasiado puede alejarte del contacto real con la emoción. "
    "La regulación aparece cuando utilizas el lenguaje para acompañar lo que sientes, no para escapar de ello."
),

("Luna","Mercurio","△"): (
    "Tienes facilidad para poner palabras a lo que sientes. Cuando algo se mueve dentro, normalmente encuentras una forma de expresarlo, pensarlo o compartirlo. "
    "Ese puente entre emoción y lenguaje puede convertirse en un recurso muy importante para regularte. "
    "Cuanto más espacio tiene la expresión, menos necesita la emoción quedarse circulando en silencio."
),

("Luna","Mercurio","✶"): (
    "Existe una vía natural entre lo que sientes y tu capacidad de comprenderlo. Hablar, escribir o escuchar tu propio pensamiento puede ayudarte a ordenar estados emocionales complejos. "
    "Cuando das espacio a esa expresión, recuperas claridad con mucha más facilidad. "
    "La palabra funciona aquí como un ancla: no lo resuelve todo, pero ayuda a que la emoción deje de moverse sin dirección."
),

("Luna","Mercurio","⚻"): (
    "Existe un ajuste constante entre sentir y entender. A veces necesitas hablar para ordenar lo que ocurre y otras veces hablar demasiado puede alejarte de lo que realmente sientes. "
    "No existe una única fórmula estable. "
    "Tu equilibrio requiere aprender cuándo poner palabras y cuándo permanecer en contacto con la emoción sin intentar explicarla enseguida."
),


("Luna","Venus","="): (
    "Tu forma de querer y tu mundo emocional están profundamente unidos. Lo que necesitas emocionalmente suele aparecer también en la manera en que cuidas, amas o te vinculas. "
    "Eso puede darte mucha capacidad de afecto, sensibilidad y presencia dentro de las relaciones. "
    "La dificultad aparece cuando das continuamente sin distinguir con claridad qué necesitas tú realmente. "
    "Tu equilibrio mejora cuando el cuidado también puede dirigirse hacia ti sin culpa ni sensación de exceso."
),

("Luna","Venus","□"): (
    "A veces lo que necesitas emocionalmente y lo que intentas sostener en los vínculos no coincide. Puedes cuidar demasiado mientras tus propias necesidades quedan en segundo plano. "
    "Y cuando intentas atender lo que realmente sientes, puede aparecer miedo a romper el equilibrio de la relación o a generar distancia. "
    "El aprendizaje no consiste en elegir entre vínculo y necesidad propia, sino en aprender a sostener ambas cosas con más honestidad y menos autoabandono."
),

("Luna","Venus","☍"): (
    "Puede haber tensión entre lo que necesitas emocionalmente y la forma en que buscas afecto. A veces intentas recibir amor adaptándote, agradando o cuidando más de lo que realmente puedes sostener. "
    "Cuando eso ocurre, una parte de ti queda esperando algo que no termina de pedir directamente. "
    "La sensación de equilibrio aparece cuando el afecto deja de implicar renunciar a lo que tú también necesitas."
),

("Luna","Venus","△"): (
    "Tu mundo emocional y tu forma de relacionarte suelen ir en la misma dirección. Cuando quieres a alguien, normalmente existe coherencia entre lo que sientes y la manera en que lo expresas. "
    "El afecto puede convertirse en un recurso muy importante para recuperar calma, orden y sensación de bienestar interno. "
    "Las relaciones claras y recíprocas suelen ayudarte mucho a sentir estabilidad emocional."
),

("Luna","Venus","✶"): (
    "Existe facilidad para encontrar apoyo emocional a través del afecto, la belleza o los vínculos cuidados. Cuando hay armonía alrededor, el mundo interno suele ordenarse con más facilidad. "
    "El cuidado, cuando es recíproco y auténtico, tiene un efecto profundamente estabilizador sobre ti. "
    "La suavidad no funciona aquí como algo superficial, sino como una necesidad emocional real."
),

("Luna","Venus","⚻"): (
    "Existe un ajuste constante entre lo que necesitas emocionalmente y la manera en que te vinculas. A veces cuidar demasiado el vínculo puede alejarte de ti mismo. "
    "Y otras veces atenderte más a ti puede remover equilibrios que parecían estables. "
    "Tu bienestar depende mucho de revisar continuamente esa medida para que el cuidado no termine convirtiéndose en abandono propio."
),

("Luna","Marte","="): (
    "Lo que sientes y la necesidad de actuar aparecen casi al mismo tiempo. Cuando algo te afecta, el cuerpo suele responder muy rápido. "
    "Eso puede darte mucha capacidad de reacción y movimiento, pero también hacer que algunas emociones salgan antes de haber encontrado una forma más consciente de expresarse. "
    "Necesitas vías físicas claras para mover la energía y descargar lo que se acumula dentro."
),

("Luna","Marte","□"): (
    "Cuando algo emocionalmente te activa, el cuerpo entra rápidamente en tensión. Si no existe una forma clara de descargar esa energía, puede aparecer irritabilidad, impulsividad o necesidad de confrontación. "
    "Muchas veces la reacción responde más al nivel de activación acumulada que a lo que realmente está ocurriendo en ese momento. "
    "El aprendizaje no consiste en dejar de sentir intensidad, sino en aprender a darle una salida y un canal más consciente."
),

("Luna","Marte","☍"): (
    "Dentro de ti conviven dos necesidades muy distintas. Una parte necesita cuidado, apoyo o contención emocional, mientras otra responde con fuerza, independencia o confrontación. "
    "Las dos pueden aparecer al mismo tiempo y generar sensación de contradicción interna. "
    "La regulación mejora cuando reconoces ambas partes como reales, sin obligarte a convertirte únicamente en una de ellas."
),

("Luna","Marte","△"): (
    "Tu emoción y tu capacidad de acción suelen trabajar juntas. Cuando algo te mueve por dentro, normalmente puedes transformarlo con bastante rapidez en movimiento, decisión o acción concreta. "
    "Eso ayuda a que la energía emocional no se quede completamente acumulada dentro del cuerpo. "
    "El movimiento y la acción consciente pueden ayudarte muchísimo a ordenar lo que sientes."
),

("Luna","Marte","✶"): (
    "Existe facilidad para mover emocionalmente lo que te pasa. Cuando algo te afecta, normalmente encuentras alguna manera de actuar, descargar o transformar esa energía en algo útil. "
    "La acción puede ayudarte a no quedarte demasiado tiempo atrapado dentro de la activación emocional. "
    "Mover el cuerpo o tomar iniciativa suele regular mucho tu estado interno."
),

("Luna","Marte","⚻"): (
    "Existe un ajuste constante entre lo que sientes y la forma en que reaccionas. A veces la emoción necesita cuidado y el cuerpo responde automáticamente con tensión o acción. "
    "Otras veces intentas actuar cuando internamente todavía necesitarías parar y sostener lo que está ocurriendo dentro. "
    "Tu equilibrio depende mucho de aprender cuándo descargar y cuándo permanecer con la emoción sin reaccionar enseguida."
),

("Luna","Júpiter","="): (
    "Tus emociones funcionan a gran escala. Cuando algo te hace bien, la alegría puede expandirse muchísimo. Y cuando algo duele, también puede sentirse mucho más grande de lo que otras personas esperan. "
    "No se trata de exageración, sino de amplitud emocional y de una necesidad muy profunda de vivir las cosas con sentido y plenitud. "
    "La dificultad aparece cuando no existe una sensación clara de suficiente y todo parece necesitar siempre un poco más para sentirse completo."
),

("Luna","Júpiter","□"): (
    "Muchas veces puedes sentir más necesidad emocional de la que el entorno puede cubrir fácilmente. Cuando algo te hace bien, quieres más. Y cuando falta, el vacío puede sentirse enorme. "
    "Internamente cuesta encontrar un punto de suficiente y eso puede llevarte a moverte entre exceso y sensación de carencia. "
    "Tu equilibrio no necesita negar lo que sientes, sino aprender medida sin apagar la amplitud emocional."
),

("Luna","Júpiter","☍"): (
    "Puede haber oscilación entre necesidad emocional y exceso. A veces buscas amplitud, sentido o afecto en una escala mayor de la que el entorno realmente puede sostener. "
    "Y cuando eso no llega, puede aparecer una sensación de vacío muy grande o de desilusión difícil de llenar. "
    "Tu bienestar depende mucho de aprender medida emocional sin reducir la amplitud natural de lo que sientes."
),

("Luna","Júpiter","△"): (
    "Tienes capacidad para darle espacio a lo que sientes. Cuando aparece una dificultad emocional, suele existir tendencia a buscar perspectiva antes de quedarte completamente atrapado dentro del problema. "
    "Eso puede ayudarte muchísimo a atravesar experiencias complejas con más amplitud, comprensión y capacidad de recuperación. "
    "Tu mundo emocional necesita sentido, horizonte y sensación de espacio suficiente para sentirse bien."
),

("Luna","Júpiter","✶"): (
    "Tu mundo emocional suele encontrar alivio cuando amplías perspectiva. Hablar, comprender o mirar más allá del problema inmediato puede ayudarte mucho a recuperar calma y estabilidad interna. "
    "Necesitas sentir que siempre existe algún horizonte posible y alguna dirección hacia la que avanzar. "
    "La esperanza funciona aquí como un recurso importante, siempre que no sustituya el contacto real con lo que estás sintiendo."
),

("Luna","Júpiter","⚻"): (
    "Existe un ajuste continuo entre lo que emocionalmente necesitas y la tendencia a expandirlo todo. A veces necesitas más espacio y otras veces más límite, pero no siempre resulta fácil distinguir cuándo hace falta cada cosa. "
    "La dificultad está en encontrar medida emocional sin cortar la amplitud natural de lo que sientes. "
    "Aprender esa proporción es una parte importante de tu equilibrio interno."
),

("Luna","Saturno","="): (
    "Antes de mostrar lo que sientes, una parte de ti ya lo ha evaluado. Eso puede darte muchísima capacidad para sostener situaciones difíciles, pero también hacer que guardes emociones dentro durante demasiado tiempo. "
    "A veces otras personas no perciben la intensidad de lo que estás conteniendo porque has aprendido a sostenerlo en silencio. "
    "Tu equilibrio mejora cuando la estructura no impide que la emoción exista y tenga también espacio para expresarse."
),

("Luna","Saturno","□"): (
    "Puede costarte permitir ciertas emociones sin intentar controlarlas enseguida. La vulnerabilidad puede sentirse peligrosa, excesiva o difícil de mostrar abiertamente. "
    "Muchas veces una parte de ti intenta contener lo que siente antes incluso de haberlo reconocido por completo. "
    "No necesitas destruir tu estructura interna para sentir. Necesitas permitir que la emoción exista dentro de ella sin convertirla automáticamente en un problema que corregir."
),

("Luna","Saturno","☍"): (
    "Existe tensión entre lo que sientes y la necesidad de mantener control. Cuando emocionalmente algo sube, la respuesta automática suele ser contenerlo o intentar sostenerlo sin mostrar demasiado. "
    "El problema es que lo que permanece contenido durante demasiado tiempo termina acumulando presión dentro del cuerpo y del mundo emocional. "
    "La sensación de estabilidad aparece cuando la contención deja de ser bloqueo y se convierte en una forma consciente de sostener lo que sientes."
),

("Luna","Saturno","△"): (
    "Tienes capacidad para sostener lo que sientes sin desbordarte fácilmente. Eso no significa ausencia de intensidad emocional, sino que existe cierta estructura interna capaz de contenerla y darle tiempo. "
    "Cuando estás en equilibrio, emoción y sostén trabajan juntos y eso puede darte muchísima estabilidad en momentos difíciles. "
    "La paciencia y la capacidad de permanecer suelen convertirse aquí en recursos importantes."
),

("Luna","Saturno","✶"): (
    "Existe capacidad para darle estructura a lo que sientes sin bloquearlo completamente. La estabilidad aparece cuando encuentras equilibrio entre contención y expresión emocional. "
    "Tu mundo interno suele fortalecerse cuando existen orden, límites claros y suficiente tiempo para procesar lo que te ocurre. "
    "La estructura puede convertirse en un recurso muy valioso siempre que no se transforme en rigidez emocional."
),

("Luna","Saturno","⚻"): (
    "Existe una tensión constante entre sentir y contener. A veces necesitas expresar lo que te pasa y al mismo tiempo aparece una necesidad muy fuerte de controlarlo o reducirlo. "
    "Cuando una de las dos partes domina demasiado, puede aparecer rigidez emocional o descargas que llegan después de haber sostenido demasiado tiempo la presión interna. "
    "Tu equilibrio depende mucho de reajustar continuamente la relación entre estructura y emoción."
),

("Luna","Urano","="): (
    "Tu mundo emocional cambia rápido y necesita mucha libertad para poder respirar. Cuando una situación empieza a sentirse demasiado cerrada, absorbente o asfixiante, puede aparecer desconexión de forma bastante repentina. "
    "Muchas veces el cuerpo se retira antes incluso de que hayas decidido conscientemente tomar distancia. "
    "Necesitas espacio para procesar lo que sientes sin presión constante ni sensación de invasión emocional. "
    "Tu equilibrio mejora cuando existe libertad suficiente para moverte emocionalmente sin sentirte atrapado."
),

("Luna","Urano","□"): (
    "Existe tensión entre la necesidad de estabilidad emocional y la necesidad de libertad. Cuando una relación o situación se vuelve demasiado intensa o absorbente, suele aparecer necesidad de distancia o aire. "
    "Y cuando existe demasiada distancia, puede reaparecer necesidad de conexión, cercanía o referencia emocional. "
    "La dificultad está en no sentir que tienes que elegir constantemente entre vínculo y libertad. "
    "Tu regulación necesita encontrar espacio y movimiento sin romper completamente aquello que también te sostiene."
),

("Luna","Urano","☍"): (
    "Puedes oscilar entre necesidad de vínculo y necesidad de ruptura o distancia. Cuando algo se vuelve demasiado previsible, puede aparecer inquietud o sensación de encierro. "
    "Y cuando todo cambia demasiado rápido, aparece necesidad de suelo, estabilidad o referencia emocional. "
    "Dentro de ti conviven ambas necesidades y ninguna desaparece del todo. "
    "Tu equilibrio depende de encontrar libertad sin perder completamente el contacto con aquello que te da estabilidad interna."
),

("Luna","Urano","△"): (
    "Tienes facilidad para soltar emocionalmente aquello que ya terminó. Eso no significa ausencia de dolor, sino cierta capacidad para no quedarte atrapado indefinidamente dentro de lo que ya no tiene vida o movimiento. "
    "Cuando algo deja de sostenerse, normalmente aparece impulso hacia el cambio, la renovación o la apertura hacia otra etapa. "
    "La libertad emocional puede convertirse en un recurso importante para volver a moverte y recuperar energía."
),

("Luna","Urano","✶"): (
    "Existe facilidad para introducir cambios que alivian tu mundo emocional. Cuando algo se estanca, mover una pieza, cambiar de ritmo o tomar un poco de distancia puede ayudarte muchísimo a recuperar claridad interna. "
    "Tu mundo emocional respira mejor cuando siente margen de libertad y posibilidad de movimiento. "
    "El cambio consciente puede convertirse aquí en una vía muy importante de regulación."
),

("Luna","Urano","⚻"): (
    "Existe un ajuste constante entre seguridad emocional y libertad. A veces necesitas mucha cercanía y otras veces aparece necesidad de espacio de forma bastante repentina. "
    "Si esa necesidad de aire no se reconoce a tiempo, puede surgir corte emocional, desconexión o necesidad de alejarte bruscamente para recuperar equilibrio interno. "
    "Tu bienestar depende mucho de anticipar esa necesidad antes de llegar al límite."
),

("Luna","Neptuno","="): (
    "Absorbes muchísimo emocionalmente del entorno. Muchas veces te afecta el estado emocional de otras personas sin que seas plenamente consciente de ello. "
    "Cuando no existen límites emocionales claros, puedes terminar sosteniendo dentro cargas, tensiones o confusiones que en realidad no eran tuyas. "
    "Necesitas silencio, descanso y momentos reales de vaciado emocional para volver a sentir claridad interna. "
    "Tu equilibrio depende mucho de revisar continuamente qué pertenece realmente a tu mundo emocional y qué viene del entorno."
),

("Luna","Neptuno","□"): (
    "A veces cuesta distinguir claramente lo que sientes de lo que querrías sentir o imaginar sentir. Cuando emocionalmente necesitas claridad, puede aparecer todavía más confusión, mezcla o ambigüedad interna. "
    "La percepción emocional puede llegar mezclada con expectativas, idealización o imágenes internas difíciles de separar de la realidad concreta. "
    "Necesitas mucho más suelo emocional y referencia clara de lo que normalmente crees. "
    "Tu regulación mejora cuando existe descanso, límites y contacto real con lo que está ocurriendo aquí y ahora."
),

("Luna","Neptuno","☍"): (
    "Dentro de ti conviven dos necesidades muy distintas. Una parte busca estabilidad, claridad y suelo emocional, mientras otra necesita abrirse, fluir o perder límites. "
    "Cuando una de esas partes domina demasiado, la otra suele reaccionar intentando compensarlo. "
    "A veces necesitas refugio y otras veces disolución, silencio o distancia del mundo concreto. "
    "Tu equilibrio requiere apertura emocional sin perder completamente el contacto con la realidad presente."
),

("Luna","Neptuno","△"): (
    "Tu sensibilidad emocional puede fluir con bastante naturalidad. Tienes facilidad para captar matices, estados y atmósferas sin necesidad de explicarlo todo racionalmente. "
    "Cuando existen espacios de silencio, descanso y calma emocional, esa sensibilidad se convierte en un recurso muy profundo. "
    "Tu intuición suele funcionar mucho mejor cuando no existe saturación emocional alrededor."
),

("Luna","Neptuno","✶"): (
    "Existe una vía suave entre tu mundo emocional y tu sensibilidad más sutil. La imaginación, la música, el descanso, el silencio o la contemplación pueden ayudarte muchísimo a regularte. "
    "Cuando cuidas bien tus límites, la sensibilidad deja de sentirse como sobrecarga y empieza a convertirse en un apoyo interno. "
    "Tu equilibrio mejora cuando existe apertura emocional, pero también contorno y protección suficiente."
),

("Luna","Neptuno","⚻"): (
    "Existe un ajuste constante entre sensibilidad y límites. A veces te abres demasiado y absorbes más de lo que realmente puedes procesar. "
    "Otras veces necesitas retirarte del entorno para volver a recuperar claridad y sensación de centro interno. "
    "Tu regulación depende mucho de revisar continuamente qué es tuyo y qué pertenece emocionalmente al ambiente o a otras personas."
),

("Luna","Plutón","="): (
    "Tus emociones no funcionan a medias. Cuando algo te afecta de verdad, la intensidad puede ser enorme aunque externamente apenas se note. "
    "Tu mundo emocional tiene mucha profundidad y necesita espacios igual de reales donde poder expresarse sin tener que reducirse o esconderse. "
    "Intentar apagar esa intensidad rara vez funciona durante mucho tiempo. "
    "Tu equilibrio no depende de sentir menos, sino de encontrar formas seguras y conscientes de sostener todo lo que se mueve dentro."
),

("Luna","Plutón","□"): (
    "Cuando una emoción aparece, otra parte de ti intenta controlarla o contenerla casi al mismo tiempo. Puedes sentir intensidad profunda y, a la vez, necesidad de cerrarla, esconderla o empujarla hacia abajo. "
    "Muchas veces esa lucha interna termina agotando más que la emoción en sí. "
    "Existe miedo a perder el control, a quedar demasiado expuesto o a que la intensidad te desborde completamente. "
    "Tu regulación empieza cuando dejas de pelearte con lo que sientes y aprendes a sostenerlo con recursos y espacio suficiente."
),

("Luna","Plutón","☍"): (
    "Tu mundo emocional tiende a atraer intensidad. Existe una atracción muy fuerte hacia lo profundo, hacia los vínculos intensos y hacia todo aquello que remueve emocionalmente. "
    "Pero al mismo tiempo puede aparecer miedo a perderte dentro de esa intensidad o a quedar demasiado absorbido por ella. "
    "A veces surge acercamiento emocional muy profundo y después necesidad de distancia para recuperar sensación de control interno. "
    "El aprendizaje está en poder entrar en profundidad sin sentir que tienes que desaparecer dentro de ella."
),

("Luna","Plutón","△"): (
    "Tienes una capacidad muy profunda de transformación emocional. Cuando algo te afecta, puedes atravesarlo con una fuerza interna enorme aunque el proceso no siempre sea sencillo. "
    "Existe capacidad real para regenerarte desde dentro y reconstruirte después de experiencias intensas. "
    "La emoción aquí no se queda solo en impacto: puede convertirse en comprensión, fuerza y transformación profunda cuando encuentra un cauce adecuado."
),

("Luna","Plutón","✶"): (
    "Existe una vía de profundidad emocional que puede convertirse en un recurso muy importante para ti. Cuando te permites mirar lo que ocurre por debajo de la superficie, normalmente recuperas fuerza interna y sensación de verdad emocional. "
    "Tu mundo interno se regula mucho mejor cuando no tiene que quedarse únicamente en lo superficial o en lo aparentemente correcto. "
    "La honestidad profunda contigo mismo puede devolverte centro y estabilidad."
),

("Luna","Plutón","⚻"): (
    "Existe un ajuste constante entre intensidad emocional y necesidad de control. A veces necesitas entrar en profundidad y atravesar lo que se está moviendo dentro, y otras veces necesitas tomar distancia para no sentirte absorbido por ello. "
    "No siempre resulta fácil distinguir cuánta intensidad puedes sostener en cada momento sin agotarte o saturarte emocionalmente. "
    "Tu regulación depende mucho de aprender a medir esa profundidad y darte espacio suficiente para procesarla."
),

("Luna","Quirón","="): (
    "Existe una sensibilidad emocional muy profunda relacionada con el cuidado, la pertenencia y la sensación de poder descansar emocionalmente en algún lugar. "
    "Hay heridas emocionales que probablemente nunca desaparezcan del todo, pero cuando dejas de vivirlas como algo que deberías esconder o corregir, aparece una enorme capacidad de comprensión y humanidad. "
    "Tu sensibilidad puede convertirse en una forma muy precisa de acompañamiento, tanto hacia ti como hacia otras personas."
),

("Luna","Quirón","□"): (
    "Hay una herida emocional que puede activarse especialmente en momentos de necesidad, cuidado o pertenencia. A veces aquello que más necesitas también es lo que más cuesta recibir con tranquilidad. "
    "La sensibilidad se activa justo en el lugar donde haría falta descanso, apoyo o contención emocional. "
    "La dificultad no está en sentir demasiado, sino en rechazar esa sensibilidad o vivirla como un problema que habría que corregir. "
    "Tu regulación empieza cuando aprendes a acompañarte sin atacar lo que más vulnerable se siente dentro de ti."
),

("Luna","Quirón","☍"): (
    "Puede haber tensión entre tu necesidad emocional y una herida profunda que se activa especialmente dentro de los vínculos. A veces buscas cuidado fuera y, al mismo tiempo, algo dentro se protege automáticamente de recibirlo por completo. "
    "Esa defensa no es el problema. Es una parte de ti que aprendió hace tiempo a protegerse para no volver a sentirse herido. "
    "Tu equilibrio mejora cuando puedes reconocer esa defensa sin convertirla en enemiga ni obligarte a derribarla de golpe."
),

("Luna","Quirón","△"): (
    "Tu sensibilidad emocional puede convertirse en una fuente muy profunda de comprensión. Lo que has vivido o sentido con más vulnerabilidad puede ayudarte a acompañarte y acompañar mejor a otras personas. "
    "No porque deje de doler completamente, sino porque aprendes a relacionarte con esa herida desde un lugar mucho más consciente y humano. "
    "La herida deja de ser solamente fragilidad cuando empieza a transformarse en comprensión profunda."
),

("Luna","Quirón","✶"): (
    "Existe una vía de aprendizaje emocional muy ligada a tu sensibilidad. Cuando escuchas las zonas que más fácilmente se hieren, aparece también una capacidad muy precisa de cuidado y comprensión. "
    "Tu vulnerabilidad puede convertirse en orientación y ayudarte a entender con mucha profundidad lo que necesitas realmente. "
    "Tu regulación mejora cuando esa sensibilidad tiene espacio y legitimidad, no cuando intentas eliminarla o endurecerte contra ella."
),

("Luna","Quirón","⚻"): (
    "Existe un ajuste constante entre lo que sientes y una sensibilidad emocional más profunda que se activa de formas diferentes según el momento. Lo que te ayuda a regularte en una etapa puede no servir igual en otra. "
    "No existe aquí una única forma fija de equilibrio emocional. "
    "Necesitas aprender a escucharte continuamente y adaptar el sostén a lo que realmente está ocurriendo dentro de ti en cada momento."
),

("Luna","Lilith","="): (
    "Hay una parte emocional muy instintiva dentro de ti que no acepta fácilmente ser domesticada o reducida para encajar. Cuando intentas adaptarte demasiado, esa parte puede aparecer como irritación, rechazo o necesidad de romper con lo que se siente falso o invasivo. "
    "No es una parte que haya que eliminar ni controlar constantemente. "
    "Necesita ser reconocida y escuchada sin dejar que tome completamente el mando de tus decisiones o vínculos."
),

("Luna","Lilith","□"): (
    "Puede haber tensión entre tus necesidades emocionales y una parte instintiva que se resiste profundamente a la adaptación. Cuando aparece sensación de invasión, control o condicionamiento emocional, puede surgir una reacción muy fuerte incluso antes de entender del todo lo que está ocurriendo. "
    "Esa reacción contiene información importante sobre tus límites y sobre lo que no puedes seguir sosteniendo internamente. "
    "El aprendizaje está en escuchar esa fuerza sin dejar que destruya automáticamente el vínculo o la situación cada vez que se activa."
),

("Luna","Lilith","☍"): (
    "Puede haber oscilación entre buscar cuidado y rechazarlo cuando se siente demasiado invasivo o absorbente. Una parte de ti necesita pertenecer, sentirse acogido y poder descansar emocionalmente en alguien o en algo. "
    "Y al mismo tiempo existe otra parte que se rebela rápidamente ante cualquier forma de dependencia emocional o sensación de pérdida de libertad interna. "
    "Tu regulación mejora cuando puedes reconocer ambas necesidades sin expulsar ninguna de ellas."
),

("Luna","Lilith","△"): (
    "Tu mundo emocional tiene acceso a una fuerza instintiva importante. Cuando escuchas esa parte sin miedo ni rechazo, puede ayudarte muchísimo a proteger tus límites y reconocer con claridad lo que no es verdadero para ti. "
    "Existe una sabiduría corporal muy profunda que no pasa por adaptarte constantemente a lo que otras personas esperan. "
    "Tu regulación mejora cuando esa fuerza tiene un lugar consciente y puede expresarse sin necesidad de explotar."
),

("Luna","Lilith","✶"): (
    "Existe una vía de contacto bastante accesible con una parte emocional más instintiva, libre y difícil de domesticar. Cuando le das un espacio consciente, esa fuerza puede ayudarte a recuperar autenticidad y conexión contigo mismo. "
    "No necesitas expulsarla ni dejar que ocupe todo el espacio interno. "
    "Tu equilibrio aparece cuando puedes integrarla con presencia y sin miedo a lo que muestra."
),

("Luna","Lilith","⚻"): (
    "Existe un ajuste constante entre necesidad emocional y fuerza instintiva. A veces necesitas cuidado, cercanía y sostén emocional. "
    "Y otras veces aparece una necesidad muy fuerte de romper con aquello que se siente demasiado condicionado, invasivo o limitante. "
    "Tu regulación necesita escuchar ambas capas sin dejar que una silencie completamente a la otra."
),

("Luna","Nodo Norte","="): (
    "Tu crecimiento está profundamente ligado a tu mundo emocional. Lo que aprendes a través de los vínculos, el cuidado y la forma de sentir tiene muchísimo peso en tu desarrollo personal. "
    "La dirección de tu vida no pasa por alejarte de lo emocional ni por endurecerte para dejar de sentir. "
    "Pasa por aprender a habitar todo eso con más consciencia, presencia y capacidad de sostén interno."
),

("Luna","Nodo Norte","□"): (
    "Tu mundo emocional puede entrar en tensión con la dirección de crecimiento que la vida intenta abrir para ti. A veces lo que resulta emocionalmente familiar o cómodo no es necesariamente lo que más ayuda a avanzar. "
    "Existe tendencia a volver a patrones conocidos porque generan sensación de seguridad, incluso cuando ya no acompañan tu evolución actual. "
    "Tu regulación mejora cuando puedes distinguir entre seguridad conocida y crecimiento real."
),

("Luna","Nodo Norte","☍"): (
    "Existe tensión entre lo emocionalmente conocido y la dirección hacia la que tu vida intenta moverse. Puede haber atracción hacia formas antiguas de pertenencia, cuidado o refugio emocional aunque ya no sostengan realmente tu desarrollo actual. "
    "Lo familiar puede sentirse seguro incluso cuando limita profundamente el movimiento o el crecimiento. "
    "Tu equilibrio aparece cuando puedes honrar lo vivido sin quedarte atrapado dentro de ello."
),

("Luna","Nodo Norte","△"): (
    "Tu mundo emocional acompaña de forma bastante natural tu dirección de crecimiento. Cuando escuchas honestamente lo que sientes, suelen aparecer señales bastante claras sobre hacia dónde avanzar y qué necesita realmente tu vida en ese momento. "
    "La sensibilidad emocional puede funcionar aquí como una brújula muy precisa. "
    "Atender lo interno no te aleja del camino, sino que muchas veces te ayuda a encontrarlo."
),

("Luna","Nodo Norte","✶"): (
    "Existe una vía favorable entre tu mundo emocional y tu dirección de crecimiento. Los vínculos, el cuidado y la manera en que aprendes a sostenerte emocionalmente pueden abrir caminos muy importantes en tu vida. "
    "Cuando atiendes lo emocional con honestidad, también empiezan a moverse cosas relacionadas con tu desarrollo y tu dirección vital. "
    "Aquí regulación y crecimiento no aparecen separados."
),

("Luna","Nodo Norte","⚻"): (
    "Existe un ajuste constante entre tus necesidades emocionales y la dirección de crecimiento que la vida te pide. A veces lo que calma o da seguridad no es exactamente lo que ayuda a avanzar. "
    "Y otras veces crecer implica modificar formas antiguas de protección o seguridad emocional. "
    "Tu equilibrio depende mucho de revisar esa tensión con honestidad y escuchar qué necesita realmente cada momento."
),

("Luna","Nodo Sur","="): (
    "Tu mundo emocional está muy ligado a patrones antiguos y conocidos. Hay formas de sentir, cuidar o buscar seguridad que aparecen automáticamente porque llevan mucho tiempo dentro de ti. "
    "Eso puede darte profundidad emocional y mucha sensibilidad hacia el mundo íntimo, pero también hacer que permanezcas en dinámicas que ya no necesitas repetir. "
    "Tu regulación necesita distinguir entre refugio verdadero y permanencia automática en lo conocido."
),

("Luna","Nodo Sur","□"): (
    "Hay patrones emocionales antiguos que pueden generar tensión interna en el presente. A veces reaccionas desde una memoria emocional que ya no corresponde completamente a la situación actual. "
    "Algo se activa ahora, pero la respuesta puede venir de un lugar mucho más antiguo dentro de ti. "
    "El aprendizaje está en reconocer cuándo algo pertenece realmente al presente y cuándo responde a formas anteriores de protección emocional."
),

("Luna","Nodo Sur","☍"): (
    "Existe una atracción muy fuerte hacia formas conocidas de seguridad emocional. Aunque una parte de ti quiera avanzar, otra puede volver automáticamente hacia dinámicas familiares incluso cuando ya no sostienen realmente tu crecimiento. "
    "Lo conocido puede sentirse como refugio aunque limite el movimiento o la evolución. "
    "Tu regulación aparece cuando dejas de confundir familiaridad con verdadero sostén emocional."
),

("Luna","Nodo Sur","△"): (
    "Existe una memoria emocional disponible como recurso interno. Hay formas de cuidado, sensibilidad o pertenencia que reconoces con mucha facilidad y que pueden ayudarte a sostenerte en momentos difíciles. "
    "La clave está en utilizar esos recursos como apoyo y no como lugar donde quedarte detenido. "
    "El pasado puede sostenerte siempre que no sustituya completamente el presente."
),

("Luna","Nodo Sur","✶"): (
    "Hay recursos emocionales antiguos que pueden ayudarte mucho si los utilizas con consciencia. Ciertas formas de intuición, cuidado o memoria emocional aparecen con bastante facilidad dentro de ti. "
    "Pueden convertirse en apoyo importante siempre que no sustituyan el movimiento hacia lo nuevo o hacia aquello que todavía necesita desarrollarse. "
    "Tu regulación mejora cuando lo conocido acompaña, pero no dirige completamente el proceso."
),

("Luna","Nodo Sur","⚻"): (
    "Existe un ajuste constante entre formas emocionales antiguas y necesidades actuales. A veces vuelves automáticamente a patrones conocidos porque generan sensación inmediata de calma o refugio. "
    "Pero no siempre aquello que resulta familiar es lo que realmente ayuda a crecer o sostenerte en el presente. "
    "Tu equilibrio depende mucho de distinguir entre refugio real y repetición automática."
),

}

# ─── CÁLCULO ASTROLÓGICO ──────────────────────────────────────────────────────

def geocodificar(ciudad):
    g = Nominatim(user_agent="ai_luna_c4c6", timeout=10)
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

def _chiron_kepler(jd):
    jd_peri, period, e, peri_lon = 2450128.5, 18412.3, 0.383, 188.76
    M = math.radians(((jd - jd_peri) / period * 360.0) % 360.0)
    E = M
    for _ in range(50):
        dE = (M - E + e * math.sin(E)) / (1.0 - e * math.cos(E))
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


    # Lilith
    pos_li, _ = swe.calc_ut(jd, LILITH_ID, FLAGS)
    signo_li, grado_li = grados_a_signo(pos_li[0])
    planetas["Lilith"] = {
        "simbolo":"⚸","lon":pos_li[0],"signo":signo_li,"grado":grado_li,"retrogrado":False
    }

    # Nodos
    pos_nn, _ = swe.calc_ut(jd, swe.TRUE_NODE, FLAGS)
    signo_nn, grado_nn = grados_a_signo(pos_nn[0])
    lon_ns = (pos_nn[0] + 180) % 360
    signo_ns, grado_ns = grados_a_signo(lon_ns)
    planetas["Nodo Norte"] = {
        "simbolo":"☊","lon":pos_nn[0],"signo":signo_nn,"grado":grado_nn,"retrogrado":False
    }
    planetas["Nodo Sur"] = {
        "simbolo":"☋","lon":lon_ns,"signo":signo_ns,"grado":grado_ns,"retrogrado":False
    }

    # Casas Placidus
    cuspides, ascmc = swe.houses(jd, lat, lon, b'P')
    asc_lon, mc_lon = ascmc[0], ascmc[1]
    signo_asc, grado_asc = grados_a_signo(asc_lon)
    signo_mc,  grado_mc  = grados_a_signo(mc_lon)

    def casa_de(p_lon):
        for i in range(12):
            c_ini = cuspides[i]
            c_fin = cuspides[(i+1) % 12]
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


def calcular_aspectos_luna(planetas):
    luna = planetas.get("Luna")
    if not luna:
        return []
    lon_luna = luna["lon"]
    aspectos = []
    for nombre, p in planetas.items():
        if nombre == "Luna":
            continue
        diff = abs(lon_luna - p["lon"]) % 360
        if diff > 180:
            diff = 360 - diff
        for tipo, angulo, orbe_max, simbolo in ASPECTOS_DEF:
            if abs(diff - angulo) <= orbe_max:
                orbe_val = round(abs(diff - angulo), 2)
                aspectos.append({
                    "planeta": nombre,
                    "tipo": tipo,
                    "simbolo": simbolo,
                    "orbe": orbe_val,
                    "relevancia": "exacto" if orbe_val <= 1.0 else "estructural",
                })
                break
    return sorted(aspectos, key=lambda x: x["orbe"])


def planetas_en_casa(planetas, num_casa):
    excluir = {"Nodo Norte", "Nodo Sur"}
    return [n for n, p in planetas.items()
            if p.get("casa") == num_casa and n not in excluir]


def signo_cuspide_casa(cuspides, num_casa):
    lon = cuspides[num_casa - 1]
    signo, _ = grados_a_signo(lon)
    return signo


# ─── HELPERS DE TEXTO ─────────────────────────────────────────────────────────

def _desc_casa_breve(n):
    d = {
        1:  "la identidad y el cuerpo",
        2:  "los recursos y el valor propio",
        3:  "la comunicación y el entorno cercano",
        4:  "las raíces y el hogar interno",
        5:  "la creatividad y la expresión",
        6:  "el trabajo y la regulación cotidiana",
        7:  "las relaciones y las asociaciones",
        8:  "los procesos intensos y la intimidad profunda",
        9:  "la búsqueda de sentido y la ampliación de horizontes",
        10: "la vocación y el espacio público",
        11: "la comunidad y los proyectos colectivos",
        12: "la vida interna y la necesidad de retiro",
    }
    return d.get(n, "la vida")


def _desc_elemento_breve(elem):
    return {
        "Fuego":  "activa y directa",
        "Tierra": "concreta y sostenida",
        "Aire":   "mental y relacional",
        "Agua":   "receptiva y emocional",
    }.get(elem, "particular")


def _con_articulo(planeta):
    articulos = {
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
        "Quirón": "Quirón",
        "Lilith": "Lilith",
        "Nodo Norte": "el Nodo Norte",
        "Nodo Sur": "el Nodo Sur",
    }
    return articulos.get(planeta, planeta)


def lista_y(items):
    if not items:
        return ""

    items = [_con_articulo(item) for item in items]

    if len(items) == 1:
        return items[0]

    if len(items) == 2:
        return f"{items[0]} y {items[1]}"

    return ", ".join(items[:-1]) + f" y {items[-1]}"


# ─── GENERACIÓN DE TEXTOS ─────────────────────────────────────────────────────

def texto_luna_completo(planetas, aspectos_luna):
    luna  = planetas.get("Luna", {})
    signo = luna.get("signo", "")
    casa  = luna.get("casa", "")

    partes = []

    t_signo = LUNA_SIGNO.get(signo, "")
    if t_signo:
        partes.append(t_signo)

    t_casa = LUNA_CASA.get(casa, "")
    if t_casa:
        partes.append(t_casa)

    if aspectos_luna:
        _exactos = [a for a in aspectos_luna if a.get("relevancia") == "exacto"]
        _estruc  = [a for a in aspectos_luna if a.get("relevancia") == "estructural"]
        asp_relevantes = (_exactos + _estruc)[:6]

        for a in asp_relevantes:
            p2  = a["planeta"]
            sim = a["simbolo"]

            clave1 = ("Luna", p2, sim)
            clave2 = (p2, "Luna", sim)

            t_asp = ASPECTOS_LUNA.get(clave1) or ASPECTOS_LUNA.get(clave2)

            if t_asp:
                partes.append(t_asp)

    return "\n\n".join(partes)


def texto_casa4(planetas, cuspides):
    signo_c4    = signo_cuspide_casa(cuspides, 4)
    planetas_c4 = planetas_en_casa(planetas, 4)

    partes = []

    t_base = CASA4_SIGNO.get(signo_c4, "")
    if t_base:
        partes.append(t_base)

    regente = REGENTE_SIGNO.get(signo_c4, "")

    if regente and regente in planetas:
        p_reg     = planetas[regente]
        casa_reg  = p_reg.get("casa", "")
        signo_reg = p_reg.get("signo", "")

        partes.append(
            f"El regente de la Casa 4 es {_con_articulo(regente)}, en {signo_reg} "
            f"y en Casa {casa_reg}. La base interna tiende a organizarse desde "
            f"{_desc_casa_breve(casa_reg)}, "
            f"con la cualidad {_desc_elemento_breve(ELEMENTO_SIGNO.get(signo_reg, ''))} "
            f"de {signo_reg}."
        )

    for nombre in planetas_c4:
        t_p = PLANETA_CASA4.get(nombre, "")
        if t_p:
            partes.append(t_p)

    return "\n\n".join(partes)


def texto_casa6(planetas, cuspides):
    signo_c6    = signo_cuspide_casa(cuspides, 6)
    planetas_c6 = planetas_en_casa(planetas, 6)

    partes = []

    t_base = CASA6_SIGNO.get(signo_c6, "")
    if t_base:
        partes.append(t_base)

    regente = REGENTE_SIGNO.get(signo_c6, "")

    if regente and regente in planetas:
        p_reg     = planetas[regente]
        casa_reg  = p_reg.get("casa", "")
        signo_reg = p_reg.get("signo", "")

        partes.append(
            f"El regente de la Casa 6 es {_con_articulo(regente)}, en {signo_reg} "
            f"y en Casa {casa_reg}. La regulación cotidiana tiende a organizarse "
            f"desde {_desc_casa_breve(casa_reg)}, "
            f"con la cualidad {_desc_elemento_breve(ELEMENTO_SIGNO.get(signo_reg, ''))} "
            f"de {signo_reg}."
        )

    for nombre in planetas_c6:
        t_p = PLANETA_CASA6.get(nombre, "")
        if t_p:
            partes.append(t_p)

    return "\n\n".join(partes)

def texto_integracion(planetas, cuspides, aspectos_luna):
    luna        = planetas.get("Luna", {})
    signo_luna  = luna.get("signo", "")
    casa_luna   = luna.get("casa", "")
    signo_c4    = signo_cuspide_casa(cuspides, 4)
    signo_c6    = signo_cuspide_casa(cuspides, 6)
    elem_luna   = ELEMENTO_SIGNO.get(signo_luna, "")
    elem_c4     = ELEMENTO_SIGNO.get(signo_c4, "")
    elem_c6     = ELEMENTO_SIGNO.get(signo_c6, "")

    planetas_c4 = planetas_en_casa(planetas, 4)
    planetas_c6 = planetas_en_casa(planetas, 6)

    tensiones = [a for a in aspectos_luna if a["simbolo"] in ("□", "☍", "⚻")]
    apoyos    = [a for a in aspectos_luna if a["simbolo"] in ("△", "✶", "=")]

    apertura = (
        f"Tu Luna en {signo_luna} muestra cómo reaccionas emocionalmente cuando algo te afecta.\n\n"

        f"Es el primer movimiento: lo que aparece antes de que puedas ordenarlo, explicarlo o decidir qué hacer con ello.\n\n"

        f"Después, esa emoción busca un lugar donde apoyarse. "
        f"Ahí entra tu Casa 4, con {signo_c4} en la cúspide: "
        f"la parte de ti que necesita sentir base, refugio y seguridad interna.\n\n"

        f"Si esa base está disponible, lo que sientes puede moverse con más facilidad.\n"
        f"Si no lo está, la emoción se queda más tiempo en estado de alerta.\n\n"

        f"Y lo que no encuentra apoyo interno termina llegando al cuerpo. "
        f"Ahí entra tu Casa 6, con {signo_c6} en la cúspide: "
        f"tus hábitos, tu energía diaria, tu descanso y la forma en que el cuerpo sostiene lo que vives.\n\n"

        f"Por eso, cuando algo se desordena emocionalmente, no se queda solo en lo emocional. "
        f"Puede acabar apareciendo como cansancio, pérdida de ritmo, dificultad para descansar "
        f"o sensación de no poder sostener el día con la misma energía."
    )

    if elem_luna == elem_c4 == elem_c6:
        elem_coherencia = (
            f"En tu caso, las tres capas comparten el elemento {elem_luna}.\n\n"

            f"Esto hace que emoción, base interna y cuerpo hablen un idioma parecido.\n\n"

            f"Cuando una parte se estabiliza, puede ayudar a las otras a volver al centro. "
            f"Pero cuando una se altera, la activación también puede propagarse rápido.\n\n"

            f"Una emoción intensa puede mover tu sensación de seguridad interna. "
            f"Y si esa base se mueve, el cuerpo puede notarlo enseguida."
        )

    elif elem_luna == elem_c4:
        elem_coherencia = (
            f"Tu Luna y tu Casa 4 comparten el elemento {elem_luna}.\n\n"

            f"Eso significa que lo que sientes y lo que necesitas para sentir base interna "
            f"tienen un lenguaje parecido.\n\n"

            f"Cuando emocionalmente algo se activa, una parte profunda de ti reconoce bastante rápido "
            f"qué necesita para sentirse más segura.\n\n"

            f"La Casa 6, en cambio, está en {elem_c6}. "
            f"Tu cuerpo y tus hábitos funcionan con otra lógica.\n\n"

            f"Puede que entiendas emocionalmente lo que necesitas, "
            f"pero aun así te cueste llevarlo al ritmo cotidiano, al descanso, al cuerpo o a la rutina."
        )

    elif elem_luna == elem_c6:
        elem_coherencia = (
            f"Tu Luna y tu Casa 6 comparten el elemento {elem_luna}.\n\n"

            f"Esto hace que emoción y cuerpo estén muy conectados.\n\n"

            f"Lo que sientes puede notarse rápido en tu energía, en tus hábitos, en tu descanso "
            f"o en la forma en que sostienes el día.\n\n"

            f"También ocurre al revés: cuando el cuerpo pierde ritmo, descanso o estabilidad, "
            f"tu mundo emocional lo percibe enseguida.\n\n"

            f"La Casa 4, en cambio, está en {elem_c4}. "
            f"Tu base interna necesita otro tipo de sostén.\n\n"

            f"Puede que el cuerpo ya esté mostrando lo que ocurre "
            f"mientras una parte más profunda de ti todavía intenta encontrar seguridad."
        )

    elif elem_c4 == elem_c6:
        elem_coherencia = (
            f"Tu Casa 4 y tu Casa 6 comparten el elemento {elem_c4}.\n\n"

            f"Esto une directamente tu sensación de base interna con el cuerpo y la vida cotidiana.\n\n"

            f"Cuando tu entorno íntimo está más estable, tu cuerpo suele regularse mejor. "
            f"Y cuando tus hábitos están cuidados, también aparece más sensación de seguridad interna.\n\n"

            f"La Luna, en cambio, está en {elem_luna}. "
            f"Tu reacción emocional inicial puede ir a otro ritmo.\n\n"

            f"Puede que lo primero que sientas no sea exactamente lo mismo que después necesita tu cuerpo "
            f"para volver a estabilizarse."
        )

    else:
        elem_coherencia = (
            f"En tu caso, las tres capas tienen elementos distintos: "
            f"{elem_luna} en la Luna, {elem_c4} en la Casa 4 y {elem_c6} en la Casa 6.\n\n"

            f"Esto significa que tu emoción, tu base interna y tu cuerpo no siempre piden lo mismo.\n\n"

            f"Lo que te ayuda emocionalmente puede no ser lo que tu cuerpo necesita ese día. "
            f"Lo que te da seguridad interna puede no coincidir con el ritmo que sostiene tu rutina.\n\n"

            f"Por eso es importante no buscar una única respuesta para todo. "
            f"A veces una parte de ti necesita expresión, otra necesita refugio "
            f"y otra necesita descanso, orden o movimiento."
        )

    partes = [apertura, elem_coherencia]

    if planetas_c4:
        partes.append(
            f"Además, {lista_y(planetas_c4)} en la Casa 4 influye directamente en tu sensación de base interna.\n\n"

            f"Cuando buscas seguridad, refugio o estabilidad emocional profunda, "
            f"esa energía ya está presente ahí.\n\n"

            f"Por eso tu forma de sentir hogar, intimidad y raíz no depende solo del signo de la Casa 4. "
            f"También está marcada por lo que esos planetas activan dentro de ti."
        )

    if planetas_c6:
        partes.append(
            f"Además, {lista_y(planetas_c6)} en la Casa 6 influye en cómo tu cuerpo sostiene la vida cotidiana.\n\n"

            f"No se trata solo de hábitos o rutina. "
            f"Se trata de cómo organizas tu energía, cómo respondes al cansancio "
            f"y qué ocurre cuando el cuerpo empieza a pedir ajuste.\n\n"

            f"Esos planetas muestran qué tipo de fuerza, sensibilidad o tensión entra en tu regulación diaria."
        )

    if tensiones:
        nombres_t = [a["planeta"] for a in tensiones[:3]]
        texto_tensiones = (
            f"Los aspectos de tensión con {lista_y(nombres_t)} hacen que el mundo emocional tenga menos margen en ciertos momentos.\n\n"

            f"Cuando algo te activa, puede haber menos tiempo entre sentir y reaccionar. "
            f"La emoción puede llegar más intensa, más mezclada o más difícil de ordenar.\n\n"

            f"Esto no significa que sí o sí vayas a desregularte. "
            f"Significa que necesitas reconocer antes las señales iniciales, "
            f"porque cuando la activación ya ha subido mucho, cuesta más volver al centro."
        )

        if apoyos:
            nombres_a = [a["planeta"] for a in apoyos[:3]]
            texto_tensiones += (
                f"\n\nAl mismo tiempo, los aspectos de apoyo con {lista_y(nombres_a)} ofrecen recursos reales.\n\n"

                f"Cuando consigues encontrar un primer punto de estabilidad, "
                f"esos aspectos ayudan a sostenerlo.\n\n"

                f"No eliminan la tensión, pero pueden facilitar que vuelvas a organizarte "
                f"sin quedarte completamente dentro de lo que se activó."
            )

        partes.append(texto_tensiones)

    elif apoyos:
        nombres_a = [a["planeta"] for a in apoyos[:3]]
        partes.append(
            f"Los aspectos de apoyo con {lista_y(nombres_a)} facilitan la regulación emocional.\n\n"

            f"Cuando algo te afecta, existe más posibilidad de encontrar un recurso interno, "
            f"una vía de expresión o un punto de estabilidad desde el que recomponerte.\n\n"

            f"Eso no significa que no haya intensidad emocional. "
            f"Significa que tienes más caminos disponibles para volver a sostenerte."
        )

    cierre = (
        f"Lo más difícil no suele ser que una sola parte se altere.\n\n"

        f"Lo más difícil aparece cuando las tres capas se mueven al mismo tiempo:\n"
        f"la Luna en {signo_luna}, con su forma concreta de sentir;\n"
        f"la Casa 4 en {signo_c4}, con su necesidad de base y seguridad interna;\n"
        f"y la Casa 6 en {signo_c6}, con el cuerpo intentando sostenerlo todo en la vida diaria.\n\n"

        f"Cuando esto ocurre, puedes notar que no sabes por dónde empezar: "
        f"emocionalmente hay activación, internamente falta suelo "
        f"y el cuerpo empieza a mostrar cansancio, tensión o pérdida de ritmo.\n\n"

        f"El trabajo no consiste en resolverlo todo a la vez.\n\n"

        f"Consiste en encontrar la primera capa disponible: "
        f"una emoción que pueda expresarse, un entorno que pueda darte más seguridad, "
        f"o una acción corporal sencilla que te ayude a volver poco a poco a la estabilidad."
    )

    partes.append(cierre)

    return "\n\n".join(partes)

def texto_sosten_desregulacion(planetas, cuspides, aspectos_luna):
    signo_luna = planetas.get("Luna", {}).get("signo", "")
    signo_c4   = signo_cuspide_casa(cuspides, 4)
    signo_c6   = signo_cuspide_casa(cuspides, 6)

    tensiones  = [a for a in aspectos_luna if a["simbolo"] in ("□", "☍", "⚻")]
    apoyos     = [a for a in aspectos_luna if a["simbolo"] in ("△", "✶", "=")]

    nombres_t  = [a["planeta"] for a in tensiones[:3]]
    nombres_a  = [a["planeta"] for a in apoyos[:2]]

    desborde = (
        f"Tu Luna en {signo_luna} se desregula cuando lo que sientes no encuentra salida.\n\n"

        f"Puede ser porque no puedes expresarlo, porque no hay espacio para moverte, "
        f"porque el entorno no lo recibe o porque intentas sostenerlo demasiado tiempo dentro.\n\n"

        f"No siempre hace falta que ocurra algo muy intenso.\n\n"

        f"A veces basta con acumular durante demasiado tiempo una emoción que no ha tenido lugar, "
        f"palabra, movimiento o descanso."
    )

    if nombres_t:
        desborde += (
            f"\n\nLos aspectos de tensión con {lista_y(nombres_t)} hacen que ese margen sea más estrecho.\n\n"

            f"Cuando algo te activa, puede haber menos tiempo entre sentir y reaccionar.\n\n"

            f"La emoción puede llegar más fuerte, más mezclada o más difícil de ordenar. "
            f"Por eso es importante reconocer las primeras señales antes de llegar al punto de desborde."
        )

    bloqueo_c4 = (
        f"Tu Casa 4 con {signo_c4} pierde estabilidad cuando dejas de sentir base interna.\n\n"

        f"No siempre tiene que haber un conflicto claro.\n\n"

        f"A veces basta con que cambie el clima emocional del entorno, "
        f"con que una relación cercana se tense, "
        f"con que no puedas descansar de verdad "
        f"o con que el espacio íntimo deje de sentirse seguro.\n\n"

        f"Cuando eso ocurre, no solo cambia el ánimo. "
        f"Cambia la sensación de tener suelo por dentro."
    )

    bloqueo_c6 = (
        f"Tu Casa 6 con {signo_c6} muestra la desregulación en el cuerpo y en la vida cotidiana.\n\n"

        f"Puede aparecer como cansancio, pérdida de ritmo, tensión física, sueño menos reparador "
        f"o dificultad para sostener hábitos que normalmente sí puedes sostener.\n\n"

        f"Muchas veces el cuerpo avisa antes de que puedas explicar qué está pasando.\n\n"

        f"Cuando el cuerpo empieza a perder continuidad, "
        f"conviene mirar también qué emoción no ha encontrado salida "
        f"y qué parte de tu base interna ha dejado de sentirse segura."
    )

    convergencia = (
        f"Los momentos más difíciles aparecen cuando las tres capas se mueven a la vez.\n\n"

        f"La Luna en {signo_luna} se activa.\n"
        f"La Casa 4 en {signo_c4} deja de sentirse como base.\n"
        f"Y la Casa 6 en {signo_c6} empieza a mostrarlo en el cuerpo, el descanso o la rutina.\n\n"

        f"Ahí puedes sentir que no sabes por dónde empezar.\n\n"

        f"No se trata de resolverlo todo a la vez.\n"
        f"Se trata de encontrar la primera capa disponible: "
        f"expresar algo, descansar, ordenar una pequeña rutina, moverte, pedir espacio "
        f"o recuperar una mínima sensación de seguridad."
    )

    partes_sosten = []

    if nombres_a:
        partes_sosten.append(
            f"Los aspectos de apoyo con {lista_y(nombres_a)} funcionan como recursos cuando consigues recuperar un primer punto de estabilidad.\n\n"

            f"No eliminan la desregulación, pero pueden ayudarte a reorganizarte antes.\n\n"

            f"Cuando aparece una mínima base, esos aspectos facilitan que no te quedes dentro "
            f"de lo que se activó."
        )

    partes = [
        desborde,
        bloqueo_c4,
        bloqueo_c6,
        convergencia
    ]

    partes.extend(partes_sosten)

    return "\n\n".join(partes)

def texto_orientacion_final(planetas, cuspides, aspectos_luna):
    luna        = planetas.get("Luna", {})
    signo_luna  = luna.get("signo", "")
    casa_luna   = luna.get("casa", "")
    signo_c4    = signo_cuspide_casa(cuspides, 4)
    signo_c6    = signo_cuspide_casa(cuspides, 6)
    elem_c6     = ELEMENTO_SIGNO.get(signo_c6, "")

    observar = (
        f"Empieza observando qué situaciones activan tu Luna en {signo_luna}.\n\n"

        f"No para corregirte.\n"
        f"No para controlar lo que sientes.\n\n"

        f"Solo para reconocer antes cómo empieza la activación.\n\n"

        f"¿Qué ocurre justo antes de sentirte que la situación te sobrepasa?\n"
        f"¿Qué cambia en el entorno, en los vínculos o en el ritmo diario?\n\n"

        f"Muchas veces la desregulación no empieza en el momento del desborde. "
        f"Empieza bastante antes: "
        f"cuando tu Casa 4 en {signo_c4} deja de sentirse segura "
        f"o cuando tu Casa 6 en {signo_c6} pierde continuidad y el cuerpo empieza a acumular tensión."
    )

    desregula = (
        f"En tu caso, la desregulación suele seguir una secuencia.\n\n"

        f"Primero, tu Luna en {signo_luna} busca algo que necesita para estabilizarse "
        f"y no lo encuentra.\n\n"

        f"Después, tu Casa 4 deja de funcionar como base interna. "
        f"Puede ser por tensión emocional, por cambios en el entorno, "
        f"por exceso de carga o simplemente porque llevas demasiado tiempo sosteniendo más de lo que puedes absorber.\n\n"

        f"Y finalmente, la Casa 6 en {signo_c6} empieza a mostrarlo en el cuerpo:\n"
        f"menos energía,\n"
        f"menos descanso,\n"
        f"menos capacidad de sostener hábitos o continuidad.\n\n"

        f"Cuando las tres capas coinciden, puedes sentir que todo cuesta más de lo habitual "
        f"aunque desde fuera no parezca estar ocurriendo nada tan grave."
    )

    sostiene = (
        f"Lo que te ayuda a regularte no tiene que ser enorme.\n\n"

        f"De hecho, muchas veces lo más importante son cosas pequeñas que se sostienen en el tiempo.\n\n"

        f"Una mínima rutina corporal.\n"
        f"Un espacio de descanso real.\n"
        f"Un entorno que se sienta más seguro.\n"
        f"Una forma de expresar lo que ocurre antes de acumularlo demasiado.\n\n"

        f"Cuando tu Casa 4 siente suelo, tu Luna necesita menos esfuerzo para estabilizarse.\n\n"

        f"Y cuando tu Casa 6 mantiene cierta continuidad —aunque sea pequeña— "
        f"el cuerpo puede absorber mejor lo que emocionalmente estás atravesando.\n\n"

        f"No se trata de no sentir.\n"
        f"Se trata de que lo que sientes no tenga que terminar descargándose siempre en agotamiento, tensión o pérdida de equilibrio."
    )

    practicas = {
        "Fuego": (
            "Tu regulación necesita movimiento.\n\n"

            "Dedica unos minutos al día a mover el cuerpo conscientemente.\n\n"

            "No hace falta intensidad extrema. "
            "Hace falta salida.\n\n"

            "Caminar rápido, movilizar el cuerpo, sacudir tensión o activar la respiración "
            "puede ayudar a que la energía no se quede acumulada internamente.\n\n"

            "Cuando el cuerpo puede descargar, la emoción también encuentra más espacio para ordenarse."
        ),

        "Tierra": (
            "Tu regulación necesita repetición y continuidad.\n\n"

            "Elige una práctica corporal o cotidiana sencilla y mantenla estable en el tiempo.\n\n"

            "Puede ser desayunar sin prisa, salir unos minutos al exterior, "
            "tener una rutina de descanso o respirar conscientemente siempre en el mismo momento del día.\n\n"

            "Lo importante no es la intensidad.\n"
            "Es la constancia.\n\n"

            "La repetición le transmite seguridad al sistema nervioso."
        ),

        "Aire": (
            "Tu regulación necesita expresión mental y espacio para ordenar lo que ocurre.\n\n"

            "Reserva unos minutos al día para escribir, hablar o simplemente nombrar tu estado interno.\n\n"

            "No hace falta entenderlo todo.\n"
            "Hace falta que no se quede circulando continuamente dentro.\n\n"

            "Cuando encuentras palabras, dejas de sostener tanta carga en silencio."
        ),

        "Agua": (
            "Tu regulación necesita vaciado emocional.\n\n"

            "Dedica un momento del día a cerrar lo absorbido:\n"
            "silencio,\n"
            "respiración,\n"
            "una ducha consciente,\n"
            "música tranquila,\n"
            "o simplemente estar sin estímulos.\n\n"

            "No es una pausa superficial.\n"
            "Es una forma de ayudarte a soltar lo que has ido acumulando.\n\n"

            "Cuando no existe ese cierre, el cuerpo sigue cargando emociones incluso mientras intenta descansar."
        ),
    }

    practica = practicas.get(elem_c6, (
        "Busca una práctica corporal sencilla que puedas sostener cada día.\n\n"

        "No necesitas hacerlo perfecto.\n"
        "Necesitas que exista continuidad.\n\n"

        "Lo pequeño y estable suele regular más que los grandes cambios que duran poco."
    ))

    return {
        "observar":  observar,
        "desregula": desregula,
        "sostiene":  sostiene,
        "practica":  practica,
    }

# ─── ESCAPADO LATEX ───────────────────────────────────────────────────────────

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


# ─── RUEDA FILTRADA LUNA ──────────────────────────────────────────────────────

def dibujar_rueda_luna(carta, aspectos_luna, archivo_salida):
    """Rueda filtrada: Luna, regentes C4/C6 y planetas en aspecto con Luna."""
    ORBES_ESTRICTOS = {
        "=": 10.0,
        "✶": 6.0,
        "□": 8.0,
        "△": 8.0,
        "⚻": 4.0,
        "☍": 8.0,
    }

    planetas = carta["planetas"]
    cuspides = carta["cuspides"]
    asc_lon  = carta["asc"]["lon"]

    signo_c4   = signo_cuspide_casa(cuspides, 4)
    signo_c6   = signo_cuspide_casa(cuspides, 6)
    regente_c4 = REGENTE_SIGNO.get(signo_c4, "")
    regente_c6 = REGENTE_SIGNO.get(signo_c6, "")

    asp_estrictos = []

    for a in aspectos_luna:
        sim = a["simbolo"]
        orbe_max = ORBES_ESTRICTOS.get(sim, 0)

        # Oposición ampliada a 10° si participa Sol o Luna
        if sim == "☍":
            p1 = a.get("p1", "Luna")
            p2 = a.get("p2", a.get("planeta", ""))

            if p1 in ("Sol", "Luna") or p2 in ("Sol", "Luna"):
                orbe_max = 10.0

        if a["orbe"] <= orbe_max:
            asp_estrictos.append(a)

    planetas_mostrar = {"Luna"}
    if regente_c4 and regente_c4 in planetas:
        planetas_mostrar.add(regente_c4)
    if regente_c6 and regente_c6 in planetas:
        planetas_mostrar.add(regente_c6)
    for a in asp_estrictos:
        if a["planeta"] in planetas:
            planetas_mostrar.add(a["planeta"])

    def lon_a_angulo(lon):
        return math.radians(180 + (lon - asc_lon))

    R_EXT = 1.35; R_SIGN_IN = 1.05
    R_CASA_OUT = 1.02; R_CASA_IN = 0.65; R_PLANETA = 0.82

    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    ax.set_aspect('equal'); ax.axis('off')
    ax.set_xlim(-1.55, 1.55); ax.set_ylim(-1.55, 1.55)

    # Bandas de signos
    for i, signo in enumerate(SIGNOS):
        elem  = ELEMENTO_SIGNO[signo]
        color = COLORES_ELEMENTO[elem]
        ang_ini = lon_a_angulo(i * 30)
        ang_fin = lon_a_angulo((i + 1) * 30)
        theta = np.linspace(ang_ini, ang_fin, 50)
        xs = [math.cos(a) * R_EXT for a in theta] + [math.cos(a) * R_SIGN_IN for a in reversed(theta)]
        ys = [math.sin(a) * R_EXT for a in theta] + [math.sin(a) * R_SIGN_IN for a in reversed(theta)]
        ax.fill(xs, ys, color=color, alpha=0.22, zorder=1)

    # Círculos
    for r, lw, c in [(R_EXT, 2, '#333'), (R_SIGN_IN, 1.5, '#333'),
                     (R_CASA_IN, 1.5, '#555'), (0.25, 1, '#888')]:
        ax.add_patch(plt.Circle((0, 0), r, fill=False, color=c, linewidth=lw, zorder=2))

    # Divisiones de signos
    for i in range(12):
        ang = lon_a_angulo(i * 30)
        ax.plot([math.cos(ang) * R_SIGN_IN, math.cos(ang) * R_EXT],
                [math.sin(ang) * R_SIGN_IN, math.sin(ang) * R_EXT],
                color='#666', linewidth=0.7, zorder=2)

    # Símbolos de signos
    for i, (signo, simbolo) in enumerate(zip(SIGNOS, SIMBOLOS_SIGNOS)):
        ang_mid = lon_a_angulo(i * 30 + 15)
        r_mid   = (R_SIGN_IN + R_EXT) / 2
        elem    = ELEMENTO_SIGNO[signo]
        ax.text(math.cos(ang_mid) * r_mid, math.sin(ang_mid) * r_mid, simbolo,
                ha='center', va='center', fontsize=16, color=COLORES_ELEMENTO[elem],
                fontweight='bold', alpha=0.65, zorder=5)

    # Cúspides de casas
    for i, cusp in enumerate(cuspides):
        ang = lon_a_angulo(cusp)
        lw  = 1.8 if i in (0, 3, 6, 9) else 0.6
        col = '#111' if i in (0, 3, 6, 9) else '#888'
        ax.plot([math.cos(ang) * R_CASA_IN, math.cos(ang) * R_CASA_OUT],
                [math.sin(ang) * R_CASA_IN, math.sin(ang) * R_CASA_OUT],
                color=col, linewidth=lw, zorder=3)
        ang_num = lon_a_angulo(cusp + 4.0)
        r_num   = (R_CASA_IN + 0.25) / 2 + 0.12
        ax.text(math.cos(ang_num) * r_num, math.sin(ang_num) * r_num, str(i + 1),
                ha='center', va='center', fontsize=7, color='#666', zorder=4)

    # Líneas de aspecto (solo Luna, orbes estrictos)
    _ASP_COL = {"□": "#CC2200", "☍": "#CC2200", "△": "#1A5FA8",
                "✶": "#1A5FA8", "⚻": "#2E7D32", "=": "#7B2D8B"}
    _ASP_LW  = {"□": 1.3, "☍": 1.3, "△": 1.1, "✶": 1.0, "⚻": 0.9, "=": 1.1}
    R_ASP = R_CASA_IN - 0.02
    a_luna = lon_a_angulo(planetas["Luna"]["lon"])
    for a in asp_estrictos:
        sim = a["simbolo"]
        if sim not in _ASP_COL: continue
        p_nombre = a["planeta"]
        if p_nombre not in planetas: continue
        a2 = lon_a_angulo(planetas[p_nombre]["lon"])
        ax.plot([math.cos(a_luna) * R_ASP, math.cos(a2) * R_ASP],
                [math.sin(a_luna) * R_ASP, math.sin(a2) * R_ASP],
                color=_ASP_COL[sim], linewidth=_ASP_LW[sim], alpha=0.60, zorder=2)

    # Planetas seleccionados
    orden = ["Sol", "Luna", "Mercurio", "Venus", "Marte", "Júpiter", "Saturno",
             "Urano", "Neptuno", "Plutón", "Quirón", "Lilith", "Nodo Norte", "Nodo Sur"]

    RADIO_BASE = R_PLANETA
    RADIO_MIN  = R_CASA_IN + 0.10
    RADIO_MAX  = R_SIGN_IN - 0.10

    CARRILES = [
        RADIO_BASE,
        min(RADIO_BASE + 0.09, RADIO_MAX),
        max(RADIO_BASE - 0.09, RADIO_MIN),
        min(RADIO_BASE + 0.16, RADIO_MAX),
        max(RADIO_BASE - 0.16, RADIO_MIN),
    ]

    planetas_ordenados = []
    for nombre in orden:
        if nombre not in planetas_mostrar or nombre not in planetas:
            continue
        lon = planetas[nombre]["lon"]
        planetas_ordenados.append((nombre, lon))

    planetas_ordenados.sort(key=lambda x: x[1])

    radios = {}

    for nombre, lon in planetas_ordenados:
        carril = CARRILES[0]

        cercanos = []
        for otro_nombre, otro_lon in planetas_ordenados:
            if otro_nombre == nombre:
                continue

            d = abs(lon - otro_lon) % 360
            if d > 180:
                d = 360 - d

            if d < 9:
                cercanos.append(otro_nombre)

        if cercanos:
            usados = [
                radios[o]
                for o in cercanos
                if o in radios
            ]

            for candidato in CARRILES:
                if all(abs(candidato - u) > 0.04 for u in usados):
                    carril = candidato
                    break

        radios[nombre] = max(RADIO_MIN, min(carril, RADIO_MAX))

    for nombre in orden:
        if nombre not in planetas_mostrar or nombre not in planetas:
            continue

        p   = planetas[nombre]
        ang = lon_a_angulo(p["lon"])
        r   = radios[nombre]

        color   = COLORES_PLANETA.get(nombre, '#333')
        simbolo = p["simbolo"] + ("ᴿ" if p.get("retrogrado") else "")
        fs = 21 if nombre == "Luna" else 17

        ax.text(
            math.cos(ang) * r,
            math.sin(ang) * r,
            simbolo,
            ha='center',
            va='center',
            fontsize=fs,
            color=color,
            fontweight='bold',
            zorder=8
        )

        # Etiqueta R4 / R6
        etq = ""
        if nombre == regente_c4 and nombre == regente_c6:
            etq = "R4·R6"
        elif nombre == regente_c4:
            etq = "R4"
        elif nombre == regente_c6:
            etq = "R6"

        if etq:
            ax.text(
                math.cos(ang) * (r + 0.14),
                math.sin(ang) * (r + 0.14),
                etq,
                ha='center',
                va='center',
                fontsize=7,
                color=color,
                fontweight='bold',
                zorder=8
            )

        # Línea hacia anillo de signos
        ax.plot(
            [math.cos(ang) * (r + 0.07), math.cos(ang) * (R_SIGN_IN + 0.01)],
            [math.sin(ang) * (r + 0.07), math.sin(ang) * (R_SIGN_IN + 0.01)],
            color=color,
            linewidth=0.8,
            alpha=0.65,
            zorder=3
        )

    # AC / DC / MC / IC
    for etq, lon_pt in [("AC", carta["asc"]["lon"]), ("DC", (carta["asc"]["lon"] + 180) % 360),
                        ("MC", carta["mc"]["lon"]),  ("IC", (carta["mc"]["lon"] + 180) % 360)]:
        ang = lon_a_angulo(lon_pt)
        ax.text(math.cos(ang) * (R_EXT + 0.11), math.sin(ang) * (R_EXT + 0.11), etq,
                ha='center', va='center', fontsize=11, fontweight='bold', color='#111', zorder=7)

    plt.title("Luna · Casa 4 · Casa 6", fontsize=12, fontweight='bold', pad=12, color='#1E508C')
    plt.tight_layout()
    plt.savefig(archivo_salida, dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()


# ─── GENERACIÓN LATEX ─────────────────────────────────────────────────────────

def generar_latex(carta, nombre, anio, mes, dia, hora, minuto,
                  ciudad, lat, lon, tz_name, aspectos_luna, ruta_rueda=None):
    planetas  = carta["planetas"]
    cuspides  = carta["cuspides"]
    asc       = carta["asc"]
    mc        = carta["mc"]
    luna      = planetas.get("Luna", {})

    fecha_str  = f"{dia:02d}/{mes:02d}/{anio}"
    hora_str   = f"{hora:02d}:{minuto:02d}"
    tz_obj     = pytz.timezone(tz_name)
    dt_local   = tz_obj.localize(datetime(anio, mes, dia, hora, minuto))
    utc_off    = dt_local.strftime("%z")
    utc_str    = f"UTC{utc_off[:3]}:{utc_off[3:]}"
    nom_esc    = esc(nombre)
    ciu_esc    = esc(ciudad)

    signo_luna  = luna.get("signo", "")
    casa_luna   = luna.get("casa", "")
    grado_luna  = luna.get("grado", 0)
    signo_c4    = signo_cuspide_casa(cuspides, 4)
    signo_c6    = signo_cuspide_casa(cuspides, 6)
    planetas_c4 = planetas_en_casa(planetas, 4)
    planetas_c6 = planetas_en_casa(planetas, 6)
    regente_c4  = REGENTE_SIGNO.get(signo_c4, "")
    regente_c6  = REGENTE_SIGNO.get(signo_c6, "")

    t_luna   = texto_luna_completo(planetas, aspectos_luna)
    t_casa4  = texto_casa4(planetas, cuspides)
    t_casa6  = texto_casa6(planetas, cuspides)
    t_integ  = texto_integracion(planetas, cuspides, aspectos_luna)
    t_sost   = texto_sosten_desregulacion(planetas, cuspides, aspectos_luna)
    t_orient = texto_orientacion_final(planetas, cuspides, aspectos_luna)

    # Tabla de aspectos lunares
    asp_rows = ""
    for a in aspectos_luna[:10]:
        asp_rows += (
            f"  Luna & {esc(a['simbolo'])} & {esc(a['planeta'])} & "
            f"{esc(a['tipo'])} & {a['orbe']:.1f}° \\\\\n"
        )

    # Bloque de imagen de la rueda (si existe)
    if ruta_rueda and os.path.exists(ruta_rueda):
        _ruta_tex = ruta_rueda.replace("\\", "/").replace("%", "\\%").replace("#", "\\#")
        rueda_bloque = (
            f"\\vspace{{0.8cm}}\n"
            f"\\begin{{center}}\n"
            f"\\includegraphics[width=0.80\\textwidth]{{{_ruta_tex}}}\n"
            f"\\end{{center}}\n"
        )
    else:
        rueda_bloque = ""

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
\\usepackage{{etoolbox}}
\\usepackage{{graphicx}}

\\widowpenalty=10000
\\clubpenalty=10000
\\displaywidowpenalty=10000
\\raggedbottom
\\sloppy
\\hbadness=10000
\\hfuzz=2pt

\\geometry{{top=3.0cm,bottom=3.0cm,left=3.5cm,right=3.5cm}}
\\setlength{{\\parskip}}{{0.65em}}
\\setlength{{\\parindent}}{{0em}}
\\setlength{{\\headheight}}{{14pt}}

\\definecolor{{azulai}}{{RGB}}{{30,80,140}}
\\definecolor{{doradoai}}{{RGB}}{{140,90,0}}
\\definecolor{{grisai}}{{RGB}}{{70,70,70}}

\\titleformat{{\\section}}{{\\Large\\bfseries\\color{{azulai}}}}{{}}{{0em}}{{}}[{{\\color{{azulai}}\\titlerule[0.5pt]}}]
\\titlespacing*{{\\section}}{{0pt}}{{1.8em}}{{0.8em}}

\\titleformat{{\\subsection}}{{\\large\\bfseries\\color{{doradoai}}}}{{}}{{0em}}{{}}
\\titlespacing*{{\\subsection}}{{0pt}}{{1.4em}}{{0.5em}}

\\titleformat{{\\subsubsection}}{{\\normalsize\\bfseries\\color{{grisai}}}}{{}}{{0em}}{{}}
\\titlespacing*{{\\subsubsection}}{{0pt}}{{1.0em}}{{0.3em}}

% Evita títulos huérfanos al final de página
\\pretocmd{{\\section}}{{\\Needspace{{12\\baselineskip}}}}{{}}{{}}
\\pretocmd{{\\subsection}}{{\\Needspace{{9\\baselineskip}}}}{{}}{{}}
\\pretocmd{{\\subsubsection}}{{\\Needspace{{6\\baselineskip}}}}{{}}{{}}

\\pagestyle{{fancy}}
\\fancyhf{{}}
\\rhead{{\\textcolor{{grisai}}{{\\small {nom_esc} — Arquitectura Interna}}}}
\\lhead{{\\textcolor{{grisai}}{{\\small Luna · Casa 4 · Casa 6}}}}
\\cfoot{{\\textcolor{{grisai}}{{\\small\\thepage}}}}
\\renewcommand{{\\headrulewidth}}{{0.3pt}}

\\hypersetup{{colorlinks=true,linkcolor=azulai,urlcolor=azulai}}
\\setstretch{{1.45}}
\\tolerance=2500
\\emergencystretch=8em

\\begin{{document}}

% ── Portada ──────────────────────────────────────────────────────────────────
\\begin{{titlepage}}
  \\centering
  \\vspace*{{1.5cm}}
  {{\\Huge\\bfseries\\color{{azulai}} Luna · Casa 4 · Casa 6}}\\\\[0.5cm]
  {{\\large\\color{{grisai}} Arquitectura Interna}}\\\\[0.3cm]
  {{\\small\\itshape\\color{{grisai}} Un método para sostener cuerpo, energía y vida con coherencia}}\\\\[2cm]
  {{\\huge\\color{{doradoai}} {nom_esc}}}\\\\[1.5cm]
  {{\\Large {fecha_str} \\quad {hora_str}}}\\\\[0.3cm]
  {{\\Large {ciu_esc}}}\\\\[0.3cm]
  {{\\normalsize Lat: {lat:.4f}° \\quad Lon: {lon:.4f}° \\quad {utc_str}}}\\\\[0.3cm]
  {{\\normalsize Ascendente: {esc(asc['signo'])} {grado_a_dms(asc['grado'])} \\quad
    MC: {esc(mc['signo'])} {grado_a_dms(mc['grado'])}}}\\\\[2cm]

  \\begin{{tabular}}{{lll}}
    \\textbf{{Luna:}} & {esc(signo_luna)} & Casa {casa_luna} \\\\
    \\textbf{{Casa 4:}} & {esc(signo_c4)} en cúspide & Regente: {esc(regente_c4)} \\\\
    \\textbf{{Casa 6:}} & {esc(signo_c6)} en cúspide & Regente: {esc(regente_c6)} \\\\
  \\end{{tabular}}\\\\[2cm]

  \\vfill
  {{\\small Generado el {datetime.now().strftime("%d/%m/%Y")}}}
\\end{{titlepage}}

\\tableofcontents
\\clearpage

% ── Datos de referencia ───────────────────────────────────────────────────────
\\section{{Datos de referencia}}

\\begin{{center}}
\\begin{{tabular}}{{llll}}
  \\toprule
  \\textbf{{Eje}} & \\textbf{{Signo}} & \\textbf{{Posición}} & \\textbf{{Datos}} \\\\
  \\midrule
  Luna & {esc(signo_luna)} & Casa {casa_luna} & {grado_a_dms(grado_luna)} \\\\
  Casa 4 (cúspide) & {esc(signo_c4)} & --- & Regente: {esc(regente_c4)} \\\\
  Casa 6 (cúspide) & {esc(signo_c6)} & --- & Regente: {esc(regente_c6)} \\\\
  Ascendente & {esc(asc['signo'])} & --- & {grado_a_dms(asc['grado'])} \\\\
  Medio Cielo & {esc(mc['signo'])} & --- & {grado_a_dms(mc['grado'])} \\\\
  \\bottomrule
\\end{{tabular}}
\\end{{center}}

\\vspace{{0.4cm}}
\\textbf{{Planetas en Casa 4:}} {esc(', '.join(planetas_c4) if planetas_c4 else 'ninguno')}\\\\
\\textbf{{Planetas en Casa 6:}} {esc(', '.join(planetas_c6) if planetas_c6 else 'ninguno')}

\\vspace{{0.5cm}}
\\textbf{{Aspectos de la Luna:}}

\\begin{{center}}
\\begin{{tabular}}{{lllll}}
  \\toprule
  & \\textbf{{Asp.}} & \\textbf{{Planeta}} & \\textbf{{Tipo}} & \\textbf{{Orbe}} \\\\
  \\midrule
{asp_rows}  \\bottomrule
\\end{{tabular}}
\\end{{center}}

{rueda_bloque}

\\vspace{{0.5cm}}
\\Needspace{{5\\baselineskip}}

% ── Interpretación ────────────────────────────────────────────────────────────
\\section{{Interpretación — Arquitectura Interna}}

\\Needspace{{8\\baselineskip}}
\\begin{{center}}
{{\\small\\itshape
No se trata de explicarte. Se trata de mostrar cómo funciona tu regulación interna,\\\\
dónde puede haber desregulación y qué necesitas para sostenerte.
}}
\\end{{center}}

\\vspace{{0.8cm}}
\\Needspace{{5\\baselineskip}}

% ── 1. Luna ───────────────────────────────────────────────────────────────────
\\subsection{{1. Tu Luna — Función emocional}}

\\subsubsection*{{Luna en {esc(signo_luna)} — Casa {casa_luna}}}

{parrafos(t_luna)}

\\vspace{{0.8cm}}
\\Needspace{{5\\baselineskip}}

% ── 2. Casa 4 ─────────────────────────────────────────────────────────────────
\\subsection{{2. Tu Casa 4 — Raíz interna}}

\\subsubsection*{{{esc(signo_c4)} en la cúspide — Regente: {esc(regente_c4)}}}

{parrafos(t_casa4)}

\\vspace{{0.8cm}}
\\Needspace{{5\\baselineskip}}

% ── 3. Casa 6 ─────────────────────────────────────────────────────────────────
\\subsection{{3. Tu Casa 6 — Regulación cotidiana}}

\\subsubsection*{{{esc(signo_c6)} en la cúspide — Regente: {esc(regente_c6)}}}

{parrafos(t_casa6)}

\\vspace{{0.8cm}}
\\Needspace{{5\\baselineskip}}

% ── 4. Integración ────────────────────────────────────────────────────────────
\\subsection{{4. Integración — Cómo funcionan las tres capas juntas}}

{parrafos(t_integ)}

\\vspace{{0.8cm}}
\\Needspace{{5\\baselineskip}}

% ── 5. Sostén y desregulación ─────────────────────────────────────────────────
\\subsection{{5. Sostén y desregulación}}

{parrafos(t_sost)}

\\vspace{{0.8cm}}
\\Needspace{{5\\baselineskip}}

% ── 6. Orientación final ──────────────────────────────────────────────────────
\\subsection{{6. Orientación final}}

\\subsubsection*{{Qué observar}}

{parrafos(t_orient['observar'])}

\\subsubsection*{{Qué puede desregularte}}

{parrafos(t_orient['desregula'])}

\\subsubsection*{{Qué te estructura y sostiene}}

{parrafos(t_orient['sostiene'])}

\\subsubsection*{{Práctica}}

{parrafos(t_orient['practica'])}

\\Needspace{{8\\baselineskip}}
\\vspace{{0.6cm}}

\\begin{{center}}
{{\\small\\itshape\\color{{grisai}}
La astrología se usa aquí como lenguaje simbólico de observación, no como definición de la persona.\\\\
Lo que tienes delante es un mapa de posibilidades, no un destino fijo.
}}
\\end{{center}}

\\end{{document}}
"""
    return latex

# ─── PROGRAMA PRINCIPAL ───────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("   LUNA, CASA 4 Y CASA 6 — Arquitectura Interna")
    print("=" * 60)
    print()

    nombre = input("Nombre completo: ").strip()
    if not nombre:
        print("El nombre no puede estar vacío.")
        sys.exit(1)

    while True:
        try:
            fecha_str = input("Fecha de nacimiento (DD/MM/AAAA): ").strip()
            dia, mes, anio = map(int, fecha_str.split("/"))
            datetime(anio, mes, dia)
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
    print("Calculando carta natal...")

    try:
        lat, lon = geocodificar(ciudad)
        print(f"  Coordenadas: {lat:.4f}°N, {lon:.4f}°E")
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
        carta = calcular_carta(anio, mes, dia, hora, minuto, lat, lon, tz_name)
        print(f"  ASC: {carta['asc']['signo']} {grado_a_dms(carta['asc']['grado'])}")
        print(f"  MC:  {carta['mc']['signo']}  {grado_a_dms(carta['mc']['grado'])}")
        luna = carta["planetas"].get("Luna", {})
        print(f"  Luna: {luna.get('signo','')} {grado_a_dms(luna.get('grado',0))} — Casa {luna.get('casa','')}")
    except Exception as e:
        print(f"Error en cálculo astrológico: {e}")
        sys.exit(1)

    aspectos_luna = calcular_aspectos_luna(carta["planetas"])
    print(f"  Aspectos lunares: {len(aspectos_luna)}")

    nombre_f = nombre.replace(" ", "_").replace("/", "-")
    ruta_base = os.path.join(BASE_DIR, nombre_f + "_Luna_C4_C6")
    ruta_tex = ruta_base + ".tex"
    ruta_pdf = ruta_base + ".pdf"
    ruta_rueda = ruta_base + "_rueda.png"

    print("  Generando rueda filtrada...")
    try:
        dibujar_rueda_luna(carta, aspectos_luna, ruta_rueda)
        print(f"  Rueda guardada: {ruta_rueda}")
    except Exception as e:
        print(f"  Aviso: no se pudo generar la rueda ({e})")
        ruta_rueda = None

    print("  Generando interpretación...")
    latex = generar_latex(
        carta, nombre, anio, mes, dia, hora, minuto,
        ciudad, lat, lon, tz_name, aspectos_luna, ruta_rueda
    )

    with open(ruta_tex, "w", encoding="utf-8") as f:
        f.write(latex)

    print(f"  LaTeX guardado: {ruta_tex}")
    print("  Compilando PDF...")

    try:
        last_result = None

        for _ in range(2):
            last_result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", os.path.basename(ruta_tex)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=180,
                cwd=BASE_DIR
            )

        if os.path.exists(ruta_pdf):
            print()
            print("  PDF generado correctamente:")
            print(f"  {ruta_pdf}")
        else:
            print("  PDF no generado. Revisa el archivo .tex para más detalles.")
            if last_result:
                print(last_result.stdout[-3000:])
                print(last_result.stderr[-3000:])

    except FileNotFoundError:
        print("  pdflatex no encontrado. El archivo .tex está listo para compilar.")
    except Exception as e:
        print(f"  Error al compilar: {e}")

    print()
    print("Proceso completado.")

if __name__ == "__main__":
    main()