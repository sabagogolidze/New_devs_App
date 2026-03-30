from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from decimal import Decimal, ROUND_HALF_UP
from app.services.cache import get_revenue_summary
from app.core.auth import authenticate_request as get_current_user

router = APIRouter()

@router.get("/properties")
async def get_properties(
    current_user: dict = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    import asyncpg
    import os

    tenant_id = getattr(current_user, "tenant_id", "default_tenant") or "default_tenant"

    conn = await asyncpg.connect(os.environ["DATABASE_URL"])
    try:
        rows = await conn.fetch(
            "SELECT id, name FROM properties WHERE tenant_id = $1 ORDER BY id",
            tenant_id
        )
        return [{"id": row["id"], "name": row["name"]} for row in rows]
    finally:
        await conn.close()

@router.get("/dashboard/summary")
async def get_dashboard_summary(
    property_id: str,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    
    tenant_id = getattr(current_user, "tenant_id", "default_tenant") or "default_tenant"
    
    revenue_data = await get_revenue_summary(property_id, tenant_id)
    
    total_revenue_float = float(revenue_data['total'])
    
    return {
        "property_id": revenue_data['property_id'],
        "total_revenue": total_revenue_float,
        "currency": revenue_data['currency'],
        "reservations_count": revenue_data['count']
    }
