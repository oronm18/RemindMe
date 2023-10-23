"""
Base user definition.
Author: Oron Moshe
Date: 22/10/2023
"""
# ----- Imports ----- #

import dataclasses
from typing import Optional

from core.exceptions import RemindMeBaseException


# ----- Exceptions ----- #


class UserAlreadyExist(RemindMeBaseException):
    """
    User already exist exception.
    """
    pass


class UserDoesNotExist(RemindMeBaseException):
    """
    User does not exist exception.
    """
    pass


class EventAlreadyInUser(RemindMeBaseException):
    """
    Event already in the user exception.
    """
    pass


class EventDoesNotInUser(RemindMeBaseException):
    """
    Event does not in the user exception.
    """
    pass

# ----- Classes ----- #


@dataclasses.dataclass
class User:
    """
    Dataclass that store events details.
    """
    user_id: Optional[str]
    user_name: str
    user_mail: str
    hashed_password: str
    hosts_events: list[str] = dataclasses.field(default_factory=list)