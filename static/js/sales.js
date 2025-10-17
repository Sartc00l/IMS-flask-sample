// Sales management JavaScript - FIXED VERSION

let currentSaleId = null;

document.addEventListener('DOMContentLoaded', function() {
    initializeSalesHandlers();
});

function initializeSalesHandlers() {
    // Initialize date field
    initializeDateField();
    
    // Item selection change
    const itemSelect = document.getElementById('itemSelect');
    if (itemSelect) {
        itemSelect.addEventListener('change', handleItemSelection);
    }

    // Quantity input change
    const quantityInput = document.getElementById('quantityInput');
    if (quantityInput) {
        quantityInput.addEventListener('input', handleQuantityChange);
        quantityInput.addEventListener('blur', validateQuantity);
    }

    // Add sale form submission
    const addSaleForm = document.getElementById('addSaleForm');
    if (addSaleForm) {
        addSaleForm.addEventListener('submit', handleAddSale);
    }

    // Delete sale functionality
    const deleteButtons = document.querySelectorAll('.delete-sale');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const saleId = this.dataset.saleId;
            if (!this.disabled) {
                showDeleteConfirmation(saleId);
            }
        });
    });

    // Confirm delete button
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', handleDeleteSale);
    }

    // Modal show/hide events
    const addSaleModal = document.getElementById('addSaleModal');
    if (addSaleModal) {
        addSaleModal.addEventListener('show.bs.modal', function() {
            resetSaleForm();
        });
        
        addSaleModal.addEventListener('hidden.bs.modal', function() {
            resetSaleForm();
        });
    }

    // Check if there are available items
    checkAvailableItems();
}

function initializeDateField() {
    const saleDateInput = document.getElementById('saleDate');
    if (saleDateInput && !saleDateInput.value) {
        const today = new Date();
        saleDateInput.value = today.toISOString().split('T')[0];
    }
}

function checkAvailableItems() {
    const itemSelect = document.getElementById('itemSelect');
    const addSaleBtn = document.getElementById('addSaleBtn');
    const submitSaleBtn = document.getElementById('submitSaleBtn');
    
    if (itemSelect && itemSelect.options.length <= 1) {
        if (addSaleBtn) {
            addSaleBtn.disabled = true;
            addSaleBtn.title = 'Нет доступных товаров для продажи';
        }
        if (submitSaleBtn) {
            submitSaleBtn.disabled = true;
        }
    }
}

function handleItemSelection() {
    const selectedOption = this.options[this.selectedIndex];
    const availableQuantity = parseInt(selectedOption.dataset.quantity) || 0;
    const price = parseFloat(selectedOption.dataset.price) || 0;
    const manufacturer = selectedOption.dataset.manufacturer || '';
    const model = selectedOption.dataset.model || '';
    
    document.getElementById('availableQuantity').textContent = availableQuantity;
    document.getElementById('quantityInput').max = availableQuantity;
    
    // Reset quantity and total amount
    document.getElementById('quantityInput').value = '';
    document.getElementById('totalAmount').value = '';
    
    // Show/hide item info
    const itemInfo = document.getElementById('itemInfo');
    const selectedItemName = document.getElementById('selectedItemName');
    const selectedItemPrice = document.getElementById('selectedItemPrice');
    
    if (this.value && availableQuantity > 0) {
        selectedItemName.textContent = `${manufacturer} ${model}`;
        selectedItemPrice.textContent = price.toFixed(2);
        itemInfo.style.display = 'block';
    } else {
        itemInfo.style.display = 'none';
    }
    
    // Update quantity input placeholder
    document.getElementById('quantityInput').placeholder = `Макс: ${availableQuantity}`;
    
    // Clear any previous errors
    clearQuantityError();
}

function handleQuantityChange() {
    const itemSelect = document.getElementById('itemSelect');
    const selectedOption = itemSelect.options[itemSelect.selectedIndex];
    const price = parseFloat(selectedOption.dataset.price) || 0;
    const quantity = parseInt(this.value) || 0;
    
    if (quantity > 0 && price > 0) {
        const total = quantity * price;
        document.getElementById('totalAmount').value = formatCurrency(total);
    } else {
        document.getElementById('totalAmount').value = '';
    }
}

function validateQuantity() {
    const quantityInput = document.getElementById('quantityInput');
    const quantity = parseInt(quantityInput.value) || 0;
    
    if (isNaN(quantity) || quantity <= 0) {
        showQuantityError('Количество должно быть числом больше 0');
        return false;
    }
    
    const itemSelect = document.getElementById('itemSelect');
    const selectedOption = itemSelect.options[itemSelect.selectedIndex];
    const availableQuantity = parseInt(selectedOption.dataset.quantity) || 0;
    
    if (quantity > availableQuantity) {
        showQuantityError(`Недостаточно товара. Доступно: ${availableQuantity} шт.`);
        return false;
    }
    
    clearQuantityError();
    return true;
}

