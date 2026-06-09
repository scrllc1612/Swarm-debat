from app.graphs.debate_graph import debate_graph


def main():
    initial_state = {
        "topic": "La inteligencia artificial mejora la calidad de la educación superior",
        "current_round": 1,
        "max_rounds": 3,
        "proposer_argument": "",
        "opponent_argument": "",
        "debate_history": [],
        "next_speaker": "proponente",
        "debate_finished": False,
        "winner": None,
    }

    result = debate_graph.invoke(initial_state)

    print("\n=== RESULTADO FINAL DEL DEBATE ===\n")
    print(f"Tema: {result['topic']}")
    print(f"Rondas ejecutadas: {result['current_round']}")
    print("\n--- Historial del debate ---")

    for turn in result["debate_history"]:
        print(f"\nRonda {turn['round']} - {turn['speaker'].upper()}")
        print(turn["argument"])

    print("\n--- Último argumento del proponente ---")
    print(result["proposer_argument"])

    print("\n--- Último argumento del oponente ---")
    print(result["opponent_argument"])


if __name__ == "__main__":
    main()