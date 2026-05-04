        if (window.self !== window.top) {
            console.log('📦 Dashboard carregado em iframe');

            // Garantir altura suficiente
            document.addEventListener('DOMContentLoaded', function () {
                const bodyHeight = document.body.scrollHeight;
                const viewportHeight = window.innerHeight;

                console.log('📏 Alturas:', {
                    body: bodyHeight + 'px',
                    viewport: viewportHeight + 'px'
                });

                // Se necessário, expandir mais
                if (bodyHeight < viewportHeight + 300) {
                    const scrollArea = document.querySelector('.scroll-end-area');

                    if (scrollArea) {
                        scrollArea.style.height = (viewportHeight + 400 - bodyHeight) + 'px';
                        console.log('⚡ Área de scroll ajustada');
                    }
                }

                // Informar ao parent que carregamos
                setTimeout(() => {
                    try {
                        window.parent.postMessage({
                            type: 'iframeLoaded',
                            page: 'dashboard.html',
                            height: document.body.scrollHeight
                        }

                            , '*');
                    }

                    catch (e) {
                        // Ignorar cross-origin
                    }
                }

                    , 500);
            });
        }

