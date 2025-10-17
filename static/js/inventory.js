// Inventory management JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeInventoryHandlers();
});

function initializeInventoryHandlers() {
    // Add item form submission
    const addItemForm = document.getElementById('addItemForm');
    if (addItemForm) {
        addItemForm.addEventListener('submit', handleAddItem);
    }

    // Edit item functionality
    const editButtons = document.querySelectorAll('.edit-item');
    editButtons.forEach(button => {
        button.addEventListener('click', function() {
            const itemId = this.dataset.itemId;
            openEditModal(itemId);
        });
    });

    // Delete item functionality
    const deleteButtons = document.querySelectorAll('.delete-item');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const itemId = this.dataset.itemId;
            handleDeleteItem(itemId);
        });
    });

    // Edit item form submission
    const editItemForm = document.getElementById('editItemForm');
    if (editItemForm) {
        editItemForm.addEventListener('submit', handleEditItem);
    }
}

async function handleAddItem(e) {
    e.preventDefault();
    
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    showLoading(submitBtn);
    
    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());
    
    try {
        const response = await apiCall('/api/inventory', {
            method: 'POST',
            body: JSON.stringify(data)
        });
        
        showAlert(response.message, 'success');
        bootstrap.Modal.getInstance(document.getElementById('addItemModal')).hide();
        this.reset();
        // Reload the page to show new item
        setTimeout(() => location.reload(), 1000);
    } catch (error) {
        // Error handling is done in apiCall
    } finally {
        hideLoading(submitBtn, originalText);
    }
}

async function handleEditItem(e) {
    e.preventDefault();
    
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    showLoading(submitBtn);
    
    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());
    const itemId = data.item_id;
    
    try {
        const response = await apiCall(`/api/inventory/${itemId}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
        
        showAlert(response.message, 'success');
        bootstrap.Modal.getInstance(document.getElementById('editItemModal')).hide();
        // Reload the page to show updated item
        setTimeout(() => location.reload(), 1000);
    } catch (error) {
        // Error handling is done in apiCall
    } finally {
        hideLoading(submitBtn, originalText);
    }
}

async function handleDeleteItem(itemId) {
    if (!confirm('Вы уверены, что хотите удалить этот товар? Это действие нельзя отменить.')) {
        return;
    }
    
    try {
        const response = await apiCall(`/api/inventory/${itemId}`, {
            method: 'DELETE'
        });
        
        showAlert(response.message, 'success');
        // Reload the page to reflect changes
        setTimeout(() => location.reload(), 1000);
    } catch (error) {
        // Error handling is done in apiCall
    }
}

async function openEditModal(itemId) {
    try {
        const items = await apiCall('/api/inventory');
        const item = items.find(i => i.id == itemId);
        
        if (item) {
            // Populate the edit form with item data
            document.getElementById('editItemId').value = item.id;
            document.getElementById('editReceiptDate').value = formatDateForInput(item.receipt_date);
            document.getElementById('editDocumentNumber').value = item.document_number;
            document.getElementById('editSupplierId').value = item.supplier_id;
            document.getElementById('editComponentType').value = item.component_type;
            document.getElementById('editManufacturer').value = item.manufacturer;
            document.getElementById('editModel').value = item.model;
            document.getElementById('editQuantity').value = item.quantity;
            document.getElementById('editPurchasePrice').value = item.purchase_price;
            document.getElementById('editSellingPrice').value = item.selling_price;
            
            // Show the modal
            const editModal = new bootstrap.Modal(document.getElementById('editItemModal'));
            editModal.show();
        }
    } catch (error) {
        // Error handling is done in apiCall
    }
}

// Search functionality for inventory
function setupInventorySearch() {
    const searchInput = document.getElementById('inventorySearch');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function() {
            const searchTerm = this.value.toLowerCase();
            const rows = document.querySelectorAll('#inventoryTable tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        }, 300));
    }
}

// Initialize when page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeInventoryHandlers);
} else {
    initializeInventoryHandlers();
}