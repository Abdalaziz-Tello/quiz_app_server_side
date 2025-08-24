from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from jose import JWTError, jwt
from datetime import datetime, timedelta, date
from typing import List, Optional
from pydantic import BaseModel
import os
import hashlib
import secrets

# Import configuration
from config import settings

# Security configuration
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# Database setup
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# JWT token security
security = HTTPBearer()

app = FastAPI(title="Quiz App API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String, unique=True, index=True)
    device_id = Column(String, unique=True, index=True)
    nickname = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text)
    option_a = Column(String)
    option_b = Column(String)
    option_c = Column(String)
    option_d = Column(String)
    correct_answer = Column(String)
    points = Column(Integer)
    time_limit = Column(Integer)  # in seconds

class OTP(Base):
    __tablename__ = "otps"
    
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String, index=True)
    otp_code = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    is_used = Column(Boolean, default=False)
    daily_attempts = Column(Integer, default=0)

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    score = Column(Integer)
    total_points = Column(Integer)
    time_taken = Column(Integer)  # in seconds
    completed_at = Column(DateTime, default=datetime.utcnow)

# Pydantic models
class UserCreate(BaseModel):
    nickname: str
    device_id: Optional[str] = None

class UserLogin(BaseModel):
    ip_address: str
    otp_code: str

class UserResponse(BaseModel):
    id: int
    ip_address: str
    device_id: Optional[str]
    nickname: str
    created_at: datetime
    last_active: datetime
    is_active: bool

class OTPRequest(BaseModel):
    ip_address: str
    device_id: Optional[str] = None

class OTPResponse(BaseModel):
    message: str
    otp_code: str
    expires_in_minutes: int

class QuestionCreate(BaseModel):
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str
    points: int
    time_limit: int

class QuestionResponse(BaseModel):
    id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    points: int
    time_limit: int

class QuizAttemptCreate(BaseModel):
    score: int
    total_points: int
    time_taken: int

class QuizAttemptResponse(BaseModel):
    id: int
    user_id: int
    score: int
    total_points: int
    time_taken: int
    completed_at: datetime

class LeaderboardEntry(BaseModel):
    username: str
    score: int
    total_points: int
    time_taken: int
    completed_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Authentication functions
def get_client_ip(request: Request) -> str:
    """Extract client IP address from request"""
    # Get IP from various headers (for proxy/load balancer scenarios)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    return request.client.host

def generate_otp() -> str:
    """Generate a 6-digit OTP"""
    return str(secrets.randbelow(1000000)).zfill(6)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        ip_address: str = payload.get("sub")
        if ip_address is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return ip_address
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# API endpoints
@app.post("/request-otp", response_model=OTPResponse)
def request_otp(otp_request: OTPRequest, request: Request, db: Session = Depends(get_db)):
    """Request OTP for IP-based authentication"""
    ip_address = otp_request.ip_address
    
    # Check if IP already has an active OTP for today
    today = date.today()
    existing_otp = db.query(OTP).filter(
        OTP.ip_address == ip_address,
        OTP.created_at >= today,
        OTP.is_used == False
    ).first()
    
    if existing_otp:
        # Check daily attempt limit (max 5 attempts per day)
        if existing_otp.daily_attempts >= 5:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Daily OTP limit reached. Try again tomorrow."
            )
        # Update existing OTP
        existing_otp.otp_code = generate_otp()
        existing_otp.expires_at = datetime.utcnow() + timedelta(minutes=10)
        existing_otp.daily_attempts += 1
        existing_otp.is_used = False
        db.commit()
        otp_code = existing_otp.otp_code
    else:
        # Create new OTP
        otp_code = generate_otp()
        new_otp = OTP(
            ip_address=ip_address,
            otp_code=otp_code,
            expires_at=datetime.utcnow() + timedelta(minutes=10),
            daily_attempts=1
        )
        db.add(new_otp)
        db.commit()
    
    return {
        "message": "OTP sent successfully",
        "otp_code": otp_code,  # In production, send this via email/SMS
        "expires_in_minutes": 10
    }

