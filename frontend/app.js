/**
 * MicroLLM-PrivateStack Frontend JavaScript
 */

const API_URL = 'http://localhost:8000';

// DOM Elements
const messagesDiv = document.getElementById('messages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const statusIndicator = document.getElementById('statusIndicator');
const statusText = document.getElementById('statusText');

// Check API health
async function checkHealth() {
    try {
        const response = await fetch(`${API_URL}/health`);
        const data = await response.json();
        
        if (data.status === 'healthy') {
            statusIndicator.className = 'status-indicator online';
            statusText.textContent = 'Connected';
        }
    } catch (error) {
        statusIndicator.className = 'status-indicator offline';
        statusText.textContent = 'Offline';
    }
}

// Send message
async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    // Add user message to chat
    addMessage('user', message);
    messageInput.value = '';

    // Show loading
    const loadingId = addMessage('assistant', 'Thinking...');

    try {
        const response = await fetch(`${API_URL}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message })
        });

        const data = await response.json();
        
        // Replace loading with actual response
        const loadingElement = document.getElementById(loadingId);
        if (loadingElement) {
            loadingElement.remove();
        }
        
        addMessage('assistant', data.response);
    } catch (error) {
        addMessage('system', 'Error: Could not connect to API');
    }
}

// Add message to chat
function addMessage(role, content) {
    const messageId = `msg-${Date.now()}`;
    const messageDiv = document.createElement('div');
    messageDiv.id = messageId;
    messageDiv.className = `message ${role}`;
    
    const icon = role === 'user' ? '👤' : role === 'assistant' ? '🤖' : 'ℹ️';
    const label = role.charAt(0).toUpperCase() + role.slice(1);
    
    messageDiv.innerHTML = `
        <div class="message-header">
            <span class="message-icon">${icon}</span>
            <strong>${label}:</strong>
        </div>
        <div class="message-content">${content}</div>
    `;
    
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    
    return messageId;
}

// Event listeners
sendButton.addEventListener('click', sendMessage);
messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Initialize
checkHealth();
setInterval(checkHealth, 30000); // Check every 30 seconds
