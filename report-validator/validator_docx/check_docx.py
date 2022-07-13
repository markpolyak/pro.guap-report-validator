import io
import json
import docx2txt
import datetime
import sys
from operator import itemgetter

def check_docx(infstudent, infreport, document) -> list:

    if type(infstudent) != dict:
        raise TypeError('Информация о студенте не является словарем')

    if type(infreport) != dict:
        raise TypeError('Информация об отчете не является словарем')

    if type(infreport["teacher"]) != dict:
        raise TypeError('Ключ "teacher" словаря отчета не является словарем')
    
    #проверка на количество ключей в словаре отчета
    if len(infreport.keys()) != 6:
        raise ValueError('В словаре отчета недостаточное количество ключей')

    #проверка на количество ключей в словаре студента
    len_stud = len(infstudent.keys())
    if not (len_stud == 4 or (len_stud == 3 and 'patronymic' not in infstudent.keys())):
        raise ValueError('В словаре студента недостаточное количество ключей')

    #проверка на количество ключей в словаре преподавателя
    if type(infreport["teacher"]) == dict:
        len_teach = len(infreport["teacher"].keys())
        if not (len_teach == 4 or (len_teach == 3 and 'patronymic' not  in infreport["teacher"].keys())):
            raise ValueError('В словаре учителя недостаточное количество ключей')
    
    #проверка на пустую строку ключей словаря студента
    for k in infstudent.keys():
        if infstudent[k] == '':
            raise ValueError('В словаре студента ключ "'+k+'" является пустой строкой')

    #проверка на пустую строку ключей словаря отчета
    for k in infreport.keys():
        if infreport[k] == '':
            raise ValueError('В словаре отчета ключ "'+k+'" является пустой строкой')

    #проверка на пустую строку ключей словаря преподавателя
    for k in infreport["teacher"].keys():
        if infreport["teacher"][k] == '':
            raise ValueError('В словаре учителя ключ "'+k+'" является пустой строкой')

    #извлечение содержимого документа
    result = docx2txt.process(document)
   
    #строка фио студента
    stud_fio = infstudent["name"][0] + "."
    if "patronymic" in infstudent.keys() and infstudent["patronymic"] != None:
        stud_fio +=  infstudent["patronymic"][0] + "."
    stud_fio+= ' '+ infstudent["surname"]

    #строка фио преподавателя
    teach_fio = infreport["teacher"]["name"][0] + "."
    if "patronymic" in infreport["teacher"].keys() and infreport["teacher"]["patronymic"] != None:
        teach_fio +=  infreport["teacher"]["patronymic"][0] + "."
    teach_fio+= ' '+ infreport["teacher"]["surname"]

    #дата загрузки отчета
    uploaded_at = datetime.datetime.strptime(infreport["uploaded_at"], '%Y-%m-%dT%H:%M:%SZ')

    #добавление в список непустых строк, извлеченнных из документа
    content = []
    for line in result.splitlines():
        if line != '':
            content.append(line)

    #список с ошибками
    errors = list()

    #список структуры отчета с найденными и не найденными элементами
    struc_info = [ #наименование (или индекс массива), номер строки, номер позиции
        ["Должность преподавателя", -1, -1],
        ["ФИО преподавателя", -1, -1],
        ["Тип задания", -1, -1],
        ["Название работы", -1, -1],
        ["Название предмета",-1, -1],
        ["Номер группы", -1, -1],
        ["ФИО студента", -1, -1],
        ["Год",-1, -1]
        ]

    N = len(content)
    
    #если указаны обязательные разделы отчета
    if "report_structure" in infreport.keys() and infreport["report_structure"] !=None and len(infreport["report_structure"])!=0:
        #добавляем в список индексы массива
        for i in range(len(infreport["report_structure"])):
            struc_info.append([i,-1,-1])
        #ищем ключевые слова обязательных разделов отчета
        for s in range(len(infreport["report_structure"])):
            for line in range(N):
                struc_info[8+s][2] = content[line].find(infreport["report_structure"][s])
                if struc_info[8+s][2] != -1:
                    struc_info[8+s][1] = line
                    break

    #тип задания
    if "лабораторная работа" in infreport["task_type"].lower():
        for line in range(N):
            struc_info[2][2] = content[line].find(infreport["task_type"])
            if struc_info[2][2] != -1:
                struc_info[2][1] = line
                break
            else:
                struc_info[2][2] = content[line].find("ЛАБОРАТОРНОЙ РАБОТЕ")
                if struc_info[2][2] !=-1:
                    struc_info[2][1] = line
                    break
                else:
                    struc_info[2][2] = content[line].find("лабораторной работе")
                    if struc_info[2][2] !=-1:
                        struc_info[2][1] = line
                        break
                    else:
                        struc_info[2][2] = content[line].find("Лабораторная работа")
                        if struc_info[2][2] !=-1:
                            struc_info[2][1] = line
                            break
    elif "контрольная работа" in infreport["task_type"].lower():
        for line in range(N):
            struc_info[2][2] = content[line].find(infreport["task_type"])
            if struc_info[2][2] != -1:
                struc_info[2][1] = line
                break
            else:
                struc_info[2][2] = content[line].find("КОНТРОЛЬНАЯ РАБОТА")
                if struc_info[2][2] != -1:
                    struc_info[2][1] = line
                    break
                else:
                    struc_info[2][2] = content[line].find("Контрольная работа")
                    if struc_info[2][2] != -1:
                        struc_info[2][1] = line
                        break
    elif "реферат" in infreport["task_type"].lower():
        for line in range(N):
            struc_info[2][2] = content[line].find(infreport["task_type"])
            if struc_info[2][2] != -1:
                struc_info[2][1] = line
                break
            else:
                struc_info[2][2] = content[line].find("РЕФЕРАТ")
                if struc_info[2][2] == 0:
                    struc_info[2][1] = line
                    break
                else:
                    struc_info[2][2] = content[line].find("Реферат")
                    if struc_info[2][2] == 0:
                        struc_info[2][1] = line
                        break
    elif "курсовая работа" in infreport["task_type"].lower():
        for line in range(N):
            struc_info[2][2] = content[line].find(infreport["task_type"])
            if struc_info[2][2] != -1:
                struc_info[2][1] = line
                break
            else:
                struc_info[2][2] = content[line].find("КУРСОВОЙ РАБОТЕ")
                if struc_info[2][2] != -1:
                    struc_info[2][1] = line
                    break
                else:
                    struc_info[2][2] = content[line].find("курсовой работе")
                    if struc_info[2][2] != -1:
                        struc_info[2][1] = line
                        break
    elif "курсовой проект" in infreport["task_type"].lower():
        for line in range(N):
            struc_info[2][2] = content[line].find(infreport["task_type"])
            if struc_info[2][2] != -1:
                struc_info[2][1] = line
                break
            else:
                struc_info[2][2] = content[line].find("КУРСОВОМУ ПРОЕКТУ")
                if struc_info[2][2] != -1:
                    struc_info[2][1] = line
                    break
                else:
                    struc_info[2][2] = content[line].find("курсовому проекту")
                    if struc_info[2][2] != -1:
                        struc_info[2][1] = line
                        break
    
    for line in range(N):
        #должность преподавателя
        struc_info[0][2] = content[line].find(infreport["teacher"]["status"])
        if  struc_info[0][2] != -1 and struc_info[0][1] == -1:
            struc_info[0][1] = line

        #ФИО преподавателя
        struc_info[1][2] = content[line].find(teach_fio)
        if struc_info[1][2] != -1 and struc_info[1][1] == -1:
            struc_info[1][1] = line

        #название работы
        struc_info[3][2] = content[line].find(infreport["task_name"])
        if struc_info[3][2] != -1 and struc_info[3][1] == -1:
            struc_info[3][1] = line
        else:
            struc_info[3][2] = content[line].find(infreport["task_name"].upper())
            if struc_info[3][2] != -1 and struc_info[3][1] == -1:
                struc_info[3][1] = line

        #название предмета
        struc_info[4][2] = content[line].find(infreport["subject_name"])
        if struc_info[4][2] != -1 and struc_info[4][1] == -1:
            struc_info[4][1] = line
        else:
            struc_info[4][2] = content[line].find(infreport["subject_name"].upper())
            if  struc_info[4][2] != -1 and struc_info[4][1] == -1:
                struc_info[4][1] = line
            else:
                struc_info[4][2] = content[line].find(infreport["subject_name"].lower())
                if  struc_info[4][2] != -1 and struc_info[4][1] == -1:
                    struc_info[4][1] = line

        #номер группы
        struc_info[5][2] = content[line].find(str(infstudent["group"]))
        if struc_info[5][2] != -1 and struc_info[5][1] == -1:
            struc_info[5][1] = line

        #ФИО студента
        struc_info[6][2] = content[line].find(stud_fio)
        if struc_info[6][2] != -1 and struc_info[6][1] == -1:
            struc_info[6][1] = line

        #год      
        struc_info[7][2] = content[line].find(str(uploaded_at.year))
        if struc_info[7][2] != -1 and struc_info[7][1] == -1:
            struc_info[7][1] = line
    
    #если что-то не найдено в титульнике
    if struc_info[0][1] == -1:
        errors.append('Неверная должность преподавателя. Предполагалось: "'+infreport["teacher"]["status"]+'"')
    if struc_info[1][1] == -1:
        errors.append('Неверные ФИО преподавателя. Предполагалось: "'+ teach_fio+'"')
    if struc_info[2][1] == -1:
        errors.append('Неверный тип задания. Предполагалось: "'+ infreport["task_type"]+'"')
    if struc_info[3][1] == -1:
        errors.append('Неверное название работы. Предполагалось: "'+ infreport["task_name"]+'"')
    if struc_info[4][1] == -1:
        errors.append('Неверное название предмета. Предполагалось: "'+ infreport["subject_name"]+'"')
    if struc_info[5][1] == -1:
        errors.append('Неверный номер группы. Предполагалось: "'+ str(infstudent["group"])+'"')
    if struc_info[6][1] == -1:
        errors.append('Неверные ФИО студента. Предполагалось: "'+ stud_fio+'"')
    if struc_info[7][1] == -1:
        errors.append('Неверный год. Предполагалось: "'+ str(uploaded_at.year)+'"')
    if len(struc_info) > 8:
        #если что-то не найдено в отчете
        for i in range(8, len(struc_info)):
            if struc_info[i][1] == -1:
                errors.append('Неверная структура отчета. Не найдено: "'+ infreport["report_structure"][struc_info[i][0]]+'"')
   
    #структура отчета с найденными и ненайденными элементами
    struc_info_cor = list(struc_info)

    #далее работаем только с теми, что были найдены
    #удалить все ненайденные элементы (-1)
    struc_info1 = [s for s in struc_info if s[1] != -1]
   
    #если список непустой, что-то было найдено
    if len(struc_info1) != 0:
        #сортируем список по строкам и сравниваем с верной структурой отчета
        #выводим что нарушает последовательность и верную последовательсноть с первого элемента, нарушающего ее
        struc_info_correct_order = list(struc_info1)
        struc_info1.sort(key=itemgetter(1, 2))
    
        lst = []
        lst_cor = []
        k = -1
        for i in range(len(struc_info_correct_order)):
            if struc_info1[i][0] != struc_info_correct_order[i][0]:
                if k == -1:
                    k = struc_info_correct_order[i][0]
                if type(struc_info_correct_order[i][0]) == int:
                    lst.append('"'+infreport["report_structure"][struc_info_correct_order[i][0]]+'"')
                else:
                    lst.append('"'+struc_info_correct_order[i][0]+'"')

        #составляем список верной структуры (даже с теми элементами, которые были пропущены)
        if len(lst) != 0:
            for l in range(len(struc_info_cor)):
                if struc_info_cor[l][0] == k:
                    for i in range(l,len(struc_info_cor)):
                        if type(struc_info_cor [i][0]) == int:
                            lst_cor.append('"'+infreport["report_structure"][struc_info_cor[i][0]]+'"')
                        else:
                            lst_cor.append('"'+struc_info_cor[i][0]+'"')
                    break
            delim = ', '
            errors.append("Элементы отчета: "+delim.join(lst) + " — нарушают его корректную структуру. Верная структура: "+delim.join(lst_cor)+'.')

    return errors

if __name__ == "__main__":

    # вызов из консоли
    if len(sys.argv) == 4:
        #преобразуем в словари принятые аргументы
        arg1 = json.loads(sys.argv[1])
        arg2 = json.loads(sys.argv[2])
        #file = sys.argv[3] #путь к файлу
        #передаем в функцию буферизированный поток байт
        #check_docx(arg1, arg2, io.BytesIO(open("{}".format(file),'rb').read()))
        file = open("{}".format(sys.argv[3]),'rb')
        res = check_docx(arg1, arg2, io.BytesIO(file.read()))
        file.close()
        for i in res:
            print(i+'\n')
    elif len(sys.argv) > 4:
        print("Слишком много аргументов")
    elif len(sys.argv) < 4:
        print("Слишком мало аргументов")