@app.post("/register", response_model=UserResponse)
def register(user: UserCreate, request: Request, db: Session = Depends(get_db)):
    """Register a new user based on IP address"""
    ip_address = get_client_ip(request)
    
    # Check if IP already registered
    db_user = db.query(User).filter(User.ip_address == ip_address).first()
    if db_user:
        raise HTTPException(status_code=400, detail="IP address already registered")
    
    # Generate device ID if not provided
    device_id = user.device_id or f"device_{secrets.token_hex(8)}"
    
    # Create new user
    db_user = User(
        ip_address=ip_address,
        device_id=device_id,
        nickname=user.nickname
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/login", response_model=Token)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login using IP address and OTP"""
    ip_address = user_credentials.ip_address
    otp_code = user_credentials.otp_code
    
    # Verify OTP
    otp_record = db.query(OTP).filter(
        OTP.ip_address == ip_address,
        OTP.otp_code == otp_code,
        OTP.expires_at > datetime.utcnow(),
        OTP.is_used == False
    ).first()
    
    if not otp_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired OTP",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Mark OTP as used
    otp_record.is_used = True
    db.commit()
    
    # Get or create user
    user = db.query(User).filter(User.ip_address == ip_address).first()
    if not user:
        # Auto-create user if not exists
        user = User(
            ip_address=ip_address,
            device_id=f"device_{secrets.token_hex(8)}",
            nickname=f"User_{ip_address.split('.')[-1]}"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Update last active
    user.last_active = datetime.utcnow()
    db.commit()
    
    # Generate token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": ip_address}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/questions", response_model=List[QuestionResponse])
def get_questions(db: Session = Depends(get_db)):
    questions = db.query(Question).all()
    return questions

@app.post("/questions", response_model=QuestionResponse)
def create_question(question: QuestionCreate, db: Session = Depends(get_db), ip_address: str = Depends(verify_token)):
    db_question = Question(**question.model_dump())
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question

@app.post("/quiz-attempt", response_model=QuizAttemptResponse)
def submit_quiz_attempt(attempt: QuizAttemptCreate, db: Session = Depends(get_db), ip_address: str = Depends(verify_token)):
    user = db.query(User).filter(User.ip_address == ip_address).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_attempt = QuizAttempt(**attempt.model_dump(), user_id=user.id)
    db.add(db_attempt)
    db.commit()
    db.refresh(db_attempt)
    return db_attempt

@app.get("/leaderboard/week", response_model=List[LeaderboardEntry])
def get_weekly_leaderboard(db: Session = Depends(get_db)):
    week_ago = datetime.utcnow() - timedelta(days=7)
    attempts = db.query(QuizAttempt).filter(QuizAttempt.completed_at >= week_ago).order_by(QuizAttempt.score.desc()).limit(10).all()
    
    leaderboard = []
    for attempt in attempts:
        user = db.query(User).filter(User.id == attempt.user_id).first()
        if user:
            leaderboard.append(LeaderboardEntry(
                username=user.nickname,
                score=attempt.score,
                total_points=attempt.total_points,
                time_taken=attempt.time_taken,
                completed_at=attempt.completed_at
            ))
    
    return leaderboard

@app.get("/leaderboard/month", response_model=List[LeaderboardEntry])
def get_monthly_leaderboard(db: Session = Depends(get_db)):
    month_ago = datetime.utcnow() - timedelta(days=30)
    attempts = db.query(QuizAttempt).filter(QuizAttempt.completed_at >= month_ago).order_by(QuizAttempt.score.desc()).limit(10).all()
    
    leaderboard = []
    for attempt in attempts:
        user = db.query(User).filter(User.id == attempt.user_id).first()
        if user:
            leaderboard.append(LeaderboardEntry(
                username=user.nickname,
                score=attempt.score,
                total_points=attempt.total_points,
                time_taken=attempt.time_taken,
                completed_at=attempt.completed_at
            ))
    
    return leaderboard

@app.get("/leaderboard/year", response_model=List[LeaderboardEntry])
def get_yearly_leaderboard(db: Session = Depends(get_db)):
    year_ago = datetime.utcnow() - timedelta(days=365)
    attempts = db.query(QuizAttempt).filter(QuizAttempt.completed_at >= year_ago).order_by(QuizAttempt.score.desc()).limit(10).all()
    
    leaderboard = []
    for attempt in attempts:
        user = db.query(User).filter(User.id == attempt.user_id).first()
        if user:
            leaderboard.append(LeaderboardEntry(
                username=user.nickname,
                score=attempt.score,
                total_points=attempt.total_points,
                time_taken=attempt.time_taken,
                completed_at=attempt.completed_at
            ))
    
    return leaderboard

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Quiz App API - IP-Based Authentication",
        "endpoints": {
            "request_otp": "POST /request-otp - Get OTP for your IP",
            "register": "POST /register - Register with nickname",
            "login": "POST /login - Login with IP and OTP",
            "questions": "GET /questions - Get all questions",
            "create_question": "POST /questions - Create question (authenticated)",
            "quiz_attempt": "POST /quiz-attempt - Submit quiz results",
            "leaderboards": "GET /leaderboard/{week|month|year}"
        }
    }

@app.get("/user/info", response_model=UserResponse)
def get_user_info(request: Request, db: Session = Depends(get_db), ip_address: str = Depends(verify_token)):
    """Get current user information"""
    user = db.query(User).filter(User.ip_address == ip_address).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Create database tables
Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
