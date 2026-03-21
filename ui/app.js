// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// State
let selectedAgent = 'executor';
let isProcessing = false;

// Initialize
async function init() {
    // Don't load old tasks - start fresh each time
    chatHistory = [];
    chatStarted = false;
    
    // Ensure we start at welcome screen
    document.getElementById('welcomeScreen').classList.remove('hidden');
    document.getElementById('chatSection').classList.add('hidden');
    
    setupEventListeners();
}

// Store chat history
let chatHistory = [];
let chatStarted = false;

// API Calls
async function fetchAPI(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
            },
            ...options,
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'API request failed');
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showError(error.message);
        throw error;
    }
}

async function loadStats() {
    try {
        const stats = await fetchAPI('/api/stats');
        updateStatsUI(stats);
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

async function loadTasks() {
    try {
        const tasks = await fetchAPI('/api/tasks');
        // Convert tasks to chat messages
        chatHistory = tasks.slice(0, 10).reverse().flatMap(task => [
            { type: 'user', content: task.task },
            { type: 'assistant', content: task.result, agent: task.agent }
        ]);
        renderChat();
    } catch (error) {
        console.error('Failed to load tasks:', error);
    }
}

async function executeTask(task, agent) {
    const response = await fetchAPI('/api/execute', {
        method: 'POST',
        body: JSON.stringify({ task, agent }),
    });
    return response;
}

// UI Updates
function updateStatsUI(stats) {
    document.getElementById('activeAgents').textContent = stats.active_agents;
    document.getElementById('totalTasks').textContent = stats.total_tasks;
    document.getElementById('successRate').textContent = `${stats.success_rate}%`;
    document.getElementById('serverStatus').textContent = stats.server_status;
}

// Render chat messages
function renderChat() {
    const chatMessages = document.getElementById('chatMessages');
    
    chatMessages.innerHTML = chatHistory.map(msg => {
        if (msg.type === 'user') {
            return `
                <div class="chat-message user">
                    <div class="message-avatar user-icon"></div>
                    <div class="message-content">${escapeHtml(msg.content)}</div>
                </div>
            `;
        } else {
            return `
                <div class="chat-message assistant">
                    <div class="message-avatar bot-icon"></div>
                    <div class="message-content">${escapeHtml(msg.content)}</div>
                </div>
            `;
        }
    }).join('');
    // Manual scroll only - no auto-scroll
}

// Show chat interface (hide welcome, show chat)
function showChatInterface() {
    if (chatStarted) return;
    chatStarted = true;
    
    document.getElementById('welcomeScreen').classList.add('hidden');
    document.getElementById('chatSection').classList.remove('hidden');
    renderChat();
}

// Start new chat - reset and go back to welcome screen
function startNewChat() {
    // Clear chat history
    chatHistory = [];
    chatStarted = false;
    
    // Clear inputs
    document.getElementById('taskInput').value = '';
    document.getElementById('chatInput').value = '';
    
    // Hide chat section, show welcome screen
    document.getElementById('chatSection').classList.add('hidden');
    document.getElementById('welcomeScreen').classList.remove('hidden');
    
    console.log('New chat started');
}

function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}

function clearError() {
    document.getElementById('errorMessage').style.display = 'none';
}

function setLoading(loading, isWelcome = true) {
    isProcessing = loading;
    const btn = isWelcome ? document.getElementById('executeBtn') : document.getElementById('chatSendBtn');
    const input = isWelcome ? document.getElementById('taskInput') : document.getElementById('chatInput');

    if (loading) {
        btn.disabled = true;
        input.disabled = true;
    } else {
        btn.disabled = false;
        input.disabled = false;
        input.focus();
    }
}

// Agent Selection
function selectAgent(agentKey) {
    selectedAgent = agentKey;

    // Update UI
    document.querySelectorAll('.agent-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`.agent-btn[data-agent="${agentKey}"]`)?.classList.add('active');

    console.log('Selected agent:', agentKey);
}

// Task Execution from welcome screen
async function handleExecuteTask() {
    if (isProcessing) return;

    const input = document.getElementById('taskInput');
    const taskDescription = input.value.trim();

    if (!taskDescription) {
        showError('Please enter a message');
        return;
    }

    clearError();
    
    // Switch to chat interface
    showChatInterface();
    
    // Add user message to chat
    chatHistory.push({ type: 'user', content: taskDescription });
    renderChat();
    
    setLoading(true, true);

    try {
        const result = await executeTask(taskDescription, selectedAgent);
        
        // Add assistant response to chat
        chatHistory.push({ type: 'assistant', content: result.result, agent: result.agent });
        renderChat();

        // Clear welcome input
        input.value = '';
        // Also clear chat input
        document.getElementById('chatInput').value = '';

        console.log('Task executed:', result);
    } catch (error) {
        showError(`Failed to execute task: ${error.message}`);
        // Remove user message on error
        chatHistory.pop();
        renderChat();
    } finally {
        setLoading(false, true);
    }
}

// Task Execution from chat interface
async function handleChatSend() {
    if (isProcessing) return;

    const input = document.getElementById('chatInput');
    const taskDescription = input.value.trim();

    if (!taskDescription) {
        return;
    }
    
    // Add user message to chat
    chatHistory.push({ type: 'user', content: taskDescription });
    renderChat();
    
    setLoading(true, false);

    try {
        const result = await executeTask(taskDescription, selectedAgent);
        
        // Add assistant response to chat
        chatHistory.push({ type: 'assistant', content: result.result, agent: result.agent });
        renderChat();

        // Clear input
        input.value = '';

        console.log('Task executed:', result);
    } catch (error) {
        showError(`Failed to execute task: ${error.message}`);
        // Remove user message on error
        chatHistory.pop();
        renderChat();
    } finally {
        setLoading(false, false);
    }
}

// Event Listeners
function setupEventListeners() {
    // Welcome screen execute button
    document.getElementById('executeBtn').addEventListener('click', handleExecuteTask);

    // Welcome screen enter key support
    document.getElementById('taskInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleExecuteTask();
        }
    });

    // Chat send button
    document.getElementById('chatSendBtn').addEventListener('click', handleChatSend);

    // Chat input enter key support
    document.getElementById('chatInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleChatSend();
        }
    });

    // Agent selection
    document.querySelectorAll('.agent-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const agent = this.dataset.agent;
            selectAgent(agent);
        });
    });
}

// Utility functions
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(timestamp) {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleString();
}

// Auth handlers (placeholder)
function handleAuth(provider) {
    alert(`Authentication with ${provider === 'google' ? 'Google' : 'Apple'} coming soon!`);
    console.log(`Auth initiated: ${provider}`);
}

// Feature handlers (placeholder)
function showComingSoon(feature) {
    alert(`${feature} feature coming soon!`);
    console.log(`Feature clicked: ${feature}`);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', init);
