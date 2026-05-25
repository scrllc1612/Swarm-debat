import re


# =====================================================
# UTILIDADES
# =====================================================

def contar_palabras(texto: str) -> int:
    palabras = re.findall(r"\b\w+\b", texto.lower())
    return len(palabras)


def contar_conectores(texto: str) -> int:
    conectores = [
        "por lo tanto",
        "sin embargo",
        "no obstante",
        "además",
        "en consecuencia",
        "por otro lado",
        "asimismo",
        "debido a",
        "en primer lugar",
        "en segundo lugar",
        "finalmente",
        "en conclusión",
        "aunque",
        "mientras que",
        "por consiguiente"
    ]

    texto_lower = texto.lower()

    return sum(
        texto_lower.count(conector)
        for conector in conectores
    )


# =====================================================
# FORMALIDAD
# =====================================================

def detectar_formalidad(texto: str) -> float:

    expresiones_informales = [
        "creo que",
        "yo pienso",
        "bueno",
        "osea",
        "o sea",
        "tipo",
        "pues",
        "la verdad",
        "en fin"
    ]

    texto_lower = texto.lower()

    total = sum(
        texto_lower.count(exp)
        for exp in expresiones_informales
    )

    if total == 0:
        return 5.0
    elif total <= 2:
        return 4.0
    elif total <= 4:
        return 3.0
    elif total <= 6:
        return 2.0
    else:
        return 1.0


# =====================================================
# REFUTACIÓN
# =====================================================

def detectar_refutacion(texto: str) -> float:

    marcadores = [
        "sin embargo",
        "no obstante",
        "aunque",
        "contrario a",
        "esto contradice",
        "la postura opuesta",
        "el oponente",
        "el proponente",
        "refuta",
        "contraargumento"
    ]

    texto_lower = texto.lower()

    total = sum(
        texto_lower.count(m)
        for m in marcadores
    )

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


# =====================================================
# CALIDAD ARGUMENTATIVA
# =====================================================

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


# =====================================================
# COHERENCIA
# =====================================================

def evaluar_coherencia(texto: str, tema: str) -> float:

    palabras_tema = set(
        re.findall(r"\b\w+\b", tema.lower())
    )

    palabras_texto = set(
        re.findall(r"\b\w+\b", texto.lower())
    )

    if not palabras_tema:
        return 1.0

    coincidencias = palabras_tema.intersection(
        palabras_texto
    )

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


# =====================================================
# EVIDENCIA
# =====================================================

