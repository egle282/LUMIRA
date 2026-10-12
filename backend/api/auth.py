from datetime import datetime, timedelta
import re

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import settings
from backend.database.database import AdminAsyncSessionLocal, get_db
from backend.database.models import User, Tenant
from backend.database.tenant import set_tenant_context

router = APIRouter(prefix="/auth", tags=["Authentication"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7


class Token(BaseModel):
    access_token: str
    token_type: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not re.search(r"[A-Z]", value) or not re.search(r"[0-9]", value):
            raise ValueError("Password must contain at least one uppercase letter and one number")
        return value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower().strip()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=ALGORITHM)


async def _find_user_by_email(email: str) -> User | None:
    # Cross-tenant email lookup is read-only and uses the dedicated SELECT-only role.
    if AdminAsyncSessionLocal is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin database lookup is not configured",
        )
    async with AdminAsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == email))
        return result.scalars().first()


@router.post("/register", response_model=Token)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await _find_user_by_email(user_data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_tenant = Tenant(name=f"Tenant for {user_data.email}")
    db.add(new_tenant)
    await db.flush()
    await set_tenant_context(db, str(new_tenant.id))
    new_user = User(
        tenant_id=new_tenant.id,
        email=user_data.email,
        role="user",
        hashed_password=get_password_hash(user_data.password),
    )
    db.add(new_user)
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Could not register account")
    await db.refresh(new_user)
    token = create_access_token(
        {"sub": new_user.id, "role": new_user.role, "tenant_id": new_user.tenant_id},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": token, "token_type": "bearer"}


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = await _find_user_by_email(form_data.username.lower().strip())
    if user is None or not user.hashed_password or not verify_password(
        form_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )
    token = create_access_token(
        {"sub": user.id, "role": user.role, "tenant_id": user.tenant_id},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": token, "token_type": "bearer"}
