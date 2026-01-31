# ========================================
# FILE: flight_routes.py - COMPLETE VERSION
# Module 2.2 - 100% Complete with All Features
# ========================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, aliased
from sqlalchemy import and_, func
from datetime import datetime, timedelta, date as date_type
from typing import List, Optional

from database import get_db
from models import (
    User, Aircraft, Airport, Route, Flight, Seat,
    FlightStatusLog, FlightOperationalCost, FlightAuditLog,
    FlightTemplate, UserPermission
)
from schemas import (
    AircraftCreate, AircraftUpdate, AircraftResponse,
    AirportCreate, AirportResponse,
    RouteCreate, RouteResponse,
    FlightCreate, FlightUpdate, FlightResponse
)

from models import FlightOperationalCost, FlightTemplate
from schemas import FlightCostCreate,FlightCostResponse, FlightTemplateCreate, FlightTemplateResponse
from datetime import date, time, timedelta

router = APIRouter(prefix="/api/flights", tags=["flights"])

# ========================================
# PERMISSION HELPER FUNCTIONS
# ========================================

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
security = HTTPBearer()



def user_has_permission(user: User, permission_name: str, db: Session) -> bool:
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


def require_permission(permission_name: str):
    def permission_checker(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
    ):
        from main import get_current_user  # lazy import (SAFE)
        current_user = get_current_user(credentials, db)

        if not user_has_permission(current_user, permission_name, db):
            raise HTTPException(
                status_code=403,
                detail=f"You don't have permission: {permission_name}"
            )
        return current_user

    return permission_checker



# ========================================
# AUDIT LOG HELPER
# ========================================

def log_flight_audit(
    db: Session,
    flight_id: int,
    action: str,
    performed_by: int,
    old_values: dict = None,
    new_values: dict = None,
    reason: str = None
):
    """Log flight operations for audit trail"""
    audit = FlightAuditLog(
        flight_id=flight_id,
        action=action,
        performed_by=performed_by,
        old_values=old_values,
        new_values=new_values,
        reason=reason,
        timestamp=datetime.utcnow()
    )
    db.add(audit)
    db.commit()


# ========================================
# AIRCRAFT ENDPOINTS (WITH PERMISSIONS)
# ========================================

@router.get("/aircraft", response_model=List[AircraftResponse])
async def get_all_aircraft(db: Session = Depends(get_db)):
    """Get all aircraft - PUBLIC ACCESS"""
    aircraft = db.query(Aircraft).all()
    return aircraft


@router.get("/aircraft/{aircraft_id}", response_model=AircraftResponse)
async def get_aircraft(aircraft_id: int, db: Session = Depends(get_db)):
    """Get specific aircraft - PUBLIC ACCESS"""
    aircraft = db.query(Aircraft).filter(Aircraft.id == aircraft_id).first()
    if not aircraft:
        raise HTTPException(status_code=404, detail="Aircraft not found")
    return aircraft


