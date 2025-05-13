import axios from 'axios';

// Configura la URL base de tu API
const API_URL = 'http://192.168.1.10:8000'; // Cámbialo a la IP donde corre tu API

// Configuración básica de axios
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chatService = {
  // Enviar un mensaje al chatbot
  sendMessage: async (message, history) => {
    try {
      const response = await api.post('/chat', {
        message,
        history,
      });
      return response.data;
    } catch (error) {
      console.error('Error en la llamada a la API:', error);
      throw error;
    }
  },
};

export default api;