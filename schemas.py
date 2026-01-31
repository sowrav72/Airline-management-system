from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
import re  # Added for regex validations in new features

# ========================================
# USER SCHEMAS (UPDATED)
# ========================================

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=6)
    phone: Optional[str] = None
    role: str = "passenger"
    staff_id: Optional[str] = None  # ✅ NEW
    
    @validator('staff_id')
    def validate_staff_id(cls, v, values):
        """Validate staff_id based on role"""
        role = values.get('role', 'passenger')
        
        # Staff and admin MUST have staff_id
        if role in ['staff', 'admin'] and not v:
            raise ValueError('Staff ID is required for staff and admin roles')
        
        # Passenger must NOT have staff_id
        if role == 'passenger' and v:
            raise ValueError('Passengers cannot have a staff ID')
        
        # Validate staff_id format
        if v:
            if len(v) < 5 or len(v) > 50:
                raise ValueError('Staff ID must be between 5 and 50 characters')
            if not v.replace('-', '').replace('_', '').isalnum():
                raise ValueError('Staff ID can only contain letters, numbers, hyphens, and underscores')
        
        return v
    
    @validator('role')
    def validate_role(cls, v):
        """Validate role is one of the allowed values"""
        allowed_roles = ['passenger', 'staff', 'admin']
        if v.lower() not in allowed_roles:
            raise ValueError(f'Role must be one of: {", ".join(allowed_roles)}')
        return v.lower()
    
    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number format (optional international)"""
        if v and not re.match(r'^\+?[\d\s\-\$\$]{7,15}$', v):
            raise ValueError('Phone number must be a valid format (e.g., +1234567890)')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str
    staff_id: Optional[str] = None  # ✅ NEW - Required for staff/admin


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None


class PasswordReset(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6)


class EmailVerification(BaseModel):
    token: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    staff_id: Optional[str] = None  # ✅ NEW
    staff_id_active: bool = True  # ✅ NEW
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
   

# ✅ NEW: Staff ID Management Schemas
class StaffIdDeactivate(BaseModel):
    staff_id: str
    reason: Optional[str] = None


class StaffIdActivate(BaseModel):
    staff_id: str
    reason: Optional[str] = None


class StaffIdLogResponse(BaseModel):
    id: int
    staff_id: str
    action: str
    performed_by: Optional[int]
    reason: Optional[str]
    timestamp: datetime
    
    class Config:
        from_attributes = True

# -------------------END OF USER SCHEMAS-------------------#

# ========================================
# BOOKING SCHEMAS (NEW)
# ========================================

class PassengerDetails(BaseModel):  # Nested model for booking passengers
    full_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    phone: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    passport_number: Optional[str] = Field(None, max_length=20)


class BookingCreate(BaseModel):
    flight_id: int = Field(..., gt=0)
    user_id: int = Field(..., gt=0)  # Link to user
    passengers: List[PassengerDetails] = Field(..., min_items=1)  # At least one passenger
    seat_class: str = Field(..., pattern="^(economy|business|first)$")  # Restrict to valid classes
    number_of_seats: int = Field(..., gt=0, le=10)  # Reasonable limit
    extra_baggage: Optional[int] = Field(0, ge=0)  # Kg of extra baggage
    special_requests: Optional[str] = Field(None, max_length=500)


class BookingUpdate(BaseModel):
    seat_class: Optional[str] = Field(None, pattern="^(economy|business|first)$")
    number_of_seats: Optional[int] = Field(None, gt=0, le=10)
    extra_baggage: Optional[int] = Field(None, ge=0)
    special_requests: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = Field(None, pattern="^(confirmed|cancelled|pending)$")  # Booking status


class BookingResponse(BaseModel):
    id: int
    flight_id: int
    user_id: int
    passengers: List[PassengerDetails]
    seat_class: str
    number_of_seats: int
    total_price: Decimal  # Calculated field (e.g., base price + extras)
    status: str
    extra_baggage: int
    special_requests: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# ========================================
# PAYMENT SCHEMAS (NEW)
# ========================================

class PaymentCreate(BaseModel):
    booking_id: int = Field(..., gt=0)
    amount: Decimal = Field(..., gt=0)  # Must be positive
    payment_method: str = Field(..., pattern="^(credit_card|debit_card|paypal|bank_transfer)$")
    card_number: Optional[str] = Field(None, pattern=r'^\d{13,19}$')  # For cards (masked in responses)
    expiry_date: Optional[str] = Field(None, pattern=r'^(0[1-9]|1[0-2])\/\d{2}$')  # MM/YY
    cvv: Optional[str] = Field(None, pattern=r'^\d{3,4}$')  # 3-4 digits


class PaymentResponse(BaseModel):
    id: int
    booking_id: int
    amount: Decimal
    payment_method: str
    status: str  # e.g., 'pending', 'completed', 'failed'
    transaction_id: Optional[str]
    processed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# ========================================
# NOTIFICATION SCHEMAS (NEW)
# ========================================

class NotificationCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    type: str = Field(..., pattern="^(email|sms|push)$")  # Notification type
    subject: str = Field(..., max_length=100)
    message: str = Field(..., max_length=1000)
    scheduled_at: Optional[datetime] = None


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    type: str
    subject: str
    message: str
    status: str  # e.g., 'sent', 'pending', 'failed'
    sent_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# ========================================
# AIRCRAFT SCHEMAS
# ========================================

class AircraftCreate(BaseModel):
    aircraft_number: str = Field(..., max_length=50)
    model: str = Field(..., max_length=100)
    manufacturer: str = Field(..., max_length=100)
    total_seats: int = Field(..., gt=0)
    economy_seats: int = Field(..., ge=0)
    business_seats: int = Field(..., ge=0)
    first_class_seats: int = Field(..., ge=0)
    manufacturing_year: Optional[int] = None
    status: Optional[str] = "active"

class AircraftUpdate(BaseModel):
    model: Optional[str] = None
    status: Optional[str] = None
    
class AircraftResponse(BaseModel):
    id: int
    aircraft_number: str
    model: str
    manufacturer: str
    total_seats: int
    economy_seats: int
    business_seats: int
    first_class_seats: int
    manufacturing_year: Optional[int]
    status: str
    
    class Config:
        from_attributes = True

# ========================================
# AIRPORT SCHEMAS
# ========================================

class AirportCreate(BaseModel):
    code: str = Field(..., max_length=10)
    name: str = Field(..., max_length=255)
    city: str = Field(..., max_length=100)
    country: str = Field(..., max_length=100)
    timezone: Optional[str] = None

class AirportResponse(BaseModel):
    id: int
    code: str
    name: str
    city: str
    country: str
    timezone: Optional[str]
    
    class Config:
        from_attributes = True

# ========================================
# ROUTE SCHEMAS
# ========================================

class RouteCreate(BaseModel):
    origin_airport_id: int
    destination_airport_id: int
    distance_km: Optional[int] = None
    estimated_duration: Optional[int] = None
    base_price_economy: Decimal
    base_price_business: Decimal
    base_price_first: Decimal
    is_active: Optional[bool] = True

class RouteResponse(BaseModel):
    id: int
    origin_airport_id: int
    destination_airport_id: int
    distance_km: Optional[int]
    estimated_duration: Optional[int]
    base_price_economy: Decimal
    base_price_business: Decimal
    base_price_first: Decimal
    is_active: bool
    
    class Config:
        from_attributes = True

# ========================================
# FLIGHT SCHEMAS
# ========================================

class FlightCreate(BaseModel):
    flight_number: str = Field(..., max_length=20)
    route_id: int
    aircraft_id: int
    departure_datetime: datetime
    arrival_datetime: datetime
    gate: Optional[str] = None

class FlightUpdate(BaseModel):
    status: Optional[str] = None
    gate: Optional[str] = None
    departure_datetime: Optional[datetime] = None
    arrival_datetime: Optional[datetime] = None

class FlightSearch(BaseModel):
    origin: Optional[str] = None
    destination: Optional[str] = None
    departure_date: Optional[str] = None
    seat_class: Optional[str] = None

class FlightResponse(BaseModel):
    id: int
    flight_number: str
    route_id: int
    aircraft_id: int
    departure_datetime: datetime
    arrival_datetime: datetime
    status: str
    available_economy: int
    available_business: int
    available_first: int
    gate: Optional[str]
    
    class Config:
        from_attributes = True

# ========================================
# OPERATIONAL COST SCHEMAS
# ========================================

class FlightCostCreate(BaseModel):
    fuel_cost: float = 0
    crew_cost: float = 0
    airport_charges: float = 0
    catering_cost: float = 0
    maintenance_cost: float = 0
    other_costs: float = 0
    notes: Optional[str] = None


class FlightCostResponse(BaseModel):
    id: int
    flight_id: int
    fuel_cost: float
    crew_cost: float
    airport_charges: float
    catering_cost: float
    maintenance_cost: float
    other_costs: float
    total_cost: float
    notes: Optional[str]
    recorded_at: Optional[datetime]

    class Config:
        from_attributes = True

# ========================================
# FLIGHT TEMPLATE SCHEMAS
# ========================================

class FlightTemplateCreate(BaseModel):
    template_name: str = Field(..., min_length=3, max_length=100)
    flight_number_prefix: str = Field(..., min_length=2, max_length=10)
    route_id: int = Field(..., gt=0)
    aircraft_id: int = Field(..., gt=0)
    recurrence_type: str = Field(..., pattern="^(daily|weekly|monthly)$")
    days_of_week: Optional[str] = Field(None, pattern="^[1-7](,[1-7])*$")  # e.g., "1,3,5"
    departure_time: str = Field(..., pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")  # HH:MM
    duration_minutes: int = Field(..., gt=0, le=1440)
    start_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")  # YYYY-MM-DD
    end_date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    gate: Optional[str] = Field(None, max_length=10)

class FlightTemplateResponse(BaseModel):
    id: int
    template_name: str
    flight_number_prefix: str
    route_id: int
    aircraft_id: int
    recurrence_type: str
    days_of_week: Optional[str]
    departure_time: str
    duration_minutes: int
    start_date: str
    end_date: Optional[str]
    gate: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True