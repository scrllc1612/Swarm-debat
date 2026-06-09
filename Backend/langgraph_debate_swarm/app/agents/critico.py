from app.state.swarm_state import SwarmState


def criticar_argumento(state: SwarmState) -> dict:
    draft = state["draft_argument"]
    topic = state["topic"]
    speaker = state["speaker"]

    feedback = []

    if len(draft.strip()) < 120:
        feedback.append(
            "El argumento es demasiado breve y necesita más desarrollo."
        )

    if topic.lower() not in draft.lower():
        feedback.append(
            "El argumento no menciona explícitamente el tema central del debate."
        )

    if "porque" not in draft.lower() and "ya que" not in draft.lower():
        feedback.append(
            "El argumento carece de un conector claro de justificación."
        )

    if speaker == "oponente" and state.get("opponent_argument", "").strip() == "":
        feedback.append(
            "No se observa todavía referencia explícita al argumento previo del proponente."
        )

    if not feedback:
        return {
            "critic_feedback": (
                "El argumento es suficientemente claro y no requiere más mejoras básicas."
            ),
            "improvement_needed": False,
            "final_argument": draft,
        }

    return {
        "critic_feedback": " ".join(feedback),
        "improvement_needed": True,
    }
