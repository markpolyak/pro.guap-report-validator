from asyncio.log import logger
from base64 import encode
from distutils.log import error
from email import message
import pathlib
import requests
import shutil
import re
from requests.adapters import HTTPAdapter, Retry
from pathlib import Path


class ValidatorReports:
    def __init__(self, report_description, filename, file):
        self.report_description = report_description
        self.filename = filename
        self.format_file = self._determine_file_format()
        self.file = file

    def validation_report(self):
        validation_response = self._choice_report_validation()
        return validation_response

    def save_report(self, file):
        try:
            open(self.filename, 'wb').write(file)
            '''
            with open(self.filename, 'wb') as buffer:
                shutil.copyfileobj(file, buffer)
                '''

        except IOError as e:
            logger.error('Error save report: ' + str(e))

    def _determine_file_format(self):
        format_file = Path(self.filename).suffix
        # delete '.'
        format_file = format_file.lstrip('.')
        return format_file

    # change plugs
    def _report_validation_word(self):
        return []

    def _report_validation_odt(self):
        return []

    def _report_validation_pdf(self):
        return []

    def _choice_report_validation(self):
        if self.format_file == 'doc' or self.format_file == 'docx':
            return self._report_validation_word()
        elif self.format_file == 'pdf':
            return self._report_validation_pdf()
        elif self.format_file == 'odt':
            return self._report_validation_odt()
        else:
            return ["Файл неправильного формата, требуется doc, docx, pdf, odt"]


class FileUploader:
    def __init__(self, file_link, username, password):
        self.file_link = self._make_url_to_file(file_link)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) "
            "Gecko/20100101 Firefox/66.0",
            "Accept-Encoding": "*",
            "Connection": "keep-alive"
        }
        self.username = username
        self.password = password

    def _make_url_to_file(self, file_link):
        host = 'https://pro.guap.ru'
        if file_link.find(host, 0, len(host)) == -1:
            file_link = host + file_link
        return file_link

    # copyright markpolyak
    def _requests_retry_session(self,
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

    def _get_filename_from_cd(self, cd):
        # Get filename from content-disposition
        if not cd:
            return None
        fname = re.findall('filename=(.+)', cd)
        if len(fname) == 0:
            return None
        file_name = fname[0].replace('"', '')
        return file_name

    def upload_file(self):
        session = self._requests_retry_session()
        url_form_authorization = 'https://pro.guap.ru/user/login'
        url_authorization = 'https://pro.guap.ru/user/login_check'
        res = session.get(url_form_authorization,
                          headers=self.headers)
        message = ''
        filename = ''
        if res.status_code == 200:
            res = session.post(
                url_authorization,
                data={'_username': self.username, '_password': self.password},
                headers=self.headers
            )
            if res.url == 'https://pro.guap.ru/inside_s':
                res = session.get(
                    self.file_link, headers=self.headers)
                if res.status_code == 200 and res.url == self.file_link:
                    # translation of the header into the desired encoding
                    if res.content[1:5] != b'html':
                        filename = self._get_filename_from_cd(
                            res.headers.get('content-disposition').encode('ISO-8859-1').decode('UTF-8'))
                    else:
                        res.status_code = 400
                        message = f'Не удалось скачать документ с {self.file_link}'
                elif res.status_code == 200 and res.url != self.file_link:
                    res.status_code = 403
                    message = f'Не удалось скачать документ с {self.file_link}, нет прав'
                else:
                    message = f'Не удалось скачать документ с {self.file_link}'
            else:
                res.status_code = 401
                message = f'Не удалось авторизироваться на {url_authorization}'
        else:
            message = f'Не удалось получить форму авторизации с {url_form_authorization}'
        return {'filename': filename, 'file_binary': res.content, 'status_code': res.status_code, 'message': message}
