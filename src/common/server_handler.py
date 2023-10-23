"""
Server handler file.
Author: Oron Moshe
Date: 22/10/2023
"""
# ----- Imports ----- #

from datetime import datetime
from pathlib import Path
from typing import Union, Optional

from common.events_handler import EventsHandler
from common.users_handler import UsersHandler
from core.user import User
from core.event import Event

# ----- Constants ----- #

USERS_DATABASE_NAME = "data.db"
EVENTS_DATABASE_NAME = "data.db"


# ----- Classes ----- #

class CombinedHandler:
    def __init__(self,
                 users_database_file: Union[str, Path] = USERS_DATABASE_NAME,
                 events_database_file: Union[str, Path] = EVENTS_DATABASE_NAME):
        """
        Initialize the combined handler class.
        :param users_database_file: The user database.
        :param events_database_file: The event database.
        """
        self.users_handler = UsersHandler(users_database_file)
        self.events_handler = EventsHandler(events_database_file)

    def add_user(self, username: str, mail: str, password: str) -> str:
        """
        Add user to the database.
        :param username: User name.
        :param mail: Mail of user.
        :param password: Password.
        :return: User id.
        """
        user = User(None, username, mail, "", [])

        return self.users_handler.add_user(user, password)

    def get_user(self, user_id: str) -> User:
        """
        Get user by id from the database.
        :param user_id: Given user id.
        :return: User.
        """
        return self.users_handler.get_user(user_id)

    def remove_user(self, user_id: str):
        """
        Remove user from the database.
        :param user_id: Given user id to remove.
        """
        user = self.get_user(user_id)
        for event_id in user.hosts_events:
            self.remove_event(event_id)
        self.users_handler.remove_user(user_id)

    def add_event(
            self,
            user_id: str,
            name: str,
            description: str,
            location: str,
            subscribers: list[str],
            start: datetime,
            end: datetime = None
    ) -> str:
        """
        Add event to the database.
        :param user_id: Who created the event.
        :param name: Name of the event.
        :param description: Details about the event.
        :param location: Where the event?
        :param subscribers: who invited?
        :param start: start time.
        :param end: end time.
        :return: Event id.
        """
        end = end if end is not None else start

        start = start.strftime('%Y-%m-%d %H:%M:%S+00:00')
        end = end.strftime('%Y-%m-%d %H:%M:%S+00:00')
        event = Event(None, user_id, name, description, location, subscribers, start, end, None)
        self.get_user(event.created_user_id)  # Check if user exist
        if event.created_user_id not in event.subscribers:
            event.subscribers.append(event.created_user_id)
        event_id = self.events_handler.add_event(event)
        self.assign_event_to_user(event.created_user_id, event_id)
        return event_id

    def get_event(self, event_id: str) -> Event:
        """
        Get event by id from the database.
        :param event_id: Given event id.
        :return: Event.
        """
        return self.events_handler.get_event(event_id)

    def remove_event(self, event_id: str):
        """
        Remove event from the database.
        :param event_id: Given event id to remove.
        """
        event = self.get_event(event_id)
        self.remove_event_from_user(event.created_user_id, event_id)
        self.events_handler.remove_event(event_id)

    def assign_event_to_user(self, user_id: str, event_id: str):
        """
        Assign an event to a user.
        :param user_id: User ID.
        :param event_id: Event ID.
        """
        self.users_handler.add_event_to_user(user_id, event_id)

    def remove_event_from_user(self, user_id: str, event_id: str):
        """
        Remove an event from a user.
        :param user_id: User ID.
        :param event_id: Event ID.
        """
        self.users_handler.remove_event_from_user(user_id, event_id)

    def get_user_id_by_name(self, user_name):
        """
        Return the user id by the given name.
        :param user_name: Name of user.
        :return: User id.
        """
        return self.users_handler.get_user_id_by_name(user_name)

    def modify_event(self, event_id: str, **changes) -> None:
        """
        Modify an existing event in the database by its event ID.
        :param event_id: ID of the event to modify.
        :param changes: Key Value pairs of the fields you want to update and their new values.
        """
        self.events_handler.modify_event(event_id, **changes)

    def get_events_by_attribute(
            self,
            sort_by_attribute: Optional[str] = None,
            reverse: bool = False,
            location_filter: str = None,
            **filters

        ) -> list[Event]:
        """
        Fetch all events with a specific attribute.
        :param sort_by_attribute: The attribute to sort by (examples:
                                                                'event_start_time', 'creation_time', 'subscribers').
        :param reverse: If True, sort in descending order. otherwise, sort in ascending order.
        :param filters: Key Value pairs of the attributes and values you want to filter by.
        :param location_filter:
        :return: List of events that match the given attributes.
        """
        if location_filter:
            filters["location"] = location_filter
        return self.events_handler.get_events(sort_by_attribute, reverse, **filters)

    def add_subscriber_to_event(self, event_id: str, user_id: str) -> None:
        """
        Add a subscriber to an event.
        :param event_id: ID of the event.
        :param user_id: ID of the new subscriber.
        """
        self.get_user(user_id)
        self.events_handler.add_subscriber(event_id, user_id)

    def remove_subscriber_from_event(self, event_id: str, user_id: str) -> None:
        """
        Remove a subscriber from an event.
        :param event_id: ID of the event.
        :param user_id: ID of the subscriber to be removed.
        """
        self.get_user(user_id)
        self.events_handler.remove_subscriber(event_id, user_id)

    def send_message(self, event_id, message):
        event = self.get_event(event_id)
        for user_id in event.subscribers:
            user = self.get_user(user_id)
            msg = f"Reminder: Hi {user.user_name}, about '{event.event_name}' at {event.location}, {message}"
            self.users_handler.send_mail(user, msg)

    def close(self):
        """
        Close the database connections.
        """
        self.users_handler.close()
        self.events_handler.close()
