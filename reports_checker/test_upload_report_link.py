import json
from fastapi import status

from Хуань.reports_checker.models import ReportUploadDataWithReportLink, StatusEnum

import pytest
from fastapi.testclient import TestClient
from Хуань.reports_checker.main import app  # Импортируем ваше FastAPI приложение
import tempfile
import os

from Хуань.reports_checker.checkers.pdf_checker import PDFCheckResult


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_pdf():
    # Создаем временный PDF файл для тестов
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(b'%PDF-1.4 fake pdf content')
    yield f.name
    os.unlink(f.name)


def test_upload_pdf_report(client, sample_pdf):
    """Тест успешной обработки PDF отчета"""
    test_data = {
        "student": {
            "name": "Иван",
            "surname": "Иванов",
            "patronymic": "Иванович",
            "group": "4931"
        },
        "report": {
            "subject_name": "Операционные системы",
            "task_name": "ЛР1",
            "task_type": "Лабораторная работа",
            "teacher": {
                "name": "Марк",
                "surname": "Поляк",
                "patronymic": "Дмитриевич"
            },
            "report_structure": ["Цель", "Задание"],
            "uploaded_at": "2022-06-01T00:00:00Z"
        },
        "report_link": f"https://docs.google.com/uc?export=download&id=1eC_2x2MPafHuKM8oiOehm0CY7NveCum1"  # Используем локальный файл
    }

    response = client.post(
        "/upload-report-link/",
        json=test_data
    )

    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.json()["status"] == StatusEnum.SUCCESS
    assert response.json()["parser"] == "pdf"
    assert isinstance(response.json()["results"], list)


def test_invalid_url(client):  # works
    """Тест обработки невалидного URL"""
    test_data = {
        "student": {
            "name": "Иван",
            "surname": "Иванов",
            "patronymic": "Иванович",
            "group": "4931"
        },
        "report": {
            "subject_name": "Операционные системы",
            "task_name": "ЛР1",
            "task_type": "Лабораторная работа",
            "teacher": {
                "name": "Юлия",
                "surname": "Антохина",
                "patronymic": "Анатольевна"
            },
            "report_structure": ["Цель", "Задание"],
            "uploaded_at": "2022-06-01T00:00:00Z"
        },
        "report_link": "https://docs.google.com/uc?export=download&id=1eC_2x2MPafHuKM8oiOehm0CY7NveCum1fdgsdf"
    }


    response = client.post(
        "/upload-report-link/",
        json=test_data
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
