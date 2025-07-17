import React from 'react';
import { Box, Typography, TextField, Grid, Paper } from '@mui/material';

const StudentForm = ({ studentInfo, setStudentInfo }) => {
  const handleChange = (field) => (e) => {
    setStudentInfo({
      ...studentInfo,
      [field]: e.target.value
    });
  };

  return (
    <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        学生信息
      </Typography>

      <Grid container spacing={2}>
        <Grid item xs={12} sm={4}>
          <TextField
            label="姓氏"
            fullWidth
            value={studentInfo.surname}
            onChange={handleChange('surname')}
            variant="outlined"
          />
        </Grid>
        <Grid item xs={12} sm={4}>
          <TextField
            label="名字"
            fullWidth
            value={studentInfo.name}
            onChange={handleChange('name')}
            variant="outlined"
          />
        </Grid>
        <Grid item xs={12} sm={4}>
          <TextField
            label="中间名"
            fullWidth
            value={studentInfo.patronymic}
            onChange={handleChange('patronymic')}
            variant="outlined"
          />
        </Grid>
        <Grid item xs={12}>
          <TextField
            label="组别"
            fullWidth
            value={studentInfo.group}
            onChange={handleChange('group')}
            variant="outlined"
          />
        </Grid>
      </Grid>
    </Paper>
  );
};

export default StudentForm;
