from fastapi import HTTPException, Depends
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, Any, Union
from cas import CASClientV3
from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta
from ..settings import settings
import traceback
from .key import UserKey, ModKey, AdminKey
from prisma.models import AccessLevel as DbAccessLevel


# CASClient abuses class constructors (__new__),
# so we are using the versioned class directly
cas_client: CASClientV3 = CASClientV3(
    service_url=settings.login_endpoint,
    server_url=settings.cas_server_url,
)


def _is_admin(rut: str):
    """
    Checks if user with given RUT is an admin.
    """
    admin = settings.admin_rut.get_secret_value()
    if admin == "":
        return False
    return rut == admin


async def _is_mod(rut: str):
    """
    Checks if user with given RUT is a mod.
    """
    level = await DbAccessLevel.prisma().find_unique(where={"user_rut": rut})
    if level is None:
        return False
    return level.is_mod


async def generate_token(user: str, rut: str, expire_delta: Optional[float] = None):
    """
    Generate a signed token (one that is unforgeable) with the given user, rut and
    expiration time.
    """
    # Calculate the time that this token expires
    if expire_delta is None:
        expire_delta = settings.jwt_expire
    expire_time = datetime.utcnow() + timedelta(seconds=expire_delta)
    # Pack user, rut and expire date into a signed token
    payload: dict[str, Union[datetime, str, bool]] = {
        "exp": expire_time,
        "sub": user,
        "rut": rut,
    }
    if _is_admin(rut):
        payload["is_admin"] = True
    elif await _is_mod(rut):
        payload["is_mod"] = True
    token = jwt.encode(
        payload, settings.jwt_secret.get_secret_value(), settings.jwt_algorithm
    )
    return token


def decode_token(token: str):
    """
    Verify a token and extract the user data within it.
    """
    try:
        payload = jwt.decode(
            token, settings.jwt_secret.get_secret_value(), [settings.jwt_algorithm]
        )
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    if not isinstance(payload["sub"], str):
        raise HTTPException(status_code=401, detail="Invalid token")
    if not isinstance(payload["rut"], str):
        raise HTTPException(status_code=401, detail="Invalid token")

    if "is_admin" in payload:
        if not isinstance(payload["is_admin"], bool):
            raise HTTPException(status_code=401, detail="Invalid token")
        if payload["is_admin"]:
            return AdminKey(payload["sub"], payload["rut"])

    if "is_mod" in payload:
        if not isinstance(payload["is_mod"], bool):
            raise HTTPException(status_code=401, detail="Invalid token")
        if payload["is_mod"]:
            return ModKey(payload["sub"], payload["rut"])

    return UserKey(payload["sub"], payload["rut"])


def require_authentication(
    bearer: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
):
    """
    Intended for API endpoints that requires user authentication.

    Example:
    def endpoint(user_data: UserKey = Depends(require_authentication)):
        pass
    """
    return decode_token(bearer.credentials)


def require_mod_auth(
    bearer: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
):
    """
    Intended for API endpoints that requires authentication with mod access.

    Example:
    def endpoint(user_data: ModKey = Depends(require_mod_auth)):
        pass
    """
    key = require_authentication(bearer=bearer)
    if not key.is_mod:
        raise HTTPException(status_code=403, detail="Insufficient access")
    return key


def require_admin_auth(
    bearer: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
):
    """
    Intended for API endpoints that requires authentication with admin access.

    Example:
    def endpoint(user_data: AdminKey = Depends(require_admin_auth)):
        pass
    """
    key = require_authentication(bearer=bearer)
    if not key.is_admin:
        raise HTTPException(status_code=403, detail="Insufficient access")
    return key


async def login_cas(next: Optional[str] = None, ticket: Optional[str] = None):
    """
    Login endpoint.
    Has two uses, depending on the presence of `ticket`.

    If `ticket` is not present, then it redirects the browser to the CAS login page.
    This type of requests come from the user browser, who was probably redirected here
    after clicking a "Login" button in the frontend.

    If `ticket` is present, then we assume that the CAS login page redirected the user
    to this endpoint with a token. We verify the token and create a JWT. Then, the
    browser is redirected to the frontend along with this JWT.
    In this case, the frontend URL is whatever the `next` field indicates.
    """
    if ticket:
        # User has just authenticated themselves with CAS, and were redirected here
        # with a token
        if not next:
            return HTTPException(status_code=422, detail="Missing next URL")

        # Verify that the ticket is valid directly with the authority (the CAS server)
        user: Any
        attributes: Any
        _pgtiou: Any
        try:
            (
                user,
                attributes,
                _pgtiou,
            ) = cas_client.verify_ticket(  # pyright: ignore[reportUnknownMemberType]
                ticket
            )
        except Exception:
            traceback.print_exc()
            return HTTPException(status_code=502, detail="Error verifying CAS ticket")

        if not isinstance(user, str) or not isinstance(attributes, dict):
            # Failed to authenticate
            return HTTPException(status_code=401, detail="Authentication failed")

        # Get rut
        rut: Any = attributes["carlicense"]
        if not isinstance(rut, str):
            return HTTPException(
                status_code=500, detail="RUT is missing from CAS attributes"
            )

        # CAS token was validated, generate JWT token
        token = await generate_token(user, rut)

        # Redirect to next URL with JWT token attached
        return RedirectResponse(next + f"?token={token}")
    else:
        # User wants to authenticate
        # Redirect to authentication page
        cas_login_url: Any = (
            cas_client.get_login_url()  # pyright: ignore[reportUnknownMemberType]
        )
        if not isinstance(cas_login_url, str):
            return HTTPException(
                status_code=500, detail="CAS redirection URL not found"
            )
        return RedirectResponse(cas_login_url)


class AccessLevelOverview(BaseModel):
    name: Optional[str] = None

    # attributes from db
    user_rut: str
    is_mod: bool
    created_at: datetime
    updated_at: datetime
