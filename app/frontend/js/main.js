// HealthPlatform - SPA Controller CORRIGIDO
// Arquivo: /app/frontend/js/main.js
// Versão: FINAL FUNCIONAL

// ============================================
// CONFIGURAÇÕES GLOBAIS ATUALIZADAS
// ============================================
const APP_CONFIG = {
    baseURL: window.location.origin,
    paths: {
        dashboards: '/static/dashboards/',
        pages: '/static/pges/',
        auth: '/static/pges/auth/'
    }
};

// Estado da aplicação
let appState = {
    currentPage: 'dashboard.html',
    currentTitle: 'Dashboard Geral',
    isLoading: false
};

// ============================================
// FUNÇÃO PRINCIPAL LOADPAGE - VERSÃO FINAL CORRIGIDA
// ============================================

function loadPage(pagePath, pageTitle, element = null) {
    console.log(`📄 [SPA] Carregando: ${pagePath}`);

    // Prevenir múltiplos cliques
    if (appState.isLoading) {
        console.log('⏳ Já carregando, aguarde...');
        return;
    }

    // Se já está na mesma página, não faz nada
    if (appState.currentPage === pagePath) {
        console.log('✅ Já está nesta página');
        return;
    }

    const iframe = document.getElementById('main-frame');
    const loadingElement = document.getElementById('frame-loading');

    if (!iframe || !loadingElement) {
        console.error('❌ Elementos não encontrados!');
        return;
    }

    // Iniciar loading
    appState.isLoading = true;
    loadingElement.style.display = 'flex';

    // DETERMINAR CAMINHO CORRETO - LÓGICA SIMPLIFICADA
    let fullPath = '';

    // Lista de dashboards (arquivos diretos na pasta dashboards)
    const dashboardFiles = [
        'dashboard.html',
        'coordenador.html',
        'kpi_dashboard.html',
        'comissoes.html',
        'teste_ia.html',
        'clientes.html',
        'leads.html',
        'relatorios.html'
    ];

    // Verificar se é um dashboard
    if (dashboardFiles.includes(pagePath) ||
        pagePath.includes('dashboard') ||
        pagePath.endsWith('coordenador.html') ||
        pagePath.endsWith('comissoes.html') ||
        pagePath.endsWith('teste_ia.html')) {

        // Dashboards principais
        fullPath = `${APP_CONFIG.paths.dashboards}${pagePath}`;
    }
    // Verificar se é uma subpasta de dashboards (ex: leads/)
    else if (pagePath.startsWith('leads/')) {
        fullPath = `${APP_CONFIG.paths.dashboards}${pagePath}`;
    }
    // Todas as outras páginas estão em /static/pges/
    else {
        fullPath = `${APP_CONFIG.paths.pages}${pagePath}`;
    }

    console.log(`📍 Caminho final: ${fullPath}`);

    // Atualizar estado
    appState.currentPage = pagePath;
    appState.currentTitle = pageTitle;

    // Atualizar título
    updatePageTitle(pageTitle);

    // Marcar item ativo
    if (element) {
        setActiveMenuItem(element);
    }

    // Carregar no iframe
    iframe.src = fullPath;

    // Configurar eventos do iframe UMA VEZ
    iframe.onload = function () {
        console.log('✅ Iframe carregado com sucesso');

        setTimeout(() => {
            loadingElement.style.display = 'none';
            appState.isLoading = false;

            // Ajustar altura
            adjustIframeHeight(iframe);

            // Atualizar histórico
            updateBrowserHistory(pagePath, pageTitle);
        }, 300);
    };

    iframe.onerror = function () {
        console.error('❌ Erro ao carregar iframe:', fullPath);

        loadingElement.style.display = 'none';
        appState.isLoading = false;

        // Fallback para dashboard
        if (pagePath !== 'dashboard.html') {
            console.log('🔄 Voltando para dashboard...');
            appState.currentPage = 'dashboard.html';
            appState.currentTitle = 'Dashboard Geral';
            iframe.src = `${APP_CONFIG.paths.dashboards}dashboard.html`;
        }
    };
}

// ============================================
// FUNÇÕES AUXILIARES (mantenha estas)
// ============================================

function updatePageTitle(title) {
    const titleElement = document.getElementById('page-title');
    if (titleElement) {
        titleElement.textContent = title;
    }
}

