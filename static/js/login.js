// ========================================
// SKYLINK AIRLINES - LOGIN SCRIPT
// ========================================

document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Get form data
    const formData = {
        email: document.getElementById('email').value.trim(),
        password: document.getElementById('password').value
    };
    
    // Validate inputs
    if (!formData.email || !formData.password) {
        alert('❌ Please fill in all fields!');
        return;
    }
    
    // Disable submit button
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = 'Logging in...';
    
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Store token and user info in localStorage
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('user', JSON.stringify(data.user));
            
            // Success message
            alert('✅ Login successful! Welcome back, ' + data.user.full_name + '!');
            
            // Redirect to dashboard
            window.location.href = '/dashboard';
        } else {
            // Error from server
            alert('❌ Error: ' + (data.detail || 'Invalid email or password'));
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