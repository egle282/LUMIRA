import asyncio
import argparse
import sys
import uuid

from sqlalchemy import select

from backend.database.database import AsyncSessionLocal, AdminAsyncSessionLocal
from backend.database.models import User, Tenant
from backend.database.tenant import set_tenant_context
from backend.api.auth import get_password_hash


async def create_admin(email: str, password: str):
    if AdminAsyncSessionLocal is None:
        raise RuntimeError(
            "ADMIN_DATABASE_URL must be configured to safely check for existing users and tenants."
        )

    # The read-only admin connection is allowed to find records across tenants.
    async with AdminAsyncSessionLocal() as lookup:
        existing = await lookup.execute(select(User).where(User.email == email))
        if existing.scalars().first():
            print(f"Admin account {email} already exists; no changes made.")
            return
        tenant_result = await lookup.execute(
            select(Tenant).where(Tenant.name == "System Admin").limit(1)
        )
        existing_tenant = tenant_result.scalars().first()
        tenant_id = str(existing_tenant.id) if existing_tenant else str(uuid.uuid4())

    # Tenant context must be set before inserting either the tenant registry row
    # or the user row, because both tables are protected by RLS.
    async with AsyncSessionLocal() as session:
        async with session.begin():
            await set_tenant_context(session, tenant_id)
            if existing_tenant is None:
                session.add(Tenant(id=tenant_id, name="System Admin"))
                await session.flush()
            admin = User(
                email=email.lower().strip(),
                hashed_password=get_password_hash(password),
                role="admin",
                tenant_id=tenant_id,
            )
            session.add(admin)

    print(f"Admin user {email} created successfully!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bootstrap the first admin user.")
    parser.add_argument("email", type=str, help="Admin email address")
    parser.add_argument("password", type=str, help="Admin password (at least 8 chars)")
    args = parser.parse_args()
    if len(args.password) < 8:
        print("Error: Admin password must contain at least 8 characters.")
        sys.exit(1)
    asyncio.run(create_admin(args.email, args.password))
