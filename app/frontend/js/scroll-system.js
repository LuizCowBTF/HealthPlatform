// ===========================================
// SISTEMA DE ROLAGEM PADRÃO - HEALTHPLATFORM
// ===========================================

const ScrollSystem = {

    // CONFIGURAÇÕES
    config: {
        barWidth: 20,           // Largura padrão da barra (px)
        barColor: '#d48262',    // Cor principal
        trackColor: '#f8f9fa',  // Cor do track
        animationSpeed: 300,    // Velocidade das animações (ms)
        forceScrollbar: true,   // Forçar barra sempre visível
        debug: false           // Modo debug
    },

    // ESTADO DO SISTEMA
    state: {
        isInitialized: false,
        currentBarWidth: 20,
        scrollPosition: 0,
        isMobile: false,
        hasScrollbar: true
    },

    // ===========================================
    // INICIALIZAÇÃO
    // ===========================================

    init(options = {}) {
        console.log('🚀 Inicializando sistema de rolagem...');

        // Mesclar configurações
        this.config = { ...this.config, ...options };

        // Detectar dispositivo
        this.detectDevice();

        // Aplicar configurações iniciais
        this.applyBaseStyles();

        // Configurar eventos
        this.setupEventListeners();

        // Forçar barra de rolagem se configurado
        if (this.config.forceScrollbar) {
            this.forceScrollbarVisibility();
        }

        // Verificar se a página tem conteúdo suficiente
        this.checkContentHeight();

        // Marcar como inicializado
        this.state.isInitialized = true;

        // Log de sucesso
        console.log('✅ Sistema de rolagem inicializado');
        this.log('Configuração:', this.config);

        return this;
    },

    // ===========================================
    // FUNÇÕES PRINCIPAIS
    // ===========================================

    detectDevice() {
        const isMobile = window.innerWidth <= 768;
        this.state.isMobile = isMobile;

        // Ajustar largura da barra para mobile
        if (isMobile) {
            this.state.currentBarWidth = 16;
            document.body.classList.add('is-mobile');
        } else {
            this.state.currentBarWidth = this.config.barWidth;
            document.body.classList.remove('is-mobile');
        }

        this.log('Dispositivo detectado:', isMobile ? 'Mobile' : 'Desktop');
    },

    applyBaseStyles() {
        // Adicionar classe base ao body
        document.body.classList.add('scroll-system-initialized');

        // Aplicar rolagem suave se suportado
        if ('scrollBehavior' in document.documentElement.style) {
            document.documentElement.style.scrollBehavior = 'smooth';
            document.body.classList.add('scroll-smooth');
        }

        // Garantir que o body tenha altura mínima
        document.body.style.minHeight = '100vh';

        this.log('Estilos base aplicados');
    },

    setupEventListeners() {
        // Evento de redimensionamento
        window.addEventListener('resize', () => {
            this.detectDevice();
            this.checkContentHeight();
        });

        // Evento de scroll
        window.addEventListener('scroll', () => {
            this.state.scrollPosition = window.scrollY;
            this.updateScrollIndicator();
        });

        // Evento de carregamento da página
        window.addEventListener('load', () => {
            setTimeout(() => {
                document.body.classList.add('loaded');
                this.checkContentHeight();
            }, 100);
        });

        // Detectar mudanças no DOM (para conteúdo dinâmico)
        this.setupMutationObserver();

        this.log('Event listeners configurados');
    },

    setupMutationObserver() {
        // Observar mudanças no DOM que podem afetar a altura
        const observer = new MutationObserver((mutations) => {
            let shouldCheckHeight = false;

            mutations.forEach((mutation) => {
                if (mutation.type === 'childList' || mutation.type === 'attributes') {
                    shouldCheckHeight = true;
                }
            });

            if (shouldCheckHeight) {
                setTimeout(() => this.checkContentHeight(), 50);
            }
        });

        // Observar o body e main content
        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true
        });

        this.log('Mutation Observer configurado');
    },

    // ===========================================
    // FUNÇÕES DE CONTROLE
    // ===========================================

    forceScrollbarVisibility() {
        // Forçar barra sempre visível
        document.body.style.overflowY = 'scroll';
        document.documentElement.style.overflowY = 'scroll';

        // Adicionar classe para garantir
        document.body.classList.add('scrollbar-always');

        this.log('Barra de rolagem forçada como sempre visível');
    },

    checkContentHeight() {
        const bodyHeight = document.body.scrollHeight;
        const htmlHeight = document.documentElement.scrollHeight;
        const viewportHeight = window.innerHeight;
        const maxHeight = Math.max(bodyHeight, htmlHeight);

        this.log(`Alturas: Conteúdo=${maxHeight}px, Viewport=${viewportHeight}px`);

        // Se o conteúdo for menor que a viewport, expandir
        if (maxHeight < viewportHeight && this.config.forceScrollbar) {
            const minHeight = viewportHeight + 1; // 1px a mais para forçar rolagem
            document.body.style.minHeight = minHeight + 'px';
            this.log(`Conteúdo expandido para ${minHeight}px`);
        }

        // Verificar se realmente tem barra de rolagem
        this.state.hasScrollbar = maxHeight > viewportHeight;

        // Disparar evento customizado
        this.dispatchEvent('scrollsystem:heightchecked', {
            contentHeight: maxHeight,
            viewportHeight: viewportHeight,
            hasScrollbar: this.state.hasScrollbar
        });

        return maxHeight;
    },

    updateScrollIndicator() {
        // Pode ser usado para mostrar indicador de progresso
        const scrollPercent = (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100;

        // Disparar evento de progresso
        this.dispatchEvent('scrollsystem:progress', {
            position: window.scrollY,
            percent: scrollPercent
        });

        return scrollPercent;
    },

    // ===========================================
    // FUNÇÕES UTILITÁRIAS
    // ===========================================

    // Alterar largura da barra dinamicamente
    setBarWidth(width) {
        if (width >= 12 && width <= 32) {
            this.state.currentBarWidth = width;

            // Aplicar via CSS custom property
            document.documentElement.style.setProperty('--scrollbar-width', width + 'px');

            // Adicionar classe apropriada
            document.body.classList.remove('scrollbar-extra-large', 'scrollbar-mega-large');

            if (width >= 24) {
                document.body.classList.add('scrollbar-extra-large');
            }
            if (width >= 28) {
                document.body.classList.add('scrollbar-mega-large');
            }

            this.log(`Largura da barra alterada para ${width}px`);
            return true;
        }

        console.warn(`Largura ${width}px fora do intervalo permitido (12-32px)`);
        return false;
    },

    // Alterar cores dinamicamente
    setColors(thumbColor, trackColor) {
        document.documentElement.style.setProperty('--scrollbar-thumb', thumbColor);
        document.documentElement.style.setProperty('--scrollbar-track', trackColor);

        this.log(`Cores alteradas: Thumb=${thumbColor}, Track=${trackColor}`);
    },

    // Reset para configurações padrão
    reset() {
        this.setBarWidth(this.config.barWidth);
        this.setColors(this.config.barColor, this.config.trackColor);
        document.body.style.minHeight = '100vh';

        this.log('Configurações resetadas para padrão');
    },

    // Desabilitar/abilitar rolagem
    disable() {
        document.body.classList.add('scrollbar-disabled');
        document.body.style.overflow = 'hidden';
        this.log('Rolagem desabilitada');
    },

    enable() {
        document.body.classList.remove('scrollbar-disabled');
        document.body.style.overflow = 'auto';
        this.log('Rolagem habilitada');
    },

    // Scroll para posição específica
    scrollTo(position = 0, duration = 500) {
        const start = window.scrollY;
        const change = position - start;
        const startTime = performance.now();

        const animateScroll = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);

            // Easing function (easeInOutQuad)
            const easeProgress = progress < 0.5
                ? 2 * progress * progress
                : 1 - Math.pow(-2 * progress + 2, 2) / 2;

            window.scrollTo(0, start + change * easeProgress);

            if (progress < 1) {
                requestAnimationFrame(animateScroll);
            }
        };

        requestAnimationFrame(animateScroll);
        this.log(`Scroll animado para posição ${position}px`);
    },

    // Scroll para elemento
    scrollToElement(selector, offset = 20) {
        const element = document.querySelector(selector);
        if (element) {
            const elementPosition = element.getBoundingClientRect().top + window.scrollY;
            this.scrollTo(elementPosition - offset);
            this.log(`Scroll para elemento: ${selector}`);
            return true;
        }

        console.warn(`Elemento não encontrado: ${selector}`);
        return false;
    },

    // ===========================================
    // EVENTOS CUSTOMIZADOS
    // ===========================================

    dispatchEvent(name, detail = {}) {
        const event = new CustomEvent(name, {
            detail: {
                timestamp: Date.now(),
                system: 'ScrollSystem',
                ...detail
            }
        });

        window.dispatchEvent(event);
        return event;
    },

    // ===========================================
    // DEBUG E LOG
    // ===========================================

    log(message, data = null) {
        if (this.config.debug) {
            if (data) {
                console.log(`[ScrollSystem] ${message}`, data);
            } else {
                console.log(`[ScrollSystem] ${message}`);
            }
        }
    },

    // ===========================================
    // GETTERS
    // ===========================================

    getScrollPosition() {
        return this.state.scrollPosition;
    },

    getScrollPercent() {
        return this.updateScrollIndicator();
    },

    isMobile() {
        return this.state.isMobile;
    },

    hasScrollbar() {
        return this.state.hasScrollbar;
    },

    // ===========================================
    // STATUS E INFO
    // ===========================================

    getInfo() {
        return {
            version: '1.0.0',
            initialized: this.state.isInitialized,
            config: this.config,
            state: this.state,
            viewport: {
                width: window.innerWidth,
                height: window.innerHeight
            },
            content: {
                bodyHeight: document.body.scrollHeight,
                htmlHeight: document.documentElement.scrollHeight
            }
        };
    },

    printInfo() {
        const info = this.getInfo();
        console.group('📊 ScrollSystem - Informações do Sistema');
        console.table(info.config);
        console.table(info.state);
        console.table(info.viewport);
        console.table(info.content);
        console.groupEnd();
        return info;
    }
};

// ===========================================
// INICIALIZAÇÃO AUTOMÁTICA
// ===========================================

// Auto-inicializar quando o DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        // Inicializar com configurações padrão
        window.ScrollSystem = ScrollSystem.init({
            forceScrollbar: true,     // Forçar barra sempre visível
            debug: false              // Modo debug desligado por padrão
        });
    });
} else {
    // DOM já carregado, inicializar imediatamente
    window.ScrollSystem = ScrollSystem.init({
        forceScrollbar: true,
        debug: false
    });
}

// Exportar para uso em módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ScrollSystem;
}