// HealthPlatform - Dashboard Controller
// Arquivo: /app/frontend/js/dashboard.js
// Responsável pelo dashboard principal

// ============================================
// CONFIGURAÇÕES DO DASHBOARD
// ============================================
const DASHBOARD_CONFIG = {
    refreshInterval: 30000, // 30 segundos
    apiEndpoints: {
        basic: '/api/v1/crm/dashboard/completo',
        advanced: '/api/v1/crm/dashboard/avancado',
        leads: '/api/v1/crm/leads',
        comissoes: '/api/v1/finance/comissoes'
    },
    chartColors: {
        primary: '#d48262',
        secondary: '#3b82f6',
        success: '#10b981',
        warning: '#f59e0b',
        danger: '#ef4444',
        info: '#8b5cf6'
    }
};

// Estado do dashboard
let dashboardState = {
    isLoading: true,
    lastUpdate: null,
    data: null,
    charts: {}
};

// ============================================
// INICIALIZAÇÃO
// ============================================

/**
 * Inicializa o dashboard
 */
function initializeDashboard() {
    console.log('📊 Dashboard - Inicializando...');

    // Notificar o parent que carregou
    notifyParentLoaded();

    // Verificar se está em iframe
    if (window.self !== window.top) {
        console.log('📦 Dashboard carregado em iframe');
        setupIframeCommunication();
    }

    // Carregar dados
    loadDashboardData();

    // Configurar auto-refresh
    setupAutoRefresh();

    // Configurar eventos
    setupDashboardEvents();
}

/**
 * Notifica o parent que o dashboard carregou
 */
function notifyParentLoaded() {
    try {
        if (window.parent !== window.self) {
            window.parent.postMessage({
                type: 'dashboard-loaded',
                status: 'success',
                timestamp: new Date().toISOString()
            }, '*');
        }
    } catch (e) {
        // Ignorar erros de cross-origin
    }
}

/**
 * Configura comunicação com parent (se estiver em iframe)
 */
function setupIframeCommunication() {
    window.addEventListener('message', function (event) {
        if (event.data && event.data.type === 'parent-loaded') {
            console.log('📩 Parent carregou, ajustando dashboard...');
            adjustDashboardForIframe();
        }
    });
}

/**
 * Ajusta o dashboard para visualização em iframe
 */
function adjustDashboardForIframe() {
    // Ajustar estilos para iframe
    document.body.style.padding = '20px';
    document.body.style.minHeight = '600px';

    // Remover cabeçalhos duplicados se existirem
    const duplicateHeaders = document.querySelectorAll('header, nav');
    duplicateHeaders.forEach(header => {
        if (!header.classList.contains('dashboard-header')) {
            header.style.display = 'none';
        }
    });
}

// ============================================
// CARREGAMENTO DE DADOS
// ============================================

/**
 * Carrega todos os dados do dashboard
 */
async function loadDashboardData() {
    console.log('🔄 Carregando dados do dashboard...');

    dashboardState.isLoading = true;
    showLoading(true);

    try {
        // Carregar dados básicos e avançados em paralelo
        const [basicData, advancedData] = await Promise.all([
            fetchDashboardData('basic'),
            fetchDashboardData('advanced')
        ]);

        // Processar e combinar dados
        dashboardState.data = {
            ...basicData,
            ...advancedData,
            timestamp: new Date().toISOString()
        };

        dashboardState.lastUpdate = new Date();

        // Atualizar UI
        updateDashboardUI();

        console.log('✅ Dashboard atualizado com sucesso');

    } catch (error) {
        console.error('❌ Erro ao carregar dados:', error);
        showError('Não foi possível carregar os dados do dashboard');
        useFallbackData();
    } finally {
        dashboardState.isLoading = false;
        showLoading(false);
    }
}

/**
 * Busca dados da API
 */
async function fetchDashboardData(type) {
    const endpoint = DASHBOARD_CONFIG.apiEndpoints[type];

    if (!endpoint) {
        throw new Error(`Tipo de dados inválido: ${type}`);
    }

    console.log(`🔍 Buscando dados (${type}): ${endpoint}`);

    const response = await fetch(endpoint);

    if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const result = await response.json();

    if (!result.success) {
        throw new Error(result.error || 'Erro na resposta da API');
    }

    return result.data;
}

// ============================================
// ATUALIZAÇÃO DA UI
// ============================================

/**
 * Atualiza toda a UI do dashboard
 */
function updateDashboardUI() {
    if (!dashboardState.data) return;

    console.log('🎨 Atualizando UI do dashboard...');

    // 1. Atualizar KPI Cards
    updateKPICards();

    // 2. Atualizar gráficos
    updateCharts();

    // 3. Atualizar tabelas
    updateTables();

    // 4. Atualizar atividades recentes
    updateRecentActivities();

    // 5. Atualizar timestamp
    updateLastUpdateTime();
}

