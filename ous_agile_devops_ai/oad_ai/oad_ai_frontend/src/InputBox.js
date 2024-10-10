import React from 'react';

function InputBox({ question, setQuestion, handleSendMessage, isLoading, showSpinner }) {
  return (
    <form className="input-container" onSubmit={handleSendMessage}>
      <input
        type="text"
        name="message"
        placeholder="Ask OUS Agile DevOps.."
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        disabled={isLoading}
      />
      <button className="bot-button" type="submit" disabled={isLoading}>
        {isLoading ? (
          <div className="spinner spinner-button"></div>
        ) : (
          <div className="spinner spinner-button" style={{ display: showSpinner ? 'block' : 'none' }}></div>
        )}
        Send
      </button>
    </form>
  );
}

export default InputBox;
