import requests
import uuid

async def run_langflow_a2(tema, str=None):

    url = "http://localhost:7860/api/v1/run/75b9e4c4-2813-45b2-8593-ff97dc48b6e7"

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