import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000'; // 后端API地址

export const validateReport = async (file, studentInfo, reportInfo) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('student_info', JSON.stringify(studentInfo));
  formData.append('report_info', JSON.stringify(reportInfo));

  try {
    const response = await axios.post(`${API_BASE_URL}/validate`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.error || '服务器返回错误');
    } else {
      throw new Error('无法连接到服务器');
    }
  }
};
