/**
 * MicroLLM-PrivateStack Corporate UI
 * Clean, simplified JavaScript for business users
 */

// === CONFIGURATION ===
const CONFIG = {
    API_BASE_URL: 'http://localhost:8000',
    ENDPOINTS: {
        CHAT: '/api/chat',
        MODELS: '/api/models/list',
        SECURITY: '/api/security/status',
        METRICS: '/api/metrics/system'
    }
};

// === STATE ===
const state = {
    theme: 'light',
    panelCollapsed: false,
    messages: []
};

// === DOM ELEMENTS ===
const elements = {
    chatInput: null,
    sendBtn: null,
    chatContainer: null,
    themeToggle: null,
    collapseBtn: null,
    aiDetails: null
};

// === INITIALIZATION ===
document.addEventListener('DOMContentLoaded', () => {
    initializeElements();
    initializeEventListeners();
    loadAIDetails();
    loadSystemMetrics();
    
    // Auto-update metrics every 10 seconds
    setInterval(loadSystemMetrics, 10000);
});

function initializeElements() {
    elements.chatInput = document.getElementById('chatInput');
    elements.sendBtn = document.getElementById('sendBtn');
    elements.chatContainer = document.getElementById('chatContainer');
    elements.themeToggle = document.getElementById('themeToggle');
    elements.collapseBtn = document.getElementById('collapseBtn');
    elements.aiDetails = document.getElementById('aiDetails');
}

// === EVENT LISTENERS ===
function initializeEventListeners() {
    // Send message
    elements.sendBtn?.addEventListener('click', sendMessage);
    
    // Enter to send
    elements.chatInput?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Theme toggle
    elements.themeToggle?.addEventListener('click', toggleTheme);
    
    // Panel collapse
    elements.collapseBtn?.addEventListener('click', togglePanel);
    
    // Quick actions
    document.querySelectorAll('.quick-action-btn').forEach(btn => {
        btn.addEventListener('click', handleQuickAction);
    });
}

// === CHAT FUNCTIONALITY ===
async function sendMessage() {
    const message = elements.chatInput?.value.trim();
    
    if (!message) return;
    
    // Add user message to UI
    addMessage('user', message);
    
    // Clear input
    elements.chatInput.value = '';
    
    try {
        // Call API
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
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        // Add AI response
        addMessage('ai', data.response || data.message || 'No response');
        
    } catch (error) {
        console.error('Chat error:', error);
        addMessage('ai', '⚠️ Sorry, I encountered an error. Please try again.');
    }
}

function addMessage(type, content) {
    // Remove welcome card if exists
    const welcomeCard = document.querySelector('.welcome-card');
    if (welcomeCard) {
        welcomeCard.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = content;
    
    messageDiv.appendChild(contentDiv);
    elements.chatContainer?.appendChild(messageDiv);
    
    // Scroll to bottom
    elements.chatContainer.scrollTop = elements.chatContainer.scrollHeight;
    
    // Save to state
    state.messages.push({
        type,
        content,
        timestamp: Date.now()
    });
}

// === AI DETAILS PANEL ===
async function loadAIDetails() {
    try {
        // Load model info
        const modelsResponse = await fetch(`${CONFIG.API_BASE_URL}${CONFIG.ENDPOINTS.MODELS}`);
        if (modelsResponse.ok) {
            const modelsData = await modelsResponse.json();
            document.getElementById('modelName').textContent = modelsData.loaded || 'DeepSeek-R1-1.5B';
        }
        
        // Load security info
        const securityResponse = await fetch(`${CONFIG.API_BASE_URL}${CONFIG.ENDPOINTS.SECURITY}`);
        if (securityResponse.ok) {
            const securityData = await securityResponse.json();
            document.getElementById('encryptionType').textContent = 
                `Encryption: ${securityData.encryption || 'AES-256'}`;
            
            const compliance = securityData.compliance?.join(', ') || 'GDPR, SOC 2';
            document.getElementById('complianceInfo').textContent = 
                `Compliance: ${compliance}`;
        }
        
    } catch (error) {
        console.warn('Failed to load AI details:', error);
        // Keep default values
    }
}

async function loadSystemMetrics() {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}${CONFIG.ENDPOINTS.METRICS}`);
        
        if (response.ok) {
            const data = await response.json();
            
            // Update RAM usage
            const ramUsage = `${data.ram_used_gb?.toFixed(1) || '1.3'}GB / ${data.ram_total_gb?.toFixed(1) || '2.0'}GB`;
            document.getElementById('ramUsage').textContent = ramUsage;
            
            // Update system status based on RAM
            const ramPercent = data.ram_percent || 65;
            let status = 'Optimal';
            if (ramPercent > 85) status = 'High Usage';
            if (ramPercent > 95) status = 'Critical';
            
            document.getElementById('systemStatus').textContent = status;
        }
    } catch (error) {
        console.warn('Failed to load system metrics:', error);
        // Show fallback data
        document.getElementById('ramUsage').textContent = 'Loading...';
    }
}

// === THEME TOGGLE ===
function toggleTheme() {
    state.theme = state.theme === 'light' ? 'dark' : 'light';
    document.body.setAttribute('data-theme', state.theme);
    
    // Update icon
    const icon = elements.themeToggle.querySelector('.theme-icon');
    if (icon) {
        icon.textContent = state.theme === 'light' ? '🌙' : '☀️';
    }
    
    // Save preference
    localStorage.setItem('theme', state.theme);
}

// === PANEL COLLAPSE ===
function togglePanel() {
    state.panelCollapsed = !state.panelCollapsed;
    
    if (state.panelCollapsed) {
        elements.aiDetails?.classList.add('collapsed');
        elements.collapseBtn.textContent = '+';
    } else {
        elements.aiDetails?.classList.remove('collapsed');
        elements.collapseBtn.textContent = '−';
    }
}

// === QUICK ACTIONS ===
function handleQuickAction(e) {
    const button = e.currentTarget;
    const actionText = button.querySelector('span:last-child')?.textContent;
    
    const actionMessages = {
        'Analyze Report': 'Please analyze the latest quarterly report and highlight key trends.',
        'Draft Summary': 'Can you draft an executive summary of our recent project outcomes?',
        'Search Documents': 'Search for compliance documents related to data privacy.'
    };
    
    const message = actionMessages[actionText] || actionText;
    
    if (elements.chatInput) {
        elements.chatInput.value = message;
        elements.chatInput.focus();
    }
}

// === LOAD SAVED THEME ===
const savedTheme = localStorage.getItem('theme');
if (savedTheme) {
    state.theme = savedTheme;
    document.body.setAttribute('data-theme', savedTheme);
    
    const icon = document.querySelector('.theme-icon');
    if (icon) {
        icon.textContent = savedTheme === 'light' ? '🌙' : '☀️';
    }
}

// === EXPORT FOR DEBUGGING ===
window.MicroLLMCorporate = {
    state,
    config: CONFIG,
    sendMessage,
    loadAIDetails,
    loadSystemMetrics
};

console.log('✅ MicroLLM-PrivateStack Corporate UI Loaded');
console.log('📧 For: Legal teams, executives, analysts, compliance officers');
