from fastapi import APIRouter

from app.dependencies import shioaji_client
from app.schemas.trading import LoginRequest, LoginResponse

router = APIRouter(prefix="/api", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    state = shioaji_client.login(payload.api_key, payload.secret_key)
    return LoginResponse(success=True, **state.__dict__)
