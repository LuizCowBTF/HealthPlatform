// ============================================
// SISTEMA DE NAVEGAÇÃO - VERSÃO OTIMIZADA
// ============================================

class NavigationSystem {
    constructor() {
        this.currentPage = '';
        this.isLoading = false;
        this.init();
    }

    init() {
        console.log('🚀 HealthCRM Navigation - Inicializado');
        this.setupEventListeners();
        this.loadInitialPage();
    }

    setupEventListeners() {
        // Busca global
        const searchInput = document.getElementById('global-search');
        if (searchInput) {
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && searchInput.value.trim()) {
                    this.handleSearch(searchInput.value);
                }
            });
        }

        // Histórico do navegador
        window.addEventListener('popstate', (event) => {
            if (event.state && event.state.page) {
                this.loadPage(event.state.page, event.state.title);
            }
        });
    }

    loadInitialPage() {
        const urlParams = new URLSearchParams(window.location.search);
        const pageParam = urlParams.get('page');

        if (pageParam) {
            this.loadPage(decodeURIComponent(pageParam), 'Sistema Atualizado');
        } else {
            setTimeout(() => {
                this.loadPage('dashboard.html', 'Dashboard Geral');
            }, 100);
        }
    }

    loadPage(pagePath, pageTitle, element = null) {
        console.log(`📄 Carregando: ${pagePath}`);

        if (this.isLoading) return;
        if (this.currentPage === pagePath) return;

        this.isLoading = true;
        this.currentPage = pagePath;

        const iframe = document.getElementById('main-frame');
        const loading = document.getElementById('frame-loading');

        if (!iframe || !loading) {
            console.error('❌ Elementos não encontrados');
            this.isLoading = false;
            return;
        }

        loading.style.display = 'flex';
        this.updatePageTitle(pageTitle);

        if (element) {
            this.setActiveMenuItem(element);
        }

        // Determinar caminho completo
        const fullPath = this.getPagePath(pagePath);
        console.log(`📍 Caminho: ${fullPath}`);

        // Configurar eventos do iframe
        iframe.onload = () => {
            console.log('✅ Página carregada com sucesso');

            // Aguardar renderização completa
            setTimeout(() => {
                loading.style.display = 'none';
                this.isLoading = false;

                // Injetar estilos para garantir scroll
                this.injectIframeStyles(iframe);

                // Atualizar histórico
                this.updateHistory(pagePath, pageTitle);

                // Ajustar altura
                if (window.heightManager) {
                    window.heightManager.calculateAndSetHeight();
                }
            }, 300);
        };

        iframe.onerror = () => {
            console.error(`❌ Erro ao carregar: ${fullPath}`);
            loading.style.display = 'none';
            this.isLoading = false;

            // Mostrar erro no iframe
            iframe.srcdoc = this.getErrorHTML(pageTitle, fullPath);
        };

        // Carregar a página
        iframe.src = fullPath;
    }

    getPagePath(pagePath) {
        const dashboards = [
            'dashboard.html', 'coordenador.html', 'kpi_dashboard.html',
            'comissoes.html', 'teste_ia.html', 'clientes.html',
            'leads.html', 'relatorios.html'
        ];

        if (dashboards.includes(pagePath) || pagePath.includes('dashboard')) {
            return `/static/dashboards/${pagePath}`;
        }

        if (!pagePath.endsWith('.html')) pagePath += '.html';
        return `/static/pages/${pagePath}`;
    }

    updatePageTitle(title) {
        const titleElement = document.getElementById('page-title');
        if (titleElement) titleElement.textContent = title;
    }

    setActiveMenuItem(element) {
        document.querySelectorAll('.menu-item').forEach(item => {
            item.classList.remove('bg-primary', 'text-white');
        });

        if (element) {
            element.classList.add('bg-primary', 'text-white');
        }
    }

    injectIframeStyles(iframe) {
        setTimeout(() => {
            try {
                const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                if (!iframeDoc) return;

                // Remover estilos antigos
                const oldStyle = iframeDoc.getElementById('injected-styles');
                if (oldStyle) oldStyle.remove();

                // Criar novos estilos
                const styleEl = iframeDoc.createElement('style');
                styleEl.id = 'injected-styles';

                // CSS para garantir scroll
                styleEl.textContent = `
                    html, body {
                        min-height: 100vh !important;
                        height: auto !important;
                        overflow-y: auto !important;
                        overflow-x: hidden !important;
                    }
                    
                    .max-w-7xl {
                        min-height: 800px !important;
                        padding-bottom: 100px !important;
                    }
                    
                    /* Barra de rolagem estilizada */
                    body::-webkit-scrollbar {
                        width: 12px;
                    }
                    
                    body::-webkit-scrollbar-track {
                        background: #f1f1f1;
                        border-radius: 6px;
                    }
                    
                    body::-webkit-scrollbar-thumb {
                        background: #d48262;
                        border-radius: 6px;
                        border: 3px solid #f1f1f1;
                    }
                    
                    body::-webkit-scrollbar-thumb:hover {
                        background: #b86a50;
                    }
                `;

                iframeDoc.head.appendChild(styleEl);
                console.log('🎨 Estilos injetados no iframe');

            } catch (error) {
                console.log('⚠️ Não foi possível injetar estilos (cross-origin)');
            }
        }, 500);
    }

    updateHistory(pagePath, pageTitle) {
        try {
            history.pushState(
                { page: pagePath, title: pageTitle },
                pageTitle,
                `/?page=${encodeURIComponent(pagePath)}`
            );
        } catch (e) { }
    }

    getErrorHTML(title, path) {
        return `
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { 
                        padding: 50px; 
                        font-family: 'Inter', sans-serif;
                        text-align: center;
                        background: #f8f9fa;
                    }
                    .error-box {
                        background: white;
                        padding: 30px;
                        border-radius: 10px;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                        max-width: 600px;
                        margin: 0 auto;
                    }
                    h2 { color: #d48262; margin-bottom: 20px; }
                    .path {
                        background: #f1f3f5;
                        padding: 10px;
                        border-radius: 5px;
                        font-family: monospace;
                        margin: 20px 0;
                    }
                    button {
                        background: #d48262;
                        color: white;
                        border: none;
                        padding: 12px 24px;
                        border-radius: 6px;
                        cursor: pointer;
                        font-weight: bold;
                    }
                </style>
            </head>
            <body>
                <div class="error-box">
                    <h2>⚠️ Erro ao carregar página</h2>
                    <p><strong>${title}</strong></p>
                    <div class="path">${path}</div>
                    <button onclick="window.parent.loadPage('dashboard.html', 'Dashboard Geral')">
                        Voltar ao Dashboard
                    </button>
                </div>
            </body>
            </html>
        `;
    }

    handleSearch(query) {
        if (!query.trim()) return;
        alert(`Busca em desenvolvimento: ${query}`);
    }

    toggleSubmenu(id) {
        const submenu = document.getElementById(id);
        const icon = document.getElementById(`icon-${id}`);

        if (submenu.classList.contains('hidden')) {
            submenu.classList.remove('hidden');
            if (icon) icon.classList.add('rotate-180');
        } else {
            submenu.classList.add('hidden');
            if (icon) icon.classList.remove('rotate-180');
        }
    }

    toggleSidebar() {
        const expanded = document.getElementById('expanded-sidebar');
        expanded.classList.toggle('hidden');
        localStorage.setItem('sidebarExpanded', expanded.classList.contains('hidden') ? 'false' : 'true');
    }

    logout() {
        if (confirm('Tem certeza que deseja sair?')) {
            alert('Sistema de logout em desenvolvimento...');
            window.location.reload();
        }
    }
}


