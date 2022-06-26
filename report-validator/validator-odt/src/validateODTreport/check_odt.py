# Copyright 2022 TessierAshpoule256
import io
import json
import logging
import re
import sys

from datetime import datetime
from typing import cast

from odf.opendocument import load


class Check:
    def __init__(self, desired, errorDescription):
        self.desired = desired
        self.errorDescription = errorDescription
        self.flag = False

    def check(self, string):
        if re.search(self.desired, string, re.I) is not None:
            # if self.desired in string:
            return True
        else:
            return False


class Checks:
    def __init__(self, checksList):
        self.checksList = checksList

    def checking(self, string):
        for i in range(len(self.checksList)):
            if self.checksList[i].check(string):
                self.checksList[i].flag = True

    def result(self):
        lst = list()
        for i in range(len(self.checksList)):
            if not self.checksList[i].flag:
                lst.append(self.checksList[i].errorDescription)

        return lst


"""
input
    studentInformation     - словарь с информацией о студенте
        name            Иван
        surname         Иванов
        patronymic      Иванович
        group           4931
    informationAboutReport - словарь с информацией об отчете
        subject_name    Операционные системы
        task_name       ЛР1. Знакомство с командным интерпретатором bash
        task_type       Лабораторная работа
        teacher {
            name        Юлия
            surname     Антохина
            patronymic  Анатольевна
            status      Ректор, д.т.н., проф
        }
        report_structure: [
            "Цель", "Задание", "Результат выполнения", "Выводы"
        ]
        uploaded_at     2022-06-01T00:00:00Z
    inputStream            - файл с отчетом в виде потока байт
output
    Список строк с описанием ошибок в отчете, по одной строке на каждую ошибку
        error_list
"""


