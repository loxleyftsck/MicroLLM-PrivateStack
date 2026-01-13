/**
 * Panel Management for AI Assistants, Security, Settings
 */

// === AI ASSISTANTS PANEL ===
let assistantsVisible = false;
let currentAssistant = 'general';

const ASSISTANTS = {
    legal: {
        name: 'Legal Assistant',
        icon: '⚖️',
        description: 'Specialized in contract analysis, compliance review, and legal research',
        badge: 'Legal Expert',
        systemPrompt: 'You are a professional legal assistant specializing in contract analysis and compliance.'
    },
    finance: {
        name: 'Financial Analyst',
        icon: '💼',
        description: 'Expert in financial analysis, budgeting, and data-driven insights',
        badge: 'Finance Expert',
        systemPrompt: 'You are a financial analyst providing data-driven insights and quantitative analysis.'
    },
    general: {
        name: 'General Assistant',
        icon: '🤝',
        description: 'Balanced conversational AI for general business tasks',
        badge: 'General Purpose',
        systemPrompt: 'You are a helpful business assistant providing balanced, professional responses.'
    },
    compliance: {
        name: 'Compliance Officer',
        icon: '📋',
        description: 'Focused on regulatory compliance, risk assessment, and policy review',
        badge: 'Compliance',
        systemPrompt: 'You are a compliance officer focused on regulatory requirements and risk management.'
    }
};

function toggleAssistantsPanel() {
    assistantsVisible = !assistantsVisible;
    let panel = document.getElementById('assistantsPanel');
    
    if (!panel) {
        panel = createAssistantsPanel();
        document.querySelector('.app-container').appendChild(panel);
    }
    
    panel.classList.toggle('show', assistantsVisible);
    
    // Hide other panels
    if (assistantsVisible) {
        document.getElementById('documentsPanel')?.classList.remove('show');
        document.getElementById('securityPanel')?.classList.remove('show');
        document.getElementById('settingsPanel')?.classList.remove('show');
    }
}

function createAssistantsPanel() {
    const panel = document.createElement('div');
    panel.id = 'assistantsPanel';
    panel.className = 'assistants-panel';
    
    const assistantCards = Object.entries(ASSISTANTS).map(([id, assistant]) => `
        <div class="assistant-card ${id === currentAssistant ? 'active' : ''}" data-assistant="${id}">
            <div class="assistant-icon">${assistant.icon}</div>
            <h4>${assistant.name}</h4>
            <p>${assistant.description}</p>
            <span class="assistant-badge">${assistant.badge}</span>
        </div>
    `).join('');
    
    panel.innerHTML = `
        <div class="assistants-header">
            <h2>AI Assistants</h2>
            <p>Choose the right AI assistant for your specific task</p>
        </div>
        <div class="assistant-grid">
            ${assistantCards}
        </div>
    `;
    
    // Setup click handlers
    setTimeout(() => {
        panel.querySelectorAll('.assistant-card').forEach(card => {
            card.addEventListener('click', function() {
                const assistantId = this.dataset.assistant;
                switchAssistant(assistantId);
            });
        });
    }, 100);
    
    return panel;
}

function switchAssistant(assistantId) {
    currentAssistant = assistantId;
    
    // Update UI
    document.querySelectorAll('.assistant-card').forEach(card => {
        card.classList.toggle('active', card.dataset.assistant === assistantId);
    });
    
    // Update chat configuration
    const assistant = ASSISTANTS[assistantId];
    console.log(`Switched to: ${assistant.name}`);
    console.log(`System prompt: ${assistant.systemPrompt}`);
    
    // Show notification
    alert(`Now using: ${assistant.name}\n\n${assistant.description}`);
}

// === SECURITY PANEL ===
let securityVisible = false;

function toggleSecurityPanel() {
    securityVisible = !securityVisible;
    let panel = document.getElementById('securityPanel');
    
    if (!panel) {
        panel = createSecurityPanel();
        document.querySelector('.app-container').appendChild(panel);
    }
    
    panel.classList.toggle('show', securityVisible);
    
    // Hide other panels
    if (securityVisible) {
        document.getElementById('documentsPanel')?.classList.remove('show');
        document.getElementById('assistantsPanel')?.classList.remove('show');
        document.getElementById('settingsPanel')?.classList.remove('show');
    }
}

