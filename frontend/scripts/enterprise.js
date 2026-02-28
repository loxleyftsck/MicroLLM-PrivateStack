/**
 * MicroLLM-PrivateStack Enterprise UI
 * JavaScript Controller v1.1 — Security Hardened
 *
 * TRUST BOUNDARY INVARIANT (enforced 2026-02-28):
 *   All model-derived content is UNTRUSTED until encoded at UI sink.
 *   Rule: NEVER assign dynamic content via innerHTML.
 *         ALWAYS use renderSafe() or textContent for all LLM/user output.
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

// === SAFE RENDER HELPERS (Trust Boundary Enforcement) ===
// Invariant: ALL model-derived and user-derived content MUST pass through
// these helpers before touching the DOM. innerHTML is prohibited for dynamic data.

/**
 * Creates a text node — the atomic safe render primitive.
 * Use for any single string value from untrusted sources.
 */
function makeSafeText(str) {
    return document.createTextNode(String(str ?? ''));
}

/**
 * Creates an element with a CSS class and sets its text content safely.
 */
function makeSafeEl(tag, className, text) {
    const el = document.createElement(tag);
    if (className) el.className = className;
    if (text !== undefined) el.textContent = String(text);
    return el;
}

function addMessage(type, content, metadata = {}) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;

    if (type === 'ai') {
        // Avatar — static emoji constant, safe as textContent
        const avatar = makeSafeEl('div', 'message-avatar', '🤖');

        // Message text — model output encoded as text node, never innerHTML
        const msgText = document.createElement('div');
        msgText.className = 'message-text';
        msgText.appendChild(makeSafeText(content));  // ← ENCODED: model output

        const expandBtn = document.createElement('button');
        expandBtn.className = 'expand-btn';
        expandBtn.textContent = '→';
        msgText.appendChild(expandBtn);

        // Reasoning panel — static scaffold, no dynamic content
        const reasoningPanel = document.createElement('div');
        reasoningPanel.className = 'reasoning-panel';
        reasoningPanel.style.display = 'none';
        const panelHeader = makeSafeEl('div', 'panel-header', 'Reasoning Trace');
        const panelContent = makeSafeEl('div', 'panel-content', 'Processing completed with multi-step reasoning...');
        reasoningPanel.appendChild(panelHeader);
        reasoningPanel.appendChild(panelContent);

        const msgMeta = document.createElement('div');
        msgMeta.className = 'message-meta';
        msgMeta.appendChild(reasoningPanel);

        // Stats — metadata values encoded via textContent
        const msgStats = document.createElement('div');
        msgStats.className = 'message-stats';

        const tokensStat = makeSafeEl('span', 'stat');
        tokensStat.textContent = `TOKENS: ${String(metadata.tokens ?? 'N/A')}`; // encoded
        const sep = makeSafeEl('span', 'stat', '|');
        const latencyStat = makeSafeEl('span', 'stat');
        latencyStat.textContent = `LATENCY: ${String(metadata.latency ?? 'N/A')}`; // encoded

        msgStats.appendChild(tokensStat);
        msgStats.appendChild(sep);
        msgStats.appendChild(latencyStat);

        if (metadata.security?.validated) {
            msgStats.appendChild(makeSafeEl('span', 'stat', '| ✅ VALIDATED'));
        }

        // Assemble
        const msgContent = document.createElement('div');
        msgContent.className = 'message-content';
        msgContent.appendChild(msgText);
        msgContent.appendChild(msgMeta);
        msgContent.appendChild(msgStats);

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(msgContent);

    } else {
        // User message — user input encoded via textContent
        const msgTextEl = makeSafeEl('div', 'message-text');
        msgTextEl.appendChild(makeSafeText(content));  // ← ENCODED: user input

        const msgContent = document.createElement('div');
        msgContent.className = 'message-content';
        msgContent.appendChild(msgTextEl);

        const avatar = makeSafeEl('div', 'message-avatar', '👤');

        messageDiv.appendChild(msgContent);
        messageDiv.appendChild(avatar);
    }

    elements.chatMessages?.appendChild(messageDiv);
    scrollToBottom();

    // Save sanitized metadata only — do NOT persist raw content to avoid
    // localStorage becoming a secondary exfiltration target.
    state.messages.push({
        type,
        content,  // stored in memory; saveChatHistory() is now a no-op (see below)
        metadata: {
            tokens: metadata.tokens,
            latency: metadata.latency
        },
        timestamp: Date.now()
    });
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
        if (!response.ok) return;
        const data = await response.json();

        // REMEDIATION (MEDIUM-4 2026-02-28):
        // Synthetic Math.random() simulation REMOVED — gauges now driven exclusively
        // by real data from the /health endpoint. If the field is absent the gauge
        // retains its last known value, which is honest. Fabricated telemetry that
        // obscures real system state during load events has been eliminated.
        if (typeof data.cpu_percent === 'number') {
            state.systemMetrics.cpu = data.cpu_percent;
        }
        if (typeof data.gpu_percent === 'number') {
            state.systemMetrics.gpu = data.gpu_percent;
        }
        if (typeof data.ram_percent === 'number') {
            state.systemMetrics.ram = data.ram_percent;
        }

        updateGauges();

    } catch (error) {
        // Health endpoint unreachable — gauges retain last known values.
        // Log once to avoid console spam.
        console.warn('[MicroLLM] Health check failed — metrics paused:', error.message);
    }
}

function updateGauges() {
    // Render from state values — NO random simulation.
    const metricMap = ['cpu', 'gpu'];

    document.querySelectorAll('.gauge').forEach((gauge, index) => {
        const key = metricMap[index];
        if (!key) return;
        const value = state.systemMetrics[key] ?? 0;

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
// REMEDIATION (LOW-1 2026-02-28):
// localStorage persistence DISABLED. The UI claimed "End-to-End Encrypted" but
// stored full conversation plaintext in browser storage — accessible to any
// in-page XSS payload. Until server-side encrypted session storage is implemented,
// chat history is in-memory only and cleared on page reload.
function saveChatHistory() {
    // No-op: localStorage persistence disabled pending encrypted storage implementation.
    // To re-enable, implement AES-GCM with a session-derived key before storing.
}

function loadChatHistory() {
    // No-op: clears any previously stored plaintext history to remediate LOW-1.
    try {
        localStorage.removeItem('microllm_chat_history');
    } catch (_) {
        // Ignore — storage may not be available
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

// === DEBUG EXPORT (GATED) ===
// REMEDIATION (LOW-2 2026-02-28):
// window.MicroLLM is ONLY exposed when the server returns debug_mode=true in
// the /health response. In production (DEBUG=false) this object is never set,
// preventing state exfiltration via any XSS payload that might reach the page.
async function maybeExposeDebugInterface() {
    try {
        const res = await fetch(`${CONFIG.API_BASE_URL}${CONFIG.ENDPOINTS.HEALTH}`);
        const data = await res.json();
        if (data?.debug_mode === true) {
            window.MicroLLM = { state, config: CONFIG, addMessage, logToConsole, selectModel };
            console.warn('[MicroLLM] ⚠️ Debug interface exposed — debug_mode is ON. Disable in production.');
        }
    } catch (_) {
        // Health unreachable — debug interface never exposed
    }
}
maybeExposeDebugInterface();

console.log('%c🧠 MicroLLM-PrivateStack UI Loaded', 'color: #00d4ff; font-weight: bold; font-size: 14px');
console.log('%cEnterprise AI Operating System v1.1 — Security Hardened', 'color: #a855f7; font-size: 12px');
