from unittest import TestCase
from fastapi.testclient import TestClient
import getpass
import requests
from requests.adapters import HTTPAdapter, Retry
from api.main import api as web_app


class ValidationEndpointTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        '''use once'''
        super(ValidationEndpointTestCase, cls).setUpClass()
        cls._authorization()

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
            "report_link": "string",
            "username": self.username,
            "password": self.password
        }
        self.url = "http://localhost:8000/api/validation_report"

    @classmethod
    def _requests_retry_session(cls,
                                retries=3,
                                backoff_factor=0.3,
                                status_forcelist=(500, 502, 504),
                                session=None
                                ):
        session = session or requests.Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    @classmethod
    def input_credentials(cls):
        cls.username = input('\nEnter your username: ')
        cls.password = getpass.getpass(prompt='Enter your password: ')

    @classmethod
    def _authorization(cls):
        while True:
            cls.input_credentials()
            session = requests.Session()
            url_form_authorization = 'https://pro.guap.ru/user/login'
            url_authorization = 'https://pro.guap.ru/user/login_check'
            res = session.get(url_form_authorization)
            if res.status_code == 200:
                res = session.post(
                    url_authorization,
                    data={'_username': cls.username,
                          '_password': cls.password}
                )
                if res.url != 'https://pro.guap.ru/inside_s':
                    print('\nНеправильно введены username или password!\n')
                else:
                    print('\nУспешная авторизация\n')
                    break

    def test_format_doc(self):
        '''status 200 with .doc'''
        self.report_description['report_link'] = input(
            'Enter a link to the report in doc format: ')
        response = self.client.post(
            url=self.url, json=self.report_description)
        self.assertEqual(response.status_code, 200)
        response_json = {
            "status": "Успешно",
            "parser": "doc",
            "results": []
        }
        self.assertEqual(response.json(), response_json)

    def test_format_docx(self):
        '''status 200 with .docx'''
        self.report_description['report_link'] = input(
            'Enter a link to the report in docx format: ')
        response = self.client.post(
            url=self.url, json=self.report_description)
        self.assertEqual(response.status_code, 200)
        response_json = {
            "status": "Успешно",
            "parser": "docx",
            "results": []
        }
        self.assertEqual(response.json(), response_json)

    def test_format_pdf(self):
        '''status 200 with .pdf'''
        self.report_description['report_link'] = input(
            'Enter a link to the report in pdf format: ')
        response = self.client.post(
            url=self.url, json=self.report_description)
        self.assertEqual(response.status_code, 200)
        response_json = {
            "status": "Успешно",
            "parser": "pdf",
            "results": []
        }
        self.assertEqual(response.json(), response_json)

    def test_format_odt(self):
        '''status 200 with .odt'''
        self.report_description['report_link'] = input(
            'Enter a link to the report in odt format: ')
        response = self.client.post(
            url=self.url, json=self.report_description)
        self.assertEqual(response.status_code, 200)
        response_json = {
            "status": "Успешно",
            "parser": "odt",
            "results": []
        }
        self.assertEqual(response.json(), response_json)

    def test_bad_request(self):
        '''status 400 without name'''
        self.report_description['student'].pop('name')
        response = self.client.post(
            url=self.url, json=self.report_description)

        self.assertEqual(response.status_code, 400)
        response_json = {
            "status": "error",
            "message": "1 validation error for Request\nbody -> student -> name\n  field required (type=value_error.missing)",
            "parser": None,
            "results": []
        }
        self.assertEqual(response.json(), response_json)
