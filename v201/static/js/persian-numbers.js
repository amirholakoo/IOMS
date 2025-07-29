/**
 * 🔢 Persian Number Normalization Utility - HomayOMS
 * 📱 تبدیل خودکار اعداد فارسی به انگلیسی در فرم‌ها
 * 🎯 پشتیبانی از تمام فیلدهای عددی در پروژه
 */

(function() {
    'use strict';
    
    // نگاشت اعداد فارسی به انگلیسی
    const persianToEnglishMap = {
        '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
        '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9'
    };
    
    // نگاشت اعداد انگلیسی به فارسی (برای نمایش)
    const englishToPersianMap = {
        '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
        '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'
    };
    
    /**
     * تبدیل اعداد فارسی به انگلیسی
     * @param {string} input - ورودی حاوی اعداد فارسی
     * @returns {string} - خروجی با اعداد انگلیسی
     */
    function normalizePersianNumbers(input) {
        if (!input) return input;
        
        return input.toString().replace(/[۰-۹]/g, function(digit) {
            return persianToEnglishMap[digit] || digit;
        });
    }
    
    /**
     * تبدیل اعداد انگلیسی به فارسی (برای نمایش)
     * @param {string} input - ورودی حاوی اعداد انگلیسی
     * @returns {string} - خروجی با اعداد فارسی
     */
    function convertToPersianNumbers(input) {
        if (!input) return input;
        
        return input.toString().replace(/[0-9]/g, function(digit) {
            return englishToPersianMap[digit] || digit;
        });
    }
    
    /**
     * اعتبارسنجی شماره تلفن
     * @param {string} phone - شماره تلفن
     * @returns {boolean} - معتبر یا نامعتبر
     */
    function validatePhoneNumber(phone) {
        const normalized = normalizePersianNumbers(phone);
        const phoneRegex = /^09\d{9}$/;
        return phoneRegex.test(normalized);
    }
    
    /**
     * اعتبارسنجی کد پستی
     * @param {string} postcode - کد پستی
     * @returns {boolean} - معتبر یا نامعتبر
     */
    function validatePostcode(postcode) {
        const normalized = normalizePersianNumbers(postcode);
        return /^\d{10}$/.test(normalized);
    }
    
    /**
     * اعتبارسنجی شناسه ملی
     * @param {string} nationalId - شناسه ملی
     * @returns {boolean} - معتبر یا نامعتبر
     */
    function validateNationalId(nationalId) {
        const normalized = normalizePersianNumbers(nationalId);
        return /^\d{10}$/.test(normalized);
    }
    
    /**
     * اعتبارسنجی کد اقتصادی
     * @param {string} economicCode - کد اقتصادی
     * @returns {boolean} - معتبر یا نامعتبر
     */
    function validateEconomicCode(economicCode) {
        const normalized = normalizePersianNumbers(economicCode);
        return /^\d+$/.test(normalized);
    }
    
    /**
     * اعتبارسنجی اعداد (قیمت، تعداد، ابعاد)
     * @param {string} number - عدد
     * @returns {boolean} - معتبر یا نامعتبر
     */
    function validateNumber(number) {
        const normalized = normalizePersianNumbers(number);
        return /^\d+(\.\d+)?$/.test(normalized);
    }
    
    /**
     * اضافه کردن event listener برای تبدیل خودکار اعداد
     * @param {HTMLElement} element - المان HTML
     */
    function addPersianNumberListener(element) {
        const inputType = element.getAttribute('data-persian-type') || 'number';
        
        // تبدیل در هنگام تایپ
        element.addEventListener('input', function(e) {
            const originalValue = e.target.value;
            const normalizedValue = normalizePersianNumbers(originalValue);
            
            // اگر مقدار تغییر کرده، آن را به‌روزرسانی کن
            if (originalValue !== normalizedValue) {
                e.target.value = normalizedValue;
            }
        });
        
        // تبدیل در هنگام blur (خروج از فیلد)
        element.addEventListener('blur', function(e) {
            const value = e.target.value;
            if (value) {
                const normalized = normalizePersianNumbers(value);
                e.target.value = normalized;
                
                // اعتبارسنجی بر اساس نوع فیلد
                let isValid = true;
                let errorMessage = '';
                
                switch (inputType) {
                    case 'phone':
                        isValid = validatePhoneNumber(normalized);
                        errorMessage = 'شماره تلفن باید با 09 شروع شده و 11 رقم باشد';
                        break;
                    case 'postcode':
                        isValid = validatePostcode(normalized);
                        errorMessage = 'کد پستی باید دقیقاً 10 رقم باشد';
                        break;
                    case 'national_id':
                        isValid = validateNationalId(normalized);
                        errorMessage = 'شناسه ملی باید 10 رقم باشد';
                        break;
                    case 'economic_code':
                        isValid = validateEconomicCode(normalized);
                        errorMessage = 'کد اقتصادی باید فقط شامل اعداد باشد';
                        break;
                    case 'number':
                    case 'price':
                    case 'quantity':
                    case 'dimension':
                        isValid = validateNumber(normalized);
                        errorMessage = 'فقط اعداد مجاز هستند';
                        break;
                }
                
                // نمایش خطا یا حذف آن
                showFieldError(e.target, isValid, errorMessage);
            }
        });
        
        // تبدیل در هنگام focus (ورود به فیلد)
        element.addEventListener('focus', function(e) {
            // حذف پیام خطا در هنگام ورود به فیلد
            hideFieldError(e.target);
        });
    }
    
    /**
     * نمایش خطای فیلد
     * @param {HTMLElement} element - المان HTML
     * @param {boolean} isValid - معتبر یا نامعتبر
     * @param {string} message - پیام خطا
     */
    function showFieldError(element, isValid, message) {
        // حذف کلاس‌های قبلی
        element.classList.remove('is-valid', 'is-invalid');
        
        // حذف پیام خطای قبلی
        const existingError = element.parentNode.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
        
        if (!isValid) {
            element.classList.add('is-invalid');
            
            // ایجاد پیام خطا
            const errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            errorDiv.textContent = message;
            element.parentNode.appendChild(errorDiv);
        } else {
            element.classList.add('is-valid');
        }
    }
    
    /**
     * حذف خطای فیلد
     * @param {HTMLElement} element - المان HTML
     */
    function hideFieldError(element) {
        element.classList.remove('is-invalid');
        const existingError = element.parentNode.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
    }
    
    /**
     * راه‌اندازی خودکار برای تمام فیلدهای عددی
     */
    function initializePersianNumbers() {
        // فیلدهای شماره تلفن
        document.querySelectorAll('input[type="tel"], input[name*="phone"], input[id*="phone"]').forEach(function(element) {
            element.setAttribute('data-persian-type', 'phone');
            addPersianNumberListener(element);
        });
        
        // فیلدهای کد پستی
        document.querySelectorAll('input[name*="postcode"], input[id*="postcode"]').forEach(function(element) {
            element.setAttribute('data-persian-type', 'postcode');
            addPersianNumberListener(element);
        });
        
        // فیلدهای شناسه ملی
        document.querySelectorAll('input[name*="national_id"], input[id*="national_id"]').forEach(function(element) {
            element.setAttribute('data-persian-type', 'national_id');
            addPersianNumberListener(element);
        });
        
        // فیلدهای کد اقتصادی
        document.querySelectorAll('input[name*="economic_code"], input[id*="economic_code"]').forEach(function(element) {
            element.setAttribute('data-persian-type', 'economic_code');
            addPersianNumberListener(element);
        });
        
        // فیلدهای قیمت
        document.querySelectorAll('input[name*="price"], input[id*="price"]').forEach(function(element) {
            element.setAttribute('data-persian-type', 'price');
            addPersianNumberListener(element);
        });
        
        // فیلدهای تعداد
        document.querySelectorAll('input[name*="quantity"], input[id*="quantity"]').forEach(function(element) {
            element.setAttribute('data-persian-type', 'quantity');
            addPersianNumberListener(element);
        });
        
        // فیلدهای ابعاد (عرض، طول، GSM)
        document.querySelectorAll('input[name*="width"], input[name*="length"], input[name*="gsm"], input[name*="breaks"]').forEach(function(element) {
            element.setAttribute('data-persian-type', 'dimension');
            addPersianNumberListener(element);
        });
        
        // فیلدهای عددی عمومی
        document.querySelectorAll('input[type="number"]').forEach(function(element) {
            if (!element.hasAttribute('data-persian-type')) {
                element.setAttribute('data-persian-type', 'number');
                addPersianNumberListener(element);
            }
        });
    }
    
    // راه‌اندازی در هنگام بارگذاری صفحه
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializePersianNumbers);
    } else {
        initializePersianNumbers();
    }
    
    // راه‌اندازی مجدد برای محتوای داینامیک
    document.addEventListener('DOMContentLoaded', function() {
        // مشاهده تغییرات DOM برای فرم‌های داینامیک
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach(function(node) {
                        if (node.nodeType === 1) { // Element node
                            // بررسی فیلدهای جدید اضافه شده
                            const newInputs = node.querySelectorAll ? node.querySelectorAll('input') : [];
                            newInputs.forEach(function(input) {
                                if (input.type === 'tel' || input.type === 'number' || 
                                    input.name && (input.name.includes('phone') || input.name.includes('price') || 
                                                 input.name.includes('quantity') || input.name.includes('width') ||
                                                 input.name.includes('length') || input.name.includes('gsm'))) {
                                    initializePersianNumbers();
                                }
                            });
                        }
                    });
                }
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    });
    
    // قرار دادن توابع در scope عمومی برای استفاده در جاهای دیگر
    window.PersianNumbers = {
        normalize: normalizePersianNumbers,
        convertToPersian: convertToPersianNumbers,
        validatePhone: validatePhoneNumber,
        validatePostcode: validatePostcode,
        validateNationalId: validateNationalId,
        validateEconomicCode: validateEconomicCode,
        validateNumber: validateNumber,
        initialize: initializePersianNumbers
    };
    
})(); 