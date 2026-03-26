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

// ── Trust boundary: ALL dynamic content via textContent, never innerHTML ──
// REMEDIATION (2026-03-26): app.js had identical XSS sink to enterprise.js
function addMessage(role, content) {
    const messageId = `msg-${Date.now()}`;
    const messageDiv = document.createElement('div');
    messageDiv.id = messageId;
    messageDiv.className = `message ${role}`;

    const ICONS = { user: '👤', assistant: '🤖' };
    const icon = ICONS[role] ?? 'ℹ️';
    const label = role.charAt(0).toUpperCase() + role.slice(1);

    // Header
    const header = document.createElement('div');
    header.className = 'message-header';

    const iconEl = document.createElement('span');
    iconEl.className = 'message-icon';
    iconEl.textContent = icon;          // emoji — safe literal

    const labelEl = document.createElement('strong');
    labelEl.textContent = label + ':';  // role label — safe literal

    header.appendChild(iconEl);
    header.appendChild(labelEl);

    // Content — UNTRUSTED: model output or user input, always textContent
    const contentEl = document.createElement('div');
    contentEl.className = 'message-content';
    contentEl.textContent = String(content ?? '');

    messageDiv.appendChild(header);
    messageDiv.appendChild(contentEl);

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
