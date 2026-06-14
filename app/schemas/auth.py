from __future__ import annotations

"""Authentication Pydantic schemas."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class LoginRequest(BaseModel):
    """Login form payload."""

    email: EmailStr
    password: str = Field(min_length=1)


class SignupRequest(BaseModel):
    """Signup form payload with password confirmation."""

    email: EmailStr
    password: str = Field(min_length=4)
    confirm_password: str = Field(min_length=4)

    @model_validator(mode="after")
    def passwords_match(self) -> "SignupRequest":
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class UserRead(BaseModel):
    """Authenticated user returned from services."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    is_active: bool = True


class AuthMessageResponse(BaseModel):
    """Simple auth operation response."""

    success: bool
    message: str


class AuthStatusResponse(BaseModel):
    """Current authentication status."""

    authenticated: bool
    email: Optional[EmailStr] = None
