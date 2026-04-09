from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, CheckConstraint, Time, Date, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from database import Base
from datetime import datetime
import enum

class UserRole(enum.Enum):
    PASSENGER = "passenger"
    STAFF = "staff"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    role = Column(String(20), default="passenger", nullable=False)
    profile_photo = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Email verification
    verification_token = Column(String(255), nullable=True)
    verification_token_expires = Column(DateTime, nullable=True)
    
    # Password reset
    password_reset_token = Column(String(255), nullable=True)
    password_reset_token_expires = Column(DateTime, nullable=True)
    
    # ✅ NEW: Staff ID fields
    staff_id = Column(String(50), unique=True, nullable=True, index=True)
    staff_id_active = Column(Boolean, default=True)
    deactivated_at = Column(DateTime, nullable=True)
    deactivated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    activity_logs = relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan")
    deactivated_users = relationship("User", remote_side=[id], foreign_keys=[deactivated_by])
    permissions = relationship("UserPermission", back_populates="user", foreign_keys="UserPermission.user_id")
    bookings = relationship("Booking", back_populates="user", cascade="all, delete-orphan")

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    action = Column(String(100), nullable=False)
    details = Column(String(500), nullable=True)
    ip_address = Column(String(50), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="activity_logs")

class StaffIdLog(Base): 
    __tablename__ = "staff_id_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(String(50), nullable=False, index=True)
    action = Column(String(50), nullable=False)  # 'activated', 'deactivated', 'created'
    performed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reason = Column(String(500), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationship
    performed_by_user = relationship("User", foreign_keys=[performed_by])

# Aircraft Model
class Aircraft(Base):
    __tablename__ = "aircraft"
    
    id = Column(Integer, primary_key=True, index=True)
    aircraft_number = Column(String(50), unique=True, nullable=False, index=True)
    model = Column(String(100), nullable=False)
    manufacturer = Column(String(100), nullable=False)
    total_seats = Column(Integer, nullable=False)
    economy_seats = Column(Integer, nullable=False)
    business_seats = Column(Integer, nullable=False)
    first_class_seats = Column(Integer, nullable=False)
    manufacturing_year = Column(Integer)
    status = Column(String(20), default='active')

    # Seat layout configuration
    economy_start_row = Column(Integer, default=1)
    business_start_row = Column(Integer)
    first_start_row = Column(Integer)
    seats_per_row_economy = Column(Integer, default=6)
    seats_per_row_business = Column(Integer, default=4)
    seats_per_row_first = Column(Integer, default=2)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)
    
    # Relationships
    flights = relationship("Flight", back_populates="aircraft")

# Airport Model
class Airport(Base):
    __tablename__ = "airports"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False)
    timezone = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    origin_routes = relationship("Route", foreign_keys="Route.origin_airport_id", back_populates="origin_airport")
    destination_routes = relationship("Route", foreign_keys="Route.destination_airport_id", back_populates="destination_airport")

# Route Model
class Route(Base):
    __tablename__ = "routes"
    
    id = Column(Integer, primary_key=True, index=True)
    origin_airport_id = Column(Integer, ForeignKey("airports.id"), nullable=False)
    destination_airport_id = Column(Integer, ForeignKey("airports.id"), nullable=False)
    distance_km = Column(Integer)
    estimated_duration = Column(Integer)  # minutes
    base_price_economy = Column(Numeric(10, 2))
    base_price_business = Column(Numeric(10, 2))
    base_price_first = Column(Numeric(10, 2))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    origin_airport = relationship("Airport", foreign_keys=[origin_airport_id], back_populates="origin_routes")
    destination_airport = relationship("Airport", foreign_keys=[destination_airport_id], back_populates="destination_routes")
    flights = relationship("Flight", back_populates="route")

