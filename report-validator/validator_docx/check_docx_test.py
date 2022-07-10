from check_docx import check_docx
import io
import pytest
from copy import deepcopy

student = {
  "name": "Екатерина",
  "surname": "Цыганкова",
  "patronymic": "Александровна",
  "group": "4936"
}

report = {
  "subject_name": "Операционные системы",
  "task_name": "ЛР2. Работа с текстовыми потоками в командном интерпретаторе Bash",
  "task_type": "Лабораторная работа",
  "teacher": {
    "name": "Марк",
    "surname": "Поляк",
    "patronymic": "Дмитриевич",
    "status": "Старший преподаватель"
  },
  "report_structure": [
    "Цель","Индивидуальное задание", "Описание входных данных", "Результат выполнения работы", "Исходный код программы с комментариями", "Выводы"
  ],
  "uploaded_at": "2022-06-01T00:00:00Z"
}

f1 = open('docx_files//lab.docx','rb')
f2 = open('docx_files//lab_title.docx','rb')
f3 = open('docx_files//lab_wrong_struc.docx','rb')
f4 = open('docx_files//kontr.docx','rb')
f5 = open('docx_files//ref.docx','rb')
f6 = open('docx_files//kursrab.docx','rb')
f7 = open('docx_files//kurspr.docx','rb')
f8 = open('docx_files//lab_lot_err.docx','rb')

reports = {
    "lab": f1.read(),
    "lab_title" : f2.read(),
    "lab_wrong_struc" : f3.read(),
    "kontr" : f4.read(),
    "ref" : f5.read(),
    "kursrab" : f6.read(),
    "kurspr" : f7.read(),
    "lab_lot_err" : f8.read()
}

"""
reports = {
    "lab": open('docx_files//lab.docx','rb').read(),
    "lab_title" : open('docx_files//lab_title.docx','rb').read(),
    "lab_wrong_struc" : open('docx_files//lab_wrong_struc.docx','rb').read(),
    "kontr" : open('docx_files//kontr.docx','rb').read(),
    "ref" : open('docx_files//ref.docx','rb').read(),
    "kursrab" : open('docx_files//kursrab.docx','rb').read(),
    "kurspr" : open('docx_files//kurspr.docx','rb').read(),
    "lab_lot_err" : open('docx_files//lab_lot_err.docx','rb').read()
}
"""

#тесты для проверки входных данных
#словарь отчета без одного ключа
def test_rep_without_key():
    rep = deepcopy(report)
    rep.pop("uploaded_at")
    with pytest.raises(SystemExit) as e:
        check_docx(student, rep, io.BytesIO(reports["lab"]))
    assert e.type == SystemExit
    assert e.value.code == 1

#словарь студента без одного ключа
def test_stud_without_key():
    stud = deepcopy(student)
    stud.pop("surname")
    with pytest.raises(SystemExit) as e:
        check_docx(stud, report, io.BytesIO(reports["lab"]))
    assert e.type == SystemExit
    assert e.value.code == 2

#словарь студента без ключа отчества
#возвращается не код ошибки, программа завершается корректно с
#выводом ошибки о неверных фио студента
def test_stud_without_patr():
    stud = deepcopy(student)
    stud.pop("patronymic")
    res = check_docx(stud, report, io.BytesIO(reports["lab"]))
    assert len(res) == 1
    assert res[0][0:21] == "Неверные ФИО студента"

#словарь студента с none в отчестве
#возвращается не код ошибки, программа завершается корректно с
#выводом ошибки о неверных фио студента
def test_stud_none_patr():
    stud = deepcopy(student)
    stud["patronymic"] = None
    res = check_docx(stud, report, io.BytesIO(reports["lab"]))
    assert len(res) == 1
    assert res[0][0:21] == "Неверные ФИО студента"

#словарь учителя без одного ключа
def test_teach_without_key():
    rep = deepcopy(report)
    rep["teacher"].pop("name")
    with pytest.raises(SystemExit) as e:
        check_docx(student, rep, io.BytesIO(reports["lab"]))
    assert e.type == SystemExit
    assert e.value.code == 3

#словарь отчета без ключа отчества
#возвращается не код ошибки, программа завершается корректно с
#выводом ошибки о неверных фио преподавателя
def test_teach_without_patr():
    rep = deepcopy(report)
    rep["teacher"].pop("patronymic")
    res = check_docx(student, rep, io.BytesIO(reports["lab"]))
    assert len(res) == 1
    assert res[0][0:26] == "Неверные ФИО преподавателя"

