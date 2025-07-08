// Admin Panel JavaScript

// Test data for users
const testUsers = [
    {
        id: 1,
        name: 'احمد محمدی',
        phone: '09123456789',
        status: 'approved',
        registrationDate: '2024-01-15',
        lastLogin: '2024-01-20'
    },
    {
        id: 2,
        name: 'فاطمه احمدی',
        phone: '09187654321',
        status: 'pending',
        registrationDate: '2024-01-18',
        lastLogin: '2024-01-19'
    },
    {
        id: 3,
        name: 'علی رضایی',
        phone: '09111223344',
        status: 'approved',
        registrationDate: '2024-01-10',
        lastLogin: '2024-01-21'
    },
    {
        id: 4,
        name: 'مریم کریمی',
        phone: '09155667788',
        status: 'deactive',
        registrationDate: '2024-01-05',
        lastLogin: '2024-01-12'
    },
    {
        id: 5,
        name: 'حسین نوری',
        phone: '09199887766',
        status: 'approved',
        registrationDate: '2024-01-20',
        lastLogin: '2024-01-21'
    }
];

// Test data for products
const testProducts = [
    {
        id: 1,
        name: 'کاغذ A4 تحریر',
        type: 'cash',
        paperType: 'کاغذ تحریر',
        grammage: '80 گرم',
        size: 'A4 (210×297)',
        color: 'سفید',
        price: 25000,
        stock: 150,
        status: 'active'
    },
    {
        id: 2,
        name: 'کاغذ A3 تحریر',
        type: 'cash',
        paperType: 'کاغذ تحریر',
        grammage: '80 گرم',
        size: 'A3 (297×420)',
        color: 'سفید',
        price: 45000,
        stock: 80,
        status: 'active'
    },
    {
        id: 3,
        name: 'کاغذ رنگی آبی',
        type: 'credit',
        paperType: 'کاغذ رنگی',
        grammage: '120 گرم',
        size: 'A4 (210×297)',
        color: 'آبی',
        price: 35000,
        stock: 45,
        status: 'active'
    },
    {
        id: 4,
        name: 'کاغذ گلاسه',
        type: 'cash',
        paperType: 'کاغذ گلاسه',
        grammage: '150 گرم',
        size: 'A4 (210×297)',
        color: 'سفید',
        price: 55000,
        stock: 60,
        status: 'active'
    },
    {
        id: 5,
        name: 'کاغذ کاهی',
        type: 'credit',
        paperType: 'کاغذ کاهی',
        grammage: '70 گرم',
        size: 'A4 (210×297)',
        color: 'کاهی',
        price: 18000,
        stock: 200,
        status: 'active'
    }
];

// Test data for orders
const testOrders = [
    {
        id: 'ORD-001',
        customer: 'احمد محمدی',
        products: 'کاغذ A4 تحریر (2 عدد)',
        totalAmount: 50000,
        paymentType: 'cash',
        status: 'confirmed',
        orderDate: '2024-01-20'
    },
    {
        id: 'ORD-002',
        customer: 'فاطمه احمدی',
        products: 'کاغذ رنگی آبی (1 عدد), کاغذ گلاسه (1 عدد)',
        totalAmount: 90000,
        paymentType: 'credit',
        status: 'pending',
        orderDate: '2024-01-21'
    },
    {
        id: 'ORD-003',
        customer: 'علی رضایی',
        products: 'کاغذ A3 تحریر (3 عدد)',
        totalAmount: 135000,
        paymentType: 'cash',
        status: 'processing',
        orderDate: '2024-01-19'
    }
];

// Working hours configuration
let workingHours = {
    startHour: 8,
    startMinute: 0,
    endHour: 18,
    endMinute: 0,
    isActive: true
};

// Load working hours from localStorage
function loadWorkingHours() {
    const saved = localStorage.getItem('workingHours');
    if (saved) {
        workingHours = JSON.parse(saved);
    }
    updateWorkingHoursDisplay();
}

