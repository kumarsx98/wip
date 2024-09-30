import React from 'react';

function Login() {
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
