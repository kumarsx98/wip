// Home.js
import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from './AuthContext';

function Home() {
  const { user } = useAuth();

  return (
    <div style={{
      backgroundColor: '#f4f4f4',
      color: '#333',
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      textAlign: 'center'
    }}>
      <h1>Welcome to the Chatbot App</h1>
      <p>Access the following components:</p>
      <ul style={{ listStyleType: 'none', padding: 0 }}>
        <li style={{ margin: '10px 0' }}>
          <Link to="/sources" style={{ color: '#007bff', textDecoration: 'none' }}>View All Sources</Link>
        </li>
        <li style={{ margin: '10px 0' }}>
          <Link to="/auto-upload" style={{ color: '#007bff', textDecoration: 'none' }}>
            Manage Auto-Uploads
          </Link>
        </li>
      </ul>
      {user ? (
        <p>Hello, {user.username}!</p>
      ) : (
        <p>Please <Link to="/login" style={{ color: '#007bff', textDecoration: 'none' }}>login</Link> for full access to app features.</p>
      )}
    </div>
  );
}

export default Home;