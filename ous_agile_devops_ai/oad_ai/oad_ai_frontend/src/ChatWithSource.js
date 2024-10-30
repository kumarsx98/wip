import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import Header from './Header';
import ConversationBox from './ConversationBox'; // Import the ConversationBox component
import InputBox from './InputBox';
import './App.css';

//const baseURL = 'http://localhost:8001'; // Define your backend base URL here
const baseURL = 'http://oad-ai.abbvienet.com:8001';


const ChatWithSource = () => {
  const { sourceName } = useParams();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showSpinner, setShowSpinner] = useState(false);
  const conversationBoxRef = useRef(null);

  useEffect(() => {
    if (conversationBoxRef.current) {
      conversationBoxRef.current.scrollTop = conversationBoxRef.current.scrollHeight;
    }
  }, [messages]);

  const sendMessage = async () => {
    if (!input) return;

    const userMessage = { text: input, sender: 'user' };
    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setIsLoading(true);
    setShowSpinner(true);

    try {
      const response = await axios.post(`${baseURL}/chat-with-source/${sourceName}/`, {
        question: input,
        filters: JSON.stringify({}),
        history: updatedMessages.map((msg) => ({
          role: msg.sender === 'user' ? 'user' : 'assistant',
          content: msg.text,
        })),
      });

      console.log('Received response from API:', response.data);

      let responseContent = response.data.response.content;
      if (response.data.error) {
        responseContent = response.data.error;
      }

      const formattedReferences = response.data.response.references ? response.data.response.references.map((ref) => {
        // Use sourceName from the URL and filename to construct the preview URL
        const source = sourceName;
        const filename = ref.filename || 'undefined';

        console.log(`Source: ${source}, Filename: ${filename}`);

        // Encode the source#filename for the URL
        const previewURL = `${baseURL}/media/previews/${encodeURIComponent(`${source}#${filename}`)}`;
        console.log(`Formatted URL: ${previewURL}`); // Log the formatted URL

        return {
          ...ref,
          preview_url: previewURL,
        };
      }) : [];

      const botMessage = {
        text: formatResponse(responseContent),
        sender: 'bot',
        copyButton: true,
        filenames: formattedReferences.map((ref) => ref.filename),
        references: formattedReferences,
      };

      setMessages((prevMessages) => [...prevMessages, botMessage]);

    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        text: 'Sorry, an error occurred while processing your request.',
        sender: 'bot',
        copyButton: false,
      };
      setMessages((prevMessages) => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
      setShowSpinner(false);
      setInput('');
    }
  };

  const formatResponse = (response) => {
    response = response.replace(/\[(.*?)\]/g, '\n\n');
    response = response.replace(/(\w+)\.\n\n/g, '$1\n');
    response = response.replace(/\.\n\n/g, '.\n');
    response = response.replace(/^\s+|\s+$/g, '');
    response = response.replace(/^"|"$/g, '');
    response = response.replace(/\.\s+(\d+)\./g, '$1.');
    response = response.replace(/^\.\s*/gm, '');
    response = response.replace(/([^.\n])$/gm, '.');

    const linkRegex = /(https?:\/\/[^\s]+)/g;
    const urlRegex = /go\/([^\s]+)/g;
    const emailRegex = /([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)/g;

    response = response.replace(linkRegex, (match, url) =>
        `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`);
    response = response.replace(urlRegex, (match, sometext) =>
        `<a href="http://go/${sometext}" target="_blank" rel="noopener noreferrer">go/${sometext}</a>`);
    response = response.replace(emailRegex, (match, email) =>
        `<a href="mailto:${email}">${email}</a>`);

    return response;
  };

  const handleSendMessage = (e) => {
    e.preventDefault();
    sendMessage();
  };

  return (
    <div className="Chatbot">
      <Header title={`Chat with ${sourceName} Bot`} />
      <ConversationBox
        messages={messages}
        isLoading={isLoading}
        conversationBoxRef={conversationBoxRef}
        sourceName={sourceName}
      />
      <InputBox
        question={input}
        setQuestion={setInput}
        handleSendMessage={handleSendMessage}
        isLoading={isLoading}
        showSpinner={showSpinner}
      />
    </div>
  );
};

export default ChatWithSource;
