// ============================================
// IFRAME CONTENT FIXER - VERSÃO DEFINITIVA
// ============================================
// Garante que o conteúdo dentro do iframe seja COMPLETAMENTE visível
// ============================================

console.log('🔧 Iframe Content Fixer - Ativado');

class IframeContentFixer {
    constructor() {
        this.isInIframe = window.self !== window.top;
        this.minHeight = 800; // Altura mínima garantida
        this.contentExpanded = false;

        if (this.isInIframe) {
            this.init();
        }
    }

    init() {
        console.log('📦 Estamos dentro de um iframe - Configurando...');

        // 1. Configurar listeners primeiro
        this.setupParentCommandsListener();

        // 2. Tornar elementos expansíveis
        this.makeElementsExpandable();

        // 3. Adicionar espaço extra no FINAL
        this.addFinalSpace();

        // 4. Ajustar altura dinamicamente
        this.adjustContentHeight();

        // 5. Configurar observers para conteúdo dinâmico
        this.setupObservers();

        // 6. Informar ao parent nossa altura REAL
        this.reportHeightToParent();

        // 7. Forçar verificação inicial
        this.forceInitialCheck();
    }

    // ============================================
    // CONFIGURAÇÕES INICIAIS
    // ============================================

    makeElementsExpandable() {
        console.log('📐 Tornando elementos expansíveis...');

        // CSS CRÍTICO - Aplicar imediatamente
        const criticalStyles = `
            /* GARANTIA ABSOLUTA DE VISIBILIDADE */
            html, body {
                min-height: 100vh !important;
                height: auto !important;
                overflow: visible !important;
                overflow-x: hidden !important;
                margin: 0 !important;
                padding: 0 !important;
                padding-bottom: 150px !important;
            }
            
            /* Remover qualquer limite */
            .container, .max-w-7xl, .mx-auto {
                min-height: 100vh !important;
                max-height: none !important;
                height: auto !important;
                overflow: visible !important;
                padding-bottom: 100px !important;
            }
            
            /* Espaço entre elementos */
            .card, [class*="bg-"], [class*="rounded-"] {
                margin-bottom: 20px !important;
            }
            
            /* Garantir que tudo seja visível */
            * {
                max-height: none !important;
                overflow: visible !important;
            }
            
            /* MARCADOR FINAL VISÍVEL */
            .iframe-final-marker {
                height: 150px !important;
                width: 100% !important;
                background: linear-gradient(transparent, rgba(212, 130, 98, 0.15)) !important;
                border-top: 3px dashed #d48262 !important;
                position: relative !important;
                margin-top: 50px !important;
                opacity: 0.8 !important;
                display: block !important;
            }
            
            .final-marker-text {
                position: absolute !important;
                top: 50% !important;
                left: 50% !important;
                transform: translate(-50%, -50%) !important;
                background: #d48262 !important;
                color: white !important;
                padding: 8px 20px !important;
                border-radius: 25px !important;
                font-weight: bold !important;
                font-size: 14px !important;
                box-shadow: 0 4px 12px rgba(212, 130, 98, 0.3) !important;
            }
        `;

        const styleEl = document.createElement('style');
        styleEl.id = 'iframe-critical-styles';
        styleEl.textContent = criticalStyles;
        document.head.appendChild(styleEl);
    }

    addFinalSpace() {
        console.log('➕ Adicionando espaço final GARANTIDO...');

        // Remover marcadores antigos
        const oldMarkers = document.querySelectorAll('.iframe-final-marker');
        oldMarkers.forEach(el => el.remove());

        // Calcular quanto espaço precisamos
        const bodyHeight = document.body.scrollHeight;
        const viewportHeight = window.innerHeight;
        const neededHeight = Math.max(300, viewportHeight + 200 - bodyHeight);

        // Criar marcador FINAL com altura GARANTIDA
        const finalMarker = document.createElement('div');
        finalMarker.className = 'iframe-final-marker';
        finalMarker.id = 'final-content-marker';
        finalMarker.style.cssText = `
            height: ${neededHeight}px !important;
            min-height: 200px !important;
            width: 100% !important;
            background: linear-gradient(transparent, rgba(212, 130, 98, 0.2)) !important;
            border-top: 3px solid #d48262 !important;
            position: relative !important;
            margin-top: 50px !important;
            display: block !important;
        `;

        // Texto do marcador
        const markerText = document.createElement('div');
        markerText.className = 'final-marker-text';
        markerText.innerHTML = '🏁 FIM DO CONTEÚDO • BARRA DEVE ROLAR ATÉ AQUI 🏁';
        markerText.style.cssText = `
            position: absolute !important;
            top: 50% !important;
            left: 50% !important;
            transform: translate(-50%, -50%) !important;
            background: #d48262 !important;
            color: white !important;
            padding: 10px 25px !important;
            border-radius: 30px !important;
            font-weight: bold !important;
            font-size: 16px !important;
            box-shadow: 0 6px 20px rgba(212, 130, 98, 0.4) !important;
            white-space: nowrap !important;
        `;

        // Label informativo
        const infoLabel = document.createElement('div');
        infoLabel.innerHTML = `Altura garantida: ${neededHeight}px`;
        infoLabel.style.cssText = `
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(0,0,0,0.7);
            color: #00ff00;
            padding: 5px 10px;
            border-radius: 4px;
            font-family: monospace;
            font-size: 12px;
        `;

        finalMarker.appendChild(markerText);
        finalMarker.appendChild(infoLabel);
        document.body.appendChild(finalMarker);

        console.log(`✅ Marcador final adicionado com ${neededHeight}px garantidos`);
    }


