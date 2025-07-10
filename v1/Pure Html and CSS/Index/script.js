// Functions for handling purchase button clicks
/* Go to login page */

function goToLogin() {
    window.location.href = 'login.html';
}

/**
 * Check if user is logged in
 * @returns {boolean} - True if logged in
 */
function isUserLoggedIn() {
    const isLoggedIn = sessionStorage.getItem('isLoggedIn');
    const loginTime = sessionStorage.getItem('loginTime');

    if (!isLoggedIn || !loginTime) {
        return false;
    }

    // Check if login is still valid (24 hours)
    const loginDate = new Date(loginTime);
    const now = new Date();
    const hoursDiff = (now - loginDate) / (1000 * 60 * 60);

    return hoursDiff < 24;
}

/**
 * Update login button based on login status
 */
function updateLoginButton() {
    const loginBtn = document.getElementById('loginBtn');
    if (!loginBtn) return;

    if (isUserLoggedIn()) {
        const userName = sessionStorage.getItem('userName') || 'کاربر';
        loginBtn.innerHTML = `
            <span class="btn-icon">👤</span>
            <span class="btn-text">${userName}</span>
        `;
        loginBtn.onclick = logout;
    } else {
        loginBtn.innerHTML = `
            <span class="btn-icon">🔐</span>
            <span class="btn-text">ورود</span>
        `;
        loginBtn.onclick = goToLogin;
    }
}

/**
 * Logout user
 */
function logout() {
    sessionStorage.removeItem('isLoggedIn');
    sessionStorage.removeItem('userPhone');
    sessionStorage.removeItem('userName');
    sessionStorage.removeItem('loginTime');

    showMessage('خروج با موفقیت انجام شد', 'success');
    updateLoginButton();
}

/**
 * Handle cash purchase
 */
function handleCashPurchase() {
    showMessage('در حال هدایت به صفحه خرید...', 'success');
    setTimeout(() => {
        window.location.href = '../Shopping/shopping.html';
    }, 1500);
}

/**
 * Handle credit purchase
 */
function handleCreditPurchase() {
    showMessage('در حال هدایت به صفحه خرید...', 'success');
    setTimeout(() => {
        window.location.href = '../Shopping/shopping.html';
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

    // Add styles
    messageDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        left: 20px;
        z-index: 1000;
        background: ${type === 'success' ? '#27ae60' : type === 'error' ? '#e74c3c' : '#3498db'};
        color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        font-family: 'Vazirmatn', Tahoma, Arial, sans-serif;
        font-size: 1.1rem;
        font-weight: 600;
        text-align: center;
        animation: slideIn 0.3s ease;
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
 * Add loading animation styles
 */
function addLoadingStyles() {
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateY(-100px);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }
        
        .purchase-btn.loading {
            opacity: 0.7;
            pointer-events: none;
        }
        
        .purchase-btn.loading::after {
            content: '';
            position: absolute;
            width: 20px;
            height: 20px;
            border: 3px solid transparent;
            border-top: 3px solid white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
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

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function () {
    addLoadingStyles();

    // Update login button status
    // updateLoginButton();

    // Add touch feedback for mobile devices
    const buttons = document.querySelectorAll('.purchase-btn');
    buttons.forEach(button => {
        button.addEventListener('touchstart', function () {
            this.style.transform = 'scale(0.95)';
        });

        button.addEventListener('touchend', function () {
            this.style.transform = '';
        });
    });

    console.log('Mobile Home Project loaded successfully!');
});

// Prevent double-clicking on buttons
let isProcessing = false;

function preventDoubleClick(func) {
    if (isProcessing) return;

    isProcessing = true;
    func();

    setTimeout(() => {
        isProcessing = false;
    }, 2000);
}

// Working Hours Management
let workingHoursTimer = null;

// Initialize page
function initializePage() {
    checkWorkingHours();
    // Check every 5 minutes
    workingHoursTimer = setInterval(checkWorkingHours, 5 * 60 * 1000);
}

// Check if site should be open
function checkWorkingHours() {
    const saved = localStorage.getItem('workingHours');

    if (!saved) {
        // Default working hours if not set by admin
        showMainContent();
        return;
    }

    const workingHours = JSON.parse(saved);

    if (!workingHours.isActive) {
        showClosedContent();
        return;
    }

    const now = new Date();
    const currentHour = now.getHours();
    const currentMinute = now.getMinutes();
    const currentTime = currentHour * 60 + currentMinute;

    const startTime = workingHours.startHour * 60 + workingHours.startMinute;
    const endTime = workingHours.endHour * 60 + workingHours.endMinute;

    if (currentTime >= startTime && currentTime <= endTime) {
        showMainContent();
    } else {
        showClosedContent();
        updateWorkingHoursDisplay(workingHours);
    }
}

// Show main content
function showMainContent() {
    const mainContent = document.getElementById('mainContent');
    const closedContent = document.getElementById('closedContent');
    const pageSubtitle = document.getElementById('pageSubtitle');
    
    if (mainContent) mainContent.style.display = 'block';
    if (closedContent) closedContent.style.display = 'none';
    if (pageSubtitle) pageSubtitle.textContent = 'قیمت و موجودی';
    
    // Load data from localStorage
    loadMainPageData();
}

// Load main page data from localStorage
function loadMainPageData() {
    const saved = localStorage.getItem('mainPageContent');
    if (saved) {
        const mainPageContent = JSON.parse(saved);

        // Update cash section
        const cashPriceElement = document.getElementById('cashPrice');
        const cashStockElement = document.getElementById('cashStock');

        if (cashPriceElement) {
            cashPriceElement.textContent = new Intl.NumberFormat('fa-IR').format(mainPageContent.cashPrice) + ' تومان';
        }
        if (cashStockElement) {
            cashStockElement.textContent = mainPageContent.cashStock + ' کیلو';
        }

        // Update credit section
        const creditPriceElement = document.getElementById('creditPrice');
        const creditStockElement = document.getElementById('creditStock');

        if (creditPriceElement) {
            creditPriceElement.textContent = new Intl.NumberFormat('fa-IR').format(mainPageContent.creditPrice) + ' تومان';
        }
        if (creditStockElement) {
            creditStockElement.textContent = mainPageContent.creditStock + ' کیلو';
        }
    }
}

// Show closed content
function showClosedContent() {
    const mainContent = document.getElementById('mainContent');
    const closedContent = document.getElementById('closedContent');
    const pageSubtitle = document.getElementById('pageSubtitle');

    if (mainContent) mainContent.style.display = 'none';
    if (closedContent) closedContent.style.display = 'block';
    if (pageSubtitle) pageSubtitle.textContent = 'سایت بسته است';
}

// Update working hours display in closed content
function updateWorkingHoursDisplay(workingHours) {
    const display = document.getElementById('workingHoursDisplay');
    if (display && workingHours) {
        const startTime = `${workingHours.startHour.toString().padStart(2, '0')}:${workingHours.startMinute.toString().padStart(2, '0')}`;
        const endTime = `${workingHours.endHour.toString().padStart(2, '0')}:${workingHours.endMinute.toString().padStart(2, '0')}`;
        display.textContent = `از ${startTime} تا ${endTime}`;
    }
}

// Initialize when page loads
window.addEventListener('load', initializePage);

// Cleanup timer when page unloads
window.addEventListener('beforeunload', function () {
    if (workingHoursTimer) {
        clearInterval(workingHoursTimer);
    }
});
