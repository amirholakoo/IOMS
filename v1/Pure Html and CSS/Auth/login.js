// Login Page JavaScript

// Simulated user database for demo purposes
const userDatabase = {
    '09123456789': { status: 'approved', name: 'احمد محمدی' },
    '09187654321': { status: 'pending', name: 'علی رضایی' },
    '09111111111': { status: 'deactive', name: 'محمد کریمی' },
    '09122222222': { status: 'approved', name: 'حسن احمدی' },
    '09133333333': { status: 'pending', name: 'رضا محمودی' },
    '09144444444': { status: 'deactive', name: 'علی احمدی' },
    '09155555555': { status: 'approved', name: 'محمد رضایی' }
};

/**
 * Handle phone number form submission
 * @param {Event} event - Form submit event
 */
function handlePhoneSubmit(event) {
    event.preventDefault();

    const phoneInput = document.getElementById('phoneNumber');
    const submitBtn = document.getElementById('submitBtn');
    const phoneNumber = phoneInput.value.trim();

    // Validate phone number
    if (!isValidPhoneNumber(phoneNumber)) {
        showInputError(phoneInput, 'شماره تلفن باید با صفر شروع شود و ۱۱ رقم باشد');
        return;
    }

    // Add loading state
    submitBtn.classList.add('loading');
    submitBtn.querySelector('.btn-text').textContent = 'در حال بررسی...';

    // Simulate API call
    setTimeout(() => {
        submitBtn.classList.remove('loading');
        submitBtn.querySelector('.btn-text').textContent = 'ارسال کد تایید';

        // Check user status
        const userStatus = checkUserStatus(phoneNumber);

        if (userStatus === 'approved') {
            // Store phone number in session storage
            sessionStorage.setItem('userPhone', phoneNumber);
            sessionStorage.setItem('userName', userDatabase[phoneNumber]?.name || 'کاربر');

            // Show success message and redirect to verification page
            showMessage('کد تایید برای شما ارسال شد', 'success');
            setTimeout(() => {
                window.location.href = 'verification.html';
            }, 1500);

        } else if (userStatus === 'pending') {
            showMessage('شماره شما در انتظار تایید است. لطفاً با مدیر سیستم تماس بگیرید.', 'error');
            setTimeout(() => {
                window.location.href = '../Index/index.html';
            }, 4000);

        } else if (userStatus === 'deactive') {
            showMessage('حساب شما غیرفعال است. لطفاً با مدیر سیستم تماس بگیرید.', 'error');
            setTimeout(() => {
                window.location.href = '../Index/index.html';
            }, 4000);

        } else {
            showMessage('شماره شما در سیستم ثبت نشده است', 'error');
            setTimeout(() => {
                window.location.href = '../Index/index.html';
            }, 3000);
        }

    }, 2000);
}

/**
 * Validate phone number format
 * @param {string} phoneNumber - Phone number to validate
 * @returns {boolean} - True if valid
 */
function isValidPhoneNumber(phoneNumber) {
    // Check if it's exactly 11 digits and starts with 0
    const phoneRegex = /^0\d{10}$/;
    return phoneRegex.test(phoneNumber);
}

/**
 * Check user status in database
 * @param {string} phoneNumber - Phone number to check
 * @returns {string} - User status (approved, pending, deactive, not_found)
 */
function checkUserStatus(phoneNumber) {
    const user = userDatabase[phoneNumber];
    return user ? user.status : 'not_found';
}

/**
 * Show input error
 * @param {HTMLElement} input - Input element
 * @param {string} message - Error message
 */
function showInputError(input, message) {
    // Remove existing error
    removeInputError(input);

    // Add error class
    input.classList.add('input-error');

    // Create error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;

    // Insert after input container
    const inputContainer = input.closest('.input-group');
    inputContainer.appendChild(errorDiv);

    // Focus on input
    input.focus();
}

/**
 * Remove input error
 * @param {HTMLElement} input - Input element
 */
function removeInputError(input) {
    input.classList.remove('input-error');
    const errorMessage = input.closest('.input-group').querySelector('.error-message');
    if (errorMessage) {
        errorMessage.remove();
    }
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
        
        .submit-btn.loading {
            opacity: 0.7;
            pointer-events: none;
        }
        
        .submit-btn.loading::after {
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

    // Add input validation on blur
    const phoneInput = document.getElementById('phoneNumber');

    phoneInput.addEventListener('blur', function () {
        const phoneNumber = this.value.trim();
        if (phoneNumber && !isValidPhoneNumber(phoneNumber)) {
            showInputError(this, 'شماره تلفن باید با صفر شروع شود و ۱۱ رقم باشد');
        } else {
            removeInputError(this);
        }
    });

    // Add input validation on input
    phoneInput.addEventListener('input', function () {
        // Remove error when user starts typing
        removeInputError(this);

        // Only allow numbers
        this.value = this.value.replace(/[^0-9]/g, '');
    });

    // Add touch feedback for mobile devices
    const submitBtn = document.getElementById('submitBtn');
    submitBtn.addEventListener('touchstart', function () {
        this.style.transform = 'scale(0.95)';
    });

    submitBtn.addEventListener('touchend', function () {
        this.style.transform = '';
    });

    console.log('Login page loaded successfully!');
});

// Prevent double-clicking on submit button
let isSubmitting = false;

function preventDoubleSubmit(func) {
    if (isSubmitting) return;

    isSubmitting = true;
    func();

    setTimeout(() => {
        isSubmitting = false;
    }, 3000);
}

// Update the original function to use double-submit prevention
function handlePhoneSubmit(event) {
    event.preventDefault();

    preventDoubleSubmit(() => {
        const phoneInput = document.getElementById('phoneNumber');
        const submitBtn = document.getElementById('submitBtn');
        const phoneNumber = phoneInput.value.trim();

        // Validate phone number
        if (!isValidPhoneNumber(phoneNumber)) {
            showInputError(phoneInput, 'شماره تلفن باید با صفر شروع شود و ۱۱ رقم باشد');
            return;
        }

        // Add loading state
        submitBtn.classList.add('loading');
        submitBtn.querySelector('.btn-text').textContent = 'در حال بررسی...';

        // Simulate API call
        setTimeout(() => {
            submitBtn.classList.remove('loading');
            submitBtn.querySelector('.btn-text').textContent = 'ارسال کد تایید';

            // Check user status
            const userStatus = checkUserStatus(phoneNumber);

            if (userStatus === 'approved') {
                // Store phone number in session storage
                sessionStorage.setItem('userPhone', phoneNumber);
                sessionStorage.setItem('userName', userDatabase[phoneNumber]?.name || 'کاربر');

                // Show success message and redirect to verification page
                showMessage('کد تایید برای شما ارسال شد', 'success');
                setTimeout(() => {
                    window.location.href = 'verification.html';
                }, 1500);

            } else if (userStatus === 'pending') {
                showMessage('شماره شما در انتظار تایید است. لطفاً با مدیر سیستم تماس بگیرید.', 'error');
                setTimeout(() => {
                    window.location.href = 'index.html';
                }, 4000);

            } else if (userStatus === 'deactive') {
                showMessage('حساب شما غیرفعال است. لطفاً با مدیر سیستم تماس بگیرید.', 'error');
                setTimeout(() => {
                    window.location.href = 'index.html';
                }, 4000);

            } else {
                showMessage('شماره شما در سیستم ثبت نشده است', 'error');
                setTimeout(() => {
                    window.location.href = 'index.html';
                }, 3000);
            }

        }, 2000);
    });
} 
