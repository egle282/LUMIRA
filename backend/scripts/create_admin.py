import asyncio
import argparse
import sys
from backend.database.database import AsyncSessionLocal
from backend.database.models import User, Tenant
from backend.api.auth import get_password_hash
from sqlalchemy import text
from sqlalchemy.future import select

async def create_admin(email: str, password: str):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Create default admin tenant if not exists
            result = await session.execute(select(Tenant).where(Tenant.name == "System Admin"))
            tenant = result.scalar_one_or_none()
            if not tenant:
                tenant = Tenant(name="System Admin")
                session.add(tenant)
                await session.flush()

            # Set tenant context for RLS policy enforcement
            await session.execute(text(f"SET app.current_tenant = '{tenant.id}'"))

            # Check if user already exists
            result = await session.execute(select(User).where(User.email == email))
            existing_user = result.scalar_one_or_none()
            if existing_user:
                print(f"Error: User {email} already exists.")
                return

            # Create the admin user
            admin = User(
                email=email,
                hashed_password=get_password_hash(password),
                role="admin",
                tenant_id=tenant.id
            )
            session.add(admin)
            
        print(f"Admin user {email} created successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bootstrap the first admin user.")
    parser.add_argument("email", type=str, help="Admin email address")
    parser.add_argument("password", type=str, help="Admin password (at least 8 chars)")
    
    args = parser.parse_args()
    
    if len(args.password) < 8:
        print("Error: Password must be at least 8 characters.")
        sys.exit(1)
        
    asyncio.run(create_admin(args.email, args.password))
