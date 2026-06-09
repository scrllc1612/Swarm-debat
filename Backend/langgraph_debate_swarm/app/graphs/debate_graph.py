from langgraph.graph import StateGraph, START, END

from app.state.debate_state import DebateState
from app.graphs.swarm_subgraph import swarm_subgraph
from app.agents.proponente import generar_borrador_proponente
from app.agents.oponente import generar_borrador_oponente


def ejecutar_swarm_proponente(state: DebateState) -> dict:
    swarm_input = {
        "topic": state["topic"],
        "speaker": "proponente",
        "draft_argument": state["proposer_argument"],
        "opponent_argument": state["opponent_argument"],
        "critic_feedback": "",
        "refined_argument": "",
        "final_argument": "",
        "iteration_count": 0,
        "max_iterations": 3,
        "improvement_needed": True,
        "iteration_history": [],
    }

    swarm_output = swarm_subgraph.invoke(swarm_input)

    final_text = (
        swarm_output["final_argument"]
        if swarm_output["final_argument"]
        else swarm_output["draft_argument"]
    )

    return {
        "proposer_argument": final_text,
        "debate_history": state["debate_history"] + [
            {
                "round": state["current_round"],
                "speaker": "proponente",
                "argument": final_text,
            }
        ],
    }


def ejecutar_swarm_oponente(state: DebateState) -> dict:
    swarm_input = {
        "topic": state["topic"],
        "speaker": "oponente",
        "draft_argument": state["opponent_argument"],
        "opponent_argument": state["proposer_argument"],
        "critic_feedback": "",
        "refined_argument": "",
        "final_argument": "",
        "iteration_count": 0,
        "max_iterations": 3,
        "improvement_needed": True,
        "iteration_history": [],
    }

    swarm_output = swarm_subgraph.invoke(swarm_input)

    final_text = (
        swarm_output["final_argument"]
        if swarm_output["final_argument"]
        else swarm_output["draft_argument"]
    )

    return {
        "opponent_argument": final_text,
        "debate_history": state["debate_history"] + [
            {
                "round": state["current_round"],
                "speaker": "oponente",
                "argument": final_text,
            }
        ],
    }


def decidir_siguiente_paso(state: DebateState) -> str:
    if state["current_round"] >= state["max_rounds"]:
        return "fin"
    return "siguiente_ronda"


def avanzar_ronda(state: DebateState) -> dict:
    return {
        "current_round": state["current_round"] + 1
    }


builder = StateGraph(DebateState)

builder.add_node("proponente", generar_borrador_proponente)
builder.add_node("swarm_proponente", ejecutar_swarm_proponente)
builder.add_node("oponente", generar_borrador_oponente)
builder.add_node("swarm_oponente", ejecutar_swarm_oponente)
builder.add_node("avanzar_ronda", avanzar_ronda)

builder.add_edge(START, "proponente")
builder.add_edge("proponente", "swarm_proponente")
builder.add_edge("swarm_proponente", "oponente")
builder.add_edge("oponente", "swarm_oponente")

builder.add_conditional_edges(
    "swarm_oponente",
    decidir_siguiente_paso,
    {
        "siguiente_ronda": "avanzar_ronda",
        "fin": END,
    },
)

builder.add_edge("avanzar_ronda", "proponente")

debate_graph = builder.compile()
