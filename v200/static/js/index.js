// Product selection tracking
let selectedItems = {
    cash: 0,
    credit: 0
};

let MAX_TOTAL_SELECTION = 6; // Default value, will be updated from API

// Fetch working hours configuration to get dynamic limit
async function fetchWorkingHoursConfig() {
    try {
        const response = await fetch('/core/api/working-hours-config/');
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                MAX_TOTAL_SELECTION = data.max_selection_limit;
                console.log(`🔢 Max selection limit updated to: ${MAX_TOTAL_SELECTION}`);
            }
        }
    } catch (error) {
        console.warn('⚠️ Could not fetch working hours config, using default limit:', error);
        // Keep default value of 6
    }
}

// Initialize the page
document.addEventListener('DOMContentLoaded', function () {
    // Fetch working hours configuration first
    fetchWorkingHoursConfig().then(() => {
        initializeSelectionButtons();
        updateSelectionCount('cash');
        updateSelectionCount('credit');
        updateProductCounts();
        // Add row click functionality
        const stockRows = document.querySelectorAll('.stock-row');
        stockRows.forEach(row => {
            row.addEventListener('click', function (e) {
                if (!e.target.closest('.quantity-controls')) {
                    const plusBtn = this.querySelector('.plus-btn');
                    if (plusBtn) {
                        handleQuantityChange(plusBtn);
                    }
                }
            });
        });
    });
});

// Toggle mobile menu
function toggleMenu() {
    const navList = document.getElementById('navbarMenu');
    navList.classList.toggle('show');
}

