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
        METRICS: '/api/metrics/system',
        WORKSPACES: '/api/workspaces',
        HISTORY: '/api/chat/history/'
    }
};

// === STATE ===
const state = {
    theme: 'light',
    panelCollapsed: false,
    messages: [],
    workspaces: [],
    currentWorkspaceId: null
};

// === DOM ELEMENTS ===
const elements = {
    chatInput: null,
    sendBtn: null,
    chatContainer: null,
    themeToggle: null,
    collapseBtn: null,
    aiDetails: null,
    logoutBtn: null,
    workspaceBtn: null,
    workspaceDropdown: null
};

// === INITIALIZATION ===
document.addEventListener('DOMContentLoaded', () => {
    // Check authentication first
    if (!checkAuth()) {
        return; // Will redirect to login
    }
    
    initializeElements();
    initializeEventListeners();
    loadAIDetails();
    loadSystemMetrics();
    loadUserInfo();
    loadWorkspaces();
    
    // Auto-update metrics every 10 seconds
    setInterval(loadSystemMetrics, 10000);
});

async function loadWorkspaces() {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}${CONFIG.ENDPOINTS.WORKSPACES}`, {
            headers: getAuthHeaders()
        });
        
        if (handleApiError(response)) return;
        
        const data = await response.json();
        state.workspaces = data.workspaces;
        
        if (state.workspaces.length > 0) {
            state.currentWorkspaceId = state.workspaces[0].id;
            updateWorkspaceUI();
            loadChatHistory(state.currentWorkspaceId);
        }
    } catch (error) {
        console.error('Failed to load workspaces:', error);
    }
}

async function loadChatHistory(workspaceId) {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}${CONFIG.ENDPOINTS.HISTORY}${workspaceId}`, {
            headers: getAuthHeaders()
        });
        
        if (handleApiError(response)) return;
        
        const data = await response.json();
        
        // Clear chat container
        elements.chatContainer.innerHTML = '';
        
        if (data.history.length === 0) {
            showWelcomeCard();
        } else {
            data.history.forEach(msg => {
                const role = msg.role === 'user' ? 'user' : 'ai';
                addMessageToUI(role, msg.message);
            });
        }
    } catch (error) {
        console.error('Failed to load history:', error);
    }
}

function updateWorkspaceUI() {
    const workspaceName = document.querySelector('.workspace-name');
    const current = state.workspaces.find(w => w.id === state.currentWorkspaceId);
    if (workspaceName && current) {
        workspaceName.textContent = current.name;
    }
    
    // Update list
    const list = document.querySelector('.workspace-list');
    if (list) {
        list.innerHTML = state.workspaces.map(w => `
            <div class="workspace-item ${w.id === state.currentWorkspaceId ? 'active' : ''}" data-id="${w.id}">
                <span class="workspace-icon">📁</span>
                <span>${w.name}</span>
            </div>
        `).join('');
        
        // Add listeners
        list.querySelectorAll('.workspace-item').forEach(item => {
            item.addEventListener('click', () => {
                const id = item.dataset.id;
                state.currentWorkspaceId = id;
                updateWorkspaceUI();
                loadChatHistory(id);
            });
        });
    }
}

function showWelcomeCard() {
    elements.chatContainer.innerHTML = `
        <div class="welcome-card">
            <div class="welcome-header">
                <h2>Private AI Workspace</h2>
                <p class="welcome-subtitle">Confidential. Compliant. On-premise.</p>
            </div>
            <div class="welcome-features">
                <div class="feature-item">
                    <span class="feature-check">✓</span>
                    <span>Your data never leaves your company</span>
                </div>
                <div class="feature-item">
                    <span class="feature-check">✓</span>
                    <span>GDPR, SOC 2, ISO 27001 compliant</span>
                </div>
                <div class="feature-item">
                    <span class="feature-check">✓</span>
                    <span>End-to-end encrypted</span>
                </div>
            </div>
            <div class="welcome-cta">
                <p class="cta-text">Ask a question to get started</p>
            </div>
        </div>
    `;
}

function addMessageToUI(type, content) {
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
}