// ============================================
// BREADCRUMB DINÂMICO
// ============================================

function updateBreadcrumb(pageTitle, pathParts = []) {
    const breadcrumbNav = document.querySelector('nav.mt-4');
    if (!breadcrumbNav) return;
    
    if (!pathParts.length) {
        // Se não tiver pathParts, usa apenas o título da página
        breadcrumbNav.innerHTML = `
            <a href="#" onclick="loadPage('dashboard.html', 'Dashboard Geral'); return false;" class="hover:text-white opacity-80">Home</a>
            <span class="mx-2 opacity-60">/</span>
            <span class="font-medium">${pageTitle}</span>
        `;
        return;
    }
    
    // Constroi o breadcrumb com os caminhos
    let breadcrumbHtml = `<a href="#" onclick="loadPage('dashboard.html', 'Dashboard Geral'); return false;" class="hover:text-white opacity-80">Home</a>`;
    
    pathParts.forEach((part, index) => {
        breadcrumbHtml += `<span class="mx-2 opacity-60">/</span>`;
        
        if (index === pathParts.length - 1) {
            // Último item (página atual)
            breadcrumbHtml += `<span class="font-medium">${part.title || part}</span>`;
        } else {
            // Item clicável
            breadcrumbHtml += `<a href="#" onclick="${part.action || `loadPage('${part.path}', '${part.title}')`}; return false;" class="hover:text-white opacity-80">${part.title || part}</a>`;
        }
    });
    
    breadcrumbNav.innerHTML = breadcrumbHtml;
}