    // ============================================
    // CONTROLE DE ALTURA
    // ============================================

    adjustContentHeight() {
        console.log('📈 Ajustando altura do conteúdo...');

        // Calcular altura REAL do conteúdo
        const bodyHeight = document.body.scrollHeight;
        const htmlHeight = document.documentElement.scrollHeight;
        const viewportHeight = window.innerHeight;

        const maxContentHeight = Math.max(bodyHeight, htmlHeight);
        const targetHeight = Math.max(maxContentHeight, viewportHeight + 300, this.minHeight);

        console.log('📊 Alturas calculadas:', {
            body: bodyHeight + 'px',
            html: htmlHeight + 'px',
            viewport: viewportHeight + 'px',
            max: maxContentHeight + 'px',
            target: targetHeight + 'px'
        });

        // Se o conteúdo for menor que o desejado, EXPANDIR
        if (maxContentHeight < targetHeight && !this.contentExpanded) {
            this.expandToHeight(targetHeight);
        }

        return targetHeight;
    }

    expandToHeight(targetHeight) {
        console.log(`⚡ Expandindo para ${targetHeight}px...`);

        // Calcular quanto expandir
        const currentHeight = Math.max(
            document.body.scrollHeight,
            document.documentElement.scrollHeight
        );

        const expandBy = targetHeight - currentHeight + 100; // +100px de margem

        if (expandBy > 0) {
            // Criar expansor
            const expander = document.createElement('div');
            expander.id = 'content-expander-guaranteed';
            expander.style.cssText = `
                height: ${expandBy}px;
                width: 100%;
                background: linear-gradient(
                    rgba(212, 130, 98, 0.05),
                    rgba(212, 130, 98, 0.1)
                );
                position: relative;
                margin-top: 20px;
                border-left: 4px solid #d48262;
            `;

            // Texto informativo
            const info = document.createElement('div');
            info.style.cssText = `
                position: absolute;
                top: 10px;
                right: 10px;
                background: #d48262;
                color: white;
                padding: 5px 10px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: bold;
            `;
            info.textContent = `+${expandBy}px garantidos`;
            expander.appendChild(info);

            // Adicionar ANTES do marcador final
            const finalMarker = document.getElementById('final-content-marker');
            if (finalMarker) {
                document.body.insertBefore(expander, finalMarker);
            } else {
                document.body.appendChild(expander);
            }

            this.contentExpanded = true;
            console.log(`✅ Expandido em ${expandBy}px`);
        }
    }

    // ============================================
    // COMUNICAÇÃO COM PARENT
    // ============================================

    setupParentCommandsListener() {
        window.addEventListener('message', (event) => {
            try {
                console.log('📨 Mensagem recebida do parent:', event.data);

                if (event.data && event.data.type === 'EXPAND_CONTENT') {
                    if (event.data.command === 'expandToFull') {
                        const minHeight = event.data.minHeight || 1200;
                        console.log(`🔄 Comando para expandir para ${minHeight}px`);
                        this.expandToHeight(minHeight);
                        this.reportHeightToParent();
                    }
                }

                if (event.data && event.data.type === 'GET_HEIGHT') {
                    this.reportHeightToParent();
                }

            } catch (e) {
                console.log('⚠️ Erro ao processar mensagem do parent');
            }
        });

        console.log('📡 Listener de comandos configurado');
    }

    reportHeightToParent() {
        try {
            const contentHeight = Math.max(
                document.body.scrollHeight,
                document.documentElement.scrollHeight
            );

            window.parent.postMessage({
                type: 'iframeContentHeight',
                height: contentHeight,
                url: window.location.href,
                timestamp: Date.now(),
                hasMarker: !!document.getElementById('final-content-marker'),
                expanded: this.contentExpanded
            }, '*');

            console.log(`📤 Altura reportada ao parent: ${contentHeight}px`);

            return contentHeight;
        } catch (e) {
            console.log('❌ Não foi possível reportar altura (cross-origin)');
            return 0;
        }
    }

    // ============================================
    // OBSERVERS E MONITORAMENTO
    // ============================================

