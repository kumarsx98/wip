import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from './AuthContext';

function Navigation() {
  const { user, logout } = useAuth();

  return (
    <nav>
      <ul>
        <li><Link to="/">Home</Link></li>
        <li><Link to="/sources">View All Sources</Link></li>
        {/* Conditionally render these links based on user authentication */}
        {user && (
          <>
            <li><Link to="/create-source">Create a New Source</Link></li>
            <li><Link to="/auto-upload">Manage Auto-Uploads</Link></li>
          </>
        )}
        {user ? (
          <>
            <li style={{ color: 'yellow' }} role="img" aria-label="Star">🌟 Your login was successful! 🌟</li> {/* Make text yellow */}
            <li><button onClick={logout}>Logout</button></li>
          </>
        ) : (
          <li><Link to="/login">Login</Link></li>
        )}
      </ul>
    </nav>
  );
}

export default Navigation;
