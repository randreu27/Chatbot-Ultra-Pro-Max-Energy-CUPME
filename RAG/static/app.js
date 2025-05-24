console.log('🚀 APP.JS LOADED - NEW VERSION - ' + new Date().toISOString());
// Variables to store message history and language preference
let isRecording = false;
let recognition = null;
let selectedLanguage = null;

// Language welcome messages
const welcomeMessages = {
    es: "Hola, soy el Asistente de Siemens Energy. Estoy aquí para ayudarte con información sobre nuestras soluciones energéticas sostenibles, servicios e innovaciones. Puedes escribir o usar entrada de voz para hacerme preguntas. ¿Cómo puedo ayudarte hoy?",
    ca: "Hola, sóc l'Assistent de Siemens Energy. Estic aquí per ajudar-te amb informació sobre les nostres solucions energètiques sostenibles, serveis i innovacions. Pots escriure o usar entrada de veu per fer-me preguntes. Com puc ajudar-te avui?",
    en: "Hello, I'm the Siemens Energy Assistant. I'm here to help you with information about our sustainable energy solutions, services, and innovations. You can type or use voice input to ask me questions. How can I assist you today?",
    zh: "您好，我是西门子能源助手。我在这里帮助您了解我们的可持续能源解决方案、服务和创新。您可以打字或使用语音输入向我提问。我今天能为您做些什么？"
};

// Check if the browser supports the Web Speech API
const isSpeechRecognitionSupported = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;