/**
 * Atualiza os cards KPI
 */
function updateKPICards() {
    const data = dashboardState.data;

    if (!data || !data.metricas_principais) {
        console.warn('⚠️ Dados KPI não disponíveis');
        return;
    }

    const metricas = data.metricas_principais;

    // Formatar valores
    const formatCurrency = (value) => {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL',
            minimumFractionDigits: 2
        }).format(value || 0);
    };

    const formatNumber = (value) => {
        return new Intl.NumberFormat('pt-BR').format(value || 0);
    };

    // Atualizar cada KPI (usando IDs que devem existir no HTML)
    const kpiUpdates = {
        'kpi-faturamento': formatCurrency(metricas.faturamento_total),
        'kpi-leads': formatNumber(metricas.leads_novos),
        'kpi-conversao': `${(metricas.taxa_conversao || 0).toFixed(1)}%`,
        'kpi-clientes': formatNumber(metricas.clientes_ativos),
        'kpi-vendas': formatNumber(metricas.vendas_mes_atual),
        'kpi-meta': `${metricas.progresso_meta || 0}%`
    };

    Object.entries(kpiUpdates).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;

            // Adicionar animação
            element.classList.add('kpi-updated');
            setTimeout(() => element.classList.remove('kpi-updated'), 500);
        }
    });

    // Atualizar barra de progresso da meta
    const progressBar = document.getElementById('meta-progress-bar');
    const progressText = document.getElementById('meta-progress-text');

    if (progressBar && metricas.progresso_meta) {
        progressBar.style.width = `${metricas.progresso_meta}%`;
        progressBar.setAttribute('aria-valuenow', metricas.progresso_meta);

        // Mudar cor baseada no progresso
        if (metricas.progresso_meta >= 100) {
            progressBar.classList.remove('bg-warning');
            progressBar.classList.add('bg-success');
        } else if (metricas.progresso_meta >= 70) {
            progressBar.classList.remove('bg-primary');
            progressBar.classList.add('bg-warning');
        } else {
            progressBar.classList.remove('bg-warning', 'bg-success');
            progressBar.classList.add('bg-primary');
        }
    }

    if (progressText && metricas.progresso_meta) {
        progressText.textContent = `${metricas.progresso_meta}%`;
    }
}

/**
 * Atualiza todos os gráficos
 */
function updateCharts() {
    const data = dashboardState.data;

    if (!data) {
        console.warn('⚠️ Dados para gráficos não disponíveis');
        return;
    }

    // 1. Gráfico de evolução mensal
    if (data.evolucao_mensal && data.evolucao_mensal.length > 0) {
        renderEvolucaoChart(data.evolucao_mensal);
    }

    // 2. Gráfico de distribuição de leads
    if (data.distribuicao_leads && data.distribuicao_leads.length > 0) {
        renderDistribuicaoChart(data.distribuicao_leads);
    }

    // 3. Gráfico de status de leads
    if (data.leads_por_status_detalhado && data.leads_por_status_detalhado.length > 0) {
        renderStatusLeadsChart(data.leads_por_status_detalhado);
    }
}

/**
 * Renderiza gráfico de evolução
 */
