// Estado da aplicação
let currentUser = null;
let reunioes = [];
let usuarios = [];

// Elementos do DOM
const loginScreen = document.getElementById('loginScreen');
const mainScreen = document.getElementById('mainScreen');
const loginForm = document.getElementById('loginForm');
const reuniaoForm = document.getElementById('reuniaoForm');
const userForm = document.getElementById('userForm');
const listaReunioes = document.getElementById('listaReunioes');
const listaUsuarios = document.getElementById('listaUsuarios');
const contadorReunioes = document.getElementById('contadorReunioes');
const userWelcome = document.getElementById('userWelcome');
const logoutBtn = document.getElementById('logoutBtn');
const navReunioes = document.getElementById('navReunioes');
const navUsuarios = document.getElementById('navUsuarios');
const reunioesSection = document.getElementById('reunioesSection');
const usuariosSection = document.getElementById('usuariosSection');
const loginError = document.getElementById('loginError');

// Funções de Tela
function showLoginScreen() {
    loginScreen.style.display = 'block';
    mainScreen.style.display = 'none';
}

function showMainScreen() {
    loginScreen.style.display = 'none';
    mainScreen.style.display = 'block';
}

// Handle login
async function handleLogin(e) {
    e.preventDefault();
    hideError();
    
    const formData = new FormData(loginForm);
    const loginData = Object.fromEntries(formData.entries());
    
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify(loginData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            currentUser = result.user;
            userWelcome.textContent = `Olá, ${currentUser.username}`;
            
            if (currentUser.is_admin) {
                navUsuarios.style.display = 'block';
            } else {
                navUsuarios.style.display = 'none';
            }
            
            showMainScreen();
            loadReunioes();
        } else {
            showError(result.error || 'Erro ao fazer login');
        }
    } catch (error) {
        console.error('Erro no login:', error);
        showError('Erro de conexão. Tente novamente.');
    }
}

// Handle logout
async function handleLogout() {
    try {
        await fetch('/api/logout', {
            method: 'POST',
            credentials: 'include'
        });
        
        currentUser = null;
        reunioes = [];
        usuarios = [];
        showLoginScreen();
    } catch (error) {
        console.error('Erro no logout:', error);
    }
}

// Carregar reuniões
async function loadReunioes() {
    try {
        const response = await fetch('/api/reunioes', {
            credentials: 'include'
        });
        
        if (response.ok) {
            reunioes = await response.json();
            renderReunioes();
        } else {
            console.error('Erro ao carregar reuniões');
        }
    } catch (error) {
        console.error('Erro ao carregar reuniões:', error);
    }
}

