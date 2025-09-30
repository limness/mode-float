from pydantic import BaseModel

class DateBoundsResponse(BaseModel):
    min_date: str | None
    max_date: str | None

