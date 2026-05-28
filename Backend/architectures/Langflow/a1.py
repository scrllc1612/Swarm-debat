import requests
import uuid

async def run_langflow_a1(tema):

    url = "http://localhost:7860/api/v1/run/d6e271f8-25af-4200-91d5-4efc4082e1bc"

    payload = {
        "output_type": "chat",
        "input_type": "chat",
        "input_value": tema,
        "session_id": str(uuid.uuid4())
    }

    headers = {
        "Content-Type": "application/json",
        "x-api-key": "sk-z99sLlai_Zo41ulAKxkCctG72R26CUdZgn0d1ZLUWk4"
    }

    response = requests.post(
        url,
        json=payload,
        headers=headers
    )

    response.raise_for_status()

    return response.json()