// Custom Popup System
function createPopup(message, type = 'info', title = '', duration = 3000) {
    const existingPopup = document.querySelector('.popup-overlay');
    if (existingPopup) {
        existingPopup.remove();
    }
    const popupConfig = {
        success: { title: title || 'موفقیت!', icon: '✅' },
        error: { title: title || 'خطا!', icon: '❌' },
        warning: { title: title || 'هشدار!', icon: '⚠️' },
        info: { title: title || 'اطلاع!', icon: 'ℹ️' }
    };
    const config = popupConfig[type] || popupConfig.info;
    const popupHTML = `
        <div class="popup-overlay" id="customPopup">
            <div class="popup-container ${type}">
                <button class="popup-close" onclick="closePopup()">×</button>
                <div class="popup-icon">${config.icon}</div>
                <div class="popup-title">${config.title}</div>
                <div class="popup-message">${message}</div>
                <div class="popup-progress">
                    <div class="popup-progress-bar" id="progressBar"></div>
                </div>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', popupHTML);
    const popup = document.getElementById('customPopup');
    setTimeout(() => { popup.classList.add('show'); }, 10);
    const progressBar = document.getElementById('progressBar');
    setTimeout(() => { progressBar.style.width = '0%'; }, 100);
    setTimeout(() => { closePopup(); }, duration);
    return popup;
}
function closePopup() {
    const popup = document.querySelector('.popup-overlay');
    if (popup) {
        popup.classList.remove('show');
        setTimeout(() => { popup.remove(); }, 300);
    }
}
function showAlert(message, type = 'info', title = '') {
    return createPopup(message, type, title, 3000);
}
// Product selection functions
function initializeSelectionButtons() {
    const selectionButtons = document.querySelectorAll('.selection-btn');
    selectionButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            handleSelectionButtonClick(this);
        });
    });
    const checkboxes = document.querySelectorAll('.stock-checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function () {
            handleCheckboxChange(this);
        });
    });
}
function handleSelectionButtonClick(button) {
    const section = button.dataset.section;
    const row = button.closest('.stock-row');
    const checkbox = row.querySelector('.stock-checkbox');
    if (button.classList.contains('selected')) {
        button.classList.remove('selected');
        button.querySelector('.selection-icon').textContent = '⭕';
        button.querySelector('span:last-child').textContent = 'انتخاب';
        checkbox.checked = false;
        selectedItems[section]--;
        row.classList.remove('selected');
        updateSelectionCount(section);
        return;
    }
    if (selectedItems[section] >= MAX_TOTAL_SELECTION) {
        showAlert(`حداکثر ${MAX_TOTAL_SELECTION} مورد قابل انتخاب است!`, 'warning');
        return;
    }
    // Directly select the product (no confirmation popup)
    button.classList.add('selected');
    button.querySelector('.selection-icon').textContent = '✅';
    button.querySelector('span:last-child').textContent = 'انتخاب شده';
    checkbox.checked = true;
    selectedItems[section]++;
    row.classList.add('selected');
    updateSelectionCount(section);
}
function handleCheckboxChange(checkbox) {
    const section = checkbox.dataset.section;
    const row = checkbox.closest('.stock-row');
    const button = row.querySelector('.selection-btn');
    if (checkbox.checked) {
        if (selectedItems[section] >= MAX_TOTAL_SELECTION) {
            checkbox.checked = false;
            showAlert(`حداکثر ${MAX_TOTAL_SELECTION} مورد قابل انتخاب است!`, 'warning');
            return;
        }
        button.classList.add('selected');
        button.querySelector('.selection-icon').textContent = '✅';
        button.querySelector('span:last-child').textContent = 'انتخاب شده';
        selectedItems[section]++;
        row.classList.add('selected');
    } else {
        button.classList.remove('selected');
        button.querySelector('.selection-icon').textContent = '⭕';
        button.querySelector('span:last-child').textContent = 'انتخاب';
        selectedItems[section]--;
        row.classList.remove('selected');
    }
    updateSelectionCount(section);
}
function updateSelectionCount(section) {
    const countElement = document.getElementById(section + 'SelectedCount');
    const purchaseBtn = document.getElementById(section + 'PurchaseBtn');
    if (countElement) {
        countElement.textContent = selectedItems[section];
    }
    if (purchaseBtn) {
        if (selectedItems[section] > 0) {
            purchaseBtn.disabled = false;
            purchaseBtn.classList.remove('disabled');
        } else {
            purchaseBtn.disabled = true;
            purchaseBtn.classList.add('disabled');
        }
    }
}
function updateProductCounts() {
    const cashRows = document.querySelectorAll('#cashStockTable .stock-row');
    const cashCount = cashRows.length;
    const cashTotalElement = document.getElementById('cashTotalCount');
    if (cashTotalElement) {
        cashTotalElement.textContent = cashCount;
    }
    const creditRows = document.querySelectorAll('#creditStockTable .stock-row');
    const creditCount = creditRows.length;
    const creditTotalElement = document.getElementById('creditTotalCount');
    if (creditTotalElement) {
        creditTotalElement.textContent = creditCount;
    }
}
function getTotalSelectedProducts() {
    return selectedItems.cash + selectedItems.credit;
}
// Purchase functions
function handleCashPurchase() {
    if (getTotalSelectedProducts() === 0) {
        showAlert('لطفا حداقل یک مورد را انتخاب کنید', 'error', 'انتخاب محصول');
        return;
    }
    // Save selected products and redirect with payment type Cash
    saveSelectedProductsAndRedirect('Cash');
}
function handleCreditPurchase() {
    if (getTotalSelectedProducts() === 0) {
        showAlert('لطفا حداقل یک مورد را انتخاب کنید', 'error', 'انتخاب محصول');
        return;
    }
    // Save selected products and redirect with payment type Terms
    saveSelectedProductsAndRedirect('Terms');
}
function saveSelectedProductsAndRedirect(paymentType) {
    let selected = [];
    document.querySelectorAll('.stock-row').forEach(row => {
        const checkbox = row.querySelector('.stock-checkbox');
        if (checkbox && checkbox.checked) {
            selected.push({
                product_id: row.getAttribute('data-product-id'),
                quantity: 1 // Default quantity for checkbox selection
            });
        }
    });
    if (selected.length === 0) {
        showAlert('لطفا حداقل یک مورد را انتخاب کنید', 'error', 'انتخاب محصول');
        return;
    }
    // Show loading state
    const purchaseBtns = document.querySelectorAll('.purchase-btn');
    purchaseBtns.forEach(btn => {
        btn.disabled = true;
        btn.innerHTML = '<span class="loading">در حال پردازش...</span>';
    });
    // Send to server with AJAX
    fetch('/core/save-selected-products/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({selected_products: selected})
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Network response was not ok');
        }
    })
    .then(data => {
        showAlert('انتخاب‌های شما با موفقیت ذخیره شد', 'success', 'موفقیت');
        setTimeout(() => {
            window.location.href = `/core/selected-products/?default_payment=${paymentType}`;
        }, 1000);
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('خطا در ذخیره انتخاب‌ها. لطفاً دوباره تلاش کنید.', 'error', 'خطا');
        // Reset button states
        purchaseBtns.forEach(btn => {
            btn.disabled = false;
            if (btn.classList.contains('cash-btn')) {
                btn.innerHTML = '<span class="btn-icon">💰</span><span class="btn-text">خرید نقدی</span>';
            } else if (btn.classList.contains('credit-btn')) {
                btn.innerHTML = '<span class="btn-icon">📋</span><span class="btn-text">خرید نسیه</span>';
            }
        });
    });
}
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
// Quantity management functions (if using quantity inputs)
function handleQuantityChange(button) {
    const action = button.dataset.action;
    const input = button.parentElement.querySelector('.qty-input');
    const section = input.dataset.section;
    const row = input.closest('.stock-row');
    let currentValue = parseInt(input.value) || 0;
    if (action === 'plus') {
        if (canIncreaseQuantity(section)) {
            currentValue++;
        } else {
            showAlert(`حداکثر ${MAX_TOTAL_SELECTION} محصول می‌توانید انتخاب کنید`, 'warning', 'محدودیت انتخاب');
            return;
        }
    } else if (action === 'minus' && currentValue > 0) {
        currentValue--;
    }
    input.value = currentValue;
    input.classList.add('updated');
    setTimeout(() => {
        input.classList.remove('updated');
    }, 300);
    updateRowSelection(row, section, currentValue);
}
function handleQuantityInputChange(input) {
    let value = parseInt(input.value);
    if (isNaN(value) || value < 0) {
        value = 0;
    }
    const otherInputs = Array.from(document.querySelectorAll('.qty-input')).filter(i => i !== input);
    let othersTotal = otherInputs.reduce((sum, i) => sum + (parseInt(i.value) || 0), 0);
    if (value + othersTotal > MAX_TOTAL_SELECTION) {
        value = Math.max(0, MAX_TOTAL_SELECTION - othersTotal);
        showAlert(`حداکثر ${MAX_TOTAL_SELECTION} محصول می‌توانید انتخاب کنید`, 'warning', 'محدودیت انتخاب');
    }
    input.value = value;
    input.classList.add('updated');
    setTimeout(() => {
        input.classList.remove('updated');
    }, 300);
    const section = input.dataset.section;
    const row = input.closest('.stock-row');
    updateRowSelection(row, section, value);
}
function updateRowSelection(row, section, quantity) {
    if (quantity > 0) {
        row.classList.add('selected');
    } else {
        row.classList.remove('selected');
    }
    updateTotalSelectedCount(section);
}
function updateTotalSelectedCount(section) {
    const inputs = document.querySelectorAll(`[data-section="${section}"] .qty-input`);
    let totalSelected = 0;
    inputs.forEach(input => {
        const quantity = parseInt(input.value) || 0;
        if (quantity > 0) {
            totalSelected++;
        }
    });
    selectedItems[section] = totalSelected;
    updateSelectionCount(section);
}
function canIncreaseQuantity(section) {
    const currentTotal = getTotalSelectedProducts();
    return currentTotal < MAX_TOTAL_SELECTION;
}

// View order details function
function viewOrderDetails(orderId) {
    // Redirect to order detail page
    window.location.href = `/core/order/${orderId}/`;
}
// Accessibility improvements
document.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && e.target.classList.contains('purchase-btn')) {
        e.target.click();
    }
});
document.addEventListener('DOMContentLoaded', function () {
    const focusableElements = document.querySelectorAll('.purchase-btn, .refresh-btn, .social-link, .selection-btn');
    focusableElements.forEach(element => {
        element.addEventListener('focus', function () {
            this.style.outline = '3px solid #3498db';
            this.style.outlineOffset = '2px';
        });
        element.addEventListener('blur', function () {
            this.style.outline = 'none';
        });
    });
});
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}); 