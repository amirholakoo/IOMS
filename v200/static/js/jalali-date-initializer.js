/**
 * Jalali Date Initializer
 * Automatically converts all dates with class 'jalali-date' to Persian format
 * This file should be included after jalali-date-converter.js
 */

(function() {
    'use strict';

    // Function to convert all Jalali dates on the page
    function convertAllJalaliDates() {
        const jalaliDateElements = document.querySelectorAll('.jalali-date');
        
        jalaliDateElements.forEach(element => {
            const dateString = element.getAttribute('data-date');
            if (dateString) {
                try {
                    // Determine the appropriate format based on the context
                    let format = 'DD Month YYYY، HH:mm';
                    
                    // If the date string includes seconds, use the full format
                    if (dateString.includes(':ss') || dateString.includes(':s')) {
                        format = 'DD Month YYYY، HH:mm:ss';
                    }
                    
                    // If it's just a date without time, use date-only format
                    if (!dateString.includes(':')) {
                        format = 'DD Month YYYY';
                    }
                    
                    const jalaliDate = JalaliDateConverter.format(dateString, format);
                    element.textContent = jalaliDate;
                    
                    // Add a subtle visual indicator that this is a converted date
                    element.style.fontWeight = '500';
                    element.style.color = '#1976d2';
                    
                } catch (error) {
                    console.error('Error converting Jalali date:', error);
                    console.error('Date string:', dateString);
                    console.error('Element:', element);
                    
                    // Keep original date if conversion fails
                    element.style.color = '#dc3545';
                    element.title = 'خطا در تبدیل تاریخ';
                }
            } else {
                console.warn('Jalali date element missing data-date attribute:', element);
            }
        });
    }

    // Function to convert a single date element
    function convertJalaliDate(element, format = 'DD Month YYYY، HH:mm') {
        const dateString = element.getAttribute('data-date');
        if (dateString) {
            try {
                const jalaliDate = JalaliDateConverter.format(dateString, format);
                element.textContent = jalaliDate;
                element.style.fontWeight = '500';
                element.style.color = '#1976d2';
                return true;
            } catch (error) {
                console.error('Error converting Jalali date:', error);
                element.style.color = '#dc3545';
                element.title = 'خطا در تبدیل تاریخ';
                return false;
            }
        }
        return false;
    }

    // Function to convert dates in dynamically loaded content
    function convertJalaliDatesInElement(container) {
        const jalaliDateElements = container.querySelectorAll('.jalali-date');
        jalaliDateElements.forEach(element => {
            convertJalaliDate(element);
        });
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', convertAllJalaliDates);
    } else {
        // DOM is already ready
        convertAllJalaliDates();
    }

    // Also convert dates when new content is loaded (for AJAX content)
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1) { // Element node
                        if (node.classList && node.classList.contains('jalali-date')) {
                            convertJalaliDate(node);
                        } else if (node.querySelectorAll) {
                            convertJalaliDatesInElement(node);
                        }
                    }
                });
            }
        });
    });

    // Start observing when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
        });
    } else {
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    // Make functions available globally for manual use
    window.JalaliDateUtils = {
        convertAll: convertAllJalaliDates,
        convertElement: convertJalaliDate,
        convertInElement: convertJalaliDatesInElement
    };

    // Add a global function to manually trigger conversion
    window.convertJalaliDates = convertAllJalaliDates;

    console.log('✅ Jalali Date Initializer loaded successfully');
    console.log('📅 Found and converted', document.querySelectorAll('.jalali-date').length, 'date elements');

})(); 