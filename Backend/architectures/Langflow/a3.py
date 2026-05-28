import requests
import uuid

async def run_langflow_a3(tema):

    url = "http://localhost:7860/api/v1/run/1a0c8c0e-d07d-4bdc-9cc4-bc648c77221b"

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