from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# =========================
# IMPORTAR ARQUITECTURAS LANGFLOW
# =========================

from architectures.Langflow.a1 import run_langflow_a1
from architectures.Langflow.a2 import run_langflow_a2
from architectures.Langflow.a3 import run_langflow_a3
from architectures.Langflow.a4 import run_langflow_a4

# =========================
# IMPORTAR ARQUITECTURAS FLOWISE
# =========================

from architectures.Flowise.a1 import run_flowise_a1
from architectures.Flowise.a2 import run_flowise_a2
from architectures.Flowise.a3 import run_flowise_a3
from architectures.Flowise.a4 import run_flowise_a4

# =========================
# IMPORTAR EVALUADORES
# =========================

from evaluator_A2 import evaluar_debate
from evaluador_A4 import evaluar_debate_a4
from evaluator_A1 import evaluar_debate_a1

# =========================
# FASTAPI
# =========================

app = FastAPI()

# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# MEMORIA TEMPORAL
# =========================

ultimo_debate = {
    "tema": "",
    "arquitectura": "",
    "framework": "",
    "debate": ""
}

# =========================
# REQUEST MODEL
# =========================

class DebateRequest(BaseModel):
    tema: str
    framework: str
    arquitectura: str

# =========================
# HOME
# =========================

@app.get("/")
def home():

    return {
        "message": "Backend Multiagente funcionando correctamente"
    }

# =========================
# GENERAR DEBATE
# =========================

@app.post("/generar-debate")
async def generar_debate(request: DebateRequest):

    try:

        resultado = None
        nombre_arquitectura = ""

        # ==================================================
        # FLOWISE
        # ==================================================

        if request.framework.lower() == "flowise":

            if request.arquitectura == "A1":
                resultado = await run_flowise_a1(request.tema)
                nombre_arquitectura = "A1 - Secuencial Simple"

            elif request.arquitectura == "A2":
                resultado = await run_flowise_a2(request.tema)
                nombre_arquitectura = "A2 - Jerárquica Síncrona"

            elif request.arquitectura == "A3":
                resultado = await run_flowise_a3(request.tema)
                nombre_arquitectura = "A3 - Secuencial Deliberativa"

            elif request.arquitectura == "A4":
                resultado = await run_flowise_a4(request.tema)
                nombre_arquitectura = "A4 - Swarm Intelligence"

        # ==================================================
        # LANGFLOW
        # ==================================================

        elif request.framework.lower() == "langflow":

            if request.arquitectura == "A1":
                resultado = await run_langflow_a1(request.tema)
                nombre_arquitectura = "A1 - Secuencial Simple"

            elif request.arquitectura == "A2":
                resultado = await run_langflow_a2(request.tema)
                nombre_arquitectura = "A2 - Jerárquica Síncrona"

            elif request.arquitectura == "A3":
                resultado = await run_langflow_a3(request.tema)
                nombre_arquitectura = "A3 - Secuencial Deliberativa"

            elif request.arquitectura == "A4":
                resultado = await run_langflow_a4(request.tema)
                nombre_arquitectura = "A4 - Swarm Intelligence"

        else:

            return {
                "error": "Framework no válido"
            }

        # ==================================================
        # VALIDAR RESULTADO
        # ==================================================

        if resultado is None:

            return {
                "error": "Arquitectura no válida"
            }

        # ==================================================
        # EXTRAER TEXTO
        # ==================================================

        debate = resultado.get("text", resultado)

        # ==================================================
        # GUARDAR ÚLTIMO DEBATE
        # ==================================================

        ultimo_debate["tema"] = request.tema
        ultimo_debate["arquitectura"] = nombre_arquitectura
        ultimo_debate["framework"] = request.framework
        ultimo_debate["debate"] = debate

        # ==================================================
        # RESPONSE
        # ==================================================

        return {
            "tema": request.tema,
            "framework": request.framework,
            "arquitectura": nombre_arquitectura,
            "debate": debate
        }

    except Exception as e:

        return {
            "error": "No se pudo generar el debate",
            "detalle": str(e)
        }

# =========================
# EVALUAR DEBATE
# =========================

@app.post("/evaluar-debate")
def evaluar_ultimo_debate():

    if not ultimo_debate["debate"]:

        return {
            "error": "No hay debate generado para evaluar"
        }

    # ==================================================
    # EVALUADORES
    # ==================================================

    if "A1" in ultimo_debate["arquitectura"]:

        resultado = evaluar_debate_a1(
            tema=ultimo_debate["tema"],
            arquitectura=ultimo_debate["arquitectura"],
            debate=ultimo_debate["debate"]
        )

    elif "A2" in ultimo_debate["arquitectura"]:

        resultado = evaluar_debate(
            tema=ultimo_debate["tema"],
            arquitectura=ultimo_debate["arquitectura"],
            debate=ultimo_debate["debate"]
        )

    elif "A4" in ultimo_debate["arquitectura"]:

        resultado = evaluar_debate_a4(
            tema=ultimo_debate["tema"],
            arquitectura=ultimo_debate["arquitectura"],
            debate=ultimo_debate["debate"]
        )

    else:

        return {
            "error": "Arquitectura no soportada para evaluación"
        }

    return resultado