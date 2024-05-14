import json

from project.config import settings


async def analyze_request_type(message_history: list[dict], today: str) -> dict:
    messages = [
        {
            "role": 'system',
            "content": settings.PROMPTS['analyze_query']
            .replace('{today}', today)
        }
    ]
    messages += message_history
    completion = await settings.OPENAI_CLIENT.chat.completions.create(
        messages=messages,
        n=1,
        model="gpt-4o",
        temperature=0,
        response_format={'type': 'json_object'}
    )
    response = completion.choices[0].message.content
    response = json.loads(response)
    return response


async def generate_ai_response(message_history: list[dict]) -> str:
    messages = [
        {
            "role": 'system',
            "content": settings.PROMPTS['generate_ai_response']
        }
    ]
    messages += message_history
    completion = await settings.OPENAI_CLIENT.chat.completions.create(
        messages=messages,
        n=1,
        model="gpt-4o",
        temperature=0,
    )
    response = completion.choices[0].message.content
    return response
