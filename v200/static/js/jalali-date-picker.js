/**
 * Persian Jalali Date Picker Plugin
 * Converts HTML5 date inputs to Persian Jalali date pickers
 * Compatible with existing jalali-date-converter.js
 */

class JalaliDatePicker {
    constructor() {
        this.persianMonths = [
            'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
            'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
        ];
        this.persianWeekDays = ['یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه', 'شنبه'];
        this.shortWeekDays = ['ی', 'د', 'س', 'چ', 'پ', 'ج', 'ش'];
        this.currentDate = new Date();
        this.selectedDate = null;
        this.isOpen = false;
        this.targetInput = null;
        this.pickerElement = null;
    }

    // Convert Georgian date to Persian date using proper algorithm
    gregorianToPersian(date) {
        const year = date.getFullYear();
        const month = date.getMonth() + 1;
        const day = date.getDate();
        
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
            const monthLength = this.isPersianLeapYear(persianYear) && i === 11 ? 30 : persianMonthLengths[i];
            if (persianDay <= monthLength) {
                persianMonth = i + 1;
                break;
            }
            persianDay -= monthLength;
        }
        
        return {
            year: persianYear,
            month: persianMonth,
            day: persianDay
        };
    }

    // Convert Persian date to Georgian date using proper algorithm
    persianToGregorian(persianYear, persianMonth, persianDay) {
        // Persian calendar starts on March 21st of the Georgian year
        // Calculate the Georgian year
        let georgianYear = persianYear + 621;
        
        // Calculate days since March 21st
        let daysSinceMarch21 = 0;
        
        // Add days from previous months
        for (let i = 1; i < persianMonth; i++) {
            daysSinceMarch21 += this.getPersianMonthDays(persianYear, i);
        }
        
        // Add days of current month
        daysSinceMarch21 += persianDay - 1;
        
        // Calculate Georgian month and day
        let georgianMonth = 3; // Start from March
        let georgianDay = 21 + daysSinceMarch21;
        
        // Adjust month and day
        const daysInMonth = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
        
        // Check for leap year
        if ((georgianYear % 4 === 0 && georgianYear % 100 !== 0) || georgianYear % 400 === 0) {
            daysInMonth[2] = 29;
        }
        
        // Adjust month and day
        while (georgianDay > daysInMonth[georgianMonth]) {
            georgianDay -= daysInMonth[georgianMonth];
            georgianMonth++;
            
            // If we go past December, move to next year
            if (georgianMonth > 12) {
                georgianMonth = 1;
                georgianYear++;
                
                // Recalculate leap year for new year
                if ((georgianYear % 4 === 0 && georgianYear % 100 !== 0) || georgianYear % 400 === 0) {
                    daysInMonth[2] = 29;
                } else {
                    daysInMonth[2] = 28;
                }
            }
        }
        
        return new Date(georgianYear, georgianMonth - 1, georgianDay);
    }

    // Check if Persian year is leap year
    isPersianLeapYear(year) {
        return ((year + 38) * 31) % 128 < 31;
    }

    // Get days in Persian month
    getPersianMonthDays(year, month) {
        if (month <= 6) return 31;
        if (month <= 11) return 30;
        return this.isPersianLeapYear(year) ? 30 : 29;
    }

    // Create date picker HTML
    createPickerHTML() {
        const persianDate = this.gregorianToPersian(this.currentDate);
        
        return `
            <div class="jalali-date-picker" style="
                position: absolute;
                top: 100%;
                left: 0;
                z-index: 1000;
                background: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                padding: 15px;
                min-width: 280px;
                font-family: 'Vazirmatn', sans-serif;
                direction: rtl;
            ">
                <div class="picker-header" style="
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 15px;
                    padding-bottom: 10px;
                    border-bottom: 1px solid #eee;
                ">
                    <button type="button" class="prev-month" style="
                        background: none;
                        border: none;
                        font-size: 18px;
                        cursor: pointer;
                        padding: 5px;
                        border-radius: 4px;
                        color: #666;
                    ">&lt;</button>
                    <div class="current-month-year" style="
                        font-weight: bold;
                        color: #333;
                        font-size: 14px;
                    ">${this.persianMonths[persianDate.month - 1]} ${persianDate.year}</div>
                    <button type="button" class="next-month" style="
                        background: none;
                        border: none;
                        font-size: 18px;
                        cursor: pointer;
                        padding: 5px;
                        border-radius: 4px;
                        color: #666;
                    ">&gt;</button>
                </div>
                
                <div class="weekdays" style="
                    display: grid;
                    grid-template-columns: repeat(7, 1fr);
                    gap: 2px;
                    margin-bottom: 10px;
                ">
                    ${this.shortWeekDays.map(day => `
                        <div style="
                            text-align: center;
                            font-size: 12px;
                            color: #999;
                            padding: 5px;
                            font-weight: bold;
                        ">${day}</div>
                    `).join('')}
                </div>
                
                <div class="days" style="
                    display: grid;
                    grid-template-columns: repeat(7, 1fr);
                    gap: 2px;
                " id="days-grid">
                    <!-- Days will be populated here -->
                </div>
                
                <div class="picker-footer" style="
                    margin-top: 15px;
                    padding-top: 10px;
                    border-top: 1px solid #eee;
                    text-align: center;
                ">
                    <button type="button" class="today-btn" style="
                        background: #007bff;
                        color: white;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 4px;
                        cursor: pointer;
                        font-size: 12px;
                    ">امروز</button>
                    <button type="button" class="clear-btn" style="
                        background: #6c757d;
                        color: white;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 4px;
                        cursor: pointer;
                        font-size: 12px;
                        margin-right: 10px;
                    ">پاک کردن</button>
                </div>
            </div>
        `;
    }

    // Populate days grid
    populateDays() {
        const daysGrid = this.pickerElement.querySelector('#days-grid');
        const persianDate = this.gregorianToPersian(this.currentDate);
        
        // Get first day of month
        const firstDayOfMonth = this.persianToGregorian(persianDate.year, persianDate.month, 1);
        const firstDayWeekday = firstDayOfMonth.getDay();
        
        // Get days in month
        const daysInMonth = this.getPersianMonthDays(persianDate.year, persianDate.month);
        
        // Get previous month days
        const prevMonth = persianDate.month === 1 ? 12 : persianDate.month - 1;
        const prevYear = persianDate.month === 1 ? persianDate.year - 1 : persianDate.year;
        const prevMonthDays = this.getPersianMonthDays(prevYear, prevMonth);
        
        let html = '';
        
        // Previous month days
        for (let i = firstDayWeekday - 1; i >= 0; i--) {
            const day = prevMonthDays - i;
            html += `
                <div class="day prev-month-day" data-day="${day}" data-month="${prevMonth}" data-year="${prevYear}" style="
                    text-align: center;
                    padding: 8px;
                    cursor: pointer;
                    border-radius: 4px;
                    color: #ccc;
                    font-size: 12px;
                ">${day}</div>
            `;
        }
        
        // Current month days
        for (let day = 1; day <= daysInMonth; day++) {
            const isToday = day === persianDate.day;
            const isSelected = this.selectedDate && 
                             this.selectedDate.year === persianDate.year &&
                             this.selectedDate.month === persianDate.month &&
                             this.selectedDate.day === day;
            
            html += `
                <div class="day current-month-day ${isToday ? 'today' : ''} ${isSelected ? 'selected' : ''}" 
                     data-day="${day}" data-month="${persianDate.month}" data-year="${persianDate.year}" style="
                    text-align: center;
                    padding: 8px;
                    cursor: pointer;
                    border-radius: 4px;
                    font-size: 12px;
                    ${isToday ? 'background: #007bff; color: white; font-weight: bold;' : ''}
                    ${isSelected ? 'background: #28a745; color: white; font-weight: bold;' : ''}
                    ${!isToday && !isSelected ? 'color: #333;' : ''}
                ">${day}</div>
            `;
        }
        
        // Next month days
        const remainingDays = 42 - (firstDayWeekday + daysInMonth);
        const nextMonth = persianDate.month === 12 ? 1 : persianDate.month + 1;
        const nextYear = persianDate.month === 12 ? persianDate.year + 1 : persianDate.year;
        
        for (let day = 1; day <= remainingDays; day++) {
            html += `
                <div class="day next-month-day" data-day="${day}" data-month="${nextMonth}" data-year="${nextYear}" style="
                    text-align: center;
                    padding: 8px;
                    cursor: pointer;
                    border-radius: 4px;
                    color: #ccc;
                    font-size: 12px;
                ">${day}</div>
            `;
        }
        
        daysGrid.innerHTML = html;
    }

    // Initialize date picker for an input
    init(inputElement) {
        // Create picker element
        this.targetInput = inputElement;
        this.pickerElement = document.createElement('div');
        this.pickerElement.innerHTML = this.createPickerHTML();
        this.pickerElement = this.pickerElement.firstElementChild;
        
        // Position picker
        this.positionPicker();
        
        // Add event listeners
        this.addEventListeners();
        
        // Populate days
        this.populateDays();
        
        // Add to DOM
        document.body.appendChild(this.pickerElement);
        
        // Hide initially
        this.pickerElement.style.display = 'none';
    }

    // Position the picker
    positionPicker() {
        const rect = this.targetInput.getBoundingClientRect();
        this.pickerElement.style.position = 'fixed';
        this.pickerElement.style.top = (rect.bottom + window.scrollY + 5) + 'px';
        this.pickerElement.style.left = (rect.left + window.scrollX) + 'px';
    }

    // Add event listeners
    addEventListeners() {
        // Input click
        this.targetInput.addEventListener('click', (e) => {
            e.preventDefault();
            this.toggle();
        });

        // Input focus
        this.targetInput.addEventListener('focus', (e) => {
            e.preventDefault();
            this.show();
        });

        // Previous/Next month buttons
        this.pickerElement.querySelector('.prev-month').addEventListener('click', () => {
            this.currentDate.setMonth(this.currentDate.getMonth() - 1);
            this.updatePicker();
        });

        this.pickerElement.querySelector('.next-month').addEventListener('click', () => {
            this.currentDate.setMonth(this.currentDate.getMonth() + 1);
            this.updatePicker();
        });

        // Day clicks
        this.pickerElement.addEventListener('click', (e) => {
            if (e.target.classList.contains('day')) {
                const day = parseInt(e.target.dataset.day);
                const month = parseInt(e.target.dataset.month);
                const year = parseInt(e.target.dataset.year);
                
                this.selectDate(year, month, day);
            }
        });

        // Today button
        this.pickerElement.querySelector('.today-btn').addEventListener('click', () => {
            this.currentDate = new Date();
            this.selectDate(
                this.gregorianToPersian(this.currentDate).year,
                this.gregorianToPersian(this.currentDate).month,
                this.gregorianToPersian(this.currentDate).day
            );
        });

        // Clear button
        this.pickerElement.querySelector('.clear-btn').addEventListener('click', () => {
            this.clearDate();
        });

        // Close picker when clicking outside
        document.addEventListener('click', (e) => {
            if (!this.pickerElement.contains(e.target) && !this.targetInput.contains(e.target)) {
                this.hide();
            }
        });
    }

    // Update picker display
    updatePicker() {
        const persianDate = this.gregorianToPersian(this.currentDate);
        this.pickerElement.querySelector('.current-month-year').textContent = 
            `${this.persianMonths[persianDate.month - 1]} ${persianDate.year}`;
        this.populateDays();
    }

    // Select a date
    selectDate(year, month, day) {
        this.selectedDate = { year, month, day };
        
        // Convert to Georgian date
        const georgianDate = this.persianToGregorian(year, month, day);
        
        // Format for input value (YYYY-MM-DD)
        const formattedDate = georgianDate.toISOString().split('T')[0];
        
        // Update input value
        this.targetInput.value = formattedDate;
        
        // Update picker display
        this.currentDate = georgianDate;
        this.updatePicker();
        
        // Trigger change event
        this.targetInput.dispatchEvent(new Event('change', { bubbles: true }));
        
        // Hide picker
        this.hide();
    }

    // Clear selected date
    clearDate() {
        this.selectedDate = null;
        this.targetInput.value = '';
        this.targetInput.dispatchEvent(new Event('change', { bubbles: true }));
        this.hide();
    }

    // Show picker
    show() {
        this.pickerElement.style.display = 'block';
        this.isOpen = true;
        this.positionPicker();
    }

    // Hide picker
    hide() {
        this.pickerElement.style.display = 'none';
        this.isOpen = false;
    }

    // Toggle picker
    toggle() {
        if (this.isOpen) {
            this.hide();
        } else {
            this.show();
        }
    }

    // Destroy picker
    destroy() {
        if (this.pickerElement && this.pickerElement.parentNode) {
            this.pickerElement.parentNode.removeChild(this.pickerElement);
        }
    }
}

