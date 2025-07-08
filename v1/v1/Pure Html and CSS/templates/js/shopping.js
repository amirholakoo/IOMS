// Shopping Page JavaScript

// Product database with paper characteristics
const productDatabase = {
    cash: [
        {
            id: 'cash_1',
            name: 'کاغذ A4',
            type: 'کاغذ تحریر',
            grammage: '80 گرم',
            size: 'A4 (210×297)',
            color: 'سفید',
            price: 25000,
            stock: 150,
            stockStatus: 'high'
        },
        {
            id: 'cash_2',
            name: 'کاغذ A3',
            type: 'کاغذ تحریر',
            grammage: '80 گرم',
            size: 'A3 (297×420)',
            color: 'سفید',
            price: 45000,
            stock: 80,
            stockStatus: 'medium'
        },
        {
            id: 'cash_3',
            name: 'کاغذ رنگی',
            type: 'کاغذ رنگی',
            grammage: '120 گرم',
            size: 'A4 (210×297)',
            color: 'آبی',
            price: 35000,
            stock: 45,
            stockStatus: 'low'
        },
        {
            id: 'cash_4',
            name: 'کاغذ گلاسه',
            type: 'کاغذ گلاسه',
            grammage: '150 گرم',
            size: 'A4 (210×297)',
            color: 'سفید',
            price: 55000,
            stock: 60,
            stockStatus: 'medium'
        },
        {
            id: 'cash_5',
            name: 'کاغذ کاهی',
            type: 'کاغذ کاهی',
            grammage: '70 گرم',
            size: 'A4 (210×297)',
            color: 'کاهی',
            price: 18000,
            stock: 200,
            stockStatus: 'high'
        },
        {
            id: 'cash_6',
            name: 'کاغذ A5',
            type: 'کاغذ تحریر',
            grammage: '90 گرم',
            size: 'A5 (148×210)',
            color: 'سفید',
            price: 15000,
            stock: 120,
            stockStatus: 'medium'
        },
        {
            id: 'cash_7',
            name: 'کاغذ مقوا',
            type: 'کاغذ مقوا',
            grammage: '200 گرم',
            size: 'A4 (210×297)',
            color: 'سفید',
            price: 75000,
            stock: 30,
            stockStatus: 'low'
        },
        {
            id: 'cash_8',
            name: 'کاغذ رنگی سبز',
            type: 'کاغذ رنگی',
            grammage: '100 گرم',
            size: 'A4 (210×297)',
            color: 'سبز',
            price: 32000,
            stock: 55,
            stockStatus: 'medium'
        }
    ],
    credit: [
        {
            id: 'credit_1',
            name: 'کاغذ A4 نسیه',
            type: 'کاغذ تحریر',
            grammage: '80 گرم',
            size: 'A4 (210×297)',
            color: 'سفید',
            price: 28000,
            stock: 120,
            stockStatus: 'medium'
        },
        {
            id: 'credit_2',
            name: 'کاغذ A3 نسیه',
            type: 'کاغذ تحریر',
            grammage: '80 گرم',
            size: 'A3 (297×420)',
            color: 'سفید',
            price: 50000,
            stock: 50,
            stockStatus: 'low'
        },
        {
            id: 'credit_3',
            name: 'کاغذ رنگی نسیه',
            type: 'کاغذ رنگی',
            grammage: '120 گرم',
            size: 'A4 (210×297)',
            color: 'قرمز',
            price: 38000,
            stock: 30,
            stockStatus: 'low'
        },
        {
            id: 'credit_4',
            name: 'کاغذ گلاسه نسیه',
            type: 'کاغذ گلاسه',
            grammage: '200 گرم',
            size: 'A4 (210×297)',
            color: 'سفید',
            price: 65000,
            stock: 40,
            stockStatus: 'low'
        },
        {
            id: 'credit_5',
            name: 'کاغذ کاهی نسیه',
            type: 'کاغذ کاهی',
            grammage: '70 گرم',
            size: 'A4 (210×297)',
            color: 'کاهی',
            price: 20000,
            stock: 180,
            stockStatus: 'high'
        },
        {
            id: 'credit_6',
            name: 'کاغذ A2 نسیه',
            type: 'کاغذ تحریر',
            grammage: '120 گرم',
            size: 'A2 (420×594)',
            color: 'سفید',
            price: 85000,
            stock: 25,
            stockStatus: 'low'
        },
        {
            id: 'credit_7',
            name: 'کاغذ رنگی زرد نسیه',
            type: 'کاغذ رنگی',
            grammage: '100 گرم',
            size: 'A4 (210×297)',
            color: 'زرد',
            price: 35000,
            stock: 40,
            stockStatus: 'low'
        },
        {
            id: 'credit_8',
            name: 'کاغذ مقوا نسیه',
            type: 'کاغذ مقوا',
            grammage: '250 گرم',
            size: 'A3 (297×420)',
            color: 'سفید',
            price: 120000,
            stock: 15,
            stockStatus: 'low'
        }
    ]
};