def evaluar_uso_evidencia(texto: str) -> float:

    patrones = [
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

    for patron in patrones:
        total += len(
            re.findall(patron, texto_lower)
        )

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


# =====================================================
# INTELIGENCIA COLECTIVA
# =====================================================

def evaluar_integracion_swarm(texto: str) -> float:

    indicadores = [
        "comparación",
        "por otro lado",
        "ambas posturas",
        "en contraste",
        "síntesis",
        "integración",
        "análisis comparativo",
        "colectivo",
        "refinamiento"
    ]

    texto_lower = texto.lower()

    total = sum(
        texto_lower.count(i)
        for i in indicadores
    )

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


# =====================================================
# INTERPRETACIÓN
# =====================================================

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


# =====================================================
# OBSERVACIÓN
# =====================================================

def generar_observacion(promedio: float) -> str:

    if promedio >= 4.5:
        return "La arquitectura swarm presenta un desempeño colectivo muy sólido."

    elif promedio >= 3.5:
        return "La arquitectura swarm presenta buena integración y calidad argumentativa."

    elif promedio >= 2.5:
        return "La arquitectura swarm presenta desempeño medio y requiere mayor refinamiento colectivo."

    elif promedio >= 1.5:
        return "La arquitectura swarm presenta debilidades importantes de coherencia o integración."

    else:
        return "La arquitectura swarm requiere una reformulación significativa."


# =====================================================
# EXTRAER SECCIONES
# =====================================================

def extraer_seccion(
    texto: str,
    inicio: str,
    posibles_finales: list
) -> str:

    texto_lower = texto.lower()
    inicio_lower = inicio.lower()

    pos_inicio = texto_lower.find(inicio_lower)

    if pos_inicio == -1:
        return ""

    pos_contenido = pos_inicio + len(inicio)

    posiciones_finales = []

    for final in posibles_finales:

        pos_final = texto_lower.find(
            final.lower(),
            pos_contenido
        )

        if pos_final != -1:
            posiciones_finales.append(pos_final)

    if posiciones_finales:

        pos_fin = min(posiciones_finales)

        return texto[pos_contenido:pos_fin].strip()

    return texto[pos_contenido:].strip()


# =====================================================
# SEPARAR PARTES DEL DEBATE
# =====================================================

def separar_partes_debate(debate: str) -> dict:

    proponente = extraer_seccion(
        debate,
        "⚖️ POSTURA PROPONENTE:",
        [
            "⚖️ POSTURA OPONENTE:",
            "📚 ANÁLISIS COMPARATIVO:",
            "🧾 CONCLUSIÓN GENERAL:"
        ]
    )

    oponente = extraer_seccion(
        debate,
        "⚖️ POSTURA OPONENTE:",
        [
            "📚 ANÁLISIS COMPARATIVO:",
            "🧾 CONCLUSIÓN GENERAL:"
        ]
    )

    analisis = extraer_seccion(
        debate,
        "📚 ANÁLISIS COMPARATIVO:",
        [
            "🧾 CONCLUSIÓN GENERAL:"
        ]
    )

    conclusion = extraer_seccion(
        debate,
        "🧾 CONCLUSIÓN GENERAL:",
        []
    )

    return {
        "proponente": proponente,
        "oponente": oponente,
        "analisis": analisis,
        "conclusion": conclusion
    }


# =====================================================
# EVALUAR FRAGMENTO
# =====================================================

def evaluar_fragmento(
    texto: str,
    tema: str
) -> dict:

    calidad = evaluar_calidad_argumentativa(texto)

    coherencia = evaluar_coherencia(texto, tema)

    formalidad = detectar_formalidad(texto)

    evidencia = evaluar_uso_evidencia(texto)

    refutacion = detectar_refutacion(texto)

    integracion_swarm = evaluar_integracion_swarm(texto)

    promedio = round(
        (
            calidad +
            coherencia +
            formalidad +
            evidencia +
            refutacion +
            integracion_swarm
        ) / 6,
        2
    )

    return {
        "calidad_argumentativa": calidad,
        "coherencia": coherencia,
        "formalidad_academica": formalidad,
        "uso_evidencia": evidencia,
        "capacidad_refutacion": refutacion,
        "integracion_swarm": integracion_swarm,
        "promedio": promedio,
        "nivel": interpretar_nivel(promedio)
    }


# =====================================================
# EVALUADOR PRINCIPAL
# =====================================================

def evaluar_debate_a4(
    tema: str,
    arquitectura: str,
    debate: str
) -> dict:

    partes = separar_partes_debate(debate)

    evaluacion_general = evaluar_fragmento(
        debate,
        tema
    )

    evaluacion_proponente = evaluar_fragmento(
        partes["proponente"],
        tema
    ) if partes["proponente"] else None

    evaluacion_oponente = evaluar_fragmento(
        partes["oponente"],
        tema
    ) if partes["oponente"] else None

    evaluacion_analisis = evaluar_fragmento(
        partes["analisis"],
        tema
    ) if partes["analisis"] else None

    return {
        "tema": tema,

        "arquitectura": arquitectura,

        "evaluacion_general": evaluacion_general,

        "evaluacion_swarm": {
            "proponente": evaluacion_proponente,
            "oponente": evaluacion_oponente,
            "analisis_comparativo": evaluacion_analisis
        },

        "partes_detectadas": {
            "proponente_detectado": bool(partes["proponente"]),
            "oponente_detectado": bool(partes["oponente"]),
            "analisis_detectado": bool(partes["analisis"]),
            "conclusion_detectada": bool(partes["conclusion"])
        },

        "observacion_general": generar_observacion(
            evaluacion_general["promedio"]
        )
    }