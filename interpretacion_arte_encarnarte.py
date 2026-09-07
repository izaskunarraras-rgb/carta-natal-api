import os
import re
import json

from openai import OpenAI

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    PageBreak,
    KeepTogether,
    Table,
    TableStyle,
)

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors

from estilos_pdf import crear_estilos_pdf

import Figuras

from contexto_ia import (
    generar_contexto_arte_encarnarte,
    construir_contexto_compacto_arte_encarnarte,
)


# ─── BIBLIOTECA ASTROLÓGICA GENERAL · FILE SEARCH ───────────────────────────
# La biblioteca NO contiene reglas para una carta concreta.
# Python calcula la carta y las figuras. La API consulta la misma biblioteca
# general para profundizar únicamente en los factores presentes en cada carta.
BIBLIOTECA_ASTROLOGICA_FILE_SEARCH = True
BIBLIOTECA_ASTROLOGICA_CONFIG = "biblioteca_astrologica_config.json"
BIBLIOTECA_ASTROLOGICA_ENV = "ASTROLOGIA_VECTOR_STORE_ID"


def cargar_vector_store_biblioteca_astrologica():
    """
    Obtiene el Vector Store de la biblioteca general.

    Prioridad:
    1. variable de entorno ASTROLOGIA_VECTOR_STORE_ID (útil en Render);
    2. biblioteca_astrologica_config.json junto a este programa.

    El ID del Vector Store no es una clave secreta.
    """
    desde_entorno = str(
        os.getenv(BIBLIOTECA_ASTROLOGICA_ENV, "")
        or ""
    ).strip()

    if desde_entorno:
        return desde_entorno

    ruta = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        BIBLIOTECA_ASTROLOGICA_CONFIG,
    )

    if not os.path.exists(ruta):
        raise RuntimeError(
            "No encuentro biblioteca_astrologica_config.json y tampoco está "
            "configurada ASTROLOGIA_VECTOR_STORE_ID. "
            "La biblioteca astrológica general no puede consultarse."
        )

    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            config = json.load(archivo)
    except Exception as exc:
        raise RuntimeError(
            "No se ha podido leer biblioteca_astrologica_config.json."
        ) from exc

    vector_store_id = str(
        config.get("vector_store_id", "")
        or ""
    ).strip()

    if not vector_store_id:
        raise RuntimeError(
            "biblioteca_astrologica_config.json no contiene vector_store_id."
        )

    return vector_store_id


def herramienta_file_search_biblioteca_astrologica(
    vector_store_id,
    max_num_results=20,
):
    """Construye la herramienta File Search común para las dos llamadas normales."""
    return {
        "type": "file_search",
        "vector_store_ids": [vector_store_id],
        "max_num_results": int(max_num_results),
    }


def instrucciones_biblioteca_astrologica(
    modo,
):
    """
    Instrucciones universales para utilizar la biblioteca.

    La biblioteca amplía la profundidad interpretativa, pero nunca modifica
    la geometría ni los hechos calculados por Python.
    """
    base = """
BIBLIOTECA ASTROLÓGICA GENERAL · USO OBLIGATORIO

Tienes acceso mediante File Search a una biblioteca general de astrología.

Utilízala como FUENTE DE PROFUNDIDAD INTERPRETATIVA para la carta concreta
que Python ha calculado. No existe una biblioteca especial para esta persona:
la misma biblioteca debe servir para cualquier carta natal.

REGLA DE AUTORIDAD

1. Python manda sobre todos los hechos de esta carta:
   posiciones, casas, aspectos, orbes, retrogradaciones, figuras, vértices,
   roles geométricos, puntos permitidos y selección principal/rescate.
2. Los libros sirven para comprender mejor el significado de esos hechos.
3. Nunca cambies, completes ni corrijas una geometría basándote en un libro.
4. Si un fragmento recuperado no corresponde a los datos reales de la carta,
   no lo uses.
5. No atribuyas una idea a un autor en el informe final. Integra el
   conocimiento de forma natural y original; no hagas una reseña bibliográfica.

6. La existencia de la biblioteca es COMPLETAMENTE INTERNA.
   En el informe destinado a la persona NO menciones nunca:
   "biblioteca", "libros", "fuentes", "File Search", "búsqueda en archivos",
   "material recuperado", "texto recuperado", "documentos consultados",
   ni expresiones como "la biblioteca ayuda", "la biblioteca apoya",
   "según los libros" o equivalentes.
7. Tampoco nombres autores como justificación de una conclusión.
   Usa el conocimiento consultado, pero escribe la interpretación como una
   lectura directa de la carta.
8. No reproduzcas marcadores técnicos de citación o referencias internas
   como "filecite", "cite", "turn0file1", "turn0search1" ni equivalentes.
   Son metadatos internos y nunca forman parte del informe visible.

CRITERIO DE BÚSQUEDA

Busca únicamente conocimiento relacionado con los factores que aparecen
realmente en los datos que estás interpretando.

La recuperación puede apoyarse, según sea pertinente, en:
- Huber para forma global, figura de aspectos, geometría, motivación y
  funcionamiento de las figuras;
- Greene y Sasportas para profundidad psicológica de planetas y relaciones;
- Sasportas para casas y ámbitos de experiencia;
- Arroyo para elementos, signos, aspectos y flujo entre funciones;
- Carutti para Luna, Ascendente y procesos de identificación cuando
  correspondan a los datos;
- otros libros de la biblioteca cuando aporten un matiz útil.

No intentes "usar todos los autores". La relevancia para la carta manda.

SÍNTESIS, NO INVENTARIO

No escribas:
"Huber dice...", "Greene dice...", "Arroyo dice...".

No sumes definiciones independientes.

La biblioteca debe ayudarte a responder:
- qué relación humana está describiendo esta configuración;
- qué cambia por los signos concretos;
- dónde puede notarse por las casas concretas;
- cómo modifica el conjunto la forma de vivir cada relación.

No copies párrafos de los libros. Sintetiza.
""".strip()

    if modo == "global":
        extra = """
USO EN LA LECTURA GLOBAL

Consulta la biblioteca para enriquecer la lectura del conjunto, pero NO
desarrolles figuras individuales en esta llamada.

Usa el conocimiento recuperado para comprender mejor:
- repeticiones y núcleos;
- relaciones entre funciones planetarias que aparecen varias veces;
- casas y ejes con peso;
- significado de signos cuando ayuden a precisar un patrón global;
- diferencias entre tensión, facilidad, concentración y dirección.

No conviertas la lectura global en una enciclopedia de posiciones.
""".strip()
    else:
        extra = """
USO EN LAS FIGURAS

Para cada figura, la búsqueda debe partir de sus propios datos:
- nombre/tipo de figura;
- puntos permitidos;
- relaciones internas reales;
- signos;
- casas;
- retrogradaciones;
- roles geométricos;
- condición de principal, rescate o complementaria.

Profundiza en la RELACIÓN, no en cada planeta por separado.

En figuras principales, usa la biblioteca para desarrollar el mecanismo
completo con más profundidad.

En figuras de rescate, céntrate en lo que añaden las líneas nuevas.
No uses la biblioteca como excusa para volver a explicar todas las líneas
reutilizadas.

En un Stellium, interpreta el conjunto como unidad.

Si una relación interna tiene un peso claro en la geometría, busca material
que ayude a comprender esa relación concreta y después intégrala dentro de
la figura completa. No la conviertas en una sección independiente.
""".strip()

    return base + "\n\n" + extra

# ─── FIN BIBLIOTECA ASTROLÓGICA GENERAL ─────────────────────────────────────



# ─── FASE 15: AUDITORÍA GLOBAL DE EVIDENCIA E INFERENCIAS ───────────────────
HUBER_FASE15_AUDITORIA_GLOBAL = True


def _fase15_lista_segura(valor):
    if isinstance(valor, list):
        return valor
    if isinstance(valor, tuple):
        return list(valor)
    return []



def _rol_seleccion_huber_2026_figura(figura):
    """Lee el rol técnico Huber 2026 desde la figura o su paquete IA."""
    paquete = figura.get("paquete_huber_ia") or {}
    return (
        figura.get("seleccion_huber_2026")
        or paquete.get("seleccion_huber_2026")
        or ""
    )


def construir_contrato_evidencia_global_fase15(contexto_compacto):
    figuras_bloque = contexto_compacto.get("figuras", {})
    arquitectura = figuras_bloque.get("arquitectura", {})
    posiciones = figuras_bloque.get("posiciones_natales", {})
    aspectos = figuras_bloque.get("aspectos_relevantes", [])

    nucleos = []
    for nucleo in _fase15_lista_segura(arquitectura.get("nucleos", [])):
        puntos = [
            str(p).strip()
            for p in _fase15_lista_segura(nucleo.get("puntos_nucleo", []))
            if str(p).strip()
        ]
        if puntos:
            nucleos.append({
                "puntos": puntos,
                "peso": (
                    nucleo.get("peso")
                    or nucleo.get("puntuacion")
                    or nucleo.get("repeticion")
                ),
            })

    figuras = []
    for figura in _fase15_lista_segura(arquitectura.get("figuras", [])):
        figuras.append({
            "id_figura": figura.get("id_figura"),
            "tipo": figura.get("tipo"),
            "nombre_canonico": figura.get("nombre_canonico"),
            "titulo_salida": figura.get("titulo_salida"),
            "puntos": _fase15_lista_segura(figura.get("puntos", [])),
            "categoria": figura.get("categoria"),
            "consistencia": figura.get("consistencia"),
            "jerarquia": figura.get("jerarquia"),
            "puntuacion_jerarquia": figura.get("puntuacion_jerarquia"),
            "estado_estructural": figura.get("estado_estructural"),
            "nivel_composicion": figura.get("nivel_composicion"),
            "seleccion_huber_2026": _rol_seleccion_huber_2026_figura(figura),
            "fase_seleccion_huber_2026": (
                figura.get("fase_seleccion_huber_2026")
                or (figura.get("paquete_huber_ia") or {}).get("fase_seleccion_huber_2026")
            ),
        })

    puntos_organizadores = arquitectura.get("puntos_organizadores", [])

    if isinstance(puntos_organizadores, dict):
        puntos_organizadores = [
            {"punto": k, "datos": v}
            for k, v in puntos_organizadores.items()
        ]
    elif not isinstance(puntos_organizadores, list):
        puntos_organizadores = []

    posiciones_resumidas = {}
    for punto, datos in posiciones.items():
        if not isinstance(datos, dict):
            continue
        posiciones_resumidas[punto] = {
            "signo": datos.get("signo"),
            "casa": datos.get("casa"),
            "grado": datos.get("grado"),
            "retrogrado": datos.get("retrogrado"),
        }

    return {
        "version_contrato": "fase15-global-v1",
        "hechos_calculados": {
            "puntos_organizadores": puntos_organizadores,
            "nucleos": nucleos,
            "figuras": figuras,
            "posiciones_natales": posiciones_resumidas,
            "aspectos_relevantes": aspectos,
        },
        "jerarquia_evidencia": [
            {
                "nivel": 1,
                "nombre": "hecho_estructural",
                "permite": (
                    "Afirmar claramente lo calculado por Python: repetición, "
                    "figura, núcleo, posición, casa, eje, aspecto, consistencia "
                    "o jerarquía."
                ),
            },
            {
                "nivel": 2,
                "nombre": "traduccion_simbolica_directa",
                "permite": (
                    "Traducir el hecho estructural a un territorio simbólico "
                    "directamente asociado, manteniendo visible la evidencia."
                ),
            },
            {
                "nivel": 3,
                "nombre": "mecanismo_probable",
                "permite": (
                    "Proponer una tendencia funcional cuando confluyen varias "
                    "evidencias independientes. Debe redactarse como tendencia, "
                    "posibilidad o condición de funcionamiento."
                ),
            },
            {
                "nivel": 4,
                "nombre": "biografia_no_demostrada",
                "permite": (
                    "NO afirmar acontecimientos, profesión concreta, historia "
                    "familiar, tipo de relación, trauma, conducta real, éxito, "
                    "fracaso ni circunstancia vital específica."
                ),
            },
        ],
        "reglas_por_fuente": {
            "casas": {
                "permitido": "Localizar simbólicamente una dinámica en un ámbito.",
                "no_permitido": "Convertir la casa en un acontecimiento demostrado.",
            },
            "ejes": {
                "permitido": "Hablar de polaridad o coordinación entre dos ámbitos.",
                "no_permitido": (
                    "Afirmar que esa polaridad ya se manifiesta de una forma "
                    "biográfica concreta."
                ),
            },
            "medio_cielo": {
                "permitido": [
                    "visibilidad",
                    "proyección pública",
                    "orientación vocacional",
                    "trayectoria o forma de hacerse visible",
                ],
                "no_permitido": [
                    "profesión concreta",
                    "éxito profesional",
                    "estatus real",
                    "cambio laboral ocurrido",
                ],
            },
            "ascendente": {
                "permitido": [
                    "forma de presentarse",
                    "entrada en contacto",
                    "modo de hacerse visible",
                ],
                "no_permitido": [
                    "máscara",
                    "identidad falsa",
                    "conducta social demostrada",
                ],
            },
            "nodos": {
                "permitido": "Describirlos como polos de una dinámica estructural.",
                "no_permitido": "Presentarlos como una predicción biográfica cerrada o un resultado garantizado.",
            },
            "planetas_y_puntos": {
                "permitido": (
                    "Usar su simbolismo cuando ayuda a explicar una relación "
                    "estructural real. Si retrogrado=true, integrar la "
                    "retrogradación como matiz de interiorización, revisión "
                    "o reelaboración cuando el punto sea estructuralmente relevante."
                ),
                "no_permitido": (
                    "Convertir el simbolismo aislado en rasgo psicológico demostrado. "
                    "No convertir la retrogradación en bloqueo, trauma, karma, "
                    "retraso ni incapacidad."
                ),
            },
            "aspectos": {
                "permitido": "Describir la relación funcional que calculan.",
                "no_permitido": "Inventar la conducta concreta que habría producido.",
            },
        },
        "regla_de_confluencia": (
            "Cuanto más concreta sea una afirmación humana, más de una evidencia "
            "independiente debe sostenerla. Una sola casa o un solo símbolo no "
            "bastan para convertir una posibilidad en un rasgo personal."
        ),
        "regla_de_redaccion": (
            "La estructura puede afirmarse con claridad. La traducción a "
            "funcionamiento personal debe usar el grado de certeza adecuado. "
            "La biografía concreta no se inventa."
        ),
    }


def auditar_inferencias_globales_fase15(client, texto, contexto_compacto):
    if not texto:
        return texto

    contrato = construir_contrato_evidencia_global_fase15(contexto_compacto)

    prompt = f"""
AUDITORÍA FINAL DE EVIDENCIA · FASE 15

Revisa exclusivamente el INFORME GLOBAL incluido al final.

No hagas una nueva interpretación.
No mejores el estilo de forma general.
No resumas.
No amplíes.
No reorganices secciones.
No cambies encabezados Markdown.
No añadas información astrológica.

Comprueba siempre esta cadena:

DATO DETERMINISTA
→ EVIDENCIA
→ NIVEL DE INFERENCIA PERMITIDO
→ REDACCIÓN

CONTRATO DE EVIDENCIA:

{json.dumps(contrato, ensure_ascii=False, indent=2)}

REGLAS

1. Conserva como afirmación clara los hechos estructurales calculados.

2. Una casa, ángulo, planeta o punto puede localizar o matizar una dinámica,
pero no demuestra por sí solo una historia real.

Casa 4:
sí → base, intimidad, raíz, hogar como territorio simbólico.
no → conflicto familiar o infancia concreta.

Casa 7:
sí → vínculo, encuentro, negociación, relación con el otro.
no → pareja, ruptura, dependencia o relación real concreta.

Casa 10 / Medio Cielo:
sí → visibilidad, proyección pública, orientación vocacional, trayectoria.
no → profesión, éxito, estatus o hechos laborales concretos.

3. Cuando varias evidencias independientes convergen, puede mantenerse una
traducción funcional, pero como tendencia o posibilidad.

4. No atribuyas como hechos profesión, trayectoria laboral real, éxito,
fracaso, relaciones concretas, historia familiar, trauma, crisis vivida,
conducta habitual, acontecimientos, síntomas o decisiones reales.

5. Una vía de regulación puede presentarse como posibilidad funcional,
no como necesidad personal demostrada.

6. La síntesis puede describir la lógica de la arquitectura, pero no definir
de forma cerrada a la persona.

7. Corrige únicamente la frase o fragmento que exceda la evidencia.
Conserva todo lo demás literalmente siempre que sea posible.

Devuelve únicamente el informe completo corregido.

<INFORME_GLOBAL>
{texto}
</INFORME_GLOBAL>
"""

    response = client.responses.create(
        model="gpt-5.4-mini",
        input=prompt,
    )

    if not response.output_text:
        raise RuntimeError(
            "OpenAI no ha devuelto texto en la auditoría global Fase 15."
        )

    return response.output_text.strip()

# ─── FIN FASE 15 ──────────────────────────────────────────────────────────────



# ─── FASE 16: MATRIZ DE INFERENCIAS POR CONVERGENCIA ────────────────────────
HUBER_FASE16_MATRIZ_INFERENCIAS = True


def _fase16_nombre_figura(figura):
    paquete = figura.get("paquete_huber_ia") or {}
    return (
        paquete.get("nombre_huber")
        or figura.get("nombre_canonico")
        or figura.get("tipo")
        or ""
    ).strip()


def _fase16_puntos_organizadores_a_pesos(arquitectura):
    pesos = {}

    organizadores = arquitectura.get(
        "puntos_organizadores",
        [],
    )

    if isinstance(organizadores, dict):
        for punto, datos in organizadores.items():
            peso = 1
            if isinstance(datos, dict):
                peso = (
                    datos.get("repeticion")
                    or datos.get("peso")
                    or datos.get("puntuacion")
                    or 1
                )
            try:
                peso = float(peso)
            except (TypeError, ValueError):
                peso = 1
            pesos[str(punto)] = max(
                pesos.get(str(punto), 0),
                peso,
            )

    elif isinstance(organizadores, list):
        for elemento in organizadores:
            if isinstance(elemento, str):
                punto = elemento.strip()
                if punto:
                    pesos[punto] = max(
                        pesos.get(punto, 0),
                        1,
                    )
                continue

            if not isinstance(elemento, dict):
                continue

            punto = (
                elemento.get("punto")
                or elemento.get("nombre")
                or elemento.get("id")
            )

            if not punto:
                continue

            peso = (
                elemento.get("repeticion")
                or elemento.get("peso")
                or elemento.get("puntuacion")
                or elemento.get("valor")
                or 1
            )

            try:
                peso = float(peso)
            except (TypeError, ValueError):
                peso = 1

            pesos[str(punto)] = max(
                pesos.get(str(punto), 0),
                peso,
            )

    return pesos


def construir_matriz_inferencias_fase16(
    contexto_compacto,
):
    """
    Construye autorizaciones interpretativas a partir de
    convergencias reales de la carta.

    No interpreta biografía. Decide qué traducciones pueden
    utilizarse y con qué nivel de concreción.
    """
    figuras_bloque = contexto_compacto.get(
        "figuras",
        {},
    )

    arquitectura = figuras_bloque.get(
        "arquitectura",
        {},
    )

    figuras = arquitectura.get(
        "figuras",
        [],
    ) or []

    nucleos = arquitectura.get(
        "nucleos",
        [],
    ) or []

    posiciones = figuras_bloque.get(
        "posiciones_natales",
        {},
    ) or {}

    aspectos = figuras_bloque.get(
        "aspectos_relevantes",
        [],
    ) or []

    pesos_puntos = _fase16_puntos_organizadores_a_pesos(
        arquitectura
    )

    # Repetición en figuras.
    for figura in figuras:
        for punto in figura.get("puntos", []) or []:
            punto = str(punto)
            pesos_puntos[punto] = (
                pesos_puntos.get(punto, 0)
                + 1
            )

    # Repetición en núcleos.
    for nucleo in nucleos:
        for punto in nucleo.get(
            "puntos_nucleo",
            [],
        ) or []:
            punto = str(punto)
            pesos_puntos[punto] = (
                pesos_puntos.get(punto, 0)
                + 1
            )

    # Peso por casa de los puntos estructuralmente implicados.
    peso_casas = {}

    for punto, datos in posiciones.items():
        if not isinstance(datos, dict):
            continue

        casa = datos.get("casa")

        try:
            casa = int(casa)
        except (TypeError, ValueError):
            continue

        if casa < 1 or casa > 12:
            continue

        peso = max(
            1,
            pesos_puntos.get(str(punto), 0),
        )

        peso_casas[casa] = (
            peso_casas.get(casa, 0)
            + peso
        )

    def peso_punto(nombre):
        return float(
            pesos_puntos.get(nombre, 0)
            or 0
        )

    def peso_casa(numero):
        return float(
            peso_casas.get(numero, 0)
            or 0
        )

    def peso_eje(a, b):
        return (
            peso_casa(a)
            + peso_casa(b)
        )

    def comparte_figura(puntos):
        objetivo = set(puntos)

        for figura in figuras:
            presentes = set(
                str(p)
                for p in (
                    figura.get("puntos", [])
                    or []
                )
            )

            if objetivo.issubset(presentes):
                return True

        return False

    def existe_aspecto(p1, p2):
        objetivo = {
            str(p1),
            str(p2),
        }

        for aspecto in aspectos:
            presentes = {
                str(aspecto.get("p1")),
                str(aspecto.get("p2")),
            }

            if presentes == objetivo:
                return True

        return False

    nombres_figuras = [
        _fase16_nombre_figura(figura)
        .casefold()
        for figura in figuras
    ]

    def hay_figura_con(*fragmentos):
        for nombre in nombres_figuras:
            if any(
                frag.casefold() in nombre
                for frag in fragmentos
            ):
                return True
        return False

    inferencias = {}

    def registrar(
        clave,
        nivel,
        evidencias,
        permitido,
        prohibido,
    ):
        inferencias[clave] = {
            "nivel_autorizado": nivel,
            "evidencias": evidencias,
            "permitido": permitido,
            "prohibido": prohibido,
        }

    # 1. Comunicación / elaboración verbal.
    ev_comunicacion = []

    if peso_casa(3) > 0 or peso_eje(3, 9) >= 2:
        ev_comunicacion.append(
            "Casa 3 o eje 3–9 con peso estructural"
        )

    if peso_punto("Mercurio") >= 2:
        ev_comunicacion.append(
            "Mercurio repetido estructuralmente"
        )

    soporte_figura_comunicacion = hay_figura_con(
        "detect",
        "model",
        "represent",
        "bijou",
        "megáfono",
        "telescopio",
        "aprendizaje",
        "información",
        "ojo",
    )

    if soporte_figura_comunicacion:
        ev_comunicacion.append(
            "Figura compatible con elaboración, información o aprendizaje"
        )

    if (
        len(ev_comunicacion) >= 3
        and peso_punto("Mercurio") >= 2
    ):
        registrar(
            "elaboracion_por_palabra_y_orden",
            "recurso_regulacion",
            ev_comunicacion,
            [
                "nombrar",
                "ordenar",
                "comparar",
                "verbalizar",
                "escribir como posible vía de elaboración",
            ],
            [
                "afirmar que escribir sea necesario",
                "atribuir profesión comunicativa",
                "afirmar que la persona siempre procesa hablando",
            ],
        )

    elif len(ev_comunicacion) >= 1:
        registrar(
            "territorio_comunicacion_aprendizaje",
            "territorio_simbolico",
            ev_comunicacion,
            [
                "comunicación",
                "aprendizaje",
                "intercambio de información",
                "ampliación de perspectiva",
            ],
            [
                "afirmar una conducta comunicativa real",
                "recomendar escritura o verbalización como recurso personal",
            ],
        )

    # 2. Sensibilidad + discernimiento.
    ev_discernimiento = []

    if (
        peso_punto("Neptuno") >= 2
        or peso_punto("Quirón") >= 2
    ):
        ev_discernimiento.append(
            "Neptuno y/o Quirón repetidos estructuralmente"
        )

    if (
        peso_punto("Mercurio") >= 2
        or peso_punto("Saturno") >= 2
    ):
        ev_discernimiento.append(
            "Mercurio y/o Saturno aportan contraste, forma o discriminación"
        )

    if (
        comparte_figura(["Neptuno", "Mercurio"])
        or comparte_figura(["Neptuno", "Saturno"])
        or comparte_figura(["Quirón", "Mercurio"])
        or comparte_figura(["Quirón", "Saturno"])
        or existe_aspecto("Neptuno", "Mercurio")
        or existe_aspecto("Neptuno", "Saturno")
        or existe_aspecto("Quirón", "Mercurio")
        or existe_aspecto("Quirón", "Saturno")
    ):
        ev_discernimiento.append(
            "Relación estructural directa entre sensibilidad y discriminación"
        )

    if len(ev_discernimiento) >= 2:
        registrar(
            "sensibilidad_y_discernimiento",
            "mecanismo_probable",
            ev_discernimiento,
            [
                "distinguir impresión de información",
                "filtrar",
                "dar forma a lo percibido",
                "contrastar intuición con datos",
            ],
            [
                "hipersensibilidad como hecho",
                "intuición infalible",
                "confusión permanente",
            ],
        )

    # 3. Ritmo activación-pausa.
    ev_ritmo = []

    if (
        peso_punto("Marte") >= 2
        or peso_punto("Urano") >= 2
    ):
        ev_ritmo.append(
            "Marte y/o Urano repetidos estructuralmente"
        )

    if hay_figura_con(
        "t-cuadrada",
        "rendimiento",
        "provocat",
        "arena",
        "corredor",
        "amortiguador",
        "trampolín",
        "surfista",
        "ambivalencia",
    ):
        ev_ritmo.append(
            "Figuras compatibles con presión, reacción, oscilación o reajuste"
        )

    if (
        comparte_figura(["Marte", "Urano"])
        or existe_aspecto("Marte", "Urano")
    ):
        ev_ritmo.append(
            "Relación estructural Marte–Urano"
        )

    if len(ev_ritmo) >= 2:
        registrar(
            "ritmo_activacion_pausa",
            "recurso_regulacion",
            ev_ritmo,
            [
                "alternar activación y pausa",
                "distinguir urgencia de activación",
                "modular velocidad de respuesta",
                "introducir tiempo de elaboración antes de actuar",
            ],
            [
                "afirmar impulsividad como rasgo",
                "afirmar hiperactividad",
                "prescribir descanso como obligación",
            ],
        )

    # 4. Vínculo / negociación.
    ev_vinculo = []

    if peso_eje(1, 7) >= 2:
        ev_vinculo.append(
            "Eje 1–7 con peso estructural"
        )

    if (
        peso_punto("Ascendente") >= 2
        or peso_punto("Venus") >= 2
    ):
        ev_vinculo.append(
            "Ascendente y/o Venus repetidos estructuralmente"
        )

    if hay_figura_con(
        "arena",
        "bijou",
        "ambivalencia",
        "escenario",
    ):
        ev_vinculo.append(
            "Figura compatible con polaridad, mediación o negociación"
        )

    if len(ev_vinculo) >= 2:
        registrar(
            "vinculo_y_negociacion",
            "mecanismo_probable",
            ev_vinculo,
            [
                "coordinación entre presencia propia y encuentro",
                "negociación",
                "mediación",
                "polaridad entre autonomía y vínculo",
            ],
            [
                "afirmar tipo de pareja",
                "afirmar dependencia o ruptura",
                "describir relaciones reales de la persona",
            ],
        )

    elif peso_eje(1, 7) >= 1:
        registrar(
            "territorio_vincular",
            "territorio_simbolico",
            ev_vinculo or [
                "Eje 1–7 activado"
            ],
            [
                "vínculo",
                "encuentro",
                "presentación y relación con el otro como territorios",
            ],
            [
                "inferir conducta relacional concreta",
                "afirmar autonomía o dependencia como rasgos",
            ],
        )

    # 5. Base interna y proyección / recogimiento.
    ev_base_proyeccion = []

    if peso_eje(4, 10) >= 2:
        ev_base_proyeccion.append(
            "Eje 4–10 con peso estructural"
        )

    if (
        peso_punto("Medio Cielo") >= 2
        or peso_casa(10) >= 2
    ):
        ev_base_proyeccion.append(
            "Medio Cielo o Casa 10 con repetición estructural"
        )

    if (
        peso_casa(4) >= 1
        and (
            peso_punto("Luna") >= 2
            or peso_punto("Neptuno") >= 2
            or peso_punto("Saturno") >= 2
        )
    ):
        ev_base_proyeccion.append(
            "Casa 4 activada junto a un punto relevante de base, sensibilidad o contención"
        )

    if len(ev_base_proyeccion) >= 3:
        registrar(
            "alternancia_exposicion_recogimiento",
            "recurso_regulacion",
            ev_base_proyeccion,
            [
                "alternar exposición y recogimiento",
                "preservar una base interna antes de aumentar visibilidad",
                "introducir tiempos de recuperación tras alta exposición",
            ],
            [
                "afirmar necesidad de aislamiento",
                "afirmar vida privada concreta",
                "prescribir retiro como obligación",
            ],
        )

    elif len(ev_base_proyeccion) >= 1:
        registrar(
            "base_y_proyeccion",
            "territorio_simbolico",
            ev_base_proyeccion,
            [
                "base interna",
                "intimidad",
                "visibilidad",
                "proyección pública",
            ],
            [
                "afirmar acontecimientos familiares",
                "afirmar profesión o éxito público",
                "recomendar retiro sin evidencia adicional",
            ],
        )

    # 6. Expansión y medida.
    ev_expansion = []

    if peso_punto("Júpiter") >= 2:
        ev_expansion.append(
            "Júpiter repetido estructuralmente"
        )

    if (
        peso_punto("Saturno") >= 2
        or comparte_figura(["Júpiter", "Saturno"])
        or existe_aspecto("Júpiter", "Saturno")
    ):
        ev_expansion.append(
            "Saturno o relación Júpiter–Saturno aporta medida"
        )

    if hay_figura_con(
        "aprendizaje",
        "ambivalencia",
        "t-cuadrada",
        "rendimiento",
    ):
        ev_expansion.append(
            "Figuras compatibles con contraste, medida o reajuste"
        )

    if len(ev_expansion) >= 2:
        registrar(
            "expansion_y_medida",
            "mecanismo_probable",
            ev_expansion,
            [
                "calibrar amplitud",
                "traducir expansión en pasos concretos",
                "distinguir crecimiento de sobreextensión",
            ],
            [
                "afirmar exceso real",
                "afirmar ambición",
                "prescribir contención moral",
            ],
        )

    # 7. Creatividad / circulación.
    ev_creatividad = []

    if peso_eje(5, 11) >= 2:
        ev_creatividad.append(
            "Eje 5–11 con peso estructural"
        )

    if (
        peso_punto("Sol") >= 2
        or peso_punto("Venus") >= 2
        or peso_punto("Mercurio") >= 2
    ):
        ev_creatividad.append(
            "Sol, Venus y/o Mercurio repetidos estructuralmente"
        )

    if hay_figura_con(
        "talento",
        "cometa",
        "model",
        "represent",
        "bijou",
    ):
        ev_creatividad.append(
            "Figura compatible con talento, forma o representación"
        )

    if len(ev_creatividad) >= 3:
        registrar(
            "creatividad_y_circulacion",
            "mecanismo_probable",
            ev_creatividad,
            [
                "expresión creativa",
                "dar forma a una idea",
                "hacer circular o compartir una producción",
            ],
            [
                "afirmar talento artístico",
                "afirmar proyectos reales",
                "afirmar reconocimiento social",
            ],
        )

    elif peso_eje(5, 11) >= 1:
        registrar(
            "territorio_creatividad_comunidad",
            "territorio_simbolico",
            ev_creatividad or [
                "Eje 5–11 activado"
            ],
            [
                "expresión personal",
                "creatividad",
                "participación en redes o grupos como territorios",
            ],
            [
                "afirmar que la persona crea, lidera o participa realmente",
                "afirmar proyectos o comunidad concretos",
            ],
        )

    # 8. Recursos / valor / transformación.
    ev_recursos = []

    if peso_eje(2, 8) >= 2:
        ev_recursos.append(
            "Eje 2–8 con peso estructural"
        )

    if (
        peso_punto("Plutón") >= 2
        or peso_punto("Venus") >= 2
    ):
        ev_recursos.append(
            "Plutón y/o Venus repetidos estructuralmente"
        )

    if len(ev_recursos) >= 2:
        registrar(
            "valor_recursos_transformacion",
            "mecanismo_probable",
            ev_recursos,
            [
                "relación entre valor, recursos y transformación",
                "revisión de criterios de sostén",
            ],
            [
                "afirmar pérdidas",
                "afirmar crisis económicas",
                "afirmar dependencia financiera",
            ],
        )

    elif peso_eje(2, 8) >= 1:
        registrar(
            "territorio_recursos_transformacion",
            "territorio_simbolico",
            ev_recursos or [
                "Eje 2–8 activado"
            ],
            [
                "valor",
                "recursos",
                "sostén",
                "transformación como territorios",
            ],
            [
                "afirmar circunstancias económicas reales",
                "afirmar crisis o pérdidas",
            ],
        )

    return {
        "version": "fase16-matriz-v1",
        "pesos": {
            "puntos": pesos_puntos,
            "casas": peso_casas,
            "ejes": {
                "1-7": peso_eje(1, 7),
                "2-8": peso_eje(2, 8),
                "3-9": peso_eje(3, 9),
                "4-10": peso_eje(4, 10),
                "5-11": peso_eje(5, 11),
                "6-12": peso_eje(6, 12),
            },
        },
        "inferencias_autorizadas": inferencias,
        "regla_global": (
            "No utilizar una inferencia concreta que no aparezca en "
            "inferencias_autorizadas. Si solo existe nivel "
            "territorio_simbolico, hablar del ámbito, no de conducta "
            "ni de recomendación personal."
        ),
    }


def auditar_matriz_inferencias_fase16(
    client,
    texto,
    contexto_compacto,
):
    if not texto:
        return texto

    matriz = construir_matriz_inferencias_fase16(
        contexto_compacto
    )

    prompt = f"""
AUDITORÍA DE CONVERGENCIA · FASE 16

Revisa exclusivamente el texto GLOBAL que aparece al final.

No hagas una nueva interpretación.
No resumas.
No amplíes.
No cambies encabezados.
No cambies nombres técnicos.
No añadas información astrológica.

MATRIZ DETERMINISTA DE INFERENCIAS AUTORIZADAS:

{json.dumps(
    matriz,
    ensure_ascii=False,
    indent=2,
)}

REGLA CENTRAL

No basta con cambiar un verbo categórico por "puede".
Una inferencia concreta solo puede mantenerse si su contenido
está autorizado por la matriz.

Si una entrada tiene nivel "territorio_simbolico":
- puedes hablar del ámbito;
- NO puedes convertirlo en conducta real;
- NO puedes convertirlo en recurso práctico personal.

Si tiene nivel "mecanismo_probable":
- puedes describir el mecanismo como tendencia o posibilidad;
- NO puedes convertirlo en biografía demostrada.

Si tiene nivel "recurso_regulacion":
- puedes proponer únicamente los recursos expresamente incluidos
  en "permitido";
- siempre como posibilidad funcional, no como obligación.

EJEMPLOS

Si la matriz solo autoriza "comunicación" como territorio:
SÍ: "el eje 3–9 concentra peso en comunicación y aprendizaje".
NO: "ordenar por escrito te ayuda a regularte".

Si la matriz autoriza "elaboracion_por_palabra_y_orden":
SÍ: "nombrar, ordenar o escribir puede servir como vía de elaboración".
NO: "necesitas escribir".

Si la matriz no autoriza "alternancia_exposicion_recogimiento":
elimina recomendaciones de retiro, aislamiento, intimidad o recuperación
como recurso específico, aunque Casa 4 o Casa 10 aparezcan activadas.

Si la matriz no autoriza una inferencia, conserva la evidencia estructural
y reformula a un nivel más básico.

Corrige únicamente las frases que excedan la matriz.
Conserva literalmente todo lo demás siempre que sea posible.

Devuelve únicamente el informe global completo corregido.

<INFORME_GLOBAL>
{texto}
</INFORME_GLOBAL>
"""

    response = client.responses.create(
        model="gpt-5.4-mini",
        input=prompt,
    )

    if not response.output_text:
        raise RuntimeError(
            "OpenAI no ha devuelto texto en la auditoría Fase 16."
        )

    return response.output_text.strip()

# ─── FIN FASE 16 ──────────────────────────────────────────────────────────────



# ─── MODO MANUAL CHATGPT ─────────────────────────────────────────────────────
MODO_IA_MANUAL = False


# ─── TRATAMIENTO LINGÜÍSTICO DEL INFORME ─────────────────────────────────────
# Valores admitidos:
# - "femenino"  -> terminaciones femeninas cuando corresponda;
# - "masculino" -> terminaciones masculinas cuando corresponda;
# - "neutro"    -> lenguaje neutro con terminación -e cuando corresponda.
#
# Esta variable puede sustituirse más adelante por el valor recibido desde Wix.
TRATAMIENTO_LINGUISTICO = "neutro"


def normalizar_tratamiento_linguistico(valor):
    valor = str(valor or "").strip().casefold()
    if valor not in {"femenino", "masculino", "neutro"}:
        return "neutro"
    return valor



def elegir_tratamiento_linguistico():
    """
    Pregunta al introducir los datos cómo quiere recibir el informe.

    Acepta:
    1 / femenino / f
    2 / masculino / m
    3 / neutro / n
    """
    opciones = {
        "1": "femenino",
        "f": "femenino",
        "femenino": "femenino",
        "2": "masculino",
        "m": "masculino",
        "masculino": "masculino",
        "3": "neutro",
        "n": "neutro",
        "neutro": "neutro",
    }

    print()
    print("Tratamiento lingüístico del informe:")
    print("  1. Femenino")
    print("  2. Masculino")
    print("  3. Neutro (-e)")
    print()

    while True:
        respuesta = input(
            "Elige 1, 2 o 3: "
        ).strip().casefold()

        tratamiento = opciones.get(respuesta)

        if tratamiento:
            print(
                "Tratamiento seleccionado:",
                tratamiento
            )
            print()
            return tratamiento

        print(
            "Opción no válida. Escribe 1, 2 o 3."
        )


def instruccion_tratamiento_linguistico(valor=None):
    """
    Instrucción de tratamiento para la IA.

    V39:
    Python no modifica después el género del texto.
    Por tanto, la IA debe resolver correctamente:
    - el tratamiento de la persona lectora;
    - la concordancia gramatical normal del resto de sustantivos.
    """
    tratamiento = normalizar_tratamiento_linguistico(
        TRATAMIENTO_LINGUISTICO if valor is None else valor
    )

    regla_comun = """
REGLA GRAMATICAL CRÍTICA

El tratamiento elegido se aplica ÚNICAMENTE a palabras que se refieren
DIRECTAMENTE a la persona que lee.

NO cambies el género gramatical normal de sustantivos, pronombres,
adjetivos o participios que se refieran a otras cosas.

La concordancia gramatical ordinaria del español debe conservarse siempre.

Ejemplos que deben mantenerse aunque el tratamiento de la persona sea neutro:

"esa energía aparece muy concentrada"
"una respuesta muy concentrada"
"la figura está integrada"
"una dinámica intensa"
"una postura cerrada"
"la carta está organizada"
"la relación queda definida"

En esos ejemplos, "concentrada", "integrada", "intensa", "cerrada",
"organizada" y "definida" concuerdan con sustantivos femeninos.
NO se refieren a quien lee y NUNCA deben convertirse en -e.

Antes de usar una terminación de tratamiento, identifica el referente:
¿el adjetivo o participio describe a la persona lectora o describe
a un sustantivo de la frase?

Solo si describe directamente a la persona lectora se aplica
el tratamiento elegido.

No neutralices palabras por proximidad a "tu", "te", "ti" o "tú".
La concordancia depende del referente gramatical real.

Python NO corregirá después estas terminaciones.
La redacción que devuelvas debe salir ya gramaticalmente correcta.
""".strip()

    if tratamiento == "femenino":
        especifica = """
TRATAMIENTO ELEGIDO: FEMENINO

Cuando un adjetivo, participio o forma con género se refiera
DIRECTAMENTE a quien lee, utiliza femenino.

Ejemplos:
"puedes sentirte segura"
"puedes estar convencida"
"puedes quedar expuesta"
"puedes sentirte preparada"

Pero conserva la concordancia propia de otros sustantivos:
"esa energía está concentrada"
"el impulso está concentrado"
"la respuesta está preparada"
""".strip()

    elif tratamiento == "masculino":
        especifica = """
TRATAMIENTO ELEGIDO: MASCULINO

Cuando un adjetivo, participio o forma con género se refiera
DIRECTAMENTE a quien lee, utiliza masculino.

Ejemplos:
"puedes sentirte seguro"
"puedes estar convencido"
"puedes quedar expuesto"
"puedes sentirte preparado"

Pero conserva la concordancia propia de otros sustantivos:
"esa energía está concentrada"
"el impulso está concentrado"
"la respuesta está preparada"
""".strip()

    else:
        especifica = """
TRATAMIENTO ELEGIDO: NEUTRO (-e)

Cuando un adjetivo, participio o forma con género se refiera
DIRECTAMENTE a quien lee, utiliza terminación -e cuando corresponda.

Ejemplos:
"puedes sentirte segure"
"puedes estar convencide"
"puedes quedar expueste"
"puedes sentirte preparade"
"puedes quedarte atrapade"

La terminación -e se aplica SOLO al referente humano directo.

NO la apliques a sustantivos gramaticales ni a conceptos de la carta.

CORRECTO:
"esa energía aparece muy concentrada"
"una sola respuesta muy concentrada"
"la figura queda integrada"
"la dinámica está orientada hacia..."
"la carta está organizada alrededor de..."
"una parte puede quedar bloqueada"
"el impulso puede quedar bloqueado"

INCORRECTO:
"esa energía aparece muy concentrade"
"una respuesta muy concentrade"
"la figura queda integrade"
"la dinámica está orientade"
"la carta está organizade"

No uses x, @, barras ni fórmulas como "seguro/a".
En neutro, usa -e solo cuando el referente sea quien lee.
""".strip()

    return regla_comun + "\n\n" + especifica


def adaptar_tratamiento_linguistico_local(texto, valor=None):
    """
    V39 · COMPATIBILIDAD.

    Python NO modifica género, concordancia ni terminaciones -a/-o/-e.

    El tratamiento lingüístico se resuelve completamente en la IA,
    porque una sustitución por expresiones regulares no puede distinguir
    con seguridad si un adjetivo se refiere a la persona lectora o a un
    sustantivo como "energía", "respuesta", "figura", "carta", etc.

    Esta función se conserva únicamente para no romper llamadas antiguas.
    """
    return texto


# ─── FIN TRATAMIENTO LINGÜÍSTICO ─────────────────────────────────────────────


def exportar_paquete_manual_chatgpt(
    nombre,
    fecha,
    hora,
    lugar,
    nombre_f,
    contexto_compacto,
):
    figuras = (
        contexto_compacto
        .get("figuras", {})
        .get("arquitectura", {})
        .get("figuras", [])
    )

    contratos_f17 = []

    for figura in figuras:
        try:
            contrato = (
                _fase17_contrato_inferencia_figura(
                    figura
                )
            )
        except Exception:
            contrato = {}

        contratos_f17.append({
            "id_estructural": figura.get(
                "id_estructural"
            ),
            "tipo": figura.get("tipo"),
            "titulo_salida": figura.get(
                "titulo_salida"
            ),
            "puntos": figura.get(
                "puntos",
                []
            ),
            "paquete_huber_ia": figura.get(
                "paquete_huber_ia"
            ),
            "contrato_inferencia_fase17": (
                contrato
            ),
        })

    try:
        contrato_f15 = (
            construir_contrato_evidencia_global_fase15(
                contexto_compacto
            )
        )
    except Exception:
        contrato_f15 = {}

    try:
        matriz_f16 = (
            construir_matriz_inferencias_fase16(
                contexto_compacto
            )
        )
    except Exception:
        matriz_f16 = {}

    paquete = {
        "version": "arte-encarnarte-manual-v1",
        "modo": "manual_chatgpt",
        "persona": {
            "nombre": nombre,
            "fecha": fecha,
            "hora": hora,
            "lugar": lugar,
        },
        "archivo_respuesta_esperado": (
            f"{nombre_f}_arte_encarnarte_manual.txt"
        ),
        "reglas_clave": [
            "Fidelidad absoluta a geometría y datos calculados.",
            "No inventar biografía, conducta, trauma, profesión ni eventos.",
            "Una figura describe dinámica estructural, no hechos personales.",
            "No basta añadir 'puede' a una conducta no demostrada.",
            "Casas y ejes localizan territorios; no prueban conductas.",
            "Aplicar recursos prácticos solo cuando Fase 16 los autorice.",
            "Conservar especificidad Huber de cada figura.",
            "Segunda persona, español de España y tratamiento lingüístico configurado.",
        ],
        "prompt_global_del_programa": (
            construir_prompt_arte_encarnarte(
                contexto_compacto
            )
        ),
        "contrato_evidencia_fase15": (
            contrato_f15
        ),
        "matriz_inferencias_fase16": (
            matriz_f16
        ),
        "figuras_con_contrato_fase17": (
            contratos_f17
        ),
        "jerarquia_editorial_fase18": construir_resumen_editorial_fase18(contexto_compacto),
        "contexto_compacto": contexto_compacto,
    }

    ruta = (
        f"{nombre_f}_PAQUETE_MANUAL_CHATGPT.json"
    )

    with open(
        ruta,
        "w",
        encoding="utf-8",
    ) as archivo:
        json.dump(
            paquete,
            archivo,
            ensure_ascii=False,
            indent=2,
        )

    return ruta


# MODO_MANUAL_NORMALIZACION_ROBUSTA_V3
def normalizar_formato_manual_chatgpt(texto, contexto_compacto):
    if not texto:
        return texto

    texto = texto.lstrip(chr(65279))

    secciones = [
        "La arquitectura central de tu carta",
        "Los núcleos que organizan tu carta",
        "Cómo se relacionan las distintas partes",
        "Tensiones estructurales",
        "Recursos y vías de integración",
        "Dónde se expresa esta arquitectura",
        "Cómo sostener esta arquitectura",
        "Tu manera particular de funcionar",
    ]

    mapa_secciones = {
        normalizar_titulo_seccion(titulo): titulo
        for titulo in secciones
    }

    try:
        titulos_figuras = obtener_titulos_figuras_esperadas(contexto_compacto)
    except Exception:
        titulos_figuras = []

    mapa_figuras = {
        re.sub(r"\s+", " ", titulo.strip()).casefold(): titulo
        for titulo in titulos_figuras
        if titulo and titulo.strip()
    }

    salida = []

    for linea in texto.splitlines():
        limpia = linea.strip()

        candidato = re.sub(r"^#{1,6}\s*", "", limpia).strip()
        clave = normalizar_titulo_seccion(candidato)

        if clave in mapa_secciones:
            salida.append("## " + mapa_secciones[clave])
            continue

        candidato_figura = limpia
        if (
            candidato_figura.startswith("**")
            and candidato_figura.endswith("**")
            and len(candidato_figura) >= 4
        ):
            candidato_figura = candidato_figura[2:-2].strip()

        clave_figura = re.sub(
            r"\s+", " ", candidato_figura
        ).casefold()

        if clave_figura in mapa_figuras:
            salida.append("**" + mapa_figuras[clave_figura] + "**")
            continue

        salida.append(linea)

    return "\n".join(salida)


def cargar_interpretacion_manual_chatgpt(
    nombre_f,
):
    ruta = (
        f"{nombre_f}_arte_encarnarte_manual.txt"
    )

    if not os.path.exists(ruta):
        return None, ruta

    with open(
        ruta,
        "r",
        encoding="utf-8",
    ) as archivo:
        texto = archivo.read().strip()

    if not texto:
        raise RuntimeError(
            f"El archivo manual está vacío: {ruta}"
        )

    return texto, ruta

# ─── FIN MODO MANUAL CHATGPT ─────────────────────────────────────────────────



def construir_resumen_retrogradacion_global(contexto_compacto):
    """
    Resume de forma determinista la retrogradación natal relevante.
    No interpreta biografía y no modifica la jerarquía de la carta.
    """
    figuras_bloque = contexto_compacto.get("figuras", {}) or {}
    posiciones = figuras_bloque.get("posiciones_natales", {}) or {}
    arquitectura = figuras_bloque.get("arquitectura", {}) or {}

    retrogrados = [
        nombre
        for nombre, datos in posiciones.items()
        if isinstance(datos, dict) and datos.get("retrogrado")
    ]

    if not retrogrados:
        return {
            "planetas_retrogrados": [],
            "organizadores_retrogrados": [],
            "participacion_en_figuras": {},
        }

    organizadores = set()
    for item in arquitectura.get("puntos_organizadores", []) or []:
        if isinstance(item, dict) and item.get("punto"):
            organizadores.add(str(item.get("punto")))

    participacion = {}
    for figura in arquitectura.get("figuras", []) or []:
        for punto in figura.get("puntos", []) or []:
            if punto in retrogrados:
                participacion[punto] = participacion.get(punto, 0) + 1

    return {
        "planetas_retrogrados": retrogrados,
        "organizadores_retrogrados": [
            p for p in retrogrados if p in organizadores
        ],
        "participacion_en_figuras": participacion,
    }


def asegurar_retrogradacion_en_global(texto, contexto_compacto):
    """
    Garantiza que una carta con planetas retrógrados relevantes no pierda
    ese matiz en la lectura global. Inserta un único párrafo en la primera
    sección solo si la IA no ha mencionado ya la retrogradación.
    """
    if not texto:
        return texto

    resumen = construir_resumen_retrogradacion_global(contexto_compacto)
    retrogrados = resumen.get("planetas_retrogrados", [])

    if not retrogrados:
        return texto

    # Si el informe global ya la integra, no duplicamos.
    if re.search(r"\bretr[oó]grad", texto, flags=re.IGNORECASE):
        return texto

    nombres = ", ".join(retrogrados[:-1])
    if len(retrogrados) == 1:
        lista = retrogrados[0]
    elif len(retrogrados) == 2:
        lista = " y ".join(retrogrados)
    else:
        lista = nombres + " y " + retrogrados[-1]

    organizadores = resumen.get("organizadores_retrogrados", [])
    participacion = resumen.get("participacion_en_figuras", {})

    relevantes = sorted(
        retrogrados,
        key=lambda p: (
            p not in organizadores,
            -participacion.get(p, 0),
            p,
        ),
    )

    foco = ", ".join(relevantes[:4])

    parrafo = (
        f"En esta carta están retrógrados {lista}. "
        "La retrogradación no cambia las figuras ni convierte estos puntos "
        "en más dominantes, pero sí matiza cómo se expresan cuando ya tienen "
        "peso estructural: introduce una tendencia a interiorizar, revisar o "
        "reelaborar su función antes de exteriorizarla. "
        f"Este matiz resulta especialmente relevante en {foco}, por su "
        "participación en la arquitectura descrita."
    )

    encabezado = "## Los núcleos que organizan tu carta"
    pos = texto.find(encabezado)

    if pos == -1:
        return texto + "\n\n" + parrafo

    izquierda = texto[:pos].rstrip()
    derecha = texto[pos:].lstrip()

    return izquierda + "\n\n" + parrafo + "\n\n" + derecha


def construir_prompt_arte_encarnarte(
    contexto_arte_encarnarte,
    guia_estilo="",
):
    contexto_json = json.dumps(
        contexto_arte_encarnarte,
        ensure_ascii=False,
        indent=2,
    )

    resumen_retrogradacion_global = construir_resumen_retrogradacion_global(
        contexto_arte_encarnarte
    )

    resumen_retrogradacion_global_json = json.dumps(
        resumen_retrogradacion_global,
        ensure_ascii=False,
        indent=2,
    )

    contrato_evidencia_global_fase15 = (
        construir_contrato_evidencia_global_fase15(
            contexto_arte_encarnarte
        )
    )

    contrato_evidencia_global_fase15_json = json.dumps(
        contrato_evidencia_global_fase15,
        ensure_ascii=False,
        indent=2,
    )

    matriz_inferencias_fase16 = (
        construir_matriz_inferencias_fase16(
            contexto_arte_encarnarte
        )
    )

    matriz_inferencias_fase16_json = json.dumps(
        matriz_inferencias_fase16,
        ensure_ascii=False,
        indent=2,
    )

    nucleos = (
        contexto_arte_encarnarte
        .get("figuras", {})
        .get("arquitectura", {})
        .get("nucleos", [])
    )

    lineas_nucleos = []

    for nucleo in nucleos:

        puntos = nucleo.get(
            "puntos_nucleo",
            []
        )

        if puntos:
            lineas_nucleos.append(
                " · ".join(puntos)
            )

    nucleos_autorizados = (
        "\n".join(lineas_nucleos)
        if lineas_nucleos
        else "No se han detectado núcleos."
    )

    figuras_detectadas = (
        contexto_arte_encarnarte
        .get("figuras", {})
        .get("arquitectura", {})
        .get("figuras", [])
    )

    lineas_figuras = []

    for figura in figuras_detectadas:

        tipo = figura.get(
            "tipo",
            ""
        )

        puntos = figura.get(
            "puntos",
            []
        )

        titulo_salida = figura.get(
            "titulo_salida",
            ""
        ).strip()

        categoria = figura.get(
            "categoria",
            ""
        )

        consistencia = figura.get(
            "consistencia",
            ""
        )

        jerarquia = figura.get(
            "jerarquia",
            ""
        )

        if tipo and puntos:

            detalles = []

            if categoria:
                detalles.append(
                    f"categoría: {categoria}"
                )

            if consistencia:
                detalles.append(
                    f"consistencia: {consistencia}"
                )

            if jerarquia:
                detalles.append(
                    f"jerarquía: {jerarquia}"
                )

            sufijo = (
                " ["
                + ", ".join(detalles)
                + "]"
                if detalles
                else ""
            )

            lineas_figuras.append(
                titulo_salida
                + sufijo
            )

    figuras_autorizadas = (
        "\n".join(lineas_figuras)
        if lineas_figuras
        else "No se han detectado figuras."
    )

    nucleos_estructurados_globales = construir_esquema_nucleos_global(
        contexto_arte_encarnarte
    )

    nucleos_estructurados_globales_json = json.dumps(
        nucleos_estructurados_globales,
        ensure_ascii=False,
        indent=2,
    )

    return f"""
GUÍA DE ESTILO OBLIGATORIA
────────────────────────────────────────────

{guia_estilo}

FIN DE LA GUÍA DE ESTILO
────────────────────────────────────────────


Eres la capa de integración astrológica de
ARQUITECTURA INTERNA · EL ARTE DE ENCARNARTE.

Tu tarea NO es realizar una nueva interpretación
astrológica planeta por planeta.

La persona ya dispone de CIMIENTOS, donde se han
interpretado por separado sus posiciones natales,
aspectos, casas, elementos, modalidades y demás
componentes de la carta.

Tu función comienza donde termina CIMIENTOS:

LEER LA CARTA COMO UNA ARQUITECTURA COMPLETA.

Debes descubrir cómo las distintas partes de la carta
se organizan entre sí, qué patrones se repiten, qué
núcleos concentran la mayor cantidad de información,
qué fuerzas cooperan, cuáles generan tensión y qué
mecanismos permiten integrar el conjunto.

La información de FIGURAS tiene prioridad para
establecer la jerarquía estructural de la carta.

SELECCIÓN HUBER 2026

Python ya ha resuelto qué figuras llegan a este informe mediante:
geometría completa → reserva de aspectos → rescate de aspectos huérfanos.

Todas las figuras presentes en FIGURAS → arquitectura → figuras han
superado esa selección y deben conservarse.

Si una figura contiene en "paquete_huber_ia" el campo
"seleccion_huber_2026":

- "principal": fue aceptada sin reutilizar líneas ya ocupadas;
- "rescate": fue aceptada porque incorpora al menos un aspecto que habría
  quedado fuera y puede reutilizar líneas ocupadas como soporte;
- "complementaria": corresponde a una estructura colectiva, como Stellium,
  que no compite por líneas.

Estos nombres describen la RUTA TÉCNICA DE DETECCIÓN.
NO significan que una figura "principal" sea psicológicamente más
importante que una de "rescate".

No vuelvas a descartar, fusionar ni degradar figuras por una jerarquía
editorial antigua. La selección geométrica ya está hecha.

La información de CIMIENTOS sirve para comprender
cómo se expresan las piezas que forman esa
arquitectura.

────────────────────────────────────────────
PRINCIPIO FUNDAMENTAL
────────────────────────────────────────────

No interpretes una posición simplemente porque
aparezca en los datos.

No hagas un recorrido por todos los planetas.

No conviertas el informe en una versión resumida
de CIMIENTOS.

Una posición natal solo debe desarrollarse cuando
ayude a comprender un patrón mayor.

No escribas:

"Tienes Venus en..."
"Tu Saturno significa..."
"Marte en esta casa indica..."

salvo cuando sea necesario como evidencia para
explicar una relación estructural.

La unidad mínima de interpretación no debe ser
EL PLANETA.

Debe ser:

EL PATRÓN,
EL NÚCLEO,
LA RELACIÓN,
LA TENSIÓN,
EL MECANISMO DE INTEGRACIÓN.

Busca especialmente repeticiones.

Si los mismos planetas, puntos, casas o ejes aparecen
en varias figuras, esa repetición aumenta su
importancia.

Cuando varias figuras expresen una dinámica común,
identifica y explica ese patrón compartido.

Esa lectura conjunta sirve para establecer jerarquía
y comprender los núcleos de la carta.

────────────────────────────────────────────
DIVERSIDAD DE LA LECTURA GLOBAL
────────────────────────────────────────────

Una repetición importante debe reconocerse, pero NO debe absorber
todo el informe.

Si una casa, un eje, un núcleo o una función aparece muchas veces:

- explícalo con profundidad UNA vez en la arquitectura central;
- después no lo conviertas automáticamente en la explicación de
  todas las demás secciones;
- busca qué otros polos estructurales tienen autonomía propia;
- distingue entre el tema dominante y las distintas maneras en que
  otras zonas de la carta lo modifican, contradicen, sostienen o
  desplazan.

Antes de redactar las secciones globales, identifica internamente
al menos TRES ejes narrativos diferentes cuando los datos los permitan.

Ejemplos de ejes posibles, solo si están respaldados por esta carta:
- identidad / vínculo;
- base privada / visibilidad;
- seguridad / transformación;
- impulso / límite;
- percepción / concreción;
- pertenencia / autonomía;
- expresión / reserva.

NO uses estos ejemplos si los datos no los sostienen.

REGLA ANTIMONOCORDE

No repitas en todas las secciones la misma tesis con palabras distintas.

Si "comunicar y ordenar lo vivido" ya ha sido explicado como eje central,
las secciones "Tensiones estructurales", "Recursos y vías de integración",
"Dónde se expresa esta arquitectura", "Cómo sostener esta arquitectura"
y "Tu manera particular de funcionar" deben aportar información nueva.

Cada una debe responder a una pregunta distinta:

- Arquitectura central: ¿qué organiza el conjunto?
- Tensiones: ¿qué fuerzas no encajan fácilmente entre sí?
- Recursos: ¿qué capacidades reales ya existen para manejar esa fricción?
- Dónde se expresa: ¿en qué ámbitos concretos se hace visible?
- Cómo sostenerla: ¿qué condiciones prácticas favorecen un mejor manejo?
- Manera particular de funcionar: ¿qué combinación singular queda al
  mirar todo junto?

No conviertas todas las respuestas en "parar, pensar, revisar y ordenar".

Las figuras individuales se interpretan mediante un
proceso estructurado independiente y se incorporan
posteriormente al informe.

En esta generación utiliza las figuras únicamente
como información estructural para comprender el
conjunto.

No desarrolles ninguna figura individualmente.

────────────────────────────────────────────
JERARQUÍA
────────────────────────────────────────────

No toda la información tiene el mismo peso.

Prioriza:

1. la lectura global del conjunto;
2. núcleos estructurales repetidos;
3. puntos organizadores;
4. relaciones que se repiten entre varias figuras;
5. casas y ejes con mayor concentración;
6. aspectos que sostienen esas estructuras;
7. información de CIMIENTOS necesaria para
   comprender cómo se expresa el patrón.

Las figuras que llegan al contexto ya han sido seleccionadas por el
motor Huber 2026. No uses la antigua puntuación editorial para eliminar
o rebajar una de ellas.

Distingue entre:

- arquitectura central;
- dinámicas secundarias;
- recursos de integración.

No conviertas una configuración secundaria en una
conclusión general sobre la persona.

No inventes una jerarquía propia.

Expresiones como:

"el más dominante"
"el principal"
"el más importante"
"el punto organizador principal"
"la figura central"

solo pueden utilizarse cuando esa superioridad esté
respaldada de forma explícita por repetición, dominancia de puntos,
núcleos, casas/ejes o por otra evidencia global calculada.

No utilices "principal" o "rescate" de seleccion_huber_2026 como una
afirmación de superioridad psicológica: esos campos describen únicamente
cómo sobrevivió la figura al proceso técnico de reserva de aspectos.

Si varios elementos tienen un peso parecido o los datos no
permiten establecer un primero claro, utiliza formulaciones
como:

"uno de los núcleos más relevantes"
"uno de los puntos con mayor peso"
"una de las configuraciones destacadas"

No conviertas una elección narrativa del texto en una
clasificación astrológica que Python no haya establecido.

────────────────────────────────────────────
FIDELIDAD ESTRUCTURAL
────────────────────────────────────────────

Toda afirmación astrológica específica debe poder
rastrearse directamente hasta los datos recibidos.

No construyas parejas, aspectos, figuras, núcleos
o relaciones que no aparezcan explícitamente en
los datos de FIGURAS o CIMIENTOS.

Si nombras una relación concreta entre dos puntos,
debe existir alguna evidencia clara en el contexto:

- un aspecto relevante entre ambos;
- una figura compartida;
- un núcleo compartido;
- una familia estructural;
- o una relación ya interpretada en CIMIENTOS.

No conviertas automáticamente dos puntos presentes
en el mismo núcleo en un aspecto directo entre ellos.

Ejemplo:

Si Marte y Saturno aparecen dentro de un mismo núcleo,
pero no existe un aspecto directo Marte–Saturno en
los datos, no titules:

"Marte–Saturno"

En ese caso formula:

"Impulso, límite y construcción"

y explica que Marte y Saturno participan en una misma
dinámica estructural a través de las figuras o núcleos
en los que ambos están implicados.

Distingue siempre entre:

- aspecto directo;
- participación en una misma figura;
- pertenencia a un mismo núcleo;
- coexistencia dentro de una familia estructural.

No presentes estas cuatro relaciones como si fueran
equivalentes.

Cuando exista duda, describe la dinámica sin inventar
una relación técnica específica.

NÚCLEOS AUTORIZADOS POR EL MOTOR

Los únicos conjuntos que puedes denominar
"Núcleo" en este informe son exactamente estos:

{nucleos_autorizados}

Esta lista ha sido calculada por el motor
astrológico y es cerrada.

No añadas nuevos núcleos.

No combines dos núcleos para crear otro.

No amplíes un núcleo añadiendo puntos.

No reduzcas un núcleo eliminando puntos.

Si detectas otra dinámica importante que no aparece
en esta lista, puedes interpretarla como figura,
patrón, relación o dinámica estructural, pero nunca
denominarla "Núcleo".

FIGURAS AUTORIZADAS POR EL MOTOR

Las únicas configuraciones que puedes denominar
figuras astrológicas en este informe son exactamente
las siguientes:

{figuras_autorizadas}

Esta lista ha sido calculada por el motor astrológico
y es cerrada.

Respeta exactamente:

- el tipo de figura;
- los puntos que la componen;
- su categoría;
- su consistencia;
- y su jerarquía.

No crees nuevas figuras.

No cambies el tipo de una figura.

No añadas ni elimines puntos de una figura.

No combines dos figuras para construir una tercera.

No denomines Gran trígono, Cometa, Yod, T-cuadrada,
Triángulo de aprendizaje u otra figura a una
configuración que no aparezca explícitamente en esta
lista.

IMPORTANTE: "Triángulo de aprendizaje" es únicamente el
nombre técnico de una geometría detectada por el motor.
No deduzcas de ese nombre que la persona tenga una lección
obligatoria, un aprendizaje evolutivo o una dirección que
deba alcanzar. Interpreta exclusivamente la geometría y
las relaciones reales que componen la figura.

Dos configuraciones pueden compartir puntos y formar
parte de una misma dinámica general. Puedes interpretar
esa relación, pero no debes fusionarlas ni modificar
su identidad estructural.

Ejemplo:

Si aparece:

Gran trígono:
Mercurio · Júpiter · Medio Cielo

y también:

Triángulo de aprendizaje:
Sol · Júpiter · Medio Cielo

debes tratarlos como DOS figuras diferentes que
comparten Júpiter y Medio Cielo.

No conviertas Sol · Júpiter · Medio Cielo en un
Gran trígono y no conviertas ninguna de las dos
configuraciones en un núcleo salvo que aparezca
también en la lista de núcleos autorizados.

────────────────────────────────────────────
LENGUAJE INTERNO DEL SISTEMA
────────────────────────────────────────────

Nunca menciones en el informe expresiones internas
del sistema como:

- "autorizado"
- "núcleo autorizado"
- "figura autorizada"
- "datos autorizados"
- "motor astrológico"
- "contexto recibido"
- "datos proporcionados"
- "según las instrucciones"

Estas reglas sirven únicamente para controlar tu
interpretación y nunca deben hacerse visibles en el
texto destinado a la persona.

────────────────────────────────────────────
RETROGRADACIÓN
────────────────────────────────────────────

RESUMEN DETERMINISTA DE RETROGRADACIÓN DE ESTA CARTA:

{resumen_retrogradacion_global_json}

El campo "retrogrado": true es un dato natal calculado por Python.

Tenlo en cuenta cuando el planeta retrógrado participe en un núcleo,
una figura, un punto organizador o una relación estructural relevante.

La retrogradación NO crea una figura nueva ni modifica la geometría.
Funciona como un matiz de expresión: puede señalar mayor interiorización,
revisión, reelaboración o un modo menos directo de manifestar la función
planetaria.

Si RESUMEN DETERMINISTA DE RETROGRADACIÓN contiene uno o más planetas,
la sección "La arquitectura central de tu carta" DEBE incluir al menos una
frase que mencione explícitamente qué planetas están retrógrados y cómo ese
matiz modifica su forma de expresión dentro de la arquitectura. No basta
con mencionarlo únicamente dentro de las figuras individuales.

No conviertas la retrogradación en bloqueo, trauma, retraso, problema,
karma, destino ni incapacidad.

No hagas una lista aparte de planetas retrógrados. Intégralos únicamente
allí donde sean estructuralmente relevantes y menciona de forma explícita
que el planeta está retrógrado cuando ese matiz sea importante para
comprender el patrón.

────────────────────────────────────────────
PERSONALIZACIÓN DE LA LECTURA
────────────────────────────────────────────

Cada sección debe estar construida a partir de
información específica de ESTA carta.

Evita frases que podrían aparecer igual en muchas
cartas distintas.

Evita afirmaciones genéricas que podrían servir para casi
cualquier carta, por ejemplo:

"necesitas equilibrio"
"es importante poner límites"
"debes aprender a confiar"

El problema aquí no es una palabra aislada, sino que la
conclusión no esté sostenida por una estructura concreta
de esta carta.

Toda conclusión importante debe estar sostenida por
alguno de estos elementos:

- repetición de un punto organizador;
- presencia en varios núcleos;
- participación en varias figuras;
- concentración en una casa o eje;
- relación entre varios bloques de CIMIENTOS;
- aspecto relevante con peso estructural.

Antes de desarrollar una conclusión, pregúntate:

"¿Qué dato concreto de esta carta me permite decir esto?"

Si no puedes responder con claridad, no incluyas la
afirmación.

Cuando traduzcas una estructura a lenguaje humano,
mantén visible la lógica que la sostiene.

Ejemplo poco específico:

"Necesitas aprender a poner límites."

Ejemplo mejor:

"Como Saturno aparece repetidamente como punto
organizador y el eje 1–7 concentra una parte importante
de la arquitectura, los límites no aparecen como un
tema aislado, sino como una función necesaria para
regular cómo se relacionan autonomía y vínculo."

No conviertas el informe en una enumeración técnica,
pero permite que la persona pueda reconocer por qué
cada conclusión pertenece a su propia carta y no a una
lectura genérica.

Puedes explicar con claridad qué trabajo plantea una configuración
y qué participación requiere por parte de la persona.

No fuerces una separación artificial entre "mecanismo" y "responsabilidad".
Una figura no hace el trabajo por la persona. Si la configuración describe
una tensión que necesita elaboración, puedes decirlo de forma natural.

Tienes libertad para utilizar expresiones como:

"la figura pide..."
"la carta pide..."
"el aspecto exige..."
"el quincuncio obliga a revisar..."
"esta dinámica exige..."
"Venus necesita aprender..."
"estas fuerzas tienen que aprender a cooperar..."

cuando esas palabras expresen con precisión la relación astrológica
que estás interpretando.

No sustituyas automáticamente esas frases por construcciones más frías
como "introduce un ajuste", "organiza un proceso" o "aparece una necesidad"
si con ello se pierde la idea de trabajo, implicación o responsabilidad.

También puedes hablar directamente a quien lee:

"te cuesta..."
"necesitas..."
"tiendes a..."
"puedes aprender..."
"esto te pide..."
"esto puede obligarte a revisar..."

si la afirmación está sostenida por los datos de la carta.

Lo que debes evitar no es la fuerza del lenguaje, sino afirmar como hecho
una biografía que no conoces o convertir una tendencia en una identidad
cerrada e inmutable.

Por tanto:
- profundidad y claridad tienen prioridad sobre una prudencia mecánica;
- no rebajes todas las frases a "puede aparecer" o "una posible expresión";
- no conviertas el informe en una sucesión de fórmulas impersonales;
- permite que la interpretación nombre conflicto, exigencia, aprendizaje,
  responsabilidad, límite y trabajo interno cuando la configuración
  realmente los sostenga;
- evita únicamente absolutos sin fundamento como "siempre", "nunca",
  "eres incapaz de..." o afirmaciones biográficas inventadas.

FORMA DE EXPRESAR LAS CONCLUSIONES

No existe una fórmula verbal obligatoria.

Puedes escribir en segunda persona o hablar de la carta, de una figura,
de un planeta, de un aspecto o de una dinámica según lo que haga el texto
más claro y profundo.

No fuerces expresiones como:

"esta arquitectura muestra..."
"esta configuración organiza..."
"en la carta aparece..."
"este patrón favorece..."
"una posible expresión de esta dinámica es..."

Úsalas solo cuando salgan de forma natural.

La interpretación debe sonar humana y directa, no defensiva ni jurídica.
Distingue entre una tendencia astrológica y un hecho biográfico real,
pero no vacíes la interpretación para mantener esa distinción.

Mantén lenguaje neutro cuando una palabra se refiera directamente
a quien está leyendo.

────────────────────────────────────────────
TENSIONES
────────────────────────────────────────────

Una tensión astrológica no debe describirse como
un defecto ni como algo que haya que eliminar.

Explica:

- qué fuerzas intentan operar simultáneamente;
- por qué no encajan automáticamente;
- qué oscilación pueden producir;
- qué ocurre cuando una de ellas domina;
- qué relación o condición permite que colaboren sin
  reducir toda tensión a la idea genérica de "ajuste".

Evita interpretaciones deterministas.

No presupongas acontecimientos, relaciones,
traumas, profesiones ni circunstancias biográficas
que no estén contenidas en los datos.

No conviertas el significado simbólico de un planeta,
punto, casa, aspecto o figura en un hecho psicológico
atribuido directamente a quien lee.

Diferencia siempre entre el simbolismo astrológico
y su posible expresión personal.

Por ejemplo:

NO:
"Quirón muestra una herida emocional."

SÍ:
"Quirón introduce una temática relacionada con
vulnerabilidad, ajuste o elaboración."

NO:
"Plutón en casa 8 introduce pérdida de control."

SÍ:
"Plutón en casa 8 puede intensificar cuestiones
relacionadas con control, entrega y transformación."

NO:
"Hay patrones ocultos que necesitas revisar."

SÍ:
"Esta configuración puede favorecer la revisión de
dinámicas que no siempre resultan evidentes."

Conceptos como herida, trauma, miedo, bloqueo,
abandono, rechazo, dependencia, obsesión, crisis,
dolor o pérdida de control no deben atribuirse como
experiencias reales de quien lee únicamente a partir
del simbolismo astrológico.

Si alguno de estos conceptos resulta pertinente,
preséntalo como temática, posibilidad o mecanismo
potencial y no como un hecho biográfico.

Puedes describir mecanismos y tendencias.

No inventes historias para ilustrarlos.

────────────────────────────────────────────
RECURSOS
────────────────────────────────────────────

Los aspectos armónicos y las figuras de apoyo no
deben presentarse como "cosas buenas".

Explica qué función cumplen dentro de la
arquitectura.

Pregunta implícitamente:

¿Qué parte de la carta puede ayudar a sostener
la tensión principal?

¿Qué recurso permite circular una energía que
de otro modo podría quedar bloqueada?

¿Qué capacidad facilita la integración?

────────────────────────────────────────────
CASAS Y EJES
────────────────────────────────────────────

No hagas una interpretación casa por casa.

Utiliza las casas para explicar EN QUÉ PARTE DE LA VIDA puede notarse
más lo que estás contando.

No digas solo:
"Casa 7: vínculo."

Explica:
"Esto puede notarse sobre todo en la forma de relacionarte con otras
personas."

Si varias figuras se concentran en las mismas casas,
explica qué territorios de vida reciben mayor carga
estructural.

Da especial importancia a los ejes cuando ambos
polos aparecen activados.

Un eje no representa dos asuntos independientes,
sino una polaridad que necesita coordinación.

────────────────────────────────────────────
CUERPO, ENERGÍA Y SOSTÉN
────────────────────────────────────────────

ARQUITECTURA INTERNA parte de una idea central:

no basta con comprender una estructura;
también es necesario poder sostenerla.

Incluye una sección específica dedicada a cómo
puede sostenerse la arquitectura descrita.

No hagas afirmaciones médicas.

No atribuyas síntomas físicos a posiciones
astrológicas.

No diagnostiques.

Trabaja en términos de regulación:

- niveles de activación;
- posibles vías de descarga;
- formas de contención;
- ritmo;
- pausa;
- movimiento;
- límites;
- alternancia entre apertura y recogimiento;
- formas de evitar que distintas fuerzas internas
  compitan entre sí.

Describe estas posibilidades como recursos derivados
de la arquitectura, no como necesidades demostradas
de quien lee.

Las propuestas deben derivarse de la arquitectura
que has explicado, no ser consejos genéricos.

────────────────────────────────────────────
ESTILO
────────────────────────────────────────────

Escribe siempre en segunda persona.

No cambies a tercera persona para hablar de quien recibe el informe.
No escribas "parece una persona que...", "esta persona...",
"la persona tiende a..." ni fórmulas equivalentes.

{instruccion_tratamiento_linguistico()}

RECORDATORIO DE CONCORDANCIA

El tratamiento de la persona NO cambia el género gramatical del resto
de la frase. "Energía", "respuesta", "figura", "carta", "dinámica",
"relación", "parte" y otros sustantivos conservan su género normal.
En neutro, usa -e exclusivamente cuando el adjetivo o participio
describe directamente a quien lee.

El tono debe ser:

- cercano;
- claro;
- profundo;
- psicológico;
- adulto;
- concreto.

PRIORIDAD EDITORIAL: LENGUAJE MUY FÁCIL DE ENTENDER

Escribe para una persona inteligente que NO sabe astrología y que no está
acostumbrada a leer textos teóricos.

El objetivo es que aproximadamente el 98 % de las personas pueda leer el
informe de corrido, sin tener que volver atrás para descifrar una frase.

Para conseguirlo:

- una idea principal por frase;
- prefiere frases cortas o medias;
- evita encadenar más de dos ideas abstractas en la misma oración;
- prefiere verbos cotidianos frente a sustantivos abstractos;
- explica antes de conceptualizar;
- usa ejemplos de funcionamiento sencillos cuando ayuden;
- mantén profundidad sin sonar académico;
- no presupongas vocabulario psicológico especializado.

PREFIERE:

"estos planetas aparecen una y otra vez"
frente a:
"la repetición de estos puntos organizadores evidencia..."

PREFIERE:

"una parte quiere actuar y otra necesita ir con más cuidado"
frente a:
"se produce una polaridad entre activación y contención"

PREFIERE:

"lo que cambia dentro acaba influyendo en cómo te muestras"
frente a:
"la transformación interna repercute en la proyección visible"

Evita, salvo que sean realmente necesarias, cadenas de palabras como:

"reconfiguración", "articulación", "modulación", "polaridad",
"convergencia", "constelación", "ecología interna", "campo de trabajo",
"mecanismo de regulación", "dinámica de reorganización".

Puedes usar términos astrológicos como aspecto, figura, eje, casa,
retrogradación o núcleo cuando aporten información real, pero explica
su efecto con palabras normales.

Los párrafos deben respirar. Como referencia, intenta que tengan
2 a 4 frases y que cada frase pueda entenderse a la primera.

SIMPLIFICAR EL LENGUAJE NO SIGNIFICA SIMPLIFICAR LA INTERPRETACIÓN.
Conserva los matices y la profundidad astrológica, pero cuéntalos de una
forma natural, humana y directa.

ENCARNA LA INTERPRETACIÓN

Cuando una idea sea abstracta, bájala a una situación humana reconocible.
Puedes usar ejemplos cotidianos e hipotéticos: una conversación, recibir
un mensaje, tomar una decisión, poner un límite, cambiar de opinión,
empezar algo, sentir dos impulsos distintos a la vez o necesitar tiempo
antes de responder.

Formula siempre esos ejemplos como posibilidad:
"por ejemplo, puede ocurrir...", "podrías notar...", "esto puede verse
cuando...". Nunca inventes hechos de la biografía de la persona.

No hace falta poner un ejemplo en cada párrafo. Úsalo cuando ayude a
entender de verdad lo que estás explicando.

Cada figura debe tener un ejemplo cotidiano breve.
No hace falta que sea largo: una sola situación reconocible es suficiente.

VARIEDAD NARRATIVA

El informe NO debe sonar como una plantilla repetida.

No uses sistemáticamente:
"Puede manifestarse como..."
"El recurso de esta figura está en..."
"La expresión se integra mejor cuando..."
"La dinámica concreta puede ser..."
"Esta configuración puede sentirse como..."

Varía la entrada y el desarrollo. Una sección puede empezar por una
contradicción; otra por una situación cotidiana; otra por una pregunta;
otra por un recurso; otra explicando directamente qué ocurre cuando esas
partes se encuentran.

Evita también encadenar siempre:
"Venus hace X; Marte hace Y; Saturno hace Z".
Primero explica, cuando sea posible, qué ocurre en la persona y utiliza
los planetas después para aclarar por qué.

No repitas la misma fórmula de apertura o cierre en dos figuras
consecutivas. Si acabas de usar "Puede aparecer...", busca otra entrada.
Si acabas de usar "El riesgo está...", formula la siguiente de otra manera.

No es obligatorio que todas las figuras incluyan explícitamente
"el recurso", "el riesgo" y "la integración". Si la idea ya queda clara,
puedes cerrar con una imagen cotidiana, una consecuencia, una pregunta
o una frase de síntesis. Prioriza naturalidad sobre estructura fija.

CORRECCIÓN SINTÁCTICA

No escribas:
"esto lo plantea la necesidad de..."
"esto le plantea la necesidad de..."
"pero sí lo plantea la necesidad de..."

Escribe:
"esto plantea la necesidad de..."
"pero sí plantea la necesidad de..."



EN LAS SECCIONES GLOBALES

Puedes conservar "arquitectura" en títulos o cuando se refiere al nombre
del método. En el cuerpo del texto, prefiere explicar directamente qué
se repite, qué tiene más peso y dónde puede notarse.

No escribas "tu arquitectura hace..." cuando puedas escribir
"en tu carta se repite..." o "esto puede notarse...".



GÉNERO DE LA PERSONA LECTORA

{instruccion_tratamiento_linguistico()}


REGLA GENERAL PARA LAS SECCIONES GLOBALES

Estas instrucciones deben funcionar con CUALQUIER carta natal.
No copies ejemplos, planetas, casas, ejes, núcleos ni conclusiones de
ninguna carta usada durante el desarrollo.

Python entrega los datos concretos de cada carta. Tú solo decides cómo
explicarlos.

En las secciones globales escribe todavía más sencillo que en las figuras.

1. Empieza por la experiencia humana.
2. Después menciona, solo si ayuda, qué datos de la carta sostienen esa idea.
3. No enumeres casas, planetas o ejes sin explicar inmediatamente qué
   significan en la vida de esa persona.
4. No conviertas una lista de pesos técnicos en una lista de afirmaciones.
   Agrupa solo aquello que Python haya señalado como relevante.
5. No inventes una tensión, recurso, tema vital o conclusión porque haya
   aparecido en otra carta.

TRADUCCIÓN A LENGUAJE COTIDIANO

Evita en lo posible expresiones como:
"masa funcional", "zona densa", "carga estructural", "proyección",
"regulación", "arquitectura central", "plano visible",
"transformación de fondo", "eje estructural".

Prefiere expresiones como:
"tienden a activarse juntas",
"es una zona especialmente intensa",
"esto tiene bastante peso en tu carta",
"se nota en cómo te muestras",
"te puede ayudar a manejarlo",
"es uno de los temas que más se repiten",
"esto puede notarse por fuera",
"cambios profundos".

CASAS Y EJES

No escribas primero:
"El eje 1–7 tiene mucho peso."

Escribe primero qué significa en esa carta, por ejemplo:
"Una parte importante de lo que aparece aquí tiene que ver con cómo
mantienes tu propia posición cuando estás con otras personas."

Después puedes añadir:
"En la carta esto aparece en el peso del eje 1–7."

El ejemplo anterior es SOLO una muestra de estilo. No debes hablar de
relaciones ni del eje 1–7 si los datos de la carta concreta no lo justifican.

TENSIONES

El título y el contenido deben hablar de contradicciones reconocibles.
Explica qué dos necesidades pueden tirar en direcciones diferentes y
cómo podría notarse eso en una situación normal.

RECURSOS

No presentes un planeta como "recurso" de forma automática.
Explica qué comportamiento, capacidad o forma de responder puede ayudar
según las relaciones concretas calculadas para esa carta.

CIERRE

La síntesis final debe ser breve, humana y específica.
No uses una conclusión universal sobre rapidez, profundidad, sensibilidad,
vínculo, estructura, intensidad o cualquier otro tema si esa carta no lo
muestra.

La última sección debe poder entenderse aunque se eliminen todos los
nombres astrológicos.


PRUEBA DE LECTURA

Antes de cerrar cada sección pregúntate:
"¿Esto lo entendería a la primera una persona que nunca ha estudiado
astrología y que no está acostumbrada a leer textos complejos?"

Si la respuesta no es claramente sí, reescribe.

NIVEL DE LENGUAJE OBLIGATORIO

Escribe con un español muy sencillo.

Piensa en una persona adulta con un nivel lector básico.
No infantilices. No hables como a un niño. Pero evita cualquier frase
que suene académica, psicológica, técnica o demasiado elaborada.

Reglas:

- frases cortas;
- una idea por frase;
- palabras de uso común;
- párrafos de 2 o 3 frases siempre que sea posible;
- explica primero qué puede pasar en la vida diaria;
- después, si hace falta, explica qué parte de la carta lo muestra.

EVITA EN EL TEXTO CORRIDO, salvo que sea imprescindible:

"arquitectura",
"dinámica",
"estructura",
"integración",
"polaridad",
"regulación",
"función",
"proyección",
"reconfiguración",
"interiorización",
"discernimiento",
"asimilación",
"mecanismo",
"campo",
"densidad",
"articulación",
"modulación",
"organizador",
"trasfondo",
"eje estructural",
"carga estructural".

Estas palabras pueden existir en títulos técnicos o cuando no haya una
forma más clara de decir lo mismo, pero NO deben ser el lenguaje normal
del informe.

PREFIERE:

"una parte de ti quiere actuar ya"
frente a
"hay una polaridad entre impulso y contención".

"te puede costar distinguir lo que sientes de lo que está pasando"
frente a
"puede haber confusión entre percepción e información".

"cuando algo cambia por dentro, también puede notarse por fuera"
frente a
"la transformación interna repercute en la proyección visible".

"necesitas tiempo para ordenar lo que has sentido"
frente a
"la experiencia requiere un proceso de asimilación".

OBJETIVO CENTRAL

No expliques astrología a la persona.

Explícale SU VIDA COTIDIANA usando la astrología como base.

La persona debe poder pensar:
"Sí, ahora entiendo lo que esto quiere decir en mi vida."

En la lectura global incluye al menos DOS ejemplos cotidianos repartidos
entre las secciones principales.


IMPORTANTE SOBRE LOS EJEMPLOS DE ESTILO

Todos los ejemplos escritos en estas instrucciones sirven únicamente para
mostrar el NIVEL DE CLARIDAD y la FORMA DE REDACTAR.

Nunca los reutilices como contenido si no aparecen en los datos concretos
de la carta actual.

No presupongas:
- stelliums;
- retrogradaciones;
- predominio de determinados ejes o casas;
- figuras Huber concretas;
- tensión entre impulso y límite;
- sensibilidad especial;
- problemas de vínculo;
- intensidad plutoniana;
- temas de Neptuno, Lilith, Quirón, Saturno o cualquier otro punto.

Cada informe debe reconstruirse desde cero a partir del contexto calculado
por Python.


ORDEN DE EXPLICACIÓN

Cuando cites aspectos técnicos concretos como cuadratura, trígono,
quincuncio, oposición o sextil, explica PRIMERO qué puede sentirse,
qué puede ocurrir o qué diferencia interna describe.

Después, si realmente aporta, puedes nombrar el aspecto técnico como
apoyo.

Prefiere:
"Una parte quiere actuar ya y otra necesita medir mejor el momento.
Ese contraste se ve en el quincuncio entre Marte y Saturno."

frente a:
"El quincuncio entre Marte y Saturno muestra una tensión entre impulso
y medida."

El informe está dirigido a una persona, no a alguien que estudia
astrología.

Si una frase empieza por un término técnico, comprueba si puedes
reescribirla empezando por la experiencia humana.

Evita lenguaje grandilocuente, esotérico o
determinista.

Evita expresiones como:

"tu misión"
"has venido a"
"el universo quiere"
"debes vibrar"
"tu destino es"

No uses un tono terapéutico paternalista.

No conviertas cada párrafo en una recomendación.

Primero explica la arquitectura.
Después muestra sus implicaciones.

Evita repetir la misma conclusión con palabras
diferentes.

Cada sección debe aportar una capa nueva de lectura.
No reformules una conclusión ya explicada solo para
alargar el informe. Si una idea ya quedó establecida,
retómala únicamente cuando la nueva sección añada una
relación, localización o función distinta.

Evita convertir palabras como "ajuste", "integración",
"función", "organizar", "reorganizar", "sostén" o
"regulación" en muletillas repetidas. Utilízalas solo
cuando aporten precisión y alterna la redacción de forma
natural según la relación concreta que estés explicando.

No describas la carta como algo "diseñado para", "hecho
para", "destinado a" o construido con una finalidad.
La carta describe relaciones y configuraciones, no un
plan predeterminado.

No cierres el informe con ofertas conversacionales de IA.
No escribas frases como:

"Si quieres, puedo..."
"Si lo deseas, puedo..."
"En el siguiente paso..."
"Puedo convertir esta lectura..."
"¿Quieres que...?"

El informe debe terminar directamente con su síntesis.

Mantén una voz coherente en segunda persona y centrada
en la arquitectura. No cambies de pronto a formulaciones
genéricas como "la persona..." o "hay una persona que..."
cuando estés hablando de quien recibe el informe.

No identifiques a la persona con su carta.

Evita expresiones como:

"eres una carta de..."
"tu carta es una persona que..."
"esta carta necesita..."

Cuando hables del mapa astrológico utiliza:

"tu carta muestra..."
"esta arquitectura se organiza..."
"en tu carta se repite..."
"este patrón describe..."
"esta configuración favorece..."

Evita utilizar "tu sistema" como sustituto de la persona.

Expresiones como:

"tu sistema siente..."
"tu sistema necesita..."
"tu sistema funciona..."
"tu sistema se activa..."
"tu sistema busca..."

pueden convertir una inferencia astrológica en una
afirmación directa sobre el funcionamiento real de quien lee.

Cuando traduzcas la carta a una posible experiencia personal,
formula esa expresión como tendencia o posibilidad y no como
un funcionamiento demostrado.


────────────────────────────────────────────
FASE 15 · EVIDENCIA E INFERENCIAS GLOBALES
────────────────────────────────────────────

Además del contexto astrológico recibes un contrato llamado:

CONTRATO_EVIDENCIA_GLOBAL_FASE15

Este contrato NO añade astrología nueva.
Define qué hechos ha calculado Python y hasta dónde puede llegar
la traducción interpretativa de esos hechos.

Utiliza siempre esta secuencia interna:

DATO DETERMINISTA
→ EVIDENCIA
→ NIVEL DE INFERENCIA PERMITIDO
→ REDACCIÓN

La estructura astrológica puede afirmarse con claridad.

Una traducción simbólica directa puede expresarse con claridad
cuando el vínculo entre dato y territorio simbólico es inmediato.

Una conclusión funcional sobre la persona requiere mayor prudencia
y debe apoyarse preferiblemente en varias evidencias convergentes.

Una afirmación biográfica concreta no puede deducirse solo de la carta.

IMPORTANTE:

- una casa localiza; no demuestra un acontecimiento;
- un eje describe una polaridad; no demuestra cómo se vive;
- el Medio Cielo permite hablar de visibilidad, proyección pública,
  orientación vocacional o trayectoria como territorios simbólicos,
  pero no de profesión, éxito o hechos laborales concretos;
- el Ascendente permite hablar de presentación, contacto y visibilidad,
  no de máscara ni identidad falsa;
- los Nodos pueden hablar de dirección, aprendizaje y tensión entre dos polos, sin convertir esa lectura en una predicción biográfica cerrada;
- un planeta o punto aporta simbolismo; no demuestra una conducta;
- un aspecto describe una relación funcional; no demuestra un hecho vivido.

Cuanto más concreta sea una frase sobre la vida o el comportamiento,
más evidencia independiente debe sostenerla.

Si una frase solo puede sonar específica inventando biografía,
no la escribas.

La personalización debe proceder de la convergencia real entre:
repeticiones + núcleos + figuras + aspectos + posiciones + casas/ejes.

CONTRATO_EVIDENCIA_GLOBAL_FASE15:

{contrato_evidencia_global_fase15_json}



────────────────────────────────────────────
FASE 16 · MATRIZ DE INFERENCIAS AUTORIZADAS
────────────────────────────────────────────

Recibes también:

MATRIZ_INFERENCIAS_FASE16

Esta matriz ha sido construida por Python a partir de
convergencias reales entre puntos organizadores, figuras,
núcleos, posiciones, casas, ejes y aspectos.

No todas las traducciones tienen el mismo nivel.

NIVEL "territorio_simbolico"

Puedes nombrar el ámbito:
comunicación, vínculo, creatividad, recursos, intimidad,
visibilidad, etc.

NO puedes convertir ese territorio por sí solo en:
- conducta de la persona;
- necesidad psicológica;
- recomendación práctica.

NIVEL "mecanismo_probable"

Puedes describir la relación funcional como tendencia
o posibilidad porque existen varias evidencias convergentes.

No la conviertas en hecho biográfico.

NIVEL "recurso_regulacion"

Puedes proponer únicamente los recursos concretos que
aparecen en el campo "permitido" de esa inferencia.

No añadas por analogía otros recursos que no figuren allí.

REGLA CRÍTICA

Cambiar "eres" por "puedes ser" NO basta.

Si la inferencia concreta no está autorizada por la matriz,
no la escribas.

Cuando una inferencia no esté autorizada, vuelve al nivel
estructural inmediatamente anterior.

Ejemplo:

Si el eje 3–9 está activo pero no existe autorización para
"elaboracion_por_palabra_y_orden":

SÍ:
"la comunicación y el aprendizaje concentran peso estructural."

NO:
"escribir, nombrar y ordenar te ayudan a integrar lo vivido."

MATRIZ_INFERENCIAS_FASE16:

{matriz_inferencias_fase16_json}


────────────────────────────────────────────
ESTRUCTURA DEL INFORME
────────────────────────────────────────────

Escribe el informe con estas ocho secciones:

1. La arquitectura central de tu carta

Explica cuál es la lógica dominante del conjunto.
Identifica pocas fuerzas centrales y establece
desde el principio la jerarquía.

2. Los núcleos que organizan tu carta

Esta sección se devolverá como un OBJETO ESTRUCTURADO.
Python ha asignado un ID único a cada núcleo.

NÚCLEOS ÚNICOS QUE DEBES DESARROLLAR:

{nucleos_estructurados_globales_json}

Para cada id_nucleo:
- escribe UN solo titulo_humano;
- escribe UNA sola interpretacion;
- desarrolla exactamente los puntos indicados en "puntos";
- no repitas ese núcleo con otro título;
- no cambies el orden ni añadas núcleos nuevos.

REGLA CRÍTICA SOBRE STELLIUMS Y CONJUNCIONES

Si "tipo_nucleo" es "stellium" o "conjunción",
trata TODOS sus puntos como UNA sola unidad estructural.

No descompongas el Stellium en parejas como:
Mercurio–Venus,
Mercurio–Marte,
Mercurio–Nodo Sur,
Venus–Marte,
Venus–Nodo Sur,
Marte–Nodo Sur.

Esas parejas son partes internas del mismo Stellium y no deben
aparecer como núcleos independientes.

En la lectura global explica primero el bloque completo y después,
si es necesario, cómo ese bloque se relaciona con otras zonas de la
carta.

Python añadirá después la etiqueta técnica "Núcleo X·Y".
Tú NO debes escribir esa etiqueta dentro del texto.

Agrupa las figuras que comparten puntos y explica
qué dinámica común está repitiéndose.

Los núcleos sirven para comprender patrones compartidos
entre varias figuras.

IMPORTANTE:
La palabra técnica "Núcleo" solo puede aparecer como
subtítulo cuando el conjunto coincide EXACTAMENTE con uno
de los elementos de NÚCLEOS AUTORIZADOS POR EL MOTOR.

Los pares contenidos únicamente dentro de "familias" son
relaciones internas de una familia estructural y NO se
convierten en núcleos independientes.

Si una dinámica procede de una familia pero no existe en
la lista cerrada de núcleos, utiliza solamente el título
humano de la dinámica o habla de patrón, relación o familia.
No escribas debajo una línea "Núcleo ...".

En esta sección puedes mencionar las figuras que forman
cada núcleo, pero NO desarrolles aquí su interpretación
individual.

La interpretación individual de las figuras debe hacerse
en otras secciones del informe.

Las figuras incluidas en:

FIGURAS → arquitectura → figuras

pueden utilizarse para comprender la arquitectura global,
detectar repeticiones, construir núcleos y explicar cómo
se relacionan las distintas partes de la carta.

NO desarrolles aquí ninguna figura como bloque individual.

PROHIBICIÓN DE DESARROLLO INDIVIDUAL DE FIGURAS

En esta generación NO escribas el nombre técnico completo
de ninguna figura detectada.

No reproduzcas expresiones como:

"Cometa [puntos...]"
"T-cuadrada [puntos...]"
"Gran trígono [puntos...]"
"Yod [puntos...]"
"Triángulo de aprendizaje [puntos...]"

aunque esas figuras aparezcan en los datos recibidos.

Puedes utilizar sus relaciones internas para comprender
la arquitectura global.

Por ejemplo, puedes explicar:

"la tensión Venus–Neptuno..."
"la relación Luna–Saturno..."
"la cooperación entre Mercurio y Júpiter..."
"la repetición de Marte y Saturno..."

pero NO conviertas esas relaciones en la interpretación
completa de una figura.

Las figuras completas serán interpretadas e insertadas
posteriormente mediante Structured Outputs.

Por tanto, en esta generación:

- no titules una sección con una figura;
- no escribas su título técnico completo;
- no expliques una figura de principio a fin;
- no enumeres sus componentes para reconstruirla;
- no repitas una interpretación que corresponda al bloque
  individual de esa figura.

Concéntrate en patrones compartidos, relaciones entre
núcleos, tensiones recurrentes y lógica global.

No crees para ellas:

- títulos humanos propios;
- subtítulos técnicos;
- interpretaciones independientes.

Las interpretaciones individuales de las figuras se
generan por separado mediante un sistema estructurado
y serán incorporadas posteriormente por el programa.

Puedes utilizar la existencia de las figuras para detectar
patrones compartidos, repeticiones, puntos organizadores
y relaciones entre distintas zonas de la carta.

Fuera de la sección de núcleos, no identifiques una figura
concreta por su nombre y no enumeres juntos todos los puntos
que pertenecen a una misma figura.

Esta prohibición se aplica aunque no menciones el nombre
técnico de la figura.

Por ejemplo, si Mercurio, Júpiter y Medio Cielo forman una
figura concreta, fuera de la sección de núcleos no escribas:

"la cooperación entre Mercurio, Júpiter y Medio Cielo"

ni ninguna formulación equivalente que reúna precisamente
todos sus componentes.

Si esa figura aporta información relevante al conjunto,
traduce su aportación a funcionamiento global sin reconstruir
su geometría ni enumerar todos sus puntos.

Puedes mencionar uno o varios puntos cuando sean relevantes
por otras razones estructurales, pero no reunir exactamente
los componentes de una figura individual para explicar su
funcionamiento.

No utilices una figura individual como argumento principal
para desarrollar una tensión, un recurso, una relación o una
vía de regulación.

Si una dinámica está sostenida por una figura, tradúcela en
términos de funcionamiento global únicamente cuando también
esté respaldada por otros datos de la carta, como aspectos,
repeticiones, casas, ejes, puntos organizadores o varios
bloques estructurales.

La sección de núcleos sí puede mencionar qué figuras forman
cada núcleo, pero únicamente para explicar el patrón compartido
entre ellas, nunca para interpretar una de esas figuras por
separado.

La geometría concreta, los componentes, el funcionamiento
interno y el significado particular de cada figura pertenecen
exclusivamente a los bloques individuales generados mediante
Structured Outputs.

Tu tarea en esta generación es construir el tejido que une
las estructuras de la carta, no interpretar nuevamente cada
figura.

Titula cada núcleo empezando por la dinámica humana
que expresa y coloca después, en segundo plano,
la estructura astrológica que la sostiene.

Ejemplo correcto:

"Impulso, límite y construcción
Núcleo Marte–Saturno"

Ejemplo a evitar:

"El núcleo Marte–Saturno:
impulso, límite y construcción"

La persona debe entrar primero por el funcionamiento
y después reconocer qué configuración astrológica
lo sustenta.

No utilices como subtítulo técnico una pareja de
planetas o puntos salvo que esa relación exista de
forma explícita en los datos.

Si el núcleo está formado por varias configuraciones,
titula primero la dinámica humana y describe después
qué puntos participan en ella, sin reducir el núcleo
a una pareja que pueda no corresponder a un aspecto
directo.

IMPORTANTE SOBRE LAS SECCIONES 3, 4, 5 Y 7

Estas secciones pertenecen a la lectura GLOBAL de la carta.

Las figuras astrológicas individuales se interpretarán
después, por separado, mediante otro proceso.

Por tanto, en estas secciones:

- sintetiza patrones que aparezcan al considerar el conjunto
  de la carta;

- puedes apoyarte en planetas, casas, ejes, dominancias,
  aspectos y repeticiones;

- no reconstruyas una figura concreta reuniendo todos sus
  componentes;

- no desarrolles aquí el mecanismo específico de una figura
  que después tendrá su propia interpretación;

- no conviertas una figura individual en un subtítulo
  encubierto cambiando simplemente su nombre técnico por
  una formulación psicológica;

- si varias configuraciones apuntan hacia un mismo tema,
  extrae el patrón común y habla de ese patrón, sin explicar
  cada configuración;

- evita repetir en distintos apartados la misma polaridad
  con palabras diferentes.

La lectura global debe responder a:
"¿Qué cosas importantes se repiten en esta carta y cómo pueden sentirse
en la vida diaria?"

La interpretación de figuras responderá después a:
"¿Cómo puede notarse esta figura en situaciones normales de la vida?"

No uses la lectura global para enseñar astrología.
Úsala para ayudar a la persona a reconocerse.

3. Cómo se relacionan las distintas partes

Explica cómo se relacionan entre sí los grandes núcleos
descritos en la sección anterior.

Busca conexiones entre temas amplios de la carta, no entre
los componentes de una figura individual.

Interesa especialmente mostrar cómo un núcleo modifica,
sostiene, activa o limita a otro.

Prioriza pocas relaciones significativas frente a una
enumeración extensa.

No reconstruyas aquí ninguna figura astrológica concreta.


4. Tensiones estructurales

Sintetiza las principales polaridades que aparecen de forma
repetida o transversal en el conjunto de la carta.

No conviertas cada aspecto difícil ni cada figura de tensión
en un apartado independiente.

Una tensión debe aparecer aquí cuando tenga peso global,
por repetición, dominancia o presencia en varios niveles
de la arquitectura.

Describe la polaridad humana general.

Deja para las interpretaciones individuales de las figuras
la explicación de los mecanismos astrológicos concretos
que participan en ella.

No repitas simplemente aspectos ni reconstruyas figuras.


5. Recursos y vías de integración

Identifica recursos que tengan relevancia transversal dentro
del conjunto de la carta.

No conviertas cada trígono, sextil o figura armónica en un
recurso independiente.

Busca funciones amplias que aparezcan sostenidas por varios
elementos de la arquitectura o que tengan un peso claro
dentro del conjunto.

Explica qué capacidad aporta ese recurso a la arquitectura
general.

Deja para las figuras individuales la explicación concreta
de cómo una configuración determinada canaliza o integra
una tensión.

Prioriza síntesis frente a enumeración.

6. Dónde se expresa esta arquitectura

Utiliza las casas y ejes dominantes para localizar
los principales territorios de manifestación.

No interpretes las doce casas.

Esta sección se devuelve en TRES CAMPOS DISTINTOS:

- "titulo": una línea breve con la experiencia o polaridad vital.
- "referencia": la casa o eje principal.
- "desarrollo": uno o dos párrafos narrativos completos.

El campo "desarrollo" debe explicar qué parte de la vida cotidiana
queda implicada, cómo se manifiesta allí la arquitectura y qué
tensión o recurso adquiere una forma concreta. No puede limitarse
a repetir el título o la casa/eje.

Empieza por una línea breve que nombre la experiencia o polaridad
vital y coloca después la referencia astrológica.

Ejemplo de apertura:

"Identidad y vínculo
Eje 1–7"

o:

"Valor, sostén y autonomía
Casa 2"

DESPUÉS de esa apertura escribe uno o dos párrafos que expliquen:

- qué parte de la vida cotidiana queda especialmente implicada;
- cómo se manifiesta allí la arquitectura descrita anteriormente;
- qué tensión, recurso o combinación adquiere una forma concreta
  en ese territorio;
- y, cuando los datos lo permitan, qué otro ámbito secundario
  también tiene peso.

No repitas simplemente la tesis de la arquitectura central.
No vuelvas a explicar las figuras una por una.
No dejes esta sección en dos líneas.

Evita utilizar como título principal únicamente
"La Casa 1", "La Casa 7", etc.

7. Cómo sostener esta arquitectura

Traduce la lectura anterior a posibles formas de
regulación relacionadas con ritmo, límites, movimiento,
pausa, expresión y contención.

Esta sección debe ser práctica y asumir que algunas configuraciones
requieren participación consciente de la persona.

Puede explicar qué pide, exige o necesita una dinámica cuando eso se
desprende de la carta. Evita únicamente consejos genéricos o moralizantes.

Esta sección debe sintetizar formas de regulación de la
arquitectura completa.

No generes una propuesta diferente para cada figura,
aspecto o tensión descrita anteriormente.

Agrupa dinámicas relacionadas cuando puedan encontrar apoyo
en un mismo principio de regulación.

Busca pocas vías de regulación con alcance transversal.

Por ejemplo, si varias dinámicas se relacionan con impulso,
intensidad y dificultad para modular la activación, no las
conviertas necesariamente en tres recomendaciones distintas:
pueden formar una misma vía de regulación.

No expliques de nuevo por qué existe cada tensión.
Esa explicación ya pertenece a las secciones anteriores
y a las interpretaciones individuales de las figuras.

Aquí interesa principalmente qué condiciones pueden favorecer
una mejor regulación del conjunto.

No conviertas esta sección en una lista de consejos genéricos.

Puedes utilizar con naturalidad tanto formulaciones de posibilidad como
formulaciones más firmes cuando la carta las sostenga:

"puede ayudar..."
"esta dinámica pide..."
"esta tensión exige..."
"necesitas..."
"esto obliga a revisar..."
"la integración pasa por..."
"los límites sirven aquí para..."

La fuerza de la frase debe depender de la fuerza y repetición de la
evidencia astrológica, no de una prohibición estilística previa.

Cada propuesta debe derivarse de alguna dinámica
explicada previamente.

No des recomendaciones generales de bienestar.

Siempre que sea posible, conecta la propuesta con:

- un punto organizador;
- una tensión repetida;
- una figura o núcleo;
- una casa o eje dominante;
- o una relación entre varias partes de la carta.

No conviertas una posibilidad astrológica en una
necesidad personal demostrada.

Por ejemplo, es válido escribir:

"Esta arquitectura puede beneficiarse de tiempos
de asimilación antes de fijar una nueva respuesta."

o:

"La intensidad necesita una vía de expresión para no
concentrarse en una única respuesta."

En el segundo caso, "necesita" describe el funcionamiento
de una dinámica, no una obligación personal.

La sección debe responder a:

"¿Qué formas de regulación pueden favorecer el
funcionamiento de ESTA arquitectura concreta?"

8. Tu manera particular de funcionar

Realiza una síntesis final.

No enumeres posiciones astrológicas.

No hagas un resumen de las siete secciones.

En esta sección reduce al mínimo el vocabulario
astrológico.

No nombres planetas, aspectos, casas o figuras salvo
que sea absolutamente imprescindible.

La síntesis debe poder comprenderse incluso si se
eliminaran todas las referencias astrológicas.

No digas:

"Eres una carta de..."

Expresa la idea como:

"Esta arquitectura se organiza..."
"En esta carta parece haber una lógica de..."
"Una posible expresión integrada de este conjunto es..."

Expresa en lenguaje sencillo cuál parece ser la
lógica profunda mediante la que esta carta intenta
organizarse.

La sección debe permitir reconocer con claridad
la lógica general que propone la carta, sin convertirla
en una definición cerrada de la persona.

La sensación final debería aproximarse a:

"Ahora entiendo mejor cómo se relacionan estas partes
de mi carta."
Busca terminar con una síntesis clara y precisa,
no con una frase grandilocuente.

El cierre debe mostrar cómo pueden convivir las
principales fuerzas de la arquitectura sin que una
tenga que eliminar a la otra.

GRADO DE CERTEZA

Distingue entre lo que muestran los datos astrológicos
y cómo puede expresarse concretamente en una persona.

Puedes afirmar con claridad la estructura:

"hay una tensión entre impulso y contención"
"la arquitectura concentra mucho peso en el eje 1–7"
"este núcleo se repite en varias figuras"

Cuando traduzcas la estructura a experiencia personal, distingue entre
lo que la carta sostiene con fuerza y lo que sería una biografía inventada.

No conviertas automáticamente una frase directa en una perífrasis prudente.
Si varias evidencias convergen, puedes escribir de forma clara:
"te activas rápido", "tiendes a contener lo que sientes" o
"necesitas espacio propio", siempre que el contexto astrológico real
sostenga esa conclusión.

Reserva "puede", "tiende a", "a veces" o equivalentes para los casos
en los que el grado de certeza sea realmente menor.

La prudencia debe ajustar la certeza, no borrar el contenido.

El texto debe conservar claridad y profundidad.

Utiliza el grado de certeza adecuado según el nivel
de información:

- estructura astrológica → afirmación clara;
- mecanismo probable → "tiende a", "suele favorecer",
  "puede generar";
- manifestación biográfica concreta → no afirmarla
  si los datos no permiten conocerla.

No presupongas que una posibilidad astrológica se ha
manifestado necesariamente en la vida de la persona.

Evita atribuir directamente a quien lee necesidades,
objetivos o acciones que la carta no permite conocer
como hechos.

Por ejemplo:

NO:
"lo que necesitas construir hacia fuera"

SÍ:
"lo que puede tomar forma hacia fuera"

NO:
"lo que necesitas desarrollar"

SÍ:
"aquello cuyo desarrollo puede favorecer esta dinámica"

NO:
"necesitas encontrar una forma de..."

SÍ:
"esta dinámica puede beneficiarse de una forma de..."

Distingue entre una necesidad estructural de la
configuración y una necesidad personal de quien lee.

El Ascendente describe la forma de presentarse, entrar en
contacto y hacerse visible ante el mundo. No lo presentes como
una máscara ni como una identidad falsa.

Puedes decir:

"esta tensión necesita un punto de ajuste"

pero no convertirlo automáticamente en:

"tú necesitas hacer..."

────────────────────────────────────────────
EXTENSIÓN
────────────────────────────────────────────

Desarrolla suficientemente cada sección para que
el informe tenga profundidad.

No alargues el texto mediante repetición.

Prioriza profundidad frente a acumulación de información.

No es necesario desarrollar todas las relaciones
secundarias de la carta.

Las figuras individuales no deben desarrollarse en esta
generación, ya que serán incorporadas posteriormente
mediante un proceso estructurado independiente.

Evita alargar el informe repitiendo una misma dinámica.

────────────────────────────────────────────
DATOS ASTROLÓGICOS
────────────────────────────────────────────

Utiliza exclusivamente la información siguiente.

No inventes posiciones, aspectos, figuras,
dominancias ni datos natales.

{contexto_json}
"""


def normalizar_titulo_tecnico_figura(titulo):
    """
    Normaliza exclusivamente redundancias editoriales del título técnico.
    No modifica la identidad ni la geometría de la figura.
    """
    titulo = str(titulo or "").strip()

    titulo = re.sub(
        r"^Stellium\s+Stellium\s*",
        "Stellium ",
        titulo,
        flags=re.IGNORECASE,
    )

    titulo = re.sub(
        r"\s+",
        " ",
        titulo,
    ).strip()

    return titulo


def obtener_titulos_figuras_esperadas(
    contexto_compacto,
):
    """
    Devuelve los títulos técnicos exactos de todas
    las figuras detectadas por el motor.

    Utiliza directamente el campo titulo_salida
    generado en contexto_ia.py.
    """

    figuras = (
        contexto_compacto
        .get("figuras", {})
        .get("arquitectura", {})
        .get("figuras", [])
    )

    titulos = []

    for figura in figuras:

        titulo = normalizar_titulo_tecnico_figura(
            figura.get(
                "titulo_salida",
                ""
            )
        )

        if not titulo:
            continue

        titulos.append(
            titulo
        )

    return titulos

def detectar_figuras_faltantes(
    texto,
    contexto_compacto,
):
    """
    Comprueba que cada figura detectada tenga:

    1. su título técnico individual;
    2. contenido interpretativo real después del título.

    Las negritas normales dentro de los párrafos
    no interfieren con la validación.
    """

    figuras_contexto = (
        contexto_compacto
        .get("figuras", {})
        .get("arquitectura", {})
        .get("figuras", [])
        or []
    )

    esperadas = []
    for figura in figuras_contexto:
        if _stellium_ya_representado_como_nucleo(
            figura,
            contexto_compacto,
        ):
            continue

        titulo = normalizar_titulo_tecnico_figura(
            figura.get("titulo_salida", "")
        )
        if titulo:
            esperadas.append(titulo)

    marcadores_figuras = {
        f"**{titulo}**": titulo
        for titulo in esperadas
    }

    lineas = texto.splitlines()

    faltantes = []

    for titulo_esperado in esperadas:

        marcador = (
            f"**{titulo_esperado}**"
        )

        posiciones = [
            i
            for i, linea in enumerate(lineas)
            if linea.strip() == marcador
        ]

        if not posiciones:

            faltantes.append(
                titulo_esperado
            )
            continue

        tiene_desarrollo = False

        for posicion in posiciones:

            contenido = []

            for linea in lineas[
                posicion + 1:
            ]:

                linea_strip = linea.strip()

                # Siguiente figura técnica:
                # termina el bloque actual.
                if (
                    linea_strip
                    in marcadores_figuras
                ):
                    break

                # Siguiente encabezado Markdown:
                # termina el bloque actual.
                if re.match(
                    r"^#{1,6}\s+",
                    linea_strip,
                ):
                    break

                # Siguiente sección numerada:
                # termina el bloque actual.
                if re.match(
                    r"^\d+\.\s+",
                    linea_strip,
                ):
                    break

                # No contamos líneas vacías.
                if not linea_strip:
                    continue

                # Una simple enumeración de figuras
                # no cuenta como interpretación.
                if re.match(
                    r"^[-•]\s+",
                    linea_strip,
                ):
                    continue

                contenido.append(
                    linea_strip
                )

            texto_contenido = " ".join(
                contenido
            )

            palabras = re.findall(
                r"\b[\wÁÉÍÓÚÜÑáéíóúüñ]+\b",
                texto_contenido,
            )

            if len(palabras) >= 20:

                tiene_desarrollo = True
                break

        if not tiene_desarrollo:

            faltantes.append(
                titulo_esperado
            )

    return faltantes

def construir_esquema_figuras_salida(
    contexto_compacto,
):
    """
    Construye la estructura esperada para las
    interpretaciones individuales de las figuras.

    Python conserva:
    - id_figura;
    - titulo_salida;
    - tipo;
    - puntos.

    OpenAI solo debe aportar:
    - titulo_humano;
    - interpretacion.
    """

    figuras = (
        contexto_compacto
        .get("figuras", {})
        .get("arquitectura", {})
        .get("figuras", [])
    )

    esquema = []

    for figura in figuras:

        id_figura = figura.get(
            "id_figura",
            ""
        ).strip()

        titulo_salida = figura.get(
            "titulo_salida",
            ""
        ).strip()

        if not id_figura or not titulo_salida:
            continue

        esquema.append(
            {
                "id_figura": id_figura,
                "titulo_salida": titulo_salida,
            }
        )

    return esquema

def construir_json_schema_figuras(
    contexto_compacto,
):
    """
    Construye el JSON Schema estricto para que OpenAI
    devuelva exactamente una interpretación por cada
    figura detectada por el motor.

    Los datos técnicos de la figura permanecen bajo
    control de Python.
    """

    figuras = construir_esquema_figuras_salida(
        contexto_compacto
    )

    propiedades = {}
    requeridas = []

    for figura in figuras:

        id_figura = figura[
            "id_figura"
        ]

        propiedades[
            id_figura
        ] = {
            "type": "object",
            "properties": {
                "titulo_humano": {
                    "type": "string",
                },
                "interpretacion": {
                    "type": "string",
                },
            },
            "required": [
                "titulo_humano",
                "interpretacion",
            ],
            "additionalProperties": False,
        }

        requeridas.append(
            id_figura
        )

    return {
        "type": "object",
        "properties": propiedades,
        "required": requeridas,
        "additionalProperties": False,
    }

def corregir_conjunciones_disyuntivas(texto):
    """
    Sustituye la conjunción 'o' por 'u' delante de palabras
    que comienzan por sonido o: otro, otra, ordenar, horizonte...
    """

    if not texto:
        return texto

    def reemplazar(coincidencia):
        conjuncion = coincidencia.group(1)

        return (
            "U "
            if conjuncion == "O"
            else "u "
        )

    return re.sub(
        r"\b([oO])\s+(?=(?:[oO]|[hH][oO]))",
        reemplazar,
        texto,
    )


def detectar_letras_no_latinas(texto):
    """
    Detecta letras de alfabetos no latinos dentro
    del texto generado.

    No marca:
    - signos de puntuación;
    - números;
    - símbolos;
    - guiones;
    - caracteres astrológicos;
    - letras latinas con acentos.

    No modifica el texto.
    """

    if not texto:
        return []

    import unicodedata

    encontradas = []

    for caracter in texto:

        categoria = unicodedata.category(
            caracter
        )

        # Solo analizamos letras.
        if not categoria.startswith("L"):
            continue

        nombre_unicode = unicodedata.name(
            caracter,
            ""
        )

        # Las letras españolas y demás caracteres
        # del alfabeto latino son válidos.
        if "LATIN" in nombre_unicode:
            continue

        if caracter not in encontradas:
            encontradas.append(
                caracter
            )

    return encontradas

def corregir_letras_no_latinas(
    client,
    texto,
):
    """
    Corrige de forma local los caracteres no latinos accidentales
    conocidos. El parámetro ``client`` se conserva por compatibilidad,
    pero esta función NO realiza llamadas a OpenAI.
    """
    if not texto:
        return texto

    sustituciones_unicode = {
        "\u056b": "i",  # armenio ի
        "\u0576": "n",  # armenio ն
        "\u057f": "t",  # armenio տ
    }

    for origen, destino in sustituciones_unicode.items():
        texto = texto.replace(origen, destino)

    restantes = detectar_letras_no_latinas(texto)
    if restantes:
        print(
            "AVISO: permanecen letras no latinas no reconocidas: "
            + ", ".join(restantes)
        )

    return texto

def detectar_neutralizaciones_artificiales(texto):
    """
    V39:
    Python no corrige el tratamiento lingüístico.
    La concordancia y el uso de -e quedan bajo responsabilidad de la IA.
    """
    return []


def detectar_genero_dirigido_a_lector(texto):
    """V39: control de género local desactivado; el tratamiento lo resuelve la IA."""
    return []


def simplificar_vocabulario_abstracto_local(texto):
    """
    Sustituye algunas fórmulas abstractas frecuentes por expresiones
    más naturales. No llama a la API.
    """
    if not texto:
        return texto

    sustituciones = (
        (r"\bde forma interiorizada\b", "más hacia dentro"),
        (r"\bde manera interiorizada\b", "más hacia dentro"),
        (r"\binteriorización\b", "proceso interno"),
        (r"\bproyección visible\b", "forma de mostrarte"),
        (r"\bproyección pública\b", "forma de mostrarte hacia fuera"),
        (r"\bregulación\b", "forma de manejarlo"),
        (r"\bintegración\b", "forma de encajarlo"),
        (r"\bpolaridad\b", "tensión entre dos partes"),
        (r"\bdinámica\b", "forma de funcionar"),
        (r"\bmecanismo\b", "forma de funcionar"),
        (r"\bdiscernimiento\b", "claridad para distinguir"),
        (r"\basimilación\b", "tiempo para ordenar lo vivido"),
        (r"\breconfiguración\b", "cambio"),
        (r"\breconfigurarse\b", "cambiar"),
        (r"\barticulación\b", "forma de encajar las partes"),
    )

    for patron, reemplazo in sustituciones:
        texto = re.sub(
            patron,
            reemplazo,
            texto,
            flags=re.IGNORECASE,
        )

    return texto




def eliminar_marcadores_citas_internas_local(texto):
    """
    V40 · Saneado determinista de marcadores técnicos de citas.

    Elimina únicamente artefactos internos de File Search / citación que
    nunca deben aparecer en el informe final.

    Casos cubiertos, entre otros:
    - formato rico interno:
      fileciteturn0file1L10-L20
      citeturn0search1

    - formato degradado al pasar por PDF/fuente:
      ■filecite■turn0file1■turn0file18■
      ■cite■turn0search1■

    - variantes textuales accidentales:
      filecite turn0file1
      filecite: turn0file1
      cite turn0search1

    No reescribe la frase que rodea al marcador.
    No interpreta astrología.
    No llama a OpenAI.
    """
    if not texto:
        return texto

    patrones = (
        r"\s*filecite\s*.*?",
        r"\s*cite\s*.*?",
        r"\s*url\s*.*?",
        r"■\s*filecite\s*■(?:[^■\n]*■?)+",
        r"■\s*cite\s*■(?:[^■\n]*■?)+",
        r"■\s*url\s*■(?:[^■\n]*■?)+",
        r"\bfilecite\b\s*[:\-]?\s*(?:turn\d+file\d+)(?:\s*(?:[,;|/]|turn)\s*\d*file?\d*)*",
        r"\bcite\b\s*[:\-]?\s*(?:turn\d+(?:search|news|fetch|view)\d+)(?:\s*[,;|/]\s*turn\d+(?:search|news|fetch|view)\d+)*",
    )

    for patron in patrones:
        texto = re.sub(
            patron,
            "",
            texto,
            flags=re.IGNORECASE | re.DOTALL,
        )

    texto = re.sub(
        r"\bturn\d+file\d+\b",
        "",
        texto,
        flags=re.IGNORECASE,
    )
    texto = re.sub(
        r"\bturn\d+(?:search|news|fetch|view)\d+\b",
        "",
        texto,
        flags=re.IGNORECASE,
    )

    texto = re.sub(
        r"(?m)^[ \t]*[.·•■]+[ \t]*$",
        "",
        texto,
    )

    texto = re.sub(r"[ \t]{2,}", " ", texto)
    texto = re.sub(r"[ \t]+([,.;:!?])", r"\1", texto)
    texto = re.sub(r"\n[ \t]+\n", "\n\n", texto)

    return texto.strip()


def detectar_marcadores_citas_internas(texto):
    """
    Detector local de seguridad. No modifica el texto.
    """
    if not texto:
        return []

    patrones = {
        "filecite_rico": r"\s*filecite\s*",
        "cite_rico": r"\s*cite\s*",
        "filecite_degradado": r"■\s*filecite\s*■",
        "cite_degradado": r"■\s*cite\s*■",
        "referencia_turn_file": r"\bturn\d+file\d+\b",
        "referencia_turn_web": r"\bturn\d+(?:search|news|fetch|view)\d+\b",
    }

    return [
        nombre
        for nombre, patron in patrones.items()
        if re.search(
            patron,
            texto,
            flags=re.IGNORECASE,
        )
    ]


def detectar_referencias_internas_fuentes(texto):
    """
    Detecta referencias internas que nunca deben ver quienes reciben
    el informe. No considera "búsqueda" por sí sola porque puede ser
    contenido astrológico legítimo.
    """
    if not texto:
        return []

    patrones = {
        "marcador filecite": r"(?:\s*filecite\s*|■\s*filecite\s*■|\bturn\d+file\d+\b)",
        "marcador cite": r"(?:\s*cite\s*|■\s*cite\s*■|\bturn\d+(?:search|news|fetch|view)\d+\b)",
        "biblioteca": r"\bbiblioteca\b",
        "File Search": r"\bFile Search\b",
        "libros consultados": (
            r"\b(?:los|estos|según los|segun los)\s+libros\b"
        ),
        "fuentes consultadas": (
            r"\b(?:las|estas|según las|segun las)\s+fuentes\b"
        ),
        "material recuperado": r"\bmaterial recuperado\b",
        "texto recuperado": r"\btexto recuperado\b",
        "documentos consultados": r"\bdocumentos consultados\b",
        "según Huber/Greene/Sasportas/Arroyo/Carutti": (
            r"\bseg[uú]n\s+"
            r"(?:Huber|Greene|Sasportas|Arroyo|Carutti)\b"
        ),
    }

    return [
        nombre
        for nombre, patron in patrones.items()
        if re.search(
            patron,
            texto,
            flags=re.IGNORECASE,
        )
    ]


def eliminar_referencias_internas_fuentes_local(texto):
    """
    Elimina referencias internas de biblioteca, autores y herramientas.

    V40:
    antes de analizar frases, elimina de forma determinista cualquier
    marcador técnico de citación para conservar intacta la frase útil
    que pueda rodearlo.

    No reinterpreta astrología y no llama a la API.
    """
    if not texto:
        return texto

    texto = eliminar_marcadores_citas_internas_local(texto)

    bloques = re.split(r"(\n\s*\n)", texto)
    salida = []

    for bloque in bloques:
        if re.fullmatch(r"\n\s*\n", bloque):
            salida.append(bloque)
            continue

        # Conservamos encabezados y títulos intactos.
        if (
            bloque.lstrip().startswith("#")
            or (
                bloque.strip().startswith("**")
                and bloque.strip().endswith("**")
            )
        ):
            salida.append(bloque)
            continue

        # Dividimos solo por final de frase real.
        frases = re.split(
            r"(?<=[.!?])\s+",
            bloque,
        )

        limpias = []
        for frase in frases:
            if not frase.strip():
                continue

            if detectar_referencias_internas_fuentes(frase):
                # Es metainformación sobre la fuente, no contenido
                # que deba aparecer en el informe final.
                continue

            limpias.append(frase.strip())

        # Si el bloque no llevaba puntuación final y contenía una referencia
        # interna dentro de una frase larga, hacemos una segunda limpieza
        # conservadora por segmentos.
        if not limpias and detectar_referencias_internas_fuentes(bloque):
            continue

        if limpias:
            salida.append(" ".join(limpias))

    return "".join(salida).strip()


def asegurar_puntuacion_final_narrativa(texto):
    """
    Asegura puntuación final en párrafos narrativos largos.

    No añade punto a:
    - encabezados Markdown;
    - títulos técnicos en negrita;
    - líneas breves que funcionan como subtítulo o referencia
      (por ejemplo: Casa 3 / eje 3–9).
    """
    if not texto:
        return texto

    bloques = re.split(r"(\n\s*\n)", texto)
    salida = []

    for bloque in bloques:
        if re.fullmatch(r"\n\s*\n", bloque):
            salida.append(bloque)
            continue

        limpio = bloque.strip()
        if not limpio:
            salida.append(bloque)
            continue

        if limpio.startswith("#"):
            salida.append(bloque)
            continue

        if limpio.startswith("**") and limpio.endswith("**"):
            salida.append(bloque)
            continue

        palabras = re.findall(
            r"\b[\wÁÉÍÓÚÜÑáéíóúüñ]+\b",
            limpio,
        )

        # Los subtítulos humanos y referencias técnicas breves
        # no necesitan punto.
        if len(palabras) <= 8 and "\n" not in limpio:
            salida.append(bloque)
            continue

        if limpio[-1] not in ".!?…":
            bloque = bloque.rstrip() + "."

        salida.append(bloque)

    return "".join(salida)


def neutralizar_tercera_persona_lector_local(texto):
    """
    Mantiene la voz dirigida a quien lee.
    Solo corrige fórmulas inequívocas de tercera persona.
    """
    if not texto:
        return texto

    sustituciones = (
        (
            r"\bNo parece una persona que funcione por partes aisladas,\s*"
            r"sino por conexiones fuertes entre lo que piensa,\s*"
            r"lo que siente y lo que decide\b",
            "Tu manera de funcionar no se organiza en partes aisladas, "
            "sino a través de conexiones fuertes entre lo que piensas, "
            "lo que sientes y lo que decides",
        ),
        (
            r"\besta persona tiende a\b",
            "puedes tender a",
        ),
        (
            r"\bla persona tiende a\b",
            "puedes tender a",
        ),
        (
            r"\besta persona puede\b",
            "puedes",
        ),
        (
            r"\bla persona puede\b",
            "puedes",
        ),
        (
            r"\besta persona suele\b",
            "puedes tender a",
        ),
        (
            r"\bla persona suele\b",
            "puedes tender a",
        ),
        (
            r"\bNo parece una persona que\b",
            "Tu manera de funcionar no ",
        ),
        (
            r"\bParece una persona que\b",
            "Tu manera de funcionar ",
        ),
    )

    for patron, reemplazo in sustituciones:
        texto = re.sub(
            patron,
            reemplazo,
            texto,
            flags=re.IGNORECASE,
        )

    return texto


def cargar_guia_estilo_arte_encarnarte():
    """Carga la guía editorial externa. No realiza llamadas a la API."""
    ruta = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "estilo_arte_encarnarte.txt",
    )
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            contenido = f.read().strip()
    except FileNotFoundError:
        raise RuntimeError(
            "Falta estilo_arte_encarnarte.txt junto a interpretacion_arte_encarnarte.py."
        )
    if len(contenido) < 500:
        raise RuntimeError("estilo_arte_encarnarte.txt parece incompleto.")
    return contenido


def corregir_repeticiones_editoriales_local(texto):
    """
    Limpia repeticiones editoriales simples sin llamar a la API.
    No altera el contenido astrológico.
    """
    if not texto:
        return texto

    # Títulos redundantes del tipo "Stellium Stellium (...)"
    texto = re.sub(
        r"\bStellium\s+Stellium\s*\(",
        "Stellium (",
        texto,
        flags=re.IGNORECASE,
    )

    # Repetición obvia: si una misma frase sobre retrogradación aparece
    # inmediatamente dos veces, conservamos una sola.
    frases = re.split(r'(?<=[.!?])\s+', texto)
    limpias = []

    for frase in frases:
        frase_limpia = frase.strip()

        if not frase_limpia:
            continue

        if limpias:
            previa = limpias[-1].strip()

            # Duplicado literal.
            if frase_limpia.casefold() == previa.casefold():
                continue

            # Duplicado casi literal de retrogradación del mismo planeta.
            patron_planeta = r"\b(Saturno|Urano|Neptuno|Plutón)\b"
            planetas_actual = set(
                re.findall(
                    patron_planeta,
                    frase_limpia,
                    flags=re.IGNORECASE,
                )
            )
            planetas_previa = set(
                re.findall(
                    patron_planeta,
                    previa,
                    flags=re.IGNORECASE,
                )
            )

            if (
                "retrógrad" in frase_limpia.casefold()
                and "retrógrad" in previa.casefold()
                and planetas_actual
                and planetas_actual == planetas_previa
            ):
                # Si ambas frases hablan de exactamente el mismo planeta o
                # conjunto y expresan la misma idea de interiorización,
                # evitamos redundancia.
                claves = (
                    "interior",
                    "revis",
                    "elabor",
                    "proces",
                )

                if any(k in frase_limpia.casefold() for k in claves) and any(
                    k in previa.casefold() for k in claves
                ):
                    continue

        limpias.append(frase_limpia)

    return " ".join(limpias)


def corregir_construcciones_poco_naturales_local(texto):
    """
    Corrige únicamente giros sintácticos defectuosos.
    V31 no modifica "pide", "exige", "obliga" ni equivalentes.
    """
    if not texto:
        return texto

    sustituciones = (
        (r"\blo plantea la necesidad de\b", "plantea la necesidad de"),
        (r"\ble plantea la necesidad de\b", "plantea la necesidad de"),
        (r"\blo plantea como una necesidad de\b", "plantea la necesidad de"),
        (r"\ble plantea como una necesidad de\b", "plantea la necesidad de"),
    )

    for patron, reemplazo in sustituciones:
        texto = re.sub(
            patron,
            reemplazo,
            texto,
            flags=re.IGNORECASE,
        )

    return texto


def corregir_genero_dirigido_local(texto):
    """V39: no modifica género; el tratamiento lo resuelve la IA."""
    return texto


def neutralizar_teleologia_editorial_local(texto):
    """V31: teleología fuera del control editorial."""
    return texto


def neutralizar_genero_lector_ampliado_local(texto):
    """V39: no modifica género; el tratamiento lo resuelve la IA."""
    return texto


def cierre_editorial_local_final(texto):
    """
    Última pasada local antes de guardar/maquetar.
    No llama a OpenAI.

    V39:
    - conserva segunda persona;
    - elimina referencias internas;
    - corrige solo cuestiones formales seguras;
    - NO modifica género, concordancia ni terminaciones -a/-o/-e.

    El tratamiento lingüístico ya debe venir resuelto por la IA.
    """
    if not texto:
        return texto

    # V40: primero retiramos cualquier artefacto técnico de citación.
    texto = eliminar_marcadores_citas_internas_local(texto)

    texto = neutralizar_tercera_persona_lector_local(texto)
    texto = eliminar_referencias_internas_fuentes_local(texto)
    texto = corregir_conjunciones_disyuntivas(texto)
    texto = corregir_letras_no_latinas(None, texto)
    texto = asegurar_puntuacion_final_narrativa(texto)

    # Segunda barrera antes de devolver el texto que irá a maquetación.
    texto = eliminar_marcadores_citas_internas_local(texto)

    residuos_citas = detectar_marcadores_citas_internas(texto)
    if residuos_citas:
        raise RuntimeError(
            "Quedan marcadores internos de citación antes de maquetar: "
            + ", ".join(residuos_citas)
        )

    return texto


def detectar_genero_marcado_lector_2026(texto):
    """V36: la validación de género marcado queda sustituida por tratamiento explícito."""
    return []


def detectar_lenguaje_teleologico(texto):
    """V31: teleología fuera del control editorial."""
    return []


def corregir_lenguaje_teleologico(
    client,
    texto,
):
    """V33: la corrección semántica restrictiva queda desactivada."""
    return texto


def neutralizar_teleologia_residual(texto):
    """V31: teleología fuera del control editorial."""
    return texto


def corregir_genero_dirigido_a_lector(
    client,
    texto,
):
    """
    V39 · COMPATIBILIDAD.

    No corrige género ni llama a OpenAI.
    La IA generadora ya recibe el tratamiento lingüístico elegido.
    """
    return texto


def detectar_lenguaje_problematico_figura(texto):
    """V31: no se generan avisos ni correcciones por teleología."""
    return []


def corregir_lenguaje_problematico_figura(
    client,
    texto,
    problemas,
):
    """V33: la corrección semántica restrictiva queda desactivada."""
    return texto


def _construir_dato_figura_para_ia_huber(
    figura,
    aspectos_compactos,
    posiciones_figura,
):
    paquete = figura.get("paquete_huber_ia")

    if paquete:
        # Aunque exista paquete_huber_ia, enviamos SIEMPRE de forma
        # explícita la lista cerrada de puntos y la geometría calculada
        # por Python. El prompt de aislamiento no puede depender de que
        # esos datos estén implícitos dentro del paquete Huber.
        return {
            "id_figura": figura.get("id_figura"),
            "titulo_salida": figura.get("titulo_salida"),
            "tipo": figura.get("tipo"),
            "nombre_canonico": figura.get("nombre_canonico"),
            "puntos": figura.get("puntos", []),
            "puntos_geometricos": figura.get(
                "puntos_geometricos",
                figura.get("puntos", []),
            ),
            "categoria": figura.get("categoria"),
            "consistencia": figura.get("consistencia"),
            "jerarquia": figura.get("jerarquia"),
            "seleccion_huber_2026": figura.get("seleccion_huber_2026"),
            "aspectos_nuevos_huber_2026": figura.get("aspectos_nuevos_huber_2026", []),
            "aspectos_reutilizados_huber_2026": figura.get("aspectos_reutilizados_huber_2026", []),
            "apice": figura.get("apice"),
            "base": figura.get("base"),
            "oposicion": figura.get("oposicion"),
            "vertices": figura.get("vertices", []),
            "componentes": figura.get("componentes", []),
            "relacion_componentes": figura.get(
                "relacion_componentes"
            ),
            "paquete_huber_ia": paquete,
            "familia_editorial_huber_2026": (
                paquete.get("familia_editorial_huber_2026")
                or figura.get("familia_editorial_huber_2026")
            ),
            "variantes_integradas_huber_2026": (
                paquete.get("variantes_integradas_huber_2026")
                or figura.get("variantes_integradas_huber_2026", [])
            ),
            "puntos_editoriales_permitidos": (
                paquete.get("puntos_editoriales_permitidos")
                or figura.get("puntos_editoriales_familia_huber_2026")
                or figura.get("puntos", [])
            ),
            "aspectos": aspectos_compactos,
            "posiciones": posiciones_figura,
        }

    return {
        "id_figura": figura.get("id_figura"),
        "titulo_salida": figura.get("titulo_salida"),
        "tipo": figura.get("tipo"),
        "nombre_canonico": figura.get("nombre_canonico"),
        "familia": figura.get("familia"),
        "colores": figura.get("colores", []),
        "dinamica_base": figura.get("dinamica_base"),
        "secuencia_crecimiento": figura.get(
            "secuencia_crecimiento"
        ),
        "puntos": figura.get("puntos"),
        "puntos_geometricos": figura.get(
            "puntos_geometricos",
            figura.get("puntos", []),
        ),
        "categoria": figura.get("categoria"),
        "consistencia": figura.get("consistencia"),
        "jerarquia": figura.get("jerarquia"),
        "seleccion_huber_2026": figura.get("seleccion_huber_2026"),
        "aspectos_nuevos_huber_2026": figura.get("aspectos_nuevos_huber_2026", []),
        "aspectos_reutilizados_huber_2026": figura.get("aspectos_reutilizados_huber_2026", []),
        "apice": figura.get("apice"),
        "base": figura.get("base"),
        "oposicion": figura.get("oposicion"),
        "vertices": figura.get("vertices", []),
        "componentes": figura.get("componentes", []),
        "relacion_componentes": figura.get(
            "relacion_componentes"
        ),
        "familia_editorial_huber_2026": figura.get(
            "familia_editorial_huber_2026"
        ),
        "variantes_integradas_huber_2026": figura.get(
            "variantes_integradas_huber_2026",
            [],
        ),
        "puntos_editoriales_permitidos": (
            figura.get("puntos_editoriales_familia_huber_2026")
            or figura.get("puntos", [])
        ),
        "aspectos": aspectos_compactos,
        "posiciones": posiciones_figura,
    }

# ─── FIN HUBER FASE 9 ─────────────────────────────────────────────────────────


FASE12_CALIDAD_EDITORIAL_FIGURAS = True


def normalizar_espanol_peninsular_figura(texto):
    """Normaliza formas accidentales de voseo sin reescribir contenido."""
    if not texto:
        return texto

    sustituciones = {
        "intuís": "intuyes",
        "podés": "puedes",
        "tenés": "tienes",
        "querés": "quieres",
        "sentís": "sientes",
        "pensás": "piensas",
        "actuás": "actúas",
        "buscás": "buscas",
        "necesitás": "necesitas",
        "percibís": "percibes",
        "recibís": "recibes",
        "decidís": "decides",
        "elegís": "eliges",
        "vivís": "vives",
        "reaccionás": "reaccionas",
        "encontrás": "encuentras",
        "distinguís": "distingues",
        "permitís": "permites",
        "convertís": "conviertes",
        "sostenés": "sostienes",
        "integrás": "integras",
        "ordenás": "ordenas",
        "ajustás": "ajustas",
        "avanzás": "avanzas",
        "confiás": "confías",
        "observás": "observas",
    }

    for origen, destino in sustituciones.items():
        texto = re.sub(
            rf"(?<!\w){re.escape(origen)}(?!\w)",
            destino,
            texto,
            flags=re.IGNORECASE,
        )

    return texto



# ─── FASE 13: ARQUITECTURA INTERPRETATIVA HUBER ──────────────────────────────
HUBER_FASE13_ARQUITECTURA_INTERPRETATIVA = True


def _nombre_huber_para_perfil(figura, dato):
    paquete = dato.get("paquete_huber_ia") or {}

    return (
        paquete.get("nombre_huber")
        or paquete.get("nombre_canonico")
        or paquete.get("tipo_interno")
        or figura.get("nombre_canonico")
        or figura.get("tipo")
        or ""
    ).strip()


def _perfil_interpretativo_huber(nombre):
    """
    Organiza la narración según la lógica de la figura.
    No añade contenido astrológico nuevo.
    """
    n = (nombre or "").strip().casefold()

    if "talento" in n or n in {
        "gran trígono",
        "cometa",
        "bijou",
        "detect",
        "grabadora",
        "model",
        "represent",
    }:
        return {
            "familia_narrativa": "recurso_talento",
            "orden_sugerido": [
                "facilidad o recurso central",
                "modo concreto de funcionamiento",
                "riesgo de automatismo, exceso o infrautilización",
                "forma de aplicación o canalización",
            ],
            "no_forzar": [
                "una tensión fuerte si la geometría no la contiene",
                "un problema psicológico para justificar el recurso",
            ],
        }

    if "aprendizaje" in n or n in {
        "ojo pequeño",
        "red de aprendizaje",
        "surfista",
        "oscilo",
        "trampolín",
    }:
        return {
            "familia_narrativa": "aprendizaje_reajuste",
            "orden_sugerido": [
                "desajuste o información que rompe la estabilidad",
                "secuencia de respuesta y reajuste",
                "qué se aprende por repetición o contraste",
                "cómo se vuelve más funcional la dinámica",
            ],
            "no_forzar": [
                "una lección moral",
                "una moraleja genérica que no se desprenda de la geometría",
                "un cierre definitivo del proceso",
            ],
        }

    if "ambivalencia" in n or n in {
        "arena",
        "escenario",
    }:
        return {
            "familia_narrativa": "ambivalencia_polaridad",
            "orden_sugerido": [
                "tendencias que operan simultáneamente",
                "forma de oscilación entre ellas",
                "qué ocurre si una domina",
                "criterio que permite sostener la polaridad",
            ],
            "no_forzar": [
                "una solución que elimine uno de los polos",
                "una lectura de bueno frente a malo",
            ],
        }

    if n in {
        "t-cuadrada",
        "cuadrado de rendimiento",
        "triángulo de rendimiento",
        "corredor",
        "corredor (saltador)",
        "amortiguador",
        "provocat",
    }:
        return {
            "familia_narrativa": "presion_rendimiento",
            "orden_sugerido": [
                "dónde se concentra la presión",
                "cómo moviliza respuesta o rendimiento",
                "riesgo de sobrecarga, choque o reacción automática",
                "condición que convierte presión en acción útil",
            ],
            "no_forzar": [
                "que toda presión sea conflicto",
                "que el rendimiento implique éxito garantizado",
            ],
        }

    if n in {
        "yod",
        "figura de proyección",
        "figura de aspiración",
        "megáfono",
        "telescopio-microscopio",
    }:
        return {
            "familia_narrativa": "orientacion_focal",
            "orden_sugerido": [
                "dirección o punto de focalización",
                "información o tensión que converge hacia él",
                "cómo cambia el enfoque",
                "qué permite una orientación más precisa",
            ],
            "no_forzar": [
                "destino",
                "misión",
                "una meta biográfica no contenida en los datos",
            ],
        }

    if n in {
        "bañera",
        "nasa",
        "mariposa",
        "gorro mágico",
        "caja de pandora",
    }:
        return {
            "familia_narrativa": "receptividad_procesamiento",
            "orden_sugerido": [
                "tipo de receptividad o captación",
                "cómo se procesa o retiene la información",
                "riesgo de saturación, pasividad o dispersión",
                "qué favorece una elaboración más diferenciada",
            ],
            "no_forzar": [
                "hipersensibilidad como hecho biográfico",
                "intuición infalible",
                "problemas relacionales no indicados",
            ],
        }

    if n in {
        "canalizador",
        "deco",
        "animat",
        "ovni",
        "escudo",
    }:
        return {
            "familia_narrativa": "direccion_transformacion",
            "orden_sugerido": [
                "función organizadora principal",
                "cómo dirige, filtra, protege o transforma",
                "dónde puede rigidizarse o excederse",
                "cómo conserva movilidad sin perder función",
            ],
            "no_forzar": [
                "control como rasgo personal fijo",
                "conflicto con autoridad sin evidencia",
            ],
        }

    if n == "diamante":
        return {
            "familia_narrativa": "red_compleja",
            "orden_sugerido": [
                "densidad y multiplicidad de conexiones",
                "capacidad de integrar información diversa",
                "riesgo de sobrecarga",
                "criterio de selección y priorización",
            ],
            "no_forzar": [
                "superioridad",
                "genialidad",
                "que toda complejidad sea un recurso",
            ],
        }

    if n == "stellium":
        return {
            "familia_narrativa": "concentracion",
            "orden_sugerido": [
                "funciones concentradas en un núcleo",
                "cómo se refuerzan entre sí",
                "riesgo de falta de distancia interna",
                "modo de discriminar sin romper la cohesión",
            ],
            "no_forzar": [
                "una tensión externa si no existe",
                "que concentración implique conflicto",
            ],
        }

    return {
        "familia_narrativa": "estructura_general",
        "orden_sugerido": [
            "dinámica central",
            "interacción entre componentes",
            "dificultad o exceso solo si existe",
            "recurso o forma de funcionamiento más integrada",
        ],
        "no_forzar": [
            "una tensión si la guía Huber no la contiene",
            "una moraleja o consejo genérico",
        ],
    }


def _reglas_inferencia_figura():
    return {
        "jerarquia_fuentes": [
            "guia_huber y geometria",
            "aspectos reales de la figura",
            "posiciones reales de sus puntos",
            "traduccion simbolica prudente",
        ],
        "reglas": [
            "No nombrar ámbitos concretos sin apoyo de casas, ángulos o posiciones.",
            "No convertir simbolismo planetario en conducta demostrada.",
            "Usar casas como localización simbólica, no como acontecimiento.",
            "No inventar profesión, trauma, conflicto familiar o relación.",
            "Preferir mecanismo estructural cuando una concreción requiera varias inferencias.",
        ],
    }


def _enriquecer_dato_figura_fase13(dato, figura):
    nombre = _nombre_huber_para_perfil(
        figura,
        dato,
    )

    dato = dict(dato)

    dato["perfil_interpretativo"] = (
        _perfil_interpretativo_huber(
            nombre
        )
    )

    dato["auditoria_inferencias"] = (
        _reglas_inferencia_figura()
    )

    return dato

# ─── FIN FASE 13 ──────────────────────────────────────────────────────────────



# ─── FASE 14: CONTRATO INTERPRETATIVO ESPECÍFICO HUBER ───────────────────────
HUBER_FASE14_CONTRATO_ESPECIFICO_46 = True

def _ruta_especifica_desde_guia_huber(dato, figura):
    paquete = dato.get("paquete_huber_ia") or {}
    guia = paquete.get("guia_huber") or {}
    nombre = (
        paquete.get("nombre_huber")
        or paquete.get("nombre_canonico")
        or paquete.get("tipo_interno")
        or figura.get("nombre_canonico")
        or figura.get("tipo")
        or ""
    ).strip()

    campos = (
        ("dinamica_central", "Abrir desde el mecanismo propio de esta figura."),
        ("foco_interpretativo", "Usar el foco solo si la geometría real permite localizarlo."),
        ("potencial", "Presentar como posibilidad estructural, no como capacidad garantizada."),
        ("riesgo", "Presentar como posibilidad, nunca como hecho biográfico."),
        ("clave_integracion", "Usar solo si aporta algo específico; no como consejo genérico."),
    )
    recorrido = []
    for campo, funcion in campos:
        contenido = guia.get(campo)
        if contenido:
            recorrido.append({
                "paso": campo,
                "contenido": contenido,
                "funcion": funcion,
            })

    return {
        "nombre_huber": nombre,
        "tipo_dinamica_huber": guia.get("tipo_dinamica"),
        "forma_huber": guia.get("forma"),
        "familia_color_huber": guia.get("familia_color"),
        "recorrido": recorrido,
        "prioridad": "Prioridad sobre el perfil general de Fase 13.",
        "evitar": [
            "No sustituir la dinámica específica por una plantilla de familia.",
            "No fabricar tensión, conflicto, aprendizaje, talento o sensibilidad.",
            "No usar el riesgo como descripción automática de la persona.",
            "No convertir la clave de integración en un consejo genérico desconectado de la figura.",
            "No inventar roles geométricos ausentes.",
        ],
    }

def _enriquecer_dato_figura_fase14(dato, figura):
    dato = dict(dato)
    contrato = _ruta_especifica_desde_guia_huber(dato, figura)
    if contrato.get("recorrido"):
        dato["contrato_interpretativo_especifico"] = contrato
    return dato
# ─── FIN FASE 14 ──────────────────────────────────────────────────────────────



# ─── FASE 17: AUDITORÍA DE INFERENCIA ESPECÍFICA POR FIGURA ─────────────────
HUBER_FASE17_AUDITORIA_INFERENCIA_FIGURAS = True


def _fase17_contrato_inferencia_figura(dato):
    paquete = dato.get("paquete_huber_ia") or {}
    guia = paquete.get("guia_huber") or {}
    contrato14 = dato.get("contrato_interpretativo_especifico") or {}

    nombre = (
        contrato14.get("nombre_huber")
        or paquete.get("nombre_huber")
        or paquete.get("nombre_canonico")
        or paquete.get("tipo_interno")
        or dato.get("tipo")
        or dato.get("nombre_canonico")
        or ""
    ).strip()

    base = {
        "nombre_huber": nombre,
        "mecanismo_estructural": guia.get("dinamica_central") or "",
        "potencial_estructural": guia.get("potencial") or "",
        "riesgo_estructural": guia.get("riesgo") or "",
        "clave_integracion": guia.get("clave_integracion") or "",
        "foco_interpretativo": guia.get("foco_interpretativo") or "",
        "regla_general": (
            "La figura describe una dinámica simbólica y estructural. "
            "No demuestra que la persona se comporte de una forma concreta "
            "ni que viva acontecimientos específicos."
        ),
        "permitido": [
            "Describir el mecanismo propio de la figura.",
            "Traducirlo a posibilidad funcional con grado de certeza adecuado.",
            "Usar casas y posiciones para localizar, no para probar hechos.",
        ],
        "prohibido": [
            "Convertir conflicto estructural en conflicto real.",
            "Convertir riesgo Huber en conducta habitual.",
            "Afirmar profesión, trauma, pareja, crisis o biografía concreta.",
            "Convertir una propuesta de integración en un mandato moral genérico que no se desprenda de la figura.",
        ],
        "reglas_especificas": [],
    }

    n = nombre.casefold()

    reglas = {
        "arena": {
            "mecanismo": (
                "posiciones contrapuestas, confrontación, lectura de fuerzas "
                "y posibilidad de mediación o negociación"
            ),
            "permitido": [
                "la figura organiza una dinámica de posiciones contrapuestas",
                "puede facilitar la lectura de perspectivas distintas",
                "puede orientar la fricción hacia mediación o acuerdo",
            ],
            "prohibido": [
                "te mete en conflictos",
                "entras en disputas",
                "mides fuerzas con otras personas",
                "buscas conflicto",
            ],
        },
        "provocat": {
            "mecanismo": (
                "detección crítica de lo que no funciona y presión "
                "movilizadora para hacerlo visible"
            ),
            "permitido": [
                "la figura pone el foco en lo que requiere revisión",
                "puede intensificar la percepción de fallos o resistencias",
                "puede movilizar cambios cuando algo queda bloqueado",
            ],
            "prohibido": [
                "provocas a los demás",
                "entras repetidamente en fricción",
                "creas conflictos",
                "ves problemas en todo",
            ],
        },
        "bañera": {
            "mecanismo": (
                "receptividad, captación y procesamiento de información "
                "o estímulos con fuerte componente sensible"
            ),
            "permitido": [
                "estructura especialmente receptiva",
                "puede favorecer una captación amplia de matices",
                "puede requerir diferenciación entre impresión y criterio",
            ],
            "prohibido": [
                "absorbes lo que pasa alrededor",
                "todo te afecta",
                "eres hipersensible",
            ],
        },
        "trampolín": {
            "mecanismo": (
                "reacción ante estímulo, aprendizaje rápido y reajuste "
                "dinámico de la respuesta"
            ),
            "permitido": [
                "puede favorecer rapidez de adaptación",
                "puede describir una secuencia de estímulo y reajuste",
            ],
            "prohibido": [
                "te lanzas y luego corriges",
                "vives en alerta",
                "reaccionas siempre demasiado rápido",
            ],
        },
        "represent": {
            "mecanismo": (
                "hacer visible, representar o sostener una idea, posición "
                "o contenido con presencia"
            ),
            "permitido": [
                "puede favorecer claridad al representar una idea",
                "puede dar forma visible a una posición o contenido",
            ],
            "prohibido": [
                "defiendes causas",
                "te identificas con una causa real",
                "adoptas posturas rígidas como hecho",
            ],
        },
        "bijou": {
            "mecanismo": (
                "comprensión, equilibrio mental, mediación y capacidad "
                "de sostener una posición con sensibilidad al contexto"
            ),
            "permitido": [
                "puede favorecer mediación y comprensión",
                "puede aportar claridad y tacto",
            ],
            "prohibido": [
                "otros se apoyan en ti",
                "cargas con el equilibrio de los demás",
                "eres quien media siempre",
            ],
        },
        "detect": {
            "mecanismo": (
                "captación de señales, detección, selección y actualización "
                "rápida de información"
            ),
            "permitido": [
                "puede favorecer detección de matices",
                "puede facilitar actualización rápida de criterios",
            ],
            "prohibido": [
                "ves cosas que otros no ven",
                "vives pendiente del entorno",
                "estás en hipervigilancia",
                "captas todo",
            ],
        },
        "model": {
            "mecanismo": (
                "modelado, prueba, revisión y reformulación de formas "
                "o representaciones"
            ),
            "permitido": [
                "puede favorecer construir y revisar modelos",
                "puede facilitar aprender mediante prueba y corrección",
            ],
            "prohibido": [
                "perfeccionas todo",
                "procrastinas por perfeccionismo",
                "siempre haces prototipos",
            ],
        },
        "surfista": {
            "mecanismo": (
                "orientación dinámica, lectura de fuerzas y avance "
                "manteniendo percepción del conjunto"
            ),
            "permitido": [
                "puede favorecer orientación rápida",
                "puede facilitar ajustar el rumbo en movimiento",
            ],
            "prohibido": [
                "siempre sabes hacia dónde ir",
                "te precipitas",
                "avanzas sin mirar",
            ],
        },
        "stellium": {
            "mecanismo": "concentración de funciones en un mismo núcleo",
            "permitido": [
                "puede favorecer cohesión entre funciones",
                "puede reducir la distancia interna entre ellas",
            ],
            "prohibido": [
                "reaccionas siempre desde un mismo centro",
                "te cuesta tomar distancia como hecho demostrado",
            ],
        },
    }

    for clave, regla in reglas.items():
        if clave in n:
            base["reglas_especificas"].append(regla)

    if (
        "talento" in n
        or "gran trígono" in n
        or "cometa" in n
    ):
        base["reglas_especificas"].append({
            "mecanismo": "facilidad o recurso disponible dentro de la geometría",
            "permitido": [
                "puede favorecer una capacidad disponible",
                "puede ofrecer una vía relativamente fluida",
            ],
            "prohibido": [
                "tienes talento demostrado para una profesión concreta",
                "eres naturalmente excelente en un ámbito biográfico",
            ],
        })

    if "aprendizaje" in n:
        base["reglas_especificas"].append({
            "mecanismo": "secuencia de contraste, reajuste o repetición estructural",
            "permitido": [
                "puede describir un proceso de reajuste",
                "puede favorecer aprendizaje por contraste",
                "puede plantear algo que necesita aprenderse o trabajarse",
                "puede expresar una exigencia de cambio cuando la geometría lo sostenga",
            ],
            "prohibido": [
                "inventar acontecimientos como si ya hubieran ocurrido",
                "afirmar que siempre se repite la misma situación",
            ],
        })

    return base


def _enriquecer_dato_figura_fase17(dato):
    dato = dict(dato)
    dato["contrato_inferencia_figura"] = (
        _fase17_contrato_inferencia_figura(dato)
    )
    return dato


def auditar_interpretaciones_figuras_fase17(
    client,
    datos_figuras,
    resultado,
):
    contratos_por_id = {}

    for dato in datos_figuras:
        id_figura = (dato.get("id_figura") or "").strip()
        if id_figura:
            contratos_por_id[id_figura] = dato.get(
                "contrato_inferencia_figura",
                {},
            )

    resultado_corregido = {}

    for id_figura, contenido in resultado.items():
        titulo = (
            contenido.get("titulo_humano")
            or ""
        ).strip()

        interpretacion = (
            contenido.get("interpretacion")
            or ""
        ).strip()

        contrato = contratos_por_id.get(
            id_figura,
            {},
        )

        if not interpretacion or not contrato:
            resultado_corregido[id_figura] = contenido
            continue

        prompt = f"""
AUDITORÍA DE INFERENCIA DE FIGURA · FASE 17

Revisa UNA interpretación de figura Huber.

No hagas una nueva interpretación.
No cambies el título.
No añadas astrología.
No cambies la geometría.
No cambies puntos, aspectos, casas ni posiciones.
No resumas ni amplíes.

CONTRATO DE INFERENCIA DE ESTA FIGURA:

{json.dumps(
    contrato,
    ensure_ascii=False,
    indent=2,
)}

REGLA CENTRAL

La figura describe una dinámica estructural o simbólica.
No demuestra que la persona se comporte así ni que viva
situaciones concretas.

No basta con añadir "puede".
Si la frase sigue describiendo una conducta concreta no demostrada,
reformula al nivel del mecanismo.

Ejemplo:
NO:
"Esta figura tiende a meterte en situaciones de choque."

SÍ:
"Esta figura organiza una dinámica de posiciones contrapuestas
y de fricción entre fuerzas que buscan salida."

NO:
"Absorbes lo que pasa alrededor."

SÍ:
"La figura describe una receptividad elevada a estímulos,
matices o información del entorno."

Conserva la especificidad Huber de la figura.
No la vuelvas genérica.

Devuelve únicamente la interpretación corregida,
sin título, Markdown ni explicaciones.

INTERPRETACIÓN ORIGINAL:

{interpretacion}
"""

        response = client.responses.create(
            model="gpt-5.4-mini",
            input=prompt,
        )

        if not response.output_text:
            raise RuntimeError(
                f"OpenAI no ha devuelto texto en la auditoría "
                f"Fase 17 de {id_figura}."
            )

        resultado_corregido[id_figura] = {
            "titulo_humano": titulo,
            "interpretacion": response.output_text.strip(),
        }

    return resultado_corregido

# ─── FIN FASE 17 ──────────────────────────────────────────────────────────────



# ─── FASE 18 · JERARQUÍA EDITORIAL ──────────────────────────────────────────
HUBER_FASE18_JERARQUIA_EDITORIAL = True


def _f18_puntos(figura):
    return {str(x).strip() for x in (figura.get("puntos") or []) if str(x).strip()}


def _f18_familia(figura):
    t = str(figura.get("tipo") or figura.get("nombre_canonico") or "").casefold()
    if "talento" in t or "cometa" in t:
        return "recurso"
    if "aprendizaje" in t or "detect" in t or "ojo" in t:
        return "aprendizaje"
    if "ambivalencia" in t or "oscil" in t:
        return "ambivalencia"
    if "rendimiento" in t or "arena" in t or "provocat" in t:
        return "tension"
    if "bañera" in t or "nasa" in t:
        return "receptividad"
    if "trampol" in t or "surfista" in t:
        return "movimiento"
    if "represent" in t or "model" in t or "escenario" in t:
        return "visibilidad"
    if "stellium" in t:
        return "concentracion"
    if "bijou" in t:
        return "mediacion"
    return "otra"


def _f18_score(figura, rep):
    s = 0.0
    j = str(figura.get("jerarquia") or "").casefold()
    for clave, valor in (("dominante", 25), ("principal", 20), ("alta", 16), ("media", 8), ("secundaria", 6), ("baja", 2)):
        if clave in j:
            s += valor
            break
    c = str(figura.get("consistencia") or "").casefold()
    for clave, valor in (("muy alta", 14), ("alta", 10), ("media", 6), ("baja", 2)):
        if clave in c:
            s += valor
            break
    cat = str(figura.get("categoria") or "").casefold()
    if "central" in cat or "nuclear" in cat:
        s += 10
    s += min(sum(rep.get(p, 0) for p in _f18_puntos(figura)), 24) * 0.55
    if figura.get("paquete_huber_ia") or figura.get("soporte_interpretativo_huber"):
        s += 4
    return s


def seleccionar_figuras_principales_fase18(contexto_compacto, maximo=None):
    """
    Mantiene compatibilidad con la antigua Fase 18.

    En la arquitectura actual, Figuras.py ya entrega únicamente las
    estructuras que deben tener bloque propio. Las variantes que pertenecen
    a una misma familia estructural quedan integradas dentro de su figura
    cabecera y NO vuelven a aparecer como capítulos independientes.
    """
    figuras = list(
        contexto_compacto.get("figuras", {})
        .get("arquitectura", {})
        .get("figuras", [])
        or []
    )

    principales = []
    for orden, figura in enumerate(figuras, 1):
        copia = dict(figura)
        rol = (
            figura.get("seleccion_huber_2026")
            or (figura.get("paquete_huber_ia") or {}).get("seleccion_huber_2026")
            or "principal"
        )
        copia["fase18_editorial"] = {
            "nivel": rol,
            "orden": orden,
            "familia": _f18_familia(figura),
            "regla": (
                "El nivel describe el papel editorial tras la selección geométrica; "
                "no es una jerarquía psicológica."
            ),
        }
        principales.append(copia)

    return {
        "total_detectadas": len(figuras),
        "principales": principales,
        "complementarias": [],
    }

def construir_resumen_editorial_fase18(contexto_compacto):
    seleccion = seleccionar_figuras_principales_fase18(contexto_compacto)
    return {
        "regla": (
            "Cada estructura editorial visible recibe un único bloque. "
            "Las variantes integradas en una familia estructural se explican dentro de su "
            "figura cabecera y no generan bloques independientes."
        ),
        "total_detectadas": seleccion["total_detectadas"],
        "numero_principales": len(seleccion["principales"]),
        "principales": seleccion["principales"],
        "complementarias": [],
    }



# ─── HUBER 2026 · PLAN INTERPRETATIVO POR FIGURA ────────────────────────────
# Esta capa NO detecta figuras y NO cambia geometría. Solo prepara para la IA
# una ruta de lectura profunda, explica el circuito cromático Huber y evita
# repetir como tema principal las mismas líneas cuando varias figuras se solapan.
HUBER_2026_PLAN_INTERPRETATIVO_FIGURAS = True
BIBLIOTECA_ASTROLOGICA_INTEGRADA_2026 = True
ORDEN_EDITORIAL_46_Y_RESCATE_ESTRICTO_2026 = True
PROFUNDIDAD_DIFERENCIAL_STELLIUM_UNICO_CIERRE_LOCAL_2026 = True
CONSISTENCIA_STELLIUM_SIN_BLOQUE_V24 = True
DIVERSIDAD_GLOBAL_PROFUNDIDAD_DIFERENCIAL_V25 = True
GENERO_NEUTRO_DONDE_SE_EXPRESA_V26 = True
VALIDACION_DONDE_SE_EXPRESA_PARRAFO_V27 = True
SIN_BLOQUEO_POST_API_DONDE_SE_EXPRESA_V28 = True
SCHEMA_DONDE_Y_GENERO_NEUTRO_V29 = True
V30_EDITORIAL_LIMPIO = True
V31_REVISION_EDITORIAL_PROFUNDA = True
V32_REPARACION_FIGURAS_INCOMPLETAS_EN_LOTE = True
V33_LIBERTAD_INTERPRETATIVA_Y_GENERO_ROBUSTO = True
V34_RESTAURA_ORDEN_EDITORIAL_46 = True
V35_RESTAURA_SECCION_EDITORIAL_HUBER = True
V36_TRATAMIENTO_LINGUISTICO_EXPLICITO = True
V37_ELECCION_TRATAMIENTO_EN_DATOS = True
V38_PROFUNDIDAD_HUBER_COLORES_Y_SIN_TECHO_RIGIDO = True
V39_TRATAMIENTO_LINGUISTICO_SOLO_IA = True
V40_SANEADO_CITAS_INTERNAS = True
V41_BLINDAJE_COLORES_HUBER = True


def _clave_aspecto_interpretativo_2026(aspecto):
    p1 = str(aspecto.get("p1") or "")
    p2 = str(aspecto.get("p2") or "")
    simbolo = str(aspecto.get("simbolo") or aspecto.get("tipo") or "")
    return (tuple(sorted((p1, p2))), simbolo)


def _claves_huber_serializadas_2026(valor):
    """Normaliza las claves guardadas por Figuras.py a un conjunto comparable."""
    resultado = set()
    for item in valor or []:
        if isinstance(item, (list, tuple)) and len(item) >= 3:
            a, b, simbolo = item[0], item[1], item[2]
            resultado.add((tuple(sorted((str(a), str(b)))), str(simbolo)))
        elif isinstance(item, (list, tuple)) and len(item) == 2:
            extremos, simbolo = item
            if isinstance(extremos, (list, tuple, set, frozenset)) and len(extremos) == 2:
                a, b = list(extremos)
                resultado.add((tuple(sorted((str(a), str(b)))), str(simbolo)))
    return resultado


def _peso_editorial_aspecto_2026(aspecto, nombre_figura=""):
    """Peso SOLO editorial para decidir qué relación explicar primero."""
    simbolo = str(aspecto.get("simbolo") or aspecto.get("tipo") or "")
    tipo = str(aspecto.get("tipo") or aspecto.get("nombre") or "").casefold()
    nombre = str(nombre_figura or "").casefold()

    pesos = {
        "☍": 8.0, "oposición": 8.0, "oposicion": 8.0,
        "□": 6.0, "cuadratura": 6.0,
        "⚻": 5.0, "quincuncio": 5.0,
        "=": 4.5, "conjunción": 4.5, "conjuncion": 4.5,
        "△": 3.5, "trígono": 3.5, "trigono": 3.5,
        "✶": 3.0, "sextil": 3.0,
        "⚺": 2.0, "semisextil": 2.0,
    }
    peso = pesos.get(simbolo, pesos.get(tipo, 1.0))

    # En una Cometa la oposición es el motor geométrico de la figura.
    if "cometa" in nombre and (simbolo == "☍" or "opos" in tipo):
        peso += 20.0

    for punto in (aspecto.get("p1"), aspecto.get("p2")):
        if punto in ("Sol", "Luna"):
            peso += 3.0
        elif punto == "Ascendente":
            peso += 2.0
        elif punto in ("Mercurio", "Venus", "Marte"):
            peso += 1.2
        else:
            peso += 0.5

    try:
        peso += max(0.0, 2.0 - min(float(aspecto.get("orbe") or 9), 2.0))
    except (TypeError, ValueError):
        pass
    return peso


def _relaciones_clave_figura_2026(figura, aspectos_compactos, posiciones_figura):
    nombre = (
        (figura.get("paquete_huber_ia") or {}).get("nombre_huber")
        or figura.get("nombre_canonico")
        or figura.get("tipo")
        or ""
    )
    nuevas = _claves_huber_serializadas_2026(
        figura.get("aspectos_nuevos_huber_2026")
        or (figura.get("paquete_huber_ia") or {}).get("aspectos_nuevos_huber_2026")
    )
    reutilizadas = _claves_huber_serializadas_2026(
        figura.get("aspectos_reutilizados_huber_2026")
        or (figura.get("paquete_huber_ia") or {}).get("aspectos_reutilizados_huber_2026")
    )

    ordenadas = sorted(
        aspectos_compactos,
        key=lambda a: _peso_editorial_aspecto_2026(a, nombre),
        reverse=True,
    )
    relaciones = []
    for asp in ordenadas:
        clave = _clave_aspecto_interpretativo_2026(asp)
        p1, p2 = asp.get("p1"), asp.get("p2")
        relaciones.append({
            "p1": p1,
            "p2": p2,
            "tipo": asp.get("tipo"),
            "simbolo": asp.get("simbolo"),
            "orbe": asp.get("orbe"),
            "estado_en_seleccion": (
                "nueva" if clave in nuevas
                else "reutilizada" if clave in reutilizadas
                else "propia_de_la_geometria"
            ),
            "posicion_p1": posiciones_figura.get(p1, {}),
            "posicion_p2": posiciones_figura.get(p2, {}),
        })

    # No es un ranking psicológico. Es una ruta para que el texto no se disperse.
    return relaciones



def _color_huber_aspecto_2026(aspecto):
    """
    Clasificación determinista del color Huber a partir del aspecto real.
    No interpreta psicológicamente por sí sola.
    """
    simbolo = str(
        aspecto.get("simbolo")
        or ""
    ).strip()

    if simbolo in {"□", "☍"}:
        return "rojo"

    if simbolo in {"△", "✶"}:
        return "azul"

    if simbolo in {"⚻", "⚺"}:
        return "verde"

    if simbolo == "=":
        return "conjuncion"

    return "otro"


def _lectura_colores_huber_2026(aspectos_compactos):
    """
    Prepara para la IA el circuito cromático REAL de la figura.

    Rojo:
        presión, activación, fricción, empuje, conflicto o rendimiento.
    Azul:
        estabilidad, sustancia, facilidad, apoyo, capacidad disponible.
    Verde:
        percepción, búsqueda, pregunta, reajuste, conciencia, información.

    La conjunción se conserva aparte y no se fuerza dentro de rojo/azul/verde.
    """
    funciones = {
        "rojo": (
            "energía de presión, activación o fricción; muestra qué obliga "
            "a moverse, responder, confrontar o producir"
        ),
        "azul": (
            "zona de estabilidad, facilidad, sustancia o capacidad disponible; "
            "muestra qué puede sostener, contener o dar una vía relativamente fluida"
        ),
        "verde": (
            "zona de percepción, pregunta, búsqueda o reajuste; muestra dónde "
            "la figura necesita observar, comprender, diferenciar o cambiar de enfoque"
        ),
        "conjuncion": (
            "concentración de funciones que actúan muy juntas; no se interpreta "
            "como un color Huber rojo/azul/verde"
        ),
        "otro": (
            "relación presente en la geometría sin clasificación cromática Huber "
            "en esta capa"
        ),
    }

    grupos = {
        "rojo": [],
        "azul": [],
        "verde": [],
        "conjuncion": [],
        "otro": [],
    }

    for aspecto in aspectos_compactos or []:
        color = _color_huber_aspecto_2026(aspecto)

        grupos.setdefault(
            color,
            [],
        ).append({
            "p1": aspecto.get("p1"),
            "p2": aspecto.get("p2"),
            "tipo": aspecto.get("tipo"),
            "simbolo": aspecto.get("simbolo"),
            "orbe": aspecto.get("orbe"),
        })

    colores_presentes = [
        color
        for color in ("rojo", "azul", "verde")
        if grupos.get(color)
    ]

    return {
        "colores_presentes": colores_presentes,
        "rojo": {
            "funcion": funciones["rojo"],
            "relaciones": grupos["rojo"],
        },
        "azul": {
            "funcion": funciones["azul"],
            "relaciones": grupos["azul"],
        },
        "verde": {
            "funcion": funciones["verde"],
            "relaciones": grupos["verde"],
        },
        "conjuncion": {
            "funcion": funciones["conjuncion"],
            "relaciones": grupos["conjuncion"],
        },
        "otro": {
            "funcion": funciones["otro"],
            "relaciones": grupos["otro"],
        },
        "regla_interpretativa": (
            "No enumeres colores como una leyenda técnica. Explica qué hacen "
            "dentro de ESTA figura. Si hay rojo, identifica la presión concreta. "
            "Si hay azul, explica el recurso o estabilidad concreta y también su "
            "posible riesgo de comodidad/inercia cuando la guía Huber lo sostenga. "
            "Si hay verde, explica qué pregunta, búsqueda o reajuste introduce. "
            "Después muestra cómo esos colores forman un circuito único. "
            "REGLA FACTUAL: solo puedes llamar rojo, azul o verde a una relación "
            "si ese color aparece en colores_presentes y esa relación está incluida "
            "en la lista correspondiente de esta lectura. Nunca uses un color Huber "
            "como metáfora psicológica si la figura real no contiene ese color."
        ),
    }



def detectar_colores_huber_ajenos_2026(
    texto,
    lectura_colores,
):
    """
    V41 · Control factual de colores Huber.

    Devuelve los colores rojo/azul/verde que la IA menciona
    pero que NO existen entre los aspectos reales de esa figura.

    No interpreta el texto.
    No obliga a mencionar todos los colores presentes.
    Solo impide atribuir un color que la geometría no contiene.
    """
    if not texto:
        return []

    presentes = {
        str(color).strip().casefold()
        for color in (
            (lectura_colores or {}).get(
                "colores_presentes",
                [],
            )
            or []
        )
        if str(color).strip()
    }

    patrones = {
        "rojo": r"\broj(?:o|a|os|as)\b",
        "azul": r"\bazul(?:es)?\b",
        "verde": r"\bverde(?:s)?\b",
    }

    mencionados = {
        color
        for color, patron in patrones.items()
        if re.search(
            patron,
            str(texto),
            flags=re.IGNORECASE,
        )
    }

    return sorted(
        mencionados - presentes
    )


def _profundidad_figura_2026(
    figura,
    aspectos_compactos,
):
    """
    Orientación editorial SEMÁNTICA, no límite de palabras.
    """
    paquete = figura.get("paquete_huber_ia") or {}

    rol = (
        figura.get("seleccion_huber_2026")
        or paquete.get("seleccion_huber_2026")
        or "principal"
    )

    lectura_colores = _lectura_colores_huber_2026(
        aspectos_compactos
    )

    numero_aspectos = len(
        aspectos_compactos or []
    )

    numero_colores = len(
        lectura_colores.get(
            "colores_presentes",
            [],
        )
    )

    vertices = figura.get("vertices", []) or []

    hay_vertice_colectivo = any(
        str(v.get("tipo") or "").casefold()
        in {"stellium", "conjunción", "conjuncion"}
        for v in vertices
        if isinstance(v, dict)
    )

    hay_oposicion = any(
        str(a.get("simbolo") or "") == "☍"
        for a in (aspectos_compactos or [])
    )

    hay_luminaria = any(
        p in {"Sol", "Luna"}
        for a in (aspectos_compactos or [])
        for p in (a.get("p1"), a.get("p2"))
    )

    densidad = 0
    densidad += min(numero_aspectos, 6)
    densidad += numero_colores
    densidad += 2 if hay_vertice_colectivo else 0
    densidad += 2 if hay_oposicion else 0
    densidad += 1 if hay_luminaria else 0

    if rol == "rescate":
        nivel = (
            "profunda"
            if densidad >= 8
            else "media-alta"
        )
        criterio = (
            "Desarrolla con detalle la aportación nueva y explica cómo modifica "
            "el circuito completo. No repitas desde cero las líneas reutilizadas, "
            "pero tampoco reduzcas el bloque a una nota breve."
        )
    elif rol == "complementaria":
        nivel = "media-alta"
        criterio = (
            "Explica la concentración como unidad, sus tensiones internas si las hay, "
            "sus recursos y la forma en que puede actuar como vértice colectivo."
        )
    else:
        nivel = (
            "muy profunda"
            if densidad >= 10
            else "profunda"
        )
        criterio = (
            "Desarrolla el mecanismo completo: presión, recursos, búsquedas, "
            "roles geométricos, signos, casas y relación entre los vértices."
        )

    return {
        "nivel": nivel,
        "criterio": criterio,
        "sin_techo_rigido_de_palabras": True,
        "condicion_de_cierre": (
            "No cierres hasta que se entienda qué pone en marcha la figura, "
            "qué sostiene o canaliza esa presión, qué cambia por signos y casas "
            "y cómo funciona el conjunto como una sola unidad."
        ),
    }


def _plan_editorial_figura_2026(figura, aspectos_compactos, posiciones_figura):
    paquete = figura.get("paquete_huber_ia") or {}

    rol = (
        figura.get("seleccion_huber_2026")
        or paquete.get("seleccion_huber_2026")
        or "principal"
    )

    relaciones = _relaciones_clave_figura_2026(
        figura,
        aspectos_compactos,
        posiciones_figura,
    )

    nombre = (
        paquete.get("nombre_huber")
        or figura.get("nombre_canonico")
        or figura.get("tipo")
        or ""
    )

    lectura_colores = _lectura_colores_huber_2026(
        aspectos_compactos
    )

    profundidad = _profundidad_figura_2026(
        figura,
        aspectos_compactos,
    )

    if rol == "rescate":
        funcion = (
            "Figura de rescate. Su razón de aparecer está en una o varias relaciones "
            "nuevas, pero debes explicar con suficiente profundidad QUÉ cambian esas "
            "relaciones dentro de la figura completa. Las líneas reutilizadas son "
            "contexto, no el tema principal. No conviertas el rescate en una nota breve."
        )
        uso_ejemplo = (
            "Incluye una escena cotidiana solo si ayuda a comprender la aportación nueva. "
            "No sacrifiques explicación astrológica para meter el ejemplo."
        )

    elif rol == "complementaria":
        funcion = (
            "Estructura colectiva de base. Explica la concentración como una unidad, "
            "cómo se combinan sus funciones y qué aporta cuando actúa como vértice "
            "colectivo en otras figuras."
        )
        uso_ejemplo = (
            "El ejemplo es opcional. Prioriza entender la concentración y sus efectos."
        )

    else:
        funcion = (
            "Figura principal de representación geométrica. Desarrolla su mecanismo "
            "completo. Identifica la presión, el recurso, la búsqueda, el movimiento o "
            "la facilidad que realmente existan y explica cómo cooperan entre sí."
        )
        uso_ejemplo = (
            "Incluye una situación cotidiana cuando ayude a encarnar la lectura. "
            "El ejemplo nunca sustituye el análisis de la figura."
        )

    regla_cometa = None

    if "cometa" in nombre.casefold():
        regla_cometa = (
            "La oposición es el motor de la Cometa. Desarróllala con profundidad dentro "
            "de la figura: funciones de ambos extremos, signos, casas y peso de los puntos. "
            "Después explica cómo el resto del gran triángulo aporta sustancia, facilidad, "
            "canalización o estabilidad. No reduzcas la oposición a una frase."
        )

    familia_editorial = (
        paquete.get("familia_editorial_huber_2026")
        or figura.get("familia_editorial_huber_2026")
        or {}
    )

    regla_familia = None

    if familia_editorial:
        nombres_variantes = [
            str(
                v.get("nombre_canonico")
                or v.get("tipo")
                or ""
            ).strip()
            for v in (
                familia_editorial.get(
                    "variantes_integradas"
                )
                or []
            )
            if str(
                v.get("nombre_canonico")
                or v.get("tipo")
                or ""
            ).strip()
        ]

        regla_familia = (
            "Esta figura es la cabecera de una familia estructural. Explica una sola vez "
            "la dinámica compartida y después integra los matices diferenciales de las "
            "variantes"
            + (
                ": " + ", ".join(nombres_variantes)
                if nombres_variantes
                else ""
            )
            + ". No conviertas las variantes en mini-fichas independientes."
        )

    return {
        "rol_seleccion_huber_2026": rol,
        "aclaracion_rol": (
            "principal/rescate/complementaria describe la selección geométrica del motor; "
            "NO es una jerarquía psicológica ni una medida de importancia personal."
        ),
        "funcion_editorial": funcion,

        # V38: ya no existe una horquilla rígida de palabras.
        "extension_orientativa": (
            "SIN LÍMITE RÍGIDO. Desarrolla lo necesario para completar el mecanismo "
            "sin repetir. La profundidad la marca la densidad real de la figura."
        ),
        "profundidad_interpretativa": profundidad,
        "uso_del_ejemplo": uso_ejemplo,

        "lectura_colores_huber_2026": lectura_colores,

        "relaciones_clave_ordenadas": relaciones,
        "relaciones_nuevas_rescate": [
            relacion
            for relacion in relaciones
            if relacion.get(
                "estado_en_seleccion"
            ) == "nueva"
        ],
        "relaciones_reutilizadas_contexto": [
            relacion
            for relacion in relaciones
            if relacion.get(
                "estado_en_seleccion"
            ) == "reutilizada"
        ],

        "regla_rescate_estricta": (
            "Si el rol es rescate, la tesis principal debe proceder de "
            "relaciones_nuevas_rescate. Después explica cómo esa relación cambia "
            "el funcionamiento del conjunto y qué papel ocupa en el circuito de colores. "
            "Las relaciones reutilizadas pueden desarrollarse SOLO lo necesario para "
            "comprender esa modificación. No hay límite de 70-110 palabras."
            if rol == "rescate"
            else None
        ),

        "regla_especifica_cometa": regla_cometa,
        "regla_familia_estructural": regla_familia,
        "familia_editorial_huber_2026": (
            familia_editorial
            or None
        ),

        "regla_signos_casas": (
            "No enumeres signos y casas. Úsalos para modificar el significado de las "
            "relaciones clave: el signo explica CÓMO opera el punto y la casa DÓNDE "
            "adquiere una forma concreta. Integra ambos dentro del mecanismo."
        ),

        "regla_mecanismo_completo": (
            "La interpretación debe distinguir, cuando existan: qué genera presión o "
            "activación; qué aporta estabilidad, facilidad o recurso; qué introduce "
            "búsqueda, sensibilidad o reajuste; y cómo esas partes forman un circuito. "
            "No basta con describir los planetas por separado."
        ),
    }


def _anotar_solapamientos_editoriales_2026(datos_figuras):
    """Añade conciencia de repetición SIN permitir mezclar puntos ajenos."""
    claves_por_id = {}
    for dato in datos_figuras:
        claves_por_id[dato.get("id_figura")] = {
            _clave_aspecto_interpretativo_2026(a)
            for a in (dato.get("aspectos") or [])
        }

    for dato in datos_figuras:
        actual = claves_por_id.get(dato.get("id_figura"), set())
        solapadas = []
        for otro in datos_figuras:
            if otro is dato:
                continue
            compartidas = actual & claves_por_id.get(otro.get("id_figura"), set())
            if compartidas:
                solapadas.append({
                    "id_figura": otro.get("id_figura"),
                    "tipo": otro.get("tipo") or otro.get("nombre_canonico"),
                    "numero_lineas_compartidas": len(compartidas),
                })
        dato["coordinacion_editorial_2026"] = {
            "figuras_con_lineas_compartidas": sorted(
                solapadas,
                key=lambda x: (-x["numero_lineas_compartidas"], str(x["id_figura"])),
            ),
            "regla": (
                "No repitas como idea central una línea ya desarrollada en otra figura. "
                "Si esta figura es rescate, centra el bloque en lo que añade. "
                "Puedes saber que existe solapamiento, pero NO puedes mencionar puntos ajenos."
            ),
        }
    return datos_figuras

# ─── FIN HUBER 2026 · PLAN INTERPRETATIVO ───────────────────────────────────



# ─── STELLIUM · CONTROL DE DUPLICACIÓN EDITORIAL ─────────────────────────────
def _normalizar_conjunto_puntos_editorial(puntos):
    return frozenset(
        str(p).strip()
        for p in (puntos or [])
        if str(p).strip()
    )


def _stellium_ya_representado_como_nucleo(
    figura,
    contexto_compacto,
):
    """
    La figura Stellium sigue existiendo en la arquitectura calculada.
    Solo evitamos un SEGUNDO bloque interpretativo cuando el mismo
    conjunto exacto ya ha sido desarrollado como núcleo global.

    Esto no modifica geometría, selección ni Figuras.py.
    """
    tipo = str(
        figura.get("tipo")
        or figura.get("nombre_canonico")
        or ""
    ).casefold()

    if "stellium" not in tipo:
        return False

    puntos_figura = _normalizar_conjunto_puntos_editorial(
        figura.get("puntos")
    )

    if not puntos_figura:
        return False

    nucleos = (
        contexto_compacto
        .get("figuras", {})
        .get("arquitectura", {})
        .get("nucleos", [])
        or []
    )

    for nucleo in nucleos:
        tipo_nucleo = str(
            nucleo.get("tipo_nucleo")
            or nucleo.get("tipo")
            or ""
        ).casefold()

        if "stellium" not in tipo_nucleo:
            continue

        puntos_nucleo = _normalizar_conjunto_puntos_editorial(
            nucleo.get("puntos_nucleo")
            or nucleo.get("puntos")
        )

        if puntos_nucleo == puntos_figura:
            return True

    return False


def _figuras_con_bloque_independiente(
    figuras,
    contexto_compacto,
):
    """
    Devuelve las figuras que necesitan bloque propio.

    Un Stellium exacto ya explicado como núcleo permanece disponible
    para la lectura global y como vértice colectivo de otras figuras,
    pero no se interpreta dos veces.
    """
    salida = []

    for figura in figuras:
        if _stellium_ya_representado_como_nucleo(
            figura,
            contexto_compacto,
        ):
            continue
        salida.append(figura)

    return salida


# ─── FIN CONTROL STELLIUM ────────────────────────────────────────────────────


def generar_interpretaciones_figuras_estructuradas(
    contexto_compacto,
):
    """
    Genera en UNA sola llamada Structured Output la interpretación
    individual de TODAS las figuras detectadas.

    Python conserva la geometría y los títulos técnicos.
    OpenAI aporta únicamente titulo_humano e interpretacion.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY no está configurada.")

    guia_estilo = cargar_guia_estilo_arte_encarnarte()

    client = OpenAI(api_key=api_key)

    figuras = list(
        contexto_compacto
        .get("figuras", {})
        .get("arquitectura", {})
        .get("figuras", [])
        or []
    )

    if not figuras:
        return {}

    # Conservamos todas las figuras en la arquitectura, pero evitamos
    # generar un segundo bloque para un Stellium ya desarrollado como núcleo.
    figuras = _figuras_con_bloque_independiente(
        figuras,
        contexto_compacto,
    )

    if not figuras:
        return {}

    aspectos_relevantes = (
        contexto_compacto
        .get("figuras", {})
        .get("aspectos_relevantes", [])
    ) or []

    figuras.sort(
        key=lambda figura: orden_editorial_figura_arte_encarnarte(
            figura,
            aspectos_relevantes,
        )
    )

    # El esquema se construye con los bloques que realmente se van a
    # interpretar. La arquitectura completa permanece intacta en contexto_compacto.
    propiedades_schema = {}
    requeridas_schema = []

    for figura_schema in figuras:
        id_schema = str(figura_schema.get("id_figura") or "").strip()
        if not id_schema:
            continue

        propiedades_schema[id_schema] = {
            "type": "object",
            "properties": {
                "titulo_humano": {"type": "string"},
                "interpretacion": {"type": "string"},
            },
            "required": ["titulo_humano", "interpretacion"],
            "additionalProperties": False,
        }
        requeridas_schema.append(id_schema)

    schema = {
        "type": "object",
        "properties": propiedades_schema,
        "required": requeridas_schema,
        "additionalProperties": False,
    }

    posiciones_natales = (
        contexto_compacto
        .get("figuras", {})
        .get("posiciones_natales", {})
    ) or {}

    datos_figuras = []

    for figura in figuras:
        aspectos_figura = Figuras.obtener_aspectos_de_figura(
            figura,
            aspectos_relevantes,
        )

        aspectos_compactos = []
        for aspecto in aspectos_figura:
            aspectos_compactos.append({
                "p1": aspecto.get("p1"),
                "p2": aspecto.get("p2"),
                "tipo": aspecto.get("tipo"),
                "simbolo": aspecto.get("simbolo"),
                "orbe": aspecto.get("orbe"),
                "direccion": aspecto.get("direccion"),
                "desde": aspecto.get("desde", []),
            })

        paquete_figura = figura.get("paquete_huber_ia") or {}
        puntos_editoriales_figura = (
            paquete_figura.get("puntos_editoriales_permitidos")
            or figura.get("puntos_editoriales_familia_huber_2026")
            or figura.get("puntos", [])
            or []
        )

        posiciones_figura = {}
        for punto in puntos_editoriales_figura:
            datos_posicion = posiciones_natales.get(punto)
            if datos_posicion:
                posiciones_figura[punto] = {
                    "signo": datos_posicion.get("signo"),
                    "casa": datos_posicion.get("casa"),
                    "grado": datos_posicion.get("grado"),
                    "retrogrado": datos_posicion.get("retrogrado"),
                }

        dato = _construir_dato_figura_para_ia_huber(
            figura=figura,
            aspectos_compactos=aspectos_compactos,
            posiciones_figura=posiciones_figura,
        )
        dato = _enriquecer_dato_figura_fase13(
            dato,
            figura,
        )
        dato = _enriquecer_dato_figura_fase14(
            dato,
            figura,
        )
        dato = _enriquecer_dato_figura_fase17(
            dato
        )
        dato["plan_interpretativo_huber_2026"] = _plan_editorial_figura_2026(
            figura,
            aspectos_compactos,
            posiciones_figura,
        )
        dato["orden_editorial_arte_encarnarte_2026"] = {
            "posicion": (
                orden_editorial_figura_arte_encarnarte(
                    figura,
                    aspectos_relevantes,
                )[0] + 1
            ),
            "nombre": _nombre_orden_editorial_arte_encarnarte(figura),
            "regla": (
                "Orden editorial del informe: más roce y crecimiento primero; "
                "talentos al final. No es una jerarquía psicológica Huber."
            ),
        }

        # Refuerzo determinista del aislamiento: además de los puntos
        # permitidos, indicamos qué nombres de puntos de ESTA carta
        # están expresamente fuera de la figura.
        puntos_permitidos = {
            str(punto)
            for punto in (
                dato.get("puntos_editoriales_permitidos")
                or puntos_editoriales_figura
                or figura.get("puntos", [])
                or []
            )
        }
        dato["puntos_permitidos"] = sorted(
            puntos_permitidos
        )
        dato["puntos_prohibidos"] = sorted(
            str(punto)
            for punto in posiciones_natales.keys()
            if str(punto) not in puntos_permitidos
        )

        datos_figuras.append(dato)

    datos_figuras = _anotar_solapamientos_editoriales_2026(datos_figuras)

    instrucciones_biblioteca = instrucciones_biblioteca_astrologica(
        "figuras"
    )

    prompt_figuras = f"""
{instrucciones_biblioteca}

────────────────────────────────────────────
GUÍA DE ESTILO OBLIGATORIA
────────────────────────────────────────────

{guia_estilo}

FIN DE LA GUÍA DE ESTILO
────────────────────────────────────────────


Eres la capa de integración astrológica de
ARQUITECTURA INTERNA · EL ARTE DE ENCARNARTE.

Interpreta TODAS las figuras incluidas en DATOS_DE_LAS_FIGURAS.
Debes devolver exactamente un objeto por cada id_figura indicado
por el esquema estructurado.

OBJETIVO

Para cada figura devuelve:
- titulo_humano: un título breve, claro y no técnico;
- interpretacion: con la profundidad indicada en
  plan_interpretativo_huber_2026.profundidad_interpretativa.
  plan_interpretativo_huber_2026.extension_orientativa NO es un techo
  de palabras; desde V38 indica expresamente que no existe un límite rígido.

NO todas las figuras deben ocupar el mismo espacio ni explicar de nuevo
las mismas relaciones. El rol principal/rescate/complementaria es una
herramienta EDITORIAL de representación geométrica, no una jerarquía
psicológica.

ORDEN EDITORIAL OBLIGATORIO

DATOS_DE_LAS_FIGURAS ya está ordenado según el orden editorial maestro
de 46 figuras: primero las configuraciones con más roce/fricción y
potencial de crecimiento; los talentos quedan al final.

Ese orden debe influir también en la coordinación del texto:
- una figura posterior no debe volver a presentar como descubrimiento
  principal una relación ya desarrollada antes;
- principal/rescate NO cambia la posición física de la figura;
- el Stellium complementario queda después de la secuencia de 46 porque
  no forma parte de ese catálogo.

PROFUNDIDAD DIFERENCIAL OBLIGATORIA

Cada figura debe tener una tesis propia.

No basta con cambiar el ejemplo o sustituir un verbo.
Dos figuras diferentes deben explicar DOS mecanismos diferentes cuando
su geometría y sus relaciones sean diferentes.

Antes de redactar cada figura, decide internamente:

1. Qué relación o secuencia es realmente irreductible en esta figura.
2. Qué cambia por los signos concretos de sus puntos.
3. Qué cambia por las casas concretas.
4. Qué cambia por el tipo de puntos implicados:
   luminaria, planeta personal, social, transpersonal, nodo, ángulo
   o punto sensible.
5. Qué aporta esta figura que no está ya explicado en otra anterior.

La biblioteca debe utilizarse para PROFUNDIZAR precisamente en esos
factores concretos. No la uses para recuperar una definición genérica
del nombre de la figura.

CUANDO HAYA DOS EXTREMOS IMPORTANTES

No escribas solo:
"uno impulsa y otro frena".

Explica qué está en juego en cada extremo, cómo cambia por signo y casa
y por qué esa relación tiene un significado particular en ESTA carta.

Por ejemplo, una oposición Sol–Plutón no es simplemente
"impulso frente a intensidad": importa que uno sea una luminaria,
que el otro sea transpersonal, en qué signos están, en qué casas,
y qué función cumplen dentro de la figura que los contiene.

Ese principio es universal. No presupongas Sol–Plutón si no aparece
en la figura real.

PROHIBICIÓN DE HOMOGENEIZAR LAS FIGURAS

No conviertas figuras distintas en versiones de:
"revisar", "ajustar", "medir", "esperar", "corregir", "sostener",
"dar estabilidad" o "pensarlo mejor".

PRESUPUESTO DE REPETICIÓN

En el conjunto de figuras, esas palabras y sus equivalentes no pueden
funcionar como explicación comodín.

Si ya has usado una de esas ideas como tesis de una figura, no la reutilices
como tesis de otra salvo que la segunda añada un mecanismo claramente
diferente y lo explique.

Busca verbos y escenas derivados de las relaciones reales:
confrontar, proteger, exponer, contener, arriesgar, vincular, separar,
intensificar, percibir, transformar, conservar, negociar, investigar,
materializar, pertenecer, independizarse, etc., SOLO cuando correspondan
a los datos concretos.

Esas ideas solo pueden ser centrales cuando la geometría concreta y las
relaciones de ESA figura las justifican.

Antes de escribir cada bloque, formula internamente:
"¿Qué añade esta figura que NO podría decir de la anterior?"

Si la respuesta es prácticamente la misma, busca de nuevo en su geometría,
en sus relaciones nuevas, en sus signos/casas y en la biblioteca hasta
encontrar la diferencia real.

PRUEBA DE INTERCAMBIO:
si dos interpretaciones pudieran intercambiar sus títulos sin que el lector
notara una diferencia clara, al menos una de las dos debe reescribirse.

PRUEBA DE PROFUNDIDAD:
si al quitar los nombres de los planetas el texto podría servir para muchas
cartas, todavía es demasiado genérico. Vuelve a los signos, casas, tipo de
planeta, relación interna y función geométrica hasta obtener una lectura
más específica.

PROFUNDIDAD NO ES INVENTARIO

No consideres profunda una frase solo porque enumera:
"Mercurio en X quiere..., Saturno en Y revisa..., Urano en Z cambia...".

Eso sigue siendo un inventario.

La interpretación profunda debe explicar la RELACIÓN:
qué ocurre cuando esas funciones concretas quedan obligadas a operar
juntas dentro de esa geometría concreta.

Usa signo y casa como modificadores del mecanismo:
- el signo modifica CÓMO opera una función;
- la casa modifica DÓNDE y mediante qué ámbito se vuelve experiencia;
- el tipo de planeta modifica el PESO y la escala de la relación;
- la geometría modifica CÓMO esas funciones quedan conectadas.

No dediques una frase independiente a cada factor si puedes explicar
mejor la interacción entre ellos.

DIFERENCIA ENTRE FIGURAS QUE COMPARTEN VÉRTICES

Cuando varias figuras comparten Stellium, planetas o líneas:
no vuelvas a describir el significado general de esos elementos.

Da por conocido lo ya explicado y responde:
"¿Qué nueva organización produce AQUÍ la combinación concreta?"

El título humano también debe expresar esa diferencia.
Evita títulos intercambiables como:
"Buscar una salida más clara",
"Dar forma a una respuesta",
"Pensar con más medida",
si no nombran una diferencia real del mecanismo.

VARIEDAD DE ESCENAS

No uses "una conversación", "un mensaje", "una respuesta" o
"explicar algo" como ejemplo automático.

Los ejemplos deben salir de las casas y ámbitos reales implicados:
hogar, recursos, trabajo, intimidad, amistades, decisiones materiales,
aprendizaje, exposición pública, rutinas, vínculos, etc., cuando esos
ámbitos estén respaldados por los datos.

No hace falta incluir ejemplo en todos los bloques.

PRUEBA DE BIBLIOTECA:
el conocimiento recuperado debe cambiar o afinar la interpretación.
Si solo confirma una frase genérica que ya podrías haber escrito sin
consultar los libros, profundiza de nuevo.

La lectura debe:
1. encontrar UNA idea humana central propia de esa figura;
2. desarrollar con profundidad la relación o secuencia que realmente
   organiza su geometría;
3. integrar signos y casas DENTRO de esa relación, no como inventario;
4. mostrar una manifestación cotidiana solo cuando ayude a entenderla;
5. explicar qué aportan las demás partes de la figura a la relación central;
6. evitar repetir una línea ya explicada como tema principal en otra figura.

EN UNA FIGURA DE RESCATE

No interpretes de nuevo la figura completa.

Usa obligatoriamente:
plan_interpretativo_huber_2026.relaciones_nuevas_rescate

como foco del bloque.

Si contiene UNA sola relación nueva:
- esa relación es la razón de existir del bloque;
- explica qué añade esa relación a lo ya contado;
- las relaciones reutilizadas solo sirven para situarla;
- no vuelvas a recorrer todos los vértices;
- no vuelvas a explicar el Stellium si ya funciona como vértice conocido;
- no cierres con el mismo consejo que una figura anterior.

El lector debería poder terminar el bloque pensando:
"Ahora entiendo qué pieza nueva añade esta figura."

En un rescate con UNA sola línea nueva:
- explica esa relación nueva;
- precisa qué cambia por los signos y casas de sus dos extremos;
- explica en una sola frase cómo se apoya en la figura ya conocida;
- termina.

No vuelvas a describir uno por uno los demás vértices reutilizados.

La extensión de rescate es deliberadamente menor.

FUENTES AUTORITATIVAS

Si existe paquete_huber_ia:
- usa paquete_huber_ia.guia_huber como marco principal;
- respeta sus puntos y roles geométricos;
- no reasignes ápice, base, oposición, vértices ni subfiguras;
- las subfiguras integradas son contexto interno, no bloques independientes.

Respeta también:
- plan_interpretativo_huber_2026;
- coordinacion_editorial_2026;
- contrato_interpretativo_especifico;
- contrato_inferencia_figura;
- perfil_interpretativo;
- aspectos reales;
- posiciones reales de los puntos de ESA figura.

PROFUNDIDAD ASTROLÓGICA OBLIGATORIA

No basta con describir la personalidad general de los puntos. Lee la
RELACIÓN concreta entre ellos dentro de la figura.

Cuando plan_interpretativo_huber_2026.relaciones_clave_ordenadas identifique
una relación central:
- explica primero qué funciones pone en contacto;
- usa signo y casa de AMBOS extremos para precisar cómo y dónde se expresa;
- considera si uno de los extremos es luminaria, Ascendente, planeta personal,
  social, transpersonal, nodo o punto sensible;
- explica qué cambia porque esa relación forma parte de ESTA figura y no es
  un aspecto aislado;
- después muestra cómo los otros vértices modifican, canalizan o contienen
  esa relación.

No escribas cuatro miniinterpretaciones planeta por planeta. La unidad de
lectura sigue siendo la figura.

COMETAS

Si plan_interpretativo_huber_2026.regla_especifica_cometa contiene texto,
síguelo de forma obligatoria. La oposición debe recibir desarrollo real.
No basta con nombrarla en una frase. En particular, si una luminaria está
en uno de sus extremos, explica qué función básica de identidad o respuesta
vital entra en tensión con el otro extremo, matizada por signo y casa.
Después explica cómo el gran triángulo cambia la forma de vivir esa oposición.
La oposición NO se interpreta aparte: se comprende dentro de la Cometa.


ÚLTIMA PASADA EDITORIAL

El cuerpo del informe no debe parecer una clase de astrología.

TECNICISMOS
No nombres cuadratura, trígono, sextil, quincuncio, semisextil u
oposición salvo que sea imprescindible para entender la idea.
La geometría ya está calculada por Python.

Explica primero la experiencia humana. Si el aspecto técnico aporta algo,
menciónalo después. El párrafo debe entenderse aunque se elimine esa
frase técnica.

FRASES
Prefiere frases de 8 a 18 palabras.
Una idea por frase.
Si una frase contiene tres ideas, divídela.
Evita encadenar más de dos comas.

CIERRES
No cierres todas las figuras con fórmulas como:
"la figura funciona mejor", "la forma de encajarlo mejora",
"integrada", "se expresa mejor" o "el recurso está".

Puedes terminar con el ejemplo, con algo concreto que puede ayudar,
con una consecuencia cotidiana o simplemente cuando la idea ya esté
clara. No fuerces una moraleja final.

La dirección Huber sirve para decidir cómo explicar la figura.
No la conviertas en una demostración técnica para quien lee.

Si la dirección Huber añade información, intégrala DENTRO de la misma
idea humana central. No abras una segunda interpretación aparte.

PRIORIDAD ABSOLUTA: QUE SE ENTIENDA

La dirección Huber es información técnica de apoyo. No puede volver
el texto más difícil.

Primero explica qué puede notar la persona en su vida.
Después pon un ejemplo cotidiano.
Solo al final, si aporta claridad, menciona la dirección de la figura.

Nunca abras una interpretación con palabras como:
"dirección funcional", "eje", "ápice", "vértice de salida",
"secuencia geométrica" o "descarga".

Traduce primero ese dato a lenguaje humano.

DIRECCIÓN Y ROLES GEOMÉTRICOS HUBER

El campo "roles_geometricos" puede incluir:
"direccion_huber_calculada".

Esa información ha sido calculada por Python a partir de la geometría
real de la figura.

Si existe "direccion_huber_calculada":
- úsala obligatoriamente;
- tradúcela primero a una experiencia humana concreta;
- incluye un ejemplo cotidiano breve que muestre esa dirección;
- explica con palabras sencillas hacia dónde se concentra, sale,
  regula o se desplaza la figura;
- da especial importancia al ápice, vértice de salida, eje de oposición
  o secuencia geométrica cuando estén presentes;
- relaciona esos puntos con su signo/casa solo si los datos están
  disponibles;
- no inventes una dirección distinta;
- no confundas esta dirección Huber con el campo "direccion" de un
  aspecto individual, que solo describe el orbe.

Si NO existe "direccion_huber_calculada":
- no inventes sentido de giro, cabeza, cola, eje, ápice ni dirección;
- interpreta únicamente los datos geométricos disponibles.

IMPORTANTE:
Python puede proporcionar una "secuencia_geometrica" sin asignarle
todavía un significado psicológico de giro horario/antihorario.
En ese caso describe la secuencia funcional indicada, pero NO inventes
la etiqueta "reconocimiento" o "experiencia" si Python no la ha dado.

STELLIUMS Y CONJUNCIONES COMO VÉRTICES COLECTIVOS

Cuando "vertices" contenga un elemento con tipo "Stellium" o
"Conjunción", ese vértice se interpreta como UNA UNIDAD.

No reduzcas el vértice al planeta concreto que permitió detectar
geométricamente la figura.

Ejemplo:
si el vértice es:
Stellium [Mercurio, Venus, Marte, Nodo Sur]

no interpretes Venus como si estuviera sola.
Explica cómo Mercurio, Venus, Marte y Nodo Sur forman juntos
ese vértice de la figura.

"puntos_geometricos" conserva la geometría técnica original.
"puntos" y "vertices" indican todo lo que debe entrar en la
interpretación.

Si varios miembros del mismo stellium permiten detectar la misma
figura, el resultado debe seguir siendo UNA sola figura colectiva,
no varias figuras separadas.

REGLA NARRATIVA OBLIGATORIA

Si existe un vértice colectivo, la interpretación debe PARTIR de ese
vértice colectivo.

No abras la explicación reconstruyendo la figura desde el planeta
representante geométrico.

Incorrecto:
"Venus, Urano, Neptuno y Nodo Norte forman..."

si Venus está dentro de:
Stellium (Mercurio + Venus + Marte + Nodo Sur).

Correcto:
"El stellium de Mercurio, Venus, Marte y Nodo Sur entra en relación
con Urano, Neptuno y Nodo Norte..."

o una formulación humana equivalente.

La persona debe entender primero qué aporta el bloque completo y solo
después, si hace falta, qué papel concreto tiene uno de sus integrantes.

Haz lo mismo con las conjunciones colectivas:
Luna + Urano + Medio Cielo se explica primero como una unidad, no
como Luna sola, Urano solo o Medio Cielo solo.

El Stellium, cuando aparezca como figura propia, recibe también
su bloque individual. Debe explicarse como una concentración
importante de la carta, no como una nota secundaria.


REGLA GENERAL DE UNIVERSALIDAD PARA LAS FIGURAS

Estas instrucciones deben funcionar con cualquier carta natal.

No presupongas rapidez, sensibilidad, conflicto, vínculo, control,
intensidad, creatividad, dificultad, aprendizaje, profundidad ni ningún
otro rasgo porque haya aparecido en cartas usadas durante el desarrollo.

Python aporta la geometría y los datos de la carta concreta.
La IA traduce SOLO esos datos a una experiencia humana comprensible.


AISLAMIENTO ESTRICTO

Cada figura se interpreta con aislamiento ASTROLÓGICO: solo puede usar sus
propios puntos y datos. Pero la redacción debe estar COORDINADA editorialmente
con las demás figuras para no repetir el mismo aspecto o la misma idea central.

Cada figura se interpreta exclusivamente con los puntos incluidos en ella.

Para CADA figura:
- "puntos_permitidos" es la lista cerrada de nombres que sí puedes mencionar;
  cuando exista una familia estructural, esta lista incluye también los puntos
  de sus variantes integradas porque forman parte del MISMO bloque editorial;
- "puntos_prohibidos" contiene nombres presentes en la carta que NO pertenecen
  a esa figura y que NO deben aparecer ni en titulo_humano ni en interpretacion.

No menciones ningún planeta, ángulo, nodo o punto fuera de
"puntos_permitidos". No mezcles información de otras figuras de la carta.
Antes de devolver cada objeto, comprueba literalmente que ninguno de los
nombres de "puntos_prohibidos" aparece en sus dos campos de salida.

No inventes aspectos, casas, relaciones, profesiones, acontecimientos,
traumas, pareja, historia familiar ni conductas habituales.

GEOMETRÍA

Cuando existan campos apice, base u oposicion, son autoritativos.
En una T-cuadrada, el ápice recibe las dos cuadraturas y los otros dos
puntos forman la oposición.
En un Yod, el ápice recibe los dos quincuncios y la base es el sextil.
No llames centro, vértice, ápice, base u oposición a otro punto.

NODOS

Nodo Norte y Nodo Sur forman un eje de desarrollo y contraste.
Puedes hablar de dirección, aprendizaje, insistencia o exigencia cuando
la geometría y el resto de la carta lo sostengan. No los conviertas en
una predicción biográfica inevitable ni en un resultado garantizado.

RETROGRADACIÓN

En "posiciones", el campo "retrogrado": true es autoritativo.
Si un planeta de ESTA figura está retrógrado, puedes integrar ese matiz
como interiorización, revisión o reelaboración de su función cuando sea
relevante para la dinámica concreta. No lo conviertas en bloqueo,
incapacidad, karma, retraso ni hecho biográfico. No menciones
retrogradaciones de puntos que no pertenezcan a esta figura.

LENGUAJE

Escribe siempre en segunda persona y en español de España.
No hables de quien recibe el informe como "esta persona",
"la persona" o "parece una persona que...".

{instruccion_tratamiento_linguistico()}

RECORDATORIO DE CONCORDANCIA PARA FIGURAS

No conviertas a -e un adjetivo porque aparezca cerca de "te", "tu" o "ti".
Primero identifica qué palabra modifica.

Ejemplos:
"la respuesta queda concentrada"
"la energía está orientada"
"la figura está integrada"
"puedes quedarte concentrade"
"puedes sentirte orientade"

Solo los dos últimos ejemplos describen directamente a quien lee.

Nunca menciones la biblioteca, los libros, File Search, autores,
fuentes, documentos consultados ni material recuperado.
Ese apoyo es interno y debe ser invisible en el informe final.

No copies ni reproduzcas marcadores técnicos de citación como
"filecite", "cite", "turn0file1", "turn0search1" ni equivalentes.
Esos identificadores son internos y no forman parte del informe.

No hay una lista de verbos prohibidos.

Puedes escribir "la figura pide", "la dinámica exige", "obliga a revisar",
"necesita aprender", "te pide", "te exige" o expresiones equivalentes
cuando traduzcan de forma precisa el trabajo interno de la configuración.

No cambies esas expresiones automáticamente por frases impersonales.

También puedes hablar directamente en segunda persona cuando la evidencia
sea suficiente. Ajusta el grado de certeza a los datos reales.

Evita únicamente:
- inventar biografía, acontecimientos o conductas que no están en los datos;
- convertir una tendencia en un absoluto inmutable;
- moralizar;
- garantizar talento, éxito, fracaso o un resultado vital.

No cierres con consejos genéricos ni ofertas conversacionales.

STELLIUM

Si el tipo es "Stellium":
- explica que varias funciones están concentradas y actúan juntas;
- nombra sus integrantes;
- explica qué aporta cada uno sin separarlos en cuatro lecturas;
- usa casa y signo cuando estén disponibles;
- explica que otras figuras pueden apoyarse en este stellium como
  vértice colectivo.



CONTROL FINAL DE NATURALIDAD

Antes de devolver cada sección global y cada figura, haz una última
lectura exclusivamente lingüística.

Corrige cualquier frase que:
- sea gramaticalmente extraña;
- parezca incompleta;
- tenga palabras colocadas en un orden poco natural;
- necesite releerse para entenderla;
- use una abstracción cuando existe una expresión cotidiana más clara.

No cambies la interpretación astrológica durante esta revisión.

VOCABULARIO COTIDIANO

En el texto dirigido a la persona evita, siempre que exista una forma
más sencilla de decirlo:
"masa funcional",
"campo denso",
"zona densa",
"regulación",
"absorción",
"arquitectura entera",
"arquitectura central",
"función organizadora",
"proyección",
"integración",
"reelaboración",
"interiorización".

No hagas sustituciones mecánicas si empeoran la frase. Reescribe la
oración completa con naturalidad.

Por ejemplo, según el contexto:
"actúan como una sola masa funcional"
puede expresarse como
"tienden a activarse juntas".

"una de las zonas más densas"
puede expresarse como
"una de las zonas más intensas".

"se regula mejor"
puede expresarse como
"te resulta más fácil manejarlo".

Los ejemplos anteriores muestran ESTILO, no contenido astrológico.

SEGUNDO PÁRRAFO DE LAS FIGURAS

Después de que la idea y el ejemplo estén claros, no hagas un inventario
de planetas.

Menciona solo los elementos astrológicos necesarios para explicar por qué
la figura funciona así. Si cuatro puntos pueden resumirse en dos frases,
no escribas cuatro frases independientes.

La astrología debe sostener la explicación, no volver a complicarla.

PROHIBICIÓN DE FRASES DE RELLENO

Elimina frases defensivas o aclaraciones que no aporten información
concreta, por ejemplo fórmulas del tipo:
"esto no significa que tengas que vivir así",
"la figura no plantea la necesidad de...",
"no se trata de X por X".

Conserva una aclaración de este tipo únicamente cuando evite de verdad
una interpretación equivocada.

PRUEBA DE ATERRIZAJE

Al terminar, una persona debe poder responder:
"¿Qué significa esto en una situación normal de mi vida?"

Si no puede hacerlo después de una sola lectura, simplifica otra vez.


USO DE LA GUÍA DE ESTILO

La guía contiene ejemplos de REDACCIÓN, no contenido astrológico.
Aprende de ella claridad, concreción, referentes claros, escenas cotidianas y ritmo de frase.
La carta actual manda siempre sobre el contenido.
No copies una situación de ejemplo si los datos de la carta no la justifican.


REGLA DE REDACCIÓN DESPUÉS DEL EJEMPLO

Una vez que la idea central y la situación cotidiana se entienden:

- no enumeres la función de cada planeta;
- agrupa los puntos que trabajan juntos;
- menciona solo los elementos necesarios para justificar la dinámica;
- no vuelvas a complicar lo que ya se ha entendido.

DIRECCIÓN HUBER

La dirección calculada por Python debe utilizarse para construir la
interpretación, pero no debe aparecer como una fórmula técnica aislada.

Nunca escribas sin traducción frases del tipo:
"la dirección funcional va de X a Y",
"el movimiento se concentra en el ápice",
"el eje descarga sobre...".

Convierte primero ese dato en una consecuencia humana concreta.
Si la traducción ya transmite correctamente la dirección, no es obligatorio
mostrar después la fórmula técnica.

REFERENTES CLAROS

No uses "lo", "eso", "aquello", "la notas", "lo viable" o expresiones
similares cuando el referente pueda resultar ambiguo.

Prefiere repetir el sustantivo o nombrar la acción concreta.
La claridad tiene prioridad sobre evitar una pequeña repetición.


MÉTODO DE PROFUNDIDAD PARA CADA FIGURA · V38

Esta sección tiene PRIORIDAD sobre cualquier instrucción anterior que
pueda empujar a resumir demasiado, limitar el número de párrafos,
reducir la figura a una sola frase o convertir la astrología en un
simple ejemplo cotidiano.

OBJETIVO CENTRAL

La persona debe entender DOS cosas a la vez:

1. qué puede significar esta figura en su vida cotidiana;
2. POR QUÉ la figura funciona así astrológicamente.

Lenguaje sencillo NO significa interpretación sencilla.

No reduzcas una figura compleja a:
"te pasa X y te ayuda Y".

No basta con que el texto sea reconocible.
Tiene que revelar la lógica interna de la figura.

NO HAY TECHO RÍGIDO DE PALABRAS

Ignora cualquier antigua horquilla como:
70-110, 140-200 o 180-260 palabras.

No escribas por llenar espacio, pero tampoco cierres una interpretación
porque ya haya un ejemplo o dos párrafos.

La extensión termina cuando se han explicado las capas necesarias.
Una figura compleja puede necesitar bastante más desarrollo que una simple.

CRITERIO DE CIERRE

Antes de cerrar una figura comprueba si ya se entiende:

- qué la pone en marcha;
- dónde está la tensión, presión, contradicción, facilidad o búsqueda;
- qué relaciones hacen ese trabajo;
- qué aportan los otros vértices;
- qué cambia por los signos;
- qué cambia por las casas;
- qué peso tiene el tipo de punto implicado;
- qué función cumple cada color Huber presente;
- cómo se enlazan los colores en un solo circuito;
- qué cambia cuando la figura funciona de una manera poco integrada
  y cuando sus partes empiezan a cooperar.

No hace falta forzar todos estos apartados si la figura no los contiene.
Pero no omitas una capa importante solo para ser breve.

LECTURA CROMÁTICA HUBER OBLIGATORIA

Cada dato incluye:

plan_interpretativo_huber_2026.lectura_colores_huber_2026

Usa esa información de forma explícita en el razonamiento.

REGLA FACTUAL ESTRICTA DE COLOR

Los colores NO se deducen por significado psicológico ni por memoria.
Los determina Python a partir de los aspectos reales de ESA figura.

Solo puedes usar las palabras rojo, azul o verde como colores Huber
si aparecen en:
plan_interpretativo_huber_2026.lectura_colores_huber_2026.colores_presentes

Y solo puedes atribuir ese color a las relaciones incluidas en la lista
rojo.relaciones / azul.relaciones / verde.relaciones correspondiente.

Si "verde" no está presente, no llames verde a ninguna relación aunque
su función te parezca de ajuste, búsqueda o sensibilidad.
Lo mismo vale para rojo y azul.

No conviertas una función psicológica en un color geométrico inexistente.

ROJO
Cuando haya líneas rojas, identifica qué presión, activación, choque,
exigencia o necesidad de actuar generan EN ESTA FIGURA.

No digas solo "hay tensión".
Explica entre qué funciones, cómo se manifiesta esa fricción y qué pone
en movimiento.

AZUL
Cuando haya líneas azules, explica qué capacidad, estabilidad, facilidad,
sustancia o apoyo ofrecen.

No las presentes como "algo bueno".
Aclara qué pueden sostener, contener o canalizar y, cuando la guía Huber
lo permita, qué riesgo existe si la persona se refugia demasiado en esa
facilidad.

VERDE
Cuando haya líneas verdes, explica qué pregunta, sensibilidad, búsqueda,
duda, percepción o necesidad de reajuste introducen.

No las reduzcas a "hay que revisar".
Explica QUÉ necesita ser comprendido, diferenciado o replanteado.

CIRCUITO
Después relaciona los colores.

Ejemplos de estructura lógica, NO de contenido para copiar:
- la presión roja activa una búsqueda verde y encuentra apoyo en una zona azul;
- una facilidad azul es cuestionada por una línea verde y acaba movilizando
  una respuesta roja;
- la oposición roja pone en marcha recursos azules que, sin esa presión,
  podrían permanecer demasiado cómodos.

La figura se interpreta como un circuito, no como una colección de colores.

IMPORTANTE

No hace falta escribir literalmente:
"rojo", "azul" y "verde" en todas las figuras.

Puedes decir:
"la tensión está aquí...",
"el recurso está aquí...",
"la parte que obliga a buscar otra respuesta está aquí...".

Pero cuando nombrar los colores ayude a entender la miniatura o la
arquitectura de la figura, puedes hacerlo de forma natural:

"Las líneas rojas concentran la presión..."
"Los aspectos azules aportan..."
"Las líneas verdes introducen..."

La persona puede ver esos colores en el dibujo, así que explicarlos puede
hacer que la imagen cobre sentido.

RELACIONES IMPORTANTES

No trates una oposición, cuadratura, quincuncio, trígono o sextil importante
como un detalle secundario.

Si una relación es el motor geométrico de la figura, dale espacio real.

Por ejemplo, una oposición que involucra una luminaria y un planeta
transpersonal puede necesitar varios párrafos para explicar:
- qué funciones enfrenta;
- qué cambian sus signos;
- qué cambian sus casas;
- qué escala tiene cada extremo;
- cómo el resto de la figura modifica esa oposición.

Ese principio es universal. Usa únicamente los datos reales de la figura.

SIGNOS Y CASAS

No escribas un inventario:
"X está en Aries casa 2; Y en Libra casa 8."

Explica qué cambia.

Ejemplo de forma:
"El extremo que intenta afirmarse lo hace desde un signo que empuja a actuar
y en una casa ligada a valor y recursos. El otro extremo introduce una
fuerza relacional y transformadora en un territorio de intercambio profundo."

El ejemplo anterior NO autoriza esos signos o casas en otra carta.

TIPO DE PUNTO

Distingue la escala de lo que entra en relación.

No pesa igual:
- una luminaria;
- un planeta personal;
- un planeta social;
- un transpersonal;
- un nodo;
- un ángulo;
- Quirón o Lilith.

No conviertas esto en teoría.
Úsalo para explicar por qué una relación puede sentirse más básica,
más personal, más colectiva o más profunda.

VÉRTICES COLECTIVOS

Si hay Stellium o conjunción como vértice:
- parte del bloque colectivo;
- explica cómo sus funciones llegan juntas a la relación;
- después, si una arista concreta usa especialmente uno de sus miembros,
  puedes precisar ese papel sin romper la unidad.

No reduzcas el vértice colectivo al planeta que permitió detectar la línea.

FIGURAS DE RESCATE

Una figura de rescate NO debe repetir toda la interpretación anterior,
pero tampoco debe quedar reducida a 70-110 palabras.

La relación nueva es el centro.
Después explica:
- qué función cumple esa nueva línea;
- qué color Huber tiene y qué añade al circuito;
- cómo cambia la figura al conectarse con líneas ya conocidas;
- qué matiz aportan signo y casa de sus extremos.

Las líneas reutilizadas pueden recordarse brevemente para que el cambio
se entienda.

El bloque debe responder:
"¿Qué añade esta figura que todavía no estaba explicado?"

PROFUNDIDAD VS. REPETICIÓN

Profundizar NO es repetir.

Puedes dedicar más espacio a una figura sin volver a explicar:
- el significado general de un Stellium;
- un aspecto ya desarrollado en otra figura;
- una misma conclusión sobre vínculo, ritmo, límites o revisión.

Cuando algo ya está explicado, úsalo como base:
"Sobre esa tensión ya conocida aparece ahora..."
"Esta figura añade..."
"Lo nuevo aquí es..."

Pero no conviertas cada rescate en una frase telegráfica.

EJEMPLOS COTIDIANOS

El ejemplo es una herramienta, no una obligación mecánica.

Inclúyelo cuando ayude a encarnar la lectura.
Puede aparecer al principio, en medio o al final.

No sacrifiques una explicación astrológica importante para mantener
la figura en dos párrafos.

No uses siempre conversaciones, mensajes o respuestas.
Deja que las casas orienten la escena cuando sea posible.

FORMA DEL TEXTO

No existe un número obligatorio de párrafos.

Una figura puede necesitar:
- 2 párrafos si es sencilla;
- 3 o 4 si necesita separar presión, recursos y funcionamiento;
- más si la geometría es especialmente densa.

Mantén frases claras y párrafos respirables, pero permite desarrollar
una idea compleja paso a paso.

UNA FIGURA PUEDE TENER MÁS DE UNA CAPA

La tesis central debe ser reconocible, pero no borres matices importantes.

Puedes desarrollar, cuando existan:
- conflicto central;
- recurso real;
- punto de búsqueda;
- riesgo de una solución parcial;
- dirección Huber;
- diferencia entre expresión poco integrada e integrada.

Todas esas capas deben pertenecer a la MISMA figura y quedar conectadas.

PRUEBA FINAL DE PROFUNDIDAD

Antes de devolver cada interpretación, comprueba:

1. ¿He explicado el mecanismo o solo he descrito a la persona?
2. ¿Se entiende qué hace cada color presente?
3. ¿He explicado qué cambia por signos y casas?
4. ¿Hay alguna relación importante despachada en una sola frase?
5. ¿El recurso azul está explicado como función y no como adjetivo positivo?
6. ¿La tensión roja está desarrollada y no solo nombrada?
7. ¿La parte verde, si existe, muestra qué obliga a buscar o reajustar?
8. ¿Se entiende cómo todas esas partes trabajan juntas?
9. ¿Podría esta interpretación pertenecer a otra carta si cambio los nombres?
   Si la respuesta es sí, profundiza.
10. ¿He cerrado porque la idea está completa o simplemente porque el texto
    ya parecía suficientemente corto?

Solo devuelve la figura cuando la respuesta sea satisfactoria.

No copies literalmente la guía Huber.
No recorras aspectos como una lista técnica.
Traduce la geometría, pero NO escondas la astrología hasta volverla superficial.


DATOS_DE_LAS_FIGURAS:

{json.dumps(datos_figuras, ensure_ascii=False, indent=2)}
"""

    print("Generando interpretaciones estructuradas de figuras...")

    vector_store_id = cargar_vector_store_biblioteca_astrologica()

    response = client.responses.create(
        model="gpt-5.4-mini",
        input=prompt_figuras,
        tools=[
            herramienta_file_search_biblioteca_astrologica(
                vector_store_id,
                max_num_results=30,
            )
        ],
        max_output_tokens=30000,
        text={
            "format": {
                "type": "json_schema",
                "name": "interpretaciones_figuras",
                "strict": True,
                "schema": schema,
            }
        },
    )

    if not response.output_text:
        raise RuntimeError(
            "OpenAI no ha devuelto las interpretaciones estructuradas de figuras."
        )

    try:
        resultado = json.loads(
            response.output_text
        )
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "La respuesta estructurada de figuras no contiene JSON válido."
        ) from exc

    ids_esperados = [
        (figura.get("id_figura") or "").strip()
        for figura in figuras
        if (figura.get("id_figura") or "").strip()
    ]

    faltantes = [
        id_figura
        for id_figura in ids_esperados
        if id_figura not in resultado
    ]
    extras = [
        id_figura
        for id_figura in resultado
        if id_figura not in ids_esperados
    ]

    if faltantes or extras:
        detalle = []
        if faltantes:
            detalle.append("faltan: " + ", ".join(faltantes))
        if extras:
            detalle.append("sobran: " + ", ".join(extras))
        raise RuntimeError(
            "La respuesta de figuras no coincide con el cálculo de Python ("
            + "; ".join(detalle)
            + ")."
        )

    # V32 · El esquema estricto garantiza las claves, pero una cadena
    # puede existir y venir vacía. No abortamos aquí porque la siguiente
    # fase puede repararla en UNA sola llamada condicional en lote.
    campos_vacios = []

    for id_figura in ids_esperados:
        contenido_previo = resultado.get(id_figura) or {}

        if not str(
            contenido_previo.get("titulo_humano", "")
            or ""
        ).strip():
            campos_vacios.append(
                f"{id_figura}.titulo_humano"
            )

        if not str(
            contenido_previo.get("interpretacion", "")
            or ""
        ).strip():
            campos_vacios.append(
                f"{id_figura}.interpretacion"
            )

    if campos_vacios:
        print(
            "Salida estructurada con campos vacíos; "
            "se repararán en lote: "
            + ", ".join(campos_vacios)
        )

    # Postprocesado exclusivamente local.
    for id_figura in ids_esperados:
        contenido = resultado.get(id_figura) or {}

        titulo = str(
            contenido.get("titulo_humano", "")
            or ""
        ).strip()

        interpretacion = str(
            contenido.get("interpretacion", "")
            or ""
        ).strip()

        titulo = corregir_letras_no_latinas(None, titulo)
        interpretacion = corregir_letras_no_latinas(None, interpretacion)

        titulo = corregir_conjunciones_disyuntivas(titulo)
        interpretacion = corregir_conjunciones_disyuntivas(interpretacion)

        titulo = normalizar_espanol_peninsular_figura(titulo)
        interpretacion = normalizar_espanol_peninsular_figura(interpretacion)

        titulo = corregir_genero_dirigido_local(titulo)
        interpretacion = corregir_genero_dirigido_local(interpretacion)

        interpretacion = neutralizar_teleologia_residual(
            interpretacion
        )
        interpretacion = cierre_editorial_local_final(
            interpretacion
        )
        titulo = cierre_editorial_local_final(
            titulo
        )
        interpretacion = eliminar_coletillas_conversacionales(
            interpretacion
        )

        resultado[id_figura] = {
            "titulo_humano": titulo,
            "interpretacion": interpretacion,
        }

    # V38 · Diagnóstico informativo de profundidad.
    # NO bloquea ni hace llamadas extra.
    diagnostico_profundidad = {}

    for dato in datos_figuras:
        id_figura = str(
            dato.get("id_figura")
            or ""
        ).strip()

        if not id_figura:
            continue

        interpretacion = str(
            (resultado.get(id_figura) or {}).get(
                "interpretacion",
                "",
            )
            or ""
        )

        palabras = re.findall(
            r"\b[\wÁÉÍÓÚÜÑáéíóúüñ]+\b",
            interpretacion,
        )

        plan = (
            dato.get(
                "plan_interpretativo_huber_2026"
            )
            or {}
        )

        diagnostico_profundidad[id_figura] = {
            "palabras": len(palabras),
            "rol": plan.get(
                "rol_seleccion_huber_2026"
            ),
            "profundidad": (
                plan.get(
                    "profundidad_interpretativa"
                )
                or {}
            ).get("nivel"),
            "colores_presentes": (
                plan.get(
                    "lectura_colores_huber_2026"
                )
                or {}
            ).get(
                "colores_presentes",
                [],
            ),
        }

    try:
        with open(
            "diagnostico_profundidad_figuras.json",
            "w",
            encoding="utf-8",
        ) as archivo:
            json.dump(
                diagnostico_profundidad,
                archivo,
                ensure_ascii=False,
                indent=2,
            )
    except Exception:
        pass

    return resultado


def convertir_bloques_figuras_a_markdown(
    bloques_figuras,
):
    """
    Convierte los bloques estructurados de figuras
    al formato Markdown que ya entiende el generador PDF.

    Formato:

    ### Título humano
    **Título técnico**

    Interpretación
    """

    lineas = []

    for bloque in bloques_figuras:

        titulo_humano = bloque.get(
            "titulo_humano",
            ""
        ).strip()

        titulo_tecnico = normalizar_titulo_tecnico_figura(
            bloque.get(
                "titulo_tecnico",
                ""
            )
        )

        interpretacion = bloque.get(
            "interpretacion",
            ""
        ).strip()

        if (
            not titulo_humano
            or not titulo_tecnico
            or not interpretacion
        ):
            continue

        lineas.append(
            f"### {titulo_humano}"
        )

        lineas.append(
            f"**{titulo_tecnico}**"
        )

        lineas.append("")

        lineas.append(
            interpretacion
        )

        lineas.append("")

    return "\n".join(
        lineas
    ).strip()


def detectar_puntos_ajenos_en_figura(
    texto,
    puntos_permitidos,
    puntos_catalogo,
):
    """
    Detecta si una interpretación individual menciona
    puntos astrológicos que no pertenecen a esa figura.

    La comparación se realiza contra el catálogo real
    de puntos natales calculados para la carta.
    """

    if not texto:
        return []

    permitidos = set(
        puntos_permitidos
    )

    encontrados_ajenos = []

    for punto in puntos_catalogo:

        if punto in permitidos:
            continue

        patron = (
            r"(?<!\w)"
            + re.escape(punto)
            + r"(?!\w)"
        )

        if re.search(
            patron,
            texto,
        ):
            encontrados_ajenos.append(
                punto
            )

    return encontrados_ajenos

def corregir_puntos_ajenos_interpretaciones_figuras(
    contexto_compacto,
    interpretaciones_figuras,
):
    """
    V32 · Reparación única y condicional de la salida de figuras.

    La generación normal sigue usando dos llamadas:
    1) informe global;
    2) todas las figuras.

    Solo si la segunda llamada devuelve alguna incidencia se hace UNA
    tercera llamada en lote.

    Se reparan conjuntamente:
    - títulos o interpretaciones vacíos/incompletos;
    - menciones a puntos astrológicos ajenos a la figura.

    Esto evita perder una generación completa por un único campo vacío.
    """

    figuras = (
        contexto_compacto
        .get("figuras", {})
        .get("arquitectura", {})
        .get("figuras", [])
        or []
    )

    figuras = _figuras_con_bloque_independiente(
        figuras,
        contexto_compacto,
    )

    posiciones_natales = (
        contexto_compacto
        .get("figuras", {})
        .get("posiciones_natales", {})
        or {}
    )

    aspectos_relevantes = (
        contexto_compacto
        .get("figuras", {})
        .get("aspectos_relevantes", [])
        or []
    )

    puntos_catalogo = list(
        posiciones_natales.keys()
    )

    figuras_por_id = {
        (figura.get("id_figura") or "").strip(): figura
        for figura in figuras
        if (figura.get("id_figura") or "").strip()
    }

    incidencias = {}

    for id_figura, figura in figuras_por_id.items():
        datos_ia = interpretaciones_figuras.get(
            id_figura,
            {},
        ) or {}

        titulo = str(
            datos_ia.get("titulo_humano", "")
            or ""
        ).strip()

        interpretacion = str(
            datos_ia.get("interpretacion", "")
            or ""
        ).strip()

        paquete = figura.get("paquete_huber_ia") or {}

        puntos_permitidos = [
            str(punto)
            for punto in (
                paquete.get("puntos_editoriales_permitidos")
                or figura.get("puntos_editoriales_familia_huber_2026")
                or figura.get("puntos", [])
                or []
            )
        ]

        motivos = []
        puntos_ajenos = []

        if not titulo:
            motivos.append("titulo_humano_vacio")

        if not interpretacion:
            motivos.append("interpretacion_vacia")

        texto_completo = ""

        if titulo or interpretacion:
            texto_completo = (
                titulo
                + ("\n" if titulo and interpretacion else "")
                + interpretacion
            )

            puntos_ajenos = detectar_puntos_ajenos_en_figura(
                texto_completo,
                puntos_permitidos,
                puntos_catalogo,
            )

            if puntos_ajenos:
                motivos.append("puntos_ajenos")

        aspectos_figura = Figuras.obtener_aspectos_de_figura(
            figura,
            aspectos_relevantes,
        )

        aspectos_compactos = []
        for aspecto in aspectos_figura:
            aspectos_compactos.append({
                "p1": aspecto.get("p1"),
                "p2": aspecto.get("p2"),
                "tipo": aspecto.get("tipo"),
                "simbolo": aspecto.get("simbolo"),
                "orbe": aspecto.get("orbe"),
            })

        lectura_colores_real = _lectura_colores_huber_2026(
            aspectos_compactos
        )

        colores_huber_ajenos = detectar_colores_huber_ajenos_2026(
            texto_completo,
            lectura_colores_real,
        )

        if colores_huber_ajenos:
            motivos.append("color_huber_ajeno")

        if not motivos:
            continue

        posiciones_figura = {}
        for punto in puntos_permitidos:
            datos_posicion = posiciones_natales.get(punto)
            if isinstance(datos_posicion, dict):
                posiciones_figura[punto] = {
                    "signo": datos_posicion.get("signo"),
                    "casa": datos_posicion.get("casa"),
                    "grado": datos_posicion.get("grado"),
                    "retrogrado": datos_posicion.get("retrogrado"),
                }

        incidencias[id_figura] = {
            "motivos": motivos,
            "puntos_permitidos": puntos_permitidos,
            "puntos_ajenos_detectados": puntos_ajenos,
            "colores_huber_ajenos_detectados": colores_huber_ajenos,
            "colores_huber_reales": lectura_colores_real.get(
                "colores_presentes",
                [],
            ),
            "titulo_humano_original": titulo,
            "interpretacion_original": interpretacion,
            "tipo": figura.get("tipo"),
            "nombre_canonico": figura.get("nombre_canonico"),
            "titulo_tecnico": figura.get("titulo_salida"),
            "seleccion_huber_2026": figura.get("seleccion_huber_2026"),
            "apice": figura.get("apice"),
            "base": figura.get("base"),
            "oposicion": figura.get("oposicion"),
            "vertices": figura.get("vertices", []),
            "aspectos": aspectos_compactos,
            "posiciones": posiciones_figura,
            "paquete_huber_ia": paquete,
            "plan_interpretativo_huber_2026": (
                _plan_editorial_figura_2026(
                    figura,
                    aspectos_compactos,
                    posiciones_figura,
                )
            ),
        }

    if not incidencias:
        return interpretaciones_figuras

    print(
        "Reparando en lote salida de figuras: "
        + ", ".join(
            f"{id_figura} ({', '.join(datos['motivos'])})"
            for id_figura, datos in incidencias.items()
        )
    )

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY no está configurada para reparar figuras."
        )

    propiedades = {}

    for id_figura in incidencias:
        propiedades[id_figura] = {
            "type": "object",
            "properties": {
                "titulo_humano": {
                    "type": "string",
                },
                "interpretacion": {
                    "type": "string",
                },
            },
            "required": [
                "titulo_humano",
                "interpretacion",
            ],
            "additionalProperties": False,
        }

    schema = {
        "type": "object",
        "properties": propiedades,
        "required": list(incidencias.keys()),
        "additionalProperties": False,
    }

    prompt = f"""
REPARACIÓN ESTRUCTURADA EN LOTE · FIGURAS

Corrige exclusivamente las figuras incluidas en INCIDENCIAS.

Cada incidencia puede deberse a una o varias causas:
- "titulo_humano_vacio";
- "interpretacion_vacia";
- "puntos_ajenos";
- "color_huber_ajeno".

OBJETIVO

Para CADA id_figura devuelve SIEMPRE:
- titulo_humano: breve, humano, claro y NO vacío;
- interpretacion: completa, clara y NO vacía.

Si el campo original estaba vacío:
- genera únicamente ese contenido a partir de los datos técnicos de ESA figura;
- conserva el otro campo si ya era correcto;
- respeta la extensión y foco de plan_interpretativo_huber_2026.

Si había puntos ajenos:
- elimina esas menciones;
- no las sustituyas por otro punto ajeno;
- conserva el sentido válido del resto.

Si había "color_huber_ajeno":
- conserva la interpretación válida;
- corrige únicamente las atribuciones cromáticas falsas;
- usa SOLO los colores incluidos en "colores_huber_reales";
- no llames verde/azul/rojo a una relación que no figure en la lista
  correspondiente de lectura_colores_huber_2026;
- si una frase usaba el color solo como metáfora, reescríbela sin ese color.

REGLAS ESTRICTAS

1. Solo puedes mencionar puntos incluidos exactamente en
   "puntos_permitidos" de ESA figura.

2. Respeta tipo, geometría, aspectos, signos, casas, retrogradaciones,
   ápice, base, oposición y vértices suministrados.

3. Si la figura es de rescate, el foco debe estar en las relaciones
   nuevas señaladas por plan_interpretativo_huber_2026, pero desarrolla
   suficientemente cómo esa relación modifica el circuito completo.
   No existe un máximo de 70-110 palabras.

3.b. Respeta lectura_colores_huber_2026 y profundidad_interpretativa.
     Si hay rojo/azul/verde, conserva la explicación de qué función cumple
     cada color en ESTA figura. Solo puedes usar un color Huber si aparece
     en colores_presentes y solo para las relaciones listadas bajo ese color.
     No uses colores como metáfora de funciones psicológicas.
     No repares una incidencia convirtiendo una interpretación profunda en
     una versión resumida.

4. No introduzcas datos de otras figuras ni de la carta global.

5. No inventes aspectos, casas, biografía, profesión, trauma,
   acontecimientos ni relaciones concretas.

6. Mantén segunda persona y español de España.
   Aplica exactamente el tratamiento lingüístico indicado más abajo.
   En modo neutro, la terminación -e SOLO se usa cuando la palabra se refiere
   directamente a quien lee. Conserva la concordancia gramatical normal de
   sustantivos como energía, respuesta, figura, carta, dinámica, relación, etc.
   Ejemplo: "esa energía aparece muy concentrada", nunca "concentrade".

7. No menciones biblioteca, libros, autores, File Search, fuentes
   ni material recuperado.

8. {instruccion_tratamiento_linguistico()}

8. No añadas Markdown, comentarios ni explicaciones externas.

9. El título y la interpretación deben contener texto real.
   No devuelvas cadenas vacías ni espacios.

INCIDENCIAS:

{json.dumps(incidencias, ensure_ascii=False, indent=2)}
"""

    client = OpenAI(api_key=api_key)

    response = client.responses.create(
        model="gpt-5.4-mini",
        input=prompt,
        max_output_tokens=12000,
        text={
            "format": {
                "type": "json_schema",
                "name": "reparacion_figuras_incompletas_o_aislamiento",
                "strict": True,
                "schema": schema,
            }
        },
    )

    if not response.output_text:
        raise RuntimeError(
            "OpenAI no ha devuelto la reparación de figuras."
        )

    try:
        reparadas = json.loads(
            response.output_text
        )
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "La reparación de figuras no contiene JSON válido."
        ) from exc

    for id_figura, incidencia in incidencias.items():
        contenido = reparadas.get(id_figura) or {}

        titulo = str(
            contenido.get("titulo_humano", "")
            or ""
        ).strip()

        interpretacion = str(
            contenido.get("interpretacion", "")
            or ""
        ).strip()

        if not titulo or not interpretacion:
            raise RuntimeError(
                f"La reparación de {id_figura} sigue incompleta."
            )

        # Mismo postprocesado local que la generación principal.
        titulo = corregir_letras_no_latinas(None, titulo)
        interpretacion = corregir_letras_no_latinas(None, interpretacion)

        titulo = corregir_conjunciones_disyuntivas(titulo)
        interpretacion = corregir_conjunciones_disyuntivas(interpretacion)

        titulo = normalizar_espanol_peninsular_figura(titulo)
        interpretacion = normalizar_espanol_peninsular_figura(
            interpretacion
        )

        titulo = corregir_genero_dirigido_local(titulo)
        interpretacion = corregir_genero_dirigido_local(
            interpretacion
        )

        titulo = neutralizar_genero_lector_ampliado_local(
            titulo
        )
        interpretacion = neutralizar_genero_lector_ampliado_local(
            interpretacion
        )

        titulo = neutralizar_tercera_persona_lector_local(
            titulo
        )
        interpretacion = neutralizar_tercera_persona_lector_local(
            interpretacion
        )

        titulo = eliminar_referencias_internas_fuentes_local(
            titulo
        )
        interpretacion = eliminar_referencias_internas_fuentes_local(
            interpretacion
        )

        interpretacion = eliminar_coletillas_conversacionales(
            interpretacion
        )

        interpretacion = asegurar_puntuacion_final_narrativa(
            interpretacion
        )

        if not titulo.strip() or not interpretacion.strip():
            raise RuntimeError(
                f"La reparación local de {id_figura} ha dejado "
                "algún campo vacío."
            )

        puntos_restantes = detectar_puntos_ajenos_en_figura(
            titulo + "\n" + interpretacion,
            incidencia["puntos_permitidos"],
            puntos_catalogo,
        )

        if puntos_restantes:
            raise RuntimeError(
                f"La reparación de {id_figura} sigue mencionando "
                "puntos ajenos: "
                + ", ".join(puntos_restantes)
            )

        interpretaciones_figuras[id_figura] = {
            "titulo_humano": titulo,
            "interpretacion": interpretacion,
        }

    return interpretaciones_figuras


ORDEN_EDITORIAL_46_ARTE_ENCARNARTE = [
    "Diamante",
    "Caja de Pandora",
    "Cuadrado de rendimiento",
    "Figura de ambivalencia doble",
    "Arena",
    "Animat",
    "Provocat",
    "Triángulo de rendimiento",
    "Rectángulo de rectitud",
    "Rectángulo de excitación",
    "Canalizador",
    "Deco",
    "Trapecio",
    "Telescopio-Microscopio",
    "Cometa",
    "Cuna",
    "Megáfono",
    "Bijou",
    "Triángulo de ambivalencia",
    "Escenario",
    "Figura de aspiración",
    "Triángulo de excitación",
    "Nasa",
    "Represent",
    "Oscilo",
    "Model",
    "Triángulo dominante",
    "Bañera",
    "Ovni",
    "Surfista",
    "Grabadora",
    "Triángulo de aprendizaje grande",
    "Escudo",
    "Corredor (saltador)",
    "Amortiguador",
    "Trampolín",
    "Detect",
    "Triángulo de aprendizaje mediano",
    "Gorro mágico",
    "Triángulo de aprendizaje pequeño",
    "Mariposa",
    "Figura de proyección",
    "Figura de búsqueda",
    "Figura de información (ojo)",
    "Triángulo de talento grande",
    "Triángulo de talento pequeño",
]

INDICE_ORDEN_EDITORIAL_46_ARTE_ENCARNARTE = {
    nombre: indice
    for indice, nombre in enumerate(ORDEN_EDITORIAL_46_ARTE_ENCARNARTE)
}

ALIAS_ORDEN_EDITORIAL_ARTE_ENCARNARTE = {
    "T-cuadrada": "Triángulo de rendimiento",
    "Gran trígono": "Triángulo de talento grande",
    "Yod": "Figura de proyección",
    "Ojo pequeño": "Figura de información (ojo)",
    "Triángulo de aprendizaje": "Triángulo dominante",
}


def _validar_orden_editorial_46_arte_encarnarte():
    if len(ORDEN_EDITORIAL_46_ARTE_ENCARNARTE) != 46:
        raise RuntimeError(
            "ORDEN_EDITORIAL_46_ARTE_ENCARNARTE debe contener exactamente 46 figuras."
        )
    if len(set(ORDEN_EDITORIAL_46_ARTE_ENCARNARTE)) != 46:
        raise RuntimeError(
            "ORDEN_EDITORIAL_46_ARTE_ENCARNARTE contiene nombres duplicados."
        )


_validar_orden_editorial_46_arte_encarnarte()


def _nombre_orden_editorial_arte_encarnarte(figura):
    paquete = figura.get("paquete_huber_ia") or {}
    nombre = (
        paquete.get("nombre_huber")
        or figura.get("nombre_canonico")
        or figura.get("tipo")
        or ""
    ).strip()
    return ALIAS_ORDEN_EDITORIAL_ARTE_ENCARNARTE.get(nombre, nombre)


def _orbe_medio_figura_editorial(figura, aspectos_relevantes):
    try:
        aspectos = Figuras.obtener_aspectos_de_figura(
            figura,
            aspectos_relevantes,
        )
    except Exception:
        aspectos = figura.get("aspectos", []) or []

    orbes = []
    for aspecto in aspectos or []:
        try:
            orbes.append(float(aspecto.get("orbe")))
        except (TypeError, ValueError, AttributeError):
            continue

    if not orbes:
        return 999.0
    return sum(orbes) / len(orbes)


def orden_editorial_figura_arte_encarnarte(
    figura,
    aspectos_relevantes=None,
):
    """
    Orden físico del informe.

    1. Orden editorial maestro de 46 figuras.
    2. Si hay varias apariciones del mismo tipo, menor orbe medio.
    3. Puntos geométricos para estabilizar empates.

    Stellium no forma parte de las 46 figuras Huber y queda después
    de la secuencia editorial como estructura complementaria.
    """
    aspectos_relevantes = aspectos_relevantes or []
    nombre = _nombre_orden_editorial_arte_encarnarte(figura)

    tipo_editorial = str(figura.get("tipo") or "").casefold()

    if tipo_editorial == "cierre colectivo de stellium":
        # Estructura complementaria creada únicamente para rescatar una
        # arista huérfana que cierra geometría al tratar el stellium como
        # vértice colectivo. No altera las 46 figuras Huber canónicas.
        indice = len(ORDEN_EDITORIAL_46_ARTE_ENCARNARTE)
    elif tipo_editorial == "stellium":
        indice = len(ORDEN_EDITORIAL_46_ARTE_ENCARNARTE) + 1
    else:
        indice = INDICE_ORDEN_EDITORIAL_46_ARTE_ENCARNARTE.get(nombre)
        if indice is None:
            raise RuntimeError(
                "Figura sin posición en el orden editorial maestro: "
                + str(nombre)
            )

    puntos = tuple(
        sorted(
            str(p)
            for p in (
                figura.get("puntos_geometricos")
                or figura.get("puntos")
                or []
            )
        )
    )

    return (
        indice,
        _orbe_medio_figura_editorial(
            figura,
            aspectos_relevantes,
        ),
        puntos,
    )


# ─── FIN ORDEN EDITORIAL MAESTRO ─────────────────────────────────────────────


SECCION_EDITORIAL_HUBER = {
    "Cuadrado de rendimiento": "tensiones",
    "Triángulo de rendimiento": "tensiones",
    "T-cuadrada": "tensiones",
    "T-cuadrada compuesta": "tensiones",
    "Triángulo de excitación": "tensiones",
    "Rectángulo de excitación": "tensiones",
    "Figura de proyección": "tensiones",
    "Yod": "tensiones",
    "Yod con Ojo pequeño en la base": "tensiones",
    "Corredor (saltador)": "tensiones",
    "Amortiguador": "tensiones",
    "Provocat": "tensiones",
    "Arena": "tensiones",
    "Canalizador": "tensiones",
    "Ovni": "tensiones",
    "Surfista": "tensiones",

    "Triángulo de talento grande": "recursos_integracion",
    "Gran trígono": "recursos_integracion",
    "Triángulo de talento pequeño": "recursos_integracion",
    "Cometa": "recursos_integracion",
    "Rectángulo de rectitud": "recursos_integracion",
    "Cuna": "recursos_integracion",
    "Detect": "recursos_integracion",
    "Grabadora": "recursos_integracion",
    "Model": "recursos_integracion",
    "Represent": "recursos_integracion",
    "Bijou": "recursos_integracion",
    "Escudo": "recursos_integracion",

    "Triángulo de ambivalencia": "relaciones",
    "Figura de ambivalencia doble": "relaciones",
    "Figura de búsqueda": "relaciones",
    "Figura de información (ojo)": "relaciones",
    "Ojo pequeño": "relaciones",
    "Triángulo de aprendizaje pequeño": "relaciones",
    "Triángulo de aprendizaje mediano": "relaciones",
    "Triángulo de aprendizaje grande": "relaciones",
    "Triángulo dominante": "relaciones",
    "Triángulo de aprendizaje": "relaciones",
    "Trapecio": "relaciones",
    "Figura de aspiración": "relaciones",
    "Caja de Pandora": "relaciones",
    "Bañera": "relaciones",
    "Mariposa": "relaciones",
    "Nasa": "relaciones",
    "Trampolín": "relaciones",
    "Telescopio-Microscopio": "relaciones",
    "Diamante": "relaciones",
    "Megáfono": "relaciones",
    "Animat": "relaciones",
    "Deco": "relaciones",
    "Escenario": "relaciones",
    "Gorro mágico": "relaciones",
    "Oscilo": "relaciones",

    "Cierre colectivo de stellium": "relaciones",
    "Stellium": "relaciones",
    "Red de aprendizaje": "relaciones",
}


PRIORIDAD_EDITORIAL_HUBER = {
    "Red de aprendizaje": 120,
    "T-cuadrada compuesta": 120,
    "Yod con Ojo pequeño en la base": 120,
    "Diamante": 115,
    "Caja de Pandora": 110,
    "Figura de ambivalencia doble": 105,
    "Cuadrado de rendimiento": 105,
    "Rectángulo de rectitud": 100,
    "Rectángulo de excitación": 100,
    "Figura de aspiración": 100,
    "Trapecio": 98,
    "Cometa": 98,

    "Bañera": 96,
    "Nasa": 96,
    "Trampolín": 96,
    "Telescopio-Microscopio": 96,
    "Escudo": 96,
    "Megáfono": 96,
    "Animat": 96,
    "Provocat": 96,
    "Arena": 96,
    "Canalizador": 96,
    "Deco": 96,
    "Bijou": 96,
    "Detect": 96,
    "Grabadora": 96,
    "Model": 96,
    "Represent": 96,
    "Escenario": 96,
    "Gorro mágico": 96,
    "Ovni": 96,
    "Surfista": 96,
    "Oscilo": 96,

    "Mariposa": 92,
    "Corredor (saltador)": 92,
    "Amortiguador": 92,

    "Gran trígono": 90,
    "Triángulo de talento grande": 90,
    "Triángulo de aprendizaje grande": 86,
    "Triángulo dominante": 84,
    "Triángulo de aprendizaje": 84,
    "Triángulo de aprendizaje mediano": 82,
    "Triángulo de rendimiento": 80,
    "T-cuadrada": 80,
    "Yod": 80,
    "Figura de proyección": 80,
    "Triángulo de ambivalencia": 78,
    "Triángulo de excitación": 78,
    "Triángulo de talento pequeño": 76,
    "Triángulo de aprendizaje pequeño": 74,
    "Figura de búsqueda": 72,
    "Figura de información (ojo)": 70,
    "Ojo pequeño": 70,
    "Cierre colectivo de stellium": 65,
    "Stellium": 60,
}


def _nombre_huber_o_tipo_editorial(figura):
    paquete = figura.get("paquete_huber_ia") or {}

    return (
        paquete.get("nombre_huber")
        or figura.get("nombre_canonico")
        or figura.get("tipo", "")
    )


def _normalizar_clave_editorial(valor):
    import unicodedata

    valor = str(valor or "").strip()

    # Repara mojibake tipico:
    # aspiración -> aspiracion correctamente codificada
    # trígono    -> trigono correctamente codificado
    # pequeño    -> pequeno correctamente codificado
    if any(marca in valor for marca in ("Ã", "Â", "â")):
        try:
            valor_reparado = valor.encode("latin1").decode("utf-8")
            valor = valor_reparado
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass

    valor = unicodedata.normalize("NFC", valor)

    return valor.casefold()

def _buscar_clave_editorial(diccionario, valor, defecto=None):
    clave_objetivo = _normalizar_clave_editorial(valor)

    for clave, resultado in diccionario.items():
        if _normalizar_clave_editorial(clave) == clave_objetivo:
            return resultado

    return defecto


def clasificar_seccion_figura(figura):
    tipo = figura.get("tipo", "")
    nombre = _nombre_huber_o_tipo_editorial(figura)

    seccion = _buscar_clave_editorial(
        SECCION_EDITORIAL_HUBER,
        tipo,
    )

    if seccion is not None:
        return seccion

    seccion = _buscar_clave_editorial(
        SECCION_EDITORIAL_HUBER,
        nombre,
    )

    if seccion is not None:
        return seccion

    raise RuntimeError(
        "Tipo de figura sin clasificacion editorial definida: "
        f"{tipo} / {nombre}"
    )


def orden_estructural_figura_huber(figura):
    """
    Orden editorial posterior a la selección Huber 2026.

    Ya no utiliza la antigua PRIORIDAD_EDITORIAL_HUBER ni la vieja
    puntuación de jerarquía. Solo ordena; nunca elimina figuras.

    "principal" y "rescate" son rutas técnicas de detección, no una escala
    de valor psicológico.
    """
    paquete = figura.get("paquete_huber_ia") or {}

    rol = (
        figura.get("seleccion_huber_2026")
        or paquete.get("seleccion_huber_2026")
        or ""
    )

    peso_rol = {
        "principal": 3,
        "rescate": 2,
        "complementaria": 1,
    }.get(rol, 0)

    nivel_composicion = int(
        figura.get("nivel_composicion", 0) or 0
    )

    aspectos = len(figura.get("aspectos", []) or [])
    puntos = len(figura.get("puntos", []) or [])

    return (
        peso_rol,
        -nivel_composicion,
        aspectos,
        puntos,
        str(
            figura.get("nombre_canonico")
            or figura.get("tipo")
            or ""
        ),
    )


# ─── FIN HUBER FASE 10 ────────────────────────────────────────────────────────

def construir_bloques_figuras(
    contexto_compacto,
    interpretaciones_figuras,
):
    """
    Combina los datos técnicos controlados por Python con la
    interpretación estructurada. Todo el postprocesado de esta fase es
    local: no realiza llamadas adicionales a OpenAI.
    """
    figuras = (
        contexto_compacto
        .get("figuras", {})
        .get("arquitectura", {})
        .get("figuras", [])
        or []
    )
    figuras = _figuras_con_bloque_independiente(
        figuras,
        contexto_compacto,
    )

    puntos_catalogo = list(
        contexto_compacto
        .get("figuras", {})
        .get("posiciones_natales", {})
        .keys()
    )

    bloques = []

    for figura in figuras:
        id_figura = (figura.get("id_figura") or "").strip()
        titulo_salida = normalizar_titulo_tecnico_figura(
            figura.get("titulo_salida")
        )

        if not id_figura or not titulo_salida:
            continue

        interpretacion_ia = interpretaciones_figuras.get(id_figura, {}) or {}
        titulo_humano = (interpretacion_ia.get("titulo_humano") or "").strip()
        interpretacion = (interpretacion_ia.get("interpretacion") or "").strip()

        # Correcciones puramente deterministas/locales.
        titulo_humano = corregir_letras_no_latinas(None, titulo_humano)
        interpretacion = corregir_letras_no_latinas(None, interpretacion)
        titulo_humano = corregir_conjunciones_disyuntivas(titulo_humano)
        interpretacion = corregir_conjunciones_disyuntivas(interpretacion)
        titulo_humano = normalizar_espanol_peninsular_figura(titulo_humano)
        interpretacion = normalizar_espanol_peninsular_figura(interpretacion)
        titulo_humano = corregir_genero_dirigido_local(titulo_humano)
        interpretacion = corregir_genero_dirigido_local(interpretacion)
        interpretacion = corregir_construcciones_poco_naturales_local(interpretacion)

        # V38: NO aplicamos aquí simplificación léxica ni deduplicación de frases.
        # Esas funciones podían aplanar una explicación astrológica válida,
        # borrar matices y eliminar saltos de párrafo. La claridad se exige ya
        # en el prompt; el postprocesado local solo corrige errores formales.
        interpretacion = neutralizar_teleologia_residual(interpretacion)

        seccion = clasificar_seccion_figura(figura)

        if not titulo_humano or not interpretacion:
            raise RuntimeError(
                f"Faltan datos interpretativos para {id_figura}."
            )

        texto_a_validar = titulo_humano + "\n" + interpretacion
        paquete_figura = figura.get("paquete_huber_ia") or {}
        puntos_permitidos = (
            paquete_figura.get("puntos_editoriales_permitidos")
            or figura.get("puntos_editoriales_familia_huber_2026")
            or figura.get("puntos", [])
        )
        puntos_ajenos = detectar_puntos_ajenos_en_figura(
            texto_a_validar,
            puntos_permitidos,
            puntos_catalogo,
        )

        if puntos_ajenos:
            raise RuntimeError(
                f"{id_figura} menciona puntos que no pertenecen a la figura: "
                + ", ".join(puntos_ajenos)
            )

        bloques.append({
            "id_figura": id_figura,
            "titulo_humano": titulo_humano,
            "titulo_tecnico": titulo_salida,
            "interpretacion": interpretacion,
            "seccion": seccion,
            "rol_seleccion_huber_2026": (
                figura.get("seleccion_huber_2026")
                or (figura.get("paquete_huber_ia") or {}).get(
                    "seleccion_huber_2026"
                )
                or ""
            ),
            "_orden_editorial": orden_editorial_figura_arte_encarnarte(
                figura,
                contexto_compacto
                .get("figuras", {})
                .get("aspectos_relevantes", [])
                or [],
            ),
        })

    if len(bloques) != len(figuras):
        ids_bloques = {b["id_figura"] for b in bloques}
        ids_faltantes = [
            (f.get("id_figura") or "<sin id>")
            for f in figuras
            if (f.get("id_figura") or "") not in ids_bloques
        ]
        raise RuntimeError(
            "No se han podido construir todos los bloques de figuras. "
            "Faltan: " + ", ".join(ids_faltantes)
        )

    bloques.sort(
        key=lambda bloque: bloque["_orden_editorial"],
    )
    for bloque in bloques:
        bloque.pop("_orden_editorial", None)

    return bloques

def detectar_figuras_reconstruidas_en_global(
    texto_global,
    contexto_compacto,
):
    """
    Detecta si el texto global reconstruye una figura
    individual mencionando juntos todos sus puntos.

    Ignora:

    - la sección 2 de núcleos;
    - los bloques estructurados de figuras que Python
      haya insertado posteriormente.

    No modifica el texto.
    """

    if not texto_global:
        return []

    figuras = (
        contexto_compacto
        .get("figuras", {})
        .get("arquitectura", {})
        .get("figuras", [])
    )

    if not figuras:
        return []

    lineas = texto_global.splitlines()

    bloques = []
    bloque_actual = []
    seccion_principal = None

    for linea in lineas:

        stripped = linea.strip()

        # Detectamos cambio de sección principal.
        if re.match(
            r"^##\s+",
            stripped,
        ):

            if bloque_actual:
                bloques.append(
                    (
                        seccion_principal,
                        "\n".join(
                            bloque_actual
                        ),
                    )
                )

                bloque_actual = []

            titulo_principal = re.sub(
                r"^##\s+",
                "",
                stripped,
            ).strip()

            coincidencia_numero = re.match(
                r"^(\d+)\.",
                titulo_principal,
            )

            if coincidencia_numero:
                seccion_principal = int(
                    coincidencia_numero.group(1)
                )
            else:
                titulo_normalizado = normalizar_titulo_seccion(
                    titulo_principal
                )
                seccion_principal = next(
                    (
                        indice
                        for indice, titulo_oficial
                        in enumerate(SECCIONES_INFORME, start=1)
                        if normalizar_titulo_seccion(titulo_oficial)
                        == titulo_normalizado
                    ),
                    None,
                )

            bloque_actual.append(
                linea
            )

            continue

        # Cada subtítulo ### inicia otro bloque,
        # pero conserva la sección principal.
        if re.match(
            r"^###\s+",
            stripped,
        ):

            if bloque_actual:
                bloques.append(
                    (
                        seccion_principal,
                        "\n".join(
                            bloque_actual
                        ),
                    )
                )

            bloque_actual = [
                linea
            ]

            continue

        bloque_actual.append(
            linea
        )

    if bloque_actual:
        bloques.append(
            (
                seccion_principal,
                "\n".join(
                    bloque_actual
                ),
            )
        )

    detectadas = []

    for numero_seccion, bloque in bloques:

        bloque_limpio = bloque.strip()

        if not bloque_limpio:
            continue

        # En núcleos sí permitimos referencias
        # a las figuras que sostienen el patrón.
        if numero_seccion == 2:
            continue

        # Los bloques individuales de figuras insertados
        # por Python tienen su propio subtítulo ### y
        # contienen el título técnico completo.
        # Se excluyen enteros del análisis del texto global.

        es_bloque_estructurado = any(
            (
                f"**{normalizar_titulo_tecnico_figura(figura.get('titulo_salida', ''))}**"
                in bloque_limpio
            )
            for figura in figuras
            if figura.get(
                "titulo_salida",
                ""
            ).strip()
        )

        if es_bloque_estructurado:
            continue


        # Analizamos unidades pequeñas de texto.
        # Así no consideramos reconstruida una figura
        # simplemente porque sus puntos aparezcan
        # dispersos por una sección larga.

        unidades = re.split(
            r"\n\s*\n+",
            bloque_limpio,
        )

        unidades = [
            unidad.strip()
            for unidad in unidades
            if unidad.strip()
        ]


        puntos_catalogo = list(
            contexto_compacto
            .get("figuras", {})
            .get("posiciones_natales", {})
            .keys()
        )

        for figura in figuras:

            titulo_salida = normalizar_titulo_tecnico_figura(
                figura.get(
                    "titulo_salida",
                    ""
                )
            )

            puntos = figura.get(
                "puntos",
                []
            )

            if (
                not titulo_salida
                or len(puntos) < 3
            ):
                continue

            for unidad in unidades:

                aparecen_todos = all(
                    re.search(
                        rf"(?<!\w){re.escape(str(punto))}(?!\w)",
                        unidad,
                        flags=re.IGNORECASE,
                    )
                    for punto in puntos
                )

                if not aparecen_todos:
                    continue

                # Si la unidad menciona otros puntos de la carta,
                # estamos ante una descripción global más amplia,
                # no ante la reconstrucción aislada de esta figura.
                puntos_mencionados = [
                    punto_catalogo
                    for punto_catalogo in puntos_catalogo
                    if re.search(
                        rf"(?<!\w)"
                        rf"{re.escape(str(punto_catalogo))}"
                        rf"(?!\w)",
                        unidad,
                        flags=re.IGNORECASE,
                    )
                ]

                puntos_ajenos = [
                    punto_mencionado
                    for punto_mencionado in puntos_mencionados
                    if punto_mencionado not in puntos
                ]

                if puntos_ajenos:
                    continue

                # No basta con que los puntos aparezcan juntos.
                # Debe existir además una formulación que los
                # esté tratando como una unidad interpretativa.
                indicadores_reconstruccion = [
                    r"\bla dinámica entre\b",
                    r"\bla relación entre\b",
                    r"\besta dinámica\b",
                    r"\besta configuración\b",
                    r"\besta figura\b",
                    r"\besta tríada\b",
                    r"\besta triada\b",
                    r"\bel circuito\b",
                    r"\bun circuito\b",
                    r"\bel gran apoyo entre\b",
                    r"\buna estructura entre\b",
                    r"\besta estructura\b",
                    r"\bla configuración que articula\b",
                    r"\bla configuración formada por\b",
                    r"\bla configuración entre\b",
                    r"\bla cooperación entre\b",
                    r"\bla interacción entre\b",
                ]

                reconstruccion_explicita = any(
                    re.search(
                        patron,
                        unidad,
                        flags=re.IGNORECASE,
                    )
                    for patron in indicadores_reconstruccion
                )

                # Estas formulaciones describen arquitectura
                # global y NO deben considerarse reconstrucción
                # de una figura concreta.
                indicadores_globales = [
                    r"\brepetición de\b",
                    r"\bla familia formada por\b",
                    r"\bfamilia de\b",
                    r"\bpuntos organizadores\b",
                ]

                descripcion_global = any(
                    re.search(
                        patron,
                        unidad,
                        flags=re.IGNORECASE,
                    )
                    for patron in indicadores_globales
                )

                if (
                    reconstruccion_explicita
                    and not descripcion_global
                ):

                    if titulo_salida not in detectadas:
                        detectadas.append(
                            titulo_salida
                        )

                    break

    return detectadas

def localizar_fragmentos_figuras_reconstruidas(
    texto_global,
    contexto_compacto,
):
    """
    Localiza los fragmentos concretos del texto global
    que reconstruyen figuras individuales.

    Devuelve una lista de diccionarios con:
    - titulo_figura
    - fragmento
    """

    if not texto_global:
        return []

    figuras = (
        contexto_compacto
        .get("figuras", {})
        .get("arquitectura", {})
        .get("figuras", [])
    )

    if not figuras:
        return []

    lineas = texto_global.splitlines()

    bloques = []
    bloque_actual = []
    seccion_principal = None

    for linea in lineas:

        stripped = linea.strip()

        if re.match(
            r"^##\s+",
            stripped,
        ):

            if bloque_actual:
                bloques.append(
                    (
                        seccion_principal,
                        "\n".join(
                            bloque_actual
                        ),
                    )
                )

                bloque_actual = []

            titulo_principal = re.sub(
                r"^##\s+",
                "",
                stripped,
            ).strip()

            coincidencia_numero = re.match(
                r"^(\d+)\.",
                titulo_principal,
            )

            if coincidencia_numero:
                seccion_principal = int(
                    coincidencia_numero.group(1)
                )
            else:
                titulo_normalizado = normalizar_titulo_seccion(
                    titulo_principal
                )
                seccion_principal = next(
                    (
                        indice
                        for indice, titulo_oficial
                        in enumerate(SECCIONES_INFORME, start=1)
                        if normalizar_titulo_seccion(titulo_oficial)
                        == titulo_normalizado
                    ),
                    None,
                )

            bloque_actual.append(
                linea
            )

            continue

        if re.match(
            r"^###\s+",
            stripped,
        ):

            if bloque_actual:
                bloques.append(
                    (
                        seccion_principal,
                        "\n".join(
                            bloque_actual
                        ),
                    )
                )

            bloque_actual = [
                linea
            ]

            continue

        bloque_actual.append(
            linea
        )

    if bloque_actual:
        bloques.append(
            (
                seccion_principal,
                "\n".join(
                    bloque_actual
                ),
            )
        )

    resultados = []

    indicadores_reconstruccion = [
        r"\bla dinámica entre\b",
        r"\bla relación entre\b",
        r"\besta dinámica\b",
        r"\besta configuración\b",
        r"\besta figura\b",
        r"\besta tríada\b",
        r"\besta triada\b",
        r"\bel circuito\b",
        r"\bun circuito\b",
        r"\bel gran apoyo entre\b",
        r"\buna estructura entre\b",
        r"\besta estructura\b",
        r"\bla configuración que articula\b",
        r"\bla configuración formada por\b",
        r"\bla configuración entre\b",
        r"\bla cooperación entre\b",
        r"\bla interacción entre\b",
    ]

    indicadores_globales = [
        r"\brepetición de\b",
        r"\bla familia formada por\b",
        r"\bfamilia de\b",
        r"\bpuntos organizadores\b",
    ]

    for numero_seccion, bloque in bloques:

        bloque_limpio = bloque.strip()

        if not bloque_limpio:
            continue

        if numero_seccion == 2:
            continue

        es_bloque_estructurado = any(
            (
                f"**{normalizar_titulo_tecnico_figura(figura.get('titulo_salida', ''))}**"
                in bloque_limpio
            )
            for figura in figuras
            if figura.get(
                "titulo_salida",
                ""
            ).strip()
        )

        if es_bloque_estructurado:
            continue

        unidades = re.split(
            r"\n\s*\n+",
            bloque_limpio,
        )

        unidades = [
            unidad.strip()
            for unidad in unidades
            if unidad.strip()
        ]

        puntos_catalogo = (
            contexto_compacto
            .get("figuras", {})
            .get("posiciones_natales", {})
            .keys()
        )

        puntos_catalogo = list(
            puntos_catalogo
        )

        for figura in figuras:

            titulo_salida = normalizar_titulo_tecnico_figura(
                figura.get(
                    "titulo_salida",
                    ""
                )
            )

            puntos = figura.get(
                "puntos",
                []
            )

            if (
                not titulo_salida
                or len(puntos) < 3
            ):
                continue

            for unidad in unidades:

                aparecen_todos = all(
                    re.search(
                        rf"(?<!\w){re.escape(str(punto))}(?!\w)",
                        unidad,
                        flags=re.IGNORECASE,
                    )
                    for punto in puntos
                )

                if not aparecen_todos:
                    continue

                puntos_mencionados = [
                    punto_catalogo
                    for punto_catalogo in puntos_catalogo
                    if re.search(
                        rf"(?<!\w)"
                        rf"{re.escape(str(punto_catalogo))}"
                        rf"(?!\w)",
                        unidad,
                        flags=re.IGNORECASE,
                    )
                ]

                puntos_ajenos = [
                    punto_mencionado
                    for punto_mencionado in puntos_mencionados
                    if punto_mencionado not in puntos
                ]

                if puntos_ajenos:
                    continue

                reconstruccion_explicita = any(
                    re.search(
                        patron,
                        unidad,
                        flags=re.IGNORECASE,
                    )
                    for patron in indicadores_reconstruccion
                )

                descripcion_global = any(
                    re.search(
                        patron,
                        unidad,
                        flags=re.IGNORECASE,
                    )
                    for patron in indicadores_globales
                )

                if (
                    reconstruccion_explicita
                    and not descripcion_global
                ):
                    resultados.append(
                        {
                            "titulo_figura": titulo_salida,
                            "fragmento": unidad,
                        }
                    )

    return resultados

def corregir_fragmentos_figuras_reconstruidas(
    client,
    texto,
    contexto_compacto,
):
    """
    Localiza y corrige únicamente los fragmentos
    que reconstruyen figuras individuales.

    El resto del informe permanece intacto.
    """

    fragmentos = (
        localizar_fragmentos_figuras_reconstruidas(
            texto,
            contexto_compacto,
        )
    )

    if not fragmentos:
        return texto

    texto_corregido = texto

    for elemento in fragmentos:

        titulo_figura = elemento[
            "titulo_figura"
        ]

        fragmento = elemento[
            "fragmento"
        ]

        prompt_correccion = f"""
Reformula únicamente el siguiente fragmento de un
informe astrológico.

El fragmento está reconstruyendo una figura individual
que se interpretará por separado en otro bloque del informe.

FIGURA QUE NO DEBE RECONSTRUIRSE:
{titulo_figura}

FRAGMENTO:
{fragmento}

Conserva la idea global que aporta el fragmento al informe,
pero elimina la reconstrucción de esa figura concreta.

No reúnas de nuevo todos los puntos de la figura en una
misma frase, párrafo o unidad interpretativa.

No menciones el nombre técnico de la figura.

No describas su geometría.

No expliques cómo funcionan conjuntamente todos sus
componentes.

Puedes hablar de la función global que estaba expresando
el fragmento sin identificar la configuración concreta
que la sostiene.

No introduzcas información nueva.

No introduzcas lenguaje de destino, misión, propósito,
evolución predeterminada o dirección vital.

No utilices lenguaje prescriptivo.

No atribuyas como hechos biográficos experiencias que
solo pueden inferirse simbólicamente de la carta.

Mantén aproximadamente la misma extensión.

Devuelve únicamente el fragmento corregido.
"""

        response = client.responses.create(
            model="gpt-5.4-mini",
            input=prompt_correccion,
        )

        fragmento_corregido = (
            response.output_text
        )

        if not fragmento_corregido:
            raise RuntimeError(
                "OpenAI no ha devuelto texto al "
                "corregir un fragmento que "
                "reconstruía una figura."
            )

        fragmento_corregido = (
            fragmento_corregido.strip()
        )

        texto_corregido = (
            texto_corregido.replace(
                fragmento,
                fragmento_corregido,
                1,
            )
        )

    return texto_corregido


def integrar_bloques_figuras_en_informe(
    texto_global,
    bloques_figuras,
):
    """
    Inserta TODAS las figuras como una secuencia editorial única.

    Regla 2026:
    - el orden físico lo marca el orden maestro de 46 figuras;
    - principal/rescate/complementaria modifica la profundidad del texto,
      pero NO la posición;
    - la antigua clasificación por relaciones/tensiones/recursos se conserva
      solo como metadato y ya no rompe la secuencia.

    La secuencia se coloca al final de:
    "Cómo se relacionan las distintas partes",
    antes de "Tensiones estructurales".
    """

    if not texto_global:
        return texto_global

    if not bloques_figuras:
        return texto_global

    markdown_figuras = convertir_bloques_figuras_a_markdown(
        bloques_figuras
    )

    lineas = texto_global.splitlines()
    resultado = []

    dentro_seccion_relaciones = False
    insertado = False

    titulo_relaciones = normalizar_titulo_seccion(
        "Cómo se relacionan las distintas partes"
    )

    for linea in lineas:
        stripped = linea.strip()

        coincidencia = re.match(
            r"^##\s+(.+)$",
            stripped,
        )

        if coincidencia:
            titulo = re.sub(
                r"^\d+\.\s*",
                "",
                coincidencia.group(1).strip(),
            )
            titulo_normalizado = normalizar_titulo_seccion(
                titulo
            )

            if (
                dentro_seccion_relaciones
                and not insertado
                and titulo_normalizado != titulo_relaciones
            ):
                resultado.extend([
                    "",
                    markdown_figuras,
                    "",
                ])
                insertado = True
                dentro_seccion_relaciones = False

            if titulo_normalizado == titulo_relaciones:
                dentro_seccion_relaciones = True
            elif insertado:
                dentro_seccion_relaciones = False

        resultado.append(linea)

    if not insertado:
        if dentro_seccion_relaciones:
            resultado.extend([
                "",
                markdown_figuras,
                "",
            ])
            insertado = True
        else:
            raise RuntimeError(
                "No se ha encontrado la sección "
                "'Cómo se relacionan las distintas partes' "
                "para insertar la secuencia editorial de figuras."
            )

    return "\n".join(resultado)



def detectar_figuras_desarrolladas_en_global(
    texto_global,
    contexto_compacto,
):
    """
    Detecta si la interpretación global ha incluido
    el título técnico completo de alguna figura.

    Las figuras individuales deben generarse
    exclusivamente mediante Structured Outputs.
    """

    if not texto_global:
        return []

    figuras = (
        contexto_compacto
        .get("figuras", {})
        .get("arquitectura", {})
        .get("figuras", [])
    )

    encontradas = []

    texto_normalizado = texto_global.casefold()

    for figura in figuras:

        titulo = figura.get(
            "titulo_salida",
            ""
        ).strip()

        if not titulo:
            continue

        if titulo.casefold() in texto_normalizado:
            encontradas.append(
                titulo
            )

    return encontradas



def obtener_nucleos_autorizados(
    contexto_compacto,
):
    """
    Devuelve los núcleos que Python ha calculado como
    núcleos reales de la arquitectura.

    Las familias y sus pares internos NO se consideran
    núcleos autorizados para el informe.
    """

    nucleos = (
        contexto_compacto
        .get("figuras", {})
        .get("arquitectura", {})
        .get("nucleos", [])
    )

    resultado = []

    for nucleo in nucleos:

        puntos = [
            str(punto).strip()
            for punto in nucleo.get(
                "puntos_nucleo",
                []
            )
            if str(punto).strip()
        ]

        if puntos:
            resultado.append(
                frozenset(puntos)
            )

    return resultado


def detectar_etiquetas_nucleo_no_autorizadas(
    texto,
    contexto_compacto,
):
    """
    Detecta subtítulos técnicos que empiezan por "Núcleo"
    pero cuyo conjunto de puntos NO coincide exactamente
    con ninguno de los núcleos calculados por Python.

    Esto evita que la IA convierta pares de una familia
    estructural en núcleos nuevos.
    """

    if not texto:
        return []

    autorizados = set(
        obtener_nucleos_autorizados(
            contexto_compacto
        )
    )

    puntos_catalogo = list(
        contexto_compacto
        .get("figuras", {})
        .get("posiciones_natales", {})
        .keys()
    )

    indebidas = []

    for linea in texto.splitlines():

        linea_limpia = linea.strip()

        # Los encabezados Markdown son títulos humanos
        # editoriales. Pueden usar la palabra "Núcleo" de
        # forma descriptiva y no constituyen la etiqueta
        # técnica que debe coincidir con el cálculo de Python.
        if re.match(
            r"^#{1,6}\s+",
            linea_limpia,
        ):
            continue

        # Quitamos únicamente Markdown exterior para
        # analizar el contenido real de la línea.
        linea_limpia = re.sub(
            r"^#{1,6}\s*",
            "",
            linea_limpia,
        )

        linea_limpia = re.sub(
            r"^\*\*(.*?)\*\*$",
            r"\1",
            linea_limpia,
        ).strip()

        if not re.match(
            r"^Núcleo\b",
            linea_limpia,
            flags=re.IGNORECASE,
        ):
            continue

        puntos_mencionados = []

        for punto in puntos_catalogo:

            if re.search(
                rf"(?<!\w){re.escape(str(punto))}(?!\w)",
                linea_limpia,
                flags=re.IGNORECASE,
            ):
                puntos_mencionados.append(
                    str(punto)
                )

        conjunto = frozenset(
            puntos_mencionados
        )

        # Una etiqueta "Núcleo" sin puntos reconocibles
        # tampoco es un subtítulo técnico válido.
        if (
            not conjunto
            or conjunto not in autorizados
        ):
            indebidas.append(
                linea.strip()
            )

    return indebidas


def eliminar_etiquetas_nucleo_no_autorizadas(
    texto,
    contexto_compacto,
):
    """
    Elimina únicamente las líneas técnicas "Núcleo ..."
    no autorizadas.

    Conserva el título humano y todo el desarrollo del
    apartado, porque la dinámica puede ser válida como
    patrón o familia aunque no constituya un núcleo real.
    """

    indebidas = set(
        detectar_etiquetas_nucleo_no_autorizadas(
            texto,
            contexto_compacto,
        )
    )

    if not indebidas:
        return texto

    lineas = []

    for linea in texto.splitlines():

        if linea.strip() in indebidas:
            continue

        lineas.append(
            linea
        )

    return "\n".join(
        lineas
    )


SECCIONES_INFORME = [
    "La arquitectura central de tu carta",
    "Los núcleos que organizan tu carta",
    "Cómo se relacionan las distintas partes",
    "Tensiones estructurales",
    "Recursos y vías de integración",
    "Dónde se expresa esta arquitectura",
    "Cómo sostener esta arquitectura",
    "Tu manera particular de funcionar",
]

CLAVES_SECCIONES_GLOBALES = [
    "arquitectura_central",
    "nucleos",
    "relaciones",
    "tensiones",
    "recursos_integracion",
    "donde_se_expresa",
    "como_sostener",
    "sintesis_final",
]

TITULO_POR_CLAVE_SECCION = dict(zip(CLAVES_SECCIONES_GLOBALES, SECCIONES_INFORME))


def reparar_mojibake_texto(valor):
    """Repara mojibake UTF-8/cp1252 frecuente sin tocar texto ya correcto."""
    if not valor:
        return valor
    valor = str(valor)
    for _ in range(2):
        if not any(marca in valor for marca in ("Ã", "Â", "â")):
            break
        try:
            reparado = valor.encode("cp1252").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            break
        if reparado == valor:
            break
        valor = reparado
    return valor


def normalizar_titulo_seccion(titulo):
    """Normaliza un encabezado principal para compararlo."""
    import unicodedata

    if not titulo:
        return ""

    titulo = reparar_mojibake_texto(titulo)
    titulo = unicodedata.normalize("NFC", str(titulo).strip())
    titulo = re.sub(r"^#{1,6}\s*", "", titulo)
    titulo = re.sub(r"^\d+\.\s*", "", titulo)
    return re.sub(r"\s+", " ", titulo).strip().casefold()


def normalizar_encabezados_secciones(texto):
    """
    Canoniza las ocho secciones principales y reconoce variantes
    editoriales antiguas. Los encabezados internos ### se conservan.
    """
    if not texto:
        return texto

    mapa = {
        normalizar_titulo_seccion(titulo): titulo
        for titulo in SECCIONES_INFORME
    }
    variantes = {
        normalizar_titulo_seccion("Los núcleos que organizan tu experiencia"):
            "Los núcleos que organizan tu carta",
        normalizar_titulo_seccion("Cómo funcionan juntas las distintas partes"):
            "Cómo se relacionan las distintas partes",
        normalizar_titulo_seccion("Dónde se expresa tu arquitectura"):
            "Dónde se expresa esta arquitectura",
    }

    salida = []
    for linea in texto.splitlines():
        coincidencia = re.match(r"^#{1,6}\s+(.+?)\s*$", linea.strip())
        if coincidencia:
            titulo = coincidencia.group(1).strip()
            clave = normalizar_titulo_seccion(titulo)
            if clave in variantes:
                linea = "## " + variantes[clave]
            elif clave in mapa:
                linea = "## " + mapa[clave]
        salida.append(linea)

    return "\n".join(salida)




def construir_esquema_nucleos_global(contexto_compacto):
    """
    Convierte los núcleos calculados por Python en una lista canónica.

    Admite:
    - parejas atómicas;
    - conjunciones colectivas;
    - stelliums colectivos.

    Un stellium no se divide aquí en Mercurio-Venus,
    Mercurio-Marte, Venus-Marte, etc.
    """
    nucleos = (
        contexto_compacto
        .get("figuras", {})
        .get("arquitectura", {})
        .get("nucleos", [])
    ) or []

    unicos = {}

    for nucleo in nucleos:
        puntos = tuple(
            Figuras.ordenar_puntos(
                [
                    str(p).strip()
                    for p in (
                        nucleo.get(
                            "puntos_nucleo",
                            [],
                        )
                        or []
                    )
                    if str(p).strip()
                ]
            )
        )

        if len(puntos) < 2:
            continue

        tipo_nucleo = (
            nucleo.get("tipo_nucleo")
            or "pareja"
        ).strip().casefold()

        clave = (
            tipo_nucleo,
            puntos,
        )

        actual = unicos.get(clave)

        if actual is None:
            unicos[clave] = nucleo
            continue

        criterio_nuevo = (
            nucleo.get(
                "puntuacion_nucleo",
                0,
            )
            or 0,
            nucleo.get(
                "apariciones",
                0,
            )
            or 0,
        )

        criterio_actual = (
            actual.get(
                "puntuacion_nucleo",
                0,
            )
            or 0,
            actual.get(
                "apariciones",
                0,
            )
            or 0,
        )

        if criterio_nuevo > criterio_actual:
            unicos[clave] = nucleo

    ordenados = sorted(
        unicos.items(),
        key=lambda item: (
            -(
                item[1].get(
                    "puntuacion_nucleo",
                    0,
                )
                or 0
            ),
            -(
                item[1].get(
                    "apariciones",
                    0,
                )
                or 0
            ),
            -len(item[0][1]),
            item[0][1],
        ),
    )

    salida = []

    for indice, (
        (tipo_nucleo, puntos),
        nucleo,
    ) in enumerate(
        ordenados,
        start=1,
    ):
        if tipo_nucleo == "stellium":
            etiqueta_tecnica = (
                "Stellium "
                + " · ".join(puntos)
            )
        elif tipo_nucleo in (
            "conjunción",
            "conjuncion",
        ):
            etiqueta_tecnica = (
                "Conjunción "
                + " · ".join(puntos)
            )
        else:
            etiqueta_tecnica = (
                "Núcleo "
                + "·".join(puntos)
            )

        salida.append({
            "id_nucleo": (
                f"nucleo_{indice:03d}"
            ),
            "tipo_nucleo": tipo_nucleo,
            "puntos": list(puntos),
            "etiqueta_tecnica": (
                etiqueta_tecnica
            ),
            "apariciones": (
                nucleo.get(
                    "apariciones"
                )
            ),
            "puntuacion_nucleo": (
                nucleo.get(
                    "puntuacion_nucleo"
                )
            ),
            "jerarquia_nucleo": (
                nucleo.get(
                    "jerarquia_nucleo"
                )
            ),
        })

    return salida

def construir_json_schema_global(contexto_compacto):
    """
    Esquema estricto de la lectura global.

    La sección de núcleos NO es texto libre: contiene exactamente
    un objeto por núcleo calculado por Python. Así un mismo núcleo
    no puede aparecer dos veces ni cambiar de nombre.
    """
    propiedades = {}

    for clave in CLAVES_SECCIONES_GLOBALES:
        if clave == "donde_se_expresa":
            propiedades[clave] = {
                "type": "object",
                "properties": {
                    "titulo": {"type": "string"},
                    "referencia": {"type": "string"},
                    "desarrollo": {"type": "string"},
                },
                "required": [
                    "titulo",
                    "referencia",
                    "desarrollo",
                ],
                "additionalProperties": False,
            }
            continue

        if clave != "nucleos":
            propiedades[clave] = {"type": "string"}
            continue

        esquema_nucleos = construir_esquema_nucleos_global(
            contexto_compacto
        )

        propiedades_nucleos = {}
        requeridos_nucleos = []

        for nucleo in esquema_nucleos:
            id_nucleo = nucleo["id_nucleo"]
            propiedades_nucleos[id_nucleo] = {
                "type": "object",
                "properties": {
                    "titulo_humano": {"type": "string"},
                    "interpretacion": {"type": "string"},
                },
                "required": [
                    "titulo_humano",
                    "interpretacion",
                ],
                "additionalProperties": False,
            }
            requeridos_nucleos.append(id_nucleo)

        propiedades[clave] = {
            "type": "object",
            "properties": propiedades_nucleos,
            "required": requeridos_nucleos,
            "additionalProperties": False,
        }

    return {
        "type": "object",
        "properties": propiedades,
        "required": list(CLAVES_SECCIONES_GLOBALES),
        "additionalProperties": False,
    }



def construir_markdown_global_desde_estructurado(datos, contexto_compacto):
    """
    Python crea los ocho encabezados principales y también las etiquetas
    técnicas de los núcleos. La IA solo escribe el título humano y el texto.
    """
    if not isinstance(datos, dict):
        raise RuntimeError(
            "La interpretación global estructurada no es un objeto JSON."
        )

    faltantes = [
        clave
        for clave in CLAVES_SECCIONES_GLOBALES
        if clave not in datos
    ]

    if faltantes:
        raise RuntimeError(
            "La interpretación global no contiene todas las secciones: "
            + ", ".join(faltantes)
        )

    partes = []

    for clave in CLAVES_SECCIONES_GLOBALES:
        partes.append("## " + TITULO_POR_CLAVE_SECCION[clave])
        partes.append("")

        if clave == "nucleos":
            esquema_nucleos = construir_esquema_nucleos_global(
                contexto_compacto
            )
            datos_nucleos = datos.get("nucleos", {})

            for nucleo in esquema_nucleos:
                id_nucleo = nucleo["id_nucleo"]
                contenido = datos_nucleos.get(id_nucleo)

                if not isinstance(contenido, dict):
                    raise RuntimeError(
                        f"Falta el desarrollo estructurado de {id_nucleo}."
                    )

                titulo_humano = str(
                    contenido.get("titulo_humano", "")
                ).strip()
                interpretacion = str(
                    contenido.get("interpretacion", "")
                ).strip()

                if not titulo_humano or not interpretacion:
                    raise RuntimeError(
                        f"El núcleo {id_nucleo} no tiene título o interpretación."
                    )

                partes.append("### " + titulo_humano)
                partes.append(nucleo["etiqueta_tecnica"])
                partes.append("")
                partes.append(interpretacion)
                partes.append("")

            continue

        if clave == "donde_se_expresa":
            donde = datos.get(clave) or {}

            if not isinstance(donde, dict):
                raise RuntimeError(
                    "La sección global donde_se_expresa no tiene "
                    "la estructura esperada."
                )

            titulo = str(donde.get("titulo") or "").strip()
            referencia = str(
                donde.get("referencia") or ""
            ).strip()
            desarrollo = str(
                donde.get("desarrollo") or ""
            ).strip()

            if not titulo or not referencia or not desarrollo:
                raise RuntimeError(
                    "Dónde se expresa esta arquitectura debe incluir "
                    "título, referencia y desarrollo."
                )

            partes.append(titulo)
            partes.append(referencia)
            partes.append("")
            partes.append(desarrollo)
            partes.append("")
            continue

        contenido = str(datos.get(clave, "") or "").strip()

        if not contenido:
            raise RuntimeError(
                f"La sección global {clave} está vacía."
            )

        lineas = contenido.splitlines()

        if (
            lineas
            and normalizar_titulo_seccion(lineas[0])
            == normalizar_titulo_seccion(
                TITULO_POR_CLAVE_SECCION[clave]
            )
        ):
            lineas = lineas[1:]
            contenido = "\n".join(lineas).strip()

        partes.append(contenido)
        partes.append("")

    return "\n".join(partes).strip()


def validar_nucleos_unicos_en_texto(texto, contexto_compacto):
    """
    Comprueba que cada núcleo calculado aparezca exactamente una vez.
    Es una validación local: no realiza llamadas a OpenAI.
    """
    if not texto:
        return

    esquema = construir_esquema_nucleos_global(
        contexto_compacto
    )

    errores = []

    for nucleo in esquema:
        etiqueta = nucleo["etiqueta_tecnica"]
        veces = sum(
            1
            for linea in texto.splitlines()
            if linea.strip() == etiqueta
        )

        if veces != 1:
            errores.append(
                f"{etiqueta}: {veces} apariciones"
            )

    if errores:
        raise RuntimeError(
            "La sección de núcleos no es única o está incompleta:\n- "
            + "\n- ".join(errores)
        )


def detectar_secciones_faltantes(texto):
    """Comprueba que las ocho secciones editoriales existan."""
    if not texto:
        return list(SECCIONES_INFORME)
    encabezados = [
        coincidencia.group(1)
        for coincidencia in re.finditer(
            r"^##\s+(.+?)\s*$",
            texto,
            flags=re.MULTILINE,
        )
    ]
    normalizados = {
        normalizar_titulo_seccion(titulo)
        for titulo in encabezados
    }
    return [
        titulo
        for titulo in SECCIONES_INFORME
        if normalizar_titulo_seccion(titulo) not in normalizados
    ]


def detectar_figuras_duplicadas(texto, contexto_compacto):
    """Detecta títulos técnicos de figuras insertados más de una vez."""
    duplicadas = []
    for titulo in obtener_titulos_figuras_esperadas(contexto_compacto):
        marcador = f"**{titulo}**"
        if texto.count(marcador) > 1:
            duplicadas.append(titulo)
    return duplicadas


def detectar_coletillas_conversacionales(texto):
    """Detecta cierres o comentarios propios de una conversación con IA."""
    if not texto:
        return []
    patrones = {
        "si quieres, puedo": r"\bsi quieres\b[^\n.!?]{0,120}\bpuedo\b",
        "si lo deseas, puedo": r"\bsi lo deseas\b[^\n.!?]{0,120}\bpuedo\b",
        "en el siguiente paso": r"\ben el siguiente paso\b",
        "puedo convertir": r"\bpuedo convertir\b",
        "puedo ayudarte": r"\bpuedo ayudarte\b",
        "quieres que": r"\bquieres que\b",
    }
    return [
        nombre
        for nombre, patron in patrones.items()
        if re.search(patron, texto, flags=re.IGNORECASE)
    ]


def eliminar_coletillas_conversacionales(texto):
    """Elimina párrafos completos que sean claramente una oferta de IA."""
    if not texto:
        return texto
    bloques = re.split(r"(\n\s*\n)", texto)
    resultado = []
    for bloque in bloques:
        if re.fullmatch(r"\n\s*\n", bloque):
            resultado.append(bloque)
            continue
        if detectar_coletillas_conversacionales(bloque):
            continue
        resultado.append(bloque)
    return "".join(resultado).strip()


def validar_interpretaciones_figuras_finales(
    contexto_compacto,
    interpretaciones_figuras,
):
    """Barrera final de las figuras después de todas las correcciones."""
    # Validamos únicamente las figuras que requieren bloque independiente.
    # Un Stellium exacto ya desarrollado como núcleo permanece en la
    # arquitectura, pero no debe exigirse de nuevo en la salida de figuras.
    figuras = (
        contexto_compacto
        .get("figuras", {})
        .get("arquitectura", {})
        .get("figuras", [])
        or []
    )
    figuras = _figuras_con_bloque_independiente(
        figuras,
        contexto_compacto,
    )

    puntos_catalogo = list(
        contexto_compacto
        .get("figuras", {})
        .get("posiciones_natales", {})
        .keys()
    )
    for figura in figuras:
        id_figura = figura.get("id_figura", "").strip()
        datos = interpretaciones_figuras.get(id_figura, {})
        titulo = (datos.get("titulo_humano", "") or "").strip()
        interpretacion = (datos.get("interpretacion", "") or "").strip()
        if not titulo or not interpretacion:
            raise RuntimeError(
                "Faltan datos finales en "
                f"{id_figura} · "
                f"{figura.get('tipo') or figura.get('nombre_canonico') or ''} · "
                f"{figura.get('titulo_salida') or ''}. "
                f"titulo_humano={'OK' if titulo else 'VACÍO'}; "
                f"interpretacion={'OK' if interpretacion else 'VACÍA'}."
            )
        texto_completo = titulo + "\n" + interpretacion
        genero = detectar_genero_dirigido_a_lector(texto_completo)
        if genero:
            print(
                f"AVISO FINAL {id_figura}: lenguaje de genero: "
                + ", ".join(genero)
            )
        neutralizaciones = detectar_neutralizaciones_artificiales(texto_completo)
        if neutralizaciones:
            print(
                f"AVISO FINAL {id_figura}: neutralizaciones artificiales: "
                + ", ".join(neutralizaciones)
            )
        letras = detectar_letras_no_latinas(texto_completo)
        if letras:
            print(
                f"AVISO FINAL {id_figura}: letras no latinas: "
                + ", ".join(letras)
            )
        puntos_ajenos = detectar_puntos_ajenos_en_figura(
            texto_completo,
            figura.get("puntos", []),
            puntos_catalogo,
        )
        if puntos_ajenos:
            raise RuntimeError(
                f"La validación final de {id_figura} ha detectado "
                "puntos ajenos: " + ", ".join(puntos_ajenos)
            )
        coletillas = detectar_coletillas_conversacionales(texto_completo)
        if coletillas:
            print(
                f"AVISO FINAL {id_figura}: coletilla conversacional: "
                + ", ".join(coletillas)
            )
    return True



def corregir_calidad_semantica_final(
    client,
    texto,
):
    """V33: la corrección semántica restrictiva queda desactivada."""
    return texto


def validar_informe_final(texto, contexto_compacto):
    """
    Barrera final antes del PDF.

    Errores estructurales (secciones, figuras, duplicados, puntos/núcleos
    imposibles) siguen siendo fatales. Cuestiones editoriales se informan
    como avisos para no perder una generación válida.
    """
    if not texto:
        raise RuntimeError("El informe final está vacío.")

    secciones_faltantes = detectar_secciones_faltantes(texto)
    if secciones_faltantes:
        raise RuntimeError(
            "Faltan secciones en el informe final:\n- "
            + "\n- ".join(secciones_faltantes)
        )

    figuras_faltantes = detectar_figuras_faltantes(texto, contexto_compacto)
    if figuras_faltantes:
        raise RuntimeError(
            "Faltan figuras o desarrollos en el informe final:\n- "
            + "\n- ".join(figuras_faltantes)
        )

    figuras_duplicadas = detectar_figuras_duplicadas(texto, contexto_compacto)
    if figuras_duplicadas:
        raise RuntimeError(
            "Hay figuras duplicadas en el informe final:\n- "
            + "\n- ".join(figuras_duplicadas)
        )

    nucleos_indebidos = detectar_etiquetas_nucleo_no_autorizadas(
        texto,
        contexto_compacto,
    )
    if nucleos_indebidos:
        raise RuntimeError(
            "El informe final contiene etiquetas de núcleo no calculadas por Python:\n- "
            + "\n- ".join(nucleos_indebidos)
        )

    avisos = []
    letras = detectar_letras_no_latinas(texto)
    if letras:
        avisos.append("letras no latinas: " + ", ".join(letras))

    genero = detectar_genero_dirigido_a_lector(texto)
    if genero:
        avisos.append("lenguaje de género: " + ", ".join(genero))

    neutralizaciones = detectar_neutralizaciones_artificiales(texto)
    if neutralizaciones:
        avisos.append("neutralizaciones artificiales: " + ", ".join(neutralizaciones))


    coletillas = detectar_coletillas_conversacionales(texto)
    if coletillas:
        avisos.append("coletillas conversacionales: " + ", ".join(coletillas))

    referencias_internas = detectar_referencias_internas_fuentes(texto)
    if referencias_internas:
        avisos.append(
            "referencias internas visibles: "
            + ", ".join(referencias_internas)
        )

    for aviso in avisos:
        print("AVISO FINAL: " + aviso)

    genero_marcado = detectar_genero_marcado_lector_2026(
        texto
    )
    if genero_marcado:
        raise RuntimeError(
            "Queda género marcado dirigido a la persona lectora: "
            + "; ".join(genero_marcado[:8])
        )

    return True

def generar_interpretacion_arte_encarnarte(
    contexto_compacto,
):
    """
    Genera la interpretación global de
    El Arte de Encarnarte.

    Las figuras individuales NO se generan aquí.
    Se generan por separado mediante Structured Outputs
    y posteriormente se integran en el informe.
    """

    api_key = os.getenv(
        "OPENAI_API_KEY"
    )

    # MODO_MANUAL_ANTES_API_KEY_V2
    if MODO_IA_MANUAL:
        interpretacion_manual, ruta_manual = (
            cargar_interpretacion_manual_chatgpt(
                nombre_f
            )
        )

        if interpretacion_manual is None:
            ruta_paquete = (
                exportar_paquete_manual_chatgpt(
                    nombre=nombre,
                    fecha=fecha,
                    hora=hora,
                    lugar=lugar,
                    nombre_f=nombre_f,
                    contexto_compacto=contexto_compacto,
                )
            )

            print()
            print(
                "MODO MANUAL CHATGPT ACTIVADO."
            )
            print(
                "Paquete preparado:"
            )
            print(
                os.path.abspath(
                    ruta_paquete
                )
            )
            print()
            print(
                "Súbeme ese JSON en ChatGPT."
            )
            print(
                "Te devolveré el archivo:"
            )
            print(
                os.path.abspath(
                    ruta_manual
                )
            )
            print(
                "Guárdalo en esta carpeta "
                "y vuelve a ejecutar el programa."
            )
            return

        print()
        print(
            "Interpretación manual encontrada:"
        )
        print(
            os.path.abspath(
                ruta_manual
            )
        )

        interpretacion = (
            normalizar_formato_manual_chatgpt(interpretacion_manual, contexto_compacto)
        )

        interpretacion = (
            eliminar_coletillas_conversacionales(
                interpretacion
            )
        )

        validar_informe_final(
            interpretacion,
            contexto_compacto,
        )

        with open(
            "diagnostico_informe_integrado.txt",
            "w",
            encoding="utf-8",
        ) as archivo:
            archivo.write(
                interpretacion
            )

        ruta_txt = (
            f"{nombre_f}_arte_encarnarte_prueba.txt"
        )

        with open(
            ruta_txt,
            "w",
            encoding="utf-8",
        ) as archivo:
            archivo.write(
                interpretacion
            )

        ruta_pdf = (
            f"{nombre_f}_Arte_de_Encarnarte.pdf"
        )

        generar_pdf_arte_encarnarte(
            nombre=nombre,
            fecha=fecha,
            hora=hora,
            lugar=lugar,
            interpretacion=interpretacion,
            ruta_rueda=ruta_rueda,
            ruta_pdf=ruta_pdf,
            miniaturas_figuras=miniaturas_figuras,
        )

        print()
        print(
            "PDF generado correctamente:"
        )
        print(
            os.path.abspath(
                ruta_pdf
            )
        )
        return

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY no está configurada."
        )

    guia_estilo = cargar_guia_estilo_arte_encarnarte()

    client = OpenAI(
        api_key=api_key
    )

    prompt = construir_prompt_arte_encarnarte(
        contexto_compacto,
        guia_estilo=guia_estilo,
    )

    instrucciones_biblioteca = instrucciones_biblioteca_astrologica(
        "global"
    )

    print(
        "Generando interpretación global con biblioteca astrológica..."
    )

    prompt_estructurado = (
        instrucciones_biblioteca
        + "\n\n"
        + prompt
        + """


FORMATO DE SALIDA OBLIGATORIO

Devuelve las ocho secciones en los ocho campos del JSON estructurado.

Siete secciones son texto.

La sección "nucleos" es un objeto estructurado con un campo por cada
id_nucleo calculado por Python. Debes devolver exactamente esos IDs,
una sola vez cada uno, con:
- titulo_humano
- interpretacion

No escribas las etiquetas técnicas "Núcleo X·Y": Python las añadirá.

No escribas los encabezados principales dentro de los valores:
Python los añadirá después. Puedes usar párrafos y, en las secciones de
texto libre, subtítulos breves cuando realmente ayuden a la lectura.
"""
    )

    vector_store_id = cargar_vector_store_biblioteca_astrologica()

    response = client.responses.create(
        model="gpt-5.4-mini",
        input=prompt_estructurado,
        tools=[
            herramienta_file_search_biblioteca_astrologica(
                vector_store_id,
                max_num_results=24,
            )
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "interpretacion_global_arte_encarnarte",
                "strict": True,
                "schema": construir_json_schema_global(contexto_compacto),
            }
        },
    )

    if not response.output_text:
        raise RuntimeError("OpenAI no ha devuelto la interpretación global.")

    try:
        datos_globales = json.loads(response.output_text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "La respuesta global estructurada no contiene JSON válido."
        ) from exc

    texto = construir_markdown_global_desde_estructurado(
        datos_globales,
        contexto_compacto,
    )

    # ---------------------------------------------------------
    # POSTPROCESADO LOCAL
    # Sin nuevas llamadas a OpenAI.
    # ---------------------------------------------------------

    texto = neutralizar_teleologia_residual(
        texto
    )

    texto = corregir_conjunciones_disyuntivas(
        texto
    )

    texto = corregir_letras_no_latinas(
        None,
        texto,
    )

    texto = corregir_genero_dirigido_local(
        texto
    )

    # Cierre editorial determinista final también para la lectura global.
    texto = cierre_editorial_local_final(
        texto
    )

    texto = asegurar_retrogradacion_en_global(
        texto,
        contexto_compacto,
    )

    # Pasada editorial definitiva después de cualquier inserción local.
    texto = cierre_editorial_local_final(
        texto
    )

    validar_nucleos_unicos_en_texto(
        texto,
        contexto_compacto,
    )

    nucleos_no_autorizados = (
        detectar_etiquetas_nucleo_no_autorizadas(
            texto,
            contexto_compacto,
        )
    )

    if nucleos_no_autorizados:
        print(
            "AVISO: etiquetas de nucleo no autorizadas detectadas. "
            "Se eliminan localmente."
        )

        texto = (
            eliminar_etiquetas_nucleo_no_autorizadas(
                texto,
                contexto_compacto,
            )
        )

    genero_final = (
        detectar_genero_dirigido_a_lector(
            texto
        )
    )

    if genero_final:
        print(
            "AVISO GLOBAL: lenguaje de genero detectado: "
            + ", ".join(genero_final)
        )

    teleologia_final = (
        detectar_lenguaje_teleologico(
            texto
        )
    )

    if teleologia_final:
        print(
            "AVISO GLOBAL: lenguaje teleologico residual: "
            + ", ".join(teleologia_final)
        )

    letras_no_latinas_final = (
        detectar_letras_no_latinas(
            texto
        )
    )

    if letras_no_latinas_final:
        print(
            "AVISO GLOBAL: caracteres no latinos detectados: "
            + ", ".join(letras_no_latinas_final)
        )

    figuras_indebidas = (
        detectar_figuras_desarrolladas_en_global(
            texto,
            contexto_compacto,
        )
    )

    if figuras_indebidas:
        print(
            "AVISO GLOBAL: se han detectado figuras "
            "desarrolladas en el texto global: "
            + ", ".join(figuras_indebidas)
        )

    figuras_reconstruidas = (
        detectar_figuras_reconstruidas_en_global(
            texto,
            contexto_compacto,
        )
    )

    if figuras_reconstruidas:
        print(
            "AVISO GLOBAL: posibles figuras reconstruidas: "
            + ", ".join(figuras_reconstruidas)
        )

    return texto

def limpiar_markdown_para_pdf(texto):
    """
    Convierte el Markdown básico generado por la IA
    en etiquetas compatibles con ReportLab Paragraph.
    """

    if not texto:
        return ""

    texto = (
        texto
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

    # Negrita Markdown → ReportLab
    while "**" in texto:
        partes = texto.split("**", 2)

        if len(partes) < 3:
            break

        texto = (
            partes[0]
            + "<b>"
            + partes[1]
            + "</b>"
            + partes[2]
        )

    # Cursiva Markdown simple → ReportLab
    while "*" in texto:
        partes = texto.split("*", 2)

        if len(partes) < 3:
            break

        texto = (
            partes[0]
            + "<i>"
            + partes[1]
            + "</i>"
            + partes[2]
        )

    # Separadores Markdown
    if texto.strip() in (
        "---",
        "___",
        "***",
    ):
        return ""

    return texto

HUBER_FASE10B_MINIATURAS_DINAMICAS_46 = True


def buscar_miniatura_figura(
    titulo,
    miniaturas_figuras,
):
    import re

    if not titulo or not miniaturas_figuras:
        return None

    titulo_limpio = titulo.replace("**", "").strip()

    tipos_figura = sorted(
        {
            str(m.get("tipo", "")).strip()
            for m in miniaturas_figuras
            if str(m.get("tipo", "")).strip()
        },
        key=len,
        reverse=True,
    )

    tipo_encontrado = None
    for tipo in tipos_figura:
        if titulo_limpio.startswith(tipo):
            tipo_encontrado = tipo
            break

    if not tipo_encontrado:
        return None

    resto = titulo_limpio[len(tipo_encontrado):].strip()

    puntos_catalogo = [
        "Sol", "Luna", "Mercurio", "Venus", "Marte",
        "Júpiter", "Saturno", "Urano", "Neptuno", "Plutón",
        "Quirón", "Lilith", "Nodo Norte", "Nodo Sur",
        "Ascendente", "Medio Cielo",
    ]

    puntos_titulo = {
        punto
        for punto in puntos_catalogo
        if re.search(
            rf"(?<!\w){re.escape(punto)}(?!\w)",
            resto,
            flags=re.IGNORECASE,
        )
    }

    if not puntos_titulo:
        return None

    for miniatura in miniaturas_figuras:
        if str(miniatura.get("tipo", "")).strip() != tipo_encontrado:
            continue

        puntos_miniatura = set(miniatura.get("puntos", []) or [])

        if puntos_miniatura == puntos_titulo:
            return miniatura.get("ruta")

    return None


def dividir_parrafo_para_miniatura(texto_parrafo, max_palabras=78):
    """
    Divide un párrafo largo de figura en dos partes.

    La primera acompaña a la miniatura.
    La segunda continúa debajo a ancho completo.

    Se corta preferentemente al final de una frase y nunca por mitad
    de palabra. Si el párrafo es corto, se deja entero junto a la imagen.
    """
    if not texto_parrafo:
        return texto_parrafo, ""

    palabras = texto_parrafo.split()

    if len(palabras) <= max_palabras:
        return texto_parrafo, ""

    # Buscamos un final de frase cerca del límite.
    candidatos = []

    for m in re.finditer(
        r'(?<=[.!?])\s+',
        texto_parrafo
    ):
        izquierda = texto_parrafo[:m.start()].strip()
        num_palabras = len(izquierda.split())

        if 45 <= num_palabras <= max_palabras:
            candidatos.append((num_palabras, m.start()))

    if candidatos:
        _, corte = candidatos[-1]
        return (
            texto_parrafo[:corte].strip(),
            texto_parrafo[corte:].strip(),
        )

    # Si no hay un final de frase adecuado, buscamos uno algo más adelante.
    for m in re.finditer(
        r'(?<=[.!?])\s+',
        texto_parrafo
    ):
        izquierda = texto_parrafo[:m.start()].strip()
        num_palabras = len(izquierda.split())

        if max_palabras < num_palabras <= 95:
            return (
                texto_parrafo[:m.start()].strip(),
                texto_parrafo[m.start():].strip(),
            )

    # Último recurso: corte por palabras.
    primera = " ".join(palabras[:max_palabras]).strip()
    resto = " ".join(palabras[max_palabras:]).strip()

    return primera, resto


def generar_pdf_arte_encarnarte(
    nombre,
    fecha,
    hora,
    lugar,
    interpretacion,
    ruta_rueda,
    ruta_pdf,
    miniaturas_figuras=None,

):
    """
    Genera el informe PDF de Arquitectura Natal
    de El Arte de Encarnarte.

    Incluye:
    - portada;
    - rueda de arquitectura;
    - interpretación integrada generada por IA.
    """

    if miniaturas_figuras is None:
        miniaturas_figuras = []

    estilos = crear_estilos_pdf()

    estilo_titulo2_figura = estilos["subtitulo2"].clone(
        "Titulo2Figura"
    )
    estilo_titulo2_figura.spaceAfter = 2

    estilo_titulo3_figura = estilos["subtitulo3"].clone(
        "Titulo3Figura"
    )
    estilo_titulo3_figura.spaceBefore = 0

    def dibujar_pie_portada(canvas, doc):
        canvas.saveState()

        canvas.setFont(
            "Times-Italic",
            10,
        )

        canvas.setFillColor(
            colors.HexColor("#666666")
        )

        canvas.drawCentredString(
            A4[0] / 2,
            1.6 * cm,
            (
                "Arquitectura Interna · "
                "Un método para sostener cuerpo, "
                "energía y vida con coherencia"
            ),
        )

        canvas.restoreState()

    doc = SimpleDocTemplate(
        ruta_pdf,
        pagesize=A4,
        rightMargin=2.2 * cm,
        leftMargin=2.2 * cm,
        topMargin=2.0 * cm,
        bottomMargin=2.0 * cm,
        title=f"El Arte de Encarnarte · {nombre}",
        author="Arquitectura Interna",
    )

    elementos = []

    # ── PORTADA ───────────────────────────────────────

    elementos.append(
        Spacer(
            1,
            2.4 * cm,
        )
    )

    elementos.append(
        Paragraph(
            "El Arte de Encarnarte",
            estilos["titulo"],
        )
    )

    elementos.append(
        Spacer(
            1,
            0.25 * cm,
        )
    )

    elementos.append(
        Paragraph(
            "Arquitectura Interna",
            estilos["centro"],
        )
    )

    elementos.append(
        Spacer(
            1,
            0.8 * cm,
        )
    )

    elementos.append(
        Paragraph(
            "Una lectura integrada de las figuras, "
            "núcleos y estructuras que organizan "
            "tu carta natal.",
            estilos["estilo_frase_final"],
        )
    )

    elementos.append(
        Spacer(
            1,
            1.5 * cm,
        )
    )

    elementos.append(
        Paragraph(
            f"<b>{nombre}</b>",
            estilos["centro"],
        )
    )

    elementos.append(
        Spacer(
            1,
            0.35 * cm,
        )
    )

    elementos.append(
        Paragraph(
            f"{fecha} · {hora}",
            estilos["centro"],
        )
    )

    elementos.append(
        Paragraph(
            lugar,
            estilos["centro"],
        )
    )

    elementos.append(
        PageBreak()
    )

    # ── RUEDA DE ARQUITECTURA ────────────────────────

    elementos.append(
        Paragraph(
            "Tu arquitectura natal",
            estilos["subtitulo"],
        )
    )

    elementos.append(
        Spacer(
            1,
            0.3 * cm,
        )
    )

    elementos.append(
        Paragraph(
            "Esta rueda muestra la red completa de aspectos "
            "calculados entre los puntos de tu carta. "
            "A partir de estas relaciones se detectan las figuras "
            "y estructuras que se desarrollan a continuación. "
            "Los puntos señalados indican aquellos que cumplen "
            "una función organizadora dentro del conjunto.",
            estilos["cuerpo"],
        )
    )

    elementos.append(
        Spacer(
            1,
            0.4 * cm,
        )
    )

    if os.path.exists(ruta_rueda):

        rueda = Image(
            ruta_rueda,
            width=16.0 * cm,
            height=16.0 * cm,
        )

        rueda.hAlign = "CENTER"

        elementos.append(
            rueda
        )

    else:
        elementos.append(
            Paragraph(
                "No se ha podido cargar la rueda "
                "de arquitectura.",
                estilos["cuerpo"],
            )
        )

    elementos.append(
        PageBreak()
    )

    # ── INTERPRETACIÓN ────────────────────────────────

    lineas = interpretacion.splitlines()

    titulos_pendientes = []

    miniatura_pendiente = None

    for linea in lineas:

        linea = linea.strip()

        if not linea:
            continue

        # ── TÍTULO 1 ─────────────────────────────────
        # Dorado grande

        linea_sin_markdown = re.sub(
            r"^#{1,3}\s*",
            "",
            linea,
        ).strip()

        if re.match(
            r"^\d+\.\s+",
            linea_sin_markdown,
        ):

            titulo_limpio = re.sub(
                r"^\d+\.\s*",
                "",
                linea_sin_markdown,
            ).strip()

            titulo_limpio = (
                titulo_limpio[0].upper()
                + titulo_limpio[1:].lower()
                if titulo_limpio
                else ""
            )

            reemplazos_titulos = {
                "Los núcleos que organizan tu experiencia":
                    "Los núcleos que organizan tu carta",

                "Cómo funcionan juntas las distintas partes":
                    "Cómo se relacionan las distintas partes",

                "Dónde se expresa tu arquitectura":
                    "Dónde se expresa esta arquitectura",
            }

            titulo_limpio = reemplazos_titulos.get(
                titulo_limpio,
                titulo_limpio,
            )

            titulos_pendientes.append(
                Paragraph(
                    limpiar_markdown_para_pdf(
                        titulo_limpio
                    ),
                    estilos["subtitulo"],
                )
            )

            continue

        # ── TÍTULO 2 ─────────────────────────────────
        # Azul grande

        if linea.startswith("### "):

            titulos_pendientes.append(
                Paragraph(
                    limpiar_markdown_para_pdf(
                        linea[4:]
                    ),
                    estilos["subtitulo2"],
                )
            )

            continue

        # ── TÍTULO 3 ─────────────────────────────────
        # Negro / gris oscuro, pequeño.
        # Si corresponde exactamente a una figura
        # detectada, guardamos también su miniatura.

        if (
            linea.startswith("**")
            and linea.endswith("**")
            and len(linea) > 4
        ):

            titulo_figura = linea[2:-2].strip()

            titulos_pendientes.append(
                Paragraph(
                    limpiar_markdown_para_pdf(
                        titulo_figura
                    ),
                    estilos["subtitulo3"],
                )
            )

            ruta_miniatura = buscar_miniatura_figura(
                titulo_figura,
                miniaturas_figuras,
            )

            if (
                ruta_miniatura
                and os.path.exists(ruta_miniatura)
            ):
                miniatura_pendiente = ruta_miniatura

            continue

        # ── SUBTÍTULO TÉCNICO DE NÚCLEO ──────────────
        # "Núcleo X·Y" debe viajar junto al título humano
        # y al primer párrafo, para no quedar huérfano
        # al final de una página.

        if re.match(
            r"^Núcleo\s+",
            linea,
            flags=re.IGNORECASE,
        ):
            titulos_pendientes.append(
                Paragraph(
                    limpiar_markdown_para_pdf(
                        linea
                    ),
                    estilos["subtitulo3"],
                )
            )
            continue

        # ── MARKDOWN DE RESPALDO ──────────────────────

        if linea.startswith("## "):

            titulos_pendientes.append(
                Paragraph(
                    limpiar_markdown_para_pdf(
                        linea[3:]
                    ),
                    estilos["subtitulo2"],
                )
            )

            continue

        if linea.startswith("# "):

            titulos_pendientes.append(
                Paragraph(
                    limpiar_markdown_para_pdf(
                        linea[2:]
                    ),
                    estilos["subtitulo"],
                )
            )

            continue

        # ── TEXTO NORMAL ───────────────────────────────

        texto_parrafo = limpiar_markdown_para_pdf(
            linea
        )

        if not texto_parrafo:
            continue

        parrafo = Paragraph(
            texto_parrafo,
            estilos["cuerpo"],
        )

        if titulos_pendientes:

            # Si este bloque corresponde a una figura,
            # colocamos títulos + primer párrafo
            # a la izquierda y la miniatura a la derecha.
            if miniatura_pendiente:

                elementos.append(
                    Spacer(
                        1,
                        0.35 * cm,
                    )
                )

                titulos_ajustados = []

                for titulo in titulos_pendientes:

                    if (
                        titulo.style.name
                        == estilos["subtitulo2"].name
                    ):
                        titulo = Paragraph(
                            titulo.text,
                            estilo_titulo2_figura,
                        )

                    elif (
                        titulo.style.name
                        == estilos["subtitulo3"].name
                    ):
                        titulo = Paragraph(
                            titulo.text,
                            estilo_titulo3_figura,
                        )

                    titulos_ajustados.append(
                        titulo
                    )

                imagen_figura = Image(
                    miniatura_pendiente,
                    width=4.2 * cm,
                    height=4.2 * cm,
                )

                imagen_figura.hAlign = "RIGHT"

                # Solo una parte del primer párrafo acompaña a la
                # miniatura. El resto continúa debajo a ancho completo,
                # como en la maquetación anterior.
                texto_lateral, texto_inferior = (
                    dividir_parrafo_para_miniatura(
                        texto_parrafo
                    )
                )

                parrafo_lateral = Paragraph(
                    texto_lateral,
                    estilos["cuerpo"],
                )

                bloque_texto = (
                    titulos_ajustados
                    + [parrafo_lateral]
                )

                tabla_figura = Table(
                    [
                        [
                            bloque_texto,
                            imagen_figura,
                        ]
                    ],
                    colWidths=[
                        11.8 * cm,
                        4.8 * cm,
                    ],
                )

                tabla_figura.setStyle(
                    TableStyle(
                        [
                            (
                                "VALIGN",
                                (0, 0),
                                (-1, -1),
                                "TOP",
                            ),

                            # El texto empieza exactamente en el mismo
                            # margen izquierdo que el resto del documento.
                            (
                                "LEFTPADDING",
                                (0, 0),
                                (0, 0),
                                0.15 * cm,
                            ),

                            # Un poco de aire entre texto y miniatura.
                            (
                                "RIGHTPADDING",
                                (0, 0),
                                (0, 0),
                                0.20 * cm,
                            ),

                            # La imagen no añade margen extra por su izquierda.
                            (
                                "LEFTPADDING",
                                (1, 0),
                                (1, 0),
                                0,
                            ),

                            (
                                "RIGHTPADDING",
                                (1, 0),
                                (1, 0),
                                0,
                            ),

                            (
                                "TOPPADDING",
                                (0, 0),
                                (-1, -1),
                                0,
                            ),

                            (
                                "BOTTOMPADDING",
                                (0, 0),
                                (-1, -1),
                                0,
                            ),
                        ]
                    )
                )

                elementos.append(
                    KeepTogether([
                        tabla_figura
                    ])
                )

                if texto_inferior:
                    elementos.append(
                        Paragraph(
                            texto_inferior,
                            estilos["cuerpo"],
                        )
                    )

                miniatura_pendiente = None

            else:

                elementos.append(
                    KeepTogether(
                        titulos_pendientes
                        + [parrafo]
                    )
                )

            titulos_pendientes = []

        else:

            elementos.append(
                parrafo
            )

    # Seguridad por si el documento terminase
    # inmediatamente después de uno o varios títulos.
    if titulos_pendientes:

        elementos.extend(
            titulos_pendientes
        )

    # ── CIERRE ────────────────────────────────────────

    elementos.append(
        Spacer(
            1,
            0.8 * cm,
        )
    )

    elementos.append(
        Paragraph(
            "ARQUITECTURA INTERNA · EL ARTE DE ENCARNARTE",
            estilos["estilo_frase_final"],
        )
    )

    doc.build(
        elementos,
        onFirstPage=dibujar_pie_portada,
    )

    return ruta_pdf


if __name__ == "__main__":

    nombre = "HAIZE"
    fecha = "18/07/2015"
    hora = "00:35"
    lugar = "PAMPLONA, ESPAÑA"
    lat = 42.8157
    lon = -1.6522
    tz_name = "Europe/Madrid"

    # ── TRATAMIENTO LINGÜÍSTICO ───────────────────────
    # Se elige al introducir los datos de cada persona.
    TRATAMIENTO_LINGUISTICO = (
        elegir_tratamiento_linguistico()
    )

    # ── CONTEXTO ASTROLÓGICO ──────────────────────────

    contexto_completo = generar_contexto_arte_encarnarte(
        nombre=nombre,
        fecha=fecha,
        hora=hora,
        lugar=lugar,
        lat=lat,
        lon=lon,
        tz_name=tz_name,
    )


    contexto_compacto = (
        construir_contexto_compacto_arte_encarnarte(
            contexto_completo
        )
    )

    print(
        "Contexto preparado:",
        len(
            json.dumps(
                contexto_compacto,
                ensure_ascii=False,
            )
        ),
        "caracteres"
    )

    # ── RUEDA DE ARQUITECTURA ─────────────────────────

    nombre_f = (
        nombre
        .replace(" ", "_")
        .replace("/", "-")
        .replace("\\", "-")
    )

    ruta_rueda = (
        f"{nombre_f}_arquitectura.png"
    )

    Figuras.dibujar_rueda_arquitectura(
        carta=contexto_completo["_carta_figuras"],
        aspectos_relevantes=(
            contexto_completo[
                "figuras"
            ][
                "aspectos_relevantes"
            ]
        ),
        puntos_organizadores=(
            contexto_completo[
                "figuras"
            ][
                "arquitectura"
            ][
                "puntos_organizadores"
            ]
        ),
        nombre_persona=nombre,
        archivo_salida=ruta_rueda,
    )

    # ── MINIATURAS DE FIGURAS ─────────────────────────

    carpeta_miniaturas = (
        f"{nombre_f}_miniaturas_figuras"
    )

    miniaturas_figuras = (
        Figuras.generar_miniaturas_figuras(
            carta=contexto_completo["_carta_figuras"],
            figuras=(
                contexto_completo[
                    "figuras"
                ][
                    "arquitectura"
                ][
                    "figuras"
                ]
            ),
            aspectos_relevantes=(
                contexto_completo[
                    "figuras"
                ][
                    "aspectos_relevantes"
                ]
            ),
            carpeta_salida=carpeta_miniaturas,
        )
    )

    print(
        "Miniaturas generadas:",
        len(miniaturas_figuras)
    )

    print(
        "Rueda generada:",
        os.path.abspath(
            ruta_rueda
        )
    )

    # ── INTERPRETACIÓN GLOBAL ─────────────────────────

    interpretacion_global = (
        generar_interpretacion_arte_encarnarte(
            contexto_compacto
        )
    )

    interpretacion_global = (
        normalizar_encabezados_secciones(
            interpretacion_global
        )
    )

    # V32 · Guardamos la lectura global de esta ejecución antes de
    # entrar en figuras. Es solo diagnóstico local; no cambia el flujo.
    with open(
        "diagnostico_global_actual.txt",
        "w",
        encoding="utf-8",
    ) as archivo:
        archivo.write(
            interpretacion_global
        )

    # ── FIGURAS ESTRUCTURADAS ─────────────────────────

    # MODO_MANUAL_CORTA_FLUJO_API_MAIN_V2
    if MODO_IA_MANUAL:
        print("Modo manual: flujo API posterior omitido.")
        raise SystemExit(0)

    interpretaciones_figuras = (
        generar_interpretaciones_figuras_estructuradas(
            contexto_compacto
        )
    )

    # Diagnóstico de la salida cruda de la llamada estructurada.
    # Permite revisar un fallo sin tener que volver a pagar la generación.
    with open(
        "diagnostico_figuras_estructuradas.json",
        "w",
        encoding="utf-8",
    ) as archivo:
        json.dump(
            interpretaciones_figuras,
            archivo,
            ensure_ascii=False,
            indent=2,
        )

    # La IA debe mantener cada figura aislada. Si excepcionalmente
    # mezcla puntos de otra figura, se repara EN LOTE antes de validar.
    interpretaciones_figuras = (
        corregir_puntos_ajenos_interpretaciones_figuras(
            contexto_compacto,
            interpretaciones_figuras,
        )
    )

    # Guardamos también la versión ya reparada/normalizada.
    with open(
        "diagnostico_figuras_finales.json",
        "w",
        encoding="utf-8",
    ) as archivo:
        json.dump(
            interpretaciones_figuras,
            archivo,
            ensure_ascii=False,
            indent=2,
        )

    validar_interpretaciones_figuras_finales(
        contexto_compacto,
        interpretaciones_figuras,
    )

    bloques_figuras = (
        construir_bloques_figuras(
            contexto_compacto,
            interpretaciones_figuras,
        )
    )

    print(
        "Bloques de figuras preparados:",
        len(bloques_figuras)
    )

    # ── INTEGRACIÓN DEL INFORME ───────────────────────

    interpretacion = (
        integrar_bloques_figuras_en_informe(
            interpretacion_global,
            bloques_figuras,
        )
    )

    interpretacion = (
        eliminar_coletillas_conversacionales(
            interpretacion
        )
    )

    # V33 · Cierre único sobre el informe ya integrado.
    interpretacion = cierre_editorial_local_final(
        interpretacion
    )

    # ── REVISIÓN SEMÁNTICA FINAL ─────────────────────
    # Una sola pasada editorial, acotada a problemas
    # claros. No funciona como una lista creciente de
    # palabras prohibidas.

    # Guardamos siempre el texto de esta ejecución antes de
    # validarlo. Así, si aparece un error, el diagnóstico no
    # corresponde a una generación anterior.
    with open(
        "diagnostico_informe_integrado.txt",
        "w",
        encoding="utf-8",
    ) as archivo:
        archivo.write(
            interpretacion
        )

    validar_informe_final(
        interpretacion,
        contexto_compacto,
    )

    print(
        "Informe integrado guardado para diagnóstico."
    )

    ruta_txt = (
        f"{nombre_f}_arte_encarnarte_prueba.txt"
    )

    with open(
        ruta_txt,
        "w",
        encoding="utf-8",
    ) as archivo:
        archivo.write(
            interpretacion
        )

    print(
        "Interpretación generada:",
        os.path.abspath(
            ruta_txt
        )
    )

    # ── PDF ───────────────────────────────────────────

    ruta_pdf = (
        f"{nombre_f}_Arte_de_Encarnarte.pdf"
    )

    generar_pdf_arte_encarnarte(
        nombre=nombre,
        fecha=fecha,
        hora=hora,
        lugar=lugar,
        interpretacion=interpretacion,
        ruta_rueda=ruta_rueda,
        ruta_pdf=ruta_pdf,
        miniaturas_figuras=miniaturas_figuras,
    )

    print()
    print(
        "PDF generado correctamente:"
    )

    print(
        os.path.abspath(
            ruta_pdf
        )
    )