// Global instance
window.JalaliDatePicker = JalaliDatePicker;

// Test function to verify date conversion
window.testPersianDateConversion = function() {
    const picker = new JalaliDatePicker();
    
    // Test current date
    const today = new Date();
    const persianToday = picker.gregorianToPersian(today);
    const backToGeorgian = picker.persianToGregorian(persianToday.year, persianToday.month, persianToday.day);
    
    console.log('Today (Georgian):', today.toISOString().split('T')[0]);
    console.log('Today (Persian):', `${persianToday.year}/${persianToday.month}/${persianToday.day}`);
    console.log('Back to Georgian:', backToGeorgian.toISOString().split('T')[0]);
    
    // Test a specific date
    const testDate = new Date('2024-01-15');
    const persianTest = picker.gregorianToPersian(testDate);
    const backToGeorgianTest = picker.persianToGregorian(persianTest.year, persianTest.month, persianTest.day);
    
    console.log('Test Date (Georgian):', testDate.toISOString().split('T')[0]);
    console.log('Test Date (Persian):', `${persianTest.year}/${persianTest.month}/${persianTest.day}`);
    console.log('Back to Georgian:', backToGeorgianTest.toISOString().split('T')[0]);
};

// Auto-initialize for all date inputs
document.addEventListener('DOMContentLoaded', function() {
    const dateInputs = document.querySelectorAll('input[type="date"]');
    const pickers = [];
    
    dateInputs.forEach(input => {
        const picker = new JalaliDatePicker();
        picker.init(input);
        pickers.push(picker);
    });
    
    // Store pickers for cleanup
    window.jalaliDatePickers = pickers;
    
    // Run test on page load
    if (window.location.href.includes('activity-logs')) {
        console.log('Testing Persian date conversion...');
        window.testPersianDateConversion();
    }
});

console.log('✅ Persian Jalali Date Picker loaded'); 