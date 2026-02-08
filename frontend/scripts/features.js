/**
 * Enterprise Features JavaScript
 * Workspaces, Documents, AI Assistants
 */

// === WORKSPACE MANAGEMENT ===
const workspaceState = {
    current: 'default',
    workspaces: [
        {
            id: 'default',
            name: 'Default Workspace',
            icon: '📁',
            description: 'General workspace',
            created: new Date().toISOString()
        }
    ]
};

// Toggle workspace dropdown
document.getElementById('workspaceBtn')?.addEventListener('click', () => {
    const dropdown = document.getElementById('workspaceDropdown');
    dropdown?.classList.toggle('show');
});

// Close dropdown when clicking outside
document.addEventListener('click', (e) => {
    const selector = document.querySelector('.workspace-selector');
    if (selector && !selector.contains(e.target)) {
        document.getElementById('workspaceDropdown')?.classList.remove('show');
    }
});

// Switch workspace
document.querySelectorAll('.workspace-item').forEach(item => {
    item.addEventListener('click', async function() {
        const workspaceId = this.dataset.workspace;
        await switchWorkspace(workspaceId);
    });
});

async function switchWorkspace(workspaceId) {
    workspaceState.current = workspaceId;
    
    // Update UI
    document.querySelectorAll('.workspace-item').forEach(item => {
        item.classList.toggle('active', item.dataset.workspace === workspaceId);
    });
    
    const workspace = workspaceState.workspaces.find(w => w.id === workspaceId);
    if (workspace) {
        document.querySelector('.workspace-name').textContent = workspace.name;
    }
    
    // Clear chat and reload for this workspace
    elements.chatContainer.innerHTML = '<div class="welcome-card">...</div>';
    
    // Close dropdown
    document.getElementById('workspaceDropdown')?.classList.remove('show');
    
    console.log(`Switched to workspace: ${workspaceId}`);
}

// Create new workspace
document.getElementById('createWorkspaceBtn')?.addEventListener('click', () => {
    const name = prompt('Workspace name:');
    if (name) {
        createWorkspace(name);
    }
});

function createWorkspace(name, description = '') {
    const newWorkspace = {
        id: `ws_${Date.now()}`,
        name: name,
        icon: '📁',
        description: description,
        created: new Date().toISOString()
    };
    
    workspaceState.workspaces.push(newWorkspace);
    
    // Add to dropdown
    const list = document.querySelector('.workspace-list');
    const item = document.createElement('div');
    item.className = 'workspace-item';
    item.dataset.workspace = newWorkspace.id;
    item.innerHTML = `
        <span class="workspace-icon">${newWorkspace.icon}</span>
        <span>${newWorkspace.name}</span>
    `;
    
    item.addEventListener('click', () => switchWorkspace(newWorkspace.id));
    list.appendChild(item);
    
    // Switch to new workspace
    switchWorkspace(newWorkspace.id);
}

// === DOCUMENTS MANAGEMENT ===
let documentsVisible = false;

// Toggle documents panel
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', function() {
        const label = this.querySelector('.nav-label')?.textContent;
        
        if (label === 'Documents') {
            toggleDocumentsPanel();
        } else {
            // Hide documents panel for other nav items
            const panel = document.getElementById('documentsPanel');
            if (panel) panel.classList.remove('show');
            documentsVisible = false;
        }
    });
});

function toggleDocumentsPanel() {
    documentsVisible = !documentsVisible;
    let panel = document.getElementById('documentsPanel');
    
    if (!panel) {
        // Create documents panel if it doesn't exist
        panel = createDocumentsPanel();
        document.querySelector('.app-container').appendChild(panel);
    }
    
    panel.classList.toggle('show', documentsVisible);
}

function createDocumentsPanel() {
    const panel = document.createElement('div');
    panel.id = 'documentsPanel';
    panel.className = 'documents-panel';
    panel.innerHTML = `
        <div class="documents-header">
            <h2>Documents</h2>
            <button class="upload-btn-large" id="uploadBtnLarge">
                📤 Upload Documents
            </button>
        </div>
        
        <div class="upload-zone" id="uploadZone">
            <div class="upload-icon">📁</div>
            <p class="upload-text">Drop files here or click to browse</p>
            <p class="upload-note">Supports: PDF, DOCX, TXT, CSV (Max 10MB)</p>
            <input type="file" id="fileInput" multiple accept=".pdf,.docx,.txt,.csv" hidden>
        </div>
        
        <div class="document-list" id="documentList">
            <div class="document-item">
                <span class="doc-icon">📄</span>
                <div class="doc-info">
                    <div class="doc-name">Sample Document.pdf</div>
                    <div class="doc-meta">1.2 MB • Uploaded today</div>
                </div>
                <button class="doc-action-btn">⋮</button>
            </div>
        </div>
    `;
    
    // Setup upload handlers
    setTimeout(() => {
        const uploadZone = panel.querySelector('#uploadZone');
        const fileInput = panel.querySelector('#fileInput');
        
        uploadZone?.addEventListener('click', () => fileInput?.click());
        
        fileInput?.addEventListener('change', handleFileUpload);
        
        // Drag and drop
        uploadZone?.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.style.borderColor = 'var(--color-accent)';
        });
        
        uploadZone?.addEventListener('dragleave', () => {
            uploadZone.style.borderColor = 'var(--border-color)';
        });
        
        uploadZone?.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.style.borderColor = 'var(--border-color)';
            if (e.dataTransfer.files.length) {
                handleFileUpload({target: {files: e.dataTransfer.files}});
            }
        });
    }, 100);
    
    return panel;
}

