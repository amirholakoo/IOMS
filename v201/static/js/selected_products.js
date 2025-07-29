let CASH_PURCHASES_DISABLED = false; // Default value, will be updated from API

// Fetch working hours configuration
async function fetchWorkingHoursConfig() {
    try {
        const response = await fetch('/core/api/working-hours-config/');
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                CASH_PURCHASES_DISABLED = data.cash_purchases_disabled;
                console.log(`💰 Cash purchases disabled: ${CASH_PURCHASES_DISABLED}`);
                
                // Update UI based on cash purchases status
                updateCashPurchaseStatus();
            }
        }
    } catch (error) {
        console.warn('⚠️ Could not fetch working hours config:', error);
    }
}

// Function to update UI based on cash purchase status
function updateCashPurchaseStatus() {
    const cashPurchaseDisabledAlert = document.getElementById('cashPurchaseDisabledAlert');
    const paymentTypeSelect = document.getElementById('payment_type');
    
    if (CASH_PURCHASES_DISABLED) {
        // Show alert
        if (cashPurchaseDisabledAlert) {
            cashPurchaseDisabledAlert.style.display = 'block';
        }
        
        // Disable cash payment option
        if (paymentTypeSelect) {
            const cashOption = paymentTypeSelect.querySelector('option[value="Cash"]');
            if (cashOption) {
                cashOption.disabled = true;
                cashOption.title = 'در حال حاضر امکان خرید نقدی غیرفعال می‌باشد';
            }
            
            // If cash is selected, switch to credit
            if (paymentTypeSelect.value === 'Cash') {
                paymentTypeSelect.value = 'Credit';
                // Trigger change event
                paymentTypeSelect.dispatchEvent(new Event('change'));
            }
        }
    } else {
        // Hide alert
        if (cashPurchaseDisabledAlert) {
            cashPurchaseDisabledAlert.style.display = 'none';
        }
        
        // Enable cash payment option
        if (paymentTypeSelect) {
            const cashOption = paymentTypeSelect.querySelector('option[value="Cash"]');
            if (cashOption) {
                cashOption.disabled = false;
                cashOption.title = '';
            }
        }
    }
}

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    // Fetch working hours configuration first
    fetchWorkingHoursConfig();
    
    // ... existing initialization code ...
}); 