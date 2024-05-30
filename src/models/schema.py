import re
from datetime import datetime
from typing import Any

from fastapi.encoders import jsonable_encoder
from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    HttpUrl,
    PositiveInt,
    SecretStr,
    computed_field,
    field_validator, model_validator,
)

STRONG_PASSWORD_PATTERN = re.compile(r"^(?=.*[\d])(?=.*[!@#$%^&*])[\w!@#$%^&*]{6,128}$")


class CustomModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )

    @model_validator(mode="before")
    @classmethod
    def set_null_microseconds(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Remove microseconds from datetime object"""
        datetime_fields = {
            k: v.replace(microsecond=0)
            for k, v in data.items()
            if isinstance(v, datetime)
        }

        return {**data, **datetime_fields}


class Package(CustomModel):
    id: str
    create_at: datetime
    update_at: datetime | None = None
    summary: str
    description: str | None = None
    comment: str | None = None
    home_page: HttpUrl | None = None
    docs_url: HttpUrl | None = None
    package_url: HttpUrl | None = None
    author_name: str | None = None
    author_email: str | None = None
    license: str | None = None


class Release(CustomModel):
    id: PositiveInt
    major_ver: int
    minor_ver: int
    build_ver: int
    create_at: datetime
    comment: str | None = None
    url: HttpUrl | None = None
    size: int | None = None
    package_id: str


class User(CustomModel):
    id: PositiveInt
    name: str
    email: EmailStr
    hash_password: SecretStr
    create_at: datetime
    login_at: datetime | None = None
    profile_image_url: HttpUrl | None = None


class ViewModelBase(CustomModel):
    user_id: int | None = Field(default=None)

    @computed_field
    @property
    def is_logged_in(self) -> bool:
        return self.user_id is not None


class HomePageView(ViewModelBase):
    release_count: int = Field(default=0)
    user_count: int = Field(default=0)
    package_count: int = Field(default=0)
    packages: list[Package | None] = Field(default_factory=list)


class SearchPageView(ViewModelBase):
    packages: list[Package | None] = Field(default_factory=list)


class DetailPackageView(ViewModelBase):
    is_latest: bool = Field(default=True)
    maintainers: list = Field(default_factory=list)
    package: Package | None = Field(default=None)
    latest_release: Release | None = Field(default=None)

    @computed_field
    @property
    def latest_version(self) -> str:
        if self.package and self.latest_release:
            return (
                f"{self.latest_release.major_ver}"
                f".{self.latest_release.minor_ver}"
                f".{self.latest_release.build_ver}"
            )
        return "0.0.0"


class AccountPageView(ViewModelBase):
    user: User | None = Field(default=None)


class LoginForm(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class RegisterForm(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    password: str = Field(min_length=6, max_length=20)
    email: EmailStr
    age: int | None = Field(ge=18, lt=120, default=None)

    @field_validator("password", mode="after")
    @classmethod
    def valid_password(cls, password: str) -> str:
        if not re.match(STRONG_PASSWORD_PATTERN, password):
            raise ValueError(
                "Password must contain at least "
                "one lower character, "
                "one upper character, "
                "digit or "
                "special symbol",
            )
        return password
