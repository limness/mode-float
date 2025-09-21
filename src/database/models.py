# from datetime import datetime
# from typing import Optional
#
# from sqlalchemy import (
#     ARRAY,
#     BigInteger,
#     Boolean,
#     CheckConstraint,
#     DateTime,
#     Enum,
#     ForeignKey,
#     Index,
#     Text,
#     event,
# )
# from sqlalchemy.orm import Mapped, mapped_column, relationship
# from sqlalchemy.sql import func
#
# from .base import Base


# class TemplateModel(Base):
#     __tablename__ = 'seen_events'
#
#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     user_id: Mapped[int] = mapped_column(
#         BigInteger, ForeignKey('users.telegram_id'), nullable=False
#     )
#     event_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('events.id'), nullable=False)
#     seen_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True), nullable=True, server_default=func.now()
#     )
#
#     user: Mapped[UserModel] = relationship(UserModel, back_populates='seen_events')
#     event: Mapped[EventModel] = relationship(EventModel, back_populates='seen_by')
