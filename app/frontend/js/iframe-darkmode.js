// Adicione este script no final do body de cada página que vai dentro do iframe
<script>
(function() {
    // Função para aplicar o tema no iframe
    function applyTheme(theme) {
        const htmlElement = document.documentElement;
        
        if (theme === 'dark') {
            htmlElement.classList.add('dark');
            htmlElement.classList.remove('light');
            
            // Se estiver usando Tailwind, adicione isso também
            document.body.classList.add('dark');
            document.body.classList.remove('light');
        } else {
            htmlElement.classList.add('light');
            htmlElement.classList.remove('dark');
            
            document.body.classList.add('light');
            document.body.classList.remove('dark');
        }
        
        // Se você tiver variáveis CSS personalizadas, atualize-as aqui
        document.documentElement.style.setProperty('color-scheme', theme);
    }
    
    // Solicitar o tema atual ao pai
    window.parent.postMessage({ type: 'getTheme' }, '*');
    
    // Escutar mudanças de tema
    window.addEventListener('message', function(event) {
        if (event.data && event.data.type === 'themeChange') {
            applyTheme(event.data.theme);
        }
    });
    
    // Verificar se já temos um tema salvo
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        applyTheme(savedTheme);
    } else {
        // Verificar preferência do sistema
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        applyTheme(prefersDark ? 'dark' : 'light');
    }
})();
</script>