// Override da função loadPage existente
const originalLoadPage = window.loadPage;
window.loadPage = function(pageUrl, pageTitle, element) {
    // Atualiza o título da página
    const titleElement = document.getElementById('page-title');
    if (titleElement) {
        titleElement.textContent = pageTitle;
    }
    
    // Atualiza o breadcrumb baseado na URL
    updateBreadcrumbFromUrl(pageUrl, pageTitle);
    
    // Carrega no iframe
    const iframe = document.getElementById('main-frame');
    const loading = document.getElementById('frame-loading');
    
    if (loading) loading.style.display = 'flex';
    if (iframe) {
        iframe.src = pageUrl;
        
        // Remove event listener anterior se existir
        iframe.onload = function() {
            if (loading) loading.style.display = 'none';
            
            // Tenta enviar informações do breadcrumb para o iframe
            try {
                iframe.contentWindow.postMessage({
                    type: 'breadcrumb',
                    pageTitle: pageTitle,
                    pageUrl: pageUrl
                }, '*');
            } catch(e) {
                console.log('Não foi possível enviar mensagem para o iframe');
            }
        };
    }
    
    // Atualiza o estado ativo do menu
    if (element) {
        document.querySelectorAll('.menu-item').forEach(item => {
            item.classList.remove('active', 'bg-primary/10');
        });
        element.classList.add('active', 'bg-primary/10');
    }
    
    // Salva no histórico
    history.pushState({ pageUrl, pageTitle }, pageTitle, `#${pageUrl}`);
};

