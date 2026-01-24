// ========================================
// SKYLINK AIRLINES - REGISTRATION SCRIPT
// ========================================

document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Get form data
    const formData = {
        email: document.getElementById('email').value.trim(),
        full_name: document.getElementById('fullName').value.trim(),
        password: document.getElementById('password').value,
        phone: document.getElementById('phone').value.trim() || null,
        role: document.getElementById('role').value
    };
    
    // Validate password length
    if (formData.password.length < 6) {
        alert('❌ Password must be at least 6 characters long!');
        return;
    }
    
    // Validate full name
    if (formData.full_name.length < 2) {
        alert('❌ Please enter a valid full name!');
        return;
    }
    
    // Disable submit button to prevent double submission
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = 'Creating Account...';
    
    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Success
            alert('✅ Registration successful! You can now login.');
            window.location.href = '/login';
        } else {
            // Error from server
            alert('❌ Error: ' + (data.detail || 'Registration failed. Please try again.'));
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    } catch (error) {
        // Network or other error
        alert('❌ Network error: ' + error.message + '\n\nPlease check your connection and try again.');
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    }
});