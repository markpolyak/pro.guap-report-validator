from PyPDF2 import PdfReader
import re
import sys
import json
import io

def parser_report_pdf(pdf_document, student, report_info):

    if len(student) == 0 or len(report_info) == 0:
        return 1
    # проверка количества агрументов о студенте
    if not (len(student.keys()) == 4 or (len(student.keys()) == 3 and 'patronymic' not in student.keys())): 
        return 1

    # проверка, что все параметры не пустые
    for key in student:
        if (student[key] == None and key != 'patronymic') or (student[key] == ''):
            return 1

    if len(report_info) != 6:
        return 1

    # проверка, что все параметры не пустые
    for key in report_info:
        if (report_info[key] == None and key != 'report_structure') or (report_info[key] == ''):
            return 1

    # проверка информации о преподавателе
    if not ('teacher' in report_info.keys()):
        return 1

    if not (len(report_info['teacher']) == 4 or (len(report_info['teacher']) == 3 and not ('patronymic' in report_info["teacher"].keys()))):
        return 1

    for key in report_info['teacher']:
        if (report_info['teacher'][key] == None and key != 'patronymic') or (report_info['teacher'][key] == ''):
            return 1

    structure = {
    "должность": -1,
    "ФИО преподавателя": -1,
    "тип работы": -1,
    "название работы": -1,
    "название предмета": -1,
    "группа студента": -1,
    "ФИО студента": -1,
    "год отчета": -1,
    }

    f = io.BytesIO(pdf_document)
    pdf = PdfReader(f)
    page1 = pdf.pages[0]
    text = page1.extract_text()

    text2 = re.sub("[\t\n\f\v\r]" , "", text)
    regex = r"\s((\s)(\s+)?)?"
    textPage1 = re.sub(regex, " ", text2)

    #проверка должности
    if textPage1.find(report_info["teacher"]["status"]) != -1:
        structure["должность"] = textPage1.find(report_info["teacher"]["status"])
    else:
        structure["должность"] = textPage1.find(report_info["teacher"]["status"].capitalize()) #устанавливаем первую букву заглавной

    #проверка ФИО преподавателя
    if 'patronymic' in report_info["teacher"].keys() and not (report_info["teacher"]["patronymic"] is None): #есть отчество
        techer_name = report_info["teacher"]["name"][0] + '.' + report_info["teacher"]["patronymic"][0] + '. ' + report_info["teacher"]["surname"] + ' '
        structure["ФИО преподавателя"] = textPage1.find(techer_name)
    else:
        techer_name = report_info["teacher"]["name"][0] + '. ' + report_info["teacher"]["surname"] + ' '
        structure["ФИО преподавателя"] = textPage1.find(techer_name)
   
    #проверка типа работы
    start_index = 0
    if structure["ФИО преподавателя"] != -1:
        start_index = structure["ФИО преподавателя"]

    elif structure["должность"] != -1:
        start_index = structure["должность"]  
       
    if textPage1.find(report_info["task_type"], start_index) != -1:
        structure["тип работы"] = textPage1.find(report_info["task_type"], start_index)

    if structure["тип работы"] == -1:
        structure["тип работы"] = textPage1.find(report_info["task_type"].upper(), start_index)

    if structure["тип работы"] == -1:

        if report_info["task_type"] == "Лабораторная работа":
            structure["тип работы"] = textPage1.find("лабораторной работе", start_index)

            if structure["тип работы"] == -1:
                structure["тип работы"] = textPage1.find("ЛАБОРАТОРНОЙ РАБОТЕ", start_index)

        elif report_info["task_type"] == "Курсовая работа":
            structure["тип работы"] = textPage1.find("курсовой работе", start_index)

            if structure["тип работы"] == -1:
                structure["тип работы"] = textPage1.find("КУРСОВОЙ РАБОТЕ", start_index)
       
        elif report_info["task_type"] == "Курсовой проект":
            structure["тип работы"] = textPage1.find("курсовому проекту", start_index)

            if structure["тип работы"] == -1:
                structure["тип работы"] = textPage1.find("КУРСОВОМУ ПРОЕКТУ", start_index)

       
    #проверка названия работы
    structure["название работы"] = textPage1.find(report_info["task_name"])
    if structure["название работы"] == -1:
        structure["название работы"] = textPage1.find(report_info["task_name"].upper())

    #проверка названия предмета
    structure["название предмета"] = textPage1.find(report_info["subject_name"])
    if structure["название предмета"] == -1:
        structure["название предмета"] = textPage1.find(report_info["subject_name"].upper())
   
    #проверка группы студента
    structure["группа студента"] = textPage1.find(student["group"].upper())
   
    #проверка ФИО студента
    if 'patronymic' in student.keys() and not (student["patronymic"] is None): #есть отчество
        student_name = student["name"][0] + '.' + student["patronymic"][0] + '. ' + student["surname"] + ' '
        structure["ФИО студента"] = textPage1.find(student_name)
    else:
        student_name = student["name"][0] + '. ' + student["surname"] + ' '
        structure["ФИО студента"] = textPage1.find(student_name)
   
    #проверка даты
    year = report_info["uploaded_at"][0:4]
    structure["год отчета"] = textPage1.rfind(year) #поиск последнего вхождения

    error_list = []
    error_key = []

    for key in structure:
        if structure[key] == -1:
            error_key.append(key)

    for key in error_key:
        structure.pop(key)
        if key == "ФИО преподавателя":
            line = techer_name
        elif key == "ФИО студента":
            line = student_name
        elif key == "год отчета":
            line = year
        elif key == "должность":
            line = report_info["teacher"]["status"]
        elif key == "тип работы":
            line = report_info["task_type"]
        elif key == "название работы":
            line = report_info["task_name"]
        elif key == "название предмета":
            line = report_info["subject_name"]
        else: 
            line = student["group"]
       
        error_list.append("Отсутствует " + key + ", ожидалось: " + line)

    sortStructure = sorted(structure.items(), key=lambda x: x[1]) #сортируем найденные ключевые слова
    sortStructureDict = dict(sortStructure)

    keysStruct = structure.keys()
    mas = [] #список ключей в верной последовательности
    for k in keysStruct:
        mas.append(k)

    i = 0
    for key in sortStructureDict:
        if mas[i] != key:
            error_list.append("Неправильная позиция элемента " + key + ", ожидалось: " + mas[i])
        i += 1

    #проверка обязательных разделов
    if not (report_info["report_structure"] is None) and len(report_info["report_structure"]) != 0:
        report_structure = dict.fromkeys(report_info["report_structure"], False)
        r_st = []

        for page in pdf.pages: # перебираем страницы
            if page != 0:
                i = 0
                for key in report_structure: # проверяем сколько ненайденных слов осталось
                    if report_structure[key] == False:
                        i += 1
                if i != 0: #если остались ненайденные ключевые слова
                    #strText = page.extractText()
                    #strText2 = strText.replace("\s","")
                    strText = page.extract_text()
                    strText2 = re.sub("[\t\n\f\v\r]" , "", strText)
                    textPageN = re.sub(regex, " ", strText2)
                    for key in report_structure:
                        if report_structure[key] == False and textPageN.find(key) != -1:
                            report_structure[key] = True
   
   
        for key in report_structure:
            if report_structure[key] == False:
                error_list.append("В содержимом отчета отсутствует раздел: " + key)

    return error_list

if __name__ == "__main__":
    if len (sys.argv) == 4:

        str1 = sys.argv[2].replace("'", "\"")
        # проверяем введенную информацию о студенте
        stud = json.loads(str1)

        str2 = sys.argv[3].replace("'", "\"")
        # проверка структуры  отчета
        rep_inf = json.loads(str2)

        file = open("{}".format(sys.argv[1]),'rb')
        
        print(parser_report_pdf(file.read() , stud, rep_inf))
        file.close()

    else:
        sys.exit(1)
