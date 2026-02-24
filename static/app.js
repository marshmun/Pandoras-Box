// Global state
let currentItemId = null;
let isDarkMode = false;
let retryCount = {};
let receiptItems = [];  // Store parsed receipt items

// Toast notification system
function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        left: 20px;
        right: 20px;
        max-width: 500px;
        padding: 16px;
        background: ${type === 'success' ? '#34C759' : type === 'error' ? '#FF3B30' : '#FF9500'};
        color: white;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        z-index: 9999;
        animation: slideUp 0.3s ease;
        font-font-weight: 500;
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideDown 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// Dark mode toggle
function toggleDarkMode() {
    isDarkMode = !isDarkMode;
    localStorage.setItem('darkMode', isDarkMode);
    
    if (isDarkMode) {
        enableDarkMode();
    } else {
        disableDarkMode();
    }
}

function enableDarkMode() {
    isDarkMode = true;
    document.body.classList.add('dark-mode');
    document.getElementById('darkModeIcon').textContent = '☀️';
}

function disableDarkMode() {
    isDarkMode = false;
    document.body.classList.remove('dark-mode');
    document.getElementById('darkModeIcon').textContent = '🌙';
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Restore dark mode setting
    if (localStorage.getItem('darkMode') === 'true') {
        enableDarkMode();
    }
    
    loadItems();
    loadExpenses();
    loadShrinkageReport();
    loadStats();

    // Setup tab switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            switchTab(this.getAttribute('data-tab'));
        });
    });

    // Refresh data every 30 seconds
    setInterval(loadStats, 30000);
    
    // Add animation styles
    addAnimationStyles();
});

// Tab Switching
function switchTab(tabName) {
    // Hide all panes
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });

    // Remove active from all tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected pane
    document.getElementById(tabName).classList.add('active');

    // Mark button as active
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // Reload tab data
    if (tabName === 'inventory') {
        loadItems();
    } else if (tabName === 'expenses') {
        loadExpenses();
    } else if (tabName === 'reports') {
        loadShrinkageReport();
    }
}

// Load Items
function loadItems() {
    apiCall('/api/items', 'GET')
        .then(items => {
            const itemList = document.getElementById('itemList');
            if (items.length === 0) {
                itemList.innerHTML = '<p class="loading">No items yet. Add one to get started!</p>';
                return;
            }

            itemList.innerHTML = items.map(item => `
                <div class="item-card" onclick="showItemDetails(${item.id})">
                    <div class="item-name">${escapeHtml(item.name)}</div>
                    <div class="item-info">
                        <div class="info-row">
                            <span class="info-label">SKU:</span>
                            <span>${item.sku || 'N/A'}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Stock:</span>
                            <span class="item-quantity">${item.quantity} units</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Cost:</span>
                            <span>$${parseFloat(item.unit_cost).toFixed(2)}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Price:</span>
                            <span>$${parseFloat(item.selling_price).toFixed(2)}</span>
                        </div>
                    </div>
                </div>
            `).join('');
        })
        .catch(error => {
            document.getElementById('itemList').innerHTML = '<p class="loading">Error loading items. Try refreshing.</p>';
        });
}

// Load Expenses
function loadExpenses() {
    apiCall('/api/expenses?limit=50', 'GET')
        .then(expenses => {
            const expenseList = document.getElementById('expenseList');
            if (expenses.length === 0) {
                expenseList.innerHTML = '<p class="loading">No expenses recorded yet</p>';
                return;
            }

            expenseList.innerHTML = expenses.map(expense => {
                const date = new Date(expense.created_at).toLocaleDateString();
                return `
                    <div class="expense-card">
                        <div class="expense-header">
                            <div class="expense-desc">${escapeHtml(expense.description)}</div>
                            <div class="expense-amount">$${parseFloat(expense.amount).toFixed(2)}</div>
                            <button class="expense-delete" onclick="deleteExpense(${expense.id})">Delete</button>
                        </div>
                        <div class="expense-meta">
                            <span>${escapeHtml(expense.category || 'Uncategorized')}</span> • <span>${date}</span>
                        </div>
                    </div>
                `;
            }).join('');
        })
        .catch(error => {
            console.error('Error loading expenses:', error);
            document.getElementById('expenseList').innerHTML = '<p class="loading">Error loading expenses</p>';
        });
}

