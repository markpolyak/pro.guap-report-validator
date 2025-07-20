import os
import json
import uuid
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from backend.validator.report_validator import ReportValidator

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('validator.log')
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # 允许跨域

# 创建临时上传目录
UPLOAD_FOLDER = 'temp_uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/')
def home():
    """根路由，提供简单的服务状态信息"""
    return jsonify({
        "status": "running",
        "service": "Student Report Validator API",
        "version": "1.0",
        "endpoints": {
            "POST /validate": "Validate student report"
        }
    })


@app.route('/status')
def status():
    """服务状态检查端点"""
    return jsonify({"status": "ok", "message": "Service is running"})


@app.route('/validate', methods=['POST'])
def validate_report():
    """验证学生报告的主端点"""
    # 检查文件
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if not file.filename.endswith('.docx'):
        return jsonify({"error": "File must be a .docx"}), 400

    # 获取其他表单数据
    student_info = request.form.get('student_info')
    report_info = request.form.get('report_info')
    if not student_info or not report_info:
        return jsonify({"error": "Missing student_info or report_info"}), 400

    try:
        student_info = json.loads(student_info)
        report_info = json.loads(report_info)
    except json.JSONDecodeError as e:
        logger.error(f"JSON解析错误: {str(e)}")
        return jsonify({"error": f"Invalid JSON: {str(e)}"}), 400

    # 保存文件到临时位置
    temp_filename = os.path.join(UPLOAD_FOLDER, str(uuid.uuid4()) + '.docx')
    file.save(temp_filename)

    logger.info(f"开始验证报告: {file.filename}")
    logger.info(f"学生信息: {json.dumps(student_info, ensure_ascii=False)}")
    logger.info(f"报告信息: {json.dumps(report_info, ensure_ascii=False)}")

    try:
        with open(temp_filename, 'rb') as f:
            docx_bytes = f.read()

        validator = ReportValidator(docx_bytes, student_info, report_info)
        errors = validator.validate()

        # 添加额外统计信息
        stats = {
            "title_page_length": len(validator.title_page_text),
            "body_length": len(validator.body_text),
            "total_length": len(validator.title_page_text) + len(validator.body_text)
        }

        logger.info(f"验证完成, 发现 {len(errors)} 个错误")
        logger.debug(f"错误列表: {errors}")

        return jsonify({
            "valid": len(errors) == 0,
            "errors": errors,
            "error_count": len(errors),
            "stats": stats
        })
    except Exception as e:
        logger.exception(f"验证过程中发生错误: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        # 清理临时文件
        if os.path.exists(temp_filename):
            try:
                os.remove(temp_filename)
                logger.debug(f"已删除临时文件: {temp_filename}")
            except Exception as e:
                logger.warning(f"无法删除临时文件: {str(e)}")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
