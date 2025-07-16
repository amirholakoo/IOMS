/**
 * Jalali Date Converter Utility
 * Converts Georgian dates to Jalali (Persian) dates
 * 
 * Usage:
 * - JalaliDateConverter.toJalali(new Date()) // Returns Jalali date object
 * - JalaliDateConverter.format(new Date(), 'YYYY/MM/DD') // Returns formatted string
 * - JalaliDateConverter.formatNow('YYYY/MM/DD HH:mm:ss') // Current date in Jalali
 */

class JalaliDateConverter {
    constructor() {
        // Jalali calendar constants
        this.JALALI_EPOCH = 1948320.5;
        this.GREGORIAN_EPOCH = 1721425.5;
        this.JALALI_WEEKDAYS = ['یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه', 'شنبه'];
        this.JALALI_MONTHS = [
            'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
            'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
        ];
        this.JALALI_MONTHS_SHORT = [
            'فر', 'ارد', 'خر', 'تی', 'مر', 'شه',
            'مه', 'آبا', 'آذ', 'دی', 'به', 'اس'
        ];
    }

    /**
     * Convert Georgian date to Julian Day Number
     * @param {Date} date - Georgian date
     * @returns {number} Julian Day Number
     */
    gregorianToJulianDay(date) {
        try {
            const year = date.getFullYear();
            const month = date.getMonth() + 1;
            const day = date.getDate();

            if (year < 0 || year > 9999) {
                throw new Error('Year must be between 0 and 9999');
            }

            let jdn = this.GREGORIAN_EPOCH - 1;
            jdn += 365 * (year - 1);
            jdn += Math.floor((year - 1) / 4);
            jdn += -Math.floor((year - 1) / 100);
            jdn += Math.floor((year - 1) / 400);
            jdn += Math.floor((367 * month - 362) / 12);
            jdn += day;

            if (month > 2) {
                if (this.isLeapYear(year)) {
                    jdn -= 1;
                } else {
                    jdn -= 2;
                }
            }

            return jdn;
        } catch (error) {
            console.error('Error in gregorianToJulianDay:', error);
            throw error;
        }
    }

    /**
     * Convert Julian Day Number to Jalali date
     * @param {number} jdn - Julian Day Number
     * @returns {Object} Jalali date object {year, month, day, weekday}
     */
    julianDayToJalali(jdn) {
        try {
            if (jdn <= 0) {
                throw new Error('Invalid Julian Day Number');
            }

            jdn = Math.floor(jdn) + 0.5;
            let depoch = jdn - this.JALALI_EPOCH;
            let cycle = Math.floor(depoch / 1029983);
            let cyear = depoch % 1029983;

            let ycycle;
            if (cyear === 1029982) {
                ycycle = 2820;
            } else {
                let aux1 = Math.floor(cyear / 366);
                let aux2 = cyear % 366;
                ycycle = Math.floor(((2134 * aux1) + (2816 * aux2) + 2815) / 1028522) + aux1 + 1;
            }

            let year = ycycle + (2820 * cycle) + 474;
            if (year <= 0) {
                year -= 1;
            }

            let yday = (jdn - this.jalaliToJulianDay(year, 1, 1)) + 1;
            let month = (yday <= 186) ? Math.ceil(yday / 31) : Math.ceil((yday - 6) / 30);
            let day = (jdn - this.jalaliToJulianDay(year, month, 1)) + 1;

            // Calculate weekday (0 = Sunday, 1 = Monday, ..., 6 = Saturday)
            let weekday = (jdn + 1) % 7;

            return {
                year: year,
                month: month,
                day: day,
                weekday: weekday,
                weekdayName: this.JALALI_WEEKDAYS[weekday]
            };
        } catch (error) {
            console.error('Error in julianDayToJalali:', error);
            throw error;
        }
    }

    /**
     * Convert Jalali date to Julian Day Number
     * @param {number} year - Jalali year
     * @param {number} month - Jalali month (1-12)
     * @param {number} day - Jalali day
     * @returns {number} Julian Day Number
     */
    jalaliToJulianDay(year, month, day) {
        try {
            if (year < 0 || month < 1 || month > 12 || day < 1 || day > 31) {
                throw new Error('Invalid Jalali date parameters');
            }

            let epbase = year - (year >= 0 ? 474 : 473);
            let epyear = 474 + (epbase % 2820);
            let mdays = (month <= 7) ? ((month - 1) * 31) : ((month - 1) * 30 + 6);

            return day + mdays + Math.floor((epyear * 682 - 110) / 2816) + (epyear - 1) * 365 + Math.floor(epbase / 2820) * 1029983 + (this.JALALI_EPOCH - 1);
        } catch (error) {
            console.error('Error in jalaliToJulianDay:', error);
            throw error;
        }
    }

    /**
     * Check if a Georgian year is a leap year
     * @param {number} year - Georgian year
     * @returns {boolean} True if leap year
     */
    isLeapYear(year) {
        try {
            return (year % 4 === 0 && year % 100 !== 0) || (year % 400 === 0);
        } catch (error) {
            console.error('Error in isLeapYear:', error);
            return false;
        }
    }

