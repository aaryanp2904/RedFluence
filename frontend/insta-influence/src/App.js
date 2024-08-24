import React, { useEffect, useState } from 'react';
import './App.css';

function App() {
  const [data, setData] = useState(null);
  const [postResponse, setPostResponse] = useState(null);

  useEffect(() => {
    // GET request to Flask API
    fetch('http://127.0.0.1:5000/api/data')
      .then(response => response.json())
      .then(data => setData(data));
  }, []);

  const handlePost = () => {
    // POST request to Flask API
    fetch('http://127.0.0.1:5000/api/post', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ userInput: 'Example Data' }),
    })
      .then(response => response.json())
      .then(data => setPostResponse(data));
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Flask and React Integration</h1>
        {data ? <p>{data.message}</p> : <p>Loading...</p>}
        <button onClick={handlePost}>Send POST Request</button>
        {postResponse && <p>{postResponse.message}</p>}
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
      </header>
    </div>
  );
}

export default App;