// Available characteristics for dropdowns
const characteristics = {
    types: ['کاغذ تحریر', 'کاغذ رنگی', 'کاغذ گلاسه', 'کاغذ کاهی', 'کاغذ مقوا'],
    grammages: ['70 گرم', '80 گرم', '90 گرم', '100 گرم', '120 گرم', '150 گرم', '200 گرم', '250 گرم'],
    sizes: ['A4 (210×297)', 'A3 (297×420)', 'A5 (148×210)', 'A2 (420×594)', 'B4 (250×353)'],
    colors: ['سفید', 'کاهی', 'آبی', 'قرمز', 'سبز', 'زرد', 'صورتی', 'نارنجی']
};

// Selected products storage
let selectedProducts = [];

/**
 * Initialize the shopping page
 */
function initializePage() {
    // Display user name (removed security check for development)
    const userName = sessionStorage.getItem('userName') || 'کاربر';
    const userNameElement = document.getElementById('userName');
    if (userNameElement) {
        userNameElement.textContent = userName;
    }

    // Load products
    loadProducts();

    // Add touch feedback for mobile devices
    addTouchFeedback();
}

/**
 * Load products into tables
 */
function loadProducts() {
    loadTableProducts('cash', productDatabase.cash);
    loadTableProducts('credit', productDatabase.credit);
}

/**
 * Load products into specific table
 * @param {string} tableType - 'cash' or 'credit'
 * @param {Array} products - Array of products
 */
function loadTableProducts(tableType, products) {
    const tableBody = document.getElementById(`${tableType}TableBody`);
    if (!tableBody) return;

    tableBody.innerHTML = '';

    products.forEach(product => {
        const row = createProductRow(product, tableType);
        tableBody.appendChild(row);
    });
}

/**
 * Create a product row
 * @param {Object} product - Product object
 * @param {string} tableType - 'cash' or 'credit'
 * @returns {HTMLElement} - Table row element
 */
function createProductRow(product, tableType) {
    const row = document.createElement('tr');
    row.className = 'product-row';
    row.dataset.productId = product.id;

    row.innerHTML = `
        <td>
            <select class="characteristic-dropdown type-dropdown" onchange="updateProductCharacteristic('${product.id}', 'type', this.value)">
                ${characteristics.types.map(type =>
        `<option value="${type}" ${type === product.type ? 'selected' : ''}>${type}</option>`
    ).join('')}
            </select>
        </td>
        <td>
            <select class="characteristic-dropdown grammage-dropdown" onchange="updateProductCharacteristic('${product.id}', 'grammage', this.value)">
                ${characteristics.grammages.map(grammage =>
        `<option value="${grammage}" ${grammage === product.grammage ? 'selected' : ''}>${grammage}</option>`
    ).join('')}
            </select>
        </td>
        <td>
            <select class="characteristic-dropdown size-dropdown" onchange="updateProductCharacteristic('${product.id}', 'size', this.value)">
                ${characteristics.sizes.map(size =>
        `<option value="${size}" ${size === product.size ? 'selected' : ''}>${size}</option>`
    ).join('')}
            </select>
        </td>
        <td>
            <select class="characteristic-dropdown color-dropdown" onchange="updateProductCharacteristic('${product.id}', 'color', this.value)">
                ${characteristics.colors.map(color =>
        `<option value="${color}" ${color === product.color ? 'selected' : ''}>${color}</option>`
    ).join('')}
            </select>
        </td>
        <td class="price-cell">${PersianNumbers.formatPrice(product.price)}</td>
        <td class="stock-cell stock-${product.stockStatus}">${PersianNumbers.formatStock(product.stock)}</td>
        <td>
            <div class="selection-controls">
                <input type="number" class="quantity-input" min="1" max="${product.stock}" value="1" 
                       onchange="updateQuantity('${product.id}', this.value)">
                <button class="select-btn" onclick="toggleProductSelection('${product.id}', '${tableType}')">
                    انتخاب
                </button>
            </div>
        </td>
    `;

    return row;
}

