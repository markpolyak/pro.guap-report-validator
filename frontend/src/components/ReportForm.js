import React from 'react';
import { Box, Typography, TextField, Grid, Paper, InputAdornment } from '@mui/material';
import { Event as EventIcon } from '@mui/icons-material';

const ReportForm = ({ reportInfo, setReportInfo }) => {
  const handleChange = (field) => (e) => {
    setReportInfo({
      ...reportInfo,
      [field]: e.target.value
    });
  };

  const handleTeacherChange = (field) => (e) => {
    setReportInfo({
      ...reportInfo,
      teacher: {
        ...reportInfo.teacher,
        [field]: e.target.value
      }
    });
  };

  return (
    <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        报告信息
      </Typography>

      <Grid container spacing={2}>
        <Grid item xs={12}>
          <TextField
            label="科目名称"
            fullWidth
            value={reportInfo.subject_name}
            onChange={handleChange('subject_name')}
            variant="outlined"
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <TextField
            label="任务名称"
            fullWidth
            value={reportInfo.task_name}
            onChange={handleChange('task_name')}
            variant="outlined"
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <TextField
            label="任务类型"
            fullWidth
            value={reportInfo.task_type}
            onChange={handleChange('task_type')}
            variant="outlined"
          />
        </Grid>

        <Grid item xs={12}>
          <Typography variant="subtitle1" sx={{ mt: 2, mb: 1 }}>
            教师信息
          </Typography>
        </Grid>

        <Grid item xs={12} sm={4}>
          <TextField
            label="教师姓氏"
            fullWidth
            value={reportInfo.teacher.surname}
            onChange={handleTeacherChange('surname')}
            variant="outlined"
          />
        </Grid>
        <Grid item xs={12} sm={4}>
          <TextField
            label="教师名字"
            fullWidth
            value={reportInfo.teacher.name}
            onChange={handleTeacherChange('name')}
            variant="outlined"
          />
        </Grid>
        <Grid item xs={12} sm={4}>
          <TextField
            label="教师中间名"
            fullWidth
            value={reportInfo.teacher.patronymic}
            onChange={handleTeacherChange('patronymic')}
            variant="outlined"
          />
        </Grid>

        <Grid item xs={12}>
          <TextField
            label="教师职位/头衔"
            fullWidth
            value={reportInfo.teacher.status}
            onChange={handleTeacherChange('status')}
            variant="outlined"
          />
        </Grid>

        <Grid item xs={12}>
          <TextField
            label="报告结构 (用逗号分隔)"
            fullWidth
            value={reportInfo.report_structure}
            onChange={handleChange('report_structure')}
            variant="outlined"
            placeholder="例如: 引言,方法,结果,结论"
            helperText="报告应包含的章节标题"
          />
        </Grid>

        <Grid item xs={12}>
          <TextField
            label="上传日期"
            fullWidth
            type="datetime-local"
            value={reportInfo.uploaded_at.slice(0, 16)}
            onChange={(e) => {
              const date = new Date(e.target.value);
              setReportInfo({
                ...reportInfo,
                uploaded_at: date.toISOString()
              });
            }}
            variant="outlined"
            InputLabelProps={{ shrink: true }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <EventIcon />
                </InputAdornment>
              ),
            }}
          />
        </Grid>
      </Grid>
    </Paper>
  );
};

export default ReportForm;
