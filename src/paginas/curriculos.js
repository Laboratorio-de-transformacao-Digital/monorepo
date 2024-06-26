import React, { useEffect, useState } from 'react';
import '../estilos/curriculos.css';

const Curriculos = () => {
  const [curriculos, setCurriculos] = useState([]);

  useEffect(() => {
    fetch('/api/curriculos')
      .then(response => response.json())
      .then(data => setCurriculos(data));
  }, []);

  return (
    <div className="curriculos-container">
      <h2 className="title">Meus Currículos</h2>
      <ul>
        {curriculos.map((curriculo, index) => (
          <li key={index}>
            <a href={`/curriculos/${curriculo}`} download>{curriculo}</a>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Curriculos;
