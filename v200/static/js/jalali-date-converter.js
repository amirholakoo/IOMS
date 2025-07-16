/**
 * Simple Persian Date Converter
 * Converts English dates to Persian (Jalali) format
 */

// Simple Persian date converter
function convertToPersianDate(englishDate) {
    console.log('Converting date:', englishDate);
    
    try {
        const date = new Date(englishDate);
        if (isNaN(date.getTime())) {
            console.log('Invalid date, returning original:', englishDate);
            return englishDate; // Return original if invalid date
        }

        // Persian month names
        const persianMonths = [
            'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
            'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
        ];

        // Convert to Persian date using a simple algorithm
        const year = date.getFullYear();
        const month = date.getMonth() + 1;
        const day = date.getDate();
        const hours = date.getHours();
        const minutes = date.getMinutes();
        const seconds = date.getSeconds();

        // Simple conversion (approximate)
        let persianYear = year - 621;
        let persianMonth = month + 2;
        let persianDay = day + 1;

        // Adjust for Persian calendar
        if (persianMonth > 12) {
            persianMonth -= 12;
            persianYear += 1;
        }

        // Format the date
        const persianMonthName = persianMonths[persianMonth - 1];
        const formattedDate = `${persianDay} ${persianMonthName} ${persianYear}`;
        
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
        return englishDate; // Return original on error
    }
}

// Make it available globally
window.convertToPersianDate = convertToPersianDate;
console.log('✅ Persian date converter loaded'); 