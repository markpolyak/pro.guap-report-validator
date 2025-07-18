// script.js - 简单的交互功能

document.addEventListener('DOMContentLoaded', function() {
    // 添加日期字段自动填充
    const dateField = document.querySelector('input[name="uploaded_at"]');
    if (dateField && !dateField.value) {
        const today = new Date();
        const formattedDate = today.toISOString().split('T')[0];
        dateField.value = formattedDate;
    }

    // 添加报告结构帮助提示
    const structureField = document.querySelector('textarea[name="report_structure"]');
    if (structureField) {
        structureField.addEventListener('focus', function() {
            if (!this.value.trim()) {
                this.value = "Цель, Задание, Результат выполнения, Выходы";
            }
        });

        structureField.addEventListener('blur', function() {
            if (this.value === "Цель, Задание, Результат выполнения, Выходы") {
                this.value = this.value;
            }
        });
    }

    // 添加表单提交时的加载指示器
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function() {
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Проверка...';
            }
        });
    }
});