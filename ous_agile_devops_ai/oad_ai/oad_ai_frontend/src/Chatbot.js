import React, { useState, useRef, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import api from './api';  // Import the custom Axios instance
import Header from './Header';
import ConversationBox from './ConversationBox';
import InputBox from './InputBox';
import './App.css';

function Chatbot() {
  const { mysource } = useParams();
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showSpinner, setShowSpinner] = useState(false);
  const [question, setQuestion] = useState('');
  const conversationBoxRef = useRef(null);

  useEffect(() => {
    if (conversationBoxRef.current) {
      conversationBoxRef.current.scrollTop = conversationBoxRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    const message = e.target.message.value.trim();

    if (message !== '') {
      setIsLoading(true);
      setShowSpinner(true);
      setMessages(prevMessages => [...prevMessages, { text: message, sender: 'user' }]);
      setQuestion('');

      try {
        // Use the custom api instance here
        const resp = await api.post('/chatbot1/search/', { question: message, mysource });
        console.log('Received response from API:', resp.data);

        let response = resp.data.response.content;
        response = response.replace(/\[(.*?)\]/g, '\n\n');
        response = response.replace(/(\w+)\.\n\n/g, '$1\n');
        response = response.replace(/\.\n\n/g, '.\n');
        response = response.replace(/^\s+|\s+$/g, '');
        response = response.replace(/^"|"$/g, '');
        response = response.replace(/\.\s+(\d+)\./g, '$1.');
        response = response.replace(/^\.\s*/gm, '');
        response = response.replace(/([^.\n])$/gm, '.');

        const linkRegex = /(https?:\/\/[^\s]+)/g;
        response = response.replace(linkRegex, (match, url) => {
          return `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`;
        });

        const urlRegex = /go\/([^\s]+)/g;
        response = response.replace(urlRegex, (match, sometext) => {
          const href = `http://go/${sometext}`;
          return `<a href="${href}" target="_blank" rel="noopener noreferrer">go/${sometext}</a>`;
        });

        const emailRegex = /([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)/g;
        response = response.replace(emailRegex, (match, email) => {
          const href = `mailto:${email}`;
          return `<a href="${href}">${email}</a>`;
        });

        setMessages(prevMessages => [
          ...prevMessages,
          {
            text: response,
            sender: 'bot',
            copyButton: true,
            filenames: resp.data.response.references ? resp.data.response.references.map((ref) => ref.filename) : [],
          },
        ]);

      } catch (error) {
        console.error('Error occurred during API request:', error);
        setMessages(prevMessages => [
          ...prevMessages,
          {
            text: 'Sorry, an error occurred while processing your request.',
            sender: 'bot',
            copyButton: false,
          },
        ]);
      } finally {
        setIsLoading(false);
        setShowSpinner(false);
      }
    }
  };

  const chatbotClassName = mysource === 'public' ? 'Chatbot-public' : 'Chatbot-internal';
  const conversationBoxClassName = mysource === 'public' ? 'conversation-box-public' : 'conversation-box-internal';

  return (
    <div className={`Chatbot ${chatbotClassName}`}>
      <Header />
      <ConversationBox
        className={conversationBoxClassName}
        messages={messages}
        isLoading={isLoading}
        conversationBoxRef={conversationBoxRef}
      />
      <InputBox
        question={question}
        setQuestion={setQuestion}
        handleSendMessage={handleSendMessage}
        isLoading={isLoading}
        showSpinner={showSpinner}
      />
    </div>
  );
}

export default Chatbot;