// Get DOM elements when document is ready
document.addEventListener('DOMContentLoaded', function() {
    const sendButton = document.getElementById('sendButton');
    const inputMessage = document.getElementById('inputMessage');
    const chatbox = document.getElementById('chatbox');
    const attachmentButton = document.getElementById('attachmentButton');
    const clearButton = document.getElementById('clearButton');
    const voiceInputButton = document.getElementById('voiceInputButton');
    const voiceModal = document.getElementById('voiceModal');
    const startVoiceBtn = document.getElementById('startVoiceBtn');
    const stopVoiceBtn = document.getElementById('stopVoiceBtn');
    const cancelVoiceBtn = document.getElementById('cancelVoiceBtn');
    const voicePrompt = document.getElementById('voicePrompt');
    const voiceResult = document.getElementById('voiceResult');
    const voiceStatus = document.getElementById('voiceStatus');
    const voiceAnimation = document.getElementById('voiceAnimation');
    const languageModal = document.getElementById('languageModal');
    const languageOptions = document.querySelectorAll('.language-option');

    // Check that all necessary elements exist
    if(!sendButton || !inputMessage || !chatbox) {
        console.error('Could not find the necessary elements');
        return;
    }

    // Set up speech recognition if supported
    if (isSpeechRecognitionSupported) {
        setupSpeechRecognition();
    } else {
        console.log('Speech Recognition not supported');
        voiceInputButton.classList.add('opacity-50');
        voiceInputButton.title = 'Voice input not supported in this browser';
    }

    // Function to set up the Web Speech API
    function setupSpeechRecognition() {
        // Use the browser's recognition engine
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        
        // Configure speech recognition
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = 'en-US'; // Default language

        // Handle speech recognition events
        recognition.onstart = function() {
            isRecording = true;
            voicePrompt.textContent = "Listening...";
            voiceStatus.classList.remove('hidden');
            voiceStatus.classList.add('bg-red-500', 'animate-pulse');
            startVoiceBtn.classList.add('hidden');
            stopVoiceBtn.classList.remove('hidden');
            voiceAnimation.classList.add('active');
        };

        recognition.onresult = function(event) {
            const transcript = Array.from(event.results)
                .map(result => result[0])
                .map(result => result.transcript)
                .join('');
            
            voiceResult.textContent = transcript;
            voiceResult.classList.remove('hidden');
        };

        recognition.onend = function() {
            isRecording = false;
            voicePrompt.textContent = "Processing...";
            setTimeout(() => {
                if (voiceResult.textContent) {
                    voiceModal.classList.add('hidden');
                    inputMessage.value = voiceResult.textContent;
                    sendMessage();
                } else {
                    voicePrompt.textContent = "I didn't catch that. Please try again.";
                }
                resetVoiceUI();
            }, 1000);
        };

        recognition.onerror = function(event) {
            console.error('Speech recognition error', event.error);
            voicePrompt.textContent = "Error: " + event.error;
            resetVoiceUI();
        };
    }

    // Reset the voice UI elements
    function resetVoiceUI() {
        voiceStatus.classList.add('hidden');
        voiceStatus.classList.remove('bg-red-500', 'animate-pulse');
        startVoiceBtn.classList.remove('hidden');
        stopVoiceBtn.classList.add('hidden');
        voiceAnimation.classList.remove('active');
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

    // Function to check if dark mode is active
    function isDarkModeActive() {
        return document.body.classList.contains('dark-mode');
    }

    // Function to apply dark mode styles to an element
    function applyDarkModeToElement(element) {
        if (isDarkModeActive()) {
            // Apply dark mode styles to message bubbles
            const lightBubbles = element.querySelectorAll('.bg-siemens-light');
            lightBubbles.forEach(el => {
                el.style.backgroundColor = '#6b7280';
            });
            
            // Apply dark mode styles to text
            const grayText = element.querySelectorAll('.text-gray-800');
            grayText.forEach(el => {
                el.style.color = '#f9fafb';
            });
            
            const gray700Text = element.querySelectorAll('.text-gray-700');
            gray700Text.forEach(el => {
                el.style.color = '#d1d5db';
            });
            
            const gray500Text = element.querySelectorAll('.text-gray-500');
            gray500Text.forEach(el => {
                el.style.color = '#9ca3af';
            });
            
            // Apply dark mode to sources cards
            const sourcesCards = element.querySelectorAll('.sources-card');
            sourcesCards.forEach(el => {
                el.style.backgroundColor = '#4b5563';
                el.style.borderColor = '#009999';
            });
            
            // Apply dark mode to link cards
            const linkCards = element.querySelectorAll('.link-card a');
            linkCards.forEach(el => {
                el.style.backgroundColor = '#4b5563';
                el.style.borderColor = '#6b7280';
            });
        }
    }

    // Function to create a user message with styling
    function createUserMessage(message) {
        const fontSize = document.documentElement.style.getPropertyValue('--message-font-size') || '1rem';
        const messageHtml = `
        <div class="flex flex-col items-end message-container animate-slideIn">
            <div class="flex items-start justify-end">
                <div class="bg-siemens-accent p-4 rounded-2xl rounded-tr-none max-w-[75%] shadow-md">
                    <p class="text-white message-text" style="font-size: ${fontSize}">${escapeHtml(message)}</p>
                </div>
                <div class="rounded-full bg-siemens-accent p-2 ml-3 shadow-md">
                    <i class="fas fa-user text-white"></i>
                </div>
            </div>
            <p class="text-xs text-gray-500 mr-14 mt-1">${getCurrentTime()}</p>
        </div>
        `;
        
        // Create a temporary container to apply dark mode styles
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = messageHtml;
        applyDarkModeToElement(tempDiv);
        
        return tempDiv.innerHTML;
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
        const sourcesIndex = message.indexOf('SOURCES:');
        
        if (sourcesIndex !== -1) {
            // Separate the message and sources
            const messageContent = message.substring(0, sourcesIndex);
            const sourcesContent = message.substring(sourcesIndex);
            
            // Format sources in an elegant card
            formattedMessage = `${messageContent}<div class="sources-card mt-4 p-3 bg-gray-50 rounded-lg border-l-4 border-siemens-primary">
                <div class="font-medium text-siemens-secondary mb-1">
                    <i class="fas fa-book-open mr-2"></i>SOURCES
                </div>
                <div class="text-sm text-gray-700">${sourcesContent.replace('SOURCES:', '')}</div>
            </div>`;
        }

        // Process links to make them clickable and display as cards
        formattedMessage = processLinks(formattedMessage);
        
        const fontSize = document.documentElement.style.getPropertyValue('--message-font-size') || '1rem';
        const messageHtml = `
        <div class="flex flex-col items-start message-container animate-slideIn">
            <div class="flex items-start">
                <div class="rounded-full bg-siemens-light p-2 mr-3 shadow-md">
                    <i class="fas fa-robot text-siemens-primary"></i>
                </div>
                <div class="bg-siemens-light p-4 rounded-2xl rounded-tl-none max-w-[75%] shadow-md">
                    <p class="text-gray-800 message-text" style="font-size: ${fontSize}">${formattedMessage}</p>
                </div>
            </div>
            <p class="text-xs text-gray-500 ml-14 mt-1">${getCurrentTime()}</p>
        </div>
        `;
        
        // Create a temporary container to apply dark mode styles
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = messageHtml;
        applyDarkModeToElement(tempDiv);
        
        return tempDiv.innerHTML;
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
            // Send the message to the backend WITH language preference
            const response = await fetch('http://127.0.0.1:8000/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    message: message,
                    language: selectedLanguage
                })
            });

            if (!response.ok) {
                throw new Error('Error in server response');
            }
            console.log('HTTP response status:', response.status);
            const text = await response.text();
            console.log('Texto crudo recibido del backend:', text);
            const data = JSON.parse(text);
            
            // Remove loading indicator
            removeLoadingIndicator();

            // Show the AI response
            chatbox.innerHTML += createBotMessage(data.response);
            
            // Scroll the chat down
            chatbox.scrollTop = chatbox.scrollHeight;

            // Enable text to speech for accessibility
            if (window.speechSynthesis && document.getElementById('ttsToggle').checked) {
                // Function to clean text for speech
                function cleanTextForSpeech(text) {
                    let cleanText = text;
                    
                    cleanText = cleanText.replace(/<div class="sources-card[^>]*>[\s\S]*?<\/div>/gi, '');
                    cleanText = cleanText.replace(/SOURCES:[\s\S]*$/gi, '');
                    
                    const tempDiv = document.createElement('div');
                    tempDiv.innerHTML = cleanText;
                    
                    const linkCards = tempDiv.querySelectorAll('.link-card');
                    linkCards.forEach(card => card.remove());
                    
                    const anchors = tempDiv.querySelectorAll('a');
                    anchors.forEach(anchor => {
                        const textContent = anchor.textContent.trim();
                        if (textContent && !textContent.match(/^https?:\/\//)) {
                            anchor.replaceWith(document.createTextNode(textContent));
                        } else {
                            anchor.remove();
                        }
                    });
                    
                    let finalText = tempDiv.textContent || tempDiv.innerText || '';
                    
                    finalText = finalText
                        .replace(/https?:\/\/[^\s]+/g, '')
                        .replace(/www\.[^\s]+/g, '')
                        .replace(/Resource Link/gi, '')
                        .replace(/SOURCES:?/gi, '')
                        .replace(/Source:?/gi, '')
                        .replace(/\.(pdf|doc|docx|txt|html|htm)/gi, '')
                        .replace(/\s+/g, ' ')
                        .trim();
                    
                    return finalText;
                }
                
                const cleanedText = cleanTextForSpeech(data.response);
                if (cleanedText.length > 0) {
                    // Set language for text-to-speech based on selected language
                    const ttsLanguages = {
                        'es': 'es-ES',
                        'ca': 'ca-ES',
                        'en': 'en-US',
                        'zh': 'zh-CN'
                    };
                    
                    const utterance = new SpeechSynthesisUtterance(cleanedText);
                    utterance.lang = ttsLanguages[selectedLanguage] || 'en-US';
                    utterance.rate = 1;
                    
                    // Try to find a voice for the selected language
                    const voices = window.speechSynthesis.getVoices();
                    const targetLang = ttsLanguages[selectedLanguage] || 'en-US';
                    
                    // Find a voice that matches the language
                    const matchingVoice = voices.find(voice => 
                        voice.lang === targetLang || 
                        voice.lang.startsWith(targetLang.split('-')[0])
                    );
                    
                    if (matchingVoice) {
                        utterance.voice = matchingVoice;
                        console.log(`🔊 Using voice: ${matchingVoice.name} for language: ${targetLang}`);
                    } else {
                        console.log(`⚠️ No specific voice found for ${targetLang}, using default`);
                    }
                    
                    window.speechSynthesis.speak(utterance);
                }
            }
        } catch (error) {
            console.error('ERROR EN FETCH O JSON:', error);
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

    // Function to update welcome message
    function updateWelcomeMessage() {
        const welcomeMessage = welcomeMessages[selectedLanguage] || welcomeMessages.en;
        const fontSize = document.documentElement.style.getPropertyValue('--message-font-size') || '1rem';
        
        const welcomeHtml = `
        <div class="flex flex-col items-start message-container">
            <div class="flex items-start">
                <div class="rounded-full bg-siemens-light p-2 mr-3 shadow-md">
                    <i class="fas fa-robot text-siemens-primary"></i>
                </div>
                <div class="bg-siemens-light p-4 rounded-2xl rounded-tl-none max-w-[75%] shadow-md">
                    <p class="text-gray-800 message-text" style="font-size: ${fontSize}">${welcomeMessage}</p>
                </div>
            </div>
            <p class="text-xs text-gray-500 ml-14 mt-1">${getCurrentTime()}</p>
        </div>`;
        
        // Create temporary container and apply dark mode if needed
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = welcomeHtml;
        applyDarkModeToElement(tempDiv);
        chatbox.innerHTML = tempDiv.innerHTML;
    }

    // Function to clear chat history
    const clearChat = async () => {
        try {
            // Call backend to clear history
            const response = await fetch('http://127.0.0.1:8000/clear-history', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) {
                throw new Error('Error clearing chat history');
            }

            // Update welcome message based on current language
            updateWelcomeMessage();
            
        } catch (error) {
            console.error('Error clearing chat history:', error);
            // Still update welcome message on error
            updateWelcomeMessage();
        }
    };

    // Function to handle voice input
    function handleVoiceInput() {
        // If browser doesn't support speech recognition
        if (!isSpeechRecognitionSupported) {
            alert('Voice input is not supported in your browser. Please use Chrome, Edge, or Safari.');
            return;
        }
        
        // Show the voice modal
        voiceModal.classList.remove('hidden');
        voiceResult.textContent = '';
        voiceResult.classList.add('hidden');
        voicePrompt.textContent = 'Press Start to begin speaking';
    }

    // Function to start voice recording
    function startVoiceRecording() {
        if (recognition) {
            try {
                recognition.start();
            } catch (err) {
                console.error('Speech recognition error on start:', err);
                voicePrompt.textContent = 'Error starting voice input. Please try again.';
            }
        }
    }

    // Function to stop voice recording
    function stopVoiceRecording() {
        if (recognition && isRecording) {
            recognition.stop();
        }
    }

    // Handle language selection
    languageOptions.forEach(option => {
        option.addEventListener('click', function() {
            selectedLanguage = this.dataset.lang;
            const languageName = this.dataset.name;
            
            // Hide language modal
            languageModal.classList.add('hidden');
            
            // Update welcome message based on selected language
            updateWelcomeMessage();
            
            // Set speech recognition language
            if (recognition) {
                const langCodes = {
                    es: 'es-ES',
                    ca: 'ca-ES', 
                    en: 'en-US',
                    zh: 'zh-CN'
                };
                recognition.lang = langCodes[selectedLanguage] || 'en-US';
            }
            
            // Load voices for the selected language (for TTS)
            if (window.speechSynthesis) {
                // Ensure voices are loaded
                window.speechSynthesis.getVoices();
                window.speechSynthesis.onvoiceschanged = function() {
                    const voices = window.speechSynthesis.getVoices();
                    const ttsLanguages = {
                        'es': 'es-ES',
                        'ca': 'ca-ES',
                        'en': 'en-US',
                        'zh': 'zh-CN'
                    };
                    const targetLang = ttsLanguages[selectedLanguage] || 'en-US';
                    const availableVoices = voices.filter(voice => 
                        voice.lang === targetLang || 
                        voice.lang.startsWith(targetLang.split('-')[0])
                    );
                    console.log(`🔊 Available voices for ${targetLang}:`, availableVoices.map(v => v.name));
                };
            }
            
            console.log('Language selected:', selectedLanguage);
        });
    });

    // Add event to the send button
    sendButton.addEventListener('click', sendMessage);
    console.log('Click event assigned to send button');

    // Add event to the clear button
    if (clearButton) {
        clearButton.addEventListener('click', clearChat);
    }

    // Add event to the voice input button
    if (voiceInputButton) {
        voiceInputButton.addEventListener('click', handleVoiceInput);
    }

    // Start voice recording
    if (startVoiceBtn) {
        startVoiceBtn.addEventListener('click', startVoiceRecording);
    }

    // Stop voice recording
    if (stopVoiceBtn) {
        stopVoiceBtn.addEventListener('click', stopVoiceRecording);
    }

    // Cancel voice recording
    if (cancelVoiceBtn) {
        cancelVoiceBtn.addEventListener('click', function() {
            if (isRecording && recognition) {
                recognition.abort();
            }
            voiceModal.classList.add('hidden');
            resetVoiceUI();
        });
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