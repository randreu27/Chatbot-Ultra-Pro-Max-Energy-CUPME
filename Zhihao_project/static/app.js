// Variables to store message history
let chatHistory = [];

// Get DOM elements when document is ready
document.addEventListener('DOMContentLoaded', function() {
    const sendButton = document.getElementById('sendButton');
    const inputMessage = document.getElementById('inputMessage');
    const chatbox = document.getElementById('chatbox');
    const attachmentButton = document.getElementById('attachmentButton');
    const clearButton = document.getElementById('clearButton');

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
        <div class="flex flex-col items-end message-container animate-slideIn">
            <div class="flex items-start justify-end">
                <div class="bg-siemens-accent p-4 rounded-2xl rounded-tr-none max-w-[75%] shadow-md">
                    <p class="text-white message-text">${escapeHtml(message)}</p>
                </div>
                <div class="rounded-full bg-siemens-accent p-2 ml-3 shadow-md">
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
        
        // Replace URLs with formatted link cards
        return text.replace(urlRegex, function(url) {
            return `
            <div class="link-card mt-3 mb-2">
                <a href="${url}" target="_blank" rel="noopener noreferrer" class="flex items-center p-3 bg-white rounded-lg border border-siemens-light shadow-sm hover:shadow-md transition-all">
                    <div class="link-icon mr-3 bg-siemens-primary bg-opacity-10 p-2 rounded-full">
                        <i class="fas fa-external-link-alt text-siemens-primary"></i>
                    </div>
                    <div class="link-content">
                        <div class="text-sm font-medium text-siemens-secondary">Resource Link</div>
                        <div class="text-xs text-gray-500 truncate max-w-xs">${url}</div>
                    </div>
                </a>
            </div>`;
        });
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
            
            // Format sources in an elegant card
            formattedMessage = `${messageContent}<div class="sources-card mt-4 p-3 bg-gray-50 rounded-lg border-l-4 border-siemens-primary">
                <div class="font-medium text-siemens-secondary mb-1">
                    <i class="fas fa-book-open mr-2"></i>USEFUL SOURCES
                </div>
                <div class="text-sm">${sourcesContent.replace('USEFUL SOURCES:', '')}</div>
            </div>`;
        }

        // Process links to make them clickable and display as cards
        formattedMessage = processLinks(formattedMessage);
        
        return `
        <div class="flex flex-col items-start message-container animate-slideIn">
            <div class="flex items-start">
                <div class="rounded-full bg-siemens-light p-2 mr-3 shadow-md">
                    <i class="fas fa-robot text-siemens-primary"></i>
                </div>
                <div class="bg-siemens-light p-4 rounded-2xl rounded-tl-none max-w-[75%] shadow-md">
                    <p class="text-gray-800 message-text">${formattedMessage}</p>
                </div>
            </div>
            <p class="text-xs text-gray-500 ml-14 mt-1">${getCurrentTime()}</p>
        </div>
        `;
    }

    // Function to show loading indicator
    function showLoadingIndicator() {
        chatbox.innerHTML += `
        <div id="loading-indicator" class="flex items-start message-container animate-fadeIn">
            <div class="rounded-full bg-siemens-light p-2 mr-3 shadow-md">
                <i class="fas fa-robot text-siemens-primary"></i>
            </div>
            <div class="bg-siemens-light p-4 rounded-2xl rounded-tl-none max-w-[75%] shadow-md">
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

            // Enable text to speech for accessibility
            if (window.speechSynthesis && document.getElementById('ttsToggle').checked) {
                const utterance = new SpeechSynthesisUtterance(data.response.replace(/<[^>]*>?/gm, ''));
                utterance.lang = 'en-US';
                utterance.rate = 1;
                window.speechSynthesis.speak(utterance);
            }
        } catch (error) {
            console.error('Error:', error);
            removeLoadingIndicator();
            chatbox.innerHTML += createBotMessage('Sorry, an error occurred while processing your question. Please try again.');
            chatbox.scrollTop = chatbox.scrollHeight;
        }
    };

    // Function to update input placeholder based on activity
    function updateInputPlaceholder(isActive) {
        if (isActive) {
            inputMessage.setAttribute('placeholder', 'Type your message here...');
        } else {
            inputMessage.setAttribute('placeholder', 'Siemens Energy Assistant is listening...');
            setTimeout(() => {
                inputMessage.setAttribute('placeholder', 'Type your message here...');
            }, 3000);
        }
    }

    // Function to clear chat history
    const clearChat = () => {
        // Keep only the welcome message
        chatbox.innerHTML = `
        <div class="flex flex-col items-start message-container">
            <div class="flex items-start">
                <div class="rounded-full bg-siemens-light p-2 mr-3 shadow-md">
                    <i class="fas fa-robot text-siemens-primary"></i>
                </div>
                <div class="bg-siemens-light p-4 rounded-2xl rounded-tl-none max-w-[75%] shadow-md">
                    <p class="text-gray-800 message-text">Hello, I'm the Siemens Energy Assistant. I'm here to help you with information about our sustainable energy solutions, services, and innovations. How can I assist you today?</p>
                </div>
            </div>
            <p class="text-xs text-gray-500 ml-14 mt-1">${getCurrentTime()}</p>
        </div>`;
        
        // Clear the chat history array
        chatHistory = [];
    };

    // Add event to the send button
    sendButton.addEventListener('click', sendMessage);
    console.log('Click event assigned to send button');

    // Add event to the clear button
    if (clearButton) {
        clearButton.addEventListener('click', clearChat);
    }

    // Also send the message when you press Enter
    inputMessage.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault(); // Prevent default behavior (important)
            sendMessage();
        }
    });

    // Add focus and blur events for input field animation
    inputMessage.addEventListener('focus', () => {
        document.querySelector('.input-container').classList.add('input-active');
        updateInputPlaceholder(true);
    });

    inputMessage.addEventListener('blur', () => {
        document.querySelector('.input-container').classList.remove('input-active');
        if (!inputMessage.value) {
            updateInputPlaceholder(false);
        }
    });

    // Handle attachment button click
    if (attachmentButton) {
        attachmentButton.addEventListener('click', () => {
            alert('File upload functionality coming soon!');
        });
    }

    // Autofocus on the input when loading the page
    inputMessage.focus();
    console.log('Focus applied to input');
});