async function handleFileUpload(event) {
    const files = event.target.files;
    const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
    const ALLOWED_TYPES = ['.pdf', '.docx', '.txt', '.csv', '.md'];
    
    // Validate files before uploading
    for (let file of files) {
        // File size validation
        if (file.size > MAX_FILE_SIZE) {
            showNotification(`File ${file.name} exceeds 10MB limit`, 'error');
            continue;
        }
        
        // File type validation
        const ext = '.' + file.name.split('.').pop().toLowerCase();
        if (!ALLOWED_TYPES.includes(ext)) {
            showNotification(`File type ${ext} not supported`, 'error');
            continue;
        }
        
        // Upload file with progress
        await uploadFileToBackend(file);
    }
}

async function uploadFileToBackend(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    // Create progress indicator
    const progressId = `upload-${Date.now()}`;
    showUploadProgress(file.name, progressId);
    
    try {
        // Get auth token
        const token = localStorage.getItem('token');
        if (!token) {
            throw new Error('Not authenticated');
        }
        
        const response = await fetch('/api/documents/upload', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Upload failed');
        }
        
        const result = await response.json();
        
        // Update progress to complete
        updateUploadProgress(progressId, 100, 'success');
        
        // Add to document list
        addDocumentToList(file.name, file.size);
        
        // Show success notification
        showNotification(`✓ ${file.name} uploaded successfully`, 'success');
        
        console.log('Upload successful:', result);
        
    } catch (error) {
        console.error('Upload error:', error);
        updateUploadProgress(progressId, 0, 'error');
        showNotification(`✗ Upload failed: ${error.message}`, 'error');
    }
}

function showUploadProgress(filename, progressId) {
    const uploadZone = document.getElementById('uploadZone');
    if (!uploadZone) return;
    
    const progressDiv = document.createElement('div');
    progressDiv.id = progressId;
    progressDiv.className = 'upload-progress';
    progressDiv.innerHTML = `
        <div class="progress-file">${filename}</div>
        <div class="progress-bar">
            <div class="progress-fill" style="width: 0%"></div>
        </div>
        <div class="progress-status">Uploading...</div>
    `;
    
    uploadZone.after(progressDiv);
    
    // Simulate progress (in real app, use XHR for real progress)
    let progress = 0;
    const interval = setInterval(() => {
        progress += 10;
        const fill = progressDiv.querySelector('.progress-fill');
        if (fill) fill.style.width = `${Math.min(progress, 90)}%`;
        if (progress >= 90) clearInterval(interval);
    }, 200);
}

function updateUploadProgress(progressId, percent, status) {
    const progressDiv = document.getElementById(progressId);
    if (!progressDiv) return;
    
    const fill = progressDiv.querySelector('.progress-fill');
    const statusText = progressDiv.querySelector('.progress-status');
    
    if (fill) fill.style.width = `${percent}%`;
    
    if (status === 'success') {
        if (fill) fill.style.backgroundColor = 'var(--color-success, #22c55e)';
        if (statusText) statusText.textContent = 'Complete ✓';
        setTimeout(() => progressDiv.remove(), 2000);
    } else if (status === 'error') {
        if (fill) fill.style.backgroundColor = 'var(--color-error, #ef4444)';
        if (statusText) statusText.textContent = 'Failed ✗';
        setTimeout(() => progressDiv.remove(), 3000);
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 24px;
        background: ${type === 'success' ? '#22c55e' : type === 'error' ? '#ef4444' : '#3b82f6'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
    `;
    
    document.body.appendChild(notification);
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}


function addDocumentToList(filename, size) {
    const list = document.getElementById('documentList');
    if (!list) return;
    
    const item = document.createElement('div');
    item.className = 'document-item';
    
    const sizeKB = (size / 1024).toFixed(1);
    const icon = filename.endsWith('.pdf') ? '📄' : 
                 filename.endsWith('.docx') ? '📝' : 
                 filename.endsWith('.txt') ? '📃' : '📊';
    
    item.innerHTML = `
        <span class="doc-icon">${icon}</span>
        <div class="doc-info">
            <div class="doc-name">${filename}</div>
            <div class="doc-meta">${sizeKB} KB • Just now</div>
        </div>
        <button class="doc-action-btn">⋮</button>
    `;
    
    list.prepend(item);
}

// === EXPORT ===
window.EnterpriseFeatures = {
    workspaceState,
    switchWorkspace,
    createWorkspace,
    toggleDocumentsPanel
};

console.log('✅ Enterprise Features Loaded');
