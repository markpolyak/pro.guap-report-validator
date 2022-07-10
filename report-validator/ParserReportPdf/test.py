from ParserReportPdf import parser_report_pdf
import copy

student = {
      "name": "Андрей",
      "surname": "Антонов",
      "patronymic": "Юрьевич",
      "group": "5131"
    }

report_info = {
      "subject_name": "Архитектура ЭВМ",
      "task_name": "Представление данных в эвм типа VAX-11",
      "task_type": "Контрольная работа",
      "teacher": {
        "name": "Валерий",
        "surname": "Федоров",
        "patronymic": None,
        "status": "доц., канд. техн. наук"
      },
      "report_structure": [
        "Цель", "Задание", "Результат выполнения", "Выводы"
      ],
      "uploaded_at": "2022-06-01T00:00:00Z"
}

#with open("kontr.pdf", "rb") as filehandle:
#    file = filehandle.read()

file = "kontr.pdf"

def test_task_type():
    r_inf = copy.deepcopy(report_info);
    r_inf["task_type"] = "Лабораторная работа"
    assert parser_report_pdf(file, student, r_inf) == ['Отсутствует тип работы, ожидалось: Лабораторная работа']

def test_student_name():
    stud = copy.deepcopy(student);
    stud["surname"] = "Лисичкин"
    assert parser_report_pdf(file, stud, report_info) == ['Отсутствует ФИО студента, ожидалось: А.Ю. Лисичкин ']
    
def test_student_group():
    stud = copy.deepcopy(student);
    stud["group"] = "5132"
    assert parser_report_pdf(file, stud, report_info) == ['Отсутствует группа студента, ожидалось: 5132']
    
def test_subject_name():
    r_inf = copy.deepcopy(report_info);
    r_inf["subject_name"] = "Основы программирования"
    assert parser_report_pdf(file, student, r_inf) == ['Отсутствует название предмета, ожидалось: Основы программирования']
    
def test_task_name():
    r_inf = copy.deepcopy(report_info);
    r_inf["task_name"] = "Элементарные функции LISP для работы со списками"
    assert parser_report_pdf(file, student, r_inf) == ['Отсутствует название работы, ожидалось: Элементарные функции LISP для работы со списками']
    
def test_teacher_name():
    r_inf = copy.deepcopy(report_info);
    r_inf["teacher"]["name"] = "Иван"
    assert parser_report_pdf(file, student, r_inf) == ['Отсутствует ФИО преподавателя, ожидалось: И. Федоров ']
    
def test_teacher_status():
    r_inf = copy.deepcopy(report_info);
    r_inf["teacher"]["status"] = "проф., д-р техн. наук"
    assert parser_report_pdf(file, student, r_inf) == ['Отсутствует должность, ожидалось: проф., д-р техн. наук']
    
def test_year():
    r_inf = copy.deepcopy(report_info);
    r_inf["uploaded_at"] = "2021-06-01T00:00:00Z"
    assert parser_report_pdf(file, student, r_inf) == ['Отсутствует год отчета, ожидалось: 2021']
    
def test_report_structure():
    r_inf = copy.deepcopy(report_info);
    r_inf["report_structure"] = [ "Цель", "Задание", "Ход работы", "Результат выполнения", "Выводы"]
    assert parser_report_pdf(file, student, r_inf) == ['В содержимом отчета отсутствует раздел: Ход работы']
    
def test_successful():
    assert parser_report_pdf(file, student, report_info) == []
    
def test_some_errors():
    stud = copy.deepcopy(student);
    r_inf = copy.deepcopy(report_info);
    stud['group'] = "4936";
    r_inf["teacher"]["name"] = "Петр";
    r_inf["subject_name"] = "Основы программирования";
    r_inf["report_structure"] = [ "Цель", "Задание", "Ход работы", "Результат выполнения", "Выводы"]
    assert parser_report_pdf(file, stud, r_inf) == ['Отсутствует ФИО преподавателя, ожидалось: П. Федоров ', 'Отсутствует название предмета, ожидалось: Основы программирования', 'Отсутствует группа студента, ожидалось: 4936', 'В содержимом отчета отсутствует раздел: Ход работы']
    
#with open("lab.pdf", "rb") as filehandle:
#    file2 = filehandle.read()
file2 = "lab.pdf"
    
def test_other_page0():
    student2 = {
      "name": "Алексей",
      "surname": "Антонов",
      "group": "5131"
    }

    report_info2 = {
      "subject_name": "Функциональное и логическое программирование",
      "task_name": "Элементарные функции LISP для работы со списками",
      "task_type": "Лабораторная работа",
      "teacher": {
        "name": "Валерий",
        "surname": "Федоров",
        "patronymic": None,
        "status": "доц., канд. техн. наук"
      },
      "report_structure": [
        "Цель", "Задание", "Результат выполнения", "Вывод"
      ],
      "uploaded_at": "2022-06-01T00:00:00Z"
}

    assert parser_report_pdf(file2, student2, report_info2) == []  

#with open("kontr (1).pdf", "rb") as filehandle:
#   file3 = filehandle.read()
file3 = "kontr (1).pdf"

def test_incorrect_position():
    assert parser_report_pdf(file3, student, report_info) == ['Отсутствует ФИО преподавателя, ожидалось: В. Федоров ', 'Отсутствует группа студента, ожидалось: 5131', 'Отсутствует год отчета, ожидалось: 2022', 'Неправильная позиция элемента название работы, ожидалось: тип работы', 'Неправильная позиция элемента тип работы, ожидалось: название работы', 'В содержимом отчета отсутствует раздел: Задание']    