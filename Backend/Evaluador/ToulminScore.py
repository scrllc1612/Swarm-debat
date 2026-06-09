"""
================================================================================
ToulminScore.py — Evaluador Argumentativo Computacional basado en el Modelo
de Toulmin (1958)

Autor: Generado para investigación académica
Última actualización: 2026-06-09

DESCRIPCIÓN:
    Sistema de evaluación argumentativa completamente determinístico y
    reproducible, basado EXCLUSIVAMENTE en el Modelo de Argumentación de
    Stephen Toulmin. No utiliza LLMs, modelos generativos ni puntuaciones
    subjetivas. Funciona mediante reglas lingüísticas, patrones regex,
    análisis estructural con spaCy y NLP tradicional.

MODELO DE TOULMIN:
    El modelo descompone un argumento en seis componentes:

    1. Claim (Tesis/Conclusión): La proposición central que se defiende.
    2. Data/Grounds (Evidencia): Los hechos, cifras o pruebas que
       sustentan el claim.
    3. Warrant (Garantía/Justificación lógica): El puente inferencial
       que conecta los datos con el claim.
    4. Backing (Respaldo): Soporte adicional que refuerza la warrant
       (autoridades, estudios, instituciones).
    5. Qualifier (Cualificador): Términos que modulan el grado de certeza
       del claim (probablemente, generalmente, etc.).
    6. Rebuttal (Refutación/Contraargumento): Excepciones, objeciones o
       condiciones bajo las cuales el claim no se sostiene.

SISTEMA DE PUNTUACIÓN:
    Claim:     20 puntos  (peso de la tesis central)
    Data:      25 puntos  (peso de la evidencia empírica)
    Warrant:   20 puntos  (peso de la justificación lógica)
    Backing:   15 puntos  (peso del respaldo institucional/académico)
    Qualifier: 10 puntos  (peso de la modulación epistémica)
    Rebuttal:  10 puntos  (peso de la consideración de objeciones)
    TOTAL:    100 puntos

DEPENDENCIAS:
    - spaCy >= 3.0 con modelo 'es_core_news_md' (o 'es_core_news_sm')
    - re (biblioteca estándar)

USO:
    evaluador = ToulminEvaluator()
    resultado = evaluador.evaluate("Texto del argumento aquí...")
    print(resultado)

FILOSOFÍA DE DISEÑO:
    - Interpretabilidad sobre complejidad
    - Trazabilidad completa de cada decisión
    - Reproducibilidad: misma entrada → misma salida SIEMPRE
    - Orientado a investigación académica y tesis doctorales/maestría
================================================================================
"""

import re
from typing import Dict, List, Optional, Any

# =====================================================
# CARGA DE SPACY
# =====================================================
# Se intenta cargar el modelo mediano de spaCy para español.
# Si no está disponible, se intenta con el modelo pequeño.
# El modelo proporciona: tokenización, POS tagging, NER,
# análisis de dependencias y lematización.
# =====================================================

try:
    import spacy
    try:
        nlp = spacy.load("es_core_news_md")
    except OSError:
        try:
            nlp = spacy.load("es_core_news_sm")
        except OSError:
            nlp = None
            print(
                "[ADVERTENCIA] No se encontró modelo spaCy para español. "
                "Instale con: python -m spacy download es_core_news_md"
            )
except ImportError:
    nlp = None
    print(
        "[ADVERTENCIA] spaCy no está instalado. "
        "Instale con: pip install spacy"
    )


# =====================================================
# CLASE PRINCIPAL: ToulminEvaluator
# =====================================================

