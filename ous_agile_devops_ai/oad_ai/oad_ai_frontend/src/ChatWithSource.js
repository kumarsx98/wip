import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import Header from './Header';
import ConversationBox from './ConversationBox';
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

    useEffect(() => {
        // Add any additional useEffect actions if needed when sourceName changes
    }, [sourceName]);

    const sendMessage = async () => {
        if (!input) return;

        const userMessage = { text: input, sender: 'user' };
        setMessages((prevMessages) => [...prevMessages, userMessage]);
        setIsLoading(true);
        setShowSpinner(true);

        try {
            const response = await axios.post(`${baseURL}/chat-with-source/${sourceName}/`, {
                question: input,
                filters: JSON.stringify({}),
            });

            console.log('Received response from API:', response.data);
            let formattedContent = formatResponse(response.data.response.content);

            const botMessage = {
                text: formattedContent,
                sender: 'bot',
                copyButton: true,
                filenames: response.data.response.references ? response.data.response.references.map((ref) => ref.filename) : [],
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

        // Return the formatted response
        return response;
    };

    const handleSendMessage = (e) => {
        e.preventDefault();
        sendMessage();
    };

    const chatbotClassName = sourceName === 'public' ? 'Chatbot-public' : 'Chatbot-internal';
    const conversationBoxClassName = sourceName === 'public' ? 'conversation-box-public' : 'conversation-box-internal';

    return (
        <div className={`Chatbot ${chatbotClassName}`}>
            <Header title={`Chat with ${sourceName} Bot`} />
            <div className="source-name-container">
                <p>You are interacting with the <b>{sourceName}</b> source.</p>
            </div>
            <ConversationBox
                className={conversationBoxClassName}
                messages={messages}
                isLoading={isLoading}
                conversationBoxRef={conversationBoxRef}
                sourceName={sourceName} // Pass the source name to ConversationBox
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
