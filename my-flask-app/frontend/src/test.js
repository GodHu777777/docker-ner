
import React, { useState } from 'react';
import axios from 'axios';
import LinearProgress from '@mui/material/LinearProgress';
import Button from '@mui/material/Button';

const ProgressBar = () => {
  const [progress, setProgress] = useState(0);

  const fetchData = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/predict', {
        onDownloadProgress: progressEvent => {
          const { loaded, total } = progressEvent;
          const percentCompleted = Math.round((loaded / total) * 100);
          console.log(Math.round((loaded / total) * 100) + '%')
          setProgress(percentCompleted);
        }
      });
      // 处理从后端返回的数据
    } catch (error) {
      // 处理错误
    }
  };

  return (
    <div>
       <Button variant="contained" color="primary" onClick={fetchData}>Fetch Data</Button>
      <LinearProgress variant="determinate" value={progress} />
    </div>
  );
};

const App = () => {
    return (
      <div>
        <h1>Fetch Data Progress</h1>
        <ProgressBar />
      </div>
    );
  };

export default App;