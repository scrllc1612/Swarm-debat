import requests

async def run_flowise_a4(tema):

    API_URL = "http://localhost:3000/api/v1/prediction/aac045d2-20e8-4147-b1b6-d2f16b4b0b27"

    payload = {
        "question": tema
    }

    response = requests.post(
        API_URL,
        json=payload
    )

    response.raise_for_status()

    return response.json()