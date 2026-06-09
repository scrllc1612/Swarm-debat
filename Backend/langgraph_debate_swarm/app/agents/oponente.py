from app.state.debate_state import DebateState


def generar_borrador_oponente(state: DebateState) -> dict:
    topic = state["topic"]
    current_round = state["current_round"]
    proposer_argument = state.get("proposer_argument", "")

    if current_round == 1:
        draft = (
            f"Como oponente, sostengo que la postura favorable sobre '{topic}' "
            f"no es completamente convincente. Considero que existen objeciones "
            f"relevantes que debilitan esa posición inicial."
        )
    else:
        draft = (
            f"Como oponente, respondo al argumento del proponente: '{proposer_argument}'. "
            f"Considero que su defensa sobre '{topic}' sigue siendo insuficiente, "
            f"porque no resuelve adecuadamente las objeciones planteadas ni prueba "
            f"de forma concluyente su postura."
        )

    return {
        "opponent_argument": draft
    }
