import asyncio
import json
from datetime import datetime

from fastapi.websockets import WebSocket
from google.oauth2.credentials import Credentials
from sqlalchemy.ext.asyncio import AsyncSession

from project.bot.calendar_apis import send_planned_events_to_google_calendar
from project.bot.models import Chat, Message
from project.bot.utils import format_datetime
from project.config import settings
from project.ws.openai_requests import extract_parameters_from_user_query, is_enough_parameters, \
    generate_events_json_from_parameters, generate_next_question, analyze_user_query_after_plan_suggestion
from project.ws.schemas import PlannerStateSchema


class Bot:
    chat_history = []
    chat_object = None
    CURRENT_STATE = PlannerStateSchema.ASKING_QUESTIONS

    @staticmethod
    async def emergency_db_saving(session: AsyncSession):
        await session.commit()
        await session.close()

    @staticmethod
    async def _process_completion_output(messages, model="gpt-3.5-turbo", temperature=0.0, is_json=False):
        response_format = {"type": 'json_object'} if is_json else {'type': 'text'}
        completion = await settings.OPENAI_CLIENT.chat.completions.create(
            messages=messages,
            model=model,
            n=1,
            temperature=temperature,
            response_format=response_format
        )
        response = completion.choices[0].message.content
        return response


class PredictionBot(Bot):
    retrieved_parameters = {}
    today = datetime.utcnow().isoformat() + "Z"
    timezone = ''
    planned_events = []
    question_count = 0

    def __init__(self, timezone: str):
        self.timezone = timezone

    async def send_initial_message(self, websocket: WebSocket):
        messages = [
            {
                "role": "system",
                'content': settings.PROMPTS['initial_prompt']
            }
        ]

        response = await self._process_completion_output(messages=messages, model="gpt-4o")
        response = {"data": {"text": response}, 'type': 'messaging'}
        await websocket.send_json(response)

        assistant_message = {"role": 'assistant', 'content': response['data']['text']}
        self.chat_history.append(assistant_message)

    async def process_user_input(self,
                                 data: dict,
                                 websocket: WebSocket,
                                 credentials: Credentials
                                 ) -> None:

        query = data['text']
        assistant_question = self.chat_history[-1]['content']
        self.chat_history.append({'role': "user", 'content': query})

        if self.CURRENT_STATE == PlannerStateSchema.ASKING_QUESTIONS:
            extracted_parameters = await extract_parameters_from_user_query(assistant_question, query)
            self.retrieved_parameters.update(extracted_parameters)

            is_enough = self.question_count == 5
            # is_enough = await is_enough_parameters(self.retrieved_parameters)
            if is_enough:
                events_json = await generate_events_json_from_parameters(self.retrieved_parameters, self.today,
                                                                         self.timezone)
                self.planned_events = events_json['events']
                result_str = ''
                for i, event in enumerate(events_json['events']):
                    result_str += f'{i + 1} event:\n'
                    summary = event.get('summary')
                    if summary:
                        result_str += f'Summary: {summary}\n'
                    description = event.get('description')
                    if description:
                        result_str += f'Description: {description}\n'
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    end = event['end'].get('dateTime', event['end'].get('date'))

                    formatted_start = format_datetime(start)
                    formatted_end = format_datetime(end)

                    result_str += f'Start Date: {formatted_start}\n'
                    result_str += f'End Date: {formatted_end}\n\n'

                self.CURRENT_STATE = PlannerStateSchema.SUGGESTING_PLAN
                await websocket.send_json(
                    {
                        "type": "suggestion",
                        "data": {
                            "text": "Hey! Look at what future events I've managed to plan for you:",
                            "events": result_str
                        }
                    }
                )
            else:
                next_question = await generate_next_question(self.chat_history)
                self.question_count += 1
                await websocket.send_json({
                    "type": "messaging",
                    "data": {
                        "text": next_question
                    }
                })
        if self.CURRENT_STATE == PlannerStateSchema.SUGGESTING_PLAN:
            analyzed_user_query_json = await analyze_user_query_after_plan_suggestion(query, self.planned_events,
                                                                                      self.today)
            is_agree = analyzed_user_query_json['is_agree']
            if is_agree:
                asyncio.create_task(send_planned_events_to_google_calendar(self.planned_events, credentials))
                await websocket.send_json({
                    "type": "messaging",
                    "data": {
                        "text": "Great! I've already added all the events to your calendar, you can check it out 😉"
                    }
                })
            else:
                improved_events_plan = await analyzed_user_query_json['data']['events']
                self.planned_events = improved_events_plan
                await websocket.send_json({
                    "type": "suggestion",
                    'data': {
                        "text": "Okay, I get you. Here is the corrected version:",
                        "events": improved_events_plan
                    }
                })
