#!/usr/bin/env python3
"""
4. Planetas Personales — Mercurio, Venus, Marte — Arquitectura Interna
Interpreta el procesamiento de información (Mercurio), la regulación del vínculo (Venus)
y la ejecución de la acción (Marte) de la carta natal.
"""

import sys, os, math, subprocess
from datetime import datetime
import swisseph as swe
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import pytz
import matplotlib.pyplot as plt
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── CONSTANTES ────────────────────────────────────────────────────────────────

SIGNOS = ["Aries","Tauro","Géminis","Cáncer","Leo","Virgo",
          "Libra","Escorpio","Sagitario","Capricornio","Acuario","Piscis"]

ELEMENTO_SIGNO = {
    "Aries":"Fuego","Tauro":"Tierra","Géminis":"Aire","Cáncer":"Agua",
    "Leo":"Fuego","Virgo":"Tierra","Libra":"Aire","Escorpio":"Agua",
    "Sagitario":"Fuego","Capricornio":"Tierra","Acuario":"Aire","Piscis":"Agua"
}

PLANETAS_IDS = [
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
    ("Oposición",  180, 8.0, "☍"),
    ("Quincuncio", 150, 4.0, "⚻"),
]

SIMBOLOS_SIGNOS = ["♈","♉","♊","♋","♌","♍","♎","♏","♐","♑","♒","♓"]
COLORES_ELEMENTO = {"Fuego":"#CC2200","Tierra":"#2E7D32","Aire":"#E67E00","Agua":"#1A5FA8"}
COLORES_PLANETA  = {
    "Marte":"#CC2200","Júpiter":"#CC2200",
    "Venus":"#2E7D32","Saturno":"#2E7D32",
    "Mercurio":"#E67E00","Urano":"#E67E00",
    "Neptuno":"#1A5FA8","Plutón":"#1A5FA8",
    "Quirón":"#7B2D8B","Lilith":"#7B2D8B",
    "Nodo Norte":"#888800","Nodo Sur":"#888800",
}


# ─── TEXTOS: MERCURIO POR SIGNO ───────────────────────────────────────────────
# Cómo organizas la información, qué te satura y cómo se bloquea o desregula la mente.

MERCURIO_SIGNO = {

"Aries": (
    "Tu mente funciona rápido y tiende a llegar a una conclusión antes de haber revisado todo el proceso. "
    "Sueles responder primero y comprobar después. Esto aporta rapidez real, capacidad de reacción "
    "y facilidad para decidir en movimiento.\n\n"

    "La saturación aparece cuando hay demasiada información sin una prioridad clara. "
    "Si todo parece urgente al mismo tiempo, la velocidad se convierte en impaciencia "
    "y puedes actuar antes de haber terminado de entender. "
    "El bloqueo suele aparecer cuando hay que esperar, repetir algo varias veces "
    "o explicar en detalle algo que internamente ya sentías resuelto.\n\n"

    "Sueles pensar mejor cuando puedes avanzar por pasos cortos, "
    "tomar decisiones concretas y descargar mentalmente la información mediante acción."
),

"Tauro": (
    "Tu mente procesa de forma lenta, estable y profunda. "
    "Necesitas tiempo para integrar antes de responder, "
    "y ese tiempo no suele poder acelerarse sin perder claridad. "
    "Cuando comprendes algo de verdad, queda asentado de forma sólida.\n\n"

    "La saturación aparece cuando el entorno exige responder rápido "
    "o cambiar de opinión antes de haber terminado de procesar. "
    "Entonces puedes cerrarte más o volverte rígide. "
    "El bloqueo suele aparecer cuando una idea ya se ha consolidado internamente: "
    "cambiarla requiere más tiempo y más evidencia que en otros signos.\n\n"

    "Sueles pensar mejor cuando no hay presión, "
    "puedes ir a tu ritmo y tienes tiempo suficiente para integrar."
),

"Géminis": (
    "Tu mente funciona de forma rápida, asociativa y muy activa. "
    "Conectas ideas constantemente, cambias de perspectiva con facilidad "
    "y muchas veces piensas varias cosas al mismo tiempo. "
    "La variedad y el movimiento mental forman parte de tu funcionamiento natural.\n\n"

    "La saturación aparece tanto por exceso de estímulos como por monotonía prolongada. "
    "Cuando hay demasiado, cuesta terminar algo; "
    "cuando hay demasiado poco, tu propia mente genera dispersión para mantenerse activa. "
    "El bloqueo aparece cuando tienes que elegir una única respuesta "
    "o sostener una sola línea de pensamiento durante demasiado tiempo.\n\n"

    "Sueles regularte mejor cuando puedes mover la atención sin fragmentarte del todo: "
    "hablar, escribir, caminar o alternar tareas breves ayuda a ordenar la mente."
),

"Cáncer": (
    "Tu mente procesa a través de la resonancia emocional. "
    "La información con carga afectiva se integra con facilidad y permanece activa mucho tiempo. "
    "Lo que no tiene conexión emocional suele costarte más de priorizar o recordar.\n\n"

    "La saturación aparece cuando el entorno emocional es intenso. "
    "Tiendes a absorber lo que ocurre alrededor y pierdes claridad para atender lo neutral. "
    "El bloqueo suele aparecer como un bucle mental: "
    "vuelves una y otra vez a algo que todavía no has terminado de procesar emocionalmente.\n\n"

    "Sueles pensar mejor cuando hay sensación de seguridad, "
    "espacios tranquilos y tiempo suficiente para digerir lo vivido."
),

"Leo": (
    "Tu mente organiza la información a través del sentido y la narrativa. "
    "Necesitas entender qué importancia tiene algo y cómo encaja dentro de una historia más amplia. "
    "Cuando encuentras significado, la comprensión se vuelve mucho más clara.\n\n"

    "La saturación aparece cuando hay demasiada información desconectada entre sí. "
    "Entonces puedes intentar crear sentido demasiado rápido "
    "y terminar exagerando o simplificando más de la cuenta. "
    "El bloqueo aparece cuando una información nueva contradice la historia que ya habías construido internamente. "
    "A veces cuesta más modificar el relato que integrar el dato nuevo.\n\n"

    "Sueles regularte mejor cuando puedes ordenar las ideas, "
    "expresarlas con claridad y comprender para qué algo es importante."
),

"Virgo": (
    "Tu mente funciona de forma analítica y orientada al detalle. "
    "Observas diferencias, detectas errores y tiendes a buscar cómo mejorar las cosas. "
    "Esto aporta precisión, capacidad de organización y atención a lo concreto.\n\n"

    "La saturación aparece cuando el análisis nunca encuentra un punto de cierre. "
    "Siempre queda algo más por revisar, corregir o evaluar. "
    "Entonces aparece tensión mental de fondo y sensación de que nada termina de estar suficientemente acabado. "
    "El bloqueo típico es la parálisis por análisis: "
    "te cuesta actuar porque sientes que todavía faltan datos.\n\n"

    "Sueles pensar mejor cuando existen estructuras simples, "
    "pasos claros y límites concretos para detener el análisis."
),

"Libra": (
    "Tu mente funciona comparando perspectivas. "
    "Tiendes a ver automáticamente varios puntos de vista y buscas equilibrio antes de decidir. "
    "Esto aporta matices, capacidad de diálogo y sensibilidad relacional.\n\n"

    "La saturación aparece cuando tienes que tomar una decisión "
    "sin haber encontrado suficiente equilibrio interno. "
    "Entonces sigues generando nuevas posibilidades incluso cuando ya hay información suficiente. "
    "El bloqueo suele aparecer especialmente en decisiones con carga relacional o emocional: "
    "si algo puede afectar a otras personas, tu mente permanece abierta más tiempo.\n\n"

    "Sueles regularte mejor cuando puedes ordenar opciones por escrito, "
    "pensar en voz alta o poner límites temporales a las decisiones."
),

"Escorpio": (
    "Tu mente busca profundidad y coherencia. "
    "Percibes rápidamente lo que parece ambiguo, incompleto o poco auténtico "
    "y tiendes a investigar lo que hay debajo de la superficie.\n\n"

    "La saturación aparece cuando percibes contradicciones que no puedes verificar. "
    "Entonces tu mente queda atrapada intentando entender qué falta o qué no encaja. "
    "El bloqueo suele aparecer como silencio o reserva: "
    "cuando algo no puede expresarse con suficiente verdad o profundidad, "
    "prefieres no decir nada.\n\n"

    "Sueles pensar mejor cuando hay privacidad, claridad emocional "
    "y espacios donde no te sientes expueste."
),

"Sagitario": (
    "Tu mente funciona buscando sentido general y visión amplia. "
    "Necesitas comprender el marco mayor antes de entrar en los detalles. "
    "Cuando algo tiene dirección o propósito, la comprensión se vuelve mucho más fluida.\n\n"

    "La saturación aparece cuando tienes que sostener detalle repetitivo durante demasiado tiempo "
    "sin acceso al conjunto completo. "
    "Entonces pierdes interés o generalizas demasiado rápido. "
    "El bloqueo suele aparecer cuando una idea ya se ha convertido en verdad absoluta: "
    "puedes seguir razonando desde un marco que ya no encaja con la realidad actual.\n\n"

    "Sueles regularte mejor cuando puedes alternar visión amplia y realidad concreta "
    "sin perder contacto con ninguna de las dos."
),

"Capricornio": (
    "Tu mente organiza la información según su utilidad y viabilidad. "
    "Tiendes a pensar de forma estructurada, práctica y orientada a resultados concretos. "
    "Lo que no parece aplicable o realista suele costarte más de integrar.\n\n"

    "La saturación aparece cuando hay demasiada incertidumbre "
    "o información poco estructurada. "
    "Entonces puedes intentar controlar, clasificar o reducir lo ambiguo demasiado rápido. "
    "El bloqueo suele aparecer como anticipación negativa: "
    "piensas constantemente en lo que podría salir mal "
    "y puedes quedarte detenide antes de actuar.\n\n"

    "Sueles regularte mejor cuando existen prioridades claras, "
    "estructura y sensación de avance realista."
),

"Acuario": (
    "Tu mente funciona de forma abstracta y sistémica. "
    "Percibes patrones, conexiones y dinámicas generales que otras personas pueden no ver. "
    "Sueles pensar desde cierta distancia, intentando comprender cómo encajan las cosas dentro de un conjunto mayor.\n\n"

    "La saturación aparece cuando tienes que permanecer demasiado tiempo "
    "en lo concreto, lo emocional o lo personal. "
    "Entonces puedes desconectarte de la experiencia directa "
    "y quedarte únicamente en el análisis mental. "
    "El bloqueo suele aparecer por exceso de distancia: "
    "puedes entender algo perfectamente sin saber ya qué relación tiene con tu propia vida.\n\n"

    "Sueles regularte mejor cuando alternas reflexión amplia "
    "con experiencias reales, corporales y presentes."
),

"Piscis": (
    "Tu mente funciona de forma intuitiva y no lineal. "
    "Sueles percibir relaciones, ambientes y significados antes de poder explicarlos con claridad. "
    "Muchas veces entiendes algo primero como sensación, imagen o intuición, "
    "y solo después aparecen las palabras.\n\n"

    "La saturación aparece cuando el entorno emocional es muy denso o confuso. "
    "Entonces absorbes demasiado y pierdes claridad sobre qué pensamientos son realmente tuyos "
    "y cuáles vienen del ambiente. "
    "El bloqueo suele aparecer como dificultad para concretar: "
    "hay percepción y sensibilidad, pero cuesta transformar todo eso en algo claro y utilizable.\n\n"

    "Sueles pensar mejor cuando hay silencio, descanso mental, "
    "espacios de imaginación y tiempo para ordenar lo que percibes sin presión."
),

}

# ─── TEXTOS: MERCURIO POR CASA ────────────────────────────────────────────────
# Dónde y cómo organizas el pensamiento. Qué necesitas para aclararte mentalmente.

