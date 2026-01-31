from models import StaffIdLog
from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
import secrets
import os
import shutil
from pathlib import Path

# Import models and database
from database import get_db, engine, Base
from models import User, UserRole, ActivityLog
from schemas import (
    UserCreate, UserLogin, UserResponse, UserUpdate,
    PasswordReset, PasswordResetConfirm, EmailVerification
)
from email_service import send_verification_email, send_password_reset_email

# Import flight routes
from flight_routes import router as flight_router

# Create tables automatically
Base.metadata.create_all(bind=engine)

# Initialize FastAPI
app = FastAPI(
    title="SkyLink Airlines - Complete Management System",
    description="User & Flight Management Module",
    version="2.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include flight management routes
app.include_router(flight_router)

# Create uploads directory if not exists
UPLOAD_DIR = Path("static/uploads/profiles")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Security configuration
SECRET_KEY = "skylink-airlines-secret-key-2024-postgresql-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def generate_token():
    """Generate a secure random token"""
    return secrets.token_urlsafe(32)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

def log_activity(db: Session, user_id: int, action: str, details: str = None):
    activity = ActivityLog(
        user_id=user_id,
        action=action,
        details=details,
        ip_address="127.0.0.1",
        timestamp=datetime.utcnow()
    )
    db.add(activity)
    db.commit()

# ========================================
# HTML ROUTES (Serve HTML Pages)
# ========================================

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/register", response_class=HTMLResponse)
async def register_page():
    """Serve the registration HTML page"""
    with open("templates/register.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/login", response_class=HTMLResponse)
async def login_page():
    """Serve the login HTML page"""
    with open("templates/login.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page():
    with open("templates/dashboard.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/profile", response_class=HTMLResponse)
async def profile_page():
    with open("templates/profile.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/verify-email", response_class=HTMLResponse)
async def verify_email_page():
    with open("templates/verify-email.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page():
    with open("templates/forgot-password.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page():
    with open("templates/reset-password.html", "r", encoding="utf-8") as f:
        return f.read()

# Flight Management HTML Routes
@app.get("/flights", response_class=HTMLResponse)
async def flights_page():
    with open("templates/flights.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/admin/flights", response_class=HTMLResponse)
async def admin_flights_page():
    with open("templates/admin-flights.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/admin/aircraft", response_class=HTMLResponse)
async def admin_aircraft_page():
    with open("templates/admin-aircraft.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/admin/costs", response_class=HTMLResponse)
async def admin_costs_page():
    with open("templates/admin-costs.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/admin/templates", response_class=HTMLResponse)
async def admin_templates_page():
    with open("templates/admin-templates.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/admin/flight-history", response_class=HTMLResponse)
async def admin_flight_history_page():
    with open("templates/admin-flight-history.html", "r", encoding="utf-8") as f:
        return f.read()

# ========================================
# API ENDPOINTS (Return JSON)
# ========================================

# AUTHENTICATION ENDPOINTS

@app.post("/api/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user with staff_id support"""
    # Check if user exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if staff_id already exists (for staff/admin)
    if user.staff_id:
        existing_staff_id = db.query(User).filter(User.staff_id == user.staff_id).first()
        if existing_staff_id:
            raise HTTPException(status_code=400, detail="Staff ID already in use")
    
    # Validate role and staff_id combination
    if user.role in ['staff', 'admin'] and not user.staff_id:
        raise HTTPException(status_code=400, detail="Staff ID is required for staff and admin roles")
    
    if user.role == 'passenger' and user.staff_id:
        raise HTTPException(status_code=400, detail="Passengers cannot have a staff ID")
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    user_role = user.role.lower() if user.role else "passenger"
    
    # Generate verification token
    verification_token = generate_token()
    verification_expires = datetime.utcnow() + timedelta(hours=24)
    
    new_user = User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        phone=user.phone,
        role=user_role,
        staff_id=user.staff_id,
        staff_id_active=True if user.staff_id else None,
        is_active=True,
        is_verified=False,
        verification_token=verification_token,
        verification_token_expires=verification_expires,
        created_at=datetime.utcnow()
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Log staff ID creation
    if user.staff_id:
        staff_log = StaffIdLog(
            staff_id=user.staff_id,
            action='created',
            performed_by=None,
            reason=f"New {user_role} account registered",
            timestamp=datetime.utcnow()
        )
        db.add(staff_log)
        db.commit()
    
    # Send verification email
    await send_verification_email(user.email, verification_token, user.full_name)
    
    # Log activity
    log_activity(db, new_user.id, "USER_REGISTERED", f"New {user_role} registered: {user.email}")
    
    return {
        "message": "Registration successful! Please check your email to verify your account.",
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "full_name": new_user.full_name,
            "role": new_user.role,
            "staff_id": new_user.staff_id
        }
    }

@app.post("/api/login")
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login with staff_id validation for staff/admin"""
    # Find user by email
    user = db.query(User).filter(User.email == user_credentials.email).first()
    
    # Check if user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check password
    if not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if user is staff/admin and requires staff_id
    if user.role in ['staff', 'admin']:
        # Staff/Admin must provide staff_id
        if not user_credentials.staff_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Staff ID is required for staff and admin login"
            )
        
        # Verify staff_id matches
        if user.staff_id != user_credentials.staff_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Staff ID"
            )
        
        # Check if staff_id is active
        if not user.staff_id_active:
            # Log deactivated login attempt
            log_activity(
                db, 
                user.id, 
                "LOGIN_FAILED_DEACTIVATED", 
                f"Attempted login with deactivated Staff ID: {user.staff_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your staff account has been deactivated. Please contact your administrator."
            )
    
    # Passenger should NOT provide staff_id
    if user.role == 'passenger' and user_credentials.staff_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Passenger login does not require Staff ID"
        )
    
    # Check if account is active
    if not user.is_active:
        raise HTTPException(status_code=400, detail="User account is inactive")
    
    # Allow login even if not verified, but show warning
    if not user.is_verified:
        print(f"⚠️ User {user.email} logged in without email verification")
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    # Log activity
    login_details = f"User logged in: {user.email}"
    if user.role in ['staff', 'admin']:
        login_details += f" (Staff ID: {user.staff_id})"
    log_activity(db, user.id, "USER_LOGIN", login_details)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "staff_id": user.staff_id if user.role in ['staff', 'admin'] else None,
            "is_verified": user.is_verified
        }
    }

@app.get("/api/verify-email/{token}")
async def verify_email(token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.verification_token == token).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid verification token")
    
    if user.verification_token_expires < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Verification token has expired")
    
    if user.is_verified:
        return {"message": "Email already verified"}
    
    # Verify user
    user.is_verified = True
    user.verification_token = None
    user.verification_token_expires = None
    db.commit()
    
    # Log activity
    log_activity(db, user.id, "EMAIL_VERIFIED", "User verified their email")
    
    return {"message": "Email verified successfully! You can now login."}

@app.post("/api/resend-verification")
async def resend_verification(request: dict, db: Session = Depends(get_db)):
    email = request.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_verified:
        return {"message": "Email already verified"}
    
    # Generate new token
    verification_token = generate_token()
    verification_expires = datetime.utcnow() + timedelta(hours=24)
    
    user.verification_token = verification_token
    user.verification_token_expires = verification_expires
    db.commit()
    
    # Send email
    await send_verification_email(user.email, verification_token, user.full_name)
    
    return {"message": "Verification email sent successfully"}

@app.post("/api/forgot-password")
async def forgot_password(request: PasswordReset, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        # Don't reveal if email exists or not for security
        return {"message": "If the email exists, a password reset link has been sent"}
    
    # Generate reset token
    reset_token = generate_token()
    reset_expires = datetime.utcnow() + timedelta(hours=1)
    
    user.password_reset_token = reset_token
    user.password_reset_token_expires = reset_expires
    db.commit()
    
    # Send password reset email
    await send_password_reset_email(user.email, reset_token, user.full_name)
    
    # Log activity
    log_activity(db, user.id, "PASSWORD_RESET_REQUESTED", "User requested password reset")
    
    return {"message": "If the email exists, a password reset link has been sent"}

@app.post("/api/reset-password")
async def reset_password(request: PasswordResetConfirm, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.password_reset_token == request.token).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid reset token")
    
    if user.password_reset_token_expires < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Reset token has expired")
    
    # Update password
    user.hashed_password = get_password_hash(request.new_password)
    user.password_reset_token = None
    user.password_reset_token_expires = None
    db.commit()
    
    # Log activity
    log_activity(db, user.id, "PASSWORD_RESET", "User reset their password")
    
    return {"message": "Password reset successfully! You can now login with your new password."}

@app.post("/api/logout")
async def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Log activity
    log_activity(db, current_user.id, "USER_LOGOUT", "User logged out")
    
    return {"message": "Logged out successfully"}

# PROFILE MANAGEMENT ENDPOINTS

@app.get("/api/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "phone": current_user.phone,
        "staff_id": current_user.staff_id if current_user.role in ['staff', 'admin'] else None,
        "is_verified": current_user.is_verified,
        "profile_photo": current_user.profile_photo,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "last_login": current_user.last_login.isoformat() if current_user.last_login else None
    }

@app.put("/api/profile")
async def update_profile(user_update: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user_update.full_name:
        current_user.full_name = user_update.full_name
    if user_update.phone:
        current_user.phone = user_update.phone
    if user_update.password:
        current_user.hashed_password = get_password_hash(user_update.password)
    
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    # Log activity
    log_activity(db, current_user.id, "PROFILE_UPDATED", "User updated profile")
    
    return {"message": "Profile updated successfully"}

@app.post("/api/upload-photo")
async def upload_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only image files are allowed (JPEG, PNG, WEBP)")
    
    # Validate file size (max 5MB)
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be less than 5MB")
    
    # Delete old photo if exists
    if current_user.profile_photo:
        old_photo_path = Path(current_user.profile_photo.replace("/static/", "static/"))
        if old_photo_path.exists():
            old_photo_path.unlink()
    
    # Generate unique filename
    file_extension = file.filename.split(".")[-1]
    new_filename = f"user_{current_user.id}_{secrets.token_hex(8)}.{file_extension}"
    file_path = UPLOAD_DIR / new_filename
    
    # Save file
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update user profile
    photo_url = f"/static/uploads/profiles/{new_filename}"
    current_user.profile_photo = photo_url
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    # Log activity
    log_activity(db, current_user.id, "PROFILE_PHOTO_UPDATED", "User uploaded profile photo")
    
    return {
        "message": "Profile photo uploaded successfully",
        "photo_url": photo_url
    }

@app.delete("/api/delete-photo")
async def delete_photo(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.profile_photo:
        raise HTTPException(status_code=400, detail="No profile photo to delete")
    
    # Delete file
    photo_path = Path(current_user.profile_photo.replace("/static/", "static/"))
    if photo_path.exists():
        photo_path.unlink()
    
    # Update user
    current_user.profile_photo = None
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    # Log activity
    log_activity(db, current_user.id, "PROFILE_PHOTO_DELETED", "User deleted profile photo")
    
    return {"message": "Profile photo deleted successfully"}

@app.get("/api/activity-logs")
async def get_activity_logs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logs = db.query(ActivityLog).filter(ActivityLog.user_id == current_user.id).order_by(ActivityLog.timestamp.desc()).limit(20).all()
    
    return [
        {
            "id": log.id,
            "action": log.action,
            "details": log.details,
            "timestamp": log.timestamp.isoformat() if log.timestamp else None,
            "ip_address": log.ip_address
        }
        for log in logs
    ]

# STAFF ID MANAGEMENT ENDPOINTS (ADMIN ONLY)

@app.post("/api/admin/deactivate-staff")
async def deactivate_staff_id(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deactivate a staff member (Admin only)"""
    
    # Only admins can deactivate staff
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Only admins can deactivate staff accounts")
    
    staff_id = request.get('staff_id')
    reason = request.get('reason', 'No reason provided')
    
    if not staff_id:
        raise HTTPException(status_code=400, detail="Staff ID is required")
    
    # Find user with this staff_id
    staff_user = db.query(User).filter(User.staff_id == staff_id).first()
    
    if not staff_user:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    # Cannot deactivate yourself
    if staff_user.id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot deactivate your own account")
    
    # Deactivate the staff ID
    staff_user.staff_id_active = False
    staff_user.deactivated_at = datetime.utcnow()
    staff_user.deactivated_by = current_user.id
    staff_user.is_active = False  # Also deactivate the account
    
    db.commit()
    
    # Log the deactivation
    staff_log = StaffIdLog(
        staff_id=staff_id,
        action='deactivated',
        performed_by=current_user.id,
        reason=reason,
        timestamp=datetime.utcnow()
    )
    db.add(staff_log)
    db.commit()
    
    # Log activity
    log_activity(
        db,
        current_user.id,
        "STAFF_DEACTIVATED",
        f"Deactivated staff member {staff_user.full_name} (Staff ID: {staff_id}). Reason: {reason}"
    )
    
    return {
        "message": f"Staff member {staff_user.full_name} has been deactivated",
        "staff_id": staff_id,
        "deactivated_at": staff_user.deactivated_at.isoformat()
    }

@app.post("/api/admin/activate-staff")
async def activate_staff_id(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reactivate a staff member (Admin only)"""
    
    # Only admins can activate staff
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Only admins can activate staff accounts")
    
    staff_id = request.get('staff_id')
    reason = request.get('reason', 'Reactivated by admin')
    
    if not staff_id:
        raise HTTPException(status_code=400, detail="Staff ID is required")
    
    # Find user with this staff_id
    staff_user = db.query(User).filter(User.staff_id == staff_id).first()
    
    if not staff_user:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    # Activate the staff ID
    staff_user.staff_id_active = True
    staff_user.deactivated_at = None
    staff_user.deactivated_by = None
    staff_user.is_active = True
    
    db.commit()
    
    # Log the activation
    staff_log = StaffIdLog(
        staff_id=staff_id,
        action='activated',
        performed_by=current_user.id,
        reason=reason,
        timestamp=datetime.utcnow()
    )
    db.add(staff_log)
    db.commit()
    
    # Log activity
    log_activity(
        db,
        current_user.id,
        "STAFF_ACTIVATED",
        f"Activated staff member {staff_user.full_name} (Staff ID: {staff_id}). Reason: {reason}"
    )
    
    return {
        "message": f"Staff member {staff_user.full_name} has been reactivated",
        "staff_id": staff_id
    }

@app.get("/api/admin/staff-list")
async def get_staff_list(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of all staff/admin accounts (Admin only)"""
    
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Only admins can view staff list")
    
    staff_members = db.query(User).filter(
        User.role.in_(['staff', 'admin'])
    ).all()
    
    return [
        {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "staff_id": user.staff_id,
            "staff_id_active": user.staff_id_active,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "deactivated_at": user.deactivated_at.isoformat() if user.deactivated_at else None
        }
        for user in staff_members
    ]

@app.get("/api/admin/staff-logs/{staff_id}")
async def get_staff_logs(
    staff_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get activity logs for a specific staff ID (Admin only)"""
    
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Only admins can view staff logs")
    
    logs = db.query(StaffIdLog).filter(
        StaffIdLog.staff_id == staff_id
    ).order_by(StaffIdLog.timestamp.desc()).all()
    
    return [
        {
            "id": log.id,
            "action": log.action,
            "performed_by": log.performed_by,
            "reason": log.reason,
            "timestamp": log.timestamp.isoformat()
        }
        for log in logs
    ]

# ADMIN ENDPOINTS

@app.get("/api/admin/users")
async def get_all_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    users = db.query(User).all()
    return [
        {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "staff_id": user.staff_id if user.role in ['staff', 'admin'] else None,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
        for user in users
    ]

# HEALTH CHECK ENDPOINT

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy", 
        "message": "SkyLink Airlines API is running",
        "database": "PostgreSQL",
        "version": "2.1.0",
        "modules": ["User Management", "Flight Management", "Staff ID Management"]
    }

if __name__ == "__main__":
    import uvicorn
    print("✈️  " + "="*50)
    print("🚀 SkyLink Airlines Management System v2.1")
    print("="*54)
    print("📍 Server: http://127.0.0.1:8000")
    print("📚 API Docs: http://127.0.0.1:8000/docs")
    print("🗄️  Database: PostgreSQL (Port 1234)")
    print("✨ Module 2.1: User Management ✓")
    print("✨ Module 2.2: Flight Management ✓")
    print("✨ Module 2.3: Staff ID Management ✓")
    print("🔧 Press CTRL+C to stop")
    print("="*54)
    uvicorn.run(app, host="127.0.0.1", port=8000)