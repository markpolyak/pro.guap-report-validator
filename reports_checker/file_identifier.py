import binascii
import os
import tempfile

import mimetypes
from typing import Optional, Tuple

import requests
from fastapi import HTTPException


class FileIdentifier:
    FILE_SIGNATURES = {
                          'pdf': ('25504446', 0),  # %PDF
                          'docx': ('504B0304', 0)}

    @classmethod
    def _detect_by_signature(cls, header: bytes, ext: str) -> Optional[str]:
        """
        Определяет тип файла по его сигнатуре (магическому числу).

        :param header: Первые 16 байт файла
        :param ext: Расширение файла из имени
        :return: Определенный тип файла или None, если не удалось определить
        """
        # Проверяем соответствие сигнатуры и расширения
        for file_type, (signature, offset) in cls.FILE_SIGNATURES.items():
            try:
                # Получаем ожидаемую сигнатуру из заголовка
                header_part = header[offset:offset + len(signature) // 2]
                header_hex = binascii.hexlify(header_part).decode('ascii').upper()

                # Сравниваем с известными сигнатурами
                if header_hex.startswith(signature.upper()):
                    # Если расширение соответствует сигнатуре
                    if file_type == ext.lower():
                        return file_type
                    # Если сигнатура соответствует, но расширение другое
                    return f"{file_type} (but has .{ext} extension)"
            except (IndexError, binascii.Error):
                continue

        return None
    def identify_file(file_path: str) -> Tuple[str, str]:
        """Определяет формат файла по расширению и сигнатуре"""
        ext = os.path.splitext(file_path)[1].lower()

        with open(file_path, 'rb') as f:
            header = f.read(256)

        # Проверка сигнатуры файла
        file_type = FileIdentifier._detect_by_signature(header, 'pdf')

        # Сопоставление с форматами
        if 'pdf' in file_type:
            return "pdf", file_type
        elif file_type == "application/vnd.oasis.opendocument.text":
            return "odt", file_type
        elif file_type in ("application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                           "application/msword"):
            return "docx", file_type
        else:
            raise HTTPException(
                status_code=415,
                detail=f"Unsupported file format. Detected: {file_type}"
            )

    @staticmethod
    def safe_identify(upload_file) -> Tuple[str, str]:
        """Безопасное определение с сохранением временного файла"""
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(upload_file.file.read())
            tmp_path = tmp.name

        try:
            return FileIdentifier.identify_file(tmp_path)
        finally:
            os.unlink(tmp_path)


    @staticmethod
    def safe_identify_from_url(url: str) -> Tuple[str, str]:
        """Безопасное определение формата файла по URL с загрузкой во временный файл"""

        try:
            # Скачиваем файл
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Проверяем статус ответа

            # Создаем временный файл
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # фильтруем keep-alive chunks
                        tmp_file.write(chunk)
                tmp_path = tmp_file.name

            # Определяем тип файла
            return FileIdentifier.identify_file(tmp_path)

        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=400,
                detail=f"Ошибка загрузки файла по URL: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Ошибка при обработке файла: {str(e)}"
            )
        finally:
            # Удаляем временный файл, если он был создан
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except:
                    pass  # Игнорируем ошибки удаления временного файла