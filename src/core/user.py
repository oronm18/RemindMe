"""
Base user definition.
Author: Oron Moshe
Date: 22/10/2023
"""
# ----- Imports ----- #

import dataclasses

from core.exceptions import RemindMeBaseException
from remind_me_utils import generate_unique_id
from datetime import datetime


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
    user_id: str
    user_name: str
    user_mail: str
    hashed_password: str
    events: list[str] = dataclasses.field(default_factory=list)
    #
    # def add_event(self, event_id):
    #     """
    #     Add an event id to the user events.
    #     :param event_id: A given event id.
    #     :return: None
    #     """
    #     if event_id in self.events:
    #         raise UserAlreadyExist()
    #     self.events.append(event_id)
    #
    # def remove_event(self, event_id):
    #     """
    #     Remove an event id from the user events.
    #     :param event_id: A given event id.
    #     :return: None
    #     """
    #     self.events = [event for event in self.events if event != event_id]
    #
