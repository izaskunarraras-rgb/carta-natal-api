import carta_natal_base
import luna_casa4_casa6
import sol_asc_nodos
import planetas_personales
import planetas_sociales
import planetas_transpersonales
import casas_por_signo
import Figuras
import copy
import json


def construir_contexto_cimientos(contenidos_ia):

    if not contenidos_ia:
        return {}

    return {
        "carta_base": contenidos_ia.get(
            "opCartaBase"
        ),

        "luna_casa4_casa6": contenidos_ia.get(
            "opLuna"
        ),

        "sol_asc_nodos": contenidos_ia.get(
            "opSolAscNodos"
        ),

        "planetas_personales": contenidos_ia.get(
            "opPersonales"
        ),

        "planetas_sociales": contenidos_ia.get(
            "opSociales"
        ),

        "planetas_transpersonales": contenidos_ia.get(
            "opTranspersonales"
        ),

        "casas_por_signo": contenidos_ia.get(
            "opCasas"
        ),
    }


def construir_contexto_arte_encarnarte(
    contenidos_ia,
    contenido_figuras,
):

    contexto_cimientos = construir_contexto_cimientos(
        contenidos_ia
    )

    return {
        "cimientos": contexto_cimientos,
        "figuras": contenido_figuras,
    }

def construir_contexto_maestro(
    contexto_cimientos,
    contenido_figuras=None,
):
    """
    Compatibilidad con el flujo existente de app.py.

    El Arte de Encarnarte utiliza su propio
    contexto mediante generar_contexto_arte_encarnarte().
    """

    return {
        "cimientos": contexto_cimientos,
        "figuras": contenido_figuras,
    }

def generar_contexto_arte_encarnarte(
    nombre,
    fecha,
    hora,
    lugar,
    lat,
    lon,
    tz_name,
):

    # ── FECHA Y HORA ──────────────────────────────────────

    dia, mes, anio = map(
        int,
        fecha.split("/")
    )

    hora_num, minuto = map(
        int,
        hora.split(":")
    )

    # ── CARTA MAESTRA ─────────────────────────────────────

    carta = carta_natal_base.calcular_carta(
        anio,
        mes,
        dia,
        hora_num,
        minuto,
        float(lat),
        float(lon),
        tz_name,
    )

    planetas = carta["planetas"]
    asc = carta["asc"]

    carta["arquitectura_casas"] = (
        casas_por_signo.calcular_arquitectura_casas(
            carta["cuspides"]
        )
    )

    # ── ASPECTOS DE CADA MÓDULO ───────────────────────────

    aspectos_luna = (
        luna_casa4_casa6.calcular_aspectos_luna(
            planetas
        )
    )

    aspectos_sol = (
        sol_asc_nodos.calcular_aspectos_sol_asc_nodos(
            planetas,
            asc,
        )
    )

    aspectos_personales = (
        planetas_personales.calcular_aspectos_planetas_personales(
            planetas,
            asc,
        )
    )

    aspectos_sociales = (
        planetas_sociales.calcular_aspectos_planetas_sociales(
            planetas,
            asc,
        )
    )

    aspectos_transpersonales = (
        planetas_transpersonales.calcular_aspectos_planetas_transpersonales(
            planetas,
            asc,
        )
    )

    # ── CONTENIDOS DE CIMIENTOS ───────────────────────────

    contenidos_ia = {

        "opCartaBase": (
            carta_natal_base.preparar_contenido_ia_base(
                carta
            )
        ),

        "opLuna": (
            luna_casa4_casa6.preparar_contenido_ia_luna(
                carta,
                aspectos_luna,
            )
        ),

        "opSolAscNodos": (
            sol_asc_nodos.preparar_contenido_ia_sol_asc_nodos(
                carta,
                aspectos_sol,
            )
        ),

        "opPersonales": (
            planetas_personales.preparar_contenido_ia_personales(
                carta,
                aspectos_personales,
            )
        ),

        "opSociales": (
            planetas_sociales.preparar_contenido_ia_sociales(
                carta,
                aspectos_sociales,
            )
        ),

        "opTranspersonales": (
            planetas_transpersonales.preparar_contenido_ia_transpersonales(
                carta,
                aspectos_transpersonales,
            )
        ),

        "opCasas": (
            casas_por_signo.preparar_contenido_ia_casas(
                carta
            )
        ),
    }

    # ── FIGURAS ───────────────────────────────────────────

    carta_figuras = copy.deepcopy(
        carta
    )

    carta_figuras["planetas"]["Ascendente"] = {
        "lon": carta["asc"]["lon"],
        "signo": carta["asc"]["signo"],
        "grado": carta["asc"]["grado"],
        "casa": 1,
        "retrogrado": False,
        "simbolo": "AC",
    }

    carta_figuras["planetas"]["Medio Cielo"] = {
        "lon": carta["mc"]["lon"],
        "signo": carta["mc"]["signo"],
        "grado": carta["mc"]["grado"],
        "casa": 10,
        "retrogrado": False,
        "simbolo": "MC",
    }

    aspectos_figuras = Figuras.calcular_aspectos_figuras(
        carta_figuras["planetas"]
    )

    figuras = Figuras.detectar_figuras(
        carta_figuras,
        aspectos_figuras,
    )

    arquitectura = Figuras.analizar_arquitectura_carta(
        carta_figuras,
        aspectos_figuras,
        figuras,
    )

    contenido_figuras = Figuras.preparar_datos_para_ia(
        carta_figuras,
        aspectos_figuras,
        arquitectura,
    )

    # ── CONTEXTO FINAL ────────────────────────────────────

    contexto_final = construir_contexto_arte_encarnarte(
        contenidos_ia,
        contenido_figuras,
    )

    contexto_final["_carta_figuras"] = carta_figuras

    return contexto_final