/**
 * Update product characteristic
 * @param {string} productId - Product ID
 * @param {string} characteristic - Characteristic type
 * @param {string} value - New value
 */
function updateProductCharacteristic(productId, characteristic, value) {
    // Find product in database
    const product = findProduct(productId);
    if (product) {
        product[characteristic] = value;

        // Update price based on characteristics (simplified logic)
        updateProductPrice(product);

        // Update display
        updateProductDisplay(productId);
    }
}

/**
 * Find product by ID
 * @param {string} productId - Product ID
 * @returns {Object|null} - Product object or null
 */
function findProduct(productId) {
    const allProducts = [...productDatabase.cash, ...productDatabase.credit];
    return allProducts.find(p => p.id === productId) || null;
}

/**
 * Update product price based on characteristics
 * @param {Object} product - Product object
 */
function updateProductPrice(product) {
    let basePrice = 20000; // Base price

    // Adjust price based on type
    switch (product.type) {
        case 'کاغذ رنگی':
            basePrice += 10000;
            break;
        case 'کاغذ گلاسه':
            basePrice += 20000;
            break;
        case 'کاغذ کاهی':
            basePrice -= 5000;
            break;
    }

    // Adjust price based on grammage
    const grammageValue = parseInt(product.grammage);
    if (grammageValue > 80) {
        basePrice += (grammageValue - 80) * 500;
    }

    // Adjust price based on size
    if (product.size.includes('A3')) {
        basePrice += 15000;
    } else if (product.size.includes('A2')) {
        basePrice += 30000;
    }

    // Adjust price based on color
    if (product.color !== 'سفید' && product.color !== 'کاهی') {
        basePrice += 5000;
    }

    product.price = basePrice;
}

/**
 * Update product display
 * @param {string} productId - Product ID
 */
function updateProductDisplay(productId) {
    const product = findProduct(productId);
    if (!product) return;

    const row = document.querySelector(`[data-product-id="${productId}"]`);
    if (row) {
        const priceCell = row.querySelector('.price-cell');
        if (priceCell) {
            priceCell.textContent = PersianNumbers.formatPrice(product.price);
        }
    }
}

/**
 * Update quantity for product
 * @param {string} productId - Product ID
 * @param {number} quantity - Quantity
 */
function updateQuantity(productId, quantity) {
    const product = findProduct(productId);
    if (!product) return;

    quantity = parseInt(quantity);
    if (quantity < 1) quantity = 1;
    if (quantity > product.stock) quantity = product.stock;

    // Update selected product quantity if already selected
    const selectedIndex = selectedProducts.findIndex(p => p.id === productId);
    if (selectedIndex !== -1) {
        selectedProducts[selectedIndex].quantity = quantity;
        updateSelectedProductsDisplay();
    }
}

/**
 * Toggle product selection
 * @param {string} productId - Product ID
 * @param {string} tableType - 'cash' or 'credit'
 */
function toggleProductSelection(productId, tableType) {
    const product = findProduct(productId);
    if (!product) return;

    const quantityInput = document.querySelector(`[data-product-id="${productId}"] .quantity-input`);
    const quantity = parseInt(quantityInput.value) || 1;

    const selectedIndex = selectedProducts.findIndex(p => p.id === productId);

    if (selectedIndex !== -1) {
        // Remove from selection
        selectedProducts.splice(selectedIndex, 1);
        updateButtonState(productId, false);
    } else {
        // Add to selection
        selectedProducts.push({
            ...product,
            quantity: quantity,
            tableType: tableType
        });
        updateButtonState(productId, true);
    }

    updateSelectedProductsDisplay();
}

