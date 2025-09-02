// Chat functionality for AI Assistant
class ChatBot {
    constructor() {
        this.sessionId = sessionId;
        this.currentLanguage = currentLanguage;
        this.currentTopic = 'general';
        this.isTyping = false;
        this.recognition = null;

        this.initializeElements();
        this.bindEvents();
        this.initializeSpeechRecognition();
        this.scrollToBottom();
    }

    initializeElements() {
        this.messageForm = document.getElementById('messageForm');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.chatMessages = document.getElementById('chatMessages');
        this.languageSelector = document.getElementById('languageSelector');
        this.topicSelector = document.getElementById('topicSelector');
        this.voiceButton = document.getElementById('voiceButton');
        this.translateButton = document.getElementById('translateButton');
        this.searchInput = document.getElementById('searchInput');
        this.searchResults = document.getElementById('searchResults');
        this.statusBadge = document.getElementById('statusBadge');
        this.loadingSpinner = document.getElementById('loadingSpinner');
    }

    bindEvents() {
        // Form submission
        this.messageForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendMessage();
        });

        // Language change
        this.languageSelector.addEventListener('change', (e) => {
            this.currentLanguage = e.target.value;
            this.updateChatTitle();
        });

        // Topic change
        this.topicSelector.addEventListener('change', (e) => {
            this.currentTopic = e.target.value;
        });

        // Voice input
        this.voiceButton.addEventListener('click', () => {
            this.toggleVoiceInput();
        });

        // Translation
        this.translateButton.addEventListener('click', () => {
            this.translateLastMessage();
        });

        // Rating buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('rating-btn')) {
                this.rateMessage(e.target);
            }
        });

        // Enter key for sending
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
    }

    initializeSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = this.currentLanguage === 'ta' ? 'ta-IN' : 'en-US';

            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                this.messageInput.value = transcript;
                this.voiceButton.classList.remove('recording');
                this.voiceButton.innerHTML = '<i class="fas fa-microphone"></i> Voice Input';
            };

            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.voiceButton.classList.remove('recording');
                this.voiceButton.innerHTML = '<i class="fas fa-microphone"></i> Voice Input';
                this.showAlert('Voice recognition error: ' + event.error, 'danger');
            };

            this.recognition.onend = () => {
                this.voiceButton.classList.remove('recording');
                this.voiceButton.innerHTML = '<i class="fas fa-microphone"></i> Voice Input';
            };
        }
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isTyping) return;

        // Clear input and show typing
        this.messageInput.value = '';
        this.showTyping(true);

        // Add user message to chat
        this.addMessage('user', message, 'You');

        try {
            const response = await fetch('/api/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    message: message,
                    session_id: this.sessionId,
                    language: this.currentLanguage,
                    topic: this.currentTopic
                })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();

            // Add AI response to chat
            this.addMessage('ai', data.ai_response.content, 'AI Assistant', {
                messageId: data.ai_response.id,
                model: data.ai_response.model_used,
                confidence: data.ai_response.confidence,
                responseTime: data.ai_response.response_time_ms
            });

        } catch (error) {
            console.error('Error sending message:', error);
            this.addMessage('ai', 'Sorry, I encountered an error. Please try again.', 'AI Assistant');
            this.showAlert('Error sending message. Please try again.', 'danger');
        } finally {
            this.showTyping(false);
        }
    }

    addMessage(type, content, sender, metadata = {}) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        if (metadata.messageId) {
            messageDiv.dataset.messageId = metadata.messageId;
        }

        const now = new Date();
        const timeString = now.toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit',
            hour12: false 
        });

        let metaHtml = '';
        if (type === 'ai' && metadata.messageId) {
            metaHtml = `
                <div class="message-meta">
                    <small class="text-muted">
                        ${metadata.model ? `Model: ${metadata.model}` : ''}
                        ${metadata.confidence ? ` | Confidence: ${metadata.confidence.toFixed(1)}` : ''}
                        ${metadata.responseTime ? ` | Time: ${metadata.responseTime}ms` : ''}
                    </small>
                    <div class="rating-buttons mt-2">
                        <small>Rate this response: </small>
                        ${[1,2,3,4,5].map(rating => 
                            `<button class="btn btn-outline-warning btn-sm rating-btn" 
                                     data-rating="${rating}" 
                                     data-message-id="${metadata.messageId}">
                                <i class="fas fa-star"></i>
                            </button>`
                        ).join('')}
                    </div>
                </div>
            `;
        }

        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-header">
                    <strong>
                        <i class="fas fa-${type === 'user' ? 'user' : 'robot'}"></i> ${sender}
                    </strong>
                    <small class="text-muted">${timeString}</small>
                    ${this.currentTopic !== 'general' ? 
                        `<span class="badge bg-secondary">${this.currentTopic}</span>` : ''}
                </div>
                <div class="message-text">${this.formatMessage(content)}</div>
                ${metaHtml}
            </div>
        `;

        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    formatMessage(content) {
        // Basic formatting for links, line breaks, etc.
        return content
            .replace(/\n/g, '<br>')
            .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" rel="noopener">$1</a>');
    }

    showTyping(show) {
        this.isTyping = show;
        this.sendButton.disabled = show;

        if (show) {
            this.sendButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
            this.addTypingIndicator();
        } else {
            this.sendButton.innerHTML = '<i class="fas fa-paper-plane"></i> Send';
            this.removeTypingIndicator();
        }
    }

    addTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message ai typing-indicator-message';
        typingDiv.innerHTML = `
            <div class="message-content">
                <div class="message-header">
                    <strong><i class="fas fa-robot"></i> AI Assistant</strong>
                </div>
                <div class="message-text">
                    <div class="typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            </div>
        `;

        this.chatMessages.appendChild(typingDiv);
        this.scrollToBottom();
    }

    removeTypingIndicator() {
        const typingIndicator = this.chatMessages.querySelector('.typing-indicator-message');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    async rateMessage(button) {
        const rating = parseInt(button.dataset.rating);
        const messageId = button.dataset.messageId;

        try {
            const response = await fetch('/api/rate/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    message_id: messageId,
                    rating: rating
                })
            });

            if (response.ok) {
                // Update UI to show rating
                const ratingButtons = button.parentNode.querySelectorAll('.rating-btn');
                ratingButtons.forEach((btn, index) => {
                    btn.classList.toggle('active', index < rating);
                });

                this.showAlert(`Thanks for rating! (${rating}/5 stars)`, 'success');
            }

        } catch (error) {
            console.error('Error rating message:', error);
            this.showAlert('Error saving rating. Please try again.', 'danger');
        }
    }

    toggleVoiceInput() {
        if (!this.recognition) {
            this.showAlert('Speech recognition not supported in your browser', 'warning');
            return;
        }

        if (this.voiceButton.classList.contains('recording')) {
            this.recognition.stop();
        } else {
            this.recognition.lang = this.currentLanguage === 'ta' ? 'ta-IN' : 'en-US';
            this.recognition.start();
            this.voiceButton.classList.add('recording');
            this.voiceButton.innerHTML = '<i class="fas fa-stop"></i> Stop Recording';
        }
    }

    async translateLastMessage() {
        const messages = this.chatMessages.querySelectorAll('.message');
        const lastMessage = messages[messages.length - 1];

        if (!lastMessage) return;

        const messageText = lastMessage.querySelector('.message-text').textContent;
        const targetLang = this.currentLanguage === 'ta' ? 'en' : 'ta';

        try {
            const response = await fetch('/api/translate/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    text: messageText,
                    target_lang: targetLang
                })
            });

            if (response.ok) {
                const data = await response.json();
                this.addMessage('system', `Translation: ${data.translated_text}`, 'Translator');
            }

        } catch (error) {
            console.error('Translation error:', error);
            this.showAlert('Translation failed. Please try again.', 'danger');
        }
    }

    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }

    updateChatTitle() {
        const title = document.getElementById('chatTitle');
        if (this.currentLanguage === 'ta') {
            title.textContent = 'பல மொழி AI உதவியாளர்';
        } else {
            title.textContent = 'Multi-language AI Assistant';
        }
    }

    showAlert(message, type = 'info') {
        // Create alert element
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Add to page
        document.body.insertBefore(alertDiv, document.body.firstChild);

        // Auto dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

// Web Search functionality
async function performWebSearch() {
    const query = document.getElementById('searchInput').value.trim();
    if (!query) return;

    const resultsDiv = document.getElementById('searchResults');
    resultsDiv.innerHTML = '<div class="text-center"><i class="fas fa-spinner fa-spin"></i> Searching...</div>';

    try {
        const response = await fetch(`/api/search/?q=${encodeURIComponent(query)}&lang=${currentLanguage}&topic=${chatBot.currentTopic}`);

        if (response.ok) {
            const data = await response.json();
            displaySearchResults(data.results);
        } else {
            throw new Error('Search failed');
        }
    } catch (error) {
        console.error('Search error:', error);
        resultsDiv.innerHTML = '<div class="text-danger">Search failed. Please try again.</div>';
    }
}

function displaySearchResults(results) {
    const resultsDiv = document.getElementById('searchResults');

    if (results.length === 0) {
        resultsDiv.innerHTML = '<div class="text-muted">No results found.</div>';
        return;
    }

    const resultsHtml = results.map(result => `
        <div class="search-result" onclick="insertSearchResult('${result.title}', '${result.body}')">
            <div class="search-result-title">${result.title}</div>
            <div class="search-result-body">${result.body.substring(0, 100)}...</div>
        </div>
    `).join('');

    resultsDiv.innerHTML = resultsHtml;
}

function insertSearchResult(title, body) {
    const messageInput = document.getElementById('messageInput');
    messageInput.value = `Based on the search result "${title}": ${body.substring(0, 200)}... Can you explain more about this?`;
    messageInput.focus();
}

// Export chat history
async function exportHistory() {
    try {
        const response = await fetch(`/export/history/?session_id=${sessionId}`);

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `chat_history_${sessionId}.csv`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            chatBot.showAlert('Chat history exported successfully!', 'success');
        } else {
            throw new Error('Export failed');
        }
    } catch (error) {
        console.error('Export error:', error);
        chatBot.showAlert('Export failed. Please try again.', 'danger');
    }
}

// Clear chat
function clearChat() {
    if (confirm('Are you sure you want to clear the chat history?')) {
        document.getElementById('chatMessages').innerHTML = `
            <div class="text-center text-muted mt-5">
                <i class="fas fa-comments fa-3x mb-3"></i>
                <h5>Chat Cleared!</h5>
                <p>Start a new conversation</p>
            </div>
        `;
        chatBot.showAlert('Chat history cleared!', 'info');
    }
}

// Show metrics modal
function showMetrics() {
    const modal = new bootstrap.Modal(document.getElementById('metricsModal'));
    modal.show();
    loadMetrics();
}

// Initialize chatbot when page loads
let chatBot;
document.addEventListener('DOMContentLoaded', function() {
    chatBot = new ChatBot();
});

// Handle page visibility changes
document.addEventListener('visibilitychange', function() {
    const statusBadge = document.getElementById('statusBadge');
    if (document.hidden) {
        statusBadge.textContent = 'Away';
        statusBadge.className = 'badge bg-warning';
    } else {
        statusBadge.textContent = 'Online';
        statusBadge.className = 'badge bg-success';
    }
});
