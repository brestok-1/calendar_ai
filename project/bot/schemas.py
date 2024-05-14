from openai import BaseModel


class UserMessageRequestSchema(BaseModel):
    query: str
    chat_id: int
    timezone: str


class GeneratedAnswerSchema(BaseModel):
    response: str