// Load Shrinkage Report
function loadShrinkageReport() {
    apiCall('/api/reports/shrinkage', 'GET')
        .then(items => {
            const reportList = document.getElementById('shrinkageReport');
            if (items.length === 0) {
                reportList.innerHTML = '<p class="loading">No shrinkage recorded</p>';
                return;
            }

            reportList.innerHTML = items.map(item => `
                <div class="report-item">
                    <div class="report-item-title">${escapeHtml(item.item)}</div>
                    <div class="report-item-stats">
                        <div class="info-row">
                            <span class="info-label">Lost:</span>
                            <span>${item.quantity_lost} units</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Value:</span>
                            <span>$${parseFloat(item.total_value).toFixed(2)}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Reason:</span>
                            <span>${escapeHtml(item.reason || 'Unknown')}</span>
                        </div>
                    </div>
                </div>
            `).join('');
        })
        .catch(error => {
            console.error('Error loading shrinkage report:', error);
            document.getElementById('shrinkageReport').innerHTML = '<p class="loading">Error loading report</p>';
        });
}

// Load Stats
function loadStats() {
    apiCall('/api/stats', 'GET')
        .then(stats => {
            document.getElementById('inventoryValue').textContent = `$${stats.total_inventory_value.toFixed(2)}`;
            document.getElementById('totalExpenses').textContent = `$${stats.total_expenses.toFixed(2)}`;
            
            // Update profit display with color based on positive/negative
            const profitElement = document.getElementById('totalProfit');
            const profit = parseFloat(stats.profit);
            profitElement.textContent = `$${profit.toFixed(2)}`;
            
            if (profit >= 0) {
                profitElement.style.color = '#34C759';
            } else {
                profitElement.style.color = '#FF3B30';
            }
        })
        .catch(error => console.error('Error loading stats:', error));
}

// Show Item Details
function showItemDetails(itemId) {
    currentItemId = itemId;
    apiCall(`/api/items/${itemId}`, 'GET')
        .then(item => {
            document.getElementById('detailsItemName').textContent = escapeHtml(item.name);
            document.getElementById('itemDetails').innerHTML = `
                <div class="item-details-content">
                    <div class="detail-row">
                        <span class="detail-label">SKU</span>
                        <span class="detail-value">${item.sku || 'N/A'}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Current Stock</span>
                        <span class="detail-value">${item.quantity} units</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Unit Cost</span>
                        <span class="detail-value">$${parseFloat(item.unit_cost).toFixed(2)}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Selling Price</span>
                        <span class="detail-value">$${parseFloat(item.selling_price).toFixed(2)}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">On Display</span>
                        <span class="detail-value">${item.on_display} units</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Category</span>
                        <span class="detail-value">${item.category || 'Uncategorized'}</span>
                    </div>
                </div>
            `;
            openModal('itemDetailsModal');
        })
        .catch(error => {
            console.error('Error loading item details:', error);
            showToast('Error loading item details', 'error');
        });
}