function createSecurityPanel() {
    const panel = document.createElement('div');
    panel.id = 'securityPanel';
    panel.className = 'security-panel';
    
    panel.innerHTML = `
        <div class="security-header">
            <h2>Security & Compliance</h2>
            <p>Manage security settings and compliance features</p>
        </div>
        
        <div class="settings-section">
            <h3>Privacy Protection</h3>
            <div class="setting-item">
                <div class="setting-info">
                    <h4>PII Masking</h4>
                    <p>Automatically mask personally identifiable information</p>
                </div>
                <label class="toggle-switch">
                    <input type="checkbox" checked id="togglePII">
                    <span class="toggle-slider"></span>
                </label>
            </div>
            <div class="setting-item">
                <div class="setting-info">
                    <h4>Prompt Injection Detection</h4>
                    <p>Block potential prompt injection attacks</p>
                </div>
                <label class="toggle-switch">
                    <input type="checkbox" checked id="toggleInjection">
                    <span class="toggle-slider"></span>
                </label>
            </div>
        </div>
        
        <div class="settings-section">
            <h3>Content Filtering</h3>
            <div class="setting-item">
                <div class="setting-info">
                    <h4>Toxicity Filter</h4>
                    <p>Filter harmful or inappropriate content</p>
                </div>
                <label class="toggle-switch">
                    <input type="checkbox" checked id="toggleToxicity">
                    <span class="toggle-slider"></span>
                </label>
            </div>
            <div class="setting-item">
                <div class="setting-info">
                    <h4>Hallucination Detection</h4>
                    <p>Warn about potentially fabricated information</p>
                </div>
                <label class="toggle-switch">
                    <input type="checkbox" checked id="toggleHallucination">
                    <span class="toggle-slider"></span>
                </label>
            </div>
        </div>
        
        <div class="settings-section">
            <h3>Compliance</h3>
            <div class="setting-item">
                <div class="setting-info">
                    <h4>Compliance Mode</h4>
                    <p>Current: GDPR + SOC 2 + ISO 27001</p>
                </div>
                <span class="compliance-badge success">
                    <span class="badge-check">✓</span>
                    <span>Active</span>
                </span>
            </div>
            <div class="setting-item">
                <div class="setting-info">
                    <h4>Audit Logging</h4>
                    <p>Track all system activities for compliance</p>
                </div>
                <label class="toggle-switch">
                    <input type="checkbox" checked id="toggleAudit">
                    <span class="toggle-slider"></span>
                </label>
            </div>
        </div>
    `;
    
    return panel;
}

// === SETTINGS PANEL ===
let settingsVisible = false;

function toggleSettingsPanel() {
    settingsVisible = !settingsVisible;
    let panel = document.getElementById('settingsPanel');
    
    if (!panel) {
        panel = createSettingsPanel();
        document.querySelector('.app-container').appendChild(panel);
    }
    
    panel.classList.toggle('show', settingsVisible);
    
    // Hide other panels
    if (settingsVisible) {
        document.getElementById('documentsPanel')?.classList.remove('show');
        document.getElementById('assistantsPanel')?.classList.remove('show');
        document.getElementById('securityPanel')?.classList.remove('show');
    }
}

function createSettingsPanel() {
    const panel = document.createElement('div');
    panel.id = 'settingsPanel';
    panel.className = 'settings-panel';
    
    panel.innerHTML = `
        <div class="settings-header">
            <h2>Settings</h2>
            <p>Manage your preferences and system configuration</p>
        </div>
        
        <div class="settings-tabs">
            <button class="settings-tab active" data-tab="general">General</button>
            <button class="settings-tab" data-tab="appearance">Appearance</button>
            <button class="settings-tab" data-tab="ai">AI Configuration</button>
        </div>
        
        <div class="settings-content" id="settingsContent">
            <div class="settings-section">
                <h3>User Information</h3>
                <div class="form-group">
                    <label>Display Name</label>
                    <input type="text" value="Corporate User"  placeholder="Your name">
                </div>
                <div class="form-group">
                    <label>Email</label>
                    <input type="email" value="user@company.com" placeholder="your@email.com">
                </div>
            </div>
            
            <div class="settings-section">
                <h3>Preferences</h3>
                <div class="form-group">
                    <label>Language</label>
                    <select>
                        <option>English</option>
                        <option>Indonesian</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Timezone</label>
                    <select>
                        <option>UTC+7 (Jakarta)</option>
                        <option>UTC+0 (GMT)</option>
                    </select>
                </div>
            </div>
            
            <button class="save-btn">Save Changes</button>
        </div>
    `;
    
    return panel;
}

// === NAVIGATION HANDLER ===
function handleNavigation(navLabel) {
    // Close chat messages (if needed)
    const chatVisible = document.querySelector('.workspace')?.style.display !== 'none';
    
    switch(navLabel) {
        case 'Chats':
            // Show main workspace, hide all panels
            document.getElementById('documentsPanel')?.classList.remove('show');
            document.getElementById('assistantsPanel')?.classList.remove('show');
            document.getElementById('securityPanel')?.classList.remove('show');
            document.getElementById('settingsPanel')?.classList.remove('show');
            break;
        case 'Documents':
            toggleDocumentsPanel();
            break;
        case 'AI Assistants':
            toggleAssistantsPanel();
            break;
        case 'Security':
            toggleSecurityPanel();
            break;
        case 'Settings':
            toggleSettingsPanel();
            break;
    }
}

// Update existing nav item click handler
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', function() {
        // Update active state
        document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
        this.classList.add('active');
        
        // Handle navigation
        const label = this.querySelector('.nav-label')?.textContent;
        if (label) {
            handleNavigation(label);
        }
    });
});

// === EXPORT ===
window.EnterprisePanels = {
    ASSISTANTS,
    currentAssistant,
    switchAssistant,
    toggleAssistantsPanel,
    toggleSecurityPanel,
    toggleSettingsPanel
};

console.log('✅ Enterprise Panels Loaded (AI Assistants + Security + Settings)');
