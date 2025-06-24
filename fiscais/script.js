// Configurações da API
const API_CONFIG = {
    baseUrl: 'https://api.pastelandia.site',
    endpoints: {
        question: '/question'
    },
    timeout: 120000
};

// Estado da aplicação
const appState = {
    isLoading: false,
    messageHistory: []
};

// Elementos DOM
const elements = {
    chatMessages: null,
    messageInput: null,
    sendButton: null,
    charCount: null,
    errorModal: null,
    errorMessage: null
};

// Inicialização da aplicação
document.addEventListener('DOMContentLoaded', function() {
    initializeElements();
    setupEventListeners();
    focusInput();
});

// Inicializar referências dos elementos DOM
function initializeElements() {
    elements.chatMessages = document.getElementById('chatMessages');
    elements.messageInput = document.getElementById('messageInput');
    elements.sendButton = document.getElementById('sendButton');
    elements.charCount = document.getElementById('charCount');
    elements.errorModal = document.getElementById('errorModal');
    elements.errorMessage = document.getElementById('errorMessage');
}

// Configurar event listeners
function setupEventListeners() {
    // Input de mensagem
    elements.messageInput.addEventListener('input', handleInputChange);
    elements.messageInput.addEventListener('keypress', handleKeyPress);
    
    // Botão de enviar
    elements.sendButton.addEventListener('click', sendMessage);
    
    // Fechar modal com ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeErrorModal();
        }
    });
}

// Manipular mudanças no input
function handleInputChange(e) {
    const value = e.target.value;
    const length = value.length;
    
    // Atualizar contador de caracteres
    elements.charCount.textContent = length;
    
    // Habilitar/desabilitar botão de enviar
    const canSend = length > 0 && length <= 500 && !appState.isLoading;
    elements.sendButton.disabled = !canSend;
}

// Manipular tecla pressionada
function handleKeyPress(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
}

// Enviar mensagem
async function sendMessage() {
    const message = elements.messageInput.value.trim();
    
    if (!message || appState.isLoading) {
        return;
    }
    
    // Adicionar mensagem do usuário
    addMessage('user', message);
    
    // Limpar input
    elements.messageInput.value = '';
    elements.charCount.textContent = '0';
    elements.sendButton.disabled = true;
    
    // Mostrar indicador de loading (três pontos)
    showTypingIndicator();
    
    try {
        // Fazer requisição para a API
        const response = await makeApiRequest(message);
        
        // Processar resposta
        const botResponse = parseApiResponse(response);
        
        // Remover indicador de loading
        hideTypingIndicator();
        
        // Adicionar resposta do bot
        addMessage('bot', botResponse);
        
    } catch (error) {
        console.error('Erro ao enviar mensagem:', error);
        hideTypingIndicator();
        handleApiError(error);
    } finally {
        setLoading(false);
        focusInput();
    }
}

// Fazer requisição para a API
async function makeApiRequest(question) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.timeout);
    
    try {
        const response = await fetch(`${API_CONFIG.baseUrl}${API_CONFIG.endpoints.question}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question }),
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status} - ${response.statusText}`);
        }
        
        const data = await response.json();
        return data;
        
    } catch (error) {
        clearTimeout(timeoutId);
        throw error;
    }
}

// Processar resposta da API
function parseApiResponse(response) {
    try {
        if (!response || !response.answer) {
            return 'Resposta inválida da API.';
        }
        
        const answerStr = response.answer;
        
        // Se a resposta já é uma string simples (não JSON), retornar diretamente
        if (typeof answerStr === 'string' && !answerStr.startsWith('{')) {
            return answerStr;
        }
        
        // Tentar fazer parse do JSON
        try {
            const answerData = JSON.parse(answerStr);
            
            // Retornar apenas o output, não o input
            if (answerData.output) {
                return answerData.output;
            }
            
            // Fallback para outros formatos possíveis
            if (answerData.answer) {
                return answerData.answer;
            }
            
            return 'Resposta não encontrada.';
            
        } catch (jsonError) {
            console.warn('Não foi possível fazer parse do JSON, tentando extrair output:', jsonError);
            
            // Se não conseguir fazer parse, tentar extrair apenas a parte do output usando regex
            const outputMatch = answerStr.match(/'output':\s*'([^']+)'/);
            if (outputMatch && outputMatch[1]) {
                return outputMatch[1];
            }
            
            // Tentar com aspas duplas
            const outputMatchDouble = answerStr.match(/"output":\s*"([^"]+)"/);
            if (outputMatchDouble && outputMatchDouble[1]) {
                return outputMatchDouble[1];
            }
            
            // Se não conseguir extrair, retornar a resposta original
            return answerStr;
        }
        
    } catch (error) {
        console.error('Erro ao processar resposta:', error);
        
        // Fallback final - retornar a resposta bruta se disponível
        if (response && response.answer) {
            return response.answer;
        }
        
        return 'Erro ao processar resposta.';
    }
}