function showQuantityError(message) {
    const errorElement = document.getElementById('quantityError');
    errorElement.textContent = message;
    errorElement.style.display = 'block';
    
    const quantityInput = document.getElementById('quantityInput');
    quantityInput.classList.add('is-invalid');
}

function clearQuantityError() {
    const errorElement = document.getElementById('quantityError');
    errorElement.style.display = 'none';
    
    const quantityInput = document.getElementById('quantityInput');
    quantityInput.classList.remove('is-invalid');
}

async function handleAddSale(e) {
    e.preventDefault();
    
    // Validate form
    if (!validateSaleForm()) {
        return;
    }
    
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    showLoading(submitBtn, 'Оформление...');
    
    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());
    
    // Преобразуем числовые поля в правильные типы
    const processedData = {
        ...data,
        item_id: parseInt(data.item_id),
        quantity_sold: parseInt(data.quantity_sold)
    };
    
    try {
        const response = await apiCall('/api/sales', {
            method: 'POST',
            body: JSON.stringify(processedData)
        });
        
        showAlert('Продажа успешно оформлена!', 'success');
        
        // Close modal and reset form
        const modal = bootstrap.Modal.getInstance(document.getElementById('addSaleModal'));
        modal.hide();
        
        // Reload the page to show new sale
        setTimeout(() => {
            window.location.reload();
        }, 1500);
        
    } catch (error) {
        console.error('Sale error:', error);
    } finally {
        hideLoading(submitBtn, originalText);
    }
}

function validateSaleForm() {
    const itemSelect = document.getElementById('itemSelect');
    const quantityInput = document.getElementById('quantityInput');
    
    // Check if item is selected
    if (!itemSelect.value) {
        showAlert('Пожалуйста, выберите товар', 'warning');
        itemSelect.focus();
        return false;
    }
    
    // Validate quantity
    if (!validateQuantity()) {
        quantityInput.focus();
        return false;
    }
    
    // Check if there are any items available
    const selectedOption = itemSelect.options[itemSelect.selectedIndex];
    const availableQuantity = parseInt(selectedOption.dataset.quantity) || 0;
    const inputQuantity = parseInt(quantityInput.value) || 0;
    
    if (availableQuantity <= 0) {
        showAlert('Выбранный товар отсутствует на складе', 'warning');
        return false;
    }
    
    if (inputQuantity > availableQuantity) {
        showAlert(`Недостаточно товара. Доступно: ${availableQuantity} шт.`, 'warning');
        return false;
    }
    
    return true;
}

function resetSaleForm() {
    const form = document.getElementById('addSaleForm');
    if (form) {
        form.reset();
    }
    
    // Reset dynamic fields
    document.getElementById('availableQuantity').textContent = '0';
    document.getElementById('totalAmount').value = '';
    document.getElementById('itemInfo').style.display = 'none';
    
    // Clear errors
    clearQuantityError();
    
    // Reset date to today
    initializeDateField();
}

function showDeleteConfirmation(saleId) {
    currentSaleId = saleId;
    const modal = new bootstrap.Modal(document.getElementById('confirmDeleteModal'));
    modal.show();
}

async function handleDeleteSale() {
    if (!currentSaleId) return;
    
    const button = document.getElementById('confirmDeleteBtn');
    const originalText = button.innerHTML;
    showLoading(button, 'Удаление...');
    
    try {
        const response = await apiCall(`/api/sales/${currentSaleId}`, {
            method: 'DELETE'
        });
        
        showAlert(response.message, 'success');
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('confirmDeleteModal'));
        modal.hide();
        
        // Reload the page to reflect changes
        setTimeout(() => {
            window.location.reload();
        }, 1000);
        
    } catch (error) {
        console.error('Delete sale error:', error);
    } finally {
        hideLoading(button, originalText);
        currentSaleId = null;
    }
}

function showLoading(element, text = 'Загрузка...') {
    element.innerHTML = `<div class="loading-spinner"></div> ${text}`;
    element.disabled = true;
}

function hideLoading(element, originalText) {
    element.innerHTML = originalText;
    element.disabled = false;
}

// Search functionality for sales
function setupSalesSearch() {
    const searchInput = document.getElementById('salesSearch');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function() {
            const searchTerm = this.value.toLowerCase();
            const rows = document.querySelectorAll('#salesTable tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        }, 300));
    }
}

// Initialize when page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeSalesHandlers);
} else {
    initializeSalesHandlers();
}