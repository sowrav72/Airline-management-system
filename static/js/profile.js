// ========================================
// SKYLINK AIRLINES - ENHANCED PROFILE SCRIPT
// ========================================

// Check if user is logged in
const token = localStorage.getItem('access_token');
if (!token) {
    alert('⚠️ Please login first!');
    window.location.href = '/login';
}

// Load current profile data
async function loadProfile() {
    try {
        const response = await fetch('/api/profile', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const user = await response.json();
            
            // Pre-fill form fields
            document.getElementById('fullName').value = user.full_name || '';
            document.getElementById('phone').value = user.phone || '';
            
            // Display profile photo if exists
            if (user.profile_photo) {
                document.getElementById('currentPhoto').src = user.profile_photo;
                document.getElementById('photoPreview').style.display = 'block';
                document.getElementById('deletePhotoBtn').style.display = 'inline-block';
            }
            
            // Show verification status
            if (!user.is_verified) {
                const verificationAlert = document.createElement('div');
                verificationAlert.className = 'alert alert-info';
                verificationAlert.innerHTML = '⚠️ Your email is not verified. <a href="#" id="resendVerification">Resend verification email</a>';
                document.querySelector('.card').insertBefore(verificationAlert, document.querySelector('.card h3'));
                
                document.getElementById('resendVerification').addEventListener('click', async (e) => {
                    e.preventDefault();
                    await resendVerification(user.email);
                });
            }
        } else if (response.status === 401) {
            alert('⚠️ Session expired. Please login again.');
            localStorage.removeItem('access_token');
            localStorage.removeItem('user');
            window.location.href = '/login';
        } else {
            alert('❌ Error loading profile data');
        }
    } catch (error) {
        console.error('Error loading profile:', error);
        alert('❌ Error loading profile data');
    }
}

// Resend verification email
async function resendVerification(email) {
    try {
        const response = await fetch('/api/resend-verification', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email: email })
        });
        
        const data = await response.json();
        if (response.ok) {
            alert('✅ ' + data.message + '\n\nPlease check your email (or terminal console).');
        } else {
            alert('❌ Error: ' + (data.detail || 'Failed to resend verification'));
        }
    } catch (error) {
        alert('❌ Failed to resend verification email: ' + error.message);
    }
}

// Update profile
document.getElementById('profileForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const updateData = {
        full_name: document.getElementById('fullName').value.trim(),
        phone: document.getElementById('phone').value.trim() || null
    };
    
    const password = document.getElementById('password').value;
    if (password) {
        if (password.length < 6) {
            alert('❌ Password must be at least 6 characters long!');
            return;
        }
        updateData.password = password;
    }
    
    if (updateData.full_name && updateData.full_name.length < 2) {
        alert('❌ Please enter a valid full name!');
        return;
    }
    
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = 'Updating...';
    
    try {
        const response = await fetch('/api/profile', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(updateData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('✅ Profile updated successfully!');
            document.getElementById('password').value = '';
            
            const storedUser = localStorage.getItem('user');
            if (storedUser) {
                const user = JSON.parse(storedUser);
                if (updateData.full_name) user.full_name = updateData.full_name;
                localStorage.setItem('user', JSON.stringify(user));
            }
            
            loadProfile();
        } else if (response.status === 401) {
            alert('⚠️ Session expired. Please login again.');
            localStorage.removeItem('access_token');
            localStorage.removeItem('user');
            window.location.href = '/login';
        } else {
            alert('❌ Error: ' + (data.detail || 'Update failed. Please try again.'));
        }
    } catch (error) {
        alert('❌ Network error: ' + error.message);
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    }
});

// Photo upload
document.getElementById('photoInput').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
        alert('❌ Please upload a valid image file (JPEG, PNG, WEBP)');
        e.target.value = '';
        return;
    }
    
    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
        alert('❌ File size must be less than 5MB');
        e.target.value = '';
        return;
    }
    
    // Show preview
    const reader = new FileReader();
    reader.onload = (event) => {
        document.getElementById('currentPhoto').src = event.target.result;
        document.getElementById('photoPreview').style.display = 'block';
    };
    reader.readAsDataURL(file);
    
    // Upload photo
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/api/upload-photo', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('✅ ' + data.message);
            document.getElementById('deletePhotoBtn').style.display = 'inline-block';
        } else {
            alert('❌ Error: ' + (data.detail || 'Upload failed'));
            loadProfile(); // Reload to show original photo
        }
    } catch (error) {
        alert('❌ Upload error: ' + error.message);
        loadProfile();
    }
    
    e.target.value = '';
});

// Delete photo
document.getElementById('deletePhotoBtn').addEventListener('click', async () => {
    if (!confirm('Are you sure you want to delete your profile photo?')) return;
    
    try {
        const response = await fetch('/api/delete-photo', {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('✅ ' + data.message);
            document.getElementById('currentPhoto').src = 'https://via.placeholder.com/150?text=No+Photo';
            document.getElementById('deletePhotoBtn').style.display = 'none';
        } else {
            alert('❌ Error: ' + (data.detail || 'Delete failed'));
        }
    } catch (error) {
        alert('❌ Error: ' + error.message);
    }
});

// Logout functionality
document.getElementById('logoutBtn').addEventListener('click', async (e) => {
    e.preventDefault();
    
    if (confirm('Are you sure you want to logout?')) {
        try {
            await fetch('/api/logout', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
        } catch (error) {
            console.error('Logout error:', error);
        }
        
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        alert('✅ Logged out successfully!');
        window.location.href = '/';
    }
});

// Load profile on page load
loadProfile();