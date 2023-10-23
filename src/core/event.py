"""
Base event definition.
Author: Oron Moshe
Date: 22/10/2023
"""
# ----- Imports ----- #

import dataclasses
from typing import Optional

from core.exceptions import RemindMeBaseException
from datetime import datetime

# ----- Exceptions ----- #


class EventAlreadyExist(RemindMeBaseException):
    """
    Event already exist exception.
    """
    pass


class EventDoesNotExist(RemindMeBaseException):
    """
    Event does not exist exception.
    """
    pass


class EventAlreadyInEvent(RemindMeBaseException):
    """
    Event already in the event exception.
    """
    pass


class EventDoesNotInEvent(RemindMeBaseException):
    """
    Event does not in the event exception.
    """
    pass


class ModifyChangesAreInvalid(RemindMeBaseException):
    """
    Modify changes are invalid exception.
    """
    pass


class InvalidAttribute(RemindMeBaseException):
    """
    Invalid attribute exception.
    """
    pass


class UserAlreadySubscriber(RemindMeBaseException):
    """
    User is already a subscriber exception.
    """
    pass


class UserDoesNotASubscriber(RemindMeBaseException):
    """
    User is not a subscriber exception.
    """
    pass


# ----- Classes ----- #


@dataclasses.dataclass
class Event:
    """
    Dataclass that store events details.
    """
    event_id: Optional[str]
    created_user_id: str
    event_name: str
    event_description: str
    location: str
    subscribers: list[str]  # list of users ids.
    event_start_time: datetime
    event_end_time: datetime
    creation_time: Optional[datetime]
