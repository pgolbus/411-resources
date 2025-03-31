import React, { useCallback, useEffect, useState } from 'react';
import axios from 'axios';
import './App.css';

const URL = process.env.REACT_APP_FLASK_API;
console.log("apiUrl: ", URL);

axios.get(`${URL}/healthcheck`)
  .then(response => {
    console.log('Health check response:', response.data);
  })
  .catch(error => {
    console.error('Health check failed:', error);
  });

function App() {
  const initialBoard = Array(9).fill('');
  const [board, setBoard] = useState(initialBoard);
  const [winner, setWinner] = useState(null);

  /**
   * Fetches the current board state from the server.
   */
  const fetchBoard = useCallback(() => {
    console.log('Fetching board state from server...');
    axios.get(`${URL}/board`)
      .then(response => {
        console.log('Board state fetched:', response.data.board);
        setBoard(response.data.board);
      })
      .catch(error => {
        console.error('Error fetching board:', error);
      });
  }, []);

  /**
   * Checks if there is a winner.
   */
  const checkWinner = useCallback(() => {
    console.log('Checking for a winner...');
    axios.get(`${URL}/check_winner`)
      .then(response => {
        if (response.data.winner) {
          console.log(`Player ${response.data.winner} wins!`);
          setWinner(response.data.winner);
        } else {
          console.log('No winner yet.');
        }
      })
      .catch(error => {
        console.error('Error checking winner:', error);
      });
  }, []);

  /**
   * Handles the click event for a cell.
   * @param {number} index - The index of the clicked cell.
   */
  const handleClick = (index) => {
    console.log(`Cell ${index} clicked.`);
    if (winner) {
      console.log('Game already has a winner.');
      return;
    }
    if (board[index]) {
      console.log('Cell already occupied.');
      window.alert('Cell already occupied');
      return;
    }

    console.log('Making move on the server...');
    axios.post(`${URL}/move`, { index })
      .then(response => {
        console.log('Move made:', response.data.board);
        const newBoard = response.data.board;
        setBoard(newBoard);
        checkWinner();
      })
      .catch(error => {
        // Handle error response
        if (error.response && error.response.data && error.response.data.error) {
          if (error.response.data.error === "Square already occupied") {
            console.error('Square already occupied', error.response.data.error);
            window.alert('Square already occupied. Try again.');
          } else {
            console.error('Other error occurred:', error.response.data.error);
            // Handle other errors
          }
        }
        console.error('Error making move:', error);
      });
  };

  // Fetch the initial board state when the component mounts
  useEffect(() => {
    fetchBoard();
  }, [fetchBoard]);

  /**
   * Renders a cell of the Tic Tac Toe board.
   * @param {number} index - The index of the cell to render.
   * @returns {JSX.Element} The cell element.
   */
  const renderCell = (index) => {
    return (
      <div className="square" onClick={() => handleClick(index)}>
        {board[index]}
      </div>
    );
  };

  return (
    <div className="App">
      <h1>Tic Tac Toe</h1>
      <div className="board">
        {board.map((cell, index) => (
          <div key={index} className="cell">
            {renderCell(index)}
          </div>
        ))}
      </div>
      {winner && <h2>Player {winner} wins!</h2>}
    </div>
  );
}

export default App;
