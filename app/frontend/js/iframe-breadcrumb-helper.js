// iframe-breadcrumb-helper.js
// Inclua este script em todas as páginas que serão carregadas no iframe

(function() {
    // Função para atualizar o breadcrumb do pai
    window.updateParentBreadcrumb = function(pageTitle, pathParts) {
        if (window.parent && window.parent !== window) {
            window.parent.postMessage({
                type: 'breadcrumb',
                pageTitle: pageTitle,
                pathParts: pathParts || []
            }, '*');
        }
    };
    
    // Função para detectar navegação interna no iframe
    function setupBreadcrumbNavigation() {
        // Detecta cliques em links internos
        document.addEventListener('click', function(e) {
            let target = e.target.closest('a');
            if (target && target.href && target.href.includes(window.location.origin)) {
                const url = new URL(target.href);
                const path = url.pathname;
                const pageName = path.split('/').pop();
                
                // Se for navegação interna, atualiza o breadcrumb
                if (pageName && pageName.endsWith('.html')) {
                    e.preventDefault();
                    
                    // Atualiza o iframe
                    window.location.href = target.href;
                    
                    // Tenta atualizar o breadcrumb (será atualizado no onload)
                    setTimeout(() => {
                        window.updateParentBreadcrumb(
                            pageName.replace('.html', ''), 
                            [{ title: 'Módulo', action: "showAlert('Módulo')" }]
                        );
                    }, 100);
                }
            }
        });
        
        // Atualiza breadcrumb quando a página carregar
        window.addEventListener('load', function() {
            const currentPage = window.location.pathname.split('/').pop();
            let pageTitle = document.querySelector('h1')?.textContent || 
                           document.title || 
                           currentPage.replace('.html', '');
            
            // Extrai path da URL
            const pathParts = [];
            const pathSegments = window.location.pathname.split('/').filter(seg => seg && !seg.includes('.html'));
            
            pathSegments.forEach((segment, index) => {
                pathParts.push({
                    title: segment.charAt(0).toUpperCase() + segment.slice(1),
                    action: `console.log('Navigate to ${segment}')`
                });
            });
            
            window.updateParentBreadcrumb(pageTitle, pathParts);
        });
    }
    
    // Inicializa
    if (window.parent && window.parent !== window) {
        setupBreadcrumbNavigation();
    }
})();