function setActiveMenuItem(element) {
    // Remover classe ativa de todos
    document.querySelectorAll('.menu-item').forEach(item => {
        item.classList.remove('bg-primary', 'text-white');
        item.classList.add('text-primary');
    });

    // Adicionar ao elemento clicado
    if (element) {
        element.classList.add('bg-primary', 'text-white');
        element.classList.remove('text-primary');
    }
}

function adjustIframeHeight(iframe) {
    try {
        const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
        const bodyHeight = iframeDoc.body.scrollHeight;
        const htmlHeight = iframeDoc.documentElement.scrollHeight;
        const newHeight = Math.max(bodyHeight, htmlHeight, 600);

        iframe.style.height = newHeight + 'px';
    } catch (e) {
        // Erros de cross-origin são normais
        iframe.style.height = '100%';
    }
}

function updateBrowserHistory(pagePath, pageTitle) {
    try {
        history.pushState({
            page: pagePath,
            title: pageTitle
        }, pageTitle, `/?page=${encodeURIComponent(pagePath)}`);
    } catch (e) {
        console.log('⚠️ Histórico não atualizado:', e.message);
    }
}

function toggleSubmenu(id) {
    const submenu = document.getElementById(id);
    const icon = document.getElementById(`icon-${id}`);

    if (!submenu || !icon) return;

    if (submenu.classList.contains('hidden')) {
        submenu.classList.remove('hidden');
        icon.classList.add('rotate-180');
    } else {
        submenu.classList.add('hidden');
        icon.classList.remove('rotate-180');
    }
}

function toggleSidebar() {
    const expanded = document.getElementById('expanded-sidebar');
    const recolher = document.getElementById('recolher-sidebar');

    if (!expanded || !recolher) return;

    expanded.classList.toggle('hidden');
    recolher.classList.toggle('hidden');

    // Salvar preferência
    localStorage.setItem('sidebarExpanded', expanded.classList.contains('hidden') ? 'false' : 'true');
}

function logout() {
    if (confirm('Tem certeza que deseja sair?')) {
        localStorage.clear();
        window.location.href = '/';
    }
}

// ============================================
// CONFIGURAÇÃO DE BUSCA (simplificada)
// ============================================

function setupGlobalSearch() {
    const searchInput = document.getElementById('global-search');
    const searchBtn = document.getElementById('search-btn');

    if (searchInput) {
        searchInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter' && this.value.trim()) {
                console.log('🔍 Buscando:', this.value);
                alert(`Busca por: ${this.value}\n\n(Implementar integração com backend)`);
            }
        });
    }

    if (searchBtn) {
        searchBtn.addEventListener('click', function () {
            const searchInput = document.getElementById('global-search');
            if (searchInput && searchInput.value.trim()) {
                console.log('🔍 Buscando:', searchInput.value);
                alert(`Busca por: ${searchInput.value}`);
            }
        });
    }
}

// ============================================
// INICIALIZAÇÃO SIMPLIFICADA
// ============================================

function initializeApp() {
    console.log('🚀 HealthCRM SPA - Inicializando...');

    // Restaurar sidebar
    const savedSidebar = localStorage.getItem('sidebarExpanded');
    if (savedSidebar === 'false') {
        toggleSidebar();
    }

    // Configurar busca
    setupGlobalSearch();

    // Carregar página da URL ou dashboard padrão
    const urlParams = new URLSearchParams(window.location.search);
    const pageParam = urlParams.get('page');

    if (pageParam) {
        const decodedPage = decodeURIComponent(pageParam);
        console.log('📖 Carregando da URL:', decodedPage);

        // Pequeno delay para garantir que tudo está carregado
        setTimeout(() => {
            loadPage(decodedPage, 'Página Carregada');
        }, 500);
    } else {
        // Carregar dashboard inicial
        setTimeout(() => {
            loadPage('dashboard.html', 'Dashboard Geral');
        }, 300);
    }

    console.log('✅ Sistema pronto!');
}

// ============================================
// EXPORTAR FUNÇÕES PARA HTML
// ============================================
window.loadPage = loadPage;
window.toggleSubmenu = toggleSubmenu;
window.toggleSidebar = toggleSidebar;
window.logout = logout;
window.initializeApp = initializeApp;

// Inicializar automaticamente
document.addEventListener('DOMContentLoaded', initializeApp);