// === AUTHENTICATION ===
function checkAuth() {
    const token = localStorage.getItem('auth_token');
    if (!token) {
        window.location.href = 'login.html';
        return false;
    }
    return true;
}

function getAuthHeaders() {
    const token = localStorage.getItem('auth_token');
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
}

function logout() {
    fetch(`${CONFIG.API_BASE_URL}/api/auth/logout`, {
        method: 'POST',
        headers: getAuthHeaders()
    }).finally(() => {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
        window.location.href = 'login.html';
    });
}

function loadUserInfo() {
    const user = localStorage.getItem('user');
    if (user) {
        const userData = JSON.parse(user);
        const userName = document.getElementById('userName');
        if (userName) {
            userName.textContent = userData.display_name || userData.email || 'User';
        }
    }
}

// Handle 401 responses globally
function handleApiError(response) {
    if (response.status === 401) {
        logout();
        return true;
    }
    return false;
}

function initializeElements() {
    elements.chatInput = document.getElementById('chatInput');
    elements.sendBtn = document.getElementById('sendBtn');
    elements.chatContainer = document.getElementById('chatContainer');
    elements.themeToggle = document.getElementById('themeToggle');
    elements.collapseBtn = document.getElementById('collapseBtn');
    elements.aiDetails = document.getElementById('aiDetails');
    elements.logoutBtn = document.getElementById('logoutBtn');
    elements.workspaceBtn = document.getElementById('workspaceBtn');
    elements.workspaceDropdown = document.getElementById('workspaceDropdown');
    elements.uploadBtn = document.getElementById('uploadBtn');
    elements.fileInput = document.getElementById('fileInput');
}

// === EVENT LISTENERS ===
function initializeEventListeners() {
    // Send message
    elements.sendBtn?.addEventListener('click', sendMessage);
    
    // Enter to send
    elements.chatInput?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault(); // Keep preventDefault to stop newline in textarea
            sendMessage();
        }
    });
    
    // Theme toggle
    elements.themeToggle?.addEventListener('click', toggleTheme);
    
    // Panel collapse
    elements.collapseBtn?.addEventListener('click', togglePanel);
    
    // Logout
    elements.logoutBtn?.addEventListener('click', logout);
    
    // Workspace dropdown
    elements.workspaceBtn?.addEventListener('click', (e) => {
        e.stopPropagation();
        elements.workspaceDropdown?.classList.toggle('show');
    });
    
    // Close dropdowns on click outside
    document.addEventListener('click', (e) => {
        if (!elements.workspaceBtn?.contains(e.target)) {
            elements.workspaceDropdown?.classList.remove('show');
        }
    });

    // File Upload Handlers
    elements.uploadBtn?.addEventListener('click', () => elements.fileInput?.click());
    
    elements.fileInput?.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        await handleFileUpload(file);
        elements.fileInput.value = ''; // Reset
    });

    // Quick actions
    document.querySelectorAll('.quick-action-btn').forEach(btn => {
        btn.addEventListener('click', handleQuickAction);
    });
}

async function handleFileUpload(file) {
    addMessageToUI('user', `📎 Uploading ${file.name}...`);
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const token = localStorage.getItem('auth_token');
        const response = await fetch(`${CONFIG.API_BASE_URL}/api/documents/upload`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });
        
        if (handleApiError(response)) return;
        
        const data = await response.json();
        
        if (response.ok) {
            addMessageToUI('ai', `✅ Document "${file.name}" added to knowledge base! (${data.chunks_added} chunks)`);
        } else {
            addMessageToUI('ai', `❌ Upload failed: ${data.error}`);
        }
    } catch (error) {
        addMessageToUI('ai', `❌ Network error: ${error.message}`);
    }
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
        // Call API with auth headers
        const response = await fetch(`${CONFIG.API_BASE_URL}${CONFIG.ENDPOINTS.CHAT}`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                message: message,
                max_tokens: 256,
                workspace_id: state.currentWorkspaceId
            })
        });
        
        // Handle 401 (unauthorized)
        if (handleApiError(response)) return;
        
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
