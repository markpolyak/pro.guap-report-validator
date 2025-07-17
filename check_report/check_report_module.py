import io
import os
import json
import argparse

from datetime import datetime

from odf import opendocument
from odf.element import Element


STUDENT_JSON = {
    "name": "str",
    "surname": "str",
    "patronymic": "str | None",
    "group": "str"
}


REPORT_JSON = {
    "subject_name": "str",
    "task_name": "str",
    "task_type": "str",
    "teacher": {
        "name": "str",
        "surname": "str",
        "patronymic": "str | None",
        "status": "str"
    },
    "report_structure": [
        "str", "str", "str", "str"
    ],
    "uploaded_at": "str (ISO 8601 UTC)"
}


def remove_file_if_exists(file_path: str) -> None:
    if os.path.exists(file_path):
        os.remove(file_path)


def write_document_struct(element: Element, level=0) -> None:
    with open(file='../document_structure.txt', mode='a', encoding='utf-8') as file:
        file.write('  ' * level + f"{element.tagName}\n")

    for child in element.childNodes:
        if isinstance(child, Element):
            write_document_struct(child, level + 1)


def detect_task_type(content: str, task_type: str) -> dict:
    temp = ''

    if 'лабораторн' in content:
        temp = 'Лабораторная работа'
    elif 'курсов' in content:
        temp = 'Курсовая работа'
    elif 'контрольн' in content:
        temp = 'Контрольная работа'
    elif 'реферат' in content:
        temp = 'Реферат'

    if temp == task_type:
        return {"success": True, "data": temp}
    else:
        return {"success": False, "error": "Неверный тип задания"}


def detect_full_name_teacher(content: str, report_json: dict) -> dict:
    name_initial = report_json.get('teacher').get('name')[0] + '.'

    patronymic_initial = report_json.get('teacher').get('patronymic', '')[0] + '.' \
        if report_json.get('teacher').get('patronymic') else ''

    surname = report_json.get('teacher').get('surname')

    teacher_full_name = name_initial + patronymic_initial + surname

    if teacher_full_name.lower() in content:
        return {"success": True, "data": teacher_full_name}
    else:
        return {"success": False, "error": "Неверное ФИО преподавателя"}


def detect_full_name_student(content: str, student_json: dict) -> dict:
    name_initial = student_json.get('name')[0] + '.'

    patronymic_initial = student_json.get('patronymic', '')[0] + '.' if student_json.get('patronymic') else ''

    surname = student_json.get('surname')

    student_full_name = name_initial + patronymic_initial + surname

    if student_full_name.lower() in content:
        return {"success": True, "data": student_full_name}
    else:
        return {"success": False, "error": "Неверное ФИО студента"}



def detect_subject_name(content: str, subject_name: str) -> dict:
    if subject_name.replace(' ', '').lower() in content:
        return {"success": True, "data": subject_name}
    else:
        return {"success": False, "error": "Неверное название предмета"}


def detect_task_name(content: str, task_name: str) -> dict:
    if task_name.strip('ЛР1234567890.').replace(' ', '').lower() in content:
        return {"success": True, "data": task_name}
    else:
        return {"success": False, "error": "Неверное название работы"}


def detect_group(content: str, group: str) -> dict:
    if group.replace(' ', '').lower() in content:
        return {"success": True, "data": group}
    else:
        return {"success": False, "error": "Неверная группа"}


def detect_status(content: str, status: str) -> dict:
    if status.replace(' ', '').lower() in content:
        return {"success": True, "data": status}
    else:
        return {"success": False, "error": "Неверная должность преподавателя"}


def detect_report_structure(content: str, report_structure: list) -> dict:
    missing_points = []

    for point in report_structure:
        if point.replace(' ', '').lower() not in content:
            missing_points.append(point)

    if not missing_points:
        return {"success": True, "data": ', '.join(report_structure)}
    else:
        missing_points_str = ', '.join(missing_points)
        return {"success": False, "error": f"Отсутствуют пункты: {missing_points_str}"}


def detect_uploaded_at(content: str, date: str) -> dict:
    date = datetime.fromisoformat(date.replace("Z", "+00:00"))

    if str(date.year) in content:
        return {"success": True, "data": str(date.date())}
    else:
        return {"success": False, "error": 'Неверная дата'}


def get_keys_json(info_json: dict) -> list[str]:
    keys = []

    for key, value in info_json.items():
        keys.append(key)
        if isinstance(value, dict):
            keys.extend(get_keys_json(value))

    return keys


def detect_json(required_json: dict, input_json: dict) -> set[str]:
    required_keys = set(get_keys_json(required_json))
    input_keys = set(get_keys_json(input_json))

    required_keys.discard('patronymic')
    input_keys.discard('patronymic')

    return required_keys.difference(input_keys)


