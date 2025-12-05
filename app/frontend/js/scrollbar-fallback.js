// ============================================
// SCROLLBAR FALLBACK - GARANTE BARRA ESTILIZADA
// ============================================

console.log('🎨 Scrollbar Fallback - Ativado');

class ScrollbarFallback {
    constructor() {
        this.isInIframe = window.self !== window.top;

        if (this.isInIframe) {
            this.init();
        }
    }

    init() {
        console.log('🔧 Configurando barra de rolagem personalizada...');

        // 1. Aplicar estilos imediatamente
        this.applyScrollbarStyles();

        // 2. Verificar periodicamente
        setInterval(() => this.checkAndFixScrollbar(), 2000);

        // 3. Aplicar após carregamento completo
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(() => this.applyScrollbarStyles(), 500);
        });
    }

    applyScrollbarStyles() {
        // Verificar se já temos estilos
        if (document.getElementById('scrollbar-styles-applied')) return;

        console.log('🔄 Aplicando estilos da barra de rolagem...');

        // CSS definitivo para barra
        const style = document.createElement('style');
        style.id = 'scrollbar-styles-applied';

        style.textContent = `
            /* =========================================== */
            /* BARRA DE ROLAGEM DEFINITIVA - HEALTHCRM */
            /* =========================================== */
            
            /* FUNDO DA PÁGINA - garantir contraste */
            html {
                background: #f8f6f6 !important;
            }
            
            /* BARRA SEMPRE VISÍVEL */
            ::-webkit-scrollbar {
                width: 16px !important;
                height: 16px !important;
                display: block !important;
                visibility: visible !important;
            }
            
            /* TRACK - estilo premium */
            ::-webkit-scrollbar-track {
                background: linear-gradient(
                    to bottom,
                    #f8f9fa,
                    #f1f3f5
                ) !important;
                border-radius: 12px !important;
                margin: 6px !important;
                border: 4px solid transparent !important;
                background-clip: padding-box !important;
                box-shadow: 
                    inset 0 1px 3px rgba(0,0,0,0.05),
                    0 1px 0 rgba(255,255,255,0.8) !important;
            }
            
            /* THUMB - cor primária do HealthCRM */
            ::-webkit-scrollbar-thumb {
                background: linear-gradient(
                    135deg,
                    #d48262 0%,
                    #d48262 30%,
                    #b86a50 70%,
                    #9c533d 100%
                ) !important;
                border-radius: 12px !important;
                border: 4px solid transparent !important;
                background-clip: padding-box !important;
                box-shadow: 
                    inset 0 -1px 0 rgba(0,0,0,0.1),
                    inset 0 1px 0 rgba(255,255,255,0.4) !important;
                min-height: 60px !important;
            }
            
            /* THUMB HOVER - efeito interativo */
            ::-webkit-scrollbar-thumb:hover {
                background: linear-gradient(
                    135deg,
                    #b86a50 0%,
                    #9c533d 30%,
                    #804536 70%,
                    #663829 100%
                ) !important;
                box-shadow: 
                    inset 0 -1px 0 rgba(0,0,0,0.2),
                    inset 0 1px 0 rgba(255,255,255,0.3),
                    0 0 8px rgba(212, 130, 98, 0.4) !important;
            }
            
            /* THUMB ACTIVE - quando arrastando */
            ::-webkit-scrollbar-thumb:active {
                background: linear-gradient(
                    135deg,
                    #9c533d 0%,
                    #804536 100%
                ) !important;
            }
            
            /* CORNER */
            ::-webkit-scrollbar-corner {
                background: #f8f9fa !important;
            }
            
            /* =========================================== */
            /* FIREFOX */
            /* =========================================== */
            * {
                scrollbar-width: auto !important;
                scrollbar-color: #d48262 #f8f9fa !important;
            }
            
            /* =========================================== */
            /* GARANTIR ESPAÇO PARA BARRA */
            /* =========================================== */
            body {
                padding-right: 2px !important;
            }
            
            /* Indicador visual (debug) */
            .scrollbar-styled-indicator {
                position: fixed;
                bottom: 10px;
                right: 10px;
                background: #d48262;
                color: white;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 10px;
                opacity: 0.7;
                z-index: 9999;
                pointer-events: none;
            }
        `;

        document.head.appendChild(style);

        // Adicionar indicador visual (opcional, pode remover depois)
        const indicator = document.createElement('div');
        indicator.className = 'scrollbar-styled-indicator';
        indicator.textContent = 'Barra Estilizada ✓';
        document.body.appendChild(indicator);

        // Remover indicador após 3 segundos
        setTimeout(() => {
            if (indicator.parentNode) {
                indicator.parentNode.removeChild(indicator);
            }
        }, 3000);

        console.log('✅ Estilos da barra aplicados com sucesso!');
    }

    checkAndFixScrollbar() {
        // Verificar se a barra está visível
        const hasScrollbar = document.documentElement.scrollHeight > window.innerHeight;

        if (!hasScrollbar) {
            // Forçar barra visível
            document.documentElement.style.minHeight = (window.innerHeight + 10) + 'px';
        }
    }
}

// ============================================
// INICIALIZAÇÃO
// ============================================

// Inicializar automaticamente se estiver em iframe
if (window.self !== window.top) {
    document.addEventListener('DOMContentLoaded', () => {
        window.scrollbarFallback = new ScrollbarFallback();
    });
}

// Função manual para forçar estilos
window.forceScrollbarStyles = function () {
    if (window.scrollbarFallback) {
        window.scrollbarFallback.applyScrollbarStyles();
        return true;
    }
    return false;
};