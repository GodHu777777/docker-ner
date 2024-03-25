import React, {useEffect, useState} from 'react';
import axios from 'axios';
import LinearProgress from '@mui/material/LinearProgress';
import Button from '@mui/material/Button';

const Train = () =>{
  const [selectList, setSelectList] = useState([])
  useEffect(()=>{
    async function getList(){
      const list = await axios.get("http://localhost:3004/list")
      setSelectList(list.data)
    }
    getList()
  },[])

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
    <form method='post'>
      <label>model:</label>
      <select>
        {selectList.map(item=><option id={item.id}>{item.name}</option>)}
      </select>
      <label>dataset:</label>
      <select>
        {selectList.map(item=><option id={item.id}>{item.dataset}</option>)}
      </select>
      <Button variant="contained" color="primary" onClick={fetchData} type='submit'>Fetch Data</Button>
      {/* <LinearProgress variant="determinate" value={progress} /> */}
    </form>
  </div>

  )
}

{/* /* <div>
      <h3>输入字符串：</h3>
      <form method="GET">
        <input  value={content} onChange={(e) => setContent(e.target.value)}></input>
      </form>
      <button onClick={()=> setPflag(true)}>提交</button>
      {pflag && <p>{content}:的结果是</p>}
    </div>
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
    </>
  );
};

export default App;