/**
 * Update button state
 * @param {string} productId - Product ID
 * @param {boolean} isSelected - Whether product is selected
 */
function updateButtonState(productId, isSelected) {
    const button = document.querySelector(`[data-product-id="${productId}"] .select-btn`);
    if (button) {
        if (isSelected) {
            button.textContent = 'حذف';
            button.classList.add('selected');
        } else {
            button.textContent = 'انتخاب';
            button.classList.remove('selected');
        }
    }
}

/**
 * Update selected products display
 */
function updateSelectedProductsDisplay() {
    const container = document.getElementById('selectedProducts');
    if (!container) return;

    if (selectedProducts.length === 0) {
        container.innerHTML = '<p class="no-selection">هیچ محصولی انتخاب نشده است</p>';
        return;
    }

    container.innerHTML = selectedProducts.map(product => `
        <div class="selected-item">
            <div class="selected-item-info">
                <div class="selected-item-name">${product.name}</div>
                <div class="selected-item-details">
                    ${product.type} - ${product.grammage} - ${product.size} - ${product.color}
                </div>
            </div>
            <div class="selected-item-quantity">${PersianNumbers.formatQuantity(product.quantity)}</div>
            <button class="remove-item-btn" onclick="removeSelectedProduct('${product.id}')">حذف</button>
        </div>
    `).join('');
}

/**
 * Remove selected product
 * @param {string} productId - Product ID
 */
function removeSelectedProduct(productId) {
    const index = selectedProducts.findIndex(p => p.id === productId);
    if (index !== -1) {
        selectedProducts.splice(index, 1);
        updateButtonState(productId, false);
        updateSelectedProductsDisplay();
    }
}

/**
 * Clear all selections
 */
function clearSelection() {
    selectedProducts = [];

    // Reset all buttons
    document.querySelectorAll('.select-btn').forEach(button => {
        button.textContent = 'انتخاب';
        button.classList.remove('selected');
    });

    updateSelectedProductsDisplay();
    showMessage('همه انتخاب‌ها پاک شدند', 'success');
}

/**
 * Proceed to checkout
 */
function proceedToCheckout() {
    if (selectedProducts.length === 0) {
        showMessage('لطفاً ابتدا محصولی انتخاب کنید', 'error');
        return;
    }

    // Store selected products in session storage
    sessionStorage.setItem('selectedProducts', JSON.stringify(selectedProducts));

    showMessage('در حال انتقال به صفحه نهایی...', 'success');
    setTimeout(() => {
        // For now, redirect back to main page
        // In a real app, this would go to checkout page
        window.location.href = 'index.html';
    }, 2000);
}

/**
 * Logout user
 */
function logout() {
    sessionStorage.clear();
    showMessage('خروج با موفقیت انجام شد', 'success');
    setTimeout(() => {
        window.location.href = 'index.html';
    }, 1500);
}

/**
 * Show message to user
 * @param {string} message - Message to display
 * @param {string} type - Message type ('success', 'error', 'info')
 */
function showMessage(message, type = 'info') {
    // Remove existing message if any
    const existingMessage = document.querySelector('.message-popup');
    if (existingMessage) {
        existingMessage.remove();
    }

    // Create message element
    const messageDiv = document.createElement('div');
    messageDiv.className = `message-popup message-${type}`;
    messageDiv.innerHTML = `
        <div class="message-content">
            <span class="message-text">${message}</span>
            <button class="message-close" onclick="this.parentElement.parentElement.remove()">×</button>
        </div>
    `;

    // Add to page
    document.body.appendChild(messageDiv);

    // Auto remove after 5 seconds
    setTimeout(() => {
        if (messageDiv.parentElement) {
            messageDiv.remove();
        }
    }, 5000);
}

/**
 * Add touch feedback for mobile devices
 */
function addTouchFeedback() {
    const buttons = document.querySelectorAll('.select-btn, .action-btn, .remove-item-btn');

    buttons.forEach(button => {
        button.addEventListener('touchstart', function () {
            this.style.transform = 'scale(0.95)';
        });

        button.addEventListener('touchend', function () {
            this.style.transform = '';
        });
    });
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function () {
    initializePage();
    console.log('Shopping page loaded successfully!');
}); 
