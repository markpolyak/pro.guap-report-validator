import React from 'react';
import { Box, Typography, Paper } from '@mui/material';
import { useDropzone } from 'react-dropzone';
import { Upload as UploadIcon } from '@mui/icons-material';

const ReportUpload = ({ file, setFile }) => {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    onDrop: acceptedFiles => {
      if (acceptedFiles && acceptedFiles.length > 0) {
        setFile(acceptedFiles[0]);
      }
    }
  });

  return (
    <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        上传报告文件
      </Typography>

      <Box
        {...getRootProps()}
        sx={{
          border: '2px dashed #ccc',
          borderRadius: '4px',
          p: 4,
          textAlign: 'center',
          backgroundColor: isDragActive ? '#f0f7ff' : '#fafafa',
          cursor: 'pointer',
          transition: 'background-color 0.2s'
        }}
      >
        <input {...getInputProps()} />
        <UploadIcon fontSize="large" sx={{ color: '#666', mb: 1 }} />
        <Typography variant="body1">
          {isDragActive
            ? '将文件拖放到此处...'
            : file
              ? `已选择文件: ${file.name}`
              : '拖放DOCX文件到此处，或点击选择文件'
          }
        </Typography>
        <Typography variant="body2" color="textSecondary" mt={1}>
          仅支持DOCX格式文件
        </Typography>
      </Box>
    </Paper>
  );
};

export default ReportUpload;
