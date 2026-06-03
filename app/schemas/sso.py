from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class SSOTokenCreate(BaseModel):
    empresa_id: UUID


class SSOTokenOut(BaseModel):
    token: str
    expires_at: datetime


class SSOLoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    empresa_id: UUID
    redirect_url: str
