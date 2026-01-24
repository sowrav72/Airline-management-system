// ========================================
// SKYLINK AIRLINES - RESET PASSWORD SCRIPT
// ========================================

// Get token from URL
const urlParams = new URLSearchParams(window.location.search);
const token = urlParams.get('token');

if (!token) {
    alert('❌ Invalid reset link. Please request a new password reset.');
    window.location.href = '/forgot-password';
}

document.getElementById('resetPasswordForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    // Validate password length
    if (password.length < 6) {
        alert('❌ Password must be at least 6 characters long!');
        return;
    }
    
    // Check if passwords match
    if (password !== confirmPassword) {
        alert('❌ Passwords do not match!');
        return;
    }
    
    // Disable submit button
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = 'Resetting...';
    
    try {
        const response = await fetch('/api/reset-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                token: token,
                new_password: password
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('✅ ' + data.message);
            window.location.href = '/login';
        } else {
            alert('❌ Error: ' + (data.detail || 'Password reset failed'));
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    } catch (error) {
        alert('❌ Network error: ' + error.message);
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    }
});