MERCURIO_CASA = {

1: (
    "Necesitas movimiento y expresión directa para aclarar lo que piensas. "
    "Sueles ordenar las ideas hablando, reaccionando, actuando o probando sobre la marcha. "
    "Muchas veces entiendes algo mientras lo estás expresando, no antes.\n\n"

    "La saturación aparece cuando acumulas demasiado pensamiento interno sin salida. "
    "Entonces la mente se acelera, pierde claridad o se vuelve más impulsiva. "
    "Sueles pensar mejor cuando puedes verbalizar, moverte "
    "y convertir rápidamente las ideas en algo concreto."
),

2: (
    "Tiendes a organizar la información de forma práctica, estable y gradual. "
    "Necesitas sentir que lo que aprendes tiene valor real, aplicación o utilidad concreta. "
    "Las ideas suelen asentarse lentamente, pero cuando lo hacen permanecen.\n\n"

    "La saturación aparece cuando hay demasiada teoría sin aplicación "
    "o cambios constantes que no te dejan consolidar una comprensión estable. "
    "Sueles pensar mejor cuando puedes ir a tu ritmo "
    "y relacionar las ideas con experiencias reales y sostenibles."
),

3: (
    "Necesitas intercambio, movimiento y estímulo constante para mantener la mente activa. "
    "Piensas hablando, escribiendo, aprendiendo, preguntando y conectando información diversa. "
    "Pensar y comunicar forman parte del mismo proceso.\n\n"

    "La saturación aparece cuando hay demasiados estímulos, conversaciones abiertas "
    "o información entrando continuamente sin descanso. "
    "Pero también cuando hay demasiado silencio o aislamiento prolongado. "
    "Sueles regularte mejor mediante intercambio ligero, escritura "
    "y movimiento mental flexible."
),

4: (
    "Procesas hacia adentro y necesitas privacidad para aclararte mentalmente. "
    "Sueles pensar mejor en espacios tranquilos, protegidos y sin demasiada presión externa. "
    "Muchas ideas necesitan madurar internamente antes de poder expresarse con claridad.\n\n"

    "La saturación aparece cuando hay demasiado ruido, exposición "
    "o interrupciones constantes mientras estás intentando pensar. "
    "Entonces cuesta encontrar claridad o expresar realmente lo que quieres decir. "
    "Sueles pensar mejor cuando tienes silencio, intimidad "
    "y tiempo suficiente para elaborar internamente."
),

5: (
    "Necesitas creatividad, expresión y participación personal para activar la mente. "
    "Comprendes mejor cuando puedes jugar con las ideas, explicarlas a tu manera "
    "o transformarlas en algo creativo y vivo.\n\n"

    "La saturación aparece cuando el pensamiento se vuelve excesivamente rígido, repetitivo "
    "o limitado a tareas puramente técnicas. "
    "Entonces disminuye el interés y la atención pierde vitalidad. "
    "Sueles regularte mejor cuando puedes crear, enseñar, explicar "
    "o expresarte de forma más libre."
),

6: (
    "Tiendes a organizar la información buscando utilidad, precisión y aplicación práctica. "
    "Tu atención suele dirigirse hacia los detalles, los procedimientos "
    "y todo aquello que puede mejorarse o hacerse funcionar mejor. "
    "Pensar y resolver problemas forman parte del mismo movimiento.\n\n"

    "La saturación aparece cuando el análisis nunca termina "
    "o cuando acumulas demasiadas tareas pequeñas abiertas al mismo tiempo. "
    "Entonces puedes quedar atrapade en correcciones constantes o sobrepensar detalles mínimos. "
    "Sueles pensar mejor con estructuras claras, rutinas simples "
    "y espacios concretos para cerrar procesos."
),

7: (
    "Necesitas diálogo para aclarar lo que piensas. "
    "Muchas veces entiendes mejor tus propias ideas cuando puedes contrastarlas con otra persona. "
    "El intercambio te ayuda a ordenar el pensamiento y ganar perspectiva.\n\n"

    "La saturación aparece cuando dependes demasiado de la respuesta externa "
    "o cuando te cuesta sostener una posición propia sin validación. "
    "También cuando conversaciones importantes quedan abiertas durante demasiado tiempo. "
    "Sueles regularte mejor mediante diálogo claro, escucha mutua "
    "y espacios de intercambio equilibrado."
),

8: (
    "Tu mente tiende a profundizar y rara vez se conforma con explicaciones superficiales. "
    "Necesitas entender qué hay detrás: motivaciones, patrones, contradicciones o dinámicas ocultas. "
    "La comprensión suele requerir intensidad y profundidad para sentirse completa.\n\n"

    "La saturación aparece cuando algo parece ambiguo o incoherente "
    "y no consigues comprenderlo del todo. "
    "Entonces puedes quedarte investigando internamente durante mucho tiempo. "
    "Sueles pensar mejor cuando tienes intimidad, silencio "
    "y conversaciones honestas donde puedas profundizar sin prisa."
),

9: (
    "Necesitas visión amplia y sentido general para organizar la mente. "
    "Comprendes mejor cuando puedes relacionar la información con una idea mayor, "
    "una filosofía o una dirección clara.\n\n"

    "La saturación aparece cuando hay exceso de detalle sin contexto "
    "o tareas repetitivas sin significado visible. "
    "Entonces la atención se dispersa o pierde motivación. "
    "Sueles regularte mejor cuando puedes alternar aprendizaje amplio "
    "con aplicaciones concretas que den sentido a lo que haces."
),

10: (
    "Tu mente suele organizarse alrededor de objetivos, estructura y resultados visibles. "
    "Tiendes a pensar de forma estratégica, práctica y orientada a construir algo sólido. "
    "La comunicación suele buscar claridad, eficiencia y credibilidad.\n\n"

    "La saturación aparece cuando hay demasiada presión mental sostenida, "
    "exceso de responsabilidad o necesidad constante de rendir intelectualmente. "
    "Entonces puedes volverte más rígide, controladore o exigente contigo misme. "
    "Sueles pensar mejor cuando existen prioridades claras, "
    "estructura y tiempo real para desconectar."
),

11: (
    "Tu mente se activa mediante el intercambio colectivo y las redes de ideas. "
    "Sueles pensar conectando perspectivas distintas "
    "y observando cómo encajan dentro de algo más amplio. "
    "Los grupos, las conversaciones compartidas y los proyectos colectivos estimulan tu pensamiento.\n\n"

    "La saturación aparece cuando hay demasiadas opiniones, "
    "exceso de información colectiva o sensación de estar mentalmente disponible para todo el mundo. "
    "Entonces puede costarte distinguir qué ideas son realmente tuyas. "
    "Sueles regularte mejor alternando intercambio social "
    "con espacios de pensamiento individual."
),

12: (
    "Necesitas silencio, soledad y pausas profundas para ordenar la mente. "
    "Procesas lentamente hacia adentro y muchas veces necesitas tiempo "
    "antes de comprender del todo lo que piensas o sientes. "
    "Las ideas suelen madurar en espacios internos más que en estímulos constantes.\n\n"

    "La saturación aparece cuando hay demasiado ruido mental, exposición "
    "o actividad continua sin descanso psicológico. "
    "Entonces la claridad disminuye y puedes sentir la mente más difusa o dispersa. "
    "Sueles pensar mejor cuando existen momentos de retiro, "
    "descanso mental y tiempo sin exigencia cognitiva."
),

}

# ─── TEXTOS: VENUS POR SIGNO ─────────────────────────────────────────────────
# Cómo vives el vínculo, qué necesitas para sentir conexión
# y qué ocurre cuando la relación deja de sostenerse.

VENUS_SIGNO = {

"Aries": (
    "Necesitas movimiento, iniciativa y espacio propio para sentirte bien dentro de una relación. "
    "La conexión suele funcionar mejor cuando puedes acercarte al otro sin sentir que pierdes autonomía.\n\n"

    "La saturación aparece cuando la relación exige demasiada adaptación sostenida, "
    "espera constante o sensación de limitación. "
    "Entonces la energía afectiva disminuye rápidamente y aparece irritación o distancia. "
    "Cuando el vínculo deja de sostenerse, tiendes a tomar distancia antes de quedarte atrapade en algo que ya no se siente vivo.\n\n"

    "Sueles regularte mejor en relaciones donde existe honestidad directa, "
    "espacio personal y sensación de movimiento compartido."
),

"Tauro": (
    "Necesitas estabilidad, continuidad y presencia real para sentir seguridad en el vínculo. "
    "Las relaciones suelen construirse lentamente y fortalecerse a través de la constancia, "
    "el contacto y la sensación de que la otra persona permanece.\n\n"

    "La saturación aparece cuando hay cambios bruscos, señales contradictorias "
    "o inestabilidad emocional sostenida. "
    "Entonces puedes empezar a cerrarte para protegerte. "
    "Cuando el vínculo deja de sostenerse, la desconexión suele ser gradual más que explosiva: "
    "la apertura disminuye poco a poco hasta que volver a confiar requiere demasiado esfuerzo.\n\n"

    "Sueles regularte mejor mediante estabilidad, tiempo compartido "
    "y relaciones donde las acciones coinciden con las palabras."
),

"Géminis": (
    "Necesitas intercambio, conversación y movimiento mental para mantener viva la conexión. "
    "La relación suele fortalecerse cuando hay curiosidad mutua, humor, ideas nuevas "
    "y sensación de dinamismo.\n\n"

    "La saturación aparece cuando la relación se vuelve demasiado repetitiva, rígida "
    "o emocionalmente densa sin espacio para el intercambio ligero. "
    "Entonces el interés disminuye y tu atención empieza a desplazarse hacia otros estímulos. "
    "Cuando el vínculo deja de sostenerse, la energía afectiva suele dispersarse "
    "antes de que exista una ruptura clara.\n\n"

    "Sueles regularte mejor en relaciones donde existe comunicación viva, "
    "flexibilidad y variedad."
),

"Cáncer": (
    "Necesitas cuidado mutuo, protección emocional y sensación de hogar compartido para sentirte en relación. "
    "La conexión suele fortalecerse cuando puedes mostrar vulnerabilidad "
    "sin miedo a perder el vínculo.\n\n"

    "La saturación aparece cuando el cuidado deja de ser recíproco "
    "y empiezas a sostener emocionalmente más de lo que recibes. "
    "Entonces aparece agotamiento silencioso y cierre progresivo. "
    "Cuando el vínculo deja de sostenerse, no siempre te vas inmediatamente: "
    "a veces sigues presente mientras la apertura emocional real se va retirando.\n\n"

    "Sueles regularte mejor en relaciones donde existe sensibilidad mutua, "
    "cuidado estable y seguridad emocional."
),

"Leo": (
    "Necesitas sentir reconocimiento genuino y apreciación real dentro del vínculo. "
    "La conexión suele fortalecerse cuando puedes mostrarte tal como eres "
    "y sentir que la otra persona realmente te ve.\n\n"

    "La saturación aparece cuando la relación se vuelve únicamente funcional "
    "y desaparece la sensación de reconocimiento mutuo. "
    "Entonces puedes empezar a esforzarte más para recuperar atención o validación, "
    "y ese esfuerzo termina agotando. "
    "Cuando el vínculo deja de sostenerse, puedes volverte más distante, más teatral emocionalmente "
    "o retirarte por completo.\n\n"

    "Sueles regularte mejor mediante calidez, reconocimiento sincero "
    "y relaciones donde puedes expresarte sin sentirte reducíde a una función."
),

"Virgo": (
    "Necesitas coherencia, cuidado concreto y reciprocidad cotidiana para sentir conexión. "
    "Muchas veces expresas el afecto a través de actos, atención práctica "
    "y presencia estable más que mediante grandes demostraciones emocionales.\n\n"

    "La saturación aparece cuando empiezas a analizar constantemente la relación: "
    "qué falla, qué debería cambiar o qué podría hacerse mejor. "
    "Entonces la observación reemplaza al contacto y la espontaneidad disminuye. "
    "Cuando el vínculo deja de sostenerse, puedes seguir presente externamente "
    "mientras internamente te vas alejando.\n\n"

    "Sueles regularte mejor en relaciones simples, honestas "
    "y donde el cuidado puede expresarse de forma concreta y mutua."
),

"Libra": (
    "Necesitas equilibrio, reciprocidad y armonía relacional para sentir estabilidad afectiva. "
    "La conexión suele fortalecerse cuando ambas personas sostienen el intercambio "
    "de forma justa y consciente.\n\n"

    "La saturación aparece cuando existen desequilibrios sostenidos "
    "o conflictos que nunca terminan de resolverse. "
    "Entonces puedes empezar a adaptarte más de lo que realmente puedes sostener. "
    "Cuando el vínculo deja de sostenerse, suele existir un límite interno "
    "que no expresaste claramente hasta que ya estabas muy cerca de romper.\n\n"

    "Sueles regularte mejor mediante diálogo equilibrado, respeto mutuo "
    "y relaciones donde ambas partes participan realmente del vínculo."
),

"Escorpio": (
    "Necesitas profundidad, verdad emocional y confianza real para abrirte afectivamente. "
    "La conexión suele fortalecerse cuando percibes autenticidad "
    "y acceso genuino a la otra persona. "
    "Lo superficial o ambiguo suele generar distancia rápidamente.\n\n"

    "La saturación aparece cuando percibes contradicciones, secretos "
    "o sensación de que algo importante no está siendo dicho. "
    "Entonces puedes entrar en vigilancia emocional e intentar descubrir qué falta. "
    "Cuando el vínculo deja de sostenerse, la desconexión no siempre es inmediata: "
    "a veces la relación continúa mientras internamente crecen la desconfianza o el resentimiento.\n\n"

    "Sueles regularte mejor en relaciones honestas, profundas "
    "y donde existe suficiente seguridad para mostrarte sin máscaras."
),

"Sagitario": (
    "Necesitas libertad, crecimiento y sensación de expansión compartida dentro del vínculo. "
    "La relación suele fortalecerse cuando permite explorar, aprender "
    "y mantener espacios propios además de los compartidos.\n\n"

    "La saturación aparece cuando la relación se vive como limitación, exceso de control "
    "o rutina demasiado cerrada. "
    "Entonces la energía afectiva empieza a alejarse incluso antes de que exista conflicto abierto. "
    "Cuando el vínculo deja de sostenerse, tiendes a tomar distancia rápidamente "
    "para recuperar amplitud y movimiento.\n\n"

    "Sueles regularte mejor en relaciones donde existe honestidad, movimiento "
    "y suficiente libertad para seguir creciendo."
),

"Capricornio": (
    "Necesitas estabilidad, compromiso y sensación de construcción compartida para abrirte del todo. "
    "La conexión suele fortalecerse cuando existe dirección, responsabilidad mutua "
    "y sensación de que la relación puede sostenerse a largo plazo.\n\n"

    "La saturación aparece cuando el vínculo parece estancado, poco claro "
    "o sostenido únicamente desde el esfuerzo. "
    "Entonces empiezas a preguntarte cuánto sentido tiene seguir invirtiendo energía. "
    "Cuando el vínculo deja de sostenerse, la retirada suele ser silenciosa, firme "
    "y difícil de revertir una vez tomada la decisión.\n\n"

    "Sueles regularte mejor mediante coherencia, estabilidad "
    "y relaciones donde el compromiso se demuestra con hechos."
),

"Acuario": (
    "Necesitas independencia, espacio personal y conexión mental real para sentirte bien dentro de una relación. "
    "El vínculo suele funcionar mejor cuando ambas personas pueden seguir siendo ellas mismas "
    "sin perder libertad.\n\n"

    "La saturación aparece cuando existe demasiada demanda emocional constante "
    "o sensación de fusión afectiva obligatoria. "
    "Entonces necesitas tomar distancia para recuperar claridad interna. "
    "Cuando el vínculo deja de sostenerse, la desconexión puede producirse lentamente "
    "mientras externamente todavía parece que todo sigue igual.\n\n"

    "Sueles regularte mejor en relaciones donde existe amistad, intercambio intelectual "
    "y suficiente espacio para respirar."
),

"Piscis": (
    "Necesitas empatía profunda, sensibilidad y conexión emocional real para sentir cercanía. "
    "La relación suele fortalecerse cuando existe sensación de acompañamiento genuino "
    "y apertura emocional mutua.\n\n"

    "La saturación aparece cuando absorbes demasiado del estado emocional de la otra persona "
    "y empiezas a perder claridad sobre qué sientes realmente tú. "
    "Entonces el cuidado puede convertirse en confusión o pérdida de referencia propia. "
    "Cuando el vínculo deja de sostenerse, no siempre te retiras claramente: "
    "a veces permaneces mientras internamente empiezas a diluirte.\n\n"

    "Sueles regularte mejor cuando existen límites emocionales suaves pero claros, "
    "espacios de descanso y relaciones donde la sensibilidad no implique perderte."
),

}

