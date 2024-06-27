import React, { useEffect, useState } from 'react';
import io from 'socket.io-client';
import '../estilos/chat.css';

const socket = io('http://127.0.0.1:5000');

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [showDownloadButton, setShowDownloadButton] = useState(false);

  useEffect(() => {
    socket.on('message', (data) => {
      setMessages((prevMessages) => [...prevMessages, { type: 'bot', text: data.text }]);
    });

    socket.on('complete', () => {
      setShowDownloadButton(true);
    });

    return () => {
      socket.off('message');
      socket.off('complete');
    };
  }, []);

  const sendMessage = () => {
    if (input.trim()) {
      setMessages((prevMessages) => [...prevMessages, { type: 'user', text: input }]);
      socket.emit('message', { text: input });
      setInput('');
    }
  };

  return (
    <div className="chat-container">
      <h2 className="chat-title">Chat CR</h2>
      <div className="chat-box">
        <div className="messages">
          {messages.map((message, index) => (
            <div key={index} className={`message ${message.type}-message`}>
              {message.text}
            </div>
          ))}
          {showDownloadButton && (
            <div className="message bot-message">
              <a href="http://127.0.0.1:5000/download" target="_blank" rel="noopener noreferrer" className="download-link">
                Baixar Currículo
              </a>
            </div>
          )}
        </div>
        <div className="input-container">
          <input
            type="text"
            placeholder="Digite sua mensagem..."
            className="chat-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <button className="send-button" onClick={sendMessage}>Enviar</button>
        </div>
      </div>
    </div>
  );
};

export default Chat;
