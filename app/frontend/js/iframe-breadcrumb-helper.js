// iframe-breadcrumb-helper.js
// Inclua este script em todas as páginas que serão carregadas no iframe

(function() {
    // Função para atualizar o breadcrumb do pai
    window.updateParentBreadcrumb = function(pageTitle, pathParts) {
        if (window.parent && window.parent !== window && window.parent.navigationSystem) {
            window.parent.navigationSystem.updateBreadcrumb(pageTitle, pathParts || []);
            
            // Também atualiza o título
            const titleElement = window.parent.document.getElementById('page-title');
            if (titleElement && pageTitle) {
                titleElement.textContent = pageTitle;
            }
        } else if (window.parent && window.parent !== window) {
            // Fallback usando postMessage
            window.parent.postMessage({
                type: 'breadcrumb',
                pageTitle: pageTitle,
                pathParts: pathParts || []
            }, '*');
        }
    };
    
    // Função para extrair informações da página atual
    function getPageInfo() {
        const currentPath = window.location.pathname;
        const pageName = currentPath.split('/').pop().replace('.html', '');
        
        // Tenta obter o título da página
        let pageTitle = document.querySelector('h1')?.textContent || 
                       document.title || 
                       pageName;
        
        // Extrai segments do path para o breadcrumb
        const pathParts = [];
        const pathSegments = currentPath.split('/').filter(seg => seg && !seg.includes('.html'));
        
        // Mapeamento de nomes de pastas para títulos amigáveis
        const folderNames = {
            'leads': 'Leads',
            'clients': 'Clientes',
            'chat': 'Chat',
            'financeiro': 'Financeiro',
            'marketing': 'Marketing',
            'operacoes': 'Operações',
            'treinamento_rh': 'Treinamento & RH',
            'relatorios': 'Relatórios',
            'executivo': 'Executivo'
        };
        
        pathSegments.forEach((segment) => {
            const friendlyName = folderNames[segment] || 
                                segment.charAt(0).toUpperCase() + segment.slice(1).replace('_', ' ');
            pathParts.push({ title: friendlyName });
        });
        
        return { pageTitle, pathParts };
    }
    
    // Atualiza breadcrumb quando a página carregar
    window.addEventListener('load', function() {
        const { pageTitle, pathParts } = getPageInfo();
        window.updateParentBreadcrumb(pageTitle, pathParts);
    });
    
    // Detecta navegação por pushState (SPAs)
    const originalPushState = history.pushState;
    history.pushState = function() {
        originalPushState.apply(this, arguments);
        setTimeout(() => {
            const { pageTitle, pathParts } = getPageInfo();
            window.updateParentBreadcrumb(pageTitle, pathParts);
        }, 100);
    };
    
    const originalReplaceState = history.replaceState;
    history.replaceState = function() {
        originalReplaceState.apply(this, arguments);
        setTimeout(() => {
            const { pageTitle, pathParts } = getPageInfo();
            window.updateParentBreadcrumb(pageTitle, pathParts);
        }, 100);
    };
    
    console.log('🍞 Iframe Breadcrumb Helper inicializado');
})();