def check_odt(studentInformation, informationAboutReport, inputStream):
    # check input
    logging.debug("\t=========== start check ODT ===========")
    input_error = 0
    sizeOfStudent = len(studentInformation.keys())
    if not ((sizeOfStudent == 3 and 'patronymic' not in studentInformation.keys()) or sizeOfStudent == 4):
        logging.error("Недостаточно данных о студенте")
        input_error += 1

    if len(informationAboutReport.keys()) != 6:
        logging.error("Недостаточно данных об отчёте")
        input_error += 1

    teacher = None
    if 'teacher' not in informationAboutReport.keys():
        logging.error("Нет информации о преподавателе")
        input_error += 1
    else:
        teacher = informationAboutReport["teacher"]
        if not ((len(teacher.keys()) == 3 and 'patronymic' not in teacher.keys()) or len(teacher.keys()) == 4):
            logging.error("Недостаточно данных о преподавателе")
            input_error += 1

    if input_error != 0:
        return input_error

    # proc
    # определение ОС, для проверки наличия данных в буфере ввода
   # read = None
   # if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == "darwin":
   #     import select
   #     read, _, _ = select.select([sys.stdin], [], [], 0)
   #     logging.debug("OS:\tUnix")
   # elif sys.platform == "win32":
   #     import msvcrt
   #     logging.debug("OS:\tWindows")
   #     read = msvcrt.kbhit()
   # else:
   #    logging.error("ошибка определения ОС")

    if inputStream is None:  # and len(read):  # перенаправлен поток
        logging.debug("\tОбнаружен поток ввода")
        inputStream = io.BytesIO(sys.stdin.buffer.read())
        # logging.error(inputStream)
    elif inputStream is not None:  # есть параметр
        logging.debug("\tПоток передан параметром")
        # logging.debug(inputStream)
    else:  # нет ни потока, ни параметра
        logging.error("Нет ни потока, ни параметра")
        # return 10

    task_type = informationAboutReport["task_type"]

    # инициалы преподавателя
    t_name = teacher["name"]
    teacher_initials = t_name[0] + '.'
    if 'patronymic' in teacher.keys():
        teacher_initials += ' ' + cast(str, teacher["patronymic"])[0] + '.'

    # инициалы студента
    student_initials = studentInformation["name"][0] + '.'
    if 'patronymic' in studentInformation.keys():
        student_initials += ' ' + studentInformation["patronymic"][0] + '.'

    # парсинг даты
    uploaded_at = datetime.strptime(informationAboutReport["uploaded_at"], "%Y-%m-%dT%H:%M:%SZ")

    # список содержания отчёта
    list_report_items = informationAboutReport["report_structure"]

    # info
    logging.info("Студент:\t" + studentInformation["surname"] + ' ' + student_initials)
    logging.info("Группа:\t" + studentInformation["group"])
    logging.info("Отчёт:\t" + informationAboutReport["task_name"])
    logging.info("Загружен в:\t" + str(uploaded_at.year) + " году")

    # stream = sys.stdin.read()
    # stream = stream.replace('\n', '', 1)
    # with open(stream, 'r+b') as file:
    #     logging.error(file.read())
    # file.close()

    # odt = readingODT(inputStream)
    lst = list()

    for node in load(inputStream).body.childNodes[0].childNodes:
        if str(node) != "":
            lst.append(str(node))

    # logging.debug("==========================================")
    # for line in lst:
    #     logging.debug(line)
    # logging.debug("==========================================")

    # check
    checks_list = list()

    # определение типа работы
    str_error_type = "Некоректный тип задания, должна быть " + task_type
    if "Лабораторная работа" in task_type or "ЛАБОРАТОРНОЙ РАБОТЕ" in task_type:
        logging.debug("task_type:\tЛабораторная работа")
        checks_list.append(Check("лаб", str_error_type))
    elif "КОНТРОЛЬНАЯ РАБОТА" in task_type:
        logging.debug("task_type: Контрольная работа")
        checks_list.append(Check("КОНТРОЛЬНАЯ", str_error_type))
    elif "К КУРСОВОЙ РАБОТЕ" in task_type:
        logging.debug("task_type: Курсовая работа")
        checks_list.append(Check("КУРСОВОЙ", str_error_type))
    elif "РЕФЕРАТ" in task_type:
        logging.debug("task_type: Реферат")
        checks_list.append(Check("РЕФЕРАТ", str_error_type))
    else:
        logging.error("Невозможно определить тип работы " + task_type)

    # год
    checks_list.append(Check(str(uploaded_at.year), "Неверная дата, отчёт загружен в " + str(uploaded_at.year)))
    # ФИО студента
    checks_list.append(Check(student_initials, "Неверное ФИО студента"))
    checks_list.append(Check(studentInformation["surname"], "Неверное ФИО студента"))
    # ФИО преподавателя
    checks_list.append(Check(teacher_initials, "Неверное ФИО преподавателя"))
    checks_list.append(Check(teacher["surname"], "Неверное ФИО преподавателя"))
    # группа
    checks_list.append(Check(studentInformation["group"], "Неверная группа"))
    # предмет
    checks_list.append(Check(informationAboutReport["subject_name"], "Неверный предмет"))
    # должность
    checks_list.append(Check(teacher["status"], "Неверная должность преподавателя"))
    # название работы
    checks_list.append(Check(informationAboutReport["task_name"],
                             "Неверное заданание, должно быть " + informationAboutReport["task_name"]))

    # содержание отчёта
    for item in list_report_items:
        checks_list.append(Check(item, "Отсутствует пункт меню " + item))

    ch = Checks(checks_list)
    for string in lst:
        ch.checking(string)
    error_list = ch.result()

    error_list = list(set(error_list))
    if len(error_list) > 0:
        logging.info("===============================")
        for error in error_list:
            logging.warning(error)

    return error_list


if __name__ == "__main__":
    # запущен из консоли
    logging.basicConfig(level=0)

    # debug print argv to start in console
    logging.debug("\t=========== consol wthis " + str(len(sys.argv)) + " arg ===========")
    for i in range(len(sys.argv)):
        logging.debug("arg[" + str(i) + "] " + sys.argv[i])

    arg1 = json.loads(sys.argv[1])
    arg2 = json.loads(sys.argv[2])

    logging.debug("\t=========== after conversion ===========")
    logging.debug("\t\tинформация о студенте")
    logging.debug(arg1)
    logging.debug("\t\tинформация об отчёте")
    logging.debug(arg2)

    if len(sys.argv) == 3:
        check_odt(arg1, arg2, None)
    elif len(sys.argv) == 4:
        check_odt(arg1, arg2, sys.argv[3])
    else:
        logging.error("Слишком мало параметров")
else:
    logging.basicConfig(level=0)
    logging.debug("import odf check")
