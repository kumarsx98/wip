import React from 'react';
import CopyButton from './CopyButton';

function createMarkup(html) {
  return { __html: html };
}

function Message({ message, isLoading, index, messages, source }) {
  const messageClass = `message ${message.sender === 'user' ? 'user' : 'bot'} ${source}`;

  return (
    <div className={messageClass}>
      {message.text.trim().split('\n\n').map((line, i) => (
        <p key={i} dangerouslySetInnerHTML={createMarkup(line.trim())}></p>
      ))}
      {message.sender === 'bot' && message.copyButton && (
        <div>
          {message.filenames && message.filenames.length > 0 && (
            <p className="filenames">
              Found in: {message.filenames.join(', ')}
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
