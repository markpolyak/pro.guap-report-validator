import sys
import os
import json
import pytest
from unittest.mock import patch, MagicMock
from docx import Document
from io import BytesIO

# 修复导入路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def create_test_docx(content):
    """创建测试DOCX文件"""
    doc = Document()
    for line in content.split('\n'):
        if line.strip():
            doc.add_paragraph(line.strip())
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

def test_valid_report(client):
    content = """
    МИНИСТЕРСТВО НАУКИ И ВЫСШЕГО ОБРАЗОВАНИЯ РОССИЙСКОЙ ФЕДЕРАЦИИ
    Санкт-Петербургский государственный университет аэрокосмического приборостроения
    Кафедра №43
    Отчет по лабораторной работе №1
    Студент: Иванов Иван Иванович Группа: 4931
    Преподаватель: Антохина Юлия Анатольевна
    Должность: Ректор, д.т.н., проф.
    Цель работы: Изучение программирования
    Задание: Реализовать алгоритм
    Результат: Успешно
    Выводы: Задание выполнено
    Санкт-Петербург 2022
    """

    # 准备表单数据
    student_info = {
        "name": "Иван",
        "surname": "Иванов",
        "patronymic": "Иванович",
        "group": "4931"
    }

    report_info = {
        "subject_name": "Операционные системы",
        "task_name": "ЛР1. Знакомство с командным интерпретатором bash",
        "task_type": "Лабораторная работа",
        "teacher": {
            "name": "Юлия",
            "surname": "Антохина",
            "patronymic": "Анатольевна",
            "status": "Ректор, д.т.н., проф."
        },
        "report_structure": ["Цель", "Задание", "Результат", "Выводы"],
        "uploaded_at": "2022-06-01T00:00:00Z"
    }

    # 发送请求 - 仅通过 input_stream 上传文件，表单数据需要传递给表单字段
    buffer = create_test_docx(content)
    data = {
        'student_info': json.dumps(student_info),
        'report_info': json.dumps(report_info),
    }

    response = client.post(
    '/validate',
    data={
        'student_info': json.dumps(student_info),
        'report_info': json.dumps(report_info),
    },
    files={'file': (buffer, 'test.docx')},  # 在这里上传文件
    content_type='multipart/form-data',
)


    assert response.status_code == 200
    errors = json.loads(response.data)
    assert len(errors) == 0



def test_missing_sections(client):
    # 创建测试文档（缺少"Выводы"章节）
    content = """
    МИНИСТЕРСТВО НАУКИ И ВЫСШЕГО ОБРАЗОВАНИЯ РОССИЙСКОЙ ФЕДЕРАЦИИ
    Санкт-Петербургский государственный университет аэрокосмического приборостроения
    Кафедра №43
    Отчет по лабораторной работе №1
    Студент: Иванов Иван Иванович Группа: 4931
    Преподаватель: Антохина Юлия Анатольевна
    Должность: Ректор, д.т.н., проф.
    Цель работы: Изучение программирования
    Задание: Реализовать алгоритм
    Результат: Успешно
    Санкт-Петербург 2022
    """
    
    # 准备表单数据
    student_info = {
        "name": "Иван",
        "surname": "Иванов",
        "patronymic": "Иванович",
        "group": "4931"
    }
    
    report_info = {
        "subject_name": "Операционные системы",
        "task_name": "ЛР1. Знакомство с командным интерпретатором bash",
        "task_type": "Лабораторная работа",
        "teacher": {
            "name": "Юлия",
            "surname": "Антохина",
            "patronymic": "Анатольевна",
            "status": "Ректор, д.т.н., проф."
        },
        "report_structure": ["Цель", "Задание", "Результат", "Выводы"],
        "uploaded_at": "2022-06-01T00:00:00Z"
    }
    
    # 发送请求 - 修复后的方式
    buffer = create_test_docx(content)
    data = {
        'student_info': json.dumps(student_info),
        'report_info': json.dumps(report_info),
    }
    response = client.post(
    '/validate',
    data={
        'student_info': json.dumps(student_info),
        'report_info': json.dumps(report_info),
    },
    files={'file': (buffer, 'test.docx')},  # 在这里上传文件
    content_type='multipart/form-data',
)

    
    assert response.status_code == 200
    errors = json.loads(response.data)
    assert "Отсутствует раздел: Выводы" in errors

def test_wrong_title(client):
    # 创建测试文档（标题页缺少组别和年份）
    content = """
    МИНИСТЕРСТВО НАУКИ И ВЫСШЕГО ОБРАЗОВАНИЯ РОССИЙСКОЙ ФЕДЕРАЦИИ
    Санкт-Петербургский государственный университет аэрокосмического приборостроения
    Кафедра №43
    Отчет по лабораторной работе №1
    Студент: Иванов Иван Иванович
    Преподаватель: Антохина Юлия Анатольевна
    Должность: Ректор, д.т.н., проф.
    Цель работы: Изучение программирования
    Задание: Реализовать алгоритм
    Результат: Успешно
    Выводы: Задание выполнено
    Санкт-Петербург
    """
    
    # 准备表单数据
    student_info = {
        "name": "Иван",
        "surname": "Иванов",
        "patronymic": "Иванович",
        "group": "4931"
    }
    
    report_info = {
        "subject_name": "Операционные системы",
        "task_name": "ЛР1. Знакомство с командным интерпретатором bash",
        "task_type": "Лабораторная работа",
        "teacher": {
            "name": "Юлия",
            "surname": "Антохина",
            "patronymic": "Анатольевна",
            "status": "Ректор, д.т.н., проф."
        },
        "report_structure": ["Цель", "Задание", "Результат", "Выводы"],
        "uploaded_at": "2022-06-01T00:00:00Z"
    }
    
    # 发送请求 - 修复后的方式
    buffer = create_test_docx(content)
    data = {
        'student_info': json.dumps(student_info),
        'report_info': json.dumps(report_info),
    }
    response = client.post(
    '/validate',
    data={
        'student_info': json.dumps(student_info),
        'report_info': json.dumps(report_info),
    },
    files={'file': (buffer, 'test.docx')},  # 在这里上传文件
    content_type='multipart/form-data',
)

    
    assert response.status_code == 200
    errors = json.loads(response.data)
    assert "Не найдено: группа студента" in errors
    assert "Не найдено: год выполнения отчета" in errors