def check_report(report_odt: bytes, student_json: dict, report_json: dict) -> list[str]:

    """
    Проверка документа OpenOffice .odt

    :param report_odt: File with a report in the form of a byte stream

    :param student_json: {
        name: str,
        surname: str,
        patronymic: str | None,
        group: str
     }

    :param report_json: {
        subject_name: str,
        task_name: str,
        task_type: str,
        teacher: {
            name: str,
            surname: str,
            patronymic: str | None,
            status: str
        },
        report_structure: list[str],
        uploaded_at: str (ISO 8601 UTC)
     }

    :return: List of errors
    """

    missing_student_keys = detect_json(STUDENT_JSON, student_json)
    missing_report_keys = detect_json(REPORT_JSON, report_json)
    # If the necessary keys are missing, the program shuts down
    if missing_student_keys:
        return [f'Отсутствие обязательных ключей в student_json: {", ".join(missing_student_keys)}']
    if missing_report_keys:
        return [f'Отсутствие обязательных ключей в report_json: {", ".join(missing_report_keys)}']

    stream = io.BytesIO(report_odt)
    document = opendocument.load(stream).body
    remove_file_if_exists('../document_structure.txt')
    write_document_struct(document)  # <office:body>...</office:body>
    """
       <office:body>        
           <office:text>                          # childNodes[0]
               <text:h>...</text:h>
               <text:p>...</text:p>
           </office:text>
       </office:body>
    """
    content = [str(element) for element in document.childNodes[0].childNodes if str(element) != '']
    content = content[0].replace(' ', '').lower()

    status = detect_status(content, report_json.get("teacher").get("status"))
    t_f_n = detect_full_name_teacher(content, report_json)
    task_type = detect_task_type(content, report_json.get("task_type"))
    task_name = detect_task_name(content, report_json.get("task_name"))
    subject_name = detect_subject_name(content, report_json.get("subject_name"))
    group = detect_group(content, student_json.get("group"))
    s_f_n = detect_full_name_student(content, student_json)
    report_structure = detect_report_structure(content, report_json.get("report_structure"))
    uploaded_at = detect_uploaded_at(content, report_json.get("uploaded_at"))

    print(f'Должность преподавателя: {status.get("data")}' if status.get("success")
          else "\n\tERROR: " + status.get("error") + "\n")
    print(f'ФИО преподавателя: {t_f_n.get("data")}' if t_f_n.get("success")
          else "\n\tERROR: " + t_f_n.get("error") + "\n")
    print(f'Тип отчета: {task_type.get("data")}' if task_type.get("success")
          else "\n\tERROR: " + task_type.get("error") + "\n")
    print(f'Название работы: {task_name.get("data")}' if task_name.get("success")
          else "\n\tERROR: " + task_name.get("error") + "\n")
    print(f'Название предмета: {subject_name.get("data")}' if subject_name.get("success")
          else "\n\tERROR: " + subject_name.get("error") + "\n")
    print(f'Номер группы: {group.get("data")}' if group.get("success")
          else "\n\tERROR: " + group.get("error") + "\n")
    print(f'ФИО студента: {s_f_n.get("data")}' if s_f_n.get("success")
          else "\n\tERROR: " + s_f_n.get("error") + "\n")
    print(f'Стуктура отчета: {report_structure.get("data")}' if report_structure.get("success")
          else "\n\tERROR: " + report_structure.get("error") + "\n")
    print(f'Дата загрузки: {uploaded_at.get("data")}' if uploaded_at.get("success")
          else "\n\tERROR: " + uploaded_at.get("error") + "\n")

    response_data = [status, t_f_n, task_type, task_name, subject_name, group, s_f_n, report_structure, uploaded_at]
    errors = [elem.get("error") for elem in response_data if not elem.get("success")]

    return errors


def main():
    cur_dir = os.path.dirname(__file__)
    report_odt_def_path = os.path.join(cur_dir, '..', 'data', 'correct_lab.odt')
    student_json_def_path = os.path.join(cur_dir, '..', 'data', 'student_info.json')
    report_json_def_path = os.path.join(cur_dir, '..', 'data', 'report_info.json')

    report_odt_def_path = os.path.abspath(report_odt_def_path)
    student_json_def_path = os.path.abspath(student_json_def_path)
    report_json_def_path = os.path.abspath(report_json_def_path)

    parser = argparse.ArgumentParser(description='Модуль проверки отчетов в формате OpenOffice')
    parser.add_argument('--report_odt', default=report_odt_def_path, help='Путь к файлу отчета .odt')
    parser.add_argument('--student_json', default=student_json_def_path, help='Путь к файлу с информацией о студенте .json')
    parser.add_argument('--report_json', default=report_json_def_path, help='Путь к файлу с информацией об отчете .json')

    args = parser.parse_args()

    with open(file=args.report_odt, mode='rb') as report_data_odt:
        report_odt = report_data_odt.read()

    with open(file=args.student_json, mode='r', encoding='utf-8') as student_data_json:
        student_json = json.load(student_data_json)

    with open(file=args.report_json, mode='r', encoding='utf-8') as report_data_json:
        report_json = json.load(report_data_json)

    errors = check_report(report_odt, student_json, report_json)


if __name__ == '__main__':
    main()
