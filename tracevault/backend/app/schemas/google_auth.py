"""
TraceVault Google Auth Request Schema
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class GoogleAuthRequest(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1)
    picture: Optional[str] = None
    google_id: Optional[str] = None
    role: Optional[str] = Field(default="senior_investigator")
    department: Optional[str] = Field(default="Crime Branch / Law Enforcement")
