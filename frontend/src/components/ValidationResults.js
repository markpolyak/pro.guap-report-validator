import React from 'react';
import { Box, Typography, Paper, List, ListItem, ListItemIcon, ListItemText } from '@mui/material';
import { CheckCircle as CheckIcon, Error as ErrorIcon } from '@mui/icons-material';

const ValidationResults = ({ results }) => {
  if (results.length === 0) {
    return (
      <Paper elevation={3} sx={{ p: 3, mt: 3, backgroundColor: '#e8f5e9' }}>
        <Box display="flex" alignItems="center">
          <CheckIcon color="success" sx={{ fontSize: 40, mr: 2 }} />
          <Typography variant="h6">报告验证通过！所有检查项均符合要求</Typography>
        </Box>
      </Paper>
    );
  }

  return (
    <Paper elevation={3} sx={{ p: 3, mt: 3 }}>
      <Typography variant="h6" gutterBottom>
        验证结果
      </Typography>

      <List>
        {results.map((result, index) => (
          <ListItem key={index}>
            <ListItemIcon>
              <ErrorIcon color="error" />
            </ListItemIcon>
            <ListItemText primary={result} />
          </ListItem>
        ))}
      </List>
    </Paper>
  );
};

export default ValidationResults;