def filtrar_aspectos_por_figuras(
    aspectos_planeta,
    aspectos_relevantes,
    nombre_planeta,
):
    """
    Conserva únicamente los aspectos que forman parte de la
    arquitectura seleccionada y añade su información estructural:

    - aspectos pertenecientes a figuras;
    - aspectos independientes jerarquizados;
    - componentes de una relación con el eje nodal.
    """

    if not aspectos_planeta:
        return []

    mapa_relevantes = {}

    for aspecto in aspectos_relevantes:

        p1 = aspecto.get("p1")
        p2 = aspecto.get("p2")
        tipo = aspecto.get("tipo")

        # ── ASPECTO NORMAL ──────────────────────────────
        if (
            p1
            and p2
            and tipo
            and p2 != "Eje nodal"
        ):
            clave = (
                frozenset([p1, p2]),
                tipo,
            )

            mapa_relevantes[clave] = {
                "origen": aspecto.get("origen"),
                "jerarquia": aspecto.get("jerarquia"),
                "puntuacion": aspecto.get("puntuacion"),
                "figuras": aspecto.get("figuras", []),
            }

        # ── ASPECTO AGRUPADO AL EJE NODAL ──────────────
        if p2 == "Eje nodal":

            punto = p1

            for componente in aspecto.get(
                "componentes",
                []
            ):
                nodo = componente.get("nodo")
                tipo_componente = componente.get("tipo")

                if (
                    punto
                    and nodo
                    and tipo_componente
                ):
                    clave = (
                        frozenset(
                            [
                                punto,
                                nodo,
                            ]
                        ),
                        tipo_componente,
                    )

                    mapa_relevantes[clave] = {
                        "origen": aspecto.get("origen"),
                        "jerarquia": aspecto.get("jerarquia"),
                        "puntuacion": aspecto.get("puntuacion"),
                        "figuras": [],
                        "eje_nodal": True,
                    }

    resultado = []

    for aspecto in aspectos_planeta:

        otro = (
            aspecto.get("planeta")
            or aspecto.get("p2")
            or aspecto.get("p1")
        )

        tipo = aspecto.get("tipo")

        if not otro or not tipo:
            continue

        clave = (
            frozenset(
                [
                    nombre_planeta,
                    otro,
                ]
            ),
            tipo,
        )

        datos_arquitectura = mapa_relevantes.get(
            clave
        )

        if datos_arquitectura is None:
            continue

        # Copiamos el aspecto original para no modificar
        # los datos procedentes de Cimientos.
        aspecto_enriquecido = dict(
            aspecto
        )

        aspecto_enriquecido[
            "origen_arquitectura"
        ] = datos_arquitectura.get(
            "origen"
        )

        aspecto_enriquecido[
            "jerarquia_arquitectura"
        ] = datos_arquitectura.get(
            "jerarquia"
        )

        aspecto_enriquecido[
            "puntuacion_arquitectura"
        ] = datos_arquitectura.get(
            "puntuacion"
        )

        aspecto_enriquecido[
            "figuras"
        ] = datos_arquitectura.get(
            "figuras",
            []
        )

        if datos_arquitectura.get(
            "eje_nodal"
        ):
            aspecto_enriquecido[
                "eje_nodal"
            ] = True

        resultado.append(
            aspecto_enriquecido
        )

    return resultado

