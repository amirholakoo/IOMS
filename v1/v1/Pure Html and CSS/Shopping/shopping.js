// Shopping Page JavaScript

// Default product database (fallback if admin hasn't set products)
const defaultProductDatabase = {
    cash: [
        {
            id: 'cash_1',
            name: 'کاغذ A4 - 80 گرم - سفید',
            price: 25000,
            stock: 150,
            stockStatus: 'high'
        },
        {
            id: 'cash_2',
            name: 'کاغذ A3 - 80 گرم - سفید',
            price: 45000,
            stock: 80,
            stockStatus: 'medium'
        },
        {
            id: 'cash_3',
            name: 'کاغذ A4 رنگی - 120 گرم - آبی',
            price: 35000,
            stock: 45,
            stockStatus: 'low'
        },
        {
            id: 'cash_4',
            name: 'کاغذ A4 گلاسه - 150 گرم - سفید',
            price: 55000,
            stock: 60,
            stockStatus: 'medium'
        }
    ],
    credit: [
        {
            id: 'credit_1',
            name: 'کاغذ A4 نسیه - 80 گرم - سفید',
            price: 28000,
            stock: 120,
            stockStatus: 'medium'
        },
        {
            id: 'credit_2',
            name: 'کاغذ A3 نسیه - 80 گرم - سفید',
            price: 50000,
            stock: 50,
            stockStatus: 'low'
        },
        {
            id: 'credit_3',
            name: 'کاغذ A4 رنگی نسیه - 120 گرم - قرمز',
            price: 38000,
            stock: 30,
            stockStatus: 'low'
        }
    ]
};

// Current product database (loaded from admin settings or defaults)
let productDatabase = {
    cash: [],
    credit: []
};

// Selected products storage
let selectedProducts = [];

/**
 * Load admin-configured products or use defaults
 */
function loadProductDatabase() {
    try {
        // Try to load from localStorage (admin configured)
        const adminProducts = localStorage.getItem('adminProducts');
        if (adminProducts) {
            const parsedProducts = JSON.parse(adminProducts);
            if (parsedProducts.cash && parsedProducts.credit) {
                productDatabase = parsedProducts;
                console.log('محصولات از تنظیمات ادمین بارگذاری شد');
                return;
            }
        }

        // Try to load from mainPageContent for backward compatibility
        const mainPageContent = localStorage.getItem('mainPageContent');
        if (mainPageContent) {
            const content = JSON.parse(mainPageContent);
            // Generate products based on main page content
            generateProductsFromMainContent(content);
            console.log('محصولات از محتوای صفحه اصلی تولید شد');
            return;
        }

        // Fallback to default products
        productDatabase = JSON.parse(JSON.stringify(defaultProductDatabase));
        console.log('محصولات پیش‌فرض بارگذاری شد');

    } catch (error) {
        console.error('خطا در بارگذاری محصولات:', error);
        productDatabase = JSON.parse(JSON.stringify(defaultProductDatabase));
    }
}

/**
 * Generate products from main page content
 */
function generateProductsFromMainContent(content) {
    const cashPrice = content.cashPrice || 25000;
    const creditPrice = content.creditPrice || 28000;
    const cashStock = parseInt(content.cashStock) || 150;
    const creditStock = parseInt(content.creditStock) || 120;

    productDatabase.cash = [
        {
            id: 'cash_main',
            name: 'کاغذ A4 - 80 گرم - سفید',
            price: cashPrice,
            stock: cashStock,
            stockStatus: cashStock > 100 ? 'high' : cashStock > 50 ? 'medium' : 'low'
        }
    ];

    productDatabase.credit = [
        {
            id: 'credit_main',
            name: 'کاغذ A4 نسیه - 80 گرم - سفید',
            price: creditPrice,
            stock: creditStock,
            stockStatus: creditStock > 100 ? 'high' : creditStock > 50 ? 'medium' : 'low'
        }
    ];
}

/**
 * Initialize the shopping page
 */
function initializePage() {
    // Load product database first
    loadProductDatabase();

    // Load user information
    loadUserInfo();

    // Load products into tables
    loadProducts();

    // Add touch feedback for mobile
    addTouchFeedback();

    // Check working hours
    checkWorkingHours();

    console.log('صفحه خرید بارگذاری شد');
}

/**
 * Load user information
 */
function loadUserInfo() {
    const userName = sessionStorage.getItem('userName') || 'کاربر';
    const userNameElement = document.getElementById('userName');
    if (userNameElement) {
        userNameElement.textContent = userName;
    }
}

/**
 * Load products into tables
 */