class ToulminEvaluator:
    """
    Evaluador argumentativo basado en el Modelo de Toulmin (1958).

    Este evaluador analiza un texto argumentativo y detecta la presencia
    de los seis componentes del modelo mediante reglas lingüísticas
    determinísticas, patrones de expresiones regulares y análisis
    morfosintáctico con spaCy.

    Cada detector retorna un diccionario con:
        - presencia: int (0 o 1)
        - confianza: float (0.0 a 1.0) — basada en cantidad y calidad
          de los indicadores detectados
        - fragmentos: list[str] — los fragmentos del texto que activaron
          la detección
        - indicadores_encontrados: list[str] — los marcadores específicos
          que fueron detectados
        - puntos: float — puntos otorgados (proporcional a confianza
          y peso máximo del componente)

    Atributos de clase:
        PESOS: dict — peso máximo de cada componente en el score total

    Principio de diseño:
        Cada detector es INDEPENDIENTE. No dependen entre sí, lo que
        permite evaluar componentes de forma aislada y facilita la
        extensibilidad del sistema.
    """

    # =================================================
    # PESOS DEL MODELO DE TOULMIN
    # =================================================
    # Justificación de los pesos:
    # - Data (25): La evidencia empírica es el fundamento más
    #   importante de cualquier argumento académico.
    # - Claim (20): Sin tesis no hay argumento, pero la tesis
    #   sin evidencia carece de fuerza.
    # - Warrant (20): La justificación lógica es esencial para
    #   la validez del razonamiento.
    # - Backing (15): El respaldo institucional refuerza la
    #   credibilidad pero es secundario a la lógica.
    # - Qualifier (10): La modulación epistémica indica madurez
    #   argumentativa pero no es estructuralmente esencial.
    # - Rebuttal (10): Considerar objeciones muestra rigor
    #   dialéctico pero no siempre es obligatorio.
    # =================================================

    PESOS = {
        "claim": 20,
        "data": 25,
        "warrant": 20,
        "backing": 15,
        "qualifier": 10,
        "rebuttal": 10,
    }

    def __init__(self):
        """
        Inicializa el evaluador y verifica la disponibilidad de spaCy.
        Precarga todos los patrones lingüísticos compilados para
        mejorar el rendimiento en evaluaciones masivas.
        """
        self.nlp = nlp
        self._compile_patterns()

    # =================================================
    # COMPILACIÓN DE PATRONES REGEX
    # =================================================
    # Se compilan una sola vez en __init__ para evitar
    # recompilación en cada llamada a los detectores.
    # =================================================

    def _compile_patterns(self):
        """
        Compila todos los patrones regex utilizados por los
        detectores. Se almacenan como atributos de instancia
        para reutilización eficiente.
        """

        # -------------------------------------------------
        # PATRONES PARA CLAIM (Tesis/Conclusión)
        # -------------------------------------------------
        # Fundamento teórico: Un claim en el modelo de Toulmin
        # es la proposición que el argumentador quiere que la
        # audiencia acepte. Se identifica mediante:
        #
        # a) Marcadores de conclusión explícitos:
        #    "en conclusión", "por lo tanto", etc.
        #    → Señalan que lo que sigue es la tesis derivada.
        #
        # b) Verbos de aserción en primera persona:
        #    "afirmo que", "sostengo que", "defiendo que"
        #    → Indican compromiso epistémico del hablante.
        #
        # c) Marcadores de postura:
        #    "mi posición es", "considero que"
        #    → Explicitan la tesis del argumentador.
        #
        # d) Estructuras de tesis declarativa:
        #    "es necesario que", "se debe", "es fundamental"
        #    → Proposiciones normativas o prescriptivas que
        #      funcionan como claims implícitos.
        # -------------------------------------------------

        self._claim_markers = [
            # Marcadores de conclusión
            r"en\s+conclusi[oó]n",
            r"por\s+lo\s+tanto",
            r"por\s+consiguiente",
            r"en\s+consecuencia",
            r"de\s+ah[ií]\s+que",
            r"se\s+concluye\s+que",
            r"podemos\s+concluir\s+que",
            r"esto\s+demuestra\s+que",
            r"esto\s+indica\s+que",
            r"queda\s+claro\s+que",
            r"resulta\s+evidente\s+que",

            # Verbos de aserción
            r"(?:yo\s+)?afirmo\s+que",
            r"(?:yo\s+)?sostengo\s+que",
            r"(?:yo\s+)?defiendo\s+que",
            r"(?:yo\s+)?argumento\s+que",
            r"(?:yo\s+)?planteo\s+que",
            r"(?:yo\s+)?propongo\s+que",

            # Marcadores de postura
            r"mi\s+posici[oó]n\s+es",
            r"mi\s+tesis\s+es",
            r"(?:yo\s+)?considero\s+que",
            r"(?:yo\s+)?creo\s+firmemente\s+que",
            r"la\s+postura\s+(?:que\s+)?(?:defiendo|sostengo)",
            r"nuestra\s+posici[oó]n",

            # Estructuras prescriptivas/declarativas
            r"es\s+necesario\s+(?:que\s+)?",
            r"es\s+fundamental\s+(?:que\s+)?",
            r"es\s+imprescindible\s+(?:que\s+)?",
            r"se\s+debe(?:r[ií]a)?",
            r"es\s+evidente\s+que",
            r"est[aá]\s+claro\s+que",
            r"no\s+cabe\s+duda\s+(?:de\s+)?que",
        ]

        self._claim_patterns = [
            re.compile(p, re.IGNORECASE) for p in self._claim_markers
        ]

        # -------------------------------------------------
        # PATRONES PARA DATA/GROUNDS (Evidencia)
        # -------------------------------------------------
        # Fundamento teórico: Los data/grounds en Toulmin son
        # los hechos, cifras, observaciones o ejemplos concretos
        # que sustentan el claim. Se detectan mediante:
        #
        # a) Cifras y estadísticas:
        #    Porcentajes, cantidades numéricas, años.
        #    → Evidencia cuantitativa.
        #
        # b) Marcadores de ejemplificación:
        #    "por ejemplo", "como ejemplo", "un caso"
        #    → Señalan evidencia anecdótica o casuística.
        #
        # c) Marcadores de referencia a datos:
        #    "según los datos", "las cifras muestran"
        #    → Señalan apelación a evidencia empírica.
        #
        # d) Marcadores de hechos observables:
        #    "se ha observado", "se ha demostrado"
        #    → Indican evidencia observacional.
        # -------------------------------------------------

        self._data_markers = [
            # Cifras y estadísticas
            r"\d+(?:\.\d+)?%",                       # Porcentajes: 45.3%
            r"\d{1,3}(?:\.\d{3})+",                  # Números grandes: 1.000.000
            r"\d+(?:\,\d+)?\s*(?:millones|mil|billones)",  # Cantidades textuales
            r"(?:el|un|una)\s+\d+(?:\.\d+)?%",        # "el 45%"

            # Marcadores de ejemplificación
            r"por\s+ejemplo",
            r"como\s+ejemplo",
            r"un\s+caso\s+(?:concreto|espec[ií]fico|ilustrativo)",
            r"un\s+ejemplo\s+(?:de\s+(?:esto|ello)|claro|concreto)",
            r"tal(?:es)?\s+como",
            r"a\s+modo\s+de\s+ejemplo",
            r"como\s+muestra",
            r"ilustr(?:a|ando)\s+(?:esto|lo\s+anterior)",

            # Referencias a datos
            r"seg[uú]n\s+los\s+datos",
            r"los\s+datos\s+(?:muestran|indican|revelan|sugieren|demuestran)",
            r"las\s+cifras\s+(?:muestran|indican|revelan)",
            r"las\s+estad[ií]sticas\s+(?:muestran|indican|revelan|señalan)",
            r"la\s+evidencia\s+(?:muestra|indica|sugiere|demuestra)",
            r"los\s+resultados\s+(?:muestran|indican|revelan|confirman)",
            r"de\s+acuerdo\s+con\s+los\s+datos",

            # Hechos observables
            r"se\s+ha\s+(?:observado|demostrado|comprobado|verificado|registrado)",
            r"se\s+puede\s+(?:observar|constatar|verificar|comprobar)",
            r"es\s+un\s+hecho\s+(?:que|conocido)",
            r"la\s+realidad\s+(?:es\s+que|muestra|demuestra)",
            r"hist[oó]ricamente",
            r"emp[ií]ricamente",

            # Referencias bibliográficas / años entre paréntesis
            r"\(\d{4}\)",                             # (2023)
            r"\(\w+(?:\s+(?:y|&|et\s+al\.?))?,?\s*\d{4}\)",  # (García, 2023)
        ]

        self._data_patterns = [
            re.compile(p, re.IGNORECASE) for p in self._data_markers
        ]

        # -------------------------------------------------
        # PATRONES PARA WARRANT (Garantía/Justificación)
        # -------------------------------------------------
        # Fundamento teórico: La warrant en el modelo de Toulmin
        # es la regla general, principio o relación causal que
        # conecta los data con el claim. Sin warrant, la
        # transición de evidencia a conclusión queda injustificada.
        # Se detecta mediante:
        #
        # a) Conectores causales:
        #    "porque", "ya que", "dado que", "debido a"
        #    → Expresan la razón que vincula datos con claim.
        #
        # b) Conectores condicionales/inferenciales:
        #    "si...entonces", "esto implica", "por ende"
        #    → Indican una relación lógica inferencial.
        #
        # c) Marcadores de justificación:
        #    "la razón es que", "esto se explica por"
        #    → Explicitan la garantía del argumento.
        # -------------------------------------------------

        self._warrant_markers = [
            # Conectores causales (relación datos → claim)
            r"\bporque\b",
            r"\bdebido\s+a\s+(?:que\s+)?",
            r"\bya\s+que\b",
            r"\bpuesto\s+que\b",
            r"\bdado\s+que\b",
            r"\ben\s+virtud\s+de\b",
            r"\ba\s+causa\s+de\b",
            r"\bgracias\s+a\s+(?:que\s+)?",
            r"\bcomo\s+resultado\s+de\b",
            r"\bcomo\s+consecuencia\s+de\b",

            # Conectores inferenciales
            r"\bpor\s+(?:lo\s+)?tanto\b",
            r"\bpor\s+ende\b",
            r"\bpor\s+consiguiente\b",
            r"\bde\s+modo\s+que\b",
            r"\bde\s+manera\s+que\b",
            r"\besto\s+(?:implica|significa|conlleva)\s+que\b",
            r"\blo\s+(?:cual|que)\s+(?:implica|significa|demuestra)\b",

            # Estructuras condicionales
            r"\bsi\b[^.;]{5,50}\bentonces\b",
            r"\ben\s+la\s+medida\s+en\s+que\b",

            # Marcadores de justificación explícita
            r"\bla\s+raz[oó]n\s+(?:es\s+que|principal|fundamental)\b",
            r"\besto\s+se\s+(?:explica|justifica|fundamenta)\s+por\b",
            r"\bel\s+motivo\s+(?:es\s+que|principal|por\s+el\s+cual)\b",
            r"\bla\s+justificaci[oó]n\s+(?:es|radica|se\s+basa)\b",
        ]

        self._warrant_patterns = [
            re.compile(p, re.IGNORECASE) for p in self._warrant_markers
        ]

        # -------------------------------------------------
        # PATRONES PARA BACKING (Respaldo)
        # -------------------------------------------------
        # Fundamento teórico: El backing refuerza la warrant
        # apelando a autoridades, instituciones, estudios o
        # consenso académico/científico. Si la warrant dice
        # "X causa Y", el backing explica POR QUÉ podemos
        # confiar en esa relación causal.
        #
        # a) Referencias a estudios/investigaciones
        # b) Citas de expertos o autoridades
        # c) Referencias institucionales (OMS, ONU, etc.)
        # d) Apelación a consenso académico/científico
        # -------------------------------------------------

        self._backing_markers = [
            # Estudios e investigaciones
            r"seg[uú]n\s+(?:un|el|los|las|diversos|m[uú]ltiples)\s+"
            r"(?:estudio|investigaci[oó]n|informe|an[aá]lisis|reporte|encuesta)",
            r"(?:un|el|los)\s+estudio\s+(?:de|del|realizado|publicado|reciente)",
            r"(?:una|la|las)\s+investigaci[oó]n\s+(?:de|del|realizada|publicada|reciente)",
            r"(?:el|los|un)\s+informe\s+(?:de|del|publicado|elaborado)",
            r"investigaciones\s+(?:recientes|previas|anteriores|cient[ií]ficas)",
            r"estudios\s+(?:recientes|previos|anteriores|cient[ií]ficos|emp[ií]ricos)",

            # Expertos y autoridades
            r"seg[uú]n\s+(?:el\s+)?(?:experto|especialista|investigador|cient[ií]fico|"
            r"profesor|doctor|acad[eé]mico|autor)",
            r"(?:el|la|los|las)\s+(?:experto|especialista|investigador|"
            r"cient[ií]fico)s?\s+(?:señala|indica|afirma|sostiene|concluye|argumenta)",
            r"como\s+(?:señala|indica|afirma|sostiene|argumenta)\s+\w+",
            r"en\s+palabras\s+de",
            r"(?:el|la)\s+(?:Dr\.|Dra\.|Prof\.|profesor|doctora?)\s+\w+",

            # Instituciones y organismos
            r"(?:la|el|los|las)\s+(?:OMS|ONU|UNESCO|UNICEF|OIT|FAO|FMI|"
            r"Banco\s+Mundial|OCDE|CEPAL|OEA|UE|Uni[oó]n\s+Europea)",
            r"(?:la|el)\s+(?:organizaci[oó]n|organismo|instituci[oó]n|"
            r"entidad)\s+(?:mundial|internacional|nacional)",
            r"(?:la|el)\s+(?:ministerio|secretar[ií]a|departamento)\s+de",
            r"(?:la|el)\s+gobierno\s+(?:de|del|federal|nacional|estatal)",
            r"(?:la|el)\s+(?:universidad|instituto|centro\s+de\s+investigaci[oó]n)",

            # Publicaciones y fuentes académicas
            r"publicado\s+en",
            r"(?:la|el)\s+(?:revista|journal|publicaci[oó]n)\s+(?:cient[ií]fica|acad[eé]mica)",
            r"(?:fuentes|datos)\s+(?:oficiales|acad[eé]mic[ao]s|cient[ií]fic[ao]s)",
            r"(?:la|el)\s+(?:literatura|bibliograf[ií]a|corpus)\s+"
            r"(?:cient[ií]fica|acad[eé]mica|especializada)",

            # Consenso
            r"(?:el|existe|hay)\s+(?:un\s+)?consenso\s+(?:cient[ií]fico|acad[eé]mico|general)",
            r"la\s+comunidad\s+(?:cient[ií]fica|acad[eé]mica|internacional)",
            r"ampliamente\s+(?:aceptado|reconocido|documentado)",
        ]

        self._backing_patterns = [
            re.compile(p, re.IGNORECASE) for p in self._backing_markers
        ]

        # -------------------------------------------------
        # PATRONES PARA QUALIFIER (Cualificador)
        # -------------------------------------------------
        # Fundamento teórico: Los qualifiers modulan el grado
        # de certeza del claim. Un argumento maduro reconoce
        # que sus conclusiones no son absolutas. Los qualifiers
        # son marcadores epistémicos que expresan probabilidad,
        # frecuencia o alcance limitado.
        #
        # Según Toulmin, su ausencia puede indicar:
        # a) Exceso de confianza (dogmatismo)
        # b) Falta de madurez argumentativa
        # c) O bien un argumento deliberadamente absoluto
        # -------------------------------------------------

        self._qualifier_markers = [
            # Probabilidad
            r"\bprobablemente\b",
            r"\bposiblemente\b",
            r"\bpresumiblemente\b",
            r"\bseguramente\b",
            r"\baparentemente\b",
            r"\bprevisiblemente\b",

            # Frecuencia
            r"\bgeneralmente\b",
            r"\busualmente\b",
            r"\bnormalmente\b",
            r"\bfrecuentemente\b",
            r"\bt[ií]picamente\b",
            r"\bhabitualmente\b",
            r"\bcom[uú]nmente\b",

            # Expresiones de alcance
            r"\ben\s+la\s+mayor[ií]a\s+de\s+(?:los\s+)?casos\b",
            r"\bcasi\s+siempre\b",
            r"\bcasi\s+nunca\b",
            r"\ben\s+general\b",
            r"\bpor\s+lo\s+general\b",
            r"\ben\s+t[eé]rminos\s+generales\b",
            r"\ben\s+gran\s+(?:parte|medida)\b",
            r"\bhasta\s+cierto\s+punto\b",

            # Modalidad epistémica
            r"\bes\s+(?:muy\s+)?probable\s+que\b",
            r"\bes\s+(?:muy\s+)?posible\s+que\b",
            r"\bpodr[ií]a\s+(?:ser|decirse|argumentarse|considerarse)\b",
            r"\btiende\s+a\b",
            r"\bsuele\s+(?:ser|ocurrir|suceder|pasar)\b",
            r"\bno\s+necesariamente\b",
            r"\bno\s+siempre\b",
            r"\ben\s+cierta\s+medida\b",
            r"\bcon\s+(?:alta|cierta|alguna)\s+probabilidad\b",
        ]

        self._qualifier_patterns = [
            re.compile(p, re.IGNORECASE) for p in self._qualifier_markers
        ]

        # -------------------------------------------------
        # PATRONES PARA REBUTTAL (Refutación/Contraargumento)
        # -------------------------------------------------
        # Fundamento teórico: El rebuttal establece las
        # condiciones bajo las cuales el claim NO se sostiene,
        # o presenta objeciones que el argumentador reconoce.
        # La presencia de rebuttals indica madurez dialéctica
        # y anticipación de posibles críticas.
        #
        # Se detecta mediante:
        # a) Conectores adversativos
        # b) Marcadores de excepción
        # c) Marcadores de concesión
        # d) Reconocimiento explícito de objeciones
        # -------------------------------------------------

        self._rebuttal_markers = [
            # Conectores adversativos
            r"\bsin\s+embargo\b",
            r"\bno\s+obstante\b",
            r"\ba\s+pesar\s+de\s+(?:que|ello|esto|todo)\b",
            r"\bpor\s+(?:el\s+)?(?:otro|otra)\s+(?:lado|parte)\b",
            r"\ben\s+(?:cambio|contraste)\b",
            r"\bpor\s+el\s+contrario\b",
            r"\bal\s+contrario\b",
            r"\bcon\s+todo\b",
            r"\bahora\s+bien\b",

            # Marcadores de excepción
            r"\bexcepto\s+(?:que|cuando|si|en)\b",
            r"\bsalvo\s+(?:que|cuando|si|en)\b",
            r"\ba\s+menos\s+que\b",
            r"\ba\s+no\s+ser\s+que\b",
            r"\bsiempre\s+(?:y\s+)?(?:que|cuando)\b",
            r"\bmientras\s+(?:que\s+)?(?:no)\b",

            # Conectores concesivos
            r"\baunque\b",
            r"\baun\s+(?:cuando|as[ií]|si)\b",
            r"\bsi\s+bien\b",
            r"\bpese\s+a\s+(?:que|ello|esto|todo)\b",

            # Reconocimiento de objeciones
            r"\bse\s+podr[ií]a\s+(?:objetar|argumentar|contra-?argumentar)\b",
            r"\b(?:los|las|algunos|algunas)\s+(?:cr[ií]ticos|cr[ií]ticas|"
            r"detractores|opositores)\s+(?:señalan|argumentan|sostienen|afirman)\b",
            r"\bla\s+(?:cr[ií]tica|objeci[oó]n|postura\s+contraria)\b",
            r"\bun\s+(?:contra-?argumento|argumento\s+en\s+contra)\b",
            r"\bquienes\s+(?:se\s+oponen|critican|cuestionan|objetan)\b",
            r"\bes\s+cierto\s+que\b.*?\bpero\b",
            r"\breconocemos?\s+que\b",
            r"\badmit(?:o|imos|iendo)\s+que\b",
        ]

        self._rebuttal_patterns = [
            re.compile(p, re.IGNORECASE | re.DOTALL)
            for p in self._rebuttal_markers
        ]

    # =================================================
    # UTILIDADES INTERNAS
    # =================================================

    def _extract_sentence_context(
        self, text: str, match: re.Match, window: int = 150
    ) -> str:
        """
        Extrae un fragmento contextual alrededor de un match regex.

        En lugar de devolver solo el marcador encontrado, extrae la
        oración o un fragmento de contexto de ±window caracteres
        alrededor del match, delimitado por puntos, punto y coma,
        o saltos de línea.

        Parámetros:
            text: Texto completo
            match: Objeto Match de regex
            window: Número máximo de caracteres de contexto a cada lado

        Retorna:
            str: Fragmento contextual recortado
        """
        start = max(0, match.start() - window)
        end = min(len(text), match.end() + window)

        fragment = text[start:end].strip()

        # Intentar delimitar por oraciones
        # Buscar el inicio de oración más cercano
        sentence_delimiters = [". ", ".\n", ";\n", "\n\n"]
        best_start = 0
        for delim in sentence_delimiters:
            idx = fragment.rfind(delim, 0, match.start() - start)
            if idx != -1:
                best_start = max(best_start, idx + len(delim))

        # Buscar el fin de oración más cercano
        best_end = len(fragment)
        for delim in [". ", ".\n", ";\n", "\n\n"]:
            idx = fragment.find(delim, match.end() - start)
            if idx != -1:
                best_end = min(best_end, idx + 1)

        result = fragment[best_start:best_end].strip()

        # Si el resultado es demasiado corto, devolver el fragmento completo
        if len(result) < 20:
            return fragment.strip()

        return result

    def _compute_confidence(
        self,
        num_indicators: int,
        num_unique_types: int,
        thresholds: tuple = (1, 2, 4, 6)
    ) -> float:
        """
        Calcula el nivel de confianza de la detección basado en la
        cantidad de indicadores encontrados y la diversidad de tipos.

        La confianza se basa en:
        1. Cantidad total de indicadores (peso 60%)
        2. Diversidad de tipos de indicadores (peso 40%)

        Esto evita que la repetición de un solo tipo de marcador
        infle artificialmente la confianza.

        Parámetros:
            num_indicators: Total de coincidencias encontradas
            num_unique_types: Número de patrones distintos que coincidieron
            thresholds: Tupla de umbrales para asignar niveles

        Retorna:
            float: Confianza entre 0.0 y 1.0
        """
        if num_indicators == 0:
            return 0.0

        # Componente de cantidad (escala 0-1)
        t1, t2, t3, t4 = thresholds
        if num_indicators >= t4:
            quantity_score = 1.0
        elif num_indicators >= t3:
            quantity_score = 0.8
        elif num_indicators >= t2:
            quantity_score = 0.6
        elif num_indicators >= t1:
            quantity_score = 0.4
        else:
            quantity_score = 0.2

        # Componente de diversidad (escala 0-1)
        if num_unique_types >= 4:
            diversity_score = 1.0
        elif num_unique_types >= 3:
            diversity_score = 0.8
        elif num_unique_types >= 2:
            diversity_score = 0.6
        else:
            diversity_score = 0.4

        # Confianza ponderada
        confidence = (0.6 * quantity_score) + (0.4 * diversity_score)

        return round(min(confidence, 1.0), 2)

    def _detect_with_patterns(
        self,
        text: str,
        patterns: List[re.Pattern],
        marker_names: List[str],
        thresholds: tuple = (1, 2, 4, 6),
    ) -> Dict[str, Any]:
        """
        Motor genérico de detección basado en patrones regex.

        Busca todas las coincidencias de cada patrón en el texto
        y recopila: fragmentos contextuales, indicadores activados,
        conteo total y diversidad de tipos.

        Parámetros:
            text: Texto a analizar
            patterns: Lista de patrones regex compilados
            marker_names: Nombres legibles de cada patrón
              (para trazabilidad)
            thresholds: Umbrales para cálculo de confianza

        Retorna:
            dict con claves:
                - total_matches: int
                - unique_types: int
                - fragments: list[str]
                - indicators_found: list[str]
                - confidence: float
        """
        all_fragments = []
        indicators_found = []
        matched_types = set()
        seen_fragments = set()

        for i, pattern in enumerate(patterns):
            for match in pattern.finditer(text):
                marker_label = (
                    marker_names[i]
                    if i < len(marker_names)
                    else pattern.pattern[:40]
                )

                matched_types.add(i)

                if marker_label not in indicators_found:
                    indicators_found.append(marker_label)

                fragment = self._extract_sentence_context(text, match)
                # Evitar fragmentos duplicados
                frag_key = fragment[:60].lower()
                if frag_key not in seen_fragments:
                    seen_fragments.add(frag_key)
                    all_fragments.append(fragment)

        total_matches = len(all_fragments)
        unique_types = len(matched_types)

        confidence = self._compute_confidence(
            total_matches, unique_types, thresholds
        )

        return {
            "total_matches": total_matches,
            "unique_types": unique_types,
            "fragments": all_fragments,
            "indicators_found": indicators_found,
            "confidence": confidence,
        }

    def _enrich_with_spacy(self, text: str) -> Dict[str, Any]:
        """
        Realiza análisis lingüístico complementario con spaCy.

        Extrae información morfosintáctica que refuerza la
        detección de componentes de Toulmin:

        - Entidades nombradas (NER): Útil para backing
          (organizaciones, personas)
        - Oraciones: Útil para segmentación del argumento
        - POS tags: Útil para detectar verbos modales
          (qualifiers), verbos de aserción (claims)

        Retorna:
            dict con:
                - entities: lista de (texto, tipo)
                - num_sentences: int
                - modal_verbs: lista de verbos modales
                - assertion_verbs: lista de verbos de aserción
        """
        if not self.nlp:
            return {
                "entities": [],
                "num_sentences": 0,
                "modal_verbs": [],
                "assertion_verbs": [],
            }

        doc = self.nlp(text)

        entities = [
            (ent.text, ent.label_) for ent in doc.ents
        ]

        num_sentences = len(list(doc.sents))

        # Verbos modales (indicadores de qualifier)
        modal_lemmas = {
            "poder", "deber", "soler", "tender"
        }
        modal_verbs = [
            token.text for token in doc
            if token.pos_ == "VERB"
            and token.lemma_.lower() in modal_lemmas
        ]

        # Verbos de aserción (indicadores de claim)
        assertion_lemmas = {
            "afirmar", "sostener", "defender", "argumentar",
            "proponer", "plantear", "concluir", "demostrar",
            "considerar", "establecer"
        }
        assertion_verbs = [
            token.text for token in doc
            if token.pos_ == "VERB"
            and token.lemma_.lower() in assertion_lemmas
        ]

        return {
            "entities": entities,
            "num_sentences": num_sentences,
            "modal_verbs": modal_verbs,
            "assertion_verbs": assertion_verbs,
        }

    # =================================================
    # DETECTOR DE CLAIM (Tesis/Conclusión)
    # =================================================

    def detect_claim(self, text: str) -> Dict[str, Any]:
        """
        Detecta la presencia de un CLAIM (tesis/conclusión) en el texto.

        Reglas implementadas:
        ─────────────────────
        R1. Marcadores de conclusión explícitos:
            "en conclusión", "por lo tanto", "se concluye que", etc.
            Justificación Toulmin: Estos marcadores señalan
            explícitamente la proposición principal que el
            argumentador defiende.

        R2. Verbos de aserción en primera persona:
            "afirmo que", "sostengo que", "defiendo que"
            Justificación Toulmin: El compromiso epistémico directo
            del hablante indica su claim personal.

        R3. Estructuras prescriptivas/declarativas:
            "es necesario que", "se debe", "es fundamental"
            Justificación Toulmin: Las proposiciones normativas
            funcionan como claims implícitos en argumentación
            práctica.

        R4. Análisis spaCy — verbos de aserción:
            Se detectan lemas de verbos asertivos mediante
            análisis morfológico.
            Justificación Toulmin: Complementa R2 detectando
            variantes conjugadas que las regex no cubren.

        Parámetros:
            text: str — Texto del argumento a analizar

        Retorna:
            dict:
                presencia: int (0 o 1)
                confianza: float (0.0 a 1.0)
                fragmentos: list[str]
                indicadores_encontrados: list[str]
                puntos: float
                reglas_activadas: list[str]
        """
        # Nombres legibles para trazabilidad
        marker_names = [
            "conclusión: en conclusión",
            "conclusión: por lo tanto",
            "conclusión: por consiguiente",
            "conclusión: en consecuencia",
            "conclusión: de ahí que",
            "conclusión: se concluye que",
            "conclusión: podemos concluir que",
            "conclusión: esto demuestra que",
            "conclusión: esto indica que",
            "conclusión: queda claro que",
            "conclusión: resulta evidente que",
            "aserción: afirmo que",
            "aserción: sostengo que",
            "aserción: defiendo que",
            "aserción: argumento que",
            "aserción: planteo que",
            "aserción: propongo que",
            "postura: mi posición es",
            "postura: mi tesis es",
            "postura: considero que",
            "postura: creo firmemente que",
            "postura: la postura que defiendo",
            "postura: nuestra posición",
            "prescriptivo: es necesario",
            "prescriptivo: es fundamental",
            "prescriptivo: es imprescindible",
            "prescriptivo: se debe",
            "prescriptivo: es evidente que",
            "prescriptivo: está claro que",
            "prescriptivo: no cabe duda",
        ]

        result = self._detect_with_patterns(
            text, self._claim_patterns, marker_names,
            thresholds=(1, 2, 3, 5)
        )

        # Enriquecimiento con spaCy
        reglas_activadas = []
        spacy_info = self._enrich_with_spacy(text)

        if spacy_info["assertion_verbs"]:
            extra_confidence_boost = min(
                len(spacy_info["assertion_verbs"]) * 0.05, 0.15
            )
            result["confidence"] = min(
                result["confidence"] + extra_confidence_boost, 1.0
            )
            reglas_activadas.append(
                f"R4_spacy_verbos_asercion: {spacy_info['assertion_verbs']}"
            )

        if result["total_matches"] > 0:
            reglas_activadas.insert(0, "R1-R3_patrones_regex")

        presencia = 1 if result["confidence"] > 0 else 0
        puntos = round(presencia * result["confidence"] * self.PESOS["claim"], 2)

        return {
            "presencia": presencia,
            "confianza": round(result["confidence"], 2),
            "fragmentos": result["fragments"][:5],  # Máximo 5 fragmentos
            "indicadores_encontrados": result["indicators_found"],
            "puntos": puntos,
            "puntos_maximos": self.PESOS["claim"],
            "reglas_activadas": reglas_activadas,
        }

    # =================================================
    # DETECTOR DE DATA/GROUNDS (Evidencia)
    # =================================================

    def detect_data(self, text: str) -> Dict[str, Any]:
        """
        Detecta la presencia de DATA/GROUNDS (evidencia) en el texto.

        Reglas implementadas:
        ─────────────────────
        R1. Cifras y estadísticas:
            Porcentajes (45.3%), números grandes, cantidades.
            Justificación Toulmin: La evidencia cuantitativa es
            el tipo más fuerte de data. Proporciona sustento
            empírico verificable al claim.

        R2. Marcadores de ejemplificación:
            "por ejemplo", "un caso concreto", "tal como"
            Justificación Toulmin: Los ejemplos concretos funcionan
            como data anecdótica que ilustra y sustenta el claim.

        R3. Referencias a datos empíricos:
            "los datos muestran", "la evidencia indica"
            Justificación Toulmin: La apelación explícita a datos
            señala que el argumentador fundamenta su claim en
            evidencia observable.

        R4. Hechos observables:
            "se ha demostrado", "empíricamente"
            Justificación Toulmin: Los hechos establecidos
            constituyen la base fáctica del argumento.

        R5. Referencias bibliográficas:
            Patrones como (2023), (García, 2024)
            Justificación Toulmin: Las citas formales indican
            que los data provienen de fuentes verificables.

        R6. Análisis spaCy — Entidades numéricas:
            Detección de entidades de tipo CARDINAL, PERCENT,
            QUANTITY, MONEY, DATE.
            Justificación Toulmin: Las entidades numéricas
            detectadas por NER complementan la detección regex
            de datos cuantitativos.

        Parámetros:
            text: str — Texto del argumento a analizar

        Retorna:
            dict con estructura estándar del detector
        """
        marker_names = [
            "cifra: porcentaje",
            "cifra: número grande",
            "cifra: cantidad textual",
            "cifra: porcentaje con artículo",
            "ejemplo: por ejemplo",
            "ejemplo: como ejemplo",
            "ejemplo: un caso concreto",
            "ejemplo: un ejemplo de esto",
            "ejemplo: tales como",
            "ejemplo: a modo de ejemplo",
            "ejemplo: como muestra",
            "ejemplo: ilustrando",
            "dato: según los datos",
            "dato: los datos muestran",
            "dato: las cifras muestran",
            "dato: las estadísticas muestran",
            "dato: la evidencia muestra",
            "dato: los resultados muestran",
            "dato: de acuerdo con los datos",
            "hecho: se ha observado/demostrado",
            "hecho: se puede observar",
            "hecho: es un hecho que",
            "hecho: la realidad es que",
            "hecho: históricamente",
            "hecho: empíricamente",
            "referencia: año entre paréntesis",
            "referencia: cita formal (Autor, año)",
        ]

        result = self._detect_with_patterns(
            text, self._data_patterns, marker_names,
            thresholds=(1, 3, 5, 8)
        )

        # Enriquecimiento con spaCy: entidades numéricas
        reglas_activadas = []
        spacy_info = self._enrich_with_spacy(text)

        numeric_entity_types = {"CARDINAL", "PERCENT", "QUANTITY", "MONEY", "DATE"}
        numeric_entities = [
            (ent_text, ent_label)
            for ent_text, ent_label in spacy_info["entities"]
            if ent_label in numeric_entity_types
        ]

        if numeric_entities:
            extra_boost = min(len(numeric_entities) * 0.04, 0.15)
            result["confidence"] = min(
                result["confidence"] + extra_boost, 1.0
            )
            reglas_activadas.append(
                f"R6_spacy_entidades_numericas: "
                f"{[e[0] for e in numeric_entities[:5]]}"
            )

        if result["total_matches"] > 0:
            reglas_activadas.insert(0, "R1-R5_patrones_regex")

        presencia = 1 if result["confidence"] > 0 else 0
        puntos = round(presencia * result["confidence"] * self.PESOS["data"], 2)

        return {
            "presencia": presencia,
            "confianza": round(result["confidence"], 2),
            "fragmentos": result["fragments"][:5],
            "indicadores_encontrados": result["indicators_found"],
            "puntos": puntos,
            "puntos_maximos": self.PESOS["data"],
            "reglas_activadas": reglas_activadas,
        }

    # =================================================
    # DETECTOR DE WARRANT (Garantía/Justificación)
    # =================================================

    def detect_warrant(self, text: str) -> Dict[str, Any]:
        """
        Detecta la presencia de WARRANT (justificación lógica)
        en el texto.

        Reglas implementadas:
        ─────────────────────
        R1. Conectores causales:
            "porque", "debido a", "ya que", "puesto que",
            "dado que", "a causa de"
            Justificación Toulmin: Los conectores causales son
            el principal indicador lingüístico de la warrant,
            ya que explicitan la relación inferencial entre
            los data y el claim. La warrant responde a la
            pregunta: "¿Por qué los datos apoyan la conclusión?"

        R2. Conectores inferenciales:
            "por tanto", "por ende", "esto implica que"
            Justificación Toulmin: Señalan la transición lógica
            que la warrant provee, haciendo explícito el paso
            del data al claim.

        R3. Estructuras condicionales:
            "si...entonces", "en la medida en que"
            Justificación Toulmin: Las construcciones
            condicionales expresan warrants en forma de regla
            general: "Si X, entonces Y".

        R4. Marcadores de justificación explícita:
            "la razón es que", "esto se explica por"
            Justificación Toulmin: Estos marcadores señalan
            explícitamente que el hablante está articulando
            la garantía de su razonamiento.

        Parámetros:
            text: str — Texto del argumento a analizar

        Retorna:
            dict con estructura estándar del detector
        """
        marker_names = [
            "causal: porque",
            "causal: debido a",
            "causal: ya que",
            "causal: puesto que",
            "causal: dado que",
            "causal: en virtud de",
            "causal: a causa de",
            "causal: gracias a",
            "causal: como resultado de",
            "causal: como consecuencia de",
            "inferencial: por tanto",
            "inferencial: por ende",
            "inferencial: por consiguiente",
            "inferencial: de modo que",
            "inferencial: de manera que",
            "inferencial: esto implica que",
            "inferencial: lo cual implica",
            "condicional: si...entonces",
            "condicional: en la medida en que",
            "justificación: la razón es que",
            "justificación: esto se explica por",
            "justificación: el motivo es que",
            "justificación: la justificación es",
        ]

        result = self._detect_with_patterns(
            text, self._warrant_patterns, marker_names,
            thresholds=(1, 2, 4, 6)
        )

        presencia = 1 if result["confidence"] > 0 else 0
        puntos = round(presencia * result["confidence"] * self.PESOS["warrant"], 2)

        reglas_activadas = []
        if result["total_matches"] > 0:
            reglas_activadas.append("R1-R4_patrones_regex")

        return {
            "presencia": presencia,
            "confianza": round(result["confidence"], 2),
            "fragmentos": result["fragments"][:5],
            "indicadores_encontrados": result["indicators_found"],
            "puntos": puntos,
            "puntos_maximos": self.PESOS["warrant"],
            "reglas_activadas": reglas_activadas,
        }

    # =================================================
    # DETECTOR DE BACKING (Respaldo)
    # =================================================

    def detect_backing(self, text: str) -> Dict[str, Any]:
        """
        Detecta la presencia de BACKING (respaldo) en el texto.

        Reglas implementadas:
        ─────────────────────
        R1. Referencias a estudios/investigaciones:
            "según un estudio", "investigaciones recientes"
            Justificación Toulmin: El backing refuerza la warrant
            citando investigación académica que respalda la regla
            general invocada.

        R2. Apelación a expertos/autoridades:
            "según el experto", "como señala el Dr."
            Justificación Toulmin: La autoridad epistémica de
            un experto proporciona backing al transferir
            credibilidad a la warrant.

        R3. Referencias institucionales:
            "la OMS", "el Banco Mundial", "la universidad"
            Justificación Toulmin: Las instituciones reconocidas
            proporcionan un respaldo institucional que refuerza
            la fiabilidad de la warrant.

        R4. Fuentes académicas:
            "publicado en", "revista científica"
            Justificación Toulmin: Las publicaciones arbitradas
            proporcionan el tipo más robusto de backing académico.

        R5. Consenso académico/científico:
            "existe consenso científico", "ampliamente aceptado"
            Justificación Toulmin: El consenso como backing indica
            que la warrant no es idiosincrásica sino compartida
            por la comunidad epistémica.

        R6. Análisis spaCy — Entidades de organización/persona:
            Detección de NER tipos ORG, PER.
            Justificación Toulmin: Las organizaciones y personas
            mencionadas pueden funcionar como backing si
            representan autoridades en el tema.

        Parámetros:
            text: str — Texto del argumento a analizar

        Retorna:
            dict con estructura estándar del detector
        """
        marker_names = [
            "estudio: según un estudio",
            "estudio: un estudio de",
            "estudio: una investigación de",
            "estudio: el informe de",
            "estudio: investigaciones recientes",
            "estudio: estudios recientes",
            "experto: según el experto",
            "experto: el experto señala",
            "experto: como señala",
            "experto: en palabras de",
            "experto: Dr./Prof.",
            "institución: organismo internacional",
            "institución: organización",
            "institución: ministerio/secretaría",
            "institución: gobierno",
            "institución: universidad/instituto",
            "fuente: publicado en",
            "fuente: revista científica",
            "fuente: fuentes oficiales",
            "fuente: literatura científica",
            "consenso: consenso científico",
            "consenso: comunidad científica",
            "consenso: ampliamente aceptado",
        ]

        result = self._detect_with_patterns(
            text, self._backing_patterns, marker_names,
            thresholds=(1, 2, 3, 5)
        )

        # Enriquecimiento con spaCy: entidades ORG y PER
        reglas_activadas = []
        spacy_info = self._enrich_with_spacy(text)

        backing_entity_types = {"ORG", "PER", "LOC"}
        backing_entities = [
            (ent_text, ent_label)
            for ent_text, ent_label in spacy_info["entities"]
            if ent_label in backing_entity_types
        ]

        if backing_entities:
            # Solo un boost moderado: las entidades por sí solas
            # no garantizan que sean backing; las regex lo confirman
            extra_boost = min(len(backing_entities) * 0.03, 0.10)
            result["confidence"] = min(
                result["confidence"] + extra_boost, 1.0
            )
            reglas_activadas.append(
                f"R6_spacy_entidades_ORG_PER: "
                f"{[e[0] for e in backing_entities[:5]]}"
            )

        if result["total_matches"] > 0:
            reglas_activadas.insert(0, "R1-R5_patrones_regex")

        presencia = 1 if result["confidence"] > 0 else 0
        puntos = round(presencia * result["confidence"] * self.PESOS["backing"], 2)

        return {
            "presencia": presencia,
            "confianza": round(result["confidence"], 2),
            "fragmentos": result["fragments"][:5],
            "indicadores_encontrados": result["indicators_found"],
            "puntos": puntos,
            "puntos_maximos": self.PESOS["backing"],
            "reglas_activadas": reglas_activadas,
        }

    # =================================================
    # DETECTOR DE QUALIFIER (Cualificador)
    # =================================================

    def detect_qualifier(self, text: str) -> Dict[str, Any]:
        """
        Detecta la presencia de QUALIFIER (cualificador) en el texto.

        Reglas implementadas:
        ─────────────────────
        R1. Adverbios de probabilidad:
            "probablemente", "posiblemente", "presumiblemente"
            Justificación Toulmin: Estos adverbios modulan la
            fuerza del claim, indicando que la conclusión no
            es absoluta sino probabilística.

        R2. Adverbios de frecuencia:
            "generalmente", "usualmente", "frecuentemente"
            Justificación Toulmin: Los adverbios de frecuencia
            limitan el alcance del claim a "la mayoría de los
            casos", reconociendo excepciones implícitas.

        R3. Expresiones de alcance:
            "en la mayoría de los casos", "casi siempre",
            "en general"
            Justificación Toulmin: Estas expresiones cuantifican
            explícitamente el grado de generalización del claim.

        R4. Modalidad epistémica:
            "es probable que", "podría ser", "tiende a"
            Justificación Toulmin: Los verbos modales epistémicos
            expresan el grado de compromiso del hablante con
            la verdad del claim.

        R5. Análisis spaCy — verbos modales:
            Detección de verbos como "poder", "deber", "soler".
            Justificación Toulmin: Los verbos modales conjugados
            que las regex no cubren son detectados por el
            análisis morfológico de spaCy.

        Parámetros:
            text: str — Texto del argumento a analizar

        Retorna:
            dict con estructura estándar del detector
        """
        marker_names = [
            "probabilidad: probablemente",
            "probabilidad: posiblemente",
            "probabilidad: presumiblemente",
            "probabilidad: seguramente",
            "probabilidad: aparentemente",
            "probabilidad: previsiblemente",
            "frecuencia: generalmente",
            "frecuencia: usualmente",
            "frecuencia: normalmente",
            "frecuencia: frecuentemente",
            "frecuencia: típicamente",
            "frecuencia: habitualmente",
            "frecuencia: comúnmente",
            "alcance: en la mayoría de los casos",
            "alcance: casi siempre",
            "alcance: casi nunca",
            "alcance: en general",
            "alcance: por lo general",
            "alcance: en términos generales",
            "alcance: en gran parte/medida",
            "alcance: hasta cierto punto",
            "epistémico: es probable que",
            "epistémico: es posible que",
            "epistémico: podría ser/decirse",
            "epistémico: tiende a",
            "epistémico: suele ser/ocurrir",
            "epistémico: no necesariamente",
            "epistémico: no siempre",
            "epistémico: en cierta medida",
            "epistémico: con alta/cierta probabilidad",
        ]

        result = self._detect_with_patterns(
            text, self._qualifier_patterns, marker_names,
            thresholds=(1, 2, 3, 5)
        )

        # Enriquecimiento con spaCy: verbos modales
        reglas_activadas = []
        spacy_info = self._enrich_with_spacy(text)

        if spacy_info["modal_verbs"]:
            extra_boost = min(
                len(spacy_info["modal_verbs"]) * 0.05, 0.15
            )
            result["confidence"] = min(
                result["confidence"] + extra_boost, 1.0
            )
            reglas_activadas.append(
                f"R5_spacy_verbos_modales: {spacy_info['modal_verbs'][:5]}"
            )

        if result["total_matches"] > 0:
            reglas_activadas.insert(0, "R1-R4_patrones_regex")

        presencia = 1 if result["confidence"] > 0 else 0
        puntos = round(presencia * result["confidence"] * self.PESOS["qualifier"], 2)

        return {
            "presencia": presencia,
            "confianza": round(result["confidence"], 2),
            "fragmentos": result["fragments"][:5],
            "indicadores_encontrados": result["indicators_found"],
            "puntos": puntos,
            "puntos_maximos": self.PESOS["qualifier"],
            "reglas_activadas": reglas_activadas,
        }

    # =================================================
    # DETECTOR DE REBUTTAL (Refutación/Contraargumento)
    # =================================================

    def detect_rebuttal(self, text: str) -> Dict[str, Any]:
        """
        Detecta la presencia de REBUTTAL (refutación/contraargumento)
        en el texto.

        Reglas implementadas:
        ─────────────────────
        R1. Conectores adversativos:
            "sin embargo", "no obstante", "a pesar de que",
            "por otro lado"
            Justificación Toulmin: Los adversativos introducen
            información que se opone o limita el claim,
            indicando que el argumentador reconoce condiciones
            bajo las cuales su conclusión podría no sostenerse.

        R2. Marcadores de excepción:
            "excepto que", "salvo que", "a menos que",
            "a no ser que"
            Justificación Toulmin: Las excepciones son el
            núcleo del rebuttal: especifican exactamente
            las circunstancias en que el claim NO aplica.

        R3. Conectores concesivos:
            "aunque", "si bien", "pese a que"
            Justificación Toulmin: La concesión reconoce la
            validez parcial de un contraargumento mientras
            se mantiene el claim, una forma sofisticada de
            rebuttal.

        R4. Reconocimiento de objeciones:
            "se podría objetar", "los críticos señalan",
            "es cierto que...pero"
            Justificación Toulmin: El reconocimiento explícito
            de objeciones potenciales es la forma más madura
            de rebuttal, demostrando que el argumentador ha
            anticipado las críticas.

        Parámetros:
            text: str — Texto del argumento a analizar

        Retorna:
            dict con estructura estándar del detector
        """
        marker_names = [
            "adversativo: sin embargo",
            "adversativo: no obstante",
            "adversativo: a pesar de que",
            "adversativo: por otro lado",
            "adversativo: en cambio/contraste",
            "adversativo: por el contrario",
            "adversativo: al contrario",
            "adversativo: con todo",
            "adversativo: ahora bien",
            "excepción: excepto que",
            "excepción: salvo que",
            "excepción: a menos que",
            "excepción: a no ser que",
            "excepción: siempre que/cuando",
            "excepción: mientras que no",
            "concesivo: aunque",
            "concesivo: aun cuando/así/si",
            "concesivo: si bien",
            "concesivo: pese a que",
            "objeción: se podría objetar",
            "objeción: los críticos señalan",
            "objeción: la crítica/objeción",
            "objeción: un contraargumento",
            "objeción: quienes se oponen",
            "objeción: es cierto que...pero",
            "objeción: reconocemos que",
            "objeción: admitimos que",
        ]

        result = self._detect_with_patterns(
            text, self._rebuttal_patterns, marker_names,
            thresholds=(1, 2, 3, 5)
        )

        presencia = 1 if result["confidence"] > 0 else 0
        puntos = round(presencia * result["confidence"] * self.PESOS["rebuttal"], 2)

        reglas_activadas = []
        if result["total_matches"] > 0:
            reglas_activadas.append("R1-R4_patrones_regex")

        return {
            "presencia": presencia,
            "confianza": round(result["confidence"], 2),
            "fragmentos": result["fragments"][:5],
            "indicadores_encontrados": result["indicators_found"],
            "puntos": puntos,
            "puntos_maximos": self.PESOS["rebuttal"],
            "reglas_activadas": reglas_activadas,
        }

    # =================================================
    # EVALUADOR PRINCIPAL
    # =================================================

    def evaluate(self, text: str) -> Dict[str, Any]:
        """
        Evalúa un argumento completo aplicando todos los
        detectores de componentes de Toulmin.

        Proceso:
        1. Ejecuta los 6 detectores de forma independiente.
        2. Calcula el puntaje total (suma de puntos de cada
           componente).
        3. Genera un diagnóstico textual interpretativo.
        4. Proporciona metadatos de trazabilidad.

        Parámetros:
            text: str — Texto del argumento a analizar

        Retorna:
            dict:
                claim: dict (resultado del detector)
                data: dict
                warrant: dict
                backing: dict
                qualifier: dict
                rebuttal: dict
                total_score: float (0-100)
                interpretacion: str
                componentes_presentes: int
                componentes_ausentes: list[str]
                metadata: dict
        """
        if not text or not text.strip():
            return {
                "error": "El texto proporcionado está vacío.",
                "total_score": 0,
            }

        # Ejecutar detectores independientes
        claim = self.detect_claim(text)
        data = self.detect_data(text)
        warrant = self.detect_warrant(text)
        backing = self.detect_backing(text)
        qualifier = self.detect_qualifier(text)
        rebuttal = self.detect_rebuttal(text)

        # Calcular puntaje total
        total_score = round(
            claim["puntos"]
            + data["puntos"]
            + warrant["puntos"]
            + backing["puntos"]
            + qualifier["puntos"]
            + rebuttal["puntos"],
            2
        )

        # Componentes presentes y ausentes
        componentes = {
            "claim": claim,
            "data": data,
            "warrant": warrant,
            "backing": backing,
            "qualifier": qualifier,
            "rebuttal": rebuttal,
        }

        presentes = sum(
            1 for c in componentes.values()
            if c["presencia"] == 1
        )

        ausentes = [
            nombre for nombre, comp in componentes.items()
            if comp["presencia"] == 0
        ]

        # Generar interpretación diagnóstica
        interpretacion = self._generar_interpretacion(
            total_score, presentes, ausentes
        )

        # Contar palabras del texto
        num_palabras = len(re.findall(r"\b\w+\b", text))

        return {
            "claim": claim,
            "data": data,
            "warrant": warrant,
            "backing": backing,
            "qualifier": qualifier,
            "rebuttal": rebuttal,
            "total_score": total_score,
            "interpretacion": interpretacion,
            "componentes_presentes": presentes,
            "componentes_ausentes": ausentes,
            "metadata": {
                "modelo": "Toulmin (1958)",
                "tipo_evaluacion": "determinística basada en reglas",
                "pesos": self.PESOS,
                "num_palabras_texto": num_palabras,
                "spacy_disponible": self.nlp is not None,
                "version": "1.0.0",
            },
        }

    # =================================================
    # EVALUADOR DE DEBATES COMPLETOS
    # =================================================

    def evaluate_debate(
        self,
        interventions: List[Dict[str, str]],
        topic: str = ""
    ) -> Dict[str, Any]:
        """
        Evalúa un debate completo compuesto por múltiples
        intervenciones.

        Cada intervención se evalúa de forma independiente con
        el modelo de Toulmin, y luego se generan métricas
        agregadas del debate.

        Parámetros:
            interventions: list[dict] — Lista de intervenciones,
                cada una con claves:
                    - "autor": str (identificador del participante)
                    - "texto": str (contenido de la intervención)
            topic: str — Tema del debate (para metadatos)

        Retorna:
            dict:
                tema: str
                num_intervenciones: int
                evaluaciones_individuales: list[dict]
                resumen_debate: dict
                    - promedio_total: float
                    - mejor_intervencion: dict
                    - peor_intervencion: dict
                    - componente_mas_fuerte: str
                    - componente_mas_debil: str
                    - distribucion_componentes: dict
                diagnostico_debate: str
        """
        if not interventions:
            return {
                "error": "No se proporcionaron intervenciones.",
                "total_score": 0,
            }

        # Evaluar cada intervención
        evaluaciones = []
        for i, intervencion in enumerate(interventions):
            autor = intervencion.get("autor", f"Participante_{i + 1}")
            texto = intervencion.get("texto", "")

            resultado = self.evaluate(texto)
            resultado["autor"] = autor
            resultado["indice"] = i + 1
            evaluaciones.append(resultado)

        # Métricas agregadas
        scores = [e["total_score"] for e in evaluaciones]
        promedio_total = round(sum(scores) / len(scores), 2) if scores else 0

        # Mejor y peor intervención
        mejor_idx = scores.index(max(scores))
        peor_idx = scores.index(min(scores))

        mejor = {
            "autor": evaluaciones[mejor_idx]["autor"],
            "indice": mejor_idx + 1,
            "score": scores[mejor_idx],
        }

        peor = {
            "autor": evaluaciones[peor_idx]["autor"],
            "indice": peor_idx + 1,
            "score": scores[peor_idx],
        }

        # Distribución de componentes a nivel de debate
        componentes_nombres = [
            "claim", "data", "warrant",
            "backing", "qualifier", "rebuttal"
        ]

        distribucion = {}
        promedios_componentes = {}

        for comp in componentes_nombres:
            presencias = sum(
                1 for e in evaluaciones
                if e.get(comp, {}).get("presencia", 0) == 1
            )

            puntos_promedio = round(
                sum(
                    e.get(comp, {}).get("puntos", 0)
                    for e in evaluaciones
                ) / len(evaluaciones),
                2
            )

            distribucion[comp] = {
                "presencia_total": presencias,
                "presencia_porcentaje": round(
                    (presencias / len(evaluaciones)) * 100, 1
                ),
                "puntos_promedio": puntos_promedio,
                "puntos_maximos": self.PESOS[comp],
            }

            promedios_componentes[comp] = puntos_promedio

        # Componente más fuerte y más débil (por proporción de puntos)
        proporciones = {
            comp: (
                promedios_componentes[comp] / self.PESOS[comp]
                if self.PESOS[comp] > 0 else 0
            )
            for comp in componentes_nombres
        }

        mas_fuerte = max(proporciones, key=proporciones.get)
        mas_debil = min(proporciones, key=proporciones.get)

        # Diagnóstico del debate
        diagnostico = self._generar_diagnostico_debate(
            promedio_total, distribucion, len(evaluaciones)
        )

        return {
            "tema": topic,
            "num_intervenciones": len(evaluaciones),
            "evaluaciones_individuales": evaluaciones,
            "resumen_debate": {
                "promedio_total": promedio_total,
                "score_maximo": max(scores),
                "score_minimo": min(scores),
                "desviacion": round(
                    (
                        sum((s - promedio_total) ** 2 for s in scores)
                        / len(scores)
                    ) ** 0.5,
                    2,
                ) if len(scores) > 1 else 0.0,
                "mejor_intervencion": mejor,
                "peor_intervencion": peor,
                "componente_mas_fuerte": mas_fuerte,
                "componente_mas_debil": mas_debil,
                "distribucion_componentes": distribucion,
            },
            "diagnostico_debate": diagnostico,
        }

    # =================================================
    # EVALUACIÓN DE TEXTO PLANO CON SEPARADOR
    # =================================================

    def evaluate_raw_debate(
        self,
        text: str,
        separator: str = "\n---\n",
        topic: str = ""
    ) -> Dict[str, Any]:
        """
        Evalúa un debate en texto plano donde las intervenciones
        están separadas por un delimitador.

        Conveniencia para evaluar debates sin estructura JSON.
        Cada segmento separado se trata como una intervención
        independiente.

        Parámetros:
            text: str — Texto completo del debate
            separator: str — Delimitador entre intervenciones
                (por defecto: "\\n---\\n")
            topic: str — Tema del debate

        Retorna:
            dict — Mismo formato que evaluate_debate()
        """
        parts = text.split(separator)
        interventions = [
            {
                "autor": f"Participante_{i + 1}",
                "texto": part.strip(),
            }
            for i, part in enumerate(parts)
            if part.strip()
        ]

        return self.evaluate_debate(interventions, topic=topic)

    # =================================================
    # GENERADORES DE INTERPRETACIÓN
    # =================================================

    def _generar_interpretacion(
        self,
        total_score: float,
        presentes: int,
        ausentes: List[str]
    ) -> str:
        """
        Genera una interpretación diagnóstica textual del resultado
        de la evaluación de un argumento individual.

        La interpretación se basa en:
        1. El puntaje total (escala 0-100)
        2. El número de componentes presentes (0-6)
        3. Los componentes ausentes específicos

        Niveles:
        - 85-100: Argumento muy completo (Toulmin completo)
        - 70-84:  Argumento sólido
        - 50-69:  Argumento con áreas de mejora
        - 30-49:  Argumento débil
        - 0-29:   Argumento muy débil o no argumentativo
        """
        # Nivel general
        if total_score >= 85:
            nivel = "MUY COMPLETO"
            descripcion = (
                "El argumento presenta una estructura argumentativa muy "
                "completa según el modelo de Toulmin. Se detectan "
                f"{presentes} de 6 componentes con buena calidad."
            )
        elif total_score >= 70:
            nivel = "SÓLIDO"
            descripcion = (
                "El argumento presenta una estructura sólida con "
                f"{presentes} componentes de Toulmin detectados. "
                "Tiene una base argumentativa fuerte pero puede "
                "mejorarse."
            )
        elif total_score >= 50:
            nivel = "MODERADO"
            descripcion = (
                "El argumento tiene una estructura moderada con "
                f"{presentes} componentes detectados. Presenta "
                "áreas significativas de mejora."
            )
        elif total_score >= 30:
            nivel = "DÉBIL"
            descripcion = (
                "El argumento presenta una estructura débil con "
                f"solo {presentes} componentes detectados. Requiere "
                "fortalecimiento significativo."
            )
        else:
            nivel = "MUY DÉBIL"
            descripcion = (
                "El texto presenta una estructura argumentativa "
                f"muy débil o insuficiente. Solo {presentes} "
                "componente(s) de Toulmin detectado(s)."
            )

        # Recomendaciones por componentes ausentes
        recomendaciones = []

        traducciones = {
            "claim": (
                "CLAIM (tesis): Incluya una afirmación clara y "
                "explícita que funcione como conclusión del argumento."
            ),
            "data": (
                "DATA (evidencia): Agregue cifras, ejemplos, "
                "estadísticas o hechos verificables que sustenten "
                "su tesis."
            ),
            "warrant": (
                "WARRANT (justificación): Explicite la conexión "
                "lógica entre sus datos y su conclusión usando "
                "conectores causales."
            ),
            "backing": (
                "BACKING (respaldo): Cite estudios, expertos o "
                "instituciones que respalden su razonamiento."
            ),
            "qualifier": (
                "QUALIFIER (cualificador): Module el grado de "
                "certeza de su tesis usando expresiones como "
                "'probablemente', 'en la mayoría de los casos'."
            ),
            "rebuttal": (
                "REBUTTAL (refutación): Considere y responda "
                "posibles objeciones o excepciones a su argumento."
            ),
        }

        for ausente in ausentes:
            if ausente in traducciones:
                recomendaciones.append(traducciones[ausente])

        interpretacion = (
            f"NIVEL: {nivel} ({total_score}/100 puntos)\n"
            f"{descripcion}"
        )

        if recomendaciones:
            interpretacion += (
                "\n\nRECOMENDACIONES:\n"
                + "\n".join(f"  • {r}" for r in recomendaciones)
            )

        return interpretacion

    def _generar_diagnostico_debate(
        self,
        promedio: float,
        distribucion: Dict,
        num_intervenciones: int
    ) -> str:
        """
        Genera un diagnóstico textual para un debate completo.

        Analiza:
        1. Calidad promedio del debate
        2. Distribución de componentes de Toulmin entre
           las intervenciones
        3. Componentes sistemáticamente ausentes
        """
        # Nivel del debate
        if promedio >= 75:
            nivel = "ALTO"
            desc = (
                f"El debate presenta una calidad argumentativa alta "
                f"con un promedio de {promedio}/100 puntos en "
                f"{num_intervenciones} intervenciones."
            )
        elif promedio >= 50:
            nivel = "MODERADO"
            desc = (
                f"El debate presenta una calidad moderada "
                f"(promedio: {promedio}/100) en "
                f"{num_intervenciones} intervenciones."
            )
        elif promedio >= 25:
            nivel = "BAJO"
            desc = (
                f"El debate presenta una calidad baja "
                f"(promedio: {promedio}/100). Las intervenciones "
                f"carecen de estructura argumentativa sólida."
            )
        else:
            nivel = "MUY BAJO"
            desc = (
                f"El debate presenta una calidad muy baja "
                f"(promedio: {promedio}/100). Se requiere una "
                f"reformulación significativa."
            )

        # Análisis de componentes débiles a nivel de debate
        debiles = []
        for comp, info in distribucion.items():
            if info["presencia_porcentaje"] < 30:
                debiles.append(
                    f"{comp.upper()} (presente en "
                    f"{info['presencia_porcentaje']}% de intervenciones)"
                )

        diagnostico = f"NIVEL DEL DEBATE: {nivel}\n{desc}"

        if debiles:
            diagnostico += (
                "\n\nCOMPONENTES DÉBILES A NIVEL DE DEBATE:\n"
                + "\n".join(f"  • {d}" for d in debiles)
            )

        return diagnostico


