// ============================================
// SISTEMA DE NAVEGAÇÃO - VERSÃO CORRIGIDA
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
                    alert(`Busca: ${searchInput.value}`);
                }
            });
        }

        // Histórico
        window.addEventListener('popstate', (event) => {
            if (event.state && event.state.page) {
                this.loadPage(event.state.page, event.state.title);
            }
        });

        // Mensagens do iframe
        window.addEventListener('message', (event) => {
            if (event.data && event.data.type === 'breadcrumb') {
                this.updateBreadcrumb(event.data.pageTitle, event.data.pathParts || []);
                const titleElement = document.getElementById('page-title');
                if (titleElement) titleElement.textContent = event.data.pageTitle;
            }
        });
    }

    loadInitialPage() {
        setTimeout(() => {
            this.loadPage('dashboard.html', 'Dashboard Geral');
        }, 100);
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
        
        // Atualiza título da página
        const titleElement = document.getElementById('page-title');
        if (titleElement) titleElement.textContent = pageTitle;
        
        // Atualiza breadcrumb
        this.updateBreadcrumbFromPath(pagePath, pageTitle);

        // Atualiza menu ativo
        if (element) {
            this.setActiveMenuItem(element);
        }

        // Constrói o caminho baseado na estrutura real
        const fullPath = this.getFullPath(pagePath);
        console.log(`📍 Caminho: ${fullPath}`);

        // Timeout para evitar loading infinito
        const timeout = setTimeout(() => {
            if (this.isLoading) {
                loading.style.display = 'none';
                this.isLoading = false;
                console.error('❌ Timeout ao carregar:', pagePath);
            }
        }, 10000);

        iframe.onload = () => {
            clearTimeout(timeout);
            console.log('✅ Página carregada:', pagePath);
            setTimeout(() => {
                loading.style.display = 'none';
                this.isLoading = false;
                this.updateHistory(pagePath, pageTitle);
                this.injectIframeStyles(iframe);
            }, 200);
        };

        iframe.onerror = () => {
            clearTimeout(timeout);
            console.error(`❌ Erro ao carregar: ${fullPath}`);
            loading.style.display = 'none';
            this.isLoading = false;
            this.showErrorInIframe(iframe, pageTitle, fullPath);
        };

        iframe.src = fullPath;
    }

    getFullPath(pagePath) {
        // Remove .html se já tiver
        let path = pagePath;
        if (!path.endsWith('.html') && !path.includes('.')) {
            path = path + '.html';
        }
        
        // Dashboards (arquivos na pasta /dashboards/)
        const dashboards = ['dashboard.html', 'coordenador.html', 'kpi_dashboard.html', 
                           'comissoes.html', 'clientes.html', 'leads.html', 
                           'relatorios.html', 'teste-ia.html'];
        
        if (dashboards.includes(path) || path === 'kpi_dashboard.html') {
            return `/dashboards/${path}`;
        }
        
        // Páginas com subpastas
        if (path.startsWith('leads/')) return `/pages/${path}`;
        if (path.startsWith('clients/')) return `/pages/${path}`;
        if (path.startsWith('chat/')) return `/pages/${path}`;
        if (path.startsWith('financeiro/')) return `/pages/${path}`;
        if (path.startsWith('marketing/')) return `/pages/${path}`;
        if (path.startsWith('operacoes/')) return `/pages/${path}`;
        if (path.startsWith('treinamento_rh/')) return `/pages/${path}`;
        if (path.startsWith('relatorios/')) return `/pages/${path}`;
        if (path.startsWith('executivo/')) return `/pages/${path}`;
        
        // Páginas na raiz de /pages/
        if (path === 'configuracoes.html' || path === 'perfil.html') {
            return `/pages/${path}`;
        }
        
        // Fallback
        return `/pages/${path}`;
    }

    setActiveMenuItem(element) {
        document.querySelectorAll('.menu-item').forEach(item => {
            item.classList.remove('active', 'bg-primary/10');
        });
        if (element) {
            element.classList.add('active', 'bg-primary/10');
        }
    }

    updateHistory(pagePath, pageTitle) {
        try {
            const url = new URL(window.location.href);
            url.searchParams.set('page', pagePath);
            history.pushState({ page: pagePath, title: pageTitle }, pageTitle, url.toString());
        } catch (e) {}
    }

    injectIframeStyles(iframe) {
        setTimeout(() => {
            try {
                const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                if (!iframeDoc) return;
                
                const style = iframeDoc.createElement('style');
                style.textContent = `
                    body { overflow-y: auto !important; }
                    html { overflow-y: auto !important; }
                `;
                iframeDoc.head.appendChild(style);
            } catch(e) {}
        }, 300);
    }

    showErrorInIframe(iframe, title, path) {
        iframe.srcdoc = `
            <html>
            <head><style>
                body { font-family: sans-serif; padding: 50px; text-align: center; background: #f5f5f5; }
                .error { color: #d48262; margin-bottom: 20px; }
                .path { background: #fff; padding: 10px; border-radius: 5px; margin: 20px; font-family: monospace; }
                button { background: #d48262; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
            </style></head>
            <body>
                <h2 class="error">⚠️ Erro ao carregar</h2>
                <p><strong>${title}</strong></p>
                <div class="path">${path}</div>
                <button onclick="window.parent.location.reload()">Voltar</button>
            </body>
            </html>
        `;
    }

    // ========== BREADCRUMB ==========
    
    updateBreadcrumb(pageTitle, pathParts = []) {
        const breadcrumbNav = document.getElementById('breadcrumb');
        console.log('🔍 Procurando #breadcrumb:', breadcrumbNav);
        
        if (!breadcrumbNav) {
            console.warn('⚠️ #breadcrumb-nav não encontrado');
            const container = document.querySelector('mt-4');
            if (container && !breadcrumbNav) {
                const newNav = document.createElement('nav');
                newNav.id = 'breadcrumb';
                newNav.className = 'flex items-center text-sm text-white/80 mb-4';
                container.appendChild(newNav);
                console.log('✅ Breadcrumb criado dinamicamente');
            }
            return;
        }
        
        let html = `<a href="#" onclick="window.navigationSystem.loadPage('dashboard.html', 'Dashboard Geral'); return false;" class="text-white/80 hover:text-white transition-colors">Home</a>`;
        
        if (pathParts && pathParts.length > 0) {
            for (let i = 0; i < pathParts.length; i++) {
                const part = pathParts[i];
                html += `<span class="mx-2 text-white/50">/</span>`;
                if (i === pathParts.length - 1) {
                    html += `<span class="text-white font-medium">${part.title || part}</span>`;
                } else {
                    html += `<span class="text-white/80">${part.title || part}</span>`;
                }
            }
        }
        
        if (pageTitle !== 'Dashboard Geral') {
            if (pathParts.length === 0) {
                html += `<span class="mx-2 text-white/50">/</span>`;
            } else {
                html += `<span class="mx-2 text-white/50">/</span>`;
            }
            html += `<span class="text-white font-medium">${pageTitle}</span>`;
        }
        
        breadcrumbNav.innerHTML = html;
        console.log('🍞 Breadcrumb atualizado:', pageTitle);
    }

    updateBreadcrumbFromPath(path, title) {
        // Mapeamento de pastas para nomes amigáveis
        const moduleMap = {
            'leads/': 'Clientes & Leads',
            'clients/': 'Clientes & Leads',
            'chat/': 'Clientes & Leads',
            'financeiro/': 'Financeiro',
            'marketing/': 'Marketing',
            'operacoes/': 'Operações',
            'treinamento_rh/': 'Treinamento & RH',
            'relatorios/': 'Relatórios',
            'executivo/': 'Executivo'
        };
        
        let moduleName = '';
        for (const [key, value] of Object.entries(moduleMap)) {
            if (path.includes(key)) {
                moduleName = value;
                break;
            }
        }
        
        // Títulos especiais
        const specialTitles = {
            'kpi_financeiro2.html': 'Executivo',
            'kpi_financeiro.html': 'Financeiro',
            'performance_times.html': 'Times',
            'gerenc_metas.html': 'Gerenciamento Metas',
            'HR_page.html': 'Central RH'
        };
        
        let finalTitle = title;
        for (const [key, value] of Object.entries(specialTitles)) {
            if (path.includes(key)) {
                finalTitle = value;
                break;
            }
        }
        
        const pathParts = moduleName ? [{ title: moduleName }] : [];
        this.updateBreadcrumb(finalTitle, pathParts);
    }

    // ========== UTILIDADES ==========
    
    toggleSubmenu(id) {
        const submenu = document.getElementById(id);
        const icon = document.getElementById(`icon-${id}`);
        if (submenu) {
            submenu.classList.toggle('hidden');
            if (icon) {
                if (submenu.classList.contains('hidden')) {
                    icon.classList.remove('rotate-180');
                } else {
                    icon.classList.add('rotate-180');
                }
            }
        }
    }

    toggleSidebar() {
        const sidebar = document.getElementById('expanded-sidebar');
        if (sidebar) {
            sidebar.classList.toggle('hidden');
            localStorage.setItem('sidebarExpanded', (!sidebar.classList.contains('hidden')).toString());
        }
    }

    logout() {
        if (confirm('Tem certeza que deseja sair?')) {
            window.location.href = '/pages/auth/login.html';
        }
    }
}

// Inicialização
let navigationSystem = null;

document.addEventListener('DOMContentLoaded', () => {
    navigationSystem = new NavigationSystem();
    window.navigationSystem = navigationSystem;
    
    // Funções globais
    window.loadPage = (path, title, el) => navigationSystem.loadPage(path, title, el);
    window.toggleSubmenu = (id) => navigationSystem.toggleSubmenu(id);
    window.toggleSidebar = () => navigationSystem.toggleSidebar();
    window.logout = () => navigationSystem.logout();
    
    // Restaura estado do sidebar
    const savedState = localStorage.getItem('sidebarExpanded');
    if (savedState === 'false') {
        const sidebar = document.getElementById('expanded-sidebar');
        if (sidebar) sidebar.classList.add('hidden');
    }
    
    console.log('✅ Sistema de navegação pronto');
});