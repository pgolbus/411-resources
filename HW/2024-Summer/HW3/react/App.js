import React, { useState } from 'react';
import './App.css';

function App() {
  const initialBoard = Array(9).fill('');
  const [board, setBoard] = useState(initialBoard);
  const [playerTurn, setPlayerTurn] = useState('X');
  const [winner, setWinner] = useState(null);

  const flip = () => {
    setPlayerTurn(playerTurn === 'X' ? 'O' : 'X');
  };

  const checkWinner = (newBoard) => {
    const lines = [
      [0, 1, 2],
      [3, 4, 5],
      [6, 7, 8],
      [0, 3, 6],
      [1, 4, 7],
      [2, 5, 8],
      [0, 4, 8],
      [2, 4, 6],
    ];

    for (let line of lines) {
      const [a, b, c] = line;
      if (newBoard[a] && newBoard[a] === newBoard[b] && newBoard[a] === newBoard[c]) {
        return newBoard[a];
      }
    }

    return null;
  };

  const handleClick = (index) => {
    if (board[index] || winner) {
      return;
    }

    const newBoard = [...board];
    newBoard[index] = playerTurn;
    setBoard(newBoard);

    const gameWinner = checkWinner(newBoard);
    if (gameWinner) {
      setWinner(gameWinner);
    } else {
      flip();
    }
  };

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
