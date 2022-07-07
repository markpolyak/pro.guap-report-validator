from unittest import TestCase
from urllib import response
from api.handlers import report_validation
from fastapi.testclient import TestClient
import os
import json

from api.main import api as web_app


class ValidationMultipartEndpointTestCase(TestCase):
    def setUp(self):
        self.client = TestClient(web_app)
        self.report_description = {
            "student": {
                "name": "string",
                "surname": "string",
                "patronymic": "string",
                "group": "string"
            },
            "report": {
                "subject_name": "string",
                "task_name": "string",
                "task_type": "string",
                "teacher": {
                    "name": "string",
                    "surname": "string",
                    "patronymic": "string",
                    "status": "string"
                },
                "report_structure": [
                    "string"
                ],
                "uploaded_at": "2022-06-01T00:00:00Z"
            },
            "report_link": "string"
        }
        self.url_multipart = "http://localhost:8000/api/validation_report_multipart"

    def test_format_doc(self):
        '''status 200 with .doc'''
        filename = "test_doc.doc"
        fpath = f"tests/test_files/{filename}"
        _data = {'report_description': json.dumps(self.report_description)}
        _file = {'file': (filename,  open(fpath, "rb"))}
        response = self.client.post(
            url=self.url_multipart, files=_file, data=_data)
        self.assertEqual(response.status_code, 200)
        response_json = {
            "status": "Успешно",
            "parser": "doc",
            "results": []
        }
        self.assertEqual(response.json(), response_json)

    def test_format_docx(self):
        '''status 200 with .docx'''
        filename = "test_docx.docx"
        fpath = f"tests/test_files/{filename}"
        _data = {'report_description': json.dumps(self.report_description)}
        _file = {'file': (filename,  open(fpath, "rb"))}
        response = self.client.post(
            url=self.url_multipart, files=_file, data=_data)
        self.assertEqual(response.status_code, 200)
        response_json = {
            "status": "Успешно",
            "parser": "docx",
            "results": []
        }
        self.assertEqual(response.json(), response_json)

    def test_format_pdf(self):
        '''status 200 with .pdf'''
        filename = "test_pdf.pdf"
        fpath = f"tests/test_files/{filename}"
        _data = {'report_description': json.dumps(self.report_description)}
        _file = {'file': (filename,  open(fpath, "rb"))}
        response = self.client.post(
            url=self.url_multipart, files=_file, data=_data)
        self.assertEqual(response.status_code, 200)
        response_json = {
            "status": "Успешно",
            "parser": "pdf",
            "results": []
        }
        self.assertEqual(response.json(), response_json)

    def test_format_odt(self):
        '''status 200 with .odt'''
        filename = "test_odt.odt"
        fpath = f"tests/test_files/{filename}"
        _data = {'report_description': json.dumps(self.report_description)}
        _file = {'file': (filename,  open(fpath, "rb"))}
        response = self.client.post(
            url=self.url_multipart, files=_file, data=_data)
        self.assertEqual(response.status_code, 200)
        response_json = {
            "status": "Успешно",
            "parser": "odt",
            "results": []
        }
        self.assertEqual(response.json(), response_json)

    def test_bad_request(self):
        '''status 400 with .pdf, without surname and name type is wrong'''
        filename = "test_pdf.pdf"
        fpath = f"tests/test_files/{filename}"
        _file = {'file': (filename,  open(fpath, "rb"))}
        report_description = self.report_description.copy()
        report_description['student']['name'] = []
        report_description['student'].pop('surname')
        #report_description['report']['uploaded_at'] = "string"
        report_description.pop('report_link')
        _data = {'report_description': json.dumps(report_description)}
        response = self.client.post(
            url=self.url_multipart, files=_file, data=_data)
        self.assertEqual(response.status_code, 400)
        response_json = {
            "status": "error",
            "message": "2 validation errors for Request\nbody -> report_description -> student -> name\n"
                       "  str type expected (type=type_error.str)\n"
                       "body -> report_description -> student -> surname\n"
                       "  field required (type=value_error.missing)",
            "parser": None,
            "results": []
        }
        self.assertEqual(response.json(), response_json)

    def test_bad_request_uploaded_at(self):
        '''status 400 with uploaded_at value is wrong format'''
        filename = "test_pdf.pdf"
        fpath = f"tests/test_files/{filename}"
        _file = {'file': (filename,  open(fpath, "rb"))}
        report_description = self.report_description.copy()
        report_description['report']['uploaded_at'] = "string"
        _data = {'report_description': json.dumps(report_description)}
        response = self.client.post(
            url=self.url_multipart, files=_file, data=_data)
        self.assertEqual(response.status_code, 400)
        response_json = {
            "status": "error",
            "message": "time data 'string' does not match format '%Y-%m-%dT%H:%M:%SZ'",
            "parser": None,
            "results": []
        }
        self.assertEqual(response.json(), response_json)

    def test_validation_format_error(self):
        ''' status 422 wrong file format:
            1) file without format
            2) file with jpg format
        '''
        # test without format
        filename = "test_without_format"
        fpath = f"tests/test_files/{filename}"
        _file = {'file': (filename,  open(fpath, "rb"))}
        _data = {'report_description': json.dumps(self.report_description)}
        response = self.client.post(
            url=self.url_multipart, files=_file, data=_data)
        self.assertEqual(response.status_code, 422)
        response_json = {
            "status": "С ошибками",
            "parser": "",
            "results": [
                "Файл неправильного формата, требуется doc, docx, pdf, odt"
            ]
        }
        self.assertEqual(response.json(), response_json)

        # test jpg
        filename = "test_jpg.jpg"
        fpath = f"tests/test_files/{filename}"
        _file = {'file': (filename,  open(fpath, "rb"))}
        _data = {'report_description': json.dumps(self.report_description)}
        response = self.client.post(
            url=self.url_multipart, files=_file, data=_data)
        self.assertEqual(response.status_code, 422)
        response_json = {
            "status": "С ошибками",
            "parser": "jpg",
            "results": [
                "Файл неправильного формата, требуется doc, docx, pdf, odt"
            ]
        }
        self.assertEqual(response.json(), response_json)