function renderEvolucaoChart(dados) {
    const canvas = document.getElementById('chart-evolucao');
    if (!canvas) {
        console.error('❌ Canvas chart-evolucao não encontrado');
        return;
    }

    // Destruir gráfico anterior se existir
    if (dashboardState.charts.evolucao) {
        dashboardState.charts.evolucao.destroy();
    }

    const ctx = canvas.getContext('2d');

    // Preparar dados
    const labels = dados.map(item => item.mes || `Mês ${dados.indexOf(item) + 1}`);
    const vendas = dados.map(item => item.vendas || 0);
    const leads = dados.map(item => item.leads || 0);
    const faturamento = dados.map(item => item.faturamento || 0);

    dashboardState.charts.evolucao = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Vendas',
                    data: vendas,
                    borderColor: DASHBOARD_CONFIG.chartColors.primary,
                    backgroundColor: hexToRgba(DASHBOARD_CONFIG.chartColors.primary, 0.1),
                    borderWidth: 3,
                    tension: 0.4,
                    fill: true,
                    yAxisID: 'y'
                },
                {
                    label: 'Leads',
                    data: leads,
                    borderColor: DASHBOARD_CONFIG.chartColors.secondary,
                    backgroundColor: hexToRgba(DASHBOARD_CONFIG.chartColors.secondary, 0.1),
                    borderWidth: 3,
                    tension: 0.4,
                    fill: true,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            scales: {
                x: {
                    grid: {
                        display: true
                    }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Vendas'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Leads'
                    },
                    grid: {
                        drawOnChartArea: false
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                if (context.dataset.label === 'Faturamento') {
                                    label += new Intl.NumberFormat('pt-BR', {
                                        style: 'currency',
                                        currency: 'BRL'
                                    }).format(context.parsed.y);
                                } else {
                                    label += context.parsed.y;
                                }
                            }
                            return label;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Renderiza gráfico de distribuição
 */
function renderDistribuicaoChart(dados) {
    const canvas = document.getElementById('chart-distribuicao');
    if (!canvas) {
        console.error('❌ Canvas chart-distribuicao não encontrado');
        return;
    }

    if (dashboardState.charts.distribuicao) {
        dashboardState.charts.distribuicao.destroy();
    }

    const ctx = canvas.getContext('2d');

    const labels = dados.map(item => item.origem);
    const valores = dados.map(item => item.quantidade || item.percentual || 0);
    const cores = [
        DASHBOARD_CONFIG.chartColors.primary,
        DASHBOARD_CONFIG.chartColors.secondary,
        DASHBOARD_CONFIG.chartColors.success,
        DASHBOARD_CONFIG.chartColors.warning,
        DASHBOARD_CONFIG.chartColors.info
    ];

    dashboardState.charts.distribuicao = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: valores,
                backgroundColor: cores,
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Renderiza gráfico de status de leads
 */
function renderStatusLeadsChart(dados) {
    const canvas = document.getElementById('chart-status-leads');
    if (!canvas) return;

    if (dashboardState.charts.statusLeads) {
        dashboardState.charts.statusLeads.destroy();
    }

    const ctx = canvas.getContext('2d');

    const labels = dados.map(item => item.status);
    const valores = dados.map(item => item.quantidade || 0);
    const cores = dados.map(item => item.cor || DASHBOARD_CONFIG.chartColors.primary);

    dashboardState.charts.statusLeads = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Leads por Status',
                data: valores,
                backgroundColor: cores,
                borderColor: cores.map(color => darkenColor(color, 20)),
                borderWidth: 1,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Quantidade'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Status'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// ============================================
// ATUALIZAÇÃO DE TABELAS
// ============================================

/**
 * Atualiza tabelas do dashboard
 */
function updateTables() {
    const data = dashboardState.data;

    // 1. Tabela de performance de corretores
    if (data.performance_corretores) {
        updatePerformanceTable(data.performance_corretores);
    }

    // 2. Tabela de top corretores
    if (data.top_corretores) {
        updateTopCorretoresTable(data.top_corretores);
    }
}

/**
 * Atualiza tabela de performance
 */
function updatePerformanceTable(corretores) {
    const container = document.getElementById('performance-corretores');
    if (!container) return;

    if (corretores.length === 0) {
        container.innerHTML = `
            <div class="text-center py-8 text-gray-500">
                <p>Nenhum dado de corretor disponível.</p>
            </div>
        `;
        return;
    }

    let html = `
        <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                    <tr>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Corretor</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Vendas</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Meta</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Atingimento</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Comissão</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ações</th>
                    </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
    `;

    corretores.forEach((corretor, index) => {
        const nome = corretor.nome || `Corretor ${index + 1}`;
        const vendas = corretor.vendas || 0;
        const meta = corretor.meta || 10;
        const comissao = corretor.comissao || 0;
        const leads = corretor.leads || 0;
        const conversao = corretor.conversao || 0;
        const atingimento = meta > 0 ? Math.round((vendas / meta) * 100) : 0;

        // Status e cores
        let statusClass = 'bg-red-100 text-red-800';
        let statusIcon = '🔴';

        if (atingimento >= 100) {
            statusClass = 'bg-green-100 text-green-800';
            statusIcon = '✅';
        } else if (atingimento >= 80) {
            statusClass = 'bg-yellow-100 text-yellow-800';
            statusIcon = '⚠️';
        }

        html += `
            <tr class="hover:bg-gray-50 transition-colors">
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                        <div class="flex-shrink-0 h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                            <span class="text-blue-600 font-bold">${nome.charAt(0)}</span>
                        </div>
                        <div class="ml-4">
                            <div class="text-sm font-medium text-gray-900">${nome}</div>
                            <div class="text-sm text-gray-500">${leads} leads • ${conversao}% conversão</div>
                        </div>
                    </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-lg font-bold text-gray-900">${vendas}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-gray-500">${meta}</td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-3 py-1 inline-flex text-sm font-semibold rounded-full ${statusClass}">
                        ${statusIcon} ${atingimento}%
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-lg font-bold text-gray-900">
                        R$ ${comissao.toFixed(2).replace('.', ',')}
                    </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button onclick="viewCorretorDetails(${index})" 
                            class="text-primary hover:text-primary-dark mr-3">
                        👁️ Detalhes
                    </button>
                    <button onclick="contactCorretor('${nome}')"
                            class="text-green-600 hover:text-green-800">
                        💬 Contatar
                    </button>
                </td>
            </tr>
        `;
    });

    html += `
                </tbody>
            </table>
        </div>
    `;

    container.innerHTML = html;
}

// ============================================
// FUNÇÕES AUXILIARES
// ============================================

/**
 * Mostra loading
 */
function showLoading(show) {
    const loading = document.getElementById('loading');
    if (loading) {
        loading.style.display = show ? 'flex' : 'none';
    }
}

/**
 * Mostra erro
 */
function showError(message) {
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.classList.remove('hidden');

        setTimeout(() => {
            errorDiv.classList.add('hidden');
        }, 5000);
    } else {
        alert(`Erro no dashboard: ${message}`);
    }
}

/**
 * Usa dados de fallback
 */
function useFallbackData() {
    console.log('🔄 Usando dados de fallback');

    dashboardState.data = {
        metricas_principais: {
            faturamento_total: 189000,
            leads_novos: 65,
            taxa_conversao: 35.4,
            clientes_ativos: 42,
            vendas_mes_atual: 25,
            meta_mensal: 50,
            progresso_meta: 84
        },
        performance_corretores: [
            { nome: "João Silva", vendas: 15, meta: 12, comissao: 2250, leads: 45, conversao: 33.3 },
            { nome: "Maria Santos", vendas: 12, meta: 12, comissao: 1800, leads: 38, conversao: 31.6 }
        ],
        evolucao_mensal: [
            { mes: "Jan", vendas: 12, leads: 40, faturamento: 18000 },
            { mes: "Fev", vendas: 15, leads: 45, faturamento: 22500 },
            { mes: "Mar", vendas: 18, leads: 50, faturamento: 27000 }
        ],
        distribuicao_leads: [
            { origem: "Site", quantidade: 120 },
            { origem: "Indicação", quantidade: 85 },
            { origem: "WhatsApp", quantidade: 65 }
        ]
    };

    updateDashboardUI();
}

/**
 * Atualiza timestamp da última atualização
 */
function updateLastUpdateTime() {
    const element = document.getElementById('last-update-time');
    if (element && dashboardState.lastUpdate) {
        const timeString = dashboardState.lastUpdate.toLocaleTimeString('pt-BR');
        element.textContent = `Atualizado: ${timeString}`;
    }
}

/**
 * Configura auto-refresh
 */
function setupAutoRefresh() {
    setInterval(() => {
        if (!dashboardState.isLoading) {
            loadDashboardData();
        }
    }, DASHBOARD_CONFIG.refreshInterval);
}

/**
 * Configura eventos do dashboard
 */
function setupDashboardEvents() {
    // Botão de refresh manual
    const refreshBtn = document.getElementById('refresh-dashboard');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', loadDashboardData);
    }

    // Exportar dados
    const exportBtn = document.getElementById('export-dashboard');
    if (exportBtn) {
        exportBtn.addEventListener('click', exportDashboardData);
    }
}

/**
 * Exporta dados do dashboard
 */
function exportDashboardData() {
    if (!dashboardState.data) {
        showError('Nenhum dado para exportar');
        return;
    }

    const dataStr = JSON.stringify(dashboardState.data, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);

    const exportFileDefaultName = `dashboard-${new Date().toISOString().split('T')[0]}.json`;

    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();

    console.log('📤 Dashboard exportado');
}

// ============================================
// FUNÇÕES UTILITÁRIAS
// ============================================

function hexToRgba(hex, alpha = 1) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);

    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

function darkenColor(color, percent) {
    const num = parseInt(color.replace("#", ""), 16);
    const amt = Math.round(2.55 * percent);
    const R = (num >> 16) - amt;
    const G = (num >> 8 & 0x00FF) - amt;
    const B = (num & 0x0000FF) - amt;

    return "#" + (
        0x1000000 +
        (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 +
        (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 +
        (B < 255 ? B < 1 ? 0 : B : 255)
    ).toString(16).slice(1);
}

// ============================================
// INICIALIZAÇÃO
// ============================================

// Inicializar quando o DOM carregar
document.addEventListener('DOMContentLoaded', initializeDashboard);

// Exportar funções para uso no HTML
window.loadDashboardData = loadDashboardData;
window.exportDashboardData = exportDashboardData;
window.viewCorretorDetails = function (index) {
    alert(`Detalhes do corretor ${index + 1}`);
};
window.contactCorretor = function (nome) {
    alert(`Contatar ${nome}`);
};