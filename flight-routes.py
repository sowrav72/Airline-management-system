# ========================================
# Flight Management API Endpoints
# ========================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, date
from typing import List, Optional
from database import get_db
from models import User, Aircraft, Airport, Route, Flight, Seat
from schemas import (
    AircraftCreate, AircraftUpdate, AircraftResponse,
    AirportCreate, AirportResponse,
    RouteCreate, RouteResponse,
    FlightCreate, FlightUpdate, FlightResponse, FlightSearch
)

router = APIRouter(prefix="/api/flights", tags=["flights"])

# Helper function - will be imported from main.py
def get_current_user_dependency():
    from main import get_current_user
    return get_current_user

# ========================================
# AIRCRAFT ENDPOINTS
# ========================================

@router.get("/aircraft", response_model=List[AircraftResponse])
async def get_all_aircraft(db: Session = Depends(get_db)):
    """Get all aircraft in the fleet"""
    aircraft = db.query(Aircraft).all()
    return aircraft

@router.get("/aircraft/{aircraft_id}", response_model=AircraftResponse)
async def get_aircraft(aircraft_id: int, db: Session = Depends(get_db)):
    """Get specific aircraft by ID"""
    aircraft = db.query(Aircraft).filter(Aircraft.id == aircraft_id).first()
    if not aircraft:
        raise HTTPException(status_code=404, detail="Aircraft not found")
    return aircraft