@router.post("/aircraft", response_model=AircraftResponse)
async def create_aircraft(
    aircraft: AircraftCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_aircraft"))
):
    """Create new aircraft - ADMIN/STAFF ONLY"""
    
    # Check if aircraft number exists
    existing = db.query(Aircraft).filter(
        Aircraft.aircraft_number == aircraft.aircraft_number
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Aircraft number already exists")
    
    # Calculate seat layout configuration
    economy_rows = (aircraft.economy_seats + 5) // 6
    business_start = economy_rows + 1
    business_rows = (aircraft.business_seats + 3) // 4
    first_start = business_start + business_rows + 1
    
    new_aircraft = Aircraft(
        **aircraft.dict(),
        economy_start_row=1,
        business_start_row=business_start if aircraft.business_seats > 0 else None,
        first_start_row=first_start if aircraft.first_class_seats > 0 else None,
        seats_per_row_economy=6,
        seats_per_row_business=4,
        seats_per_row_first=2
    )
    
    db.add(new_aircraft)
    db.commit()
    db.refresh(new_aircraft)
    
    return new_aircraft


@router.put("/aircraft/{aircraft_id}", response_model=AircraftResponse)
async def update_aircraft(
    aircraft_id: int,
    aircraft: AircraftUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_aircraft"))
):
    """Update aircraft - ADMIN/STAFF ONLY"""
    
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
# AIRPORT ENDPOINTS (WITH PERMISSIONS)
# ========================================

@router.get("/airports", response_model=List[AirportResponse])
async def get_all_airports(db: Session = Depends(get_db)):
    """Get all airports - PUBLIC ACCESS"""
    airports = db.query(Airport).all()
    return airports


@router.get("/airports/{airport_id}", response_model=AirportResponse)
async def get_airport(airport_id: int, db: Session = Depends(get_db)):
    """Get specific airport - PUBLIC ACCESS"""
    airport = db.query(Airport).filter(Airport.id == airport_id).first()
    if not airport:
        raise HTTPException(status_code=404, detail="Airport not found")
    return airport


@router.post("/airports", response_model=AirportResponse)
async def create_airport(
    airport: AirportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_routes"))
):
    """Create new airport - ADMIN ONLY"""
    
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
# ROUTE ENDPOINTS (WITH PERMISSIONS)
# ========================================

@router.get("/routes", response_model=List[RouteResponse])
async def get_all_routes(
    active_only: bool = True, 
    db: Session = Depends(get_db)
):
    """Get all routes - PUBLIC ACCESS"""
    query = db.query(Route)
    if active_only:
        query = query.filter(Route.is_active == True)
    routes = query.all()
    return routes


@router.post("/routes", response_model=RouteResponse)
async def create_route(
    route: RouteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_routes"))
):
    """Create new route - ADMIN/STAFF ONLY"""
    
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
# FLIGHT SEARCH (PUBLIC)
# ========================================

@router.get("/search")
async def search_flights(
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    departure_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Search for flights - PUBLIC ACCESS - OPTIMIZED VERSION"""
    
    # Define aliases correctly for origin and destination airports
    origin_airport = aliased(Airport, name='origin')
    dest_airport = aliased(Airport, name='dest')
    
    # Build query with proper joins to avoid N+1 problem
    query = db.query(
        Flight,
        Route,
        Aircraft,
        origin_airport,
        dest_airport
    ).join(
        Route, Flight.route_id == Route.id
    ).join(
        Aircraft, Flight.aircraft_id == Aircraft.id
    ).join(
        origin_airport, Route.origin_airport_id == origin_airport.id
    ).join(
        dest_airport, Route.destination_airport_id == dest_airport.id
    )
    
    # Filter by status - only show scheduled flights
    query = query.filter(Flight.status.in_(['scheduled', 'boarding']))
    
    # Filter by date if provided
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
    
    # Execute query once
    results = query.all()
    
    # Filter by origin/destination in memory (after single query)
    filtered_results = []
    for flight, route, aircraft, origin_airport, dest_airport in results:
        if origin and origin_airport.code.upper() != origin.upper():
            continue
        if destination and dest_airport.code.upper() != destination.upper():
            continue
        
        filtered_results.append({
            "id": flight.id,
            "flight_number": flight.flight_number,
            "airline_name": flight.airline_name or "SkyLink Airlines",
            "origin": {
                "code": origin_airport.code,
                "name": origin_airport.name,
                "city": origin_airport.city
            },
            "destination": {
                "code": dest_airport.code,
                "name": dest_airport.name,
                "city": dest_airport.city
            },
            "departure_datetime": flight.departure_datetime.isoformat(),
            "arrival_datetime": flight.arrival_datetime.isoformat(),
            "duration": route.estimated_duration,
            "aircraft": {
                "model": aircraft.model,
                "number": aircraft.aircraft_number
            },
            "available_seats": {
                "economy": flight.available_economy,
                "business": flight.available_business,
                "first": flight.available_first
            },
            "prices": {
                "economy": float(route.base_price_economy),
                "business": float(route.base_price_business),
                "first": float(route.base_price_first)
            },
            "status": flight.status,
            "gate": flight.gate
        })
    
    return filtered_results


# ========================================
# FLIGHT MANAGEMENT (WITH PERMISSIONS)
# ========================================

@router.get("/all", response_model=List[FlightResponse])
async def get_all_flights(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_flights"))
):
    """Get all flights - ADMIN/STAFF ONLY"""
    flights = db.query(Flight).all()
    return flights


@router.get("/{flight_id}")
async def get_flight_details(
    flight_id: int, 
    db: Session = Depends(get_db)
):
    """Get detailed flight information - PUBLIC ACCESS"""
    flight = db.query(Flight).filter(Flight.id == flight_id).first()
    
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    return {
        "id": flight.id,
        "flight_number": flight.flight_number,
        "airline_name": flight.airline_name or "SkyLink Airlines",
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
        "actual_departure": flight.actual_departure_datetime.isoformat() if flight.actual_departure_datetime else None,
        "actual_arrival": flight.actual_arrival_datetime.isoformat() if flight.actual_arrival_datetime else None,
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
        "delay_reason": flight.delay_reason,
        "cancellation_reason": flight.cancellation_reason,
        "gate": flight.gate
    }


@router.post("/create", response_model=FlightResponse)
async def create_flight(
    flight: FlightCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_flights"))
):
    """Create new flight - ADMIN/STAFF ONLY - WITH TRANSACTION SAFETY"""
    
    # Check if flight number exists
    existing = db.query(Flight).filter(
        Flight.flight_number == flight.flight_number
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Flight number already exists")
    
    # Validate route and aircraft exist
    route = db.query(Route).filter(Route.id == flight.route_id).first()
    aircraft = db.query(Aircraft).filter(Aircraft.id == flight.aircraft_id).first()
    
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    if not aircraft:
        raise HTTPException(status_code=404, detail="Aircraft not found")
    
    if aircraft.status != 'active':
        raise HTTPException(status_code=400, detail="Aircraft is not active")
    
    try:
        # Start transaction
        new_flight = Flight(
            flight_number=flight.flight_number,
            route_id=flight.route_id,
            aircraft_id=flight.aircraft_id,
            departure_datetime=flight.departure_datetime,
            arrival_datetime=flight.arrival_datetime,
            gate=flight.gate,
            airline_name="SkyLink Airlines",
            available_economy=aircraft.economy_seats,
            available_business=aircraft.business_seats,
            available_first=aircraft.first_class_seats,
            status='scheduled'
        )
        
        db.add(new_flight)
        db.flush()  # Get the ID without committing
        
        # Generate seats for this flight
        generate_seats_for_flight(db, new_flight, aircraft, route)
        
        # Log creation
        log_flight_audit(
            db=db,
            flight_id=new_flight.id,
            action='created',
            performed_by=current_user.id,
            new_values={"flight_number": flight.flight_number, "status": "scheduled"}
        )
        
        # Commit transaction
        db.commit()
        db.refresh(new_flight)
        
        return new_flight
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create flight: {str(e)}")


@router.put("/{flight_id}", response_model=FlightResponse)
async def update_flight(
    flight_id: int,
    flight: FlightUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_flights"))
):
    """Update flight - ADMIN/STAFF ONLY - WITH STATUS LOGGING"""
    
    db_flight = db.query(Flight).filter(Flight.id == flight_id).first()
    if not db_flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    old_values = {}
    new_values = {}
    
    # Track status changes
    if flight.status and flight.status != db_flight.status:
        old_values['status'] = db_flight.status
        new_values['status'] = flight.status
        
        # Log status change
        status_log = FlightStatusLog(
            flight_id=flight_id,
            old_status=db_flight.status,
            new_status=flight.status,
            reason=getattr(flight, 'reason', None),
            changed_by=current_user.id,
            changed_at=datetime.utcnow()
        )
        db.add(status_log)
        
        # If marking as delayed, require delay_reason
        if flight.status == 'delayed' and not getattr(flight, 'delay_reason', None):
            raise HTTPException(
                status_code=400, 
                detail="Delay reason is required when marking flight as delayed"
            )
        
        # If marking as cancelled, require cancellation_reason
        if flight.status == 'cancelled' and not getattr(flight, 'cancellation_reason', None):
            raise HTTPException(
                status_code=400,
                detail="Cancellation reason is required when cancelling flight"
            )
    
    # Update flight
    for key, value in flight.dict(exclude_unset=True).items():
        if value is not None:
            old_values[key] = getattr(db_flight, key)
            new_values[key] = value
            setattr(db_flight, key, value)
    
    db_flight.updated_at = datetime.utcnow()
    
    # Log audit
    log_flight_audit(
        db=db,
        flight_id=flight_id,
        action='updated',
        performed_by=current_user.id,
        old_values=old_values,
        new_values=new_values
    )
    
    db.commit()
    db.refresh(db_flight)
    
    return db_flight


@router.delete("/{flight_id}")
async def delete_flight(
    flight_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_flights"))
):
    """Cancel flight - ADMIN/STAFF ONLY"""
    
    flight = db.query(Flight).filter(Flight.id == flight_id).first()
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    # Don't allow deleting departed flights
    if flight.status == 'departed':
        raise HTTPException(
            status_code=400, 
            detail="Cannot cancel a flight that has already departed"
        )
    
    # Mark as cancelled instead of deleting
    old_status = flight.status
    flight.status = 'cancelled'
    flight.cancellation_reason = "Cancelled by admin"
    flight.updated_at = datetime.utcnow()
    
    # Log status change
    status_log = FlightStatusLog(
        flight_id=flight_id,
        old_status=old_status,
        new_status='cancelled',
        reason="Cancelled by admin",
        changed_by=current_user.id,
        changed_at=datetime.utcnow()
    )
    db.add(status_log)
    
    # Log audit
    log_flight_audit(
        db=db,
        flight_id=flight_id,
        action='cancelled',
        performed_by=current_user.id,
        reason="Cancelled by admin"
    )
    
    db.commit()
    
    return {"message": "Flight cancelled successfully"}


# ========================================
# FLIGHT STATUS HISTORY
# ========================================

@router.get("/{flight_id}/status-history")
async def get_flight_status_history(
    flight_id: int,
    db: Session = Depends(get_db)
):
    """Get status change history for a flight - PUBLIC ACCESS"""
    
    flight = db.query(Flight).filter(Flight.id == flight_id).first()
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    logs = db.query(FlightStatusLog).filter(
        FlightStatusLog.flight_id == flight_id
    ).order_by(FlightStatusLog.changed_at.desc()).all()
    
    return [
        {
            "old_status": log.old_status,
            "new_status": log.new_status,
            "reason": log.reason,
            "changed_at": log.changed_at.isoformat(),
            "changed_by_user_id": log.changed_by
        }
        for log in logs
    ]


# ========================================
# HELPER FUNCTION - DYNAMIC SEAT GENERATION
# ========================================

def generate_seats_for_flight(db: Session, flight: Flight, aircraft: Aircraft, route: Route):
    """Generate seat layout using aircraft configuration - FIXED VERSION"""
    seats = []
    
    # Economy seats - Use aircraft configuration
    if aircraft.economy_seats > 0:
        row = aircraft.economy_start_row
        seats_per_row = aircraft.seats_per_row_economy
        seat_letters = ['A', 'B', 'C', 'D', 'E', 'F'][:seats_per_row]
        
        for i in range(aircraft.economy_seats):
            seat_letter = seat_letters[i % seats_per_row]
            is_window = (seat_letter == seat_letters[0] or seat_letter == seat_letters[-1])
            is_aisle = seat_letter in [seat_letters[seats_per_row//2 - 1], seat_letters[seats_per_row//2]] if seats_per_row >= 4 else False
            
            seats.append(Seat(
                flight_id=flight.id,
                seat_number=f"{row}{seat_letter}",
                seat_class='economy',
                is_window=is_window,
                is_aisle=is_aisle,
                price=route.base_price_economy,
                is_available=True
            ))
            
            if (i + 1) % seats_per_row == 0:
                row += 1
    
    # Business seats - Use aircraft configuration
    if aircraft.business_seats > 0 and aircraft.business_start_row:
        row = aircraft.business_start_row
        seats_per_row = aircraft.seats_per_row_business
        seat_letters = ['A', 'B', 'C', 'D'][:seats_per_row]
        
        for i in range(aircraft.business_seats):
            seat_letter = seat_letters[i % seats_per_row]
            is_window = (seat_letter == seat_letters[0] or seat_letter == seat_letters[-1])
            is_aisle = seat_letter in [seat_letters[1], seat_letters[2]] if seats_per_row >= 4 else False
            
            seats.append(Seat(
                flight_id=flight.id,
                seat_number=f"{row}{seat_letter}",
                seat_class='business',
                is_window=is_window,
                is_aisle=is_aisle,
                price=route.base_price_business,
                is_available=True
            ))
            
            if (i + 1) % seats_per_row == 0:
                row += 1
    
    # First class seats - Use aircraft configuration
    if aircraft.first_class_seats > 0 and aircraft.first_start_row:
        row = aircraft.first_start_row
        seats_per_row = aircraft.seats_per_row_first
        seat_letters = ['A', 'B'][:seats_per_row]
        
        for i in range(aircraft.first_class_seats):
            seat_letter = seat_letters[i % seats_per_row]
            
            seats.append(Seat(
                flight_id=flight.id,
                seat_number=f"{row}{seat_letter}",
                seat_class='first',
                is_window=True,
                is_aisle=False,
                price=route.base_price_first,
                is_available=True
            ))
            
            if (i + 1) % seats_per_row == 0:
                row += 1
    
    # Bulk insert all seats
    db.bulk_save_objects(seats)
    db.flush()  # Flush instead of commit (part of parent transaction)

# ========================================
# OPERATIONAL COST ENDPOINTS (FIXED)
# ========================================

@router.get("/costs/{flight_id}", response_model=FlightCostResponse)
async def get_flight_costs(
    flight_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_flights"))
):
    """Get operational costs for a flight"""
    costs = db.query(FlightOperationalCost).filter(
        FlightOperationalCost.flight_id == flight_id
    ).first()
    
    if not costs:
        # Return empty cost structure
        return FlightCostResponse(
            id=0,
            flight_id=flight_id,
            fuel_cost=0,
            crew_cost=0,
            airport_charges=0,
            catering_cost=0,
            maintenance_cost=0,
            other_costs=0,
            total_cost=0,
            notes=None,
            recorded_at=None
        )
    
    total = sum([
        float(costs.fuel_cost or 0),
        float(costs.crew_cost or 0),
        float(costs.airport_charges or 0),
        float(costs.catering_cost or 0),
        float(costs.maintenance_cost or 0),
        float(costs.other_costs or 0)
    ])
    
    return FlightCostResponse(
        id=costs.id,
        flight_id=costs.flight_id,
        fuel_cost=float(costs.fuel_cost or 0),
        crew_cost=float(costs.crew_cost or 0),
        airport_charges=float(costs.airport_charges or 0),
        catering_cost=float(costs.catering_cost or 0),
        maintenance_cost=float(costs.maintenance_cost or 0),
        other_costs=float(costs.other_costs or 0),
        total_cost=total,
        notes=costs.notes,
        recorded_at=costs.recorded_at
    )

@router.post("/costs/{flight_id}")
async def create_update_flight_costs(
    flight_id: int,
    cost_data: FlightCostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_flights"))
):
    """Create or update operational costs for a flight"""
    # Check if flight exists
    flight = db.query(Flight).filter(Flight.id == flight_id).first()
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    # Check if costs already exist
    costs = db.query(FlightOperationalCost).filter(
        FlightOperationalCost.flight_id == flight_id
    ).first()
    
    if costs:
        # Update existing
        costs.fuel_cost = cost_data.fuel_cost
        costs.crew_cost = cost_data.crew_cost
        costs.airport_charges = cost_data.airport_charges
        costs.catering_cost = cost_data.catering_cost
        costs.maintenance_cost = cost_data.maintenance_cost
        costs.other_costs = cost_data.other_costs
        costs.notes = cost_data.notes
        costs.recorded_by = current_user.id
        costs.recorded_at = datetime.utcnow()
    else:
        # Create new
        costs = FlightOperationalCost(
            flight_id=flight_id,
            fuel_cost=cost_data.fuel_cost,
            crew_cost=cost_data.crew_cost,
            airport_charges=cost_data.airport_charges,
            catering_cost=cost_data.catering_cost,
            maintenance_cost=cost_data.maintenance_cost,
            other_costs=cost_data.other_costs,
            notes=cost_data.notes,
            recorded_by=current_user.id
        )
        db.add(costs)
    
    db.commit()
    db.refresh(costs)
    
    return {"message": "Costs saved successfully", "cost_id": costs.id}

# ========================================
# FLIGHT TEMPLATE ENDPOINTS (FIXED)
# ========================================

@router.get("/templates", response_model=List[FlightTemplateResponse])
async def get_flight_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_flights"))
):
    """Get all flight templates"""
    templates = db.query(FlightTemplate).all()
    
    # Convert to response format
    return [
        FlightTemplateResponse(
            id=t.id,
            template_name=t.template_name,
            flight_number_prefix=t.flight_number_prefix,
            route_id=t.route_id,
            aircraft_id=t.aircraft_id,
            recurrence_type=t.recurrence_type,
            days_of_week=t.days_of_week,
            departure_time=t.departure_time.strftime('%H:%M'),
            duration_minutes=t.duration_minutes,
            start_date=t.start_date.isoformat(),
            end_date=t.end_date.isoformat() if t.end_date else None,
            gate=t.gate,
            is_active=t.is_active,
            created_at=t.created_at
        )
        for t in templates
    ]

@router.post("/templates")
async def create_flight_template(
    template_data: FlightTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_flights"))
):
    """Create a new flight template for recurring flights"""
    # Parse time
    departure_time_obj = datetime.strptime(template_data.departure_time, '%H:%M').time()
    
    # Parse dates
    start_date_obj = datetime.strptime(template_data.start_date, '%Y-%m-%d').date()
    end_date_obj = datetime.strptime(template_data.end_date, '%Y-%m-%d').date() if template_data.end_date else None
    
    template = FlightTemplate(
        template_name=template_data.template_name,
        flight_number_prefix=template_data.flight_number_prefix,
        route_id=template_data.route_id,
        aircraft_id=template_data.aircraft_id,
        recurrence_type=template_data.recurrence_type,
        days_of_week=template_data.days_of_week,
        departure_time=departure_time_obj,
        duration_minutes=template_data.duration_minutes,
        start_date=start_date_obj,
        end_date=end_date_obj,
        gate=template_data.gate,
        created_by=current_user.id
    )
    
    db.add(template)
    db.commit()
    db.refresh(template)
    
    return {"message": "Template created successfully", "template_id": template.id}

@router.post("/templates/{template_id}/generate")
async def generate_flights_from_template(
    template_id: int,
    days_ahead: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_flights"))
):
    """Generate flights from a template for the next X days"""
    template = db.query(FlightTemplate).filter(FlightTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    if not template.is_active:
        raise HTTPException(status_code=400, detail="Template is inactive")
    
    # Get route for seat generation
    route = db.query(Route).filter(Route.id == template.route_id).first()
    
    flights_created = []
    current_date = date.today()
    end_date = current_date + timedelta(days=days_ahead)
    
    # Don't go beyond template end_date
    if template.end_date and end_date > template.end_date:
        end_date = template.end_date
    
    # Generate flights
    check_date = max(current_date, template.start_date)
    
    while check_date <= end_date:
        should_create = False
        
        if template.recurrence_type == 'daily':
            should_create = True
        elif template.recurrence_type == 'weekly':
            if template.days_of_week:
                day_of_week = check_date.weekday() + 1  # Monday = 1
                allowed_days = [int(d) for d in template.days_of_week.split(',')]
                should_create = day_of_week in allowed_days
        elif template.recurrence_type == 'monthly':
            if check_date.day == template.start_date.day:
                should_create = True  # Simple monthly on same day, ignoring month length issues
        
        if should_create:
            departure_datetime = datetime.combine(check_date, template.departure_time)
            arrival_datetime = departure_datetime + timedelta(minutes=template.duration_minutes)
            
            # FIXED: Include year to avoid duplicates
            flight_number = f"{template.flight_number_prefix}{check_date.strftime('%d%m%y')}"
            
            existing = db.query(Flight).filter(
                Flight.flight_number == flight_number
            ).first()
            
            if not existing:
                aircraft = db.query(Aircraft).filter(Aircraft.id == template.aircraft_id).first()
                
                new_flight = Flight(
                    flight_number=flight_number,
                    route_id=template.route_id,
                    aircraft_id=template.aircraft_id,
                    departure_datetime=departure_datetime,
                    arrival_datetime=arrival_datetime,
                    gate=template.gate,
                    status='scheduled',
                    available_economy=aircraft.economy_seats,
                    available_business=aircraft.business_seats,
                    available_first=aircraft.first_class_seats,
                    parent_template_id=template_id
                )
                
                db.add(new_flight)
                db.flush()
                
                # Generate seats
                generate_seats_for_flight(db, new_flight, aircraft, route)
                
                flights_created.append({
                    'flight_number': flight_number,
                    'date': check_date.isoformat()
                })
        
        check_date += timedelta(days=1)
    
    db.commit()
    
    return {
        "message": f"Generated {len(flights_created)} flights",
        "flights": flights_created
    }

@router.delete("/templates/{template_id}")
async def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_flights"))
):
    """Deactivate a flight template"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    template = db.query(FlightTemplate).filter(FlightTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    template.is_active = False
    db.commit()
    
    return {"message": "Template deactivated successfully"}