import React from 'react';
import { useNavigate } from 'react-router-dom';

function Login() {
  const navigate = useNavigate();

  const handleLogin = () => {
    // Redirect to Django's SAML login URL
    window.location.href = 'http://localhost:8001/saml2/login/';
  };

  return (
    <div>
      <h2>Login</h2>
      <button onClick={handleLogin}>Login with SAML</button>
    </div>
  );
}

export default Login;