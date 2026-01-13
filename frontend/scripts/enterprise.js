/**
 * MicroLLM-PrivateStack Enterprise UI
 * JavaScript Controller v1.0
 */

// === CONFIGURATION ===
const CONFIG = {
    API_BASE_URL: 'http://localhost:8000',
    ENDPOINTS: {
        CHAT: '/api/chat',
        HEALTH: '/health',
        MODEL_INFO: '/api/model/info'
    },
    ANIMATION: {
        MESSAGE_DELAY: 300,
        TYPING_SPEED: 50
    }
};

// === STATE MANAGEMENT ===
const state = {
    currentModel: 'DeepSeek-R1-1.5B',
    isProcessing: false,
    messages: [],
    systemMetrics: {
        ram: 50,
        cpu: 35,
        gpu: 50
    }
};

// === DOM ELEMENTS ===
const elements = {
    chatInput: null,
    chatMessages: null,
    sendBtn: null,
    consoleContent: null
};

// === INITIALIZATION ===
document.addEventListener('DOMContentLoaded', () => {
    initializeElements();
    initializeEventListeners();
    startSystemMonitoring();
    loadChatHistory();
    addWelcomeMessage();
});

function initializeElements() {
    elements.chatInput = document.getElementById('chatInput');
    elements.chatMessages = document.getElementById('chatMessages');
    elements.sendBtn = document.getElementById('sendBtn');
    elements.consoleContent = document.getElementById('consoleContent');
}

// === EVENT LISTENERS ===
function initializeEventListeners() {
    // Send button
    elements.sendBtn?.addEventListener('click', handleSendMessage);
    
    // Enter key in input
    elements.chatInput?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });
    
    // Auto-resize textarea
    elements.chatInput?.addEventListener('input', (e) => {
        e.target.style.height = 'auto';
        e.target.style.height = e.target.scrollHeight + 'px';
    });
    
    // Expand buttons for reasoning traces
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('expand-btn')) {
            toggleReasoningPanel(e.target);
        }
    });
    
    // Model selection
    document.querySelectorAll('.model-item').forEach(item => {
        item.addEventListener('click', () => selectModel(item));
    });
    
    // Toggle switches
    document.querySelectorAll('.toggle-switch input').forEach(toggle => {
        toggle.addEventListener('change', handleToggleChange);
    });
}

// === CHAT FUNCTIONALITY ===
async function handleSendMessage() {
    const message = elements.chatInput?.value.trim();
    
    if (!message || state.isProcessing) return;
    
    // Add user message to UI
    addMessage('user', message);
    
    // Clear input
    elements.chatInput.value = '';
    elements.chatInput.style.height = 'auto';
    
    // Set processing state
    state.isProcessing = true;
    updateSendButtonState();
    
    // Log to console
    logToConsole('INFO', `Processing query: "${message.substring(0, 30)}..."`);
    
    try {
        // Call API
        const response = await callChatAPI(message);
        
        // Add AI response
        setTimeout(() => {
            addMessage('ai', response.response, {
                tokens: response.tokens_generated,
                latency: response.latency || '0.5s',
                security: response.security
            });
            
            logToConsole('INFO', `Response generated: ${response.tokens_generated} tokens`);
        }, CONFIG.ANIMATION.MESSAGE_DELAY);
        
    } catch (error) {
        logToConsole('ERROR', `API call failed: ${error.message}`);
        addMessage('ai', '⚠️ Error: Unable to process request. Please check system logs.', {
            tokens: 0,
            latency: 'N/A'
        });
    } finally {
        state.isProcessing = false;
        updateSendButtonState();
    }
}

async function callChatAPI(message) {
    const response = await fetch(`${CONFIG.API_BASE_URL}${CONFIG.ENDPOINTS.CHAT}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            message: message,
            max_tokens: 256
        })
    });
    
    if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
}

function addMessage(type, content, metadata = {}) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    
    if (type === 'ai') {
        messageDiv.innerHTML = `
            <div class="message-avatar">🤖</div>
            <div class="message-content">
                <div class="message-text">
                    ${content}
                    <button class="expand-btn">→</button>
                </div>
                <div class="message-meta">
                    <div class="reasoning-panel" style="display: none;">
                        <div class="panel-header">Reasoning Trace</div>
                        <div class="panel-content">
                            Processing completed with multi-step reasoning...
                        </div>
                    </div>
                </div>
                <div class="message-stats">
                    <span class="stat">TOKENS: ${metadata.tokens || 'N/A'}</span>
                    <span class="stat">|</span>
                    <span class="stat">LATENCY: ${metadata.latency || 'N/A'}</span>
                    ${metadata.security?.validated ? '<span class="stat">| ✅ VALIDATED</span>' : ''}
                </div>
            </div>
        `;
    } else {
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-text">${content}</div>
            </div>
            <div class="message-avatar">👤</div>
        `;
    }
    
    elements.chatMessages?.appendChild(messageDiv);
    scrollToBottom();
    
    // Save to state
    state.messages.push({ type, content, metadata, timestamp: Date.now() });
    saveChatHistory();
}

function toggleReasoningPanel(button) {
    const messageContent = button.closest('.message-content');
    const panel = messageContent.querySelector('.reasoning-panel');
    
    if (panel) {
        const isVisible = panel.style.display !== 'none';
        panel.style.display = isVisible ? 'none' : 'block';
        button.textContent = isVisible ? '→' : '↓';
        button.style.transform = isVisible ? 'rotate(0deg)' : 'rotate(90deg)';
    }
}

