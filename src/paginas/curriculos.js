import React, { useEffect, useState } from 'react';
import '../estilos/curriculos.css';

const Curriculos = () => {
  const [curriculos, setCurriculos] = useState([]);

  useEffect(() => {
    fetch('/curriculos')
      .then(response => response.json())
      .then(data => {
        console.log('Currículos recebidos:', data); // Log para depuração
        setCurriculos(data);
      })
      .catch(error => {
        console.error('Erro ao buscar currículos:', error);
      });
  }, []);

  return (
    <div className="curriculos-container">
      <h2 className="title">Meus Currículos</h2>
      <ul>
        {curriculos.length === 0 ? (
          <li>Nenhum currículo disponível</li>
        ) : (
          curriculos.map((curriculo, index) => (
            <li key={index}>
              <a href={`/curriculos/${curriculo}`} download>{curriculo}</a>
            </li>
          ))
        )}
      </ul>
    </div>
  );
}

export default Curriculos;