def construir_contexto_compacto_arte_encarnarte(
    contexto
):

    cimientos = contexto["cimientos"]
    figuras = contexto["figuras"]

    arquitectura = figuras.get(
        "arquitectura",
        {}
    )

    aspectos_relevantes_figuras = figuras.get(
        "aspectos_relevantes",
        []
    )

    # ── PUNTOS ESTRUCTURALES IMPORTANTES ──────────────────

    puntos_importantes = {
        "Sol",
        "Luna",
        "Ascendente",
        "Nodo Norte",
        "Nodo Sur",
    }

    for punto in arquitectura.get(
        "puntos_organizadores",
        []
    ):

        nombre = punto.get(
            "punto"
        )

        if nombre:
            puntos_importantes.add(
                nombre
            )

    # ── PUNTOS IMPLICADOS EN ASPECTOS INDEPENDIENTES IMPORTANTES ──

    for aspecto in aspectos_relevantes_figuras:

        if aspecto.get("origen") != "independiente":
            continue

        if aspecto.get("jerarquia") not in (
            "principal",
            "relevante",
        ):
            continue

        p1 = aspecto.get("p1")
        p2 = aspecto.get("p2")

        if p1 and p1 != "Eje nodal":
            puntos_importantes.add(p1)

        if p2 and p2 != "Eje nodal":
            puntos_importantes.add(p2)


    for nucleo in arquitectura.get(
        "nucleos",
        []
    ):

        for nombre in nucleo.get(
            "puntos_nucleo",
            []
        ):
            puntos_importantes.add(
                nombre
            )

    for familia in arquitectura.get(
        "familias",
        []
    ):

        nombre = familia.get(
            "punto_central"
        )

        if nombre:
            puntos_importantes.add(
                nombre
            )

    # ── CASAS IMPORTANTES ─────────────────────────────────

    casas_importantes = set()

    for casa in arquitectura.get(
        "casas",
        []
    ):

        numero = casa.get(
            "casa"
        )

        if numero:
            casas_importantes.add(
                numero
            )

    for eje in arquitectura.get(
        "ejes_casas",
        []
    ):

        if eje.get("casa_1"):
            casas_importantes.add(
                eje["casa_1"]
            )

        if eje.get("casa_2"):
            casas_importantes.add(
                eje["casa_2"]
            )

    # ── BASE GENERAL ──────────────────────────────────────

    base = cimientos[
        "carta_base"
    ]

    # ── ARQUITECTURA CON TÍTULO CANÓNICO ─────────────

    arquitectura_compacta = dict(
        arquitectura
    )

    figuras_con_titulo = []

    for indice, figura in enumerate(
        arquitectura.get(
            "figuras",
            []
        ),
        start=1,
    ):

        figura_compacta = dict(
            figura
        )

        figura_compacta[
            "id_figura"
        ] = f"figura_{indice:03d}"

        tipo = (
            figura.get("nombre_canonico")
            or figura.get("tipo", "")
        ).strip()

        puntos = figura.get(
            "puntos",
            []
        )

        vertices = figura.get(
            "vertices",
            [],
        )

        if vertices:
            etiquetas_vertices = []

            for vertice in vertices:
                puntos_vertice = vertice.get(
                    "puntos",
                    [],
                )

                if not puntos_vertice:
                    continue

                if len(puntos_vertice) > 1:
                    nombre_colectivo = vertice.get(
                        "tipo",
                        "Conjunción",
                    )
                    etiquetas_vertices.append(
                        nombre_colectivo + " ("
                        + " + ".join(puntos_vertice)
                        + ")"
                    )
                else:
                    etiquetas_vertices.append(
                        puntos_vertice[0]
                    )

            titulo_puntos = " · ".join(
                etiquetas_vertices
            )
        else:
            titulo_puntos = " · ".join(
                puntos
            )

        if tipo and titulo_puntos:
            figura_compacta[
                "titulo_salida"
            ] = (
                tipo
                + " "
                + titulo_puntos
            )

        figuras_con_titulo.append(
            figura_compacta
        )

    arquitectura_compacta[
        "figuras"
    ] = figuras_con_titulo

    contexto_compacto = {

        "base_general": {

            "vision_general": base.get(
                "vision_general"
            ),

            "elementos": base.get(
                "elementos"
            ),

            "modalidades": base.get(
                "modalidades"
            ),

            "integracion_elementos": base.get(
                "integracion_elementos"
            ),

            "pilares": base.get(
                "pilares"
            ),
        },

        "sol_asc_nodos": {},

        "luna": {},

        "planetas": {},

        "casas": {},

        "figuras": {
            "arquitectura": arquitectura_compacta,

            "aspectos_relevantes": figuras.get(
                "aspectos_relevantes",
                []
            ),

            "posiciones_natales": figuras.get(
                "posiciones_natales",
                {}
            ),
        },
    }

    # ── LUNA COMPACTA ─────────────────────────────────────

    datos_luna = cimientos.get(
        "luna_casa4_casa6",
        {}
    ).get(
        "luna",
        {}
    )

    contexto_compacto["luna"] = {
        "signo": datos_luna.get("signo"),
        "casa": datos_luna.get("casa"),

        "aspectos": filtrar_aspectos_por_figuras(
            datos_luna.get(
                "aspectos",
                []
            ),
            aspectos_relevantes_figuras,
            "Luna",
        ),
    }


    # ── SOL · ASCENDENTE · NODOS COMPACTOS ───────────────

    datos_sol_asc_nodos = cimientos.get(
        "sol_asc_nodos",
        {}
    )

    datos_sol = datos_sol_asc_nodos.get(
        "sol",
        {}
    )

    datos_asc = datos_sol_asc_nodos.get(
        "ascendente",
        {}
    )

    datos_nodos = datos_sol_asc_nodos.get(
        "nodos",
        {}
    )

    contexto_compacto["sol_asc_nodos"] = {

        "direccion_general": datos_sol_asc_nodos.get(
            "direccion_general"
        ),

        "sol": {
            "signo": datos_sol.get("signo"),
            "casa": datos_sol.get("casa"),
            "grado": datos_sol.get("grado"),
        },

        "ascendente": {
            "signo": datos_asc.get("signo"),
            "grado": datos_asc.get("grado"),
            "regente": datos_asc.get("regente"),
        },

        "nodos": {
            "nodo_norte": datos_nodos.get(
                "nodo_norte"
            ),

            "nodo_sur": datos_nodos.get(
                "nodo_sur"
            ),
        },

        "integracion": datos_sol_asc_nodos.get(
            "integracion"
        ),

        "orientacion": datos_sol_asc_nodos.get(
            "orientacion"
        ),

        "interceptaciones": datos_sol_asc_nodos.get(
            "interceptaciones"
        ),

        "grados_sensibles": datos_sol_asc_nodos.get(
            "grados_sensibles"
        ),

        "aspectos": [],
    }

    aspectos_sol_asc_nodos = datos_sol_asc_nodos.get(
        "aspectos",
        []
    )

    aspectos_filtrados = []

    for nombre_punto in (
        "Sol",
        "Ascendente",
        "Nodo Norte",
        "Nodo Sur",
    ):

        encontrados = filtrar_aspectos_por_figuras(
            aspectos_sol_asc_nodos,
            aspectos_relevantes_figuras,
            nombre_punto,
        )

        for aspecto in encontrados:
            if aspecto not in aspectos_filtrados:
                aspectos_filtrados.append(
                    aspecto
                )

    contexto_compacto[
        "sol_asc_nodos"
    ][
        "aspectos"
    ] = aspectos_filtrados

    # ── COMPACTADOR DE PLANETAS ───────────────────────────

    def compactar_planeta(
        datos,
        nombre_planeta,
    ):

        if not datos:
            return None

        return {

            "signo": datos.get(
                "signo"
            ),

            "casa": datos.get(
                "casa"
            ),

            "grado": datos.get(
                "grado"
            ),

            "retrogrado": datos.get(
                "retrogrado"
            ),

            "integracion": datos.get(
                "integracion"
            ),

            "aspectos": filtrar_aspectos_por_figuras(
                datos.get(
                    "aspectos",
                    []
                ),
                aspectos_relevantes_figuras,
                nombre_planeta,
            ),
        }

    # ── PLANETAS PERSONALES ───────────────────────────────

    personales = cimientos.get(
        "planetas_personales",
        {}
    )

    mapa_personales = {
        "Mercurio": "mercurio",
        "Venus": "venus",
        "Marte": "marte",
    }

    for nombre, clave in mapa_personales.items():

        if nombre in puntos_importantes:

            contexto_compacto[
                "planetas"
            ][nombre] = compactar_planeta(
                personales.get(
                    clave
                ),
                nombre,
            )

    # ── PLANETAS SOCIALES ─────────────────────────────────

    sociales = cimientos.get(
        "planetas_sociales",
        {}
    )

    mapa_sociales = {
        "Júpiter": "júpiter",
        "Saturno": "saturno",
    }

    for nombre, clave in mapa_sociales.items():

        if nombre in puntos_importantes:

            contexto_compacto[
                "planetas"
            ][nombre] = compactar_planeta(
                sociales.get(
                    clave
                ),
                nombre,
            )

    # ── PLANETAS TRANSPERSONALES ──────────────────────────

    transpersonales = cimientos.get(
        "planetas_transpersonales",
        {}
    )

    mapa_transpersonales = {
        "Urano": "urano",
        "Neptuno": "neptuno",
        "Plutón": "plutón",
    }

    for nombre, clave in mapa_transpersonales.items():

        if nombre in puntos_importantes:

            contexto_compacto[
                "planetas"
            ][nombre] = compactar_planeta(
                transpersonales.get(
                    clave
                ),
                nombre,
            )

    # ── CASAS ESTRUCTURALES ───────────────────────────────

    casas_cimientos = cimientos.get(
        "casas_por_signo",
        {}
    ).get(
        "casas",
        {}
    )

    for numero in sorted(
        casas_importantes
    ):

        clave = f"casa_{numero}"

        if clave in casas_cimientos:

            contexto_compacto[
                "casas"
            ][clave] = casas_cimientos[
                clave
            ]

    return contexto_compacto


