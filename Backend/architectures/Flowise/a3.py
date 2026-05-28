import requests

async def run_flowise_a3(tema):

    API_URL = "http://localhost:3000/api/v1/prediction/fbd744d0-4e9f-4f82-8760-91b4d23eb18e"

    payload = {
        "question": tema
    }

    response = requests.post(
        API_URL,
        json=payload
    )

    response.raise_for_status()

    return response.json()