# ─── TEXTOS: VENUS POR CASA ──────────────────────────────────────────────────
# Dónde y cómo vives el vínculo. Qué necesitas para que la relación se sostenga.

VENUS_CASA = {

1: (
    "Necesitas presencia directa y contacto cercano para sentir viva la conexión. "
    "Sueles relacionarte de forma visible, espontánea y bastante inmediata. "
    "Poder mostrarte tal como eres y sentirte realmente viste forma parte importante de tu regulación afectiva.\n\n"

    "La saturación aparece cuando sientes que tienes que esconder demasiado quién eres "
    "o sostener una imagen artificial durante mucho tiempo. "
    "Sueles regularte mejor en vínculos donde existe naturalidad, presencia real "
    "y espacio para expresarte sin excesiva contención."
),

2: (
    "Necesitas estabilidad, continuidad y sensación de seguridad compartida para abrirte afectivamente. "
    "La conexión suele fortalecerse mediante presencia constante, intercambio concreto "
    "y construcción lenta de confianza.\n\n"

    "La saturación aparece cuando hay demasiada inestabilidad, cambios bruscos "
    "o incertidumbre sostenida dentro de la relación. "
    "Entonces puedes empezar a cerrarte para proteger tu equilibrio interno. "
    "Sueles regularte mejor cuando existen ritmos claros, cuidado tangible "
    "y sensación de sostén mutuo."
),

3: (
    "Necesitas comunicación frecuente y movimiento relacional constante para sentir conexión. "
    "El vínculo suele nutrirse mediante conversación, intercambio cotidiano, humor "
    "y cercanía mental.\n\n"

    "La saturación aparece cuando la relación pierde intercambio real "
    "o queda reducida únicamente a funciones prácticas o emociones densas. "
    "Entonces la conexión empieza a sentirse más distante aunque el vínculo continúe. "
    "Sueles regularte mejor mediante comunicación ligera, contacto frecuente "
    "y curiosidad mutua."
),

4: (
    "Necesitas intimidad, privacidad y sensación de refugio compartido para abrirte emocionalmente. "
    "La conexión suele fortalecerse en espacios protegidos, cotidianos y emocionalmente seguros. "
    "Muchas veces te abres más profundamente en lo privado que en lo visible.\n\n"

    "La saturación aparece cuando hay demasiada exposición externa "
    "o poca sensación de hogar emocional dentro de la relación. "
    "Entonces empiezas a protegerte y disminuye la apertura afectiva. "
    "Sueles regularte mejor mediante calma, intimidad "
    "y vínculos donde puedas bajar la guardia."
),

5: (
    "Necesitas disfrute, juego y expresión afectiva viva para sentirte en relación. "
    "La conexión suele fortalecerse cuando existe creatividad compartida, placer "
    "y espacio para relacionarse desde la espontaneidad.\n\n"

    "La saturación aparece cuando la relación se vuelve únicamente funcional, rutinaria "
    "o excesivamente seria durante demasiado tiempo. "
    "Entonces disminuye la vitalidad afectiva y aparece sensación de desconexión. "
    "Sueles regularte mejor mediante ligereza, creatividad "
    "y experiencias compartidas que permitan disfrutar juntes."
),

6: (
    "Necesitas cuidado concreto y presencia cotidiana para sostener el vínculo. "
    "Muchas veces expresas el afecto mediante pequeños actos, ayuda mutua "
    "y atención práctica a las necesidades de la otra persona.\n\n"

    "La saturación aparece cuando la relación se convierte únicamente en responsabilidad "
    "o cuando el cuidado deja de ser recíproco. "
    "Entonces el vínculo empieza a sentirse más como obligación que como conexión real. "
    "Sueles regularte mejor mediante rutinas simples, cooperación "
    "y gestos cotidianos de cuidado mutuo."
),

7: (
    "Las relaciones ocupan un lugar central en tu regulación afectiva. "
    "Necesitas reciprocidad clara, intercambio equilibrado "
    "y sensación de compromiso mutuo para sentir estabilidad.\n\n"

    "La saturación aparece cuando existen relaciones ambiguas, desequilibrios prolongados "
    "o dificultad para definir el lugar de cada persona dentro del vínculo. "
    "Entonces puedes empezar a compensar demasiado al otro o perder estabilidad emocional. "
    "Sueles regularte mejor mediante acuerdos claros, diálogo "
    "y relaciones donde ambas partes sostienen conscientemente el vínculo."
),

8: (
    "Necesitas profundidad emocional e intimidad real para que una relación se sienta significativa. "
    "La conexión suele vivirse con intensidad y necesidad de acceso genuino al otro. "
    "Las relaciones superficiales rara vez te resultan suficientes.\n\n"

    "La saturación aparece cuando percibes secretos, distancia emocional "
    "o sensación de conexión parcial. "
    "Entonces puedes entrar en vigilancia emocional o necesidad de entender qué ocurre realmente debajo de la superficie. "
    "Sueles regularte mejor mediante honestidad emocional, intimidad "
    "y vínculos donde exista confianza profunda."
),

9: (
    "Necesitas expansión, aprendizaje y sentido compartido dentro de la relación. "
    "La conexión suele fortalecerse mediante experiencias que amplían tu visión de la vida: "
    "viajes, conversaciones profundas, proyectos o crecimiento conjunto.\n\n"

    "La saturación aparece cuando la relación se vuelve demasiado limitada, repetitiva "
    "o cerrada sobre sí misma. "
    "Entonces disminuye el interés afectivo y aparece necesidad de movimiento o distancia. "
    "Sueles regularte mejor mediante libertad, crecimiento "
    "y vínculos que permitan evolucionar."
),

10: (
    "Relacionas el vínculo con la construcción visible de la vida, los objetivos y la estabilidad externa. "
    "La conexión suele fortalecerse cuando existe admiración mutua, dirección compartida "
    "o sensación de estar construyendo algo sólido juntes.\n\n"

    "La saturación aparece cuando la relación queda reducida únicamente a función, rendimiento "
    "o responsabilidad constante. "
    "Entonces el vínculo pierde calidez y se vuelve demasiado estructural. "
    "Sueles regularte mejor cuando existe equilibrio entre compromiso, afecto "
    "y espacio para descansar de las exigencias externas."
),

11: (
    "Necesitas amistad, intercambio libre y sensación de afinidad mental para sentir conexión. "
    "El vínculo suele fortalecerse cuando existe visión compartida, proyecto común "
    "o sensación de pertenecer juntes a algo más amplio.\n\n"

    "La saturación aparece cuando la relación se vuelve demasiado cerrada, absorbente "
    "o desconectada del mundo exterior. "
    "Entonces necesitas recuperar espacio, aire y perspectiva. "
    "Sueles regularte mejor mediante libertad relacional, amistad "
    "y vínculos donde cada persona puede seguir siendo ella misma."
),

12: (
    "Necesitas profundidad interior, privacidad y espacios de intimidad emocional silenciosa para abrirte afectivamente. "
    "Muchas veces tu vida emocional es más rica internamente de lo que muestras hacia afuera. "
    "Necesitas sentir que puedes vincularte sin exposición constante.\n\n"

    "La saturación aparece cuando la relación exige demasiada visibilidad, claridad inmediata "
    "o disponibilidad emocional continua. "
    "Entonces empiezas a replegarte emocionalmente hacia adentro. "
    "Sueles regularte mejor mediante calma, sensibilidad, tiempos de retiro "
    "y vínculos donde no todo tenga que explicarse de inmediato."
),

}

# ─── TEXTOS: MARTE POR SIGNO ─────────────────────────────────────────────────
# Cómo se activa la acción, cómo descargas la energía
# y qué ocurre cuando no encuentra salida.