# Flight Model
class Flight(Base):
    __tablename__ = "flights"
    
    id = Column(Integer, primary_key=True, index=True)
    flight_number = Column(String(20), unique=True, nullable=False, index=True)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False)
    aircraft_id = Column(Integer, ForeignKey("aircraft.id"), nullable=False)
    departure_datetime = Column(DateTime, nullable=False, index=True)
    arrival_datetime = Column(DateTime, nullable=False)
    status = Column(String(20), default='scheduled', index=True)
    available_economy = Column(Integer)
    available_business = Column(Integer)
    available_first = Column(Integer)
    gate = Column(String(10))

    # NEW: Delay and cancellation tracking
    delay_reason = Column(Text)
    cancellation_reason = Column(Text)
    airline_name = Column(String(100), default='SkyLink Airlines')
    actual_departure_datetime = Column(DateTime)
    actual_arrival_datetime = Column(DateTime)
    
    # NEW: Recurring flight support
    is_recurring = Column(Boolean, default=False, index=True)
    parent_template_id = Column(Integer, ForeignKey("flight_templates.id"), nullable=True)
    
    # NEW: Operational costs (quick access)
    fuel_cost = Column(Numeric(10, 2), default=0)
    crew_cost = Column(Numeric(10, 2), default=0)
    operational_cost = Column(Numeric(10, 2), default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)
    
    # Relationships
    route = relationship("Route", back_populates="flights")
    aircraft = relationship("Aircraft", back_populates="flights")
    seats = relationship("Seat", back_populates="flight", cascade="all, delete-orphan")
    status_logs = relationship("FlightStatusLog", back_populates="flight", cascade="all, delete-orphan")
    operational_costs = relationship("FlightOperationalCost", back_populates="flight", uselist=False)
    template = relationship("FlightTemplate", back_populates="generated_flights")
    bookings = relationship("Booking", back_populates="flight", cascade="all, delete-orphan")

# Seat Model
class Seat(Base):
    __tablename__ = "seats"
    
    id = Column(Integer, primary_key=True, index=True)
    flight_id = Column(Integer, ForeignKey("flights.id", ondelete="CASCADE"), nullable=False)
    seat_number = Column(String(10), nullable=False)
    seat_class = Column(String(20), nullable=False)
    is_available = Column(Boolean, default=True, index=True)
    is_window = Column(Boolean, default=False)
    is_aisle = Column(Boolean, default=False)
    price = Column(Numeric(10, 2))
    
    # Relationships
    flight = relationship("Flight", back_populates="seats")
    booking = relationship("Booking", back_populates="seat", uselist=False)

# ========================================
# NEW: Flight Status Logs
# ========================================

class FlightStatusLog(Base):
    __tablename__ = "flight_status_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    flight_id = Column(Integer, ForeignKey("flights.id", ondelete="CASCADE"), nullable=False, index=True)
    old_status = Column(String(20))
    new_status = Column(String(20), nullable=False)
    reason = Column(Text)
    changed_by = Column(Integer, ForeignKey("users.id"))
    changed_at = Column(DateTime, default=datetime.utcnow, index=True)
    notes = Column(Text)
    
    # Relationships
    flight = relationship("Flight", back_populates="status_logs")
    user = relationship("User", foreign_keys=[changed_by])

# ========================================
# NEW: Flight Templates (Recurring Flights)
# ========================================

