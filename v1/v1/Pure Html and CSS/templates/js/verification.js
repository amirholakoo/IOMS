// Verification state
        let currentStep = 1;
        let verificationCode = '';
        let countdownTimer = null;
        let resendTimer = null;

        // Initialize page
        function initializePage() {
            // Load phone number from session storage
            const userPhone = sessionStorage.getItem('userPhone') || '09123456789';
            document.getElementById('userPhoneDisplay').textContent = userPhone;

            // Generate verification code
            generateVerificationCode();

            // Start countdown
            startCountdown();
        }

        // Generate 6-digit verification code
        function generateVerificationCode() {
            verificationCode = Math.floor(100000 + Math.random() * 900000).toString();
            displayCode(verificationCode);
        }

        // Display code in digits
        function displayCode(code) {
            for (let i = 0; i < 6; i++) {
                const digitElement = document.getElementById(`digit${i + 1}`);
                if (digitElement) {
                    digitElement.textContent = code[i] || '-';
                }
            }
        }

        // Copy code to clipboard
        function copyCode() {
            navigator.clipboard.writeText(verificationCode).then(() => {
                showMessage('کد در کلیپ‌بورد کپی شد', 'success');
            }).catch(() => {
                showMessage('خطا در کپی کردن کد', 'error');
            });
        }

        // Go to step 2
        function goToStep2() {
            currentStep = 2;
            updateStepIndicator();
            showStepContent();
        }

        // Update step indicator
        function updateStepIndicator() {
            document.getElementById('step1').className = currentStep >= 1 ? 'step completed' : 'step active';
            document.getElementById('step2').className = currentStep >= 2 ? 'step active' : 'step pending';
        }

        // Show current step content
        function showStepContent() {
            document.querySelectorAll('.step-content').forEach(content => {
                content.classList.remove('active');
            });

            document.getElementById(`step${currentStep}Content`).classList.add('active');
        }

        // Handle form submission
        function handleVerifySubmit(event) {
            event.preventDefault();

            const inputCode = document.getElementById('otpCode').value;

            if (inputCode === verificationCode) {
                showMessage('کد تایید صحیح است', 'success');

                // Store verification status
                sessionStorage.setItem('isVerified', 'true');
                sessionStorage.setItem('userName', 'کاربر تایید شده');

                // Redirect to shopping page
                setTimeout(() => {
                    window.location.href = 'shopping.html';
                }, 1500);
            } else {
                showMessage('کد تایید اشتباه است', 'error');
                document.getElementById('otpCode').value = '';
                document.getElementById('otpCode').focus();
            }
        }

        // Resend code
        function resendCode() {
            generateVerificationCode();
            startCountdown();
            showMessage('کد جدید ارسال شد', 'success');
        }

        // Start countdown timer
        function startCountdown() {
            let countdown = 60;
            const countdownElement = document.getElementById('resendCountdown');
            const resendBtn = document.getElementById('resendBtn');

            resendBtn.disabled = true;

            countdownTimer = setInterval(() => {
                countdown--;
                if (countdownElement) {
                    countdownElement.textContent = countdown;
                }

                if (countdown <= 0) {
                    clearInterval(countdownTimer);
                    resendBtn.disabled = false;
                    if (countdownElement) {
                        countdownElement.textContent = 'آماده';
                    }
                }
            }, 1000);
        }

        // Show message
        function showMessage(message, type = 'info') {
            // Remove existing message
            const existingMessage = document.querySelector('.message-popup');
            if (existingMessage) {
                existingMessage.remove();
            }

            // Create message element
            const messageDiv = document.createElement('div');
            messageDiv.className = `message-popup message-${type}`;
            messageDiv.innerHTML = `
                <div class="message-content">
                    <span class="message-text">${message}</span>
                    <button class="message-close" onclick="this.parentElement.parentElement.remove()">×</button>
                </div>
            `;

            // Add to page
            document.body.appendChild(messageDiv);

            // Auto remove after 5 seconds
            setTimeout(() => {
                if (messageDiv.parentElement) {
                    messageDiv.remove();
                }
            }, 5000);
        }

        // Initialize when page loads
        window.addEventListener('load', initializePage);
