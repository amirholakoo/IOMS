/**
 * Accurate Persian (Jalali) Date Converter
 * Converts Gregorian dates to Persian (Jalali) format with correct month lengths
 */

// Persian month names
const PERSIAN_MONTHS = [
    'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
    'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
];

// Persian month lengths (days in each month)
const PERSIAN_MONTH_LENGTHS = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29];

// Check if a Persian year is a leap year
function isPersianLeapYear(year) {
    // Persian leap year calculation
    // A year is leap if the remainder of (year + 38) * 31 / 128 is less than 31
    return ((year + 38) * 31) % 128 < 31;
}

// Get the number of days in a Persian month
function getPersianMonthLength(year, month) {
    if (month === 11) { // Esfand (last month)
        return isPersianLeapYear(year) ? 30 : 29;
    }
    return PERSIAN_MONTH_LENGTHS[month];
}

// Convert Gregorian date to Persian date using proper algorithm
function gregorianToPersian(gregorianDate) {
    const year = gregorianDate.getFullYear();
    const month = gregorianDate.getMonth() + 1; // 1-12
    const day = gregorianDate.getDate();
    
    // Calculate days since March 21, 622 AD (Persian calendar epoch)
    let days = Math.floor((year - 622) * 365.25);
    
    // Add days for months before current month
    for (let i = 1; i < month; i++) {
        if (i <= 7) {
            days += (i % 2 === 1) ? 31 : 30;
        } else {
            days += (i % 2 === 0) ? 31 : 30;
        }
    }
    
    // Add days of current month
    days += day - 1;
    
    // Adjust for leap years
    if (month > 2 && ((year % 4 === 0 && year % 100 !== 0) || year % 400 === 0)) {
        days += 1;
    }
    
    // Convert to Persian calendar
    let persianYear = 1;
    let persianMonth = 1;
    let persianDay = 1;
    
    // Calculate Persian year
    persianYear = Math.floor(days / 365.25) + 1;
    
    // Calculate remaining days in the year
    let remainingDays = days - Math.floor((persianYear - 1) * 365.25);
    
    // Calculate Persian month and day
    for (let i = 0; i < 12; i++) {
        const monthLength = getPersianMonthLength(persianYear, i);
        if (remainingDays < monthLength) {
            persianMonth = i + 1;
            persianDay = remainingDays + 1;
            break;
        }
        remainingDays -= monthLength;
    }
    
    return {
        year: persianYear,
        month: persianMonth,
        day: persianDay
    };
}

// Alternative algorithm using a more direct approach
function gregorianToPersianDirect(gregorianDate) {
    const year = gregorianDate.getFullYear();
    const month = gregorianDate.getMonth() + 1;
    const day = gregorianDate.getDate();
    
    // Persian calendar starts on March 21st
    // Calculate days since March 21st of the current year
    let daysSinceMarch21 = 0;
    
    if (month === 1) {
        daysSinceMarch21 = day - 80; // January 1st is 80 days before March 21st
    } else if (month === 2) {
        daysSinceMarch21 = day - 49; // February 1st is 49 days before March 21st
    } else {
        // March onwards
        const daysInMonth = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
        daysSinceMarch21 = day - 21; // March 21st is day 21
        
        // Add days from previous months
        for (let i = 3; i < month; i++) {
            daysSinceMarch21 += daysInMonth[i];
        }
        
        // Adjust for leap year
        if (month > 2 && ((year % 4 === 0 && year % 100 !== 0) || year % 400 === 0)) {
            daysSinceMarch21 += 1;
        }
    }
    
    // If negative, it's from previous Persian year
    if (daysSinceMarch21 < 0) {
        daysSinceMarch21 += 365;
        if ((year % 4 === 0 && year % 100 !== 0) || year % 400 === 0) {
            daysSinceMarch21 += 1;
        }
    }
    
    // Convert to Persian date
    let persianYear = year - 621;
    let persianMonth = 1;
    let persianDay = daysSinceMarch21 + 1;
    
    // Adjust month and day
    const persianMonthLengths = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29];
    
    for (let i = 0; i < 12; i++) {
        const monthLength = (i === 11) ? (isPersianLeapYear(persianYear) ? 30 : 29) : persianMonthLengths[i];
        if (persianDay <= monthLength) {
            persianMonth = i + 1;
            break;
        }
        persianDay -= monthLength;
        if (i === 11) {
            persianYear += 1;
            i = -1; // Reset to start of next year
        }
    }
    
    return {
        year: persianYear,
        month: persianMonth,
        day: persianDay
    };
}

// Main conversion function
function convertToPersianDate(englishDate) {
    console.log('Converting date:', englishDate);
    
    try {
        const date = new Date(englishDate);
        if (isNaN(date.getTime())) {
            console.log('Invalid date, returning original:', englishDate);
            return englishDate;
        }

        const hours = date.getHours();
        const minutes = date.getMinutes();
        const seconds = date.getSeconds();

        // Convert to Persian date using the direct algorithm
        const persian = gregorianToPersianDirect(date);
        
        // Get Persian month name
        const persianMonthName = PERSIAN_MONTHS[persian.month - 1];
        
        // Format the date
        const formattedDate = `${persian.day} ${persianMonthName} ${persian.year}`;
        
        // Add time if it exists
        if (hours > 0 || minutes > 0) {
            const timeStr = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
            const result = `${formattedDate}، ${timeStr}`;
            console.log('Converted to:', result);
            return result;
        }

        console.log('Converted to:', formattedDate);
        return formattedDate;
    } catch (error) {
        console.error('Error converting date:', error);
        return englishDate;
    }
}

// Test function to validate the conversion
function testPersianConversion() {
    const testDates = [
        '2025-07-23', // Today
        '2025-07-24', // Tomorrow
        '2025-07-22', // Yesterday
        '2025-03-21', // Persian New Year (Norooz)
        '2025-03-20', // Day before Persian New Year
        '2025-12-21', // Winter solstice
        '2025-06-21', // Summer solstice
    ];
    
    console.log('Testing Persian date conversion:');
    testDates.forEach(dateStr => {
        const persian = convertToPersianDate(dateStr);
        console.log(`${dateStr} → ${persian}`);
    });
}

// Make functions available globally
window.convertToPersianDate = convertToPersianDate;
window.testPersianConversion = testPersianConversion;
window.isPersianLeapYear = isPersianLeapYear;
window.getPersianMonthLength = getPersianMonthLength;

console.log('✅ Accurate Persian date converter loaded'); 