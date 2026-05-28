import requests
import uuid

async def run_langflow_a4(tema):

    url = "http://localhost:7860/api/v1/run/9edd1a3f-37e1-46b3-b559-587389ba1a0d"

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