#словарь учетиля с None  в отчестве
#возвращается не код ошибки, программа завершается корректно с
#выводом ошибки о неверных фио преподавателя
def test_teach_none_patr():
    rep = deepcopy(report)
    rep["teacher"]["patronymic"] = None
    res = check_docx(student, rep, io.BytesIO(reports["lab"]))
    assert len(res) == 1
    assert res[0][0:26] == "Неверные ФИО преподавателя"

#словарь студента с пустой строкой в ключе
def test_stud_empty_key():
    stud = deepcopy(student)
    stud["name"] =''
    with pytest.raises(SystemExit) as e:
        check_docx(stud, report, io.BytesIO(reports["lab"]))
    assert e.type == SystemExit
    assert e.value.code == 4

#словарь отчета с пустой строкой в ключе
def test_rep_empty_key():
    rep = deepcopy(report)
    rep["task_name"] = ''
    with pytest.raises(SystemExit) as e:
        check_docx(student, rep, io.BytesIO(reports["lab"]))
    assert e.type == SystemExit
    assert e.value.code == 5

#словарь учителя с пустой строкой в ключе
def test_teach_empty_key():
    rep = deepcopy(report)
    rep["teacher"]["patronymic"] = ''
    with pytest.raises(SystemExit) as e:
        check_docx(student, rep, io.BytesIO(reports["lab"]))
    assert e.type == SystemExit
    assert e.value.code == 6


#тесты для проверки правильных отчетов
#проверка лабораторной работы
def test_correct_lab():
    res = check_docx(student, report, io.BytesIO(reports["lab"]))
    assert len(res) == 0

#контрольная работа
def test_correct_kontr():
    rep = {
    "subject_name": "Архитектура ЭВМ",
    "task_name": "ПРЕДСТАВЛЕНИЕ ДАННЫХ В ЭВМ ТИПА VAX-11",
    "task_type": "Контрольная работа",
    "teacher": {
        "name": "Владимир",
        "surname": "Федоров",
        "patronymic": "Станиславович",
        "status": "доц., канд. техн. наук"
    },
    "report_structure": [],
    "uploaded_at": "2022-06-01T00:00:00Z"
    }
    res = check_docx(student, rep, io.BytesIO(reports["kontr"]))
    assert len(res) == 0

#реферат
def test_correct_ref():
    rep = {
    "subject_name": "Информационные технологии в экономике",
    "task_name": "ИНФОРМАЦИОННОЕ ОБЩЕСТВО",
    "task_type": "Реферат",
    "teacher": {
        "name": "Владимир",
        "surname": "Орлов",
        "patronymic": "Павлович",
        "status": "проф., д-р техн. наук"
    },
    "report_structure": [],
    "uploaded_at": "2022-06-01T00:00:00Z"
    }
    res = check_docx(student, rep, io.BytesIO(reports["ref"]))
    assert len(res) == 0

#курсовая работа
def test_correct_kursrab():
    rep = {
    "subject_name": "Прикладные модели оптимизации",
    "task_name": "Школьные перевозки",
    "task_type": "Курсовая работа",
    "teacher": {
        "name": "Мария",
        "surname": "Фаттахова",
        "patronymic": "Владимировна",
        "status": "доц., к.ф.-м.н., доцент"
    },
    "report_structure": ["Цель","Постановка задачи","Математическая модель","Оптимальное решение задачи","Обоснование выбора языка программирования","Список использованной литературы"],
    "uploaded_at": "2021-06-01T00:00:00Z"
    }
    res = check_docx(student, rep, io.BytesIO(reports["kursrab"]))
    assert len(res) == 0

#курсовой проект
def test_correct_kurspr():
    rep = {
    "subject_name": "Структуры и алгоритмы обработки данных",
    "task_name": "Использование заданных структур данных и алгоритмов при разработке программного обеспечения информационной системы",
    "task_type": "Курсовой проект",
    "teacher": {
        "name": "Валерий",
        "surname": "Матьяш",
        "patronymic": "Анатольевич",
        "status": "доц., канд. техн. наук"
    },
    "report_structure": ["Задание","Введение","Алгоритмы и структуры данных","Описание программы","Тестирование программы","Заключение"],
    "uploaded_at": "2021-06-01T00:00:00Z"
    }
    res = check_docx(student, rep, io.BytesIO(reports["kurspr"]))
    assert len(res) == 0

