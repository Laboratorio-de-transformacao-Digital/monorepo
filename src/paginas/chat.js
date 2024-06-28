import React, { useEffect, useState } from 'react';
import { jsPDF } from 'jspdf';
import '../estilos/chat.css';

const steps = [
  { question: 'Qual é o seu email?', key: 'email', section: 'dadosPessoais' },
  { question: 'Qual é o seu telefone?', key: 'telefone', section: 'dadosPessoais' },
  { question: 'Qual é a sua cidade?', key: 'cidade', section: 'dadosPessoais' },
  { question: 'Qual é a sua data de nascimento?', key: 'dataNascimento', section: 'dadosPessoais' },
  { question: 'Descreva seu objetivo profissional.', key: 'descricao', section: 'objetivoProfissional' },
  { question: 'Qual é o seu curso?', key: 'curso', section: 'academica' },
  { question: 'Qual é a instituição de ensino?', key: 'instituicao', section: 'academica' },
  { question: 'Qual é o período do curso?', key: 'periodo', section: 'academica' },
  { question: 'Qual é o status atual do curso?', key: 'statusAtual', section: 'academica' },
  { question: 'Qual é a fase atual do curso?', key: 'faseAtual', section: 'academica' },
  { question: 'Qual é o nome da empresa em que trabalhou?', key: 'nome', section: 'experiencia' },
  { question: 'Qual era o cargo ocupado?', key: 'cargo', section: 'experiencia' },
  { question: 'Descreva uma função que você desempenhou.', key: 'funcao1', section: 'experiencia', subkey: 'funcoes' },
  { question: 'Descreva outra função que você desempenhou.', key: 'funcao2', section: 'experiencia', subkey: 'funcoes' },
  { question: 'Qual é o nome do seu certificado?', key: 'nome', section: 'certificacoes' },
  { question: 'Qual é o curso relacionado ao certificado?', key: 'curso', section: 'certificacoes' },
  { question: 'Qual é a instituição emissora do certificado?', key: 'instituicao', section: 'certificacoes' },
  { question: 'Qual idioma você fala?', key: 'lingua', section: 'idiomas' },
  { question: 'Qual é o seu nível de fluência no idioma?', key: 'fluencia', section: 'idiomas' },
];

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [currentStep, setCurrentStep] = useState(0);
  const [curriculoData, setCurriculoData] = useState({
    dadosPessoais: {},
    objetivoProfissional: {},
    academica: [],
    experiencia: [],
    certificacoes: [],
    idiomas: []
  });

  useEffect(() => {
    if (currentStep < steps.length) {
      setMessages((prevMessages) => [...prevMessages, { type: 'bot', text: steps[currentStep].question }]);
    } else {
      setMessages((prevMessages) => [...prevMessages, { type: 'bot', text: 'Obrigado por fornecer todas as informações! Clique no botão abaixo para baixar seu currículo.' }]);
    }
  }, [currentStep]);

  const sendMessage = () => {
    if (input.trim()) {
      const newMessage = { type: 'user', text: input };
      setMessages((prevMessages) => [...prevMessages, newMessage]);
      const step = steps[currentStep];
      const newData = { ...curriculoData };
      if (step.section === 'experiencia' || step.section === 'academica' || step.section === 'certificacoes' || step.section === 'idiomas') {
        const sectionArray = newData[step.section];
        if (!sectionArray[currentStep]) sectionArray[currentStep] = {};
        if (step.subkey) {
          if (!sectionArray[currentStep][step.subkey]) sectionArray[currentStep][step.subkey] = [];
          sectionArray[currentStep][step.subkey].push(input);
        } else {
          sectionArray[currentStep][step.key] = input;
        }
      } else {
        newData[step.section][step.key] = input;
      }
      setCurriculoData(newData);
      setInput('');
      setCurrentStep(currentStep + 1);
    }
  };

  const generatePDF = () => {
    const doc = new jsPDF();
    doc.setFont('Helvetica');
    doc.setFontSize(20);
    doc.text('Currículo', 105, 10, null, null, 'center');
    
    doc.setFontSize(14);
    let currentY = 20; // Y position starts after the title

    const addSection = (title, content) => {
      doc.setFontSize(16);
      doc.text(title, 10, currentY);
      currentY += 10; // Move Y position down
      doc.setFontSize(12);
      doc.text(content, 10, currentY);
      currentY += content.split('\n').length * 10; // Move Y position down based on content
    };

    addSection('Dados Pessoais', Object.entries(curriculoData.dadosPessoais).map(([key, value]) => `${key}: ${value}`).join('\n'));
    addSection('Objetivo Profissional', curriculoData.objetivoProfissional.descricao || '');
    addSection('Formação Acadêmica', curriculoData.academica.map((a) => `${a.curso} - ${a.instituicao} (${a.periodo})`).join('\n'));
    addSection('Experiência', curriculoData.experiencia.map((e) => `${e.nome} - ${e.cargo}\n${e.funcoes.join(', ')}`).join('\n'));
    addSection('Certificações', curriculoData.certificacoes.map((c) => `${c.nome} - ${c.curso} (${c.instituicao})`).join('\n'));
    addSection('Idiomas', curriculoData.idiomas.map((i) => `${i.lingua}: ${i.fluencia}`).join('\n'));

    doc.save('curriculo.pdf');
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
          {currentStep >= steps.length && (
            <div className="message bot-message">
              <button onClick={generatePDF} className="download-link">
                Baixar Currículo
              </button>
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
            onKeyPress={(e) => { if (e.key === 'Enter') sendMessage(); }}
          />
          <button className="send-button" onClick={sendMessage}>Enviar</button>
        </div>
      </div>
    </div>
  );
};

export default Chat;
