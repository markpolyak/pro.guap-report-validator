import os
import pytest
from backend.report_validator import ReportValidator

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
    
    # 打印详细验证结果
    print("\nValidation results for specific document:")
    if not errors:
        print("✅ All checks passed!")
    else:
        print("❌ Found errors:")
        for error in errors:
            print(f" - {error}")
    
    # 打印提取的文本信息
    print("\nExtracted title page text:")
    print(validator.title_page_text[:500] + "...")  # 只打印前500个字符
    
    print("\nExtracted body text:")
    print(validator.body_text[:500] + "...")  # 只打印前500个字符
    
    # 确保没有错误
    assert len(errors) == 0, f"Found {len(errors)} validation errors"
