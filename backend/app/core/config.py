"""Application configuration via pydantic-settings.

All tunables live here — no magic numbers scattered through the codebase. Nested
groups (motion, follow, search, battery) use the ``__`` env delimiter, e.g.
``MOTION__MAX_LINEAR_SPEED=0.6``.

Settings are loaded once and cached (:func:`get_settings`) so the same immutable
instance is shared across the process.
"""

from __future__ import annotations

from enum import Enum
from functools import lru_cache

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    """Deployment environment."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class MotionLimits(BaseModel):
    """Hard ceilings applied to every velocity command sent to the robot."""

    max_linear_speed: float = Field(0.6, gt=0, description="metres/second")
    max_angular_speed: float = Field(1.5, gt=0, description="radians/second")


class FollowSettings(BaseModel):
    """Proportional-controller gains for the follow-person behavior."""

    kp_angular: float = Field(1.4, gt=0, description="offset -> angular velocity gain")
    kp_linear: float = Field(0.8, gt=0, description="distance error -> linear velocity gain")
    target_bbox_ratio: float = Field(
        0.45, gt=0, lt=1, description="desired person bbox height / frame height"
    )
    deadzone: float = Field(
        0.06, ge=0, lt=0.5, description="normalized center deadzone (no correction)"
    )


class SearchSettings(BaseModel):
    """In-place scan behavior when the target is lost."""

    angular_speed: float = Field(0.8, gt=0, description="scan rotation speed (rad/s)")


class BatterySettings(BaseModel):
    """Battery guardrails that can override any behavior."""

    low_pct: float = Field(25.0, ge=0, le=100)
    critical_pct: float = Field(12.0, ge=0, le=100)


class Settings(BaseSettings):
    """Root settings object. Instantiated once via :func:`get_settings`."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

    # -- App --
    app_name: str = "Physical AI Robot Brain"
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = True
    log_level: str = "INFO"
    log_json: bool = False

    # -- API --
    api_prefix: str = "/api/v1"
    api_keys: list[str] = Field(default_factory=list)

    # -- Database (async) --
    database_url: str = "postgresql+asyncpg://robot:robot@localhost:5432/robotbrain"
    db_echo: bool = False

    # -- Redis --
    redis_url: str = "redis://localhost:6379/0"

    # -- AI wiring (swap implementations without code changes) --
    vision_detector: str = "mock"
    speech_recognizer: str = "mock"
    planner: str = "rule"
    memory_backend: str = "postgres"
    model_path: str = "/app/models"

    # -- Robot loop --
    robot_fps: int = Field(10, gt=0, le=60)

    # -- Nested tunables --
    motion: MotionLimits = Field(default_factory=MotionLimits)
    follow: FollowSettings = Field(default_factory=FollowSettings)
    search: SearchSettings = Field(default_factory=SearchSettings)
    battery: BatterySettings = Field(default_factory=BatterySettings)

    # -- Persistence --
    persist_logs: bool = True
    log_sample_n: int = Field(1, ge=1, description="persist 1 of every N steps")

    @field_validator("api_keys", mode="before")
    @classmethod
    def _split_api_keys(cls, v: object) -> object:
        """Allow ``API_KEYS=a,b,c`` in addition to a JSON list."""
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v

    @property
    def is_production(self) -> bool:
        return self.environment is Environment.PRODUCTION

    @property
    def auth_enabled(self) -> bool:
        return bool(self.api_keys)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide cached settings instance."""
    return Settings()
