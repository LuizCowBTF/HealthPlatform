// /app/frontend/js/main.js
// Sistema de navegação centralizado

const App = {
    config: {
        baseURL: window.location.origin,
        paths: {
            dashboards: '/static/dashboards/',
            pages: '/static/pages/'
        }
    },

    state: {
        currentPage: '',
        isLoading: false
    },

    init() {
        console.log('🚀 HealthCRM SPA - Inicializado');
        this.setupEventListeners();
        this.loadInitialPage();
    },

    setupEventListeners() {
        // Configurar busca global
        const searchInput = document.getElementById('global-search');
        if (searchInput) {
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.handleSearch(searchInput.value);
                }
            });
        }

        // Configurar histórico do navegador
        window.addEventListener('popstate', (event) => {
            if (event.state && event.state.page) {
                this.loadPage(event.state.page, event.state.title);
            }
        });
    },

    loadInitialPage() {
        // Verificar URL
        const urlParams = new URLSearchParams(window.location.search);
        const pageParam = urlParams.get('page');

        if (pageParam) {
            this.loadPage(decodeURIComponent(pageParam), 'Página Carregada');
        } else {
            // Carregar dashboard por padrão
            setTimeout(() => {
                this.loadPage('dashboard.html', 'Dashboard Geral');
            }, 300);
        }
    },

    async loadPage(pagePath, pageTitle, element = null) {
        console.log(`📄 Carregando: ${pagePath}`);

        // Prevenir múltiplos cliques
        if (this.state.isLoading) return;
        this.state.isLoading = true;

        const iframe = document.getElementById('main-frame');
        const loading = document.getElementById('frame-loading');

        if (!iframe || !loading) {
            console.error('Elementos não encontrados');
            return;
        }

        // Mostrar loading
        loading.style.display = 'flex';

        // Determinar caminho
        let fullPath = this.getPagePath(pagePath);
        console.log(`📍 Caminho: ${fullPath}`);

        // Atualizar título
        this.updatePageTitle(pageTitle);

        // Marcar item ativo
        if (element) {
            this.setActiveMenuItem(element);
        }

        // Configurar iframe
        iframe.onload = () => {
            console.log('✅ Página carregada');
            setTimeout(() => {
                loading.style.display = 'none';
                this.state.isLoading = false;
                this.adjustIframeHeight(iframe);
                this.updateHistory(pagePath, pageTitle);
            }, 300);
        };

        iframe.onerror = () => {
            console.error(`❌ Erro ao carregar: ${fullPath}`);
            loading.style.display = 'none';
            this.state.isLoading = false;
            this.showError(pageTitle, fullPath);
        };

        // Carregar
        iframe.src = fullPath;
        this.state.currentPage = pagePath;
    },

    getPagePath(pagePath) {
        // Dashboards conhecidos
        const dashboards = [
            'dashboard.html', 'coordenador.html', 'kpi_dashboard.html',
            'comissoes.html', 'teste_ia.html', 'clientes.html',
            'leads.html', 'relatorios.html'
        ];

        // Se for dashboard
        if (dashboards.includes(pagePath) || pagePath.includes('dashboard')) {
            return `${this.config.paths.dashboards}${pagePath}`;
        }

        // Se já tem .html
        if (pagePath.endsWith('.html')) {
            return `${this.config.paths.pages}${pagePath}`;
        }

        // Adicionar .html
        return `${this.config.paths.pages}${pagePath}.html`;
    },

    updatePageTitle(title) {
        const titleElement = document.getElementById('page-title');
        if (titleElement) {
            titleElement.textContent = title;
        }
    },

    setActiveMenuItem(element) {
        document.querySelectorAll('.menu-item').forEach(item => {
            item.classList.remove('bg-primary', 'text-white');
        });

        if (element) {
            element.classList.add('bg-primary', 'text-white');
        }
    },

    adjustIframeHeight(iframe) {
        try {
            const doc = iframe.contentDocument || iframe.contentWindow.document;
            const height = Math.max(doc.body.scrollHeight, doc.documentElement.scrollHeight, 600);
            iframe.style.height = height + 'px';
        } catch (e) {
            iframe.style.height = '100%';
        }
    },

    updateHistory(pagePath, pageTitle) {
        try {
            history.pushState(
                { page: pagePath, title: pageTitle },
                pageTitle,
                `/?page=${encodeURIComponent(pagePath)}`
            );
        } catch (e) {
            console.log('⚠️ Histórico não atualizado');
        }
    },

    showError(pageTitle, path) {
        const iframe = document.getElementById('main-frame');
        if (!iframe) return;

        iframe.srcdoc = `
            <html>
            <body style="padding:40px;text-align:center;font-family:'Segoe UI';background:#f5f5f5;">
                <div style="background:white;padding:30px;border-radius:10px;box-shadow:0 5px 15px rgba(0,0,0,0.1);max-width:600px;margin:0 auto;">
                    <h2 style="color:#d48262;">⚠️ Página não encontrada</h2>
                    <p><strong>${pageTitle}</strong></p>
                    <div style="background:#f8f9fa;padding:15px;border-radius:5px;margin:20px 0;text-align:left;font-family:monospace;font-size:12px;">
                        ${path}
                    </div>
                    <button onclick="window.parent.App.loadPage('dashboard.html', 'Dashboard')"
                            style="background:#d48262;color:white;padding:10px 20px;border:none;border-radius:5px;cursor:pointer;">
                        Voltar para Dashboard
                    </button>
                </div>
            </body>
            </html>
        `;
    },

    handleSearch(query) {
        if (!query.trim()) return;
        console.log(`🔍 Buscando: ${query}`);
        alert(`Funcionalidade de busca em desenvolvimento\n\nTermo: ${query}`);
    }
};

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => App.init());

// Exportar para uso global
window.App = App;