// Renderizar reuniões
function renderReunioes() {
    contadorReunioes.textContent = reunioes.length;
    
    if (reunioes.length === 0) {
        listaReunioes.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📅</div>
                <p>Nenhuma reunião agendada</p>
                <small>Use o formulário ao lado para criar sua primeira reunião</small>
            </div>
        `;
        return;
    }
    
    listaReunioes.innerHTML = reunioes.map(reuniao => `
        <div class="reuniao-item">
            <div class="reuniao-header">
                <h3 class="reuniao-titulo">${escapeHtml(reuniao.titulo)}</h3>
                <button class="btn-delete" onclick="deleteReuniao(${reuniao.id})" title="Remover reunião">
                    🗑️
                </button>
            </div>
            <div class="reuniao-detalhes">
                <div class="reuniao-info">
                    <span>📅</span>
                    <span>${formatarData(reuniao.data)}</span>
                </div>
                <div class="reuniao-info">
                    <span>🕐</span>
                    <span>${reuniao.hora_inicio} - ${reuniao.hora_termino}</span>
                </div>
                ${reuniao.local ? `
                    <div class="reuniao-info">
                        <span>📍</span>
                        <span>${escapeHtml(reuniao.local)}</span>
                    </div>
                ` : ''}
                ${reuniao.participantes ? `
                    <div class="reuniao-info">
                        <span>👥</span>
                        <span>${escapeHtml(reuniao.participantes)}</span>
                    </div>
                ` : ''}
                ${reuniao.descricao ? `
                    <div class="reuniao-descricao">
                        ${escapeHtml(reuniao.descricao)}
                    </div>
                ` : ''}
                <div class="reuniao-info" style="margin-top: 8px; font-size: 0.75rem; color: #9ca3af;">
                    <span>👤</span>
                    <span>Criado por: ${escapeHtml(reuniao.criador_nome)}</span>
                </div>
            </div>
        </div>
    `).join('');
}

// Handle criar reunião
async function handleCreateReuniao(e) {
    e.preventDefault();
    
    const formData = new FormData(reuniaoForm);
    const reuniaoData = {
        titulo: formData.get('titulo'),
        data: formData.get('data'),
        hora_inicio: formData.get('hora_inicio'),
        hora_termino: formData.get('hora_termino'),
        local: formData.get('local'),
        participantes: formData.get('participantes'),
        descricao: formData.get('descricao')
    };
    
    try {
        const response = await fetch('/api/reunioes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify(reuniaoData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            reuniaoForm.reset();
            setMinDate();
            loadReunioes();
            showFeedback('Reunião criada com sucesso!', 'success');
        } else {
            showFeedback(result.error || 'Erro ao criar reunião', 'error');
        }
    } catch (error) {
        console.error('Erro ao criar reunião:', error);
        showFeedback('Erro de conexão. Tente novamente.', 'error');
    }
}

// Deletar reunião
async function deleteReuniao(id) {
    if (!confirm('Tem certeza que deseja remover esta reunião?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/reunioes/${id}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        
        if (response.ok) {
            loadReunioes();
            showFeedback('Reunião removida com sucesso!', 'success');
        } else {
            const result = await response.json();
            showFeedback(result.error || 'Erro ao remover reunião', 'error');
        }
    } catch (error) {
        console.error('Erro ao deletar reunião:', error);
        showFeedback('Erro de conexão. Tente novamente.', 'error');
    }
}

// Carregar usuários (apenas admin)
async function loadUsuarios() {
    if (!currentUser || !currentUser.is_admin) return;
    
    try {
        const response = await fetch('/api/users', {
            credentials: 'include'
        });
        
        if (response.ok) {
            usuarios = await response.json();
            renderUsuarios();
        } else {
            console.error('Erro ao carregar usuários');
        }
    } catch (error) {
        console.error('Erro ao carregar usuários:', error);
    }
}

// Renderizar usuários
function renderUsuarios() {
    if (!currentUser || !currentUser.is_admin) return;
    
    if (usuarios.length === 0) {
        listaUsuarios.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">👥</div>
                <p>Nenhum usuário cadastrado</p>
            </div>
        `;
        return;
    }
    
    listaUsuarios.innerHTML = usuarios.map(usuario => `
        <div class="usuario-item">
            <div class="usuario-info">
                <div class="usuario-nome">${escapeHtml(usuario.username)}</div>
                <div class="usuario-email">${escapeHtml(usuario.email)}</div>
                <div class="usuario-badges">
                    <span class="badge ${usuario.is_admin ? 'badge-admin' : 'badge-user'}">
                        ${usuario.is_admin ? 'Administrador' : 'Usuário'}
                    </span>
                    ${!usuario.is_active ? '<span class="badge badge-inactive">Inativo</span>' : ''}
                </div>
                ${usuario.id !== currentUser.id ? `
                    <div class="usuario-actions">
                        <button class="btn-small btn-toggle" onclick="toggleUserStatus(${usuario.id})">
                            ${usuario.is_active ? 'Desativar' : 'Ativar'}
                        </button>
                        <button class="btn-small btn-danger" onclick="deleteUser(${usuario.id})">
                            Excluir
                        </button>
                    </div>
                ` : ''}
            </div>
        </div>
    `).join('');
}

