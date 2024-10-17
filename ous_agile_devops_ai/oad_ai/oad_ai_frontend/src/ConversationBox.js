import React, { useState, useEffect } from 'react';
import CopyButton from './CopyButton';
import axios from 'axios';

//const baseURL = 'http://localhost:8001'; // Define your backend base URL here
const baseURL = 'http://oad-ai.abbvienet.com:8001';

function createMarkup(html) {
  return { __html: html };
}

const checkFileExists = async (url) => {
  try {
    const response = await axios.head(url);
    return response.status === 200;
  } catch (error) {
    return false;
  }
};

function Message({ message, isLoading, index, messages, source }) {
  const messageClass = `message ${message.sender === 'user' ? 'user' : 'bot'} ${source}`;
  const [fileStatus, setFileStatus] = useState({});

  useEffect(() => {
    const checkFiles = async () => {
      const status = {};
      for (const filename of message.filenames) {
        const url = `${baseURL}/media/previews/${encodeURIComponent(filename)}`;
        const exists = await checkFileExists(url);
        status[filename] = exists;
      }
      setFileStatus(status);
    };

    if (message.filenames && message.filenames.length > 0) {
      checkFiles();
    }
  }, [message.filenames]);

  return (
    <div className={messageClass}>
      {message.text.trim().split('\n\n').map((line, i) => (
        <p key={i} dangerouslySetInnerHTML={createMarkup(line.trim())}></p>
      ))}
      {message.sender === 'bot' && message.copyButton && (
        <div>
          {message.filenames && message.filenames.length > 0 && (
            <p className="filenames">
              Found in: {message.filenames.map((filename, i) => (
                fileStatus[filename] ?
                <a key={i} href={`${baseURL}/media/previews/${encodeURIComponent(filename)}`} target="_blank" rel="noopener noreferrer">{filename}</a> :
                <span key={i}>{filename} (File preview is not available)</span>
              ))}
            </p>
          )}
          <CopyButton text={message.text} />
        </div>
      )}
      {isLoading && index === messages.length - 1 && (
        <div className="spinner spinner-conversation"></div>
      )}
    </div>
  );
}

function ConversationBox({ messages, isLoading, conversationBoxRef, className }) {
  return (
    <div className={`conversation-box ${className}`} ref={conversationBoxRef}>
      {messages.map((message, index) => (
        <Message
          key={index}
          message={message}
          isLoading={isLoading}
          index={index}
          messages={messages}
          source={className}
        />
      ))}
    </div>
  );
}

export default ConversationBox;