// Add Item Stock
function addItemStock() {
    if (!currentItemId) {
        showToast('No item selected', 'error');
        return;
    }

    const quantity = prompt('Enter quantity to add:');
    
    if (!quantity) {
        return;
    }

    if (isNaN(parseInt(quantity)) || parseInt(quantity) <= 0) {
        showToast('Please enter a valid positive number', 'error');
        return;
    }

    apiCall(`/api/items/${currentItemId}/quantity`, 'POST', {
        change: parseInt(quantity),
        type: 'stock_in'
    })
    .then(data => {
        if (data.success) {
            closeModal('itemDetailsModal');
            loadItems();
            loadStats();
            showToast(`Added ${quantity} units to stock!`, 'success');
        } else {
            showToast('Error: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Error updating stock. Please try again.', 'error');
    });
}

// Record Item Loss
function recordItemLoss() {
    if (!currentItemId) {
        showToast('No item selected', 'error');
        return;
    }

    const quantity = prompt('Enter quantity lost:');
    if (!quantity) {
        return;
    }

    if (isNaN(parseInt(quantity)) || parseInt(quantity) <= 0) {
        showToast('Please enter a valid positive number', 'error');
        return;
    }

    const reason = prompt('Enter reason (damage, theft, spoilage, etc.):');
    
    if (!reason) {
        return;
    }

    apiCall('/api/shrinkage', 'POST', {
        item_id: currentItemId,
        quantity: parseInt(quantity),
        reason: reason
    })
    .then(data => {
        if (data.success) {
            closeModal('itemDetailsModal');
            loadItems();
            loadShrinkageReport();
            loadStats();
            showToast(`Recorded ${quantity} units loss: ${reason}`, 'success');
        } else {
            showToast('Error: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Error recording shrinkage. Please try again.', 'error');
    });
}

// Delete Expense
function deleteExpense(expenseId) {
    if (!confirm('Are you sure you want to delete this expense?')) {
        return;
    }

    apiCall(`/api/expenses/${expenseId}`, 'DELETE')
        .then(data => {
            if (data.success) {
                loadExpenses();
                loadStats();
                showToast('Expense deleted successfully', 'success');
            } else {
                showToast('Error: ' + data.error, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Error deleting expense. Please try again.', 'error');
        });
}

// Receipt OCR Functions
function showReceiptUploadModal() {
    openModal('receiptUploadModal');
}

function handleReceiptUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
        showToast('Please select an image file', 'error');
        return;
    }

    uploadReceipt(file);
}

function uploadReceipt(file) {
    const formData = new FormData();
    formData.append('file', file);

    // Show progress
    document.getElementById('uploadProgress').style.display = 'block';
    document.getElementById('uploadArea').style.display = 'none';

    fetch('/api/receipt/process', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('uploadProgress').style.display = 'none';
        document.getElementById('uploadArea').style.display = 'block';

        if (data.success) {
            receiptItems = data.items;
            showReceiptItemsReview();
            closeModal('receiptUploadModal');
        } else {
            showToast('Error: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('uploadProgress').style.display = 'none';
        document.getElementById('uploadArea').style.display = 'block';
        showToast('Error processing receipt. Make sure OCR is installed.', 'error');
    });
}

function showReceiptItemsReview() {
    if (receiptItems.length === 0) {
        showToast('No items found in receipt', 'error');
        return;
    }

    const itemsList = document.getElementById('receiptItemsList');
    itemsList.innerHTML = receiptItems.map((item, index) => `
        <div class="receipt-item-card" onclick="toggleReceiptItem(${index})">
            <div class="receipt-item-info">
                <div class="receipt-item-name">${escapeHtml(item.name)}</div>
                <div class="receipt-item-price">Price: $${parseFloat(item.price).toFixed(2)}</div>
            </div>
            <input type="checkbox" class="receipt-item-checkbox" id="receipt-item-${index}" checked>
        </div>
    `).join('');

    openModal('receiptItemsModal');
}

function toggleReceiptItem(index) {
    const checkbox = document.getElementById(`receipt-item-${index}`);
    checkbox.checked = !checkbox.checked;

    const card = checkbox.closest('.receipt-item-card');
    if (checkbox.checked) {
        card.classList.add('selected');
    } else {
        card.classList.remove('selected');
    }
}

function addAllReceiptItems() {
    const selectedItems = [];
    receiptItems.forEach((item, index) => {
        const checkbox = document.getElementById(`receipt-item-${index}`);
        if (checkbox && checkbox.checked) {
            selectedItems.push({
                name: item.name,
                unit_cost: item.price,
                selling_price: item.price,
                category: 'Receipt Import',
                quantity: item.quantity || 1
            });
        }
    });

    if (selectedItems.length === 0) {
        showToast('Please select at least one item', 'error');
        return;
    }

    apiCall('/api/inventory/bulk-add', 'POST', { items: selectedItems })
        .then(data => {
            if (data.success) {
                closeModal('receiptItemsModal');
                loadItems();
                loadStats();
                receiptItems = [];
                showToast(`Added ${data.added_count} items to inventory`, 'success');
            } else {
                showToast('Error: ' + data.error, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Error adding items. Please try again.', 'error');
        });
}

// Modal Functions
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.classList.add('show');
    document.body.style.overflow = 'hidden';
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.classList.remove('show');
    document.body.style.overflow = 'auto';
}

function showAddItemModal() {
    document.getElementById('itemName').value = '';
    document.getElementById('itemSku').value = '';
    document.getElementById('itemCategory').value = '';
    document.getElementById('itemCost').value = '0';
    document.getElementById('itemPrice').value = '0';
    openModal('addItemModal');
}

function showAddExpenseModal() {
    document.getElementById('expenseDesc').value = '';
    document.getElementById('expenseAmount').value = '';
    document.getElementById('expenseCategory').value = '';
    openModal('addExpenseModal');
}

// Form Handlers
function handleAddItem(event) {
    event.preventDefault();

    const itemName = document.getElementById('itemName').value.trim();
    const itemSku = document.getElementById('itemSku').value.trim();
    const itemCategory = document.getElementById('itemCategory').value.trim();
    const itemCost = document.getElementById('itemCost').value;
    const itemPrice = document.getElementById('itemPrice').value;

    // Validation
    if (!itemName) {
        showToast('Item name is required', 'error');
        return;
    }

    if (itemCost && isNaN(parseFloat(itemCost))) {
        showToast('Unit cost must be a valid number', 'error');
        return;
    }

    if (itemPrice && isNaN(parseFloat(itemPrice))) {
        showToast('Selling price must be a valid number', 'error');
        return;
    }

    const itemData = {
        name: itemName,
        sku: itemSku || null,
        category: itemCategory || null,
        unit_cost: parseFloat(itemCost || 0),
        selling_price: parseFloat(itemPrice || 0)
    };

    apiCall('/api/items', 'POST', itemData)
        .then(data => {
            if (data.success) {
                closeModal('addItemModal');
                loadItems();
                loadStats();
                showToast('Item added successfully!', 'success');
            } else {
                showToast('Error: ' + data.error, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Error adding item. Please try again.', 'error');
        });
}

function handleAddExpense(event) {
    event.preventDefault();

    const expenseDesc = document.getElementById('expenseDesc').value.trim();
    const expenseAmount = document.getElementById('expenseAmount').value;
    const expenseCategory = document.getElementById('expenseCategory').value.trim();

    // Validation
    if (!expenseDesc) {
        showToast('Description is required', 'error');
        return;
    }

    if (!expenseAmount || isNaN(parseFloat(expenseAmount))) {
        showToast('Amount must be a valid number', 'error');
        return;
    }

    if (parseFloat(expenseAmount) <= 0) {
        showToast('Amount must be greater than 0', 'error');
        return;
    }

    const expenseData = {
        description: expenseDesc,
        amount: parseFloat(expenseAmount),
        category: expenseCategory || 'Uncategorized'
    };

    apiCall('/api/expenses', 'POST', expenseData)
        .then(data => {
            if (data.success) {
                closeModal('addExpenseModal');
                loadExpenses();
                loadStats();
                showToast('Expense added successfully!', 'success');
            } else {
                showToast('Error: ' + data.error, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Error adding expense. Please try again.', 'error');
        });
}

// Close modals when clicking outside
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.classList.remove('show');
        document.body.style.overflow = 'auto';
    }
};

// Helper Functions
// Escape HTML to prevent XSS
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Robust API call with retry and error handling
function apiCall(endpoint, method = 'GET', data = null, maxRetries = 2) {
    const requestId = `${endpoint}-${Date.now()}`;
    retryCount[requestId] = 0;

    return fetch(endpoint, {
        method: method,
        headers: method !== 'GET' ? { 'Content-Type': 'application/json' } : {},
        body: method !== 'GET' && data ? JSON.stringify(data) : null,
        timeout: 10000
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response.json();
    })
    .catch(error => {
        if (retryCount[requestId] < maxRetries) {
            retryCount[requestId]++;
            console.log(`Retry attempt ${retryCount[requestId]} for ${endpoint}`);
            return new Promise(resolve => {
                setTimeout(() => {
                    apiCall(endpoint, method, data, maxRetries)
                        .then(resolve)
                        .catch(err => {
                            throw err;
                        });
                }, 1000 * retryCount[requestId]);
            });
        }
        throw error;
    });
}

// Add animation styles
function addAnimationStyles() {
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideUp {
            from {
                transform: translateY(100px);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }
        @keyframes slideDown {
            from {
                transform: translateY(0);
                opacity: 1;
            }
            to {
                transform: translateY(100px);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}

// Validate form inputs
function validateFormData(data, requiredFields) {
    for (let field of requiredFields) {
        if (!data[field] || (typeof data[field] === 'string' && data[field].trim() === '')) {
            return { valid: false, error: `${field} is required` };
        }
    }
    return { valid: true };
}

// Confirm action dialog
function confirmAction(message) {
    return new Promise(resolve => {
        if (confirm(message)) {
            resolve(true);
        } else {
            resolve(false);
        }
    });
}
