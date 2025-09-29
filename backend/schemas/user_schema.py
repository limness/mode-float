from pydantic import BaseModel, Field


class UserInfoResponseSchema(BaseModel):
    uid: str | None = Field(None, description='Keycloak subject (sub)')
    username: str | None = None
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    roles: list[str] | None = []
    client_roles: list[str] | None = []
    groups: list[str] | None = []
    exp: int | None = None
    iat: int | None = None