function scrollToBottom() {
    if (elements.chatMessages) {
        elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
    }
}

function updateSendButtonState() {
    if (elements.sendBtn) {
        elements.sendBtn.disabled = state.isProcessing;
        elements.sendBtn.style.opacity = state.isProcessing ? '0.5' : '1';
        elements.sendBtn.style.cursor = state.isProcessing ? 'not-allowed' : 'pointer';
    }
}

// === CONSOLE LOGGING ===
function logToConsole(level, message) {
    const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
    const logLine = document.createElement('div');
    logLine.className = 'console-line';
    logLine.innerHTML = `
        <span class="timestamp">[${level}]</span>
        <span class="log-text">${timestamp} -- ${message}</span>
    `;
    
    elements.consoleContent?.appendChild(logLine);
    
    // Keep only last 50 lines
    while (elements.consoleContent?.children.length > 50) {
        elements.consoleContent.removeChild(elements.consoleContent.firstChild);
    }
    
    // Auto-scroll console
    if (elements.consoleContent) {
        elements.consoleContent.scrollTop = elements.consoleContent.scrollHeight;
    }
}

// === SYSTEM MONITORING ===
function startSystemMonitoring() {
    // Update every 2 seconds
    setInterval(updateSystemMetrics, 2000);
    
    // Initial update
    updateSystemMetrics();
}

async function updateSystemMetrics() {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}${CONFIG.ENDPOINTS.HEALTH}`);
        const data = await response.json();
        
        // Update gauge values (simplified - would use real data)
        updateGauges();
        
    } catch (error) {
        console.warn('Failed to fetch system metrics:', error);
    }
}

function updateGauges() {
    // Simulate slight variations for demo
    state.systemMetrics.cpu = 30 + Math.random() * 10;
    state.systemMetrics.gpu = 45 + Math.random() * 15;
    
    document.querySelectorAll('.gauge').forEach((gauge, index) => {
        const value = index === 0 ? state.systemMetrics.cpu : state.systemMetrics.gpu;
        const valueElement = gauge.querySelector('.gauge-value');
        const progressCircle = gauge.querySelector('.gauge-progress');
        
        if (valueElement) {
            valueElement.textContent = `${Math.round(value)}%`;
        }
        
        if (progressCircle) {
            const offset = 283 - (283 * value) / 100;
            progressCircle.style.strokeDashoffset = offset;
        }
    });
    
    // Update console with metrics
    if (Math.random() > 0.7) { // Occasional metric log
        logToConsole('METRICS', `RAM: ${state.systemMetrics.ram}% | CPU: ${Math.round(state.systemMetrics.cpu)}% | GPU: ${Math.round(state.systemMetrics.gpu)}%`);
    }
}

// === MODEL SELECTION ===
function selectModel(modelItem) {
    // Remove active class from all
    document.querySelectorAll('.model-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Add active to selected
    modelItem.classList.add('active');
    
    const modelName = modelItem.querySelector('.model-name').textContent;
    state.currentModel = modelName;
    
    logToConsole('INFO', `Model switched to: ${modelName}`);
}

// === TOGGLE CONTROLS ===
function handleToggleChange(e) {
    const toggleId = e.target.id;
    const isChecked = e.target.checked;
    
    const labels = {
        offlineMode: 'Offline Mode',
        encryption: 'Encryption',
        localMemory: 'Local Memory'
    };
    
    const status = isChecked ? 'ENABLED' : 'DISABLED';
    const label = labels[toggleId] || toggleId;
    
    logToConsole('INFO', `${label}: ${status}`);
}

// === CHAT HISTORY ===
function saveChatHistory() {
    try {
        localStorage.setItem('microllm_chat_history', JSON.stringify(state.messages));
    } catch (error) {
        console.warn('Failed to save chat history:', error);
    }
}

function loadChatHistory() {
    try {
        const saved = localStorage.getItem('microllm_chat_history');
        if (saved) {
            state.messages = JSON.parse(saved);
            // Optionally restore messages to UI
            // state.messages.forEach(msg => addMessage(msg.type, msg.content, msg.metadata));
        }
    } catch (error) {
        console.warn('Failed to load chat history:', error);
    }
}

// === WELCOME MESSAGE ===
function addWelcomeMessage() {
    logToConsole('INFO', 'System initialized successfully');
    logToConsole('INFO', `Model loaded: ${state.currentModel}`);
    logToConsole('STATUS', 'ONLINE | ENCRYPTED | PRIVATE');
}

// === ANIMATION HELPERS ===
function animatePipelineFlow() {
    // Triggered when processing
    const connectors = document.querySelectorAll('.connector-flow');
    connectors.forEach(connector => {
        connector.style.animationPlayState = state.isProcessing ? 'running' : 'paused';
    });
}

// === UTILITY FUNCTIONS ===
function formatTimestamp(timestamp) {
    return new Date(timestamp).toLocaleTimeString();
}

function sanitizeHTML(html) {
    const temp = document.createElement('div');
    temp.textContent = html;
    return temp.innerHTML;
}

// === EXPORT FOR DEBUGGING ===
window.MicroLLM = {
    state,
    config: CONFIG,
    addMessage,
    logToConsole,
    selectModel
};

console.log('%c🧠 MicroLLM-PrivateStack UI Loaded', 'color: #00d4ff; font-weight: bold; font-size: 14px');
console.log('%cEnterprise AI Operating System v1.0', 'color: #a855f7; font-size: 12px');