class FlightTemplate(Base):
    __tablename__ = "flight_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    template_name = Column(String(100), nullable=False)
    flight_number_prefix = Column(String(10), nullable=False)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False)
    aircraft_id = Column(Integer, ForeignKey("aircraft.id"), nullable=False)
    
    # Recurrence pattern
    recurrence_type = Column(String(20), nullable=False)  # 'daily', 'weekly', 'monthly'
    days_of_week = Column(String(50))  # '1,3,5' for Mon,Wed,Fri or NULL for daily
    
    # Timing
    departure_time = Column(Time, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    
    # Date range
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    
    # Other details
    gate = Column(String(10))
    airline_name = Column(String(100), default='SkyLink Airlines')
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    route = relationship("Route")
    aircraft = relationship("Aircraft")
    creator = relationship("User", foreign_keys=[created_by])
    generated_flights = relationship("Flight", back_populates="template")

# ========================================
# NEW: Flight Operational Costs
# ========================================

class FlightOperationalCost(Base):
    __tablename__ = "flight_operational_costs"
    
    id = Column(Integer, primary_key=True, index=True)
    flight_id = Column(Integer, ForeignKey("flights.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Cost breakdown
    fuel_cost = Column(Numeric(10, 2), default=0)
    crew_cost = Column(Numeric(10, 2), default=0)
    airport_charges = Column(Numeric(10, 2), default=0)
    catering_cost = Column(Numeric(10, 2), default=0)
    maintenance_cost = Column(Numeric(10, 2), default=0)
    other_costs = Column(Numeric(10, 2), default=0)
    
    # Note: total_cost is computed column in database
    
    # Metadata
    recorded_at = Column(DateTime, default=datetime.utcnow)
    recorded_by = Column(Integer, ForeignKey("users.id"))
    notes = Column(Text)
    
    # Relationships
    flight = relationship("Flight", back_populates="operational_costs")
    recorder = relationship("User", foreign_keys=[recorded_by])

class FlightAuditLog(Base):
    __tablename__ = "flight_audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    flight_id = Column(Integer, ForeignKey("flights.id", ondelete="SET NULL"), index=True)
    action = Column(String(50), nullable=False)  # 'created', 'updated', 'cancelled', 'delayed'
    performed_by = Column(Integer, ForeignKey("users.id"))
    old_values = Column(JSONB)
    new_values = Column(JSONB)
    reason = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    flight = relationship("Flight")
    user = relationship("User", foreign_keys=[performed_by])
 
# ========================================
# NEW: User Permissions
# ========================================

class UserPermission(Base):
    __tablename__ = "user_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    permission_name = Column(String(50), nullable=False)
    granted_by = Column(Integer, ForeignKey("users.id"))
    granted_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="permissions")
    granter = relationship("User", foreign_keys=[granted_by])

# ========================================
# NEW: Booking Model (for passenger reservations)
# ========================================

class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    flight_id = Column(Integer, ForeignKey("flights.id", ondelete="CASCADE"), nullable=False, index=True)
    seat_id = Column(Integer, ForeignKey("seats.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    booking_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default='confirmed')  # 'confirmed', 'cancelled', 'pending'
    total_price = Column(Numeric(10, 2), nullable=False)
    special_requests = Column(Text)
    
    # Relationships
    user = relationship("User", back_populates="bookings")
    flight = relationship("Flight", back_populates="bookings")
    seat = relationship("Seat", back_populates="booking")
    
# ========================================
# PERMISSION CONSTANTS
# ========================================

class Permission(enum.Enum):
    """Define all available permissions"""
    VIEW_FLIGHTS = "view_flights"
    MANAGE_FLIGHTS = "manage_flights"
    VIEW_AIRCRAFT = "view_aircraft"
    MANAGE_AIRCRAFT = "manage_aircraft"
    MANAGE_ROUTES = "manage_routes"
    MANAGE_USERS = "manage_users"
    VIEW_COSTS = "view_costs"
    MANAGE_COSTS = "manage_costs"
    CREATE_TEMPLATES = "create_templates"
    VIEW_BOOKINGS = "view_bookings"
    MANAGE_BOOKINGS = "manage_bookings"

    
# ========================================
# HELPER FUNCTION TO CHECK PERMISSIONS
# ========================================

def user_has_permission(user, permission_name: str, db) -> bool:
    """Check if user has a specific permission"""
    # Admins have all permissions
    if user.role == 'admin':
        return True
    
    # Check in permissions table
    perm = db.query(UserPermission).filter(
        UserPermission.user_id == user.id,
        UserPermission.permission_name == permission_name
    ).first()
    
    return perm is not None