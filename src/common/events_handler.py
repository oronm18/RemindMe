"""
Event handler file.
Author: Oron Moshe
Date: 22/10/2023
"""
# ----- Imports ----- #

import json
from datetime import datetime
from pathlib import Path
from typing import Union, Optional

from core.database_handler import DatabaseHandler
from core.event import Event, EventAlreadyExist, ModifyChangesAreInvalid, InvalidAttribute, \
    UserDoesNotASubscriber, UserAlreadySubscriber
from core.utils import generate_unique_id


# ----- Classes ----- #

class EventsHandler(DatabaseHandler):
    def __init__(self, events_database_file: Union[str, Path]):
        """
        Init the event handler class.
        :param events_database_file: The event database.
        """
        super().__init__(events_database_file)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS events
            (event_id TEXT PRIMARY KEY, 
            created_user_id TEXT,
            event_name TEXT UNIQUE, 
            event_description TEXT,
            location TEXT,
            subscribers TEXT DEFAULT '[]',
            event_start_time DATETIME,
            event_end_time DATETIME,
            creation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_user_id) REFERENCES users(user_id))
        ''')

    def add_event(self, event: Event) -> str:
        """
        Add event to the database.
        :param event: Given event to add.
        :return: Event id.
        """
        self.cursor.execute("SELECT event_id FROM events WHERE event_name=?", (event.event_name,))
        if self.cursor.fetchone():
            raise EventAlreadyExist()

        event.event_id = generate_unique_id()

        self.cursor.execute(
            "INSERT INTO events (event_id, created_user_id, event_name, event_description, location, subscribers, "
            "event_start_time, event_end_time, creation_time) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (event.event_id, event.created_user_id, event.event_name, event.event_description, event.location,
             json.dumps(event.subscribers), event.event_start_time, event.event_end_time, datetime.now()))
        self.conn.commit()
        return event.event_id

    def remove_event(self, event_id: str):
        """
        Remove event from data base.
        :param event_id: Given event id to remove
        """
        self.cursor.execute("DELETE FROM events WHERE event_id=?", (event_id,))
        self.conn.commit()

    def modify_event(self, event_id: str, **changes) -> None:
        """
        Modify an existing event in the database by its event ID.
        :param event_id: ID of the event to modify.
        :param changes: Key-value pairs of the fields you want to update and their new values.
        """
        set_conditions = []
        params = []

        for key, value in changes.items():
            if key in Event.__annotations__.keys():
                if key == "subscribers":
                    value = json.dumps(value)
                set_conditions.append(f"{key} = ?")
                params.append(value)

        if not set_conditions:
            raise ModifyChangesAreInvalid(changes)

        set_conditions_str = ', '.join(set_conditions)
        query = f"UPDATE events SET {set_conditions_str} WHERE event_id = ?"

        params.append(event_id)

        self.cursor.execute(query, params)
        self.conn.commit()

    def get_event(self, event_id) -> Event:
        """
        Get event by id from database.
        :param event_id: Given event id.
        :return: Event.
        """
        return self.get_events_by_ids([event_id])[0]

    def get_events_by_ids(self, events_ids: list[str] = None) -> list[Event]:
        """
        Return all the events.
        :param events_ids: If entered, return all the events that were given. if not return all.
        """
        if events_ids is not None:
            placeholders = ', '.join(['?'] * len(events_ids))
            query = "SELECT * FROM events WHERE event_id IN ({})".format(placeholders)
            self.cursor.execute(query, events_ids)
        else:
            self.cursor.execute("SELECT * FROM events")
        results = self.cursor.fetchall()
        return self.fetch_events(results)

    def get_events(self, sort_by_attribute: Optional[str] = None, reverse: bool = False, **filters) -> list[Event]:
        """
        Fetch all events with optional filtering and sorting.
        :param sort_by_attribute: The attribute to sort by (e.g., 'event_start_time', 'creation_time', 'subscribers').
        :param reverse: If True, sort in descending order; otherwise, sort in ascending order.
        :param filters: Key-value pairs of the attributes and values you want to filter by.
        :return: List of events that match the given filters and sorted by the provided attribute.
        """
        # Filtering query.
        query_conditions = []
        params = []
        for key, value in filters.items():
            if key in Event.__annotations__.keys():
                query_conditions.append(f"{key} = ?")
                params.append(value)
        where_clause = ''
        if query_conditions:
            where_conditions_str = ' AND '.join(query_conditions)
            where_clause = f"WHERE {where_conditions_str}"

        # Sorting query.
        order_clause = ''
        if sort_by_attribute:
            if sort_by_attribute not in Event.__annotations__.keys():
                raise InvalidAttribute(sort_by_attribute)

            # Special handling for counting the number of subscribers
            if sort_by_attribute == "subscribers":
                order_by_clause = "LENGTH(subscribers) - LENGTH(REPLACE(subscribers, ',', ''))"
            else:
                order_by_clause = sort_by_attribute

            order_direction = "DESC" if reverse else "ASC"
            order_clause = f"ORDER BY {order_by_clause} {order_direction}"

        # Constructing final query
        query = f"SELECT * FROM events {where_clause} {order_clause}"

        self.cursor.execute(query, params)
        results = self.cursor.fetchall()
        return self.fetch_events(results)

    @staticmethod
    def fetch_events(results):
        events = []
        for result in results:
            subscribers = json.loads(result[5])
            events.append(
                Event(event_id=result[0],
                      created_user_id=result[1],
                      event_name=result[2],
                      event_description=result[3],
                      location=result[4],
                      subscribers=subscribers,
                      event_start_time=datetime.fromisoformat(result[6]),
                      event_end_time=datetime.fromisoformat(result[7]),
                      creation_time=datetime.fromisoformat(result[8])))

        return events

    def add_subscriber(self, event_id: str, user_id: str) -> None:
        """
        Add a subscriber to an event.
        :param event_id: ID of the event.
        :param user_id: ID of the new subscriber.
        """
        event = self.get_event(event_id)
        if user_id in event.subscribers:
            raise UserAlreadySubscriber(user_id)

        event.subscribers.append(user_id)
        serialized_subscribers = json.dumps(event.subscribers)

        self.cursor.execute("UPDATE events SET subscribers = ? WHERE event_id = ?", (serialized_subscribers, event_id))
        self.conn.commit()

    def remove_subscriber(self, event_id: str, user_id: str) -> None:
        """
        Remove a subscriber from an event.
        :param event_id: ID of the event.
        :param user_id: ID of the subscriber to be removed.
        """
        event = self.get_event(event_id)
        if user_id not in event.subscribers:
            raise UserDoesNotASubscriber(user_id)

        event.subscribers.remove(user_id)
        serialized_subscribers = json.dumps(event.subscribers)

        self.cursor.execute("UPDATE events SET subscribers = ? WHERE event_id = ?", (serialized_subscribers, event_id))
        self.conn.commit()
