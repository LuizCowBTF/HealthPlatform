// HealthPlatform - SPA Controller
// Arquivo: /app/frontend/js/main.js
// Responsável por gerenciar toda a navegação SPA

// ============================================
// CONFIGURAÇÕES GLOBAIS
// ============================================
const APP_CONFIG = {
    baseURL: window.location.origin,
    endpoints: {
        dashboard: '/api/v1/crm/dashboard/completo',
        dashboardAvancado: '/api/v1/crm/dashboard/avancado',
        leads: '/api/v1/crm/leads',
        comissoes: '/api/v1/finance/comissoes'
    },
    paths: {
        dashboards: '/dashboards/',
        pages: '/pages/',
        auth: '/pages/auth/',
        css: '/css/',
        js: '/js/',
        img: '/img/'
    }
};

// Estado da aplicação
let appState = {
    currentPage: 'dashboard.html',
    currentTitle: 'Dashboard Geral',
    lastError: null,
    user: null,
    sidebarExpanded: true
};

// ============================================
// FUNÇÕES DE NAVEGAÇÃO PRINCIPAIS
// ============================================

/**
 * Carrega uma página no iframe principal
 * @param {string} pagePath - Caminho da página
 * @param {string} pageTitle - Título da página
 * @param {HTMLElement} element - Elemento clicado (para highlight)
 */
function loadPage(pagePath, pageTitle, element = null) {
    console.log(`📄 [loadPage] Carregando: ${pagePath}`);

    const iframe = document.getElementById('main-frame');
    const loadingElement = document.getElementById('frame-loading');

    if (!iframe || !loadingElement) {
        console.error('❌ Elementos não encontrados!');
        showError('Erro: Elementos da página não encontrados');
        return;
    }

    // DEFINIR CAMINHO CORRETO BASEADO NO TIPO DE PÁGINA
    let fullPath = getPageFullPath(pagePath);
    console.log(`📍 Caminho final: ${fullPath}`);

    // Atualizar estado
    appState.currentPage = pagePath;
    appState.currentTitle = pageTitle;
    appState.lastError = null;

    // Mostrar loading
    showLoading(true);

    // Atualizar título na UI
    updatePageTitle(pageTitle);

    // Atualizar URL no histórico (sem recarregar)
    updateBrowserHistory(pagePath, pageTitle);

    // Marcar item ativo no menu
    setActiveMenuItem(element);

    // Carregar página no iframe
    iframe.src = fullPath;

    // Configurar eventos do iframe
    setupIframeEvents(iframe, loadingElement);
}

/**
 * Retorna o caminho completo baseado no tipo de página
 * @param {string} pagePath - Caminho relativo
 * @returns {string} Caminho completo
 */
function getPageFullPath(pagePath) {
    // Dashboard principal e derivados
    if (pagePath.includes('dashboard') ||
        pagePath.includes('comissoes') ||
        pagePath.includes('coordenador') ||
        pagePath.includes('kpi') ||
        pagePath.includes('leads') ||
        pagePath.includes('relatorios') ||
        pagePath.includes('clientes') ||
        pagePath.includes('teste_ia')) {
        return `${APP_CONFIG.paths.dashboards}${pagePath}`;
    }

    // Páginas de autenticação
    else if (pagePath.includes('login') ||
        pagePath.includes('register') ||
        pagePath.includes('forgot_password')) {
        return `${APP_CONFIG.paths.auth}${pagePath}`;
    }

    // Outras páginas (remover prefixos se existirem)
    else {
        let cleanPath = pagePath;

        // Remover prefixos comuns
        const prefixes = ['pages/', 'pges/', '../', './'];
        prefixes.forEach(prefix => {
            if (cleanPath.startsWith(prefix)) {
                cleanPath = cleanPath.substring(prefix.length);
            }
        });

        // Garantir que tenha .html
        if (!cleanPath.endsWith('.html')) {
            cleanPath += '.html';
        }

        return `${APP_CONFIG.paths.pages}${cleanPath}`;
    }
}

/**
 * Configura os eventos do iframe
 */
function setupIframeEvents(iframe, loadingElement) {
    // Evento de sucesso no carregamento
    iframe.onload = function () {
        console.log('✅ Iframe carregado com sucesso');

        setTimeout(() => {
            showLoading(false);
            adjustIframeHeight(iframe);

            // Notificar o conteúdo carregado que está em um iframe
            try {
                const iframeWindow = iframe.contentWindow;
                iframeWindow.postMessage({
                    type: 'parent-loaded',
                    page: appState.currentPage
                }, '*');
            } catch (e) {
                // Ignorar erros de cross-origin
            }
        }, 500);
    };

    // Evento de erro
    iframe.onerror = function () {
        console.error(`❌ Erro ao carregar iframe`);
        showLoading(false);
        showError(`Não foi possível carregar: ${appState.currentPage}`);

        // Fallback para dashboard
        setTimeout(() => {
            loadPage('dashboard.html', 'Dashboard Geral');
        }, 2000);
    };
}

