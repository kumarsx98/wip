// src/ProtectedComponent.js

import React from 'react';
import { useAuth } from './AuthContext';

function ProtectedComponent() {
  const { user } = useAuth();

  return (
    <div>
      <h2>Protected Component</h2>
      <p>Hello, {user.username}! This is a protected area.</p>
    </div>
  );
}

export default ProtectedComponent;