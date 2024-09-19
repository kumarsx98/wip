import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from './AuthContext';

function Navigation({ sources = [] }) {
  const { user, logout } = useAuth();

  return (
    <nav>
      <ul>
        <li><Link to="/">Home</Link></li>
        {user ? (
          <>
            <li>{user.username}</li>
            <li><button onClick={logout}>Logout</button></li>
            {sources.map((source, index) => (
              <li key={index}>
                <a href={`/chat-with-source/${source}`} target="_blank" rel="noopener noreferrer">Chat with {source}</a>
              </li>
            ))}
          </>
        ) : (
          <li><Link to="/login">Login</Link></li>
        )}
      </ul>
    </nav>
  );
}

export default Navigation;
