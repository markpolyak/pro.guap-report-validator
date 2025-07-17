from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class Person(BaseModel):
    name: str
    surname: str
    patronymic: str
    status: Optional[str] = None

class Student(BaseModel):
    name: str
    surname: str
    patronymic: str
    group: str

class Report(BaseModel):
    subject_name: str
    task_name: str
    task_type: str
    teacher: Person
    report_structure: List[str]
    uploaded_at: str


class ReportUploadData(BaseModel):
    student: Student
    report: Report


class ReportUploadDataWithReportLink(BaseModel):
    student: Student
    report: Report
    report_link: str


class StatusEnum(str, Enum):
    SUCCESS = "Успешно"
    HAS_ERRORS = "С ошибками"


class ParserEnum(str, Enum):
    DOCX = "docx"
    PDF = "pdf"
    ODT = "odt"


class Response(BaseModel):
    status: StatusEnum
    parser: ParserEnum
    results: List[str]

    class Config:
        use_enum_values = True  # Для сериализации значений enum