if __name__ == "__main__":

    contexto = generar_contexto_arte_encarnarte(
        nombre="IZAS",
        fecha="16/04/1979",
        hora="04:20",
        lugar="PAMPLONA, ESPAÑA",
        lat=42.8157,
        lon=-1.6522,
        tz_name="Europe/Madrid",
    )

    Figuras.dibujar_rueda_arquitectura(
        carta=contexto["_carta_figuras"],
        aspectos_relevantes=contexto["figuras"]["aspectos_relevantes"],
        puntos_organizadores=contexto["figuras"]["arquitectura"]["puntos_organizadores"],
        nombre_persona="IZAS",
        archivo_salida="IZAS_arquitectura.png",
    )

    print(
        "Rueda arquitectura generada:",
        "IZAS_arquitectura.png"
    )

    compacto = construir_contexto_compacto_arte_encarnarte(
        contexto
    )

    completo_json = json.dumps(
        contexto,
        ensure_ascii=False
    )

    compacto_json = json.dumps(
        compacto,
        ensure_ascii=False
    )

    print("\nPUNTOS ORGANIZADORES:")
    for punto in contexto["figuras"]["arquitectura"]["puntos_organizadores"]:
        print(punto)

    print("\nNÚCLEOS:")
    for nucleo in contexto["figuras"]["arquitectura"].get("nucleos", []):
        print(nucleo)

    print("\nFIGURAS:")
    for figura in contexto["figuras"]["arquitectura"].get("figuras", []):
        print(figura)

    print("\nASPECTOS RELEVANTES:")
    for aspecto in contexto["figuras"]["aspectos_relevantes"][:10]:
        print(aspecto)

    print(
        "Contexto completo:",
        len(completo_json),
        "caracteres"
    )

    print(
        "Contexto compacto:",
        len(compacto_json),
        "caracteres"
    )

    print(
        "Reducción:",
        round(
            100 - (
                len(compacto_json)
                / len(completo_json)
                * 100
            ),
            1
        ),
        "%"
    )