# =====================================================
# FUNCIÓN DE CONVENIENCIA
# =====================================================

def evaluar_toulmin(text: str) -> Dict[str, Any]:
    """
    Función de conveniencia para evaluar un argumento individual
    con el modelo de Toulmin.

    Uso rápido:
        from ToulminScore import evaluar_toulmin
        resultado = evaluar_toulmin("Texto del argumento...")

    Parámetros:
        text: str — Texto del argumento

    Retorna:
        dict — Resultado completo de la evaluación
    """
    evaluador = ToulminEvaluator()
    return evaluador.evaluate(text)


def evaluar_debate_toulmin(
    interventions: List[Dict[str, str]],
    topic: str = ""
) -> Dict[str, Any]:
    """
    Función de conveniencia para evaluar un debate completo
    con el modelo de Toulmin.

    Uso rápido:
        from ToulminScore import evaluar_debate_toulmin
        resultado = evaluar_debate_toulmin([
            {"autor": "A", "texto": "..."},
            {"autor": "B", "texto": "..."},
        ], topic="Inteligencia Artificial")

    Parámetros:
        interventions: list[dict] — Lista de intervenciones
        topic: str — Tema del debate

    Retorna:
        dict — Resultado completo de la evaluación del debate
    """
    evaluador = ToulminEvaluator()
    return evaluador.evaluate_debate(interventions, topic=topic)


