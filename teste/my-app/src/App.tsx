import React from 'react';
import './App.css';
import { Bubble } from "@typebot.io/react";

const App = () => {
  return (
    <Bubble
      typebot="whatsapp-ltd-estacio-ia"
      theme={{ button: { backgroundColor: "#035d54" } }}
    />
  );
};


export default App;
