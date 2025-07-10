// Simple Admin Panel JavaScript

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
        status: 'deactivate',
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
        paperType: 'کاغذ تحریر',
        grammage: '80 گرم',
        size: 'A4 (210×297)',
        color: 'سفید',
        cashPrice: 25000,
        creditPrice: 28000,
        stock: 150,
        status: 'active'
    },
    {
        id: 2,
        name: 'کاغذ A3 تحریر',
        paperType: 'کاغذ تحریر',
        grammage: '80 گرم',
        size: 'A3 (297×420)',
        color: 'سفید',
        cashPrice: 45000,
        creditPrice: 50000,
        stock: 80,
        status: 'active'
    },
    {
        id: 3,
        name: 'کاغذ رنگی آبی',
        paperType: 'کاغذ رنگی',
        grammage: '120 گرم',
        size: 'A4 (210×297)',
        color: 'آبی',
        cashPrice: 35000,
        creditPrice: 39000,
        stock: 45,
        status: 'active'
    },
    {
        id: 4,
        name: 'کاغذ گلاسه',
        paperType: 'کاغذ گلاسه',
        grammage: '150 گرم',
        size: 'A4 (210×297)',
        color: 'سفید',
        cashPrice: 55000,
        creditPrice: 62000,
        stock: 60,
        status: 'active'
    },
    {
        id: 5,
        name: 'کاغذ کاهی',
        paperType: 'کاغذ کاهی',
        grammage: '70 گرم',
        size: 'A4 (210×297)',
        color: 'کاهی',
        cashPrice: 18000,
        creditPrice: 20000,
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

// Store filtered data
let filteredUsers = [...testUsers];
let filteredProducts = [...testProducts];
let filteredOrders = [...testOrders];

// Working hours configuration
let workingHours = {
    startHour: 8,
    startMinute: 0,
    endHour: 18,
    endMinute: 0,
    isActive: true
};

// Main page content configuration
let mainPageContent = {
    cashPrice: 2500000,
    cashStock: 150,
    creditPrice: 2800000,
    creditStock: 200
};

// === SIMPLE MOBILE MENU ===
function toggleMenu() {
    const menu = document.getElementById('mobileMenu');
    const overlay = document.getElementById('menuOverlay');

    menu.classList.toggle('active');
    overlay.classList.toggle('active');
}

function closeMenu() {
    const menu = document.getElementById('mobileMenu');
    const overlay = document.getElementById('menuOverlay');

    menu.classList.remove('active');
    overlay.classList.remove('active');
}

function goHome() {
    window.location.href = '../Index/index.html';
}

// Show specific section
function showSection(sectionName) {
    // Close mobile menu
    closeMenu();

    // Hide all sections
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(section => section.classList.remove('active'));

    // Show selected section
    const selectedSection = document.getElementById(sectionName);
    if (selectedSection) {
        selectedSection.classList.add('active');
    }

    // Update section title
    const sectionTitle = document.getElementById('sectionTitle');
    if (sectionTitle) {
        const titles = {
            'dashboard': 'داشبورد مدیریت',
            'cms': 'مدیریت کاربران',
            'inventory': 'مدیریت موجودی',
            'orders': 'مدیریت سفارشات',
            'working-hours': 'ساعت کاری',
            'main-page': 'مدیریت صفحه اصلی'
        };
        sectionTitle.textContent = titles[sectionName] || 'پنل مدیریت';
    }
}

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
    workingHours.startHour = Number(workingHours.startHour);
    workingHours.startMinute = Number(workingHours.startMinute);
    workingHours.endHour = Number(workingHours.endHour);
    workingHours.endMinute = Number(workingHours.endMinute);
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

    if (currentStartTime) {
        currentStartTime.textContent = PersianNumbers.formatWorkingHours(workingHours.startHour, workingHours.startMinute);
    }
    if (currentEndTime) {
        currentEndTime.textContent = PersianNumbers.formatWorkingHours(workingHours.endHour, workingHours.endMinute);
    }
    if (workingHoursStatus) {
        workingHoursStatus.textContent = workingHours.isActive ? 'فعال' : 'غیرفعال';
    }

    // اتوماتیک بررسی وضعیت فعلی بر اساس زمان واقعی
    updateCurrentWorkingStatus();
}

