from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from uuid import UUID

from app.core.redis_client import redis

# Claves:
# - revoked:{jti} -> "1" (TTL hasta exp)
# - refresh:{jti} -> HASH{sub, family} (TTL hasta exp)
# - family:{family_id} -> SET{jti1, jti2, ...} (TTL máximo de sus miembros)
# - family_revoked:{family_id} -> "1" (TTL heredado)

def _ttl_seconds(exp_ts: int) -> int:
    # exp_ts = epoch seconds
    now = int(datetime.now(timezone.utc).timestamp())
    return max(exp_ts - now, 1)

async def is_jti_revoked(jti: str) -> bool:
    return await redis.exists(f"revoked:{jti}") == 1

async def revoke_jti(jti: str, exp_ts: int) -> None:
    await redis.setex(f"revoked:{jti}", _ttl_seconds(exp_ts), "1")

async def register_refresh(jti: str, sub: str, family_id: str, exp_ts: int) -> None:
    pipe = redis.pipeline()
    pipe.hset(f"refresh:{jti}", mapping={"sub": sub, "family": family_id})
    pipe.expire(f"refresh:{jti}", _ttl_seconds(exp_ts))
    pipe.sadd(f"family:{family_id}", jti)
    # TTL del set de familia como mínimo hasta el refresh más largo
    pipe.expire(f"family:{family_id}", _ttl_seconds(exp_ts))
    await pipe.execute()

async def family_is_revoked(family_id: str) -> bool:
    return await redis.exists(f"family_revoked:{family_id}") == 1

async def revoke_family(family_id: str, ttl_sec: int) -> None:
    # Marca familia como revocada
    pipe = redis.pipeline()
    pipe.setex(f"family_revoked:{family_id}", ttl_sec, "1")
    members = await redis.smembers(f"family:{family_id}")
    for jti in members:
        # No conocemos exp exacta de cada jti, usa ttl de familia como fallback
        pipe.setex(f"revoked:{jti}", ttl_sec, "1")
    # Opcional: limpiar set
    pipe.delete(f"family:{family_id}")
    await pipe.execute()

async def take_refresh_metadata(jti: str) -> Optional[Dict[str, Any]]:
    data = await redis.hgetall(f"refresh:{jti}")
    return data or None

async def invalidate_refresh(jti: str, exp_ts: int) -> None:
    # revoca jti y saca del set de su familia
    data = await take_refresh_metadata(jti)
    if data and "family" in data:
        await redis.srem(f"family:{data['family']}", jti)
    await revoke_jti(jti, exp_ts)
    # Opcional: borra el hash
    await redis.delete(f"refresh:{jti}")