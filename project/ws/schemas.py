from enum import Enum


class PlannerStateSchema(Enum):
    ASKING_QUESTIONS = 0
    SUGGESTING_PLAN = 1