// Save working hours to localStorage
function saveWorkingHours() {
    localStorage.setItem('workingHours', JSON.stringify(workingHours));
}

// Update working hours display
function updateWorkingHoursDisplay() {
    const startHourElement = document.getElementById('startHour');
    const startMinuteElement = document.getElementById('startMinute');
    const endHourElement = document.getElementById('endHour');
    const endMinuteElement = document.getElementById('endMinute');
    const isActiveElement = document.getElementById('isActive');

    if (startHourElement) startHourElement.value = workingHours.startHour;
    if (startMinuteElement) startMinuteElement.value = workingHours.startMinute;
    if (endHourElement) endHourElement.value = workingHours.endHour;
    if (endMinuteElement) endMinuteElement.value = workingHours.endMinute;
    if (isActiveElement) isActiveElement.checked = workingHours.isActive;

    // Update display elements
    const currentStartTime = document.getElementById('currentStartTime');
    const currentEndTime = document.getElementById('currentEndTime');
    const workingHoursStatus = document.getElementById('workingHoursStatus');
    const currentWorkingStatus = document.getElementById('currentWorkingStatus');

    if (currentStartTime) {
        currentStartTime.textContent = PersianNumbers.formatWorkingHours(workingHours.startHour, workingHours.startMinute);
    }
    if (currentEndTime) {
        currentEndTime.textContent = PersianNumbers.formatWorkingHours(workingHours.endHour, workingHours.endMinute);
    }
    if (workingHoursStatus) {
        workingHoursStatus.textContent = workingHours.isActive ? 'فعال' : 'غیرفعال';
        workingHoursStatus.className = `status-indicator ${workingHours.isActive ? 'active' : 'inactive'}`;
    }
    if (currentWorkingStatus) {
        const isOpen = isWithinWorkingHours();
        currentWorkingStatus.textContent = isOpen ? 'باز' : 'بسته';
        currentWorkingStatus.className = `status-value ${isOpen ? 'open' : 'closed'}`;
    }
}

// Check if current time is within working hours
function isWithinWorkingHours() {
    if (!workingHours.isActive) return false;

    const now = new Date();
    const currentHour = now.getHours();
    const currentMinute = now.getMinutes();
    const currentTime = currentHour * 60 + currentMinute;

    const startTime = workingHours.startHour * 60 + workingHours.startMinute;
    const endTime = workingHours.endHour * 60 + workingHours.endMinute;

    return currentTime >= startTime && currentTime <= endTime;
}

// Initialize admin panel
function initializeAdmin() {
    loadWorkingHours();
    loadUsers();
    loadProducts();
    loadOrders();
    showSection('cms');
}

// Show specific section
function showSection(sectionName) {
    // Hide all sections
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(section => section.classList.remove('active'));

    // Show selected section
    const selectedSection = document.getElementById(sectionName);
    if (selectedSection) {
        selectedSection.classList.add('active');
    }

    // Update navigation buttons
    const navButtons = document.querySelectorAll('.nav-btn');
    navButtons.forEach(btn => btn.classList.remove('active'));

    const activeButton = document.querySelector(`[data-section="${sectionName}"]`);
    if (activeButton) {
        activeButton.classList.add('active');
    }

    // Update section title
    const sectionTitle = document.getElementById('sectionTitle');
    if (sectionTitle) {
        const titles = {
            'cms': 'مدیریت کاربران',
            'inventory': 'مدیریت موجودی',
            'orders': 'مدیریت سفارشات',
            'working-hours': 'ساعت کاری'
        };
        sectionTitle.textContent = titles[sectionName] || 'پنل مدیریت';
    }
}

