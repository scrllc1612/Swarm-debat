from evaluator_A1 import evaluar_debate_a1
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

from evaluator_A2 import evaluar_debate

from evaluador_A4 import evaluar_debate_a4

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FLOWISE_A1_URL = "https://cloud.flowiseai.com/api/v1/prediction/83b071ed-57dd-4cb4-aa1c-d6a5f3ce3a13"

FLOWISE_A2_URL = "http://localhost:3000/api/v1/prediction/fbd744d0-4e9f-4f82-8760-91b4d23eb18e"

FLOWISE_A4_URL = "http://localhost:3000/api/v1/prediction/aac045d2-20e8-4147-b1b6-d2f16b4b0b27"



ultimo_debate = {
    "tema": "",
    "arquitectura": "",
    "debate": ""
}

# =========================
# REQUEST MODEL
# =========================

class DebateRequest(BaseModel):
    tema: str
    arquitectura: str

# =========================
# HOME
# =========================

@app.get("/")
def home():
    return {
        "message": "Backend de debates funcionando correctamente"
    }

# =========================
# GENERAR DEBATE
# =========================

@app.post("/generar-debate")
def generar_debate(request: DebateRequest):

    # -------------------------
    # Selección de arquitectura
    # -------------------------

    if request.arquitectura == "A2":
        flow_url = FLOWISE_A2_URL
        nombre_arquitectura = "A2 - Jerárquica Síncrona"

    elif request.arquitectura == "A4":
        flow_url = FLOWISE_A4_URL
        nombre_arquitectura = "A4 - Swarm Intelligence"

    elif request.arquitectura == "A1":
        flow_url = FLOWISE_A1_URL
        nombre_arquitectura = "A1 - Secuencial Simple"

    else:
        return {
            "error": "Arquitectura no válida"
        }

    # -------------------------
    # Payload para Flowise
    # -------------------------

    payload = {
        "question": request.tema
    }

    try:

        # -------------------------
        # Request a Flowise
        # -------------------------

        response = requests.post(flow_url, json=payload)

        response.raise_for_status()

        data = response.json()

        # -------------------------
        # Obtener texto generado
        # -------------------------

        debate = data.get("text", data)

        # -------------------------
        # Guardar último debate
        # -------------------------

        ultimo_debate["tema"] = request.tema
        ultimo_debate["arquitectura"] = nombre_arquitectura
        ultimo_debate["debate"] = debate

        # -------------------------
        # Response final
        # -------------------------

        return {
            "tema": request.tema,
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
            "error": "No hay debate generado para evaluar. Primero genera un debate."
        }

    # ======================================
    # Evaluador según arquitectura
    # ======================================

    if "A2" in ultimo_debate["arquitectura"]:

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

    elif "A1" in ultimo_debate["arquitectura"]:

        resultado = evaluar_debate_a1(
            tema=ultimo_debate["tema"],
            arquitectura=ultimo_debate["arquitectura"],
            debate=ultimo_debate["debate"]
        )

    else:

        return {
            "error": "Arquitectura no soportada para evaluación"
        }

    return resultado