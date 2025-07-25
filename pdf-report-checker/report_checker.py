import pdfplumber# 用于解析PDF内容
import re# 正则表达式处理
from datetime import datetime # 日期处理
import io# 处理字节流


def check_report(pdf_bytes, student_info, report_info):
    """
    Проверяет PDF-отчет студента на соответствие требованиям
    检查学生PDF报告是否符合要求
    Аргументы:参数
        pdf_bytes: bytes - содержимое PDF-файла PDF文件的字节内容
        student_info: dict - информация о студенте 学生信息字典
        report_info: dict - информация об отчете 报告信息字典

    Возвращает:返回
        list: список строк с описанием ошибок 错误信息列表
    """
    # 初始化错误列表
    errors = []

    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            # Проверка титульного листа (первая страница)检查是否为空PDF
            if len(pdf.pages) == 0:
                errors.append("Отчет пустой")
                return errors

            # 获取第一页(封面页)
            first_page = pdf.pages[0]
            first_page_text = first_page.extract_text() # 提取文本

            # 检查文本提取是否成功
            if first_page_text is None:
                errors.append("Не удалось извлечь текст с титульного листа")
                return errors

            # Создаем очищенную версию текста清理文本：去除多余空格
            cleaned_text = re.sub(r'\s+', ' ', first_page_text).strip()
            cleaned_text_lower = cleaned_text.lower()# 转换为小写便于比较

            # === Отладочная информация === 输出调试信息
            print("===== DEBUG INFO =====")
            print(
                f"Ожидаемое ФИО студента: {student_info['surname']} {student_info['name']} {student_info.get('patronymic', '')}")
            print(
                f"Ожидаемое ФИО преподавателя: {report_info['teacher']['surname']} {report_info['teacher']['name']} {report_info['teacher'].get('patronymic', '')}")
            print(f"Ожидаемая должность преподавателя: {report_info['teacher']['status']}")
            print(f"Ожидаемый тип задания: {report_info['task_type']}")
            print("Извлеченный и очищенный текст:")
            print(cleaned_text)
            print("=======================")

            # Проверка ФИО студента检查学生姓名
            student_parts = [
                student_info['surname'].strip().lower(),
                student_info['name'].strip().lower()
            ]
            if student_info.get('patronymic'):# 如果有父称
                student_parts.append(student_info['patronymic'].strip().lower())

            found_student = True
            for part in student_parts:
                if part and part not in cleaned_text_lower:
                    found_student = False
                    print(f"Отсутствует часть ФИО студента: '{part}'")
                    break

            if not found_student:
                errors.append("Неверное ФИО студента")

            # Проверка группы检查学生小组
            if 'group' in student_info and student_info['group']:
                group_lower = student_info['group'].lower().strip()
                if group_lower not in cleaned_text_lower:
                    # Проверяем варианты написания группы尝试多种小组表示格式
                    group_variants = [
                        f"гр. {group_lower}",
                        f"группа {group_lower}",
                        f"№ {group_lower}",
                        group_lower
                    ]

                    found_group = False
                    for variant in group_variants:
                        if variant in cleaned_text_lower:
                            found_group = True
                            break

                    if not found_group:
                        errors.append("Неверная группа студента")

            # Проверка названия предмета检查课程名称
            subject_name = report_info['subject_name'].lower().strip()
            if subject_name not in cleaned_text_lower:
                # Проверяем без предлога "по курсу"尝试去除"по курсу:"前缀
                subject_clean = subject_name.replace("по курсу:", "").strip()
                if subject_clean and subject_clean not in cleaned_text_lower:
                    errors.append("Неправильное название предмета")
                    print(f"Не найдено название предмета: '{subject_name}'")

            # Проверка названия задания检查任务名称
            task_name = report_info['task_name'].lower().strip()
            if task_name not in cleaned_text_lower:
                # Проверяем варианты оформления尝试多种任务名称格式
                task_variants = [
                    f"задание {task_name}",
                    f"работа {task_name}",
                    task_name
                ]

                found_task = False
                for variant in task_variants:
                    if variant in cleaned_text_lower:
                        found_task = True
                        break

                if not found_task:
                    errors.append("Неверное название задания")
                    print(f"Не найдено название задания: '{task_name}'")

            # === 彻底优化的任务类型验证 ===
            task_type = report_info['task_type'].lower().strip()

            # 定义任务类型及其所有常见变体
            task_type_variants = {
                "лабораторная работа": [
                    "лабораторная работа", "лр", "лаба", "лабораторные работы",
                    "lab work", "laboratory work", "лабораторка"
                ],
                "практическое задание": [
                    "практическое задание", "пз", "практические задания",
                    "practical assignment", "практика", "задание",
                    "практикум", "практическое занятие", "практическая работа"  # 包含类似术语
                ],
                "практическая работа": [
                    "практическая работа", "пр", "практические работы",
                    "practical work"
                ],
                "курсовая работа": [
                    "курсовая работа", "кр", "курсовая", "курсовые работы",
                    "course work", "term paper"
                ],
                "дипломный проект": [
                    "дипломный проект", "диплом", "дипломная работа", "вкр",
                    "diploma project", "graduation project"
                ],
                "другое": []
            }

            # 创建统一的任务类型映射
            task_type_unified = {
                "практическое задание": "практическое задание",
                "практическая работа": "практическое задание",  # 统一两者
                "лабораторная работа": "лабораторная работа",
                "курсовая работа": "курсовая работа",
                "дипломный проект": "дипломный проект",
                "другое": "другое"
            }

            # 获取统一后的任务类型
            unified_task_type = task_type_unified.get(task_type, task_type)

            # 检查报告中是否存在该任务类型的任何变体
            found_task_type = False
            if unified_task_type in task_type_variants:
                for variant in task_type_variants[unified_task_type]:
                    if variant in cleaned_text_lower:
                        found_task_type = True
                        break

            if not found_task_type:
                # 尝试模糊匹配 拆分成单词
                task_type_words = re.split(r'\W+', unified_task_type)
                # 计算匹配的单词数
                found_words = 0
                for word in task_type_words:
                    if word and re.search(rf"\b{re.escape(word)}\b", cleaned_text_lower):
                        found_words += 1

                # 如果找到足够的关键词，认为匹配成功
                if found_words >= max(1, len(task_type_words) * 0.5):  # 至少匹配50%的关键词
                    found_task_type = True

            if not found_task_type:
                errors.append("Неверный тип задания")
                print(f"Не найден тип задания: '{unified_task_type}'")
                print(f"Искали варианты: {task_type_variants.get(unified_task_type, ['прямое совпадение'])}")

            # Проверка ФИО преподавателя检查教师姓名
            teacher = report_info['teacher']
            teacher_parts = [
                teacher['surname'].strip().lower(),
                teacher['name'].strip().lower()
            ]
            if teacher.get('patronymic'):
                teacher_parts.append(teacher['patronymic'].strip().lower())

            found_teacher = True
            for part in teacher_parts:
                if part and part not in cleaned_text_lower:
                    found_teacher = False
                    print(f"Отсутствует часть ФИО преподавателя: '{part}'")
                    break

            if not found_teacher:
                errors.append("Неверное ФИО преподавателя")

            # Проверка должности преподавателя检查教师职称
            teacher_status = teacher['status'].lower().strip()
            status_keywords = [
                "должность",
                "уч",
                "степень",
                "звание"
            ]

            found_status = True
            for keyword in status_keywords:
                if keyword not in cleaned_text_lower:
                    found_status = False
                    print(f"Отсутствует ключевое слово должности: '{keyword}'")
                    break

            if not found_status:
                errors.append("Неверная должность преподавателя")

            # Проверка года выполнения检查报告年份
            uploaded_at = datetime.fromisoformat(report_info['uploaded_at'].replace('Z', '+00:00'))
            year = str(uploaded_at.year)

            found_year = False
            if year in cleaned_text:
                found_year = True
            # 在字符级别检查年份（可能出现在扫描文档中）
            else:
                for char in first_page.chars:
                    if year in char['text']:
                        found_year = True
                        break

            if not found_year:
                errors.append(f"Неверный год выполнения отчета (ожидался {year})")
                print(f"Не найден год: '{year}'")

            # Проверка структуры отчета检查报告结构（从第二页开始）
            required_sections = report_info['report_structure']
            all_pages_text = ""

            # 提取所有后续页面的文本
            for page in pdf.pages[1:]:
                page_text = page.extract_text()
                if page_text:
                    cleaned_page_text = re.sub(r'\s+', ' ', page_text).strip()
                    all_pages_text += cleaned_page_text.lower() + " "

            # 检查必需部分
            missing_sections = []
            for section in required_sections:
                section_lower = section.lower().strip()

                section_pattern = r"\b" + re.escape(section_lower) + r"\b"

                # 精确匹配
                if re.search(section_pattern, all_pages_text):
                    continue

                # 尝试变体匹配
                section_variants = [
                    f"{section_lower} работы",
                    f"{section_lower} задания",
                    f"{section_lower}:"
                ]

                found_section = False
                for variant in section_variants:
                    variant_pattern = r"\b" + re.escape(variant) + r"\b"
                    if re.search(variant_pattern, all_pages_text):
                        found_section = True
                        break

                if not found_section:
                    missing_sections.append(section)
                    print(f"Не найден раздел: '{section}'")

            if missing_sections:
                errors.append(f"Отсутствуют обязательные разделы: {', '.join(missing_sections)}")

    except Exception as e:
        errors.append(f"Ошибка при обработке PDF: {str(e)}")

    return errors # 返回所有错误