// Adicionar mensagem ao chat
function addMessage(type, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const timestamp = new Date().toLocaleTimeString('pt-BR', {
        hour: '2-digit',
        minute: '2-digit'
    });
    
    const avatarIcon = type === 'bot' ? 'fas fa-robot' : 'fas fa-user';
    const avatarClass = type === 'bot' ? 'bot-avatar' : 'user-avatar';
    
    // Formatar o conteúdo para quebras de linha
    const formattedContent = formatMessageContent(content);
    
    messageDiv.innerHTML = `
        <div class="message-avatar ${avatarClass}">
            <i class="${avatarIcon}"></i>
        </div>
        <div class="message-content">
            <div class="message-text">${formattedContent}</div>
            <div class="message-time">${timestamp}</div>
        </div>
    `;
    
    elements.chatMessages.appendChild(messageDiv);
    
    // Scroll para a última mensagem
    messageDiv.scrollIntoView({ behavior: 'smooth', block: 'end' });
    
    // Adicionar ao histórico
    appState.messageHistory.push({
        type,
        content,
        timestamp: new Date().toISOString()
    });
}

// Formatar conteúdo da mensagem para quebras de linha
function formatMessageContent(content) {
    if (!content) return '';
    
    // Escapar HTML primeiro para prevenir XSS
    const escapedContent = escapeHtml(content);
    
    // Converter \n em <br> para quebras de linha
    const formattedContent = escapedContent.replace(/\\n/g, '<br>');
    
    return formattedContent;
}

// Mostrar indicador de três pontos
function showTypingIndicator() {
    appState.isLoading = true;
    
    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';
    typingDiv.id = 'typingIndicator';
    
    typingDiv.innerHTML = `
        <div class="message-avatar bot-avatar">
            <i class="fas fa-robot"></i>
        </div>
        <div class="typing-dots">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    `;
    
    elements.chatMessages.appendChild(typingDiv);
    
    // Scroll para o indicador
    typingDiv.scrollIntoView({ behavior: 'smooth', block: 'end' });
}

// Esconder indicador de três pontos
function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
    appState.isLoading = false;
}

// Enviar sugestão
function sendSuggestion(suggestion) {
    if (appState.isLoading) {
        return;
    }
    
    elements.messageInput.value = suggestion;
    handleInputChange({ target: elements.messageInput });
    sendMessage();
}

// Controlar estado de loading
function setLoading(loading) {
    appState.isLoading = loading;
    
    elements.messageInput.disabled = loading;
    elements.sendButton.disabled = loading || elements.messageInput.value.trim().length === 0;
}

// Manipular erros da API
function handleApiError(error) {
    let errorMessage = 'Ocorreu um erro inesperado ao processar sua pergunta.';
    
    if (error.name === 'AbortError') {
        errorMessage = 'A requisição demorou muito para responder. Tente novamente.';
    } else if (error.message.includes('Failed to fetch')) {
        errorMessage = 'Não foi possível conectar com a API. Verifique sua conexão com a internet.';
    } else if (error.message.includes('HTTP')) {
        errorMessage = `Erro do servidor: ${error.message}`;
    }
    
    showErrorModal(errorMessage);
}

// Mostrar modal de erro
function showErrorModal(message) {
    elements.errorMessage.textContent = message;
    elements.errorModal.classList.add('show');
}

// Fechar modal de erro
function closeErrorModal() {
    elements.errorModal.classList.remove('show');
}

// Focar no input
function focusInput() {
    if (!appState.isLoading) {
        elements.messageInput.focus();
    }
}

// Escapar HTML para prevenir XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Funções utilitárias para formatação
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

function formatDate(date) {
    return new Intl.DateTimeFormat('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    }).format(new Date(date));
}

// Exportar funções para uso global
window.sendSuggestion = sendSuggestion;
window.sendMessage = sendMessage;
window.closeErrorModal = closeErrorModal;

// Debug: Adicionar informações ao console
console.log('🤖 Agente de Notas Fiscais carregado com sucesso!');
console.log('📊 API Base URL:', API_CONFIG.baseUrl);
console.log('🔧 Versão: 1.0.0');