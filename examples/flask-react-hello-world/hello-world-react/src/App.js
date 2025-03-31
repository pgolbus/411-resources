import React, { useEffect, useState } from 'react';
import './App.css';

const apiUrl = process.env.REACT_APP_FLASK_API;
console.log("apiUrl: ", apiUrl);

function App() {
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetch(apiUrl)
      .then(response => response.json())
      .then(data => setMessage(data.message))
      .catch(error => console.error('Error fetching data: ', error));
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <p>{message || "Loading..."}</p>
      </header>
    </div>
  );
}

export default App;
