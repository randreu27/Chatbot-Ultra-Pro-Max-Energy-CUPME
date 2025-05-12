// Obtener los elementos
const sendButton = document.getElementById('sendButton');
const inputMessage = document.getElementById('inputMessage');
const chatbox = document.getElementById('chatbox');

// Función para enviar mensaje al backend y obtener la respuesta
const sendMessage = async () => {
    const message = inputMessage.value;

    if (!message.trim()) return;

    // Mostrar el mensaje del usuario
    chatbox.innerHTML += `<div class="text-right text-blue-500">${message}</div>`;
    inputMessage.value = ''; // Limpiar el input

    // Enviar el mensaje al backend
    const response = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message, history: [] })
    });

    const data = await response.json();

    // Mostrar la respuesta del AI
    chatbox.innerHTML += `<div class="text-left text-gray-700">${data.response}</div>`;
    chatbox.scrollTop = chatbox.scrollHeight; // Desplazar hacia abajo el chat
};

// Agregar evento al botón de enviar
sendButton.addEventListener('click', sendMessage);

// También enviar el mensaje cuando presionas Enter
inputMessage.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});