    setupObservers() {
        // Observer para mudanças no DOM
        const domObserver = new MutationObserver(() => {
            setTimeout(() => {
                this.adjustContentHeight();
                this.reportHeightToParent();
            }, 150);
        });

        domObserver.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['style', 'class', 'id']
        });

        // Observer para mudanças de tamanho
        const resizeObserver = new ResizeObserver(() => {
            setTimeout(() => {
                this.adjustContentHeight();
                this.reportHeightToParent();
            }, 200);
        });

        resizeObserver.observe(document.body);
        if (document.documentElement) {
            resizeObserver.observe(document.documentElement);
        }

        // Observer para scroll (verificar se chegou ao final)
        window.addEventListener('scroll', () => {
            const scrolledToBottom =
                window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 50;

            if (scrolledToBottom) {
                console.log('🎯 Usuário rolou até o FINAL!');
                // Garantir que ainda temos espaço extra
                this.adjustContentHeight();
            }
        });

        console.log('👁️ Observadores configurados');
    }

    forceInitialCheck() {
        // Verificações múltiplas para garantir
        setTimeout(() => this.adjustContentHeight(), 300);
        setTimeout(() => this.adjustContentHeight(), 800);
        setTimeout(() => this.adjustContentHeight(), 1500);
        setTimeout(() => this.adjustContentHeight(), 3000);

        // Reportar altura periodicamente
        setInterval(() => this.reportHeightToParent(), 5000);
    }
}

// ============================================
// INICIALIZAÇÃO AUTOMÁTICA
// ============================================

// Verificar estado do documento
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        console.log('📄 DOM carregado - Iniciando fixer...');
        window.iframeContentFixer = new IframeContentFixer();
    });
} else {
    console.log('⚡ DOM já carregado - Iniciando fixer imediatamente...');
    window.iframeContentFixer = new IframeContentFixer();
}

// ============================================
// FUNÇÕES GLOBAIS PARA DEBUG E CONTROLE
// ============================================

// Expansão manual (útil para debug)
window.expandIframeContent = function (extraHeight = 300) {
    const currentHeight = Math.max(
        document.body.scrollHeight,
        document.documentElement.scrollHeight
    );

    const targetHeight = currentHeight + extraHeight;

    if (window.iframeContentFixer) {
        window.iframeContentFixer.expandToHeight(targetHeight);
        window.iframeContentFixer.reportHeightToParent();
    } else {
        console.error('IframeContentFixer não inicializado');
    }

    console.log(`🛠️ Expandido manualmente para ${targetHeight}px`);
    return targetHeight;
};

// Mostrar informações de debug
window.showIframeDebug = function () {
    console.group('🔧 DEBUG DO IFRAME INTERNO');
    console.log('Altura body:', document.body.scrollHeight + 'px');
    console.log('Altura html:', document.documentElement.scrollHeight + 'px');
    console.log('Viewport:', window.innerHeight + 'px');
    console.log('Scroll Y:', window.scrollY + 'px');
    console.log('Marcador final:', document.getElementById('final-content-marker'));
    console.log('Expansor:', document.getElementById('content-expander-guaranteed'));
    console.log('Fixer ativo:', !!window.iframeContentFixer);
    console.groupEnd();

    // Mostrar alerta visual
    const debugDiv = document.createElement('div');
    debugDiv.style.cssText = `
        position: fixed;
        top: 10px;
        left: 10px;
        background: rgba(0,0,0,0.8);
        color: #00ff00;
        padding: 10px;
        border-radius: 5px;
        font-family: monospace;
        font-size: 12px;
        z-index: 99999;
        max-width: 300px;
    `;
    debugDiv.innerHTML = `
        <strong>IFRAME DEBUG:</strong><br>
        Body: ${document.body.scrollHeight}px<br>
        HTML: ${document.documentElement.scrollHeight}px<br>
        Viewport: ${window.innerHeight}px<br>
        Scroll: ${window.scrollY}px<br>
        Marker: ${document.getElementById('final-content-marker') ? '✅' : '❌'}
    `;
    document.body.appendChild(debugDiv);

    setTimeout(() => debugDiv.remove(), 5000);

    return {
        bodyHeight: document.body.scrollHeight,
        htmlHeight: document.documentElement.scrollHeight,
        viewport: window.innerHeight
    };
};

// Função para rolar até o marcador final
window.scrollToFinalMarker = function () {
    const marker = document.getElementById('final-content-marker');
    if (marker) {
        marker.scrollIntoView({ behavior: 'smooth', block: 'end' });
        console.log('⬇ Rolando até o marcador final...');
        return true;
    }
    console.log('❌ Marcador final não encontrado');
    return false;
};

// ============================================
// FALLBACK EMERGÊNCIA
// ============================================

// Se por algum motivo não inicializar, forçar após timeout
setTimeout(() => {
    if (!window.iframeContentFixer && window.self !== window.top) {
        console.log('🚨 Fallback de emergência ativado!');
        window.iframeContentFixer = new IframeContentFixer();

        // Forçar estilos críticos
        const emergencyStyle = document.createElement('style');
        emergencyStyle.textContent = `
            html, body { min-height: 1200px !important; padding-bottom: 200px !important; }
            body::after { content: ''; display: block; height: 200px; background: rgba(212,130,98,0.1); }
        `;
        document.head.appendChild(emergencyStyle);
    }
}, 2000);