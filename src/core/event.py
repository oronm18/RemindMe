"""
Base event definition.
Author: Oron Moshe
Date: 22/10/2023
"""
# ----- Imports ----- #

import dataclasses
from remind_me_utils import generate_unique_id
from datetime import datetime


# ----- Classes ----- #


@dataclasses.dataclass
class EventDetails:
    """
    Dataclass that store events details.
    """
    event_id: str
    created_user_id: str
    event_name: str
    event_description: str
    event_start_time: datetime
    event_end_time: datetime


class BaseEvent:
    """
    Base Event for the project.
    """
    def __init__(
            self,
            event_name: str,
            created_user_id: str,
            event_description: str,
            event_start_time: datetime,
            event_end_time: datetime = None
    ):
        """
        Initialize a new event.
        :param event_name: Event name.
        :param event_description: Description of the event.
        :param event_start_time: When does it start.
        :param event_end_time: When does it end.
        """
        # Make the end time be the start time if not given.
        event_end_time = event_end_time if event_end_time else event_start_time

        self.event_details = EventDetails(
            event_id=generate_unique_id(),
            event_name=event_name,
            created_user_id=created_user_id,
            event_description=event_description,
            event_start_time=event_start_time,
            event_end_time=event_end_time
        )

    def set_event_details(
            self,
            event_name: str = None,
            event_description: str = None,
            event_start_time: datetime = None,
            event_end_time: datetime = None
    ):
        if event_name:
            self.event_details.event_name = event_name
        if event_description:
            self.event_details.event_description = event_description
        if event_start_time:
            self.event_details.event_start_time = event_start_time
        if event_end_time:
            self.event_details.event_end_time = event_end_time


# ----- Functions ----- #
