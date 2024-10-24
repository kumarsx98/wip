import React from 'react';

const baseURL = 'http://localhost:8001'; // Define your backend base URL here
//const baseURL = 'http://oad-ai.abbvienet.com:8001';

function Login() {
  const handleLogin = () => {
    // Redirect to Django's SAML login URL
    window.location.href = `${baseURL}/saml2/login/`;
  };

  return (
    <div>
      <h2>Login</h2>
      <button onClick={handleLogin}>Login with SAML</button>
    </div>
  );
}

export default Login;
