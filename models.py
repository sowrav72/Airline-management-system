from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
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
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    activity_logs = relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan")

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

    # Add these classes to your existing models.py file

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, CheckConstraint
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

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
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)
    
    # Relationships
    route = relationship("Route", back_populates="flights")
    aircraft = relationship("Aircraft", back_populates="flights")
    seats = relationship("Seat", back_populates="flight", cascade="all, delete-orphan")

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