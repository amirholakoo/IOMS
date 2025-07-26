// Test Persian date conversion for today
const today = new Date();
console.log('Today (Gregorian):', today.toISOString());

// Simple Persian date converter (from your jalali-date-converter.js)
function convertToPersianDate(englishDate) {
    try {
        const date = new Date(englishDate);
        if (isNaN(date.getTime())) {
            return englishDate;
        }

        // Persian month names
        const persianMonths = [
            'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
            'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
        ];

        const year = date.getFullYear();
        const month = date.getMonth() + 1;
        const day = date.getDate();
        const hours = date.getHours();
        const minutes = date.getMinutes();

        let persianYear = year - 621;
        let persianMonth;
        let persianDay;
        
        if (month >= 3) {
            persianMonth = month - 3;
            persianDay = day;
        } else {
            persianMonth = month + 9;
            persianDay = day;
            persianYear -= 1;
        }

        // Adjust for more accurate day calculation
        if (month >= 3 && month <= 6) {
            persianDay += 3;
        } else if (month >= 7 && month <= 9) {
            persianDay += 9;
        } else if (month >= 10 && month <= 12) {
            persianDay += 6;
        } else {
            persianDay += 10;
        }

        const persianMonthName = persianMonths[persianMonth - 1];
        const formattedDate = `${persianDay} ${persianMonthName} ${persianYear}`;
        
        if (hours > 0 || minutes > 0) {
            const timeStr = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
            return `${formattedDate}، ${timeStr}`;
        }

        return formattedDate;
    } catch (error) {
        return englishDate;
    }
}

// Convert today's date
const persianToday = convertToPersianDate(today);
console.log('Today (Persian):', persianToday);

// Also show the raw date components
console.log('Date components:');
console.log('- Gregorian:', today.getFullYear(), today.getMonth() + 1, today.getDate());
console.log('- Persian year:', today.getFullYear() - 621); 