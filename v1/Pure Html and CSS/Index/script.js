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
// Load main page content from localStorage
function loadMainPageContent() {
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

function checkWorkingHoursAndLoadPage() {
    const saved = localStorage.getItem('workingHours');
    if (!saved) {
        // اگر تنظیمی وجود نداشت، فرض کنیم سیستم غیرفعال است
        window.location.href = 'closed.html';
        return;
    }

    const workingHours = JSON.parse(saved);

    // اگر ادمین سیستم را غیرفعال کرده باشد
    if (!workingHours.isActive) {
        window.location.href = 'closed.html';
        return;
    }

    // بررسی ساعت ایران
    const iranTime = getIranTimeManual();
    const currentTime = iranTime.hour * 60 + iranTime.minute;

    const startTime = Number(workingHours.startHour) * 60 + Number(workingHours.startMinute);
    const endTime = Number(workingHours.endHour) * 60 + Number(workingHours.endMinute);

    // بررسی اینکه آیا داخل ساعت کاری هست یا نه
    const isOpen = currentTime >= startTime && currentTime <= endTime;

    if (!isOpen) {
        window.location.href = 'closed.html';
    } else {
        // ادامه‌ی بارگذاری صفحه اصلی
        loadMainPageContent();
    }
}

// اجرای چک در هنگام بارگذاری
window.addEventListener('load', checkWorkingHoursAndLoadPage);
