"""
Núcleos estructurales compartidos de Arquitectura Interna.

Este módulo contiene detecciones deterministas reutilizables por los informes
Cimientos. No interpreta: únicamente reconoce agrupaciones calculadas a partir
de posiciones natales.

La definición de Stellium replica el criterio vigente de Figuras.py:
- se construye por componentes conectados de conjunciones reales;
- requiere al menos 3 puntos;
- usa los orbes generales vigentes para conjunción (10°);
- Quirón y Lilith mantienen su límite vinculante de 5°;
- no incluye Ascendente ni Medio Cielo.
"""

PUNTOS_BASE_STELLIUM = [
    "Sol", "Luna", "Mercurio", "Venus", "Marte",
    "Júpiter", "Saturno", "Urano", "Neptuno", "Plutón",
    "Quirón", "Lilith", "Nodo Norte", "Nodo Sur",
]

ORBE_CONJUNCION_GENERAL = 10.0
ORBE_CONJUNCION_PUNTO_SENSIBLE = 5.0
PUNTOS_SENSIBLES = {"Quirón", "Lilith"}


def _distancia_angular(lon1, lon2):
    diferencia = abs(float(lon1) - float(lon2)) % 360.0
    if diferencia > 180.0:
        diferencia = 360.0 - diferencia
    return diferencia


def _conjuncion_valida(nombre1, datos1, nombre2, datos2):
    """Aplica el mismo criterio vinculante de conjunción usado por Figuras.py."""
    orbe = _distancia_angular(datos1["lon"], datos2["lon"])

    if orbe > ORBE_CONJUNCION_GENERAL:
        return False

    if (
        nombre1 in PUNTOS_SENSIBLES
        or nombre2 in PUNTOS_SENSIBLES
    ) and orbe > ORBE_CONJUNCION_PUNTO_SENSIBLE:
        return False

    return True


def _amplitud_circular(longitudes):
    longitudes = sorted(float(lon) % 360.0 for lon in longitudes)
    if len(longitudes) < 2:
        return 0.0

    huecos = [
        longitudes[i + 1] - longitudes[i]
        for i in range(len(longitudes) - 1)
    ]
    huecos.append((longitudes[0] + 360.0) - longitudes[-1])
    return round(360.0 - max(huecos), 2)


def detectar_stelliums_globales(carta):
    """Devuelve stelliums como componentes conectados de conjunciones reales."""
    planetas = (carta or {}).get("planetas", {}) or {}

    puntos = [
        nombre
        for nombre in PUNTOS_BASE_STELLIUM
        if nombre in planetas
        and isinstance(planetas.get(nombre), dict)
        and planetas[nombre].get("lon") is not None
    ]

    if len(puntos) < 3:
        return []

    vecinos = {punto: set() for punto in puntos}

    for i, p1 in enumerate(puntos):
        for p2 in puntos[i + 1:]:
            if _conjuncion_valida(p1, planetas[p1], p2, planetas[p2]):
                vecinos[p1].add(p2)
                vecinos[p2].add(p1)

    visitados = set()
    grupos = []

    for punto in puntos:
        if punto in visitados:
            continue

        pendientes = [punto]
        grupo = []

        while pendientes:
            actual = pendientes.pop()
            if actual in visitados:
                continue
            visitados.add(actual)
            grupo.append(actual)
            pendientes.extend(vecinos.get(actual, set()) - visitados)

        if len(grupo) >= 3:
            grupos.append(grupo)

    orden = {nombre: i for i, nombre in enumerate(PUNTOS_BASE_STELLIUM)}
    nucleos = []

    for grupo in grupos:
        puntos_ordenados = sorted(grupo, key=lambda p: orden.get(p, 999))
        posiciones = {
            punto: {
                "signo": planetas[punto].get("signo"),
                "casa": planetas[punto].get("casa"),
                "grado": planetas[punto].get("grado"),
                "retrogrado": planetas[punto].get("retrogrado", False),
                "lon": planetas[punto].get("lon"),
            }
            for punto in puntos_ordenados
        }

        casas = []
        signos = []
        for punto in puntos_ordenados:
            casa = posiciones[punto].get("casa")
            signo = posiciones[punto].get("signo")
            if casa not in (None, "") and casa not in casas:
                casas.append(casa)
            if signo and signo not in signos:
                signos.append(signo)

        conjunciones = []
        for i, p1 in enumerate(puntos_ordenados):
            for p2 in puntos_ordenados[i + 1:]:
                if _conjuncion_valida(p1, planetas[p1], p2, planetas[p2]):
                    conjunciones.append({
                        "punto1": p1,
                        "punto2": p2,
                        "orbe": round(
                            _distancia_angular(
                                planetas[p1]["lon"],
                                planetas[p2]["lon"],
                            ),
                            2,
                        ),
                    })

        nucleos.append({
            "tipo": "Stellium",
            "puntos": puntos_ordenados,
            "posiciones": posiciones,
            "casas": casas,
            "signos": signos,
            "conjunciones": conjunciones,
            "amplitud": _amplitud_circular(
                posiciones[p]["lon"] for p in puntos_ordenados
            ),
        })

    return sorted(
        nucleos,
        key=lambda n: (-len(n["puntos"]), n["amplitud"]),
    )


def detectar_nucleos_globales(carta):
    """
    Punto de entrada común para Cimientos.

    Se deja deliberadamente extensible para incorporar en el futuro otros
    núcleos colectivos sin cambiar la interfaz de los informes.
    """
    return detectar_stelliums_globales(carta)


def nucleos_de_punto(carta, punto):
    return [
        nucleo
        for nucleo in detectar_nucleos_globales(carta)
        if punto in nucleo.get("puntos", [])
    ]
