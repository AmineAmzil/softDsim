from abc import ABC
from typing import List
from pydantic import BaseModel


class SkillTypeDTO(BaseModel):
    id: int
    name: str


class MemberDTO(BaseModel):
    id: int
    motivation: float
    stress: float
    xp: float
    skill_type: SkillTypeDTO


class AnswerDTO(BaseModel):
    id: int
    label: str
    points: int


class QuestionDTO(BaseModel):
    id: int
    index: int
    text: str
    multi: bool
    answers: List[AnswerDTO]


class QuestionCollectionDTO(BaseModel):
    id: int
    index: int
    questions: List[QuestionDTO]


class ScenarioStateDTO(BaseModel):
    counter: int
    day: int
    cost: float


class TasksStatusDTO(BaseModel):
    tasks_todo: int
    task_done: int
    tasks_unit_tested: int
    tasks_integration_tested: int
    tasks_bug: int


class ScenarioResponse(BaseModel, ABC):
    """
    This is the abstract response class that provides all data
    required in every step of the simulation. Every specific
    response inherits from this class and add their own specific
    data and also sets the type value.
    """

    type: str
    state: ScenarioStateDTO


class SimulationResponse(ScenarioResponse):
    type: str = "SIMULATION"
    tasks: TasksStatusDTO
    members: List[MemberDTO]
    # ToDo: Add list of actions (Issue #235)


class QuestionResponse(ScenarioResponse):
    type: str = "QUESTION"
    question_collection: QuestionCollectionDTO


class ModelResponse(ScenarioResponse):
    type: str = "MODEL"
    # ToDo: Add list of models (Issue #243)


class ResultResponse(ScenarioResponse):
    type: str = "RESULT"
    # ToDo: Add result stats (Issue #237)