/**
 * Ajusta a altura do iframe baseado no conteúdo
 */
function adjustIframeHeight(iframe) {
    try {
        const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;

        // Esperar um pouco para o conteúdo renderizar
        setTimeout(() => {
            const bodyHeight = iframeDoc.body.scrollHeight;
            const htmlHeight = iframeDoc.documentElement.scrollHeight;
            const contentHeight = Math.max(bodyHeight, htmlHeight, 600); // Mínimo 600px

            iframe.style.height = `${contentHeight}px`;
            console.log(`📏 Altura ajustada para: ${contentHeight}px`);
        }, 100);
    } catch (e) {
        // Erros de cross-origin são normais
        console.log('⚠️ Não foi possível ajustar altura (cross-origin)');
        iframe.style.height = '100%';
    }
}

// ============================================
// FUNÇÕES DE UI/UX
// ============================================

/**
 * Mostra/esconde o loading
 */
function showLoading(show) {
    const loadingElement = document.getElementById('frame-loading');
    if (loadingElement) {
        loadingElement.style.display = show ? 'flex' : 'none';
    }
}

/**
 * Mostra mensagem de erro
 */
function showError(message) {
    appState.lastError = message;
    console.error(`❌ Erro: ${message}`);

    // Pode implementar um toast/snackbar aqui
    alert(`Erro: ${message}`);
}

/**
 * Atualiza o título da página
 */
function updatePageTitle(title) {
    const titleElement = document.getElementById('page-title');
    if (titleElement) {
        titleElement.textContent = title;
    }

    // Atualizar título da aba do navegador
    document.title = `${title} - Health CRM`;
}

/**
 * Marca item ativo no menu
 */
function setActiveMenuItem(element) {
    // Remover classe ativa de todos
    document.querySelectorAll('.menu-item, .submenu-item').forEach(item => {
        item.classList.remove('active');
        item.classList.remove('bg-primary');
        item.classList.remove('text-white');
        item.classList.add('text-primary');
    });

    // Adicionar ao elemento clicado
    if (element) {
        element.classList.add('active');
        element.classList.add('bg-primary');
        element.classList.add('text-white');
        element.classList.remove('text-primary');

        // Também marcar o menu pai
        const parentMenu = element.closest('.menu-parent');
        if (parentMenu) {
            parentMenu.classList.add('active');
        }
    }
}

// ============================================
// FUNÇÕES DO SIDEBAR
// ============================================

/**
 * Alterna submenu
 */
function toggleSubmenu(id) {
    const submenu = document.getElementById(id);
    const icon = document.getElementById(`icon-${id}`);

    if (!submenu || !icon) {
        console.error(`Submenu ${id} não encontrado`);
        return;
    }

    if (submenu.classList.contains('hidden')) {
        submenu.classList.remove('hidden');
        icon.classList.add('rotate-180');
    } else {
        submenu.classList.add('hidden');
        icon.classList.remove('rotate-180');
    }
}

/**
 * Alterna sidebar expandida/recolhida
 */
function toggleSidebar() {
    const expanded = document.getElementById('expanded-sidebar');
    const collapsed = document.getElementById('recolher-sidebar');

    if (!expanded || !collapsed) return;

    expanded.classList.toggle('hidden');
    collapsed.classList.toggle('hidden');

    appState.sidebarExpanded = !appState.sidebarExpanded;

    // Salvar preferência
    localStorage.setItem('sidebarExpanded', appState.sidebarExpanded);
}

// ============================================
// FUNÇÕES DE HISTÓRICO E URL
// ============================================

/**
 * Atualiza o histórico do navegador
 */
function updateBrowserHistory(pagePath, pageTitle) {
    const url = new URL(window.location);
    url.searchParams.set('page', encodeURIComponent(pagePath));
    url.searchParams.set('title', encodeURIComponent(pageTitle));

    history.pushState({
        page: pagePath,
        title: pageTitle,
        timestamp: Date.now()
    }, pageTitle, url.toString());
}

/**
 * Carrega página da URL atual
 */
function loadPageFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    const page = urlParams.get('page');
    const title = urlParams.get('title');

    if (page && title) {
        const decodedPage = decodeURIComponent(page);
        const decodedTitle = decodeURIComponent(title);
        loadPage(decodedPage, decodedTitle);
    } else {
        // Carregar última página ou dashboard padrão
        const lastPage = localStorage.getItem('lastPage') || 'dashboard.html';
        const lastTitle = localStorage.getItem('lastTitle') || 'Dashboard Geral';
        loadPage(lastPage, lastTitle);
    }
}

