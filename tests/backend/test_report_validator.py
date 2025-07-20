import os
import pytest
import sys
from io import BytesIO
from docx import Document

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

# 现在可以导入 backend 模块
from backend.validator.report_validator import ReportValidator

# 测试文档路径
SPECIFIC_DOCX_PATH = os.path.join(os.path.dirname(__file__), "4233K_цзя хао_ЛР1.docx")

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

@pytest.mark.skipif(
    not os.path.exists(SPECIFIC_DOCX_PATH),
    reason="Specific test document not found"
)
def test_specific_document():
    # 读取文档内容
    with open(SPECIFIC_DOCX_PATH, "rb") as f:
        docx_bytes = f.read()
    
    # 创建验证器
    validator = ReportValidator(docx_bytes, STUDENT_INFO, REPORT_INFO)
    errors = validator.validate()
    
    # 确保没有错误
    assert len(errors) == 0, f"Found {len(errors)} validation errors: {errors}"

# 添加一个简单的测试用例作为后备
def test_empty_document():
    """测试空文档处理"""
    doc = Document()
    stream = BytesIO()
    doc.save(stream)
    docx_bytes = stream.getvalue()
    
    validator = ReportValidator(docx_bytes, STUDENT_INFO, REPORT_INFO)
    errors = validator.validate()
    
    assert "Документ пуст" in errors
