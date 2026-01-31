// ========================================
// ADMIN AIRCRAFT MANAGEMENT - FIXED VERSION
// ========================================

const API_URL = 'http://127.0.0.1:8000/api';

// FIX: Use consistent token storage key
let token = localStorage.getItem('access_token');

// Check authentication
if (!token) {
    alert('⚠️ Please login first!');
    window.location.href = '/login';
}

let editingAircraftId = null;

// Auto-calculate total seats
['economy_seats', 'business_seats', 'first_class_seats'].forEach(id => {
    const element = document.getElementById(id);
    if (element) {
        element.addEventListener('input', calculateTotalSeats);
    }
});

function calculateTotalSeats() {
    const economy = parseInt(document.getElementById('economy_seats').value) || 0;
    const business = parseInt(document.getElementById('business_seats').value) || 0;
    const first = parseInt(document.getElementById('first_class_seats').value) || 0;
    const total = economy + business + first;
    
    const totalElement = document.getElementById('totalSeatsCalc');
    if (totalElement) {
        totalElement.textContent = total;
    }
}

// Load aircraft
async function loadAircraft() {
    try {
        const response = await fetch(`${API_URL}/flights/aircraft`);
        
        if (!response.ok) {
            throw new Error('Failed to load aircraft');
        }
        
        const aircraft = await response.json();
        console.log('Loaded aircraft:', aircraft);
        
        displayAircraft(aircraft);
        updateStats(aircraft);
    } catch (error) {
        console.error('Error loading aircraft:', error);
        document.getElementById('aircraftGrid').innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">❌</div>
                <p>Error loading aircraft: ${error.message}</p>
            </div>
        `;
    }
}

// Display aircraft
function displayAircraft(aircraft) {
    const grid = document.getElementById('aircraftGrid');
    
    if (!grid) {
        console.error('Aircraft grid element not found');
        return;
    }
    
    if (aircraft.length === 0) {
        grid.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">✈️</div>
                <p>No aircraft found. Click "Add New Aircraft" to add one.</p>
            </div>
        `;
        return;
    }
    
    grid.innerHTML = aircraft.map(a => `
        <div class="aircraft-card">
            <div class="aircraft-header">
                <div class="aircraft-number">${a.aircraft_number}</div>
                <div class="aircraft-status status-${a.status}">${a.status}</div>
            </div>
            <div class="aircraft-info">
                <div class="info-row">
                    <span class="info-label">Manufacturer</span>
                    <span class="info-value">${a.manufacturer}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Model</span>
                    <span class="info-value">${a.model}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Year</span>
                    <span class="info-value">${a.manufacturing_year || 'N/A'}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Total Capacity</span>
                    <span class="info-value">${a.total_seats} seats</span>
                </div>
            </div>
            <div class="seat-breakdown">
                <div class="seat-type">
                    <div class="seat-type-label">Economy</div>
                    <div class="seat-type-value">${a.economy_seats}</div>
                </div>
                <div class="seat-type">
                    <div class="seat-type-label">Business</div>
                    <div class="seat-type-value">${a.business_seats}</div>
                </div>
                <div class="seat-type">
                    <div class="seat-type-label">First</div>
                    <div class="seat-type-value">${a.first_class_seats}</div>
                </div>
            </div>
            <div class="aircraft-actions">
                <button class="btn btn-warning btn-small" style="flex: 1;" onclick="editAircraft(${a.id})">Edit</button>
                <button class="btn btn-secondary btn-small" onclick="changeStatus(${a.id}, '${a.status}')">Change Status</button>
            </div>
        </div>
    `).join('');
}

// Update stats
function updateStats(aircraft) {
    const total = aircraft.length;
    const active = aircraft.filter(a => a.status === 'active').length;
    const totalSeats = aircraft.reduce((sum, a) => sum + a.total_seats, 0);
    
    const totalElement = document.getElementById('totalAircraft');
    const activeElement = document.getElementById('activeAircraft');
    const seatsElement = document.getElementById('totalSeats');
    
    if (totalElement) totalElement.textContent = total;
    if (activeElement) activeElement.textContent = active;
    if (seatsElement) seatsElement.textContent = totalSeats.toLocaleString();
}

