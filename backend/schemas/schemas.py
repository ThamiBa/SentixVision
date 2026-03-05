from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict
from datetime import datetime

# ── CAMERA ──────────────────────────────────────────────────────
class CameraBase(BaseModel):
    name: str
    url: str
    location: str
    is_active: bool = True
    zone_config: Optional[Dict] = None

class CameraCreate(CameraBase):
    pass

class Camera(CameraBase):
    id: int
    tenant_id: int

    class Config:
        from_attributes = True

# ── USER ────────────────────────────────────────────────────────
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: str = "Viewer"

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    tenant_id: int

    class Config:
        from_attributes = True

# ── TENANT ──────────────────────────────────────────────────────
class TenantBase(BaseModel):
    name: str
    subscription_plan: str = "Standard"

class TenantCreate(TenantBase):
    pass

class Tenant(TenantBase):
    id: int
    created_at: datetime
    users: List[User] = []
    cameras: List[Camera] = []

    class Config:
        from_attributes = True

# ── ANALYTICS ───────────────────────────────────────────────────
class AnalyticsRecord(BaseModel):
    timestamp: datetime
    worker_count: int
    client_count: int
    total_count: int
    mood_score: int
    emotion_metrics: Dict

    class Config:
        from_attributes = True