#лр со свободным титульным листом
def test_correct_lab_title():
    res = check_docx(student, report, io.BytesIO(reports["lab_title"]))
    assert len(res) == 0

#тесты для проверки всех элементов отчета
#проверка структуры отчета
def test_incorrect_struture_title():
    res = check_docx(student, report, io.BytesIO(reports["lab_wrong_struc"]))
    assert len(res) == 1
    assert res[0][0:115] == 'Элементы отчета: "Должность преподавателя", "ФИО преподавателя", "Год", "Цель" — нарушают его корректную структуру.'


#в данном тесте и далее проверяется один отчет, меняются только входные данные
#фио студента
def test_surname_student():
    stud = deepcopy(student)
    stud["surname"] = "Иванов"
    res = check_docx(stud, report, io.BytesIO(reports["lab"]))
    assert len(res) == 1
    assert res[0][0:21] == "Неверные ФИО студента"

#группа студента
def test_group_student():
    stud = deepcopy(student)
    stud["group"] = 4932
    res = check_docx(stud, report, io.BytesIO(reports["lab"]))
    assert len(res) == 1
    assert res[0][0:21] == "Неверный номер группы"

#предмет
def test_subject_report():
    rep = deepcopy(report)
    rep["subject_name"] = "Информационное право"
    res = check_docx(student, rep, io.BytesIO(reports["lab"]))
    assert len(res) == 1
    assert res[0][0:26] == "Неверное название предмета"

#имя работы
def test_task_name_report():
    rep = deepcopy(report)
    rep["task_name"] = "Представление данных в ЭВМ типа VAX-11"
    res = check_docx(student, rep, io.BytesIO(reports["lab"]))
    assert len(res) == 1
    assert res[0][0:24] == "Неверное название работы"

#тип работы
def test_task_type_report():
    rep = deepcopy(report)
    rep["task_type"] = "Реферат"
    res = check_docx(student, rep, io.BytesIO(reports["lab"]))
    assert len(res) == 1
    assert res[0][0:20] == "Неверный тип задания"

#фио преподавателя
def test_surname_teacher():
    rep = deepcopy(report)
    rep["teacher"]["surname"] = "Антохина"
    res = check_docx(student, rep, io.BytesIO(reports["lab"]))
    assert len(res) == 1
    assert res[0][0:26] == "Неверные ФИО преподавателя"

#должность преподавателя
def test_status_teacher():
    rep = deepcopy(report)
    rep["teacher"]["status"] = "Ректор, д.т.н., проф."
    res = check_docx(student, rep, io.BytesIO(reports["lab"]))
    assert len(res) == 1
    assert res[0][0:32] == "Неверная должность преподавателя"

#год
def test_year_report():
    rep = deepcopy(report)
    rep["uploaded_at"] = "2020-06-01T00:00:00Z"
    res = check_docx(student, rep, io.BytesIO(reports["lab"]))
    assert len(res) == 1
    assert res[0][0:12] == "Неверный год"

#наличие структуры отчета
def test_struture_report():
    rep = deepcopy(report)
    rep["report_structure"].append("Окончательные выводы")
    res = check_docx(student, rep, io.BytesIO(reports["lab"]))
    assert len(res) == 1
    assert res[0][0:61] == "Неверная структура отчета. Не найдено: "+'"Окончательные выводы"'

#отчет по лабораторной, в котором находится
#сразу несколько ошибок
def test_lab_lot_err():
    rep = deepcopy(report)
    rep["task_name"] = "ЛР5. Управление памятью"
    rep["report_structure"] = ["Цель","Задание","Описание ипользуемых алгоритмов замещения страниц","Результат выполнения работы","Исходный код программы с комментариями","Выводы"]
    res = check_docx(student, rep, io.BytesIO(reports["lab_lot_err"]))
    assert len(res) == 5
    assert res[0][0:32] == "Неверная должность преподавателя"
    assert res[1][0:20] == "Неверный тип задания"
    assert res[2][0:12] == "Неверный год"
    assert res[3][0:90] == 'Неверная структура отчета. Не найдено: "'+rep["report_structure"][2]+'"'
    assert res[4][0:165] == 'Элементы отчета: "Название работы", "Название предмета", "Результат выполнения работы", "Исходный код программы с комментариями" — нарушают его корректную структуру.'
    
f1.close()
f2.close()
f3.close()
f4.close()
f5.close()
f6.close()
f7.close()
f8.close()
