from langgraph.graph import StateGraph, START, END

from app.state.swarm_state import SwarmState
from app.agents.critico import criticar_argumento
from app.agents.refiner import refinar_argumento


def decidir_siguiente_paso(state: SwarmState) -> str:
    if not state["improvement_needed"]:
        return "fin"

    if state["iteration_count"] >= state["max_iterations"]:
        return "fin"

    return "refiner"


builder = StateGraph(SwarmState)

builder.add_node("critico", criticar_argumento)
builder.add_node("refiner", refinar_argumento)

builder.add_edge(START, "critico")

builder.add_conditional_edges(
    "critico",
    decidir_siguiente_paso,
    {
        "refiner": "refiner",
        "fin": END,
    },
)

builder.add_edge("refiner", "critico")

swarm_subgraph = builder.compile()
