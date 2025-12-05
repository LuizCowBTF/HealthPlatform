// ============================================
// IFRAME SCROLL FIX - GARANTE BARRA DE ROLAGEM VISÍVEL
// ============================================

console.log('🔧 Iframe Scroll Fix - Ativado');

// Verificar se estamos dentro de um iframe
if (window.self !== window.top) {
    console.log('📦 Detectado dentro de iframe - Aplicando fix de scroll...');

    // Função para garantir altura mínima
    function guaranteeMinimumHeight() {
        const viewportHeight = window.innerHeight;
        const bodyHeight = document.body.scrollHeight;
        const htmlHeight = document.documentElement.scrollHeight;

        console.log('📏 Medições:', {
            viewport: viewportHeight + 'px',
            body: bodyHeight + 'px',
            html: htmlHeight + 'px'
        });

        // Altura mínima necessária para scroll (viewport + 500px)
        const minRequiredHeight = viewportHeight + 500;
        const currentMaxHeight = Math.max(bodyHeight, htmlHeight);

        if (currentMaxHeight < minRequiredHeight) {
            console.log(`⚠️ Conteúdo muito curto! Expandindo de ${currentMaxHeight}px para ${minRequiredHeight}px`);

            // Criar div expansora
            const expander = document.createElement('div');
            expander.id = 'scroll-guarantee-expander';
            expander.style.cssText = `
                height: ${minRequiredHeight - currentMaxHeight + 200}px;
                width: 100%;
                background: linear-gradient(
                    rgba(212, 130, 98, 0.05),
                    rgba(212, 130, 98, 0.15)
                );
                position: relative;
                margin-top: 50px;
                border-left: 4px solid #d48262;
                border-radius: 0 0 8px 8px;
            `;

            // Adicionar label informativo
            const label = document.createElement('div');
            label.innerHTML = `SCROLL GARANTIDO (+${minRequiredHeight - currentMaxHeight + 200}px)`;
            label.style.cssText = `
                position: absolute;
                top: 10px;
                right: 10px;
                background: #d48262;
                color: white;
                padding: 5px 12px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: bold;
                font-family: monospace;
            `;

            expander.appendChild(label);
            document.body.appendChild(expander);

            console.log('✅ Expansor adicionado para garantir scroll');
        } else {
            console.log('✅ Altura suficiente para scroll');
        }
    }

    // Função para forçar barra de rolagem sempre visível
    function forceScrollbarVisible() {
        // CSS CRÍTICO - Garantir que o body tenha scroll
        const style = document.createElement('style');
        style.id = 'scrollbar-force-style';
        style.textContent = `
            /* =========================================== */
            /* GARANTIA ABSOLUTA DE SCROLL */
            /* =========================================== */
            
            html, body {
                min-height: 1200px !important;
                height: auto !important;
                overflow-y: auto !important;
                overflow-x: hidden !important;
                margin: 0 !important;
                padding: 0 !important;
                padding-bottom: 200px !important;
            }
            
            /* Container principal expansível */
            .max-w-7xl, .container, .mx-auto {
                min-height: 1100px !important;
                max-height: none !important;
                padding-bottom: 150px !important;
            }
            
            /* Forçar barra de rolagem */
            body::-webkit-scrollbar {
                width: 16px !important;
                display: block !important;
            }
            
            body::-webkit-scrollbar-track {
                background: #f1f1f1 !important;
                border-radius: 10px !important;
                margin: 4px !important;
            }
            
            body::-webkit-scrollbar-thumb {
                background: #d48262 !important;
                border-radius: 10px !important;
                border: 3px solid #f1f1f1 !important;
            }
            
            /* Firefox */
            html {
                scrollbar-width: auto !important;
                scrollbar-color: #d48262 #f1f1f1 !important;
            }
            
            /* Espaço final VISÍVEL */

            #scroll-end-marker {
                height: 200px !important;
                width: 100% !important;
                background: linear-gradient(
                    transparent,
                    rgba(212, 130, 98, 0.3)
                ) !important;
                border-top: 3px solid #d48262 !important;
                margin-top: 50px !important;
                position: relative !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
            }
          
            .scroll-marker-text {
                background: #d48262 !important;
                color: white !important;
                padding: 12px 30px !important;
                border-radius: 30px !important;
                font-weight: bold !important;
                font-size: 16px !important;
                box-shadow: 0 6px 20px rgba(212, 130, 98, 0.4) !important;
            }
        `;

        document.head.appendChild(style);
        console.log('🎨 Estilos de scroll forçados aplicados');
    }

    // Função para adicionar marcador final VISÍVEL
    function addVisibleEndMarker() {
        // Remover marcador antigo se existir
        const oldMarker = document.getElementById('scroll-end-marker');
        if (oldMarker) oldMarker.remove();

        // Criar marcador
        const marker = document.createElement('div');
        marker.id = 'scroll-end-marker';

        const markerText = document.createElement('div');
        markerText.className = 'scroll-marker-text';
        markerText.innerHTML = '🏁 FIM • BARRA DEVE ROLAR ATÉ AQUI 🏁';

        marker.appendChild(markerText);
        document.body.appendChild(marker);

        console.log('🎯 Marcador final VISÍVEL adicionado');
    }

    // Inicializar quando o DOM estiver pronto
    document.addEventListener('DOMContentLoaded', function () {
        console.log('📄 DOM carregado - Aplicando fixes...');

        // 1. Forçar barra visível
        forceScrollbarVisible();

        // 2. Adicionar marcador final
        addVisibleEndMarker();

        // 3. Garantir altura mínima
        setTimeout(guaranteeMinimumHeight, 300);

        // 4. Recalcular após imagens/carregamentos
        setTimeout(guaranteeMinimumHeight, 1000);
        setTimeout(guaranteeMinimumHeight, 2000);

        // 5. Informar ao parent que ajustamos a altura
        setTimeout(() => {
            try {
                window.parent.postMessage({
                    type: 'iframeHeightAdjusted',
                    height: document.body.scrollHeight,
                    hasScroll: true,
                    timestamp: Date.now()
                }, '*');
                console.log('📤 Informando altura ajustada ao parent');
            } catch (e) {
                console.log('⚠️ Não foi possível comunicar com parent');
            }
        }, 1500);
    });

    // Fallback se DOM já carregado
    if (document.readyState !== 'loading') {
        setTimeout(() => {
            forceScrollbarVisible();
            addVisibleEndMarker();
            guaranteeMinimumHeight();
        }, 100);
    }

    // Escutar mensagens do parent
    window.addEventListener('message', function (event) {
        if (event.data && event.data.type === 'checkScroll') {
            console.log('🔍 Parent solicitando verificação de scroll');
            guaranteeMinimumHeight();
        }
    });

    console.log('✅ Iframe Scroll Fix configurado');
} else {
    console.log('🌍 Não está em iframe - Scroll Fix ignorado');
}