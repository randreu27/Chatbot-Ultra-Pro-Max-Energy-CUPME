// Variables to store message history
let chatHistory = [];

// Get DOM elements when document is ready
document.addEventListener('DOMContentLoaded', function() {
    const sendButton = document.getElementById('sendButton');
    const inputMessage = document.getElementById('inputMessage');
    const chatbox = document.getElementById('chatbox');

    // Check that all necessary elements exist
    if(!sendButton || !inputMessage || !chatbox) {
        console.error('Could not find the necessary elements');
        return;
    }

    // Function to get current time in format HH:MM AM/PM
    function getCurrentTime() {
        const now = new Date();
        let hours = now.getHours();
        const minutes = now.getMinutes().toString().padStart(2, '0');
        const ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12;
        hours = hours ? hours : 12; // Convert hour '0' to '12'
        return `${hours}:${minutes} ${ampm}`;
    }

    // Function to create a user message with styling
    function createUserMessage(message) {
        return `
        <div class="flex flex-col items-end">
            <div class="flex items-start justify-end">
                <div class="bg-blue-600 p-4 rounded-xl rounded-tr-none max-w-[75%]">
                    <p class="text-white">${escapeHtml(message)}</p>
                </div>
                <div class="rounded-full bg-blue-600 p-2 ml-3">
                    <i class="fas fa-user text-white"></i>
                </div>
            </div>
            <p class="text-xs text-gray-500 mr-14 mt-1">${getCurrentTime()}</p>
        </div>
        `;
    }

    // Function to process links in bot messages
    function processLinks(text) {
        // Regular expression to find URLs
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        
        // Replace URLs with formatted link tags
        return text.replace(urlRegex, '<br><a href="$1" target="_blank" rel="noopener noreferrer">$1</a>');
    }

    // Function to create a bot message with styling
    function createBotMessage(message) {
        // Process the text to highlight sources if present
        let formattedMessage = message;
        
        // Look for a sources section at the end
        const sourcesIndex = message.indexOf('USEFUL SOURCES:');
        
        if (sourcesIndex !== -1) {
            // Separate the message and sources
            const messageContent = message.substring(0, sourcesIndex);
            const sourcesContent = message.substring(sourcesIndex);
            
            // Format sources in bold
            formattedMessage = `${messageContent}<br><br><strong>${sourcesContent}</strong>`;
        }

        // Process links to make them clickable and display on new lines
        formattedMessage = processLinks(formattedMessage);
        
        return `
        <div class="flex flex-col items-start">
            <div class="flex items-start">
                <div class="rounded-full bg-siemens-light p-2 mr-3">
                    <i class="fas fa-robot text-siemens-primary"></i>
                </div>
                <div class="bg-siemens-light p-4 rounded-xl rounded-tl-none max-w-[75%]">
                    <p class="text-gray-800">${formattedMessage}</p>
                </div>
            </div>
            <p class="text-xs text-gray-500 ml-14 mt-1">${getCurrentTime()}</p>
        </div>
        `;
    }

    // Function to show loading indicator
    function showLoadingIndicator() {
        chatbox.innerHTML += `
        <div id="loading-indicator" class="flex items-start">
            <div class="rounded-full bg-siemens-light p-2 mr-3">
                <i class="fas fa-robot text-siemens-primary"></i>
            </div>
            <div class="bg-siemens-light p-4 rounded-xl rounded-tl-none max-w-[75%]">
                <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        </div>
        `;
    }

    // Function to remove loading indicator
    function removeLoadingIndicator() {
        const indicator = document.getElementById('loading-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    // Function to escape HTML and prevent XSS
    function escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Function to send message to backend and get the response
    const sendMessage = async () => {
        console.log('sendMessage function executed');
        const message = inputMessage.value;

        if (!message.trim()) return;

        // Show the user message
        chatbox.innerHTML += createUserMessage(message);
        
        // Clear the input
        inputMessage.value = '';
        
        // Scroll the chat down
        chatbox.scrollTop = chatbox.scrollHeight;
        
        // Show loading indicator
        showLoadingIndicator();

        try {
            // Send the message to the backend with chat history
            const response = await fetch('http://127.0.0.1:8000/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    message: message, 
                    history: chatHistory 
                })
            });

            if (!response.ok) {
                throw new Error('Error in server response');
            }

            const data = await response.json();
            
            // Remove loading indicator
            removeLoadingIndicator();

            // Show the AI response
            chatbox.innerHTML += createBotMessage(data.response);
            
            // Update chat history
            chatHistory.push({
                user: message,
                ai: data.response
            });
            
            // Scroll the chat down
            chatbox.scrollTop = chatbox.scrollHeight;
        } catch (error) {
            console.error('Error:', error);
            removeLoadingIndicator();
            chatbox.innerHTML += createBotMessage('Sorry, an error occurred while processing your question. Please try again.');
            chatbox.scrollTop = chatbox.scrollHeight;
        }
    };

    // Add event to the send button
    sendButton.addEventListener('click', sendMessage);
    console.log('Click event assigned to send button');

    // Also send the message when you press Enter
    inputMessage.addEventListener('keypress', (e) => {
        console.log('Key pressed:', e.key);
        if (e.key === 'Enter') {
            console.log('Enter detected, trying to send message');
            e.preventDefault(); // Prevent default behavior (important)
            sendMessage();
        }
    });
    console.log('Keypress event assigned to input');

    // Autofocus on the input when loading the page
    inputMessage.focus();
    console.log('Focus applied to input');
});