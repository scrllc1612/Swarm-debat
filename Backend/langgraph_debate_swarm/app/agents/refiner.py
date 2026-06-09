from app.state.swarm_state import SwarmState


def refinar_argumento(state: SwarmState) -> dict:
    draft = state["draft_argument"]
    feedback = state["critic_feedback"]
    iteration_count = state["iteration_count"] + 1

    refined = f"""
Argumento original:
{draft}

Mejora aplicada a partir de la crítica:
{feedback}

Versión refinada:
{draft} Además, este argumento ahora presenta una justificación más clara, una relación
más directa con el tema debatido y una formulación más sólida.
""".strip()

    iteration_history = list(state.get("iteration_history", []))
    iteration_history.append(
        {
            "iteration": iteration_count,
            "draft": draft,
            "feedback": feedback,
            "refined": refined,
        }
    )

    return {
        "draft_argument": refined,
        "refined_argument": refined,
        "iteration_count": iteration_count,
        "iteration_history": iteration_history,
    }