// Load users into table
function loadUsers() {
    const tableBody = document.getElementById('usersTableBody');
    if (!tableBody) return;

    tableBody.innerHTML = testUsers.map(user => `
        <tr>
            <td>${PersianNumbers.formatUserId(user.id)}</td>
            <td>${user.name}</td>
            <td>${PersianNumbers.formatPhone(user.phone)}</td>
            <td><span class="status-indicator ${user.status}">${getStatusText(user.status)}</span></td>
            <td>${PersianNumbers.formatDate(user.registrationDate)}</td>
            <td>${PersianNumbers.formatDate(user.lastLogin)}</td>
            <td>
                <button class="action-btn edit-btn" onclick="editUser(${user.id})">ویرایش</button>
                <button class="action-btn delete-btn" onclick="deleteUser(${user.id})">حذف</button>
            </td>
        </tr>
    `).join('');
}

// Load products into table
function loadProducts() {
    const tableBody = document.getElementById('productsTableBody');
    if (!tableBody) return;

    tableBody.innerHTML = testProducts.map(product => `
        <tr>
            <td>${PersianNumbers.formatProductId(product.id)}</td>
            <td>${product.name}</td>
            <td>${product.type === 'cash' ? 'نقدی' : 'نسیه'}</td>
            <td>${product.paperType}</td>
            <td>${product.grammage}</td>
            <td>${product.size}</td>
            <td>${product.color}</td>
            <td>${PersianNumbers.formatPrice(product.price)}</td>
            <td>${PersianNumbers.formatStock(product.stock)}</td>
            <td><span class="status-indicator ${product.status}">${getStatusText(product.status)}</span></td>
            <td>
                <button class="action-btn edit-btn" onclick="editProduct(${product.id})">ویرایش</button>
                <button class="action-btn delete-btn" onclick="deleteProduct(${product.id})">حذف</button>
            </td>
        </tr>
    `).join('');
}

// Load orders into table
function loadOrders() {
    const tableBody = document.getElementById('ordersTableBody');
    if (!tableBody) return;

    tableBody.innerHTML = testOrders.map(order => `
        <tr>
            <td>${PersianNumbers.formatOrderId(order.id)}</td>
            <td>${order.customer}</td>
            <td>${order.products}</td>
            <td>${PersianNumbers.formatTotalAmount(order.totalAmount)}</td>
            <td>${order.paymentType === 'cash' ? 'نقدی' : 'نسیه'}</td>
            <td><span class="status-indicator ${order.status}">${getOrderStatusText(order.status)}</span></td>
            <td>${PersianNumbers.formatDate(order.orderDate)}</td>
            <td>
                <button class="action-btn view-btn" onclick="viewOrderDetails('${order.id}')">مشاهده</button>
                <button class="action-btn edit-btn" onclick="updateOrderStatus('${order.id}')">وضعیت</button>
            </td>
        </tr>
    `).join('');
}

// Get status text
function getStatusText(status) {
    const statusMap = {
        'approved': 'تایید شده',
        'pending': 'در انتظار',
        'deactive': 'غیرفعال'
    };
    return statusMap[status] || status;
}

// Get order status text
function getOrderStatusText(status) {
    const statusMap = {
        'pending': 'در انتظار',
        'confirmed': 'تایید شده',
        'processing': 'در حال پردازش',
        'shipped': 'ارسال شده',
        'delivered': 'تحویل داده شده',
        'cancelled': 'لغو شده'
    };
    return statusMap[status] || status;
}

// Filter functions
function filterUsers() {
    // Implementation for user filtering
    console.log('Filtering users...');
}

function filterProducts() {
    // Implementation for product filtering
    console.log('Filtering products...');
}

function filterOrders() {
    // Implementation for order filtering
    console.log('Filtering orders...');
}

// Modal functions
function showAddUserModal() {
    document.getElementById('addUserModal').style.display = 'flex';
}

function showAddProductModal() {
    document.getElementById('addProductModal').style.display = 'flex';
}

