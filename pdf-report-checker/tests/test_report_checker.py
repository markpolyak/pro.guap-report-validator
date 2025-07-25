import unittest
from report_checker import check_report
import os


class TestReportChecker(unittest.TestCase):
    def setUp(self):
        self.correct_pdf_path = os.path.join(os.path.dirname(__file__), 'test_data', 'correct_report.pdf')
        self.incorrect_pdf_path = os.path.join(os.path.dirname(__file__), 'test_data', 'incorrect_report.pdf')

        self.student_info = {
            'name': 'Ху',
            'surname': 'Чунь',
            'group': '4233K'
        }

        self.report_info = {
            'subject_name': 'Основы машинного обучения',
            'task_name': 'ЛР3. Алгоритмы классификации',
            'task_type': 'Практическая работа',
            'teacher': {
                'name': 'Поляк',
                'surname': 'Марк',
                'patronymic': 'Дмитриевич',
                'status': 'должность,уч.степень,звание'
            },
            'report_structure': ['Цель', 'Задание', 'Выход'],
            'uploaded_at': '2025-06-01T00:00:00Z'
        }

    def test_correct_report(self):
        with open(self.correct_pdf_path, 'rb') as f:
            pdf_bytes = f.read()

        errors = check_report(pdf_bytes, self.student_info, self.report_info)
        self.assertEqual(len(errors), 0, f"Ожидалось 0 ошибок, но найдено: {errors}")

    def test_incorrect_report(self):
        with open(self.incorrect_pdf_path, 'rb') as f:
            pdf_bytes = f.read()

        errors = check_report(pdf_bytes, self.student_info, self.report_info)
        self.assertGreater(len(errors), 0, "Ожидались ошибки, но их нет")


if __name__ == '__main__':
    unittest.main()