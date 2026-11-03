from dataclasses import dataclass
from typing import List, Optional
from fastapi import Header, HTTPException, status

@dataclass
class Actor:
    id: str
    role: str
    type: str # "human", "agent", "system"

VALID_ROLES = {
    "ap_clerk": "human",
    "procurement_owner": "human",
    "finance_approver": "human",
    "invoice_intake_agent": "agent",
    "invoice_match_agent": "agent",
    "ap_admin": "human",
}

def get_current_actor(
    authorization: Optional[str] = Header(None),
    x_actor_role: Optional[str] = Header(None),
    x_actor_id: Optional[str] = Header(None),
) -> Actor:
    """
    Resolves the caller identity and role.
    Accepts:
    1. Direct X-Actor-Role & X-Actor-ID headers (preferred for transparent workbench/CLI testing)
    2. Bearer token in Authorization header (e.g. Bearer ap_clerk, Bearer finance_approver, etc.)
    """
    role = None
    actor_id = x_actor_id

    if x_actor_role:
        role = x_actor_role.strip().lower()
    elif authorization and authorization.startswith("Bearer "):
        token = authorization[7:].strip()
        # Handle bearer tokens formatted like "token-<role>" or simply "<role>"
        if token.startswith("token-"):
            role = token[6:].lower()
        elif token in VALID_ROLES:
            role = token.lower()
        else:
            role = "ap_clerk"

    if not role:
        # Default fallback to ap_clerk for frictionless local demo
        role = "ap_clerk"

    if role not in VALID_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": "INVALID_ROLE",
                    "message": f"Role '{role}' is not a valid actor role.",
                }
            },
        )

    actor_type = VALID_ROLES[role]
    if not actor_id:
        actor_id = f"{role}_user"

    return Actor(id=actor_id, role=role, type=actor_type)


def require_roles(allowed_roles: List[str]):
    def role_checker(actor: Actor = Header(None)) -> Actor:
        pass
    # We will use this in endpoint dependencies
    def dependency(
        authorization: Optional[str] = Header(None),
        x_actor_role: Optional[str] = Header(None),
        x_actor_id: Optional[str] = Header(None),
    ) -> Actor:
        actor = get_current_actor(authorization, x_actor_role, x_actor_id)
        if actor.role not in allowed_roles and "ap_admin" not in allowed_roles and actor.role != "ap_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "PERMISSION_DENIED",
                        "message": f"Actor role '{actor.role}' lacks permission for this action. Allowed roles: {allowed_roles}",
                    }
                },
            )
        return actor
    return dependency