function showWorkingHoursModal() {
    updateWorkingHoursDisplay();
    document.getElementById('workingHoursModal').style.display = 'flex';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Form submission handlers
document.addEventListener('DOMContentLoaded', function () {
    // Add user form
    const addUserForm = document.getElementById('addUserForm');
    if (addUserForm) {
        addUserForm.addEventListener('submit', function (e) {
            e.preventDefault();
            // Handle add user
            console.log('Adding new user...');
            closeModal('addUserModal');
        });
    }

    // Add product form
    const addProductForm = document.getElementById('addProductForm');
    if (addProductForm) {
        addProductForm.addEventListener('submit', function (e) {
            e.preventDefault();
            // Handle add product
            console.log('Adding new product...');
            closeModal('addProductModal');
        });
    }

    // Working hours form
    const workingHoursForm = document.getElementById('workingHoursForm');
    if (workingHoursForm) {
        workingHoursForm.addEventListener('submit', function (e) {
            e.preventDefault();
            saveWorkingHoursFromForm();
        });
    }
});

// Save working hours from form
function saveWorkingHoursFromForm() {
    workingHours.startHour = parseInt(document.getElementById('startHour').value);
    workingHours.startMinute = parseInt(document.getElementById('startMinute').value);
    workingHours.endHour = parseInt(document.getElementById('endHour').value);
    workingHours.endMinute = parseInt(document.getElementById('endMinute').value);
    workingHours.isActive = document.getElementById('isActive').checked;

    saveWorkingHours();
    updateWorkingHoursDisplay();
    showMessage('ساعت کاری با موفقیت ذخیره شد', 'success');
    closeModal('workingHoursModal');
}

// Export functions
function exportUsers() {
    console.log('Exporting users...');
    showMessage('گزارش کاربران در حال آماده‌سازی است', 'info');
}

function exportInventory() {
    console.log('Exporting inventory...');
    showMessage('گزارش موجودی در حال آماده‌سازی است', 'info');
}

function exportOrders() {
    console.log('Exporting orders...');
    showMessage('گزارش سفارشات در حال آماده‌سازی است', 'info');
}

// Action functions
function editUser(userId) {
    console.log('Editing user:', userId);
}

function deleteUser(userId) {
    if (confirm('آیا از حذف این کاربر اطمینان دارید؟')) {
        console.log('Deleting user:', userId);
    }
}

function editProduct(productId) {
    console.log('Editing product:', productId);
}

function deleteProduct(productId) {
    if (confirm('آیا از حذف این محصول اطمینان دارید؟')) {
        console.log('Deleting product:', productId);
    }
}

function viewOrderDetails(orderId) {
    console.log('Viewing order details:', orderId);
    document.getElementById('orderDetailsModal').style.display = 'flex';
}

function updateOrderStatus(orderId) {
    console.log('Updating order status:', orderId);
}

function showOrderStats() {
    console.log('Showing order statistics...');
}

// Admin logout
function adminLogout() {
    if (confirm('آیا از خروج اطمینان دارید؟')) {
        window.location.href = 'login.html';
    }
}

// Show message
function showMessage(message, type = 'info') {
    // Create message element
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${type}`;
    messageDiv.textContent = message;

    // Add to page
    document.body.appendChild(messageDiv);

    // Remove after 3 seconds
    setTimeout(() => {
        messageDiv.remove();
    }, 3000);
}

// Working hours functions
function testWorkingHours() {
    const isOpen = isWithinWorkingHours();
    const message = isOpen ?
        'سایت در حال حاضر باز است و در ساعت کاری قرار دارد.' :
        'سایت در حال حاضر بسته است و خارج از ساعت کاری قرار دارد.';
    const type = isOpen ? 'success' : 'warning';
    showMessage(message, type);
}

function exportWorkingHours() {
    console.log('Exporting working hours...');
    showMessage('گزارش ساعت کاری در حال آماده‌سازی است', 'info');
}

// Main page content configuration
let mainPageContent = {
    cashPrice: 2500000,
    cashStock: 150,
    creditPrice: 2800000,
    creditStock: 200
};

// Load main page content from localStorage
function loadMainPageContent() {
    const saved = localStorage.getItem('mainPageContent');
    if (saved) {
        mainPageContent = JSON.parse(saved);
    }
    updateMainPageDisplay();
}

// Save main page content to localStorage
function saveMainPageContent() {
    localStorage.setItem('mainPageContent', JSON.stringify(mainPageContent));
}

// Update main page display
function updateMainPageDisplay() {
    const currentCashPrice = document.getElementById('currentCashPrice');
    const currentCashStock = document.getElementById('currentCashStock');
    const currentCreditPrice = document.getElementById('currentCreditPrice');
    const currentCreditStock = document.getElementById('currentCreditStock');

    if (currentCashPrice) {
        currentCashPrice.textContent = PersianNumbers.formatPrice(mainPageContent.cashPrice);
    }
    if (currentCashStock) {
        currentCashStock.textContent = PersianNumbers.formatStock(mainPageContent.cashStock) + ' کیلو';
    }
    if (currentCreditPrice) {
        currentCreditPrice.textContent = PersianNumbers.formatPrice(mainPageContent.creditPrice);
    }
    if (currentCreditStock) {
        currentCreditStock.textContent = PersianNumbers.formatStock(mainPageContent.creditStock) + ' کیلو';
    }
}

// Format price to Persian numbers (updated to use utility function)
function formatPrice(price) {
    return PersianNumbers.formatPrice(price);
}

// Main page management functions
function showMainPageEditModal() {
    // Load current values into form
    document.getElementById('cashPrice').value = mainPageContent.cashPrice;
    document.getElementById('cashStock').value = mainPageContent.cashStock;
    document.getElementById('creditPrice').value = mainPageContent.creditPrice;
    document.getElementById('creditStock').value = mainPageContent.creditStock;

    document.getElementById('mainPageEditModal').style.display = 'flex';
}

function saveMainPageFromForm() {
    mainPageContent.cashPrice = parseInt(document.getElementById('cashPrice').value);
    mainPageContent.cashStock = parseInt(document.getElementById('cashStock').value);
    mainPageContent.creditPrice = parseInt(document.getElementById('creditPrice').value);
    mainPageContent.creditStock = parseInt(document.getElementById('creditStock').value);

    saveMainPageContent();
    updateMainPageDisplay();
    showMessage('اطلاعات صفحه اصلی با موفقیت ذخیره شد', 'success');
    closeModal('mainPageEditModal');
}

function previewMainPage() {
    window.open('index.html', '_blank');
}

function exportMainPageData() {
    console.log('Exporting main page data...');
    showMessage('گزارش صفحه اصلی در حال آماده‌سازی است', 'info');
}

// Mobile menu functions
function toggleSidebar() {
    const sidebar = document.getElementById('adminSidebar');
    sidebar.classList.toggle('active');
}

function showMobileSearch() {
    document.getElementById('mobileSearchOverlay').classList.add('active');
}

function hideMobileSearch() {
    document.getElementById('mobileSearchOverlay').classList.remove('active');
}

function showMobileMenu() {
    document.getElementById('mobileMenuOverlay').classList.add('active');
}

function hideMobileMenu() {
    document.getElementById('mobileMenuOverlay').classList.remove('active');
}

function performMobileSearch() {
    const searchTerm = document.getElementById('mobileSearchInput').value;
    console.log('Mobile search:', searchTerm);
    hideMobileSearch();
    showMessage('جستجو در حال انجام است', 'info');
}

// Initialize when page loads
window.addEventListener('load', function () {
    initializeAdmin();
    loadMainPageContent();

    // Add main page edit form handler
    const mainPageEditForm = document.getElementById('mainPageEditForm');
    if (mainPageEditForm) {
        mainPageEditForm.addEventListener('submit', function (e) {
            e.preventDefault();
            saveMainPageFromForm();
        });
    }

    // Close mobile overlays when clicking outside
    document.addEventListener('click', function (e) {
        if (e.target.classList.contains('mobile-menu-overlay')) {
            hideMobileMenu();
        }
        if (e.target.classList.contains('mobile-search-overlay')) {
            hideMobileSearch();
        }
    });
}); 
