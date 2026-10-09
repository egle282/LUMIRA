from sqlalchemy import Column, String, DateTime, Float, ForeignKey, func, Integer
from sqlalchemy.orm import relationship
import uuid
from .database import Base

def generate_uuid():
    return str(uuid.uuid4())

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String, default="user", nullable=False)  # admin, user
    email = Column(String, unique=True, nullable=True, index=True)
    hashed_password = Column(String, nullable=True)
    telegram_id = Column(String, unique=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tenant = relationship("Tenant", back_populates="users")
    profiles = relationship("Profile", back_populates="user", cascade="all, delete-orphan")


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name = Column(String, nullable=False)
    # Birth data
    birth_date = Column(DateTime, nullable=False) # Store as naive datetime, user timezone is separate
    birth_time_str = Column(String, nullable=False) # e.g. "14:30"
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    timezone = Column(String, nullable=False) # e.g. "Europe/Moscow"
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="profiles")


class InteractionLog(Base):
    __tablename__ = "interaction_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    intent = Column(String, nullable=True)
    input_text = Column(String, nullable=False)
    output_text = Column(String, nullable=False)
    tokens_used = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Memory(Base):
    __tablename__ = "memories"

    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    memory_type = Column(String, nullable=False) # fact, preference, correction, reading_summary
    content = Column(String, nullable=False)
    confidence = Column(Float, default=1.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    plan_name = Column(String, nullable=False, default="free") # free, pro, premium
    status = Column(String, nullable=False, default="active") # active, canceled, past_due
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
