from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from backend.database.database import get_db
from backend.database.models import User, Tenant
from backend.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days for MVP

from pydantic import BaseModel, EmailStr, Field, field_validator
import re

class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long, contain at least one uppercase letter and one number.")

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one number")
        return v
    
    @field_validator('email')
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.lower().strip()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/register", response_model=Token)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == user_data.email)
    result = await db.execute(stmt)
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")

    new_tenant = Tenant(name=f"Tenant for {user_data.email}")
    db.add(new_tenant)
    await db.flush()

    new_user = User(
        tenant_id=new_tenant.id,
        email=user_data.email,
        role="user",
        hashed_password=get_password_hash(user_data.password)
    )
    db.add(new_user)
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")
    await db.refresh(new_user)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.id, "role": new_user.role, "tenant_id": new_user.tenant_id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == form_data.username)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id, "role": user.role, "tenant_id": user.tenant_id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
