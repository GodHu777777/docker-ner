import React, {useEffect, useState} from 'react';
import axios from 'axios';
import LinearProgress from '@mui/material/LinearProgress';
import Button from '@mui/material/Button';

const Train = () =>{
  //抓数据
  const [selectList, setSelectList] = useState([])
  useEffect(()=>{
    async function getList(){
      const list = await axios.get("http://localhost:3004/list")
      setSelectList(list.data)
    }
    getList()
  },[])

  //发数据
  const [selectedOption, setSelectedOption] = useState('');
  const handleChange = (event) => {
    setSelectedOption(event.target.value);
  };
  const handleSubmit = (event) => {
    event.preventDefault();
    // 在这里使用 Axios 发送 POST 请求
    axios.post('/training', { selectedOption })
      .then(response => {
        alert('Training');
      })
      .catch(error => {
        console.error('There was a problem with your Axios operation:', error);
      });
  };

  //进度条
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


  return(
    <div>
    <h3>Model Training</h3>
    <form method='POST'  onSubmit={handleSubmit}>
      <label>model:</label>
      <select value={selectedOption} onChange={handleChange}> 
        {selectList.map(item=><option id={item.id}>{item.name}</option>)}
      </select>
      <label>dataset:</label>
      <select>
        {selectList.map(item=><option id={item.id}>{item.dataset}</option>)}
      </select>
      <Button size="small" variant="contained"  type='submit'>Train</Button>
      {/* <LinearProgress variant="determinate" value={progress} /> */}
    </form>
  </div>

  )
}

const Predict = () =>{
  //发数据并接受前端传来的数据

  //设置输入文本状态
  const [inputValue, setInputValue] = useState('');
  //设置后端返回数据状态
  const [responseData, setResponseData] = useState(null);
  //设置错误状态
  const [error, setError] = useState(null);

  //保持input文本框的状态
  const handleChange = (event) => {
    setInputValue(event.target.value);
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    // 在这里使用 Axios 发送 POST 请求，将输入框中的值发送到后端
    axios.post('/predict', { inputValue })
      .then(response => {
        console.log('Data sent successfully!');
        // 在这里处理成功的响应并设置状态
        setResponseData(response.data);
        setError(null); // 清除可能存在的错误
      })
      .catch(error => {
        console.error('There was a problem with your Axios operation:', error);
        setError('There was a problem with your Axios operation'); // 设置错误状态
        setResponseData(null); // 清除可能存在的数据
      });
  };

  return(
    <div>
      <h3>Model Predict</h3>
        <form method="POST" onSubmit={handleSubmit}>
          <label>String:</label>
          <input type='text'  onChange={handleChange}></input>
          <Button size="small" variant="contained" type='submit'>Predict</Button>
        </form>
      {error && <div>Error: {error}</div>}
      {responseData && (
        <div>
          <h2>Response from server:</h2>
          <p>{responseData}</p> 
        </div>
      )}
      <p></p>  
    </div>
  )
}

const Evaluation = ()=>{
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const handleClick = () =>{
    axios.get('/evalution')
      .then(response => {
        console.log('Data fetched successfully:', response.data);
        setData(response.data); // 设置数据状态
        setError(null); // 清除可能存在的错误
      })
      .catch(error => {
        console.error('There was a problem with your Axios operation:', error);
        setError('There was a problem with your Axios operation'); // 设置错误状态
        setData(null); // 清除可能存在的数据
      });
  }
  return(
    <div>
      <h3>Model Evaluation</h3>
      <Button size="small" variant="contained" onClick={handleClick}>Predict</Button>
      {error && <div>Error: {error}</div>}
      {data && (
        <div>
          <h2>Data from server:</h2>
          <p>{data}</p> {/* 这里假设后端返回的是文本数据 */}
        </div>
      )}
    </div>
  )
}
{/* /* 
    <div>
      <h3>模型评估</h3>
        <button onClick={() => setEflag(1)}>
          模型评估
        </button>
        {eflag &&  <p>模型评估结果为</p>}
    </div> */ }

const App = () => {
  return (
    <> 
    <Train />
    <Predict/>
    <Evaluation/>
    </>
  );
};

export default App;
