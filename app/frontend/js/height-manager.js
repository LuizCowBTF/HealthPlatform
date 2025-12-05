// ============================================
// HEIGHT MANAGER - CONTROLE DE ALTURA
// ============================================

console.log('📏 Height Manager - Ativado');

class HeightManager {
    constructor() {
        this.container = document.getElementById('content-container');
        this.header = document.querySelector('.health-header');

        if (this.container) {
            this.init();
        }
    }

    init() {
        console.log('🔄 Configurando altura...');

        // Calcular e aplicar altura inicial
        this.calculateAndSetHeight();

        // Listener para redimensionamento
        window.addEventListener('resize', () => {
            setTimeout(() => this.calculateAndSetHeight(), 100);
        });

        // Verificação periódica
        setInterval(() => this.calculateAndSetHeight(), 3000);

        console.log('✅ Height Manager configurado');
    }

    calculateAndSetHeight() {
        if (!this.container) return;

        // Altura da janela
        const windowHeight = window.innerHeight;

        // Altura do header
        const headerHeight = this.header ? this.header.offsetHeight : 0;

        // Margens (1rem top + 1rem bottom = 32px)
        const margins = 32;

        // Altura disponível
        const availableHeight = windowHeight - headerHeight - margins;

        // Altura mínima garantida
        const minHeight = 600;
        const finalHeight = Math.max(availableHeight, minHeight);

        // Aplicar altura
        this.container.style.height = `${finalHeight}px`;

        return finalHeight;
    }
}

// ============================================
// INICIALIZAÇÃO
// ============================================

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.heightManager = new HeightManager();
    });
} else {
    window.heightManager = new HeightManager();
}