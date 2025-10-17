// Analytics JavaScript

let financialChart = null;
let popularItemsChart = null;

document.addEventListener('DOMContentLoaded', function() {
    initializeAnalyticsHandlers();
});

function initializeAnalyticsHandlers() {
    // Generate analytics on page load
    generateAnalytics();

    // Generate analytics button
    const generateAnalyticsBtn = document.getElementById('generateAnalytics');
    if (generateAnalyticsBtn) {
        generateAnalyticsBtn.addEventListener('click', generateAnalytics);
    }
}

async function generateAnalytics() {
    const button = document.getElementById('generateAnalytics');
    const originalText = button ? button.innerHTML : null;
    
    if (button) {
        showLoading(button);
    }
    
    try {
        const analytics = await apiCall('/api/analytics');
        displayAnalytics(analytics);
        createCharts(analytics);
    } catch (error) {
        // Error handling is done in apiCall
    } finally {
        if (button) {
            hideLoading(button, originalText);
        }
    }
}

function displayAnalytics(analytics) {
    const resultsDiv = document.getElementById('analyticsResults');
    
    const { statistics, financials, popular_items } = analytics;
    
    let html = `
        <div class="row">
            <div class="col-md-6">
                <h5>Статистика</h5>
                <div class="list-group">
                    <div class="list-group-item d-flex justify-content-between align-items-center">
                        Всего товаров в системе
                        <span class="badge bg-primary rounded-pill">${statistics.total_items}</span>
                    </div>
                    <div class="list-group-item d-flex justify-content-between align-items-center">
                        Всего продаж
                        <span class="badge bg-success rounded-pill">${statistics.total_sales}</span>
                    </div>
                    <div class="list-group-item d-flex justify-content-between align-items-center">
                        Количество поставщиков
                        <span class="badge bg-info rounded-pill">${statistics.total_suppliers}</span>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <h5>Финансовые показатели</h5>
                <div class="list-group">
                    <div class="list-group-item d-flex justify-content-between align-items-center">
                        Общая выручка
                        <span class="badge bg-success rounded-pill">${formatCurrency(financials.revenue)}</span>
                    </div>
                    <div class="list-group-item d-flex justify-content-between align-items-center">
                        Себестоимость
                        <span class="badge bg-warning rounded-pill">${formatCurrency(financials.cost)}</span>
                    </div>
                    <div class="list-group-item d-flex justify-content-between align-items-center">
                        Прибыль
                        <span class="badge bg-primary rounded-pill">${formatCurrency(financials.profit)}</span>
                    </div>
                    <div class="list-group-item d-flex justify-content-between align-items-center">
                        Маржа прибыли
                        <span class="badge bg-info rounded-pill">${financials.profit_margin}%</span>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-12">
                <h5>Популярные товары</h5>
                <div class="table-responsive">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>Товар</th>
                                <th>Количество продаж</th>
                            </tr>
                        </thead>
                        <tbody>
    `;
    
    if (popular_items && popular_items.length > 0) {
        popular_items.forEach(item => {
            html += `
                <tr>
                    <td>${item.product}</td>
                    <td>${item.total_sold} шт.</td>
                </tr>
            `;
        });
    } else {
        html += `
            <tr>
                <td colspan="2" class="text-center text-muted">Нет данных о популярных товарах</td>
            </tr>
        `;
    }
    
    html += `
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <div class="mt-3">
            <small class="text-muted">Дата формирования: ${analytics.report_date}</small>
        </div>
    `;
    
    resultsDiv.innerHTML = html;
}

function createCharts(analytics) {
    const { financials, popular_items } = analytics;
    
    // Destroy existing charts if they exist
    if (financialChart) {
        financialChart.destroy();
    }
    if (popularItemsChart) {
        popularItemsChart.destroy();
    }
    
    // Financial Chart
    const financialCtx = document.getElementById('financialChart');
    if (financialCtx) {
        financialChart = new Chart(financialCtx, {
            type: 'bar',
            data: {
                labels: ['Выручка', 'Себестоимость', 'Прибыль'],
                datasets: [{
                    label: 'Сумма (руб.)',
                    data: [financials.revenue, financials.cost, financials.profit],
                    backgroundColor: [
                        'rgba(40, 167, 69, 0.8)',
                        'rgba(255, 193, 7, 0.8)',
                        'rgba(0, 123, 255, 0.8)'
                    ],
                    borderColor: [
                        'rgb(40, 167, 69)',
                        'rgb(255, 193, 7)',
                        'rgb(0, 123, 255)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Финансовые показатели'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value.toLocaleString('ru-RU') + ' руб.';
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Popular Items Chart
    const popularCtx = document.getElementById('popularItemsChart');
    if (popularCtx && popular_items && popular_items.length > 0) {
        popularItemsChart = new Chart(popularCtx, {
            type: 'pie',
            data: {
                labels: popular_items.map(item => item.product),
                datasets: [{
                    data: popular_items.map(item => item.total_sold),
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.8)',
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(255, 206, 86, 0.8)',
                        'rgba(75, 192, 192, 0.8)',
                        'rgba(153, 102, 255, 0.8)'
                    ],
                    borderColor: [
                        'rgb(255, 99, 132)',
                        'rgb(54, 162, 235)',
                        'rgb(255, 206, 86)',
                        'rgb(75, 192, 192)',
                        'rgb(153, 102, 255)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    title: {
                        display: true,
                        text: 'Популярные товары'
                    }
                }
            }
        });
    }
}

// Initialize when page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeAnalyticsHandlers);
} else {
    initializeAnalyticsHandlers();
}