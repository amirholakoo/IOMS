# 🧪 Browser Testing Guide for Persian Number Validation

## 🚀 Quick Start

### 1. Start the Django Server
```bash
cd v200
python manage.py runserver
```

### 2. Open Your Browser
Go to: `http://localhost:8000`

---

## 📱 **Test 1: SMS Login Page**

### URL: `http://localhost:8000/accounts/customer/sms-login/`

**Test Cases:**

1. **Valid Persian Phone Number:**
   - Enter: `۰۹۱۲۳۴۵۶۷۸۹`
   - Expected: Should convert to `09123456789`
   - ✅ Should proceed to verification page

2. **Mixed Persian/English:**
   - Enter: `۰۹۱۲۳۴۵۶۷۸۹`
   - Expected: Should convert to `09123456789`
   - ✅ Should proceed to verification page

3. **Invalid Phone Number:**
   - Enter: `۰۸۱۲۳۴۵۶۷۸۹` (wrong prefix)
   - Expected: Should show error message
   - ❌ Should not proceed

4. **Too Short:**
   - Enter: `۰۹۱۲۳۴۵۶۷۸`
   - Expected: Should show error message
   - ❌ Should not proceed

### **Test 1.1: SMS Verification Page**

**Test Cases:**

1. **Valid Persian Verification Code:**
   - Enter: `۱۲۳۴۵۶`
   - Expected: Should convert to `123456`
   - ✅ Should submit automatically

2. **Mixed Persian/English Code:**
   - Enter: `۱۲۳۴۵۶`
   - Expected: Should convert to `123456`
   - ✅ Should submit automatically

3. **Paste Persian Code:**
   - Copy: `۱۲۳۴۵۶`
   - Paste into field
   - Expected: Should convert to `123456`
   - ✅ Should work correctly

---

## 📝 **Test 2: Customer Registration**

### URL: `http://localhost:8000/accounts/customer-registration/`

**Test Cases:**

1. **Valid Persian Phone Number:**
   - Enter: `۰۹۱۲۳۴۵۶۷۸۹`
   - Expected: Should convert to `09123456789`
   - ✅ Should show success

2. **Mixed Persian/English:**
   - Enter: `۰۹۱۲۳۴۵۶۷۸۹`
   - Expected: Should convert to `09123456789`
   - ✅ Should show success

3. **Invalid Phone Number:**
   - Enter: `۰۸۱۲۳۴۵۶۷۸۹` (wrong prefix)
   - Expected: Should show error message
   - ❌ Should not submit

4. **Too Short:**
   - Enter: `۰۹۱۲۳۴۵۶۷۸`
   - Expected: Should show error message
   - ❌ Should not submit

---

## 🎛️ **Test 3: Admin Interface**

### URL: `http://localhost:8000/admin/`

**Login with admin credentials, then:**

### A. Create Customer
1. Go to: `Customers` → `Add Customer`
2. Fill form with Persian numbers:
   - **Phone:** `۰۹۱۲۳۴۵۶۷۸۹`
   - **National ID:** `۱۲۳۴۵۶۷۸۹۰`
   - **Economic Code:** `۱۲۳۴۵۶۷۸۹`
   - **Postcode:** `۱۲۳۴۵۶۷۸۹۰`
3. Click "Save"
4. **Expected:** All numbers should be saved as English numbers

### B. Create Product
1. Go to: `Products` → `Add Product`
2. Fill form with Persian numbers:
   - **Width:** `۱۲۳`
   - **Length:** `۴۵۶`
   - **GSM:** `۸۰`
   - **Breaks:** `۲`
   - **Price:** `۱۲۳۴۵۶۷`
3. Click "Save"
4. **Expected:** All numbers should be saved as English numbers

---

## 🛒 **Test 4: Shopping Page**

### URL: `http://localhost:8000/shopping/`

**Test Cases:**

1. **Quantity Input:**
   - Click on any product's quantity field
   - Enter: `۱۲۳` (Persian numbers)
   - Expected: Should convert to `123`
   - ✅ Should accept the input

2. **Mixed Numbers:**
   - Enter: `۱۲۳` (mixed Persian/English)
   - Expected: Should convert to `123`
   - ✅ Should work correctly

---

## 🔍 **Test 5: Customer Edit Modal**

### URL: `http://localhost:8000/core/customers/`

1. Click on any customer's "Edit" button
2. In the modal, test these fields:
   - **Phone:** `۰۹۱۲۳۴۵۶۷۸۹`
   - **National ID:** `۱۲۳۴۵۶۷۸۹۰`
   - **Economic Code:** `۱۲۳۴۵۶۷۸۹`
   - **Postcode:** `۱۲۳۴۵۶۷۸۹۰`
3. Click "Save"
4. **Expected:** All numbers should be normalized

---

## 🌐 **Test 6: JavaScript Functionality**

### Open Browser Developer Tools (F12)

**Test in Console:**

```javascript
// Test Persian number normalization
window.PersianNumbers.normalize("۰۹۱۲۳۴۵۶۷۸۹")
// Expected: "09123456789"

// Test phone validation
window.PersianNumbers.validatePhone("۰۹۱۲۳۴۵۶۷۸۹")
// Expected: true

// Test number validation
window.PersianNumbers.validateNumber("۱۲۳۴۵۶")
// Expected: true
```

---

## ✅ **Expected Results**

### ✅ **What Should Work:**
- Persian numbers automatically convert to English
- Real-time validation with error messages
- Form submission with normalized data
- Admin interface accepts Persian numbers
- JavaScript functions are available globally

### ❌ **What Should NOT Work:**
- Invalid phone numbers (wrong prefix, wrong length)
- Non-numeric characters in number fields
- Multiple decimal points in prices
- Empty required fields

---

## 🐛 **Troubleshooting**

### If Tests Fail:

1. **Check Console Errors:**
   - Open Developer Tools (F12)
   - Look for JavaScript errors in Console tab

2. **Check Network Tab:**
   - Look for failed requests
   - Check if static files are loading

3. **Check Django Logs:**
   - Look at terminal where server is running
   - Check for Python errors

4. **Verify File Structure:**
   ```bash
   ls -la static/js/persian-numbers.js
   ls -la templates/base.html
   ```

5. **Run Quick Test Script:**
   ```bash
   python test_persian_numbers_quick.py
   ```

---

## 📊 **Test Checklist**

- [ ] SMS login page accepts Persian phone numbers
- [ ] SMS verification page accepts Persian verification codes
- [ ] Customer registration accepts Persian phone numbers
- [ ] Admin customer creation works with Persian numbers
- [ ] Admin product creation works with Persian numbers
- [ ] Shopping page quantity inputs work with Persian numbers
- [ ] Customer edit modal works with Persian numbers
- [ ] JavaScript functions are available in browser console
- [ ] Error messages appear for invalid inputs
- [ ] All numbers are saved as English in database

---

## 🎯 **Success Criteria**

✅ **System is working correctly if:**
- All Persian numbers convert to English automatically
- Forms submit successfully with normalized data
- Error messages appear for invalid inputs
- JavaScript functions work in browser console
- Admin interface accepts and normalizes Persian numbers

If all tests pass, your Persian number validation system is working perfectly! 🎉 