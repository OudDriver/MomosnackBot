import React, { useState, useEffect, useRef } from 'react';
import io from 'socket.io-client';
import './App.css';

const socket = io();

function App() {
  const [leaderboard, setLeaderboard] = useState([]);
  const prevLeaderboard = useRef(leaderboard); // Store the previous leaderboard

  useEffect(() => {
    fetch('/initial-messages')
      .then(response => response.json())
      .then(data => setLeaderboard(data))
      .catch(error => console.error('Error fetching initial leaderboard:', error));
  }, []);

  useEffect(() => {
    socket.on('leaderboard_update', (newLeaderboard) => {
      setLeaderboard(newLeaderboard);
    });
  }, []);

  // Animation Logic
  useEffect(() => {
    // Compare the current and previous leaderboards
    const changes = leaderboard.map((entry, index) => {
      const prevEntry = prevLeaderboard.current.find(e => e.author === entry.author);
      if (prevEntry && prevEntry.amount !== entry.amount) {
        return { index, type: 'amount-change' };
      } else if (index !== prevLeaderboard.current.findIndex(e => e.author === entry.author)) {
        return { index, type: 'position-change' };
      }
      return null;
    }).filter(change => change !== null);

    // Apply animations based on changes
    changes.forEach(change => {
      const listItem = document.querySelector(`.message-list li:nth-child(${change.index + 1})`);
      if (listItem) {
        if (change.type === 'amount-change') {
          listItem.classList.add('amount-changed');
          setTimeout(() => {
            listItem.classList.remove('amount-changed');
          }, 1000); // Remove the class after the animation
        } else if (change.type === 'position-change') {
          listItem.classList.add('position-changed');
          setTimeout(() => {
            listItem.classList.remove('position-changed');
          }, 1000); // Remove the class after the animation
        }
      }
    });

    // Update the previous leaderboard
    prevLeaderboard.current = leaderboard;
  }, [leaderboard]);

  return (
    <div className="container">
      <h1 className="title">Momosnacks Leaderboard</h1>
      <ul className="message-list">
        {leaderboard.map((entry, index) => (
          <li key={index} className="message-item">
            <span className="author">{entry.author}:</span>
            <span className="amount"> {entry.amount} momosnacks(s) </span>
            <span className="timestamp">{entry.latestTimeStamp}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;