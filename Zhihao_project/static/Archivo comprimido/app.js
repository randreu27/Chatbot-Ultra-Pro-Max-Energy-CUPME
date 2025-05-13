// Variables para almacenar el historial de mensajes
let chatHistory = [];

// Obtener los elementos del DOM cuando el documento esté listo
document.addEventListener('DOMContentLoaded', function() {
    const sendButton = document.getElementById('sendButton');
    const inputMessage = document.getElementById('inputMessage');
    const chatbox = document.getElementById('chatbox');

    // Verificamos que todos los elementos necesarios existen
    if(!sendButton || !inputMessage || !chatbox) {
        console.error('No se pudieron encontrar los elementos necesarios');
        return;
    }

    // Función para crear un mensaje del usuario con estilo
    function createUserMessage(message) {
        return `
        <div class="flex items-start justify-end">
            <div class="bg-blue-600 p-4 rounded-xl rounded-tr-none max-w-[75%]">
                <p class="text-white">${escapeHtml(message)}</p>
            </div>
            <div class="rounded-full bg-blue-600 p-2 ml-3">
                <i class="fas fa-user text-white"></i>
            </div>
        </div>
        `;
    }

    // Función para crear un mensaje del bot con estilo
    function createBotMessage(message) {
        // Procesa el texto para resaltar las fuentes si están presentes
        let formattedMessage = message;
        
        // Busca si hay una sección de fuentes al final
        const sourcesIndex = message.indexOf('USEFUL SOURCES:');
        
        if (sourcesIndex !== -1) {
            // Separa el mensaje y las fuentes
            const messageContent = message.substring(0, sourcesIndex);
            const sourcesContent = message.substring(sourcesIndex);
            
            // Formatea las fuentes en negrita
            formattedMessage = `${messageContent}<br><br><strong>${sourcesContent}</strong>`;
        }
        
        return `
        <div class="flex items-start">
            <div class="rounded-full bg-blue-100 p-2 mr-3">
                <i class="fas fa-robot text-blue-600"></i>
            </div>
            <div class="bg-blue-100 p-4 rounded-xl rounded-tl-none max-w-[75%]">
                <p class="text-gray-800">${formattedMessage}</p>
            </div>
        </div>
        `;
    }

    // Función para mostrar indicador de carga
    function showLoadingIndicator() {
        chatbox.innerHTML += `
        <div id="loading-indicator" class="flex items-start">
            <div class="rounded-full bg-blue-100 p-2 mr-3">
                <i class="fas fa-robot text-blue-600"></i>
            </div>
            <div class="bg-blue-100 p-4 rounded-xl rounded-tl-none max-w-[75%]">
                <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        </div>
        `;
    }

    // Función para eliminar indicador de carga
    function removeLoadingIndicator() {
        const indicator = document.getElementById('loading-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    // Función para escapar HTML y prevenir XSS
    function escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Función para enviar mensaje al backend y obtener la respuesta
    const sendMessage = async () => {
        console.log('Función sendMessage ejecutada');
        const message = inputMessage.value;

        if (!message.trim()) return;

        // Mostrar el mensaje del usuario
        chatbox.innerHTML += createUserMessage(message);
        
        // Limpiar el input
        inputMessage.value = '';
        
        // Desplazar hacia abajo el chat
        chatbox.scrollTop = chatbox.scrollHeight;
        
        // Mostrar indicador de carga
        showLoadingIndicator();

        try {
            // Enviar el mensaje al backend con el historial de chat
            const response = await fetch('http://127.0.0.1:8000/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    message: message, 
                    history: chatHistory 
                })
            });

            if (!response.ok) {
                throw new Error('Error en la respuesta del servidor');
            }

            const data = await response.json();
            
            // Eliminar indicador de carga
            removeLoadingIndicator();

            // Mostrar la respuesta del AI
            chatbox.innerHTML += createBotMessage(data.response);
            
            // Actualizar el historial de chat
            chatHistory.push({
                user: message,
                ai: data.response
            });
            
            // Desplazar hacia abajo el chat
            chatbox.scrollTop = chatbox.scrollHeight;
        } catch (error) {
            console.error('Error:', error);
            removeLoadingIndicator();
            chatbox.innerHTML += createBotMessage('Lo siento, ha ocurrido un error al procesar tu pregunta. Por favor, intenta de nuevo.');
            chatbox.scrollTop = chatbox.scrollHeight;
        }
    };

    // Agregar evento al botón de enviar
    sendButton.addEventListener('click', sendMessage);
    console.log('Evento click asignado al botón de enviar');

    // También enviar el mensaje cuando presionas Enter
    inputMessage.addEventListener('keypress', (e) => {
        console.log('Tecla presionada:', e.key);
        if (e.key === 'Enter') {
            console.log('Enter detectado, intentando enviar mensaje');
            e.preventDefault(); // Prevenir comportamiento por defecto (importante)
            sendMessage();
        }
    });
    console.log('Evento keypress asignado al input');

    // Autofocus en el input al cargar la página
    inputMessage.focus();
    console.log('Focus aplicado al input');
});