MARTE_SIGNO = {

"Aries": (
    "Tu energía se activa rápido y con poca necesidad de preparación. "
    "Funcionas mejor cuando puedes iniciar, avanzar y responder de forma directa. "
    "La acción te ayuda a ordenar la activación interna.\n\n"

    "La saturación aparece cuando hay demasiada espera, inmovilidad "
    "o sensación de bloqueo constante. "
    "Entonces se acumula irritabilidad, impaciencia o necesidad de confrontación. "
    "Cuando no encuentras una salida clara, puedes terminar generando fricción simplemente "
    "para descargar energía acumulada.\n\n"

    "Sueles regularte mejor mediante movimiento físico, objetivos concretos "
    "y espacios donde puedas actuar con autonomía."
),

"Tauro": (
    "Tu energía se activa lentamente pero con gran capacidad de sostén. "
    "Necesitas tiempo para ponerte en marcha, "
    "pero una vez activade puedes sostener el esfuerzo de forma muy estable. "
    "La acción descarga mejor a través de procesos concretos y continuos.\n\n"

    "La saturación aparece cuando existe demasiada presión para cambiar de dirección rápidamente "
    "o cuando llevas demasiado tiempo conteniendo lo que necesitas expresar. "
    "Entonces puedes volverte más rígide o acumular tensión silenciosamente. "
    "Si esa acumulación continúa, la descarga puede aparecer de forma intensa y repentina.\n\n"

    "Sueles regularte mejor mediante ritmos estables, acción sostenida "
    "y contacto físico con la realidad concreta."
),

"Géminis": (
    "Tu energía se activa a través del pensamiento, la curiosidad y el intercambio mental. "
    "Necesitas movimiento cognitivo, variedad y estímulo para mantenerte en marcha. "
    "La acción descarga hablando, escribiendo, aprendiendo o cambiando de enfoque.\n\n"

    "La saturación aparece cuando hay demasiados estímulos "
    "o demasiadas tareas abiertas al mismo tiempo. "
    "Entonces la energía se dispersa y cuesta terminar lo que empiezas. "
    "También puede aparecer inquietud verbal, aceleración mental "
    "o necesidad de discutir como forma de descarga.\n\n"

    "Sueles regularte mejor mediante movimiento, conversación, escritura "
    "y actividades que permitan cambiar de foco sin perder dirección."
),

"Cáncer": (
    "Tu energía se activa cuando hay algo que cuidar, proteger o sostener emocionalmente. "
    "Muchas veces no actúas desde impulso directo, "
    "sino desde la percepción de una necesidad afectiva o de protección.\n\n"

    "La saturación aparece cuando la energía no puede expresarse hacia afuera "
    "y queda retenida internamente. "
    "Entonces la activación se transforma en irritabilidad silenciosa, sensibilidad excesiva "
    "o resentimiento acumulado. "
    "En lugar de descargarse mediante acción clara, la energía permanece dando vueltas por dentro.\n\n"

    "Sueles regularte mejor mediante espacios seguros, movimiento suave "
    "y acciones donde sientas que proteges o cuidas algo importante."
),

"Leo": (
    "Tu energía se activa a través del entusiasmo, la creatividad y la posibilidad de expresarte plenamente. "
    "Necesitas sentir que lo que haces tiene relevancia, impacto o visibilidad. "
    "La acción descarga mediante expresión, creación o liderazgo.\n\n"

    "La saturación aparece cuando tu esfuerzo no es visto, reconocido "
    "o encuentra constantemente indiferencia. "
    "Entonces la energía busca hacerse notar de alguna manera "
    "y puede aparecer dramatización o frustración expresiva. "
    "La activación retenida rara vez permanece completamente silenciosa.\n\n"

    "Sueles regularte mejor mediante creatividad, juego, expresión "
    "y espacios donde puedas actuar con autenticidad."
),

"Virgo": (
    "Tu energía se activa cuando hay algo que ordenar, mejorar o resolver. "
    "Funcionas bien cuando puedes aplicar esfuerzo a tareas concretas "
    "y producir resultados útiles y precisos.\n\n"

    "La saturación aparece cuando el análisis reemplaza a la acción "
    "o cuando hay demasiadas cosas pequeñas abiertas al mismo tiempo. "
    "Entonces la energía se transforma en tensión mental, hipercontrol "
    "o crítica constante hacia ti o hacia el entorno. "
    "Puedes quedarte corrigiendo indefinidamente sin llegar a descargar realmente.\n\n"

    "Sueles regularte mejor mediante rutinas claras, trabajo concreto "
    "y tareas que tengan principio, desarrollo y cierre."
),

"Libra": (
    "Tu energía se activa en relación con otras personas. "
    "Funcionas mejor cuando puedes actuar en intercambio, negociación "
    "o cooperación. "
    "La acción descarga buscando equilibrio, acuerdo o resolución relacional.\n\n"

    "La saturación aparece cuando existe conflicto sostenido "
    "y no encuentras una forma clara de expresarlo directamente. "
    "Entonces la tensión puede salir de forma indirecta, pasiva "
    "o mediante acumulación silenciosa de malestar. "
    "El conflicto frontal suele evitarse hasta que ya no puede sostenerse más.\n\n"

    "Sueles regularte mejor mediante diálogo claro, movimiento compartido "
    "y vínculos donde el desacuerdo pueda expresarse sin ruptura."
),

"Escorpio": (
    "Tu energía se activa con intensidad y concentración. "
    "Respondes con mucha fuerza cuando percibes amenaza, desafío "
    "o necesidad de transformación profunda. "
    "La acción descarga mediante enfoque, confrontación "
    "o procesos de cambio radical.\n\n"

    "La saturación aparece cuando la energía queda acumulada sin salida clara. "
    "Entonces puedes entrar en estados de control excesivo, obsesión "
    "o activación interna permanente. "
    "La tensión retenida durante mucho tiempo puede descargarse de forma muy intensa "
    "cuando finalmente encuentra salida.\n\n"

    "Sueles regularte mejor mediante actividad intensa, profundidad emocional "
    "y espacios donde puedas actuar con honestidad y enfoque."
),

"Sagitario": (
    "Tu energía se activa mediante entusiasmo, expansión y sensación de propósito. "
    "Necesitas dirección, horizonte y movimiento para sentirte vitalmente en marcha. "
    "La acción descarga explorando, aprendiendo, viajando "
    "o persiguiendo algo que sientes significativo.\n\n"

    "La saturación aparece cuando hay exceso de limitación, rutina cerrada "
    "o falta de sentido en lo que haces. "
    "Entonces aparece inquietud, impaciencia o necesidad constante de escapar hacia otra cosa. "
    "La energía puede terminar descargándose en impulsividad "
    "o en defender ideas con demasiada intensidad.\n\n"

    "Sueles regularte mejor mediante movimiento, aprendizaje "
    "y objetivos que permitan crecimiento real."
),

"Capricornio": (
    "Tu energía se activa mediante estructura, objetivos claros y sensación de construcción a largo plazo. "
    "Puedes sostener grandes cantidades de esfuerzo "
    "cuando existe dirección y sentido práctico.\n\n"

    "La saturación aparece cuando toda tu energía queda atrapada en control, responsabilidad "
    "o exigencia constante sin espacios reales de descarga. "
    "Entonces puedes endurecerte, volverte demasiado rígide "
    "o perder capacidad de descanso. "
    "Si la tensión acumulada continúa demasiado tiempo, puede aparecer una ruptura brusca "
    "después de largos periodos de contención.\n\n"

    "Sueles regularte mejor mediante estructura clara, acción sostenida "
    "y momentos reales de pausa y recuperación."
),

"Acuario": (
    "Tu energía se activa mediante ideas nuevas, proyectos colectivos "
    "y necesidad de cambiar lo establecido. "
    "Funcionas mejor cuando sientes que lo que haces tiene impacto más allá de lo individual.\n\n"

    "La saturación aparece cuando hay demasiada rigidez, repetición "
    "o sensación de limitación dentro de estructuras cerradas. "
    "Entonces la energía se vuelve errática o rebelde: "
    "cambios bruscos de dirección, ruptura de normas "
    "o impulso de actuar simplemente en contra de algo. "
    "La acción pierde estabilidad cuando no encuentra un propósito claro.\n\n"

    "Sueles regularte mejor mediante libertad, innovación "
    "y proyectos con sentido colectivo."
),

"Piscis": (
    "Tu energía se activa de forma sensible y cambiante. "
    "Muchas veces no actúas desde impulso directo, "
    "sino desde estados internos, intuiciones o conexión emocional con lo que ocurre alrededor. "
    "La acción descarga mejor mediante creatividad, ayuda, arte "
    "o actividades con dimensión emocional o espiritual.\n\n"

    "La saturación aparece cuando la energía no encuentra dirección clara "
    "o absorbes demasiado del entorno. "
    "Entonces aparece pasividad, dispersión o dificultad para actuar desde una decisión propia. "
    "La acción puede quedar reemplazada por adaptación constante a lo que otras personas necesitan.\n\n"

    "Sueles regularte mejor mediante descanso, espacios creativos, "
    "movimiento suave y actividades que permitan conectar con sentido interno."
),

}

# ─── TEXTOS: MARTE POR CASA ──────────────────────────────────────────────────
# Dónde y cómo descargas la energía.
# Qué activa la acción y qué ocurre cuando no encuentra salida.

MARTE_CASA = {

1: (
    "Necesitas movimiento directo y expresión inmediata para regularte. "
    "Descargas activación a través del cuerpo, la iniciativa y la acción visible. "
    "Moverte, empezar y actuar forman parte natural de tu regulación.\n\n"

    "La saturación aparece cuando hay demasiada inmovilidad, contención "
    "o sensación de no poder actuar libremente. "
    "Entonces se acumula tensión física, irritabilidad o impaciencia. "
    "Sueles regularte mejor mediante actividad corporal, decisiones rápidas "
    "y acción concreta."
),

2: (
    "Tu energía se activa cuando hay algo que construir, sostener o proteger. "
    "Descargas bien mediante trabajo constante, objetivos tangibles "
    "y sensación de avance material o práctico.\n\n"

    "La saturación aparece cuando el esfuerzo no produce resultados visibles "
    "o existe inseguridad sostenida respecto a recursos y estabilidad. "
    "Entonces la energía puede quedarse bloqueada en frustración silenciosa o rigidez. "
    "Sueles regularte mejor mediante ritmos estables, trabajo concreto "
    "y sensación de utilidad real."
),

3: (
    "Tu energía descarga a través de la comunicación, el intercambio y el movimiento mental. "
    "Necesitas hablar, debatir, escribir o aprender activamente para mantenerte regulade. "
    "Pensamiento y acción suelen ir unidos.\n\n"

    "La saturación aparece cuando la energía no encuentra salida comunicativa "
    "o hay exceso de estímulos mentales sin dirección clara. "
    "Entonces aparece agitación, discusión constante "
    "o dificultad para sostener el foco. "
    "Sueles regularte mejor mediante conversación, movimiento "
    "y actividades que mantengan la mente activa."
),

4: (
    "Tu energía se activa en el espacio privado y en relación con la protección emocional o territorial. "
    "Respondes intensamente cuando sientes que debes cuidar, defender "
    "o sostener algo cercano.\n\n"

    "La saturación aparece cuando la tensión emocional queda acumulada dentro de tu espacio íntimo "
    "sin posibilidad de descarga clara. "
    "Entonces el hogar o la vida privada pueden llenarse de irritabilidad silenciosa "
    "o activación constante de fondo. "
    "Sueles regularte mejor mediante privacidad, descanso "
    "y espacios seguros donde puedas bajar la vigilancia."
),

5: (
    "Necesitas creatividad, juego y expresión activa para que tu energía circule bien. "
    "Descargas mediante deporte, sexualidad, placer físico "
    "o actividades donde puedas implicarte con intensidad y disfrute.\n\n"

    "La saturación aparece cuando toda tu energía queda reducida a obligación, rutina "
    "o exceso de control. "
    "Entonces disminuye la vitalidad y aparece frustración acumulada. "
    "Sueles regularte mejor mediante movimiento creativo, juego "
    "y experiencias donde puedas expresarte libremente."
),

6: (
    "Tu energía descarga bien mediante trabajo, disciplina y actividad cotidiana estructurada. "
    "Sueles funcionar mejor cuando existe una rutina clara "
    "donde la acción pueda sostenerse de forma constante.\n\n"

    "La saturación aparece cuando hay exceso de tareas, autoexigencia "
    "o sensación de estar permanentemente resolviendo problemas. "
    "Entonces la energía se convierte en tensión nerviosa, hiperactividad "
    "o dificultad para descansar realmente. "
    "Sueles regularte mejor mediante hábitos simples, actividad física regular "
    "y equilibrio entre esfuerzo y recuperación."
),

7: (
    "Tu energía se activa intensamente en los vínculos y en el intercambio con otras personas. "
    "Descargas mediante relación, cooperación, confrontación "
    "o movimiento compartido.\n\n"

    "La saturación aparece cuando el conflicto queda retenido "
    "o toda tu energía se expresa únicamente a través de las relaciones. "
    "Entonces pueden aparecer discusiones recurrentes, tensión relacional "
    "o necesidad inconsciente de activar conflicto para descargar energía acumulada. "
    "Sueles regularte mejor mediante relaciones claras, movimiento compartido "
    "y capacidad de expresar desacuerdo directamente."
),

8: (
    "Necesitas profundidad e intensidad para sentirte plenamente activade. "
    "Tu energía descarga mejor en procesos transformadores, vínculos profundos "
    "o experiencias emocionalmente intensas.\n\n"

    "La saturación aparece cuando la energía queda contenida durante demasiado tiempo "
    "o no encuentra espacios de descarga profunda. "
    "Entonces puede aparecer control excesivo, tensión interna constante "
    "o sensación de activación acumulada difícil de soltar. "
    "Sueles regularte mejor mediante intensidad consciente, honestidad emocional "
    "y procesos reales de transformación."
),

9: (
    "Tu energía se activa mediante movimiento, expansión y dirección clara. "
    "Descargas bien cuando persigues objetivos amplios, aprendes algo nuevo "
    "o sientes que avanzas hacia un horizonte significativo.\n\n"

    "La saturación aparece cuando la vida se vuelve demasiado limitada, repetitiva "
    "o sin sentido de avance. "
    "Entonces aparece inquietud, impulsividad "
    "o necesidad constante de escapar hacia otra experiencia. "
    "Sueles regularte mejor mediante viaje, aprendizaje, movimiento físico "
    "y proyectos con propósito."
),

10: (
    "Tu energía descarga mediante objetivos, ambición y construcción visible. "
    "Sueles activarte con fuerza cuando existe una dirección profesional, "
    "un reto concreto o algo que construir a largo plazo.\n\n"

    "La saturación aparece cuando toda tu energía queda atrapada en exigencia, rendimiento "
    "o necesidad constante de sostener responsabilidad. "
    "Entonces puede aparecer dureza interna, dificultad para parar "
    "o sensación de vivir permanentemente en modo esfuerzo. "
    "Sueles regularte mejor mediante metas claras, estructura "
    "y tiempos reales de descanso."
),

11: (
    "Tu energía se activa en proyectos colectivos, redes y objetivos compartidos. "
    "Descargas bien cuando sientes que formas parte de algo más amplio "
    "y puedes colaborar activamente con otras personas.\n\n"

    "La saturación aparece cuando no existe dirección colectiva "
    "o tu energía queda aislada sin intercambio. "
    "Entonces disminuye la motivación y la acción pierde fuerza o continuidad. "
    "Sueles regularte mejor mediante colaboración, proyectos grupales "
    "y causas que generen sentido compartido."
),

12: (
    "Tu energía tiende a funcionar hacia adentro y no siempre encuentra salida visible inmediata. "
    "Puedes acumular activación silenciosamente "
    "si no existen espacios seguros de descarga.\n\n"

    "La saturación aparece cuando toda la energía queda retenida internamente "
    "o te adaptas constantemente a lo que otras personas necesitan sin registrar tu propio impulso. "
    "Entonces aparece agotamiento, confusión o sensación de pérdida de dirección. "
    "Sueles regularte mejor mediante descanso profundo, creatividad, práctica interior "
    "y actividades donde puedas actuar sin exceso de exposición externa."
),

}

