import requests

async def run_flowise_a1(tema):

    API_URL = "http://localhost:3000/api/v1/prediction/11004ee8-f183-4e06-a18a-7b1b64f9c892"

    payload = {
        "question": tema
    }

    response = requests.post(
        API_URL,
        json=payload
    )

    response.raise_for_status()

    return response.json()