// Open create modal
function openCreateModal() {
    editingAircraftId = null;
    document.getElementById('modalTitle').textContent = 'Add New Aircraft';
    document.getElementById('aircraftForm').reset();
    document.getElementById('aircraft_number').disabled = false;
    calculateTotalSeats();
    document.getElementById('aircraftModal').style.display = 'block';
}

// Edit aircraft
async function editAircraft(id) {
    try {
        const response = await fetch(`${API_URL}/flights/aircraft/${id}`);
        
        if (!response.ok) {
            throw new Error('Failed to load aircraft');
        }
        
        const aircraft = await response.json();
        
        editingAircraftId = id;
        document.getElementById('modalTitle').textContent = 'Edit Aircraft';
        document.getElementById('aircraft_number').value = aircraft.aircraft_number;
        document.getElementById('aircraft_number').disabled = true;
        document.getElementById('manufacturer').value = aircraft.manufacturer;
        document.getElementById('model').value = aircraft.model;
        document.getElementById('manufacturing_year').value = aircraft.manufacturing_year || '';
        document.getElementById('economy_seats').value = aircraft.economy_seats;
        document.getElementById('business_seats').value = aircraft.business_seats;
        document.getElementById('first_class_seats').value = aircraft.first_class_seats;
        document.getElementById('status').value = aircraft.status;
        
        calculateTotalSeats();
        document.getElementById('aircraftModal').style.display = 'block';
    } catch (error) {
        console.error('Error loading aircraft:', error);
        alert('Error loading aircraft details: ' + error.message);
    }
}

// Change status
async function changeStatus(id, currentStatus) {
    const statuses = ['active', 'maintenance', 'retired'];
    const newStatus = prompt(
        `Current status: ${currentStatus}\nEnter new status (${statuses.join('/')}):`, 
        currentStatus
    );
    
    if (!newStatus || !statuses.includes(newStatus.toLowerCase())) {
        alert('Invalid status');
        return;
    }
    
    try {
        showLoading();
        
        const response = await fetch(`${API_URL}/flights/aircraft/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ status: newStatus.toLowerCase() })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to update status');
        }
        
        alert('Status updated successfully!');
        loadAircraft();
    } catch (error) {
        console.error('Error updating status:', error);
        alert('Error updating status: ' + error.message);
    } finally {
        hideLoading();
    }
}

// Save aircraft
async function saveAircraft() {
    const form = document.getElementById('aircraftForm');
    
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const economy = parseInt(document.getElementById('economy_seats').value);
    const business = parseInt(document.getElementById('business_seats').value);
    const first = parseInt(document.getElementById('first_class_seats').value);
    
    const aircraftData = {
        aircraft_number: document.getElementById('aircraft_number').value,
        manufacturer: document.getElementById('manufacturer').value,
        model: document.getElementById('model').value,
        manufacturing_year: parseInt(document.getElementById('manufacturing_year').value) || null,
        economy_seats: economy,
        business_seats: business,
        first_class_seats: first,
        total_seats: economy + business + first,
        status: document.getElementById('status').value
    };
    
    try {
        showLoading();
        
        const url = editingAircraftId 
            ? `${API_URL}/flights/aircraft/${editingAircraftId}`
            : `${API_URL}/flights/aircraft`;
        
        const method = editingAircraftId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(aircraftData)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to save aircraft');
        }
        
        alert(editingAircraftId ? 'Aircraft updated successfully!' : 'Aircraft created successfully!');
        closeModal();
        loadAircraft();
    } catch (error) {
        console.error('Error saving aircraft:', error);
        alert(`Error: ${error.message}`);
    } finally {
        hideLoading();
    }
}

// Close modal
function closeModal() {
    document.getElementById('aircraftModal').style.display = 'none';
}

// Show/hide loading
function showLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = 'flex';
    }
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

// Logout
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    window.location.href = '/login';
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('aircraftModal');
    if (event.target == modal) {
        closeModal();
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Page loaded, loading aircraft...');
    loadAircraft();
});