// تابع جداگانه برای بروزرسانی وضعیت فعلی
function updateCurrentWorkingStatus() {
    const currentWorkingStatus = document.getElementById('currentWorkingStatus');
    if (currentWorkingStatus) {
        const isOpen = isWithinWorkingHours();
        currentWorkingStatus.textContent = isOpen ? 'باز' : 'بسته';
        currentWorkingStatus.className = `status-value ${isOpen ? 'open' : 'closed'}`;
    }
}

function getIranTimeManual() {
    const now = new Date();
    const utcMinutes = now.getUTCHours() * 60 + now.getUTCMinutes();
    const tehranOffset = 270; // +3:30 in minutes
    const totalMinutes = (utcMinutes + tehranOffset) % (24 * 60);
    const hour = Math.floor(totalMinutes / 60);
    const minute = totalMinutes % 60;
    return { hour, minute };
}


// Check if current time is within working hours
function isWithinWorkingHours() {
    if (!workingHours.isActive) return false;

    const iranTime = getIranTimeManual();  // نسخه بدون DST
    const currentHour = iranTime.hour;
    const currentMinute = iranTime.minute;
    const currentTime = currentHour * 60 + currentMinute;

    const startHour = Number(workingHours.startHour);
    const startMinute = Number(workingHours.startMinute);
    const endHour = Number(workingHours.endHour);
    const endMinute = Number(workingHours.endMinute);

    const startTime = startHour * 60 + startMinute;
    const endTime = endHour * 60 + endMinute;

    console.log({ currentTime, startTime, endTime, iranTime });

    return currentTime >= startTime && currentTime <= endTime;
}

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

