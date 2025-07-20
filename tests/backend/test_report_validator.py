import pytest
import os
import json
from io import BytesIO
from docx import Document
from datetime import datetime
from backend.report_validator import ReportValidator

def create_test_docx(title_page_content, body_content):
    """创建测试用的DOCX文档"""
    doc = Document()
    
    # 添加标题页内容
    for text in title_page_content:
        doc.add_paragraph(text)
    
    # 添加分页符
    doc.add_page_break()
    
    # 添加正文内容
    for section in body_content:
        doc.add_paragraph(section)
    
    # 保存到内存
    stream = BytesIO()
    doc.save(stream)
    stream.seek(0)
    return stream.read()

# 测试数据
VALID_STUDENT = {
    "name": "Иван",
    "surname": "Иванов",
    "patronymic": "Иванович",
    "group": "4931"
}

VALID_REPORT = {
    "subject_name": "Операционные системы",
    "task_name": "ЛР1. Знакомство с командным интерпретатором bash",
    "task_type": "Лабораторная работа",
    "teacher": {
        "name": "Юлия",
        "surname": "Антохина",
        "patronymic": "Анатольевна",
        "status": "Ректор, д.т.н., проф."
    },
    "report_structure": ["Цель", "Задание", "Результат выполнения", "Выводы"],
    "uploaded_at": "2022-06-01T00:00:00Z"
}

@pytest.fixture
def valid_docx():
    title_page = [
        "Тип задания: Лабораторная работа",
        "Студент: Иванов Иван Иванович",
        "Группа: 4931",
        "Предмет: Операционные системы",
        "Название задания: ЛР1. Знакомство с командным интерпретатором bash",
        "Преподаватель: Антохина Юлия Анатольевна",
        "Должность: Ректор, д.т.н., проф.",
        "2022"  # Год
    ]
    body = [
        "Цель",
        "Цель работы...",
        "Задание",
        "Задание...",
        "Результат выполнения",
        "Результаты...",
        "Выводы",
        "Выводы..."
    ]
    return create_test_docx(title_page, body)

def test_valid_report(valid_docx):
    validator = ReportValidator(valid_docx, VALID_STUDENT, VALID_REPORT)
    errors = validator.validate()
    assert len(errors) == 0

def test_missing_student_name():
    title_page = [
        "Тип задания: Лабораторная работа",
        "Группа: 4931",
        "Предмет: Операционные системы"
    ]
    docx_bytes = create_test_docx(title_page, [])
    
    student_info = VALID_STUDENT.copy()
    validator = ReportValidator(docx_bytes, student_info, VALID_REPORT)
    errors = validator.validate()
    
    assert "Не найдено на титульном листе: студент: Иванов Иван Иванович" in errors

def test_incorrect_year():
    title_page = [
        "Тип задания: Лабораторная работа",
        "Студент: Иванов Иван Иванович",
        "Группа: 4931",
        "2023"  # Неправильный год
    ]
    docx_bytes = create_test_docx(title_page, [])
    
    validator = ReportValidator(docx_bytes, VALID_STUDENT, VALID_REPORT)
    errors = validator.validate()
    
    assert "Не найден год выполнения отчета: 2022" in errors

def test_missing_section():
    title_page = ["Тип задания: Лабораторная работа"]
    body = ["Цель", "Задание"]  # Отсутствуют разделы "Результат выполнения" и "Выводы"
    docx_bytes = create_test_docx(title_page, body)
    
    validator = ReportValidator(docx_bytes, VALID_STUDENT, VALID_REPORT)
    errors = validator.validate()
    
    assert "Отсутствует раздел: Результат выполнения" in errors
    assert "Отсутствует раздел: Выводы" in errors

def test_table_content_extraction():
    # 创建包含表格的文档
    doc = Document()
    table = doc.add_table(rows=2, cols=2)
    table.cell(0, 0).text = "Студент"
    table.cell(0, 1).text = "Иванов Иван Иванович"
    table.cell(1, 0).text = "Группа"
    table.cell(1, 1).text = "4931"
    
    # 保存到内存
    stream = BytesIO()
    doc.save(stream)
    docx_bytes = stream.getvalue()
    
    validator = ReportValidator(docx_bytes, VALID_STUDENT, VALID_REPORT)
    validator._extract_document()
    
    assert "Иванов Иван Иванович" in validator.title_page_text
    assert "4931" in validator.title_page_text
