import React, { useState } from 'react';
import { Container, Typography, Box, CssBaseline, CircularProgress, Snackbar, Alert } from '@mui/material';
import ReportUpload from './components/ReportUpload';
import StudentForm from './components/StudentForm';
import ReportForm from './components/ReportForm';
import ValidationResults from './components/ValidationResults';
import { validateReport } from './services/apiService';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [studentInfo, setStudentInfo] = useState({
    name: '',
    surname: '',
    patronymic: '',
    group: ''
  });
  const [reportInfo, setReportInfo] = useState({
    subject_name: '',
    task_name: '',
    task_type: '',
    teacher: {
      name: '',
      surname: '',
      patronymic: '',
      status: ''
    },
    report_structure: '',
    uploaded_at: new Date().toISOString().split('T')[0] + 'T00:00:00Z'
  });
  const [validationResults, setValidationResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // 唯一的 handleSubmit 函数
  const handleSubmit = async () => {
    if (!file) {
      setError('请上传报告文件');
      return;
    }

    // 检查文件大小（可选，但推荐）
    if (file.size < 1024) {
      setError('文件大小异常，可能为空文档');
      return;
    }

    try {
      setLoading(true);

      // 准备报告结构
      const reportData = {
        ...reportInfo,
        report_structure: reportInfo.report_structure
          ? reportInfo.report_structure.split(',').map(s => s.trim())
          : []
      };

      console.log("提交的请求数据:", {
        studentInfo,
        reportInfo: reportData,
        file: file.name
      });

      // 调用验证API
      const result = await validateReport(file, studentInfo, reportData);

      console.log("API响应结果:", result);

      // 使用新的响应结构
      setValidationResults(result.errors || []);

      if (result.valid) {
        setSuccess(`报告验证通过！文档统计: ${result.stats?.total_length || 0} 字符`);
      } else {
        setError(`报告验证失败，发现 ${result.error_count} 个问题`);
      }
    } catch (err) {
      console.error("验证请求失败:", err);
      setError(`验证失败: ${err.message}`);
      setValidationResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCloseSnackbar = () => {
    setError(null);
    setSuccess(null);
  };

  return (
    <Container maxWidth="md">
      <CssBaseline />
      <Box my={4}>
        <Typography variant="h4" align="center" gutterBottom>
          学生报告验证系统
        </Typography>
        <Typography variant="subtitle1" align="center" color="textSecondary" paragraph>
          上传DOCX报告文件并填写相关信息进行验证
        </Typography>

        <ReportUpload file={file} setFile={setFile} />
        <StudentForm studentInfo={studentInfo} setStudentInfo={setStudentInfo} />
        <ReportForm reportInfo={reportInfo} setReportInfo={setReportInfo} />

        <Box mt={4} display="flex" justifyContent="center">
          <button
            className="submit-button"
            onClick={handleSubmit}
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : '验证报告'}
          </button>
        </Box>

        {validationResults.length > 0 && (
          <ValidationResults results={validationResults} />
        )}
      </Box>

      <Snackbar open={!!error} autoHideDuration={6000} onClose={handleCloseSnackbar}>
        <Alert onClose={handleCloseSnackbar} severity="error" sx={{ width: '100%' }}>
          {error}
        </Alert>
      </Snackbar>

      <Snackbar open={!!success} autoHideDuration={3000} onClose={handleCloseSnackbar}>
        <Alert onClose={handleCloseSnackbar} severity="success" sx={{ width: '100%' }}>
          {success}
        </Alert>
      </Snackbar>
    </Container>
  );
}

export default App;
