import json
from typing import Optional, List

from pydantic import BaseModel


class Student(BaseModel):
    name: str
    surname: str
    patronymic: Optional[str]  # maybe = None, clarify
    group: str


class Teacher(BaseModel):
    name: str
    surname: str
    patronymic: Optional[str]  # maybe = None, clarify
    status: str


class Report(BaseModel):
    subject_name: str
    task_name: str
    task_type: str
    teacher: Teacher
    report_structure: List[str]
    uploaded_at: str


class ReportDescription(BaseModel):
    student: Student
    report: Report
    report_link: Optional[str]

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


class ValidatorResponse(BaseModel):
    status: str
    parser: str = None
    results: List[str]


class ValidatorResponseBadRequest(BaseModel):
    status: str
    message: str
    parser: str = None
    results: List[str]


class ReportDescriptionWithLink(BaseModel):
    student: Student
    report: Report
    report_link: str
    username: str
    password: str
