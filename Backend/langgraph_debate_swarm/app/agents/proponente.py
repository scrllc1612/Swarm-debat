from app.state.debate_state import DebateState


def generar_borrador_proponente(state: DebateState) -> dict:
    topic = state["topic"]
    current_round = state["current_round"]
    opponent_argument = state.get("opponent_argument", "")

    if current_round == 1:
        draft = (
            f"Como proponente, sostengo que sobre el tema '{topic}' existe una "
            f"posición defendible con bases racionales, coherencia interna y "
            f"relevancia argumentativa."
        )
    else:
        draft = (
            f"Como proponente, respondo al argumento del oponente: '{opponent_argument}'. "
            f"Considero que esa réplica no invalida mi postura inicial sobre '{topic}', "
            f"porque mantiene debilidades en su justificación y alcance."
        )

    return {
        "proposer_argument": draft
    }
