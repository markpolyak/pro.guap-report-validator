import sys
import os
import json
import pytest
from docx import Document
from io import BytesIO
from backend.app import app

# 修复导入路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def load_test_docx(file_path):
    """从文件中加载 DOCX 并返回 BytesIO 对象"""
    with open(file_path, 'rb') as docx_file:
        return BytesIO(docx_file.read())

def test_valid_report(client):
    # 加载测试文档
    buffer = load_test_docx('tests/backend/valid_report.docx')

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

    # 发送请求
    response = client.post(
        '/validate',
        data={
            'student_info': json.dumps(student_info),
            'report_info': json.dumps(report_info),
            'file': (buffer, 'valid_report.docx')
        },
    )

    # 断言响应
    assert response.status_code == 200
    errors = json.loads(response.data)
    assert len(errors) == 0
