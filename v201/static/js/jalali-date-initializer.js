/**
 * Simple Persian Date Initializer
 * Converts all dates with class 'jalali-date' to Persian format
 */

// Function to convert all Persian dates on the page
function convertAllPersianDates() {
    console.log('🔍 Looking for date elements...');
    
    const dateElements = document.querySelectorAll('.jalali-date');
    console.log('📅 Found', dateElements.length, 'date elements');
    
    dateElements.forEach((element, index) => {
        const dateString = element.getAttribute('data-date');
        console.log(`Element ${index + 1}:`, dateString);
        
        if (dateString) {
            try {
                const persianDate = convertToPersianDate(dateString);
                element.textContent = persianDate;
                element.style.color = '#1976d2';
                element.style.fontWeight = '500';
                console.log(`✅ Converted element ${index + 1} to:`, persianDate);
            } catch (error) {
                console.error('❌ Error converting date:', error);
                element.style.color = '#dc3545';
                element.title = 'خطا در تبدیل تاریخ';
            }
        } else {
            console.warn('⚠️ Element missing data-date attribute:', element);
        }
    });
    
    console.log('✅ Converted', dateElements.length, 'dates to Persian format');
}

// Convert dates when page loads
if (document.readyState === 'loading') {
    console.log('📄 Page still loading, waiting for DOMContentLoaded...');
    document.addEventListener('DOMContentLoaded', function() {
        console.log('📄 DOM loaded, converting dates...');
        convertAllPersianDates();
    });
} else {
    console.log('📄 DOM already ready, converting dates...');
    convertAllPersianDates();
}

// Make function available globally
window.convertAllPersianDates = convertAllPersianDates;
console.log('✅ Persian date initializer loaded'); 