import requests

async def run_flowise_a2(tema):

    API_URL = "http://localhost:3000/api/v1/prediction/4f16c919-0a29-4c7f-b3b5-16fe541aff60"

    payload = {
        "question": tema
    }

    response = requests.post(
        API_URL,
        json=payload
    )

    response.raise_for_status()

    return response.json()