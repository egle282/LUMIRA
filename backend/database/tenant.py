from typing import Optional
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

async def set_tenant_context(session: AsyncSession, tenant_id: str):
    """
    Sets the current tenant ID in the Postgres session.
    This activates the Row-Level Security (RLS) policies for the transaction.
    """
    await session.execute(
        text("SELECT set_config('app.current_tenant', :tenant_id, false)"),
        {"tenant_id": tenant_id}
    )

def get_tenant_id_from_request(request: Request) -> str:
    """
    Extracts tenant_id from the request headers or context.
    For MVP, we might pass it via a custom header 'X-Tenant-ID'.
    """
    tenant_id = request.headers.get("X-Tenant-ID")
    if not tenant_id:
        raise ValueError("X-Tenant-ID header is missing")
    return tenant_id