# ─── ASPECTOS ENTRE PLANETAS PERSONALES ──────────────────────────────────────
# Cómo interactúan pensamiento, vínculo y acción.

ASPECTOS_PERSONALES = {

# ── Mercurio – Venus ──────────────────────────────────────────────────────────

("Mercurio", "Venus", "="): (
    "Mercurio y Venus en conjunción: tu forma de pensar y tu forma de vincularte "
    "funcionan a través del mismo circuito. "
    "Necesitas comprender para conectar y muchas veces conectas a través de la conversación, "
    "las palabras y el intercambio mental.\n\n"

    "Hablar, explicar y compartir ideas puede generar sensación real de cercanía. "
    "La dificultad aparece cuando analizar el vínculo reemplaza a vivirlo. "
    "Entonces la relación puede quedarse atrapada en conversaciones, interpretaciones "
    "o necesidad constante de entenderlo todo.\n\n"

    "Sueles regularte mejor cuando puedes combinar claridad mental "
    "con experiencia emocional directa."
),

("Mercurio", "Venus", "□"): (
    "Mercurio cuadrando Venus: tu forma de pensar y tu forma de vincularte "
    "entran fácilmente en fricción. "
    "A veces entiendes algo mentalmente pero emocionalmente necesitas otra cosa, "
    "o la necesidad de analizar interfiere con la conexión.\n\n"

    "La saturación aparece cuando intentas resolver lo relacional únicamente desde la cabeza "
    "o cuando el estado afectivo desorganiza demasiado tu claridad mental. "
    "Puedes sentir que pensar demasiado enfría el vínculo "
    "y que el vínculo ocupa demasiado espacio dentro de la mente.\n\n"

    "Sueles regularte mejor diferenciando momentos para analizar "
    "y momentos para simplemente estar en relación."
),

("Mercurio", "Venus", "☍"): (
    "Mercurio oponiéndose a Venus: pensamiento y vínculo parecen moverse en direcciones distintas. "
    "Cuando entras mucho en análisis, la conexión emocional puede alejarse; "
    "cuando te implicas profundamente en el vínculo, la claridad mental disminuye.\n\n"

    "La tensión aparece porque ambas funciones necesitan ritmos diferentes. "
    "Puedes sentir que comprender y conectar no siempre ocurren al mismo tiempo.\n\n"

    "Sueles regularte mejor aprendiendo a alternar conscientemente entre reflexión "
    "y experiencia emocional, sin exigir que ambas estén igual de activas a la vez."
),

("Mercurio", "Venus", "△"): (
    "Mercurio en trígono a Venus: pensamiento y vínculo cooperan con naturalidad. "
    "Sueles comunicar con facilidad lo que sientes "
    "y comprender emocionalmente lo que ocurre en las relaciones.\n\n"

    "La conexión entre mente y afecto suele ser fluida "
    "y eso facilita mucho el intercambio relacional. "
    "La dificultad es que algunos desequilibrios pueden pasar desapercibidos "
    "porque el vínculo sigue funcionando incluso cuando hay cosas importantes sin revisar.\n\n"

    "Sueles regularte bien mediante comunicación clara, cercanía emocional "
    "y vínculos donde exista intercambio genuino."
),

("Mercurio", "Venus", "✶"): (
    "Mercurio en sextil a Venus: existe compatibilidad entre pensamiento y vínculo. "
    "La comunicación puede convertirse en un recurso importante para sostener relaciones "
    "y los vínculos pueden ayudarte a organizar internamente lo que piensas.\n\n"

    "Cuando utilizas conscientemente esta conexión, "
    "las palabras pueden convertirse en un puente real entre claridad y afecto."
),

# ── Mercurio – Marte ──────────────────────────────────────────────────────────

("Mercurio", "Marte", "="): (
    "Mercurio y Marte en conjunción: pensamiento y acción funcionan juntos y con rapidez. "
    "Tiendes a actuar sobre lo que piensas casi inmediatamente "
    "y las palabras suelen llevar mucha energía e intensidad.\n\n"

    "La saturación aparece cuando la velocidad supera la capacidad de procesamiento. "
    "Entonces puede haber impulsividad verbal, conclusiones demasiado rápidas "
    "o acción antes de haber comprendido completamente la situación.\n\n"

    "Sueles regularte mejor cuando encuentras espacios "
    "para desacelerar antes de reaccionar."
),

("Mercurio", "Marte", "□"): (
    "Mercurio cuadrando Marte: pensamiento y acción entran fácilmente en tensión. "
    "A veces analizas tanto que te cuesta moverte; "
    "otras veces actúas demasiado rápido y el pensamiento llega después.\n\n"

    "La saturación aparece como irritación mental, discusión constante "
    "o sensación de estar empujándote continuamente a hacer algo. "
    "La comunicación puede volverse defensiva o combativa "
    "sin que exista intención consciente de conflicto.\n\n"

    "Sueles regularte mejor diferenciando momentos de reflexión "
    "y momentos de ejecución."
),

("Mercurio", "Marte", "☍"): (
    "Mercurio oponiéndose a Marte: pensar y actuar parecen tirar en direcciones opuestas. "
    "Cuando analizas mucho, actuar cuesta; "
    "cuando actúas impulsivamente, el procesamiento queda atrás.\n\n"

    "La tensión suele aparecer entre planificación y ejecución. "
    "Puedes alternar entre exceso de preparación "
    "y movimiento demasiado rápido.\n\n"

    "La regulación mejora cuando pensamiento y acción encuentran un ritmo de colaboración "
    "en lugar de sustituirse mutuamente."
),

("Mercurio", "Marte", "△"): (
    "Mercurio en trígono a Marte: pensamiento y acción colaboran de forma natural. "
    "Sueles organizar, decidir y ejecutar sin demasiada fricción interna.\n\n"

    "La facilidad aporta rapidez y capacidad resolutiva, "
    "aunque a veces puede hacer que actúes tan fluidamente "
    "que no detectes momentos donde sería útil detenerte un poco más.\n\n"

    "Sueles regularte bien mediante acción clara y objetivos concretos."
),

("Mercurio", "Marte", "✶"): (
    "Mercurio en sextil a Marte: existe compatibilidad entre claridad mental y capacidad de acción. "
    "Puedes transformar ideas en movimiento con relativa facilidad "
    "cuando existe dirección consciente.\n\n"

    "Esta conexión funciona especialmente bien "
    "cuando tienes objetivos claros y espacio para actuar progresivamente."
),

# ── Venus – Marte ─────────────────────────────────────────────────────────────

("Venus", "Marte", "="): (
    "Venus y Marte en conjunción: vínculo y acción funcionan a través del mismo circuito energético. "
    "La conexión afectiva moviliza intensamente tu energía "
    "y gran parte de tu impulso se dirige hacia los vínculos.\n\n"

    "Deseo, iniciativa, atracción y conflicto pueden aparecer muy mezclados entre sí. "
    "Las relaciones rara vez se viven de forma tibia.\n\n"

    "Sueles regularte mejor cuando existe espacio para deseo, movimiento "
    "y expresión directa dentro del vínculo."
),

("Venus", "Marte", "□"): (
    "Venus cuadrando Marte: tu necesidad de vínculo y tu forma de actuar "
    "entran fácilmente en fricción. "
    "A veces lo que deseas emocionalmente "
    "no coincide con la dirección hacia la que impulsa tu energía.\n\n"

    "La saturación aparece cuando la acción daña la conexión "
    "o cuando el vínculo absorbe toda la energía disponible. "
    "Puede existir tensión entre autonomía y relación, "
    "entre deseo de estabilidad y necesidad de movimiento.\n\n"

    "La regulación requiere aprender a sostener ambas fuerzas "
    "sin que una anule completamente a la otra."
),

("Venus", "Marte", "☍"): (
    "Venus oponiéndose a Marte: vínculo y acción parecen pedir direcciones diferentes. "
    "Cuando priorizas la relación, la acción propia puede detenerse; "
    "cuando sigues plenamente tu impulso, el vínculo puede quedar en segundo plano.\n\n"

    "La tensión aparece porque ambas necesidades compiten por energía y prioridad. "
    "Puedes sentir que elegir una implica alejarte temporalmente de la otra.\n\n"

    "Sueles regularte mejor cuando aprendes a alternar conscientemente "
    "momentos de conexión y momentos de afirmación personal."
),

("Venus", "Marte", "△"): (
    "Venus en trígono a Marte: vínculo y acción cooperan de forma fluida. "
    "Puedes relacionarte sin perder impulso propio "
    "y la acción puede fortalecer el vínculo en lugar de dañarlo.\n\n"

    "Existe facilidad para combinar deseo, iniciativa y conexión afectiva. "
    "Las relaciones tienden a sentirse vivas, dinámicas y movilizadoras.\n\n"

    "Sueles regularte bien en vínculos donde existe expresión mutua, movimiento "
    "y autenticidad."
),

("Venus", "Marte", "✶"): (
    "Venus en sextil a Marte: existe compatibilidad entre vínculo y acción. "
    "Puedes relacionarte y actuar de forma complementaria "
    "cuando existe claridad y consciencia.\n\n"

    "La conexión entre afecto y movimiento puede convertirse en un recurso importante "
    "tanto para relaciones como para proyectos personales."
),

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


def calcular_aspectos_personales(planetas):
    """Calcula aspectos entre Mercurio, Venus y Marte."""

    pares = [
        ("Mercurio", "Venus"),
        ("Mercurio", "Marte"),
        ("Venus",    "Marte"),
    ]

    aspectos = []

    for p1_nom, p2_nom in pares:

        p1 = planetas.get(p1_nom)
        p2 = planetas.get(p2_nom)

        if not p1 or not p2:
            continue

        diff = abs(p1["lon"] - p2["lon"]) % 360

        if diff > 180:
            diff = 360 - diff

        for tipo, angulo, orbe_max, simbolo in ASPECTOS_DEF:

            if abs(diff - angulo) <= orbe_max:

                orbe_val = round(abs(diff - angulo), 2)

                aspectos.append({
                    "p1": p1_nom,
                    "p2": p2_nom,
                    "tipo": tipo,
                    "simbolo": simbolo,
                    "orbe": orbe_val,
                    "relevancia": (
                        "exacto"
                        if orbe_val <= 1.0
                        else "estructural"
                    ),
                })

                break

    return sorted(aspectos, key=lambda x: x["orbe"])


def detectar_estelium_personales(planetas):
    """
    Detecta concentración funcional entre Mercurio, Venus y Marte.
    No depende únicamente de aspectos clásicos.
    """

    personales = []

    for nombre in ["Mercurio", "Venus", "Marte"]:

        p = planetas.get(nombre)

        if p:
            personales.append({
                "nombre": nombre,
                "lon": p["lon"],
                "signo": p["signo"],
                "casa": p["casa"]
            })

    if len(personales) < 2:
        return []

    personales.sort(key=lambda x: x["lon"])

    grupo = [personales[0]]

    for i in range(1, len(personales)):

        actual = personales[i]
        previo = personales[i - 1]

        diff = abs(actual["lon"] - previo["lon"])

        if diff > 180:
            diff = 360 - diff

        # margen amplio para continuidad funcional
        if diff <= 18:
            grupo.append(actual)

    if len(grupo) >= 2:
        return grupo

    return []


# ─── TEXTOS DE SECCIÓN ────────────────────────────────────────────────────────

def _get_asp(aspectos, p1, p2):
    """Devuelve el aspecto entre dos planetas o None."""
    return next(
        (a for a in aspectos
         if (a["p1"] == p1 and a["p2"] == p2) or (a["p1"] == p2 and a["p2"] == p1)),
        None
    )


def _texto_asp(p1, p2, asp):
    """Devuelve el texto del aspecto del dict, o None si no existe."""
    if asp is None:
        return None
    clave1 = (p1, p2, asp["simbolo"])
    clave2 = (p2, p1, asp["simbolo"])
    return ASPECTOS_PERSONALES.get(clave1) or ASPECTOS_PERSONALES.get(clave2)


def _es_aspecto_tenso(asp):
    return asp and asp.get("simbolo") in ("□", "☍", "⚻")


def _es_conjuncion(asp):
    return asp and asp.get("simbolo") == "="


def _lista_nombres_estelium(estelium):
    orden = ["Mercurio", "Venus", "Marte"]
    nombres = [p["nombre"] for p in estelium]
    nombres = [n for n in orden if n in nombres]
    return ", ".join(nombres)


def _signos_estelium(estelium):
    signos = []
    for p in estelium:
        s = p.get("signo", "")
        if s and s not in signos:
            signos.append(s)
    return ", ".join(signos)


def _casas_estelium(estelium):
    casas = []
    for p in estelium:
        c = str(p.get("casa", ""))
        if c and c not in casas:
            casas.append(c)
    return ", ".join(casas)


def texto_funcionamiento_general(carta, aspectos):
    planetas = carta["planetas"]

    merc  = planetas.get("Mercurio", {})
    venus = planetas.get("Venus", {})
    marte = planetas.get("Marte", {})

    merc_sig  = merc.get("signo", "")
    merc_casa = merc.get("casa", "")
    ven_sig   = venus.get("signo", "")
    ven_casa  = venus.get("casa", "")
    mar_sig   = marte.get("signo", "")
    mar_casa  = marte.get("casa", "")

    elem_merc  = ELEMENTO_SIGNO.get(merc_sig, "")
    elem_venus = ELEMENTO_SIGNO.get(ven_sig, "")
    elem_marte = ELEMENTO_SIGNO.get(mar_sig, "")

    texto = (
        f"Mercurio está en {merc_sig}, Casa {merc_casa}: "
        f"muestra cómo piensas, cómo ordenas lo que percibes "
        f"y cómo traduces lo que ocurre en palabras o ideas.\n"
        f"Venus está en {ven_sig}, Casa {ven_casa}: "
        f"muestra cómo te vinculas, qué necesitas para sentir conexión "
        f"y cómo buscas equilibrio afectivo.\n"
        f"Marte está en {mar_sig}, Casa {mar_casa}: "
        f"muestra cómo se activa tu acción, cómo descargas energía "
        f"y cómo respondes ante el impulso."
    )

    estelium = detectar_estelium_personales(planetas)

    if len(estelium) >= 3:
        nombres = _lista_nombres_estelium(estelium)
        signos = _signos_estelium(estelium)
        casas = _casas_estelium(estelium)

        texto += (
            f"\n\nHay una concentración funcional de planetas personales: {nombres}. "
            f"Esto indica que pensamiento, vínculo y acción no funcionan como partes aisladas, "
            f"sino como un mismo campo de experiencia. "
            f"Esta concentración se expresa en {signos}, en las casas {casas}."
        )

        texto += (
            "\n\nCuando una de estas áreas se activa, las otras suelen responder rápidamente. "
            "Lo que piensas puede afectar a la forma en que te vinculas; "
            "lo que ocurre en tus relaciones puede modificar tu energía disponible; "
            "y la acción puede cambiar con rapidez la manera en que entiendes lo que estás viviendo. "
            "La ventaja es intensidad, coherencia interna y capacidad de respuesta. "
            "El riesgo es que, bajo presión, una sola área desorganizada arrastre a las demás."
        )

    elif len(estelium) == 2:
        nombres = _lista_nombres_estelium(estelium)

        texto += (
            f"\n\nHay una concentración funcional entre {nombres}. "
            "Estas dos áreas tienden a activarse de forma cercana. "
            "Cuando una se mueve, la otra suele implicarse también. "
            "Esto puede dar fluidez, pero también puede hacer que cueste separarlas bajo presión."
        )

    pares_ok = []
    pares_fric = []

    pares_comp = [
        ("tu forma de pensar", "Mercurio", elem_merc, "tu forma de vincularte", "Venus", elem_venus),
        ("tu forma de pensar", "Mercurio", elem_merc, "tu forma de actuar", "Marte", elem_marte),
        ("tu forma de vincularte", "Venus", elem_venus, "tu forma de actuar", "Marte", elem_marte),
    ]

    for a_func, a_plan, a_elem, b_func, b_plan, b_elem in pares_comp:
        if not a_elem or not b_elem:
            continue

        if a_elem == b_elem:
            pares_ok.append(f"{a_func} ({a_plan}) y {b_func} ({b_plan}) comparten elemento: {a_elem}")
        elif {a_elem, b_elem} in ({"Fuego", "Aire"}, {"Tierra", "Agua"}):
            pares_ok.append(f"{a_func} ({a_plan}) y {b_func} ({b_plan}) se apoyan por elementos compatibles: {a_elem}/{b_elem}")
        else:
            pares_fric.append(f"{a_func} ({a_plan}, {a_elem}) y {b_func} ({b_plan}, {b_elem})")

    if pares_ok:
        texto += f"\n\nHay coherencia elemental entre: {'; '.join(pares_ok)}. "
        texto += (
            "Esto facilita que esas áreas colaboren entre sí. "
            "Aun así, lo que fluye con facilidad también puede volverse automático "
            "si no lo observas con consciencia."
        )

    if pares_fric:
        texto += f"\n\nHay tensión elemental entre: {'; '.join(pares_fric)}. "
        texto += (
            "Esto no es un problema en sí mismo, pero sí pide más atención. "
            "Cuando esas áreas necesitan cooperar, conviene hacer una integración consciente "
            "para que una no bloquee, desborde o desconecte a la otra."
        )

    conjunciones = []
    otros_aspectos = []

    for p1, p2 in [("Mercurio", "Venus"), ("Mercurio", "Marte"), ("Venus", "Marte")]:
        asp = _get_asp(aspectos, p1, p2)
        if asp:
            if _es_conjuncion(asp):
                conjunciones.append(f"{p1}–{p2} en conjunción (orbe {asp['orbe']}°)")
            else:
                otros_aspectos.append(f"{p1}–{p2} en {asp['tipo'].lower()} (orbe {asp['orbe']}°)")

    if conjunciones:
        texto += f"\n\nHay conjunción entre planetas personales: {', '.join(conjunciones)}. "
        texto += (
            "Una conjunción une dos funciones de forma muy estrecha. "
            "No se vive como una simple relación entre partes separadas, "
            "sino como una mezcla interna: esas áreas tienden a encenderse juntas "
            "y a responder como una unidad."
        )

    if otros_aspectos:
        texto += f"\n\nOtros aspectos entre planetas personales: {', '.join(otros_aspectos)}."

    if not conjunciones and not otros_aspectos:
        texto += (
            "\n\nNo aparecen aspectos clásicos entre los planetas personales dentro de los orbes definidos. "
            "Aun así, puede existir una concentración funcional si los planetas están próximos por signo, "
            "por casa o por continuidad de experiencia."
        )

    return texto


def texto_mercurio(carta, aspectos):
    planetas = carta["planetas"]
    merc = planetas.get("Mercurio", {})
    sig  = merc.get("signo", "")
    casa = merc.get("casa", 1)
    ret  = merc.get("retrogrado", False)

    t = MERCURIO_SIGNO.get(sig, "")
    t += "\n\n" + MERCURIO_CASA.get(casa, "")

    if ret:
        t += (
            "\n\nMercurio está retrógrado. Tu forma de procesar tiende a ser más interna "
            "y necesita más revisión antes de salir hacia afuera. "
            "Las conclusiones pueden llegar después de varias vueltas internas, "
            "y comunicar con claridad puede requerir más tiempo."
        )

    aspectos_merc = []

    for p2 in ("Venus", "Marte"):
        asp = _get_asp(aspectos, "Mercurio", p2)
        t_asp = _texto_asp("Mercurio", p2, asp)
        if t_asp:
            aspectos_merc.append(t_asp)

    if aspectos_merc:
        t += "\n\nEn relación con los otros planetas personales:"
        t += "\n\n" + "\n\n".join(aspectos_merc)

    return t


def texto_venus(carta, aspectos):
    planetas = carta["planetas"]
    venus = planetas.get("Venus", {})
    sig   = venus.get("signo", "")
    casa  = venus.get("casa", 1)
    ret   = venus.get("retrogrado", False)

    t = VENUS_SIGNO.get(sig, "")
    t += "\n\n" + VENUS_CASA.get(casa, "")

    if ret:
        t += (
            "\n\nVenus está retrógrada. Tu forma de vincularte puede ser más interna, "
            "más reflexiva o necesitar revisión consciente. "
            "Puedes tardar más en reconocer qué necesitas en relación, "
            "qué contacto te resulta suficiente y qué tipo de vínculo puedes sostener."
        )

    aspectos_venus = []

    asp_vm = _get_asp(aspectos, "Venus", "Marte")
    t_asp = _texto_asp("Venus", "Marte", asp_vm)
    if t_asp:
        aspectos_venus.append(t_asp)

    if aspectos_venus:
        t += "\n\nEn relación con los otros planetas personales:"
        t += "\n\n" + "\n\n".join(aspectos_venus)

    return t


def texto_marte(carta, aspectos):
    planetas = carta["planetas"]
    marte = planetas.get("Marte", {})
    sig   = marte.get("signo", "")
    casa  = marte.get("casa", 1)
    ret   = marte.get("retrogrado", False)

    t = MARTE_SIGNO.get(sig, "")
    t += "\n\n" + MARTE_CASA.get(casa, "")

    if ret:
        t += (
            "\n\nMarte está retrógrado. Tu energía de acción puede ir primero hacia adentro "
            "antes de encontrar una salida clara. "
            "Puedes tardar más en iniciar, acumular impulso sin descargarlo "
            "o revisar muchas veces una acción antes de ejecutarla. "
            "Cuando la acción finalmente aparece, puede hacerlo con más carga acumulada."
        )

    return t


def texto_integracion(carta, aspectos):
    planetas = carta["planetas"]

    merc  = planetas.get("Mercurio", {})
    venus = planetas.get("Venus", {})
    marte = planetas.get("Marte", {})

    merc_sig = merc.get("signo", "")
    ven_sig  = venus.get("signo", "")
    mar_sig  = marte.get("signo", "")

    elem_merc  = ELEMENTO_SIGNO.get(merc_sig, "")
    elem_venus = ELEMENTO_SIGNO.get(ven_sig, "")
    elem_marte = ELEMENTO_SIGNO.get(mar_sig, "")

    partes = []

    estelium = detectar_estelium_personales(planetas)

    if len(estelium) >= 3:
        nombres = _lista_nombres_estelium(estelium)
        partes.append(
            f"La integración principal de esta carta se organiza alrededor de la concentración funcional "
            f"de {nombres}. Esto significa que pensamiento, vínculo y acción están muy cerca entre sí. "
            f"No conviene leerlos como partes completamente separadas: cuando una se mueve, "
            f"las otras suelen implicarse."
        )

        partes.append(
            "La clave no es separar artificialmente estas áreas, sino aprender a reconocer "
            "dónde empieza la desorganización. A veces comienza por exceso de pensamiento; "
            "otras por absorción relacional; otras por acción impulsiva o por falta de descarga. "
            "La regulación consiste en localizar la primera señal antes de que todo el circuito entre en saturación."
        )

    elif len(estelium) == 2:
        nombres = _lista_nombres_estelium(estelium)
        partes.append(
            f"Hay una integración fuerte entre {nombres}. "
            "Estas áreas se activan de manera cercana y conviene observarlas juntas. "
            "A veces una de ellas expresa la tensión que en realidad empezó en la otra."
        )

    asp_mv = _get_asp(aspectos, "Mercurio", "Venus")
    if asp_mv:
        if _es_conjuncion(asp_mv):
            partes.append(
                "La conjunción Mercurio–Venus une pensamiento y vínculo. "
                "Tiendes a pensar lo relacional y a vincularte a través de la palabra, "
                "la comprensión y el intercambio. "
                "Esto puede darte mucha capacidad para comunicar lo que ocurre en una relación, "
                "pero también puede hacer que analizar el vínculo sustituya a estar realmente dentro de él."
            )
        else:
            t_asp = _texto_asp("Mercurio", "Venus", asp_mv)
            if t_asp:
                partes.append(t_asp)
    else:
        if elem_merc == elem_venus:
            partes.append(
                f"Mercurio y Venus comparten elemento en {elem_merc}. "
                "Tu forma de pensar y tu forma de vincularte pueden comprenderse con relativa facilidad. "
                "Suele haber continuidad entre lo que percibes, lo que sientes "
                "y lo que necesitas expresar en relación."
            )
        elif {elem_merc, elem_venus} not in ({"Fuego", "Aire"}, {"Tierra", "Agua"}):
            partes.append(
                f"Mercurio ({merc_sig}, {elem_merc}) y Venus ({ven_sig}, {elem_venus}) "
                f"operan en elementos que crean tensión. "
                "Lo que necesitas para procesar y lo que necesitas para vincularte "
                "no siempre siguen la misma lógica."
            )

    asp_mm = _get_asp(aspectos, "Mercurio", "Marte")
    if asp_mm:
        if _es_conjuncion(asp_mm):
            partes.append(
                "La conjunción Mercurio–Marte une pensamiento y acción. "
                "Tiendes a actuar rápidamente sobre lo que piensas, "
                "y la palabra puede salir cargada de fuerza, dirección o impaciencia. "
                "La ventaja es capacidad de decisión y respuesta. "
                "El riesgo es actuar antes de haber terminado de procesar."
            )
        else:
            t_asp = _texto_asp("Mercurio", "Marte", asp_mm)
            if t_asp:
                partes.append(t_asp)
    else:
        if elem_merc == elem_marte:
            partes.append(
                f"Mercurio y Marte comparten elemento en {elem_merc}. "
                "El pensamiento puede convertirse en acción sin demasiada fricción. "
                "La facilidad está en pasar de la idea al movimiento; "
                "la observación necesaria está en no actuar automáticamente sin verificar."
            )
        elif {elem_merc, elem_marte} not in ({"Fuego", "Aire"}, {"Tierra", "Agua"}):
            partes.append(
                f"Mercurio ({merc_sig}, {elem_merc}) y Marte ({mar_sig}, {elem_marte}) "
                f"operan en elementos que crean tensión. "
                "Tu modo de procesar y tu modo de actuar no se alimentan de forma directa. "
                "Puede haber mucho pensamiento sin movimiento, "
                "o acción antes de que exista claridad suficiente."
            )

    asp_vm = _get_asp(aspectos, "Venus", "Marte")
    if asp_vm:
        if _es_conjuncion(asp_vm):
            partes.append(
                "La conjunción Venus–Marte une vínculo y acción. "
                "Tiendes a activar mucha energía en el campo relacional: "
                "deseo, iniciativa, atracción, conflicto y movimiento pueden aparecer muy cerca entre sí. "
                "La ventaja es vitalidad afectiva. "
                "El riesgo es que la relación se convierta en el lugar principal de descarga energética."
            )
        else:
            t_asp = _texto_asp("Venus", "Marte", asp_vm)
            if t_asp:
                partes.append(t_asp)
    else:
        if elem_venus == elem_marte:
            partes.append(
                f"Venus y Marte comparten elemento en {elem_venus}. "
                "Tu forma de vincularte y tu forma de actuar pueden colaborar con relativa facilidad. "
                "La energía disponible puede alimentar la relación, "
                "y el vínculo puede sostener el movimiento."
            )
        elif {elem_venus, elem_marte} not in ({"Fuego", "Aire"}, {"Tierra", "Agua"}):
            partes.append(
                f"Venus ({ven_sig}, {elem_venus}) y Marte ({mar_sig}, {elem_marte}) "
                f"operan en elementos que crean tensión. "
                "Lo que necesitas para conectar y lo que necesitas para actuar "
                "no siempre se refuerzan. "
                "Cuando hay demanda simultánea de vínculo y acción, "
                "puedes tender a priorizar una cosa a expensas de la otra."
            )

    MERC_DIS = {
        "Fuego":  "acelera hacia conclusiones antes de que el análisis esté completo",
        "Tierra": "se fija en una posición y le cuesta actualizarla",
        "Aire":   "multiplica perspectivas sin llegar a una dirección clara",
        "Agua":   "queda atrapado repasando lo que no ha terminado de procesar emocionalmente",
    }

    VEN_DIS = {
        "Fuego":  "se aleja del vínculo o usa la relación como escenario de descarga",
        "Tierra": "se cierra lentamente y deja de estar disponible",
        "Aire":   "distribuye la energía relacional sin concentrarla en un vínculo real",
        "Agua":   "absorbe el estado del entorno y pierde la referencia de lo que necesita",
    }

    MART_DIS = {
        "Fuego":  "busca cualquier fricción disponible como salida",
        "Tierra": "se comprime, se endurece y acumula tensión",
        "Aire":   "genera agitación que no siempre produce movimiento real",
        "Agua":   "se disipa o actúa en dirección del entorno antes que desde el propio impulso",
    }

    partes.append(
        f"Cuando hay demasiada presión, puede aparecer una cadena reconocible: "
        f"Mercurio en {merc_sig} {MERC_DIS.get(elem_merc, 'pierde regulación')}. "
        f"Desde ahí, Venus en {ven_sig} {VEN_DIS.get(elem_venus, 'se desregula')}. "
        f"Y Marte en {mar_sig} {MART_DIS.get(elem_marte, 'pierde dirección')}. "
        f"El ciclo se cierra cuando la energía acumulada vuelve a saturar el punto inicial."
    )

    return "\n\n".join(partes)

def texto_orientacion(carta, aspectos):
    planetas = carta["planetas"]

    merc  = planetas.get("Mercurio", {})
    venus = planetas.get("Venus", {})
    marte = planetas.get("Marte", {})

    merc_sig  = merc.get("signo", "")
    merc_casa = merc.get("casa", 1)
    ven_sig   = venus.get("signo", "")
    ven_casa  = venus.get("casa", 1)
    mar_sig   = marte.get("signo", "")
    mar_casa  = marte.get("casa", 1)

    elem_merc  = ELEMENTO_SIGNO.get(merc_sig, "")
    elem_venus = ELEMENTO_SIGNO.get(ven_sig, "")
    elem_marte = ELEMENTO_SIGNO.get(mar_sig, "")

    estelium = detectar_estelium_personales(planetas)

    orden_activacion = {"Fuego": 0, "Aire": 1, "Tierra": 2, "Agua": 3}

    funciones = [
        ("tu forma de pensar", "Mercurio", merc_sig, merc_casa, elem_merc),
        ("tu forma de vincularte", "Venus", ven_sig, ven_casa, elem_venus),
        ("tu forma de actuar", "Marte", mar_sig, mar_casa, elem_marte),
    ]

    funcion_inicio = min(funciones, key=lambda x: orden_activacion.get(x[4], 2))
    f_func, f_planeta, f_sig, f_casa, f_elem = funcion_inicio

    inicio_detail = {
        "Fuego":  "activar el movimiento antes de intentar resolverlo todo mentalmente",
        "Aire":   "ponerlo en palabras, escribirlo o llevarlo a un intercambio claro",
        "Tierra": "llevarlo a una acción concreta, pequeña y verificable",
        "Agua":   "darte tiempo de registro antes de exigir claridad o acción",
    }

    if len(estelium) >= 3:
        desde_donde = (
            f"Al haber una concentración funcional de los tres planetas personales, "
            f"no conviene empezar intentando resolverlo todo a la vez. "
            f"La entrada más útil suele ser {f_func} ({f_planeta}) en {f_sig}, Casa {f_casa}: "
            f"{inicio_detail.get(f_elem, 'activar su modo natural')}. "
            f"Desde ahí, el resto puede empezar a ordenarse con más facilidad."
        )
    else:
        desde_donde = (
            f"Desde {f_func} ({f_planeta}) en {f_sig}, Casa {f_casa}. "
            f"De las tres áreas, esta suele requerir menos energía para activarse. "
            f"La entrada es {inicio_detail.get(f_elem, 'activar su modo natural')}. "
            f"Empezar por aquí puede abrir movimiento en el resto."
        )

    degradacion = {"Agua": 0, "Tierra": 1, "Aire": 2, "Fuego": 3}
    funcion_sostener = min(funciones, key=lambda x: degradacion.get(x[4], 2))
    fs_func, fs_planeta, fs_sig, fs_casa, fs_elem = funcion_sostener

    sostenimiento_detail = {
        "Agua":   "tiempo de integración, silencio emocional y límites sensibles",
        "Tierra": "estructura concreta, ritmo estable y resultado tangible",
        "Aire":   "espacio mental, palabra clara e intercambio regulado",
        "Fuego":  "objetivo vivo, movimiento y margen de iniciativa",
    }

    sostener = (
        f"Conviene sostener especialmente {fs_func} ({fs_planeta}) en {fs_sig}: "
        f"{sostenimiento_detail.get(fs_elem, 'su modo natural de regulación')}. "
        f"Bajo presión, esta área puede desorganizarse antes que las demás. "
        f"Cuando se estabiliza, el resto de tu funcionamiento tiene más capacidad para reorganizarse."
    )

    bucles = []

    asp_mm = _get_asp(aspectos, "Mercurio", "Marte")
    asp_mv = _get_asp(aspectos, "Mercurio", "Venus")
    asp_vm = _get_asp(aspectos, "Venus", "Marte")

    if _es_conjuncion(asp_mv):
        bucles.append(
            "confundir comprender el vínculo con estar realmente disponible dentro de él"
        )
    elif _es_aspecto_tenso(asp_mv):
        bucles.append(
            "entrar en el bucle pensamiento-vínculo: analizar la relación sin que eso produzca más presencia"
        )

    if _es_conjuncion(asp_mm):
        bucles.append(
            "actuar demasiado rápido sobre una conclusión que todavía no estaba terminada"
        )
    elif _es_aspecto_tenso(asp_mm):
        bucles.append(
            "entrar en el bucle pensamiento-acción: analizar sin ejecutar o ejecutar sin haber procesado"
        )

    if _es_conjuncion(asp_vm):
        bucles.append(
            "usar el vínculo como lugar principal de descarga de la energía"
        )
    elif _es_aspecto_tenso(asp_vm):
        bucles.append(
            "entrar en el bucle vínculo-acción: detener la acción propia por tensión relacional "
            "o descargar en el vínculo una energía que necesitaba otro canal"
        )

    if len(estelium) >= 3:
        bucles.append(
            "intentar regular pensamiento, vínculo y acción como si fueran áreas independientes, "
            "cuando en realidad están funcionando de forma muy conectada"
        )

    if not bucles:
        bucles.append(
            "asumir que la ausencia de fricción visible significa que todo está bien. "
            "A veces los bucles no hacen ruido porque te has acostumbrado a funcionar así"
        )

    evitar = "Evitar " + "; ".join(bucles) + "."

    if len(estelium) >= 3:
        si_no = (
            "Si no se sostiene: no se desorganiza una parte aislada, sino una cadena completa. "
            "La claridad mental puede disminuir, el vínculo puede absorber demasiado o desconectarse, "
            "y la acción puede buscar una salida rápida o quedar bloqueada. "
            "La regulación empieza cuando detectas cuál de las tres áreas se alteró primero."
        )
    else:
        si_no = (
            "Si no se sostiene: pensamiento, vínculo y acción empiezan a funcionar por separado. "
            "Lo que piensas no alimenta la acción, la acción no informa al vínculo "
            "y el vínculo no regula la energía disponible. "
            "El esfuerzo aumenta, la claridad disminuye y la saturación llega antes."
        )

    return {
        "desde_donde": desde_donde,
        "sostener": sostener,
        "evitar": evitar,
        "si_no": si_no,
    }

# ─── RUEDA SIMPLIFICADA: PLANETAS PERSONALES ────────────────────────────────

def dibujar_rueda_planetas_personales(carta, archivo_salida):
    """Rueda simplificada: Mercurio, Venus y Marte."""
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

    nombres_personales = ["Mercurio", "Venus", "Marte"]

    puntos_aspecto = {
        nombre: planetas.get(nombre)
        for nombre in nombres_personales
        if planetas.get(nombre)
    }

    pares_aspecto = []
    for i, p1 in enumerate(nombres_personales):
        for p2 in nombres_personales[i + 1:]:
            pares_aspecto.append((p1, p2))

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

                ax.plot(
                    [math.cos(a1) * R_ASP, math.cos(a2) * R_ASP],
                    [math.sin(a1) * R_ASP, math.sin(a2) * R_ASP],
                    color=_ASP_COL[simbolo],
                    linewidth=_ASP_LW[simbolo],
                    alpha=0.60,
                    linestyle="solid",
                    zorder=2,
                )
                break

    puntos = {
        nombre: planetas.get(nombre)
        for nombre in nombres_personales
        if planetas.get(nombre)
    }

    lones_usados = []
    radios = {}

    for nombre, p in puntos.items():
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
        ang = lon_a_angulo(p["lon"])
        r = radios[nombre]
        color = COLORES_PLANETA.get(nombre, "#333")
        simbolo = p["simbolo"]

        fs = 22 if nombre in ("Sol", "Luna") else 18

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

    plt.title("Planetas personales", fontsize=12, fontweight="bold", pad=12, color="#1E508C")
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
    asc       = carta["asc"]
    mc        = carta["mc"]
    merc  = planetas.get("Mercurio", {})
    venus = planetas.get("Venus",    {})
    marte = planetas.get("Marte",    {})
    ruta_rueda = os.path.basename(ruta_rueda).replace("\\", "/")

    fecha_str  = f"{dia:02d}/{mes:02d}/{anio}"
    hora_str   = f"{hora:02d}:{minuto:02d}"
    tz_obj     = pytz.timezone(tz_name)
    dt_local   = tz_obj.localize(datetime(anio, mes, dia, hora, minuto))
    utc_off    = dt_local.strftime("%z")
    utc_str    = f"UTC{utc_off[:3]}:{utc_off[3:]}"
    nom_esc    = esc(nombre)
    ciu_esc    = esc(ciudad)

    def signo_casa(p):
        return f"{esc(p.get('signo',''))} — Casa {p.get('casa','')} {grado_a_dms(p.get('grado',0))}"

    t_gral   = texto_funcionamiento_general(carta, aspectos)
    t_merc   = texto_mercurio(carta, aspectos)
    t_venus  = texto_venus(carta, aspectos)
    t_marte  = texto_marte(carta, aspectos)
    t_integ  = texto_integracion(carta, aspectos)
    t_or     = texto_orientacion(carta, aspectos)

    # Tabla de aspectos
    _ASP_TEX = {"=":"conj","☍":"opo","□":"cua","△":"tri","✶":"sex","⚻":"qui"}
    asp_rows = ""
    for a in aspectos:
        asp_rows += (
            f"  {esc(a['p1'])} & {esc(_ASP_TEX.get(a['simbolo'], a['simbolo']))} & "
            f"{esc(a['p2'])} & {esc(a['tipo'])} & {a['orbe']:.1f}° \\\\\n"
        )

    if asp_rows.strip():
        tabla_aspectos = (
            "\\begin{center}\n"
            "\\begin{tabular}{lllll}\n"
            "  \\toprule\n"
            "  \\textbf{Planeta 1} & \\textbf{Asp.} & \\textbf{Planeta 2} "
            "& \\textbf{Tipo} & \\textbf{Orbe} \\\\\n"
            "  \\midrule\n"
            f"{asp_rows}"
            "  \\bottomrule\n"
            "\\end{tabular}\n"
            "\\end{center}"
        )
    else:
        tabla_aspectos = "\\vspace{0.3cm}\\textit{No hay aspectos entre los planetas personales en los orbes definidos.}"

    def parrafos(texto):
        return "\n\n".join(esc(p) for p in texto.split("\n\n") if p.strip())

    ret_merc  = " (Rx)" if merc.get("retrogrado")  else ""
    ret_venus = " (Rx)" if venus.get("retrogrado") else ""
    ret_marte = " (Rx)" if marte.get("retrogrado") else ""

    latex = f"""\\documentclass[11pt,a4paper]{{article}}

\\usepackage[utf8]{{inputenc}}
\\usepackage[T1]{{fontenc}}
\\usepackage[spanish]{{babel}}

\\usepackage{{tgpagella}}
\\usepackage{{geometry}}
\\usepackage{{booktabs}}
\\usepackage{{xcolor}}
\\usepackage{{graphicx}}
\\usepackage{{titlesec}}
\\usepackage{{fancyhdr}}
\\usepackage[parfill]{{parskip}}
\\usepackage[expansion=false]{{microtype}}
\\usepackage{{hyperref}}
\\usepackage{{setspace}}
\\usepackage{{needspace}}
\\usepackage{{etoolbox}}
\\usepackage{{ragged2e}}

\\widowpenalty=10000
\\clubpenalty=10000
\\displaywidowpenalty=10000

\\hyphenpenalty=8000
\\exhyphenpenalty=8000

\\geometry{{top=3.0cm,bottom=3.0cm,left=3.5cm,right=3.5cm}}

\\setlength{{\\parskip}}{{0.65em}}
\\setlength{{\\parindent}}{{0em}}

\\definecolor{{azulai}}{{RGB}}{{30,80,140}}
\\definecolor{{doradoai}}{{RGB}}{{140,90,0}}
\\definecolor{{grisai}}{{RGB}}{{70,70,70}}

\\AtBeginDocument{{\\justifying}}

\\titleformat{{\\section}}
{{\\Large\\bfseries\\color{{azulai}}\\justifying}}
{{}}
{{0em}}
{{}}
[{{\\color{{azulai}}\\titlerule[0.5pt]}}]

\\titlespacing*{{\\section}}
{{0pt}}{{1.3em}}{{0.5em}}

\\titleformat{{\\subsection}}
{{\\large\\bfseries\\color{{doradoai}}\\justifying}}
{{}}
{{0em}}
{{}}

\\titlespacing*{{\\subsection}}
{{0pt}}{{1.0em}}{{0.35em}}

\\titleformat{{\\subsubsection}}
{{\\normalsize\\bfseries\\color{{grisai}}\\justifying}}
{{}}
{{0em}}
{{}}

\\titlespacing*{{\\subsubsection}}
{{0pt}}{{0.8em}}{{0.25em}}

\\preto\\section{{\\Needspace{{8\\baselineskip}}}}
\\preto\\subsection{{\\Needspace{{6\\baselineskip}}}}
\\preto\\subsubsection{{\\Needspace{{4\\baselineskip}}}}

\\pagestyle{{fancy}}
\\fancyhf{{}}

\\rhead{{\\textcolor{{grisai}}{{\\small {nom_esc} — Arquitectura Interna}}}}
\\lhead{{\\textcolor{{grisai}}{{\\small Mercurio · Venus · Marte}}}}
\\cfoot{{\\textcolor{{grisai}}{{\\small\\thepage}}}}

\\renewcommand{{\\headrulewidth}}{{0.3pt}}

\\hypersetup{{
colorlinks=true,
linkcolor=azulai,
urlcolor=azulai
}}

\\setstretch{{1.32}}

\\tolerance=1500
\\emergencystretch=4em

\\begin{{document}}

% ── Portada ──────────────────────────────────────────────────────────────────

\\begin{{titlepage}}
  \\centering

  \\vspace*{{2cm}}

  {{\\Huge\\bfseries\\color{{azulai}} Mercurio · Venus · Marte}}\\\\[0.6cm]

  {{\\large\\color{{grisai}} Arquitectura Interna}}\\\\[0.4cm]

  {{\\small\\itshape\\color{{grisai}}
  Procesamiento, vínculo y acción en el funcionamiento cotidiano
  }}\\\\[2.2cm]

  {{\\huge\\color{{doradoai}} {nom_esc}}}\\\\[1.6cm]

  {{\\Large {fecha_str} \\quad {hora_str}}}\\\\[0.35cm]

  {{\\Large {ciu_esc}}}\\\\[0.35cm]

  {{\\normalsize
  Lat: {lat:.4f}° \\quad
  Lon: {lon:.4f}° \\quad
  {utc_str}
  }}\\\\[0.35cm]

  {{\\normalsize
  Ascendente: {esc(asc['signo'])} {grado_a_dms(asc['grado'])}
  \\quad
  MC: {esc(mc['signo'])} {grado_a_dms(mc['grado'])}
  }}\\\\[2.2cm]

  \\renewcommand{{\\arraystretch}}{{1.35}}

  \\begin{{tabular}}{{ll}}
    \\textbf{{Mercurio:}} & {signo_casa(merc)}{ret_merc} \\\\
    \\textbf{{Venus:}}    & {signo_casa(venus)}{ret_venus} \\\\
    \\textbf{{Marte:}}    & {signo_casa(marte)}{ret_marte} \\\\
  \\end{{tabular}}

  \\vfill

  {{\\small\\color{{grisai}}
  Generado el {datetime.now().strftime("%d/%m/%Y")}
  }}

\\end{{titlepage}}

\\justifying

\\tableofcontents

\\clearpage

% ── Datos de referencia ───────────────────────────────────────────────────────
\\section{{Datos de referencia}}

\\begin{{center}}
\\renewcommand{{\\arraystretch}}{{1.25}}
\\begin{{tabular}}{{llll}}
  \\toprule
  \\textbf{{Planeta}} & \\textbf{{Signo}} & \\textbf{{Casa}} & \\textbf{{Posición}} \\\\
  \\midrule
  Mercurio{ret_merc}  & {esc(merc.get('signo',''))}  & {merc.get('casa','')}  & {grado_a_dms(merc.get('grado',0))} \\\\
  Venus{ret_venus}    & {esc(venus.get('signo',''))} & {venus.get('casa','')} & {grado_a_dms(venus.get('grado',0))} \\\\
  Marte{ret_marte}    & {esc(marte.get('signo',''))} & {marte.get('casa','')} & {grado_a_dms(marte.get('grado',0))} \\\\
  Ascendente          & {esc(asc['signo'])}           & ---                    & {grado_a_dms(asc['grado'])} \\\\
  Medio Cielo         & {esc(mc['signo'])}            & ---                    & {grado_a_dms(mc['grado'])} \\\\
  \\bottomrule
\\end{{tabular}}
\\end{{center}}
\\justifying

\\vspace{{0.5cm}}

\\textbf{{Aspectos entre planetas personales:}}

{tabla_aspectos}

\\justifying

\\vspace{{0.7cm}}

\\begin{{center}}
\\includegraphics[width=0.72\\textwidth]{{{ruta_rueda}}}
\\end{{center}}

\\vspace{{0.3cm}}
\\Needspace{{5\\baselineskip}}

% ── Interpretación ────────────────────────────────────────────────────────────
\\section{{Interpretación — Arquitectura Interna}}

\\begin{{center}}
{{\\small\\itshape\\color{{grisai}}
No se trata de describir la personalidad.\\\\
Se trata de observar cómo procesas, cómo te vinculas\\\\
y cómo se mueve tu energía en la vida cotidiana.
}}
\\end{{center}}

\\justifying

\\vspace{{0.8cm}}

% ── 1. Funcionamiento general ─────────────────────────────────────────────────
\\subsection{{1. Funcionamiento general}}

\\justifying
{parrafos(t_gral)}

\\vspace{{0.8cm}}

% ── 2. Mercurio ───────────────────────────────────────────────────────────────
\\subsection{{2. Mercurio — Pensamiento y procesamiento}}

\\subsubsection*{{Mercurio en {esc(merc.get('signo',''))} — Casa {merc.get('casa','')}{ret_merc}}}

\\justifying
{parrafos(t_merc)}

\\vspace{{0.8cm}}

% ── 3. Venus ──────────────────────────────────────────────────────────────────
\\subsection{{3. Venus — Vínculo y regulación relacional}}

\\subsubsection*{{Venus en {esc(venus.get('signo',''))} — Casa {venus.get('casa','')}{ret_venus}}}

\\justifying
{parrafos(t_venus)}

\\vspace{{0.8cm}}

% ── 4. Marte ──────────────────────────────────────────────────────────────────
\\subsection{{4. Marte — Acción y descarga}}

\\subsubsection*{{Marte en {esc(marte.get('signo',''))} — Casa {marte.get('casa','')}{ret_marte}}}

\\justifying
{parrafos(t_marte)}

\\vspace{{0.8cm}}

% ── 5. Integración ────────────────────────────────────────────────────────────
\\subsection{{5. Integración — Coherencias, fricciones y bucles}}

\\justifying
{parrafos(t_integ)}

\\vspace{{0.8cm}}

% ── 6. Orientación práctica ───────────────────────────────────────────────────
\\subsection{{6. Orientación práctica}}

\\subsubsection*{{Desde dónde empezar}}

\\justifying
{parrafos(t_or['desde_donde'])}

\\subsubsection*{{Qué sostener}}

\\justifying
{parrafos(t_or['sostener'])}

\\subsubsection*{{Qué evitar}}

\\justifying
{parrafos(t_or['evitar'])}

\\vspace{{0.6cm}}

\\justifying
{parrafos(t_or['si_no'])}

\\vspace{{1.2cm}}

\\begin{{center}}
{{\\small\\itshape\\color{{grisai}}
La astrología se utiliza aquí como lenguaje simbólico de observación,\\\\
no como una definición cerrada de quién eres.\\\\[0.2cm]
Este documento propone una lectura funcional y orientativa, no un diagnóstico.
}}
\\end{{center}}

\\end{{document}}
"""

    return latex


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print("═" * 57)
    print("  MERCURIO · VENUS · MARTE — Arquitectura Interna")
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
        merc  = carta["planetas"].get("Mercurio", {})
        venus = carta["planetas"].get("Venus",    {})
        marte = carta["planetas"].get("Marte",    {})
        print(f"  ASC:      {asc['signo']} {grado_a_dms(asc['grado'])}")
        print(f"  Mercurio: {merc.get('signo','')} {grado_a_dms(merc.get('grado',0))} — Casa {merc.get('casa','')}")
        print(f"  Venus:    {venus.get('signo','')} {grado_a_dms(venus.get('grado',0))} — Casa {venus.get('casa','')}")
        print(f"  Marte:    {marte.get('signo','')} {grado_a_dms(marte.get('grado',0))} — Casa {marte.get('casa','')}")
    except Exception as e:
        print(f"Error en cálculo astrológico: {e}"); sys.exit(1)

    aspectos = calcular_aspectos_personales(carta["planetas"])
    print(f"  Aspectos personales: {len(aspectos)}")

    estelium = detectar_estelium_personales(carta["planetas"])
    if estelium:
        nombres_estelium = ", ".join([p["nombre"] for p in estelium])
        print(f"  Estelium personal detectado: {nombres_estelium}")
    else:
        print("  Estelium personal: no detectado")

    nombre_f  = nombre.replace(" ", "_").replace("/", "-")
    ruta_base = os.path.join(BASE_DIR, nombre_f + "_Planetas_Personales")
    ruta_tex  = ruta_base + ".tex"
    ruta_pdf  = ruta_base + ".pdf"

    ruta_rueda = ruta_base + "_rueda.png"

    print("  Generando rueda...")
    dibujar_rueda_planetas_personales(carta, ruta_rueda)

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
