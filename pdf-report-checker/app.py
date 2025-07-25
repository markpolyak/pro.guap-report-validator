from flask import Flask, render_template, request, redirect, url_for, send_file
from report_checker import check_report
import os
from datetime import datetime
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Создаем папку для загрузок, если ее нет创建上传目录
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

#处理根路径 / 的 GET 请求；渲染 index.html 模板（上传表单页面）
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/check', methods=['POST'])
def check():
    # Получаем данные формы获取上传的PDF文件
    pdf_file = request.files['report']
    # 获取学生信息
    student_info = {
        'name': request.form['student_name'],
        'surname': request.form['student_surname'],
        'patronymic': request.form.get('student_patronymic', ''),# 可选字段
        'group': request.form['student_group']
    }

    # 获取报告信息
    report_info = {
        'subject_name': request.form['subject_name'],
        'task_name': request.form['task_name'],
        'task_type': request.form['task_type'],
        'teacher': {
            'name': request.form['teacher_name'],
            'surname': request.form['teacher_surname'],
            'patronymic': request.form.get('teacher_patronymic', ''),# 可选字段
            'status': request.form['teacher_status']
        },
        # 将逗号分隔的结构转换为列表；添加时间部分使成为完整ISO格式
        'report_structure': [s.strip() for s in request.form['report_structure'].split(',')],
        'uploaded_at': request.form['uploaded_at'] + 'T00:00:00Z'  # 添加时间部分
    }

    # Сохраняем файл保存上传的文件
    filename = f"report_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    pdf_file.save(filepath)

    # Читаем файл как байты读取文件内容为字节
    with open(filepath, 'rb') as f:
        pdf_bytes = f.read()

    # Проверяем отчет调用检查函数
    errors = check_report(pdf_bytes, student_info, report_info)

    # Формируем результат构建结果对象
    result = {
        'filename': filename,# 保存的文件名
        'student_info': student_info,
        'report_info': report_info,
        'errors': errors,# 错误列表
        'is_valid': len(errors) == 0# 是否有效
    }

    # Сохраняем результат в сессии для отображения# 渲染结果页面
    return render_template('result.html', result=result)


@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)