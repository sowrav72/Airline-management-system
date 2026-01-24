// ========================================
// SKYLINK AIRLINES - DASHBOARD SCRIPT
// ========================================

// Check if user is logged in
const token = localStorage.getItem('access_token');
if (!token) {
    alert('⚠️ Please login first!');
    window.location.href = '/login';
}

// Load user profile
async function loadProfile() {
    try {
        const response = await fetch('/api/profile', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const user = await response.json();
            
            // Display user name
            document.getElementById('userName').textContent = user.full_name;
            
            // Format dates
            const createdDate = user.created_at ? new Date(user.created_at).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            }) : 'N/A';
            
            const lastLoginDate = user.last_login ? new Date(user.last_login).toLocaleString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            }) : 'First time login';
            
            // Display user information
            const userInfo = `
                <div style="padding: 1rem 0;">
                    ${user.profile_photo ? `
                        <div style="text-align: center; margin-bottom: 1.5rem;">
                            <img src="${user.profile_photo}" alt="Profile Photo" style="width: 100px; height: 100px; border-radius: 50%; object-fit: cover; border: 3px solid #667eea; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">
                        </div>
                    ` : ''}
                    <p style="margin-bottom: 0.8rem;">
                        <strong style="color: #667eea;">📧 Email:</strong> 
                        <span style="color: #666;">${user.email}</span>
                    </p>
                    <p style="margin-bottom: 0.8rem;">
                        <strong style="color: #667eea;">👤 Role:</strong> 
                        <span style="color: #666; text-transform: capitalize;">${user.role}</span>
                    </p>
                    <p style="margin-bottom: 0.8rem;">
                        <strong style="color: #667eea;">📱 Phone:</strong> 
                        <span style="color: #666;">${user.phone || 'Not provided'}</span>
                    </p>
                    <p style="margin-bottom: 0.8rem;">
                        <strong style="color: #667eea;">✅ Verified:</strong> 
                        <span style="color: ${user.is_verified ? '#28a745' : '#dc3545'};">${user.is_verified ? '✓ Yes' : '✗ No'}</span>
                    </p>
                    <p style="margin-bottom: 0.8rem;">
                        <strong style="color: #667eea;">📅 Member Since:</strong> 
                        <span style="color: #666;">${createdDate}</span>
                    </p>
                    <p style="margin-bottom: 0;">
                        <strong style="color: #667eea;">🕒 Last Login:</strong> 
                        <span style="color: #666;">${lastLoginDate}</span>
                    </p>
                </div>
            `;
            document.getElementById('userInfo').innerHTML = userInfo;
        } else if (response.status === 401) {
            // Token expired or invalid
            alert('⚠️ Session expired. Please login again.');
            localStorage.removeItem('access_token');
            localStorage.removeItem('user');
            window.location.href = '/login';
        } else {
            document.getElementById('userInfo').innerHTML = '<p style="color: #dc3545;">Error loading profile</p>';
        }
    } catch (error) {
        console.error('Error loading profile:', error);
        document.getElementById('userInfo').innerHTML = '<p style="color: #dc3545;">Error loading profile</p>';
    }
}

// Load activity logs
async function loadActivityLogs() {
    try {
        const response = await fetch('/api/activity-logs', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const logs = await response.json();
            
            if (logs.length === 0) {
                document.getElementById('activityLogs').innerHTML = '<p style="text-align: center; color: #999;">No recent activity</p>';
                return;
            }
            
            const logsHtml = logs.map(log => {
                const timestamp = new Date(log.timestamp).toLocaleString('en-US', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                });
                
                return `
                    <div class="activity-item">
                        <strong>${log.action}</strong>
                        <p>${log.details || 'No details available'}</p>
                        <small>🕒 ${timestamp} | 📍 ${log.ip_address || 'Unknown'}</small>
                    </div>
                `;
            }).join('');
            
            document.getElementById('activityLogs').innerHTML = logsHtml;
        } else {
            document.getElementById('activityLogs').innerHTML = '<p style="color: #dc3545;">Error loading activity logs</p>';
        }
    } catch (error) {
        console.error('Error loading activity logs:', error);
        document.getElementById('activityLogs').innerHTML = '<p style="color: #dc3545;">Error loading activity logs</p>';
    }
}

// Logout functionality
document.getElementById('logoutBtn').addEventListener('click', async (e) => {
    e.preventDefault();
    
    if (confirm('Are you sure you want to logout?')) {
        try {
            // Call logout API
            await fetch('/api/logout', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
        } catch (error) {
            console.error('Logout error:', error);
        }
        
        // Clear local storage
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        
        // Redirect to home
        alert('✅ Logged out successfully!');
        window.location.href = '/';
    }
});

// Load data on page load
loadProfile();
loadActivityLogs();