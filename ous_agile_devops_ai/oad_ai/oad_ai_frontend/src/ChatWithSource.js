import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

const ChatWithSource = () => {
    const { sourceName } = useParams();
    const navigate = useNavigate();
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');

    useEffect(() => {
        // Ensure new data loading for changed sourceName
    }, [sourceName]);

    const sendMessage = async () => {
        if (!input) return;

        const userMessage = {
            text: input,
            user: 'Me',
        };
        setMessages((prevMessages) => [...prevMessages, userMessage]);

        try {
            const response = await axios.post(`/chat-with-source/${sourceName}/`, {
                question: input,
                filters: JSON.stringify({}),
            });
            console.log('Received response from API:', response.data);
            let formattedContent = formatResponse(response.data.response.content);

            const botMessage = {
                text: formattedContent,
                user: 'Bot'
            };
            setMessages((prevMessages) => [...prevMessages, botMessage]);
        } catch (error) {
            console.error('Error sending message:', error);
            const errorMessage = {
                text: 'Sorry, an error occurred while processing your request.',
                user: 'Bot'
            };
            setMessages((prevMessages) => [...prevMessages, errorMessage]);
        } finally {
            setInput('');
        }
    };

    const formatResponse = (response) => {
        // Custom formatting logic
        response = response.replace(/\[(.*?)\]/g, '\n\n');
        response = response.replace(/(\w+)\.\n\n/g, '$1\n');
        response = response.replace(/\.\n\n/g, '.\n');
        response = response.replace(/^\s+|\s+$/g, '');
        response = response.replace(/^"|"$/g, '');
        response = response.replace(/\.\s+(\d+)\./g, '$1.');
        response = response.replace(/^\.\s*/gm, '');
        response = response.replace(/([^.\n])$/gm, '.');

        // Link and email formatting
        const linkRegex = /(https?:\/\/[^\s]+)/g;
        const urlRegex = /go\/([^\s]+)/g;
        const emailRegex = /([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)/g;

        response = response.replace(linkRegex, (match, url) => `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`);
        response = response.replace(urlRegex, (match, sometext) => `<a href="http://go/${sometext}" target="_blank" rel="noopener noreferrer">go/${sometext}</a>`);
        response = response.replace(emailRegex, (match, email) => `<a href="mailto:${email}">${email}</a>`);

        return response;
    };

    const copyToClipboard = (text) => {
        navigator.clipboard.writeText(text).then(() => {
            alert('Copied to clipboard!');
        }, (err) => {
            console.error('Failed to copy text: ', err);
        });
    };

    return (
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)' }}>
            <h2>Chat with Source: {sourceName}</h2>
            <div style={{ backgroundColor: '#f0f0f0', padding: '10px', minHeight: '300px', border: '1px solid #ccc', borderRadius: '4px', overflowY: 'auto' }}>
                {messages.map((message, index) => (
                    <div key={index} style={{ marginBottom: '10px', display: 'flex', alignItems: 'center' }}>
                        <strong>{message.user}:</strong>
                        <span dangerouslySetInnerHTML={{ __html: message.text }} style={{ flexGrow: 1, marginLeft: '10px' }} />
                        {message.user === 'Bot' && (
                            <button
                                style={{
                                    marginLeft: '10px',
                                    background: 'none',
                                    border: 'none',
                                    cursor: 'pointer',
                                    padding: '0'
                                }}
                                onClick={() => copyToClipboard(message.text)}
                            >
                                <img src="/copy-icon.png" alt="Copy" style={{ width: '20px', height: '20px' }} />
                            </button>
                        )}
                    </div>
                ))}
            </div>
            <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => (e.key === 'Enter' ? sendMessage() : null)}
                style={{ width: 'calc(100% - 20px)', padding: '10px', margin: '10px 0', borderRadius: '4px', border: '1px solid #ccc' }}
            />
            <button
                onClick={sendMessage}
                style={{
                    padding: '10px 20px',
                    backgroundColor: '#ff7f0e',  // Changed to orange color
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    marginRight: '10px'
                }}
            >
                Send
            </button>
            <button
                onClick={() => navigate('/sources')}
                style={{
                    padding: '10px 20px',
                    backgroundColor: '#6c757d',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                }}
            >
                Back to Sources
            </button>
        </div>
    );
};

export default ChatWithSource;
