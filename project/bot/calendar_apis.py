from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from project.bot.utils import format_datetime


async def add_new_event(data: dict, credentials: Credentials, timezone: str) -> None:
    try:
        service = build('calendar', 'v3', credentials=credentials)
        event = {
            'start': {
                'dateTime': data['data']['date']['startTime'],
                'timeZone': timezone,
            },
            'end': {
                'dateTime': data['data']['date']['startTime'],
                'timeZone': timezone,
            },
        }
        location = data['data'].get('location')
        if location:
            event['location'] = location
        description = data['data'].get('description')
        if description:
            event['description'] = description
        summary = data['data'].get('summary')
        if summary:
            event['summary'] = summary
        service.events().insert(calendarId='primary', body=event).execute()
    except Exception as e:
        print(e)


async def show_events(data: dict, credentials: Credentials) -> str:
    service = build('calendar', 'v3', credentials=credentials)
    params = {
        'calendarId': 'primary',
        'timeMin': data['data']["date"].get('startTime'),
        'timeMax': data['data']["date"].get('endTime'),
        'singleEvents': True,
        'orderBy': 'startTime'
    }
    events_result = service.events().list(**params).execute()
    events = events_result.get('items', [])
    result_str = ''
    if not events:
        result_str = 'No events found'
    else:
        for i, event in enumerate(events):
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
    return result_str


async def delete_event(data: dict, credentials: Credentials) -> None:
    service = build('calendar', 'v3', credentials=credentials)
    params = {
        'calendarId': 'primary',
        'timeMin': data['data']["date"].get('startTime'),
        'timeMax': data['data']["date"].get('endTime'),
        'singleEvents': True,
        'orderBy': 'startTime'
    }
    events_result = service.events().list(**params).execute()
    events = events_result.get('items', [])
    for event in events:
        event_id = event['id']
        service.events().delete(calendarId='primary', eventId=event_id).execute()