# =====================================================
# EJEMPLOS DE USO
# =====================================================

if __name__ == "__main__":

    import json

    print("=" * 70)
    print("EJEMPLO 1: Evaluación de un argumento individual")
    print("=" * 70)

    argumento_ejemplo = """
    En conclusión, la implementación de energías renovables es fundamental
    para combatir el cambio climático. Según los datos del Panel
    Intergubernamental sobre Cambio Climático (IPCC, 2023), las emisiones
    de CO2 han aumentado un 45% desde niveles preindustriales. Esto ocurre
    porque la quema de combustibles fósiles libera gases de efecto
    invernadero que alteran el equilibrio térmico de la atmósfera, dado que
    estos gases impiden la disipación del calor hacia el espacio.

    Un estudio publicado en la revista Nature Energy (Smith et al., 2022)
    demuestra que la transición a energías limpias podría reducir las
    emisiones globales en un 70% para 2050. Según el Dr. James Hansen,
    climatólogo de la NASA, la evidencia científica es contundente sobre
    la relación entre combustibles fósiles y calentamiento global.

    Probablemente, en la mayoría de los casos, las políticas de transición
    energética generarán beneficios económicos netos, aunque los costos
    iniciales pueden ser significativos.

    Sin embargo, es cierto que la transición energética enfrenta desafíos
    importantes. Los críticos señalan que la intermitencia de las fuentes
    renovables como la solar y la eólica representa un problema técnico
    real. No obstante, los avances en tecnología de almacenamiento de
    energía están mitigando progresivamente esta limitación.
    """

    evaluador = ToulminEvaluator()
    resultado = evaluador.evaluate(argumento_ejemplo)

    # Mostrar resultado legible
    print("\n[RESULTADO DE LA EVALUACION]:\n")

    for componente in ["claim", "data", "warrant", "backing", "qualifier", "rebuttal"]:
        comp = resultado[componente]
        estado = "[SI]" if comp["presencia"] == 1 else "[NO]"
        print(
            f"  {estado} {componente.upper():10s} | "
            f"Confianza: {comp['confianza']:.2f} | "
            f"Puntos: {comp['puntos']:5.2f}/{comp['puntos_maximos']}"
        )
        if comp["indicadores_encontrados"]:
            for ind in comp["indicadores_encontrados"][:3]:
                print(f"     +-- {ind}")

    print(f"\n  PUNTAJE TOTAL: {resultado['total_score']}/100")
    print(f"\n  Componentes presentes: {resultado['componentes_presentes']}/6")
    if resultado["componentes_ausentes"]:
        print(f"  [!] Componentes ausentes: {', '.join(resultado['componentes_ausentes'])}")

    print(f"\n{resultado['interpretacion']}")

    # =========================================
    print("\n" + "=" * 70)
    print("EJEMPLO 2: Evaluación de un debate completo")
    print("=" * 70)

    debate_ejemplo = [
        {
            "autor": "Proponente",
            "texto": """
            Sostengo que la inteligencia artificial debe ser regulada de manera
            estricta. Los datos de la Unión Europea muestran que el 67% de las
            empresas que implementan IA no realizan auditorías éticas. Esto es
            preocupante porque los algoritmos de IA pueden perpetuar sesgos
            discriminatorios que afectan a millones de personas, ya que aprenden
            de datos históricos que reflejan desigualdades sociales existentes.

            Según la UNESCO y la Organización para la Cooperación y el
            Desarrollo Económicos (OCDE), es urgente establecer marcos
            regulatorios que garanticen la transparencia algorítmica.
            Probablemente, la autorregulación del sector tecnológico no será
            suficiente para prevenir abusos.

            Aunque reconozco que una regulación excesiva podría frenar la
            innovación, los riesgos de la IA no regulada superan con creces
            los costos regulatorios.
            """
        },
        {
            "autor": "Oponente",
            "texto": """
            Mi posición es que la regulación excesiva de la inteligencia
            artificial sería contraproducente. Por ejemplo, China invirtió
            15.000 millones de dólares en investigación de IA en 2023,
            mientras que la regulación europea ha llevado a un éxodo de
            talento tecnológico del 12% según datos del European Tech
            Alliance.

            Esto se debe a que la innovación tecnológica requiere libertad
            experimental y ciclos rápidos de iteración, dado que los marcos
            regulatorios rígidos no pueden adaptarse a la velocidad del
            cambio tecnológico.

            Un estudio del MIT Technology Review (2024) señala que los
            países con menor regulación tecnológica generalmente lideran
            en innovación y competitividad global. Sin embargo, admito que
            ciertos usos de IA de alto riesgo, como el reconocimiento facial
            o los sistemas de crédito social, podrían requerir supervisión
            específica.
            """
        },
    ]

    resultado_debate = evaluador.evaluate_debate(
        debate_ejemplo,
        topic="Regulación de la Inteligencia Artificial"
    )

    print(f"\n[RESULTADO DEL DEBATE]: {resultado_debate['tema']}")
    print(f"   Intervenciones: {resultado_debate['num_intervenciones']}")

    resumen = resultado_debate["resumen_debate"]
    print(f"\n   Promedio total: {resumen['promedio_total']}/100")
    print(f"   Score maximo:   {resumen['score_maximo']}/100")
    print(f"   Score minimo:   {resumen['score_minimo']}/100")
    print(f"   Desviacion:     {resumen['desviacion']}")

    print(f"\n   Componente mas fuerte: {resumen['componente_mas_fuerte'].upper()}")
    print(f"   Componente mas debil:  {resumen['componente_mas_debil'].upper()}")

    print("\n   Distribucion de componentes:")
    for comp, info in resumen["distribucion_componentes"].items():
        bar_len = int(info["presencia_porcentaje"] / 5)
        bar = "#" * bar_len + "." * (20 - bar_len)
        print(
            f"      {comp.upper():10s} | {bar} "
            f"{info['presencia_porcentaje']:5.1f}% | "
            f"Promedio: {info['puntos_promedio']:.2f}/{info['puntos_maximos']}"
        )

    print(f"\n{resultado_debate['diagnostico_debate']}")

    # =========================================
    print("\n" + "=" * 70)
    print("EJEMPLO 3: Argumento debil (para contraste)")
    print("=" * 70)

    argumento_debil = """
    Yo creo que la educación online es mejor que la presencial.
    Bueno, todo el mundo lo sabe. Es algo que se nota.
    Pues la verdad es que a mí me parece más cómoda.
    """

    resultado_debil = evaluador.evaluate(argumento_debil)

    print(f"\n   PUNTAJE TOTAL: {resultado_debil['total_score']}/100")
    print(f"   Componentes presentes: {resultado_debil['componentes_presentes']}/6")
    print(f"\n{resultado_debil['interpretacion']}")

    # =========================================
    print("\n" + "=" * 70)
    print("EJEMPLO 4: Salida JSON completa (formato requerido)")
    print("=" * 70)

    # Generar salida JSON simplificada
    salida_json = {
        "claim": {
            "presencia": resultado["claim"]["presencia"],
            "confianza": resultado["claim"]["confianza"],
            "puntos": resultado["claim"]["puntos"],
            "fragmento": (
                resultado["claim"]["fragmentos"][0]
                if resultado["claim"]["fragmentos"]
                else None
            ),
        },
        "data": {
            "presencia": resultado["data"]["presencia"],
            "confianza": resultado["data"]["confianza"],
            "puntos": resultado["data"]["puntos"],
            "fragmento": (
                resultado["data"]["fragmentos"][0]
                if resultado["data"]["fragmentos"]
                else None
            ),
        },
        "warrant": {
            "presencia": resultado["warrant"]["presencia"],
            "confianza": resultado["warrant"]["confianza"],
            "puntos": resultado["warrant"]["puntos"],
            "fragmento": (
                resultado["warrant"]["fragmentos"][0]
                if resultado["warrant"]["fragmentos"]
                else None
            ),
        },
        "backing": {
            "presencia": resultado["backing"]["presencia"],
            "confianza": resultado["backing"]["confianza"],
            "puntos": resultado["backing"]["puntos"],
            "fragmento": (
                resultado["backing"]["fragmentos"][0]
                if resultado["backing"]["fragmentos"]
                else None
            ),
        },
        "qualifier": {
            "presencia": resultado["qualifier"]["presencia"],
            "confianza": resultado["qualifier"]["confianza"],
            "puntos": resultado["qualifier"]["puntos"],
            "fragmento": (
                resultado["qualifier"]["fragmentos"][0]
                if resultado["qualifier"]["fragmentos"]
                else None
            ),
        },
        "rebuttal": {
            "presencia": resultado["rebuttal"]["presencia"],
            "confianza": resultado["rebuttal"]["confianza"],
            "puntos": resultado["rebuttal"]["puntos"],
            "fragmento": (
                resultado["rebuttal"]["fragmentos"][0]
                if resultado["rebuttal"]["fragmentos"]
                else None
            ),
        },
        "total_score": resultado["total_score"],
    }

    print("\n" + json.dumps(salida_json, indent=4, ensure_ascii=False))

    print("\n" + "=" * 70)
    print("[OK] Todos los ejemplos ejecutados correctamente.")
    print("=" * 70)
