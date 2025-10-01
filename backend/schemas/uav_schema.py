from pydantic import BaseModel, Field


class DateBoundsQuery(BaseModel):
    min_date: str = Field(..., description='Начало диапазона дат в ISO-формате')
    max_date: str = Field(..., description='Конец диапазона дат в ISO-формате')
    limit: int | None = Field(None, ge=1, le=1000)


class DateBoundsResponse(BaseModel):
    min_date: str | None
    max_date: str | None


class UavFlightsResponse(BaseModel):
    flights: list[dict] | None
