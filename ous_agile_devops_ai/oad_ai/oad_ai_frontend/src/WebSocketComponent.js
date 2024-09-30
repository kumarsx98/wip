import React, { useEffect, useState } from 'react';

const WebSocketComponent = () => {
  const [message, setMessage] = useState('');

  useEffect(() => {
    const socket = new WebSocket('ws://oad-ai.abbvienet.com:3001/ws/some_path/');

    socket.onopen = () => {
      console.log('WebSocket connection established');
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('Received message from WebSocket:', data);
      setMessage(data.message);
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    socket.onclose = (event) => {
      console.log('WebSocket connection closed:', event);
    };

    return () => {
      if (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING) {
        socket.close();  // Close WebSocket connection when component unmounts
        console.log('WebSocket connection closed by the component');
      }
    };
  }, []);

  return (
    <div>
      <h1>WebSocket Message</h1>
      <p>{message}</p>
    </div>
  );
};

export default WebSocketComponent;