@router.post("/aircraft", response_model=AircraftResponse)
async def create_aircraft(
    aircraft: AircraftCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency)
):
    """Create new aircraft (Admin/Staff only)"""
    if current_user.role not in ["admin", "staff"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Check if aircraft number exists
    existing = db.query(Aircraft).filter(Aircraft.aircraft_number == aircraft.aircraft_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Aircraft number already exists")
    
    new_aircraft = Aircraft(**aircraft.dict())
    db.add(new_aircraft)
    db.commit()
    db.refresh(new_aircraft)
    return new_aircraft

@router.put("/aircraft/{aircraft_id}", response_model=AircraftResponse)
async def update_aircraft(
    aircraft_id: int,
    aircraft: AircraftUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency)
):
    """Update aircraft (Admin/Staff only)"""
    if current_user.role not in ["admin", "staff"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db_aircraft = db.query(Aircraft).filter(Aircraft.id == aircraft_id).first()
    if not db_aircraft:
        raise HTTPException(status_code=404, detail="Aircraft not found")
    
    for key, value in aircraft.dict(exclude_unset=True).items():
        setattr(db_aircraft, key, value)
    
    db_aircraft.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_aircraft)
    return db_aircraft

# ========================================
# AIRPORT ENDPOINTS
# ========================================

@router.get("/airports", response_model=List[AirportResponse])
async def get_all_airports(db: Session = Depends(get_db)):
    """Get all airports"""
    airports = db.query(Airport).all()
    return airports

@router.get("/airports/{airport_id}", response_model=AirportResponse)
async def get_airport(airport_id: int, db: Session = Depends(get_db)):
    """Get specific airport by ID"""
    airport = db.query(Airport).filter(Airport.id == airport_id).first()
    if not airport:
        raise HTTPException(status_code=404, detail="Airport not found")
    return airport

@router.post("/airports", response_model=AirportResponse)
async def create_airport(
    airport: AirportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency)
):
    """Create new airport (Admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Check if code exists
    existing = db.query(Airport).filter(Airport.code == airport.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Airport code already exists")
    
    new_airport = Airport(**airport.dict())
    db.add(new_airport)
    db.commit()
    db.refresh(new_airport)
    return new_airport

# ========================================
# ROUTE ENDPOINTS
# ========================================

@router.get("/routes", response_model=List[RouteResponse])
async def get_all_routes(active_only: bool = True, db: Session = Depends(get_db)):
    """Get all routes"""
    query = db.query(Route)
    if active_only:
        query = query.filter(Route.is_active == True)
    routes = query.all()
    return routes

@router.post("/routes", response_model=RouteResponse)
async def create_route(
    route: RouteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency)
):
    """Create new route (Admin/Staff only)"""
    if current_user.role not in ["admin", "staff"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Validate airports exist
    origin = db.query(Airport).filter(Airport.id == route.origin_airport_id).first()
    destination = db.query(Airport).filter(Airport.id == route.destination_airport_id).first()
    
    if not origin or not destination:
        raise HTTPException(status_code=404, detail="Airport not found")
    
    if route.origin_airport_id == route.destination_airport_id:
        raise HTTPException(status_code=400, detail="Origin and destination must be different")
    
    new_route = Route(**route.dict())
    db.add(new_route)
    db.commit()
    db.refresh(new_route)
    return new_route

# ========================================
# FLIGHT ENDPOINTS
# ========================================

@router.get("/search")
async def search_flights(
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    departure_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Search for flights with filters"""
    
    query = db.query(Flight).join(Route).join(
        Airport, Route.origin_airport_id == Airport.id
    ).join(
        Airport, Route.destination_airport_id == Airport.id, aliased=True
    ).join(Aircraft)
    
    # Filter by status - only show scheduled flights
    query = query.filter(Flight.status.in_(['scheduled', 'boarding']))
    
    # Filter by origin
    if origin:
        query = query.filter(Airport.code == origin.upper())
    
    # Filter by destination
    if destination:
        query = query.filter(Airport.code == destination.upper())
    
    # Filter by departure date
    if departure_date:
        try:
            search_date = datetime.strptime(departure_date, "%Y-%m-%d").date()
            query = query.filter(
                and_(
                    Flight.departure_datetime >= datetime.combine(search_date, datetime.min.time()),
                    Flight.departure_datetime < datetime.combine(search_date, datetime.max.time())
                )
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    flights = query.all()
    
    # Format response with full details
    result = []
    for flight in flights:
        result.append({
            "id": flight.id,
            "flight_number": flight.flight_number,
            "origin": {
                "code": flight.route.origin_airport.code,
                "name": flight.route.origin_airport.name,
                "city": flight.route.origin_airport.city
            },
            "destination": {
                "code": flight.route.destination_airport.code,
                "name": flight.route.destination_airport.name,
                "city": flight.route.destination_airport.city
            },
            "departure_datetime": flight.departure_datetime.isoformat(),
            "arrival_datetime": flight.arrival_datetime.isoformat(),
            "duration": flight.route.estimated_duration,
            "aircraft": {
                "model": flight.aircraft.model,
                "number": flight.aircraft.aircraft_number
            },
            "available_seats": {
                "economy": flight.available_economy,
                "business": flight.available_business,
                "first": flight.available_first
            },
            "prices": {
                "economy": float(flight.route.base_price_economy),
                "business": float(flight.route.base_price_business),
                "first": float(flight.route.base_price_first)
            },
            "status": flight.status,
            "gate": flight.gate
        })
    
    return result

@router.get("/all", response_model=List[FlightResponse])
async def get_all_flights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency)
):
    """Get all flights (Admin/Staff only)"""
    if current_user.role not in ["admin", "staff"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    flights = db.query(Flight).all()
    return flights

@router.get("/{flight_id}")
async def get_flight_details(flight_id: int, db: Session = Depends(get_db)):
    """Get detailed flight information"""
    flight = db.query(Flight).filter(Flight.id == flight_id).first()
    
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    return {
        "id": flight.id,
        "flight_number": flight.flight_number,
        "origin": {
            "code": flight.route.origin_airport.code,
            "name": flight.route.origin_airport.name,
            "city": flight.route.origin_airport.city,
            "country": flight.route.origin_airport.country
        },
        "destination": {
            "code": flight.route.destination_airport.code,
            "name": flight.route.destination_airport.name,
            "city": flight.route.destination_airport.city,
            "country": flight.route.destination_airport.country
        },
        "departure_datetime": flight.departure_datetime.isoformat(),
        "arrival_datetime": flight.arrival_datetime.isoformat(),
        "duration": flight.route.estimated_duration,
        "distance": flight.route.distance_km,
        "aircraft": {
            "model": flight.aircraft.model,
            "manufacturer": flight.aircraft.manufacturer,
            "number": flight.aircraft.aircraft_number,
            "total_seats": flight.aircraft.total_seats
        },
        "available_seats": {
            "economy": flight.available_economy,
            "business": flight.available_business,
            "first": flight.available_first
        },
        "prices": {
            "economy": float(flight.route.base_price_economy),
            "business": float(flight.route.base_price_business),
            "first": float(flight.route.base_price_first)
        },
        "status": flight.status,
        "gate": flight.gate
    }

@router.post("/create", response_model=FlightResponse)
async def create_flight(
    flight: FlightCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency)
):
    """Create new flight (Admin/Staff only)"""
    if current_user.role not in ["admin", "staff"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Check if flight number exists
    existing = db.query(Flight).filter(Flight.flight_number == flight.flight_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Flight number already exists")
    
    # Validate route and aircraft exist
    route = db.query(Route).filter(Route.id == flight.route_id).first()
    aircraft = db.query(Aircraft).filter(Aircraft.id == flight.aircraft_id).first()
    
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    if not aircraft:
        raise HTTPException(status_code=404, detail="Aircraft not found")
    
    # Create flight with available seats from aircraft
    new_flight = Flight(
        flight_number=flight.flight_number,
        route_id=flight.route_id,
        aircraft_id=flight.aircraft_id,
        departure_datetime=flight.departure_datetime,
        arrival_datetime=flight.arrival_datetime,
        gate=flight.gate,
        available_economy=aircraft.economy_seats,
        available_business=aircraft.business_seats,
        available_first=aircraft.first_class_seats,
        status='scheduled'
    )
    
    db.add(new_flight)
    db.commit()
    db.refresh(new_flight)
    
    # Generate seats for this flight
    generate_seats_for_flight(db, new_flight, aircraft, route)
    
    return new_flight

@router.put("/{flight_id}", response_model=FlightResponse)
async def update_flight(
    flight_id: int,
    flight: FlightUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency)
):
    """Update flight (Admin/Staff only)"""
    if current_user.role not in ["admin", "staff"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db_flight = db.query(Flight).filter(Flight.id == flight_id).first()
    if not db_flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    for key, value in flight.dict(exclude_unset=True).items():
        setattr(db_flight, key, value)
    
    db_flight.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_flight)
    return db_flight

@router.delete("/{flight_id}")
async def delete_flight(
    flight_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency)
):
    """Delete/Cancel flight (Admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    flight = db.query(Flight).filter(Flight.id == flight_id).first()
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    # Instead of deleting, mark as cancelled
    flight.status = 'cancelled'
    flight.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Flight cancelled successfully"}

# ========================================
# HELPER FUNCTION - Generate Seats
# ========================================

def generate_seats_for_flight(db: Session, flight: Flight, aircraft: Aircraft, route: Route):
    """Generate seat layout for a flight"""
    seats = []
    
    # Economy seats (rows 1-27, A-F)
    row = 1
    for i in range(aircraft.economy_seats):
        seat_letter = ['A', 'B', 'C', 'D', 'E', 'F'][i % 6]
        seats.append(Seat(
            flight_id=flight.id,
            seat_number=f"{row}{seat_letter}",
            seat_class='economy',
            is_window=(seat_letter in ['A', 'F']),
            is_aisle=(seat_letter in ['C', 'D']),
            price=route.base_price_economy,
            is_available=True
        ))
        if (i + 1) % 6 == 0:
            row += 1
    
    # Business seats (rows 28-35, A-D)
    row = 28
    for i in range(aircraft.business_seats):
        seat_letter = ['A', 'B', 'C', 'D'][i % 4]
        seats.append(Seat(
            flight_id=flight.id,
            seat_number=f"{row}{seat_letter}",
            seat_class='business',
            is_window=(seat_letter in ['A', 'D']),
            is_aisle=(seat_letter in ['B', 'C']),
            price=route.base_price_business,
            is_available=True
        ))
        if (i + 1) % 4 == 0:
            row += 1
    
    # First class seats (rows 36-38, A-B)
    row = 36
    for i in range(aircraft.first_class_seats):
        seat_letter = ['A', 'B'][i % 2]
        seats.append(Seat(
            flight_id=flight.id,
            seat_number=f"{row}{seat_letter}",
            seat_class='first',
            is_window=True,
            is_aisle=False,
            price=route.base_price_first,
            is_available=True
        ))
        if (i + 1) % 2 == 0:
            row += 1
    
    db.bulk_save_objects(seats)
    db.commit()