function loadProducts() {
    // Ensure product database is loaded
    if (!productDatabase.cash.length && !productDatabase.credit.length) {
        loadProductDatabase();
    }

    // Load cash products
    if (productDatabase.cash.length > 0) {
        loadTableProducts('cash', productDatabase.cash);
    } else {
        showEmptyTableMessage('cashTableBody', 'نقدی');
    }

    // Load credit products
    if (productDatabase.credit.length > 0) {
        loadTableProducts('credit', productDatabase.credit);
    } else {
        showEmptyTableMessage('creditTableBody', 'نسیه');
    }
}

/**
 * Show empty table message
 */
function showEmptyTableMessage(tableBodyId, type) {
    const tableBody = document.getElementById(tableBodyId);
    if (tableBody) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="4" class="empty-message">
                    <div class="empty-content">
                        <div class="empty-icon">📦</div>
                        <div class="empty-text">هیچ محصول ${type} موجود نیست</div>
                        <div class="empty-subtext">ادمین هنوز محصولی اضافه نکرده است</div>
                    </div>
                </td>
            </tr>
        `;
    }
}

/**
 * Load products into a specific table
 */
function loadTableProducts(tableType, products) {
    const tableBodyId = tableType === 'cash' ? 'cashTableBody' : 'creditTableBody';
    const tableBody = document.getElementById(tableBodyId);

    if (!tableBody) {
        console.error(`Table not found: ${tableBodyId}`);
        return;
    }

    // Clear existing content
    tableBody.innerHTML = '';

    // Add each product as a row
    products.forEach(product => {
        const row = createProductRow(product, tableType);
        tableBody.appendChild(row);
    });
}

/**
 * Create a product row for the table
 */
function createProductRow(product, tableType) {
    const row = document.createElement('tr');
    row.className = 'product-row';
    row.dataset.productId = product.id;

    // Get stock status class
    const stockClass = getStockStatusClass(product.stockStatus);

    row.innerHTML = `
        <td class="product-name-cell">
            <span class="product-name">${product.name}</span>
        </td>
        <td class="price-cell">
            <span class="price-value">${formatPrice(product.price)}</span>
        </td>
        <td class="stock-cell">
            <span class="stock-value ${stockClass}">${product.stock} کیلو</span>
        </td>
        <td class="action-cell">
            <div class="quantity-controls">
                <button class="quantity-btn minus-btn" onclick="updateQuantity('${product.id}', -1)">-</button>
                <input type="number" class="quantity-input" id="quantity_${product.id}" value="1" min="1" max="${product.stock}" onchange="updateQuantity('${product.id}', this.value)">
                <button class="quantity-btn plus-btn" onclick="updateQuantity('${product.id}', 1)">+</button>
            </div>
            <button class="select-btn" id="btn_${product.id}" onclick="toggleProductSelection('${product.id}', '${tableType}')">
                <span class="btn-icon">➕</span>
                <span class="btn-text">انتخاب</span>
            </button>
        </td>
    `;

    return row;
}

/**
 * Get stock status CSS class
 */
function getStockStatusClass(stockStatus) {
    switch (stockStatus) {
        case 'high': return 'stock-high';
        case 'medium': return 'stock-medium';
        case 'low': return 'stock-low';
        default: return '';
    }
}

/**
 * Format price with Persian numbers
 */
function formatPrice(price) {
    if (typeof convertToPersianNumbers === 'function') {
        return convertToPersianNumbers(new Intl.NumberFormat('fa-IR').format(price)) + ' تومان';
    }
    return new Intl.NumberFormat('fa-IR').format(price) + ' تومان';
}

/**
 * Find product by ID
 */
function findProduct(productId) {
    // Search in cash products
    let product = productDatabase.cash.find(p => p.id === productId);
    if (product) return product;

    // Search in credit products
    product = productDatabase.credit.find(p => p.id === productId);
    return product;
}

/**
 * Update quantity for a product
 */
function updateQuantity(productId, changeOrValue) {
    const quantityInput = document.getElementById(`quantity_${productId}`);
    if (!quantityInput) return;

    const product = findProduct(productId);
    if (!product) return;

    let newQuantity;

    // If it's a change (+1 or -1), calculate new value
    if (typeof changeOrValue === 'number' && (changeOrValue === 1 || changeOrValue === -1)) {
        newQuantity = parseInt(quantityInput.value) + changeOrValue;
    } else {
        // Direct value assignment
        newQuantity = parseInt(changeOrValue) || 1;
    }

    // Validate quantity bounds
    if (newQuantity < 1) {
        newQuantity = 1;
    } else if (newQuantity > product.stock) {
        newQuantity = product.stock;
        showMessage(`حداکثر موجودی این محصول ${product.stock} کیلو است`, 'warning');
    }

    // Update input value
    quantityInput.value = newQuantity;

    // If product is selected, update the selected quantity
    const selectedProduct = selectedProducts.find(p => p.id === productId);
    if (selectedProduct) {
        selectedProduct.quantity = newQuantity;
        updateSelectedProductsDisplay();
    }
}

/**
 * Toggle product selection
 */
function toggleProductSelection(productId, tableType) {
    const product = findProduct(productId);
    if (!product) {
        showMessage('محصول یافت نشد', 'error');
        return;
    }

    const quantityInput = document.getElementById(`quantity_${productId}`);
    const quantity = quantityInput ? parseInt(quantityInput.value) || 1 : 1;

    // Check if already selected
    const existingIndex = selectedProducts.findIndex(p => p.id === productId);

    if (existingIndex !== -1) {
        // Remove from selection
        selectedProducts.splice(existingIndex, 1);
        updateButtonState(productId, false);
        showMessage('محصول از سبد خرید حذف شد', 'info');
    } else {
        // Add to selection
        if (quantity > product.stock) {
            showMessage(`موجودی کافی نیست. حداکثر ${product.stock} کیلو`, 'error');
            return;
        }

        const selectedProduct = {
            ...product,
            quantity: quantity,
            tableType: tableType,
            totalPrice: product.price * quantity
        };

        selectedProducts.push(selectedProduct);
        updateButtonState(productId, true);
        showMessage('محصول به سبد خرید اضافه شد', 'success');
    }

    updateSelectedProductsDisplay();
}

/**
 * Update button state (selected/unselected)
 */
function updateButtonState(productId, isSelected) {
    const button = document.getElementById(`btn_${productId}`);
    if (button) {
        const icon = button.querySelector('.btn-icon');
        const text = button.querySelector('.btn-text');

        if (isSelected) {
            button.classList.add('selected');
            if (icon) icon.textContent = '✅';
            if (text) text.textContent = 'انتخاب شده';
        } else {
            button.classList.remove('selected');
            if (icon) icon.textContent = '➕';
            if (text) text.textContent = 'انتخاب';
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

    let totalAmount = 0;

    const productsHTML = selectedProducts.map(product => {
        const itemTotal = product.price * product.quantity;
        totalAmount += itemTotal;

        return `
            <div class="selected-item" data-product-id="${product.id}">
                <div class="item-info">
                    <div class="item-name">${product.name}</div>
                    <div class="item-pricing">
                        <span class="unit-price">${formatPrice(product.price)}</span>
                        <span class="quantity">× ${product.quantity} کیلو</span>
                        <span class="total-price">${formatPrice(itemTotal)}</span>
                    </div>
                </div>
                <div class="item-type-badge ${product.tableType}-badge">
                    ${product.tableType === 'cash' ? 'نقدی' : 'نسیه'}
                </div>
                <button class="remove-item-btn" onclick="removeSelectedProduct('${product.id}')">
                    <span class="remove-icon">🗑️</span>
                </button>
            </div>
        `;
    }).join('');

    container.innerHTML = `
        <div class="selected-products-list">
            ${productsHTML}
        </div>
        <div class="order-summary">
            <div class="summary-row total-row">
                <span class="summary-label">مبلغ کل:</span>
                <span class="summary-value final-value">${formatPrice(totalAmount)}</span>
            </div>
        </div>
    `;
}

/**
 * Remove selected product
 */
function removeSelectedProduct(productId) {
    const index = selectedProducts.findIndex(p => p.id === productId);
    if (index !== -1) {
        selectedProducts.splice(index, 1);
        updateButtonState(productId, false);
        updateSelectedProductsDisplay();
        showMessage('محصول از سبد خرید حذف شد', 'info');
    }
}

/**
 * Clear all selections
 */
function clearSelection() {
    if (selectedProducts.length === 0) {
        showMessage('سبد خرید خالی است', 'info');
        return;
    }

    // Update all button states
    selectedProducts.forEach(product => {
        updateButtonState(product.id, false);
    });

    // Clear selections
    selectedProducts = [];
    updateSelectedProductsDisplay();
    showMessage('تمام انتخاب‌ها پاک شد', 'success');
}

/**
 * Proceed to checkout
 */
function proceedToCheckout() {
    if (selectedProducts.length === 0) {
        showMessage('لطفاً حداقل یک محصول انتخاب کنید', 'error');
        return;
    }

    // Calculate totals
    let totalAmount = 0;
    selectedProducts.forEach(product => {
        totalAmount += product.price * product.quantity;
    });

    // Prepare order data (without discount)
    const orderData = {
        products: selectedProducts,
        summary: {
            totalAmount: totalAmount,
            finalAmount: totalAmount, // No discount applied
            itemCount: selectedProducts.length,
            totalQuantity: selectedProducts.reduce((sum, product) => sum + product.quantity, 0)
        },
        orderDate: new Date().toISOString(),
        orderTime: new Date().toLocaleTimeString('fa-IR'),
        customerInfo: {
            name: sessionStorage.getItem('userName') || 'کاربر',
            phone: sessionStorage.getItem('userPhone') || ''
        }
    };

    // Store order data in session storage
    sessionStorage.setItem('currentOrder', JSON.stringify(orderData));

    // Show loading message
    showMessage('در حال انتقال به صفحه پرداخت...', 'success');

    // Redirect to payment page
    setTimeout(() => {
        window.location.href = '../Payment/payment.html';
    }, 1500);
}

/**
 * Logout user
 */
function logout() {
    // Clear session data
    sessionStorage.removeItem('isLoggedIn');
    sessionStorage.removeItem('userPhone');
    sessionStorage.removeItem('userName');
    sessionStorage.removeItem('loginTime');
    sessionStorage.removeItem('isVerified');
    sessionStorage.removeItem('currentOrder');

    showMessage('خروج با موفقیت انجام شد', 'success');

    // Redirect to main page
    setTimeout(() => {
        window.location.href = '../Index/index.html';
    }, 1500);
}

/**
 * Show message to user
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

    // Get color based on type
    let backgroundColor;
    switch (type) {
        case 'success':
            backgroundColor = '#28a745';
            break;
        case 'error':
            backgroundColor = '#dc3545';
            break;
        case 'warning':
            backgroundColor = '#ffc107';
            break;
        default:
            backgroundColor = '#007bff';
    }

    // Add styles
    messageDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        left: 20px;
        z-index: 1000;
        background: ${backgroundColor};
        color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        font-family: 'Vazirmatn', Tahoma, Arial, sans-serif;
        font-size: 1.1rem;
        font-weight: 600;
        text-align: center;
        animation: slideInDown 0.3s ease;
    `;

    // Add animation keyframes if not already added
    if (!document.querySelector('#message-animation-styles')) {
        const style = document.createElement('style');
        style.id = 'message-animation-styles';
        style.textContent = `
            @keyframes slideInDown {
                from {
                    transform: translateY(-100px);
                    opacity: 0;
                }
                to {
                    transform: translateY(0);
                    opacity: 1;
                }
            }
            
            .message-close {
                background: none;
                border: none;
                color: white;
                font-size: 1.5rem;
                cursor: pointer;
                margin-right: 10px;
                padding: 0;
                width: 30px;
                height: 30px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
                transition: background-color 0.3s ease;
            }
            
            .message-close:hover {
                background-color: rgba(255,255,255,0.2);
            }
            
            .message-content {
                display: flex;
                align-items: center;
                justify-content: space-between;
            }
            
            .message-text {
                flex: 1;
            }
        `;
        document.head.appendChild(style);
    }

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
    const interactiveElements = document.querySelectorAll('.select-btn, .quantity-btn, .action-btn');

    interactiveElements.forEach(element => {
        element.addEventListener('touchstart', function (e) {
            this.style.transform = 'scale(0.95)';
        });

        element.addEventListener('touchend', function (e) {
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
        });
    });
}

