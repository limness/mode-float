import enum


class EventCreationMetricNameEnum(enum.StrEnum):
    CREATION_STARTED = 'creation_started'
    CREATION_DESCRIPTION_STEP = 'creation_description_step'
    CREATION_DATE_STEP = 'creation_date_step'
    CREATION_TIME_STEP = 'creation_time_step'
    CREATION_LOCATION_STEP = 'creation_location_step'
    CREATION_PHOTO_STEP = 'creation_photo_step'
    CREATION_INTERESTS_STEP = 'creation_interests_step'
    CREATION_JOIN_TYPE_STEP = 'creation_join_type_step'
    CREATION_PRIVACY_STEP = 'creation_privacy_step'
    CREATION_JOIN_LINK_STEP = 'creation_join_link_step'
    CREATION_COMPLETED = 'creation_completed'
    CREATION_CANCELLED = 'creation_cancelled'
