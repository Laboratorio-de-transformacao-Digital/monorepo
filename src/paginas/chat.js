import React, { useEffect } from 'react';
import '../estilos/chat.css';

const Chat = () => {
  useEffect(() => {
    const script = document.createElement('script');
    script.type = 'module';
    script.innerHTML = `
      import Typebot from 'https://cdn.jsdelivr.net/npm/@typebot.io/js@0.2/dist/web.js';

      Typebot.initBubble({
        typebot: "whatsapp-ltd-estacio-ia",
        theme: {
          button: { backgroundColor: "#035d54" },
          chatWindow: {
            backgroundColor: "https://s3.fr-par.scw.cloud/typebot/public/typebots/cli88mae30010mh0f0yzjqn48/background?v=1685470080750",
          },
        },
      });
    `;
    document.body.appendChild(script);

    // Cleanup the script when the component is unmounted
    return () => {
      document.body.removeChild(script);
    };
  }, []);

  return (
    <div className="chat-container">
      <h2 className="chat-title">Chat CR</h2>
      <div className="chat-box">
        <div className="messages">
          <div className="message bot-message">Olá! Como posso ajudar você hoje?</div>
          {/* Adicione aqui as mensagens do chat */}
        </div>
        <div className="input-container">
          <input type="text" placeholder="Digite sua mensagem..." className="chat-input" />
          <button className="send-button">Enviar</button>
        </div>
      </div>
    </div>
  );
}

export default Chat;
