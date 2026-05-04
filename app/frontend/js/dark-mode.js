        // Gerenciamento do Dark Mode
        (function() {
            // Inicializar tema do localStorage
            const savedTheme = localStorage.getItem('theme');
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            const initialTheme = savedTheme || (prefersDark ? 'dark' : 'light');
            
            // Aplicar tema no HTML
            document.documentElement.classList.add(initialTheme);
            if (initialTheme === 'dark') {
                document.documentElement.classList.remove('light');
            } else {
                document.documentElement.classList.add('light');
            }
            
            // Variável global para controlar o tema
            window.currentTheme = initialTheme;
        })();
