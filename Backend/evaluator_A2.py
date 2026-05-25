import re


def contar_palabras(texto: str) -> int:
    palabras = re.findall(r"\b\w+\b", texto.lower())
    return len(palabras)


def contar_conectores(texto: str) -> int:
    conectores = [
        "por lo tanto", "sin embargo", "no obstante", "además",
        "en consecuencia", "por otro lado", "asimismo", "debido a",
        "en primer lugar", "en segundo lugar", "finalmente",
        "en conclusión", "aunque", "mientras que", "por consiguiente"
    ]

    texto_lower = texto.lower()
    return sum(texto_lower.count(conector) for conector in conectores)


def detectar_formalidad(texto: str) -> float:
    expresiones_informales = [
        "creo que", "yo pienso", "bueno", "osea", "o sea",
        "tipo", "pues", "la verdad", "en fin"
    ]

    texto_lower = texto.lower()
    total_informales = sum(texto_lower.count(exp) for exp in expresiones_informales)

    if total_informales == 0:
        return 5.0
    elif total_informales <= 2:
        return 4.0
    elif total_informales <= 4:
        return 3.0
    elif total_informales <= 6:
        return 2.0
    else:
        return 1.0


def detectar_refutacion(texto: str) -> float:
    marcadores_refutacion = [
        "sin embargo", "no obstante", "aunque", "contrario a",
        "esto no implica", "esto contradice", "se cuestiona",
        "la postura contraria", "el oponente", "el proponente",
        "refuta", "contraargumento", "respuesta a"
    ]

    texto_lower = texto.lower()
    total = sum(texto_lower.count(m) for m in marcadores_refutacion)

    if total >= 8:
        return 5.0
    elif total >= 5:
        return 4.0
    elif total >= 3:
        return 3.0
    elif total >= 1:
        return 2.0
    else:
        return 1.0


def evaluar_calidad_argumentativa(texto: str) -> float:
    palabras = contar_palabras(texto)
    conectores = contar_conectores(texto)

    puntaje = 1.0

    if palabras >= 150:
        puntaje += 1.0
    if palabras >= 300:
        puntaje += 1.0
    if conectores >= 3:
        puntaje += 1.0
    if conectores >= 6:
        puntaje += 1.0

    return min(puntaje, 5.0)


def evaluar_coherencia(texto: str, tema: str) -> float:
    palabras_tema = set(re.findall(r"\b\w+\b", tema.lower()))
    palabras_texto = set(re.findall(r"\b\w+\b", texto.lower()))

    if not palabras_tema:
        return 1.0

    coincidencias = palabras_tema.intersection(palabras_texto)
    proporcion = len(coincidencias) / len(palabras_tema)

    conectores = contar_conectores(texto)

    puntaje = 1.0

    if proporcion >= 0.3:
        puntaje += 1.0
    if proporcion >= 0.5:
        puntaje += 1.0
    if conectores >= 3:
        puntaje += 1.0
    if conectores >= 6:
        puntaje += 1.0

    return min(puntaje, 5.0)


def evaluar_uso_evidencia(texto: str) -> float:
    patrones_evidencia = [
        r"\(\d{4}\)",
        r"según",
        r"estudio",
        r"investigación",
        r"informe",
        r"datos",
        r"evidencia",
        r"autor",
        r"universidad"
    ]

    texto_lower = texto.lower()
    total = 0

    for patron in patrones_evidencia:
        total += len(re.findall(patron, texto_lower))

    if total >= 6:
        return 5.0
    elif total >= 4:
        return 4.0
    elif total >= 2:
        return 3.0
    elif total >= 1:
        return 2.0
    else:
        return 1.0


def interpretar_nivel(promedio: float) -> str:
    if promedio >= 4.5:
        return "Muy alto"
    elif promedio >= 3.5:
        return "Alto"
    elif promedio >= 2.5:
        return "Medio"
    elif promedio >= 1.5:
        return "Bajo"
    else:
        return "Muy bajo"


