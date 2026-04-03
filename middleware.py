from fastapi import HTTPException, status, Depends
from database import User
from auth import get_current_user
from functools import wraps


# --- Role Hierarchy ---
ROLE_LEVELS = {
    "viewer": 1,
    "analyst": 2,
    "admin": 3
}


# --- Core Role Checker ---
def require_role(*allowed_roles: str):
    """
    Dependency that checks if the current user has one of the allowed roles.
    Usage: Depends(require_role("admin")) or Depends(require_role("analyst", "admin"))
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {' or '.join(allowed_roles)}. Your role: {current_user.role}"
            )
        return current_user
    return role_checker


# --- Minimum Role Level Checker ---
def require_min_role(min_role: str):
    """
    Dependency that checks if user meets minimum role level.
    viewer(1) < analyst(2) < admin(3)
    Usage: Depends(require_min_role("analyst")) — allows analyst and admin
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_level = ROLE_LEVELS.get(current_user.role, 0)
        required_level = ROLE_LEVELS.get(min_role, 99)

        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Minimum required role: {min_role}. Your role: {current_user.role}"
            )
        return current_user
    return role_checker


# --- Prebuilt Role Dependencies ---
# Use these directly in route definitions for clean code

def admin_only(current_user: User = Depends(get_current_user)) -> User:
    """Only admins can access this route."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin role required."
        )
    return current_user


def analyst_or_admin(current_user: User = Depends(get_current_user)) -> User:
    """Analysts and admins can access this route."""
    if current_user.role not in ["analyst", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Analyst or Admin role required."
        )
    return current_user


def any_authenticated_user(current_user: User = Depends(get_current_user)) -> User:
    """Any logged in user can access this route."""
    return current_user


# --- Role Permission Summary (for docs reference) ---
PERMISSIONS = {
    "viewer": [
        "GET /records",
        "GET /records/{id}",
    ],
    "analyst": [
        "GET /records",
        "GET /records/{id}",
        "GET /dashboard/summary",
        "GET /dashboard/trends",
        "GET /dashboard/categories",
    ],
    "admin": [
        "ALL endpoints"
    ]
}
