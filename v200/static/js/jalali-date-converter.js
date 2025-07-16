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

        // Persian month names - CORRECTED ORDER
        const persianMonths = [
            'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
            'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
        ];

        // Convert to Persian date using a more accurate algorithm
        const year = date.getFullYear();
        const month = date.getMonth() + 1; // 1-12
        const day = date.getDate();
        const hours = date.getHours();
        const minutes = date.getMinutes();

        // More accurate Persian year calculation
        let persianYear = year - 621;
        
        // CORRECTED month mapping for Persian calendar
        let persianMonth;
        let persianDay;
        
        // Persian calendar mapping:
        // March 21-April 20 = فروردین (1)
        // April 21-May 21 = اردیبهشت (2)
        // May 22-June 21 = خرداد (3)
        // June 22-July 22 = تیر (4)
        // July 23-August 22 = مرداد (5)
        // August 23-September 22 = شهریور (6)
        // September 23-October 22 = مهر (7)
        // October 23-November 21 = آبان (8)
        // November 22-December 21 = آذر (9)
        // December 22-January 20 = دی (10)
        // January 21-February 19 = بهمن (11)
        // February 20-March 20 = اسفند (12)
        
        // More precise month mapping
        if (month >= 3) {
            // March onwards: subtract 3 months (not 2)
            persianMonth = month - 3;
            persianDay = day;
        } else {
            // January and February: add 9 months and subtract 1 year
            persianMonth = month + 9;
            persianDay = day;
            persianYear -= 1;
        }

        // Adjust for more accurate day calculation
        // This is a simplified adjustment - for exact precision, we'd need a full Persian calendar algorithm
        if (month >= 3 && month <= 6) {
            // Spring months: add a few days
            persianDay += 3;
        } else if (month >= 7 && month <= 9) {
            // Summer months: add more days
            persianDay += 9;
        } else if (month >= 10 && month <= 12) {
            // Fall months: add some days
            persianDay += 6;
        } else {
            // Winter months: add days
            persianDay += 10;
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