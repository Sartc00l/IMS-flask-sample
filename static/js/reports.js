// Reports JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeReportsHandlers();
});

function initializeReportsHandlers() {
    // Set default dates for sales report
    setDefaultDates();
    
    // Generate inventory report
    const generateInventoryReport = document.getElementById('generateInventoryReport');
    if (generateInventoryReport) {
        generateInventoryReport.addEventListener('click', generateInventoryReportHandler);
    }

    // Generate sales report
    const generateSalesReport = document.getElementById('generateSalesReport');
    if (generateSalesReport) {
        generateSalesReport.addEventListener('click', generateSalesReportHandler);
    }

    // Generate quarterly report
    const generateQuarterlyReport = document.getElementById('generateQuarterlyReport');
    if (generateQuarterlyReport) {
        generateQuarterlyReport.addEventListener('click', generateQuarterlyReportHandler);
    }
}

function setDefaultDates() {
    const startDate = document.getElementById('startDate');
    const endDate = document.getElementById('endDate');
    
    if (startDate && endDate) {
        const today = new Date();
        const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
        
        startDate.valueAsDate = firstDay;
        endDate.valueAsDate = today;
    }
}

async function generateInventoryReportHandler() {
    const button = document.getElementById('generateInventoryReport');
    const originalText = button.innerHTML;
    showLoading(button);
    
    try {
        const report = await apiCall('/api/reports/inventory');
        displayInventoryReport(report);
    } catch (error) {
        // Error handling is done in apiCall
    } finally {
        hideLoading(button, originalText);
    }
}

async function generateSalesReportHandler() {
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    
    if (!startDate || !endDate) {
        showAlert('Пожалуйста, выберите начальную и конечную даты', 'warning');
        return;
    }
    
    const button = document.getElementById('generateSalesReport');
    const originalText = button.innerHTML;
    showLoading(button);
    
    try {
        const report = await apiCall(`/api/reports/sales?start_date=${startDate}&end_date=${endDate}`);
        displaySalesReport(report);
    } catch (error) {
        // Error handling is done in apiCall
    } finally {
        hideLoading(button, originalText);
    }
}

async function generateQuarterlyReportHandler() {
    const year = document.getElementById('yearSelect').value;
    const quarter = document.getElementById('quarterSelect').value;
    
    const button = document.getElementById('generateQuarterlyReport');
    const originalText = button.innerHTML;
    showLoading(button);
    
    try {
        const report = await apiCall(`/api/reports/sales?quarter=${quarter}&year=${year}`);
        displaySalesReport(report);
    } catch (error) {
        // Error handling is done in apiCall
    } finally {
        hideLoading(button, originalText);
    }
}

function displayInventoryReport(report) {
    const resultsDiv = document.getElementById('reportResults');
    
    let html = `
        <div class="report-section">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h4>Отчет по остаткам на складе</h4>
                <button class="btn btn-primary" onclick="window.print()">
                    <i class="fas fa-print me-2"></i>Печать
                </button>
            </div>
            
            <div class="row mb-4">
                <div class="col-md-6">
                    <p><strong>Дата формирования:</strong> ${report.report_date}</p>
                    <p><strong>Общее количество товаров:</strong> ${report.total_items} шт.</p>
                </div>
                <div class="col-md-6">
                    <p><strong>Общая стоимость запасов:</strong> ${formatCurrency(report.total_value)}</p>
                </div>
            </div>
            
            <div class="table-responsive">
                <table class="table table-striped report-table">
                    <thead>
                        <tr>
                            <th>Тип</th>
                            <th>Производитель</th>
                            <th>Модель</th>
                            <th>Количество</th>
                            <th>Цена закупки</th>
                            <th>Общая стоимость</th>
                        </tr>
                    </thead>
                    <tbody>
    `;
    
    report.items.forEach(item => {
        html += `
            <tr>
                <td>${item.component_type}</td>
                <td>${item.manufacturer}</td>
                <td>${item.model}</td>
                <td>
                    <span class="badge ${item.quantity < 5 ? 'bg-warning' : 'bg-success'}">
                        ${item.quantity} шт.
                    </span>
                </td>
                <td>${formatCurrency(item.purchase_price)}</td>
                <td>${formatCurrency(item.value)}</td>
            </tr>
        `;
    });
    
    html += `
                    </tbody>
                </table>
            </div>
        </div>
    `;
    
    resultsDiv.innerHTML = html;
}

function displaySalesReport(report) {
    const resultsDiv = document.getElementById('reportResults');
    
    let html = `
        <div class="report-section">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h4>Отчет по продажам</h4>
                <button class="btn btn-primary" onclick="window.print()">
                    <i class="fas fa-print me-2"></i>Печать
                </button>
            </div>
            
            <div class="row mb-4">
                <div class="col-md-6">
                    <p><strong>Период:</strong> ${report.period}</p>
                    <p><strong>Общая выручка:</strong> ${formatCurrency(report.total_revenue)}</p>
                    <p><strong>Общее количество проданных единиц:</strong> ${report.total_units} шт.</p>
                </div>
                <div class="col-md-6">
                    <p><strong>Себестоимость проданного:</strong> ${formatCurrency(report.total_cost)}</p>
                    <p><strong>Прибыль:</strong> 
                        <span class="${report.total_profit >= 0 ? 'text-success' : 'text-danger'}">
                            ${formatCurrency(report.total_profit)}
                        </span>
                    </p>
                </div>
            </div>
            
            <div class="table-responsive">
                <table class="table table-striped report-table">
                    <thead>
                        <tr>
                            <th>Дата</th>
                            <th>Документ</th>
                            <th>Покупатель</th>
                            <th>Товар</th>
                            <th>Количество</th>
                            <th>Цена за шт.</th>
                            <th>Выручка</th>
                        </tr>
                    </thead>
                    <tbody>
    `;
    
    if (report.sales && report.sales.length > 0) {
        report.sales.forEach(sale => {
            html += `
                <tr>
                    <td>${sale.sale_date}</td>
                    <td>${sale.document_number}</td>
                    <td>${sale.customer}</td>
                    <td>${sale.product}</td>
                    <td>${sale.quantity} шт.</td>
                    <td>${formatCurrency(sale.unit_price)}</td>
                    <td>${formatCurrency(sale.revenue)}</td>
                </tr>
            `;
        });
    } else {
        html += `
            <tr>
                <td colspan="7" class="text-center text-muted">Нет данных о продажах за выбранный период</td>
            </tr>
        `;
    }
    
    html += `
                    </tbody>
                </table>
            </div>
        </div>
    `;
    
    resultsDiv.innerHTML = html;
}

// Initialize when page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeReportsHandlers);
} else {
    initializeReportsHandlers();
}