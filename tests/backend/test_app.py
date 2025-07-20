import pytest
import json
import os
import tempfile
import sys
from docx import Document

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

# 现在可以导入 backend 模块
from backend.app import app
from backend.validator.report_validator import ReportValidator

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"status" in response.data

def test_validate_endpoint(client):
    # 创建测试文件
    _, temp_path = tempfile.mkstemp(suffix='.docx')
    with open(temp_path, 'wb') as f:
        doc = Document()
        doc.add_paragraph("Тестовый документ")
        doc.save(f)
    
    # 准备测试数据
    student_info = {
        "name": "Тест",
        "surname": "Тестов",
        "group": "9999"
    }
    report_info = {
        "subject_name": "Тестовый предмет",
        "task_type": "Тестовая работа",
        "uploaded_at": "2023-01-01T00:00:00Z"
    }
    
    # 发送请求
    with open(temp_path, 'rb') as f:
        response = client.post('/validate', data={
            'file': (f, 'test.docx'),
            'student_info': json.dumps(student_info),
            'report_info': json.dumps(report_info)
        })
    
    # 清理临时文件
    os.unlink(temp_path)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'valid' in data
    assert 'errors' in data
