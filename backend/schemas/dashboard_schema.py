from pydantic import BaseModel, Field


class DatalensEmbedRequestSchema(BaseModel):
    embed_id: str = Field(..., min_length=8)
    ttl_seconds: int | None = Field(None, ge=1)
    params: dict[str, str | list[str]] | None = None


class DatalensEmbedResponseSchema(BaseModel):
    url: str
