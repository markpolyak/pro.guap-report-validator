import os
import sys
import tempfile

import requests

import uvicorn
from typing import List, Optional, Annotated
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status

from Хуань.reports_checker.checkers.docx_checker import DOCXChecker
from slowapi import Limiter
from Хуань.reports_checker.checkers.odt_checker import ODTChecker
from Хуань.reports_checker.checkers.pdf_checker import PDFChecker
from Хуань.reports_checker.file_identifier import FileIdentifier
from slowapi.util import get_remote_address
from Хуань.reports_checker.models import StatusEnum, Response, ReportUploadDataWithReportLink, ReportUploadData

app = FastAPI(title='Проверка отчетов',
              docs_url='/docs',
              version="1.0",
              servers="",
              openapi_url="/api/v1/сheck_reports_api.json",
              redoc_url='/redoc')

limiter = Limiter(key_func=get_remote_address, enabled=False)

def is_rate_limit_enabled():
    # Здесь можно проверить флаг из аргументов CLI, переменных окружения и т.д.
    # Например, если при запуске сервера передан ключ активации
    return limiter.enabled

@app.post('/upload-report/',
          status_code=status.HTTP_200_OK,
          response_model=Response
          )
def upload_report(
        description: ReportUploadData,
        report_file: UploadFile = File(..., description="Двоичный файл отчёта")
):
    file_type, mime = FileIdentifier.safe_identify(report_file)

    checkers = {
        "pdf": PDFChecker,
        "docx": DOCXChecker,
        "odt": ODTChecker
    }

    checker = checkers.get(file_type)
    if not checker:
        raise HTTPException(400, "Unsupported file type")

    # В реальной реализации нужно сохранить файл временно
    result = checker.check_report(report_file.filename)

    return Response(status=StatusEnum.SUCCESS if result.is_valid else StatusEnum.HAS_ERRORS,
                    parser=mime,
                    results=[*result.error_message])


@app.post('/upload-report-link/',
          status_code=status.HTTP_200_OK,
          response_model=Response
          )
def upload_report(description: ReportUploadDataWithReportLink):
    file_type, mime = FileIdentifier.safe_identify_from_url(description.report_link)

    checkers = {
        "pdf": PDFChecker,
        "docx": DOCXChecker,
        "odt": ODTChecker
    }

    checker = checkers.get(file_type)
    if not checker:
        raise HTTPException(400, "Unsupported file type")

    response = requests.get(description.report_link, stream=True)
    response.raise_for_status()  # Проверяем статус ответа

    # Создаем временный файл
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:  # фильтруем keep-alive chunks
                tmp_file.write(chunk)
        tmp_path = tmp_file.name
    result = checker.check_report(tmp_path)

    if 'tmp_path' in locals() and os.path.exists(tmp_path):
        try:
            os.unlink(tmp_path)
        except:
            pass  # Игнорируем ошибки удаления временного файла

    if result.is_valid == StatusEnum.HAS_ERRORS:
        return {'status': StatusEnum.HAS_ERRORS,
                'parser': mime,
                'message': 'описание ошибки',
                'resulrs': [*result.issues]
                }

    return Response(status=StatusEnum.SUCCESS if result.is_valid else StatusEnum.HAS_ERRORS,
                    parser=mime,
                    results=[*result.issues])

RATE_LIMIT_KEY = "SECRET_KEY"  # Замените на ваш ключ активации

def enable_rate_limit(activation_key: str):
    if activation_key == RATE_LIMIT_KEY:
        limiter.enabled = True


if __name__=='__main__':
    rate_limit_key = None
    if "--rate-limit-key" in sys.argv:
        index = sys.argv.index("--rate-limit-key")
        rate_limit_key = sys.argv[index + 1]

    if rate_limit_key:
        enable_rate_limit(rate_limit_key)
    uvicorn.run(app, host='127.0.0.1', port=8000)
