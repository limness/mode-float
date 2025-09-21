# from datetime import datetime
#
# from sqlalchemy.ext.asyncio import AsyncSession
#
# from src.core.time import app_now
# from src.database import (
#     EventModel,
#     EventParticipantModel,
#     EventRequestModel,
#     FileModel,
#     InterestsEnum,
#     UserModel,
# )
# from src.repositories import (
#     event_participant_repo,
#     event_repo,
#     event_request_repo,
#     file_repo,
#     seen_event_repo,
#     user_repo,
# )
# from src.services.exceptions import (
#     EventCreatorLeaveError,
#     EventExpiredError,
#     EventNotFoundError,
#     NotEventCreatorError,
#     UserIsAlreadyParticipantError,
#     UserNotFoundError,
#     UserNotParticipantError,
# )
#
#
# async def create_event(
#     db_session: AsyncSession,
#     description: str,
#     interests: list[InterestsEnum],
#     starts_at: datetime,
#     address: str,
#     creator_id: int,
#     is_private: bool = False,
#     join_type: str | None = None,
#     join_link: str | None = None,
#     priority: int = 0,
#     file: FileModel | None = None,
#     created_at: datetime | None = None,
# ) -> EventModel:
#     """
#     Create a new event.
#
#     Args:
#         db_session: Database session
#         description: Event name
#         interests: Interests (comma-separated)
#         starts_at: Start date and time (timezone required)
#         address: Event location
#         creator_id: Creator ID
#         is_private: Private event requires organizer approve
#         join_type: Join type
#         join_link: Join link
#         priority: Event priority
#         file: Event file (photo, video, etc.)
#         created_at: Event creation date
#
#     Returns:
#         Created event
#
#     Raises:
#         ValueError: If no event exists
#         ValueError: If no event participants exist
#     """
#     # Check if creator exists
#     creator = await user_repo.get_one(db_session, telegram_id=creator_id)
#     if not creator:
#         raise UserNotFoundError(f'User {creator_id} not found')
#
#     # Check if timezone is set
#     if starts_at.tzinfo is None or starts_at.tzinfo.utcoffset(starts_at) is None:
#         raise ValueError('Timezone required')
#
#     # Check if date is in the future
#     if starts_at <= datetime.now(starts_at.tzinfo):
#         raise ValueError('Event date must be in the future')
#
#     # Create event
#     event = await event_repo.create_one(
#         db_session,
#         description=description,
#         interests=interests,
#         starts_at=starts_at,
#         address=address,
#         creator_id=creator_id,
#         is_private=is_private,
#         join_type=join_type,
#         join_link=join_link,
#         priority=priority,
#         file_id=file.id if file else None,
#         created_at=created_at,
#     )
#     await event_participant_repo.create_one(db_session, user_id=creator_id, event_id=event.id)
#     await mark_event_as_seen(
#         db_session,
#         user_id=creator_id,
#         event_id=event.id,
#         seen_at=app_now(),
#     )
#     return event
#
#
# async def get_user_events(db_session: AsyncSession, user_id: int) -> list[EventModel]:
#     """
#     Get all events where user is a participant (including created by user).
#     """
#     return await event_participant_repo.get_user_events(db_session, user_id)
#
#
# async def get_event(db_session: AsyncSession, event_id: int) -> EventModel | None:
#     """
#     Get event by id.
#     """
#     return await event_repo.get_one(db_session, id=event_id)
#
#
# async def delete_event(db_session: AsyncSession, event_id: int, user_id: int) -> None:
#     """
#     Delete an event and all its associated data.
#
#     This function performs the following operations:
#     - Validates that the event exists.
#     - Ensures that the requesting user is the creator of the event.
#     - Deletes all participants associated with the event.
#     - Deletes all views (seen records) related to the event.
#     - Deletes all join requests for the event.
#     - Deletes the event record itself.
#     - Deletes the event's associated file (e.g., photo).
#
#     Args:
#         db_session (AsyncSession): The database session used for querying and deleting data.
#         event_id (int): The ID of the event to be deleted.
#         user_id (int): The ID of the user requesting the deletion.
#
#     Raises:
#         EventNotFoundError: If the event does not exist.
#         NotEventCreatorError: If the user is not the creator of the event.
#     """
#     event_model = await event_repo.get_one(db_session, id=event_id)
#
#     if not event_model:
#         raise EventNotFoundError('Event not found.')
#
#     if event_model.creator_id != user_id:
#         raise NotEventCreatorError('Only the event creator can delete the event.')
#
#     # del all participants from event
#     await event_participant_repo.delete(db_session, event_id=event_id)
#
#     # del all views of the event
#     await seen_event_repo.delete(db_session, event_id=event_id)
#
#     # del all requests of event
#     await event_request_repo.delete(db_session, event_id=event_id)
#
#     # del event itself
#     await event_repo.delete(db_session, id=event_id)
#
#     # del event photo
#     await file_repo.delete(db_session, id=event_model.file_id)
#
#
# async def format_event_message(event: EventModel) -> str:
#     """
#     Format event for display in message.
#     """
#     message = f'{event.description[:800]}\n\n'
#
#     # Add interests
#     message += '*Что будет:*\n'
#     if event.interests:
#         for interest in event.interests:
#             message += f'{interest.description}\n'
#     else:
#         message += '• Не указано\n'
#
#     # Add date and time
#     message += '\n-----------\n'
#     message += f'📍 *{event.starts_at.strftime("%d.%m %H:%M")} | * {event.address}\n'
#
#     return message[:1024]
#
#
# async def mark_event_as_seen(
#     db_session, user_id: int, event_id: int, seen_at: datetime | None = None
# ) -> None:
#     """
#     Mark event as seen for a user.
#
#     Args:
#         db_session: Database session
#         user_id: User ID who has seen event
#         event_id: Seen event ID
#         seen_at: Seen date
#
#     Raises:
#         UserNotFoundError: If user is not found
#         EventNotFoundError: If event is not found
#     """
#
#     user = await user_repo.get_one(db_session, telegram_id=user_id)
#
#     if not user:
#         raise UserNotFoundError(f'User {user_id} not found.')
#
#     event = await event_repo.get_one(db_session, id=event_id)
#
#     if not event:
#         raise EventNotFoundError(f'Event {event_id} not found.')
#
#     await seen_event_repo.create_one(
#         db_session, user_id=user_id, event_id=event_id, seen_at=seen_at
#     )
#
#
# async def validate_join_event(
#     db_session: AsyncSession,
#     user_id: int,
#     event_id: int,
# ) -> tuple[UserModel, EventModel]:
#     """
#     Validate whether a user is eligible to join a given event.
#
#     This function performs the following checks:
#     - Verifies that the user exists.
#     - Verifies that the event exists.
#     - Ensures the user is not already a participant.
#     - Ensures the event has not already started or expired.
#
#     Raises:
#         UserNotFoundError: If the user with the given ID does not exist.
#         EventNotFoundError: If the event with the given ID does not exist.
#         UserIsAlreadyParticipantError: If the user is already a participant in the event.
#         EventExpiredError: If the event has already started or passed.
#
#     Returns:
#         tuple[UserModel, EventModel]: The user and event objects, if all checks pass.
#     """
#
#     user = await user_repo.get_one(db_session, telegram_id=user_id)
#     if not user:
#         raise UserNotFoundError(f'User {user_id} not found.')
#
#     event = await event_repo.get_one(db_session, id=event_id)
#     if not event:
#         raise EventNotFoundError(f'Event {event_id} not found.')
#
#     is_participant = await event_participant_repo.is_user_participant(db_session, user_id, event_id)
#     if is_participant:
#         raise UserIsAlreadyParticipantError(f'User {user_id} is already participant.')
#
#     if event.starts_at <= app_now():
#         raise EventExpiredError(f'Event {event_id} is expired.')
#
#     return user, event
#
#
# async def join_event(
#     db_session: AsyncSession,
#     user_id: int,
#     event_id: int,
#     joined_at: datetime | None = None,
#     validate: bool = True,
# ) -> EventParticipantModel:
#     """
#     Add a user to an event's participants list.
#
#     Optionally validates whether the user can join the event by checking:
#     - User existence
#     - Event existence
#     - Non-duplicate participation
#     - Event is upcoming
#
#     Args:
#         db_session (AsyncSession): Active SQLAlchemy async DB session.
#         user_id (int): Telegram user ID.
#         event_id (int): Target event ID.
#         joined_at (datetime | None, optional): Timestamp of joining. Defaults to current time if not provided.
#         validate (bool): Whether to validate eligibility before joining. Defaults to True.
#
#     Raises:
#         UserNotFoundError
#         EventNotFoundError
#         UserIsAlreadyParticipantError
#         EventExpiredError
#
#     Returns:
#         EventParticipantModel: The created participant record.
#     """
#
#     if validate:
#         await validate_join_event(db_session, user_id, event_id)
#
#     return await event_participant_repo.create_one(
#         db_session, user_id=user_id, event_id=event_id, joined_at=joined_at
#     )
#
#
# async def is_user_participant(db_session: AsyncSession, user_id: int, event_id: int) -> bool:
#     """
#     Check if user is already a participant of the event.
#
#     Args:
#         db_session (AsyncSession): database session
#         event_id (int): ID of the event
#         user_id (int): ID of the user
#
#     Returns:
#         bool: True if the user is already a participant
#     """
#     return await event_participant_repo.is_user_participant(db_session, user_id, event_id)
#
#
# async def leave_event(db_session: AsyncSession, event_id: int, user_id: int) -> None:
#     """
#     Leave an event as a participant.
#
#     Args:
#         db_session (AsyncSession): The async database session.
#         event_id (int): ID of the event to leave.
#         user_id (int): ID of the user attempting to leave the event.
#
#     Raises:
#         EventNotFoundError: If the specified event does not exist.
#         EventCreatorLeaveError: If the user is the creator of the event.
#         UserNotParticipantError: If the user is not a participant of the event.
#     """
#
#     event = await event_repo.get_one(db_session, id=event_id)
#
#     if not event:
#         raise EventNotFoundError(f'Event {event_id} not found.')
#
#     if event.creator_id == user_id:
#         raise EventCreatorLeaveError('Event creator cannot leave their own event.')
#
#     is_participant = await event_participant_repo.is_user_participant(db_session, user_id, event_id)
#     if not is_participant:
#         raise UserNotParticipantError('User is not a participant of the event.')
#
#     await event_participant_repo.leave_event(db_session, event_id=event_id, user_id=user_id)
#
#
# async def get_event_request(
#     db_session: AsyncSession, event_id: int, user_id: int
# ) -> EventRequestModel:
#     """
#     Create new event request
#     """
#     return await event_request_repo.get_one(db_session, event_id=event_id, user_id=user_id)
#
#
# async def create_event_request(
#     db_session: AsyncSession, event_id: int, user_id: int
# ) -> EventRequestModel:
#     """
#     Create new event request
#     """
#     return await event_request_repo.create_one(db_session, event_id=event_id, user_id=user_id)
#
#
# async def delete_event_request(db_session: AsyncSession, event_id: int, user_id: int) -> None:
#     """
#     Delete a user's request to join an event.
#
#     This function:
#     - Ensures the event exists.
#     - Ensures the user exists.
#     - Deletes the user's join request for the specified event.
#
#     Args:
#        db_session (AsyncSession): The database session for accessing data.
#        event_id (int): The ID of the event from which to remove the request.
#        user_id (int): The Telegram ID of the user whose request is to be deleted.
#
#     Raises:
#        EventNotFoundError: If the event with the given ID does not exist.
#        UserNotFoundError: If the user with the given Telegram ID does not exist.
#     """
#     event = await event_repo.get_one(db_session, id=event_id)
#
#     if not event:
#         raise EventNotFoundError(f'Event {event_id} not found.')
#
#     user = await user_repo.get_one(db_session, telegram_id=user_id)
#
#     if not user:
#         raise UserNotFoundError(f'User {user_id} not found.')
#
#     await event_request_repo.delete(db_session, event_id=event_id, user_id=user_id)
