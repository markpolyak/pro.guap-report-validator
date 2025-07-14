import pytest
import os
import copy

from check_report.check_report_module import check_report


student_json = {
    "name": "Владимир",
    "surname": "Иванов",
    "patronymic": "Петрович",
    "group": "4133К"
}

report_json = {
  "subject_name": "Операционные системы",
  "task_name": "ЛР1. Знакомство с командным интерпретатором bash",
  "task_type": "Лабораторная работа",
  "teacher": {
    "name": "Марк",
    "surname": "Поляк",
    "patronymic": "Дмитриевич",
    "status": "Старший преподаватель"
  },
  "report_structure": [
    "Цель", "Задание", "Результат выполнения", "Выводы"
  ],
  "uploaded_at": "2024-06-01T00:00:00Z"
}


cur_dir = os.path.dirname(__file__)
report_odt_def_path = os.path.join(cur_dir, '..', 'data', 'correct_lab.odt')
report_odt_def_path = os.path.abspath(report_odt_def_path)


with open(file=report_odt_def_path, mode='rb') as report_data_odt:
    report_odt = report_data_odt.read()


def test_correct_report():
    errors = check_report(report_odt, student_json, report_json)
    assert len(errors) == 0


def test_missing_student_keys():
    student_keys_error = student_json.copy()
    student_keys_error.pop('surname', None)
    errors = check_report(report_odt, student_keys_error, report_json)
    assert "Отсутствие обязательных ключей в student_json: surname" in errors and len(errors) == 1


def test_missing_report_keys():
    report_keys_error = copy.deepcopy(report_json)
    report_keys_error['teacher'].pop('surname', None)
    errors = check_report(report_odt, student_json, report_keys_error)
    assert "Отсутствие обязательных ключей в report_json: surname" in errors and len(errors) == 1


def test_incorrect_student_group():
    student_group_error = student_json.copy()
    student_group_error['group'] = '1111K'
    errors = check_report(report_odt, student_group_error, report_json)
    assert "Неверная группа" in errors and len(errors) == 1


def test_incorrect_teacher_status():
    teacher_status_error = copy.deepcopy(report_json)
    teacher_status_error['teacher']['status'] = 'Директор'
    errors = check_report(report_odt, student_json, teacher_status_error)
    assert "Неверная должность преподавателя" in errors and len(errors) == 1


def test_incorrect_report_structure():
    report_structure_error = copy.deepcopy(report_json)
    report_structure_error['report_structure'] = report_structure_error['report_structure']
    report_structure_error['report_structure'].append('Список источников')
    errors = check_report(report_odt, student_json, report_structure_error)
    assert "Отсутствуют пункты: Список источников" in errors and len(errors) == 1


def test_incorrect_uploaded_at():
    report_uploaded_at_error = copy.deepcopy(report_json)
    report_uploaded_at_error['uploaded_at'] = '2023-06-01T00:00:00Z'
    errors = check_report(report_odt, student_json, report_uploaded_at_error)
    assert "Неверная дата" in errors and len(errors) == 1


def test_incorrect_subject_name():
    report_subject_name_error = copy.deepcopy(report_json)
    report_subject_name_error['subject_name'] = 'Архитектура ЭВМ'
    errors = check_report(report_odt, student_json, report_subject_name_error)
    assert "Неверное название предмета" in errors and len(errors) == 1


def test_incorrect_task_name():
    report_task_name_error = copy.deepcopy(report_json)
    report_task_name_error['task_name'] = 'ЛР2. Разработка многопоточного приложения ' \
                                          'средствами POSIX в ОС Linux или Mac OS'
    errors = check_report(report_odt, student_json, report_task_name_error)
    assert "Неверное название работы" in errors and len(errors) == 1


def test_incorrect_task_type():
    report_task_type_error = copy.deepcopy(report_json)
    report_task_type_error['task_type'] = 'Контрольная работа'
    errors = check_report(report_odt, student_json, report_task_type_error)
    assert "Неверный тип задания" in errors and len(errors) == 1


def test_incorrect_student_name():
    student_name_error = student_json.copy()
    student_name_error['name'] = 'Иван'
    errors = check_report(report_odt, student_name_error, report_json)
    assert "Неверное ФИО студента" in errors and len(errors) == 1


def test_incorrect_student_surname():
    student_surname_error = student_json.copy()
    student_surname_error['surname'] = 'Иванов'
    errors = check_report(report_odt, student_surname_error, report_json)
    assert "Неверное ФИО студента" in errors and len(errors) == 1


def test_incorrect_student_patronymic():
    student_patronymic_error = student_json.copy()
    student_patronymic_error['patronymic'] = 'Иванович'
    errors = check_report(report_odt, student_patronymic_error, report_json)
    assert "Неверное ФИО студента" in errors and len(errors) == 1


def test_incorrect_teacher_name():
    teacher_name_error = copy.deepcopy(report_json)
    teacher_name_error['teacher']['name'] = 'Иван'
    errors = check_report(report_odt, student_json, teacher_name_error)
    assert "Неверное ФИО преподавателя" in errors and len(errors) == 1


def test_incorrect_teacher_surname():
    teacher_surname_error = copy.deepcopy(report_json)
    teacher_surname_error['teacher']['surname'] = 'Иванов'
    errors = check_report(report_odt, student_json, teacher_surname_error)
    assert "Неверное ФИО преподавателя" in errors and len(errors) == 1


def test_incorrect_teacher_patronymic():
    teacher_patronymic_error = copy.deepcopy(report_json)
    teacher_patronymic_error['teacher']['patronymic'] = 'Иванович'
    errors = check_report(report_odt, student_json, teacher_patronymic_error)
    assert "Неверное ФИО преподавателя" in errors and len(errors) == 1


def test_multiple_errors():
    student_errors = student_json.copy()
    report_errors = copy.deepcopy(report_json)
    report_errors['subject_name'] = 'Архитектура ЭВМ'
    student_errors['group'] = '1111K'
    report_errors['uploaded_at'] = '2023-06-01T00:00:00Z'
    expected_errors = {'Неверное название предмета', 'Неверная группа', 'Неверная дата'}
    errors = check_report(report_odt, student_errors, report_errors)
    assert expected_errors == set(errors) and len(errors) == 3