    /**
     * Convert Georgian date to Jalali date object
     * @param {Date|string} date - Georgian date (Date object or date string)
     * @returns {Object} Jalali date object
     */
    toJalali(date) {
        try {
            let georgianDate;
            
            if (typeof date === 'string') {
                georgianDate = new Date(date);
                if (isNaN(georgianDate.getTime())) {
                    throw new Error('Invalid date string format');
                }
            } else if (date instanceof Date) {
                georgianDate = date;
            } else {
                throw new Error('Invalid date parameter. Must be Date object or date string.');
            }

            const jdn = this.gregorianToJulianDay(georgianDate);
            const jalali = this.julianDayToJalali(jdn);

            return {
                ...jalali,
                monthName: this.JALALI_MONTHS[jalali.month - 1],
                monthNameShort: this.JALALI_MONTHS_SHORT[jalali.month - 1],
                originalDate: georgianDate
            };
        } catch (error) {
            console.error('Error in toJalali:', error);
            throw error;
        }
    }

    /**
     * Format Jalali date to string
     * @param {Date|string} date - Georgian date
     * @param {string} format - Format string (e.g., 'YYYY/MM/DD', 'DD Month YYYY')
     * @returns {string} Formatted Jalali date string
     */
    format(date, format = 'YYYY/MM/DD') {
        try {
            const jalali = this.toJalali(date);
            
            return format
                .replace(/YYYY/g, jalali.year.toString().padStart(4, '0'))
                .replace(/YY/g, jalali.year.toString().slice(-2))
                .replace(/MM/g, jalali.month.toString().padStart(2, '0'))
                .replace(/M/g, jalali.month.toString())
                .replace(/DD/g, jalali.day.toString().padStart(2, '0'))
                .replace(/D/g, jalali.day.toString())
                .replace(/Month/g, jalali.monthName)
                .replace(/MonthShort/g, jalali.monthNameShort)
                .replace(/Weekday/g, jalali.weekdayName);
        } catch (error) {
            console.error('Error in format:', error);
            throw error;
        }
    }

    /**
     * Format current date to Jalali
     * @param {string} format - Format string
     * @returns {string} Current date in Jalali format
     */
    formatNow(format = 'YYYY/MM/DD') {
        try {
            return this.format(new Date(), format);
        } catch (error) {
            console.error('Error in formatNow:', error);
            throw error;
        }
    }

    /**
     * Get current Jalali date object
     * @returns {Object} Current Jalali date object
     */
    now() {
        try {
            return this.toJalali(new Date());
        } catch (error) {
            console.error('Error in now:', error);
            throw error;
        }
    }

    /**
     * Convert Jalali date back to Georgian date
     * @param {number} year - Jalali year
     * @param {number} month - Jalali month (1-12)
     * @param {number} day - Jalali day
     * @returns {Date} Georgian date object
     */
    jalaliToGeorgian(year, month, day) {
        try {
            const jdn = this.jalaliToJulianDay(year, month, day);
            const gregorianJdn = jdn - this.GREGORIAN_EPOCH + this.JALALI_EPOCH;
            
            // Convert Julian Day Number to Georgian date
            const a = gregorianJdn + 32044;
            const b = Math.floor((4 * a + 3) / 146097);
            const c = a - Math.floor((b * 146097) / 4);
            const d = Math.floor((4 * c + 3) / 1461);
            const e = c - Math.floor((d * 1461) / 4);
            const m = Math.floor((5 * e + 2) / 153);
            
            const day2 = e - Math.floor((153 * m + 2) / 5) + 1;
            const month2 = m + 3 - 12 * Math.floor(m / 10);
            const year2 = b * 100 + d - 4800 + Math.floor(m / 10);
            
            return new Date(year2, month2 - 1, day2);
        } catch (error) {
            console.error('Error in jalaliToGeorgian:', error);
            throw error;
        }
    }

    /**
     * Validate Jalali date
     * @param {number} year - Jalali year
     * @param {number} month - Jalali month
     * @param {number} day - Jalali day
     * @returns {boolean} True if valid Jalali date
     */
    isValidJalaliDate(year, month, day) {
        try {
            if (year < 1 || month < 1 || month > 12 || day < 1) {
                return false;
            }

            const daysInMonth = (month <= 6) ? 31 : 30;
            if (month === 12 && day === 30) {
                // Check if it's a leap year in Jalali calendar
                const leapYear = (year + 12) % 33 % 4 === 1;
                return leapYear;
            }

            return day <= daysInMonth;
        } catch (error) {
            console.error('Error in isValidJalaliDate:', error);
            return false;
        }
    }
}

// Create global instance
const JalaliDateConverter = new JalaliDateConverter();

// Export for different module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = JalaliDateConverter;
} else if (typeof window !== 'undefined') {
    window.JalaliDateConverter = JalaliDateConverter;
}

// Example usage and documentation
/*
// Basic conversion
const jalaliDate = JalaliDateConverter.toJalali(new Date());
console.log(jalaliDate); // { year: 1403, month: 1, day: 15, weekday: 2, ... }

// Formatting
const formatted = JalaliDateConverter.format(new Date(), 'YYYY/MM/DD');
console.log(formatted); // "1403/01/15"

const fullFormat = JalaliDateConverter.format(new Date(), 'DD Month YYYY');
console.log(fullFormat); // "15 فروردین 1403"

// Current date
const now = JalaliDateConverter.formatNow('YYYY/MM/DD HH:mm:ss');
console.log(now); // "1403/01/15 14:30:25"

// Convert back to Georgian
const georgianDate = JalaliDateConverter.jalaliToGeorgian(1403, 1, 15);
console.log(georgianDate); // Date object

// Validation
const isValid = JalaliDateConverter.isValidJalaliDate(1403, 1, 15);
console.log(isValid); // true
*/ 