// Função para atualizar breadcrumb baseado na URL
function updateBreadcrumbFromUrl(url, pageTitle) {
    const breadcrumbMap = {
        // Dashboard
        'dashboard.html': { title: 'Dashboard Geral', path: [] },
        'coordenador.html': { title: 'Dashboard Coordenador', path: [] },
        'kpi_dashboard.html': { title: 'Dashboard KPI', path: [] },
        
        // Relatórios
        'relatorios/kpi_financeiro2.html': { 
            title: 'Executivo', 
            path: [
                { title: 'Relatórios', action: "showAlert('Relatórios')" }
            ]
        },
        'relatorios/kpi_financeiro.html': { 
            title: 'Financeiro', 
            path: [
                { title: 'Relatórios', action: "showAlert('Relatórios')" }
            ]
        },
        'relatorios/performance_times.html': { 
            title: 'Times', 
            path: [
                { title: 'Relatórios', action: "showAlert('Relatórios')" }
            ]
        },
        
        // Clientes & Leads
        'leads/incluir_leads.html': { 
            title: 'Incluir Lead', 
            path: [
                { title: 'Clientes & Leads', action: "toggleSubmenu('clientes-leads-menu')" }
            ]
        },
        'leads/atualizar_leads.html': { 
            title: 'Atualizar Leads', 
            path: [
                { title: 'Clientes & Leads', action: "toggleSubmenu('clientes-leads-menu')" }
            ]
        },
        'clients/base_clients.html': { 
            title: 'Base de Clientes', 
            path: [
                { title: 'Clientes & Leads', action: "toggleSubmenu('clientes-leads-menu')" }
            ]
        },
        'chat/chat_corretores.html': { 
            title: 'Chat Corretores', 
            path: [
                { title: 'Clientes & Leads', action: "toggleSubmenu('clientes-leads-menu')" }
            ]
        },
        
        // Financeiro
        'financeiro/despesas.html': { 
            title: 'Despesas', 
            path: [
                { title: 'Financeiro', action: "toggleSubmenu('financeiro-menu')" }
            ]
        },
        'financeiro/receitas.html': { 
            title: 'Receitas', 
            path: [
                { title: 'Financeiro', action: "toggleSubmenu('financeiro-menu')" }
            ]
        },
        'financeiro/propostas.html': { 
            title: 'Analisador de Propostas', 
            path: [
                { title: 'Financeiro', action: "toggleSubmenu('financeiro-menu')" }
            ]
        },
        'financeiro/aprovacoes_financeira.html': { 
            title: 'Aprovações Financeiras', 
            path: [
                { title: 'Financeiro', action: "toggleSubmenu('financeiro-menu')" }
            ]
        },
        'financeiro/comissionamentos.html': { 
            title: 'Comissionamento', 
            path: [
                { title: 'Financeiro', action: "toggleSubmenu('financeiro-menu')" }
            ]
        },
        
        // Marketing
        'marketing/campanhas.html': { 
            title: 'Campanhas', 
            path: [
                { title: 'Marketing', action: "toggleSubmenu('marketing-menu')" }
            ]
        },
        'marketing/gerenciamento.html': { 
            title: 'Gerenciamento', 
            path: [
                { title: 'Marketing', action: "toggleSubmenu('marketing-menu')" }
            ]
        },
        
        // Operações
        'operacoes/admin_chat.html': { 
            title: 'Admin Chat', 
            path: [
                { title: 'Operações', action: "toggleSubmenu('operacao-menu')" }
            ]
        },
        'operacoes/banco_corretores.html': { 
            title: 'Banco de Corretores', 
            path: [
                { title: 'Operações', action: "toggleSubmenu('operacao-menu')" }
            ]
        },
        'operacoes/calendario_geral.html': { 
            title: 'Calendário Geral', 
            path: [
                { title: 'Operações', action: "toggleSubmenu('operacao-menu')" }
            ]
        },
        
        // Treinamento & RH
        'comissoes.html': { 
            title: 'HR Page - Central RH', 
            path: [
                { title: 'Treinamento & RH', action: "toggleSubmenu('treinamento-menu')" }
            ]
        },
        'treinamento_rh/treinamentos.html': { 
            title: 'Treinamentos', 
            path: [
                { title: 'Treinamento & RH', action: "toggleSubmenu('treinamento-menu')" }
            ]
        },
        
        // Executivo
        'executivo/gerenc_metas.html': { 
            title: 'Gerenciamento Metas', 
            path: [
                { title: 'Executivo', action: "showAlert('Executivo')" }
            ]
        },
        
        // Configurações
        'configuracoes.html': { title: 'Configurações', path: [] },
        'perfil.html': { title: 'Perfil', path: [] }
    };
    
    const config = breadcrumbMap[url] || { title: pageTitle, path: [] };
    updateBreadcrumb(config.title, config.path);
}

// Função auxiliar para alertas (pode ser removida ou adaptada)
window.showAlert = function(message) {
    console.log(message);
    // Se quiser um toast/notificação
    // showToast(message);
};

// Listener para navegação do histórico
window.addEventListener('popstate', function(event) {
    if (event.state) {
        loadPage(event.state.pageUrl, event.state.pageTitle);
    }
});

// Listener para mensagens do iframe (breadcrumb interno)
window.addEventListener('message', function(event) {
    if (event.data && event.data.type === 'breadcrumb') {
        updateBreadcrumb(event.data.pageTitle, event.data.pathParts || []);
        const titleElement = document.getElementById('page-title');
        if (titleElement && event.data.pageTitle) {
            titleElement.textContent = event.data.pageTitle;
        }
    }
});

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    // Configura página inicial
    const currentUrl = window.location.hash.substring(1) || 'dashboard.html';
    const currentTitle = document.getElementById('page-title')?.textContent || 'Dashboard Geral';
    updateBreadcrumbFromUrl(currentUrl, currentTitle);
});


// ============================================
// INICIALIZAÇÃO
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    window.navigationSystem = new NavigationSystem();

    // Funções globais
    window.loadPage = (pagePath, pageTitle, element) =>
        window.navigationSystem.loadPage(pagePath, pageTitle, element);

    window.toggleSubmenu = (id) =>
        window.navigationSystem.toggleSubmenu(id);

    window.toggleSidebar = () =>
        window.navigationSystem.toggleSidebar();

    window.logout = () =>
        window.navigationSystem.logout();
});