// ============================================
// FUNÇÕES DE BUSCA E NOTIFICAÇÕES
// ============================================

/**
 * Configura a busca global
 */
function setupGlobalSearch() {
    const searchInput = document.getElementById('global-search');
    if (!searchInput) return;

    searchInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter' && this.value.trim()) {
            performSearch(this.value.trim());
        }
    });

    // Botão de busca (se existir)
    const searchBtn = document.getElementById('search-btn');
    if (searchBtn) {
        searchBtn.addEventListener('click', () => {
            if (searchInput.value.trim()) {
                performSearch(searchInput.value.trim());
            }
        });
    }
}

/**
 * Executa busca
 */
function performSearch(query) {
    console.log(`🔍 Buscando: ${query}`);
    // Implementar lógica de busca aqui
    alert(`Busca por: ${query}\n\n(Implementar integração com backend)`);
}

// ============================================
// FUNÇÕES DE AUTENTICAÇÃO
// ============================================

/**
 * Realiza logout
 */
function logout() {
    if (confirm('Tem certeza que deseja sair?')) {
        // Limpar estado
        appState.user = null;
        localStorage.removeItem('userToken');
        localStorage.removeItem('lastPage');
        localStorage.removeItem('lastTitle');

        // Redirecionar para login
        loadPage('auth/login.html', 'Login');
    }
}

/**
 * Verifica autenticação
 */
async function checkAuth() {
    const token = localStorage.getItem('userToken');

    if (!token && !window.location.pathname.includes('login')) {
        // Redirecionar para login se não estiver autenticado
        loadPage('auth/login.html', 'Login');
        return false;
    }

    // Validar token com API (implementar depois)
    return true;
}

// ============================================
// COMUNICAÇÃO ENTRE IFRAMES
// ============================================

/**
 * Configura listener para mensagens
 */
function setupMessageListener() {
    window.addEventListener('message', function (event) {
        console.log('📩 Mensagem recebida:', event.data);

        // Mensagens do iframe para o parent
        if (event.data && event.data.type) {
            switch (event.data.type) {
                case 'dashboard-loaded':
                    console.log('✅ Dashboard carregado no iframe');
                    break;

                case 'navigate-to':
                    if (event.data.page && event.data.title) {
                        loadPage(event.data.page, event.data.title);
                    }
                    break;

                case 'show-error':
                    showError(event.data.message);
                    break;
            }
        }
    });
}

// ============================================
// INICIALIZAÇÃO DA APLICAÇÃO
// ============================================

/**
 * Inicializa a aplicação
 */
function initializeApp() {
    console.log('🚀 HealthCRM SPA - Inicializando...');

    // 1. Restaurar preferências
    const savedSidebar = localStorage.getItem('sidebarExpanded');
    if (savedSidebar === 'false') {
        toggleSidebar(); // Começar recolhido
    }

    // 2. Configurar listeners
    setupMessageListener();
    setupGlobalSearch();

    // 3. Configurar eventos de navegação
    window.addEventListener('popstate', function (event) {
        if (event.state && event.state.page) {
            loadPage(event.state.page, event.state.title);
        }
    });

    // 4. Fechar menu mobile ao clicar fora
    document.addEventListener('click', function (event) {
        const expandedSidebar = document.getElementById('expanded-sidebar');
        const mobileToggle = document.querySelector('[onclick*="toggleMobileMenu"]');

        if (expandedSidebar &&
            expandedSidebar.classList.contains('fixed') &&
            !expandedSidebar.contains(event.target) &&
            event.target !== mobileToggle &&
            !mobileToggle.contains(event.target)) {
            expandedSidebar.classList.add('hidden');
        }
    });

    // 5. Verificar autenticação
    checkAuth().then(isAuthenticated => {
        if (isAuthenticated) {
            // 6. Carregar página inicial
            loadPageFromURL();

            console.log('✅ HealthCRM SPA - Inicializado com sucesso!');
        }
    });

    // 7. Salvar última página ao sair
    window.addEventListener('beforeunload', function () {
        localStorage.setItem('lastPage', appState.currentPage);
        localStorage.setItem('lastTitle', appState.currentTitle);
    });
}

// ============================================
// EXPORTAR FUNÇÕES PARA HTML
// ============================================
// Torna as funções disponíveis globalmente
window.loadPage = loadPage;
window.toggleSubmenu = toggleSubmenu;
window.toggleSidebar = toggleSidebar;
window.logout = logout;

// Inicializar quando o DOM carregar
document.addEventListener('DOMContentLoaded', initializeApp);