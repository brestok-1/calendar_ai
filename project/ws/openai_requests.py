import ast
import json

from project.config import settings


async def extract_parameters_from_user_query(assistant_question: str, query: str) -> str:
    messages = [
        {
            "role": 'system',
            "content": settings.PROMPTS['parameters_extraction']
            .replace('{assistant_message}', assistant_question)
            .replace('{user_query}', query)
        }
    ]
    completion = await settings.OPENAI_CLIENT.chat.completions.create(
        messages=messages,
        n=1,
        model="gpt-4o",
        temperature=0,
        response_format={'type': "json_object"}
    )
    response = completion.choices[0].message.content
    response = json.loads(response)
    return response


async def is_enough_parameters(parameters: dict):
    parameters_str = '\n'.join([f"{k}: {v}" for k, v in parameters.items()])
    messages = [
        {
            "role": "system",
            "content": settings.PROMPTS['is_enough_parameters'].replace('{parameters_str}', parameters_str)
        }
    ]
    completion = await settings.OPENAI_CLIENT.chat.completions.create(
        messages=messages,
        n=1,
        model="gpt-4o",
        temperature=0,
    )
    response = completion.choices[0].message.content
    return response


async def generate_events_json_from_parameters(parameters: dict, today: str, timezone: str):
    parameters_str = '\n'.join([f"{k}: {v}" for k, v in parameters.items()])

    messages = [
        {
            "role": "system",
            "content": settings.PROMPTS['generate_events_from_parameters']
            .replace('{parameters_str}', parameters_str)
            .replace('{today}', today)
            .replace('{timezone}', timezone)
        }
    ]
    completion = await settings.OPENAI_CLIENT.chat.completions.create(
        messages=messages,
        n=1,
        model="gpt-4o",
        temperature=0.2,
        response_format={'type': "json_object"}
    )
    response = completion.choices[0].message.content
    extracted_parameters = json.loads(response)
    return extracted_parameters


async def generate_next_question(message_history: list) -> str:
    messages = [
        {
            "role": "system",
            "content": settings.PROMPTS['asking_question']
        }
    ]
    messages += message_history
    completion = await settings.OPENAI_CLIENT.chat.completions.create(
        messages=messages,
        n=1,
        model="gpt-4o",
        temperature=0.4,
    )
    response = completion.choices[0].message.content
    return response


async def analyze_user_query_after_plan_suggestion(query: str, planned_events: list[dict], today: str) -> dict:
    json_string = json.dumps(planned_events, ensure_ascii=False, indent=4)
    messages = [
        {
            "role": "system",
            "content": settings.PROMPTS['analyze_user_query_after_suggestion']
            .replace('{user_query}', query)
            .replace('{planned_events}', json_string)
            .replace('{today}', today)
        }
    ]
    completion = await settings.OPENAI_CLIENT.chat.completions.create(
        messages=messages,
        n=1,
        model="gpt-4o",
        temperature=0,
        response_format={'type': "json_object"}
    )
    response = completion.choices[0].message.content
    response = json.loads(response)
    return response