def generar_observacion(promedio: float) -> str:
    if promedio >= 4.5:
        return "El debate presenta un desempeño muy sólido en términos argumentativos, coherencia, formalidad y refutación."
    elif promedio >= 3.5:
        return "El debate presenta un desempeño adecuado, aunque puede mejorar en profundidad argumentativa o uso de evidencia."
    elif promedio >= 2.5:
        return "El debate presenta un nivel medio; requiere mayor desarrollo, mejor conexión lógica y más respaldo académico."
    elif promedio >= 1.5:
        return "El debate presenta debilidades importantes en estructura, coherencia o formalidad."
    else:
        return "El debate presenta un desempeño muy bajo y requiere una reformulación completa."


def evaluar_fragmento(texto: str, tema: str) -> dict:
    calidad = evaluar_calidad_argumentativa(texto)
    coherencia = evaluar_coherencia(texto, tema)
    formalidad = detectar_formalidad(texto)
    evidencia = evaluar_uso_evidencia(texto)
    refutacion = detectar_refutacion(texto)

    promedio = round(
        (calidad + coherencia + formalidad + evidencia + refutacion) / 5,
        2
    )

    return {
        "calidad_argumentativa": calidad,
        "coherencia": coherencia,
        "formalidad_academica": formalidad,
        "uso_evidencia": evidencia,
        "capacidad_refutacion": refutacion,
        "promedio": promedio,
        "nivel": interpretar_nivel(promedio)
    }


def extraer_seccion(texto: str, inicio: str, posibles_finales: list) -> str:

    texto_normalizado = texto.lower()

    inicio_normalizado = inicio.lower()

    pos_inicio = texto_normalizado.find(inicio_normalizado)

    if pos_inicio == -1:
        return ""

    pos_inicio += len(inicio)

    pos_fin = len(texto)

    for final in posibles_finales:

        final_normalizado = final.lower()

        posible_pos_fin = texto_normalizado.find(
            final_normalizado,
            pos_inicio
        )

        if posible_pos_fin != -1 and posible_pos_fin < pos_fin:

            pos_fin = posible_pos_fin

    return texto[pos_inicio:pos_fin].strip()


def separar_partes_debate(debate: str) -> dict:
    proponente = extraer_seccion(
        debate,
        "ARGUMENTO DEL PROPONENTE:",
        [
            "CONTRAARGUMENTO DEL OPONENTE:",
            "RÉPLICA DEL PROPONENTE:",
            "EVALUACIÓN DEL JUEZ:",
            "CONCLUSIÓN GENERAL:"
        ]
    )

    oponente = extraer_seccion(
        debate,
        "CONTRAARGUMENTO DEL OPONENTE:",
        [
            "RÉPLICA DEL PROPONENTE:",
            "EVALUACIÓN DEL JUEZ:",
            "CONCLUSIÓN GENERAL:"
        ]
    )

    replica = extraer_seccion(
        debate,
        "RÉPLICA DEL PROPONENTE:",
        [
            "EVALUACIÓN DEL JUEZ:",
            "CONCLUSIÓN GENERAL:"
        ]
    )

    return {
        "proponente": proponente,
        "oponente": oponente,
        "replica_proponente": replica
    }


def evaluar_debate(tema: str, arquitectura: str, debate: str) -> dict:
    partes = separar_partes_debate(debate)

    evaluacion_general = evaluar_fragmento(debate, tema)

    evaluacion_proponente = evaluar_fragmento(partes["proponente"], tema) if partes["proponente"] else None
    evaluacion_oponente = evaluar_fragmento(partes["oponente"], tema) if partes["oponente"] else None
    evaluacion_replica = evaluar_fragmento(partes["replica_proponente"], tema) if partes["replica_proponente"] else None

    return {
        "tema": tema,
        "arquitectura": arquitectura,
        "evaluacion_general": evaluacion_general,
        "evaluacion_por_agente": {
            "proponente": evaluacion_proponente,
            "oponente": evaluacion_oponente,
            "replica_proponente": evaluacion_replica
        },
        "partes_detectadas": {
            "proponente_detectado": bool(partes["proponente"]),
            "oponente_detectado": bool(partes["oponente"]),
            "replica_detectada": bool(partes["replica_proponente"])
        },
        "observacion_general": generar_observacion(evaluacion_general["promedio"])
    }