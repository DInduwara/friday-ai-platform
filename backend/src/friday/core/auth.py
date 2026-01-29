from __future__ import annotations

import time
from typing import Any, Dict, Optional

import httpx
from fastapi import Depends, HTTPException, Request, status
from jose import jwt
from jose.exceptions import JWTError

from friday.core.config import settings

_JWKS_CACHE: dict[str, Any] = {"jwks": None, "fetched_at": 0.0}
_JWKS_TTL_SECONDS = 60.0


def _get_bearer_token(request: Request) -> str:
    auth = request.headers.get("authorization") or request.headers.get("Authorization")
    if not auth:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header")
    if not auth.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Authorization scheme")
    token = auth.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Empty bearer token")
    return token


async def _fetch_jwks() -> Dict[str, Any]:
    if not settings.CLERK_JWKS_URL:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server not configured: CLERK_JWKS_URL missing",
        )

    now = time.time()
    if _JWKS_CACHE["jwks"] and (now - float(_JWKS_CACHE["fetched_at"])) < _JWKS_TTL_SECONDS:
        return _JWKS_CACHE["jwks"]

    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(settings.CLERK_JWKS_URL)
        r.raise_for_status()
        jwks = r.json()

    _JWKS_CACHE["jwks"] = jwks
    _JWKS_CACHE["fetched_at"] = now
    return jwks


def _find_jwk_by_kid(jwks: Dict[str, Any], kid: str) -> Optional[Dict[str, Any]]:
    keys = jwks.get("keys") or []
    for k in keys:
        if k.get("kid") == kid:
            return k
    return None


async def get_current_user_id(request: Request) -> str:
    if not settings.CLERK_ISSUER:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server not configured: CLERK_ISSUER missing",
        )

    token = _get_bearer_token(request)

    # 1) Read token header to get kid
    try:
        header = jwt.get_unverified_header(token)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token header")

    kid = header.get("kid")
    if not kid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing kid")

    # 2) Fetch JWKS and pick the correct key
    jwks = await _fetch_jwks()
    jwk = _find_jwk_by_kid(jwks, kid)
    if not jwk:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown signing key (kid)")

    # 3) Verify JWT using that key
    try:
        payload = jwt.decode(
            token,
            jwk,  #  single JWK, not the entire jwks
            algorithms=["RS256"],
            issuer=settings.CLERK_ISSUER,
            options={"verify_aud": False},  # ok for many Clerk setups
        )
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user_id = payload.get("sub")
    if not user_id or not isinstance(user_id, str):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing user identity")

    return user_id


def require_user(user_id: str = Depends(get_current_user_id)) -> str:
    return user_id
