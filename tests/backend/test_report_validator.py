import os
import pytest
from docx import Document
from io import BytesIO

# 学生信息
STUDENT_INFO = {
    "name": "хао",
    "surname": "Цзя",
    "patronymic": "",
    "group": "4233k"
}

# 报告信息
REPORT_INFO = {
    "subject_name": "Основы программирования",
    "task_name": "Практическое задание №1",
    "task_type": "Практическое задание",
    "teacher": {
        "name": "Елена",
        "surname": "Шумова",
        "patronymic": "Олеговна",
        "status": "ПРЕПОДАВАТЕЛЬ"
    },
    "report_structure": ["Выход"],
    "uploaded_at": "2025-01-01T00:00:00Z"
}

@pytest.fixture
def specific_document_bytes():
    """返回特定文档的字节内容"""
    doc_path = os.path.join(os.path.dirname(__file__), "4233K_цзя хао_ЛР1.docx")
    if not os.path.exists(doc_path):
        pytest.skip(f"Specific document not found: {doc_path}")
    
    with open(doc_path, "rb") as f:
        return f.read()

def test_specific_document(specific_document_bytes):
    """测试特定文档的验证"""
    # 创建验证器 - 这里需要您实际实现的验证器类
    # 由于不依赖 backend 模块，您需要在这里实现一个简化版的验证器
    # 或者跳过验证器的创建，直接检查文档内容
    from validator import ReportValidator  # 假设有独立的验证器模块
    
    validator = ReportValidator(specific_document_bytes, STUDENT_INFO, REPORT_INFO)
    errors = validator.validate()
    
    # 确保没有错误
    assert len(errors) == 0, f"Found {len(errors)} validation errors: {errors}"

def test_document_has_required_sections(specific_document_bytes):
    """测试文档包含必要的章节"""
    # 检查文档是否包含必要的章节
    doc = Document(BytesIO(specific_document_bytes))
    full_text = "\n".join(para.text for para in doc.paragraphs)
    
    # 检查必要的章节
    required_sections = ["Выход"]
    for section in required_sections:
        assert section in full_text, f"Required section '{section}' not found in document"

def test_document_has_title_page_info(specific_document_bytes):
    """测试文档标题页包含必要信息"""
    doc = Document(BytesIO(specific_document_bytes))
    full_text = "\n".join(para.text for para in doc.paragraphs)
    
    # 检查必要的信息
    required_info = [
        "Цзя хао",
        "4233k",
        "Основы программирования",
        "Практическое задание №1",
        "Шумова Елена Олеговна",
        "2025"
    ]
    
    for info in required_info:
        assert info in full_text, f"Required info '{info}' not found in document title page"
