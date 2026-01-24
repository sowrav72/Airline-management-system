// ========================================
// SKYLINK AIRLINES - FORGOT PASSWORD SCRIPT
// ========================================

document.getElementById('forgotPasswordForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('email').value.trim();
    
    if (!email) {
        alert('❌ Please enter your email address!');
        return;
    }
    
    // Disable submit button
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = 'Sending...';
    
    try {
        const response = await fetch('/api/forgot-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email: email })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('✅ ' + data.message + '\n\nPlease check your email (or terminal console in development mode) for the password reset link.');
            // Clear form
            document.getElementById('email').value = '';
        } else {
            alert('❌ Error: ' + (data.detail || 'Failed to send reset email'));
        }
    } catch (error) {
        alert('❌ Network error: ' + error.message);
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    }
});