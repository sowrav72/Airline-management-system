from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=6)
    phone: Optional[str] = None
    role: Optional[str] = "passenger"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

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
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Add these classes to your existing schemas.py file

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

# Aircraft Schemas
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

# Airport Schemas
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

# Route Schemas
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

# Flight Schemas
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