// Load users into table
function loadUsers(usersToShow = filteredUsers) {
    const tableBody = document.getElementById('usersTableBody');
    if (!tableBody) return;

    tableBody.innerHTML = usersToShow.map(user => `
        <tr>
            <td>${user.name}</td>
            <td>${PersianNumbers.formatPhone(user.phone)}</td>
            <td><span class="status-badge status-${user.status}">${getStatusText(user.status)}</span></td>
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
function loadProducts(productsToShow = filteredProducts) {
    const tableBody = document.getElementById('productsTableBody');
    if (!tableBody) return;

    tableBody.innerHTML = productsToShow.map(product => `
        <tr>
            <td>${product.name}</td>
            <td>${product.paperType} - ${product.grammage} - ${product.size} - ${product.color}</td>
            <td>${PersianNumbers.formatPrice(product.cashPrice)}</td>
            <td>${PersianNumbers.formatPrice(product.creditPrice)}</td>
            <td>${PersianNumbers.formatStock(product.stock)}</td>
            <td><span class="status-badge status-${product.status}">${getStatusText(product.status)}</span></td>
            <td>
                <button class="action-btn edit-btn" onclick="editProduct(${product.id})">ویرایش</button>
                <button class="action-btn delete-btn" onclick="deleteProduct(${product.id})">حذف</button>
            </td>
        </tr>
    `).join('');
}

// Load orders into table
function loadOrders(ordersToShow = filteredOrders) {
    const tableBody = document.getElementById('ordersTableBody');
    if (!tableBody) return;

    tableBody.innerHTML = ordersToShow.map(order => `
        <tr>
            <td>${PersianNumbers.formatOrderId(order.id)}</td>
            <td>${order.customer}</td>
            <td>${order.products}</td>
            <td>${PersianNumbers.formatTotalAmount(order.totalAmount)}</td>
            <td>${order.paymentType === 'cash' ? 'نقدی' : 'نسیه'}</td>
            <td><span class="status-badge status-${order.status}">${getOrderStatusText(order.status)}</span></td>
            <td>${PersianNumbers.formatDate(order.orderDate)}</td>
            <td>
                <button class="action-btn view-btn" onclick="viewOrderDetails('${order.id}')">مشاهده</button>
                <button class="action-btn edit-btn" onclick="updateOrderStatus('${order.id}')">وضعیت</button>
                <button class="action-btn delete-btn" onclick="deleteOrder('${order.id}')">حذف</button>
            </td>
        </tr>
    `).join('');
}

// Get status text
function getStatusText(status) {
    const statusMap = {
        'approved': 'تایید شده',
        'pending': 'در انتظار',
        'deactive': 'غیرفعال',
        'active': 'فعال'
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
    const statusFilter = document.getElementById('userStatusFilter').value;
    const searchFilter = document.getElementById('userSearch').value.toLowerCase();

    filteredUsers = testUsers.filter(user => {
        const statusMatch = !statusFilter || user.status === statusFilter;
        const searchMatch = !searchFilter ||
            user.name.toLowerCase().includes(searchFilter) ||
            user.phone.includes(searchFilter);

        return statusMatch && searchMatch;
    });

    loadUsers(filteredUsers);
}

function filterProducts() {
    const stockFilter = document.getElementById('stockFilter').value;
    const searchFilter = document.getElementById('productSearch').value.toLowerCase();

    filteredProducts = testProducts.filter(product => {
        const stockMatch = !stockFilter || getStockLevel(product.stock) === stockFilter;
        const searchMatch = !searchFilter ||
            product.name.toLowerCase().includes(searchFilter) ||
            product.paperType.toLowerCase().includes(searchFilter);

        return stockMatch && searchMatch;
    });

    loadProducts(filteredProducts);
}

function filterOrders() {
    const statusFilter = document.getElementById('orderStatusFilter').value;
    const paymentFilter = document.getElementById('paymentTypeFilter').value;
    const dateFromFilter = document.getElementById('dateFromFilter').value;
    const dateToFilter = document.getElementById('dateToFilter').value;
    const searchFilter = document.getElementById('orderSearch').value.toLowerCase();

    filteredOrders = testOrders.filter(order => {
        const statusMatch = !statusFilter || order.status === statusFilter;
        const paymentMatch = !paymentFilter || order.paymentType === paymentFilter;
        const searchMatch = !searchFilter ||
            order.id.toLowerCase().includes(searchFilter) ||
            order.customer.toLowerCase().includes(searchFilter);

        // Date filtering
        let dateMatch = true;
        if (dateFromFilter || dateToFilter) {
            const orderDate = new Date(order.orderDate);
            if (dateFromFilter) {
                const fromDate = new Date(dateFromFilter);
                dateMatch = dateMatch && orderDate >= fromDate;
            }
            if (dateToFilter) {
                const toDate = new Date(dateToFilter);
                dateMatch = dateMatch && orderDate <= toDate;
            }
        }

        return statusMatch && paymentMatch && searchMatch && dateMatch;
    });

    loadOrders(filteredOrders);
}

// Get stock level for filtering
function getStockLevel(stock) {
    if (stock <= 0) return 'out';
    if (stock <= 50) return 'low';
    if (stock <= 100) return 'medium';
    return 'high';
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

function showMainPageEditModal() {
    // Load current values into form
    document.getElementById('cashPrice').value = mainPageContent.cashPrice;
    document.getElementById('cashStock').value = mainPageContent.cashStock;
    document.getElementById('creditPrice').value = mainPageContent.creditPrice;
    document.getElementById('creditStock').value = mainPageContent.creditStock;

    document.getElementById('mainPageEditModal').style.display = 'flex';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Edit user function
function editUser(userId) {
    const user = testUsers.find(u => u.id === userId);
    if (!user) return;

    document.getElementById('editUserId').value = user.id;
    document.getElementById('editUserName').value = user.name;
    document.getElementById('editUserPhone').value = user.phone;
    document.getElementById('editUserStatus').value = user.status;

    document.getElementById('editUserModal').style.display = 'flex';
}

// Edit product function
function editProduct(productId) {
    const product = testProducts.find(p => p.id === productId);
    if (!product) return;

    document.getElementById('editProductId').value = product.id;
    document.getElementById('editProductName').value = product.name;
    document.getElementById('editProductCashPrice').value = product.cashPrice;
    document.getElementById('editProductCreditPrice').value = product.creditPrice;
    document.getElementById('editProductStock').value = product.stock;

    document.getElementById('editProductModal').style.display = 'flex';
}

// Update order status function
function updateOrderStatus(orderId) {
    const order = testOrders.find(o => o.id === orderId);
    if (!order) return;

    document.getElementById('orderStatusId').value = order.id;
    document.getElementById('newOrderStatus').value = order.status;

    document.getElementById('orderStatusModal').style.display = 'flex';
}

function viewOrderDetails(orderId) {
    const order = testOrders.find(o => o.id === orderId);
    if (!order) return;

    const orderDetailsContent = document.getElementById('orderDetailsContent');
    orderDetailsContent.innerHTML = `
        <div class="order-details">
            <div class="detail-section">
                <h4>اطلاعات سفارش</h4>
                <p><strong>شماره سفارش:</strong> ${order.id}</p>
                <p><strong>مشتری:</strong> ${order.customer}</p>
                <p><strong>تاریخ سفارش:</strong> ${PersianNumbers.formatDate(order.orderDate)}</p>
                <p><strong>نوع پرداخت:</strong> ${order.paymentType === 'cash' ? 'نقدی' : 'نسیه'}</p>
                <p><strong>وضعیت:</strong> <span class="status-badge status-${order.status}">${getOrderStatusText(order.status)}</span></p>
            </div>
            <div class="detail-section">
                <h4>محصولات</h4>
                <p>${order.products}</p>
            </div>
            <div class="detail-section">
                <h4>مبلغ کل</h4>
                <p class="total-amount">${PersianNumbers.formatTotalAmount(order.totalAmount)}</p>
            </div>
        </div>
    `;

    document.getElementById('orderDetailsModal').style.display = 'flex';
}

// Delete functions
function deleteUser(userId) {
    if (confirm('آیا از حذف این کاربر اطمینان دارید؟')) {
        const index = testUsers.findIndex(u => u.id === userId);
        if (index !== -1) {
            testUsers.splice(index, 1);
            filterUsers();
            showMessage('کاربر با موفقیت حذف شد', 'success');
        }
    }
}

function deleteProduct(productId) {
    if (confirm('آیا از حذف این محصول اطمینان دارید؟')) {
        const index = testProducts.findIndex(p => p.id === productId);
        if (index !== -1) {
            testProducts.splice(index, 1);
            filterProducts();
            showMessage('محصول با موفقیت حذف شد', 'success');
        }
    }
}

function deleteOrder(orderId) {
    if (confirm('آیا از حذف این سفارش اطمینان دارید؟')) {
        const index = testOrders.findIndex(o => o.id === orderId);
        if (index !== -1) {
            testOrders.splice(index, 1);
            filterOrders();
            showMessage('سفارش با موفقیت حذف شد', 'success');
        }
    }
}

function saveWorkingHoursFromForm() {
    workingHours.startHour = parseInt(document.getElementById('startHour').value);
    workingHours.startMinute = parseInt(document.getElementById('startMinute').value);
    workingHours.endHour = parseInt(document.getElementById('endHour').value);
    workingHours.endMinute = parseInt(document.getElementById('endMinute').value);
    // Always keep working hours active for automatic operation
    workingHours.isActive = true;

    saveWorkingHours();
    updateWorkingHoursDisplay();
    showMessage('ساعت کاری با موفقیت ذخیره شد', 'success');
    closeModal('workingHoursModal');
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

function showOrderStats() {
    showMessage('نمایش آمار سفارشات در حال توسعه است', 'info');
}

function adminLogout() {
    if (confirm('آیا از خروج اطمینان دارید؟')) {
        window.location.href = '../Auth/login.html';
    }
}

// Show message
function showMessage(message, type = 'info') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${type}`;
    messageDiv.textContent = message;
    document.body.appendChild(messageDiv);

    setTimeout(() => {
        messageDiv.remove();
    }, 3000);
}

// Initialize admin panel
function initializeAdmin() {
    loadWorkingHours();
    loadUsers();
    loadProducts();
    loadOrders();
    loadMainPageContent();
    showSection('dashboard');

    // شروع تایمر اتوماتیک برای بررسی وضعیت ساعت کاری هر دقیقه
    startWorkingHoursTimer();
}

// تایمر اتوماتیک برای بررسی وضعیت ساعت کاری
function startWorkingHoursTimer() {
    // بررسی اولیه
    updateCurrentWorkingStatus();

    // بررسی هر ۶۰ ثانیه (۱ دقیقه)
    setInterval(function () {
        updateCurrentWorkingStatus();
    }, 60000);
}

// Form submission handlers
document.addEventListener('DOMContentLoaded', function () {
    // Add user form
    const addUserForm = document.getElementById('addUserForm');
    if (addUserForm) {
        addUserForm.addEventListener('submit', function (e) {
            e.preventDefault();

            const newUser = {
                id: Math.max(...testUsers.map(u => u.id)) + 1,
                name: document.getElementById('userName').value,
                phone: document.getElementById('userPhone').value,
                status: document.getElementById('userStatus').value,
                registrationDate: new Date().toISOString().split('T')[0],
                lastLogin: new Date().toISOString().split('T')[0]
            };

            testUsers.push(newUser);
            filterUsers();
            closeModal('addUserModal');
            showMessage('کاربر جدید با موفقیت اضافه شد', 'success');
        });
    }

    // Edit user form
    const editUserForm = document.getElementById('editUserForm');
    if (editUserForm) {
        editUserForm.addEventListener('submit', function (e) {
            e.preventDefault();

            const userId = parseInt(document.getElementById('editUserId').value);
            const userIndex = testUsers.findIndex(u => u.id === userId);

            if (userIndex !== -1) {
                testUsers[userIndex].name = document.getElementById('editUserName').value;
                testUsers[userIndex].phone = document.getElementById('editUserPhone').value;
                testUsers[userIndex].status = document.getElementById('editUserStatus').value;

                filterUsers();
                closeModal('editUserModal');
                showMessage('اطلاعات کاربر با موفقیت بروزرسانی شد', 'success');
            }
        });
    }

    // Add product form
    const addProductForm = document.getElementById('addProductForm');
    if (addProductForm) {
        addProductForm.addEventListener('submit', function (e) {
            e.preventDefault();

            const newProduct = {
                id: Math.max(...testProducts.map(p => p.id)) + 1,
                name: document.getElementById('productName').value,
                paperType: document.getElementById('productPaperType').value,
                grammage: document.getElementById('productGrammage').value,
                size: document.getElementById('productSize').value,
                color: document.getElementById('productColor').value,
                cashPrice: parseInt(document.getElementById('productCashPrice').value),
                creditPrice: parseInt(document.getElementById('productCreditPrice').value),
                stock: parseInt(document.getElementById('productStock').value),
                status: 'active'
            };

            testProducts.push(newProduct);
            filterProducts();
            closeModal('addProductModal');
            showMessage('محصول جدید با موفقیت اضافه شد', 'success');
        });
    }

    // Edit product form
    const editProductForm = document.getElementById('editProductForm');
    if (editProductForm) {
        editProductForm.addEventListener('submit', function (e) {
            e.preventDefault();

            const productId = parseInt(document.getElementById('editProductId').value);
            const productIndex = testProducts.findIndex(p => p.id === productId);

            if (productIndex !== -1) {
                testProducts[productIndex].name = document.getElementById('editProductName').value;
                testProducts[productIndex].cashPrice = parseInt(document.getElementById('editProductCashPrice').value);
                testProducts[productIndex].creditPrice = parseInt(document.getElementById('editProductCreditPrice').value);
                testProducts[productIndex].stock = parseInt(document.getElementById('editProductStock').value);

                filterProducts();
                closeModal('editProductModal');
                showMessage('اطلاعات محصول با موفقیت بروزرسانی شد', 'success');
            }
        });
    }

    // Order status form
    const orderStatusForm = document.getElementById('orderStatusForm');
    if (orderStatusForm) {
        orderStatusForm.addEventListener('submit', function (e) {
            e.preventDefault();

            const orderId = document.getElementById('orderStatusId').value;
            const orderIndex = testOrders.findIndex(o => o.id === orderId);

            if (orderIndex !== -1) {
                testOrders[orderIndex].status = document.getElementById('newOrderStatus').value;

                filterOrders();
                closeModal('orderStatusModal');
                showMessage('وضعیت سفارش با موفقیت تغییر کرد', 'success');
            }
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

    // Main page edit form
    const mainPageEditForm = document.getElementById('mainPageEditForm');
    if (mainPageEditForm) {
        mainPageEditForm.addEventListener('submit', function (e) {
            e.preventDefault();
            saveMainPageFromForm();
        });
    }
});

// Initialize when page loads
window.addEventListener('load', function () {
    initializeAdmin();
}); 