// Handle criar usuário
async function handleCreateUser(e) {
    e.preventDefault();
    
    const formData = new FormData(userForm);
    const userData = {
        username: formData.get('username'),
        email: formData.get('email'),
        password: formData.get('password'),
        is_admin: formData.get('is_admin') === 'on'
    };
    
    try {
        const response = await fetch('/api/create-user', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify(userData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            userForm.reset();
            loadUsuarios();
            showFeedback('Usuário criado com sucesso!', 'success');
        } else {
            showFeedback(result.error || 'Erro ao criar usuário', 'error');
        }
    } catch (error) {
        console.error('Erro ao criar usuário:', error);
        showFeedback('Erro de conexão. Tente novamente.', 'error');
    }
}

// Toggle status do usuário
async function toggleUserStatus(userId) {
    try {
        const response = await fetch(`/api/users/${userId}/toggle-status`, {
            method: 'PUT',
            credentials: 'include'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            loadUsuarios();
            showFeedback(result.message, 'success');
        } else {
            showFeedback(result.error || 'Erro ao alterar status', 'error');
        }
    } catch (error) {
        console.error('Erro ao alterar status:', error);
        showFeedback('Erro de conexão. Tente novamente.', 'error');
    }
}

// Deletar usuário
async function deleteUser(userId) {
    if (!confirm('Tem certeza que deseja excluir este usuário?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/users/${userId}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        
        if (response.ok) {
            loadUsuarios();
            showFeedback('Usuário excluído com sucesso!', 'success');
        } else {
            const result = await response.json();
            showFeedback(result.error || 'Erro ao excluir usuário', 'error');
        }
    } catch (error) {
        console.error('Erro ao excluir usuário:', error);
        showFeedback('Erro de conexão. Tente novamente.', 'error');
    }
}

// Funções utilitárias
function formatarData(dataStr) {
    const data = new Date(dataStr + 'T00:00:00');
    return data.toLocaleDateString('pt-BR');
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function setMinDate() {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('data').min = today;
}

function showError(message) {
    loginError.textContent = message;
    loginError.style.display = 'block';
}

function hideError() {
    loginError.style.display = 'none';
}

function showFeedback(message, type = 'success') {
    const feedback = document.createElement('div');
    feedback.className = type === 'success' ? 'success-message' : 'error-message';
    feedback.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        z-index: 1000;
        font-weight: 500;
        animation: slideIn 0.3s ease-out;
        max-width: 300px;
    `;
    feedback.textContent = message;

    // Adicionar CSS da animação se não existir
    if (!document.getElementById('feedback-styles')) {
        const style = document.createElement('style');
        style.id = 'feedback-styles';
        style.textContent = `
            @keyframes slideIn {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
        `;
        document.head.appendChild(style);
    }

    document.body.appendChild(feedback);

    setTimeout(() => {
        feedback.style.animation = 'slideIn 0.3s ease-out reverse';
        setTimeout(() => {
            if (feedback.parentNode) {
                feedback.parentNode.removeChild(feedback);
            }
        }, 300);
    }, 3000);
}

// Event Listeners
document.addEventListener('DOMContentLoaded', async () => {
    loginForm.addEventListener('submit', handleLogin);
    logoutBtn.addEventListener('click', handleLogout);
    reuniaoForm.addEventListener('submit', handleCreateReuniao);
    userForm.addEventListener('submit', handleCreateUser);

    navReunioes.addEventListener('click', () => {
        reunioesSection.style.display = 'block';
        usuariosSection.style.display = 'none';
        navReunioes.classList.add('active');
        navUsuarios.classList.remove('active');
    });

    navUsuarios.addEventListener('click', () => {
        reunioesSection.style.display = 'none';
        usuariosSection.style.display = 'block';
        navReunioes.classList.remove('active');
        navUsuarios.classList.add('active');
        loadUsuarios();
    });

    setMinDate();

    // Verificar status do login
    try {
        const response = await fetch('/api/user-status', {
            credentials: 'include'
        });
        if (response.ok) {
            const data = await response.json();
            if (data.logged_in) {
                currentUser = data.user;
                userWelcome.textContent = `Olá, ${currentUser.username}`;
                if (currentUser.is_admin) {
                    navUsuarios.style.display = 'block';
                }
                showMainScreen();
                loadReunioes();
            } else {
                showLoginScreen();
            }
        } else {
            showLoginScreen();
        }
    } catch (error) {
        console.error('Erro ao verificar status do usuário:', error);
        showLoginScreen();
    }
});