/**
 * Check working hours and redirect if necessary
 */
function checkWorkingHours() {
    const saved = localStorage.getItem('workingHours');

    if (!saved) {
        // No working hours set, allow access
        return true;
    }

    try {
        const workingHours = JSON.parse(saved);

        if (!workingHours.isActive) {
            showMessage('سایت در حال حاضر غیرفعال است', 'error');
            setTimeout(() => {
                window.location.href = '../Index/index.html';
            }, 2000);
            return false;
        }

        const now = new Date();
        const currentHour = now.getHours();
        const currentMinute = now.getMinutes();
        const currentTime = currentHour * 60 + currentMinute;

        const startTime = workingHours.startHour * 60 + workingHours.startMinute;
        const endTime = workingHours.endHour * 60 + workingHours.endMinute;

        if (currentTime < startTime || currentTime > endTime) {
            showMessage('خارج از ساعت کاری هستیم', 'warning');
            setTimeout(() => {
                window.location.href = '../Index/index.html';
            }, 2000);
            return false;
        }

        return true;

    } catch (error) {
        console.error('خطا در بررسی ساعت کاری:', error);
        return true; // Allow access if there's an error
    }
}

// Initialize page when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    initializePage();
});

// Initialize page when window is loaded
window.addEventListener('load', function () {
    // Double check initialization
    if (productDatabase.cash.length === 0 && productDatabase.credit.length === 0) {
        initializePage();
    }
});

console.log('Shopping page script loaded successfully!');