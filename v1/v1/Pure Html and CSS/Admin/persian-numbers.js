// Persian Numbers Utility for Admin Panel

const PersianNumbers = {
    // Persian digit mapping
    persianDigits: ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'],
    englishDigits: ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],

    // Convert English digits to Persian
    toPersian: function (str) {
        if (!str) return '';
        let result = str.toString();
        for (let i = 0; i < this.englishDigits.length; i++) {
            result = result.replace(new RegExp(this.englishDigits[i], 'g'), this.persianDigits[i]);
        }
        return result;
    },

    // Convert Persian digits to English
    toEnglish: function (str) {
        if (!str) return '';
        let result = str.toString();
        for (let i = 0; i < this.persianDigits.length; i++) {
            result = result.replace(new RegExp(this.persianDigits[i], 'g'), this.englishDigits[i]);
        }
        return result;
    },

    // Format number with Persian digits and thousand separators
    formatNumber: function (num) {
        if (num === null || num === undefined) return '';
        const formatted = num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
        return this.toPersian(formatted);
    },

    // Format price with Persian digits and "تومان" suffix
    formatPrice: function (price) {
        if (price === null || price === undefined) return '';
        const formatted = this.formatNumber(price);
        return formatted + ' تومان';
    },

    // Format stock with Persian digits
    formatStock: function (stock) {
        if (stock === null || stock === undefined) return '';
        return this.toPersian(stock.toString());
    },

    // Format phone number with Persian digits
    formatPhone: function (phone) {
        if (!phone) return '';
        // Add spaces for better readability: 0912 345 6789
        const formatted = phone.replace(/(\d{4})(\d{3})(\d{4})/, '$1 $2 $3');
        return this.toPersian(formatted);
    },

    // Format order ID with Persian digits
    formatOrderId: function (orderId) {
        if (!orderId) return '';
        return this.toPersian(orderId.toString());
    },

    // Format total amount with Persian digits and styling
    formatTotalAmount: function (amount) {
        if (amount === null || amount === undefined) return '';
        const formatted = this.formatNumber(amount);
        return formatted + ' تومان';
    },

    // Format date to Persian
    formatDate: function (dateStr) {
        if (!dateStr) return '';
        const date = new Date(dateStr);
        const year = this.toPersian(date.getFullYear().toString());
        const month = this.toPersian((date.getMonth() + 1).toString().padStart(2, '0'));
        const day = this.toPersian(date.getDate().toString().padStart(2, '0'));
        return `${year}/${month}/${day}`;
    },

    // Format working hours
    formatWorkingHours: function (hour, minute) {
        const formattedHour = this.toPersian(hour.toString().padStart(2, '0'));
        const formattedMinute = this.toPersian(minute.toString().padStart(2, '0'));
        return `${formattedHour}:${formattedMinute}`;
    },

    // Format time (current time)
    formatCurrentTime: function () {
        const now = new Date();
        return this.formatWorkingHours(now.getHours(), now.getMinutes());
    },

    // Get Persian month name
    getPersianMonth: function (monthIndex) {
        const months = [
            'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
            'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
        ];
        return months[monthIndex] || '';
    },

    // Get Persian day name
    getPersianDay: function (dayIndex) {
        const days = [
            'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه', 'شنبه'
        ];
        return days[dayIndex] || '';
    },

    // Format full Persian date with day name
    formatFullPersianDate: function (dateStr) {
        if (!dateStr) return '';
        const date = new Date(dateStr);
        const dayName = this.getPersianDay(date.getDay());
        const day = this.toPersian(date.getDate().toString());
        const month = this.getPersianMonth(date.getMonth());
        const year = this.toPersian(date.getFullYear().toString());
        return `${dayName} ${day} ${month} ${year}`;
    },

    // Convert file size to Persian
    formatFileSize: function (bytes) {
        if (bytes === 0) return this.toPersian('0') + ' بایت';
        const k = 1024;
        const sizes = ['بایت', 'کیلوبایت', 'مگابایت', 'گیگابایت'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        const size = parseFloat((bytes / Math.pow(k, i)).toFixed(2));
        return this.toPersian(size.toString()) + ' ' + sizes[i];
    },

    // Format percentage
    formatPercentage: function (num) {
        if (num === null || num === undefined) return '';
        return this.toPersian(num.toString()) + '%';
    },

    // Validate Persian phone number
    isValidPersianPhone: function (phone) {
        const phoneRegex = /^09[0-9]{9}$/;
        const englishPhone = this.toEnglish(phone.replace(/\s/g, ''));
        return phoneRegex.test(englishPhone);
    },

    // Validate Persian national ID
    isValidNationalId: function (nationalId) {
        const id = this.toEnglish(nationalId.replace(/\s/g, ''));
        if (!/^\d{10}$/.test(id)) return false;

        const check = parseInt(id[9]);
        let sum = 0;
        for (let i = 0; i < 9; i++) {
            sum += parseInt(id[i]) * (10 - i);
        }
        const remainder = sum % 11;
        return (remainder < 2 && check === remainder) || (remainder >= 2 && check === 11 - remainder);
    },

    // Format duration in minutes to Persian
    formatDuration: function (minutes) {
        if (!minutes) return '';
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;

        let result = '';
        if (hours > 0) {
            result += this.toPersian(hours.toString()) + ' ساعت';
        }
        if (mins > 0) {
            if (result) result += ' و ';
            result += this.toPersian(mins.toString()) + ' دقیقه';
        }
        return result || this.toPersian('0') + ' دقیقه';
    },

    // Format distance
    formatDistance: function (meters) {
        if (meters < 1000) {
            return this.toPersian(meters.toString()) + ' متر';
        } else {
            const km = (meters / 1000).toFixed(1);
            return this.toPersian(km) + ' کیلومتر';
        }
    },

    // Get relative time in Persian
    getRelativeTime: function (dateStr) {
        if (!dateStr) return '';

        const now = new Date();
        const past = new Date(dateStr);
        const diffMs = now - past;
        const diffMinutes = Math.floor(diffMs / (1000 * 60));
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

        if (diffMinutes < 1) {
            return 'همین الان';
        } else if (diffMinutes < 60) {
            return this.toPersian(diffMinutes.toString()) + ' دقیقه پیش';
        } else if (diffHours < 24) {
            return this.toPersian(diffHours.toString()) + ' ساعت پیش';
        } else if (diffDays < 7) {
            return this.toPersian(diffDays.toString()) + ' روز پیش';
        } else {
            return this.formatDate(dateStr);
        }
    },

    // Format currency with different units
    formatCurrency: function (amount, unit = 'تومان') {
        if (amount === null || amount === undefined) return '';
        const formatted = this.formatNumber(amount);
        return formatted + ' ' + unit;
    },

    // Convert number to Persian words (for small numbers)
    numberToPersianWords: function (num) {
        const ones = ['', 'یک', 'دو', 'سه', 'چهار', 'پنج', 'شش', 'هفت', 'هشت', 'نه'];
        const tens = ['', '', 'بیست', 'سی', 'چهل', 'پنجاه', 'شصت', 'هفتاد', 'هشتاد', 'نود'];
        const teens = ['ده', 'یازده', 'دوازده', 'سیزده', 'چهارده', 'پانزده', 'شانزده', 'هفده', 'هجده', 'نوزده'];
        const hundreds = ['', 'یکصد', 'دویست', 'سیصد', 'چهارصد', 'پانصد', 'ششصد', 'هفتصد', 'هشتصد', 'نهصد'];

        if (num === 0) return 'صفر';
        if (num < 0) return 'منفی ' + this.numberToPersianWords(-num);
        if (num < 10) return ones[num];
        if (num < 20) return teens[num - 10];
        if (num < 100) {
            const ten = Math.floor(num / 10);
            const one = num % 10;
            return tens[ten] + (one > 0 ? ' و ' + ones[one] : '');
        }
        if (num < 1000) {
            const hundred = Math.floor(num / 100);
            const remainder = num % 100;
            return hundreds[hundred] + (remainder > 0 ? ' و ' + this.numberToPersianWords(remainder) : '');
        }

        // For larger numbers, return Persian digits
        return this.toPersian(num.toString());
    }
};

// Make it available globally
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PersianNumbers;
} else if (typeof window !== 'undefined') {
    window.PersianNumbers = PersianNumbers;
} 